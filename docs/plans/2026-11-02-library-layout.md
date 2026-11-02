# 2026-11-02: library directory layout - separate galleries from intake/processing

**Status:** active (LY1 decided Nov 2: all five recommendations accepted)

**Queue focus:** LY2, LY3

**Order:** LY2/LY3 (code + tests) -> LY5 -> LY4 clean sandbox reset and LEAN
rebase on the new layout, timed with Acronis off -> storage S32/S27 acceptance
-> retire the old sandbox `_backup` snapshot and `fresh-v23` run state. No full
intake runs on the old layout. Production writes remain gated by the existing
acceptance plans.

Owners kept elsewhere: storage
[S32/S33](2026-10-28-storage-operations-and-retention.md) (replay method and
`gallery_intake` compaction), gallery
[L19/L20](2026-10-22-gallery-review-layout.md) (navigation, intake-run
retention). This plan owns only *where* things live and the migration to it.

## Current structure (measured Nov 2, stat and manifest reads only)

Sandbox `B:\Sovereign Territories Sandbox\Working`, 282 person/pool folders:

| Per-person folder | Role | People | Files | GB |
| --- | --- | ---: | ---: | ---: |
| `gallery` | accepted native photos, `z_<name>.txt` profile/history | 273 | 3,213 | 1.39 |
| `review` | photos the matcher is unsure about | 15 | 99 | 0.06 |
| `gallery_944x1104`, `headshot_944x1104`, `chest_944x1104` | maintained 944x1104 ComfyUI/viewer copies | 269/261/202 | 8,522 | 7.93 |
| `review_gallery_`/`review_headshot_`/`review_chest_944x1104` | the same for Review photos | 15 | 286 | 0.27 |
| `.photo-derivatives.json` (file) | derivative source/output hashes and recipe | 203 | - | small |
| `gallery_org\<set-key>` | exact incoming original bytes | 203 | 2,793 | 0.45 |
| `gallery_intake\<set-key>` | per-photo processing history: variants, padded copies, masks, thumbnails, `manifest.json`, `detail.html` | 203 | 34,567 | 23.96 |

So one person folder can hold up to 10 entries; about 72% of the bytes and
76% of the files under person folders are processing history, not gallery.
`gallery_intake` is current functionality (written by every install), not
leftovers. By role: never-selected `tone`/`denoise` alternatives 14.8 GB,
`control` 4.11 GB (2,036 of 2,793 rows selected the unchanged original),
selected-step native/padded copies about 2 GB, masks/thumbnails/manifest/detail
under 0.6 GB (see storage S33).

Top level of the sandbox: `_backup` 42.0 GB (one FULL snapshot), `_sandbox-state`
33.0 GB (run `fresh-v23-20261029`, whose `inputs\_reports\preparation\all` holds
the same variants that install **copied** into `gallery_intake`), `_reports`
1.2 GB, `_retired` 0.5 GB, `_likeness` 0.07 GB.

Production `B:\Sovereign Territories` still has the **older** layout: per person
only `gallery` (0.48 GB), `gallery_944x1104` (2.43 GB), `headshot_944x1104`
(2.20 GB) and occasional `review`; no `gallery_org`, `gallery_intake` or chest
copies yet. Top level: `_backup` 14.0 GB, `_archive` 6.5 GB, `_reports` 0.3 GB,
`_retired` 0.5 GB. Production therefore needs no migration of processing
history: whatever layout we agree is what the first accepted install creates.

## Problems with the current layout

- Inputs, processing evidence and outputs are mixed per person; browsing a
  person shows 6-10 folders where the user cares about `gallery`/`review` and
  the 944x1104 workflow copies.
- Processing history is owned by a person folder although its key is not:
  the 32-hex set key covers source hash, source path, photo ID, domain and
  recipe, never the owner. Every move between people, Review approval, Junk,
  retirement or undo must therefore physically transfer the original and
  every artifact (`plan_transfer`/`execute_transfer`, about 12-25 files per
  photo) and rewrite manifest and detail. That is most of the move/undo
  complexity in `actions.py` and `maintenance.py`, and the reason whole-person
  renames/merges with retained sets are currently held.
