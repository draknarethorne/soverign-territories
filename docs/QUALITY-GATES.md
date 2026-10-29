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
- `bin\check.cmd` now requires pre-commit explicitly; its old fallback was
  neither equivalent to the hook set nor quick, and ran live mutation tests.
  Missing tooling is an explicit error with the installation command.

The mutation self-test corrupts an isolated copy and verifies rejection.
It protects the validator itself, not just the current data. It remains
valuable for schema/validator changes and deep validation, but need not repeat
on every routine image-schema edit and again on push.

### CI quality workflow

- `.github/workflows/quality.yml`
- installs and runs pre-commit hooks in clean environment (including the data validation hook)
- runs on push/PR to `main`, or explicit `workflow_dispatch` for a selected
  branch. Feature-branch pushes without a main-targeting PR do not
  automatically run this workflow; do not claim remote coverage until a run
  exists and succeeds
- Windows matrix retains Python 3.12 and adds 3.13/3.14; image tooling recommends
  regular 64-bit CPython 3.14, without raising the source compatibility floor
- runs both routine and explicit `manual` hooks, preserving all former hook
  test coverage on GitHub runners
- installs pinned core image dependencies from `requirements.txt` and runs
  `bin\validate.cmd --quick` after both hook stages; optional Torch/LaMa
  dependencies and model downloads are not needed for those regression tests
- local validation and newly configured CI coverage are distinct: see the
  [runtime guide](art/original-photos.md#python-runtime-and-dependencies) for
  measured versions and local interpreter limitations

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
