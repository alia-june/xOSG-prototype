# Hindi-English and Arabic-English translation-source survey

Status: generated research synthesis dated 2026-10-03. This is not legal
advice, permission to download content, or acceptance of any lexical claim.

## Answer

There are useful sources we can lawfully build adapters for, but "free to
access" is not enough. The cleanest immediate acquisitions are the United
Nations Arabic-English Parallel Corpus and the Apache-licensed QCRI WAW corpus.
FreeDict supplies usable GPL translation dictionaries for both English-Hindi
and English-Arabic, provided they remain attributed GPL packs rather than being
silently absorbed into a differently licensed core.

No equally clean, large Hindi-English government corpus was confirmed in this
pass. India has an excellent open-data license, but it applies only to exact
resources published under that license. The large IIT Bombay and AI4Bharat
collections have noncommercial, component-specific, conflicting, or
underlying-source complications.

## Decision matrix

| Source | Pair/type | Scale or character | Controlling evidence found | Production disposition |
|---|---|---|---|---|
| UN Parallel Corpus v1.0 | Arabic-English sentence/document alignments | official records, 1990-2014; large; manually translated | corpus page says records are public domain; UN acknowledgement and corpus disclaimer required | **Acquire first** after pinning download and preserving document metadata |
| QCRI WAW | Arabic-English interpreted speech, transcript, translation | three education/research/health conferences | corpus page explicitly applies Apache 2.0 | **Acquire first** as a distinct interpreted-speech pack |
| FreeDict English-Hindi 1.6 | bilingual dictionary | 25,642 headwords; examples uneven | TEI header: GPL-2.0-or-later; explicitly marked low quality | **Acquire as isolated GPL pack**, never as accepted equivalence |
| FreeDict English-Arabic 0.6.3 | bilingual dictionary | 87,424 headwords; Arabeyes-derived | TEI header: GPL-2.0-or-later; status `stable` | **Acquire as isolated GPL pack** with quality sampling |
| Tatoeba downloads | Arabic-English and Hindi-English sentences | community-contributed, variable register and quality | downloads are CC-BY-2.0-FR; separate CC0 subset exists | **Acquire only with row/source attribution**; keep CC0 separate |
| FAO AGROVOC | concept identifiers and multilingual labels | agricultural and related domains; Arabic, English, Hindi labels exist | official pages disagree between CC-BY-IGO-3.0 and CC-BY-4.0 for FAO languages; non-FAO languages have institution ownership | **Review first**; Arabic-English is promising, Hindi requires separate rights evidence |
| India OGD / GODL-India | exact published government datasets | generic discovery lane, not itself a translation corpus | license permits attributed commercial/noncommercial use, adaptation, translation, and derivatives | **Admit exact GODL resources only**; ordinary government webpages do not inherit this license |
| AI4Kosh/BHASHINI catalog | per-item datasets and benchmarks | mixed owners and licenses | catalog shows item-level licenses such as CC-BY-SA, CC-BY-NC, GODL, or none | **Use as a registry**, not as one licensable collection |
| AI4Bharat BPCC | English-Indic parallel collection | about 230M bitext pairs across 22 Indic languages | some new subsets CC-BY-4.0; much is CC0-packaged while authors disclaim ownership of extracted text | **Partition-level review required**; do not take the bundle wholesale |
| AI4Bharat Samanantar 0.3 | English-Hindi and ten other English-Indic pairs | 49.6M pairs overall | project page says CC0 packaging; current Hugging Face metadata says CC-BY-NC-4.0 | **Blocked pending written/versioned resolution** |
| IIT Bombay English-Hindi 3.1 | composite parallel corpus | 1,659,082 pairs from many sources | CC-BY-NC-4.0 for compiled work; incorporated sources keep their own licenses | **Noncommercial isolated adapter only**; split every source partition |
| TDIL/ILCI Hindi-English | aligned, POS/chunk-tagged | 70,000 pairs in four domains | portal offers commercial or research licenses, not an open grant | **Blocked until a specific license is obtained** |
| HPLT | mined Arabic-English and Hindi-English web bitext | large, filtered web alignments | CC0 covers packaging; project says it does not own underlying text | **Coverage/test oracle only pending URL-level rights controls** |
| WIPO Pearl | Arabic-English technical terminology and concept maps | expert-validated terms with reliability scores | terms prohibit scraping, bulk acquisition/storage/copying/sharing/redistribution | **Human point lookup only**; do not build a bulk adapter |
| MADAR | Arabic dialects, MSA, English/French basis | 25 city dialects | noncommercial terms; English and French withheld for copyright reasons | **Blocked for requested Arabic-English acquisition** |
| Althobaiti Arabic-English Wikipedia corpus | automatically extracted sentence pairs | 105,010 pairs | CC-BY-NC-ND-4.0 and available on request | **Blocked from generic production core** |
| General UN website materials | documents on un.org outside the named corpus | broad | general UN terms are personal, noncommercial and restrict redistribution/derivatives | **Do not generalize the corpus permission to un.org** |

