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
SPEC = importlib.util.spec_from_file_location("audit_surface_normalization", ROOT / "audit_surface_normalization.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class NormalizationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(MODULE.DECISION_PATH.read_text(encoding="utf-8"))
        cls.baseline_receipt = MODULE.validate_audit_decision(cls.decision)
        cls.report = json.loads(MODULE.REPORT_JSON_PATH.read_text(encoding="utf-8"))
        cls.records = {}
        with gzip.open(MODULE.RECORDS_PATH, "rt", encoding="utf-8") as stream:
            for line in stream:
                record = json.loads(line)
                cls.records[record["historical_term"]] = record

    def test_decision_is_test_only_and_ordered(self):
        self.assertEqual("TEST_AUDIT_ONLY", self.decision["authority_effect"])
        self.assertFalse(self.decision["semantic_equivalence_allowed"])
        self.assertEqual(list(MODULE.LAYER_FUNCTIONS), [item["id"] for item in self.decision["ordered_layers"]])

    def test_funnel_reconciles(self):
        counts = self.report["exclusive_first_recovery_counts"]
        self.assertEqual(self.report["baseline_unmatched_count"], sum(counts.values()))
        self.assertEqual(self.report["historical_term_count"], self.report["baseline_exact_primary_count"] + sum(counts.values()))
        self.assertEqual(self.report["remaining_unresolved_count"], counts["UNRESOLVED"])

    def test_known_layers_do_not_imply_equivalence(self):
        self.assertEqual("EXACT_INDEXED_FORM", self.records["admitted"]["first_recovery_layer"])
        self.assertEqual("SEPARATOR_TO_SPACE", self.records["air tight"]["first_recovery_layer"])
        self.assertEqual("SEPARATOR_ELIDED", self.records["a light"]["first_recovery_layer"])
        self.assertEqual("LOOSE_COLLISION_PRONE_CANDIDATE", self.records["a light"]["risk"])
        self.assertFalse(self.records["a light"]["semantic_equivalence"])

    def test_looser_separator_rule_exposes_more_collision_pressure(self):
        stats = self.report["modern_index_collision_stats"]
        self.assertGreater(
            stats["SEPARATOR_ELIDED"]["multi_surface_key_count"],
            stats["SEPARATOR_TO_SPACE"]["multi_surface_key_count"],
        )

    def test_records_exclude_expressive_dictionary_content(self):
        forbidden = {"definition", "definitions", "example", "examples", "gloss"}
        for record in self.records.values():
            self.assertFalse(forbidden & record.keys())

    def test_receipt_hashes(self):
        receipt = json.loads(MODULE.RECEIPT_PATH.read_text(encoding="utf-8"))
        self.assertEqual("PASSED", receipt["status"])
        for output in receipt["outputs"].values():
            path = MODULE.OUTPUT_DIR / output["relative_path"]
            self.assertEqual(output["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
