# 2026-10-19: library rebaseline, frame retirement and Angel Primes shots

**Status:** dropped (superseded; not completed)

## Supersession record

**Superseded:** 2026-10-22T16:34:08-05:00 (local offset recorded).

**Reason:** the Oct 22 full-plan reconciliation separates enduring rules,
dated evidence and focused execution owners. Later approved direction
supersedes conflicting older sequencing/limits; remaining work is not done.

**Context:** [live reference](../../../art/library-reconciliation-context.md), [full reconciliation audit](../../../audits/2026-10-22-plan-feedback-audit.md).
Original user wording and historical evidence are retained below.
The source checklist is historical; formerly open items are explicitly
marked transferred, not checked off as implemented.

## Unfinished work and successors

| Source item | Live owner | Destination / disposition |
| --- | --- | --- |
| R9 | [2026-10-22-library-upkeep.md](../../2026-10-22-library-upkeep.md) | U1 |
| R11 | [2026-10-22-library-upkeep.md](../../2026-10-22-library-upkeep.md) | U2 |

## Result of reconciliation

Retired as an execution owner after task and context transfer. Archival
does not assert implementation, render approval, convergence or production
acceptance. Live owners above retain the remaining gates and questions.

## Original source record

**Original status:** active (ingest complete; user review and chest-crop assessment remain)

This plan coordinates today's library ingestion and frame retirement with a
first pass over the older plan queue. The canonical runbook is
[original-photos.md](../../../art/original-photos.md); likeness matching and safety
rules are in [likeness.md](../../../art/likeness.md).

## Current state

- Before the Oct 19 run, `Various\gallery` contained 787 incoming originals
  (about 106 MB); the pool is now empty after ingestion.
- A second batch arrived later on Oct 19 with 916 incoming originals (117,332,043
  bytes). Its verified pre-run snapshot is `library-20261019-171329` (8,287
  files / 4,088,450,098 bytes); that batch has also been processed and checked.
- A read-only preflight on Oct 16 counted 9 incoming images; that run did not
  happen because ComfyUI input files changed during both backup attempts.
  Those earlier backups are explicitly marked incomplete and are not usable.
- The user has since cleaned Angel Primes inputs and says they should now be
  stable. ComfyUI output generation may continue; the library tool does not
  back up or alter output renders.
- An earlier pull brought 25 Angelica `zz_Shots` into
  `workflows/_shots/angel-primes/Angelica`. The Oct 19 workspace-wide preview
  found six updates and 19 unchanged; only those six updated shot JSONs were
  imported. No candidates or finals were pulled.
- The current repository has extensive uncommitted changes. Preserve them;
  inspect and classify, but do not stage, commit, or overwrite unrelated work.
- Two input inventories 20 seconds apart matched exactly: 192 files and the
  same size/timestamp digest. The library preflight found 787 photos in the
  `Various` pool.
- The first snapshot attempt at 12:54 failed safely because the running
  read-only preview/check commands were still writing run logs under
  `_reports\runs`. Its incomplete folder `library-20261019-125421` is retained
  and must not be used as a backup. After both commands finished, snapshot
  `library-20261019-125822` verified all 7,344 files (3,298,240,866 bytes)
  against its manifest and SHA-256 hashes.
- Frame generation and the configured `flows.frame` entry have been removed.
  The 972 work-root frame images in 246 folders and the 9 remaining ComfyUI
  frame inputs were moved to `_archive\frame-retirement-20261019`; every hash
  matches the verified snapshot. The archive has a CSV manifest.
- The 54 tracked generated Prime-frame workflows were moved to
  `workflows/_archive/frame-retirement-20261019`; the 54 local `.test` copies
  and all 114 installed Prime-frame workflows were moved to workflow backups.
  The tracked and test workflow hashes were checked after moving. Unrelated
  hair workflows with `Frame`/`Framed` in their names were not part of this
  partial-body flow and were left alone.

## Decisions

| ID | Question | Answer |
| --- | --- | --- |
| L1 | Should today's 787-photo batch run through the full likeness/library routine? | Yes. Preview the work, create and verify a fresh full backup, then run the existing end-to-end launcher. |
| L2 | Should the failed Prime frame flow and its derived images/workflows be retired? | Yes. Stop generating frames, remove configured frame inputs/workflow variants, and archive existing frame files rather than deleting them. Preserve other workflow work. |
| L3 | Should a chest crop replace frames in this pass? | No. Defer implementation until a preview can be assessed on varied source crops. The current run should produce normal scaled images and headshots only. |
| L4 | Should saved Angel Primes shots be pulled before any publication? | Yes. Preview and pull only `zz_Shots` from the Angel Primes workspace into `workflows/_shots`; do not publish them to another workspace. |
| L5 | May the current uncommitted changes be staged or committed as part of this work? | No. Keep them intact and report their scope for the user's later decision. |

