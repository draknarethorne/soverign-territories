# 🔍 Documentation + Quality + Branding Audit — July 27, 2026

## Executive Summary

This audit records:

1. what was completed in today’s architectural reassessment,
2. what remains before broader lint/quality hardening,
3. how to adopt the stronger quality patterns already used in other Draknare Thorne repositories,
4. how to align GitHub metadata and project presentation with the Thorne/Viper style.

**Primary outcome today**: MVP architecture and canon rules were successfully re-aligned and pushed (`317700a`).

---

## ✅ What was completed today (locked in)

### Major documentation realignment commit

**Commit**: `317700a` on `main`  
**Message**: `Reassess and realign MVP docs`

### Files changed in that pass

- `docs/README.md`
- `docs/design/combat-calculation-spec.md`
- `docs/design/deck-progression-rules.md`
- `docs/game-bible.md`
- `docs/mvp/mvp-scope-final.md`
- `docs/specs/README.md`
- `docs/working/mvp-architecture-reassessment-jul2026.md` (new)

### Architectural corrections completed

- MVP baseline clarified as deterministic tactical core (HP/Mana/ATK/DEF).
- MVP scope creep reduced (crafting + async arena moved to Phase 1.1 stretch).
- Progression canon normalized (including Uncommon = 2 and single-hero MVP rule).
- Cross-doc formula ownership clarified (combat/progression canon in focused design docs).
- Schema change workflow strengthened (design → schema → companion docs → scripts/tools → validation).
- Monetization language guardrails improved toward player-respect framing.

---

## ✅ Phase 1 execution update (completed)

The planned Phase 1 baseline has now been implemented in-repo:

- ✅ `.pre-commit-config.yaml`
- ✅ `.markdownlint.json`
- ✅ `.editorconfig`
- ✅ `PSScriptAnalyzerSettings.psd1`
- ✅ `scripts/Invoke-QualityChecks.ps1`
- ✅ `scripts/Invoke-PrePushValidation.ps1`
- ✅ `.github/workflows/quality.yml`
- ✅ `CONTRIBUTING.md`
- ✅ `SECURITY.md`
- ✅ `.github/CODEOWNERS`
- ✅ `docs/QUALITY-GATES.md`
- ✅ `docs/CHANGE-MANAGEMENT.md`
- ✅ `docs/RELEASE-CHECKLIST.md`

### Overnight iteration checkpoint (same date)

- ✅ Full repository quality hooks now execute successfully via:
   - `python -m pre_commit run --all-files`
- ✅ Baseline enforcement now stable on Windows shells (PowerShell hook runtime corrected).
- ✅ Repository-wide hygiene normalization applied (EOF newline + trailing whitespace cleanup across legacy files).
- ✅ Phase-1 gating strategy finalized:
   - blocking: file hygiene, YAML/JSON validity, markdownlint baseline, PowerShell analyzer errors
   - tracked debt (non-blocking in this phase): markdown style strictness and PowerShell warning-level backlog

---

## ⚠️ Remaining gaps (post-phase-1)

### 1) Lint/style debt still present

- `docs/design/combat-calculation-spec.md` still contains significant markdown style/lint debt from legacy formatting.
- This is primarily formatting debt, not architecture logic debt.
- Recommend handling as **separate style-only pass** to avoid mixing behavior and formatting changes.

### 2) Quality hardening is now active (next step = tighten over time)

Current Sovereign Territories repo state:

- ✅ Baseline quality toolchain present
- ✅ Quality CI workflow present (`.github/workflows/quality.yml`)
- ✅ Existing schema validation workflow retained (`.github/workflows/validate-schemas.yml`)
- 🔄 Next: retire lint/style debt in structured batches and tighten relaxed markdown rules incrementally

### 3) Metadata and brand consistency gap

Current repository **About** text is still generic:

- `Idea for a new mobile strategy card and rpg game.`

This undersells current project identity and does not match Thorne/Viper-quality presentation style.

### 4) Debt inventory to retire in Phase 1.1+

