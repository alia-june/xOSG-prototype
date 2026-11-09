"""Small, inspectable helpers for UniMorph-style feature strings."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping, Any


FEATURE_LABELS = {
    "N": "noun", "V": "verb", "ADJ": "adjective", "ADV": "adverb",
    "SG": "singular", "PL": "plural", "PST": "past", "PRS": "present",
    "PTCP": "participle", "INF": "infinitive", "NFIN": "nonfinite",
    "IMP": "imperative", "SBJV": "subjunctive", "1": "first person",
    "2": "second person", "3": "third person", "COMP": "comparative",
    "SPRL": "superlative",
}


def parse_features(features: str | Iterable[str]) -> tuple[str, ...]:
    if isinstance(features, str):
        parts = features.replace("|", ";").split(";")
    else:
        parts = list(features)
    return tuple(part.strip() for part in parts if part and part.strip())


def describe_features(features: str | Iterable[str]) -> tuple[str, ...]:
    return tuple(FEATURE_LABELS.get(feature, feature.casefold().replace(".", " ")) for feature in parse_features(features))


def group_forms(rows: Iterable[Mapping[str, Any]]) -> dict[str, tuple[Mapping[str, Any], ...]]:
    """Group inflection rows by lemma while retaining every form record."""

    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        lemma = str(row.get("lemma", "")).strip()
        if lemma:
            grouped[lemma].append(row)
    return {lemma: tuple(values) for lemma, values in sorted(grouped.items())}
