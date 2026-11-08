# Decision log

Only explicitly accepted entries become canon. Proposed entries remain generated
planning material.

## Recorded boundaries

| ID | State | Decision | Basis |
|---|---|---|---|
| D-001 | SOURCE | Preserve the original export manifest as the historical snapshot ledger. | `PACKAGE_MANIFEST.json`, `README_FIRST.md` |
| D-002 | SOURCE | NLP and catalog outputs remain non-authoritative proposals. | Packaged contracts and project documentation |
| D-003 | DERIVED | Add production controls outside the historical manifest rather than rewriting it. | Maintains provenance between supplied snapshot and new work |
| D-004 | GENERATED_SYNTHESIS | Use the ordered P00–P11 lifecycle in `production_plan.json`. | User request for methodical ordered production work |

## Decisions required before P03 can pass

| ID | State | Required decision | Why it matters |
|---|---|---|---|
| Q-001 | ACCEPTED CANON FOR DEVELOPMENT | Suite-level monorepo is the canonical development source; canonical remote remains unresolved | Determines versioning, local CI preparation, releases, and ownership |
| Q-002 | ACCEPTED CANON FOR DEVELOPMENT | Generic `nlp-offline-interpreter/0.1` development scope and stated exclusions | Direct user acceptance recorded in `P03_SCOPE_ACCEPTANCE_2026-10-01.md`; not production approval |
| Q-003 | ACCEPTED CANON FOR DEVELOPMENT | Catalog v0.1 is advisory; a supplied versioned receiving-system registry remains authoritative | Enables compatibility work without claiming receiving-system acceptance |
| Q-004 | ACCEPTED CANON FOR DEVELOPMENT | Unavailable sister schemas and compatibility claims are excluded until supplied, assessed, and separately accepted | Preserves unknowns without inventing external contracts |
| Q-005 | ACCEPTED CANON FOR DEVELOPMENT | Local offline single-user process; Python 3.11 canonical release build; newer Python conditional on tests; Windows validated first; no service claim | Bounds packaging and operating claims without asserting deployment readiness |
| Q-006 | ACCEPTED CANON FOR DEVELOPMENT | Packaged OEWN 2025 only with verified license/attribution; no omitted-corpus redistribution, telemetry, transmission, or automatic input retention | Establishes the policy while retaining release-candidate compliance review |
| Q-007 | ACCEPTED CANON FOR DEVELOPMENT | User is product/canon and release-scope authority for the bounded local release; no separate human approver; evidence gates remain; operations and receiver roles are not applicable | Defines accountability without treating tests as independent attestation |
| TESTBED-001 | ACCEPTED CANON FOR DEVELOPMENT | Current artifacts are internal testbed evidence and are not being published or externally redistributed | Defers distribution-license completion without weakening the future publication gate |

## P03 proposal dispositions

These values originated as proposals in `P03_AUTHORIZATION_PACKET.md`. Their
current dispositions are recorded below; acceptance remains bounded to the
stated scope and does not grant deployment authority.

| ID | Proposed value | Status |
|---|---|---|
| Q-001 | Suite-level monorepo retaining component directories and provenance | Accepted for development on 2026-10-02; no remote, deployment, or production effect |
| Q-002 | `nlp-offline-interpreter/0.1`: generic local library and plan-only CLI | Accepted for bounded development |
| Q-003 | Catalog v0.1 remains an advisory compatibility profile | Accepted boundary on 2026-10-02; no receiving-system, execution, mutation, or production effect |
| Q-004 | Sister schemas excluded until supplied and accepted | Accepted boundary on 2026-10-02; absence remains UNKNOWN |
| Q-005 | Local single-user Python 3.11+ process; Windows validated first | Accepted with Python 3.11 canonical build on 2026-10-02; no service, availability, or production effect |
| Q-006 | Included OEWN only; no telemetry or omitted-corpus redistribution | Accepted on 2026-10-02 with license/attribution verification and no automatic input retention |
| Q-007 | User authority for bounded local release; evidence gates retained; external roles not applicable | Accepted on 2026-10-02; scope expansion requires new authorization |

## Acceptance template

When a decision is made, append a new entry; do not silently rewrite an older
entry. Record the decision ID, accepted value, authority, acceptance date,
version, scope, locked terms, superseded values, migration note, and unresolved
conflicts.

## Accepted decision records

### TESTBED-001/1 — No-publication operating scope

- **State:** ACCEPTED CANON FOR DEVELOPMENT.
- **Accepted value:** The suite remains an internal test bed. Current wheels,
  reports, manifests, and test artifacts are not being published or externally
  redistributed.
