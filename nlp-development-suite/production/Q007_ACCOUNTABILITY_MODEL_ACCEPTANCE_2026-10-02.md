# Q-007 accountability-model acceptance

## Source

On 2026-10-02, the user explicitly accepted the proposed Q-007 decision after
the applicable approval roles and evidence gates were stated.

## Accepted canon

For the bounded local downloadable release, the user is the product/canon and
release-scope authority. No separate human approver is required.

Technical, security/data, licensing, and reproducibility requirements remain
evidence gates that must pass. Passing tests is validation, not independent
attestation.

An operations approver is not applicable because no service or deployment is
authorized. A receiving-system approver is not applicable because no catalog
or sister-system integration is being accepted.

Any future deployment, network service, shared or multi-user operation, or
receiving-system integration requires a new authorization decision and
appropriately assigned roles.

## Scope

- the bounded local downloadable `nlp-offline-interpreter/0.1` release;
- product/canon and release-scope authority;
- technical, security/data, licensing, and reproducibility evidence gates;
- operations and receiving-system roles that are not applicable to this scope.

## Locked terms

- `user is product/canon and release-scope authority`;
- `no separate human approver for the bounded local release`;
- `evidence gates are not waived`;
- `validation is not independent attestation`;
- `deployment and integration require new authorization`.

## Not established by this acceptance

- independent technical, security, legal, or receiving-system attestation;
- deployment, hosted service, shared-user, or network authority;
- catalog or sister-system acceptance;
- production readiness before the applicable evidence gates pass.

## Version and migration

- Decision version: `Q-007/1`.
- Superseded values: the prior state was `UNKNOWN` with approver roles
  unassigned.
- Migration: if the release scope expands, identify the new external effects,
  assign the applicable roles, and obtain a new authorization before work
  crosses this boundary.
- Unresolved conflict: none within the bounded local release scope. External
  deployment and integration approvals remain outside scope.
