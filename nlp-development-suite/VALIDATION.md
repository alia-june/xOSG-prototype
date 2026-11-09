# Export validation

Validation was run against the staged export, not only the source workspaces.

| Project | Check | Result |
|---|---|---|
| Lexicon Core | `python -m unittest discover -s tests -v` with `PYTHONPATH=src` | 22 passed |
| Lexicon Core | Draft 2020-12 schemas, supplied registry, and published fixtures | 2 schemas and 8 fixtures passed |
| Natural Language front end | full Python test discovery using the source workspace's pinned environment | 54 passed |
| Lexicon Atlas | `validate_build.py` | schema `lexicon-atlas-data/4`, 1,440,449 terms, structurally valid |
| Lexicon Atlas | JavaScript syntax checks | passed |
| File Atlas | `verify_frontend.mjs` | 12 checks passed across 37 rules |

The original pinned Python environment was used to supply installed dependencies during validation. It is excluded from the export. Recreate the bounded code-only validation environment with `requirements-prototype.txt`. The full `requirements-development.txt` retains its source-workspace dependency on an excluded local `aprompt` wheel and is not a reproducible installation contract for this sanitized export.

Package-manifest verification is recorded in the external export receipt after the final archive is created. Archive and member hashes demonstrate byte integrity, not semantic correctness or receiver acceptance.
