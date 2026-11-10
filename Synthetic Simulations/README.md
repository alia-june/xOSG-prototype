# Synthetic Simulations

> **Public relocation — 2026-11-05:** this bounded documentation and the existing sanitized failed-experiment tree were migrated from private OpenSurface by explicit approval. The private control-plane implementation and quarantined candidate packages are not included. Earlier private-publication descriptions below and inside the retained source are historical; see the [migration record](../docs/xosg/MIGRATION.md). Failure classifications and test limitations are unchanged.

**Inspectable rehearsal for bounded AI control planes**

Synthetic Simulations is the xOSG laboratory for exploring how proposed AI
roles, deterministic expert rules, evidence gates, and human authority can
cooperate without quietly becoming an executing agent.

The current source basis is a Python 3.11+ **deterministic AI control-plane simulation**
named **Deterministic AI Control Plane v0.4**. It accepts a closed mission
contract, checks pinned local evidence, prepares a non-launching setup packet,
and emits a deterministic synthetic turn with an inspectable trace.

It does not call a model, launch a process, execute a workload, virtualize an
operating system, grant authority, or declare a task successful.

## Current State

| Property | State |
|---|---|
| Public project identity | Accepted under xOSG |
| Source basis | Deterministic AI Control Plane v0.4.0 |
| Implementation language | Python 3.11+ |
| Public source import | Not yet staged |
| Fresh source-suite result | 31/31 tests passed on 2026-10-31 |
| Memory-instrument candidates | Two private packages inspected |
| Atomized-package integrity | Blocked: 14/15 manifest hashes match |
| Defunct experiments | One sanitized failure record published |
| Model inference | None |
| Workload launch | Denied |
| Execution authority | None |
| Release authority | None |

The OpenSurface page documents an exercised private prototype. It is not yet a
source release. Promotion requires a separate dependency, license, packaging,
and public-interface review.

## Two Project Lanes

Synthetic Simulations currently has two evidence-backed lanes:

1. **Deterministic control-plane simulation** explores bounded roles, contracts,
   gates, traceability, and non-execution.
2. **LLM memory instrumentation simulation** explores portable, anonymized
   behavior and continuity packages as controlled inputs to model experiments.

Neither lane treats a prompt package, declared identity, model response, or
successful simulation as authority or real-world task completion.

## Defunct Experiments

Failed experiments are retained as bounded learning records, not as dormant
implementations. Raw packages, nested evidence bundles, and unlicensed source
remain outside the storefront.

Current record:

- [LLM Prompt Hardening Modular Kit Candidate 1.5](defunct-experiments/failure/llm-prompt-hardening-modular-kit-v1-5-candidate) - user-designated failed experiment with sanitized source originally admitted under MIT in private OpenSurface and now publicly relocated; archive integrity passed, but a fresh Windows run passed 42/43 tests and reproduced a POSIX-mode portability defect.

## Historical reference staging and defunct records

The following records are published as **documentation and cross-references**. No source ZIP in either new entry is hosted here, and neither is admitted to Synthetic Simulations:

| Historical item | Public record | Status | Source ZIP |
| --- | --- | --- | --- |
| Omnifact Reference v0.8.0 | [Staging record](research-staging/omnifact-ref-v0-8-0/README.md) · [sanitization report](research-staging/omnifact-ref-v0-8-0/SANITIZATION_REPORT.md) | Historical research reference; not admitted, **not** designated defunct | Sanitized archive prepared; **not uploaded** |
| MAGE Core 0.1.7-prealpha | [Defunct record](defunct-experiments/retired/mage-core-v0-1-7-prealpha/README.md) · [design record](defunct-experiments/retired/mage-core-v0-1-7-prealpha/DESIGN_RECORD.md) | Defunct / retired; not active | De-identified archive prepared; **not uploaded** |
| LLM Prompt Hardening Modular Kit 1.5 | [Failure and defunct record](defunct-experiments/failure/llm-prompt-hardening-modular-kit-v1-5-candidate/README.md) | Historical failed candidate | Existing sanitized source tree; original nested archive excluded |

The retained private file-by-file exclusion ledgers are not published. A staging record is not a public source release.

## Why Simulate

AI-system diagrams often collapse proposal, authority, execution, observation,
and acceptance into one box. Synthetic Simulations keeps them separate.

A simulation can answer bounded engineering questions:

- Did a closed contract parse without ambiguous or unknown fields?
- Did declared source bytes match caller-pinned hashes?
- Which profile and module references followed from declared effects?
- Which gates remain unresolved?
- Which role proposed, denied, observed, or rendered each step?
- Is the same input producing the same synthetic trace?
- Did termination or malformed state fail closed?

It cannot establish that a person holds authority, a model behaved correctly, a
sandbox contained a workload, or the underlying mission succeeded.

