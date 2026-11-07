# xOSG Prototype — Governed Microserver Transmigration

**MIT-licensed research prototype · v0.5 source baseline · candidate-only validation**

**Intended public repository:** [`alia-june/xosg-prototype`](https://github.com/alia-june/xosg-prototype) (remote publication is not asserted).

A local, JSON-based reference system for reconstructing bounded capabilities as independent microserver processes and connecting them through explicitly declared *glue*. The repository does not purport to implement the complete xOSG architecture. The repository does not purport to implement the complete xOSG architecture. The current implementation is much narrower than the eventual architecture: it validates a proposed **microserver/glue manifest** using a schema gate, graph gate, authority preflight and a separate-code semantic audit.

> **Security and maturity notice:** This is experimental code, **not** a production sandbox, untrusted-code execution service, API gateway, automated code-transmigration engine, or deployment system. Windows AppContainer/Job Object support is a **source candidate that has not been executed or independently verified on Windows**. Static validation does not authorize deployment or prove security. Do not use this system to process hostile content or protect valuable data without your own assessment.

## What it does today

- Validates versioned JSON declarations of services, operations and glue connections.
- Rejects invalid schemas, references, incompatible interfaces and dependency cycles.
- Runs two local JSON-CLI workers: `schema-gate` and `graph-gate`.
- Propagates upstream refusal; checks payload digests across an **identity-only** glue edge.
- Performs read-only candidate policy checking and a separate-code semantic cross-check.
- Returns structured results marked `CANDIDATE_ONLY`, `NOT_ADMITTED`, `NOT_PUBLISHED`.
- Provides a Linux x86-64 *strict-mode reference* using namespaces and mount restrictions, plus a Windows 11 24H2/LTSC 2024+ **unverified** AppContainer/Job Object implementation.

It does **not** automatically decompose arbitrary source code, build new services from source, run general HTTP servers, authenticate IPC cryptographically, implement hardened Crete joins, sign independent attestations, admit workloads, or publish/deploy microservers.

## System at a glance

```text
manifest.json
    |
    v
local governed orchestrator
    |
    +--> authority preflight [candidate-only policy]
    |
    +--> schema-gate [bounded JSON-CLI worker]
    |        |
    |        v
    |    ordinary identity glue [digest and refusal checks]
    |        |
    +--> graph-gate  [bounded JSON-CLI worker]
    |
    +--> separate-code semantic audit
    |
    v
structured receipt: STATIC_PASSED | REFUSED
                    CANDIDATE_ONLY
                    NOT_ADMITTED / NOT_PUBLISHED
```

**Trust boundary:** The orchestrator, authority-gate subprocess, and auditor are not all independently OS-confined. Digest matching detects certain consistency failures but is **not authentication**. See [Architecture](docs/ARCHITECTURE.md), [Threat model](docs/SECURITY_BOUNDARIES.md), and [Verification](docs/VERIFICATION.md).

## Requirements

- Python **3.10+**, with the `jsonschema` dependency listed in [`requirements.txt`](requirements.txt).
- For the governed Linux path: **Linux x86-64**, `unshare`, required user/mount/network namespace support and permissions.
- For the governed Windows candidate: **Windows 11 24H2 / LTSC 2024 or later**, x64 Python, separately provisioned AppContainer profiles, carefully scoped read/execute ACLs, and host verification. **Not yet verified on Windows.**
- Other platforms fail closed for governed execution.

This repository is **not** a PyPI package and does not require a network connection at runtime after dependencies are installed.

## Quick start — inspect and test locally

Clone or extract the repository, open a terminal **in its root**, and install dependencies in an isolated virtual environment:

```bash
python -m venv .venv
# Linux:
. .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run **functional-only** composition (no OS sandbox; do **not** use hostile input):

```bash
python -m microtrans.glue examples/implementation_manifest_v0_3.json
```

Run limited, cross-platform contract tests without invoking OS-containment tests:

```bash
python -m unittest -v \
  tests.test_transmigration.ProtocolTests \
  tests.test_transmigration.SourceParityTests \
  tests.test_governed_v0_4.PolicyTests \
  tests.test_windows_v0_5.WindowsContractTests
```

On PowerShell, put the `python -m unittest ...` arguments on one line rather than using the Bash line-continuation characters.

### Governed execution — Linux test host only

The following requires kernel namespace permissions and should be evaluated in an isolated test machine, not an irreplaceable workstation:

```bash
python -m microtrans.governed examples/implementation_manifest_v0_3.json
```

If required Linux containment cannot be established, the governed path must refuse. An accepted manifest is **not** an admitted deployment.

### Windows candidate — explicitly opt-in, isolated test VM only

Do **not** run these on a production workstation as a way to establish trust. Windows native behavior has **not** been validated. Review [`WINDOWS_IMPLEMENTATION.md`](WINDOWS_IMPLEMENTATION.md) and [`docs/SECURITY_BOUNDARIES.md`](docs/SECURITY_BOUNDARIES.md) first.

```powershell
# Review exact AppContainer profiles and filesystem ACL requirements first.
py -3 -m windows.profiles --i-approve-profile-creation
# Then perform opt-in negative probes on disposable test resources.
py -3 -m windows.smoke --i-approve-local-probes
# Only if host evidence meets the documented boundary checks:
py -3 -m microtrans.governed examples\implementation_manifest_v0_3.json
```

Profile creation persists OS state. The code does **not** automatically adjust filesystem ACLs. Missing permissions must not lead to broadening access or running workers unsandboxed. See [Windows implementation](WINDOWS_IMPLEMENTATION.md).

## Status and evidence

| Area | Status |
| --- | --- |
| JSON protocol, two worker processes and ordinary glue | Implemented as a local reference |
| Schema/graph checks and candidate receipts | Tested historically on Linux |
| Linux namespace containment | Specific negative probes passed in recorded v0.4/v0.5 Linux environment; not a universal proof |
| Windows AppContainer and Job Objects | Source + cross-platform contract tests only; **no native Windows execution evidence** |
| Signed IPC, full Crete enforcement, automatic transmigration | Not implemented |
| Admission, deployment and publication by the runtime | Explicitly disabled |

The upstream v0.5 report records **43 historical tests passing on Linux**, including static/contract tests. Those are **not** claims of successful Windows isolation. See [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) and [`docs/VERIFICATION.md`](docs/VERIFICATION.md) for test scope and limitations.

## Repository layout

| Path | Role |
| --- | --- |
| [`microtrans/`](microtrans/) | JSON-CLI workers, protocol, glue, governed entry point |
| [`authority/`](authority/) | Static candidate-only authority preflight |
| [`external_validator/`](external_validator/) | Independent-code semantic cross-check (not independent custody) |
| [`runtime/`](runtime/) | Worker and OS boundary entry points |
| [`windows/`](windows/) | Experimental native Windows sandbox backend and opt-in probe |
| [`contracts/`](contracts/) | JSON Schema contracts |
| [`examples/`](examples/) | Candidate manifests and example receipts |
| [`tests/`](tests/) | Unit, parity and platform-specific boundary tests |
| [`source_witness/`](source_witness/) | Retained v0.2 checker and witness hashes |
| [`lineage/`](lineage/) | Historical, version-scoped documents and reports |
| [`docs/`](docs/) | Public architecture, verification, policies, release checklist |

## Contributing and disclosures

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before proposing changes, especially to authority gates and native launch code. Report potential vulnerabilities privately according to [`SECURITY.md`](SECURITY.md), not in public issues.

### Licensing

Released under the [MIT License](LICENSE). Copyright (c) 2026 Alia June.

**Rights review:** The repository preparation cannot itself establish provenance or redistribution rights for every retained historical source witness; the maintainer must verify ownership and third-party obligations before the first public push.

### Release readiness

This is a **repository publication candidate**, not an announced or deployed release. No remote repository has been created or updated as part of this package. The publication checklist is in [`docs/PUBLICATION_CHECKLIST.md`](docs/PUBLICATION_CHECKLIST.md); confirmed owner/license choices are in [`docs/PUBLICATION_DECISIONS.md`](docs/PUBLICATION_DECISIONS.md).
