# Generative relational lexicon status and next actions

Date: 2026-10-06

Status: verified internal research baseline; not accepted lexical canon; not
part of the immutable P08 candidate; not production-ready or publication-ready.

## Evidence inventory

| Identifier | Location | Truth state | Current result | Boundary |
|---|---|---|---|---|
| Post-repair source | `run_tier_zero_pilot.py` and pinned Project Gutenberg artifact | SOURCE plus DERIVED parse | Parser v4 emits 1,043 stable heads and 102,235 memberships | Structure and source placement only |
| Parser-repair decision | `PARSER_REPAIR_DECISION.json` | ACCEPTED TEST AUTHORITY | Six repeated patterns authorized; three patterns held | No semantic or production authority |
| Parser-repair delta | `pilot/parser-repair/PARSER_REPAIR_DELTA_REPORT.json` | DERIVED | Six authorized patterns have zero residuals in the regenerated sample | Samples are diagnostic rather than population estimates |
| Modern comparison | `pilot/modern-comparison/DISCREPANCY_SHAPE_REPORT.json` | DERIVED | 59,636 historical forms; 28,271 exact modern lemma candidates | Exact spelling is not sense identity |
| Normalization audit | `pilot/modern-comparison/normalization-audit/NORMALIZATION_SHAPE_REPORT.json` | DERIVED | 1,145 additional surface candidates; 30,220 unresolved | Transformations are not semantic equivalence |
| Review dispositions | `pilot/modern-comparison/normalization-audit/review-sample/dispositions/REVIEW_DISPOSITION_REPORT.json` | DERIVED BOUNDED SAMPLE | Two confirmed one-off parser defects remain in 258 sampled records | Unsampled records receive no disposition |
| Strict source map | `INITIAL_MINING_GAP_REPORT.json` | DERIVED FROM RECORDED POLICY | Five eligible sources and one mining-ready unit among 44 surveyed sources | Eligibility does not authorize ingestion |
| Sense-aboutness baseline | `SENSE_ABOUTNESS_BASELINE_DECISION.json` | ACCEPTED TEST AUTHORITY | Eight exact inputs pinned to commit `b365c25` | Schema and baseline work only |
| Sense-aboutness contract | `pilot/sense-aboutness/SENSE_ABOUTNESS_CONTRACT_RECEIPT.json` | DERIVED | Draft 2020-12 schema and semantic invariants pass three valid and four invalid fixtures | No candidate meaning has been generated or reviewed |
| Blank semantic review package | `pilot/sense-aboutness/review-sample/SENSE_REVIEW_SAMPLE_RECEIPT.json` | DERIVED | 853 observed structural strata each have one deterministic source-bearing record | All 5,971 reviewer fields remain null |
| Review protocol | `SENSE_REVIEW_PROTOCOL_2026-10-06.md` | GENERATED_SYNTHESIS | Independent calibration, abstention, disagreement, and stop conditions are defined | No calibration tranche has been reviewed |
| Blank dual-review calibration | `pilot/sense-aboutness/calibration/SENSE_CALIBRATION_RECEIPT.json` | DERIVED TEST PACKAGE | 34 deterministic records cover all 57 observed calibration atoms with two blank reviewer copies | No reviewer judgments, agreement, or adjudication exists |
| Review intake validator | `validate_sense_calibration_review.py` | VERIFIED TEST CONTROL | Rejects source-evidence mutation, malformed statuses, and premature reviewed-mode claims; blank package reports `BLANK_NOT_REVIEWED` | Does not create reviewer judgments or adjudicate disagreements |
| Independent reviewer packets | `pilot/sense-aboutness/review-packets/SENSE_REVIEW_PACKET_MANIFEST.json` | DERIVED TEST PACKAGE | Two deterministic 34-record packets share source evidence while exposing only one reviewer slot each | Packets remain blank and require independent human review |
| Existing P08 candidate | `../../production/p08/CANDIDATE_RECEIPT.json` | VERIFIED INTERNAL TEST CANDIDATE | Exact artifact remains unchanged and awaits P09 disposition | It excludes this research track |

