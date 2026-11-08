"""Verify exact members recorded by PACKAGE_MANIFEST.json."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import sys


def main() -> int:
    root = Path(__file__).resolve().parent
    manifest_path = root / "PACKAGE_MANIFEST.json"
    if not manifest_path.is_file():
        print("PACKAGE_MANIFEST.json is missing", file=sys.stderr)
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    seen: set[str] = set()
    for item in manifest.get("members", []):
        name = item.get("path", "")
        pure = PurePosixPath(name)
        if not name or pure.is_absolute() or ".." in pure.parts or name in seen:
            errors.append(f"unsafe or duplicate manifest path: {name!r}")
            continue
        seen.add(name)
        path = root.joinpath(*pure.parts)
        if not path.is_file():
            errors.append(f"missing: {name}")
            continue
        data = path.read_bytes()
        if len(data) != item.get("size"):
            errors.append(f"size mismatch: {name}")
        if sha256(data).hexdigest() != item.get("sha256"):
            errors.append(f"hash mismatch: {name}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"verified {len(seen)} manifest members")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
