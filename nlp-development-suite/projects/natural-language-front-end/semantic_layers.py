"""Session history and optional proposal providers; none dispatch file operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from command_aliases import Candidate


ProposalProvider = Callable[[str], list[dict[str, Any]]]
MAX_HISTORY = 100
MAX_PROVIDER_PROPOSALS = 8


def _display_safe(value: str) -> bool:
    return not any(ord(character) < 32 or ord(character) == 127 for character in value)


def _key(source: str) -> str:
    return " ".join(source.casefold().split())


@dataclass
class SessionHistory:
    """Records explicit user choices in one REPL session; never authorizes execution."""

    choices: dict[str, tuple[str, dict[str, str]]] = field(default_factory=dict)

    def record_choice(self, original: str, capability: str, arguments: dict[str, str]) -> None:
        key = _key(original)
        if key not in self.choices and len(self.choices) >= MAX_HISTORY:
            self.choices.pop(next(iter(self.choices)))
        self.choices[key] = (capability, dict(arguments))

    def prior_choice(self, source: str) -> tuple[str, dict[str, str]] | None:
        return self.choices.get(_key(source))

    def rerank(self, source: str, candidates: tuple[Candidate, ...]) -> tuple[Candidate, ...]:
        prior = self.prior_choice(source)
        if prior is None:
            return candidates
        ranked = []
        for candidate in candidates:
            if candidate.capability == prior[0] and candidate.arguments == prior[1]:
                ranked.append(Candidate(candidate.capability, candidate.arguments,
                                        candidate.score + 20, candidate.rule_id,
                                        candidate.evidence + ("session_history_choice",)))
            else:
                ranked.append(candidate)
        return tuple(sorted(ranked, key=lambda c: (-c.score, c.capability, c.rule_id)))

    def suggest(self, source: str) -> tuple[Candidate, ...]:
        prior = self.prior_choice(source)
        if prior is None:
            return ()
        capability, arguments = prior
        return (Candidate(capability, dict(arguments), 50, "session_history",
                          ("session_history_choice",)),)


def validate_provider_proposals(source: str, provider: ProposalProvider,
                                *, layer: str,
                                capabilities: dict[str, tuple[str, ...]]) -> tuple[Candidate, ...]:
    """Normalize untrusted web/LLM outputs to non-executing typed suggestions."""
    records = provider(source)
    if not isinstance(records, list) or len(records) > MAX_PROVIDER_PROPOSALS:
        raise ValueError(f"{layer} provider returned an invalid proposal list")
    candidates = []
    seen = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict) or set(record) != {"capability", "arguments", "source"}:
            raise ValueError(f"{layer} proposal has invalid fields")
        capability = record["capability"]
        arguments = record["arguments"]
        citation = record["source"]
        if not isinstance(capability, str) or capability not in capabilities:
            raise ValueError(f"{layer} proposal names an unknown capability")
        if not isinstance(arguments, dict) or set(arguments) != set(capabilities[capability]) or not all(
                isinstance(k, str) and isinstance(v, str) and 0 < len(v) <= 1024 and _display_safe(v)
                for k, v in arguments.items()):
            raise ValueError(f"{layer} proposal has invalid arguments")
        if not isinstance(citation, str) or not citation or len(citation) > 500 or not _display_safe(citation):
            raise ValueError(f"{layer} proposal has invalid source")
        if layer == "web" and not citation.startswith("https://"):
            raise ValueError("Web proposal requires an HTTPS source URL")
        key = (capability, tuple(sorted(arguments.items())))
        if key in seen:
            continue
        seen.add(key)
        candidates.append(Candidate(capability, dict(arguments), 35 if layer == "web" else 20,
                                    f"{layer}_proposal_{index + 1}",
                                    (f"source_layer:{layer}", f"source:{citation}",
                                     "unverified_proposal")))
    return tuple(sorted(candidates, key=lambda c: (-c.score, c.capability, c.rule_id)))
