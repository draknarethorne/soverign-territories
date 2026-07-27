# Implementation Roadmap and Phases

This document outlines a phased approach for research, prototyping, and implementation.

## Phase 0 — Design & Specs (Now)
- Finalize `game-bible.md` as the product book.
- Extract authoritative schemas into `docs/specs/*` (card, map, player, alliance, ability).
- Define minimal runnable vertical slice (MVP) scope and success metrics.

## Phase 1 — Prototype (3-6 weeks)
- Implement server-authoritative combat simulation (turn-based engine) with headless bots for testing.
- Implement client prototype in Unity: map rendering, Codex UI, basic deck placement.
- Create automated balance tests and replay logging.

## Phase 2 — Alpha (6-12 weeks)
- Add persistence (Nakama), matchmaking, and basic social features (friends, alliances).
- Iterate on economy, VIP flows, and auction house prototypes.
- Start limited closed alpha with telemetry and retention hooks.

## Phase 3 — Beta (3-6 months)
- Full feature set for core gameplay modes (Saga, Territorial Conquest, Alliance Events).
- Polish UX, accessibility features, and localization.
- Marketing tests, store setups, and broader stress testing.

## Phase 4 — Launch & Live Ops
- Launch on targeted platforms; monitor economy and balance.
- Post-launch live ops, seasonal content, and feature roadmaps.

## Research & Risk Mitigation
- Balance automation: run large-scale simulations before card releases.
- Anti-cheat: staged rollouts with strict server-side validation.
- Scalability: early architecture review (sharding, caching) and capacity planning.

## Deliverables
- `docs/specs/*.json` authoritative schemas
- Minimal server simulation and client prototype
- Telemetry dashboards and automated playtest harness