## Lane A: Deterministic Control-Plane

### System Shape

~~~mermaid
flowchart LR
    A[Closed mission contract] --> B[Deterministic validation]
    B --> C[Non-launching setup packet]
    C --> D[Synthetic orchestrator proposal]
    D --> E[Expert-system gate]
    E --> F[Inspectable hypervisor trace]
    F --> G[Synthetic response renderer]
    G --> H[One terminal result]
    E -->|deny| H
~~~

The system is a holarchy: bounded roles contribute to one terminal result while
retaining distinct authority ceilings.

| Role | Responsibility | Authority ceiling |
|---|---|---|
| Synthetic orchestrator LLM | Proposes routing and decomposition | Proposal only |
| Deterministic expert system | Applies simulation rules and blocks unsafe state | Simulation gate only |
| Inspectable hypervisor | Records hashes, rules, and decisions | Observation only |
| Synthetic response LLM | Renders a bounded placeholder response | Render only |

The word **hypervisor** names a trace role in this prototype. It does not claim
virtualization, isolation, privilege control, or a security boundary.

### Simulation Pipeline

#### 1. Contract intake

The prototype reads a closed JSON mission contract. Duplicate keys, unknown
fields, invalid effect declarations, oversized contracts, and ambiguous source
paths are rejected.

Declared identity or authority is recorded as a declaration. It is not upgraded
to authenticated permission merely because the contract is well formed.

#### 2. Evidence verification

Declared local inputs are confined beneath an explicit root and checked against
SHA-256 values. Missing files, unsafe paths, symlinks, changed bytes, and pin
drift fail closed.

The contract and the external kit configuration are pinned independently. A
mutable filename is never treated as a stable generation by itself.

#### 3. Deterministic planning

Declared task effects map to profile and module references through deterministic
rules. Dependency closure is visible in the result. Mapping completion proves
only that the declared inputs were processed; it does not prove that all effects
were declared or that a selected module is accepted authority.

#### 4. Non-launching setup

The setup phase keeps three domains separate:

- generated control instructions;
- declared task data;
- selected candidate-kit references.

Source or request text remains data. It is not promoted into control authority.
Every setup result preserves:

- **can_launch: false**
- **can_execute: false**
- **release_ready: false**

#### 5. Synthetic turn

A bounded request is registered by digest. The orchestrator proposes a route,
the expert system blocks task execution, the trace records rule decisions, and
the response role emits a fixed synthetic placeholder.

The response does not echo the request. Request and response SHA-256 values make
the trace reproducible without presenting the original request as an
instruction.

#### 6. Terminal result

The command-line interface emits one JSON result:

- **FINISHED** means the planning, setup, or simulation operation completed.
- **PROBLEM** means validation, integrity, termination, or bounded retry failed.

FINISHED never means the user's underlying task was executed or accepted.

## Lane B: LLM Memory Instrumentation

Two candidate configuration packages were supplied for Synthetic Simulations.
They are synthesized behavioral scaffolds, not raw memory dumps and not system
instructions.

| Candidate | Declared version | Archive SHA-256 | Intake state |
|---|---:|---|---|
| Anonymized LLM Memory Configuration Package | 1.0.0 | 3CC411DB83C68E33FC0C8201769EA217B99C45FC508A36A56D2E478DA7BDC15B | Structurally safe; no per-file digest ledger or license grant |
| Atomized Anonymized LLM Configuration Package | 2.0.0 | BC1087C3332E32EE7699AB2FB79BF99134260E32A56D0198ED2CFF612436D61C | Structurally safe; manifest integrity blocked |

The first package organizes an operating profile, behavioral protocol, project
context synthesis, canonical registry, anti-hallucination instrumentation,
response contracts, alias handling, redaction record, and combined upload
prompt.

The second package removes named workstreams and domain narratives in favor of
abstract operating atoms, intent patterns, whole-document assertions,
bidirectional application rules, redaction policy, evidence instrumentation,
and a safety boundary.

### Intake Findings

- Both ZIP files passed CRC and archive-path safety checks.
- No absolute paths, links, traversal names, case collisions, common credential
  forms, email addresses, or private machine paths were found by the bounded
  intake scan.
- Neither archive contains a license grant or SPDX declaration.
- The v1 manifest describes members but does not bind them with per-file
  digests.
- The v2 manifest binds 15 files, but only 14 match.
- For v2, the manifest expects
  **1e5540eeea3f52d3148ef4cb2a2d6b9db62b6915080ba8193690a7d364a939df**
  for the validation report; the archived bytes hash to
  **3795c4ace9df9b07a61eab310d1c217f7f83571eba77f5cb51a353b562a3f900**.
