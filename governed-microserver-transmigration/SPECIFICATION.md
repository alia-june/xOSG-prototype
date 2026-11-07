# Work Process — Governed Microserver Transmigration v0.4.0

## 1. Intent and governing status

- **Goal:** reconstruct validated capabilities into narrow API microservers and separately testable composition glue.
- **Current task:** enforce a limited independent policy and measurable OS process boundary around the v0.3 schema/graph microservers, then audit their composition by separate code.
- **Task queue:** bounded IPC; Windows native security boundary; authenticated handoffs; independently signed attestation; Crete break-before-mutation; human/independent admission authority.
- **Finished task queue:** v0.2 checker preservation; two v0.3 microservers plus ordinary glue; v0.4 Linux kernel restrictions and independent candidate audit.

History is evidence rather than authority. Identity is not intent. No machine-readable unknown value is `null`.

## 2. Data and control path

```text
explicit local candidate manifest
    |
    v
v0.4 trusted orchestrator
    |
    +--> separate authority gate: policy + digest + scope
    |    DENY stops before worker execution
    |
    +--> user/mount/network namespaces; readonly mounts; capability drop
    |    |
    |    +--> v0.3 schema-gate microserver
    |    |       refusal stops downstream graph dispatch
    |    +--> v0.3 graph-gate microserver
    |            no authority transfer across ordinary glue
    |
    +--> separate semantic validator
    |    compare independent graph result with v0.3 receipt
    |    reject impossible acceptance or claimed elevation
    |
    v
STATIC_PASSED | REFUSED
CANDIDATE_ONLY / NOT_ADMITTED / NOT_PUBLISHED
```

The existing v0.3 protocol remains **0.3.0** between workers and glue. The governed authority and independent audit protocol is **0.4.0**. Version separation is deliberate; v0.3 output is not silently promoted to v0.4 authority.

## 3. Authority semantics

Policy gate grants no filesystem, network, execution, or publication permission. It evaluates whether a declared operation falls within the **read-only candidate validation** policy and checks a matching payload digest. It cannot authenticate the invoker, and the gate is only an effective control when the trusted launcher exclusively uses it.

The launcher allowlists `schema-gate` and `graph-gate`. Arbitrary command names, user-provided executable paths, dynamic plugins and operations are not supported. The launcher checks gate output before creating a worker. The child modules separately revalidate their request envelope. No stage may admit, publish, or raise authority. A forged positive external audit with admission/publication elevated is rejected.

This remains **local application policy**, not a cryptographically authenticated capability system. SHA-256 binds data for accidental or adversarial mismatch detection in this topology; it does not provide service authentication against a local attacker able to rewrite the process code or messages.

## 4. Linux boundary

1. A new **user namespace** and **network namespace** are requested with `unshare` before the bootstrap Python interpreter starts.
2. A new **private mount namespace** is requested, with mount propagation set private.
3. The trusted bootstrap inspects `/proc/self/mountinfo`, remounts each existing writable mountpoint read-only using `mount -o remount,bind,ro`, and verifies none still reports writable. Any failure is fatal.
4. Before loading worker code, the bootstrap uses `setpriv` to clear inherited, permitted, effective, ambient and bounding capabilities, set `no_new_privs`, and execute `runtime.worker_entry`.
5. The worker independently verifies zero capability sets, `NoNewPrivs: 1`, and no writable mountpoints. Any failure refuses execution.
6. Worker input is JSON on stdin; output is JSON on stdout. No external API server listens on a network port.

**Observed probe:** the boundary denied overwriting a retained test file, denied creating a file in `/dev/shm`, rejected remounting the root as writable, and exposed a distinct network namespace ID. This verifies these specific operations under this Linux runtime. It is not proof of protection against every filesystem or kernel action, process-to-process IPC, untrusted native code, or all mount namespaces on all distributions. In particular, the original read permissions remain; the OS policy does not enforce read minimization.

No kernel/minifilter component and no GPU/voxel execution is involved. The native Windows design should use a separately verified least-privilege process token/AppContainer alongside Job Object resource policy; Job Objects alone are not a confidentiality/write isolation mechanism.

## 5. External validator and independence boundary

`external_validator/validator.py` is an independent implementation of graph traversal (iterative DFS instead of the candidate Kahn walk). It does not import candidate microserver or glue code. It **does** reuse the same v0.2 declarative manifest schema and runs on the same host, in the same code package and user account. Consequently the result is independent-code **corroboration**, not independent host custody, independent policy management, signed attestation, or full source-to-target equivalence.

For accepted candidates, the audit demands: matching request ID and SHA-256, valid schema and graph, complete ordered transcript, no recorded faults, and no admission or publication. An invalid candidate may produce an audited refusal; it cannot produce an audited static pass. A failure to start or communicate with the external validator refuses the entire governed chain.

## 6. Failure and recovery

- Authority gate refusal or corruption: **no worker dispatch**.
- Unsupported operating system or namespace setup: **no worker dispatch**.
- Mount remount, capability drop or kernel verification failure: **worker exits without loading gate code**.
- Worker timeout, malformed JSON, unexpected reply, schema/graph refusal: **no candidate pass**.
- External audit mismatch or outage: **no candidate pass**.
- All failures retain `CANDIDATE_ONLY / NOT_ADMITTED / NOT_PUBLISHED`; no automatic repair or privilege escalation.

## 7. Unresolved engineering issues

1. Limit stdout memory during untrusted child execution (the reference currently checks captured response size after subprocess collection).
2. Stronger OS sandbox semantics for filesystem **reads**, IPC, device access and native-code loading; test escape resistance.
3. Windows 11 LTSC process isolation with restricted token/AppContainer, separately constrained data access, and Job Object limits; verify before claiming equivalence.
4. Integrity-protected policy custody, mutually authenticated one-time IPC messages, replay prevention and signed receipts.
5. A truly external attester and authority that is maintained outside candidate source ownership.
6. Structural and behavioral testing for Crete break-before-mutation, without conflating declaration with enforcement.
7. Formal transition matrix and safe publication controls; default deny, no autonomous admission.

## 8. Disposition

Implemented: **candidate v0.4 authority preflight, strict Linux execution path, independent-code audit and negative tests**. Not implemented: **portable security sandbox, production API, signed authority, Crete enforcement, admission, publication**.
