# Language expansion survey

Status: generated research synthesis as of 2026-10-03. This ranks research
directions and exact source candidates; it is not accepted lexical canon,
permission to ingest content, or a claim that language-level traits describe
every variety, speaker, period, or word.

## Finding

The best next move is not to choose one more bilingual dictionary. It is to
build a reusable comparative spine from four complementary resources:

1. [Concepticon 3.4](https://concepticon.clld.org/) supplies stable concept
   pivots and mappings among published concept lists under CC BY 4.0.
2. [Intercontinental Dictionary Series](https://ids.clld.org/) supplies a
   CC BY 4.0 CLDF dataset of comparable wordlists across hundreds of language
   varieties and a shared concept inventory.
3. [World Loanword Database](https://wold.clld.org/) supplies CC BY 3.0 DE
   evidence about recipient words, donor languages, borrowing status, age,
   analyzability, semantic fields, and grammar.
4. [Grambank](https://grambank.clld.org/) supplies CC BY 4.0 grammatical
   features across thousands of varieties, families, and isolates.

These resources answer different questions. Concept alignment is not
translation identity; a wordlist is not a dictionary definition; borrowing is
a scholarly analysis; and a grammatical feature is not a property of every
word. The system must preserve those distinctions.

## Priority A: English history and contact

| Language or group | Why it matters | Best current route | Current boundary |
|---|---|---|---|
| Old Norse | Germanic contact, borrowing, semantic competition | 1874 Cleasby-Vigfusson edition plus WOLD | Printed work is public domain, but an exact digital transcription and its terms must be selected and hashed |
| Latin | inherited comparison, learned formations, law, science, and French-mediated vocabulary | [LiLa Lemma Bank](https://github.com/CIRCSE/LiLa_Lemma-Bank) | CC BY-SA 4.0; isolate and attribute the adapter; it covers forms and word formation rather than all meaning evidence |
| Ancient Greek | scientific, philosophical, and technical formations, often through Latin | component-level source search | Perseus cannot be admitted wholesale; no exact clean Greek lexical component has yet passed review |
| Old French and Anglo-Norman | major post-Conquest contact and semantic transmission | open-corpus search | the dedicated Anglo-Norman Dictionary is lookup-only for this project under its current restrictions |
| Dutch, Low German, and German | Germanic comparison and later contact | IDS, WOLD, Concepticon, then dedicated historical sources | exact varieties and historical resources remain to be selected |
| Welsh, Irish, and Scottish Gaelic | British Isles contact and mutation systems | IDS, Grambank, WOLD | substrate claims require word-level evidence and must remain hypotheses |
| Arabic and Hebrew | root-and-pattern morphology, learned vocabulary, translation, and Semitic comparison | existing Arabic evidence plus IDS, Grambank, and a future Hebrew source review | Arabic is better covered; no exact Hebrew lexical source is yet admitted |
| Persian and Urdu | Iranian and South Asian literary, administrative, scientific, and contact routes | IDS and Grambank, followed by dedicated source research | exact open historical lexicons and aligned corpora remain missing |
| Sanskrit and Pali | Indo-European comparison, productive derivation, compounding, and historical concept vocabulary | Cologne Sanskrit candidates and [SuttaCentral Bilara](https://github.com/suttacentral/bilara-data) | Sanskrit dictionaries need edition-level review; Pali starts in a religious/historical register and must not be generalized |

## Priority B: structural diversity test panel

This is a generated testing panel, chosen to expose assumptions that an
English-only model is likely to hide. It is not a ranking of languages or a
claim that one named language has only the listed feature.

| Language | Principal stress test for the model |
|---|---|
| Mandarin Chinese | isolating morphology, classifiers, topic structure, and compact compounding |
| Japanese | agglutination, honorific/register distinctions, topic marking, and multiple scripts |
| Turkish | productive agglutination, vowel harmony, and transparent derivational chains |
| Finnish | rich case morphology and compounding |
| Basque | ergative alignment and isolate comparison |
| Swahili | noun-class agreement and productive derivation |
| Yoruba | lexical tone and serial-verb constructions |
| Georgian | complex verbal morphology and agreement |
| Inuktitut or Greenlandic | polysynthesis and word/sentence boundary pressure |
| Nahuatl | productive morphology, compounding, and contact history |
| Quechua | agglutination, evidential distinctions, and regional variety |
| Indonesian or Malay | reduplication, derivational affixes, and voice systems |

Concepticon and IDS can provide comparable concept coverage for this panel;
Grambank can expose grammatical contrasts; WOLD can expose borrowing paths.
[PHOIBLE 2.0](https://phoible.org/) is useful for sound inventories, but it is
kept in an isolated adapter until the exact distribution and license version
are pinned. [Universal Dependencies](https://universaldependencies.org/) can
support comparable morphology and syntax only after each treebank's separate
license is reviewed.

## Admission order

1. Pin versioned releases of Concepticon, IDS, WOLD, and Grambank and record
   hashes, citations, fields used, and required attribution.
2. Implement source-neutral interfaces for concept pivots, wordlist evidence,
   borrowing claims, grammatical features, and phonological inventories.
3. Add SuttaCentral Pali as a tightly scoped CC0 translation/context pilot.
4. Add Old Norse only after selecting the exact scan or transcription.
5. Add LiLa Latin and any Sanskrit data through isolated share-alike adapters.
6. Use the structural panel first as a gap and negative-test suite; do not
   generate first-party lexical claims until exact language-specific sources
   and varieties pass review.
7. Continue source research for Ancient Greek, open Old French, Hebrew,
   Persian, and Urdu rather than filling those gaps by inference.

## Ethical and evidentiary boundary

Cross-language comparison must retain language, variety, community, time,
register, source, collector, and analytical provenance. Especially for
Indigenous, endangered, sacred, or community-governed materials, an open
technical license does not erase context, attribution, community norms, or the
risk of decontextualizing a culturally bounded expression. Missing coverage is
reported as missing evidence—not as absence of a concept or deficiency in a
language.
