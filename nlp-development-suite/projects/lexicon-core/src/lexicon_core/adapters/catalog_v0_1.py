"""Catalog capability adapter for handoff contract v0.1.

The adapter produces interpretation candidates only. It does not dispatch a
catalog operation, mutate catalog state, or authorize filesystem work.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from hashlib import sha256
import json
import re
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from ..tasks.base import TaskRequest
from ..tasks.router import RouteResult


CONTRACT_ID = "catalog.modular-nlp-capability-handoff/0.1"
MODULE_ID = "lexicon-core.catalog-adapter"
MODULE_VERSION = "0.1.0"
CAPABILITY_IDS = tuple(f"NLP-CAP-{number:02d}" for number in range(1, 11))
STATUSES = frozenset({"parsed_single", "collision", "unparsed", "conflict", "invalid_input"})
ORIGIN_CLASSES = frozenset(
    {"DETERMINISTIC_RULE", "STATISTICAL_MODEL", "LLM_INFERENCE", "EXTERNAL_LOOKUP", "ADAPTER_NORMALIZATION"}
)


_RULE_DEFINITIONS = (
    ("rule:catalog-find-partial-v0.1", r"^\s*find\s+(?P<term>[^;,]+?)\s*(?:;|,)\s*(?P<unresolved>.+?)\s*$"),
    ("rule:catalog-find-v0.1", r"^\s*find\s+(?P<term>.+?)\s*$"),
    ("rule:catalog-inbox-v0.1", r"^\s*show\s+(?P<inbox>inbox)\s*$"),
    ("rule:catalog-show-object-v0.1", r"^\s*show\s+object\s+(?P<object>\S+)\s*$"),
    ("rule:catalog-list-v0.1", r"^\s*(?:list|show)\s+(?P<scope>catalog|objects|items)\s*$"),
    ("rule:catalog-project-inspect-v0.1", r"^\s*(?:inspect|show)\s+project\s+(?P<project>.+?)\s*$"),
    ("rule:catalog-move-ambiguous-v0.1", r"^\s*move\s+(?P<item>.+?)\s+into\s+(?P<target>.+?)\s*$"),
    (
        "rule:catalog-collect-no-physical-move-v0.1",
        r"^\s*put\s+(?P<item>.+?)\s+with\s+(?P<target>.+?)\s*,?\s*(?P<constraint>(?:(?:do\s+not|don't)\s+move|without\s+moving)\s+(?:the\s+)?actual\s+files)\s*$",
    ),
)
_RULESET_DESCRIPTOR = {
    "rules": _RULE_DEFINITIONS,
    "operation_mappings": (
        ("find", "catalog.find", ("term",)),
        ("inbox", "catalog.inbox", ()),
        ("show-object", "catalog.show", ("object_id",)),
        ("list", "catalog.ls", ("scope",)),
        ("project-inspect", "catalog.project.inspect", ("project",)),
        ("move-semantic", "catalog.collect", ("item", "collection")),
        ("move-physical", "catalog.file.move", ("item", "destination")),
        ("collect-no-physical-move", "catalog.collect", ("item", "collection", "physical_move")),
        ("task:file-explorer:search", "catalog.find", ("term",)),
        ("task:file-explorer:list", "catalog.ls", ("scope",)),
    ),
    "precedence": ("conflict", "explicit-constraint", "ambiguous-move", "simple-read", "abstain"),
}
RULESET_DIGEST = sha256(
    json.dumps(_RULESET_DESCRIPTOR, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
).hexdigest()


def _digest_json(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ArgumentContract:
    """Small deterministic argument contract supplied by the operation registry."""

    required: Mapping[str, str] = field(default_factory=dict)
    optional: Mapping[str, str] = field(default_factory=dict)
    allow_extra: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "required", MappingProxyType(dict(self.required)))
        object.__setattr__(self, "optional", MappingProxyType(dict(self.optional)))

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ArgumentContract":
        return cls(
            required={str(key): str(kind) for key, kind in value.get("required", {}).items()},
            optional={str(key): str(kind) for key, kind in value.get("optional", {}).items()},
            allow_extra=bool(value.get("allow_extra", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "required": dict(sorted(self.required.items())),
            "optional": dict(sorted(self.optional.items())),
            "allow_extra": self.allow_extra,
        }

    def validate(self, arguments: Mapping[str, Any]) -> tuple[str, ...]:
        errors: list[str] = []
        known = set(self.required) | set(self.optional)
        for name in self.required:
            if name not in arguments:
                errors.append(f"missing:{name}")
        if not self.allow_extra:
            errors.extend(f"unexpected:{name}" for name in sorted(set(arguments) - known))
        for name, value in arguments.items():
            expected = self.required.get(name, self.optional.get(name))
            if expected is None:
                continue
            if not _matches_type(value, expected):
                errors.append(f"type:{name}:{expected}")
        return tuple(errors)


def _matches_type(value: Any, expected: str) -> bool:
    checks = {
        "string": lambda item: isinstance(item, str),
        "boolean": lambda item: isinstance(item, bool),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "array": lambda item: isinstance(item, (list, tuple)),
        "object": lambda item: isinstance(item, Mapping),
        "null": lambda item: item is None,
    }
    check = checks.get(expected)
    return bool(check and check(value))


@dataclass(frozen=True)
class CatalogOperationRegistry:
    """The caller-supplied list of operations the catalog currently accepts."""

    version: str
    operations: frozenset[str]
    argument_contracts: Mapping[str, ArgumentContract] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "operations", frozenset(self.operations))
        object.__setattr__(self, "argument_contracts", MappingProxyType(dict(self.argument_contracts)))

    @classmethod
    def from_mapping(
        cls,
        value: Mapping[str, Any],
        *,
        version: str | None = None,
    ) -> "CatalogOperationRegistry":
        groups = value.get("current_operations", value)
        operations: set[str] = set()
        if isinstance(groups, Mapping):
            for entries in groups.values():
                if isinstance(entries, str):
                    operations.add(entries)
                elif isinstance(entries, Iterable):
                    operations.update(str(entry) for entry in entries)
        raw_contracts = value.get("operation_contracts", {})
        contracts = {
            str(operation): ArgumentContract.from_mapping(contract)
            for operation, contract in raw_contracts.items()
            if isinstance(contract, Mapping)
        }
        if not operations and contracts:
            operations.update(contracts)
        return cls(
            version=version or str(value.get("handoff_id", "unversioned")),
            operations=frozenset(operations),
            argument_contracts=contracts,
        )

    @property
    def configuration_digest(self) -> str:
        return _digest_json(
            {
                "version": self.version,
                "operations": sorted(self.operations),
                "argument_contracts": {
                    operation: contract.to_dict()
                    for operation, contract in sorted(self.argument_contracts.items())
                },
            }
        )

    def validate_arguments(self, operation: str, arguments: Mapping[str, Any]) -> tuple[str, ...]:
        contract = self.argument_contracts.get(operation)
        return contract.validate(arguments) if contract else ()


@dataclass(frozen=True)
class SourceRecord:
    exact_text: str
    sha256: str
    char_length: int

    @classmethod
    def from_text(cls, text: str) -> "SourceRecord":
        return cls(text, sha256(text.encode("utf-8")).hexdigest(), len(text))


@dataclass(frozen=True)
class SourceSpan:
    start: int
    end: int
    text: str


@dataclass(frozen=True)
class Confidence:
    value: float
    semantics: str


@dataclass(frozen=True)
class Candidate:
    operation: str
    arguments: Mapping[str, Any]
    source_spans: tuple[SourceSpan, ...]
    origin_class: str
    origin_ref: str
    confidence: Confidence
    evidence: tuple[Mapping[str, Any], ...] = ()
    constraints: tuple[Mapping[str, Any], ...] = ()
    admitted: bool = False
    execution_allowed: bool = False
    authority_effect: str = "NONE"


@dataclass(frozen=True)
class LayerTrace:
    layer_id: str
    layer_version: str
    status: str
    candidate_contribution: int
    rule_or_model_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class UnresolvedRegion:
    start: int
    end: int
    text: str
    reason: str


@dataclass(frozen=True)
class ModuleIdentity:
    module_id: str
    module_version: str
    capabilities: tuple[str, ...]
    ruleset_digest: str
    configuration_digest: str


@dataclass(frozen=True)
class InterpretationResult:
    status: str
    source: SourceRecord
    module: ModuleIdentity
    registry_version: str
    registry_digest: str
    candidates: tuple[Candidate, ...]
    layer_trace: tuple[LayerTrace, ...]
    unresolved: tuple[UnresolvedRegion, ...]
    contract_id: str = CONTRACT_ID
    authority_effect: str = "NONE"
    execution_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "status": self.status,
            "source": {
                "exact_text": self.source.exact_text,
                "sha256": self.source.sha256,
                "char_length": self.source.char_length,
            },
            "module": {
                "module_id": self.module.module_id,
                "module_version": self.module.module_version,
                "capabilities": list(self.module.capabilities),
                "ruleset_digest": self.module.ruleset_digest,
                "configuration_digest": self.module.configuration_digest,
            },
            "registry": {"version": self.registry_version, "digest": self.registry_digest},
            "candidates": [
                {
                    "operation": candidate.operation,
                    "arguments": dict(candidate.arguments),
                    "source_spans": [
                        {"start": span.start, "end": span.end, "text": span.text}
                        for span in candidate.source_spans
                    ],
                    "origin_class": candidate.origin_class,
                    "origin_ref": candidate.origin_ref,
                    "confidence": {
                        "value": candidate.confidence.value,
                        "semantics": candidate.confidence.semantics,
                    },
                    "evidence": [dict(item) for item in candidate.evidence],
                    "constraints": [dict(item) for item in candidate.constraints],
                    "admitted": candidate.admitted,
                    "execution_allowed": candidate.execution_allowed,
                    "authority_effect": candidate.authority_effect,
                }
                for candidate in self.candidates
            ],
            "layer_trace": [
                {
                    "layer_id": layer.layer_id,
                    "layer_version": layer.layer_version,
                    "status": layer.status,
                    "candidate_contribution": layer.candidate_contribution,
                    "rule_or_model_ids": list(layer.rule_or_model_ids),
                }
                for layer in self.layer_trace
            ],
            "unresolved": [
                {"start": item.start, "end": item.end, "text": item.text, "reason": item.reason}
                for item in self.unresolved
            ],
            "authority_effect": self.authority_effect,
            "execution_allowed": self.execution_allowed,
        }


class CatalogAdapter:
    """Deterministic v0.1 adapter constrained by an injected operation registry."""

    def __init__(self, registry: CatalogOperationRegistry):
        self.registry = registry

    def interpret(self, text: str) -> InterpretationResult:
        if not isinstance(text, str):
            raise TypeError("CatalogAdapter.interpret requires a string")

        source = SourceRecord.from_text(text)
        candidates: list[Candidate] = []
        unresolved: list[UnresolvedRegion] = []
        matched_rules: list[str] = []

        def span(match: re.Match[str], group: str) -> SourceSpan:
            start, end = match.span(group)
            return SourceSpan(start, end, text[start:end])

        def propose(
            operation: str,
            arguments: Mapping[str, Any],
            spans: tuple[SourceSpan, ...],
            rule_id: str,
            *,
            constraints: tuple[Mapping[str, Any], ...] = (),
        ) -> None:
            if operation not in self.registry.operations:
                first = spans[0] if spans else SourceSpan(0, len(text), text)
                unresolved.append(
                    UnresolvedRegion(first.start, first.end, first.text, f"operation_not_in_registry:{operation}")
                )
                return
            argument_errors = self.registry.validate_arguments(operation, arguments)
            if argument_errors:
                first = spans[0] if spans else SourceSpan(0, len(text), text)
                unresolved.append(
                    UnresolvedRegion(
                        first.start,
                        first.end,
                        first.text,
                        f"invalid_arguments:{operation}:{'|'.join(argument_errors)}",
                    )
                )
                return
            candidates.append(
                Candidate(
                    operation=operation,
                    arguments=arguments,
                    source_spans=spans,
                    origin_class="DETERMINISTIC_RULE",
                    origin_ref=rule_id,
                    confidence=Confidence(1.0, "deterministic_match"),
                    evidence=({"kind": "rule_match", "rule_id": rule_id},),
                    constraints=constraints,
                )
            )

        if not text.strip():
            unresolved.append(UnresolvedRegion(0, len(text), text, "empty_input"))
            return self._result("invalid_input", source, (), (), tuple(unresolved))

        no_move = re.search(
            r"\b(?:(?:do\s+not|don't)\s+move|without\s+moving)\s+(?:the\s+)?actual\s+files\b",
            text,
            re.IGNORECASE,
        )
        yes_move = re.search(r"\b(?:and|but)\s+(?:also\s+)?move\s+(?:the\s+)?actual\s+files\b", text, re.IGNORECASE)
        if no_move and yes_move:
            unresolved.extend(
                (
                    UnresolvedRegion(no_move.start(), no_move.end(), text[no_move.start():no_move.end()], "negative_physical_move_constraint"),
                    UnresolvedRegion(yes_move.start(), yes_move.end(), text[yes_move.start():yes_move.end()], "positive_physical_move_constraint"),
                )
            )
            return self._result("conflict", source, (), ("rule:catalog-constraint-conflict-v0.1",), tuple(unresolved))

        rule_id, pattern = _RULE_DEFINITIONS[0]
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            matched_rules.append(rule_id)
            term_span = span(match, "term")
            unresolved_span = span(match, "unresolved")
            propose("catalog.find", {"term": term_span.text}, (term_span,), rule_id)
            unresolved.append(
                UnresolvedRegion(
                    unresolved_span.start,
                    unresolved_span.end,
                    unresolved_span.text,
                    "unsupported_trailing_clause",
                )
            )
            status = "parsed_single" if candidates else "unparsed"
            return self._result(status, source, tuple(candidates), tuple(matched_rules), tuple(unresolved))

        rule_id, pattern = _RULE_DEFINITIONS[7]
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            matched_rules.append(rule_id)
            item_span = span(match, "item")
            target_span = span(match, "target")
            constraint_span = span(match, "constraint")
            propose(
                "catalog.collect",
                {"item": item_span.text, "collection": target_span.text, "physical_move": False},
                (item_span, target_span, constraint_span),
                rule_id,
                constraints=(
                    {
                        "name": "physical_move",
                        "value": False,
                        "source_span": {
                            "start": constraint_span.start,
                            "end": constraint_span.end,
                            "text": constraint_span.text,
                        },
                    },
                ),
            )
            status = "parsed_single" if candidates else "unparsed"
            return self._result(status, source, tuple(candidates), tuple(matched_rules), tuple(unresolved))

        rule_id, pattern = _RULE_DEFINITIONS[6]
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            matched_rules.append(rule_id)
            item_span = span(match, "item")
            target_span = span(match, "target")
            spans = (item_span, target_span)
            propose(
                "catalog.collect",
                {"item": item_span.text, "collection": target_span.text, "interpretation": "semantic_membership"},
                spans,
                rule_id,
            )
            propose(
                "catalog.file.move",
                {"item": item_span.text, "destination": target_span.text, "interpretation": "physical_move"},
                spans,
                rule_id,
            )
            if len(candidates) > 1:
                status = "collision"
            elif len(candidates) == 1:
                status = "parsed_single"
            else:
                status = "unparsed"
            return self._result(status, source, tuple(candidates), tuple(matched_rules), tuple(unresolved))

        simple_rules = (
            (1, "catalog.find", "term", lambda value: {"term": value}),
            (2, "catalog.inbox", "inbox", lambda _value: {}),
            (3, "catalog.show", "object", lambda value: {"object_id": value}),
            (4, "catalog.ls", "scope", lambda value: {"scope": value}),
            (5, "catalog.project.inspect", "project", lambda value: {"project": value}),
        )
        for rule_index, operation, group, make_arguments in simple_rules:
            rule_id, pattern = _RULE_DEFINITIONS[rule_index]
            match = re.match(pattern, text, re.IGNORECASE)
            if not match:
                continue
            matched_rules.append(rule_id)
            matched_span = span(match, group)
            propose(operation, make_arguments(matched_span.text), (matched_span,), rule_id)
            status = "parsed_single" if candidates else "unparsed"
            return self._result(status, source, tuple(candidates), tuple(matched_rules), tuple(unresolved))

        unresolved.append(UnresolvedRegion(0, len(text), text, "unsupported_text"))
        return self._result("unparsed", source, (), (), tuple(unresolved))

    def interpret_task_route(self, request: TaskRequest, routed: RouteResult) -> InterpretationResult:
        """Map existing generic task proposals into the catalog profile."""

        text = request.text
        source = SourceRecord.from_text(text)
        candidates: list[Candidate] = []
        unresolved: list[UnresolvedRegion] = []
        mapping_ids: list[str] = []

        def find_support(value: str) -> SourceSpan:
            if value:
                match = re.search(re.escape(value), text, re.IGNORECASE)
                if match:
                    return SourceSpan(match.start(), match.end(), text[match.start():match.end()])
            return SourceSpan(0, len(text), text)

        for task_result in routed.results:
            for proposal in task_result.proposals:
                key = (task_result.module_id, proposal.operation)
                if key == ("file-explorer", "search"):
                    operation = "catalog.find"
                    query = str(proposal.fields.get("query", "")).strip()
                    arguments: Mapping[str, Any] = {"term": query}
                    support = find_support(query)
                elif key == ("file-explorer", "list"):
                    operation = "catalog.ls"
                    scope = str(proposal.fields.get("path", "."))
                    arguments = {"scope": scope}
                    support = find_support(scope)
                else:
                    unresolved.append(
                        UnresolvedRegion(
                            0,
                            len(text),
                            text,
                            f"unmapped_task_proposal:{task_result.module_id}:{proposal.operation}",
                        )
                    )
                    continue

                mapping_id = f"task-map:{task_result.module_id}:{proposal.operation}/0.1"
                mapping_ids.append(mapping_id)
                if operation not in self.registry.operations:
                    unresolved.append(
                        UnresolvedRegion(
                            support.start,
                            support.end,
                            support.text,
                            f"operation_not_in_registry:{operation}",
                        )
                    )
                    continue
                argument_errors = self.registry.validate_arguments(operation, arguments)
                if argument_errors:
                    unresolved.append(
                        UnresolvedRegion(
                            support.start,
                            support.end,
                            support.text,
                            f"invalid_arguments:{operation}:{'|'.join(argument_errors)}",
                        )
                    )
                    continue
                evidence = tuple(
                    {"kind": "task_evidence", "value": item}
                    for item in proposal.evidence
                ) + ({"kind": "task_proposal", "status": proposal.status},)
                candidates.append(
                    Candidate(
                        operation=operation,
                        arguments=arguments,
                        source_spans=(support,),
                        origin_class="ADAPTER_NORMALIZATION",
                        origin_ref=mapping_id,
                        confidence=Confidence(1.0, "deterministic_mapping"),
                        evidence=evidence,
                    )
                )

        if len(candidates) > 1:
            status = "collision"
        elif len(candidates) == 1:
            status = "parsed_single"
        else:
            status = "unparsed"
            if not unresolved:
                unresolved.append(UnresolvedRegion(0, len(text), text, "no_task_proposals"))

        result = self._result(status, source, tuple(candidates), tuple(mapping_ids), tuple(unresolved))
        router_ids = tuple(match.module_id for match in routed.matches)
        task_status = "mapped" if candidates else "unmapped"
        return replace(
            result,
            layer_trace=(
                LayerTrace("generic-task-router", "0.1", routed.status, len(routed.results), router_ids),
                LayerTrace("catalog-task-adapter", MODULE_VERSION, task_status, len(candidates), tuple(mapping_ids)),
                result.layer_trace[-1],
            ),
        )

    def _result(
        self,
        status: str,
        source: SourceRecord,
        candidates: tuple[Candidate, ...],
        matched_rules: tuple[str, ...],
        unresolved: tuple[UnresolvedRegion, ...],
    ) -> InterpretationResult:
        if status not in STATUSES:
            raise ValueError(f"Unsupported catalog interpretation status: {status}")
        rule_status = "matched" if matched_rules else ("invalid" if status == "invalid_input" else "abstained")
        registry_status = "accepted" if candidates else "no_candidate_accepted"
        module = ModuleIdentity(
            module_id=MODULE_ID,
            module_version=MODULE_VERSION,
            capabilities=CAPABILITY_IDS,
            ruleset_digest=RULESET_DIGEST,
            configuration_digest=self.registry.configuration_digest,
        )
        return InterpretationResult(
            status=status,
            source=source,
            module=module,
            registry_version=self.registry.version,
            registry_digest=self.registry.configuration_digest,
            candidates=candidates,
            layer_trace=(
                LayerTrace("catalog-deterministic-rules", MODULE_VERSION, rule_status, len(candidates), matched_rules),
                LayerTrace("catalog-operation-registry", self.registry.version, registry_status, len(candidates), ()),
            ),
            unresolved=unresolved,
        )


def validate_interpretation(
    result: InterpretationResult,
    registry: CatalogOperationRegistry,
) -> tuple[str, ...]:
    """Return contract violations without mutating or executing the result."""

    errors: list[str] = []
    source = result.source
    if source.sha256 != sha256(source.exact_text.encode("utf-8")).hexdigest():
        errors.append("source_digest_mismatch")
    if source.char_length != len(source.exact_text):
        errors.append("source_length_mismatch")
    if result.status not in STATUSES:
        errors.append("unknown_status")
    if not set(CAPABILITY_IDS).issubset(result.module.capabilities):
        errors.append("required_capabilities_missing")
    if not result.module.module_id or not result.module.module_version or not result.module.ruleset_digest:
        errors.append("module_identity_incomplete")
    if result.module.configuration_digest != registry.configuration_digest:
        errors.append("configuration_digest_mismatch")
    if result.registry_version != registry.version or result.registry_digest != registry.configuration_digest:
        errors.append("registry_identity_mismatch")
    if result.authority_effect != "NONE" or result.execution_allowed:
        errors.append("result_authority_violation")
    if not result.layer_trace:
        errors.append("layer_trace_missing")

    for candidate in result.candidates:
        if candidate.operation not in registry.operations:
            errors.append(f"unknown_operation:{candidate.operation}")
        for argument_error in registry.validate_arguments(candidate.operation, candidate.arguments):
            errors.append(f"invalid_candidate_arguments:{candidate.operation}:{argument_error}")
        if candidate.origin_class not in ORIGIN_CLASSES:
            errors.append(f"unknown_origin_class:{candidate.origin_class}")
        if not candidate.confidence.semantics:
            errors.append(f"confidence_semantics_missing:{candidate.operation}")
        if candidate.admitted or candidate.execution_allowed or candidate.authority_effect != "NONE":
            errors.append(f"candidate_authority_violation:{candidate.operation}")
        if not candidate.source_spans and not candidate.origin_ref:
            errors.append(f"candidate_support_missing:{candidate.operation}")
        for support in candidate.source_spans:
            if support.start < 0 or support.end < support.start or support.end > source.char_length:
                errors.append(f"source_span_bounds:{candidate.operation}")
            elif source.exact_text[support.start:support.end] != support.text:
                errors.append(f"source_span_text_mismatch:{candidate.operation}")

    for region in result.unresolved:
        if region.start < 0 or region.end < region.start or region.end > source.char_length:
            errors.append("unresolved_span_bounds")
        elif source.exact_text[region.start:region.end] != region.text:
            errors.append("unresolved_span_text_mismatch")

    if result.status == "parsed_single" and len(result.candidates) != 1:
        errors.append("parsed_single_candidate_count")
    if result.status == "collision" and len(result.candidates) < 2:
        errors.append("collision_candidate_count")
    if result.status == "unparsed" and result.candidates:
        errors.append("unparsed_has_candidates")
    if result.status in {"unparsed", "conflict", "invalid_input"} and not result.unresolved:
        errors.append("non_success_without_unresolved")
    return tuple(errors)
