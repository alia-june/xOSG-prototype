# Export exclusions

The export intentionally omits:

- Git object databases and credentials;
- Python virtual environments;
- `__pycache__`, bytecode, and transient caches;
- raw dictionary source junctions and the complete Wiktionary JSONL extraction;
- ignored `.lexical_sources`, `node_modules`, and build-output directories;
- nested ZIP archives that duplicate unpacked handoff directories;
- source-repository write tokens and other secrets.

Tracked Lexicon Atlas browser shards are included because they are the reproducible runtime data for the packaged static site. Their inclusion does not substitute for the raw sources when rebuilding the data.

Git commits are recorded in `PROJECT_INVENTORY.json`, but repository history and branches are not included. Initialize new repositories in the destination project if continued version control is desired.
