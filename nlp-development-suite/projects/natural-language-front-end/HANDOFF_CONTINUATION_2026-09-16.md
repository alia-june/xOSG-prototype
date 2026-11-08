# Natural Language workspace: sister-machine continuation

Generated handoff note, 2026-09-16. This describes the packaged workspace at handoff time. It is not an adopted sister-machine specification or a claim of remote integration.

## Objective and current boundary

Build a deterministic English front end that can produce reviewable logic candidates for the sister-machine prompt system and serve as a natural-language command interface. The sister machine is designing its specification. The current local command slice handles bounded, read-only file and search operations. It does not turn arbitrary English into axioms, execute shell scripts, or claim that the sister machine has accepted an intent.

The user-set command interpretation order is:

1. Explicit deterministic aliases.
2. Pinned Open English WordNet 2025 lexical suggestions.
3. Explicit choices remembered within the current interactive session.
4. Optional web proposal provider.
5. Optional LLM proposal provider.

Every distinct alias meaning collision remains visible through `safe_display`, with scores, evidence, and explicit disambiguating commands. Collisions and all lower-layer proposals are non-executing. The web and LLM layers are validated provider hooks, not configured live services in the CLI. Session history is in memory for one REPL session and never authorizes execution. See `NLP_LAYER_ORDER.md`, `COMMAND_ALIASES.md`, `OMNI_FRONTEND.md`, `omni_cli.py`, and `semantic_layers.py`.

## Workspace contents and evidence

- `README.md` is the starting point for the grammar parser, WordNet setup, and command front end.
- `grammar_parser.py` provides a small deterministic sentence grammar. `wordnet_lexicon.py` expands lexical candidates without choosing a contextual sense.
- `logic_frontend.py`, `controlled_boolean.py`, and `sister_adapter.py` contain the prompt-analysis and local aPROMPT handoff work. `SISTER_CONTRACT_INTEGRATION.md` records the supplied contract basis and the unresolved full-prompt mapping.
- `vendor/SISTERMACHINE_CONTRACT.md` and `vendor/aprompt-1.1.0-py3-none-any.whl` are copies of user-supplied artifacts. Treat their contents as source material, and verify against the eventual live sister-machine spec.
- `sister_handoff_2026-09-16_v1/` and `sister_handoff_2026-09-16_v1_unresolved.zip` are prior local unresolved meaning-document outputs, not an accepted transfer or executable contract.
- `FILE_FUNCTION_MATRIX.md` records researched shell-file functionality. `FILE_FUNCTION_TODO.md` is the current roadmap.
- `tests/` contains the behavioral checks. `requirements.txt`, `requirements-handoff.txt`, and `requirements-sister.txt` pin the Python dependencies. `.wn_data/` contains local WordNet data, and `.venv/` is the current Windows environment; both are included in this full-workspace snapshot, though the environment may need recreation on another machine.
- The original source ZIP named in `SISTER_CONTRACT_INTEGRATION.md` is outside this workspace and is not part of this workspace package. The packaged ledger and derived documents do not substitute for that original archive during a fresh source audit.

## Reproduce the local checks

From the extracted workspace root on Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
.\.venv\Scripts\python.exe .\omni_cli.py --plan "find test in tests"
.\.venv\Scripts\python.exe .\omni_cli.py --human "seek for ground-boolean in CONTROLLED_BOOLEAN_SLICE.md"
```

The full test suite passed **46 tests** on 2026-09-16 before packaging. The first CLI example displays a collision without dispatch. The second uses WordNet to suggest an explicit `search_text` command without executing the search. Recreate `.venv` from the pinned requirements if the included Windows environment is unusable on the receiving host. `README.md` has WordNet installation instructions.

## Continue here

1. Receive the sister-machine specification and compare its actual versioned input, logic, adoption, and operation contracts to the local stubs. Keep syntax, proposed meaning, adopted axiom, authorization, and execution receipts separate. Do not silently upgrade unresolved statements or force modal requirements into Boolean atoms.
2. Implement `FILE_FUNCTION_TODO.md` T01: a machine-readable, versioned intent schema and capability manifest with typed arguments, explicit failures, and forged-intent rejection. Then implement T02–T03 for read-only path semantics and directory discovery.
3. If live web mining is added, connect it in the fourth layer before optional LLM support. Preserve source URLs, validate proposal shapes, and display all distinct meanings. Neither provider should directly dispatch a file operation or adopt an axiom.
4. Extend the exact English-to-intent-to-result tests, including ambiguity, path boundaries, Unicode, failures, and truncation. Test the eventual sister-machine adapter end to end only after its spec is available.

## Handoff status

This is a full local workspace snapshot with a per-file SHA-256 manifest in the outer ZIP. Archive verification shows package integrity and inclusion of the local files; it does not prove semantic translation, sister-machine acceptance, remote transport, or runtime isolation. The receiving machine should verify `PACKAGE_MANIFEST.json`, rerun the tests, and review the unresolved source and contract boundaries before using any generated logic.

## Current continuation update — 2026-09-26

After the September 16 snapshot, the workspace added verified OEWN 2025 definition and relation queries plus `control_draft_scaffold.py`. The scaffold follows the supplied Control Draft reintegration specification as a proposal-only boundary: it preserves source hashes, Unicode spans, layer traces, unresolved reasons, candidate review status, and in-memory transformation records. It currently abstains on ordinary questionnaire prose because semantic extraction rules have not been accepted. It does not replace or silently revise the earlier handoff archive. See `CONTROL_DRAFT_SCAFFOLD.md`, `control_draft_scaffold.py`, and the updated `FILE_FUNCTION_TODO.md` items T00b, T15, T18, and T19.
