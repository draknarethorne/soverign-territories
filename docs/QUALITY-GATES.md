# Quality Gates

This document defines the repository quality contract and rollout stages.

## Objectives

- prevent avoidable formatting/hygiene drift
- enforce schema and script quality
- keep local and CI checks aligned
- harden quality incrementally without destabilizing architecture work

## Current gates (Phase 1 baseline)

### Pre-commit hooks

Configured in `.pre-commit-config.yaml`:

- file hygiene: large files, merge conflicts, YAML/JSON validity, EOF newline
- markdown linting via `.markdownlint.json`
- PowerShell analysis via `scripts/Invoke-QualityChecks.ps1`
- data/schema/link validation when data or validator files change

Routine commits do **not** run unit suites or mutation self-tests. Those run
explicitly during development and in CI. Hooks are restricted to `pre-commit`;
the installed pre-push hook has no selected checks, so pushing does not
repeat the commit's validation. No cached-success shortcut or hook bypass
is involved.

PowerShell policy in Phase 1:

- blocking: `Error` severity findings
- non-blocking (tracked debt): `Warning` severity findings

### Data validation hook (pre-commit only)

- `tools/validators/validate_data.py` validates every schema-covered JSON file (gameplay cards, art identities, art pieces, art assembly cards) against its own schema and enforces cross-file integrity (card <-> art identity link is bidirectional, referenced pieces exist, generated outputs are unique)
- the coverage report lists areas with no fitting schema yet (tracked debt, not hidden)

### Explicit deeper validation

- `cmd /c bin\check.cmd` runs routine checks across all files.
- `cmd /c bin\check.cmd --deep` additionally runs the `manual` hook stage:
  isolated full mutation tests plus workflow, backdrop, reference, generator,
  validator-isolation, likeness and codex unit suites.
- `python -m pre_commit run --hook-stage manual HOOK-ID --files PATH ...`
  selects an individual deep hook. Existing file filters still apply.
- Run the smallest relevant unit suites for each change before committing;
  moving them out of hooks does not waive testing.
- The broader image/launcher regressions remain available through
  `bin\validate.cmd`; `bin\validate.cmd --isolated --quick` is the bounded
  validator smoke suite. Neither is automatically run by commit/push.
- Preview relevant tests with `cmd /c bin\validate.cmd --changed HEAD --dry-run`,
  then execute with `cmd /c bin\validate.cmd --changed HEAD --check`.
  This includes tracked changes against the base plus non-ignored untracked
  files. Use a branch-point SHA instead of `HEAD` to cover an entire branch.
  Selection errors stop explicitly; a missing Git base never means success.
- `cmd /c bin\validate.cmd --scope workflow --dry-run` previews one subsystem;
  replace `--dry-run` with `--check` to execute. Other explicit scopes are
  `intake`, `library`, `data`, `quality`, and `full`. Explicit scopes are a
  developer override; automatic selection includes shared consumers.
- `cmd /c bin\validate.cmd --full` runs full regressions plus one full
  **isolated** mutation pass. `--quick` now means only the isolated mutation
  smoke suite, not a full regression run followed by smoke mutations.
  The no-argument launcher retains the full regression/audit contract.
- `bin\check.cmd` now requires pre-commit explicitly; its old fallback was
  neither equivalent to the hook set nor quick, and ran live mutation tests.
  Missing tooling is an explicit error with the installation command.

The mutation self-test corrupts an isolated copy and verifies rejection.
It protects the validator itself, not just the current data. It remains
valuable for schema/validator changes and deep validation, but need not repeat
on every routine image-schema edit and again on push.

### CI quality workflow

- `.github/workflows/quality.yml`
- installs and runs routine pre-commit hooks in a clean environment (including data validation)
- runs on every branch push, PRs targeting `main`, or explicit
  `workflow_dispatch` for a selected branch. Concurrency cancels superseded
  runs for the same ref; a push and its PR can still produce separate runs.
  Do not claim remote success until a run exists and succeeds
- Windows matrix retains Python 3.12 and adds 3.13/3.14; image tooling recommends
  regular 64-bit CPython 3.14, without raising the source compatibility floor
- runs routine hygiene/data hooks and `bin\validate.cmd --ci`. Branch pushes
  compare the event's before/after commits; PRs compare the merge base with
  the PR head. Checkout includes history. Main pushes, manual dispatch and
  new branches without a previous commit use full acceptance coverage
- the shared [selector](../tools/validators/quality_selection.py) prints
  reasons and exact commands, then reports elapsed time/exit per subprocess.
  Documentation-only changes need no unit/mutation suite. Reference/workflow
  changes select workflow/generator tests; shared `comfy_workflows.py` and
  prompt generation include art/library consumers. Intake changes include
  retained/rebase and exported-workflow consumers. Other art/data changes include their broad
  consumers, but do not test validator mutations. Schema/validator changes
  and unclassified infrastructure paths conservatively use full coverage.
  No timing-based success cache or image-quality inference is involved
- selected subsystem runs include the lightweight quality/isolation guards.
  Full coverage runs isolated mutations once and the consolidated regression
  launcher once, not the manual hooks a second time
- installs pinned core image dependencies from `requirements.txt`; optional
  Torch/LaMa dependencies and model downloads are not needed for those
  regression tests. Real neural inference throughput, visual quality and
  sandbox/Production acceptance are not CI claims
- `tools/validators/test_quality_gates.py` compares all active `test_*.py`
  modules under `tools` with the launcher's explicit modules/library discovery
  and fails if a new module is omitted. New tests elsewhere require extending
  that inventory contract. Library test discovery includes reset, audit and
  diagnostics without duplicating them in a separate CI hook pass
- local validation and newly configured CI coverage are distinct: see the
  [runtime guide](art/original-photos.md#python-runtime-and-dependencies) for
  measured versions and local interpreter limitations

### Test scratch

The test launchers (`validate`, `test`, `check`) scope `TEMP`, `TMP`, and
`TMPDIR` to the absolute ignored repository `tmp` directory. Child Python
processes and default `tempfile` fixtures inherit it; the environment is
restored when the launcher returns. Explicit fixtures must also stay below
ignored scratch. The retained-preparation fixture no longer passes the
repository root as `TemporaryDirectory(dir=...)`.

Use the supported launcher for default scratch routing. A bare
`python -m unittest ...` outside it still uses the caller's tempfile
environment; the launchers do not install a global Python monkeypatch.
Generated untracked trees can trigger editor/Git scans, but are not
automatically tracked or committed. Do not mask misplaced output with a
blanket root `tmp*` ignore rule.

### Retired: legacy schema workflow

- `.github/workflows/validate-schemas.yml` and the old pre-push script were removed: they only watched `docs/specs/*.json` (schemas moved to `data/schemas/`) and validated each schema against itself, so they never checked a single real card

## Temporary policy exceptions

Legacy documentation debt exists. Until style remediation is complete, markdownlint rules are selectively relaxed in `.markdownlint.json`.

These exceptions are intentional and temporary; they will be tightened by staged cleanup.

Legacy PowerShell formatting/style debt also exists in older generator and migration scripts.
Warnings are currently non-blocking while we retire that debt in scoped batches.

## Planned next phases

### Phase 2 — Governance hardening

- keep the release checklist ([RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md)) and change-management ([CHANGE-MANAGEMENT.md](CHANGE-MANAGEMENT.md)) docs current
- ensure contributor workflow docs remain current
- add quality dashboards/checkpoint summaries as needed

### Phase 3 — Lint debt retirement

- clean docs in isolated style-only batches
- tighten markdownlint rules incrementally
- avoid mixing style rewrites with design/mechanics changes
