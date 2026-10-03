# `data/art/` — Structure Reference

**Status:** Living document · **Last updated:** 2026-10-02

This is the authoritative explanation of how `data/art/` is organized. Read this before adding any
new hero, race, component, or card-production folder — the goal is that we never have to reshuffle
directories again as heroes, races, dragons, pets, buildings, armor, weapons, and new card
productions get added.

Referenced from [`docs/art/comfyui-art-pipeline.md`](../../docs/art/comfyui-art-pipeline.md) and
[`docs/art/prompt-pattern.md`](../../docs/art/prompt-pattern.md).

---

## The two layers (this is the core idea — everything else is detail)

1. **Definitions** — reusable facts: who a hero *is* (palette/physique), and reusable style
   pieces (hairstyles, motion/poses, armor/clothing/weapons). These files don't generate anything
   by themselves. Within definitions there's a **specificity spectrum**, most generic to most
   specific — pick the narrowest tier a piece actually needs, default to the widest:
   - **`wardrobe/<kind>/<family>/`** — cross-cutting pieces usable across outfits, heroes, and
     races ("a long sword", "a kite shield", a plain necklace style any outfit could use). The
     default home for a new piece unless it has a real reason to be narrower.
   - **`races/<race-slug>/<kind>/<family>/`** — shared by every hero/NPC of that race, narrower
     than wardrobe but not locked to one named character (a Dark Elf-specific hair texture, an
     Ogre-scaled armor silhouette). Hair currently lives here (`races/human/cosmetics/hair/`).
   - **`heroes/<group>/<hero-slug>/<kind>/`** — signature items unique to ONE named hero (e.g. a
     hero's own signature weapon), living alongside that hero's identity file in the same group
     folder (`heroes/drakn-sisters/drakness/armor/` next to `heroes/drakn-sisters/drakness-thorne.json`).
   A hero can draw from all three tiers at once — most of her look might be wardrobe/race-shared,
   with one or two deliberately unique signature pieces. `motion` sits outside this spectrum
   entirely (its own top-level category) since poses are action, not appearance.
2. **Assembly** (`_sets/<group>/`) — the testing/working folder where a group's hero definition +
   components + a stage template get pulled together into an actual generated prompt. Each
   `_sets/` folder is named **identically to the definitions-layer group it mirrors**
   (`_sets/drakn-sisters/` ↔ `heroes/drakn-sisters/`) — no separate "-set" word needed once it's
   already under `_sets/`. This is deliberately **not** a 1:1 mirror of a game card series — a real
   series (like Sovereign Dawn) can pull from several groups (drakn-sisters today; drakn-bound and
   elder-dragons later), and that series↔group mapping lives on the `data/cards/` side via asset-ID
   references, not via art-side directory nesting. `angel-primes` doesn't correspond to any real
   card series at all — it's a calibration/testing sandbox for proving prompt changes against
   arbitrary reference photos before touching real heroes.

Only the **assembly** layer's `tools/generators/gen_prompt.py` output is ever regenerated/committed
as a finished prompt. Everything in the **definitions** layer is only ever *referenced*.

### Decomposed pieces vs. one complete chunk — which do I use?

Some things (Figure, Eyes, Lips, Expression) are always a single inline template line — there's
only ever one of them per render, nothing to swap independently, no reuse benefit. Other things
(jewelry, a cape, a held weapon) are worth pulling into their **own small piece file**, referenced
by *slot name* from a card's `components` dict (see below), specifically when:

- it's plausible you'd **swap it independently** while keeping the rest of the outfit (a different
  weapon with the same armor — this is exactly what `bone-scythe.json` / `bone-dagger.json` prove), or
- it's plausible the **same piece gets reused** across more than one outfit or hero (a generic
  bracelet, a cape, a necklace style).

If neither is true — the piece only ever exists as part of one specific design and swapping it
would stop being "that outfit" — just write it as part of that outfit's own `wearing`/`arms`/etc.
piece under the hero's signature folder. Don't decompose further than the reuse actually needs.

---

## Scopes, themes and kinds: where does a new piece go?

Every piece has two coordinates: a **kind** (what it is) and a **scope** (how widely it applies). Every scope uses
the same internal layout, `<kind>/<family>/<piece>.json`, so a piece can move between scopes without changing shape.

| Scope | Folder | Put a piece here when |
| --- | --- | --- |
| core | `wardrobe/`, `cosmetics/`, `backgrounds/` | it works in any theme, or it is the standard D&D fantasy default |
| race | `races/<race>/` | it exists because of anatomy (hair texture, skin, ears, horns) |
| theme | `themes/<theme>/` | it belongs to a culture or event pack (Greek, Roman, Thanksgiving, ...) |
| hero | `heroes/<group>/<slug>/` | it is one named hero's signature item |

Rules of thumb: theme beats race (a Greek gown is `themes/greek/` even for a dark elf; the dark elf's skin and hair
live in the race); hero beats everything (a signature weapon stays with its hero); when unsure, start in the narrowest
scope and promote it to core the second time it is reused.

**Theme first, not kind first.** A themed deck is one unit (outfit, jewelry, makeup, hair, background): putting
`themes/greek/` on the outside means one folder to add, version, ship or retire (an event pack like Thanksgiving is
switched on for a period and then removed), and a tool can list "everything in this theme". Kind-first
(`wardrobe/armor/roman/`) would scatter one theme across a dozen folders.

**Kinds** (folder under a scope, token slot a card fills):

