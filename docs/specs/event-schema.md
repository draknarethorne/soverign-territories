# Event Schema — challenges and modes

This document explains the event schema for challenges, tournaments, and gameplay modes.

## Key Fields

- `eventId`, `eventType` — Unique ID and type (dailyChallenge, allianceEvent, etc.).
- `name`, `description` — Display info.
- `startTime`, `endTime` — Duration.
- `requirements` — Objectives with progress tracking.
- `rewards` — Prizes for completion.
- `participants`, `leaderboard` — For competitive events.
- `status` — Upcoming, active, completed.

## Mechanics

- Daily/Weekly: Reset at midnight; streaks preserved by VIP.
- Tournaments: PvP brackets with themed restrictions.
- Expeditions: Board-based mini-games with random events.

## Engine Integration

- Server schedules events; tracks progress.
- Client shows UI for participation; real-time updates.
- Events trigger notifications and rewards distribution.