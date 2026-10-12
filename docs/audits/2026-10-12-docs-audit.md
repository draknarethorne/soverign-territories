# Documentation audit, Oct 12, 2026

Scope: every `*.md` under `docs/` (not `_archive`), plus `workflows/README.md`, `data/art/README.md`, `.github/copilot-instructions.md`, compared with `tools/`, `data/`, `bin/*.cmd` and `workflows/workspaces.json`.
Method: link and path checks over all docs, every `bin\*.cmd` name and `--flag` in the docs looked up in `bin/` and `tools/`, `codex_drift.py --check`, `validate_data.py` (exit 0 before and after), then reading the plans, art guides, MVP and design docs against each other.
Not touched on purpose (another worker is changing them): `docs/STATUS.md`, `docs/art/likeness.md`, `docs/art/original-photos.md`, `tools/art/*`. Issues in them are listed below as findings only.

## Summary

- The art and photo-library docs (`prime-flows.md`, `original-photos.md`, the `likeness.md` commands, `workflows/README.md`) agree with the code: every `.cmd` name exists, every flag exists (`--flow`, `--prime`, `--bare`, `--shots`, `--all-renders`, `--check`, `--archive-old`, `--no-frames`, ...), and the frame threshold (0.14), headshot limits (60 px, 2.5 face heights) and `library` step order match `originals.py` and `library_sync.py`. `codex_drift.py --check` says the roster pages match the data.
- The real conflicts are older: the MVP and design documents still carry the July 2026 text and never absorbed the Oct 9 decision (Darkness and Light only), the draft notes in `docs/specs/` describe a card model that no longer exists, two art docs point at folders archived on Oct 4, and `STATUS.md` has three stale statements.
- Fixed 7 groups of obvious issues (see "Minor issues fixed"). The table below is what needs your decision or the other worker's attention; the numbered details follow it.

## Major issues

| # | File | What conflicts | Right source | Proposed action | Your decision |
| ---: | --- | --- | --- | --- | --- |
| 1 | `mvp/*.md`, `design/*.md` (July 2026 text) | No mention of the Oct 9 MVP element set; still 18 to 30 cards and a 20-card starter | Oct 9 decision for elements; MVP docs for counts until decided | State the elements; decide the card and starter counts | yes |
| 2 | `design/deck-progression-rules.md`, `game-bible.md` | "Transcendent is the seventh tier" against 8 tiers in the schema | `codex-schema.json` | Reword to "eighth tier, seventh collectible" | no (wording), approve canon edit |
| 3 | `specs/card-schema.md` | Describes a card model the schema does not have | `codex-schema.json` | Rewrite from the schema or mark as draft | no |
| 4 | `STATUS.md` (not edited) | Date, `_org` folders, one renamed file | code and `original-photos.md` | STATUS owner fixes three lines | no |
| 5 | `workspaces.json`, `STATUS.md` against the disk and 3 docs | `Sovereign` against `Soverign` work folder | the config (intent) | Rename the folder, then sweep the docs | yes |
| 6 | `art/comfyui-art-pipeline.md`, `art/template-analysis-findings.md` | `workflows/Experimental/` and `workflows/Templates/` no longer exist | `workflows/README.md` | Mark as removed or historical, or archive | yes |
| 7 | `plans/2026-10-09-finals-and-mvp.md` | Depends on git-ignored `tmp/2026-10-09-cli-review.md` | `plans/README.md` rule | Copy the proposal table into the plan | yes |
| 8 | `bin\help.cmd`, `bin\likeness.cmd` | Seven likeness sub-commands missing from the launcher help | `likeness.py --help` | Add them after the likeness edit ends | no |
| 9 | several (rarity table, elements, library routine) | Same fact in several documents | one owner each | Keep one copy and link | no |

### Details

1. **MVP docs.** `solo-dev-realistic-mvp.md`, `mvp-scope-final.md`, `tutorial-flow.md` and the `design/` docs say "Last updated July 2026" and never mention that the MVP is Darkness and Light only (plan 10-09 D4, "Decisions made" in STATUS, `game-bible.md` line 792, `sovereign_dawn_codex.md`).
   They still say "18-30 playable cards" and "one prevalidated 20-card starter collection", but only 4 Darkness and 4 Light cards exist (STATUS next work G1). The Oct 9 plan keeps an unticked box "mvp docs checked, nothing to change". `docs/README.md` called the element choice open (fixed).
   Needed: one sentence in `solo-dev-realistic-mvp.md` and your answer on whether 18-30 cards and the 20-card, 40-point starter hold for two elements plus Neutral (STATUS G1, D3, D2).
