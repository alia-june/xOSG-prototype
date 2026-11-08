# sf-UUID Member Identity Contract v0.1 — Lock Decision

**Status:** LOCKED

**Decision date:** 2026-11-08

**Accepted artifact:** [sf-UUID Member Identity Contract v0.1](../contracts/SF_UUID_IDENTITY_CONTRACT_v0.1_LOCKED.md)

## Decision

Explicit project-owner direction recorded in the governing Codex chat accepts and locks the sf-UUID Member Identity Contract v0.1. The lock is limited to member sf-UUID identity. It supplements locked sf-AmorphDataDrive v0.3 and does not create sf-AmorphDataDrive v0.4.

## Proposal provenance

- The bounded proposal was introduced by [pull request #6](https://github.com/alia-june/xOSG-prototype/pull/6).
- The proposal was merged on 2026-11-05 at commit `3c95ae8989feb9d89549048039222886007e8c91` while retaining `PROPOSED` status.
- A later explicit lock-and-merge approval on 2026-11-08 authorized this acceptance record, the locked filename and status, and the related project-index updates.
- Chat direction and repository history record the decision; they do not provide cryptographic authentication of a person or a trusted timestamp.

## Accepted scope

The lock accepts the contract's member-identity rules, including:

- the 128-bit RFC 9562 UUIDv4 profile and canonical encodings;
- opaque logical-member identity, distinct from content, location, generation, drive identity, authority, or attestation;
- CSPRNG issuance and eight bounded generation-and-admission-check attempts;
- fail-closed collision and incompatible-claim handling;
- continuity rules for relocation, replicas, copies, forks, replacement, reconstruction, and generations;
- same-member promotion versus new-identity multi-member gestalt/gesple composition;
- the prohibition against assigning member identity to raw D0;
- optional and discouraged drive-level sf-UUID;
- deferral of a separate 64-bit identifier and prohibition against authoritative UUID truncation or folding;
- the requirement for an explicit external bitmap-position-to-member mapping.

## Decisions still open

This lock does not resolve:

1. physical and logical ID/data/metadata topology;
2. bitmap syntax, ordered occurrences, repetition, multiplicity, malformed references, or reconstruction grammar;
3. `x`/`y` width ownership, packing, padding, alignment, or exceptional values;
4. the complete touple-to-gestalt/gesple transition, dependency, invalidation, equivalence, or recursion contract;
5. generation numbering, lifecycle order, receipts, or reattestation;
6. verification, attestation, authorization, execution, or recovery mechanisms;
7. an optional drive-identity profile;
8. a future 64-bit identifier or UUID-to-64-bit mapping;
9. Etabit qualification, dependency, or cross-map.

## Proof boundary

This decision establishes project acceptance of the documented member-identity contract. It does not prove implementation correctness, physical-medium behavior, uniqueness in an unenumerated external domain, valid lineage, attestation, authority, recovery, security, Etabit compatibility, or production conformance. No parser, database, drive image, registry integration, runtime, release, or deployment is accepted or created by this lock.
