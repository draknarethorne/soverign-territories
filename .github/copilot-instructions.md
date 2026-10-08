# Sovereign Territories - Copilot Instructions

Card-driven tactical strategy game (Unity/C#, planned). Tagline: "Build the Deck. Conquer the Campaign. Level Your Heroes."
The first release is **Sovereign Dawn** (cards `SD-001`..`SD-219`): a local-first PvE vertical slice. PvP, alliances,
territory maps, AFK economy and backend (Nakama) are later-phase vision, not current scope.

## Start here

- [docs/STATUS.md](../docs/STATUS.md) - current state, decisions, open questions, next work. Read before design or data work.
- [docs/README.md](../docs/README.md) - which document owns which topic.
- [data/art/README.md](../data/art/README.md) - the art/prompt pipeline.

Rules live in `docs/mvp/`, `docs/design/` (combat, deck, tutorial) and win over `docs/game-bible.md`, which is vision.
If a number or rule here disagrees with those docs, the docs win.

## Repo map

| Path | Contents |
| --- | --- |
| `data/cards/sovereign-dawn/` | Gameplay cards (the primary record of every card) |
| `data/schemas/` | Runtime JSON schemas; `codex-schema.json` is the card schema (`card-schema.json` is deprecated) |
| `data/art/` | Art identities, components, templates, art schemas (`data/art/_schema/`) |
| `data/decks`, `data/products`, `data/manifests` | Starter decks, packs, manifests (currently out of sync; see STATUS.md) |
| `prompts/` | **Generated** ComfyUI prompts; never edit by hand, regenerate |
| `workflows/` | ComfyUI workflow JSON |
| `tools/generators/gen_prompt.py` | Prompt generator |
| `data/animation/` | Video cards, motions, transitions and looks; `tools/generators/gen_animation.py` turns cards into video prompts |
| `tools/workflows/comfy_workflows.py`, `workflows/` | Builds ComfyUI workflows from prompts and syncs them to workspaces; `workflows/_templates` (ST0-ST6) are the only masters, `workflows/_curated` holds hand-tuned ones |
| `bin/*.cmd` | Quick launchers for the above; `bin/help.cmd` lists them |
| `docs/art/tutorial-art.md`, `tutorial-video.md` | How to create art and video JSON, by hand or with an AI |
| `tools/validators/` | `validate_data.py` and its mutation self-test |
| `docs/specs/` | Narrative notes for schemas (not the contracts) |
| `src/` | Reserved for Unity; not created yet |

## Data rules

- A card is defined once in `data/cards/**`; art is linked by `cardId` (card `art.artIdentity` <-> art `cardId`).
  Gameplay and art data never define the same attribute.
- `cardId` is the stable machine id; `collectionNumber` (`SD-###`) is the human number. Products reference ids or pools,
  never copies of card definitions.
- 10 elements (Darkness, Fire, Grass, Ice, Water, Light, Earth, Lightning, Wind, Poison, plus Neutral), released in stages.
  8 rarity tiers: Basic 0, Common 1, Uncommon 2, Rare 4, Epic 8, Legendary 16, Mythic 32, Transcendent 64 budget points.
- Order of change: design rule -> schema -> validator/tooling -> implementation -> tests.
- After data or art changes run `python tools/validators/validate_data.py`; after validator or schema changes also `python tools/validators/test_validate_data.py` (`--quick` for a short run).
  Commit hooks run `pre-commit` (markdownlint, validators).

## C# conventions (when Unity work starts)

- PascalCase for types/methods, camelCase for fields/locals; namespaces `SovereignTerritories.<Area>`.
- ScriptableObjects for data, no heavy logic in `Update()`, `async/await` for I/O.
- Game rules come from `docs/design/combat-calculation-spec.md` and `deck-progression-rules.md`, not from the game bible.

## Working style

- Be concise; use tables and bullets for complex topics; no emojis unless the user uses them.
- Use absolute paths with file tools. Read a file before editing it.
- Documentation: one home per fact. Move superseded files with `git mv` into the nearest `_archive` folder (the repo-wide
  archive convention: `docs/_archive`, `data/_archive`, `prompts/_archive`).
- **Ignore every `_archive` folder** when reading documentation, data, or prompts, and do not cite or link to it,
  unless the user explicitly asks for archived material. Folders like `data/art/_templates`, `_sets`, `_schema` are active.
- Do not make major design decisions without user approval, and do not commit code that fails the validators.
- Do not create art assets; describe them for the artist or generate prompts through the pipeline.
