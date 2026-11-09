# Catalog ↔ Modular NLP Capability Handoff v0.1

**Status:** interface handoff / pre-integration contract  
**Authority:** advisory interpretation only  
**Runtime mutation authority:** NONE  
**Catalog baseline:** v0.5+ canonical command and proof-ceiling architecture

## 1. Purpose

The catalog needs an interchangeable NLP module that converts human language into **non-authoritative interpretation candidates**. The NLP does not execute catalog operations, write catalog state, move files, admit relationships, or decide truth. It supplies structured evidence to the catalog's canonical command/policy layer.

```text
human text
   ↓
NLP adapter
   ↓
InterpretationResult
   ↓
canonical command validation
   ↓
READ may execute
MUTATION remains separately authorized/wired
```

## 2. Required capabilities

### NLP-CAP-01 — Exact-source preservation
Return the exact input text plus a SHA-256 digest. Candidate evidence must identify source spans by character offsets and include the exact spanned text.

### NLP-CAP-02 — Finite canonical-operation mapping
Map supported requests only to operations supplied by the catalog command registry. Unknown operations must not be invented or forwarded as executable text.

### NLP-CAP-03 — Multiple-candidate preservation
When one phrase supports more than one materially different operation, return every supported candidate and status `collision`; do not pick one merely to make progress.

Required example:

```text
move report into MageCore
```

must preserve at least the semantic-membership versus physical-move distinction when both are supported by the phrase.

### NLP-CAP-04 — Constraint / negation extraction
Represent constraints explicitly rather than dropping them. Example:

```text
put report with MageCore, don't move the actual files
```

should support a semantic collection candidate carrying `physical_move: false` and no physical-move candidate unless another phrase independently supports it.

### NLP-CAP-05 — Typed non-success states
The adapter must support at least:

```text
parsed_single
collision
unparsed
conflict
invalid_input
```

`unparsed` is a valid abstention state, not a parser failure that grants permission to guess.

### NLP-CAP-06 — Explicit unresolved regions
Return unresolved spans/references/constraints at the smallest useful scope. Partial parsing preserves valid candidates and explicit holes independently.

### NLP-CAP-07 — Layer trace
Return ordered interpretation layers consulted, including layer ID/version, status, candidate contribution, and rule/model identifier. A lower layer may propose alternatives but must not silently overwrite a stronger higher-layer result.

### NLP-CAP-08 — Provenance class
Every candidate must identify how it was produced. Minimum vocabulary:

```text
DETERMINISTIC_RULE
STATISTICAL_MODEL
LLM_INFERENCE
EXTERNAL_LOOKUP
ADAPTER_NORMALIZATION
```

The catalog may map these into its own provenance taxonomy. These labels describe origin; they do not grant authority.

### NLP-CAP-09 — Confidence with semantics
If confidence is emitted, include its semantics (`probability`, `score`, `rank`, `heuristic`, etc.). A score without declared semantics is treated as `UNASSIGNED`.

### NLP-CAP-10 — Stable module identity
Expose:

```text
module_id
module_version
capability_ids[]
ruleset_digest / model_id+version
configuration_digest when configuration affects interpretation
```

This identity becomes part of interpretation provenance.

## 3. Required output envelope

Conceptual contract:

```json
{
  "status": "parsed_single | collision | unparsed | conflict | invalid_input",
  "source": {
    "exact_text": "...",
    "sha256": "...",
    "char_length": 0
  },
  "module": {
    "module_id": "...",
    "module_version": "...",
    "capabilities": ["NLP-CAP-01"],
    "ruleset_digest": "..."
  },
  "candidates": [
    {
      "operation": "catalog.find",
      "arguments": {"term": "recovery"},
      "source_spans": [{"start": 5, "end": 13, "text": "recovery"}],
      "origin_class": "DETERMINISTIC_RULE",
      "origin_ref": "rule:find-v2",
      "confidence": {"value": 1.0, "semantics": "deterministic_match"},
      "evidence": [],
      "admitted": false,
      "execution_allowed": false,
      "authority_effect": "NONE"
    }
  ],
  "layer_trace": [],
  "unresolved": [],
  "authority_effect": "NONE",
  "execution_allowed": false
}
```

The exact transport syntax may differ, but the semantic fields above are required.

## 4. Catalog operations the NLP may currently propose

Read operations:

```text
catalog.inbox
catalog.ls
catalog.show
catalog.find
catalog.project.inspect
```

Non-read candidates may be proposed but never executed by the NLP:

```text
catalog.collect
catalog.relate
catalog.file.move
```

The catalog command registry is authoritative for the current operation list. The NLP must accept a registry/version or capability description rather than hard-code a competing command ontology.

## 5. Explicit non-capabilities

The NLP must not:

- execute commands;
- write SQLite/JSON/XML catalog state;
- create admitted relationships or project membership;
- move, rename, delete, copy, or overwrite files;
- convert confidence into authority;
- resolve collisions invisibly;
- replace original source text with normalized paraphrase;
- infer that equal hashes imply one semantic object;
- claim that a generated interpretation is recovered historical fact;
- use external lookup without reporting that layer and its evidence.

## 6. Optional later capabilities

These are useful but are not prerequisites for initial integration:

```text
entity candidates
concept/topic candidates
relationship candidates
project/collection candidates
reference resolution candidates
intent/use candidates
keywords
synopsis proposal
synthesis proposal
implication proposal
```

All remain proposals with provenance and review status. Synopsis, synthesis, and implications must remain separate output classes.

## 7. Acceptance examples

| Input | Minimum acceptable disposition |
|---|---|
| `find recovery` | one `catalog.find` candidate |
| `show inbox` | one `catalog.inbox` candidate |
| `show object abc123` | one `catalog.show` candidate |
| `move report into MageCore` | collision preserving semantic versus physical interpretations |
| `put report with MageCore, don't move the actual files` | semantic candidate with explicit no-physical-move constraint |
| unsupported prose | `unparsed` with unresolved span; no invented command |
| empty input | `invalid_input` |

## 8. Integration handshake

Before accepting candidates, the catalog should validate:

1. module identity/version is present;
2. required capability IDs are declared;
3. source digest matches the text received by the catalog;
4. every candidate operation exists in the current catalog command registry;
5. every candidate has source support/spans or an explicit generated-origin record;
6. no candidate sets `admitted=true`, `execution_allowed=true`, or a non-`NONE` authority effect;
7. collision/unresolved information has not been collapsed;
8. module/ruleset/model provenance is recorded in the interpretation journal.

Failure of this handshake rejects the NLP envelope as an interpretation input. It does not authorize fallback execution.

## 9. Transmigration note

This handoff describes **capabilities and contracts**, not a requested implementation language or package. Your modular NLP may use its own internal architecture. The catalog needs the observable contract above so NLP components can be replaced without replacing catalog authority or query semantics.
