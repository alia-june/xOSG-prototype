# Working research prompt — Next boundary after v0.3

## Purpose

Review the local candidate microserver transmigration package and design the smallest next independent validation step. Do not change the existing source witness, claim admission, or activate Crete merely because it is named.

## Inputs

- `source_witness/check_manifest_v0_2.py` (historical behavior witness)
- `contracts/manifest_v0_2.schema.json` (source and destination schema contract)
- `microtrans/` (two separate-process JSON CLI candidate microservers and glue)
- `examples/implementation_manifest_v0_3.json` (candidate composition)
- `tests/test_transmigration.py` (current differential/regression corpus)

## Research questions

1. What additional independent tests distinguish v0.2 behavior from v0.3 behavior under malformed, adversarial and extreme-but-valid manifests?
2. Which process boundary gives genuine least-privilege read-only execution on the target Windows system? Specify the responsible component and independently verifiable evidence.
3. What is the minimal authenticated JSON IPC transport contract that preserves a participating microserver's right to refuse without implicit authority transfer?
4. How can glue compatibility be attested independently, with input and output schema references and verified identity-only semantics?
5. What exact witness is necessary to make *break-before-mutation* of a Crete join enforceable and independently detectable?
6. What external authority decides admission and seals/publishes an immutable generation, without circular trust in candidate microservers?

## Required method

- Apply recurring Being, Belief, Understanding and Observation functions to each proposed distinction, claimed property and evidence artifact.
- Identify source observations vs requirements vs inferences explicitly. No guesses promoted to facts.
- Use four-field intent: Goal, Current Task, Task Queue, Finished Task Queue. Identity and history remain distinct.
- Provide at least one intentionally invalid counterexample per invariant; preserve failure evidence rather than silently fixing it.
- Never use `null` in proposed machine-readable artifacts; use semantically typed named sentinels.
- Keep Knowledge Core as knowledge/evidence, not the executable process implementation.
- Start with an independently testable computational reference model. Defer GPU/voxel and kernel/minifilter integration until correctness is supported.
- Report verified vs unverified vs blocked properties. No autonomous admission or publication.

## Expected deliverables

A source-grounded gap ledger; a formal candidate transition/authority model; a bounded negative/property test plan; an independent validator reference implementation where feasible; a validation report; and explicit unresolved decisions. Never overwrite earlier specification generations; produce a new version with lineage.
