from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("run_tier_zero_pilot", ROOT / "run_tier_zero_pilot.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
QUERY_SPEC = importlib.util.spec_from_file_location("query_word_history", ROOT / "query_word_history.py")
assert QUERY_SPEC and QUERY_SPEC.loader
QUERY_MODULE = importlib.util.module_from_spec(QUERY_SPEC)
QUERY_SPEC.loader.exec_module(QUERY_MODULE)


class TierZeroPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads((ROOT / "TIER_ZERO_PILOT_DECISION.json").read_text(encoding="utf-8"))
        cls.artifact_path = MODULE.validate_decision(copy.deepcopy(cls.decision))
        cls.data, cls.digest = MODULE.verify_artifact(cls.artifact_path, cls.decision)
        cls.records, cls.memberships = MODULE.parse_roget(cls.data.decode("utf-8-sig"), cls.digest)

    def test_decision_is_test_only(self):
        self.assertEqual("TEST_EXECUTION_ONLY", self.decision["authority_effect"])
        self.assertFalse(self.decision["production_ready"])
        self.assertFalse(self.decision["publication_allowed"])
        self.assertFalse(self.decision["canon_admission"])

    def test_pinned_artifact_and_structural_parse(self):
        self.assertEqual(self.decision["artifact"]["sha256"], self.digest)
        self.assertEqual(1043, len(self.records))
        self.assertGreater(len(self.memberships), 10000)
        self.assertEqual(1, self.records[0]["head_number"])
        self.assertEqual("1", self.records[0]["head_id"])
        self.assertEqual("Existence", self.records[0]["heading"])
        first_terms = {item["term"] for item in self.memberships if item["head_number"] == 1}
        self.assertIn("subsistence", first_terms)
        self.assertIn("reality", first_terms)
        self.assertNotIn("subsistence. reality", first_terms)
        self.assertFalse(any("&c" in term for term in first_terms))

    def test_suffixed_heads_are_structural_boundaries(self):
        head_ids = [record["head_id"] for record in self.records]
        self.assertEqual(len(head_ids), len(set(head_ids)))
        self.assertIn("847a", head_ids)
        self.assertIn("465b", head_ids)
        self.assertFalse(any(item["normalized_term"] == "#847a" for item in self.memberships))
        jewelry = [item for item in self.memberships if item["head_id"] == "847a"]
        self.assertTrue(jewelry)
        self.assertTrue(all(item["head_number"] == 847 for item in jewelry))

    def test_repeated_boundary_defects_are_removed_before_segmentation(self):
        terms = {item["normalized_term"] for item in self.memberships}
        forbidden = {
            "logy [u",
            "2] esprit de corps",
            "158} production",
            "iii) musical sounds",
            "inattentive 458",
            "#847a",
        }
        self.assertFalse(forbidden & terms)
        self.assertIn("logy", terms)
        self.assertIn("inattentive", terms)
        logy = [item for item in self.memberships if item["normalized_term"] == "logy"]
        self.assertTrue(any("[U.S.]" in item["source_bracket_labels"] for item in logy))

    def test_modern_queries_are_historical_candidates_only(self):
        report = MODULE.build_modern_queries(self.memberships)
        queries = {item["modern_word"]: item for item in report["queries"]}
        self.assertEqual("PROPOSAL_ONLY", report["acceptance_state"])
        self.assertGreater(queries["precision"]["candidate_count"], 0)
        self.assertEqual("NO_EXACT_HISTORICAL_CANDIDATE", queries["mapping"]["status"])

    def test_mutated_artifact_fails_hash_check(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.txt"
            path.write_bytes(self.data + b"mutation")
            with self.assertRaisesRegex(ValueError, "byte count"):
                MODULE.verify_artifact(path, self.decision)

    def test_same_length_mutation_fails_hash_check(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.txt"
            mutated = bytearray(self.data)
            mutated[-1] = (mutated[-1] + 1) % 256
            path.write_bytes(mutated)
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                MODULE.verify_artifact(path, self.decision)

    def test_membership_quality_invariants(self):
        for membership in self.memberships:
            term = membership["term"]
            self.assertEqual(term.casefold(), membership["normalized_term"])
            self.assertLessEqual(len(term.split()), 6)
            self.assertNotIn("\n", term)
            self.assertNotIn("&c", term)
            self.assertIn("head_id", membership)
            self.assertLessEqual(membership["source_line_start"], membership["source_line_end"])

    def test_arbitrary_modern_word_query(self):
        report = QUERY_MODULE.query_memberships(["precision", "mapping"])
        results = {item["modern_word"]: item for item in report["results"]}
        self.assertEqual("PROPOSAL_ONLY", report["acceptance_state"])
        self.assertGreater(results["precision"]["candidate_count"], 0)
        self.assertEqual(0, results["mapping"]["candidate_count"])

    def test_checked_receipt_hashes_exist(self):
        receipt = json.loads(MODULE.RECEIPT_PATH.read_text(encoding="utf-8"))
        self.assertEqual("PASSED", receipt["status"])
        for output in receipt["output"].values():
            path = MODULE.OUTPUT_DIR / output["relative_path"]
            self.assertTrue(path.is_file())
            self.assertEqual(output["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
