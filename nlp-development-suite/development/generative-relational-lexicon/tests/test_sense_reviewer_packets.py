from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "export_sense_reviewer_packets", ROOT / "export_sense_reviewer_packets.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SenseReviewerPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MODULE.MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.packets = {}
        for slot in MODULE.SLOTS:
            path = MODULE.OUTPUT_DIR / cls.manifest["outputs"][slot]["relative_path"]
            with gzip.open(path, "rt", encoding="utf-8") as stream:
                cls.packets[slot] = [json.loads(line) for line in stream]

    def test_two_packets_have_expected_size(self):
        self.assertEqual(2, len(self.packets))
        self.assertTrue(all(len(records) == 34 for records in self.packets.values()))

    def test_packets_are_source_identical(self):
        left = self.packets["reviewer_a"]
        right = self.packets["reviewer_b"]
        for a, b in zip(left, right):
            self.assertEqual(a["calibration_id"], b["calibration_id"])
            self.assertEqual(a["source_sample_id"], b["source_sample_id"])
            self.assertEqual(a["historical_evidence"], b["historical_evidence"])
            self.assertEqual(a["selection"], b["selection"])

    def test_packets_expose_only_one_review_slot(self):
        for slot, records in self.packets.items():
            for record in records:
                self.assertEqual(slot, record["reviewer_slot"])
                self.assertIn("review", record)
                self.assertNotIn("reviewer_a", record)
                self.assertNotIn("reviewer_b", record)
                self.assertNotIn("adjudication", record)
                self.assertTrue(all(value is None for value in record["review"].values()))

    def test_manifest_hashes(self):
        for output in self.manifest["outputs"].values():
            path = MODULE.OUTPUT_DIR / output["relative_path"]
            self.assertEqual(output["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_manifest_authority_boundary(self):
        self.assertEqual("GENERATED_BLANK_INDEPENDENT_PACKETS", self.manifest["status"])
        self.assertFalse(self.manifest["production_ready"])
        self.assertFalse(self.manifest["publication_allowed"])
        self.assertFalse(self.manifest["canon_admission"])


if __name__ == "__main__":
    unittest.main()
