from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from omni_cli import execute_intent, parse_command, safe_display
from semantic_layers import SessionHistory
from wordnet_lexicon import WordNetLexicon


class SemanticLayersTests(unittest.TestCase):
    def test_wordnet_secondary_suggests_without_executing(self):
        try:
            WordNetLexicon()
        except RuntimeError as exc:
            self.skipTest(str(exc))
        intent = parse_command("seek for alpha in tests")
        self.assertEqual(intent.status, "wordnet_suggestions")
        self.assertIsNone(intent.capability)
        self.assertEqual(intent.candidates[0].capability, "search_text")
        self.assertTrue(any(item.startswith("shared_synset:oewn-")
                            for item in intent.candidates[0].evidence))
        self.assertEqual(execute_intent(intent)["status"], "not_executed")
        choice = safe_display(intent)["options"][0]["explicit_command"]
        self.assertEqual(parse_command(choice).capability, "search_text")

    def test_primary_alias_precedes_wordnet(self):
        with TemporaryDirectory() as directory:
            intent = parse_command("list files", wordnet_dir=Path(directory) / "missing")
        self.assertEqual(intent.status, "parsed")
        self.assertEqual(intent.layer_trace, ({"layer": "aliases", "status": "parsed"},))

    def test_history_ranks_collision_but_does_not_select(self):
        history = SessionHistory()
        history.record_choice("find test in tests", "search_text", {"term": "test", "path": "tests"})
        intent = parse_command("find test in tests", history=history)
        self.assertEqual(intent.status, "collision")
        self.assertEqual(intent.candidates[0].capability, "search_text")
        self.assertIn("session_history_choice", intent.candidates[0].evidence)
        self.assertEqual(len(safe_display(intent)["options"]), 2)

    def test_history_precedes_web_and_llm_after_wordnet(self):
        history = SessionHistory()
        history.record_choice("blorp alpha", "search_text", {"term": "alpha", "path": "."})
        calls = []

        def web(_):
            calls.append("web")
            return []

        def llm(_):
            calls.append("llm")
            return []

        intent = parse_command("blorp alpha", history=history, web_provider=web, llm_provider=llm)
        self.assertEqual(intent.status, "history_suggestions")
        self.assertEqual(calls, [])
        self.assertEqual([part["layer"] for part in intent.layer_trace],
                         ["aliases", "wordnet", "history"])

    def test_web_precedes_optional_llm(self):
        calls = []

        def web(_):
            calls.append("web")
            return [{"capability": "search_text", "arguments": {"term": "alpha", "path": "."},
                     "source": "https://example.org/reference"}]

        def llm(_):
            calls.append("llm")
            return [{"capability": "list_files", "arguments": {"path": "."},
                     "source": "fake-model"}]

        intent = parse_command("blorp alpha", web_provider=web, llm_provider=llm)
        self.assertEqual(intent.status, "web_suggestions")
        self.assertEqual(calls, ["web"])
        self.assertEqual(execute_intent(intent)["status"], "not_executed")
        self.assertEqual([part["layer"] for part in intent.layer_trace],
                         ["aliases", "wordnet", "history", "web"])

    def test_llm_is_last_and_proposals_are_not_executed(self):
        calls = []

        def web(_):
            calls.append("web")
            return []

        def llm(_):
            calls.append("llm")
            return [{"capability": "list_files", "arguments": {"path": "."},
                     "source": "fake-model"}]

        intent = parse_command("blorp alpha", web_provider=web, llm_provider=llm)
        self.assertEqual(intent.status, "llm_suggestions")
        self.assertEqual(calls, ["web", "llm"])
        self.assertEqual(execute_intent(intent)["status"], "not_executed")

    def test_invalid_provider_output_is_rejected(self):
        def bad_web(_):
            return [{"capability": "run_shell", "arguments": {}, "source": "https://example.org"}]

        intent = parse_command("blorp alpha", web_provider=bad_web)
        self.assertEqual(intent.status, "unparsed")
        self.assertIn({"layer": "web", "status": "invalid_or_failed"}, intent.layer_trace)


if __name__ == "__main__":
    unittest.main()
