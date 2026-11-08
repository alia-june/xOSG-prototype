# Current direction

Date transcribed for public export: 2026-11-04  
Status: working direction; not a new specification lock.

Lock update: 2026-11-08. The [sf-UUID member identity contract v0.1](../contracts/SF_UUID_IDENTITY_CONTRACT_v0.1_LOCKED.md) is accepted and locked for member identity. The [lock decision](../decisions/SF_UUID_IDENTITY_CONTRACT_v0.1_LOCK_2026-11-08.md) records its scope and residual boundaries. This is a supplement to locked v0.3, not v0.4.

## Baseline

Locked v0.3 remains the current supplied baseline. Locked v0.2 remains historical. No v0.4 exists.

The baseline separates D0 raw existence, D1 relation/interpretation, and D2 composition/coherence. New work must not place identity, metadata, datatype, encoding, attestation, reconstruction, filesystem, partition, or composition structures on raw D0.

## Identity and integration

| Topic | Current direction | Open boundary |
| --- | --- | --- |
| Member identifier | Locked v0.1 defines a 128-bit RFC 9562 UUIDv4 profile and member-identity continuity rules. | Physical topology, bitmap grammar, attestation, authority, optional drive identity, and any future 64-bit mapping remain separate. |
| Separate 64-bit identifier | Possible later addition. | Not a mandatory current second key; no current mapping requirement. |
| Drive sf-UUID | Optional and discouraged. | Matching must not require universal drive UUIDs. |
| Touple / gestalt / gesple | May carry identity, value/width information, datatype, and data. | Identity transition and record structure. |
| Drive integration | ID, data, and metadata drives participate in recursive bitmap-to-ID and gestalt integration. | Cross-map to D0/D1/D2. |
| Bitmap | Associates members and participates in reconstruction. | Order, repetition, multiplicity, positions, bounds, malformed references. |
| Widths | y meaningful bits may be represented in x storage bits. | Units, ranges, padding, alignment, canonicalization, exceptions. |

The terms “touple,” “gestalt,” and “gesple” are preserved pending an explicit terminology decision.

Historical prompts, proposals, attestations, and labels are sources, not independent authorization. The earlier recursive section A proposal remains unaccepted.
