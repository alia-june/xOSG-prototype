from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("measure_parser_repair", ROOT / "measure_parser_repair.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ParserRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(MODULE.DECISION_PATH.read_text(encoding="utf-8"))
        MODULE.validate_decision(cls.decision)
        cls.report = json.loads(MODULE.REPORT_JSON_PATH.read_text(encoding="utf-8"))

    def test_repair_is_test_only(self):
        self.assertEqual("TEST_PARSER_REPAIR_ONLY", self.decision["authority_effect"])
        self.assertFalse(self.decision["production_ready"])
        self.assertFalse(self.decision["publication_allowed"])
        self.assertFalse(self.decision["canon_admission"])

    def test_complete_output_deltas_reconcile(self):
        self.assertEqual("PASSED", self.report["status"])
        self.assertEqual(43, self.report["delta_after_minus_before"]["head_record_count"])
        self.assertEqual(-756, self.report["delta_after_minus_before"]["historical_membership_count"])
        self.assertEqual(-566, self.report["delta_after_minus_before"]["historical_unique_term_count"])
        self.assertEqual(108, self.report["delta_after_minus_before"]["exact_modern_lemma_count"])
        self.assertEqual(-674, self.report["delta_after_minus_before"]["no_exact_modern_lemma_count"])
        self.assertEqual(-682, self.report["delta_after_minus_before"]["remaining_unresolved_count"])

    def test_authorized_patterns_have_no_new_sample_residual(self):
        self.assertEqual(
            set(self.decision["authorized_repeated_patterns"]),
            set(self.report["authorized_pattern_residuals_in_new_sample"]),
        )
        self.assertFalse(any(self.report["authorized_pattern_residuals_in_new_sample"].values()))
        self.assertEqual(1, self.report["held_pattern_observations_in_new_sample"]["BARE_SUFFIXED_HEAD_MARKER_CAPTURE"])
        self.assertEqual(1, self.report["held_pattern_observations_in_new_sample"]["LEADING_FOOTNOTE_MARKER_CAPTURE"])

    def test_receipt_hashes(self):
        receipt = json.loads(MODULE.RECEIPT_PATH.read_text(encoding="utf-8"))
        self.assertEqual("PASSED", receipt["status"])
        for output in receipt["outputs"].values():
            path = MODULE.OUTPUT_DIR / output["relative_path"]
            self.assertEqual(output["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
