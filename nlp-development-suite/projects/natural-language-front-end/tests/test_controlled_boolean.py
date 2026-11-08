from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aprompt import load_axioms, prepare_contract, review_contract, validate_meaning

from controlled_boolean import build_meaning, publish_meaning, validate_meaning_document
from sister_adapter import ROOT


CONTRACT = ROOT / "vendor" / "SISTERMACHINE_CONTRACT.md"


class ControlledBooleanTests(unittest.TestCase):
    def test_expression_shapes_and_atom_reuse(self):
        text = ("input is empty.\nrequest is not approved.\n"
                "If input is empty, then request is blocked.\n"
                "request is blocked and input is empty.\n"
                "request is approved or request is blocked.\n")
        meaning = build_meaning(text)
        self.assertEqual(len(meaning["atoms"]), 3)
        self.assertEqual([s["expression"]["op"] for s in meaning["statements"]],
                         ["atom", "not", "implies", "all", "any"])
        self.assertEqual(meaning["issues"], [])
        self.assertTrue(all(s["adoption"] is None and s["kind"] == "assertion" for s in meaning["statements"]))
        self.assertEqual(validate_meaning(meaning), meaning)

    def test_unsupported_sentence_blocks_preparation_and_adds_no_atom(self):
        meaning = build_meaning("If input is empty, then merge records.\n")
        self.assertEqual(meaning["atoms"], [])
        self.assertEqual(meaning["statements"][0]["kind"], "unresolved")
        self.assertEqual(len(meaning["issues"]), 1)
        validate_meaning_document(meaning, CONTRACT)

    def test_offsets_are_unicode_code_points(self):
        text = "⚑\ninput is empty.\n"
        meaning = build_meaning(text)
        self.assertEqual(meaning["statements"][1]["source_refs"][0],
                         {"source_id": "Text1", "start": 2, "end": 17})

    def test_pure_prepare_and_review_do_not_enable_execution(self):
        meaning = build_meaning("input is empty.\nIf input is empty, then request is blocked.\n")
        validated = validate_meaning_document(meaning, CONTRACT)
        self.assertGreater(len(validated), 0)
        prepared = prepare_contract(
            meaning, rule_ids=["Stmt1", "Stmt2"], facts=[], mode="evaluate", action=None,
            workspace_id=sha256(b"synthetic-test-workspace").hexdigest(),
            expected_axioms_sha256=load_axioms().generation,
        )
        review = review_contract(prepared)
        self.assertFalse(review["can_execute"])
        self.assertEqual(review["prepared_contract"]["mode"], "evaluate")
        self.assertIsNone(review["prepared_contract"]["action"])

    def test_publication_refuses_overwrite(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "source.txt"
            output = Path(directory) / "meaning.json"
            source.write_text("input is empty.\n", encoding="utf-8")
            result = publish_meaning(source, output, CONTRACT)
            self.assertEqual(result["issues"], 0)
            with self.assertRaises(FileExistsError):
                publish_meaning(source, output, CONTRACT)


if __name__ == "__main__":
    unittest.main()
