# 2026-10-22: independent photo-library upkeep

**Status:** holding (Oct 30 scheduling; delivered derivatives retained, broader integration acceptance open)

**Resume gate:** actual installed derivative/selected-input checks reveal a
specific defect, or baseline acceptance permits U1/U3/U6/U7 follow-through.
The current installation already uses these helpers; no independent upkeep
run or Production maintenance is authorized by this scheduling change.

## Oct 23 priority and implementation boundary

This is Phase 2 in the [library work order](README.md#current-library-work-order-oct-23),
downstream of [intake preparation I8](2026-10-23-image-intake-preparation.md).
U1/U3/U6 own output maintenance/recovery, not new enhancement algorithms or
cast release. Hook the accepted prepared source into this existing work rather
than create a second derivative generator. U2/U4/U5 retain independent scope.

The Oct 23 maintenance implementation passed 198 parent integration tests;
the FULL-backup follow-up passed 105 focused tests. Normal-temp quick validation
passed including 19/19 mutation cases. That implementation has since been
published, including synthetic prepared-source integration/undo coverage.
Real sandbox apply and user visual acceptance are not complete, so U1/U3/U6
remain open. U7 also retains direct `originals`/incremental ingest and selected
ComfyUI-input cutover: legacy `originals` still calls screenshot-cleaning
defaults, unlike the prepared installer and maintained derivatives. Use the
maintained route for verified prepared photos; do not generalize its cleanup
bypass to every old caller. The final Oct 23 large preview did not finish;
do not report a verified whole-library generation count or `IN SYNC`.

Routine/action recovery should omit only proven reproducible generated files.
The optional `library-backup.cmd --full --apply` includes generated outputs for
monthly snapshots; it still excludes the root backup/archive trees and is not
a backup of every historical archive or the proposed independent raw store.
Phase 1 must define protection of that raw store separately. Active Amelia
rename undo is not settled; the Draknoxa/Lia Joyce swap is not applied.

## Review and questions: 2026-10-22 16:21 -05:00

This plan retains unfinished library work that is neither matcher acceptance
nor prompt migration. No new blocking decision is needed for inventory.
The Oct 23 clarification below approves the chest derivative and post-action
refresh work (U1/U3). Ask before adding the near-duplicate report (U4).
No defaults, destructive cleanup or data migration are approved by this plan.

## Scope and decisions

Frames were retired Oct 19: no frame generation/input flow is to be revived.
The chest derivative is distinct from the old gray frame. The Oct 23 clarification
identifies standard 944x1104 derivatives as the intended ComfyUI inputs, not
native Gallery references. Existing full/head choices must be preserved;
complete chest selection/repoint/sync support remains U7, not an automatic
workflow retarget. Preserve originals and all user-selected input choices.
Junk is repair/resubmit; subjective quality and uncertain
identity are not reasons for automatic retirement.

| Source | Current destination |
| --- | --- |
| Oct 19 frame plan R9 | U1 |
| Oct 19 frame plan R11 | U2, retaining the dated inventory as a review lead only |
| Oct 12 Prime L4 | U3 |
| Oct 12 Prime L7 | U4 |
| Oct 19 management L1 | Engine acceptance E6, measurable usable/retirement criteria |
| Oct 19 management L5 | Manual actions A2/A4, retirement versus Junk and recovery |
| Oct 19 management L8 | Engine acceptance E8 plus U5, future intake and Demon pairing policy |

- [ ] **P1 ai** U1 Complete maintained padded/head/chest standard derivatives
  and derive both viewers' thumbnails from those outputs, with source/hash/
  recipe-aware invalidation and explicit missing/stale diagnostics.
  Cover Gallery/Review sources, varied framing and unprocessable photos.
  Coordinate with artist-crop A4; do not overwrite originals or infer workflow
  input changes. User visual acceptance of chest framing remains separate.
- [ ] **P3 you** U2 Review current photo outcomes using fresh inventories:
  Junk, Review, Various duplicates, replaced originals, protected multi-face
  Drakness images and recoverable duplicate archives. The Oct 19 snapshot
  recorded 6 junk, 3 older same-ID imports, 24 replacement originals,
  9 review and 332 archived duplicate files; these are historical leads,
  not today's counts. Decide salvage/manual resolution without deletion.
- [ ] **P1 ai** U3 Wire supported sandbox-aware post-action maintenance:
  folder-prefix normalization, padded/head/chest generation/check, then
  thumbnail/index/report refresh, without invoking matching. Provide preview,
  read-only check and repeat-safe execution through supported launchers.
  Preserve action apply/undo recovery across file-name/derivative changes;
  never merely rewrite tree hashes to bless an unknown transformation.
- [ ] **P1 ai** U6 Exclude proven regenerable outputs from routine snapshots,
  with sufficient provenance to recreate them. Preserve originals, histories,
  decisions, hand-edited assets and unrecognized/unproven derivative files.
  Verify full-library restore/rebase baseline behavior and action undo;
  narrow transaction snapshots are not proof broader backups omit images.
  Include optional FULL monthly-mode verification and Phase 1 raw-store scope.
  Regenerate from accepted prepared sources; stage valid replacements and
  prune/archive obsolete managed outputs so moved photos leave no stale images.
  Preserve unknown/edited outputs and do not erase a batch before replacements
  and rollback are verified.
  Oct 23 browser follow-up: routine snapshots can omit exactly manifest-owned
  People/Artist HTML and thumbnail bytes; manifests, face caches, original
  Gallery/Review trees, catalogue/history and retained preparation inputs stay
  included. Edited/unknown/unmanifested report files remain included; FULL and
  scoped transaction snapshots retain generated files. Restored browser reports
  are regenerated explicitly, separate from exact standard-derivative restore.
  Track thumbnail count/bytes on report generation and do not bless old assets
  as regenerable without reproducing the exact payload. User words are retained
  in [layout's Oct 23 authorization](2026-10-22-gallery-review-layout.md).
- [ ] **P1 ai** U7 Integrate accepted preparation with existing derivatives
  and selected ComfyUI inputs, coordinated with intake I12. Preserve full-photo
  fit/pad and head/chest framing; remove independent screenshot/source-cleanup
  crops for accepted prepared sources, including originals helpers, maintained
  chest rendering and viewer inspection. Recompute face coordinates for prepared
  bytes, version derivative recipes, preserve backup reproduction/undo and reject
  stale metadata. Verify full/head/chest selection, photo-ID rename/repoint and
  workspace input copying without silently changing selected framing or supplying
  native Gallery files. Test an end-to-end sandbox fixture through preparation,
  assignment, rename, generation, viewer and selected-input sync; include no-op,
  unsafe-overlay fallback, cross-identity moves, stale-output pruning and exact
  repeat. This step does not accept a preparation recipe or authorize production.
  Keep full/head/chest as explicit purpose-dependent reference choices, not a
  universal ranking: full for useful outfit/pose, head to reduce conflicting
  source-pose influence, chest for upper-body context. Record user ComfyUI
  comparisons as observations, not automatic switching rules; preserve fuller
  recoverable context when an upstream crop favors a tighter reference.
- [ ] **P3 ai** U4 If requested, report likely resized/re-encoded near
  duplicates within an identity with content/embedding evidence. A proposed
  0.98 face score is not accepted duplicate proof or deletion permission;
  byte-identical duplicate handling remains separate and recoverable.
- [ ] **P3 either** U5 Before future Demon automation, define counterpart
  mapping, direction-specific likeness/eligibility bands, global assignment
  conflicts and explicit swap permissions. Current Angels remain report-only
  replacement recommendations and user-chosen cast changes. Pairing fit cost,
  photo-count variety proxy and identity similarity are different measures.

## Historical context retained live

The current photo routine and recovery commands are in
[original photos](../art/original-photos.md) and [likeness](../art/likeness.md).
The Oct 19 snapshot/ingest/frame retirement record is in the
[library context reference](../art/library-reconciliation-context.md).
It distinguishes verified backups from incomplete failed ones, shots-only
pull from publication, ID replacements/duplicate archives from lost files,
and historical `IN SYNC` from unaccepted current matcher convergence.
No prior production run is silently replayed by this plan.

## Oct 23: derivative-backed gallery clarification

The latest request identifies an integration gap: report-only refresh did not
run originals normalization, and the viewer independently cropped originals
into small Chest-up/Head thumbnails instead of consuming standard derivatives.
Shared thumbnail cache delivery was not completion of the maintained
derivative-backed pipeline. Existing full snapshots also retained generated
outputs; only narrow action snapshots avoided those copies.

Use the identity folder prefix: fixed Angel/Sister slot names remain fixed,
while non-cast names follow their folder. Normalization must not silently
invalidate already applied rename/swap undo inventory guards. Implement and
verify the recovery boundary before external maintenance. This request does
not authorize global matching, production processing or applying the pending
Draknoxa/Lia Joyce swap.

### User feedback (verbatim)

<!-- markdownlint-disable MD013 -->
```text
So - when we are regenerating the gallery - what why am I not seeing the resulting _944x1104 images alongside the gallery images?  Also, they aren't being renamed ... are we skipping a step in the likeness process to manage the gallery?  The backups don't need to capture the _944x1104 to conserve space - but the gallery should get the files renamed to the identity and then generate the head, chest and cropped/padded images.  I thought that was always happening or is that a miss on what we're doing.

I would note that the gallery viewer should use those images to generate the thumbnails for the gallery.  I thought we had built that out already?

We can allow for an option to be a complete FULL backup including generated ones - that I can use for monthly full/complete backups - but for actions and normal backups where we're messing around with images we need to regenerate files.  Also - the regeneration needs to make sure it would remove existing images before generating a new batch so as photos move between identities we don't leave generated files for images that no longer are in the gallery for the identity.
```
<!-- markdownlint-enable MD013 -->
