# Plans of action

One file per piece of work we agreed to act on. This is how we work day to day, so the other documents stay clean.
Where to look: **what needs you, by priority, is [../todo.md](../todo.md)** (generated from the plans); what is decided is [../STATUS.md](../STATUS.md); how each day went is [../recap/](../recap).

## The pattern

**Current scheduling (Oct 30):** finish the existing sandbox baseline, do not
restart intake. Recovery and the full intake/matching/AI audit are complete;
publication is safely rolled back and waiting for Explorer handles to clear
after the user's reboot. Exact resume evidence is pinned in the
[recap index](../recap/README.md).

## Now, next and holding

This supersedes Oct 29's choice to keep all independent plans active.
There are **4 active, 14 holding and 1 proposed plans**. All unfinished scopes
stay in their original files: no `_holding` directory or broad link migration.
Holding is a scheduling state, never completion, cancellation or acceptance.
The [plan table](#plans) and each held plan's **Resume gate** give its owner
and reactivation condition.

| Window | Work | Exit / boundary |
| --- | --- | --- |
| Now, blocked until reboot | Cast C6/C7, intake I59/I60, performance T16, storage S15 | Rebind the unchanged preview with supported replan; backed-up same-stage install; installed check; actual Gallery/Overview/Review, retained intake history and exact face/prepared/padded links; human placement/quality review. No new full intake |
| Next, before another expensive run | Storage S24/S25 | Measure file/byte budget; compare scope, packing/compression and retention; agree FULL/LEAN/COLLAGE evidence contract. Preserve verified recovery and active sources; no automatic deletion or ZIP assumption |
| Next bounded quality round | Performance T17, intake I68/I69/I70 | Recipe-aware statistics, all 13 named cases, coordinated early crop/masks and calibrated denoise/tone selection. Use frozen comparisons before approving another full run; do not change the staged baseline |
| After those results | Intake I71-I76, performance T18/T19; reactivate upkeep/actions/naming/engine slices as needed | UX/terminology/Artist scope, processing profiles; incremental batch/calibration and action UAT are separate gates, not silently approved |
| Documentation return checkpoint | [Tooling D13/D4](2026-10-12-tooling-debt.md#steps); D22 agent refresh delivered | After installed-baseline review, explicitly select a bounded remaining documentation slice, then scope day-close automation from findings. Do not preempt storage-before-next-run or reopen a broad reorganization |
| Holding, downstream | Manual prompt P14-P17 and reference rendering R44; finals/Artist/profile/game tracks; broad refactors/model experiments | Resume only when their per-plan gate is met and the slice is selected. Preserve current inputs, rendered evidence, manual drafts and frozen receipts |

Only a **demonstrated blocker** may interrupt now. For example L19 Intake
navigation or a derivative defect can reactivate the relevant held slice if
installed UAT fails. This does not reactivate its whole redesign or authorize
Production, family renames, pending swaps or broad cleanup.

**Ownership, not dates, drives execution.** C6 owns one installation;
T16 consumes its timing/recovery evidence, S15 consumes its backup/rollback
evidence, and I59 consumes its actual viewer/face/history evidence. These are
four acceptance views of the **same run**, not four instructions to rerun it.
Likewise I68/I69 owns the old T11 mask comparison; T17 owns statistics,
S24 owns backup scope/format/retention, S25 owns retained evidence modes, and
intake I71-I73 owns preparation-report UX. Gallery L18/L20 and upkeep U6
reuse those contracts rather than inventing parallel policies.

The user's Oct 30 follow-up authorizes sensible merges/splits, not an immediate
new umbrella plan. Keep existing independent contracts for this blocked
milestone: wholesale date/path changes would add review cost without resolving
it. When a real duplicate is found, select one primary owner, explicitly map
every transferred task/context/source, and archive the superseded plan only
after the [reconciliation gates](#how-a-plan-moves). A split must leave a
specific live owner and links for every unfinished part. A newer date alone
is never a reason to restart work or lose earlier evidence.

An active plan may declare `**Queue focus:** C6, C7` using its **open task
IDs**. `bin\todo.cmd` lists only those tasks as the execution queue, plus a
linked count of everything deferred in active/holding plans. Without that
field, all open tasks in an active plan are listed. Unknown, closed or duplicate
focus IDs fail generation, rather than silently dropping work. When a focused
task finishes, update the focus in the same change; select the next slice
deliberately. Within the same plan/priority/owner, focus-list order is retained
(e.g. S15 before S24/S25). Priorities within later scopes remain unchanged and do not
bypass prerequisites.

## Parallel analysis and small improvements

The sequence above is the **mutation/acceptance order**, not a requirement
that all thinking be serial. Keep one primary milestone, with bounded
independent analysis and one small quality improvement alongside it:

| Lane | Current candidates | Required output / stop |
| --- | --- | --- |
| Main delivery | Same-stage install and real viewer/recovery checks | Finish or report a concrete blocker; no new intake or recipe change to the frozen run |
| Parallel analysis | S24/S25 backup/artifact alternatives; I68/I69 mask/erase case diagnosis; I70 denoise/tone criteria; T17 measurement design | One owner, bounded sources, evidence and a decision/recommendation handed back to the existing task. Reading existing evidence may proceed before install; mutation, benchmarks and default adoption keep their own gates |
| Small quality improvement | Clearer report labels/links/empty states, documentation navigation and focused regression coverage, scoped within I71-I73 or the owning tool | Preview and focused validation; no model/threshold/recipe, schema, root layout, dependency or storage-retention change disguised as a quick win |

Select one small independent slice per iteration, not every easy-looking item.
If it expands into new behavior or requires a major decision, record the
finding in its owner and return to the milestone. Analysis helpers must not
edit the main worker's files or read mutable half-published evidence; use
frozen/read-only inputs and avoid competing heavy B: I/O during installation.
Parallel analysis is permission to prepare decisions, not to apply them early.

The generated queue stays in one file for now: current tasks first, deferred
inventory and history collapsed, card state collapsed separately, and personal
notes visible. This avoids several generated priority files becoming competing
queues. Split into additional generated views only when a specific navigation
need remains; generate them from the same plan tasks, never duplicate them
by hand. Multiline task summaries and named plan links make current tasks
readable without opening every date-named file.

The complete fresh-v23 note is preserved with
[F01-F31 coverage](2026-10-23-image-intake-preparation.md#complete-source-to-plan-coverage-ledger).
Archiving a captured feedback file is independent of finishing its tasks.
Root migration/`_Intake` S17-S19 remains proposed, not installed behavior.

| Kind of document | Where | Rule |
| --- | --- | --- |
| Raw feedback and draft thinking | `feedback/<topic>.md` (git-ignored), or directly in chat | Brain-dumps, review notes and drafts, free-form. Preserve each file until its complete text is captured word for word in the owning plan and coverage is verified. Never bulk-clear this directory |
| A plan we agreed to act on | `docs/plans/YYYY-MM-DD-<slug>.md` (this folder, tracked) | Incorporates file or chat feedback when we agree to act on it. Your words go at the end, word for word |
| A finished plan | `docs/plans/_archive/` | `Status: done` or `dropped`, with a `Result` section; it stays as history and is ignored when reading |
| Current state | [../STATUS.md](../STATUS.md) | Decisions and open questions only. It does not list the plans: this README does |
| Your queue | [../todo.md](../todo.md) | Generated by `bin\todo.cmd` from active-plan Queue focus (or all open boxes when absent), sorted by priority and owner, with linked deferred/holding counts, card state and your notes. Never ticked by hand |
| The day | `docs/recap/YYYY-MM-DD-HHMM-recap.md` | A reflection written at the end of a working day (see [../recap/README.md](../recap/README.md)) |

## How a plan moves

1. **Capture** raw feedback in `feedback/` or directly in chat. Read it before acting; do not treat a note as agreement to major design decisions. `tmp/` is for disposable tool output, not new user feedback. Existing raw notes there receive the same preservation guarantees.
2. **Agree and incorporate.** Update the existing owning plan, or create `YYYY-MM-DD-<slug>.md` (the date is the day we agreed), with a `**Status:**` line (`proposed`, `active`, `holding`, `done`, `dropped`) and a row below. Preserve the original file text or relevant chat messages word for word at the end, with their source/date. Turn every request into a step, decision or explicitly recorded disposition; raw text alone is not a plan.
3. **Work it.** Decisions are asked one at a time and recorded in the plan's decision table; steps are checkboxes ticked as they finish; code and doc changes follow the normal order (design rule, schema, validator or tooling, implementation, tests).
4. **Close.** Set `**Status:** done` (or `dropped`), add a short `Result` section, `git mv` the file into `_archive/` (fix the relative links), and update the row below. A done plan has no open boxes: each is finished, dropped, or moved to a live plan.
5. **Supersede.** Follow the preservation and reconciliation gates below.
   A newer date or shorter plan alone does not supersede an older plan.

After incorporation, re-read the raw source and verify both verbatim preservation
and actionable coverage. Only then may that specific feedback file be removed.
When the user requests archival, move that exact note into `feedback/_archive/`
instead of deleting it; do not overwrite an existing archived copy.
Choose its topic folder and update the local index and tracked coverage ledger
in the same change, following the [physical filing model](../archive-guide.md#physical-layout-and-ongoing-filing).
The same physical-folder plus index rule applies to documentation archives.
The current intake directory is root `feedback/`, not `docs/feedback/`.
Re-read it immediately before removal so edits made during the work are not lost.
If a note spans plans, keep one complete verbatim copy in the primary plan and
link the other owning plans to it. Unresolved or not-yet-incorporated feedback
stays in place; an empty feedback directory is not a completion requirement.
Never clear `feedback/` as temporary-file cleanup.

## Keeping plans current without losing context

Plans evolve as design decisions change and work pauses or resumes. Review
the affected owners when that happens, not only at day-close. Reconcile one
plan at a time; a repository-wide inventory is not a full content audit.

**At each pivot:** before adding another continuation, identify the affected
current owner, say which old decision changed, and either update that owner
or draft a named successor. If the pivot strands work, record its destination
immediately. Keep the index and dated questions current; don't wait for a
large retrospective cleanup. Day-close checks should flag status/index drift,
unowned transfers and competing active ownership, never auto-retire plans.

1. **Inventory before changing.** Record the plan's status, independent scope,
   decisions and rationale, constraints, examples/known failures, evidence,
   dependencies, open questions, user wording, and every unfinished task.
   Do not reduce context preservation to copying unchecked boxes.
2. **Classify every part.** Keep it active, retain it as independent/deferred
   work, move it to an identified successor/reference, or explicitly supersede
   it with a dated decision and reason. A replacement decision must say which
   older rule it replaces and why. Never infer completion from age or a newer
   implementation summary.
3. **Draft without changing authority.** A proposed successor is labelled
   `proposed` and identifies the still-active source owner. It is excluded
   from the generated execution queue. Do not run competing checklists.
4. **Verify the transfer before activation.** Use a source-to-destination
   ledger covering tasks and context. Re-read the source and verify complete
   raw-text preservation, rationale, examples, decision precedence, links and
   dependencies. Put enduring rules in canonical documentation, execution
   work in focused plans, and dated evidence in a clearly labelled reference.
   Current work must not require reading an ignored archive to recover a rule.
5. **Activate coherently.** Update source dispositions, successor status,
   index rows, references, current status and generated queue together.
   Mark a checkbox as transferred/superseded with its destination and reason,
   not as implemented. Validate that no unfinished scope vanished or has two
   active owners. Preserve the source wording separately from its disposition.
6. **Archive only after the gate passes.** Add the banner below immediately
   after the title, a terminal status and a `Result`. Move with `git mv`;
   fix relative links. Every formerly open item must have an explicit
   completed, dropped-by-decision or transferred disposition. The banner
   explains incomplete-looking checklists without pretending they were done.
7. **When uncertain, leave it.** Keep the source in place, record the
   uncertainty and next review step, and ask one focused question when needed.
   Independent plans waiting for user tests remain active; record the blocker
   rather than manufacturing work or closing them. Revisit a paused plan's
   assumptions before resuming it.

Use `done` only for delivered/accepted scope. For a plan retired because a
replacement makes it obsolete, use `dropped (superseded; not completed)`.
Both terminal states are excluded from the active queue; the index explains
the distinction. No new queue/parser status is needed.

Required supersession banner:

```text
Superseded: YYYY-MM-DD HH:MM:SS +/-HH:MM (local timezone/offset).
Reason: what changed and why this is no longer an execution plan.
Successors: links to the active plan(s) and enduring rules/evidence.
Unfinished work: source task IDs -> destination IDs, including deferred items.
Context: where decisions, rationale, examples, dependencies and raw words live.
Completion: archival is not implementation or acceptance of the remaining work.
```

Keep the ledger proportionate: use a table in the owning plan or a requested
audit, not a new management document for every small edit. Split genuinely
unrelated work; do not fragment tightly coupled tasks merely to meet a length
target. Source notes are never deleted as a side effect of reconciliation.

## The queue: priority and owner on every open box

Every open step is a checkbox that starts with a tag, `- [ ] **P1 you** T3 ...`. `bin\todo.cmd` reads the tags of the `active` plans and writes `docs/todo.md` with one queue.

| Tag | Meaning |
| --- | --- |
| `P1` | blocks other work, or is cheap and valuable |
| `P2` | normal |
| `P3` | later, or an idea |
| `you` | needs your hands or your decision (picking photos, ComfyUI runs, approvals, art choices) |
| `ai` | the assistant can do it, when you say go |
| `either` | whoever gets to it; a decision with a recommendation |

An untagged box counts as `P2 either`. A note that is not a task is a plain bullet, not a box.

## The day's hygiene

Before we commit and push at the end of a working day, we do these, so nothing is forgotten:

1. **Feedback is accounted for.** Re-read `feedback/*.md`, relevant chat feedback and any legacy raw notes in `tmp/`. Incorporate them into owning plans with raw words preserved and coverage checked before removing any specific source. Notes awaiting decisions stay safely in place; never empty either directory just to satisfy hygiene.
2. **Plans are current.** Every plan has a `**Status:**` line; finished plans are archived; open boxes carry a tag; the table below is right.
3. **`bin\todo.cmd`** is run, so `docs/todo.md` shows the real queue.
4. **STATUS.md** has the decisions of the day and no list of plans.
5. **A recap** is written in `docs/recap/`.
6. Validators, tests and markdownlint pass (`pre-commit`).

## What a plan contains

- A `**Status:**` line and the date.
- The threads or goals, in the user's words where they matter.
- A vocabulary table if the plan introduces names.
- Decisions (ID, question, recommendation, answer) and phased steps as tagged `- [ ]` checkboxes.
- A `Result` section when closed.
- The raw brain-dump, word for word, at the end of a plan that came from one.

## Rules

- Big design decisions need the user's approval before any file is edited for them (for example the MVP element set).
- A plan states what is open; `STATUS.md` states what is decided. Do not copy one into the other.
- Keep lines under 1,000 characters (markdownlint), one home per fact.

## Oct 22 feedback intake process

**Status:** adopted. The intake location and preservation rules above replace
the older requirement to empty `tmp/`. Existing feedback documents are not
implicitly implemented, approved or safe to delete because this process changed.

### Original process feedback (verbatim)

Source: `feedback/revise_docs_planning_process.md`, Oct 22, 2026.

```text
When you get some time - I want to revise our docs/plans overall process to use the feedback/ directory for my raw .md files instead of tmp/ directory.  I've written up a couple feedback documents while you have been working and want to have those feed into our docs/plans either as updates to existing plans or a new plan and then we can remove them once the docs/plan is written.  You can revise any instructions, memory or readme.md that indicate how we work together to accept raw feedback either in a feedback/ .md file or just direct feedback in this chat that needs to be captured in the plans.  In general this is working really well using tmp/ - but I just wanted to ensure an accidental clearing of tmp/ doesn't happen and removing .md files from feedback/ only happens when we ensure the information is into a plan.
```

## Current library work order (Oct 23)

### Oct 27 feedback disposition and intake restart

Archiving a raw note means its complete wording and actionable coverage have
been incorporated, not that every resulting task is implemented. Do not
archive active plans because their source feedback was filed.

| Raw feedback basename | Owning work / answer | Disposition |
| --- | --- | --- |
| `auto_protection_thoughts.md` | Engine E13; draft gates/overrides implemented, calibration and real acceptance open | Individually verified and archived |
| `family_naming_question.md` | Family N7/N9; draft metadata/display exist, acceptance and transitions open | Answer recorded; individually verified and archived |
| `feedback_on_acceptance_testing.md` | Layout L1-L20 and its source coverage; actions A1-A9, engine/protection and naming dependencies remain live | Individually verified and archived; not all accepted |
| `image_analysis_question.md` | Face-analysis M1-M4; learned face embeddings have no explicit hair/lipstick weight, controlled evaluation still open | Individually verified and archived; empirical evaluation open |
| `image_intake_feedback.md` | Intake I30-I37, all 26 named examples plus controls; latest recipe remains unaccepted | Individually verified and archived; implementation underway |
| `fresh-v23-20261029_feedback.md` | Intake F01-F31/I68-I76; performance T17-T19; storage S24/S25/S17-S19 | Complete current snapshot and all 13 named cases mapped; individually verified and archived; implementation/acceptance open |
| `revise_docs_planning_process.md` | This README's adopted feedback/preservation process | Answered/implemented; individually verified and archived |
| `update_recap_10_22.md` | Actions A4/A6 scenario explanations/UAT; current combined recap and queue track state | Individually verified and archived; scenarios not silently run |
| `person_names_folders.md` | Family N11 resolved: explicit correction replaces erroneous original name; N12 implements after intake, before family acceptance | Answer recorded; individually verified and archived |
| `categories_and_code.md` | Storage S17-S19; S4/S5 path authority | Exact current source captured; category/schema/global configuration and unchanged-policy tests remain open |
| `chasing_my_tail.md` | Tooling D17; this index's now/next/holding and same-run ownership | Exact current source captured; explicit deferrals adopted, storage not assumed solved |
| `cleanup_backups_reports.md` | Storage S10-S16; S24 growth/retention | Complete source preserved; active inputs protected, ST-v9 disposition remains dependency-gated |
| `edit_and_prime_templates.md` | Manual migration P14-P16; P7/P9 documentation | Exact source captured; manual nuance/token/camera/light fidelity and workflow regression review remain open |
| `gallery_directory_structure.md` | Storage S1/S4/S5/S17-S19; layout L19 | Exact source captured; current-state inventory, future categories and reversible sandbox-first migration remain open |
| `generated_images_to_gallery.md` | Rendering R8/R16/R21/R23/R24/R44 | Exact source captured; selected generated pullback, compatible chaining and real GUI round-trip acceptance remain open |
| `gui_and _thumbnails.md` | Storage S10/S11/S24/S25; upkeep U6 and layout L20 | Exact source captured; per-page thumbnail costs, reference-safe retention/trash/purge contract remain open |
| `overlay_reference.md` | Intake I77 and existing reference-bank implementation | Complete source preserved; eligible input/config inventory remains open, people photos stay out of Git |
| `pipeline_code_complexity.md` | Structure E4, consuming intake/cast/engine/naming evidence | Exact source captured; bounded maintainability audit and full named/unnamed/rebase acceptance remain open |
| `recap_10_27.md` | Storage S21/S23; tooling D4/D16 | Complete source preserved; manual recap lifecycle handled, day-close automation and human checks not inferred |
| `trigginer_cli_from_gui.md` | Actions A7; rendering R23/R8/R24 | Exact source captured; paired jobs versus trusted GUI bridge, preview/apply/progress/recovery design remains open |
| `various_people_names.md` | Naming N12/N13; intake I75, cast C10 and actions A2/A6 | Exact source captured; explicit asserted-name/mixed-face/history/filename acceptance matrix, no blind force-merge |

**Oct 30 filing batch:** the 13 current source snapshots above were reviewed
against their owners and verified complete before individual archival into
the local feedback archive. At 14:05, all 24 archived notes (this batch plus
11 earlier notes) were physically grouped into seven topic folders with a
local README; the date-only batch folder was removed. Original bytes and source
hashes are retained; missing exact copies were appended at their primary
plans' ends, rather than rewriting earlier dated feedback. Open or holding
implementation is not a reason to keep an already captured raw note active.
Future edits/new notes remain in `feedback/` until independently reconciled.
No implementation checkbox was closed merely because its source was filed.

The [current scheduling table](#now-next-and-holding) replaces the old
phase-order summary. It does not merge independent owners or mark their
unfinished work complete. Existing authorized 20-30 source-bound Prime samples
remain downstream of verified rebase, R44 routing and source-faithful prompts;
there is no parallel rendering queue during the Explorer blocker. N11 is an
answered naming decision; N12 remains implementation after intake tuning.

The Oct 22 run remains dated evidence, not validation of the new preparation
recipe or cast-release policy. The Oct 25 prepared runner now checks/migrates
one-to-one decisions and preserves recovery; it does not make the real acceptance
run implicit. Review intake first, then the saved matching preview and backup
before a deliberately approved sandbox installation. The Oct 25 overnight request
authorizes the documented sandbox run and small Sovereign Females pilot, not
production processing or broad workflow retargeting. Older uncropped-original recovery is
deferred; exact current inputs and all user decisions remain protected.

## Plans

| Plan | Status | What it is |
| --- | --- | --- |
| [2026-10-09-finals-and-mvp.md](2026-10-09-finals-and-mvp.md) | holding | Resume selected-source/finals/video tests after prepared-library acceptance; no current-input reset |
| [2026-10-09-cli-simplification.md](2026-10-09-cli-simplification.md) | proposed | Historical inventory supporting only the remaining command folds/forwarders (finals 6.3b/6.5); no new consolidation approved |
| [2026-10-11-tidy-junk-organise.md](2026-10-11-tidy-junk-organise.md) | holding | Resume selected element/profile classification after prepared-library review; face-pass experiment conditional |
| [2026-10-12-artists-reset-and-auto-crop.md](2026-10-12-artists-reset-and-auto-crop.md) | holding | Resume Artist-specific review with intake I74 or explicit request; no new reset |
| [2026-10-12-roadmap-and-mvp-data.md](2026-10-12-roadmap-and-mvp-data.md) | holding | Explicitly select the independent Darkness/Light data or game-design track after this milestone |
| [2026-10-12-tooling-debt.md](2026-10-12-tooling-debt.md) | holding | Resume selected tooling slice or demonstrated blocker; day-close automation/non-art audit remain separate |
| [2026-10-20-art-tools-structure.md](2026-10-20-art-tools-structure.md) | holding | Resume bounded extraction needed by approved implementation; preserve current engine bindings |
| [2026-10-22-gallery-review-layout.md](2026-10-22-gallery-review-layout.md) | holding | Reactivate proven installed-viewer blocker only, otherwise after acceptance; L18-L20 remain open |
| [2026-10-22-likeness-engine-acceptance.md](2026-10-22-likeness-engine-acceptance.md) | holding | Accepted baseline/labelled review before calibration, convergence and separate incremental batch; Production still gated |
| [2026-10-22-identity-family-naming.md](2026-10-22-identity-family-naming.md) | holding | Intake tuning before N12 correction/family acceptance; no current bulk naming change |
| [2026-10-22-review-actions.md](2026-10-22-review-actions.md) | holding | Resume deliberate action UAT on installed baseline, or narrow verified recovery blocker; pending actions untouched |
| [2026-10-22-face-analysis-evaluation.md](2026-10-22-face-analysis-evaluation.md) | holding | Labelled ambiguity after installed review, or actual blocking alignment defect; no speculative model dependency |
| [2026-10-22-manual-prompts-to-art-library.md](2026-10-22-manual-prompts-to-art-library.md) | holding | Prepared-input review and explicit selection before P14-P17 fidelity/token/set work; manual drafts preserved |
| [2026-10-22-library-upkeep.md](2026-10-22-library-upkeep.md) | holding | Actual derivative/input defect or accepted baseline before U1/U3/U6/U7 follow-through; no independent maintenance now |
| [2026-10-23-image-intake-preparation.md](2026-10-23-image-intake-preparation.md) | active | Phase 1: full v23 intake/check and AI screening complete; expanded human feedback fully mapped F01-F31. I68-I70 own next-round cases/masking/enhancement; I71-I76 own report/scope/naming/Junk follow-ups. Installed face/history acceptance remains blocked on Explorer |
| [2026-10-23-cast-seeded-library-rebase.md](2026-10-23-cast-seeded-library-rebase.md) | active | Phase 3: revised matching/audit complete, 99 Review holds and full backup verified; safe same-preview retry follows measured native-owner fix, then actual checks/viewers; family/name/Production gates remain |
| [2026-10-25-reference-rendering.md](2026-10-25-reference-rendering.md) | holding | Verified rebase/prepared inputs plus manual fidelity and R44 routing before bounded Prime batch; no queue during install block |
| [2026-10-28-intake-performance.md](2026-10-28-intake-performance.md) | active | T16 actual publication/viewers first after Explorer release; T17 recipe-aware statistics P1 next round, T18 profile/recipe contract P2, T19 CUSTOM P3. Mask comparison T11 transferred to intake I68/I69; T13/T14/T15 remain independent |
| [2026-10-28-storage-operations-and-retention.md](2026-10-28-storage-operations-and-retention.md) | active | S24 backup scope/format/retention and S25 orthogonal FULL/LEAN/COLLAGE storage are top P1 follow-ups after sandbox acceptance; active sources/recovery protected. S17-S19 physical-root/config proposals remain gated |

The Oct 22 retained plans have review/questions blocks; affected owners now
also record the Oct 23 foundation-first scheduling pivot. The
[full reconciliation audit](../audits/2026-10-22-plan-feedback-audit.md)
records scope/task/context coverage. Revisit those questions one at a time;
historical counts are not new runtime acceptance.

### Retired in the Oct 22 reconciliation

These links are historical records, not current execution instructions.
Each superseded source has a timestamp/offset, reason, exact unfinished-task
map, live context homes and an explicit not-completed disclaimer.

| Plan | Status | Disposition |
| --- | --- | --- |
| [Oct 11 first-shot flows](_archive/superseded-prompts/2026-10-11-first-shot-flows.md) | dropped | Current manual migration replaces the old winner-selection sequence |
| [Oct 12 Prime/frames/inputs](_archive/superseded-prompts/2026-10-12-prime-prompts-frames-and-inputs.md) | dropped | Prompt work to migration; missing inputs to finals; upkeep decisions preserved separately |
| [Oct 12 prompt standards](_archive/superseded-prompts/2026-10-12-prompt-template-standards.md) | dropped | Migration owns tested standards, vocabulary mapping and incremental rollout gates |
| [Oct 15 likeness/edit prompts](_archive/superseded-prompts/2026-10-15-likeness-and-edit-prompts.md) | dropped | Manual batch can be reviewed now; report acceptance remains a separate live task |
| [Oct 19 management rebaseline](_archive/superseded-library/2026-10-19-library-management-rebaseline.md) | dropped | Quality, retirement and future intake/pairing split among engine, actions and upkeep |
| [Oct 19 frame retirement](_archive/superseded-library/2026-10-19-library-rebaseline-and-frame-retirement.md) | dropped | Completed retirement evidence retained; chest crop and user outcomes transferred to upkeep |
| [Oct 20 self-healing](_archive/superseded-library/2026-10-20-likeness-library-self-healing.md) | dropped | Foundations retained live; all nine open items transferred to focused owners |
| [Oct 21 rebaseline/family](_archive/superseded-library/2026-10-21-likeness-rebaseline-and-family-naming.md) | dropped | Full contract/evidence retained live; all 69 open items transferred, not declared delivered |
| [Oct 22 reconciliation](_archive/completed/2026-10-22-plan-reconciliation.md) | done | Full current-plan review, context/task preservation, activation, archival and validated handoff |
| [_archive/2026-10-10-names-ingest-headshots.md](_archive/completed/2026-10-10-names-ingest-headshots.md) | done | Names that follow the photos (`z_` files), `Sisters`, the new `Various` batch, headshots, the look-alike guard |
