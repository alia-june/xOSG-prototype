"""Capability routing that preserves ambiguity instead of selecting silently."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .base import TaskModule, TaskRequest, TaskResult


@dataclass(frozen=True)
class ModuleMatch:
    module_id: str
    score: float


@dataclass(frozen=True)
class RouteResult:
    request: TaskRequest
    matches: tuple[ModuleMatch, ...]
    results: tuple[TaskResult, ...]
    status: str


def route_request(request: TaskRequest, modules: Iterable[TaskModule], *, threshold: float = 0.25) -> RouteResult:
    module_list = tuple(modules)
    scored = [(module, module.score(request)) for module in module_list]
    matches = sorted(
        (ModuleMatch(module.module_id, score) for module, score in scored if score >= threshold),
        key=lambda match: (-match.score, match.module_id),
    )
    module_by_id = {module.module_id: module for module in module_list}
    results = tuple(module_by_id[match.module_id].analyze(request) for match in matches)
    if not matches:
        status = "unmatched"
    elif len(matches) == 1 or matches[0].score > matches[1].score:
        status = "candidate-route"
    else:
        status = "collision-review"
    return RouteResult(request, tuple(matches), results, status)
