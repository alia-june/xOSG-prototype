"""Run bounded P07 validation for the unpublished internal testbed."""

from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
from time import perf_counter
import tracemalloc
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
P07 = ROOT / "production" / "p07"
PROFILE_PATH = P07 / "VALIDATION_PROFILE.json"
SOURCE_ROOT = ROOT / "development" / "nlp-offline-interpreter" / "src"
PACKAGE_ROOT = SOURCE_ROOT / "nlp_offline_interpreter"
REPORTS = ROOT / "production" / "reports"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def static_security(profile: dict[str, Any]) -> dict[str, Any]:
    forbidden_imports = set(profile["security"]["forbidden_runtime_import_roots"])
    forbidden_calls = set(profile["security"]["forbidden_runtime_calls"])
    findings: list[str] = []
    inspected = 0
    for path in sorted(PACKAGE_ROOT.glob("*.py")):
        inspected += 1
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".", 1)[0] for alias in node.names}
                for name in sorted(roots & forbidden_imports):
                    findings.append(f"{path.name}:{node.lineno}:forbidden import {name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                name = node.module.split(".", 1)[0]
                if name in forbidden_imports:
                    findings.append(f"{path.name}:{node.lineno}:forbidden import {name}")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in forbidden_calls:
                    findings.append(
                        f"{path.name}:{node.lineno}:forbidden call {node.func.id}"
                    )
    return {
        "status": "passed" if not findings else "failed",
        "files_inspected": inspected,
        "findings": findings,
    }


def behavioral_and_performance(profile: dict[str, Any]) -> dict[str, Any]:
    sys.path.insert(0, str(SOURCE_ROOT))
    try:
        from nlp_offline_interpreter import analyze_text, canonical_json

        typical = "Please examine this generic testbed input."
        expected = canonical_json(analyze_text(typical))
        deterministic = all(
            canonical_json(analyze_text(typical)) == expected for _ in range(1000)
        )

        limits = profile["performance"]
        started = perf_counter()
        for _ in range(limits["typical_iterations"]):
            analyze_text(typical)
        typical_seconds = perf_counter() - started

        # Exceed the 256-token retention bound while staying below the accepted
        # 4,096-character source bound so the expected result is partial.
        maximum = " ".join("token" for _ in range(600))
        started = perf_counter()
        maximum_result = None
        for _ in range(limits["maximum_input_iterations"]):
            maximum_result = analyze_text(maximum)
        maximum_seconds = perf_counter() - started
        assert maximum_result is not None
        rendered = canonical_json(maximum_result).encode("utf-8")

        tracemalloc.start()
        for _ in range(500):
            analyze_text(typical)
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        payload = json.loads(rendered)
        boundary_ok = (
            payload["authority_effect"] == "NONE"
            and payload["execution_allowed"] is False
            and payload["status"] == "partial"
            and bool(payload["unresolved"])
        )
        passed = (
            deterministic
            and boundary_ok
            and typical_seconds <= limits["typical_total_seconds_max"]
            and maximum_seconds <= limits["maximum_input_total_seconds_max"]
            and peak_bytes <= limits["tracked_peak_bytes_max"]
            and len(rendered) <= limits["maximum_canonical_output_bytes"]
        )
        return {
            "status": "passed" if passed else "failed",
            "deterministic_repetitions": 1000,
            "deterministic": deterministic,
            "authority_boundary_preserved": boundary_ok,
            "typical_iterations": limits["typical_iterations"],
            "typical_total_seconds": round(typical_seconds, 6),
            "maximum_input_iterations": limits["maximum_input_iterations"],
            "maximum_input_total_seconds": round(maximum_seconds, 6),
            "tracked_peak_bytes": peak_bytes,
            "maximum_output_bytes": len(rendered),
        }
    finally:
        try:
            sys.path.remove(str(SOURCE_ROOT))
        except ValueError:
            pass


def compatibility(profile: dict[str, Any]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for version in profile["compatibility"]["windows_cpython_versions"]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(SOURCE_ROOT)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        command = [
            "py",
            f"-{version}",
            "-B",
            "-m",
            "nlp_offline_interpreter",
            "--basic",
            "testbed",
            "compatibility",
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            parsed = json.loads(completed.stdout) if completed.returncode == 0 else {}
            passed = (
                completed.returncode == 0
                and parsed.get("authority_effect") == "NONE"
                and parsed.get("execution_allowed") is False
                and parsed.get("status") == "parsed_single"
            )
            results.append(
                {
                    "version": version,
                    "status": "passed" if passed else "failed",
                    "returncode": completed.returncode,
                    "stderr": completed.stderr[-2000:],
                }
            )
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            results.append(
                {"version": version, "status": "failed", "error": type(exc).__name__}
            )
    return {
        "status": "passed" if all(item["status"] == "passed" for item in results) else "failed",
        "runtimes": results,
    }


def recovery(profile: dict[str, Any]) -> dict[str, Any]:
    artifact_value = profile["artifact"]
    pure = PurePosixPath(artifact_value)
    if pure.is_absolute() or ".." in pure.parts:
        return {"status": "failed", "error": "unsafe artifact path"}
    artifact = ROOT.joinpath(*pure.parts)
    expected = profile["artifact_sha256"]
    if not artifact.is_file() or file_sha256(artifact) != expected:
        return {"status": "failed", "error": "known-good artifact mismatch"}
    started = perf_counter()
    with tempfile.TemporaryDirectory(prefix="nlp-p07-recovery-") as temporary:
        work = Path(temporary)
        backup = work / "known-good.whl"
        active = work / "active.whl"
        shutil.copy2(artifact, backup)
        shutil.copy2(artifact, active)
        with active.open("ab") as stream:
            stream.write(b"P07-INJECTED-CORRUPTION")
        corruption_detected = file_sha256(active) != expected
        shutil.copy2(backup, active)
        restored = file_sha256(active) == expected
    elapsed = perf_counter() - started
    return {
        "status": "passed" if corruption_detected and restored else "failed",
        "failure_injected": "appended bytes to isolated working copy",
        "corruption_detected": corruption_detected,
        "restored_sha256": expected if restored else file_sha256(artifact),
        "restore_elapsed_seconds": round(elapsed, 6),
        "data_loss_window": "not applicable; no persistent runtime state",
    }


def evaluate() -> tuple[dict[str, Any], list[str]]:
    profile = load_json(PROFILE_PATH)
    checks = {
        "static_security": static_security(profile),
        "behavior_and_performance": behavioral_and_performance(profile),
        "compatibility": compatibility(profile),
        "recovery": recovery(profile),
    }
    errors = [name for name, result in checks.items() if result["status"] != "passed"]
    report = {
        "schema": "nlp-p07-validation-report/1",
        "status": "passed" if not errors else "failed",
        "scope": profile["scope"],
        "production_ready": False,
        "authority_effect": "NONE",
        "checks": checks,
        "errors": errors,
        "limitations": profile["limitations"],
    }
    return report, errors


def safe_report_path(value: str) -> Path:
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError("report path must be safe and relative")
    target = ROOT.joinpath(*pure.parts)
    if target.parent.resolve() != REPORTS.resolve():
        raise ValueError("report path must be directly under production/reports")
    if target.exists():
        raise FileExistsError("report path already exists")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    report, errors = evaluate()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        target = safe_report_path(args.report)
        target.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
