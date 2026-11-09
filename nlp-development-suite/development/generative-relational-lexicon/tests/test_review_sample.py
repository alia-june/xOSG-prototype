from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SPEC = importlib.util.spec_from_file_location("build_review_sample", ROOT / "build_review_sample.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReviewSampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(MODULE.DECISION_PATH.read_text(encoding="utf-8"))
        MODULE.validate_decision(cls.decision)
        cls.report = json.loads(MODULE.REPORT_JSON_PATH.read_text(encoding="utf-8"))
        cls.records = []
        with gzip.open(MODULE.RECORDS_PATH, "rt", encoding="utf-8") as stream:
            for line in stream:
                cls.records.append(json.loads(line))

    def test_decision_is_test_only(self):
        self.assertEqual("TEST_REVIEW_SAMPLE_ONLY", self.decision["authority_effect"])
        self.assertFalse(self.decision["review_disposition_assignment_allowed"])

    def test_sample_is_stratified_and_bounded(self):
        self.assertEqual(self.report["sample_record_count"], len(self.records))
        counts = {}
        for record in self.records:
            key = (record["primary_shape"], "+".join(record["historical_pos_markers"]) or "NONE")
            counts[key] = counts.get(key, 0) + 1
        self.assertTrue(counts)
        self.assertLessEqual(max(counts.values()), self.decision["source_sample_rule"]["maximum_per_stratum"])

    def test_raw_blocks_are_pinned_and_present(self):
        source_lines = MODULE.SOURCE_PATH.read_text(encoding="utf-8").splitlines()
        for record in self.records:
            self.assertIsNone(record["review_disposition"])
            self.assertIsNone(record["review_notes"])
            self.assertTrue(record["raw_source_blocks"])
            for block in record["raw_source_blocks"]:
                self.assertIn(block["text"].splitlines()[0], source_lines)

    def test_receipt_hashes(self):
        receipt = json.loads(MODULE.RECEIPT_PATH.read_text(encoding="utf-8"))
        self.assertEqual("PASSED", receipt["status"])
        for output in receipt["outputs"].values():
            path = MODULE.OUTPUT_DIR / output["relative_path"]
            self.assertEqual(output["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
