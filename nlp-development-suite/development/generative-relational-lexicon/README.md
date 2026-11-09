# Generative Relational Lexicon

Status: generated research scaffold; not accepted lexical canon, not a source
ingestion authorization, and not part of the immutable P08 candidate.

This track builds an English lexical system from independently generated
substructure and superstructure. External resources are used first to map
language lineage, source capability, coverage, gaps, and conflicts. Their
definitions and other expressive content are not imported into the first-party
core by this scaffold.

## Initial artifacts

- `SOURCE_LANGUAGE_MAP.json` records the English inheritance backbone,
  contact/borrowing layers, candidate evidence sources, and explicit gaps.
- `SOURCE_REGISTER.md` explains what each researched source may contribute and
  why some sources remain isolated or blocked.
- `TRANSLATION_SOURCE_SURVEY.md` compares Hindi-English and Arabic-English
  government, university, dictionary, terminology, and parallel-corpus sources
  by exact reuse terms and production disposition.
- `LANGUAGE_EXPANSION_SURVEY.md` ranks historically relevant and structurally
  contrasting languages, then maps them to reusable multilingual resources.
- `INITIAL_MINING_LICENSE_POLICY.json` defines a proposed CC0/public-domain-only
  first mining tier; `analyze_initial_mining.py` produces the resulting
  machine-readable and human-readable hole reports without mining content.
- `TIER_ZERO_PILOT_DECISION.json` records the user-authorized, non-production
  Roget pilot boundary; `run_tier_zero_pilot.py` verifies the pinned artifact
  before emitting source-spanned, proposal-only structural evidence.
- `query_word_history.py` queries those historical memberships for any modern
  word by exact normalized form and returns evidence candidates and absences.
- `MODERN_COMPARISON_DECISION.json` and `compare_roget_oewn.py` keep the
  attribution-licensed OEWN 2025 adapter separate from Tier Zero and report
  discrepancy shapes without importing definitions or choosing explanations.
- `NORMALIZATION_AUDIT_DECISION.json` and `audit_surface_normalization.py`
  measure dictionary-supplied variants and increasingly loose surface rules as
  separate candidate layers without asserting semantic equivalence.
- `UNRESOLVED_SHAPE_AUDIT_DECISION.json` and `audit_unresolved_shapes.py`
  partition the remaining candidates by visible structure and emit proposal-only
  review queues while preserving source evidence and unknown lexical validity.
- `REVIEW_SAMPLE_DECISION.json` and `build_review_sample.py` select a bounded,
  deterministic shape/POS sample and attach the pinned raw Roget source blocks
  for review without assigning dispositions.
- `REVIEW_DISPOSITION_DECISION.json` and `review_sample_dispositions.py`
  discriminate evidenced parser-boundary defects from literal raw occurrences
  and propose regression guards only for repeated sample patterns.
- `PARSER_REPAIR_DECISION.json` and `measure_parser_repair.py` pin the
  pre-repair commit, authorize only repeated evidenced patterns, and measure
  complete before/after corpus and comparison deltas.
- `STATUS_AND_NEXT_ACTIONS_2026-10-06.md` records the current evidence state,
  viability boundary, open work, and dependency-ordered research gates without
  changing the immutable P08 candidate.
- `SENSE_ABOUTNESS_BASELINE_DECISION.json`, the schema under `schemas/`, and
  `validate_sense_aboutness.py` freeze the semantic-evaluation inputs and define
  a proposal-only sense-scoped contract with explicit ambiguity, conflict, and
  abstention behavior.
- `SENSE_REVIEW_SAMPLE_DECISION.json` and `build_sense_review_sample.py` create
  one deterministic blank review record for each observed seven-axis structural
  stratum while retaining raw source spans and null reviewer fields.
- `SENSE_REVIEW_PROTOCOL_2026-10-06.md` defines independent calibration review,
  abstention, disagreement, adjudication, and stop conditions for that package.
- `SENSE_CALIBRATION_DECISION.json` and `build_sense_calibration.py` select a
  deterministic blank dual-review calibration tranche; the generated receipt
  and worksheet remain test-only and contain no semantic judgments.
- `validate_sense_calibration_review.py` verifies source identity, reviewer
  fields, allowed review statuses, and the test-only authority boundary without
  assigning or adjudicating meaning.
- `export_sense_reviewer_packets.py` emits separate deterministic blank packets
  for reviewer A and reviewer B, with a manifest proving shared source evidence
  while excluding the other reviewer’s fields and adjudication.
- `WORD_UNIVERSE_MODEL.md` defines how past attestations, present senses, roots,
  fragments, derivations, and explicitly generated future possibilities remain
  connected without collapsing their truth states.
- `RECONSTRUCTION_MODEL.md` defines root, etymology, derivation, meaning,
  scoped translation equivalence, faceted historical aboutness, and deferred
  geist with their truth-state boundaries.
- `validate_source_map.py` checks identifiers, references, admission states,
  relation kinds, and the generated-only geist boundary.
- `tests/test_source_map.py` supplies positive and negative regression tests.

## Current boundary

No external dataset is downloaded, queried in bulk, decomposed, copied, or
redistributed by this track. `admitted_for_mapping` means that the source may
inform the research map under its recorded terms. It does not authorize later
content ingestion or publication. Each future adapter requires its own exact
version, hash, field-level purpose, license evidence, and acceptance decision.

The current research priority is sense-scoped aboutness: subject, domain,
operation, quality, object, period, and register. Thus a usage cluster can be
proposed as concerning sociology, or an occurrence can be related to mapping
and precision, without asserting that every sense of the spelling has those
properties. Historical dictionaries, thesauri, encyclopedias, catalogs, and
newspapers are treated as dated classification/context evidence. Geist remains
the lowest-priority, generated layer.

Run the local structural checks from the package root:

```powershell
python -B .\development\generative-relational-lexicon\validate_source_map.py
python -B .\development\generative-relational-lexicon\analyze_initial_mining.py
python -B .\development\generative-relational-lexicon\run_tier_zero_pilot.py
python -B .\development\generative-relational-lexicon\query_word_history.py precision mapping identity
python -B .\development\generative-relational-lexicon\compare_roget_oewn.py
python -B .\development\generative-relational-lexicon\audit_surface_normalization.py
python -B .\development\generative-relational-lexicon\audit_unresolved_shapes.py
python -B .\development\generative-relational-lexicon\build_review_sample.py
python -B .\development\generative-relational-lexicon\review_sample_dispositions.py
python -B .\development\generative-relational-lexicon\measure_parser_repair.py
python -B .\development\generative-relational-lexicon\validate_sense_aboutness.py
python -B .\development\generative-relational-lexicon\build_sense_review_sample.py
python -B .\development\generative-relational-lexicon\build_sense_calibration.py
python -B .\development\generative-relational-lexicon\validate_sense_calibration_review.py
python -B .\development\generative-relational-lexicon\export_sense_reviewer_packets.py
python -B -m unittest discover -s .\development\generative-relational-lexicon\tests -v
```
