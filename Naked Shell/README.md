# Naked Shell

Naked Shell is the xOSG natural-language command-line universal shell.

Its accepted purpose is to make command-line work accessible through natural
language without hiding the commands, authority, effects, or recovery path that
govern execution.

Current truth state: project identity and xOSG membership accepted. No shell
implementation, parser, command grammar, execution model, platform adapter, or
security authority is claimed by this folder yet.

## NLP development relationship — candidate interface

[NLP Development Suite](../nlp-development-suite/README.md) provides a
separate, code-only research prototype for controlled natural-language
interpretation, source-preserving lexical processing, bounded command parsing,
and explicit unresolved regions. Its proposed command/interpretation outputs
are **non-executing** and do not confer shell authority.

For future Naked Shell work, review:

- [Suite overview and evidence boundaries](../nlp-development-suite/README.md)
- [Development continuation and open contract work](../nlp-development-suite/CONTINUATION.md)
- [Production status and evidence requirements](../nlp-development-suite/PRODUCTION.md)

**Relationship:** a potential interpretation-side component/reference for the
Naked Shell design. This is a cross-project navigation and research link,
**not** an implemented adapter, an accepted parser binding, a shell command
grammar, an execution bridge, or permission to perform any effect.
Before integration, define the receiving shell contract, explicit candidate
mapping, provenance, failure and ambiguity handling, external authority
checks, and an independently admitted execution boundary.

Original software published here continues under the repository MIT License
unless an individual file carries a different SPDX license expression.
