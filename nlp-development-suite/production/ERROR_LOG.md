# Error and diagnostic-redux log

## ERR-001 — Historical snapshot mutation caught before baseline completion

- Date: 2026-10-01
- Observation: initial generic-engine files were added inside manifest-covered
  `projects/` directories.
- Risk: new development could be confused with the immutable supplied snapshot,
  and `VERIFY_EXPORT.py` would correctly report changed members.
- Discriminator: move new files into a separate successor, restore the one
  modified historical file, and rerun the historical manifest verifier.
- Resolution: new work now lives in
  `development/nlp-offline-interpreter`; manifest-covered files were restored.
- Regression guard: the ordered baseline begins with `snapshot-manifest` and
  the successor has its own baseline pointer and manifest.
- Result: `verified 1306 manifest members`.

## ERR-002 — Layer-local miss incorrectly downgraded fallback success

- Date: 2026-10-01
- Observation: `I feel uncertain` produced an ELIZA NXT proposal but the global
  result was `partial` because the earlier alias layer's no-match region was
  promoted globally.
- Competing explanations: the fallback was incomplete, or the aggregation rule
  conflated layer-local and global unresolved state.
- Discriminator: inspect the candidate and layer trace independently.
- Resolution: no-match unresolved regions remain pending and become global only
  when no later layer supplies a candidate. The layer-local miss remains visible
  in the trace.
- Regression guard: `test_layer_local_no_match_does_not_downgrade_successful_fallback`.

## ERR-003 — Initial wheel command masked missing build backend

- Date: 2026-10-01
- Observation: `pip wheel --no-build-isolation` failed because the active test
  environment lacked `setuptools`, but a following successful file-list command
  caused the shell invocation to report exit code zero.
- Discriminator: inspect `importlib.util.find_spec`, run `pip show`, and propagate
  the packaging command's exit code before any later command.
- Resolution: pin `setuptools==84.0.0`, use isolated PEP 517 build, and stop on
  nonzero exit. Wheel build and clean temporary installation then passed.
- Regression guard: packaging commands must check `$LASTEXITCODE` immediately;
  `BUILD_VALIDATION.json` records the exact development wheel evidence.

## ERR-004 — System interpreter lacked the pinned schema validator

- Date: 2026-10-01
- Observation: the final ordered run invoked the system Python, which did not
  contain `jsonschema`; the runner stopped at successor test 6 of 11.
- Discriminator: import the dependency in both the system interpreter and the
  prepared development environment, then rerun the same ordered suite.
- Resolution: preserve the failed receipt and rerun through the prepared
  `.venv`, which contains the pinned `jsonschema==4.26.0` dependency.
- Regression guard: the entry-point instructions require the development
  dependencies, and every report records the exact interpreter command.

## ERR-005 — Torture test overstated the accepted JSON depth boundary

- Date: 2026-10-01
- Observation: the first torture run expected sixteen nested arrays beneath the
  root metadata object to pass, but the documented depth budget counts the root
  object as depth zero and its value as depth one.
- Discriminator: trace the recursive depth argument from the metadata root to
  the scalar leaf and test the adjacent accepted and rejected cases.
- Resolution: the accepted fixture now uses fifteen nested arrays beneath the
  root; adding one more is the rejected boundary.
- Regression guard: the torture test keeps both adjacent cases and the item
  budget boundary in the same test.

## ERR-006 — Package probe used the wrong relative interpreter path

- Date: 2026-10-01
- Observation: the first post-hardening wheel probe addressed the prepared
  interpreter with two parent traversals from the successor directory instead
  of the required three. PowerShell reported a launch error but the surrounding
  command did not provide a trustworthy nonzero process result.
- Discriminator: resolve the interpreter to an absolute existing file before
  invoking the build and use `$?` immediately after native and PowerShell
  launches.
- Resolution: no build from the failed attempt was accepted; its isolated
  temporary directory was identified for removal before a corrected rerun.
- Regression guard: package probes must validate absolute tool paths and test
  both `$?` and `$LASTEXITCODE` where their command types differ.

## ERR-007 — Default wheel timestamps prevented byte reproducibility

- Date: 2026-10-01
- Observation: two isolated builds contained byte-identical members and had the
  same size but different wheel hashes.
- Discriminator: compare every ZIP member hash and timestamp between builds.
- Resolution: only generated distribution metadata timestamps differed. Both
  builds were repeated with `SOURCE_DATE_EPOCH=1704067200`; the resulting wheels
  were byte-identical with SHA-256
  `511d8cb79835ed38c33bdf96461e097fa652dd11bc1dc9c6f0c65eb084d6a20f`.
  One of those exact wheels was installed and exercised in a new environment.
