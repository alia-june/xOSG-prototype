# Initial mining gap report

Status: generated license-gap analysis. One pinned Roget unit is authorized for internal test mining only; production ingestion and publication remain unauthorized.

## Result

- Sources inventoried: 44
- Tier-zero eligible sources: 5
- Tier-zero eligible content units: 5
- Sources excluded from initial mining: 39
- Mining-ready units: 1

Eligible source containers: `project-gutenberg-roget-22`, `suttacentral-bilara`, `tatoeba-sentence-pairs`, `un-parallel-corpus-v1`, `wikidata-lexemes`.

The eligible container does not imply that every file in it is eligible. Tatoeba and SuttaCentral are component-filtered.

## Global holes exposed by the strict tier

`GRAMMAR`, `PHONOLOGY`.

`GEIST` is deliberately deferred rather than counted as a mining hole.

## Language and layer candidate coverage

This table reports only whether an eligible source is typed for a dimension. It does not claim that the source contains a usable record for any particular word; empirical record coverage remains unknown until a separately authorized mining run.

| Language or layer | Status | Eligible sources | Unserved dimensions |
|---|---|---|---|
| proto-indo-european | candidate_for_all_declared_dimensions | wikidata-lexemes | none declared by the capability map |
| proto-germanic | candidate_for_all_declared_dimensions | wikidata-lexemes | none declared by the capability map |
| west-germanic | candidate_for_all_declared_dimensions | wikidata-lexemes | none declared by the capability map |
| old-english | candidate_for_all_declared_dimensions | wikidata-lexemes | none declared by the capability map |
| middle-english | candidate_for_all_declared_dimensions | wikidata-lexemes | none declared by the capability map |
| modern-english | candidate_for_all_declared_dimensions | project-gutenberg-roget-22, wikidata-lexemes | none declared by the capability map |
| old-norse | partial_candidate_coverage | wikidata-lexemes | PERIOD, REGISTER |
| anglo-norman | candidate_for_all_declared_dimensions | wikidata-lexemes | none declared by the capability map |
| old-french | candidate_for_all_declared_dimensions | wikidata-lexemes | none declared by the capability map |
| latin | partial_candidate_coverage | wikidata-lexemes | GRAMMAR |
| ancient-greek | candidate_for_all_declared_dimensions | wikidata-lexemes | none declared by the capability map |
| sanskrit-pali | partial_candidate_coverage | suttacentral-bilara, wikidata-lexemes | GRAMMAR, TRANSLATION_EQUIVALENCE |
| semitic-comparison | partial_candidate_coverage | un-parallel-corpus-v1, wikidata-lexemes | GRAMMAR |
| persian-urdu | partial_candidate_coverage | wikidata-lexemes | ABOUTNESS, DOMAIN, GRAMMAR, PERIOD, REGISTER, TRANSLATION_EQUIVALENCE |
| celtic-languages | partial_candidate_coverage | wikidata-lexemes | ABOUTNESS, GRAMMAR, PERIOD, PHONOLOGY, REGISTER |
| structural-diversity-panel | partial_candidate_coverage | wikidata-lexemes | ABOUTNESS, DOMAIN, GRAMMAR, PERIOD, PHONOLOGY, REGISTER, TRANSLATION_EQUIVALENCE |
| later-contact-languages | partial_candidate_coverage | wikidata-lexemes | GRAMMAR, PHONOLOGY |

## Excluded-source ledger

