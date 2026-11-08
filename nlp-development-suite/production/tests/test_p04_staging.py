from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
P04 = ROOT / "production" / "p04"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


import sys

sys.path.insert(0, str(P04))
verify = load("verify_p04", P04 / "VERIFY_P04_STAGE.py")
builder = load("build_p04_manifest", P04 / "BUILD_WHEELHOUSE_MANIFEST.py")
runner = load("run_clean_stage", P04 / "RUN_CLEAN_STAGE.py")


class P04StagingTests(unittest.TestCase):
    def test_input_and_hash_lock_cover_the_same_exact_versions(self):
        direct = verify.parse_input(P04 / "requirements-py314.in")
        for tag in ("py311", "py312", "py313", "py314"):
            locked = verify.parse_lock(P04 / f"requirements-{tag}.lock")
            self.assertEqual(
                direct, {name: version for name, (version, _) in locked.items()}
            )
            self.assertEqual(len(locked), 15)

    def test_lock_parser_rejects_unhashed_or_editable_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.lock"
            path.write_text("-e ../../project\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                verify.parse_lock(path)

    def test_setuptools_wheel_ignores_nested_vendored_metadata(self):
        wheel = next((P04 / "wheelhouse").glob("setuptools-*.whl"))
        name, version, _ = builder.metadata(wheel)
        self.assertEqual((name.lower(), version), ("setuptools", "84.0.0"))

    def test_current_staging_package_has_no_structural_errors(self):
        self.assertEqual(verify.verify(), [])

    def test_active_workflow_is_non_deploying_and_uses_no_secrets(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("deploy", workflow.lower())
        self.assertIn("VERIFY_P04_STAGE.py", workflow)
        self.assertIn("RUN_CLEAN_STAGE.py", workflow)

    def test_report_path_is_confined_and_append_only(self):
        with self.assertRaises(ValueError):
            runner.report_path(ROOT / "outside.json")
        with tempfile.NamedTemporaryFile(
            dir=ROOT / "production" / "reports", suffix=".json"
        ) as existing:
            with self.assertRaises(FileExistsError):
                runner.report_path(Path(existing.name))

    def test_git_source_state_is_bound_to_current_revision(self):
        state = runner.git_source_state()
        self.assertEqual("git", state["kind"])
        self.assertIsInstance(state["commit"], str)
        self.assertEqual(40, len(state["commit"]))
        self.assertIsInstance(state["clean"], bool)


if __name__ == "__main__":
    unittest.main()
