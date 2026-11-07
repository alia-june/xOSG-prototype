# Security boundaries and threat assumptions

## Non-goals and status

This release is a research candidate. It does **not** claim a secure sandbox for arbitrary hostile Python, read-denial isolation, network isolation on every host, arbitrary filesystem safety, hardened Crete enforcement, authenticated IPC, or secure deployment.

## Trusted components

The local orchestrator, authority-gate subprocess, external validator, runtime and configuration are trusted parts of the current design. They are not all mutually isolated, and the external validator has neither independent operational custody nor cryptographic attestations.

## Inputs and adversarial surfaces

- JSON manifest and envelopes: bounded and shape-checked in relevant entry points, but this is not a general hostile-content execution service.
- Worker responses: compared by identity fields, decisions and digests, but these are **not cryptographic sender authentication**. A compromised trusted broker invalidates the assumption.
- Python import path and dependencies: read/execute access is required. Underlying interpreter/dependency supply chains remain outside the current verification scope.
- Windows profiles and ACLs: provisioned separately, not automatically granted. An AppContainer may have writable private resources; a zero-capability list is not universal filesystem read/write denial.
- Linux namespaces: enforcement depends on host kernel configuration, namespace availability, mount setup and code paths. Negative tests show only observed operations.

## Fail-closed expectations

Refuse when supported OS boundaries cannot be established, worker identity conflicts, handles or response envelope violate the contract, a policy rejects an operation, a manifest fails schema or graph checks, or an audit claims admission/publication. Refusal must not trigger fallback to an unsandboxed worker or broadened ACLs.

## Evidence boundaries

| Claim | Evidence disposition |
| --- | --- |
| Historical 43-test v0.5 Linux run | Source-reported pass, historical log retained |
| Linux write/remount/network negative probes | Specific operations tested in historical Linux environment |
| Windows native AppContainer token/job membership | Not verified |
| Windows filesystem/loopback/child denial | Not verified |
| Full security confinement against malicious code | Not demonstrated |
| External signed attestation | Not implemented |

See `WINDOWS_IMPLEMENTATION.md`, `VALIDATION_REPORT.md` and `docs/VERIFICATION.md`. Each new platform-specific claim requires separately collected evidence.
