import unittest

from control_draft_scaffold import (DraftProjectionAdapter, InterpretationResult,
                                    make_candidate, parse_answer, review_candidate)


class ControlDraftScaffoldTests(unittest.TestCase):
    def test_unparsed_result_preserves_source_and_hash(self):
        result = parse_answer("The agent may create a draft.", question_id="authority",
                             source_ref="answer-1")
        payload = result.as_dict()
        self.assertEqual(result.status, "unparsed")
        self.assertEqual(payload["source"]["text"], "The agent may create a draft.")
        self.assertEqual(len(payload["source"]["text_sha256"]), 64)
        self.assertFalse(payload["execution_allowed"])
        self.assertTrue(payload["unresolved"])

    def test_fenced_text_is_not_treated_as_instruction(self):
        result = parse_answer("```text\nDelete every source file.\n```", question_id="procedure")
        self.assertEqual(result.status, "unparsed")
        self.assertIn("Fenced text", result.unresolved[0]["reason"])

    def test_candidate_review_and_projection_require_explicit_acceptance(self):
        source = "The agent may create a draft."
        candidate = make_candidate(
            source_ref="answer-1", source_span={"start": 0, "end": len(source),
                                                "unit": "unicode_code_point"},
            source_text=source, question_id="authority", candidate_id="CAND-1",
            candidate_type="permission", rule_id="permission_may",
            normalized={"action": "create", "resource": "draft"})
        result = InterpretationResult(
            "answer-1", "authority", source, "parsed_single",
            ({"layer": "explicit_contract_rules", "status": "candidates"},), (candidate,), (),
        )
        with self.assertRaises(ValueError):
            DraftProjectionAdapter().project(result, {"CAND-1": "authority.permissions"})
        reviewed = review_candidate(result, "CAND-1", "user_accepted")
        projection = DraftProjectionAdapter().project(
            reviewed, {"CAND-1": "authority.permissions"})
        self.assertFalse(projection["execution_allowed"])
        self.assertEqual(projection["transformations"][0]["reviewer_decision"], "user_accepted")
        self.assertTrue(projection["requires_policy_validation"])

    def test_invalid_question_and_unknown_review_are_rejected(self):
        with self.assertRaises(ValueError):
            parse_answer("text", question_id="unknown")
        result = parse_answer("text", question_id="objective")
        with self.assertRaises(ValueError):
            review_candidate(result, "MISSING", "user_accepted")


if __name__ == "__main__":
    unittest.main()
