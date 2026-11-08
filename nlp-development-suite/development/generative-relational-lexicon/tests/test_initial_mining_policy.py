from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("analyze_initial_mining", ROOT / "analyze_initial_mining.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class InitialMiningPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source_map = json.loads((ROOT / "SOURCE_LANGUAGE_MAP.json").read_text(encoding="utf-8"))
        cls.policy = json.loads((ROOT / "INITIAL_MINING_LICENSE_POLICY.json").read_text(encoding="utf-8"))
        cls.pilot_decision = json.loads((ROOT / "TIER_ZERO_PILOT_DECISION.json").read_text(encoding="utf-8"))

    def test_strict_policy_exposes_holes_without_authorizing_mining(self):
        report = MODULE.analyze(copy.deepcopy(self.source_map), copy.deepcopy(self.policy))
        self.assertFalse(report["content_ingestion_authorized"])
        self.assertEqual(0, report["mining_ready_unit_count"])
        self.assertEqual(5, report["eligible_source_count"])
        self.assertGreater(report["excluded_source_count"], report["eligible_source_count"])
        self.assertIn("GRAMMAR", report["global_evidence_holes"])
        self.assertIn("PHONOLOGY", report["global_evidence_holes"])
        self.assertNotIn("OPERATION", report["global_evidence_holes"])
        self.assertNotIn("QUALITY", report["global_evidence_holes"])

    def test_roget_is_a_separate_tier_zero_electronic_edition(self):
        roget = next(unit for unit in self.policy["eligible_units"] if unit["source_id"] == "project-gutenberg-roget-22")
        self.assertEqual("PUBLIC_DOMAIN", roget["rights_class"])
        self.assertIn("electronic edition", roget["caution"])
        self.assertEqual("license_eligible_not_pinned", roget["selection_status"])

    def test_pinned_roget_decision_unlocks_test_execution_only(self):
        report = MODULE.analyze(
            copy.deepcopy(self.source_map),
            copy.deepcopy(self.policy),
            [copy.deepcopy(self.pilot_decision)],
        )
        self.assertEqual(1, report["mining_ready_unit_count"])
        self.assertTrue(report["test_mining_authorized"])
        self.assertFalse(report["production_ingestion_authorized"])
        self.assertEqual(["ebook-22-pinned-plain-text-body"], report["test_execution_ready_units"])

    def test_attribution_license_cannot_enter_tier_zero(self):
        policy = copy.deepcopy(self.policy)
        policy["eligible_units"][0]["rights_class"] = "CC-BY-4.0"
        with self.assertRaisesRegex(ValueError, "ineligible rights class"):
            MODULE.analyze(copy.deepcopy(self.source_map), policy)

    def test_component_cannot_claim_dimensions_missing_from_source(self):
        policy = copy.deepcopy(self.policy)
        tatoeba = next(unit for unit in policy["eligible_units"] if unit["source_id"] == "tatoeba-sentence-pairs")
        tatoeba["eligible_dimensions"].append("ETYMOLOGY")
        with self.assertRaisesRegex(ValueError, "exceeds source dimensions"):
            MODULE.analyze(copy.deepcopy(self.source_map), policy)

    def test_tatoeba_cc0_sentences_do_not_create_translation_equivalence(self):
        policy = copy.deepcopy(self.policy)
        tatoeba = next(unit for unit in policy["eligible_units"] if unit["source_id"] == "tatoeba-sentence-pairs")
        self.assertNotIn("TRANSLATION_EQUIVALENCE", tatoeba["eligible_dimensions"])

    def test_checked_in_reports_match_generator(self):
        report = MODULE.analyze(
            copy.deepcopy(self.source_map),
            copy.deepcopy(self.policy),
            [copy.deepcopy(self.pilot_decision)],
        )
        checked_json = json.loads((ROOT / "INITIAL_MINING_GAP_REPORT.json").read_text(encoding="utf-8"))
        checked_markdown = (ROOT / "INITIAL_MINING_GAP_REPORT.md").read_text(encoding="utf-8")
        self.assertEqual(report, checked_json)
        self.assertEqual(MODULE.render_markdown(report), checked_markdown)


if __name__ == "__main__":
    unittest.main()
