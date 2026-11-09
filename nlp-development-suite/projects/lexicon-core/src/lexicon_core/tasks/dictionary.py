"""Dictionary and lexical-evidence task adapter."""

from __future__ import annotations

from ..intent import parse_intent
from ..normalize import normalize_text
from .base import TaskProposal, TaskRequest, TaskResult


class DictionaryModule:
    module_id = "dictionary"

    def score(self, request: TaskRequest) -> float:
        words = normalize_text(request.text).split()
        if not words:
            return 0.0
        if words[0] in {"define", "definition", "meaning", "explain"}:
            return 1.0
        if words[0] in {"word", "dictionary", "lookup"}:
            return 0.85
        return 0.0

    def analyze(self, request: TaskRequest) -> TaskResult:
        intent = parse_intent(request.text)
        term = intent.query.strip() or normalize_text(request.text)
        proposal = TaskProposal(
            self.module_id,
            "lookup",
            {"term": term, "sources": tuple(request.metadata.get("sources", ("oewn", "wiktionary", "gcide")))},
            evidence=("deterministic dictionary intent",),
        )
        return TaskResult(self.module_id, (proposal,))
