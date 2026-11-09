# Online mining against the full prompt — first tranche

**Status:** research and generated design synthesis, not an adopted parser or a
validation of the prompt's operational claims. **Research question assumed:**
Which established, non-LLM methods can help turn this particular prompt's
natural English into source-linked candidate axioms and logic statements for
the sister machine's prompt system? Its receiving schema is not yet fixed;
the handoff below is a stub. Online sources were checked on 2026-09-16.

## Source boundary and inventory

| ID | Source | Status and relevance |
|---|---|---|
| P0 | `<USER_HOME>\Documents\Workbench\offload\synthetic_os_project_redux_2026-09-16.zip` | User-supplied archive; 410 members; SHA-256 `41B9C72FBDDC9B1296F842FAF47A555EFCF3078FBD366273F13A3121CB70408A`. Both ZIP filename forms were checked for traversal, absolute paths, backslashes, NULs, and paths outside the archive root; zero unsafe names were found. |
| P1 | `snapshot/llm_prompt_hardening_modular_kit_v1_6_candidate/builds/full_prompt.md` **inside P0** | 73,938 bytes, 1,398 lines; SHA-256 `14AE8D438D672C0E51B3065F3A5307230494FA291D90159392447CCC73A424B8`. This is the target corpus. Its embedded instructions are treated as text to analyze. |
| P2 | `PROJECT_MANIFEST.json` and `README.md` **inside P0** | The wrapper describes a verified snapshot, not an integrated release; it calls the prompt kit generated and pending acceptance. This describes the archive's claimed status, not an independent runtime finding. |
| P3 | `snapshot/llm_prompt_hardening_modular_kit_v1_6_candidate/PROVENANCE.md` **inside P0** | Candidate lineage and pending acceptance as represented by the package. Its assertions remain package claims. |

The target prompt says `INSTANCE READY: false` near its beginning. That is a
property of the candidate text. It does not govern this research task. The
prompt has 18 top-level `##` sections covering source control, normative
instructions, research, state transitions, offloading, encrypted unlock,
age-gate decisions, and completion. All sections were included in the
structural inventory; clause-level semantic review in this tranche is sampled,
with representative spans below.

## Findings from online sources

