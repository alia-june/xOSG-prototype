# Repository preparation audit

**Scope:** local source archive used to construct the public candidate. Findings are not a third-party audit or a complete secret scan.

## Inspected archive

- Baseline: `WORK_PROCESS_WINDOWS_APPCONTAINER_MICROSERVERS_v0_5.zip` (76 entries; ZIP CRC check passed).
- Archive contents and the candidate's Python/JSON files were inspected programmatically.
- A regex-based scan inspected source and documentation for common credential patterns, email addresses, private-network IP strings, personal-name examples and absolute local paths.
- **Two build-machine paths** were found in the root `PROVENANCE.md` and `PROVENANCE_v0_5.md` and replaced with a portable statement identifying the retained v0.4 source archive.
- No matches for the scanned hard-coded credential, email, private-address or personal-name patterns appeared in the upstream text. This is **not** proof that no sensitive data exists.
- Existing source history and tests were retained; the root README is replaced with a public-facing version.
- `SOURCE_ARCHIVE_CHECKSUMS_SHA256.txt` is a historical source-archive file and is **not** a checksum record for this modified candidate.

## Claims that remain unverified

Windows native execution, sandbox ACL enforcement, signed attestation, authenticated IPC, Crete joining and production-readiness. No vulnerability or penetration assessment was performed.

## Repository review before publication

The repository owner should independently inspect all included historical files, review copyright and license status, and decide whether the intended public distribution should include the original complete lineage.

## Candidate-specific tests and limits

- Non-privileged protocol, parity, policy and Windows contract subset: **22 tests passed** on the Linux preparation host.
- Separate glue/composition subset: **8 tests passed** on the Linux preparation host.
- Full `python -m unittest discover -s tests -v` was attempted but **did not complete before the runner time limit**; last logged case was `test_worker_without_bootstrap_is_denied`. Therefore **no fresh full-suite pass is claimed for this repackaged tree**.
- Windows native AppContainer and Job Object calls were not run.

## v0.5 publication-target update

The MIT license has been selected and the intended remote set to `alia-june/xosg-prototype`. This is an administrative selection, **not** a completed third-party rights audit or a remote publication. The archived core implementation and historical test claims are unchanged.
