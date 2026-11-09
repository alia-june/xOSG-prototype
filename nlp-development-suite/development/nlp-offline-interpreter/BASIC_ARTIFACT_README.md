# NLP Offline Interpreter 0.1.0 — Basic artifact

## Status and boundary

This is a user-directed, local downloadable artifact. No approver is required
for this bounded artifact. It is not evidence of external deployment,
production readiness, receiving-authority acceptance, or canon admission.

The basic mode is deterministic and dependency-free. It performs bounded
surface tokenization and reports exact source spans, counts, and truncation.
It does not infer intent, execute an operation, use the network, or mutate
external state.

## Install

Python 3.11 or newer is required. From the unpacked artifact directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index --no-deps .\wheel\nlp_offline_interpreter-0.1.0-py3-none-any.whl
```

## Run the basic function

```powershell
.\.venv\Scripts\nlp-offline-interpreter.exe --basic "Hello, generic world!"
```

Or use the module entry point:

```powershell
.\.venv\Scripts\python.exe -m nlp_offline_interpreter --basic "Hello, generic world!"
```

The command emits canonical JSON using `generic-interpretation/1`. Successful
output keeps `authority_effect` as `NONE` and `execution_allowed` as `false`.
Inputs are limited to 4,096 characters and retained output to 256 tokens.

## Verify

Run the verifier from the source suite against the ZIP before unpacking it:

```powershell
python .\VERIFY_BASIC_ARTIFACT.py .\dist\nlp-offline-interpreter-0.1.0-basic.zip
```

Inside the ZIP, `ARTIFACT_MANIFEST.json` and `SHA256SUMS.txt` bind every payload
member by path, byte size, and SHA-256 digest.

## Optional suite integration

`--check-integration` reports whether the separate Lexicon Core and Natural
Language modules are available. Those optional modules are not required for
`--basic` and are not bundled in this artifact.
