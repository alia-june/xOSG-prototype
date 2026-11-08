# Shared Lexicon Data

This is the central machine-local dictionary registry for Lexicon Atlas and sibling NLP projects. `registry.json` records source roles, versions, licenses, hashes, and stable relative paths.

The source directories are Windows junctions to the verified files already used by the Natural Language workspace. The registry avoids a second 3.6 GB copy while giving each project one stable root: set `LEXICON_DATA_ROOT` to this directory.

Sources currently registered: OEWN, CMUdict, Open Dict Data IPA, UniMorph English, complete local English Wiktionary, GCIDE, ODict, and a StarDict import inbox.

Junctions are an access layer, not a license or authority upgrade. Source records stay separate, and imported dictionaries remain candidates until reviewed.
