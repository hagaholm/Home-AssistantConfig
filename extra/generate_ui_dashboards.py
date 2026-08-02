import argparse
import json
import re
import shutil
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / "generated_ui"

# ── Category grouping ───────────────────────────────────────────────────────
# Maps a folder-path fragment (relative to repo root) to a human-visible
# category name and icon.  The FIRST matching rule wins.
CATEGORY_RULES: list[tuple[str, str, str]] = [
    ("packages/lights",        "Lights",          "mdi:lightbulb-group-outline"),
    ("packages/climate",       "Climate & HVAC",  "mdi:thermostat"),
    ("packages/ventilation",   "Ventilation",     "mdi:fan"),
    ("packages/frigate",       "Frigate",         "mdi:cctv"),
    ("packages/media",         "Media",           "mdi:play-box-multiple-outline"),
    ("packages/presence",      "Presence",        "mdi:map-marker-account"),
    ("packages/sensors",       "Sensors",         "mdi:thermometer-lines"),
    ("packages/scripts",       "Scripts",         "mdi:script-text-outline"),
    ("packages/notifications", "Notifications",   "mdi:bell-outline"),
    ("packages/helpers",       "Helpers",         "mdi:tune-vertical"),
    ("packages/alerts",        "Alerts",          "mdi:alarm-light-outline"),
    ("packages/automations",   "Automations",     "mdi:robot-outline"),
    ("packages/integrations",  "Integrations",    "mdi:puzzle-outline"),
    ("packages/wiim",          "WiiM",            "mdi:music-box-outline"),
    ("packages/system",        "System",          "mdi:cog-outline"),
    ("sensor",                 "Sensors",         "mdi:thermometer-lines"),
    ("group",                  "Groups",          "mdi:account-group-outline"),
]


def categorize_file(rel_posix: str) -> tuple[str, str]:
    """Return (category_name, icon) for a repo-relative posix path."""
    for prefix, name, icon in CATEGORY_RULES:
        if rel_posix.startswith(prefix):
            return name, icon
    return "Other", "mdi:folder-open"


SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".storage", "node_modules", "backup", "www", "esphome", "custom_components", "docs", "githooks", "python_scripts", "script", "logging"}
SKIP_NAMES = {".DS_Store"}
TARGET_DIRS = {"automations", "group", "packages", "sensor"}
TEXT_EXTENSIONS = {".yaml", ".yml"}
HELPER_SECTIONS = {
    "input_text",
    "input_number",
    "input_boolean",
    "input_datetime",
    "input_select",
    "input_date",
    "input_time",
    "timer",
    "counter",
    "utility_meter",
}
YAML_FALLBACK_SECTIONS = HELPER_SECTIONS | {"automation", "script", "rest_command"}
NAME_BASED_ENTITY_SECTIONS = {
    "sensor",
    "binary_sensor",
    "switch",
    "light",
    "fan",
    "climate",
    "cover",
    "lock",
    "media_player",
    "camera",
    "select",
    "number",
    "scene",
    "device_tracker",
    "image",
}
SECTION_ORDER = [
    "input_text",
    "input_number",
    "input_boolean",
    "input_datetime",
    "input_select",
    "input_date",
    "input_time",
    "timer",
    "counter",
    "utility_meter",
    "template",
    "sensor",
    "binary_sensor",
    "switch",
    "light",
    "fan",
    "climate",
    "cover",
    "lock",
    "media_player",
    "camera",
    "select",
    "number",
    "automation",
    "script",
    "rest_command",
    "scene",
    "device_tracker",
    "image",
]
SECTION_TITLES = {
    "input_text": "Input text",
    "input_number": "Input numbers",
    "input_boolean": "Input booleans",
    "input_datetime": "Input datetimes",
    "input_select": "Input selects",
    "input_date": "Input dates",
    "input_time": "Input times",
    "timer": "Timers",
    "counter": "Counters",
    "utility_meter": "Utility meters",
    "template": "Template sensors",
    "sensor": "Sensors",
    "binary_sensor": "Binary sensors",
    "switch": "Switches",
    "light": "Lights",
    "fan": "Fans",
    "climate": "Climate",
    "cover": "Covers",
    "lock": "Locks",
    "media_player": "Media players",
    "camera": "Cameras",
    "select": "Selects",
    "number": "Numbers",
    "automation": "Automations",
    "script": "Scripts",
    "rest_command": "Rest commands",
    "scene": "Scenes",
    "device_tracker": "Device trackers",
    "image": "Images",
}
SECTION_ICONS = {
    "input_text": "mdi:form-textbox",
    "input_number": "mdi:numeric",
    "input_boolean": "mdi:toggle-switch",
    "input_datetime": "mdi:calendar-clock",
    "input_select": "mdi:format-list-bulleted",
    "input_date": "mdi:calendar",
    "input_time": "mdi:clock-outline",
    "timer": "mdi:timer-outline",
    "counter": "mdi:counter",
    "utility_meter": "mdi:gauge",
    "template": "mdi:chart-box-outline",
    "sensor": "mdi:thermometer",
    "binary_sensor": "mdi:toggle-switch-outline",
    "switch": "mdi:toggle-switch",
    "light": "mdi:lightbulb-outline",
    "fan": "mdi:fan",
    "climate": "mdi:thermostat",
    "cover": "mdi:garage",
    "lock": "mdi:lock-outline",
    "media_player": "mdi:play-box-multiple-outline",
    "camera": "mdi:cctv",
    "select": "mdi:format-list-bulleted",
    "number": "mdi:numeric",
    "automation": "mdi:home-automation",
    "script": "mdi:script-text-outline",
    "rest_command": "mdi:api",
    "scene": "mdi:palette",
    "device_tracker": "mdi:map-marker",
    "image": "mdi:image",
}
SERVICE_LIKE_OBJECT_IDS = {
    "turn_on",
    "turn_off",
    "toggle",
    "set_datetime",
    "set_value",
    "select_option",
    "play_media",
    "select_source",
    "cancel",
    "start",
    "finished",
}
NON_ENTITY_DOMAINS = {"rest_command"}
ENTITY_RE = re.compile(
    r"\b((?:automation|script|input_boolean|input_select|input_number|input_datetime|input_text|input_date|input_time|rest_command|sensor|switch|light|fan|binary_sensor|climate|media_player|cover|lock|person|select|device_tracker|camera|scene|sun|zone|weather|timer)\.[A-Za-z0-9_:-]+)\b"
)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_value = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_value).strip("_")
    return ascii_value.lower() or "folder"


def iter_target_folders(root: Path) -> Iterable[Path]:
    for name in sorted(TARGET_DIRS):
        target = root / name
        if target.exists() and target.is_dir():
            yield target


def iter_subfolders(folder: Path) -> Iterable[Path]:
    for path in sorted(folder.iterdir()):
        if path.name in SKIP_NAMES:
            continue
        if path.is_dir() and path.name not in SKIP_DIRS:
            yield path
            yield from iter_subfolders(path)


def iter_source_files(folder: Path) -> Iterable[Path]:
    for path in sorted(folder.iterdir()):
        if path.name in SKIP_NAMES:
            continue
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            yield path


def _classify_usage(text: str, entity_id: str) -> str:
    """Return 'read', 'write', or 'read/write' for how entity_id is used in text."""
    domain = entity_id.split(".", 1)[0]
    # A service call that mutates state for this entity's domain
    write_re = re.compile(
        r"service:\s+(?:" + re.escape(domain) + r"\.\w+|homeassistant\.(?:turn_on|turn_off|toggle))",
        re.IGNORECASE,
    )
    has_write = False
    has_read = False
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if entity_id not in line:
            continue
        context = "\n".join(lines[max(0, i - 10) : i + 1])
        if write_re.search(context):
            has_write = True
        else:
            has_read = True
    if has_write and has_read:
        return "read/write"
    return "write" if has_write else "read"


