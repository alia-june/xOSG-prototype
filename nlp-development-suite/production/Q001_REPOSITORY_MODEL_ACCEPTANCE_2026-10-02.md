# Q-001 repository-model acceptance

## Source

On 2026-10-02, the user explicitly accepted the proposed Q-001 decision after
its scope and consequences were stated.

## Accepted canon

The suite-level monorepo is the canonical development source for
`nlp-offline-interpreter/0.1`. Component directories and historical manifests
retain their provenance.

## Scope

- development source, versioning, local validation, and release preparation;
- the current suite root and its component directories;
- preservation of the supplied historical `PACKAGE_MANIFEST.json` as a
  snapshot ledger rather than rewriting it to describe later work.

## Locked terms

- `suite-level monorepo`;
- `canonical development source`;
- `component provenance preserved`.

## Not established by this acceptance

- a canonical remote repository or hosting provider;
- remote CI authority or successful remote validation;
- deployment or production-operation authority;
- production readiness;
- permission to collapse component provenance or rewrite historical manifests.

## Version and migration

- Decision version: `Q-001/1`.
- Superseded values: none; the prior state was `UNKNOWN` with a generated,
  unaccepted proposal.
- Migration: use the suite root as the development versioning and release
  preparation boundary while retaining component paths and provenance.
- Unresolved conflict: the future canonical remote location remains unknown.
