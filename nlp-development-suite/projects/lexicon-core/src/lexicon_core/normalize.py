"""Small deterministic normalization helpers shared by parser layers."""

from __future__ import annotations

import re


_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]{2,}")
_STOPWORDS = frozenset(
    "a an and are as at be by for from in into is it of on or that the their this to was with"
    .split()
)


def normalize_text(value: str) -> str:
    """Normalize whitespace and case without changing source text records."""

    return " ".join(str(value or "").casefold().split())


def root_token(token: str) -> str:
    """Apply a deliberately small suffix reduction for context matching."""

    return re.sub(r"(ingly|edly|ing|ed|es|s)$", "", token, flags=re.IGNORECASE)


def token_set(value: str, *, remove_stopwords: bool = True, roots: bool = False) -> set[str]:
    """Return inspectable lexical tokens; this is not a semantic parser."""

    tokens = {token.casefold() for token in _TOKEN_RE.findall(str(value or ""))}
    if remove_stopwords:
        tokens.difference_update(_STOPWORDS)
    if roots:
        tokens = {root_token(token) for token in tokens}
    return tokens
