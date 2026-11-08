# sf-UUID Member Identity Contract v0.1

**Status:** LOCKED — accepted sf-AmorphDataDrive member identity contract

**Proposed:** 2026-11-05

**Accepted and locked:** 2026-11-08

**Applies to:** sf-AmorphDataDrive member identity

**Baseline:** locked sf-AmorphDataDrive v0.3 remains unchanged and controlling

## 1. Purpose and authority

This contract defines the meaning, representation, issuance, comparison, and continuity rules for a member `sf-UUID`. It resolves only the member-identity portion of the architecture.

This contract was accepted and locked through explicit owner direction on 2026-11-08. It is a controlling member-identity supplement to locked sf-AmorphDataDrive v0.3; it does not rewrite v0.3, create v0.4, or settle the residual contracts listed in section 16.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** express controlling requirements within this locked member-identity scope. They do not grant execution, publication, attestation, or operating authority.

## 2. Scope

This contract defines:

- the logical subject identified by a member sf-UUID;
- its 128-bit UUID profile and canonical encodings;
- issuance and admission-domain duplicate checks;
- collision and incompatible-claim handling;
- identity outcomes for relocation, replication, copying, reconstruction, drive replacement, generation change, promotion, and composition;
- placement constraints imposed by D0, D1, and D2;
- boundaries for drive identity, a possible future 64-bit identifier, bitmap lookup, and physical topology.

This contract does not define:

- a physical ID, data, or metadata drive layout;
- a mandatory drive identifier;
- bitmap syntax, occurrence ordering, repetition, multiplicity, or reconstruction grammar;
- `x` storage-width or `y` meaningful-width packing;
- a touple, gestalt, or gesple record schema;
- recursion bounds, invalidation order, commit order, receipts, or reattestation;
- a hash, signature, attestation verifier, authorization model, or recovery controller;
- an Etabit dependency, Cypher Disk authority, or Experience Orchestration Drive;
- a registry operation or deployed storage implementation.

## 3. Identity subject

An sf-UUID identifies one **logical sf member**.

The identifier is an opaque identity token. Its bits MUST NOT encode or be interpreted as:

- a D0 position or value;
- a physical drive, controller, path, file, partition, or filesystem location;
- a datatype, encoding, code page, symbol, or semantic value;
- an `x` width, `y` width, bitmap position, occurrence position, or recursion level;
- a generation, timestamp, lifecycle state, or ordering claim;
- a content hash, integrity result, attestation, authority, or permission;
- a touple, gestalt, or gesple class;
- a future compact 64-bit key.

Equality of sf-UUID values means only that two records claim the same logical member identity. Equality does not independently prove equal content, compatible generations, valid lineage, authenticity, authorization, attestation, semantic equivalence, or safe reconstruction.

Equal content does not imply equal identity. Independently created members MUST receive distinct sf-UUID values even when their bytes or hashes are equal.

## 4. UUID profile and canonical representation

### 4.1 Issuance profile

A newly issued sf-UUID MUST be an RFC 9562 UUID version 4 using the RFC UUID variant. It contains 128 bits represented as 16 octets. The version field MUST be `0100` and the variant field MUST begin with `10`.

The nil UUID and maximum UUID are prohibited. A UUID using another version or variant MUST NOT be issued as an sf-UUID under this v0.1 profile.

Version 4 is selected because member identity is intended to be opaque, distributable, and independent of content, names, physical placement, and issuance time. This contract does not use name-derived UUIDv5 or time-ordered UUIDv7 semantics.

### 4.2 Canonical text

The canonical text form is 36 lowercase ASCII characters using the `8-4-4-4-12` hexadecimal layout:

```text
xxxxxxxx-xxxx-4xxx-[89ab]xxx-xxxxxxxxxxxx
```

Example conforming value:

```text
4e5d2c28-7c17-4db5-89ab-b42cf3861c27
```

