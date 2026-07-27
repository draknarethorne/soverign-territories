# Game Bible Review - Decision Log (July 2026)

**Status**: Accepted for documentation reset  
**Intent**: Convert independent review feedback into enforceable repo documentation policy and MVP execution focus.

---

## Accepted conclusions

1. `docs/game-bible.md` should remain the **vision anchor**, not the implementation truth for every formula.
2. MVP boundaries must be explicit and protected from Phase 2-3 feature bleed.
3. Progression/combat/economy formulas should be canonicalized in dedicated design/spec docs.
4. Monetization language should align with player-respect values and avoid exploitative framing.
5. Scripts/tools should align to schema contracts, not prose-heavy narrative sections.

---

## Immediate actions approved

- Use `docs/mvp/solo-dev-realistic-mvp.md` as the authoritative MVP timeline and scope baseline.
- Keep `docs/mvp/mvp-scope-final.md` for dependency mapping and implementation decomposition.
- Keep progression rules canonicalized in `docs/design/deck-progression-rules.md`.
- Keep combat formulas canonicalized in `docs/design/combat-calculation-spec.md`.
- Keep JSON schemas in `docs/specs/*.json` as script/tool/runtime contracts.

---

## Working implementation plan

See: `docs/working/documentation-reset-plan-jul2026.md`

This plan defines:

- MVP firewall
- canonical source-of-truth matrix
- archive criteria
- schema -> scripts/tools alignment protocol
- 2-week execution checkpoint goals

---

## Historical review content (preserved)

The original imported review write-up and prompt pack are preserved below for traceability.

---

Absolutely. Here’s a write-up you can feed into GHCP / Claude Opus 4.8 as structured feedback and prompt material. I’m going to frame it as **actionable repo-agent instructions**, not just “general thoughts,” so you can paste chunks directly into GitHub Copilot Chat / Claude.

***

# Feedback for GHCP / Claude: Sovereign Territories Game Bible Cleanup

## Context

This game bible was drafted and evolved with older AI assistance, which helped generate a lot of breadth but also introduced **inconsistencies, over-scoping, aggressive monetization language, duplicated systems, and blurred MVP boundaries**.

The current document is impressive and highly detailed, but it needs a **canonicalization pass**: reduce contradictions, separate MVP from future phases, soften monetization language, and reorganize the project into something buildable by a solo/part-time creator who is still learning Unity and may source/create graphics separately.

The repo should treat `docs/game-bible.md` as the **vision document**, not as the implementation truth for every detail. Supporting specs should become the source of truth for concrete systems.

