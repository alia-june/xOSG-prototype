"""Build a deterministic, self-verifying ZIP around an already-built wheel."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parent
FIXED_EPOCH = 1_704_067_200
PAYLOAD_FILES = {
    "BASIC_ARTIFACT_README.md": ROOT / "BASIC_ARTIFACT_README.md",
    "BUILD_VALIDATION.json": ROOT / "BUILD_VALIDATION.json",
    "DEVELOPMENT_MANIFEST.json": ROOT / "DEVELOPMENT_MANIFEST.json",
    "schemas/generic-interpretation-v1.schema.json": (
        ROOT / "schemas" / "generic-interpretation-v1.schema.json"
    ),
}


def zip_info(name: str, epoch: int) -> ZipInfo:
    instant = datetime.fromtimestamp(max(epoch, 315_532_800), timezone.utc)
    info = ZipInfo(name, instant.timetuple()[:6])
    info.compress_type = ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    wheel = args.wheel.resolve()
    output = args.output.resolve()
    if not wheel.is_file() or wheel.suffix != ".whl":
        parser.error("--wheel must identify an existing .whl file")
    if output.exists() or output.is_symlink():
        parser.error(f"refusing to replace existing output: {output}")
    if not output.parent.is_dir():
        parser.error(f"output parent does not exist: {output.parent}")

    payload: dict[str, bytes] = {}
    for name, path in PAYLOAD_FILES.items():
        payload[name] = path.read_bytes()
    payload[f"wheel/{wheel.name}"] = wheel.read_bytes()

    records = [
        {"path": name, "size": len(data), "sha256": sha256(data).hexdigest()}
        for name, data in sorted(payload.items())
    ]
    sums = "".join(f"{item['sha256']}  {item['path']}\n" for item in records).encode(
        "utf-8"
    )
    payload["SHA256SUMS.txt"] = sums
    records.append(
        {
            "path": "SHA256SUMS.txt",
            "size": len(sums),
            "sha256": sha256(sums).hexdigest(),
        }
    )
    records.sort(key=lambda item: str(item["path"]))
    manifest = canonical_json(
        {
            "schema": "nlp-basic-download-manifest/1",
            "artifact": "nlp-offline-interpreter/0.1.0-basic",
            "status": "user-directed-local-artifact",
            "approver_required": False,
            "authority_effect": "NONE",
            "production_ready": False,
            "execution_allowed": False,
            "member_count": len(records),
            "members": records,
        }
    )

    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", str(FIXED_EPOCH)))
    all_members = {**payload, "ARTIFACT_MANIFEST.json": manifest}
    with ZipFile(output, "x", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(all_members):
            archive.writestr(zip_info(name, epoch), all_members[name])

    print(
        json.dumps(
            {
                "artifact": str(output),
                "members": len(all_members),
                "size": output.stat().st_size,
                "sha256": sha256(output.read_bytes()).hexdigest(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
