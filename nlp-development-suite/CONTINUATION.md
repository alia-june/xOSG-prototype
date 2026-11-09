# Development continuation

## Current working state

The modular core provides normalization, dictionary registry access, collision grouping, morphology, bounded relations, deterministic intent proposals, synthesis, and task adapters for dictionary lookup, file exploration, expert-system proposals, and ELIZA NXT.

The catalog profile `catalog.modular-nlp-capability-handoff/0.1` currently provides:

- exact source text, SHA-256, Unicode character counts, and source spans;
- the statuses `parsed_single`, `collision`, `unparsed`, `conflict`, and `invalid_input`;
- an injected operation registry with immutable typed argument contracts;
- visible semantic-membership versus physical-move candidates;
- explicit no-physical-move constraints;
- provenance classes, confidence semantics, layer traces, and unresolved regions;
- independent validation of operation membership, arguments, hashes, spans, capabilities, and authority invariants;
- a bridge from generic file-explorer search and list proposals to `catalog.find` and `catalog.ls`.

The staged packaged core passed 22 tests and the staged Natural Language front end passed 54 tests. Both generated Draft 2020-12 schemas, the supplied Aurora registry summary, and eight published fixtures were validated with `jsonschema` 4.26.0.

## Next development items

1. Receive reviewed catalog argument contracts and replace generated examples where necessary.
2. Add task mappings only after the catalog registry defines operations for dictionary, expert-control, or ELIZA NXT outputs.
3. Extend constraint parsing through reviewed examples and fixtures rather than unrestricted guessing.
4. Add more partial parses that preserve supported candidates and unresolved spans independently.
5. Define the sister parser's canonical parse-tree, logic, acceptance-state, and authority schemas.
6. Add metadata-preserving import and export to the Scaffold Walker UI.
7. Create a new handoff package after the observable contract stabilizes. Preserve older verified archives and receipts.

## Known boundary

The Aurora handoff is an advisory pre-integration contract. Local schema and behavioral validation demonstrate conformance of tested generated outputs; they do not establish catalog acceptance.
