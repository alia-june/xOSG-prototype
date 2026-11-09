"""Verify the pinned complete Open English WordNet 2025 installation."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from wordnet_lexicon import DEFAULT_DATA_DIR, WORDNET_RELEASE, WordNetLexicon


EXPECTED_ARCHIVE_SHA256 = "9ca6d1dcb75f822fdd66617f7d9da48142ace38dd544d6ad5e2feca1674ad3fe"
EXPECTED_RESOURCE_URL = "https://en-word.net/static/english-wordnet-2025.xml.gz"


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(data_dir: Path) -> dict:
    import wn
    from wn.project import iterpackages

    wn.config.data_directory = str(data_dir)
    info = wn.config.get_project_info(WORDNET_RELEASE)
    cache = Path(info["cache"]) if info.get("cache") else None
    archive_hash = file_sha256(cache) if cache and cache.is_file() else None
    project_readable = False
    if cache and cache.is_file():
        project_readable = any(package.resource_file().is_file()
                               for package in iterpackages(cache))
    inventory = WordNetLexicon(data_dir).inventory()
    checks = {
        "release_installed": inventory["release"] == WORDNET_RELEASE,
        "database_counts_match": inventory["complete"],
        "source_archive_present": cache is not None and cache.is_file(),
        "source_archive_sha256_matches": archive_hash == EXPECTED_ARCHIVE_SHA256,
        "source_archive_is_readable_lmf": project_readable,
        "resource_url_matches": info.get("resource_urls") == [EXPECTED_RESOURCE_URL],
    }
    return {"wordnet_release": WORDNET_RELEASE, "data_directory": str(data_dir.resolve()),
            "resource_url": info.get("resource_urls"), "source_archive": str(cache) if cache else None,
            "source_archive_sha256": archive_hash, **inventory,
            "checks": checks, "verified_complete": all(checks.values())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wordnet-dir", type=Path, default=DEFAULT_DATA_DIR)
    args = parser.parse_args()
    try:
        result = verify(args.wordnet_dir)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["verified_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
