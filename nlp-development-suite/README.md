# DEFUNCT: Matched-Signal Lexicon Reference Build

## An ethical framework for using Roget, UniMorph, Open English WordNet, and Wiktionary in deterministic NLP

**Project:** NLP Development Suite  
**Former research lane:** Roget derivation-signal measurement  
**Status:** **DEFUNCT AS A GROWTH PATH — PRESERVED AS HISTORICAL EVIDENCE**  
**Authority:** verified internal test result; not production, publication authority, accepted lexical canon, an upstream submission, or permission to merge source content  
**Date:** 2026-11-13

## Retirement notice

On 2026-11-13 the user retired the Roget matched-signal lane and the proposed
collaborative-dictionary fold-back path. The project will not use this work to
grow the first-party lexicon, prepare upstream contributions, or justify mining
collaborative lexical resources. Existing scripts, reports, receipts, tests,
and hashes remain only so the research and its retirement can be audited.

The closing recalculation did not erase the measured association: 7,354 of
12,355 eligible Roget/UniMorph rows shared a Roget head (59.5225%); the
410-pair recorded sample rate was 54.3902%; and the stricter diagnostic control
rate was 4.1463%, for a descriptive lift of 13.117647. The controls remain
imperfect and the numbers establish neither semantic derivation nor cause. The
lane is retired regardless of this numerical signal.

The 410 recorded pairs and 410 controls were deliberately a conservative,
disputable, non-authoritative sample. Its scale was chosen so that the same
kind of source lookup and comparison could theoretically be done by one
careful person by hand over roughly a year. That is a human-legibility
principle, not a claim that such a manual replication occurred or that manual
work would be authoritative. Automation supplied speed and reproducibility,
not semantic standing.

The successor direction is human reading of progressively later,
item-verified public-domain works without lexical harvesting. The resulting
language is expected to be idiosyncratic, archaic, and historically uneven.
Where inherited language is insufficient, new words may be coined ad hoc, but
every coinage must remain visibly generated rather than represented as
attested or standard.

The readable public explanation is
[`RETIREMENT_RECORD.md`](review/roget-growth-retirement-2026-11-13/RETIREMENT_RECORD.md).
The binding machine-readable decision remains local pending external
verification.
All continuation, contribution, fold-back, and future-research language below
is retained as historical context and is superseded by that decision.

## Meaning, growth, and closure

Is there meaning in what we did? **Yes and no.**

The experiment has meaning as a bounded observation and as a record of a route
we examined. It also helped reveal the method's own limit. Any meaning
extracted from a prepared source remains limited by that source: its selection,
categories, absences, period, editorial history, and assumptions. More
extraction cannot, by itself, remove that inheritance.

We therefore want a different route—an organic and everyday route developed
through sustained encounter with everyday sources. Extracted language and
grown language are not the same thing. Extraction asks what structures can be
recovered from material already organized by someone else. Growth includes the
slower work of reading, use, misunderstanding, reconsideration, forgetting,
recombination, and invention. Its meaning arises through an ongoing
relationship rather than from the size of a harvested collection.

Growth also requires material to be decomposed: absorbed, questioned, broken
apart, and allowed to become something different. Legal access does not always
give us the moral access required for that relationship. Where we cannot
confidently claim such moral access, we will leave the material intact rather
than treat availability or an open license as an obligation to consume it.

Our preferred organic route is to travel a common road down history: encounter
past works in sequence, understand later language in relation to earlier
language, and let that accumulated reading alter the system slowly. That route
depends on access we can defend both legally and morally. We will not force a
continuous historical account where the necessary material is unavailable to
us on those terms.

When we cannot learn responsibly from the past sources needed to travel that
common road, we will induct from public-education sources. Induction here means
learning general forms, distinctions, vocabulary, and relationships from
materials prepared for shared education, then testing what we have understood
through ordinary use. It does not mean scraping textbooks, copying curricular
content into a database, or treating an educational source as unrestricted
merely because it serves the public. Each source retains its own provenance,
access conditions, and rights boundary.

Public-education sources therefore provide an alternate common road—not proof
of final meaning and not a claim of institutional endorsement. They allow the
project to rejoin knowledge intended for broad learning when direct historical
growth is unavailable, while keeping the resulting interpretation
non-authoritative and open to correction.

This choice does not promise a more complete language. The resulting language
may remain partial, idiosyncratic, archaic, ordinary, and peculiar to its path
of reading and use. Those qualities are not failures to disguise. They are
conditions of the route we have chosen.

