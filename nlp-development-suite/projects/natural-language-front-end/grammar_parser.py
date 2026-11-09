"""A small, deterministic English phrase-structure parser.

The grammar and vocabulary are intentionally explicit. An unknown word is never
assigned a part of speech by guessing.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import cache
import json
import re
from pathlib import Path
from typing import Any


LEXICON: dict[str, frozenset[str]] = {
    "DET": frozenset({"a", "an", "the"}),
    "ADJ": frozenset({"big", "blue", "old", "red", "small", "young"}),
    "N": frozenset({"book", "boy", "cat", "dog", "girl", "man", "park", "table", "telescope", "woman"}),
    "PRON": frozenset({"he", "her", "him", "i", "it", "me", "she", "them", "they", "us", "we", "you"}),
    "PROPN": frozenset({"alice", "bob"}),
    "IV": frozenset({"run", "runs", "sleep", "sleeps", "walk", "walks"}),
    "TV": frozenset({"chase", "chased", "find", "found", "like", "likes", "saw", "see", "sees"}),
    "P": frozenset({"by", "in", "near", "on", "under", "with"}),
}

TOKEN_PATTERN = re.compile(r"\w+(?:['’]\w+)*|[^\w\s]", re.UNICODE)
MAX_WORDS = 30
MAX_TREES = 128


@dataclass(frozen=True)
class Token:
    text: str
    start: int
    end: int

    @property
    def key(self) -> str:
        return self.text.casefold()

    def as_dict(self) -> dict[str, Any]:
        return {"text": self.text, "start": self.start, "end": self.end}


@dataclass(frozen=True)
class Node:
    label: str
    start: int
    end: int
    children: tuple[Node, ...] = ()
    text: str | None = None

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"label": self.label, "start": self.start, "end": self.end}
        if self.text is not None:
            result["text"] = self.text
        else:
            result["children"] = [child.as_dict() for child in self.children]
        return result

    def bracketed(self) -> str:
        if self.text is not None:
            return f"({self.label} {self.text})"
        return f"({self.label} {' '.join(child.bracketed() for child in self.children)})"


def tokenize(text: str) -> list[Token]:
    return [Token(m.group(), m.start(), m.end()) for m in TOKEN_PATTERN.finditer(text)]


def parse(
    text: str,
    *,
    use_wordnet: bool = False,
    wordnet_data_dir: Path | None = None,
    include_senses: bool = False,
) -> dict[str, Any]:
    """Return all recognized trees, up to MAX_TREES, with source offsets.

    Supported rules: S -> NP VP; NP -> PRON | PROPN | DET? ADJ* N |
    NP PP; VP -> IV | TV NP | VP PP; PP -> P NP.
    """
    if include_senses and not use_wordnet:
        raise ValueError("include_senses requires use_wordnet=True")
    wordnet = None
    if use_wordnet:
        from wordnet_lexicon import WordNetLexicon, WORDNET_RELEASE
        wordnet = WordNetLexicon(wordnet_data_dir)

    all_tokens = tokenize(text)
    words = all_tokens[:]
    if words and words[-1].text in {".", "?", "!"}:
        words.pop()

    result: dict[str, Any] = {"accepted": False, "tokens": [t.as_dict() for t in all_tokens], "trees": []}
    if wordnet:
        result["wordnet_release"] = WORDNET_RELEASE
    if not words:
        result["error"] = "No words to parse."
        return result
    if len(words) > MAX_WORDS:
        result["error"] = f"Input exceeds the {MAX_WORDS}-word limit."
        return result
    punctuation = [t.text for t in words if not t.text[0].isalnum() and t.text[0] != "_"]
    if punctuation:
        result["error"] = f"Unsupported internal punctuation: {', '.join(punctuation)}"
        return result

    manual_categories = {
        t.key: {category for category, forms in LEXICON.items() if t.key in forms}
        for t in words
    }
    categories = {
        t.key: (manual_categories[t.key] or
                (set(wordnet.grammar_categories(t.key)) if wordnet else set()))
        for t in words
    }
    if wordnet:
        result["lexical_evidence"] = [
            {
                "text": t.text,
                "grammar_categories": sorted(categories[t.key]),
                "manual_categories": sorted(manual_categories[t.key]),
                "wordnet_pos_candidates": list(wordnet.parts_of_speech(t.key)),
                **({"sense_candidates": wordnet.sense_candidates(t.key)} if include_senses else {}),
            }
            for t in words
        ]
    unknown = list(dict.fromkeys(t.text for t in words if not categories[t.key]))
    if unknown:
        result["unknown_words"] = unknown
        result["error"] = "The grammar has no usable category for one or more words."
        return result

    def leaf(category: str, index: int) -> Node | None:
        if index < len(words) and category in categories[words[index].key]:
            t = words[index]
            return Node(category, t.start, t.end, text=t.text)
        return None

    def branch(label: str, children: tuple[Node, ...]) -> Node:
        return Node(label, children[0].start, children[-1].end, children)

    def extend_pp(label: str, initial: list[tuple[Node, int]]) -> tuple[tuple[Node, int], ...]:
        found = list(initial)
        seen = set(initial)
        cursor = 0
        while cursor < len(found) and len(found) < MAX_TREES:
            node, end = found[cursor]
            cursor += 1
            for pp, pp_end in parse_pp(end):
                item = (branch(label, (node, pp)), pp_end)
                if item not in seen:
                    seen.add(item)
                    found.append(item)
                    if len(found) >= MAX_TREES:
                        break
        return tuple(found)

    @cache
    def parse_np(index: int) -> tuple[tuple[Node, int], ...]:
        base: list[tuple[Node, int]] = []
        for category in ("PRON", "PROPN"):
            token = leaf(category, index)
            if token:
                base.append((branch("NP", (token,)), index + 1))

        parts: list[Node] = []
        pos = index
        det = leaf("DET", pos)
        if det:
            parts.append(det)
            pos += 1
        while (adj := leaf("ADJ", pos)) is not None:
            parts.append(adj)
            pos += 1
        noun = leaf("N", pos)
        if noun:
            base.append((branch("NP", (*parts, noun)), pos + 1))
        return extend_pp("NP", base)

    @cache
    def parse_pp(index: int) -> tuple[tuple[Node, int], ...]:
        prep = leaf("P", index)
        if prep is None:
            return ()
        return tuple((branch("PP", (prep, np)), end) for np, end in parse_np(index + 1))[:MAX_TREES]

    @cache
    def parse_vp(index: int) -> tuple[tuple[Node, int], ...]:
        base: list[tuple[Node, int]] = []
        iv = leaf("IV", index)
        if iv:
            base.append((branch("VP", (iv,)), index + 1))
        tv = leaf("TV", index)
        if tv:
            base.extend((branch("VP", (tv, np)), end) for np, end in parse_np(index + 1))
        return extend_pp("VP", base[:MAX_TREES])

    trees: list[Node] = []
    for np, np_end in parse_np(0):
        for vp, vp_end in parse_vp(np_end):
            if vp_end == len(words):
                tree = branch("S", (np, vp))
                if tree not in trees:
                    trees.append(tree)
                    if len(trees) >= MAX_TREES:
                        break
        if len(trees) >= MAX_TREES:
            break

    result["accepted"] = bool(trees)
    result["trees"] = [tree.as_dict() for tree in trees]
    if not trees:
        result["error"] = "No complete parse under the current grammar."
    if len(trees) >= MAX_TREES:
        result["truncated"] = True
    return result


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("sentence", nargs="*", help="Sentence to parse; reads stdin if omitted")
    cli.add_argument("--json", action="store_true", help="Print machine-readable results")
    cli.add_argument("--wordnet", action="store_true", help="Use pinned Open English WordNet for noun/adjective lookup")
    cli.add_argument("--senses", action="store_true", help="List possible WordNet senses without choosing one (requires --wordnet)")
    cli.add_argument("--wordnet-dir", type=Path, help="Directory containing the pinned WordNet data")
    args = cli.parse_args()
    text = " ".join(args.sentence) if args.sentence else input("Sentence: ")
    try:
        result = parse(text, use_wordnet=args.wordnet, wordnet_data_dir=args.wordnet_dir,
                       include_senses=args.senses)
    except (RuntimeError, ValueError) as exc:
        cli.error(str(exc))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Accepted: {result['accepted']}")
        if result.get("error"):
            print(result["error"])
        if result.get("unknown_words"):
            print("Unknown words:", ", ".join(result["unknown_words"]))
        for i, tree in enumerate(result["trees"], 1):
            print(f"{i}. {Node_from_dict(tree).bracketed()}")
        if result.get("truncated"):
            print(f"Stopped after {MAX_TREES} trees.")


def Node_from_dict(data: dict[str, Any]) -> Node:
    """Rebuild a node for the human-readable CLI display."""
    return Node(data["label"], data["start"], data["end"],
                tuple(Node_from_dict(child) for child in data.get("children", [])), data.get("text"))


if __name__ == "__main__":
    main()
