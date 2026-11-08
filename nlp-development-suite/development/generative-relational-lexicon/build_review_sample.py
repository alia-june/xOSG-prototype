from __future__ import annotations

from collections import Counter, defaultdict
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

import audit_unresolved_shapes as unresolved_audit
import compare_roget_oewn as baseline


ROOT = Path(__file__).resolve().parent
DECISION_PATH = ROOT / "REVIEW_SAMPLE_DECISION.json"
UNRESOLVED_RECEIPT_PATH = ROOT / "pilot" / "modern-comparison" / "normalization-audit" / "unresolved-shapes" / "UNRESOLVED_SHAPE_AUDIT_RECEIPT.json"
SOURCE_PATH = ROOT / "pilot" / "tier-zero" / "raw" / "project-gutenberg-ebook-22.txt"
OUTPUT_DIR = ROOT / "pilot" / "modern-comparison" / "normalization-audit" / "review-sample"
RECORDS_PATH = OUTPUT_DIR / "review-sample-records.jsonl.gz"
REPORT_JSON_PATH = OUTPUT_DIR / "REVIEW_SAMPLE_REPORT.json"
REPORT_MD_PATH = OUTPUT_DIR / "REVIEW_SAMPLE_REPORT.md"
RECEIPT_PATH = OUTPUT_DIR / "REVIEW_SAMPLE_RECEIPT.json"
BUILDER_VERSION = "unresolved-review-sample/1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_decision(decision: dict[str, object]) -> dict[str, object]:
    if decision.get("status") != "AUTHORIZED_TEST_REVIEW_SAMPLE":
        raise ValueError("review sample is not authorized")
    if decision.get("authority_effect") != "TEST_REVIEW_SAMPLE_ONLY":
        raise ValueError("review sample authority must remain test-only")
    for field in (
        "production_ready",
        "publication_allowed",
        "canon_admission",
        "review_disposition_assignment_allowed",
    ):
        if decision.get(field) is not False:
            raise ValueError(f"review sample boundary changed: {field}")
    pin = decision.get("unresolved_shape_receipt")
    if not isinstance(pin, dict):
        raise ValueError("unresolved-shape receipt pin is missing")
    if UNRESOLVED_RECEIPT_PATH.stat().st_size != pin.get("bytes"):
        raise ValueError("unresolved-shape receipt byte count changed")
    if sha256_path(UNRESOLVED_RECEIPT_PATH) != pin.get("sha256"):
        raise ValueError("unresolved-shape receipt SHA-256 changed")
    receipt = json.loads(UNRESOLVED_RECEIPT_PATH.read_text(encoding="utf-8"))
    if receipt.get("status") != "PASSED":
        raise ValueError("unresolved-shape audit is not passed")
    for output in receipt.get("outputs", {}).values():
        path = UNRESOLVED_RECEIPT_PATH.parent / output["relative_path"]
        if sha256_path(path) != output["sha256"]:
            raise ValueError(f"unresolved-shape output changed: {path.name}")
    return receipt


def load_unresolved_records() -> list[dict[str, object]]:
    records = []
    path = UNRESOLVED_RECEIPT_PATH.parent / "unresolved-shape-records.jsonl.gz"
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            records.append(json.loads(line))
    if not records:
        raise ValueError("unresolved shape record set is empty")
    return records


def pos_signature(record: dict[str, object]) -> str:
    markers = record.get("historical_pos_markers", [])
    return "+".join(markers) or "NONE"


def choose_sample(records: list[dict[str, object]], source_sha256: str, maximum: int) -> list[dict[str, object]]:
    strata: dict[tuple[str, str], list[tuple[str, dict[str, object]]]] = defaultdict(list)
    for record in records:
        stratum = (record["primary_shape"], pos_signature(record))
        material = "|".join((source_sha256, record["historical_term"], stratum[0], stratum[1])).encode("utf-8")
        rank = hashlib.sha256(material).hexdigest()
        strata[stratum].append((rank, record))
    selected = []
    for stratum in sorted(strata):
        for rank, record in sorted(strata[stratum], key=lambda item: (item[0], item[1]["historical_term"]))[:maximum]:
            selected.append((stratum, rank, record))
    return [record | {"selection_rank": rank} for _stratum, rank, record in sorted(selected, key=lambda item: (item[0], item[1], item[2]["historical_term"]))]


def attach_raw_blocks(record: dict[str, object], lines: list[str]) -> dict[str, object]:
    blocks = []
    for start, end in record["source_line_spans"]:
        if start < 1 or end < start or end > len(lines):
            raise ValueError(f"invalid raw source span for {record['historical_term']}: {start}-{end}")
        blocks.append(
            {
                "source_line_start": start,
                "source_line_end": end,
                "text": "\n".join(lines[start - 1:end]),
            }
        )
    return record | {
        "raw_source_blocks": blocks,
        "raw_source_sha256": sha256_path(SOURCE_PATH),
        "review_disposition": None,
        "review_notes": None,
    }


