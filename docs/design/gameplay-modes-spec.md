# Gameplay Modes and Phase Gates

**Last updated:** July 2026
**Status:** Phased mode inventory; only the MVP mode is approved for baseline implementation.

## MVP: linear tactical campaign

The sole MVP mode is a local-first, single-player sequence of authored tactical PvE
encounters. It uses the one-hero, six-card formation and deterministic combat defined in
the canonical MVP, deck, and combat documents.

The campaign validates collection, formation, combat, rewards, saving, and onboarding. It
does not require a Realm map, daily board, auto-battle, procedural spawns, multiplayer,
or an event calendar.

## Later candidates

| Mode | Earliest phase | Reason to defer |
| --- | --- | --- |
| Expanded campaign / challenge encounters | 1.1 | Add only when the initial campaign shows which content players enjoy. |
| Fusion or crafting progression | 1.1 | Requires an acquisition economy and balance data. |
| Async challenge / PvP prototype | 1.1+ | Requires abuse prevention, privacy, and a backend authority model. |
| Realm exploration | 2+ | Requires navigation, encounter generation, persistence, and content density. |
| Economy deployment and AFK progression | 2+ | Requires a complete resource economy and anti-obligation safeguards. |
| Ranked PvP, alliances, trade, territory wars | 3+ | Requires moderation, operations, anti-cheat, and fairness protections. |
| Seasonal world maps and expeditions | 3+ | Requires sustainable content and live-service capacity. |

## Mode admission rule

A later mode is not added because it is documented. It is added only when its
prerequisites are explicit, its data contract exists under `data/schemas/`, its abuse and
support cases are understood, and playtest or production evidence justifies the work.
