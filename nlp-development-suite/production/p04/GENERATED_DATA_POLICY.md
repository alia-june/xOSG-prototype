# Proposed generated-data policy

Truth state: `GENERATED_SYNTHESIS`  
Authority effect: `NONE`

Every data artifact must be classified as source input, generated output,
cache, development evidence, or release artifact. A hash proves byte identity,
not semantic correctness, licensing, canon, or production fitness.

- Source inputs require origin, version, license status, and integrity evidence.
- Generated outputs require a deterministic builder, input identities, tool
  versions, output manifest, and a reproducibility result.
- Caches and virtual environments are never release inputs and remain ignored.
- Large Lexicon Atlas shards stay separate from the historical package manifest.
- The P04 wheelhouse is generated staging material, not recovered source. It is
  retained in the staging repository so clean checkouts can install without the
  network. Its manifest and hash lock bind every wheel by identity and bytes.
- No omitted raw corpus may be fetched, redistributed, or treated as available
  without a separately accepted data decision.
