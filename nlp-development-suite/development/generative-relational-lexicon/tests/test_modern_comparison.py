from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("compare_roget_oewn", ROOT / "compare_roget_oewn.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ModernComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads((ROOT / "MODERN_COMPARISON_DECISION.json").read_text(encoding="utf-8"))
        cls.database = MODULE.validate_decision(cls.decision)
        cls.historical = MODULE.load_historical()
        cls.modern, cls.relation_counts, cls.inventory = MODULE.load_modern(cls.database)
        cls.report = json.loads(MODULE.REPORT_JSON_PATH.read_text(encoding="utf-8"))

    def test_comparison_is_structural_and_non_production(self):
        self.assertEqual("TEST_COMPARISON_ONLY", self.decision["authority_effect"])
        self.assertFalse(self.decision["production_ready"])
        self.assertFalse(self.decision["publication_allowed"])
        self.assertIn("definitions", self.decision["excluded_fields"])
        self.assertIn("examples", self.decision["excluded_fields"])

    def test_primary_form_rank_regression(self):
        subset = {term: self.historical[term] for term in ("existence", "identity", "precision", "truth")}
        records = MODULE.compare_terms(subset, self.modern, self.relation_counts)
        by_term = {record["normalized_term"]: record for record in records}
        for term in subset:
            self.assertTrue(by_term[term]["modern_exact_lemma"], term)
            self.assertGreater(by_term[term]["modern_sense_count"], 0)

    def test_report_reconciles_without_explaining_discrepancies(self):
        total = self.report["historical_unique_term_count"]
        self.assertEqual(total, self.report["exact_modern_lemma_count"] + self.report["no_exact_modern_lemma_count"])
        self.assertEqual(total, sum(self.report["modern_sense_count_buckets"].values()))
        self.assertEqual(total, sum(self.report["historical_head_count_buckets"].values()))
        self.assertIn("do not identify", self.report["interpretation_boundary"])
        self.assertIn("segmentation candidates", self.report["candidate_quality_boundary"])

    def test_records_exclude_expressive_dictionary_content(self):
        forbidden = {"definition", "definitions", "example", "examples", "gloss"}
        count = 0
        with gzip.open(MODULE.RECORDS_PATH, "rt", encoding="utf-8") as stream:
            for line in stream:
                record = json.loads(line)
                self.assertFalse(forbidden & record.keys())
                count += 1
        self.assertEqual(self.report["historical_unique_term_count"], count)

    def test_checked_receipt_hashes_exist(self):
        receipt = json.loads(MODULE.RECEIPT_PATH.read_text(encoding="utf-8"))
        self.assertEqual("PASSED", receipt["status"])
        historical = receipt["inputs"]["historical_memberships"]
        self.assertEqual(historical["sha256"], hashlib.sha256(MODULE.HISTORICAL_PATH.read_bytes()).hexdigest())
        modern = receipt["inputs"]["modern_database"]
        self.assertEqual(modern["sha256"], hashlib.sha256(self.database.read_bytes()).hexdigest())
        for output in receipt["outputs"].values():
            path = MODULE.OUTPUT_DIR / output["relative_path"]
            self.assertTrue(path.is_file())
            self.assertEqual(output["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
