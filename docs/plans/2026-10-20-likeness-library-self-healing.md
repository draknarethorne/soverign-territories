# 2026-10-20: self-healing likeness library and review workflow

**Status:** active (approved Oct 20, 2026; incremental implementation)

## Purpose

Design an auditable, recoverable workflow that helps the user curate identity
photos and maintain the photo library without hand-moving files or interpreting
long reports. It should distinguish identity evidence from personal preference
and ComfyUI input choice, allow incoming and reviewed photos to be reconciled
together, and gradually make Prospect folders more internally consistent.

The user approved the direction and implementation on Oct 20, 2026. This plan
does not authorize changing matching thresholds or applying photo moves
without the preview, backup, and per-phase safety gates below.

## Decisions and constraints from the discussion

| Topic | Agreed direction |
| --- | --- |
| ComfyUI source photo | Keep `workspaces.json` as the record of the photo currently loaded by a workflow. |
| Identity references | Store trusted identity-photo references separately from the ComfyUI photo in one git-tracked JSON file. |
| Keep versus identify | A photo may be protected because the user likes it without contributing to the identity core. A trusted identity photo may be an anchor without being a preferred art or workflow photo. |
| Angels and Sisters | Protect their galleries from automatic outlier movement. A user can explicitly send an individual photo to Review; any cast-wide force/rebaseline behavior requires a deliberate opt-in and preview. |
| Prospects | Build a guarded, self-healing audit. First flag likely outliers; automatic movement, if validated, goes to Review rather than directly to another identity. |
| Potentials | Keep them matchable. Do not apply Prospect-strength cleanup to one-to-four-photo folders without a separately validated rule. |
| Review and incoming photos | Reconcile both in the same maintenance run. A bounded follow-up audit may use new clusters to resolve remaining same-run candidates, so they do not require a second user-triggered run. |
| Retirement | Distinguish retiring one unusable photo from retiring an entire person. Photo retirement is a recoverable archive that does not re-enter matching; person retirement uses the existing command to return that person's photos to `Various` for normal reprocessing. Whole-folder archival remains a separately labeled operation. |
| User interface | Keep the current People Gallery as a concise overview. Add a focused local review/maintenance gallery for large folders, photo scores, Review images and staged actions. The browser stages actions; a CLI validates and applies them. |
| Review gallery layout | Organize the review view category-first, then person; use a responsive left-to-right image grid with adjustable thumbnail size, face/chest-up framing, and click-through to the full image. Keep scores/actions and the primary identity/workflow reference visible. |
| Identity naming | Let the user stage Prospect/Potential renames in the review UI. Reject collisions unless the user explicitly selects both people for a two-person name swap; preserve both stable identities and `z_` histories. Never rename fixed Angel/Sister slot folders. |
| Potential match context | Show Potentials' closest eligible same-side people and score evidence so the user can decide whether to stage a merge or return the person/photos to normal reprocessing. Never merge from score alone. |
| Report lifecycle | Keep dated report output available for inspection; after the user approves the workflow, support replacing one stable review-report directory. Link a person from the concise overview to their filtered review view when both local reports are available. |
| Metadata | Use machine-readable JSON tied to stable photo identity, not filename grades. Preserve an audit trail and keep user decisions distinct from inferred scores. |
| Tooling structure | Improve the workflow incrementally. Split likeness responsibilities into testable modules and simplify user-facing commands over time; do not combine this with a risky all-at-once rewrite. |
| Python package layout | Move related, low-risk modules and tests into domain packages as work proceeds; keep `bin/*.cmd` stable and audit direct references before moves. Broader `tools/art/` organization has its own [incremental plan](2026-10-20-art-tools-structure.md). |

## Proposed metadata model

### Recommendation to evaluate

Use one versioned, machine-readable JSON file tracked in the repository:
`data/art/likeness-library.json`, validated by
`data/art/_schema/likeness-library.schema.json`. Keep identity metadata and
photo-level decisions in this central catalogue so they remain under Git
versioning and do not need to travel between the external photo library's
folders. Keep path configuration and ComfyUI workflow-photo selection in
`workflows/workspaces.json`; the two files have distinct ownership.

The schema must associate person identity with stable person identifiers and
photo decisions with stable photo identifiers, not only mutable folder names
or filenames. Before implementation, prove how identifiers survive moves,
renames, cropping, deduplication, restoration and backup. Store aliases or
content hashes as needed and reject ambiguous identities rather than guessing.

The existing `z_<name>.txt` remains the human-readable name and history file;
this plan does not migrate or replace it.

### Distinct concepts to represent

- **ComfyUI photo:** the workflow input selected in `workspaces.json`.
- **Identity anchor:** a user-confirmed face reference that contributes to a
  person's trusted identity core.
- **Protected photo:** do not automatically move or reclassify this photo.
  Protection does not imply that it belongs in the identity core.
