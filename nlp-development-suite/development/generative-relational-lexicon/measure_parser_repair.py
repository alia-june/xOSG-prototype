from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
DECISION_PATH = ROOT / "PARSER_REPAIR_DECISION.json"
PILOT_RECEIPT_PATH = ROOT / "pilot" / "tier-zero" / "output" / "PILOT_RECEIPT.json"
COMPARISON_REPORT_PATH = ROOT / "pilot" / "modern-comparison" / "DISCREPANCY_SHAPE_REPORT.json"
NORMALIZATION_REPORT_PATH = ROOT / "pilot" / "modern-comparison" / "normalization-audit" / "NORMALIZATION_SHAPE_REPORT.json"
UNRESOLVED_REPORT_PATH = ROOT / "pilot" / "modern-comparison" / "normalization-audit" / "unresolved-shapes" / "UNRESOLVED_SHAPE_REPORT.json"
SAMPLE_REPORT_PATH = ROOT / "pilot" / "modern-comparison" / "normalization-audit" / "review-sample" / "REVIEW_SAMPLE_REPORT.json"
DISPOSITION_REPORT_PATH = ROOT / "pilot" / "modern-comparison" / "normalization-audit" / "review-sample" / "dispositions" / "REVIEW_DISPOSITION_REPORT.json"
REGRESSION_PATH = ROOT / "pilot" / "modern-comparison" / "normalization-audit" / "review-sample" / "dispositions" / "PARSER_REGRESSION_CANDIDATES.json"
OUTPUT_DIR = ROOT / "pilot" / "parser-repair"
REPORT_JSON_PATH = OUTPUT_DIR / "PARSER_REPAIR_DELTA_REPORT.json"
REPORT_MD_PATH = OUTPUT_DIR / "PARSER_REPAIR_DELTA_REPORT.md"
RECEIPT_PATH = OUTPUT_DIR / "PARSER_REPAIR_RECEIPT.json"
MEASURER_VERSION = "parser-repair-delta/1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def baseline_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=REPO_ROOT)


def validate_decision(decision: dict[str, object]) -> dict[str, dict[str, object]]:
    if decision.get("status") != "AUTHORIZED_TEST_PARSER_REPAIR":
        raise ValueError("parser repair is not authorized")
    if decision.get("authority_effect") != "TEST_PARSER_REPAIR_ONLY":
        raise ValueError("parser repair authority must remain test-only")
    for field in ("production_ready", "publication_allowed", "canon_admission"):
        if decision.get(field) is not False:
            raise ValueError(f"parser repair boundary changed: {field}")
    commit = str(decision["baseline_commit"])
    loaded = {}
    for artifact in decision["baseline_artifacts"]:
        data = baseline_bytes(commit, artifact["path"])
        if len(data) != artifact["bytes"]:
            raise ValueError(f"baseline byte count changed: {artifact['path']}")
        if sha256_bytes(data) != artifact["sha256"]:
            raise ValueError(f"baseline SHA-256 changed: {artifact['path']}")
        loaded[artifact["path"]] = json.loads(data)
    return loaded


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def metrics(
    pilot: dict[str, object],
    comparison: dict[str, object],
    normalization: dict[str, object],
    unresolved: dict[str, object],
    sample: dict[str, object],
    disposition: dict[str, object],
    regression: dict[str, object],
) -> dict[str, int | float | str]:
    shapes = unresolved["exclusive_primary_shape_counts"]
    return {
        "parser_version": pilot["parser_version"],
        "head_record_count": pilot["output"]["head_records"]["record_count"],
        "historical_membership_count": pilot["output"]["historical_memberships"]["record_count"],
        "historical_unique_term_count": comparison["historical_unique_term_count"],
        "exact_modern_lemma_count": comparison["exact_modern_lemma_count"],
        "exact_modern_lemma_percent": comparison["exact_modern_lemma_percent"],
        "no_exact_modern_lemma_count": comparison["no_exact_modern_lemma_count"],
        "remaining_unresolved_count": normalization["remaining_unresolved_count"],
        "reference_marker_shaped_count": shapes["REFERENCE_MARKER_SHAPED"],
        "delimiter_or_markup_shaped_count": shapes["DELIMITER_OR_MARKUP_SHAPED"],
        "numeric_mixed_shaped_count": shapes["NUMERIC_MIXED_SHAPED"],
        "sample_record_count": sample["sample_record_count"],
        "sample_confirmed_boundary_defect_count": disposition["disposition_counts"].get("PARSER_BOUNDARY_DEFECT_CONFIRMED", 0),
        "proposed_regression_candidate_count": len(regression["candidates"]),
    }


