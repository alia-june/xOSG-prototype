"""Deterministic controlled-English to aPROMPT ground Boolean meaning.

Accepted sentence forms (one per nonblank line):
  entity is property.
  entity is not property.
  entity is property and entity is property.
  entity is property or entity is property.
  If entity is property, then entity is property.

`entity` and `property` are lowercase ASCII identifiers. `is` maps to the
project-local predicate has_property(entity, property). `If` is material
implication, as defined by aPROMPT 1.1. Unsupported lines remain unresolved.
No source sentence becomes an axiom or authority to execute.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from uuid import uuid4

from jsonschema import Draft202012Validator

from sister_adapter import ROOT, _json_bytes, verify_contract_runtime


NAME = r"[a-z][a-z0-9_]*"
ATOM = re.compile(rf"(?P<entity>{NAME}) is (?P<negation>not )?(?P<property>{NAME})")
CONDITIONAL = re.compile(r"If (.+), then (.+)")


class AtomTable:
    def __init__(self) -> None:
        self._ids: dict[tuple[str, str], str] = {}
        self.atoms: list[dict] = []

    def expression(self, sentence: str) -> dict | None:
        match = ATOM.fullmatch(sentence)
        if match is None:
            return None
        key = match["entity"], match["property"]
        if key not in self._ids:
            identifier = f"A{len(self.atoms) + 1}"
            self._ids[key] = identifier
            self.atoms.append({"id": identifier, "predicate": "has_property",
                               "arguments": [{"type": "string", "value": key[0]},
                                             {"type": "string", "value": key[1]}]})
        expression = {"op": "atom", "id": self._ids[key]}
        return {"op": "not", "arg": expression} if match["negation"] else expression


def parse_expression(sentence: str, atoms: AtomTable) -> dict | None:
    if not sentence.endswith(".") or sentence.count(".") != 1:
        return None
    body = sentence[:-1]
    conditional = CONDITIONAL.fullmatch(body)
    if conditional:
        if not ATOM.fullmatch(conditional[1]) or not ATOM.fullmatch(conditional[2]):
            return None
        return {"op": "implies", "left": atoms.expression(conditional[1]),
                "right": atoms.expression(conditional[2])}
    for conjunction, op in ((" and ", "all"), (" or ", "any")):
        if conjunction in body:
            parts = body.split(conjunction)
            if len(parts) != 2 or not all(ATOM.fullmatch(part) for part in parts):
                return None
            return {"op": op, "args": [atoms.expression(part) for part in parts]}
    return atoms.expression(body)


def build_meaning(text: str) -> dict:
    """Preserve exact source text and Unicode code-point offsets."""
    if not text or len(text) > 32768 or "\x00" in text:
        raise ValueError("Controlled source must be 1..32768 code points without NUL")
    meaning = {"schema_version": "1.0", "processor": {"name": "controlled-boolean-front-end", "version": "0.1.0"},
               "sources": [{"id": "Text1", "text": text, "sha256": sha256(text.encode("utf-8")).hexdigest()}],
               "atoms": [], "statements": [], "issues": []}
    atoms = AtomTable()
    offset = 0
    for raw_line in text.splitlines(keepends=True):
        content = raw_line.rstrip("\r\n")
        sentence = content.strip()
        if sentence:
            if len(meaning["statements"]) >= 128:
                raise ValueError("Controlled input exceeds 128 nonblank sentences")
            leading = len(content) - len(content.lstrip())
            start = offset + leading
            ref = {"source_id": "Text1", "start": start, "end": start + len(sentence)}
            expression = parse_expression(sentence, atoms)
            number = len(meaning["statements"]) + 1
            statement = {"id": f"Stmt{number}", "kind": "assertion" if expression else "unresolved",
                         "epistemic": "supplied" if expression else "unknown", "expression": expression,
                         "source_refs": [ref], "derived_from": [], "adoption": None}
            meaning["statements"].append(statement)
            if expression is None:
                if len(meaning["issues"]) >= 64:
                    raise ValueError("Controlled input exceeds 64 unsupported sentences")
                meaning["issues"].append({"id": f"Issue{number}", "kind": "unsupported",
                                          "description": "Sentence is outside the documented controlled Boolean grammar.",
                                          "source_refs": [ref], "alternatives": []})
        offset += len(raw_line)
    if not meaning["statements"]:
        raise ValueError("Controlled input has no nonblank sentences")
    meaning["atoms"] = atoms.atoms
    return meaning


def validate_meaning_document(meaning: dict, contract: Path) -> bytes:
    from aprompt import decode_contract_json, validate_meaning

    schema = verify_contract_runtime(contract)
    Draft202012Validator(schema).validate(meaning)
    data = _json_bytes(meaning)
    if validate_meaning(decode_contract_json(data)) != meaning:
        raise ValueError("aPROMPT admission changed the controlled meaning")
    return data


def publish_meaning(input_path: Path, output_path: Path, contract: Path) -> dict:
    if output_path.exists() or output_path.is_symlink():
        raise FileExistsError("Choose a new output file; existing meaning documents are never replaced")
    raw = input_path.read_bytes()
    if len(raw) > 256 * 1024:
        raise ValueError("Input exceeds the aPROMPT ingress byte bound")
    text = raw.decode("utf-8")
    meaning = build_meaning(text)
    data = validate_meaning_document(meaning, contract)
    stage = output_path.with_name(output_path.name + f".stage-{uuid4().hex}")
    with stage.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    from aprompt import decode_contract_json, validate_meaning
    if validate_meaning(decode_contract_json(stage.read_bytes())) != meaning:
        raise ValueError(f"Staged meaning failed readback at {stage}")
    os.link(stage, output_path)
    stage.unlink()
    return {"output": str(output_path), "sha256": sha256(data).hexdigest(),
            "statements": len(meaning["statements"]), "atoms": len(meaning["atoms"]),
            "issues": len(meaning["issues"]), "axioms_adopted": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contract", type=Path, default=ROOT / "vendor" / "SISTERMACHINE_CONTRACT.md")
    args = parser.parse_args()
    print(json.dumps(publish_meaning(args.input, args.output, args.contract)))


if __name__ == "__main__":
    main()