## Plan rebaseline: Oct 19 audit

All 10 active plans and the one proposed plan in the index were reviewed
against the current queue and work. No older active plan is ready to archive:
each retains a real user decision, photo/classification review, ComfyUI test,
manual prompt task, game-data decision, or explicitly scoped tooling follow-up.
The CLI-simplification plan remains proposed until the user decides whether to
combine commands.

- Frame generation, its threshold decision, frame-vs-normal comparison, and
  pose-frame options are retired. The old frame records now point to this plan.
- The seven possibly missing Prime renders have one home in T5; the old E13
  duplicate points there. The stale T10 prospect names/scores point to the
  current run review (R11) and candidate-ranking feedback (D10).
- The old A2 junk review is consolidated into R11; the duplicate gallery and
  Angel-to-Prospect ranking review is kept once, under D10.
- Remaining work stays open where it depends on the user's image choices,
  classification, ComfyUI tests, prompt approval, product decisions, or
  review of the fresh library results. No older plan was silently closed.

## Steps

- [x] **P1 ai** R0 Read the current plan index, generated queue, relevant photo and prompt plans, worktree state, and the incoming gallery before acting.
- [x] **P1 ai** R1 Reconcile stale frame decisions and checklist items in the first-shot and Prime/frame plans; keep unrelated open work visible.
- [x] **P1 ai** R2 Preview `pull --only shots` for the Angel Primes workspace, verify it is shots-only, then import those shots into the repo before any publishing. Six updated Angelica shots were pulled; 19 existing shots were unchanged.
- [x] **P1 ai** R3 Create and verify a fresh full library backup (work root excluding `_archive` and old `_backup`, ComfyUI inputs, and workspace config). The verified snapshot is `B:\Sovereign Territories\_backup\library-20261019-125822`.
- [x] **P1 ai** R4 With the verified snapshot available, remove frame generation/configuration and generated frame workflow variants. Archive active frame images and workflow copies in the work library and installed workspaces; do not delete them. Preserve unrelated ComfyUI input/output files and the user's manual removals.
- [x] **P1 ai** R5 Previewed and inspected the full run. It proposes 1 same-ID replacement, 3 older incoming same-ID copies to `Various\duplicates`, 228 byte-identical duplicate copies, no unresolved ID conflicts, and 786 of 787 pool photos eligible to move. The 6 junk candidates are a per-step preview, not a projected final count; the preview does not simulate earlier moves.
- [x] **P1 ai** R6 Run `bin\library.cmd` end to end, then check `IN SYNC`, updated reports, duplicate/replacement archives, `_junk`, review
  counts, and the final sort summary. The first attempt made no crop-history changes and was stopped after progress stalled; the retry
  snapshot `library-20261019-140638` verified at 7,107 files / 3,868,753,524 bytes. The retry processed the remaining 546 pool photos (542
  sorted, 3 set aside as junk, 1 duplicate archived); 24 prior same-ID originals were preserved. `bin\library-check.cmd` reports `IN SYNC`,
  0 active duplicate pairs, 0 conflicting IDs, and `NOTHING WAITING`. The full-run launcher completed ingestion and synchronization but
  returned 1 when the gallery step hit a stale `frame_photo` call; after fixing it, `bin\people-gallery.cmd` regenerated the 237-person
  gallery and pairing report successfully. The sync-input step still reports missing/placeholder workspace assets and a selected Female
  photo now in Fantasy; these were not changed.
- [x] **P1 ai** R7 Inventory uncommitted changes by coherent area and summarize them without staging or committing; specifically keep the
  existing prompt/template work, the shots, and pull-scope fix distinguishable. The worktree has 525 changed paths (378 modified, 54
  deleted, 93 untracked) and nothing staged. The 7 `prompts\_edit\female` files are distinct manual drafts; generated prompt outputs, art
  data, and 25 untracked `workflows\_shots` files remain separate. Workflow state includes 54 deleted tracked Prime-frame variants and 55
  untracked archived files (the 54 variants plus manifest), alongside the user's other Angel Primes/Drakn Sisters workflow edits. The
  pull-scope fix is in `tools/workflows/comfy_workflows.py` with a regression test in `tools/workflows/test_cli_surface.py`; other
  routing/tool changes remain in `bin` and workspace configuration. Art tools/tests, plans, runbooks, and other data edits are inventoried
  separately; none were staged or committed.
