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
