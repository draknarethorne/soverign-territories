# Storage operations, retention and clean sandbox

**Status:** active

**Queue focus:** S25, S24

**Scheduling:** S15's automated install/recovery/viewer gate passed Oct 31;
S25 exact-byte artifact reuse/recommended-only padding and S26 installed
lineage references now have bounded implementation/proof. S25's mode/default
review and S24's read-only amplification/dependency inventory may proceed in
parallel. Backup scope changes, packing/default adoption and PRUNE still
need their evidence/approval gates before another full intake. Other cleanup, root/configuration
and report I/O tasks remain open backlog, not permission to prune now.

This plan turns the current ad hoc locations for runs, reports, backups and
temporary files into a predictable, configurable and auditable system. It also
covers the one-time cleanup and the eventual clean sandbox recreation needed
before the production rebase.

## Non-negotiable safety boundary

**Never prune active photo-source directories or alter their contents as part
of storage cleanup.** This includes `Angels`, `Sisters`, `Models`, `Prospects`,
`Potentials`, `Artists`, `Various`, and any active `gallery` or `review`
folders. A photo appearing in a generated report or run does not make the
canonical source disposable.

Cleanup may target only files proven to be generated, obsolete, temporary, or
backups no longer needed for recovery. Before removal, prove there is no
dependency from an active run, undo journal, history page, report link, source
manifest, or planned production operation. No production photo or production
backup is in scope for the first manual cleanup.

## Current evidence

- The verified v21b intake contains 2,741 outcomes for the 2,700 immutable
  inputs plus 41 current Various inputs. Its report is under
  `B:\Sovereign Territories Sandbox\Working\_sandbox-state\r21b-20261028`.
- Earlier full intake runs include `clean-rebase-20261027-full-intake` (v16),
  `r17-20261028` (v17), `r20-20261028` (v20), and the completed `r21b-20261028`
  (v21). Full runs are expensive to retain; report-only pilots also accumulate
  under `Working\_reports\preparation`.
- The stopped `r21-20261028` has no intake receipt. Its preparation output
  directory had an orphan `.preparation-n1y5a5ps` staging directory. After the
  reboot, no related worker or ownership lock remained; the exact temporary
  directory was removed. It had no intake receipt and no durable report was
  removed.
- `B:\ST-v9\Sovereign Territories Sandbox\Working` is a separate old tree with
  a subset of `Various\gallery`, preparation reports `v9` through `v16`, and a
  gallery-intake preview. It is not the active sandbox Working root. Compare
  every photo against active sources by content hash before treating any copy
  as redundant; verify report references before pruning it.
- The hash comparison is complete: all 12 photos in the old `ST-v9` tree are
  exact matches for files in current `Working\Various`; there are no unique
  photos in that subset. The old tree still has report/history files, so it
  was retained pending the dependency and value review below.
- A second read-only link check found seven preparation manifests (v9, v10,
  v11, v12, v14c, v15 and v16) and a two-page gallery-intake preview in the
  old tree. The preview links to its run histories using relative paths, and
  the manifests identify `B:\ST-v9\Sovereign Territories Sandbox\Working` as
  their library root. No literal `ST-v9` reference was found in the current
  Working `_reports` HTML, JSON, Markdown, text or CSV files searched. The old
  tree is therefore an internally linked historical bundle, not a live input
  to current reports; deleting it would break those old report links. The
  tree is classified as a self-contained historical bundle, not a live input
  or a source of unique photos. Keep it outside the Working reset; decide
  whether to retire it through S10's dependency-aware retention policy. No
  files were removed.
- The sandbox's immutable `Source` manifest identifies
  `B:\Sovereign Territories` as its source root and lists 8,845 files totaling
  5.19 GiB. It was created on 2026-10-21 UTC and has been reverified against
  its manifest. It remains immutable historical evidence, not the current
  Production baseline.
- The read-only `likeness sandbox-reset --full` preview verified all 8,845
  Source files against the manifest and confirmed the exact target is
  `B:\Sovereign Territories Sandbox\Working`. The Production root contains
  65,259 files (27,044,732,226 bytes); the preview excludes 56,059 files
  (21,429,886,503 bytes) in configured operational roots and reserved
  `_archive`, while preserving `_junk` and `_retired` as deliberate
  photo/provenance stores. The managed Production baseline is 9,200 files
  (5,614,845,723 bytes): 8,842 Source paths unchanged, three removed under
  `_junk`, 358 additions under active `Various`, and no changed or unclassified
  paths. The Source copy is intact but stale; it must not seed a fresh Working
  tree as though it were current Production.
- Reset-boundary dependencies were checked against
  `workflows/workspaces.json` and the shared path validator. `Working` is the
  only future replacement target. Its sibling `Source` tree and
  `source-manifest.json`, and sibling Production root, remain outside that
  target. ComfyUI installs and workflows resolve under configured
  `installsRoot`; selected input filenames resolve under configured
  `inputsRoot` / `sharedInput`, and workflow outputs under `outputRoot` /
  `sharedOutput`. These roots are configured separately from Working and
  validated against overlap. Workspace input selections are external
  filenames, not paths into Working. The historical `ST-v9` tree is separate;
  its 12 photos duplicate active Working content and its report links remain
  internal to that old tree.
- SHA-256 comparison of active photo categories found 106 Working files whose
  content is absent from Production's active categories (79,661,819 bytes):
  89 JPEG source photos in `Working\Various\gallery` and 17 small gallery
  metadata files. None of those contents are in the old Source snapshot.
  Working has no same-path modified files in those categories; many other
  files have moved to different Production paths. Preserve the 89 active
  photos through reset. Carry the 17 metadata files in a non-active review
  bundle so a clean rebase does not silently reapply old sandbox assignments;
  one records Amelia Morgan history and 16 explicitly refer to a discarded
  clean-rebuild `run.json`.
- The existing `sandbox-reset` command only restores Models, Prospects and
  Potentials from Source. It is not a full Working rebuild or a current
  Production comparison.
- The `sandbox-reset --full` preview reports `resetReady: true`, with no path
  conflicts or unknown Production roots. Its configured-root exclusions must
  not discard `_junk` or `_retired`, which contain deliberately retained
  photos.
  Working currently contains 270,191 files (146,857,778,934 bytes), including
  6,044 active-category files (3,187,790,265 bytes). Of 675 active Working
  entries whose paths/content differ from Production, 569 exact contents
  already exist at another active Production path; the unique carry-forward
  set is exactly 89 JPEG photos (79,660,386 bytes) plus 17 metadata files
  (1,433 bytes). None of those 106 hashes occur in Source. Carry the photos
  into their same relative paths and retain metadata in a non-active review
  bundle. No data was changed by the preview.
- The current sandbox `Working` has distinct `_backup`, `_generation`,
  `_reports`, `_likeness`, `_actions`, `_junk`, `_retired`, and
  `_sandbox-state` areas. Their contents are not interchangeable: backups and
  action journals may be required for undo; generation outputs and report
  histories may have downstream links.
- The active intake implementation already uses a temporary staging
  directory, but an abrupt process stop can leave it behind. The parallel
  v21b run used 3 workers and completed its 2,741-row manifest; no intake
  process remains active.

These are inventory observations, not permission to delete a directory.

### Writer/reader map (verified foundations; inventory remains open)

| Area | Writers and readers | Lifecycle and dependency |
|---|---|---|
| Active category galleries | User-owned originals; `originals`, intake publication, likeness actions; gallery, likeness, and workflow-input discovery | Canonical sources. Never a storage-cleanup target; only explicit, reviewed library actions may move a photo. |
| `_backup` | `library_backup` and action/maintenance transactions; restore and undo commands | Recovery snapshots are durable until their dependent operation is explicitly settled. |
| `_reports` | Preparation, library, likeness, benchmark, gallery, and ComfyUI review publishers; browser pages, manifests, and history readers | Reports can link to detail pages, source photos, and run evidence. No age- or name-only pruning. |
| `_sandbox-state` | Sandbox rebase/preparation runs; matching, review, and resume readers | Contains large run copies and receipts. Recovery is waived for the eventual Working rebuild, but the tree remains untouched until the exact reset preview is verified. |
| `_likeness` / `_actions` | Likeness caches and aligned-face evidence; staged action writers; reconciliation and undo readers | Cache data is content-derived; action journals can remain required for undo. |
| `_generation` | ComfyUI output gallery and selected synthetic-result publishers; page, lineage, and review readers | Generated results are not identity evidence and may have downstream pages/sidecars. Discard only at the approved full Working rebuild or through a dependency-aware policy. |
| `_tmp` | Image preparation, report publishers, benchmarks, reference rendering, and configuration writes through `temporary_storage.staging_directory` | Same-volume owner-locked stages clean in `finally`; a later invocation removes a released orphan. Live locks and unknown stages are preserved/refused. |
| Model cache | Intake and likeness model loaders under configured `modelCacheRoot` | Downloaded model weights are reusable external cache data, not library sources; failed pinned downloads remove partial files. |
| ComfyUI installs and shared folders | Workflow deploy/sync, `sync_inputs`, and reference-rendering tools; workspace and output browsers | Roots are now configurable and validated; deployment backups and rendered outputs have their own readers and are outside the photo-library cleanup boundary. |

### Post-reboot B: performance check (2026-10-28)

- B: maps to a Samsung PSSD T7 over USB, formatted exFAT. Windows reports
  `Healthy`/`Online` and about 266 GB free. Read-only `chkdsk B:` found no
  filesystem problems and 0 KB in bad sectors; it warned that another process
  had the volume open, but completed its verification.
- A controlled 256 MiB write-through test measured 301 MiB/s on B: and
  336 MiB/s on C:. The 2,000-file create/enumerate/delete test measured
  1.11 s / 6.1 ms / 0.44 s on B:, versus 5.52 s / 10.6 ms / 3.65 s on C:.
  Reads were buffered and cache-dominated; this was a single comparative run,
  not a long-term benchmark.
