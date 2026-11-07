# Architecture and intended use

## Scope

The current implementation reconstructs **one existing manifest-checking capability** as two JSON-CLI processes and ordinary identity-only glue. It is not yet a general service generator or API microserver runtime for arbitrary user-selected operations.

## Processing sequence

1. The trusted local orchestrator loads the candidate manifest.
2. The authority gate checks a fixed, read-only, candidate-only request policy.
3. The schema worker verifies the manifest's JSON Schema.
4. Ordinary glue forwards the same payload and checks corresponding digests, while refusing to dispatch downstream if the first worker rejects it.
5. The graph worker checks identity uniqueness, operation endpoints, schema compatibility and dependency topology.
6. A separate-code semantic validator reviews the manifest and candidate receipts.
7. The orchestrator emits `STATIC_PASSED` or `REFUSED` without admission or publication authority.

## Boundaries and identity

- **Microserver:** an isolated-by-process JSON-CLI validation operation; it is not a public HTTP service.
- **Ordinary glue:** an explicit typed relationship with identity-only transformation and refusal propagation.
- **Crete:** hardened, break-before-mutation composition concept; **only declarations are checked**, enforcement is not implemented.
- **Authority:** a separate application-level policy decision; the existing actor value is explicitly unauthenticated and is not an attested identity.
- **External validator:** a separate implementation path for semantic checking, but not an independently operated service, different trust domain, or signed witness.
- **Source witness:** prior checker and hashes retained for traceability; parity tests cover a limited corpus, not full semantic equivalence.

## Platforms

The governed Linux path attempts mount/network namespaces, capability dropping and read-only mounts; limitations are enumerated in [SECURITY_BOUNDARIES.md](SECURITY_BOUNDARIES.md). The Windows backend attempts a suspended AppContainer process launch with a constrained Job Object and handles, but remains unverified. Unavailable boundaries lead to refusal rather than an unsandboxed governed fallback.

## Next architectural milestones (not implemented)

- Verify the Windows backend on Windows 11 LTSC with disposable negative probes.
- Specify a generic service registry and more than two fixed operations.
- Introduce signed/authenticated IPC and binding between receipts and principals.
- Enforce hardened Crete join semantics with measured failure behavior.
- Keep independent evidence custody and service admission separate from code publication.
- Reconstruct a second source-grounded capability and test its behavior independently and in composition.