Nor must the project succeed. It is not required to produce a comprehensive
lexicon, prove a theory, or arrive at a predetermined system. Research can
close an avenue without replacing it. Learning that we should not proceed is
itself a legitimate result. The retired experiment therefore matters partly
because it marks a boundary: this is an avenue we explored, understood more
clearly, and chose to close.

## Former intended outcome: contribute upstream — superseded

The intended outcome of this work is to identify small, well-supported lexical
improvements that may be offered back to UniMorph, Open English WordNet,
Wiktionary, or another appropriate upstream project **under that project's
license, contributor terms, technical format, and community review process**.

This repository was a **Reference Build**. It was intended to sit here for review while its
method, evidence, licensing, controls, and proposed contribution path are
examined. It is not an upstream patch, pull request, wiki edit, or claim that an
upstream community has accepted any result.

We are outsiders to the communities that created and maintain these lexical
resources. Their contributors have supplied the scholarship, editorial labor,
software, community knowledge, and long-term stewardship on which this study
depends. We approach their work with respect and with the limited standing of
an informatics student: to learn from their methods, test a transparent idea,
document mistakes and uncertainty, and offer useful work back without claiming
ownership or authority over their projects.

Upstream maintainers and contributors—not this Reference Build—decide whether
a proposed improvement is accurate, useful, appropriately licensed, in scope,
and suitable for inclusion. Rejection, correction, or a request to redesign the
work is a valid and valuable outcome.

### Two-document publication boundary

The online update publishes **this README and the retirement explanation
only**. The machine-readable retirement decision, retirement manifest, current
measurement script, authorization decision, generated pair records, reports,
receipts, probe, and regression tests remain in the local Reference Build
pending external verification. They are not included in the online suite by
this update.

Accordingly, the measurements below report the verified local Reference Build
but are not independently reproducible from the present online checkout. No
code, lexical data, generated evidence bundle, license bundle, or upstream
submission is published or implied by this two-document change.

## Abstract

This research asks a narrow question: **can historical Roget co-heading serve as
a useful structural signal when investigating English word derivation?**

The experiment does not ask Roget to prove derivation. Instead, it compares
exact Roget category co-membership with independently recorded derivational
pairs from UniMorph. Open English WordNet (OEWN) supplies modern lemma,
part-of-speech, and sense coordinates. A pinned local English Wiktionary
extraction supplies only etymology-field availability, hashes, and a mechanical
source-token mention signal. Deterministic matched controls provide a baseline.

The completed test sampled 410 UniMorph-recorded pairs across 25
part-of-speech signatures and 410 matched controls. Of the recorded pairs, 223
shared at least one exact Roget head (54.39%); 9 matched controls did (2.20%).
The observed rate difference was 52.20 percentage points and the descriptive
rate lift was 24.78. This is evidence that Roget co-heading may be a useful
research feature. It is **not** evidence that Roget proves derivation,
etymological lineage, root identity, semantic continuity, or cause.

The larger ethical question is what happens next. A signal produced from open
lexical sources can easily be laundered into an apparently authoritative
dictionary claim. This project therefore treats every source as independent
evidence, preserves collisions and provenance, prohibits silent merging, and
requires review before any result can be contributed back to the appropriate
upstream lexical project under that project's license and contribution rules.

## Research question

The working hypothesis is:

> Exact Roget co-heading may be a measurable structural signal for
> independently recorded English derivation pairs.

The hypothesis is deliberately weaker than any of the following claims:

- words in one Roget head are morphologically related;
- a UniMorph relation is etymological proof;
- an OEWN sense identifies the historically intended Roget sense;
- a Wiktionary etymology mention establishes lineage;
- agreement among sources establishes truth;
- absence from a source establishes novelty or nonexistence.

The distinction matters. A thesaurus organizes conceptual neighborhoods. A
morphological dataset records formal relations. A wordnet organizes lexical
senses and semantic relations. A collaborative dictionary records broader
lexical and etymological material. Their overlap can produce useful questions,
but their functions are not interchangeable.

## Source roles and ethical boundaries

