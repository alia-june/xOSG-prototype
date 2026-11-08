"""Generic, deterministic, non-executing interpretation contracts.

The engine orders independent proposal layers and preserves their candidates,
unresolved regions, diagnostics, and trace.  It deliberately has no execution
interface and no domain-specific command ontology.
"""

from __future__ import annotations

from collections.abc import Sequence as SequenceABC
from dataclasses import dataclass, field
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Any, Mapping, Protocol, Sequence


RESULT_SCHEMA = "generic-interpretation/1"
DEFAULT_MAX_SOURCE_CHARS = 16_384
MAX_JSON_DEPTH = 16
MAX_JSON_ITEMS = 10_000
MAX_JSON_STRING_CHARS = 65_536
MAX_IDENTIFIER_CHARS = 256
MAX_DIAGNOSTIC_CHARS = 4_096
MAX_LAYERS = 64
MAX_LAYER_CANDIDATES = 256
MAX_LAYER_UNRESOLVED = 256
MAX_LAYER_DIAGNOSTICS = 256
MAX_CANDIDATE_EVIDENCE = 256
LAYER_STATUSES = frozenset(
    {"no_match", "candidates", "collision", "partial", "invalid_input", "error"}
)
INTERPRETER_MODES = frozenset({"first_candidate", "collect_all"})
RESULT_STATUSES = frozenset(
    {"parsed_single", "collision", "partial", "unparsed", "invalid_input"}
)
TRACE_STATUSES = LAYER_STATUSES | {"not_consulted"}


def _require_identifier(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    if len(value) > MAX_IDENTIFIER_CHARS:
        raise ValueError(f"{field_name} exceeds the length bound")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"{field_name} contains a control character")


def _require_diagnostic(value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("layer diagnostic must be a non-empty string")
    if len(value) > MAX_DIAGNOSTIC_CHARS:
        raise ValueError("layer diagnostic exceeds the length bound")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError("layer diagnostic contains a control character")


def _validate_json(value: Any, *, depth: int = 0, budget: list[int] | None = None) -> None:
    if budget is None:
        budget = [MAX_JSON_ITEMS]
    if depth > MAX_JSON_DEPTH:
        raise ValueError("JSON value exceeds the depth bound")
    budget[0] -= 1
    if budget[0] < 0:
        raise ValueError("JSON value exceeds the item bound")
    if value is None or isinstance(value, (bool, int)):
        return
    if isinstance(value, str):
        if len(value) > MAX_JSON_STRING_CHARS:
            raise ValueError("JSON string exceeds the length bound")
        return
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("JSON numbers must be finite")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("JSON object keys must be strings")
            _validate_json(item, depth=depth + 1, budget=budget)
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _validate_json(item, depth=depth + 1, budget=budget)
        return
    raise ValueError(f"value is not JSON-compatible: {type(value).__name__}")


def _freeze_json(
    value: Any, *, depth: int = 0, budget: list[int] | None = None
) -> Any:
    """Validate and detach JSON-like input into immutable containers."""

    if budget is None:
        budget = [MAX_JSON_ITEMS]
    if depth > MAX_JSON_DEPTH:
        raise ValueError("JSON value exceeds the depth bound")
    budget[0] -= 1
    if budget[0] < 0:
        raise ValueError("JSON value exceeds the item bound")
    if value is None or isinstance(value, (str, bool, int)):
        if isinstance(value, str) and len(value) > MAX_JSON_STRING_CHARS:
            raise ValueError("JSON string exceeds the length bound")
        return value
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("JSON numbers must be finite")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("JSON object keys must be strings")
            if len(key) > MAX_JSON_STRING_CHARS:
                raise ValueError("JSON object key exceeds the length bound")
            frozen[key] = _freeze_json(item, depth=depth + 1, budget=budget)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(
            _freeze_json(item, depth=depth + 1, budget=budget) for item in value
        )
    raise ValueError(f"value is not JSON-compatible: {type(value).__name__}")


def _json_copy(value: Any) -> Any:
    """Return detached built-in JSON containers for public serialization."""

    if isinstance(value, Mapping):
        return {key: _json_copy(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_copy(item) for item in value]
    return value


def _bounded_error(exc: BaseException) -> str:
    """Render a provider failure without unbounded or control-rich diagnostics."""

    try:
        message = str(exc)
    except Exception:
        message = "exception text unavailable"
    message = "".join(
        character if ord(character) >= 32 and ord(character) != 127 else " "
        for character in message
    ).strip()
    rendered = f"{type(exc).__name__}: {message or 'provider failure'}"
    if len(rendered) > MAX_DIAGNOSTIC_CHARS:
        return rendered[: MAX_DIAGNOSTIC_CHARS - 3] + "..."
    return rendered


@dataclass(frozen=True)
class SourceSpan:
    start: int
    end: int
    label: str = "evidence"

    def __post_init__(self) -> None:
        if (
            not isinstance(self.start, int)
            or isinstance(self.start, bool)
            or not isinstance(self.end, int)
            or isinstance(self.end, bool)
        ):
            raise ValueError("source span offsets must be integers")
        if self.start < 0 or self.end < self.start:
            raise ValueError("source span offsets are invalid")
        _require_identifier(self.label, "source span label")

    def validate(self, source_length: int) -> None:
        if (
            not isinstance(self.start, int)
            or isinstance(self.start, bool)
            or not isinstance(self.end, int)
            or isinstance(self.end, bool)
        ):
            raise ValueError("source span offsets must be integers")
        if self.start < 0 or self.end < self.start or self.end > source_length:
            raise ValueError("source span is outside the source text")
        _require_identifier(self.label, "source span label")

    def to_dict(self) -> dict[str, Any]:
        return {"start": self.start, "end": self.end, "label": self.label}


@dataclass(frozen=True)
class InterpretationRequest:
    source_text: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.source_text, str):
            raise TypeError("source_text must be a string")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze_json(self.metadata))

    @property
    def source_sha256(self) -> str:
        return sha256(self.source_text.encode("utf-8", errors="surrogatepass")).hexdigest()


