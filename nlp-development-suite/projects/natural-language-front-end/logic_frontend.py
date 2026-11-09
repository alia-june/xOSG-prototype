"""Conservative, deterministic English-to-logic candidate extractor.

This is a source-linked front end, not an authority or execution engine. It
recognizes a deliberately small set of clause forms and records everything
else as unparsed. Its JSON envelope follows handoff-stub/0.1 until the sister
machine supplies its actual contract.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from typing import Any
from uuid import uuid4

from source_archive import load_archive_member
from wordnet_lexicon import WordNetLexicon, WORDNET_RELEASE


ROOT = Path(__file__).resolve().parent
DEFAULT_MEMBER = (
    "synthetic_os_project_redux_2026-09-16/snapshot/"
    "llm_prompt_hardening_modular_kit_v1_6_candidate/builds/full_prompt.md"
)
WORD = r"[A-Za-z][A-Za-z'-]*"
NOUN_PHRASE = r"[A-Za-z][A-Za-z' -]*"
COMPLEX_SCOPE = re.compile(r"\b(?:and|or|if|unless|except|before|after|when|while|without|because|which|that)\b|[;:]", re.I)
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
LIST_PREFIX = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
IMPERATIVE_VERBS = frozenset({
    "apply", "define", "emit", "freeze", "identify", "keep", "label", "mark",
    "preserve", "record", "reject", "report", "require", "select", "state",
    "stop", "use", "verify", "write",
})


def _plain_clause(source_text: str) -> str:
    clause = LIST_PREFIX.sub("", source_text.strip())
    return clause[:-1].strip() if clause.endswith(".") else clause


def _candidate(clause: str) -> tuple[str, dict[str, Any], list[str]] | None:
    """Parse only complete, single clauses with explicit surface markers."""
    if not clause or any(c in clause for c in ".?!`\n"):
        return None

    match = re.fullmatch(
        rf"If (?:the )?(?P<subject>{NOUN_PHRASE}) is (?P<property>{WORD}), "
        rf"do not (?P<verb>{WORD})(?: (?P<object>{NOUN_PHRASE}))?",
        clause, re.I,
    )
    if match:
        parts = match.groupdict()
        ast = {
            "op": "implies",
            "condition": {"op": "has_property", "subject_text": parts["subject"], "property_text": parts["property"]},
            "consequence": {"op": "prohibit", "actor": "implicit_addressee",
                            "action_text": parts["verb"], "object_text": parts["object"]},
        }
        return "rule", ast, ["The condition's property and the addressee require project-level interpretation."]

    if COMPLEX_SCOPE.search(clause):
        return None

    match = re.fullmatch(rf"(?:Do not|Never) (?P<verb>{WORD})(?: (?P<object>{NOUN_PHRASE}))?", clause, re.I)
    if match:
        ast = {"op": "prohibit", "actor": "implicit_addressee",
               "action_text": match["verb"], "object_text": match["object"]}
        return "rule", ast, ["The implicit addressee, verb sense, object reference, and any modifiers require review."]

    match = re.fullmatch(
        rf"(?P<subject>{NOUN_PHRASE}) must (?P<negation>not )?"
        rf"(?P<verb>{WORD})(?: (?P<object>{NOUN_PHRASE}))?", clause, re.I,
    )
    if match:
        ast = {"op": "prohibit" if match["negation"] else "obligate",
               "actor_text": match["subject"], "action_text": match["verb"],
               "object_text": match["object"]}
        return "rule", ast, ["The actor reference, verb sense, modal scope, and any modifiers require review."]

    match = re.fullmatch(rf"(?P<verb>{WORD})(?: (?P<object>{NOUN_PHRASE}))?", clause, re.I)
    if match and match["verb"].casefold() in IMPERATIVE_VERBS:
        ast = {"op": "obligate", "actor": "implicit_addressee",
               "action_text": match["verb"], "object_text": match["object"]}
        return "rule", ast, ["Imperative force, addressee, object reference, and any modifiers require review."]
    return None


def parse_clause(source_text: str, *, lexicon: WordNetLexicon | None = None) -> dict[str, Any]:
    """Return a partial candidate or an explicit abstention for one source line."""
    clause = _plain_clause(source_text)
    parsed = _candidate(clause)
    if parsed is None:
        return {"kind": "unparsed", "interpretation_status": "unparsed",
                "logic_candidates": [],
                "unresolved": ["No supported complete single-clause pattern matched this text."]}

    kind, ast, unresolved = parsed
    action = ast.get("action_text") or ast["consequence"]["action_text"]
    if lexicon is not None:
        ast["lexical_evidence"] = {"release": WORDNET_RELEASE, "action_form": action,
                                   "pos_candidates": list(lexicon.parts_of_speech(action.casefold()))}
        unresolved.append("WordNet parts of speech are lexical candidates, not a selected verb sense.")
    return {"kind": kind, "interpretation_status": "candidate_partial",
            "logic_candidates": [{"id": "pending", "language": "stub-typed-ir/0.1",
                                  "ast": ast, "review_status": "unreviewed"}],
            "unresolved": unresolved}


def parse_markdown(text: str, *, lexicon: WordNetLexicon | None = None) -> list[dict[str, Any]]:
    """Preserve line provenance and fence context for every nonblank line."""
    entries: list[dict[str, Any]] = []
    fence_char = ""
    fence_size = 0
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        fence = FENCE.match(line)
        in_fence = bool(fence_char)
        if fence:
            marker = fence.group(1)
            if not fence_char:
                fence_char, fence_size = marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_size:
                fence_char, fence_size = "", 0
            in_fence = True
        structural = in_fence or line.lstrip().startswith(("#", ">", "|"))
        fragments = [line] if structural else split_sentences(line)
        for sentence_number, fragment in enumerate(fragments, 1):
            result = (
                {"kind": "unparsed", "interpretation_status": "unparsed", "logic_candidates": [],
                 "unresolved": ["Markdown structure or fenced content is retained as source, not parsed as a directive."]}
                if structural else parse_clause(fragment, lexicon=lexicon)
            )
            entry_id = f"L{number}-S{sentence_number}"
            for index, candidate in enumerate(result["logic_candidates"], 1):
                candidate["id"] = f"{entry_id}-logic-{index}"
            entries.append({"id": entry_id, "source_span": {"start_line": number, "end_line": number},
                            "source_text": fragment, "adoption_status": "unadopted", **result})
    return entries


def split_sentences(line: str) -> list[str]:
    """Split only obvious period boundaries outside inline code and brackets."""
    fragments: list[str] = []
    list_prefix = LIST_PREFIX.match(line)
    first_content = list_prefix.end() if list_prefix else 0
    start = 0
    backtick = False
    bracket_depth = 0
    for index in range(first_content, len(line)):
        char = line[index]
        if char == "`":
            backtick = not backtick
        elif not backtick:
            if char in "([":
                bracket_depth += 1
            elif char in ")]":
                bracket_depth = max(0, bracket_depth - 1)
            elif char in ".?!" and bracket_depth == 0:
                rest = line[index + 1:]
                space = len(rest) - len(rest.lstrip())
                if space and space < len(rest) and rest[space].isupper():
                    fragments.append(line[start:index + 1].strip())
                    start = index + 1 + space
    fragments.append(line[start:].strip())
    return [fragment for fragment in fragments if fragment]


def parse_archive(archive: Path, member: str = DEFAULT_MEMBER, *,
                  lexicon: WordNetLexicon | None = None) -> dict[str, Any]:
    archive_bytes, member_bytes = load_archive_member(archive, member)
    text = member_bytes.decode("utf-8-sig")
    return {
        "schema_version": "handoff-stub/0.1",
        "producer": "natural-language-front-end",
        "consumer_contract_status": "unconfirmed",
        "execution_allowed": False,
        "source": {"archive_sha256": sha256(archive_bytes).hexdigest(), "member_path": member,
                   "member_sha256": sha256(member_bytes).hexdigest(),
                   "authority_status": "candidate_unadopted"},
        "entries": parse_markdown(text, lexicon=lexicon),
    }


def _write_new(path: Path, data: bytes) -> None:
    with path.open("xb") as target:
        target.write(data)
        target.flush()
        os.fsync(target.fileno())


def publish_result(result: dict[str, Any], archive: Path, output: Path, *,
                   replace: bool = False) -> dict[str, Any]:
    """Validate a staged ledger, then publish it and a content-addressed receipt.

    An existing different output requires explicit replacement and is retained
    under its full SHA-256 name. This is local file publication, not a remote
    transfer protocol or sister-machine acceptance.
    """
    from validate_handoff_stub import validate

    if output.is_symlink():
        raise ValueError("Output path is a symlink")
    if not output.parent.is_dir():
        raise FileNotFoundError(f"Output directory does not exist: {output.parent}")
    data = (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    output_hash = sha256(data).hexdigest()
    previous = output.read_bytes() if output.exists() else None
    if previous is not None and previous != data and not replace:
        raise FileExistsError("Output differs; pass --replace to preserve and replace the prior generation")

    stage = output.with_name(output.name + f".stage-{uuid4().hex}")
    _write_new(stage, data)
    try:
        checks = validate(archive, ROOT / "handoff_stub.schema.json", stage)
    except Exception as exc:
        # Preserve the failed stage for diagnosis; never publish it as output.
        raise RuntimeError(f"Staged output failed validation and remains at {stage}") from exc

    backup: Path | None = None
    if previous is not None and previous != data:
        previous_hash = sha256(previous).hexdigest()
        backup = output.with_name(output.name + f".previous-{previous_hash}")
        if backup.exists():
            if sha256(backup.read_bytes()).hexdigest() != previous_hash:
                raise ValueError(f"Prior-generation backup conflicts: {backup}")
        else:
            _write_new(backup, previous)
        if output.read_bytes() != previous:
            raise ValueError("Output changed before replacement; staged result was not published")

    if previous != data:
        if previous is None:
            os.link(stage, output)  # Atomic creation without replacing an existing path.
        else:
            os.replace(stage, output)
    if stage.exists():
        stage.unlink()
    if sha256(output.read_bytes()).hexdigest() != output_hash:
        raise ValueError("Published output digest differs from staged output")

    counts = {"entries": len(result["entries"]),
              "candidate_partial": sum(bool(e["logic_candidates"]) for e in result["entries"])}
    counts["unparsed"] = counts["entries"] - counts["candidate_partial"]
    receipt = {"receipt_kind": "local-generated-candidate", "accepted_by_sister_machine": False,
               "created_utc": datetime.now(timezone.utc).isoformat(),
               "output_path": str(output.resolve()), "output_sha256": output_hash,
               "source_archive_sha256": result["source"]["archive_sha256"],
               "source_member_sha256": result["source"]["member_sha256"],
               "schema_version": result["schema_version"], "validation": checks,
               "previous_output_path": str(backup) if backup else None, **counts}
    receipt_path = output.with_name(output.name + f".{output_hash}.receipt.json")
    try:
        if receipt_path.exists():
            existing_receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            if existing_receipt.get("output_sha256") != output_hash:
                raise ValueError(f"Existing receipt conflicts with published output: {receipt_path}")
        else:
            _write_new(receipt_path, (json.dumps(receipt, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    except Exception as exc:
        raise RuntimeError(
            f"Ledger is published at {output} with SHA-256 {output_hash}, "
            f"but its receipt is incomplete; inspect that exact output before retrying"
        ) from exc
    return {"output": str(output), "output_sha256": output_hash,
            "receipt": str(receipt_path), "previous_output": str(backup) if backup else None,
            **counts}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--member", default=DEFAULT_MEMBER)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replace", action="store_true", help="Preserve a different prior output before replacing it")
    parser.add_argument("--wordnet", action="store_true", help="Attach lexical POS candidates without choosing a sense")
    parser.add_argument("--wordnet-dir", type=Path)
    args = parser.parse_args()
    lexicon = WordNetLexicon(args.wordnet_dir) if args.wordnet else None
    result = parse_archive(args.archive, args.member, lexicon=lexicon)
    print(json.dumps(publish_result(result, args.archive, args.output, replace=args.replace)))


if __name__ == "__main__":
    main()