- `chkdsk` reports 982,517 files and 114,834 indexes across all of B:. A
  read-only no-follow inventory of generated Working roots found 266,337 files
  in 29,866 directories, totaling about 135.5 GiB: `_sandbox-state` 196,156
  files / 109.00 GiB; `_reports` 37,705 / 19.52 GiB; `_backup` 27,653 /
  6.21 GiB; `_generation` 1,744 / 0.27 GiB; `_likeness` 2,448 / 0.06 GiB;
  `_retired` 630 / 0.47 GiB; `_actions` and `_junk` were negligible.
- Walking those trees and `lstat`-ing every file took 50.88 s for
  `_sandbox-state`, 52.93 s for `_reports`, and 34.95 s for `_backup`. A
  second pass took 56.18 s, 53.01 s, and 33.73 s respectively. Repeated
  recursive metadata work remains expensive even after the first pass; the
  generated file count/tree shape is a material cost for inventory, copy and
  cleanup operations, but not evidence of failed bulk throughput or filesystem
  corruption.
- Four full intake runs under `_sandbox-state` account for about 174,569 files
  and 101.97 GiB: the v16 run (29.43 GiB), v17 (23.99 GiB), v20 (23.92 GiB),
  and v21b (24.63 GiB). The v21 run has 5,934 files / 1.03 GiB but no intake
  receipt. These are generated run copies, not the canonical active galleries.
  Since sandbox recovery is waived, retaining these runs is not a prerequisite
  for rebuilding Working.
- The prior interrupted `.preparation-n1y5a5ps` staging directory had 2,657
  files and about 2.0 GiB. With no related worker, linked path, or ownership
  lock present, that exact temporary directory was removed after the reboot;
  B: free space rose from 265.83 to 267.75 GiB. Its unusually slow earlier
  cleanup did not recur; the removal completed within the 120-second command
  window. No active source folders or durable reports were removed.

## Work and acceptance

### Oct 29: clean-sandbox rehearsal authorization

The user authorizes resolving the reset blocker without waiting for another
confirmation, preserving the sandbox-only Various additions, and treating the
fresh Working tree as a Production-gallery rehearsal. Production, historical
Source and ST-v9 remain outside the reset target. Old generated Working
reports/recovery state may be discarded, not active source photos.

The reset's `WinError 5` is now explained by observed open handles, not a drive
fault: Microsoft Sysinternals Handle identified Explorer PID 12768 holding
`Working\_reports\library` twice, despite its visible window showing Production.
Gracefully closing that Explorer window released both handles; a new query
found none. A disposable B: fixture also proved populated cross-parent directory
renames work. The reset then committed successfully. Its first cleanup hit
MAX_PATH (Windows long paths are disabled); the existing backup extended-path
helper fixed deletion of the deeply nested rollback tree. Committed recovery
now finishes cleanup without starting another reset. See S14's exact audit.

- [ ] **P1 ai** S20 Measure fresh-baseline inventory, preparation, matching and
  report verification separately. Record worker count, input/output counts,
  configuration/recipe bindings and cleanup state. Compare with the measured
  old run without attributing recipe, population or cache differences to disk
  cleanup alone. Verify fresh intake covers current Working galleries rather
  than silently treating historical Source as current Production.
- [x] **P1 ai** S21 Finish the Oct 27/28 retrospective and Oct 29 run recap,
  reconcile feedback coverage and plans, run validators/tests/markdownlint,
  and commit/push coherent validated batches. Leave unfinished acceptance and
  storage lifecycle gaps explicit.
  **Result (Oct 30):** retrospectives and overnight checkpoints were
  reconciled into the current resume/feedback handoffs and a 20-record recap
  transfer ledger. All 13 current feedback notes have exact tracked source
  copies and task coverage; statuses/index/queue now distinguish active focus
  and holding. Ten queue tests, syntax checks and routine hygiene/data
  validation pass. Publication uses the normal commit/push gates; blocked
  installation, human acceptance and remaining storage work stay open.
- [x] **P2 either** S23 Agree recap pinning/retirement criteria, then archive
  only individually reviewed superseded recaps with corrected index links.
  The Oct 27/28 retrospectives already exist; the overnight Oct 29-30 recap
  must distinguish automated/AI checks from remaining human acceptance.
  Keep raw `feedback/recap_10_27.md` until its preservation and coverage are
  verified; no bulk recap or feedback removal is authorized.
  **Result (Oct 30):** the recap index now defines manual current/pinned/
  archive criteria and the exact 20-record transfer ledger; two relevant
  handoffs stay active. Moved prose is preserved and relative links verified.
  Raw feedback was separately reconciled source by source (13 exact-byte
  snapshots and actionable coverage), then individually archived. This is
  explicit reviewed housekeeping, not automatic archival/deletion or D4
  automation, and does not close any image acceptance gate.

### 1. Complete the storage and dependency inventory

- [ ] **P2 either** S22 Review C: cleanup candidates from performance T9's
  read-only inventory. Keep current profiling/recovery evidence, raw feedback,
  active chat state and extension state. Verify Visual Studio installer staging
  is unused before supported removal; identify exact old logs/contact sheets
  and dependency-free test remnants before deleting anything. No blanket
  Temp/AppData/cache/session cleanup is authorized by the inventory request.
  Measurements and the user's words live in the
  [performance plan](2026-10-28-intake-performance.md).

- [ ] **P1 ai** S1 Map every writer and reader for `Working` outputs,
  sandbox-state runs, report roots, backups, action/undo journals, likeness
  caches, ComfyUI workspaces/results, generated gallery images, scratch files,
  model downloads, and any external `B:\ST-v9` tree. For each, record the
  owner, configured or hard-coded root, creation mechanism, downstream
  dependencies, and cleanup behavior on success, error, Ctrl+C and hard stop.
- [x] **P1 ai** S2 Inventory the current sandbox and the approved Production
  source baseline without altering either. Focus on active source trees,
  immutable source manifests, source-only additions and the exact reset
  boundary. Compare candidate source copies by SHA-256, not by name.
- [x] **P1 ai** S3 Map only dependencies that cross the planned reset boundary:
  active source bytes, the immutable Source manifest, external workflow/input
  references, and the configuration needed to recreate Working. The user has
  waived recovery of sandbox-generated reports, backups, run evidence and
  undo data; do not spend effort preserving those outputs for the reset.

### 2. Establish configuration as the path authority

- [ ] **P1 ai** S4 Define one validated configuration contract for environment
  roots and per-area destinations: sandbox/production roots, run state,
  reports, backups, temporary staging, generated outputs, and local model
  cache. Preserve explicit CLI overrides for exceptional runs, but print and
  receipt every resolved path and configuration hash.
- [ ] **P1 ai** S5 Route every relevant writer and reader through the shared
  path resolver. Keep machine-specific absolute paths out of shared defaults;
  support the existing Windows workspace and allow tests to supply isolated
  temporary roots. Validate that resolved paths cannot cross into protected
  source roots or escape their configured base.
- [x] **P1 ai** S6 Add schema validation and focused tests for missing roots,
  invalid/overlapping roots, path overrides, path separators, and Windows
  junction/reparse points. Update launchers and docs to expose the same
  defaults.

Configuration groundwork (2026-10-29): `workflows/workspaces.json` has a
`storageRoots` map. `comfy_workflows.storage_root` rejects unknown root names,
overlapping or escaping destinations, overlap with active photo categories or
the reserved `_archive`, and reparse points (including junctions). Preparation
and library-sync reports, library backup snapshots, reference generation and
output galleries, selected gallery reports, likeness caches and aligned-face
evidence, sandbox reset staging, retained action journals, configured
junk/retired operations and their domain readers, incoming duplicate checks,
likeness reports, eraser/intake-sequence benchmarks, and overlay-review
reports now use configured roots. Nested intake report validation resolves
the sandbox-state root by its configured path rather than assuming a fixed
folder depth. The reset helper also rejects a staging root outside Working.

Focused verification passed: 74 duplicate/likeness tests and a 77-test
storage-root regression set covering retained-preparation classification,
photo retirement/junk, and workflow storage roots. Seven focused regression
tests for the latest benchmark/report routing changes passed. The full
`bin\test.cmd` launcher passed after those changes (339 tests across seven
suites).

Oct 29 configuration progress: the versioned schema now covers the
`referenceWorkspace` and the Production, sandbox, model-cache, install,
ComfyUI input/output, and shared input/output roots. Matching environment
overrides are resolved and validated; invalid or overlapping roots, a
drive-relative/escaping workflow subpath, and a multi-component reference
workspace are rejected. Configuration mutations validate before an atomic
same-volume publish through owner-locked staging under the repository's
ignored `tmp` directory. Workflow deployment, input synchronization,
backdrop workspaces, reference execution, and output browsing use the shared
root helpers instead of the prior hard-coded reference install.
`comfy_workflows.configuration_receipt` fingerprints the validated source
configuration and its effective resolved paths, including environment
overrides. `storage_configuration_receipt` is now attached to the full reset
preview, library-backup manifests, and image-preparation manifests; the
preparation schema accepts and validates the receipt. The follow-up routing
pass sends ComfyUI config staging through the configured temporary root under
ignored `tmp`; workflow backup operations use the configured backup root and
record source/destination entries in per-stamp receipts. Original-photo rename
maps use the configured actions root, include a configuration receipt, and
retain a legacy-map read fallback. Likeness diagnostics constrain explicit
`--out` paths to the configured reports root and publish a receipt with the
report. The complete writer/reader inventory and remaining storage receipts
remain part of S4-S5. The configured active work root still resolves to
Production by default, so no live storage operation was run during this pass.

