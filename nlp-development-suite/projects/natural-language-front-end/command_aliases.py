"""Validated declarative aliases and deterministic command ranking."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Callable


ALIAS_VERSION = "omni-alias/0.1"
DEFAULT_CATALOG = Path(__file__).with_name("command_aliases.json")
MAX_CATALOG_BYTES = 64 * 1024
MAX_RULES = 200
MODES = frozenset({"exact", "path", "term", "generic_path", "word"})


@dataclass(frozen=True)
class AliasRule:
    rule_id: str
    phrase: str
    mode: str
    capability: str
    score: int
    arguments: dict[str, str]


@dataclass(frozen=True)
class Candidate:
    capability: str
    arguments: dict[str, str]
    score: int
    rule_id: str
    evidence: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"capability": self.capability, "arguments": self.arguments,
                "score": self.score, "rule_id": self.rule_id,
                "evidence": list(self.evidence)}


@dataclass(frozen=True)
class Resolution:
    status: str
    winner: Candidate | None
    candidates: tuple[Candidate, ...]
    reason: str | None


def _operand(raw: str) -> str | None:
    raw = raw.strip()
    if not raw or "\x00" in raw or "\n" in raw or "\r" in raw:
        return None
    if raw[0] in {"'", '"'}:
        if len(raw) < 2 or raw[-1] != raw[0] or raw[0] in raw[1:-1]:
            return None
        return raw[1:-1] or None
    if '"' in raw:
        return None
    return raw


def _split_unquoted_in(raw: str) -> tuple[str, str] | None:
    quote = None
    for index, character in enumerate(raw):
        if character in {"'", '"'}:
            if quote is None:
                quote = character
            elif quote == character:
                quote = None
        elif quote is None and raw[index:index + 4].casefold() == " in ":
            return raw[:index], raw[index + 4:]
    return None


def load_alias_catalog(path: Path = DEFAULT_CATALOG,
                       *, capabilities: dict[str, tuple[str, ...]]) -> tuple[AliasRule, ...]:
    """Load data-only aliases; never load handlers or arbitrary expressions."""
    with path.open("rb") as stream:
        raw = stream.read(MAX_CATALOG_BYTES + 1)
    if len(raw) > MAX_CATALOG_BYTES:
        raise ValueError("Alias catalog exceeds size bound")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key in alias catalog: {key}")
            result[key] = value
        return result

    document = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    if not isinstance(document, dict) or set(document) != {"schema_version", "rules"}:
        raise ValueError("Alias catalog has invalid top-level fields")
    if document["schema_version"] != ALIAS_VERSION:
        raise ValueError("Unsupported alias catalog version")
    records = document["rules"]
    if not isinstance(records, list) or not 0 < len(records) <= MAX_RULES:
        raise ValueError("Alias catalog has invalid rule count")
    rules: list[AliasRule] = []
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != {
                "id", "phrase", "mode", "capability", "score", "arguments"}:
            raise ValueError("Alias rule has invalid fields")
        rule_id, phrase, mode, capability, score, arguments = (
            record[key] for key in ("id", "phrase", "mode", "capability", "score", "arguments"))
        if not isinstance(rule_id, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", rule_id) or rule_id in seen:
            raise ValueError("Alias rule ID is invalid or duplicated")
        if not isinstance(phrase, str) or not phrase or phrase != phrase.strip() or len(phrase) > 80:
            raise ValueError(f"Alias phrase is invalid: {rule_id}")
        if "\n" in phrase or "\r" in phrase or "\x00" in phrase or '"' in phrase:
            raise ValueError(f"Alias phrase has forbidden characters: {rule_id}")
        if not isinstance(mode, str) or not isinstance(capability, str) or mode not in MODES or capability not in capabilities:
            raise ValueError(f"Alias mode or capability is invalid: {rule_id}")
        if type(score) is not int or not 0 <= score <= 100:
            raise ValueError(f"Alias score is invalid: {rule_id}")
        if not isinstance(arguments, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in arguments.items()):
            raise ValueError(f"Alias arguments are invalid: {rule_id}")
        expected = set(capabilities[capability])
        if mode == "exact":
            if set(arguments) != expected or ("path" in arguments and arguments["path"] != "."):
                raise ValueError(f"Exact alias has invalid arguments: {rule_id}")
        elif mode == "word":
            if arguments != {} or expected != {"word"} or capability not in {
                    "define_word", "word_relations"}:
                raise ValueError(f"Word alias has invalid capability: {rule_id}")
        elif arguments != {"path": "."}:
            raise ValueError(f"Alias has invalid argument defaults: {rule_id}")
        if mode in {"path", "generic_path"} and expected != {"path"}:
            raise ValueError(f"Path alias has invalid capability: {rule_id}")
        if mode == "term" and capability not in {"find_files", "search_text"}:
            raise ValueError(f"Term alias has invalid capability: {rule_id}")
        if mode == "term" and expected != {"path", "name" if capability == "find_files" else "term"}:
            raise ValueError(f"Term alias has invalid capability arguments: {rule_id}")
        if mode == "generic_path" and capability not in {"list_files", "read_file"}:
            raise ValueError(f"Generic path alias has invalid capability: {rule_id}")
        seen.add(rule_id)
        rules.append(AliasRule(rule_id, phrase, mode, capability, score, arguments))
    return tuple(rules)


def rules_digest(rules: tuple[AliasRule, ...]) -> str:
    payload = [{"id": rule.rule_id, "phrase": rule.phrase, "mode": rule.mode,
                "capability": rule.capability, "score": rule.score,
                "arguments": rule.arguments} for rule in rules]
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _match(rule: AliasRule, command: str,
           path_kind: Callable[[str], str | None] | None) -> Candidate | None:
    folded = command.casefold()
    prefix = rule.phrase.casefold()
    if rule.mode == "exact":
        if folded != prefix:
            return None
        return Candidate(rule.capability, dict(rule.arguments), rule.score, rule.rule_id,
                         ("exact_alias", f"phrase:{rule.phrase}"))
    if not folded.startswith(prefix + " "):
        return None
    raw = command[len(rule.phrase) + 1:]
    if rule.mode == "generic_path" and (
            raw.casefold() in {"file", "files", "current directory", "relations for"} or
            raw.casefold().startswith(("file ", "files ", "current directory ",
                                       "relations for "))):
        return None
    if rule.rule_id == "read_plain" and (raw.casefold() == "file" or raw.casefold().startswith("file ")):
        return None
    if rule.rule_id.startswith("generic_find_") and (
            raw.casefold() in {"files named", "text"} or
            raw.casefold().startswith(("files named ", "text "))):
        return None
    if rule.mode == "word":
        word = _operand(raw)
        if word is None or len(word) > 200:
            return None
        return Candidate(rule.capability, {"word": word}, rule.score, rule.rule_id,
                         ("word_operand", f"phrase:{rule.phrase}"))
    if rule.mode in {"path", "generic_path"}:
        path = _operand(raw)
        if path is None:
            return None
        evidence = ["path_operand", f"phrase:{rule.phrase}"]
        score = rule.score
        if rule.mode == "generic_path":
            if path.endswith(("/", "\\")) and rule.capability == "list_files":
                score += 15
                evidence.append("directory_separator")
            elif Path(path).suffix and rule.capability == "read_file":
                score += 15
                evidence.append("file_extension")
            kind = path_kind(path) if path_kind is not None else None
            if kind in {"file", "directory"}:
                expected = "file" if rule.capability == "read_file" else "directory"
                if kind == expected:
                    score += 25
                    evidence.append(f"path_is_{kind}")
                else:
                    score -= 20
                    evidence.append(f"path_is_{kind}_conflict")
        return Candidate(rule.capability, {"path": path}, score, rule.rule_id, tuple(evidence))
    if raw.casefold().endswith(" in"):
        return None
    split = _split_unquoted_in(raw)
    term_raw, path_raw = split if split is not None else (raw, ".")
    term, path = _operand(term_raw), _operand(path_raw)
    if term is None or path is None:
        return None
    key = "name" if rule.capability == "find_files" else "term"
    evidence = ("term_operand", "explicit_path" if split else "default_path", f"phrase:{rule.phrase}")
    return Candidate(rule.capability, {key: term, "path": path}, rule.score,
                     rule.rule_id, evidence)


def resolve_aliases(source: str, rules: tuple[AliasRule, ...],
                    *, path_kind: Callable[[str], str | None] | None = None) -> Resolution:
    command = source.strip()
    if not command or len(command) > 1024 or "\n" in command or "\r" in command:
        return Resolution("unparsed", None, (), "Command is empty, multiline, or over the length bound.")
    best: dict[tuple[str, tuple[tuple[str, str], ...]], Candidate] = {}
    for rule in rules:
        candidate = _match(rule, command, path_kind)
        if candidate is None:
            continue
        key = (candidate.capability, tuple(sorted(candidate.arguments.items())))
        prior = best.get(key)
        if prior is None or (candidate.score, candidate.rule_id) > (prior.score, prior.rule_id):
            best[key] = candidate
    ranked = tuple(sorted(best.values(), key=lambda c: (-c.score, c.capability, c.rule_id)))
    if not ranked:
        return Resolution("unparsed", None, (), "No registered alias matched the complete input.")
    if len(ranked) > 1:
        return Resolution("collision", None, ranked,
                          "Multiple distinct meanings matched; choose an explicit phrase.")
    return Resolution("parsed", ranked[0], ranked, None)
