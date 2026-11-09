# Rollback runbook

## Current status

Generated template; not rehearsed. It is not a production recovery claim.

## Preconditions

Before any staged or production change, record:

- exact known-good application, data, schema, configuration, and dependency
  versions;
- immutable artifact and manifest hashes;
- verified backups and their storage/retention policy;
- changes since the baseline;
- state that can be reconstructed and state that cannot;
- forward and backward data-compatibility constraints;
- rollback operator, approver, trigger thresholds, and communication path.

## Procedure

1. Stop further rollout and freeze evidence.
2. Identify the exact failing deployment and affected scope.
3. Preserve logs, metrics, inputs, outputs, and state identifiers.
4. Determine whether rollback is safe for current data and schema state.
5. Restore the last accepted immutable application and configuration artifacts.
6. Restore or migrate data only through the accepted recovery procedure.
7. Re-run health, integrity, authorization, and semantic checks.
8. Confirm that monitoring has returned to the known-good envelope.
9. Record the rollback receipt and unresolved impact.
10. Open a diagnostic redux before resuming forward deployment.

## Unsafe rollback conditions

Rollback must stop for explicit review if it would discard accepted writes,
violate a data-retention obligation, reintroduce a known security issue, cross an
irreversible schema migration, lose provenance, or target an unverified backup.

## Rehearsal evidence required at P07

- isolated staging environment identity;
- initial and restored artifact hashes;
- backup creation and restore logs;
- semantic validation before and after restore;
- elapsed recovery time and data-loss window;
- injected failure and discriminator;
- deviations, unresolved issues, and reviewer decision.
