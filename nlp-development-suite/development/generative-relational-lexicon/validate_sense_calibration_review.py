from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RECORDS_PATH = ROOT / "pilot" / "sense-aboutness" / "calibration" / "blank-dual-review-records.jsonl.gz"
SOURCE_RECORDS_PATH = ROOT / "pilot" / "sense-aboutness" / "review-sample" / "blank-review-records.jsonl.gz"
REVIEW_FIELDS = (
    "reviewer_id",
    "reviewed_at",
    "review_status",
    "sense_candidates",
    "aboutness_assertions",
    "abstention",
    "review_notes",
)
REVIEW_STATUSES = {
    "SUPPORTED_CANDIDATE",
    "MULTIPLE_CANDIDATES",
    "ABSTAINED",
    "PARSER_OR_SOURCE_ISSUE",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream]


def validate_source_identity(records: list[dict[str, Any]]) -> None:
    source_records = {record["sample_id"]: record for record in load_jsonl(SOURCE_RECORDS_PATH)}
    seen_ids: set[str] = set()
    seen_sources: set[str] = set()
    for record in records:
        calibration_id = record.get("calibration_id")
        source_id = record.get("source_sample_id")
        if not isinstance(calibration_id, str) or calibration_id in seen_ids:
            raise ValueError("calibration IDs must be present and unique")
        if not isinstance(source_id, str) or source_id in seen_sources:
            raise ValueError("source sample IDs must be present and unique")
        if source_id not in source_records:
            raise ValueError(f"source sample is not in the frozen package: {source_id}")
        source = source_records[source_id]
        for field in (
            "normalized_term",
            "selection",
            "historical_evidence",
            "modern_shape_evidence",
            "normalization_evidence",
            "unresolved_shape_evidence",
        ):
            if record.get(field) != source.get(field):
                raise ValueError(f"source evidence changed for {source_id}: {field}")
        seen_ids.add(calibration_id)
        seen_sources.add(source_id)


def validate_review_copy(review: Any, *, require_reviewed: bool) -> bool:
    if not isinstance(review, dict) or set(review) != set(REVIEW_FIELDS):
        raise ValueError("review copy fields do not match the protocol")
    blank = all(value is None for value in review.values())
    if blank:
        if require_reviewed:
            raise ValueError("review is required but a reviewer copy is still blank")
        return False
    if not isinstance(review["reviewer_id"], str) or not review["reviewer_id"].strip():
        raise ValueError("reviewer_id is required")
    if not isinstance(review["reviewed_at"], str) or not review["reviewed_at"].strip():
        raise ValueError("reviewed_at is required")
    status = review["review_status"]
    if status not in REVIEW_STATUSES:
        raise ValueError(f"unsupported review status: {status!r}")
    if not isinstance(review["review_notes"], str) or not review["review_notes"].strip():
        raise ValueError("review_notes are required")
    if status in {"SUPPORTED_CANDIDATE", "MULTIPLE_CANDIDATES"}:
        if not isinstance(review["sense_candidates"], list) or not review["sense_candidates"]:
            raise ValueError("candidate status requires sense_candidates")
        if not isinstance(review["aboutness_assertions"], list) or not review["aboutness_assertions"]:
            raise ValueError("candidate status requires aboutness_assertions")
        if review["abstention"] is not None:
            raise ValueError("candidate status cannot carry abstention")
    elif status == "ABSTAINED":
        if not isinstance(review["abstention"], dict):
            raise ValueError("ABSTAINED requires an abstention object")
        if review["sense_candidates"] not in (None, []):
            raise ValueError("ABSTAINED cannot carry sense_candidates")
    else:
        if not isinstance(review["sense_candidates"], (type(None), list)):
            raise ValueError("parser/source issue has malformed sense_candidates")
    return True


def validate_records(records: list[dict[str, Any]], *, require_reviewed: bool = False) -> dict[str, Any]:
    if not records:
        raise ValueError("review package is empty")
    validate_source_identity(records)
    reviewed = 0
    for record in records:
        if record.get("schema") != "sense-aboutness-dual-review-record/1":
            raise ValueError("unexpected review record schema")
        if record.get("authority_effect") != "BLANK_DUAL_REVIEW_ONLY":
            raise ValueError("review package authority effect changed")
        if validate_review_copy(record.get("reviewer_a"), require_reviewed=require_reviewed):
            reviewed += 1
        if validate_review_copy(record.get("reviewer_b"), require_reviewed=require_reviewed):
            reviewed += 1
        adjudication = record.get("adjudication")
        if not isinstance(adjudication, dict) or set(adjudication) != {
            "status", "reviewer_a_preserved", "reviewer_b_preserved", "agreement_category", "notes"
        }:
            raise ValueError("adjudication fields do not match the protocol")
        if all(value is None for value in adjudication.values()) and require_reviewed:
            raise ValueError("reviewed package requires an adjudication record")
    expected = len(records) * 2
    return {
        "schema": "sense-aboutness-review-validation/1",
        "status": "REVIEWED_VALIDATED" if reviewed == expected else "BLANK_NOT_REVIEWED",
        "record_count": len(records),
        "review_copy_count": expected,
        "completed_review_copy_count": reviewed,
        "require_reviewed": require_reviewed,
        "authority_effect": "TEST_REVIEW_VALIDATION_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate sense-aboutness review intake without assigning semantics.")
    parser.add_argument("--input", type=Path, default=RECORDS_PATH)
    parser.add_argument("--require-reviewed", action="store_true")
    args = parser.parse_args()
    result = validate_records(load_jsonl(args.input), require_reviewed=args.require_reviewed)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