def build_report(decision: dict[str, object], baseline: dict[str, dict[str, object]]) -> dict[str, object]:
    suffix = "development/generative-relational-lexicon/"
    before = metrics(
        baseline[suffix + "pilot/tier-zero/output/PILOT_RECEIPT.json"],
        baseline[suffix + "pilot/modern-comparison/DISCREPANCY_SHAPE_REPORT.json"],
        baseline[suffix + "pilot/modern-comparison/normalization-audit/NORMALIZATION_SHAPE_REPORT.json"],
        baseline[suffix + "pilot/modern-comparison/normalization-audit/unresolved-shapes/UNRESOLVED_SHAPE_REPORT.json"],
        baseline[suffix + "pilot/modern-comparison/normalization-audit/review-sample/REVIEW_SAMPLE_REPORT.json"],
        baseline[suffix + "pilot/modern-comparison/normalization-audit/review-sample/dispositions/REVIEW_DISPOSITION_REPORT.json"],
        baseline[suffix + "pilot/modern-comparison/normalization-audit/review-sample/dispositions/PARSER_REGRESSION_CANDIDATES.json"],
    )
    current_regression = read_json(REGRESSION_PATH)
    current_disposition = read_json(DISPOSITION_REPORT_PATH)
    after = metrics(
        read_json(PILOT_RECEIPT_PATH),
        read_json(COMPARISON_REPORT_PATH),
        read_json(NORMALIZATION_REPORT_PATH),
        read_json(UNRESOLVED_REPORT_PATH),
        read_json(SAMPLE_REPORT_PATH),
        current_disposition,
        current_regression,
    )
    deltas = {}
    for key, value in before.items():
        if isinstance(value, (int, float)) and isinstance(after[key], (int, float)):
            deltas[key] = round(after[key] - value, 4)
    current_patterns = current_disposition["confirmed_defect_pattern_counts"]
    repaired_residuals = {
        pattern: current_patterns.get(pattern, 0)
        for pattern in decision["authorized_repeated_patterns"]
    }
    held_residuals = {
        pattern: current_patterns.get(pattern, 0)
        for pattern in decision["held_patterns"]
    }
    return {
        "schema": "parser-repair-delta-report/1",
        "status": "PASSED" if not any(repaired_residuals.values()) else "RESIDUAL_REPAIRED_PATTERN_FOUND",
        "authority_effect": "TEST_PARSER_REPAIR_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "baseline_commit": decision["baseline_commit"],
        "before": before,
        "after": after,
        "delta_after_minus_before": deltas,
        "authorized_pattern_residuals_in_new_sample": repaired_residuals,
        "held_pattern_observations_in_new_sample": held_residuals,
        "boundary": "Corpus deltas compare complete deterministic outputs. Review-sample counts compare different deterministic samples and are diagnostic observations, not population-rate estimates.",
    }


def render_markdown(report: dict[str, object]) -> str:
    keys = (
        "head_record_count",
        "historical_membership_count",
        "historical_unique_term_count",
        "exact_modern_lemma_count",
        "exact_modern_lemma_percent",
        "no_exact_modern_lemma_count",
        "remaining_unresolved_count",
        "reference_marker_shaped_count",
        "delimiter_or_markup_shaped_count",
        "numeric_mixed_shaped_count",
    )
    lines = [
        "# Parser repair delta report",
        "",
        f"Status: {report['status']}; internal test repair only.",
        "",
        "| Metric | Before | After | Delta |",
        "|---|---:|---:|---:|",
    ]
    for key in keys:
        lines.append(f"| `{key}` | {report['before'][key]} | {report['after'][key]} | {report['delta_after_minus_before'][key]} |")
    lines.extend(
        [
            "",
            "## Repaired-pattern residuals in the new sample",
            "",
        ]
    )
    for pattern, count in report["authorized_pattern_residuals_in_new_sample"].items():
        lines.append(f"- `{pattern}`: {count}")
    lines.extend(["", "## Boundary", "", report["boundary"]])
    return "\n".join(lines) + "\n"


def write_outputs(report: dict[str, object], decision: dict[str, object]) -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_bytes = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    REPORT_JSON_PATH.write_bytes(report_bytes)
    markdown_bytes = render_markdown(report).encode("utf-8")
    REPORT_MD_PATH.write_bytes(markdown_bytes)
    current_inputs = [
        PILOT_RECEIPT_PATH,
        COMPARISON_REPORT_PATH,
        NORMALIZATION_REPORT_PATH,
        UNRESOLVED_REPORT_PATH,
        SAMPLE_REPORT_PATH,
        DISPOSITION_REPORT_PATH,
        REGRESSION_PATH,
    ]
    receipt = {
        "schema": "parser-repair-receipt/1",
        "status": report["status"],
        "authority_effect": "TEST_PARSER_REPAIR_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "measurer_version": MEASURER_VERSION,
        "inputs": {
            "decision": {"sha256": sha256_path(DECISION_PATH)},
            "baseline_commit": decision["baseline_commit"],
            "current": {
                str(path.relative_to(ROOT)): {"bytes": path.stat().st_size, "sha256": sha256_path(path)}
                for path in current_inputs
            },
        },
        "outputs": {
            "report_json": {"relative_path": REPORT_JSON_PATH.name, "bytes": len(report_bytes), "sha256": sha256_bytes(report_bytes)},
            "report_markdown": {"relative_path": REPORT_MD_PATH.name, "bytes": len(markdown_bytes), "sha256": sha256_bytes(markdown_bytes)},
        },
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    return receipt


def main() -> int:
    decision = read_json(DECISION_PATH)
    baseline = validate_decision(decision)
    report = build_report(decision, baseline)
    receipt = write_outputs(report, decision)
    print(json.dumps({"receipt": receipt, "report": report}, sort_keys=True))
    return 0 if report["status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