- **Authority:** User, by explicit clarification in the active session.
- **Acceptance date:** 2026-10-02.
- **Version:** `TESTBED-001/1`.
- **Scope:** Current P06 verification and subsequent internal validation.
- **Locked terms:** `internal test bed`, `not being published`, `no external
  redistribution`, and `license review reopens before publication`.
- **Superseded values:** The earlier inference that the locally downloadable
  development wheel was already crossing a publication gate.
- **Migration:** Treat licensing as inventoried risk during internal testing;
  require exact-artifact terms, notices, and attribution before publication.
- **Unresolved conflicts:** First-party distribution terms and third-party
  redistribution obligations remain unresolved because no distribution is
  currently authorized.
- **Evidence:** `TESTBED_SCOPE_ACCEPTANCE_2026-10-02.md`.

### Q-001/1 — Repository model

- **State:** ACCEPTED CANON FOR DEVELOPMENT
- **Accepted value:** The suite-level monorepo is the canonical development
  source for `nlp-offline-interpreter/0.1`; component directories and
  historical manifests retain their provenance.
- **Authority:** User, by explicit acceptance in the active session.
- **Acceptance date:** 2026-10-02.
- **Version:** `Q-001/1`.
- **Scope:** Development source, versioning, local validation, and release
  preparation.
- **Locked terms:** `suite-level monorepo`, `canonical development source`,
  and `component provenance preserved`.
- **Superseded values:** None. The earlier state was UNKNOWN and the earlier
  monorepo wording was generated but unaccepted.
- **Migration:** Treat the suite root as the development boundary while
  retaining component paths and the historical `PACKAGE_MANIFEST.json`.
- **Unresolved conflicts:** No canonical remote repository has been selected.
  This acceptance does not authorize remote CI, deployment, or production use.
- **Evidence:** `Q001_REPOSITORY_MODEL_ACCEPTANCE_2026-10-02.md`.

### Q-003/1 — Catalog authority

- **State:** ACCEPTED CANON FOR DEVELOPMENT
- **Accepted value:** Catalog v0.1 is an advisory development compatibility
  profile. A supplied, versioned receiving-system command registry remains
  authoritative.
- **Authority:** User, by explicit acceptance in the active session.
- **Acceptance date:** 2026-10-02.
- **Version:** `Q-003/1`.
- **Scope:** Compatibility development, local validation, and proposal-only
  operation mapping.
- **Locked terms:** `advisory development compatibility profile`,
  `receiving-system registry remains authoritative`, `unknown operations are
  rejected`, and `no execution or catalog mutation authority`.
- **Superseded values:** None. The earlier state was UNKNOWN and the earlier
  advisory-profile wording was generated but unaccepted.
- **Migration:** Retain catalog v0.1 as a development fixture and require a
  supplied versioned registry at an actual receiving-system boundary.
- **Unresolved conflicts:** No receiving catalog has supplied or accepted its
  canonical operation registry and argument contracts.
- **Evidence:** `Q003_CATALOG_AUTHORITY_ACCEPTANCE_2026-10-02.md`.

### Q-004/1 — Sister-schema authority

- **State:** ACCEPTED CANON FOR DEVELOPMENT
- **Accepted value:** No absent or externally referenced sister schema is
  canonical for this release. Unavailable parse-tree, logic, transition,
  acceptance, and authority schemas and compatibility claims are excluded.
- **Authority:** User, by explicit acceptance in the active session.
- **Acceptance date:** 2026-10-02.
- **Version:** `Q-004/1`.
- **Scope:** The `nlp-offline-interpreter/0.1` release contract, external
  sister schemas, and the boundary around the interpreter's own versioned
  internal output schema.
- **Locked terms:** `unavailable sister schemas are excluded`, `absence remains
  UNKNOWN`, `no unsupported compatibility claim`, and `later integration
  requires separate acceptance`.
- **Superseded values:** None. The earlier state was UNKNOWN and the earlier
  exclusion wording was generated but unaccepted.
- **Migration:** A later supplied schema must be inventoried, compared for
  conflict, given a reversible migration plan, validated, and separately
  accepted before integration.
- **Unresolved conflicts:** Canonical sister schemas have not been supplied.
- **Evidence:** `Q004_SISTER_SCHEMA_AUTHORITY_ACCEPTANCE_2026-10-02.md`.

### Q-005/1 — Runtime and operating model

- **State:** ACCEPTED CANON FOR DEVELOPMENT
- **Accepted value:** The first release is a local, offline, single-user Python
  process. Python 3.11 is the canonical release-build runtime; newer Python
  support is conditional on passing tests. Windows is validated first, and no
  service or availability claim is made.
