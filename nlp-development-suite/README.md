# NLP Suite Prototype Repository

Status: code-only, identity-reduced prototype staging tree. It is not a production deployment or semantic authority.

This repository keeps the suite's separable projects and integration contracts while excluding private/local dictionaries, generated lexical shards, historical review datasets, build artifacts, credentials, hosting identifiers, and machine-specific paths.

## Components

- `projects/lexicon-core`: reusable deterministic lexical primitives and proposal-only task adapters.
- `projects/natural-language-front-end`: controlled grammar and read-only command interpretation source.
- `projects/lexicon-atlas`: newer code-only Atlas interface; runtime dictionary data is not included.
- `projects/file-atlas`: bounded read-only browser file interface.
- `development/nlp-offline-interpreter`: generic non-executing interpretation core.
- `development/generative-relational-lexicon`: schemas, research code, and tests without generated lexical datasets.

## Data boundary

Set `LEXICON_DATA_ROOT` to a separately managed, policy-approved data location. Do not commit dictionary databases, generated shards, import inboxes, or local source archives. See `DATA_POLICY.md`.

Run `python -B RUN_PROTOTYPE_CHECKS.py` before creating a remote repository or deploying a preview.
