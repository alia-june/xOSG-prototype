"""Access to the shared machine-local dictionary registry."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path.home() / "Documents" / "Workbench" / "Lexicon Data"
REGISTRY_NAME = "registry.json"


@dataclass(frozen=True)
class SourceRecord:
    """A registered source with provenance metadata and a relative path."""

    source_id: str
    path: Path
    metadata: dict[str, Any]


def registry_root(root: str | Path | None = None) -> Path:
    value = root or os.environ.get("LEXICON_DATA_ROOT") or DEFAULT_ROOT
    return Path(value).expanduser().resolve()


def load_registry(root: str | Path | None = None) -> dict[str, Any]:
    base = registry_root(root)
    registry_path = base / REGISTRY_NAME
    if not registry_path.is_file():
        raise FileNotFoundError(f"Shared lexicon registry not found: {registry_path}")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("schema") != "lexicon-atlas-registry/1":
        raise ValueError(f"Unsupported lexicon registry schema: {registry.get('schema')!r}")
    registry["_root"] = str(base)
    return registry


def source_record(source_id: str, registry: dict[str, Any] | None = None) -> SourceRecord:
    registry = registry or load_registry()
    metadata = registry.get("sources", {}).get(source_id)
    if not metadata:
        raise KeyError(f"Source is not registered: {source_id}")
    base = registry_root(registry.get("_root"))
    relative = Path(metadata["path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Registry path escapes shared root: {source_id}")
    # Junctions intentionally resolve to the existing verified source roots.
    path = (base / relative).resolve()
    return SourceRecord(source_id, path, dict(metadata))


def source_path(source_id: str, registry: dict[str, Any] | None = None) -> Path:
    return source_record(source_id, registry).path


def inventory(root: str | Path | None = None) -> dict[str, dict[str, Any]]:
    registry = load_registry(root)
    result: dict[str, dict[str, Any]] = {}
    for source_id in registry.get("sources", {}):
        record = source_record(source_id, registry)
        result[source_id] = {
            "path": str(record.path),
            "exists": record.path.exists(),
            "is_file": record.path.is_file(),
            "is_directory": record.path.is_dir(),
            "metadata": record.metadata,
        }
    return result