@dataclass(frozen=True)
class InterpretationCandidate:
    candidate_id: str
    operation: str
    arguments: Mapping[str, Any]
    layer_id: str
    provenance_class: str
    evidence: tuple[str, ...] = ()
    spans: tuple[SourceSpan, ...] = ()
    confidence: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        _require_identifier(self.candidate_id, "candidate_id")
        _require_identifier(self.operation, "operation")
        _require_identifier(self.layer_id, "layer_id")
        _require_identifier(self.provenance_class, "provenance_class")
        if not isinstance(self.arguments, Mapping):
            raise ValueError("candidate arguments must be a mapping")
        object.__setattr__(self, "arguments", _freeze_json(self.arguments))
        if not isinstance(self.evidence, SequenceABC) or isinstance(
            self.evidence, (str, bytes)
        ):
            raise ValueError("candidate evidence must be a sequence of strings")
        if not isinstance(self.spans, SequenceABC) or isinstance(self.spans, (str, bytes)):
            raise ValueError("candidate spans must be a sequence")
        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(self, "spans", tuple(self.spans))
        if len(self.evidence) > MAX_CANDIDATE_EVIDENCE:
            raise ValueError("candidate evidence count exceeds the bound")
        for item in self.evidence:
            _require_identifier(item, "candidate evidence")
        if not all(isinstance(item, SourceSpan) for item in self.spans):
            raise ValueError("candidate spans must contain SourceSpan values")
        if self.confidence is not None:
            if not isinstance(self.confidence, Mapping):
                raise ValueError("candidate confidence must be a mapping or null")
            object.__setattr__(self, "confidence", _freeze_json(self.confidence))

    def validate(self, source_length: int) -> None:
        _require_identifier(self.candidate_id, "candidate_id")
        _require_identifier(self.operation, "operation")
        _require_identifier(self.layer_id, "layer_id")
        _require_identifier(self.provenance_class, "provenance_class")
        _validate_json(self.arguments)
        if self.confidence is not None:
            if not isinstance(self.confidence, Mapping):
                raise ValueError("candidate confidence must be a mapping or null")
            _validate_json(self.confidence)
        for item in self.evidence:
            _require_identifier(item, "candidate evidence")
        for span in self.spans:
            span.validate(source_length)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "operation": self.operation,
            "arguments": _json_copy(self.arguments),
            "layer_id": self.layer_id,
            "provenance_class": self.provenance_class,
            "evidence": list(self.evidence),
            "spans": [span.to_dict() for span in self.spans],
            "confidence": _json_copy(self.confidence) if self.confidence is not None else None,
            "authority_effect": "NONE",
            "execution_allowed": False,
        }


