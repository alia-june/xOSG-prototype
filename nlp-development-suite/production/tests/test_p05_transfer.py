from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "production" / "validate_p05_slice.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_p05_slice", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class P05TransferTests(unittest.TestCase):
    def test_current_slice_passes(self):
        report, errors = validator.evaluate()
        self.assertEqual([], errors)
        self.assertEqual("passed", report["status"])
        self.assertEqual(8, report["requirements"])
        self.assertEqual("NONE", report["authority_effect"])
        self.assertFalse(report["execution_allowed"])
        self.assertFalse(report["production_ready"])

    def test_requirement_set_is_exact(self):
        trace = validator.load_json(validator.TRACE)
        ids = [item["id"] for item in trace["requirements"]]
        self.assertEqual(validator.EXPECTED_REQUIREMENTS, ids)

    def test_source_imports_exclude_network_clients(self):
        for path in sorted((validator.SRC / "nlp_offline_interpreter").glob("*.py")):
            self.assertFalse(
                validator.imported_roots(path) & validator.FORBIDDEN_IMPORT_ROOTS,
                path.name,
            )


if __name__ == "__main__":
    unittest.main()