2. **Tier count.** `deck-progression-rules.md` ("the seventh, rarest tier") and `game-bible.md` 2.1 and 2.9 ("seven tiers", "the seventh, apex rarity") against `codex-schema.json`, STATUS, copilot-instructions and `ideation_lists.md`: 8 tiers, Basic 0 to Transcendent 64, Transcendent numbered 7. Both are true only if Basic is not counted. This is STATUS next work D2, so do it in that change.
3. **`specs/card-schema.md`.** `specs/README.md` calls it the one narrative with live data, but it requires `id`, `level`, `schemaVersion`, uses lower-case `type` and a string `rarity`, `stats.hp`, `speed`, `stackSize`, `attackType`, `moveType`, `production` and server-owned instances.
   `codex-schema.json` has `additionalProperties: false`, requires `cardId`, `collectionNumber`, `series`, `name`, `type` (Hero, Unit, ...), `element`, `rarity {tier, stars, points}`, and its stats are `health`, `mana`, `attack`, `defense`, `moveRange`, `attackRange`, `flying`. The example in the doc would fail validation.
4. **`STATUS.md`.** (a) Header "Updated: 2026-10-08" while it lists work of Oct 9 to 12. (b) Original photos row says copies of removed originals "move to the `_org` folders"; since Oct 11 they go to `<work>\_archive\<same path>\gallery_944x1104_org` (`original-photos.md`, `originals.py`). (c) Line 131 cites `elder_dragons_.md`, now `codex/heroes/elder_dragons_details.md`.
5. **Work-folder spelling.** `workflows/workspaces.json` has `paths.workRoot` = `B:/Sovereign Territories` and STATUS line 93 says Sovereign. The folder on disk is `B:\Soverign Territories`, and `original-photos.md` line 7, `likeness-reorg-2026-10-09.md` and `likeness-reorg-2026-10-10.md` say Soverign. `comfy_workflows.work_root()` silently falls back to the misspelled folder "until it is renamed"; `B:\Sovereign Territories` does not exist.
6. **Removed folders.** `comfyui-art-pipeline.md` (lines 104, 273, 332, 340: "benchmark harness assembled in `workflows/Experimental/`", "downloaded `workflows/Templates`") and `template-analysis-findings.md` ("23 templates in `workflows/Templates/`"). Both folders left the repo in the Oct 4 layout change (commit `9a289075a`); `workflows/` now has `_templates` (ST0 to ST6), `_curated`, `_candidates`, `_shots`, `_test`, `_archive`.
7. **Plan depends on tmp.** Plan 10-09 (D7, Phase 6) points to `tmp/2026-10-09-cli-review.md`, but `plans/README.md` says nothing depends on `tmp/` and copilot-instructions says a tmp draft is not deleted until its text is copied into the plan. Items 6.3b and 6.5 are still open and rely on that table.
8. **Launcher help.** `likeness.py` has 28 sub-commands. `bin\help.cmd` and the comment in `bin\likeness.cmd` omit `scan`, `calibrate`, `artists`, `crop`, `crosscheck`, `rematch`, `photos`, all documented in `likeness.md`. Copilot-instructions say new launcher routines are listed in `bin\help.cmd`.
9. **Same fact, several homes.** The rarity table (`deck-progression-rules.md`, `ideation_lists.md`, STATUS, copilot-instructions), the 10-element list (6 files) and the library routine steps (`original-photos.md`, `likeness.md`, `bin\library.cmd`, `library_sync.py`, plan 10-12 L5; `_archive` and `_junk` are also described twice). They agree today but will drift.
   Owners: rarity `deck-progression-rules.md` and `codex-schema.json`; elements `codex-schema.json`; library routine `original-photos.md` ("The routine"). The README row for original photos now names `bin\library.cmd`.

## Minor issues fixed