- **Authority:** User, by explicit acceptance in the active session.
- **Acceptance date:** 2026-10-02.
- **Version:** `Q-005/1`.
- **Scope:** Release builds, Python compatibility claims, first validated host
  family, user model, and service exclusions.
- **Locked terms:** `Python 3.11 canonical release-build runtime`, `local
  offline single-user process`, `Windows validated first`, `newer Python
  support requires passing tests`, and `no service or availability claim`.
- **Superseded values:** None. The earlier state was UNKNOWN and the earlier
  runtime wording was generated but unaccepted.
- **Migration:** Construct canonical release artifacts with Python 3.11; test
  newer runtimes without treating their artifacts as canonical.
- **Unresolved conflicts:** Additional operating-system targets and any future
  service-level requirements remain unspecified.
- **Evidence:** `Q005_RUNTIME_OPERATING_MODEL_ACCEPTANCE_2026-10-02.md`.

### Q-006/1 — Data, privacy, and redistribution

- **State:** ACCEPTED CANON FOR DEVELOPMENT
- **Accepted value:** Only packaged OEWN 2025 candidate data may be included,
  subject to verified license and attribution. Omitted corpora are not
  redistributed; runtime operation has no telemetry, network transmission, or
  automatic input retention.
- **Authority:** User, by explicit acceptance in the active session.
- **Acceptance date:** 2026-10-02.
- **Version:** `Q-006/1`.
- **Scope:** Packaged lexical data, omitted corpora, telemetry, transmission,
  retention, and release-candidate license checks.
- **Locked terms:** `packaged OEWN 2025 candidate data only`, `license and
  attribution must be preserved and verified`, `no omitted-corpus
  redistribution`, `no telemetry, analytics, or background collection`, and
  `no automatic input retention`.
- **Superseded values:** None. The earlier state was UNKNOWN and the earlier
  data-policy wording was generated but unaccepted.
- **Migration:** Any new data source, persistence, telemetry, or network
  behavior requires separate assessment, testing, and explicit acceptance.
- **Unresolved conflicts:** Legal/license compliance of the exact release
  candidate remains to be verified before distribution.
- **Evidence:** `Q006_DATA_POLICY_ACCEPTANCE_2026-10-02.md`.

### Q-007/1 — Approval and accountability model

- **State:** ACCEPTED CANON FOR DEVELOPMENT
- **Accepted value:** The user is the product/canon and release-scope
  authority for the bounded local downloadable release. No separate human
  approver is required. Evidence gates remain mandatory; operations and
  receiving-system approvers are not applicable to this scope.
- **Authority:** User, by explicit acceptance in the active session.
- **Acceptance date:** 2026-10-02.
- **Version:** `Q-007/1`.
- **Scope:** The bounded local downloadable `nlp-offline-interpreter/0.1`
  release only.
- **Locked terms:** `user is product/canon and release-scope authority`, `no
  separate human approver for the bounded local release`, `evidence gates are
  not waived`, `validation is not independent attestation`, and `deployment
  and integration require new authorization`.
- **Superseded values:** The earlier state was UNKNOWN with roles unassigned.
- **Migration:** Scope expansion requires identification of new effects,
  assignment of applicable roles, and new authorization before work crosses
  the boundary.
- **Unresolved conflicts:** None within the bounded local release scope.
  External deployment and integration approvals remain outside scope.
- **Evidence:** `Q007_ACCOUNTABILITY_MODEL_ACCEPTANCE_2026-10-02.md`.

### PLAN-001/1 — Bounded production workflow

- **State:** ACCEPTED CANON
- **Accepted value:** P00 through P09 govern the bounded local downloadable
  release. P09 is the user's exact-hash release decision after mandatory
  evidence gates pass. P10 deployment and P11 retirement remain blocked.
- **Authority:** User, by explicit acceptance in the active session.
- **Acceptance date:** 2026-10-02.
- **Version:** `production-plan/1-bounded-local-release`.
- **Scope:** Ordered preparation, verification, validation, construction, and
  acceptance of the local `nlp-offline-interpreter/0.1` artifact.
- **Locked terms:** `P00-P09 local release workflow`, `exact-hash user
  acceptance`, `evidence gates are mandatory`, and `P10-P11 require new
  authorization`.
- **Superseded values:** `generated-plan-unaccepted`.
- **Migration:** P03 changes to verified and P04 changes to in progress. Later
  phases retain their dependency gates.
