# WordNet definitions, relations, and data verification

The NLP front end uses the pinned `wn==1.1.1` library and the complete Open English WordNet release `oewn:2025`. The local database contains 135,969 words, 107,519 synsets, and 185,129 senses. `verify_wordnet.py` checks those exact counts, the project resource URL, the cached source archive SHA-256, and whether Wn can open the compressed WN-LMF resource.

```powershell
.\.venv\Scripts\python.exe .\verify_wordnet.py
```

The cached `english-wordnet-2025.xml.gz` source has SHA-256 `9CA6D1DCB75F822FDD66617F7D9DA48142ACE38DD544D6AD5E2FECA1674AD3FE`. On 2026-09-26, the complete compressed source also passed all 18 checks in `python -m wn validate`.

## Query commands

```powershell
.\.venv\Scripts\python.exe .\omni_cli.py "define dog"
.\.venv\Scripts\python.exe .\omni_cli.py "definition of run"
.\.venv\Scripts\python.exe .\omni_cli.py "show relations for dog"
.\.venv\Scripts\python.exe .\omni_cli.py "word relations for run"
```

Definition queries return every candidate synset with its part of speech, lemmas, definition, and examples. Relation queries return every candidate synset, semantic relations between synsets, and lexical relations between senses. The result sets `sense_selected: false`; WordNet supplies candidates and does not decide which sense the user intended.

Each relation type reports its full target count. At most 50 target records per relation type are emitted, and `truncated: true` marks a longer list. This output bound does not remove the relation type or conceal its actual size.

The commands are deterministic read-only lexicon queries. They do not make a web request, adopt an axiom, or authorize another operation.

## Graphical explorer

[`wordnet-explorer-site`](wordnet-explorer-site/README.md) is the graphical
view of this same verified database. Lexicon Atlas searches all 131,094 indexed
term forms, keeps all senses visible, and lets a user move through semantic and
lexical relations as a graph or list. A depth selector follows a chosen
semantic or lexical relation recursively through as many as five levels. The graph labels
its deterministic node bounds; the direct relation list remains separate.
Its footer and sense note preserve the
candidate-only boundary: the interface does not choose a contextual sense.

The static dataset is generated directly from `.wn_data/wn.db` by
`wordnet-explorer-site/build_data.py`. The generated manifest records the OEWN
release, counts, source URL, license, and source database SHA-256. Rebuilding
the site does not download data or query an external service.
