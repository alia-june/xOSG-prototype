# Verification and reproduction

## Historical evidence retained from v0.5

The source archive recorded **43 passing tests** on a Linux development host. The historical log is `WINDOWS_V0_5_TEST_LOG.txt`; its suite includes Linux regression, protocol, authority and static Windows contract tests. It is **not** Windows native runtime evidence. The 6 Windows contract tests were rerun after certain final source changes, while the 43-test combined run predated those adjustments; see `VALIDATION_REPORT.md`.

The v0.5 implementation includes a separate-code semantic validator. This is not a third-party attester and does not sign or transfer custody of evidence.

## Publication-preparation verification

See `docs/REPOSITORY_AUDIT.md` for checks run specifically against the public repository candidate. Do not confuse repository hygiene checks or limited CI tests with security proof or operational admission.

## Safe CI scope

The default GitHub Actions workflow runs only non-privileged protocol, source-parity, policy and Windows cross-platform contract tests. It does **not** attempt Windows profile creation, privileged Linux mount namespaces, security probes, nor arbitrary worker execution.

Full regression must be run separately in a deliberately configured, isolated test environment, with the host's OS/build, dependencies, permissions, exact command, exit code and scope recorded.

## Admission disposition

A test pass, JSON schema pass, source publication, repository tag, or signed release archive is **not** authority to deploy validated microservers. The runtime continues to emit `CANDIDATE_ONLY`, `NOT_ADMITTED` and `NOT_PUBLISHED`.

## Candidate preparation run (current package)

The public candidate passed **22 non-privileged contract tests** and **8 glue tests** on the preparation Linux host. A subsequent full discovery invocation did not complete within the command execution limit. Its incomplete log must not be interpreted as a successful full regression. These results do not validate Windows native containment.

## Publication-target preparation recheck (2026-11-07)

The renamed `xosg-prototype` candidate passed 22 nonprivileged contract/policy tests and 8 glue/composition tests on the preparation host. The first glue run stalled during its final test, but a subsequent complete 8-test rerun succeeded. No native Windows containment test was performed. These are limited candidate checks, not a new full-suite or security audit result.

## Publication-target preparation recheck (2026-11-07)

The renamed `xosg-prototype` candidate passed 22 nonprivileged contract/policy tests and 8 glue/composition tests on the preparation host. The first glue run stalled during its final test, but a subsequent complete 8-test rerun succeeded. No native Windows containment test was performed. These are limited candidate checks, not a new full-suite or security audit result.
