# Sovereign Dawn Roster: Heroes and Elder Dragons (SD-001 to SD-030)

> **What this is:** the readable roster of the first Sovereign Dawn heroes and Elder Dragons, with the decisions behind them. It started as ideation and became this document.
> It is **not the codex itself**: the card data is `data/cards/sovereign-dawn/` (JSON, validated by `data/schemas/codex-schema.json`), and where the two differ the JSON wins.
> The wider rules are in [`docs/game-bible.md`](../../game-bible.md) and the design docs.
>
> **Card series:** `SD-###` is the Sovereign Dawn series (this document). The Angel Primes are a separate series, `AP-###`, in
> [`angel_primes_codex.md`](angel_primes_codex.md) (build rationale in [`angel_primes_physique.md`](angel_primes_physique.md)).
>
> **Element expansion:** this roster moves the game from the original element set to a **10-element** model: **Darkness, Fire, Grass, Ice, Water, Light, Earth, Lightning, Wind,
> Poison** (plus Neutral for element-agnostic cards).

## Roster shape

- **10 female heroes** — the **"Drakn" line** (`7 - Transcendent`), each paired to an Elder
  Dragon of the same element. Each has a Dragon pet companion.
- **10 male heroes** (`6 - Mythic`) — only **Draknare Thorne** carries the Drakn name; the
  rest are standalone signature characters.
- **10 Elder Dragons** (`6 - Mythic`) — aligned by element to the female heroes. They
  surface in **"combined" cards** and appear in the **background of certain female-hero
  series**.

**Art status is not tracked in this document.** Which images exist is shown by `data/art/` and `prompts/` (the validator reports coverage), and which key images have been pulled back into the repo or set as a workspace default is shown by `python tools/workflows/comfy_workflows.py inputs --status` (see [workflows/README.md](../../../workflows/README.md)).

---

## Female Heroes — The Drakn Line

| Card ID | Card Name        | Rarity           | Element   | Archetype           | Class       | Creature Type | Race      | Sex    | Pet Companion |
| ------- | ---------------- | ---------------- | --------- | ------------------- | ----------- | ------------- | --------- | ------ | ------------- |
| SD-001  | Drakness Thorne  | 7 - Transcendent | Darkness  | Summoner / Spawner  | Necromancer | Humanoid      | Dark Elf  | Female | Dragon        |
| SD-002  | Draknora Thorne  | 7 - Transcendent | Fire      | Caster / Magic      | Magician    | Humanoid      | Human     | Female | Dragon        |
| SD-003  | Drakniya Thorne  | 7 - Transcendent | Grass     | Support / Healer    | Druid       | Humanoid      | Wood Elf  | Female | Dragon        |
| SD-004  | Draknira Thorne  | 7 - Transcendent | Ice       | Caster / Magic      | Wizard      | Humanoid      | High Elf  | Female | Dragon        |
| SD-005  | Draknisa Thorne  | 7 - Transcendent | Water     | Control / Disruptor | Enchanter   | Humanoid      | Human     | Female | Dragon        |
| SD-006  | Drakniss Thorne  | 7 - Transcendent | Light     | Support / Healer    | Cleric      | Humanoid      | Human     | Female | Dragon        |
| SD-007  | Draknara Thorne  | 7 - Transcendent | Earth     | Specialist / Hybrid | Shaman      | Humanoid      | Barbarian | Female | Dragon        |
| SD-008  | Drakneta Thorne  | 7 - Transcendent | Lightning | Summoner / Spawner  | Summoner    | Humanoid      | Celestial | Female | Dragon        |
| SD-009  | Draknava Thorne  | 7 - Transcendent | Wind      | Support / Healer    | Bard        | Humanoid      | Wood Elf  | Female | Dragon        |
| SD-010  | Draknoxa Thorne  | 7 - Transcendent | Poison    | Control / Disruptor | Alchemist   | Humanoid      | Dark Elf  | Female | Dragon        |

---

## Male Heroes