The baseline now passes, but quality debt remains and is intentionally tracked for incremental cleanup:

- Markdown strictness backlog in long-form legacy docs (rule-tightening deferred intentionally)
- PowerShell analyzer warning backlog concentrated in older generator/migration scripts

Retirement strategy:

1. perform style-only batches by directory/topic,
2. keep behavior and balancing changes separate from formatting,
3. tighten markdownlint and PowerShell severity policies in controlled increments.

---

## 📚 Cross-repo quality patterns to adopt

Reference repos reviewed:

- `draknarethorne/thorne-ui`
- `draknarethorne/thorne-timer`
- `draknarethorne/viper-health`

### Notable patterns observed

1. **Pre-commit as first-line guardrail**
   - baseline hygiene hooks
   - language/tool specific quality checks
   - staged checks (fast pre-commit, heavier pre-push)

2. **CI as non-bypassable authority**
   - CI runs quality gates from clean environment
   - local hooks accelerate feedback but do not replace CI truth

3. **Explicit contributor quality contract**
   - documented setup and commands
   - clear policy for what runs locally vs CI

4. **Pragmatic markdown policy**
   - lint enabled, but noisy rules selectively relaxed until legacy debt is paid down

5. **Repo identity + guide structure**
   - strong README framing
   - explicit docs index
   - contributor and release process guides

---

## 🧭 Recommended rollout for Sovereign Territories (staged)

## Phase 0 — Document-first (this audit)

- ✅ Complete this audit and scope ownership notes.
- ✅ Keep architecture decisions locked before broad lint rewrites.

## Phase 1 — Safe quality baseline (no mass reformat)

Add a conservative baseline with minimal risk:

1. `.pre-commit-config.yaml`
   - `pre-commit-hooks`: `check-added-large-files`, `check-merge-conflict`, `check-yaml`, `end-of-file-fixer`, `trailing-whitespace` (exclude Markdown initially).
2. `.markdownlint.json`
   - start with practical rule set similar to existing Thorne repos (temporarily relax noisy rules where needed).
3. Root `.editorconfig`
   - line endings, charset, whitespace normalization.
4. `PSScriptAnalyzerSettings.psd1`
   - baseline for PowerShell scripts in `scripts/` and `tools/`.
5. CI quality workflow
   - run pre-commit hooks in CI (`pre-commit run --all-files --show-diff-on-failure`).

## Phase 2 — Governance docs

Add repo-level quality/governance docs:

- `CONTRIBUTING.md` (setup, local commands, CI expectations)
- `SECURITY.md` (reporting process and dependency policy)
- `.github/CODEOWNERS` (ownership clarity)
- `docs/QUALITY-GATES.md` (what is enforced now vs later)

## Phase 3 — Style debt retirement

- Batch-fix legacy markdown lint debt by directory (e.g., `docs/design/` first).
- Keep each batch style-only; no design/mechanics changes mixed in.
- Tighten markdownlint rules progressively as debt falls.

---

## 🧱 Guide structure recommendation (Thorne/Viper style fit)

Suggested minimum guide set for this repository:

1. `README.md` — project identity + quick start + roadmap snapshot.
2. `docs/README.md` — canonical docs index and source-of-truth matrix.
3. `CONTRIBUTING.md` — contributor workflow + quality contract.
4. `SECURITY.md` — security and disclosure baseline.
5. `docs/QUALITY-GATES.md` — quality policy and tool stages.
6. `docs/RELEASE-CHECKLIST.md` — release hygiene and artifact checks.
7. `docs/CHANGE-MANAGEMENT.md` — design → schema → tooling sync protocol.

---

## 🏷️ GitHub metadata + presentation alignment

### Recommended About description (Sovereign Territories)

> Campaign-first hybrid strategy card game: deck-building + tactical 8x8 battles now,
> territorial conquest and empire automation in later phases.
> Built in the Draknare Thorne / Thorne / Viper quality style.

### Recommended repository topics

- `unity`
- `csharp`
- `tactical-rpg`
- `deckbuilding`
- `strategy-game`
- `game-design`
- `nakama`
- `json-schema`
- `solo-dev`

