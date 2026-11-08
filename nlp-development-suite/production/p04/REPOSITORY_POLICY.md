# Proposed repository policy

Truth state: `GENERATED_SYNTHESIS`  
Authority effect: `NONE`

The working shape is one local suite-level Git repository with component
directories retained. The historical `PACKAGE_MANIFEST.json` remains immutable
evidence and new development uses separate manifests. This reversible staging
implementation is recorded in `WORKING_ASSUMPTIONS.json`; it does not silently
accept Q-001 as production canon.

Required controls after acceptance:

- protect the default branch and require the P04 check set;
- review dependency and workflow changes separately from behavior changes;
- prohibit committed credentials, local environments, caches, and build output;
- retain source, generated data, and release artifacts as distinct classes;
- preserve historical manifest members as raw bytes through root `* -text`
  attributes and verify them first in every clean checkout;
- bind releases and acceptance receipts to exact commit and artifact hashes;
- require non-executing defaults and prevent CI from receiving production
  credentials.

The root `.gitignore` and local repository implement the working assumption.
No remote, protected branch, deployment integration, or production authority is
implied.
