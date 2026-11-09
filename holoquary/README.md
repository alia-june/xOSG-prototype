# Holoquary v1.3

Holoquary is a bounded C99 research substrate for deterministic logic, typed numerical computation, explicit uncertainty, higher functions, small transactional state, LESSONS/feedback, recovery experiments, and optional neural components.

**Project direction:** `m.A.R.S.`  
**Current repository line:** **RECONSTITUTED v1.3 candidate**  
**Reconstitution date:** 2026-11-08  
**Deployment status:** host-tested prototype; not independently attested, production-certified, or board-specific firmware.

> **Provenance notice:** the original October 2, 2026 v1.3 source archive is not available in the current source set. The published v1.3 source was reconstructed from the complete preserved v1.2 source plus the surviving v1.3 contract, historical test report, AI error log, and TODO material. It is **not claimed to be byte-identical** to the lost original. See [RECONSTITUTION.md](RECONSTITUTION.md).

---

## Downloads

The complete artifacts are stored in this repository.

### Holoquary v1.3 — reconstituted source

**[Download the complete source ZIP](releases/holoquary_nonrecursive_v1_3_RECONSTITUTED_2026-11-08_source.zip)**

- Size: **580,705 bytes**
- ZIP entries: **186**
- SHA-256: `df9ca9d4543e85537525c9237a002bdfb1b61c1a1b522058f239011dc621a9d0`
- Git blob: `7ead07af24466eed93cce20e541b027ece88d4de`

This is the complete current v1.3 reconstitution, including source, tests, examples, preserved baseline components, contracts, logs, and historical evidence.

### Holoquary UPTI handoff v0.2 — candidate

**[Download the UPTI handoff ZIP](releases/holoquary_upti_handoff_v0_2_candidate.zip)**

- Size: **53,254 bytes**
- ZIP entries: **34**
- SHA-256: `72dca130208f12a4dd226b128ace15db5f153b0c93bcd09c0975f8064abf0d04`
- Git blob: `07644b30c287505f80c652d69d7d2bee0df93152`

This package is a **local application-handoff candidate**, not a live transport implementation. It does not establish authenticated peer communication, delivery, UPTI wire conformance, Sisterhood communication, or remote execution.

Both repository ZIP blobs were transferred byte-for-byte and their Git object hashes were checked against the supplied local files before publication.

---

## What Holoquary is

Holoquary investigates a small computational substrate in which **computation, knowledge, execution status, and provenance remain separate concerns**.

The central design direction is that a value should not silently gain meaning or authority merely because a computation completed.

At the current boundary:

```text
                    HOLOQUARY

          ┌───────────────────────┐
          │ COMPUTATIONAL VALUES  │
          │                       │
          │ logic   numeric neural│
          └───────────┬───────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │  HIGHER FUNCTIONS     │
          │                       │
          │ compare · select      │
          │ range · majority      │
          │ guards · composition  │
          └───────────┬───────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │ LOCAL STATE / CELLS   │
          │ staged transactions   │
          └───────────────────────┘

     SEPARATE FROM THE VALUE ITSELF:

     knowledge        execution        provenance
     possibilities    completion       source/scope
     uncertainty      failure          generation
     constraints      diagnostics      origin
```

Holoquary is not intended to collapse these layers into a single scalar or universal "confidence" value.

---

## Core rules

### 1. Computational data is not metadata

A numerical value is a numerical value. A logical symbol is a logical symbol. Knowledge about a value belongs in a different lane.

The v1.2/v1.3 normalized record is:

```text
HQDRecord
├── domain
├── data
│   ├── exact number
│   ├── exact logic
│   └── absent
├── knowledge
│   ├── possibility mask
│   └── opaque unknown grade
├── execution
│   ├── COMPLETE
│   ├── FAILED
│   └── COMPLETION_UNKNOWN
└── provenance
    ├── source
    ├── scope
    ├── generation
    └── origin
```

No lane is allowed to silently impersonate another.

### 2. Logical UNKNOWN is not missing numerical data

Strong-Kleene logic contains a legitimate exact logical value:

```text
FALSE
UNKNOWN
TRUE
```

An exact Kleene `UNKNOWN` is therefore **computational data inside KLEENE3**.

