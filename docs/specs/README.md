# Specs directory

This folder contains machine-readable JSON Schemas and companion human-readable notes for engineers.

Files:

- card-schema.json — authoritative JSON Schema for cards.
- card-schema.md — narrative notes for card schema.
- map-schema.json — authoritative JSON Schema for maps and tiles.
- map-schema.md — narrative notes for map schema.
- player-schema.json — authoritative JSON Schema for player/account records.
- player-schema.md — narrative notes for player schema.
- alliance-schema.json — authoritative JSON Schema for alliances.
- alliance-schema.md — narrative notes for alliance schema.
- ability-schema.json — authoritative JSON Schema for ability/effect definitions.
- ability-schema.md — narrative notes for ability schema.
- algorithms.md — core algorithms for pathfinding, AoE, combat.
- effect-types.md — effect categories, resolution order, stacking.
- resource-schema.json — authoritative JSON Schema for currencies and resources.
- resource-schema.md — narrative notes for resource schema.
- trade-schema.json — authoritative JSON Schema for trades and auctions.
- trade-schema.md — narrative notes for trade schema.
- event-schema.json — authoritative JSON Schema for events and challenges.
- event-schema.md — narrative notes for event schema.
- progression-schema.json — authoritative JSON Schema for leveling and unlocks.
- progression-schema.md — narrative notes for progression schema.
- deck-schema.json — authoritative JSON Schema for decks.
- deck-schema.md — narrative notes for deck schema.
- deployment-schema.json — authoritative JSON Schema for tile deployments.
- deployment-schema.md — narrative notes for deployment schema.
- pack-schema.json — authoritative JSON Schema for card packs.
- pack-schema.md — narrative notes for pack schema.
- tactic-schema.json — authoritative JSON Schema for AI tactics.
- tactic-schema.md — narrative notes for tactic schema.
- equipment-schema.json — authoritative JSON Schema for hero equipment.
- equipment-schema.md — narrative notes for equipment schema.
- theme-schema.json — authoritative JSON Schema for card themes.
- theme-schema.md — narrative notes for theme schema.
- matchmaking-schema.json — authoritative JSON Schema for Elo matchmaking.
- matchmaking-schema.md — narrative notes for matchmaking schema.
- audio-schema.json — authoritative JSON Schema for audio assets and music.
- audio-schema.md — narrative notes for audio schema.
- session-schema.json — authoritative JSON Schema for player sessions and analytics.
- session-schema.md — narrative notes for session schema.
- store-schema.json — authoritative JSON Schema for IAP products and monetization.
- store-schema.md — narrative notes for store schema.

Purpose and guidance

- JSON Schemas are structural and used for validation, codegen (TypeScript, C#), and automated CI checks.
- Narrative details, usage examples, edge-cases, and implementation notes are in the `*.md` files alongside each schema.

CI and validation

- GitHub Actions workflow validates schemas and generates TypeScript types on changes.
- Use `ajv` or `ajv-cli` locally to validate payloads.

Versioning

- Each schema contains `schemaVersion`. When changing schema, increment and provide migration notes in the corresponding `*.md`.

How to use

1. Read the `*.md` companion document for intent and examples.
2. Use the `*.json` file for codegen and runtime validation.
3. Add breaking changes behind feature flags when possible; update `schemaVersion` and migration docs.

Schema change protocol (required)

When changing gameplay behavior that touches data contracts, follow this order:

1. Update the canonical design rule in `docs/design/*.md`.
2. Update the corresponding schema in `docs/specs/*.json`.
3. Update companion notes in `docs/specs/*.md` (examples, migration notes).
4. Update affected generators/importers/validators (`tools/` and `scripts/`).
5. Re-run local validation (`ajv` / CI checks) before merging.

Guardrails

- Do not ship behavior that depends on prose in `docs/game-bible.md` alone.
- Runtime and tooling logic must derive from schema + canonical design docs.
- Any breaking schema update must include migration guidance in the companion `*.md`.