- **Ordinary photo:** available for scoring and conservative automatic review.
- **User-sent-to-review:** remove the photo from its current person gallery
  and active identity evidence; compare it against that person and every other
  candidate through the normal combined matching pass.
- **User-rejected-to-pool:** return the photo to `Various` and process it like
  new incoming material. Do not give its former folder priority, while still
  allowing a normal whole-library match to find that folder if the evidence
  independently supports it.
- **Photo retirement:** a user decision that a photo is unusable. Archive it
  recoverably under a photo-specific `_retired` subtree, remove it from active
  identity evidence and exclude it from matching. It is not Review,
  Reject-to-Various, or deletion.
- **Person retirement:** use the existing `likeness retire` operation to send
  the person's photos to `Various` for normal reprocessing. Label the
  destination in the preview. Keep `archive-list` whole-folder archival
  distinct; it must not be presented as the same action.
- **Observed match and score:** a generated suggestion, never user-authored
  identity truth.
- **Action history:** what was proposed, approved, applied, reversed, by which
  command and when.

The schema must support more than a fixed number of anchors. The user expects
to be able to protect a trusted core of roughly five to ten images when useful,
but some people may have fewer or more suitable references.

### Stable photo identity

Before finalizing the schema, prove that a photo keeps its metadata when it is
renamed, moved, scaled, cropped, deduplicated, restored, or found in a backup.
The current tools recognize several source IDs and cache face data by content;
neither fact alone proves that every transformation can be joined safely.
Reject ambiguous IDs and stale manifests rather than guessing. Record hashes
and aliases as needed, and test restoration and duplicate cases.

The initial helper generates opaque UUID-based person IDs and photo IDs from
`comfy_workflows.photo_key()` on originals-managed filenames. `originals.py`
preserves the embedded source ID when folder prefixes change, and the crop
command replaces a photo under the same name while archiving its uncropped
bytes. Thus a crop retains the filename-derived ID but changes the content
hash; metadata refresh and restore behavior still need explicit tests. Duplicate
and backup-restore continuity are not yet proven, so A4 remains open.

## Matching and self-healing policy

### Keep current thresholds until action-specific validation

Treat the current scores as calibrated starting points, not universal weights.
Measure false assignments and missed matches separately for:

1. a photo assigned to an existing person;
2. a photo returned from Review to its source folder;
3. a photo sent from Review to another existing person;
4. several photos clustered into one new person;
5. two person folders merged;
6. a photo flagged as an outlier from its current Prospect.

Use user-confirmed examples, including laughter, unusual angles, expressions,
lighting, makeup and changes in appearance. Report precision and recall for
each action. Do not lower thresholds just to shrink Review counts. A cutoff
that is acceptable for a suggestion may be unsafe for an automatic move or
whole-folder merge.

### Build a robust identity core

- Use user-selected identity anchors as trusted evidence where present.
- Keep protected-only photos in the person's gallery, but exclude them from
  the identity core unless the user also marks them as anchors.
- For people without user-selected anchors, compute a provisional robust core
  from ordinary gallery photos. Show which images formed it and why.
- Do not let a suspected outlier shift the core used to judge itself.
- Preserve a minimum viable core. A cleanup pass must not move the last
  trusted anchor or reduce a Prospect below the agreed minimum core size.
- A low score alone is not sufficient to reassign a photo. Require evidence
  against the trusted core, a strong destination match with a clear margin, or
  otherwise stage it in Review.

### Scope by category

- **Prospects:** run an outlier audit. Initially report-only; after validation,
  permit eligible ordinary outliers to move to that person's Review folder.
  Do not auto-reassign directly from one Prospect to another in the cleanup
  action.
- **Potentials:** keep all available photos for future matching. Flag concerns
  for review; do not apply Prospect outlier rules until the photo count and
  thresholds have been validated for this category.
- **Angels and Sisters:** never move ordinary photos automatically as part of
  routine maintenance. User-staged actions may move selected photos into
  Review. Trusted anchors and protected photos remain immovable by ordinary
  runs. Any force operation must name its scope, preview all proposed changes,
  and require explicit confirmation.
- **Various and Review:** compare against all active person folders and against
  candidate groups formed from both sources in the same planned batch.
  Ambiguous photos remain staged; they are not silently turned into a new
  identity.

### One reconciliation plan for Review and incoming photos

The current routine processes Review before sorting the pool, so a group made
from that run's incoming photos cannot serve as a destination until a later
run. The new planner should take one read-only snapshot of person galleries,
Review, and `Various`, then:

1. Establish each person’s protected/trusted core without including Review
   photos in the gallery centroid.
2. Score ordinary Prospect photos for potential outliers.
3. Add user-sent-to-Review photos and eligible incoming pool photos to the
   same candidate set.
4. Compare candidates against all current person cores and cluster candidates
   with one another.
