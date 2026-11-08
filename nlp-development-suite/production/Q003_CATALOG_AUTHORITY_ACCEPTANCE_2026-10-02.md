# Q-003 catalog-authority acceptance

## Source

On 2026-10-02, the user explicitly accepted the proposed Q-003 decision after
its scope and authority limits were stated.

## Accepted canon

Catalog v0.1 is an advisory development compatibility profile. The NLP may
generate non-executing proposals using its documented operation names and
argument shapes, but the profile is not receiving-system canon. An actual
catalog must supply its current versioned command registry, which remains
authoritative.

## Scope

- compatibility development and local validation;
- proposal-only mappings to documented catalog operation names;
- validation against a supplied, versioned receiving-system registry before
  any candidate can be accepted downstream.

## Locked terms

- `advisory development compatibility profile`;
- `receiving-system registry remains authoritative`;
- `unknown operations are rejected`;
- `no execution or catalog mutation authority`.

## Not established by this acceptance

- receiving-system acceptance of catalog v0.1;
- authority to hard-code a competing command ontology;
- execution, admission, or catalog-state mutation authority;
- approval of any future or unavailable registry;
- production readiness or deployment authority.

## Version and migration

- Decision version: `Q-003/1`.
- Superseded values: none; the prior state was `UNKNOWN` with a generated,
  unaccepted proposal.
- Migration: retain the v0.1 profile as a development fixture and require a
  supplied versioned registry at an actual receiving-system boundary.
- Unresolved conflict: no receiving catalog has supplied or accepted its
  canonical operation registry and argument contracts.
