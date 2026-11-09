# NLP Development Suite

A modular, deterministic natural-language development bed for lexical analysis,
bounded interpretation, controlled command parsing, word-history research, and
source-aware browser interfaces.

This directory is the public **code-only prototype**. It contains source,
schemas, fixtures, tests, contracts, and evidence records, but deliberately
does not contain the private or separately licensed dictionary payloads used by
the full local workbench. It is not a production deployment, an accepted
semantic authority, or an execution engine.

## What it can do

The included modules can:

- normalize and tokenize text deterministically while preserving source text,
  hashes, character spans, and unresolved regions;
- group spelling collisions without silently choosing one dictionary or sense;
- label morphological features and traverse lexical or semantic relations with
  explicit depth and node bounds;
- rank source-labelled lexical candidates without converting the ranking into
  canon;
- parse a controlled grammar and versioned command-alias catalog;
- produce proposal-only task results for dictionary lookup, file exploration,
  expert-control drafts, and deterministic ELIZA-style interaction;
- interpret bounded read-only file commands with path, file-size, traversal,
  and result limits;
- emit a generic, canonical JSON interpretation envelope with fixed
  `authority_effect: NONE` and `execution_allowed: false` fields;
- display code-only Lexicon Atlas and File Atlas browser interfaces;
- measure historical/modern lexical discrepancy shapes and prepare blank,
  evidence-bearing review packets without assigning meaning; and
- validate prototype membership, file hashes, excluded data classes, identity
  reduction, Python behavior, and JavaScript syntax.

It does **not** execute proposed commands, mutate files through the interpreter,
admit axioms or rules, choose a canonical word meaning, download dictionaries,
or make generated lexical research authoritative.

## How the pieces fit together

```text
source text
    |
    +-- controlled grammar and command aliases
    +-- generic bounded interpretation layers
    +-- lexical normalization, morphology, collisions, relations, synthesis
    |
    v
source-preserving candidates + diagnostics + unresolved regions
    |
    v
optional receiving adapter or browser UI
    |
    v
external review / authority / execution boundary
```

| Path | Role | Current public boundary |
|---|---|---|
| [`projects/lexicon-core`](projects/lexicon-core/) | Reusable lexical primitives, task routing, and advisory catalog adapter | Proposal generation only |
| [`development/nlp-offline-interpreter`](development/nlp-offline-interpreter/) | Domain-neutral bounded interpreter and dependency-free basic analysis | No execution interface |
| [`projects/natural-language-front-end`](projects/natural-language-front-end/) | Controlled grammar, aliases, semantic layers, read-only command front end, and sister handoff scaffolding | Receiving schemas and acceptance remain external |
| [`projects/lexicon-atlas`](projects/lexicon-atlas/) | Word/sense exploration, source comparison, synthesis UI, and desktop scaffold | Runtime dictionary shards are excluded |
| [`projects/file-atlas`](projects/file-atlas/) | Browser interface for bounded read-only file commands | Browser-local access only; no shell or mutation |
| [`development/generative-relational-lexicon`](development/generative-relational-lexicon/) | Historical gap mapping, word-universe modelling, calibration, and review tooling | Generated research scaffold, not lexical canon |
| [`contracts`](contracts/) | Advisory capability handoff | Contract evidence, not receiver acceptance |
| [`production`](production/) | Decision, hardening, threat, rollback, and staged-release evidence | Historical/bounded evidence; not a blanket production claim |
| [`scaffold-editor`](scaffold-editor/) | Standalone supplied scaffold-walker interface | Separate UI artifact |

## Quick start: data-free validation

Requirements:

- Python 3.11 through 3.14;
- Node.js 22 for JavaScript syntax checks; and
- network access once to install the pinned validation dependency.

