# Basic downloadable artifact scope — 2026-10-01

## User direction

The user requested a downloadable artifact with no approver requirement and a
basic function. This record applies that direction only to the bounded local
artifact `nlp-offline-interpreter/0.1.0-basic`.

## Included

- a dependency-free `--basic` command;
- deterministic surface tokenization with exact offsets;
- bounded input and output;
- a wheel, schema, instructions, build evidence, and integrity manifests;
- local verification and clean-install testing.

## Excluded

- external or production deployment;
- canonical rule admission or receiver acceptance;
- inferred intent, autonomous actions, network access, or external mutation;
- a claim that production gate P03 or later gates have passed;
- compatibility claims for untested runtimes.

No separate approver is required for creating or downloading this scoped
artifact. Existing production authorization gates remain unchanged for any
broader release or deployment.