def collect_source_file_items(root: Path) -> list[tuple[Path, Path]]:
    """Return (folder, path) pairs for all meaningful YAML files in scan order."""
    items: list[tuple[Path, Path]] = []
    for base in iter_target_folders(root):
        for folder in [base, *iter_subfolders(base)]:
            for path in iter_source_files(folder):
                if is_meaningful_yaml(read_text(path)):
                    items.append((folder, path))
    return items


def build_cross_reference_map(
    file_items: list[tuple[Path, Path]],
    *,
    root: Path,
    name_map: dict[tuple[str, str], str] | None,
    available_entities: set[str] | None = None,
) -> dict[str, list[tuple[str, str]]]:
    """Map entity_id -> [(rel_path, usage_type), ...] across all source files.

    usage_type is 'read', 'write', or 'read/write'.
    """
    refs_by_entity: dict[str, list[tuple[str, str]]] = {}
    for _folder, path in file_items:
        rel = path.relative_to(root).as_posix()
        file_text = read_text(path)
        parsed = parse_entities(file_text, name_map=name_map, available_entities=available_entities)
        for entity_id in parsed.get("referenced", []):
            usage = _classify_usage(file_text, entity_id)
            refs_by_entity.setdefault(entity_id, []).append((rel, usage))
    return refs_by_entity


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def normalize_entity(value: str) -> str:
    return value.strip().strip('"\'')


def is_service_like_entity(entity_id: str) -> bool:
    if "." not in entity_id:
        return False
    return entity_id.split(".", 1)[1] in SERVICE_LIKE_OBJECT_IDS


def is_stateful_entity(entity_id: str) -> bool:
    if "." not in entity_id:
        return False
    domain = entity_id.split(".", 1)[0]
    return domain not in NON_ENTITY_DOMAINS


def is_meaningful_yaml(text: str) -> bool:
    if not text.strip():
        return False
    stripped = text.strip()
    if stripped in {"[]", "{}"}:
        return False
    if re.fullmatch(r"[-\s\n\r]+", stripped):
        return False

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return False

    if all(line.startswith("#") for line in lines):
        return False

    return True


