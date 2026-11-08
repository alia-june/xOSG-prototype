"""Verify a prepared NLP prototype repository without trusting its manifest."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import sys


ROOT = Path(__file__).resolve().parent
POLICY_PATH = ROOT / "PROTOTYPE_REPO_POLICY.json"
MANIFEST_PATH = ROOT / "PROTOTYPE_MANIFEST.json"
FORBIDDEN_PARTS = {".git", ".lexical_sources", ".openai", ".wn_data", "__pycache__", "build-output", "node_modules", "vendor"}
FORBIDDEN_SUFFIXES = {
    ".db", ".dict", ".gz", ".idx", ".ifo", ".jsonl", ".odict", ".odxml",
    ".p12", ".pem", ".pfx", ".pyc", ".sqlite", ".sqlite3", ".tar", ".whl", ".xz", ".zip",
}
TEXT_SUFFIXES = {
    "", ".cjs", ".css", ".csv", ".html", ".in", ".ini", ".js", ".json",
    ".lock", ".md", ".mjs", ".ps1", ".py", ".toml", ".tsv", ".txt", ".xml", ".yml", ".yaml",
}
LOCAL_ACCOUNT = "privateuser" + "-5"
PUBLIC_ACCOUNT = "dastardly" + "rat"
PUBLIC_HOST = "dastardly" + "-rat"
PERSONAL_NAME = "Philippe" + " Stuart"
PERSONAL_PROFILE = "facebook.com/" + "philippe"
PERSONAL_ASSET = "philippe" + "-stuart-art"
HOSTING_PROJECT = "appgprj" + "_"
INTERNAL_HOST = "git." + "chatgpt-team.site"
IDENTITY_PATTERNS = {
    "local account": re.compile(re.escape(LOCAL_ACCOUNT), re.I),
    "public account": re.compile(f"{re.escape(PUBLIC_ACCOUNT)}|{re.escape(PUBLIC_HOST)}", re.I),
    "personal profile": re.compile(f"{re.escape(PERSONAL_NAME)}|{re.escape(PERSONAL_PROFILE)}|{re.escape(PERSONAL_ASSET)}", re.I),
    "hosting project": re.compile(f"{re.escape(HOSTING_PROJECT)}|{re.escape(INTERNAL_HOST)}", re.I),
    "absolute user path": re.compile(r"[A-Za-z]:[\\/]Users[\\/]", re.I),
}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "GitHub token": re.compile(r"(?:ghp_|github_pat_)[A-Za-z0-9_]{12,}"),
    "OpenAI token": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
}


def main() -> int:
    errors: list[str] = []
    if not POLICY_PATH.is_file() or not MANIFEST_PATH.is_file():
        print("Prototype policy or manifest is missing", file=sys.stderr)
        return 2
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected = {item["path"]: item for item in manifest.get("members", [])}
    actual: dict[str, Path] = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == MANIFEST_PATH:
            continue
        relative = path.relative_to(ROOT)
        name = relative.as_posix()
        actual[name] = path
        if FORBIDDEN_PARTS.intersection(relative.parts):
            errors.append(f"forbidden directory: {name}")
        if path.suffix.casefold() in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden data/archive suffix: {name}")
        if path.stat().st_size > int(policy["max_file_bytes"]):
            errors.append(f"oversize file: {name}")
        if relative.parts[:3] == ("projects", "lexicon-atlas", "dist") and len(relative.parts) > 3 and relative.parts[3] == "data":
            allowed = {"projects/lexicon-atlas/dist/data/.gitkeep", "projects/lexicon-atlas/dist/data/README.md"}
            if name not in allowed:
                errors.append(f"Atlas runtime data present: {name}")
        if path.suffix.casefold() in TEXT_SUFFIXES:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                errors.append(f"non-UTF-8 text candidate: {name}")
                continue
            license_exception = name == policy["license_identity_exception"]
            for label, pattern in IDENTITY_PATTERNS.items():
                if pattern.search(text) and not (license_exception and label == "public account"):
                    errors.append(f"identity marker ({label}): {name}")
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    errors.append(f"secret marker ({label}): {name}")
    if set(actual) != set(expected):
        for name in sorted(set(expected) - set(actual)):
            errors.append(f"manifest member missing: {name}")
        for name in sorted(set(actual) - set(expected)):
            errors.append(f"unmanifested file: {name}")
    for name, path in actual.items():
        item = expected.get(name)
        if not item:
            continue
        data = path.read_bytes()
        if len(data) != item.get("bytes") or sha256(data).hexdigest() != item.get("sha256"):
            errors.append(f"manifest mismatch: {name}")
        pure = PurePosixPath(name)
        if pure.is_absolute() or ".." in pure.parts:
            errors.append(f"unsafe manifest path: {name}")
    required = {
        "README.md",
        "DATA_POLICY.md",
        "projects/lexicon-atlas/LICENSE",
        "projects/lexicon-atlas/dist/index.html",
        "projects/lexicon-atlas/dist/data/README.md",
        "projects/lexicon-core/src/lexicon_core/__init__.py",
        "development/nlp-offline-interpreter/src/nlp_offline_interpreter/__init__.py",
    }
    for name in sorted(required - set(actual)):
        errors.append(f"required prototype file missing: {name}")
    if errors:
        print("Prototype verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(json.dumps({
        "schema": "nlp-suite-prototype-verification/1",
        "status": "passed",
        "files": len(actual),
        "bytes": sum(path.stat().st_size for path in actual.values()),
        "dictionary_data_present": False,
        "identity_scan": "passed-with-license-notice-exception",
        "publication_allowed": False,
        "deployment_allowed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
