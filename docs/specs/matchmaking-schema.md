# Matchmaking Schema — Elo and lobbies

This document explains the matchmaking schema for fair PvP pairing.

## Key Fields

- `playerId`, `eloRating` — Rating for balancing.
- `eloHistory` — Change log for transparency.
- `matchmakingPreferences` — Mode, wait time, region.
- `allianceId` — For guild matches.
- `banStatus` — Anti-cheat enforcement.

## Mechanics

- Elo adjusts post-match.
- Preferences filter opponents.
- Bans for violations.

## Engine Integration

- Nakama handles queuing; server authoritative.
- Events: Match results update ratings.