By contrast:

```text
X ∈ {FALSE, TRUE}
```

means that the available knowledge does not determine which definite logical value applies.

Those are intentionally different states.

### 3. Contradiction is not zero and not execution failure

A possibility mask with no remaining values represents an empty set of admissible possibilities.

That means:

```text
CONTRADICTION != 0
CONTRADICTION != UNKNOWN
CONTRADICTION != EXECUTION_FAILED
```

The execution lane remains responsible for reporting whether the operation itself failed.

### 4. Provenance is not attestation

Source, scope, generation, origin, hashes, and message IDs are useful identifiers and trace information.

They do **not**, by themselves, prove:

- authenticity;
- truth;
- authorization;
- independent verification;
- sender identity;
- permission to execute an external effect.

### 5. Successful computation does not grant authority

A guard may compute TRUE. A comparison may be definite. A neural score may cross a threshold. A lesson may derive a result.

None of those events automatically authorize an external action.

---

## Computational domains

The normalized v1.3 layer supports four declared domains.

| Domain | Computational meaning | Partial knowledge |
| --- | --- | --- |
| `BALANCED3` | numerical `-1, 0, +1` | possibility mask over the three exact values |
| `PURE5` | numerical `0..4` | possibility mask over five exact values |
| `BALANCED7` | numerical `-3..+3` | possibility mask over seven exact values |
| `KLEENE3` | logical `FALSE, UNKNOWN, TRUE` | logical possibility mask when the exact symbol is unresolved |

Conversions between domains are explicit. Ordinal positions are not assumed to have the same numerical or logical meaning across domains.

---

## v1.3 higher-function layer

The reconstituted v1.3 module is implemented in:

```text
src/hqd_functions.h
src/hqd_functions.c
```

Its public operations include:

| Function | Purpose |
| --- | --- |
| `hqdn_logic` | NOT, AND, OR, XOR, IMPLIES, EQUIV, MAJORITY over normalized logical records |
| `hqdn_guard` | strict three-input diagnostic logical conjunction |
| `hqdn_compare_set` | enumerate possible numerical relation outcomes |
| `hqdn_between` | inclusive range evaluation while retaining local value correlation |
| `hqdn_select` | logical/numerical branch selection under definite or unresolved selectors |
| `hqdn_cell_init` | initialize a caller-owned typed state cell |
| `hqdn_cell_read` | read cell state and generation together |
| `hqdn_tick_transaction` | preflight, stage, and commit 1–4 cell ticks as one bounded local operation |

The higher-function layer consumes and emits the v1.2 `HQDRecord` representation.

---

## Local correlation

Possibility sets are not automatically symbolic variables.

For example:

```text
X ∈ {0,+1}
lower = +1
upper = 0
```

If two comparisons are evaluated independently:

```text
X >= +1
X <= 0
```

each comparison has a possible TRUE outcome—but those TRUE outcomes require **different values of X**.

A naive conjunction could therefore manufacture an impossible TRUE.

`hqdn_between(value, lower, upper)` avoids that error by reusing each single completion of `value` through both clauses:

```text
+1 <= X <= 0  =>  FALSE
```

This establishes **local correlation inside that bounded operation**.

It does **not** establish general symbolic identity across arbitrary records or across a computation graph. Two equal possibility masks do not imply that they represent the same unresolved variable.

---

## Small transactional state

v1.3 adds caller-owned `HQDNCell` state:

```c
typedef struct {
    uint32_t instance_id;
    uint32_t generation;
    HQDRecord state;
} HQDNCell;
```

A transaction can contain **1–4 ticks**.

The implementation performs preflight and result construction before committing any cell:

```text
ticks
  │
  ▼
validate
  ├── pointers
  ├── cell identity
  ├── generations
  ├── domains
  ├── selectors
  ├── write records
  └── duplicate-cell rejection
  │
  ▼
stage every resulting state
  │
  ├── failure ───────► no commit
  │
  ▼
commit all staged cells
  │
  ▼
receipts
```

A successful HOLD is still a successful tick and advances generation by one.

### Transaction ceiling

This is **local function-call atomicity under documented assumptions**, not a durable database transaction.

It does not currently provide:

