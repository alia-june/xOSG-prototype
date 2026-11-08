# NLP Development Suite export

**Export status:** generated development snapshot. This package is not a canon-admission receipt, execution authorization, or proof that another project has accepted the included interfaces.

This bundle collects the current modular deterministic NLP work so development can continue in another project without depending on the original workspace layout.

## Projects

| Directory | Purpose | Snapshot basis |
|---|---|---|
| `projects/lexicon-core/` | Reusable deterministic NLP, task modules, catalog adapter, schemas, fixtures, and tests | Git commit `49a9251483e89242482d694a52b4daffac972b33` |
| `projects/lexicon-atlas/` | Word and sense explorer, dictionary synthesis, offline browser data, and desktop scaffold | Git commit `14c0f4fe907d82447c9147fe32cfe3b20deff539` |
| `projects/file-atlas/` | Browser-based file-interface prototype | Git commit `fb3f07cbd2f7ba505f896ed7a7d33a8ed136bc06` |
| `projects/natural-language-front-end/` | Grammar parser, command aliases, verified OEWN database, logic candidates, sister adapters, tests, and historical evidence | Filesystem snapshot; source root was not a Git repository |
| `scaffold-editor/` | Supplied standalone Scaffold Walker HTML | User-supplied attachment copied byte-for-byte |
| `contracts/` | Aurora catalog capability handoff v0.1 | Advisory source material |
| `shared-registry/` | Lexicon registry metadata and source inventory | Metadata only; raw corpora are external |

## First checks

From the extracted package root on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements-development.txt
cd .\projects\lexicon-core
$env:PYTHONPATH = 'src'
..\..\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

To inspect the packaged Lexicon Atlas browser:

```powershell
python -m http.server 8000 --directory .\projects\lexicon-atlas\dist
```

To use the full dictionary sources on the original machine:

```powershell
$env:LEXICON_DATA_ROOT = '<LEXICON_DATA_ROOT>'
```

On another machine, recreate the sources listed in `DATA_DEPENDENCIES.md` and point `LEXICON_DATA_ROOT` to the recreated registry.

## Authority boundary

- Source files and supplied contracts remain distinguishable from generated adapters and documentation.
- WordNet and attached dictionaries provide candidate lexical evidence.
- Parser and catalog outputs remain proposals until reviewed by their receiving authority.
- Collisions, unresolved regions, provenance, and source spans remain visible.
- No included NLP module authorizes command execution, filesystem mutation, rule admission, or catalog mutation.

Read `CONTINUATION.md` for the current development state, `VALIDATION.md` for tested coverage, and `EXCLUSIONS.md` before assuming a dependency is present.
