from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "production" / "p07" / "RUN_P07_VALIDATION.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("run_p07_validation", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load_runner()


class P07ValidationTests(unittest.TestCase):
    def test_profile_is_internal_and_non_production(self):
        profile = runner.load_json(runner.PROFILE_PATH)
        self.assertEqual("internal-testbed-no-publication", profile["scope"])
        self.assertFalse(profile["production_ready"])

    def test_standalone_source_has_no_forbidden_capabilities(self):
        profile = runner.load_json(runner.PROFILE_PATH)
        result = runner.static_security(profile)
        self.assertEqual("passed", result["status"], result["findings"])

    def test_hash_rollback_rehearsal_passes(self):
        profile = runner.load_json(runner.PROFILE_PATH)
        result = runner.recovery(profile)
        self.assertEqual("passed", result["status"])
        self.assertTrue(result["corruption_detected"])


if __name__ == "__main__":
    unittest.main()