@dataclass(frozen=True)
class UnresolvedRegion:
    start: int
    end: int
    reason: str
    layer_id: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.start, int)
            or isinstance(self.start, bool)
            or not isinstance(self.end, int)
            or isinstance(self.end, bool)
        ):
            raise ValueError("unresolved offsets must be integers")
        if self.start < 0 or self.end < self.start:
            raise ValueError("unresolved offsets are invalid")
        _require_identifier(self.reason, "unresolved reason")
        _require_identifier(self.layer_id, "unresolved layer_id")

    def validate(self, source_length: int) -> None:
        SourceSpan(self.start, self.end, "unresolved").validate(source_length)
        _require_identifier(self.reason, "unresolved reason")
        _require_identifier(self.layer_id, "unresolved layer_id")

    def to_dict(self) -> dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "reason": self.reason,
            "layer_id": self.layer_id,
        }


@dataclass(frozen=True)
class LayerResult:
    layer_id: str
    layer_version: str
    status: str
    candidates: tuple[InterpretationCandidate, ...] = ()
    unresolved: tuple[UnresolvedRegion, ...] = ()
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_identifier(self.layer_id, "layer_id")
        _require_identifier(self.layer_version, "layer_version")
        if self.status not in LAYER_STATUSES:
            raise ValueError(f"unsupported layer status: {self.status}")
        for field_name in ("candidates", "unresolved", "diagnostics"):
            value = getattr(self, field_name)
            if not isinstance(value, SequenceABC) or isinstance(value, (str, bytes)):
                raise ValueError(f"{field_name} must be a sequence")
            object.__setattr__(self, field_name, tuple(value))
        if not all(isinstance(item, InterpretationCandidate) for item in self.candidates):
            raise ValueError("candidates must contain InterpretationCandidate values")
        if not all(isinstance(item, UnresolvedRegion) for item in self.unresolved):
            raise ValueError("unresolved must contain UnresolvedRegion values")

    def validate(self, source_length: int) -> None:
        _require_identifier(self.layer_id, "layer_id")
        _require_identifier(self.layer_version, "layer_version")
        if self.status not in LAYER_STATUSES:
            raise ValueError(f"unsupported layer status: {self.status}")
        if len(self.candidates) > MAX_LAYER_CANDIDATES:
            raise ValueError("layer candidate count exceeds the bound")
        if len(self.unresolved) > MAX_LAYER_UNRESOLVED:
            raise ValueError("layer unresolved count exceeds the bound")
        if len(self.diagnostics) > MAX_LAYER_DIAGNOSTICS:
            raise ValueError("layer diagnostic count exceeds the bound")
        seen: set[str] = set()
        for candidate in self.candidates:
            candidate.validate(source_length)
            if candidate.layer_id != self.layer_id:
                raise ValueError("candidate layer_id does not match its layer result")
            if candidate.candidate_id in seen:
                raise ValueError(f"duplicate candidate_id in layer: {candidate.candidate_id}")
            seen.add(candidate.candidate_id)
        for item in self.unresolved:
            item.validate(source_length)
            if item.layer_id != self.layer_id:
                raise ValueError("unresolved layer_id does not match its layer result")
        for diagnostic in self.diagnostics:
            _require_diagnostic(diagnostic)
        if any(len(item.evidence) > MAX_CANDIDATE_EVIDENCE for item in self.candidates):
            raise ValueError("candidate evidence count exceeds the bound")
        if self.status == "no_match" and self.candidates:
            raise ValueError("no_match layer result cannot contain candidates")
        if self.status == "candidates" and not self.candidates:
            raise ValueError("candidates layer result must contain a candidate")
        if self.status == "candidates" and self.unresolved:
            raise ValueError("candidates with unresolved regions must use partial status")
        if self.status == "collision" and len(self.candidates) < 2:
            raise ValueError("collision layer result must contain at least two candidates")
        if self.status == "partial" and (not self.candidates or not self.unresolved):
            raise ValueError("partial layer result requires candidates and unresolved regions")


class InterpretationLayer(Protocol):
    layer_id: str
    layer_version: str

    def interpret(self, request: InterpretationRequest) -> LayerResult:
        """Return proposals and evidence without executing an operation."""


@dataclass(frozen=True)
class LayerTrace:
    layer_id: str
    layer_version: str
    status: str
    candidate_count: int
    unresolved_count: int
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_identifier(self.layer_id, "layer trace layer_id")
        _require_identifier(self.layer_version, "layer trace layer_version")
        if self.status not in TRACE_STATUSES:
            raise ValueError(f"unsupported layer trace status: {self.status}")
        for name in ("candidate_count", "unresolved_count"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if not isinstance(self.diagnostics, SequenceABC) or isinstance(
            self.diagnostics, (str, bytes)
        ):
            raise ValueError("layer trace diagnostics must be a sequence")
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        if len(self.diagnostics) > MAX_LAYER_DIAGNOSTICS:
            raise ValueError("layer trace diagnostic count exceeds the bound")
        for diagnostic in self.diagnostics:
            _require_diagnostic(diagnostic)

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "layer_version": self.layer_version,
            "status": self.status,
            "candidate_count": self.candidate_count,
            "unresolved_count": self.unresolved_count,
            "diagnostics": list(self.diagnostics),
        }


