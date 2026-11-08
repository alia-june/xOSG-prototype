# sf-Edabit / sf-AmorphDataDrive

**Status:** locked baseline v0.3 with locked sf-UUID member identity contract v0.1 and open successor direction  
**Environment:** non-production research  
**Integration:** separate from Etabit; candidate substrate relationship only

sf-AmorphDataDrive is a strict raw-substrate architecture:

    D0 = existence
    D1 = relation / interpretation
    D2 = composition / coherence

D0 contains raw, flat, ordered, enumerated values. Identity, metadata, datatype, encoding, attestation, reconstruction information, filesystem structures, partitions, and composition structures remain outside D0.

## Current direction

- Member sf-UUID identity is governed by the locked [sf-UUID member identity contract v0.1](contracts/SF_UUID_IDENTITY_CONTRACT_v0.1_LOCKED.md), covering format, issuance, scope, duplicate/collision handling, continuity, and copy/replacement matching.
- A separate 64-bit identifier is deferred as a possible later addition.
- Drive-level sf-UUID is optional and discouraged.
- A touple can become a gestalt or gesple containing identity, y-bit value information represented in x bits, datatype, and data.
- ID, data, and metadata drives participate in a recursive build with bitmap-to-ID and gestalt integration.
- The relationship between those drive roles and D0/D1/D2 is unresolved.
- Bitmap ordering, repetition, multiplicity, bounds, and x/y packing remain unresolved.

These statements are current direction, not a new specification lock or completed implementation.

## Project map

- [Locked baseline v0.3](specifications/sf_edabit_amorph_data_drive_locked_spec_v0_3.md)
- [Historical locked baseline v0.2](specifications/sf_edabit_amorph_data_drive_locked_spec_v0_2.md)
- [Current direction](docs/CURRENT_DIRECTION.md)
- [Open decisions](docs/OPEN_DECISIONS.md)
- [Locked sf-UUID member identity contract v0.1](contracts/SF_UUID_IDENTITY_CONTRACT_v0.1_LOCKED.md)
- [sf-UUID v0.1 lock decision](decisions/SF_UUID_IDENTITY_CONTRACT_v0.1_LOCK_2026-11-08.md)
- [Relation to Etabit](docs/ETABIT_RELATION.md)
- [Source and proof boundary](docs/SOURCE_BOUNDARY.md)
- [Coherence summary](evidence/COHERENCE_SUMMARY.md)
- [Reconciliation summary](evidence/RECONCILIATION_SUMMARY.md)
- [Public handoff](handoff/HANDOFF_PUBLIC_2026-11-04.md)
- [Export validation](EXPORT_VALIDATION.md)
- [Export manifest](EXPORT_MANIFEST.json)

## Boundaries

The locked member-identity contract does not claim a formatted disk, on-media sf-UUID placement, bitmap grammar, gestalt/gesple runtime, Etabit implementation, Experience Orchestration Drive, Cypher Disk, deployed service, physical medium, optical isolation, recovery proof, or production conformance.

The sf-Registry working candidate is deliberately excluded. It is a separate operation/preservation registry candidate, not this storage architecture. Read locked v0.3 before proposing changes, and apply the production gate to each new scope.
