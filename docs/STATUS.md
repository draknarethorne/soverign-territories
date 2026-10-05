# Project Status

**Updated:** 2026-10-04 · This is the one working document: where the project is, what has
been decided, what is open, and what is next. Rules live in the canonical docs listed in
[README.md](README.md); this file only tracks state and decisions.

## Where we are

Design and art are ahead of gameplay data. The repo has no Unity project yet.

| Area | State |
| --- | --- |
| Art pipeline | Working. `data/art/` identities + pieces + templates compile to prompts via `tools/generators/gen_prompt.py`. Core wardrobe plus six theme packs (Greek, Roman, Egyptian, Norse, Celtic, Thanksgiving). Every sister has Signature, Glamour, Elegant Casting, Staged Enchanted Evening, **The Dawn** (rising in her homeland) and **Robe** scenes, each with its own background. How to add to it: [art/tutorial-art.md](art/tutorial-art.md). |
| ComfyUI workflows | Automated. `tools/workflows/comfy_workflows.py` builds workflows from prompts and syncs them across dev, per-sister UAT and series PROD workspaces (`workflows/workspaces.json`, [../workflows/README.md](../workflows/README.md)); `bin/*.cmd` are the quick launchers. Three engines: Qwen (card-art look, tracked in git), FireRed (photoreal, local test copies with a real-then-magic effects instruction) and MiniMax video (tracked). The `ST0`-`ST6` templates are the only masters. Hand-tuned workflows are kept in `workflows/_curated/` and never regenerated. |
| Video | First pipeline built: `data/animation` cards (actions as `Motion:`/`Scene:` blocks with transitions) -> `gen_animation.py` -> MiniMax H3 workflow from `ST6_MiniMax_Video`. Three Drakness example clips are deployed; none rendered yet. Guide: [art/tutorial-video.md](art/tutorial-video.md). |
| Sister variants | Every sister has a **Signature Shiny** (`<slug>-scene-signature-shiny`: the Signature card with a prismatic `overrides.palette` and a glitter-sheen effects line), a **Battle** scene (war gear piece plus homeland battlefield), a **Bond** scene (first meeting with her Elder Dragon) and a **Dawn Rising** video card. First new culture pack: `themes/danish` (Snow Queen inspired) with `draknira-scene-danish`. Prompts and dev workflows built; none rendered yet. |
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
- **Art and video are data-driven (Oct 2026).** Pieces, cards and animation cards generate prompts; prompts generate workflows. Prompts
  are never hand-edited. Work is **studio** (cream backdrop: poses, heads, hair, armor) or **scene** (realm, background, effects; video
  counts as scene); studio goes to a sister's own workspace, scenes to the shared `Drakn Sisters` workspace.
- **Dev/UAT/Prod workspaces** in ComfyUI: dev builds and proves, UAT is acceptance, PROD is the series workspace. Workflows are
  promoted (moved) up the tiers.
- **A hand-made workflow is never overwritten.** Anything tuned by hand is forked or pulled into `workflows/_curated/`; patterns that
  recur graduate into pieces, motions, transitions or templates.
- Prompt injection into ComfyUI workflows is automated; delivering rendered images back to cards is still manual (C1).
- **Variants are art editions of one card (Oct 2026).** `SD-001` stays the only definition; `art.variants` on the card lists editions
  (`shiny`, `holo`; tiers in `data/art/_schema/finishes.json`), each pointing at an art card that carries the same `finish`. A variant
  never changes gameplay; its code is `<collectionNumber>-<SUFFIX>` (`SD-001-HOLO`), derived, never stored. Shiny = recolour and sheen
  for every card hero; Holo = a re-authored edition with a title, ascended pose, upgraded items and a video. The foil/holo shader belongs
  to the client, not the baked art. Every card hero has a Holo (the ascended weapon descriptions are a start for equipment art).
- **Sister studio workspaces (Oct 2026).** Each sister's non-scene work (everything with studio class, including the new `showcase` stage)
  deploys to her own ComfyUI workspace with `deploy --to uat --hero <Name> --class studio`; scenes stay in the dev project. First proven
  with Draknara: a studio kit (`data/art/_kits/<slug>.json`, built by `tools/generators/scaffold_sister_studio.py`) lists the A-pose
  bases, outfits, armor, motions and showcase shots that suit her class and element.