@dataclass(frozen=True)
class InterpretationResult:
    source_text: str
    source_sha256: str
    source_length: int
    status: str
    candidates: tuple[InterpretationCandidate, ...]
    unresolved: tuple[UnresolvedRegion, ...]
    layer_trace: tuple[LayerTrace, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.source_text, str):
            raise TypeError("source_text must be a string")
        expected_hash = sha256(
            self.source_text.encode("utf-8", errors="surrogatepass")
        ).hexdigest()
        if self.source_sha256 != expected_hash:
            raise ValueError("source_sha256 does not match source_text")
        if (
            not isinstance(self.source_length, int)
            or isinstance(self.source_length, bool)
            or self.source_length != len(self.source_text)
        ):
            raise ValueError("source_length does not match source_text")
        if self.status not in RESULT_STATUSES:
            raise ValueError(f"unsupported interpretation status: {self.status}")
        object.__setattr__(self, "candidates", tuple(self.candidates))
        object.__setattr__(self, "unresolved", tuple(self.unresolved))
        object.__setattr__(self, "layer_trace", tuple(self.layer_trace))
        if not all(isinstance(item, InterpretationCandidate) for item in self.candidates):
            raise ValueError("result candidates contain an invalid value")
        if not all(isinstance(item, UnresolvedRegion) for item in self.unresolved):
            raise ValueError("result unresolved regions contain an invalid value")
        if not all(isinstance(item, LayerTrace) for item in self.layer_trace):
            raise ValueError("result layer trace contains an invalid value")
        candidate_ids: set[str] = set()
        candidate_counts: dict[str, int] = {}
        for candidate in self.candidates:
            candidate.validate(len(self.source_text))
            if candidate.candidate_id in candidate_ids:
                raise ValueError("result candidate IDs must be unique")
            candidate_ids.add(candidate.candidate_id)
            candidate_counts[candidate.layer_id] = candidate_counts.get(candidate.layer_id, 0) + 1
        for item in self.unresolved:
            item.validate(len(self.source_text))
        trace_ids = [item.layer_id for item in self.layer_trace]
        if len(trace_ids) != len(set(trace_ids)):
            raise ValueError("result layer trace IDs must be unique")
        trace_counts = {item.layer_id: item.candidate_count for item in self.layer_trace}
        if any(trace_counts.get(layer_id) != count for layer_id, count in candidate_counts.items()):
            raise ValueError("result candidate counts do not match the layer trace")
        if sum(trace_counts.values()) != len(self.candidates):
            raise ValueError("result layer trace candidate total is inconsistent")
        if self.status == "parsed_single" and len(self.candidates) != 1:
            raise ValueError("parsed_single result requires exactly one candidate")
        if self.status == "parsed_single" and self.unresolved:
            raise ValueError("parsed_single result cannot contain unresolved regions")
        if self.status == "collision" and len(self.candidates) < 2:
            raise ValueError("collision result requires at least two candidates")
        if self.status == "partial" and (not self.candidates or not self.unresolved):
            raise ValueError("partial result requires candidates and unresolved regions")
        if self.status in {"unparsed", "invalid_input"} and self.candidates:
            raise ValueError(f"{self.status} result cannot contain candidates")
        if self.status in {"unparsed", "invalid_input"} and not self.unresolved:
            raise ValueError(f"{self.status} result requires an unresolved region")
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze_json(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": RESULT_SCHEMA,
            "source_text": self.source_text,
            "source_sha256": self.source_sha256,
            "source_length": self.source_length,
            "status": self.status,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "unresolved": [item.to_dict() for item in self.unresolved],
            "layer_trace": [item.to_dict() for item in self.layer_trace],
            "metadata": _json_copy(self.metadata),
            "authority_effect": "NONE",
            "execution_allowed": False,
        }