| Card ID | Card Name            | Rarity     | Element   | Archetype            | Class         | Creature Type | Race      | Sex  | Pet Companion |
| ------- | -------------------- | ---------- | --------- | -------------------- | ------------- | ------------- | --------- | ---- | ------------- |
| SD-011  | Draknare Thorne      | 6 - Mythic | Darkness  | Defense / Tank       | Shadow Knight | Humanoid      | Human     | Male | Reaper        |
| SD-012  | Ignis Emberstride    | 6 - Mythic | Fire      | Melee / Striker      | Warrior       | Humanoid      | Human     | Male | Elemental     |
| SD-013  | Nizaras Featherstone | 6 - Mythic | Grass     | Specialist / Hybrid  | Rogue         | Humanoid      | Wood Elf  | Male | Treant        |
| SD-014  | Lyran Frostfall      | 6 - Mythic | Ice       | Defense / Tank       | Knight        | Humanoid      | High Elf  | Male | Frost Owl     |
| SD-015  | Corin Tidewalker     | 6 - Mythic | Water     | Specialist / Hybrid  | Beast Lord    | Humanoid      | Human     | Male | Shark         |
| SD-016  | Hauk Hammerfell      | 6 - Mythic | Light     | Defense / Tank       | Paladin       | Humanoid      | Human     | Male | Angel         |
| SD-017  | Torvald Stonebreaker | 6 - Mythic | Earth     | Melee / Striker      | Berserker     | Humanoid      | Barbarian | Male | Dire Bear     |
| SD-018  | Dorian Stormstrike   | 6 - Mythic | Lightning | Melee / Striker      | Monk          | Humanoid      | Celestial | Male | Gryphon       |
| SD-019  | Zephyr Galeheart     | 6 - Mythic | Wind      | Melee / Striker      | Warrior       | Humanoid      | High Elf  | Male | Giant Eagle   |
| SD-020  | Malakor Venomcaller  | 6 - Mythic | Poison    | Assassin / Burst DPS | Assassin      | Humanoid      | Orc       | Male | Basilisk      |

---

## Elder Dragons

| Card ID | Card Name | Rarity     | Element   | Archetype       | Class        | Creature Type | Race | Sex    | Pet Companion |
| ------- | --------- | ---------- | --------- | --------------- | ------------ | ------------- | ---- | ------ | ------------- |
| SD-021  | Umbrath   | 6 - Mythic | Darkness  | Aerial / Flying | Elder Dragon | Dragon        | n/a  | Male   | n/a           |
| SD-022  | Pyraxis   | 6 - Mythic | Fire      | Aerial / Flying | Elder Dragon | Dragon        | n/a  | Male   | n/a           |
| SD-023  | Sylvanya  | 6 - Mythic | Grass     | Aerial / Flying | Elder Dragon | Dragon        | n/a  | Female | n/a           |
| SD-024  | Glaciora  | 6 - Mythic | Ice       | Aerial / Flying | Elder Dragon | Dragon        | n/a  | Female | n/a           |
| SD-025  | Aquaria   | 6 - Mythic | Water     | Aerial / Flying | Elder Dragon | Dragon        | n/a  | Female | n/a           |
| SD-026  | Lumira    | 6 - Mythic | Light     | Aerial / Flying | Elder Dragon | Dragon        | n/a  | Female | n/a           |
| SD-027  | Terrador  | 6 - Mythic | Earth     | Aerial / Flying | Elder Dragon | Dragon        | n/a  | Male   | n/a           |
| SD-028  | Fulgora   | 6 - Mythic | Lightning | Aerial / Flying | Elder Dragon | Dragon        | n/a  | Female | n/a           |
| SD-029  | Zephyros  | 6 - Mythic | Wind      | Aerial / Flying | Elder Dragon | Dragon        | n/a  | Male   | n/a           |
| SD-030  | Venomis   | 6 - Mythic | Poison    | Aerial / Flying | Elder Dragon | Dragon        | n/a  | Female | n/a           |

---

