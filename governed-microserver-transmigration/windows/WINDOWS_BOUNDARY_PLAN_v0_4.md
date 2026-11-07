# Windows 11 LTSC Microserver Containment — Research / Not Implemented

**Disposition:** `RESEARCH_ONLY / NOT_WIRED / NOT_VERIFIED_ON_WINDOWS`.

The v0.4 Linux proof uses filesystem and network namespaces and mount flags that do not translate directly to Windows 11 LTSC. The Windows implementation must be independently reconstructed and tested rather than declaring a shell or PowerShell wrapper equivalent to Linux containment.

## Proposed native Windows boundary

1. **Broker:** a separately controlled authority process, initially capable only of accepting a local read-only validation request. The broker owns the stage allowlist and validates manifest identity and scope prior to worker launch.
2. **Token isolation:** create workers with an appropriately restricted primary token or verified AppContainer isolation. Define the exact deny and allowed ACL surface for each input, executable, dependency, and output; do not rely on JSON envelope fields as OS enforcement.
3. **Process management:** use Job Objects to set CPU, memory, active-process and process-lifetime limits and kill the job on broker termination. A Job Object does not replace a restricted token or AppContainer.
4. **Controlled IPC:** broker-owned local anonymous or named pipes with restrictive ACLs. Define explicit identity and replay handling before accepting results. Avoid insecure inherited handles, environment and implicit privilege transfer.
5. **Immutable inputs:** use an independently protected read-only acquisition path. Candidate workers must not obtain write handles to originals. No operation may publish or authorize admission.
6. **Adversarial verification:** independently test that workers cannot write protected files/registry locations, spawn uncontrolled descendants, open disallowed networking, use unbrokered privileges or escape process limits. Record process tokens and job membership, and test refusal when creation restrictions fail.

## Required platform research questions

- Are restricted primary tokens sufficient for the exact file, registry, and network restrictions, or is AppContainer necessary for the intended threat model?
- Which Win32 launch sequence ensures resource limits are established *before* executing worker code? Study suspended process creation and assignment to an initialized Job Object, and guarantee termination on failure.
- Is the selected Windows build compatible with the chosen API and app packaging mode? Confirm on the actual edition and patch level.
- How will source dependencies, Python's runtime imports, and controlled output pipes be available to workers without ambient read/write access to unrelated user data?
- What external principal controls the policy, attestation, and admission decisions? How are its custody and signatures validated independently?

## Verification gates

| Gate | Status |
|---|---|
| Restricted token / AppContainer creation | NOT_IMPLEMENTED |
| Job Object limits and kill-on-close | NOT_IMPLEMENTED |
| OS-level file/registry permission negative probes | NOT_TESTED |
| IPC principal authentication and replay protection | NOT_IMPLEMENTED |
| Windows 11 LTSC deployment test | NOT_TESTED |

## Primary sources

- Microsoft, [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects): resource accounting, process-group limits and enforcement.
- Microsoft, [AssignProcessToJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject): assignment rules and related process rights.
- Microsoft, [Restricted Tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/restricted-tokens): restrictions on process security access checks and restricted primary tokens.
- Microsoft, [Processes in the Client Security Context](https://learn.microsoft.com/en-us/windows/win32/secauthz/processes-in-the-client-security-context): primary-token process creation considerations.
- Microsoft, [Create Process In Sandbox APIs](https://learn.microsoft.com/en-us/windows/win32/secauthz/createprocessinsandbox): evaluate applicability to the actual Windows 11 LTSC deployment; do not assume availability without testing.

No Windows security guarantees were demonstrated in this release.
