"""Proposal-only parsing for the first command families."""

from __future__ import annotations

from dataclasses import dataclass

from .normalize import normalize_text, token_set


SEARCH_WORDS = frozenset({"find", "search", "locate", "look"})
SHOW_WORDS = frozenset({"show", "open", "read", "inspect", "display"})
DEFINE_WORDS = frozenset({"define", "definition", "meaning", "explain"})
RELATION_WORDS = frozenset({"related", "relation", "relations", "similar", "synonyms"})


@dataclass(frozen=True)
class IntentProposal:
    operation: str
    target: str
    query: str
    matched_tokens: tuple[str, ...]
    status: str = "proposal-only"


def parse_intent(text: str) -> IntentProposal:
    """Recognize a narrow command shape without executing or authorizing it."""

    normalized = normalize_text(text)
    words = normalized.split()
    first = words[0] if words else ""
    matched: list[str] = []
    if first in SEARCH_WORDS:
        operation = "search"
        matched.append(first)
        target = "files" if "file" in words or "files" in words else "unknown"
        if target != "unknown":
            matched.append(target)
        query = normalized
        for marker in ("named", "matching", "for"):
            if marker in words:
                query = " ".join(words[words.index(marker) + 1:])
                break
        return IntentProposal(operation, target, query, tuple(matched))
    if first in DEFINE_WORDS:
        return IntentProposal("define", "word", " ".join(words[1:]), (first,))
    if first in RELATION_WORDS or any(word in RELATION_WORDS for word in words):
        matched.extend(word for word in words if word in RELATION_WORDS)
        return IntentProposal("relate", "word", " ".join(word for word in words if word not in RELATION_WORDS), tuple(matched))
    if first in SHOW_WORDS:
        matched.append(first)
        target = "files" if "file" in words or "files" in words else "word"
        return IntentProposal("inspect", target, " ".join(words[1:]), tuple(matched))
    return IntentProposal("unknown", "unknown", normalized, tuple(token_set(normalized, remove_stopwords=False)))
