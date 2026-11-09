from __future__ import annotations

import hashlib
import gzip
import io
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DECISION_PATH = ROOT / "TIER_ZERO_PILOT_DECISION.json"
OUTPUT_DIR = ROOT / "pilot" / "tier-zero" / "output"
RECORDS_PATH = OUTPUT_DIR / "roget-structural-evidence.jsonl"
MEMBERSHIPS_PATH = OUTPUT_DIR / "roget-historical-memberships.jsonl.gz"
MODERN_QUERY_PATH = OUTPUT_DIR / "modern-word-historical-candidates.json"
RECEIPT_PATH = OUTPUT_DIR / "PILOT_RECEIPT.json"
PARSER_VERSION = "roget-structure-pilot/4"
MODERN_WORD_TEST_SET = [
    "computer",
    "data",
    "identity",
    "language",
    "machine",
    "mapping",
    "network",
    "precision",
    "relation",
    "sociology",
]

HEAD_RE = re.compile(r"^#(?P<head_id>(?P<number>\d+)(?P<suffix>[a-z])?)\.\s*(?P<lead>.*)$", re.IGNORECASE)
CLASS_RE = re.compile(r"^CLASS\s+(?P<number>[IVXLCDM]+)(?:\.|\s|$)")
SECTION_RE = re.compile(r"^SECTION\s+(?P<number>[IVXLCDM]+)\.\s*(?P<label>.*)$")
POS_RE = re.compile(r"(?<![A-Za-z])(?P<pos>N|V|Adj|Adv|Phr)\.")
CROSS_REF_RE = re.compile(r"&c\.(?:\s*\([^)]*\))?\s*(?P<number>\d{1,4})")
BRACKETED_RE = re.compile(r"\[[^\]]*\]")
BRACED_RE = re.compile(r"\{[^}]*\}")
PAREN_REF_RE = re.compile(r"\([^)]*\)\s*\d{1,4}")
ETC_REF_RE = re.compile(r"\s*&c\.?(?:\s*\([^)]*\))?(?:\s*\d{1,4})?")
TRAILING_POS_RE = re.compile(r"\s+(?:adj|adv|n|v|phr)\.?$", re.IGNORECASE)
TRAILING_HEAD_REF_RE = re.compile(r"\s+(?P<head_id>(?:[1-9]\d{2}|1000)[a-b]?)$", re.IGNORECASE)
SEE_DIRECTIVE_RE = re.compile(r"(?:[—-]\s*)?(?:for\s+the\s+latter\s+)?see\b.*$", re.IGNORECASE)
NUMBERED_HEADING_RE = re.compile(r"^\(?(?:\d+|[ivxlcdm]+)\)\s+.+$", re.IGNORECASE)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_decision(decision: dict[str, object]) -> Path:
    if decision.get("status") != "AUTHORIZED_TEST_EXECUTION":
        raise ValueError("pilot execution is not authorized")
    if decision.get("authority_effect") != "TEST_EXECUTION_ONLY":
        raise ValueError("pilot authority must remain test-only")
    for field in ("production_ready", "publication_allowed", "canon_admission", "network_refresh_allowed"):
        if decision.get(field) is not False:
            raise ValueError(f"pilot boundary changed: {field}")
    if decision.get("source_id") != "project-gutenberg-roget-22":
        raise ValueError("pilot source is not allowlisted")
    artifact = decision.get("artifact")
    if not isinstance(artifact, dict):
        raise ValueError("pilot artifact record is missing")
    relative_path = artifact.get("relative_path")
    if not isinstance(relative_path, str):
        raise ValueError("pilot artifact path is missing")
    path = (ROOT / relative_path).resolve()
    pilot_root = (ROOT / "pilot" / "tier-zero").resolve()
    if pilot_root not in path.parents:
        raise ValueError("pilot artifact escaped its controlled directory")
    return path


