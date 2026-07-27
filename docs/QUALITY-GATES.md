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

### Pre-push hook

- `scripts/Invoke-PrePushValidation.ps1` runs schema self-validation checks

### CI quality workflow

- `.github/workflows/quality.yml`
- installs and runs pre-commit hooks in clean environment
- runs on push/PR to `main`

### Existing schema workflow

- `.github/workflows/validate-schemas.yml`
- retained to preserve existing schema contract checks

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
