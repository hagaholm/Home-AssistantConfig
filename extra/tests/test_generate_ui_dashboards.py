import shutil
import tempfile
import unittest
import json
from pathlib import Path

from extra.generate_ui_dashboards import generate_dashboards


class GenerateUiDashboardsTests(unittest.TestCase):
    def test_generates_dashboard_for_folder_with_tabs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages"
            folder.mkdir()
            (folder / "alerts.yaml").write_text(
                "automation:\n  test_alert:\n    alias: Test alert\n",
                encoding="utf-8",
            )
            (folder / "notes.txt").write_text("Useful notes\n", encoding="utf-8")

            generated_files = generate_dashboards(root=root, output_dir=output_dir)

            self.assertGreaterEqual(len(generated_files), 1)
            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("title:", content)
            self.assertIn("alerts", content)
            self.assertIn("automation.test_alert", content)
            self.assertNotIn("Useful notes", content)

    def test_generates_dashboard_for_nested_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            nested_folder = root / "packages" / "alerts"
            nested_folder.mkdir(parents=True)
            (nested_folder / "config.yaml").write_text(
                "automation:\n  test_alert:\n    alias: Nested alert\n",
                encoding="utf-8",
            )

            generated_files = generate_dashboards(root=root, output_dir=output_dir)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("automation.test_alert", content)

    def test_treats_commented_yaml_as_meaningful(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "group"
            folder.mkdir()
            (folder / "group.yaml").write_text(
                "# Header comment\n# Another comment\nautomation:\n  test_alert:\n    alias: Commented alert\n",
                encoding="utf-8",
            )

            generated_files = generate_dashboards(root=root, output_dir=output_dir)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("automation.test_alert", content)

    def test_includes_packages_automations_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages" / "automations"
            folder.mkdir(parents=True)
            (folder / "global.yaml").write_text(
                "automation:\n  - alias: Global automation\n",
                encoding="utf-8",
            )

            generated_files = generate_dashboards(root=root, output_dir=output_dir)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("automation.global_automation", content)

    def test_extracts_sensor_entities_from_monitored_conditions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "sensor"
            folder.mkdir()
            (folder / "trafikverket.yaml").write_text(
                "sensor:\n  - platform: trafikverket_weatherstation\n    name: Trafikverket Gröndal\n    monitored_conditions:\n      - air_temp\n      - road_temp\n",
                encoding="utf-8",
            )

            generated_files = generate_dashboards(root=root, output_dir=output_dir)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("sensor.trafikverket_grondal_air_temp", content)
            self.assertIn("sensor.trafikverket_grondal_road_temp", content)

    def test_extracts_mqtt_sensor_entities_from_name_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages" / "integrations"
            folder.mkdir(parents=True)
            (folder / "mqtt.yaml").write_text(
                "mqtt:\n"
                "  sensor:\n"
                "    - state_topic: hassbian/1wire/ute\n"
                "      name: Ute\n"
                "    - state_topic: hassbian/1wire/sovrum\n"
                "      name: Sovrum\n",
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("sensor.ute", content)
            self.assertIn("sensor.sovrum", content)

    def test_extracts_mqtt_similar_entities_from_name_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages" / "integrations"
            folder.mkdir(parents=True)
            (folder / "mqtt_similar.yaml").write_text(
                "mqtt:\n"
                "  binary_sensor:\n"
                "    - state_topic: hassbian/door/contact\n"
                "      name: Friggebod Door\n"
                "  switch:\n"
                "    - state_topic: hassbian/heater/state\n"
                "      name: Friggebod Heater\n",
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("Binary sensors", content)
            self.assertIn("Switches", content)
            self.assertIn("binary_sensor.friggebod_door", content)
            self.assertIn("switch.friggebod_heater", content)

    def test_script_mapping_alias_does_not_create_extra_script_entity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages" / "lights"
            folder.mkdir(parents=True)
            (folder / "bathroom_like.yaml").write_text(
                "script:\n"
                "  bathroom_light_day:\n"
                "    alias: Badrumsbelysning dag\n"
                "    sequence: []\n"
                "automation:\n"
                "  - alias: Trigger test\n"
                "    action:\n"
                "      - service: script.bathroom_light_day\n",
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("script.bathroom_light_day", content)
            self.assertNotIn("script.badrumsbelysning_dag", content)

    def test_extracts_helper_entities(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages" / "helpers"
            folder.mkdir(parents=True)
            (folder / "helpers.yaml").write_text(
                "input_boolean:\n"
                "  christmas_light:\n"
                "    name: Christmas\n"
                "input_datetime:\n"
                "  some_timeout:\n"
                "    has_date: true\n"
                "    has_time: true\n"
                "input_select:\n"
                "  home_status:\n"
                "    options:\n"
                "      - Home\n",
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("input_boolean.christmas_light", content)
            self.assertIn("input_datetime.some_timeout", content)
            self.assertIn("input_select.home_status", content)

    def test_filters_entities_not_present_in_inventory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages" / "lights"
            folder.mkdir(parents=True)
            (folder / "lights.yaml").write_text(
                "light:\n"
                "  bedroom:\n"
                "    name: Bedroom\n"
                "  kitchen:\n"
                "    name: Kitchen\n",
                encoding="utf-8",
            )
            inventory_path = root / "inventory.json"
            inventory_path.write_text(
                json.dumps({"entities": [{"entity_id": "light.bedroom", "original_name": "Bedroom"}]}),
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir, inventory_json=inventory_path)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("light.bedroom", content)
            self.assertNotIn("light.kitchen", content)

    def test_skips_views_with_no_substantive_cards(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages"
            folder.mkdir()
            (folder / "empty.yaml").write_text(
                "sensor: []\n",
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertNotIn('title: "empty"', content)
            self.assertNotIn('path: "empty"', content)

    def test_generates_single_dashboard_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages"
            folder.mkdir()
            (folder / "alerts.yaml").write_text(
                "automation:\n  - alias: Single file alert\n",
                encoding="utf-8",
            )

            generated_files = generate_dashboards(root=root, output_dir=output_dir)

            self.assertEqual(len(generated_files), 3)
            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            entity_type_path = output_dir / "ui-generated-entity-types.yaml"
            self.assertTrue(entity_type_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("automation.single_file_alert", content)
            self.assertIn("title: \"Generated Home Assistant UI\"", content)

    def test_extracts_multiple_automations_using_alias_entity_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages" / "integrations"
            folder.mkdir(parents=True)
            (folder / "rest_command.yaml").write_text(
                "automation:\n"
                "  - alias: First automation\n"
                "    id: first_internal_id\n"
                "    trigger:\n"
                "      - platform: homeassistant\n"
                "        event: start\n"
                "  - alias: Second automation\n"
                "    id: second_internal_id\n"
                "    trigger:\n"
                "      - platform: homeassistant\n"
                "        event: start\n",
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("automation.first_automation", content)
            self.assertIn("automation.second_automation", content)
            self.assertNotIn("automation.first_internal_id", content)
            self.assertNotIn("automation.second_internal_id", content)

    def test_splits_local_and_external_references(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages"
            folder.mkdir()
            (folder / "mixed.yaml").write_text(
                "script:\n"
                "  local_script:\n"
                "    alias: Local script\n"
                "    sequence:\n"
                "      - service: script.local_script\n"
                "      - service: light.turn_on\n"
                "        target:\n"
                "          entity_id: light.kitchen\n",
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("Entities defined and used in this file", content)
            self.assertIn("script.local_script", content)
            self.assertIn("Entities used from other files", content)
            self.assertIn("light.kitchen", content)

    def test_renders_rest_commands_as_non_entity_definitions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages" / "integrations"
            folder.mkdir(parents=True)
            (folder / "rest_command.yaml").write_text(
                "rest_command:\n"
                "  send_data:\n"
                "    url: https://example.com\n"
                "automation:\n"
                "  - alias: Send data\n"
                "    action:\n"
                "      - service: rest_command.send_data\n"
                "      - service: light.turn_on\n"
                "        target:\n"
                "          entity_id: light.kitchen\n",
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("Rest commands defined here", content)
            self.assertIn("rest_command.send_data", content)
            self.assertIn("Entities used from other files", content)
            self.assertIn("light.kitchen", content)

    def test_resolves_automation_entity_ids_from_inventory_export(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages" / "automations"
            folder.mkdir(parents=True)
            (folder / "input_select_light_control.yaml").write_text(
                "automation:\n"
                "  - alias: Media av vid Sover\n"
                "    id: media_off_on_sleep\n",
                encoding="utf-8",
            )

            inventory_path = root / "ha_inventory.sanitized.json"
            inventory_path.write_text(
                json.dumps(
                    {
                        "entities": [
                            {
                                "entity_id": "automation.media_och_varmekallor_av_vid_sover",
                                "original_name": "Media av vid Sover",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir, inventory_json=inventory_path)

            output_path = output_dir / "ui-generated-flat.yaml"
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("automation.media_och_varmekallor_av_vid_sover", content)
            self.assertNotIn("automation.media_av_vid_sover", content)


    def test_grouped_mode_produces_category_views(self):
        """--grouped yields one view per category, not one per file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            (root / "packages" / "lights").mkdir(parents=True)
            (root / "packages" / "lights" / "bathroom.yaml").write_text(
                "script:\n  bathroom_light_day:\n    alias: Day light\n    sequence: []\n",
                encoding="utf-8",
            )
            (root / "packages" / "climate").mkdir(parents=True)
            (root / "packages" / "climate" / "forrad.yaml").write_text(
                "input_boolean:\n  forrad_varme_auto:\n    name: Förråd värme\n",
                encoding="utf-8",
            )

            generated = generate_dashboards(root=root, output_dir=output_dir)
            output_path = output_dir / "ui-generated-grouped.yaml"
            self.assertEqual(len(generated), 3)
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")

            # Should have category-level views, not file-level
            self.assertIn("title: \"Lights\"", content)
            self.assertIn("title: \"Climate & HVAC\"", content)
            # Full entity detail still present
            self.assertIn("script.bathroom_light_day", content)
            self.assertIn("input_boolean.forrad_varme_auto", content)
            # File-level heading separator present inside view
            self.assertIn("Bathroom", content)
            self.assertIn("Forrad", content)

    def test_grouped_mode_uses_heading_cards_as_separators(self):
        """Each file inside a category view is preceded by a heading card."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages" / "lights"
            folder.mkdir(parents=True)
            (folder / "hall.yaml").write_text(
                "script:\n  hall_light_off:\n    alias: Hall off\n    sequence: []\n",
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir)

            content = (output_dir / "ui-generated-grouped.yaml").read_text(encoding="utf-8")
            self.assertIn("type: \"heading\"", content)
            self.assertIn("Hall", content)

    def test_grouped_mode_single_file_flag_still_works(self):
        """Both output files are always generated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            folder = root / "packages"
            folder.mkdir()
            (folder / "alerts.yaml").write_text(
                "automation:\n  - alias: Test alert\n",
                encoding="utf-8",
            )

            generated = generate_dashboards(root=root, output_dir=output_dir)
            self.assertTrue((output_dir / "ui-generated-flat.yaml").exists())
            self.assertTrue((output_dir / "ui-generated-grouped.yaml").exists())
            content = (output_dir / "ui-generated-flat.yaml").read_text(encoding="utf-8")
            # Flat mode: individual file path in view
            self.assertIn("alerts", content)

    def test_flat_view_shows_used_elsewhere_with_usage_type(self):
        """Flat view shows which files use a defined entity and whether read or write."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            (root / "packages" / "helpers").mkdir(parents=True)
            (root / "packages" / "helpers" / "defs.yaml").write_text(
                "input_boolean:\n  vacation_mode:\n    name: Vacation\n",
                encoding="utf-8",
            )
            (root / "packages" / "automations").mkdir(parents=True)
            # condition reference → read
            (root / "packages" / "automations" / "auto.yaml").write_text(
                "automation:\n"
                "  - alias: Vacation on\n"
                "    condition:\n"
                "      - condition: state\n"
                "        entity_id: input_boolean.vacation_mode\n"
                "        state: 'on'\n",
                encoding="utf-8",
            )
            # service call → write
            (root / "packages" / "scripts").mkdir(parents=True)
            (root / "packages" / "scripts" / "enable.yaml").write_text(
                "script:\n"
                "  enable_vacation:\n"
                "    alias: Enable vacation\n"
                "    sequence:\n"
                "      - service: input_boolean.turn_on\n"
                "        target:\n"
                "          entity_id: input_boolean.vacation_mode\n",
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir)
            content = (output_dir / "ui-generated-flat.yaml").read_text(encoding="utf-8")

            self.assertIn("Entities from this file used elsewhere", content)
            self.assertIn("input_boolean.vacation_mode", content)
            self.assertIn("packages/automations/auto.yaml", content)
            self.assertIn("packages/scripts/enable.yaml", content)
            # usage types annotated
            self.assertIn("(read)", content)
            self.assertIn("(write)", content)

    def test_grouped_view_has_navigate_button_to_flat(self):
        """Each file section in the grouped view has a button linking to the flat view."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_dir = root / "out"
            output_dir.mkdir()

            (root / "packages" / "lights").mkdir(parents=True)
            (root / "packages" / "lights" / "hall.yaml").write_text(
                "script:\n  hall_off:\n    alias: Hall off\n    sequence: []\n",
                encoding="utf-8",
            )

            generate_dashboards(root=root, output_dir=output_dir)
            content = (output_dir / "ui-generated-grouped.yaml").read_text(encoding="utf-8")

            self.assertIn('type: "button"', content)
            self.assertIn("navigation_path:", content)
            self.assertIn("/ui-generated-flat/", content)
            # slug should contain the file name (hyphens slugified to underscores)
            self.assertIn("packages_lights_hall", content)


if __name__ == "__main__":
    unittest.main()
