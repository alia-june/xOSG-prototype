"""Map the source-linked parser ledger into aPROMPT 1.1 meaning documents.

The current English parser emits modal/imperative partial candidates, which
ground-boolean/1.0 cannot express. The adapter therefore preserves every
fragment as an unresolved statement and issue. It never creates axioms,
approvals, facts, prepared contracts, or executable expressions.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from importlib import resources
import json
import os
from pathlib import Path
import re
from uuid import uuid4
from zipfile import ZipFile

from jsonschema import Draft202012Validator

from validate_handoff_stub import validate as validate_legacy_ledger


ROOT = Path(__file__).resolve().parent
PROCESSOR = {"name": "natural-language-front-end", "version": "0.1.0"}
WHEEL = ROOT / "vendor" / "aprompt-1.1.0-py3-none-any.whl"
WHEEL_SHA256 = "9baccbad73341e47265e1321bfc9367aedce904f6fdc4ba8862af87010c68257"
CONTRACT_SHA256 = "3a2f88dc7a9730e5ed7a7c603050c8b31072d683957130d6a176952edb9702d3"
MAX_BATCH = 16  # aPROMPT 1.0 permits at most 16 sources per meaning document.
ENTRY_ID = re.compile(r"L([1-9][0-9]*)-S([1-9][0-9]*)")


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def verify_contract_runtime(contract: Path) -> dict:
    """Pin the supplied contract and installed admission code to the wheel."""
    if sha256(contract.read_bytes()).hexdigest() != CONTRACT_SHA256:
        raise ValueError("Sister-machine contract differs from the reviewed file")
    if sha256(WHEEL.read_bytes()).hexdigest() != WHEEL_SHA256:
        raise ValueError("aPROMPT wheel differs from the reviewed file")

    import aprompt

    if aprompt.__version__ != "1.1.0":
        raise ValueError("Installed aPROMPT version is not 1.1.0")
    installed = Path(aprompt.__file__).resolve().parent
    with ZipFile(WHEEL) as wheel:
        for member in wheel.namelist():
            if not member.startswith("aprompt/") or member.endswith("/"):
                continue
            if (installed / member.removeprefix("aprompt/")).read_bytes() != wheel.read(member):
                raise ValueError(f"Installed aPROMPT file differs from reviewed wheel: {member}")
    schema = json.loads(resources.files("aprompt").joinpath("contracts/meaning-v1.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    return schema


def _ids(entry: dict) -> tuple[str, str, str]:
    match = ENTRY_ID.fullmatch(entry["id"])
    if not match:
        raise ValueError(f"Unsupported legacy entry ID: {entry['id']!r}")
    suffix = f"L{match[1]}S{match[2]}"
    return f"Src{suffix}", f"Stmt{suffix}", f"Issue{suffix}"


def build_meaning(entries: list[dict]) -> dict:
    """Create one closed meaning document for 1..16 legacy entries."""
    if not 1 <= len(entries) <= MAX_BATCH:
        raise ValueError("A meaning batch must contain 1..16 entries")
    meaning = {"schema_version": "1.0", "processor": dict(PROCESSOR),
               "sources": [], "atoms": [], "statements": [], "issues": []}
    for entry in entries:
        source_id, statement_id, issue_id = _ids(entry)
        source_text = entry["source_text"]
        if not isinstance(source_text, str) or not 0 < len(source_text) <= 32768 or "\x00" in source_text:
            raise ValueError(f"Source text is empty, oversized, or contains NUL: {entry['id']}")
        ref = {"source_id": source_id, "start": 0, "end": len(source_text)}
        meaning["sources"].append({"id": source_id, "text": source_text,
                                   "sha256": sha256(source_text.encode("utf-8")).hexdigest()})
        meaning["statements"].append({"id": statement_id, "kind": "unresolved",
                                      "epistemic": "unknown", "expression": None,
                                      "source_refs": [ref], "derived_from": [], "adoption": None})
        if entry["logic_candidates"]:
            description = (f"Partial parser candidate {entry['id']} has modal or imperative meaning "
                           "outside ground-boolean/1.0. Review the legacy ledger; no executable expression was emitted.")
        else:
            description = (f"No supported complete logic translation for {entry['id']}. "
                           "The source fragment remains unresolved in the legacy ledger.")
        meaning["issues"].append({"id": issue_id, "kind": "unsupported",
                                  "description": description, "source_refs": [ref], "alternatives": []})
    return meaning


def validated_batches(ledger: dict, schema: dict) -> list[tuple[str, bytes, dict]]:
    """Use both the portable schema and Python admission for every batch."""
    from aprompt import decode_contract_json, validate_meaning

    entries = ledger["entries"]
    batches: list[tuple[str, bytes, dict]] = []
    for offset in range(0, len(entries), MAX_BATCH):
        group = entries[offset:offset + MAX_BATCH]
        meaning = build_meaning(group)
        Draft202012Validator(schema).validate(meaning)
        data = _json_bytes(meaning)
        decoded = decode_contract_json(data)
        if validate_meaning(decoded) != meaning:
            raise ValueError("aPROMPT admission changed a meaning document")
        name = f"meaning_{len(batches) + 1:04d}.json"
        batches.append((name, data, {"first_entry": group[0]["id"],
                                     "last_entry": group[-1]["id"], "entries": len(group)}))
    return batches


def publish_handoff(ledger_path: Path, archive: Path, contract: Path, output_dir: Path) -> dict:
    """Validate source and receiver contract, then publish a new directory."""
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError("Choose a new output directory; prior handoffs are never replaced")
    if not output_dir.parent.is_dir():
        raise FileNotFoundError(f"Output parent does not exist: {output_dir.parent}")
    schema = verify_contract_runtime(contract)
    checks = validate_legacy_ledger(archive, ROOT / "handoff_stub.schema.json", ledger_path)
    ledger_bytes = ledger_path.read_bytes()
    ledger = json.loads(ledger_bytes)
    batches = validated_batches(ledger, schema)
    if not batches:
        raise ValueError("Legacy ledger has no entries")
    stage = output_dir.with_name(output_dir.name + f".stage-{uuid4().hex}")
    stage.mkdir()
    documents = []
    try:
        for name, data, coverage in batches:
            target = stage / name
            with target.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            documents.append({"name": name, "sha256": sha256(data).hexdigest(), **coverage})
        manifest = {
            "manifest_version": "sister-handoff/0.1", "status": "unresolved_no_executable_rules",
            "execution_allowed": False, "accepted_by_sister_machine": False,
            "meaning_schema_version": "1.0", "compiler_limit": "ground-boolean/1.0",
            "source_archive_sha256": ledger["source"]["archive_sha256"].lower(),
            "source_member_path": ledger["source"]["member_path"],
            "source_member_sha256": ledger["source"]["member_sha256"].lower(),
            "legacy_ledger_sha256": sha256(ledger_bytes).hexdigest(),
            "wheel_sha256": WHEEL_SHA256, "contract_sha256": CONTRACT_SHA256,
            "validation": checks, "fragments": len(ledger["entries"]),
            "unresolved_statements": len(ledger["entries"]),
            "unsupported_issues": len(ledger["entries"]),
            "executable_statements": 0, "axioms_adopted": 0,
            "documents": documents,
        }
        manifest_data = _json_bytes(manifest)
        with (stage / "manifest.json").open("xb") as stream:
            stream.write(manifest_data)
            stream.flush()
            os.fsync(stream.fileno())
        from aprompt import decode_contract_json, validate_meaning
        for document in documents:
            written = (stage / document["name"]).read_bytes()
            if sha256(written).hexdigest() != document["sha256"]:
                raise ValueError(f"Staged meaning digest differs: {document['name']}")
            validate_meaning(decode_contract_json(written))
        if (stage / "manifest.json").read_bytes() != manifest_data:
            raise ValueError("Staged manifest differs from the validated manifest")
        if output_dir.exists():
            raise FileExistsError("Output directory appeared before publication")
        os.rename(stage, output_dir)
    except Exception:
        # Keep the stage so a failed publication can be diagnosed.
        raise
    return {"output_dir": str(output_dir), "manifest_sha256": sha256(manifest_data).hexdigest(),
            "documents": len(documents), "fragments": manifest["fragments"],
            "executable_statements": 0, "axioms_adopted": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=ROOT / "FRONTEND_FULL_PROMPT_CANDIDATES.json")
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--contract", type=Path, default=ROOT / "vendor" / "SISTERMACHINE_CONTRACT.md")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(publish_handoff(args.ledger, args.archive, args.contract, args.output_dir)))


if __name__ == "__main__":
    main()
