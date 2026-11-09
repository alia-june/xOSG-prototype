from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_sense_review_sample", ROOT / "build_sense_review_sample.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SenseReviewSampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = MODULE.read_json(MODULE.DECISION_PATH)
        MODULE.validate_decision(cls.decision)
        cls.report = MODULE.read_json(MODULE.REPORT_PATH)
        cls.receipt = MODULE.read_json(MODULE.RECEIPT_PATH)
        cls.records = []
        with gzip.open(MODULE.RECORDS_PATH, "rt", encoding="utf-8") as stream:
            for line in stream:
                cls.records.append(json.loads(line))

    def test_authority_is_blank_review_only(self):
        self.assertFalse(self.decision["review_disposition_assignment_allowed"])
        self.assertFalse(self.decision["semantic_candidate_generation_allowed"])
        self.assertFalse(self.report["canon_admission"])
        self.assertEqual("TEST_BLANK_REVIEW_PACKAGE_ONLY", self.report["authority_effect"])

    def test_population_strata_and_sample_reconcile(self):
        self.assertEqual(59636, self.report["population_record_count"])
        self.assertEqual(853, self.report["observed_stratum_count"])
        self.assertEqual(853, self.report["sample_record_count"])
        self.assertEqual(853, len(self.records))
        stratum_keys = [record["selection"]["stratum_key"] for record in self.records]
        self.assertEqual(len(stratum_keys), len(set(stratum_keys)))

    def test_every_review_field_is_null(self):
        for record in self.records:
            self.assertEqual(set(MODULE.NULL_REVIEW_FIELDS), set(record["review"]))
            self.assertTrue(all(value is None for value in record["review"].values()))
            self.assertEqual("BLANK_REVIEW_ONLY", record["authority_effect"])
        self.assertEqual(853 * len(MODULE.NULL_REVIEW_FIELDS), self.report["null_review_field_count"])

    def test_selection_rank_is_reproducible(self):
        source_hash = hashlib.sha256(MODULE.SOURCE_PATH.read_bytes()).hexdigest()
        for record in self.records:
            selection = record["selection"]
            material = "|".join(
                (source_hash, record["normalized_term"], selection["stratum_key"])
            ).encode("utf-8")
            self.assertEqual(hashlib.sha256(material).hexdigest(), selection["selection_rank"])

    def test_all_sampling_dimensions_are_represented(self):
        counts = self.report["counts_by_dimension"]
        self.assertEqual(
            {"EXACT_MODERN_LEMMA", "EXACT_INDEXED_FORM", "SEPARATOR_TO_SPACE", "SEPARATOR_ELIDED", "UNRESOLVED"},
            set(counts["match_layer"]),
        )
        self.assertEqual({"1", "2", "3-5", "6+"}, set(counts["historical_head_bucket"]))
        self.assertEqual({"ATTACHED", "NONE"}, set(counts["source_label_bucket"]))
        self.assertEqual({"0", "1", "2_PLUS"}, set(counts["modern_surface_collision_bucket"]))
        self.assertIn("REFERENCE_MARKER_SHAPED", counts["unresolved_primary_shape"])

    def test_source_spans_are_attached_and_bounded(self):
        source_lines = MODULE.SOURCE_PATH.read_text(encoding="utf-8").splitlines()
        source_hash = hashlib.sha256(MODULE.SOURCE_PATH.read_bytes()).hexdigest()
        for record in self.records:
            historical = record["historical_evidence"]
            self.assertEqual(source_hash, historical["source_sha256"])
            self.assertTrue(historical["memberships"])
            for membership in historical["memberships"]:
                start = membership["source_line_start"]
                end = membership["source_line_end"]
                self.assertGreaterEqual(start, 1)
                self.assertGreaterEqual(end, start)
                self.assertLessEqual(end, len(source_lines))
                self.assertEqual("\n".join(source_lines[start - 1 : end]), membership["raw_source_text"])

    def test_no_expressive_modern_content_is_imported(self):
        forbidden = {"definition", "definitions", "example", "examples", "gloss", "glosses"}

        def visit(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden.intersection(value))
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        for record in self.records:
            visit(record["modern_shape_evidence"])
            visit(record["normalization_evidence"])

    def test_receipt_hashes(self):
        self.assertEqual("PASSED", self.receipt["status"])
        for output in self.receipt["outputs"].values():
            path = MODULE.OUTPUT_DIR / output["relative_path"]
            self.assertEqual(output["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
