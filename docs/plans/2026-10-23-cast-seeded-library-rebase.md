# 2026-10-23: all-image preparation and cast-seeded rebase experiments

**Status:** active (Phase 3; blocked on accepted Phase 1 preparation and Phase 2 recovery)

## Scope and dependencies

**Oct 25 clarification:** the next user acceptance run is a clean supplied-image
start with new intake preparation, optionally stopping after intake or resuming
through matching/assignment. It is not another matcher-only raw-source rebase.
The complete wording and I21/I22/I23 handoffs live in the
[intake plan](2026-10-23-image-intake-preparation.md#oct-25-incremental-scope-and-the-next-clean-start-acceptance).
Do not run that rebase before integrated preparation/retained-set lineage is
ready. Matching uses a fresh reference baseline while preserving original-name,
manual override and family decisions through verified stable-ID migration;
current refusal guards do not count as delivering that migration.

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
- [ ] **P1 ai** C4 Prepare all seeds and candidates through Phase 1, record
  source/prepared/analysis/recipe hashes and per-photo outcomes, and rebuild
  run-local face features/centering consistently. Flatten eligible non-cast
  and released cast sources exactly once with no old non-cast reference seeds.
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