## Element Alignment — Female Hero ↔ Elder Dragon

| Element   | Female Hero (Drakn Line) | Elder Dragon |
| --------- | ------------------------ | ------------ |
| Darkness  | Drakness Thorne          | Umbrath      |
| Fire      | Draknora Thorne          | Pyraxis      |
| Grass     | Drakniya Thorne          | Sylvanya     |
| Ice       | Draknira Thorne          | Glaciora     |
| Water     | Draknisa Thorne          | Aquaria      |
| Light     | Drakniss Thorne          | Lumira       |
| Earth     | Draknara Thorne          | Terrador     |
| Lightning | Drakneta Thorne          | Fulgora      |
| Wind      | Draknava Thorne          | Zephyros     |
| Poison    | Draknoxa Thorne          | Venomis      |

---

## Decisions (confirmed) & follow-ups

**Confirmed on this branch:**

- **10 elements plus Neutral:** Darkness, Fire, Grass, Ice, Water, Light, Earth, Lightning, Wind, Poison
  (plus Neutral for element-agnostic cards). Proposed strength/weakness cycles:
  - **Duality:** Light ⟷ Darkness.
  - **Primal triangle:** Fire / Water / Earth.
  - **Storm quad:** Ice / Lightning / Wind / Poison.
  - *Open:* Grass placement (recommended: fold into a Fire → Grass → Water → Earth four-cycle),
    exact directions, and multipliers. Owned by
    [`design/combat-calculation-spec.md`](../../design/combat-calculation-spec.md); elements are
    visual-only until finalized.
- **Neutral is a real element slot, held back from the heroes on purpose.** There is no Neutral Drakn sister, no Neutral Drakn Bound
  hero and no Neutral Elder Dragon: the ten elements carry the story heroes. Neutral is for the cards that belong to no element and
  can be used across elements: tactics, items and equipment, utility cards and lower-tier cards, and the herald pair of the Angel
  Primes, Angelica and Angelo (`AP-001` and `AP-012`, see [`angel_primes_codex.md`](angel_primes_codex.md)), who are meant to be heroes
  any deck can play. How Neutral cards enter a deck is a deck and combat rule that is not written yet (open question below); the
  shared Neutral pool in the blueprint is the starting point.
- **Transcendent = new 7th rarity tier** (above Mythic), rarity-budget cost **64**. Reserved
  for the ten Drakn story heroines. Treated as apex chase/showcase cards; standard-format
  legality is an open Phase 2 decision (see deck-progression rules).
- **Combined cards:** a female hero fused with her aligned Elder Dragon — primarily alternate
  art, with the option to grant a spell/power boost. Detailed rules TBD.
- **Archetype retained** as a differentiation field, now first-class in the card schema
  alongside `class`, `creatureType`, `race`, `sex`, and `companion`.
- **Thorne naming is canonical** for the Drakn bloodline (the ten heroines + Draknare Thorne).
  Other heroes use names fitting their role/origin. `SD-###` collection numbers are adjustable.
- **Staged element rollout (revised Oct 2026; supersedes "all 10 elements from launch").** All ten
  elements are *designed* and their art pipeline is proven, but they release in stages: **Grass,
  Fire, Water** first (MVP), with **Darkness + Light** either folded into the first public push
  (five elements) or following as the first expansion; the remaining elements arrive in later
  expansions in an order driven by the story. Balance is still held by the symmetric per-element
  template (see the blueprint below) -- it now describes one element's worth of content, repeated per
  release. Real expansions also arrive later as new *themes*.
- **Card taxonomy** — card `type` is a **mechanical role** with six values today
  (Hero, Unit, Building, Worker, Tactic, Equipment) and is **extensible** (future roles such
  as Consumable). `creatureType` is a separate flavor/mechanics axis: **Humanoid, Dragon,
  Beast, Elemental, Undead, Construct, Spirit** (extensible).
