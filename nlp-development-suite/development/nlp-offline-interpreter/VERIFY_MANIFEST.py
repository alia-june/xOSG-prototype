"""Verify the exact non-generated source set in DEVELOPMENT_MANIFEST.json."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import sys

from BUILD_MANIFEST import MANIFEST_NAME, members


def main() -> int:
    root = Path(__file__).resolve().parent
    manifest_path = root / MANIFEST_NAME
    try:
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"manifest load failed: {exc}", file=sys.stderr)
        return 2
    errors: list[str] = []
    if document.get("schema") != "nlp-successor-manifest/1":
        errors.append("unexpected manifest schema")
    if document.get("authority_effect") != "NONE" or document.get("production_ready") is not False:
        errors.append("manifest authority boundary changed")

    listed: dict[str, dict[str, object]] = {}
    for item in document.get("members", []):
        name = item.get("path") if isinstance(item, dict) else None
        if not isinstance(name, str):
            errors.append("manifest member path is invalid")
            continue
        pure = PurePosixPath(name)
        if pure.is_absolute() or ".." in pure.parts or name in listed:
            errors.append(f"unsafe or duplicate manifest path: {name!r}")
            continue
        listed[name] = item

    actual = {path.relative_to(root).as_posix(): path for path in members(root)}
    for missing in sorted(set(listed) - set(actual)):
        errors.append(f"missing member: {missing}")
    for extra in sorted(set(actual) - set(listed)):
        errors.append(f"unlisted member: {extra}")
    for name in sorted(set(listed) & set(actual)):
        data = actual[name].read_bytes()
        if listed[name].get("size") != len(data):
            errors.append(f"size mismatch: {name}")
        if listed[name].get("sha256") != sha256(data).hexdigest():
            errors.append(f"hash mismatch: {name}")
    if document.get("member_count") != len(listed):
        errors.append("manifest member_count does not match listed members")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(json.dumps({"status": "passed", "members": len(listed)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
