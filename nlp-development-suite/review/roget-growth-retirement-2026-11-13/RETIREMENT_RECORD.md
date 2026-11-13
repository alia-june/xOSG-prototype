# Roget research branch closure record

Date: 2026-11-13  
Decision: `RLX-ROGET-RETIREMENT-001`  
Truth state: **ACCEPTED CANON FOR DEVELOPMENT**  
Suite status: **ACTIVE — NLP IS ALIVE AND WELL**  
Branch status: **CLOSED AS A GROWTH PATH**

Publication boundary: this explanation and the project README may be published
for external review. The machine-readable decision, manifest, probe, code,
data, reports, receipts, and tests remain local pending external verification.
This explanation does not make the withheld evidence independently
reproducible from the public repository.

## Scope erratum

An earlier public heading used **DEFUNCT** without placing the branch boundary
first. It could therefore be misread as declaring the NLP Development Suite—or
NLP itself—defunct. That was not the decision.

The NLP Development Suite remains active. Only the Roget matched-signal and
collaborative-dictionary growth research branch is closed. The deterministic
NLP system, parsers, command front end, lexical exploration tools, and other
research branches continue under their own status and evidence boundaries.
This correction does not reactivate the closed branch or authorize release of
the supporting artifacts held for external verification.

## Outcome

The project retires the Roget matched-signal lane and the proposed path of
growing a lexicon by mining collaborative dictionaries and folding candidate
changes back into them. The experiment remains preserved as historical,
non-authoritative research evidence. It is not a roadmap, active feature,
quality score, or contribution queue.

This is an ethical and operational decision, not a finding that open licenses
are invalid. A license can grant legal permission within its terms. This
project nevertheless requires a higher threshold before it mines, transforms,
or returns material to a living collaborative work: explicit, source-specific
confidence that the relationship is welcome, traceable, and governable. The
work needed to obtain and maintain that assurance is too high a burden for this
project. We therefore decline the path.

No upstream community is criticized by this decision. Their licenses,
contribution processes, and stewardship remain their own. The project is
choosing a narrower practice for itself.

## Closing recalculation

The closing numbers come from the reproducible diagnostic in
`../reference-build-2026-11-13/PROBE_RESULTS.json`:

| Measurement | Closing value |
|---|---:|
| Exact Roget/UniMorph eligible rows | 12,355 |
| Eligible rows sharing a Roget head | 7,354 (59.5225%) |
| Recorded sample | 410 pairs |
| Recorded sample sharing a Roget head | 54.3902% |
| Original controls sharing a Roget head | 2.1951% |
| Original descriptive rate lift | 24.778006 |
| Stricter diagnostic controls sharing a Roget head | 4.1463% |
| Recorded-minus-stricter-control difference | 50.2439 percentage points |
| Stricter diagnostic descriptive lift | 13.117647 |

The stricter diagnostic matched part of speech, nearest available spelling
similarity, absolute length difference, and target Roget head degree. It did
not erase the observed association. It also did not cure the design: the
controls remained less spelling-similar than the recorded pairs and were not
human-verified linguistic negatives. These values are descriptive association,
not semantic derivation, cause, accuracy, or permission to contribute.

The lane is retired regardless of the numerical signal.

## Why the sample was bounded

The 410 recorded pairs and 410 controls were chosen as a conservative,
disputable, non-authoritative research sample. The governing scale principle
was human legibility: the same class of source lookup and comparison could
theoretically have been performed by one careful person by hand over roughly a
year. Automation reduced time and made the selection reproducible; it did not
turn the output into authority.

“Could theoretically have been done by hand” is a scale description, not a
validation claim. No person is claimed to have independently repeated all 820
records manually, and one year is not presented as a measured labor estimate.
Manual work would remain contestable as well. Every sampled pair, control,
source coordinate, and interpretation can be disputed, corrected, or rejected.
The sample was meant to expose a question at inspectable scale, not to settle
language.

## Successor direction

The first-party lexicon will grow organically through human reading of
progressively later works that have been individually verified as public
domain for the relevant jurisdiction. “Later” means chronological progression
within the rights-cleared corpus; it does not mean that every later work is
public domain.

The project will learn from works rather than harvest them:

- no dictionary scraping, lexical crawling, or bulk conversion of text into a
  word list;
- no silent import of definitions, category systems, or community judgments;
- bibliographic identity and the reader's dated observations remain separate;
- interpretations are first-party notes, not assertions about what a source or
  speech community authoritatively means;
- a work's rights status is checked item by item and recorded before use.

This produces a deliberately different kind of language system. Its vocabulary
may be idiosyncratic, archaic, historically uneven, and incomplete by modern
dictionary standards. Those properties are disclosed design consequences, not
coverage defects to conceal.

When inherited words are insufficient, the project may coin a word ad hoc.
Every coinage must be marked `GENERATED_COINAGE` and retain its date, authoring
authority, motivating gap, and intended meaning. A coined word is never to be
represented as attested, standard, community-approved, or historically
inherited merely because the system uses it consistently.

## Open-domain boundary

The target is open-source code and openly reusable first-party lexical work.
This decision does not silently place newly authored data under MIT, CC0, or
another instrument. The exact data dedication or license is a separate canon
decision. Until it is recorded, “open-domain” is an intended outcome, not a
completed legal state.

## Preservation and prohibition

Preserve the existing Roget source pins, scripts, reports, receipts, tests,
probe, and hashes so the decision remains auditable. Do not delete or rewrite
them to make the retired path appear never to have existed.

From this decision forward:

- do not run additional Roget-growth experiments without a new explicit
  decision;
- do not use collaborative dictionary content to grow the first-party lexicon;
- do not prepare or send upstream lexical contributions from this lane;
- do not treat prior cross-source agreement as independent confirmation;
- do not publish the local experiment bundle under the retired roadmap;
- do not describe the lane as held, pending, promising, or awaiting permission;
  its growth status is **defunct**.

Read-only preservation, reproducibility checks, criticism, and historical study
remain allowed. They do not reactivate the lane.
