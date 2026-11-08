"""Shared task-module contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class TaskRequest:
    text: str
    context: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaskProposal:
    module_id: str
    operation: str
    fields: Mapping[str, Any]
    evidence: tuple[str, ...] = ()
    status: str = "proposal-only"


@dataclass(frozen=True)
class TaskResult:
    module_id: str
    proposals: tuple[TaskProposal, ...]
    diagnostics: tuple[str, ...] = ()


class TaskModule(Protocol):
    module_id: str

    def score(self, request: TaskRequest) -> float:
        """Return a routing score between 0 and 1 without performing work."""

    def analyze(self, request: TaskRequest) -> TaskResult:
        """Return inspectable proposals; this method must not execute actions."""
