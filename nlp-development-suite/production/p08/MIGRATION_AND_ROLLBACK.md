# Internal test candidate migration and rollback

## Migration

Install the contained wheel only into an isolated test environment. Adoption is
explicit; the candidate does not replace the historical projects, lexical data,
catalog state, user files, or system configuration. It creates no persistent
runtime state.

## Rollback

1. Preserve the failing input, output, candidate archive, wheel, and hashes.
2. Stop invoking the candidate in the isolated environment.
3. Uninstall it or discard the isolated environment.
4. Restore the prior exact wheel or environment from its verified hash.
5. Rerun the plan, authority, manifest, P06, and P07 checks.
6. Record the failure and discriminator before creating another candidate.

Rollback must not delete user data, historical evidence, or external lexical
sources. A future stateful consumer needs a separate recovery design.
