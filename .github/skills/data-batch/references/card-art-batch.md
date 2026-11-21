# Card and art data batch workflow

## Sources

- Read [STATUS](../../../../docs/STATUS.md), the affected plan and
  [documentation ownership](../../../../docs/README.md).
- [Sovereign Dawn cards](../../../../data/cards/sovereign-dawn/) are the
  primary gameplay records; [codex-schema.json](../../../../data/schemas/codex-schema.json)
  is the card contract. Read representative current records and the exact
  schema before choosing fields, IDs, enums or output layout.
- `cardId` is the stable machine ID; `collectionNumber` is the human number.
  Link card `art.artIdentity` to the art identity's `cardId` in both
  directions. Products and decks reference IDs/pools, never copied card
  definitions. The [status summary](../../../../docs/STATUS.md) records
  current elements and rarity budgets; canonical design rules own changes.
- Use [art data guidance](../../../../data/art/README.md) for art-specific
  schemas and source components. Gameplay and art must not duplicate
  attributes.
- `data/art/_templates`, `_sets` and `_schema` are active directories, not
  archives. Only treat `_archive` as historical material when explicitly
  asked to work on it.
- Current MVP elements and eight rarity tiers come from canonical rules,
  not old six-tier, Fire/Norse or flat ATK/HP sample records.

## Batch workflow

1. Establish approved count, IDs, release/element/rarity scope, owner and
   expected output paths. Do not create a new set or invent stat curves.
2. Inspect [available launchers](../../../../bin/help.cmd) and tools for an
   existing generator/transformer. Preview the exact input/output inventory
   first.
3. Validate a small representative output before a larger batch. Reuse
   current stable `cardId` and human `collectionNumber` conventions; reject
   duplicate IDs and path collisions explicitly.
4. Write complete records without overwriting unrelated work. Products and
   decks reference IDs/pools, not copied card definitions.
5. Regenerate generated prompts through the pipeline. Preserve manual
   prompt drafts; do not edit generated outputs or create art assets.
6. Validate schema constraints, references, uniqueness and expected counts.
   Run supported checks under
   [quality gates](../../../../docs/guidelines/QUALITY-GATES.md); an
   incomplete or invalid batch is not successful generation.
7. For renames/moves, inventory exact paths, preview collisions, preserve
   sources and update references. No broad wildcard mutation of image
   libraries, no new intake or source pruning through a generic data task.

Report requested/generated/validated counts, representative records,
explicit errors and affected paths. Do not invent fictional pass counts.
Balance changes need approved design; Unity asset import requires an actual
authorized project and importer. Do not create duplicate gameplay records
in ScriptableObjects or unsupported new schema formats by example.