- Install copies variants from the run tree into `gallery_intake`, so the same
  bytes exist in the run (`_sandbox-state`), the library and the backup.
- Backup scope has to special-case `gallery_org`/`gallery_intake` inside
  person folders (`library_backup.py`).

## Proposed target layout

```text
<library root>\
  Angels\Angelica\
    gallery\                    accepted photos + z_angelica.txt         (unchanged)
    review\                     photos to look at                        (unchanged)
    944x1104\                   [LY1-b] maintained workflow copies
      full\  head\  chest\        from gallery
      review\full\ head\ chest\   from review
      .photo-derivatives.json
  Various\gallery, review         unassigned pool (unchanged role)
  _processing\<domain>\<set-key>\ original.ext, variants, masks, thumbnails,
                                  manifest.json, detail.html   [LY1-a]
  _processing\<domain>\index.json  photo ID / current hash -> set key (rebuildable)
  _sandbox-state\<run>\           run workspaces (inputs, preparation reports)
  _reports\                       viewers and run reports (unchanged)
  _backup\ _likeness\ _actions\ _junk\ _retired\ _tmp\   (unchanged roles)
```

`_processing` becomes a new configured `storageRoots` entry like the others.
`<domain>` keeps the general/Artist matching boundary physical. A person folder
then holds only `gallery`, `review` and one derivative folder.

Effects:

- Moves, Review approval, Junk, retirement and undo touch only the gallery
  photo, its derivatives and one manifest field (`current`) plus detail
  navigation; no evidence bytes move. Whole-person renames/merges stop being
  blocked by retained sets.
- Backups can treat `_processing` as its own scope (back up once, then
  incrementally; it is append-only per set).
- Install can **move** the selected row's artifacts from the run into
  `_processing` on the same volume instead of copying (LY1-d), removing one of
  the three copies; the run receipt then points at the published set.
- S33 compaction (dropping unselected `tone`/`denoise`/`control` copies)
  applies in the same migration pass, so manifests and detail pages are
  rewritten once, not twice.

## Code impact (measured Nov 2)

Path construction is already centralised: `retained_preparation.py` (775
lines) builds every `gallery_org`/`gallery_intake` path and `derivatives.py`
(219 lines) builds every 944x1104 path through `relative_target`. Python under
`tools` is 189 files / 65k lines with 72 test files.

| Area | Modules (call sites) | Change | Size |
| --- | --- | --- | --- |
| Processing store paths, lookup, index | `retained_preparation.py` (`stage_photo`, `owned_files`, `claims_photo`, `verify_link`, `refresh_detail`, `rename_photo`, `plan/validate/execute_transfer`) | root-level paths, index, transfer reduced to manifest/detail update | medium-large |
| Moves and undo | `likeness_library/actions.py` (8), `maintenance.py` (10) | simplify; keep reading journals written in the old layout | medium |
| Install/replay | `clean_rebase.py` (6), `library_rebase_replay.py`, `library_storage_experiment.py` | publish into `_processing`; optional move-not-copy | medium |
| Backup/restore | `library_backup.py`, `library_backup_archive.py` | new scope; restore of old snapshots keeps old layout, then migrate | small-medium |
| Small path users | `originals.py`, `identity_maintenance.py`, `likeness.py` (`crop_guard`), `preparation_history.py`, `preparation_provenance.py` | follow new API | small |
| Derivative grouping (LY1-b only) | `derivatives.relative_target`, `gallery_maintenance.py`, `review_gallery.py`, `reference_gallery.py`/`reference_rendering.py` folder lists, `identity_maintenance.py`, `originals.py`, ComfyUI input sync | folder names only; workflow input names unchanged | small-medium |
| Tests | 5 files test intake/org/transfer directly; layout fixtures in more | update + new migration tests | medium |
| Migration tool | dropped (see Decisions): a clean reset and rebase builds the new layout; tools refuse the old one | - |
| Docs | `docs/art/original-photos.md` layout, `likeness.md`, gallery/storage plans | rewrite layout sections | small |

