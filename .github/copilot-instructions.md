# Sovereign Territories - Copilot Instructions

Card-driven tactical strategy game (Unity/C#, planned). Tagline: "Build the Deck. Conquer the Campaign. Level Your Heroes."
The first release is **Sovereign Dawn** (cards `SD-001`..`SD-219`): a local-first PvE vertical slice. PvP, alliances,
territory maps, AFK economy and backend (Nakama) are later-phase vision, not current scope.

## Start here

- [docs/STATUS.md](../docs/STATUS.md) - current state, decisions, open questions, next work. Read before design or data work.
- [docs/README.md](../docs/README.md) - which document owns which topic.
- [docs/plans/README.md](../docs/plans/README.md) - canonical planning process, now/next/holding order and per-scope owners. Read affected plans and their gates; holding is not completion.
- [docs/todo.md](../docs/todo.md) - generated execution window from active plans' `Queue focus` (all open tasks if absent), with linked deferred work. Check it before suggesting "what next"; never edit generated tasks by hand.
- [docs/recap/README.md](../docs/recap/README.md) - pinned current resume and feedback handoffs, not simply the newest dated reflection.
- [docs/archive-guide.md](../docs/archive-guide.md) - physical topic/status/month filing and matching indexes; archive does not mean implemented or disposable.
- [docs/QUALITY-GATES.md](../docs/QUALITY-GATES.md) - routine versus explicit targeted/deep validation; use supported launchers.
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
| `prompts/` | Regenerate generated ComfyUI outputs; `prompts/_edit/` holds preserved manual migration sources, not disposable generated files |
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
- 10 elements (Darkness, Fire, Grass, Ice, Water, Light, Earth, Lightning, Wind, Poison, plus Neutral), released in stages:
  the MVP is Darkness and Light only; the next cycle is Fire, Grass, Water and Earth (decided Oct 9, 2026).
  8 rarity tiers: Basic 0, Common 1, Uncommon 2, Rare 4, Epic 8, Legendary 16, Mythic 32, Transcendent 64 budget points.
- Order of change: design rule -> schema -> validator/tooling -> implementation -> tests.
- After data or art changes run `cmd /c bin\check.cmd` for routine hygiene/data validity.
  For schema/validator changes also run `cmd /c bin\validate.cmd --isolated --quick`; expand when the change requires it.
  Run relevant targeted tests separately; routine hooks/CI are not full regression acceptance. Commands and scope live in the quality contract.

## C# conventions (when Unity work starts)

- PascalCase for types/methods, camelCase for fields/locals; namespaces `SovereignTerritories.<Area>`.
- ScriptableObjects for data, no heavy logic in `Update()`, `async/await` for I/O.
- Game rules come from `docs/design/combat-calculation-spec.md` and `deck-progression-rules.md`, not from the game bible.

## Working style

- Be concise; use tables and bullets for complex topics; no emojis unless the user uses them.
- Use absolute paths with file tools. Read a file before editing it.
- Documentation: one home per fact. Follow the archive guide: tracked history uses `git mv` into the appropriate
  topic/status/month group; update actual folders, indexes, incoming links and generated readers together.
  Preserve historical prose and fenced raw sources; fix link destinations for moves. Ignored feedback moves require
  non-overwriting byte/hash verification. Filing a source does not close its implementation tasks.
- **Ignore every `_archive` folder** for ordinary work unless the user explicitly requests historical material or
  scoped archive maintenance. Navigation indexes may link to history as history, never current authority.
  Folders like `data/art/_templates`, `_sets`, `_schema` are active, not archives.
- Do not make major design decisions without user approval, and do not commit code that fails the validators.
- **Plans:** accept raw notes in `feedback/<topic>.md` (git-ignored) or directly in chat. When agreed, incorporate them into the owning existing plan or `docs/plans/YYYY-MM-DD-<slug>.md`
  with a `**Status:**` line and a row in the table of `docs/plans/README.md` (STATUS.md does not list plans), ask open decisions one at a
  time, and keep the user's own words at the end of the plan, word for word. Every open step is a checkbox with a tag,
  `- [ ] **P1 you** T3 ...` (priority P1 to P3; owner `you` = needs the user's hands or decision, `ai`, or `either`): `bin\todo.cmd`
  turns the tags into `docs/todo.md`. Use `holding` with a reason/resume gate for deferred scope, and `Queue focus`
  for an active plan's current open task IDs; update focus when tasks close. A finished plan gets `**Status:** done`
  and a `Result`, and is `git mv`ed into its archive group with no open boxes left. Superseded plans use `dropped`
  and explicit task/context transfers, not completion claims. Preserve raw feedback word for word at the end of its
  primary plan, including relevant chat messages, and record coverage of every request. Re-read each source immediately
  before individually filing it into the feedback archive topic folder, after preservation/coverage verification.
  Never bulk-clear `feedback/`; legacy raw notes in `tmp/` have the same protection.
- **Execution lanes:** keep one primary milestone; bounded independent read-only analysis and one tested quality
  improvement may accompany it under the plan index's gates. Analysis does not authorize early mutation, a new full
  intake, threshold/recipe changes or heavy competing I/O. Reuse shared run evidence across acceptance owners,
  rather than rerunning the same operation for each plan. Merge/split only with explicit ownership transfers.
- **Specialized agents:** follow the [shared agent contract](agents/AGENT-SELECTION-GUIDE.md#shared-working-contract).
  Verify actual project/tool/model availability before use; a role cannot authorize future-phase Unity/Nakama work,
  change the source of truth, silently substitute a model, or bypass validation/publication approval.
- **The day's hygiene (before a commit and push at the end of a working day):** feedback files, chat requests and legacy tmp notes are accounted for
  in owning plans; unresolved/unincorporated notes stay safely in place (neither directory must be empty); every plan has a status and tagged boxes; finished plans are
  archived; `bin\todo.cmd` was run; STATUS.md has the day's decisions; a recap is written in `docs/recap/`; validators, tests and
  markdownlint pass. The checklist is in `docs/plans/README.md`.
- **Large days:** split the work into steps and say what you are doing and why; run long jobs so that they can be checked (a log, a count,
  a preview first) and verify each step before building on it; have helpers (background agents) read, audit or summarise in parallel
  while you work, and give them a bounded read-only task; never leave half-finished state (write files whole, swap them in, keep originals);
  when a process seems stuck check whether it is suspended before assuming a bug. Reflect at the end of the day (see the recap).
- Do not create art assets; describe them for the artist or generate prompts through the pipeline.
- **Scratch output:** write disposable logs, session files, test output and intermediate artifacts under the repository's
  git-ignored `tmp\` (for example `tmp\session-logs\<date>\`), using an explicitly resolved absolute path when invoking
  tools or helpers. Never create repository-root `files\` or `session files\` directories; do not confuse those names
  with an external session folder. Scripts, tests and launchers must follow the same rule for default scratch paths.
  Another output area is allowed only when it is explicitly designated and verified git-ignored before writing
  (`git check-ignore`); existing ignored `reports\` is for generated review reports, not a new scratch convention.
  Keep durable library receipts/recovery evidence in their documented library locations, not disposable `tmp\`.
  Never treat legacy raw feedback in `tmp\` as disposable; its preservation rules above still apply.

## Commands: run the bin launchers, and make new ones

- Run the `bin\*.cmd` launchers (`cmd /c bin\name.cmd ...`) instead of calling `python tools\...` by hand, so that you and the user run the same
  commands with the same defaults and the launchers stay tested. `bin\help.cmd` lists them. Changing a launcher or the tool behind it: run the
  launcher itself (its preview first), then the tests.
- Before writing a script, a new subcommand or a long shell sequence, read `bin\help.cmd` and `bin\`: the thing may exist (for example
  `sync-inputs.cmd` copies workflow input images; a duplicate `inputs sync` was written and removed on Oct 12).
- A routine that needs several commands or arguments the user would have to remember becomes a launcher: a thin `.cmd` that calls one Python tool,
  previews with `--dry-run`, has a read-only `--check`, repeats safely, and is listed in `bin\help.cmd` and `bin\menu.cmd`, documented, and tested.
- Photo library routine: drop new photos into `Various\gallery`, run `bin\library.cmd` (originals, duplicates, crop, likeness, scaled copies, headshots,
  frames, inputs); `--retry-junk` sends `_junk` back through it, `likeness pullback` re-sorts prospects. The runbook is `docs/art/original-photos.md`. `bin\library-check.cmd` says whether anything is waiting; `bin\library-preview.cmd` previews every step.