| Kind folder | Slot | Notes |
| --- | --- | --- |
| `wardrobe/armor`, `wardrobe/clothing` | `wearing` | body garment; armor families by material (plate, leather, mail, robes) |
| `wardrobe/headwear` | `headwear` | optional line: omitted when a card sets none |
| `wardrobe/jewelry`, `accessories`, `footwear`, `capes` | `jewelry`, `legs_feet`, `back`, ... | |
| `wardrobe/weapons`, `wardrobe/props` | `holding` | weapons vs held non-weapons (book, harp, cornucopia) |
| `wardrobe/swimwear` | `underlayer` | what the A-pose wears |
| `wardrobe/effects` | `effects`, `eye_effect` | |
| `cosmetics/makeup` | `makeup` | replaces the default studio face-styling line; optional line in scenes |
| `races/*/cosmetics/hair`, `themes/*/cosmetics/hair` | `component` on a hair card | |
| `backgrounds/<realm>/` | `background` | realm folder is mandatory (fantasy, modern, studio) |

**A theme manifest** (`themes/<theme>/theme.json`, `type`: `culture` or `event`) names the pack. A theme's pieces use
`{{PRIMARY}}` / `{{ACCENT_SOFT}}` so each hero renders them in her own colours; an event that needs its own season
palette sets `overrides.palette` on the card (see `drakniya-scene-thanksgiving.json`).

**Piece ids equal their paths** under `wardrobe/`, `cosmetics/` and `themes/` (validator-enforced), so a move can never
leave a stale id. To move or rename a piece safely use the reference-aware tool, never plain `mv`:

```bash
python tools/art/art_refs.py where-used wardrobe/weapons/swords/greatsword
python tools/art/art_refs.py move wardrobe/footwear/boots/combat-boots wardrobe/footwear/boots/knee/combat-boots --dry-run
```

A pure move must leave every generated prompt byte-identical; regenerate and check `git status prompts/`.

**Optional template lines.** A template line starting with `?` (e.g. `?Headwear: {{HEADWEAR}}.`) is printed only when
every token in it has a value, so slots like headwear or makeup cost nothing for cards that do not use them.

## Where rendered images live (convention)

The prompt file path is the identity of an image. A rendered PNG sits at the same path under `assets/art/` with the
extension changed: `prompts/drakn-sisters/Drakniya/scene/Drakniya_Scene_Thanksgiving.txt` becomes
`assets/art/drakn-sisters/Drakniya/scene/Drakniya_Scene_Thanksgiving.png`. Because the card's `output` field already
defines the prompt path, the image path is derived, not stored twice; a tool (or the validator, later) can check that
it exists, and Unity import can mirror the folder. Large binaries should use Git LFS or external storage. Still to
decide (STATUS C1): how the gameplay card's `portraitAsset` / `fullArtAsset` fields point at these.

## Directory map

