# Holoquary v1.3

Holoquary is a bounded C99 research substrate for deterministic logic, typed numerical computation, uncertainty-aware higher functions, small transactional state, LESSONS/feedback, recovery experiments, and optional neural components.

**Project direction:** m.A.R.S.  
**Repository status:** RECONSTITUTED v1.3 candidate  
**Reconstitution date:** 2026-11-08  
**Deployment status:** host-tested prototype; not independently attested, production-certified, or board-specific firmware.

> The original October 2, 2026 v1.3 source archive is not available in the current source set. This repository line was reconstructed from the complete preserved v1.2 source plus the surviving v1.3 contract, historical test report, error log, and TODO material. It is **not claimed to be byte-identical** to the lost original.

## Purpose

Holoquary explores a small computational foundation in which:

- computational values remain separate from knowledge about those values;
- execution status and error conditions do not silently become arithmetic data;
- provenance remains a distinct record;
- uncertainty can be represented without manufacturing an exact value;
- higher functions can preserve local correlation within one bounded operation;
- state changes can be staged and rejected before commit;
- generated or inferred results do not automatically grant authority.

The current development line remains intentionally nonrecursive at the higher-function layer. An older bounded pure-logic recursive evaluator remains in the historical lineage, but general mixed recursion is deferred.

## Current capability stack

| Area | Current capability |
| --- | --- |
| Logic | Strong-Kleene TRUE/FALSE/UNKNOWN foundation; NAND plus NOT, AND, OR, XOR, implication, equivalence, majority |
| Numeric domains | Balanced ternary, PURE5, BLOCK7 / balanced-seven research substrate |
| Knowledge representation | Exact values or explicit possibility masks; exact logical UNKNOWN remains distinct from epistemic {FALSE, TRUE} |
| Higher functions | Comparison sets, inclusive range checks, selectors, majority and diagnostic guards |
| Local correlation | Reuses one completion of an unresolved value throughout a bounded compound operation such as BETWEEN |
| State | Caller-owned typed cells with instance identity and generation |
| Transactions | Staged all-or-nothing commit for 1–4 local cells under single-threaded/disjoint-pointer preconditions |
| LESSONS | Bounded facts/rules and externally admitted lesson mechanisms inherited from earlier versions |
| Recovery | Bounded recovery/error recording and reevaluation experiments inherited from earlier versions |
| Neural | Feed-forward neural kernel and experimental neural supervisor remain available |
| Composition | Typed logical/numerical ports, explicit conversion policies, NAND-composed gates, switches, MUX/DEMUX and guarded logical controls |

## Architectural boundary

```text
COMPUTATIONAL DATA
    │
    ├── logic
    ├── numeric domains
    └── neural values
    │
    ▼
HIGHER FUNCTIONS
    │
    ├── compare
    ├── select
    ├── range
    ├── majority
    └── guards
    │
    ▼
LOCAL STATE / TRANSACTIONS

SEPARATE RECORDS:
    knowledge metadata
    execution status
    provenance
```

A failed computation does not become FALSE or zero merely because another operand would normally annihilate it. An empty possibility set represents contradiction, not numerical zero and not logical UNKNOWN.

## v1.3 higher-function interface

The v1.3 layer adds normalized operations over the v1.2 separated record type:

- `hqdn_logic`
- `hqdn_guard`
- `hqdn_compare_set`
- `hqdn_between`
- `hqdn_select`
- `hqdn_cell_init`
- `hqdn_cell_read`
- `hqdn_tick_transaction`

The local transaction layer stages every proposed update before committing any cell. Successful HOLD and WRITE operations advance generation. Rejected transactions leave caller-visible cell state unchanged under the documented preconditions.

## Local-correlation example

For:

```text
X ∈ {0,+1}
lower = +1
upper = 0
```

independent predicates can each admit a TRUE completion:

```text
X >= +1
X <= 0
```

but no single value of X satisfies both. `hqdn_between` reuses the same completion of X through both clauses and therefore returns definite FALSE.

This is local correlation inside one bounded operation. It is **not** a claim of general symbolic variable identity across an arbitrary graph.

## Validation evidence

Current reconstitution evidence:

| Check | Result |
| --- | --- |
| GCC strict C99 | PASS |
| Clang strict C99 | PASS |
| Reconstitution suite | **187,861 assertions PASS** |
| Targeted undefined/bounds sanitizer | PASS |
| Inherited functional suites | PASS |
| GCC freestanding host relocatable object | no unresolved symbols |
| Clang freestanding host relocatable object | no unresolved symbols |

The preserved historical October 2 report records **857,664 assertions** for the lost original v1.3 implementation. That count remains historical evidence only and is not relabeled as a result from the current reconstitution.

Prepared source-package SHA-256:

```text
df9ca9d4543e85537525c9237a002bdfb1b61c1a1b522058f239011dc621a9d0
```

The prepared source archive contains 186 ZIP entries.

## Evidence limits

The current evidence does **not** establish:

- byte-identical recovery of the lost October 2 v1.3 source;
- general mixed neural/logic/state recursion;
- durable or crash-safe transactions;
- thread-safe or concurrent mutation;
- cryptographically authenticated provenance or receipts;
- trusted autonomous lesson admission;
- a completed Knowledge Net or dependency-aware Error Net;
- real bare-metal board execution;
- live UPTI, SSMI, or Sisterhood integration.

## Development direction

The next pre-recursion work is expected to focus on:

1. dependency and justification tracking for knowledge;
2. dependency-aware failure isolation for errors;
3. explicit revision/invalidation without rewriting observed history;
4. retaining source and authority boundaries across those overlays;
5. only then reconsidering broader recursive composition.

Existing expert-system and recovery research is being mined for patterns rather than imported wholesale.

## Repository provenance

This project should preserve three evidence classes separately:

1. **historical evidence** from the lost October 2 v1.3 implementation;
2. **reconstitution evidence** from the November 8 source reconstruction;
3. **future modifications** made after repository publication.

Do not silently merge those classes.

## Relationship to the wider repository

Holoquary is a separate research system within `xOSG-prototype`. It may exchange patterns or future interfaces with xOSG, MATH.SC-0, SSMI, UPTI, and other projects, but those relationships do not imply runtime dependency, shared authority, or completed integration.

---

**Boundary rule:** make computational state simple, keep metadata typed, preserve uncertainty, and do not let successful execution certify its own truth or authority.
