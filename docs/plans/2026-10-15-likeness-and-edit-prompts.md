# 2026-10-15: likeness reports and manual edit prompts

**Status:** active (library reporting is in place; manual prompt drafts are being refined)

This plan records the current photo-library/likeness state and the user's manual
prompt-development workflow. The detailed command reference remains
[../art/likeness.md](../art/likeness.md); the end-to-end photo runbook is
[../art/original-photos.md](../art/original-photos.md).

## Likeness process: current state

The last full library run completed with the library reported `IN SYNC`. Its
backup excluded `_archive` and older `_backup` snapshots. The regular
`bin\library.cmd` routine covers crop, junk handling, sorting, artist grouping,
Prospect regrouping, duplicate handling, and sync. The report generators then
provide the library gallery and comparison views.

Reports now live under `<work>\_reports\library`, `runs`, `comparisons`, and
`analysis`. The generated gallery last reported 207 people: 11 Angels, 10
Sisters, 115 Prospects, and 71 Artists. It shows the paired Sister, canonical
hair wording, and the top eligible Prospect alternatives for each paired
Angel. The separate report at
`<work>\_reports\comparisons\pairings\angel-prospect-candidates.md` contains
independent rankings for 10 Angel/Sister pairs; it is not a global assignment.
Candidate eligibility and scoring are described in [likeness.md](../art/likeness.md).

Promotion remains an explicit CLI operation shown as a preview command in the
gallery. The static HTML does not execute filesystem changes or guarantee that
a local folder link opens Explorer.

## Completed

- [x] Reorganize existing reports into purpose-based subfolders and update their generators, launchers, and documentation.
- [x] Generate the gallery with Angel-to-Sister context and top Prospect alternatives, plus the complete per-Angel candidate report.
- [x] Verify the focused report tests and quick repository validation; regenerate the report after the implementation.
- [x] Preserve the current generated report set for user review; no Angel promotion was applied.
- [x] Keep the current manual prompt drafts under `prompts/_edit/female` separate from generated prompt outputs and template inputs.

## Remaining work

Review of the gallery and Angel-to-Prospect rankings is consolidated under D10 in [the tooling-debt plan](2026-10-12-tooling-debt.md); use the refreshed reports after the Oct 19 library run.
- [ ] **P1 you** Finish and refine the manual edit-prompt set in `prompts/_edit/female`; tell the assistant when the batch is ready for review.
- [ ] **P2 ai** Once requested, compare the selected manual prompts and vocabulary against the existing JSON inputs, prompt templates, and generated prompts. Report what should map to new templates and what existing templates may be affected before editing them.
- [ ] **P2 either** After prompt review and approval, implement only the agreed template/data changes, regenerate the affected prompts and workflows, and verify that unrelated outputs remain unchanged.
- [ ] **P2 either** Continue the approved likeness/report follow-up after the user reviews the current gallery; do not automatically promote a Prospect or globally assign candidates from the independent rankings.
- [ ] **P3 you** Archive `prompts/_edit` only after the manual prompt work is finished and any accepted content has been incorporated or deliberately retained elsewhere.
- [ ] **P3 either** Continue the vocabulary audit in S5/S6 of [the prompt-template plan](2026-10-12-prompt-template-standards.md); keep `female_anatomy.txt` a user-maintained working reference until selected terms are reviewed.

## Raw request (Oct 15)

Record what you're doing with the likenss process to memory and create a
docs/plans/xxxxxx.md (following proper conventions) for what we have done and
some work left to do with respect to remaining work. Then - I am working on a
series of edit prompts and have several files I have staged and I would like
committed and pushed as they are in a decent spot right now and I want to be
able to track changes/history on them. I will circle back with the remainder
as I lock down on the prompts. Once I finish and eventually we'll just archive
this directory - but for now it's a working directory so I can save my manual
prompts and we'll need to review them and add apporpriate templates and address
some changes I'm making that will impact existing templates. It's easier to
fine-tune things manually and then we'll work on our prompt generation process
and templates. Hope all this makes sense and if you want to take a sneak peek
at the work I'm doing, that's fine. It's been a long process to get some of the
ordering and keywords right to trigger the right effects for the Qwen workflows.