class Interpreter:
    """Compose ordered proposal layers under an explicit collection policy."""

    def __init__(
        self,
        layers: Sequence[InterpretationLayer],
        *,
        mode: str = "first_candidate",
        max_source_chars: int = DEFAULT_MAX_SOURCE_CHARS,
    ) -> None:
        if mode not in INTERPRETER_MODES:
            raise ValueError(f"unsupported interpreter mode: {mode}")
        if (
            not isinstance(max_source_chars, int)
            or isinstance(max_source_chars, bool)
            or max_source_chars < 1
        ):
            raise ValueError("max_source_chars must be a positive integer")
        if not isinstance(layers, SequenceABC) or isinstance(layers, (str, bytes)):
            raise TypeError("layers must be a finite sequence")
        self.layers = tuple(layers)
        if len(self.layers) > MAX_LAYERS:
            raise ValueError("layer count exceeds the bound")
        self.mode = mode
        self.max_source_chars = max_source_chars
        seen: set[str] = set()
        identities: list[tuple[str, str]] = []
        for layer in self.layers:
            _require_identifier(layer.layer_id, "layer_id")
            _require_identifier(layer.layer_version, "layer_version")
            if not callable(getattr(layer, "interpret", None)):
                raise TypeError(f"layer {layer.layer_id!r} has no callable interpret method")
            if layer.layer_id in seen:
                raise ValueError(f"duplicate layer_id: {layer.layer_id}")
            seen.add(layer.layer_id)
            identities.append((layer.layer_id, layer.layer_version))
        self._layer_identities = tuple(identities)

    def interpret(
        self, source_text: str, *, metadata: Mapping[str, Any] | None = None
    ) -> InterpretationResult:
        request = InterpretationRequest(source_text, metadata if metadata is not None else {})
        too_long = len(source_text) > self.max_source_chars
        empty = False if too_long else not source_text.strip()
        if too_long or empty:
            reason = "source text exceeds the length bound" if too_long else "source text is empty"
            unresolved = (
                UnresolvedRegion(0, len(source_text), reason, "interpreter"),
            )
            return InterpretationResult(
                source_text,
                request.source_sha256,
                len(source_text),
                "invalid_input",
                (),
                unresolved,
                (),
                dict(request.metadata),
            )

        candidates: list[InterpretationCandidate] = []
        unresolved: list[UnresolvedRegion] = []
        pending_unresolved: list[UnresolvedRegion] = []
        trace: list[LayerTrace] = []
        seen_candidate_ids: set[str] = set()
        stopped = False

        for layer, (layer_id, layer_version) in zip(self.layers, self._layer_identities):
            if stopped:
                trace.append(
                    LayerTrace(layer_id, layer_version, "not_consulted", 0, 0)
                )
                continue
            try:
                result = layer.interpret(request)
                if result.layer_id != layer_id or result.layer_version != layer_version:
                    raise ValueError("layer result identity does not match provider identity")
                result.validate(len(source_text))
                duplicates = seen_candidate_ids.intersection(
                    candidate.candidate_id for candidate in result.candidates
                )
                if duplicates:
                    raise ValueError(
                        f"candidate IDs are not unique across layers: {sorted(duplicates)}"
                    )
            except Exception as exc:  # provider failures are evidence, not process authority
                trace.append(
                    LayerTrace(
                        layer_id,
                        layer_version,
                        "error",
                        0,
                        0,
                        (_bounded_error(exc),),
                    )
                )
                continue

            candidates.extend(result.candidates)
            if result.candidates:
                unresolved.extend(result.unresolved)
            else:
                pending_unresolved.extend(result.unresolved)
            seen_candidate_ids.update(candidate.candidate_id for candidate in result.candidates)
            trace.append(
                LayerTrace(
                    result.layer_id,
                    result.layer_version,
                    result.status,
                    len(result.candidates),
                    len(result.unresolved),
                    result.diagnostics,
                )
            )
            if self.mode == "first_candidate" and result.candidates:
                stopped = True

        if len(candidates) > 1:
            status = "collision"
        elif candidates and unresolved:
            status = "partial"
        elif candidates:
            status = "parsed_single"
        else:
            status = "unparsed"
            unresolved.extend(pending_unresolved)
            if not unresolved:
                unresolved.append(
                    UnresolvedRegion(
                        0, len(source_text), "no layer produced a candidate", "interpreter"
                    )
                )
        return InterpretationResult(
            source_text,
            request.source_sha256,
            len(source_text),
            status,
            tuple(candidates),
            tuple(unresolved),
            tuple(trace),
            request.metadata,
        )


def canonical_json(result: InterpretationResult) -> str:
    """Return deterministic UTF-8 JSON text for a result."""

    return json.dumps(
        result.to_dict(),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