5. Treat new clusters as provisional destinations in this same run.
6. Apply approved Prospect outliers to Review in the planned state, then add
   those and user-staged Review/Various photos to the candidate graph.
7. Form provisional clusters; compare unresolved candidates with both existing
   people and new clusters, including same-run clusters formed from Sophie-like
   user-rejected photos.
8. Repeat only the candidate-matching step against the frozen identity cores
   until no additional unambiguous destinations emerge. Each photo can be
   assigned once per run; assignments cannot feed back into or change an
   existing identity core during that run. Ambiguous or unstable cases remain
   in Review or the pool.
9. Produce one complete plan, checking conflicts, minimum cores, category
   boundaries, protected IDs, and stale file hashes before any disk change.
10. Apply approved actions and regenerate galleries, reports and input sync;
    save a recoverable action record.

This is a bounded fixed-point calculation over a finite candidate set, not a
loop that repeatedly changes files and rescans until it happens to look right.
All scores use the frozen pre-run person cores; new clusters can attract
candidate photos but cannot mutate existing person identities mid-run.

## Review interface and action manifest

### Two complementary gallery views

- Keep `people_gallery.html` concise and useful for browsing identities,
  pairings and readiness.
- Add a separate local `people_gallery_review.html` for maintenance. It should
  surface Gallery and Review photos together, show scores/order and reasons,
  and distinguish trusted core, protected, ordinary, Review and suggested
  outlier items.
- Support large libraries with filtering, pagination or incremental display,
  lazy thumbnail work and cached derivatives. Do not require generating or
  embedding every full-size image just to inspect a 100+ photo person.
- Show which comparison was used: own trusted core, current person candidate,
  another person, or provisional cluster. Keep the numerical score
  interpretable and do not present it as certainty.
- The report is local and read-only. It must not run filesystem operations or
  fetch images or scripts from third-party services.

### Staged actions

The page should export a versioned JSON action manifest for a CLI to inspect
and apply. The supported actions should be explicit and separate, such as:

