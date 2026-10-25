# Original photos: pick, rename, scale, prune

How the photos you start from (the originals every angel and sister is built from) are kept, named and handed to the workflows. One command does the housekeeping; you only drop, move and delete files.

## The library

Under the work folder (`paths.workRoot` in `workflows/workspaces.json`, today `B:\Soverign Territories`):

```text
Angels\Angelica\gallery                  your originals for Angelica (jpg, png, webp, bmp)
Angels\Angelica\gallery_944x1104         made by the tool: every original on a cream 944x1104 canvas, as PNG
Angels\Angelica\headshot_944x1104        made by the tool: the face of each original, cropped around it and scaled up (see Headshots)
Angels\Angelica\chest_944x1104           maintained chest-up crop for the viewers, not a new workflow input
Angels\Angelica\.photo-derivatives.json exact source/output hashes and rendering recipe for maintained derivatives
Angels\Angelica\review                   photos the likeness tool is not sure about (yours to look at)
Angels\Angelica\gallery\z_angelica.txt   the person's name, profile and history (written by the likeness tool; see likeness.md)
_archive\Angels\Angelica\...             old scaled copies and set-aside duplicates (the same path as the folder)
_junk\Prospects\rhea_ives_...jpg         legacy unusable photos, flat per side; retained, not automatically retried
_junk\Various\gallery\incoming.jpg      report-bound early Junk; exact source path retained below _junk
_junk\Artists\Artist\gallery\image.jpg   early artist Junk; owner never becomes Various or another artist
Sisters\Draknara\...  Prospects\Anya Sloane\...  Artists\Pierre\Mara Locke\...  Various\...   the same layout in the other roots
```

