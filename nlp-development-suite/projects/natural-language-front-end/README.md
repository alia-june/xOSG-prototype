# Grammar parsing without an LLM

## Natural English command front end

The first command-line-like slice is [`omni_cli.py`](omni_cli.py). It parses
explicit English commands for listing, reading, finding, and searching files
within a selected workspace root, then dispatches bounded read-only adapters.
Run `python .\omni_cli.py "help"` to see registered capabilities, or use
`--plan` to inspect an intent without executing it. The accepted phrases,
limits, intent format, and sister-machine boundary are in
[`OMNI_FRONTEND.md`](OMNI_FRONTEND.md).
The [ranked alias catalog](COMMAND_ALIASES.md) accepts more English and shell
vocabulary. Every distinct meaning collision displays all ranked alternatives
and leaves the file operation unexecuted.
The [NLP layer order](NLP_LAYER_ORDER.md) places pinned WordNet second, local
session history third, web proposals fourth, and optional LLM proposals last.
The [WordNet data and query guide](WORDNET_DATA.md) documents the verified
complete OEWN 2025 download plus definition and word-relation commands.
The [Lexicon Atlas](wordnet-explorer-site/README.md) provides a graphical web
view of the same complete local release, with search, every candidate sense,
definitions, examples, relation filters, and a clickable relation graph.
The [Control Draft scaffold](CONTROL_DRAFT_SCAFFOLD.md) defines a separate,
proposal-only exchange shape for questionnaire interpretations.
The [researched file-function matrix](FILE_FUNCTION_MATRIX.md) compares
PowerShell, GNU/Linux utilities, and Windows Command Prompt; its
[implementation TODO](FILE_FUNCTION_TODO.md) tracks the next capabilities.
The [File Atlas](file-interface-site/README.md) web front end applies the same
reviewed alias catalog to a browser-selected read-only workspace. Parsing,
collision review, and bounded file access remain separate steps.

This is a small, deterministic English parser. It uses a written vocabulary and
phrase rules, so its output is reproducible and every accepted structure can be
traced to a rule. It does not learn from text or guess the role of an unknown word.

## Try it

The small built-in vocabulary needs Python 3.10 or newer and no third-party
packages.

```powershell
python .\grammar_parser.py "the red dog runs"
python .\grammar_parser.py "I saw the man with the telescope"
python .\grammar_parser.py --json "Alice sees a cat."
```

The second sentence has two parses. In one, *with the telescope* describes the
man. In the other, it attaches to the action of seeing. The program reports
both trees; it does not choose a meaning without evidence.

## Current grammar

```text
S  -> NP VP
NP -> PRON | PROPN | DET? ADJ* N | NP PP
VP -> IV | TV NP | VP PP
PP -> P NP
```

The built-in vocabulary is the `LEXICON` table near the top of
[`grammar_parser.py`](grammar_parser.py). `IV` means intransitive verb and `TV`
means transitive verb. The JSON output includes character offsets into the
original input.

## Add WordNet

