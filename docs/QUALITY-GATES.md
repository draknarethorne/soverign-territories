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

PowerShell policy in Phase 1:

- blocking: `Error` severity findings
- non-blocking (tracked debt): `Warning` severity findings

### Data validation hook (pre-commit and pre-push)

- `tools/validators/validate_data.py` validates every schema-covered JSON file (gameplay cards, art identities, art pieces, art assembly cards) against its own schema and enforces cross-file integrity (card <-> art identity link is bidirectional, referenced pieces exist, generated outputs are unique)
- `tools/validators/test_validate_data.py` is a mutation self-test that corrupts a temp copy of `data/` and asserts the validator catches each case, so the gate cannot silently go dead
- the coverage report lists areas with no fitting schema yet (tracked debt, not hidden)

### CI quality workflow

- `.github/workflows/quality.yml`
- installs and runs pre-commit hooks in clean environment (including the data validation hook)
- runs on push/PR to `main`

### Retired: legacy schema workflow

- `.github/workflows/validate-schemas.yml` and the old pre-push script were removed: they only watched `docs/specs/*.json` (schemas moved to `data/schemas/`) and validated each schema against itself, so they never checked a single real card

## Temporary policy exceptions

Legacy documentation debt exists. Until style remediation is complete, markdownlint rules are selectively relaxed in `.markdownlint.json`.

These exceptions are intentional and temporary; they will be tightened by staged cleanup.

Legacy PowerShell formatting/style debt also exists in older generator and migration scripts.
Warnings are currently non-blocking while we retire that debt in scoped batches.

## Planned next phases

### Phase 2 — Governance hardening

- add release checklist and change-management docs
- ensure contributor workflow docs remain current
- add quality dashboards/checkpoint summaries as needed

### Phase 3 — Lint debt retirement

- clean docs in isolated style-only batches
- tighten markdownlint rules incrementally
- avoid mixing style rewrites with design/mechanics changes
