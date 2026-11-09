# Production acceptance checklist

An unchecked item is not a failure by itself; it means production acceptance is
not yet evidenced. Each checked item must link to evidence for the exact release
candidate.

## Scope and canon

- [x] Release capability and exclusions are accepted. Evidence:
  `P03_SCOPE_ACCEPTANCE_2026-10-01.md`, Q-001 through Q-007 records, and
  `PRODUCTION_PLAN_ACCEPTANCE_2026-10-02.md`.
- [x] Canon registry records contracts, versions, locked terms, and migrations.
  Evidence: `DECISION_LOG.md`.
- [x] All advisory material remains distinguishable from accepted canon.
  Evidence: Q-003 and Q-004 acceptance records.
- [ ] All unresolved conflicts have an owner and disposition.

## Build and artifacts

- [ ] Clean checkout builds in the supported environment.
- [ ] Direct and transitive dependencies are pinned and reviewed.
- [ ] Generated data is reproducible or its source receipt is retained.
- [ ] Artifact manifest and dependency inventory match the candidate.
- [ ] Licenses and redistribution obligations are satisfied.
- [ ] No credentials, private data, caches, or machine-local paths leaked.

## Behavior and integration

- [ ] Unit, negative, property, contract, and regression checks pass.
- [ ] Producer and consumer validate the same schemas and versions.
- [ ] Collisions, abstentions, conflicts, and unresolved regions remain visible.
- [ ] Proposal layers cannot authorize execution or mutation.
- [ ] External providers have bounded input/output and failure handling.

## Security, privacy, and operations

- [ ] Threat model and abuse cases are reviewed.
- [ ] Authentication, authorization, secrets, network, and audit controls pass.
- [x] Privacy, telemetry, retention, and redistribution policy is accepted.
  Evidence: `Q006_DATA_POLICY_ACCEPTANCE_2026-10-02.md`.
- [ ] Performance, capacity, compatibility, and accessibility targets pass.
- [ ] Monitoring, alerts, support ownership, and incident response are active.

## Recovery and release

- [ ] Backup restore and rollback have been rehearsed in staging.
- [ ] Migration and rollback are safe for current data and schemas.
- [ ] Release candidate is immutable, versioned, and independently verified.
- [ ] Applicable evidence gates pass and the user records the exact-candidate decision.
- [ ] Staged rollout thresholds and automatic stop conditions are configured.
- [ ] Post-deployment validation and evidence retention are complete.

## Final status

- [ ] Exact candidate accepted for production by named authority.

Until the final item is supported, report the status as development,
validation-required, blocked, or release-candidate—not production-ready.
