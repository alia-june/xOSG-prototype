# v0.5 validation report — Windows source candidate

## Scope

Linux host testing of preserved Linux implementation and cross-platform static/contract tests for the Windows implementation. **No actual Windows process token, AppContainer ACL, Windows Job Object or Win32 pipe behavior was executed** in this environment.

## Verified tests

- Original v0.4 suite: 36 test methods.
- New v0.5 Windows contract suite: 6 test methods.
- Combined suite reported 43 passing tests in 71.379 seconds. The additional count above 42 includes one test discovered in the historical test tree; no assumption is made about all 43 being security proofs.
- The Windows contract tests include fixed service names, no implicit provisioning, unknown-service refusal, refusal on non-Windows, fixed resource ceilings and candidate-only admission.
- See `WINDOWS_V0_5_TEST_LOG.txt` for the exact discoverable test identities and results.

## Unverified

- Win32 ctypes declaration layout and runtime call success on Windows 11 LTSC.
- AppContainer profile creation and read/execute ACL setup.
- Token identity, capability and job-membership evidence on the target host.
- Protected-file, network, registry and descendant-process denial on the target host.
- Full Windows end-to-end candidate pass or refusal trace.
- Independent host custody, external signed attestation and Crete enforcement.

Disposition: `CANDIDATE_ONLY / NOT_VERIFIED_ON_WINDOWS / NOT_ADMITTED / NOT_PUBLISHED`.

## Final source and control checks

- Source byte-parity: 8 critical v0.4 source, contract and witness files unchanged.
- AST parsing: all 29 Python files parse.
- JSON parsing: all 17 JSON files parse and contain no literal `null` values.
- No-approval provisioning: `python -m windows.profiles` exited 1 and printed refusal.
- No-approval probe: `python -m windows.smoke` exited 1 and printed refusal.
- Final Windows contract test re-run: 6 tests passed after the final source revisions.
- The 43-test consolidated run was recorded before the final local probe-path and Windows build-gate refinements; the 6 Windows contract tests were rerun after those refinements. These refinements did not change the historical Linux worker modules.
