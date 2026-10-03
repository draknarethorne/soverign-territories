# Art ↔ Gameplay Reconciliation Plan (October 2026)

**Status:** Active plan · grounded in a full re-read of the docs suite + the art pipeline built Sep–Oct 2026.
**Purpose:** Capture how the top-down design vision and the bottom-up art pipeline diverged, and the ordered,
actionable tasks to bring them back together — without re-litigating settled scope.
**Companion authority:** `docs/working/archive-canon-reconciliation-jul2026.md` (July scope reset) remains the
MVP-scope authority; this doc is specifically about the **art pipeline ↔ gameplay-data ↔ schema** seam that
the July reset predates and did not cover.

---

## 1. The reconciled understanding (not a contradiction — a staged vision)

Three planning layers exist. They are **not** in conflict once read as a timeline rather than competing specs:

| Layer | Where | What it is | Correct reading |
| --- | --- | --- | --- |
| **Legacy 140-card MVP** | `docs/design/complete-card-series-mvp.md`, `docs/codex/base-set/COMPLETE-CARD-LIST.md`, `docs/design/assets.md` | Old roster (Aria/Thalor/Gaia…), 6–7 elements, pre-art-pipeline | **Superseded.** Already migrated into `data/cards/sovereign-dawn/` as labeled legacy content (`SD-041`–`SD-219`). Mine for unit/tactic/building ideas; don't treat its roster or art guidance as current. |
| **Drakn-sisters ideation** | `docs/codex/heroes/ideation_codex.md` + everything under `data/art/` | 10 elements · 30 heroes (10 sisters + 10 bound + 10 dragons) · 7th "Transcendent" tier · the Sundering storyline | **The long-horizon vision.** Deliberately larger than any one release — a multi-generation roster (Pokémon-style staged introduction). The art phase proved we can *produce* art for all of it; it does not claim all of it ships at once. |
| **July 2026 feasible MVP** | `docs/mvp/solo-dev-realistic-mvp.md`, `mvp-scope-final.md`, `working/mvp-architecture-reassessment-jul2026.md` | 18–30 cards, a meaningful starter deck, deterministic 8×8 PvE, elements as visual identity | **The first shippable slice.** Will use a *subset* of elements (3–4, not 10) drawn from the proven roster. |

**The resolved tension:** the earlier "exactly one hero" MVP line was premature — it predated the art pipeline,
when hand-drawing every card made a large roster infeasible. Now that art is data-driven and manageable, the MVP
can be "a meaningful deck from 3–4 elements" instead of "one hero." That is a **scope *refinement*, not a reversal** —
record it, don't reopen the whole scope debate.

**Action A1 (decision to record, owner = you):** State, in `game-bible.md` or the MVP scope doc, which **3–4
elements** seed the first Sovereign Dawn release and roughly how many cards per element. This unblocks every
downstream "what do I actually build first" question. *(Not blocking the art work; blocking the balance work.)*

---

## 2. The central technical finding: art data has forked from gameplay data

This is the real "schemas fighting each other" issue, and it is confirmed, not hypothetical.

**The same hero's palette/physique exists in two files, and they have already diverged:**

| File | Role | Palette/physique content |
| --- | --- | --- |
| `data/cards/sovereign-dawn/heroes/hero-drakness-thorne.json` | **Gameplay card** | Full `art.palette` + `art.physique` block — *but stale*: hair "obsidian-black with amethyst ribbons", build "elf-like with elongated proportions" |
| `data/art/heroes/drakn-sisters/drakness-thorne.json` | **Art-pipeline identity** (drives `gen_prompt.py`) | Full `art.palette` + `art.physique` — the *live* one: hair "black with espresso depth + plum-amethyst face-framing streaks", build "long-limbed" |

Only the second file feeds generation. The first is an unconsumed, drifted copy. Every one of the 10 sisters'
gameplay cards carries this divergent duplicate.