From `nlp-development-suite` in Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements-prototype.txt
$emptyData = New-Item -ItemType Directory -Force .\.prototype-empty-data
$env:LEXICON_DATA_ROOT = $emptyData.FullName
.\.venv\Scripts\python.exe -B .\RUN_PROTOTYPE_CHECKS.py
```

The runner verifies the manifest and sanitization boundary, then runs 81 Python
tests across Lexicon Core, the Offline Interpreter, controlled grammar,
command aliases, and bounded read-only commands. When Node.js is available, it
also checks every retained Atlas JavaScript file. The repository workflow runs
this profile on Python 3.11, 3.12, 3.13, and 3.14.

`requirements-prototype.txt` is intentionally smaller than
`requirements-development.txt`. The latter describes a fuller source-workspace
environment and references dependencies that are not part of this sanitized
export.

## Try the generic interpreter

The standalone basic layer performs bounded surface analysis. It tokenizes the
input and reports spans, counts, truncation, provenance, and diagnostics without
inferring intent.

```powershell
$env:PYTHONPATH = '.\development\nlp-offline-interpreter\src'
python -B -m nlp_offline_interpreter --basic "Map words precisely."
```

To exercise the optional suite integration, place all three source roots on
`PYTHONPATH`:

```powershell
$env:PYTHONPATH = '.\development\nlp-offline-interpreter\src;.\projects\lexicon-core\src;.\projects\natural-language-front-end'
python -B -m nlp_offline_interpreter.integration --no-wordnet "find files named report in ."
```

The command prints an interpretation plan. There is no execute option.

## Explore the browser interfaces

File Atlas includes a demonstration workspace and can be served without a
dictionary bundle:

```powershell
python -m http.server 8000 --directory .\projects\file-atlas\dist
```

Lexicon Atlas can also be served from `projects/lexicon-atlas/dist`, but its
word and sense views expect a separately built `dist/data/manifest.json` and
associated shards. A code-only checkout therefore reports that lexical data is
unavailable. Any deployed, data-bearing Atlas remains a separate artifact with
its own source, data, license, and validation records.

## Optional lexical data

Set `LEXICON_DATA_ROOT` to a separately managed registry only after reviewing
the exact source versions and licenses:

```powershell
$env:LEXICON_DATA_ROOT = 'D:\approved-lexical-data'
```

The public prototype excludes OEWN databases, Wiktionary/Kaikki extractions,
GCIDE, CMUdict, IPA and UniMorph datasets, Roget source/output corpora,
StarDict/ODict payloads, generated browser shards, and user-supplied dictionary
inboxes. See [`DATA_POLICY.md`](DATA_POLICY.md) and
[`DATA_DEPENDENCIES.md`](DATA_DEPENDENCIES.md).

Attaching a source does not merge its authority with another source. Every
adapter must retain provenance, version, license, purpose, conflicts, and
unknowns. Generated relations or classifications remain generated until a
separate acceptance process says otherwise.

## Evidence and truth boundaries

The suite distinguishes direct source material, accepted decisions, derived
results, inference, unknowns, and generated synthesis. In practical terms:

- a parse is evidence that a grammar matched, not that its interpretation is
  correct;
- a schema-valid envelope is not receiving-system acceptance;
- a test pass covers only the named test profile;
- a manifest hash proves byte identity, not semantic correctness;
- a lexical candidate is not a canonical definition; and
- a proposal is not authorization to execute or mutate anything.

Start with these records when reviewing the project:

- [`README_FIRST.md`](README_FIRST.md) — source snapshot and first-run context;
- [`PROTOTYPE_TEST_PROFILE.md`](PROTOTYPE_TEST_PROFILE.md) — what public CI does
  and does not test;
- [`VALIDATION.md`](VALIDATION.md) — staged-export validation evidence;
- [`CONTINUATION.md`](CONTINUATION.md) — current implementation state and next
  development gates;
- [`PRODUCTION.md`](PRODUCTION.md) — production-track status and evidence map;
- [`PROTOTYPE_MANIFEST.json`](PROTOTYPE_MANIFEST.json) — exact public component
  membership; and
- [`SANITIZATION_REPORT.json`](SANITIZATION_REPORT.json) — excluded-data and
  identity-reduction report.

## Development rules

1. Keep source evidence, accepted decisions, generated material, and unknowns
   distinguishable.
2. Add new interpretation behavior as a bounded layer with explicit provenance,
   diagnostics, failure states, and regression tests.
3. Preserve source text and spans; do not repair ambiguity by silently choosing
   a meaning.
4. Keep execution and authority outside the NLP layers.
5. Never commit local dictionaries, generated shards, credentials, machine
   paths, caches, or review data that the public policy excludes.
6. Update `PROTOTYPE_MANIFEST.json` whenever an intentional public component
   file changes.
7. Run `python -B RUN_PROTOTYPE_CHECKS.py` before proposing publication.

## Status

The data-free prototype profile is reproducible and continuously tested. The
open work is primarily at the data, receiving-contract, calibration, semantic
review, packaging, live-runtime, and human-acceptance boundaries. Those gates
remain open unless a narrower evidence record explicitly says otherwise.
