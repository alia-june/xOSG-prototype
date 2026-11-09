# File-function implementation TODO

Generated planning artifact, updated 2026-09-26. This plan derives from [the file-function matrix](FILE_FUNCTION_MATRIX.md), the verified `omni_cli.py` registry, and the proposal-only [Control Draft scaffold](CONTROL_DRAFT_SCAFFOLD.md). No file mutation operation was implemented. The sister machine has not adopted this roadmap.

## Source and status inventory

| Identifier | Location / type | Version and authority | Access / integrity | Relevance |
|---|---|---|---|---|
| `omni_cli.py` | Local Python source | Current generated front end, `omni-intent/0.4` | Readable; local tests run in this project | Actual capability and limit baseline |
| `OMNI_FRONTEND.md` | Local design document | Current generated interface proposal | Readable; descriptive, not receiver acceptance | Current grammar and boundary |
| `vendor/SISTERMACHINE_CONTRACT.md` | Supplied contract copy | Supplied aPROMPT 1.1.0 contract; authority limited to its specified receiving interface | Readable; hash recorded in `SISTER_CONTRACT_INTEGRATION.md` | Future mapping constraint, not shell authorization |
| Official shell manuals | External documentation linked in the matrix | Verified external descriptions as retrieved 2026-09-16 | Readable in bounded online research; versions vary by page | Evidence for operation families |

## Foundation: P0, read-only

- [x] **T00 — Ranked alias layer.** Add a validated data-only alias catalog, candidate evidence and scores, workspace path-kind evidence, and a `collision` status with a safe display of every option. See [COMMAND_ALIASES.md](COMMAND_ALIASES.md). Future command families need reviewed rules in the same catalog.
- [x] **T00a — Ordered proposal layers.** Connect local pinned WordNet as the second layer and in-memory confirmed session choices as the third. Add validated provider hooks for web before optional LLM, with all proposals displayed without dispatch. See [NLP_LAYER_ORDER.md](NLP_LAYER_ORDER.md). Live web and LLM providers are not yet configured in the CLI.
- [x] **T00b — Control Draft exchange scaffold.** Add proposal-only source, candidate, review, and in-memory projection seams from the supplied reintegration specification. The scaffold preserves source hashes, Unicode spans, layer traces, unresolved reasons, and explicit review status. It intentionally implements no semantic extraction rules or contract writes. See [CONTROL_DRAFT_SCAFFOLD.md](CONTROL_DRAFT_SCAFFOLD.md).
- [x] **T00c — Graphical WordNet explorer.** Add a static web front end over the complete pinned OEWN 2025 database. It exposes search, every candidate sense, definitions, examples, semantic and lexical relation filters, and bounded graph navigation through as many as five relation levels without selecting a contextual meaning. See [wordnet-explorer-site/README.md](wordnet-explorer-site/README.md).
- [x] **T00d — Graphical file interface.** Add a browser front end for the reviewed file aliases and live read-only capabilities. It keeps parsing, collision review, explicit choice, and bounded file access separate; supports a browser-selected local folder; and provides no mutation or generic shell adapter. See [file-interface-site/README.md](file-interface-site/README.md).
- [ ] **T01 — Formalize the intent schema** (F01–F10). Add a machine-readable schema and versioned capability manifest, with argument types, side-effect class, path scope, result type, and explicit failure codes. Keep `source_text` and digest. Validate malformed/forged intents before dispatch.
- [ ] **T02 — Session navigation and path semantics** (F02–F04). Add a REPL-scoped working directory, path inspection, and existence/type queries. Keep an explicit root boundary. Resolve Windows drive, UNC, separator, case, and symlink behavior in fixtures. A single-command call must have a defined starting directory.
- [ ] **T03 — Complete directory discovery** (F05–F09). Add recursive tree, exact name/glob modes, type/size/time/depth filters, deterministic sort, and pagination or continuation. Report skipped/inaccessible paths and truncation distinctly from no match.
- [ ] **T04 — Complete bounded content inspection** (F10–F14). Add selectable case sensitivity, UTF-8/UTF-16 detection or explicit encoding, line ranges/head/tail, counts, and optional search context. Preserve literal-search default; regex requires an explicit phrase and bounded matching.
- [ ] **T05 — Integrity and comparison** (F16–F18). Add SHA-256 hashing, byte equality, and text diff with size limits. Make hash output evidence of byte equality only where the algorithm and complete inputs are known; a digest is not a semantic validation result.
- [ ] **T06 — Read-only acceptance fixtures**. Cover spaces, quotes, Unicode, empty files, binary files, long paths, case differences, symlinks/junctions, inaccessible directories, large trees, changed files, and deliberate unsupported phrases. Verify no shell or subprocess invocation occurs.

