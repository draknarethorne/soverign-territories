# Project Status

**Updated:** 2026-10-03 · This is the one working document: where the project is, what has
been decided, what is open, and what is next. Rules live in the canonical docs listed in
[README.md](README.md); this file only tracks state and decisions.

## Where we are

Design and art are ahead of gameplay data. The repo has no Unity project yet.

| Area | State |
| --- | --- |
| Art pipeline | Working. `data/art/` identities + components + templates compile to prompts via `tools/generators/gen_prompt.py`. Rendering is manual in ComfyUI. Core wardrobe plus six theme packs (Greek, Roman, Egyptian, Norse, Celtic, Thanksgiving); each Drakn sister has one themed scene and hairstyle. |
| Vision roster | 30 cards (10 Drakn sisters, 10 bound heroes, 10 Elder Dragons) plus 10 pets, all with art identities; prompts generated. |
| Gameplay cards | `data/cards/sovereign-dawn/`: 219 cards, ids `SD-001`..`SD-219`. `SD-041`+ is legacy content (Fire/Water/Earth + Neutral). |
| Validation | `tools/validators/validate_data.py` (schemas + card/art links) and its mutation self-test run in pre-commit and CI. |
| Starter decks, packs, manifests | **Broken** (see Data debt). |
| Unity client, backend | Not started. |

## Decisions made

- **A card is defined once, in the codex** (`data/cards/**`, `codex-schema.json`). Art is built for it and linked by
  `cardId`. Gameplay and art data never define the same attribute; see `data/art/README.md`.
- **First series is Sovereign Dawn.** `cardId` (machine, stable) is separate from `collectionNumber` (`SD-###`, human).
  Products reference card ids or pools; they never copy card definitions.
- **10 elements**, released in stages: Grass/Fire/Water first, then Darkness + Light, then Earth, Ice, Lightning, Wind,
  Poison in story order. Elements are cosmetic in the MVP.
- **8 rarity tiers** (Basic 0, Common 1, Uncommon 2, Rare 4, Epic 8, Legendary 16, Mythic 32, Transcendent 64 points).
- **Starter decks stay low-rarity (Oct 2026).** Starter heroes are Rare-Legendary "lower-level" heroes under the
  40-point budget. Bound heroes and dragons (Mythic) and sisters (Transcendent) are earned from packs, campaign
  rewards, or story beats; sisters are apex showcase cards. The budget does not change.
- Player-facing title is **Sovereign**, not "Player".
- Asset delivery and prompt injection into ComfyUI workflow JSONs are deferred; manual copy-paste is acceptable.

## Open decisions

| ID | Question | Notes |
| --- | --- | --- |
| O1 | 3 or 5 elements in the first public release? | Estimate from a finished Grass set (G1). |
| O2 | Does "exactly one hero per formation" survive? | Written before the art pipeline made a larger roster cheap. Revisit after a playtest. |
| O3 | How are vision cards obtained? | All 30 have empty `acquisition` today. Needs pack/reward/campaign rules. |
| O4 | Transcendent format legality | 64 points exceeds any starter budget; decide special formats (Phase 2+). |

## Next work (in order)

1. **G1 Grass set.** Only 4 Grass cards exist (sister, bound hero, dragon, pet) and no legacy Grass heroes; Fire has 53,
   Water 46. Define heroes, units, tactics in the codex, then art. Best end-to-end test of the card -> art -> prompt flow.
2. **D3 Starter decks and products.** Rebuild around Grass/Fire/Water using the starter-hero decision above; include
   lower-level heroes, and decide where bound heroes and dragons enter (O3). Fixes everything under Data debt.
3. **D2 Rule reconciliation.** Re-check `combat-calculation-spec.md` and `deck-progression-rules.md` against the 8-tier
   model and the chosen elements.
4. **G2 Decide O1** with G1's cost in hand.
5. **Art for the 15 legacy heroes** that lack art identities, plus full sets for Grass, Darkness, Light.

## Data debt

- `data/decks/starter/starter-decks.json` has 26 card ids that do not exist and is built on the retired Fire/Water/Earth
  trio (old heroes Aria, Thalor, Gaia).
- `mythic-pack` and `monthly-reward-pack` reference nonexistent `HERO_MALAKAR_DEMON_OVERLORD`; packs name seven `cardPool`
  ids defined nowhere.
- `data/manifests/series-manifest.json` still describes the old elements and factions;
  `sovereign-dawn-card-list-mvp.json` says `cardCount: 131` but lists 135 ids.
- None of the 30 vision cards is in a deck, box, or MVP list (only the marquee list and collection checklist).
- `card-schema.json` was retired Oct 2026; `data/schemas/codex-schema.json` is the card schema.

### Schemas still to write

The validator's coverage report lists data with no fitting schema: packs (16 files, `pack-schema` matches none), boxes (3),
rewards (1), starter decks (1), manifests (4), collection checklist (1), card element-lists (7). For each, decide
whether to rewrite the schema to the data or the data to the schema; do it alongside D3.
Another ~30 schemas in `data/schemas/` (map, player, alliance, store, ...) have no data yet and are not needed
before the systems they describe; `docs/specs/*.md` holds their narrative notes.

## Deferred

- **Asset delivery (C1).** Chain stops at "a text prompt exists." Needs: where rendered PNGs live and how they are named,
  how the card's `portraitAsset`/`fullArtAsset`/`shinyPortrait` fields point at them, how Unity loads them (provisional
  card-art target 512x768, 2:3), and a validator check that referenced files exist. Includes a tool that injects prompts into
  `workflows/**.json` instead of copy-paste.
- **Shiny/foil (C2).** Same scene card plus an `effects` layer, or its own variant; decide with C1.
- **Beyond-card art:** frames, icons, map tiles, battle UI, menus. Rendering quality is checked by hand with
  [art/output-qa-checklist.md](art/output-qa-checklist.md); the generator cannot judge images.
- **Thorne Art Studio:** a Windows tool for editing art JSON, previewing prompts and driving ComfyUI; assessed in
  [art/thorne-art-studio-proposal.md](art/thorne-art-studio-proposal.md). Build the command-line pieces first.
- Unity project scaffolding; mining signature pieces back into shared wardrobe/background components.

## Readiness gates

Do not say "MVP ready for Unity" until all pass:

- [ ] MVP, combat, deck, tutorial, and hub docs agree on the baseline.
- [ ] Data contracts in `data/schemas/` are mapped to the selected MVP subset.
- [ ] Starter deck, card inventory, encounters, and rewards validate against real files (blocked by Data debt).
- [ ] A small playtestable vertical slice exists with measurable acceptance checks.
- [ ] Phase 1.1+ work is kept separate from MVP work.

Optional later gates, not MVP: fusion, persistent HP/Mana recovery, equipment, crafting, PvP, complex stores, map
exploration, economy deployment, backend services.

## Documentation rule

One home per fact. Superseded docs are moved (`git mv`) into an `_archive` folder, never kept beside the current
version; `_archive` content is a recycle bin that is ignored as documentation and purged later (see
[README.md](README.md#the-_archive-convention)).
