# Archive-to-Canon Reconciliation (July 2026)

**Status:** Evidence review complete; canonical correction work remains in progress.  
**Purpose:** Record what each archived document claimed, where its useful information now belongs, and which active documents must be corrected before implementation readiness can be claimed.

## Scope and method

This review read every Markdown file in `docs/archive/` against the July 2026 MVP baseline in `mvp-architecture-reassessment-jul2026.md`. It does **not** treat an archived file as reconciled merely because it was moved: a disposition must name its authoritative replacement and any remaining carry-forward action.

### Current authority

| Concern | Authoritative source |
| --- | --- |
| Long-term player promise and phased vision | `docs/game-bible.md` |
| MVP scope and delivery realism | `docs/mvp/solo-dev-realistic-mvp.md` |
| MVP dependency plan and acceptance checks | `docs/mvp/mvp-scope-final.md` |
| Combat rules | `docs/design/combat-calculation-spec.md` |
| Deck and rarity constraints | `docs/design/deck-progression-rules.md` |
| Runtime validation contracts | `data/schemas/*.json` |

> **Schema correction:** Runtime schemas are under `data/schemas/`, not `docs/specs/`. Any active document naming `docs/specs/` as the contract location is stale and must be updated or redirected.

## Archive disposition matrix

| Archived document | Disposition | What remains useful | Canonical destination / active action |
| --- | --- | --- | --- |
| `AUDIT-BASE-SET-INVENTORY-JAN2026-SUPERSEDED.md` | Superseded inventory snapshot | Historical inventory methodology only | Validate current manifests and card JSON files before making inventory claims; do not reuse its counts in active docs. |
| `AUDIT-DATA-DIRECTORY-JAN2026-SUPERSEDED.md` | Superseded structure audit | Data-versus-documentation separation rationale | `README.md`, `docs/README.md`, and `docs/working/documentation-reset-plan-jul2026.md` must name `data/schemas/` as the contract location. |
| `AUDIT-STARTER-CARDS-JAN2026-SUPERSEDED.md` | Superseded content audit | Starter-card validation questions | Revalidate actual starter-deck data against `data/decks/` and current card files before documenting tutorial rewards. |
| `COMPLETION-DATA-DOCS-SEPARATION-JAN2026-HISTORICAL.md` | Historical milestone | Decision to keep runtime data outside docs | Retain as history; repair current links and paths rather than relying on milestone claims. |
| `DOCUMENTATION-AUDIT-JAN2026-SUPERSEDED.md` | Superseded audit | Early duplicate/ownership findings | Replaced by this reconciliation and the July quality audit; no implementation claims retained. |
| `bible-reorganization-plan.md` | Superseded plan | Intent to make the Bible navigable | `docs/game-bible.md` still needs a phased-vision reduction; links must point to focused canonical documents rather than duplicate rules. |
| `CAMPAIGN-MODE-RESTRUCTURE.md` | Extract insight first | Need for a clear campaign progression model | Preserve the linear campaign principle; reject its outdated map scale, content volume, and feature assumptions. Encode the baseline in `mvp-scope-final.md`. |
| `CLEANUP-SUMMARY.md` | Historical only | Trace of prior cleanup actions | Do not treat as readiness evidence. Current status belongs in the July audit and this reconciliation. |
| `documentation-status-report.md` | Superseded status report | Earlier cataloguing work | Replace stale counts and "complete" claims in the docs hub after verifying filesystem data. |
| `final-mvp-review-dec2025-SUPERSEDED.md` | Superseded review | Solo-dev risk framing | Current feasibility verdict must supersede its feature-heavy MVP recommendation. |
| `mvp-scope.md` | Superseded scope | Original feature decomposition | `mvp-scope-final.md` must become a small dependency-driven baseline, not inherit its 8-week/full-feature assumptions. |
| `reorganization-status.md` | Historical only | Reorganization history | No active planning value; `docs/README.md` owns navigation and canonical sources. |
| `roadmap.md` | Superseded roadmap | Long-term phases as aspirations | Reframe future work behind decision gates; `game-bible.md` owns vision, `solo-dev-realistic-mvp.md` owns the current schedule. |
| `tutorial-gap-resolutions.md` | Superseded tutorial detail | Specific onboarding failure modes | Preserve the principle of short, optional, learn-by-doing onboarding; rewrite `mvp/tutorial-flow.md` to the MVP baseline before treating it as canonical. |

## Findings carried into active corrections

### 1. Archive claims were frequently overconfident

Several archived reports declared systems "complete," "ready," or implementation-safe while their source assumptions diverged on combat, deck composition, map complexity, content quantities, and monetization. Passing quality gates or moving those reports to archive therefore cannot establish implementation readiness.

### 2. The active corpus still repeats the same drift

The principal documents currently retain incompatible material:

- `game-bible.md` mixes MVP framing with production AFK economies, alliance warfare, multi-hero armies, aggressive live-service mechanics, and deployment architecture.
- `solo-dev-realistic-mvp.md` labels 100 cards, 60–80 battles, fusion, equipment, crafting, and Arena as must-have even though those cannot fit the stated part-time MVP.
- `mvp-scope-final.md` still contains map exploration, persistent HP/Temple systems, 28-step onboarding, broad stores, and obsolete 8-week assumptions.
- `combat-calculation-spec.md` correctly names the deterministic model but incorrectly defers its HP/Mana foundations and retains PvP as MVP work.
- `deck-progression-rules.md` contains arithmetic and copy-limit violations, plus future unlocks and elemental counter language.
- `tutorial-flow.md`, `map-tier-progression.md`, and `gameplay-modes-spec.md` describe systems that are incompatible with the linear-campaign, one-hero baseline.

### 3. Feasibility verdict before correction

The project vision is feasible **as a multi-phase product**, but the currently documented MVP is not feasible for a first-time, part-time solo developer in 16–24 weeks. A feasible baseline is:

1. local data loading and save state;
2. one small, validated starter collection and one legal starter formation;
3. deterministic six-unit, one-hero, 8×8 PvE combat;
4. a short linear campaign with hand-authored encounters;
5. basic rewards, deck validation, and a compact onboarding path;
6. playtest instrumentation and a clear go/no-go review.

Card fusion, persistent HP/Mana recovery, equipment, crafting, PvP, complex stores, broad achievement/codex systems, map exploration, economy deployment, and backend services are optional later gates—not baseline requirements.

## Readiness gates

Do not call the MVP "ready for Unity" until all gates pass:

- [ ] Canonical MVP, combat, deck, tutorial, and docs hub documents agree on the baseline.
- [ ] Data contracts are confirmed in `data/schemas/` and mapped to the selected MVP subset.
- [ ] Starter deck, card inventory, campaign encounters, and reward data are validated against real files.
- [ ] The baseline has a small playtestable vertical slice and measurable acceptance checks.
- [ ] Phase 1.1 and later features are explicitly separated from MVP work.

## Next corrections in dependency order

1. Rewrite `solo-dev-realistic-mvp.md` and `mvp-scope-final.md` around the feasible vertical slice.
2. Make combat and deck rules internally consistent, then verify their data contracts.
3. Replace the tutorial/map-mode documents with baseline-compatible versions or label them future-only.
4. Reduce the game bible to vision, explicit phase labels, and references to canonical details.
5. Update `README.md`, `docs/README.md`, the archive index, reset plan, and quality audit only after the factual sources are corrected.
