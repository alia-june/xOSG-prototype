"""Create an exact, non-overwriting manifest for the P04 wheelhouse."""

from __future__ import annotations

from email.parser import Parser
from hashlib import sha256
import json
from pathlib import Path
import sys
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parent
WHEELHOUSE = ROOT / "wheelhouse"
OUTPUT = ROOT / "WHEELHOUSE_MANIFEST.json"


def metadata(path: Path) -> tuple[str, str, str | None]:
    with ZipFile(path) as archive:
        names = [
            name
            for name in archive.namelist()
            if name.endswith(".dist-info/METADATA") and name.count("/") == 1
        ]
        if len(names) != 1:
            raise ValueError(f"wheel must contain one METADATA member: {path.name}")
        parsed = Parser().parsestr(archive.read(names[0]).decode("utf-8"))
    name = parsed.get("Name")
    version = parsed.get("Version")
    if not name or not version:
        raise ValueError(f"wheel metadata lacks name or version: {path.name}")
    return name, version, parsed.get("Requires-Python")


def main() -> int:
    if OUTPUT.exists() or OUTPUT.is_symlink():
        print(f"refusing to replace existing manifest: {OUTPUT}", file=sys.stderr)
        return 2
    try:
        wheels = sorted(WHEELHOUSE.glob("*.whl"), key=lambda item: item.name.casefold())
        if not wheels:
            raise ValueError("wheelhouse contains no wheels")
        records = []
        for wheel in wheels:
            name, version, requires_python = metadata(wheel)
            normalized = name.lower().replace("_", "-")
            data = wheel.read_bytes()
            records.append(
                {
                    "path": f"wheelhouse/{wheel.name}",
                    "package": normalized,
                    "version": version,
                    "requires_python": requires_python,
                    "size": len(data),
                    "sha256": sha256(data).hexdigest(),
                }
            )
    except (OSError, BadZipFile, UnicodeError, ValueError) as exc:
        print(f"wheelhouse inventory failed: {exc}", file=sys.stderr)
        return 1
    document = {
        "schema": "nlp-p04-wheelhouse-manifest/1",
        "status": "generated-staging-evidence",
        "authority_effect": "NONE",
        "production_ready": False,
        "runtime": "CPython 3.11-3.14 Windows x86-64 wheel set",
        "wheel_count": len(records),
        "wheels": records,
    }
    with OUTPUT.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"manifest": str(OUTPUT), "wheels": len(records)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