A conforming writer MUST emit the lowercase canonical form without braces, whitespace, a `urn:uuid:` prefix, or an `sf-uuid:` prefix.

A conforming stored identity MUST use the canonical form. An intake process MAY recognize an uppercase but otherwise valid RFC representation, but it MUST preserve the original supplied spelling as intake evidence when provenance is required and MUST canonicalize before admission. Intake tolerance does not make a noncanonical stored value conforming.

### 4.3 Canonical binary form and comparison

The canonical binary form is the 16 UUID octets in RFC/network order. Implementations MUST NOT apply platform-specific mixed-endian field rearrangement to the canonical serialized form.

Comparison MUST operate on the decoded 128-bit value. Text case and an intake representation are not identity fields. A value that cannot be decoded unambiguously into the required profile MUST be rejected rather than compared approximately.

## 5. Issuance and admission

### 5.1 Generation

An issuer MUST use a cryptographically secure random source suitable for UUIDv4 generation. It MUST NOT derive the identifier from member content, a content hash, a path, a drive serial, a clock, a counter, a username, or a D0 location.

### 5.2 Admission domain

An **admission domain** is the set of member identities that may be compared, matched, recursively integrated, or reconstructed together.

Before a newly generated sf-UUID is admitted, the issuer MUST check it against the target admission domain. When previously separate domains are joined, their identity claims MUST be reconciled before the combined domain is admitted.

The admission check does not require a universal online registry and MUST NOT require every physical drive to possess a drive-level sf-UUID. The responsible topology or registry profile must later define how the relevant domain is enumerated and checked.

### 5.3 Bounded generation attempts

Initial issuance has a maximum of eight generation-and-check attempts. If all eight candidates conflict with existing admitted identities, issuance MUST fail with `SF_UUID_ISSUANCE_EXHAUSTED`.

An issuer MUST NOT respond to exhaustion by truncating a UUID, changing to an unapproved UUID version, inserting local machine information, reusing a conflicting value, or continuing without a bound.

## 6. Duplicate claims and collisions

The same sf-UUID may appear in more than one record or physical placement when those records are validated occurrences of the same logical member. Duplicate appearance alone therefore does not prove either a valid replica or a collision.

The following cases are distinct:

1. **Validated same-member occurrence:** the same sf-UUID is accompanied by compatible generation and lineage evidence for a replica, relocation, or accepted reconstruction.
2. **Content duplicate:** content or hashes are equal but sf-UUID values differ. The members remain distinct unless a separate relation records another form of equivalence.
3. **Identity conflict:** the same sf-UUID is accompanied by incompatible member histories, incompatible generation claims, or mutually exclusive lineage claims.
4. **Identifier collision:** independent issuance assigned the same sf-UUID to different logical members.

An identity conflict or collision MUST fail closed. It MUST NOT cause automatic merge, overwrite, deletion, equivalence, lineage transfer, or authority transfer.

A conflicting candidate detected before publication or external reference MAY be discarded and replaced during the bounded initial issuance process. Once a conflicting identity has been admitted, published, or externally referenced, the system MUST preserve both claims and their evidence. Any later re-identification requires an explicit reviewed operation outside this contract; silent reminting is prohibited.

## 7. Matching and continuity

### 7.1 Identity match

Two canonical sf-UUID values match when their decoded 128-bit values are equal. A positive identity match is necessary but not sufficient to select data or metadata. The consuming relation MUST also establish the required generation, lineage, and validation state.

Drive identity, path, ordinal position, device serial, and content hash MUST NOT be required for the sf-UUID equality comparison.

### 7.2 Relocation and replicas

A physical relocation of the same logical member preserves its sf-UUID.

A validated replica of the same logical member preserves its sf-UUID and generation. Replica or placement identity, if needed, is a separate topology concern and MUST NOT be encoded into the member sf-UUID.

### 7.3 Copies and forks

