# System boundaries

## Component map

| Component | Present evidence | Current authority | Execution boundary |
|---|---|---|---|
| Lexicon Core | Source, schemas, examples, 22 reproduced tests | Generated implementation | Proposal generation only |
| Natural Language front end | Filesystem snapshot, OEWN data, 54 reproduced tests | Generated implementation plus historical source | Registered read-only adapters only; secondary layers do not execute |
| Lexicon Atlas | Static site, generated shards, validation script | Generated application snapshot | Browser/desktop behavior not production-validated in this intake |
| File Atlas | Static prototype and verifier | Generated prototype | File-interface behavior is not production authority |
| Scaffold Walker | Byte-preserved supplied HTML | User-supplied artifact | No accepted import/export contract is present |
| Aurora capability handoff | Markdown and JSON summary | Advisory interface handoff | No runtime mutation authority |
| Shared registry | Metadata and external source references | Source inventory metadata | Does not merge source authority or admit lexical claims |
| NLP Offline Interpreter successor | Separate generic core and staged adapters | Accepted bounded local-release implementation through P05 | No execution interface; production-ready, deployment, and receiver acceptance remain absent |

## Data boundary

The export includes generated Lexicon Atlas browser shards and a verified OEWN
database. Complete raw Wiktionary, GCIDE source archive, CMUdict, IPA Dict,
UniMorph, ODict, and StarDict inbox data are external. Local availability does
not establish that a clean build machine or production host can reproduce them.

## Authority boundary

Parser, lexical, routing, catalog, expert-control, ELIZA, and synthesis outputs
are candidates or proposals. They do not establish truth, canon admission,
operation authorization, filesystem mutation authority, or deployment approval.
The receiving registry and its accepted policy layer remain authoritative.

## Environment boundary

The supplied export omits virtual environments, Git databases, credentials,
tokens, transient caches, and most raw datasets. P04 added a hash-locked
offline wheelhouse and verified the complete baseline on canonical Python 3.11
from a clean Git commit on Windows AMD64. This remains local staging evidence,
not production-host, remote-CI, or cross-platform readiness.

## Remaining unknowns and deferred authority

- canonical remote repository location, if a remote is later required;
- exact-candidate license and attribution compliance;
- catalog and sister-system acceptance, both excluded from the bounded release;
- security, performance, accessibility, recovery, and compatibility thresholds;
- exact release-candidate identity and user acceptance at P09;
- any network service, shared-user, deployment, operations, or retirement model.
