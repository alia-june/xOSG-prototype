"""Safe proposal layer for axioms, rules, and expert-system checks."""

from __future__ import annotations

import re

from ..normalize import normalize_text
from .base import TaskProposal, TaskRequest, TaskResult


class ExpertControlModule:
    module_id = "expert-control"
    _RULE = re.compile(r"^if (?P<premise>.+?) then (?P<conclusion>.+)$", re.IGNORECASE)

    def score(self, request: TaskRequest) -> float:
        text = normalize_text(request.text)
        if self._RULE.match(text):
            return 1.0
        if text.startswith(("axiom ", "assert ", "rule ", "prove ", "check ")):
            return 0.9
        return 0.0

    def analyze(self, request: TaskRequest) -> TaskResult:
        text = normalize_text(request.text)
        match = self._RULE.match(text)
        if match:
            fields = {"kind": "rule", "premise": match.group("premise"), "conclusion": match.group("conclusion")}
            operation = "propose-rule"
        else:
            kind, _, body = text.partition(" ")
            fields = {"kind": kind or "unknown", "body": body}
            operation = "propose-axiom" if kind == "axiom" else "propose-check"
        proposal = TaskProposal(self.module_id, operation, fields, evidence=("controlled-English pattern",), status="proposal-only")
        return TaskResult(self.module_id, (proposal,), ("No rule was accepted or executed.",))
