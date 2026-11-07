# Manual GitHub publishing guide

**This package has not been published or pushed to GitHub.** Review [PUBLICATION_CHECKLIST.md](PUBLICATION_CHECKLIST.md) and confirm licensing/provenance rights before publication. The intended license is MIT.

## Suggested GitHub metadata (editable)

- Repository name: `xosg-prototype`
- Owner: `alia-june`
- Repository URL (intended): `https://github.com/alia-june/xosg-prototype`
- License: `MIT` (root `LICENSE` included)
- Description: `Experimental governed JSON microservers, composition glue, and Windows AppContainer research.`
- Topics: `python`, `microservices`, `json-schema`, `windows`, `appcontainer`, `software-architecture`, `research-prototype`
- Visibility: **public**, only after the owner completes the release checklist
- Primary branch: `main`

## Manual steps

1. Review the complete tree, examples, documentation and source witnesses.
2. Confirm the included MIT license can lawfully cover all distributed code, documentation and witnesses; verify ownership and third-party notices.
3. Create an **empty repository** with the chosen name under your intended GitHub account or organization, without auto-generating a README or license.
4. From a terminal at the root of this extracted candidate, and **only when ready to publish**, run:

```bash
git init
git branch -M main
git add .
git status --short
git diff --cached --stat
git commit -m "Initial public research prototype v0.5"
git remote add origin https://github.com/alia-june/xosg-prototype.git
git push -u origin main
```

The remote target is explicitly set to `alia-june/xosg-prototype`. If this repository already contains commits, do not initialize and push an unrelated history: inspect the remote and reconcile first. Review staged files, especially source lineage, before committing. `git push` makes the selected content public when the remote repository is public; it is intentionally **not** run by the preparation workflow.

5. In GitHub, configure permissions, private vulnerability reporting, branch protection, and source scanning where supported.
6. Inspect Actions results; contract CI is not an OS containment validation program. Optionally create a **prototype** release tag after review.

## Data and history caution

Creating a new repository from this candidate avoids importing older local Git history. Do **not** push another project's `.git` directory, private development archives, secret files or logs. Removing a secret from the current tree does not erase it from already-pushed history.
