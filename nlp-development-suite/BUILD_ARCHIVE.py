"""Build a deterministic ZIP from the verified development export."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import shutil
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo


STORED_SUFFIXES = {".gz", ".zip", ".whl", ".png", ".jpg", ".jpeg", ".woff", ".woff2"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    manifest_path = root / "PACKAGE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output = (args.output or root.with_suffix(".zip")).resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to replace existing archive: {output}")

    members: list[Path] = []
    for item in manifest["members"]:
        pure = PurePosixPath(item["path"])
        if pure.is_absolute() or ".." in pure.parts:
            raise ValueError(f"Unsafe manifest path: {item['path']!r}")
        path = root.joinpath(*pure.parts)
        data_hash = sha256(path.read_bytes()).hexdigest()
        if path.stat().st_size != item["size"] or data_hash != item["sha256"]:
            raise ValueError(f"Manifest mismatch: {item['path']}")
        members.append(path)
    members.append(manifest_path)

    prefix = root.name
    with ZipFile(output, "x", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(members):
            relative = path.relative_to(root).as_posix()
            info = ZipInfo(f"{prefix}/{relative}", date_time=(2026, 9, 28, 0, 0, 0))
            info.compress_type = ZIP_STORED if path.suffix.lower() in STORED_SUFFIXES else ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with path.open("rb") as source, archive.open(info, "w") as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)

    print(json.dumps({
        "archive": str(output),
        "size": output.stat().st_size,
        "sha256": sha256(output.read_bytes()).hexdigest(),
        "members": len(members),
    }))


if __name__ == "__main__":
    main()