- Regression guard: reproducibility evidence must compare at least two isolated
  builds using the recorded epoch and then install the exact hashed artifact.

## ERR-008 — Relative interpreter mistake recurred during manifest renewal

- Date: 2026-10-01
- Observation: after intentionally removing the stale successor manifest for
  regeneration, the builder was invoked from the successor directory with the
  same two-parent relative interpreter path error recorded in ERR-006.
- Risk: the successor temporarily had no development manifest.
- Resolution: stop using relative interpreter paths for nested working
  directories and invoke the already validated absolute prepared interpreter;
  regenerate and independently verify the manifest before any baseline run.
- Regression guard: all remaining validation commands in this hardening pass
  use the absolute prepared interpreter path.

## ERR-2026-10-01-P04-001 — clean-stage dependency omission

- Observation: the first clean P04 environment installed its 14 locked wheels,
  then the Natural Language suite failed to import `aprompt` in two test modules.
- Explanation: `aprompt==1.1.0` was installed in the existing development
  environment from a local wheel but was absent from the exported requirements.
- Discriminator: the remaining 52 Natural Language tests and all earlier stages
  passed; both errors were `ModuleNotFoundError: aprompt`.
- Correction: copied the byte-identical local wheel into the ignored P04
  wheelhouse and added its exact version and SHA-256 to the reviewed input and
  hash lock.
- Regression guard: P04 now requires the input, lock, wheel metadata, manifest,
  and exact wheelhouse membership to agree; the clean-stage run starts from a
  new environment and performs a network-disabled installation.
- Status: verified by `p04-stage-2026-10-01-py314-r3.json`; the offline install,
  full baseline, two builds, and reproducibility comparison passed.

## ERR-2026-10-02-P04-002 — initial Git checkout normalized historical bytes

- Observation: the first detached worktree failed `VERIFY_EXPORT.py` with 54
  historical text files reporting size and SHA-256 mismatches.
- Explanation: those files were initially indexed before the root binary
  preservation attribute existed, so Git stored normalized line endings even
  though the source workspace remained unchanged.
- Discriminator: affected clean-checkout files were shorter by one byte per
  source line while the original workspace still passed all 1,306 manifest
  records.
- Correction: retain `* -text` at the repository root and re-index tracked files
  with explicit renormalization, causing Git to store the original raw bytes.
- Regression guard: every clean-checkout stage begins with the historical
  manifest verifier before dependency installation or behavior testing.
- Status: verified from commit `017a961`; all 1,306 historical members and the
  full CPython 3.11–3.14 clean-checkout matrix passed.

## ERR-2026-10-02-P04-003 — unprepared interpreter reused for final baseline

- Observation: a final top-level baseline stopped at the dependency preflight
  because the bare system Python 3.14 did not contain `jsonschema==4.26.0`.
- Explanation: the command bypassed both the prepared development environment
  and `RUN_CLEAN_STAGE.py`, repeating the interpreter-selection class already
  recorded in ERR-004.
- Discriminator: manifest, plan, authorization, first-slice, successor, and P04
  checks passed before the dependency preflight reported `jsonschema: null`.
- Correction: preserve the failed receipt and rerun with the prepared exact
  environment; all 16 baseline checks then passed.
- Regression guard: support-matrix evidence is produced by `RUN_CLEAN_STAGE.py`,
  which always creates and provisions a fresh hash-locked environment.
- Status: verified by `baseline-2026-10-02-p04-local-staging-r2.json`.

## ERR-2026-10-02-P06-001 — host interpreter rejected by dependency preflight

- Observation: the first P06 production-control discovery run used the bare
  host Python 3.14 and one test failed because `jsonschema==4.26.0` was absent.
- Explanation: this was an unprepared-host check, not the authoritative pinned
  P06 environment.
- Discriminator: the P06 structural validator passed, while the environment
  regression test reported only `jsonschema must be exactly 4.26.0; found
  None`.
- Correction: create a fresh CPython 3.11 environment and install all 15 locked
  packages from the offline wheelhouse with hash enforcement.
- Regression guard: `test-environment` precedes behavior checks in the ordered
  runner and `test_environment_preflight_passes_in_prepared_environment`
  exercises the exact dependency check.
- Status: verified by `p06-control-2026-10-02-py311.json`; all 13 checks and 80
  constituent tests passed.

## ERR-2026-10-03-P07-001 — performance fixture crossed the wrong boundary

- Observation: the first P07 validation receipt failed its authority-boundary
  assertion while all static-security, compatibility, recovery, time, memory,
  output-size, and determinism checks passed.
