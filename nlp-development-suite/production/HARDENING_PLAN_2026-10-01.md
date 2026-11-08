# Generic successor hardening plan

Status: generated and executed for the accepted development scope only.
Authority effect: `NONE`. Production-ready: no.

## Ordered rounds

1. Harden the generic engine: immutable detached inputs, strict public
   invariants, bounded cardinality and text, safe Unicode, and contained
   provider failures.
2. Test the test rig: exercise timeout, missing executable, output truncation,
   environment injection, dependency preflight, report confinement, and
   overwrite refusal.
3. Harden the rig: add a pinned environment preflight, explicit timeout state,
   bounded output receipts, safe report paths, and an ordered hardening suite.
4. Harden the engine again: validate directly constructed results and traces,
   freeze provider identities, require finite collections, and verify trace-to-
   candidate consistency.
5. Run deterministic loose and fuzzy tests: natural-language variation,
   hostile Unicode, mutable JSON inputs, malformed providers, and real adapter
   paths.
6. Run bounded torture tests: maximum sizes and cardinalities, adjacent
   accepted/rejected boundaries, 50,000 repeated calls, and 5,000 concurrent
   calls.

Each round must retain `execution_allowed: false`, record any failure before
repair, and rerun the complete ordered baseline after source-manifest renewal.

## Acceptance conditions

- all new regression, fuzzy, torture, and rig tests pass;
- the historical 1,306-member manifest still passes unchanged;
- the successor manifest exactly describes the hardened source set;
- a clean wheel build and isolated installation reproduce the generic core;
- failures and limitations remain visible;
- no result is described as deployment, receiving-system, security, or
  production acceptance.
