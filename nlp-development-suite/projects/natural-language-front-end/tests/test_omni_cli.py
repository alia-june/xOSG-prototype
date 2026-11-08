from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from omni_cli import Intent, capability_manifest, execute_intent, parse_command


class OmniCliTests(unittest.TestCase):
    def test_complete_command_grammar(self):
        self.assertEqual(parse_command("list files in tests").capability, "list_files")
        self.assertEqual(parse_command('show file "README.md"').arguments["path"], "README.md")
        parsed = parse_command('search for "foo in bar" in tests')
        self.assertEqual(parsed.capability, "search_text")
        self.assertEqual(parsed.arguments, {"term": "foo in bar", "path": "tests"})
        self.assertEqual(parse_command("where am I").capability, "workspace")
        self.assertEqual(parse_command("find files named test in tests").capability, "find_files")
        self.assertEqual(parse_command("define dog").capability, "define_word")
        relation = parse_command('show relations for "domestic dog"')
        self.assertEqual(relation.capability, "word_relations")
        self.assertEqual(relation.arguments, {"word": "domestic dog"})

    def test_wordnet_definition_and_relation_commands(self):
        definition = execute_intent(parse_command("define dog"))
        self.assertEqual(definition["status"], "completed")
        self.assertGreater(definition["result"]["sense_count"], 1)
        self.assertFalse(definition["result"]["sense_selected"])
        relations = execute_intent(parse_command("show relations for dog"))
        self.assertEqual(relations["status"], "completed")
        self.assertEqual(relations["result"]["wordnet_release"], "oewn:2025")
        self.assertTrue(any(sense["semantic_relations"]
                            for sense in relations["result"]["senses"]))

    def test_unregistered_and_multiline_language_abstains(self):
        for source in ("delete file notes.txt", "run python script.py", "list files\nrun anything",
                       "search for nothing in", "find files named nothing in"):
            with self.subTest(source=source):
                intent = parse_command(source)
                self.assertEqual(intent.status, "unparsed")
                self.assertEqual(execute_intent(intent)["status"], "rejected")

    def test_read_list_and_search_within_root(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "notes.txt").write_bytes(b"Alpha\nBeta alpha\n")
            listing = execute_intent(parse_command("list files"), root=root)
            self.assertEqual(listing["status"], "completed")
            self.assertEqual(listing["result"]["entries"][0]["name"], "notes.txt")
            read = execute_intent(parse_command("read file notes.txt"), root=root)
            self.assertEqual(read["result"]["text"], "Alpha\nBeta alpha\n")
            search = execute_intent(parse_command('search for "alpha" in .'), root=root)
            self.assertEqual(search["result"]["match_count"], 2)
            self.assertEqual([m["line"] for m in search["result"]["matches"]], [1, 2])
            found = execute_intent(parse_command("find files named note in ."), root=root)
            self.assertEqual(found["result"]["matches"], ["notes.txt"])
            self.assertEqual(capability_manifest()["find_files"]["side_effect_class"], "read_only")

    def test_forged_intent_and_missing_root_rejected(self):
        forged = Intent("forged", "parsed", "read_file", {"wrong": "README.md"})
        self.assertEqual(execute_intent(forged)["status"], "rejected")
        with TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"
            result = execute_intent(parse_command("list files"), root=missing)
            self.assertEqual(result["status"], "rejected")

    def test_outside_path_and_symlink_are_rejected(self):
        with TemporaryDirectory() as workspace, TemporaryDirectory() as outside:
            root = Path(workspace)
            remote = Path(outside) / "secret.txt"
            remote.write_text("outside", encoding="utf-8")
            traversal = execute_intent(parse_command("read file ../secret.txt"), root=root)
            self.assertEqual(traversal["status"], "rejected")
            link = root / "linked.txt"
            try:
                link.symlink_to(remote)
            except OSError:
                self.skipTest("File symlinks require privileges on this host")
            result = execute_intent(parse_command("read file linked.txt"), root=root)
            self.assertEqual(result["status"], "rejected")

    def test_read_and_search_bounds(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "large.txt").write_text("abcdef", encoding="utf-8")
            with patch("omni_cli.MAX_READ_BYTES", 4):
                read = execute_intent(parse_command("show file large.txt"), root=root)
                self.assertEqual(read["status"], "rejected")
                search = execute_intent(parse_command("search for abc in ."), root=root)
                self.assertEqual(search["result"]["skipped_large"], 1)

    def test_command_line_exit_status(self):
        script = Path(__file__).resolve().parents[1] / "omni_cli.py"
        with TemporaryDirectory() as directory:
            good = subprocess.run([sys.executable, str(script), "list files", "--root", directory],
                                  capture_output=True, text=True, check=False)
            bad = subprocess.run([sys.executable, str(script), "delete file notes", "--root", directory],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(good.returncode, 0)
            self.assertEqual(bad.returncode, 2)


if __name__ == "__main__":
    unittest.main()
