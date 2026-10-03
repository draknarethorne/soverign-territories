# Art ↔ Gameplay Reconciliation Plan (October 2026)

**Status:** Active plan · **B1, B2, B3 and A1 completed Oct 2026** (see §2–§3); remaining tasks listed in §3.
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

**Action A1 — RESOLVED (Oct 2026): staged element rollout.** The game is designed for ten elements but
releases in stages: **Grass, Fire, Water** first (MVP — the classic trio), then **Darkness + Light** (either folded
into the first public push for a five-element launch, or as the first expansion), then the remaining five in an order
driven by the Sundering storyline. The 3-vs-5 choice depends on how much work a complete, balanced card set per element
turns out to be. Recorded in `game-bible.md` and `ideation_codex.md` (which previously said "all ten from day one").

**What the existing card inventory says about that decision** (cards under `data/cards/sovereign-dawn/`, by element):

| Element | Cards | Heroes | Units | Tactics | Note |
| --- | ---: | ---: | ---: | ---: | --- |
| Fire | 53 | 7 | 42 | 3 | Legacy depth — first-trio ready to build on |
| Water | 46 | 7 | 36 | 3 | Legacy depth — first-trio ready to build on |
| **Grass** | **4** | 2 | 2 | 0 | **The gap.** Only the sister + her bound hero + dragon + pet exist; no legacy Grass content |
| Darkness / Light | 4 each | 2 | 2 | 0 | Same shape as Grass: just the 4 vision cards each |
| Earth | 46 | 7 | 36 | 3 | Legacy depth, but **not** in the new first trio — sits ready for a later expansion |
| Ice / Lightning / Wind / Poison | 4 each | 2 | 2 | 0 | Vision cards only |
| Neutral | 46 | 0 | 0 | 3 | 19 buildings, 10 workers, 14 equipment, 3 tactics |

So the old trio (Fire/Water/Earth) had the legacy buildout; the new trio swaps **Earth for Grass**, and Grass has almost
nothing yet. Fire and Water are in good shape; **a complete Grass set is the first real content task**, and Darkness/Light
(for a five-element launch) would each need a full set built from the 4-card seed.

---

## 2. The art ↔ gameplay split (B1 — completed)

