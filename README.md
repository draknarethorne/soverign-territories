# Sovereign Territories

**Tagline**: "Build the Deck. Rule the Map. Automate the Empire."

A hybrid strategy game merging:
- **Risk-style territorial conquest** (global map, alliance wars)
- **Pokemon TCG deck-building** (collect cards, build decks, rarity progression)
- **Heroes of Might and Magic tactical combat** (hero-led armies, turn-based battles)
- **AFK progression** (place economy cards on tiles for passive income - Phase 2)

---

## Quick Links

**Core Documentation**:
- [game-bible.md](docs/game-bible.md) - Master design document (6,700+ lines, single source of truth)
- [mvp-scope-final.md](docs/mvp-scope-final.md) - 8-week implementation roadmap
- [tutorial-flow.md](docs/tutorial-flow.md) - Step-by-step player onboarding (28 steps, 0-60 minutes)

**Implementation Specs**:
- [economy-system.md](docs/economy-system.md) - Currency earning/spending (MVP Gold/Gems/Energy, Phase 2 Food/Lumber/Ore)
- [combat-calculation-spec.md](docs/combat-calculation-spec.md) - Battle formulas (MVP Attack/Defense, Phase 2 RPG stats)
- [map-tier-progression.md](docs/map-tier-progression.md) - Map hierarchy (World → Territory → Realm → Battle)
- [rpg-systems-spec.md](docs/rpg-systems-spec.md) - Post-MVP RPG mechanics (Health/Mana/Stamina, Consumables, Shops)
- [terminology-guide.md](docs/terminology-guide.md) - Canonical naming reference (map tiers, player title "Sovereign")

**Planning**:
- [bible-reorganization-plan.md](docs/bible-reorganization-plan.md) - Documentation structure and scope decisions
- [roadmap.md](docs/plan/roadmap.md) - High-level development phases (Prototype → Alpha → Beta → Launch)

---

## Project Status

**Current Phase**: Design & Specs (Phase 0)  
**MVP Target**: 8 weeks (Week 1-2: Card system, Week 3-4: Combat, Week 5-6: Realm Map, Week 7-8: Progression/Stores)  
**Recent Updates** (Dec 2024):
- ✅ Created 6 specification documents (economy, combat, MVP scope, RPG systems, map progression, terminology)
- ✅ Updated game-bible.md with Phase 2/3 disclaimers (Food/Lumber/Ore deferred, Arena Tokens Phase 3)
- ✅ Global map terminology update (County→Realm, State→Territory, Global→World)
- ✅ Tutorial updated for MVP scope (treasure nodes instead of economy deployment)

---

## Tech Stack

- **Engine**: Unity 2021+ LTS
- **Language**: C# (.NET Standard 2.1)
- **Server**: Nakama 3.x (PostgreSQL, WebSockets)
- **Platforms**: Mobile (iOS/Android) + PC (Steam)
- **Art Style**: 2.5D isometric maps, 2D tactical battles (stylized painterly)

---

## MVP Scope (8 Weeks)

**Must Have**:
- Card system (100 cards, 6 rarities: Common → Mythic)
- Pack opening (Standard Packs 1,000 Gold, Element Boosters 1,500 Gold)
- Deck building (10-50 cards, rarity budget prevents all-Legendary decks)
- Battle system (8×8 tactical grid, Attack/Defense one-hit removal)
- Realm Map (20-40 Locations, HoMM-style exploration, 5-10 treasure nodes)
- Tutorial (28 steps, 30-60 minutes, 31 cards at completion)
- Progression (Player Level 1-30, deck size 10-50 cards)
- Currencies (Gold/Gems/Energy only)
- Stores (Pack Store only, Gold purchases)

**Won't Have** (Post-MVP):
- **Phase 2** (Month 2-3): Food/Lumber/Ore economy, Resource Store, Economy deployment, Alliance system, Daily/Weekly quests, RPG Card Stats (Health/Mana/Stamina), Consumables, RPG Shops
- **Phase 3** (Month 4-6): Territory Map, World Map, Occupation mechanics, PvP Arena, Elemental interactions, Status effects, Equipment System, Sockets

---

## Getting Started

1. **Read the Design**: Start with [game-bible.md](docs/game-bible.md) Sections 1-2 (Overview, Card System)
2. **Understand MVP**: Review [mvp-scope-final.md](docs/mvp-scope-final.md) for 8-week roadmap
3. **Check Tutorial**: Walk through [tutorial-flow.md](docs/tutorial-flow.md) for player onboarding flow
4. **Review Specs**: Consult implementation specs for exact formulas and earning rates

---

## Contributing

This is a solo design project. If interested in collaboration, contact [project owner].

---

**Last Updated**: December 29, 2024
