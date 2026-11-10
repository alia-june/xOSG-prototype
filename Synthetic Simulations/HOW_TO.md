# How to read the Synthetic Simulations record

This is a reading guide to the public research record. The private control-plane implementation and quarantined candidate packages are not included here. The repository contains a bounded description of the work and one sanitized failed experiment, not a supported simulation runtime to launch.

## Choose the part you want to understand

| Question | Start here | Keep this boundary in view |
| --- | --- | --- |
| What is public, and what stayed private? | [Project README](README.md#current-state) and [xOSG migration record](../docs/xosg/MIGRATION.md) | The public relocation notice describes the current placement. Earlier references to private publication describe their historical context. |
| How was the control plane intended to behave? | [Deterministic control-plane lane](README.md#lane-a-deterministic-control-plane) | Read the mission contract, evidence checks, planning, non-launching setup, synthetic turn, and terminal result as separate steps. |
| What was investigated for memory instrumentation? | [LLM memory instrumentation lane](README.md#lane-b-llm-memory-instrumentation) | Intake findings and proposed experiment boundaries do not establish admission, deployment, or integration of the private candidates. |
| What happened in the retained failed experiment? | [Failed kit record](defunct-experiments/failure/llm-prompt-hardening-modular-kit-v1-5-candidate/README.md) and its [validation record](defunct-experiments/failure/llm-prompt-hardening-modular-kit-v1-5-candidate/source/VALIDATION.md) | The sanitized source is retained to preserve evidence and lessons. Its presence does not change the failed and defunct disposition. |

## Newly indexed historical references

- [Omnifact v0.8.0 — research-staging record](research-staging/omnifact-ref-v0-8-0/README.md) and [sanitization summary](research-staging/omnifact-ref-v0-8-0/SANITIZATION_REPORT.md): historical reference candidate, not designated defunct, not admitted; sanitized ZIP bytes not hosted here.
- [MAGE Core 0.1.7-prealpha — defunct record](defunct-experiments/retired/mage-core-v0-1-7-prealpha/README.md) and [scoped design](defunct-experiments/retired/mage-core-v0-1-7-prealpha/DESIGN_RECORD.md): retired environment research, not integrated; sanitized ZIP bytes not hosted here.
- [LLM prompt hardening modular-kit failure](defunct-experiments/failure/llm-prompt-hardening-modular-kit-v1-5-candidate/README.md): sanitized historical failed experiment already present.

These links concern research records, not active components or downloadable ZIP releases.

## Read results in their own scope

In the control-plane lane, the synthetic orchestrator proposes a route, a deterministic rule gate constrains it, a trace role records the decision, and a synthetic response role renders a bounded placeholder. The historical use of *hypervisor* names the trace role; it does not establish hardware virtualization or isolation. Setup retains `can_launch: false`, `can_execute: false`, and `release_ready: false`. `FINISHED` means the declared planning, setup, or simulation operation completed, not that the underlying workload ran or was accepted.

The [exercised behavior record](README.md#exercised-behavior) reports **31 passing tests** for the private v0.4 suite. That is historical evidence for the listed simulation behaviors. It does not show actual model behavior, authenticated approval, isolation, or production safety, and the implementation is not supplied here for a replay.

For the separate modular-kit candidate, the public README reports a Windows run of **42/43 tests passing**, with a reproduced POSIX-mode portability defect. Archive integrity and that test outcome answer different questions. Neither converts the candidate into the control-plane implementation or a supported release. Keep the failed record and its migration context together when citing it.

For the remaining requirements before real execution, read [Before Real Integration](README.md#before-real-integration). For the broader family and related projects, use the [xOSG overview](../docs/xosg/README.md). No command is needed to follow this reading route.
