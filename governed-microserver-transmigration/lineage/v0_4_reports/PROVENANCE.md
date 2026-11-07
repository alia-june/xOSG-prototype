# v0.4 provenance and state ledger

| Asset | Status | Source / relationship |
|---|---|---|
| `source_witness/check_manifest_v0_2.py` | PRESERVED_SOURCE_WITNESS | Original v0.2 static checker bytes, unchanged from v0.3 |
| `contracts/manifest_v0_2.schema.json` | PRESERVED_CONTRACT_WITNESS | Historical schema dependency, unchanged |
| `microtrans/{protocol,schema_gate,graph_gate,glue,schema_validation}.py` | PRESERVED_v0_3_CANDIDATES | Unmodified functional source from v0.3 |
| `authority/gate.py`, policy JSON | NEW_CANDIDATE | Independent preflight evaluator; no principal authentication |
| `runtime/mount_entry.py`, `worker_entry.py`, `probe.py` | NEW_CANDIDATE | Linux strict boundary and negative probe |
| `microtrans/governed.py` | NEW_CANDIDATE | Orchestrates policy, namespaced workers and audit |
| `external_validator/validator.py` | NEW_CANDIDATE | Independent graph algorithm, but shared JSON Schema and host |
| `contracts/*v0_4.schema.json` | NEW_CANDIDATE | Versioned request and receipt constraints |
| `tests/test_governed_v0_4.py` | EXECUTED_TEST_EVIDENCE | Controlled negative tests and valid/refusal chain checks |
| `research/landlock_guard_UNWIRED.py` | ABORTED_RESEARCH_FRAGMENT | Host Landlock syscall version query returned ENOSYS; not activated |
| `lineage/v0_3/` | PRESERVED_HISTORY | Previous docs retained as historical statements |

**Source witness checksum:** `c45a747ccca6107cdbc83ad692fc2f984e78502b93ae653b44e68d16d1a402e1`  
**Manifest schema checksum:** `901e4572faf66153060c9e01f2b8533faaa3be43fb7963ebf3fda2f44f536afe`

SHA-256 establishes byte identity inside this package, not trusted provenance or signature. All new components remain candidates.