Verification: the full `bin\test.cmd` launcher passed 363 tests across eight
suites. Focused post-pass tests passed for the workflow backup receipt entries,
final-command backup paths (23 tests), configured/legacy rename maps (2 tests),
and diagnostics receipts/output containment (4 tests). Tests used temporary
roots; no Production operation or Working reset was applied.

Verification: 77 workflow-configuration tests, 40 preparation/backup tests,
and 13 sandbox-reset tests passed. The full `bin\test.cmd` launcher passed
358 tests across eight suites. A refreshed read-only full-reset preview
reported both 64-character hashes and all 20 resolved paths. Its baseline
remains 9,200 managed Production files (5,614,845,723 bytes), with 56,059
storage files excluded; carry-forward remains 89 active photos and 17 metadata
files. It is reset-ready with no blockers. The receipt is at
`tmp\storage\full-reset-preview-receipt-20261029-postreceipts.json`; no reset
was applied. S4-S5, the remaining storage inventory and receipts, S10-S11,
and the actual Working rebuild remain open. S6's schema, runtime validation,
environment overrides, path-safety and reparse-point regressions passed.
S12's read-only preview is complete.

Fresh-rehearsal follow-up: People, Review and Prime comparison explicit output
paths now share report-root containment and reparse checks. Reference runs
retain frozen configuration receipts; valid historical receipts remain usable
after a configuration change, while malformed receipts refuse. The bounded
follow-up passed 151 focused tests and the reference launcher preview/check.
Clean-rebase overlay, input-mirror and intake-receipt publication now use
owner-locked configured staging. A failed input copy leaves no published
partial mirror; a verified published report can resume after an interrupted
receipt without re-rendering. The related baseline/preparation/reset/staging
set passed 69 tests.

S1/S4/S5 are deliberately still open. Destination-local scratch in Review,
report assets, gallery chrome and metadata needs consistent hard-stop/orphan
handling; People multi-file publication is not fully transactional, and its
remaining report manifests do not all carry complete configuration receipts.
Input-mirror staging/resume is no longer one of those outstanding gaps.

### 3. Make temporary data lifecycle-safe

- [x] **P1 ai** S7 Give each run a unique staging area on the same volume as its
  final destination when atomic publication requires it. Record ownership and
  state; clean it in `finally` on success, ordinary failure, and Ctrl+C.
- [x] **P1 ai** S8 For image-preparation staging, use a sidecar OS lock to
  distinguish a live process from a hard-stopped orphan. At the next run,
  automatically remove only an orphan with the tool's reserved staging name
  and a released owner lock; log the exact path. Preserve active locks and
  refuse unknown staging without a lock. This is temporary-run cleanup, not
  pruning of durable reports or backups.
- [x] **P1 ai** S9 Verify staging cleanup on success, ordinary failure,
  KeyboardInterrupt, a released lock after terminating another process, and
  while another process still holds the lock.

Future staging work beyond image preparation remains in S1 and S4-S8: inventory
other tools' scratch paths, migrate them to the shared storage policy, and
provide an explicit preview/check/apply interface for durable-output pruning.
- [x] **P1 ai** S9b Verify interruption and resume behavior with tests for
  failure before publication, failure during publication, cancellation, stale
  staging, and a live concurrent run. Preserve a clear error if cleanup itself
  fails.

Verification: `test_image_preparation` covers render failure before publish
and publication failure without replacing an existing result;
`test_temporary_storage` covers normal/error/KeyboardInterrupt cleanup,
released-orphan recovery, explicit cleanup failure, unknown-stage refusal, and
a concurrently locked live stage. Both passed in the Oct 29 focused
staging/report-publisher run.

### 4. Retention, deduplication and one-time cleanup

#### Oct 31 duplicate-first contract

**Authorized next iterations (Oct 31, 11:57):** complete a bounded LEAN
installed-native slice and recipe-aware timing/storage report statistics;
then compare independently verifiable COMPACT (downsized diagnostics) and
COLLAGE (labelled contact history) bundles from FULL/LEAN reports. Use
20-30 mixed Various/existing Gallery inputs through preparation, publication,
derivatives, viewers and backup/recovery. Record actual wall time, files,
bytes, exact/approximate role availability, selection/outcome counts and
input/output denominators. Do not select defaults from intake-only timing.
FULL evidence stays available; compact history is not exact rollback.
Source-report PRUNE requires dependency clearance and a recoverable
transaction; conversion alone must never silently remove the source.
FAST remains a separate processing-quality gate. Use short per-photo asset
names and avoid new unnecessary folder levels; do not bulk-migrate old paths.

The user's latest direction supersedes packing-first scheduling, not the
recovery safety gates. Prevent unnecessary files at the producer before
compressing copies of them. A report role is a label/reference, not an
instruction to store another image. Exact SHA-256 equality, not similar
appearance, permits reuse within one source lineage. Different encodings
of identical decoded pixels are not exact duplicates; do not silently
substitute EXIF/ICC-bearing raw bytes for normalized control pixels.

| Order | Owner | Increment / gate |
| --- | --- | --- |
| 1 | S25 | Opt-in LEAN preparation: exact-byte native/preview aliases within one photo, unchanged role labels and recipe, only recommended workflow padding. FULL preserves existing denoise/tone padding for explicit comparisons. Check actual files/bytes, hashes, report links and recovery before a bounded real-image comparison |
| 2 | S26 | At installation reuse the exact current Gallery/Review bytes for original/selected roles; create `gallery_org` only when original bytes differ. Version lineage/ownership and verify move/rename/action undo/restore before wiring a new rebase |
| 3 | S24, S11 | Map mirror/run/retained/backup/history amplification with measured unique-content and dependency counts; reduce backup scope only with independently restorable evidence. Packing and retention come after avoiding redundant payloads |
| Later | T18, T13/T14 | FAST processing profile and FULL/LEAN evidence are separate axes; cheap-step skipping needs quality tests. COLLAGE/on-demand alternative generation needs a reproducible recipe, sources and explicit availability states, not broken links or deleted masks |

No existing run, gallery, receipt or backup is rewritten to adopt this
contract. LEAN initially remains an explicit standalone preparation option;
it does not change `library.cmd` or the frozen rebase. Unselected native
enhancements/masks remain diagnostic evidence in this first increment;
only their unnecessary padding is omitted. Avoiding their computation or
retaining only composites is later work, not an unannounced FAST profile.

**Writer/reader map for this increment (verified Oct 31):**

| Boundary | Current copies / references | Next action |
| --- | --- | --- |
| Immutable source -> `clean_preparation.prepare` input mirror | Copies each input and binds its hash; separate from current Gallery | S24/S1 map recovery ownership before proposing cross-run reuse; no external mutable reference or hardlink as a shortcut |
| Mirror/source -> `image_preparation.render_photo` | Retains original, then encodes native controls/candidates and previews | S25 LEAN now resolves equal encoded bytes to one path per photo, including raw/control when truly identical. Distinct encodings stay distinct |
| Recommendation -> per-image checkpoint | FULL pads recommendation plus denoise/tone; manifests bind exact artifact set | LEAN pads recommendation only. Storage mode participates in recovery fingerprint; missing/changed shared files invalidate recovery/check |
| Selected source -> `clean_rebase.stage` native Gallery/Review | Copies selected bytes to the assigned native path | Opt-in S26 LEAN format 2 uses this exact native as the canonical installed reference, without changing matching/identity decisions |
| `retained_preparation.stage_photo` | FULL preserves compatibility; LEAN retains originals only when bytes differ from installed native | S26 aliases exact-equal original/variant roles to that photo's native path. Ownership, detail links, move/rename/undo and backup restore understand both formats; no migration of old evidence |
| Derivatives, history and backups | Derivatives can overlap selected padding; history links evidence rather than owning its own image store; backups copy retained/run payloads too | Hash-map these boundaries before unifying paths. Keep browser thumbnails when distinct and useful; keep independently recoverable snapshot bytes until a replacement is proven |

#### Oct 31 LEAN producer proof

Implemented `prepare-images.cmd --storage-mode lean` for **new standalone
v23 reports**. FULL is unchanged/default and old manifests remain verifiable.
The optional manifest field and checkpoint binding distinguish modes; repeat
apply with another mode refuses rather than rewriting the report. Alias hits
still verify the canonical file's hash. No pixel-similarity substitution,
cross-row/domain pooling, symlink/hardlink or persistent cache was introduced.
Normalization/processing and PNG/JPEG encoding still run: this first increment
avoids permanent duplicate writes, not the encoding CPU cost.

Supported preview/apply/check on the same six real installed Gallery inputs
(five general, one Artist) produced:

| Measured output | FULL | LEAN |
| --- | ---: | ---: |
| Actual image files | 62 | 46 |
| Actual image bytes | 61,128,917 | 42,901,872 |
| Total report files, including HTML/manifest | 70 | 54 |
| Workflow padding roles | 18 | 6 |
| Single-pass command seconds | 42.83 | 33.84 |

The difference is **12 unselected padded files plus four exact original/control
copies**; original/control HTML panels now point to the same file for those
four PNGs. All 38 native/preview role hashes, processing decisions excluding
timings, recommendations and selected padding hashes agree. The image-space
reduction is 29.8% **in this six-photo sample only**. These inputs already
passed the installed intake; neither their no-op frequency nor full-first,
warm-cache timings predict fresh-population or whole-rebase savings.

