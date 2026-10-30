# Daily recaps

Recaps are dated reflections and handoffs; [active plans](../plans/README.md)
own unfinished work and [todo.md](../todo.md) is the generated queue. This
index keeps the current resume handoff and still-relevant feedback visible,
and preserves chronological access to manually archived records.

## Pinned and current

| State | Recap | Why it remains active |
| --- | --- | --- |
| **Pinned — resume** | [2026-10-30-1247](2026-10-30-1247-recap.md) | Exact reboot, same-stage install and installed-viewer/recovery gates for the blocked v23 baseline. |
| **Pinned — feedback** | [2026-10-30-1234](2026-10-30-1234-recap.md) | Complete F01-F31 human-feedback coverage and next-round quality priorities remain relevant after baseline publication. |

“Pinned” is a manual index designation, not an automated workflow or an
acceptance claim. Keep a recap active while it has a unique current resume
state, unresolved user feedback, or decisions not yet transferred. The current
resume recap changes only when a later verified checkpoint supersedes it;
feedback recaps stay active while their decisions still need attention.

## Manual archive policy

Archive a recap only after an explicit reviewer (the user or an authorized
assistant) has:

1. Verified the checkpoint is superseded or no longer a safe current handoff.
2. Identified each unique outstanding decision, user request, blocker and
   resume detail, and recorded its live home below in this ledger (or kept the
   recap active if transfer is uncertain).
3. Checked that referenced active plans/canonical docs exist and still own the
   work; archival never means completion.
4. Used `git mv`, preserving historical prose while fixing relative links for
   the extra directory depth, added the exact file and transfer destinations
   to this chronological ledger, and retargeted links in active documents to
   the current recap or owning plan.

This is manual documentation housekeeping only. Nothing here automatically
pins, moves, deletes, or marks a recap complete. Do not archive raw feedback
through this process; follow the separate plan feedback-preservation rules.

## Archived recaps — chronological ledger

Each entry gives the reason the dated checkpoint is no longer an active
handoff and the verified live homes for its remaining decisions or tasks.
Older counts, run results and chronological details stay in the linked
historical record; task completion/status is determined by the owning plan.

