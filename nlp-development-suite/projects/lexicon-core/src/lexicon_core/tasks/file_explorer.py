"""Proposal-only file explorer intent adapter."""

from __future__ import annotations

from pathlib import PurePath

from ..intent import parse_intent
from ..normalize import normalize_text
from .base import TaskProposal, TaskRequest, TaskResult


class FileExplorerModule:
    module_id = "file-explorer"

    def score(self, request: TaskRequest) -> float:
        words = set(normalize_text(request.text).split())
        if words & {"file", "files", "folder", "folders", "directory", "directories"}:
            return 0.95
        if words & {"find", "search", "locate", "list"}:
            return 0.45
        return 0.0

    def analyze(self, request: TaskRequest) -> TaskResult:
        normalized = normalize_text(request.text)
        intent = parse_intent(normalized)
        words = normalized.split()
        path_hint = request.metadata.get("path", ".")
        safe_path = str(PurePath(str(path_hint)))
        operation = "search" if intent.operation == "search" else "list"
        query = intent.query if intent.query != normalized else ""
        proposal = TaskProposal(
            self.module_id,
            operation,
            {"path": safe_path, "query": query, "recursive": "recursive" in words, "execute": False},
            evidence=("file-family lexical pattern", "filesystem access not performed"),
        )
        return TaskResult(self.module_id, (proposal,))
