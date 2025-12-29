Specs directory

This folder contains machine-readable JSON Schemas and companion human-readable notes for engineers.

Files:
- card-schema.json — authoritative JSON Schema for cards.
- map-schema.json — authoritative JSON Schema for maps and tiles.
- player-schema.json — authoritative JSON Schema for player/account records.
- alliance-schema.json — authoritative JSON Schema for alliances.
- ability-schema.json — authoritative JSON Schema for ability/effect definitions.

Purpose and guidance
- JSON Schemas are structural and used for validation, codegen (TypeScript, C#), and automated CI checks.
- Narrative details, usage examples, edge-cases, and implementation notes are in the `*.md` files alongside each schema.

CI and validation
- Recommended validation: use `ajv` or `ajv-cli` in CI to validate example payloads and ensure schema correctness.

Versioning
- Each schema contains `schemaVersion`. When changing schema, increment and provide migration notes in the corresponding `*.md`.

How to use
1. Read the `*.md` companion document for intent and examples.
2. Use the `*.json` file for codegen and runtime validation.
3. Add breaking changes behind feature flags when possible; update `schemaVersion` and migration docs.