Rough effort: the processing-store move (LY2-LY4) is about three focused
working sessions including tests and the sandbox rehearsal; derivative
grouping (LY5) about one more. These are estimates, not measurements. The
migration itself is cheap on disk: same-volume renames, no new copies, and
S33 compaction frees roughly 19 GB in the same pass.

Risks: old backups and action journals use the old layout (keep a read-only
compatibility reader or migrate them explicitly); Acronis must exclude the
library scratch areas before ~37k renames; detail links change depth and need
the existing hash-checked rewrite.

## Decisions (LY1, Nov 2)

| | Decision |
| --- | --- |
| a | Processing history lives in `_processing\<domain>\<set-key>`, not in person folders |
| b | The six 944x1104 folders become one `944x1104\{full,head,chest,review\...}` folder per person |
| c | `Various\gallery` stays the drop zone |
| d | Install **moves** the selected run artifacts into `_processing` instead of copying |
| e | LEAN retention keeps only what a set needs: original, selected-step native/padded output (aliased when byte-identical), masks, thumbnails, manifest, detail. No never-selected `tone`/`denoise` alternatives and no `control` copy equal to the original |

**No migration of the 2,793 legacy sets.** Production has no retained sets, and
the existing `likeness sandbox-reset --full` rebuilds Working from production
while the 89 unique photos and 17 metadata files travel in
`_reports\reset-review-bundle`. A clean rebase therefore creates the new layout
directly. LY4 shrinks to refusing/detecting the old layout plus that reset and
rebase procedure; the separate migration tool is dropped.

## Modes: two separate axes

| Axis | Values | Owner | Decides |
| --- | --- | --- | --- |
| Storage | FULL / LEAN / COMPACT / COLLAGE | [storage](2026-10-28-storage-operations-and-retention.md) | which computed bytes are **kept** |
| Processing | FULL / FAST / OVERLAY-ONLY | performance [T18](2026-10-28-intake-performance.md), intake [I70](2026-10-23-image-intake-preparation.md) | which steps are **computed** |

Decision (e) tightens LEAN (storage): it no longer keeps unselected
alternatives. It does not change what is computed. The recipe treats
enhancement as comparison-only (never selected), so computing `tone`/`denoise`
is pure cost under LEAN; whether to stop computing them is a T18/I70 processing
decision that needs user approval, not part of this plan.

## `_` directories (hash audit Nov 2, Acronis off)

All 70,913 files in production and the sandbox active stores were SHA-256
hashed (185 s; production 27 GB read at about 180 MB/s).

| Library | Folder | Finding | Action |
| --- | --- | --- | --- |
| Production | `_archive` 6.5 GB | 10k exact copies of active/backup photos, 1,330 old 944x1104/headshot copies, 195 unique `gallery_uncropped` pre-crop originals, Workflows, scripts, Oct 11 manifest | **Done Nov 2:** copies and scaled files removed; the 603 unique files stay in place (0.11 GB left) |
| Production | `_backup\library-20261014-162634` 2.7 GB | earlier "2,617 unique" now all matched in active galleries, regenerable scaled copies, or 174 unique metadata/report files | **Done:** removed; the 174 unique files are in the ZIP below |
| Production | `_backup\_packed` (Oct 19 bundle) 5.2 GB | 0 unique photos; 25 unique members | **Done:** removed; members in the ZIP below |
| Production | `_backup\library-20261020-222038` 5.6 GB | newest snapshot; now the **only** copy of about 2,100 older files (`Potentials`, `_reports`, ComfyUI inputs) | keep; never retire without its own audit |
| Production | `_reports`, `_retired`, `_junk` | current/user-dispositioned | keep |
| Sandbox | `_reports\library-performance-20261031` 231 MB | regenerable viewer from the timed run; timing recorded in the gallery plan | **Done:** HTML/thumbnails removed; manifest and `RETIRED.json` kept |
| Sandbox | `_backup\library-20261029-235003` 42 GB, `_sandbox-state\fresh-v23-20261029` 33 GB | sole FULL snapshot and run state of the current sandbox | retire after the clean rebase is accepted, keeping JSON receipts |
| Sandbox | `_reports\reset-review-bundle`, `storage-experiments` | carried metadata, durable evidence | keep |

