"""Deterministic natural-English command front end for bounded local reads.

This first command family lists, reads, and searches files under an explicit
workspace root. Parsing never invokes a shell. Only registered read-only
adapters may run; unsupported language remains unparsed.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable

from command_aliases import (ALIAS_VERSION, AliasRule, Candidate, DEFAULT_CATALOG,
                             load_alias_catalog, resolve_aliases, rules_digest)
from semantic_layers import ProposalProvider, SessionHistory, validate_provider_proposals
from wordnet_command_layer import suggest_wordnet
from wordnet_lexicon import DEFAULT_DATA_DIR, WORDNET_RELEASE, WordNetLexicon


VERSION = "omni-intent/0.4"
DEFAULT_ROOT = Path(__file__).resolve().parent
MAX_COMMAND_CHARS = 1024
MAX_LIST_ENTRIES = 500
MAX_READ_BYTES = 128 * 1024
MAX_SEARCH_FILES = 1000
MAX_SEARCH_DIRS = 200
MAX_SEARCH_BYTES = 8 * 1024 * 1024
MAX_SEARCH_RESULTS = 50
SKIP_DEFAULT_SEARCH_DIRS = frozenset({".git", ".venv", ".wn_data", "__pycache__"})


@dataclass(frozen=True)
class Intent:
    source_text: str
    status: str
    capability: str | None
    arguments: dict[str, str]
    reason: str | None = None
    candidates: tuple[Candidate, ...] = ()
    alias_rules_sha256: str | None = None
    layer_trace: tuple[dict[str, str], ...] = ()

    def as_dict(self) -> dict[str, Any]:
        capability = CAPABILITIES.get(self.capability) if self.capability else None
        return {"schema_version": VERSION, "source_text": self.source_text,
                "source_sha256": sha256(self.source_text.encode("utf-8")).hexdigest(),
                "status": self.status, "capability": self.capability,
                "arguments": self.arguments, "reason": self.reason,
                "alias_catalog_version": ALIAS_VERSION,
                "alias_rules_sha256": self.alias_rules_sha256,
                "layer_trace": list(self.layer_trace),
                "candidates": [candidate.as_dict() for candidate in self.candidates],
                "side_effect_class": capability.side_effect_class
                if self.status == "parsed" and capability else None}


def parse_command(source: str, *, rules: tuple[AliasRule, ...] | None = None,
                  root: Path | None = None, use_wordnet: bool = True,
                  wordnet_dir: Path = DEFAULT_DATA_DIR,
                  history: SessionHistory | None = None,
                  web_provider: ProposalProvider | None = None,
                  llm_provider: ProposalProvider | None = None) -> Intent:
    """Apply aliases, WordNet, session history, web, and optional LLM in order."""
    selected_rules = ALIAS_RULES if rules is None else rules
    kind_cache: dict[str, str | None] = {}

    def path_kind(operand: str) -> str | None:
        if operand in kind_cache:
            return kind_cache[operand]
        if root is None:
            return None
        kind = None
        try:
            selected_root = root.resolve(strict=True)
            target = _within_root(selected_root, operand)
            if target.is_file():
                kind = "file"
            elif target.is_dir():
                kind = "directory"
        except (OSError, ValueError):
            pass
        kind_cache[operand] = kind
        return kind

    resolution = resolve_aliases(source, selected_rules,
                                 path_kind=path_kind if root is not None else None)
    digest = rules_digest(selected_rules)
    trace: list[dict[str, str]] = [{"layer": "aliases", "status": resolution.status}]

    def make_intent(status: str, candidates: tuple[Candidate, ...],
                    reason: str | None = None) -> Intent:
        winner = candidates[0] if status == "parsed" else None
        return Intent(source, status, winner.capability if winner else None,
                      dict(winner.arguments) if winner else {}, reason,
                      candidates, digest, tuple(trace))

    if resolution.status == "parsed":
        return make_intent("parsed", resolution.candidates)
    if resolution.status == "collision":
        candidates = history.rerank(source, resolution.candidates) if history else resolution.candidates
        trace.append({"layer": "history", "status": "ranked" if history and history.prior_choice(source) else "no_choice"})
        return make_intent("collision", candidates, resolution.reason)
    if resolution.reason and "empty, multiline, or over the length bound" in resolution.reason:
        return make_intent("unparsed", (), resolution.reason)

    if use_wordnet:
        try:
            candidates = suggest_wordnet(source, selected_rules, data_dir=wordnet_dir)
            trace.append({"layer": "wordnet", "status": "suggestions" if candidates else "no_match"})
            if candidates:
                candidates = history.rerank(source, candidates) if history else candidates
                trace.append({"layer": "history", "status": "ranked" if history and history.prior_choice(source) else "no_choice"})
                return make_intent("wordnet_suggestions", candidates,
                                   f"{WORDNET_RELEASE} supplied possible verb senses; choose an explicit command.")
        except (OSError, RuntimeError, ValueError):
            trace.append({"layer": "wordnet", "status": "unavailable"})
    else:
        trace.append({"layer": "wordnet", "status": "disabled"})

    if history is not None:
        candidates = history.suggest(source)
        trace.append({"layer": "history", "status": "suggestions" if candidates else "no_choice"})
        if candidates:
            return make_intent("history_suggestions", candidates,
                               "A prior choice in this session suggests an explicit command.")
    else:
        trace.append({"layer": "history", "status": "disabled"})

    capability_args = {key: value.arguments for key, value in CAPABILITIES.items()}
    for layer, provider in (("web", web_provider), ("llm", llm_provider)):
        if provider is None:
            trace.append({"layer": layer, "status": "not_configured"})
            continue
        try:
            candidates = validate_provider_proposals(source, provider, layer=layer,
                                                     capabilities=capability_args)
        except (OSError, RuntimeError, ValueError):
            trace.append({"layer": layer, "status": "invalid_or_failed"})
            continue
        trace.append({"layer": layer, "status": "suggestions" if candidates else "no_match"})
        if candidates:
            return make_intent(f"{layer}_suggestions", candidates,
                               f"{layer.upper()} supplied unverified proposals; choose an explicit command.")
    return make_intent("unparsed", (), resolution.reason)


def _within_root(root: Path, operand: str) -> Path:
    candidate = Path(operand)
    candidate = candidate if candidate.is_absolute() else root / candidate
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError("Requested path is outside the workspace root")
    return resolved


def _relative(root: Path, path: Path) -> str:
    return str(path.relative_to(root)) or "."


def _list_files(root: Path, path: str) -> dict[str, Any]:
    directory = _within_root(root, path)
    if not directory.is_dir():
        raise ValueError("List target is not a directory")
    children = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if len(children) >= MAX_LIST_ENTRIES:
                raise ValueError(f"Directory exceeds the {MAX_LIST_ENTRIES}-entry listing bound")
            kind = "symlink" if entry.is_symlink() else "directory" if entry.is_dir(follow_symlinks=False) else "file"
            children.append({"name": entry.name, "kind": kind})
    children.sort(key=lambda item: (item["name"].casefold(), item["name"]))
    return {"path": _relative(root, directory), "entries": children, "count": len(children)}


def _read_file(root: Path, path: str) -> dict[str, Any]:
    target = _within_root(root, path)
    if not target.is_file():
        raise ValueError("Read target is not a regular file")
    if target.stat().st_size > MAX_READ_BYTES:
        raise ValueError(f"File exceeds the {MAX_READ_BYTES}-byte read bound")
    with target.open("rb") as stream:
        data = stream.read(MAX_READ_BYTES + 1)
    if len(data) > MAX_READ_BYTES or b"\x00" in data:
        raise ValueError("File is oversized or binary")
    return {"path": _relative(root, target), "sha256": sha256(data).hexdigest(),
            "bytes": len(data), "text": data.decode("utf-8")}


def _search_text(root: Path, path: str, term: str) -> dict[str, Any]:
    target = _within_root(root, path)
    needle = term.casefold()
    matches: list[dict[str, Any]] = []
    visited_files = 0
    read_bytes = 0
    skipped_binary = 0
    skipped_large = 0
    skipped_directories = 0
    visited_directories = 0
    truncated = False

    def inspect_file(file: Path) -> None:
        nonlocal visited_files, read_bytes, skipped_binary, skipped_large, truncated
        if not file.resolve(strict=True).is_relative_to(root):
            return
        size = file.stat().st_size
        if size > MAX_READ_BYTES:
            skipped_large += 1
            return
        if visited_files >= MAX_SEARCH_FILES or read_bytes + size > MAX_SEARCH_BYTES:
            truncated = True
            return
        visited_files += 1
        with file.open("rb") as stream:
            data = stream.read(MAX_READ_BYTES + 1)
        if len(data) > MAX_READ_BYTES:
            skipped_large += 1
            return
        read_bytes += len(data)
        if b"\x00" in data:
            skipped_binary += 1
            return
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            skipped_binary += 1
            return
        for number, line in enumerate(text.splitlines(), 1):
            if needle in line.casefold():
                matches.append({"path": _relative(root, file), "line": number,
                                "text": line[:300]})
                if len(matches) >= MAX_SEARCH_RESULTS:
                    truncated = True
                    return

    if target.is_file():
        inspect_file(target)
    elif target.is_dir():
        for current, dirs, files in os.walk(target, followlinks=False):
            if truncated:
                break
            if visited_directories >= MAX_SEARCH_DIRS:
                truncated = True
                break
            visited_directories += 1
            kept = []
            for dirname in dirs:
                child = Path(current) / dirname
                if child.is_symlink() or dirname in SKIP_DEFAULT_SEARCH_DIRS:
                    skipped_directories += 1
                else:
                    kept.append(dirname)
            dirs[:] = sorted(kept, key=str.casefold)
            for filename in sorted(files, key=str.casefold):
                file = Path(current) / filename
                if not file.is_symlink() and file.is_file():
                    inspect_file(file)
                if truncated:
                    break
    else:
        raise ValueError("Search target is neither a file nor a directory")
    return {"path": _relative(root, target), "term": term, "matches": matches,
            "match_count": len(matches), "files_examined": visited_files,
            "directories_examined": visited_directories,
            "bytes_examined": read_bytes, "skipped_binary": skipped_binary,
            "skipped_large": skipped_large, "skipped_directories": skipped_directories,
            "truncated": truncated}


def _find_files(root: Path, path: str, name: str) -> dict[str, Any]:
    target = _within_root(root, path)
    if not target.is_dir():
        raise ValueError("Find target is not a directory")
    needle = name.casefold()
    matches: list[str] = []
    visited_files = visited_directories = skipped_directories = 0
    truncated = False
    for current, dirs, files in os.walk(target, followlinks=False):
        if visited_directories >= MAX_SEARCH_DIRS:
            truncated = True
            break
        visited_directories += 1
        kept = []
        for dirname in dirs:
            child = Path(current) / dirname
            if child.is_symlink() or dirname in SKIP_DEFAULT_SEARCH_DIRS:
                skipped_directories += 1
            else:
                kept.append(dirname)
        dirs[:] = sorted(kept, key=str.casefold)
        for filename in sorted(files, key=str.casefold):
            file = Path(current) / filename
            if file.is_symlink() or not file.is_file():
                continue
            if visited_files >= MAX_SEARCH_FILES:
                truncated = True
                break
            visited_files += 1
            if needle in filename.casefold():
                matches.append(_relative(root, file))
                if len(matches) >= MAX_SEARCH_RESULTS:
                    truncated = True
                    break
        if truncated:
            break
    return {"path": _relative(root, target), "name": name, "matches": matches,
            "match_count": len(matches), "files_examined": visited_files,
            "directories_examined": visited_directories,
            "skipped_directories": skipped_directories, "truncated": truncated}


@dataclass(frozen=True)
class Capability:
    description: str
    arguments: tuple[str, ...]
    example: str
    handler: Callable[..., dict[str, Any]]
    side_effect_class: str = "read_only"
    uses_wordnet: bool = False


def _help(root: Path) -> dict[str, Any]:
    return {"capabilities": capability_manifest()}


def _workspace(root: Path) -> dict[str, Any]:
    return {"root": str(root)}


def _define_word(root: Path, word: str, *, wordnet_dir: Path) -> dict[str, Any]:
    lexicon = WordNetLexicon(wordnet_dir)
    definitions = lexicon.definitions(word)
    return {"word": word, "wordnet_release": WORDNET_RELEASE,
            "sense_count": len(definitions), "senses": definitions,
            "sense_selected": False}


def _word_relations(root: Path, word: str, *, wordnet_dir: Path) -> dict[str, Any]:
    lexicon = WordNetLexicon(wordnet_dir)
    relations = lexicon.relations(word)
    return {"word": word, "wordnet_release": WORDNET_RELEASE,
            "sense_count": len(relations["senses"]), **relations,
            "sense_selected": False}


CAPABILITIES: dict[str, Capability] = {
    "help": Capability("Show registered commands", (), "help", _help),
    "workspace": Capability("Show the workspace root", (), "where am I", _workspace),
    "list_files": Capability("List one directory", ("path",), "list files in tests", _list_files),
    "read_file": Capability("Read a bounded UTF-8 file", ("path",), "show file README.md", _read_file),
    "find_files": Capability("Find file names containing text", ("path", "name"),
                             "find files named test in tests", _find_files),
    "search_text": Capability("Find text within files", ("path", "term"),
                              'search for "ground-boolean" in .', _search_text),
    "define_word": Capability("Show every WordNet definition for a word", ("word",),
                              "define dog", _define_word, uses_wordnet=True),
    "word_relations": Capability("Show semantic and lexical WordNet relations for every sense",
                                 ("word",), "show relations for dog", _word_relations,
                                 uses_wordnet=True),
}

ALIAS_RULES = load_alias_catalog(
    capabilities={key: value.arguments for key, value in CAPABILITIES.items()})


def capability_manifest() -> dict[str, dict[str, Any]]:
    """Describe the registered adapter surface without exposing handler objects."""
    return {key: {"description": value.description, "arguments": list(value.arguments),
                  "example": value.example, "side_effect_class": value.side_effect_class}
            for key, value in CAPABILITIES.items()}


def _quote_choice(value: str) -> str | None:
    if '"' not in value:
        return f'"{value}"'
    if "'" not in value:
        return f"'{value}'"
    return None


def _explicit_choice(candidate: Candidate) -> str | None:
    args = candidate.arguments
    if candidate.capability == "help":
        return "help"
    if candidate.capability == "workspace":
        return "where am I"
    path = _quote_choice(args.get("path", "."))
    if path is None:
        return None
    if candidate.capability == "read_file":
        return f"read file {path}"
    if candidate.capability == "list_files":
        return f"list files in {path}"
    if candidate.capability in {"find_files", "search_text"}:
        key = "name" if candidate.capability == "find_files" else "term"
        if key not in args:
            return None
        term = _quote_choice(args[key])
        if term is None:
            return None
        prefix = "find files named" if candidate.capability == "find_files" else "search for"
        return f"{prefix} {term} in {path}"
    if candidate.capability in {"define_word", "word_relations"}:
        word = _quote_choice(args.get("word", ""))
        if word is None:
            return None
        prefix = "define" if candidate.capability == "define_word" else "show relations for"
        return f"{prefix} {word}"
    return None


def safe_display(intent: Intent) -> dict[str, Any]:
    """Show every ranked collision or lower-layer proposal without execution."""
    display_kinds = {"collision": "meaning_collision",
                     "wordnet_suggestions": "wordnet_suggestions",
                     "history_suggestions": "history_suggestions",
                     "web_suggestions": "web_suggestions",
                     "llm_suggestions": "llm_suggestions"}
    if intent.status not in display_kinds:
        raise ValueError("Safe display requires a non-executing proposal intent")
    options = []
    for rank, candidate in enumerate(intent.candidates, 1):
        capability = CAPABILITIES.get(candidate.capability)
        options.append({"rank": rank, "capability": candidate.capability,
                        "description": capability.description if capability else "Unknown capability",
                        "arguments": candidate.arguments, "score": candidate.score,
                        "rule_id": candidate.rule_id, "evidence": list(candidate.evidence),
                        "explicit_command": _explicit_choice(candidate)})
    message = ("Multiple meanings matched. Use an explicit command to choose one."
               if intent.status == "collision" else
               "Unverified lexical or provider suggestions. Use an explicit command to choose one.")
    return {"kind": display_kinds[intent.status], "source_text": intent.source_text,
            "message": message,
            "options": options,
            "lead_score_gap": options[0]["score"] - options[1]["score"] if len(options) > 1 else None,
            "operation_executed": False,
            "inspection_note": "Ranking may have inspected path metadata within the workspace root."}


def render_safe_display(display: dict[str, Any]) -> str:
    """Readable view of every meaning in a collision display."""
    title = "Meaning collision" if display["kind"] == "meaning_collision" else "Non-executing suggestions"
    lines = [f"{title}: {display['source_text']}",
             "No requested file command ran. Ranking may have inspected path metadata.",
             "Ranked meanings:"]
    for option in display["options"]:
        lines.append(f"  {option['rank']}. {option['capability']} (score {option['score']}): "
                     f"{option['description']}")
        lines.append(f"     arguments: {json.dumps(option['arguments'], ensure_ascii=False, sort_keys=True)}")
        lines.append(f"     evidence: {', '.join(option['evidence'])}")
        if option["explicit_command"] is not None:
            lines.append(f"     choose with: {option['explicit_command']}")
    return "\n".join(lines)


def execute_intent(intent: Intent, *, root: Path = DEFAULT_ROOT,
                   wordnet_dir: Path = DEFAULT_DATA_DIR) -> dict[str, Any]:
    """Execute only the registered read-only capability named by an intent."""
    if intent.status in {"collision", "wordnet_suggestions", "history_suggestions",
                         "web_suggestions", "llm_suggestions"}:
        return {"status": "not_executed", "reason": "Meaning needs an explicit command",
                "safe_display": safe_display(intent)}
    if intent.status != "parsed" or intent.capability is None:
        return {"status": "rejected", "reason": intent.reason or "Input was not parsed"}
    try:
        root = root.resolve(strict=True)
        if not root.is_dir():
            return {"status": "rejected", "reason": "Workspace root is not a directory"}
        capability = CAPABILITIES.get(intent.capability)
        if capability is None or capability.side_effect_class != "read_only":
            return {"status": "rejected", "reason": "Capability is not registered for execution"}
        if set(intent.arguments) != set(capability.arguments):
            return {"status": "rejected", "reason": "Intent arguments do not match the registered capability"}
        if capability.uses_wordnet:
            result = capability.handler(root, wordnet_dir=wordnet_dir, **intent.arguments)
        else:
            result = capability.handler(root, **intent.arguments)
    except (OSError, RuntimeError, UnicodeError, ValueError) as exc:
        return {"status": "rejected", "reason": str(exc)}
    return {"status": "completed", "capability": intent.capability,
            "root": str(root), "result": result}


def _respond(source: str, root: Path, plan_only: bool,
             rules: tuple[AliasRule, ...] | None = None, *,
             use_wordnet: bool = True, wordnet_dir: Path = DEFAULT_DATA_DIR,
             history: SessionHistory | None = None,
             web_provider: ProposalProvider | None = None,
             llm_provider: ProposalProvider | None = None) -> dict[str, Any]:
    intent = parse_command(source, rules=rules, root=root, use_wordnet=use_wordnet,
                           wordnet_dir=wordnet_dir, history=history,
                           web_provider=web_provider, llm_provider=llm_provider)
    response: dict[str, Any] = {"intent": intent.as_dict()}
    if intent.status in {"collision", "wordnet_suggestions", "history_suggestions",
                         "web_suggestions", "llm_suggestions"}:
        response["safe_display"] = safe_display(intent)
    if not plan_only:
        execution = execute_intent(intent, root=root, wordnet_dir=wordnet_dir)
        if "safe_display" in response:
            execution = {"status": "not_executed", "reason": "Meaning needs an explicit command"}
        response["execution"] = execution
    return response


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="*", help="Direct English command; omit for interactive mode")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Accessible workspace root")
    parser.add_argument("--plan", action="store_true", help="Parse without executing")
    parser.add_argument("--aliases", type=Path, default=DEFAULT_CATALOG,
                        help="Validated JSON alias catalog")
    parser.add_argument("--human", action="store_true",
                        help="Show collisions as ranked readable choices")
    parser.add_argument("--no-wordnet", action="store_true",
                        help="Disable the secondary WordNet layer")
    parser.add_argument("--wordnet-dir", type=Path, default=DEFAULT_DATA_DIR,
                        help="Local pinned WordNet data directory")
    args = parser.parse_args()
    try:
        rules = load_alias_catalog(args.aliases,
                                   capabilities={key: value.arguments for key, value in CAPABILITIES.items()})
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        parser.error(f"Invalid alias catalog: {exc}")
    if args.command:
        response = _respond(" ".join(args.command), args.root, args.plan, rules,
                            use_wordnet=not args.no_wordnet, wordnet_dir=args.wordnet_dir)
        if args.human and "safe_display" in response:
            print(render_safe_display(response["safe_display"]))
        else:
            print(json.dumps(response, ensure_ascii=False, indent=2))
        if "safe_display" in response:
            return 3
        if response["intent"]["status"] != "parsed":
            return 2
        if not args.plan and response["execution"]["status"] != "completed":
            return 2
        return 0
    print("Omni file/search front end. Type 'help' or 'exit'.")
    history = SessionHistory()
    pending_source: str | None = None
    pending_options: set[tuple[str, tuple[tuple[str, str], ...]]] = set()
    while True:
        try:
            source = input("omni> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if source.strip().casefold() in {"exit", "quit"}:
            break
        response = _respond(source, args.root, args.plan, rules,
                            use_wordnet=not args.no_wordnet, wordnet_dir=args.wordnet_dir,
                            history=history)
        parsed = response["intent"]
        if pending_source is not None and parsed["status"] == "parsed":
            key = (parsed["capability"], tuple(sorted(parsed["arguments"].items())))
            if key in pending_options:
                history.record_choice(pending_source, parsed["capability"], parsed["arguments"])
                response["session_history_recorded_for"] = pending_source
        pending_source = None
        pending_options = set()
        if "safe_display" in response:
            pending_source = source
            pending_options = {(option["capability"], tuple(sorted(option["arguments"].items())))
                               for option in response["safe_display"]["options"]}
        if "safe_display" in response:
            print(render_safe_display(response["safe_display"]))
        else:
            print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