- Explanation: the generated 700-token fixture was about 4,199 characters and
  correctly crossed the 4,096-character input limit, producing
  `invalid_input`; the check expected a below-input-limit but above-token-limit
  `partial` result.
- Discriminator: compare the fixture length with both adjacent documented
  bounds and inspect the returned typed status.
- Correction: use 600 tokens, which exceeds the 256-token retention limit while
  staying below the 4,096-character input limit.
- Regression guard: retain the expected `partial` status, non-empty unresolved
  region, and fixed no-authority fields in the P07 runner.
- Evidence: failed receipt `p07-validation-2026-10-03.json` is preserved; the
  corrected rerun uses a new append-only report path.

## ERR-2026-10-03-P07-002 — hardening order expectation omitted P07

- Observation: after adding `p07-validation` to the hardening runner slice, the
  control regression still expected the prior six-check list.
- Explanation: runner behavior and its exact-order regression were changed in
  separate edits.
- Discriminator: the failure showed one additional leading check and no missing
  or reordered prior check.
- Correction: add `p07-validation` as the first expected hardening check.
- Regression guard: the exact baseline, control, and hardening lists remain
  asserted independently.

## ERR-2026-10-06-RLX-001 — post-repair shape test retained a structural artifact

- Observation: the first complete test run after the Roget parser repair raised
  a `KeyError` because the unresolved-shape regression still expected `#100a`
  to exist as a lexical candidate.
- Explanation: parser version 4 correctly recognizes suffixed Roget head markers
  as structure, but the downstream visible-shape fixture still encoded the
  parser version 3 artifact.
- Discriminator: inspect the regenerated membership and unresolved-shape sets;
  confirm that head identifier `100a` exists structurally and that `#100a` no
  longer appears as an unresolved term.
- Correction: replace the stale shape expectation with a negative assertion
  that the structural marker is absent from lexical candidates.
- Regression guard: suffixed-head tests now require unique stable head IDs and
  explicitly reject representative suffixed markers as lexical memberships.
- Status: resolved in commit `bd3109a`; complete discovery passed 60 tests.

## ERR-2026-10-06-RLX-002 — deterministic receipt check used one wrong filename

- Observation: the first repeated-generation verifier requested
  `UNRESOLVED_SHAPE_RECEIPT.json`, while the recorded artifact is named
  `UNRESOLVED_SHAPE_AUDIT_RECEIPT.json`; six receipts were checked and the
  seventh check was incomplete.
- Explanation: the ad hoc verification inventory did not use the exact checked-in
  filename.
- Discriminator: enumerate the unresolved-shape output directory with `rg
  --files` and compare the requested path to the actual receipt name.
- Correction: rerun the entire dependency-ordered generation pipeline with the
  corrected seven-file inventory and fail on any missing path or changed hash.
- Regression guard: future reproducibility checks must derive or first validate
  the receipt inventory and use terminating path errors.
- Status: resolved; all seven receipts were byte-stable on the corrected run.

## ERR-2026-10-06-CTRL-001 — documentation validation used the bare host interpreter

- Observation: the first control-suite run after updating the logs passed 41 of
  42 tests but failed the dependency preflight because the bare host Python did
  not contain `jsonschema`.
- Explanation: the validation command did not select the prepared environment;
  this is the same interpreter-selection class recorded in ERR-004 and later
  P04/P06 occurrences rather than a change to the control records.
- Discriminator: query both interpreters for their executable path and pinned
  package version, then rerun identical test discovery.
- Correction: use `..\.venv\Scripts\python.exe`, which reports
  `jsonschema==4.26.0`; all 42 production-control tests pass.
- Regression guard: final handoff commands must name the prepared interpreter
  whenever the dependency preflight is in scope.
- Status: resolved in the same work session; the failed observation is retained.

## ERR-2026-10-06-RLX-003 — combined Git revision path crossed Windows path handling

- Observation: the first semantic-baseline validation stopped while reading the
  longest pinned receipt through `git show <commit>:<path>`; Git reported
  `Filename too long` before any schema fixture ran.
- Explanation: the combined revision expression was interpreted through a
  Windows path-handling limit. The tracked blob and working file were present.
- Discriminator: resolve the same path with `git ls-tree <commit> -- <path>` and
  read the returned object ID with `git cat-file blob`.
- Correction: baseline verification now separates path-to-object resolution from
  byte retrieval and requires the listed path to match exactly.
- Regression guard: all eight baseline inputs use the two-step blob method and
  are compared byte-for-byte with the working files.
- Status: resolved; the validator and all focused contract tests pass.

