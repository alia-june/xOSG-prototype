# P04 local staging report — 2026-10-02

## Status

`VERIFIED_LOCAL_PRE_STAGE`

P04 engineering evidence is complete for CPython 3.11–3.14 on this Windows
host. The production phase remains `not_started` because P03 is still blocked.
No remote repository, remote CI result, deployment, receiver acceptance, or
production-readiness claim is included.

## Repository evidence

- Local suite-level monorepo initialized with no remote.
- Initial staging commit: `5eb56e0c646326304e180f0b93d025760a36b310`.
- Exact-byte correction commit: `d5e8f7d`.
- Multi-runtime staging commit tested from a detached checkout: `017a961`.
- All 1,306 historical manifest members verified from the detached checkout.
- The verified OEWN database is retained even though its historical component
  `.gitignore` excludes `.wn_data`.

## Runtime matrix

| Runtime | Clean-checkout result | Repeated wheel SHA-256 |
|---|---|---|
| CPython 3.11.9 | Passed | `f624914598b98115dda294d0e34bee3e722326dcecfad2082ca437c957f138e2` |
| CPython 3.12.10 | Passed | `f624914598b98115dda294d0e34bee3e722326dcecfad2082ca437c957f138e2` |
| CPython 3.13.15 | Passed | `f624914598b98115dda294d0e34bee3e722326dcecfad2082ca437c957f138e2` |
| CPython 3.14.4 | Passed | `a3ef932ef0832716a17628d5318ac36175796fa2e2d80950079b6d149b59d9b3` |

Each run created a fresh environment, installed 15 exact dependencies from the
18-wheel offline wheelhouse with hash enforcement, ran the complete ordered
baseline, and built the successor twice. Repeated builds were byte-identical
within each runtime.

The Python 3.14 wheel differs byte-for-byte from the 3.11–3.13 wheel even though
both are `py3-none-any` builds. Cross-runtime byte identity is therefore not
claimed; P08 must select one canonical build runtime or normalize and prove the
archive construction.

## CI and security controls

- `.github/workflows/ci.yml` expresses the four-version Windows matrix.
- It has read-only repository permission, uses no secrets, and has no deployment
  step.
- The local commands represented by the workflow passed; no remote workflow run
  has been observed.
- The bounded high-confidence secret scan passed. This is not a full security
  audit.

## Remaining boundary

Formal P04 completion still requires accepted P03 decisions and remote CI
evidence if GitHub Actions is retained. Non-Windows support, independent-host
reproduction, raw-corpus reconstruction, and production security/performance
validation remain outside this report.
