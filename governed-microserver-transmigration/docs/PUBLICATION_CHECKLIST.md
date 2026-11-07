# Public repository publication checklist

## Repository and ownership

- [x] Record intended repository name and owner: `alia-june/xosg-prototype`.
- [ ] Verify ownership/access to the target GitHub namespace and whether the remote repository already exists.
- [ ] Confirm rights to all code, historical files, source witnesses, examples and bundled documentation.
- [x] Select MIT and add the full `LICENSE` text; update README and publishing guide.
- [ ] Confirm legal authority to license every included file under MIT and preserve any required third-party notices.
- [ ] Review author attribution, provenance and third-party notices; the copyright notice currently reads `Alia June` (2026).

## Privacy and security

- [ ] Review repository history and all files for secrets, emails, absolute local paths, personal data, internal references and build logs.
- [ ] Confirm this candidate's scan findings; an automated pattern scan is not complete human review.
- [ ] Ensure example manifests contain no sensitive values or real credentials.
- [ ] Review security-policy contact route; enable GitHub private vulnerability reporting if available.
- [ ] Confirm public code does not contain unexpectedly privileged or network-exposed functionality.
- [ ] Run dependency/license review and enable code/dependency scanning in the eventual host repository.

## Accuracy and tests

- [ ] Run the public nonprivileged contract test command on both Windows and Linux.
- [ ] Run the full regression where kernel prerequisites are available, recording skipped tests separately.
- [ ] Run native Windows opt-in profile/probe tests in an **isolated non-production VM**, and retain evidence. Not required for publishing *source labeled unverified*, but required for verified-Windows claims.
- [ ] Confirm no README, release title, badge or security claim implies native Windows verification.
- [ ] Review `SOURCE_ARCHIVE_CHECKSUMS_SHA256.txt` as **historical only** and use `REPOSITORY_SHA256SUMS.txt` for the candidate.

## Git hosting and announcement

- [ ] Initialize and inspect Git history locally; do not push private archives or unreviewed work.
- [ ] Create the remote public repository explicitly under the chosen account.
- [ ] Configure branch protection and review requirements; repository admins decide the exact policy.
- [ ] Verify the contract-only CI workflow and security reporting settings.
- [ ] Publish an initial *prototype/source candidate* tag; avoid production or Windows-verified language.
- [ ] After publication, confirm links, license, provenance, release asset checksums and repository visibility.

**Current status:** package prepared locally; no public repository, remote push, tag, GitHub release or runtime admission action has been performed.