The roots are Angels, Sisters (the old name, Models, is still read), Prospects (people who are not yet an angel or sister), Artists (an artist's photos, grouped into people) and `Various`, the pool of photos not sorted yet, at the top level next to them. `paths.photoRoots` in `workspaces.json` changes the list.

## The routine

### Agreed end-to-end flow and current cutover boundary

The Oct 23 clarification separates **source preparation** from **derivative
framing**. The target flow below is agreed direction, not the installed
`library.cmd` sequence. The [intake plan](../plans/2026-10-23-image-intake-preparation.md)
owns upstream preparation/crop cutover; the
[upkeep plan](../plans/2026-10-22-library-upkeep.md) owns downstream integration.

| Order | Role | Output / safeguard |
| --- | --- | --- |
| 1 | Retain exact incoming bytes before transformations | Verified raw-source/provenance link, separate from the prepared working reference and reproducible outputs; durable storage placement still needs its gate |
| 2 | Prepare at native geometry | Safe first crop -> targeted overlay repair if needed -> optional finishing crop -> issue-specific denoise/tone; preserve head/hair, skip unnecessary stages, retain unchanged content with reasons where unsafe/unavailable |
| 3 | Analyze and assign | Fresh geometry-correct detection/features; shared likeness policy; cast membership protection remains separate from processing |
| 4 | Publish the accepted reference | Prepared source in person `gallery` (or `review`), destination-prefix normalization with stable photo ID and history retained |
| 5 | Generate standard 944x1104 derivatives | Full-photo fit/pad, head framing and chest framing from the accepted source; framing crops/padding remain necessary, but must not rerun source-cleanup crops |
| 6 | Refresh viewers and selected workflow copies | Thumbnails use maintained derivatives, with raw/prepared comparisons available separately; sync verified explicitly selected derivative files to ComfyUI inputs |

The raw original is for recovery/comparison. The Gallery file is the native
working reference, not the normal workflow input. The user uses the 944x1104
outputs for ComfyUI. Full-photo padding preserves the prepared photo's aspect;
head/chest framing has its own crop/fit policy and quality checks. Do not make
all three identical or reinstate the retired frame experiment. A requested
crop cannot recreate hair already absent from the input.

**Subject-preserving composition (Oct 24 clarification):** source cropping
also removes excess background, not just screenshot clutter. The intended
sequence is retain original -> initial safe crop -> localized cleanup ->
final composition crop -> publish accepted native source -> padded derivatives.
Keep the visible person centered with breathing room, preserving head/hair,
torso, arms/hands and legs/feet in a full-body source. Do not force a fixed
aspect ratio or cut limbs to fill 944x1104; padding handles that canvas.
Centering follows the full visible subject, not only the face. Already-tight
inputs can skip either crop; retain wider useful context when subject bounds
are uncertain. Head/chest derivative framing is a separate later operation.

The retained-preparation staging API publishes exact incoming bytes under the
destination owner's `gallery_org/<set-key>/original.ext`; the accepted
native image remains in `gallery` or `review`. Its declared variants (including
denoise/tone, masks, previews and padded comparisons), photo detail and recipe
are retained under `gallery_intake/<set-key>/`. The 32-hex set key covers the
immutable source path, source photo ID, matching domain, original SHA-256 and
full recipe; byte-identical distinct photo records are not deduplicated.
The manifest preserves and verifies those full identity fields, not just the
short directory key. It copies only that
retained row's artifacts, not discarded candidates or historical runs, and
refuses existing sets rather than overwriting evidence. This staging API does
not itself run preparation or enable the production library cutover.
Copied variants use short deterministic filenames directly inside the set,
avoiding repeated SHA-256 directory names and Windows path-length failures.
The manifest maps each exact source artifact path to its published path;
detail links are rewritten without changing artifact bytes or checksums.
Retained detail pages identify themselves as retained intake evidence, with
current-native and available gallery/history return links. The shared
`retained_preparation.refresh_detail(root, current_photo, photo_id=None)`
refreshes navigation after viewers and maintained derivatives exist, updating
the detail and manifest checksums together. It links full/head/chest outputs
only when their maintained source/output hashes and recipe verify. Staging
callers must capture their final file inventory after this refresh.
Clean-rebase staging can pass `include_gallery_navigation=True` to include
conventional gallery/Review/history return links before those required
post-install pages exist; derivative links still require existing verified
outputs. This permits capturing final retained hashes before publication,
without mutating published evidence afterward.

The bounded per-photo manifest records the original checksum, selected native
checksum, exact current path, stable photo ID and matching domain. Overview and
Review prefer this link only after verifying the current photo and every
retained artifact; neither basename nor photo-ID similarity proves a move.
Originals housekeeping preserves `gallery_org`; routine backups retain both
retained directories rather than treating comparisons as disposable outputs.
Same-owner originals renaming updates the manifest with rollback on failure.
Matching moves transfer the entire verified retained set with their journal:
the original and every declared artifact move to the new owner, the manifest
records the new native path, and undo restores the exact previous manifest and
bytes. Source versions are frozen before backup and checked again afterward;
existing destination sets, changed evidence and cross-domain transfers refuse
before mutation. Do not manually move these photos or owner folders. Derivative framing remains
separate: never copy padded outputs back over retained originals.
Whole-identity category transitions and merges with retained directories are
planner holds, not partial folder moves. They leave the source set untouched
while unrelated photo membership moves remain eligible in the same run.
Manual photo actions use the same retained-set transfer boundary, including
Review moves, rejection to Various, retirement and Junk. Their exact transfer
snapshots live beside action recovery reports under `_reports/runs/`; undo
checks those snapshots and all current retained hashes before moving anything.
Whole-person folder renames with retained sets are explicitly held rather
than orphaning lineage; same-slot metadata-only name changes do not move sets.
The shared Intake runs navigator also discovers checked intake-only receipts
under `_sandbox-state/<run>/intake.json`, using only that run's fixed
`inputs/_reports/preparation/all` report and source mirror. Receipt input hashes,
manifest checksum and full preparation verification must pass before links
appear. These entries are labelled staged/intake-only, never accepted
publication or inferred current-photo continuity. Reports outside this
conventional run directory are not automatically discovered.

Removing an external bar is not repairing text over hair. Blending/inpainting
may synthesize plausible pixels rather than recover the true hidden image;
such repairs require a recorded mask/recipe and must not silently become
trusted identity evidence. When unavailable/unsafe, retain content and expose
the warning, without forcing manual intervention solely for overlays.

**Crop/repair refinement (Oct 23):** consider each edge independently.
Remove separable external UI panels first, not only perfectly uniform strips.
If that clears the image, skip repair. Otherwise attempt localized repair of
remaining graphics where validated; if unsuccessful, a finishing crop may
trade some lower-body/background coverage for less clutter. This is not
permission to cut head/hair to satisfy a clean-image target. Do not repeatedly
crop an image until a detector reports no text. Record crop coordinates,
repair masks/results, skipped-stage reasons and any sacrificed body coverage.
Keep original, first-crop, repair and finishing-crop comparisons separately.

**Eraser and purpose-specific references (Oct 23 follow-up):** use "eraser"
as the user-facing name for a targeted masked repair attempt, not a promise
of recovered original pixels. Crop/eraser attempts may alternate as bounded,
traceable candidates; retain the last safe result and stop on no improvement
or uncertain subject loss rather than progressively destroying context.
If erasing right-side reactions fails, a side crop can be preferable to
keeping clutter when it avoids the useful person region. Background and
flowing dress edges can be expendable; arms, hands, torso and outfit details
must be considered, not just the face. Losing legs is purpose-dependent,
not an unconditional acceptance rule. Later padding standardizes the canvas
but cannot restore discarded pose/outfit evidence.

Keep all three standard derivative roles available for explicit selection:

| Reference | Useful starting point, not an automatic rule |
| --- | --- |
| Gallery/full 944x1104 | Carry useful outfit, body pose or composition into a workflow; a source already in an A pose can help an A-pose target |
| Chest 944x1104 | Retain face/hair and upper-body context while reducing lower-body pose influence |
| Head 944x1104 | Emphasize identity when crouching/lying or another source pose fights the target; body/figure/pose tags still describe the desired output |

The user tested a variety of these roles in `0_Edit`; usefulness depends on
the expected output and must be compared in ComfyUI. No universal best framing
or automatic full-to-head/chest switch follows. A cleanup recommendation is
not a workflow-reference ranking. Preserve the recoverable fuller source so
a crop suitable for a head/chest task does not erase the option of using
outfit/pose context later. Pixel-change or face-similarity scores alone cannot
decide which reference best serves a particular generation.

Direct inspection of the two supplied examples establishes these pilot cases:

- `Screenshot_20261010_123511_Facebook.jpg`: top/bottom external app panels
  surround a clearly bounded photograph. The v5 solid-strip rule removes only
  34 top pixels, not the full top panel. A better first crop should retain the
  full visible head and useful body. Right-side reaction icons still overlap
  the photograph/dress and require separate treatment; removing panels alone
  does not remove all graphics.
- `Screenshot_20261010_123318_Facebook.jpg`: the search overlay crosses the
  hair, so a top crop is not a safe solution. The bottom comment/navigation
  panel is separable; remaining captions/icons could be repair candidates or
  motivate a higher bottom crop with recorded loss of lower-body context.

These observations guide intake I11 experiments, not automatic crop coordinates
or an accepted repair recipe. Small simple-background marks and large overlays
over hair/body need different safeguards. Face boxes are not hair segmentation.

**Still-installed paths to replace together, not abandon as legacy code:**

- `library_sync.plan` currently runs `originals` before matching and invokes
  `likeness crop`, which may replace working Gallery photos.
- `originals.fit` can independently apply the fixed screenshot crop, even
  without a face box; `originals.headshot` applies screenshot-specific logic.
- Maintained padded/head output calls those helpers; maintained chest output
  also contains screenshot cropping. Viewer framing inspection has another
  screenshot-coordinate adjustment. These must respect one accepted geometry
  decision instead of applying hidden cleanup a second time.
- `comfy_workflows.photo_library` enumerates full-photo scaled outputs;
  `headshot_library` recognizes deliberately selected headshots. Chest output
  generation does not yet establish complete chest selection/repoint/sync
  support. Preserve existing choices; do not silently switch framing.

At cutover, ordinary library runs must stop the old source-overwriting crop
route, and direct legacy crop commands must explicitly redirect/refuse or
offer a clearly separate recoverable migration mode. Keep existing crop-history
and undo/recovery records usable. Detect/cache face coordinates against the
accepted prepared bytes; old source coordinates cannot be reused after a crop.
Version derivative recipes and verify regeneration/recovery rather than
changing existing provenance records to bless new pixels.

These are intake I12 and upkeep U7 acceptance requirements. The v5 sidecar
pilot below has **not** performed this cutover, changed live source pixels,
integrated overlay repair, or retargeted workflows.

### Experimental preparation comparisons (sandbox only)

This is a separate read-only-source pilot, not a change to `library.cmd` or
permission to replace Gallery photos. It includes retained Angel/Sister cores
without reassigning them. From the repo terminal:

```bat
bin\prepare-images.cmd --root "B:\Sovereign Territories Sandbox\Working" --out "B:\Sovereign Territories Sandbox\Working\_reports\preparation\YOUR-NEW-RUN" --limit 28 --dry-run
```

Use the same command with `--apply` instead of `--dry-run` to save exact input
bytes and separate control/geometry/denoise/tone comparison files; `--check` verifies
source and artifact hashes without writes. Default limit is 28; `--limit 0`
explicitly processes all active Gallery/Review sources into sidecars. Sampling
round-robins categories/identity folders, preferring screenshot-named photos.
It is not a labelled representative dataset or automatic quality selection.

For only the new unsorted test images, add `--source-folder "Various\gallery"
--limit 0` to the same launcher with a new run directory. This reads all supported
images directly in that folder, not Review, other identities or subfolders.
It leaves the incoming files in place. The report explains every role and
links the **original or provisional border/panel geometry candidate as a conservative
recommendation**, with its reason. This is not a measured enhancement winner
or semantic hair-safety guarantee. A missed screenshot heuristic does not
mean clean. Control means oriented/sRGB only; geometry is prepared before
denoise and tone, which are separate experiments. Padded examples are downstream
canvas fitting, not another enhancement.

Recipe v5 introduced non-mutating geometry planning: contiguous, full-span
near-solid black/white external strips qualify (channel range <=10, black <=20
or white >=235, at least five pixels, no more than 20% of the dimension).
It retains a two-pixel guard at the boundary. Broad flat backgrounds, thin
strips and content interrupted by text are left alone. This deliberately misses
many real screenshot bars rather than interpreting dark hair as removable UI.
Coordinates and unchanged reasons appear on each page and in the manifest.

**Recipe v6 adds the per-image processing trace.** Each photo starts with three
views: original, recommended after crop/eraser, and final recommended source
for 944x1104 generation. The table records input, attempt output, kept selection,
status and reason for first crop, eraser, second crop, denoise and tone.
Statuses are skipped, attempted-selected, attempted-rejected or failed.
Skipped steps do not invent result images. Readable but unassessed/unsupported
operations are not labelled clean. All decisions are provisional for user tuning.

**Face eligibility precedes transformations:** use the existing local YuNet
model, shared human-face row filtering and .7/.5 detector retry, without
recognition, cache writes or downloads. No detected human face, or the largest
face's minimum dimension below 60 pixels (the current library/derivative
threshold), produces a report-only `junk-candidate`: retain exact bytes,
show the original, skip every crop/eraser/enhancement and padded candidate,
and recommend no source for generation. Default comparison `--apply` remains
sidecar-only. The separately requested disposition below can now route eligible
loose incoming Junk automatically without a per-photo approval.
Missing/broken detector is `assessment-failed`, not Junk or a clean success;
it skips transforms and exits nonzero. Unreadable inputs are separate errors.
This is not the complete legacy Junk rule: overlays alone are not grounds
for rejection, multi-face classification is not changed here, and missed
human detections remain possible. Tiny faces may be useful for other purposes;
the report exposes the measured size rather than deleting them.

