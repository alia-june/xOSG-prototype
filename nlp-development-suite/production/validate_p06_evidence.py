"""Validate P06 artifact, dependency, provenance, and license evidence."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parent.parent
P06 = ROOT / "production" / "p06"
LICENSE_NAMES = {"license", "licence", "copying", "notice"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate() -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    try:
        manifest = load_json(P06 / "ARTIFACT_MANIFEST.json")
        dependencies = load_json(P06 / "DEPENDENCY_INVENTORY.json")
        provenance = load_json(P06 / "PROVENANCE.json")
        plan = load_json(ROOT / "production" / "production_plan.json")
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"schema": "nlp-p06-validation/1", "status": "failed"}, [str(exc)]

    phases = {item.get("id"): item for item in plan.get("phases", []) if isinstance(item, dict)}
    if phases.get("P05", {}).get("state") != "verified":
        errors.append("P05 must be verified before P06")
    p06_phase = phases.get("P06", {})
    if p06_phase.get("state") != "verified":
        errors.append("P06 must be verified for the accepted internal-testbed scope")
    if plan.get("current_scope") != "internal-testbed-no-publication":
        errors.append("P06 verification requires the no-publication testbed boundary")
    if p06_phase.get("blockers"):
        errors.append("P06 must not retain a distribution blocker in internal-testbed scope")

    if manifest.get("schema") != "nlp-p06-wheel-manifest/1":
        errors.append("unexpected artifact manifest schema")
    if manifest.get("production_ready") is not False or manifest.get("execution_allowed") is not False:
        errors.append("artifact manifest exceeds the accepted boundary")
    artifact_value = manifest.get("artifact")
    pure = PurePosixPath(artifact_value) if isinstance(artifact_value, str) else None
    if pure is None or pure.is_absolute() or ".." in pure.parts:
        errors.append("artifact path is unsafe")
        artifact = None
    else:
        artifact = ROOT.joinpath(*pure.parts)
        if not artifact.is_file():
            errors.append("verification wheel is missing")

    actual_members: dict[str, bytes] = {}
    metadata_text = ""
    if artifact is not None and artifact.is_file():
        data = artifact.read_bytes()
        if manifest.get("size") != len(data) or manifest.get("sha256") != sha256(data).hexdigest():
            errors.append("verification wheel size or hash mismatch")
        try:
            with ZipFile(artifact) as wheel:
                names = wheel.namelist()
                if len(names) != len(set(names)):
                    errors.append("wheel contains duplicate members")
                for name in names:
                    member = PurePosixPath(name)
                    if member.is_absolute() or ".." in member.parts or "\\" in name:
                        errors.append(f"unsafe wheel member: {name!r}")
                        continue
                    actual_members[name] = wheel.read(name)
                metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
                if len(metadata_names) != 1:
                    errors.append("wheel must contain one METADATA file")
                else:
                    metadata_text = actual_members[metadata_names[0]].decode("utf-8")
        except (BadZipFile, UnicodeError) as exc:
            errors.append(f"wheel inspection failed: {exc}")

    listed: dict[str, dict[str, Any]] = {}
    for item in manifest.get("members", []):
        name = item.get("path") if isinstance(item, dict) else None
        if not isinstance(name, str) or name in listed:
            errors.append(f"invalid or duplicate manifest member: {name!r}")
            continue
        listed[name] = item
    if set(listed) != set(actual_members):
        errors.append("artifact manifest does not exactly match wheel membership")
    for name in sorted(set(listed) & set(actual_members)):
        data = actual_members[name]
        if listed[name].get("size") != len(data) or listed[name].get("sha256") != sha256(data).hexdigest():
            errors.append(f"wheel member size or hash mismatch: {name}")
    if manifest.get("member_count") != len(listed):
        errors.append("artifact member_count mismatch")

    metadata_lines = metadata_text.splitlines()
    if any(line.startswith("Requires-Dist:") for line in metadata_lines):
        errors.append("runtime wheel unexpectedly declares a dependency")
    if any(line.startswith(("License:", "License-Expression:", "Classifier: License")) for line in metadata_lines):
        errors.append("license evidence changed without updating the P06 disposition")
    if any(
        part.casefold() in LICENSE_NAMES
        for name in actual_members
        for part in PurePosixPath(name).parts
    ):
        errors.append("wheel contains unreviewed license or notice material")
    if any(
        "oewn" in name.casefold() or "wordnet" in name.casefold() or name.casefold().endswith(".db")
        for name in actual_members
    ):
        errors.append("wheel unexpectedly bundles lexical data")

    runtime = dependencies.get("runtime", {})
    if runtime.get("dependencies") != [] or runtime.get("dependency_count") != 0:
        errors.append("dependency inventory does not describe a dependency-free runtime")
    lexical = dependencies.get("lexical_data", {})
    if lexical.get("bundled") is not False:
        errors.append("dependency inventory incorrectly bundles lexical data")
    if provenance.get("verification_wheel", {}).get("sha256") != manifest.get("sha256"):
        errors.append("provenance and artifact hashes disagree")
    if provenance.get("successor_source", {}).get("member_count") != 20:
        errors.append("unexpected successor source member count")

    project_license_files = [
        path
        for path in (ROOT / "development" / "nlp-offline-interpreter").rglob("*")
        if path.is_file() and path.stem.casefold() in LICENSE_NAMES
    ]
    if project_license_files:
        errors.append("project license evidence changed without updating P06")

    report = {
        "schema": "nlp-p06-validation/1",
        "status": "passed" if not errors else "failed",
        "p06_disposition": "verified_internal_testbed_distribution_deferred",
        "wheel_sha256": manifest.get("sha256"),
        "wheel_members": len(actual_members),
        "runtime_dependencies": runtime.get("dependency_count"),
        "lexical_data_bundled": lexical.get("bundled"),
        "production_ready": False,
        "errors": errors,
    }
    return report, errors


def main() -> int:
    report, errors = evaluate()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
