# 2026-10-20: self-healing likeness library and review workflow

**Status:** active (foundation work retained; engine scope reconciled with the Oct 21 plan)

## Purpose

Design an auditable, recoverable workflow that helps the user curate identity
photos and maintain the photo library without hand-moving files or interpreting
long reports. It should distinguish identity evidence from personal preference
and ComfyUI input choice, allow incoming and reviewed photos to be reconciled
together, and gradually make Prospect folders more internally consistent.

The user approved the direction and implementation on Oct 20, 2026. This plan
owns catalogue/stable-ID, staged-action, review-interface and recovery
foundations. The later
[unified processing contract](2026-10-21-likeness-rebaseline-and-family-naming.md#unified-processing-contract-oct-21-reconciliation)
owns matching, clustering, tier-aware automation, configuration, and clean
sandbox/production rebuilding. It supersedes the earlier audit-only and
blanket lower-tier restrictions here. Production changes still require its
acceptance/backup gates; authorized sandbox experiments make real placements
without per-photo approval. The Oct 22 implementation now shares candidate
planning and incoming/Review execution. Whole-identity maintenance now has
tested apply/undo paths and synthetic no-reset stability cases; labelled
real-batch acceptance remains open. The Oct 22 morning continuation also
implements staged person-wide protection for Models/Prospects under Oct 21
task 5.1i, separately from photo protection.

## Decisions and constraints from the discussion

| Topic | Agreed direction |
| --- | --- |
| ComfyUI source photo | Keep `workspaces.json` as the record of the photo currently loaded by a workflow. |
| Identity references | Store trusted identity-photo references separately from the ComfyUI photo in one git-tracked JSON file. |
| Keep versus identify | A photo may be protected because the user likes it without contributing to the identity core. A trusted identity photo may be an anchor without being a preferred art or workflow photo. |
| Angels and Sisters | Protect their galleries from automatic outlier movement. A user can explicitly send an individual photo to Review; any cast-wide force/rebaseline behavior requires a deliberate opt-in and preview. |
| Prospects | Use the Oct 21 tier-aware action policy: eligible unprotected identities may attach, merge/split and reclassify automatically under validated rules. Selective Review is for uncertainty, not a mandatory intermediate for every lower-tier action. |
| Potentials | Preserve valid pairs and unmatched singletons, keep them matchable, and allow configured organic growth. Group formation is separate from minimum evidence for destructive cleanup. The older minimum-three clustering gate is not a goal. |
| Review and incoming photos | Reconcile both in the same maintenance run. A bounded follow-up audit may use new clusters to resolve remaining same-run candidates, so they do not require a second user-triggered run. |
| Historical cast-audit priority (Oct 20) | The report-only cast audit was a diagnostic milestone, not the final engine or a permanent prohibition on automation. Later engine work belongs to the Oct 21 plan; its selective cast Review never silently admits candidates to cast Gallery/core. Preserve former-identity history and do not classify from raw counts alone. |
| Retirement | Distinguish retiring one unusable photo from retiring an entire person. Photo retirement is a recoverable archive that does not re-enter matching; person retirement uses the existing command to return that person's photos to `Various` for normal reprocessing. Whole-folder archival remains a separately labeled operation. |
| User interface | Keep the current People Gallery as a concise overview. Add a focused local review/maintenance gallery for large folders, photo scores, Review images and staged actions. The browser is strictly a staging/export surface: it never renames folders, edits `z_` files, or writes catalogue data. Photo and person changes are exported in the versioned JSON manifest; a CLI validates, previews, backs up, applies and can undo them. Person changes use a separate `personActions` array so they cannot be confused with photo actions. |
| Review gallery layout | Organize the review view category-first, then person; use a responsive left-to-right image grid with adjustable thumbnail size, face/chest-up framing, and click-through to the full image. Keep scores/actions and the primary identity/workflow reference visible. |
| Gallery consistency | Keep the overview and full review in the same category/person order and use the same selectable sort modes: Core identity first (anchors, then core members, then other scored photos) and Highest identity score. The overview's visible nine must match the filtered Gallery view in the review page. Both pages share the same cached Chest-up/Head crops; person links open the matching Gallery view in a new tab. Prime-start suitability remains a separate photo-quality signal, not identity confidence. |
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

- **ComfyUI photo:** the workflow input selected in `workspaces.json`;
  automatically photo-protected, but not automatically an identity anchor.
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
hash; metadata refresh and restore behavior still need explicit tests. Duplicate and backup-restore continuity were subsequently verified for
originals-managed IDs in A4; unsupported transformations still require
explicit mappings rather than guessed continuity.

## Matching and self-healing policy

### Action-specific validation, not a universal safety threshold

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

The later
[tier behavior and protection contract](2026-10-21-likeness-rebaseline-and-family-naming.md#tier-behavior-not-a-global-caution-switch)
is authoritative. Earlier report-only Prospect cleanup and cautious Potential
handling were delivery stages, not permanent limits on lower-tier automation.
Cast Gallery protection does not forbid separately permitted incoming cast
Review or impose a clustering threshold on unrelated candidates. A protected
photo must not move automatically, but may stay outside the core.

### One reconciliation plan for Review and incoming photos

The primary routine now calls shared reconciliation instead of its former
Review/sort/singles/rematch decision chain. Its established maintenance paths
are implemented, but labelled real-batch acceptance is still outstanding. The
[ordered decision flow](2026-10-21-likeness-rebaseline-and-family-naming.md#ordered-decision-flow)
now specifies one planner for rebase and incremental maintenance. This plan
supplies its metadata, review actions and recoverable execution foundation;
it does not define a second matching sequence.

Keep established and provisional reference vectors frozen during bounded
same-run matching. Retain small-group evidence, keep unresolved holds distinct
from new identities, and separate proposed destinations from write
authorization. The later plan owns category transitions, merge/split planning,
effective configuration, source modes and full-path behavioral tests.

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
settings combined defaults then in `tools/art/likeness.py` (subsequently
extracted to `likeness_library/engine.py`) with
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
  their identity decisions. Restore/backup continuity is recorded under A4.
- [x] **P2 either** B5 Transfer action-specific precision/recall validation
  to Phase 4 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md);
  production thresholds remain unchanged until its evidence gate passes.

**Exit:** repeatable output; no writes except explicitly generated reports/cache;
action-specific measurements on user-labelled examples.

### Phase C — focused review gallery

Header image/details/actions separation and formatting feedback are tracked
in the [layout plan](2026-10-22-gallery-review-layout.md), not implicitly
completed by the action implementation below.

- [x] **P1 ai** C0b Verify available-action execution readiness: supported
  launcher help works; an exhaustive schema-enumerated regression round-trips
  all ten non-workflow photo actions through saved JSON, validation,
  temporary-file apply and undo with byte/metadata restoration. Existing
  identity protection and workflow apply/undo tests remain passing, including
  refusal to change shared workflow selection from an isolated sandbox.
  The likeness guide now gives exact sandbox validate/preview/apply/undo
  commands, batch/stale-page cautions and unfinished-control boundaries.
  This verifies implementation wiring, not actual-library visual acceptance.
- [x] **P1 ai** C0a Address the photo-evidence slice of Oct 22 acceptance
  feedback: show three closest same-side photo-to-core comparisons with
  scores/category/name, preserve the existing single-match consumer contract,
  and explain approval versus photo protection versus anchors/core eligibility.
  These are diagnostic comparisons, not automatic-routing authorization.
  No thresholds or real placements change. The other acceptance-feedback
  requests remain open in their owning phases; raw feedback is retained.
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
- [x] **P1 ai** C6 Transfer Prospect/Potential rename, name-swap, collision,
  and history work to Phases 2 and 5 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
  Existing Potentials' closest-person evidence remains implemented.
  Manual standalone rename is now implemented under task 5.3a there, also
  covering Models. Name swaps and broader family-link changes remain open.
- [ ] **P2 ai** C7 Keep dated report output available and support replacing
  a stable output directory. The overview/review link and order consistency
  are implemented; verify stable-directory replacement without losing the
  dated reports.
- [x] **P2 ai** C8 Add an explicit user-staged move to the closest identity,
  including destination choice, hash/protection validation, preview, backup
  and undo. Implemented as `match-accepted`, always to destination Review.
  Manifest and audit retain its stable destination ID; stale target ownership
  blocks apply/undo. Generated scripts compile and protected/anchor/workflow
  selections offer no reassignment. Local visual acceptance remains separate.
- [ ] **P2 ai** C9 Investigate a local secondary face model on labelled difficult
  expressions, including `7515826497811991332` (Arwen Ames / Rhiannon Frost).
  Compare models and disagreement evidence before selecting any new scoring
  algorithm; do not replace SFace or add score-patching exceptions silently.
  Preliminary source review: [InsightFace](https://github.com/deepinsight/insightface#license)
  distinguishes MIT code from non-commercial-research pretrained weights;
  do not auto-download a package as if the code licence covered the weights.
  [AdaFace](https://github.com/mk-minchul/AdaFace#pretrained-models) provides
  local quality-adaptive models and MIT code, but no model-use clearance was
  established here for the selected checkpoint/training dataset. Its BGR
  112x112 aligned input also differs from InsightFace's documented RGB input.
  No new model was installed, selected or tested on library images. A labelled
  expression/pose/quality comparison and checkpoint licence review remain
  necessary; never average raw cosine scores from different model spaces.

**Oct 20 gallery update:** C5 is implemented. The category filter now
constrains the person selector, person sections fill the available width with
responsive left-to-right grids, and small/medium/large tile sizes are
selectable. Each source photo has cached head and chest-up derivatives named
from its master stem and content key; both link to the full image. Potential
gallery records now show closest-other-folder score evidence. C6's rename and
explicit swap controls remain open.

**Oct 20 overview consistency update:** `bin\people-gallery.cmd` builds
both reports in one output directory. The overview and full review share
identity sort modes, and a person's initial nine photos match when opening
the filtered Gallery in the review page. Both pages use the same cached
Chest-up/Head derivatives; the overview sort and framing controls update
without generating a separate thumbnail set. Person links open in a new tab,
and the history file remains a separate link. Both reports follow the same
category/person ordering. The library routine refreshes the review report
before the overview. Stable-directory replacement remains open under C7.

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

**Oct 22 progress:** clean rebuilding and ordinary incoming/Review processing
now call the shared policy planner. Production draft apply is blocked before
housekeeping; sandbox apply has an isolated catalogue, verified backup,
transaction journal and undo. Review holds do not become named identities
and existing ambiguous cast Review stays staged. The installed trial and
nonzero follow-up preview are recorded in the
[Oct 21 plan](2026-10-21-likeness-rebaseline-and-family-naming.md#installed-unified-sandbox-trial-oct-22).
Earlier prototype completion below does not by itself close operational
acceptance. The later continuation implements merge/split and existing
category transitions; three synthetic full command paths reach no-change
second previews. Real-batch and global convergence acceptance remain open.

- [x] **P1 ai** E1 Transfer combined Review, incoming `Various`, and validated
  Prospect/Potential candidate planning against a frozen snapshot to Phase 4
  of the [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
- [x] **P1 ai** E2 Implement a read-only combined-candidate prototype with
  provisional destinations. This is a prototype milestone only; pair
  preservation, proposal/authorization separation and applied integration
  were subsequently implemented under Oct 21 tasks 4.9 and 4.15-4.20; those
  tasks retain broader evidence and acceptance gates.
- [x] **P1 ai** E3 Implement bounded frozen-reference follow-up in that
  prototype. The prototype's draft gate was subsequently repaired under
  4.17/4.20. This historical milestone is not real-batch convergence acceptance.
- [x] **P1 ai** E4 Support empty-pool read-only reconciliation. Operational
  maintenance now uses the shared integration in 4.9-4.12; acceptance remains
  tracked there rather than inferred from this prototype checkbox.
- [x] **P1 either** E5 Transfer comparison of preview/applied results and
  action-specific approval gates to Phases 3, 4, and 6 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).

**Historical Oct 20 prototype:** `likeness reconcile [--out FILE.json]` built
one read-only snapshot of current person cores, usable Review photos, and
usable `Various` pool photos. It applies stable average-linkage clustering to
the combined candidate set, allows an eligible new cluster to attract a
remaining candidate without changing that cluster's frozen vector, and
reports ambiguous, protected, duplicate-ID and unassigned candidates as held.
An empty pool is supported. The command does not move files, change catalogue
metadata or apply any matching decision; it can update the embedding cache.
Prospect outliers are not yet fed into this planner. The report-only evidence
exists under F1a; operational candidate selection and shared apply integration
remain open in the Oct 21 plan. E1 is a completed transfer, not a completed
implementation. A later sandbox clean run and preview exist there; production
unified reconciliation/apply has not been delivered.

**Exit:** validated routing behavior; ambiguous cases stay in Review/pool and
same-run clusters can resolve candidates without order-dependent cascades.

### Phase F — guarded Prospect self-healing

- [x] **P1 ai** F1a Before the next ingest, produce a report-only,
  per-photo audit of all usable Prospect and Potential Gallery photos against
  current Angel/Sister folders and their source-person folder. Include each
  photo's all-cast ranking, score/margin evidence, leave-one-out source-folder
  score (or no-peer status), and the person-local Review destination a user may
  choose. Label folder-centroid matches as provisional evidence; do not move
  photos or modify scores/thresholds. Separately list Potentials that exceed
  the usable-photo boundary and histories indicating a former Angel/Sister
  identity.
- [x] **P1 either** F1b Transfer visual review of the cast audit and safe
  cross-person Review routing to Phases 3 and 4 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
- [x] **P1 either** F1c Transfer labelled comparison of incoming-photo and
  uncertain-cast routing policies to Phases 3 and 4 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
- [x] **P1 ai** F1d Transfer frozen-core Prospect/Potential cross-person
  comparisons to Phase 4 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
- [x] **P1 either** F2 Transfer validated Prospect-to-Review routing and
  minimum-core protections to Phases 4 and 7 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
- [x] **P1 ai** F3 Transfer explicit, previewed cast-photo handling to Phases
  3 and 6 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
- [x] **P2 either** F4 Transfer action-specific precision/recall gates to
  Phase 4 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).

**Oct 20 diagnostic evidence:** a read-only `likeness folder "Harlow Chase"
--all` audit found 100 usable photos: 97 agreed with the folder core, two
scored 0.15–0.25, and one scored below 0.15. The two-face photo
`harlow_chase_shot_20261010124403.jpg` scored 0.00 and was suggested for
holding in Various; another photo scored 0.39 against Harlow's core and 0.46
against Camaris. Camaris's `z_` history records Prospect merges at 0.55, 0.49
and 0.49. These are concrete review leads, not proof of a wrong identity:
the catalogue has no confirmed anchors yet. This historical audit did not
authorize production changes; later isolated sandbox experimentation follows
the Oct 21 contract and does not require anchoring every provisional identity.

**Oct 20 cast-audit report-only run:** `bin\likeness.cmd rebaseline --out
"B:\Sovereign Territories\_reports\library\rebaseline-20261020-cast-audit.md"`
generated `prospect-cast-audit.csv` with 1,146 usable Prospect/Potential
Gallery photos. `Angels/angelica` ranked first for 67 photos; 12 scored at
least 0.40, four at least 0.45, two at least 0.50, and none at least 0.55.
Angelica ranked first for all four photos in Potentials/Fia Hadley and
Potentials/Amara Berkley, three of five in Prospects/Petra Wilde, and ten of
fourteen in Prospects/Jacinta Alden. These are folder-centroid rankings, not
identity confirmation; current peer-centroid scores are often stronger.
The whole-library preview separately flagged Potentials/Lia Joyce (35 usable
photos) across the category boundary and a former-cast history note for
Potentials/Wren Thorn (one usable photo). Neither category nor photo changes
were applied. The report lists 26 threshold-based out-of-folder suggestions
and three Junk-rule candidates; those also remain suggestions. No photos or
folders moved, and matching thresholds were unchanged by that audit. F1a is
complete; F1b is a transfer, with remaining visual acceptance and operational
routing tracked in the Oct 21 plan.

**Exit:** action-specific safety targets pass; rollback and “why moved” records
are verified on real, backed-up batches before enabling routine use.

### Phase G — add photo and person retirement to the review interface

- [x] **P1 ai** G0a Add distinct permanent photo-to-identity rejection:
  `match-rejected` preserves the current identity's stable ID against the
  photo's SHA-256, returns the original to Various through existing backed-up
  actions, and is reversible by undo. Individual and group matching exclude
  that identity and its merged successor. Explicit approval/reassignment and
  whole-identity merges cannot bypass the decision. Changed bytes are held;
  legacy move paths refuse unsupported exclusions, and clean rebuilding
  refuses non-cast exclusions pending stable-ID migration. Ordinary pool
  rejection remains nonpersistent. Synthetic browser export and cancel pass;
  no actual library rejection was applied.
- [x] **P1 ai** G0 Deliver the photo-level slice: `photo-retired` manifests,
  exact recoverable `_retired/photos/<person>/<bucket>` destination preview,
  current ID/hash validation, photo-protection/anchor/workflow guards,
  verified-backup apply and undo, archive collision/stale-state refusal and
  rollback tests. Gallery and Review controls share the existing transaction
  path. Nine focused tests pass. The regenerated sandbox Review page exposes
  2,321 Gallery and 55 Review retirement choices, with zero photo-protection,
  anchor, workflow-selection or nonstageable violations. Catalogue/policy
  hashes are unchanged. Identity protection is an automatic-change gate,
  not a ban on explicit user retirement. G1-G3 remain open for the whole-person
  scope; Various/Artist sources are not stageable photo identities yet.
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

- [x] **P1 ai** H1 Transfer primary-routine planner integration and
  empty-pool maintenance to Oct 21 tasks 4.9-4.12/4.20. The transfer is
  complete; the ordinary routine now calls shared reconciliation. Legacy
  commands remain compatibility surfaces pending their separate sunset audit.
- [ ] **P2 ai** H2 Extract metadata, core/scoring, planning and report/action
  responsibilities from `likeness.py` in small, behavior-preserving,
  test-covered changes. Do not do an all-at-once rewrite.
- [x] **P1 ai** H3 Transfer effective behavioral-policy ownership, migration,
  provenance and calibration to Oct 21 tasks 4.15/4.19. The current split
  between code defaults, workspace settings and policy JSON is not accepted
  as completed externalization.
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

- [x] **P1 ai** I1 Transfer recovery and continuity audit for recorded
  identity names, including empty/legacy cast `z_` files, promotion, return,
  merge and slot swaps, to Phases 2 and 5 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
- [x] **P1 ai** I2 Transfer name-history regression coverage, including
  Draknora's reported case and the distinction between recorded identity and
  fixed character-slot names, to Phase 2 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
- [x] **P2 ai** I3 Transfer staged Prospect/Potential rename controls and
  collision-safe family naming to Phase 5 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
- [x] **P2 ai** I4 Transfer preview/apply/undo, catalogue history, and people
  index refresh behavior for supported name changes to Phases 2 and 5 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
- [x] **P2 ai** I5 Transfer case-insensitive collision and rollback tests for
  name changes and swaps to Phases 2 and 5 of the
  [rebaseline plan](2026-10-21-likeness-rebaseline-and-family-naming.md).

**Exit:** all name-continuity and family-naming work is tracked in the
rebaseline plan; this plan retains the stable-ID and manifest foundations.

### Phase J — organize large galleries into reviewable clusters

- [x] **P2 either** J1 Present options for organizing large galleries and
  review groups, including explicit membership, source/import provenance, and
  inferred similarity clusters. On Oct 21, the user chose Option A: keep
  existing category folders and add virtual family/lookalike groups, with a
  shared-surname naming convention for explicitly related identities.
- [x] **P2 ai** J2 Transfer implementation of the approved family metadata,
  gallery grouping, and safe naming workflow to
  [the rebaseline and family-naming plan](2026-10-21-likeness-rebaseline-and-family-naming.md).
  Preserve the flat view; do not physically move photos or create a Families,
  Twins, or Lookalikes directory as part of Option A.

**Exit:** large galleries can be browsed by core and clearly separated groups
without changing person identity, moving files, or losing the existing flat
view.

## Safety and acceptance criteria

- No automatic deletion. Every source remains recoverable from its original
  location, archive, backup or action history.
- Identity anchors, protection, workflow-photo choice and inferred match are
  independent fields and visibly explained.
- Routine processing never moves protected photos or Angel/Sister gallery
  photos without an explicit user-staged action.
- Cleanup cannot remove trusted anchors or violate the applicable minimum
  core. Ambiguous outliers go to Review/hold; qualified lower-tier actions
  follow the later tier-aware contract, not a blanket no-reassignment rule.
- Review and pool candidates are considered together against existing people
  and same-run provisional clusters; bounded iteration is deterministic and
  cannot oscillate or reassign a candidate more than once.
- The user can audit exactly why a photo was held, returned, moved to Review,
  or matched elsewhere.
- A preview and verified backup precede every batch with file changes.
- Production thresholds remain unchanged until action-specific validation
  and approval. Explicit sandbox overrides may vary thresholds for real
  trials; record them without creating a second matching engine.
- Large-gallery UI performance and the action-manifest workflow have focused
  tests, including stale hashes, missing files, duplicate IDs and undo.

## Existing plan reconciliation

- D2 and D3 of the tooling-debt plan were transferred to Phase H. Incremental
  modularization remains here; H1/H3 integration and policy-resolution work
  now transfer onward to the Oct 21 plan, with no duplicate open tasks.
  Production settings still require measured results and approval.
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
- The Option A family organization and shared-surname convention are now
  approved; the new [rebaseline and family-naming plan](2026-10-21-likeness-rebaseline-and-family-naming.md)
  coordinates source-scope audit, matcher simplification, visual scenarios,
  family metadata, and guarded library rebaseline. Existing metadata,
  manifest, backup, apply, and undo work remains the foundation; open
  implementation tasks must be reconciled there rather than assumed complete.

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
| D14 | Keep the existing category roots and use virtual, stable-identity family/lookalike groups; no physical family/twin root is added in this iteration. |
| D15 | Use shared surnames only for explicitly associated identities, keep first names distinct, and never use names or family links as matching evidence. Audit `z_` first/last names and surname collisions before any rename. |

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

## Raw user direction: Prospect/Potential sprawl (Oct 20)

I am fine with the photo-by-photo audit of Prospects and Potentials - also I noticed that some
potentials do have more than 5 photos and one is actually supposed to be in Prospects as she was a
Sister at one time - but that said, I do think that if we have an incoming photo (in the future) or
we do the photo-by-photo comparison, it would be better to put them into a Review of an existing
Angel or Sister.  At least that would pull out some of the Sister or Angel pictures that are
sprinkled into the Prospects and have created a new identity.  That's probably the first iteration
or priority.  After that, then being able to try do the same from Prospect to Prospect and Potential
would be a next way to try to fix some of the clusters.  What I am worried about is that since we
have established identities for Prospects AND they may be mis-matches themselves it's difficult to
fix them - unless you think that the photo-by-photo processing would work to address that as well.
But I think this is the time to address the Prospect sprawl - before I ever pull in more images.

Jacinta is also Angelica

IF we processed them 1 at a time without Petra existing at all ...

## Raw user feedback: review and large-gallery clusters (Oct 20)

As we do this, the one thing that might be useful in the Review is to have sub-directories of clusters of like photos within each person's review folder or even within the main gallery itself. This would allow us to better organize and visually separate different sets of similar images, making it easier to identify duplicates, mis-matches, or potential new identities.  Basically, just thinking of a way from keeping them from becoming yet another prospect, but also clustering them within an identity for easier management and review.  Not exactly sure what I am really thinking - so need some deep through on this, but at least getting them into Review and out of Prospects and cluttering up others.  What I am trying to avoid is an accidental flooding of a review folder with other unrelated images, which could make the review process more confusing and less efficient.

So, like in the case of Angelica - there were 3 images that created Petra, there's 4 in Fia Hadley (that are Angelica) and 3 in Amara Berkley (that are Angelica).  Briony StoneHaving sub-directories or clusters within the review folder would help keep these grouped together and make it easier to see the connections between them, rather than having them scattered and potentially mistaken for separate identities.

This approach could also help when we have multiple potential identities for a single person, as it would allow us to visually separate and compare the different clusters of images.  It would make the review process more structured and less prone to errors, as we could focus on one cluster at a time and make more informed decisions about merging, retiring, or reassigning images.

Thoughts????

Later on - maybe the Gallery does also need the clusters for groups as well - that would also help with galleries that are 100+ where we keep the core in the main Gallery and the other clusters underneath - I can still pick from them, but I'm thinking bigger picture as we have some very large galleries with now as well.  I know that breaks the gallery .html so it's not an immediate - but it's something that needs thought for large galleries.

## Raw scratch follow-up: review layering

Preserved from the latest scratch revision; Phase J owns organization work.
Words are unchanged; long paragraphs are wrapped for Markdown.

As we do this, the one thing that might be useful in the Review is to have sub-directories of clusters of like photos within each person's review folder or even within the main gallery itself. This would allow us to better organize and visually separate different sets of similar images, making it easier to identify duplicates, mis-matches, or potential new identities.  Basically, just thinking of a way from keeping them from becoming yet another prospect, but also clustering them within an identity for easier management and review.  Not exactly sure what I am really thinking - so need some deep through on this, but at least getting them into Review and out of Prospects and cluttering up others.  What I am trying to avoid is an accidental flooding of a review folder with other unrelated images, which could make the review process more confusing and less efficient.

So, like in the case of Angelica - there were 3 images that created Petra, there's 4 in Fia Hadley (that are Angelica) and 3 in Amara Berkley (that are Angelica) and Briony Stone as well is Angelica, Aradine Baldwin, Cressida Fontaine, Cecily Radcliffe, Daphne Lane, Uma Zane.  Having sub-directories or clusters within the review folder would help keep these grouped together and make it easier to see the connections between them, rather than having them scattered and potentially mistaken for separate identities.

This approach could also help when we have multiple potential identities for a single person, as it would allow us to visually separate and compare the different clusters of images.  It would make the review process more structured and less prone to errors, as we could focus on one cluster at a time and make more informed decisions about merging, retiring, or reassigning images.

Thoughts????

I killed the windows search indexer as it was chewing up CPU.  Also Well - it's not just a .html thing -- when I pull images into Comfy UI inputs - I need to scroll through 100+ images to find some of the other ones to test with for generating poses and such.  While I know I will focus on having a single "likeness" for the Angel - I do use other poses for various testing.  It's not a high priority now - but as I get back into the work within ComfyUI - having directory structure will help if we can have some sort of proper naming - instead of cluster 1, cluster 2, etc... Again, that's down the road - but long term having to pick from 100+ images and not knowing which ones are core within ComfyUI to choose a new photo is more of an issue.  and I won't know which ones to use until I pull them in and test with them.  Anyway - not critical to cleaning up the Prospects - but certainly we already have examples of Angels with large number of images we'll need to work on that with.

## Raw scratch follow-up: tiered maintenance and production reuse

The Oct 21 plan owns these engine requirements; this preserves the source
discussion, not a second action policy.

As I look at the items for the auto-merge threshold for an identity to identity, I think we also need a tiered system for how Potentials might auto merge together.
When you hit a stopping point I'd like to discuss that auto-merge logic around the 0.55 threhold and how it applies and what the auto-merge for potential to potential is.
I don't want to make changes - just want to discuss how I think we have to ensure we have some threshold for Sisters, Angels, Models, Prospects and Potentials at differing layers to cluster the Potentials a bit more effectively.
But maybe the rebase will take that into account - but longer term as a Potential grows with a few images - prior to being auto-promoted to a Prospect, we could merge at a different ratio (potentially).
Same with Prospect to Prospect merges.  With Sisters, Angels and Models I would want the threshold to be higher as we go up the hierarchy and I can do the reviews without having to "manually" combine the Potentials that I would basically combine when I see that they align to another Potential and not have to rely on a complete rebase but the normal cycle of compares of likeness can hand that when I bring in new images.
We can discuss what I am thinking to ensure it doesn't impact the rebase or if it does - then we need to assess.  So, it's just a discussion point when we are ready.
Maybe the rebase handles it, but I do want the ongoing process to handle it as well so I don't have to manually drive combines that the likeness between Potentials or maybe prospects as well - if they grow to 0.40 or higher as we add images.  It's just a discussion point.

Secondly, I see a specific sandbox.py that handles work - just want to make sure we're not building something for rebase that ONLY works in the sandbox and if we want to run this in the production image directory afterwards it will run without a rewrite of a bunch of code.
I understand we're cautious about the sandbox and how it's rebuilding everything ... but I want to ensure that we aren't sandboxing the sandbox code and building a silo that won't work in production right after I agree that we've tweaked the threshold and functionality - like the auto_merge logic.
Basically the entire rebase, ongoing self healing, merging - pulling out the lower scoring images from an identity as we find better ones so we don't clutter ANY identity with low scoring images.
With Prospects and Potentials - much more freedom to move images in/out of the identity and as we go up the hierarchy we are more restrictive.
For instance - not auto pulling out low scoring images in a Sister or Angel - but we do identify them and call them out specifically.  With Models it'll be a middle ground of how we'd want that to happen.
And it's all probably just configuring thresholds at each level in the hierarch and setting things to Protect at the Identity or even Image level from the auto-merge or auto-move functionality.
Basically the system will organically grow and shuffle images around as we build more and get better scores and drop out lower scores, which then might merge "up" the hierarchy when we get rid of the lower scores.
A 2 photo Potential could grow into a Prospect with several new photos that match 1 of the 2 photos and then the 1 photo becomes a much lower score - so we'd want to kick it out automatically into it's own Potential.
Over time - that one Potential could match another Prospect and jump up to that one - which might be different than the original Potential it was paired with.
I feel like that's the way the bottom layer would be handling things.  Given they are just Potentials - it's fine to be more free about clustering them to see how they move up the hierarchy or splitting them from a Prospect, Model or another Potential automatically due to the low score 0.15 or lower.
We have a scale for the green, yellow, orange, red that I think we can apply through the hierarchy and auto-merge/moving without re-running the rebase.
Once we get the library "stable" with the rebase I don't expect to run that again - other than if I see it get's messed up for some reason and we fall back to it.  Hope that all makes sense.

Both topics to discuss....

## Raw scratch follow-up: mismatched images and identity cores

So here's my dillema - I can see photos in Petra Cole where I know the first 3 in that group are actually Angelica - as I took those screen shots directly and since they weren't posed they didn't match Angelica - but there are others already in Angelica - where I know the Angels are more protected, but there are some with a score of 0.19 and I would have thought that these would really have matched her.
So what is the best path forward to addressing situations like that?  I could manually move them into her directory or how do I handle that effectively as the GUI doesn't really allow me to move them to an angel and the CLI is a bit awkward when handling this type of reorganization?
I could try to just move them back to Various and see what happens?  this is happening more often than not.  Would it make sense for me to add some of those photos into Angelica's core and see if it pulls them in?  or do I risk pulling to many others into Angelica that aren't her?
That's where I need some thought and advice.  If you needed to run commands to look at those 3 for Petra Cole and figure out what you think is that feasable?
Somehow I feel like if we had a bug in how the matching worked a while ago - it may not have handled things properly.  Maybe a report tells us if those images are "close" to Angelica or not...

Basically - as I am scanning and looking at the images, I am noticing that there are some mismatches and inconsistencies in how the images are being categorized.
It seems like the matching algorithm may not be functioning as expected, leading to some images being incorrectly associated with the wrong person.
What I don't know is how to effectively address these mismatches without causing further confusion or misclassification.
It's clear that some images are being misidentified, and I want to ensure that the correct images are associated with the right individuals.
If the GUI doesn't allow for easy reorganization and the CLI is cumbersome, I need to find a more efficient way to manage these mismatches.
We could add functionality to the GUI to allow me to move images between directories more easily, or perhaps implement a feature that allows for better verification of matches before they are finalized.
Additionally, it might be helpful to have a reporting tool that can analyze the images and provide insights into their similarity scores, helping to identify potential mismatches more effectively.
At least if someone is a Sister or Angel I'd want to know how similar the images are to the core images of that individual, so I can make a more informed decision about whether to reclassify them or not.
Overall, I think we need to improve the tools and processes for managing these mismatches to ensure that the images are accurately categorized and associated with the correct individuals.

Eventually, I'd want to ensure that we can deal with prospect across prospect mismatches as well - that's what I think happened since it found a cluster of 3 images that were very similar to each other but not to the core images of Angelica, leading to them being misclassified.
So I think we need to have a way to handle these types of situations more effectively, whether it's through better tools, improved algorithms, or more robust verification processes.
Ultimately, the goal is to ensure that the images are accurately categorized and associated with the correct individuals, minimizing the risk of misclassification and ensuring that the data is reliable and trustworthy.
Then it added more images to Petra Cole once she was created that are not Angelica, but they are similar to the other images in Petra Cole's directory.
So I think we need to have a way to handle these types of situations more effectively, whether it's through better tools, improved algorithms, or more robust verification processes.
Ultimately, the goal is to ensure that the images are accurately categorized and associated with the correct individuals, minimizing the risk of misclassification and ensuring that the data is reliable and trustworthy.

To be honest, I'm confused why they didn't match to Angelica in the first place, since I know they are her.
I think it may have been a bug in the matching algorithm that caused them to be misclassified.
So I think we need to have a way to handle these types of situations more effectively, whether it's through better tools, improved algorithms, or more robust verification processes.
Ultimately, the goal is to ensure that the images are accurately categorized and associated with the correct individuals, minimizing the risk of misclassification and ensuring that the data is reliable and trustworthy.

Those 3 are just one example of where I see images I know are Angels or Sisters that are showing up as a Prospect when they all come in as a very like set of images that aren't a very solid match for core images of an existing individual.
I guess it's a bit confusing on what I need to do without just going in and manually just moving images around by hand.

I guess it goes back to what is the core identity of someone like Angelica and do I need to ensure that other items are added to the core and re-run things to get them to match up.
The reason I provided the comment that I do not like Camaris is that it's not as consistent of a person of all the images, so when I asked to swap prompte Ruby Eden to Camaris - I did not look at the entire gallery and only based it off the grid of 9 in the gallery last night, it's only today when I look at the entire gallery that I see that Camaris is not a good match for Ruby Eden, so I need to go back and fix that.
I think the same thing is happening with Angelica and Petra Cole, where the core images of Angelica are not a good match for the images that were added to Petra Cole's directory, leading to misclassification.
So I think we need to have a way to handle these types of situations more effectively, whether it's through better tools, improved algorithms, or more robust verification processes.
Ultimately, the goal is to ensure that the images are accurately categorized and associated with the correct individuals, minimizing the risk of misclassification and ensuring that the data is reliable and trustworthy.

I know we made some adjustments to the matching algorithm over time, so is there something that would go photo by photo of a single prospect and match it against other Angels, Sister and Prospects and only pull it back into the same Prospect it started from if there isn't another valid match?
I thought that was something we were considering in older plans and maybe that was what I wanted with the re-baseline work without pulling every single prospect back to Various to see where they land ... basically, I don't trust ALL of the prospects, while some do seem good - others aren't.
I could just move them all into Potentials and we could do the logic that way for Potentials.  I guess I'm just confused on which way to go now.

## Raw scratch follow-up: cast-associated appearance groups

That's where in the future, the sub-directories for that cluster under Angelica would make more sense instead of a new Prospect.  At least then we'd know that it was very much like here.
But maybe that would bite us in the long run with other angels or sisters.  So the question I have is - what is the match threshold to get into a Prospect vs. Angel/Sister - that was added to prevent "unwanted" items from showing up in a "protected" type identity - but it's having the counter effect of bloating out the Prospects with many new identities that are so similar to Angelica that they suck other photos that are of Angelica.
Lastly, it's time consuming for me to try to see which photos are referenced from the .csv in the simulation vs. having a simulated result in an actual gallery along with what goes where.
What's interesting is that when I see the items that are a .40 and above for a "looks like Angelica" for the new cluster - they are actually Angelica.
I understand the .55 to auto merge them into Angelica, but this is where I think we could take a step back and try to understand a better way to address those clusters that do look alike an angel or sister that fall below .55 and are above .40 - the whole point of wanting them under and Angel or a Sister is to help bring home that association is very high - versus the Prospects that don't look like any angel or a sister.
I checked the same for Rosalind Davenport and she looks like Haniya at .46 and it's just bad images of Haniya - so they are actually her as well.
I checked yvonne caldwell and she is .43 for Serephine with some coming direct to Serephine - that's also all Serephine, just a large group of ones that were not as good.
If it's not serephine, it's her twin sister.  Basically - what I am observing is the .55 threshold is good for automatic inclusion - but we need that nexy layer to figure out how to keep them with their "look-a-like" in a way that they aren't automatically clustered - but new photos that match them would result in going into that cluster.
The other thing I can think of is to create somewhere other than Prospects to put them into and use the same angel/sister name for those?
Like Twins/Angelica xxxxx  Twins/Seraphine xxxx with last names so if there are more than one twin of Angelica or more than one of any Angel or Sister we accomodate that and fold it in like we split off Potentials from Prospects ... but we have different logic for what goes into Twins as they are so close to matching Angels or Sisters
 - Angel Twins/Angelica Dawn, Sister Twins/Drakniss Jasper ... in doing this - we keep a physical separation from the actual sisters and we can then use some of the same Angel/Sister logic for pulling in new photos to guard against "clutter" in that Twin of what happens in Prospects.

## Raw user feedback: catalogue IDs, closest action and secondary scoring

Preserved from the scratch note; C8/C9 own the outstanding requests. The clean
sandbox catalogue now supplies IDs, but the manual closest-destination action
and secondary-model investigation are not implemented.

```text
Even for angels and sisters I see "Identity ID: not catalogued" which is not useful - so maybe we don't need that since I don't use the internal identity - I just thought maybe it would be useful, but if not assigned to anyone, it's pointless.


Lastly - on the details page, I think a staged action should be able to actually move the image to closest if I choose to do that as well.   I also feel like our scoring may need to be double checked and I'll get back to you on that as I have 7515826497811991332 in Arwen Ames, but the Closest Other is Rhiannon Frost ... her eyes are more closed in that picture, so what I am wondering is if there are other models we can use as a secondary face check on top of what we're doing in certain cases.  It seems like the face recognition we have might not be perfect.  We've put patches in place to try to handle the existing scoring and some of the routines
```
