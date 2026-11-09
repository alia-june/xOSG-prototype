# Q-005 runtime and operating-model acceptance

## Source

On 2026-10-02, the user explicitly accepted the proposed Q-005 decision after
its runtime, host, user, and availability limits were stated.

## Accepted canon

The first release is a local, offline, single-user Python process. Python 3.11
is the canonical release-build runtime. Python 3.11 and newer may be supported
only where the applicable test matrix passes. Windows is the first validated
host family.

The release makes no server, multi-user, network-service, uptime, scaling, or
availability claim. Other operating systems remain unclaimed until separately
validated.

## Scope

- release artifact construction and reproducibility;
- supported Python runtime claims;
- initial host and user model;
- explicit service and availability exclusions.

## Locked terms

- `Python 3.11 canonical release-build runtime`;
- `local offline single-user process`;
- `Windows validated first`;
- `newer Python support requires passing tests`;
- `no service or availability claim`.

## Evidence and limits

The clean-checkout matrix passed on Python 3.11 through 3.14, but the wheel
built under Python 3.14 did not have the same bytes as the wheels built under
Python 3.11 through 3.13. Selecting Python 3.11 fixes the canonical build
environment; it does not establish cross-runtime byte identity.

## Not established by this acceptance

- server, daemon, hosted API, or network-service behavior;
- multi-user isolation, authentication, concurrency, or tenancy;
- an uptime, support, latency, throughput, or scaling commitment;
- support for an operating system that has not been separately validated;
- production deployment or operational readiness.

## Version and migration

- Decision version: `Q-005/1`.
- Superseded values: none; the prior state was `UNKNOWN` with a generated,
  unaccepted runtime proposal.
- Migration: construct canonical release artifacts using Python 3.11 and test
  newer runtimes without treating their output as the canonical artifact.
- Unresolved conflict: additional operating-system targets and any future
  service-level requirements remain unspecified.