- mark/unmark identity anchor;
- protect/unprotect from automatic movement;
- send a selected photo from a person gallery to Review (remove it from that
  person's active identity core);
- reject a selected photo to `Various` for normal incoming-photo processing,
  without preferring its former person;
- approve a Review photo back to its person;
- request reprocessing through the combined Review/Various planner;
- accept or reject a proposed match or cluster.
- stage a Prospect/Potential name change, or explicitly pair two people for a
  collision-resolving name swap.
- later, retire one unusable photo to the photo archive, or retire a Potential
  or Prospect through the existing CLI operation that returns its photos to
  `Various`. Keep retirement out of the first Review/Reject delivery.

The manifest should use stable photo IDs, expected content hashes, current
source locations, destination intent, actor/reason and schema version. The CLI
must reject stale or ambiguous entries, show a dry-run summary, create and
verify a backup before moves, log each action, and support undo. Applying a
manifest must never mean “trust the old score”; recalculate current evidence
and enforce current protections and category boundaries.

The interface must make **Review** and **Reject to Various** distinct. Review
means compare the photo against all people including its former person.
Reject-to-Various means start the normal incoming-photo path, without giving
the former folder priority; a strong whole-library match may still return it
there. Neither action deletes the photo, retires a person, nor claims identity
truth.

Sending a protected photo to Review is a deliberate, photo-specific override
of the automatic-move protection; it does not authorize changes to any other
protected photo. A photo sent to Review or Reject-to-Various stops being an
active identity anchor for its former person. Preserve the previous decision
in history and require confirmation in the staged-action preview.

### Review-folder location

Initially retain person-local physical Review folders to avoid a risky library
migration. The review interface should aggregate them into one navigable
maintenance view. Evaluate a root such as `Review/Prospects/<name>` only if
the interface exposes a concrete limitation that cannot be solved by
aggregation; if needed, migrate with a verified backup and reversible mapping.

## Incremental delivery and verification

Implement one working phase at a time. Each coherent, validated increment
updates its directly related documentation and is committed before unrelated
work begins. Do not leave a broken or half-migrated state between increments.

### Phase A — baseline and design contract

- [x] **P1 ai** A1 Capture current settings, command behavior, reports and
  focused test results; inventory every command that moves, merges, protects
  or reclassifies images.
- [x] **P1 you** A2 Approve one git-tracked global JSON catalogue, separate
  from `workspaces.json` and `z_<name>.txt`.
- [x] **P1 you** A3 Confirm Review removes the photo from its active identity;
  Reject sends it through the normal `Various` path without source-folder
  priority.
- [x] **P1 ai** A4 Define the stable person/photo ID model, schema, score/action
  semantics, failure behavior, audit guarantees and safety targets. Prove
  identity continuity through move, rename, crop, duplicate and restore cases.

**Exit:** the accepted decisions above and verified stable-ID/schema design.

### Phase A baseline record

The command inventory is maintained in the [likeness guide](../art/likeness.md)
and [bin help](../../bin/help.cmd). Image-changing surfaces were traced through
`bin\library.cmd` (`library_sync.py`), `bin\likeness.cmd` (`likeness.py`),
`bin\originals.cmd` (`originals.py`), and the staged review-action CLI.
Relevant operations include ingest/sort, review, singles/rematch, pullback,
crop/junk, artist grouping, merge/retire/archive, cast promotion/swap, and
Prospect/Potential rename. Their preview/apply behavior and recovery paths are
documented beside each command. Reports, caches, and UI outputs are kept apart
from source-photo and catalogue writes.

At the Oct 20 baseline, the active likeness catalogue is empty. Effective
settings combine defaults in `tools/art/likeness.py` with
`workflows/workspaces.json`: assign `0.40`, margin `0.10`, cluster `0.25`,
minimum new cluster `3`, outlier `0.15`, similar-person report `0.30`, minimum
face size `60`, secondary-face ratio `0.30`, singles `0.35`, Prospect rematch
`0.48`, cast report `0.50`, and cast merge `0.55`. The configured Angelica
anchors, keep-photo heroes, and one `different` pair remain as recorded in the
workspace config. No thresholds changed in this plan.

Stable photo IDs come from the embedded source key in the original filename,
independent of folder and name prefix; tests cover move/rename, scaled suffix,
crop (same ID, changed SHA-256), ambiguous duplicate IDs, and a verified
backup-copy/restore. A staged action manifest separately uses a full SHA-256,
so edits invalidate old manifests without changing the source identity.
Ambiguous active copies and stale hashes are rejected, not guessed. A4 is
complete for originals-managed IDs and the current backup/crop flows; future
transformations that discard source IDs must remain explicitly unsupported
until they have an alias or restore mapping.

### Phase B — metadata and read-only audit

- [x] **P1 ai** B1 Add and validate
  `data/art/_schema/likeness-library.schema.json` and the versioned
  `data/art/likeness-library.json` catalogue. Register the catalogue with the
  data validator and cover schema, format and referential checks with focused
  tests.
- [x] **P1 ai** B2 Add library metadata read/write helpers with atomic writes,
  explicit errors, and no edits to `workspaces.json` or `z_` history for
  identity/protection choices. The writer targets only the catalogue; tests
  cover round-trip, validation failure, failed replacement and untouched
  workspace/history files.
- [x] **P1 ai** B3 Generate a read-only trusted/provisional core, photo score
  ordering, outlier suggestions and human-readable reasons with
  `likeness audit-core`. The command never moves images; it can update the
  existing embedding cache.
- [x] **P1 ai** B4 Test changed-folder mappings, duplicate/ambiguous IDs,
  stable IDs with changed crop hashes, trusted anchors, protected-only photos,
  small folders and stale metadata. Reject duplicate active-folder and
  identity-anchor ownership; report renamed-folder mismatches without applying
  their identity decisions. Restore/backup continuity remains open under A4.
- [ ] **P2 either** B5 Establish user-confirmed examples and report
  action-specific precision and recall without changing production thresholds.

**Exit:** repeatable output; no writes except explicitly generated reports/cache;
action-specific measurements on user-labelled examples.

### Phase C — focused review gallery

- [x] **P1 ai** C1 Produce a separate high-volume
  `people_gallery_review.html` with Gallery and Review photos, score ordering,
  filters and identity/protection states. Keep the existing overview concise;
  the dedicated launcher writes content-cached thumbnails beside the report.
- [x] **P1 ai** C2 Add staged anchor/protect, Review, Reject-to-Various and
  Review-approval actions; export a versioned JSON manifest by download.
- [x] **P1 ai** C3 Keep source files and catalogue read-only (allow only an
  explicit manifest download); use bounded/lazy thumbnails and benchmark
  100+ photo folders.
- [x] **P1 ai** C4 Organize review work by person, with within-person score
  ordering, Review-only and low-score views, an adjustable score cutoff, and
  a visible reference photo when filters hide it. Distinguish the workflow
  selection and user-confirmed identity anchor from a provisional scored
  reference; preserve the flat all-photos view.
- [x] **P1 ai** C5 Make category selection drive the person list, replace
  vertical person columns with a responsive adjustable-size grid, show a
  face/chest-up local thumbnail while linking to the full image, and retain
  reference/photo decision information in filtered views.
- [ ] **P1 ai** C6 Add Potentials' closest-person evidence and staged rename
  and explicit two-person name-swap controls; preserve name history and stable
  identity IDs, reject unselected collisions, and keep fixed cast slots.
- [ ] **P2 ai** C7 Keep dated report output available, then support replacing
  a stable output directory and linking the concise overview to a filtered
  person review page.

**Oct 20 gallery update:** C5 is implemented. The category filter now
constrains the person selector, person sections fill the available width with
responsive left-to-right grids, and small/medium/large tile sizes are
selectable. Each source photo has cached head and chest-up derivatives named
from its master stem and content key; both link to the full image. Potential
gallery records now show closest-other-folder score evidence. C6's rename and
explicit swap controls remain open.

The Oct 20 real-library run indexed 2,668 active Gallery/Review photos into
the dated report at `B:\Sovereign Territories\_reports\likeness-review-20261020-1339\people_gallery_review.html`.
The library has four Gallery folders with at least 100 photos (maximum 322).
The initial report and thumbnail-cache build took 88.3 seconds; a cached
regeneration took 7.6 seconds and produced a 2.25 MB standalone HTML page with
2,668 content-cached thumbnails. The browser renders at most 100 cards at a
time and lazily loads images. A real-library validate/preview of a staged
Prospect Review move passed, and the source SHA-256 remained unchanged. That
example was not applied. It exposed and fixed a previous bug: the review page
had placed the embedding cache's SHA-1 into the manifest's SHA-256 field;
regression tests now require real 64-character SHA-256 values.
The grouped-gallery refresh at
`B:\Sovereign Territories\_reports\likeness-review-20261020-grouped\people_gallery_review.html`
contains all 2,668 photos and cached thumbnails across 261 folders. It
identifies 146 folders with a usable primary reference and labels 21
workflow-selected images; the identity catalogue is still empty, so no
user-confirmed anchors are present in this real-library report.

**Exit:** user can inspect a large person and stage actions without hand-editing
JSON or moving files. C5-C7 are iterative refinements requested after the
first real-library report; they're tracked separately from the completed C1-C4
baseline.

### Phase D — safe action CLI

- [x] **P1 ai** D1 Add manifest validate and preview commands with explicit
  rejection of stale hashes, missing/ambiguous IDs, invalid moves and
  conflicting actions. Validation and preview remain read-only.
- [x] **P1 ai** D2 Add backup-verified apply and undo for metadata-only
  decisions and user-staged photo moves; record an auditable action history.
- [x] **P1 ai** D3 Verify category rules, protected anchors, one-time anchor
  removal on explicit Review/Reject, and path containment before file writes.
- [x] **P2 ai** D4 Keep existing commands as compatibility entry points while
  the new workflow is tested; no existing command entry points were replaced.

`bin\likeness-actions.cmd apply FILE.json --apply` backs up the active photo
library, configured inputs, workspace configuration and catalogue, revalidates
the manifest, then applies file and metadata changes. `undo [BATCH_ID]`
previews by default; with `--apply`, it backs up and reverses only the newest
active action batch when recorded files and metadata still match. Application
is not run against the real photo library during implementation.

**Exit:** stale or conflicting manifests fail explicitly; valid operations are
recoverable, logged and idempotent where appropriate.

### Phase E — combined Review and pool reconciliation

- [ ] **P1 ai** E1 Plan user-staged Review photos, incoming `Various` photos,
  and validated Prospect outliers together against one frozen library snapshot.
- [x] **P1 ai** E2 Cluster rejected, reviewed and incoming candidates together;
  allow new provisional clusters to become destinations in the same run.
- [x] **P1 ai** E3 Iterate candidate matching to a deterministic fixed point.
  Each candidate is assigned at most once; ambiguous or unstable candidates
  stay staged. Do not mutate established identity cores mid-run.
- [x] **P1 ai** E4 Add an empty-pool mode for Review-only and self-healing runs.
- [ ] **P1 either** E5 Compare preview and applied results with user decisions
  before enabling any automatic action beyond sending validated Prospect
  outliers to Review.

**Oct 20 implementation:** `likeness reconcile [--out FILE.json]` now builds
one read-only snapshot of current person cores, usable Review photos, and
usable `Various` pool photos. It applies stable average-linkage clustering to
the combined candidate set, allows an eligible new cluster to attract a
remaining candidate without changing that cluster's frozen vector, and
reports ambiguous, protected, duplicate-ID and unassigned candidates as held.
An empty pool is supported. The command does not move files, change catalogue
metadata or apply any matching decision; it can update the embedding cache.
Prospect outliers are deliberately not fed into this planner yet: Phase F1
must first provide report-only outlier evidence, and E1 will then be completed
with that candidate source. No real-library reconciliation or apply has run.

**Exit:** validated routing behavior; ambiguous cases stay in Review/pool and
same-run clusters can resolve candidates without order-dependent cascades.

### Phase F — guarded Prospect self-healing

- [ ] **P1 ai** F1 Add report-only Prospect outlier detection against
  trusted/provisional cores, with scores and destination evidence.
- [ ] **P1 either** F2 After action-specific validation, allow only eligible
  ordinary Prospect outliers to enter Review; preserve protected images and a
  minimum viable identity core.
- [ ] **P1 ai** F3 Keep routine Angel/Sister gallery processing report-only.
  Add only a deliberately explicit, previewed action for cast photos selected
  by the user.
- [ ] **P2 either** F4 Define and verify action-specific precision/recall
  gates before enabling each automatic Prospect operation.

**Exit:** action-specific safety targets pass; rollback and “why moved” records
are verified on real, backed-up batches before enabling routine use.

### Phase G — add photo and person retirement to the review interface

- [ ] **P2 ai** G1 After Review/Reject workflows are working, expose
  photo-level retirement of unusable images and whole-person retirement of
  Potentials/Prospects through explicit, distinct manifest actions.
- [ ] **P2 ai** G2 Show each operation's destination and consequences in
  preview. Keep photo retirement, person retirement, Review, Reject-to-Various
  and whole-folder archival distinct.
- [ ] **P2 ai** G3 Test cancel, stale-manifest rejection, backup, apply,
  restore and undo for both retirement scopes against temporary libraries.

**Exit:** the gallery can stage both retirement scopes without implementing
file movement in the browser or silently changing existing CLI semantics.

### Phase H — integrate, modularize and document

- [ ] **P2 ai** H1 Integrate the planner into `bin\library.cmd`, retaining
  preview and verified-backup behavior; support empty-pool maintenance.
- [ ] **P2 ai** H2 Extract metadata, core/scoring, planning and report/action
  responsibilities from `likeness.py` in small, behavior-preserving,
  test-covered changes. Do not do an all-at-once rewrite.
- [ ] **P2 ai** H3 Inventory all effective thresholds and options in one
  documented table; add a command that prints current effective values and
  action-specific calibration. Do not change production values without
  measured results and a documented decision.
- [ ] **P2 ai** H4 Simplify the user-facing workflow and CLI options only
  after the replacement is proven; keep current command entry points working
  until migration is verified.
- [ ] **P2 ai** H5 Update the likeness guide, original-photo runbook, gallery
  help, tests, schema docs and generated queue after each relevant phase.
- [ ] **P3 either** H6 Keep broader art-authoring and ComfyUI batch-execution
  interfaces as a future GUI roadmap, not a deliverable of this likeness plan.
  Ensure the manifest and metadata design can integrate with those tools
  without introducing browser-side file access.

**Exit:** existing ingest, review, crop, sorting, selected workflow photos,
archive history and artist separation behave as before unless explicitly
changed and covered by tests.

### Phase I — recover and manage person names

- [ ] **P1 ai** I1 Trace and reproduce name continuity through promotion,
  return, merges and Sister/Angel swaps. Include the original cast folders
  whose `z_` files are empty or have no `name:` header; test names recovered
  from the filename, missing files, and names reconstructed from history.
  Determine what evidence can recover the original name without guessing.
- [ ] **P1 ai** I2 Add regression coverage for name preservation across every
  supported identity move, including empty/legacy `z_` files and Draknora's
  reported case. Keep the Angel/Sister slot folder name distinct from the
  person's recorded Prospect/Potential identity.
- [ ] **P2 ai** I3 Add staged GUI renaming for Prospects and Potentials.
  Preserve the previous name in `z_` history and stable catalogue identity;
  do not rename fixed Angel/Sister slots. Reject case-insensitive name
  collisions unless the user explicitly selects a second person for a
  two-person name swap.
- [ ] **P2 ai** I4 Add preview, backup and apply support for staged name
  changes. Update the catalogue's current folder and history, retain both
  `z_` histories, and refresh `people_index.csv` and `.md` after relevant
  rename, promotion, return or swap operations.
- [ ] **P2 ai** I5 Verify collisions across Prospects and Potentials, including
  case-only variants, and test rollback when either side of a name swap fails.

**Exit:** a user can recover or change a Prospect/Potential's recorded name
without losing history, colliding with another person, changing fixed cast-slot
names, or leaving the gallery and people index inconsistent.

## Safety and acceptance criteria

- No automatic deletion. Every source remains recoverable from its original
  location, archive, backup or action history.
- Identity anchors, protection, workflow-photo choice and inferred match are
  independent fields and visibly explained.
- Routine processing never moves protected photos or Angel/Sister gallery
  photos without an explicit user-staged action.
- Prospect cleanup cannot remove trusted anchors or take the folder below its
  minimum core; ambiguous outliers go to Review, not another person.
- Review and pool candidates are considered together against existing people
  and same-run provisional clusters; bounded iteration is deterministic and
  cannot oscillate or reassign a candidate more than once.
- The user can audit exactly why a photo was held, returned, moved to Review,
  or matched elsewhere.
- A preview and verified backup precede every batch with file changes.
- Existing thresholds remain unchanged until action-specific validation
  demonstrates acceptable precision and recall.
- Large-gallery UI performance and the action-manifest workflow have focused
  tests, including stale hashes, missing files, duplicate IDs and undo.

## Existing plan reconciliation

- D2 and D3 of the tooling-debt plan are transferred to Phase H: modularize
  likeness responsibilities incrementally, document the settings in one place,
  provide an effective-settings view, and calibrate action thresholds from
  evidence. The settings work must not change production thresholds without
  measured results and a documented decision.
- D12 is superseded by this plan's metadata, review-gallery, manifest and
  combined reprocessing workflow. Its requirement for a recoverable,
  previewable individual-photo exclusion is retained in Phases C–E.
- D11's archive-first handling of a false whole-person folder remains open in
  the tooling-debt plan. Phase G keeps person retirement's existing
  `likeness retire` behavior separate from `archive-list` archival and
  photo-level retirement; none of these operations deletes files.
- The manual edit-prompt plan remains independent and active.
- The Oct 19 library plan's manual Sophie pullback/reprocessing steps are
  superseded by this plan's review workflow; its unrelated Junk, gallery,
  chest-crop and outcome-review tasks remain open. Neither Oct 19 plan is
  ready to archive.
- Keep the proposed CLI-consolidation plan separate. Preserve current command
  entry points until any new workflow is tested and migration is verified.
- Organize Python files under `tools/art/` incrementally under the
  [art-tools structure plan](2026-10-20-art-tools-structure.md). The metadata
  foundation is in `tools/art/likeness_library/`; the directory name avoids
  shadowing the existing `likeness.py` module.
- The separate review gallery and local manifest are the chosen initial
  interface. Broader art-authoring and ComfyUI batch execution remain future
  UI work, outside this plan.

## Approved design decisions

| ID | Decision |
| --- | --- |
| D1 | Store identity metadata and photo decisions in one versioned, git-tracked `data/art/likeness-library.json`, validated by a schema beside the art schemas. Keep workflow paths and selected ComfyUI photos in `workflows/workspaces.json`; do not replace `z_<name>.txt`. |
| D2 | Keep identity anchors, keep/protect preferences, and workflow-photo choice distinct. A photo can be protected but not an anchor. |
| D3 | Sending an image to Review or Reject-to-Various removes it from its former person's active identity evidence. Review compares it against all people, including its former person. Reject follows the regular incoming pool path without a special preference for the former folder. |
| D4 | Permit a bounded, deterministic same-run follow-up using provisional clusters to resolve eligible candidates. Do not mutate existing identity cores mid-run, reassign candidates repeatedly, or loop without a convergence condition. |
| D5 | Keep current person-local Review folders and aggregate them in a separate, efficient review gallery. Do not move the physical Review tree unless later evidence requires it. |
| D6 | Add photo- and person-level retirement to the GUI after Review/Reject works. Photo retirement archives one unusable image recoverably and excludes it from matching. Person retirement uses the existing CLI behavior and returns that person's photos to `Various` for reprocessing. Keep both distinct from Review, Reject-to-Various and whole-folder archival. |
| D7 | Implement and commit validated increments. Keep larger art-authoring and ComfyUI execution UI as future scope, while preserving integration paths. |
| D8 | Keep the photo archive in a separate `_retired/photos/` subtree; preview the path, preserve content and history, and support restore. Treat `archive-list` as a separately named whole-folder archive operation. |
| D13 | Keep a person's recorded identity name separate from fixed Angel/Sister slot folders. Prospect/Potential name changes must preserve `z_` history, reject collisions by default, and permit a two-person swap only when both identities are explicitly selected. |

## Raw user feedback

I like the recommendations, but have a few comments about each item and then we can build the plan as a whole.  1) I agree that we should keep those separate and workspaces.json can identify the comfyui photo and we'd store the other trusted identities in a new file or set of files (which ever seems the simplest - using a z_xxxx.json convention if we choose to store it in the gallery directory along side the z_xxx.txt file)
2) I agree with that split and it makes sense as there are some photos that I know I want to keep that are laughing or smiling or bad angles and don't want to use them as the identity, just keep them for my use for that person.
3) and 4) I like the idea of having the audit and I also like the idea of moving things into the Review folder more automatically and also to have the Review folders processed in conjunction with the incoming images in the Various/gallery - so it's possible we could cluster a new identity in the same run - not a separate run.
5) I agree with this as well, and if the people_gallery allows me to "reject" a picture and move it to the Review for auto processing, then it's only when I specifically chose to move a picture out of an Angel or Sister that it would pull it back to review.
6)  Yes, if the gallery can be interactive to stage work into a .json or some file for the CLI to process and/or pre-process ahead of a new run on an incoming batch of new Various/gallery photos (or even empty for just a self-healing/clean-up run) it prevents me from manuallying having to run many different CLI commands that already exist to do much of this work.
7) Agree, you convinced me.  The id of the file and the metadata in a .json file are a solid approach and it's auditable as well - and can be used for also me as well.
If we can build out the plan for this, work on the CLI commands, the gui, etc... then I can actually go into the people gallery and try to use it to protect files for Sophie and many others to generate the file for the processing.
I also think as we do this it might also be time to include some incremental pieces for addressing the tooling-debt and simplifying the cli options as we go and either making dedicated cli commands for certain actions instead of having a monolithic likeness.py that does everything and is huge and unmaintainable.
8)  Basically, there is a lot of reading in reports and manual review items that if we could either incorporate that into the existing people_gallery or make a different people_gallery_review.html where I do larger maintenance would be decent.
That way for people who have 100+ images I'd have a place to do that review and it wouldn't pollute the existing gallery and would not require so many thumbnails to be generated if we can figure out a way to make that efficient.
Basically looking at the entire process end-to-end with the insight into how things work.  We can build things incrementally in the plan and test out different pieces - but getting the interactive GUI up prevents me from hand-writing .json files, hand moving files in/out of review or back into the Various/gallery and brings more self-healing/self-adjusting on the low scoring items that are not protected within a persons gallery.

