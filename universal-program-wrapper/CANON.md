# Canon / Extraction Record

## Accepted project rules carried into this unit

1. Public command-line interfaces use JSON input and JSON output.
2. JSON is the standard application-level semantic message format for interprocess communication unless explicitly overridden.
3. Messages are typed/versioned and carry request identity plus provenance/authority metadata fields where applicable.
4. Native JSON tools are validated directly.
5. Legacy command-line tools are adapted explicitly; the wrapper must not falsely claim the legacy tool speaks the native protocol.
6. Stable operation semantics and introspection are required.
7. Raw program exit status is preserved; wrapper-normalized outcome is separate.
8. Capability evidence levels remain distinct: declared, discovered, tested, observed, attested.
9. The Universal Program Wrapper is below/outside `sf-Program-Access`; `sf-Program-Access` applies safety restrictions and containment above the wrapper.
10. Authority metadata carried by a request is not itself an authority grant.

## Extraction rule

This package contains only the Universal Program Wrapper. Driver, catalog, BitCore, state-witness verifier, and safety-policy implementation are deliberately excluded.

## Implementation choices in v0.1 (not asserted as universal canon)

- Python standard-library reference implementation.
- One JSON object per CLI invocation rather than streaming NDJSON.
- Manifest-driven legacy CLI adapter.
- A small named wrapper control plane (`describe`, `operations`, `schema`, `version`, `status`, `invoke`). These names are wrapper API controls, not assignments of semantic aliases to BitCore operator codes.
