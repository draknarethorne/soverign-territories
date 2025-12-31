# Progression Schema — leveling and unlocks

This document explains the progression schema for player growth, castle upgrades, and VIP systems.

## Key Fields

- `level`, `xp`, `xpToNext` — Player leveling; XP from battles/quests.
- `castleLevel`, `castleXp`, `castleXpToNext` — Castle hub leveling; unlocks slots/buffs.
- `unlocks` — Features unlocked (deck size, tactics).
- `vipLevel`, `vipXp`, `vipPerks` — VIP from gem spending; perks like extra stamina.
- `achievements` — Progress tracking for milestones.

## Mechanics

- XP Formula: Base XP per action + multipliers for difficulty/streaks.
- Castle Unlocks: Level 10 enables PvP; higher levels increase limits.
- VIP: Levels unlock perks; preserves login streaks.

## Engine Integration

- Server calculates XP; validates unlocks.
- Client shows progress bars; animations for level-ups.
- Events: Level-up triggers notifications and rewards.