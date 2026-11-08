"""Validate the admitted P05 interpreter slice and its authority boundaries."""

from __future__ import annotations

import ast
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tomllib
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PRODUCTION = ROOT / "production"
PROJECT = ROOT / "development" / "nlp-offline-interpreter"
SRC = PROJECT / "src"
TRACE = PRODUCTION / "p05" / "REQUIREMENT_TRACE.json"
EXPECTED_REQUIREMENTS = [f"P05-REQ-{index:03d}" for index in range(1, 9)]
FORBIDDEN_IMPORT_ROOTS = {"httpx", "requests", "socket", "urllib"}
FORBIDDEN_CLI_FLAGS = {
    "--apply",
    "--delete",
    "--execute",
    "--move",
    "--mutate",
    "--write",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_file(value: object) -> Path | None:
    if not isinstance(value, str):
        return None
    pure = PurePosixPath(value)
    if not value or pure.is_absolute() or ".." in pure.parts:
        return None
    path = ROOT.joinpath(*pure.parts)
    return path if path.is_file() else None


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.partition(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.partition(".")[0])
    return roots


def evaluate() -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    try:
        trace = load_json(TRACE)
        plan = load_json(PRODUCTION / "production_plan.json")
        authorization = load_json(PRODUCTION / "p03_authorization.json")
        pyproject = tomllib.loads((PROJECT / "pyproject.toml").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        return {"schema": "nlp-p05-validation/1", "status": "failed"}, [str(exc)]

    if trace.get("schema") != "nlp-p05-requirement-trace/1":
        errors.append("unexpected P05 trace schema")
    if trace.get("status") != "accepted-implementation-slice":
        errors.append("P05 trace status is not accepted-implementation-slice")
    if (
        trace.get("authority_effect") != "NONE"
        or trace.get("execution_allowed") is not False
        or trace.get("production_ready") is not False
    ):
        errors.append("P05 trace exceeds the accepted authority boundary")

    phases = {item.get("id"): item for item in plan.get("phases", []) if isinstance(item, dict)}
    for phase_id in ("P03", "P04"):
        if phases.get(phase_id, {}).get("state") != "verified":
            errors.append(f"{phase_id} must be verified before P05 admission")
    if phases.get("P05", {}).get("state") not in {"in_progress", "verified"}:
        errors.append("P05 must be in_progress or verified during slice validation")
    if authorization.get("status") != "accepted-bounded-local-release":
        errors.append("bounded authorization is not accepted")
    if authorization.get("deployment_authority") != "NONE":
        errors.append("P05 cannot run with deployment authority")

    requirements = trace.get("requirements")
    if not isinstance(requirements, list):
        errors.append("requirements must be a list")
        requirements = []
    ids = [item.get("id") for item in requirements if isinstance(item, dict)]
    if ids != EXPECTED_REQUIREMENTS:
        errors.append("P05 requirement IDs must be complete and ordered")
    for item in requirements:
        if not isinstance(item, dict):
            errors.append("each P05 requirement must be an object")
            continue
        for field in ("implementation", "tests"):
            values = item.get(field)
            if not isinstance(values, list) or not values:
                errors.append(f"{item.get('id')} {field} must be non-empty")
                continue
            for value in values:
                if safe_file(value) is None:
                    errors.append(f"{item.get('id')} has unsafe or missing {field}: {value!r}")
    decision_sources = trace.get("decision_sources")
    if not isinstance(decision_sources, list) or not decision_sources:
        errors.append("decision_sources must be a non-empty list")
    else:
        for value in decision_sources:
            if safe_file(value) is None:
                errors.append(f"unsafe or missing decision source: {value!r}")

    project = pyproject.get("project", {})
    if project.get("name") != "nlp-offline-interpreter" or project.get("version") != "0.1.0":
        errors.append("unexpected package identity")
    if project.get("requires-python") != ">=3.11":
        errors.append("package must require Python 3.11 or newer")
    if project.get("dependencies") != []:
        errors.append("generic wheel must remain dependency-free")
    scripts = project.get("scripts", {})
    if scripts.get("nlp-offline-interpreter") != "nlp_offline_interpreter.integration:main":
        errors.append("unexpected CLI entry point")

    for path in sorted((SRC / "nlp_offline_interpreter").glob("*.py")):
        forbidden = imported_roots(path) & FORBIDDEN_IMPORT_ROOTS
        if forbidden:
            errors.append(f"forbidden network import in {path.name}: {sorted(forbidden)}")

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC)
    help_result = subprocess.run(
        [sys.executable, "-B", "-m", "nlp_offline_interpreter", "--help"],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    if help_result.returncode != 0:
        errors.append("CLI help failed")
    help_text = help_result.stdout.casefold()
    for flag in sorted(FORBIDDEN_CLI_FLAGS):
        if flag in help_text:
            errors.append(f"forbidden CLI authority flag is exposed: {flag}")

    sys.path.insert(0, str(SRC))
    try:
        from nlp_offline_interpreter import analyze_text, canonical_json

        first = analyze_text("Hello, bounded world!")
        second = analyze_text("Hello, bounded world!")
        payload = first.to_dict()
        if canonical_json(first) != canonical_json(second):
            errors.append("basic output is not deterministic")
        if payload.get("authority_effect") != "NONE" or payload.get("execution_allowed") is not False:
            errors.append("basic output exceeds authority boundary")
        if payload.get("schema") != "generic-interpretation/1":
            errors.append("basic output schema is unexpected")
        if payload.get("source_sha256") != sha256(b"Hello, bounded world!").hexdigest():
            errors.append("basic source digest is incorrect")
    except (ImportError, TypeError, ValueError) as exc:
        errors.append(f"public API smoke test failed: {exc}")
    finally:
        if sys.path and sys.path[0] == str(SRC):
            sys.path.pop(0)

    report = {
        "schema": "nlp-p05-validation/1",
        "slice_id": trace.get("slice_id"),
        "status": "passed" if not errors else "failed",
        "requirements": len(requirements),
        "authority_effect": "NONE",
        "execution_allowed": False,
        "production_ready": False,
        "errors": errors,
    }
    return report, errors


def main() -> int:
    report, errors = evaluate()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
