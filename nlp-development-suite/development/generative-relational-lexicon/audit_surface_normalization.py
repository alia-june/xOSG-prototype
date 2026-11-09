from __future__ import annotations

from collections import Counter, defaultdict
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sqlite3
import unicodedata

import compare_roget_oewn as baseline


ROOT = Path(__file__).resolve().parent
DECISION_PATH = ROOT / "NORMALIZATION_AUDIT_DECISION.json"
BASELINE_RECEIPT_PATH = ROOT / "pilot" / "modern-comparison" / "COMPARISON_RECEIPT.json"
OUTPUT_DIR = ROOT / "pilot" / "modern-comparison" / "normalization-audit"
RECORDS_PATH = OUTPUT_DIR / "surface-normalization-candidates.jsonl.gz"
REPORT_JSON_PATH = OUTPUT_DIR / "NORMALIZATION_SHAPE_REPORT.json"
REPORT_MD_PATH = OUTPUT_DIR / "NORMALIZATION_SHAPE_REPORT.md"
RECEIPT_PATH = OUTPUT_DIR / "NORMALIZATION_AUDIT_RECEIPT.json"
AUDITOR_VERSION = "surface-normalization-audit/1"

DASH_APOSTROPHE_TRANSLATION = str.maketrans(
    {
        "\u2019": "'",
        "\u2018": "'",
        "\u02bc": "'",
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2015": "-",
    }
)
SEPARATORS_RE = re.compile(r"[\s_-]+")
ELIDED_RE = re.compile(r"[\s_'\-]+")


def exact_indexed(value: str) -> str:
    return value.casefold()


def unicode_compatibility(value: str) -> str:
    return unicodedata.normalize("NFKC", value).casefold()


def punctuation_harmonized(value: str) -> str:
    return " ".join(unicode_compatibility(value).translate(DASH_APOSTROPHE_TRANSLATION).split())


def separator_to_space(value: str) -> str:
    return SEPARATORS_RE.sub(" ", punctuation_harmonized(value)).strip()


def separator_elided(value: str) -> str:
    return ELIDED_RE.sub("", punctuation_harmonized(value))


