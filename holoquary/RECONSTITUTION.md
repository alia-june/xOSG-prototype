# Holoquary v1.3 reconstitution record

## Disposition

**Status:** RECONSTITUTED SOURCE CANDIDATE  
**Date:** 2026-11-08  
**Project direction:** m.A.R.S.

The original October 2, 2026 Holoquary v1.3 source ZIP was unavailable in the active source set. A byte-identical recovery is therefore **not claimed**.

## Reconstruction basis

The current source candidate was rebuilt from:

- the complete preserved Holoquary v1.2 source;
- the surviving v1.3 higher-function contract;
- the surviving historical v1.3 test report;
- the surviving v1.3 AI error log;
- the surviving v1.3 TODO material.

The reconstruction restores the documented v1.3 nonrecursive surface: normalized logic, guards, comparison sets, correlated inclusive range checks, selectors, caller-owned cells, and bounded 1–4-cell staged transactions.

## Current verification

- GCC strict C99: PASS.
- Clang strict C99: PASS.
- Reconstitution suite: **187,861 assertions PASS**.
- Targeted GCC undefined/bounds sanitizer: PASS.
- Inherited functional suites: PASS.
- GCC/Clang freestanding host relocatable objects: no unresolved symbols.

## Historical evidence

The preserved October 2 v1.3 report records **857,664 assertions** for the lost historical implementation.

That count is retained as historical evidence only. It is not used as evidence for the reconstructed source.

## Prepared source package

SHA-256:

```text
df9ca9d4543e85537525c9237a002bdfb1b61c1a1b522058f239011dc621a9d0
```

Archive entries: **186**

## Evidence rule

Future repository changes should retain the distinction:

```text
historical v1.3 evidence
        !=
2026-11-08 reconstitution evidence
        !=
later repository development
```

No later success should be used to retroactively certify the unavailable historical source.
