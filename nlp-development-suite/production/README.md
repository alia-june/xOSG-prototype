# Production controls

## Purpose

This directory converts a verified development snapshot into an inspectable,
ordered production-development process. It does not declare the software
production-ready. The controls separate source evidence, generated planning,
accepted decisions, implementation, validation, and deployment authority.

## Control files

| File | Role |
|---|---|
| `production_plan.json` | Machine-readable ordered gates and dependencies |
| `PRODUCTION_PLAN.md` | Human-readable plan, exit criteria, and current state |
| `BASELINE_EVIDENCE.json` | Reproduced intake and validation evidence |
| `SOURCE_INVENTORY.csv` | Source, authority, accessibility, integrity, relevance |
| `COVERAGE_LEDGER.csv` | Requested production concerns and their current coverage |
| `RISK_REGISTER.csv` | Known risks, mitigations, owners, and blocking gates |
| `DECISION_LOG.md` | Decisions, unresolved choices, and canon boundaries |
| `ERROR_LOG.md` | Preserved failures, discriminators, repairs, and regression guards |
| `HARDENING_PLAN_2026-10-01.md` | Ordered development hardening rounds and acceptance conditions |
| `HARDENING_REPORT_2026-10-01.md` | Hardening, fuzz, torture, and proof-limit summary |
| `BASIC_ARTIFACT_SCOPE_2026-10-01.md` | User-directed no-approver boundary for the local basic download |
| `P04_STAGE_REPORT_2026-10-02.md` | Local repository, clean-checkout, runtime-matrix, and CI staging evidence |
| `P04_COMPLETION_REPORT_2026-10-02.md` | Canonical Python 3.11 P04 completion and retained limits |
| `P05_COMPLETION_REPORT_2026-10-02.md` | Traced bounded implementation admission and retained limits |
| `p05/` | P05 requirements trace, review, migration, and rollback evidence |
| `P06_BLOCKER_REPORT_2026-10-02.md` | Historical distribution-gate record retained for provenance |
| `P06_TESTBED_COMPLETION_REPORT_2026-10-02.md` | P06 completion within the no-publication testbed boundary |
| `P07_COMPLETION_REPORT_2026-10-03.md` | Bounded internal security, behavior, performance, compatibility, and recovery evidence |
| `P08_COMPLETION_REPORT_2026-10-03.md` | Exact immutable unpublished internal test candidate evidence |
| `TESTBED_SCOPE_ACCEPTANCE_2026-10-02.md` | User clarification that current artifacts are internal test evidence, not publication |
| `p06/` | Dependency, provenance, artifact, bundled-license, and verification-wheel evidence |
| `p07/` | Internal-testbed validation profile, threat model, and validation runner |
| `p08/` | Deterministic candidate builder, verifier, receipt, changelog, limitations, and rollback material |
| `p04/` | Hash-locked offline staging controls, repository policy, and CI contract |
| `P03_AUTHORIZATION_PACKET.md` | Accepted bounded local release authorization and exclusions |
| `p03_authorization.json` | Machine-readable P03 decisions and authority boundary |
| `PRODUCTION_PLAN_ACCEPTANCE_2026-10-02.md` | User acceptance of the bounded P00–P09 workflow |
| `SYSTEM_BOUNDARIES.md` | Component, authority, data, and execution boundaries |
| `CHANGE_CONTROL.md` | Change admission and evidence rules |
| `ROLLBACK_RUNBOOK.md` | Recovery prerequisites and rollback procedure |
| `ACCEPTANCE_CHECKLIST.md` | Final acceptance and deployment checklist |
| `validate_plan.py` | Static validation for order, dependencies, and controls |
| `validate_authorization.py` | Enforces accepted P03 scope and deployment exclusions |
| `validate_p05_slice.py` | Enforces P05 traceability, package identity, and non-execution boundaries |
| `validate_p06_evidence.py` | Verifies the P06 evidence set and preserves the package-license blocker |
| `validate_first_slice.py` | Non-executing feasibility smoke test for the proposed slice |
| `validate_test_environment.py` | Pinned test-dependency and test-directory preflight |
| `run_checks.py` | Ordered, non-deploying baseline validation runner |
| `tests/test_production_control.py` | Regression tests for the control layer |
| `tests/test_test_rig_hardening.py` | Timeout, output, environment, and receipt safety tests |

## Truth-state policy

Statements use the states `SOURCE`, `ACCEPTED_CANON`, `VERIFIED_EXTERNAL`,
`DERIVED`, `INFERENCE`, `UNKNOWN`, and `GENERATED_SYNTHESIS`. Generated plans
remain generated until an authorized reviewer accepts a decision. A passing
test establishes only the behavior covered by that test.

## Commands

From the package root:

```powershell
python .\production\validate_plan.py
python .\production\validate_authorization.py
python .\production\validate_first_slice.py
python .\production\validate_p05_slice.py
python .\production\validate_p06_evidence.py
python .\production\p07\RUN_P07_VALIDATION.py
python .\production\p08\VERIFY_P08_CANDIDATE.py
python -m unittest discover -s .\production\tests -v
python .\production\run_checks.py --list
python .\production\run_checks.py --suite hardening
python .\production\run_checks.py --suite baseline
```

`run_checks.py` does not deploy, mutate catalog state, admit rules, move user
files, or overwrite reports. Use `--report production/reports/NAME.json` to
write a new JSON receipt; paths outside that directory and existing targets are
rejected.

## Current boundary

Gates P00 through P03 are verified. On 2026-10-02, the user accepted Q-001
through Q-007 and the bounded local release plan. P04 and P05 are verified for
local reproducible staging and the bounded non-executing implementation. P06
artifact, provenance, dependency, and license-risk evidence passes for the
internal testbed. P06 and P07 are verified; distribution terms remain mandatory
before publication but do not block internal validation. P08 is verified as an
unpublished internal test candidate; P09 remains not started. P10 deployment
and P11 retirement are blocked until separately
authorized. The suite is not production-ready and is not being published.
