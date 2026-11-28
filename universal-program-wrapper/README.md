# Universal Program Wrapper v0.1

Status: extracted standalone working unit.

The Universal Program Wrapper (UPW) provides one stable JSON boundary around programs and tools. It normalizes discovery, request validation, invocation, results, provenance carriage, and adapter behavior without absorbing the safety policy layer above it or the program-specific semantics below it.

## Owns

- JSON stdin/stdout request-response contract.
- Typed/versioned envelopes and request IDs.
- Operation registry and introspection.
- Schema validation at the wrapper boundary.
- Adapter dispatch.
- Legacy CLI translation: structured input -> argv/stdin/env -> stdout/stderr/exit -> normalized JSON.
- Raw process outcome preservation alongside normalized wrapper outcome.
- Provenance and authority-context carriage as data.
- Explicit side-effect and capability declarations supplied by manifests.
- Transport-neutral core callable from CLI, IPC, service, or another adapter.

## Does not own

- `sf-Program-Access` safety/containment policy.
- Authority grants or privilege elevation.
- Bitcode semantic verification / State Frames / State Witnesses.
- Windows minifilter behavior.
- File cataloging or lineage storage.
- The wrapped program's internal semantics.
- Attestation merely because metadata is present.

## Quick start

```bash
python -m upw.cli --manifest examples/python_manifest.json < request.json
```

For real use, replace the example executable path with an exact executable path valid on the host.

## Canonical stream behavior

- stdin: one JSON request object per invocation.
- stdout: one JSON response object only.
- stderr: human diagnostics only.
- wrapper must not mix human prose into stdout.

See `ARCHITECTURE.md`, `SPEC.md`, and `CANON.md`.