- The packages' anonymization claims remain self-asserted. A clean term scan is
  useful evidence, but it cannot prove that all identifying combinations or
  sensitive abstractions are absent.

The raw archives remain in private intake custody and are excluded from the
public storefront until ownership, licensing, integrity, and a deeper privacy
review are complete.

### Proposed Experiment Contract

When this lane becomes executable, each synthetic comparison should bind:

- package name, version, and exact digest;
- target model and interface version;
- system and safety-policy context;
- scenario and expected invariant set;
- permitted and prohibited observations;
- captured response and trace digests;
- claim ledger and source-support review;
- redaction and privacy review;
- outcome state: pass, fail, blocked, or inconclusive.

This is a proposed public experiment shape, not an implemented runner.

## Safety Invariants

The v0.4 prototype is organized around explicit denials:

1. No setup packet may launch or execute a workload.
2. No synthetic role may grant itself more authority.
3. Model-like roles remain proposal or rendering roles.
4. Expert rules may block but cannot authorize real execution.
5. Request text is data, not a replacement instruction stream.
6. Unknown contract fields, gates, and states fail closed.
7. Integrity failures are not retried as transient errors.
8. A transient read may retry once against the same pinned inputs.
9. Cooperative termination returns a terminal problem state when reporting
   remains possible.
10. Release remains false even when every synthetic step completes.

## Trust Vocabulary

| State | Meaning |
|---|---|
| VERIFIED | Direct deterministic observation, such as a matching digest |
| DECLARED | Present in supplied data but not independently authenticated |
| BLOCKED | Required evidence or implementation is absent |
| FAIL | Evidence is invalid or contradictory |
| NOT_APPLICABLE | A gate does not apply to the declared effect set |

Only a future, separately authorized mechanism may convert declared authority
into authenticated approval.

## Exercised Behavior

The private v0.4 source suite was rerun on 2026-10-31. All 31 tests passed.

Coverage includes:

- duplicate-key, unknown-field, oversize, and invalid-effect rejection;
- confined-path, missing-file, symlink, and SHA-256 mismatch rejection;
- deterministic effect union and dependency closure;
- constant non-execution and non-release planning results;
- contract and kit pin-drift detection;
- one bounded retry for transient reads;
- fail-closed repeated read failure and cooperative termination;
- separation of instructions, task data, and module references;
- four-role holarchy and expert-system control edges;
- deterministic request and response trace hashes;
- malicious-request non-echo;
- invalid setup, gate, and request rejection;
- exactly one terminal JSON line on exercised CLI paths.

The tests are evidence for those behaviors only. They do not establish real
model behavior, real hypervisor containment, authenticated approval, semantic
task correctness, race-free filesystem access, force-kill durability, complete
effect classification, or production safety.

## Before Real Integration

The project deliberately blocks real execution until separate proof exists for:

- authenticated, versioned expert-rule packages;
- model adapters with model and output provenance;
- independent effect classification;
- immutable exact-action intent and replay-resistant approval;
- real process, filesystem, network, and resource isolation;
- handle-based no-follow input opening;
- workload-specific semantic validators;
- append-only evidence and decision records;
- crash-safe supervision and durable terminal state;
- clean-room recovery and independent failure-domain testing;
- reviewed integration with any executor.

Connecting this prototype directly to a workload runner would violate its
current boundary.

## Relationship To xOSG

Synthetic Simulations instruments the decision structure around a proposed AI
system. It makes role boundaries, evidence states, rule decisions, digests, and
denials inspectable before real adapters or authority are introduced.

It complements:

- **Naked Shell**, the xOSG natural-language command-line universal shell;
- **Amorphous Durable AI Workspace**, the xOSG durable-workspace project.

No runtime integration among these projects is claimed yet.

## Source Lineage

Private source project:

    deterministic_ai_control_plane_v0_4

Version:

    0.4.0

Source package SHA-256:

    7BC0651F4432F55DE1A9877DCB800723D032DC5F865A616EA9EC51A7822B6DA0

Candidate memory-instrumentation archive SHA-256 values:

    3CC411DB83C68E33FC0C8201769EA217B99C45FC508A36A56D2E478DA7BDC15B
    BC1087C3332E32EE7699AB2FB79BF99134260E32A56D0198ED2CFF612436D61C

The private control-plane source and candidate instrumentation packages remain
under project custody while their public boundaries are reviewed. This README
is a generated public synthesis grounded in those sources, the fresh test
result, and the archive intake. It is not a claim that the source or candidates
have already been released.

## License

Future original Synthetic Simulations source published through OpenSurface
defaults to the repository MIT License unless an individual file records a
different SPDX license expression. Third-party or candidate dependencies retain
their own terms and must pass the publication gate before inclusion. The two
candidate memory-instrumentation archives currently contain no license grant
and therefore are not included in the public distribution.