The LEAN index and all six detail pages passed browser checks: original and
recommended role panels remain, all 86 loaded image elements resolve, no page
errors. Source files, installed catalogue/pages, applied receipt, backup
manifest and measured implementation/schema hashes were unchanged. The
standalone sidecars are under `_reports/preparation/storage-{full,lean}-sample-20261031`;
durable measurements, helper, browser receipt and focused test log are under
`_sandbox-state/fresh-v23-20261029/storage-lean-audit-20261031`.
167 focused preparation/retained/history/rebase tests passed, including
exact-byte aliasing, distinct JPEG encodings, selected-only padding, stale
hashes, recovery mode binding and alias-preserving cross-owner move/undo.
Schema/link validation, 19/19 isolated quick mutation checks and scoped
hooks pass. The data-scope launcher needed a process-local
`PYTHONPATH=<repo>\tools\art` for an existing sibling import in
`test_identity_audit`; no package/configuration change was made. Its full-run
coverage guard also caught the two previous optimization modules missing
from the explicit full launcher; those entries are now wired and the guard
passes (scoped discovery already included them).
That producer proof alone did not validate a LEAN installation or authorize
pruning old runs. The subsequent S26 proof below supersedes its next-step
instruction; S25 stays open for broader defaults/dependency acceptance.

#### Oct 31 installed LEAN and history-mode proof

Two **24-photo mixed cohorts** completed actual preparation, fresh matching,
preview/install/check, Gallery/Overview/Review/history publication, full
backup and materialized recovery. Each combines 12 Various photos with
12 assigned Gallery photos, including Angel/Sister core context. These
isolated `tmp/s1` and `tmp/s2` libraries are not a full-scale rebase or
replacement for the existing human-review baseline.

| Cohort / scope | FULL | LEAN |
| --- | ---: | ---: |
| Installed recommendations replayed: preparation images / bytes | 240 / 209,937,761 | 187 / 150,874,548 |
| Same cohort: installed category files / bytes | 391 / 293,455,622 | 314 / 223,430,837 |
| Original pre-processing inputs replayed: preparation images / bytes | 336 / 241,014,133 | 276 / 190,247,836 |
| Same changed-input cohort: installed category files / bytes | 495 / 339,606,575 | 411 / 255,248,597 |

Installed storage fell **23.9% and 24.8%** respectively. All native and preview
role hashes, chosen padding, recommendations and matching destinations agree
within each FULL/LEAN pair. The first cohort selected all 24 originals and
LEAN created no original duplicates; the second genuinely changed all 24:
15 composition, five head-overlay reconstruction, two first-crop and two
head-overlay composition recommendations. Its distinct originals remain
exactly recoverable. This checks both halves of conditional `gallery_org`,
not only already-clean inputs.

Each source report also passed independent COMPACT and COLLAGE conversion:

| Source | Complete source report files / MB | COMPACT files / MB | COLLAGE files / MB |
| --- | ---: | ---: | ---: |
| First cohort FULL | 266 / 211.26 | 286 / 45.77 | 75 / 37.66 |
| First cohort LEAN | 213 / 152.19 | 238 / 43.37 | 75 / 37.23 |
| Changed cohort FULL | 362 / 242.71 | 399 / 74.82 | 99 / 64.62 |
| Changed cohort LEAN | 302 / 191.92 | 351 / 72.38 | 99 / 64.21 |

MB means decimal bytes / 1,000,000; totals include bundle metadata/HTML.
COMPACT substantially reduces bytes but **can increase file count**, since
exact originals/selected/padding accompany the reduced diagnostic files.
COLLAGE is the stronger file-count candidate. Both retain exact original,
selected native and selected padded bytes, with row/role/recipe provenance;
lossy diagnostics cannot replace exact masks or alternative-stage inputs.
All eight bundles passed independent check. They remain additive copies:
**zero source reports deleted and zero bytes reclaimed by conversion**.

Recipe-aware counters and external wall phases are in the experiment JSON
and HTML, including overlapping source/mirror/installed/backup/recovery
scopes. Pre-history phase totals were about 191 -> 233 seconds in the first
cohort and 340 -> 240 seconds in the second. FULL-first order, warm shared
models, simultaneous tests/ComfyUI and repository-volume copies confound
causal speed claims; storage improvements are proven, a general speedup is
not. No candidate processing/encoding step was skipped.

Browser acceptance loaded both cohorts' real Overview, Review and history,
all 48 LEAN installed detail pages and history conversions with no broken
images. Filters, head framing, card size, sorting and all 24 history rows
were exercised. These are technical link/rendering checks, not human
placement or image-quality acceptance. Move/rename/action undo remains
focused fixture coverage; these experiments performed full backup restore,
not another full-scale undo.

The experiments exposed Windows long-path accounting and a transient atomic
publication lock. Inventory now uses the existing extended-path helper;
the launcher rejects overlong OpenCV evidence roots before writing. Atomic
directory publication reuses bounded permission-lock retry with explicit
diagnostics, propagates persistent failure and preserves recovery checkpoints.
No processing pixels or decisions change.

Final focused batches passed 129 storage/history tests, 104 preparation/
Artist-publication tests and 95 rebase/action/derivative/backup tests.
Schema/link validation, all 19 isolated quick mutations and scoped commit
hooks passed. The transient directory-lock failure was reproduced before
the bounded retry fix; both transient recovery and persistent refusal are
covered, not dismissed as a successful retry of the test suite.

Durable receipts, report, source list, reproduction code and validation/browser
proof are under `Working/_reports/storage-experiments/20261031-lean-history`.
The isolated sample roots remain in ignored repository `tmp/s1` and `tmp/s2`
for inspection; they are generated experiment copies, not new canonical
sources. The failed overlong-path attempt is disposable after its diagnostic
receipt is preserved. Original B: source/catalogue/pages, applied receipt and
backup manifest hashes remain unchanged.

**Next:** review S25's evidence/default choices alongside S24's read-only
mirror/run/retained/backup dependency inventory before generic post-FULL PRUNE.
FULL compatibility remains the default; LEAN is opt-in. FAST processing,
on-demand alternate padding and exact selective FULL regeneration remain
separate later capabilities. No broad directory migration or existing-run
pruning is authorized by these results.

**Oct 30 priority clarification:** finish the current sandbox installation and
actual viewer/rollback acceptance first. Backup growth is a top item in the
next priority review, not another prerequisite detour. Evaluate what we retain
and back up, how it is stored, and when testing copies can safely be pruned.
No archive format, retention duration or automatic deletion policy is approved
by this clarification. Preserve the current verified snapshot and rollback
evidence through acceptance; active source galleries remain protected.

