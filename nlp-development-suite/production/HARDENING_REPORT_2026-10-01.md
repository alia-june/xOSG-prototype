# Generic successor hardening report

Status: development hardening and the final ordered baseline passed.
Authority effect: `NONE`. Production-ready: no.

## Work completed

- Engine pass 1: nested inputs are detached and immutable; numeric Boolean
  impostors, oversized identifiers, excessive layers, provider candidates,
  unresolved regions, evidence, diagnostics, JSON depth, JSON items, and JSON
  strings are bounded.
- Rig pass: the runner distinguishes timeouts from ordinary failures, bounds
  captured output, records the exact interpreter, validates the pinned schema
  dependency, confines receipts to `production/reports`, and refuses overwrite.
- Engine pass 2: direct results, candidates, spans, unresolved regions, traces,
  source hashes, source lengths, statuses, provider identities, finite
  collections, candidate uniqueness, and trace counts are checked.
- Fuzzy pass: deterministic seed `20261001` covers 5,000 hostile generic texts,
  1,000 mutable metadata cases, 1,000 hostile real-adapter texts, 600 malformed
  provider cases, and 25 loose language variants.
- Torture pass: source, depth, item, layer, and candidate boundaries; 50,000
  repeated calls; and 5,000 calls across eight worker threads.
- Packaging pass: an initial two-build comparison exposed timestamp-only wheel
  drift. With `SOURCE_DATE_EPOCH=1704067200`, two isolated wheels were
  byte-identical and the exact hashed artifact passed a clean installation
  probe.
- Optional-integration pass: the dependency-free wheel now imports its
  integration-status module without suite sources, names the three missing
  modules, retains `execution_allowed: false`, and returns documented exit code
  4 rather than producing an import traceback.
- Entry-point pass: both `python -m nlp_offline_interpreter` and the installed
  `nlp-offline-interpreter` console script return the same structured bounded
  status when optional adapters are absent.

## Current receipts

- `reports/hardening-2026-10-01-pass1.json`: first separated hardening run.
- `reports/hardening-2026-10-01-torture.json`: expanded fuzzy and torture run.
- `reports/baseline-2026-10-01-hardened.json`: final 15-stage baseline; all
  stages passed.
- `reports/hardening-2026-10-01-packaging.json`: lazy optional-integration
  hardening suite; all six stages passed.
- `reports/baseline-2026-10-01-optional-integration.json`: post-packaging
  15-stage baseline; all stages passed.
- `reports/baseline-2026-10-01-entrypoints.json`: final console-entry-point
  15-stage baseline; all stages passed.

## Final measured result

- 21 successor core tests passed.
- 9 successor integration tests passed.
- 5 deterministic fuzzy test groups passed across 7,625 generated or varied
  cases.
- 4 torture groups passed including 55,000 repeated or concurrent calls.
- 26 production-control and test-rig tests passed.
- 22 historical Lexicon Core and 54 Natural Language tests passed.
- The 1,440,449-term Lexicon Atlas and File Atlas 12 checks across 37 rules
  passed.
- The historical 1,306-member manifest and the hardened 15-member successor
  manifest passed.
- A static source scan found no execution, subprocess, socket, HTTP-client, or
  destructive filesystem interface in the successor source package.

## Diagnostic redux

`ERROR_LOG.md` retains the test-depth fixture error, the failed relative-path
package probe, and the non-reproducible default wheel timestamps. Each issue was
reduced before correction and has a stated regression guard.

## Remaining proof limits

These checks are local development evidence. They do not prove external
security, arbitrary third-party provider isolation, subprocess-descendant
termination, cross-platform behavior, service performance, receiving-system
acceptance, or production readiness. P03 remains blocked.
