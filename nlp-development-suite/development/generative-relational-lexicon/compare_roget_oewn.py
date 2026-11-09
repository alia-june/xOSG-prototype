from __future__ import annotations

from collections import Counter, defaultdict
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parent
DECISION_PATH = ROOT / "MODERN_COMPARISON_DECISION.json"
HISTORICAL_PATH = ROOT / "pilot" / "tier-zero" / "output" / "roget-historical-memberships.jsonl.gz"
HISTORICAL_RECEIPT_PATH = ROOT / "pilot" / "tier-zero" / "output" / "PILOT_RECEIPT.json"
OUTPUT_DIR = ROOT / "pilot" / "modern-comparison"
RECORDS_PATH = OUTPUT_DIR / "roget-oewn-discrepancy-records.jsonl.gz"
REPORT_JSON_PATH = OUTPUT_DIR / "DISCREPANCY_SHAPE_REPORT.json"
REPORT_MD_PATH = OUTPUT_DIR / "DISCREPANCY_SHAPE_REPORT.md"
RECEIPT_PATH = OUTPUT_DIR / "COMPARISON_RECEIPT.json"
COMPARATOR_VERSION = "roget-oewn-discrepancy-shapes/1"

ROGET_POS_MAP = {
    "N": {"n"},
    "V": {"v"},
    "Adj": {"a", "s"},
    "Adv": {"r"},
    "Phr": set(),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_decision(decision: dict[str, object]) -> Path:
    if decision.get("status") != "AUTHORIZED_TEST_COMPARISON":
        raise ValueError("modern comparison is not authorized")
    if decision.get("authority_effect") != "TEST_COMPARISON_ONLY":
        raise ValueError("comparison authority must remain test-only")
    for field in ("production_ready", "publication_allowed", "canon_admission"):
        if decision.get(field) is not False:
            raise ValueError(f"comparison boundary changed: {field}")
    modern = decision.get("modern_source")
    if not isinstance(modern, dict) or modern.get("release") != "oewn:2025":
        raise ValueError("the pinned modern comparator is missing")
    database = (ROOT / str(modern["relative_path"])).resolve()
    if not database.is_file():
        raise ValueError(f"modern comparator database is missing: {database}")
    if database.stat().st_size != modern.get("bytes"):
        raise ValueError("modern comparator byte count changed")
    if sha256_path(database) != modern.get("sha256"):
        raise ValueError("modern comparator SHA-256 changed")
    return database


def validate_historical_input() -> dict[str, object]:
    receipt = json.loads(HISTORICAL_RECEIPT_PATH.read_text(encoding="utf-8"))
    if receipt.get("status") != "PASSED":
        raise ValueError("historical pilot receipt is not passed")
    expected = receipt.get("output", {}).get("historical_memberships", {})
    if HISTORICAL_PATH.stat().st_size != expected.get("bytes"):
        raise ValueError("historical membership byte count changed")
    if sha256_path(HISTORICAL_PATH) != expected.get("sha256"):
        raise ValueError("historical membership SHA-256 changed")
    return {
        "relative_path": str(HISTORICAL_PATH.relative_to(ROOT)),
        "record_count": expected.get("record_count"),
        "bytes": expected.get("bytes"),
        "sha256": expected.get("sha256"),
        "source_sha256": receipt.get("source", {}).get("sha256"),
        "parser_version": receipt.get("parser_version"),
    }


def load_historical(path: Path = HISTORICAL_PATH) -> dict[str, dict[str, object]]:
    terms: dict[str, dict[str, object]] = {}
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            normalized = record["normalized_term"]
            item = terms.setdefault(
                normalized,
                {
                    "surfaces": set(),
                    "historical_head_ids": set(),
                    "historical_head_numbers": set(),
                    "historical_pos": set(),
                    "source_bracket_labels": set(),
                    "membership_count": 0,
                },
            )
            item["surfaces"].add(record["term"])
            item["historical_head_ids"].add(record.get("head_id", str(record["head_number"])))
            item["historical_head_numbers"].add(record["head_number"])
            item["historical_pos"].add(record["part_of_speech_marker"])
            item["source_bracket_labels"].update(record.get("source_bracket_labels", []))
            item["membership_count"] += 1
    return terms


def load_modern(database: Path) -> tuple[dict[str, dict[str, set[object]]], dict[int, int], dict[str, object]]:
    connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
    try:
        lexicon = connection.execute("SELECT specifier, license FROM lexicons").fetchall()
        if lexicon != [("oewn:2025", "https://creativecommons.org/licenses/by/4.0")]:
            raise ValueError(f"unexpected modern lexicon metadata: {lexicon}")
        modern: dict[str, dict[str, set[object]]] = {}
        query = """
            SELECT f.form, e.pos, e.id, s.id, s.synset_rowid
            FROM forms AS f
            JOIN entries AS e ON e.rowid = f.entry_rowid
            LEFT JOIN senses AS s ON s.entry_rowid = e.rowid
            WHERE f.rank = 0
        """
        for form, pos, entry_id, sense_id, synset_rowid in connection.execute(query):
            normalized = str(form).casefold()
            item = modern.setdefault(
                normalized,
                {"pos": set(), "entries": set(), "senses": set(), "synsets": set()},
            )
            item["pos"].add(pos)
            item["entries"].add(entry_id)
            if sense_id is not None:
                item["senses"].add(sense_id)
            if synset_rowid is not None:
                item["synsets"].add(synset_rowid)
        relation_counts = dict(
            connection.execute(
                "SELECT source_rowid, COUNT(*) FROM synset_relations GROUP BY source_rowid"
            ).fetchall()
        )
        inventory = {
            "entries": connection.execute("SELECT COUNT(*) FROM entries").fetchone()[0],
            "forms": connection.execute("SELECT COUNT(*) FROM forms").fetchone()[0],
            "senses": connection.execute("SELECT COUNT(*) FROM senses").fetchone()[0],
            "synsets": connection.execute("SELECT COUNT(*) FROM synsets").fetchone()[0],
        }
        return modern, relation_counts, inventory
    finally:
        connection.close()


def sense_bucket(count: int) -> str:
    if count == 0:
        return "0"
    if count == 1:
        return "1"
    if count <= 3:
        return "2-3"
    if count <= 7:
        return "4-7"
    return "8+"


def head_bucket(count: int) -> str:
    if count == 1:
        return "1"
    if count == 2:
        return "2"
    if count <= 5:
        return "3-5"
    return "6+"


def compare_terms(
    historical: dict[str, dict[str, object]],
    modern: dict[str, dict[str, set[object]]],
    relation_counts: dict[int, int],
) -> list[dict[str, object]]:
    records = []
    for normalized in sorted(historical):
        old = historical[normalized]
        current = modern.get(normalized)
        historical_markers = set(old["historical_pos"])
        historical_pos = set().union(*(ROGET_POS_MAP[marker] for marker in historical_markers))
        modern_pos = set(current["pos"]) if current else set()
        sense_count = len(current["senses"]) if current else 0
        synset_count = len(current["synsets"]) if current else 0
        head_count = len(old["historical_head_ids"])
        shapes = []
        if current is None:
            shapes.append("NO_EXACT_MODERN_LEMMA")
        elif historical_pos and modern_pos and historical_pos.isdisjoint(modern_pos):
            shapes.append("POS_DISJOINT")
        elif historical_pos and modern_pos and historical_pos != modern_pos:
            shapes.append("POS_PARTIAL_OVERLAP")
        if head_count >= 3:
            shapes.append("HISTORICAL_HEAD_DISPERSION")
        if sense_count >= 2:
            shapes.append("MODERN_SENSE_MULTIPLICITY")
        if head_count == 1 and sense_count >= 2:
            shapes.append("ONE_HISTORICAL_HEAD_TO_MANY_MODERN_SENSES")
        if head_count >= 2 and sense_count == 1:
            shapes.append("MANY_HISTORICAL_HEADS_TO_ONE_MODERN_SENSE")
        if head_count >= 2 and sense_count >= 2:
            shapes.append("MANY_TO_MANY_PRESSURE")
        if "Phr" in historical_markers:
            shapes.append("HISTORICAL_PHRASE_MEMBERSHIP_PRESENT")
        if old["source_bracket_labels"]:
            shapes.append("SOURCE_BRACKET_LABEL_PRESENT")
        records.append(
            {
                "schema": "roget-oewn-discrepancy-shape/1",
                "truth_state": "DERIVED_COMPARISON",
                "acceptance_state": "SHAPE_ONLY_NO_EXPLANATION",
                "normalized_term": normalized,
                "historical_surfaces": sorted(
                    old["surfaces"], key=lambda value: (value.casefold(), value)
                ),
                "historical_membership_count": old["membership_count"],
                "historical_head_count": head_count,
                "historical_head_ids": sorted(old["historical_head_ids"]),
                "historical_head_numbers": sorted(old["historical_head_numbers"]),
                "historical_pos_markers": sorted(historical_markers),
                "source_bracket_label_count": len(old["source_bracket_labels"]),
                "modern_exact_lemma": current is not None,
                "modern_pos": sorted(modern_pos),
                "modern_entry_count": len(current["entries"]) if current else 0,
                "modern_sense_count": sense_count,
                "modern_synset_count": synset_count,
                "modern_outgoing_relation_count": (
                    sum(relation_counts.get(int(rowid), 0) for rowid in current["synsets"])
                    if current
                    else 0
                ),
                "sense_count_bucket": sense_bucket(sense_count),
                "historical_head_bucket": head_bucket(head_count),
                "discrepancy_shapes": sorted(shapes),
            }
        )
    return records


def summarize(records: list[dict[str, object]], inventory: dict[str, object]) -> dict[str, object]:
    shape_counts: Counter[str] = Counter()
    combination_counts: Counter[tuple[str, ...]] = Counter()
    sense_buckets: Counter[str] = Counter()
    head_buckets: Counter[str] = Counter()
    pos_matrix: Counter[tuple[str, str]] = Counter()
    exact = 0
    for record in records:
        shapes = tuple(record["discrepancy_shapes"])
        shape_counts.update(shapes)
        combination_counts[shapes] += 1
        sense_buckets[record["sense_count_bucket"]] += 1
        head_buckets[record["historical_head_bucket"]] += 1
        if record["modern_exact_lemma"]:
            exact += 1
        historical_key = "+".join(record["historical_pos_markers"]) or "none"
        modern_key = "+".join(record["modern_pos"]) or "none"
        pos_matrix[(historical_key, modern_key)] += 1
    total = len(records)
    return {
        "schema": "roget-oewn-discrepancy-shape-report/1",
        "status": "GENERATED_TEST_RESULT",
        "authority_effect": "TEST_COMPARISON_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "historical_source": "project-gutenberg-roget-22",
        "modern_source": "oewn:2025",
        "comparison_method": "exact Unicode-casefolded form match; no lemmatization, definitions, examples, or contextual sense selection",
        "historical_unique_term_count": total,
        "exact_modern_lemma_count": exact,
        "no_exact_modern_lemma_count": total - exact,
        "exact_modern_lemma_percent": round(exact * 100 / total, 4) if total else 0,
        "modern_inventory": inventory,
        "shape_counts": dict(sorted(shape_counts.items())),
        "shape_combination_counts": [
            {"shapes": list(shapes), "count": count}
            for shapes, count in sorted(combination_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "modern_sense_count_buckets": dict(sorted(sense_buckets.items())),
        "historical_head_count_buckets": dict(sorted(head_buckets.items())),
        "part_of_speech_matrix": [
            {"historical": old, "modern": current, "count": count}
            for (old, current), count in sorted(pos_matrix.items(), key=lambda item: (-item[1], item[0]))
        ],
        "candidate_quality_boundary": "Historical terms are deterministic segmentation candidates from the mixed electronic Roget artifact. They have passed structural tests but not individual lexical review and may retain transcription or segmentation noise.",
        "interpretation_boundary": "Counts describe comparison shapes only. They do not identify error, semantic change, cause, lexical validity, or which source is correct.",
    }


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Roget to Open English WordNet discrepancy-shape report",
        "",
        "Status: generated internal test comparison; not production, publication, canon, or a judgment about which source is correct.",
        "",
        "## Scope",
        "",
        f"- Historical unique normalized terms: {report['historical_unique_term_count']}",
        f"- Exact modern lemmas: {report['exact_modern_lemma_count']} ({report['exact_modern_lemma_percent']}%)",
        f"- No exact modern lemma: {report['no_exact_modern_lemma_count']}",
        "- Match rule: exact Unicode-casefolded form only; no lemmatization.",
        "- Definitions and examples were not read into the comparison output.",
        "- Roget terms remain mechanically extracted candidates, not individually accepted lexemes.",
        "",
        "## Discrepancy shapes",
        "",
        "| Shape | Count | What the shape records |",
        "|---|---:|---|",
    ]
    explanations = {
        "NO_EXACT_MODERN_LEMMA": "Roget candidate has no exact OEWN primary form.",
        "POS_DISJOINT": "Historical and modern POS sets have no mapped overlap.",
        "POS_PARTIAL_OVERLAP": "The POS sets overlap but are not identical.",
        "HISTORICAL_HEAD_DISPERSION": "The term occurs under at least three Roget heads.",
        "MODERN_SENSE_MULTIPLICITY": "OEWN supplies at least two candidate senses.",
        "ONE_HISTORICAL_HEAD_TO_MANY_MODERN_SENSES": "One Roget head meets multiple OEWN senses.",
        "MANY_HISTORICAL_HEADS_TO_ONE_MODERN_SENSE": "Multiple Roget heads meet one OEWN sense.",
        "MANY_TO_MANY_PRESSURE": "Multiple historical heads meet multiple modern senses.",
        "HISTORICAL_PHRASE_MEMBERSHIP_PRESENT": "At least one historical membership is in Roget's phrase section.",
        "SOURCE_BRACKET_LABEL_PRESENT": "The electronic source attaches at least one bracketed source label.",
    }
    for shape, count in report["shape_counts"].items():
        lines.append(f"| `{shape}` | {count} | {explanations[shape]} |")
    lines.extend(
        [
            "",
            "## Modern sense-count distribution",
            "",
            "| Candidate senses | Terms |",
            "|---|---:|",
        ]
    )
    for bucket, count in report["modern_sense_count_buckets"].items():
        lines.append(f"| {bucket} | {count} |")
    lines.extend(
        [
            "",
            "## Historical head dispersion",
            "",
            "| Roget heads | Terms |",
            "|---|---:|",
        ]
    )
    for bucket, count in report["historical_head_count_buckets"].items():
        lines.append(f"| {bucket} | {count} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            report["interpretation_boundary"],
            report["candidate_quality_boundary"],
            "A missing exact lemma may reflect spelling, inflection, phrase structure, transcription noise, historical vocabulary, or a genuine coverage gap; this pass does not choose among those explanations.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(
    records: list[dict[str, object]],
    report: dict[str, object],
    historical_input: dict[str, object],
    modern_database: Path,
) -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    records_text = "".join(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n" for record in records)
    raw_records = records_text.encode("utf-8")
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as stream:
        stream.write(raw_records)
    compressed = buffer.getvalue()
    RECORDS_PATH.write_bytes(compressed)
    report_text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    with REPORT_JSON_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(report_text)
    markdown = render_markdown(report)
    with REPORT_MD_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(markdown)
    receipt = {
        "schema": "roget-oewn-comparison-receipt/1",
        "status": "PASSED",
        "authority_effect": "TEST_COMPARISON_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "comparator_version": COMPARATOR_VERSION,
        "inputs": {
            "historical_memberships": historical_input,
            "modern_database": {
                "relative_path": os.path.relpath(modern_database, ROOT),
                "bytes": modern_database.stat().st_size,
                "sha256": sha256_path(modern_database),
            },
        },
        "outputs": {
            "records": {
                "relative_path": RECORDS_PATH.name,
                "record_count": len(records),
                "uncompressed_bytes": len(raw_records),
                "bytes": len(compressed),
                "sha256": sha256_bytes(compressed),
            },
            "report_json": {
                "relative_path": REPORT_JSON_PATH.name,
                "bytes": len(report_text.encode("utf-8")),
                "sha256": sha256_bytes(report_text.encode("utf-8")),
            },
            "report_markdown": {
                "relative_path": REPORT_MD_PATH.name,
                "bytes": len(markdown.encode("utf-8")),
                "sha256": sha256_bytes(markdown.encode("utf-8")),
            },
        },
    }
    with RECEIPT_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main() -> int:
    decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
    database = validate_decision(decision)
    historical_input = validate_historical_input()
    historical = load_historical()
    modern, relation_counts, inventory = load_modern(database)
    records = compare_terms(historical, modern, relation_counts)
    report = summarize(records, inventory)
    receipt = write_outputs(records, report, historical_input, database)
    print(json.dumps({"receipt": receipt, "summary": {key: report[key] for key in ("historical_unique_term_count", "exact_modern_lemma_count", "no_exact_modern_lemma_count", "exact_modern_lemma_percent")}}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
