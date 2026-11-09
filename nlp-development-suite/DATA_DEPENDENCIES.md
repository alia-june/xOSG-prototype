# Data dependencies

## Included

- Lexicon Atlas generated browser shards under `projects/lexicon-atlas/dist/data/`.
- Pinned tracked source files needed by the Lexicon Atlas repository.
- The shared registry metadata in `shared-registry/registry.json`.
- Source hashes, revisions, licenses, and URLs recorded by that registry.
- The verified Open English WordNet database under `projects/natural-language-front-end/.wn_data/`.

The packaged browser data allows the static Lexicon Atlas front end to run without the multi-gigabyte raw Wiktionary extraction.

## External

The following source datasets are intentionally not duplicated:

| Source | Recorded identity |
|---|---|
| CMUdict | revision `74790861f652b15e4ac49015a90074ad62a27690` |
| IPA Dict | revision `43c3570eb3553bdd19fccd2bd0091534889af023` |
| UniMorph English | revision `66e0e9e8e2dcd196da081a25a48e5c1fe3d8b49b` |
| Wiktionary extraction | 3,335,555,506 bytes; SHA-256 `e6e485811ce4f21910d989c88a90453a3faec05542e46bcab9defaa5ba43fb0e` |
| GCIDE | 0.54 archive SHA-256 `22416f6f36175b160dc388b7547512514d464473cf7d7c898d738efb26c51d42` |
| ODict | revision `6a2bb5ab7a3d33b185ce6341381525b91c75e990` |

The original machine exposes these sources through Windows junctions beneath:

```text
<LEXICON_DATA_ROOT>
```

For a different location, set `LEXICON_DATA_ROOT` and recreate `registry.json` plus its relative source directories. Do not copy junction objects and assume their targets were included.
