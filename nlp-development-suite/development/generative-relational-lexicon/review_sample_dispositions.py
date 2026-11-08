from __future__ import annotations

from collections import Counter, defaultdict
import gzip
import hashlib
import io
import json
from pathlib import Path
import re

import build_review_sample as review_sample


ROOT = Path(__file__).resolve().parent
DECISION_PATH = ROOT / "REVIEW_DISPOSITION_DECISION.json"
SAMPLE_RECEIPT_PATH = review_sample.RECEIPT_PATH
OUTPUT_DIR = review_sample.OUTPUT_DIR / "dispositions"
RECORDS_PATH = OUTPUT_DIR / "reviewed-sample-records.jsonl.gz"
REPORT_JSON_PATH = OUTPUT_DIR / "REVIEW_DISPOSITION_REPORT.json"
REPORT_MD_PATH = OUTPUT_DIR / "REVIEW_DISPOSITION_REPORT.md"
REGRESSION_PATH = OUTPUT_DIR / "PARSER_REGRESSION_CANDIDATES.json"
RECEIPT_PATH = OUTPUT_DIR / "REVIEW_DISPOSITION_RECEIPT.json"
REVIEWER_VERSION = "raw-source-disposition-review/1"

PATTERN_DESCRIPTIONS = {
    "SUFFIXED_HEAD_HEADING_CAPTURE": "A suffixed Roget head line such as #847a. was not recognized as a head boundary and entered the prior head's candidate stream.",
    "BRACKET_ANNOTATION_SPLIT": "A bracket annotation containing punctuation was split before annotation removal, leaving a partial label in the candidate.",
    "STANDALONE_HEADING_CAPTURE": "A numbered or uppercase standalone structural heading entered the candidate stream.",
    "BARE_HEAD_NUMBER_SUFFIX_CAPTURE": "A trailing bare Roget head number remained attached to a source surface candidate.",
    "BRACE_CROSS_REFERENCE_FRAGMENT": "A brace-delimited cross-reference fragment remained attached to the following candidate text.",
    "SQUARE_BRACKET_FRAGMENT": "A square-bracket annotation fragment was split from its opening bracket and entered the candidate stream.",
    "LEADING_FOOTNOTE_MARKER_CAPTURE": "A leading numeric footnote marker remained attached to source prose admitted as a candidate.",
    "BARE_SUFFIXED_HEAD_MARKER_CAPTURE": "A bare suffixed-head marker without its leading hash was admitted as a candidate.",
    "GROUPED_NUMBER_SPLIT": "A comma inside a grouped number was treated as a candidate delimiter.",
}