**The problem, as found:** the same hero's palette/physique existed in two files and had already diverged. The
gameplay card `hero-drakness-thorne.json` carried an `art.palette`/`art.physique` block (hair "obsidian-black with
amethyst ribbons", build "elf-like") while the art identity that actually drives `gen_prompt.py` said something
different (hair "black with espresso depth + plum-amethyst streaks", build "long-limbed"). Only the art file was
consumed; the card's copy was a silently drifting duplicate on all 10 sisters. It happened because the card schema was
authored for gameplay only, back when art was assumed to be hand-drawn.

**The resolution — one owner per attribute, linked by `cardId`:**

| Concern | Owner | Where |
| --- | --- | --- |
| Identity + mechanics: name, element, sex, race, class, rarity, stats, abilities, lore, companion | **Gameplay card** | `data/cards/**` · `data/schemas/codex-schema.json` |
| Look: palette, physique, hairstyle, wardrobe, signature pieces, scene recipes | **Art** | `data/art/**` · `data/art/_schema/*.schema.json` |
| Card → art link | card | `art.artIdentity` (path to the identity file) |
| Art → card link | art identity | `cardId` (art pulls name/element/sex/race/class from the card at generation time) |
| Rendered output references | card | `art.portraitAsset` / `fullArtAsset` / `shinyPortrait` (naming defined in C1) |

**The rule:** *gameplay data and art-direction data never both define the same attribute.* An attribute needed by both
(e.g. `sex` choosing the female vs male figure) lives on the card and the art side reads it through the link.

**The flow for a new card:**

1. Define the card in the codex (`data/cards/…`) — this is the primary record; the schema validates it.
2. Create its art identity (`data/art/heroes|dragons/…`) with `cardId`, and set the card's `art.artIdentity` to point back.
3. Add assembly cards under `data/art/_sets/<group>/<slug>/…` (pose, head, armor, signature scene).
4. `python tools/generators/gen_prompt.py` → prompts. Render in ComfyUI. Record the outputs in the card's `*Asset` fields.

Steps 1–3 are enforced by `tools/validators/validate_data.py` (below).

**What shipped:**

- `codex-schema.json`: `art` reduced to `artIdentity` + asset references, `additionalProperties: false` on the card and on
  `art` (art direction can no longer creep back onto a card); four previously-undeclared gameplay fields
  (`equipSlot`, `manaCost`, `effect`, `resourceType`) now declared.
- New art-side schemas in `data/art/_schema/`: `hero-identity`, `dragon-identity`, `art-piece` (per-`kind` required
  fields), `art-card` (the `_sets` recipes). Together with `field-vocabulary.json` these define the art contract.
- 30 art identities migrated to the `cardId` shape (20 heroes + 10 dragons; Angel Primes are `testBed: true` with no card)
  and 30 cards now carry `art.artIdentity`. `gen_prompt.py` resolves the link and fails loudly on a dangling `cardId`.
  All 177 prompts regenerated **byte-identical** — the migration changed structure, not output.
- `tools/validators/validate_data.py`: schema-validates 562 files and enforces cross-file integrity (bidirectional
  card↔art link, referenced pieces exist, a typo'd piece path can't silently become literal prompt text, generated
  outputs are unique, physique shape matches the card's sex, unique `cardId` / `collectionNumber`). It prints a coverage
  report so schema-less areas stay visible.
- `tools/validators/test_validate_data.py`: mutation tests that corrupt a temp copy of `data/` ten ways and assert each is
  caught — so the gate cannot silently go dead the way the old one did.
- Both run as pre-commit/pre-push hooks and therefore in CI (`quality.yml` runs `pre-commit run --all-files`).

### Dead validation, removed

`.github/workflows/validate-schemas.yml` and `scripts/Invoke-PrePushValidation.ps1` only watched `docs/specs/*.json`
(moved to `data/schemas/` in Jan 2026, so they never ran) and validated each schema *against itself*, so no real card
was ever checked. Both are deleted and the docs that cited them updated.

### Open items from this work

- **15 legacy hero cards have no art identity** (Aria, Thalor, Gaia, …). Expected — they are not in the 30 — but the
  validator's coverage line keeps the number visible as the MVP deck takes shape.
- **`card-schema.json` is still present** (self-labeled DEPRECATED). It is harmless, but 22 stale docs/agent files still
  cite it; retiring it is a reference sweep, not a delete. See S2.
- **Schema debt** the validator reports as PENDING: see S1.

---

## 3. Task list and status

### Done

- [x] **F1 — Surface the art pipeline in the docs hub** (`docs/README.md` source matrix now lists the art pipeline,
  the vision roster, and this plan).
- [x] **A1 — Element rollout decision** (Grass/Fire/Water, then Darkness + Light, then the rest; see §1).
- [x] **B1 — Single source of truth for art direction** (see §2).
- [x] **B2 — Real card validation replacing the dead CI** (see §2). The old `card-schema.json` reference sweep was
  *not* folded in after all — it is its own task, S2.
- [x] **B3 — Art-pipeline validator.** Delivered as part of B2: art identities, pieces and assembly cards each have a
  schema, and the validator checks them plus all cross-file references.

### Next — content and balance (the product work this unblocks)

- [ ] **G1 — Build out a complete Grass set.** The new trio's gap: Grass has 4 cards against Fire 53 / Water 46 (see §1).
  Define the per-element template's worth of Grass cards (heroes, units, tactics) in the codex, then art for each. This is
  the best first exercise of the new flow: card → art identity → assembly cards → prompts, validator-enforced.
- [ ] **G2 — Decide 3 vs 5 elements for the first public release** (Darkness + Light now vs. as Expansion 1). Use G1 as the
  cost estimate: if a full Grass set is cheap, five elements is realistic.
- [ ] **D2 — Reconcile `combat-calculation-spec.md` / `deck-progression-rules.md`** against the 7-tier (Transcendent)
  model and the chosen first-release elements; the July reconciliation flagged arithmetic/copy-limit issues in both. Do
  this once G2 fixes which cards exist to balance.
- [ ] **D3 — Starter decks and products for the new trio.** `data/decks/starter/` and `data/products/` still reflect the
  old Fire/Water/Earth trio (earth starter box, frost/lightning/wind boosters). Rebuild around Grass/Fire/Water.

### Next — pipeline and tooling

- [ ] **C1 — Asset-delivery spec** (`docs/art/asset-delivery-pipeline.md`): prompt → ComfyUI render → where the PNG
  lives and how it is named → the card's `portraitAsset`/`fullArtAsset`/`shinyPortrait` → how Unity loads it. The chain
  still stops at "a text prompt exists." Once defined, extend the validator to check that every referenced asset exists.
- [ ] **C2 — Shiny/foil and rarity-frame art plan.** Decide whether a shiny is the same scene card with an added
  `effects` layer plus `shinyPortrait`, or its own variant. Document in C1.
- [ ] **S1 — Schema debt (the validator's PENDING list).** `pack-schema` (0/16 files match), box, reward, starter-deck,
  manifest, collection and element-list files have no schema that fits. Decide per area: rewrite the schema to the
  current data, or rewrite the data to the schema. Fold into D3 for products/decks.
- [ ] **S2 — Retire `card-schema.json`.** Deprecated, unused, but cited by 22 docs/agent files (several at the stale
  `docs/specs/` path). A reference sweep, then move it to an archive folder.
- [ ] **F4 — Refresh or archive `docs/design/assets.md`.** Dec 2024, written against the old 140-card roster; its category
  scaffold (card frames, icons, map tiles, battle UI, menus) is the right skeleton for the beyond-cards art.

### Deferred

- Unity project scaffolding (no `Assets/` yet; `unity-implementation-guide.md` is self-flagged pre-reset).
- Beyond-deck art (map tiles, battle-grid UI, menu/intro scenes, status-effect icons), blocked on F4.
- Mining signature `.json` files back into shared wardrobe/background pieces, once there is enough content for real patterns.

---

## 4. The through-line (why this is healthy, not thrashing)

Top-down vision, bottom-up work in one topic, reconcile the gaps, repeat — the same loop that took the art from
"just Drakness" → sisters → males → dragons, each round surfacing issues we fixed and documented. This doc is the
"step back and look at the big picture" checkpoint for the **art ↔ gameplay** seam specifically. The next natural
checkpoint is after B1/B2/C1 land: at that point a single hero can go fully end-to-end (card data + art direction +
rendered PNG + schema-validated + loadable), proving the whole chain on one example before scaling to the MVP deck.