- crash atomicity;
- journaled recovery;
- thread-safe concurrent mutation;
- protection from hostile pointers;
- authenticated receipts;
- hardware-fault tolerance;
- persistent replay protection.

---

## Strong-Kleene logic foundation

The original Holoquary logic kernel uses three-valued strong-Kleene semantics:

```text
FALSE
TRUE
UNKNOWN
```

The historical logic path includes a NAND primitive and static NAND graph composition. XOR is constructed from NAND rather than being treated as a privileged primitive.

NAND remains a useful deterministic reference primitive; it is **not the definition of a holon** and does not imply that every later domain or subsystem must be represented as NAND gates.

An execution error is reported through status/state and is not inserted as a fourth truth-table symbol.

---

## LESSONS

The preserved LESSONS subsystem provides a bounded, caller-owned rule/fact mechanism.

Two paths remain distinct:

### QUICK

```text
hq_eval(...)
```

Evaluates the logic program directly and does not consult LESSONS.

### EXTENDED

```text
hq_eval_extended(...)
```

May use externally admitted facts and rules under an exact scope and an explicit round budget.

Its basic model is:

```text
admitted fact/rule
      │
      ▼
bounded inference rounds
      │
      ├── fixed point
      ├── conflict
      └── budget exhaustion
      │
      ▼
logical result + trace
```

Important boundaries:

- repetition does not create truth;
- more rounds do not invent evidence;
- a source ID is not authentication;
- conflict or exhaustion conservatively produces unresolved logic rather than a fabricated definite answer;
- admission policy remains external to the underlying NAND evaluator.

---

## Feedback and lesson admission

The feedback layer adds candidate lesson handling around the existing LESSONS bank.

It supports:

- candidate facts;
- candidate rules;
- anti-lessons / scoped negative observations;
- caller-selected verifier callback;
- ACCEPT / REJECT / DEFER;
- conflict recording;
- local generation and decision history.

A verifier callback is still caller supplied. Holoquary does not prove that the verifier is independent, trustworthy, or cryptographically identified.

A rejected observation is not automatically logical FALSE.

---

## Recovery

The recovery subsystem provides bounded local recovery experiments and error recording.

It can represent a failed evaluation, attempt bounded reevaluation, and retain recovery-related records.

Its current role is deliberately limited.

It is not:

- a durable recovery journal;
- side-effect rollback;
- protected storage;
- independent attestation;
- a crash-safe system supervisor;
- permission to repeat arbitrary external effects.

The broader dependency-aware **Error Net** remains future work.

---

## Flexibility layer

The v0.7 flexibility work adds typed logical/numerical ports, snapshots, identities, policy-controlled numerical-to-logical classification, generation checks, and bounded caller-owned structures.

This allows components to exchange typed state without silently treating a numerical score as a logical fact.

For example, a numerical classifier can produce:

```text
FALSE    x <= false_max
UNKNOWN  false_max < x < true_min
TRUE     x >= true_min
```

The resulting TRUE means **the value satisfied the declared threshold**. It is not independent evidence that a real-world proposition is true.

---

## Composites and state primitives

The composite layer includes bounded deterministic structures such as:

- NOT;
- AND;
- OR;
- NOR;
- XNOR;
- XOR;
- enabled switch;
- consensus MUX;
- DEMUX;
- guarded logical lock;
- explicit-tick bit/state cells.

These are functional components, not authentication or physical security primitives.

A "guarded lock" in this context is a logical gate structure. It does not establish identity or external authorization.

---

## Numerical research

### PURE5

PURE5 is a numerical radix-five domain over exact digits:

```text
0 1 2 3 4
```

The package includes bounded digit arithmetic, carry handling, comparisons, configurable predicate tables, word operations, and state experiments.

UNKNOWN and ERROR are not PURE5 digits in the normalized v1.2/v1.3 representation.

### Balanced ternary

Balanced ternary uses:

```text
-1 0 +1
```

It remains a numerical domain separate from KLEENE3 logic.

Historical TERNARY-UE interfaces are retained for compatibility, but the normalized layer separates numerical data from uncertainty and execution state.

### BLOCK7 / balanced-seven profile

The user-specified 3–1–3 structure is:

```text
block -1 : [-1, 0, +1]
block  0 : [0]
block +1 : [-1, 0, +1]
```

The bounded arithmetic prototype maps those seven valid structural pairs to `-3..+3` using a proposed balanced-seven profile.

That numerical mapping is an implemented research profile—not a claim that every use of the 3–1–3 structure must adopt balanced-seven arithmetic.

BLOCK7 also demonstrates an important representation rule: digit and carry outcomes are kept **joint** during lifted arithmetic so independent marginal sets cannot manufacture impossible combinations.

---

## Higher logic

The higher-logic layer adds:

- equality and inequality;
- less/greater comparisons;
- zero/known/unknown/error predicates;
- NOT/AND/OR/XOR;
- implication and equivalence;
- MIN/MAX;
- range checks;
- majority;
- conditional selection;
- bounded word comparison;
- configurable PURE5 predicate tables.

Historical TERNARY-UE and four-outcome interfaces remain compatibility layers. v1.2/v1.3 is the normalized direction for keeping computation and metadata separate.

---

## Neural components

The package retains a small feed-forward neural baseline and an experimental neural action supervisor.

The neural supervisor was tested as a bounded imitation experiment over a four-state synthetic policy. It matched the deterministic labels in that in-sample experiment.

That experiment **did not demonstrate**:

- improvement over the deterministic controller;
- out-of-distribution generalization;
- calibrated truth probability;
- autonomous lesson creation;
- authority to execute an action;
- evidence of general intelligence.

The neural path is optional and can be disabled without changing the deterministic logic substrate.

---

## Recursion status

The source lineage contains a **bounded pure-NAND DAG evaluator** with:

- caller-owned immutable nodes;
- maximum 16 reachable nodes;
- maximum depth 8;
- strong-Kleene NAND evaluation;
- cycle rejection;
- duplicate identity checks;
- generation/snapshot checks;
- memoization of shared DAG nodes;
- bounded execution trace.

That is a narrow historical recursion experiment.

**General Holoquary recursion remains deferred.**

Not implemented as a general recursive substrate:

- arbitrary mixed logic/neural/state recursion;
- recurrent mutable cycles;
- recursive state ownership;
- arbitrary typed port routing through nested holons;
- durable recursive recovery;
- distributed recursive execution.

---

## Normalized value model

The principal v1.2/v1.3 type is `HQDRecord`.

Conceptually:

```text
record
│
├── domain
│
├── data
│   └── exact computational payload or ABSENT
│
├── knowledge
│   └── possible values + opaque grade
│
├── execution
│   └── completion/failure state
│
└── provenance
    └── source/scope/generation/origin
```

### Unknown grades

`U1/U2/U3` are retained only as opaque caller-provided classifications.

No ordering, probability, confidence semantics, truth semantics, or automatic transition rule is currently assigned to them.

---

## Error handling

Holoquary intentionally keeps several conditions separate.

| Condition | Meaning |
| --- | --- |
| exact logical `UNKNOWN` | a legitimate KLEENE3 computational symbol |
| non-singleton possibility mask | available knowledge permits multiple exact values |
| empty possibility mask | contradiction / no admissible values under current constraints |
| `EXEC_FAILED` | the operation failed |
| legacy E marker | compatibility marker; not automatically proof of runtime failure |
| non-OK API status | validation/runtime operation did not complete normally |

An error cannot be hidden merely because another operand would normally dominate the mathematical result.

For example, a failed input is not silently converted into clean FALSE by an annihilating logical branch.

---

## Build

The source archive uses C99 and a Makefile.

### Requirements

Typical host build:

- GCC or Clang;
- `make`;
- a C99-capable host environment.

The package has been exercised with strict warning settings:

```text
-std=c99 -O2 -Wall -Wextra -Wpedantic -Werror
```

### Extract and enter the source tree

```sh
unzip holoquary_nonrecursive_v1_3_RECONSTITUTED_2026-11-08_source.zip
cd holoquary_nonrecursive_v1_3_RECONSTITUTED
```

### Run the reconstructed v1.3 tests

```sh
make CC=gcc functions_test
make CC=clang functions_test
```

### Run the full integrated functional suite

```sh
make CC=gcc test
make CC=clang test
```

### Run preserved baseline tests

