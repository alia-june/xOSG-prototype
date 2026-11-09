# Ranked command aliases

Status: generated local alias system for `omni-intent/0.4`; the sister machine has not adopted it. The catalog is [command_aliases.json](command_aliases.json), validated and interpreted by [command_aliases.py](command_aliases.py). Aliases map words only to registered capability IDs and typed argument shapes. They cannot name a shell command or add an executable handler.

## Try collisions and rankings

```powershell
python .\omni_cli.py --plan "find test in tests"
python .\omni_cli.py --plan "find files named test in tests"
python .\omni_cli.py --plan "show tests"
python .\omni_cli.py --plan "show README.md"
python .\omni_cli.py --plan "show unknown"
```

`find test in tests` gives `find_files` and `search_text` 70 points each. Its status is `collision`, so it is never dispatched. `find files named test in tests` uses an explicit 100-point file-name alias and resolves to `find_files`. With the default workspace root, `show tests` ranks `list_files` first because `tests` is a directory, while `show README.md` ranks `read_file` first. Both still return a collision display. If `unknown` is absent, `show unknown` displays an equal-score collision.

The ranked candidate list is included in every intent, even when a winner exists. Each candidate has a capability, extracted arguments, integer score, alias rule ID, and evidence tags. A collision also produces `safe_display` with every option, its meaning, and an explicit command that chooses it. The intent records a canonical SHA-256 digest of the active rule set. Scores are deterministic ranking points, **not probabilities or confidence percentages**.

## Ranking rule

1. Match the entire input against the catalog's exact, path, term, generic-path, and word forms. A term form may take an explicit `in PATH` suffix; quote a term containing ` in `.
2. Keep the highest-scoring rule for each distinct `(capability, arguments)` meaning. Sort by descending score and then stable IDs.
3. Explicit aliases have higher catalog scores than broad aliases. The generic `show PATH` form adds 15 points for a file extension or trailing directory separator. If the path exists within the selected root, it adds 25 points for matching file/directory kind and subtracts 20 for a conflicting kind. File-kind checks are read-only and cached for that parse.
4. If two or more distinct meanings remain, return `collision` with no selected capability, regardless of score gap. Display every ranked meaning. No matching rule returns `unparsed`. Only a one-meaning `parsed` intent can reach the read-only dispatcher.

The lexical extension and separator cues are heuristics; a path-kind check is stronger evidence. An unknown path does not gain a kind score. An explicit but nonexistent path may still parse and then be rejected by the file adapter. Parser rankings can therefore change if the workspace changes; the source text, rules digest, and evidence make the decision inspectable. A high score never hides another distinct meaning or grants execution authority.

Run `python .\omni_cli.py --human "find test in tests"` to see the ranked choices as text. The interactive prompt uses the same readable display. JSON output retains the structured `safe_display` object. Single-command exit code 3 means a collision was displayed and no file operation ran.

## Catalog format and extension

Each rule has `id`, `phrase`, `mode`, `capability`, `score` (0–100), and `arguments` defaults. The modes are:

| Mode | Meaning | Example |
|---|---|---|
| `exact` | Entire phrase; fixed arguments | `ls` → `list_files` with `path: "."` |
| `path` | Phrase followed by one path | `cat README.md` → `read_file` |
| `term` | Phrase followed by text and optional `in PATH` | `grep alpha in notes` → `search_text` |
| `generic_path` | One path with competing meanings | `show docs` → list or read |
| `word` | Phrase followed by a word or quoted multiword expression | `define dog` → all definition candidates |

The catalog is data-only and bounded to 64 KiB / 200 rules. Loading rejects unknown versions, duplicate IDs or JSON keys, malformed fields, invalid argument shapes, and capabilities absent from the executor registry. Use `--aliases PATH` to try a custom catalog; the defaults remain in `command_aliases.json`. For example, adding an alias may change a collision's ranking, but it cannot register `run_shell` or bypass the read-only dispatcher.

WordNet is the second lexical layer after the explicit alias catalog. Its shared verb synsets can propose an explicit command when no alias matches, but these proposals cannot execute. See [NLP_LAYER_ORDER.md](NLP_LAYER_ORDER.md). To make a WordNet-derived phrase directly executable as an alias, it must be explicitly reviewed and entered in this catalog.

The catalog also contains explicit `word` operand rules for `define_word` and `word_relations`. These query the pinned local WordNet directly and return every candidate sense; they do not use the secondary synonym proposal path or choose a contextual meaning.

## Supplied Blue Key draft boundary

The supplied `rfc-blue-key-safe-operations-0001-draft.md` (SHA-256 `E8F3A1C8958DF382F0E87B1EB9E072DB80BD82E76152BD7748B911BCD0F9F0F7`) is a **draft source artifact**, not adopted canon or executable authority. Its sections 21, 26, and 27 distinguish execution, inspection, and bounded reading; its universal invariants prohibit hidden execution. The collision display follows that separation locally: it reports candidate meanings and performs no file adapter call. This implementation has not established the draft's identity, authority, redaction, consistency, or recovery requirements, so it makes **no Blue Key conformance claim**. The draft does not define a `SAFE-DISPLAY` operation; `safe_display` here is a local UI result name, not a registered Blue Key operation.
