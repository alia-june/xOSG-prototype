"""Run a bounded high-confidence credential scan over development controls."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
SCOPES = (ROOT / "production", ROOT / "development", ROOT / ".github")
EXCLUDED_PARTS = {"reports", "wheelhouse", "dist", "__pycache__", "build"}
EXCLUDED_FILES = {Path(__file__).name, "SECRETS_POLICY.md"}
TEXT_SUFFIXES = {".py", ".json", ".md", ".csv", ".toml", ".txt", ".yml", ".yaml"}
PATTERNS = {
    "private-key": re.compile("-----BEGIN " + "(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github-token": re.compile("gh" + r"[opusr]_[A-Za-z0-9]{36,}"),
    "github-fine-grained": re.compile("github_pat" + r"_[A-Za-z0-9_]{40,}"),
    "openai-project-key": re.compile("sk-" + r"proj-[A-Za-z0-9_-]{20,}"),
    "aws-access-key": re.compile("AKIA" + r"[A-Z0-9]{16}"),
}


def candidate_files() -> list[Path]:
    files: list[Path] = []
    for scope in SCOPES:
        for path in scope.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower() in TEXT_SUFFIXES
                and path.name not in EXCLUDED_FILES
                and not any(part in EXCLUDED_PARTS or part.endswith(".egg-info") for part in path.parts)
            ):
                files.append(path)
    return sorted(files, key=lambda path: path.relative_to(ROOT).as_posix())


def scan() -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in candidate_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            for label, pattern in PATTERNS.items():
                if pattern.search(line):
                    findings.append(
                        {
                            "file": path.relative_to(ROOT).as_posix(),
                            "line": line_number,
                            "pattern": label,
                        }
                    )
    return findings


def main() -> int:
    findings = scan()
    result = {
        "schema": "nlp-p04-secret-scan/1",
        "status": "passed" if not findings else "failed",
        "authority_effect": "NONE",
        "files_scanned": len(candidate_files()),
        "findings": findings,
        "limitation": "high-confidence local patterns only; not a full security audit",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
