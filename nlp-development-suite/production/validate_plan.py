"""Validate the production-control plan without changing workspace state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any


EXPECTED_TRANSITIONS = [
    "identify",
    "freeze",
    "describe",
    "authorize",
    "stage",
    "transfer",
    "verify",
    "validate",
    "commit",
    "attest",
    "retain",
    "retire",
]
ALLOWED_STATES = {"not_started", "in_progress", "blocked", "verified"}
REQUIRED_PHASE_KEYS = {
    "id",
    "sequence",
    "transition",
    "name",
    "depends_on",
    "state",
    "objective",
    "deliverables",
    "exit_criteria",
    "evidence",
}


class DuplicateKeyError(ValueError):
    """Raised when JSON contains a duplicate object key."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def load_plan(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
    )


def _is_safe_relative_path(value: str) -> bool:
    pure = PurePosixPath(value)
    return bool(value) and not pure.is_absolute() and ".." not in pure.parts


def validate_document(plan: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []

    if plan.get("schema") != "nlp-production-plan/1":
        errors.append("schema must be nlp-production-plan/1")
    if plan.get("status") != "accepted-bounded-local-release-plan":
        errors.append("status must identify the accepted bounded local release plan")
    if plan.get("authority_effect") != "P00-P09_LOCAL_RELEASE_WORKFLOW":
        errors.append("authority_effect must remain bounded to P00-P09")
    if plan.get("production_ready") is not False:
        errors.append("production_ready must remain false before exact-candidate acceptance")
    acceptance_evidence = plan.get("acceptance_evidence")
    if not isinstance(acceptance_evidence, str) or not _is_safe_relative_path(
        acceptance_evidence
    ):
        errors.append("acceptance_evidence must be a safe relative path")
    elif not root.joinpath(*PurePosixPath(acceptance_evidence).parts).is_file():
        errors.append("acceptance_evidence is missing")
    if plan.get("control_sequence") != EXPECTED_TRANSITIONS:
        errors.append("control_sequence does not match the required transition order")

    control_files = plan.get("required_control_files")
    if not isinstance(control_files, list) or not control_files:
        errors.append("required_control_files must be a non-empty list")
    else:
        seen_files: set[str] = set()
        for value in control_files:
            if not isinstance(value, str) or not _is_safe_relative_path(value):
                errors.append(f"unsafe control file path: {value!r}")
                continue
            if value in seen_files:
                errors.append(f"duplicate control file path: {value}")
                continue
            seen_files.add(value)
            path = root.joinpath(*PurePosixPath(value).parts)
            if not path.is_file():
                errors.append(f"required control file is missing: {value}")

    phases = plan.get("phases")
    if not isinstance(phases, list) or not phases:
        errors.append("phases must be a non-empty list")
        return errors
    if len(phases) != len(EXPECTED_TRANSITIONS):
        errors.append("there must be exactly one phase for each transition")

    phase_ids: list[str] = []
    seen_ids: set[str] = set()
    for index, phase in enumerate(phases):
        if not isinstance(phase, dict):
            errors.append(f"phase at index {index} is not an object")
            continue
        missing = REQUIRED_PHASE_KEYS - phase.keys()
        if missing:
            errors.append(
                f"phase at index {index} is missing keys: {', '.join(sorted(missing))}"
            )

        phase_id = phase.get("id")
        expected_id = f"P{index:02d}"
        if not isinstance(phase_id, str) or not re.fullmatch(r"P\d{2}", phase_id):
            errors.append(f"invalid phase id at index {index}: {phase_id!r}")
        elif phase_id != expected_id:
            errors.append(f"phase at index {index} must be {expected_id}, not {phase_id}")
        if phase_id in seen_ids:
            errors.append(f"duplicate phase id: {phase_id}")
        if isinstance(phase_id, str):
            seen_ids.add(phase_id)
            phase_ids.append(phase_id)

        if phase.get("sequence") != index:
            errors.append(f"{phase_id or expected_id} sequence must be {index}")
        expected_transition = EXPECTED_TRANSITIONS[index]
        if phase.get("transition") != expected_transition:
            errors.append(
                f"{phase_id or expected_id} transition must be {expected_transition}"
            )
        if phase.get("state") not in ALLOWED_STATES:
            errors.append(f"{phase_id or expected_id} has an invalid state")

        dependencies = phase.get("depends_on")
        if not isinstance(dependencies, list):
            errors.append(f"{phase_id or expected_id} depends_on must be a list")
        else:
            if index == 0 and dependencies:
                errors.append("P00 must not have dependencies")
            if index > 0:
                previous = f"P{index - 1:02d}"
                if previous not in dependencies:
                    errors.append(f"{phase_id or expected_id} must depend on {previous}")
            for dependency in dependencies:
                if dependency not in seen_ids:
                    errors.append(
                        f"{phase_id or expected_id} dependency is not an earlier phase: {dependency}"
                    )

        if phase.get("state") == "verified" and not phase.get("evidence"):
            errors.append(f"{phase_id or expected_id} is verified without evidence")
        if phase.get("state") == "blocked" and not phase.get("blockers"):
            errors.append(f"{phase_id or expected_id} is blocked without blockers")

        for key in ("deliverables", "exit_criteria", "evidence"):
            value = phase.get(key)
            if not isinstance(value, list):
                errors.append(f"{phase_id or expected_id} {key} must be a list")
        for key in ("name", "objective"):
            value = phase.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{phase_id or expected_id} {key} must be non-empty")

    if len(phase_ids) != len(set(phase_ids)):
        errors.append("phase identifiers must be unique")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan",
        type=Path,
        default=Path(__file__).with_name("production_plan.json"),
    )
    args = parser.parse_args(argv)
    plan_path = args.plan.resolve()
    root = Path(__file__).resolve().parent.parent
    try:
        plan = load_plan(plan_path)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        print(f"plan load failed: {exc}", file=sys.stderr)
        return 2

    errors = validate_document(plan, root)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "passed",
                "schema": plan["schema"],
                "phases": len(plan["phases"]),
                "required_control_files": len(plan["required_control_files"]),
                "production_ready": plan["production_ready"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
