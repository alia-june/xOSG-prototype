# P04 staging package

## Status

This is the bounded staging package for `nlp-offline-interpreter/0.1`. P03 was
verified on 2026-10-02 after Q-001 through Q-007 and the bounded production
plan were accepted. P04 is verified for the bounded local release after a
canonical Python 3.11 run from a clean Git commit passed the full baseline and
reproduced the release wheel byte-for-byte.

## Proven scope

- CPython 3.11 through 3.14 on the current Windows host;
- 15 exact direct, transitive, build, and local test dependencies;
- an offline wheelhouse with byte hashes;
- a fresh virtual environment with network-disabled installation;
- the successor, production-control, Lexicon Core, and Natural Language tests;
- two deterministic wheel builds;
- a bounded high-confidence secret scan.

Another operating system and a remote CI provider remain unverified.

## Files

- `requirements-py314.in`: reviewed exact dependency versions.
- `requirements-py311.lock` through `requirements-py314.lock`: generated
  runtime-specific hash-locked installation inputs.
- `WHEELHOUSE_MANIFEST.json`: exact offline wheel inventory.
- `BUILD_WHEELHOUSE_MANIFEST.py`: refuses overwrite and creates the inventory.
- `VERIFY_P04_STAGE.py`: validates policies, lock, wheelhouse, and boundaries.
- `SCAN_SECRETS.py`: bounded high-confidence local scan.
- `RUN_CLEAN_STAGE.py`: creates a fresh environment, installs offline, tests,
  and builds twice.
- `REPOSITORY_POLICY.md`, `GENERATED_DATA_POLICY.md`, `SECRETS_POLICY.md`, and
  `CI_CONTRACT.md`: staging controls governed by the accepted bounded plan.
- `.github/workflows/ci.yml`: active repository workflow for the verified 3.14
  Windows slice; no remote execution has yet been observed.
- `templates/github-actions-ci.yml`: inert broader support-matrix example.

## Reproduce

From the suite root, after the wheelhouse has been provisioned:

```powershell
python .\production\p04\VERIFY_P04_STAGE.py
python .\production\p04\RUN_CLEAN_STAGE.py --report .\production\reports\p04-stage-NAME.json
```

Reports are append-only and confined to `production/reports`.
