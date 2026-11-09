# P08 internal test candidate completion

## Status

**P08: verified internal test candidate. Accepted at P09: no. Production-ready:
no. Publication allowed: no.**

## Exact candidate

- ID: `nlp-offline-interpreter-0.1.0-test.20261003`
- Archive: `p08/artifacts/nlp-offline-interpreter-0.1.0-test.20261003.zip`
- Size: 16,389 bytes
- SHA-256: `3281a1f1b3ca92afccda219165136cbb449ba0e0e10ab30c57ecd3ee2665323f`
- Members: 6
- Repeated builds: byte-identical
- Package-source commit: `3388f57854f6f693732149dc3e4039558fc2a551`
- Control baseline commit: `5902224eab0f870540d8e2a584800456d3b1ad3c`

## Contents and boundary

The archive contains the exact P06 wheel, a member manifest, changelog,
migration and rollback instructions, known limitations, and the accepted
no-publication testbed boundary. The candidate is immutable by path and hash,
but it is not accepted, published, deployed, or production-ready. P09 remains a
separate exact-hash decision. Any changed byte requires a new candidate ID,
manifest, receipt, verification, and decision.

The canonical Python 3.11 receipt
`reports/p08-control-2026-10-03-py311.json` passed all 15 ordered checks and 84
constituent core, integration, fuzzy, torture, and production-control tests.