```sh
make CC=gcc baseline
```

### Build the freestanding host relocatable object

```sh
make CC=gcc freestanding
make CC=clang freestanding
```

The freestanding target proves host object-level compilation and an unresolved-symbol check. It does **not** prove boot or execution on physical bare-metal hardware.

### Run sanitizer targets

```sh
make CC=gcc sanitized
```

The current v1.3 reconstitution evidence separately records a targeted GCC undefined/bounds sanitizer pass for the reconstructed function suite.

### Selected demos

```sh
make CC=gcc functions_demo
make CC=gcc separation_demo
make CC=gcc block7_demo
make CC=gcc higher_demo
make CC=gcc composites_demo
make CC=gcc flex_demo
make CC=gcc feedback_demo
make CC=gcc recovery_demo
make CC=gcc recursive_demo
make CC=gcc supervisor_demo
```

---

## Validation evidence

### Current reconstitution

Observed for the November 8, 2026 reconstruction:

| Check | Result |
| --- | --- |
| GCC strict C99 reconstructed suite | **PASS — 187,861 assertions** |
| Clang strict C99 reconstructed suite | **PASS — 187,861 assertions** |
| GCC targeted undefined/bounds sanitizer | **PASS — 187,861 assertions** |
| Complete inherited functional suite, GCC | PASS |
| Complete inherited functional suite, Clang | PASS |
| GCC freestanding combined host object | no unresolved symbols |
| Clang freestanding combined host object | no unresolved symbols |

### Historical v1.3 evidence

The surviving October 2 historical report records:

```text
857,664 assertions
```

for the lost original implementation.

That number remains **historical evidence only** and is not relabeled as a test result from the reconstructed source.

---

## Source archive layout

The published ZIP contains the working source tree rather than only release binaries.

```text
holoquary_nonrecursive_v1_3_RECONSTITUTED/
│
├── Makefile
├── MANIFEST_SHA256.txt
├── README.md
│
├── src/
│   ├── hqd_functions.*
│   ├── hqd_separation.*
│   ├── hq_block7.*
│   ├── hq_higher.*
│   ├── hq_radix5.*
│   ├── hq_composites.*
│   ├── hq_cells.*
│   ├── hci_flex.*
│   ├── hci_feedback.*
│   ├── hci_recovery.*
│   ├── hci_recursive.*
│   ├── hci_supervisor.*
│   └── adapters/controller support
│
├── tests/
│   └── functional tests for each major module
│
├── examples/
│   └── runnable bounded demonstrations
│
├── docs/
│   ├── contracts
│   ├── test reports
│   ├── error logs
│   ├── stage logs
│   ├── migration/reconstitution records
│   └── TODO material
│
├── baseline/
│   ├── Holoquary LESSONS v0.2
│   └── neural topology baseline
│
├── reference/
│   └── preserved controller/research documentation
│
└── logs/
    └── compiler/test receipts retained with the package
```

---

## Development lineage

The current package preserves several additive research stages.

| Stage | Main contribution |
| --- | --- |
| v0.1 | static NAND DAG, strong-Kleene logic, XOR reference composition |
| v0.2 | optional bounded LESSONS facts/rules and fixed-point rounds |
| integration/controller stages | typed frames, deterministic action proposals, logic/neural adapters |
| feedback | verifier-mediated candidate facts/rules/anti-lessons |
| recovery | bounded reevaluation/error records |
| supervisor experiment | separate small neural action proposer; benefit not established |
| recursive experiment | bounded pure-NAND DAG evaluation |
| v0.7 FLEX | typed logical/numerical ports, snapshots and explicit classification |
| v0.8 composites | gates, switches, MUX/DEMUX, guarded logic, explicit-tick state |
| v0.9 radix research | PURE5 and historical balanced-ternary UE interfaces |
| v1.0 | higher logic and uncertainty-aware predicates |
| v1.1 | BLOCK7 3–1–3 structure and optional balanced-seven arithmetic |
| v1.2 | explicit computational / knowledge / execution / provenance separation |
| v1.3 | normalized higher functions, local correlation and 1–4-cell staged transactions |

The stages are preserved as research lineage. Later stages do not retroactively prove earlier experimental claims.

---

