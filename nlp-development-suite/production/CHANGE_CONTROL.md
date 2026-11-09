# Change control

## Admission rule

A change may enter implementation only when it has:

1. a stable change identifier;
2. an identifiable source requirement or explicitly generated proposal;
3. a truth state and authority owner;
4. a bounded target and explicit exclusions;
5. resolved or recorded canon conflicts;
6. acceptance criteria that distinguish success from failure;
7. a rollback or an explicitly accepted irreversible effect;
8. tests appropriate to its risk;
9. a coverage-ledger and risk-register update;
10. review evidence tied to the exact changed version.

## Change record template

| Field | Required content |
|---|---|
| Change ID | Stable `CHG-...` identifier |
| Title | Specific behavior or artifact being changed |
| Truth state | Source, accepted canon, derived, inference, unknown, or generated synthesis |
| Requirement source | Exact file, issue, or accepted decision |
| Scope | Files, components, users, and environments affected |
| Exclusions | Work intentionally not included |
| Dependencies | Prior gates, contracts, datasets, and approvals |
| Risk | Linked risk IDs and new risks |
| Validation | Unit, contract, integration, security, performance, recovery |
| Rollback | Baseline, procedure, data implications, and unsafe conditions |
| Decision | Proposed, accepted, rejected, superseded, or deployed |
| Evidence | Commit, artifact hash, reports, reviewers, and date |

## Working rules

- Do not edit `PACKAGE_MANIFEST.json` to make new work resemble the historical
  export. Generate a new versioned release manifest at P08.
- Do not silently change advisory contracts or accepted canon. Add a versioned
  decision and migration note.
- Preserve collisions, unresolved spans, and failed evidence.
- Do not add execution or mutation authority to a proposal layer.
- Do not mix dependency upgrades with unrelated behavior changes.
- Reproduce a failure before correcting its explanation or implementation.
- Refuse release artifacts that overwrite an existing path.

## Required validation depth

| Risk | Minimum evidence |
|---|---|
| Low documentation-only | Link and structural checks |
| Local deterministic behavior | Unit and negative regression tests |
| Cross-component contract | Schema plus producer and consumer tests |
| Filesystem or data mutation | Confinement, idempotency, backup, restore, rollback |
| Network, authentication, or secrets | Threat model, security review, adversarial tests |
| Bounded local release | Full P06–P09 evidence and user acceptance of the exact candidate hash |
| Deployment or service | New authorization plus applicable P10 operational and independent evidence |
