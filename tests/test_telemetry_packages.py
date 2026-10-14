"""Validate optional PDO declarations and request-list behavior without hardware."""

import importlib.util
import json
from pathlib import Path
import re
import unittest

from esphome import config_validation as cv
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("telemetry_component", ROOT / "components/zehnder_comfoair_q/__init__.py")
component = importlib.util.module_from_spec(spec)
spec.loader.exec_module(component)


class Loader(yaml.SafeLoader):
    pass


Loader.add_constructor("!extend", lambda loader, node: loader.construct_scalar(node))


class TelemetryTests(unittest.TestCase):
    def test_request_ids_are_unique_and_ordered(self):
        config = component.CONFIG_SCHEMA({"id": "comfoair", "canbus_id": "bus", "request_ids": [65, 16, 65, 18, 16]})
        self.assertEqual(config["request_ids"], [65, 16, 18])

    def test_default_request_list_is_empty(self):
        config = component.CONFIG_SCHEMA({"id": "comfoair", "canbus_id": "bus"})
        self.assertEqual(config["request_ids"], [])

    def test_high_ids_remain_explicitly_unsupported(self):
        with self.assertRaises(cv.Invalid):
            component.CONFIG_SCHEMA({"id": "comfoair", "canbus_id": "bus", "request_ids": [1024]})

    def test_status_types_and_polling_match(self):
        package = yaml.load((ROOT / "packages/core_telemetry.yml").read_text(), Loader=Loader)
        code = package["canbus"][0]["on_frame"][0]["then"][0]["lambda"]
        matches = re.findall(r"comfoair_on_frame_case\((\d+), id\(comfoair\), (\w+)\)", code)
        self.assertEqual({int(pdo) for pdo, _ in matches}, set(package["zehnder_comfoair_q"]["request_ids"]))
        entities = {entity["id"] for kind in ("sensor", "text_sensor") for entity in package.get(kind, [])}
        self.assertEqual({name for _, name in matches}, entities)
        mapping = json.loads((ROOT / "components/zehnder_comfoair_q/pdo_mapping.json").read_text())
        types = {entry["id"]: entry["type"] for entry in mapping["pdos"]}
        for pdo, _ in matches:
            self.assertEqual(types[int(pdo)], "CN_UINT32" if int(pdo) in (338, 342, 343) else "CN_UINT8")
        self.assertNotIn("send_command", code)

    def test_timer_addresses_and_formatting(self):
        package = yaml.load((ROOT / "packages/fan_timers.yml").read_text(), Loader=Loader)
        frames = package["canbus"][0]["on_frame"]
        self.assertEqual([frame["can_id"] >> 14 for frame in frames], [86, 87])
        for frame in frames:
            self.assertTrue(frame["use_extended_id"])
            self.assertFalse(frame["remote_transmission_request"])
            self.assertIn("publish_duration_state", frame["then"][0]["lambda"])

    def test_preheater_declared_types_and_units(self):
        package = yaml.load((ROOT / "packages/preheater_telemetry.yml").read_text(), Loader=Loader)
        self.assertEqual(package["zehnder_comfoair_q"]["request_ids"], [144, 145, 146])
        self.assertEqual([sensor["unit_of_measurement"] for sensor in package["sensor"]], ["kWh", "kWh", "W"])
        code = package["canbus"][0]["on_frame"][0]["then"][0]["lambda"]
        self.assertNotIn("send_command", code)
        for pdo in (144, 145, 146):
            self.assertIn(f"comfoair_on_frame_case({pdo},", code)

    def test_analog_units_and_scale(self):
        package = yaml.load((ROOT / "packages/analog_inputs.yml").read_text(), Loader=Loader)
        self.assertEqual(package["zehnder_comfoair_q"]["request_ids"], [369, 370, 371, 372])
        for sensor in package["sensor"]:
            self.assertEqual(sensor["unit_of_measurement"], "V")
            self.assertEqual(sensor["filters"], [{"multiply": 0.1}])
        code = package["canbus"][0]["on_frame"][0]["then"][0]["lambda"]
        self.assertNotIn("send_command", code)

    def test_pressure_candidates_make_no_unit_or_side_claim(self):
        package = yaml.load((ROOT / "packages/unidentified_pressure_candidates.yml").read_text(), Loader=Loader)
        self.assertEqual(package["zehnder_comfoair_q"]["request_ids"], [305, 306])
        for sensor in package["sensor"]:
            self.assertNotIn("unit_of_measurement", sensor)
            self.assertNotIn("device_class", sensor)
            self.assertNotIn("filters", sensor)
        self.assertEqual([f["can_id"] >> 14 for f in package["canbus"][0]["on_frame"]], [305, 306])
        for frame in package["canbus"][0]["on_frame"]:
            self.assertIn("publish_raw_state", frame["then"][0]["lambda"])
            self.assertIn("PdoType::UINT16", frame["then"][0]["lambda"])


if __name__ == "__main__":
    unittest.main()
