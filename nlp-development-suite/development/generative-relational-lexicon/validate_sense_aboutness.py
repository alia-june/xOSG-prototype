from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
DECISION_PATH = ROOT / "SENSE_ABOUTNESS_BASELINE_DECISION.json"
SCHEMA_PATH = ROOT / "schemas" / "sense-aboutness-candidate-v0.1.schema.json"
FIXTURE_DIR = ROOT / "fixtures" / "sense-aboutness"
ROGET_SOURCE_PATH = ROOT / "pilot" / "tier-zero" / "raw" / "project-gutenberg-ebook-22.txt"
OUTPUT_DIR = ROOT / "pilot" / "sense-aboutness"
REPORT_PATH = OUTPUT_DIR / "SENSE_ABOUTNESS_CONTRACT_REPORT.json"
RECEIPT_PATH = OUTPUT_DIR / "SENSE_ABOUTNESS_CONTRACT_RECEIPT.json"
VALIDATOR_VERSION = "sense-aboutness-contract/1"
SEMANTIC_SUPPORT_KINDS = {
    "CATEGORY_PLACEMENT",
    "SOURCE_DOMAIN_LABEL",
    "USAGE_CONTEXT",
    "REVIEWED_SENSE_RELATION",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def baseline_bytes(commit: str, path: str) -> bytes:
    listing = subprocess.check_output(
        ["git", "ls-tree", commit, "--", path], cwd=REPO_ROOT, text=True, encoding="utf-8"
    ).strip()
    if not listing:
        raise ValueError(f"baseline path is absent from commit {commit}: {path}")
    metadata, listed_path = listing.split("\t", 1)
    if listed_path != path:
        raise ValueError(f"baseline path resolution changed: {path} -> {listed_path}")
    mode, object_type, object_id = metadata.split()
    if mode != "100644" or object_type != "blob":
        raise ValueError(f"baseline input is not a regular tracked blob: {path}")
    return subprocess.check_output(["git", "cat-file", "blob", object_id], cwd=REPO_ROOT)


def validate_decision(decision: dict[str, Any]) -> None:
    if decision.get("status") != "AUTHORIZED_TEST_SCHEMA_AND_EVALUATION_BASELINE":
        raise ValueError("sense-aboutness baseline is not authorized")
    if decision.get("authority_effect") != "TEST_SCHEMA_AND_BASELINE_ONLY":
        raise ValueError("authority effect must remain schema-and-baseline only")
    for field in (
        "production_ready",
        "publication_allowed",
        "canon_admission",
        "content_ingestion_authorized",
        "semantic_generation_authorized",
    ):
        if decision.get(field) is not False:
            raise ValueError(f"decision boundary changed: {field}")
    commit = str(decision["baseline_commit"])
    for artifact in decision["baseline_inputs"]:
        path = REPO_ROOT / artifact["path"]
        current = path.read_bytes()
        committed = baseline_bytes(commit, artifact["path"])
        if current != committed:
            raise ValueError(f"baseline input differs from pinned commit: {artifact['path']}")
        if len(current) != artifact["bytes"]:
            raise ValueError(f"baseline byte count changed: {artifact['path']}")
        if sha256_bytes(current) != artifact["sha256"]:
            raise ValueError(f"baseline SHA-256 changed: {artifact['path']}")


def build_schema_validator(schema: dict[str, Any]):
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:  # pragma: no cover - exercised by environment preflight
        raise RuntimeError("jsonschema==4.26.0 is required for Draft 2020-12 validation") from exc
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _unique(values: list[str], label: str, errors: list[str]) -> None:
    if len(values) != len(set(values)):
        errors.append(f"duplicate {label}")


def validate_semantics(record: dict[str, Any]) -> None:
    errors: list[str] = []
    evidence = record.get("evidence", [])
    evidence_ids = [item.get("evidence_id", "") for item in evidence]
    _unique(evidence_ids, "evidence identifiers", errors)
    evidence_by_id = {item.get("evidence_id"): item for item in evidence}
    roget_lines: list[str] | None = None
    for item in evidence:
        span = item.get("source_span", {})
        if span.get("end", -1) < span.get("start", 0):
            errors.append(f"reversed source span: {item.get('evidence_id')}")
        if item.get("source_id") == "project-gutenberg-roget-22":
            if item.get("artifact_sha256") != sha256_path(ROGET_SOURCE_PATH):
                errors.append(f"wrong Roget artifact hash: {item.get('evidence_id')}")
            if span.get("kind") == "LINE":
                if roget_lines is None:
                    roget_lines = ROGET_SOURCE_PATH.read_text(encoding="utf-8").splitlines()
                start = span.get("start", 0)
                end = span.get("end", -1)
                if start < 1 or end > len(roget_lines):
                    errors.append(f"Roget line span is out of range: {item.get('evidence_id')}")
                else:
                    excerpt = "\n".join(roget_lines[start - 1 : end]).casefold()
                    normalized_form = record.get("form", {}).get("normalized_text", "").casefold()
                    if normalized_form not in excerpt:
                        errors.append(f"Roget span lacks the recorded form: {item.get('evidence_id')}")

    senses = record.get("sense_candidates", [])
    sense_ids = [item.get("sense_candidate_id", "") for item in senses]
    _unique(sense_ids, "sense candidate identifiers", errors)
    assertion_ids = [
        assertion.get("assertion_id", "")
        for sense in senses
        for assertion in sense.get("aboutness_assertions", [])
    ]
    _unique(assertion_ids, "assertion identifiers", errors)
    assertion_id_set = set(assertion_ids)
    sense_id_set = set(sense_ids)
    assertion_by_id = {
        assertion.get("assertion_id"): assertion
        for sense in senses
        for assertion in sense.get("aboutness_assertions", [])
    }
    sense_by_id = {sense.get("sense_candidate_id"): sense for sense in senses}

    def require_refs(refs: list[str], owner: str, semantic: bool) -> None:
        for ref in refs:
            item = evidence_by_id.get(ref)
            if item is None:
                errors.append(f"unknown evidence reference {ref} from {owner}")
            elif semantic and item.get("evidence_kind") not in SEMANTIC_SUPPORT_KINDS:
                errors.append(
                    f"{owner} uses non-semantic {item.get('evidence_kind')} evidence {ref}"
                )

    for sense in senses:
        sense_id = sense.get("sense_candidate_id", "")
        require_refs(sense.get("scope_evidence_refs", []), f"scope {sense_id}", semantic=True)
        distinguished = sense.get("distinguished_from", [])
        for other in distinguished:
            if other not in sense_id_set:
                errors.append(f"unknown distinguished sense {other} from {sense_id}")
            if other == sense_id:
                errors.append(f"sense candidate distinguishes itself: {sense_id}")
            elif other in sense_by_id and sense_id not in sense_by_id[other].get("distinguished_from", []):
                errors.append(f"non-reciprocal sense distinction: {sense_id} -> {other}")
        if sense.get("candidate_state") in {"AMBIGUOUS_CANDIDATE", "CONFLICTED_CANDIDATE"} and not distinguished:
            errors.append(f"ambiguous or conflicted sense lacks distinction: {sense_id}")
        for assertion in sense.get("aboutness_assertions", []):
            assertion_id = assertion.get("assertion_id", "")
            require_refs(assertion.get("evidence_refs", []), f"assertion {assertion_id}", semantic=True)
            conflicts = assertion.get("conflicts_with", [])
            for other in conflicts:
                if other not in assertion_id_set:
                    errors.append(f"unknown conflicting assertion {other} from {assertion_id}")
                if other == assertion_id:
                    errors.append(f"assertion conflicts with itself: {assertion_id}")
                elif other in assertion_by_id and assertion_id not in assertion_by_id[other].get("conflicts_with", []):
                    errors.append(f"non-reciprocal assertion conflict: {assertion_id} -> {other}")
            if assertion.get("candidate_state") == "CONFLICTED_CANDIDATE" and not conflicts:
                errors.append(f"conflicted assertion lacks conflict reference: {assertion_id}")

    abstention = record.get("abstention")
    if abstention:
        require_refs(abstention.get("evidence_refs", []), "abstention", semantic=False)

    if record.get("status") == "REVIEW_REQUIRED":
        states = {sense.get("candidate_state") for sense in senses}
        if not states.intersection({"AMBIGUOUS_CANDIDATE", "CONFLICTED_CANDIDATE"}):
            errors.append("review-required record lacks ambiguous or conflicted candidate")

    if errors:
        raise ValueError("; ".join(errors))


def validate_record(record: dict[str, Any], schema_validator) -> None:
    schema_validator.validate(record)
    validate_semantics(record)


def validate_fixtures(schema_validator) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    valid_results = []
    invalid_results = []
    for path in sorted(FIXTURE_DIR.glob("valid-*.json")):
        validate_record(read_json(path), schema_validator)
        valid_results.append({"fixture": path.name, "status": "PASSED"})
    for path in sorted(FIXTURE_DIR.glob("invalid-*.json")):
        try:
            validate_record(read_json(path), schema_validator)
        except Exception as exc:  # expected rejection is captured as evidence
            invalid_results.append(
                {"fixture": path.name, "status": "REJECTED_AS_EXPECTED", "error": str(exc)}
            )
        else:
            raise ValueError(f"invalid fixture unexpectedly passed: {path.name}")
    return valid_results, invalid_results


def write_outputs(
    decision: dict[str, Any],
    valid_results: list[dict[str, Any]],
    invalid_results: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fixtures = sorted(FIXTURE_DIR.glob("*.json"))
    report = {
        "schema": "sense-aboutness-contract-report/1",
        "status": "PASSED",
        "authority_effect": "TEST_SCHEMA_AND_BASELINE_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "baseline_commit": decision["baseline_commit"],
        "baseline_input_count": len(decision["baseline_inputs"]),
        "aboutness_facets": [
            "SUBJECT",
            "DOMAIN",
            "OPERATION",
            "QUALITY",
            "OBJECT",
            "PERIOD",
            "COMMUNITY",
            "REGISTER",
        ],
        "semantic_support_kinds": sorted(SEMANTIC_SUPPORT_KINDS),
        "valid_fixture_results": valid_results,
        "invalid_fixture_results": invalid_results,
        "boundary": "Passing proves contract shape and recorded invariants only. It does not prove a candidate meaning correct or authorize semantic generation, review acceptance, canon admission, ingestion, publication, or deployment.",
    }
    report_bytes = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    REPORT_PATH.write_bytes(report_bytes)
    receipt = {
        "schema": "sense-aboutness-contract-receipt/1",
        "status": "PASSED",
        "authority_effect": "TEST_SCHEMA_AND_BASELINE_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "validator_version": VALIDATOR_VERSION,
        "inputs": {
            "decision": {"bytes": DECISION_PATH.stat().st_size, "sha256": sha256_path(DECISION_PATH)},
            "schema": {"bytes": SCHEMA_PATH.stat().st_size, "sha256": sha256_path(SCHEMA_PATH)},
            "fixtures": {
                path.name: {"bytes": path.stat().st_size, "sha256": sha256_path(path)}
                for path in fixtures
            },
        },
        "output": {
            "relative_path": REPORT_PATH.name,
            "bytes": len(report_bytes),
            "sha256": sha256_bytes(report_bytes),
        },
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report, receipt


def main() -> int:
    decision = read_json(DECISION_PATH)
    validate_decision(decision)
    schema_validator = build_schema_validator(read_json(SCHEMA_PATH))
    valid_results, invalid_results = validate_fixtures(schema_validator)
    report, receipt = write_outputs(decision, valid_results, invalid_results)
    print(json.dumps({"report": report, "receipt": receipt}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
