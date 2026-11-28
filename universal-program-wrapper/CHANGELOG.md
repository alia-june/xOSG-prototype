# Changelog

## 0.1.0

- Extracted Universal Program Wrapper from the surrounding driver/safety/BitCore architecture.
- Added JSON control/invocation envelope.
- Added operation manifest and introspection.
- Added legacy CLI adapter with exact executable path, shell-disabled argv construction, bounded timeout, explicit environment inheritance, and raw result preservation.
- Added embedded native handler interface.
- Kept authority grants, safety policy, bitcode semantic verification, cataloging, and kernel behavior outside the unit.
