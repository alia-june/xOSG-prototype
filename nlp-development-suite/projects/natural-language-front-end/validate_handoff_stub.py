"""Validate the provisional sister-machine handoff and its source pointers."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from source_archive import load_archive_member


ROOT = Path(__file__).resolve().parent


def validate(archive: Path, schema_path: Path, example_path: Path) -> dict[str, object]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    example = json.loads(example_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(example)

    archive_bytes, member_data = load_archive_member(archive, example["source"]["member_path"])
    actual_archive_hash = sha256(archive_bytes).hexdigest()
    if actual_archive_hash.lower() != example["source"]["archive_sha256"].lower():
        raise ValueError("Archive SHA-256 does not match handoff source record")

    actual_member_hash = sha256(member_data).hexdigest()
    if actual_member_hash.lower() != example["source"]["member_sha256"].lower():
        raise ValueError("Prompt member SHA-256 does not match handoff source record")

    lines = member_data.decode("utf-8-sig").splitlines()
    seen_ids: set[str] = set()
    for entry in example["entries"]:
        if entry["id"] in seen_ids:
            raise ValueError(f"Duplicate entry ID: {entry['id']}")
        seen_ids.add(entry["id"])
        span = entry["source_span"]
        start, end = span["start_line"], span["end_line"]
        if start > end or end > len(lines):
            raise ValueError(f"Invalid source span: {entry['id']}")
        if entry["source_text"] not in "\n".join(lines[start - 1:end]):
            raise ValueError(f"Source text is absent from declared span: {entry['id']}")

    return {"schema_valid": True, "example_valid": True,
            "source_hashes_valid": True, "source_quotes_valid": len(example["entries"])}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--schema", type=Path, default=ROOT / "handoff_stub.schema.json")
    parser.add_argument("--example", type=Path, default=ROOT / "handoff_stub.example.json")
    args = parser.parse_args()
    print(json.dumps(validate(args.archive, args.schema, args.example)))


if __name__ == "__main__":
    main()
