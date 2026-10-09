# Project Status

**Updated:** 2026-10-08 · This is the one working document: where the project is, what has
been decided, what is open, and what is next. Rules live in the canonical docs listed in
[README.md](README.md); this file only tracks state and decisions.

## Where we are

Design and art are ahead of gameplay data. The repo has no Unity project yet.

| Area | State |
| --- | --- |
| Art pipeline | Working. `data/art/` identities + pieces + templates compile to prompts via `tools/generators/gen_prompt.py`. Core wardrobe plus six theme packs (Greek, Roman, Egyptian, Norse, Celtic, Thanksgiving). Every sister has Signature, Glamour, Elegant Casting, Staged Enchanted Evening, **The Dawn** (rising in her homeland) and **Robe** scenes, each with its own background. How to add to it: [art/tutorial-art.md](art/tutorial-art.md). |
| ComfyUI workflows | Automated. `tools/workflows/comfy_workflows.py` builds workflows from prompts and syncs them to the home workspace of each set (Drakn Sisters, Sovereign Dawn Series, Sovereign Territories, Angel Primes; temporary copies in other workspaces on request) (`workflows/workspaces.json`, [../workflows/README.md](../workflows/README.md)); `bin/*.cmd` are the quick launchers. Three engines: Qwen (card-art look, tracked in git), FireRed (photoreal, local test copies with a real-then-magic effects instruction) and MiniMax video (tracked). The `ST0`-`ST6` templates are the only masters. Hand-tuned workflows are kept in `workflows/_curated/` and never regenerated. |
| Video | First pipeline built: `data/animation` cards (actions as `Motion:`/`Scene:` blocks with transitions) -> `gen_animation.py` -> MiniMax H3 workflow from `ST6_MiniMax_Video`. Three Drakness example clips are deployed; none rendered yet. Guide: [art/tutorial-video.md](art/tutorial-video.md). |
| Sister variants | Every sister has a **Signature Shiny** (`<slug>-scene-signature-shiny`: the Signature card with a prismatic `overrides.palette` and a glitter-sheen effects line), a **Battle** scene (war gear piece plus homeland battlefield), a **Bond** scene (first meeting with her Elder Dragon) and a **Dawn Rising** video card. First new culture pack: `themes/danish` (Snow Queen inspired) with `draknira-scene-danish`. Prompts and workflows built; none rendered yet. |
| Vision roster | 30 cards (10 Drakn sisters, 10 bound heroes, 10 Elder Dragons) plus 10 pets, all with art identities; prompts generated. |
| Gameplay cards | `data/cards/sovereign-dawn/`: 219 cards, ids `SD-001`..`SD-219`. `SD-041`+ is legacy content (Fire/Water/Earth + Neutral). |
| Validation | `tools/validators/validate_data.py` (schemas + card/art links) and its mutation self-test run in pre-commit and CI. The self-test changes real files in place and undoes them (a copy of `data/` per case cost a minute on Windows): `--quick` takes under 2 minutes, the full run about 6 (it was 15). |
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
- **Workspaces are tied to sets of cards (Oct 2026).** Each set has a *home* workspace (`homes` in `workflows/workspaces.json`): `Drakn Sisters`
  (the whole sister pipeline; final art is made there), `Sovereign Dawn Series` (the Sovereign Dawn card set), `Sovereign Territories` (the art and brand set and the `ST?_` templates),
  `Angel Primes`, and the planned `Drakn Bound` and `Elder Dragons`. A deploy goes to the set's home and nowhere else; a set with no home stops the command (a missing home once
  silently filled the brand workspace with 174 card workflows, and the workspaces cloned from it carried the leftovers). A workspace may also take a set on request, for a while, if it lists it under `accepts`:
  `Sovereign Territories` accepts any set (promotional videos for reels and feeds, a scene kept next to the art), `Sovereign Dawn Series` accepts the Drakn sets; you ask with `deploy -w` and remove the copy
  with `cleanup -w` when you are done, and a workspace that neither homes nor accepts a set is refused. Only `active` workspaces with an install are written to. `Drakness` stays as a deliberate second copy of one
  sister for working through issues with `zz_` items, and any sister can get a temporary one. Hand-made `zz_Shots`, `zz_Curated` and `zz_Test` workflows are mastered in the workspace and never replaced, moved or
  removed by deploy, cleanup or tidy. `cleanup -w` removes what a workspace is not home for (only when the home workspace has an identical copy; to backup; empty folders pruned). Details and rules:
  [../workflows/README.md](../workflows/README.md#workspaces-one-home-per-set).
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
  `7_Video`, and `Bench/motion` (a test run on any phase's image, not a phase). The other permanent workspaces are Angel Primes, Drakn Bound, Elder Dragons, Sovereign Dawn Series and
  Sovereign Territories (brand). A single-sister workspace is spun up only while needed and discarded; only `Drakness` is kept (and kept in sync) until her
  hand-made armor, clothing and scenes are covered by the generated set. The chosen image of each later phase is named `_00000` too (`<Hero>_Qwen_Scene_00000.png`
  feeds Polish, `_Polish_00000.png` feeds Final), so a skipped phase shows as a missing image. The card folders (`data/art/_sets/`), the prompts and the output all use these same phase folders (one layout everywhere). `comfy_workflows.py cleanup -w` previews (and with `--apply` moves to backup) the workflows a workspace is not meant to hold. Every sister has
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
  FireRed's 1 MP resize lands on the same size. Generated workflows start at the high end of the range in their stage template (1.0 only for the Prime from the original
  photo; `denoise` in `workspaces.json`, tool `comfy_workflows.py denoise`); the edit stages now run at 0.8 to 0.95, see the Oct 8 decision below. Tuning rules:
  [art/comfyui-art-pipeline.md](art/comfyui-art-pipeline.md#denoise-is-the-key-lever).
- **The Alpha stage (Oct 2026).** The first workflows of a hero are not poses: they create her likeness, so they have their own stage and folder, `alpha/`
  (sorts first). Alpha 1 Prime (original photo to the bikini A-pose, standard figure), Alpha 2 Bare (Prime to bare skin: individual build, hair, eyes, skin and
  bust re-asserted; the figure and chest looks sit flat in `1_Alpha/2_Bare/`, next to the hand-made `Alpha_2_Bare_Skin` shots; the coverings and celestial experiments are Alpha 2b in `alpha/bare/coverings/` and `alpha/bare/celestial/`) and Alpha 3 Barefoot and Heels (Bare image back into the bikini on her own figure, `alpha/footwear/`).
  `Alpha_2_Bare_Figure` is the intended Bare step; the hand-made `Alpha_2_Bare_Skin` shots are temporary while it is tuned and are not kept long term.
  Bare, Barefoot and Heels are the three golden images, named `<Hero>_Qwen_Alpha_1_Prime|Alpha_2_Bare|Alpha_3_Barefoot|Alpha_3_Heels_00000.png` (the `_00000`
  sorts above the numbered renders); `poses/` now holds only variations fed the Bare image. Input roles: `photo`, `prime`, `bare`, `apose` (the Barefoot image), `heels`
  (`workspaces.json` `inputRoles` and `inputs`, `inputs --set --prime`). Sisters and Angel Primes (Angelica and Angelo included) use it; dragons and bound heroes keep their X Pose in `poses/` for now. The Barefoot and
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
  motions) are tried here and only the ones that work are pulled into the Drakn workspaces; Drakness is no longer the test-everything hero. Roster, kits and the full
  set (about 179 prompts per female angel and about 105 per male angel) are in [../data/art/README.md](../data/art/README.md#angel-primes-the-clean-test-bed). Angelica and Angelo stay as the older pair
  (the only ones named Prime; their art slugs are `angelica` and `angelo`, like every other angel); every other angel has a family name, shared by the pair. Every angel owns signature items
  (weapon, armor, gown or attire, circlet, jewelry, elemental drift) under `heroes/angel-primes/<division>/<slug>/`, each built with `extends` on a library piece plus her element and alignment
  (written by `scaffold_angel_library.py`; her signature, battle, spell-calling, armor-stand and elegant-casting cards use them). The male angels now have the full set too (see the male wardrobe pack decision below).
- **Pieces can extend pieces (Oct 2026).** A piece may name a base (`"extends"`), carry only what differs, and use `{{BASE}}` or a leading `+` to splice the base text in: a standard
  silver necklace plus a hero's own details instead of a second full description. Validator-checked (exists, same kind, no cycle) and tested (`tools/generators/test_gen_prompt_extends.py`).
  `tools/art/extract_literals.py` moved repeated inline sentences (jewelry, anklets, effects, companions) out of 1,604 card slots into 67 pieces with every prompt unchanged. Still inline by design:
  generic fillers ("bare arms", "empty hands") and the long pose literals of the sisters' scenes (a motion piece needs many fields); converting more sister signature items to `extends` is open.
- **Frames, designs and shared poses (Oct 2026).** A base piece can be a frame with named gaps (`[[SLOT]]`); a piece that extends it fills them with `vars`, or takes them from one design file
  (`"varsFrom"`, kind `design`) so several pieces of one hero share one set of values. The ten sisters' four celestial armor pieces (plate, fitted plate, skin armor, skin suit) are now four frames
  in `wardrobe/armor/celestial/frame/` plus one `celestial-design.json` per sister (metal, breast and hip shapes, engraving, gem); every prompt is unchanged. Repeated scene poses and expressions became
  pieces too (kinds `pose` and `expression` in `motion/scene/` and `motion/expressions/scene/`, or in a hero's own folder): the 405-character lineup pose, the battle leap and the bond pose that all
  ten sisters (and every angel) carried inline. Still inline by design: generic fillers ("bare arms", "empty hands"), one-off pose sentences and each sister's own gown, robe and regalia wording (a frame fits
  them, but their grammar differs; do it when one is rewritten anyway).
- **Realism is a setting, not a rewrite (Oct 2026).** The default realm line says "a high-fantasy, Dungeons & Dragons-style realm ... living magic", which pulls Qwen toward illustrated, game-box art. A second realm,
  `realms/fantasy-cinematic`, describes the same fantasy backgrounds as a film still shot on location (real materials, natural light, subtle magic, with bans on cartoon, illustration and cel shading). A realm is
  chosen per card (`components.realm`), per hero (`art.defaultRealm`) or for a whole group (`_settings/studio.json` `realmByGroup`). Angel Primes, the test bed, uses the cinematic realm and grounded versions of
  the ten elemental realms (`backgrounds/fantasy/elemental/grounded/`); each angel also has a Signature (illustrated) twin in the old realm so the two looks sit side by side. The sisters are unchanged until
  you have compared renders. `python tools/art/style_audit.py` ranks the pieces that lean illustrated (the realm line, the elemental realms, forests, caves and libraries score highest; most other
  backgrounds are already grounded). Open: pick the look per set after the first comparison, rewrite the worst-scoring backgrounds, and decide where a card-like (cartoon) look is wanted on purpose.
- **Default images are pulled back from the workspaces (Oct 2026).** The photo and golden images a workflow loads are chosen inside ComfyUI (Load Image node) and live in `workspaces.json` (`photos`, `inputs`). `inputs --pull` reads the choices back
  (generated Qwen workflows only; placeholders and other heroes' images ignored; unanimous per hero and role, otherwise `MIXED`), `status` flags `inputs-changed`, `setup` pulls first and `inputs --reset` stops until a choice is pulled, so a reset cannot undo it.
  The ten women's photos and Angelica's were pulled this way. Angelica and Angelo now have the same Phase 1 and 2 as every other angel (the old `X_Pose` card and workflow are retired; her pastel bikini no longer carries heels).
- **Male wardrobe pack (Oct 2026).** Ten swimwear and underlayer pieces, twelve clothing sets (tuxedo, suit, military dress, trench coat ...) and one man's outfit for each of the 26 theme packs, written in
  realistic tailoring terms. The male angels now get wardrobe, theme, showcase and scene cards (about 105 prompts each, up from 57). Library pieces are written for women, so for a male hero the generator turns
  she/her into he/his/him in the finished prompt (`masculine()` in `gen_prompt.py`); before this the male angels' motion and hair prompts said "her". Male-angel themes use only male or unisex outfits,
  armor, headwear and jewelry; footwear, props and weapons unless tagged female.
- **One tree in every layer, with divisions (Oct 2026).** A group listed in `data/art/_settings/groups.json` files its work below a division folder
  (`angel-primes`: `female`, `male`, `pets`, `units`, `buildings`, `equipment`, `tactics`, `workers`, the Sovereign Dawn card categories with heroes split by sex). The same path is used for the identity
  (`data/art/heroes/angel-primes/female/seraphine.json`), the cards (`_sets/angel-primes/female/seraphine/...`), the prompts
  (`prompts/angel-primes/female/Seraphine/...`) and the ComfyUI output and workspace folders (`female/Seraphine/1_Alpha/...`), so the Angel Primes workspace is one tree for a
  whole test deck instead of a workspace per kind. The Drakn groups and the Elder Dragons stay as separate groups and workspaces (decided Oct 2026: ten story characters each, they
  will not grow); the Sovereign Territories set is expected to use the division scheme.

## Planned workspaces: what is left

The workspace tool skips any workspace whose `status` is not `active` or whose install folder is missing, so these can be prepared in the repo first.

| Workspace | Home of | Ready in the repo | Still to do |
| --- | --- | --- | --- |
| Drakn Bound | the ten bound heroes | identities and the `homes` rule | art sets and prompts (clone the sister kit: `scaffold-sister`), an install (clone Drakn Sisters, then `cleanup` it), set `status` to `active`, then `setup-workspace "Drakn Bound" --apply` |
| Elder Dragons | the ten dragons (text-to-image plates, heads, lairs) | identities, lair backgrounds, the `homes` rule | dragon card sets (heads, lairs, a plate stage), the install, `active`, `setup-workspace` |
| FireRed workspace | the photoreal engine's copies (today local test files, not in git) | `--engine firered` builds, `refresh-firered` | decide whether it gets its own install or stays a folder in each home; a FireRed template check |
| Sovereign Territories set | title, logo, icons, key art, plates | 22 workflows, 4 curated pulled into the repo | divisions for units, buildings, tactics art; the Drakn videos are not published there (publish a set only when you want it: `publish`) |

Order: Drakn Bound first (its heroes mirror the sisters, so the generators already fit), then Elder Dragons.

## Open decisions

| ID | Question | Notes |
| --- | --- | --- |
| O1 | 3 or 5 elements in the first public release? | Estimate from a finished Grass set (G1). |
| O2 | Does "exactly one hero per formation" survive? | Written before the art pipeline made a larger roster cheap. Revisit after a playtest. |
| O3 | How are vision cards obtained? | All 30 have empty `acquisition` today. Needs pack/reward/campaign rules, including the quest-earned Celestial edition, the pack-chance share and the codex teaser. |
| O4 | Transcendent format legality | 64 points exceeds any starter budget; decide special formats (Phase 2+). |

## Agreed next steps (Oct 8, 2026)

Five steps (0 to 4), done in this order. Each one ends with a pause: a summary of what was done, then the go-ahead for the next. Step 3 is itself split into phases (3a to 3d) with a pause after each.

| Step | What | Plan |
| --- | --- | --- |
| 0 | **Done (Oct 8).** Commit and push everything | Four commits on `ideation/hero-roster-10-elements`: (1) tooling, schemas, launchers and docs, (2) art and animation data, (3) generated prompts, (4) workflows and `workspaces.json`; then push to GitHub. Backups (`workflows/.sync/`) stay ignored. |
| 1 | **Done (Oct 8).** Alpha test sets: `angel-primes/alpha/female` and `alpha/male` | Two reusable test-bed heroes in a new `alpha` division, so any photo can be tried as an angel without touching a real angel's folders or output. A small version of the phases (see below). |
| 2 | **Done (Oct 8), rolled out to the repo and Angel Primes; Drakn workspaces pending.** Higher denoise for edits that change a lot | Raise the denoise of the Bare, footwear, pose, motion and scene edits (0.7 holds the pose too tight); let the prompt's positive likeness text carry the likeness. Find what you actually used in the Drakness `zz_Shots` first. |
| 3 | **In progress: 3a done (Oct 8).** Signature items for Angelica and Angelo | The same definition and art as the other twenty angels: element and alignment, wings, pet, signature weapon, armor, gown or attire, circlet, jewelry, elemental drift, and the cards that use them. |
| 4 | Sisters' companions from the Elder Dragon definitions | The sisters' dragon companions are text copied into companion pieces and cards; the Elder Dragon identity files are not used. Make one canonical companion piece per dragon from its identity and let each sister's piece extend it with only the scene placement. See below. |

### Step 1: alpha test sets

- **Where:** division `alpha` of group `angel-primes`, one test-bed hero per sex (`data/art/heroes/angel-primes/alpha/<slug>.json`, `_sets/angel-primes/alpha/<slug>/`, `prompts/angel-primes/alpha/<Hero>/`, workspace and output folder `alpha/<Hero>/...`). Their identity is as generic as Angelica's and Angelo's (the reference photo's own face, hair and eyes, no fixed look), so any photo works.
- **What is in the small set:** Phase 1 complete (Prime, Bare, Bare chest, Barefoot and Heels for the woman; Prime and Bare for the man), Phase 2 core (head, face close-up, a few head and body views, two hairstyles), two layer tests, one clothing and one armor card, a few motions and two scenes. Enough to see whether a photo makes a better angel; not the 180-card suite.
- **Using it:** put the photo in the `Angel Primes` input folder, pick it in the Prime workflow's Load Image node, run Phase 1 and 2, and compare. If it wins, give that photo to an angel (`inputs --set` or the same pick in her Prime workflow, then `inputs --pull`). `inputs --pull` also picks up the test photo, so it never overwrites an angel's.
- **Built (Oct 8):** hero names `Female` and `Male` (folders `alpha/Female/...`, `alpha/Male/...`), made by `scaffold_angel_set.py --alpha` (`bin\scaffold-angels.cmd --alpha`) from library pieces only, with a short studio library (`scaffold_studio_library.py --small`) and a shared `wardrobe/capes/wings/white-angel-wings`.
  The woman has 23 cards and workflows (+2 FireRed scenes), the man 20 (+2): Phase 1 (Prime, Bare, and for her Bare chest, Barefoot, Heels; no 2b experiments), Phase 2 (head, face close-up, 2 head views, 3 body views, 2 hairstyles), 2 layer tests, 1 outfit, 1 armor,
  Glamour and Signature scenes (cinematic realm), 3 motions. Their inputs and photos are in `workspaces.json` (`alpha_female_photo_944x1104.png` and `alpha_male_photo_944x1104.png` are placeholders: pick a photo in the Prime workflow, then `inputs --pull`).
  `gen_prompt.py --slug` now matches the hero folder only, so `--slug female` no longer means the whole `female` division. Not touched: every angel's folders, prompts, workflows, photos and output.

### Step 2: denoise

- **Today:** each card carries a hint (`~0.5-0.7`) and `denoise_for` picks the high end (0.7); a full redraw from the photo is 1.0 and drops to 0.7 when fed a golden image. At 0.7 the edit keeps the person and also the pose.
- **Plan:**
  - (a) Read the denoise values saved in the Drakness `zz_Shots` and curated workflows (Drakn Sisters and Drakness) to see what you settled on.
  - (b) Set the new values per stage in one table in `workspaces.json` (`denoise.stages`, over the card hints); proposed starting points are about 0.9 for Bare and footwear edits, motions and scene edits,
    tuned on one angel set first.
  - (c) Strengthen the likeness wording in the positive "Critical details" and fidelity paragraphs of the edit templates, because a higher denoise leans on the prompt.
  - (d) Apply with `denoise --reset` (preview first), which changes only the denoise widget in the repo and the workspaces, so seeds and inputs stay.
- **Risk to watch:** higher denoise loosens the likeness; compare a few renders per stage before regenerating everything, and keep hand-made `zz_` workflows untouched.
- **What you had used (read from the workspaces):** your hand-made Drakness armor edits (`zz_Curated_Drakness_Qwen_Armor_Bikini`, `..._Armor_Bone`) run at 0.9, and the Drakn Sisters `Alpha_2_Bare` shots at 0.8
  (one in the workspace); the older curated ones are at the template default. The generated defaults were 0.7 for edits and scenes, 0.6 for motion, head and hair.
- **Built and applied (Oct 8):** the range is in each stage template, not on the cards (the card `denoise` field is only a note), so the change is 16 template lines plus `denoise.golden` 0.7 to 0.9. New defaults (high end of the range):
  Bare, outfit, armor, clothing, scenes, showcases, body views and the golden-fed Barefoot, Heels and layer tests **0.9**; motion **0.95**; head and hair **0.8**; staged scenes **0.8**; Prime 1.0, final 0.8 and polish 0.4 unchanged.
  Full table in [art/comfyui-art-pipeline.md](art/comfyui-art-pipeline.md#denoise-is-the-key-lever).
- **Likeness in the positive prompt:** the Critical details block (hair, eyes, skin and the hero's own bust line, the same lines as the Prime) is now switched on for every edit stage in
  `TEMPLATE_KEY_DEFAULTS` (hair edits leave out the hair line, staged scenes keep eyes and skin only), and the `hair` and `scene-staged` templates got the slot.
  All 4,996 prompts were regenerated: 4,147 changed, and every changed line is the `Denoise` header or the added Critical details block (checked against git: 0 other lines).
- **Safety:** `denoise --reset` now keeps a denoise you set by hand in a workspace (a workspace file that differs from its repo copy is listed as `KEPT`; `--force` overwrites, with a backup) and takes `-w` to limit the workspaces. 5 new tests (43 in all).
- **Applied so far:** all repo workflows (5,274 denoise values, 3,883 prompt texts), the Angel Primes workspace (prompt text and 3,091 denoise values) and, on Oct 8, Drakn Sisters (1,911 aligned; 1,843 denoise values reset). **Not yet applied:** Drakness and Sovereign Dawn Series, which hold final art and may be in use. Per workspace, preview then apply:
  `comfy_workflows.py setup -w "<workspace>"` then `--apply`, then `comfy_workflows.py denoise --reset -w "<workspace>" --dry-run` and without `--dry-run`.
  `setup` only patches prompt text, so the workspace keeps its old denoise and `denoise --reset` lists nearly everything as KEPT (a hand-set guess).
  Compare against the repo's pre-Oct-8 values (`git show 2d23454d0:<path>`) to find the few that really were hand-set, then run `denoise --reset --force` (each changed file is backed up first) and put those back.
  In Drakn Sisters the only one was `Drakness_Qwen_Alpha_2_Bare_Figure` at 0.8, which was kept.
- **To check on renders:** that the 0.9 and 0.95 edits keep the face (if not, lower that stage's range in its template, regenerate, `update`, `denoise --reset`), and that the Critical details lines read well in the finished prompts.

### Step 3: signature items for Angelica and Angelo

- **3a. Definition. Done (Oct 8).** No cards are generated yet; this is only the definition, for you to review.
  - **Element and alignment:** Neutral (the eleventh element; added to the hero and pet schemas) and Balanced (neutral good), rank 5, as an eleventh pair beside the ten. Their palette is already pearl white and champagne gold, so the tone is "clean, with a quiet shine".
    A new `rotation` key (10) in their kits makes them take their own slice of every library pool instead of repeating Sandalyn and Baracel's rank-5 picks.
  - **Element tables:** material (soft white light, drifting pale feathers), motif (a single white feather within a plain ring), weapon family (polearms), the animation motion `feathers-drift`, and a new realm: `backgrounds/fantasy/elemental/meridian-vale-realm` (a high white-stone plateau) with its grounded twin.
  - **Identity:** each has a `profile` like the other angels (archetype: the first herald and the first sentinel; inspired by the messenger and the guardian angels; wings; pair; pet).
  - **Wings and pets:** pearl-white wings edged in champagne gold (his with dove-grey primaries); pets Plume (a pearl-white dove) and Ward (a lean pale hound), neither a dragon, with `companion` pieces for the scene slot and the two-way links to their angels.
  - **Kits** (`_kits/angel-primes/angelica.json`, `angelo.json`): three underlayers, three outfits, two armors, four motions, heels and a signature scene, picked to differ from the layers and clothing they already have; the paladin plate for her, the parade plate for him.
  - **Generators:** once a kit exists the normal kit builder takes over for them (it only adds what is missing, so their hand-picked cards stay); the "keep it pure" filter for lawful angels also skips shadow, umbral and raven pieces.
  - **To confirm before 3b:** Neutral at rank 5 for the pair, the two pets, and the wings.
- **3b. Signature pieces. Done (Oct 8).** The same six signature pieces as every angel (weapon, armor, gown or attire, circlet, jewelry, elemental drift), each extending a library piece plus their element and alignment tone, and the signature armor and gown wardrobe cards.
- **3c. Cards. Done (Oct 8).** The rest of the angel suite around those pieces (showcases, signature, battle, spell-calling and glamour scenes, theme scenes, video), keeping their hand-picked layers, clothing and modern scenes.
- **3d. Regenerate and verify. Done (Oct 8).** Angelica has 164 cards and Angelo 89, with the same signature pieces as every angel (picked by the kit's `signature` override: her paladin holy plate, spear, column gown and silver circlet; his full plate, halberd, long coat and laurel wreath).
  Validator OK, prompts generated (0 failures, no she/her in Angelo's prompts), workflows made for Qwen, FireRed and MiniMax, deployed to Angel Primes (3,386 aligned, 0 stale, 0 missing), Phase 1 and 2 audit 0 problems.

### Step 4: the sisters' companions from the Elder Dragon definitions. Done (Oct 8)

- **Result:** each dragon has two frames, `data/art/dragons/elder-dragons/<slug>/companion/<slug>-companion.json` (the identity's description, with `[[PLACEMENT]]` and `[[DETAIL]]` gaps) and `<slug>-companion-distant.json` (the opening and name only, for scenes that word the dragon themselves).
  The 20 sister companion pieces and the 20 sentences that scene cards carried inline (now 20 new pieces, 40 in all) extend a frame and fill the gaps with `vars`; the cards name the piece. `tools/art/dragon_companions.py` writes it all (re-runnable; `--apply`), and every conversion is asserted to join back to the old text.
  All 5,271 prompts came out byte-identical, so nothing changed in the images' wording yet; the gain is that an edit to a dragon's identity now reaches the frames, and the full-frame scenes through them.
- **Validator:** a sister's companion piece must extend a piece under `data/art/dragons/`, and a sister scene must name its companion as a piece, not type the dragon (2 mutation cases, both in `--quick`). Pieces under `dragons/<group>/<slug>/` are now validated as pieces.
- **Still hand-worded:** 23 scene texts describe the dragon their own way (distant silhouettes, close-ups), and 10 of them cite only one of its colours or miss one (for example Venomis, tarnished brass). They use the distant frame; review them when you want the dragons to match their identities exactly (`dragon_companions.py` lists them).
- **Original plan, kept for the record:**

- **Today:** each sister has two companion pieces (`heroes/drakn-sisters/<slug>/companion/`, for example "her aligned Elder Dragon, Terrador, a vast distant silhouette on the far ridge...") and some scene cards, such as the Draknara Bond scene, carry the dragon as an inline sentence.
  The Elder Dragon identity files (`data/art/dragons/elder-dragons/<slug>.json`: description, silhouette, scale texture, wing membrane, horns and crest, elemental venting) are not used by them, so the same dragon is described several ways and an edit to the dragon changes nothing in the scenes.
- **Proposed reconciliation:** (1) audit every sister companion piece and inline companion sentence against the dragon's identity; (2) one canonical companion piece per dragon, written from the identity (`data/art/dragons/elder-dragons/<slug>/companion/`, kind `companion`, the dragon as it looks in a scene);
  (3) each sister's companion pieces `extend` it and add only the scene placement with `+` (a distant silhouette on the ridge, towering beside her with its head lowered, ...), and the cards reference pieces instead of carrying sentences; (4) a validator check that a sister's companion piece extends her dragon's; (5) regenerate and review the prompt differences, which will be intentional wording changes where the dragon's own description now shows through.
- **Why this way:** the dragon stays defined once, in its identity, and what a sister adds is only what changes from scene to scene. The alternative, a generator that builds the companion text from the identity at prompt time, hides the wording and cannot be adapted per scene.
- **To decide at the start:** whether the canonical piece is written by hand from the identity or generated by a small tool (proposed: a tool, re-runnable, so a change to a dragon reaches the pieces), and how much of the identity belongs in a scene (proposed: silhouette, scales, wings, horns and venting, not the lore).

## Workspace sync and the zz_ reconcile (Oct 8)

| Workspace | State | What is left |
| --- | --- | --- |
| Sovereign Territories | 18 aligned, 0 stale | its 4 `zz_Curated` items are identical to the repo and their prompts are fully covered by the art data: safe to delete from the workspace |
| Drakn Sisters | 1,987 aligned, 0 stale | its 38 `zz_Curated` are identical to the repo; 25 shots kept; `zz_Shots/alpha/bare/Drakness_Qwen_Alpha_2_Bare_Skin` is a different seed from the Drakness workspace copy (see below) |
| Drakness | 284 aligned, 0 stale | refreshed and its denoise reset to the repo values (Oct 8); 37 `zz_Curated` and 5 shots are identical to the repo and now covered by the art data (see the reconcile below); `Armor_Bikini_00001` is in the repo and was added back |
| Angel Primes | 3,650 aligned, 0 stale, 0 missing, 0 install-only | 35 numbered saves are shots in the repo; the 62 clone leftovers were moved to `workflows/.sync/backup` (22 male `X_Pose` files with no prompt, and 40 MiniMax videos that were rebuilt from the `7_Video` prompts, which come from `data/animation`) |
| Sovereign Dawn Series | 174 aligned | nothing |
| Drakn Bound, Elder Dragons | planned, no install | see the planned workspaces table |

- **Numbered saves are shots (new).** A workflow ComfyUI saved from a render (`Azaline_Qwen_Alpha_1_Prime_00004_.json`) keeps that render's seed. Left loose in the list it is now a shot: `status` shows `shots-new`, `pull --shots` keeps it in `workflows/_shots/<set>/<Hero>/`, and `cleanup` and `tidy` leave it alone. 35 were captured from Angel Primes. Moving a good seed into the art data (so the generated workflows carry it) is still to design.
- **Two seeds, one name.** `Drakness_Qwen_Alpha_2_Bare_Skin` exists as a shot in Drakn Sisters (seed 517397163969845) and in Drakness (seed 119517098111188). A repo shot holds one, so `pull --shots` now keeps the first and reports `CONFLICT`; rename one in its workspace to keep both.
- **The zz_Curated reconcile (Oct 8).** Every curated prompt was compared with `data/art`. Result: **hair 12 of 12** and **motion 8 of 8** trace to art pieces by their `sourceVariant`; the Bone, Raven, Iridescent and Gown armor and clothing were already folded in (the pieces note the prompt they came from); the X_Head and both X_Pose prompts are replaced by the Prime, Bare and head cards; the 4 Sovereign Territories prompts are fully covered.
  Four designs were missing and are now art: the violet **Chain Bikini** armor, the **Elegant** armor (ornate bikini armor under glowing waist drapes) with an **Elegant Pointed Toe** variant, and the **Bikini-Strap Gown**.
  They are reusable wardrobe pieces (`armor/bikini/chain-disc-bikini`, `ornate-bikini-armor`, `capes/drapes/ethereal-waist-drapes`, three heels, `clothing/gowns/bikini-strap-evening-gown`) in her palette tokens, plus four Drakness cards, with prompts and Qwen workflows deployed. The Raven boots gained the matching upper-left thigh band.
  **Not captured, to decide:** the per-outfit lipstick and nail colours (the curated prompts use Deep, Light or Midnight Violet by outfit; the identity holds one value each); the dimples line of `X_Pose_Original`; the Raven and Bone *battle stance* poses and the Gown_Pose wording (the closest are the Bench motion cards).
- **FireRed 1_Alpha everywhere (new).** Every 1_Alpha step (Prime, Bare, Footwear, 2b experiments) of every hero has a FireRed workflow beside the Qwen one (244 built), and the Angel Primes `alpha/female` and `alpha/male` sets carry the whole suite in both engines (23 and 20 each), all deployed to Angel Primes and Drakn Sisters (and the 9 for Drakness).
  The FireRed steps read the same input images as their Qwen twins, so a FireRed Bare starts from the Qwen Prime; pick another image in ComfyUI to run a pure FireRed chain. Which engine each phase should use is still a test, and the documents that name one are assumptions until you decide.
- **Filename case (Oct 8).** Git tracked 20 older-angel prompts and workflows as `Head_Face_Closeup` while the generator writes `Head_face_closeup`; a branch switch rewrote them and Angel Primes showed 20 missing. They are renamed to the generator's case. Many "missing" and "install-only" pairs that differ only by case point to this.

## Negations in prompts (Oct 9)

"Do not recolour" recoloured and "no pale areas" paled: a model reads a negation as the thing it names. A scan of all 5,475 positive prompts found **39,755 negation hits**, nearly all from a few shared sources (the angels' palette strings, the eye-effect pieces, the contour pieces, the sisters' build text, the studio lighting, the realms and the shared templates).
They are removed at the source (243 data files plus the hair-motion scaffold; about 50 rules, each dropping a tail whose positive half was already in the sentence) and all prompts regenerated: **0 command phrases ("do not", "never", "avoid") and 0 flip-risk phrases are left**; the generic review list fell from about 31,000 hits to about 360 (descriptive ones such as "without bulk"), plus 1,428 in allowlisted video prompts.
Examples: `do not recolour` (5,687), `do not alter undertone` (3,260), `no backlight or rim light` (3,300), `no gap between them ... rather than drooping` (2,540), `not glowing` (1,886), `no pale areas` (1,447), `no footwear` (1,299), `not squinting` and `no squint` (about 2,500), `nothing from the modern world` (929), `no breeze` became `still air`, and "Change nothing else: keep" became "Keep".
`tools/art/negation_audit.py` (`bin\negation-audit.cmd`) now keeps it that way: `validate.cmd` runs it in check mode, and the rules and allowlist are in `data/art/_settings/negation-audit.json`. The README rule is "Write positives, not negations".
**Left on purpose:** the video prompts (no negative prompt on the video model), gameplay-card lore (the card owns it), brand text ("no text"), and the 2b covering experiments, which say "only these three coverings" and "no clothing at all" as part of what they test.
**Also done (Oct 9):** "lightly enhanced" and "gently enhanced" in the angels' skin, hair and eye strings (24 identities) invited change as much as the old negatives did, so they now say "exactly as in the reference image".
They keep only the detail (evenly toned, healthy shine and dimension, crisp definition).
The eye string is now "irises in their natural colour ..." so it also reads correctly inside the glow pieces (it used to say "natural natural"). 3,260 angel prompts regenerated and deployed.
If one photo needs brightening, do it on that angel's own identity, not as a default.

## Angel Primes: builds, colours, roster docs (Oct 9)

- **Slender women.** Camaris, Sandalyn, Remiah, Nyxene, Ravaelle and Haniya had strength wording (Sandalyn came out "ape" muscular). All 11 angel women are now slender; the men stay a deliberate mix of lean, heroic and heavy.
- **Colours forced.** All 22 angels now define hair, eye and skin colour (plus their negative lists), so the 1_Prime and 2_Bare prompts change the photo to match. Angelica and Angelo used to follow the photo; their colours are a first choice that can be edited. The bound heroes gained `hairColorNegatives` (they already forced hair, eyes and skin).
- **Standard male figure.** Male Prime cards get `figureProfile: standard` like the women (`standardFigure.male` in `phrases.json`; the scaffold sets it for both sexes). The individual build is applied at 2_Bare.
- **Audit.** `python tools/art/identity_audit.py` (`bin\identity-audit.cmd`, run by `validate.cmd`) checks every angel, sister and bound hero: colours defined and carried by the Prime prompt, the Bare prompt applies the build, no strength words on a female angel. The alpha test heroes follow the photo on purpose. Bound heroes still use the older `X_Pose` Prime card.
- **Docs.** New `angel_primes_codex.md` and `angel_primes_physique.md`; `ideation_codex.md` is now `sovereign_dawn_codex.md`. Series IDs fixed: Sovereign Dawn is `SD-###` (the roster wrongly said `ST-###`); the angels are planned as `AP-###` (proposal AP-001 to AP-022, herald pair first). The roster tables no longer carry art-progress columns; use `python tools/workflows/comfy_workflows.py inputs --status`.
- **Open:** spells and abilities for the angels, the story link between each angel and the same-element Drakn sister, gameplay cards, and whether the roster pages should be called `*_roster.md` since the JSON is the real codex.

## Library gaps (audit of Oct 8)

`tools/art/library_audit.py` (`bin\library-audit.cmd`) measures where the library is thin, over-used or built from shortcuts, and is meant to be re-run as the library grows. **Over-use is the signal, not unused pieces** (pieces are written ahead of their scenes):
a piece doing most of a folder's work for many heroes means the look repeats, unless it is on purpose (a studio default, ten sisters in one base robe), which is recorded with its reason in `data/art/_settings/library-audit.json`. What it found, in the order to work through it:

| Order | Gap | Result | Still open |
| --- | --- | --- | --- |
| 1 | Robes | **Done.** 15 robes; each angel's robe scene matched to element | more robe families when a theme needs them |
| 2 | Over-used pieces | **Done for the angels.** Modern backgrounds (32, was 14), shared scene effects (18), flats and sandals (10 each), staves (8), wands (7) and the six armor families (+3 each) were filled and spread across the angel cards by element or rotation (238 cards); the audit is clean except for the allowlisted sharing | the Drakn Sisters still share their scenes on purpose (recorded in the allowlist); pieces nothing uses yet (8 helms, 7 cloaks, 6 bracers) are information only |
| 3 | Jewelry | **Done for the angels' occasion showcases.** 31 atomic pieces and nine sets; editorial, glamour and city-street showcases wear a set in each angel's own metal and gem (121 cards); the sets carry no belly ring so they suit gowns | move the remaining cards off the old bundles (`library_audit.py` lists them under SHORTCUTS); belly rings go on bikini and armor cards one by one; grow headwear (circlets, hats, hoods are 3 each) |
| 4 | Makeup and highlights | **Done to start.** 50 makeup looks (was 3) and 20 highlights (was 14); the female angels' 200 occasion showcases each wear a look, spread so no family repeats one | per-outfit lip and nail colour is not supported (one value per identity); only showcase and scene templates render makeup; more looks as trends move |
| 5 | Hair | 10 short styles added (6 male, 4 female) | the male angels' default hair is still the textured crop (allowlisted until their photos are chosen); add hair study cards for the new styles |
| 6 | Races | not started: seven non-human races are one `race.json` each | flesh out when the `{{RACE}}` slot is wired for bound heroes |

## Scenes: series, character and theme (Oct 8)

Scenes now have three tiers (explained in [data/art/README.md](../data/art/README.md#scenes-series-character-theme)): a **series** the whole cast shares for the marketing pictures (Lineup, The Dawn, The Bond, Robe, Casting, Battle, Enchanted Evening, Signature), **character** scenes unique to each hero, and **theme** scenes.

| Added | For | Count |
| --- | --- | --- |
| **Lineup** (the flat-backdrop group cut-out the sisters already had) | the 22 angels | 22 |
| **Duty** and **Quiet**, from the alignment rank: Vigil, Blessing, Judgment, Reckoning, Exile; Cloister, Garden, Study, Watch Fire, Ruin | the 22 angels | 44 |
| **Domain**: the element at work in its realm (11 recipes) | angels and sisters | 32 |
| **Craft**: what the class does (Shaman, Shadow Knight, Bard, Necromancer, Summoner, Wizard, Enchanter, Cleric, Druid, Magician, Alchemist) | the 10 sisters | 10 |
| **Celebration** from a new theme pack, by element: coronation, masquerade ball, midwinter festival, siege defense, victory feast | angels and sisters | 32 |

That is 140 new cards, each with a prompt, a Qwen and a FireRed workflow, deployed to Angel Primes, Drakn Sisters and Drakness. The recipes live in `data/art/_settings/scene-recipes.json` (add a scene type there, then `bin\scaffold-characters.cmd`); the validator checks every rank, element and sister class has one.
Also new: two realms (`fantasy-gothic` for the fallen and grieving, `fantasy-pastoral` for gentle scenes) and five theme packs (31 in all, with a new `ceremony` group).

**Realistic realms for every element and class (Oct 8).** Each sister now has her own country and place, in the library so the males and later common and uncommon cards can use the same ones:
- **11 element homelands** (`realms/<element>-lands`): red-rock canyonlands (Draknara), ashen volcanic badlands (Draknora), tidal coast and reefs (Draknisa), glacial highlands (Draknira), windswept highlands (Draknava), storm plains (Drakneta), ancient greenwood (Drakniya), mangrove bayou (Draknoxa), radiant uplands (Drakniss), fogbound moors and crypts (Draknare and Drakness) and the meridian highlands (the neutral pair).
- **55 country environments** (`backgrounds/fantasy/country/<element>/`, five per element, tagged establishing, road, settlement, weather and night) and **33 class haunts** (`backgrounds/fantasy/haunts/<class>/`, three per class, eleven classes).
- **A realm series for the sisters** (`5_Scenes/realm/`): Homeland, Wayfarer, Settlement, Weather and Nightfall in her own country, plus her class's Haunt, 60 cards; her Craft scene now also uses her class's haunt and her element's realm. All have prompts, Qwen and FireRed workflows, deployed to Drakn Sisters and Drakness.
- **The angels can opt in** to the same series (`scaffold_angel_set.py --realm`, 110 cards); not run yet, to keep Angel Primes quiet while you test.

**Marketing series, still to decide:** the series scenes are the same pose and template for everyone but each hero stands in her own element realm, so a composite needs either the Lineup (flat backdrop) or a shared backdrop per series scene. A "series cut-out" variant of The Dawn, The Bond, Robe and Casting on one common backdrop would make them composable like the Lineup; say if you want it.

**Still open (needs your thinking):**
- **More character scenes.** Each hero could have more: a scene per sister's lore, the pair (an angel with her paired angel), the pet's own scene, seasonal portraits at home, travel and adventure, sports and action, night city.
- **More realms.** Noir city, historic, desert and storm, and a place for each of the sisters' pets and dragons' lairs in the same realistic style; each with backgrounds, effects and wording of its own.
- **More themes.** Valentine, lunar new year, slavic winter, fey court, gaslamp, circus, jungle explorer; the audit does not cover themes yet, and theme makeup, jewelry and robes could extend the new library pieces.
- **Moving over.** The sisters' pieces and the older bundles can be rebuilt on the atomic pieces whenever you want; that changes their prompts, so it is a choice.

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
