from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "production" / "p08" / "VERIFY_P08_CANDIDATE.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_p08_candidate", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verifier = load_verifier()


class P08CandidateTests(unittest.TestCase):
    def test_exact_internal_candidate_passes(self):
        report, errors = verifier.evaluate()
        self.assertEqual([], errors)
        self.assertEqual("passed", report["status"])
        self.assertFalse(report["production_ready"])
        self.assertFalse(report["publication_allowed"])
        self.assertEqual("NONE", report["authority_effect"])
        self.assertEqual(6, report["members"])


if __name__ == "__main__":
    unittest.main()