| Source | Role in this test | Recorded rights basis | What it may not become silently |
|---|---|---|---|
| Project Gutenberg Roget Ebook 22 | Historical category membership and exact source spans | Pinned electronic artifact treated as public-domain material in the USA, with Project Gutenberg notice, trademark, and jurisdiction cautions retained | A timeless definition, a pure 1911 transcription, or proof of derivation |
| UniMorph English | Recorded directed derivation pairs, POS signatures, and affix labels | CC BY-SA 3.0; pinned revision and file hash | A complete gold standard, etymological proof, or evidence that an unrecorded pair is unrelated |
| Open English WordNet 2025 | Exact modern lemma, POS, entry, and sense identifiers | CC BY 4.0 plus preserved Princeton WordNet notice; pinned database hash | Automatic historical sense selection or evidence of derivational lineage |
| English Wiktionary via Kaikki | Etymology-field availability, field hashes, and mechanical source-token mentions | Local manifest records CC BY-SA 3.0 and GFDL; exact-dump redistribution terms require separate review | Unattributed prose, automatically accepted etymology, or permission to relicense extracted content |
| Other attached dictionaries | Backup coverage, disagreement detection, review evidence, and source-specific contribution targets | Source-specific; container formats do not determine content rights | A merged anonymous “consensus dictionary” or a way to move incompatible content between projects |

Licensing is a minimum condition, not an ethical conclusion. Openly licensed or
public-domain material can still contain historical prejudice, transcription
errors, culturally narrow classifications, obsolete labels, or misleading
claims. Conversely, a useful source cannot be ingested merely because it is
easy to download or packaged in an open-source format.

The local Wiktionary license record and the current source-register description
are not treated as automatically identical. Until the exact extraction's
applicable terms are reconciled, this project may analyze pinned local fields
under the recorded test boundary but must not assume unrestricted republication
or license compatibility with every downstream dictionary.

## Method

### 1. Freeze source identity

Every comparator is pinned by release or revision, byte count, SHA-256, role,
and recorded license. The Roget parser output is accepted only when its receipt
matches the pinned source artifact and parser version.

### 2. Form the positive population

UniMorph directed derivation rows are normalized by Unicode case folding. A row
is eligible when both forms have exact entries in the pinned Roget membership
output. Duplicate source-target-POS-affix rows are collapsed deterministically.

### 3. Draw a deterministic stratified sample

Eligible rows are separated by UniMorph part-of-speech signature. Rows in each
stratum are ordered by a reproducible SHA-256 key, and up to 24 are selected.
The current run contains 410 recorded pairs across 25 observed signatures.

### 4. Construct matched controls

Each recorded pair receives one deterministic control. The source form and
target POS signature are retained, while the target is replaced with another
Roget-covered target not recorded as a directed UniMorph derivation from that
source.

A control is therefore **unrecorded in the pinned UniMorph file**, not known to
be unrelated. It may represent an omitted relation, another kind of relation,
or a chance semantic association.

### 5. Measure the Roget signal

The measured feature is binary: do the source and target forms share at least
one exact Roget head? Every record retains all contributing Roget memberships,
head identifiers, headings, source line ranges, and source hash.

### 6. Attach modern coverage without selecting a meaning

OEWN contributes exact lemma, POS, entry, and sense identifiers. Definitions
and examples are excluded. No OEWN sense is selected as the intended historical
sense.

Wiktionary contributes the number of local records, POS labels, the number and
hashes of etymology fields, and whether a target etymology mechanically mentions
the source token. The etymology text itself is not copied into the experiment
output. A token mention is not treated as lineage proof.

### 7. Abstain from semantic confidence

Every pair has `semantic_confidence: null`. The system has no reviewed
calibration set from which to estimate a semantic probability. A transparent
absence of confidence is ethically preferable to an attractive but unsupported
number.

## Archived result and closing recalculation

| Measurement | Result |
|---|---:|
| UniMorph-recorded pairs sampled | 410 |
| Recorded pairs sharing a Roget head | 223 |
| Recorded-pair shared-head rate | 54.39% |
| Matched controls | 410 |
| Controls sharing a Roget head | 9 |
| Control shared-head rate | 2.20% |
| Descriptive rate difference | 52.20 percentage points |
| Descriptive rate lift | 24.78 |
| Recorded pairs with exact OEWN lemmas on both sides | 352 |
| Recorded targets with local Wiktionary etymology fields | 393 |
| Target etymology fields mechanically mentioning the source token | 364 |
| Full eligible Roget/UniMorph rows | 12,355 |
| Full eligible rows sharing a Roget head | 7,354 (59.5225%) |
| Stricter diagnostic controls sharing a Roget head | 17 of 410 (4.1463%) |
| Recorded-minus-stricter-control difference | 50.2439 percentage points |
| Stricter diagnostic descriptive lift | 13.117647 |

