from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "production" / "validate_p06_evidence.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_p06_evidence", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class P06EvidenceTests(unittest.TestCase):
    def test_current_evidence_is_verified_for_internal_testbed(self):
        report, errors = validator.evaluate()
        self.assertEqual([], errors)
        self.assertEqual("passed", report["status"])
        self.assertEqual(
            "verified_internal_testbed_distribution_deferred",
            report["p06_disposition"],
        )
        self.assertEqual(10, report["wheel_members"])
        self.assertEqual(0, report["runtime_dependencies"])
        self.assertFalse(report["lexical_data_bundled"])
        self.assertFalse(report["production_ready"])


if __name__ == "__main__":
    unittest.main()