- **Unresolved conflicts:** No deployment target or deployment authority exists;
  these are outside the accepted scope.
- **Evidence:** `PRODUCTION_PLAN_ACCEPTANCE_2026-10-02.md`.

## Non-canonical research-track status records

These entries record evidence, inference, and generated planning for the
generative relational lexicon. They do not amend the accepted P08 candidate,
admit lexical canon, or authorize publication or deployment.

### RLX-STATUS-001 — Post-repair research baseline

- **State:** DERIVED.
- **Recorded value:** Parser version `roget-structure-pilot/4` recognizes 1,043
  stable Roget head identifiers and emits 102,235 source-spanned historical
  memberships. The complete research test suite passes 60 tests, and seven
  dependency-ordered receipts were byte-stable across repeated generation.
- **Method:** Compare the pinned pre-repair commit `5d670d0` with commit
  `bd3109a`; run the parser-repair measurer, complete test discovery, source-map
  validator, mining-gap analyzer, and repeated generation pipeline.
- **Recorded date:** 2026-10-06.
- **Scope:** Internal generative-relational-lexicon test scaffold only.
- **Limits:** Structural extraction and reproducibility do not establish
  lexical validity, semantic identity, dictionary completeness, independent
  attestation, production readiness, or publication authority.
- **Evidence:**
  `development/generative-relational-lexicon/PARSER_REPAIR_DECISION.json` and
  `development/generative-relational-lexicon/pilot/parser-repair/PARSER_REPAIR_DELTA_REPORT.json`.

### RLX-ASSESSMENT-001 — Current approach viability

- **State:** INFERENCE.
- **Assessment:** The approach is presently viable for a provenance-bearing
  historical evidence graph, discrepancy mapper, and lexical-reconstruction
  testbed. It is not yet sufficient evidence for a comprehensive modern
  dictionary or a complete word universe.
- **Basis:** 59,636 historical normalized forms yield 28,271 exact modern lemma
  candidates and 1,145 additional layered surface candidates; 30,220 remain
  unresolved. The strict initial mining policy identifies five eligible sources
  but only one currently mining-ready unit.
- **Recorded date:** 2026-10-06.
- **Limits:** Counts measure surface and structural coverage rather than sense
  accuracy. No population-level semantic precision or recall has been proven.
- **Next discriminator:** Build and independently review a bounded sense-scoped
  aboutness evaluation set before scaling semantic synthesis.

### RLX-PLAN-001 — Ordered next course of action

- **State:** GENERATED_SYNTHESIS.
- **Plan:** Follow the ordered research gates documented in
  `development/generative-relational-lexicon/STATUS_AND_NEXT_ACTIONS_2026-10-06.md`:
  freeze the post-repair baseline; specify sense-scoped aboutness; construct a
  reviewed evaluation set; implement evidence-only candidate generation;
  measure accuracy and abstention; add permissive sources one adapter at a
  time; admit only reviewed sense relations; then construct a new candidate
  distinct from P08.
- **Recorded date:** 2026-10-06.
- **Authority effect:** Planning and internal test work only. Each ingestion,
  canon-admission, publication, or deployment transition retains its own gate.

### RLX-STATUS-002 — Semantic baseline and aboutness contract

- **State:** DERIVED.
- **Recorded value:** RLX-N01 pins eight exact post-repair evidence inputs to
  commit `b365c25110a7770df89642f53b0153986221b589`. RLX-N02 defines a Draft
  2020-12 sense-aboutness candidate contract with eight facet types, scoped
  evidence references, ambiguity, conflict, and abstention.
- **Method:** Verify current bytes against committed Git blobs; meta-validate the
  schema with `jsonschema==4.26.0`; run three valid and four invalid fixtures;
  run ten focused contract tests.
- **Recorded date:** 2026-10-06.
- **Scope:** Test schema and semantic-evaluation baseline only.
- **Limits:** No evaluation sample was selected, no candidate meaning was
  generated, no reviewer decision occurred, and no lexical canon was admitted.
- **Evidence:** `SENSE_ABOUTNESS_BASELINE_DECISION.json` and
  `pilot/sense-aboutness/SENSE_ABOUTNESS_CONTRACT_RECEIPT.json`.
- **Next gate:** RLX-N03 deterministic reviewed-evaluation package.

### RLX-STATUS-003 — Blank semantic review package

- **State:** DERIVED.
- **Recorded value:** The pinned 59,636-record historical-form population has
  853 observed combinations across match layer, historical head dispersion,
  POS signature, source-label presence, modern sense-count bucket, surface
  collision bucket, and unresolved-shape class. One SHA-256-ranked record per
  observed stratum forms the blank review package.
