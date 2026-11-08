"""Verify the bounded P04 staging package without activating deployment."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

from BUILD_WHEELHOUSE_MANIFEST import metadata


ROOT = Path(__file__).resolve().parents[2]
P04 = Path(__file__).resolve().parent
LOCK_PATTERN = re.compile(
    r"^([a-z0-9][a-z0-9._-]*)==([^\s]+) --hash=sha256:([0-9a-f]{64})$"
)
REQUIRED_POLICIES = {
    "README.md",
    "REPOSITORY_POLICY.md",
    "GENERATED_DATA_POLICY.md",
    "SECRETS_POLICY.md",
    "CI_CONTRACT.md",
    "WORKING_ASSUMPTIONS.json",
    "templates/github-actions-ci.yml",
}


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_input(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.count("==") != 1 or any(marker in line for marker in ("/", "@", "-e ")):
            raise ValueError(f"unbounded requirement: {line!r}")
        name, version = line.split("==", 1)
        key = normalize(name)
        if not key or not version or key in result:
            raise ValueError(f"invalid or duplicate requirement: {line!r}")
        result[key] = version
    return result


def parse_lock(path: Path) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = LOCK_PATTERN.fullmatch(line)
        if not match:
            raise ValueError(f"invalid hash-locked requirement: {line!r}")
        name, version, digest = match.groups()
        key = normalize(name)
        if key in result:
            raise ValueError(f"duplicate locked package: {key}")
        result[key] = (version, digest)
    return result


def verify() -> list[str]:
    errors: list[str] = []
    for relative in sorted(REQUIRED_POLICIES):
        if not (P04 / relative).is_file():
            errors.append(f"missing P04 policy: {relative}")
    if not (ROOT / ".gitignore").is_file():
        errors.append("missing root .gitignore")
    assumptions = ROOT / "production" / "p04" / "WORKING_ASSUMPTIONS.json"
    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    if (ROOT / ".git").exists() and not assumptions.is_file():
        errors.append("Git repository lacks a bounded working-assumption record")
    if workflow.exists() and not assumptions.is_file():
        errors.append("live CI workflow lacks a bounded working-assumption record")
    if assumptions.is_file():
        try:
            working = json.loads(assumptions.read_text(encoding="utf-8"))
            if (
                working.get("schema") != "nlp-p04-working-assumptions/1"
                or working.get("truth_state") != "ACCEPTED_CANON"
                or working.get("authority_effect") != "P04_LOCAL_STAGING"
                or working.get("production_ready") is not False
            ):
                errors.append("working-assumption authority boundary changed")
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"working-assumption record failed: {exc}")

    try:
        direct = parse_input(P04 / "requirements-py314.in")
        locks = {
            tag: parse_lock(P04 / f"requirements-{tag}.lock")
            for tag in ("py311", "py312", "py313", "py314")
        }
        for tag, locked in locks.items():
            if direct != {name: version for name, (version, _) in locked.items()}:
                errors.append(f"input requirements and {tag} lock versions differ")
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"requirements validation failed: {exc}")
        direct = {}
        locks = {}

    try:
        manifest = json.loads((P04 / "WHEELHOUSE_MANIFEST.json").read_text(encoding="utf-8"))
        if manifest.get("schema") != "nlp-p04-wheelhouse-manifest/1":
            errors.append("unexpected wheelhouse manifest schema")
        if manifest.get("authority_effect") != "NONE" or manifest.get("production_ready") is not False:
            errors.append("wheelhouse authority boundary changed")
        listed: dict[str, dict[str, object]] = {}
        for item in manifest.get("wheels", []):
            name = item.get("path") if isinstance(item, dict) else None
            pure = PurePosixPath(name) if isinstance(name, str) else None
            if (
                pure is None
                or pure.is_absolute()
                or ".." in pure.parts
                or not name.startswith("wheelhouse/")
                or name in listed
            ):
                errors.append(f"unsafe or duplicate wheel path: {name!r}")
                continue
            listed[name] = item
        actual = {
            f"wheelhouse/{path.name}": path
            for path in (P04 / "wheelhouse").glob("*.whl")
            if path.is_file()
        }
        if set(actual) != set(listed):
            errors.append("wheelhouse membership differs from manifest")
        discovered: set[tuple[str, str, str]] = set()
        for name in sorted(set(actual) & set(listed)):
            path = actual[name]
            data = path.read_bytes()
            item = listed[name]
            package, version, _ = metadata(path)
            package = normalize(package)
            digest = sha256(data).hexdigest()
            if item.get("size") != len(data) or item.get("sha256") != digest:
                errors.append(f"wheel integrity mismatch: {name}")
            if normalize(str(item.get("package"))) != package or item.get("version") != version:
                errors.append(f"wheel metadata mismatch: {name}")
            identity = (package, version, digest)
            if identity in discovered:
                errors.append(f"duplicate wheel identity: {package} {version}")
            discovered.add(identity)
        locked_identities = {
            (package, version, digest)
            for locked in locks.values()
            for package, (version, digest) in locked.items()
        }
        if locks and discovered != locked_identities:
            errors.append("runtime hash locks do not exactly cover wheelhouse metadata")
        if manifest.get("wheel_count") != len(listed):
            errors.append("wheel_count mismatch")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"wheelhouse validation failed: {exc}")

    plan = json.loads((ROOT / "production" / "production_plan.json").read_text(encoding="utf-8"))
    states = {phase["id"]: phase["state"] for phase in plan["phases"]}
    if states.get("P03") != "verified" or states.get("P04") != "verified":
        errors.append("P04 completion requires verified P03 and P04 gates")
    return errors


def main() -> int:
    errors = verify()
    if not errors:
        scan = subprocess.run(
            [sys.executable, "-B", str(P04 / "SCAN_SECRETS.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if scan.returncode != 0:
            errors.append("bounded secret scan failed")
    result = {
        "schema": "nlp-p04-stage-verification/1",
        "status": "passed" if not errors else "failed",
        "authority_effect": "P04_LOCAL_STAGING",
        "production_ready": False,
        "p04_phase_advanced": True,
        "runtime_scope": "CPython 3.11-3.14 Windows x86-64 wheel set",
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
