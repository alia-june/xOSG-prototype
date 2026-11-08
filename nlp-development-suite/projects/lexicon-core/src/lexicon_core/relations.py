"""Bounded relation traversal for semantic and lexical graphs."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class RelationNode:
    node: str
    depth: int
    relation: str
    parent: str


@dataclass(frozen=True)
class TraversalResult:
    nodes: tuple[RelationNode, ...]
    truncated: bool


def _edge_parts(edge: Any) -> tuple[str, str]:
    if isinstance(edge, Mapping):
        return str(edge.get("target", "")), str(edge.get("relation", "related"))
    if isinstance(edge, (tuple, list)) and len(edge) >= 2:
        return str(edge[0]), str(edge[1])
    return str(edge), "related"


def traverse_relations(
    start: str,
    adjacency: Mapping[str, Iterable[Any]],
    *,
    max_depth: int = 5,
    per_level_limit: int = 20,
    total_limit: int = 100,
) -> TraversalResult:
    """Traverse a graph with explicit depth and node bounds."""

    if not 1 <= max_depth <= 5:
        raise ValueError("max_depth must be between 1 and 5")
    if per_level_limit < 1 or total_limit < 1:
        raise ValueError("relation limits must be positive")
    queue = deque([(start, 0)])
    visited = {start}
    output: list[RelationNode] = []
    truncated = False
    while queue:
        parent, depth = queue.popleft()
        if depth >= max_depth:
            continue
        added_this_level = 0
        for raw_edge in adjacency.get(parent, ()):
            target, relation = _edge_parts(raw_edge)
            if not target or target in visited:
                continue
            if added_this_level >= per_level_limit or len(output) >= total_limit:
                truncated = True
                break
            visited.add(target)
            node = RelationNode(target, depth + 1, relation, parent)
            output.append(node)
            queue.append((target, depth + 1))
            added_this_level += 1
        if len(output) >= total_limit:
            truncated = True
            break
    return TraversalResult(tuple(output), truncated)
