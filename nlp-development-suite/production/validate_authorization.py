"""Validate the accepted, bounded P03 authorization and its exclusions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any


EXPECTED_DECISIONS = [f"Q-{index:03d}" for index in range(1, 8)]
ALLOWED_DECISION_STATES = {
    "proposed",
    "unresolved",
    "accepted_for_development",
    "accepted_canon_for_development",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_relative(value: str) -> bool:
    pure = PurePosixPath(value)
    return bool(value) and not pure.is_absolute() and ".." not in pure.parts


def validate_authorization(
    packet: dict[str, Any], plan: dict[str, Any], root: Path
) -> list[str]:
    errors: list[str] = []
    if packet.get("schema") != "nlp-production-authorization/1":
        errors.append("authorization schema is invalid")
    if packet.get("status") != "accepted-bounded-local-release":
        errors.append("authorization status must be accepted-bounded-local-release")
    if packet.get("truth_state") != "ACCEPTED_CANON":
        errors.append("authorization truth_state must be ACCEPTED_CANON")
    if packet.get("authority_effect") != "P00-P09_LOCAL_RELEASE_WORKFLOW":
        errors.append("authorization authority_effect exceeds or misses P00-P09")
    if packet.get("production_ready") is not False:
        errors.append("authorization must not claim production readiness")
    if packet.get("deployment_authority") != "NONE":
        errors.append("authorization must not grant deployment authority")
    if packet.get("current_operating_scope") != "internal-testbed-no-publication":
        errors.append("current operating scope must remain an unpublished internal testbed")
    if packet.get("phase") != "P03":
        errors.append("authorization packet must apply to P03")
    acceptance_evidence = packet.get("acceptance_evidence")
    if not isinstance(acceptance_evidence, str) or not _safe_relative(
        acceptance_evidence
    ):
        errors.append("authorization acceptance evidence path is unsafe")
    elif not root.joinpath(*PurePosixPath(acceptance_evidence).parts).is_file():
        errors.append("authorization acceptance evidence is missing")

    development = packet.get("development_authorization")
    if not isinstance(development, dict):
        errors.append("development_authorization must be an object")
    else:
        if development.get("status") != "accepted":
            errors.append("bounded development authorization is not recorded")
        if development.get("authority") != "user":
            errors.append("bounded development authority must be the user")
        if development.get("production_effect") != "NONE":
            errors.append("development authorization must have no production effect")
        evidence = development.get("evidence")
        if not isinstance(evidence, str) or not _safe_relative(evidence):
            errors.append("development authorization evidence path is unsafe")
        elif not root.joinpath(*PurePosixPath(evidence).parts).is_file():
            errors.append("development authorization evidence is missing")

    release = packet.get("first_release")
    if not isinstance(release, dict):
        errors.append("first_release must be an object")
    else:
        if release.get("id") != "nlp-offline-interpreter/0.1":
            errors.append("first release id is not the bounded proposed release")
        for key in (
            "execution_allowed",
            "network_allowed",
            "filesystem_mutation_allowed",
            "catalog_mutation_allowed",
        ):
            if release.get(key) is not False:
                errors.append(f"{key} must be false")
        for key in ("included", "excluded", "acceptance_criteria"):
            value = release.get(key)
            if not isinstance(value, list) or not value:
                errors.append(f"first_release {key} must be a non-empty list")
        excluded = " ".join(str(value).casefold() for value in release.get("excluded", []))
        for phrase in ("filesystem operation execution", "network", "production deployment"):
            if phrase not in excluded:
                errors.append(f"first release exclusions must include {phrase!r}")

    decisions = packet.get("decisions")
    if not isinstance(decisions, list):
        errors.append("decisions must be a list")
    else:
        ids = [decision.get("id") for decision in decisions if isinstance(decision, dict)]
        if ids != EXPECTED_DECISIONS:
            errors.append("decisions must contain Q-001 through Q-007 in order")
        for decision in decisions:
            if not isinstance(decision, dict):
                errors.append("each decision must be an object")
                continue
            state = decision.get("state")
            decision_id = decision.get("id")
            if state not in ALLOWED_DECISION_STATES:
                errors.append(f"{decision_id} has an accepted or invalid state")
            if state == "accepted_for_development":
                if decision_id != "Q-002" or decision.get("authority") != "user":
                    errors.append("Q-002 development scope is not correctly authorized")
            elif state == "accepted_canon_for_development":
                if decision_id not in {
                    "Q-001",
                    "Q-003",
                    "Q-004",
                    "Q-005",
                    "Q-006",
                    "Q-007",
                }:
                    errors.append(f"{decision_id} cannot use the accepted canon state")
                if decision.get("authority") != "user":
                    errors.append(f"{decision_id} canon is not user-authorized")
                if decision.get("production_effect") != "NONE":
                    errors.append(f"{decision_id} must have no production effect")
                decision_evidence = decision.get("evidence")
                if not isinstance(decision_evidence, str) or not _safe_relative(
                    decision_evidence
                ):
                    errors.append(f"{decision_id} evidence path is unsafe")
                elif not root.joinpath(
                    *PurePosixPath(decision_evidence).parts
                ).is_file():
                    errors.append(f"{decision_id} evidence is missing")
            elif decision.get("authority") != "unassigned":
                errors.append(f"{decision_id} authority must remain unassigned")
            if not isinstance(decision.get("value"), str) or not decision["value"].strip():
                errors.append(f"{decision.get('id')} value must be non-empty")

    evidence = packet.get("source_evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("source_evidence must be a non-empty list")
    else:
        for value in evidence:
            if not isinstance(value, str) or not _safe_relative(value):
                errors.append(f"unsafe evidence path: {value!r}")
                continue
            path = root.joinpath(*PurePosixPath(value).parts)
            if not path.is_file():
                errors.append(f"missing source evidence: {value}")

    phases = {phase.get("id"): phase for phase in plan.get("phases", []) if isinstance(phase, dict)}
    if phases.get("P03", {}).get("state") != "verified":
        errors.append("P03 must be verified after bounded authorization")
    if phases.get("P04", {}).get("state") != "verified":
        errors.append("P04 must be verified after bounded staging completion")
    if phases.get("P05", {}).get("state") != "verified":
        errors.append("P05 must be verified after bounded implementation admission")
    if phases.get("P06", {}).get("state") != "verified":
        errors.append("P06 must be verified only for the internal-testbed scope")
    if phases.get("P07", {}).get("state") != "verified":
        errors.append("P07 must be verified only for the internal-testbed scope")
    if phases.get("P08", {}).get("state") != "verified":
        errors.append("P08 must be verified only as an unpublished internal test candidate")
    if phases.get("P09", {}).get("state") != "not_started":
        errors.append("P09 must remain not_started before exact-hash acceptance")
    for phase_id in ("P10", "P11"):
        if phases.get(phase_id, {}).get("state") != "blocked":
            errors.append(f"{phase_id} must remain blocked without new authority")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--packet",
        type=Path,
        default=Path(__file__).with_name("p03_authorization.json"),
    )
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    try:
        packet = load_json(args.packet.resolve())
        plan = load_json(Path(__file__).with_name("production_plan.json"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"authorization load failed: {exc}", file=sys.stderr)
        return 2
    errors = validate_authorization(packet, plan, root)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "passed",
                "proposal_id": packet["proposal_id"],
                "decision_count": len(packet["decisions"]),
                "authorization_status": packet["status"],
                "p03_state": "verified",
                "production_ready": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
