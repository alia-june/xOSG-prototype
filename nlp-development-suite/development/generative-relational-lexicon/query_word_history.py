from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MEMBERSHIPS_PATH = ROOT / "pilot" / "tier-zero" / "output" / "roget-historical-memberships.jsonl.gz"


def query_memberships(words: list[str], path: Path = MEMBERSHIPS_PATH) -> dict[str, object]:
    requested = {word.casefold(): word for word in words}
    matches: dict[str, list[dict[str, object]]] = {key: [] for key in requested}
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            normalized = record.get("normalized_term")
            if normalized in matches:
                matches[normalized].append(
                    {
                        "term": record["term"],
                        "head_id": record.get("head_id", str(record["head_number"])),
                        "head_number": record["head_number"],
                        "heading": record["heading"],
                        "part_of_speech_marker": record["part_of_speech_marker"],
                        "historical_scope": record["historical_scope"],
                        "source_line_start": record["source_line_start"],
                        "source_line_end": record["source_line_end"],
                    }
                )
    results = []
    for normalized, supplied in requested.items():
        candidates = matches[normalized]
        results.append(
            {
                "modern_word": supplied,
                "normalized_query": normalized,
                "status": "HISTORICAL_CANDIDATES_FOUND" if candidates else "NO_EXACT_HISTORICAL_CANDIDATE",
                "candidate_count": len(candidates),
                "candidates": candidates,
            }
        )
    return {
        "schema": "word-universe-historical-query/1",
        "status": "GENERATED_TEST_RESULT",
        "acceptance_state": "PROPOSAL_ONLY",
        "source_id": "project-gutenberg-roget-22",
        "results": results,
        "boundary": "Exact historical category membership in one mixed electronic edition; not a definition, proof of origin, proof of continuity, or exhaustive history.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Query the Tier-Zero historical Roget pilot.")
    parser.add_argument("words", nargs="+", help="Modern words to look up by exact normalized form.")
    arguments = parser.parse_args()
    print(json.dumps(query_memberships(arguments.words), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
