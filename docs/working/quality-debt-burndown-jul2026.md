# Quality Debt Burn-Down Plan — July 27, 2026

## Goal

Move from a stabilized **Phase 1 baseline** (gates passing) to tighter standards with minimal churn risk.

## Prerequisite: semantic truth before style work

Passing lint or normalizing formatting does not validate design quality, source-of-truth
ownership, data contracts, or MVP feasibility. Before the waves below, apply and close
the readiness gates in `archive-canon-reconciliation-jul2026.md`:

1. reconcile canonical MVP, combat, deck, tutorial, and hub documents;
2. validate the selected MVP data subset against `data/schemas/` and actual data files;
3. record a prototype/playtest feasibility decision.

Lint debt remains useful work, but it is not the first readiness gate.

## Current state (done)

- pre-commit baseline is active and passing
- markdownlint baseline is active with temporary rule relaxations
- PowerShell analyzer blocks on `Error`, reports `Warning`
- historical/stale audits were archived and indexed

## Next execution waves

## Wave 1 — Markdown debt reduction (safe docs-first)

Focus: reduce lint debt in active docs without touching game logic.

1. Normalize `docs/QUALITY-GATES.md`, `docs/README.md`, and root `README.md` to strict-clean state.
2. Trim/normalize long historical appendices in active files (move large historical prompt dumps to `docs/archive/` references where appropriate).
3. Fix table/link/reference anomalies in active design docs and legacy specification notes
	(high signal only); runtime schema contracts are in `data/schemas/`.

Exit criteria:

- no regressions in canonical docs
- reduced dependency on relaxed markdownlint rules

## Wave 2 — PowerShell warning backlog reduction

Focus: tooling hygiene without behavior changes.

1. Tackle scripts in `scripts/` first (active developer entrypoints).
2. Tackle `tools/generators/` second.
3. Keep each commit style-only and script-scoped.

Exit criteria:

- warning count materially reduced
- no script behavior changes unless explicitly documented

## Wave 3 — Tightening policy

1. Re-enable markdown rules incrementally (one rule family at a time).
2. Raise PowerShell warnings from non-blocking toward blocking by threshold.
3. Update `docs/QUALITY-GATES.md` and `docs/AUDIT-DOCUMENTATION-QUALITY-BRANDING-JUL2026.md` after each tightening step.

## Commit strategy

- Commit after each wave/batch.
- Keep commit messages explicit: "style-only", "lint policy tighten", "powershell warning cleanup".
- Avoid mixing architecture/design decisions with formatting debt.

## Night-run order

1. Wave 1.1: active docs strict-clean pass.
2. Wave 1.2: archive/historical content normalization.
3. Wave 2.1: scripts/ warnings batch.
4. Wave 2.2: tools/ warnings batch.
5. Wave 3.1: first markdown rule tighten + validation.