## What "take" should mean technically

For an admitted source, acquisition still produces an evidence pack, not our
dictionary. Each pack needs:

1. exact source identifier, version, retrieval date, URL, and SHA-256;
2. the license text and source-specific notice stored beside the data;
3. original row/document identifiers and attribution fields;
4. language/script, domain, date, register, dialect, and provenance metadata;
5. an immutable raw layer and a reproducible normalized layer;
6. train/development/test and benchmark-contamination flags;
7. quality sampling for alignment, encoding, OCR, and sense ambiguity;
8. an adapter boundary that can be disabled or removed without damaging the
   first-party graph.

## How translation evidence enters the lexicon

A translation pair is not a meaning identity. The proposed relation is:

```text
source sense or usage cluster
    --translation_candidate-->
target sense or usage cluster
```

Every relation should record direction, source, domain, period, register,
human/machine/mined origin, alignment score, and contradictions. Dictionary
headword pairs without sense identifiers stay candidates. Sentence alignments
can support sense clustering, but cannot by themselves establish synonymy,
etymology, or universal equivalence.

## Recommended acquisition order

1. UN Arabic-English Parallel Corpus v1.0: strongest rights/provenance
   combination and includes useful subject/date metadata.
2. QCRI WAW: permissive license and a valuable spoken/interpreted contrast.
3. FreeDict English-Hindi and English-Arabic: compact lexical bridges, isolated
   under GPL and subjected to aggressive quality tests.
4. Tatoeba CC0 subset first, then attributed CC-BY rows if the attribution
   ledger is ready.
5. Exact GODL-India or AIKosh items only when the item page explicitly supplies
   a compatible license and both sides of the language pair.
6. Resolve AGROVOC's exact-release license and Hindi-language rights before
   ingesting labels.

Do not begin with BPCC, Samanantar, IITB, HPLT, WIPO Pearl, MADAR, or TDIL as a
wholesale import. They remain valuable for gap discovery, comparison, licensed
adapters, or later negotiated access.

## Primary evidence links

- UN Parallel Corpus: https://www.un.org/dgacm/en/content/uncorpus
- UN corpus Arabic disclaimer: https://www.un.org/dgacm/ar/content/uncorpus/ar
- QCRI WAW: https://alt.qcri.org/resources/wawcorpus/
- FreeDict dictionaries: https://github.com/freedict/fd-dictionaries
- Tatoeba downloads: https://tatoeba.org/en/downloads
- AGROVOC access and rights: https://aims.fao.org/standards/agrovoc/access-agrovoc
- AGROVOC machine access: https://www.fao.org/agrovoc/machine-use
- Government Open Data License - India:
  https://data.gov.in/sites/default/files/Gazette_Notification_OGDL.pdf
- AI4Bharat IndicTrans2/BPCC: https://github.com/AI4Bharat/IndicTrans2
- Samanantar project statement:
  https://github.com/AI4Bharat/indicnlp.ai4bharat.org/blob/master/content/pages/samanantar.md
- Samanantar current dataset card:
  https://huggingface.co/datasets/ai4bharat/samanantar/blob/main/README.md
- IIT Bombay English-Hindi corpus: https://www.cfilt.iitb.ac.in/iitb_parallel/
- TDIL ILCI Hindi-English corpus:
  https://tdil-dc.in/nplt/index.php?product_id=1934&route=product/product
- HPLT data: https://hplt-project.org/datasets/v1.2
- WIPO Pearl terms: https://www.wipo.int/en/web/wipo-pearl/terms-wipopearl
- MADAR: https://camel.abudhabi.nyu.edu/madar-parallel-corpus/
- Althobaiti corpus: https://github.com/Maha-J-Althobaiti/Ara_Eng_Parallel_Corpus

