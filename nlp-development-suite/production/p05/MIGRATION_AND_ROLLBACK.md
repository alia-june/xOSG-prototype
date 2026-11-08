# P05 migration and rollback

## Migration

This slice adds a separate package, `nlp-offline-interpreter/0.1`; it does not
replace or rewrite Lexicon Core, the Natural Language front end, the historical
manifest, catalog state, user files, or sister-system schemas.

Consumers may adopt the dependency-free `analyze_text` API or the `--basic`
CLI explicitly. The optional suite adapter remains an opt-in proposal layer and
reports a typed unavailable state when its separately packaged dependencies are
absent. There is no persistent application-state migration in P05.

## Rollback baseline

- Source baseline: Git parent of the P05 admission commit.
- Historical archive baseline: unchanged `PACKAGE_MANIFEST.json` and source ZIP.
- Runtime state: none created by the interpreter itself.
- User-controlled redirected output is outside automatic rollback and must not
  be deleted by the package.

## Rollback procedure

1. Stop distributing or invoking the P05 package version.
2. Preserve the failing input, canonical JSON output, package version, and
   manifest hashes.
3. Remove the package from the isolated environment or return to the prior Git
   commit; do not alter the historical snapshot.
4. Re-run manifest, authority, baseline, and non-execution checks.
5. Record the failure and discriminator before re-admitting a corrected slice.

Rollback does not authorize deletion of user data, catalog state, or historical
evidence. A future stateful consumer requires its own migration and rollback
procedure.
