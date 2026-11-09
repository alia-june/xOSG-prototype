import json
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import warnings
from zipfile import ZipFile

from jsonschema import Draft202012Validator

from logic_frontend import parse_archive, parse_clause, parse_markdown, publish_result, split_sentences
from source_archive import load_archive_member


ROOT = Path(__file__).resolve().parents[1]


class LogicFrontendTests(unittest.TestCase):
    def test_simple_prohibition_is_partial_candidate(self):
        result = parse_clause("Do not merge these diagnoses.")
        self.assertEqual(result["interpretation_status"], "candidate_partial")
        self.assertEqual(result["logic_candidates"][0]["ast"]["op"], "prohibit")
        self.assertEqual(result["logic_candidates"][0]["ast"]["action_text"], "merge")

    def test_if_clause_keeps_condition_and_prohibition(self):
        result = parse_clause("If input is empty, do not proceed.")
        ast = result["logic_candidates"][0]["ast"]
        self.assertEqual(ast["op"], "implies")
        self.assertEqual(ast["condition"]["property_text"], "empty")
        self.assertEqual(ast["consequence"]["op"], "prohibit")

    def test_unsupported_scope_and_multiple_sentences_abstain(self):
        for text in ("Do not merge A and B.", "Stop the branch if evidence is missing.",
                     "Do not merge. Continue later.",
                     "Capability is not authority."):
            with self.subTest(text=text):
                self.assertEqual(parse_clause(text)["interpretation_status"], "unparsed")

    def test_positive_imperative_and_sentence_split(self):
        self.assertEqual(parse_clause("Preserve the parent.")["logic_candidates"][0]["ast"]["op"], "obligate")
        self.assertEqual(split_sentences("1. Preserve the parent. Do not delete records."),
                         ["1. Preserve the parent.", "Do not delete records."])
        entries = parse_markdown("1. Preserve the parent. Do not delete records.\n")
        self.assertEqual([entry["id"] for entry in entries], ["L1-S1", "L1-S2"])
        self.assertTrue(all(entry["interpretation_status"] == "candidate_partial" for entry in entries))

    def test_markdown_preserves_source_and_ignores_fenced_code(self):
        text = "# Rules\nDo not merge these diagnoses.\n```text\nDo not delete records.\n```\n"
        entries = parse_markdown(text)
        self.assertEqual([entry["source_span"]["start_line"] for entry in entries], [1, 2, 3, 4, 5])
        self.assertEqual(entries[1]["source_text"], "Do not merge these diagnoses.")
        self.assertEqual(entries[3]["interpretation_status"], "unparsed")
        self.assertTrue(all(entry["adoption_status"] == "unadopted" for entry in entries))

    def test_archive_handoff_matches_schema_and_source_hashes(self):
        with TemporaryDirectory() as directory:
            archive = Path(directory) / "fixture.zip"
            with ZipFile(archive, "w") as package:
                package.writestr("prompt.md", "Do not merge these diagnoses.\n")
            result = parse_archive(archive, "prompt.md")
            schema = json.loads((ROOT / "handoff_stub.schema.json").read_text(encoding="utf-8"))
            Draft202012Validator(schema).validate(result)
            self.assertFalse(result["execution_allowed"])
            self.assertEqual(len(result["entries"]), 1)

    def test_archive_rejects_traversal_member(self):
        with TemporaryDirectory() as directory:
            archive = Path(directory) / "bad.zip"
            with ZipFile(archive, "w") as package:
                package.writestr("../prompt.md", "Do not merge records.\n")
            with self.assertRaisesRegex(ValueError, "Unsafe ZIP member"):
                load_archive_member(archive, "prompt.md")

    def test_archive_rejects_duplicate_and_oversize_member(self):
        with TemporaryDirectory() as directory:
            archive = Path(directory) / "duplicate.zip"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with ZipFile(archive, "w") as package:
                    package.writestr("prompt.md", "one")
                    package.writestr("prompt.md", "two")
            with self.assertRaisesRegex(ValueError, "Duplicate ZIP member"):
                load_archive_member(archive, "prompt.md")

            archive = Path(directory) / "oversize.zip"
            with ZipFile(archive, "w") as package:
                package.writestr("prompt.md", "a little too long")
            with patch("source_archive.MAX_MEMBER_BYTES", 4):
                with self.assertRaisesRegex(ValueError, "exceeds"):
                    load_archive_member(archive, "prompt.md")

    def test_archive_rejects_case_insensitive_collision(self):
        with TemporaryDirectory() as directory:
            archive = Path(directory) / "collision.zip"
            with ZipFile(archive, "w") as package:
                package.writestr("prompt.md", "one")
                package.writestr("PROMPT.md", "two")
            with self.assertRaisesRegex(ValueError, "Case-insensitive"):
                load_archive_member(archive, "prompt.md")

    def test_publishing_preserves_prior_generation_and_receipt(self):
        with TemporaryDirectory() as directory:
            archive = Path(directory) / "fixture.zip"
            output = Path(directory) / "result.json"
            with ZipFile(archive, "w") as package:
                package.writestr("prompt.md", "Do not merge records.\n")
            result = parse_archive(archive, "prompt.md")
            first = publish_result(result, archive, output)
            self.assertTrue(Path(first["receipt"]).is_file())
            prior = output.read_bytes()
            changed = deepcopy(result)
            changed["entries"][0]["unresolved"].append("Additional review needed.")
            with self.assertRaises(FileExistsError):
                publish_result(changed, archive, output)
            second = publish_result(changed, archive, output, replace=True)
            self.assertEqual(Path(second["previous_output"]).read_bytes(), prior)
            self.assertNotEqual(output.read_bytes(), prior)


if __name__ == "__main__":
    unittest.main()