Before retirement, the original result supported further investigation of
Roget co-heading as a feature. The closing probe found that the original
controls were poorly matched on spelling similarity. A stricter diagnostic
matched part-of-speech signature, nearest available spelling similarity,
absolute length difference, and target Roget head degree; it reduced but did
not erase the descriptive separation. Even those controls remained less
spelling-similar than the recorded pairs and were not human-verified negatives.

The result does not measure precision, recall, semantic accuracy, fairness, or
etymological correctness. No inferential significance test or completed human
adjudication exists. The 410 recorded pairs and 410 controls are a
conservative, disputable, non-authoritative sample kept at a scale whose class
of comparison could theoretically be performed by one careful person by hand
over roughly a year. No such full manual replication is claimed, and manual
work would not become authoritative merely by being manual.

## Ethical analysis

### Provenance must survive synthesis

The system must never emit an anonymous merged fact such as “the dictionaries
agree.” Each observation retains its source, version, exact record or span,
license, extraction method, and transformation history. If a conclusion depends
on three sources, the three evidence paths remain separately inspectable.

### Apparent agreement may not be independent

Two dictionaries can share upstream material, editorial traditions, imports,
or community contributors. Until source lineage is audited, cross-source
agreement is evidence repetition—not necessarily independent corroboration.
This is especially important when using Wiktionary alongside datasets that may
have learned from, imported, or been compared against collaborative lexical
sources.

The system therefore needs a source-dependency graph. Agreement scores must be
discounted or withheld when upstream independence is unknown.

### Historical classifications are evidence of their edition

Roget heads reflect a particular historical classificatory system transmitted
through a mixed electronic edition containing later additions, rearrangements,
omissions, and transcription defects. The categories are valuable evidence of
organization and association. They are not neutral, universal, or timeless
maps of meaning.

Historical labels that are obsolete, stigmatizing, colonial, medicalized, or
otherwise harmful must retain their period and source context. They must not be
presented as current preferred terminology merely because they appear in a
historical reference work.

### Missingness is not nonexistence

Absence from OEWN may reflect scope, editorial lag, POS policy, spelling,
regional use, specialist use, or a genuinely emerging form. Absence from
UniMorph does not prove that no derivational relation exists. Absence from
Wiktionary does not prove that a community does not use a word.

The only defensible statement is source-scoped: “not observed in this pinned
source under this lookup rule.”

### Backup dictionaries must remain backups

Other dictionaries can fill gaps, reveal conflicts, or supply review context.
They must not be used to overwrite the primary source record or conceal a
collision. The term “backup” means **additional evidence available when a field
is missing or disputed**, not an authority hierarchy that silently picks the
first convenient answer.

### Community language requires community-sensitive review

Emerging terms may concern identity, disability, sexuality, ethnicity,
religion, health, politics, violence, or reclaimed language. Automated systems
can freeze contested meanings, strip self-identification from context, or give
harmful labels an institutional appearance.

Sensitive emergent-word candidates require:

- dated and community-scoped evidence;
- separation of self-designation, external designation, and slur usage;
- register and reclamation status where supported;
- visible disagreement and competing definitions;
- review by people familiar with the affected language community;
- correction, deprecation, and appeal paths;
- no inference about an individual from their vocabulary.

### Open data does not waive privacy

Dictionary records are generally less privacy-sensitive than raw usage logs,
but emergent-word research often turns toward forums, chats, search queries, or
social media. Public visibility does not automatically make individual-level
collection ethical.

Future usage-corpus work should prefer aggregate counts, minimum-frequency
thresholds, source-level time buckets, and deletion of personal identifiers.
Private communications, deleted material, and vulnerable-community spaces
require separate authority and review.

## Retired proposal: safe folding back into upstream dictionaries

> **Superseded:** no fold-back or upstream contribution will proceed from this
> lane. This section is preserved to show the former proposal and its safeguards.

The intended outcome is reciprocal: where review finds a genuine correction,
coverage improvement, or relation that belongs in an upstream project, the
project should offer that improvement back under the upstream project's
license. “Fold back” means a source-specific contribution submitted through the
upstream project's normal governance process. It does not mean publishing a
blended database and declaring its contents compatible with every input.

Because we are not members or representatives of these upstream communities,
we must begin by listening: read their contribution documentation, ask where
necessary, use their vocabulary and data model, respect maintainer time, and
submit the smallest useful change. The Reference Build remains here for review
until those prerequisites are satisfied. No community owes this project review,
adoption, endorsement, or support.

