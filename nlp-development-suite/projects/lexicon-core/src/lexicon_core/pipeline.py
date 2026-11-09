"""Small orchestration layer joining independent proposal modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .collisions import CollisionGroup, group_records
from .intent import IntentProposal, parse_intent
from .synthesis import SynthesisResult, synthesize


@dataclass(frozen=True)
class AnalysisResult:
    normalized_text: str
    intent: IntentProposal
    collisions: tuple[CollisionGroup, ...]
    synthesis: SynthesisResult | None


def analyze_text(
    text: str,
    *,
    records: Iterable[Mapping[str, Any]] = (),
    context: str = "",
) -> AnalysisResult:
    record_list = tuple(records)
    intent = parse_intent(text)
    synthesis = synthesize(text, record_list, context) if record_list else None
    return AnalysisResult(
        normalized_text=" ".join(text.casefold().split()),
        intent=intent,
        collisions=group_records(record_list),
        synthesis=synthesis,
    )
