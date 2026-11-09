# Relational reconstruction and historical aboutness model

Status: generated design proposal. No lexical claim produced under this model is
accepted canon merely because the pipeline emits it.

## Distinct dimensions

### Root

A root record identifies an attested or reconstructed form proposed as an
ancestor or structural base. Reconstructed forms must be visibly marked and
must never be presented as directly observed strings.

### Etymology

An etymology record is a path of typed historical claims. It distinguishes
inheritance, borrowing, calque, learned formation, semantic influence,
uncertain transmission, and competing accounts. A language-family edge cannot
serve as proof of a word-level etymology.

### Derivation

A derivation record describes a synchronic or diachronic construction from
fragments or lexemes. It can preserve several segmentations, transformations,
and exceptions. Formal resemblance alone produces a candidate, not a fact.

### Phonology

A phonology record describes a source-scoped sound inventory, feature, or
proposed transformation. It retains the particular variety, inventory source,
notation, and time scope. Similar sound shapes can generate candidates but do
not establish cognacy, borrowing, or meaning.

### Grammar

A grammar record describes a language- or construction-scoped morphological or
syntactic feature. Typological coding helps detect assumptions built around
English, but a language-level feature cannot be silently assigned to every
lexeme, speaker, register, or historical period.

### Meaning

A meaning record is a first-party concept node supported by sense evidence,
usage evidence, contrasts, and relations. Source glosses are evidence objects
or coverage observations; they are not silently copied into the first-party
definition.

### Translation equivalence

A translation relation joins a source sense or usage cluster to a target sense
or usage cluster for a stated domain, period, register, and direction. It is
evidence of a usable correspondence in that scope—not proof that the two words
have identical meanings, histories, connotations, or grammatical behavior.

Dictionary headword pairs without sense identifiers remain translation
candidates. Sentence alignments may help induce the missing sense clusters,
but a parallel sentence does not establish synonymy or etymology. Human,
interpreted, machine-generated, and automatically mined translations must be
distinguished.

### Aboutness

Aboutness records what a particular **sense or historical usage cluster** is
about without copying or attempting to replace a definition. It must not be
attached permanently to an orthographic word. The same spelling can have
unrelated senses, domains, and histories.

Aboutness is faceted rather than flattened into one label:

- `subject`: sociology, cartography, kinship, navigation;
- `domain`: a discipline, craft, institution, or community of practice;
- `operation`: mapping, measuring, classifying, comparing;
- `quality`: precision, uncertainty, scale, reliability;
- `object`: the entity or phenomenon being discussed;
- `period`: the dated interval supported by the evidence;
- `register`: technical, legal, colloquial, journalistic, archaic;
- `source_context`: reference-work section, catalog subject, article context,
  or another traceable evidence location.

For example, one sense candidate for `mapping` may concern the domain of
cartography and the operation of spatial representation. Another may concern
mathematics or computing. A context containing `precision` may support the
quality facet `precision`, but it does not make every sense of the word a
precision concept.

Every aboutness assertion retains one of four non-interchangeable states:

- `SOURCE_SUBJECT_LABEL`: a label directly supplied by a catalog, heading, or
  source structure;
- `DERIVED_CONTEXT_CLUSTER`: a reproducible result from dated contexts;
- `GENERATED_CLASSIFICATION`: a system-proposed facet or topic;
- `ACCEPTED_TOPIC_MAPPING`: a reviewed mapping explicitly accepted for its
  declared scope.

Old dictionaries, thesauri, and encyclopedias are useful here as dated maps of
classification and vocabulary. Their placement of a term under a heading is
historical evidence about organization and association, not proof that the
classification is correct now. Newspaper archives add usage and register
evidence, but OCR error, editorial bias, geography, and date coverage must stay
attached to the result.

### Geist

Geist is a generated synthesis over time-aware meaning, register, cultural
association, metaphor, contrast, and colexification evidence. It must include:

- a declared time and community scope;
- supporting and contradicting evidence references;
- a generation method and version;
- explicit uncertainty;
- no claim of being a directly sourced psychological or cultural essence.

Geist may be `GENERATED_SYNTHESIS` or a reviewed proposal. It may never enter
the source-fact field.

Geist is deliberately the lowest-priority dimension. It remains deferred until
the more testable root, lineage, phonology, grammar, meaning, aboutness, domain,
operation, quality, period, and register layers have usable evidence and
negative controls.

## Reconstruction object

```json
{
  "form": "example",
  "language": "modern-english",
  "root_candidates": [],
  "etymology_paths": [],
  "derivation_candidates": [],
  "phonology_evidence": [],
  "grammar_evidence": [],
  "temporal_evidence": {"past": [], "present": [], "future": []},
  "meaning_candidates": [],
  "translation_candidates": [],
  "sense_usage_clusters": [],
  "aboutness_assertions": [],
  "geist_proposals": [],
  "future_projections": [],
  "coverage_observations": [],
  "gaps": [],
  "conflicts": [],
  "truth_state": "GENERATED_SYNTHESIS"
}
```

An aboutness assertion has this minimum shape:

```json
{
  "sense_or_usage_cluster_id": "required-not-a-bare-spelling",
  "facet": "domain | operation | quality | subject | object | period | register",
  "topic": "generated-or-controlled-topic-identifier",
  "truth_state": "SOURCE_SUBJECT_LABEL | DERIVED_CONTEXT_CLUSTER | GENERATED_CLASSIFICATION | ACCEPTED_TOPIC_MAPPING",
  "time_scope": {"start": null, "end": null},
  "community_scope": null,
  "evidence_refs": [],
  "method": null,
  "confidence": null,
  "contradictions": []
}
```

## Required separation

The system must not collapse:

- language genealogy into word genealogy;
- cognacy into direct descent;
- borrowing into inheritance;
- orthographic similarity into shared root;
- phonological similarity into cognacy;
- a language-level grammatical feature into a property of every lexeme;
- colexification into identity of meaning;
- a translation pair into meaning identity or shared etymology;
- a headword-level translation into equivalence across every sense;
- machine-mined alignment into human translation;
- a source gloss into our definition;
- a source subject heading into an accepted topic mapping;
- a label on one sense into a property of every homograph or polyseme;
- an obsolete classification into present-day truth;
- OCR co-occurrence into semantic identity;
- absence from a source into global nonexistence;
- generated geist into historical fact.
- a future form or meaning projection into present usage or historical fact.

## First reconstruction gate

The first executable slice should accept a small, user-reviewed list of modern
English forms and emit only:

1. source-capability and coverage questions;
2. candidate language routes;
3. explicit missing evidence;
4. no external definitions or examples;
5. no accepted etymology;
6. proposed, sense-scoped aboutness with its evidence state visible;
7. no accepted topic mapping until a controlled-topic review passes;
8. no generated geist until the underlying time-aware evidence schema passes
   review.

This makes missingness the first product and reconstruction the later,
reviewable product.
