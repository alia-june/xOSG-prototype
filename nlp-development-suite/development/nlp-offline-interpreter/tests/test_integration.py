from __future__ import annotations

import json
from itertools import repeat
from io import StringIO
from pathlib import Path
import sys
import unittest
from contextlib import redirect_stdout


SUITE_ROOT = Path(__file__).resolve().parents[3]
PROJECTS = SUITE_ROOT / "projects"
PACKAGE_SRC = Path(__file__).resolve().parents[1] / "src"
CORE_SRC = PROJECTS / "lexicon-core" / "src"
FRONTEND = PROJECTS / "natural-language-front-end"
for path in (PACKAGE_SRC, CORE_SRC, FRONTEND):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from nlp_offline_interpreter.core import canonical_json  # noqa: E402
from nlp_offline_interpreter.basic import BASIC_MAX_TOKENS, analyze_text  # noqa: E402
from nlp_offline_interpreter.integration import (  # noqa: E402
    MAX_TASK_MODULES,
    PUBLIC_API_VERSION,
    build_interpreter,
    integration_status,
    main,
    interpret_text,
)


class OfflineInterpreterTests(unittest.TestCase):
    def test_explicit_alias_uses_primary_layer_and_executes_nothing(self):
        result = interpret_text("find files named report in .", use_wordnet=False)
        data = result.to_dict()
        self.assertEqual("parsed_single", result.status)
        self.assertEqual("find_files", result.candidates[0].operation)
        self.assertEqual({"name": "report", "path": "."}, dict(result.candidates[0].arguments))
        self.assertEqual("not_consulted", result.layer_trace[1].status)
        self.assertFalse(data["execution_allowed"])
        self.assertEqual("NONE", data["authority_effect"])

    def test_generic_task_fallback_is_not_file_specific(self):
        result = interpret_text("I feel uncertain", use_wordnet=False)
        self.assertEqual("parsed_single", result.status)
        self.assertEqual("eliza-nxt.respond", result.candidates[0].operation)
        self.assertEqual("no_match", result.layer_trace[0].status)
        self.assertEqual("candidates", result.layer_trace[1].status)

    def test_collect_all_preserves_independent_operation_namespaces(self):
        result = interpret_text(
            "find files named report in .",
            use_wordnet=False,
            mode="collect_all",
        )
        self.assertEqual("collision", result.status)
        operations = [candidate.operation for candidate in result.candidates]
        self.assertIn("find_files", operations)
        self.assertIn("file-explorer.search", operations)

    def test_unsupported_input_abstains(self):
        result = interpret_text("flibbertigibbet", use_wordnet=False)
        self.assertEqual("unparsed", result.status)
        self.assertEqual([], list(result.candidates))
        self.assertTrue(result.unresolved)

    def test_public_output_is_deterministic_and_generic(self):
        first = interpret_text("define otter", use_wordnet=False)
        second = interpret_text("define otter", use_wordnet=False)
        self.assertEqual(canonical_json(first), canonical_json(second))
        parsed = json.loads(canonical_json(first))
        self.assertEqual("generic-interpretation/1", parsed["schema"])
        self.assertFalse(parsed["execution_allowed"])
        self.assertEqual(PUBLIC_API_VERSION, parsed["metadata"]["public_api_version"])
        self.assertEqual(PUBLIC_API_VERSION, "nlp-offline-interpreter/0.1")

    def test_input_bound_returns_typed_invalid_state(self):
        result = interpret_text("x" * 1025, use_wordnet=False)
        self.assertEqual("invalid_input", result.status)
        self.assertFalse(result.to_dict()["execution_allowed"])

    def test_invalid_configuration_fails_closed(self):
        with self.assertRaisesRegex(TypeError, "use_wordnet"):
            build_interpreter(use_wordnet=1)  # type: ignore[arg-type]
        with self.assertRaisesRegex(TypeError, "wordnet_dir"):
            build_interpreter(wordnet_dir=object())  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "module count"):
            build_interpreter(modules=repeat(None, MAX_TASK_MODULES + 1))  # type: ignore[arg-type]

    def test_optional_integration_status_is_non_executing(self):
        status = integration_status()
        self.assertTrue(status["available"])
        self.assertEqual([], status["missing_modules"])
        self.assertFalse(status["execution_allowed"])
        self.assertEqual("NONE", status["authority_effect"])

    def test_cli_status_is_machine_readable(self):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(["--check-integration"])
        self.assertEqual(0, exit_code)
        status = json.loads(output.getvalue())
        self.assertTrue(status["available"])
        self.assertFalse(status["execution_allowed"])

    def test_dependency_free_basic_analysis_is_structural_only(self):
        result = analyze_text("Hello, generic world!")
        payload = result.to_dict()
        self.assertEqual("parsed_single", result.status)
        self.assertEqual("text.analyze", result.candidates[0].operation)
        self.assertEqual(
            ["Hello", ",", "generic", "world", "!"],
            [item["text"] for item in result.candidates[0].arguments["tokens"]],
        )
        self.assertEqual("basic", payload["metadata"]["mode"])
        self.assertFalse(payload["execution_allowed"])

    def test_basic_analysis_reports_token_truncation(self):
        result = analyze_text(" ".join("token" for _ in range(BASIC_MAX_TOKENS + 10)))
        self.assertEqual("partial", result.status)
        self.assertEqual(BASIC_MAX_TOKENS, result.candidates[0].arguments["token_count"])
        self.assertTrue(result.candidates[0].arguments["truncated"])
        self.assertTrue(result.unresolved)

    def test_cli_basic_mode_needs_no_optional_adapter_decision(self):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(["--basic", "Hello", "world"])
        self.assertEqual(0, exit_code)
        payload = json.loads(output.getvalue())
        self.assertEqual("text.analyze", payload["candidates"][0]["operation"])
        self.assertFalse(payload["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