```text
data/art/
├── _templates/                     Stage templates — static scaffolding, {{TOKEN}} placeholders.
│   └── heroes/                     Archetype: humanoid. (pose-female-human.txt, pose-male-human.txt,
│                                   pose-view-human.txt (turnaround from the A-pose),
│                                   head-human.txt (any angle/framing/expression), hair-human.txt,
│                                   motion-human.txt, armor-human.txt, clothing-human.txt,
│                                   scene-human.txt, scene-with-outfit-human.txt,
│                                   scene-with-companion-human.txt, scene-minimal-human.txt,
│                                   scene-combat-human.txt — no casting-eyes-glow line, for
│                                   non-caster martial heroes). Naming: `<stage>-<archetype>.txt`;
│                                   a SHOT (cream studio) is any non-scene stage, a SCENE adds a
│                                   realm, background and effects.
│   └── dragons/                    ✅ Archetype: Elder Dragon (pose-dragon.txt, head-dragon.txt) —
│                                   text-to-image, NOT img2img (no incoming reference to edit;
│                                   a dragon is generated entirely from its own description).
│
├── _sets/                          ASSEMBLY: one folder per GROUP, same name as its definitions-
│   │                               layer twin below — the recipe .json files that actually
│   │                               generate prompts. Testing/working folders; which real card
│   │                               series (if any) consumes a group's output is tracked on the
│   │                               data/cards/ side, not here.
│   ├── drakn-sisters/              ✅ 101 cards (10 heroes × pose/head, 44 hair + 25 motion + 2
│   │   └── <slug>/<stage>/<family>/*.json    armor + 1 clothing for Drakness; all 10 now have a
│   │                               signature scene — 3 bespoke [Drakness/Draknora/Drakneta],
│   │                               7 first-pass minimal reusing proven wardrobe defaults)
│   ├── angel-primes/                ✅ 4 cards (Angelo + Angelica × pose/head)
│   │   └── <slug>/<stage>/<family>/*.json
│   ├── drakn-bound/                ✅ 40 cards (10 male heroes × pose/head/armor/scene) — each now
│   │   └── <slug>/<stage>/*.json   has its OWN signature weapon (heroes/drakn-bound/<slug>/weapons/),
│   │                               not just the shared archetype-group default
│   └── elder-dragons/              ✅ 20 cards (10 dragons × pose/head) — text-to-image only, no
│       └── <slug>/<stage>/*.json   scene stage yet (dragons aren't humanoid, no outfit/companion
│                                   concept applies to them the way it does a hero)
│
├── heroes/                         CATEGORY: humanoid hero definitions, grouped by roster.
│   ├── drakn-sisters/              ✅ GROUP: the 10 Thorne sisters (an actual Sovereign Dawn roster).
│   │   ├── <slug>-thorne.json      art identity (palette/physique); links to its card by cardId
│   │   ├── drakness/               ✅ hero-SIGNATURE pieces: armor/ (bone, iridescent, raven),
│   │   │                           clothing/, weapons/, effects/
│   │   └── draknora/               ✅ hero-SIGNATURE pieces: armor/, weapons/, effects/, and her
│   │                               first companion/ piece (pyraxis-flight.json)
│   ├── drakn-bound/                ✅ GROUP: the 10 male heroes bound to the sisters in the story.
│   │   └── <slug>.json             art identity (palette/physique, male build/chest/waist/legs schema),
│   │                               linked to its card by cardId — first-pass invented palettes, no
│   │                               archived source material.
│   └── angel-primes/               ✅ GROUP: Angelo Prime / Angelica Prime — calibration test-bed
│       └── <slug>.json             heroes (testBed: true, no card), not part of any real card series.
│
├── races/                          🔶 CATEGORY: shared by every hero/NPC of a race — narrower than
│   │                               wardrobe, not locked to one named hero.
│   ├── dark-elf/
│   │   └── hair/<family>/*.json    one skeletal example (midnight-cascade.json), not yet wired
│   │                               to any hero's hairStyleComponent
│   └── human/                      ✅ the Drakn sisters' race — hair moved here from the retired
│       └── cosmetics/              "universal" bucket, since every current style was designed
│           └── hair/<family>/*.json    for human presentation specifically (44)
│
├── wardrobe/                       ✅ CORE wardrobe: generic pieces + the standard D&D fantasy set, laid
│   │                               out <kind>/<family>/<piece>.json. A card's components pull
│   │                               interchangeable slot-fillers from here (see "Scopes" below).
│   ├── armor/{plate,leather,mail,robes,bikini}/
│   ├── clothing/{gowns,dresses,sets,robes}/
│   ├── headwear/{helms,circlets,crowns,hoods,hats}/
│   ├── weapons/{swords,daggers,polearms,staves,bows,wands,blunt,axes,shields}/
│   ├── props/{tomes,...}/          held items that are NOT weapons (books, instruments, vessels)
│   ├── jewelry/{necklaces,sets,bracelets,earrings,anklets,belts,rings}/
│   ├── footwear/{boots,heels,sandals,barefoot}/
│   ├── capes/{cloaks,short-capes,mantles}/
│   ├── accessories/{bags,quivers,bracers,gloves}/
│   ├── swimwear/*.json             A-pose UNDERLAYERS, swappable (triangle-bikini default,
│   │                               swim-brief default male, multicolor, high-waist, bandeau,
│   │                               sporty, one-piece, board-shorts, athletic-trunks)
│   └── effects/{ambient,eyes}/
│
├── cosmetics/                      ✅ CORE cosmetics not tied to a race: makeup/<family>/*.json
│                                   (soft-glam, smoky-eye, statement-lip). Core human hair stays
│                                   under races/human/cosmetics/hair/.
│
├── themes/                         ✅ THEME PACKS, one self-contained folder per culture or event:
│   │                               greek, roman, egyptian, norse, celtic (culture) and
│   │                               thanksgiving (event). Each has a theme.json manifest and
│   │                               the same layout as the core: wardrobe/<kind>/<family>/,
│   │                               cosmetics/{hair,makeup}/<family>/, backgrounds/<realm>/<family>/.
│   └── <theme>/theme.json          (schema: _schema/theme.schema.json)
│
├── dragons/                        ✅ CATEGORY: all 10 Elder Dragons seeded (elder-dragons/*.json),
│   └── elder-dragons/              aligned by element to the female Drakn sisters per the codex's
│                                   Element Alignment table. Only Pyraxis is grounded in archived
│                                   content; the other 9 are first-pass invented, colour-grounded
│                                   in their paired hero's own palette. Each now has its own
│                                   text-to-image A-pose/Head via _sets/elder-dragons/ (see
│                                   _templates/dragons/) — but no outfit/scene stage yet, since a
│                                   dragon doesn't wear armor/clothing the way a humanoid hero does;
│                                   Pyraxis is additionally referenced as a companion/ placement
│                                   piece inside Draknora's own scene (two different concerns).
├── pets/                           ⬜ CATEGORY: future.
├── buildings/                      ⬜ CATEGORY: future.
├── realms/                         ✅ CATEGORY: the WORLD a scene lives in — fantasy.json (canon, the
│                                   default for every scene) and modern.json (fun tests, not canon).
│                                   A realm supplies the setting sentence ({{REALM}}) and the bans
│                                   that keep the other world out ({{REALM_NEG}}: modern objects,
│                                   cars, neon ... for fantasy).
├── shots/                          ✅ CATEGORY: what makes a STUDIO SHOT (cream backdrop, flat light)
│   ├── views/body/*.json           different from a scene: camera/subject orientation for the
│   ├── views/head/*.json           reference library — front, 3/4, profile, back, looking down, chin
│   └── framing/*.json              up, over the shoulder ... (left/right are camera-relative), and
│                                   how tight a head shot is (bust-up, face close-up, chest and hair).
└── backgrounds/                    ✅ CATEGORY: split by REALM, and the folder IS the realm:
    ├── fantasy/                    canon scene backgrounds (D&D-style: castle/, cityscape/ (a medieval
    │                               citadel, never a modern city), dungeons/, elemental/, evening/,
    │                               forests/, frozen/, coast/, mountains/, highlands/, canyon/, swamp/,
    │                               temple/, tavern/, camp/ — one or more per element).
    ├── studio/                     cream-even (default for every cream-backdrop stage),
    │                               cream-beauty-light, white-high-key, grey-seamless — the lighting
    │                               lives in the piece, not buried in templates.
    └── modern/                     real-world locations (city street, cornfield, kitchen, rooftop) for
                                    realism experiments only, never game art.
```

