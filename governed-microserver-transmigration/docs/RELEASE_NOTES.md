# Prototype source candidate — v0.5 (publication preparation)

**Disposition:** prepared for repository review, **not published**.

**Target:** `alia-june/xosg-prototype` · **License:** MIT · **Copyright:** Alia June (2026).

## Included

- v0.5 microserver and ordinary-glue reference implementation and retained source witnesses.
- Candidate-only authority and independent-code audit components.
- Linux namespace path and *unverified* Windows 11 AppContainer/Job Object source candidate.
- Public README, contribution/security guidance, publication checklist, source audit notes and limited contract-only CI.

## Verified on the prepared repository tree

- **22** contract/policy/source-parity tests passed in one run.
- **8** glue/composition tests passed in a fresh complete suite rerun (the first attempt stalled on its last test; its isolated rerun also passed).
- **29** Python files parsed, **17** JSON files parsed with no literal `null` or duplicate keys.
- Pattern scan found no matches for email/credential signatures or local absolute paths in the final repository candidate. This is not a comprehensive privacy audit.
- Only 3 existing v0.5 text files were changed: public README replacement and local path removal from two provenance documents; original core implementation files are byte-identical to the v0.5 archive.

## Publishing selections confirmed

- Intended GitHub remote: `https://github.com/alia-june/xosg-prototype.git`.
- License: MIT; copyright notice: `Copyright (c) 2026 Alia June`.
- Remote publication still requires a separate explicit action and rights review.

## Publishing selections confirmed

- Intended GitHub remote: `https://github.com/alia-june/xosg-prototype.git`.
- License: MIT; copyright notice: `Copyright (c) 2026 Alia June`.
- Remote publication still requires a separate explicit action and rights review.

## Pending

- Confirm publication rights and third-party license compatibility; root MIT license now selected.
- Native Windows host execution and containment evidence.
- Fresh full regression on the candidate (the attempted run did not complete within execution limit).
- Independent security review and hosted CI result.
- Confirm GitHub namespace access and execute actual public push (not performed).

Source publication never implies runtime admission or authorization.
