# P06 license and attribution review

## Verified observations

- The verification wheel contains only five package modules and five standard
  distribution-metadata files.
- It contains no OEWN database, WordNet source archive, omitted corpus, runtime
  dependency, license file, or notice file.
- The package declares no runtime dependencies.
- Build and test dependencies are staging inputs and are not included in the
  runtime wheel.
- The shared registry identifies optional OEWN 2025 candidate data as CC BY
  4.0, but that registry entry is evidence, not a substitute for a release
  attribution file.

## Deferred distribution prerequisite

No license or distribution terms have been selected or supplied for the newly
authored `nlp-offline-interpreter` code. The wheel metadata has no `License`,
`License-Expression`, or license classifier, and the source project has no
`LICENSE`, `LICENCE`, `COPYING`, or `NOTICE` file.

P06 therefore cannot verify license compliance for distribution. This is not
evidence of infringement or non-compliance; it is a missing authority and
evidence condition. Under the accepted internal-testbed boundary it does not
block local testing, because no publication or external redistribution is
occurring.

`BUNDLED_LICENSE_INVENTORY.md` separately enumerates the larger suite's
generated lexical-data bundle and the staging-only wheelhouse. Those materials
do not occur in the downloadable interpreter wheel. Their GPL, share-alike,
attribution, and notice terms therefore do not automatically select a license
for the standalone first-party package.

## Required disposition before publication

The user must identify the license or distribution terms for the newly authored
package. After that decision, the project metadata, license/notice files,
artifact manifest, wheel, and this review must be regenerated and revalidated.

If optional OEWN data is later bundled, its exact license text and required
attribution must also be included and verified against the exact candidate.
If the larger Lexicon Atlas bundle is distributed, its distinct GCIDE,
IPA Dict, UniMorph, Wiktionary, OEWN, and CMUdict obligations must be handled
component by component; a blanket license label is insufficient.