A copy intended to become an independently governed or independently evolving member MUST receive a new sf-UUID. It MAY carry an external `derived-from` relation to the source member.

A byte-for-byte copy does not automatically qualify as a replica. Replica status requires validated lineage under the later authority and attestation contracts.

### 7.4 Drive replacement

Replacing an ID, data, or metadata drive MUST NOT by itself change member sf-UUID values. A replacement medium may claim continuity only for members whose association and lineage are validated externally.

The absence of a drive-level sf-UUID does not prevent member matching. A new physical drive MUST NOT acquire the logical identities of an old drive merely by occupying the same port, path, or role.

### 7.5 Reconstruction

A reconstruction preserves the member sf-UUID only when the required lineage, source generation, and reconstruction result have been validated under contracts external to this document.

An unproven reconstruction MUST receive a new sf-UUID if it is admitted as a member. It MAY retain a non-equivalence provenance claim describing the candidate source, but it MUST NOT claim the original identity.

## 8. Generations

Generation is external to the sf-UUID.

An accepted new generation of the same continuing logical member MAY preserve its sf-UUID. Its generation value and transition evidence MUST be represented outside D0 and MUST NOT be packed into UUID bits.

An identity match without a compatible generation reference is insufficient to select a particular data or metadata state. Conflicting concurrent generation claims MUST fail closed pending reconciliation.

This contract does not define generation numbering, invalidation, promotion order, commit order, receipt proof, or reattestation.

## 9. Touple, gestalt, and gesple identity

This contract preserves the project vocabulary `touple`, `gestalt`, and `gesple` without normalizing or collapsing those terms.

For identity purposes:

- a promotion that produces a richer validated representation of the same single logical member MAY preserve that member's sf-UUID;
- a composition that assembles multiple independently identified members into a new gestalt or gesple MUST issue a new sf-UUID for the assembled object;
- constituent member sf-UUID values MUST remain unchanged and MUST be retained through external membership relations;
- promotion MUST NOT erase the source generation or lineage record;
- composition MUST NOT reuse one constituent's identity as the assembled object's identity;
- an operation that cannot determine whether it is same-member promotion or multi-member composition MUST fail with `SF_UUID_TRANSITION_AMBIGUOUS`.

These rules define identity outcomes only. Qualification, membership grammar, dependency ranks, invalidation, equivalence, recursion bounds, and record structure remain open.

## 10. D0, D1, and D2 placement

Locked v0.3 remains controlling:

- an sf-UUID MUST NOT be assigned or stored as identity metadata on raw D0;
- a coincidental 128-bit pattern present in D0 is not thereby an sf-UUID;
- member identity records belong in D1 or in an explicitly external identity structure compatible with D1 ownership of relation and interpretation;
- D2 MAY reference sf-UUID-bearing D1 relations when composing coherent objects;
- neither text nor binary sf-UUID representation changes the meaning of D0;
- an ID drive that stores assigned identities MUST NOT be classified as raw D0 merely because it is the lowest drive in a physical arrangement.

This contract does not decide whether a physical ID drive is a D1 realization, a separate external identity medium, or another recursive role.

## 11. Drive identity

A drive-level sf-UUID remains optional and discouraged. This contract neither issues nor requires one.

Any later drive-identity profile MUST:

- distinguish drive scope from member scope;
- prevent a drive identifier from substituting for a member sf-UUID;
- preserve member matching when no drive sf-UUID exists;
- define drive copy and replacement behavior separately;
- prevent drive replacement from silently rewriting member identities.

## 12. Deferred 64-bit identifier

A separate 64-bit identifier remains a possible later addition and is not required by this contract.

An implementation MUST NOT obtain an authoritative 64-bit member identifier by truncating, folding, hashing, or otherwise compressing an sf-UUID. No current one-to-one sf-UUID-to-64-bit mapping is defined.

