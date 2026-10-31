# 2026-10-23: all-image preparation and cast-seeded rebase experiments

**Status:** active (Phase 3; C6 installed and independently verified; C7 human identity/quality review remains)

**Queue focus:** C7

**Scheduling:** now: human placement review of the verified installed baseline.
Other open scenarios, C10 future duplicate selection and eventual Production/
family gates stay in this plan but are outside today's execution focus.

## Oct 29: fresh v23 matching continuation

The full 3,072-outcome intake and its independent artifact check passed.
The same `fresh-v23-20261029` run now resumes matching with
`--baseline working --cast-seeds core`. This deliberately uses the existing
protected/core/workflow-selected retention policy rather than the default
retain-all mode; it does not lower thresholds or authorize Production.
Matching started at 22:06 -05:00 with timestamped capture and a live measured
photo count. Audit releases, destinations, Review reasons, exact faces and
curation continuity before applying the saved preview.

The user's autonomous investigation, sandbox installation and publication
authorization is preserved in the
[performance continuation](2026-10-28-intake-performance.md#oct-29-autonomous-continuation-chat-word-for-word).
C8/C9 remain open until the real preview/install/viewer checks finish.

### Incoming-ID defect found before apply

The first v23 preview accounted for 2,793 people photos (Artists remain
separate), retained 1,218 cast photos and released 48. Review contained 421
photos: **364 lacked a recognized filename ID**, rather than failing a
similarity threshold. Direct inspection found 352 incoming Facebook downloads
whose IDs the existing `originals.standard_name` already understands, including
leading-dot download names. The clean matcher had skipped that normalization.

A failing regression reproduced zero matching candidates for such a download.
The fix derives an ID using that existing filename rule without renaming or
modifying frozen inputs. An inferred ID must be unique across the full
population; collisions and genuinely unidentifiable descriptive names still
hold. Only the installed destination is normalized using the recorded ID.
No content-based guess, fabricated identity or threshold adjustment is added.
All **67 clean-rebase/preparation/retained-evidence tests passed**, including
collision refusal and original-path preservation.

At 23:03 -05:00 the supported launcher began a matching-only `--replan`,
preserving the initial preview, prepared pixels and measured face cache.
The first preview is not installation approval; review the new destinations
and reasons before apply. Twelve descriptive/unknown names remain outside
the recognized-ID fix; do not silently invent IDs for those.

### Revised v23 preview and first-pass audit

The matching-only replan completed successfully at 23:43:54 -05:00.
Preparation manifest/pixels and face measurements are unchanged. Saved preview
SHA-256: `ce61389bd0fe07da8e4f7582fb7db998f6ebf1f5e7e93ee4f7c05d043a917873`.
The original preview remains in `initial-preview.json`.

| Evidence | Result |
| --- | ---: |
| Prepared people photos / separate Artist outcomes | 2,793 / 279 |
| Cast-only reference identities | 21 |
| Retained cast / eligible releases | 1,218 / 48 |
| Candidate-pool photos, including releases | 1,575 |
| Non-cast Gallery photos / destination identities | 1,476 / 181 |
| Review photos | 99 |
| Recognized incoming IDs, without source renames | 352 |
| Destinations differing from original Working folder | 942 |
| Destinations changed from the initial preview | 570 |
| Exact aligned face/model/selected-source bindings verified | 2,793 |

Review reasons are now 44 small-group cast resemblance, 19 high cast
similarity requiring same-person review, 17 ambiguous cast matches, 12
unrecognized/descriptive IDs, five multiple-face holds and two 56px-face
holds. The initial 421-to-99 reduction is not simply 352: newly admitted
candidates change grouping and expose additional legitimate cast holds.
No threshold was lowered and no forced match replaces Review.

All 1,575 non-retained-cast destinations received scored-face screening across
17 labelled sheets, alongside six original/prepared/exact-face release
sheets. Every source/destination route and selected SHA-256 was checked.
All 48 releases have false core/anchor/identity-protection/photo-protection/
workflow-selection flags. Three Drakness releases intentionally have no
core score because their multiple-face quality gate excludes them; they
remain Review, not confident regrouping. Other displayed scores retain their
actual configured meaning: a display band alone does not establish a core.

This is AI first-pass screening, not proof of identity. Numerical cohesion
flags a few groups for final user inspection, especially the 35-photo
`Prospects/Lucia Reyes` group (minimum leave-one-out centroid similarity
0.2332), the two-photo `Potentials/Celine Gilbert` group (0.2538), and the
68-photo `Prospects/Harlow Chase` group (minimum 0.2947). Leave-one-out
centroid similarity is diagnostic, not a substitute for the configured
average-linkage clustering rule or permission to silently split a group.
Family/protection calibration and the user's final inspection remain open.

The complete pre-install snapshot was previewed and started through
`library-backup.cmd` at 23:45 -05:00. It completed at Oct 30, 00:54:29 -05:00:
**72,991 files / 41,998,676,177 bytes**, with every file and SHA-256 verified
and exit code 0. Snapshot: `_backup/library-20261029-235003`; manifest SHA-256:
`b73ced418f289a0109899dd8601b368b2b55fa6337bcbf9f327b4e27c8280ccf`.
The supported same-run install started at 00:54:53. At 01:22 it remained
active in read-only preflight, with increasing process I/O and no staging or
publication yet. A quiet log is not grounds to restart it. Installation,
independent check and actual viewer acceptance remain separate gates.

Later live sampling found a real derivative-stage performance blocker,
not a suspended owner. The first attempt was stopped before any publication;
all 2,868 Working input hashes and the source catalogue were reverified.
Staging and the empty previous directory were preserved, not deleted, with
run-local receipt `install-attempt-20261030-040207.json`. The tested
[native-owner fix and retry evidence](2026-10-28-intake-performance.md#oct-30-measured-installation-blocker)
do not change this preview or its selected pixels. Retry the supported apply
against the same saved preview and existing verified backup.
The supported measurement-reusing replan completed at 04:23:54. All 2,793
audited photo rows, policy, selected preparation and catalogue bindings are
exactly unchanged; only the implementation binding changes. The rebound
preview SHA-256 is
`ec72a3523ccce9f0d3b26cf1a915fe071b4d9355735d9fb483e500f1cc3f7fc1`.
Apply restarted at 04:24:53, with the full backup independently reverified
at 04:33:51. All derivatives and retained details completed, but at 08:15:05
the pre-publication guard refused unowned legacy cast derivatives. No swap
occurred: `previous` is empty and `run.json` remains `preview`. Preserve and
verify the completed stage; explicitly journal all 2,401 colliding old files
for exact undo rather than infer reproducibility or regenerate the stage.
Actual installation/viewer success remains pending.

### Oct 30 resumed human-review milestone

The user resumed work at 09:53, asking for completed outputs to review while
automated acceptance continues. The native intake comparison report is ready
for image-quality feedback; final installed viewers are not yet published.
The current-input audit found 75 repeated IDs, all one incoming Various file
beside its assigned baseline version: **zero IDs have multiple competing
incoming Various files**, and the frozen overlay has no duplicate aliases.
Its 75 incoming replacements remain correct under the clarified refresh rule.
Do not compare processed baseline/output mtimes against an explicitly supplied
refresh as a reason to discard the refresh.

The supported measurement-reusing replan ran 09:54:17 to 10:03:30 -05:00,
exit 0. All 2,793 photo rows and Working inputs, policy, seed policy,
preparation, overlay and catalogue bindings remain exactly equal to
`pre-stage-recovery-preview.json`. Only `clean_rebase.py` and `derivatives.py`
implementation hashes changed. Preview SHA-256:
`616893eabf7e73921291bbe6a4c82be435eeb3c41f2d5becee22af3f9ade458b`.
The supported completed-stage read-only check started at 10:03:45 with
explicit exact-byte legacy preservation. This is not yet a publication result.

That read-only check completed successfully at 10:45:35: 2,793 photos and
48,792 staged files verify. Apply began at 10:53:34, reverified the full
snapshot at 11:02:06 and the completed stage at 11:39:48. It rolled back at
11:46:33 after Explorer's open handles prevented the `Various` rename.
All 2,868 Working input hashes and the source catalogue independently verify
unchanged. The stage is intact, plan `preview`, and `previous` has no files.
The exact old-file preservation inventory is 2,402: the 2,401 output conflicts
plus one old Drakniss headshot rejected by today's generation quality gate.
The receipt `install-attempt-20261030-114633.json` records the failure and
restore proof. Release the confirmed Explorer lock before replan/retry;
installed viewers and human identity acceptance remain open.

- [ ] **P1 ai** C10 Before a future run with competing same-ID incoming files,
  implement and test the user's newest-file-modification-timestamp selection
  rule, retaining nonselected bytes as scoped recovery rather than independent
  candidates. Define safe equal-timestamp behavior, preserve timestamp evidence,
  and keep refreshed source selection separate from derivative output mtimes.
  The current frozen run has no competing incoming duplicates, so this is not
  a reason to repeat its intake or delay its human-review milestone.

## Oct 28: renewed sandbox authorization

The user's complete direction is preserved in
[intake's Oct 28 continuation](2026-10-23-image-intake-preparation.md#oct-28-approved-prepared-image-matching-and-full-sandbox-iteration).
Match the final recommended prepared pixels, not the obscured original.
Retain protected/core/workflow-selected Sister/Angel anchors, but allow
unprotected low-scoring cast photos to re-enter normal grouping under C8.
Inspect every identity move and changed intake output, including exact aligned
face evidence. Non-cast identities may regroup and carry mutable family
associations without same-person merging or hierarchy. A large Review queue
requires diagnosis and evidence-based secondary checks, not a threshold cut
or invented confident assignments. Rebase iterations and small downstream
Prime samples are authorized; production is not.

Run `r17-20261028` starts with all 2,741 inputs. Immutable-source preflight
found 134 unlisted additions; all original manifest entries were exact and all
extra bytes were bound by the previous intake receipt. A separate durable
`_source-recovery/20261028-v17/receipt.json` records their non-destructive
relocation outside Source. The immutable manifest was unchanged and the
supported launcher's inventory then passed.

### Oct 28 matching audit and corrected preview

The initial preview has 21 cast reference identities and accounts for 1,209
candidate-pool photos, with 1,253 cast photos retained and 13 released. Artists
account for the remaining 279 intake outcomes and are not generally matched.
The initial 158 Review destinations included 55 repaired screenshots rejected
because quality read the original while using prepared-image face coordinates.
A regression reproduced this mismatch; quality now reads the selected pixels
without changing source identity/path provenance.

The matching-only replan preserves `initial-preview.json`, intake artifacts,
measurements, model evidence and thresholds. It completed with **89 Review
destinations**, down from 158, and **zero original-app-bar holds**. Normal
grouping changes also resolve some other small-group holds, so the net change
is 69, not simply 55. There are 168 changed preview destinations; these are
proposals, not applied moves. Remaining Review reasons:

| Reason | Photos |
| --- | ---: |
| Small-group cast resemblance | 48 |
| High cast similarity requiring same-person review | 5 |
| Ambiguous matches across cast identities | 5 |
| Missing stable photo ID | 26 |
| No face | 1 |
| Face below configured minimum | 2 |
| Multiple usable faces | 2 |

No threshold was lowered and no forced assignment replaces these holds.
The quality-input fix passes 39 focused clean-preparation/rebase tests.
All 2,448 persisted exact-face artifacts and their selected-source bindings
verify by SHA-256; the remaining cache entry has no detected face/vector.

All 13 cast releases are from Angelica. All original/prepared/exact-face
triples have received an initial visual inspection, but destination-cluster
and protected-core comparisons are still required before acceptance.
The inspected face crops are face-bearing and aligned; that is not proof
that different photos represent the same identity. Release is based on
configured core eligibility, not solely the displayed 0.3 score threshold;
a score above 0.3 alone does not establish current core membership.

Intake defects found during that audit: GMW survives on
`7513772466838834360`, and partial lettering/ring survives on
`7518039923121523507`. The separate Camaris bottom-pill residual is recorded
under intake I60. These prevent declaring every input clean.
The 11 intake junk candidates were visually inspected: eight are Artist
fantasy/dragon/scene images, which remain separate preparation-only evidence,
not blanket permission to discard art without a human face. Three are Various
inputs (animal screenshot, collage and below-threshold face). Their final
disposition remains subject to the existing scoped Junk/recovery policy.
Nothing has been installed and no new Prime batch has been submitted.

## Oct 27, 11:05: intake review precedes the next rebase action

Later user clarification: the next sandbox preview must expose the actual
approved core-retention thresholds and explicitly selected workflow reference
photos per Angel/Sister. The user's `x.xx` is not a new numeric policy.
The existing preview retaining all 1,266 cast photos is historical evidence,
not acceptance of the narrower next seed set. Preview demoted/non-core
destinations and protection conflicts before any moves; preserve fixed cast
slots, stable person IDs and reference selections.

- [ ] **P1 ai** C8 Reconcile high-confidence/selected cast seeds with current
  protections and usability gates (intake I44-I46). Show every retained,
  demoted, Review and Junk outcome, actual policy threshold, source score/
  domain and workflow selection; no unusable generated face used as core
  evidence. Run remaining inputs through fresh approved matching/grouping/
  merge-in/out rules, then separately propose near-but-not-same families
  under N7/N9; surname resemblance is not a merge criterion.
- [ ] **P1 ai** C9 After sample acceptance, validate the full sandbox rebase,
  grouping/family behavior, reversible original-name correction N12 and exact
  restore/check end to end. Only then preview equivalent production migration
  with verified backups, accepted policy/recipe, input hashes and explicit
  installation approval. No production changes are authorized by wanting the
  sandbox finished soon. Report incomplete gates rather than calling the
  sandbox or production library 100% accurate without evidence.

The user has reviewed Angels and some Potentials in the completed preparation
report and identified crop/erase/framing regressions. The bounded benchmark
and acceptance gate now live in
[intake I30-I37](2026-10-23-image-intake-preparation.md#oct-27-1105-review-driven-crop-erase-and-framing-refinement).
Preserve the completed preparation and matching preview as baseline evidence;
do not install that preview or repeat all inputs while the recipe is being
tuned. If selected prepared bytes change after acceptance, produce a new
versioned preparation/matching preview with all hashes and curation continuity
reverified; the old preview is not transferable approval for changed inputs.
C1-C3/C5-C7, R11 and Phase 2 recovery acceptance remain open. No source/cast
decision is implied by a promising cleaned image or generated audition.

## Oct 27: complete preparation; matching-preview continuity correction

The fresh run prepared and verified all **2,741 outcomes**, with
`assessmentErrors: false`. Its immutable preparation report and intake receipt
are complete. No installation or assignment has been performed.

The first matching preview stopped safely on a duplicate current photo ID:
an Angelica original still exists in its assigned Gallery beside the newer
Various screenshot that the overlay deliberately substitutes for preparation.
Both byte versions were already preserved, but the curation guard recognized
only isolated timestamp collisions, not this verified original/replacement pair.

The guard now accepts the original **only** when exactly one current file
matches the overlay's verified `immutable-original` recovery hash, and the
unique matching Various replacement names that recovered source target,
photo ID and prepared-input hash. The current original may have moved into a
cast Review folder since the source snapshot; its stable ID and bytes must
still match. Both current paths remain in the curation snapshot.
Unknown duplicates, duplicate original copies, changed originals and wrong
replacement targets still refuse. No stable IDs, assignments, source bytes
or overlay receipts are changed.
The regression reproduced the real refusal before the fix; all 47 related
rebase, clean-preparation and retained-preparation tests pass afterward.

Matching preview is being retried against this same verified run, without
`--apply`, installation or repeating preparation. Log: session
`files/prepared-matching-retry-20261027.log`. Final preview counts remain
pending; do not infer acceptance from the completed preparation.

The matched preview subsequently exposed two historical display-label
collisions, not a likeness-scoring failure: Eloise's one-to-one output group
was labelled Jade, and Dahl's was labelled Afton, while those labels still
belonged to other stable IDs. Labels are now retained from the current stable
identity in this narrow case, only if its current folder is otherwise unused
by the new routing. No face assignment, membership, score or other identity
record changes. Split/merged decision-bearing identities and occupied fallback
folders still refuse. `Various` root holds also cannot rename a stable identity.

`bin\sandbox-rebase.cmd ... --include-current-various --replan` can now resume
an incomplete matching preview without a saved `run.json`, provided this run
has its complete verified `intake.json` and measured cache. It rechecks
preparation, rebuilds matching from the cached content hashes, and saves only
a preview. Missing or tampered preparation still refuses; no apply is implied.
Both new regressions failed before the fixes; all 49 related tests pass.
The resume log is session `files/prepared-matching-resume-20261027.log`.

That retry exposed 11 case-insensitive destination collisions among 22 legacy
photos without stable IDs. They were correctly excluded from matching and
held in `Various/review`, but identical filenames from different source
folders would overwrite one another. Only these colliding missing-ID holds
now receive a deterministic `_held-<source-path-UUID>` filename suffix.
Both copies and their preparation lineage remain separate, even when their
bytes are identical; no new photo ID, identity assignment or deduplication
is inferred. Protected, cast and ID-managed routing guards are unchanged.
The regression reproduced the real refusal before the fix and verifies
preview/replan determinism, retained evidence, install/check and exact undo.
All 885 normal tests in 29 suites pass. Final preview retry log:
session `files/prepared-matching-holds-20261027.log`.

The final retry completed successfully as **`status: preview`**. Its 2,741
prepared inputs comprise 2,462 general photos and 279 Artist inputs, kept
outside general matching. The 21 Angel/Sister reference identities retain
all 1,266 existing cast photos. Of 1,196 non-cast inputs accounted for,
1,048 route to non-cast galleries, 40 are proposed cast **Review** additions
(27 Angels, 13 Sisters), and 108 remain in Various Review. There are 26
missing-ID holds, including the 22 filename-disambiguated copies.
The source manifest, overlay and live catalogue hashes still match the
preview bindings. No Working assignment, catalogue, cast or source bytes
were changed. The launcher's final read-only `--check` exited 0.
The run-local `report.md`, `photos.csv`, `policy.json`,
`catalog.json` and `run.json` are the review evidence; measurement reuse
is explicit in the receipt. C2/C6/R11 remain open for broader acceptance and
approved reversible installation, not more preparation.

## Oct 26 late: fresh all-input retry in progress

The renewed end-to-end authorization is preserved in the
[rendering owner](2026-10-25-reference-rendering.md#oct-26-2312-continuation-finish-the-whole-pipeline).
Started a **new** intake-only run
`Working\_sandbox-state\clean-rebase-20261027-full-intake` after its read-only
preview: 2,741 outcomes, 74 newer-byte replacements, 41 additions; about
400 GiB available. First verified progress: 101/2,741.
The owned detached process logs to session `files/intake-full-20261027.log`;
on exit 0 it runs the launcher's read-only `--check`. It stops on error,
never deletes/restarts an unfinished mirror or resumes the failed Oct 25 run.
This is preparation only: no matching/install, cast changes, production writes
or interference with ComfyUI. R11 and C2/C6 remain incomplete until the actual
receipt and recovery/curation gates are verified.
A separate bounded supervisor now waits for this run's `intake.json`, refuses
assessment errors, runs the read-only verification and then saves the ordinary
matching preview only. It never uses `--apply` or installs a new assignment.
Eight-hour receipt wait; failures stop visibly in session
`files/prepared-rebase-preview-20261027.log`. Snapshot at 05:30 UTC:
669/2,741 prepared; no completed intake receipt yet.

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
- [x] **P1 ai** C6 Install reversibly only after approved preview, then normalize
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

### Oct 30 refresh selection and human-review milestone (chat, verbatim)

<!-- markdownlint-disable MD013 -->

> Sure - but it should actually replace them if a new image came in with the same id - that can happen if we're trying to pull a refreshed image through again or it's just that we're replaying the same images through so they can get cleaned up, cropped, composed - so it must replace the old ones in the padding or anywhere.  If we have two images that collide in a run for some reason we want the newest file timestamp.  Is that what we did for the collisions?

Human-review request:

> Let's get to a point where it's ready for Human review - if you do have parts ready for my review already - please let me know what I can look at while you are completing the rest.  I can gather feedback on any of the completed reports, pages, outputs that are generated while you are iterating aggressively on the remaining automated work you have to do.

<!-- markdownlint-enable MD013 -->

Coverage: refreshed-source and generated-output replacement -> C6; competing
incoming same-ID newest-timestamp behavior -> C10; current-run audit and
parallel human intake review -> resumed milestone above, C7 and performance
T16. Backup scope/format/retention priority remains storage S24.

## Oct 30 afternoon: resume without reboot and full-scale journal failure

The read-only handle scan found no remaining Various handle. The user
authorized resuming while ComfyUI continues, accepting resource contention.
No new intake, model/recipe change or Production write is authorized.

The old recap's bare replan command defaulted to `all`; the exact comparison
caught changed seed/decision bindings before any install. The corrected
supported command uses `--baseline working --cast-seeds core`. All 2,793 rows
and every frozen field match the preserved audited
`pre-resume-20261030-1521-preview.json`; only time/implementation rebinding
may differ. The recap's check/apply commands now carry the explicit policy.

The completed-stage check passed 2,793 photos / 48,792 files. Apply began at
17:06:50 -05:00 and reverified the existing 72,991-file / 41,998,676,177-byte
snapshot; it did not create another full backup. At 18:30:52 it failed:
the 19,623,486-byte applied journal exceeded retention's old 16 MiB reader
limit. Automatic rollback restored library files but left an `applied`
journal; this was not installed acceptance.

The failure is preserved in run-local
`install-attempt-20261030-183052-manifest-limit.json`.
Independent `manifest-limit-rollback-verification.json` verifies all 7,686
recorded original hashes (including all 2,868 Working inputs), all 48,792
staged hashes, unchanged source catalogue and no files in `previous`.
Only 2,681 empty generated publication directories were removed; no source
image or retained file was deleted. The exact audited preview was restored
after verification, then rebound through supported core-mode replan.

The fix keeps a bounded 64 MiB retention receipt and restores the previous
journal on registration failure; transaction rollback removes only empty
directories it created. Platform JSON serialization is preserved so catalogue
hashes do not change merely from writing. Regression fixtures reproduce the
old failure before verifying rollback, retry and undo.
The supported runbook in [likeness](../art/likeness.md) owns these semantics.
At 19:07 -05:00 the final same-stage check/retry started; no installed
success or viewer acceptance is claimed by this checkpoint.

Coverage: handle diagnosis and authorized retry -> C6/T16; independent
rollback/backup audit -> storage S15; actual installed pages -> intake I59;
human quality/identity acceptance remains C7/I60. ComfyUI contention prevents
interpreting these wall times as isolated performance benchmarks.

### Oct 31, 02:19: final installed verification

C6 is complete, not C7's human identity/quality approval. The same-stage apply
finished at 00:28:56 -05:00, exit 0. The independent ordinary launcher check
passed; all 48,792 published files and 2,793 frozen rows remain accounted for.
No new intake, another full backup, recipe/default change, ComfyUI submission
or Production write occurred.

The separate recovery audit verifies exact rollback inventories and all 7,686
file hashes (4,018 category plus 3,668 external), all 279 unchanged Artist
sources and installed catalogue SHA-256
`9293fce4863cfdb2264cf48c6e06b8ef5bcb002538ef4a1d265eb53413a6efaa`.
The applied journal and catalogue stayed byte-identical through report repair.
Actual full-scale undo was **not** executed; rollback bytes/readiness were
audited, prior failed-install rollback was proven and fixtures exercise undo.

Actual Edge acceptance verified 2,793 exact-face/preparation evidence records,
2,694 Gallery / 99 Review, person/name/location filters, actual head/chest image
changes, Overview controls, native padded and exact 112x112 aligned face,
retained detail/return links, and source-hash-matched per-photo intake history.
No loaded-image failures, unexpected missing local targets or JavaScript
errors remained. Optional shared Outputs/Comparison links still point to
uninitialized reports; this is explicitly reported under gallery L19, not
silently treated as successful navigation.

The browser initially caught another real scale defect: the 49,709,196-byte
preparation manifest exceeded the history reader's old 8 MiB limit, leaving a
run label and **zero** photos. The 64 MiB bounded fix preserves path/hash,
scope and row limits. A tested `people-gallery-review.cmd --history-only`
preview/apply/check repairs only history and ownership metadata, avoiding a
second hours-long viewer refresh. All 56 focused history/retention/Review
tests passed, followed by actual browser verification of 2,793 history rows,
filename filtering and the original source-bound photo trace. Frozen intake
history retains its historical staged/not-accepted label; it does not itself
prove the independently verified final publication.

Durable evidence beside `run.json`:

- `installed-recovery-audit-20261031.json`
- `installed-viewer-acceptance-20261031.json`
- `installed-refresh-stack-20261030.txt`

[Performance T16](2026-10-28-intake-performance.md#oct-31-measured-installed-continuation)
owns measured timings; gallery L18 owns repeated verification I/O.
Storage S24/S25 remains before another expensive run. C7/I60, known quality
defects, family/name/engine acceptance and Production approval stay open.

## Oct 31: cast routing, name continuity and iteration audit

The user asked for more than technical installation: explain cast moves,
names/families, what worked, remaining iterations and speed. This follow-up
audits every frozen decision and name sidecar, not faces or biological identity.
Existing first-pass image screening is historical evidence, not a new
image-by-image identity sign-off. The user's visual/identity review remains C7;
I60's cleanup-quality work and C8/C9's wider acceptance remain open.

### Actual cast movement, not just matching suggestions

All 2,793 installed decision rows equal the audited pre-install preview.
There are 942 **folder** changes across the full people population. Filename/
extension normalization is separate: 281 retained cast paths changed without
changing their cast folder or Gallery membership.

| Category | Before | Retained Gallery | Released to candidate pool | Review placements now | Final Gallery + Review |
| --- | ---: | ---: | ---: | ---: | ---: |
| Angels | 463 | 445 | 18 | 36 | 481 |
| Sisters | 803 | 773 | 30 | 27 | 800 |
| Total | 1,266 | 1,218 | 48 | 63 | 1,281 |

**No new image was automatically promoted into a cast Gallery or core.**
The 63 cast Review placements comprise 58 non-cast arrivals, three Angelica
releases held in Angelica's own Review, one Drakniss release held in
Angelica Review and one Draknoxa release held in Sammara Review. These are
review suggestions, not accepted cast replacements. No fixed slot changed
occupant through a rename/swap. A best-match field is not a destination.

| Fixed slot | Before | Retained Gallery | Released | Final Review | Final total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Camaris | 51 | 50 | 1 | 5 | 55 |
| Gavrielle | 20 | 19 | 1 | 0 | 19 |
| Nyxene | 15 | 15 | 0 | 0 | 15 |
| Ravaelle | 79 | 76 | 3 | 2 | 78 |
| Angelica | 61 | 49 | 12 | 15 | 64 |
| Azaline | 18 | 18 | 0 | 0 | 18 |
| Haniya | 94 | 94 | 0 | 0 | 94 |
| Remiah | 51 | 51 | 0 | 2 | 53 |
| Sammara | 17 | 17 | 0 | 6 | 23 |
| Sandalyn | 11 | 11 | 0 | 3 | 14 |
| Seraphine | 46 | 45 | 1 | 3 | 48 |
| Draknara | 97 | 97 | 0 | 5 | 102 |
| Draknava | 40 | 40 | 0 | 0 | 40 |
| Drakness | 113 | 110 | 3 | 2 | 112 |
| Drakneta | 31 | 25 | 6 | 4 | 29 |
| Draknira | 34 | 33 | 1 | 0 | 33 |
| Draknisa | 95 | 95 | 0 | 1 | 96 |
| Drakniss | 322 | 307 | 15 | 7 | 314 |
| Drakniya | 23 | 21 | 2 | 3 | 24 |
| Draknora | 26 | 25 | 1 | 0 | 25 |
| Draknoxa | 22 | 20 | 2 | 5 | 25 |

Of the 48 releases, 27 went to Potentials Gallery, seven to Prospects Gallery,
six to Models Gallery, five to Angel Review and three to Various Review.
The three Drakness releases are quality/multiple-face holds, not confident
alternative assignments. All releases have false core, anchor, identity-lock,
photo-lock and workflow-selected flags. All 21 workflow selections and three
configured anchors remained retained; 19 selections are also core members.
Two workflow-selected non-core photos remained retained deliberately.

Thus the **recorded safeguards and conservative routing worked**. It does
not follow that every release/grouping is visually right: the policy permits
unprotected low-scoring photos to leave fixed cast Gallery. Highest-yield
human checks are Drakniss's 15 releases, Angelica's 12 and Drakneta's six
(33 of 48 together), plus both Sister-to-Angel Review suggestions. Do not
lower thresholds or auto-promote these holds to make the result look cleaner.

### Names and organizational families: preservation is not reconciliation

- The source catalogue was empty and no prior local catalogue existed. The
  run created 202 identity records; migration of previously populated stable-ID
  family/name metadata was therefore **not exercised by this dataset**.
- The installed catalogue contains **zero structured `names` records and
  zero `family` records**. This run did not execute family reconciliation,
  correction N12 or automatic family-name assignment.
- All 21 cast `z_` name/history files match the frozen source hashes. Of 181
  non-cast destination summaries, 133 preserve a same-label source file
  byte-for-byte; 48 are generated summary stubs pointing to the run journal.
  Complete source sidecars remain in the overlay: 194 people plus 67 Artist.
- No duplicate recorded full-name labels were found across the 202 people
  destinations. However, **45 surname labels are shared across 118 folders**.
  With zero family metadata, these surnames must not be presented as accepted
  organizational-family links, let alone real relationships.
- 61 old non-cast folders split across destinations; 105 non-cast destinations
  combine more than one source folder. These are routing facts, not errors
  by themselves. A copied name/history file is not proof that its old label
  correctly describes all new members, nor is a generated name an original
  source name. N9/N12/N13 and C8/C9 retain this acceptance boundary.

Concrete review anchors from recorded lineage: Lucia Reyes now has 35 photos
from its own old folder; Celine Gilbert has two from Celine Gilbert and
Keira Stone; Harlow Chase has 68 from Harlow Chase, Lucia Reyes, Davina Banks,
Angelica and Various. These were already flagged for review by existing
diagnostics; no new face comparison or identity conclusion is made here.

### What worked, and what needs another iteration

| Area | Finding | Next owner / boundary |
| --- | --- | --- |
| Conservation and publication | Audited rows unchanged; protected/core/selected membership preserved; no automatic cast Gallery additions | C6 delivered; C7 human review remains |
| Cast release and regrouping | Exact destinations/reasons available; 48 releases and 99 holds conserved | C8/C9 and C7: inspect intended placement; do not treat score bands as truth |
| Cleanup | Prior output screening and artifact proofs exist, but known overlays/framing/repaint defects remain | I60/I68/I69; reproduce named cases on a bounded frozen set |
| Names/families | History files preserved, but no structured family/name reconciliation occurred | N9/N12/N13; explicit reversible correction/family acceptance, no automatic rename now |
| Speed | Installation succeeded, but repeated provenance verification dominates useful next speed work | L18 with T15/T17; see the linked performance audit |
| Storage | 48,792 publication files include 34,567 retained-evidence files; 8,255 maintained derivatives, 2,793 originals, 2,793 natives, 181 name stubs/copies and 203 other receipts | S24/S25; preserve sources/recovery, measure before packing/pruning |

The 99 Review outcomes remain 44 small-group cast holds, 19 high-cast holds,
17 ambiguous-cast holds, 12 missing-ID holds, five multiple-face holds and
two small-face holds. This is explainable conservative behavior, not proof
that these are all genuine errors or that the remaining Gallery is correct.

The read-only audit is preserved beside the run in
`outcome-audit-20261031/audit.json`, `cast-transitions.csv` (106 distinct
release/arrival rows; five rows belong to both sets), `name-lineage.csv`
(202 folders) and `audit-rebase-outcomes-20261031.py`. The script checks
current catalogue binding, all sidecar hashes and protection/routing
invariants. It does not rerun inference, modify images or assert identity.
The [performance follow-up](2026-10-28-intake-performance.md#oct-31-outcome-review-speed-priorities)
ranks measured next work without starting another full intake.

### Oct 31 review questions (chat, verbatim)

<!-- markdownlint-disable MD013 -->
```text
Did you do a full review of what happened in the sandbox rebase and validate those images and the moves make sense to you?

I'll do my review, but I'm wondering if you did inspections and comparisons to see if things did move in/out of angels or sisters as well as the family names and if it all makes sense and what actually worked and what might need more iterations and features looked into.  If you can also look at the performance and speed issues that would also be the most useful.
```
<!-- markdownlint-enable MD013 -->

User words (chat, Oct 30), word for word:

<!-- markdownlint-disable MD013 -->
```text
Can you check if the file handle is fixed - I am still waiting to be able to reboot.

Why don't we try to start things back up again.  I do have comfy running and taking up some CPU, GPU, memory and disk utilization - so it might be slower, but we should try to push the next phase of the work and verify the results.
```
<!-- markdownlint-enable MD013 -->