| Date and archived record | Why archived; live context and task homes |
| --- | --- |
| 2026-10-12 — [artists reset and tooling recap](_archive/2026-10-12-1722-recap.md) | Superseded daily state. Remaining diagnostics/hygiene, atomic-write, Windows-suspension, ranking and false-identity deactivation work: [tooling debt D1, D4, D6-D11, D13](../plans/2026-10-12-tooling-debt.md); modularization/settings: [structure](../plans/2026-10-20-art-tools-structure.md), [engine](../plans/2026-10-22-likeness-engine-acceptance.md), and [manual actions](../plans/2026-10-22-review-actions.md). |
| 2026-10-20 — [library and prompt closeout](_archive/2026-10-20-0150-recap.md) | Its “manual prompts next” priority was superseded by later work order. Manual source/token review remains in [prompt migration](../plans/2026-10-22-manual-prompts-to-art-library.md); library cleanup, review and recovery in [upkeep](../plans/2026-10-22-library-upkeep.md); explicit identity/name choices in [family and naming](../plans/2026-10-22-identity-family-naming.md). |
| 2026-10-22 — [overnight implementation sequence](_archive/2026-10-22-0038-recap.md) | Later recaps and current plans supersede its evolving checkpoint. Convergence/protection/production gates: [engine acceptance](../plans/2026-10-22-likeness-engine-acceptance.md); family decisions: [family and naming](../plans/2026-10-22-identity-family-naming.md); action recovery/UAT: [review actions](../plans/2026-10-22-review-actions.md); presentation: [gallery layout](../plans/2026-10-22-gallery-review-layout.md); installed-trial evidence: [likeness sandbox trial](../art/likeness-sandbox-trial.md). |
| 2026-10-22 16:06 — [pause handoff](_archive/2026-10-22-1606-recap.md) | The 16:40 reconciliation and later follow-ups superseded its pause state. Scenario UAT, swaps and action recovery: [review actions](../plans/2026-10-22-review-actions.md); clean rebase/production boundary: [cast rebase](../plans/2026-10-23-cast-seeded-library-rebase.md); visual and identity acceptance: [current reboot recap](2026-10-30-1247-recap.md) and its linked owners. |
| 2026-10-22 16:40 — [plan reconciliation and rename follow-up](_archive/2026-10-22-1640-recap.md) | Later status and plans supersede the dated UAT handoff. Current swap/rename tests: [review actions](../plans/2026-10-22-review-actions.md); naming/family decisions: [family and naming](../plans/2026-10-22-identity-family-naming.md); prompt-source questions: [prompt migration](../plans/2026-10-22-manual-prompts-to-art-library.md); engine and production gates: [engine acceptance](../plans/2026-10-22-likeness-engine-acceptance.md). |
| 2026-10-23 17:08 — [intake and Artist GUI handoff](_archive/2026-10-23-1708-recap.md) | Its build-in-progress and UI preview state were superseded. Actual Gallery/Overview/Review/history UAT: [layout L12/L15/L17](../plans/2026-10-22-gallery-review-layout.md) and [current T16/I59 resume](2026-10-30-1247-recap.md); Artist scope/intake acceptance: [image intake](../plans/2026-10-23-image-intake-preparation.md). |
| 2026-10-23 21:21 — [visual UAT and preparation evidence](_archive/2026-10-23-2121-recap.md) | Old v8-v12 experiment outcomes are dated evidence, not the current recipe or acceptance. Mask/reconstruction/crop and human-quality work: [intake I18-I20, I30-I37, I68-I70](../plans/2026-10-23-image-intake-preparation.md); retained-detail viewer and report I/O: [layout](../plans/2026-10-22-gallery-review-layout.md); T11's older comparison is transferred to [intake I68/I69](../plans/2026-10-23-image-intake-preparation.md). |
| 2026-10-24 — [crop sequence and named folders](_archive/2026-10-24-0300-recap.md) | v14/v15 implementation state was superseded by later recipes and real rebase work. Remaining version/retention, named-drop and cutover questions: [intake](../plans/2026-10-23-image-intake-preparation.md) and [upkeep U7](../plans/2026-10-22-library-upkeep.md). |
| 2026-10-25 06:00 — [v16 intake and modular package](_archive/2026-10-25-0600-recap.md) | Early v16 and initial clean-start integration were superseded by later measured runs. Current crop/recipe review: [intake](../plans/2026-10-23-image-intake-preparation.md); real prepared install: [cast rebase](../plans/2026-10-23-cast-seeded-library-rebase.md); incremental/source cutover: [upkeep U7](../plans/2026-10-22-library-upkeep.md); Python/CI compatibility: [tooling D14/D20](../plans/2026-10-12-tooling-debt.md). |
| 2026-10-25 16:25 — [review-first handoff and art-doc audit](_archive/2026-10-25-1625-recap.md) | Later run evidence and plan-level ownership replace this multi-stream handoff. Prepared-input and visual acceptance: [intake](../plans/2026-10-23-image-intake-preparation.md); real install: [cast rebase](../plans/2026-10-23-cast-seeded-library-rebase.md); derivatives: [upkeep](../plans/2026-10-22-library-upkeep.md); protection/family: [engine](../plans/2026-10-22-likeness-engine-acceptance.md) and [family](../plans/2026-10-22-identity-family-naming.md); gallery UAT: [layout](../plans/2026-10-22-gallery-review-layout.md); broader non-art document review: [tooling D13](../plans/2026-10-12-tooling-debt.md). |
| 2026-10-26 01:15 — [overnight rendering checkpoint](_archive/2026-10-26-0115-recap.md) | Run-in-progress and queue snapshots are obsolete. Render acceptance, batching and retained-output choices remain in [reference rendering](../plans/2026-10-25-reference-rendering.md); intake/rebase gates in [intake](../plans/2026-10-23-image-intake-preparation.md) and [cast rebase](../plans/2026-10-23-cast-seeded-library-rebase.md). |
| 2026-10-26 10:04 — [pilot results and intake interruption](_archive/2026-10-26-1004-recap.md) | Pilot receipts remain historical; the interrupted partial preparation was superseded by later complete runs. Human pilot review and render lineage: [reference rendering R6/R16](../plans/2026-10-25-reference-rendering.md) and [prompt migration P11/P12](../plans/2026-10-22-manual-prompts-to-art-library.md); current full-baseline acceptance: [cast rebase](../plans/2026-10-23-cast-seeded-library-rebase.md). |
| 2026-10-26 16:30 — [Outputs browser and pullback](_archive/2026-10-26-1630-recap.md) | Browser/pilot checkpoint is superseded by later output and queue work. User review of rendering, queue and pulled outputs: [reference rendering](../plans/2026-10-25-reference-rendering.md); cleanup preparation and quality acceptance: [image intake](../plans/2026-10-23-image-intake-preparation.md). |
| 2026-10-26 17:00 — [combined Oct 24-26 work and review list](_archive/2026-10-26-1700-recap.md) | Its broad review list and running-job statuses were reconciled into owners and later checkpoints. Intake examples/recipe gates: [I30-I37 and I68-I70](../plans/2026-10-23-image-intake-preparation.md); ComfyUI source fidelity, routing and user review: [reference rendering R6/R21/R27/R35/R37/R44](../plans/2026-10-25-reference-rendering.md) and [prompt migration P14-P17](../plans/2026-10-22-manual-prompts-to-art-library.md); rebase: [cast plan](../plans/2026-10-23-cast-seeded-library-rebase.md). |
| 2026-10-29 06:20 — [Oct 27 retrospective](_archive/2026-10-29-0620-recap.md) | Its named recipe failures and review guidance were incorporated into current intake work. Bounded reproduction, controls, masks and visual acceptance: [intake I30-I37 and I68-I70](../plans/2026-10-23-image-intake-preparation.md); pre-install cast review: [cast rebase](../plans/2026-10-23-cast-seeded-library-rebase.md). |
| 2026-10-29 06:21 — [Oct 28 retrospective](_archive/2026-10-29-0621-recap.md) | Run-throughput/storage measurements are historical; open decisions remain explicitly owned. Run retention and backup/storage budgets: [storage S24/S25](../plans/2026-10-28-storage-operations-and-retention.md); recipe-aware timing: [performance T17](../plans/2026-10-28-intake-performance.md); cast/user review: [cast rebase](../plans/2026-10-23-cast-seeded-library-rebase.md). |
| 2026-10-29 07:12 — [fresh reset checkpoint](_archive/2026-10-29-0712-recap.md) | The reset and active intake snapshot were superseded by the completed v23 baseline. Same-stage install and viewer gates: [cast rebase C6/C7](../plans/2026-10-23-cast-seeded-library-rebase.md), [storage S15](../plans/2026-10-28-storage-operations-and-retention.md), and [current resume](2026-10-30-1247-recap.md). |
| 2026-10-29 09:40 — [overlay-first performance handoff](_archive/2026-10-29-0940-recap.md) | The v22 profile and fresh-chat handoff are no longer the current resumption state. Verified performance behavior and later measurements: [performance T5/T6/T16/T17](../plans/2026-10-28-intake-performance.md); reconstruction semantics: [intake I68/I69](../plans/2026-10-23-image-intake-preparation.md); test selection/hygiene: [tooling D21](../plans/2026-10-12-tooling-debt.md). |
| 2026-10-30 09:22 — [recovery and matching pause](_archive/2026-10-30-0922-recap.md) | Superseded by the resumed and audited 11:57 state and current 12:47 handoff. Completed-stage recovery/install: [performance T16](../plans/2026-10-28-intake-performance.md), [cast C6/C7](../plans/2026-10-23-cast-seeded-library-rebase.md), and [storage S15](../plans/2026-10-28-storage-operations-and-retention.md). |
| 2026-10-30 11:57 — [stage verified; Explorer blocked installation](_archive/2026-10-30-1157-recap.md) | The exact rollback receipt, stage, backup and reboot sequence are now summarized in the active [12:47 resume recap](2026-10-30-1247-recap.md); detailed stage/timing evidence remains in [performance T16](../plans/2026-10-28-intake-performance.md) and [cast C6/C7/C10](../plans/2026-10-23-cast-seeded-library-rebase.md). |

The archive links above are for historical inspection, not active task
authority. For the next action, use the [current resume](2026-10-30-1247-recap.md)
and its owning plans.
