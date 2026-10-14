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

    def test_comfofond_presence_and_availability(self):
        package = yaml.load((ROOT / "packages/comfofond_telemetry.yml").read_text(), Loader=Loader)
        self.assertEqual(package["zehnder_comfoair_q"]["request_ids"], [419, 416, 417, 418])
        for sensor in package["sensor"]:
            gate = sensor["filters"][0]["lambda"]
            self.assertIn("comfofond_present).has_state()", gate)
            self.assertIn("comfofond_present).state", gate)
            self.assertIn("NAN", gate)
        invalidation = package["binary_sensor"][0]["on_state"]["then"][0]["lambda"]
        for sensor in package["sensor"]:
            self.assertIn(f"id({sensor['id']}).publish_state(NAN)", invalidation)
        self.assertNotIn("send_command", invalidation)

    def test_comfocool_requires_explicit_hardware_declaration(self):
        package = yaml.load((ROOT / "packages/comfocool_telemetry.yml").read_text(), Loader=Loader)
        self.assertEqual(package["substitutions"]["comfocool_installed"], "false")
        requests = package["zehnder_comfoair_q"]["request_ids"]
        self.assertIn("comfocool_installed == 'true'", requests)
        self.assertIn("else []", requests)
        code = package["canbus"][0]["on_frame"][0]["then"][0]["lambda"]
        self.assertIn('if (installed != "true") return', code)
        self.assertIn("static_assert", code)
        self.assertNotIn("send_command", code)

    def test_comfocool_real_substitution_merge(self):
        from esphome.config import read_config
        from esphome.core import CORE
        import shutil
        secrets = ROOT / "tests/firmware/secrets.yaml"
        if not secrets.exists():
            shutil.copy2(ROOT / "secrets.yaml.example", secrets)
        try:
            for name, expected in (("comfocool_telemetry", [85, 784, 785, 802]), ("comfocool_disabled", [])):
                CORE.reset()
                CORE.config_path = ROOT / f"tests/firmware/{name}.yml"
                config = read_config({})
                self.assertIsNotNone(config)
                ids = [int(pdo) for pdo in config["zehnder_comfoair_q"]["request_ids"]]
                self.assertEqual([pdo for pdo in ids if pdo in (85, 784, 785, 802)], expected)
        finally:
            CORE.reset()

    def test_unidentified_package_is_passive_and_unscaled(self):
        package = yaml.load((ROOT / "packages/unidentified_telemetry.yml").read_text(), Loader=Loader)
        self.assertNotIn("zehnder_comfoair_q", package)
        self.assertEqual(len(package["text_sensor"]), 13)
        for entity in package["text_sensor"]:
            self.assertTrue(entity["disabled_by_default"])
            self.assertNotIn("filters", entity)
            self.assertNotIn("unit_of_measurement", entity)

    def test_reference_coverage_is_complete(self):
        spec = importlib.util.spec_from_file_location("check_coverage", ROOT / "scripts/check_pdo_coverage.py")
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        rows, handlers = audit.inventory()
        self.assertEqual(sum(row["registry"] for row in rows), 86)
        self.assertFalse([row for row in rows if row["registry"] and row["status"] != "mapped"])
        self.assertEqual(sorted(set(handlers) - {row["id"] for row in rows}), [305, 306])


if __name__ == "__main__":
    unittest.main()
