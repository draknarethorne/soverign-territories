# Documentation Reset Plan (July 2026)

**Date**: 2026-07-27  
**Status**: Proposed and partially applied  
**Goal**: Make the dream smaller without making the vision smaller.

---

## Why this reset

Recent independent review feedback confirms four recurring issues:

1. **MVP boundary drift** (future systems leak into implementation planning)
2. **Canonical source ambiguity** (same rules duplicated across files)
3. **Tone mismatch** (some monetization language conflicts with player-respect philosophy)
4. **Docs/tools misalignment risk** (specs, scripts, and design docs can diverge)

This reset enforces a practical split:

- `docs/game-bible.md` = **vision and principles**
- `docs/mvp/*` = **build-order and delivery reality**
- `docs/design/*` = **system-level executable design rules**
- `data/schemas/*.json` = **data contract for scripts/tools/runtime validation**

---

## Authoritative rules (effective immediately)

### 1) MVP timeline and scope authority

- **Authoritative schedule/scope**: `docs/mvp/solo-dev-realistic-mvp.md`
- `docs/mvp/mvp-scope-final.md` remains useful for dependency decomposition, but any schedule conflict defaults to the solo realistic plan.

### 2) Progression authority

- **Authoritative progression/deck constraints**: `docs/design/deck-progression-rules.md`
- `docs/game-bible.md` should reference, not duplicate exact formulas.

### 3) Combat authority

- **Authoritative combat formulas by phase**: `docs/design/combat-calculation-spec.md`
- `docs/game-bible.md` should keep high-level framing only.

### 4) Schema/tooling authority

- **Authoritative data contracts**: `data/schemas/*.json`
- Scripts in `scripts/` and validators/generators/importers in `tools/` must treat schema files as source of truth.

---

## MVP firewall (what is in/out)

### MVP (build now)

- Card data + collection UI
- Deck construction and validation
- 8x8 tactical battles
- Single-player campaign/tutorial loop
- Basic reward and progression loop

### Post-MVP (documented, not implemented now)

- Territory/World map conquest loops
- Alliance wars and social warfare systems
- Auction house/trade economy
- Advanced live-service systems and heavy event cadence

---

## Documentation restructuring actions

### Completed in this pass

- Updated `docs/README.md` tagline and quick-start sequencing to MVP-first workflow.
- Added canonical source matrix in `docs/README.md`.

### Next actions (high-priority)

1. Add a short **"MVP Firewall" note near the top of `docs/game-bible.md`** clarifying that implementation detail is delegated to `mvp/`, `design/`, and `specs/`.
2. Reduce duplicate formulas in `game-bible.md` by replacing deep mechanics with references to:
   - `design/deck-progression-rules.md`
   - `design/combat-calculation-spec.md`
3. Tone pass on monetization language in `game-bible.md`:
   - Replace exploitative framing with player-respect framing
   - Keep revenue strategy in internal/business framing, not core design identity
4. Add/refresh `docs/specs/README.md` section: "Schema Change Protocol" (required for script/tool updates).

---

## Scripts and tools alignment protocol

When changing a game rule that affects data:

1. Update design source (`docs/design/*.md`) first.
2. Update schema contract (`data/schemas/*.json`) second.
3. Update generators/importers/validators/scripts third.
4. Run validation scripts and data audits.
5. Only then update high-level narrative references in `game-bible.md`.

**Rule**: No script/tool logic should rely on prose in `game-bible.md` for numeric behavior.

---

## Archive policy

A document is archive-candidate if any of the following are true:

- It is superseded by a newer canonical file with same purpose
- It mixes aspirational roadmap with active implementation instructions without phase markers
- It duplicates formulas now owned by `docs/design/*` or `docs/specs/*`

**Archive process**:

- Move to `docs/archive/`
- Add one-line supersession note at top:
   - "Superseded by [new-canonical-path], YYYY-MM-DD"

---

## Success criteria for this reset

1. A new contributor can identify **one authoritative file per subsystem** in <10 minutes.
2. MVP contributors can follow a scope-safe path from docs without accidentally implementing Phase 2-3 systems.
3. Schema/tooling changes are traceable from design rule -> schema -> script/tool.
4. `game-bible.md` reads as coherent vision narrative, not conflicting implementation spec.

## Reconciliation prerequisite

Documentation readiness cannot be inferred from archive moves or passing lint. Before
claiming this reset is complete, apply the dispositions and feasibility gates in
`docs/working/archive-canon-reconciliation-jul2026.md` and correct the active canonical
sources it identifies.

---

## 2-week execution checkpoint

By next review checkpoint, deliver:

- `game-bible.md` MVP firewall + de-dup pass for progression/combat sections
- monetization tone rewrite pass
- schema/tooling synchronization checklist integrated into docs hub
- archive moves for any newly superseded implementation-planning docs