**"Universal" was retired.** It broke down once dragons/buildings were on the horizon — armor/
weapons/clothing aren't universal to the whole game, only to humanoid characters, and even within
that scope the content that actually exists was written for human presentation specifically.
`motion` became its own top-level category instead (poses are action, not appearance — genuinely
non-racial), and `hair` moved under `races/human/cosmetics/`.

**Different complete outfits can need different slot sets** — Bone Armor uses
Wearing/Arms/Jewelry/Back/Legs&feet/Holding; the archived Raven outfit instead has Drapes and
Belt&kit (no Holding at all). That's expected, not a bug: a new outfit shape may need its own
template variant rather than forcing every outfit through one fixed slot list. The **scene** stage
has four template variants for this reason: `scene-human.txt` (preserve everything from a prior
stage, only add atmosphere — the **two-stage** path: feed in an already-rendered clothing/armor
image), `scene-with-outfit-human.txt` (describe the outfit directly — the **single-stage**,
A-pose-in/full-scene-out path), `scene-with-companion-human.txt` (adds `{{COMPANION}}` for a bonded
pet/dragon), and `scene-minimal-human.txt` (wearing/pose/effects/background only — no
jewelry/weapon/companion slots, for lower-priority content like the Angel Primes test-bed where
footwear is baked into the one bundled `wearing` piece instead of decomposed). A **companion** is
its own piece, deliberately separate from `background` — the dragon's identity/placement is one
reusable concern, the environment it flies through is another.

**Motion component tokens join into ONE token per slot, not one-per-field** — a rich motion
component (editorial/breeze/body/head/pose) referenced for a scene's `pose` slot becomes a single
combined `{{POSE}}` line, not several new template tokens. This keeps the template token surface
flat regardless of how rich the underlying piece is — the fix for "pose" previously being a
hand-typed literal string on several scene cards instead of a real, reusable `motion/standing/...`
component (now corrected).

**Motion is "faceless" — gaze and expression are their own concern, with a default** — a motion
component only owns the *physical* side of a pose (body/head/limb detail); it carries a
`defaultGaze` and `defaultExpression` purely for convenience, so referencing a motion normally
"just works" without having to also pick a gaze/expression every time. Both are folded into the
joined `{{POSE}}` text automatically. A scene can override either independently — declare its own
`components.gaze` and/or `components.expression` (pointing at a `motion/expressions/*.json` piece,
or a brand-new one, or just a literal inline string) — and that value is substituted **in place**
of the motion's own default, with no risk of both appearing and contradicting each other (e.g.
"alluring... fierce"). See "Field-name vocabulary" below for exactly how this is enforced.

