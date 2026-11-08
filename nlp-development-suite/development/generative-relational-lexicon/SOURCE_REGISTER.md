# English source-language evidence register

Status: generated research synthesis dated 2026-10-03. This is not legal
advice, lexical canon, or permission to ingest a dataset.

## Admission classes

- `admitted_for_mapping`: current primary evidence supports using the source to
  describe capabilities, lineage, and gaps. Content ingestion remains a later
  decision.
- `isolated_adapter_only`: useful evidence with reciprocal or source-specific
  terms; it must not silently merge into the first-party core.
- `review_required`: promising source whose exact artifact, terms, or component
  boundary is incomplete.
- `blocked`: current evidence contradicts admission or leaves a material rights
  conflict.

## Initial source findings

| Source | Principal contribution | Terms finding | Initial disposition |
|---|---|---|---|
| Wikidata Lexemes | roots, derivation links, forms, senses, attestations | Structured Lexeme data is CC0 | admitted for mapping |
| Glottolog 5.3 | language identifiers and genealogical classification | CC BY 4.0 | admitted for mapping |
| IE-CoR | Indo-European cognates, root references, forms, concepts | CC BY 4.0 | admitted for mapping |
| OEWN 2025 | current English senses and semantic relations | CC BY 4.0 plus Princeton notice | admitted for mapping |
| CLICS3 | cross-linguistic colexification patterns | CC BY 4.0 | admitted for mapping; geist remains generated |
| Bosworth-Toller Online | Old English lexical coverage | Site says data is free for any purpose and requests academic citation | admitted for mapping; obtain a versioned dump before ingestion |
| UniMorph English | inflection, segmentation, derivation | CC BY-SA 3.0 | isolated adapter only |
| English Wiktionary | multilingual etymology and broad lexical coverage | current CC BY-SA 4.0/GFDL; local dump records 3.0/GFDL | isolated pending exact-dump resolution |
| Corpus of Middle English | Middle English attestations and semantic context | corpus generally reusable, but an OTA subset remains share-alike; MED itself is copyrighted | component review required |
| Etymological WordNet 2013 | legacy etymological and derivational graph | CC BY-SA 3.0 is reported, but direct archive terms were not verified | review required |
| PanLex | translations and cross-language conceptual links | PanLex's current pages conflict between CC0 and CC BY-NC-SA 4.0 | blocked pending written resolution |
| Anglo-Norman Dictionary | specialist Anglo-Norman lexical evidence | free to search, but copying/incorporation is expressly restricted | blocked for ingestion |
| Perseus | potential Greek and Latin evidence | mixed component-level rights; wholesale commercial reuse is not granted | blocked wholesale; review components individually |
| GCIDE | historical English definitions | GPL-3.0-or-later | isolated GPL-compatible pack only |
| Library of Congress Chronicling America | dated newspaper context, place, period, topic, and register evidence | LoC states public domain or no known restrictions; later items can contain third-party material | admitted for mapping with item, OCR, and bias controls |
| Library of Congress collections API | structured collection, catalog, subject, date, place, and format metadata | rights are collection and item specific | review required before content use |
| Open Library catalog/dumps | edition discovery and bibliographic subject/date metadata | Internet Archive asserts no new database rights but warns that existing rights may remain | review required; metadata discovery is not content permission |
| Project Gutenberg historical reference works | dated dictionary and thesaurus category placement | exact ebook and jurisdiction specific; electronic editions may contain later changes | review each ebook identifier separately |
| Project Gutenberg Roget Ebook 22 | dated concept classes, heads, lexical groupings, cross-references, and obsolescence markings | public domain in the USA; electronic edition has 1,000+ additions, rearrangements, omissions, and transcription errors | Tier-Zero candidate as its own electronic edition after byte pinning |

## Historical aboutness lane

The immediate objective is not to copy old definitions. It is to recover
time-stamped evidence that a sense or usage cluster was associated with a
subject, domain, operation, quality, object, period, or register.

The source roles are deliberately separated:

1. National-library and archive catalogs locate editions and supply source
   labels, dates, places, formats, and collection context.
2. Public-domain or otherwise admitted dictionaries reveal dated lexical
   coverage and editorial labeling.
3. Historical thesauri reveal category placement and conceptual neighborhoods.
4. Historical encyclopedias reveal the discipline or subject under which a
   concept was discussed in that edition and period.
5. Newspaper archives reveal usage, register, co-occurrence, and change across
   dates and communities.

A source heading remains `SOURCE_SUBJECT_LABEL`; a reproducible contextual
cluster remains `DERIVED_CONTEXT_CLUSTER`; a new system label remains
`GENERATED_CLASSIFICATION`. None becomes `ACCEPTED_TOPIC_MAPPING` without a
separate review decision. Geist is downstream and lowest priority.

Candidate reference works are not admitted as a class. Each exact edition and
electronic artifact needs an identifier, date, hash, provenance record, rights
record, transcription-quality note, and allowed-field decision. This is
especially important where an old printed work has a later edited or
supplemented digital transcription.

## Translation-evidence lane

The detailed Hindi-English and Arabic-English findings are recorded in
`TRANSLATION_SOURCE_SURVEY.md`. Translation evidence is admitted only as a
scoped relation between sense or usage clusters. A bilingual headword pair or
aligned sentence does not establish identical meaning, synonymy, or shared
etymology.

The current strongest acquisition candidates are the public-domain UN
Arabic-English corpus and the Apache-licensed QCRI WAW corpus. FreeDict's
English-Hindi and English-Arabic dictionaries are usable only as separately
attributed GPL packs. Large mined or composite collections remain under
component review because a license on packaging does not necessarily clear the
underlying text.

## Source-language reconstruction order

