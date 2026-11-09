"""Dependency-free generic text analysis for the standalone artifact."""

from __future__ import annotations

import re

from .core import (
    InterpretationCandidate,
    InterpretationRequest,
    Interpreter,
    LayerResult,
    SourceSpan,
    UnresolvedRegion,
)


BASIC_LAYER_VERSION = "basic-text/1"
BASIC_MAX_SOURCE_CHARS = 4_096
BASIC_MAX_TOKENS = 256
_TOKEN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


class BasicTextLayer:
    """Create a bounded lexical surface analysis without inferring intent."""

    layer_id = "basic-text"
    layer_version = BASIC_LAYER_VERSION

    def interpret(self, request: InterpretationRequest) -> LayerResult:
        matches = []
        for match in _TOKEN.finditer(request.source_text):
            matches.append(match)
            if len(matches) > BASIC_MAX_TOKENS:
                break
        retained = matches[:BASIC_MAX_TOKENS]
        truncated = len(matches) > BASIC_MAX_TOKENS
        tokens = [
            {
                "text": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "kind": "word" if match.group(0).isalnum() or match.group(0).replace("_", "").isalnum() else "symbol",
            }
            for match in retained
        ]
        candidate = InterpretationCandidate(
            candidate_id="basic-text:analyze:1",
            operation="text.analyze",
            arguments={
                "tokens": tokens,
                "token_count": len(tokens),
                "truncated": truncated,
                "character_count": len(request.source_text),
                "line_count": request.source_text.count("\n") + 1,
            },
            layer_id=self.layer_id,
            provenance_class="deterministic_surface_analysis",
            evidence=("unicode lexical surface scan",),
            spans=(SourceSpan(0, len(request.source_text), "source"),),
            confidence={
                "semantics": "structural tokenization only; no intent or authority inference"
            },
        )
        if truncated:
            unresolved = (
                UnresolvedRegion(
                    retained[-1].end(),
                    len(request.source_text),
                    "token limit exceeded",
                    self.layer_id,
                ),
            )
            return LayerResult(
                self.layer_id,
                self.layer_version,
                "partial",
                (candidate,),
                unresolved,
            )
        return LayerResult(
            self.layer_id,
            self.layer_version,
            "candidates",
            (candidate,),
        )


def analyze_text(source_text: str):
    """Return a deterministic non-executing surface analysis."""

    return Interpreter(
        (BasicTextLayer(),),
        max_source_chars=BASIC_MAX_SOURCE_CHARS,
    ).interpret(
        source_text,
        metadata={"mode": "basic", "basic_layer_version": BASIC_LAYER_VERSION},
    )
