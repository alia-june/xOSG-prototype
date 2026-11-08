"""Replaceable boundary adapters for external consumers."""

from .catalog_v0_1 import (
    CAPABILITY_IDS,
    CONTRACT_ID,
    ArgumentContract,
    CatalogAdapter,
    CatalogOperationRegistry,
    InterpretationResult,
    validate_interpretation,
)

__all__ = [
    "CAPABILITY_IDS",
    "CONTRACT_ID",
    "ArgumentContract",
    "CatalogAdapter",
    "CatalogOperationRegistry",
    "InterpretationResult",
    "validate_interpretation",
]
