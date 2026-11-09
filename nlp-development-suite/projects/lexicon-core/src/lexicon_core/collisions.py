"""Visible grouping for spelling collisions across lexical sources."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .normalize import normalize_text


@dataclass(frozen=True)
class CollisionGroup:
    term: str
    records: tuple[Mapping[str, Any], ...]
    sources: tuple[str, ...]

    @property
    def collision(self) -> bool:
        return len(self.records) > 1 or len(self.sources) > 1


def group_records(records: Iterable[Mapping[str, Any]], term_key: str = "term") -> tuple[CollisionGroup, ...]:
    """Group records by normalized spelling without dropping any row."""

    grouped: dict[str, list[Mapping[str, Any]]] = {}
    sources: dict[str, list[str]] = {}
    for record in records:
        term = normalize_text(str(record.get(term_key, "")))
        if not term:
            continue
        grouped.setdefault(term, []).append(record)
        source = str(record.get("source", "unknown"))
        if source not in sources.setdefault(term, []):
            sources[term].append(source)
    return tuple(
        CollisionGroup(term, tuple(grouped[term]), tuple(sources[term]))
        for term in sorted(grouped)
    )
