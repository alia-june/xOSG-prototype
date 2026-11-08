# P07 internal-testbed threat model

## Protected properties

- supplied input is not executed;
- interpretation output cannot grant authority;
- the standalone package performs no network access or filesystem mutation;
- malformed providers become bounded visible evidence rather than process
  authority;
- output size, source length, metadata depth, item counts, diagnostics, layers,
  and candidates remain bounded;
- the exact artifact can be identified and restored by hash.

## Trust boundaries

| Boundary | Current treatment |
|---|---|
| User text and metadata | Untrusted; validated, detached, bounded, and serialized canonically |
| Interpretation layers | Trusted first-party testbed code; failures are caught and surfaced |
| Optional historical-suite adapters | Absent from the standalone wheel; explicit availability check only |
| Lexical datasets | Not bundled in the wheel; any future pack requires separate verification |
| Filesystem | No runtime write interface in the package |
| Network | No accepted runtime network capability |
| Output consumer | Receives proposal-only JSON with fixed `authority_effect: NONE` and `execution_allowed: false` |

## Abuse and failure cases

- control characters, lone surrogates, oversized text, deep metadata, excessive
  candidates, forged public objects, malformed spans, and provider exceptions;
- attempts to reinterpret a candidate as authorization or executable action;
- hidden network or process imports introduced into the standalone package;
- accidental filesystem access introduced through a convenience API;
- corrupted or substituted wheel bytes;
- nondeterministic output across repeated or concurrent calls;
- unavailable optional adapters being mistaken for successful integration.

## Controls

P05 tests already exercise input, provider, output, concurrency, and resource
bounds. P07 adds a source-level forbidden-capability scan, repeated deterministic
measurements, host-bounded performance and memory checks, Python 3.11–3.14 basic
CLI probes, and a corrupted-artifact restore rehearsal.

## Residual risk

In-process third-party Python providers would not be forcibly time- or
memory-isolated. They remain outside the accepted testbed boundary. Future
resource modularization should prefer declarative data packs read by first-party
adapters; accepting executable plug-ins requires a process-isolation design and
new validation.