## Common file changes: P1

- [ ] **T07 — Mutation contract** (F21–F26). Define typed `create_directory`, `create_file`, `write_file`, `copy_path`, `move_path`, `rename_path`, and `remove_path` intents. Separate parsing, validation, preview, authorization, execution, and receipt. The current read-only dispatcher must not execute these merely because a grammar matches.
- [ ] **T08 — Safe destination rules**. Specify overwrite and collision policy, parent creation, copy depth, treatment of links, cross-volume moves, and whether deletion is reversible. Include source/destination identity and changed-state checks. Refuse ambiguous targets and unbounded wildcard effects.
- [ ] **T09 — Implement common mutations after the contract is settled**. Begin with create, copy, and rename in disposable fixtures; then add write, move, and deletion. Stage where practical, verify the result, and retain a recovery record. Record partial failure explicitly.
- [ ] **T10 — Space and text editing** (F19–F20, F23). Add path-size and free-space queries. Define literal replace/append/clear operations with encoding, newline, expected prior digest, and output validation before enabling text writes.

## Advanced file operations: P2/P3

- [ ] **T11 — Metadata and links** (F27–F32). Add timestamp, attribute, link, permission, owner, and extended-metadata inspection first. Gate changes by platform/filesystem and exact actor authority; never flatten Windows ACLs into Unix mode bits or vice versa.
- [ ] **T12 — Archives** (F33–F36). Add member listing before extraction, size and expansion bounds, duplicate/case-collision detection, path traversal/link checks, CRC/integrity validation where available, staging, and post-extraction verification. Preserve original archive bytes and failures.
- [ ] **T13 — Tree synchronization** (F37). Plan source/destination comparison, preview additions/replacements/deletions, define conflict and exclusion rules, then require explicit authorization for the selected plan. Treat mirror deletion as a separate consequential action.
- [ ] **T14 — Platform-specific functions** (F15, F38–F40). Consider binary hex inspection, compression/encryption attributes, opening an associated application, and volume listing only after platform behavior and result contracts are specified. These are not prerequisites for the common file workflow.

## Sister-machine integration

- [~] **T15 — Contract mapping**. The local Control Draft scaffold now provides source, candidate, review, and transformation shapes, but no sister-machine contract mapping is accepted. When the specification arrives, map accepted intent types and outcomes to its schema. Distinguish a syntactic command parse from a logic statement, an adopted axiom, authorization, and an execution receipt. Reject loss of modal or permission meaning rather than inventing fields.
- [ ] **T16 — End-to-end validation**. For each capability, test English phrase → intent → argument validation → adapter → result/receipt, including failures and rollback. Add contract-version negotiation and keep older intents interpretable or explicitly migrate them.
- [ ] **T17 — Review the supplied Blue Key draft as a proposal.** Map its inspection, read, and execution concepts to the eventual sister-machine contract, identify the additional identity, authority, redaction, and consistency requirements, and test them before any conformance claim. The current collision display makes no such claim.
- [ ] **T18 — Implement reviewed Control Draft extraction rules.** Add one candidate family at a time for objective, resources, scope, authority, procedure, outputs, acceptance, and escalation. Each rule needs source spans, evidence, negative cases, exported evaluation coverage, and collision/conflict behavior.
- [ ] **T19 — Validate the exported reintegration package.** Run the 18 evaluation cases, Draft 2020-12 schema validation, authority invariants, privacy review, and failure-path checks. Update the source inventory to the current `omni-intent/0.4` and WordNet-enabled workspace before claiming coverage.

## Suggested implementation order

`T01 → T02–T06 → T07–T10 → T11–T14 → T15–T19`, with sister contract mapping brought forward as soon as its spec is available. The immediate next increment for the Control Draft branch is **T18**, beginning with one reviewed authority rule family and its evaluation cases. The current scaffold remains proposal-only and does not introduce file mutations.
