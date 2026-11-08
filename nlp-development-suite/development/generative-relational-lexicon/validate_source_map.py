from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MAP_PATH = ROOT / "SOURCE_LANGUAGE_MAP.json"
DIMENSIONS = {
    "ROOT",
    "ETYMOLOGY",
    "DERIVATION",
    "PHONOLOGY",
    "GRAMMAR",
    "MEANING",
    "TRANSLATION_EQUIVALENCE",
    "ABOUTNESS",
    "DOMAIN",
    "OPERATION",
    "QUALITY",
    "PERIOD",
    "REGISTER",
    "GEIST",
}
ABOUTNESS_TRUTH_STATES = {
    "SOURCE_SUBJECT_LABEL",
    "DERIVED_CONTEXT_CLUSTER",
    "GENERATED_CLASSIFICATION",
    "ACCEPTED_TOPIC_MAPPING",
}
ADMISSION_STATES = {
    "admitted_for_mapping",
    "isolated_adapter_only",
    "review_required",
    "blocked",
}
RELATION_KINDS = {
    "genealogical_hypothesis",
    "historical_continuation",
    "contact_or_borrowing",
}
NON_ADMISSIBLE_LICENSE_STATES = {
    "conflict",
    "official-license-version-conflict",
    "specific-license-required",
    "underlying-rights-unresolved",
}


def validate(data: dict[str, object]) -> dict[str, int | str]:
    errors: list[str] = []
    if data.get("schema") != "generative-relational-lexicon-source-map/1":
        errors.append("unexpected schema")
    if data.get("authority_effect") != "NONE":
        errors.append("authority effect must remain NONE")
    if data.get("content_ingestion_authorized") is not False:
        errors.append("content ingestion must remain unauthorized")
    if data.get("publication_authorized") is not False:
        errors.append("publication must remain unauthorized")
    if set(data.get("evidence_dimensions", [])) != DIMENSIONS:
        errors.append("evidence dimensions are incomplete")
    priority = data.get("dimension_priority", [])
    if not isinstance(priority, list) or set(priority) != DIMENSIONS or len(priority) != len(DIMENSIONS):
        errors.append("dimension priority must contain every dimension exactly once")
    elif priority[-1] != "GEIST":
        errors.append("geist must remain the lowest-priority dimension")
    if set(data.get("aboutness_truth_states", [])) != ABOUTNESS_TRUTH_STATES:
        errors.append("aboutness truth states are incomplete")
    aboutness = str(data.get("aboutness_definition", ""))
    if "sense or usage cluster" not in aboutness.casefold() or "not a definition" not in aboutness.casefold():
        errors.append("aboutness must remain sense-scoped and non-definitional")

    sources = data.get("sources")
    languages = data.get("languages")
    relations = data.get("relations")
    if not isinstance(sources, list) or not isinstance(languages, list) or not isinstance(relations, list):
        raise ValueError("sources, languages, and relations must be lists")

    source_ids = [item.get("id") for item in sources if isinstance(item, dict)]
    language_ids = [item.get("id") for item in languages if isinstance(item, dict)]
    if len(source_ids) != len(set(source_ids)):
        errors.append("source identifiers must be unique")
    if len(language_ids) != len(set(language_ids)):
        errors.append("language identifiers must be unique")
    source_id_set = set(source_ids)
    language_id_set = set(language_ids)

    for source in sources:
        if not isinstance(source, dict):
            errors.append("source must be an object")
            continue
        if source.get("admission_status") not in ADMISSION_STATES:
            errors.append(f"invalid admission state for {source.get('id')}")
        if (
            source.get("license_status") in NON_ADMISSIBLE_LICENSE_STATES
            and source.get("admission_status") == "admitted_for_mapping"
        ):
            errors.append(f"unresolved license state cannot be admitted: {source.get('id')}")
        dimensions = set(source.get("dimensions", []))
        if not dimensions or not dimensions <= DIMENSIONS:
            errors.append(f"invalid dimensions for {source.get('id')}")
        if source.get("admission_status") == "blocked" and not source.get("caution"):
            errors.append(f"blocked source lacks caution: {source.get('id')}")

    for language in languages:
        if not isinstance(language, dict):
            errors.append("language must be an object")
            continue
        unknown = set(language.get("source_candidates", [])) - source_id_set
        if unknown:
            errors.append(f"unknown sources for {language.get('id')}: {sorted(unknown)}")
        dimensions = set(language.get("dimensions", []))
        if not dimensions or not dimensions <= DIMENSIONS:
            errors.append(f"invalid dimensions for {language.get('id')}")

    for relation in relations:
        if not isinstance(relation, dict):
            errors.append("relation must be an object")
            continue
        if relation.get("from") not in language_id_set or relation.get("to") not in language_id_set:
            errors.append(f"relation has unknown endpoint: {relation}")
        if relation.get("kind") not in RELATION_KINDS:
            errors.append(f"invalid relation kind: {relation.get('kind')}")
        if relation.get("from") == relation.get("to"):
            errors.append(f"self relation is not allowed: {relation}")

    geist = str(data.get("geist_definition", ""))
    if "generated" not in geist.casefold() or "never a direct source fact" not in geist.casefold():
        errors.append("geist definition must preserve the generated-only boundary")

    if errors:
        raise ValueError("; ".join(errors))
    return {
        "status": "passed",
        "sources": len(sources),
        "languages": len(languages),
        "relations": len(relations),
    }


def main() -> int:
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    print(json.dumps(validate(data), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
