# Publication and review notes - 28 November 2026

Universal Program Wrapper v0.1 is a Python reference implementation of a common JSON request/response boundary for explicitly declared program operations. It provides introspection, manifest-driven legacy CLI dispatch, embedded native handlers, and normalized results.

## Privacy review and provenance

All 17 supplied text files were reviewed for personal identifiers, email addresses, user/machine paths, credentials, private endpoints and identifying metadata. No private identifiers requiring substitution were found. The supplied files are therefore published unchanged beneath this descriptive project directory. The Python executable in the example manifest is already a generic placeholder. Public JSON Schema references, operation IDs and project terminology are retained.

The source ZIP is retained separately and is not published here. Detailed local intake paths and private audit records are not included. No new license, ownership claim or authorship attribution is assigned. Existing package wording, including CANON.md, is preserved as source context; publication does not independently adopt those rules across this repository or grant execution authority.

## Implemented boundary

The package implements one JSON request per CLI invocation, operation lookup and selected input checks, absolute-path legacy executable selection, argument-list construction with shell=False, selected environment inheritance, subprocess result capture, output normalization and registered in-process native handlers. An absolute executable path and shell=False do not establish containment or permission to invoke an operation.

Authority-context and provenance fields are carried as data. Capability and side-effect declarations remain declarations. The safety-policy/containment layer, BitCore verifier, catalog, state-witness machinery and kernel/driver functions described as surrounding architecture are not implemented by this package.

## Known implementation limits from static inspection

- The JSON Schema documents are supplied, but runtime validation is handwritten and does not enforce every schema constraint. Request timeout bounds and rejection of extra top-level fields are examples of differences.
- A launched program whose output fails declared JSON normalization can produce a wrapper-error response that omits the already captured raw process result.
- Timeout handling passes captured output through without explicit normalization; that path needs qualification for JSON serialization.
- The status control reports ready after manifest construction without establishing executable availability or native-handler registration.
- Subprocess output is captured without a size bound. Requests can override adapter timeouts. Process-tree containment and enforcement of declared side effects are not supplied.
- Native handlers default to SUCCESS when they omit wrapper_outcome. This needs qualification against the stated outcome contract.

These are source-inspection findings, not reproduced runtime failures. No functional repairs are included in this publication.

## Validation performed for publication

The intake checked ZIP integrity, all-file privacy review, UTF-8 decoding, JSON and TOML parsing, Python syntax via AST parsing, relative documentation links, exact file coverage, and byte identity for the unchanged source files. The supplied validate.py and tests/test_upw.py were inspected but not executed; no dependencies were installed and no wrapped program was launched.

The four supplied unit tests cover description, successful legacy invocation, rejection of extra operation input and duplicate-operation refusal. The supplied validator checks required paths, JSON parsing, Python compilation and selected forbidden strings; it does not itself establish full schema conformance or runtime qualification.

[Project overview](README.md) · [Architecture](ARCHITECTURE.md) · [Protocol specification](SPEC.md)