### Profile/presentation consistency checklist (manual GitHub update)

For each repo in `draknarethorne`:

- [ ] About text follows clear identity + scope + quality style.
- [ ] Pinned README opening matches project maturity and current roadmap phase.
- [ ] Topics are specific and searchable.
- [ ] Links/reference paths use current org/repo canonical URL.
- [ ] Contributor/security docs present where appropriate.

---

## 🔜 Next execution steps (carry-forward plan)

1. Capture a formal debt report for markdown + PowerShell warning backlog (by file and rule class).
2. Execute lint/style remediation in isolated documentation-only batches.
3. Execute PowerShell warning remediation in tooling-only batches.
4. Tighten markdownlint rules as debt is reduced.
5. Raise PowerShell warning policy from non-blocking to blocking once backlog is under threshold.
6. Update GitHub About + topics for `soverign-territories` and then harmonize across org repos.

---

## 🗂️ Audit directory sweep decisions (July 27, 2026)

To reduce active-doc noise and remove stale/contradictory baseline assumptions from root `docs/`, the following were moved to `docs/archive/`:

- `AUDIT-BASE-SET-INVENTORY-JAN2026.md` → `archive/AUDIT-BASE-SET-INVENTORY-JAN2026-SUPERSEDED.md`
- `AUDIT-DATA-DIRECTORY-JAN2026.md` → `archive/AUDIT-DATA-DIRECTORY-JAN2026-SUPERSEDED.md`
- `AUDIT-STARTER-CARDS-JAN2026.md` → `archive/AUDIT-STARTER-CARDS-JAN2026-SUPERSEDED.md`
- `DOCUMENTATION-AUDIT-JAN2026.md` → `archive/DOCUMENTATION-AUDIT-JAN2026-SUPERSEDED.md`
- `COMPLETION-DATA-DOCS-SEPARATION-JAN2026.md` → `archive/COMPLETION-DATA-DOCS-SEPARATION-JAN2026-HISTORICAL.md`

Rationale:

- these files are historically valuable but no longer canonical for current MVP architecture and quality policy,
- several assumptions are now outdated relative to July 2026 canonicalization,
- archive naming now explicitly signals superseded vs historical reference status.

---

## Semantic reconciliation update

The quality baseline and archive moves do **not** prove documentation truth or MVP
feasibility. A subsequent evidence pass read every archived document and compared its
claims to the active canonical sources.

### Findings

- Archived reports often used ready/complete claims while retaining incompatible combat,
   scope, map, monetization, and schedule assumptions.
- Active canonical documents also retained substantial drift, including a feature-heavy
   solo MVP, exploration and persistent-health tutorials, and mismatched schema paths.
- Runtime schemas are located in `data/schemas/`; references that designate
   `docs/specs/` as the machine-readable contract are stale.

### Corrective work completed

- Created `docs/working/archive-canon-reconciliation-jul2026.md` with a disposition for
   every archived document, retained insights, active-document actions, and readiness gates.
- Replaced the active MVP scope, dependency, combat, deck, tutorial, map-mode, Bible, and
   documentation-hub sources with a shared local-first baseline.
- Reduced the feasible baseline to a small card subset, a one-hero six-card formation,
   deterministic 8×8 PvE, a short authored campaign, local saves, and playtesting.

### Remaining blocking evidence

- Validate the selected starter collection, campaign encounters, and reward data against
   actual `data/` files and `data/schemas/` contracts.
- Confirm the remaining implementation/design documents and schema companions do not
   reintroduce contradictory MVP requirements.
- Complete a prototype and external playtest before claiming implementation readiness.

## Audit status

- **Date**: July 2026
- **Auditor mode**: Sovereign Beast Mode (design architecture + documentation)
- **Status**: Quality baseline passes; semantic reconciliation is active and implementation
   readiness remains unverified.
- **Blocking risk**: Scope/data-contract coherence remains a blocker until the readiness
   gates in the reconciliation document are satisfied.
