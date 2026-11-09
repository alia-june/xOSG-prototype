from __future__ import annotations

from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DECISION_PATH = ROOT / "SENSE_CALIBRATION_DECISION.json"
BLANK_RECEIPT_PATH = ROOT / "pilot" / "sense-aboutness" / "review-sample" / "SENSE_REVIEW_SAMPLE_RECEIPT.json"
BLANK_RECORDS_PATH = ROOT / "pilot" / "sense-aboutness" / "review-sample" / "blank-review-records.jsonl.gz"
OUTPUT_DIR = ROOT / "pilot" / "sense-aboutness" / "calibration"
RECORDS_PATH = OUTPUT_DIR / "blank-dual-review-records.jsonl.gz"
REPORT_PATH = OUTPUT_DIR / "SENSE_CALIBRATION_REPORT.json"
REPORT_MD_PATH = OUTPUT_DIR / "SENSE_CALIBRATION_REPORT.md"
RECEIPT_PATH = OUTPUT_DIR / "SENSE_CALIBRATION_RECEIPT.json"
BUILDER_VERSION = "sense-aboutness-calibration/1"
DIMENSIONS = (
    "match_layer",
    "historical_head_bucket",
    "historical_pos_signature",
    "source_label_bucket",
    "modern_sense_count_bucket",
    "modern_surface_collision_bucket",
    "unresolved_primary_shape",
)
NULL_REVIEW_FIELDS = (
    "reviewer_id",
    "reviewed_at",
    "review_status",
    "sense_candidates",
    "aboutness_assertions",
    "abstention",
    "review_notes",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def validate_decision(decision: dict[str, Any]) -> None:
    if decision.get("status") != "AUTHORIZED_TEST_BLANK_DUAL_REVIEW_CALIBRATION":
        raise ValueError("calibration decision is not authorized")
    if decision.get("authority_effect") != "TEST_BLANK_DUAL_REVIEW_CALIBRATION_ONLY":
        raise ValueError("calibration authority effect changed")
    for field in ("production_ready", "publication_allowed", "canon_admission", "review_judgment_assignment_allowed"):
        if decision.get(field) is not False:
            raise ValueError(f"calibration boundary changed: {field}")
    pin = decision["blank_sample_receipt"]
    if BLANK_RECEIPT_PATH.stat().st_size != pin["bytes"] or sha256_path(BLANK_RECEIPT_PATH) != pin["sha256"]:
        raise ValueError("blank sample receipt pin changed")
    if read_json(BLANK_RECEIPT_PATH).get("status") != "PASSED":
        raise ValueError("blank sample receipt is not passed")
    if tuple(decision["required_null_fields"]) != NULL_REVIEW_FIELDS:
        raise ValueError("calibration null-field contract changed")


def load_records() -> list[dict[str, Any]]:
    records = []
    with gzip.open(BLANK_RECORDS_PATH, "rt", encoding="utf-8") as stream:
        for line in stream:
            records.append(json.loads(line))
    if len(records) != 853:
        raise ValueError(f"expected 853 blank records, found {len(records)}")
    return records


def atoms(record: dict[str, Any]) -> set[tuple[str, str]]:
    stratum = record["selection"]["stratum"]
    return {(dimension, stratum[dimension]) for dimension in DIMENSIONS}


def choose(records: list[dict[str, Any]], target: int) -> tuple[list[dict[str, Any]], set[tuple[str, str]]]:
    remaining = {atom for record in records for atom in atoms(record)}
    pool = records[:]
    selected: list[dict[str, Any]] = []
    while remaining and len(selected) < target:
        ranked = []
        for record in pool:
            gain = len(atoms(record) & remaining)
            ranked.append((-gain, record["selection"]["selection_rank"], record["normalized_term"], record))
        if not ranked:
            break
        chosen = min(ranked, key=lambda item: item[:3])[-1]
        selected.append(chosen)
        remaining -= atoms(chosen)
        pool.remove(chosen)
    if remaining:
        raise ValueError(f"calibration target leaves uncovered atoms: {sorted(remaining)}")
    selected.sort(key=lambda record: record["selection"]["selection_rank"])
    return selected, remaining


def blank_copy() -> dict[str, Any]:
    return {field: None for field in NULL_REVIEW_FIELDS}


def build_records(selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for index, source in enumerate(selected, 1):
        records.append(
            {
                "schema": "sense-aboutness-dual-review-record/1",
                "calibration_id": f"sense-calibration-{index:02d}",
                "source_sample_id": source["sample_id"],
                "normalized_term": source["normalized_term"],
                "selection": source["selection"],
                "historical_evidence": source["historical_evidence"],
                "modern_shape_evidence": source["modern_shape_evidence"],
                "normalization_evidence": source["normalization_evidence"],
                "unresolved_shape_evidence": source["unresolved_shape_evidence"],
                "reviewer_a": blank_copy(),
                "reviewer_b": blank_copy(),
                "adjudication": {
                    "status": None,
                    "reviewer_a_preserved": None,
                    "reviewer_b_preserved": None,
                    "agreement_category": None,
                    "notes": None,
                },
                "authority_effect": "BLANK_DUAL_REVIEW_ONLY",
            }
        )
    return records


def build_report(decision: dict[str, Any], records: list[dict[str, Any]], population: int) -> dict[str, Any]:
    covered = {atom for record in records for atom in atoms(record)}
    expected = decision["selection_rule"]["expected_coverage_atom_count"]
    return {
        "schema": "sense-aboutness-calibration-report/1",
        "status": "GENERATED_BLANK_DUAL_REVIEW_CALIBRATION",
        "authority_effect": "TEST_BLANK_DUAL_REVIEW_CALIBRATION_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "population_record_count": population,
        "calibration_record_count": len(records),
        "coverage_atom_count": len(covered),
        "expected_coverage_atom_count": expected,
        "uncovered_atom_count": expected - len(covered),
        "reviewer_copy_count": 2,
        "reviewer_null_field_count": len(records) * 2 * len(NULL_REVIEW_FIELDS),
        "adjudication_field_count": len(records) * 5,
        "coverage_by_dimension": {
            dimension: sorted({record["selection"]["stratum"][dimension] for record in records})
            for dimension in DIMENSIONS
        },
        "boundary": "This package presents identical source-bearing records to two future independent reviewers. It contains no reviewer judgment, adjudication, semantic candidate, definition, or canon admission.",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Blank sense-aboutness dual-review calibration",
        "",
        "Status: generated internal calibration worksheet; no review judgment assigned.",
        "",
        f"- Population: {report['population_record_count']}",
        f"- Calibration records: {report['calibration_record_count']}",
        f"- Coverage atoms: {report['coverage_atom_count']}",
        f"- Uncovered atoms: {report['uncovered_atom_count']}",
        "- Independent copies: reviewer A and reviewer B",
        "",
        "Every reviewer and adjudication field is null. Preserve both independent copies before any adjudication.",
    ]
    return "\n".join(lines) + "\n"


def write_outputs(decision: dict[str, Any], records: list[dict[str, Any]], report: dict[str, Any]) -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = "".join(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n" for record in records).encode("utf-8")
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as stream:
        stream.write(raw)
    compressed = buffer.getvalue()
    RECORDS_PATH.write_bytes(compressed)
    report_bytes = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    REPORT_PATH.write_bytes(report_bytes)
    markdown_bytes = render_markdown(report).encode("utf-8")
    REPORT_MD_PATH.write_bytes(markdown_bytes)
    receipt = {
        "schema": "sense-aboutness-calibration-receipt/1",
        "status": "PASSED",
        "authority_effect": "TEST_BLANK_DUAL_REVIEW_CALIBRATION_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "builder_version": BUILDER_VERSION,
        "inputs": {
            "decision": {"bytes": DECISION_PATH.stat().st_size, "sha256": sha256_path(DECISION_PATH)},
            "blank_sample_receipt": {"bytes": BLANK_RECEIPT_PATH.stat().st_size, "sha256": sha256_path(BLANK_RECEIPT_PATH)},
            "blank_sample_records": {"bytes": BLANK_RECORDS_PATH.stat().st_size, "sha256": sha256_path(BLANK_RECORDS_PATH)},
        },
        "outputs": {
            "records": {"relative_path": RECORDS_PATH.name, "record_count": len(records), "bytes": len(compressed), "uncompressed_bytes": len(raw), "sha256": sha256_bytes(compressed)},
            "report_json": {"relative_path": REPORT_PATH.name, "bytes": len(report_bytes), "sha256": sha256_bytes(report_bytes)},
            "report_markdown": {"relative_path": REPORT_MD_PATH.name, "bytes": len(markdown_bytes), "sha256": sha256_bytes(markdown_bytes)},
        },
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return receipt


def main() -> int:
    decision = read_json(DECISION_PATH)
    validate_decision(decision)
    source_records = load_records()
    selected, uncovered = choose(source_records, int(decision["selection_rule"]["target_record_count"]))
    if uncovered:
        raise ValueError("calibration coverage is incomplete")
    records = build_records(selected)
    report = build_report(decision, records, len(source_records))
    receipt = write_outputs(decision, records, report)
    print(json.dumps({"receipt": receipt, "summary": report}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
