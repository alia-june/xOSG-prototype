"""Verify the exact unpublished P08 internal test candidate."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile

ROOT = Path(__file__).resolve().parents[2]
P08 = ROOT / "production" / "p08"
CANDIDATE_NAME = "nlp-offline-interpreter-0.1.0-test.20261003"
ARCHIVE = P08 / "artifacts" / f"{CANDIDATE_NAME}.zip"
RECEIPT = P08 / "CANDIDATE_RECEIPT.json"
EXPECTED_CONTENT_NAMES = {
    "CHANGELOG.md",
    "MIGRATION_AND_ROLLBACK.md",
    "KNOWN_LIMITATIONS.md",
    "TESTBED_SCOPE.md",
    "nlp_offline_interpreter-0.1.0-py3-none-any.whl",
}


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def evaluate() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    try:
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        archive_bytes = ARCHIVE.read_bytes()
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"schema": "nlp-p08-verification/1", "status": "failed"}, [str(exc)]
    if receipt.get("sha256") != sha256(archive_bytes).hexdigest():
        errors.append("candidate archive hash mismatch")
    if receipt.get("size") != len(archive_bytes):
        errors.append("candidate archive size mismatch")
    if receipt.get("production_ready") is not False or receipt.get("publication_allowed") is not False:
        errors.append("candidate exceeds internal-testbed authority")
    actual: dict[str, bytes] = {}
    try:
        with ZipFile(ARCHIVE) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                errors.append("candidate contains duplicate paths")
            prefix = f"{CANDIDATE_NAME}/"
            for name in names:
                pure = PurePosixPath(name)
                if pure.is_absolute() or ".." in pure.parts or not name.startswith(prefix):
                    errors.append(f"unsafe candidate member: {name!r}")
                    continue
                actual[name.removeprefix(prefix)] = archive.read(name)
    except BadZipFile as exc:
        errors.append(f"candidate ZIP is invalid: {exc}")
    expected_names = EXPECTED_CONTENT_NAMES | {"MANIFEST.json"}
    if set(actual) != expected_names:
        errors.append("candidate membership mismatch")
    try:
        manifest = json.loads(actual.get("MANIFEST.json", b"").decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        manifest = {}
        errors.append(f"candidate manifest is invalid: {exc}")
    if manifest.get("scope") != "internal-testbed-no-publication":
        errors.append("candidate manifest scope mismatch")
    if manifest.get("production_ready") is not False or manifest.get("publication_allowed") is not False:
        errors.append("candidate manifest exceeds authority")
    listed = {item.get("path"): item for item in manifest.get("members", []) if isinstance(item, dict)}
    if set(listed) != expected_names - {"MANIFEST.json"}:
        errors.append("candidate manifest membership mismatch")
    for name in sorted(set(listed) & set(actual)):
        data = actual[name]
        if listed[name].get("size") != len(data) or listed[name].get("sha256") != digest(data):
            errors.append(f"candidate member mismatch: {name}")
    report = {
        "schema": "nlp-p08-verification/1",
        "status": "passed" if not errors else "failed",
        "candidate_id": CANDIDATE_NAME,
        "archive_sha256": receipt.get("sha256"),
        "members": len(actual),
        "production_ready": False,
        "publication_allowed": False,
        "authority_effect": "NONE",
        "errors": errors,
    }
    return report, errors


def main() -> int:
    report, errors = evaluate()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