def verify_artifact(path: Path, decision: dict[str, object]) -> tuple[bytes, str]:
    data = path.read_bytes()
    artifact = decision["artifact"]
    digest = sha256_bytes(data)
    if len(data) != artifact.get("bytes"):
        raise ValueError("artifact byte count differs from the accepted decision")
    if digest != artifact.get("sha256"):
        raise ValueError("artifact SHA-256 differs from the accepted decision")
    return data, digest


def heading_from_lead(lead: str) -> str:
    marker = POS_RE.search(lead)
    heading = lead[: marker.start()] if marker else lead
    return " ".join(heading.split()).strip(" .,:;—–-")


def split_term_candidates(section: str) -> list[str]:
    candidates: list[str] = []
    buffer: list[str] = []
    square_depth = 0
    brace_depth = 0
    for character in section:
        if character == "[":
            square_depth += 1
        elif character == "]" and square_depth:
            square_depth -= 1
        elif character == "{":
            brace_depth += 1
        elif character == "}" and brace_depth:
            brace_depth -= 1
        if character in ";,.\n" and square_depth == 0 and brace_depth == 0:
            candidates.append("".join(buffer))
            buffer = []
        else:
            buffer.append(character)
    candidates.append("".join(buffer))
    return candidates


def is_structural_heading(value: str) -> bool:
    candidate = " ".join(value.strip().strip("_").split())
    if not candidate:
        return False
    if NUMBERED_HEADING_RE.fullmatch(candidate):
        return True
    letters = [character for character in candidate if character.isalpha()]
    return len(candidate.split()) > 1 and bool(letters) and candidate.upper() == candidate


def clean_term_candidate_with_evidence(value: str) -> tuple[str | None, list[str]]:
    if is_structural_heading(value):
        return None, []
    value = BRACKETED_RE.sub(" ", value)
    value = BRACED_RE.sub(" ", value)
    value = PAREN_REF_RE.sub(" ", value)
    value = CROSS_REF_RE.sub(" ", value)
    value = ETC_REF_RE.sub(" ", value)
    value = value.replace("_", " ")
    value = " ".join(value.split()).strip(" .:—–-(){}[]'\"")
    value = TRAILING_POS_RE.sub("", value).strip()
    head_references: list[str] = []
    trailing_reference = TRAILING_HEAD_REF_RE.search(value)
    if trailing_reference:
        head_references.append(trailing_reference.group("head_id").casefold())
        value = value[: trailing_reference.start()].rstrip()
        value = SEE_DIRECTIVE_RE.sub("", value).strip(" .:—–-(){}[]'\"")
    if not value or len(value) > 80 or len(value.split()) > 6:
        return None, head_references
    if not any(character.isalpha() for character in value):
        return None, head_references
    if any(character in value for character in ("?", "!", '"')):
        return None, head_references
    return value, head_references


def clean_term_candidate(value: str) -> str | None:
    return clean_term_candidate_with_evidence(value)[0]


def extract_memberships(block: str, head_record: dict[str, object]) -> list[dict[str, object]]:
    markers = list(POS_RE.finditer(block))
    memberships: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for index, marker in enumerate(markers):
        part_of_speech = marker.group("pos")
        stop = markers[index + 1].start() if index + 1 < len(markers) else len(block)
        section = block[marker.end():stop]
        section = ETC_REF_RE.sub(" ", section)
        for raw_candidate in split_term_candidates(section):
            source_bracket_labels = sorted(
                set(BRACKETED_RE.findall(raw_candidate)),
                key=lambda value: (value.casefold(), value),
            )
            candidate, candidate_head_references = clean_term_candidate_with_evidence(raw_candidate)
            if candidate is None:
                continue
            normalized = candidate.casefold()
            key = (part_of_speech, normalized)
            if key in seen:
                continue
            seen.add(key)
            memberships.append(
                {
                    "schema": "roget-historical-membership/1",
                    "truth_state": "SOURCE_STRUCTURE",
                    "acceptance_state": "MODERN_SENSE_CANDIDATE_ONLY",
                    "source_id": head_record["source_id"],
                    "source_sha256": head_record["source_sha256"],
                    "historical_scope": "mixed_1911_derived_electronic_edition_with_later_additions",
                    "term": candidate,
                    "normalized_term": normalized,
                    "part_of_speech_marker": part_of_speech,
                    "source_bracket_labels": source_bracket_labels,
                    "head_number": head_record["head_number"],
                    "head_id": head_record["head_id"],
                    "candidate_head_references": candidate_head_references,
                    "heading": head_record["heading"],
                    "class_number": head_record["class_number"],
                    "section_number": head_record["section_number"],
                    "source_line_start": head_record["source_line_start"],
                    "source_line_end": head_record["source_line_end"],
                }
            )
    return memberships


