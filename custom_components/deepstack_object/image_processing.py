"""
Component that will perform object detection and identification via deepstack.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/image_processing.deepstack_object
"""
import datetime
import io
import logging
import os
import re
from datetime import timedelta
from typing import Tuple
from pathlib import Path

from PIL import Image, ImageDraw

import deepstack.core as ds
import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
import voluptuous as vol
from homeassistant.util.pil import draw_box
from homeassistant.components.image_processing import (
    ATTR_CONFIDENCE,
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_SOURCE,
    DOMAIN,
    PLATFORM_SCHEMA,
    ImageProcessingEntity,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_NAME,
    CONF_IP_ADDRESS,
    CONF_PORT,
    HTTP_BAD_REQUEST,
    HTTP_OK,
    HTTP_UNAUTHORIZED,
)
from homeassistant.core import split_entity_id

_LOGGER = logging.getLogger(__name__)

CONF_API_KEY = "api_key"
CONF_TARGETS = "targets"
CONF_TIMEOUT = "timeout"
CONF_SAVE_FILE_FOLDER = "save_file_folder"
CONF_SAVE_TIMESTAMPTED_FILE = "save_timestamped_file"

DATETIME_FORMAT = "%Y-%m-%d_%H:%M:%S"
DEFAULT_API_KEY = ""
DEFAULT_TARGETS = ["person"]
DEFAULT_TIMEOUT = 10

EVENT_OBJECT_DETECTED = "deepstack.object_detected"
BOX = "box"
FILE = "file"
OBJECT = "object"

RED = (255, 0, 0)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Required(CONF_PORT): cv.port,
        vol.Optional(CONF_API_KEY, default=DEFAULT_API_KEY): cv.string,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
        vol.Optional(CONF_TARGETS, default=DEFAULT_TARGETS): vol.All(
            cv.ensure_list, [cv.string]
        ),
        vol.Optional(CONF_SAVE_FILE_FOLDER): cv.isdir,
        vol.Optional(CONF_SAVE_TIMESTAMPTED_FILE, default=False): cv.boolean,
    }
)


def get_valid_filename(name: str) -> str:
    return re.sub(r"(?u)[^-\w.]", "", str(name).strip().replace(" ", "_"))