def load_inventory(path: Path) -> tuple[dict[tuple[str, str], str], set[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entities = payload.get("entities", []) if isinstance(payload, dict) else []
    name_map: dict[tuple[str, str], str] = {}
    available_entities: set[str] = set()

    for entity in entities:
        if not isinstance(entity, dict):
            continue
        entity_id = entity.get("entity_id")
        original_name = entity.get("original_name")
        if not isinstance(entity_id, str) or "." not in entity_id:
            continue
        available_entities.add(entity_id)
        if not isinstance(original_name, str) or not original_name.strip():
            continue

        domain = entity_id.split(".", 1)[0]
        name_map[(domain, slugify(original_name))] = entity_id

    return name_map, available_entities


def load_inventory_name_map(path: Path) -> dict[tuple[str, str], str]:
    name_map, _ = load_inventory(path)
    return name_map


def maybe_add_entity(groups: dict[str, list[str]], section: str, entity_id: str, available_entities: set[str] | None = None) -> None:
    if available_entities is None:
        groups[section].append(entity_id)
        return

    domain = entity_id.split(".", 1)[0]
    if entity_id in available_entities:
        groups[section].append(entity_id)
        return

    if section in YAML_FALLBACK_SECTIONS and not any(entity.startswith(f"{domain}.") for entity in available_entities):
        groups[section].append(entity_id)


def parse_entities(
    text: str,
    *,
    name_map: dict[tuple[str, str], str] | None = None,
    available_entities: set[str] | None = None,
) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {name: [] for name in SECTION_ORDER}
    groups["referenced"] = []
    lines = text.splitlines()

    current_section: str | None = None
    current_item_name: str | None = None
    current_platform: str | None = None
    current_sensor_name: str | None = None
    current_sensor_entity_added = False
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if re.match(r"^[a-zA-Z0-9_]+:\s*$", stripped):
            indent = len(line) - len(line.lstrip(" "))
            if indent == 0:
                current_section = stripped[:-1]
                current_item_name = None
                current_platform = None
                current_sensor_name = None
                current_sensor_entity_added = False
                continue
            if current_section in {"automation", "script"} and indent <= 2:
                entity_name = stripped[:-1]
                entity_id = f"{current_section}.{slugify(entity_name)}"
                maybe_add_entity(groups, current_section, entity_id, available_entities)
                current_item_name = entity_name
                continue
            if (
                current_section in NAME_BASED_ENTITY_SECTIONS
                and indent > 0
                and current_section not in {"sensor"}
                and not stripped.startswith("- ")
                and stripped[:-1] not in SECTION_ORDER
            ):
                entity_name = stripped[:-1]
                entity_id = (name_map or {}).get((current_section, slugify(entity_name)), f"{current_section}.{slugify(entity_name)}")
                maybe_add_entity(groups, current_section, entity_id, available_entities)
                current_sensor_name = entity_name
                current_sensor_entity_added = True
                current_item_name = entity_name
                continue
            if current_section == "rest_command" and indent <= 2:
                entity_name = stripped[:-1]
                entity_id = f"rest_command.{slugify(entity_name)}"
                maybe_add_entity(groups, "rest_command", entity_id, available_entities)
                current_item_name = entity_name
                continue
            if current_section in HELPER_SECTIONS and indent <= 2:
                entity_name = stripped[:-1]
                entity_id = f"{current_section}.{slugify(entity_name)}"
                maybe_add_entity(groups, current_section, entity_id, available_entities)
                current_item_name = entity_name
                continue
            if current_section in HELPER_SECTIONS and indent > 2 and current_item_name is not None:
                entity_name = stripped[:-1]
                entity_id = f"{current_section}.{slugify(entity_name)}"
                maybe_add_entity(groups, current_section, entity_id, available_entities)
                current_item_name = entity_name
                continue
            if current_section in HELPER_SECTIONS and indent == 2:
                entity_name = stripped[:-1]
                entity_id = f"{current_section}.{slugify(entity_name)}"
                maybe_add_entity(groups, current_section, entity_id, available_entities)
                current_item_name = entity_name
                continue
            if current_section in NAME_BASED_ENTITY_SECTIONS and indent > 2:
                continue
            if current_section in HELPER_SECTIONS and indent > 2:
                continue
            if current_section in SECTION_ORDER and indent > 2:
                continue
            current_section = stripped[:-1]
            current_item_name = None
            current_platform = None
            current_sensor_name = None
            current_sensor_entity_added = False
            continue

        if current_section == "sensor" and stripped.startswith("- platform:"):
            current_platform = stripped.split(":", 1)[1].strip()
            current_sensor_name = None
            current_sensor_entity_added = False
            continue

        if current_section in NAME_BASED_ENTITY_SECTIONS and re.match(r"^-\s+[A-Za-z0-9_]+:\s*", stripped):
            current_sensor_name = None
            current_sensor_entity_added = False

        if current_section in NAME_BASED_ENTITY_SECTIONS and stripped.startswith(("name:", "- name:")):
            name_match = re.match(r"^(?:- )?name:\s*(.+)$", stripped)
            if name_match:
                current_sensor_name = name_match.group(1).strip().strip('"\'')
                if current_sensor_name and not current_sensor_entity_added:
                    domain = current_section
                    entity_id = (name_map or {}).get((domain, slugify(current_sensor_name)), f"{domain}.{slugify(current_sensor_name)}")
                    maybe_add_entity(groups, domain, entity_id, available_entities)
                    current_sensor_entity_added = True
                continue

        if current_section == "sensor" and current_platform and stripped.startswith("monitored_conditions:"):
            continue

        if current_section == "sensor" and current_platform and current_sensor_name and re.match(r"^-\s+([A-Za-z0-9_]+)", stripped):
            condition_name = re.match(r"^-\s+([A-Za-z0-9_]+)", stripped).group(1)
            entity_id = f"sensor.{slugify(f'{current_sensor_name}_{condition_name}') }"
            maybe_add_entity(groups, "sensor", entity_id, available_entities)

        if current_section in HELPER_SECTIONS:
            if current_section in {"input_boolean", "input_text", "input_select", "input_datetime", "input_number", "input_date", "input_time"}:
                helper_match = re.match(r"^([A-Za-z0-9_]+):\s*$", stripped)
                if helper_match:
                    entity_id = f"{current_section}.{helper_match.group(1)}"
                    maybe_add_entity(groups, current_section, entity_id, available_entities)
                    current_item_name = helper_match.group(1)
                    continue

            match = re.match(r"^([A-Za-z0-9_]+):\s*$", stripped)
            if match:
                entity_id = f"{current_section}.{match.group(1)}"
                maybe_add_entity(groups, current_section, entity_id, available_entities)
                current_item_name = match.group(1)
                continue

        if current_section == "automation":
            alias_match = re.match(r"^-\s+alias:\s*(.+)$", stripped)
            if alias_match:
                alias = alias_match.group(1)
                entity_id = (name_map or {}).get(("automation", slugify(alias)), f"automation.{slugify(alias)}")
                maybe_add_entity(groups, "automation", entity_id, available_entities)
                continue

        if current_section == "script":
            alias_match = re.match(r"^-\s+alias:\s*(.+)$", stripped)
            if alias_match:
                alias = alias_match.group(1)
                entity_id = (name_map or {}).get(("script", slugify(alias)), f"script.{slugify(alias)}")
                maybe_add_entity(groups, "script", entity_id, available_entities)
                continue

        if current_section == "template":
            name_match = re.match(r"^- name:\s*(.+)$", stripped)
            if name_match:
                entity_id = f"sensor.{slugify(name_match.group(1))}"
                maybe_add_entity(groups, "template", entity_id, available_entities)
                continue

        for entity in ENTITY_RE.findall(line):
            value = normalize_entity(entity)
            if value and not is_service_like_entity(value) and value not in groups["referenced"]:
                groups["referenced"].append(value)

    for name in list(groups):
        groups[name] = sorted(set(groups[name]))
    return groups


def build_markdown_card(title: str, content: str, *, icon: str = "mdi:folder") -> dict[str, Any]:
    return {
        "type": "markdown",
        "title": title,
        "icon": icon,
        "content": content,
    }


def build_entities_card(title: str, entities: list[str]) -> dict[str, Any]:
    return {
        "type": "entities",
        "title": title,
        "show_header_toggle": False,
        "state_color": True,
        "entities": entities,
    }


def build_bullet_markdown(title: str, items: list[str], *, icon: str) -> dict[str, Any]:
    return build_markdown_card(title, "\n".join(f"- {item}" for item in items), icon=icon)


def build_entity_type_catalog(
    root: Path,
    *,
    name_map: dict[tuple[str, str], str] | None = None,
    available_entities: set[str] | None = None,
) -> dict[str, list[dict[str, str]]]:
    catalog: dict[str, list[dict[str, str]]] = {section: [] for section in SECTION_ORDER}
    for folder, path in collect_source_file_items(root):
        parsed_entities = parse_entities(read_text(path), name_map=name_map, available_entities=available_entities)
        for section in SECTION_ORDER:
            for entity_id in parsed_entities.get(section, []):
                catalog[section].append(
                    {
                        "entity_id": entity_id,
                        "source": path.relative_to(root).as_posix(),
                        "folder": folder.relative_to(root).as_posix() or ".",
                    }
                )

    for section in SECTION_ORDER:
        seen: set[str] = set()
        unique_items: list[dict[str, str]] = []
        for item in sorted(catalog[section], key=lambda entry: (entry["entity_id"], entry["source"])):
            if item["entity_id"] in seen:
                continue
            seen.add(item["entity_id"])
            unique_items.append(item)
        catalog[section] = unique_items

    return catalog


def build_view_for_file(
    folder: Path,
    path: Path,
    *,
    generated_at: str,
    root: Path,
    name_map: dict[tuple[str, str], str] | None = None,
    cross_refs: dict[str, list[tuple[str, str]]] | None = None,
    available_entities: set[str] | None = None,
) -> dict[str, Any] | None:
    text = read_text(path)
    parsed_entities = parse_entities(text, name_map=name_map, available_entities=available_entities)

    summary_lines = [
        f"# {path.stem}",
        "",
        f"- Source folder: {folder.name}",
        f"- File path: {path.relative_to(root).as_posix()}",
        f"- Generated: {generated_at}",
        f"- Size: {path.stat().st_size} bytes",
    ]

    cards: list[dict[str, Any]] = [
        build_markdown_card("Overview", "\n".join(summary_lines), icon="mdi:file-document-outline"),
    ]
    has_substantive_content = False

    for section in SECTION_ORDER:
        items = parsed_entities.get(section, [])
        if not items:
            continue
        has_substantive_content = True
        title = SECTION_TITLES[section]
        icon = SECTION_ICONS[section]
        if section == "rest_command":
            cards.append(build_bullet_markdown("Rest commands defined here", items, icon=icon))
        else:
            cards.append(build_entities_card(title, items))

    local_entities = {
        entity_id
        for section in SECTION_ORDER
        for entity_id in parsed_entities.get(section, [])
    }
    referenced = parsed_entities.get("referenced", [])
    referenced_defined_here = [entity_id for entity_id in referenced if entity_id in local_entities]
    referenced_external = [entity_id for entity_id in referenced if entity_id not in local_entities]

    local_stateful = [entity_id for entity_id in referenced_defined_here if is_stateful_entity(entity_id)]
    local_non_stateful = [entity_id for entity_id in referenced_defined_here if not is_stateful_entity(entity_id)]
    external_stateful = [entity_id for entity_id in referenced_external if is_stateful_entity(entity_id)]
    external_non_stateful = [entity_id for entity_id in referenced_external if not is_stateful_entity(entity_id)]

    if local_stateful:
        has_substantive_content = True
        cards.append(build_entities_card("Entities defined and used in this file", local_stateful))

    if local_non_stateful:
        has_substantive_content = True
        cards.append(build_bullet_markdown("Non-entity definitions used in this file", local_non_stateful, icon="mdi:source-branch"))

    if external_stateful:
        has_substantive_content = True
        cards.append(build_entities_card("Entities used from other files", external_stateful))

    if external_non_stateful:
        has_substantive_content = True
        cards.append(build_bullet_markdown("Non-entity references from other files", external_non_stateful, icon="mdi:format-list-bulleted"))

    if cross_refs is not None:
        this_file_rel = path.relative_to(root).as_posix()
        used_elsewhere: list[str] = []
        for section in SECTION_ORDER:
            for entity_id in parsed_entities.get(section, []):
                other_usages = [(f, ut) for f, ut in cross_refs.get(entity_id, []) if f != this_file_rel]
                if other_usages:
                    parts = [f"{f} ({ut})" for f, ut in other_usages]
                    used_elsewhere.append(f"- `{entity_id}`: " + ", ".join(parts))
        if used_elsewhere:
            has_substantive_content = True
            cards.append(build_markdown_card(
                "Entities from this file used elsewhere",
                "\n".join(used_elsewhere),
                icon="mdi:share-variant-outline",
            ))

    if not has_substantive_content:
        return None

    return {
        "path": slugify(f"{folder.relative_to(root).as_posix().replace('/', '-')}-{path.stem}"),
        "title": path.stem,
        "icon": "mdi:folder-open",
        "cards": cards,
    }


def format_yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def dump_yaml(data: Any, *, indent: int = 0) -> list[str]:
    lines: list[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            prefix = " " * indent + str(key) + ":"
            if isinstance(value, dict):
                if value:
                    lines.append(prefix)
                    lines.extend(dump_yaml(value, indent=indent + 2))
                else:
                    lines.append(prefix + " {}")
            elif isinstance(value, list):
                if value:
                    lines.append(prefix)
                    lines.extend(dump_yaml(value, indent=indent + 2))
                else:
                    lines.append(prefix + " []")
            elif isinstance(value, str) and "\n" in value:
                lines.append(prefix + " |")
                for line in value.splitlines():
                    lines.append(" " * (indent + 2) + line)
            else:
                lines.append(prefix + " " + format_yaml_scalar(value))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                if item:
                    lines.append(" " * indent + "-")
                    lines.extend(dump_yaml(item, indent=indent + 2))
                else:
                    lines.append(" " * indent + "- {}")
            elif isinstance(item, list):
                lines.append(" " * indent + "-")
                lines.extend(dump_yaml(item, indent=indent + 2))
            else:
                lines.append(" " * indent + "- " + format_yaml_scalar(item))
    else:
        lines.append(" " * indent + format_yaml_scalar(data))
    return lines


def write_dashboard(path: Path, dashboard: dict[str, Any]) -> None:
    text = "\n".join(dump_yaml(dashboard)) + "\n"
    path.write_text(text, encoding="utf-8")


def build_grouped_dashboard(
    *,
    root: Path,
    generated_at: str,
    name_map: dict[tuple[str, str], str] | None = None,
    available_entities: set[str] | None = None,
) -> dict[str, Any]:
    """Build a dashboard with one view per category.

    Each category view contains the full per-file detail (overview + entity
    cards) rendered as sequential cards, separated by a heading card so the
    user can still tell which file each block belongs to.
    """
    from collections import defaultdict

    groups: dict[str, list[tuple[Path, Path]]] = defaultdict(list)
    cat_icons: dict[str, str] = {}
    for folder, path in collect_source_file_items(root):
        rel = path.relative_to(root).as_posix()
        cat, icon = categorize_file(rel)
        groups[cat].append((folder, path))
        cat_icons.setdefault(cat, icon)

    views: list[dict[str, Any]] = []
    for cat, file_pairs in groups.items():
        icon = cat_icons[cat]
        cards: list[dict[str, Any]] = []
        for folder, path in file_pairs:
            flat_view_slug = slugify(
                f"{folder.relative_to(root).as_posix().replace('/', '-')}-{path.stem}"
            )
            cards.append({
                "type": "heading",
                "heading": path.stem.replace("_", " ").title(),
                "heading_style": "subtitle",
                "icon": "mdi:file-document-outline",
                "badges": [],
            })
            cards.append({
                "type": "button",
                "name": "Open detailed view",
                "icon": "mdi:open-in-new",
                "show_name": True,
                "show_icon": True,
                "tap_action": {
                    "action": "navigate",
                    "navigation_path": f"/ui-generated-flat/{flat_view_slug}",
                },
            })
            file_view = build_view_for_file(
                folder,
                path,
                generated_at=generated_at,
                root=root,
                name_map=name_map,
                available_entities=available_entities,
            )
            if file_view is not None:
                cards.extend(file_view["cards"])

        views.append({
            "path": slugify(cat),
            "title": cat,
            "icon": icon,
            "cards": cards,
        })

    return {
        "title": "Generated Home Assistant UI",
        "views": views,
    }


def build_entity_type_dashboard(
    *,
    root: Path,
    generated_at: str,
    name_map: dict[tuple[str, str], str] | None = None,
    available_entities: set[str] | None = None,
) -> dict[str, Any]:
    catalog = build_entity_type_catalog(root, name_map=name_map, available_entities=available_entities)
    views: list[dict[str, Any]] = []

    for section in SECTION_ORDER:
        entries = catalog.get(section, [])
        if not entries:
            continue

        entity_ids = [item["entity_id"] for item in entries]
        summary_lines = [
            f"# {SECTION_TITLES[section]}",
            "",
            f"- Generated: {generated_at}",
            f"- Total entries: {len(entity_ids)}",
            f"- Source files: {len({item['source'] for item in entries})}",
        ]
        cards: list[dict[str, Any]] = [
            build_markdown_card("Overview", "\n".join(summary_lines), icon="mdi:information-outline"),
        ]

        if section == "rest_command":
            cards.append(build_bullet_markdown("Definitions", entity_ids, icon=SECTION_ICONS[section]))
        else:
            cards.append(build_entities_card(SECTION_TITLES[section], entity_ids))

        views.append({
            "path": slugify(SECTION_TITLES[section]),
            "title": SECTION_TITLES[section],
            "icon": SECTION_ICONS[section],
            "cards": cards,
        })

    return {
        "title": "Entity Type Index",
        "views": views,
    }


def generate_grouped_dashboard(
    *,
    root: Path,
    output_dir: Path,
    generated_at: str,
    name_map: dict[tuple[str, str], str] | None = None,
    available_entities: set[str] | None = None,
) -> Path:
    dashboard = build_grouped_dashboard(
        root=root,
        generated_at=generated_at,
        name_map=name_map,
        available_entities=available_entities,
    )
    output_path = output_dir / "ui-generated-grouped.yaml"
    write_dashboard(output_path, dashboard)
    return output_path


def generate_single_dashboard(
    *,
    root: Path,
    output_dir: Path,
    generated_at: str,
    name_map: dict[tuple[str, str], str] | None = None,
    available_entities: set[str] | None = None,
) -> Path:
    file_items = collect_source_file_items(root)
    cross_refs = build_cross_reference_map(file_items, root=root, name_map=name_map, available_entities=available_entities)

    views = [
        view
        for folder, path in file_items
        if (view := build_view_for_file(
            folder,
            path,
            generated_at=generated_at,
            root=root,
            name_map=name_map,
            cross_refs=cross_refs,
            available_entities=available_entities,
        )) is not None
    ]

    dashboard = {
        "title": "Generated Home Assistant UI",
        "views": views,
    }

    output_path = output_dir / "ui-generated-flat.yaml"
    write_dashboard(output_path, dashboard)
    return output_path


def generate_entity_type_dashboard(
    *,
    root: Path,
    output_dir: Path,
    generated_at: str,
    name_map: dict[tuple[str, str], str] | None = None,
    available_entities: set[str] | None = None,
) -> Path:
    dashboard = build_entity_type_dashboard(
        root=root,
        generated_at=generated_at,
        name_map=name_map,
        available_entities=available_entities,
    )
    output_path = output_dir / "ui-generated-entity-types.yaml"
    write_dashboard(output_path, dashboard)
    return output_path


def generate_dashboards(
    *,
    root: Path | None = None,
    output_dir: Path | None = None,
    inventory_json: Path | None = None,
    include_entity_type_dashboard: bool = True,
) -> list[Path]:
    root_path = (root or ROOT).resolve()
    output_path = (output_dir or (root_path / "generated_ui")).resolve()
    name_map, available_entities = load_inventory(inventory_json.resolve()) if inventory_json else (None, None)
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    generated_files = [
        generate_single_dashboard(
            root=root_path,
            output_dir=output_path,
            generated_at=generated_at,
            name_map=name_map,
            available_entities=available_entities,
        ),
        generate_grouped_dashboard(
            root=root_path,
            output_dir=output_path,
            generated_at=generated_at,
            name_map=name_map,
            available_entities=available_entities,
        ),
    ]
    if include_entity_type_dashboard:
        generated_files.append(
            generate_entity_type_dashboard(
                root=root_path,
                output_dir=output_path,
                generated_at=generated_at,
                name_map=name_map,
                available_entities=available_entities,
            )
        )
    return generated_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate concise Home Assistant UI dashboards for each folder.")
    parser.add_argument("--root", default=str(ROOT), help="Root directory to scan")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory where generated UI files will be written")
    parser.add_argument("--inventory-json", default=None, help="Optional path to sanitized HA inventory export JSON for resolving real entity_ids")
    parser.add_argument("--entity-type-dashboard", action="store_true", help="Write the entity-type index dashboard")
    args = parser.parse_args()

    root_path = Path(args.root).resolve()
    output_dir = Path(args.output_dir).resolve()
    inventory_json = Path(args.inventory_json).resolve() if args.inventory_json else None
    generated = generate_dashboards(
        root=root_path,
        output_dir=output_dir,
        inventory_json=inventory_json,
        include_entity_type_dashboard=True,
    )
    print(f"Generated {len(generated)} dashboard files")
    for path in generated:
        print(path.relative_to(root_path).as_posix())


if __name__ == "__main__":
    main()