| Source | Recorded license | License status | Existing source-map status |
|---|---|---|---|
| ai4bharat-bpcc | CC0 packaging declarations plus underlying-source rights caveat; CC-BY-4.0 for newly authored human subsets | component-and-underlying-rights-review | review_required |
| althobaiti-ar-en-wikipedia | CC-BY-NC-ND-4.0 | verified-current-repository-statement | blocked |
| anglo-norman-dictionary | All substantive/digital rights reserved with explicit copying restrictions | verified-current | blocked |
| bosworth-toller-online | Data stated free for any purpose; academic citation requested | verified-current-site-statement | admitted_for_mapping |
| cleasby-vigfusson-1874 | Public-domain historical edition; digitization-specific terms unresolved | exact-artifact-review-required | review_required |
| clics3 | CC-BY-4.0 | verified-current | admitted_for_mapping |
| cologne-sanskrit-lexicons | Project guides state CC-BY-SA-4.0 | exact-artifact-review-required | review_required |
| concepticon-3.4 | CC-BY-4.0 | verified-current-site-statement | admitted_for_mapping |
| etymwn-2013 | Reported CC-BY-SA-3.0 | direct-license-not-yet-verified | review_required |
| fao-agrovoc-ar-en | Official pages identify CC-BY-IGO-3.0 or CC-BY-4.0 for FAO-language content | official-license-version-conflict | review_required |
| freedict-eng-ara-0.6.3 | GPL-2.0-or-later | verified-in-tei-header | isolated_adapter_only |
| freedict-eng-hin-1.6 | GPL-2.0-or-later | verified-in-tei-header | isolated_adapter_only |
| gcide-0.54 | GPL-3.0-or-later | verified-current | isolated_adapter_only |
| glottolog-5.3 | CC-BY-4.0 | verified-current | admitted_for_mapping |
| grambank | CC-BY-4.0 | verified-current-site-statement | admitted_for_mapping |
| hplt-ar-en-hi-en | CC0 for packaging; project disclaims ownership of extracted web text | underlying-rights-unresolved | review_required |
| ids-cldf | CC-BY-4.0 | verified-current-site-and-repository-statement | admitted_for_mapping |
| iecor | CC-BY-4.0 | verified-current | admitted_for_mapping |
| iitb-en-hi-3.1 | CC-BY-NC-4.0 for newly compiled work; included corpora retain their respective licenses | verified-current-composite | isolated_adapter_only |
| india-ogd-godl | Government Open Data License - India | verified-current-license | admitted_for_mapping |
| lila-lemma-bank | CC-BY-SA-4.0 | verified-current-repository-statement | isolated_adapter_only |
| loc-chronicling-america | Library of Congress states public domain or no known restrictions; item-level assessment remains required | verified-current-collection-statement | admitted_for_mapping |
| loc-collections-api | Collection and item specific | item-level-review-required | review_required |
| madar-parallel | Noncommercial research terms; English and French source sentences withheld for copyright reasons | verified-current-restrictions | blocked |
| middle-english-corpus | Generally unrestricted reuse; identified OTA subset remains share-alike | mixed-components | review_required |
| oewn-2025 | CC-BY-4.0 plus Princeton WordNet notice | verified-current | admitted_for_mapping |
| open-library-catalog | Internet Archive asserts no new rights in the database; existing contribution and jurisdictional rights may remain | verified-current-with-rights-caveat | review_required |
| panlex | Conflicting current site statements: English data page says CC0; localized page says CC-BY-NC-SA-4.0 | conflict | blocked |
| perseus | Component-specific and mixed | mixed-components | blocked |
| phoible-2.0 | Site states CC-BY-SA-3.0; current derived distributions may state different terms | version-conflict | isolated_adapter_only |
| project-gutenberg-historical-reference | Exact ebook and jurisdiction specific under the Project Gutenberg license | exact-artifact-review-required | review_required |
| qcri-waw-corpus | Apache-2.0 | verified-current-site-statement | admitted_for_mapping |
| samanantar-0.3 | Official project page says CC0 packaging; current Hugging Face dataset metadata says CC-BY-NC-4.0 | conflict | blocked |
| tdil-ilci-hin-eng | Commercial or research license offered; no blanket open grant shown | specific-license-required | blocked |
| unimorph-eng | CC-BY-SA-3.0 | verified-current | isolated_adapter_only |
| universal-dependencies | Treebank-specific and mixed | mixed-components | review_required |
| wiktionary-en | CC-BY-SA-4.0 and GFDL; local Kaikki snapshot records CC-BY-SA-3.0 and GFDL | version-conflict | isolated_adapter_only |
| wipo-pearl | Free lookup under restrictive database terms | verified-current-restrictions | blocked |
| wold | CC-BY-3.0-DE | verified-current-site-statement | admitted_for_mapping |

## Readiness boundary

Readiness is test-only. Every other eligible unit still requires an exact version or dated export, SHA-256, enforced scope filter, and a separate execution decision; no unit is production-ready.

Exclusion at this tier is not a judgment that a source is unusable; it means the source is outside the deliberately narrow CC0/public-domain pilot.
