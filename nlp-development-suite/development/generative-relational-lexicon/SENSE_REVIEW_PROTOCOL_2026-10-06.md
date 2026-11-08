# Sense-scoped review protocol

Date: 2026-10-06

Status: generated review procedure; no reviewer decision has been assigned.

This protocol applies to the frozen blank package under
`pilot/sense-aboutness/review-sample/`. It is a review instrument, not a
semantic generator and not a canon-admission procedure.

## Reviewer separation

The person or process that builds the sample must not supply the reference
judgment for the same record. A calibration tranche is reviewed independently
by two reviewers before any adjudication. Reviewer identity and timestamp are
recorded in the copy being reviewed. A reviewer may abstain; abstention is a
valid result, not a failure to complete the record.

Reviewers inspect the attached raw source spans and structural comparison
fields. They do not treat the historical heading, exact spelling, normalized
surface, or modern index match as a definition. External lookup is optional and
must be recorded as a separate source with its own license and provenance; it
cannot silently replace the pinned evidence.

## Per-record procedure

1. Confirm the record ID, normalized form, source hash, source spans, and
   stratum coordinates.
2. Confirm that the raw block actually supports the observed form and structural
   placement. Record a parser/source issue if it does not.
3. Identify whether the evidence supports one distinguishable sense candidate,
   multiple competing sense candidates, or no sense-scoped claim.
4. For each candidate, fill only the versioned sense-aboutness contract. Every
   scope field and aboutness assertion must cite evidence references. Use
   `INFERENCE` or `GENERATED_SYNTHESIS` only for the truth state of a proposal;
   never use `ACCEPTED_CANON` in this package.
5. Use `CONFLICTED_CANDIDATE` when evidence supports incompatible candidates;
   list reciprocal conflict references. Use `ABSTAINED` when the evidence does
   not distinguish a sense or facet.
6. Record concise notes about the evidence boundary and unresolved question.
   Do not write a dictionary definition or promote a source heading into a
   timeless meaning during this pass.

## Allowed review statuses

| Status | Meaning |
|---|---|
| `SUPPORTED_CANDIDATE` | One bounded candidate is supportable as an inference, with cited evidence; it is still unaccepted. |
| `MULTIPLE_CANDIDATES` | Two or more scoped candidates remain live and must be distinguished or adjudicated. |
| `ABSTAINED` | Evidence is insufficient, form-only, contradictory, or out of scope. |
| `PARSER_OR_SOURCE_ISSUE` | The raw block, source span, or structural extraction cannot be reconciled. |

These statuses describe the review result only. None admits a lexical canon or
licenses redistribution.

## Calibration tranche

The first tranche should be small enough for two independent passes and broad
enough to include every match layer, every unresolved visible-shape class,
source-label presence and absence, at least two head-dispersion buckets, and
single and composite POS signatures. The tranche selector must be deterministic
and recorded before reviewers see the records. Do not choose examples because
their spelling appears easy or familiar.

The tranche exit record must include:

- exact record IDs and selection hashes;
- reviewer identities and timestamps;
- per-field agreement and disagreement counts;
- disagreement categories: source-span, sense-boundary, facet, conflict,
  abstention, or schema error;
- adjudication notes that preserve both original judgments;
- the number of records still unresolved after adjudication.

Agreement is a measurement of this tranche, not proof that the remaining
population is semantically resolved. No candidate-generation rule may be tuned
against a single reviewer’s judgment without recording the change and adding a
regression fixture.

## Stop conditions

Pause the review and preserve the record when:

- the source span is missing, corrupted, or inconsistent with the membership;
- a proposed facet requires a definition not present in the evidence;
- reviewers disagree about whether two forms are the same sense;
- a source license or external lookup boundary is unclear;
- the proposed record would require a new truth state or authority effect.

Those cases go to the unresolved queue. They do not justify silently widening
the schema or filling the gap with generated prose.

## Exit gate for RLX-N03

RLX-N03 is complete only when the calibration and subsequent review records are
independently attributable, source-linked, schema-valid, disagreement-bearing,
and reproducible. Until then, the 853-record package remains a blank structural
coverage set and RLX-N04 candidate generation must not begin.
