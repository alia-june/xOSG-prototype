# Q-004 sister-schema authority acceptance

## Source

On 2026-10-02, the user explicitly accepted the proposed Q-004 decision after
its scope and evidence limits were stated.

## Accepted canon

No absent or externally referenced sister schema is canonical for this
release. Parse-tree, logic, transition, acceptance, and authority schemas that
have not been supplied and explicitly accepted are excluded from the release
contract. Their absence is an unknown, not evidence that they do not exist.

The interpreter may use its own versioned internal output schema, but it must
not claim compatibility with an unavailable sister system.

## Scope

- the `nlp-offline-interpreter/0.1` development and release contract;
- external parse-tree, logic, transition, acceptance, and authority schemas;
- internal output schemas that remain explicitly versioned and bounded to the
  interpreter.

## Locked terms

- `unavailable sister schemas are excluded`;
- `absence remains UNKNOWN`;
- `no unsupported compatibility claim`;
- `later integration requires separate acceptance`.

## Not established by this acceptance

- that the named sister schemas do not exist;
- canonical definitions for any sister schema;
- compatibility with, conformance to, or acceptance by a sister system;
- authority to silently translate or reconcile future schema conflicts;
- production readiness or deployment authority.

## Version and migration

- Decision version: `Q-004/1`.
- Superseded values: none; the prior state was `UNKNOWN` with a generated,
  unaccepted exclusion proposal.
- Migration: when a sister schema is supplied, inventory and compare it,
  record conflicts, define a reversible migration, validate it, and obtain a
  separate explicit acceptance before integration.
- Unresolved conflict: canonical sister schemas have not been supplied.
