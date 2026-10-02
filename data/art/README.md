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
│                                   clothing-human.txt)
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
│   └── drakn-bound/                ⬜ future, once the 10 male heroes get art-ified
│
├── heroes/                         CATEGORY: humanoid hero definitions, grouped by roster.
│   ├── drakn-sisters/              ✅ GROUP: the 10 Thorne sisters (an actual Sovereign Dawn roster).
│   │   ├── <slug>-thorne.json      identity (palette/physique) — unchanged for all 10
│   │   ├── drakness/               ✅ hero-SIGNATURE pieces: armor/, clothing/, weapons/, effects/
│   │   └── draknora/               ✅ hero-SIGNATURE pieces: armor/, weapons/, effects/, and her
│   │                               first companion/ piece (pyraxis-flight.json)
│   ├── drakn-bound/                ⬜ GROUP: the 10 male heroes bound to the sisters in the story
│   │                               (Draknare Thorne, Hauk Hammerfell, ...) — reserved, not yet
│   │                               populated.
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
│   ├── jewelry/necklaces/*.json    (2: bone-skull-pendant, ornate-gem-pendant)
│   ├── jewelry/sets/*.json         (1: silver-gem-set, token-parameterized)
│   ├── capes/*.json                (1: simple-black-leather)
│   ├── bracelets/*.json            (1: simple-silver)
│   ├── footwear/*.json             (1: glowing-strap-heels, token-parameterized)
│   └── accessories/*.json          (1: midnight-violet-satchel — Raven's bag, not yet wired;
│                                   Raven needs its own template shape, see below)
│
├── dragons/                        🔶 CATEGORY: one real entry seeded — elder-dragons/pyraxis.json
│   └── elder-dragons/              (Fire-aligned, Draknora's companion per the codex's Element
│                                   Alignment table). Not yet wired as a hero's bonded pet — only
│                                   referenced today via a hero's own companion/ placement piece
│                                   (see heroes/ below). A matching _sets/elder-dragons/ is future.
├── pets/                           ⬜ CATEGORY: future.
├── buildings/                      ⬜ CATEGORY: future.
└── backgrounds/                    🔶 CATEGORY: skeletal examples seeded (forests/, dungeons/,
                                    elemental/, cityscape/) — reusable scene components, usable
                                    across every other category, blended into a hero's final card
                                    prompt once that assembly step exists. Not yet wired into the
                                    generator except via the scene stage (see below).
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
component (editorial/breeze/body/head/gaze/expression/pose) referenced for a scene's `pose` slot
becomes a single combined `{{POSE}}` line, not seven new template tokens. This keeps the template
token surface flat regardless of how rich the underlying piece is — the fix for "pose" previously
being a hand-typed literal string on several scene cards instead of a real, reusable
`motion/standing/...` component (now corrected).

**Known gap: most of the motion/wardrobe library has female pronouns baked in** ("her"/"she"),
since it was authored for the Drakn sisters first. `wardrobe/effects/soft-ambient-glow.json` was
caught and fixed (needed for Angelo Prime's scene); the rest of `motion/` has not been swept yet —
pick pronoun-neutral pieces when building a male hero's scene until a proper cleanup pass happens.

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