- **Method:** Join only structural discrepancy, normalization, unresolved-shape,
  and historical-membership evidence; attach pinned raw Roget source spans;
  initialize all seven reviewer fields to null; verify selection hashes and
  exact stratum uniqueness.
- **Recorded date:** 2026-10-06.
- **Scope:** Deterministic structural coverage set for internal review.
- **Limits:** The 853 records are not population-weighted. No reviewer has
  assigned a sense, aboutness facet, abstention, definition, or lexical-validity
  judgment. This is not yet a gold set and provides no semantic accuracy result.
- **Evidence:** `SENSE_REVIEW_SAMPLE_DECISION.json` and
  `pilot/sense-aboutness/review-sample/SENSE_REVIEW_SAMPLE_RECEIPT.json`.
- **Next gate:** Define the review protocol and complete a bounded calibration
  tranche before broad review or candidate generation.

### RLX-STATUS-004 — Review protocol boundary

- **State:** GENERATED_SYNTHESIS.
- **Recorded value:** A protocol now separates sample construction from
  independent reviewer judgment, allows explicit abstention and conflict,
  preserves disagreement and adjudication, and defines stop conditions for
  missing or contradictory evidence.
- **Recorded date:** 2026-10-06.
- **Scope:** The 853-record blank semantic review package only.
- **Limits:** No calibration tranche has been selected or reviewed. The
  protocol is not a semantic result, reviewer acceptance, or canon decision.
- **Evidence:** `SENSE_REVIEW_PROTOCOL_2026-10-06.md`.
- **Next gate:** Build the deterministic blank dual-review calibration worksheet.

### RLX-STATUS-005 — Blank dual-review calibration worksheet

- **State:** DERIVED TEST PACKAGE.
- **Recorded value:** A deterministic greedy selector chose 34 records from the
  frozen 853-record blank package and covered all 57 observed calibration atoms
  across the seven review dimensions. Each record has two independent blank
  reviewer copies and a blank adjudication object.
- **Method:** Rank candidates by uncovered-atom gain, then deterministic
  selection rank and normalized term; preserve the attached raw source spans;
  leave all reviewer and adjudication fields null.
- **Recorded date:** 2026-10-06.
- **Scope:** Internal calibration worksheet only; no semantic or production
  authority.
- **Limits:** No reviewer has entered a disposition, sense distinction,
  agreement result, adjudication, definition, or canon decision.
- **Evidence:** `SENSE_CALIBRATION_DECISION.json`,
  `pilot/sense-aboutness/calibration/SENSE_CALIBRATION_RECEIPT.json`, and
  `pilot/sense-aboutness/calibration/blank-dual-review-records.jsonl.gz`.
- **Next gate:** Complete independent review of both copies and preserve any
  disagreement before adjudication or candidate generation.

### RLX-STATUS-006 — Review-intake validation control

- **State:** VERIFIED TEST CONTROL.
- **Recorded value:** The review-intake validator checks that calibration
  records remain attached to the frozen source package, reviewer fields use the
  allowed statuses, and blank records cannot be presented as reviewed.
- **Recorded date:** 2026-10-06.
- **Scope:** Internal calibration review intake only.
- **Limits:** It does not assign senses, validate semantic truth, adjudicate
  disagreements, admit canon, or authorize production/publication.
- **Evidence:** `validate_sense_calibration_review.py` and
  `tests/test_sense_calibration_review.py`; the current package returns
  `BLANK_NOT_REVIEWED`.
- **Next gate:** Complete and preserve two independent reviewer copies, then
  run the validator in `--require-reviewed` mode.

### RLX-STATUS-007 — Independent reviewer packet export

- **State:** DERIVED TEST PACKAGE.
- **Recorded value:** The 34-record calibration tranche is exported as two
  deterministic packets. Each retains the same source-bearing evidence but
  exposes only its assigned reviewer slot; cross-reviewer judgments and
  adjudication are excluded.
- **Recorded date:** 2026-10-06.
- **Scope:** Internal independent-review handoff only.
- **Limits:** Both packets are blank. Export does not assign meanings, measure
  agreement, adjudicate, admit canon, or authorize production/publication.
- **Evidence:** `export_sense_reviewer_packets.py`,
  `pilot/sense-aboutness/review-packets/SENSE_REVIEW_PACKET_MANIFEST.json`, and
  `tests/test_sense_reviewer_packets.py`.
- **Next gate:** Deliver packets to independent reviewers and preserve their
  completed copies before adjudication.
