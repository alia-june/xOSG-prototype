from __future__ import annotations

from collections import Counter, defaultdict
import gzip
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DECISION_PATH = ROOT / "SENSE_REVIEW_SAMPLE_DECISION.json"
SOURCE_PATH = ROOT / "pilot" / "tier-zero" / "raw" / "project-gutenberg-ebook-22.txt"
MEMBERSHIPS_PATH = ROOT / "pilot" / "tier-zero" / "output" / "roget-historical-memberships.jsonl.gz"
DISCREPANCY_PATH = ROOT / "pilot" / "modern-comparison" / "roget-oewn-discrepancy-records.jsonl.gz"
NORMALIZATION_PATH = ROOT / "pilot" / "modern-comparison" / "normalization-audit" / "surface-normalization-candidates.jsonl.gz"
UNRESOLVED_PATH = ROOT / "pilot" / "modern-comparison" / "normalization-audit" / "unresolved-shapes" / "unresolved-shape-records.jsonl.gz"
OUTPUT_DIR = ROOT / "pilot" / "sense-aboutness" / "review-sample"
RECORDS_PATH = OUTPUT_DIR / "blank-review-records.jsonl.gz"
REPORT_PATH = OUTPUT_DIR / "SENSE_REVIEW_SAMPLE_REPORT.json"
REPORT_MD_PATH = OUTPUT_DIR / "SENSE_REVIEW_SAMPLE_REPORT.md"
RECEIPT_PATH = OUTPUT_DIR / "SENSE_REVIEW_SAMPLE_RECEIPT.json"
BUILDER_VERSION = "sense-aboutness-blank-review-sample/1"
NULL_REVIEW_FIELDS = (
    "reviewer_id",
    "reviewed_at",
    "review_status",
    "sense_candidates",
    "aboutness_assertions",
    "abstention",
    "review_notes",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_decision(decision: dict[str, Any]) -> None:
    if decision.get("status") != "AUTHORIZED_TEST_BLANK_REVIEW_SAMPLE":
        raise ValueError("blank sense-review sample is not authorized")
    if decision.get("authority_effect") != "TEST_BLANK_REVIEW_PACKAGE_ONLY":
        raise ValueError("authority effect must remain blank-review-package only")
    for field in (
        "production_ready",
        "publication_allowed",
        "canon_admission",
        "review_disposition_assignment_allowed",
        "semantic_candidate_generation_allowed",
    ):
        if decision.get(field) is not False:
            raise ValueError(f"review-sample boundary changed: {field}")
    for pin in decision["pinned_receipts"]:
        path = ROOT / pin["path"]
        if path.stat().st_size != pin["bytes"]:
            raise ValueError(f"pinned receipt byte count changed: {pin['path']}")
        if sha256_path(path) != pin["sha256"]:
            raise ValueError(f"pinned receipt SHA-256 changed: {pin['path']}")
        if read_json(path).get("status") != "PASSED":
            raise ValueError(f"pinned receipt is not passed: {pin['path']}")
    if tuple(decision["review_template"]["fields_required_null"]) != NULL_REVIEW_FIELDS:
        raise ValueError("blank review field contract changed")


def load_gzip_index(path: Path, key: str) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            value = record[key]
            if value in records:
                raise ValueError(f"duplicate {key} in {path.name}: {value}")
            records[value] = record
    return records


def collision_bucket(count: int) -> str:
    if count == 0:
        return "0"
    if count == 1:
        return "1"
    return "2_PLUS"


def stratum_for(
    discrepancy: dict[str, Any],
    normalization: dict[str, Any] | None,
    unresolved: dict[str, Any] | None,
) -> dict[str, str]:
    if discrepancy["modern_exact_lemma"]:
        match_layer = "EXACT_MODERN_LEMMA"
        collision_count = int(discrepancy["modern_entry_count"])
    elif normalization and normalization.get("first_recovery_layer"):
        match_layer = str(normalization["first_recovery_layer"])
        collision_count = int(normalization["modern_surface_collision_count"])
    else:
        match_layer = "UNRESOLVED"
        collision_count = 0
    return {
        "match_layer": match_layer,
        "historical_head_bucket": str(discrepancy["historical_head_bucket"]),
        "historical_pos_signature": "+".join(discrepancy["historical_pos_markers"]) or "NONE",
        "source_label_bucket": "ATTACHED" if discrepancy["source_bracket_label_count"] else "NONE",
        "modern_sense_count_bucket": str(discrepancy["sense_count_bucket"]),
        "modern_surface_collision_bucket": collision_bucket(collision_count),
        "unresolved_primary_shape": str(unresolved["primary_shape"]) if unresolved else "NOT_UNRESOLVED",
    }


def canonical_stratum(stratum: dict[str, str]) -> str:
    return json.dumps(stratum, sort_keys=True, separators=(",", ":"))


def choose_sample(
    discrepancies: dict[str, dict[str, Any]],
    normalizations: dict[str, dict[str, Any]],
    unresolved_records: dict[str, dict[str, Any]],
    source_sha256: str,
    maximum: int,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    strata: dict[str, list[tuple[str, str, dict[str, str]]]] = defaultdict(list)
    for term, discrepancy in discrepancies.items():
        stratum = stratum_for(discrepancy, normalizations.get(term), unresolved_records.get(term))
        key = canonical_stratum(stratum)
        material = "|".join((source_sha256, term, key)).encode("utf-8")
        rank = hashlib.sha256(material).hexdigest()
        strata[key].append((rank, term, stratum))
    selected: list[dict[str, Any]] = []
    sizes: Counter[str] = Counter()
    for key in sorted(strata):
        ranked = sorted(strata[key], key=lambda item: (item[0], item[1]))
        sizes[key] = len(ranked)
        for rank, term, stratum in ranked[:maximum]:
            selected.append(
                {
                    "normalized_term": term,
                    "stratum": stratum,
                    "stratum_key": key,
                    "population_stratum_size": len(ranked),
                    "selection_rank": rank,
                }
            )
    selected.sort(key=lambda item: (item["stratum_key"], item["selection_rank"], item["normalized_term"]))
    return selected, sizes


def load_selected_memberships(selected_terms: set[str]) -> dict[str, list[dict[str, Any]]]:
    memberships: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with gzip.open(MEMBERSHIPS_PATH, "rt", encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            term = record["normalized_term"]
            if term in selected_terms:
                memberships[term].append(record)
    missing = selected_terms.difference(memberships)
    if missing:
        raise ValueError(f"sample terms lack historical memberships: {sorted(missing)[:5]}")
    return memberships


def source_membership_evidence(
    memberships: list[dict[str, Any]], source_lines: list[str]
) -> list[dict[str, Any]]:
    evidence = []
    for membership in sorted(
        memberships,
        key=lambda item: (
            item["source_line_start"],
            item["source_line_end"],
            item["head_id"],
            item["part_of_speech_marker"],
        ),
    ):
        start = int(membership["source_line_start"])
        end = int(membership["source_line_end"])
        if start < 1 or end < start or end > len(source_lines):
            raise ValueError(f"invalid source span {start}-{end} for {membership['normalized_term']}")
        evidence.append(
            {
                "head_id": membership["head_id"],
                "head_number": membership["head_number"],
                "heading": membership["heading"],
                "part_of_speech_marker": membership["part_of_speech_marker"],
                "source_bracket_labels": membership.get("source_bracket_labels", []),
                "source_line_start": start,
                "source_line_end": end,
                "raw_source_text": "\n".join(source_lines[start - 1 : end]),
            }
        )
    return evidence


def build_records(
    selected: list[dict[str, Any]],
    discrepancies: dict[str, dict[str, Any]],
    normalizations: dict[str, dict[str, Any]],
    unresolved_records: dict[str, dict[str, Any]],
    memberships: dict[str, list[dict[str, Any]]],
    source_lines: list[str],
    source_sha256: str,
) -> list[dict[str, Any]]:
    records = []
    for sample_index, item in enumerate(selected, 1):
        term = item["normalized_term"]
        discrepancy = discrepancies[term]
        normalization = normalizations.get(term)
        unresolved = unresolved_records.get(term)
        historical_memberships = source_membership_evidence(memberships[term], source_lines)
        review = {field: None for field in NULL_REVIEW_FIELDS}
        records.append(
            {
                "schema": "sense-aboutness-blank-review-record/1",
                "sample_id": f"sense-review-{sample_index:04d}",
                "normalized_term": term,
                "historical_surfaces": discrepancy["historical_surfaces"],
                "selection": item,
                "historical_evidence": {
                    "source_id": "project-gutenberg-roget-22",
                    "source_sha256": source_sha256,
                    "head_ids": discrepancy["historical_head_ids"],
                    "head_numbers": discrepancy["historical_head_numbers"],
                    "part_of_speech_markers": discrepancy["historical_pos_markers"],
                    "memberships": historical_memberships,
                },
                "modern_shape_evidence": {
                    "exact_lemma": discrepancy["modern_exact_lemma"],
                    "entry_count": discrepancy["modern_entry_count"],
                    "sense_count": discrepancy["modern_sense_count"],
                    "synset_count": discrepancy["modern_synset_count"],
                    "parts_of_speech": discrepancy["modern_pos"],
                    "discrepancy_shapes": discrepancy["discrepancy_shapes"],
                    "truth_state": discrepancy["truth_state"],
                },
                "normalization_evidence": normalization,
                "unresolved_shape_evidence": unresolved,
                "review": review,
                "authority_effect": "BLANK_REVIEW_ONLY",
            }
        )
    return records


def build_report(
    decision: dict[str, Any],
    records: list[dict[str, Any]],
    population_count: int,
    strata_sizes: Counter[str],
) -> dict[str, Any]:
    dimensions = decision["sampling_rule"]["strata"]
    counts_by_dimension = {
        dimension: dict(
            sorted(Counter(record["selection"]["stratum"][dimension] for record in records).items())
        )
        for dimension in dimensions
    }
    return {
        "schema": "sense-aboutness-review-sample-report/1",
        "status": "GENERATED_BLANK_TEST_REVIEW_PACKAGE",
        "authority_effect": "TEST_BLANK_REVIEW_PACKAGE_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "review_disposition_assignment_allowed": False,
        "semantic_candidate_generation_allowed": False,
        "population_record_count": population_count,
        "observed_stratum_count": len(strata_sizes),
        "sample_record_count": len(records),
        "maximum_per_observed_stratum": decision["sampling_rule"]["maximum_per_observed_stratum"],
        "counts_by_dimension": counts_by_dimension,
        "null_review_field_count": sum(
            value is None for record in records for value in record["review"].values()
        ),
        "sampling_boundary": "One deterministically selected record represents each observed seven-axis stratum. This is a structural coverage set, not a population-weighted sample and not evidence of semantic accuracy.",
        "review_boundary": "All reviewer fields are null. Source text and comparison shapes are evidence for human review only; no sense, aboutness, abstention, definition, or lexical-validity judgment is prefilled.",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Sense-aboutness blank review sample",
        "",
        "Status: generated internal blank review package; no semantic judgment assigned.",
        "",
        f"- Population records: {report['population_record_count']}",
        f"- Observed seven-axis strata: {report['observed_stratum_count']}",
        f"- Selected records: {report['sample_record_count']}",
        f"- Null reviewer fields: {report['null_review_field_count']}",
        "",
        "## Coverage",
        "",
    ]
    for dimension, counts in report["counts_by_dimension"].items():
        lines.append(f"- `{dimension}`: " + ", ".join(f"{key}={value}" for key, value in counts.items()))
    lines.extend(
        [
            "",
            "## Boundaries",
            "",
            report["sampling_boundary"],
            "",
            report["review_boundary"],
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(
    decision: dict[str, Any], records: list[dict[str, Any]], report: dict[str, Any]
) -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = "".join(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n" for record in records).encode("utf-8")
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as stream:
        stream.write(raw)
    compressed = buffer.getvalue()
    RECORDS_PATH.write_bytes(compressed)
    report_bytes = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    REPORT_PATH.write_bytes(report_bytes)
    markdown_bytes = render_markdown(report).encode("utf-8")
    REPORT_MD_PATH.write_bytes(markdown_bytes)
    inputs = (SOURCE_PATH, MEMBERSHIPS_PATH, DISCREPANCY_PATH, NORMALIZATION_PATH, UNRESOLVED_PATH)
    receipt = {
        "schema": "sense-aboutness-review-sample-receipt/1",
        "status": "PASSED",
        "authority_effect": "TEST_BLANK_REVIEW_PACKAGE_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "builder_version": BUILDER_VERSION,
        "inputs": {
            "decision": {"bytes": DECISION_PATH.stat().st_size, "sha256": sha256_path(DECISION_PATH)},
            "artifacts": {
                str(path.relative_to(ROOT)): {"bytes": path.stat().st_size, "sha256": sha256_path(path)}
                for path in inputs
            },
        },
        "outputs": {
            "records": {
                "relative_path": RECORDS_PATH.name,
                "record_count": len(records),
                "bytes": len(compressed),
                "uncompressed_bytes": len(raw),
                "sha256": sha256_bytes(compressed),
            },
            "report_json": {
                "relative_path": REPORT_PATH.name,
                "bytes": len(report_bytes),
                "sha256": sha256_bytes(report_bytes),
            },
            "report_markdown": {
                "relative_path": REPORT_MD_PATH.name,
                "bytes": len(markdown_bytes),
                "sha256": sha256_bytes(markdown_bytes),
            },
        },
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return receipt


def main() -> int:
    decision = read_json(DECISION_PATH)
    validate_decision(decision)
    discrepancies = load_gzip_index(DISCREPANCY_PATH, "normalized_term")
    normalizations = load_gzip_index(NORMALIZATION_PATH, "historical_term")
    unresolved_records = load_gzip_index(UNRESOLVED_PATH, "historical_term")
    expected = decision["sampling_rule"]
    if len(discrepancies) != expected["expected_population_count"]:
        raise ValueError("review population count changed")
    source_sha256 = sha256_path(SOURCE_PATH)
    selected, strata_sizes = choose_sample(
        discrepancies,
        normalizations,
        unresolved_records,
        source_sha256,
        int(expected["maximum_per_observed_stratum"]),
    )
    if len(strata_sizes) != expected["expected_observed_stratum_count"]:
        raise ValueError("observed stratum count changed")
    if len(selected) != expected["expected_sample_count"]:
        raise ValueError("selected sample count changed")
    memberships = load_selected_memberships({item["normalized_term"] for item in selected})
    source_lines = SOURCE_PATH.read_text(encoding="utf-8").splitlines()
    records = build_records(
        selected,
        discrepancies,
        normalizations,
        unresolved_records,
        memberships,
        source_lines,
        source_sha256,
    )
    report = build_report(decision, records, len(discrepancies), strata_sizes)
    receipt = write_outputs(decision, records, report)
    print(json.dumps({"receipt": receipt, "summary": report}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
