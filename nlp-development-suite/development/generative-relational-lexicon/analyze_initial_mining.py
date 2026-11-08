from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MAP_PATH = ROOT / "SOURCE_LANGUAGE_MAP.json"
POLICY_PATH = ROOT / "INITIAL_MINING_LICENSE_POLICY.json"
REPORT_PATH = ROOT / "INITIAL_MINING_GAP_REPORT.json"
REPORT_MD_PATH = ROOT / "INITIAL_MINING_GAP_REPORT.md"
PILOT_DECISION_PATH = ROOT / "TIER_ZERO_PILOT_DECISION.json"


def analyze(
    source_map: dict[str, object],
    policy: dict[str, object],
    execution_decisions: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    if policy.get("authority_effect") != "NONE":
        raise ValueError("policy authority effect must remain NONE")
    if policy.get("content_ingestion_authorized") is not False:
        raise ValueError("policy must not authorize ingestion")
    if policy.get("allowed_rights_classes") != ["CC0-1.0", "PUBLIC_DOMAIN"]:
        raise ValueError("tier-zero rights classes changed")

    sources = source_map.get("sources")
    languages = source_map.get("languages")
    dimensions = source_map.get("evidence_dimensions")
    units = policy.get("eligible_units")
    if not all(isinstance(value, list) for value in (sources, languages, dimensions, units)):
        raise ValueError("map and policy collections must be lists")

    sources_by_id = {source["id"]: source for source in sources}
    unit_ids: set[str] = set()
    eligible_by_source: dict[str, set[str]] = {}
    for unit in units:
        source_id = unit.get("source_id")
        unit_id = unit.get("unit_id")
        if source_id not in sources_by_id:
            raise ValueError(f"unknown eligible source: {source_id}")
        if unit_id in unit_ids:
            raise ValueError(f"duplicate eligible unit: {unit_id}")
        unit_ids.add(unit_id)
        if unit.get("rights_class") not in policy["allowed_rights_classes"]:
            raise ValueError(f"ineligible rights class admitted: {unit_id}")
        if unit.get("selection_status") != "license_eligible_not_pinned":
            raise ValueError(f"eligible unit must remain unpinned: {unit_id}")
        unit_dimensions = set(unit.get("eligible_dimensions", []))
        source_dimensions = set(sources_by_id[source_id].get("dimensions", []))
        if not unit_dimensions or not unit_dimensions <= source_dimensions:
            raise ValueError(f"unit exceeds source dimensions: {unit_id}")
        eligible_by_source.setdefault(source_id, set()).update(unit_dimensions)

    deferred = policy.get("deferred_dimension")
    active_dimensions = set(dimensions) - {deferred}
    covered_dimensions = set().union(*eligible_by_source.values()) if eligible_by_source else set()
    global_holes = sorted(active_dimensions - covered_dimensions)

    language_coverage: list[dict[str, object]] = []
    for language in languages:
        language_dimensions = set(language.get("dimensions", [])) - {deferred}
        matching_sources = sorted(set(language.get("source_candidates", [])) & eligible_by_source.keys())
        covered = set()
        for source_id in matching_sources:
            covered.update(eligible_by_source[source_id])
        covered &= language_dimensions
        missing = language_dimensions - covered
        status = (
            "no_tier_zero_candidate"
            if not matching_sources
            else ("candidate_for_all_declared_dimensions" if not missing else "partial_candidate_coverage")
        )
        language_coverage.append(
            {
                "language_id": language["id"],
                "status": status,
                "eligible_source_candidates": matching_sources,
                "candidate_dimensions": sorted(covered),
                "unserved_dimensions": sorted(missing),
            }
        )

    excluded_sources = sorted(set(sources_by_id) - set(eligible_by_source))
    ready_units: list[str] = []
    for decision in execution_decisions or []:
        if decision.get("status") != "AUTHORIZED_TEST_EXECUTION":
            raise ValueError("execution decision is not authorized for testing")
        if decision.get("authority_effect") != "TEST_EXECUTION_ONLY":
            raise ValueError("execution decision exceeds test authority")
        for field in ("production_ready", "publication_allowed", "canon_admission"):
            if decision.get(field) is not False:
                raise ValueError(f"execution decision changed boundary: {field}")
        source_id = decision.get("source_id")
        unit_id = decision.get("unit_id")
        if source_id not in eligible_by_source:
            raise ValueError(f"execution source is outside tier zero: {source_id}")
        eligible_unit_ids = {unit.get("unit_id") for unit in units if unit.get("source_id") == source_id}
        if unit_id not in eligible_unit_ids:
            raise ValueError(f"execution unit is outside tier zero: {unit_id}")
        artifact = decision.get("artifact")
        if not isinstance(artifact, dict) or not re.fullmatch(r"[0-9a-f]{64}", str(artifact.get("sha256", ""))):
            raise ValueError("execution decision lacks a pinned SHA-256")
        ready_units.append(str(unit_id))
    excluded_source_details = [
        {
            "source_id": source_id,
            "license": sources_by_id[source_id].get("license"),
            "license_status": sources_by_id[source_id].get("license_status"),
            "source_admission_status": sources_by_id[source_id].get("admission_status"),
            "tier_zero_decision": "excluded",
        }
        for source_id in excluded_sources
    ]
    return {
        "schema": "generative-relational-lexicon-initial-mining-gap-report/1",
        "status": "generated-license-gap-analysis",
        "authority_effect": "NONE",
        "content_ingestion_authorized": False,
        "test_mining_authorized": bool(ready_units),
        "production_ingestion_authorized": False,
        "policy_id": policy["policy_id"],
        "source_count": len(sources),
        "eligible_source_count": len(eligible_by_source),
        "eligible_unit_count": len(units),
        "excluded_source_count": len(excluded_sources),
        "eligible_sources": sorted(eligible_by_source),
        "excluded_sources": excluded_sources,
        "excluded_source_details": excluded_source_details,
        "candidate_dimensions": sorted(covered_dimensions & active_dimensions),
        "global_evidence_holes": global_holes,
        "intentionally_deferred_dimensions": [deferred],
        "mining_ready_unit_count": len(ready_units),
        "test_execution_ready_units": sorted(ready_units),
        "readiness_blocker": "Readiness is test-only. Every other eligible unit still requires an exact version or dated export, SHA-256, enforced scope filter, and a separate execution decision; no unit is production-ready.",
        "language_coverage": language_coverage,
    }


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Initial mining gap report",
        "",
        "Status: generated license-gap analysis. One pinned Roget unit is authorized for internal test mining only; production ingestion and publication remain unauthorized.",
        "",
        "## Result",
        "",
        f"- Sources inventoried: {report['source_count']}",
        f"- Tier-zero eligible sources: {report['eligible_source_count']}",
        f"- Tier-zero eligible content units: {report['eligible_unit_count']}",
        f"- Sources excluded from initial mining: {report['excluded_source_count']}",
        f"- Mining-ready units: {report['mining_ready_unit_count']}",
        "",
        "Eligible source containers: " + ", ".join(f"`{item}`" for item in report["eligible_sources"]) + ".",
        "",
        "The eligible container does not imply that every file in it is eligible. Tatoeba and SuttaCentral are component-filtered.",
        "",
        "## Global holes exposed by the strict tier",
        "",
        ", ".join(f"`{item}`" for item in report["global_evidence_holes"]) + ".",
        "",
        "`GEIST` is deliberately deferred rather than counted as a mining hole.",
        "",
        "## Language and layer candidate coverage",
        "",
        "This table reports only whether an eligible source is typed for a dimension. It does not claim that the source contains a usable record for any particular word; empirical record coverage remains unknown until a separately authorized mining run.",
        "",
        "| Language or layer | Status | Eligible sources | Unserved dimensions |",
        "|---|---|---|---|",
    ]
    for item in report["language_coverage"]:
        sources = ", ".join(item["eligible_source_candidates"]) or "none"
        missing = ", ".join(item["unserved_dimensions"]) or "none declared by the capability map"
        lines.append(f"| {item['language_id']} | {item['status']} | {sources} | {missing} |")
    lines.extend(
        [
            "",
            "## Excluded-source ledger",
            "",
            "| Source | Recorded license | License status | Existing source-map status |",
            "|---|---|---|---|",
        ]
    )
    for item in report["excluded_source_details"]:
        license_text = str(item["license"]).replace("|", "\\|")
        lines.append(
            f"| {item['source_id']} | {license_text} | {item['license_status']} | {item['source_admission_status']} |"
        )
    lines.extend(
        [
            "",
            "## Readiness boundary",
            "",
            report["readiness_blocker"],
            "",
            "Exclusion at this tier is not a judgment that a source is unusable; it means the source is outside the deliberately narrow CC0/public-domain pilot.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    source_map = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    decisions = [json.loads(PILOT_DECISION_PATH.read_text(encoding="utf-8"))] if PILOT_DECISION_PATH.is_file() else []
    report = analyze(source_map, policy, decisions)
    with REPORT_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
    with REPORT_MD_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(render_markdown(report))
    print(json.dumps({key: report[key] for key in ("status", "source_count", "eligible_source_count", "eligible_unit_count", "excluded_source_count", "mining_ready_unit_count")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
