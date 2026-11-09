from __future__ import annotations

from collections import Counter, defaultdict
import gzip
import hashlib
import io
import json
from pathlib import Path
import re

import audit_surface_normalization as normalization
import compare_roget_oewn as baseline


ROOT = Path(__file__).resolve().parent
DECISION_PATH = ROOT / "UNRESOLVED_SHAPE_AUDIT_DECISION.json"
NORMALIZATION_RECEIPT_PATH = normalization.RECEIPT_PATH
OUTPUT_DIR = normalization.OUTPUT_DIR / "unresolved-shapes"
RECORDS_PATH = OUTPUT_DIR / "unresolved-shape-records.jsonl.gz"
REPORT_JSON_PATH = OUTPUT_DIR / "UNRESOLVED_SHAPE_REPORT.json"
REPORT_MD_PATH = OUTPUT_DIR / "UNRESOLVED_SHAPE_REPORT.md"
RECEIPT_PATH = OUTPUT_DIR / "UNRESOLVED_SHAPE_AUDIT_RECEIPT.json"
AUDITOR_VERSION = "unresolved-surface-shapes/1"

LETTER_TOKEN = r"[^\W\d_]+(?:[-'’][^\W\d_]+)*"
SINGLE_TOKEN_RE = re.compile(rf"{LETTER_TOKEN}$", re.UNICODE)
MULTI_TOKEN_RE = re.compile(rf"{LETTER_TOKEN}(?: {LETTER_TOKEN})+$", re.UNICODE)
REFERENCE_MARKER_RE = re.compile(r"^(?:#|\d+[a-z]?\s*(?:\]|\})|\d+\)\s*)", re.IGNORECASE)
DELIMITER_OR_MARKUP_RE = re.compile(r"[\[\]{}()|*]")

PRIMARY_SHAPES = (
    "REFERENCE_MARKER_SHAPED",
    "DELIMITER_OR_MARKUP_SHAPED",
    "NUMERIC_MIXED_SHAPED",
    "SINGLE_TOKEN_LETTER_SHAPED",
    "MULTI_TOKEN_LETTER_SHAPED",
    "OTHER_SURFACE_SHAPED",
)