def parse_roget(text: str, source_sha256: str) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    required_markers = [
        "*** START OF THE PROJECT GUTENBERG EBOOK ROGET'S THESAURUS ***",
        "An electronic thesaurus derived from the version of Roget's Thesaurus",
        "supplemented with",
        "*** END OF THE PROJECT GUTENBERG EBOOK ROGET'S THESAURUS ***",
    ]
    for marker in required_markers:
        if marker not in text:
            raise ValueError(f"required source marker missing: {marker}")

    lines = text.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith("*** START OF"))
    end = next(index for index, line in enumerate(lines) if line.startswith("*** END OF"))
    if start >= end:
        raise ValueError("invalid source boundaries")

    heads: list[tuple[int, re.Match[str], str | None, str | None]] = []
    current_class: str | None = None
    current_section: str | None = None
    for index in range(start + 1, end):
        stripped = lines[index].strip()
        class_match = CLASS_RE.match(stripped)
        if class_match:
            current_class = class_match.group("number")
            current_section = None
        section_match = SECTION_RE.match(stripped)
        if section_match:
            current_section = section_match.group("number")
        head_match = HEAD_RE.match(stripped)
        if head_match:
            heads.append((index, head_match, current_class, current_section))

    records: list[dict[str, object]] = []
    memberships: list[dict[str, object]] = []
    for position, (line_index, match, class_number, section_number) in enumerate(heads):
        next_index = heads[position + 1][0] if position + 1 < len(heads) else end
        block = "\n".join(lines[line_index:next_index])
        part_of_speech = sorted({item.group("pos") for item in POS_RE.finditer(block)})
        cross_references = sorted({int(item.group("number")) for item in CROSS_REF_RE.finditer(block)})
        record = {
                "schema": "roget-structural-evidence/1",
                "truth_state": "SOURCE_STRUCTURE",
                "acceptance_state": "PROPOSAL_ONLY",
                "source_id": "project-gutenberg-roget-22",
                "source_sha256": source_sha256,
                "head_number": int(match.group("number")),
                "head_id": match.group("head_id").casefold(),
                "heading": heading_from_lead(match.group("lead")),
                "class_number": class_number,
                "section_number": section_number,
                "part_of_speech_markers": part_of_speech,
                "cross_reference_heads": cross_references,
                "source_line_start": line_index + 1,
                "source_line_end": next_index,
            }
        records.append(record)
        memberships.extend(extract_memberships(block, record))
    if len(records) < 1000:
        raise ValueError(f"implausibly few Roget heads: {len(records)}")
    head_ids = [record["head_id"] for record in records]
    if len(head_ids) != len(set(head_ids)):
        raise ValueError("duplicate Roget head identifiers")
    if len(memberships) < 10000:
        raise ValueError(f"implausibly few historical memberships: {len(memberships)}")
    return records, memberships


