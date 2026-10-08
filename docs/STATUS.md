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
  counts as scene); everything goes to the one workspace per group (see the pipeline phases below).
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
- **One workspace per group, hero first, by pipeline phase (Oct 2026, replaces the per-sister workspaces).** `Drakn Sisters` holds every sister laid out
  `<Hero>/<phase>/...`: `1_Alpha`, `2_Studies`, `3_Layers`, `4_Wardrobe`, `5_Scenes`, `6_Finish` (`polish`, `final` skeletons per sister; upscale is not built yet),
  `7_Video`, and `Bench/motion` (a test run on any phase's image, not a phase). The other permanent workspaces are Angel Primes, Drakn Bound, Elder Dragons and
  Sovereign Territories (dev and brand). A single-sister workspace is spun up only while needed and discarded; only `Drakness` is kept (and kept in sync) until her
  hand-made armor, clothing and scenes are covered by the generated set. The chosen image of each later phase is named `_00000` too (`<Hero>_Qwen_Scene_00000.png`
  feeds Polish, `_Polish_00000.png` feeds Final), so a skipped phase shows as a missing image. The card folders (`data/art/_sets/`), the prompts and the output all use these same phase folders (one layout everywhere). Dev keeps whatever is not
  delivered, edited or hand-curated: `comfy_workflows.py cleanup` previews (and with `--apply` moves to backup) only the plain duplicates. Every sister has
  a studio kit; first proven with Draknara: a studio kit (`data/art/_kits/<slug>.json`, built by `tools/generators/scaffold_sister_studio.py`) lists the A-pose
  bases, outfits, armor, motions and showcase shots that suit her class and element.
- **Three kinds of hand-made workflow (Oct 2026).** `zz_Curated` = older hand-written workflows and new ones written from scratch; `zz_Shots` =
  workflows tuned for a render (seed, Turbo or not), kept in the repo under `workflows/_shots/<set>/<Hero>/` with their subfolders;
  `zz_Test` = temporary. Generated workflows are never edited by hand.
- **A-pose bleed tests and real-world showcases (Oct 2026, in progress).** Celestial armor showcases let the A-pose swimsuit bleed through. Options
  under test: a `strip` instruction (`wardrobe/effects/strip/remove-original`, `replace-original`; the celestial strip-test cards were retired, the pieces and the optional `?{{STRIP}}` template line stay for other edits),
  a neutral base-layer A-pose (`<slug>-x-pose-base-layer`) and the user's own nude A-pose workflow (a shot). Also 13 real-world photo showcases per sister
  (`showcase/photo/glamour|romantic|daily`: catwalk, grand staircase, bed, beach, city street, bathroom selfie ...) to see how realistic she stays;
  template `showcase-photo-human.txt`, locations in `backgrounds/modern/`. Whether Turbo is worth it for the A-pose is a render question, recorded as shots.
- **Footwear in the A-pose (Oct 2026, decided).** The A-pose is barefoot by default, which keeps shoes out of every later outfit. One switch,
  `data/art/_settings/studio.json` `aPoseFootwear` (`barefoot` today, `signature` to bring back each sister's heels after a regenerate),
  plus `<slug>-x-pose-heels` cards for glamour work. Showcases are filed in families (`celestial`, `elemental`, `studio`, `editorial`, `photo/<mood>`).
- **Output folders follow card families (Oct 2026).** Cards, prompts and ComfyUI output folders are grouped by family below the stage
  (`scene/signature`, `scene/glamour`, `poses/lingerie`, `clothing/gowns` ...) and the output folder starts with the set and hero
  (`drakn-sisters/Draknara/scenes/signature/...`), mirroring `prompts/`; the rule lives in `tools/generators/art_layout.py` and is
  validated. A variant such as shiny or holo sits beside its main card, and one-card groups stay flat. See `data/art/README.md`.
- **Folders outside the repo (Oct 2026).** Originals live in `B:\Sovereign Territories\Models`, hand-picked keepers in `...\Masters`;
  everything under `B:\Comfy-Desktop` is a transient copy. Each ComfyUI workspace has its own inputs (`ComfyUI-Inputs\<Workspace>`) and
  writes to a project output folder (`Sovereign Territories`, `Angel Primes` as a test bed, `Sovereign Dawn Series` for production), set
  in `workflows/workspaces.json`. The brand and marketing set (title, logos, icons, key art) will be the `sovereign-territories` set.
- **Brand, card art and video pieces (Oct 2026).** The brand set (key art, plates, title, logo, icons, two videos) lives in
  `data/art/brand/` and `_sets/sovereign-territories/`. Non-hero gameplay cards (units, pets, buildings, tactics, equipment, workers; 174)
  get mechanical card-art prompts from their own name, element and lore (`data/art/cards/sovereign-dawn.json`,
  `tools/generators/scaffold_card_art.py`, stage `card`); they are first drafts, not hand-directed art. Reusable video effect pieces
  (ambient, element, theme) in `data/animation/motions/` feed ten theme scene videos. Nothing from these has been rendered yet.
- **Showcase stage:** a studio-class shot on a coloured or magical backdrop (`backgrounds/studio/*`) with an effects line, between a cream
  studio render and a full scene.
- **Celestial armor and the Celestial finish (design, Oct 2026).** Every sister has her own signature celestial armor
  (`heroes/drakn-sisters/<slug>/armor/celestial-armor.json`): small ornate filigree plates in her metal and class/element motif, each a
  different shape (crescents, flames, leaves, snowflakes, shells, sunbursts ...), covering the area of a small bikini cup and a small
  front hip piece, held by magic alone with no straps or wire. The `celestial` finish (`SD-001-CELESTIAL`, rank 3 in
  `finishes.json`) is the earned top edition: unlocked by a sister's celestial quest chain rather than drawn from a pack, with some
  held back in packs for a small chance (rules are open decision O3). The codex shows a silhouette or masked teaser until it is owned.
- **Body contour on by default (Oct 2026).** `bodyContour` in `data/art/_settings/studio.json` adds a fit-to-the-incoming-body line (`fitted-contour`; `armor-contour` for the armor stage)
  to every outfit, armor, showcase and scene prompt for the female sisters; a card sets `components.body_contour` to another piece (`sheer-contour`) or `"off"` to change or skip it.
- **Key learning: the incoming image decides what bleeds through (Oct 2026).** Outfits fed a bikini A-pose kept the bikini (low-cut dresses were not low cut; celestial armor kept the
  straps). The chain is therefore: original photo, then the standard X Pose (a clean metallic-bikini, barefoot A-pose that also sets the bust and pose), then an edit-only `bare` stage
  (removal plus a small covering or none), then the other poses fed the bare image with the body contour on, then
  outfit, armor, showcase and scene, each fed the incoming image that gives the wanted result; documented in `docs/art/tutorial-art.md`. Complete scenes describe the outfit,
  staged scenes take a dressed image, and a semi-staged scene is a complete scene fed an A-pose that already wears a layer. FireRed versions of the bare study and celestial
  steps exist for overnight non-Turbo comparison; the best bare A-poses become the input for everything else.
- **Standard size and denoise defaults (Oct 2026, provisional).** Originals are padded to 944x1104 (`standardSize`), a Kontext bucket, so the Qwen chain keeps one size;
  FireRed's 1 MP resize lands on the same size. Generated workflows start at the high end of their card's denoise range (1.0 only for the X Pose from the original
  photo; `denoise` in `workspaces.json`, tool `comfy_workflows.py denoise`), so the stages after a golden image keep some creativity. Tuning rules:
  [art/comfyui-art-pipeline.md](art/comfyui-art-pipeline.md#denoise-is-the-key-lever).
- **The Alpha stage (Oct 2026).** The first workflows of a hero are not poses: they create her likeness, so they have their own stage and folder, `alpha/`
  (sorts first). Alpha 1 Prime (original photo to the bikini A-pose, standard figure), Alpha 2 Bare (Prime to bare skin: individual build, hair, eyes, skin and
  bust re-asserted; the figure and chest looks sit flat in `1_Alpha/2_Bare/`, next to the hand-made `Alpha_2_Bare_Skin` shots; the coverings and celestial experiments are Alpha 2b in `alpha/bare/coverings/` and `alpha/bare/celestial/`) and Alpha 3 Barefoot and Heels (Bare image back into the bikini on her own figure, `alpha/footwear/`).
  `Alpha_2_Bare_Figure` is the intended Bare step; the hand-made `Alpha_2_Bare_Skin` shots are temporary while it is tuned and are not kept long term.
  Bare, Barefoot and Heels are the three golden images, named `<Hero>_Qwen_Alpha_1_Prime|Alpha_2_Bare|Alpha_3_Barefoot|Alpha_3_Heels_00000.png` (the `_00000`
  sorts above the numbered renders); `poses/` now holds only variations fed the Bare image. Input roles: `photo`, `prime`, `bare`, `apose` (the Barefoot image), `heels`
  (`workspaces.json` `inputRoles` and `inputs`, `inputs --set --prime`). Sisters only so far; dragons, bound heroes and Angel Primes keep their X Pose in `poses/`. The Barefoot and
  Heels cards still use the photo-oriented `pose-female-human.txt`; an edit-focused template for them is open, as is the same for the other stages.
- **Individual physique, standard X Pose (Oct 2026).** The 10 sisters and 10 bound heroes each carry their own build (`physique`: `torso` and `arms` are new optional fields; the male
  schema stays `chest`/`waist` plus `arms`), merged from an external review (`docs/codex/heroes/*_physique.md`, `elder_dragons_.md`); its colours, metals, prompt-assembly sections and
  invented ids were not adopted. The X Pose from the original photo keeps the standard lithe, slender figure (`figureProfile: standard`, text in `data/art/_settings/phrases.json`); the
  individual build is applied from the Bare stage on (`Body:` line), so it never fights the original photo, clothes or background. The 10 Elder Dragons gain structured morphology
  (`silhouette`, `scaleTexture`, `wingMembrane`, `hornsAndCrest`, `elementalVenting`) in our own palettes. Studio smile: new `studio-soft-smile` (A-pose and head default).
- **Two celestial looks and a two-step core (Oct 2026, ideation).** The original larger plates are kept as `celestial-plate-armor`; the new
  `celestial-skin-armor` is thin metallic design formed on the skin by magic (open filigree, form-fitting, skin showing through, her class and element
  motif). The `bare` stage (`Bare_*`) is an edit-only pass on a finished A-pose; `Bare_CelestialPlate` and `Bare_CelestialCore` (skin) produce a
  "celestial A-pose" that can be fed into scenes, showcases or other outfits to carry her celestial form into the picture. Later: Shiny and Holo
  editions add glow, a little more coverage and accessories, probably as a second pass on that image.
- **Theme scenes have two paths over one library (Oct 2026).** Every outfit, armor, jewelry, footwear, headwear and weapon item is a
  library piece, never inline text in a card (generic fillers such as "bare arms" excepted), so a scene can be built either way: a
  *complete* scene (`<hero>-scene-<theme>`) names all the pieces so the model has freedom and a scene can be tested at once, or a
  *pre-staged* path where a studio outfit card (`<hero>-armor|clothing-<theme>`) is rendered first and the `-scene-staged-<theme>`
  card only adds scene, effects and pose. Each sister has six themes (the 12 new packs plus the older ones); effects, expression and pose
  stay literal text on the card. Raven armor is now pieces (`heroes/drakn-sisters/drakness/armor/raven-*`).
- **Every bust is full, firm and lifted, on purpose (Oct 2026).** Clothing and armor that is applied to a flatter or lower body loses the bust line, so the Alpha images
  establish a lifted, crisp cleavage for every sister (shared `bustKey` for the Prime, each sister's own `bust` line for the Bare step through the `ownBust` key; the
  lines differ in shape and detail, not in lift), and the standard `fitted-contour` / `armor-contour` pieces (also `-male` variants, applied to male heroes) tell every
  outfit to follow and support the bust, waist and hips unless a card opts out. Explicit anatomical wording stays in the hand-made `zz_Shots`, never in generated files.
- **Angel Primes is the clean test bed (Oct 2026).** Twenty angels (ten female, ten male, humans only, no card, `testBed`) on a good-to-evil spectrum, one female and one male
  per element in each of ten pairs, each with a bonded non-dragon pet (`data/art/pets/angel-primes/`). New things (themes, backgrounds, creatures, clothing, weapons,
  motions) are tried here and only the ones that work are pulled into the Drakn workspaces; Drakness is no longer the test-everything hero. Roster, kits and the trimmed
  set (about 16-20 cards each) are in [../data/art/README.md](../data/art/README.md#angel-primes-the-clean-test-bed). Angelica and Angelo stay as the older pair.

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

- **Library gaps (Oct 2026):** the map of what exists and where the gaps land (backgrounds, props, races, creatures, unit/building/tactic art, theme gear for bounds and dragons) is in [../data/art/README.md](../data/art/README.md#library-map-what-exists-where-the-gaps-are). Do these as the sisters' scenes show what is missing, not as a separate big push.
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

### Generator and automation debt (hidden wording and defaults)

Fixed Oct 2026: the hero prompt wording that lived in `gen_prompt.py` (keep line, bust key, figure negatives, makeup and grooming lines, default breeze,
hairFrom text, "slim waist" and "slim, tapering thighs", card-art grandeur) is now in `data/art/_settings/phrases.json`. Still open:

- `SLOT_DEFAULTS` in `gen_prompt.py` (default expression, underlayer, footwear, sheen, background, framing by stage and sex) is code, not data; move it to a settings file.
- `TEMPLATE_KEY_DEFAULTS` (which details each template calls out up front) and the `FIGURE_FIELDS_*` order are code constants.
- `tokens_for_brand` hard-codes "a woman in ..." for the lineup; `tokens_for_cardart` and the card-art `SIZE` in `scaffold_card_art.py` hold wording and size in code.
- `comfy_workflows.py` `engine_prompt()` rewrites FireRed prompts (environment-first, magic `fx` line) outside the prompt files; its text is in `workspaces.json` but the rewrite is invisible in `prompts/`.
- Defaults derived in code rather than stated: nail colour ("Light <last word of primary>"), eyeshadow, magic and gem colours from the first accent when a hero omits them.
- The three templates still hold some fixed prose by design (studio lines, negatives); a template change is a deliberate edit, not hidden.
- The older studio and glamour expression pieces, and `motion/*` default expressions, still carry closed-mouth or sultry wording; only the A-pose and head defaults were changed.

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
