"""Create a deterministic source manifest for the successor project."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


MANIFEST_NAME = "DEVELOPMENT_MANIFEST.json"
IGNORED_PARTS = frozenset({"__pycache__", ".venv", "build", "dist"})


def members(root: Path) -> list[Path]:
    result = []
    for path in root.rglob("*"):
        if not path.is_file() or path.name == MANIFEST_NAME:
            continue
        relative = path.relative_to(root)
        if any(part in IGNORED_PARTS or part.endswith(".egg-info") for part in relative.parts):
            continue
        if path.suffix == ".pyc":
            continue
        result.append(path)
    return sorted(result, key=lambda item: item.relative_to(root).as_posix())


def main() -> None:
    root = Path(__file__).resolve().parent
    output = root / MANIFEST_NAME
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to replace existing manifest: {output}")
    records = []
    for path in members(root):
        data = path.read_bytes()
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size": len(data),
                "sha256": sha256(data).hexdigest(),
            }
        )
    document = {
        "schema": "nlp-successor-manifest/1",
        "project": "nlp-offline-interpreter/0.1",
        "status": "development",
        "authority_effect": "NONE",
        "production_ready": False,
        "member_count": len(records),
        "members": records,
    }
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"manifest": str(output), "members": len(records)}, sort_keys=True))


if __name__ == "__main__":
    main()
