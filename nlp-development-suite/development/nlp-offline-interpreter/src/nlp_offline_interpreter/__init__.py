"""Generic, deterministic, non-executing interpretation framework."""

from .core import (
    DEFAULT_MAX_SOURCE_CHARS,
    RESULT_SCHEMA,
    InterpretationCandidate,
    InterpretationLayer,
    InterpretationRequest,
    InterpretationResult,
    Interpreter,
    LayerResult,
    LayerTrace,
    SourceSpan,
    UnresolvedRegion,
    canonical_json,
)
from .basic import BASIC_LAYER_VERSION, BasicTextLayer, analyze_text

__version__ = "0.1.1rc1"

__all__ = [
    "DEFAULT_MAX_SOURCE_CHARS",
    "RESULT_SCHEMA",
    "InterpretationCandidate",
    "InterpretationLayer",
    "InterpretationRequest",
    "InterpretationResult",
    "Interpreter",
    "LayerResult",
    "LayerTrace",
    "SourceSpan",
    "UnresolvedRegion",
    "canonical_json",
    "BASIC_LAYER_VERSION",
    "BasicTextLayer",
    "analyze_text",
]
