from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from aprompt import decode_contract_json, prepare_contract, validate_meaning
from aprompt.core import Rejected

from logic_frontend import parse_archive
from package_sister_handoff import package_handoff
from sister_adapter import ROOT, build_meaning, publish_handoff, validated_batches, verify_contract_runtime


class SisterAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = verify_contract_runtime(ROOT / "vendor" / "SISTERMACHINE_CONTRACT.md")

    def test_unicode_code_point_span_and_source_hash(self):
        text = "Do not merge 📚 records."
        meaning = build_meaning([{"id": "L7-S2", "source_text": text,
                                  "logic_candidates": [{"ast": {"op": "prohibit"}}]}])
        self.assertEqual(meaning["sources"][0]["sha256"], sha256(text.encode("utf-8")).hexdigest())
        self.assertEqual(meaning["statements"][0]["source_refs"][0]["end"], len(text))
        self.assertEqual(meaning["statements"][0]["kind"], "unresolved")
        self.assertIsNone(meaning["statements"][0]["adoption"])
        self.assertEqual(validate_meaning(meaning), meaning)

    def test_batches_respect_source_limit_and_python_ingress(self):
        entries = [{"id": f"L{i}-S1", "source_text": f"Clause {i}.", "logic_candidates": []}
                   for i in range(1, 18)]
        batches = validated_batches({"entries": entries}, self.schema)
        self.assertEqual([item[2]["entries"] for item in batches], [16, 1])
        for _, data, _ in batches:
            self.assertEqual(validate_meaning(decode_contract_json(data))["schema_version"], "1.0")

    def test_unresolved_meaning_cannot_be_prepared(self):
        meaning = build_meaning([{"id": "L1-S1", "source_text": "Do not merge records.",
                                  "logic_candidates": [{"ast": {"op": "prohibit"}}]}])
        with self.assertRaises(Rejected) as caught:
            prepare_contract(meaning, rule_ids=["StmtL1S1"], facts=[], mode="evaluate", action=None,
                             workspace_id="0" * 64, expected_axioms_sha256="0" * 64)
        self.assertEqual(caught.exception.code, "UNRESOLVED_ISSUES")

    def test_publication_is_new_directory_with_checked_manifest(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "source.zip"
            ledger_path = root / "ledger.json"
            output = root / "handoff"
            with ZipFile(archive, "w") as package:
                package.writestr("prompt.md", "Do not merge records.\n")
            ledger = parse_archive(archive, "prompt.md")
            ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
            result = publish_handoff(ledger_path, archive, ROOT / "vendor" / "SISTERMACHINE_CONTRACT.md", output)
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(result["documents"], 1)
            self.assertEqual(manifest["executable_statements"], 0)
            self.assertFalse(manifest["accepted_by_sister_machine"])
            self.assertEqual(sha256((output / "meaning_0001.json").read_bytes()).hexdigest(),
                             manifest["documents"][0]["sha256"])
            package = root / "handoff.zip"
            packaged = package_handoff(output, package)
            self.assertEqual(packaged["members"], 2)
            with ZipFile(package) as zipped:
                self.assertEqual(zipped.read("meaning_0001.json"), (output / "meaning_0001.json").read_bytes())
            with self.assertRaises(FileExistsError):
                publish_handoff(ledger_path, archive, ROOT / "vendor" / "SISTERMACHINE_CONTRACT.md", output)


if __name__ == "__main__":
    unittest.main()
