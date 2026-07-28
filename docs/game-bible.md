# ⚔️ Sovereign Territories — The Complete Codex

> **Build the Deck. Conquer the Campaign. Level Your Heroes.** *(the promise we prove first)*
>
> **Build the Deck. Rule the Map. Automate the Empire.** *(the world we grow into)*

*The master design codex for Sovereign Territories — a multi-genre hybrid strategy game
where card collection meets tactical command meets territorial conquest. This is the grand
vision: how the finished game should look, feel, play, and endure. It is written to inspire
the build, not to constrain it into a single sprint.*

**Vision** • **Card System** • **Maps** • **Modes** • **Economy** • **Social** •
**Combat** • **Progression** • **Multiplayer** • **UI** • **Tech** • **Polish** •
**Expansions** • **Roadmap**

---

## 📜 How to read this codex

This is the **Grand Bible** — the complete creative vision. It intentionally describes the
whole game, across every phase, in full colour. It is the north star for artists,
designers, and engineers alike.

To keep ambition and delivery honest, every major system in this codex carries four tags:

- **MVP expression** — the small, shippable form of the idea today (often "none yet").
- **Future expression** — the full realized vision.
- **Authority** — the canonical document that owns exact rules, numbers, and contracts.
- **Status** — `Vision`, `Proposed`, `Validated`, or `Deferred`.

**The codex inspires. The canonical documents decide.** When this file and a canonical
document disagree on an implementation detail, the canonical document wins.

| Concern | Canonical authority |
| --- | --- |
| MVP scope, schedule, go/no-go | [`mvp/solo-dev-realistic-mvp.md`](mvp/solo-dev-realistic-mvp.md) |
| MVP dependency and acceptance plan | [`mvp/mvp-scope-final.md`](mvp/mvp-scope-final.md) |
| Combat rules and formulas | [`design/combat-calculation-spec.md`](design/combat-calculation-spec.md) |
| Deck legality, rarity, formation | [`design/deck-progression-rules.md`](design/deck-progression-rules.md) |
| Onboarding sequence | [`mvp/tutorial-flow.md`](mvp/tutorial-flow.md) |
| Map/mode phase gates | [`design/map-tier-progression.md`](design/map-tier-progression.md), [`design/gameplay-modes-spec.md`](design/gameplay-modes-spec.md) |
| Runtime data contracts | [`../data/schemas/*.json`](../data/schemas) |
| Archive reconciliation & readiness | [`working/archive-canon-reconciliation-jul2026.md`](working/archive-canon-reconciliation-jul2026.md) |

> 💡 **A note on numbers.** Where this codex mentions specific values (drop rates, costs,
> stat curves, map sizes), treat them as *illustrative texture* that communicates intent.
> The living numbers live in the canonical design docs and `data/schemas/`, and they win.

---

## 🗺️ Table of Contents

1. Core Philosophy
2. The Card System (Assets & Collection)
3. The Map Hierarchy (The World)
4. Gameplay Modes
5. Economy & Trading
6. Social Infrastructure
7. Combat Mechanics
8. Progression & Balance
9. Multiplayer & Matchmaking
10. User Interface & Experience
11. Technical Integration
12. Sound & Polish
13. Extension Roadmap (Future-Proofing)
14. Legal, Safety & Compliance
15. Edge Cases & Resilience
16. Delivery Roadmap
17. Inspirations & Credits

---

## ⚔️ SECTION 1 — Core Philosophy

### What Sovereign Territories is

Sovereign Territories is a **multi-genre hybrid strategy game** that takes the most joyful
mechanics from decades of gaming and stitches them into one coherent world.

**Genre DNA**:

- **TCG / CCG** (Pokémon TCG, Magic, Hearthstone) — deck-building, six rarity tiers, the
  thrill of the pack, collection as identity.
