# v0.5 provenance and claims ledger

- Source baseline: the retained v0.4 source archive (local development artifact; not a network dependency).
- Preserved source witness: `source_witness/check_manifest_v0_2.py` and original `source_witness/SHA256SUMS.json`.
- Preserved core worker logic: `microtrans/schema_gate.py`, `microtrans/graph_gate.py`, `microtrans/glue.py` and core protocol (byte-parity to be checked in final package).
- Deliberate updated entry: `microtrans/governed.py`, selecting fixed Windows AppContainer launch on `win32` and Linux v0.4 otherwise.
- New source: `windows/native.py`, `windows/launcher.py`, `windows/policy.py`, `windows/profiles.py`, `windows/smoke.py`, `runtime/windows_entry.py`, `runtime/windows_probe.py`, `tests/test_windows_v0_5.py`.
- New documentation: `WINDOWS_IMPLEMENTATION.md`, `FAIL_CLOSED_MATRIX_v0_5.md`, `WORKING_RESEARCH_PROMPT_v0_5.md`, this ledger.

Claims:

| ID | Claim | Evidence / status |
|---|---|---|
| C01 | v0.4 Linux reference behavior retained | Linux regression tests; full test run results recorded separately |
| C02 | Windows launch path refuses unsupported host/service | Cross-platform tests |
| C03 | Windows AppContainer and Job Object APIs are wired | Source inspection only; **not Windows execution** |
| C04 | Windows kernel actually isolates workers | `SENTINEL_UNRESOLVED`; **requires Windows host evidence** |
| C05 | Probe denies file, TCP and child processes | `SENTINEL_UNRESOLVED`; **requires Windows host evidence** |
| C06 | Crete, signed attestations and admission authority implemented | **No** |

Historical v0.4 documents are in `lineage/v0_4_reports` and are not upgraded to v0.5 evidence. Changes to Windows policy are candidates until operator/independent validation.
