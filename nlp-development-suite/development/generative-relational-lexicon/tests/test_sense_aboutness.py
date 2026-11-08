from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_sense_aboutness", ROOT / "validate_sense_aboutness.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SenseAboutnessContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = MODULE.read_json(MODULE.DECISION_PATH)
        cls.schema_validator = MODULE.build_schema_validator(MODULE.read_json(MODULE.SCHEMA_PATH))
        cls.supported = MODULE.read_json(MODULE.FIXTURE_DIR / "valid-supported.json")

    def test_baseline_is_exact_and_test_only(self):
        MODULE.validate_decision(self.decision)
        self.assertFalse(self.decision["semantic_generation_authorized"])
        self.assertFalse(self.decision["content_ingestion_authorized"])
        self.assertEqual(8, len(self.decision["baseline_inputs"]))

    def test_valid_fixtures_pass_and_invalid_fixtures_fail(self):
        valid, invalid = MODULE.validate_fixtures(self.schema_validator)
        self.assertEqual(3, len(valid))
        self.assertEqual(4, len(invalid))
        self.assertTrue(all(item["status"] == "REJECTED_AS_EXPECTED" for item in invalid))

    def test_form_level_aboutness_is_rejected(self):
        record = copy.deepcopy(self.supported)
        record["form"]["aboutness"] = "unscoped topic"
        with self.assertRaises(Exception):
            MODULE.validate_record(record, self.schema_validator)

    def test_form_match_cannot_support_aboutness(self):
        record = copy.deepcopy(self.supported)
        record["evidence"][0]["evidence_kind"] = "FORM_MATCH"
        with self.assertRaisesRegex(ValueError, "non-semantic FORM_MATCH"):
            MODULE.validate_record(record, self.schema_validator)

    def test_unknown_evidence_reference_is_rejected(self):
        record = copy.deepcopy(self.supported)
        record["sense_candidates"][0]["aboutness_assertions"][0]["evidence_refs"] = ["ev-unknown"]
        with self.assertRaisesRegex(ValueError, "unknown evidence reference"):
            MODULE.validate_record(record, self.schema_validator)

    def test_accepted_canon_truth_state_is_rejected(self):
        record = copy.deepcopy(self.supported)
        record["sense_candidates"][0]["aboutness_assertions"][0]["truth_state"] = "ACCEPTED_CANON"
        with self.assertRaises(Exception):
            MODULE.validate_record(record, self.schema_validator)

    def test_abstention_has_no_sense_candidate(self):
        record = MODULE.read_json(MODULE.FIXTURE_DIR / "valid-abstained.json")
        MODULE.validate_record(record, self.schema_validator)
        self.assertEqual([], record["sense_candidates"])
        self.assertEqual("FORM_ONLY_EVIDENCE", record["abstention"]["reason"])

    def test_sense_distinctions_must_be_reciprocal(self):
        record = MODULE.read_json(MODULE.FIXTURE_DIR / "valid-ambiguous-conflict.json")
        record["sense_candidates"][1]["distinguished_from"] = []
        with self.assertRaisesRegex(ValueError, "non-reciprocal sense distinction"):
            MODULE.validate_record(record, self.schema_validator)

    def test_assertion_conflicts_must_be_reciprocal(self):
        record = MODULE.read_json(MODULE.FIXTURE_DIR / "valid-ambiguous-conflict.json")
        record["sense_candidates"][1]["aboutness_assertions"][0]["conflicts_with"] = []
        with self.assertRaisesRegex(ValueError, "non-reciprocal assertion conflict"):
            MODULE.validate_record(record, self.schema_validator)

    def test_receipt_hashes(self):
        receipt = MODULE.read_json(MODULE.RECEIPT_PATH)
        self.assertEqual("PASSED", receipt["status"])
        self.assertEqual(receipt["output"]["sha256"], hashlib.sha256(MODULE.REPORT_PATH.read_bytes()).hexdigest())
        for name, item in receipt["inputs"]["fixtures"].items():
            self.assertEqual(item["sha256"], hashlib.sha256((MODULE.FIXTURE_DIR / name).read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
