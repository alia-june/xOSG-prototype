"""Fail closed when the ordered test rig lacks its pinned Python dependency."""

from __future__ import annotations

from importlib import metadata
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
REQUIRED = {"jsonschema": "4.26.0"}


def evaluate() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    versions: dict[str, str | None] = {}
    if sys.version_info < (3, 10):
        errors.append("Python 3.10 or newer is required")
    for package, expected in REQUIRED.items():
        try:
            actual = metadata.version(package)
        except metadata.PackageNotFoundError:
            actual = None
        versions[package] = actual
        if actual != expected:
            errors.append(f"{package} must be exactly {expected}; found {actual!r}")
    required_paths = (
        ROOT / "development" / "nlp-offline-interpreter" / "tests",
        ROOT / "projects" / "lexicon-core" / "tests",
        ROOT / "projects" / "natural-language-front-end" / "tests",
    )
    for path in required_paths:
        if not path.is_dir():
            errors.append(f"required test directory is missing: {path.relative_to(ROOT)}")
    report: dict[str, object] = {
        "schema": "nlp-test-environment/1",
        "status": "passed" if not errors else "failed",
        "python": ".".join(str(item) for item in sys.version_info[:3]),
        "dependencies": versions,
        "authority_effect": "NONE",
        "production_ready": False,
    }
    return report, errors


def main() -> int:
    report, errors = evaluate()
    print(json.dumps(report, sort_keys=True))
    for error in errors:
        print(error, file=sys.stderr)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
