# NLP Development Suite Staging Record

Status: **code-only branch candidate; not deployed or accepted as production**.

Remote branch, pull-request, and merge state are external facts and must be
verified against the repository rather than inferred from this file.

## Target

- Repository: `alia-june/xOSG-prototype`
- Branch: `feat/add-nlp-development-suite`
- Component path: `nlp-development-suite/`
- Basis: `origin/main` at `7c6f0ee`

The candidate was rebased from its original `0b0ed62` basis onto current
`origin/main` on 2026-11-08. The root README conflict was reconciled by retaining
the current project-directory structure and adding the suite to that structure.

## Source and transformation

- Prepared source archive: `NLP_SUITE_PROTOTYPE_REPO_2026-11-08_v7.zip`
- Archive SHA-256: `56e3909ce8b9f0f323390240cb1a1d778b08a3de24c1e3e1fecb2bc4d7df528c`
- Transformation status: generated sanitized export from the working NLP suite
- Source export inventory: 315 manifest-bound files, 2,704,305 bytes
- Staged inventory: 316 manifest-bound files, 2,705,711 bytes

Two inert historical evidence filenames were shortened during staging so a
clean Windows checkout remains below the practical path-length limit. The
receipt's internal previous-output path and the prototype manifest were updated;
the prior candidate content and its SHA-256 remain unchanged.

The staged component excludes private or local dictionaries, generated lexical
shards, historical review datasets, build artifacts, credentials, hosting
identifiers, and machine-specific paths. Runtime lexical data must be supplied
separately under `nlp-development-suite/DATA_POLICY.md`.

## Validation scope

The local pre-staging run recorded:

- 22 Lexicon Core tests;
- 42 Offline Interpreter tests;
- 4 controlled-grammar tests;
- 6 command-alias tests;
- 7 data-free command-line tests;
- JavaScript syntax checks;
- prototype policy, manifest, and identity scans;
- deterministic archive reproduction and extraction verification.

After Git staging, the same code-only profile passed from a clean checkout of
the index. This confirms that ignored-but-manifested Atlas front-end files and
packaged evidence are present in the proposed commit rather than available only
from the preparer's working tree.

The first GitHub Actions run exposed one hidden host dependency: the registry
test fell back to a developer-machine data root when `LEXICON_DATA_ROOT` was
unset. The test now builds a temporary synthetic registry and source-directory
fixture. It retains the same registry assertions without reading private or
external lexical data; the manifest records the changed test bytes.

The second GitHub Actions run reached the Offline Interpreter tests and exposed
a separate CI configuration defect: the workflow had not installed the suite's
declared validation dependencies, so `jsonschema` was unavailable. Both the
host workflow and the suite's portable workflow now install the pinned
prototype validation requirements before running the data-free checks. A clean
environment discriminator then showed that the full `requirements-development.txt`
also references a local `aprompt` wheel intentionally omitted from the sanitized
export. The new `requirements-prototype.txt` isolates only the pinned dependency
needed by this bounded profile. A further clean-install discriminator rejected
the Offline Interpreter's editable source-development requirement because its
relative Lexicon Core path is not a portable host-repository install target;
the prototype runner already supplies that component through its bounded
`PYTHONPATH`. This does not add a runtime dependency to the dependency-free
basic interpreter mode.

After that correction, fresh virtual environments on Python 3.11, 3.12, 3.13,
and 3.14 each installed only `requirements-prototype.txt` and passed the full
data-free runner against an intentionally empty `LEXICON_DATA_ROOT`: 22 Lexicon
Core, 42 Offline Interpreter, 4 grammar, 6 command-alias, and 7 bounded
read-only command tests, plus all JavaScript syntax and prototype-boundary
checks.

The root workflow `.github/workflows/nlp-suite-code-only.yml` makes the nested
suite checks active for this host repository on Python 3.11 through 3.14. A
passing workflow would validate only this declared code-only profile. It would
not validate external dictionaries, lexical completeness, semantic correctness,
live hosting, production readiness, or human acceptance.

## Repository evidence boundary

The root `EXPORT_MANIFEST.json` and `EXPORT_VALIDATION.md` predate this branch.
They are retained as historical export evidence and are not silently rewritten
to describe the new staging state. This record is the branch-specific handoff.

The host repository deliberately applies `* -text` so supplied evidence remains
byte-for-byte stable. `git diff --check` therefore reports retained whitespace
or CRLF findings in eight imported component files. Newly authored host files
pass the same check when the preserved component is excluded. Normalizing the
imported bytes would invalidate their manifest hashes and is not part of this
staging change.