def build_modern_queries(memberships: list[dict[str, object]]) -> dict[str, object]:
    index: dict[str, list[dict[str, object]]] = {}
    for membership in memberships:
        index.setdefault(str(membership["normalized_term"]), []).append(membership)
    queries = []
    for word in MODERN_WORD_TEST_SET:
        matches = index.get(word.casefold(), [])
        queries.append(
            {
                "modern_word": word,
                "status": "HISTORICAL_CANDIDATES_FOUND" if matches else "NO_EXACT_HISTORICAL_CANDIDATE",
                "candidate_count": len(matches),
                "candidates": [
                    {
                        "head_number": match["head_number"],
                        "head_id": match["head_id"],
                        "heading": match["heading"],
                        "part_of_speech_marker": match["part_of_speech_marker"],
                        "source_line_start": match["source_line_start"],
                        "source_line_end": match["source_line_end"],
                    }
                    for match in matches
                ],
            }
        )
    return {
        "schema": "modern-word-historical-candidates/1",
        "status": "GENERATED_TEST_RESULT",
        "acceptance_state": "PROPOSAL_ONLY",
        "historical_scope": "mixed_1911_derived_electronic_edition_with_later_additions",
        "queries": queries,
        "interpretation_boundary": "An exact historical term placement can propose modern sense questions. It is not a modern definition, proof of continuity, or proof that the placement originated in 1911.",
    }


def write_outputs(records: list[dict[str, object]], memberships: list[dict[str, object]], source_data: bytes, source_sha256: str) -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    records_text = "".join(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n" for record in records)
    with RECORDS_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(records_text)
    memberships_text = "".join(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n" for record in memberships)
    membership_bytes = memberships_text.encode("utf-8")
    compressed_buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=compressed_buffer, mtime=0) as stream:
        stream.write(membership_bytes)
    compressed_memberships = compressed_buffer.getvalue()
    MEMBERSHIPS_PATH.write_bytes(compressed_memberships)
    modern_queries = build_modern_queries(memberships)
    modern_query_text = json.dumps(modern_queries, indent=2, ensure_ascii=False) + "\n"
    with MODERN_QUERY_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(modern_query_text)
    receipt = {
        "schema": "generative-relational-lexicon-tier-zero-pilot-receipt/1",
        "status": "PASSED",
        "authority_effect": "TEST_EXECUTION_ONLY",
        "production_ready": False,
        "publication_allowed": False,
        "canon_admission": False,
        "parser_version": PARSER_VERSION,
        "source": {
            "id": "project-gutenberg-roget-22",
            "relative_path": str(Path("..") / "raw" / "project-gutenberg-ebook-22.txt"),
            "bytes": len(source_data),
            "sha256": source_sha256,
        },
        "output": {
            "head_records": {
                "relative_path": RECORDS_PATH.name,
                "record_count": len(records),
                "bytes": len(records_text.encode("utf-8")),
                "sha256": sha256_bytes(records_text.encode("utf-8")),
                "first_head": min(record["head_number"] for record in records),
                "last_head": max(record["head_number"] for record in records),
            },
            "historical_memberships": {
                "relative_path": MEMBERSHIPS_PATH.name,
                "record_count": len(memberships),
                "uncompressed_bytes": len(membership_bytes),
                "bytes": len(compressed_memberships),
                "sha256": sha256_bytes(compressed_memberships),
            },
            "modern_word_queries": {
                "relative_path": MODERN_QUERY_PATH.name,
                "query_count": len(modern_queries["queries"]),
                "queries_with_candidates": sum(1 for query in modern_queries["queries"] if query["candidate_count"]),
                "bytes": len(modern_query_text.encode("utf-8")),
                "sha256": sha256_bytes(modern_query_text.encode("utf-8")),
            },
        },
        "claim_boundary": "Structural evidence from the pinned electronic edition; no definition, timeless semantic fact, production readiness, publication approval, or canon admission is asserted.",
    }
    with RECEIPT_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main() -> int:
    decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
    artifact_path = validate_decision(decision)
    data, digest = verify_artifact(artifact_path, decision)
    records, memberships = parse_roget(data.decode("utf-8-sig"), digest)
    receipt = write_outputs(records, memberships, data, digest)
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
