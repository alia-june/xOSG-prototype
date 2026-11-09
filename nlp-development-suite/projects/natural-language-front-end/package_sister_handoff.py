"""Package and independently verify a local unresolved sister handoff."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def package_handoff(directory: Path, output: Path) -> dict:
    if output.exists() or output.is_symlink():
        raise FileExistsError("Package output already exists")
    manifest_data = (directory / "manifest.json").read_bytes()
    manifest = json.loads(manifest_data)
    if manifest["execution_allowed"] or manifest["accepted_by_sister_machine"]:
        raise ValueError("This packager only accepts unresolved local handoffs")
    files = {"manifest.json": manifest_data}
    for record in manifest["documents"]:
        name = record["name"]
        if not isinstance(name, str) or re.fullmatch(r"meaning_[0-9]{4}\.json", name) is None or name in files:
            raise ValueError(f"Unsafe or duplicate package member: {name!r}")
        data = (directory / name).read_bytes()
        if sha256(data).hexdigest() != record["sha256"]:
            raise ValueError(f"Meaning document digest differs: {name}")
        files[name] = data

    stage = output.with_name(output.name + f".stage-{uuid4().hex}")
    with ZipFile(stage, "w", compression=ZIP_DEFLATED, compresslevel=9) as package:
        for name in sorted(files):
            info = ZipInfo(name, date_time=(2026, 9, 16, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            package.writestr(info, files[name], compress_type=ZIP_DEFLATED, compresslevel=9)
    with ZipFile(stage) as package:
        if set(package.namelist()) != set(files) or len(package.infolist()) != len(files):
            raise ValueError(f"Packaged member set differs; staged archive retained at {stage}")
        for name, expected in files.items():
            if package.read(name) != expected:
                raise ValueError(f"Packaged bytes differ for {name}; staged archive retained at {stage}")
    os.link(stage, output)
    stage.unlink()
    return {"output": str(output), "sha256": sha256(output.read_bytes()).hexdigest(),
            "members": len(files), "meaning_documents": len(manifest["documents"])}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(package_handoff(args.directory, args.output)))


if __name__ == "__main__":
    main()
