# Working research prompt — v0.5 Windows candidate

Goal: Validate and harden the independent Windows 11 LTSC microserver sandbox without changing the user-established architecture. Do not claim runtime evidence from cross-platform mocks.

Current task: Stage on Windows 11 LTSC 2024 x64 test VM, provision exactly three AppContainer identities with explicit approval, set least-permissive read/execute ACLs on a trusted immutable Python/runtime/package deployment, then run opt-in probes and end-to-end candidate validation. Independently capture process token data, AppContainer SID, capabilities, integrity level, Job Object limits and membership, inherited handles, filesystem/registry/network denial, and failure receipts.

Task queue:
- Verify the compiled Win32 ctypes signatures, structure layouts and pointer widths against Windows SDK headers; compare both 64-bit Python builds and supported Win11 LTSC releases.
- Exercise create-suspended→job→token check→resume under privilege, access-denial, namespace, nested-job and low-memory faults.
- Instrument bounded IPC and failure behavior when a worker floods stdout, never closes pipe, spawns a descendant or calls a forbidden API.
- Verify no IPC handle, untrusted environment, source path or AppContainer private resource can be promoted to execution or admission authority.
- Decompose external attestation and custody requirements. Do not add Crete without independently measurable break-before-mutation implementation.
- Keep the source witness, change ledger, error log and four intent queues distinct.

Finished task queue: v0.2 static source witness; v0.3 separate JSON schema and graph microservers with ordinary glue; v0.4 Linux experimental enforcement; v0.5 source candidate Windows AppContainer+Job+bounded pipe launcher and opt-in negative probe. Windows OS runtime verification remains open.

Explicit sentinels: `SENTINEL_UNRESOLVED`; no JSON nulls. Refuse when the evidence is insufficient. Historical intent is evidence, not active permission. All claims of security must be tied to a concrete OS enforcement and probe witness.
