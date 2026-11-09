"""Deterministic ELIZA NXT conversation adapter without an AI provider."""

from __future__ import annotations

import re

from ..normalize import normalize_text
from .base import TaskProposal, TaskRequest, TaskResult


REFLECTIONS = {"i": "you", "me": "you", "my": "your", "mine": "yours", "am": "are", "you": "I", "your": "my"}


def _reflect(value: str) -> str:
    return " ".join(REFLECTIONS.get(word, word) for word in value.split())


class ElizaNxtModule:
    module_id = "eliza-nxt"

    def score(self, request: TaskRequest) -> float:
        text = normalize_text(request.text)
        if text.startswith(("hello", "hi", "i ", "i'm ", "i am ", "because ", "why ", "you ")):
            return 0.8
        return 0.15 if text else 0.0

    def respond(self, text: str) -> str:
        normalized = normalize_text(text)
        patterns = (
            (r"^i feel (.+)$", lambda match: f"Why do you feel {_reflect(match.group(1))}?"),
            (r"^i am (.+)$", lambda match: f"How long have you been {_reflect(match.group(1))}?"),
            (r"^i need (.+)$", lambda match: f"What would it mean to you if you had {_reflect(match.group(1))}?"),
            (r"^because (.+)$", lambda match: f"What makes you think {_reflect(match.group(1))}?"),
            (r"^why (.+)$", lambda match: f"What do you think is the reason {_reflect(match.group(1))}?"),
        )
        for pattern, handler in patterns:
            match = re.match(pattern, normalized, re.IGNORECASE)
            if match:
                return handler(match)
        return "Please continue."

    def analyze(self, request: TaskRequest) -> TaskResult:
        response = self.respond(request.text)
        proposal = TaskProposal(self.module_id, "respond", {"text": response, "deterministic": True}, evidence=("ELIZA NXT pattern response",), status="generated-response")
        return TaskResult(self.module_id, (proposal,))