| File | Fix |
| --- | --- |
| `docs/README.md` | MVP row and "Vision vs. MVP" note use the Oct 9 decision instead of "3-4 elements, open"; "Face likeness" row names the people index, the Oct 10 report and the top-level `Various` (was `Prospects\Various`); "Original photos" row names `bin\library.cmd`; one line added for this audit |
| `workflows/README.md` | Quick reference used `deploy ... --staged`, which line 22 of the same page and `comfy_workflows.py` say is replaced: now `--include staged`. Template path `heroes/*.txt` is now `heroes/<stage>/*.txt` (split by stage on Oct 11) |
| `art/prompt-pattern.md` | Dead link `_templates/heroes/scene-human.txt` replaced by the six real scene templates; four links into `prompts/_archive` made plain names (docs must not link to `_archive`); the `Distinguishing marks:` slot in `_TEMPLATE_Pose` (neither exists) now points to the `distinguishingMarks` field in `data/art/README.md` |
| `art/comfyui-art-pipeline.md`, `art/tutorial-art.md` | Template paths `_templates/heroes/*.txt` and `<archetype>/*.txt` now show the stage folders |
| `specs/economy-node-schema.md`, `specs/trainer-deck-schema.md` | Seven dead links to `*-schema.json` now point to `../../data/schemas/` |
| `plans/2026-10-10-names-ingest-headshots.md` | Source link to the git-ignored `tmp/likeness_brain_dump.md` (dead in a clone) replaced by a pointer to the verbatim copy at the end of the plan |
| `QUALITY-GATES.md` | Lists the two hooks that were missing (workflow tool tests, generator tests); "Phase 2: add release checklist and change-management docs" now says keep them current (they exist) |

## Smaller findings not fixed (judgement, or in files that must not be touched now)

- `docs/README.md` links to `_archive/README.md` ("Archive index") although its own `_archive` rule says not to link to archives. Keep the one index link or drop it: your call.
- `specs/trainer-deck-schema.md` ("Step 6") and `specs/economy-node-schema.md` ("Step 27") cite steps of `tutorial-flow.md`, which now has 8 steps (the 28-step tutorial was retired). Drafts, left as they are.
- `CHANGE-MANAGEMENT.md` asks for an "audit note in the current working audit document"; none existed. `docs/audits/` is now that place.
- `likeness.md` line 118 says a duplicate is set aside "in the source folder's `gallery_org`"; `likeness.py` writes it to `<work>\_archive\<source folder>\gallery_org`. The two reorg reports keep the Oct 9 and Oct 10 names (Models, `Prospects\Various`); they are point-in-time records, so that is right.
- `STATUS.md` line 19 says "plus 10 pets, all with art identities"; the validator counts 22 pet identities (all under `angel-primes`). Not verified which pets the line means.
- `data/cards/sovereign-dawn/PHASE-2-NOTES.md` has a mojibake icon in its first heading.

## Future-phase ideation (not errors)

- `game-bible.md` (whole file: phases, PvP, alliances, economy, map hierarchy), `design/map-tier-progression.md`, `design/gameplay-modes-spec.md`, and the "Elemental cycles, Phase 2 proposal" section of `design/combat-calculation-spec.md`.
- `codex/heroes/*` (30-hero roster, `AP-001` to `AP-022` angel series "proposed", Elder Dragon and physique pages, `ideation_lists.md`): ideation tier, a subset ships first.
- `specs/*` except `card-schema.md`: drafts for systems with no data yet (maps, players, alliances, stores, trade, diplomacy, leaderboards, expeditions, economy nodes, notifications, sessions, ...).
- Art proposals: `art/art-packs-and-comfy-node-proposal.md`, `art/thorne-art-studio-proposal.md`, the open C1 part of `art/comfyui-automation-proposal.md` (API runs and delivery of renders; `tools/art/comfy_run.py` does not exist), the reference-to-video idea in `art/minimax-h3-video-templates.md`.
- Deferred plan items: multi-image input phase (plan 10-09, 3.8), game animation backlog (8.7), folding `tidy`, `list` and `--class` (6.3b), the P4 face pass with a second image (plans 10-11 and 10-12), Phase 5 of the names plan (several Primes per hero).