Matched-signal results may inform upstream dictionaries only through a staged,
reversible evidence pipeline:

```text
pinned source records
        ↓
source-specific observations
        ↓
matched-signal candidate
        ↓
conflict and dependency analysis
        ↓
independent human review
        ↓
accepted first-party relation or upstream-specific patch, or rejection/abstention
        ↓
upstream review and separately recorded acceptance, rejection, or revision
```

### Upstream contribution covenant

For every proposed fold-back:

1. **Choose one upstream target.** A UniMorph relation, an OEWN sense change,
   and a Wiktionary etymology edit are different contributions with different
   schemas, editorial standards, and licenses.
2. **Reconstruct the contribution from eligible evidence.** Do not copy prose,
   relation rows, examples, or editorial judgments from another source whose
   license or contribution terms are incompatible with the target.
3. **Use the target's license.** Project-authored additions intended for
   UniMorph are offered under its applicable CC BY-SA terms; OEWN-targeted work
   is offered under OEWN's applicable attribution terms; Wiktionary-targeted
   edits follow the contribution terms and licenses in force on Wiktionary at
   the time of contribution.
4. **Preserve attribution and evidence internally.** Even when an upstream
   accepts a concise patch, the project retains the full provenance ledger,
   source versions, hashes, review record, and license analysis.
5. **Do not imply acceptance.** A generated patch, pull request, or wiki edit is
   a proposal until the upstream authority accepts it. Upstream rejection is a
   valid research result and remains recorded.
6. **Respect share-alike boundaries.** If a contribution incorporates material
   governed by share-alike terms, its distribution and adaptation obligations
   must be satisfied. Rephrasing content does not automatically remove those
   obligations.
7. **Keep incompatible evidence out of the patch.** An observation can motivate
   investigation without supplying redistributable content. When rights are
   unclear, cite the gap internally and abstain from upstream submission.

The contribution unit should be the smallest reviewable change: one relation,
one form, one sense distinction, one correction, or one source-scoped note.
Bulk synchronization is prohibited until field-level license compatibility,
source dependence, and upstream consent are established.

### Source layer

Source records are immutable evidence. They remain under their original source
identifier and license. Corrections are represented as new observations, not
destructive edits to historical input.

### Candidate layer

A candidate may state that a relation is worth reviewing. It must include:

- source and target forms;
- proposed relation type and direction;
- exact supporting and contradicting evidence references;
- source-dependency status;
- time, language variety, domain, and register when known;
- generation method and version;
- `semantic_confidence: null` until calibrated;
- review status and explicit abstention reason;
- no execution or canon authority.

### Review layer

Reviewers assess the source evidence without being shown a generated conclusion
as if it were ground truth. Disagreement is retained. Adjudication is separate
from initial review. A rejected candidate remains recorded so it is not
reintroduced repeatedly by later pipeline runs.

### Accepted layer

An accepted relation becomes a first-party, versioned statement with its own
scope, evidence references, reviewer authority, conflicts, superseded values,
and rollback history. It does not erase the source records from which it was
derived and does not inherit a more permissive license by being rewritten.

If the intended destination is an upstream dictionary, local acceptance only
authorizes preparation of a source-compatible contribution. Canonical upstream
status begins only when that upstream accepts the change through its own
process. The local ledger records the submitted patch, terms offered, upstream
identifier, disposition, accepted revision if any, and any later supersession.

### Feedback-loop prevention

Once a generated or accepted relation is contributed to an upstream dictionary,
it must carry a project-origin marker in the local ledger. A later run may not
count that accepted upstream contribution as independent external confirmation.
Otherwise the system can create a self-reinforcing loop: generate a candidate,
contribute it upstream, re-import it in the next release, and mistake its return
for corroboration.

Recommended controls are:

1. immutable origin identifiers;
2. source lineage and import/export ledgers;
3. holdout sources never used for generation;
4. temporal cutoffs that prevent future exports from entering past baselines;
5. duplicate-content and provenance matching;
6. independent review before promotion;
7. periodic audits for circular evidence.

## Superseded proposal: emergent-word research

The matched-signal architecture can help investigate emerging words, but the
current dictionary stack cannot by itself prove that a word is new. An
emergence claim requires dated usage evidence.

A responsible emergent-word lane should distinguish:

- **newly observed:** first seen by this pipeline at a recorded date;
- **new to a source:** absent from an earlier release and present in a later one;
- **new form:** a productive inflection or derivation of an established form;
- **new sense:** an established spelling used with a distinguishable meaning;
- **new register or community use:** an older form adopted in a new context;
- **rediscovered or revived:** historically attested but newly visible again;
- **unknown:** evidence is insufficient to classify the change.