- **Elder Dragons** = card `type: Unit`, `creatureType: Dragon`, `race: Dragon` (Mythic,
  aerial). **Beasts** (e.g., Dire Wolf) = `type: Unit`, `creatureType: Beast`. Non-hero
  creatures are Units by role, differentiated by creature type and archetype.
- **Series = Sovereign Dawn, `SD-###` numbering.** The launch series is **Sovereign Dawn**
  with **`SD-###`** collection numbers (replacing the placeholder "Base Set" / `BS-###`).
  Existing `BS-###` cards are renumbered/renamed as a migration.
- **Basic (0) tier.** A foundation/token tier below Common (0 rarity points) for spawned
  minions and humble filler; not a pack-collectible rarity. Full ladder is 0–7 (Basic →
  Transcendent).
- **Bonded pets & pairing.** Any **Rare-or-above** card can have a **bonded pet** that exists
  as its own card. **Leaning:** a *fusion-combine* model — like card evolution, you use the pet
  to evolve the owner into a **single combined card** (combined art + merged power). Exact rules
  next iteration. Schema support: `pairing` on `codex-schema.json`.
- **Vocabularies.** Canonical value pools for class, archetype, race, creature type, rarity,
  and the series name pool live in [`ideation_lists.md`](ideation_lists.md).
- **Story canon (draft).** The Drakn origin — the **Sundering** — is framed as a *union of
  magics*: Draknare and Drakness's bond of shadow-and-death magic overflowed and birthed the
  nine elemental sisters (Drakness remaining the tenth, Darkness). Drafted in the bible Prologue;
  explains ten heroines, one Drakn son, and the war over territory.

**Applied so far (this branch):**

- `data/schemas/codex-schema.json` — 10-element enum, Transcendent tier, points `[1,2,4,8,16,32,64]`,
  0–8 stars, `maxStars`, `tacticSlots` up to 8, six-role `type` enum + widened `cardId` pattern,
  and `archetype/class/creatureType/race/sex/companion` fields.
- `docs/game-bible.md` — seven-tier ladder, ten-element table, creature-taxonomy note, the Drakn
  Line / Thorne subsection (2.9), and the single-Base-Set + evolving-taxonomy + Consumable ideas.
- `docs/design/deck-progression-rules.md` — Transcendent cost (64) + apex/format notes + 10-element note.
- `docs/design/combat-calculation-spec.md` — 10-element cycle proposal with open decisions (Phase 2).
- `prompts/_templates/_hero-template.txt` — 10-element art palette.

**Tracked follow-ups (not yet done):**

- **Collection numbers:** the series is **Sovereign Dawn** with **`SD-###`**. The marquee 30
  (`SD-001`–`SD-030`) and 10 male bonded pets (`SD-031`–`SD-040`) are authored. ✅ The former
  `BS-###` base-set cards are migrated to `SD-041`–`SD-219` (219 cards total).
- **Bonded pets:** ✅ the 10 male heroes' pets (Reaper, Fire Elemental, Treant, Frost Owl,
  Shark, Angel, Dire Bear, Gryphon, Giant Eagle, Basilisk) are authored as `SD-031`–`SD-040`
  and wired to their owners. Remaining: pets for Rare+ *units* (per the pairing rule) as the
  element pool is built out.
- **Sovereign Dawn data migration (deliberate pass):** ✅ **done.** Migrated the 179 legacy
  cards + manifests + product boxes/packs + collection checklist from `base-set`/`Base Set`/`BS-###`
  to `sovereign-dawn`/`Sovereign Dawn`/`SD-041`–`SD-219`; added `series` objects; mapped `Frost` → `Ice`
  (pack + element-list renames); resolved the `UNIT_TREANT` collision (legacy → `UNIT_GROVE_TREANT`);
  rebuilt the 219-entry checklist and series-manifest breakdowns; rebuilt the earth/water starter
  boxes (were referencing phantom cardIds). Scripted + schema-validated (0 invalid of 219).
  Directories consolidated via `git mv` — all cards now live under `data/cards/sovereign-dawn/`
  (`heroes`, `units`, `dragons`, `pets`, `tactics`, `buildings`, `equipment`, `workers`,
  `element-lists`); the former `base-set/` and `phase-2-expansion/` folders are removed.