## Raw approval and follow-up direction

I am ok with one single .json file for the reasons you suggest and want to keep it in the location so it's maintained in git for versioning as well.  Same with how we have workspace.json for the other generation of the workflows, prompts, etc...

Yes, if I send something to Review or even Reject it all the way back into the Various/gallery for a total reprocessing it should not count as part of the identity as I'm basically trying to see if it would either automatically come back to the person from Review or find another match, if I Reject it back into the Various/gallery - it's really up for reprocessing like a new incoming image without first attempting to see if it matches the person it originally came from.
I think that's the two approaches I like to see what happens.  With Sophie, I'd pick some to be Rejected and some to be Reviewed.  I'd also like the people gallery to allow me to Retire a Potential or Prospect as well as part of this - but that can be added later one after the Review/Reject process is working.  We already support CLI for Retiring, so it should just be GUI and building the config to drive the CLI for that work.

I am also infavor of automatically moving images back to Review for ones I may have missed based on the scoring - so if I move 10 images out of Sophie to Review (they are not longer part of her identity and I missed one - I would hope that one would be caught and moved into Review for a re-processing just like others.)
Basically bumping things into Review automatically based on the identity of person changing as I move files out should also pickup the "trash" so to speak and bring it along with the batch of other files to Review OR it could put it into Review for another run/iteration - which ever is cleanest from a coding and processing.
Ideally, it could happen as part of a larger batch so I don't need to iterate twice on the process - but we can handle it in incremental work as well.  I guess what could happens is after the processing an audit could take place and IF there was items still in Review or moved into Review it could then see where to put them?
I mean - if we automatically figure out that an image in Sophie was a nearly identical match to a new Prospect from the ones I moved out - I'd want that to just move as part of the cycle and not require yet another iteration.  Whatever can happen the cleanest in terms of coding.  If the process takes longer and runs a few iterations, that's fine as long as I end up with a clean result in the end based on the way we're planning to protect images and such.

