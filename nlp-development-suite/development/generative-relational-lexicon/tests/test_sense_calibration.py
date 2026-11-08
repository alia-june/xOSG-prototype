from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import unittest


ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_sense_calibration", ROOT / "build_sense_calibration.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SenseCalibrationTests(unittest.TestCase):
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

    def test_calibration_is_blank_and_dual_copy(self):
        self.assertEqual(34, len(self.records))
        self.assertEqual(2, self.report["reviewer_copy_count"])
        for record in self.records:
            for reviewer in (record["reviewer_a"], record["reviewer_b"]):
                self.assertEqual(set(MODULE.NULL_REVIEW_FIELDS), set(reviewer))
                self.assertTrue(all(value is None for value in reviewer.values()))
            self.assertTrue(all(value is None for value in record["adjudication"].values()))

    def test_all_coverage_atoms_are_present(self):
        atoms = {
            (dimension, record["selection"]["stratum"][dimension])
            for record in self.records
            for dimension in MODULE.DIMENSIONS
        }
        self.assertEqual(57, len(atoms))
        self.assertEqual(0, self.report["uncovered_atom_count"])

    def test_selection_is_reproducible_and_unique(self):
        ids = [record["calibration_id"] for record in self.records]
        self.assertEqual(len(ids), len(set(ids)))
        ranks = [record["selection"]["selection_rank"] for record in self.records]
        self.assertEqual(len(ranks), len(set(ranks)))

    def test_authority_boundary(self):
        self.assertFalse(self.decision["review_judgment_assignment_allowed"])
        self.assertFalse(self.report["canon_admission"])
        self.assertEqual("TEST_BLANK_DUAL_REVIEW_CALIBRATION_ONLY", self.receipt["authority_effect"])

    def test_receipt_hashes(self):
        self.assertEqual("PASSED", self.receipt["status"])
        for output in self.receipt["outputs"].values():
            path = MODULE.OUTPUT_DIR / output["relative_path"]
            self.assertEqual(output["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