- **Card JSON authoring:** create `data/cards/` entries for the marquee 30, then fill element parity
  per the blueprint below (authored in waves with balance review).
- **Element art refresh:** existing `Frost` cards map to `Ice`; `Dark`/`Arcane` map to `Darkness`.

---

## Base Set composition blueprint

> **Status:** Proposed balance framework for the single 10-element Base Set. Counts are tunable;
> the point is a **symmetric per-element template** so the set stays balanced. Authored in waves.

**Per element (×10 elements):**

| Role | Count | Rarity spread | Notes |
| --- | ---: | --- | --- |
| Hero — female marquee | 1 | Transcendent | Drakn heroine (the "face" of the element) |
| Hero — male | 1 | Mythic | signature male hero |
| Hero — support | 1 | Epic | additional element hero |
| Elder Dragon | 1 | Mythic | `Unit` · `creatureType: Dragon` (aligned to the heroine) |
| Units | 8 | 3 Common · 2 Uncommon · 2 Rare · 1 Epic | mixed creatureType (Humanoid/Beast/Elemental/…) and archetype |
| Tactics | 4 | 2 Common · 1 Uncommon · 1 Rare/Epic | element-themed spells |
| **Per-element subtotal** | **16** | | **×10 = 160 element cards** |

**Shared Neutral pool (element-agnostic, authored once):**

| Role | Count | Notes |
| --- | ---: | --- |
| Buildings | ~12 | economy + military (Granary, Sawmill, Mine, Barracks, …) — art-only in MVP |
| Workers | ~8 | resource producers (Farmer, Miner, Lumberjack, …) — art-only in MVP |
| Equipment | ~14 | weapons / armor / accessories |
| Neutral tactics | ~4 | element-agnostic (Charge, Heal, Shield Wall, …) |
| Neutral heroes | 2 | Angelica and Angelo of the Angel Primes (`AP-001`, `AP-012`), a separate series usable in any deck; not in the subtotal |
| **Shared subtotal** | **~38** | |

**Base Set total ≈ 198 cards** (160 element + ~38 shared). Large but coherent as a single set,
and in the same ballpark as the prior 174-card base set — expanded for 10-element parity.

**Balance rules of thumb:**

- Every element gets the **same role/rarity template**, so no element is mechanically favored.
- Creature-type and archetype variety lives **within** each element's 8 units.
- Neutral economy/equipment is shared, keeping the elemental identity focused on heroes, dragons,
  units, and tactics. Neutral is also the home of utility and lower-tier cards that any deck can use.
- Expansions add new units/creatures/mechanics (and possibly new card types) on top — never by
  reworking this foundation.

---

## Open questions for reconciliation

- **10-element impact:** The Codex and combat/deck docs currently describe a smaller
  element set. Expanding to 10 elements touches element palettes, visual identity, and any
  future counter-chart design.
- **Rarity tiers:** This roster introduces `7 - Transcendent` (above Mythic) for the Drakn
  females. The bible's six-tier ladder (Common → Mythic) would need a defined 7th tier.
- **Combined cards:** Define how a female hero + her aligned Elder Dragon fuse into a
  "combined" card (stats, art, deck legality).
- **Neutral cards and decks:** Neutral cards (utility, tactics, items, lower-tier cards, and the Angel Primes herald pair) are
  meant to be playable in any deck whatever its elements. Define the deck-building rule (always legal, any count limits, whether a
  Neutral hero can lead a deck) in the deck and combat docs. Neutral heroes beyond Angelica and Angelo are not planned.
- **Class vs. archetype:** Confirm whether `Class` (Necromancer, Druid, etc.) and
  `Archetype` (Summoner / Spawner, etc.) both persist as card fields in `codex-schema.json`.
- **Naming:** Confirm the `SD-###` numbering scheme and the `<Name> Thorne` convention for the
  Drakn line as canonical.
