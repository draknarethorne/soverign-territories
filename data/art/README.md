# `data/art/` — Structure Reference

**Status:** Living document · **Last updated:** 2026-10-02

This is the authoritative explanation of how `data/art/` is organized. Read this before adding any
new hero, component, or card-production folder — the goal is that we never have to reshuffle
directories again as heroes, dragons, pets, buildings, armor, weapons, and new card productions
get added.

Referenced from [`docs/art/comfyui-art-pipeline.md`](../../docs/art/comfyui-art-pipeline.md) and
[`docs/art/prompt-pattern.md`](../../docs/art/prompt-pattern.md).

---

## The two layers (this is the core idea — everything else is detail)

1. **Definitions** — reusable facts: who a hero *is* (palette/physique), and reusable style
   components (a hairstyle, a motion/pose, eventually armor/clothing/weapons). These files don't
   generate anything by themselves. They're set-agnostic — any group can point at them.
2. **Assembly** (`_sets/<group>/`) — the testing/working folder where a group's hero definition +
   an optional component + a stage template get pulled together into an actual generated prompt.
   Each `_sets/` folder is named **identically to the definitions-layer group it mirrors**
   (`_sets/drakn-sisters/` ↔ `heroes/drakn-sisters/`) — no separate "-set" word needed once it's
   already under `_sets/`. This is deliberately **not** a 1:1 mirror of a game card series — a real
   series (like Sovereign Dawn) can pull from several groups (drakn-sisters today; drakn-bound and
   elder-dragons later), and that series↔group mapping lives on the `data/cards/` side via asset-ID
   references, not via art-side directory nesting. `angel-primes` doesn't correspond to any real
   card series at all — it's a calibration/testing sandbox for proving prompt changes against
   arbitrary reference photos before touching real heroes.

Only the **assembly** layer's `tools/generators/gen_prompt.py` output is ever regenerated/committed
as a finished prompt. Everything in the **definitions** layer is only ever *referenced*.

---

## Directory map

```text
data/art/
├── _templates/                     Stage templates — static scaffolding, {{TOKEN}} placeholders.
│   └── heroes/                     Archetype: humanoid. (pose-female-human.txt, pose-male-human.txt,
│                                   head-human.txt, hair-human.txt, motion-human.txt)
│   └── dragons/                    (future — a dragon archetype's own templates)
│
├── _sets/                          ASSEMBLY: one folder per GROUP, same name as its definitions-
│   │                               layer twin below — the recipe .json files that actually
│   │                               generate prompts. Testing/working folders; which real card
│   │                               series (if any) consumes a group's output is tracked on the
│   │                               data/cards/ side, not here.
│   ├── drakn-sisters/
│   │   └── <slug>/<stage>/<family>/*.json
│   ├── angel-primes/
│   │   └── <slug>/<stage>/<family>/*.json
│   └── drakn-bound/                (future, once the 10 male heroes get art-ified)
│
├── heroes/                         CATEGORY: humanoid hero definitions + reusable components.
│   ├── components/                Reusable STYLE traits, usable by any hero in any group.
│   │   ├── hair/<family>/*.json
│   │   ├── motion/<family>/*.json
│   │   ├── armor/<family>/*.json      (future)
│   │   ├── clothing/<family>/*.json   (future)
│   │   └── weapons/<family>/*.json    (future)
│   ├── drakn-sisters/              GROUP: the 10 Thorne sisters (an actual Sovereign Dawn roster).
│   │   └── <slug>-thorne.json
│   ├── drakn-bound/                GROUP: the 10 male heroes bound to the sisters in the story
│   │                               (Draknare Thorne, Hauk Hammerfell, ...) — reserved, not yet
│   │                               populated.
│   └── angel-primes/               GROUP: Angelo Prime / Angelica Prime — calibration test-bed
│       └── <slug>.json             heroes, not part of any real card series.
│
├── dragons/                        CATEGORY: future. Same shape — components/ + group folders
│                                   (e.g. elder-dragons/) + a matching _sets/elder-dragons/.
├── pets/                           CATEGORY: future.
├── buildings/                      CATEGORY: future.
└── backgrounds/                    CATEGORY: future (forests/, castles/, dungeons/, ...) — reusable
                                    scene components, usable across every other category, blended
                                    into a hero's final card prompt once that assembly step exists.
```

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
| **category** | What *kind* of subject | `heroes`, `dragons`, `pets`, `buildings`, `backgrounds` |
| **group** | A themed roster, same name used on both layers | `heroes/drakn-sisters/` (definitions) ↔ `_sets/drakn-sisters/` (assembly) |
| **component** | A reusable style trait, referenced by a `_sets/` card | a hairstyle, a motion pose |
| **stage** | Which generation step | `pose`, `head`, `hair`, `motion` |
| **family** | A sub-grouping of a component or card, for navigability | `down`, `walking`, `romantic` |

---

## How a card actually gets generated

A `_sets/` card JSON (e.g. `data/art/_sets/drakn-sisters/drakness/hair/down/beach-waves.json`)
has three pointers: `heroArt` (a definitions-layer hero file), `component` (optional, a
definitions-layer style file), and `template` (a stage template). `tools/generators/gen_prompt.py`
resolves all three, fills `{{TOKENS}}`, and writes the result to `output` under `prompts/`. The
generator itself has **zero hardcoded paths** — every path is a string field on the card JSON, so
moving/renaming folders only ever means updating path strings, never generator logic.

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
