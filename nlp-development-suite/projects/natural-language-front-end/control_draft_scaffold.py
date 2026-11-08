"""Proposal-only scaffold for the Control Draft interpretation contract.

This module defines the source, candidate, review, and projection seams described
by Control_Draft_Parser_Reintegration_Spec_v0.1. It deliberately has no semantic
extraction rules and never writes a contract, calls a tool, or executes a command.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Mapping


SCHEMA_VERSION = "control-draft-interpretation/0.1"
PARSER_VERSION = "control-draft-scaffold/0.1"
MAX_SOURCE_CHARS = 64 * 1024
QUESTION_IDS = frozenset({
    "objective", "inputs", "scope", "authority", "procedure", "outputs",
    "acceptance", "escalation",
})
CANDIDATE_TYPES = frozenset({
    "primary_goal", "desired_state", "secondary_goal", "non_goal",
    "resource", "input", "source_precedence", "scope_include", "scope_exclude",
    "permission", "prohibition", "approval_gate", "obligation", "preference",
    "capability_claim", "procedure_step", "dependency", "checkpoint", "artifact",
    "format", "destination", "acceptance_criterion", "evidence_requirement",
    "human_acceptance_gate", "stop_condition", "escalation_condition", "blocker",
    "collision", "unresolved_reference", "unsupported_modality", "contract_conflict",
})
RULE_IDS = ("scaffold_no_semantic_rule", "scaffold_fenced_text_boundary")
RULE_SET_SHA256 = sha256(json.dumps(RULE_IDS, separators=(",", ":")).encode()).hexdigest()


def _source_hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _span(start: int, end: int) -> dict[str, Any]:
    return {"start": start, "end": end, "unit": "unicode_code_point"}


def _safe_source_ref(source_ref: str) -> str:
    if not isinstance(source_ref, str) or not source_ref or len(source_ref) > 500:
        raise ValueError("source_ref must be a nonempty bounded string")
    if any(ord(char) < 32 or ord(char) == 127 for char in source_ref):
        raise ValueError("source_ref contains control characters")
    return source_ref


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    source_ref: str
    source_span: dict[str, Any]
    source_text: str
    question_id: str
    candidate_type: str
    layer: str
    rule_id: str
    ranking_points: int
    evidence: tuple[str, ...]
    truth_state: str = "INFERENCE"
    review_status: str = "unreviewed"
    normalized: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        result = {
            "candidate_id": self.candidate_id,
            "source_ref": self.source_ref,
            "source_span": dict(self.source_span),
            "source_text": self.source_text,
            "question_id": self.question_id,
            "candidate_type": self.candidate_type,
            "layer": self.layer,
            "rule_id": self.rule_id,
            "ranking_points": self.ranking_points,
            "evidence": list(self.evidence),
            "truth_state": self.truth_state,
            "review_status": self.review_status,
        }
        if self.normalized is not None:
            result["normalized"] = dict(self.normalized)
        return result


@dataclass(frozen=True)
class InterpretationResult:
    source_ref: str
    question_id: str
    text: str
    status: str
    layer_trace: tuple[dict[str, str], ...]
    candidates: tuple[Candidate, ...]
    unresolved: tuple[dict[str, Any], ...]
    parser_version: str = PARSER_VERSION
    rule_set_sha256: str = RULE_SET_SHA256
    execution_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "parser_version": self.parser_version,
            "rule_set_sha256": self.rule_set_sha256,
            "source": {
                "source_ref": self.source_ref,
                "question_id": self.question_id,
                "text": self.text,
                "text_sha256": _source_hash(self.text),
            },
            "status": self.status,
            "layer_trace": [dict(item) for item in self.layer_trace],
            "candidates": [candidate.as_dict() for candidate in self.candidates],
            "unresolved": [dict(item) for item in self.unresolved],
            "execution_allowed": self.execution_allowed,
        }


def make_candidate(*, source_ref: str, source_span: Mapping[str, Any], source_text: str,
                   question_id: str, candidate_id: str, candidate_type: str,
                   rule_id: str, ranking_points: int = 50,
                   evidence: tuple[str, ...] = ("scaffold_candidate",),
                   layer: str = "explicit_contract_rules",
                   truth_state: str = "INFERENCE",
                   normalized: dict[str, Any] | None = None) -> Candidate:
    """Construct a schema-shaped candidate for a future reviewed rule."""
    _safe_source_ref(source_ref)
    if question_id not in QUESTION_IDS:
        raise ValueError(f"Unsupported question_id: {question_id}")
    if candidate_type not in CANDIDATE_TYPES:
        raise ValueError(f"Unsupported candidate_type: {candidate_type}")
    if not re.fullmatch(r"[A-Z][A-Z0-9_-]+$", candidate_id):
        raise ValueError("candidate_id must use the exported identifier pattern")
    if type(ranking_points) is not int or not 0 <= ranking_points <= 100:
        raise ValueError("ranking_points must be an integer from 0 through 100")
    if truth_state not in {"DERIVED", "INFERENCE"}:
        raise ValueError("truth_state must be DERIVED or INFERENCE")
    if not evidence or not all(isinstance(item, str) and item for item in evidence):
        raise ValueError("evidence must contain at least one nonempty string")
    start, end = source_span.get("start"), source_span.get("end")
    if source_span.get("unit") != "unicode_code_point" or type(start) is not int or type(end) is not int:
        raise ValueError("source_span must use Unicode code-point integer offsets")
    if not 0 <= start < end <= len(source_text):
        raise ValueError("source_span is outside source_text")
    return Candidate(candidate_id, source_ref, dict(source_span), source_text[start:end],
                     question_id, candidate_type, layer, rule_id, ranking_points,
                     tuple(evidence), truth_state, "unreviewed", normalized)


def parse_answer(text: str, *, question_id: str, source_ref: str = "conversation-local") -> InterpretationResult:
    """Return a safe scaffold result; semantic rules are intentionally pending."""
    _safe_source_ref(source_ref)
    if question_id not in QUESTION_IDS:
        raise ValueError(f"Unsupported question_id: {question_id}")
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if not text or len(text) > MAX_SOURCE_CHARS:
        reason = "Input is empty." if not text else f"Input exceeds the {MAX_SOURCE_CHARS}-character bound."
        return InterpretationResult(
            source_ref, question_id, text, "invalid_input",
            ({"layer": "explicit_contract_rules", "status": "invalid_or_failed"},), (),
            ({"source_span": _span(0, len(text)) if text else _span(0, 0), "reason": reason},),
        )
    if "```" in text:
        reason = "Fenced text is preserved as source but is not interpreted as an operative answer."
        return InterpretationResult(
            source_ref, question_id, text, "unparsed",
            ({"layer": "explicit_contract_rules", "status": "no_match"},
             {"layer": "reviewed_lexical_aliases", "status": "not_consulted"}), (),
            ({"source_span": _span(0, len(text)), "reason": reason},),
        )
    reason = "No Control Draft semantic extraction rule is implemented in this scaffold yet."
    return InterpretationResult(
        source_ref, question_id, text, "unparsed",
        ({"layer": "explicit_contract_rules", "status": "no_match"},
         {"layer": "reviewed_lexical_aliases", "status": "no_match"},
         {"layer": "pinned_wordnet_candidates", "status": "not_consulted"},
         {"layer": "session_confirmed_ranking", "status": "not_consulted"},
         {"layer": "optional_web_provider", "status": "not_configured"},
         {"layer": "optional_model_provider", "status": "not_configured"}), (),
        ({"source_span": _span(0, len(text)), "reason": reason},),
    )


def review_candidate(result: InterpretationResult, candidate_id: str,
                     decision: str) -> InterpretationResult:
    """Record an explicit review decision without projecting or executing it."""
    if decision not in {"user_accepted", "user_rejected"}:
        raise ValueError("decision must be user_accepted or user_rejected")
    if not any(candidate.candidate_id == candidate_id for candidate in result.candidates):
        raise ValueError(f"Unknown candidate_id: {candidate_id}")
    candidates = tuple(
        replace(candidate, review_status=decision) if candidate.candidate_id == candidate_id else candidate
        for candidate in result.candidates
    )
    return replace(result, candidates=candidates, execution_allowed=False)


class DraftProjectionAdapter:
    """Build an in-memory draft projection from explicitly accepted candidates."""

    def project(self, result: InterpretationResult,
                accepted_targets: Mapping[str, str]) -> dict[str, Any]:
        if result.status in {"collision", "conflict", "unparsed", "invalid_input"}:
            raise ValueError("Only a reviewed, non-ambiguous result may be projected")
        by_id = {candidate.candidate_id: candidate for candidate in result.candidates}
        if set(accepted_targets) - set(by_id):
            raise ValueError("Projection names a candidate absent from the result")
        transformations = []
        fields = {}
        for candidate_id, target_path in accepted_targets.items():
            candidate = by_id[candidate_id]
            if candidate.review_status != "user_accepted":
                raise ValueError("Projection requires an explicit user_accepted candidate")
            if not isinstance(target_path, str) or not target_path or "\x00" in target_path:
                raise ValueError("target_path must be a bounded nonempty string")
            fields[target_path] = candidate.normalized or {"source_text": candidate.source_text}
            transformations.append({
                "candidate_id": candidate_id,
                "source_ref": candidate.source_ref,
                "source_span": dict(candidate.source_span),
                "target_path": target_path,
                "semantic_change": "candidate_to_draft_projection",
                "reviewer_decision": candidate.review_status,
            })
        return {
            "execution_allowed": False,
            "draft_fields": fields,
            "transformations": transformations,
            "requires_policy_validation": True,
            "requires_sister_machine_acceptance": True,
        }
