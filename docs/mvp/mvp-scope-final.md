# MVP Scope — Dependency and Acceptance Plan

**Last updated:** July 2026
**Status:** Supporting implementation plan; `solo-dev-realistic-mvp.md` wins on scope and schedule.

## Baseline contract

The MVP is a local-first vertical slice: a small collection, a legal one-hero formation, deterministic 8×8 PvE combat, a short linear campaign, and basic rewards/progress. It is not a map-conquest, live-service, or multiplayer release.

## Build order

| Order | Dependency | Deliverable | Acceptance check |
| ---: | --- | --- | --- |
| 1 | Data subset | 18–30 validated card definitions and one starter collection | Validation passes; the starter collection can make a legal six-card formation. |
| 2 | Local profile | Save/load of owned cards, selected formation, campaign progress, and earned currency | Restart preserves state without duplication or loss. |
| 3 | Collection and formation | Inspect cards; select six cards; enforce exactly one hero and copy/budget rules | Invalid formations explain why they cannot start. |
| 4 | Battle core | 8×8 board, move, basic attack, authored Mana ability, win/loss detection | Same input state produces the same result; minimum damage is one. |
| 5 | Encounter content | 8–12 authored PvE encounters and a boss | Difficulty progression is playable with starter cards. |
| 6 | Rewards and campaign | Stage select, unlock sequence, simple rewards and pack/reward grant | Completing a stage saves progress and advances the next stage. |
| 7 | Onboarding | Brief learn-by-doing path through collection, formation, and first battle | A new tester reaches the first victory without assistance. |
| 8 | Playtest pass | Defect fixes and balance notes | No blocker in start, battle, reward, or save loop. |

## MVP rules

- One active formation has six cards and exactly one hero.
- The campaign is linear stage selection; no movement points, fog, exploration, or map occupation are required.
- All MVP battles are PvE and local-first.
- Damage and stat behavior are defined in `docs/design/combat-calculation-spec.md`.
- Deck limits, rarity costs, and copy limits are defined in `docs/design/deck-progression-rules.md`.
- Runtime schemas and validation contracts live in `data/schemas/`.

## Deliberate exclusions

| Later system | Earliest phase | Admission condition |
| --- | --- | --- |
| Fusion, equipment, persistent health, Temple | 1.1 | Baseline battle/reward loop is stable and playtest need is clear. |
| Crafting or async challenge | 1.1 | Data model, reward economy, and abuse model are designed. |
| Online PvP, accounts, matchmaking | 1.1+ | Backend plan, privacy/security work, and deterministic replay requirements are validated. |
| Economy deployment, exploration, territory systems | 2+ | Core loop retention and content pipeline justify strategic-map investment. |
| Alliances, trade, wars, seasonal world maps | 3+ | Live operations, moderation, and server capacity are funded and designed. |

## Non-goals for the first vertical slice

- 100-card content set, 60–80 campaign battles, or a 28-step/30-minute tutorial;
- auto-battle, advanced tactics, procedural encounters, daily boards, boss loot tables;
- stores, IAP, battle pass, VIP, energy monetization, or timed retention mechanics;
- hex-grid maps, terrain, multi-hero armies, resource nodes, and AFK production.

## Handoff checklist

Before implementation work starts, confirm:

- [ ] The chosen card data subset validates against `data/schemas/`.
- [ ] The starter collection and every encounter have deterministic expected results.
- [ ] UI flows use the one-hero/six-card baseline.
- [ ] Each task cites the authoritative design or schema source.
- [ ] Playtest events and feedback capture are defined without requiring a backend.

## Completion condition

MVP scope is complete when a fresh local profile can obtain the starter collection, create a legal formation, complete the short campaign loop, receive rewards, save, reload, and repeat without a blocker. Passing this condition authorizes a playtest—not automatic expansion into Phase 1.1.