REVIEW_QUEUES = {
    "REFERENCE_MARKER_SHAPED": "REFERENCE_MARKER_REVIEW",
    "DELIMITER_OR_MARKUP_SHAPED": "DELIMITER_REVIEW",
    "NUMERIC_MIXED_SHAPED": "NUMERIC_REVIEW",
    "SINGLE_TOKEN_LETTER_SHAPED": "SINGLE_TOKEN_LEXICAL_REVIEW",
    "MULTI_TOKEN_LETTER_SHAPED": "MULTI_TOKEN_PHRASE_REVIEW",
    "OTHER_SURFACE_SHAPED": "OTHER_SURFACE_REVIEW",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_decision(decision: dict[str, object]) -> dict[str, object]:
    if decision.get("status") != "AUTHORIZED_TEST_AUDIT":
        raise ValueError("unresolved-shape audit is not authorized")
    if decision.get("authority_effect") != "TEST_AUDIT_ONLY":
        raise ValueError("unresolved-shape authority must remain test-only")
    for field in (
        "production_ready",
        "publication_allowed",
        "canon_admission",
        "lexical_validity_assignment_allowed",
        "cause_assignment_allowed",
    ):
        if decision.get(field) is not False:
            raise ValueError(f"unresolved-shape boundary changed: {field}")
    if tuple(decision.get("exclusive_primary_shapes", [])) != PRIMARY_SHAPES:
        raise ValueError("primary shape order changed")
    if decision.get("review_queue_effect") != "PROPOSAL_ONLY":
        raise ValueError("review queues must remain proposal-only")
    pin = decision.get("normalization_receipt")
    if not isinstance(pin, dict):
        raise ValueError("normalization receipt pin is missing")
    if NORMALIZATION_RECEIPT_PATH.stat().st_size != pin.get("bytes"):
        raise ValueError("normalization receipt byte count changed")
    if baseline.sha256_path(NORMALIZATION_RECEIPT_PATH) != pin.get("sha256"):
        raise ValueError("normalization receipt SHA-256 changed")
    receipt = json.loads(NORMALIZATION_RECEIPT_PATH.read_text(encoding="utf-8"))
    if receipt.get("status") != "PASSED":
        raise ValueError("normalization audit is not passed")
    for output in receipt.get("outputs", {}).values():
        path = NORMALIZATION_RECEIPT_PATH.parent / output["relative_path"]
        if baseline.sha256_path(path) != output["sha256"]:
            raise ValueError(f"normalization output changed: {path.name}")
    return receipt


def load_unresolved_terms() -> set[str]:
    unresolved = set()
    with gzip.open(normalization.RECORDS_PATH, "rt", encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            if record["first_recovery_layer"] is None:
                unresolved.add(record["historical_term"])
    return unresolved


def load_source_evidence(unresolved: set[str]) -> dict[str, dict[str, object]]:
    evidence: dict[str, dict[str, object]] = {}
    with gzip.open(baseline.HISTORICAL_PATH, "rt", encoding="utf-8") as stream:
        for line in stream:
            membership = json.loads(line)
            term = membership["normalized_term"]
            if term not in unresolved:
                continue
            item = evidence.setdefault(
                term,
                {
                    "surfaces": set(),
                    "head_ids": set(),
                    "head_numbers": set(),
                    "pos": set(),
                    "source_labels": set(),
                    "line_spans": set(),
                    "membership_count": 0,
                },
            )
            item["surfaces"].add(membership["term"])
            item["head_ids"].add(membership.get("head_id", str(membership["head_number"])))
            item["head_numbers"].add(membership["head_number"])
            item["pos"].add(membership["part_of_speech_marker"])
            item["source_labels"].update(membership.get("source_bracket_labels", []))
            item["line_spans"].add((membership["source_line_start"], membership["source_line_end"]))
            item["membership_count"] += 1
    if set(evidence) != unresolved:
        missing = sorted(unresolved - set(evidence))[:5]
        raise ValueError(f"unresolved terms missing source evidence: {missing}")
    return evidence


def primary_shape(term: str) -> str:
    if REFERENCE_MARKER_RE.search(term):
        return "REFERENCE_MARKER_SHAPED"
    if DELIMITER_OR_MARKUP_RE.search(term):
        return "DELIMITER_OR_MARKUP_SHAPED"
    if any(character.isdigit() for character in term):
        return "NUMERIC_MIXED_SHAPED"
    if SINGLE_TOKEN_RE.fullmatch(term):
        return "SINGLE_TOKEN_LETTER_SHAPED"
    if MULTI_TOKEN_RE.fullmatch(term):
        return "MULTI_TOKEN_LETTER_SHAPED"
    return "OTHER_SURFACE_SHAPED"


def surface_signatures(term: str, source: dict[str, object]) -> list[str]:
    signatures = []
    tests = (
        ("LEADING_HASH", term.startswith("#")),
        ("LEADING_ASTERISK", term.startswith("*")),
        ("HAS_DIGIT", any(character.isdigit() for character in term)),
        ("HAS_SQUARE_BRACKET", "[" in term or "]" in term),
        ("HAS_BRACE", "{" in term or "}" in term),
        ("HAS_PARENTHESIS", "(" in term or ")" in term),
        ("HAS_VERTICAL_BAR", "|" in term),
        ("HAS_ASTERISK", "*" in term),
        ("HAS_AMPERSAND", "&" in term),
        ("HAS_APOSTROPHE", "'" in term or "’" in term),
        ("HAS_HYPHEN_OR_DASH", any(character in term for character in "-‐‑‒–—―")),
        ("HAS_NON_ASCII", any(ord(character) > 127 for character in term)),
        ("SOURCE_LABEL_ATTACHED", bool(source["source_labels"])),
        ("MULTIPLE_MEMBERSHIPS", int(source["membership_count"]) > 1),
        ("MULTIPLE_HEADS", len(source["head_ids"]) > 1),
        ("SIX_TOKEN_SEQUENCE", len(term.split()) == 6),
    )
    for label, present in tests:
        if present:
            signatures.append(label)
    return signatures


def build_records(
    unresolved: set[str],
    evidence: dict[str, dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    records = []
    shape_counts: Counter[str] = Counter()
    signature_counts: Counter[str] = Counter()
    queue_counts: Counter[str] = Counter()
    token_counts: Counter[str] = Counter()
    pos_counts: Counter[str] = Counter()
    source_label_counts: Counter[str] = Counter()
    for term in sorted(unresolved):
        source = evidence[term]
        shape = primary_shape(term)
        queue = REVIEW_QUEUES[shape]
        signatures = surface_signatures(term, source)
        shape_counts[shape] += 1
        signature_counts.update(signatures)
        queue_counts[queue] += 1
        tokens = len(term.split())
        token_counts[str(tokens)] += 1
        for marker in source["pos"]:
            pos_counts[str(marker)] += 1
        source_label_counts.update(str(label) for label in source["source_labels"])
        spans = sorted(source["line_spans"])
        records.append(
            {
                "schema": "unresolved-surface-shape/1",
                "truth_state": "DERIVED_SURFACE_CLASSIFICATION",
                "acceptance_state": "SHAPE_ONLY_REVIEW_PROPOSAL",
                "historical_term": term,
                "historical_surfaces": sorted(source["surfaces"], key=lambda value: (value.casefold(), value)),
                "primary_shape": shape,
                "review_queue": queue,
                "review_queue_effect": "PROPOSAL_ONLY",
                "surface_signatures": signatures,
                "character_count": len(term),
                "token_count": tokens,
                "alphabetic_character_count": sum(character.isalpha() for character in term),
                "digit_character_count": sum(character.isdigit() for character in term),
                "punctuation_characters": sorted(
                    {character for character in term if not character.isalnum() and not character.isspace()}
                ),
                "historical_membership_count": source["membership_count"],
                "historical_head_ids": sorted(source["head_ids"]),
                "historical_head_numbers": sorted(source["head_numbers"]),
                "historical_pos_markers": sorted(source["pos"]),
                "source_bracket_labels": sorted(source["source_labels"], key=lambda value: (value.casefold(), value)),
                "source_line_spans": [list(span) for span in spans],
                "lexical_validity": None,
                "cause": None,
            }
        )
    total = len(records)
    report = {
        "schema": "unresolved-surface-shape-report/1",
        "status": "GENERATED_TEST_RESULT",
        "authority_effect": "TEST_AUDIT_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "lexical_validity_assignment_allowed": False,
        "cause_assignment_allowed": False,
        "unresolved_term_count": total,
        "exclusive_primary_shape_counts": {shape: shape_counts[shape] for shape in PRIMARY_SHAPES},
        "review_queue_counts": dict(sorted(queue_counts.items())),
        "surface_signature_counts": dict(sorted(signature_counts.items())),
        "token_count_distribution": dict(sorted(token_counts.items(), key=lambda item: int(item[0]))),
        "historical_pos_membership_counts": dict(sorted(pos_counts.items())),
        "source_label_attached_term_count": signature_counts["SOURCE_LABEL_ATTACHED"],
        "top_source_bracket_labels": [
            {"label": label, "term_count": count}
            for label, count in sorted(
                source_label_counts.items(),
                key=lambda item: (-item[1], item[0].casefold(), item[0]),
            )[:25]
        ],
        "source_label_boundary": "Bracket labels are retained as literal source evidence and are not automatically interpreted as citations, languages, domains, authors, or works.",
        "interpretation_boundary": "Shape labels describe visible characters and source structure only; they do not establish lexical validity, extraction error, citation status, obsolescence, or semantic cause.",
    }
    return records, report


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Unresolved Roget candidate shape map",
        "",
        "Status: generated internal test evidence; review queues are proposals only.",
        "",
        f"Unresolved candidates classified: {report['unresolved_term_count']}",
        "",
        "## Exclusive visible shapes",
        "",
        "| Shape | Count | Proposed review queue |",
        "|---|---:|---|",
    ]
    for shape in PRIMARY_SHAPES:
        queue = REVIEW_QUEUES[shape]
        lines.append(f"| `{shape}` | {report['exclusive_primary_shape_counts'][shape]} | `{queue}` |")
    lines.extend(
        [
            "",
            "## Source and surface signals",
            "",
            f"- Terms with attached source bracket labels: {report['source_label_attached_term_count']}",
            f"- Terms containing digits: {report['surface_signature_counts'].get('HAS_DIGIT', 0)}",
            f"- Terms containing square brackets: {report['surface_signature_counts'].get('HAS_SQUARE_BRACKET', 0)}",
            f"- Terms containing vertical bars: {report['surface_signature_counts'].get('HAS_VERTICAL_BAR', 0)}",
            f"- Terms beginning with `#`: {report['surface_signature_counts'].get('LEADING_HASH', 0)}",
            f"- Six-token sequences: {report['surface_signature_counts'].get('SIX_TOKEN_SEQUENCE', 0)}",
            "",
            "## Most frequent attached source bracket labels",
            "",
            "| Literal source label | Terms |",
            "|---|---:|",
        ]
    )
    for item in report["top_source_bracket_labels"][:10]:
        lines.append(f"| `{item['label']}` | {item['term_count']} |")
    lines.extend(
        [
            "",
            report["source_label_boundary"],
            "",
            "## Boundary",
            "",
            report["interpretation_boundary"],
            "`SINGLE_TOKEN_LETTER_SHAPED` means only that the candidate has one letter-based token under the recorded regular expression; it does not declare a word.",
            "`MULTI_TOKEN_LETTER_SHAPED` does not declare an idiom, quotation, or valid phrase.",
            "Attached bracket labels are preserved as source evidence and are not automatically interpreted as citations.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(
    records: list[dict[str, object]],
    report: dict[str, object],
    normalization_receipt: dict[str, object],
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
        "schema": "unresolved-surface-shape-audit-receipt/1",
        "status": "PASSED",
        "authority_effect": "TEST_AUDIT_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "auditor_version": AUDITOR_VERSION,
        "inputs": {
            "decision": {"sha256": baseline.sha256_path(DECISION_PATH)},
            "normalization_receipt": {"sha256": baseline.sha256_path(NORMALIZATION_RECEIPT_PATH)},
            "normalization_records": normalization_receipt["outputs"]["records"],
            "historical_memberships": normalization_receipt["inputs"]["historical_memberships"],
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
    normalization_receipt = validate_decision(decision)
    unresolved = load_unresolved_terms()
    evidence = load_source_evidence(unresolved)
    records, report = build_records(unresolved, evidence)
    receipt = write_outputs(records, report, normalization_receipt)
    print(json.dumps({"receipt": receipt, "summary": report}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
