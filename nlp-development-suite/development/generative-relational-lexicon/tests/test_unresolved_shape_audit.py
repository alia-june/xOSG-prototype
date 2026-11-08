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
SPEC = importlib.util.spec_from_file_location("audit_unresolved_shapes", ROOT / "audit_unresolved_shapes.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class UnresolvedShapeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(MODULE.DECISION_PATH.read_text(encoding="utf-8"))
        MODULE.validate_decision(cls.decision)
        cls.report = json.loads(MODULE.REPORT_JSON_PATH.read_text(encoding="utf-8"))
        cls.records = {}
        with gzip.open(MODULE.RECORDS_PATH, "rt", encoding="utf-8") as stream:
            for line in stream:
                record = json.loads(line)
                cls.records[record["historical_term"]] = record

    def test_decision_preserves_unknowns(self):
        self.assertFalse(self.decision["lexical_validity_assignment_allowed"])
        self.assertFalse(self.decision["cause_assignment_allowed"])
        self.assertEqual("PROPOSAL_ONLY", self.decision["review_queue_effect"])

    def test_exclusive_shapes_reconcile(self):
        counts = self.report["exclusive_primary_shape_counts"]
        self.assertEqual(self.report["unresolved_term_count"], sum(counts.values()))
        self.assertEqual(set(MODULE.PRIMARY_SHAPES), set(counts))
        self.assertEqual(self.report["unresolved_term_count"], len(self.records))

    def test_known_visible_shapes(self):
        expected = {
            "ablepsy|": "DELIMITER_OR_MARKUP_SHAPED",
            "1st class carriage": "NUMERIC_MIXED_SHAPED",
            "abacist": "SINGLE_TOKEN_LETTER_SHAPED",
            "a bee": "MULTI_TOKEN_LETTER_SHAPED",
            "a$": "OTHER_SURFACE_SHAPED",
        }
        for term, shape in expected.items():
            self.assertEqual(shape, self.records[term]["primary_shape"])
            self.assertIsNone(self.records[term]["lexical_validity"])
            self.assertIsNone(self.records[term]["cause"])

        # Suffixed Roget head markers are structure in parser v4, not lexical
        # candidates for this unresolved-shape audit.
        self.assertNotIn("#100a", self.records)

    def test_source_evidence_is_retained(self):
        for record in self.records.values():
            self.assertGreater(record["historical_membership_count"], 0)
            self.assertTrue(record["historical_head_numbers"])
            self.assertTrue(record["historical_pos_markers"])
            self.assertTrue(record["source_line_spans"])

    def test_source_labels_remain_literal_evidence(self):
        labels = self.report["top_source_bracket_labels"]
        self.assertTrue(labels)
        self.assertEqual("[obs3]", labels[0]["label"])
        self.assertIn("not automatically interpreted", self.report["source_label_boundary"])

    def test_receipt_hashes(self):
        receipt = json.loads(MODULE.RECEIPT_PATH.read_text(encoding="utf-8"))
        self.assertEqual("PASSED", receipt["status"])
        for output in receipt["outputs"].values():
            path = MODULE.OUTPUT_DIR / output["relative_path"]
            self.assertEqual(output["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
