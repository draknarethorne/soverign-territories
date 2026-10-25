# 2026-10-09: step back on the command line (comfy_workflows.py and bin\*.cmd)

**Status:** proposed (remaining folds/forwarders only; no additional consolidation approved)

## Oct 25: continued simplification interest

The [gallery continuation](2026-10-22-gallery-review-layout.md#oct-25-0913-intake-integration-and-next-safe-work)
holds the user's new request to simplify actions/parameters after image work.
Inventory and accurate help can proceed without intake-quality feedback. Current
launcher help now describes v16 crop/crop/LaMa/frame and apply-only model downloads.
No command/parameter removal, default change, `inputs sync` revival or speculative
compatibility wrapper is implied. C2 and finals 6.3b/6.5 still gate actual folds.

## Review and questions: 2026-10-22 16:26 -05:00

The counts and option tables below are an Oct 9 historical inventory, not
today's command contract. Finals Phase 6 already records preview/explicit apply,
deploy/pull/inputs simplification and `audit.cmd`; C1/C3/C4/C5 are not unanswered
prerequisites for those shipped slices. The remaining decisions are finals
6.3b (command folds) and 6.5 (which forwarders to keep), informed by C2.
Ask which current launchers the user uses before proposing any removal.
Oct 20 H4 transfers here: preserve entry points until tested replacements
and an explicit user decision. Read current help and caller tests first.

In particular, retain existing `sync-inputs.cmd`; the historical `inputs sync`
proposal is not an approved additional command. No new command, hidden option,
changed default or forwarder removal is authorized by this review.

An inventory of the command line and a proposal to simplify it. It is decision D7 and Phase 6 (6.3b, 6.5) of [2026-10-09-finals-and-mvp.md](2026-10-09-finals-and-mvp.md); the first steps (one preview rule, forwarders) were built there.
What is left is the part that needs your decision: fold the overlapping commands as the tables below propose, or leave them. Tick nothing here; the boxes in the finals plan (6.3b, 6.5) carry it to `docs/todo.md`.

## The size of it today

| Thing | Count |
| --- | ---: |
| `comfy_workflows.py` sub-commands | 12 (`list`, `status`, `deploy`, `cleanup`, `fork`, `pull`, `make`, `inputs`, `denoise`, `setup`, `tidy`, `finals`) |
| Long options across them (shared ones counted per command) | 123 |
| Launchers in `bin\` (not counting `_env`, `_end`) | 43 |

`deploy` has 20 options, `inputs` 19, `pull` 14, `cleanup` 13, `status` 12, `make` and `tidy` 11 each.
The same six filters (`--hero --group --stage --class --engine --match`) are repeated on `status`, `deploy`, `cleanup`, `pull`, `make` and `tidy`.

## What looks like legacy or overlap

| Area | Today | Proposal |
| --- | --- | --- |
| Preview vs apply | Two conventions: `deploy`, `pull`, `make`, `inputs`, `denoise` write unless `--dry-run`; `cleanup`, `tidy`, `setup`, `finals` preview unless `--apply` | One rule: **every command that changes files previews unless `--apply`**. Step 1 (safe): accept `--apply` on all of them. Step 2: flip the old ones, with the launchers passing `--apply` so nothing changes for you |
| `deploy` content switches | `--curated --tests --shots --staged --templates` (5 flags) | One `--include curated,shots,tests,staged,templates,finals` (a list) |
| `deploy` modes | `--overwrite --patch-only --new-only --existing` (4 flags) | One `--mode patch\|new\|existing\|overwrite` |
| `deploy --reset-inputs` | Duplicates `inputs --reset` | Remove; run `inputs reset` |
| `pull` kinds | `--shots --templates --prune --include-legacy --force` | `pull` takes every kind by default now (workflows, curated, shots, candidates, finals); `--only shots\|templates\|finals` narrows it |
| Arranging files | `tidy` (workspace), `finals sort` (zz_ folders), `finals reclassify` (repo) | `tidy` does the workspace including the zz_ folders (absorbs `finals sort`); `tidy --repo` replaces `finals reclassify` |
| Showing state | `list`, `status`, `finals status`, `inputs --status` | `status` shows everything (workflows, finals, inputs) with `--only`; `list` becomes `status --homes` |
| `inputs` | `--pull --reset --fix --status --set` plus 8 role flags (`--photo --prime --apose --heels --scene --polish --bare`) | Actions like `finals`: `inputs pull\|reset\|fix\|status\|set HERO --photo ...` |
| `--class` vs `--stage` | Two ways to filter by stage | Keep `--stage`, make `--class` a value of it (`--stage scene`, `--stage studio`) |
| `--root` | A testing override shown in every `--help` | Keep, hide from help |

## Launchers: what they wrap

| Group | Launchers | Proposal |
| --- | --- | --- |
| Deploy | `deploy`, `deploy-group`, `deploy-curated`, `deploy-shots`, `deploy-templates`, `publish` | Keep `deploy` and `publish`; the rest become `deploy` options (forwarders until you stop using them) |
| Pull | `pull`, `pull-shots`, `pull-templates` | Keep `pull`; the others forward to `pull --only ...` |
| Build | `make`, `update` (same command), `refresh`, `refresh-group`, `refresh-firered`, `prompts` | `refresh` is the daily one (prompts, then make, then deploy existing); `refresh --group G`, `refresh --firered`; drop `update` |
| Workspace | `setup-workspace`, `tidy`, `cleanup`, `workspaces`, `status` | `setup` for the whole job, `status` to look; `tidy` and `cleanup` stay for the single step |
| Inputs and outputs | `inputs`, `sync-inputs`, `organize-outputs` | `inputs sync`, and `organize-outputs` stays (rarely used) |
| Candidates and finals | `finals` | Stays |
| Audits and checks | `identity-audit`, `negation-audit`, `library-audit`, `style-audit`, `codex-drift`, `validate`, `check`, `test` | One `audit NAME` front door; `validate` stays and runs the cheap ones |
| Scaffolds | `scaffold-angels`, `scaffold-characters`, `scaffold-sister`, `animate`, `videoprompts` (same tool as `animate`), `extract-literals`, `art-refs` | Keep (each is one job); drop `videoprompts` |

## How we would do it without breaking your habits

1. **Nothing disappears at first.** Every old launcher and option keeps working and prints one line saying what replaces it.
2. **One change at a time, with tests:** the parser tests pin each old spelling to the new behaviour.
3. **Update `help.cmd` and the workflows README once**, at the end, so they describe the new surface only.
4. After a few weeks of use, remove the forwarders you no longer type.

## Questions for you

| ID | Question |
| --- | --- |
| C1 | Preview-by-default everywhere (with `--apply`), launchers adding `--apply` for the old ones: yes? |
| C2 | Which launchers do you actually type? (The list above is guessed from names.) |
| C3 | Is a single `audit NAME` front door worth it, or do you like the separate `*-audit` names? |
| C4 | `inputs` as actions (`inputs set HERO --photo ...`) instead of flags: fine? |
| C5 | Should `status` show candidates and finals by default, or only when asked? |