**Recipe v7 records original matching scope.** Artists use the same detector,
cleanup trials, enhancements and 944x1104 padding as all other categories.
`Artists/<artist>/gallery` retains `Artists/<artist>` scope; nested artist person
folders retain that same original artist, never the general pool or another
artist. Artist intake without a known owner is labelled `Artists-unassigned`,
not silently general. Copies deliberately placed in `Various/gallery` may stay
there for these nonmatching tests, but their artist ownership is unknown.
For actual artist intake, use the owning artist's gallery. No pilot version
assigns identities; the existing artist-scoped grouping remains separate.

**Animals:** the early test asks whether there is a usable human-face candidate,
not whether an animal is present. Animal-only/no-human-face photos skip all
transforms and become Junk candidates. A usable human with an animal is not
automatically Junk. Shared `human_rows` confidence filtering can suppress weak
secondary detections, but is **not a species classifier**; missed humans and
animal false detections remain possible. Do not claim universal animal
recognition or crop around an animal as though it proved a human subject.
Use the report and manual Junk action to correct detector mistakes.

### Early Junk disposition (explicit sandbox opt-in)

After generating and checking a comparison report, use the same launcher:

```bat
bin\prepare-images.cmd --root "B:\Sovereign Territories Sandbox\Working" --out "B:\Sovereign Territories Sandbox\Working\_reports\preparation\YOUR-RUN" --quarantine-junk --dry-run
```

Review that batch preview once; `--quarantine-junk --apply` automatically routes
the eligible candidates without individual prompts. It verifies exact current
source hashes, creates a verified scoped `_backup` snapshot, and records
`junk-disposition.json` before moves. Sources go below `_junk/<original-path>`;
artist provenance, names and exact bytes/mtime are retained. No deletion,
matching, catalogue edits or derivative generation occurs. Repeating a completed
disposition verifies without rewriting. `--check` also verifies its journal,
recovery snapshot and moved bytes while keeping the immutable report intact.

Only unregistered loose `Various/gallery` and `Artists/<artist>/gallery` sources
qualify for this path. Registered identity folders, photos with catalogue
decisions/anchors, cast and selected-workflow sources are held explicitly for
the guarded staged-action route; held rows exit nonzero. Detector errors,
unreadable inputs, overlays alone and human-plus-animal content are not automatic
Junk reasons. Stale files, destination collisions and linked/escaping paths
fail without overwriting. The immutable report sets the scope; disposition
flags cannot be combined with new `--source-folder`/`--limit` selections.

`--undo-junk` previews recovery; `--undo-junk --apply` returns exact retained
files to their original incoming locations, after checking backup integrity,
collisions and new ownership/reference guards. This is deliberate mistake
recovery, not ordinary retry. Interrupted/failed journals block further automatic
work; inspect their move map and verified snapshot before recovery. A caught
mid-batch error rolls completed moves back; an incomplete status never reports
success. No production route or live preparation/crop cutover is enabled here.

### Guarded crop and repair candidates

For usable reel screenshots, v6 tests black external-panel transitions with
local face-margin guards rather than applying one fixed rectangle. The recipe
records thresholds and model hash. It is still narrow black-panel detection,
not general app-layout, hair or body segmentation. First-crop geometry may be
provisionally selected; unflagged/unsupported layouts retain content with reasons.

The eraser is a **rejected-for-automatic-use trial**, not a shipped magic eraser.
Since v8 the old right-only search includes bounded white strokes at all
edges, magenta lower-corner emblem envelopes, and neutral top-bubble envelopes
on detected reel screenshots. Corner trials do not require a reel flag.
Expanded face/hair regions exclude generic strokes and corner trials.
In v10, complete detected neutral bubbles may override the hair margin only
when they do not intersect the detected face box plus 2% (minimum 2px).
A face-intersecting bubble is refused whole, not partially repaired.
The trace records excluded pixels, complete-shape attempts/refusals and final
mask coverage. The local Telea radius-3 mask and result are both shown,
never automatically accepted. These heuristics are not
general text/logo detection. They can affect real clothing/background detail,
leave artifacts or invent incorrect fill; they do not restore hair under
large top overlays. Complete bubble removal can leave a conspicuous streaked
hair cap; protecting hair can instead leave the bubble untouched.
Filling a logo can replace fabric/marble with conspicuous smearing.
After a rejected eraser, one mask-directed left/right/bottom crop can be shown
from the last selected input if expanded head margins fit and area loss is at
most 30%. Mask removal per area lost only prioritizes a comparison; it is not
a quality score. The candidate remains rejected because
arms/body/outfit loss is unverified. No repeated eraser/crop search or automatic
repair/body-aware crop acceptance is implemented.
v13 also compares a top cut at a detected outlined oval's actual lower edge
plus a small guard on reel screenshots. It requires face evidence, clearance
above every expanded head margin and at most 30% area loss. A banner across
hair cannot be declared safe to crop just because the face would fit.
The top trial remains rejected automatically; when refused, reasons say
whether the top banner remains unresolved even if another edge crop is shown.

