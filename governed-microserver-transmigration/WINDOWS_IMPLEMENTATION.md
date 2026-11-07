# Windows 11 LTSC — Native Microserver Containment v0.5

**Disposition:** `CANDIDATE_ONLY / NOT_VERIFIED_ON_WINDOWS / NOT_ADMITTED / NOT_PUBLISHED`.

This is a source implementation, not an assertion of successful Windows isolation. The original v0.4 Linux path remains available on Linux. The Windows path refuses if its security prerequisites cannot be established.

## Architecture

```
trusted local governed orchestrator
  |--> policy gate (separate process, v0.4 semantics)
  |--> candidate worker launch #1
  |      derive preprovisioned AppContainer SID, capabilities = zero
  |      create Job Object: kill-on-last-close; active process count 1;
  |         512 MiB process/job memory caps
  |      create two anonymous pipes and a NUL error target
  |      STARTUPINFOEX: security-capabilities + 3-handle allowlist
  |      CreateProcessW(CREATE_SUSPENDED | CREATE_NO_WINDOW)
  |      AssignProcessToJobObject
  |      query OS token: is AppContainer, zero capabilities, expected SID
  |      query OS job membership; ResumeThread ONLY if all checks pass
  |      bounded stdin/stdout and deadline; close job to terminate workers
  |--> candidate worker launch #2 (separate AppContainer profile and Job)
  |--> independent-code semantic audit (v0.4 trusted subprocess)
  +--> STATIC_PASSED or REFUSED, never ADMITTED/PUBLISHED
```

`schema-gate` and `graph-gate` have separate AppContainer profile SIDs. The optional diagnostic `boundary-probe` has its own third profile; it is **not a permitted stage** in the governed schema/graph chain.

Neither the request nor its JSON manifest can select a process executable, add capabilities, change the profile, alter Job limits, or set an arbitrary filesystem ACL. The host Python executable path is taken from the interpreter running the broker.

### Differences from Linux v0.4

- Windows Job Objects constrain resource use and descendant processes; they do **not** by themselves restrict file, registry, or network access.
- AppContainer provides OS-level resource and network containment tied to the capability list and ACL grants. Zero declared capabilities are used, but actual restrictions and exemptions **require verification** on the target machine.
- AppContainer normally has writable private profile resources. Therefore this implementation must **not** be described as an entirely read-only filesystem sandbox. It aims to deny writes to ungranted external resources.
- The trusted policy gate and independent-code validator are launched outside the AppContainer: this preserves v0.4 semantics, not complete containment of every process.
- Windows native API calls have **not been executed** in this Linux environment. Windows build compatibility, Python installation access, privilege behavior, and kernel enforcement remain unverified.

## Explicit provisioning — only on the user's Windows host

Requires Python 3.10+ x64 and installed `jsonschema`, plus a Python runtime and code directory that the AppContainer can read but must not modify. Do not grant broad filesystem access. Use an offline copy of the package and make immutable/read-only originals separately. The packaged code does not alter ACLs.

From PowerShell in the extracted v0.5 package root:

```powershell
py -3 -m pip install -r requirements.txt
py -3 -m windows.profiles
# The first command above should refuse without the approval switch.
py -3 -m windows.profiles --i-approve-profile-creation
# Each profile is created for the current user; this changes local Windows profile state.
py -3 -m windows.smoke --i-approve-local-probes
# Only after the negative probe passes:
py -3 -m microtrans.governed examples\implementation_manifest_v0_3.json
py -3 -m unittest discover -s tests -v
```

**Operational advice:** Prefer an isolated, non-administrative Windows test VM, not a main workstation, for the initial deployment. Profile creation and OS ACL adjustments are explicit operator actions. The broker does not attempt a best-effort non-sandbox fallback when it cannot execute a worker.

### Program access and AppContainer ACLs

A typical per-user Python installation or `pip` package location may not be readable from AppContainer. The profile must be created first and its exact SID inspected; the Python binary, `python*.dll`, standard library, `jsonschema` dependencies and microserver package need carefully scoped **read/execute** access for that SID. Do not grant write access to source trees, arbitrary user directories, the Windows registry, or private files. Granting `Everyone` or `All Application Packages` wide access is not recommended for this experiment. An access failure must not trigger a permissive retry.

Actual ACL setup is machine-specific and deliberately **not automated** here. The profile process is not considered successfully tested until the OS token, job membership, access-denial probes and end-to-end manifest result have been independently observed.

## Probe interpretation

`windows.smoke` creates a temporary file with known bytes, opens a broker-owned TCP listener on `127.0.0.1`, and launches a third AppContainer diagnostic service. The worker attempts to modify the disposable witness, connect to the local port, and create a descendant process. The broker checks that the witness is unchanged and that no connection was accepted. A `NEGATIVE_PROBES_PASSED_CANDIDATE` result is evidence for **only those three operations on that host**, not a formal escape-resistant security proof.

No real project input is used for the write test. The diagnostic does not request a model API, listen for remote clients or publish outputs.

## Verification / failure table

| Gate | Code path | Runtime result |
|---|---|---|
| No implicit profile creation | `windows.profiles` opt-in | Cross-platform policy test passed |
| Separate per-service AppContainer SID | `windows.policy` | Cross-platform contract test passed; Windows runtime pending |
| Zero-capability `STARTUPINFOEX` | `windows.launcher` | Constructed; Win32 execution pending |
| `CREATE_SUSPENDED` → job assignment → token verification → resume | `windows.launcher` | Constructed; Win32 execution pending |
| Max one active process and process/job memory caps | Windows Job Object | Constructed; enforcement pending |
| Exact 3-handle allowlist | `PROC_THREAD_ATTRIBUTE_HANDLE_LIST` | Constructed; inheritance audit pending |
| Bounded JSON IPC and termination | `windows.launcher.invoke` | Constructed; Win32 stress test pending |
| Protected file/network/descendant denial | `windows.smoke` | NOT TESTED on Windows |
| Whole governed chain on Windows | `microtrans.governed` | NOT TESTED on Windows |
| Authenticated IPC, signed external attestation, Crete | Unimplemented | NOT IMPLEMENTED |

## Model and unclosed risks

1. **No hostile-code safety claim.** A Windows sandbox boundary needs adversarial assessment, AppContainer policy inspection and kernel ACL tests. Some host objects may remain accessible.
2. **Read minimization is not enforced.** AppContainer's default read access can remain broader than the recovery architecture's default-deny read requirement.
3. **Private writes are possible.** Windows AppContainer storage is not globally immutable; no Crete enforcement is implemented.
4. **Broker integrity is assumed.** A malicious same-user attacker who can rewrite package code or executable paths may invalidate evidence. Signed binaries, directory ACL/custody and profile identity management remain needed.
5. **No Windows functional parity claim.** The Linux tests cannot test Win32 `CreateProcessW`, AppContainer tokens, ACLs or Job Objects.
6. **No production HTTP API.** These are local JSON CLI/IPC microservers; external transport and mutual authentication remain separate tasks.

## Primary research sources

- [Microsoft: AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)
- [Microsoft: Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)
- [Microsoft: CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)
- [Microsoft: DeriveAppContainerSidFromAppContainerName](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername)
- [Microsoft: UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)
- [Microsoft: Handle inheritance](https://learn.microsoft.com/en-us/windows/win32/procthread/creating-processes)
- [Microsoft: Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
