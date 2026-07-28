# Release Checklist (Documentation + Data Baseline)

Use this checklist before tagging project milestones or major documentation baselines.

## 1) Canonical docs readiness

- [ ] `docs/README.md` source-of-truth matrix is accurate.
- [ ] `docs/game-bible.md` reflects current vision framing.
- [ ] MVP baseline docs are aligned (`docs/mvp/*`).
- [ ] Any superseded docs are moved to `docs/archive/`.

## 2) Data + schema contract readiness

- [ ] Schema files under `data/schemas/*.json` validate.
- [ ] Companion spec docs updated where required.
- [ ] Runtime data references canonical IDs and current structures.

## 3) Quality gates

- [ ] pre-commit hooks installed locally.
- [ ] `pre-commit run --all-files --show-diff-on-failure` passes.
- [ ] `scripts/Invoke-QualityChecks.ps1` passes.
- [ ] `scripts/Invoke-PrePushValidation.ps1` passes.
- [ ] GitHub Actions quality workflows are green.

## 4) Governance + security docs

- [ ] `CONTRIBUTING.md` reflects current workflow.
- [ ] `SECURITY.md` is present and accurate.
- [ ] `.github/CODEOWNERS` is current.
- [ ] `docs/QUALITY-GATES.md` is current.
- [ ] `docs/CHANGE-MANAGEMENT.md` is current.

## 5) Repository presentation

- [ ] GitHub About description matches current project phase.
- [ ] Topics are relevant and updated.
- [ ] README links use canonical org URL.

## 6) Publish

- [ ] Commit message clearly describes release baseline.
- [ ] Push to `main`.
- [ ] Add/update release notes if tagging.