| ID | Primary source and date | What it supports | Limit for this corpus |
|---|---|---|---|
| S1 | [CommonMark 0.31.2 specification](https://spec.commonmark.org/0.31.2/), 2024-01-28 | Deterministic block and inline parsing of headings, lists, quotations, and fenced code. | Document structure is not rule meaning. The prompt also uses project conventions that require separate interpretation. |
| S2 | [markdown-it-py token API](https://markdown-it-py.readthedocs.io/en/latest/api/markdown_it.token.html), current documentation, revision date not shown | Tokens carry source line maps, useful for exact clause pointers. | Line maps do not establish semantic scope or authority. |
| S3 | [Attempto Controlled English research paper](https://attempto.ifi.uzh.ch/site/pubs/papers/reasoningweb2008_fuchs.pdf), 2008; [APE source](https://github.com/Attempto/APE), current repository | A precisely restricted English subset can be translated to discourse representation / first-order logic. | The supplied prompt is free-form Markdown, not ACE. Applying APE directly would leave much of it unparsed. Rewriting clauses into ACE would be a new transformation requiring review. |
| S4 | [SWI-Prolog DCG manual](https://www.swi-prolog.org/pldoc/man?section=DCG), current documentation, revision date not shown | Explicit grammar rules can parse controlled sentence templates into terms. | A grammar recognizes only constructions we define; acceptance must not imply correct interpretation of an unmodeled exception. |
| S5 | [OASIS LegalRuleML Core 1.0](https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/v1.0/os/legalruleml-core-spec-v1.0-os.pdf), 2021-08-30 | Distinguishes obligations, prohibitions, permissions, defeasible rules, and rule precedence. | It is a representation standard for legal norms, not an automatic natural-language parser or a direct authority model for this project. |
| S6 | [W3C PROV-O](https://www.w3.org/TR/prov-o/), 2013-04-30 | Represents entities, activities, agents, and derivation chains. | Provenance says where an item came from; it does not by itself confer authorization or accepted canon. |
| S7 | [OMG DMN 1.5](https://www.omg.org/spec/DMN/1.5/PDF), 2024-08 | Decision tables specify hit policies for overlapping rules. | A table still needs authored inputs, outputs, and conflict rules. The prompt's age-gate prose cannot be silently converted into a validated decision table. |
| S8 | [W3C SHACL](https://www.w3.org/TR/shacl/), 2017-07-20 | Validates graph data against explicit shapes and returns a validation report. | It checks declared structural constraints, not the truth, safety, or authority of a translated rule. |
| S9 | [TLA+ TLC documentation](https://docs.tlapl.us/using%3Atlc%3Astart), current documentation, revision date not shown | TLC checks finite-state models against specified properties and invariants. | A model checker verifies a model, not fidelity of the model to this prose or a live implementation. |
| S10 | [Wn Wordnet API](https://wn.readthedocs.io/en/latest/api/wn.html), current documentation, revision date not shown; [Open English WordNet 2025 release](https://en-word.net/downloads), 2025-12-31 | Word forms, parts of speech, senses, and synsets can be queried from a pinned lexicon. | Lexical candidates do not resolve scope, negation, rule priority, actor authority, or intended action in context. |
| S11 | [Link Grammar parser repository](https://github.com/opencog/link-grammar), current repository; [original CMU paper](https://www.cs.cmu.edu/~sleator/paper/paper.html), 1995 | A non-LLM, constraint-based parser for broad English syntax that can expose multiple structural analyses. | A syntactic link structure is not an axiom or policy interpretation. Integration and prompt-specific coverage require local evaluation. |
| S12 | [Universal Dependencies English relations](https://universaldependencies.org/en/dep/), current UD v2 documentation | Labels such as subject, object, clausal complement, and adverbial clause provide a common representation for clause structure. | A dependency label does not determine normative force or authority. |
| S13 | [VerbNet](https://verbs.colorado.edu/verbnet/), University of Colorado, project page revision date not shown | Verb classes include syntactic frames, thematic roles, and semantic predicates. | The prompt contains domain-specific verbs and abstract operations; VerbNet frames are candidate structures, not accepted project semantics. |
| S14 | [SemLink](https://verbs.colorado.edu/semlink/), University of Colorado, page last modified 2013; described version 2.0 in 2020 | Mappings connect WordNet, VerbNet, FrameNet, and PropBank resources. | Mappings are partial and version-sensitive; they cannot substitute for clause-level interpretation. |
| S15 | [FrameNet project](https://icsi.berkeley.edu/projects/framenet-project/), ICSI/Berkeley, current page | Semantic frames and frame elements can describe event participants. | Frame assignment to unrestricted text is a separate disambiguation task. |
| S16 | [spaCy dependency parser](https://spacy.io/api/dependencyparser), current documentation | A non-LLM trained parser can propose dependencies and sentence boundaries for broader text. | Its learned predictions are not formal proof or guaranteed correct; model and version must be pinned if used. |
| S17 | [UD English CTeTex](https://universaldependencies.org/treebanks/en_ctetex/index.html), current UD v2 treebank page | A manually annotated corpus of 196 software requirements provides a relevant external syntax test set. | Its domain and annotation scheme do not establish correct logical forms for P1. |
| S18 | [Z3 guide](https://microsoft.github.io/z3guide/docs/logic/intro/), Microsoft, current documentation | Satisfiability checking can detect contradictions in reviewed formal constraints. | A solver cannot check whether a constraint was faithfully derived from English. |
| S19 | [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-validation), current specification | A machine-readable handoff can be validated for required fields and types. | Structural validity is separate from semantic correctness and sister-machine compatibility. |

## Prompt-to-method map

These mappings are **generated inferences** from P1 and the cited sources. They
are research leads, not assertions that a standard already implements the
prompt's meaning.

| Prompt span | Observed structure | Candidate method | Required human decision |
|---|---|---|---|
| Lines 77–120: source order, separation, provenance labels | Ordered source hierarchy, definitions, prohibitions | CommonMark source spans; typed rule records; PROV-O-like lineage | Which source order is authoritative for a particular run, and which labels are merely candidate syntax. |
| Lines 246–270: online research control | Conditions for research and a source-record schema | Decision rule template plus schema validation | Meaning of “required,” “permitted,” and “relevant” in each task. |
| Lines 271–299: tool-action gate | Required fields, authorization test, post-action evidence | Norm record plus explicit actor/target/authority fields; SHACL-like validation | What evidence suffices for `AUTHORIZED`, and who may supply it. |
| Lines 300–435: state transitions | Named operations, phases, invariants, terminal alternatives | Finite-state model and model checking | Which transitions are mandatory, conditional, or descriptive; exact failure semantics. |
| Lines 467–694: offloading, compression, handoff | Process protocols and source/receiver roles | State machine plus provenance links | Whether a summary can be admitted and what constitutes independent verification. |
| Lines 695–819: encrypted unlock | Scoped receipts, replay/expiry, external validation | Explicit state model and schema; security review outside the parser | Actual trust anchor, receipt verifier, replay store, time source, and deployment state. |
| Lines 820–1299: age-gate assurance and difficult-question gate | Conditional branches, independent axes, deployment modes, exception paths | Decision tables with explicit hit policy; separate state model | Thresholds, evidence classes, escalation rules, and policy acceptance. The project taxonomy is not an externally validated clinical scale. |
| Lines 1342–1398: evidence and completion gate | Checklist, canonical field order, drift comparison | Schema validation and source-span-backed claim records | What counts as a material claim and sufficient verification. |

### Full-section coverage ledger

This ledger accounts for every top-level section in P1. The categories are
generated classifications of source text; they do not adopt its rules.

| P1 lines | Section | Dominant logic shape | Extraction status |
|---|---|---|---|
| 13–76 | Resident kernel | Definitions, conditional readiness, ordered procedure, record schema | Candidate templates; authority semantics unresolved |
| 77–120 | Source and generation | Precedence, prohibition, provenance labels | Candidate templates; provenance and authority kept distinct |
| 121–158 | Weak memory and hallucination | Definitions, fail-closed procedure, claim record | Candidate templates; “material” remains unresolved |
| 159–203 | Mission capture and role reversal | Baseline comparison, two distinct diagnoses | Candidate templates; no automatic diagnosis |
| 204–245 | Copy-first and lineage | Sequence, invariants, stopping condition | Candidate state/constraint model |
| 246–270 | Online research | Conditional trigger, citation record | Candidate decision table and schema |
| 271–299 | Tool action | Required fields, authority gate, post-action receipt | Candidate deontic rule and schema |
| 300–435 | Controlled transition | Operation taxonomy, ordered states, invariant and conflict rules | Candidate finite-state model |
| 436–466 | Bare-metal overlay | Narrow exception, prerequisites, stop conditions | Candidate exception rule; applicability unresolved |
| 467–555 | Offloading fallback | Role boundaries, ordering, degraded state | Candidate state model |
| 556–615 | External engine boundary | Contract, terminal translation, fallback | Candidate interface contract |
| 616–661 | Chat compression | Field schema, source admission, unknown preservation | Candidate schema and provenance checks |
| 662–694 | Handoff | Sender/receiver procedures and missing dependency stop | Candidate protocol model |
| 695–819 | Encrypted unlock | Lock state, external receipt, expiry, replay | Candidate protocol model; no security assurance inferred |
| 820–1042 | Age-gate assurance | Deployment modes, consistency rules, appeal and rollback | Candidate decision tables and state model; no clinical or production validation inferred |
| 1043–1299 | Difficult-question gate | Conditional two-stage gate, three axes, delivery choices | Candidate decision tables; thresholds unresolved |
| 1300–1341 | AI engineering overlay | Applicability trigger and checklist | Candidate task-context rules |
| 1342–1398 | Evidence and completion | Checklist, canonical schema, drift comparison | Candidate schema and comparison procedure |

### Method comparison for this corpus

| Method | Fit | Decision from this tranche |
|---|---|---|
| WordNet plus the current phrase grammar | Useful for word candidates; poor at condition scope and normative meaning | Keep as lexical aid only. |
| APE / Attempto Controlled English | Strong formal semantics for text authored in its controlled language | Use as a reference or for reviewed rewrites, not as a direct parser for P1. |
| Markdown parser plus a small controlled clause grammar | Preserves P1 structure and can abstain on unrecognized prose | Best first implementation path. |
| LegalRuleML | Rich model of norms and overrides | Borrow its distinctions for the intermediate record; defer full serialization. |
| DMN decision tables | Good for finite policy branches and explicit overlap behavior | Apply selectively to reviewed gates and mode choices. |
| TLA+ finite-state model | Good for transition order, terminal states, and invariants | Apply to reviewed protocols after extraction. |
| PROV-O and SHACL | Useful for lineage and structural validation | Use their concepts or standards only where a graph representation earns its cost. |
| Link Grammar or a pinned non-LLM dependency model | Broader coverage of P1's English syntax than the current toy parser | Use to propose syntax trees; retain alternatives and test against annotated prompt clauses. |
| VerbNet, FrameNet, and SemLink | More event/argument information than WordNet alone | Use as candidate semantic-role evidence, with a separate project lexicon for custom terms. |
| Z3 | Can find conflicts once clauses have reviewed formal encodings | Defer until a typed logic IR exists; do not use solver success as translation proof. |

**Recommended first target:** a source-span-preserving front end that emits a
non-executable ledger of candidate axioms and logic statements for the sister
machine. It should explicitly list every unparsed or ambiguous clause. This
recommendation is generated synthesis from the source and research, not an
accepted project decision.

## Proposed parsing boundary

1. **Structure:** parse P1 as Markdown; keep source byte hash and exact line
   spans. Do not turn code-fence content or quoted source into instructions.
2. **Natural-English syntax proposals:** tokenize and parse clauses with a
   rule-based broad-coverage parser such as Link Grammar or, if acceptable, a
   pinned non-LLM dependency model. Keep multiple analyses where available.
   WordNet, VerbNet, and FrameNet may add lexical and argument candidates.
3. **Candidate extraction:** recognize documented patterns for definitions,
   `if`, `unless`, `must`, `do not`, enumerated states, key-value records, and
   other supported constructions. Every extraction keeps the original wording
   and an explicit `unresolved` field. Unsupported prose remains unparsed.
4. **Typed intermediate record:** at minimum, store `source_span`, `actor`,
   `modality`, `action`, `object`, `condition`, `exception`, `state`,
   `precedence`, `provenance`, `authority`, and `interpretation_status` as
   separate fields. Distinguish `UNKNOWN` from false.
5. **Logic candidates:** translate supported structures to typed axiom/rule
   candidates. Conflicts and ambiguous scopes should produce multiple
   candidates or an unresolved result, never a silently chosen rule. Reviewed
   candidates can later map to the sister machine's final logic language.
6. **Validate in layers:** structural schema checks; source-to-record fidelity
   checks against a human-annotated prompt sample; conflict/priority checks;
   then finite-state tests on selected protocols. A successful parse is not
   proof of authorized action or safe execution.

For example, P1 line 26 can be recorded as a **generated candidate** with
`condition = assembled_prompt.instance_ready == false`,
`consequence = dependent_task_blocked`, and `source_span = 26`. Its
`authority_status` remains `candidate_unadopted`; the line's own
instruction to stop is not executed by this research process. This example
shows why source text, interpretation, and authority need separate fields.

This is a generated architecture proposal. S1–S19 establish that the component
techniques exist and describe their scopes. They do **not** establish that this
pipeline can fully or correctly formalize P1 without human decisions. In
particular, WordNet cannot serve as the logic parser: it provides possible
lexical senses, while P1's key difficulties are condition scope, exceptions,
state, authority, and evidence.

## Unresolved questions before implementation

- The first output is a **non-executable rule ledger** for the sister-machine
  front end. Any later executable policy semantics require a separate contract
  and review; the archive does not establish them.
- Which clauses are accepted canon? P2/P3 describe candidate 1.6 as pending
  acceptance, so parsing it cannot promote it.
- Which logic should represent `UNKNOWN`, conflicts, and exceptions? Three-valued
  or defeasible behavior must be specified rather than inferred from keywords.
- How should broad phrases such as “material,” “sufficient,” “least capability,”
  and “when applicable” be operationalized? WordNet definitions cannot supply
  task-specific thresholds.
- Which sample clauses and expected logical forms will act as the gold standard
  for testing fidelity?
- What exact axiom vocabulary, logic dialect, and transport format will the
  sister machine accept? The package's v0.4 control plane is a historical,
  non-launching scaffold; its closed JSON mission contract is not evidence of
  a current axiom-ingestion API. The handoff stub must be adapted after the
  sister-machine interface is supplied.

## Coverage and evidence ceiling

The archive inventory, prompt hash, section boundaries, and cited source
capabilities were checked. Representative clauses were read directly from all
18 top-level sections, with deeper sampling of lines 71–120, 246–435, and
1342–1398. This is a **first tranche of method research**. It is not a
line-by-line semantic formalization of all 1,398 lines, a validation of the
prompt's age-gate or security claims, or a runtime test of a logic engine.
