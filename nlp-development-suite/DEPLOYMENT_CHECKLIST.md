# Prototype repository deployment checklist

1. Run `python -B RUN_PROTOTYPE_CHECKS.py` and retain its complete output.
2. Inspect `PROTOTYPE_MANIFEST.json`, `SANITIZATION_REPORT.json`, `DATA_POLICY.md`, and the retained component licenses.
3. Confirm the remote owner, repository name, visibility, and branch policy separately; none is inferred by this staging tree.
4. Initialize Git only in a fresh copy if commit-author metadata is appropriate for publication.
5. Do not add dictionary databases, generated shards, local registries, hosting metadata, credentials, or build caches.
6. If deploying the Atlas UI, mount or build separately approved runtime data; a code-only deployment will show data unavailable.
7. Treat the deployment as a prototype. Production, publication, semantic-canon, and receiving-system acceptance remain separate decisions.
