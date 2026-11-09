"""Reusable source-aware lexical evidence primitives."""

from .normalize import normalize_text, token_set
from .registry import SourceRecord, inventory, load_registry, source_path
from .synthesis import Candidate, SynthesisResult, synthesize
from .collisions import CollisionGroup, group_records
from .intent import IntentProposal, parse_intent
from .morphology import describe_features, group_forms, parse_features
from .pipeline import AnalysisResult, analyze_text
from .relations import RelationNode, TraversalResult, traverse_relations
from .adapters import ArgumentContract, CatalogAdapter, CatalogOperationRegistry, InterpretationResult, validate_interpretation

__all__ = [
    "Candidate",
    "ArgumentContract",
    "CatalogAdapter",
    "CatalogOperationRegistry",
    "AnalysisResult",
    "CollisionGroup",
    "IntentProposal",
    "InterpretationResult",
    "RelationNode",
    "SynthesisResult",
    "SourceRecord",
    "TraversalResult",
    "analyze_text",
    "describe_features",
    "group_forms",
    "group_records",
    "inventory",
    "load_registry",
    "normalize_text",
    "parse_features",
    "parse_intent",
    "source_path",
    "synthesize",
    "token_set",
    "traverse_relations",
    "validate_interpretation",
]