If introduced later, a 64-bit identifier must be an external compact key or index with its own scope, collision handling, mapping lifecycle, and failure rules. It MUST NOT replace the member sf-UUID merely by being shorter.

## 13. Bitmap and topology interface

This contract imposes the following requirements on later bitmap and topology contracts without defining those contracts:

- a bitmap position that resolves to a member MUST use an explicit external position-to-member mapping;
- an sf-UUID MUST NOT be converted directly into a bitmap position by assumption;
- resolving an sf-UUID identifies a member claim but does not establish occurrence order, repetition, multiplicity, generation selection, metadata selection, or attestation;
- the later occurrence grammar must distinguish sequences such as `ABA` and `AAB`;
- physical ID, data, and metadata drive roles must preserve the D0/D1/D2 boundary at every recursive level;
- integration must remain possible without mandatory drive sf-UUID values.

## 14. Contract-local failure outcomes

These labels describe outcomes in this locked member-identity contract. They are not registered sf operations and do not modify the separate sf-Registry candidate.

| Outcome | Required condition |
| --- | --- |
| `SF_UUID_MALFORMED` | Input cannot be decoded as an unambiguous 128-bit UUID. |
| `SF_UUID_NONCANONICAL` | A stored identity is not in the required canonical form. |
| `SF_UUID_PROFILE_UNSUPPORTED` | UUID version, variant, nil, maximum, or other profile rule is unsupported. |
| `SF_UUID_COLLISION` | Independent logical members claim the same sf-UUID. |
| `SF_UUID_IDENTITY_CONFLICT` | Same-identity records carry incompatible history or lineage claims. |
| `SF_UUID_LINEAGE_UNPROVED` | A copy, replacement, or reconstruction lacks evidence required to preserve identity. |
| `SF_UUID_GENERATION_CONFLICT` | The requested state cannot select a compatible generation. |
| `SF_UUID_TRANSITION_AMBIGUOUS` | Same-member promotion cannot be distinguished from new-object composition. |
| `SF_UUID_ISSUANCE_EXHAUSTED` | Eight bounded generation-and-check attempts all conflict. |

Failures MUST preserve the conflicting evidence needed for review. A failure label is not itself proof of cause, authority to repair, or permission to delete a record.

## 15. Conformance examples

| Scenario | Identity result |
| --- | --- |
| Same member moved to another physical location | Preserve sf-UUID. |
| Validated mirror of the same member and generation | Preserve sf-UUID and generation. |
| Equal bytes created independently | Issue distinct sf-UUID values. |
| Independently evolving fork | Issue a new sf-UUID; retain external derivation relation. |
| Replacement drive with validated member lineage | Preserve member sf-UUID values. |
| Reconstruction without validated lineage | New sf-UUID if admitted; do not claim original identity. |
| New accepted generation of one continuing member | May preserve sf-UUID; generation remains external. |
| Several identified members assembled into a gestalt/gesple | Issue a new sf-UUID for the assembly; preserve member IDs. |
| Same sf-UUID with incompatible histories | Fail closed; preserve both claims. |
| UUID truncated to 64 bits | Nonconforming; not an sf-UUID or authoritative alias. |
| Raw D0 happens to contain the same 128-bit pattern | No identity assignment is created. |

## 16. Residual open decisions

This contract resolves the member sf-UUID representation and identity-lifecycle rules defined here. It does not close:

1. physical and logical ID/data/metadata topology;
2. bitmap and ordered-occurrence grammar;
3. `x`/`y` width ownership and canonical packing;
4. complete touple-to-gestalt/gesple transition and recursion rules;
5. generation, invalidation, commit, receipt, and reattestation sequence;
6. verification, attestation, authority, and recovery mechanisms;
7. optional drive identity;
8. any future 64-bit identifier and mapping;
9. Etabit qualification or cross-map.

Those residual boundaries and this contract's limited lock scope MUST remain visible. Changing a residual decision or this locked member-identity contract requires a separately reviewed and approved scope.
