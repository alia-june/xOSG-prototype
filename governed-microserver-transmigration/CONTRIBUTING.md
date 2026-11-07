# Contributing

This is an experimental, candidate-only microserver validation project. Contributions should preserve explicit boundaries among **identity, interface contracts, validation, authority, composition, and publication**.

## Before opening a pull request

1. Explain the intent, expected behavior and security/authority impact.
2. Prefer small, reviewable changes. Do not import large implementations wholesale without source provenance and review of rights.
3. Add a failing test for any bug being fixed, or contract/negative tests for new interfaces.
4. Preserve candidate-only outcomes unless an independently reviewed admission design is explicitly in scope.
5. Do not add remote execution, implicit permission escalation, automatic profile creation, broad ACL grants or unsandboxed fallback.
6. Keep secrets, host-specific paths, private data, credentials, tokens and real production files out of fixtures, logs and screenshots.
7. Document whether a result is **tested**, **source-inspected**, **proposed**, or **unverified**. Do not silently promote a source-only claim into runtime assurance.

## Checks before proposing a change

Install dependencies from `requirements.txt`. For non-privileged tests, run:

```bash
python -m unittest -v tests.test_transmigration.ProtocolTests tests.test_transmigration.SourceParityTests tests.test_governed_v0_4.PolicyTests tests.test_windows_v0_5.WindowsContractTests
```

Full regression is:

```bash
python -m unittest discover -s tests -v
```

Some full-suite tests attempt Linux namespaces and may skip or refuse on hosts where prerequisites are absent. Windows isolation assertions require an actual Windows test environment and must be reported as such. **Do not use GitHub-hosted CI as proof of Windows native containment.**

## Proposed change format

Include: goal, source/lineage references, changes made, contract implications, test command + host, observed results, unresolved issues and any new permissions or OS resources. Refusals and test failures are reportable results, not reasons to weaken a boundary.

## Security reports

See [SECURITY.md](SECURITY.md). If reporting an exploit or bypass, do not publish working bypass details in a public issue before the maintainers have a secure channel to review it.

## Conduct

Disagree over evidence, contracts and implementations rather than people. Be specific and reproducible; do not claim verification beyond observed evidence.
