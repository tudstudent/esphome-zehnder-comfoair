"""Pressure log parsing is data handling, never protocol-type inference."""

import unittest
from scripts.capture_pressure_properties import parse_result


class PressureResultTests(unittest.TestCase):
    def test_matching_raw_result(self):
        result = parse_result("[D][pressure_rmi]: subunit: 1, property: 3, error: 0, length: 2, data: 67.00 (2)")
        self.assertEqual(result, {"subunit": 1, "property": 3, "error": False, "hex": "6700", "length": 2})
        self.assertNotIn("pressure", result)
        self.assertNotIn("type", result)

    def test_error_is_preserved(self):
        result = parse_result("subunit: 2, property: 7, error: 1, length: 1, data: 0E")
        self.assertTrue(result["error"])
        self.assertEqual(result["hex"], "0e")

    def test_invalid_length_and_unrelated_logs(self):
        self.assertIsNone(parse_result("ordinary PDO log"))
        self.assertIsNone(parse_result("subunit: 1, property: 3, error: 0, length: 2, data: 67"))
        self.assertIsNone(parse_result("subunit: 1, property: 3, error: 0, length: 1, data: garbage"))


if __name__ == "__main__":
    unittest.main()