def get_objects(predictions: list, img_width: int, img_height: int):
    """Return objects with formatting and extra info."""
    objects = []
    decimal_places = 3
    for pred in predictions:
        box_width = pred["x_max"] - pred["x_min"]
        box_height = pred["y_max"] - pred["y_min"]
        box = {
            "height": round(box_height / img_height, decimal_places),
            "width": round(box_width / img_width, decimal_places),
            "y_min": round(pred["y_min"] / img_height, decimal_places),
            "x_min": round(pred["x_min"] / img_width, decimal_places),
            "y_max": round(pred["y_max"] / img_height, decimal_places),
            "x_max": round(pred["x_max"] / img_width, decimal_places),
        }
        box_area = round(box["height"] * box["width"], decimal_places)
        centroid = {
            "x": round(box["x_min"] + (box["width"] / 2), decimal_places),
            "y": round(box["y_min"] + (box["height"] / 2), decimal_places),
        }
        name = pred["label"]
        confidence = round(pred["confidence"] * 100, decimal_places)

        objects.append(
            {
                "bounding_box": box,
                "box_area": box_area,
                "centroid": centroid,
                "name": name,
                "confidence": confidence,
            }
        )
    return objects


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the classifier."""
    save_file_folder = config.get(CONF_SAVE_FILE_FOLDER)
    if save_file_folder:
        save_file_folder = Path(save_file_folder)

    targets = [t.lower() for t in config[CONF_TARGETS]]  # ensure lower case
    entities = []
    for camera in config[CONF_SOURCE]:
        object_entity = ObjectClassifyEntity(
            config.get(CONF_IP_ADDRESS),
            config.get(CONF_PORT),
            config.get(CONF_API_KEY),
            config.get(CONF_TIMEOUT),
            targets,
            config.get(ATTR_CONFIDENCE),
            save_file_folder,
            config.get(CONF_SAVE_TIMESTAMPTED_FILE),
            camera.get(CONF_ENTITY_ID),
            camera.get(CONF_NAME),
        )
        entities.append(object_entity)
    add_devices(entities)


class ObjectClassifyEntity(ImageProcessingEntity):
    """Perform a face classification."""

    def __init__(
        self,
        ip_address,
        port,
        api_key,
        timeout,
        targets,
        confidence,
        save_file_folder,
        save_timestamped_file,
        camera_entity,
        name=None,
    ):
        """Init with the API key and model id."""
        super().__init__()
        self._dsobject = ds.DeepstackObject(ip_address, port, api_key, timeout)
        self._targets = targets
        self._confidence = confidence
        self._camera = camera_entity
        if name:
            self._name = name
        else:
            camera_name = split_entity_id(camera_entity)[1]
            self._name = "deepstack_object_{}".format(camera_name)

        self._state = None
        self._objects = []  # The parsed raw data
        self._targets_found = []
        self._summary = {}

        self._last_detection = None
        self._image_width = None
        self._image_height = None
        self._save_file_folder = save_file_folder
        self._save_timestamped_file = save_timestamped_file

    def process_image(self, image):
        """Process an image."""
        self._image_width, self._image_height = Image.open(
            io.BytesIO(bytearray(image))
        ).size
        self._state = None
        self._objects = []  # The parsed raw data
        self._targets_found = []
        self._summary = {}

        try:
            self._dsobject.detect(image)
        except ds.DeepstackException as exc:
            _LOGGER.error("Deepstack error : %s", exc)
            return

        predictions = self._dsobject.predictions.copy()
        self._summary = ds.get_objects_summary(predictions)
        self._objects = get_objects(predictions, self._image_width, self._image_height)
        self._targets_found = [
            obj
            for obj in self._objects
            if (obj["name"] in self._targets) and (obj["confidence"] > self._confidence)
        ]

        self._state = len(self._targets_found)
        if self._state > 0:
            self._last_detection = dt_util.now().strftime(DATETIME_FORMAT)

        # Fire events
        for target in self._targets_found:
            target_event_data = target.copy()
            target_event_data[ATTR_ENTITY_ID] = self.entity_id
            self.hass.bus.fire(EVENT_OBJECT_DETECTED, target_event_data)

        if self._save_file_folder and self._state > 0:
            self.save_image(
                image, self._targets, self._confidence, self._save_file_folder,
            )

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "targets"

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        attr = {}
        for target in self._targets:
            attr[f"ALL {target} count"] = len(
                [t for t in self._objects if t["name"] == target]
            )
        if self._last_detection:
            attr["last_target_detection"] = self._last_detection
        attr["summary"] = self._summary
        attr["objects"] = self._objects
        return attr

    def save_image(self, image, targets, confidence, directory):
        """Draws the actual bounding box of the detected objects."""
        try:
            img = Image.open(io.BytesIO(bytearray(image))).convert("RGB")
        except UnidentifiedImageError:
            _LOGGER.warning("Deepstack unable to process image, bad data")
            return
        draw = ImageDraw.Draw(img)

        for obj in self._objects:
            if not obj["name"] in self._targets:
                continue
            name = obj["name"]
            confidence = obj["confidence"]
            box = obj["bounding_box"]
            centroid = obj["centroid"]
            box_label = f"{name}: {confidence:.1f}%"
            draw_box(
                draw,
                (box["y_min"], box["x_min"], box["y_max"], box["x_max"]),
                img.width,
                img.height,
                text=box_label,
                color=RED,
            )

            # draw bullseye
            draw.text(
                (centroid["x"] * img.width, centroid["y"] * img.height),
                text="X",
                fill=RED,
            )

        latest_save_path = (
            directory / f"{get_valid_filename(self._name).lower()}_latest.jpg"
        )
        img.save(latest_save_path)

        if self._save_timestamped_file:
            timestamp_save_path = directory / f"{self._name}_{self._last_detection}.jpg"
            img.save(timestamp_save_path)
            _LOGGER.info("Deepstack saved file %s", timestamp_save_path)