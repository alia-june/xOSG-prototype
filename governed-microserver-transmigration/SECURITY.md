# Security policy

## Project maturity

**Research prototype; not production security software.** The v0.5 Windows backend has not been exercised on a Windows host, and no claim of full sandbox isolation, escape resistance, cryptographic IPC authentication, or independently signed attestation is made. The repository has no operational admission or deployment authority.

## Responsible reporting

If this project is hosted on GitHub, use the repository's **Security → Report a vulnerability** private reporting feature if its owner has enabled it. If private vulnerability reporting is not configured, request a private channel from the maintainer without publishing exploit steps or sensitive details in a public issue. No project-specific security email address is asserted here.

Include the affected version/commit, host OS/build, Python version, reproducible minimal test, expected vs observed boundary, and whether the report involves privileged local access or untrusted input. Never attach real credentials, private files or destructive payloads.

## Supported security assurance

None of the repository revisions is currently designated a security-supported production release. Historical Linux negative probes test **specific operations** only. Windows Win32, AppContainer, Job Object, ACL and network containment evidence is pending on a real Windows host. See [docs/SECURITY_BOUNDARIES.md](docs/SECURITY_BOUNDARIES.md).

## Disclosure expectations

Fixes to authority, isolation, IPC, Crete or attestation logic require independent review and new negative tests. No test result automatically grants admission, changes component authority, or authorizes use with sensitive data.