**A motion's own default may itself point at a shared `motion/gaze/` or `motion/expressions/`
piece, instead of inlining literal text** — when an audit found the same `defaultGaze`/
`defaultExpression` string duplicated verbatim across several unrelated motions (e.g. "eyes to
camera." on both `over-the-shoulder-glance` and `three-quarter-glamour`), the duplicated value was
extracted into one shared piece and every motion that used it now references that piece by path
instead of repeating the text — single source of truth, no drift if it's ever tweaked later. A
motion whose gaze/expression is genuinely one-off keeps it as inline literal text; only genuinely
*repeated* text gets extracted. This is the same path-or-literal duality `components.<slot>`
already has, just on the read side (`_resolve_field_value()` in `gen_prompt.py`) instead of the
override side (`_is_literal_ref()`).

**Known gap: most of the motion/wardrobe library has female pronouns baked in** ("her"/"she"),
since it was authored for the Drakn sisters first. Fixed so far: `wardrobe/effects/soft-ambient-glow.json`,
`backgrounds/fantasy/dungeons/ossuary-violet-sky.json`, `backgrounds/fantasy/cityscape/citadel-skyline-dusk.json`,
`backgrounds/fantasy/elemental/rising-flames.json` — each caught only when a male hero's card actually
reused the piece and surfaced the mismatch in generated output. The rest of `motion/` (poses
themselves, not just backgrounds) has not been swept — pick pronoun-neutral pieces, or write a
fresh literal, when building a male hero's scene until a proper cleanup pass happens.

**Archetype-grouped defaults for the male roster** — rather than inventing 10 unique armor/weapon
sets, the 10 `drakn-bound` heroes share 3 default wardrobe groups by class archetype: **Tank**
(`wardrobe/armor/plate/plate-tank.json` + `wardrobe/weapons/swords/broadsword-and-shield.json` — Draknare,
Lyran, Hauk), **Striker** (`leather/leather-striker.json` + `swords/greatsword.json` — Ignis, Torvald,
Dorian, Zephyr), **Rogue** (`leather/leather-rogue.json` + `daggers/paired-daggers.json` — Nizaras,
Malakor; Corin uses the same armor with `polearms/trident.json` instead, fitting his Beast Lord/
Water theme). All embed `{{PRIMARY}}`/`{{ACCENT_SOFT}}` so each hero renders in his own palette.
A new `scene-combat-human.txt` template variant exists alongside the 4 caster-oriented scene
templates — it drops the hardcoded "Eyes glowing {{ACCENT_SOFT}}, luminous, mid-cast" line (and
the bust-related negative-prompt terms), which doesn't fit a non-caster martial hero standing in
a signature scene. This first pass is deliberately bare-bones (one armor set, one signature scene
each) — the Iridescent/Raven-style per-hero decomposition the Drakn sisters have can follow later,
per-hero, as each one gets real design attention.

**Signature scenes: gaze toward camera, and an "effects" layer for every one** — two rules
enforced across every signature scene after an audit found violations: (1) the pose's `body`/`gaze`
should keep the face substantially toward camera — a true side-profile motion hides too much of
the face for a card meant to represent that hero (this is why Draknora's Dragon Flight switched
from `motion/standing/side-profile-elegant.json` to `three-quarter-glamour.json` — a 3/4 turn
still reads as dynamic but keeps most of the face visible; pure off-camera/profile motions are
fine for glamour-library variety, just not for a hero's signature card). (2) every signature scene
should have *something* in its `effects` slot beyond a flat "no additional magical effects" —
swirling leaves, drifting ice crystals, dust, mist, static, whatever fits the hero's element —
literal text is fine, it doesn't need to be a shared reusable piece unless the same effect is
likely to recur elsewhere. A hero-specific detail tied to a *specific worn item* (e.g. Draknora's
"flames around her glowing sandals") belongs in the scene's `effects` slot, not on the footwear
piece itself — the footwear (`wardrobe/footwear/heels/glowing-strap-heels.json`) is shared across many
heroes in their own palette, so baking in a permanent flame effect there would leak onto every
other hero wearing it; the effect is a property of *this scene*, not of the shoes.

`prompts/` mirrors the **`_sets/`** contents exactly — one level flatter than `data/art/`, since
everything under `prompts/` is already generated art output (no sibling non-art content to
disambiguate from, so no `_sets/` wrapper needed there):

```text
prompts/
├── _archive/                        Historical reference only (old hand-crafted system).
├── drakn-sisters/
│   └── <Hero>/<stage>/<family>/*.txt
└── angel-primes/
    └── <Hero>/<stage>/<family>/*.txt
```

`data/art/_sets/<group>/...` → `prompts/<group>/<Hero>/<stage>/<family>/*.txt`.
Definitions never get mirrored into `prompts/` — they aren't "generated," they're read.

---

## Glossary

| Term | Meaning | Example |
| --- | --- | --- |
| **category** | What *kind* of subject | `heroes`, `races`, `wardrobe`, `motion`, `dragons`, `pets`, `buildings`, `backgrounds` |
| **group** | A themed hero roster, same name used on both layers | `heroes/drakn-sisters/` (definitions) ↔ `_sets/drakn-sisters/` (assembly) |
| **specificity tier** | How widely a piece can be reused | `wardrobe` (any outfit/hero/race) → `races/<race>` (a race) → `heroes/<group>/<hero-slug>` (one hero's signature piece) |
| **component** | A single complete reusable trait, referenced by a card's `component` field | a hairstyle, a motion pose |
| **slot / piece** | One named part of a composed outfit, referenced by a card's `components` dict | `wearing`, `jewelry`, `holding` |
| **stage** | Which generation step | `pose`, `head`, `hair`, `motion`, `armor`, `clothing` |
| **family** | A sub-grouping of a component or card, for navigability | `down`, `walking`, `romantic` |

---

## How a card actually gets generated

A `_sets/` card JSON has pointers: `heroArt` (a definitions-layer hero file), a stage `template`,
and **either** `component` (one complete reusable trait — hair, motion) **or** `components` (a
dict of named slots, each pointing at its own small piece file — armor, clothing). A piece file's
single content field (by convention `description`) becomes the token named after its *slot*
(`components.jewelry` → `{{JEWELRY}}`), not the piece's own field name — that's what lets the same
piece fill the same slot in many different outfits. `tools/generators/gen_prompt.py` resolves
everything, fills `{{TOKENS}}`, and writes the result to `output` under `prompts/`. The generator
itself has **zero hardcoded paths** — every path is a string field on the card JSON, so
moving/renaming folders only ever means updating path strings, never generator logic.

**`heroArt` doesn't have to be a humanoid hero** — if the loaded identity is a dragon (no `art`
key, e.g. `dragons/elder-dragons/pyraxis.json`), `generate()` branches to
`tokens_for_dragon()` instead of `tokens_for()`, producing a much smaller token set (`{{DRAGON}}`,
`{{DESCRIPTION}}`, `{{ELEMENT}}`; name and element come from the dragon's card via `cardId`) for the
dragon archetype's own text-to-image templates
(`_templates/dragons/pose-dragon.txt`, `head-dragon.txt` — no incoming reference image, no
"maintain fidelity to the reference image" line, since there's no existing dragon photo to edit
from; the whole image is generated from the identity file's own `description`).

Example — swapping a weapon without touching the armor at all:

```jsonc
// data/art/_sets/drakn-sisters/drakness/armor/bone-scythe.json
"components": {
  "wearing": "data/art/heroes/drakn-sisters/drakness/armor/bone-wearing.json",
  "arms": "data/art/heroes/drakn-sisters/drakness/armor/bone-arms.json",
  "jewelry": "data/art/wardrobe/jewelry/necklaces/bone-skull-pendant.json",
  "back": "data/art/wardrobe/capes/short-capes/simple-black-leather.json",
  "legs_feet": "data/art/heroes/drakn-sisters/drakness/armor/bone-legs-feet.json",
  "holding": "data/art/heroes/drakn-sisters/drakness/weapons/reaper-scythe.json"
}
```

`bone-dagger.json` is identical except the last line points at `weapons/ornate-dagger.json` —
verified byte-identical generated output except the one `Holding:` line.

**CLI filtering** — no-args generates everything under `_sets/`; composable flags narrow it down:

```bash
python tools/generators/gen_prompt.py                                     # everything
python tools/generators/gen_prompt.py <card.json>                         # one exact file
python tools/generators/gen_prompt.py --group drakn-sisters               # one group
python tools/generators/gen_prompt.py --group drakn-sisters --slug drakness
python tools/generators/gen_prompt.py --group drakn-sisters --slug drakness --stage hair
python tools/generators/gen_prompt.py --group drakn-sisters --slug drakness --stage hair --family down
```

**Cleanup is a safe two-phase plan/apply, like `terraform plan`/`apply`** — `--cleanup` alone only
*previews* `.txt` files that no longer match any current card's output (e.g. leftovers from a
renamed `artId`/`output`, exactly what happened when Drakness/Draknora/Drakneta's bespoke scenes
were renamed to the canonical `Signature` naming); nothing is deleted until you also pass `--yes`.
Scoped to the **exact directories** that received an output this run — not the whole group — so a
narrow `--slug`/`--stage` run can never flag a sibling hero's untouched files as orphans just
because they weren't part of that run (an earlier draft of this scoped by group only, which a
quick test caught doing exactly that — fixed before it shipped). Never touches `prompts/_archive/`.

```bash
python tools/generators/gen_prompt.py --cleanup                            # preview only, safe
python tools/generators/gen_prompt.py --cleanup --yes                      # actually delete
```

---

## Future direction: organizing templates by rarity/card-type (documented, not built yet)

Noticed while building signature scenes: a Transcendent/Mythic **signature** card (companion,
elemental effects, hero-specific weapon) is a fundamentally richer *kind* of card than a Common/
Uncommon **unit** card will be — they probably shouldn't share a template file long-term, the way
`scene-combat-human.txt` already diverged from the caster-oriented scene templates for a different
*reason* (non-caster vs caster). As the roster grows past heroes into units/buildings/tactics,
template naming/organization will likely need a second axis beyond "archetype" (`heroes/`,
`dragons/`) — something like **card tier/type**, so it's clear at a glance which templates are
rich "signature/hero" cards (full effects, companions, backgrounds) vs. simpler mass-produced
card types, vs. the existing `pose-*`/`head-*`/`armor-*` **studio-background test** stages (cream
backdrop, no scene) that exist purely to validate a look before it reaches a real card. Concretely,
once that content exists, expect to need: **building** card templates (architecture, not a figure),
**unit/troop** templates (likely simpler than hero signature scenes — fewer unique effects), and
eventual **foil/"shiny"/alternate-art** variants (extra shimmer/glow effects layered on an existing
signature scene — possibly the *same* template with an added effects field, possibly its own
variant; genuinely undecided until that content exists to design against). Also worth doing once
there's enough signature-scene content to look for patterns: "mining" the signature `.json` files
for genuinely-repeated phrasing/effects and pushing those back into shared `wardrobe/`/`backgrounds/`
pieces, the same way `motion/gaze/`, `motion/expressions/`, and the archetype-grouped male wardrobe
defaults were extracted this session — only once duplication is *verified*, not speculatively.
**Deliberately deferred** — there isn't yet enough built in each of these areas to design the right
split with confidence; forcing a taxonomy now risks guessing wrong and reshuffling later for nothing.

---

## Tag slots: templates are thin shells, pieces carry the text

The direction of travel: a template holds only what is truly specific to a stage; everything reusable is a
`{{SLOT}}` filled by a proven piece. A card overrides any slot with `components.<slot>` (a piece path, a literal, or
`+literal` to extend). A slot a card leaves empty falls back to `SLOT_DEFAULTS` in `gen_prompt.py` (by stage, and by
sex where it differs), so existing cards need no change.

| Slot / token | What it is | Pieces | Default |
| --- | --- | --- | --- |
| `background` | Where the subject stands; for cream stages this carries the studio lighting too | `backgrounds/studio/*`, `fantasy/*`, `modern/*` | studio `cream-even` for every cream stage; **required** on scenes |
| `realm` | World rule + bans (`{{REALM}}`, `{{REALM_NEG}}`) | `realms/*.json` | `fantasy` on scenes |
| `view` | Camera/subject orientation | `shots/views/body/*`, `shots/views/head/*` | front |
| `framing` | How tight a head shot is | `shots/framing/*` | `bust-up` |
| `expression` | Facial read | `motion/expressions/*` | per stage and sex (above) |
| `underlayer` | What the A-pose wears | `wardrobe/swimwear/*`, hero `wearing/` pieces | triangle bikini / swim brief |
| `eye_effect` | Scene eye glow | `wardrobe/effects/eyes/*` | `partial-glow` |

Pieces may carry an optional `tags` list (e.g. `studio`, `profile`, `swimwear`) purely for finding and ideation;
tags are never rendered. A piece's `negatives` list becomes a `{{<SLOT>_NEG}}` token (the realm uses this).

**Shots vs scenes.** A *shot* is a cream studio render (pose, head, hair, motion, armor, clothing) for clearly
seeing the subject, an outfit or an armor piece; it may still include motion (a catwalk, a battle stance). A *scene*
adds a realm, background and effects. Canon scenes are always the `fantasy` realm; the validator rejects a scene
whose background folder doesn't match its realm, so a modern location can only appear if a card explicitly sets
`components.realm` to `realms/modern.json` (the Angel Primes' `scene/modern/` cards, for fun).

**Template folders were deliberately not split** (e.g. `shots/` vs `scenes/`): that would mean rewriting ~300 card
paths for no behaviour change. Split when buildings/units/armor-only renders add a second axis of templates.

## The reference-shot library (built from the A-pose)

Every hero's X Pose is the baseline; a library of studio references is derived from it so a specific close-up or
angle can later be fed in as an image reference instead of re-describing the face with JSON. Generate a hero's whole
library with one command, then `gen_prompt.py` to produce prompts:

```bash
python tools/generators/scaffold_shot_library.py --group angel-primes --slug angelica-prime --hero Angelica \
    --underlayer data/art/heroes/angel-primes/angelica-prime/wearing/angelic-pastel-bikini.json
python tools/generators/gen_prompt.py --group angel-primes --slug angelica-prime
```

Per hero: 6 body views (3/4 L/R, profile L/R, back, back-glance), 8 head views (3/4 L/R, profile L/R, looking down,
chin up, over shoulder, tilt), 2 extra head framings (face close-up, chest and hair) and 4 head expressions.
The Angel Primes are the test bed for all of this (colourful underlayers make direction changes visible); sisters
and bound heroes only need their signature armor, motion, hair and poses, plus the library where it is useful.

## Eyes, makeup, expression and hair: what each stage says

Every cream-backdrop (studio) stage uses the **same** studio eyes and makeup, so a full-body shot and the close-up agree.
Glow is only ever added in `scene` stages.

| Concern | Token | Used in | Notes |
| --- | --- | --- | --- |
| Studio eyes | `{{EYE}}` | pose, head, hair, motion, armor, clothing | Iris colour + striations + limbal ring, always "natural, not glowing"; `glowing eyes` is in those negatives. |
| Studio makeup/grooming | `{{FACE_STYLE}}` | pose, head, hair, motion, armor, clothing | One line in `gen_prompt.py` (`FACE_STYLE`): subtle eyeshadow in the hero's accent colour, light blush; "present, never heavy". Males get a grooming line. |
| Expression | `{{EXPRESSION}}` | pose, head | Defaults in `SLOT_DEFAULTS` (see below): pose = per-sex studio glamour/confident; head = `studio-glamour-smile` (lips, cheeks, dimples). Override on a card with `components.expression` (a piece or literal). The pose also resets the source photo's head tilt and body angle. |
| Hairstyle | `{{HAIRSTYLE}}`, `{{HAIRSTYLE_NEG}}` | pose | From the hero's `hairStyleComponent`. `hair/down/center-part-natural.json` takes the hair down, centre-parted, keeping the source's natural texture; its `a_pose_negatives` (ponytail, bun, updo, ...) go into the negative prompt. |
| Scene eye glow | `{{EYE_EFFECT}}` | scene templates | Chosen with `components.eye_effect`; default `partial-glow`. |
| (Soft iris-only eyes) | `{{EYE_SOFT}}` | inside the eye-effect pieces | Not used by the studio stages. |

Scene glow pieces live in `data/art/wardrobe/effects/eyes/`: `natural` (no glow), `iris-kindling` (glow just starting at the
iris rim), `partial-glow` (**default**, mid-cast, iris detail kept), `full-glow` (power peak, overrides the eye colour and
dominates the face). Override per scene card: `"eye_effect": "data/art/wardrobe/effects/eyes/full-glow.json"`.
`scene-combat-human.txt` has no eye line (martial heroes). These alternatives exist for ideation: try them, then settle
which suits which art.

## Signature items match the character

A signature weapon should read as the hero's class at a glance (a Shaman's totem staff with hanging cloth and a shaman
symbol, a Druid's living-wood staff, a Cleric's sunburst staff), never a generic "skull staff". Each sister's staff lives in
`heroes/drakn-sisters/<slug>/weapons/`; `wardrobe/weapons/ornate-staff.json` (skull jewel) is only for Necromancer scenes.

---

## Field-name vocabulary (master inventory) — why field names must stay consistent

`data/art/_schema/field-vocabulary.json` is the **enforced**, authoritative registry of every
shared field name a piece can use, whether it's `overridable`, and which piece kinds own it. The
generator validates every field it loads from a `components` piece against this file — an unknown
field name is a hard error at generation time ("add it to field-vocabulary.json"), not a silent
typo. **When adding a new piece kind, reuse an existing registry name if the concept matches;
don't invent a synonym** (e.g. use `expression`, not `mood` or `face`, for facial expression text)
— if it's genuinely new, add it to the registry first.

| Field name | Overridable | Meaning | Owner |
| --- | --- | --- | --- |
| `description` | no | Catch-all content field for a simple, single-purpose piece | `wardrobe/*`, `backgrounds/*`, `heroes/*/armor,clothing,weapons,effects` |
| `editorial` | no | Overall shot framing/style line | `motion/*` |
| `breeze` | no | Ambient wind/movement flavor | `motion/*` |
| `body` | no | Torso/weight stance | `motion/*` |
| `head` | no | Head angle/tilt | `motion/*` |
| `pose` | no | Limb/hand positioning detail (also the *slot* name for the whole motion bundle — deliberately non-overridable so that name collision can never hijack it) | `motion/*` |
| `gaze` | **yes** | Where the eyes look | `motion/gaze/*` standalone pieces, or a literal inline string |
| `expression` | **yes** | Facial/emotional read | `motion/expressions/*` standalone pieces, or a literal inline string |
| `defaultGaze` | no (aliases to `gaze`) | The gaze a motion implies by default — literal text, or a path to a `motion/gaze/*.json` piece if the same default repeats across motions | `motion/*` |
| `defaultExpression` | no (aliases to `expression`) | The expression a motion implies by default — literal text, or a path to a `motion/expressions/*.json` piece if the same default repeats across motions | `motion/*` |
| `extras` | no | Freeform additive list — general tags that don't claim a reserved field name | `motion/*` |
| `mood` | no | A short tonal tag, distinct from `description` (currently excluded from generated output) | some multi-field `backgrounds/*` pieces |

**A `components.<slot>` value can be a literal inline string instead of a file path** — useful for
a quick final scene-level tweak, or for authoring an entire scene from scratch without any
reusable pieces at all (see the worked example below and `_sets/drakn-sisters/drakneta/scene/
drakneta-castle-spellcast.json`).

**A literal value can EXTEND the default instead of fully replacing it** — prefix it with `+`, e.g.
`"expression": "+a faint, knowing smile, teeth just barely visible."`. The fragment is appended
after whatever the default would otherwise have been (the motion's own `defaultExpression`/
`defaultGaze`, or another slot's value for that canonical field) instead of replacing it outright
— a plain literal or a piece reference (no `+`) is still a full replace, as before. This is for
tuning a scene from a proven, already-"validated" default (the same reuse philosophy as hair and
motion) by adding just the one small thing that's different this time, instead of re-authoring
the whole expression/gaze from scratch for a minor variation. See `_sets/drakn-sisters/drakness/
scene/drakness-elegant-casting.json` — `commanding-cast.json`'s own default expression ("composed,
commanding, lips softly together.") stays, with "a faint, knowing smile, teeth just barely
visible." appended after it.

**Worked example — overriding an expression** (`_sets/drakn-sisters/draknora/scene/draknora-dragon-flight.json`):

```jsonc
"components": {
  "pose": "data/art/motion/standing/side-profile-elegant.json",       // defaultExpression: "composed, serene; ..."
  "expression": "data/art/motion/expressions/fierce-focused.json"     // expression: "fierce, intensely focused; ..."
}
```

Because the `expression` slot's own piece has a field literally named `expression` (a registry
`overridable` field), that value is registered as an override. When the `pose` slot's motion piece
is joined, its `defaultExpression` field — recognized via its canonical alias `expression` — is
replaced by the override: the generated `{{POSE}}` token reads "...off-camera into the distance.
**fierce, intensely focused; jaw set, a slight knowing curl; eyes locked on the threat.** one foot
forward..." instead of the motion's default "composed, serene...". No template change was needed.
Standalone expression pieces live in `motion/expressions/` (`composed-serene`, `alluring-confident`,
`composed-commanding`, `glamorous-confident` — one extracted from each repeated motion default —
plus `fierce-focused` as a genuinely new, contrasting option). Standalone gaze pieces live in
`motion/gaze/` (`focused-on-camera`, `eyes-to-camera`, `seductive-unpredictable` — each one
extracted because the exact same `defaultGaze` text was duplicated verbatim across 2-3 motions).
Gaze/expression text unique to one motion stays inline — extraction only happens for genuine,
verified duplication, not speculatively.

---

## Relationship to `data/cards/sovereign-dawn/` — the card ↔ art link

A card is **defined first in the codex** (`data/cards/sovereign-dawn/<category>/*.json`, validated by
`data/schemas/codex-schema.json`); the art is then built *for* that card. The two are separate pipelines with
separate schemas and **never both define the same attribute**. They meet at one link, keyed on `cardId`:

```text
data/cards/.../hero-drakness-thorne.json            data/art/heroes/drakn-sisters/drakness-thorne.json
  cardId: HERO_DRAKNESS_THORNE        <──────────     cardId: HERO_DRAKNESS_THORNE
  name, element, sex, race, class,    ──────────>     art: { palette, physique }   (look only)
  rarity, stats, abilities, lore                      (name/element/sex/race/class are PULLED from the card)
  art: { artIdentity: "data/art/heroes/drakn-sisters/drakness-thorne.json",
         portraitAsset / fullArtAsset / shinyPortrait }   <- references to rendered output (see C1 plan)
```

- **The card owns** identity and mechanics: name, element, sex, race, class, rarity, stats, abilities, lore, companion.
- **The art identity owns** look: palette, physique, hairstyle. `gen_prompt.py` resolves `cardId` through
  `load_identity()` and pulls `name`/`element`/`sex`/`race`/`class` from the card, so they exist in exactly one place.
  A dangling `cardId` is a hard generation error.
- **An attribute both sides need lives on the card** and the art side reads it through the link (e.g. the card's `sex`
  decides female vs male physique; the validator checks the identity's physique shape agrees).
- **Dragons** link the same way (`cardId: UNIT_PYRAXIS`) and take `name`/`element` from their card; only the visual
  `description` lives in `data/art/dragons/`.
- **Test-bed heroes** (`angel-primes`) have no card by design: `testBed: true` plus their own `name`.
- A specific `_sets/` card can still deviate for one render via `overrides.palette` / `overrides.physique`.

### Adding a new card (the workflow)

1. Define the card in the codex. Validate: `python tools/validators/validate_data.py`.
2. Create its art identity (`data/art/heroes|dragons/…`) with `cardId`, then set the card's `art.artIdentity` to that path
   (the link must point **both** ways or the validator fails).
3. Add assembly cards under `data/art/_sets/<group>/<slug>/…` (pose, head, armor, signature scene) pointing `heroArt` at
   the identity.
4. `python tools/generators/gen_prompt.py` → prompts; render in ComfyUI; record outputs in the card's `*Asset` fields.

### What the validator enforces (`tools/validators/validate_data.py`, a pre-commit/CI gate)

Schemas, per file class: gameplay cards → `codex-schema.json`; and in `data/art/_schema/`: `hero-identity`,
`dragon-identity`, `art-piece` (required fields vary by `kind`), `art-card` (the `_sets/` recipes). Plus the rules JSON
Schema can't express: the card↔art link is bidirectional; every path a card references exists (the generator treats a
non-existent `.json` path as *literal prompt text*, so a typo would otherwise silently leak a file path into a prompt);
generated `output` paths are unique; `cardId`/`collectionNumber` are unique. `test_validate_data.py` mutation-tests all
of this so the gate cannot silently go dead. Areas with no fitting schema yet are listed as PENDING in its coverage
report. Current status and backlog: [`docs/STATUS.md`](../../docs/STATUS.md).
