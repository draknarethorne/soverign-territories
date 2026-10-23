# Library reconciliation: dated pairing and frame-retirement context

**Preserved:** 2026-10-22T16:34:08-05:00. Historical evidence, not current counts or a
new instruction to ingest, pair or retire anything. [Upkeep](../plans/2026-10-22-library-upkeep.md)
owns remaining chest-crop/Junk/refresh work. [Engine acceptance](../plans/2026-10-22-likeness-engine-acceptance.md)
owns current quality criteria and incremental validation. [Action work](../plans/2026-10-22-review-actions.md)
owns retirement semantics; [current guide](likeness.md) owns executable syntax.

## Pairing boundaries

Current Angel changes are explicit user choices, not automatic swaps.
The Oct 19 production migration applied only 135 category moves after a
verified backup; identity/Junk proposals remained report-only. The four
cast choices were Aria Muse to Gavrielle, Ruby Eden to Camaris, Amethyst
Montgomery to Ravaelle and Sabine Vale to Nyxene. These historical choices
do not authorize a new swap or identify every photo in their galleries.

## Pairing score

Candidate selection is two-stage and shared by the global pairing command,
People Gallery, candidate report, and rebaseline preview:

1. **Eligibility:** at least five usable photos and 0.45 cohesion.
2. **Ranking:** likeness-fit cost against the configured counterpart, adjusted
   by a small variety proxy: subtract 0.02 at 10 usable photos, 0.04 at 15,
   and 0.06 at 20 or more. The target is 0.28 within the preferred 0.15–0.40
   band; a photo bonus cannot qualify an out-of-band replacement. Global
   pairing additionally avoids assigning one person twice and penalizes
   likeness clashes between selected candidates.

This gives larger photo groups an edge when likeness fits are reasonably
close without treating photo count as identity evidence. It does not measure
distinct poses or outfits. The score is faction-neutral: future Demon-to-
counterpart pairings can reuse it once their counterpart mapping and any
direction-specific likeness band are decided.

## Oct 19 ingestion and frame-retirement evidence

### Historical Oct 19 state

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
