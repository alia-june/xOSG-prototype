# Executed validation report — candidate v0.3.0

**Date:** 2026-11-06  
**Environment:** Python 3.13.5 on Linux, `jsonschema` 4.26.0  
**Disposition:** CANDIDATE_ONLY / NOT_ADMITTED / NOT_PUBLISHED

## Results observed in this environment

- `python -m unittest discover -s tests -v`: **19 tests; 19 passed; no failures or errors**. Full captured output: `TEST_RESULTS.txt`.
- Source parity: one valid v0.2 manifest and 18 negative/modified manifests compared with unchanged v0.2 `check_manifest.py`; no accept/reject mismatches observed among the 19 cases.
- Direct JSON CLI invocation: both independent microserver processes accepted the original valid manifest.
- Full glue path: original v0.2 sample manifest produced `STATIC_PASSED` and a two-service execution transcript.
- Full glue path: v0.3 self-manifest produced `STATIC_PASSED` and a two-service execution transcript.
- Deliberately broken graph endpoint: glue emitted `REFUSED`, never `STATIC_PASSED`.
- Four JSON Schema documents passed Draft 2020-12 meta-schema checks.
- Two captured example composition receipts passed the v0.3 receipt schema.
- Controlled fault tests verified rejection of excessive authority, duplicate JSON members, invalid/multiple protocol messages, `null`, NaN/non-finite overflow, oversized input, tampered application payload and tampered graph digest.
- Controlled refusal test verified that upstream schema refusal stops dispatch of the graph microserver.

## Test coverage boundaries

| Claim | Status | Reason |
|---|---|---|
| Two JSON CLI microservers are runnable | TESTED_LOCALLY | Both invoked as distinct child processes |
| Example data is passed by identity-only ordinary glue | TESTED_LOCALLY | Exact application-data comparison and digest checks in reference graph |
| Selected v0.2 behavior preserved | TESTED_ON_CORPUS | 19 manifests; not exhaustive |
| All v0.2 behavior equivalent | NOT_PROVEN | Finite differential tests only |
| Schema compatibility and declared join rules | STATICALLY_TESTED | v0.2 checker logic + JSON Schema |
| Independent semantic validator | NOT_IMPLEMENTED | Reuses pinned schema and same project codebase |
| OS-enforced least privilege | NOT_PROVEN | Subprocesses not in distinct privilege sandbox |
| IPC authenticity/replay protection | NOT_IMPLEMENTED | Digest equality alone is not authentication |
| Crete break-before-mutation guarantee | NOT_IMPLEMENTED | Only v0.2 declarative checks exist |
| Windows 11 LTSC compatibility | NOT_TESTED | Executed on Linux |
| Admission and publication | NOT_IMPLEMENTED | Both hardcoded negative dispositions |
| HTTP microserver interface | NOT_IMPLEMENTED | Local JSON CLI is the chosen reference transport |

## Reproducibility and source identity

Read `source_witness/SHA256SUMS.json` for the unchanged v0.2 source checksum and schema checksum. The output receipt digests are SHA-256 values of deterministic JSON serialization; no cryptographic key or signature is used. The `CHECKSUMS_SHA256.txt` package file enumerates all other source and artifact file hashes after generation; it does not attest provenance outside the local package.

**Conclusion:** A bounded candidate microserver + ordinary-glue reconstruction was built and tested locally. No stronger assurance is justified by the available evidence.
