"""Run ordered local checks without deployment or external mutation."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time
from typing import Mapping


ROOT = Path(__file__).resolve().parent.parent
REPORT_ROOT = (ROOT / "production" / "reports").resolve()
OUTPUT_TAIL_LIMIT = 12_000


@dataclass(frozen=True)
class Check:
    check_id: str
    description: str
    command: tuple[str, ...]
    cwd: Path
    environment: Mapping[str, str] | None = None
    timeout_seconds: int = 300

    def __post_init__(self) -> None:
        if not self.check_id or any(character.isspace() for character in self.check_id):
            raise ValueError("check_id must be a non-empty token")
        if not self.command or not all(isinstance(item, str) and item for item in self.command):
            raise ValueError("check command must contain non-empty strings")
        if not self.cwd.is_dir():
            raise ValueError(f"check cwd is not a directory: {self.cwd}")
        if (
            not isinstance(self.timeout_seconds, int)
            or isinstance(self.timeout_seconds, bool)
            or self.timeout_seconds < 1
        ):
            raise ValueError("check timeout_seconds must be a positive integer")
        if self.environment is not None and not all(
            isinstance(key, str)
            and key
            and isinstance(value, str)
            for key, value in self.environment.items()
        ):
            raise ValueError("check environment must contain non-empty string pairs")


def build_checks(python: str | None = None, node: str | None = None) -> list[Check]:
    python_executable = python or sys.executable
    node_executable = node or shutil.which("node") or "node"
    core = ROOT / "projects" / "lexicon-core"
    frontend = ROOT / "projects" / "natural-language-front-end"
    atlas = ROOT / "projects" / "lexicon-atlas"
    file_atlas = ROOT / "projects" / "file-atlas"
    successor = ROOT / "development" / "nlp-offline-interpreter"
    successor_pythonpath = os.pathsep.join(
        (
            str(successor / "src"),
            str(core / "src"),
            str(frontend),
        )
    )
    return [
        Check(
            "snapshot-manifest",
            "Verify every historical manifest member without treating new files as historical.",
            (python_executable, "VERIFY_EXPORT.py"),
            ROOT,
        ),
        Check(
            "plan-order",
            "Validate the production plan sequence, dependencies, invariants, and control files.",
            (python_executable, "production/validate_plan.py"),
            ROOT,
        ),
        Check(
            "authorization-proposal",
            "Validate the accepted bounded P03 scope and deployment exclusions.",
            (python_executable, "production/validate_authorization.py"),
            ROOT,
        ),
        Check(
            "first-slice-smoke",
            "Compare proposal-only Core and front-end outputs without executing an operation.",
            (python_executable, "production/validate_first_slice.py"),
            ROOT,
        ),
        Check(
            "successor-manifest",
            "Verify the exact generic interpreter successor source set.",
            (python_executable, "development/nlp-offline-interpreter/VERIFY_MANIFEST.py"),
            ROOT,
        ),
        Check(
            "p04-pre-stage",
            "Verify the hash-locked offline package for the active P04 staging gate.",
            (python_executable, "production/p04/VERIFY_P04_STAGE.py"),
            ROOT,
        ),
        Check(
            "p05-slice",
            "Validate P05 requirement traceability and non-executing package boundaries.",
            (python_executable, "production/validate_p05_slice.py"),
            ROOT,
        ),
        Check(
            "p06-evidence",
            "Validate P06 artifact, dependency, provenance, and license evidence.",
            (python_executable, "production/validate_p06_evidence.py"),
            ROOT,
        ),
        Check(
            "p07-validation",
            "Run bounded security, behavior, performance, compatibility, and recovery validation.",
            (python_executable, "production/p07/RUN_P07_VALIDATION.py"),
            ROOT,
        ),
        Check(
            "p08-candidate",
            "Verify the exact immutable unpublished internal test candidate.",
            (python_executable, "production/p08/VERIFY_P08_CANDIDATE.py"),
            ROOT,
        ),
        Check(
            "test-environment",
            "Verify the interpreter and pinned test-only dependencies before behavior tests.",
            (python_executable, "production/validate_test_environment.py"),
            ROOT,
        ),
        Check(
            "successor-core-tests",
            "Run the generic interpreter contract and hardening tests.",
            (
                python_executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "development/nlp-offline-interpreter/tests",
                "-p",
                "test_core.py",
                "-v",
            ),
            ROOT,
            {"PYTHONPATH": successor_pythonpath},
        ),
        Check(
            "successor-integration-tests",
            "Run the staged generic adapter integration tests.",
            (
                python_executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "development/nlp-offline-interpreter/tests",
                "-p",
                "test_integration.py",
                "-v",
            ),
            ROOT,
            {"PYTHONPATH": successor_pythonpath},
        ),
        Check(
            "successor-fuzzy-tests",
            "Run deterministic loose-language, hostile-text, and metadata fuzz tests.",
            (
                python_executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "development/nlp-offline-interpreter/tests",
                "-p",
                "test_fuzzy.py",
                "-v",
            ),
            ROOT,
            {"PYTHONPATH": successor_pythonpath},
        ),
        Check(
            "successor-torture-tests",
            "Run bounded cardinality, repetition, concurrency, and boundary torture tests.",
            (
                python_executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "development/nlp-offline-interpreter/tests",
                "-p",
                "test_torture.py",
                "-v",
            ),
            ROOT,
            {"PYTHONPATH": successor_pythonpath},
        ),
        Check(
            "production-control-tests",
            "Run negative and positive regression tests for production controls.",
            (
                python_executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "production/tests",
                "-v",
            ),
            ROOT,
        ),
        Check(
            "lexicon-core-tests",
            "Run Lexicon Core behavior and catalog adapter tests.",
            (python_executable, "-m", "unittest", "discover", "-s", "tests", "-v"),
            core,
            {"PYTHONPATH": "src"},
        ),
        Check(
            "natural-language-tests",
            "Run the Natural Language front-end test suite.",
            (python_executable, "-m", "unittest", "discover", "-s", "tests", "-v"),
            frontend,
        ),
        Check(
            "lexicon-atlas-validate",
            "Validate the packaged Lexicon Atlas data build.",
            (python_executable, "validate_build.py"),
            atlas,
        ),
        Check(
            "file-atlas-verify",
            "Run the File Atlas frontend verifier.",
            (node_executable, "verify_frontend.mjs"),
            file_atlas,
        ),
    ]


def checks_for_suite(suite: str) -> list[Check]:
    checks = build_checks()
    if suite == "control":
        return checks[1:16]
    if suite == "hardening":
        return checks[8:16]
    if suite == "baseline":
        return checks
    raise ValueError(f"unsupported suite: {suite}")


def _tail(value: str | bytes | None, limit: int = OUTPUT_TAIL_LIMIT) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    if len(value) <= limit:
        return value
    marker = f"[output truncated; original_chars={len(value)}]\n"
    return marker + value[-(limit - len(marker)) :]


def run_check(check: Check) -> dict[str, object]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    if check.environment:
        environment.update(check.environment)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            check.command,
            cwd=check.cwd,
            env=environment,
            text=True,
            capture_output=True,
            timeout=check.timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "id": check.check_id,
            "description": check.description,
            "status": "timed_out",
            "duration_seconds": round(time.monotonic() - started, 3),
            "command": list(check.command),
            "cwd": str(check.cwd),
            "timeout_seconds": check.timeout_seconds,
            "stdout": _tail(exc.stdout),
            "stderr": _tail(exc.stderr),
            "error": "check exceeded its timeout",
        }
    except OSError as exc:
        return {
            "id": check.check_id,
            "description": check.description,
            "status": "failed",
            "duration_seconds": round(time.monotonic() - started, 3),
            "command": list(check.command),
            "cwd": str(check.cwd),
            "error": f"{type(exc).__name__}: {exc}",
        }
    return {
        "id": check.check_id,
        "description": check.description,
        "status": "passed" if completed.returncode == 0 else "failed",
        "duration_seconds": round(time.monotonic() - started, 3),
        "command": list(check.command),
        "cwd": str(check.cwd),
        "returncode": completed.returncode,
        "stdout": _tail(completed.stdout),
        "stderr": _tail(completed.stderr),
    }


def _resolve_report_path(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.parent != REPORT_ROOT:
        raise ValueError(f"report must be written directly under {REPORT_ROOT}")
    if resolved.suffix.lower() != ".json":
        raise ValueError("report filename must end in .json")
    if resolved.exists() or resolved.is_symlink():
        raise FileExistsError(f"refusing to replace existing report: {resolved}")
    return resolved


def _write_new_report(path: Path, report: dict[str, object]) -> None:
    resolved = _resolve_report_path(path)
    with resolved.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--suite", choices=("control", "hardening", "baseline"), default="control"
    )
    parser.add_argument("--list", action="store_true", help="List checks without running them")
    parser.add_argument("--report", type=Path, help="Write a new JSON report; refuse overwrite")
    args = parser.parse_args(argv)

    checks = checks_for_suite(args.suite)
    if args.list:
        for check in checks:
            print(f"{check.check_id}: {check.description}")
        return 0

    results: list[dict[str, object]] = []
    for check in checks:
        print(f"[{check.check_id}] {shlex.join(check.command)}", flush=True)
        result = run_check(check)
        results.append(result)
        print(f"[{check.check_id}] {result['status']}", flush=True)
        if result["status"] != "passed":
            break

    passed = len(results) == len(checks) and all(
        result["status"] == "passed" for result in results
    )
    report: dict[str, object] = {
        "schema": "nlp-production-check-report/1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "suite": args.suite,
        "status": "passed" if passed else "failed",
        "production_ready": False,
        "authority_effect": "NONE",
        "checks_planned": len(checks),
        "checks_run": len(results),
        "results": results,
    }
    if args.report:
        try:
            _write_new_report(args.report, report)
        except (FileExistsError, OSError, ValueError) as exc:
            print(f"report write failed: {exc}", file=sys.stderr)
            return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
