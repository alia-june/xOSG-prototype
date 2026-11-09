# NLP Offline Interpreter

Status: accepted bounded local-release implementation slice; not
production-ready, deployed, or receiving-system accepted.

This project provides a generic deterministic interpretation contract. It is
kept outside the immutable exported projects so new development cannot be
confused with the verified historical snapshot.

## Generic core

`nlp_offline_interpreter.core` defines:

- arbitrary ordered interpretation layers through a small protocol;
- domain-neutral operation names and JSON-compatible arguments;
- exact source text, SHA-256, and Unicode character length;
- candidate provenance, evidence, optional spans, and confidence semantics;
- explicit unresolved regions and layer diagnostics;
- `first_candidate` and `collect_all` policies;
- deterministic canonical JSON;
- immutable detached JSON-like inputs and strict public-object invariants;
- explicit bounds for layers, provider output, diagnostics, JSON depth/items,
  source length, and task-module adapters;
- fixed `authority_effect: NONE` and `execution_allowed: false` values.

The core has no dependency on WordNet, the catalog, file operations, an LLM,
the web, or the existing front end. It has no execution interface.

## Suite integration

`nlp_offline_interpreter.integration` adapts two existing source components:

1. the Natural Language front end as the primary deterministic alias and local
   lexical-candidate layer;
2. Lexicon Core task modules as proposal-only fallbacks.

The integration is staged against the exported source trees. The standalone
wheel intentionally remains dependency-free; optional suite adapters are not
bundled and must be supplied separately when explicitly used.

The wheel can inspect this optional boundary without those sources installed:

```powershell
python -m nlp_offline_interpreter.integration --check-integration
python -m nlp_offline_interpreter --check-integration
nlp-offline-interpreter --check-integration
```

The command emits `nlp-offline-integration-status/1`, lists missing modules,
retains `execution_allowed: false`, and returns exit code 4 when the adapters
are unavailable. Importing the integration module itself no longer requires
the historical suite packages.

From the suite root, run the staged CLI with:

```powershell
$env:PYTHONPATH = '.\development\nlp-offline-interpreter\src;.\projects\lexicon-core\src;.\projects\natural-language-front-end'
python -m nlp_offline_interpreter.integration --no-wordnet "find files named report in ."
```

The CLI only emits an interpretation plan. There is no execute option.

The installable wheel currently guarantees the dependency-free generic core.
Using the suite integration still requires Lexicon Core plus the Natural
Language source modules on `PYTHONPATH`; it is not a self-contained wheel
capability. Its availability and failure state are now explicit and
machine-readable.

For byte-reproducible local wheels, set `SOURCE_DATE_EPOCH=1704067200` before
the PEP 517 build. `BUILD_VALIDATION.json` retains the earlier Python 3.14
development-build evidence. The canonical P04 Python 3.11 receipt is recorded
in `production/reports/p04-stage-2026-10-02-authorized-py311.json`; it produced
two byte-identical wheels. Neither record is the future immutable P08 release
candidate or cross-platform attestation.

## Rebuild the licensed wheel candidate

Version **0.1.1rc1** packages the five implementation modules under
**MIT OR Apache-2.0**. The license texts and copyright notice are in
[LICENSES/](LICENSES/). The historical P06 records describe the earlier
0.1.0 wheel.

On Windows with Python 3.14.3, run the following from this project directory
to stage just the wheel inputs in a new temporary folder. The build uses the
setuptools version pinned in `pyproject.toml`.

```powershell
$project = (Get-Location).Path
$stage = Join-Path $env:TEMP ("nlp-offline-wheel-" + [guid]::NewGuid().ToString("N"))
$source = Join-Path $stage "source"
$package = Join-Path $source "src\nlp_offline_interpreter"
New-Item -ItemType Directory -Path $package -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $project "pyproject.toml") -Destination $source
Copy-Item -LiteralPath (Join-Path $project "LICENSES") -Destination $source -Recurse
$modules = "__init__.py", "__main__.py", "basic.py", "core.py", "integration.py"
foreach ($module in $modules) {
    Copy-Item -LiteralPath (Join-Path $project "src\nlp_offline_interpreter\$module") -Destination $package
}
$env:SOURCE_DATE_EPOCH = "1704067200"
$dist = Join-Path $stage "dist"
python -m pip --isolated --disable-pip-version-check wheel --no-deps --no-cache-dir --index-url https://pypi.org/simple --wheel-dir $dist $source
Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $dist "nlp_offline_interpreter-0.1.1rc1-py3-none-any.whl")
```

The validated wheel SHA-256 is
`740e838f120f3727b586cf68521884be9b7776bdbf3f061307653fab1b3c5a9b`.

## Tests

```powershell
$env:PYTHONPATH = '.\development\nlp-offline-interpreter\src;.\projects\lexicon-core\src;.\projects\natural-language-front-end'
python -m unittest discover -s .\development\nlp-offline-interpreter\tests -v
```

The JSON Schema is `schemas/generic-interpretation-v1.schema.json`.
`BUILD_VALIDATION.json` records the isolated wheel build and clean temporary
installation check. `DEVELOPMENT_MANIFEST.json` records the exact successor
source set and is verified by `VERIFY_MANIFEST.py`.

The test tree separates contract and integration checks from deterministic
loose/fuzzy and torture suites. The current fuzzy seed is `20261001`; torture
coverage includes maximum accepted boundaries, 50,000 repeated calls, and
5,000 calls distributed across eight worker threads. These are P05 bounded
implementation tests, not production performance or security certification.
