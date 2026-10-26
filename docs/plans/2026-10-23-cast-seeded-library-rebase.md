# 2026-10-23: all-image preparation and cast-seeded rebase experiments

**Status:** active (Phase 3; blocked on accepted Phase 1 preparation and Phase 2 recovery)

## Oct 25 authorized all-image sandbox run (stopped; intake incomplete)

The user authorized the complete, recoverable sandbox run, including current
`Working\Various`, while keeping production cutover out of scope. The immutable
root is `B:\Sovereign Territories Sandbox\Source`; its verified manifest still
names production `B:\Sovereign Territories` and records 8,845 files / 5,570,978,132
bytes. The only mutation target is `B:\Sovereign Territories Sandbox\Working`.
Run ID: `clean-rebase-20261025-overnight`. This run performs no production or
immutable Source writes, no ComfyUI job, and no `_generation` writes.

The launcher’s read-only preview found 2,700 active immutable preparation
inputs. Including all 134 current Working Various images requires a run-local
copy-on-write-by-copy overlay; the immutable Source snapshot itself is never
changed. Stable-ID mapping, exact-byte checks and duplicate handling found 74
one-to-one ID replacements with newer Working bytes and 41 additional distinct
input paths, for 2,741 total preparation outcomes. This is more than the
anticipated “up to nine”: direct inventory showed only 93 current Various
images with active-source stable-ID matches, 27 other stable IDs and 14 names
without a parseable stable ID. Two exact duplicate files collapse to one
prepared input while both raw paths remain in recovery; a timestamp-key
collision with different bytes is isolated under a hash-derived name instead
of being misidentified. The resulting count is the exact union, not a cap:
none of the current Various files are silently omitted.

The dated run-local `source-overlay` retains the original source hashes and
the raw Working versions of every changed/new input, with a manifest binding
each copy to `source-manifest.json`. The same run’s `inputs` mirror and
preparation receipt must verify all 2,741 outcomes before likeness resumes.
At 2026-10-25 23:52 local, the live intake log recorded 453 of 2,741 per-image
terminal preparation rows: 451 `compared`, 2 `compared-overlay`, and 2,288
not yet processed. The live process is responsive and advancing. This is
progress only, not a claim of complete preparation. Installation and gallery
publication have not begun.
Before installation, create and verify a full
pre-run Working backup. Preserve the parent’s frozen render inputs and all
`Working\_generation` contents.

Progress snapshot: at 2026-10-26 01:05:37 `-05:00`, the process had logged
1,165/2,741 outcomes (1,109 `compared`, 48 `compared-overlay`,
8 `junk-candidate`; 1,576 pending), without an intake receipt or preparation
manifest. Its final observed count was 1,302/2,741, then Pillow raised
`MemoryError` while encoding a padded PNG into a `BytesIO` buffer. The process
terminated before the preparation receipt/manifest, matching preview,
backup/install or Gallery publication. No active clean-rebase process remains.

The preparation writer now streams file copies/hashes and image saves to disk
and computes image differences in chunks. `bin\validate.cmd` passed 29 suites /
811 tests after the change, but a full all-input retry has not verified it.
The partial `inputs` mirror exists without `intake.json`; `clean_preparation`
refuses to reuse an unfinished mirror, so preserve this run and use a new run
directory rather than deleting or resuming it in place. The same run's
`source-overlay` receipt remains the source of truth for its input mapping.
At the state check B: had 402.09 GB free.

A separate test-isolation follow-up made the two overlay tests independent of
optional OpenCV: their active-image inventory boundary is mocked with a
lightweight synthetic gallery inventory, excluding recovery trees as the
production inventory does. The metadata pre-commit hook then passed all 287
tests in its intentionally lightweight environment without adding OpenCV.
This test result does not establish full input outcomes.

The saved overlay receipt is the source of truth for this run: 2,700 immutable
active inputs, 134 current Various paths, 74 same-ID changed-byte replacements,
41 additional preparation inputs, and 2,741 unique preparation inputs. The
previously reported `125 ID matches / 86 hash changes / 9 new` estimate remains
unreconciled and is not used to classify this saved overlay. These 41 inputs
are preparation inputs, not claims of 41 new people. The receipt at
`Working\_sandbox-state\clean-rebase-20261025-overnight\source-overlay\overlay.json`
and its recovery hashes must be rechecked before matching/apply.

