# Work Process — Governed Microserver Transmigration v0.5

**Status:** Windows backend implemented as source candidate. Tested in this runtime: static/contract tests and Linux regression only. **No Windows host execution or admission.**

## Windows quick start (in an isolated Win11 LTSC test VM)

```powershell
py -3 -m pip install -r requirements.txt
py -3 -m windows.profiles --i-approve-profile-creation
py -3 -m windows.smoke --i-approve-local-probes
py -3 -m microtrans.governed examples\implementation_manifest_v0_3.json
py -3 -m unittest discover -s tests -v
```

Profiles are per-user and persisted; see `WINDOWS_IMPLEMENTATION.md` for ACL requirements and security limits. Nothing auto-creates profiles during `governed` execution.

## Linux compatibility

```bash
python -m microtrans.governed examples/implementation_manifest_v0_3.json
python -m unittest discover -s tests -v
```

v0.4 Linux namespace path is preserved. Windows code is not activated on Linux. No fallback from denied Windows AppContainer execution to an unsandboxed subprocess.

## Files

- `windows/native.py`: ctypes Win32 security/token/job/pipe calls.
- `windows/launcher.py`: suspended AppContainer worker launch and bounded IPC.
- `windows/policy.py`: fixed profiles and resource ceilings.
- `windows/profiles.py`: explicit per-user profile provisioning, never automatic.
- `runtime/windows_entry.py`: worker-side OS verification before service import.
- `runtime/windows_probe.py`: diagnostic worker.
- `windows/smoke.py`: opt-in broker-side negative probe.
- `WINDOWS_IMPLEMENTATION.md`: security analysis, host setup and evidence gates.
- `WORKING_RESEARCH_PROMPT_v0_5.md`: remaining Win11 host verification program.

No production API, Crete, external signed attestation, remote service, admission, or publication implemented.
