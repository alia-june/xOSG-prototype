# Windows v0.5 fail-closed transition matrix

| Condition | OS/control before candidate code | Disposition |
|---|---|---|
| Not Windows 11 build 26100 or newer | No worker launch | `REFUSED` |
| Python executable missing or not absolute | No worker launch | `REFUSED` |
| Service not on fixed allowlist | No worker launch | `REFUSED` |
| AppContainer profile missing/invalid | Refuse before process creation or on process launch | `REFUSED` |
| Job Object creation/limit configuration fails | No worker launch | `REFUSED` |
| Pipe setup, handle inheritance allowlist, attributes fail | No worker launch | `REFUSED` |
| `CreateProcessW` fails | No worker execution | `REFUSED` |
| `AssignProcessToJobObject` fails | Child remains suspended, then terminated and handles closed | `REFUSED` |
| Token not expected AppContainer / capabilities not zero / SID mismatch | Child remains suspended; job handle closed | `REFUSED` |
| Job membership absent | Child remains suspended; job handle closed | `REFUSED` |
| ResumeThread fails | Job handle closed; child terminated | `REFUSED` |
| Worker hangs, floods output, or exits abnormally | Terminate/close job and refuse | `REFUSED` |
| Worker JSON invalid, wrong identity, or rejects | Propagate refusal; do not run next stage after schema refusal | `REFUSED` |
| External validator mismatches, fails, or claims admission | Refuse entire chain | `REFUSED` |
| All checks succeed | Candidate static pass only | `STATIC_PASSED`; `NOT_ADMITTED`; `NOT_PUBLISHED` |

**Evidence status:** Windows API enforcement and probes in this matrix are **not yet verified on Windows**. Code paths are written but not observed on the target OS. Linux v0.4 containment tests remain a separate Linux-only witness.