LAYER_FUNCTIONS = {
    "EXACT_INDEXED_FORM": exact_indexed,
    "UNICODE_COMPATIBILITY": unicode_compatibility,
    "PUNCTUATION_HARMONIZED": punctuation_harmonized,
    "SEPARATOR_TO_SPACE": separator_to_space,
    "SEPARATOR_ELIDED": separator_elided,
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_audit_decision(decision: dict[str, object]) -> dict[str, object]:
    if decision.get("status") != "AUTHORIZED_TEST_AUDIT":
        raise ValueError("normalization audit is not authorized")
    if decision.get("authority_effect") != "TEST_AUDIT_ONLY":
        raise ValueError("normalization authority must remain test-only")
    for field in ("production_ready", "publication_allowed", "canon_admission", "semantic_equivalence_allowed"):
        if decision.get(field) is not False:
            raise ValueError(f"normalization boundary changed: {field}")
    ordered = decision.get("ordered_layers")
    layer_ids = [item["id"] for item in ordered] if isinstance(ordered, list) else []
    if layer_ids != list(LAYER_FUNCTIONS):
        raise ValueError("normalization layer order changed")
    pin = decision.get("baseline_receipt")
    if not isinstance(pin, dict):
        raise ValueError("baseline receipt pin is missing")
    if BASELINE_RECEIPT_PATH.stat().st_size != pin.get("bytes"):
        raise ValueError("baseline receipt byte count changed")
    if baseline.sha256_path(BASELINE_RECEIPT_PATH) != pin.get("sha256"):
        raise ValueError("baseline receipt SHA-256 changed")
    receipt = json.loads(BASELINE_RECEIPT_PATH.read_text(encoding="utf-8"))
    if receipt.get("status") != "PASSED":
        raise ValueError("baseline comparison is not passed")
    for output in receipt.get("outputs", {}).values():
        path = BASELINE_RECEIPT_PATH.parent / output["relative_path"]
        if baseline.sha256_path(path) != output["sha256"]:
            raise ValueError(f"baseline output changed: {path.name}")
    return receipt


def load_modern_forms(database: Path) -> tuple[dict[int, dict[str, object]], list[tuple[str, int, int]]]:
    entries: dict[int, dict[str, object]] = {}
    forms: list[tuple[str, int, int]] = []
    connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
    try:
        query = """
            SELECT f.form, f.rank, e.rowid, e.id, e.pos
            FROM forms AS f
            JOIN entries AS e ON e.rowid = f.entry_rowid
        """
        for form, rank, entry_rowid, entry_id, pos in connection.execute(query):
            item = entries.setdefault(
                entry_rowid,
                {"entry_id": entry_id, "pos": pos, "primary_forms": set(), "forms": set(), "sense_ids": set()},
            )
            item["forms"].add(form)
            if rank == 0:
                item["primary_forms"].add(form)
            forms.append((form, rank, entry_rowid))
        for entry_rowid, sense_id in connection.execute("SELECT entry_rowid, id FROM senses"):
            entries[entry_rowid]["sense_ids"].add(sense_id)
    finally:
        connection.close()
    return entries, forms


def build_indices(
    forms: list[tuple[str, int, int]],
) -> tuple[dict[str, dict[str, set[object]]], dict[str, set[int]]]:
    indices: dict[str, dict[str, set[object]]] = {}
    for layer_id, function in LAYER_FUNCTIONS.items():
        index: dict[str, set[object]] = defaultdict(set)
        for form, _rank, entry_rowid in forms:
            key = function(form)
            index[key].add(entry_rowid)
            index[f"\0surface:{key}"].add(form)
        indices[layer_id] = index
    primary: dict[str, set[int]] = defaultdict(set)
    for form, rank, entry_rowid in forms:
        if rank == 0:
            primary[form.casefold()].add(entry_rowid)
    return indices, primary


def audit_terms(
    historical: dict[str, dict[str, object]],
    entries: dict[int, dict[str, object]],
    forms: list[tuple[str, int, int]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    indices, primary = build_indices(forms)
    layer_risks = {
        "EXACT_INDEXED_FORM": "DICTIONARY_SUPPLIED_VARIANT",
        "UNICODE_COMPATIBILITY": "CONSERVATIVE_SURFACE_NORMALIZATION",
        "PUNCTUATION_HARMONIZED": "CONSERVATIVE_SURFACE_NORMALIZATION",
        "SEPARATOR_TO_SPACE": "MODERATE_SURFACE_CANDIDATE",
        "SEPARATOR_ELIDED": "LOOSE_COLLISION_PRONE_CANDIDATE",
    }
    baseline_exact = sum(1 for term in historical if term in primary)
    records: list[dict[str, object]] = []
    layer_counts: Counter[str] = Counter()
    risk_counts: Counter[str] = Counter()
    for term in sorted(historical):
        if term in primary:
            continue
        recovered_layer = None
        recovered_key = None
        recovered_entries: set[int] = set()
        modern_surfaces: set[str] = set()
        for layer_id, function in LAYER_FUNCTIONS.items():
            key = function(term)
            index = indices[layer_id]
            hits = {int(item) for item in index.get(key, set())}
            if hits:
                recovered_layer = layer_id
                recovered_key = key
                recovered_entries = hits
                modern_surfaces = {str(item) for item in index.get(f"\0surface:{key}", set())}
                break
        if recovered_layer is None:
            layer_counts["UNRESOLVED"] += 1
            records.append(
                {
                    "schema": "surface-normalization-candidate/1",
                    "truth_state": "DERIVED_COMPARISON",
                    "acceptance_state": "NO_SURFACE_CANDIDATE",
                    "historical_term": term,
                    "first_recovery_layer": None,
                    "risk": None,
                    "semantic_equivalence": False,
                }
            )
            continue
        layer_counts[recovered_layer] += 1
        risk = layer_risks[recovered_layer]
        risk_counts[risk] += 1
        primary_forms = set()
        candidate_pos = set()
        sense_ids = set()
        for entry_id in recovered_entries:
            primary_forms.update(entries[entry_id]["primary_forms"])
            candidate_pos.add(entries[entry_id]["pos"])
            sense_ids.update(entries[entry_id]["sense_ids"])
        records.append(
            {
                "schema": "surface-normalization-candidate/1",
                "truth_state": "DERIVED_COMPARISON",
                "acceptance_state": "SURFACE_CANDIDATE_ONLY",
                "historical_term": term,
                "first_recovery_layer": recovered_layer,
                "risk": risk,
                "normalization_key": recovered_key,
                "candidate_modern_surfaces": sorted(modern_surfaces, key=lambda value: (value.casefold(), value)),
                "candidate_primary_forms": sorted(primary_forms, key=lambda value: (value.casefold(), value)),
                "candidate_pos": sorted(candidate_pos),
                "candidate_entry_count": len(recovered_entries),
                "candidate_sense_count": len(sense_ids),
                "modern_surface_collision_count": len(modern_surfaces),
                "semantic_equivalence": False,
            }
        )
    unmatched = len(historical) - baseline_exact
    recovered = unmatched - layer_counts["UNRESOLVED"]
    collision_stats = {}
    for layer_id, index in indices.items():
        keys = [key for key in index if not key.startswith("\0surface:")]
        collision_stats[layer_id] = {
            "modern_key_count": len(keys),
            "multi_surface_key_count": sum(
                1 for key in keys if len(index.get(f"\0surface:{key}", set())) > 1
            ),
        }
    report = {
        "schema": "surface-normalization-shape-report/1",
        "status": "GENERATED_TEST_RESULT",
        "authority_effect": "TEST_AUDIT_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "semantic_equivalence_allowed": False,
        "historical_term_count": len(historical),
        "baseline_exact_primary_count": baseline_exact,
        "baseline_unmatched_count": unmatched,
        "exclusive_first_recovery_counts": {
            layer_id: layer_counts[layer_id] for layer_id in [*LAYER_FUNCTIONS, "UNRESOLVED"]
        },
        "recovered_surface_candidate_count": recovered,
        "remaining_unresolved_count": layer_counts["UNRESOLVED"],
        "cumulative_surface_candidate_count": baseline_exact + recovered,
        "cumulative_surface_candidate_percent": round((baseline_exact + recovered) * 100 / len(historical), 4),
        "risk_counts": dict(sorted(risk_counts.items())),
        "modern_index_collision_stats": collision_stats,
        "interpretation_boundary": "A recovered surface candidate is not an accepted lemma mapping, semantic equivalence, explanation, or canon admission.",
    }
    return records, report


def render_markdown(report: dict[str, object]) -> str:
    counts = report["exclusive_first_recovery_counts"]
    lines = [
        "# Controlled surface-normalization audit",
        "",
        "Status: generated internal test evidence; no semantic equivalence, production approval, publication approval, or canon admission.",
        "",
        "## Funnel",
        "",
        f"- Historical candidates: {report['historical_term_count']}",
        f"- Exact OEWN primary forms: {report['baseline_exact_primary_count']}",
        f"- Baseline unmatched: {report['baseline_unmatched_count']}",
        f"- Additional surface candidates: {report['recovered_surface_candidate_count']}",
        f"- Remaining unresolved: {report['remaining_unresolved_count']}",
        f"- Cumulative surface candidates: {report['cumulative_surface_candidate_count']} ({report['cumulative_surface_candidate_percent']}%)",
        "",
        "## Exclusive first recovery layer",
        "",
        "| Layer | Candidates | Boundary |",
        "|---|---:|---|",
        f"| `EXACT_INDEXED_FORM` | {counts['EXACT_INDEXED_FORM']} | OEWN-supplied non-primary form |",
        f"| `UNICODE_COMPATIBILITY` | {counts['UNICODE_COMPATIBILITY']} | NFKC surface candidate |",
        f"| `PUNCTUATION_HARMONIZED` | {counts['PUNCTUATION_HARMONIZED']} | Apostrophe/dash surface candidate |",
        f"| `SEPARATOR_TO_SPACE` | {counts['SEPARATOR_TO_SPACE']} | Moderate separator candidate |",
        f"| `SEPARATOR_ELIDED` | {counts['SEPARATOR_ELIDED']} | Loose and collision-prone |",
        f"| `UNRESOLVED` | {counts['UNRESOLVED']} | No candidate from these layers |",
        "",
        "## Modern index collision pressure",
        "",
        "| Layer | Distinct keys | Keys merging multiple source spellings |",
        "|---|---:|---:|",
    ]
    for layer_id, stats in report["modern_index_collision_stats"].items():
        lines.append(
            f"| `{layer_id}` | {stats['modern_key_count']} | {stats['multi_surface_key_count']} |"
        )
    lines.extend(
        [
        "",
        "## Boundary",
        "",
        report["interpretation_boundary"],
        "Layers are cumulative and exclusive: a term is counted only at its first successful layer.",
        "The loose elision layer intentionally exposes collision pressure; examples such as `a light` and `alight` must not be silently merged.",
        "Definitions and examples were not queried or emitted.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(
    records: list[dict[str, object]],
    report: dict[str, object],
    baseline_receipt: dict[str, object],
    database: Path,
) -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = "".join(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n" for record in records).encode("utf-8")
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as stream:
        stream.write(raw)
    compressed = buffer.getvalue()
    RECORDS_PATH.write_bytes(compressed)
    report_bytes = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    REPORT_JSON_PATH.write_bytes(report_bytes)
    markdown_bytes = render_markdown(report).encode("utf-8")
    REPORT_MD_PATH.write_bytes(markdown_bytes)
    receipt = {
        "schema": "surface-normalization-audit-receipt/1",
        "status": "PASSED",
        "authority_effect": "TEST_AUDIT_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "semantic_equivalence_allowed": False,
        "auditor_version": AUDITOR_VERSION,
        "inputs": {
            "decision": {"sha256": baseline.sha256_path(DECISION_PATH)},
            "baseline_receipt": {"sha256": baseline.sha256_path(BASELINE_RECEIPT_PATH)},
            "historical_memberships": baseline_receipt["inputs"]["historical_memberships"],
            "modern_database": {
                "relative_path": os.path.relpath(database, ROOT),
                "bytes": database.stat().st_size,
                "sha256": baseline.sha256_path(database),
            },
        },
        "outputs": {
            "records": {"relative_path": RECORDS_PATH.name, "record_count": len(records), "bytes": len(compressed), "uncompressed_bytes": len(raw), "sha256": sha256_bytes(compressed)},
            "report_json": {"relative_path": REPORT_JSON_PATH.name, "bytes": len(report_bytes), "sha256": sha256_bytes(report_bytes)},
            "report_markdown": {"relative_path": REPORT_MD_PATH.name, "bytes": len(markdown_bytes), "sha256": sha256_bytes(markdown_bytes)},
        },
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return receipt


def main() -> int:
    decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
    baseline_receipt = validate_audit_decision(decision)
    comparison_decision = json.loads(baseline.DECISION_PATH.read_text(encoding="utf-8"))
    database = baseline.validate_decision(comparison_decision)
    baseline.validate_historical_input()
    historical = baseline.load_historical()
    entries, forms = load_modern_forms(database)
    records, report = audit_terms(historical, entries, forms)
    receipt = write_outputs(records, report, baseline_receipt, database)
    print(json.dumps({"receipt": receipt, "summary": report}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
