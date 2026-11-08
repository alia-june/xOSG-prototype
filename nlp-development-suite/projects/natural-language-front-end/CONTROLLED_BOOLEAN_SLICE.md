# Controlled Boolean English slice

The new `controlled_boolean.py` path is an explicitly restricted English
grammar for aPROMPT `ground-boolean/1.0`. It handles one sentence per nonblank
line, with lowercase ASCII `entity` and `property` identifiers:

```text
entity is property.
entity is not property.
entity is property and entity is property.
entity is property or entity is property.
If entity is property, then entity is property.
```

The documented mapping is `has_property(entity, property)`. `not`, `and`,
`or`, and `If ..., then ...` map to the corresponding aPROMPT Boolean operators;
implication is material implication. Repeated grounded atoms reuse one ID.
Input text and exact UTF-8 SHA-256 are retained; statement spans index Unicode
code points in the unchanged source text. A recognized sentence becomes a
`supplied` assertion with `adoption: null`, never an axiom. Unsupported sentences
become `unknown` unresolved statements and issues, which block preparation.

The generated [example meaning document](examples/controlled_boolean.meaning.json)
contains five assertions, three grounded atoms, zero issues, and zero adopted
axioms. Its SHA-256 is
`82E564F8542368DD9C608B8EE4ABFBEC63FC71A368A01939DB523FAA66D7C9E3`.
It passed the wheel's packaged JSON Schema, `decode_contract_json`, and
`validate_meaning`. A synthetic, in-memory `evaluate` preparation using the
installed catalog can be reviewed with `can_execute: false`; no approval,
runtime execution, or SafeAPI operation was performed. The example is newly
authored test text, not recovered content from the full prompt.

```powershell
.\.venv\Scripts\python.exe .\controlled_boolean.py --input .\examples\controlled_boolean.txt --output .\examples\new_controlled_boolean.meaning.json
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
```

An exact scan of the 1,196 fragments in the supplied full-prompt ledger found
**zero matches** to this controlled grammar. The full-prompt sister handoff
therefore remains unresolved. Its instructions and modal rules require
reviewed formalization, and aPROMPT's current Boolean compiler cannot encode
obligation or prohibition directly. The 26 local tests pass.
