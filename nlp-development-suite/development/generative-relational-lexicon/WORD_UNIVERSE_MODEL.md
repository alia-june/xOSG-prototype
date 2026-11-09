# Word universe temporal model

Status: generated architecture proposal. It does not make any source claim,
accept a lexical canon, authorize production, or turn projections into facts.

## Objective

The system is intended to represent a word universe rather than a conventional
dictionary. Its graph must support words and fragments across past, present,
and possible future usage while preserving derivation, uncertainty, competing
accounts, language contact, grammar, sound, translation, and conceptual
relations.

No source is the universe. Each source supplies bounded evidence coordinates.
Roget, for example, supplies one historical classification lens that can help
form questions about a modern word; it does not define the word for all time.

## Temporal strata

### Past: attested evidence

Past records retain the exact artifact, date or date range, edition, language,
variety, register, source span, and transcription history. They may record a
form, category placement, derivation claim, usage, translation, grammatical
feature, or relation. A later electronic addition to an old work remains dated
to the electronic artifact unless its earlier origin is independently proven.

### Present: current evidence and synthesis

Present records combine current usage evidence, reviewed lexical relations,
and historical candidates without erasing their dates. A modern sense is a
reviewed, versioned node supported by evidence; it is not obtained merely by
copying a historical heading or accepting a co-occurrence.

### Future: generated possibility

Future records describe possible coined forms, new compounds, predicted sense
extensions, domain transfers, and compositional meanings. Their truth state is
always `GENERATED_PROJECTION` until later evidence establishes actual use.
Every projection retains its generating rules, parent fragments or senses,
constraints, confidence, contradictions, and generation time.

## Core objects

- `FORM`: an observed or generated written or spoken form;
- `FRAGMENT`: a proposed reusable substructure such as a root, stem, affix,
  sound pattern, or independently induced component;
- `LEXEME`: a language- and variety-scoped lexical unit;
- `SENSE`: a time-, community-, domain-, and register-scoped meaning node;
- `USAGE`: an attested occurrence with a source span;
- `DERIVATION`: a typed construction or historical pathway;
- `CATEGORY_PLACEMENT`: a source's organization of a term under a heading;
- `TRANSLATION_RELATION`: a directional, sense-scoped correspondence;
- `GRAMMAR_EVIDENCE` and `PHONOLOGY_EVIDENCE`: source-scoped structural facts;
- `PROJECTION`: a generated possible form, sense, or relation.

## Temporal relations

- `ATTESTED_AS`: source evidence for a form, sense, or usage;
- `PLACED_UNDER`: historical or current category membership;
- `CONTINUES_AS`: evidence-supported continuity between time-scoped nodes;
- `DIVERGES_INTO`: supported semantic or formal branching;
- `BORROWED_FROM`, `CALQUED_FROM`, and `INHERITED_FROM`: competing typed
  historical paths rather than one generic ancestry edge;
- `DERIVED_FROM` and `COMPOSED_OF`: synchronic or diachronic construction;
- `TRANSLATES_TO`: directional and scope-limited translation evidence;
- `PROJECTS_TO`: a generated future possibility, never an attestation.

## Historical-to-modern interpretation

For a modern word lookup, the engine may return:

1. exact historical form occurrences;
2. the categories and parts of speech under which they appeared;
3. dated derivation and etymology claims;
4. continuities and conflicts with current evidence;
5. missing periods, communities, registers, and languages;
6. generated modern sense candidates that require review;
7. separately labeled future projections.

Absence from a historical source does not mean that the word or concept did
not exist. Presence in a mixed electronic edition does not prove presence in
the nominal historical edition.

Before proposing a semantic explanation, the engine records discrepancy
shapes between historical and modern evidence: exact-form absence,
part-of-speech overlap, historical category dispersion, modern sense
multiplicity, and one-to-many or many-to-many pressure. These are diagnostic
measurements, not claims that either source is wrong or that semantic change
caused the observed structure.

Surface reconciliation proceeds in recorded layers: exact dictionary-indexed
forms, Unicode compatibility, punctuation harmonization, separator-to-space,
and loose separator elision. The first successful layer and its collision risk
are preserved. A transformed surface hit remains a candidate and cannot silently
become a lexical identity or semantic equivalence.

Candidates still unresolved after surface reconciliation are partitioned only
by visible structure. Reference-marker, delimiter, numeric, single-token,
multi-token, and residual shapes create separate proposal-only review queues.
The queue label does not decide lexical validity, extraction error, citation
status, obsolescence, or cause.

Before parser changes, a deterministic sample is drawn from every visible
shape/POS stratum and paired with its pinned raw source block. Review
disposition and notes remain null until independently examined.

Review dispositions distinguish demonstrated parser-boundary capture, literal
raw-source occurrence without a listed defect, and unresolved transformation.
Only defect patterns repeated within the pinned sample may become proposed
regression guards; proposals do not authorize parser repair.

An authorized repair pins its pre-change commit, runs failing regressions,
regenerates every dependent artifact, and records full-corpus deltas separately
from diagnostic sample observations.

## Admission sequence

```text
source artifact
  -> immutable evidence record
  -> time-scoped normalized candidate
  -> competing relation graph
  -> reviewed present sense
  -> generated future projection
```

Skipping a stage is invalid. In particular, neither historical category
placement nor a generated projection can silently become a modern definition.
