# Lexicon Core todo

## Catalog adapter v0.1

- [x] Inventory the advisory Aurora capability handoff and record its hashes.
- [x] Add a catalog-specific adapter without changing generic task-module authority.
- [x] Inject the catalog operation registry and version into the adapter.
- [x] Preserve exact input, SHA-256, Unicode character length, and source spans.
- [x] Add required result statuses, provenance class, confidence semantics, layer trace, and unresolved regions.
- [x] Preserve semantic-membership versus physical-move collisions.
- [x] Extract the explicit no-physical-move constraint in the acceptance example.
- [x] Add a Draft 2020-12 output schema and behavioral tests.
- [x] Validate the schema and seven acceptance envelopes with `jsonschema` 4.26.0 Draft 2020-12 validation.
- [x] Add registry-supplied typed argument contracts and validate generated or received candidate arguments against them.
- [x] Add a generated Draft 2020-12 schema for the catalog operation-registry input.
- [ ] Map existing generic task-module proposals through the catalog profile.
  - [x] Map file-explorer search and list proposals.
  - [ ] Define catalog operations before mapping dictionary, expert-control, or ELIZA NXT proposals.
- [ ] Extend constraint parsing beyond the accepted no-physical-move family.
  - [x] Support both `do not move` and `without moving` forms.
  - [ ] Add further forms only with reviewed examples and explicit fixtures.
- [x] Add a partial-parse fixture containing both a supported candidate and an unresolved region.
- [ ] Receive and record catalog acceptance or rejection; generated compatibility is not acceptance.
- [ ] Create a new versioned sister handoff after the adapter contract stabilizes; do not overwrite the verified prior archive.

## Other task profiles

- [ ] Add the sister parser's parse-tree and logic representation after its canonical schema is supplied.
- [ ] Add expert-system acceptance and transition schemas.
- [ ] Add the ELIZA NXT response and history contract.
- [ ] Add scaffold-editor metadata-preserving import and export.
