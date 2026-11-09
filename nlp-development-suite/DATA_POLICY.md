# Prototype data policy

The repository contains code, schemas, fixtures, and documentation only. It deliberately excludes OEWN databases, Wiktionary/Kaikki extractions, GCIDE data, CMUdict data, IPA datasets, UniMorph datasets, StarDict/ODict payloads, Roget source/output corpora, generated browser shards, and user-supplied dictionary inboxes.

Runtime data must be mounted or built separately under its own provenance and license review. A local path may be supplied through `LEXICON_DATA_ROOT`; no machine-specific default path is part of the repository.

The Atlas UI expects `projects/lexicon-atlas/dist/data/manifest.json` and associated shards. Their absence is intentional in this code-only prototype.
