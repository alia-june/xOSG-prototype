# P03 bounded authorization

## Status

**Bounded local release workflow accepted on 2026-10-02. P03 verified.
Production-ready: no. Deployment authority: none.**

This packet defines the smallest accepted local release workflow supported by
the current evidence without inventing receiving-system contracts or granting
execution or deployment authority.

## Accepted bounded first release

Release ID: `nlp-offline-interpreter/0.1`

The release would provide a local Python library and plan-only command-line
interface that converts bounded UTF-8 requests into deterministic structured
interpretation proposals. It would combine Lexicon Core's normalization,
intent, collision, routing, morphology, relations, and synthesis primitives
with the Natural Language front end's explicit alias grammar, local OEWN
candidate evidence, source hashes, spans, layer traces, and visible abstention.

The default and only release mode would be non-executing. Existing bounded
read-only file adapters remain source material and test fixtures, but invoking
them is outside this first release scope.

## Accepted decisions

| Decision | Proposal | State |
|---|---|---|
| Q-001 repository | One suite-level monorepo while retaining component directories and provenance | Accepted for bounded development and release preparation |
| Q-002 capability | Offline deterministic interpretation library and plan-only CLI | Accepted for bounded development |
| Q-003 catalog | Treat catalog v0.1 as advisory; a supplied receiving registry remains authoritative | Accepted boundary |
| Q-004 sister schemas | Exclude unavailable sister schemas until supplied, assessed, and separately accepted | Accepted boundary |
| Q-005 runtime | Python 3.11 canonical build; local offline single-user process; Windows first; no service claim | Accepted boundary |
| Q-006 data | Packaged OEWN 2025 only with verified license/attribution; no omitted corpora, telemetry, transmission, or automatic retention | Accepted boundary |
| Q-007 accountability | User is release-scope authority; evidence gates remain; external operations and receiver roles are not applicable | Accepted boundary |

## Included behavior

- deterministic normalization and explicit controlled parsing;
- exact source text and SHA-256 retention;
- visible aliases, collisions, unresolved regions, and layer traces;
- local OEWN candidate definitions and relations without sense selection;
- proposal-only task routing;
- JSON output with versioned schemas;
- clean-environment unit, contract, determinism, and offline tests.

## Explicit exclusions

- filesystem command execution, including existing read-only adapters;
- catalog writes, file movement, rule admission, or other mutation;
- network providers, web lookup, LLM calls, authentication, or remote service;
- Lexicon Atlas, File Atlas, Scaffold Walker, Electron, and desktop installer;
- external raw Wiktionary, GCIDE, CMUdict, IPA Dict, UniMorph, ODict, or
  StarDict redistribution;
- sister-machine schemas or receiving-system acceptance claims;
- production deployment, uptime, security, performance, or scale claims.

## Evidence from the current code

For `find files named report in .`:

- Lexicon Core produces a `file-explorer` search proposal with
  `execute: false` and status `proposal-only`.
- The Natural Language front end produces `find_files` with the same essential
  operands, exact source hash, alias rule evidence, and `read_only` side-effect
  classification.
- No direct import or adapter currently connects the front end to Lexicon Core.

This demonstrates a feasible integration seam, not an integrated release.
`validate_first_slice.py` reproduces the observation without executing a file
operation.

## Acceptance criteria for the bounded release

1. A clean Python 3.11+ environment installs from reviewed locked dependencies.
2. One versioned public API and one plan-only CLI use Lexicon Core rather than a
   duplicated hidden ontology.
3. The CLI has no execution mode in this release.
4. Repeated identical inputs and configuration produce byte-stable JSON except
   for explicitly excluded runtime metadata.
5. Empty, oversized, multiline, unsupported, ambiguous, and conflicting inputs
   return typed non-success or review states.
6. WordNet access is local, pinned, optional, and never selects a sense.
7. Alias -> WordNet -> session history -> optional provider ordering is retained;
   provider layers are disabled in this offline release.
8. Unit, contract, schema, determinism, offline, malformed-input, and packaging
   tests pass from a clean checkout.
9. The artifact includes manifests, licenses, limitations, rollback instructions,
   and no machine-local paths, credentials, caches, or unapproved corpora.
10. Approval applies to an exact release-candidate hash and does not imply a
    catalog or sister-machine acceptance not separately recorded.

## Authorization outcome

The user accepted bounded development on 2026-10-01, accepted Q-001 through
Q-007 on 2026-10-02, and then accepted the production plan for P00 through P09
of the local downloadable release. P03 is verified and P04 is in progress.
P10 deployment and P11 retirement remain blocked pending new authorization.
Exact-candidate acceptance remains a future P09 decision and production-ready
remains false.