- **Party RPG** (Baldur's Gate, Neverwinter Nights, Diablo) — heroes with real stats,
  equipment, leveling, and a party that feels like *yours*.
- **Tactical strategy** (Heroes of Might and Magic, Fire Emblem) — grid battles, hero-led
  armies, formations, terrain.
- **Territorial conquest** (Risk, Civilization) — map control, alliances, seasonal wars.
- **Tabletop wargaming** (Warhammer) — figurines on the map, visual armies, deployment.
- **Roguelike & idle** (Slay the Spire, AFK Arena) — replayable runs and progression that
  respects a busy life.

**The core loop**: *Collect cards → Build decks → Command heroes → Conquer battles → Grow
stronger → Unlock new worlds → Repeat with fresh themes and seasons.*

**What makes it different**: We keep the **fun** (opening packs, leveling heroes, clever
tactics, exploration) and refuse the **tedium** (forced resource grinding, build timers,
babysitting production queues). The engine is universal — one ruleset that can wear Medieval
Fantasy, Norse Myth, Sci-Fi, or Historical skins without a rewrite.

### The five pillars

1. **Strategic clarity** — Visible information and deterministic early combat. A player can
   *understand* a decision before they make it, and *learn* from every outcome.
2. **Collector identity** — Six rarities, thematic decks, seasonal exclusives. Growing a
   roster opens tactics, not paywalls.
3. **Respect for time** — Short, complete sessions. No coercive check-ins, no punishing
   streak traps, no "log in or lose everything."
4. **Fair competition** — When PvP arrives, skill and roster fairness come first, with real
   protections against griefing.
5. **Phased ambition** — Maps, economies, and social warfare are *earned* by proving the
   core loop, never bolted on as unproven scope.

### What we EMBRACE / what we AVOID

**We EMBRACE (the fun parts)**:

- ✅ The dopamine of opening a pack and chasing a legendary.
- ✅ Leveling a hero you love and watching them become iconic.
- ✅ Tactical battles where positioning and card roles decide the day.
- ✅ Passive, opt-in progression that rewards you for coming back — never for grinding.
- ✅ A collection that lives *on the map*, not hidden in an abstract list.

**We AVOID (the tedious parts)**:

- ❌ Tap-to-collect resource grind and endless build timers.
- ❌ Forced PvP that lets veterans stomp newcomers.
- ❌ Pay-to-win power sold to the highest spender.
- ❌ Manipulative FOMO, loss-aversion streaks, and social guilt as retention.
- ❌ Complexity for its own sake that buries the joy.

### The MVP firewall

> **Status:** Validated · **Authority:** [`mvp/solo-dev-realistic-mvp.md`](mvp/solo-dev-realistic-mvp.md)

To protect both the dream and the delivery, we hold one discipline: **the first release
proves the tactical loop, nothing more.** The MVP is a local-first, single-player slice —
a small collection, a six-card formation with exactly one hero, deterministic 8×8 PvE
battles, a short authored campaign, and honest rewards. Everything grander in this codex is
*documented vision*, phase-gated behind proof and playtesting.

If a section here reads like a launch requirement, read it again through the firewall: it is
the world we grow into, not the sprint we start with.

---

## 🎴 SECTION 2 — The Card System (Assets & Collection)

*Everything in Sovereign Territories is a card. Heroes, units, buildings, tactics,
equipment — you collect them, customize them, and deploy them as living pieces on the
world. This is the heart of the game.*

### 2.1 Card types

> **MVP expression:** Heroes, Units, Tactics (small validated set). Buildings/Workers exist
> as art/identity only. · **Future expression:** All six types fully functional. ·
> **Authority:** [`../data/schemas/card-schema.json`](../data/schemas/card-schema.json)

- **Heroes** — Unique commanders who anchor a formation. Immortal in spirit (defeated heroes
  recover), they grant identity and, in later phases, lead independent armies. *Thor calls
  the storm; a stone sentinel holds the line.*
- **Units** — The body of your force: infantry, archers, cavalry, mages. Stackable in the
  grand vision, expendable in the harsh calculus of war.
- **Buildings** *(economy vision)* — Static structures placed on the world for production
  and defense. Drawn from a separate economy deck.
- **Workers** *(economy vision)* — The quiet engines of an empire: farmers, miners,
  lumberjacks who turn tiles into resources while you sleep.
- **Tactics** — The dual-purpose soul of combat: **AI instruction** (who, what, when) fused
  with **effect** (how much). "Heal the hero below 70%" plus "restore 50 HP" equals a
  Legendary saved from death. Tactics *attach* to cards; they do not burn deck slots.
- **Equipment** — Gear that bolts onto heroes for power and spectacle: a blade that glows,
  armor that turns a silhouette into a legend.

### 2.2 Rarity & customization — the six tiers

> **MVP expression:** Rarities exist as identity + budget cost. · **Future expression:**
> Full fusion, star ranks, skill trees, shinies. · **Authority:**
> [`design/deck-progression-rules.md`](design/deck-progression-rules.md)

Six tiers form the collector's ladder — **Common, Uncommon, Rare, Epic, Legendary,
Mythic**. Our visual grammar is Pokémon-clean:

- **Element determines frame colour** — Fire is red-orange, Water is blue, Earth is
  brown-green, Lightning is gold-violet, Wind is cyan-white, Frost is pale ice.
- **Rarity determines frame complexity & effect** — from a Common's clean matte border to a
  Mythic's living, screen-touching aura.
- **Stars show progression** within a tier — white stars with an element-coloured glow.

**Why it works**:

- **Instant recognition** — a Fire deck reads as a wall of warm frames.
- **Collector excitement** — holographic shimmer means *something rare just happened*.
- **Accessibility** — colourblind players still read rarity by frame complexity.
- **Future-proof** — new elements are new colours; new rarities are new effect tiers.

> 💡 The exact star ranges, fusion costs, stat multipliers, and drop rates are owned by the
> deck-progression and card schemas so the codex never drifts from the math.

### 2.3 Card anatomy

```text
┌─────────────────────────────────┐
│ [Rarity Badge]        [Element] │  ← identity at a glance
│                                 │
│           [Card Art]            │  ← illustration on an element-tinted field
│                                 │
├─────────────────────────────────┤
│  [Name]                 [Cost]  │
├─────────────────────────────────┤
│        [Stats & Abilities]      │
├─────────────────────────────────┤
│        ★ ★ ★ ☆ ☆                │  ← star progression, element-glow
└─────────────────────────────────┘
   frame colour = element · frame complexity = rarity
```

### 2.4 Fusion & star ranks *(future vision)*

> **Status:** Deferred (Phase 1.1+) · **Authority:** deck-progression rules + card schema

Duplicate cards fuse to raise **star rank**, granting more stats and more tactic slots.
Lower rarities max quickly (a satisfying F2P goal); higher rarities demand real investment
(a whale-and-veteran chase). Rarity supremacy is preserved — a same-star Epic always
out-bases a Common. The dopamine ladder runs Bronze → Silver → Gold → Prismatic borders,
with damage numbers that brighten as a card ascends.

### 2.5 Shiny variants *(future vision)*

> **Status:** Deferred (Phase 2) · **Authority:** pack + card schemas

Shinies are **cosmetic-first** alternate arts with living animation and a small, honest
collector's edge (a modest deploy bonus — flex, not dominance). They carry a transparent
pity system and weekly acquisition caps so the market stays healthy and no one can "buy the
ladder" on day one. Shinies exist to make collectors smile, not to gate power.

### 2.6 Tactics — the attachment system *(design signature)*

> **MVP expression:** A small set of deterministic, mana-costed abilities. · **Future
> expression:** Rich AI-instruction + effect library, swappable per battle. · **Authority:**
> combat spec + `../data/schemas/tactic-schema.json`

Where other card games *spend* a spell and discard it, Sovereign Territories **attaches**
tactics to cards. They persist for the whole battle, they scale with star rank, and the same
unit becomes a different soldier depending on what it carries. Five Healers with five
loadouts are five distinct roles: a taunting guardian, a mobile medic, a burst-saver, a
battle-cleric, a budget backup. *This is deck-building that lives on the battlefield.*

### 2.7 The pack system — three tiers *(future vision)*

> **Status:** Deferred (Phase 1.1+) · **Authority:** `../data/schemas/pack-schema.json`

- **Tier 1 — Universal Packs**: the friendly default. A familiar mix of card types, with
  guaranteed foundation cards and transparent pity counters.
- **Tier 2 — Specialized Boosters**: focus a hunt (battle-only, economy-only) for veterans
  who know what they need.
- **Tier 3 — Premium Theme Packs**: element sets, faction collections, and seasonal drops
  with alternate art for collectors.

Every pack shows its odds. Pity systems are visible and honest. **No card is ever locked
behind a wall of money** — the rarest legendary is reachable through play.

### 2.8 Onboarding — the Trainer Deck philosophy

> **MVP expression:** One prevalidated starter collection and a short learn-by-doing path. ·
> **Future expression:** Curated + element Trainer Decks with a signature choice moment. ·
> **Authority:** [`mvp/tutorial-flow.md`](mvp/tutorial-flow.md)

The first five minutes should feel like *power, not paperwork*. A new Sovereign gets a
playable hero immediately and a meaningful choice of path — never a "bad luck" first pull.
The full vision offers curated decks (perfect synergy for beginners) and element decks
(higher variance for veterans). The MVP delivers a single, guaranteed-legal starter so no
one is ever stranded without a formation.

---

## 🌍 SECTION 3 — The Map Hierarchy (The World)

> **MVP expression:** Static campaign stage selection + the 8×8 battle board. No exploration.
> · **Future expression:** A fractal, four-tier living world. · **Status:** Deferred
> (Phase 2+) · **Authority:** [`design/map-tier-progression.md`](design/map-tier-progression.md)

*The world of Sovereign Territories is fractal: time scales to map size, and every tier
nests inside the next. This is the "Rule the Map" half of the promise — and it is
deliberately a later chapter.*

### The four tiers

- **Tier 1 — World Map** *(seasonal)*: continents and oceans, hundreds of territories,
  alliance wars, wonders that grant server-wide blessings, three-month seasons.
- **Tier 2 — Territory Map** *(monthly)*: a hex region of realms, castle sieges in phases
  (breach the walls, take the courtyard, storm the throne), monthly campaigns.
- **Tier 3 — Realm Map** *(weekly / exploration)*: a HoMM-style board of locations —
  towns, dungeons, mines, ruins, treasure, monster spawns — with fog of war and paced
  movement.
- **Tier 4 — Battle Map** *(the encounter)*: the 8×8 tactical grid where every conflict is
  actually decided. **This is the only tier in the MVP.**

### Figurines, castles, and living territory *(vision)*

The grand vision makes your collection *visible on the world*. A controlled tile shows your
army as figurines whose look reflects their composition — a cavalry general becomes a
mounted statue; a stacked garrison layers into a grouped monument. Towns grow into castles
with banners and walls as you level them. **Your collection is your kingdom, on display.**

**Why it works**: collecting feels tangible, position matters (flanks, chokepoints,
terrain), and status is visible ("look at my Tier 3 castle with its legendary standard").

> 🔮 Every map layer is gated behind a prototype, a data contract in `data/schemas/`, and an
> anti-griefing / catch-up design. The world is a promise, not a launch requirement.

---

## 🎮 SECTION 4 — Gameplay Modes

> **MVP expression:** One mode — the linear tactical campaign. · **Future expression:** A
> constellation of modes for every playstyle. · **Authority:**
> [`design/gameplay-modes-spec.md`](design/gameplay-modes-spec.md)

### 4.1 Campaign — the MVP core *(Validated)*

A linear, authored PvE journey through a named world. The MVP uses a **World → Territory →
Realm → Battle** naming so players learn the world's language early, without needing the
full map systems. Static stage selection (think Fire Emblem's campaign map), three-star
ratings (Victory / Speed / Perfect), and boss encounters that punctuate the climb. This is
where we prove that collecting, forming a party, and fighting is *fun*.

### 4.2 Bounty Board — replayable challenges *(vision)*

> **Status:** Proposed (Phase 1.x)

Rotating combat contracts with `/con`-style difficulty (green → red, an EverQuest homage),
randomized enemy compositions, and refresh timers. Optional content that never blocks the
campaign — variety for the hungry, ignorable for the busy.

### 4.3 Loot & spawn systems — Diablo texture *(vision)*

> **Status:** Deferred (Phase 2)

Per-enemy loot drops, enemy-specific tables, rare "named mobs" with guaranteed prizes, and a
governor that keeps card drops exciting without gutting pack value. Instance-style spawn
pools give the same stage a fresh face on every run.

### 4.4 The wider constellation *(vision)*

- **Saga Campaign** — story chapters with narrative and multi-phase bosses.
- **Expeditions** — a weekly board-game mode (roll, move, mini-battle) for a change of pace.
- **Alliance Events** — cooperative PvE raids and PvP sieges at guild scale.
- **Arena** — matchmade, bracketed competition that rewards skill.
- **Territory & World conquest** — the seasonal endgame.

Each mode is admitted only when its prerequisites, data contract, and safety model exist —
and when players have told us they want it.

---

## 💰 SECTION 5 — Economy & Trading

> **MVP expression:** A simple local reward loop (earned soft currency, basic grants). ·
> **Future expression:** A multi-currency economy that resists pay-to-win by design. ·
> **Authority:** `../data/schemas/resource-schema.json`, economy design docs

*Multiple currencies exist for one reason: so that no single stack of money can buy the
whole game.*

### The currency philosophy

- **Gold (soft)** — earned through play, **never** bought with money. This is the F2P
  fairness pillar.
- **Gems (premium)** — bought or slowly earned, spent on convenience and cosmetics, with
  sane weekly ceilings.
- **Energy / Stamina** — a gentle session pacer that encourages a few visits a day, not a
  grind marathon.
- **Food / Lumber / Ore** *(future)* — AFK production resources that **cannot** be bought,
  so patience and presence — not wallets — build an empire.

### AFK progression — respect, not obligation *(vision)*

Placed buildings and workers generate resources while you are away. The point is *coming
back to good news*, never *punishment for leaving*. Auto-collection means no tap-tap-tap;
you spend resources on meaningful choices, not micromanaged queues.

### Monetization — player-respect by design

> **MVP expression:** None required; the MVP is judged on fun, not revenue. · **Future
> expression:** Pay-for-convenience and pay-for-cosmetics — **never** pay-for-power.

**What money may buy**: time (convenience), style (cosmetics), and support for the project.
**What money must never buy**: raw power, exclusive win-conditions, or an unfair edge.

**Our guardrails**:

- ✅ Transparent odds and visible pity on everything random.
- ✅ Skill- and roster-fair matchmaking so spenders meet spenders.
- ✅ Meta decks buildable mostly from common cards.
- ✅ Honest spend awareness and family controls.
- ❌ No loot-box gambling framing, no manufactured FOMO in the core philosophy, no
  "one-more-pack" dark patterns.

> 💡 Business modeling (ARPU, conversion, tiers) belongs in internal planning, not in the
> creative identity of the game. The codex commits to *fairness*; the spreadsheets live
> elsewhere.

---

## 🤝 SECTION 6 — Social Infrastructure

> **MVP expression:** None (single-player, local-first). · **Future expression:** A living
> social world — alliances, diplomacy, chat, friends. · **Status:** Deferred (Phase 3+) ·
> **Authority:** `../data/schemas/alliance-schema.json`, `diplomacy-schema.json`

*The endgame fantasy of Sovereign Territories is social: rise from a lone Sovereign to a
warlord among allies. It is also the phase that demands the most care — moderation, safety,
and fairness before spectacle.*

### Safe growth to competitive play *(vision)*

The social ladder is **opt-in and level-gated**, so newcomers master fundamentals in safety
before any competitive pressure:

- **Alliance membership** — social foundation and cooperative PvE first.
- **Matchmade Arena** — controlled, bracketed PvP with no territory loss.
- **Active PvP maps** — opt-in open-world conquest with anti-griefing shields.
- **Alliance Wars** — large-scale guild warfare for the truly seasoned.

### Chat, diplomacy & safety *(vision)*

Rich channels (global, regional, alliance, whisper, battle), translation for a global
community, and treaties with real teeth (non-aggression, resource-sharing, joint defense).
Every social system ships **with** its moderation, reporting, and anti-harassment tooling —
never after. A safe PvE path always remains for players who prefer it.

---

## ⚔️ SECTION 7 — Combat Mechanics

> **MVP expression:** Deterministic HP/Mana/ATK/DEF on an 8×8 grid; elements are visual
> only. · **Future expression:** Elemental counters, terrain, status effects, deeper
> tactics. · **Authority:** [`design/combat-calculation-spec.md`](design/combat-calculation-spec.md)

*Combat is the heart of the game, and the MVP heart beats with total clarity.*

### The MVP contract *(Validated)*

- **8×8 tactical grid**, turn-based, no hidden rolls.
- **Damage = `max(1, ATK − DEF)`**; a card survives until HP reaches zero.
- **Mana** gates authored abilities; basic attacks are always free (no deadlock).
- **Elements are identity only** in the MVP — the same visible stats produce the same result
  regardless of colour.
- **No** critical RNG, terrain modifiers, or status effects at launch.

**Why deterministic first**: players can plan several turns ahead with certainty, losses
feel *earned* ("I misplayed") rather than *robbed* ("bad RNG"), replays are perfectly
reproducible, and balance is honest because no randomness hides a flaw.

### The tactical vision *(future)*

> **Status:** Deferred (Phase 2+) · **Authority:** combat spec, phase-gated sections

Later chapters introduce the classic rock-paper-scissors of the elements, terrain that
rewards the high ground, status effects (burn, freeze, poison, stun), stack mathematics, and
multi-hero armies. Each is a designed system with published multipliers, caps, counterplay,
and — critically — a rebalance of the whole card set. The exact numbers always live in the
combat spec, never here.

---

## 📈 SECTION 8 — Progression & Balance

> **MVP expression:** Card grants + light player progress. · **Future expression:** Dual
> progression — account-wide Player Level and per-territory Castle Level. · **Authority:**
> `../data/schemas/progression-schema.json`, deck-progression rules

### Dual progression *(vision)*

- **Player Level** — account-wide mastery that *unlocks content*, never raw power. A Level 50
  player with commons should still fear a Level 10 player with a sharp legendary deck.
- **Castle Level** — per-territory development that grants economic and building depth, and
  can be lost and rebuilt without erasing your account identity.

### Deck constraints — fairness as a feature

> **Authority:** [`design/deck-progression-rules.md`](design/deck-progression-rules.md)

The **rarity budget** is the anti-pay-to-win keystone: a deck's total rarity cost is capped,
so no one fields all-legendaries. Combined with a copy limit and the single-hero MVP rule,
this keeps decks expressive and fair. The MVP formation is six cards, exactly one hero — a
rule that gives every deck a clear identity. Multi-hero armies are a celebrated *future*
format, not an MVP assumption.

### Endless goals *(vision)*

Short-term dailies, medium-term collection chases, long-term rank climbs, and infinite
prestige/tower loops keep a north star always on the horizon — for achievers, competitors,
socializers, and explorers alike.

---

## 🌐 SECTION 9 — Multiplayer & Matchmaking

> **MVP expression:** None (local-first PvE). · **Future expression:** Elo-fair, roster-fair
> competition with real anti-cheat. · **Status:** Deferred (Phase 1.1+) · **Authority:**
> `../data/schemas/matchmaking-schema.json`

*When competition arrives, it arrives fair.* The vision pairs Elo skill tiers with
deck-power brackets so free players meet free players and spenders meet spenders. Everything
authoritative is server-side; anti-smurf, anti-AFK, and anti-win-trading protections are
part of the system, not an afterthought. Seasonal rewards celebrate the climb.

> 🔐 Online play is a serious commitment: authoritative backend, deterministic replay, a
> cheating model, privacy, and live operations. It is admitted only with that full plan in
> place.

---

## 🖥️ SECTION 10 — User Interface & Experience

> **MVP expression:** Clean collection, formation, battle, and reward screens. · **Future
> expression:** A codex-driven, figurine-rich, accessible experience. · **Authority:**
> `../data/schemas/ui-schema.json`

### Design principles *(the Thorne standard)*

- **Always-visible information** — HP, mana, buffs, and turn order legible at a glance.
- **Player-first choice** — layouts and pacing that respect how *you* play.
- **Quality craftsmanship** — consistent spacing, readable type, professional polish.
- **Playable, not flashy** — spectacle serves clarity, never buries it.

### Visual style

A **2.5D isometric** world paired with a **2D top-down** tactical grid — the warmth of a
board game with the readability of a chessboard. Painterly, high-saturation art for mobile
legibility; a stylized look that carries any theme skin.

### The Codex & accessibility

The **Codex of Knowledge** is the player's living manual — searchable, dynamically
unlocking, always a tap away — and the home of the card/tile views where your collection and
territory come to life. Accessibility is a first-class citizen: colourblind support,
scalable controls, audio cues, difficulty modifiers, and full localization. *Best-in-class
means everyone can play.*

---

## 🔧 SECTION 11 — Technical Integration

> **MVP expression:** Local-first Unity/C#, minimal external dependencies. · **Future
> expression:** Nakama-backed live service when an online feature demands it. · **Status:**
> Vision · **Authority:** `../data/schemas/*.json`

### Client & MVP posture

- **Engine**: Unity 2021+ LTS, C# (.NET Standard 2.1), targeting mobile and PC.
- **MVP persistence**: local-first (PlayerPrefs / local save) — no backend required to prove
  the loop.
- **Data as contract**: runtime schemas live in **`data/schemas/`**. Documentation explains
  intent; schemas, validators, and code enforce it. No numeric behavior derives from prose.

### Server & live-service *(future)*

When an online feature needs it, the intended stack is **Nakama 3.x** over PostgreSQL, with
WebSockets for real-time, a server-authoritative model, deterministic battle replay logs,
and analytics hooks. Cloud region, scaling, and infrastructure choices are deliberately left
open until a defined online feature justifies them.

> ⚠️ The codex names these technologies as *direction*, not as MVP prerequisites. The first
> release ships without them.

### The change-management contract

Every rule change flows in one direction: **design rule → `data/schemas/` → validators &
tools → implementation → tests → codex reference.** This is how we keep 100+ systems from
drifting apart again.

---

## 🎵 SECTION 12 — Sound & Polish

> **MVP expression:** Placeholder audio and essential feedback. · **Future expression:**
> Adaptive music, feedback-driven SFX, voice, and VFX polish. · **Status:** Vision

Great feel is made of a thousand small confirmations. The vision: an **adaptive music**
system that swells with the battle (The Witcher 3), **feedback-driven SFX** where every tap
and hit lands with satisfying weight (Hearthstone), tasteful VFX that celebrate rarity
without drowning the board, and accessibility-grade audio cues throughout. Premium
soundtracks and effect packs are cosmetic-only — flair you can wear, never power you can buy.

---

## 🚀 SECTION 13 — Extension Roadmap (Future-Proofing)

> **Status:** Vision · **Authority:** [`design/gameplay-modes-spec.md`](design/gameplay-modes-spec.md)

*The Universal Engine exists so the game can grow forever without a rewrite.* Each expansion
is a modular content pack — new cards, new biomes, one or two fresh mechanics — designed to
add texture without invalidating what came before.

### Themed expansions *(illustrative)*

- **Storm Rising** — Lightning and Wind elements, chain attacks and mobility, floating-island
  battlefields.
- **Iron Legion** — modern warfare texture: range, armor, and cover systems.
- **Valhalla** — Norse myth: rage mechanics, berserker risk/reward, resurrection.
- **Cyber Dominion** — sci-fi: hacking, energy shields, drone swarms.

Plus seasonal rotations (Halloween, Winter, Summer, Lunar New Year) that return yearly —
excitement without permanent loss.

### Design philosophy for growth

- **Backward compatibility** — new cards work with old decks; no forced obsolescence.
- **Intentional meta shifts** — each set answers the last, keeping the game fresh.
- **No power creep** — new cards are *different*, not strictly *better*.
- **Community content** — a long-term dream of modding and creator collaboration, cosmetic
  and PvE-safe.

---

## ⚖️ SECTION 14 — Legal, Safety & Compliance

> **Status:** Vision (activated per feature) · **Authority:** platform + legal requirements

The finished product respects its players and the law: **GDPR / CCPA / COPPA** privacy by
design, transparent IAP and odds disclosure, honest age ratings, robust community
moderation, and clear terms. Safety tooling ships *with* every social and monetization
feature, not after it. The MVP, being local-first and single-player, keeps this surface
small by design — and grows it deliberately as online and social features arrive.

---

## 🛡️ SECTION 15 — Edge Cases & Resilience

> **Status:** Vision (scoped per phase) · **Authority:** engineering design docs

A durable game plans for the unhappy paths: mid-battle disconnects, save corruption and
recovery, schema migration, exploit and dupe prevention, economic guardrails (no negative
balances, no inflation spirals), payment/refund handling, and platform quirks. The MVP
scopes this to its real surface (local save integrity, deterministic battle recovery); each
later phase expands the resilience plan alongside the systems that need it. **Chaos and
penetration testing are part of the craft, not a bolt-on.**

---

## 🗓️ SECTION 16 — Delivery Roadmap

> **Authority:** [`mvp/solo-dev-realistic-mvp.md`](mvp/solo-dev-realistic-mvp.md),
> [`mvp/mvp-scope-final.md`](mvp/mvp-scope-final.md)

We iterate toward the dream in honest, provable phases.

| Phase | Focus | Status |
| --- | --- | --- |
| **MVP** | Local-first cards · six-card, one-hero formation · deterministic 8×8 PvE · short authored campaign · save/reward loop · concise onboarding | ✅ In focus |
| **Phase 1.1** | *One* evidence-backed addition at a time — richer campaign/content, or a single progression/async experiment | 🔵 Gated |
| **Phase 2** | Exploration, economy prototype, deeper card systems, designed elemental/terrain mechanics | 🟡 Vision |
| **Phase 3+** | Social conquest — alliances, ranked PvP, territory & world maps, live-service | 🟣 Vision |

**The rule of admission**: a later system is added when its prerequisites are explicit, its
data contract exists in `data/schemas/`, its safety and support cases are understood, and
playtest or production evidence justifies the work. **Ambition is welcome; unproven scope is
not.**

### Feasibility, honestly stated

The full vision is feasible **as staged work**. A part-time, first-game solo MVP is feasible
as a *contained tactical vertical slice* — it is **not** feasible as a launch-day card
service with 100+ cards, online PvP, AFK economies, world maps, and social warfare. The
reconciliation record and readiness gates live in
[`working/archive-canon-reconciliation-jul2026.md`](working/archive-canon-reconciliation-jul2026.md).

---

## 🙏 SECTION 17 — Inspirations & Credits

*Sovereign Territories stands on the shoulders of the games that shaped us.*

### Mechanical influences

- **TCG / CCG** — Pokémon TCG, Magic: The Gathering, Hearthstone, Slay the Spire
  *(collection, deck-building, the joy of the pack).*
- **Party RPG** — Baldur's Gate, Neverwinter Nights, Diablo *(heroes with soul, gear, and
  growth).*
- **Tactical strategy** — Heroes of Might and Magic, Fire Emblem *(the grid, the formation,
  the hero-led army).*
- **Territorial conquest** — Risk, Civilization *(the map as a story).*
- **Tabletop wargaming** — Warhammer *(figurines and armies you can see).*
- **Idle / AFK** — AFK Arena, Clash of Clans *(progression that respects a life outside the
  game).*

### Thematic inspirations

Medieval fantasy, Norse mythology, historical strategy, sci-fi and modern warfare, and the
timeless clarity of great board games.

### Design creed

- **We EMBRACE** the fun — packs, heroes, tactics, exploration, a visible collection.
- **We AVOID** the tedium — grind, forced PvP, pay-to-win, and manipulative retention.

---

> ⚔️ **Sovereign Territories** — *Build the Deck. Conquer the Campaign. Level Your Heroes.*
> Crafted in the Draknare Thorne tradition: player-first, quality-obsessed, ambitious in
> vision and honest in delivery. The codex dreams the whole world; the canonical docs build
> it one proven stone at a time.
