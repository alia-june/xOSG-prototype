# Lexicon Core

Reusable NLP primitives for Lexicon Atlas and sibling projects.

## First extraction

- `lexicon_core.registry` resolves the shared dictionary registry and source paths.
- `lexicon_core.normalize` provides deterministic text and token normalization.
- `lexicon_core.collisions` groups shared spellings while retaining every source row.
- `lexicon_core.morphology` labels UniMorph-style features and groups forms.
- `lexicon_core.relations` traverses semantic or lexical edges with depth and node bounds.
- `lexicon_core.intent` recognizes a narrow command shape as a proposal only.
- `lexicon_core.pipeline` composes the independent proposal stages.
- `lexicon_core.synthesis` ranks source-labeled lexical candidates without collapsing collisions.

The package is deliberately independent of Electron, the browser, and any LLM provider. It can be imported by the deterministic command parser, desktop shell services, or other front ends.

For local development, install it into a project environment with `pip install -e .` or add `src/` to that project's `PYTHONPATH`.

## Shared dictionary root

The default registry is:

```text
<LEXICON_DATA_ROOT>
```

Set `LEXICON_DATA_ROOT` to use another registry location. The registry exposes OEWN, CMUdict, IPA Dict, UniMorph, complete local Wiktionary, GCIDE, ODict, and the StarDict import inbox.

```text
python -c "from lexicon_core.registry import inventory; print(inventory())"
```

## Provenance boundary

The registry gives projects access to source files; it does not merge authority. WordNet and imported dictionary records remain candidate lexical evidence. Synthesis returns generated proposals with source references and scores. It does not create axioms, authorize commands, or execute anything.

## Status

This is the first extraction scaffold. The next work is to move the parser grammar and task-specific acceptance schemas into this package while keeping data access and generated interpretation separate.

The first command families are intentionally narrow: file search, word definition, relation lookup, and inspection. They return proposal objects; execution and authority remain outside this package.

## Task modules

`lexicon_core.tasks` supplies the first task adapters:

- `DictionaryModule` for lexical lookup proposals
- `FileExplorerModule` for file and directory search proposals
- `ExpertControlModule` for axiom, rule, and check proposals
- `ElizaNxtModule` for deterministic pattern-based conversation
- `route_request` for ranked capability routing with collision review

Every task returns `TaskResult` and `TaskProposal` objects. There is no shell execution, filesystem mutation, rule admission, or hidden module selection in this layer.

## Catalog adapter profile

`lexicon_core.adapters.catalog_v0_1` implements the advisory Aurora contract `catalog.modular-nlp-capability-handoff/0.1`. It accepts the catalog's current operation registry at runtime and returns a source-preserving `InterpretationResult` containing candidate operations, exact character spans, provenance, confidence semantics, layer trace, unresolved regions, and fixed non-authority fields.

```python
from lexicon_core.adapters import CatalogAdapter, CatalogOperationRegistry

registry = CatalogOperationRegistry.from_mapping({
    "handoff_id": "catalog.modular-nlp-capability-handoff/0.1",
    "current_operations": {
        "read": ["catalog.inbox", "catalog.show", "catalog.find"],
        "proposal_only": ["catalog.collect", "catalog.file.move"],
    },
    "operation_contracts": {
        "catalog.find": {
            "required": {"term": "string"},
            "optional": {},
            "allow_extra": False,
        }
    },
})
result = CatalogAdapter(registry).interpret("move report into MageCore")
print(result.to_dict())
```

The adapter does not execute a returned operation. The injected registry may provide typed argument contracts, and `interpret_task_route` maps existing file-explorer search and list proposals into the same catalog envelope. Generated schemas for the registry input and interpretation output are under `schemas/`, the seven source-derived dispositions are recorded in `examples/catalog-v0.1-acceptance.json`, and a candidate-plus-unresolved example is in `examples/catalog-v0.1-partial.json`. Implementation status and remaining work are recorded in `NOTES.md` and `TODO.md`.