**Why it happened (and it's fine that it did):** early on, the schema was authored for gameplay only — art was
assumed to be hand-drawn, so a loose `art` block on the card seemed harmless. Once prompts went data-driven, the
real art source of truth moved to `data/art/` and the card's `art` block silently fell out of date.

**The fix is a clean separation of concerns, which `codex-schema.json` already half-anticipates:**

- `data/schemas/codex-schema.json` already has an `art` block with `portraitAsset`, `fullArtAsset`,
  `shinyPortrait` (asset *references* — correctly game-side, since the client loads them) **plus** a full
  `palette`/`physique` (art *direction* — which duplicates `data/art/`).
- `data/schemas/card-schema.json` is **already self-labeled `DEPRECATED`** and points to codex-schema — so there
  is really *one* intended card schema, not two fighting. But it is **not** cheap to delete: 22 files reference it
  (mostly archived or themselves-stale docs) **and** a CI workflow names it (see finding below). Treat removal as
  a deliberate reference-sweep task, not a quick delete. It is harmless where it sits (nothing loads it) — the
  priority is *enforcing* codex-schema, not erasing the deprecated file.

### New finding: card validation in CI is dead

`.github/workflows/validate-schemas.yml` only triggers on changes to `docs/specs/*.json` — but the Jan 2026
migration moved every schema to `data/schemas/`, so **the workflow never fires**. Worse, even if it ran, each
line is `ajv validate -s X -d X` (validates a schema *against itself*), so it **never validates a single real
card** against its schema. Net: there is currently **no enforcement** that `data/cards/sovereign-dawn/*.json`
conforms to `codex-schema.json`. Task B2 below is the replacement.

### The decision this needs (Action B1)

Pick the single source of truth for art *direction* (palette/physique) and make the other side a reference:

- **Recommended:** `data/art/heroes/<group>/<slug>.json` is the **sole** source of art direction (palette,
  physique, signature pieces). The gameplay card keeps only **asset-reference** art fields
  (`portraitAsset`/`fullArtAsset`/`shinyPortrait`) that point at *rendered output*, plus a one-line
  `artIdentity` pointer to the art file. Delete the duplicated `palette`/`physique` from the 10 gameplay cards.
- This is already the *stated* intent — `drakness-thorne.json`'s own notes say: *"The SD-001 game card should
  eventually keep only game data (stats/abilities/lore) plus any art attributes it intentionally OVERRIDES."*
  B1 just finishes that intent and makes it a rule.

**Net rule:** *gameplay data and art-direction data never both define the same attribute.* The card schema owns
mechanics + asset references; the art schema owns look. They meet only at asset-reference strings.

---

## 3. Actionable task list (ordered by leverage ÷ effort)

### Tier 0 — Low-hanging fruit (safe, bounded, do now)

- [x] **F1 — Surface the art pipeline in the docs hub.** `docs/README.md` never references `data/art/README.md`,
  `docs/art/*`, or `ideation_codex.md`, so the entire art system + the vision roster are invisible top-down.
  *(Handled in this pass.)*
- [ ] **F4 — Refresh or archive `docs/design/assets.md`.** Dated Dec 2024, "no assets created yet," written
  entirely against the old 140-card/old-roster model. Its *category scaffold* (card frames, icons, map tiles,
  battle UI, menus) is genuinely useful for the "beyond cards" art you'll need — but its roster/counts/colors are
  wrong. Either stamp it `-SUPERSEDED` and write a lean replacement, or update the roster-specific parts in place.

> **Downgraded from Tier 0 after investigation:** retiring `card-schema.json` + its 4-element enum ghost looked
> trivial but is not — 22 files and a CI workflow reference it (several at the stale `docs/specs/` path). It is
> harmless where it sits; folded into B2's reference sweep rather than done as quick fruit. *(This is the kind of
> "looks easy, isn't" that's better caught before acting than after.)*

### Tier 1 — Schema reconciliation (the real work)

- [ ] **B1 — Single source of truth for art direction** (see §2). Decision + delete duplicated palette/physique
  from the 10 gameplay cards + add `artIdentity` pointer. ~1 session.
- [ ] **B2 — Replace the dead CI validation with a real one.** Today nothing validates
  `data/cards/sovereign-dawn/*.json` against `codex-schema.json` (the existing workflow is dead — see §2 finding).
  Stand up a single Python `jsonschema` validator in the empty `tools/validators/` that checks every card against
  codex-schema, wire it into `.pre-commit-config.yaml`, and either fix or delete `validate-schemas.yml`. Fold the
  `card-schema.json` reference sweep (ex-F2/F3) into this task since you're touching schema plumbing anyway. This
  is the automation you asked for — and the guardrail that stops art/gameplay re-merging by accident.
- [ ] **B3 — Add an art-pipeline validator** (optional, parallels B2): validate `data/art/**/*.json` against a
  small schema derived from the field-vocabulary registry (`data/art/_schema/field-vocabulary.json`) so new
  pieces can't introduce unknown fields. `gen_prompt.py` already half-does this at generation time; B3 makes it a
  standalone check.

### Tier 2 — The asset pipeline spec (answers "once I get the .png files…")

- [ ] **C1 — Write `docs/art/asset-delivery-pipeline.md`.** The single clearest gap. Define the full chain:
  `prompts/<group>/<Hero>/<stage>/*.txt` → (ComfyUI render, manual) → **where the PNG lives** (propose
  `assets/renders/<group>/<slug>/<stage>/*.png`, git-LFS or external) → **naming convention** → how
  `portraitAsset`/`fullArtAsset`/`shinyPortrait` on the card reference it → how Unity loads it
  (`Resources/` or Addressables). Right now the chain stops dead at "a text prompt exists."
- [ ] **C2 — "Shiny"/foil + rarity-frame art plan.** You flagged special/foil variants. Decide now whether a
  shiny is (a) the *same* scene card with an added `effects` layer + `shinyPortrait` asset, or (b) its own card
  variant. Document in C1; `codex-schema.json` already has a `shinyPortrait` slot waiting.

### Tier 3 — Game balance (needs A1 first; mostly deferred)

- [ ] **D1 — Pick MVP elements + card counts** (= Action A1). Prerequisite for everything balance.
- [ ] **D2 — Reconcile `combat-calculation-spec.md` / `deck-progression-rules.md`** against the 7-tier
  (Transcendent) model the roster now uses — the July reconciliation flagged arithmetic/copy-limit issues and
  these docs predate the Transcendent tier. Defer until D1 picks the actual MVP cards to balance.

### Deferred (documented, not now)

- Unity project scaffolding (no `Assets/` exists yet; `unity-implementation-guide.md` is self-flagged pre-reset).
- Beyond-deck art (map tiles, battle-grid UI, menu/intro scenes, status-effect icons) — scoped in `assets.md`,
  blocked on F4 refreshing it against the real roster.
- Mining signature `.json` files back into shared wardrobe/background pieces (per `data/art/README.md`) — wait
  for more content to find real patterns.

---

## 4. The through-line (why this is healthy, not thrashing)

Top-down vision, bottom-up work in one topic, reconcile the gaps, repeat — the same loop that took the art from
"just Drakness" → sisters → males → dragons, each round surfacing issues we fixed and documented. This doc is the
"step back and look at the big picture" checkpoint for the **art ↔ gameplay** seam specifically. The next natural
checkpoint is after B1/B2/C1 land: at that point a single hero can go fully end-to-end (card data + art direction +
rendered PNG + schema-validated + loadable), proving the whole chain on one example before scaling to the MVP deck.
