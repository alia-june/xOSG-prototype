"""Build a deterministic, unpublished P08 internal test candidate."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[2]
P08 = ROOT / "production" / "p08"
ARTIFACTS = P08 / "artifacts"
CANDIDATE_NAME = "nlp-offline-interpreter-0.1.0-test.20261003"
ARCHIVE = ARTIFACTS / f"{CANDIDATE_NAME}.zip"
RECEIPT = P08 / "CANDIDATE_RECEIPT.json"
SOURCE_COMMIT = "3388f57854f6f693732149dc3e4039558fc2a551"
CONTROL_BASELINE_COMMIT = "5902224eab0f870540d8e2a584800456d3b1ad3c"
WHEEL = ROOT / "production" / "p06" / "artifacts" / "nlp_offline_interpreter-0.1.0-py3-none-any.whl"
WHEEL_SHA256 = "f624914598b98115dda294d0e34bee3e722326dcecfad2082ca437c957f138e2"
SOURCES = {
    "CHANGELOG.md": P08 / "CHANGELOG.md",
    "MIGRATION_AND_ROLLBACK.md": P08 / "MIGRATION_AND_ROLLBACK.md",
    "KNOWN_LIMITATIONS.md": P08 / "KNOWN_LIMITATIONS.md",
    "TESTBED_SCOPE.md": ROOT / "production" / "TESTBED_SCOPE_ACCEPTANCE_2026-10-02.md",
    "nlp_offline_interpreter-0.1.0-py3-none-any.whl": WHEEL,
}


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def candidate_files() -> tuple[dict[str, bytes], bytes]:
    files = {name: path.read_bytes() for name, path in SOURCES.items()}
    if digest(files[WHEEL.name]) != WHEEL_SHA256:
        raise ValueError("P06 wheel hash mismatch")
    manifest = {
        "schema": "nlp-internal-test-candidate-manifest/1",
        "candidate_id": CANDIDATE_NAME,
        "scope": "internal-testbed-no-publication",
        "production_ready": False,
        "publication_allowed": False,
        "execution_allowed": False,
        "authority_effect": "NONE",
        "package_source_commit": SOURCE_COMMIT,
        "control_baseline_commit": CONTROL_BASELINE_COMMIT,
        "members": [
            {"path": name, "size": len(data), "sha256": digest(data)}
            for name, data in sorted(files.items())
        ],
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return files, manifest_bytes


def write_archive(path: Path) -> None:
    files, manifest = candidate_files()
    files["MANIFEST.json"] = manifest
    with ZipFile(path, "x", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            info = ZipInfo(
                f"{CANDIDATE_NAME}/{name}",
                date_time=(2026, 10, 3, 0, 0, 0),
            )
            info.compress_type = ZIP_STORED if name.endswith(".whl") else ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)


def main() -> int:
    if ARCHIVE.exists() or RECEIPT.exists():
        raise FileExistsError("refusing to replace an existing P08 candidate or receipt")
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="nlp-p08-build-") as temporary:
        work = Path(temporary)
        first = work / "first.zip"
        second = work / "second.zip"
        write_archive(first)
        write_archive(second)
        first_bytes = first.read_bytes()
        second_bytes = second.read_bytes()
        if first_bytes != second_bytes:
            raise ValueError("repeated P08 builds are not byte-identical")
        with ARCHIVE.open("xb") as target:
            target.write(first_bytes)
    receipt = {
        "schema": "nlp-p08-candidate-receipt/1",
        "candidate_id": CANDIDATE_NAME,
        "status": "built-unaccepted-internal-test-candidate",
        "scope": "internal-testbed-no-publication",
        "production_ready": False,
        "publication_allowed": False,
        "authority_effect": "NONE",
        "archive": ARCHIVE.relative_to(ROOT).as_posix(),
        "size": ARCHIVE.stat().st_size,
        "sha256": digest(ARCHIVE.read_bytes()),
        "repeated_builds_byte_identical": True,
        "members": 6,
        "package_source_commit": SOURCE_COMMIT,
        "control_baseline_commit": CONTROL_BASELINE_COMMIT,
    }
    RECEIPT.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
