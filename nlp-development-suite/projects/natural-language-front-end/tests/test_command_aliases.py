import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from command_aliases import DEFAULT_CATALOG, load_alias_catalog
from omni_cli import CAPABILITIES, execute_intent, parse_command


CAPABILITY_ARGS = {key: value.arguments for key, value in CAPABILITIES.items()}


class CommandAliasTests(unittest.TestCase):
    def test_explicit_aliases_and_ranked_winner(self):
        for phrase, capability in (("ls tests", "list_files"),
                                   ("cat README.md", "read_file"),
                                   ("locate files named test in tests", "find_files"),
                                   ("grep alpha in .", "search_text")):
            with self.subTest(phrase=phrase):
                self.assertEqual(parse_command(phrase).capability, capability)
        intent = parse_command("show README.md")
        self.assertEqual(intent.status, "collision")
        self.assertEqual(intent.candidates[0].rule_id, "generic_show_file")
        self.assertGreaterEqual(intent.candidates[0].score - intent.candidates[1].score, 15)
        self.assertEqual(len(intent.as_dict()["alias_rules_sha256"]), 64)
        self.assertEqual(parse_command("show file README.md").capability, "read_file")
        self.assertEqual(parse_command("show files").capability, "list_files")
        self.assertEqual(parse_command("read file").status, "unparsed")
        self.assertEqual(parse_command("find files named").status, "unparsed")

    def test_equal_meanings_abstain_and_cannot_execute(self):
        intent = parse_command("find test in tests")
        self.assertEqual(intent.status, "collision")
        self.assertIsNone(intent.capability)
        self.assertEqual([c.capability for c in intent.candidates], ["find_files", "search_text"])
        self.assertEqual([c.score for c in intent.candidates], [70, 70])
        shown = execute_intent(intent)
        self.assertEqual(shown["status"], "not_executed")
        self.assertFalse(shown["safe_display"]["operation_executed"])
        self.assertEqual(len(shown["safe_display"]["options"]), 2)
        for option in shown["safe_display"]["options"]:
            chosen = parse_command(option["explicit_command"])
            self.assertEqual(chosen.status, "parsed")
            self.assertEqual(chosen.capability, option["capability"])

    def test_path_kind_disambiguates_generic_show(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "report.v1").mkdir()
            (root / "notes").write_text("hello", encoding="utf-8")
            self.assertEqual(parse_command("show report.v1").status, "collision")
            resolved_dir = parse_command("show report.v1", root=root)
            self.assertEqual(resolved_dir.status, "collision")
            self.assertEqual(resolved_dir.candidates[0].capability, "list_files")
            self.assertIn("path_is_directory", resolved_dir.candidates[0].evidence)
            self.assertEqual(parse_command("show notes").status, "collision")
            self.assertEqual(parse_command("show notes", root=root).candidates[0].capability, "read_file")
            self.assertEqual(parse_command("show missing", root=root).status, "collision")

    def test_custom_catalog_is_data_only_and_validated(self):
        document = json.loads(DEFAULT_CATALOG.read_text(encoding="utf-8"))
        document["rules"].append({"id": "workspace_here", "phrase": "where is here", "mode": "exact",
                                  "capability": "workspace", "score": 80, "arguments": {}})
        with TemporaryDirectory() as directory:
            path = Path(directory) / "aliases.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            rules = load_alias_catalog(path, capabilities=CAPABILITY_ARGS)
            self.assertEqual(parse_command("where is here", rules=rules).capability, "workspace")
            document["rules"][-1]["capability"] = "run_shell"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_alias_catalog(path, capabilities=CAPABILITY_ARGS)
            path.write_text('{"schema_version":"omni-alias/0.1","rules":[],"rules":[]}',
                            encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
                load_alias_catalog(path, capabilities=CAPABILITY_ARGS)

    def test_custom_scores_change_resolution_without_new_handler(self):
        document = json.loads(DEFAULT_CATALOG.read_text(encoding="utf-8"))
        for rule in document["rules"]:
            if rule["id"] == "generic_find_name":
                rule["score"] = 90
        with TemporaryDirectory() as directory:
            path = Path(directory) / "aliases.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            rules = load_alias_catalog(path, capabilities=CAPABILITY_ARGS)
            intent = parse_command("find note in .", rules=rules)
            self.assertEqual(intent.status, "collision")
            self.assertIsNone(intent.capability)
            self.assertEqual(intent.candidates[0].capability, "find_files")
            self.assertEqual([c.score for c in intent.candidates], [90, 70])

    def test_collision_cli_displays_without_execution(self):
        script = Path(__file__).resolve().parents[1] / "omni_cli.py"
        result = subprocess.run([sys.executable, str(script), "find test in tests"],
                                capture_output=True, text=True, check=False)
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(payload["intent"]["status"], "collision")
        self.assertEqual(payload["execution"]["status"], "not_executed")
        self.assertEqual(len(payload["safe_display"]["options"]), 2)
        human = subprocess.run([sys.executable, str(script), "--human", "find test in tests"],
                               capture_output=True, text=True, check=False)
        self.assertEqual(human.returncode, 3)
        self.assertIn("find files named", human.stdout)
        self.assertIn("search for", human.stdout)


if __name__ == "__main__":
    unittest.main()
