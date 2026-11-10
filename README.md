```text
IF reader = heuristic engine THEN read ai.landing.pad.json.
ELSE IF reader = AI THEN read ai.landing.pad.low-mem.json.
ELSE continue with the human README.
IF a required reference fails to resolve THEN stop the dependent step AND report the unresolved reference.
```

[Heuristic engine landing pad](ai.landing.pad.json) · [AI landing germ](ai.landing.pad.low-mem.json)

# xOSG-prototype

Public research prototypes for inspectable AI-assisted work, reference-native documents, and deterministic computation. Each project identifies its own authority, evidence, validation, and release boundaries.

**Working on tool instrumentation?** Start with [How to Instrument a Tool](Instrumentation/README.md) and the [living tooling workspace guide](Instrumentation/WORKSPACE_HOW_TO.md). The [existing-controller how-to](Instrumentation/HOW_TO_USE.md) applies after a controller has been fitted to a declared tool and approved.

## Current publication and recovery phase

**Stage 0 — site hydration (in progress):** publish eligible research theory, proof-of-concept records, links, statuses, and evidence boundaries arising from EOL simulation research. **Stage 1 — stable programmatic code rehydration (planned):** expert-system- and rule-led reconstruction from admissible evidence; synthetic generative text only as a separately qualified last resort. Existing bounded prototypes such as Code-Lexigraph are **not** general Stage 1 admission. Private data is excluded from the public corpus. [Read the public roadmap](https://github.com/alia-june/ethical-and-intellectual-theory/blob/main/research-ethics/EOL_SITE_HYDRATION_AND_REHYDRATION_ROADMAP.md).

## Project directory

| Project | What you will find | Architecture or design | Run or read first |
| --- | --- | --- | --- |
| [xOSG instrumentation family](docs/xosg/README.md) | DWSK R4 source, Naked Shell identity, Synthetic Simulations documentation, and related deterministic tool instrumentation | [Family and member boundaries](docs/xosg/README.md) | [Choose a member](docs/xosg/README.md) or [set up a tooling workspace](Instrumentation/WORKSPACE_HOW_TO.md) |
| [xOSG-0](syn-xOSG-0/README.md) | Developmental orchestration research from ES-xOSG-7 through Seed | [Developmental architecture](syn-xOSG-0/ARCHITECTURE.md) | [Read the source ledger](syn-xOSG-0/docs/SOURCE_LEDGER.md) |
| [Mill Factory](mill-factory/README.md) | PowerShell work batches with evidence, gates, and fail-closed promotion | [Batch architecture](mill-factory/ARCHITECTURE.md) | [Create a disposable batch](mill-factory/HOW_TO.md) |
| [Code-Lexigraph](code-lexigraph/README.md) | Bounded Python code reconstruction with bidirectional traces and a restricted construction grammar | [Design and grammar](code-lexigraph/docs/DESIGN.md) | [Inspect a reconstruction](code-lexigraph/HOW_TO.md) |
| [NLP Development Suite](nlp-development-suite/README.md) | Code-only lexical, grammar, Atlas, and non-executing interpretation prototypes with separately managed data | [Suite boundaries and components](nlp-development-suite/README.md) | [Run the data-free checks](nlp-development-suite/README.md#quick-start-data-free-validation) |
| [Etabit Schema](etabit-schema/README.md) | Draft multi-drive construction schema, source and reference examples, and unresolved contracts | [Drive and authority architecture](etabit-schema/ARCHITECTURE.md) | [Review and validate a descriptor](etabit-schema/HOW_TO.md) |
| [Syn-Etabit Transformer — Textual](syn-etabit-transformer-textual/README.md) | Reference-native document construction research and a retained CPU compatibility service | [Construction and service architecture](syn-etabit-transformer-textual/ARCHITECTURE.md) | [Read the service setup and environment limits](syn-etabit-transformer-textual/service/README.md) |
| [sf-AmorphDataDrive](sf-amorph-data-drive/README.md) | Locked v0.3 raw substrate baseline and locked v0.1 member identity contract | [Locked v0.3 specification](sf-amorph-data-drive/specifications/sf_edabit_amorph_data_drive_locked_spec_v0_3.md) and [locked sf-UUID contract](sf-amorph-data-drive/contracts/SF_UUID_IDENTITY_CONTRACT_v0.1_LOCKED.md) | [Review a specification change](sf-amorph-data-drive/HOW_TO.md) |
| [MATH.SC-0](xosg-0-math-sc0/README.md) | Deterministic numerical work across Python, JavaScript, and native C/C++ with verification | [Three-runtime architecture](xosg-0-math-sc0/docs/three_runtime_architecture.md) | [Build and check the runtimes](xosg-0-math-sc0/HOW_TO.md) |
| [GFX Form Engine / Encoded Lexical Raster](gfx-form-engine/README.md) | JSON-0 CPU scaffold and research on frames, aligned reads, and lexical raster execution | [Frame and execution architecture](gfx-form-engine/ARCHITECTURE.md) | [Build and test the CPU scaffold](gfx-form-engine/HOW_TO.md) |
| [Semantic Symbol Interpreter](semantic-symbol-interpreter/README.md) | Synthetic text interpretation and an adversarial harness for context, evidence, and uncertainty | [Interpretation architecture](semantic-symbol-interpreter/ARCHITECTURE.md) | [Inspect a fixture grade](semantic-symbol-interpreter/HOW_TO.md) |
| [Holoquary v1.3](holoquary/README.md) | Reconstituted C99 prototype for deterministic logic, explicit uncertainty, and small transactional state | [Computational model](holoquary/README.md#what-holoquary-is) | [Read the reconstitution record](holoquary/RECONSTITUTION.md) |
| [Governed Microserver Transmigration](governed-microserver-transmigration/README.md) | Candidate-only validation of JSON microserver manifests and declared glue | [Microserver and glue architecture](governed-microserver-transmigration/docs/ARCHITECTURE.md) | [Review the verification scope](governed-microserver-transmigration/docs/VERIFICATION.md) |

**xOSG family entry points:** [Amorphous Durable AI Workspace / DWSK](amorphous-durable-ai-workspace/README.md) (source-qualified storage and recovery; [architecture](amorphous-durable-ai-workspace/ARCHITECTURE.md)), [Naked Shell](Naked%20Shell/README.md) (identity only), [Synthetic Simulations](Synthetic%20Simulations/README.md) (public research account and retained failed experiment; [reading guide](Synthetic%20Simulations/HOW_TO.md)), and [Instrumentation](Instrumentation/README.md) (related tooling and worked controller examples; [architecture](Instrumentation/ARCHITECTURE.md)).

These are separate research systems, not one finished product. Each keeps its own contracts, evidence, compatibility boundaries, validation status, integration gates, and release decisions.

> **Make the boundary visible. Keep evidence attached. Do not turn uncertainty into authority.**

---

## Historical seed research links

- **[Omnifact Reference v0.8.0](Synthetic%20Simulations/defunct-experiments/retired/omnifact-ref-v0-8-0/README.md)** — sanitized source **staging record and checksum**, retired historical reference; not admitted; no test failure is asserted. [Sanitization summary](Synthetic%20Simulations/defunct-experiments/retired/omnifact-ref-v0-8-0/SANITIZATION_REPORT.md).
- **[MAGE Core 0.1.7-prealpha](Synthetic%20Simulations/defunct-experiments/retired/mage-core-v0-1-7-prealpha/README.md)** — retired, de-identified historical record. [Scoped design](Synthetic%20Simulations/defunct-experiments/retired/mage-core-v0-1-7-prealpha/DESIGN_RECORD.md).
- **[LLM Prompt Hardening Modular Kit Candidate 1.5](Synthetic%20Simulations/defunct-experiments/failure/llm-prompt-hardening-modular-kit-v1-5-candidate/README.md)** — prior sanitized failed experiment.

**Link status:** these new OmniFact and MageCore pages host documentation and verified artifact identifiers; their sanitized ZIP binaries have not been uploaded to GitHub. The original archives and private exclusion ledgers are not public.

## System landscape

```text
                         HUMAN / OPERATOR
                               │
                      explicit decision authority
                               │
          ┌────────────┬──────────────┴──────────────┐
          │            │                             │
       xOSG-0      Mill Factory                bounded services
 orchestration     evidence batches           /       |        \
   / control       gates + decisions          /        |         \
          │            │              Code-Lexigraph Syn-Etabit MATH.SC-0
          │            │              code semantics  documents   computation
          │            │                    │             │          │
          │            │              reconstruction transformations verification
          │            │              traces + maps    receipts    + evidence
          │            │                    │             │          │
          └──────── provenance / gates / explicit failure ────────────┘
```

This is a conceptual map, not a dependency graph.

---

# Project constellation

## xOSG instrumentation — durable state and inspectable experiments

**[Open family →](docs/xosg/README.md)** · **[Tool instrumentation →](Instrumentation/README.md)** · **[DWSK kit →](amorphous-durable-ai-workspace/README.md)** · **[Migration and evidence →](docs/xosg/MIGRATION.md)**

> **Instrumentation starts with how to instrument a tool:** begin with
> [Instrumentation/README.md](Instrumentation/README.md). It is the required
> tool-by-tool method for inspecting a real interface and designing only the
> instrumentation it needs. Read the downstream how-to only after a specific,
> approved controller exists for the tool in question.

xOSG, **expert Overlay System Gestalt**, brings together durable project storage, a staged shell identity, and bounded AI control-plane research. DWSK supplies local transactional records, a hash-chained journal, verified checkpoints, and quorum recovery. Naked Shell remains identity-only. Synthetic Simulations documents a private control-plane prototype and preserves a sanitized failed experiment as failed.

The separate [Instrumentation](Instrumentation/README.md) package documents a
tool-by-tool method for moving justified mechanical work out of an LLM prompt.
Its three Mill controllers—creation, verification, and gate recording—are
worked examples, not the starting assumption or a generic wrapper. Each binds
a bounded request to an authority assertion and observed source identity,
retains receipts, and keeps uncertain outcomes visible. The package is
experimental local tooling—not a universal orchestrator, a generic tool
protocol, a promotion authority, or proof that all AI/system cost has been
removed.

The OpenSurface migration retains the merged DWSK R4 repairs. Its fresh migration checks cover the fixed Windows unit/self-check suites; they do not reproduce the full fault campaign, publish the private simulation runtime, integrate a conversation logger, or grant agent authority. This family remains distinct from the developmental xOSG-0 research line below.

## xOSG-0 — developmental orchestration spine

**[Open project →](syn-xOSG-0/README.md)** · **[Growth spine →](syn-xOSG-0/growth/README.md)** · **[Source ledger →](syn-xOSG-0/docs/SOURCE_LEDGER.md)**

xOSG-0 is the repository's governance and orchestration research line. It records how a broad experimental system is reduced, actualized, pressured, hardened, and finally distilled toward a smaller Seed.

```text
ES-xOSG-7
    ↓
xOSG-0 bare-metal 0
    ↓
xOSG-0 v0.2 — actualized runtime
    ↓
xOSG-0 v0.3 — deterministic testing + hardening
    ↓
xOSG-0 v0.4 — loose/fuzzy hardening
    ↓
Seed
```

Research themes include layered human/operator authority, explicit workflow state, deterministic offload, provenance-aware transitions, fail-closed behavior, fuzzy/adversarial pressure, and extracting a minimum justified kernel only after developmental evidence exists.

The documented v0.4 fuzzy stage records **107 / 107 bounded cases passing with no crashes or timeouts**. The source ledger also preserves historical uncertainty: reconstructed evidence is not silently relabeled as recovered original source.

---

## Mill Factory — evidence-bearing work batches

**[Open project →](mill-factory/README.md)** · **[Validation →](mill-factory/VALIDATION.md)** · **[Provenance →](mill-factory/PROVENANCE.md)**

Mill Factory creates dated, non-overwriting experimental batches that keep
source, generated candidates, validation evidence, packaging, live results,
and promotion decisions separate.

```text
intake → source freeze → candidate → static → compiler → package → live
                                                                   │
                                                                   v
                                              hold / revise / reject / promote
```

Every batch begins at `HOLD` with pending gates. Non-pending gate results
require in-batch evidence, promotion requires all gates to pass plus explicit
approval evidence, and promoted batches become immutable.

The standalone repository replay records **10 / 10 bounded controls passing**,
including portable default output, tamper detection, unresolved-reference
refusal, premature-promotion refusal, fully gated promotion, and
post-promotion immutability. These controls establish factory behavior only;
they do not validate the semantic or runtime claims of a particular batch.

---

## Code-Lexigraph — reconstructable programming knowledge

**[Open project →](code-lexigraph/README.md)** · **[Design contract →](code-lexigraph/docs/DESIGN.md)** · **[Validation →](code-lexigraph/docs/VALIDATION.md)**

Code-Lexigraph tests whether programming meanings, requirements, construction
rules, code roles, and evidence can remain connected while a declared graph is
rehydrated into source code. The current prototype reconstructs one bounded
safe-fall-through Python profile through a restricted grammar rather than an
unconstrained code generator.

```text
meaning → requirement → contract → construction → code → evidence
   ↑                                                       │
   └──────────────── inspectable reverse trace ────────────┘
```

The retained example contains 29 graph entries, 43 relationships, 22
construction records, eight direct code mappings, and two supporting
declarations. Its repository replay records **19 / 19 tests passing** across
construction, behavior, refusal, and command-line integration checks.

Those checks qualify only the declared example and tested interpreter. They do
not establish formal semantic proof, general code synthesis, arbitrary-input
hardening, universal sentinel semantics, or guarantees about external effects.

---

## NLP Development Suite — bounded language tooling

**[Open project →](nlp-development-suite/README.md)** · **[Data policy →](nlp-development-suite/DATA_POLICY.md)** · **[Test profile →](nlp-development-suite/PROTOTYPE_TEST_PROFILE.md)**

The NLP Development Suite stages reusable lexical primitives, a controlled
natural-language front end, a code-only Lexicon Atlas interface, a bounded
read-only File Atlas, and non-executing interpretation and relational-lexicon
research. The repository carries code, schemas, contracts, and tests while
keeping dictionary payloads, generated lexical shards, historical review data,
credentials, and machine-local paths outside the public tree.

The [data-free validation profile](nlp-development-suite/PROTOTYPE_TEST_PROFILE.md)
covers **81 Python checks**, repository-policy verification, and JavaScript
syntax checks when Node.js is available. The [Windows CI workflow](.github/workflows/nlp-suite-code-only.yml)
configures Python 3.11 through 3.14 with Node.js 22. These checks establish only the
packaged code surface and declared data boundary; they do not establish lexical
completeness, semantic authority, production readiness, or approval of any
separately supplied dataset.

---

## sf-AmorphDataDrive — strict raw-substrate architecture

**[Open project →](sf-amorph-data-drive/README.md)** · **[Locked v0.3 →](sf-amorph-data-drive/specifications/sf_edabit_amorph_data_drive_locked_spec_v0_3.md)** · **[Relation to Etabit →](sf-amorph-data-drive/docs/ETABIT_RELATION.md)**

sf-AmorphDataDrive separates raw existence, relation/interpretation, and composition/coherence. Locked v0.3 keeps identity and metadata outside raw D0. The [locked sf-UUID member identity contract v0.1](sf-amorph-data-drive/contracts/SF_UUID_IDENTITY_CONTRACT_v0.1_LOCKED.md) defines member identity, including issuance, scope, duplicate and collision handling, and continuity. Storage topology, bitmap mapping, x/y packing widths, and recursion bounds remain [open decisions](sf-amorph-data-drive/docs/OPEN_DECISIONS.md).

It is related to Etabit as a possible strict substrate profile; no integration is admitted.

---

## Syn-Etabit Transformer — Textual

**[Open project →](syn-etabit-transformer-textual/README.md)** · **[Compatibility service →](syn-etabit-transformer-textual/service/README.md)** · **[Integration boundaries →](syn-etabit-transformer-textual/INTEGRATIONS.md)**

Syn-Etabit explores a document model in which text, structure, metadata, transformations, assets, and emitted artifacts retain separate identities instead of collapsing early into one opaque file.

```text
Markdown content
      +
JSON-governed document plan
      ↓
reference-native state
      ↓
ordered transformations
      ↓
resolved immutable package
      ↓
EJECT → TRANSFORM → EJECTION
      ↓
derived artifact + receipt
```

The retained CPU compatibility implementation includes immutable semantic snapshots, typed transformations, logical output streams, an explainable reducer, SQLite receipts/recovery, rendering, Markdown/DOCX adapters, and rigid/fuzzy/torture harnesses.

Open findings remain visible: rigid and bounded torture checks pass, while the retained 500-case fuzzy run exposes **three character/conversion finding groups**.

External capabilities such as WordNet, external conversion, GPU execution, and agentic control remain explicit integration boundaries rather than automatic dependencies.

---

## xOSG-0 MATH.SC-0 — Straight Computation Core

**[Open project →](xosg-0-math-sc0/README.md)** · **[Build / test evidence →](xosg-0-math-sc0/BUILD_TEST_REPORT.txt)** · **[Current wall →](xosg-0-math-sc0/docs/hardening_and_walls.md)**

MATH.SC-0 is the deterministic numerical substrate. Its purpose is to keep mathematical execution out of the language model whenever a deterministic backend can perform and verify the work.

```text
JavaScript
contract + authority plane
        ↓
Python
numerical semantics + verification
        ↓
C / C++
native deterministic kernels
        ↓
independent checks + numerical evidence
        ↓
web, only where admitted
        ↓
LLM, strict last resort
```

Current v0.8.0 work includes exact rational arithmetic, high precision, exact rational intervals, directed-rounding transcendental intervals, determinant/solve/inverse, native LU kernels, residual and conditioning diagnostics, replay fingerprints, resource ceilings, and differential/metamorphic/containment tests.

| Evidence | Result |
| --- | ---: |
| Python tests | **58 / 58 PASS** |
| JavaScript / integration tests | **23 / 23 PASS** |
| Native self-test | **PASS** |
| AddressSanitizer / UBSan | **PASS** |
| Seeded interval containment | **PASS** |
| Native LU differential testing | **PASS** |
| Exact metamorphic identities | **PASS** |

The current higher-assurance wall is explicit: independent compiled MPFR verification and real GPU/open-compute certification require development headers and hardware/runtime support outside the reference host.

---

## Holoquary — nonrecursive logic, uncertainty, and local state

**[Open project →](holoquary/README.md)** · **[Reconstitution record →](holoquary/RECONSTITUTION.md)**

Holoquary v1.3 is a C99 research substrate for deterministic three-valued logic, typed numerical domains, explicit possibility sets, uncertainty-aware comparisons and selectors, bounded local correlation, and staged transactions over small caller-owned state cells. Computational data, knowledge metadata, execution status, and provenance are kept separate.

The repository line is explicitly **RECONSTITUTED**: the original October 2 v1.3 source archive is unavailable, so the November 8 source is not claimed byte-identical. Current reconstruction tests and the preserved historical test report remain separate evidence classes. General mixed recursion, durable concurrency, authenticated provenance, Knowledge/Error Nets, bare-metal deployment, and live UPTI/SSMI/Sisterhood integration remain open.

---

# Shared design language

| Principle | Meaning here |
| --- | --- |
| **Request ≠ completion** | Asking for an action is not evidence that it occurred. |
| **Generation ≠ verification** | The component that produced a result does not automatically certify it. |
| **Authority is explicit** | Human, policy, runtime, verifier, and external-service roles remain distinguishable. |
| **Fail closed** | Invalid, ambiguous, unsupported, or excessive requests should remain visible failures. |
| **Provenance survives transformation** | Successor states, conversions, and derived artifacts retain traceable origins. |
| **External integrations begin closed** | A documented integration is not the same thing as an activated integration. |
| **Reference behavior precedes acceleration** | Faster implementations must remain comparable to the semantic reference. |
| **Evidence scopes claims** | A passing test proves the stated test, not general production readiness. |
| **History is not rewritten** | Working names, prior interfaces, findings, and reconstructed evidence remain distinguishable from current design. |

---

## Theoretical application space

Taken together, the work explores:

- human-led AI orchestration with bounded machine initiative;
- inspectable multi-stage workflows;
- deterministic services underneath language-model interfaces;
- AI-native document genesis and non-destructive revision;
- provenance-aware scientific and engineering computation;
- capability-aware execution across heterogeneous machines;
- explicit integration and production gates;
- adversarial and fuzzy testing as architecture discovery;
- reusable kernels distilled from larger experimental systems.

The emphasis is not on claiming these problems are solved. The emphasis is on making the path from **idea → mechanism → pressure → evidence → boundary** inspectable.

---

## Repository map

```text
xOSG-prototype/
│
├── amorphous-durable-ai-workspace/  DWSK source and development checks
├── Naked Shell/                staged shell identity
├── Synthetic Simulations/      bounded documentation and failed source
├── docs/xosg/                  family overview, license and migration records
├── Instrumentation/           tool instrumentation and controller examples
│
├── mill-factory/               evidence-bearing batch factory
│   ├── templates/              ledgers, contracts, decision, and rollback forms
│   └── tests/                  positive and negative factory controls
│
├── code-lexigraph/             meaning-to-code reconstruction prototype
│   ├── code_lexigraph/         dependency-free Python implementation
│   ├── examples/               retained bundle and reference program
│   ├── tests/                  construction, behavior, and CLI checks
│   └── docs/                   design, provenance, validation, open decisions
│
├── nlp-development-suite/      code-only language and lexical research suite
│   ├── projects/               bounded reusable prototype components
│   ├── development/            offline and relational-lexicon experiments
│   ├── contracts/              cross-component interface definitions
│   └── production/             non-deploying production-readiness records
│
├── syn-xOSG-0/
│   ├── growth/                 canonical developmental spine
│   ├── docs/                   source and boundary records
│   ├── history/                retained development evidence
│   └── supporting/             supporting kernels and mechanisms
│
├── etabit-schema/              standalone Etabit architectural schema research
│   ├── schema/                draft research descriptor schema
│   ├── examples/              illustrative four-symbol source
│   └── docs/                  decisions and open contracts
│
├── sf-amorph-data-drive/       strict raw-substrate architecture
│   ├── specifications/         locked v0.2/v0.3 baselines
│   ├── docs/                   direction and boundaries
│   └── evidence/               review summaries
│
├── syn-etabit-transformer-textual/
│   ├── service/                retained CPU compatibility implementation
│   ├── docs/                   contracts, validation, findings, integrations
│   └── ...                     transformation and research artifacts
│
├── xosg-0-math-sc0/
│   ├── js/                     JavaScript control plane + frozen web UI
│   ├── src/                    Python numerical and verification plane
│   ├── native/                 C/C++ kernels
│   ├── protocol/               operation and result contracts
│   ├── tests/                  numerical and hardening suites
│   └── docs/                   architecture, evidence, walls
│
├── gfx-form-engine/            JSON-0 and lexical raster CPU scaffold
├── semantic-symbol-interpreter/ synthetic-text interpretation and fixtures
├── holoquary/                  reconstituted v1.3 source ZIP and UPTI handoff candidate
└── governed-microserver-transmigration/ JSON manifest and glue validation
```

---

## Start here

1. **[xOSG-0](syn-xOSG-0/README.md)** — developmental and authority model.
2. **[Mill Factory](mill-factory/README.md)** — evidence-bearing batches and fail-closed promotion.
3. **[Code-Lexigraph](code-lexigraph/README.md)** — bidirectional meaning-to-code reconstruction.
4. **[NLP Development Suite](nlp-development-suite/README.md)** — code-only lexical, grammar, and language-tool prototypes.
5. **[Etabit Schema](etabit-schema/README.md)** — multi-drive construction and distributed-authority schema research.
6. **[sf-AmorphDataDrive](sf-amorph-data-drive/README.md)** — raw substrate, locked member identity, and open successor contracts.
7. **[Syn-Etabit Transformer — Textual](syn-etabit-transformer-textual/README.md)** — reference-native document model.
8. **[MATH.SC-0](xosg-0-math-sc0/README.md)** — deterministic computation architecture.
9. **[xOSG instrumentation](docs/xosg/README.md)** — durable workspace kit, shell identity, and simulation records.
10. **[GFX Form Engine](gfx-form-engine/README.md)** — frame-scoped data, execution, and recovery research.
11. **[Semantic Symbol Interpreter](semantic-symbol-interpreter/README.md)** — contextual readings and evidence for synthetic text.
12. **[Holoquary](holoquary/README.md)** — reconstituted v1.3 source and its evidence boundary.
13. **[Governed Microserver Transmigration](governed-microserver-transmigration/README.md)** — candidate manifest and glue validation. [Verification notes](governed-microserver-transmigration/docs/VERIFICATION.md) distinguish functional and static checks from unverified native Windows containment.

Read each project's validation, source-boundary, and integration documents before treating test results as broader acceptance.

---

## Licensing

See the [licensing index](LICENSING.md) for file-specific grants and existing component notices.

## Public repository boundary

This is a **public prototype and research repository**.

Public visibility does not change the status of the work. The presence of code, passing tests, a historical release label, or a documented integration does **not** imply production deployment, autonomous authority, external activation, or general certification.

Machine-local environments, caches, mutable runtime stores, installed browser distributions, downloaded third-party payloads, and other host-specific material are intentionally excluded where they would blur the boundary between source and environment.

Each project retains its own decisions, contracts, compatibility boundaries, evidence, validation status, integration gates, and production gate.

---

<div align="center">

---

**Prototype systems should make their limits easier to inspect, not easier to forget.**

</div>
