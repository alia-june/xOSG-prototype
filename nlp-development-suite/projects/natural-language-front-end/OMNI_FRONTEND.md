# Natural English command front end: files, search, and WordNet

Status: first working slice, `omni-intent/0.4`. This is a generated interface proposal for the sister-machine prompt system. The sister-machine specification is still pending; this format has not been adopted by it. Version 0.2 added ranked alias candidates and collision display; version 0.3 added ordered lexical, history, web, and optional LLM proposal layers; version 0.4 adds deterministic WordNet definition and relation queries.

`omni_cli.py` accepts a complete direct English command, emits a typed intent, and dispatches only registered read-only capabilities. It does not call a shell, a subprocess, or aPROMPT. An unrecognized command receives `status: unparsed`; any distinct meaning collision receives `status: collision` and a safe display of every ranked option. Neither can run. The existing logic and aPROMPT handoff code remains separate.

## Run it

Python 3.10 or newer is sufficient for the file slice. WordNet queries require the pinned dependency and local data described in [WORDNET_DATA.md](WORDNET_DATA.md).

```powershell
python .\omni_cli.py --plan "search for alpha in tests"
python .\omni_cli.py "list files"
python .\omni_cli.py "find files named test in tests"
python .\omni_cli.py "show file README.md"
python .\omni_cli.py "search for ground-boolean in ."
python .\omni_cli.py --human "seek for ground-boolean in CONTROLLED_BOOLEAN_SLICE.md"
python .\omni_cli.py "define dog"
python .\omni_cli.py "show relations for dog"
python .\omni_cli.py --root C:\path\to\workspace
```

With no command, it opens a local interactive prompt. `exit` and `quit` leave the prompt. `--plan` emits the intent without dispatching it. The default root is the directory containing `omni_cli.py`; `--root` selects another existing root.

## Accepted language

| Capability | Representative English forms | Arguments |
|---|---|---|
| `help` | `help`; `what can you do`; `commands` | none |
| `workspace` | `where am I`; `current directory`; `pwd` | none |
| `list_files` | `list files`; `show files in PATH`; `ls PATH`; `dir PATH` | `path` |
| `read_file` | `show file PATH`; `read file PATH`; `cat PATH`; `type PATH` | `path` |
| `find_files` | `find files named NAME in PATH`; `locate files named NAME` | `name`, `path` |
| `search_text` | `search for TERM in PATH`; `find text TERM`; `grep TERM` | `term`, `path` |
| `define_word` | `define WORD`; `definition of WORD`; `definitions of WORD` | `word` |
| `word_relations` | `show relations for WORD`; `word relations for WORD`; `relations of WORD` | `word` |

`find_files` uses a case-insensitive substring of the file name. `search_text` uses a case-insensitive literal substring of UTF-8 text, not a regular expression. Quote a term containing ` in `, for example `search for "truth in logic" in notes`. Paths with spaces may be quoted. Each input must match a full command on one line; compound commands and unsupported synonyms abstain. Broad aliases such as `find X in PATH` show ranked meanings without selecting one. The full alias catalog, score rule, and collision behavior are in [COMMAND_ALIASES.md](COMMAND_ALIASES.md).

WordNet definition and relation queries return results for every candidate synset and set `sense_selected: false`. Relations distinguish semantic synset relations from lexical sense relations. Every relation type reports its target count; output lists at most 50 target records per relation type and marks longer lists as truncated. See [WORDNET_DATA.md](WORDNET_DATA.md) for the verified release inventory.

## Intent contract

The parser emits an object like:

```json
{
  "schema_version": "omni-intent/0.4",
  "source_text": "list files",
  "source_sha256": "<SHA-256 of exact UTF-8 source text>",
  "status": "parsed",
  "capability": "list_files",
  "arguments": {"path": "."},
  "reason": null,
  "alias_catalog_version": "omni-alias/0.1",
  "alias_rules_sha256": "<SHA-256 of canonical active rules>",
  "layer_trace": [{"layer": "aliases", "status": "parsed"}],
  "candidates": [{"capability": "list_files", "score": 100, "rule_id": "list_plain", "arguments": {"path": "."}, "evidence": ["exact_alias", "phrase:list files"]}],
  "side_effect_class": "read_only"
}
```

The command returns separate `intent` and `execution` objects. `status: parsed` means only that an explicit local grammar matched; it does not mean an axiom was accepted or an operation was approved. `execution.status` reports `completed`, `rejected`, or `not_executed`; the last status covers collisions and lower-layer proposals awaiting an explicit command. `help` reports the live capability manifest with descriptions, argument names, examples, and side-effect classes.

The [layer-order record](NLP_LAYER_ORDER.md) describes WordNet as the second lexical layer, in-memory session history as the third, web proposals as the fourth, and optional LLM proposals as the fifth. None of these proposal layers directly executes file operations.

In single-command mode, the process exits with code 0 for a parsed plan or completed read, 2 for unparsed or rejected input, and 3 when it displays a collision or lower-layer proposal without running a file operation. Use `--human` for a readable display. Interactive mode shows that readable display by default and remains open.

## Execution boundary

- Every path is resolved under the selected workspace root. Traversal and symlinks resolving outside it are rejected. Search does not follow directory symlinks.
- Directory listing is limited to 500 entries. File reads are limited to 128 KiB and require UTF-8 text without NUL bytes.
- Searches inspect at most 1,000 files and 200 directories. Text search reads at most 8 MiB overall and returns at most 50 matching lines. File-name search returns at most 50 paths. A `truncated` flag reports when a traversal or result limit ends the scan.
- Recursive search skips `.git`, `.venv`, `.wn_data`, and `__pycache__` by default. An explicitly named path can still be listed or read.
- The path check is intended for a local trusted workspace. Concurrent hostile filesystem mutation could race a path check; this slice is not an operating-system isolation boundary.

## Extending toward an omni front end

The capability registry is `CAPABILITIES` in `omni_cli.py`. A new command family needs an explicit complete-input grammar in `parse_command`, an argument contract and handler in the registry, and behavior checks. The registry currently dispatches only entries classified `read_only`; it does not offer generic shell execution. A future adapter can consume the intent JSON, map it to the sister machine's eventual contract, and require its validation and authorization before any consequential action. That mapping is pending the sister-machine specification.

The current slice answers file and search requests locally. It does not turn arbitrary English into CLI commands, infer a user's intended side effects, or translate these commands into aPROMPT axioms.

## Graphical file front end

[`file-interface-site`](file-interface-site/README.md) provides the browser UI
for the file slice. It loads the reviewed `omni-alias/0.1` catalog, exposes the
same workspace, list, read, filename-search, and literal-text-search families,
and preserves the CLI bounds. A command is parsed and displayed before a
separate user action invokes a registered read-only browser adapter.

The UI starts with a deterministic demonstration workspace and can request a
local folder through the browser's File System Access API. A fallback directory
input supports browsers without that API. The site has no server-side file
adapter, mutation capability, shell, subprocess, web proposal provider, or LLM
provider. Distinct alias meanings always remain visible as a collision, even
after session history changes their ranking.