1. Establish stable language identities and separate genealogy from contact
   using Glottolog.
2. Map Indo-European cognacy and reconstructed root references using IE-CoR.
3. Map structured lexeme/root/derivation coverage using Wikidata without
   promoting its community statements to accepted truth.
4. Establish the Old English layer with Bosworth-Toller coverage and a future
   admitted attestation corpus.
5. Establish the Middle English transition from an exact, component-audited
   corpus rather than the copyrighted MED database.
6. Add Old Norse, Anglo-Norman, Old French, Latin, and Ancient Greek as
   contact/transmission layers; never represent borrowing as direct descent.
7. Anchor modern sense coverage in OEWN while keeping etymology separate.
8. Use CLICS colexifications to identify conceptual-neighborhood questions,
   not to manufacture historical claims.
9. Split later contact languages into individually identified language and
   route records before admitting word-level evidence.
10. Use Concepticon, IDS, WOLD, and Grambank as the cross-language comparison
    spine while preserving their distinct concept, wordlist, borrowing, and
    typological claim types.
11. Exercise a generated structural-diversity panel before assuming that an
    English form, word boundary, derivation, sound system, or grammar is the
    universal case.
12. Build sense/usage clusters before assigning aboutness; never label a bare
    spelling as globally sociological, cartographic, or precise.
13. Populate subject, domain, operation, quality, period, and register facets
    with their distinct truth states; defer geist.

## Evidence links

- Wikidata licensing: https://www.wikidata.org/wiki/Wikidata:Licensing
- Wikidata lexicographical model:
  https://www.wikidata.org/wiki/Wikidata:Lexicographical_data
- Glottolog downloads and license: https://glottolog.org/meta/downloads
- IE-CoR: https://iecor.clld.org/
- OEWN downloads: https://en-word.net/downloads
- OEWN license:
  https://github.com/globalwordnet/english-wordnet/blob/main/LICENSE.md
- CLICS3: https://github.com/clics/clics3
- Bosworth-Toller Online: https://bosworthtoller.com/
- Corpus of Middle English statement:
  https://websites.umich.edu/~pfs/mec/med/
- English Wiktionary terms:
  https://en.wiktionary.org/wiki/Wiktionary:Copyrights
- Anglo-Norman restrictions: https://anglo-norman.net/copyright/
- Perseus component warning:
  https://www.perseus.tufts.edu/hopper/help/copyright.jsp
- GCIDE license: https://gcide.gnu.org.ua/license
- PanLex English license page: https://panlex.org/license
- PanLex conflicting localized page:
  https://panlex.org/es/licencia-de-base-de-datos-de-panlex/
- Library of Congress Chronicling America API:
  https://www.loc.gov/apis/additional-apis/chronicling-america-api/
- Library of Congress Chronicling America rights:
  https://www.loc.gov/collections/chronicling-america/about-this-collection/rights-and-access/
- Library of Congress JSON API:
  https://www.loc.gov/apis/json-and-yaml/
- Library of Congress item-rights guidance:
  https://www.loc.gov/legal/security-copyright-and-privacy/understanding-copyright/
- Open Library licensing: https://openlibrary.org/developers/licensing
- Open Library monthly dumps: https://openlibrary.org/developers/dumps
- Project Gutenberg 1911-derived Roget artifact:
  https://www.gutenberg.org/ebooks/22
- Project Gutenberg Roget plain text artifact:
  https://www.gutenberg.org/ebooks/22.txt.utf-8
- Project Gutenberg 1913 Webster text example:
  https://www.gutenberg.org/files/664/664-h/664-h.htm
- Project Gutenberg license: https://www.gutenberg.org/policy/license.html
- Concepticon: https://concepticon.clld.org/
- Intercontinental Dictionary Series: https://ids.clld.org/
- IDS versioned data repository:
  https://github.com/intercontinental-dictionary-series/ids
- World Loanword Database: https://wold.clld.org/
- Grambank: https://grambank.clld.org/
- PHOIBLE 2.0: https://phoible.org/
- Universal Dependencies licensing:
  https://universaldependencies.org/contributing/licensing.html
- SuttaCentral Bilara data and license:
  https://github.com/suttacentral/bilara-data/blob/published/LICENSE.md
- LiLa Lemma Bank: https://github.com/CIRCSE/LiLa_Lemma-Bank
- Cologne Digital Sanskrit Lexicon guides:
  https://github.com/sanskrit-lexicon/csl-guides
- Cleasby-Vigfusson 1874 edition record:
  https://www.worldtreeproject.org/document/94

## Known gaps

- Select a directly licensed Proto-Germanic lexical dataset.
- Select and hash an exact machine-readable Cleasby-Vigfusson artifact and
  verify its digitization-specific terms.
- Select an open Old French source.
- Admit LiLa Latin only through a separately attributed share-alike adapter;
  select an exact Ancient Greek component rather than relying on mixed Perseus.
- Research exact reusable Hebrew, Persian, and Urdu lexical sources.
- Select exact Sanskrit dictionary artifacts and validate their edition,
  transcription, correction, and share-alike provenance.
- Select a dated, reusable English corpus for semantic change and register.
- Define first-party reconstruction algorithms and negative controls.
- Obtain direct license evidence for Etymological WordNet 2013.
- Resolve PanLex's contradictory license pages before any adapter is enabled.
- Pin and hash Roget Ebook 22 as a dated electronic edition; continue selecting
  other exact obsolete dictionary, thesaurus, and encyclopedia artifacts with
  their rights and transcription lineage.
- Define controlled-topic identifiers and a review rule for promoting proposed
  aboutness to accepted topic mappings.
- Quantify OCR error, publication bias, geographic bias, and period coverage
  before deriving topic clusters from historical newspapers.
