from __future__ import annotations

import gzip
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_sense_calibration_review", ROOT / "validate_sense_calibration_review.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SenseCalibrationReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with gzip.open(MODULE.RECORDS_PATH, "rt", encoding="utf-8") as stream:
            cls.records = [json.loads(line) for line in stream]

    def test_blank_package_is_source_bound_and_not_reviewed(self):
        result = MODULE.validate_records(self.records)
        self.assertEqual("BLANK_NOT_REVIEWED", result["status"])
        self.assertEqual(0, result["completed_review_copy_count"])

    def test_require_reviewed_rejects_blank_package(self):
        with self.assertRaisesRegex(ValueError, "review is required"):
            MODULE.validate_records(self.records, require_reviewed=True)

    def test_source_evidence_mutation_is_rejected(self):
        mutated = json.loads(json.dumps(self.records))
        mutated[0]["normalized_term"] = "changed"
        with self.assertRaisesRegex(ValueError, "source evidence changed"):
            MODULE.validate_records(mutated)

    def test_malformed_status_is_rejected(self):
        mutated = json.loads(json.dumps(self.records))
        mutated[0]["reviewer_a"] = {
            "reviewer_id": "reviewer-a",
            "reviewed_at": "2026-10-06T00:00:00Z",
            "review_status": "MADE_UP",
            "sense_candidates": [],
            "aboutness_assertions": [],
            "abstention": {"reason": "SOURCE_BOUNDARY"},
            "review_notes": "note",
        }
        with self.assertRaisesRegex(ValueError, "unsupported review status"):
            MODULE.validate_records(mutated)

    def test_authority_remains_test_only(self):
        result = MODULE.validate_records(self.records)
        self.assertFalse(result["production_ready"])
        self.assertFalse(result["publication_allowed"])
        self.assertFalse(result["canon_admission"])


if __name__ == "__main__":
    unittest.main()