Wiktionary may provide earlier coverage of community language than slower
curated sources, but edit recency is not proof of linguistic birth. OEWN can
help expose sense gaps. UniMorph can identify whether a form fits a recorded
morphological relation. Historical dictionaries can reveal apparent “new” words
that are actually revivals. Dated corpora are still required to test emergence.

No emergent term should be promoted solely because it is frequent, surprising,
or absent from a conventional dictionary. The system should report evidence
and uncertainty, not decide which language is legitimate.

## Cancelled next research gates

The following gates were required by the former roadmap. They are preserved as
historical review criteria, not as an active work queue.

1. **Source-dependency audit** — determine whether comparator agreement is
   independent or inherited.
2. **Improved controls** — match spelling distance, length, frequency,
   productivity, and Roget head degree in addition to POS.
3. **Blind human calibration** — review a bounded sample before assigning any
   semantic confidence or threshold.
4. **Holdout evaluation** — test candidates against a source not used in
   generation.
5. **Temporal evaluation** — use dated releases and corpora to separate
   emergence, revival, and editorial lag.
6. **License compatibility review** — resolve exact-dump Wiktionary terms and
   define field-level redistribution rules before publication.
7. **Sensitive-language protocol** — add community review, harm labels,
   correction paths, and privacy limits before mining social usage.
8. **Fold-back ledger** — prevent exported project claims from returning as
   apparently independent evidence.
9. **Upstream contribution profiles** — record each project's current license,
   contributor terms, schema, review channel, attribution format, and accepted
   patch granularity before preparing submissions.

## Archival local reproduction

The commands in this section apply to the complete local Reference Build. The
required current-work files are deliberately absent from the README-only online
publication.

Set the shared lexical data root on the original Windows machine:

```powershell
$env:LEXICON_DATA_ROOT = Join-Path $PWD 'lexicon-data'
```

Run the deterministic measurement from the suite root:

```powershell
python -B .\development\generative-relational-lexicon\measure_roget_derivation_signal.py
```

Run the focused regression tests:

```powershell
python -B -m unittest discover `
  -s .\development\generative-relational-lexicon\tests `
  -p 'test_derivation_signal.py' -v
```

Run complete relational-lexicon discovery with the prepared environment because
the sense-aboutness contract requires `jsonschema==4.26.0`:

```powershell
& '..\.venv\Scripts\python.exe' -B -m unittest discover `
  -s .\development\generative-relational-lexicon\tests -v
```

The current prepared-environment result is 99 passing tests. The generated pair
records are byte-stable across repeated runs.

## Evidence and implementation

The following current-work artifacts are held in the local Reference Build and
are **not published by this two-document update**:

- `development/generative-relational-lexicon/ROGET_DERIVATION_SIGNAL_DECISION.json`
- `development/generative-relational-lexicon/measure_roget_derivation_signal.py`
- `development/generative-relational-lexicon/pilot/derivation-signal/`
- `development/generative-relational-lexicon/tests/test_derivation_signal.py`

The online suite already contains these background materials:

- [Relational reconstruction model](development/generative-relational-lexicon/RECONSTRUCTION_MODEL.md)
- [Source and rights register](development/generative-relational-lexicon/SOURCE_REGISTER.md)
- [Coverage ledger](production/COVERAGE_LEDGER.csv)
- [Recorded failures and corrections](production/ERROR_LOG.md)
- [Suite orientation](README_FIRST.md)
- [External data boundaries](DATA_DEPENDENCIES.md)

## Retirement conclusion

The closing probe preserves a measurable association and also preserves its
limits. Neither result governs the decision. The Roget collaborative-growth
path is defunct because this project declines to treat license permission alone
as sufficient relationship permission for mining, transforming, and folding
work into living lexical communities, and because obtaining and carrying the
additional explicit permission is too high a burden for this project.

The next lexicon will therefore not claim comprehensive modern coverage or
dictionary consensus. It will develop slowly from human reading of
item-verified public-domain works, moving chronologically toward later works as
rights permit. It will preserve the reader's interpretation separately from
the work itself, avoid automated harvesting, disclose its archaic and
idiosyncratic character, and mark every ad hoc coinage as generated.

The former contribution framework remains in this file solely as an audit
trail. It is not a dormant roadmap and cannot be resumed by completing its old
gates. Reactivation would require a new explicit canon decision.
