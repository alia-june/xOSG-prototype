# Work Process / Microserver Transmigration v0.4.0

**Disposition:** `CANDIDATE_ONLY / NOT_ADMITTED / NOT_PUBLISHED`  
**Date:** 2026-11-06  
**Lineage:** v0.2 static validator → v0.3 microserver/glue reconstruction → v0.4 governed candidate chain

## What was implemented

This release retains the two runnable v0.3 JSON CLI microservers and their identity-only composition glue. It adds:

1. A **separate-process authority preflight** (`authority/gate.py`) with an explicit, versioned read-only candidate policy. The gate binds request ID, scope, and a manifest SHA-256 value. It does **not** authenticate the local operator.
2. A **strict Linux launcher** (`microtrans/governed.py`) that initiates each worker in its own user, mount, and network namespaces (`unshare`). A trusted bootstrap remounts all existing writable mountpoints read-only, then discards effective, permitted, bounding, inheritable and ambient capabilities and sets `no_new_privs` before importing worker code.
3. A **separate semantic validator** (`external_validator/validator.py`) with independent graph-traversal code and no import of `microtrans`. It shares the unchanged v0.2 JSON Schema, so this is *code-path independence*, not independent schema authority or external signing.
4. Negative probes for attempted writes to a protected file, writes to `/dev/shm`, remounting, forged authority/audit decisions and an unsupported OS path.

## Run the governed chain

Requirements: **Linux x86-64**, Python 3.10+, `jsonschema`, `unshare` with unprivileged user/mount/network namespace support, `setpriv`, `/usr/bin/mount` and `/proc`. The supported runtime in this package has only been tested in the local Linux environment, not broadly across distributions.

```bash
python -m pip install -r requirements.txt
python -m microtrans.governed examples/implementation_manifest_v0_3.json
python -m microtrans.governed examples/invalid_manifest_v0_3.json
python -m unittest discover -s tests -v
```

The first governed command returns `STATIC_PASSED` when all checks succeed. The deliberately invalid graph command returns `REFUSED` and exit status 1.

**Windows 11 LTSC:** `microtrans.governed` returns `OS_BOUNDARY_UNAVAILABLE` by design. Use no non-strict fallback when relying on this security boundary. The earlier v0.3 `microtrans.glue` remains available for comparative testing but is **not** covered by the v0.4 strict containment claim.

## Component locations

| Path | Description |
|---|---|
| `microtrans/schema_gate.py` | Existing v0.3 schema microserver (preserved) |
| `microtrans/graph_gate.py` | Existing v0.3 graph microserver (preserved) |
| `microtrans/glue.py` | Existing v0.3 ordinary composition glue (preserved) |
| `microtrans/governed.py` | v0.4 preflight/boundary/audit orchestrator |
| `authority/` | Separate-process static authority policy gate |
| `runtime/` | Namespaced read-only mount bootstrap, worker entry, negative probe |
| `external_validator/` | Separate implementation of graph checks and receipt cross-checks |
| `contracts/` | v0.2, v0.3 retained contracts and new v0.4 schemas |
| `tests/test_transmigration.py` | Retained v0.3 regression/parity corpus |
| `tests/test_governed_v0_4.py` | v0.4 governance, refusal and containment tests |
| `source_witness/` | Unchanged v0.2 checker and checksums |
| `lineage/v0_3/` | Previous release documentation, retained unmodified |
| `research/` | Non-activated Landlock experiment and reason for refusal |

## Explicitly out of scope

No HTTP listener, remote API credential, model API invocation, cryptographic service authentication, external signing, admission, publication, Crete enforcement, immutable generation management, broad file read containment, generic native-code sandbox, Windows security token implementation, or claim of proven source-wide equivalence.

The `STATIC_PASSED` result is **only a candidate static-validation result**.
