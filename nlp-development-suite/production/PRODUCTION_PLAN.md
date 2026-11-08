# NLP suite production-development plan

## Status

**Accepted internal-testbed plan. Production-ready: no. Publication and
deployment authority: none.**

This plan orders work so that implementation cannot silently outrun source,
canon, validation, or deployment authority. The machine-readable counterpart is
`production_plan.json`; `validate_plan.py` checks its sequence and dependencies.

## Ordered gates

| Gate | Transition | Current state | Required outcome |
|---|---|---|---|
| P00 | Identify | Verified | Inventory projects, sources, contracts, data, and authority |
| P01 | Freeze | Verified | Preserve and reproduce the supplied baseline |
| P02 | Describe | Verified | Record architecture, gaps, risks, failure states, and proof ceilings |
| P03 | Authorize | Verified | Accepted scope, canon, accountability, repository shape, runtime, and data boundaries |
| P04 | Stage | Verified | Reproducible local staging on canonical Python 3.11 with retained scope limits |
| P05 | Transfer | Verified | Admitted the traced, generic, non-executing interpreter slice |
| P06 | Verify | Verified | Structure, provenance, dependencies, artifact contents, and deferred distribution risks are recorded for internal testing |
| P07 | Validate | Verified | Bounded behavior, security, performance, compatibility, and recovery checks pass for the internal testbed |
| P08 | Commit | Verified | Immutable unpublished internal test candidate built and hash-verified |
| P09 | Attest | Not started | Obtain the user's exact-hash decision after mandatory evidence gates pass |
| P10 | Retain | Blocked | Deployment requires a new authorization and target |
| P11 | Retire | Blocked | Retirement requires new authorization and a completed deployment lifecycle |

No gate may begin merely because a later artifact template exists. Each gate
must satisfy its exit criteria and record evidence before the next gate changes
from `not_started`.

## P00 — Identify

Scope includes Lexicon Core, Lexicon Atlas, File Atlas, the Natural Language
front end, the standalone Scaffold Walker, advisory Aurora contracts, and the
shared registry metadata. The original export ZIP and its manifest are baseline
evidence. Generated files in `production/` are not part of that historical
snapshot and are not canon.

## P01 — Freeze

The original ZIP remains outside the extracted working directory. Its SHA-256,
member count, uncompressed size, manifest verification, and reproduced project
checks are recorded in `BASELINE_EVIDENCE.json`. `PACKAGE_MANIFEST.json` remains
unchanged and continues to verify only the historical export members.

## P02 — Describe

Before implementation, complete the system boundary, coverage, and risk review.
Every claim must identify whether it is source, accepted canon, derived,
inference, unknown, or generated synthesis. Static and structural validation do
not establish production behavior, security, performance, external acceptance,
or deployment readiness.

P02 exit criteria:

- all components and interfaces have named ownership or an explicit unknown;
- all external datasets and providers have availability and license evidence;
- every production concern is present in `COVERAGE_LEDGER.csv`;
- every blocking risk has a mitigation and gate;
- recovery prerequisites and irreversible operations are identified.

## P03 — Authorize

The user accepted Q-001 through Q-007 and the bounded production plan on
2026-10-02. The accepted scope is a local, offline, single-user downloadable
release with Python 3.11 as the canonical build runtime. Catalog v0.1 remains
advisory, unavailable sister schemas remain excluded, evidence gates remain
mandatory, and no deployment or receiving-system authority is granted.

P03 is verified by the versioned acceptance records in `DECISION_LOG.md` and
`PRODUCTION_PLAN_ACCEPTANCE_2026-10-02.md`.

## P04 — Stage

Create reproducible development and CI environments after P03. Pin direct
and transitive dependencies, define generated-versus-source data policy, add
secret scanning and dependency review, and reproduce the baseline from a clean
checkout. Staging must default to no external mutation.

Pre-stage evidence exists under `production/p04/`: CPython 3.11 through
3.14 on the current Windows host passed offline hash-locked installation, the
complete baseline, and two byte-identical successor builds. A local Git
monorepo and non-deploying CI workflow are staged, and CPython 3.14 reproduced
from a detached checkout. A later canonical Python 3.11 run from clean commit
`95d7061aab9403695e39f9052c221896419b6a21` passed the complete baseline and
produced two byte-identical wheels. P04 is verified for the bounded local
scope. No remote CI run or non-Windows host is claimed.

## P05 — Transfer

Implement one accepted vertical slice at a time. Each slice must include source
requirements, exact interfaces, negative behavior, visible collisions and
unresolved regions, tests, migration notes, and rollback. Proposal layers remain
separate from authority and execution.

The first slice is verified in `P05_COMPLETION_REPORT_2026-10-02.md`. Eight
accepted requirements trace to the generic core, dependency-free basic mode,
plan-only CLI, optional proposal adapters, and core/integration/fuzzy/torture
tests. P06 verification has begun.

## P06 — Verify

Verify schemas, source spans, hashes, manifests, dependency identities, build
reproducibility, licenses, generated artifacts, and configuration completeness.
Verification confirms form and traceability only within the check's scope.

The P06 structural evidence is recorded under `p06/` and summarized in
`P06_TESTBED_COMPLETION_REPORT_2026-10-02.md`. The canonical Python 3.11 wheel reproduces
the P04 hash, has no runtime dependencies, and contains neither lexical data nor
a license file. The user clarified that no publication is occurring, so the
missing distribution terms are deferred to a future publication gate rather
than blocking internal validation. This is not a legal-compliance conclusion.

## P07 — Validate

Run behavioral and semantic tests, cross-component integration, malformed and
adversarial inputs, filesystem confinement, security analysis, accessibility,
load and latency tests, failure injection, backup restoration, and rollback
rehearsal. Record failures before changing explanations or implementations.

The bounded internal-testbed profile is verified in
`P07_COMPLETION_REPORT_2026-10-03.md`. It combines the existing hardening,
fuzzy, torture, and control tests with a static capability scan, deterministic
performance and memory measurements, Python 3.11–3.14 basic CLI probes, and an
isolated corrupted-wheel restoration rehearsal. Its thresholds are generated
testbed criteria, not production service levels.

## P08 — Commit

Create a versioned immutable release candidate with a complete manifest,
changelog, migration instructions, known limitations, and rollback package.
Never overwrite the verified input archive or a prior release candidate.

P08 produced the unpublished internal candidate recorded in
`P08_COMPLETION_REPORT_2026-10-03.md`. Two constructions were byte-identical.
The exact archive SHA-256 is
`3281a1f1b3ca92afccda219165136cbb449ba0e0e10ab30c57ecd3ee2665323f`.
This is a test candidate, not a public release, and has not been accepted at
P09.

## P09 — Attest

Acceptance applies only to the exact candidate hash. The user records the
bounded release decision after mandatory evidence gates pass. Local tests do
not become independent attestation or receiving-system acceptance.

## P10 — Retain

P10 is blocked because deployment is outside the accepted scope. If separately
authorized later, deploy only through an authorized staged rollout. Define health thresholds,
automatic stop conditions, human rollback authority, evidence retention, backup
verification, and post-deployment monitoring before the first production change.

## P11 — Retire

P11 is blocked because retirement is outside the accepted scope. If separately
authorized later, retire old interfaces, data, or artifacts only after consumers migrate and
retention, audit, rollback, and support obligations are met. Retirement must be
separately authorized and recorded.

## Immediate next action

P09 is the next gate: record the user's disposition of the exact internal test
candidate hash without converting that decision into publication or deployment
authority. Before any future publication or external redistribution, select
package terms and reopen the distribution review.
