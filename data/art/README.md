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

## Directory map

```text
data/art/
├── _templates/                     Stage templates — static scaffolding, {{TOKEN}} placeholders.
│   └── heroes/                     Archetype: humanoid. (pose-female-human.txt, pose-male-human.txt,
│                                   head-human.txt, hair-human.txt, motion-human.txt, armor-human.txt,
│                                   clothing-human.txt, scene-human.txt, scene-with-outfit-human.txt,
│                                   scene-with-companion-human.txt, scene-minimal-human.txt,
│                                   scene-combat-human.txt — no casting-eyes-glow line, for
│                                   non-caster martial heroes)
│   └── dragons/                    (future — a dragon archetype's own templates)
│
├── _sets/                          ASSEMBLY: one folder per GROUP, same name as its definitions-
│   │                               layer twin below — the recipe .json files that actually
│   │                               generate prompts. Testing/working folders; which real card
│   │                               series (if any) consumes a group's output is tracked on the
│   │                               data/cards/ side, not here.
│   ├── drakn-sisters/              ✅ 94 cards (10 heroes × pose/head, 44 hair + 25 motion + 2
│   │   └── <slug>/<stage>/<family>/*.json    armor + 1 clothing for Drakness)
│   ├── angel-primes/                ✅ 4 cards (Angelo + Angelica × pose/head)
│   │   └── <slug>/<stage>/<family>/*.json
│   └── drakn-bound/                ✅ 40 cards (10 male heroes × pose/head/armor/scene) — first-pass
│       └── <slug>/<stage>/*.json   minimal scaffold, 3 archetype-grouped default wardrobe sets
│
├── heroes/                         CATEGORY: humanoid hero definitions, grouped by roster.
│   ├── drakn-sisters/              ✅ GROUP: the 10 Thorne sisters (an actual Sovereign Dawn roster).
│   │   ├── <slug>-thorne.json      identity (palette/physique) — unchanged for all 10
│   │   ├── drakness/               ✅ hero-SIGNATURE pieces: armor/ (bone, iridescent, raven),
│   │   │                           clothing/, weapons/, effects/
│   │   └── draknora/               ✅ hero-SIGNATURE pieces: armor/, weapons/, effects/, and her
│   │                               first companion/ piece (pyraxis-flight.json)
│   ├── drakn-bound/                ✅ GROUP: the 10 male heroes bound to the sisters in the story.
│   │   └── <slug>.json             identity (palette/physique, male build/chest/waist/legs schema)
│   │                               — first-pass invented palettes, no archived source material.
│   └── angel-primes/               ✅ GROUP: Angelo Prime / Angelica Prime — calibration test-bed
│       └── <slug>.json             heroes, not part of any real card series.
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
├── wardrobe/                       ✅ CATEGORY: cross-cutting PIECES, reusable across outfits,
│   │                               heroes, and races — jewelry/capes/bracelets/accessories, not
│   │                               bundled into any one complete "look." This is the library a
│   │                               card's components dict pulls interchangeable slot-fillers from.
│   ├── armor/*.json                (iridescent-bikini, plate-tank, leather-striker, leather-rogue
│   │                               — the 3 are archetype-group defaults for male heroes)
│   ├── arms/*.json                 (1: matching-bracelets, token-parameterized)
│   ├── jewelry/necklaces/*.json    (2: bone-skull-pendant, ornate-gem-pendant)
│   ├── jewelry/sets/*.json         (1: silver-gem-set, token-parameterized)
│   ├── capes/*.json                (2: simple-black-leather, sheer-glowing-cloak)
│   ├── bracelets/*.json            (1: simple-silver)
│   ├── footwear/*.json             (2: glowing-strap-heels, combat-boots — both token-parameterized)
│   ├── weapons/*.json              (broadsword-and-shield, greatsword, paired-daggers, trident —
│   │                               archetype/thematic defaults for male heroes)
│   └── accessories/*.json          (1: midnight-violet-satchel — Raven's bag, not yet wired;
│                                   Raven needs its own template shape, see below)
│
├── dragons/                        ✅ CATEGORY: all 10 Elder Dragons seeded (elder-dragons/*.json),
│   └── elder-dragons/              aligned by element to the female Drakn sisters per the codex's
│                                   Element Alignment table. Only Pyraxis is grounded in archived
│                                   content; the other 9 are first-pass invented, colour-grounded
│                                   in their paired hero's own palette. Not yet wired as a hero's
│                                   bonded pet beyond Pyraxis's companion/ placement piece — a
│                                   dragon doesn't have its own pose/scene archetype templates yet
│                                   (dragons aren't humanoid), so these are companion/background
│                                   identities only, not independently renderable subjects.
├── pets/                           ⬜ CATEGORY: future.
├── buildings/                      ⬜ CATEGORY: future.
└── backgrounds/                    ✅ CATEGORY: forests/, dungeons/, elemental/, cityscape/,
                                    evening/, castle/ (6 families, 1 piece each so far) — reusable
                                    scene components, wired into the generator via the scene stage.
                                    Background choice doesn't have to match a hero's element 1:1
                                    (e.g. Draknora/Fire uses a cityscape-dusk background) — it's as
                                    much about scene story as elemental theming.
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
`backgrounds/dungeons/ossuary-violet-sky.json`, `backgrounds/cityscape/city-skyline-dusk.json`,
`backgrounds/elemental/rising-flames.json` — each caught only when a male hero's card actually
reused the piece and surfaced the mismatch in generated output. The rest of `motion/` (poses
themselves, not just backgrounds) has not been swept — pick pronoun-neutral pieces, or write a
fresh literal, when building a male hero's scene until a proper cleanup pass happens.

**Archetype-grouped defaults for the male roster** — rather than inventing 10 unique armor/weapon
sets, the 10 `drakn-bound` heroes share 3 default wardrobe groups by class archetype: **Tank**
(`wardrobe/armor/plate-tank.json` + `wardrobe/weapons/broadsword-and-shield.json` — Draknare,
Lyran, Hauk), **Striker** (`leather-striker.json` + `weapons/greatsword.json` — Ignis, Torvald,
Dorian, Zephyr), **Rogue** (`leather-rogue.json` + `weapons/paired-daggers.json` — Nizaras,
Malakor; Corin uses the same armor with `weapons/trident.json` instead, fitting his Beast Lord/
Water theme). All embed `{{PRIMARY}}`/`{{ACCENT_SOFT}}` so each hero renders in his own palette.
A new `scene-combat-human.txt` template variant exists alongside the 4 caster-oriented scene
templates — it drops the hardcoded "Eyes glowing {{ACCENT_SOFT}}, luminous, mid-cast" line (and
the bust-related negative-prompt terms), which doesn't fit a non-caster martial hero standing in
a signature scene. This first pass is deliberately bare-bones (one armor set, one signature scene
each) — the Iridescent/Raven-style per-hero decomposition the Drakn sisters have can follow later,
per-hero, as each one gets real design attention.

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

Example — swapping a weapon without touching the armor at all:

```jsonc
// data/art/_sets/drakn-sisters/drakness/armor/bone-scythe.json
"components": {
  "wearing": "data/art/heroes/drakn-sisters/drakness/armor/bone-wearing.json",
  "arms": "data/art/heroes/drakn-sisters/drakness/armor/bone-arms.json",
  "jewelry": "data/art/wardrobe/jewelry/necklaces/bone-skull-pendant.json",
  "back": "data/art/wardrobe/capes/simple-black-leather.json",
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

## Relationship to `data/cards/sovereign-dawn/`

`data/cards/sovereign-dawn/<category>/*.json` is the real game-data card (stats/abilities/lore) —
a separate system the generator does **not** read from today (that wiring was ideation-only; work
pivoted to focus on the art pipeline directly). A real card series pulls from one or more
`_sets/<group>/` folders (Sovereign Dawn currently only draws from `drakn-sisters`; `drakn-bound`
and `elder-dragons` join later) — that series↔group mapping is tracked via asset-ID references on
the card JSON (e.g. `combinedArtAsset`), not via art-side directory nesting. Known duplication to
reconcile later: some physical traits are currently duplicated between a hero's game card and its
`data/art/heroes/<group>/` definition. Eventual plan: the art definition becomes the source of
truth for physical traits, the game card references it, and a specific `_sets/` card can still
override an attribute via `overrides.palette` / `overrides.physique` (already supported by the
generator) when a card series needs a deliberate deviation.
