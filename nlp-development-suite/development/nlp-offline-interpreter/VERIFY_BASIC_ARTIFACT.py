"""Verify path safety, exact membership, hashes, and wheel contents of a basic ZIP."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import stat
import sys
from zipfile import BadZipFile, ZipFile


REQUIRED_WHEEL_MEMBERS = {
    "nlp_offline_interpreter/basic.py",
    "nlp_offline_interpreter/__main__.py",
    "nlp_offline_interpreter/integration.py",
    "nlp_offline_interpreter-0.1.0.dist-info/entry_points.txt",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    try:
        with ZipFile(args.artifact) as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            folded: set[str] = set()
            for info in infos:
                name = info.filename
                pure = PurePosixPath(name)
                mode = info.external_attr >> 16
                if (
                    not name
                    or "\\" in name
                    or pure.is_absolute()
                    or ".." in pure.parts
                    or name.endswith("/")
                ):
                    errors.append(f"unsafe member path: {name!r}")
                if name.casefold() in folded:
                    errors.append(f"duplicate or case-colliding member: {name!r}")
                folded.add(name.casefold())
                if stat.S_ISLNK(mode):
                    errors.append(f"symbolic link is forbidden: {name!r}")
            if len(names) != len(set(names)):
                errors.append("duplicate member path")
            try:
                manifest = json.loads(archive.read("ARTIFACT_MANIFEST.json"))
            except (KeyError, UnicodeError, json.JSONDecodeError) as exc:
                errors.append(f"manifest load failed: {exc}")
                manifest = {}
            if manifest.get("schema") != "nlp-basic-download-manifest/1":
                errors.append("unexpected artifact manifest schema")
            if (
                manifest.get("approver_required") is not False
                or manifest.get("authority_effect") != "NONE"
                or manifest.get("production_ready") is not False
                or manifest.get("execution_allowed") is not False
            ):
                errors.append("artifact boundary changed")

            listed: dict[str, dict[str, object]] = {}
            for item in manifest.get("members", []):
                name = item.get("path") if isinstance(item, dict) else None
                if not isinstance(name, str) or name in listed:
                    errors.append(f"invalid or duplicate manifest path: {name!r}")
                    continue
                listed[name] = item
            expected = set(listed) | {"ARTIFACT_MANIFEST.json"}
            if set(names) != expected:
                errors.append("ZIP membership does not exactly match artifact manifest")
            if manifest.get("member_count") != len(listed):
                errors.append("manifest member_count mismatch")
            for name, item in listed.items():
                try:
                    data = archive.read(name)
                except KeyError:
                    continue
                if item.get("size") != len(data):
                    errors.append(f"size mismatch: {name}")
                if item.get("sha256") != sha256(data).hexdigest():
                    errors.append(f"hash mismatch: {name}")

            try:
                checksum_lines = archive.read("SHA256SUMS.txt").decode("utf-8").splitlines()
                checksum_entries: dict[str, str] = {}
                for line in checksum_lines:
                    digest, separator, name = line.partition("  ")
                    if (
                        separator != "  "
                        or len(digest) != 64
                        or any(character not in "0123456789abcdef" for character in digest)
                        or not name
                        or name in checksum_entries
                    ):
                        raise ValueError(f"invalid checksum line: {line!r}")
                    checksum_entries[name] = digest
                expected_checksums = {
                    name: str(item.get("sha256"))
                    for name, item in listed.items()
                    if name != "SHA256SUMS.txt"
                }
                if checksum_entries != expected_checksums:
                    errors.append("SHA256SUMS.txt does not match the artifact manifest")
            except (KeyError, UnicodeError, ValueError) as exc:
                errors.append(f"checksum list validation failed: {exc}")

            wheel_names = [name for name in listed if name.startswith("wheel/")]
            if len(wheel_names) != 1 or not wheel_names[0].endswith(".whl"):
                errors.append("artifact must contain exactly one wheel")
            elif wheel_names[0] in names:
                from io import BytesIO

                with ZipFile(BytesIO(archive.read(wheel_names[0]))) as wheel:
                    missing = REQUIRED_WHEEL_MEMBERS - set(wheel.namelist())
                    if missing:
                        errors.append(f"wheel members missing: {sorted(missing)}")
    except (OSError, BadZipFile) as exc:
        print(f"artifact load failed: {exc}", file=sys.stderr)
        return 2

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "passed",
                "artifact": str(args.artifact.resolve()),
                "size": args.artifact.stat().st_size,
                "sha256": sha256(args.artifact.read_bytes()).hexdigest(),
                "members": len(names),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