Over time we can add more capabilities to the GUI to support ALL the CLI commands and if we need to pivot from an .html to something else - that's also a possility -- I have other things in mind for a GUI that would allow me to trigger a batch of workflow runs based on the images (using their ID), making sure they were in the ComfyUI inputs properly
and automatically running a batch of workflows for a series of different images instead of me having to do it manually in the ComfyUI ... but that's another topic - but letting you know I have more ideas in mind for GUI work with respect to the way we manage the .json data today to build workflows/prompts and running them.
Right now - it's all based on doing work in VS Code to manage the .json and I have to shift to ComfyUI for managing the execution of the workflows.  So the gallery GUI's are a step in making things more user friendly - which will allow for my daughter to work on the image library, art .json libraries, prompts and executing workflows all from a Thorne set of UI's.  Anyway - that's just for you to think about as you work on the plans and layout a longer term picture.

That said - I agree with the plan as per my comments above.  You can move it to an official plan, archive and update other existing ones and let's get started on the foundational pieces and implement them automatically.
I give you full permission to keep going, make decisions and only stop if you are truly blocked and you must get an answer from me.  OR require me to use the GUI - when you get there.
We'll need all documentation, tests and commits as you go so it's not one huge piece of work.  As you build, test and document pieces - we can commit as long as things are working and you move onto the next chunk of work.  That way it won't be as huge of deal in the end.  Make sense?  If so, then get rolling!

When it comes to Retire - I want to be able to Retire either an individual picture for a person or the entire person - so that can be in the plan and a decision as well.  I'm reading our docs and watching you work, so that's the iterative feedback loop we've got going.  Keep on working as I love what you are doing so far and the speed at which you're working.
