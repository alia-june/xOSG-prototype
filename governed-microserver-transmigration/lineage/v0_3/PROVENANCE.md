# Source / destination provenance ledger

| Item | Classification | Path | Observed or designed relationship |
|---|---|---|---|
| v0.2 manifest checker | Historical original witness | `source_witness/check_manifest_v0_2.py` | Unchanged bytes copied from previously generated v0.2 source |
| v0.2 manifest schema | Historical original witness | `contracts/manifest_v0_2.schema.json` | Unchanged bytes copied from v0.2 source |
| v0.2 sample manifest | Historical sample witness | `examples/source_manifest_v0_2.json` | Unchanged v0.2 candidate manifest |
| New strict JSON protocol | Candidate new implementation | `microtrans/protocol.py` | Reconstructed local transport and refusal framing |
| Schema microserver | Candidate new implementation | `microtrans/schema_gate.py` | Extracted behavior via pinned schema, new bounded process |
| Graph microserver | Candidate new implementation | `microtrans/graph_gate.py` | Reconstructed duplicate, endpoint, type alignment, join and cycle checks |
| Local glue | Candidate new implementation | `microtrans/glue.py` | No equivalent execution layer existed in v0.2; newly designed candidate |
| Contract artifacts | Candidate new implementation | `contracts/*v0_3.schema.json` | New versioned JSON request, response, receipt shapes |
| Differential tests | Candidate verification evidence | `tests/test_transmigration.py` | Compares original and target decisions on a selected 19-case corpus |

**Witness SHA-256:** `source_witness/check_manifest_v0_2.py` = `c45a747ccca6107cdbc83ad692fc2f984e78502b93ae653b44e68d16d1a402e1`.  
**Schema SHA-256:** `contracts/manifest_v0_2.schema.json` = `901e4572faf66153060c9e01f2b8533faaa3be43fb7963ebf3fda2f44f536afe`.

These hashes identify the copied bytes; they do not prove their original authorship, the absence of compromise, or runtime security. Microserver names and the v0.3 protocol are newly defined candidates; their details were **not** present as runnable behavior in v0.2.
