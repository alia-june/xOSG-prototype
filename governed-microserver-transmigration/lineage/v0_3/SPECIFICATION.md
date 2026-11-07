# Microserver Transmigration — Executable Candidate Specification v0.3.0

## 1. Lineage and scope

This is an implementation of the previously specified *Transmigrate → {API microservers, glue}* stage, specifically for the static candidate manifest checker from v0.2. It does not claim to implement Plan/Research/Build/Redux/Decompose as an automatic lifecycle engine, nor does it reinterpret or finalize the three Redux pass objectives.

The source-checker functionality was **reconstructed** across two operations. The original checker, original manifest schema, and original example manifest are preserved in this package. The original v0.2 script remains a historical comparison witness; no original project is overwritten.

| Source behavior | Candidate microserver | Notes |
|---|---|---|
| JSON Schema Draft 2020-12 validation | `schema-gate.validate_manifest_schema` | Preserves the accepted manifest unchanged as application data |
| Duplicate server/operation/edge identity rejection | `graph-gate.validate_manifest_graph` | Reconstructed logic, typed faults |
| Endpoint existence + schema alignment | `graph-gate.validate_manifest_graph` | Uses exact versioned schema identities from v0.2 |
| Ordinary vs Crete declaration constraints | `graph-gate.validate_manifest_graph` | Verifies declarations, does **not** implement Crete |
| Unbounded dependency-cycle rejection | `graph-gate.validate_manifest_graph` | Iterative topological test rather than recursive DFS |
| CLI tool return code | Microserver response envelope + glue process exit | CANDIDATE_ONLY receipts, explicit refusal |

## 2. Runtime composition

```text
explicit local CLI request (manifest path)
       |
       v
 manifest-glue (read-only candidate flow, bounded input)
       |
       | JSON request #1 (local stdin/stdout, separate Python process)
       v
 schema-gate ---> accepted application data: the identical manifest
       |                              |
       +---- SHA-256 equality check --+
       |
       | identity-only application data forwarding; no authority transfer
       v
 graph-gate (separate process; independently rechecks schema precondition)
       |
       v
 glue verifies digest, response identity, no contradictions
       |
       v
 STATIC_PASSED or REFUSED receipt; always NOT_ADMITTED and NOT_PUBLISHED
```

The JSON protocol framing may differ between services, but **application payload** on the only glue edge is an identical canonical JSON object; no content conversion or permission transfer is performed. The shared schema contract is a read-only library dependency, not a third microserver. Only the two named services can be spawned; there is no name-to-command registry accepting user-supplied executable paths.

## 3. Contract boundaries

Service request shape:

```json
{
  "protocol_version": "0.3.0",
  "request_id": "demo-001",
  "operation": "validate_manifest_schema",
  "authority": {"mode": "READ_ONLY_CANDIDATE", "basis": "EXPLICIT_LOCAL_INVOKER"},
  "payload": {"manifest": {"schema_version": "0.2.0"}}
}
```

The excerpt above describes **framing only**; its abbreviated manifest intentionally does not satisfy the full v0.2 manifest schema. Use `examples/request_schema_v0_3.json` for a valid complete request.

- One request per child process invocation; one response with `decision` ACCEPTED/REFUSED.
- Strict UTF-8 JSON. Duplicate member names, `null`, NaN, Infinity, exponent overflow to non-finite floats, unsupported operations, and broader authority claims are rejected.
- Max input is 2 MiB per request; child process has a 5-second subprocess timeout; captured reply is size-limited. These are **local control bounds**; the OS is not sandboxed and untrusted code is not executed.
- Existing candidate manifest schema is unchanged and can describe CRETE edges as **declarations only**. The v0.3 implementation graph uses ORDINARY_GLUE / NO_MUTATION.
- Schema-gate response data is the same application manifest. Graph-gate response data is a static check report. Both carry an input digest and candidate-only status.
- Service-level accepted decisions mean the service evaluated its contract successfully, not that any authority was granted.
- Unexpected service exit, schema refusal, graph refusal, digest disagreement, timeout, or malformed response leads to **REFUSED**, never to publication.

## 4. Identity, intent and authority

Identity, source witness and 4-field intent stay separate. The 4 required intent fields are `goal`, `current_task`, `task_queue`, and `finished_task_queue`; prior history does not grant present authority. All unresolved/absent fields use typed named sentinels (never JSON `null`).

The service declaration `READ_ONLY_CANDIDATE` and process separation do not authenticate the calling process or enforce filesystem restrictions at the operating-system level. They are local application constraints. The test harness does not run under a restricted user/token, network sandbox, brokered IPC namespace, or integrity-enforced kernel policy.

No component can admit itself. Neither a microserver response nor glue output can upgrade authority, bypass refusal, sign receipts, or publish an artifact. Declared authority ceilings remain maxima requiring separate runtime authorization for any future side effects.

## 5. Source comparison and validation scope

The source witness is the unchanged v0.2 `check_manifest.py` function. The parity suite runs that original validator against a corpus of 19 candidate manifests and independently checks the v0.3 two-stage result. These cases include valid input, schema violations, duplicate identities, missing endpoints, mismatched schema references, invalid Crete/ordinary joins, and feedback cycles.

Matching acceptance for a finite set of test inputs is **not** general semantic equivalence. The implementation also tests separate child-process calls, refusals, SHA-256 identity checks, and structural validity of its own self-manifest. The reference checker and reimplementation share the same JSON Schema; this is not wholly independent validation.

## 6. Remaining gates (not implemented)

1. An external, independently maintained semantic validator and broader property/differential corpus.
2. OS-enforced process confinement, least-privilege identity, resource limits, and securely brokered IPC; Windows validation is pending.
3. Authenticated service messages, canonical serialization specification across languages, replay controls, and independently signed receipts if required.
4. Hardened Crete joins with independently testable break-before-mutation witnesses. Crete cannot be inferred from a manifest field.
5. Authorized admission, sealed immutable generation, rollback/retirement, and publication.
6. Any transport adapter beyond local JSON CLI, including HTTP and remote APIs.
7. Provenance selection and migration of a production module beyond this one bounded static capability.

## 7. Explicit disposition

**IMPLEMENTED:** two callable JSON CLI processes; ordinary glue; candidate schema/graph validation; source-comparison and negative tests.  
**TESTED LOCALLY:** Python 3.13 on Linux; tests recorded in `VALIDATION_REPORT.md`.  
**NOT CLAIMED:** a generic complete microserver platform, network service, Crete security, signed attestation, runtime sandbox, source-wide equivalence, admission, or deployment.
