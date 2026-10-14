"""Offline capture parsing/credential tests; never connect to a device."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("capture_pdos", ROOT / "scripts/capture_pdos.py")
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


class CaptureTests(unittest.TestCase):
    def test_frame_and_ansi(self):
        text = "\x1b[0;36m[D][comfoair_dump]: Node: 1, PDO: 305, rtr: 0, length: 2, content: 67.00 (can_id: 0x004c4041)\x1b[0m"
        self.assertEqual(capture.parse_frame(text),
                         {"node": 1, "pdo": 305, "rtr": False, "length": 2, "hex": "6700", "unsigned": 103})

    def test_remote_request(self):
        frame = capture.parse_frame("Node: 42, PDO: 212, rtr: 1, length: 0, content: n/a")
        self.assertTrue(frame["rtr"])
        self.assertIsNone(frame["unsigned"])

    def test_malformed_logs_are_ignored(self):
        for text in ("unrelated log", "Node: 1, PDO: 212, rtr: 0, length: 2, content: E9",
                     "Node: 1, PDO: 212, rtr: 0, length: 1, content: E",
                     "Node: 1, PDO: 212, rtr: 0, length: 9, content: 00.00.00.00.00.00.00.00.00"):
            self.assertIsNone(capture.parse_frame(text))

    def test_local_credentials_and_secrets(self):
        directory = ROOT / "tests/.esphome/credentials"
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as temporary:
            path = Path(temporary) / "device.yaml"
            (path.parent / "secrets.yaml").write_text("api_key: test-placeholder\n", encoding="utf-8")
            path.write_text("api:\n  encryption:\n    key: !secret api_key\nsensor:\n  - lambda: !lambda 'return 1;'\n", encoding="utf-8")
            self.assertEqual(capture.credentials(path), ("test-placeholder", None))
            path.write_text("api:\n  password: test-password\n", encoding="utf-8")
            self.assertEqual(capture.credentials(path), (None, "test-password"))


if __name__ == "__main__":
    unittest.main()
