"""Deterministic ranking of source-labeled lexical candidates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Any

from .normalize import root_token, token_set


SOURCE_WEIGHTS = {"Open English WordNet": 5, "Wiktionary": 3, "GCIDE": 2}


@dataclass(frozen=True)
class Candidate:
    source: str
    reference: str
    definition: str
    part_of_speech: str = "entry"
    example: str = ""
    weight: int = 1
    score: int = 0
    agreement: int = 0
    context_match: int = 0


@dataclass(frozen=True)
class SynthesisResult:
    candidates: tuple[Candidate, ...]
    ranked: tuple[Candidate, ...]
    cues: tuple[str, ...]
    proposal: str


def _candidate(raw: Mapping[str, Any]) -> Candidate:
    source = str(raw.get("source", "unknown"))
    return Candidate(
        source=source,
        reference=str(raw.get("reference", raw.get("ref", "unspecified"))),
        definition=str(raw.get("definition", "")),
        part_of_speech=str(raw.get("part_of_speech", raw.get("pos", "entry"))),
        example=str(raw.get("example", "")),
        weight=int(raw.get("weight", SOURCE_WEIGHTS.get(source, 1))),
    )


def synthesize(term: str, records: Iterable[Mapping[str, Any]], context: str = "") -> SynthesisResult:
    """Rank records without merging them or asserting a selected meaning."""

    candidates = tuple(candidate for candidate in (_candidate(record) for record in records) if candidate.definition)
    context_tokens = {root_token(token) for token in token_set(context, roots=False)}
    context_tokens.discard(root_token(str(term).casefold()))
    token_sets = [token_set(candidate.definition) for candidate in candidates]
    ranked: list[Candidate] = []
    for index, candidate in enumerate(candidates):
        agreement = 0
        for other_index, other in enumerate(token_sets):
            if index == other_index:
                continue
            agreement += min(sum(token in other for token in token_sets[index]), 4)
        candidate_roots = {root_token(token) for token in token_sets[index]}
        context_match = sum(token in candidate_roots for token in context_tokens)
        score = candidate.weight * 10 + min(agreement, 12) + context_match * 7
        ranked.append(Candidate(**{**candidate.__dict__, "score": score, "agreement": agreement, "context_match": context_match}))
    ranked.sort(key=lambda item: (-item.score, item.source, item.reference))
    cue_counts: dict[str, int] = {}
    for candidate in ranked[:12]:
        for token in token_set(candidate.definition):
            cue_counts[token] = cue_counts.get(token, 0) + 1
    cues = tuple(sorted((token for token, count in cue_counts.items() if count > 1), key=lambda token: (-cue_counts[token], token))[:8])
    if ranked:
        best = ranked[0]
        proposal = f"The leading lexical candidate is “{best.definition}” ({best.source}, {best.part_of_speech})."
        if context.strip():
            proposal = f"In the supplied context, the leading lexical candidate is “{best.definition}” ({best.source}, {best.part_of_speech})."
    else:
        proposal = "No lexical candidate is attached for this spelling."
    return SynthesisResult(candidates, tuple(ranked), cues, proposal)