The existing bible includes a strong structure: core philosophy, card system, map hierarchy, gameplay modes, economy, social systems, roadmap, combat, progression, matchmaking, UI/UX, technical integration, content pipeline, legal/compliance, edge cases, and next technical steps. It also references supporting MVP docs, Unity implementation guides, design specs, and JSON schemas. [\[usbank-my....epoint.com\]](https://usbank-my.sharepoint.com/personal/scott_elmer1_usbank_com/Documents/Microsoft%20Copilot%20Chat%20Files/game-bible.md)

***

# High-Level Assessment

## What is strong

Sovereign Territories has a very compelling design foundation:

* **Card-centric architecture**: everything revolves around cards — heroes, units, buildings, tactics, equipment, deployment, economy, map representation, and visual figurines. [\[usbank-my....epoint.com\]](https://usbank-my.sharepoint.com/personal/scott_elmer1_usbank_com/Documents/Microsoft%20Copilot%20Chat%20Files/game-bible.md)
* **Universal engine concept**: the core game engine can support multiple themes such as Medieval Fantasy, Sci-Fi, Norse Mythology, Historical, and Modern Warfare without rewriting core mechanics. [\[usbank-my....epoint.com\]](https://usbank-my.sharepoint.com/personal/scott_elmer1_usbank_com/Documents/Microsoft%20Copilot%20Chat%20Files/game-bible.md)
* **Player-time respect**: the design includes a 5-minute mobile loop, 30-minute deep session loop, AFK progression, auto-battle, offline rewards, and anti-grind language. [\[usbank-my....epoint.com\]](https://usbank-my.sharepoint.com/personal/scott_elmer1_usbank_com/Documents/Microsoft%20Copilot%20Chat%20Files/game-bible.md)
* **MVP awareness**: the document already distinguishes MVP, Phase 2, Phase 3, and Phase 4 in many areas, and references an MVP scope document, tutorial flow, implementation guide, economy spec, combat spec, and schema files. [\[usbank-my....epoint.com\]](https://usbank-my.sharepoint.com/personal/scott_elmer1_usbank_com/Documents/Microsoft%20Copilot%20Chat%20Files/game-bible.md)
* **Systems-thinking depth**: the design includes schemas, progression, economy, map hierarchy, AI tactics, matchmaking, legal/compliance, and content pipeline considerations. [\[usbank-my....epoint.com\]](https://usbank-my.sharepoint.com/personal/scott_elmer1_usbank_com/Documents/Microsoft%20Copilot%20Chat%20Files/game-bible.md)

## What needs cleanup

The bible currently feels like it contains **several complete games at once**:

* CCG / deck-builder
* tactical grid combat
* party-based RPG
* territory conquest
* AFK economy
* alliance warfare
* PvP matchmaking
* auction house
* social platform
* live-service monetization
* seasonal expansion engine

That is fine for a long-term vision, but it is too broad for MVP. The next pass should **protect the MVP from the full dream**.

***

# Key Problems to Fix

## 1. MVP scope is too broad

The current document sometimes says the MVP is focused on card collection, deck-building, and tactical campaign battles, while other sections include AFK economy, territory conquest, buildings, alliances, shiny systems, PvP, auction house, battle pass, VIP, and live operations concepts. The document does label many of these as future phases, but the separation is not always consistent. [\[usbank-my....epoint.com\]](https://usbank-my.sharepoint.com/personal/scott_elmer1_usbank_com/Documents/Microsoft%20Copilot%20Chat%20Files/game-bible.md)

### Recommendation

Create a hard three-tier separation:

```text
MVP / Phase 1A:
Build only the smallest playable vertical slice.

Phase 1.5 / Polish:
Improve retention, tutorial, content, UX, balancing, and art.

Phase 2+ / Expansion:
Territory systems, economy depth, PvP, alliance, auction house, major live-service mechanics.
```

The MVP should probably be:

```text
1. Unity project setup
2. Static card data
3. Basic card collection screen
4. 6-slot battle formation
5. deterministic 8x8 tactical combat
6. simple PvE campaign path
7. basic reward loop
8. gold/energy only
9. tutorial flow
10. placeholder art
```

Defer:

```text
- alliances
- PvP
- auction house
- shiny bonuses
- territory conquest
- full AFK economy
- VIP system
- battle pass
- named mobs
- loot governors
- social chat
- seasonal events
- multiple themes
```

***

## 2. Rarity, stars, and leveling have contradictions

The bible has multiple versions of rarity and star progression. In one place, Common cards can rank from 1–3 stars and all rarities can rank up. Later, another section says Common cards are fixed at 1★ and cannot level. Similar drift exists around Legendary/Mythic progression and star caps. [\[usbank-my....epoint.com\]](https://usbank-my.sharepoint.com/personal/scott_elmer1_usbank_com/Documents/Microsoft%20Copilot%20Chat%20Files/game-bible.md)

### Recommendation

Create a single canonical document:

```text
docs/design/progression-rules.md
```

Then make `game-bible.md` point to it instead of repeating the rules in multiple places.

The progression document should define:

```text
- rarity tiers
- starting stars
- max stars
- duplicate requirements
- gold costs
- tactic slot scaling
- stat scaling
- whether each rarity can level
- MVP rules vs future rules
```

Use one of these strategies:

### Option A — Simple MVP rules

```text
Common: 1★ only
Uncommon: 1–2★
Rare: 2–3★
Epic: 3–4★
Legendary: 5★ fixed
Mythic: not in MVP
```

### Option B — Full future rules

```text
Common: 1–3★
Uncommon: 1–4★
Rare: 2–5★
Epic: 3–6★
Legendary: 5–7★
Mythic: 6–8★
```

But do **not** mix both without explicitly labeling one as MVP and one as future.

***

## 3. Monetization language is too aggressive

Older AI likely pushed the document toward “whales,” FOMO, VIP, pity systems, spending caps, shiny utility, battle pass, and revenue projections. Some of that is valid for market analysis, but the language can feel extractive and may conflict with the stated “respect player time” and “zero pay-to-win” philosophy. [\[usbank-my....epoint.com\]](https://usbank-my.sharepoint.com/personal/scott_elmer1_usbank_com/Documents/Microsoft%20Copilot%20Chat%20Files/game-bible.md)

The design says “zero pay-to-win,” but also gives shinies 5% production/combat bonuses and gives Premium Packs a 10× shiny rate. That creates tension. [\[usbank-my....epoint.com\]](https://usbank-my.sharepoint.com/personal/scott_elmer1_usbank_com/Documents/Microsoft%20Copilot%20Chat%20Files/game-bible.md)

### Recommendation

Replace aggressive monetization framing with ethical monetization principles.

Use language like:

```text
The monetization model should prioritize:
- cosmetics
- convenience
- optional content
- expansion packs
- battle pass cosmetics
- account-level quality-of-life

The monetization model should avoid:
- exclusive mechanical power
- unlimited spending loops
- pressure-based FOMO
- paid-only competitive advantages
- manipulative whale targeting
```

Replace “whale bait” and similar phrases with:

```text
collector-oriented
high-engagement player
premium convenience
optional acceleration
cosmetic prestige
```

Also decide whether shinies are:

```text
A) purely cosmetic
B) minor progression utility
C) non-competitive utility only
```

For fairness, I recommend:

```text
MVP: shinies are cosmetic only.
Future: shiny utility can be reconsidered only for non-ranked/non-PvP systems.
```

***

## 4. Too many systems are described as if implementation-ready

The document includes detailed designs for systems that should not exist in the first build:

* auction house
* alliance diplomacy
* multi-channel chat
* moderation
* VIP
* battle pass
* PvP market
* named mob loot
* global leaderboards
* player stat histories
* seasonal expansions
* territory wars

These are valuable vision notes, but they should be moved out of the MVP path. [\[usbank-my....epoint.com\]](https://usbank-my.sharepoint.com/personal/scott_elmer1_usbank_com/Documents/Microsoft%20Copilot%20Chat%20Files/game-bible.md)

### Recommendation

Reorganize the bible into layers:

```text
docs/game-bible.md
  High-level vision only

docs/mvp/
  MVP scope
  tutorial flow
  first playable loop
  Unity implementation guide

docs/design/
  Long-term systems
  economy
  combat
  cards
  progression
  maps
  tactics

docs/future/
  alliance wars
  auction house
  PvP
  seasonal events
  social/chat
  monetization experiments

docs/archive/
  Older superseded ideas
```

***

# Prompt 1: Full Bible Audit

Paste this into GHCP / Claude:

```text
You are acting as a senior game systems designer and software architect reviewing this repository.

The file docs/game-bible.md was generated and iterated with older AI tooling. It contains strong design ideas but also contradictions, over-scoping, aggressive monetization language, repeated concepts, and unclear MVP boundaries.

Please audit docs/game-bible.md and produce a structured report with:

1. Major contradictions
2. Repeated or duplicated systems
3. Mechanics that conflict with the stated design philosophy
4. Sections that belong in MVP
5. Sections that should move to Phase 2+
6. Sections that should move to archive/future notes
7. Monetization language that should be softened or rewritten
8. Star/rarity/progression inconsistencies
9. Economy inconsistencies
10. Recommended document reorganization

Do not rewrite the whole document yet. First produce a concise but thorough audit with file/section references and concrete recommendations.
```

***

# Prompt 2: MVP Firewall

```text
Act as a ruthless MVP product owner for an indie Unity game.

The current game bible describes a large long-term vision for Sovereign Territories, but I need to define the smallest playable vertical slice that I can realistically build while learning Unity.

Please create a strict MVP scope for Phase 1A.

Constraints:
- Solo/part-time developer
- Still learning Unity
- Placeholder art is acceptable
- No backend unless absolutely required
- No multiplayer
- No alliance system
- No auction house
- No live-service monetization
- No PvP
- No full territory conquest
- No complex AFK economy
- No final art requirement

MVP should include only:
- basic card data
- starter deck
- 6-slot formation
- deterministic 8x8 battle
- simple campaign progression
- basic rewards
- simple card collection screen
- tutorialized first session

Output:
1. MVP feature list
2. Explicit non-goals
3. 4-week prototype plan
4. 8-week MVP plan
5. Unity scenes needed
6. ScriptableObject/data model needed
7. Minimum placeholder art list
8. Success criteria for “playable”
```

***

# Prompt 3: Canonical Rules Extraction

```text
Review docs/game-bible.md and extract all rules related to:
- card rarity
- star rank
- card leveling
- duplicate fusion
- tactic slots
- stat scaling
- card drops
- pack rarity odds

The current bible appears to contain conflicting versions of these systems.

Please produce a new canonical document draft for:

docs/design/progression-rules.md

Requirements:
- Clearly separate MVP rules from future expansion rules
- Remove contradictions
- Prefer simple MVP implementation
- Include open questions where design decisions are unresolved
- Do not overcomplicate the MVP
- Make the document suitable as the single source of truth for progression rules

After drafting, list which sections of docs/game-bible.md should be updated to reference this new file instead of repeating progression formulas.
```

***

# Prompt 4: Monetization Rewrite

```text
Review the monetization, VIP, pack, shiny, pity, battle pass, and “whale” sections in docs/game-bible.md.

The current language is too aggressive and was generated with older AI. I want the tone to reflect ethical monetization and player respect.

Please rewrite the monetization philosophy with these principles:
- No exclusive mechanical power
- No pay-to-win
- Paid options may provide cosmetics, convenience, or optional acceleration
- Competitive modes should be normalized or budget-limited
- Avoid exploitative FOMO language
- Avoid referring to players as “whales” in player-facing or design philosophy sections
- Keep revenue ideas as internal notes only, not core design identity
- Shinies should be cosmetic-only for MVP

Output:
1. Recommended monetization principles
2. Revised language for the game bible
3. Sections to archive or move to internal business notes
4. Systems that should be deferred until after the game is fun without purchases
```

***

# Prompt 5: Reorganize the Game Bible

```text
Act as a technical documentation architect.

Please propose a reorganization of the Sovereign Territories documentation.

Current problem:
docs/game-bible.md is too large and mixes vision, MVP implementation, future roadmap, monetization, legal, combat formulas, economy details, schemas, and social systems.

Goal:
Make docs/game-bible.md readable as the master vision document while moving implementation details into focused specs.

Propose:
1. New docs folder structure
2. What stays in game-bible.md
3. What moves to docs/mvp/
4. What moves to docs/design/
5. What moves to docs/future/
6. What moves to docs/archive/
7. A migration checklist
8. Naming conventions for canonical docs
9. Cross-reference strategy so each system has one source of truth

Do not delete content. Preserve ideas, but move detail to the right place.
```

***

# Prompt 6: Unity Learning Path + First Prototype

```text
Act as a Unity technical mentor for a senior software engineer who is new to Unity but experienced in architecture and systems design.

Given the Sovereign Territories game bible, recommend the first playable prototype.

Constraints:
- I am still learning Unity
- I can use placeholder graphics
- I may have my daughter create original card art / UI art later
- I want to avoid overbuilding architecture before proving the loop
- I prefer clean foundations and maintainable systems

Output:
1. What Unity concepts I need to learn first
2. Minimal scenes to create
3. Minimal scripts/components
4. Recommended ScriptableObject structure
5. How to represent cards with placeholder art
6. How to build the 8x8 grid simply
7. How to implement deterministic combat first
8. What to avoid until later
9. A week-by-week learning/build plan for the first month
```

***

# Prompt 7: Art Direction / Daughter-Friendly Brief

```text
Create an art direction brief for Sovereign Territories suitable for a young/learning artist or a family collaborator.

The art should support a prototype first, not a polished commercial release.

Needs:
- placeholder-friendly style
- simple card frames
- readable icons
- element colors
- rarity indicators
- simple unit tokens for an 8x8 grid
- basic terrain tiles
- UI buttons and panels
- future direction toward stylized fantasy card art

Output:
1. Art style principles
2. MVP asset list
3. Nice-to-have asset list
4. Card template requirements
5. Unit token requirements
6. Color palette suggestions
7. File naming conventions
8. Tips for working iteratively with a developer
9. What not to spend time on yet
```

***

# Prompt 8: “Tone Down and Humanize” Pass

```text
Review docs/game-bible.md for tone.

The current document was created with older AI and sometimes uses aggressive or overly commercial language around monetization, FOMO, whales, addiction loops, and retention pressure.

Please rewrite the tone to align with these values:
- strategic depth without exploitation
- respect for player time
- fair progression
- cozy but tactical
- collectible but not predatory
- competitive but not punishing
- accessible for busy adults
- solo/indie build realism

Output:
1. List of phrases/sections that feel too aggressive
2. Suggested replacement language
3. Revised design philosophy section
4. Revised retention philosophy section
5. Revised monetization philosophy section
```

***

# Recommended Order to Run These Prompts

I would not toss all of this at Claude at once. I’d run them in this order:

```text
1. Full Bible Audit
2. MVP Firewall
3. Canonical Rules Extraction
4. Reorganize the Game Bible
5. Monetization Rewrite
6. Unity Learning Path
7. Art Direction Brief
8. Tone Down and Humanize Pass
```

That order matters because you want the repo to first understand:

```text
What is inconsistent?
What is MVP?
What are canonical rules?
Where should content live?
```

Only then should it rewrite tone, monetization, and implementation plans.

***

# My Suggested North Star for the Rewrite

If I were giving Claude one guiding sentence, it would be this:

```text
Preserve the ambition of Sovereign Territories, but reorganize it so Phase 1 is a small, learnable, playable Unity tactics/card prototype, while the larger empire/territory/live-service vision remains documented as future architecture rather than MVP scope.
```

Or shorter:

```text
Make the dream smaller without making the vision smaller.
```

That’s the key. You don’t need to throw away the big idea. You just need to keep the big idea from crushing the first playable build.