## Relationship to Holon research

Holoquary is related to the repository's broader Holon work but is not identical to the entire Holon architecture.

See:

**[Holon design research](../syn-etabit-transformer-textual/research/holon-design/README.md)**

That research includes decomposition, occurrence/reference work, source mining, and conceptual illustrations.

Holoquary provides one bounded computational substrate that can inform future holonic composition; it does not define every holon, every identity model, or the complete xOSG architecture.

---

## UPTI boundary

The published UPTI handoff candidate intentionally stops before transport.

Current local flow:

```text
Holoquary application payload
        │
        ▼
local validation
        │
        ▼
stage
        │
        ▼
verify same captured bytes
        │
        ▼
mark READY_FOR_UPTI_HANDOFF
        │
        ▼
[ future accepted UPTI adapter boundary ]
```

`READY_FOR_UPTI_HANDOFF` means only that the local application candidate reached its declared local state.

It does **not** mean:

- delivered;
- remotely acknowledged;
- authenticated;
- encrypted;
- authorized;
- accepted by another model;
- accepted as canonical knowledge.

Holoquary remains the application producer/consumer. It is not the transport authority.

---

## What is not currently claimed

Holoquary v1.3 does **not** establish:

- byte-identical recovery of the lost October 2 v1.3 source;
- a universal many-valued logic;
- general symbolic variable identity;
- complete Knowledge Net or truth-maintenance system;
- dependency-aware Error Net;
- autonomous truth discovery;
- autonomous lesson admission;
- neural-controller advantage;
- general mixed neural/logic/state recursion;
- durable/crash-safe transactions;
- concurrent/thread-safe state mutation;
- cryptographic authentication;
- authenticated provenance;
- remote execution authority;
- physical seven-state hardware;
- board-specific bare-metal execution;
- live UPTI transport;
- live Sisterhood communication;
- SSMI integration.

These are separate future research or integration questions.

---

## Current development direction

The current pre-general-recursion direction is:

1. retain the v1.2 computational/metadata separation;
2. continue strengthening deterministic higher functions and state semantics;
3. add justification/dependency tracking to knowledge without turning metadata into computational values;
4. add dependency-aware failure isolation without letting diagnostics authorize recovery;
5. preserve immutable observations and explicit invalidation/revision;
6. measure optional neural assistance against deterministic baselines before granting it any larger role;
7. defer Universal/UPTI/SSMI/Sisterhood adaptation until an accepted communications boundary exists.

Existing expert-system, recovery, and dependency work in the wider project is being **mined for patterns and contracts**, not imported wholesale into Holoquary.

---

## Evidence and authority policy

When extending Holoquary, preserve these distinctions:

```text
OBSERVED
    !=
INFERRED
    !=
PROPOSED
    !=
AUTHORIZED
    !=
ATTESTED
```

Likewise:

```text
computation completed
    !=
result externally true
    !=
result authorized for action
```

A later success must not be used to retroactively certify an earlier unavailable or failed implementation.

Historical evidence, reconstitution evidence, and future repository changes should remain separately identifiable.

---

## Repository files

At the repository level:

```text
holoquary/
├── README.md
├── RECONSTITUTION.md
└── releases/
    ├── holoquary_nonrecursive_v1_3_RECONSTITUTED_2026-11-08_source.zip
    └── holoquary_upti_handoff_v0_2_candidate.zip
```

For implementation details, download the source archive and begin with:

- `README.md`
- `docs/V13_FUNCTION_CONTRACT.md`
- `docs/V13_RECONSTITUTION_REPORT.md`
- `docs/V12_SEPARATION_CONTRACT.md`
- `docs/CONTRACT.md`
- `Makefile`

---

## Attribution

Project direction and originating architectural requirements: **m.A.R.S.**

Implementation artifacts in this repository include operator-specified architecture, assistant-generated candidate interfaces and code, preserved experiments, and reconstructed source. Individual contracts identify where a numerical profile, API, or implementation detail is a generated proposal rather than an accepted architectural requirement.

---

**Boundary rule:** keep computational state simple, keep metadata typed and separate, preserve uncertainty and contradiction explicitly, preserve provenance without mistaking it for attestation, and do not let successful execution certify its own truth or authority.