## Current viability

The current approach is viable for a provenance-bearing historical evidence
graph, structural discrepancy mapper, and controlled lexical-reconstruction
testbed. It is not yet demonstrated as a comprehensive modern dictionary or a
complete past-present-future word universe.

Strong evidence exists for deterministic extraction, provenance retention,
visible abstention, layered surface comparison, and reversible regeneration.
The principal missing proof is semantic: there is no independently reviewed
sense-scoped gold set, measured sense accuracy, or accepted path from historical
category placement to a present first-party sense and definition.

## Open work

| ID | State | Work | Exit evidence |
|---|---|---|---|
| RLX-O01 | HELD | `BARE_SUFFIXED_HEAD_MARKER_CAPTURE` observed once | A repeated raw-source pattern or an explicit separately authorized one-off rule |
| RLX-O02 | HELD | `LEADING_FOOTNOTE_MARKER_CAPTURE` observed once | A repeated raw-source pattern or an explicit separately authorized one-off rule |
| RLX-O03 | HELD | `GROUPED_NUMBER_SPLIT` had no residual in the new sample | New evidence demonstrating a reproducible defect |
| RLX-O04 | VERIFIED TEST CONTRACT | Sense-scoped aboutness schema and review vocabulary | Versioned schema plus positive negative ambiguous and abstention fixtures passed |
| RLX-O05 | CALIBRATION WORKSHEET VERIFIED; REVIEW PENDING | Independent semantic evaluation set | 853 source-bearing records exist; a 34-record dual-review calibration worksheet covers all 57 calibration atoms, but no reviewer judgments or agreement evidence exists |
| RLX-O06 | NOT STARTED | Evidence-only sense candidate generator | Deterministic output with source paths competing candidates and visible unknowns |
| RLX-O07 | NOT STARTED | Semantic quality and abstention evaluation | Precision error taxonomy coverage and abstention receipt against the frozen set |
| RLX-O08 | NOT STARTED | Additional permissive-source adapters | One decision manifest and reproducible adapter receipt per exact source version |
| RLX-O09 | NOT STARTED | First-party reviewed senses and definitions | Explicit review and acceptance separate from source evidence and generated prose |
| RLX-O10 | NOT STARTED | Successor downloadable candidate | New ID manifest hashes rollback and tests; never overwrite P08 |

## Ordered next course

### RLX-N01 — Freeze the semantic-evaluation baseline

Status: **verified test baseline** on 2026-10-06.

Pin commit `bd3109a`, the parser-repair receipt, exact source hashes, and the
current unresolved population. Add a machine-readable decision declaring the
evaluation scope and prohibited inferences.

Exit gate: every evaluation input has a path, byte count, SHA-256, truth state,
and authority boundary.

Evidence: `SENSE_ABOUTNESS_BASELINE_DECISION.json`; all eight inputs match both
the working tree and their blobs in commit `b365c25`.

### RLX-N02 — Specify sense-scoped aboutness

Status: **verified test contract** on 2026-10-06.

Define candidate facets such as subject, domain, operation, quality, object,
period, community, and register. Require every facet assertion to attach to a
sense candidate rather than an undifferentiated spelling. Represent conflict,
unknown, not-applicable, and abstention directly.

Exit gate: schema validation and adversarial fixtures prove that form-level
co-occurrence cannot silently become sense-level fact.

Evidence: `schemas/sense-aboutness-candidate-v0.1.schema.json`, seven fixtures,
and `pilot/sense-aboutness/SENSE_ABOUTNESS_CONTRACT_RECEIPT.json`. The contract
requires sense-local assertions, evidence references, proposal-only authority,
and explicit ambiguity, conflict, or abstention. Form-only support and
`ACCEPTED_CANON` promotion are rejected.

### RLX-N03 — Build the reviewed evaluation set

Status: **sampling frame and blank package verified; human review not started**.

