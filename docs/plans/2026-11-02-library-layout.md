# 2026-11-02: library directory layout - separate galleries from intake/processing

**Status:** active (LY1 decided Nov 2: all five recommendations accepted; LY2,
LY3 publication/undo and LY5 implemented and tested Nov 2)

**Queue focus:** LY11, LY13, LY14, LY12, LY9, LY6, LY8

## Nov 3: authorized new source rehearsal

The 12:46 request selects naming N14/LY13, cast C11/engine E13/E14 and
recap L21-L23 as tested prerequisites to a separate complete fresh rebase.
Copy current Production through full reset; do not use installed
`fresh-20261102` identities as inputs. The reset's processed-copy provenance
excludes old generated pixels when the original remains in Production;
genuinely unique sources and review metadata stay preserved. Compact prior
run/catalogue/policy JSON is carried into the reset-review bundle for
historical recap comparison only, never auto-applied or used as match seeds.

LY12 report-state integration now uses shared gallery publication after
install, in addition to the previously tested content-ID naming slice.
The core trial, bounded in-place refinement (engine E15, added 14:17) and
final-membership audit are explicit run-local behavior;
ordinary defaults stay unchanged. Broader convergence beyond the four-pass
refinement, surname-rule acceptance and Production true-up remain gated with their
owners. LY10 stays open through fresh reset, intake, actual release/name
preview, install and Gallery/Overview/Review/recap checks. See the
[exact runbook](../art/likeness.md#fresh-sandbox-from-production-step-by-step).

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

**Implementation notes (Nov 2).**

- (a) as built: sets live at `_processing\<owner path>\<set-key>` (for example
  `_processing\Angels\Angelica\<32 hex>`), mirroring the person path instead of
  a `<domain>` index. Ownership stays obvious, clean-rebase install/undo moves
  `_processing\<category>` together with its category, and no separate lookup
  must be rebuilt. Whole-person rename/merge still holds while a person owns
  sets (unchanged behavior). The old in-person `gallery_org`/`gallery_intake`
  layout is refused (`LegacyLayoutError`), never migrated.
- (b) as built: `<person>\944x1104\{full,head,chest}` and
  `944x1104\review\{full,head,chest}`, with `.photo-derivatives.json` inside
  `944x1104` (keys still relative to the person folder). File names are
  unchanged (`<stem>_944x1104.png`, `<stem>_head_944x1104.png`), so the
  generated workflows and `sync-inputs` names are unaffected. Every
  `originals` run first moves the former folders by rename (byte-identical
  duplicates dropped, different files kept and reported, the manifest moved
  with rewritten keys), so production's 335 `gallery_944x1104`/
  `headshot_944x1104` folders move without regenerating about 5 GB.
  `originals --check` reports anything still to move. Workflow-input discovery
  (`photo_library`/`headshot_library`) falls back to the former folder names
  until then; viewers and likeness read only the new layout.
- (d) not yet built: install still copies the selected artifacts from the run
  into `_processing`; with LEAN only the selected/needed artifacts are copied,
  and the run's `inputs` mirror is retired after acceptance. Tracked as LY3b.

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
- [x] **P1 ai** LY2 Implement the `_processing` store in `retained_preparation.py`
  (new `processing` storage root, per-set manifest with `current` path,
  manifest-only transfers, LEAN retention per (e)) and refuse the old in-person
  layout; focused regressions first. Done Nov 2 (owner-path layout, see notes).
- [x] **P1 ai** LY3 Update install/undo/check, backup scope and small path users
  to the new API; run the affected test files. Done Nov 2.
- [ ] **P2 ai** LY3b Install moves the selected run artifacts into `_processing`
  instead of copying (decision d), keeping the run's undo/replay receipts valid.
- [ ] **P1 ai** LY4 Reset the sandbox from production (`sandbox-reset --full` plus
  the carried bundle), run the clean LEAN rebase in place with per-step timings
  (Acronis off), verify Gallery/Overview/Review, then hand to storage S32/S27
  and retire the old sandbox snapshot and run state.
  Progress Nov 2 (run `fresh-20261102`, Acronis off), timings in seconds:
  reset preview 221, reset apply 314, `originals` migration 103, backup 83
  (10,550 files, 6.56 GB), rebase dry run 47; intake of 3,093 images started
  14:48 with 3 CPU-bound workers (about 17 images/min). Fixes found by the run:
  the full reset no longer carries regenerable output (43,623 files, 32.2 GB)
  or the 757 processed copies of production originals (`190c0e77f`), and
  directory publishes retry scanner locks for up to about 30 s after a
  repeatable `WinError 5` on the source-overlay rename (`deac77b52`). The first
  intake then stopped ordering rows after image 759: removing a worker's
  scratch folder hit the same scanner lock, and the process pool silently
  drained all queued images before reporting. Scratch removal now retries and
  a failed ordered publish cancels queued work (`0e50eb5f4`); the resumed run
  recovered all 1,267 per-image checkpoints (T6 recovery confirmed live).
  At 1,738 the same removal met `WinError 145` (a scanned file still pending
  delete leaves its folder "not empty"); that is now retried too
  (`dc019ce33`), and the second resume recovered 1,744 checkpoints.
  Intake took about 1,890 + 4,896 s; then check 225, preview 1,025 and replan
  485. The first apply refused an ambiguous ID for byte-identical copies
  (fixed `91a7a992a`); attempt 1 spent 77% of its time reloading the workflow
  configuration once per retained set (prefix hoisted, `030259282`) and was
  stopped; attempt 2 staged about 184 photos/min but died with a session
  restart (long runs are now detached). Both kept their `staged`/`previous`
  as `*-attemptN-interrupted` with a receipt; Working was untouched. Attempt
  3 started 21:16 with `--preserve-legacy-derivatives` and finished 04:49
  (exit 0, 27,180 s): about 25 min staging, 2 h 50 min scaled copies (8,000+
  `944x1104` files), 1 h 50 min detail-page refresh, 40 min hashing and safety
  checks, 2 h 15 min Review/People/intake gallery rebuild; 354 GB read in
  total for about 26 GB of data (LY9). Applied: 2,814 photos (stayed 1,904,
  moved 792, moved to Review 96, to Review 22), 749 renamed, 118 in Review,
  68 new identities, 73 emptied; person folders hold only
  `gallery`/`review`/`944x1104`, no `gallery_intake`/`gallery_org` remain,
  `_processing` holds all six categories. Diagnostics: 120 head crops not
  reproducible from the cached face box and 3 photos without a usable face
  (padded copy only). Cast: nothing left Angels/Sisters (all-seeds mode); all
  79 cast gains from Various/Potentials/Prospects are in that cast member's
  Review. Finding for review: a pre-existing `Potentials\Camaris` identity
  (5 photos, nearest Drakniss 0.20) was promoted to `Prospects\Camaris`, so
  two identities share the Angel name Camaris. After install, `--check` runs
  without `--preserve-legacy-derivatives` (with it the check selects the
  unpublished-plan recovery preview and is refused); runbook corrected.
  Decided Nov 2 (chat): the run must go all the way in the sandbox (every move
  and rename applied) so the outcome can be reviewed in the galleries; the
  review aid is automatic and repeatable, not one-off: every
  `sandbox-rebase.cmd` step writes `_reports\library\rebase-recap\<run>.html`
  plus an index (moves, renames, Review holds, cast gains/losses, new
  identities by surname with nearest cast member, comparison with other runs
  of the same inputs), and the user's look-alike picks and expected photo
  placements live in `rebase-expectations.json` beside Working, scored on
  every recap. Cast matches stay in Review for this run; tuning (whether
  low-score supplements join Angels/Sisters) follows the user's review.
- [x] **P2 ai** LY5 Group derivative folders (LY1-b) and update
  viewers and ComfyUI input sync; verify `sync-inputs` output names unchanged.
  Done Nov 2: names unchanged by construction; rename-only migration in
  `originals`.
- [ ] **P2 ai** LY6 Rewrite the layout sections in `docs/art/original-photos.md`
  and `likeness.md` (layout and retained-storage text updated Nov 2) and add the
  fresh-sandbox step-by-step runbook, confirmed by the LY4 run; production
  adopts the layout at its first accepted install.
- [x] **P1 ai** LY7 Leave Artists out of the sandbox: `sandbox-reset --full`
  neither copies Production `Artists` nor carries sandbox Artists forward
  (`--include-artists` opts back in), so they are never copied or prepared.
  Done Nov 2 for the next fresh sandbox; the current `fresh-20261102` run
  already prepared its 279 Artists images before the decision and matching
  ignores them. The Production-side Artist scope stays with intake I74.
- [ ] **P1 either** LY8 Production true-up before the first direct Production
  clean rebase: inventory Production for the old in-person layout
  (`gallery_944x1104`/`headshot_*`, `gallery_intake`, `gallery_org`,
  `.photo-derivatives.json`), stale `_` directories and fragmented or
  unnecessary files; decide per class (migrate by `originals`, move to
  `_processing`, retire with a backup, or leave); write the runbook for
  running directly in Production. Gate: the fresh sandbox run (LY4) accepted,
  so the same classification rules are proven there first.
- [ ] **P2 ai** LY9 Cut repeated verification in apply (attempt 3 read 354
  GB for about 26 GB of data and took 7.5 h): load the workflow configuration
  once per pass (`verify_link`, `_set_folder`, `_detail_navigation` still call
  `cw.load_cfg` per photo); memoise per-folder derivative manifests and
  `source_is_prepared` within a pass (detail refresh slowed from 40 to 20
  pages/min as folders grew); reuse digests already verified in the same
  transaction instead of re-hashing; hash person trees once per gallery build
  (`person_rename.tree_hash` per item); print one progress line per phase so
  a long apply is checkable without a profiler. Call-count regressions for each. The
  read-only `bin\people-gallery.cmd ... --check` (Nov 3, over 1.5 h, silent log) sits
  in the same `derivatives.maintain` -> `verified` -> `verify_link` -> `_manifests`
  chain, so it benefits too. Gate: attempt 3 checked (the engine is in the run's
  implementation hashes).
- [x] **P2 either** LY10 Read-only `--cast-seeds core` comparison in a
  separate run directory, so the recap shows who would leave Angels/Sisters
  under core seeds; first measure whether a new run must repeat intake (about
  1.9 h) or can reuse `fresh-20261102` inputs. Nov 3: with today's code a core run
  releases nothing, because 20 of 21 cast identities are catalog-protected; run it
  with [cast C11](2026-10-23-cast-seeded-library-rebase.md) semantics. Gate: attempt
  3 checked; C11 approved.
  Result (Nov 4): run `fresh-20261103-core` reset from Production, full intake
  (197 min), matched preview, refinement and audit, then installed (309 min) and
  checked (exit 0). 153 photos left cast members, 64 cast gains in cast Review,
  Drakness -> Nyxene 4. Recap/Gallery/Review pages verified in a browser (all
  images load; source links fixed). Outcome review continues in LY11; decisions
  in engine E16/E17. See the [Nov 4 recap](../recap/2026-11-04-0230-recap.md).
- [ ] **P1 you** LY11 Review the applied sandbox galleries and the recap; record
  look-alike picks and expected placements in `rebase-expectations.json`, and
  feedback on Review volume, cast joins, and the duplicate Camaris name
  (`Prospects\Camaris` versus the Angel).
- [ ] **P2 ai** LY12 Align gallery maintenance with the rebase. The Nov 3
  `bin\people-gallery.cmd ... --check` (97 min, EXIT 1) wants to rename 5
  `Various\review` "missing stable photo ID" holds that `clean_rebase` keeps
  under their original names on purpose, and it reports the galleries "out of
  sync" because the rebase's `_refresh_galleries` does not write
  `.gallery-maintenance-report-state.json`. User decision (Nov 3): any file in
  `Various\gallery` that does not follow the naming standard gets a stable ID and
  standard Various naming at intake; do not keep source names. Implement that in
  the rebase/intake, write the state after a rebase gallery rebuild, so a fresh
  install checks clean, and add a test for each.
  Filename slice implemented Nov 3: preserve recognized download IDs; assign
  ID-less non-cast inputs the existing originals content ID and normalize
  prepared destination prefixes without renaming frozen inputs. Exact byte
  copies are held with distinct `various_duplicate_*` names and explicit
  canonical-source reasons, not clustered twice; differing-byte ID collisions
  refuse explicitly. Manifest SHA-256 values are reused. Install/check/undo
  naming and duplicate recovery tests pass. This does not retroactively rename
  the installed review baseline. The maintenance report-state slice remains
  open; LY12 is not complete.
- [ ] **P1 ai** LY13 Cast-name collision. `Potentials\Camaris` is not a new
  identity: Production has had it since Oct 8 (two photos). Its `z_camaris_bloom.txt`
  says "Camaris Bloom", "returned to Potentials; replaced as Camaris by Ruby Eden"
  (Oct 19), but the folder kept the cast name. The rebase reused the folder name
  for a 5-photo cluster (nearest Drakniss 0.20) as `Prospects\Camaris`. Fix: the
  cast-replacement path renames the retired folder to its recorded display name;
  the rebase and intake refuse or rename any non-cast identity whose name matches
  an Angel/Sister (case-insensitive), preferring the recorded `name:`; a
  validator lists existing collisions. Correct the Production folder only through
  the LY8 true-up. Tests for each.
  Nov 3 extends this with [naming N14](2026-10-22-identity-family-naming.md#nov-3-name-continuity-and-character-slot-boundaries):
  non-character identities must have first and last names; valid merges keep
  the oldest original identity's name, including protected Prospect cores.
- [ ] **P2 you** LY14 Decide whether to cap maintained 944x1104
  derivatives (`gallery_944x1104`/headshots) to each identity's core,
  protected and workflow photos. Measured Nov 4 (table below): derivatives
  are 8,291 files / 7.2 GB in Working and cost about 1.15 s per photo
  (padded 0.39 s, head and chest the rest), roughly 54 serial minutes of a
  2,814-photo apply. A cap to core/protected/workflow photos would save most
  of that time and space plus the matching `_backup`/`previous` copies. Various
  holds only about 115 Review photos (0.10 GB), so excluding it alone changes
  little. If adopted: originals stay and still show in Review; protecting a
  photo generates its derivative; unprotecting or moving out removes them
  through the existing derivative manifest. Confirm the per-phase numbers with
  the timed N15 re-run before deciding. Source: user feedback below (Nov 4).
- [x] **P2 ai** LY14a LEAN intake no longer renders the comparison-only denoise
  and tone candidates (never auto-selected in 2,811 of 2,811 photos). Their
  steps are recorded as `skipped` with an explicit LEAN reason; FULL still
  renders them, and a FULL manifest with LEAN-skipped steps fails validation.
  The checkpoint binding gains `leanComparisons` so older LEAN checkpoints are
  never mixed in. Existing LEAN manifests with the renders still validate.
  The rebase install and apply now print per-phase seconds (`Install: ...`,
  `Plan: ...`, `Apply: ...`) for the next measurement. Takes effect on a new
  intake only; undo/replan/apply of an existing run reuses its old inputs.

**Nov 4 measured bottlenecks** (the `fresh-20261103-core` run; the apply log had
no timestamps outside verification, so derivative time is a 30-photo benchmark):

| Phase | Measure | Note |
| --- | --- | --- |
| Intake preparation CPU | about 587 worker-min | denoise 305 (52%), composition 71, head reconstruction 55, control 36, eraser 31.5, tone 20 |
| Run `inputs` on disk | 31,429 files / 17.9 GB | tone 4.6 GB, denoise 3.9 GB, control 3.8 GB; denoise/tone never selected |
| Apply: Review inputs verify | 1,619 s | 31,637 reads / 13.1 GB, mostly candidates |
| Apply: Overview thumbnails verify | 510 s | 13,681 reads / 4.5 GB |
| Apply: Overview evidence verify | 219 s | 11,311 reads / 2.5 GB |
| Apply: preparation history index (x2) | 268 s + 260 s | full artifact/source checks |
| Apply: 944x1104 derivatives | about 54 min (estimated) | 1.15 s per photo, 3 framings |
| Apply: preparation evidence verify (x2) | untimed until now | re-hashes the whole run `inputs`; LY14a halves it |
| Sandbox state | 23 GB | `inputs` 17.9, `previous` 4.5, source overlay 0.6 |

Expected effect of LY14a on the next fresh run: about 8.5 GB less run state,
about half the preparation CPU, and roughly half the bytes read by every
`inputs` verification pass.

**Nov 3 recap feedback ownership:** the complete
`rebase_fresh_20261102_feedback.md` is preserved once in
[gallery L21-L24](2026-10-22-gallery-review-layout.md#nov-3-fresh-rebase-recap-feedback).
That scope owns consistent recap styling/navigation, final-destination links,
membership-flow tables, core/surname image comparisons, explicit reason/score
labels, No Change distinctions and the ranked-picker idea. N14 owns Harlow/
Sophie/name continuity; engine E14/E15 owns final-rival audits and bounded
recomparison. C11/engine E13 owns the approved core-protection trial. Reuse
the same saved run evidence and preserve the installed pages for ongoing
review; no new full intake or broad plan reorganization is authorized.

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

Nov 2, coverage: move forward with the changes -> LY2, LY3, LY5 implemented and
tested; gallery holds only what is needed after the full process -> the
`gallery`/`review`/`944x1104` person layout and `_processing`; re-copy
production (with the new `Various\gallery` photos) into a fresh sandbox, run it
end to end, then redo the whole process from documented steps -> LY4 and the
LY6 runbook; status update -> the session reply and recap.

<!-- markdownlint-disable MD013 -->
````text
Let's move forward with those changes and then give me an update on where we are at - we need that we properly handle the structure so the gallery is cleaner and only has what we need after the full processes.  Basically - I want to re-replicate copying down the existing Production directory to the Sandbox.  I have files into the production Various/gallery so that when we snap things all from the start that things will work end-to-end in a fresh sandbox that isn't in the current state we're in.  So when we get things tested and verified are working - we'll need to step back and re-do that entire process and ensure all documentation and steps for executing it are in place and we can see the first runs working on a fresh sandbox and then we'll know how it processes, how it cleans things up that might not align or how the process works on that fresh sandbox set of galleries.
````
<!-- markdownlint-enable MD013 -->

Nov 2, coverage: commands and their order, and what copies exist at each step
of a fresh sandbox -> answered in chat as stages 0-5 and recorded as the LY6
runbook; workflow names injected at generation -> LY5 changes only code paths,
never the generated workflow JSON by hand, and keeps file names unchanged.

<!-- markdownlint-disable MD013 -->
````text
Before you start with a complete refresh of the sandbox - tell me what commands we run and in what order to get things going.  I want to understand just how it works when we snap the fresh and new copy of production down to the sandbox and all what we do run and what copies of things we do have in the sandbox at each step along the way.  More of a sandbox processing for dummies type step-by-step read out.
````

````text
Workflows are generated and the names get injected to them in the generation process.
````
<!-- markdownlint-enable MD013 -->

Nov 2 16:27, coverage: "Have we been finding issues" -> the lock fixes in LY4;
do not copy unneeded files into the sandbox -> the reset already leaves
regenerable output behind, and LY7 leaves Artists out; a concise, clean
sandbox on demand and a known way to run directly in Production with its
existing clutter -> LY8 true-up, gated on LY4 acceptance; clean break from
Artists (no copying or processing in the sandbox) -> LY7, with the Production
Artist scope kept at intake I74.

<!-- markdownlint-disable MD013 -->
````text
Have we been finding issues or what is going on?
````

````text
I hope this doesn't stop the background task ... but Yes - let's not copy forward files we don't need into the sandbox - which goes along with re-structuring things to make it easier to determine that in the future state as well as current state.  While we will have to deal with running a clean re-base directly into production - if we need to do something to clean it up ahead of time or to restructure things, I'll need to sort that out so we get a) a concise and clean sandbox when we want a new one and b) know exactly how to deal with production runs directly that may have a lot of existing structure and fragmented or unncessary files in many areas already.  That's a true-up that needs to happen in Production when we get the sandbox working the way we want it.
When running - we need to make a clean-break from doing anything with Artists - that was one of the plans and maybe we didn't finish that but it would save a lot of time in both copying files down to the Sandbox and processing them - if we don't actually want to process the Artists in the sandbox - which I do not want at this point.
````
<!-- markdownlint-enable MD013 -->

Nov 2 evening, coverage: run the sandbox to completion with every move and
rename applied, then review the galleries and trace back through intake,
comparisons and history -> LY4 attempt 3 (full apply) and the automatic recap;
an HTML page of what happened -> `rebase-recap\<run>.html`; who goes where,
renames, cast pulls, Review, who leaves, nearest identity, shared surnames ->
recap sections; "who do I think they look like" and the dropped-in test
images -> the Looks like picker and `rebase-expectations.json` (LY11);
protect Angels/Sisters while letting aligned supplements join, tune if too
many land in Review -> cast matches held in Review this run, tuning after
LY11, core-seed comparison LY10; repeatable automation, not one-off -> the
recap runs after every `sandbox-rebase.cmd` step; morning expectation of a
complete, clean rebase with docs and plans synced -> LY4 acceptance, this
plan, STATUS.md and the Nov 2 recap.

<!-- markdownlint-disable MD013 -->
````text
Since this is a sandbox - I'd actually like it to run to completion and actually move ahead with all the moves, renames of all files.  I want to see what does move in/out of the galleries, what is actually renamed, how does history look for those, etc... I do want a recap of what did happen - if we have a .html page that shows all that would be great.  I really want to check the final gallery UI and then drive backwards through what did happen and if needed review the intake processing work, see what the comparisons did and how things moved.  Hope this makes sense - we can have you check things for my human review - but when I come back, I want to see if we can't run it all the way and apply all changes and see what happened with the galleries.  I am doing this because I know some pictures for angels might fall out and some pictures in various SHOULD land in angels or sisters and that some things may end up in review, but if there are too many - then we need tuning.  As you know, I want protect the core identity of angels and sisters and if images supplement and align - they should be there, even with low scores so we don't create additional identities that ARE one of those - but if many fall out into a Model and the surname indicates the alignment - that'll help.  I can see when looking at a gallery just how close it aligns to other identities and that helps me see if it is or isn't someone else and it's just that our face scoring could use further improvements.  Does this all make sense on how far I want the rebase to run and how much I want to see all the actual changes applied?  Since it's sandbox - we can be aggressive in how we approach it since we can always make updates and re-run all or some pieces depending no my final feedback of the entire end-to-end run.
````

````text
Ultimately what I want to understand is who goes where in terms of the final end-to-end processing, who's renamed, who pulls from angels or sisters based on core, who is in review, who moves out - all that helps me understand what actually heppened in a run and why, who are they closest to, are they sharing surnames or not.  Who do I think they look like.  I know I have dropped in images to test this and that's what I want to see happen and how the entire system we have setup is or is not working to my visual reviews at the final outcome of the rebase.  Does that make sense and what questions do you have for me based on this comment?
````

````text
I want this to be repeatable and part of the automation, not a one time thing
````

````text
What I expect in the morning is a full and clean rebase completed and I can start to review the GUI and capture feedback about the GUI and results.  Don't forget to review and update docs/plans and to ensure you build all what we need and any late breaking things we decided that are not in the plans do get into the plans.  It's a complete end-to-end and sync up with docs and decisions.  So finish all what you know is needed for all this.
````
<!-- markdownlint-enable MD013 -->

## speed_and_space_optimization.md (Nov 4, verbatim)

Coverage: derivative cap, protect/unprotect generation and clean-up, Various
derivatives and the bottleneck question -> LY14 (measured Nov 4, decision
open); denoise/tone in LEAN -> LY14a (done); machine-transfer setup -> the main
README and the Nov 4 hand-off recap.

<!-- markdownlint-disable MD013 -->
````text
What if during the process we "cap" the number of 944x1104 images we generate for a single identity and focus on generating them for the core set of images based on score or any protected or workflow set?  Just wondering if that would actually speed up the end-to-end process and save on disk space.  We can still keep all the originals and show them in the review and if we protect one, it would auto generate the 944x1104 version.  We'd also need to ensure if we unprotect one and it moves out that we clean-up the various generated images.

I am wondering if this would have an improvement on overall processing, amount of files copied - checked etc... it would reduce the spwral of generting so many images - but I don't know if it would actually save time.  

I also don't think Various needs to generate all possible 944x1104 images that are left there for review as well.  Unless moving them would want to have those generated already.  

I guess - I want to know in the rebase process where the time is being spent and if capping the number of generated images would actually make a noticeable difference.

I'd want to know where the bottlenecks are in the processing overall.
````

Chat (Nov 4):

````text
I have this question in the speed and optimization - if you find somewhere else where we're taking so much time - how can we trim that down.  I also thought we were going to skip the denoise and tone images if we're running LEAN or was that in a different approach.  We've done a lot of optimization to save space and improve speed - but I see that the sandbox state is 17GB and looks like a lot of that is the denoise and tone images.  So please let's figure this out before one last re-run on this maching.  I am getting my other machine setup to run and we'll need to shift to being able to ensure we have a write-up on how to get that machine setup in the main README.md and setup instructions for the development environment - what tools we use when working and how it all works - and a hand-off with recap on where we are so I can pickup on that machine.   But first - we need to sort out these last enhancements we need to do while memory and context are up to date.
````
<!-- markdownlint-enable MD013 -->
