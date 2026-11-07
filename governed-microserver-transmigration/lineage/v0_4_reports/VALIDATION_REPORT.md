# Governed Microserver Transmigration v0.4.0 — Executed Validation

**Date:** 2026-11-06  
**Disposition:** `CANDIDATE_ONLY / NOT_ADMITTED / NOT_PUBLISHED`  
**Test host:** Debian GNU/Linux 13, x86-64, kernel 6.18.57, Python 3.13.5, jsonschema 4.26.0, util-linux 2.41.5.

## Recorded results

| Check | Recorded result | Evidence |
|---|---|---|
| Full regression + security suite | **36 tests passed, 0 failed, 0 errors** | `FULL_TEST_RESULTS.txt`; `FULL_TEST_EXIT.txt` (`0`), elapsed 74.227 s |
| Independent-checker parity addition (written after the full-suite process started) | **1 separate test passed** | Invoked `python -m unittest tests.test_governed_v0_4.IndependentAuditTests.test_independent_checker_matches_source_corpus -v`; compares 19 source test manifests |
| Preserved source checker byte identity | **matched v0.3 source hash** | `source_witness/check_manifest_v0_2.py` SHA-256 `c45a747ccca6107cdbc83ad692fc2f984e78502b93ae653b44e68d16d1a402e1` |
| Preserved manifest schema byte identity | **matched v0.3 schema hash** | `contracts/manifest_v0_2.schema.json` SHA-256 `901e4572faf66153060c9e01f2b8533faaa3be43fb7963ebf3fda2f44f536afe` |
| Linux kernel filesystem boundary probe | **write to existing protected test file denied** | `test_kernel_denies_writes_remount_and_separates_network` |
| Linux tmpfs probe | **file creation under `/dev/shm` denied** | Same test |
| Linux remount probe | **remount root as read-write denied after capability drop** | Same test |
| Network namespace probe | **worker and parent namespace IDs differed** | Same test |
| External independently coded semantic audit | **valid and invalid behavior corroborated** | Targeted independent parity test plus receipt fraud tests; shared JSON Schema caveat |
| Explicit invalid example | **REFUSED, exit 1** | `examples/governed_refused_receipt_v0_4.json` |
| Valid reference example | **STATIC_PASSED, exit 0** | `examples/governed_pass_receipt_v0_4.json` |
| Both generated v0.4 example receipts | **passed v0.4 JSON Schema** | `contracts/governed_receipt_v0_4.schema.json` |

There are **37 unique test methods** including the separately run parity addition, but the captured *single full-suite run* counted 36. Do not misrepresent the 37 as one complete recorded invocation. The additional test was run independently and passed.

## Direct observed containment probe output

```json
{"disposition":"CANDIDATE_ONLY","net_namespace":"net:[4026532186]","remount_denied":true,"shm_write_denied":true,"write_denied":true}
```

Parent namespace observed as `net:[4026531833]`. The test file remained byte-for-byte `UNTOUCHED`. These namespace inode numbers are local, ephemeral identifiers, not stable API identities.

## Security / scope claims

| Property | Disposition | Basis |
|---|---|---|
| Policy gate runs as separate process | TESTED_LOCALLY | Independent Python process and read-only allowlist |
| Gate grants no admission/publication | TESTED_ON_CORPUS | No positive authority transitions in output; negative escalation tests |
| Two worker processes are independently contained by Linux namespaces | TESTED_LOCALLY | Child launch and kernel probes in this container |
| Existing mounts appear read-only after bootstrap | TESTED_LOCALLY | Worker checks `/proc/self/mountinfo`; negative writes/remounts observed |
| No external network routes in worker namespace | PARTIALLY_OBSERVED | Different network namespace observed; full routing/egress policy not exhaustively probed |
| OS read permission minimization | NOT_IMPLEMENTED | Worker inherits broad readable filesystem paths |
| IPC peer authentication/replay protection | NOT_IMPLEMENTED | Message digest is not authentication |
| Untrusted native-code sandbox security | NOT_PROVEN | No comprehensive escape/security audit |
| Independent attestation and trusted policy custody | NOT_IMPLEMENTED | Same package, host and ownership; shared manifest schema |
| Behavior-preserving source transmigration | TESTED_ON_19_CASE_CORPUS | Not universal semantic equivalence |
| Crete break-before-mutation | NOT_IMPLEMENTED | Declarative check only |
| Native Windows restricted-token/Job Object implementation | NOT_IMPLEMENTED | Future target, see `WINDOWS_BOUNDARY_PLAN.md` |
| Admission / publication | FORBIDDEN_BY_DESIGN | Never granted or performed |

## Unsuccessful research preserved

Landlock availability probe returned `ENOSYS` (errno 38) when attempting to query the ABI. The Landlock prototype was **not wired**; see `research/LANDLOCK_ATTEMPT.md`. The exercised boundary is the mount/user/network namespace path, followed by explicit capability dropping.

## Reproduction

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m microtrans.governed examples/implementation_manifest_v0_3.json
python -m microtrans.governed examples/invalid_manifest_v0_3.json
```

**Conclusion:** A governed, Linux-only candidate validation chain was constructed and tested. The observed tests support bounded process-level write-denial on the tested mount locations and an independently coded semantic check. This does not establish a general sandbox, authenticated system of microservices, formal verification, Windows compatibility, Crete, or authorized publication.
