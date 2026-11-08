# Sister-machine handoff stub

[`handoff_stub.schema.json`](handoff_stub.schema.json) is a draft JSON Schema
for the planned front end. [`handoff_stub.example.json`](handoff_stub.example.json)
contains one **partial, unreviewed** logic candidate from the supplied full
prompt and one deliberately unparsed clause. Both preserve the source text and
line pointers. The example is generated interpretation, not recovered canon.

The sister machine's receiving schema is not yet known. This stub therefore
defines only a safe exchange boundary: source identity, candidate logic,
unresolved questions, adoption status, and an explicit `execution_allowed:
false`. The `ast` object is intentionally provisional. No current sister
machine API or executable rule engine has been inferred from the ZIP.

The source archive's `deterministic_ai_control_plane_v0_4` directory describes
a non-launching historical scaffold with a closed JSON mission contract. That
contract is not treated as the new axiom-ingestion interface.

Before integration, agree on the logic dialect, atom and variable types,
quantifier/scoping rules, modality, unknown/conflict semantics, identifier
namespace, review/adoption protocol, and versioned transport envelope. Keep
source evidence separate from the authority to apply an axiom.

The draft uses [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-validation)
for structure only. Schema validation cannot prove that natural English was
translated faithfully.

To reproduce the structural and source checks:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-handoff.txt
.\.venv\Scripts\python.exe .\validate_handoff_stub.py --archive "<USER_HOME>\Documents\Workbench\offload\synthetic_os_project_redux_2026-09-16.zip"
```
