# Sistermachine contract integration

**Result:** The local English parser's full-prompt ledger is mapped into valid
aPROMPT 1.1.0 meaning documents. Every statement is unresolved and every
fragment has an unsupported issue. No axiom, executable expression, approval,
prepared contract, SafeAPI request, or remote transfer was generated.

## Source inventory

| ID | Supplied source | Integrity and authority |
|---|---|---|
| A1 | `<USER_HOME>\Desktop\Inbox\SISTERMACHINE_CONTRACT.md` | SHA-256 `3A2F88DC7A9730E5ED7A7C603050C8B31072D683957130D6A176952EDB9702D3`. User-supplied interface description, copied byte-for-byte to `vendor/SISTERMACHINE_CONTRACT.md`. Its claims about wider runtime behavior were not treated as an instruction to execute. |
| A2 | `<USER_HOME>\Desktop\Inbox\aprompt-1.1.0-py3-none-any.whl` | SHA-256 `9BACCBAD73341E47265E1321BFC9367AEDCE904F6FDc4BA8862AF87010C68257`, copied byte-for-byte to `vendor/`. All 57 hashed RECORD entries matched; 58 member names had no unsafe paths, duplicates, or case collisions. |
| A3 | `FRONTEND_FULL_PROMPT_CANDIDATES.json` | Legacy full-prompt ledger, SHA-256 `D901F9B1F1E65433B57E290E977E60834F05911E9A95122765B9AD66F77F84D4`; archive/member hashes and all 1,196 source quotes revalidated before adaptation. |
| A4 | `sister_handoff_2026-09-16_v1/manifest.json` | Generated local handoff manifest, SHA-256 `725937E64AA68F862EC96185ADB690F0C4D64B56AE622B5D0AC83A74DD48AD64`. This is generation evidence, not receiver acceptance. |
| A5 | `sister_handoff_2026-09-16_v1_unresolved.zip` | 76 verified members (A4 plus 75 meaning documents), SHA-256 `8FAC0B933993FF410E6C6EF67BAAE2AB1B04B555C67C71ECE2BB97C54DDC31D0`. Local review package only. |

## Exact mapping

The aPROMPT meaning schema is closed. The adapter makes one `sources` item per
legacy fragment, with the **exact fragment text** and its lowercase UTF-8
SHA-256. `source_refs` span `[0, len(text))` in Python Unicode code points.
Identifiers encode the original line and sentence number: `L22-S1` becomes
`SrcL22S1`, `StmtL22S1`, and `IssueL22S1`. The legacy ledger retains the ZIP
member path and line pointers; the manifest pins that ledger's hash.

Every mapped statement has `kind: unresolved`, `epistemic: unknown`,
`expression: null`, `derived_from: []`, and `adoption: null`. Every issue has
`kind: unsupported` and a source reference. This is intentional: the current
candidate AST uses modal operations such as `prohibit` and `obligate`, while
`ground-boolean/1.0` supports only atom, literal, not, all, any, and implies.
Mapping a prohibition to a Boolean atom would discard its normative force.
The adapter does not infer an adopting actor or scope from the prompt.

The 1,196 fragments are split into **75 meaning documents**, at most 16
sources each, respecting the receiving schema. All documents were checked by
the packaged JSON Schema, `decode_contract_json`, and `validate_meaning` before
publication and again from staged bytes. Every installed aPROMPT package file
was compared byte-for-byte with A2. A direct `prepare_contract` test
rejects these documents with `UNRESOLVED_ISSUES`, as required by the contract.
The 26 current local tests pass. A controlled Boolean slice produces a
separate synthetic example; see
`CONTROLLED_BOOLEAN_SLICE.md`. It does not change this full-prompt handoff.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-sister.txt
.\.venv\Scripts\python.exe .\sister_adapter.py --archive "<USER_HOME>\Documents\Workbench\offload\synthetic_os_project_redux_2026-09-16.zip" --output-dir .\sister_handoff_new_generation
.\.venv\Scripts\python.exe .\package_sister_handoff.py --directory .\sister_handoff_new_generation --output .\sister_handoff_new_generation_unresolved.zip
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
```

The adapter only creates a **new** output directory; it does not replace a
prior handoff. The selected transport, receiver authentication, semantic
review of English-to-logic translations, adoption records, and the trusted
host's approval flow are outside this local publication. This work verifies
the meaning-document boundary, not a completed sister-machine operation.
