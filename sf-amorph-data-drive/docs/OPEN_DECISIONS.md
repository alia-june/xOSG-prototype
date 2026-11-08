# Open decisions

These decisions block a complete successor architecture or implementation.

1. **sf-UUID member identity contract — resolved and locked.** The [locked v0.1 contract](../contracts/SF_UUID_IDENTITY_CONTRACT_v0.1_LOCKED.md) defines format, width, issuance, admission-domain checks, duplicates, collisions, copy identity, replacement identity, generation continuity, and matching without drive UUIDs. The [lock decision](../decisions/SF_UUID_IDENTITY_CONTRACT_v0.1_LOCK_2026-11-08.md) records acceptance and scope. Physical topology, bitmap mapping, attestation/authority mechanisms, optional drive identity, and any future 64-bit mapping remain open.
2. **Storage topology** — ID, data, and metadata drive roles and their relationship to D0/D1/D2 at every recursive level.
3. **Bitmap grammar** — mapping, order, repetition, multiplicity, conflicts, malformed references, bounds, and deterministic reconstruction.
4. **x/y width contract** — units, ranges, packing, padding, alignment, canonical form, exceptional values, and record ownership.
5. **Touple-to-gestalt/gesple transition** — identity, membership, dependencies, invalidation, generations, equivalence, and recursion bounds.
6. **Raw enumeration wording** — coincident bit patterns versus assigned header, hash, instruction, or metadata roles without weakening D0.
7. **Lifecycle sequence** — validation, promotion, commit, receipt, and reattestation order and receipt proof.
8. **One-way transfer profile** — domain-local interactions and claims permitted across a physically one-way boundary.
9. **Etabit relationship** — optional strict source profile, lower substrate, or separate related architecture.
10. **Verification and authority** — evidence, attestation, authorization, execution, and recovery contracts.

Do not resolve these by importing generic UUID, filesystem, Etabit, Cypher Disk, or library conventions.
