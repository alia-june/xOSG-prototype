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
SPEC = importlib.util.spec_from_file_location("review_sample_dispositions", ROOT / "review_sample_dispositions.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReviewDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(MODULE.DECISION_PATH.read_text(encoding="utf-8"))
        MODULE.validate_decision(cls.decision)
        cls.report = json.loads(MODULE.REPORT_JSON_PATH.read_text(encoding="utf-8"))
        cls.regression = json.loads(MODULE.REGRESSION_PATH.read_text(encoding="utf-8"))
        cls.records = {}
        with gzip.open(MODULE.RECORDS_PATH, "rt", encoding="utf-8") as stream:
            for line in stream:
                record = json.loads(line)
                cls.records[record["historical_term"]] = record

    def test_scope_boundaries(self):
        self.assertFalse(self.decision["parser_repair_allowed"])
        self.assertFalse(self.decision["lexical_validity_assignment_allowed"])
        self.assertFalse(self.report["parser_repair_allowed"])

    def test_dispositions_reconcile(self):
        self.assertEqual(self.report["sample_record_count"], sum(self.report["disposition_counts"].values()))
        self.assertEqual(self.report["sample_record_count"], len(self.records))
        self.assertEqual(2, self.report["disposition_counts"]["PARSER_BOUNDARY_DEFECT_CONFIRMED"])
        self.assertEqual(251, self.report["disposition_counts"]["RAW_LITERAL_PRESENT_NO_LISTED_DEFECT"])
        self.assertEqual(5, self.report["disposition_counts"]["REVIEW_REQUIRED"])

    def test_known_discriminators(self):
        expected = {
            "1the word miscreant": "LEADING_FOOTNOTE_MARKER_CAPTURE",
            "527a": "BARE_SUFFIXED_HEAD_MARKER_CAPTURE",
        }
        for term, pattern in expected.items():
            record = self.records[term]
            self.assertEqual("PARSER_BOUNDARY_DEFECT_CONFIRMED", record["review_disposition"])
            self.assertEqual(pattern, record["defect_pattern"])
            self.assertTrue(record["evidence_lines"])
            self.assertIsNone(record["lexical_validity"])

    def test_regressions_require_repetition(self):
        proposed = {item["pattern"] for item in self.regression["candidates"]}
        held = {item["pattern"] for item in self.regression["held_below_threshold"]}
        self.assertFalse(proposed)
        self.assertNotIn("LEADING_FOOTNOTE_MARKER_CAPTURE", proposed)
        self.assertNotIn("BARE_SUFFIXED_HEAD_MARKER_CAPTURE", proposed)
        self.assertIn("LEADING_FOOTNOTE_MARKER_CAPTURE", held)
        self.assertIn("BARE_SUFFIXED_HEAD_MARKER_CAPTURE", held)
        for item in self.regression["candidates"]:
            self.assertGreaterEqual(item["sample_occurrences"], self.regression["minimum_sample_occurrences"])
            self.assertEqual("PROPOSED_TEST_ONLY", item["effect"])

    def test_receipt_hashes(self):
        receipt = json.loads(MODULE.RECEIPT_PATH.read_text(encoding="utf-8"))
        self.assertEqual("PASSED", receipt["status"])
        for output in receipt["outputs"].values():
            path = MODULE.OUTPUT_DIR / output["relative_path"]
            self.assertEqual(output["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
