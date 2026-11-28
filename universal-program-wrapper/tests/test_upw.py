import json
import os
import sys
import tempfile
import unittest

from upw.core import UniversalProgramWrapper


class UPWTests(unittest.TestCase):
    def make_manifest(self):
        return {
            "manifest_version": "upw-manifest/0.1",
            "program": {"program_id": "test.python", "evidence_level": "tested"},
            "operations": [
                {
                    "operation_id": "T001",
                    "evidence_level": "tested",
                    "input": {
                        "allow_extra": False,
                        "fields": {"text": {"type": "string", "required": True}},
                    },
                    "side_effects": [],
                    "adapter": {
                        "type": "legacy_cli",
                        "executable": os.path.abspath(sys.executable),
                        "argv": [
                            {"literal": "-c"},
                            {"literal": "import sys; print(sys.argv[1])"},
                            {"param": "text", "required": True},
                        ],
                        "inherit_env": [],
                        "env": {},
                        "stdout": "text",
                        "timeout_ms": 5000,
                    },
                }
            ],
        }

    def test_describe(self):
        w = UniversalProgramWrapper(self.make_manifest())
        r = w.handle({"protocol": "upw/0.1", "request_id": "R1", "kind": "describe"})
        self.assertEqual(r["wrapper_outcome"], "SUCCESS")
        self.assertFalse(r["result"]["separation"]["authority_grant"])

    def test_legacy_invoke(self):
        w = UniversalProgramWrapper(self.make_manifest())
        r = w.handle({
            "protocol": "upw/0.1",
            "request_id": "R2",
            "kind": "invoke",
            "operation_id": "T001",
            "input": {"text": "hello"},
            "authority_context": {"claimed_role": "test"},
        })
        self.assertEqual(r["wrapper_outcome"], "SUCCESS")
        self.assertEqual(r["raw"]["exit_code"], 0)
        self.assertEqual(r["result"]["stdout"].strip(), "hello")

    def test_reject_extra_input(self):
        w = UniversalProgramWrapper(self.make_manifest())
        r = w.handle({
            "protocol": "upw/0.1",
            "request_id": "R3",
            "kind": "invoke",
            "operation_id": "T001",
            "input": {"text": "hello", "extra": "no"},
        })
        self.assertEqual(r["wrapper_outcome"], "WRAPPER_ERROR")

    def test_duplicate_operation_rejected(self):
        m = self.make_manifest()
        m["operations"].append(dict(m["operations"][0]))
        with self.assertRaises(Exception):
            UniversalProgramWrapper(m)


if __name__ == "__main__":
    unittest.main()
