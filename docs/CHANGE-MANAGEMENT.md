# Change Management

This document defines the required sequence for design/system changes so docs, schemas, and tooling stay synchronized.

## Core rule

When a gameplay/system rule changes, update all impacted layers in order:

1. **Design canon** (`docs/design/*.md`, `docs/mvp/*.md`, or `docs/game-bible.md` summary)
2. **Schema contracts** (`data/schemas/*.json` and any companion documentation)
3. **Runtime/supporting data** (`data/**` as needed)
4. **Scripts/tooling** (`scripts/**`, `tools/**`, workflows)
5. **Validation and quality checks** (local hooks + CI)

## Required checklist for canonical rule changes

- [ ] Design intent and phase boundary are explicitly documented.
- [ ] One canonical source of truth is identified for formulas/rules.
- [ ] JSON schema contracts are updated.
- [ ] Companion docs are updated for human-readable context.
- [ ] Scripts and validators are aligned to the new contract.
- [ ] Pre-commit and CI checks pass.
- [ ] Change log/audit note updated when high-impact.

## Classification model

### Minor change

Examples:

- typo fixes
- wording clarification with no rule impact
- examples/screenshots only

Requirements:

- docs update only
- no schema/tool changes required

### Major change

Examples:

- formula changes (combat/progression/economy)
- MVP scope/phase boundary changes
- schema shape/property changes
- validation or workflow changes

Requirements:

- full checklist above
- explicit audit note in current working audit document

## Practical guardrails

- Do not mix architecture behavior changes with broad formatting-only rewrites.
- Keep style debt remediation in isolated commits.
- Prefer additive migration notes over destructive rewrites when preserving historical context.
- Archive superseded docs with `-SUPERSEDED` or `-HISTORICAL` suffixes.
