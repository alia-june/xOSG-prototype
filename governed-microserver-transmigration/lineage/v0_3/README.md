# Work Process: Microserver Transmigration Reference v0.3.0

**Disposition:** CANDIDATE_ONLY / NOT_ADMITTED / NOT_PUBLISHED  
**Date:** 2026-11-06  
**Source:** v0.2 static candidate-manifest checker, preserved under `source_witness/`

This package transmigrates an actual existing capability rather than creating an unrelated illustrative service: v0.2's manifest checker is reconstructed as two independently callable **local JSON CLI microservers** and a separately declared **ordinary glue** layer. The microservers run in distinct Python subprocesses; this is process separation, **not** an OS security sandbox.

## Contents

- `microtrans/schema_gate.py`: candidate manifest schema validation, preserving application payload.
- `microtrans/graph_gate.py`: graph identity, endpoint, type-alignment, join declarations, acyclicity.
- `microtrans/glue.py`: bounded subprocess orchestration, identity-only forwarding, digest checks, refusal propagation.
- `microtrans/schema_validation.py`: shared prerequisite schema check (pinned contract; not a server).
- `microtrans/protocol.py`: request/response framing, strict JSON, typed refusals, SHA-256.
- `contracts/`: unchanged v0.2 candidate manifest JSON Schema plus new v0.3 protocol contracts.
- `examples/`: source manifest, v0.3 self-manifest, request and execution receipts.
- `source_witness/`: original checker and its SHA-256 source witness.
- `tests/`: regression and negative tests, including comparison against the preserved v0.2 checker.
- `SPECIFICATION.md`: boundaries, semantics, and authority model.
- `VALIDATION_REPORT.md`: observed test scope and unproven claims.
- `WORKING_RESEARCH_PROMPT.md`: exportable next-step research instructions.

## Run (Python 3.10+; `jsonschema` dependency)

From the package root, install dependency into your **own isolated Python environment**:

```powershell
python -m pip install -r requirements.txt
python -m microtrans.glue examples/source_manifest_v0_2.json
python -m microtrans.glue examples/implementation_manifest_v0_3.json
python -m unittest discover -s tests -v
```

The same commands are available in a POSIX shell. Python 3.13 and jsonschema 4.26 were used for the recorded local test run; Windows 11 LTSC is **not** tested here.

Direct service calls accept one UTF-8 JSON value on stdin and emit one JSON response on stdout. Examples:

```powershell
Get-Content -Raw examples/request_schema_v0_3.json | python -m microtrans.schema_gate
```

```bash
python -m microtrans.schema_gate < examples/request_schema_v0_3.json
```

For a rejection demo:

```powershell
python -m microtrans.glue examples/invalid_manifest_v0_3.json
```

The rejection invocation intentionally exits 1 and emits a structured refusal. No service listens on an HTTP port. There are no provider API calls, model-generated results, admission changes, publication, persistent database writes, or target mutations.

## Interpretation

`STATIC_PASSED` means only that the designated static validators accepted this particular manifest. It is not an execution authorization, independent attestation, approved provenance chain, Crete verification, or admission/publication decision. Every receipt stays `CANDIDATE_ONLY / NOT_ADMITTED / NOT_PUBLISHED`.

Consult `SPECIFICATION.md` for the exact source-to-destination mapping and stop conditions.
