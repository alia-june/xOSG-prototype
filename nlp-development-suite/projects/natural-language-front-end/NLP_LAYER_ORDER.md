# Deterministic NLP layer order

Status: generated local interface, `omni-intent/0.4`; not adopted by the sister machine. The current order is:

```text
1. Explicit alias grammar
2. Pinned Open English WordNet 2025
3. Confirmed choices in the current CLI session
4. Optional web proposal provider
5. Optional LLM proposal provider
```

An explicit alias with one meaning may reach a registered read-only adapter. A direct alias collision displays every ranked meaning and does not execute. If no alias matches, WordNet's second layer checks whether the first verb shares a **verb synset** with a small set of reviewed command verbs. It substitutes that verb into the explicit grammar to form suggestions. The shared synset ID and release are included as evidence; no WordNet sense is selected as contextually correct. WordNet suggestions only produce `safe_display`, even when there is one option. The implementation uses the pinned [Wn 1.1.1 API](https://wn.readthedocs.io/en/latest/api/wn.html) and the local `oewn:2025` data.

History is in memory for one interactive CLI session. After a collision or proposal is shown, the user can enter one displayed explicit command. The program records that choice for the original wording, then uses it to rank future appearances of the same wording. It still displays all collision meanings and never treats history as authorization. No command text is persisted by default.

Web and LLM are **provider hooks**, not active services in the CLI. A host application can pass a web provider and an LLM provider to `parse_command`. If earlier layers produce no proposal, the web hook is called before the LLM hook. Provider outputs must name an existing capability, supply exact typed arguments, and include a source. Web proposals require an HTTPS source URL. These are unverified proposals; they are displayed for explicit selection and cannot dispatch an adapter. Unknown capabilities, malformed fields, control characters, and oversized proposal lists are rejected. The CLI does not send user text to a website or model by default.

## Sample

```powershell
.\.venv\Scripts\python.exe .\omni_cli.py --human "seek for ground-boolean in CONTROLLED_BOOLEAN_SLICE.md"
```

The alias layer does not match `seek for`. WordNet finds the verb synset shared by `seek` and `search` (`oewn-01318273-v`), so the output displays `search for "ground-boolean" in "CONTROLLED_BOOLEAN_SLICE.md"`. No search runs until that explicit command is entered.

`layer_trace` in the intent records the stages actually consulted, with statuses such as `parsed`, `no_match`, `suggestions`, `not_configured`, or `invalid_or_failed`. A stage not listed was not consulted because an earlier stage produced a result or input validation stopped the pipeline. This trace describes local proposal generation, not axiom adoption or Blue Key conformance.
