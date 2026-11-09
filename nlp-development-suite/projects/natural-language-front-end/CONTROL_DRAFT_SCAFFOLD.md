# Control Draft parser scaffold

Status: generated proposal-only scaffold, `control-draft-scaffold/0.1`; not reintegrated and not accepted by the sister machine.

This scaffold is based on `Control_Draft_Parser_Reintegration_Spec_v0.1.zip`. It creates the exchange seam for a future questionnaire parser while preserving the current command and WordNet front ends. It stores exact source text, UTF-8 hashes, Unicode code-point spans, question IDs, candidate IDs, layer traces, unresolved reasons, review status, and a rule-set digest.

`parse_answer()` currently abstains on ordinary prose with `unparsed` and an explicit unresolved reason. Fenced text is retained as source and also remains unparsed. This is intentional: no contract-field extraction rule has been admitted yet. `make_candidate()` provides a validated constructor for future deterministic rules. `review_candidate()` records an explicit user decision, and `DraftProjectionAdapter.project()` creates an in-memory transformation ledger only after acceptance. It performs no file, network, shell, site, or sister-machine operation.

The scaffold does not replace `omni_cli.py`, does not route WordNet definitions into contract fields, and does not claim to implement the 18 exported evaluation cases. WordNet remains lexical evidence; it cannot choose authority, obligation, prohibition, approval, or scope.

## Smoke test

```powershell
.\.venv\Scripts\python.exe -c "from control_draft_scaffold import parse_answer; print(parse_answer('The agent may create a draft.', question_id='authority').as_dict())"
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
```

The next implementation increment is to add one reviewed deterministic rule family at a time, bind each rule to the exported candidate schema, add evaluation cases, then validate explicit review and policy projection. The scaffold must remain proposal-only until the sister-machine contract and acceptance gates are confirmed.
