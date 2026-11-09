from __future__ import annotations

import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
INPUT_PATH = ROOT / "pilot" / "sense-aboutness" / "calibration" / "blank-dual-review-records.jsonl.gz"
INPUT_RECEIPT_PATH = ROOT / "pilot" / "sense-aboutness" / "calibration" / "SENSE_CALIBRATION_RECEIPT.json"
OUTPUT_DIR = ROOT / "pilot" / "sense-aboutness" / "review-packets"
MANIFEST_PATH = OUTPUT_DIR / "SENSE_REVIEW_PACKET_MANIFEST.json"
SLOTS = ("reviewer_a", "reviewer_b")

_SPEC = importlib.util.spec_from_file_location(
    "validate_sense_calibration_review", ROOT / "validate_sense_calibration_review.py"
)
assert _SPEC and _SPEC.loader
_VALIDATOR = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_VALIDATOR)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_records() -> list[dict[str, Any]]:
    return _VALIDATOR.load_jsonl(INPUT_PATH)


def packet_record(record: dict[str, Any], slot: str) -> dict[str, Any]:
    return {
        "schema": "sense-aboutness-reviewer-packet-record/1",
        "reviewer_slot": slot,
        "calibration_id": record["calibration_id"],
        "source_sample_id": record["source_sample_id"],
        "normalized_term": record["normalized_term"],
        "selection": record["selection"],
        "historical_evidence": record["historical_evidence"],
        "modern_shape_evidence": record["modern_shape_evidence"],
        "normalization_evidence": record["normalization_evidence"],
        "unresolved_shape_evidence": record["unresolved_shape_evidence"],
        "review": record[slot],
        "authority_effect": "BLANK_INDEPENDENT_REVIEW_PACKET_ONLY",
    }


def encode_records(records: list[dict[str, Any]]) -> bytes:
    raw = "".join(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n" for record in records).encode("utf-8")
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as stream:
        stream.write(raw)
    return buffer.getvalue()


def build() -> dict[str, Any]:
    records = load_records()
    _VALIDATOR.validate_records(records)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for slot in SLOTS:
        packet = [packet_record(record, slot) for record in records]
        compressed = encode_records(packet)
        path = OUTPUT_DIR / f"{slot}-packet.jsonl.gz"
        path.write_bytes(compressed)
        outputs[slot] = {
            "relative_path": path.name,
            "record_count": len(packet),
            "bytes": len(compressed),
            "sha256": sha256_bytes(compressed),
        }
    manifest = {
        "schema": "sense-aboutness-review-packet-manifest/1",
        "status": "GENERATED_BLANK_INDEPENDENT_PACKETS",
        "authority_effect": "TEST_BLANK_INDEPENDENT_REVIEW_PACKETS_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "input": {
            "relative_path": str(INPUT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "bytes": INPUT_PATH.stat().st_size,
            "sha256": sha256_bytes(INPUT_PATH.read_bytes()),
            "receipt_sha256": sha256_bytes(INPUT_RECEIPT_PATH.read_bytes()),
        },
        "outputs": outputs,
        "boundary": "Each packet contains one blank reviewer slot and the same source-bearing evidence. Cross-reviewer judgments and adjudication are excluded.",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True))
