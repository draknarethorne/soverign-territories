# Original photos: pick, rename, scale, prune

Current runbook for source photos, retained preparation, maintained derivatives,
backups and selected workflow inputs. Use the guarded commands, not manual
deletion or folder moves, when a photo has catalogue decisions or retained sets.

## Choose the right flow

| Need | Entry point | Current boundary |
| --- | --- | --- |
| Inspect crop/erase candidates without changing sources | `bin\prepare-images.cmd` | Sandbox sidecars; v20 recommended sequence, no identity assignment |
| Prepare immutable sandbox inputs, optionally stop, then match/install | `bin\sandbox-rebase.cmd` | Implemented retained-cast flow; real acceptance still pending |
| Maintain names/derivatives and refresh galleries without matching | `bin\people-gallery.cmd` | Preview/check/apply with backup and action-undo guards |
| Change one photo or a recorded name deliberately | `bin\likeness-actions.cmd` | Validate/preview first; supported actions use backed-up transactions |
| Ordinary incremental ingest | `bin\library.cmd` | Production writes paused by draft policy; upstream prepared-source cutover remains incomplete |

The [likeness guide](likeness.md#clean-sandbox-rebuild-versus-category-reclassification)
owns the exact clean-start stop/resume/install sequence. The
[long-run instructions](likeness.md#running-and-observing-a-long-rebase)
explain output capture, progress versus completion, checkpoint recovery and
the receipt checks needed before matching. The
[plans index](../plans/README.md#current-library-work-order-oct-23) owns acceptance
order. No command example below authorizes a production run.

## Python runtime and dependencies

Use regular **64-bit CPython 3.14**, not a free-threaded build, for local image
processing. The Oct 25 checked environment is Python **3.14.3** with NumPy 2.4.2,
Pillow 12.1.1, OpenCV headless 4.13.0.92, JSON Schema 4.26.0, CPU PyTorch 2.10.0
and torchvision 0.25.0. The launchers already use this runtime through `python`
on PATH; they fall back to `py -3` only if `python` is unavailable.

Intake preparation runs in parallel worker processes on the CPU: by default one
worker per 2.5 GB of free memory, up to 3 (each peaks near 1.7 GB), with the
cores split between them. Start a big run after closing ComfyUI to get all three,
or pass `--workers N` / set `ST_INTAKE_WORKERS`. Batches under 16 images stay
serial. Outputs are byte-identical to a serial run; measurements are in the
[intake performance plan](../plans/2026-10-28-intake-performance.md).

Full intake preparation checkpoints each completed image in a same-volume,
OS-locked recovery directory. Its fingerprint binds the ordered source paths
and hashes, recipe, configuration receipt and run scope. A checkpoint is
reused only when its complete row and every retained, detail and variant
artifact hash verify; incomplete image staging is rerendered. Worker-completion
progress is reported separately from ordered report publication. Recovery
keeps the verified report staging tree in place, removing each worker's
duplicate artifacts as its row is materialized. A partial row can be restored
from its worker checkpoint; data is removed only after the immutable report is
verified and published. Other owned temporary stages retain their own cleanup
and recovery rules.

[Core requirements](../../requirements.txt) pin the direct validator/gallery/
image dependencies. [Intake requirements](../../requirements-intake.txt) include
those plus the matched CPU Torch/torchvision wheels from PyTorch's official CPU
index. These are direct dependency pins, not a complete transitive lockfile.
Install only one OpenCV distribution: headless provides the `cv2` DNN/image
operations used here without desktop GUI dependencies.

To set up a **new, separate** repository environment (do not overwrite an
existing one), from the repository root:

```bat
py -3.14 -m venv .venv-processing
call .venv-processing\Scripts\activate.bat
python -m pip install -r requirements-intake.txt
python -m pip install pre-commit==4.6.1
python --version
bin\validate.cmd --quick
```

Core-only tools can install `requirements.txt` instead. Activate the environment
before running the normal `bin` launchers so those exact commands use it.
The existing `.venv` is not automatically selected or repaired. Never install
these requirements into ComfyUI's embedded Python or change its Torch/CUDA
stack: it is a separate application environment.

Python **3.12 remains the compatibility baseline**; no 3.14-only syntax/API is
required. The Windows CI matrix now checks 3.12/3.13/3.14 with the core
requirements and the launcher regression suite. Local full validation has run
on 3.14; adding the matrix is not a claim that its new remote jobs have passed.
The registered Store 3.13 interpreter was inaccessible during the local audit;
3.12 was not installed. Optional CPU Torch native operations are checked locally
on 3.14, not installed by every core-only CI job.

The declared requirements were installed/checked in a separate 3.14.3 validation
environment without altering the existing interpreter or `.venv`. That environment
inherited already installed core packages read-only and installed its own exact
CPU torchvision wheel; it was not a completely clean-room dependency build.
All 735 launcher tests and 19/19 quick mutation cases pass with deprecation
warnings enabled. Native checks confirm OpenCV's face APIs, CPU torchvision NMS
and no-download Mask R-CNN construction. Core Windows wheel resolution also
succeeds for 3.12 and 3.13; that is not execution testing on those runtimes.

The official [3.13 porting notes](https://docs.python.org/3.13/whatsnew/3.13.html#porting-to-python-3-13)
and [3.14 porting notes](https://docs.python.org/3.14/whatsnew/3.14.html#porting-to-python-3-14)
cover removed modules/APIs, deferred annotations and changed process defaults.
Keep those compatibility boundaries when adding optimizations. No Python 3.15,
free-threading, GPU migration or speedup is claimed by this setup change.
Use maintained stable 3.14 patch releases after validation; this audit did not
replace the machine-wide 3.14.3 installation.

## The library

Under the configured Production library folder (`paths.productionRoot` in
`workflows/workspaces.json`; do not assume a historical drive path):

```text
Angels\Angelica\gallery                  your originals for Angelica (jpg, png, webp, bmp)
Angels\Angelica\gallery_org\<set-key>     exact incoming bytes retained by prepared publication
Angels\Angelica\gallery_intake\<set-key>  checked retained alternatives, manifest and detail
Angels\Angelica\gallery_944x1104         made by the tool: every original on a light-grey 944x1104 canvas, as PNG
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

The general roots are Angels, Sisters, Models, Prospects, Potentials and Various.
Models is a distinct draft category, not an alias for Sisters. Artists is a
separate provenance/matching domain, with people below each artist. Various is
the unassigned intake/hold pool, not an identity. `paths.photoRoots` configures
housekeeping discovery; likeness entry points enforce their own domain boundary.

Storage roots and the reference ComfyUI workspace are configured in
`workflows/workspaces.json`, validated against
`workflows/workspaces.schema.json`; configuration edits validate and publish
through same-volume owner-locked staging. `paths.productionRoot`,
`paths.sandboxWorkingRoot`, and `paths.modelCacheRoot` can be overridden with
`SOVEREIGN_TERRITORIES_PRODUCTION_ROOT`,
`SOVEREIGN_TERRITORIES_SANDBOX_WORKING_ROOT`, and
`SOVEREIGN_TERRITORIES_MODEL_CACHE_ROOT`. ComfyUI paths also support
`SOVEREIGN_TERRITORIES_INSTALLS_ROOT`, `SOVEREIGN_TERRITORIES_INPUTS_ROOT`,
`SOVEREIGN_TERRITORIES_OUTPUT_ROOT`,
`SOVEREIGN_TERRITORIES_SHARED_INPUT_ROOT`, and
`SOVEREIGN_TERRITORIES_SHARED_OUTPUT_ROOT`. Storage directory names are mapped
by `storageRoots` beneath the selected library root; paths that escape it are
rejected. Defaults retain established names such as `_backup`, `_reports`,
`_generation`, `_likeness`, `_actions`, `_junk`, `_retired`,
`_sandbox-state`, and `_tmp`. Preparation reports, library-sync reports,
library snapshots, and migrated run staging resolve through these configured
roots. Keep the configured roots disjoint; do not repoint them while a run is
active.

## The routine

### Agreed end-to-end flow and current cutover boundary

The Oct 23 clarification separates **source preparation** from **derivative
framing**. The prepared sandbox clean-start implements stages 1-5 and gallery
refresh in stage 6. The table is not the installed incremental `library.cmd`
sequence and does not authorize workflow retargeting. The
[intake plan](../plans/2026-10-23-image-intake-preparation.md)
owns upstream preparation/crop cutover; the
[upkeep plan](../plans/2026-10-22-library-upkeep.md) owns downstream integration.

| Order | Role | Output / safeguard |
| --- | --- | --- |
| 1 | Retain exact incoming bytes before transformations | Immutable run input, then checked `gallery_org` publication alongside retained `gallery_intake` evidence |
| 2 | Prepare at native geometry | v23 overlay/border preflight -> guarded first crop -> eraser -> residual crop -> confirmed-pattern reconstruction -> guarded no-proposal composition -> denoise/tone comparisons; preserve subject, skip unsafe/unavailable stages with reasons |
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
sequence is retain original -> safe crops -> localized cleanup ->
final composition crop -> publish accepted native source -> padded derivatives.
Keep the visible person centered with breathing room, preserving head/hair,
torso, arms/hands and legs/feet in a full-body source. Do not force a fixed
aspect ratio or cut limbs to fill 944x1104; padding handles that canvas.
Centering follows the full visible subject, not only the face. Already-tight
inputs can skip either crop; retain wider useful context when subject bounds
are uncertain. Head/chest derivative framing is a separate later operation.

The FULL retained-preparation staging API publishes exact incoming bytes under
the destination owner's `gallery_org/<set-key>/original.ext`; the accepted
native image remains in `gallery` or `review`. New opt-in LEAN publications
reference that native file instead when the original bytes match exactly,
and share exact-equal native variant roles with it. Differing originals
still live in `gallery_org`. Its declared variants (including
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
- Direct legacy `originals` calls still use `fit`/`headshot` screenshot cleanup
  by default. Do not use that route to regenerate prepared photos.
- The prepared clean installer and maintained-derivative path already disable
  screenshot stripping for verified prepared natives; `likeness crop` skips
  those natives too. This does not complete the incremental `originals`/ingest
  cutover. Viewer framing inspection and selected-input integration still need
  U7 acceptance against the same prepared geometry.
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

These are intake I12 and upkeep U7 acceptance requirements. The current sandbox
prepared installer does not authorize the incremental/production cutover or
retarget workflows. Earlier sidecar reports are experiment evidence only.

### Experimental preparation comparisons (sandbox only)

This launcher reads sources without changing them and writes sidecar comparisons;
it is not a change to `library.cmd` or permission to replace Gallery photos.
It includes retained Angel/Sister cores
without reassigning them. The example uses the default reports root; use the
configured `storageRoots.reports` path if it has been changed. From the repo
terminal:

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
links the **provisionally selected cleanup/composition**, with its reason.
The v23 recipe below can select masked cleanup/reconstruction and a guarded
no-proposal composition; selection is not a measured enhancement winner or
hair-safety guarantee. A missed screenshot heuristic does not mean clean.
Control means oriented/sRGB only. Denoise and tone remain separate comparison
alternatives. In default FULL evidence, only the recommendation and denoise/tone
alternatives receive 944x1104 padding; masks and interim candidates remain native-sized.
Retained Gallery evidence supports this sparse padding and preserves the
separate padded-original record when the recommendation is the original.
Detailed evidence remains required while the flow is unsettled. Labeled
composites are review aids, not substitutes for exact originals, selected
inputs, masks or recovery lineage. Summary retention and production-intake
terminology are acceptance-gated follow-ups in performance T13/T14, not
permission to delete current reports.

#### LEAN evidence experiment (standalone reports)

For a **new bounded** comparison, add `--storage-mode lean` to the preparation
command above; start with `--limit 6 --dry-run`, then `--apply`. Use the same
mode for repeated apply. `--check` reads the saved mode from the manifest and
fully verifies sources/artifacts; it does not convert an existing report.
The menu's preparation preview offers `full` or `lean`. FULL remains the
compatibility default. Fresh `sandbox-rebase.cmd` runs also accept LEAN;
ordinary `library.cmd` has not changed defaults.

LEAN preserves original/control/recommended panel labels while aliasing
exact-byte roles within each photo to the same file, including previews.
Only the selected recommendation receives workflow padding. Denoise/tone
native alternatives and masks remain available, but unselected alternatives
do not have padded links. Use a separate FULL comparison when those padded
alternatives are needed; per-variant on-demand generation is not implemented.
LEAN does not skip processing or encoding, and is **not FAST**: processing
profiles remain a separately gated quality change. Different byte encodings
of apparently identical pixels remain distinct, including raw JPEG versus
normalized PNG. Sources and existing evidence are never pruned or rewritten.

The first six real installed-photo FULL/LEAN comparison retained identical
recommendations, native/preview hashes and recommended padding, with 62 to
46 image files and 61,128,917 to 42,901,872 image bytes. Twelve unselected
padded images and four exact original/control copies were avoided.
This is a bounded, already-prepared input sample, not a full-library savings
forecast or an installed LEAN migration. Complete evidence and the next
conditional-`gallery_org`/installed-native work live in
[storage S25/S26](../plans/2026-10-28-storage-operations-and-retention.md#oct-31-lean-producer-proof).

#### Installed LEAN, COMPACT and COLLAGE experiments

For a **new** rebase, append `--storage-mode lean` to the usual preview and
intake commands. Resume with that mode or omit the option to use the recorded
mode. A conflicting explicit mode refuses; nothing converts an applied run.
LEAN retained format 2 references its own installed native photo for all
exact-equal roles. It creates `gallery_org` only when source original bytes
differ. Renames, owner moves, undo and backup restore must carry that lineage;
another photo with identical bytes is not an allowed substitute.

New preparation manifests and index pages include recipe-derived outcome,
recommendation and step/status counts, distinct image files/bytes, image-role
references, worker count and current-invocation preparation wall time.
The timing stops before final publication/verification and is not end-to-end.
Image totals exclude manifests, HTML, mirrors, installed copies and backups.
Historical manifests without statistics remain valid.

Convert a verified FULL or LEAN report into a **new independent** history:

```cmd
bin\preparation-history.cmd --root "SANDBOX\Working" --report "REPORT" --out "Working\_reports\preparation-history\NEW" --mode compact --dry-run
bin\preparation-history.cmd --root "SANDBOX\Working" --report "REPORT" --out "Working\_reports\preparation-history\NEW" --mode compact --apply
bin\preparation-history.cmd --root "SANDBOX\Working" --out "Working\_reports\preparation-history\NEW" --check
```

Replace the example paths with absolute paths. Reports inside a verified
rebase input mirror are supported. COMPACT keeps downsized JPEG diagnostics
(640-pixel long edge); COLLAGE makes one labelled stage sheet per photo.
Both preserve exact original, selected native and selected padded payloads
once per photo, with provenance/role mappings. The layout is shallow, without
cross-photo or cross-artist pooling. Limits: 1-64 photos; oversized or linked
paths refuse. The source report is rechecked before atomic publication.
Repeat apply/check safely reuses the same verified conversion.

These are **lossy historical views**, not exact masks, alternative-stage
processing inputs or full rollback. FULL remains available. Conversion alone
is additive storage: it deletes no source report and reclaims zero bytes.
Do not prune a run needed by an installed receipt, undo, backup, history link
or production dependency. Existing `storage-retention.cmd` clearances apply
only to its supported superseded runs; generic report-to-bundle PRUNE is
not implemented. Selective FULL reproduction also requires the exact source,
recipe, model/config/runtime, and is not guaranteed by a collage.

For a real mixed end-to-end comparison, use a short ignored output path
(the long aligned-face filename must fit OpenCV's Windows path limit):

```cmd
bin\storage-experiment.cmd --root "B:\Sovereign Territories Sandbox\Working" --out "C:\Soverign-Territories\soverign-territories\tmp\s1" --limit 24 --dry-run
```

`--apply` copies the same balanced sample of Various and assigned Galleries
into isolated FULL/LEAN sandbox roots, then exercises preparation, real
matching, install/check, Gallery/Overview/Review/history publication, exact
backup/materialized restore and both history conversions. The supplied
library is read-only. `--check` verifies persisted bytes and native-reference
lineage. A failed incomplete output is retained for diagnosis and requires
a different short output, not silent continuation. Completed repeat apply
does not rerun preparation; it verifies the saved experiment.

The HTML/JSON summarize individual stage wall times, preparation counters,
active installed files/bytes, overlapping mirror/report/backup/restore scopes,
and history conversion/verification totals. Do not sum overlapping scopes.
FULL runs first; model/cache warming, simultaneous tests/ComfyUI load and
different volumes limit timing conclusions. No automatic FAST recipe, source
PRUNE, frozen-baseline migration or default adoption follows from a sample.
For a second changed-image cohort, `--sources LIST.json` accepts exactly
`--limit` relative active paths, balanced between Various and general assigned
Galleries, including at least three Angel and three Sister core candidates.
An immutable earlier input mirror can be the read-only `--root`; this
replays unprocessed originals instead of measuring only already-cleaned
installed recommendations. The source-list choice and every input SHA are
preserved through the resulting experiment receipt.

Current v23 checks known overlay patterns, borders, screenshot layout and
uncertain glyphs before cleanup. No detected proposal retains original pixels
as **unassessed**, still runs person detection, and can recommend a composition
only when the grown-subject mask-loss guard passes. A miss does not certify
clean pixels; hair and feet still need visual review. Pattern proposals are
reused; person-sensitive clutter
checks run with the mask/current crop when needed, and post-fill residual
detection remains. Confirmed patterns can still enter synthetic reconstruction
even off the person; the separate guarded/synthetic policies have not changed.
Published v22 and older reports retain their recorded pixels and contracts.
Measured results and the two-pass policy discussion live in the
[intake performance plan](../plans/2026-10-28-intake-performance.md).

#### Same-mask eraser A/B (comparison only)

`bin\eraser-compare.cmd` compares the **saved LaMa eraser** of an existing
preparation run with OpenCV Telea and Navier-Stokes inpainting (radius 3). Each
method fills the identical saved binary `eraser-mask` on the identical
pre-eraser input (the eraser step's traced input, never the final selection);
outside the mask the OpenCV outputs are byte-identical to that input, and this
is verified. List 1 to 64 exact report `source` strings in a JSON array, or
objects with `source` and an optional `sourceSha256` that must match the report
(no duplicates); every listed row is either compared or recorded as an explicit skip
(no saved eraser or mask), never silently dropped.

```bat
bin\eraser-compare.cmd --report "B:\Sovereign Territories Sandbox\Working\_reports\preparation\RUN" --sources "D:\path\sources.json" --out "B:\Sovereign Territories Sandbox\Working\_reports\eraser-compare\NEW-RUN" --dry-run
```

The root comes from the report's frozen manifest: either the sandbox `Working`
itself, or a clean-rebase intake mirror `Working\_sandbox-state\RUN\inputs` whose
`_reports\preparation\all` report is bound by that run's `intake.json` (manifest
hash, recipe and the complete source inventory); other roots are refused. `--out`
must be a new run directly in the real `Working\_reports\eraser-compare`, never
inside the intake run.
`--dry-run` (default) writes nothing; `--apply` stages and renames one immutable
run (native PNGs, padded 944x1104 displays, source/input/mask/baseline copies,
`sources.json`, `manifest.json`, `index.html`; the shared gallery banner is copied
once to `Working\_reports\_assets`) and repeating it only verifies;
`--check` re-verifies the selection, report binding, the selected report
artifacts, every output hash and the outside-mask rule, read-only, without
loading a model. Only the listed rows' artifacts are hashed, not the whole report.

Limits: no candidate is selected, recommended or assigned. Inside-mask pixel
change is not quality, and every fill is synthetic reconstruction, not recovery.
This is a post-crop reconstruction A/B, not an erase-first sequence; LaMa ran
at patch scale with a slightly dilated model mask but pasted only inside the
saved mask. Size or non-binary mask mismatches and any hash mismatch refuse the run.

#### Experimental erase-first sequence

The same launcher accepts `--sequence` with the same report, selection and
output-location arguments. Use a separate new run name; preview first, then
`--apply`, then `--check`. This does not alter v16 or any Gallery source.
Unlike the same-mask mode, apply uses the pinned local subject/LaMa models
and may download a missing model; preview/check never load models.

The experimental order is first crop, guarded localized erase, one residual
detection and subject-guarded crop, then framing. It does not use v16's
screenshot bottom-bar exception permitting large subject loss.
First crop is recomputed from the original, not reused from saved geometry.
For detected screenshots, paired picture/black-panel transitions at both outer
side strips, with coloured-content evidence, can identify the picture rectangle.
The first crop removes external UI panels while extending above the picture
to retain the **complete pill** for reconstruction. The later composition
removes that temporary extension. Face boxes remain protected. Person-mask
predictions outside the observed picture rectangle are excluded from this
panel-only crop budget; this is not the old below-hips app-bar exception.
Unpaired/ambiguous screenshots fall back to full-span solid borders. The
older face-margin panel heuristic remains a proposal, not selection evidence.
Residual clutter is evidence, not permission for an unbounded erase loop. Existing
heuristic overlay masks are not manually verified text/logo masks; face/body
and coverage refusals remain visible. Successful processing is not visual
acceptance, and a residual detection miss does not establish a clean photo.
Subject-box composition proposals are comparison-only: zero calculated mask loss cannot
prove that hair, shoes or other missed subject pixels are retained. The
ordinary experimental final keeps the pre-composition image and uses padding instead.
Every row retains original/saved-v16 views, native experimental candidates,
padded previews and its ordered trace. The manifest binds the frozen report,
selection, policy/model versions and output hashes. Failed publication leaves
no partial run; repeated apply verifies instead of rerendering.

For an explicitly requested head-overlapping search pill, add `--head-overlay`
to `--sequence` and use a separate output run. This automatically proposes the
complete detected pill and nearby outlined-icon masks without clipping them
at the face. New runs use the cleaned-input synthetic review branch: guarded
crop/cleanup first, then reconstruction on that actual final, retaining prior
cleanup and source coordinates. Successful reconstruction becomes the explicit
**recommendation for visual review only**, never original/core likeness evidence,
and may invent eyes/hair. The guarded fallback remains recorded. Cumulative
source-coordinate masks and outside-mask RGB preservation are recorded and
checked. Overlay proposals come from the pattern profiles in
`tools/art/intake_library/overlay_profiles.json`, read by `overlays.py`, on
every eligible image (not only when a pill is found):

| Pattern | Kind | Detection | Result |
| --- | --- | --- | --- |
| `phone-reel` frame | screenshot | Portrait (aspect >= 1.9); nav bar/comment panel/UP NEXT card rows anchor the bottom; a black top panel makes it `boxed`, otherwise `full-bleed` with a status band. A `boxed` picture ends where the black under it starts (caption lines on that black are cropped, not erased) | First crop to the picture box (the complete pill is kept); zone parts fill status glyphs, pill and its companions, top icons, rail, stickers, sliders, caption lines and avatar |
| `corner-text` watermark | any image | Short white text line in a corner (e.g. "Dola AI"), at least 0.7% of the height: thin bright strokes over their surroundings, at least 3 separate letters on one baseline, not touching the image edge. Two or more stacked, centred lines grow into a caption block with the title line above them | Filled box per line or per caption block |
| `corner-sparkle` | any image | Pale four-point star near the bottom-right corner: square box, tips touching the box mid-sides, empty box corners | Filled box |
| `letterbox` | non-reel images | Flat dark bars above/below the picture (blurred fill) that end at one sharp full-width edge, 2-20% of the height each; never across a face | Joins the first crop |
| `tilted-sticker` | any image | Rotated (8-82 degrees) flat pale card with dark lettering and straight contrast edges along its length, e.g. a music or date sticker; an end is extended over an album thumbnail when both long edges run on into it | Filled rotated polygon, not a box |
| `viewer-corner-icons` | any image | A photo viewer's pure-white close "X" (both diagonals, no arms on the sides) and a row of three evenly spaced "..." dots in the top 10%, within 20% of a side | Filled box per icon |
| reference logos | any image | Stored crops in `tools/art/intake_library/overlay_references/` (one per known logo, listed under `references` in the profile), matched at 0.6-1.6x relative size on a colour feature (`gold` or `white`), then confirmed by edge correlation at the same spot; first entry: `echoes-of-fantasia` | Filled box |
| `gmw` badge | any image | Closed magenta ring with silver lettering inside (ring coverage, isolation, letter band) | Filled disc slightly larger than the ring; colour-blob "logos" are never erased |

A new layout or mark is added as data in the profile file; only a new kind of
measurement needs code. A new logo is added by saving a tight crop of it into
`overlay_references/` and a `references` entry (feature, `shortSide` of the
source, threshold); check it against the 100-image sample for false hits
first. A miss is not proof of clean pixels. Face-overlapping
proposals other than the pill are refused, except a face whose centre lies
inside a pattern part (the reel's own avatar thumbnail); avatar faces on the
reel's UI panel also do not block the first crop. The reconstruction branch may fill
up to 30% of the picture (pattern-confirmed UI such as a rail column); the
guarded eraser keeps its 20% cap. Fills may alter a handbag or background
beneath UI.
The picture-boundary composition **is selected after reconstruction**, then
feeds all enhancements; full-bleed reels also drop the status band when the
person mask starts below it. Subject-mask-only framing remains comparison-only;
it cannot prove complete hair/feet preservation. No proposal
means a visible skip, not permission to erase arbitrary parts of a head.
Nearby-icon detection is a constrained shape/brightness heuristic, not
proof that a highlight is UI. Review both masks and results.
Earlier immutable runs retain their independent, unselected head trial and
original page layout; `--check` continues to verify those without rewriting.
Use a new output directory for the revised branch.

Add `--enhancements` to `--sequence` for independent native denoise, tone and
restrained unsharp-mask comparisons on the current review recommendation
(the selected reconstructed composition when available, otherwise the actual
selected reconstruction or guarded fallback).
Every candidate starts from the same input;
no repeated filter chain. Luminance/extreme-pixel fractions and Laplacian
variance are diagnostics, not calibrated blur/noise/exposure classifications
or quality scores. The recommendation retains the unenhanced prepared input.
Ineligible face assessments skip enhancements explicitly.
New pages show original, historical v16 baseline and current recommendation
as the first three panels. All stages carry visible status/border markings
and input/consumer labels; masks and rejected crops are not recommendations.

`bin\overlay-review.cmd` accepts the same `--report`, `--sources`, `--out`
and preview/apply/check arguments, but publishes reference proposals only.
It searches pill shapes and magenta badge-like regions, including positions
outside the old lower-corner heuristic. It does not erase, train a matcher,
confirm a GMW logo or label a person. Candidate crops, binary masks and source
coordinates/hashes remain **unconfirmed** until reviewed. Pink clothing and
similar shapes are expected hard negatives; confirm by source and candidate
ID in chat. At most eight candidates per row are shown with explicit truncation
warnings. Source bytes remain untouched, repeat apply verifies, and check
refuses missing/extra/tampered files or an attempted automatic confirmation.

#### Earlier sidecar recipes (v5-v13), not current selection rules

The following explains old immutable reports only. The v16 order and
selection rules follow this historical section; they supersede the older
automatic-rejection statements, not the retained old evidence.

Recipe v5 introduced non-mutating geometry planning: contiguous, full-span
near-solid black/white external strips qualify (channel range <=10, black <=20
or white >=235, at least five pixels, no more than 20% of the dimension).
It retains a two-pixel guard at the boundary. Broad flat backgrounds, thin
strips and content interrupted by text are left alone. This deliberately misses
many real screenshot bars rather than interpreting dark hair as removable UI.
Coordinates and unchanged reasons appear on each page and in the manifest.

**Recipe v6 introduced the per-image processing trace.** Each photo starts with three
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

In v8-v13 the eraser was a **rejected-for-automatic-use trial**.
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

The historical v8 source-preserving UAT run is
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

#### Current v20 recipe and comparison behavior

The current recipe is `preparation-comparison-v20`. It promotes the proven
100-image sequence through shared code, rather than maintaining a separate
benchmark implementation:

**guarded first crop -> eraser -> residual crop -> confirmed-pattern
reconstruction -> composition -> enhancement comparisons**.

The first crop removes confirmed exterior borders/panels while preserving
the person and repairable hair. Small confirmed clutter is erased before the
residual subject-guarded crop. Confirmed head/pattern overlays can take a
separate masked reconstruction path; masks and synthetic provenance remain
visible. The final composition uses the repaired image and observed screenshot
picture boundary, not a stale eraser candidate or a subject-only crop. The
complete candidate graph and selected ancestry are retained in the report.
Clean controls retain their original bytes for publication.
Version 18 strengthens transparent GMW ring/central-letter confirmation and
requires horizontal flatness at the bottom of a phone navigation panel.
Dark clothing alone cannot establish that external panel. Published v17-v19
reports remain readable with their recorded decisions and pixels; they are
not silently regenerated with the new detectors.
Inside an already confirmed phone frame, paired bright horizontal outlines
must also have both rounded caps before they can confirm a transparent search
pill. Parallel lines or a rectangle alone are insufficient.
V20 also proposes a lower-left nested reel inset only inside an already
confirmed phone-reel frame, and only when a small secondary face, visible
bilateral side edges, a bright top bezel and a dark inner header agree. The
detected box is clipped to the observed picture boundary. This does not cover
phone overlays on ordinary photos or other inset layouts; misses remain
unresolved rather than being labelled clean. The targeted eight-image proof
is awaiting visual review; Ruby's lower-left fill is visibly soft and Harlow's
clothing artifact remains open. Published v17-v19 reports keep their recorded
recipes and pixels and remain readable.

Final recommended pixels are the shared input for Gallery, likeness and
ComfyUI in the authorized sandbox rebuild. Exact originals, variants, masks
and processing history follow the assigned photo; matching also retains its
exact aligned face separately. Reconstruction does not claim recovered
identity or automatically replace protected cast anchors. See the
[likeness guide](likeness.md) for matching evidence and rebase safeguards.

Denoise/tone consume the selected cleanup image, never a rejected eraser or
second crop. Both are rendered for review but not automatically accepted:
there is no calibrated benefit/detail-preservation test yet. A filter failure
retains the last safe cleanup selection rather than reverting a good crop.

**Published v16 compatibility:** from v14 a pure overlay crop can become the cleanup. From v16
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

The two models download once, with pinned hashes, into the configured
`modelCacheRoot\models` (default
`%LOCALAPPDATA%\sovereign-territories\models`; about 400 MB; `torch` and
`torchvision` must be installed; CPU is enough, about 20 s per photo).
Older reports (v5-v19) still verify through `intake_library\legacy.py`;
their recipes and artifacts are not rewritten. Results, decisions and known
gaps are in the intake plan.

For detected reel screenshots, `ui-crop-proposal` also shows the existing
`screens.clean_box` rectangle. It is **comparison only**, never recommended or
fed to enhancement: a fixed rectangle may cut hair/body. The selected cleanup
is the enhancement input. Cropping removes pixels; it does not reconstruct
overlaid hair. Unresolved graphics still pass
through with a reason for later ComfyUI cleanup, without a manual-intervention
requirement. Person-aware framing is not a guarantee
that every detected body or limb boundary is correct.

Open `index.html` in that run directory. Click a candidate for the larger
per-photo page: retained input, control/candidates, then their padded 944x1104
examples. Candidates never replace Gallery sources or the maintained derivatives.
All crops/eraser attempts from this launcher are sidecars. It does not run
identity matching, update the likeness cache, settle actions or change ComfyUI.
Apply may download the pinned models once and the recipe may select their output
provisionally; preview/check do not perform inference/downloads. Denoise/tone can make a
clean image worse; neither is accepted automatically. Native geometry is separate
from downstream padding/resizing; there is no detail-recovering superresolution.

`originals/` retains exact **current** input bytes before decoding; these may
already be cropped. SHA-256 and filename-derived stable photo ID are recorded
in `manifest.json` against the versioned recipe. No raw provenance is invented.
The overlay heuristic is informational: retain the original, show
`original-overlay-unremoved`, and do not block processing or require manual
approval solely for an overlay. ComfyUI can clean it later. Filter failures
show `original-enhancement-failed`, retaining original/control without blocking.
`original-unassessed` is not a claim that a photo is clean. The prepared sandbox flow publishes selected cleanup and verified retained
evidence into People/Review. Automatic denoise/tone selection and the ordinary
incremental production cutover remain unimplemented.
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
for real gallery acceptance and remaining layout work.

### Legacy incremental ingest (paused, not the prepared clean-start flow)

1. General incoming photos go into `Various\gallery`; known-person sets go into
   `Various\<Name>\gallery`. Known Artist inputs belong to that artist's gallery,
   not the general pool. Do not infer Artist provenance from an unknown copy.
2. `bin\library-preview.cmd` previews the installed incremental steps below;
   it is not a simulation of the new prepared-source flow.
3. A likeness-enabled `bin\library.cmd` currently refuses before housekeeping
   because the policy is draft. Do not approve policy merely to bypass that
   guard. After the separate acceptance/cutover gates, the run log would be
   `<work>\_reports\runs\library_sync_<time>.log`.

For today's preparation/likeness experiment, use the
[prepared sandbox sequence](likeness.md#clean-sandbox-rebuild-versus-category-reclassification)
instead. It preserves explicit Artist boundaries and retained photo lineage.

The preview runs each step independently against the current folders; it does not simulate the earlier steps' proposed moves. A file may therefore appear in more than one step's preview even though the real run moves it in sequence. Treat preview counts as current-state counts and use the completed run log for final results.

Then look at where everything landed: `bin\people-gallery.cmd --apply` maintains
folder-prefixed original names and standard derivatives, then builds both
`<work>\_reports\library\people_gallery.html` and
`people_gallery_review.html` with the shared thumbnail cache beside them. The overview and filtered review use the same
identity sort modes and first-nine order, plus shared Chest-up and Head
thumbnail files. Prime-start suitability remains a photo-quality score,
not identity confidence. Use the gallery's current relationship/category
ordering and explicit sort controls; no folder order is identity evidence. Click a thumbnail to open its source, or
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
apart; `bin\likeness.cmd names` and `index` list the people. A repeat can write
reports or propose further maintenance; a successful first pass is not proof
of no-op convergence. Preview and inspect the affected inventories first.
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

The configured reports root (default `<work>\_reports`) is grouped by purpose.
The library routine keeps its current reports in `library`, dated run logs in
`runs`, Angel/Sister/Prospect likeness work in `comparisons\pairings`,
historical comparison material in `comparisons\history`, comparison sheets in
`comparisons\images`, Prime sheets in `comparisons\primes`, and move plans in
`analysis`. Routine commands overwrite their current reports; dated logs are
retained. Old reports have been moved into these folders without deleting them.

**Backups before a real run.** `bin\library.cmd` creates a dated snapshot before changing files; if backup
fails, the routine stops before processing. The snapshot is written under the
configured backup root (default `_backup\library-<timestamp>`) and contains the
work root except `_archive` and older backups, the configured ComfyUI inputs,
and `workflows\workspaces.json`. Its `manifest.json` lists each copied file
with size and SHA-256; every run verifies the copied file list, sizes and
hashes before proceeding. ComfyUI output renders are not included because the
library routine does not modify them. To make a snapshot on demand,
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

#### Bounded backup-format benchmark (explicit experiment)

`bin\library-backup.cmd --benchmark SNAPSHOT` previews a deterministic,
manifest-selected sample; it does **not** create a backup or change its format.
The source must be a completed snapshot. Only selected files are checked against
its recorded SHA-256; this command never scans or verifies the full snapshot.
Selection round-robins extension/path strata with stable hashed filename order.
The defaults are 24 files / 32 MiB, with hard caps of 64 files / 128 MiB.
This is representative sampling, not an exhaustive or random statistical sample.

```powershell
$snapshot = 'B:\Sovereign Territories Sandbox\Working\_backup\library-20261029-235003'
$out = 'C:\Soverign-Territories\soverign-territories\tmp\backup-benchmarks\s24-20261031-real24-final'
cmd /c bin\library-backup.cmd --benchmark "$snapshot" --out "$out" --dry-run
# Use a NEW output path for a new measurement; the saved example below is reusable by --check.
cmd /c bin\library-backup.cmd --benchmark "$snapshot" --out "$out" --apply
cmd /c bin\library-backup.cmd --benchmark "$snapshot" --out "$out" --check
```

Outputs must resolve strictly below the repository's git-ignored `tmp`.
Each format retains its payload and an independently hash-verified restored tree.
ZIP members force ZIP64 local headers; STORED and deflate level 1 are compared
against ordinary directory copies. Nanosecond file mtimes are recorded separately
in `receipt.json`, not entrusted to ZIP's coarse timestamps. Restore verifies exact
selected filenames, sizes, SHA-256 and recorded mtimes, not ACLs, empty directories
or directory timestamps. Library sources, snapshots and reviewer pages are read-only.
Reparse points/junctions/symlinks, unsafe members and snapshot/output overlap are refused.

`--check` verifies the persisted receipt, selected source hashes, every payload
and every retained restore, including exact file counts and bytes. Repeating an
unchanged invocation verifies/reuses the receipt without rewriting measurements.
Changed inputs/settings, modified/truncated archives and incomplete runs fail
closed: use a new ignored output path after investigation. Interrupted benchmark
folders have no complete receipt and are never resumed or silently overwritten;
they are **not** recovery snapshots. No existing snapshot is removed or replaced.

Oct 31 bounded measurement (Python 3.14.3): 24 of 72,991 manifest files,
13,697,208 of 41,998,676,177 bytes. Twelve selected JPEG/PNG files total
3,242,746 bytes; the other twelve are metadata/pages and one MP4.
The useful persisted receipt is the example `$out\receipt.json` above.

| Payload | Build s | Full hash verify s | Restore + full hash/mtime check s | Payload bytes | Payload files |
| --- | ---: | ---: | ---: | ---: | ---: |
| DIRECTORY | 0.1085 | 0.1047 | 0.2166 | 13,697,208 | 24 |
| ZIP64 STORED | 0.0952 | 0.0201 | 0.2788 | 13,703,134 | 1 |
| ZIP64 deflate 1 | 0.3266 | 0.0690 | 0.2823 | 12,596,858 | 1 |

Every restored format contains all 24 files / 13,697,208 bytes with exact hashes
and recorded mtimes. Deflate saves 8.03% on this **mixed** sample, but the twelve
image members alone expand to 3,411,290 compressed payload bytes (before ZIP
headers), so this is not evidence that compressing image backups saves space.
ZIP64 STORED adds 5,926 bytes but reduces payload file count from 24 to 1.
Logical payload bytes exclude allocation size, restored copies and receipt overhead.
Single passes run in fixed DIRECTORY/STORED/deflate order with warm OS caches;
no cache eviction, fsync, cold-drive or same-volume B: throughput is measured.
Builds read B: and write repository tmp on C:. An independent final `--check`
passed. The >4-GiB ZIP64 boundary and full-library interruption recovery are
not exercised by this bounded experiment.

**Recommendation:** retain DIRECTORY as the backup default. Archive file-count
reduction is promising, not approval to adopt archives, change retention or prune.
Broader workload/cold-drive measurements and dependency-aware recovery/retention
approval remain [S24 work](../plans/2026-10-28-storage-operations-and-retention.md).

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
| 3 `likeness crop` | legacy face-guided app-bar/other-subject/background crop for unprepared photos; verified prepared natives skip it; it cannot guarantee limbs are kept | the uncropped photo: `_archive\<folder>\gallery_uncropped` (`likeness crop --undo` puts the last batch back) |
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

**Legacy reprocessing commands.** `likeness pullback NAME ...` (or `--small 2`,
or `--all`) previews returning eligible Prospect photos to Various; selected
photos and other active protection/exclusion/retained-set guards still apply.
Do not use legacy `sort` threshold overrides as a policy-calibration shortcut.
The Artist-only backup grouping entry point is
`bin\likeness-artists.cmd artists --from <backup>\Artists`; preview and confirm
its domain/recovery conditions before any apply. None is a substitute for the
prepared sandbox clean-start run.

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

### Deliberate photo maintenance

1. Keep incoming general and named-person sources in Various until their
   supported intake/assignment step. Keep Artist inputs in their own domain.
2. Use staged Review/Reject/retirement/Junk actions instead of deleting an
   unwanted photo or manually moving a retained set.
3. Preview `bin\people-gallery.cmd --dry-run` for maintained names/derivatives
   and report refresh. Respect its action-undo/backup gates. Direct
   `bin\originals.cmd` is the legacy Gallery-only renderer, not the prepared
   maintenance contract.
4. For a separately approved configured-library workflow choice:
   `bin\inputs.cmd set Angelica --photo angelica_image_<id>_944x1104.png`, then
   `bin\inputs.cmd reset --hero Angelica`. Do not run this against sandbox inputs.

Not every photo has a headshot, by design: a headshot needs a face big enough to enlarge to 944x1104 without mush (a crop of at least 30% of the output height) and not hidden under a phone's app bars.

## What `originals` does

| Step | What |
| --- | --- |
| Rename | Each original prefix follows its current folder; stable IDs are retained. Use supported moves rather than manually shuffling retained/catalogued photos. A collision is held with a warning. |
| Scale | Each original is fitted inside 944x1104 (the shape is kept, EXIF rotation applied), centred on light grey (`originals.STUDIO_GREY`, 190,190,190; cream until Oct 26), saved as `<name>_944x1104.png`. A phone screenshot of Facebook (tall, with the app's light navigation bar along the bottom) is first cut down to the picture itself, without the bars, caption and icons (`tools/art/screens.py`), unless her head reaches into them. A copy already newer than its original is skipped (`--force` redoes all). |
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

Two files with the same picture ID require deliberate comparison. Use the
duplicate preview or staged recovery-aware actions; do not delete one merely
because its filename ID matches.

A chosen photo whose original is in another hero's folder, or is gone, is reported (`ELSEWHERE`, `MISSING`), never guessed. A hero whose photo is still a placeholder name is listed as `NO PHOTO`.

## Notes

- Use the [runtime requirements](#python-runtime-and-dependencies); Pillow
  supports WebP too. Pillow alone is not the complete processing dependency set.
- `rename_originals.py` and `rename_inputs.py` (a rename map for the old facebook/Screenshot names, sisters only) are superseded by this; nothing calls them.
- A scaled image becomes a workflow input only when you choose it (`inputs set`) or run `inputs photos`; `sync-inputs.cmd` and `inputs reset` also find images in the library.
- The old `scale_rename_prune_images.ps1` in the work folder now only forwards to `bin\originals.cmd`.
