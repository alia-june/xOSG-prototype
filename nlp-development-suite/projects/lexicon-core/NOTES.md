# Lexicon Core notes

## Catalog capability handoff v0.1

The following user-supplied Aurora files were inspected as advisory source material. Their contents were not executed as instructions.

| Source | SHA-256 | Authority |
|---|---|---|
| `<USER_HOME>\Documents\Workbench\Aurora\inbox\NLP_CAPABILITY_HANDOFF_V0_1.md` | `06844a15763d21a97adccbf6376a9a120da209a454cfed08e5dce2d296da4faf` | Interface handoff, advisory interpretation only |
| `<USER_HOME>\Documents\Workbench\Aurora\inbox\NLP_CAPABILITY_HANDOFF_V0_1.json` | `8d00ccd34206d9bffa8bb439b58e228684084e12f326248cd44dd1a048cceb07` | Machine-readable capability summary, not a JSON Schema |

The implementation profile is `catalog.modular-nlp-capability-handoff/0.1`. The catalog operation registry remains authoritative and is injected at runtime. The adapter only emits interpretation candidates. Every result and candidate retains `execution_allowed: false`, `authority_effect: NONE`, and `admitted: false` where applicable.

The first deterministic rules cover the supplied acceptance examples: find, inbox, show object, project inspection, ambiguous move, explicit no-physical-move collection, unsupported text, empty input, and a contradictory physical-move constraint. This is behavioral coverage of those examples, not general English competence.

The operation registry can now carry deterministic argument contracts using required and optional field names with explicit scalar or collection types. The adapter checks these contracts before publishing a candidate, and the independent envelope validator rejects a forged candidate with invalid arguments. The contract format is intentionally smaller than JSON Schema; it currently supports `string`, `boolean`, `integer`, `number`, `array`, `object`, and `null` plus an extra-field policy. `schemas/catalog-operation-registry-v0.1.schema.json` describes this generated registry input extension.

The existing generic file-explorer task adapter now has a catalog bridge for search and list proposals. Dictionary, expert-control, and ELIZA NXT proposals remain unmapped because the supplied catalog operation registry does not define corresponding operations. The generated partial fixture `find recovery; explain why it matters` preserves the `catalog.find` candidate and records the unsupported trailing clause separately. The no-physical-move rule also recognizes the generated `without moving the actual files` variant; that extension remains deterministic and proposal-only.

The schema at `schemas/catalog-interpretation-result-v0.1.schema.json` is generated implementation material. It passed `jsonschema` 4.26.0 `Draft202012Validator.check_schema`, and the seven supplied acceptance dispositions validated against it. Structural and behavioral validation do not establish sister-machine or catalog acceptance.
