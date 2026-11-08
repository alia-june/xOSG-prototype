# P07 internal-testbed validation completion

## Status

**P07: verified for the unpublished internal testbed. Production-ready: no.
Publication and deployment authority: none.**

## Results

The corrected P07 receipt is
`reports/p07-validation-2026-10-03-r2.json`.
The final canonical Python 3.11 control receipt is
`reports/p07-control-2026-10-03-py311.json`; all 14 ordered checks and 83
constituent core, integration, fuzzy, torture, and production-control tests
passed.

- Static security: all five standalone package modules passed the forbidden
  network, process, dynamic-code, and direct file-open scan.
- Determinism: 1,000 identical calls produced byte-identical canonical JSON.
- Typical performance: 5,000 calls completed in 0.713901 seconds on this host,
  below the generated 5-second testbed threshold.
- Bounded maximum-input performance: 50 calls completed in 0.092611 seconds.
- Tracked peak memory during 500 typical calls was 3,665 bytes under
  `tracemalloc`, below the 32 MiB testbed threshold.
- Maximum canonical output was 18,345 bytes, below the 256 KiB threshold.
- Authority boundary: the above-token-limit fixture returned `partial`, retained
  an unresolved region, and preserved `authority_effect: NONE` and
  `execution_allowed: false`.
- Compatibility: the dependency-free basic CLI passed on installed Windows
  CPython 3.11, 3.12, 3.13, and 3.14 runtimes.
- Recovery: corruption of an isolated wheel copy was detected and the exact
  P06 SHA-256 was restored from a verified backup in 0.028242 seconds. The
  package has no persistent runtime state, so no data-loss window applies.

## Diagnostic redux

The first report, `reports/p07-validation-2026-10-03.json`, is retained as a
failed test-harness receipt. Its fixture crossed the source-length limit rather
than only the token-retention limit. `ERROR_LOG.md` records the discriminator,
correction, and regression guard.

## Retained limits

- Measurements are host-specific internal-testbed evidence, not service-level
  objectives or independent security certification.
- No graphical interface is in the accepted product scope; accessibility is
  bounded to machine-readable deterministic CLI output and clear failure
  states.
- Executable third-party providers remain excluded because they are not process
  or memory isolated. Declarative optional data packs remain the preferred
  modularization boundary.
- No publication, external redistribution, network service, deployment, or
  production-readiness claim is made.
