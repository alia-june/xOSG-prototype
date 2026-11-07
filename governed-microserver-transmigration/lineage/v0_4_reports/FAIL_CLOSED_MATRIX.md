# Candidate control-state and fault matrix — v0.4

This is an **inspection model**, not a separately verified formal proof. Runtime implementation is in `microtrans/governed.py` and `microtrans/glue.py`.

| State | Evidence needed before next state | Next on success | Default on failure |
|---|---|---|---|
| `S0_INPUT_RECEIVED` | One strict JSON manifest, bounded, no `null` or nonfinite numbers | `S1_INPUT_ACCEPTED` | `F_REFUSED` |
| `S1_INPUT_ACCEPTED` | Correct scope, request ID and digest accepted by distinct policy process | `S2_POLICY_PASSED` | `F_REFUSED`; no worker launch |
| `S2_POLICY_PASSED` | Child namespace/mount/capability controls established and verified | `S3_SCHEMA_EVALUATION` | `F_REFUSED`; do not import worker code |
| `S3_SCHEMA_EVALUATION` | Schema microserver accepts and output preserves identical manifest | `S4_GRAPH_EVALUATION` | `F_REFUSED`; do not call graph gate |
| `S4_GRAPH_EVALUATION` | Graph microserver accepts, receipts and digests match | `S5_EXTERNAL_AUDIT` | `F_REFUSED` |
| `S5_EXTERNAL_AUDIT` | Separate validator agrees on candidate semantics and negative authority ceilings | `S6_STATIC_PASSED_CANDIDATE` | `F_REFUSED` |
| `S6_STATIC_PASSED_CANDIDATE` | No automatic next state | Terminal candidate result | No admission/publication transition |
| `F_REFUSED` | No automatic recovery | Terminal refusal | No admission/publication transition |

## Cross-cutting invariants

**I-1 Identity**: input hash and request ID bind all stage receipts.  
**I-2 Authority**: authority can only remain at or below read-only candidate scope, never rise.  
**I-3 Refusal**: upstream refusal prevents downstream execution.  
**I-4 Provenance**: v0.2 witness remains byte-identical; reconstructed behavior remains candidate.  
**I-5 Composition**: identity-only ordinary glue cannot transform payload or transfer authority.  
**I-6 Self-validation**: neither microserver nor glue can pronounce itself admitted or published.  
**I-7 External audit**: corroboration means separate implementation, not separate independent custody.  
**I-8 Windows**: strict OS profile unavailable; cannot silently run insecure alternative with strict label.

## Negative evidence map

| Invariant | Counterexample | Exercised by |
|---|---|---|
| I-1 | Manifest digest changed | `test_policy_digest_binding`; `test_external_audit_refuses_forged_success_on_bad_manifest` |
| I-2 | Request for `FULL_CONTROL` | `test_policy_refuses_authority_escalation` |
| I-3 | Schema refusal followed by graph launch | `test_schema_refusal_blocks_graph_execution` (retained v0.3) |
| I-4 | Reconstructed checker disagrees with preserved v0.2 | 19-case source parity suites |
| I-5 | Mutated upstream data | `test_glue_payload_tamper_refuses` (retained v0.3) |
| I-6 | Forged publication/admission | `test_forged_validator_cannot_admit` |
| I-7 | Forged static pass on invalid graph | `test_external_audit_refuses_forged_success_on_bad_manifest` |
| I-8 | Unsupported OS profile | `test_fail_closed_on_unsupported_os` |

## Evidence methodology

Each observation should be examined using the repeated functions **Being, Belief, Understanding and Observation**. Tests establish particular observations only. Conclusions exceeding the observed test reach remain unverified, and any rule unsupported by a precise mechanism is documented as planned rather than activated.