Draw a deterministic stratified sample across exact matches, normalized
candidates, unresolved shapes, historical head dispersion, parts of speech,
source labels, and collision levels. Preserve the raw source spans. Reviewers
record evidence-supported facets, competing senses, insufficient evidence, and
parser defects without repairing data during review.

Exit gate: the frozen set reconciles exactly; disagreements and unknowns remain
visible; no generated answer is used as its own reference.

Partial evidence: `SENSE_REVIEW_SAMPLE_DECISION.json` and
`pilot/sense-aboutness/review-sample/SENSE_REVIEW_SAMPLE_RECEIPT.json` reconcile
59,636 population records to 853 observed seven-axis strata and 853 selected
records. All reviewer fields are null. The N03 exit gate remains open until
review dispositions and agreement/conflict evidence exist.

### RLX-N04 — Implement candidate generation

Generate ranked aboutness and sense candidates from allowed structural
features. Keep source evidence, inference, and generated synthesis in separate
fields. Default to abstention when evidence is absent or contradictory.

Exit gate: deterministic unit and negative tests pass; no candidate is emitted
without traceable evidence features and a declared truth state.

### RLX-N05 — Evaluate before scaling

Measure per-facet precision, disagreement, collision, abstention, and coverage.
Inspect false positives before optimizing coverage. Establish testbed thresholds
only after the baseline result is visible.

Exit gate: an append-only evaluation receipt distinguishes measured performance
from proposed thresholds and records every known failure class.

### RLX-N06 — Expand sources one adapter at a time

Prioritize permissive historical and governmental sources that fill measured
gaps. Each adapter requires an exact artifact or endpoint version, license
evidence, field-level purpose, source-span policy, hash where possible, negative
tests, and an acceptance decision. Do not bulk-ingest merely because a source is
listed as eligible.

Exit gate: the adapter is reproducible and removal leaves the first-party graph
valid with explicit evidence gaps.

### RLX-N07 — Admit reviewed lexical relations

Promote only reviewed candidate relations into versioned first-party sense
records. Independently authored definitions remain distinguishable from source
facts and generated drafts. Rejections and superseded interpretations remain
retained.

Exit gate: every admitted relation has reviewer authority, evidence links,
scope, version, conflicts, and rollback history.

### RLX-N08 — Construct a successor artifact

After N01 through N07 pass, build a new downloadable candidate with a new
identifier. Include the accepted schema, bounded data, notices, manifest,
verification receipt, known limitations, and rollback instructions. The P08
candidate remains immutable.

Exit gate: two byte-identical constructions pass the full rig and the exact new
hash is presented for a separate acceptance decision.

## Immediate action

Continue RLX-N03 with the review protocol and bounded human review. Begin with a
small calibration tranche drawn from the frozen 853-record package; record
reviewer identity, evidence-supported sense distinctions, abstentions,
disagreements, and adjudication separately. Do not implement candidate
generation until the reviewed reference set and its agreement limits exist.

The protocol is recorded in `SENSE_REVIEW_PROTOCOL_2026-10-06.md`. The blank
dual-review calibration worksheet is now generated and verified in
`pilot/sense-aboutness/calibration/`; it must not prefill any semantic
judgment. The review-intake validator now confirms the package is
`BLANK_NOT_REVIEWED`. The next action is independent human review of both
copies; run the validator with `--require-reviewed` only after both copies have
been completed and preserved. Separate reviewer packets are available under
`pilot/sense-aboutness/review-packets/`.

## Validation of this status update

- Production plan validation: passed for 12 ordered phases and 82 required
  control files.
- Coverage-ledger structure: passed for 32 unique records.
- Production-control suite: 42 tests passed in the prepared environment with
  `jsonschema==4.26.0`.
- Generative-relational-lexicon suite: 93 tests passed after adding five
  independent reviewer-packet tests.
- Whitespace/error-marker check: passed.

The initial production-control attempt under the bare host interpreter failed
only its dependency preflight and is recorded in `production/ERROR_LOG.md`; it
is not represented as a passing prepared-environment run.
