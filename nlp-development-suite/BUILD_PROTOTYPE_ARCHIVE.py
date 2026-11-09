"""Build a deterministic ZIP from a verified prototype repository tree."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import shutil
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo


STORED_SUFFIXES = {".jpg", ".jpeg", ".png", ".woff", ".woff2"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest_path = root / "PROTOTYPE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output = (args.output or root.with_suffix(".zip")).resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to replace existing archive: {output}")
    members: list[tuple[Path, str]] = []
    for item in manifest["members"]:
        pure = PurePosixPath(item["path"])
        if pure.is_absolute() or ".." in pure.parts:
            raise ValueError(f"Unsafe manifest path: {item['path']!r}")
        path = root.joinpath(*pure.parts)
        data = path.read_bytes()
        if len(data) != item["bytes"] or sha256(data).hexdigest() != item["sha256"]:
            raise ValueError(f"Manifest mismatch: {item['path']}")
        members.append((path, item["path"]))
    members.append((manifest_path, "PROTOTYPE_MANIFEST.json"))
    with ZipFile(output, "x", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path, relative in sorted(members, key=lambda item: item[1]):
            info = ZipInfo(f"{root.name}/{relative}", date_time=(2026, 11, 8, 0, 0, 0))
            info.compress_type = ZIP_STORED if path.suffix.casefold() in STORED_SUFFIXES else ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with path.open("rb") as source, archive.open(info, "w") as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)
    print(json.dumps({
        "archive": str(output),
        "bytes": output.stat().st_size,
        "members": len(members),
        "sha256": sha256(output.read_bytes()).hexdigest(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