- [ ] **P1 ai** S24 After the duplicate-first S25/S26 increments, reduce backup growth:
  measure retained/backup scope and redundant snapshots with S11; benchmark
  directory snapshots against bounded ZIP64 stored/low-compression archives
  for creation, verification, exact restore, interruption recovery and space.
  Propose testing retention/prune eligibility and explicit recovery dependency
  clearance, including timestamps for newest-input selection. Present measured
  options before adopting a format or deletion schedule. Coordinate detailed
  intake-image retention with performance T13/T14 rather than duplicate it.
  **Oct 31 order:** finish the duplicate-first S25/S26 slices before more
  archive benchmarks; inventory backup amplification in parallel, not as
  permission to discard independent recovery copies.

  **Oct 31 bounded implementation:** the existing `library-backup.cmd
  --benchmark SNAPSHOT` now previews/measures DIRECTORY, ZIP64 STORED and
  ZIP64 deflate 1 under explicitly resolved ignored repo `tmp`; `--check`
  verifies saved measurements, all selected source hashes, payload hashes and
  exact restored file mtimes/counts/bytes. Changed inputs and incomplete/truncated
  outputs are refused, not overwritten; links/traversal and long Windows paths
  have focused regressions. The verified historical snapshot was read only:
  no full snapshot walk/hash, new intake, library mutation, backup replacement
  or pruning occurred. Verbatim authorization belongs to the parent's
  [L18 implementation/user-request record](2026-10-22-gallery-review-layout.md#oct-31-l18-implementation),
  rather than another copy here.

  **Measured evidence:** a 24-file / 13.7-MB mixed real-image sample passed
  all three restores and the independent final receipt/output `--check`.
  Archive packing reduces payload file count; mixed-sample deflate savings
  must not be interpreted as image savings (the image members expand).
  Exact denominators, measured times/bytes, commands, output location,
  boundaries and single-pass warm-cache/B:-read/C:-write caveats live in the
  [canonical backup runbook](../art/original-photos.md#bounded-backup-format-benchmark-explicit-experiment).
  DIRECTORY remains the default. S24 stays open for retained scope,
  whole-library recovery dependencies, broader cold/same-volume measurements
  and a user-approved retention/prune decision; packing alone does not satisfy S25.

- [ ] **P1 ai** S25 Producer, installed-native and opt-in COMPACT/COLLAGE
  experiments are verified above. Finish broader evidence availability,
  default/dependency acceptance and production-scope tests for optional
  storage modes independent of processing recipes: FULL detail, LEAN shared
  verified artifacts for identical original/control/recommendation roles, and
  COLLAGE review previews. Preserve role labels in the GUI while resolving to
  one file where exact content equivalence permits; do not infer equality from
  visual similarity or deduplicate distinct source lineage/identity. Account
  for per-run, retained, backup and rollback copies, source-coordinate masks,
  selected native/padded workflow inputs and reproduction dependencies.
  Measure file count/bytes/restore cost and interruption-safe cleanup; no
  deletion of current evidence until the approved dependency policy permits.
  Enhancement skipping is a processing/quality choice under I70/T18, not a
  silent effect of LEAN. T13 owns composite tooling; T14 owns detailed/summary
  evidence acceptance. Source and full item ledger are in intake's Oct 30
  12:31 reconciliation.
  FULL ultimately means richer alternatives, not a requirement for duplicate
  equal-byte payloads. Promote exact-byte aliases across future modes after
  the downstream/default gates; the current FULL branch remains the unchanged
  compatibility control for this first opt-in LEAN experiment.

  **Oct 31 metadata-only LEAN screen:** the frozen manifest's 2,793 people
  rows reference 31,774 image roles at 31,650 distinct paths. Restricting
  candidates to different paths with the same declared SHA-256 **within one
  original row**, and excluding paths shared by multiple rows, identifies
  462 potentially avoidable files across 222 photos (462 equal-content groups).
  This is about 1.46% of referenced image paths, not a byte-saving estimate or
  proof that an existing artifact may be deleted. No artifact stat/hash pass,
  cross-lineage merge, rewriting of detail links or change to retained evidence
  occurred. The reproducible helper and full group ledger are in ignored
  `tmp/perf/audit-role-reuse-20261031.py` and
  `tmp/perf/role-reuse-candidates-20261031.json`.
  This bounded the first experiment; the producer proof above now tests
  role-to-artifact aliases with identical bytes and source lineage.
  Directory packing and within-row aliases alone do not explain away all
  backup/history amplification; S24's scope/dependency inventory remains P1.

- [x] **P1 ai** S26 After S25's bounded producer proof, version retained
  publication so unchanged originals and selected roles reference the
  installed native file rather than copying it to `gallery_org` or
  `gallery_intake`. Changed originals still require exact original recovery.
  Map original/control/selected/preview/padded roles explicitly, without
  cross-photo or cross-artist merging, hardlinks or symlinks. Cover the
  current `stage_photo` copy, `verify_link` owned-path restrictions,
  transfer/rename/retirement/action undo, installed verification, backup
  restore and history availability together. Read-only mapping first;
  no deletion/migration of the frozen installed baseline. Only then expose
  LEAN through a fresh rebase. Version 2, native-reference ownership,
  unchanged-original/no-`gallery_org`, differing-original recovery, exact
  alias tamper rejection, rename, cross-owner move/undo and real backup
  restoration are tested. The fresh mixed real-image experiments below
  exercise the CLI and installed check. Routine default adoption remains
  S25's separate evidence/human-acceptance decision; FULL compatibility stays.

- [x] **P1 ai** S10 Define and implement a versioned run retention manifest
  and dependency-aware policy. Receipt-backed new runs register as review/keep;
  unsupported and unregistered directories remain held. Only successfully
  applied runs can be accepted. Keep the latest accepted run per pipeline and
  every unaccepted/incomplete run. An older accepted run requires explicit
  review, undo and audit clearance, a full-tree content fingerprint, a clean
  Working text-reference scan, a second explicit deletion apply, a durable
  receipt, and refresh of generated intake-history pages. A completed deletion
  with failed history publication has a report-only repair path. A changed run
  manifest/content or partial deletion blocks cleanup pending review.

Verification (2026-10-29): added `storage-retention.cmd` preview/check/register/
accept/supersede/delete surfaces, automatic registration from intake and
rebase receipt writers, and focused retention tests. The full
`cmd /c bin\test.cmd` suite passed 363 tests across eight suites; the five
retention tests plus the automatic registration regression passed (6 tests).
CLI help and `git diff --check`
passed. The read-only B: preview found 10 unregistered runs and kept all of
them; no existing run was registered or deleted. An initial no-candidate
preview took 162 seconds while redundantly walking Working, so the preview was
changed to defer tree fingerprints/reference scans until an approved prune is
actually eligible. The same live preview then completed in 0.59 seconds.
- [ ] **P1 ai** S11 Measure duplicate bytes across per-run source mirrors,
  retained originals, source overlays, thumbnails, padded PNGs, generated
  images and reports. Prototype content-addressed sharing or same-volume
  hardlinks only where validation and recovery semantics remain exact; retain
  copy fallback where links are unavailable. Measure B: I/O and disk savings
  before adopting.

  Include `gui_and _thumbnails.md`: map every actual page/reference and
  measure thumbnail versus original/full-image browsing cost before retaining
  or eliminating copies. U6 owns manifest-proven thumbnail regeneration;
  S24/S25 owns retained evidence budgets; S10/L20 owns dependency-aware run
  retention. Propose separate recoverable-trash and irreversible-purge stages,
  user-approved retention windows and exact restore tests. No current source,
  snapshot, report or trash deletion is authorized by this review.

Verification (2026-10-29, read-only): the full Working scan covered 270,191
files / 146,857,778,934 bytes with no inventory errors or reparse entries.
SHA-256 was computed for all 239,555 files in repeated-size groups
(113,344,624,911 bytes). It found 49,952 exact-duplicate groups and 172,244
redundant copies, representing 81,028,741,928 duplicate bytes (about 75.5
GiB, 55.2% of total Working bytes); the scan took 815.9 seconds. Largest
buckets were 43,439,609,499
duplicate bytes within `_sandbox-state`, 15,103,288,656 across `_reports` and
`_sandbox-state`, and 4,726,132,748 within `_reports`. This measures byte
identity only: no files were deleted, deduplicated, or hardlinked. S11 remains
open to test storage-sharing and recovery semantics and measure actual B: I/O
and savings before adopting any optimization. B: is healthy and formatted
exFAT, so NTFS
hardlinks are unavailable. A content-addressed store was not adopted because
its reference, update, and recovery semantics are not yet validated across all
readers and writers.
- [x] **P1 ai** S12 Prepare a read-only reset preview naming the exact
  sandbox target, the approved Production/Source baseline, counts and bytes,
  and every active source file present only in the current sandbox. Do not
  copy sandbox recovery outputs. The 89 Working-only `Various` JPEGs must be
  carried into the new Working tree; carry the 17 unique gallery metadata
  files in a non-active review bundle unless they are separately reconciled.
  Do not apply until the target boundary and a fresh current-Production
  baseline are verified.

Verification (2026-10-29): `bin\likeness.cmd --root "B:\Sovereign
Territories Sandbox\Working" sandbox-reset --full` produced a fresh,
hash-bound preview with `resetReady: true`. The final policy excludes eight
configured operational/reserved roots (`_actions`, `_archive`, `_backup`,
`_generation`, `_likeness`, `_reports`, `_sandbox-state`, `_tmp`) and keeps
Production `_junk`/`_retired`. The managed baseline is 9,200 files
(5,614,845,723 bytes); 56,059 storage files (21,429,886,503 bytes) are
excluded. It records 358 additions, 3 removals, no changed/unclassified paths,
and the exact carry-forward hashes: 89 active photos and 17 metadata files.
The 569 identical items already active in Production need no copy.
- [x] **P1 ai** S13 Classify `B:\ST-v9` and verify whether its `Various` images
  are exact copies of active sources and whether its reports are still linked.
  Do not remove the tree until S2/S3 prove the disposition.

Verification (2026-10-29): S2/S3 show all 12 photos are byte-identical to
current Working sources, seven old preparation manifests and the gallery
preview link only within `ST-v9`, and no searched current-Working report
references `ST-v9`. Preserve the old tree until S10's retention preview can
show its full dependency/space impact; no external cleanup was applied.

### 5. Recreate the sandbox and prepare production

- [x] **P1 ai** S14 After the storage policy and writer migration are in use,
  recreate sandbox Working from the verified Production/Source baseline using
  its manifest. The user prefers replacing the generated sandbox wholesale
  rather than manually pruning old runs and does not require sandbox recovery
  copies. Preserve or explicitly disposition any sandbox-only active source
  before replacing Working; keep the immutable Source baseline and Production
  outside the reset target.

Reset apply implementation (2026-10-29): `sandbox-reset --full --apply` now
stages current Production under the configured Working-local `_tmp`, verifies
the full copied file/hash set, carries the 89 approved active photos and 17
metadata files, and writes a configuration receipt into the new
`_reports\reset-review-bundle`. A sidecar lock and transaction journal support
rollback after a failed swap and recovery after a hard stop. The focused reset
and staging tests pass (28 tests, including long-path cleanup and avoiding a
second reset after committed recovery). The two original denied swaps rolled
back. After releasing Explorer's confirmed report handles, the next attempt
installed the verified baseline but could not delete nested old backup paths
beyond 260 characters. Extended Windows paths resolved that cleanup failure;
the same apply resumed the committed journal and completed in 106.25 seconds
without another reset.

The post-reset SHA-256 audit verified the exact installed file set: 9,307 files /
5,694,510,002 bytes, consisting of 9,200 managed Production files, 89 unique
active photos, 17 non-active metadata files and the reset receipt. All six
operational output roots were empty; the temporary journal, stage and lock
were gone. Historical Source reverified all 8,845 files / 5,570,978,132 bytes.
The current Production baseline remained 9,200 files with the same 358
additions, three removals and no changed paths. Production and ST-v9 were not
mutation targets. Logical Working bytes fell by 141,163,268,932 (131.47 GiB),
with 260,884 fewer files. Fresh pipeline outputs now grow from this baseline,
not the old reports. Verification took 168.35 seconds including Source and
Production checks, not just Working enumeration.

The audit was subsequently copied, with matching SHA-256, into
`Working\_reports\reset-review-bundle\reset-verification-20261029.json`.
It records the pre-intake baseline, not the growing live run. This durable
evidence adds one report file after the audited 9,307-file snapshot; the
disposable `tmp` copy is not the sole record.

An input-boundary gap was also found: the old clean-rebase default still
replays historical Source plus optional Various. New `--baseline working`
freezes current assigned galleries plus Various into the run-local verified
overlay; Source remains unchanged. Preview: 2,700 assigned inputs plus 372
new Various outcomes = 3,072, with 75 baseline IDs substituted by newer
Various bytes. This includes the preserved sandbox-only additions. The
supported launcher inventory took 55.68 seconds. Matching has not been
accepted merely because reset/inventory passed.
- [x] **P1 ai** S15 Run the final sandbox dry-run, audit source counts, protected
  Angels/Sisters retention, candidate moves, review counts, backups, and undo.
  No Production install in this step.

Oct 31 automated gate complete: the same-stage install reused the verified
72,991-file full snapshot; installed checks, exact rollback inventories/hashes,
Artist isolation and actual viewer/history acceptance passed. Recovery proof
and browser evidence are durable beside `run.json`; see
[C6's final verification](2026-10-23-cast-seeded-library-rebase.md#oct-31-0219-final-installed-verification).
This closes the **undo-readiness audit**, not an executed full-scale undo:
the earlier failed install's real rollback was independently proven and
focused fixtures exercise undo/retry. The installed baseline was not undone
and reinstalled merely to obtain another test. C7/I60 human quality/identity
approval is still separate. No backups, originals or retained evidence were
pruned; S24/S25 decisions remain required before another expensive run.

Oct 29 execution checkpoint: the supported inventory-only preview for
`fresh-v23-20261029` confirms 3,072 outcomes (2,700 assigned plus 372 current
Various; 75 newer-byte substitutions). After performance T12's tested
recovery/current-sample disposition, the intake-only sandbox iteration was
started with three workers. Its source-overlay copy and live process CPU
progress were verified. It subsequently completed all 3,072 outcomes with
no assessment errors, and the separate launcher `--baseline working --check`
passed. The subsequent matching preview and tested incoming-ID correction
completed through matching-only replan at 23:43 -05:00: 2,793 people photos,
1,218 retained cast, 48 eligible releases, 942 folder changes and 99 Review
outcomes. All selected inputs/exact-face bindings and protected release flags
verify; 53 intake sheets and 17 destination sheets received AI screening.
The [cast owner](2026-10-23-cast-seeded-library-rebase.md#revised-v23-preview-and-first-pass-audit)
records the full audit, remaining review priorities and unchanged thresholds.
The complete snapshot preview covers 72,991 files / 41,998,676,177 bytes
(the earlier preview preceded final matching-report updates). Its supported
apply started at 23:45 -05:00, before installation. Snapshot
`library-20261029-235003` completed at Oct 30, 00:54:29 -05:00 with exit 0:
all 72,991 files / 41,998,676,177 bytes passed file-list and SHA-256 checks.
Manifest SHA-256:
`b73ced418f289a0109899dd8601b368b2b55fa6337bcbf9f327b4e27c8280ccf`.
The install began at 00:54:53 and was still in active read-only preflight at
01:22. This completes the backup gate, not installation, undo or viewer
acceptance. Current
sample findings/timings live in T12 and intake I60, not a new storage redesign.

The first install was subsequently stopped before publication for the measured
native-owner performance blocker in performance T16. All 2,868 Working input
hashes and the unchanged source catalogue were independently verified.
Run-local `install-attempt-20261030-040207.json` records that proof and the
preserved `abandoned-staged-20261030-040207` / empty
`abandoned-previous-20261030-040207` directories. Nothing was deleted; the
verified full backup and saved preview remain the same. Retry apply only
after the narrow fix's tests/commit; final installed/undo/viewer gates remain.

- [ ] **P1 ai** S16 Write the Production runbook with exact source snapshot,
  configuration, destination roots, backups, validation gates, rollback and
  post-run verification. Production execution remains separately gated.

### 6. Related category configuration feedback

The newer Artists/Humans/Animals and `_Intake` proposals are preserved in
[intake's fresh-v23 feedback](2026-10-23-image-intake-preparation.md#feedbackfresh-v23-20261029_feedbackmd-verbatim-proposals-remain-gated).
S17-S19 cover the proposed physical/category contract, not an immediate tree
migration during sandbox installation. Artist preparation and exclusion from
general people matching are separate decisions.

The expanded Oct 30 note retains the concrete proposed root families
`Artists` (Fantasy, Pierre, Her Legends), `Humans` (Angels, Sisters, Models,
Prospects, Potentials, Various), and `Animals` (Bears, Lions, Tigers, Sharks,
Cats, Dragons), plus a possible Various-to-`_Intake` rename. S17 must inventory
all path/config/report/workflow/undo consumers and distinguish domain roots
from display categories; S18/S19 propose and approve a reversible migration
with old-path lineage, not merely rename directories. Optional Artist
preparation and separate Artist execution belong to intake I74, not this
physical migration. See
[the complete item ledger](2026-10-23-image-intake-preparation.md#complete-source-to-plan-coverage-ledger).

The attached category/configuration feedback describes a broader refactor:
category metadata (type, rank, path, protection, thresholds and other logic
drivers) and global defaults should replace category-name conditionals and
hard-coded policy paths. This is related to S4/S5 but must not be hidden inside
storage cleanup.

- [ ] **P2 ai** S17 Map current category-name conditionals and existing policy
  sources; identify the authoritative schema/config owner and the behavior of
  each category before changing logic.
  Include every directory/CLI/cache/Junk/erasure-config/report/workspace
  consumer in the current-state inventory (S1/S4/S5). Sketch future Drakn
  Bound males, Elder Dragons and Demons alongside Artist/Human/Animal domains,
  separating future display categories from physical roots.
- [ ] **P2 ai** S18 Propose a versioned category/global configuration contract,
  validate it, migrate one low-risk consumer at a time, and test that current
  category routing, protection and likeness thresholds remain unchanged.
- [ ] **P2 either** S19 Review the configuration proposal before broad
  category-driven logic migration. Adding a category must not silently change
  storage paths, protection or matching behavior.
  Preview incremental versus justified larger migration chunks, repeat the
  high-risk cases from a frozen sandbox baseline, verify backup/restore and
  every CLI/GUI consumer, then seek separate Production approval. Neither
  `gallery_directory_structure.md` nor category feedback authorizes big-bang
  renames or skipping current-state analysis.

## Scope and guardrails

- The user has waived recovery of generated sandbox state. This changes the
  planned cleanup from selective report/backup pruning to a whole-Working
  rebuild once the storage layout is ready; it does not waive protection for
  active source photos or authorize changes to Production.
- The existing Source snapshot predates current Production. Refresh it only
  through an explicit, hash-verified baseline operation; the old snapshot is
  not a current-production copy. The active Working-only photos and metadata
  are a separate carry-forward set, not sandbox recovery data.
- The reset preview must distinguish `Working` from its sibling immutable
  `Source` snapshot. Do not delete the whole Sandbox parent or Source as an
  interpretation of "reset Working."
- The exact reset target, Production baseline, full Working apply and
  post-reset hash audit are verified under S14. The fresh pipeline/move/undo
  acceptance remains open under S15/S20.
- No production cleanup, source mutation, or production rebase is authorized
  by this plan.
- No deletion based solely on a name, age, recipe version, or apparent duplicate.
- Durable-output pruning must have a read-only preview, a check mode, an
  explicit apply, a durable receipt and a recovery story. The narrow exception
  is owner-locked temporary staging: removing a released lock's ephemeral run
  directory at next preparation is automatic and logged.
- Related plans remain owners of their domain details: gallery history/pruning
  navigation in `2026-10-22-gallery-review-layout.md`, ComfyUI output retention
  and gallery return in `2026-10-25-reference-rendering.md`, and category/code
  organization in `2026-10-20-art-tools-structure.md`. This plan coordinates
  their storage-root contract and the sandbox reset.

## Preserved user feedback

<!-- markdownlint-disable MD013 MD046 -->

### feedback/recap_10_27.md (verbatim; S21/S23)

```text
We'll need to write a recap for 10-27-2026 of all that was done, where we are, what I need to validate, etc... following the standard practice, but ensuring we also highlight the big wins, gotchas, remaining items and manual verification I need to do as well as all the automated verification you were doing all the way to speed this up.

This tells me that as we move into additional phases - including the likeness comparison that as long as we work it similar to how we did the intake that you can do the initial verification passes on all the outstanding items we need to work on and not just rely on me for all the manual work and present me with the final list of things you couldn't verify or need me to do manually.

I'm finding out that getting our requirements, plans and verification processes clearly defined upfront is crucial to ensure smooth progress and minimize the need for extensive manual intervention later on. This approach allows us to catch potential issues early, streamline the verification workflow, and maintain a high level of accuracy and efficiency throughout the project.
Moving forward, we should continue to refine our processes, document any changes, and ensure that both manual and automated verification steps are well-integrated and consistently applied. This will help us maintain momentum and reduce the risk of errors as we tackle more complex phases of the project.

Our feedback loop we have has been working well and we can just continue to improve on it, update our instructions, docs and working agreement together and that will make the continued work on this very effective.

I'll also want to start to archive older recaps that aren't important any more.  Keep ones that are still important (like pinning them) so that ongoing the recaps are things I still need to pay attention to.  It's sort of like how we have active feedback .md files until we get them into plans and archive the feedback.  Same with active plans and how we archive completed or obsolete or superceeded ones as we learn.  

Basically just document management hygeine. We want to make sure that our recaps, feedback, and plans are all organized, easily accessible, and that outdated or irrelevant information is properly archived to avoid clutter and confusion.
```

Oct 28 chat, 21:32:56:

> Is it still running in the background? Also, we can probably drop all older
> runs that are on code we don't care about history for. At least a little
> pruning is good as we're still doing work and iterating on the large sets of
> data.

Oct 28 chat, 22:04:27:

> We also have B:\ST-v9 that I don't know what it is as well as many other things in B:\Sovereign Territories Sandbox\Working in _ directories that I don't know if are necessary as well.  Older backups and such that may be invalid.  Ideally we keep only what we need for the work.  B:\Sovereign Territories Sandbox\Working\_backup  and B:\Sovereign Territories Sandbox\Working\_generation and B:\Sovereign Territories Sandbox\Working\_reports and I don't know what is needed ... maybe other places as well.  As things were running to test various changes lots of residual files were left behind as we progressed.  Lots of interim fragments of files clutter the Working directory.  I do want to keep what is necessary, but ultimately need a clean-house when we get to the Production working directory and not have files left that aren't needed after things are run.  It seems the location of backups and reports and such has changed over time and isn't driven from a configuration file and when left to a command line the input changes based on our prompts we work on together so there may not be a rigorious system in place that we need to knowing what is where and what can be pruned over time.  So we need to 1) clean things up and 2) fix it with configuration so it's predictable, tracked well and can be pruned properly and 3) ensure that after a run, temporary files are removed - even when runs fail or we stop them.  A system needs to be put in place.  If we need a plan for all this, then we'd better write one for that as well so we can build the system after a manual clean-up effort.  Once the sandbox runs are complete and fully functional, we could just remove everything in the sandbox, re-create it from Production and test one last time - but prior to that we need that structured system in place to handle ongoing updates and not exploding the directory size.  If we are creating temporary places to put files, clean them up, if we need files - can we compress things, store them more efficiently or directly reference same files where we can do that instead of multiple copies.  There has to be a system we can think of.  Might take quite a bit of inspection because many of the tools write to different places and I am not sure how we controlled all the destinations in the past.  I'm also sure the structure stores things inefficiently as well - which also slows the performance of the B: drive overall with so many files.

Oct 28 chat, 22:06:21:

> Just to be clear - we shouldn't prune directories that include active source
> files even after we put them into the gallery like Angels, Sister, Various
> or others - it's really the backups, copies, old reports no longer valid,
> temporary files used only during process and not after. It's both short term
> clean-up and long term strategy.

Oct 28 chat, 23:33:26:

> If I need to just delete directories manually in windows explorer - I can do that

Oct 28 chat, 23:33:40:

> I don't care about data recovery in the sandbox
> I am ready to want to just delete the entire sandbox and start fresh after we figure out the proper way to have out files structured

`feedback/cleanup_backups_reports.md`, word for word:

```markdown
As we have worked there are many different and out-dated versions of reports in the sandbox and I am sure we have many copies of thumbnails that are no longer necessary and we will want to reset the entire sandbox as a copy of the production environment to ensure we are working with the most current and relevant data for a dry-run after all the code is completed.

We should have a snapshot of that in the B:\Sovereign Territories Sandbox\Source but there is not any likeness that is established yet, so we'll need to figure out how to reset our sandbox working directory and start just like we would if we had a production copy.  We'll want to figure out the right approach to give it another try.

Do we just need to copy the directories from C:\Soverign Territories to the Sandbox as a fresh copy of Production and just run the rebase commands the right way - since it has likeness already in cache somewhere and we'll need to handle the process of just keeping the core for Angels and Sisters as we want to run that and figure out how to write up a document for the Production run when it's time for that.

There's also clean-up in production we need to do as many copies of things are stored and I don't think are useful given where we are at.

I also noticed a b:\ST-v9 directory I think we can clean-up but I don't know what that is.

Basically it's a clean-up and get Sandbox in the dry-run for Production run, test and confirm a few key aspects one again, the write up a proper playbook for the Production run, create proper backups, execute the Production run and verify things are clean.
```

`feedback/categories_and_code.md`, word for word:

```markdown
# Categories and Code Organization

This document outlines the approach for managing categories and organizing code in a way that reduces hard-coded dependencies and ensures that logic is driven by configuration files.

## Hard Coding Categories

In reading some code, I see hard-coded references to "Sisters, Models, Angels, Prospects, Potentials and Artists" in logic areas and such.  While that is some of my direct statements, what we need to do is get the categories setup with properties that are defined that drive the decisions about logic instead of the literal about the category name.  

Things like
    - Category Name
    - Description
    - Type (person, animal, artist, etc...)
    - Rank (priority or importance of the category)
    - Path (path to storage)
    - Default Protected (is this protected by default)
    - Thresholds (for likeness comparison)
    - Required Min Number Photos (or whatever is appropriate)
    - Additional Properties (any other relevant properties for the category)
    - Logic Drivers (any specific logic that depends on this category)

Basically anything driving a logic piece that is based on the name right now, needs to be based on logic around the categories and if we add Demons we only really need to add

We'd have some global properties that are part of the entire project scope for all pieces for things we need as well for things like
    - Base Storage Path
    - Default Thresholds (for likeness comparison)
    - Default Min Number Photos (for likeness comparison)

In short, I think we have at least some .json files for how things work already - but I still see code with hard-coded references as well as places where C:\Soverign-Territories\soverign-territories\data\art\likeness-engine-policy.json being used.  So we're probably a bit fragile in how logic isn't always driven from a config.

As you do the analysis, you can probably figure out the logic and what it's trying to do based on category names and we can enhance the properties and ensure that all things are setup properly.

Basically, it's sort of like defining a workspace in comfyui which has default behaviour that you can adjust and setup properties for specifically.  In our case, the categories and global properties act as the configuration for the system, and we should aim to drive all logic from these configurations rather than hard-coded values.

## Code Organization

When organizing code, it's important to separate concerns and ensure that each module or component has a clear responsibility. For our project, we should consider:

- **Category Management**: Handling the creation, modification, and retrieval of category properties.
- **Global Configuration**: Managing global properties and ensuring they are accessible throughout the system.
- **Image Processing**: Handling the intake, processing, and likeness comparison of images.
- **Likeness Comparison**: Implementing the logic for comparing images based on likeness thresholds and other relevant criteria.
- **Logic Drivers**: Implementing the logic that depends on category properties and global configurations.
- **Utilities**: Any helper functions or common utilities that are used across multiple modules.

By organizing code in this manner, we can reduce hard-coded dependencies and make the system more maintainable and extensible.

We have an outstanding task of refactoring the existing code to remove hard-coded category references and ensure that all logic is driven by the configuration defined in the category and global property files. This will involve:
    - Identifying all instances of hard-coded category names.
    - Mapping the logic to the appropriate category properties.
    - Updating the code to use the configuration files for decision-making.
    - Ensuring that any new categories can be added without modifying the core logic.
```

    <!-- markdownlint-enable MD013 -->

    ### Oct 30 backup priority after current acceptance (chat, verbatim)

    <!-- markdownlint-disable MD013 -->

    > Ok - I was just wondering if we had a quick solution we could try, but sounds like we circle back on that after we get through the remaning steps we had with where we are at.  I have a lot of other items that we do need to circle back on to replan the next priorities - so this is important to get through - but the way we manage our backups has to be a top one as we're bleeding disk space with so many images we're creating in the process.  So, it's either trimming down on what we do keep/backup, how we back them up and how long we actually keep them before pruning during testing.

    <!-- markdownlint-enable MD013 -->

    Coverage: finish current acceptance before expanding scope -> S15; prioritize
    backup growth in the next review, retained/backup scope, storage format and
    testing retention/pruning -> S24 with S10/S11 and performance T13/T14.

    Coverage: old run pruning and active-source protection -> safety boundary,
S10-S13; output path/configuration -> S4-S6; interrupted staging -> S7-S9;
deduplication and B: I/O -> S11; `ST-v9` -> S13; sandbox reset and eventual
Production runbook -> S14-S16; category/global configuration -> S17-S19.

### Oct 29 overnight authorization (chat, verbatim)

<!-- markdownlint-disable MD013 -->

> I'm giving you full authority to get the sandbox setup cleanly again and I noticed you saw there are files in the sandbox Various that aren't in production - that's correct I pulled files into there for the work we were doing.  That's a great catch.  I really want to know if all the files in the sandbox are also impacting the intake processing for the work we were doing with the latest version - so I feel like if you can get the sandbox back we need to ensure the process is documented and consider this a dry run of a new/fresh sandbox which looks like Production from the galleries.  We'll lose all the previous reports and such - so we'll need to confirm what the performance is now on running the intake and likeness processes that produce all the reports - and hopefully we can get a new baseline and verify all the output locations, clean-up and other pieces we did get ready are in place and what else is truly remaining from the management of all the files in the sandbox as we wrote up the design for.  So, you can complete that along with validating the intake processing and that it catches all the issues that were to be addressed.  I am heading to bed, so it work you can do can handle all the tasks until I wake in the morning.  Getting to the point where we can run the clean rebase in the sandbox and see how all the new various files land and how all the cropping, masking and other enhancements we made are working.  So complete all the work that makes sense given all the issues we've had and check performance of evertyhing running and see if things will be faster after the clean snapshot and sandbox.  I'll want a complete recap written up as well - we didn't even get the recap from 10-27 written, so now we'll miss 10-28 and likely to generate the recap on 10-29 shortly.  Given it's nearly 12:00 am CST where I am at and working.  Finall if we get a clean codebase - we should commit and push all the files in batches for all this work since it's about 2 days worth of work.

<!-- markdownlint-enable MD013 -->


## Oct 30 source snapshot: categories_and_code.md

Source: `feedback/categories_and_code.md`. Coverage: S17-S19. SHA-256: `97bf75e828add5d2b35d29bb6b2c78776a33fb1b828e53499d8cd5c0df4ac170`.
Captured for planning; open tasks are not implementation acceptance.

<!-- markdownlint-disable MD013 MD009 -->
````text
# Categories and Code Organization

This document outlines the approach for managing categories and organizing code in a way that reduces hard-coded dependencies and ensures that logic is driven by configuration files.

## Hard Coding Categories

In reading some code, I see hard-coded references to "Sisters, Models, Angels, Prospects, Potentials and Artists" in logic areas and such.  While that is some of my direct statements, what we need to do is get the categories setup with properties that are defined that drive the decisions about logic instead of the literal about the category name.  

Things like
    - Category Name
    - Description
    - Type (person, animal, artist, etc...)
    - Rank (priority or importance of the category)
    - Path (path to storage)
    - Default Protected (is this protected by default)
    - Thresholds (for likeness comparison)
    - Required Min Number Photos (or whatever is appropriate)
    - Additional Properties (any other relevant properties for the category)
    - Logic Drivers (any specific logic that depends on this category)

Basically anything driving a logic piece that is based on the name right now, needs to be based on logic around the categories and if we add Demons we only really need to add

We'd have some global properties that are part of the entire project scope for all pieces for things we need as well for things like
    - Base Storage Path
    - Default Thresholds (for likeness comparison)
    - Default Min Number Photos (for likeness comparison)

In short, I think we have at least some .json files for how things work already - but I still see code with hard-coded references as well as places where C:\Soverign-Territories\soverign-territories\data\art\likeness-engine-policy.json being used.  So we're probably a bit fragile in how logic isn't always driven from a config.

As you do the analysis, you can probably figure out the logic and what it's trying to do based on category names and we can enhance the properties and ensure that all things are setup properly.

Basically, it's sort of like defining a workspace in comfyui which has default behaviour that you can adjust and setup properties for specifically.  In our case, the categories and global properties act as the configuration for the system, and we should aim to drive all logic from these configurations rather than hard-coded values.

## Code Organization

When organizing code, it's important to separate concerns and ensure that each module or component has a clear responsibility. For our project, we should consider:

- **Category Management**: Handling the creation, modification, and retrieval of category properties.
- **Global Configuration**: Managing global properties and ensuring they are accessible throughout the system.
- **Image Processing**: Handling the intake, processing, and likeness comparison of images.
- **Likeness Comparison**: Implementing the logic for comparing images based on likeness thresholds and other relevant criteria.
- **Logic Drivers**: Implementing the logic that depends on category properties and global configurations.
- **Utilities**: Any helper functions or common utilities that are used across multiple modules.

By organizing code in this manner, we can reduce hard-coded dependencies and make the system more maintainable and extensible.

We have an outstanding task of refactoring the existing code to remove hard-coded category references and ensure that all logic is driven by the configuration defined in the category and global property files. This will involve:
    - Identifying all instances of hard-coded category names.
    - Mapping the logic to the appropriate category properties.
    - Updating the code to use the configuration files for decision-making.
    - Ensuring that any new categories can be added without modifying the core logic.

````
<!-- markdownlint-enable MD013 MD009 -->

## Oct 31 broader LEAN lifecycle direction (chat, verbatim)

Coverage: FULL/LEAN modes, exact native references and retained provenance ->
S25/S26; COMPACT downsized diagnostics and COLLAGE labelled sheets -> T13/S25;
independent history verification and after-run dependency-aware PRUNE -> S10/S24/T14;
FAST and selective FULL reprocessing -> T18 (not implemented by storage modes);
timing/outcome/file/byte statistics -> T17; mixed 20-30 photo end-to-end trials ->
the authorized iteration contract. Defaults and existing-layout migration remain
separate decisions; lossy diagnostics are not original or rollback substitutes.

<!-- markdownlint-disable MD013 MD009 -->
````text
I like that approach so far - and does this align with all the features I discussed for LEAN in terms of storage?  Or is there more yet we can experiment with to really trim down copies of files post image processing for LEAN.  I don't recall all of what I had thought about when I wrote that up as an option for the flow.  Having the ability to first run FAST and/or LEAN as defaults and only resort to a FULL run when I have a true need to keep all the files for inspection and then PRUNE things afterwards and/or create the COLLAGE to reduce the number of files, but still keep some representation of history in that COLLAGE and then all the files created during the intake are preserved in one file instead of all files.  Even if that file is also a smaller copy of the images during processing.  That's fine as we can always selectively re-run for a FULL process on images needing any sort of processing.  Basically that's what I think is most important and then working on performance bottlenecks as continued iterations and ensuring that we don't have image sprawl and are smart about what we do and don't keep and where we keep it and how we name things as well behind the scenes.  Basically ensuring the directory structure is also less nested where it's not needed.

I think we should probably take an iteration or two to work on getting all these in place and focus on LEAN first but making sure these other modes and flows are able to be defined so we can experiment with how they work.  We could even downsize images for historical storage instead of the collage in various modes as long as the FULL approach is retained and we can PRUNE things after we run which could even resort to creating the COLLAGE of a FULL run just to reduce and compress history down.  or we COMPACT and it just downsizes all the files.  Basically there are many ways to look at how we are running so we can run timings to see which is most effective and both storage and the speed.  This also needs to include the statistics in the report for the runs as well so that we also capture those as part of these updates.  The two pieces go hand in hand for sampling the output, speed, storage and will help be figure out what is the DEFAULT flow and which options are best for which purpose.  Keep iterating and running on small batches of 20-30 images from both Various and existing Galleries to see how it works from end-to-end.  Not just intake.
````
<!-- markdownlint-enable MD013 MD009 -->


## Oct 30 source snapshot: gallery_directory_structure.md

Source: `feedback/gallery_directory_structure.md`. Coverage: S1/S4/S5/S17-S19. SHA-256: `c3c323989981f74071b4a2478e0bfda90733655656b420187050b52567efb494`.
Captured for planning; open tasks are not implementation acceptance.

<!-- markdownlint-disable MD013 MD009 -->
````text
I'll want to revisit the gallery structure and directory names to ensure we are getting things properly named within the entire gallery and that the structure directly in the Soverign Territories directory makes sense and supports all the upcoming things cleanly - like the Drakn Bound males, Elder Dragons, future categories like Demons and such. 

I've also use the Various as the Intake directory instead of being a true gallery and in it's current state it's a mixed bag of things right now - so that also needs thought.

I think the templates did get setup at one point to support males and females, but this will be a time to revisit our structure and make sure it makes sense overall and that the GUI is prepared for all the things we will be doing.

I won't want a big bang change - but we need to re-establish the proper future directory structure, make sure backups are working and only backup what is needed so we don't over-consume storage or create unnecessary complexity in the gallery.

Additionally, we should consider how the gallery structure will interact with the GUI, ensuring that any changes we make are reflected properly and that the GUI can handle the new categories and organization without issues. This will help maintain a seamless experience for managing and viewing the gallery content.

This also includes the intake, likeness, cache storage, junk, etc... every directory under B:\Soverign Territories needs to be re-evaludated in the end-to-end structure definition.

We'll also need to sketch out more categories of things to come and show how those will fit into the future state, even if not yet supported - but we know how it'll play out.

All directory paths need to be configured and stored somewhere as well and not having anything hard-coded, assume directory paths and make false assumptions.  I am sure we haven't really gotten all that done.

This would also involve making sure categories are driven from a config and that a category can point to a directory and such.

I'm also concerned that some of the CLI commands have false assumptions or have some embedded directory structure or logic within them we'll need to refactor to be more config driven and not just embedded into the code.

We did start that at one point - but not sure how well that was driven into all the intake processing and how those scripts work, where parameters are stored and how all the erasing is being handled.  Lots to think about in the overall directory structure so a current state analysis will be needed so we can figure out where we are at, what configs do exist, what code needs to be config driven more and what our future will be.

Most importantly, what is the incremental plan to get there or do we need to do larger chunks at a time - test in the sandbox - and come back to prod.  

Basically this will involve the sandbox, how we use it repeatably to test out "high risk" changes to the processes so we don't get to a point like we are at in current production where we ran everything live, had some bugs and the gallery became mis-aligned.

Hope this all makes sense as it's more than just directory - it's directory, configs and processes all in a single brain dump.
````
<!-- markdownlint-enable MD013 MD009 -->


## Oct 30 source snapshot: gui_and _thumbnails.md

Source: `feedback/gui_and _thumbnails.md`. Coverage: S10/S11/S24/S25. SHA-256: `ea78cfb23aaba59ef9141f435828eb98b3330c18b8d3cd9632e0e7a70fa39957`.
Captured for planning; open tasks are not implementation acceptance.

<!-- markdownlint-disable MD013 MD009 -->
````text
We need to analyze all the thumbnails that may or may not be kept and used in all the various gallery pages vs. pointing to the actual images and determine which ones are necessary for performance and usability, and which ones can be removed to reduce redundancy and storage usage.

I know we'll keep backup copies of all the images that happened in the pipeline processing for a period of time and eventually we need to "trash" them and eventually "permantently delete" the trash.  We do need to manage space properly and need to sort that out.
````
<!-- markdownlint-enable MD013 MD009 -->

## Oct 31 duplicate-first direction (chat, verbatim)

Coverage: exact duplicates/references and HTML roles -> S25; conditional
`gallery_org` and installed native reuse -> S26; backup/history amplification
-> S24/S11; recommended-only padding and explicit FULL comparisons -> S25;
FAST processing versus LEAN storage -> T18/S25; incremental sprawl reduction
and priority -> the duplicate-first contract above. No request is treated as
permission to prune existing recovery evidence.

<!-- markdownlint-disable MD013 MD009 -->
````text
I think with storage one of the most saving areas is on the fact that many images aren't being processed and we simply pass the original along and recommend it.  I feel like not having duplicate copies of the exact same file and working off a reference to the same file in each step would be much better.  The .html can still give a visual representation of the same image for original, control and recommended vs. separate copies.  Same will hold true in any instance.  We don't need both an original and gallery that are identical.  I would only want originals saved in something like gallery_org if we ended up processing the image during intake and ended up with a different recommended image for the gallery.  So, exact duplicate storage should be the first target to map our and address.  That'll save on the backups, history and actual gallery.  I also feel like we should not generate padded copies of anything other than the recommended image - so if we're creating padded copies of denoise, tone that are not recommended - that's probably only something we do ON DEMAND as part of some FULL process and not typically the norm.  We really need to cut down on the number of files.  So, read more about other ideas and concepts around storage in the plans, update them with what you think is the right next pieces to incrementally try to trim down on duplicates and excessive copies of files that are not going to be used.  Some capabilities can be part of a FULL run, but in most cases we'll run FAST or LEAN - if I recall those concepts properly.  So, what if we think about those areas and actually start to build towards that.  Reducing sprawl of images is critical to both speed and storage.
````
<!-- markdownlint-enable MD013 MD009 -->