- [x] **P1 either** R8 Reconcile every active/proposed plan against the current decisions and work. The Oct 19 review has now been rechecked against all 11 active plans and the one proposed plan.
  No active plan is ready to archive: each still has a real user decision, review, ComfyUI test, manual prompt task, game-data task, or explicitly deferred tooling follow-up. The CLI proposal remains proposed pending your decision.
  The Oct 12 scratch note was incorporated into the tooling-debt plan; completed gallery display requests were verified against the implementation, while image-level exclusion remains open there.
- **Transferred, not completed:** **P2 ai** R9 Design a chest-crop preview using face-anchored head/shoulder/chest bounds; assess sample full, partial and varied-pose images before deciding whether to add it to `originals`, workspace inputs or Prime workflows.
- [x] **P2 ai** R10 Update the likeness/runbook and Prime-flow documentation after frame retirement is implemented; ensure no active instruction implies frames will be generated.
- **Transferred, not completed:** **P3 you** R11 Review the post-run photo outcomes: `_junk` now contains 6 photos (3 from the earlier batch and 3 new incoming photos
  flagged for 2+ faces), the 3 older same-ID imports in `Various\duplicates`, the 24 preserved replacement originals, 9 review photos, and
  the three protected Drakness images left active because they contain multiple faces. `_archive\Various\gallery_duplicates` contains 332
  files total, including prior history; the final active duplicate check is clean. Identify salvage or manual-resolution actions; do not
  delete files. Use D10 for feedback on the refreshed gallery and Angel-to-Prospect rankings.
- [x] **P1 ai** R12 Process and verify the later 916-photo batch. The inputs remained stable across two inventories. Snapshot
  `library-20261019-171329` was verified (8,287 files / 4,088,450,098 bytes). The run archived 70 byte-identical copies, found no
  conflicting same-ID imports, sent 3 multi-face incoming photos to `_junk`, created 39 new Prospect folders, and emptied the pool. The
  Windows host suspended the library and crop processes; their exact PIDs were checked and resumed without restarting the run. All pipeline
  stages completed, including report generation. The final `library-check.cmd` reports 0 duplicate pairs, 0 ID conflicts, no pool photos,
  `IN SYNC`, and `NOTHING WAITING`. The three new junk photos are `various_image_7518022535991337255.jpg`,
  `various_image_7518029125665347092.jpg`, and `various_image_7518041966060682367.jpg`; all were flagged as containing 2+ faces. The full
  identical-copy archive now contains 332 files including history; the three older same-ID imports in `Various\duplicates` remain unchanged.
- [x] **P1 you** R13 Superseded by the user-approved staged Review/Reject workflow in the [self-healing likeness plan](2026-10-20-likeness-library-self-healing.md); Sophie photo choices remain user-directed.
- [x] **P1 ai** R14 Superseded by the combined, previewed and backup-verified processing phases in the [self-healing likeness plan](2026-10-20-likeness-library-self-healing.md). Do not make interim Sophie moves outside that workflow.

## Preserved original discussions (verbatim)

<!-- markdownlint-disable MD013 -->
````text
## Raw request (Oct 19)

I did manually clean-up the ComfyUI inputs to remove some images I did not want for Angel Primes - it wasn't as useful to have the frames
there when I was testing. I do have workflows running to generate output, but the inputs should be stable and not changing now. In the past
we were able to run the likeness process from end-to-end even when I had workflows running to be testing things. So let's try the process
and see if we run into any issues. I agree with your plan, so do the write-up for docs/plans in the standard format of how we do the work
for today and then we can proceed. We'll also need to check plans for other days and figure out what things need to be closed as we aren't
doing some of them - but there may also be outstanding work we DO need to circle back on completing. So - maybe the docs/plans work is the
first thing we need to re-baseline on - updating olders plans and making sure that we determine what are all the outstanding items we do
need to do - but it is a priority to get the existing Various/gallery processed, clean-up the frames, pull the shots I have in the Angel
Primes install (before publishing) and ensure we get things cleaned up and if there are _junk files or _duplicates I want that summary. I
know we were also updating the .html and reports as well. So, there are a lot of moving parts right now and a lot of uncommitted changes I
need to figure out what to do with.
````
<!-- markdownlint-enable MD013 -->