- **Showcase stage:** a studio-class shot on a coloured or magical backdrop (`backgrounds/studio/*`) with an effects line, between a cream
  studio render and a full scene.
- **Celestial armor and the Celestial finish (design, Oct 2026).** Every sister has her own signature celestial armor
  (`heroes/drakn-sisters/<slug>/armor/celestial-armor.json`): ornate filigree plates in her metal and class/element motif that fully
  cover the bust and hips and are held by magic. Coverage stays at bikini level. The `celestial` finish (`SD-001-CELESTIAL`, rank 3 in
  `finishes.json`) is the earned top edition: unlocked by a sister's celestial quest chain rather than drawn from a pack, with some
  held back in packs for a small chance (rules are open decision O3). The codex shows a silhouette or masked teaser until it is owned.

## Open decisions

| ID | Question | Notes |
| --- | --- | --- |
| O1 | 3 or 5 elements in the first public release? | Estimate from a finished Grass set (G1). |
| O2 | Does "exactly one hero per formation" survive? | Written before the art pipeline made a larger roster cheap. Revisit after a playtest. |
| O3 | How are vision cards obtained? | All 30 have empty `acquisition` today. Needs pack/reward/campaign rules, including the quest-earned Celestial edition, the pack-chance share and the codex teaser. |
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

### Art and video track (runs alongside)

- Render and review the first video clips; tune looks, motions and transitions from what the renders show.
- Compare Qwen and FireRed on scenes; decide how the two (or a FireRed render plus a Qwen polish pass) are used.
- Underlayer tests for Drakness (string, push-up, balconette, bralette, sports, armor, lace, plus lace bodysuit and the backless set: halter one-piece, strapless plunge, chain harness) to choose the A-pose look that blends best. The backless pieces give a clean bare-back reference so gowns and capes do not inherit straps.
- Title and key-art scene from the text-to-image templates (`ST0_*_Text`), as a card in the pipeline; an item stage for weapons and armor.
- Use the other `ST` templates (polish, finals) to generate their own prompts.
- Documentation audit and launcher check, now with [art/tutorial-art.md](art/tutorial-art.md) and [art/tutorial-video.md](art/tutorial-video.md).

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

- **Asset delivery (C1).** The chain now reaches a ready ComfyUI workflow; it stops at the rendered image. Needs: where rendered PNGs live and how they are named,
  how the card's `portraitAsset`/`fullArtAsset` and each variant's `fullArtAsset`/`videoAsset` fields point at them, how Unity loads them (provisional
  card-art target 512x768, 2:3), and a validator check that referenced files exist. Running workflows through the ComfyUI API is
  still an option, see [art/comfyui-automation-proposal.md](art/comfyui-automation-proposal.md).
- **Animated card art:** static, animated (looping PNG or WebP) and video trailers are separate outputs; animated art plans are to be
  revisited. Videos are for reels, not the card.
- **Foil shader (C2).** Variants are modelled (see Decisions); still open: the in-client holo/foil shader and its mask, finish drop rates
  (with O3), and a reserved tier above Holo.
- **Beyond-card art:** frames, icons, map tiles, battle UI, menus. Rendering quality is checked by hand with
  [art/output-qa-checklist.md](art/output-qa-checklist.md); the generator cannot judge images.
- **Thorne Art Studio:** a Windows tool for editing art JSON, previewing prompts and driving ComfyUI; assessed in
  [art/thorne-art-studio-proposal.md](art/thorne-art-studio-proposal.md). Build the command-line pieces first.
- **Art packs and dynamic ComfyUI prompts (Oct 2026):** zip packs of art JSON and custom nodes that assemble a prompt from a template plus
  chosen pieces at run time, both on one shared prompt library; proposal in
  [art/art-packs-and-comfy-node-proposal.md](art/art-packs-and-comfy-node-proposal.md). Recommended before the Studio app.
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