REGRESSION_EXPECTATIONS = {
    "SUFFIXED_HEAD_HEADING_CAPTURE": "Recognize #<number><letter>. as a structural head boundary and exclude the heading marker from lexical candidates.",
    "BRACKET_ANNOTATION_SPLIT": "Remove or protect complete bracket annotations before splitting on periods, commas, or newlines.",
    "STANDALONE_HEADING_CAPTURE": "Exclude numbered and uppercase standalone structural headings from lexical candidates.",
    "BARE_HEAD_NUMBER_SUFFIX_CAPTURE": "Preserve a trailing head number as relation evidence, not as part of the lexical surface.",
    "BRACE_CROSS_REFERENCE_FRAGMENT": "Remove complete brace-delimited cross-reference structures before candidate segmentation.",
    "SQUARE_BRACKET_FRAGMENT": "Protect multiline or delimiter-containing square-bracket annotations before candidate segmentation.",
    "LEADING_FOOTNOTE_MARKER_CAPTURE": "Distinguish a leading numeric footnote marker from the prose that follows it.",
    "BARE_SUFFIXED_HEAD_MARKER_CAPTURE": "Recognize a bare suffixed-head marker when it occurs in structural source context.",
    "GROUPED_NUMBER_SPLIT": "Protect commas inside grouped numbers before candidate segmentation.",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_decision(decision: dict[str, object]) -> dict[str, object]:
    if decision.get("status") != "AUTHORIZED_TEST_REVIEW_DISPOSITIONS":
        raise ValueError("review dispositions are not authorized")
    if decision.get("authority_effect") != "TEST_REVIEW_DISPOSITIONS_ONLY":
        raise ValueError("review disposition authority must remain test-only")
    for field in (
        "production_ready",
        "publication_allowed",
        "canon_admission",
        "parser_repair_allowed",
        "lexical_validity_assignment_allowed",
    ):
        if decision.get(field) is not False:
            raise ValueError(f"review disposition boundary changed: {field}")
    allowed = decision.get("allowed_dispositions")
    if allowed != ["PARSER_BOUNDARY_DEFECT_CONFIRMED", "RAW_LITERAL_PRESENT_NO_LISTED_DEFECT", "REVIEW_REQUIRED"]:
        raise ValueError("review disposition vocabulary changed")
    pin = decision.get("review_sample_receipt")
    if not isinstance(pin, dict):
        raise ValueError("review sample receipt pin is missing")
    if SAMPLE_RECEIPT_PATH.stat().st_size != pin.get("bytes"):
        raise ValueError("review sample receipt byte count changed")
    if review_sample.sha256_path(SAMPLE_RECEIPT_PATH) != pin.get("sha256"):
        raise ValueError("review sample receipt SHA-256 changed")
    receipt = json.loads(SAMPLE_RECEIPT_PATH.read_text(encoding="utf-8"))
    if receipt.get("status") != "PASSED":
        raise ValueError("review sample is not passed")
    for output in receipt.get("outputs", {}).values():
        path = SAMPLE_RECEIPT_PATH.parent / output["relative_path"]
        if review_sample.sha256_path(path) != output["sha256"]:
            raise ValueError(f"review sample output changed: {path.name}")
    return receipt


def load_sample() -> list[dict[str, object]]:
    records = []
    with gzip.open(review_sample.RECORDS_PATH, "rt", encoding="utf-8") as stream:
        for line in stream:
            records.append(json.loads(line))
    return records


def raw_lines(record: dict[str, object]) -> list[str]:
    return [line for block in record["raw_source_blocks"] for line in block["text"].splitlines()]


def literal_lines(term: str, lines: list[str]) -> list[str]:
    folded = term.casefold()
    return [line for line in lines if folded in line.casefold()]


def exact_positions(term: str, line: str) -> list[int]:
    folded_term = term.casefold()
    folded_line = line.casefold()
    positions = []
    start = 0
    while True:
        index = folded_line.find(folded_term, start)
        if index < 0:
            return positions
        positions.append(index)
        start = index + max(1, len(folded_term))


def defect_result(pattern: str, lines: list[str]) -> dict[str, object]:
    return {
        "review_disposition": "PARSER_BOUNDARY_DEFECT_CONFIRMED",
        "defect_pattern": pattern,
        "review_basis": PATTERN_DESCRIPTIONS[pattern],
        "evidence_lines": lines[:5],
    }


def review_record(record: dict[str, object]) -> dict[str, object]:
    term = record["historical_term"]
    lines = raw_lines(record)
    hits = literal_lines(term, lines)
    folded = term.casefold()

    if re.fullmatch(r"#\d+[a-z]", term, re.IGNORECASE):
        evidence = [line for line in lines if re.match(r"^\s*" + re.escape(term) + r"\.", line, re.IGNORECASE)]
        if evidence:
            result = defect_result("SUFFIXED_HEAD_HEADING_CAPTURE", evidence)
            return record | result | {"lexical_validity": None}

    if "[" in term and "]" not in term:
        evidence = []
        for line in hits:
            position = line.casefold().find(folded)
            if "]" in line[position + len(term):]:
                evidence.append(line)
        if evidence:
            result = defect_result("BRACKET_ANNOTATION_SPLIT", evidence)
            return record | result | {"lexical_validity": None}

    if "}" in term and hits:
        result = defect_result("BRACE_CROSS_REFERENCE_FRAGMENT", hits)
        return record | result | {"lexical_validity": None}

    if "]" in term and "[" not in term and hits:
        result = defect_result("SQUARE_BRACKET_FRAGMENT", hits)
        return record | result | {"lexical_validity": None}

    heading_evidence = []
    for line in lines:
        cleaned = line.strip().strip("_").lstrip("(").casefold()
        if cleaned == folded and (
            re.match(r"^(?:\d+|[ivxlcdm]+)\)", folded, re.IGNORECASE)
            or line.strip().strip("_").isupper()
        ):
            heading_evidence.append(line)
    if heading_evidence:
        result = defect_result("STANDALONE_HEADING_CAPTURE", heading_evidence)
        return record | result | {"lexical_validity": None}

    grouped_evidence = []
    for line in hits:
        for position in exact_positions(term, line):
            if re.match(r",\d{3}(?:,\d{3})*", line[position + len(term):]):
                grouped_evidence.append(line)
    if grouped_evidence:
        result = defect_result("GROUPED_NUMBER_SPLIT", grouped_evidence)
        return record | result | {"lexical_validity": None}

    if re.fullmatch(r"\d{1,3}[a-z]", term, re.IGNORECASE):
        evidence = [line for line in lines if line.lstrip().casefold().startswith(folded)]
        if evidence:
            result = defect_result("BARE_SUFFIXED_HEAD_MARKER_CAPTURE", evidence)
            return record | result | {"lexical_validity": None}

    if re.match(r"^\d+[a-z]", term, re.IGNORECASE):
        evidence = [line for line in lines if line.lstrip().casefold().startswith(folded)]
        if evidence:
            result = defect_result("LEADING_FOOTNOTE_MARKER_CAPTURE", evidence)
            return record | result | {"lexical_validity": None}

    suffix = re.search(r"\s([1-9]\d{0,2})([a-b]?)$", term, re.IGNORECASE)
    if suffix and int(suffix.group(1)) <= 1000 and hits:
        result = defect_result("BARE_HEAD_NUMBER_SUFFIX_CAPTURE", hits)
        return record | result | {"lexical_validity": None}

    if hits:
        return record | {
            "review_disposition": "RAW_LITERAL_PRESENT_NO_LISTED_DEFECT",
            "defect_pattern": None,
            "review_basis": "The candidate occurs literally in the pinned raw source block and none of the accepted defect discriminators matched.",
            "evidence_lines": hits[:5],
            "lexical_validity": None,
        }

    return record | {
        "review_disposition": "REVIEW_REQUIRED",
        "defect_pattern": None,
        "review_basis": "The normalized candidate was not located literally in its attached raw source blocks; transformation or fragmentation remains unresolved.",
        "evidence_lines": [],
        "lexical_validity": None,
    }


def build_regression_candidates(records: list[dict[str, object]], minimum: int) -> dict[str, object]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        if record["review_disposition"] == "PARSER_BOUNDARY_DEFECT_CONFIRMED":
            grouped[record["defect_pattern"]].append(record)
    candidates = []
    held_singletons = []
    for pattern, matches in sorted(grouped.items()):
        item = {
            "pattern": pattern,
            "sample_occurrences": len(matches),
            "expected_guard": REGRESSION_EXPECTATIONS[pattern],
            "example_terms": sorted(record["historical_term"] for record in matches)[:5],
            "effect": "PROPOSED_TEST_ONLY",
        }
        if len(matches) >= minimum:
            candidates.append(item)
        else:
            held_singletons.append(item)
    return {
        "schema": "parser-regression-candidates/1",
        "status": "GENERATED_PROPOSAL",
        "parser_repair_allowed": False,
        "minimum_sample_occurrences": minimum,
        "candidates": candidates,
        "held_below_threshold": held_singletons,
        "boundary": "These are proposed regression guards derived from repeated sample evidence. They do not authorize parser mutation or corpus deletion.",
    }


def summarize(records: list[dict[str, object]], regression: dict[str, object]) -> dict[str, object]:
    dispositions = Counter(record["review_disposition"] for record in records)
    patterns = Counter(
        record["defect_pattern"]
        for record in records
        if record["defect_pattern"] is not None
    )
    return {
        "schema": "review-disposition-report/1",
        "status": "GENERATED_TEST_REVIEW",
        "authority_effect": "TEST_REVIEW_DISPOSITIONS_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "parser_repair_allowed": False,
        "lexical_validity_assignment_allowed": False,
        "sample_record_count": len(records),
        "disposition_counts": dict(sorted(dispositions.items())),
        "confirmed_defect_pattern_counts": dict(sorted(patterns.items())),
        "proposed_regression_candidate_count": len(regression["candidates"]),
        "held_below_threshold_count": len(regression["held_below_threshold"]),
        "interpretation_boundary": "A parser-boundary disposition is scoped to the sampled raw-source occurrence. Literal presence does not establish lexical validity, and unsampled records receive no disposition.",
    }


def render_markdown(report: dict[str, object], regression: dict[str, object]) -> str:
    lines = [
        "# Raw-source review dispositions",
        "",
        "Status: generated internal sample review; parser repair remains unauthorized.",
        "",
        f"- Sample records reviewed: {report['sample_record_count']}",
        f"- Confirmed parser-boundary defects: {report['disposition_counts'].get('PARSER_BOUNDARY_DEFECT_CONFIRMED', 0)}",
        f"- Literal raw occurrences with no listed defect: {report['disposition_counts'].get('RAW_LITERAL_PRESENT_NO_LISTED_DEFECT', 0)}",
        f"- Review required: {report['disposition_counts'].get('REVIEW_REQUIRED', 0)}",
        "",
        "## Confirmed defect patterns",
        "",
        "| Pattern | Sample occurrences | Regression status |",
        "|---|---:|---|",
    ]
    proposed = {item["pattern"] for item in regression["candidates"]}
    for pattern, count in report["confirmed_defect_pattern_counts"].items():
        status = "PROPOSED_TEST_ONLY" if pattern in proposed else "HELD_BELOW_THRESHOLD"
        lines.append(f"| `{pattern}` | {count} | `{status}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            report["interpretation_boundary"],
            regression["boundary"],
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(records: list[dict[str, object]], report: dict[str, object], regression: dict[str, object], sample_receipt: dict[str, object]) -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = "".join(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n" for record in records).encode("utf-8")
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as stream:
        stream.write(raw)
    compressed = buffer.getvalue()
    RECORDS_PATH.write_bytes(compressed)
    report_bytes = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    REPORT_JSON_PATH.write_bytes(report_bytes)
    regression_bytes = (json.dumps(regression, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    REGRESSION_PATH.write_bytes(regression_bytes)
    markdown_bytes = render_markdown(report, regression).encode("utf-8")
    REPORT_MD_PATH.write_bytes(markdown_bytes)
    receipt = {
        "schema": "review-disposition-receipt/1",
        "status": "PASSED",
        "authority_effect": "TEST_REVIEW_DISPOSITIONS_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "parser_repair_allowed": False,
        "reviewer_version": REVIEWER_VERSION,
        "inputs": {
            "decision": {"sha256": review_sample.sha256_path(DECISION_PATH)},
            "review_sample_receipt": {"sha256": review_sample.sha256_path(SAMPLE_RECEIPT_PATH)},
            "review_sample_records": sample_receipt["outputs"]["records"],
            "source": sample_receipt["inputs"]["source"],
        },
        "outputs": {
            "records": {"relative_path": RECORDS_PATH.name, "record_count": len(records), "bytes": len(compressed), "uncompressed_bytes": len(raw), "sha256": sha256_bytes(compressed)},
            "report_json": {"relative_path": REPORT_JSON_PATH.name, "bytes": len(report_bytes), "sha256": sha256_bytes(report_bytes)},
            "report_markdown": {"relative_path": REPORT_MD_PATH.name, "bytes": len(markdown_bytes), "sha256": sha256_bytes(markdown_bytes)},
            "regression_candidates": {"relative_path": REGRESSION_PATH.name, "bytes": len(regression_bytes), "sha256": sha256_bytes(regression_bytes)},
        },
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return receipt


def main() -> int:
    decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
    sample_receipt = validate_decision(decision)
    reviewed = [review_record(record) for record in load_sample()]
    regression = build_regression_candidates(reviewed, int(decision["regression_candidate_minimum_occurrences"]))
    report = summarize(reviewed, regression)
    receipt = write_outputs(reviewed, report, regression, sample_receipt)
    print(json.dumps({"receipt": receipt, "summary": report}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
