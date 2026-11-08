from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
PRODUCTION = ROOT / "production"
if str(PRODUCTION) not in sys.path:
    sys.path.insert(0, str(PRODUCTION))

import run_checks  # noqa: E402
import validate_test_environment  # noqa: E402


class TestRigHardeningTests(unittest.TestCase):
    def test_environment_preflight_passes_in_prepared_environment(self):
        report, errors = validate_test_environment.evaluate()
        self.assertEqual([], errors)
        self.assertEqual("passed", report["status"])
        self.assertFalse(report["production_ready"])

    def test_check_rejects_boolean_or_zero_timeout(self):
        for value in (True, 0, -1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                run_checks.Check("bad", "bad", (sys.executable, "-V"), ROOT, timeout_seconds=value)

    def test_timeout_is_distinct_and_bounded(self):
        check = run_checks.Check(
            "timeout-probe",
            "exercise timeout",
            (sys.executable, "-c", "import time; print('started', flush=True); time.sleep(5)"),
            ROOT,
            timeout_seconds=1,
        )
        result = run_checks.run_check(check)
        self.assertEqual("timed_out", result["status"])
        self.assertEqual(1, result["timeout_seconds"])
        self.assertIn("started", result["stdout"])

    def test_missing_executable_is_a_failed_result(self):
        check = run_checks.Check(
            "missing-probe", "exercise launch failure", ("definitely-not-a-command-92741",), ROOT
        )
        result = run_checks.run_check(check)
        self.assertEqual("failed", result["status"])
        self.assertIn("FileNotFoundError", result["error"])

    def test_output_is_tail_bounded_with_explicit_marker(self):
        check = run_checks.Check(
            "output-probe",
            "exercise output bound",
            (sys.executable, "-c", "print('x' * 20000)"),
            ROOT,
        )
        result = run_checks.run_check(check)
        self.assertEqual("passed", result["status"])
        self.assertLessEqual(len(result["stdout"]), run_checks.OUTPUT_TAIL_LIMIT)
        self.assertTrue(result["stdout"].startswith("[output truncated;"))

    def test_child_environment_disables_bytecode_and_applies_override(self):
        check = run_checks.Check(
            "environment-probe",
            "exercise environment",
            (
                sys.executable,
                "-c",
                "import json,os; print(json.dumps({'bytecode':os.getenv('PYTHONDONTWRITEBYTECODE'),'probe':os.getenv('RIG_PROBE')}))",
            ),
            ROOT,
            {"RIG_PROBE": "bounded"},
        )
        result = run_checks.run_check(check)
        payload = json.loads(result["stdout"])
        self.assertEqual({"bytecode": "1", "probe": "bounded"}, payload)

    def test_report_path_is_confined_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory) / "outside.json"
            with self.assertRaisesRegex(ValueError, "directly under"):
                run_checks._write_new_report(outside, {"status": "test"})
        target = run_checks.REPORT_ROOT / "test-rig-temporary-receipt.json"
        try:
            run_checks._write_new_report(target, {"status": "test"})
            with self.assertRaises(FileExistsError):
                run_checks._write_new_report(target, {"status": "replacement"})
        finally:
            if target.is_file():
                target.unlink()

    def test_check_order_includes_preflight_before_behavior(self):
        ids = [item.check_id for item in run_checks.checks_for_suite("baseline")]
        self.assertLess(ids.index("successor-manifest"), ids.index("p04-pre-stage"))
        self.assertLess(ids.index("p04-pre-stage"), ids.index("test-environment"))
        self.assertLess(ids.index("test-environment"), ids.index("successor-core-tests"))
        self.assertLess(ids.index("successor-fuzzy-tests"), ids.index("successor-torture-tests"))


if __name__ == "__main__":
    unittest.main()