The first integration test exposed duplicate photo-ID continuity after adding
collision-safe current paths; `_migrate_continuity` now retains all matching
current paths rather than overwriting a list with one path. The focused clean
preparation lineage/undo test and all 10 clean-rebase tests pass. Final
prepared/held/error/install counts, preserved-file comparison and Gallery
paths remain unverified and belong to a future fresh run.

## Oct 25 implementation checkpoint, before real acceptance

The existing launcher now supports the same all-image preparation run as
intake-only review or preparation/resume into matching preview and reversible
installation. C4's retained-cast implementation is delivered; it does not
silently implement optional cast release. Exact commands and refusal conditions
live in the [likeness guide](../art/likeness.md#clean-sandbox-rebuild-versus-category-reclassification).

C2 now inventories active current inputs against immutable stable IDs and
migrates one-to-one name/family/override decisions only after evidence-based
routing. Missing catalogued inputs, unknown current images, stale bytes and
ambiguous split/merged destinations hold rather than lose curation. Existing
prepared lineage can prove the current-to-original decision binding.
Broader real-curation coverage remains C2 acceptance work, not an inferred pass.

C6 stages native prepared bytes, exact originals, retained sets and standard
derivatives, without repeating screenshot cleanup. Existing owned cast outputs
and prior category bytes are journaled and hash-checked for exact undo.
Unknown/edited files refuse; concurrent native/category/auxiliary edits prevent
installation. People/Review refresh after apply; repeat apply validates installed
outputs and refreshes reports rather than installing twice.

Synthetic tests cover the full retained-cast flow, including a second isolated
prepared rebuild and undo. No real rebase, optional cast release, threshold
calibration, workflow retargeting or production apply ran. C1/C3/C5/C7 and
real C2/C6 acceptance remain open.

## Scope and dependencies

**Oct 25 clarification:** the next user acceptance run is a clean supplied-image
start with new intake preparation, optionally stopping after intake or resuming
through matching/assignment. It is not another matcher-only raw-source rebase.
The complete wording and I21/I22/I23 handoffs live in the
[intake plan](2026-10-23-image-intake-preparation.md#oct-25-incremental-scope-and-the-next-clean-start-acceptance).
Do not run that rebase before integrated preparation/retained-set lineage is
ready. Matching uses a fresh reference baseline while preserving original-name,
manual override and family decisions through verified stable-ID migration;
refusal guards alone do not count as delivering that migration. The checkpoint
above records the implemented one-to-one path and remaining acceptance boundary.

Own the new configurable cast seed/remaining-photo experiment and its sandbox
acceptance. Do not duplicate the matching engine, enhancement algorithms or
production adapter. Start only after [intake I8](2026-10-23-image-intake-preparation.md)
and [upkeep U1/U3/U6](2026-10-22-library-upkeep.md) handoffs.
[Engine acceptance E4/E6/E7/E10](2026-10-22-likeness-engine-acceptance.md)
owns general repeatability, metrics/convergence and approved thresholds; this
plan supplies the new cast-scope experiment. See [ordered phases](README.md#current-library-work-order-oct-23).

## Changed direction, not yet implemented permission

Oct 23 follow-up authorizes beginning a preparation-only sandbox pilot, including
cast core images with no reassignment. All-photo preparation can be evaluated
while membership is frozen; it does not depend on choosing a cast-release count.
The later optional membership experiment below still needs C1 approval.
Older uncropped-source recovery is deferred, not a prerequisite to processing
the currently available library. Full user wording is in the
[intake follow-up](2026-10-23-image-intake-preparation.md#follow-up-chat-verbatim).

The installed trial retained cast Gallery membership and flattened non-cast
candidates. The requested experiment prepares **all images**, retains an
explicit trusted cast seed subset, and considers eligible remaining cast photos
alongside the clean non-cast pool. This extends the earlier optional low-core
candidate idea; it is not ordinary automatic stripping of protected identities.

| Distinction | Proposed boundary |
| --- | --- |
| Image processing | Every seed, selected/protected photo and candidate gets the Phase 1 recipe or an explicit held/unchanged/error outcome; retained does not mean unprocessed |
| Fixed cast identity | Preserve Angel/Sister slots, stable IDs, recorded names/history, catalogue metadata and references; image cleanup does not rename or replace a character |
| Core evidence | Freeze eligible seed references for a run; retained membership and protected/workflow status alone do not make a photo trusted core evidence |
| Mandatory retention | Existing workflow selections, explicit photo protection and anchors remain retained; unsuitable references are retained-but-not-core or held, never silently released |
| Re-evaluation | Only explicit sandbox rebase mode may release eligible non-seed cast photos after preview of the exact release set |
| Non-cast identities | Clean rebuild may regroup/classify/re-pair eligible candidates; protected/manual decisions, exclusions and Artist provenance are not erased by category alone |
| Name continuity | Match by evidence first; reuse known names/stable IDs only through verified continuity, never seed matching with old folder labels |
| Final filenames | Normalize after destinations are assigned: fixed cast prefixes stay fixed, other prefixes follow final identity folders; preserve photo IDs and reversible move maps |

Existing automatic protection remains in force outside the explicitly approved
experiment. The user's broad non-cast rebase intent does not yet resolve safe
migration of persistent rejected-person IDs, protected identities or manual
corrections. These remain blockers, not permission to silently discard state.

## Seed policy proposals requiring agreement

Top five plus selected workflow photo is a **candidate mode**, not a hard-coded
default or an accepted threshold. Offer validated configuration for top-N,
minimum accepted score, retain-all-eligible, or an explicitly combined rule.
Define ranking reference, support/diversity, ties, minimum/maximum, fewer-than-N
cases and non-overlapping modes. User examples `0.40`/`0.45` are trial values,
not calibrated settings or raw whole-body similarity scores.

Select seeds against verified identity labels and an accepted baseline, not a
candidate's own inclusion in a centroid. Prevent high-scoring same-shoot
duplicates or contaminated old galleries from defining truth. Save initial
labels, source IDs and selection reasons before preparation; verify usability
and identity afterward without silently substituting a different person.

The current engine is face-based (YuNet/SFace aligned face features), not a
whole-body recognizer. Existing body/framing quality metrics are not body-ID
scores. [Face-analysis M1-M4](2026-10-22-face-analysis-evaluation.md) owns
explanation, labelled secondary checks and licence review; no new model is
implicitly selected here.

## Work

- [ ] **P1 either** C1 Define approved cast seed modes and exact meaning of
  mandatory-retained versus core-eligible versus releasable. Resolve top-N/
  threshold/combined behavior one question at a time; freeze per-slot labelled
  seed and release previews, selected photos, anchors and protection exceptions.
- [ ] **P1 ai** C2 Inventory all photos and decisions from the immutable source
  plus an explicit current-curation overlay. Include accepted Amelia Morgan
  history, pending swaps, exclusions, stable IDs, Artists and missing originals.
  Block reset when any decision cannot migrate; do not silently reapply sandbox
  manifests in production or lose work by restoring an old snapshot.
- [ ] **P1 ai** C3 Add schema-validated optional cast-release mode and shared
  policy/config resolution, permission guards and source/hash/recovery mapping.
  Preview every retained/core/released outcome before mutation; no force flag
  that bypasses protection in normal incremental processing.
- [x] **P1 ai** C4 Prepare all retained seeds and candidates through Phase 1, record
  source/prepared/analysis/recipe hashes and per-photo outcomes, and rebuild
  run-local face features/centering consistently. Flatten eligible non-cast
  sources exactly once with no old non-cast reference seeds. Optional released
  cast sources remain gated by C1/C3, not silently enabled.
- [ ] **P1 ai** C5 Run repeatable sandbox scenarios from the same immutable
  source/curation snapshot and preparation recipe. Vary only declared seed
  parameters; compare cast retention, released-photo destinations, false
  matches/misses, fragmentation, holds, runtime and conservation. Follow-up
  movement/convergence acceptance stays with engine E7, not hidden cascades.
- [ ] **P1 ai** C6 Install reversibly only after approved preview, then normalize
  final-folder filenames and regenerate maintained padded/head/chest outputs and
  derivative-backed viewers/index. Reconcile obsolete managed outputs safely;
  preserve unknown/edited files and exact action/rebase recovery. Verify selected
  input references; no automatic ComfyUI source retargeting.
- [ ] **P1 you** C7 Review before/after cast seeds, hair/overlay outcomes and
  every released cast destination; accept a configuration or request another
  isolated run. Record all image/decision counts and holds. Deliver accepted
  evidence to engine E6/E10 before incremental testing or production approval.

## Acceptance and coverage

| User request | Owner / verification |
| --- | --- |
| All categories prepared, including cast retained seeds | Phase 1 I6/I8 and C4; per-photo outcome conservation, no category silently skipped |
| Keep core identity and selected photo; configurable seed size/band | C1/C3; mandatory retention separated from core eligibility |
| Re-evaluate remaining cast and non-cast images | C2-C5; explicit release scope, shared engine, protection/exclusion migration |
| Repeat with different parameters | C5/C7; same source/curation/preparation baseline, run-separated cache/config/results |
| Names reused where appropriate and filenames follow new placement | C2/C6 preserve verified continuity; new family naming stays with family N2/N3; names never affect scores |
| Face versus body / secondary checks | Face-analysis M1-M4; no silent new body matcher or raw score averaging |
| Preserve recovery and existing work | C2/C3/C6; restore test, no unapproved production or workspace writes |

Counts must conserve each unique source photo ID across retained, assigned,
held and recoverably unusable outcomes; duplicates/provenance aliases are
reported separately. "All processed" does not mean all images improved,
every repair succeeded, or the system discovered ground-truth identities.
Production remains a separately previewed/approved engine P1-P6 gate.

The related chat request is preserved once in the
[intake plan's user feedback](2026-10-23-image-intake-preparation.md#related-chat-verbatim).

## User feedback (verbatim)

Source: `feedback/sister_and_angel_processing.md`, received Oct 23, 2026.

<!-- markdownlint-disable MD013 -->
```text
If we're able to implement proper clean-up, enhancements and optimization working properly, then I would like to also process the sisters and angels the same manner as we would the entire library during a rebase.  Today, we leave them out of the process and I think there are some images that may or may not pair up with others during a complete process.  The one concern I have is that I think I need to leave a few images in the sisters and angels to ensure that their identity would stick.  So, maybe the process is that we keep the top 5 images and the selected workflow image for each sister and angels to enhance them and put them back into the library.  Then we can pull all the others for the sisters, angels, models, and any other categories to process them as well.  If we leave a few core identities in place, we can maintain the integrity of each category while still benefiting from the enhancements and optimizations applied to the rest of the library and see where all the remaining images land.  It's more of a test of the end-to-end process (after we get the optimizations, cleanup and such in place.)

That way - at the end of the rebase:
    - ALL images are optimized, clean, enhanced, cropped, etc...  
    - The core identities of sisters and angels are preserved while still allowing the rest of the images to be processed and optimized.
    - I can verify where all the images for existing angels and sisters to land afterwards and possibly want to adjust just how many we keep for the core (so that needs to be configurable - it may be all the images in the core that score high already or it's a score value we decide to keep above 0.40 or 0.45 or whatever)
    - We can run the rebase multiple times with different parameters to keep more or less core images of the sisters and angels and see where things do land.
    - This may also lead us down the path of doing the secondary image checks to further refine the core identities and ensure that all images are correctly categorized and optimized.  
    - One idea I did have was to determine if the image checks are only face or whole-body, and whether we need to adjust the criteria for what constitutes a core identity based on different types of images during the likeness process.

Hope all this makes sense and it will fit in with the end-to-end rebase flows without too much problems or changes.  We've already done a lot of work to get it working to where it is - and this would just further refine all the images in the library from where they are today.
```
<!-- markdownlint-enable MD013 -->