Production went from about 27 GB to 10.9 GB: 12,988 files and 14,340,483,967
bytes were removed after re-hashing every target and survivor. The receipt,
plan, script and verified `retained-metadata.zip` (199 files) are in
`B:\Sovereign Territories\_reports\storage-retirement-20261102`; the read-only
check passed afterwards.

## Steps

- [x] **P1 you** LY1 Decide the layout: (a)-(e) accepted Nov 2, see Decisions.
- [ ] **P1 ai** LY2 Implement the `_processing` store in `retained_preparation.py`
  (new `processing` storage root, per-set manifest with `current` path, a
  rebuildable lookup, manifest-only transfers, LEAN retention per (e)) and
  refuse the old in-person layout; focused regressions first.
- [ ] **P1 ai** LY3 Update install/replay (move, not copy), backup scope and small
  path users to the new API; run the affected test files.
- [ ] **P1 ai** LY4 Reset the sandbox from production (`sandbox-reset --full` plus
  the carried bundle), run the clean LEAN rebase in place with per-step timings
  (Acronis off), verify Gallery/Overview/Review, then hand to storage S32/S27
  and retire the old sandbox snapshot and run state.
- [ ] **P2 ai** LY5 Group derivative folders (LY1-b) and update
  viewers and ComfyUI input sync; verify `sync-inputs` output names unchanged.
- [ ] **P2 ai** LY6 Rewrite the layout sections in `docs/art/original-photos.md`
  and `likeness.md`; production adopts the layout at its first accepted install.

## User request (chat, verbatim)

Nov 2 11:48, coverage: separation of intake/processing from galleries and
reports -> target layout and LY1; analysis of current/future structure and
script effort -> the measured sections above; timing with the sandbox work ->
resume gate before S32/S27.

<!-- markdownlint-disable MD013 -->
````text
We may want to revisit the directory structure again - after you figure this out and possibly separate things out a bit in terms of what ends up in the gallery at the end.  I do think after we've been working on it that some of the generated files from intake or processing might need to be outside the person's directory and we focus on having just the gallery files.  Right now we're mixing up the intake/original and the output gallery files in a single structure.  I did want to revisit our structure as part of the sandbox work - so now seems like a good time to do that.  If we have some place for intake files and the processing of them separated from reports and from galleries - we can still move files around and we adapt things a bit.  But I need much more analysis of the current structure - future structure and just how big an effort this is with all the scripts we have.
````
<!-- markdownlint-enable MD013 -->

Nov 2, coverage: agreement -> LY1 checked and Decisions; old `_` directories
in sandbox and production -> the audit table and the Nov 2 retirement; clean
sandbox by full reset/re-run with timings while Acronis is off -> Order and
LY4; keep separation and only needed files (LEAN vs FULL/FAST) -> decision (e)
and the Modes section; plan alignment -> cross-links in storage, performance and
intake plans.

<!-- markdownlint-disable MD013 -->
````text
I agree with the recommendations - and we can also revisit existing _ directories in the sandbox and production for things that are also old and no longer used or useful due to all the changes.  So, we can get the sandbox into a clean state - and I know that might mean a full rebase and re-run, but that's what I want to see in the long run.  Since I have Acronis disabled now - I am hoping that the process is actually faster and all out timings will help.  Ultimately, keeping the separation, but still having files exist for references will help in the long run and only keep files generated we need.  That was all part of the LEAN type processing we were doing vs. FULL and FAST ... so we'll need to re-read and sync up all these items along with that existing plan and bring all the docs/plans into alignment and ensure directory structure makes more sense.
````
<!-- markdownlint-enable MD013 -->