The optional WordNet mode uses **Open English WordNet 2025** through the `wn`
Python library. Both versions are pinned. Install once in this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m wn --dir .wn_data download oewn:2025
```

Then run:

```powershell
.\.venv\Scripts\python.exe .\grammar_parser.py --wordnet "the curious otter runs"
.\.venv\Scripts\python.exe .\grammar_parser.py --wordnet --senses --json "the otter runs"
.\.venv\Scripts\python.exe .\omni_cli.py "define otter"
.\.venv\Scripts\python.exe .\omni_cli.py "show relations for otter"
.\.venv\Scripts\python.exe .\verify_wordnet.py
```

For the graphical explorer, serve `wordnet-explorer-site/dist` with a static
web server. Rebuild its deterministic data shards with
`wordnet-explorer-site/build_data.py` after changing the pinned WordNet data.

WordNet supplies candidate nouns and adjectives, including inflected forms
through `wn`'s Morphy rules. The output records WordNet part-of-speech
candidates and, with `--senses`, possible synsets. **These are candidates, not
context-resolved meanings.** Built-in entries take precedence; WordNet expands
words that lack a built-in entry. Verb argument rules (`IV` and `TV`), pronouns,
determiners, prepositions, and proper names remain in the built-in table.
WordNet mode reads the local `.wn_data` directory and makes no network request
while parsing. A different data location can be passed with `--wordnet-dir`.
The command front end can also return all definitions and all semantic and
lexical relation types for every candidate sense. It never selects a sense.

The data comes from the [Open English WordNet 2025 release](https://en-word.net/downloads)
(CC BY 4.0); the integration uses the [Wn API](https://wn.readthedocs.io/en/latest/api/wn.html).
The locally downloaded source archive has SHA-256
`9CA6D1DCB75F822FDD66617F7D9DA48142ACE38DD544D6AD5E2FECA1674AD3FE`.

This is a **controlled subset** of English. It currently handles one simple
sentence, optional final punctuation, basic noun phrases, verb phrases, and
prepositional phrases. It does not check subject–verb agreement, resolve pronoun
references, or assign meaning. WordNet mode broadens lexical candidates but
does not resolve which candidate fits the sentence.
An accepted parse therefore means only that the sentence fits these rules.

Run the focused checks with:

```powershell
python -m unittest discover -s tests -v
```

## Logic front end while the sister-machine spec is pending

[`logic_frontend.py`](logic_frontend.py) adds a narrow, deterministic extraction
pass over the supplied full prompt. It recognizes simple prohibitions, selected
imperatives, `must` clauses, and one controlled `if ... is ..., do not ...`
form. It emits partial, unreviewed typed-logic candidates with line pointers;
other text is explicitly `unparsed`. Fenced code and Markdown headings are
retained as source text but are not parsed as instructions. WordNet, when
enabled, contributes possible parts of speech for an action word, not its
contextual meaning.

The output uses the provisional [`handoff_stub.schema.json`](handoff_stub.schema.json).
The sister machine's contract is still being designed, so `execution_allowed`
is always false and every item is unadopted. Run the prompt corpus with:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-handoff.txt
.\.venv\Scripts\python.exe .\logic_frontend.py --archive "<USER_HOME>\Documents\Workbench\offload\synthetic_os_project_redux_2026-09-16.zip" --wordnet --output .\FRONTEND_FULL_PROMPT_CANDIDATES.json
.\.venv\Scripts\python.exe .\validate_handoff_stub.py --archive "<USER_HOME>\Documents\Workbench\offload\synthetic_os_project_redux_2026-09-16.zip" --example .\FRONTEND_FULL_PROMPT_CANDIDATES.json
```

The extractor reads a bounded ZIP snapshot without unpacking it, checks both
stored filename forms, and rejects unsafe, duplicate, or case-colliding names.
It bounds archive and member sizes and selected-member expansion. It validates a
staged output before publication and writes a digest receipt. A different
existing output is retained as a prior generation only when `--replace` is
passed. The receipt describes local generation and validation; it is not a
sister-machine acceptance receipt. See [the compliance review](COMPLIANCE_REVIEW_YES_2026-09-16.md)
for the boundary against the supplied state-transition document.

The current corpus run emits 28 partial candidates and 1,168 unparsed
nonblank line or sentence fragments. This low coverage is intentional: a
matching pattern is only a syntactic proposal, and it cannot promote text from
the attached document into adopted rules. The [online mining report](ONLINE_MINING_FULL_PROMPT_2026-09-16.md)
lists the larger parsing and validation work still needed.

## aPROMPT sister-machine boundary

The supplied aPROMPT 1.1.0 contract is integrated through
[`sister_adapter.py`](sister_adapter.py). The adapter validates the legacy
ledger against the original ZIP, checks the pinned local wheel and contract,
then creates a new directory of aPROMPT 1.0 meaning documents. The current
75-document result covers all 1,196 fragments. Every statement remains
unresolved because the existing modal/imperative candidates cannot be
represented faithfully by the receiving `ground-boolean/1.0` compiler.
No adoption, approval, or execution is performed. See the
[integration record](SISTER_CONTRACT_INTEGRATION.md) and
[generated handoff manifest](sister_handoff_2026-09-16_v1/manifest.json).
The [unresolved review package](sister_handoff_2026-09-16_v1_unresolved.zip)
contains the manifest and all 75 meaning documents.

For text deliberately written in a small Boolean English subset,
[`controlled_boolean.py`](controlled_boolean.py) can emit actual aPROMPT
expressions. The [controlled example](examples/controlled_boolean.meaning.json)
has five assertions and no adopted axioms. The [grammar and limits](CONTROLLED_BOOLEAN_SLICE.md)
explain why this path does not yet translate any clause from the full prompt.
