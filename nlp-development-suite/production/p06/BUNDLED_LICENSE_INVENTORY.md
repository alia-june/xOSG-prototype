# P06 bundled-license inventory

## Status and scope

Generated evidence dated 2026-10-02. This inventory distinguishes four scopes
that must not be treated as one artifact:

1. the downloadable `nlp-offline-interpreter` wheel;
2. the historical development-suite snapshot;
3. the generated Lexicon Atlas browser-data bundle within that snapshot; and
4. the P04 build/test wheelhouse.

License names and obligations remain attached to their individual components.
Calling one license the "most restrictive" does not relicense other components
or prove that a combined distribution is compliant.

## A. Downloadable interpreter wheel

Artifact: `nlp_offline_interpreter-0.1.0-py3-none-any.whl`

- Contains five first-party Python modules and five distribution-metadata
  files.
- Declares zero runtime dependencies.
- Bundles no lexical database, CMUdict, UniMorph, IPA dictionary, Wiktionary,
  GCIDE, Electron, or P04 wheelhouse package.
- Contains no license or notice file and declares no license metadata.

Therefore no third-party license selects the license for this wheel. The
blocking fact is that the first-party code's distribution terms are still
unselected.

## B. Historical suite and first-party source

The historical export contains only two files named as licenses:

- `projects/lexicon-atlas/vendor/cmudict/LICENSE`;
- `projects/lexicon-atlas/vendor/ipa-dict/LICENSE`.

No top-level license was supplied for Lexicon Core, Lexicon Atlas, File Atlas,
the Natural Language front end, Scaffold Walker, or the later
`nlp-offline-interpreter`. Their distribution terms are `UNKNOWN`; absence of a
license file does not establish an intended proprietary or open-source license.

The desktop source declares `electron==35.7.5` as a development dependency,
but no Electron binary or `node_modules` tree is present in the snapshot.
The registry mentions the GPL-3.0 ODict toolchain, but that toolchain is not
present; `odict_bridge.cjs` is first-party bridge source, not a bundled ODict
binary.

## C. Generated Lexicon Atlas data bundle

The exact packaged data manifest is
`projects/lexicon-atlas/dist/data/manifest.json`. It covers 1,057 files totaling
228,971,742 bytes and records these sources:

| Component | Packaged scope | Recorded terms | Practical obligation class |
|---|---|---|---|
| Open English WordNet 2025 | Base word/synset/sense data | CC BY 4.0 plus underlying Princeton WordNet notice | Attribution, license link/text, modification indication, and preserved underlying notice |
| CMUdict | US English pronunciations | Custom permissive CMU notice | Retain notice and disclaimer in source/binary redistribution materials |
| UniMorph English | Forms and derivational links | CC BY-SA 3.0 | Attribution and share-alike for adapted licensed material/database |
| IPA Dict `en_US` | General American IPA | MIT-derived | Retain copyright and permission notice |
| IPA Dict `en_UK` | Received Pronunciation IPA | GPL-3.0-derived | Strong reciprocal/copyleft terms for the covered material and corresponding source duties where applicable |
| English Wiktionary via Kaikki | Entries, senses, etymologies, forms, pronunciations | Local manifest says CC BY-SA 3.0 and GFDL | Attribution/share-alike or GFDL route; exact snapshot terms and notices require confirmation |
| GCIDE 0.54 | Historical definitions | GPL-3.0-or-later | Strong reciprocal/copyleft terms for the covered dictionary material and source availability duties |

Two evidence qualifications matter:

- The current English Wiktionary copyright page describes text as dual-licensed
  under CC BY-SA 4.0 and GFDL, while the local 2026-09-02 dump manifest records
  CC BY-SA 3.0 and GFDL. The exact dump's applicable version and attribution
  chain are unresolved and must be verified before redistribution.
- Only the CMUdict and IPA Dict license files are physically present beside the
  exported suite. The packaged bundle does not contain complete license and
  attribution texts for OEWN, UniMorph, Wiktionary, or GCIDE.

### Restrictiveness finding

For the packaged data, GCIDE's `GPL-3.0-or-later` and IPA Dict `en_UK`'s
GPL-3.0-derived material are the clearest strong-copyleft components. UniMorph
and Wiktionary add separate share-alike/data obligations. Wiktionary's GFDL
option has its own documentation and notice requirements.

There is no reliable single "winner" that can be applied to the entire bundle:
GPL, CC BY-SA, GFDL, CC BY, MIT, and the CMU notice govern different material.
A GPL license for first-party code would not erase or replace the attribution,
share-alike, GFDL, MIT, or custom-notice duties of the data.

## D. P04 build/test wheelhouse

These packages are retained for reproducible development and testing. They are
not members of the downloadable interpreter wheel.

| Package | Version | Wheel metadata |
|---|---:|---|
| anyio | 4.15.1 | MIT |
| aprompt | 1.1.0 | No license field, expression, classifier, or bundled license found |
| attrs | 26.1.0 | MIT |
| certifi | 2026.7.22 | MPL-2.0 |
| h11 | 0.16.0 | MIT |
| httpcore | 1.0.9 | BSD-3-Clause |
| httpx | 0.28.1 | BSD-3-Clause |
| idna | 3.19 | BSD-3-Clause |
| jsonschema | 4.26.0 | MIT |
| jsonschema-specifications | 2025.9.1 | MIT |
| referencing | 0.37.0 | MIT |
| rpds-py | 2026.6.3 | MIT; four runtime-specific wheels retained |
| setuptools | 84.0.0 | MIT |
| typing_extensions | 4.16.0 | PSF-2.0 |
| wn | 1.1.1 | MIT |

`aprompt` is an evidence gap for redistribution of the wheelhouse. It does not
affect the standalone interpreter wheel because the wheel neither depends on
nor contains `aprompt`.

## Replacement and separation order

If the intended release must avoid strong reciprocal or share-alike terms, use
this order:

1. Keep the interpreter wheel data-free and dependency-free. This is already
   true and is the lowest-risk distributable boundary.
2. Remove GCIDE-derived definitions from any redistributable data bundle, or
   replace them with a source whose exact terms meet the selected policy.
3. Remove the IPA Dict `en_UK` portion, or obtain/build a replacement with
   acceptable recorded terms. The MIT-derived `en_US` portion can remain only
   with its required notice.
4. Remove or separately package UniMorph-derived forms if CC BY-SA 3.0 is not
   acceptable.
5. Remove or separately package Wiktionary/Kaikki-derived material until its
   exact dump license version, attribution chain, and redistribution notices
   are verified.
6. Retain OEWN only if CC BY 4.0 attribution and the underlying Princeton
   WordNet notice are packaged and accepted.
7. Generate new data manifests after every removal. Counts and hashes in the
   current bundle cannot be reused for a reduced bundle.

Replacement candidates are not accepted merely because they have a preferred
license name. Each candidate requires exact version, source URL, hash, license
text, attribution, provenance, data-quality checks, and a deterministic rebuild
receipt before admission.

## External verification references

Checked 2026-10-02 against upstream project sources:

- Open English WordNet license:
  https://github.com/globalwordnet/english-wordnet/blob/main/LICENSE.md
- UniMorph English repository:
  https://github.com/unimorph/eng
- IPA Dict repository and per-language credits:
  https://github.com/open-dict-data/ipa-dict
- GCIDE license:
  https://gcide.gnu.org.ua/license
- English Wiktionary copyright terms:
  https://en.wiktionary.org/wiki/Wiktionary:Copyrights

This is an engineering inventory, not legal advice or a compliance attestation.
