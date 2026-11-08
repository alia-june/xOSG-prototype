from __future__ import annotations

import copy
import csv
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
PRODUCTION = ROOT / "production"
if str(PRODUCTION) not in sys.path:
    sys.path.insert(0, str(PRODUCTION))

import run_checks  # noqa: E402
import validate_authorization  # noqa: E402
import validate_first_slice  # noqa: E402
import validate_plan  # noqa: E402


class PlanValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = validate_plan.load_plan(PRODUCTION / "production_plan.json")

    def test_current_plan_is_valid(self) -> None:
        self.assertEqual([], validate_plan.validate_document(self.plan, ROOT))

    def test_transition_reordering_is_rejected(self) -> None:
        changed = copy.deepcopy(self.plan)
        changed["control_sequence"][6], changed["control_sequence"][7] = (
            changed["control_sequence"][7],
            changed["control_sequence"][6],
        )
        errors = validate_plan.validate_document(changed, ROOT)
        self.assertTrue(any("transition order" in error for error in errors))

    def test_missing_immediate_dependency_is_rejected(self) -> None:
        changed = copy.deepcopy(self.plan)
        changed["phases"][5]["depends_on"] = ["P03"]
        errors = validate_plan.validate_document(changed, ROOT)
        self.assertTrue(any("must depend on P04" in error for error in errors))

    def test_future_dependency_is_rejected(self) -> None:
        changed = copy.deepcopy(self.plan)
        changed["phases"][4]["depends_on"].append("P09")
        errors = validate_plan.validate_document(changed, ROOT)
        self.assertTrue(any("not an earlier phase" in error for error in errors))

    def test_production_ready_claim_is_rejected(self) -> None:
        changed = copy.deepcopy(self.plan)
        changed["production_ready"] = True
        errors = validate_plan.validate_document(changed, ROOT)
        self.assertTrue(any("production_ready" in error for error in errors))

    def test_verified_phase_requires_evidence(self) -> None:
        changed = copy.deepcopy(self.plan)
        changed["phases"][0]["evidence"] = []
        errors = validate_plan.validate_document(changed, ROOT)
        self.assertTrue(any("verified without evidence" in error for error in errors))

    def test_required_control_files_are_safe_and_present(self) -> None:
        for value in self.plan["required_control_files"]:
            self.assertTrue(validate_plan._is_safe_relative_path(value))
            self.assertTrue(ROOT.joinpath(*Path(value).parts).is_file(), value)


class EvidenceAndRunnerTests(unittest.TestCase):
    def test_baseline_retains_non_production_boundary(self) -> None:
        baseline = json.loads(
            (PRODUCTION / "BASELINE_EVIDENCE.json").read_text(encoding="utf-8")
        )
        self.assertFalse(baseline["production_ready"])
        self.assertEqual("NONE", baseline["authority_effect"])
        self.assertEqual(1306, baseline["historical_manifest"]["listed_members"])
        self.assertEqual(0, baseline["historical_manifest"]["size_or_hash_failures"])

    def test_source_inventory_has_protocol_fields(self) -> None:
        with (PRODUCTION / "SOURCE_INVENTORY.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(
                [
                    "identifier",
                    "location",
                    "type",
                    "version_status",
                    "authority",
                    "accessibility",
                    "integrity",
                    "relevance",
                ],
                reader.fieldnames,
            )
            rows = list(reader)
        self.assertGreaterEqual(len(rows), 10)

    def test_baseline_check_order_starts_with_integrity_and_controls(self) -> None:
        check_ids = [check.check_id for check in run_checks.checks_for_suite("baseline")]
        self.assertEqual(
            [
                "snapshot-manifest",
                "plan-order",
                "authorization-proposal",
                "first-slice-smoke",
                "successor-manifest",
                "p04-pre-stage",
                "p05-slice",
                "p06-evidence",
                "p07-validation",
                "p08-candidate",
                "test-environment",
                "successor-core-tests",
                "successor-integration-tests",
                "successor-fuzzy-tests",
                "successor-torture-tests",
                "production-control-tests",
                "lexicon-core-tests",
                "natural-language-tests",
                "lexicon-atlas-validate",
                "file-atlas-verify",
            ],
            check_ids,
        )

    def test_control_suite_is_non_deploying_subset(self) -> None:
        control_ids = [check.check_id for check in run_checks.checks_for_suite("control")]
        self.assertEqual(
            [
                "plan-order",
                "authorization-proposal",
                "first-slice-smoke",
                "successor-manifest",
                "p04-pre-stage",
                "p05-slice",
                "p06-evidence",
                "p07-validation",
                "p08-candidate",
                "test-environment",
                "successor-core-tests",
                "successor-integration-tests",
                "successor-fuzzy-tests",
                "successor-torture-tests",
                "production-control-tests",
            ],
            control_ids,
        )
        self.assertFalse(any("deploy" in check_id for check_id in control_ids))

    def test_hardening_suite_is_explicit_and_ordered(self) -> None:
        hardening_ids = [
            check.check_id for check in run_checks.checks_for_suite("hardening")
        ]
        self.assertEqual(
            [
                "p07-validation",
                "p08-candidate",
                "test-environment",
                "successor-core-tests",
                "successor-integration-tests",
                "successor-fuzzy-tests",
                "successor-torture-tests",
                "production-control-tests",
            ],
            hardening_ids,
        )


class BoundedAuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = validate_authorization.load_json(
            PRODUCTION / "p03_authorization.json"
        )
        cls.plan = validate_authorization.load_json(PRODUCTION / "production_plan.json")

    def test_current_bounded_authorization_is_valid(self) -> None:
        self.assertEqual(
            [],
            validate_authorization.validate_authorization(
                self.packet, self.plan, ROOT
            ),
        )
        self.assertEqual("accepted-bounded-local-release", self.packet["status"])
        self.assertFalse(self.packet["production_ready"])
        self.assertEqual("NONE", self.packet["deployment_authority"])

    def test_production_accepted_state_without_authority_is_rejected(self) -> None:
        changed = copy.deepcopy(self.packet)
        changed["decisions"][0]["state"] = "accepted"
        errors = validate_authorization.validate_authorization(changed, self.plan, ROOT)
        self.assertTrue(any("accepted or invalid" in error for error in errors))

    def test_only_q002_has_bounded_development_acceptance(self) -> None:
        accepted = [
            decision["id"]
            for decision in self.packet["decisions"]
            if decision["state"] == "accepted_for_development"
        ]
        self.assertEqual(["Q-002"], accepted)
        self.assertEqual("user", self.packet["development_authorization"]["authority"])

    def test_execution_authority_is_rejected(self) -> None:
        changed = copy.deepcopy(self.packet)
        changed["first_release"]["execution_allowed"] = True
        errors = validate_authorization.validate_authorization(changed, self.plan, ROOT)
        self.assertTrue(any("execution_allowed must be false" in error for error in errors))

    def test_advancing_later_phase_before_dependency_is_rejected(self) -> None:
        changed_plan = copy.deepcopy(self.plan)
        changed_plan["phases"][9]["state"] = "in_progress"
        errors = validate_authorization.validate_authorization(
            self.packet, changed_plan, ROOT
        )
        self.assertTrue(any("P09 must remain not_started" in error for error in errors))

    def test_deployment_remains_blocked_without_new_authority(self) -> None:
        changed_plan = copy.deepcopy(self.plan)
        changed_plan["phases"][10]["state"] = "not_started"
        errors = validate_authorization.validate_authorization(
            self.packet, changed_plan, ROOT
        )
        self.assertTrue(any("P10 must remain blocked" in error for error in errors))

    def test_first_slice_smoke_executes_nothing_and_exposes_gap(self) -> None:
        report, errors = validate_first_slice.evaluate()
        self.assertEqual([], errors)
        self.assertFalse(report["operation_executed"])
        self.assertEqual("NONE", report["authority_effect"])
        self.assertFalse(report["integration"]["present"])
        self.assertTrue(report["integration"]["successor_adapter_present"])


if __name__ == "__main__":
    unittest.main()