def build_report(records: list[dict[str, object]], source_sha256: str) -> dict[str, object]:
    strata = Counter((record["primary_shape"], pos_signature(record)) for record in records)
    return {
        "schema": "unresolved-review-sample-report/1",
        "status": "GENERATED_TEST_REVIEW_SAMPLE",
        "authority_effect": "TEST_REVIEW_SAMPLE_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "review_disposition_assignment_allowed": False,
        "sample_record_count": len(records),
        "stratum_count": len(strata),
        "sample_counts_by_shape": dict(sorted(Counter(record["primary_shape"] for record in records).items())),
        "sample_counts_by_stratum": [
            {"shape": shape, "pos_signature": pos, "count": count}
            for (shape, pos), count in sorted(strata.items())
        ],
        "source_sha256": source_sha256,
        "raw_blocks_attached": sum(len(record["raw_source_blocks"]) for record in records),
        "selection_boundary": "The sample is a deterministic review proposal; it does not decide lexical validity, parser correctness, source meaning, or canon.",
    }


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Unresolved candidate review sample",
        "",
        "Status: deterministic internal review proposal; no disposition has been assigned.",
        "",
        f"- Sample records: {report['sample_record_count']}",
        f"- Shape/POS strata represented: {report['stratum_count']}",
        f"- Raw source blocks attached: {report['raw_blocks_attached']}",
        f"- Raw source SHA-256: `{report['source_sha256']}`",
        "",
        "## Sample counts by shape",
        "",
        "| Shape | Records |",
        "|---|---:|",
    ]
    for shape, count in report["sample_counts_by_shape"].items():
        lines.append(f"| `{shape}` | {count} |")
    lines.extend(
        [
            "",
            "## Review boundary",
            "",
            report["selection_boundary"],
            "Raw source text is attached for inspection only. The fields `review_disposition` and `review_notes` are intentionally null.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(records: list[dict[str, object]], report: dict[str, object], unresolved_receipt: dict[str, object], source_sha256: str) -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = "".join(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n" for record in records).encode("utf-8")
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as stream:
        stream.write(raw)
    compressed = buffer.getvalue()
    RECORDS_PATH.write_bytes(compressed)
    report_bytes = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    REPORT_JSON_PATH.write_bytes(report_bytes)
    markdown_bytes = render_markdown(report).encode("utf-8")
    REPORT_MD_PATH.write_bytes(markdown_bytes)
    receipt = {
        "schema": "unresolved-review-sample-receipt/1",
        "status": "PASSED",
        "authority_effect": "TEST_REVIEW_SAMPLE_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "builder_version": BUILDER_VERSION,
        "inputs": {
            "decision": {"sha256": sha256_path(DECISION_PATH)},
            "unresolved_shape_receipt": {"sha256": sha256_path(UNRESOLVED_RECEIPT_PATH)},
            "unresolved_shape_records": unresolved_receipt["outputs"]["records"],
            "source": {"relative_path": str(SOURCE_PATH.relative_to(ROOT)), "bytes": SOURCE_PATH.stat().st_size, "sha256": source_sha256},
        },
        "outputs": {
            "records": {"relative_path": RECORDS_PATH.name, "record_count": len(records), "bytes": len(compressed), "uncompressed_bytes": len(raw), "sha256": sha256_bytes(compressed)},
            "report_json": {"relative_path": REPORT_JSON_PATH.name, "bytes": len(report_bytes), "sha256": sha256_bytes(report_bytes)},
            "report_markdown": {"relative_path": REPORT_MD_PATH.name, "bytes": len(markdown_bytes), "sha256": sha256_bytes(markdown_bytes)},
        },
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return receipt


def main() -> int:
    decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
    unresolved_receipt = validate_decision(decision)
    records = load_unresolved_records()
    source_sha256 = sha256_path(SOURCE_PATH)
    expected_source_sha256 = unresolved_receipt["inputs"]["historical_memberships"]["source_sha256"]
    if source_sha256 != expected_source_sha256:
        raise ValueError("raw Roget source SHA-256 differs from pinned source")
    sample = choose_sample(records, source_sha256, int(decision["source_sample_rule"]["maximum_per_stratum"]))
    lines = SOURCE_PATH.read_text(encoding="utf-8").splitlines()
    sample = [attach_raw_blocks(record, lines) for record in sample]
    report = build_report(sample, source_sha256)
    receipt = write_outputs(sample, report, unresolved_receipt, source_sha256)
    print(json.dumps({"receipt": receipt, "summary": report}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