v11 also shows **eraser-ns**, Navier-Stokes radius 3, alongside the Telea
eraser on the exact same selected input and mask. Its separate manifest
comparison records method, input, mask, result and reason. It cannot change
the five-step selection chain or feed downstream crops/filters. Failures are
explicit and do not discard the other comparisons. Both local methods smear
the inspected hair/fabric/marble regions and remain automatically rejected.
v12 supplements neutral-fill detection with bounded closed rounded-outline
hypotheses on reel screenshots, so some translucent/colored top banners now
receive complete masks too. Overlapping hypotheses merge before face refusal
and reconstruction. The observed `204050` banner is now removed in the trial,
but stretched replacement architecture remains unacceptable; no new automatic
repair selection follows from this additional coverage.

The v8 source-preserving UAT run is
`_reports/preparation/visual-uat-20261023-v8/index.html`; earlier reports are
immutable and remain separately verifiable. It retains about 1.99 GB of
comparison evidence, not just regenerable viewer thumbnails. A graphic-free
crop can still be rejected because of outfit/body/context loss; the current
recommendation is a conservative preserved source, not an objective visual
quality winner. The [intake plan](../plans/2026-10-23-image-intake-preparation.md#v8-result-and-direct-visual-acceptance-boundary)
records inspected examples and next benchmark/reconstruction/crop work.
The bounded v9/v10 replay uses 12 exact retained inputs at
`B:\ST-v9\Sovereign Territories Sandbox\Working\_reports\preparation\`;
the two reports add about 363 MB. v10 attempts complete bubbles across hair,
but inspected fills are not accepted. The same plan records the remaining
translucent-bubble, mask-quality, reconstruction and purpose-specific crop gaps.
The `v11/index.html` replay in that same directory adds the identical-mask
Telea/Navier-Stokes comparison (about 206 MB retained evidence).
The `v12/index.html` replay adds the outlined-banner correction (another
206 MB); immutable earlier comparisons are not overwritten.

Denoise/tone consume the selected cleanup image, never a rejected eraser or
second crop. Both are rendered for review but not automatically accepted:
there is no calibrated benefit/detail-preservation test yet. A filter failure
retains the last safe cleanup selection rather than reverting a good crop.

From v14 a pure overlay crop can become the cleanup. From v16
(`preparation-comparison-v16`, `tools\art\intake_library\`) the order is
**first crop → second crop → eraser → composition → enhancement comparisons**:

- **Second crop** trims each side past its edge clutter (icons, the search
  bubble, app bars, corner logos) only as far as a Mask R-CNN person mask
  allows (at most 0.5% of the person lost). A screen-wide app bar may cut the
  legs well below the face.
- **Eraser**: LaMa repaints the clutter the crop could not reach, on the
  second-crop output, and the result is selected. Faces, cards lying on the
  body and fills over a fifth of the picture are never repainted.
- **Composition** frames the whole person with a small margin, widened
  toward 944x1104. When the mask stops mid-leg, the bottom is kept.

The two models download once, with pinned hashes, into
`%LOCALAPPDATA%\sovereign-territories\models` (about 400 MB; `torch` and
`torchvision` must be installed; CPU is enough, about 20 s per photo).
Older reports (v5–v15) still verify through `intake_library\legacy.py`.
Results, decisions and known gaps are in the intake plan (v16 section).

For detected reel screenshots, `ui-crop-proposal` also shows the existing
`screens.clean_box` rectangle. It is **comparison only**, never recommended or
fed to enhancement: a fixed rectangle may cut hair/body. The selected cleanup
is the enhancement input. Cropping removes pixels; it does not reconstruct
overlaid hair. Unresolved graphics still pass
through with a reason for later ComfyUI cleanup, without a manual-intervention
requirement. Face-guided background/other-subject cropping is not part of this pilot.

Open `index.html` in that run directory. Click a candidate for the larger
per-photo page: retained input, control/candidates, then their padded 944x1104
examples. Candidates never replace Gallery sources or the maintained derivatives.
All crops/eraser attempts are sidecars. No accepted reconstruction, matching,
cache update, action settlement, model download or ComfyUI change occurs. Denoise/tone can make a
clean image worse; neither is accepted automatically. Native geometry is separate
from downstream padding/resizing; there is no detail-recovering superresolution.

`originals/` retains exact **current** input bytes before decoding; these may
already be cropped. SHA-256 and filename-derived stable photo ID are recorded
in `manifest.json` against the versioned recipe. No raw provenance is invented.
The overlay heuristic is informational: retain the original, show
`original-overlay-unremoved`, and do not block processing or require manual
approval solely for an overlay. ComfyUI can clean it later. Filter failures
show `original-enhancement-failed`, retaining original/control without blocking.
`original-unassessed` is not a claim that a photo is clean. Automatic clean/
enhanced selection and normal people-gallery attributes are still integration
work; these treatment labels currently appear in new pilot comparisons.
Border/panel recommendations use `cropped-border` or
`cropped-border-overlay-unremoved`; these describe the candidate, not a change
to the live Gallery file. In v6 an enhancement failure retains the selected
cleanup source (original or crop); `original-enhancement-failed` remains a
compatibility diagnostic, not proof the cleanup selection is the original.
Pixel-change scores are unavailable when candidate dimensions differ from
control; they are not image-quality or likeness-confidence scores.
Decode/unsupported cases retain bytes, report errors and exit nonzero.
Repeat apply verifies and reuses the same run without rewriting; changed inputs,
recipe, inventory, selection or edited artifacts require a new run directory.
Completed reports publish atomically; a failed run leaves gallery bytes intact.
Keep run copies until accepted recovery is arranged: they are not independent
backups or the final immutable raw archive. Historical uncropped-source recovery
is deferred. See the [intake plan](../plans/2026-10-23-image-intake-preparation.md)
for publication/no-op/fallback gates and [layout L12](../plans/2026-10-22-gallery-review-layout.md)
for later people-page integration.

**Ingest runbook (new photos): three commands.**

1. Drop the new photos into `Various\gallery` (any name; a photo that came from an artist and is dropped again goes back to that artist by its id, see below). Photos you know are all one person go into `Various\<Name>\gallery` instead; `likeness seed` (step 0 below) files them under that name without face matching.
2. `bin\library-preview.cmd` shows what would happen, step by step, and moves nothing. Optional.
3. `bin\library.cmd` does it. Read the summary at the end; the log is `<work>\_reports\runs\library_sync_<time>.log`.

The preview runs each step independently against the current folders; it does not simulate the earlier steps' proposed moves. A file may therefore appear in more than one step's preview even though the real run moves it in sequence. Treat preview counts as current-state counts and use the completed run log for final results.

Then look at where everything landed: `bin\people-gallery.cmd --apply` maintains
folder-prefixed original names and standard derivatives, then builds both
`<work>\_reports\library\people_gallery.html` and
`people_gallery_review.html` with the shared thumbnail cache beside them. The overview and filtered review use the same
identity sort modes and first-nine order, plus shared Chest-up and Head
thumbnail files. Prime-start suitability remains a photo-quality score,
not identity confidence. Sisters and Angels
are alphabetical, while Prospects and Potentials are ordered by usable
gallery-photo count, largest first. Click a thumbnail to open its source, or
the person name to open the complete review gallery filtered to that person.
The separate history link opens the person's `z_` file. Angel cards show their paired Sister,
current canonical hair color and three eligible Prospect alternatives ranked by pairing fit. The full all-candidate
rankings for every paired Angel are in `<work>\_reports\comparisons\pairings\angel-prospect-candidates.md`.
Chosen Angels and Sisters that came through Prospect processing also show their recorded Prospect identity beside
the chosen-photo status.
For high-volume maintenance, run `bin\people-gallery-review.cmd` when only
the review page needs refreshing. That page includes every Gallery and
Review photo, core-similarity ordering, identity/protection state, filters and
content-cached lazy-loaded thumbnails. Per-photo controls stage anchor,
protection, Review, Reject-to-Various, Review approval, recoverable retirement
or unwanted/unusable Junk; use the
downloaded manifest with `bin\likeness-actions.cmd validate FILE.json` or
`preview FILE.json` to check it against the current library. After reviewing
the preview, `bin\likeness-actions.cmd apply FILE.json --apply` makes a
verified backup before moving photos or updating the catalogue.
`bin\likeness-actions.cmd undo [BATCH_ID]` is preview-only;
`bin\likeness-actions.cmd undo [BATCH_ID] --apply` backs up and reverses the
newest active batch only if the recorded files and metadata are unchanged.
Manual `photo-junked` and `photo-retired` are distinct typed actions. Junk
retains the file at `_junk/<person-folder>/<source-bucket>` and stays out of
routine processing. Retirement retains it at
`_retired/photos/<person-folder>/<source-bucket>` for deliberate later return.
Both preserve photo ID, exact bytes and history, enforce protection/anchor/
chosen-workflow and stale/collision checks, and use backed-up action undo;
neither deletes a photo or retires its whole identity.
Artists and Various support retirement and Junk without cross-root reassignment. CLI manifests
may omit `personId` for unregistered folders but still require an unambiguous
filename-derived photo ID, source folder/bucket and exact SHA256. No identity
is invented. Artists must actually be included in a review report to expose
their action controls; loose Various Gallery intake is not currently a browser
action surface. Use a CLI staged manifest when its ID is supported, or the
early no-face quarantine above for loose incoming IDs that cannot be indexed.
Use the bounded [post-action refresh](#post-action-gallery-maintenance-no-matching)
afterward; do not run global ingest/matching merely to refresh pictures. Folders
outside the catalogue's supported roots are view-only.
The Angel card prints a preview command for the top candidate; browser pages cannot safely launch filesystem
promotion commands, so run it in a terminal and review it before adding `--apply`. The Prime-start photo score describes
photo suitability, not identity confidence. Prospect cards also show the closest face-embedding matches among
sisters and readiness evidence (usable faces, full-length framing, face size, review and unusable-photo counts).
Those similarity values are candidates to inspect, not verified identities; framing counts do not measure pose
variety. `<work>\_reports\library\crop_review.html` shows every cropped photo beside
its uncropped original, and `<work>\_reports\library\crosscheck.md` who looks like whom across the lines that are kept
apart; `bin\likeness.cmd names` and `index` list the people. Run it again whenever you like: it repeats safely,
nothing is deleted, and a second run on a finished library changes nothing.
Ordinary library runs keep Junk out: they no longer call `junk --recheck`.
The later active-photo Junk test stays as a backstop for paths that did not
run early preparation. Explicit `bin\library.cmd --retry-junk` retries only
legacy flat per-category buckets (prospects to `Various`, artists back to their
recorded artist); nested preparation/manual-action Junk is not swept into that
retry. Use the owning disposition/action undo for a deliberate mistake recovery.
Junk means unwanted/unusable, not a queue for routine repair/resubmission.
Photo retirement is a separate recoverable `_retired/photos` state for images
you might bring back; neither operation requests permanent deletion.
`bin\library-check.cmd` is read only and says whether anything is waiting (exit 1 when it is).

### Report folders

`<work>\_reports` is grouped by purpose. The library routine keeps its current reports in `library`,
dated run logs in `runs`, Angel/Sister/Prospect likeness work in `comparisons\pairings`, historical
comparison material in `comparisons\history`, comparison sheets in `comparisons\images`, Prime sheets
in `comparisons\primes`, and move plans in `analysis`. Routine commands overwrite their current reports;
dated logs are retained. Old reports have been moved into these folders without deleting them.

**Backups before a real run.** `bin\library.cmd` creates a dated snapshot before changing files; if backup
fails, the routine stops before processing. The snapshot is written under `_backup\library-<timestamp>` and
contains the work root except `_archive` and older `_backup` snapshots, the configured ComfyUI inputs, and
`workflows\workspaces.json`. Its `manifest.json` lists each copied file with size and SHA-256; every run verifies
the copied file list, sizes and hashes before proceeding. ComfyUI output
renders are not included because the library routine does not modify them. To make a snapshot on demand,
`bin\library-backup.cmd` previews by default; add `--apply` to create it, or `--verify <snapshot>` to recheck one.
Routine/action backups omit only proven regenerable managed derivatives.
For a complete monthly snapshot that also stores generated derivatives, use
`bin\library-backup.cmd --full --apply`.
A failed copy is marked `INCOMPLETE.txt` and is not a usable snapshot.
On Windows, snapshot copy and verification use extended-length paths so
retained nested sandbox state can be backed up even when Windows long-path
support is disabled. This does not exclude old run evidence or weaken hash
verification; a failed snapshot remains incomplete and is never reused.
Standalone fixed-slot Angel/Sister recorded-name changes are narrower:
their action executor snapshots only the catalogue/history write set and
records the identity inventory hash, without copying unchanged images.
These transaction snapshots are verified by the same launcher but are not
eligible as full-library recovery baselines. Other actions retain full backup.
See [whole-person rename](likeness.md#whole-person-rename) for the boundary.

### Post-action gallery maintenance (no matching)

`bin\people-gallery.cmd` now previews housekeeping by default; it no longer
silently means report-only. `--dry-run` previews explicitly, `--check` is
read-only (exit 1 for pending upkeep or unresolved diagnostics), and `--apply`
creates a verified full snapshot before changing originals or derivatives.
Apply then refreshes both viewers. `--no-reports` limits apply to local files.
Use `bin\people-gallery-review.cmd` for a report-only review refresh.

For an isolated library, supply its root and cache explicitly. A sandbox
Working cache and report output must stay inside Working:

```powershell
$root = "B:\Sovereign Territories Sandbox\Working"
$scenario = "$root\_sandbox-state\unified-rebase-20261022-01"
cmd /c bin\people-gallery.cmd --root "$root" --cache "$scenario\likeness-cache.json" --policy "$scenario\policy.json" --dry-run
cmd /c bin\people-gallery.cmd --root "$root" --cache "$scenario\likeness-cache.json" --policy "$scenario\policy.json" --apply
cmd /c bin\people-gallery.cmd --root "$root" --cache "$scenario\likeness-cache.json" --policy "$scenario\policy.json" --check
```

Use the saved scenario's existing cache and policy, not a new empty cache or
the repository policy. These are command examples, not production permission.
While an action undo is pending, safely preview the bounded alternative:

```powershell
cmd /c bin\people-gallery.cmd --root "$root" --cache "$scenario\likeness-cache.json" --policy "$scenario\policy.json" --preserve-action-undo --dry-run
```

Only after separate approval, replacing `--dry-run` with `--apply` maintains
unaffected folders while leaving every active action's identity inventory
entirely untouched: no original renames, new derivatives, pruning or manifest
writes inside those identities. It does **not** settle any batch. Missing
derivatives in held identities remain visible placeholders until the user
undoes or explicitly finalizes the action. Exit 1 reports these explicit
holds; it does not mean unaffected maintenance failed. Do not bypass the
inventory guard by excluding generated files or rewriting stored hashes.

The command does not invoke reconciliation, matching, retirement, promotion
or workflow-input synchronization. Fixed cast slots retain their folder
names; original prefixes follow those folders, not recorded personal names.
Image bytes and stable filename IDs are retained. Both Gallery and Review
are maintained, including artist people and Review-only identities.
Review derivatives have `review_` directory prefixes to avoid collisions.
When several originals propose the same normalized name, all colliding
originals retain their current names and receive derivatives under those
unchanged names. No file is overwritten or silently skipped. Preview names
every held collision; apply/check return 1 until the naming conflict is
resolved deliberately. This includes non-ID names such as `*_base.jpg`.
The maintained outputs are 944x1104 PNGs: padded full photo, head and chest.
Face boxes come from the supplied content-keyed cache, which housekeeping
does not write. Missing cached faces, insufficient head crops, unreadable
photos and screenshot UI conflicts are explicit diagnostics, not silent
fallback crops. Inspect/cache missing faces separately before rerunning.
Chest framing still needs visual acceptance. The user identifies 944x1104
derivatives as the intended ComfyUI inputs; chest selection/repoint/sync support
must be verified in upkeep U7 before it is offered as a supported choice.

**Action recovery gate.** Applied action batches keep their existing undo
inventory guards. If housekeeping would change files, active batches block
apply. Undo them first, or deliberately add `--settle-actions` to close
their action-undo windows after a verified full pre-maintenance snapshot.
The default gate and explicit settlement conservatively cover all active
batches, not just identities whose files appear to need normalization.
Use `--preserve-action-undo` for independent upkeep without closing any
undo window. The two flags are mutually exclusive.
This is an explicit finalization, not transparent undo through renaming:
the root's `.gallery-maintenance-settlements.json` records each closed batch
and its snapshot. Action undo refuses those batches with the recovery path;
it never rewrites hashes to pretend the inventory was unchanged.
To recover, use the exact pre-maintenance snapshot printed at settlement
(not the action's earlier scoped backup). The following first previews, then
materializes into a **new, nonexisting** recovery directory. It leaves the
normalized library untouched and reconstructs omitted derivatives exactly:

```powershell
$snapshot = "SNAPSHOT-PRINTED-BY-MAINTENANCE"
$recovery = "C:\LibraryRecovery\before-maintenance"
cmd /c bin\library-backup.cmd --restore "$snapshot" --destination "$recovery"
cmd /c bin\library-backup.cmd --restore "$snapshot" --destination "$recovery" --apply
cmd /c bin\likeness-actions.cmd undo BATCH_ID --root "$recovery\work-root"
```

Review that undo preview before adding `--apply` against the recovery
`work-root`. Sandbox snapshots already contain `.likeness-library.json`.
For a configured production snapshot whose catalogue was external, first copy
the preserved `likeness-catalogue\likeness-library.json` into the recovery
`work-root\.likeness-library.json`; never substitute today's catalogue.
Do not overlay selected files onto the live tree or delete only the
settlement marker. Publishing a recovered tree back to the live root is a
separate deliberate whole-tree replacement, not something this command does.
No automatic restore, live replacement or settlement is implicit.

Viewers resize only verified maintained derivatives. Their shared thumbnail
keys include the rendering recipe and derivative content; source hash,
face-box and output-hash mismatches invalidate them. Missing/stale/edited
derivatives display diagnostic placeholders, never independently recropped
originals. The review data includes exact derivative source URLs and hashes.
An existing derivative is adopted only when rerendering produces identical
PNG bytes; unknown or hand-edited assets are preserved with a diagnostic.
Only manifest-owned, unchanged orphan outputs are archived. Configured
workflow-selected names are retained, and no workflow choices are rewritten.

**Exact derivative omissions.** Full snapshots omit only exact manifest-owned
padded/head/chest filenames whose source hash, output hash, supported recipe
and a fresh in-memory rerender all agree byte-for-byte. Provenance, original
sources and all unknown, modified or unreproducible files remain copied.
No suffix-based `_944x1104` exclusion is used. Snapshot manifests record every
omission's original path, recipe, face box, source/output hashes, size and times.
Backup verification independently rerenders from the **copied snapshot**
original and refuses missing sources, unsupported recipes or changed bytes.
Restore verifies the copied snapshot again before regenerating into staging
and publishing a complete recovery tree. A changed renderer/Pillow version
that cannot reproduce exact PNG bytes fails safely, never silently substitutes
a different picture. Scoped transaction backups retain their existing behavior.

### Generated browser reports and backups

Routine backups can omit generated views only when their supported ownership
manifest lists the exact current file hash and expected managed pathname:

| Report | Ownership manifest | Generated payloads |
| --- | --- | --- |
| People | `_reports/library/people-gallery-manifest.json` | Supported overview/Review/rankings files and content-keyed thumbnails in `people_gallery_review_files` |
| Artists | `_reports/artists/gallery-manifest.json` | Separate overview/Review HTML and hash-named `thumbnails` JPEGs |

The renderer records only bytes it actually reproduced. Unknown, edited,
unmanifested or unexpected paths remain in backups. Old gallery reports do
not become disposable merely because they are under `_reports`. There is no
blanket report-tree exclusion: retained preparation originals/comparisons,
face caches, Gallery/Review originals and placement, catalogue/history and
ownership manifests remain recovery data. FULL and scoped transaction snapshots
retain generated browser payloads too.

After restoring a lean snapshot, regenerate omitted browser reports explicitly;
this is distinct from verified standard-derivative regeneration during restore.
Use `bin\artists-gallery.cmd --root "<restored-library>" --cache "<restored-cache>"`
to preview, then `--apply`/`--check`. For People, use the
[supported report/upkeep commands](likeness.md#quick-start) and preserve any
active action undo. Generating a report does not apply matching or intake.
Report generation prints managed thumbnail count/bytes. People overview/Review
share their cache; Artists use one 240x300 JPEG per distinct source, shared
between their two pages. No second full-resolution photo library is created.

The small shared banner at `_reports/_assets/gallery-banner.jpg` is not a
manifest-owned disposable thumbnail and remains in backups, including custom
replacements. See the [shared theme guide](likeness.md#shared-gallery-theme-and-banner)
for its source and replacement instructions.

**The short way: `bin\library.cmd`** runs, in order:

While the shared likeness policy is draft, a likeness-enabled real run refuses
before backup, renaming, cropping or other housekeeping. Preview and check
remain available. Do not approve production merely to bypass this gate:
sandbox acceptance and the separate clean-full production rebuild are still
required. Threshold changes belong in the versioned policy, not `--min`.

| Step | What | Where the originals of a change are kept |
| --- | --- | --- |
| 0 `likeness seed` | every `Various\<Name>\gallery` (and `review`) folder joins the person called `<Name>` without face matching: an existing person of that name, else a new Prospect (5+ photos) or Potential; an ambiguous name is held; photos rejected for that person stay | `z_<name>.txt` history; `likeness undo` |
| 1 `originals` | names every original after its folder, makes the scaled copy and headshot | old scaled copies: `_archive\<folder>\gallery_944x1104_org`; old headshots: `_archive\<folder>\headshot_944x1104_org` |
| 2 `duplicates` | the same picture twice (any folder, any name) | the extra copy: `_archive\<folder>\gallery_duplicates` |
| 3 `likeness crop` | cuts every photo down to the person: a phone's app bars, other people, animals and the background beside her; all the body in the picture stays | the uncropped photo: `_archive\<folder>\gallery_uncropped` (`likeness crop --undo` puts the last batch back) |
| 3 `likeness junk` | a photo that cannot feed a Prime (no usable face, a second person that cannot be cut away, bars over her head) goes to `_junk`. A prospect's or hero's photo that only needs clean-up goes to her `review` folder instead | `_junk\<side>`, her `review` |
| 4 `likeness reconcile` | shared incoming/Review proposal with frozen cores, tier permissions, preserved small groups and explicit holds; approved apply revalidates after a verified backup | `_reports\runs\reconcile_*.json`, full snapshot; `likeness reconcile --undo JOURNAL --apply` |
| 3 `likeness-artists crop`, `junk` | the same legacy crop and later Junk backstop, separately scoped to Artists; upstream preparation cutover remains pending | artist-local crop/move logs and retained uncropped originals |
| 5 `likeness-artists group --singles` | the artists' own galleries are emptied the same way, never across artists: into one of that artist's people, or a folder of their own. Only photos with no usable face, a second person or the app's bars stay | `likeness-artists undo` |
| 6 `likeness retire-empty` | prospect folders with no original photos in either `gallery` or `review` are moved intact to `_retired`; folders with review photos and the `Various` pool are left alone | `_retired` |
| 7 `duplicates`, `originals` again | the moves create new names; `originals --check` must say IN SYNC | |
| 8 `sync-inputs`, 9 `crosscheck`, `index` | workflow inputs; the look-alike report; the people index | |

**Prime partial-body frame flow retired (Oct 19).** See [Retired frame images](#retired-prime-partial-body-frames) for what changed and where the preserved files went. Maintained `chest_944x1104` viewer crops are separate from that retired flow; their visual acceptance remains open.

The former `review`/`sort`/`singles`/`rematch` decision chain is no longer run
automatically. Reconciliation now also proposes reciprocal whole-identity
merges, qualified red-outlier splits and ID-preserving category transitions;
see [established-identity maintenance](likeness.md#established-identity-maintenance)
for policy controls, recovery and the bounded read-only final-core check.
Those paths have synthetic apply/undo tests, not completed real-batch
acceptance or demonstrated global convergence. A journal
undo requires its recorded photos and catalogue to remain unchanged; after
subsequent renaming or user decisions, use the verified snapshot/reviewed
recovery path rather than forcing stale destinations.

**The rules the routine keeps.** An artist's photos never cross to another artist, even when two people look alike (that is only reported). Prospects and artists never mix (also only reported). Cast Gallery protection and incoming Review admission are separate; similarity never grants automatic cast Gallery membership. The `_origins.json` file in the work folder records which artist every photo came from (by its id, which survives a rename and a crop).

The routine now invokes general and artist likeness through separate entry
points. Source cleanup/Junk/grouping runs artist-only where appropriate;
general reconciliation cannot see artist sources or destinations. Shared
originals, duplicates, viewers and selected-input sync remain all-library
housekeeping, not a second engine. The artist index is `artists_index.csv`/`.md`,
separate from the general `people_index`; checks include an artist-only
usable-face scan. State, legacy undo and deliberate cross-boundary transfer
limits are defined once in the
[likeness entry-point contract](likeness.md#general-and-artist-entry-points).

**To start a part over.** `likeness pullback NAME ...` (or `--small 2`, or `--all`) sends prospect folders back to `Various`, and the routine sorts them again; a folder with a chosen photo is never pulled back. A looser second look at the pool: `likeness sort --assign 0.35` (preview first). The artists can be rebuilt from a flat backup of their folders: `bin\likeness-artists.cmd artists --from <backup>\Artists`.

**What `duplicates` does** (`bin\duplicates.cmd`, also step 2): the same picture can sit in two folders or twice in one under different ids (a download saved twice, a photo moved between prospects). It finds identical bytes in every `gallery` and `review` folder and keeps one copy.
The kept copy is a chosen photo first, then a gallery photo over a review photo, then Angels, Sisters, Prospects,
Artists, Various, then a name that already carries its folder's prefix. The others move to
`_archive\<their folder>\gallery_duplicates` (`originals` then prunes their scaled copies). A standalone
duplicate check only lists files with the same id but different bytes (a resaved copy); it does not move them.
During `library.cmd` ingest, when multiple incoming photos in `Various\gallery` share an ID but have different bytes, the file with the
uniquely newest last-modified timestamp stays in the gallery; the older incoming copies move to `Various\duplicates` with their names
preserved. That folder is outside the gallery/review buckets, so those photos wait for you to compare and sort manually rather than entering
likeness processing. If the newest timestamps tie, none of that ID's files are moved or used to replace an existing copy; the conflict is
reported for you to resolve. Once the incoming set has one unambiguous file, older matching gallery, review or `_junk` copies are moved to
`_archive\<their folder>\gallery_replaced`, and the incoming copy stays in the pool to be classified again. Byte-identical copies remain
ordinary duplicates. A changed file with a different ID cannot be recognized as a replacement automatically.

By hand, one step at a time:

1. Drop originals into a hero's `gallery`, or into `Various\gallery` and let `likeness sort --singles` file them (or move them from another hero's folder).
2. Delete the ones that did not work out (in `gallery`; the tool tidies the rest).
3. Run `bin\originals.cmd` (`bin\originals.cmd --dry-run` previews first; `--only Angelica` does one folder). `bin\originals.cmd --check` only asks: IN SYNC or OUT OF SYNC, exit 1. Run it after every move of files.
4. Choose the photo for a hero: `bin\inputs.cmd set Angelica --photo angelica_image_<id>_944x1104.png`, then `bin\inputs.cmd reset --hero Angelica`.

Not every photo has a headshot, by design: a headshot needs a face big enough to enlarge to 944x1104 without mush (a crop of at least 30% of the output height) and not hidden under a phone's app bars.

## What `originals` does

| Step | What |
| --- | --- |
| Rename | Every original is named after the **folder it is in**, so you can shuffle freely between angels, sisters, prospects and artists. The id in the name is kept; only the prefix changes (details below the table). If the new name is taken the file is left alone with a warning. |
| Scale | Each original is fitted inside 944x1104 (the shape is kept, EXIF rotation applied), centred on cream, saved as `<name>_944x1104.png`. A phone screenshot of Facebook (tall, with the app's light navigation bar along the bottom) is first cut down to the picture itself, without the bars, caption and icons (`tools/art/screens.py`), unless her head reaches into them. A copy already newer than its original is skipped (`--force` redoes all). |
| Headshots | Each original with a clear face also gets `headshot_944x1104\<name>_head_944x1104.png` (see Headshots). `--no-headshots` skips this step. |
| Prune | A scaled copy that no original in that folder makes any more is **moved to `_archive\<the folder's path>\gallery_944x1104_org`**, never deleted (a headshot goes to the matching `headshot_944x1104_org`), so the person folders stay free of old copies. `originals --archive-old --apply` moves the `_org` folders that were left in the library (with a manifest; `--undo-archive` reverses it). Other files in the scaled folder are left alone. |
| Re-point | With the work done, a chosen photo (`photos` in `workspaces.json`) that was renamed is found again by its id: `workspaces.json`, the generated workflows that load it (repo and workspaces; a changed workspace file is backed up first) and the workspace input folders are updated. The same step is available alone as `bin\inputs.cmd photos` (preview with `--dry-run`). |

### Retired: Prime partial-body frames

The Prime frame experiment was retired on Oct 19. `originals` does not generate
`frame_944x1104` images, and no Prime frame input flow is configured. The
previous library images and ComfyUI input copies were preserved in
`B:\Sovereign Territories\_archive\frame-retirement-20261019`; generated repo
workflows are under `workflows/_archive/frame-retirement-20261019`, while
installed workflow copies are in `workflows/.sync/backup/frame-retirement-20261019`.
Do not restore these as part of the standard library run. Partial-body photos
use the normal scaled photo as the Prime input. Maintained chest derivatives
now exist for viewers; visual acceptance and supported workflow selection
remain open. They are not the retired frames; see [prime-flows.md](prime-flows.md).

### Headshots

A headshot is the face of an original, found with the likeness tool's face detector (the same cache, so a photo is only looked at once), cropped to about 2.5 face heights around it in the standard 944x1104 shape and scaled up; it is never letterboxed. A photo with no face, a face under 60 px, or a crop too small to scale up without turning to mush gets none (the run reports how many were skipped). The whole library is about 0.9 GB.

To try one as a Prime input: `bin\inputs.cmd set Seraphine --photo seraphine_image_<id>_head_944x1104.png`, then `bin\inputs.cmd reset --hero Seraphine`. `inputs photos` leaves a chosen headshot alone; it never swaps it back for the full photo.

### How names are decided

The first rule that fits wins; `<n>` is the folder's name in lower case with underscores.

| The file is called | It becomes | Why |
| --- | --- | --- |
| `azaline_image_123.jpg`, `eva_emily_image_123.jpg`, `various_image_123.jpg`, `facebook_<time>_123.jpg` | `<n>_image_123.jpg` | the id (a Facebook id) is kept, the prefix is swapped |
| `Screenshot_<date>_<time>_Facebook.jpg`, `drakneta_screenshot_<date>_<time>.jpg` (any older spelling) | `<n>_shot_<yyyymmddhhmmss>.jpg` | the date and time are the id, written together with no `_`; the app name is dropped |
| `Draknara Base.jpg`, `Draknara Face left.jpg`, `Draknara Pose 2.jpg` | `<n>_base.jpg`, `<n>_face_left.jpg`, `<n>_pose_2.jpg` | the descriptor is kept |
| `<n>_anything.jpg` | unchanged | already right |
| `azaline_photo_wings.jpg` (another folder's prefix, no id) | `<n>_photo_wings.jpg` | the other folder's prefix is swapped |
| `images (3).jpeg`, `download.jpg`, any Google or web name | `<n>_pic_<8 hex>.jpg` | an id made from the picture's bytes: unique, and the same wherever you move it |

Three forms, then: `<n>_image_<facebook id>`, `<n>_shot_<yyyymmddhhmmss>` and `<n>_pic_<8 hex>`. Rename a folder (Pierre to `Awesome Fantasy`) and the next run renames everything in it, including descriptive names that still carry the old prefix (read from the ids in the folder's other files); move files out and they take the new folder's prefix, move them back and they take the first folder's again.

Two files with the same picture id in one folder (the same screenshot saved twice) are flagged as probable duplicates; delete one.

A chosen photo whose original is in another hero's folder, or is gone, is reported (`ELSEWHERE`, `MISSING`), never guessed. A hero whose photo is still a placeholder name is listed as `NO PHOTO`.

## Notes

- It needs Pillow (`pip install pillow`); WebP is read too.
- `rename_originals.py` and `rename_inputs.py` (a rename map for the old facebook/Screenshot names, sisters only) are superseded by this; nothing calls them.
- A scaled image becomes a workflow input only when you choose it (`inputs set`) or run `inputs photos`; `sync-inputs.cmd` and `inputs reset` also find images in the library.
- The old `scale_rename_prune_images.ps1` in the work folder now only forwards to `bin\originals.cmd`.
