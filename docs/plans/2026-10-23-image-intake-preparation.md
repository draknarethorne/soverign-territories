# 2026-10-23: source-preserving image intake and preparation

**Status:** active (Phase 1; sandbox sidecar pilot authorized Oct 23; no gallery replacement or production apply)

## Oct 25: incremental scope and the next clean-start acceptance

The latest clarification is preserved verbatim at the end. It refines I21/I22/
I23 and cast C2-C6, rather than creating a second rebase or matching pipeline:

- The next rebase must start from the supplied immutable images and run the new
  intake preparation before likeness, not repeat the old raw-image matcher-only
  experiment. Preparing a 12-photo sidecar sample does not satisfy this.
- Offer the same staged run as **intake only**, with review and safe resume, or
  **intake → likeness → assignment**. Preserve prepared/original/model/policy
  lineage and named-person intent; do not implement competing command paths.
- Clean-start matching must not use old output folders/names as reference truth.
  It also must not erase manual decisions, original names, protection opt-outs
  or family history: preserve them through verified stable-ID continuity or
  hold/refuse the affected reset. A guard is not a completed migration.
- The user is not re-running a rebase until this integration is ready. Do not run
  one now to validate unrelated GUI/protection work.
- Gallery main navigation, Intake/run history and retained image detail remain
  the one-stop review surface. Layout owns shared mobile navigation/versioned
  footer polish, not a new execution backend.
- Commit/push is authorized after validation and day hygiene, not permission to
  include secrets, discard raw feedback, or publish unverified code.

I22's intake-only/resume and I21/I23's retained-set/publication wiring remain
explicit integration work. Current sidecar preparation plus matching commands
must not be presented as the finished combined clean-start pipeline.

## Oct 25: v16 crop → crop → erase → frame, and the modular intake package

The user's 23:08 note (verbatim below): erased icons came back after the
second crop, and the second crop cut hands. Inspecting the v15 series showed
why:

- the second crop was computed on the pre-eraser image, so it dropped the eraser result;
- crops were single-side and framed by face width, so they cut hands and legs;
- the Telea/Navier-Stokes fills smeared over hair.

**v16 decisions** (made by AI as the user asked; to review):

| Step | v16 behaviour |
| --- | --- |
| first crop | Borders and black reel panels, unchanged. |
| clutter detection | White glyphs and captions, the search bubble, magenta corner logos, app bars and cards, found on the first-crop image. |
| second crop | Runs **before** any repaint. Each side is trimmed past its edge clutter only while a Mask R-CNN person mask loses at most 0.5%. A screen-wide app bar may cut the legs only 4.5 face heights below the face. |
| eraser | LaMa repaints the clutter left inside, on the second-crop output, and **is selected**. It never repaints faces, cards lying on the body, or more than a fifth of the picture. |
| composition | Frames the whole person with a small margin, widened toward 944x1104. When the mask ends mid-leg (bottom wider than 20% of its widest row), the bottom stays at the frame edge. |
| denoise/tone | Comparison only, as before. |

Both models are pinned by sha256 and download once to
`%LOCALAPPDATA%\sovereign-territories\models`. CPU takes about 20 s per photo.

**Sandbox run** `_reports\preparation\v16`: 12 retained inputs, 217 files,
155 MB (v14c: 205 MB). `--check` passes. Every final image was inspected
against its original:

| Photo | Recommended | Visual verdict |
| --- | --- | --- |
| `203951` reel | eraser | Search bubble over the hair repainted cleanly; the picture-in-picture reel thumbnail at the bottom left stays (gap) |
| `204050` reel | second crop | Bubble and app bar cropped, hair kept; the cut is at the thighs and a sliver of the translucent ad card stays (gap) |
| `123318` reel | eraser | Right icons and the caption over the dress erased; the round avatar and a few faint caption specks stay (gap) |
| `123511` reel | eraser | Right icons erased; clean, full figure to the feet |
| angelica `...4360`, `...1248`, `...7310`, `...3507` | eraser | GMW logo fully gone, including where it crossed the trousers or legs |
| facebook `...9009` | eraser | Logo gone. The first run's composition cut the shins (mask stopped mid-leg); fixed by the limb rule above |
| `sophie_lloyd` | original | Nothing to clean |
| two Facebook screenshots | Junk candidate | No usable face, unchanged |

**Legacy removed or isolated** (user's late Oct 24 note, verbatim below):

- New package `tools\art\intake_library\`: `models`, `subject`, `clutter`, `fill`, `pipeline` and `legacy`.
- About 350 lines of retired geometry are removed from `preparation_geometry.py`: outlined
  bubbles, repair trials, finishing crops, corner marks, the old composition. Their tests are removed too.
- `legacy.py` holds only the v5–v15 recipe ids and step orders, so old reports still verify. Nothing in it produces images.

- [ ] **P2 ai** I27 Close the v16 visual gaps: the picture-in-picture reel
   thumbnail (`203951`), round avatar photos (`123318`), the translucent ad
   card in `204050`, and faint caption specks. Contour and line-pair
   detectors were tried for the thumbnail and were too fragile; a learned
   UI-element detector or template matching is the next try.
- [ ] **P1 you** I29 Review the v16 report (`_reports\preparation\v16\index.html`):
   accept or reject LaMa auto-selection, and the app-bar rule that may cut legs
   well below the face (`204050`).
- [ ] **P3 ai** I28 Delete `intake_library\legacy.py` and its `validate`
   branches when the last v5–v15 report is removed from the sandbox.

## Oct 24: version sets, intake-only runs, named folders and v14 selection

The user's late Oct 23 message (verbatim below) asks for four things, plus an
honest answer about earlier recommendations.

**Honest answer on earlier recommendations.** v6 to v13 never selected a
second crop. The recommendation was always the original or the border/panel
geometry, even when the second crop was visibly cleaner. That rule was
deliberate, but the reports did not say so plainly. v14 (`preparation-comparison-v14`)
can select a pure second crop as cleanup and final only when it:

- removes at least 95% of the proposed mask;
- loses at most 25% of the area;
- keeps an aspect ratio between 0.45 and 1.8;
- keeps a body frame around every face: 1.25 face widths each side, the head margin above, and 4 face heights below (or the image edge);
- has screenshot evidence, or a mask that is one compact corner mark (at least 95% of its pixels; the mark covers at most 5% of the image, inside the outer 40% of the frame). A small stray speck elsewhere is tolerated.

Erasers and denoise/tone are still never auto-selected. Enhancements now start from the selected cleanup.

**v15: the agreed crop → clean → final crop sequence.** The intake now runs
the user's sequence end to end:

1. first crop: solid borders and reel panels;
2. eraser trial: compared, never auto-selected;
3. overlay crop (v14 rules);
4. composition: a final framing crop of the cleaned image;
5. denoise/tone comparisons, starting from the result.

Composition reuses the gallery's existing `likeness.person_box` rule rather
than a new one: hair above, all of the body below, about 3.6 face widths
each side. It applies when one person's head is in the upper 40% and the
crop keeps under 70% of the picture. Several people, or lying or low poses,
are skipped with a reason. This is the same crop `likeness crop` already
applies after assignment, so moving it before identity changes when it
happens, not what it does. That is why it is auto-selected. At the I12 cutover
the post-assignment `likeness crop` becomes redundant for prepared photos.
v6–v14 manifests keep their five-step trace and still pass `--check`.

v15 sandbox run (`_reports\preparation\v15`), inspected visually: `123511`
(purple dress reel) is framed from the panel crop. The right-side reaction
icons and the background beside her are trimmed, and the figure is kept from
hair to feet. Only the far edge of the skirt flare is grazed; clearly better
than v14. The other portrait shots were left alone, because about 7 face widths
already fill their width. This matches the gallery's crop today; tighter
framing of portrait shots needs body evidence (I25).

v14c sandbox run on the 12 retained inputs (`_reports\preparation\v14c`,
262 files, 205 MB), inspected visually:

| Photo | v14 outcome | Visual verdict |
| --- | --- | --- |
| angelica `...7518039923121523507` | second crop selected, GMW logo removed | Clean, mid-thigh three-quarter shot; better than the original |
| angelica `...7513772617730547310` | second crop selected, GMW logo removed | Clean, but the seated pose loses shins/feet; flag for review |
| angelica `...7513772466838834360` | refused: body frame | Crop looked fine (lying selfie); conservative miss |
| angelica `...7513772571463861248` | refused: body frame | Correct; the crop cut at the waist |
| facebook `...7518708658483539009` | refused: 26.3% loss | Crop at the knees looked acceptable; conservative miss |
| `204050` reel | refused: top banner remains | Correct; the bottom crop removes the ad but not the oval |
| `123511` reel | refused: mask specks, 27% loss | Correct; the right crop clips the dress; stray mask specks |
| Others | unchanged (geometry/original/Junk skip) | As in v13 |

**Retained version sets (I21).** The user's proposal is agreed in principle:
keep every intake version of an image instead of discarding it.

- The set lives beside the incoming photo until identity assignment, then moves with it:
  - exact original → `gallery_org`;
  - recommended source → `gallery`, which feeds the 944x1104 derivatives;
  - the version set → `gallery_intake`.
- Disk: a full candidate set is about 16.5 MB/photo (all PNG), about 6.6 GB per 400 photos.
  The proposal therefore keeps the manifest, the masks and each step's selected or
  attempted crop. The comparison-only renders (enhancements, eraser variants) are
  regenerable from the retained original and the recipe, so they stay out of backups,
  like the thumbnails.
- `originals.archive_org` currently archives every `*_org` folder. The cutover must
  stop it from archiving `gallery_org`/`gallery_intake` (U7).

**Oct 25, 09:23 retention clarification:** the gallery detail must show every
version actually retained with the image, including denoise and lighting/tone
alternatives kept for evaluation, before and after assignment. The earlier
minimal-subset/backups paragraph is a proposal, not permission to discard those
variants. Discarded candidates stay out of the current retained set; historical
run comparisons remain separately labelled. I21 still settles exact storage and
backup coverage. I23 needs verified assignment/copy/move continuity, not merely
links to all historical runs. Raw feedback and main-entry navigation live in
[layout L19/L12](2026-10-22-gallery-review-layout.md#oct-25-0923-gallery-first-navigation-and-retained-image-detail).

**Intake-only stop and resume (I22).** Run intake on Various and stop there for
review. Then either redo it with a new recipe, or resume into likeness from the
reviewed results without recomputing. The resume key is the source hash plus the
recipe id, which `prepare-images` already records.

**All-versions page (I23).** One page per photo showing every version, step
reason and recommendation. It is reachable from Review and People through the L12
provenance bridge, after identity assignment as well as before.
Oct 25 reconciliation: per-run detail pages and exact-current-source comparison
links already exist (layout L12). I23 remains open for the retained version set's
post-assignment lineage, unavailable/regenerable version labels and integration
with I21/I22; the delivered bridge does not prove publication or survive an
unverified rename. Gallery layout changes do not run intake.

**Named-folder seeding (delivered, I24 verifies).**

- Cause of the regression: the folder scan treats `Various` as a single pool once
  `Various\gallery` exists, so `Various\<Name>\gallery` was never offered to likeness.
- The fix is a journaled `likeness seed` command, step 0 of `library.cmd`. Each named
  folder's photos join that person without face matching:
  - one case-insensitive name match → the existing person;
  - no match → a new Prospect (5+ photos) or Potential;
  - several matches → held.
- Photos rejected for that person stay in place. `likeness undo` reverts the move.
- Seeded people are ordinary (unprotected). A later reconcile may still split strong
  outliers out of them; whether a seeded folder should be anchored is the user's decision.

- [ ] **P1 either** I21 Implement retained version sets (`gallery_intake`) per the proposal
   above: decide the retained subset with the user, write it at intake, move it with the
   identity, exclude regenerable renders from backups, and reconcile `archive_org` (U7).
- [ ] **P1 ai** I22 Add an intake-only stop and resume to the launchers (`library.cmd`
   or `prepare-images.cmd`), keyed by source hash and recipe, with preview and `--check`.
- [ ] **P1 ai** I23 Build the per-photo all-versions page and link it from Review and
   People pages through the L12 bridge; mark missing/regenerable versions explicitly.
- [ ] **P1 you** I24 After the sandbox rebase, drop `Various\<Name>\gallery` folders of
   known people and run `bin\library.cmd`; confirm they land under that name, and decide
   whether seeded people should be protected from automatic splits.
- [x] **P2 ai** I25 Tune v14/v15 misses seen in the sample runs: speck-tolerant mask removal for
   screenshots (`123511`), a body-framed crop slightly over 25% loss (facebook), lying/selfie
   poses refused by the frame (`...4360`), protecting feet in seated full-body shots (`...7310`),
   and tighter portrait framing once a local body/person detector is evaluated.
   Result (Oct 25): v16 cleans all four with the LaMa eraser and keeps the full figure;
   Mask R-CNN is the evaluated person detector. Remaining gaps are I27.

**Simple, composable flows (user direction, Oct 24).** Every stage stays one
step that runs alone (its own command, with `--dry-run`/`--check`) or inside
the combined `library.cmd` order. There are no special paths per case:

- named folders are step 0 of the same run;
- intake-only is a stop point (I22), not a second pipeline;
- Artists use the same intake steps with their own matching domain.

Various is the single drop point for incoming photos, including
`Various\<Name>\gallery`.

**Directory reckoning (I26, proposal for the user).** Today's tree mixes three
things in its roots: where a photo is in the flow (Various, `_junk`), the
subject's role (Angels, Sisters, Prospects, Potentials) and the source domain
(Artists). The wording also assumes women. Supporting men, animals and other
subjects would multiply roots unless these are separated. The proposal, with
nothing moved until it is approved:

| Concern | Proposal |
| --- | --- |
| Intake | One holding root (today's `Various`, perhaps renamed `Intake`): `gallery` for unknown photos, `<Name>\gallery` for named sets, version sets until assignment |
| Subject kind | A small number of kind roots (`People`, later `Animals` or others), each with its own likeness domain, so faces of different kinds never mix |
| Role and sex | Catalogue attributes (role: angel, sister, prospect, potential; sex/gender), not folder roots; galleries filter on them |
| Artists | Stays a separate source domain, as now |
| Per subject | `gallery` (accepted source), `gallery_org` (original), `gallery_intake` (version set), `review`; derived `*_944x1104` folders are regenerable and excluded from backups |

- [ ] **P2 you** I26 Decide the directory reckoning: intake root name, kind roots, role and
   sex as attributes, and the per-subject folders. Then plan the migration (paths in
   `workspaces.json`, catalogue, journals, undo, galleries) as its own phase after the
   sandbox end-to-end run.

## Oct 23, 21:21: visual UAT and gallery trace continuation

The user now authorizes image inspection, source-preserving intake experiments
and GUI integration together. This supersedes the earlier ban on fresh comparison
runs only for bounded sidecar comparisons; it does not authorize assignment,
source replacement, quarantine, production changes or settlement of action undo.
Keep the existing immutable runs. Reproduce comparisons from their retained
inputs rather than assuming today's incoming folder has the same contents.

I11 owns edge-aware eraser/crop experiments and visual assessment; layout L12
owns a verified read-only bridge into gallery pages. A comparison is not a
record that a source was accepted or published into a Gallery. Missing/stale
evidence must be explicit, and an identity match is not source provenance.

Initial direct visual UAT sampled 12 v7 cases (including the two named logo
images, both motivating screenshots, clean/small-face examples and animal-only
screenshots). Observed shortcomings:

- Both named Angelica photos retain conspicuous colored lower-corner logos.
  The v7 right-side white-stroke detector does not handle them; absence of a
  reel flag is not absence of graphics.
- `123318` retains the top search bubble over the hair and lower caption.
  Right-icon repair does not address either; a head/hair exclusion deliberately
  leaves that area untouched. A generic inpaint cannot prove hair restoration.
- `123511`'s panel crop is substantially better than the phone screenshot.
  Its eraser leaves icon traces/smearing, while the right-side crop removes
  overlays at the cost of dress/background. That trade-off is a useful review
  alternative, not an automatically superior full-body source.
- Other sampled art screenshots retain top bubbles and lower labels; the
  narrow masks never attempted those areas. A black mask is not evidence that
  a photograph is clean. Animal-only/no-face skips must stay visible as skips,
  not repeated original images labelled as successful trial outputs.

Next bounded implementation: extend *exploratory* region masks beyond the
right reaction rail, expose coverage/protected-region limitations explicitly,
and preserve nonselection of uncertain reconstruction. No blind crop-to-clean
loop or invented quality score. Visual inspection is helpful UAT, not a claim
the assistant always outperforms human review.

### v8 result and direct visual acceptance boundary

New immutable comparison:
`Working/_reports/preparation/visual-uat-20261023-v8/index.html`.
All 113 incoming files were read for sidecar comparisons only, not moved,
assigned or published. 109 pass the limited face gate; four skip transforms.
107 eraser candidates are now attempted and explicitly rejected for automatic
use, versus 95 in v7. The widened mask considers white strokes at all edges,
bounded magenta lower-corner envelopes, and neutral top-bubble envelopes on
reel screenshots, without requiring a reel flag for corner trials.
Expanded face/hair exclusions remain mandatory; per-image reasons record how
many proposed pixels they excluded. These are graphic hypotheses, not OCR,
general logo detection, semantic segmentation or faithful reconstruction.

Direct inspection after generation shows:

- Both named corner-logo regions are now attempted. The dark-floor example
  loses most logo content but replaces marble texture with conspicuous smearing.
  The light-sofa example loses much of the logo but leaves a colored fragment
  and fabric/edge artifacts. Neither is accepted as restored imagery.
- The top search bubble still remains across the protected hair region.
  Erasing its exposed ends can create angular edges. Partial masking is not
  a satisfactory result; do not call this successful text removal.
- Lower-caption strokes receive trials, but labels/background silhouettes
  remain and local texture is damaged. More changed pixels are not improvement.
- The fuller `123511` panel crop remains useful. Its right-edge crop looks
  cleaner but loses dress/context; the current recommendation intentionally
  keeps the fuller provisional input. Workflow-purpose-specific review
  (portrait vs outfit/pose) is needed rather than a universal score.

Decision: broaden *observable attempts*, not automatic trust. The existing
local Telea algorithm is inadequate for faithful hair/fabric/marble repair.
Keep last conservative cleanup selected; expose failure and leave uncertain
repair for an explicitly evaluated stronger reconstruction approach. No model,
download, dependency, ComfyUI render or repair-acceptance rule was introduced.

50 focused preparation tests pass, including all-edge/corner trials on
non-reel images, full corner-envelope masks, protected hair and unchanged
unmasked pixels, lineage/nonselection, and check/repeat. Actual launcher
preview/apply/check exit 0; v7 still verifies. All 113 input hashes/mtimes,
two captured catalogue/cache records and 6,044 active file metadata records
remain unchanged. The new report costs 2,714 files / 1,991,511,772 bytes;
that is retained comparison evidence, not disposable thumbnail cache.
Generation took about 340 seconds; verification about 38 seconds. No full
library performance claim follows from this batch.

Remaining I11 substeps (I10 owns user acceptance, I12 owns live integration):

- [ ] **P1 ai** I18 Build a reviewed mask benchmark for complete bubble/logo shapes, including
   misses, false positives, face/hair overlaps and lower-caption backgrounds.
- [ ] **P1 either** I19 Compare stronger reconstruction on reviewed identical masks when a safe
   resource slot is available; Telea/Navier-Stokes are compared and rejected. Preserve
   face/identity texture, hair, fabric and background before selecting anything.
- [ ] **P2 ai** I20 Complete subject-preserving composition before/after cleanup, beyond
   the delivered edge-crop comparisons: trim excess background, center the full visible
   subject with breathing room and preserve head/hair, arms/hands, legs/feet for full-body
   sources. Skip uncertain/no-benefit crops; distinguish head/chest derivative framing.

Keep recommendations conservative until these comparisons justify changing
them. I12 then completes the live crop cutover and post-assignment provenance
contract, with separate approval and recovery tests.

### Continued requirement: complete repeated screenshot clutter

The user's follow-up explicitly includes the banner across hair, lower
captions, logos on either side, borders and other repeating screenshot graphics.
The goal is one usable final source, not many partially cleaned icon trials.
I18 must benchmark complete overlay shapes rather than isolated white letters;
I19 must evaluate reconstruction under those complete masks, including hair;
I20 must compare a bounded crop when repair fails without sacrificing the
head. A face/hair exclusion that simply leaves the banner is an unresolved
case, not completion of this requirement.

Installed ComfyUI does expose `flux1-fill-dev.safetensors` and existing edit
models, but the running Angel Primes instance has one active and 100 queued
jobs, about 1.8 GB free host RAM and 2 GB free VRAM on a 6-GB RTX 3050 at
inspection. Do not interrupt/unload models, enqueue experimental heavy jobs
ahead of that queue, download a model or start another GPU instance implicitly.
Local mask/crop work can continue; neural reconstruction benchmarking needs
an available bounded resource slot, not a hidden production queue change.

### v9/v10: complete-bubble and mask-directed crop replay

Replayed 12 exact retained v8 inputs in an isolated short-path sandbox:
`B:\ST-v9\Sovereign Territories Sandbox\Working`.
Both immutable reports live below its `_reports/preparation/`, as `v9/index.html`
and `v10/index.html`. They are replay evidence, not current incoming ownership
or new accepted Gallery sources. No new full 113-image batch was needed.

v9 added complete detected top-bubble trials and wider corner envelopes,
plus one mask-directed left/right/bottom finishing-crop comparison. The
finishing crop consumes the last selected input, never a rejected repair.
It retains the expanded head margin and limits image-area loss to 30%.
Mask removal divided by area loss prioritizes a comparison, not visual
quality or body/outfit preservation. All remain rejected automatically.

Actual v9 inspection found the motivating hair bubble still refused because
the 15% face-box expansion included the overlying hair. v10 distinguishes
that large hair margin from the detected face box plus 2% (minimum 2px).
Only a complete detected bubble may override the hair margin; any overlap
with that smaller face guard refuses the entire shape. Other stroke/emblem
masks still exclude the expanded head/hair region. Detector error remains
possible: this is an explicitly rejected reconstruction experiment, not an
accepted face-safety guarantee.

Direct enlarged v10 inspection confirms:

- `123318`: the entire detected "Find related reels" bubble is now masked
  and removed in the candidate, rather than only its ends. The fill creates
  an obvious flattened/streaked hair cap; **not an acceptable final source**.
  Side icons and lower labels also remain partly visible.
- `203951`: the complete bubble is attempted, with conspicuous hair/background
  smearing. Its bottom crop removes a lower banner but leaves the top bubble.
- `204050`: the translucent/colored top bubble is not detected as a complete
  neutral shape; isolated text repair is visibly incomplete. Bottom cropping
  is cleaner than the repair but sacrifices legs/context.
- Both named Angelica corner masks cover the main logos. The light-sofa
  repair still has pink contamination/diamond artifacts; dark marble smears.
  Bottom-crop alternatives remove the logos but lose leg/outfit context.
- `123511`: the fuller panel crop and cleaner right-side crop remain useful
  alternatives for different reference purposes, not a universal winner.
- The sampled animal screenshot is explicitly skipped as a report-only Junk
  candidate. No eraser or enhancement is run on it.

v10 counts: 12 inputs; two report-only Junk skips; four selected provisional
first crops; nine rejected eraser trials; eight rejected finishing crops;
ten rejected denoise and tone comparisons each. Preview/apply/check exit 0.
Report cost: 235 files / 180,452,688 bytes. v9 remains separately verifiable
(238 files / 182,674,747 bytes). Both add about 363 MB of retained comparison
evidence, in addition to the v8 batch; do not treat these as disposable thumbs.

54 focused preparation tests pass, covering complete shapes over hair,
face-intersecting refusal, near-face non-overlap, unchanged protected pixels,
all three finishing-crop directions, empty masks, head/area guards and
nonselection/lineage. Final verification against the untouched pre-v8 baseline
confirms all 113 live input hashes/sizes/mtimes and two catalogue/cache records
unchanged; all 12 replayed retained hashes match v8. v8 and v9 checks still pass.
The full quick checkpoint was 27 suites / 652 tests plus 19/19 mutations before
the final v10 changes; it is not relabelled as a final full-v10 run.

I18 is partial (complete neutral bubbles now observable; translucent shapes,
captions, false positives and mask benchmarking remain). I20 is partial
(three edges implemented; intended-purpose/body trade-offs uncalibrated).
I19 remains blocked on a safe stronger-reconstruction test slot. Do not loosen
automatic acceptance to make the report look finished. A genuinely clean,
usable final source remains the requirement.

Operational lesson: the first deeply nested replay failed Windows filename
length limits before publication. Retrying in the short root succeeded;
sources and previous reports were untouched. Keep replay roots short.

### Same-mask CPU reconstruction comparison

Before treating an occupied GPU as a complete stop, compare the two already
installed OpenCV reconstruction methods on identical masks: Telea radius 3
and Navier-Stokes radius 3. The latter is a separate rejected candidate, not
a second processing selection, and must not feed cropping or enhancements.
Both use the same last-selected source and mask. Show algorithm/mask lineage
and failures explicitly in the report, validate the new candidate, retain
old recipes unchanged and inspect the actual hair/fabric/marble results.
This bounds I19's available local-method comparison; it does not claim to
replace a future neural reconstruction trial or resolve missing masks.

**v11 result:** the existing preparation launcher now renders `eraser-ns`
beside Telea on identical selected-input bytes and `eraser-mask` pixels.
The manifest records its algorithm, input, mask, candidate, rejection/failure
and reason separately from the five-step selection chain. Missing variants,
wrong dimensions or broken comparison lineage are rejected. An OpenCV
alternative failure is visible and preserves Telea, the cleanup choice and
downstream processing. No dependency, model download or new command was added.

The same 12-input replay at
`B:\ST-v9\Sovereign Territories Sandbox\Working\_reports\preparation\v11`
passes launcher preview/apply/check: nine same-mask alternatives, zero failures.
Direct inspection of enlarged hair and both named logo regions finds no
acceptable improvement: Navier-Stokes also makes the artificial hair cap,
leaves pink corner contamination and produces a more visibly banded marble
fill. The partially detected translucent bubble and reaction icons remain
incomplete under both methods. Keep both rejected; mask changes alone cannot
recover hidden detail and comparing two local fills does not establish a winner.

57 preparation tests pass. The final full quick launcher passes **27 suites /
659 tests**, plus **19/19 validator mutation cases**, including the schema and
same-mask failure/lineage regressions. All 113 live hashes/sizes/mtimes and
both captured state records still match the untouched pre-v8 baseline; all
12 retained replay hashes match v8. v11 adds 262 files / 206,219,371 bytes.
This remains retained comparison evidence, not regenerable thumbnail cache.
Browser checks of v11 pass at 1440/760/375/320px without horizontal overflow:
nine alternative panels/images, explicit rejected method/input/mask lineage,
the unchanged five-step trace and the original three summary views.
All 822 local HTML artifact references resolve within the report tree.

A fresh queue-count check still shows one running and 85 pending ComfyUI jobs.
Do not consume that GPU for an implicit model experiment. I19 is now partial:
available local methods compared and rejected; stronger reconstruction remains
resource-blocked. The clean-final-source requirement is explicitly unfinished,
not closed by the successful tests or this comparison.

### CPU-only continuation: outlined translucent banners

Keep the occupied GPU queue untouched when no resource decision is available.
Measured contours from the actual prepared images show that a 3x3 closing of
Canny 50/150 edges joins the complete rounded outlines of `123318`, `203951`
and previously missed `204050`; their contour-area/bounding-area ratios are
0.907, 0.933 and 0.922. The already panel-cropped `123511` has no such candidate.
Use this bounded shape hypothesis alongside neutral-fill detection, merge
overlapping boxes, preserve face refusal and automatic rejection, and verify
filled masks rather than isolated text strokes. Shape evidence is not semantic
proof of UI or proof of faithful reconstruction.

**v12 result:** the previously missed translucent `204050` banner now receives
one complete mask, rather than isolated text-stroke repairs. Actual inspection
shows the banner removed from both local candidates, but the replacement
architecture is visibly stretched. `123318` and `203951` also have one merged
complete-bubble attempt each; the panel-cropped `123511` has no outline trial.
No new outline trials appear in the other eight replay records. Synthetic
tests cover colored/neutral outlines, merged inner/outer contours, face refusal,
unchanged unmasked pixels, non-screenshot gating and excluded low/tall shapes.
This is a useful missed-pattern correction, not accepted restoration.

The v12 replay passes actual preview/apply/check and preserves all baseline
113 live inputs and both state records, plus 12 exact retained replay hashes.
60 focused preparation tests pass. The full v11 checkpoint remains 27 suites /
659 tests and 19/19 mutations; it is not represented as a rerun of the final
v12 tree. Previous v11 still verifies. The v12 report adds 262 files /
206,105,586 bytes; 822 local references resolve, and browser checks at
1440/760/375/320px show nine alternatives, five trace steps, three summaries
and no horizontal overflow or broken loaded images.

Safe CPU-only implementation and visual UAT for this continuation are delivered.
Do not convert that delivery into closure of I18/I19/I20 or live cutover:
semantic mask quality, convincing hidden-detail reconstruction and
purpose-specific crop selection remain separate acceptance work.

### 23:01 oval-position follow-up: guarded top-crop comparison

v13 adds the missing top direction to the existing finishing-crop comparison.
On detected reel screenshots, a complete outlined oval's measured lower edge,
plus the existing 0.5%-of-min-dimension (minimum 2px) guard, defines a proposed
top cut. The cut must preserve every expanded head margin and stay within the
30% area-loss limit. Face evidence is mandatory. It uses the selected source,
not a rejected reconstruction, and remains a rejected comparison rather than
changing cleanup, enhancements or final recommendations. If another crop is
shown while the top proposal fails its safeguards, its reason explicitly
states that the top banner remains unresolved.

Synthetic end-to-end report coverage demonstrates the positive-clearance case,
checks original pixel crop dimensions and nonselection/lineage, and verifies
near-hair/multiple-face refusal, coordinate offsets, screenshot gating and
missing face evidence. Direct evaluation against saved v12 native-geometry
images confirms all three actual banner examples overlap the conservative
head margins: oval lower edges 242/243px, guarded head tops -105/-62/78px.
They must not be cropped merely because a face alone would survive.
`123511` already has its banner removed by its panel crop. No extra 200-MB
real-image report was generated to repeat these unchanged recommendations.
The launcher v13 preview and immutable v12 check pass; 62 preparation tests
pass. Existing masks/repair comparisons remain available in v12.

### Oct 24, 05:57: composition and accessible original

Cropping is not only an overlay-removal fallback. I20 also owns tighter
subject-preserving composition: first crop what can safely be removed,
clean remaining graphics, then refine framing around the full visible body
with useful margins. Full-body references should preserve visible limbs,
hands/feet, head/hair and pose while reducing excess background. Centering
on the face alone cannot establish this. Existing head-margin/area guards
do not implement subject/body segmentation; do not relabel them as such.
No fixed target ratio or crop-to-fill is required at native-source stage.
Head/chest framing and 944x1104 padding remain distinct downstream outputs.

I12 with upkeep U7 owns the clarified storage target: accessible exact original
in `gallery_org`, accepted cropped/cleaned native source in `gallery`, then
padded full/head/chest variations from the accepted source. Existing
`originals.archive_org` moves `*_org` folders into mirrored archives, so the
cutover must deliberately reconcile that behavior, original viewer access,
stable photo ID/hash links, backup, rename/move lineage and undo. Do not
publish new originals into a folder the unchanged routine would archive.
This clarification establishes the target; it does not authorize live source
replacement or assert that the current sidecar pilot already implements it.
The canonical sequence and safeguards live in the photo-library runbook.

## Oct 23, 17:05: review handoff and incoming-batch pause

Do not process the current Various/gallery batch while the user removes the
Artist test images. Do not route, quarantine, replace sources or run a fresh
batch preparation report until the user confirms it is ready. Existing immutable
sidecar reports remain available for review; their Artist test copies are dated
evidence, not instructions to include Artists in the people library.

The CLI split I16 is delivered, but it does not complete gallery isolation.
People overview/Review currently retain an opt-in Artist surface and call
`likeness.build` outside a domain context. Hiding Artist cards alone would not
exclude their evidence from centering. I17 below owns that remaining boundary;
do not claim it is already implemented.

Safe work during review, without processing the incoming batch:

1. Complete I17 with synthetic fixtures: general-only discovery, scoring,
   comparisons and people pages. Artist GUI work is deferred to layout L14.
2. Continue I1's installed-path/provenance inventory and I12/U7 fixture coverage
   for the existing crop cutover: retain -> prepare -> analyze/assign ->
   publish/rename -> full/head/chest -> viewers/selected inputs. This is
   integration preparation, not permission to activate an unaccepted recipe.
3. Exercise no-op, overlay fallback, exact restore, repeat/interruption,
   stale derivatives and stable-ID rename behavior on disposable fixtures.
   Archive placement and live publication remain gated by I2/I5/I8.

User review I10 should identify good/bad initial crops, remaining borders,
head/hair/body loss, useful versus damaged eraser candidates, finishing-crop
trade-offs, enhancement regressions and mistaken Junk decisions. Current v7
is a review instrument: eraser/second-crop candidates and denoise/tone winners
are not automatically accepted. Tune I11/I5 from this feedback before the
I6/I7/I12 live integration and bounded end-to-end sandbox UAT.

## Oct 23 follow-up: begin with recoverable comparison copies

The user authorizes starting implementation and visible sandbox experiments.
Prepare Angel/Sister cores too, **without reassigning them**. First deliver a
bounded sidecar pilot: archive exact input bytes before decoding, render an
oriented control and conservative denoise/tone candidates, and show a local
before/after report. Preserve Gallery/Review files, core membership, metadata,
scenario cache and active action undo. This is experimental evaluation, not
acceptance of an automatic enhancement recipe or the final raw-store location.

Historical uncropped source recovery is deferred and does not block this pilot.
Some originals are available separately; others might be in production or Google
Drive. No old source is assumed lost or recoverable without evidence. The current
crop command has an archive path, but that does not prove a particular image's
uncropped bytes survived. A pilot's retained input may already be cropped:
label its provenance unknown, not pristine. Do not scan old archives or copy
production/Drive photos into the sandbox without an explicit recovery batch.
Recovered originals can enter the later **400+ image** batch. Engine E8's
historical 200+ test is a minimum, not a reason to omit the larger new batch.

### First implementation slice

- [x] **P1 ai** I9 Deliver and verify a sandbox-only preview/apply/check
  launcher for sidecar preparation comparisons, source-hash retention,
  versioned outputs and repeat-safe verification. Include all active category
  inventories, representative cast and other categories, explicit unsupported/
  overlay holds and local report links. No crop, inpainting, upscaling,
  matching, identity changes or original overwrite in this first slice.
  Delivered Oct 23: launcher, schema-validated manifest, exact retained inputs,
  control/denoise/tone pages and per-photo detail/padded views. See evidence below.
- [ ] **P1 you** I10 Review the pilot's control, denoise and tone candidates.
  Label improvements/regressions and overlay/hair cases before enabling a
  recipe, selecting masks/models or publishing prepared sources to galleries.
- [ ] **P1 ai** I11 Prioritize upstream geometric preparation before further
  denoise/tone tuning. Extract/reuse the existing crop planner without its
  Gallery replacement, metadata writes, matching or Review moves; show explicit
  original -> proposed border/UI/background crop or unchanged-with-reason ->
  enhancement candidates -> padded output. Verify subject/hair preservation on
  the 14 incoming test images before recommending crops. Fixed screenshot
  rectangles and face-margin tests are not proof hair is safe. Separate external
  border removal from overlaid-content repair; assess masked cleanup separately
  and pass original with reason when repair is unavailable/unsafe.
  **Partial delivery:** recipe v5 now plans solid outer-border crops upstream,
  shows the reused `screens.clean_box` UI rectangle as a nonrecommended proposal,
  and filters/pads only the border-only candidate. Source preservation is verified;
  general subject/hair safety, face-guided cropping and masked overlay repair
  remain unaccepted. No semantic hair-preservation claim is made.
  Next comparisons must distinguish external UI panels from in-picture graphics:
  first safe per-edge crop -> targeted repair if needed -> optional finishing
  crop -> selective enhancement. Skip repair when the crop suffices; permit
  recorded lower-body/context loss rather than cutting head/hair. Preserve
  intermediate candidates/masks/reasons and explicitly test both `123511`
  and `123318` screenshot cases in the runbook. No repeated blind crop-to-clean loop.
  The user-facing "eraser" is a masked repair attempt. Allow bounded alternating
  crop/eraser candidates with explicit stop/no-improvement reasons; failed
  right-side repair may fall back to a side crop or unresolved overlay.
  Evaluate arms/body/outfit as well as face/hair. Background/flowing fabric
  loss can be acceptable; loss of legs depends on intended use. Retain fuller
  recoverable context and distinguish cleanup recommendations from workflow
  reference selection; padding does not recover removed outfit/pose information.
- [ ] **P1 ai** I12 Complete upstream crop cutover with upkeep U7 after
  preparation/provenance acceptance: replace `library_sync.plan`'s early
  derivative/crop sequence with retain -> prepare -> analyze/assign -> publish/
  normalize -> derivatives -> viewers/selected-input sync. Account for
  `likeness.cmd_crop`, `originals.fit/headshot`, maintained chest rendering and
  viewer screenshot-coordinate adjustments, not just the new sidecar pilot.
  Retire/redirect the old working-source overwrite route explicitly; preserve
  historical crop recovery/undo. Pass accepted geometry/provenance to downstream
  consumers so source cleanup cannot run twice; keep purposeful head/chest
  framing crops. Recompute geometry-dependent face evidence, version recipes,
  and test clean/no-op, overlay fallback, moved/renamed photos, preserved cast
  membership, exact originals, stale derivatives, selected workflow inputs,
  repeat runs and rollback. No implicit production migration or recipe acceptance.
  Oct 24 target: keep exact originals accessible in `gallery_org`, accepted native
  working references in `gallery`, then padded full/head/chest outputs. Reconcile
  existing `*_org` archive housekeeping before cutover; test viewer access and
  original/prepared provenance through rename/move, backup and undo.
- [x] **P1 ai** I13 Deliver a source-preserving per-image processing trace:
  original/cleanup/final summaries; named inputs, outputs, decisions and reasons
  for skipped/attempted/rejected/failed first crop, eraser, second crop and
  enhancements. Gate no-face/too-small-face candidates before transformations;
  detector failure is a separate error, not Junk. Exercise current direct
  Various/gallery files without moving them or assigning identities. Recipe v6
  delivers this bounded review instrument, not I11 recipe/repair acceptance or
  I12/U7 live cutover. Details and preservation evidence below.
- [x] **P1 ai** I14 Add an explicit report-bound early automatic Junk route
  for unregistered incoming files, before any transformations. Default report
  apply stays sidecar-only; the separately requested mode previews, verifies
  exact source bytes and a scoped recovery backup, then quarantines eligible
  no-face/too-small-face candidates with journal and exact undo. Refuse stale,
  linked/escaping paths, collisions, selected workflow sources and registered/
  catalogued identity evidence; report holds explicitly. No deletion or matching.
  Ordinary library runs no longer automatically recheck/resubmit existing Junk;
  retain the later active-photo gate and deliberately requested legacy retry.
  Manual registered-photo Junk/retire belongs to review-actions A9, not this
  loose-intake mover. Verified with focused fixtures and the actual v6 batch
  preview: four eligible candidates, zero holds, no source moves.
- [x] **P1 ai** I15 Record original artist/general source scope in recipe v7
  reports, validate it against paths, and verify identical preparation/padding
  for two artists and general inputs without matching or cross-artist routing.
  Various test copies may remain for nonmatching comparison; actual artist
  intake uses Artists/<artist>/gallery. Shared face-confidence filtering is not
  a species classifier: animal-only/no-human-face candidates stop early, a
  usable human plus an animal is not automatically Junk, and detector failures
  remain errors. Labelled animal false-positive/missed-human acceptance remains
  in I3/I5; live shared preparation and crop replacement remain I6/I12.
- [x] **P1 ai** I16 Split likeness entry-point setup, not the engine:
  `likeness.cmd` discovers general roots only; `likeness-artists.cmd` uses
  Artists only, with distinct default caches/history/report names. Share
  preparation, detector/embedding weights, crop/Junk algorithms, grouping and
  derivative code. Enforce source/destination and legacy-undo boundaries before
  any moves, including forced/cast-return paths; do not move existing trees or
  silently transfer known artist-origin photos from the general pool.
  Wire both routes in the library orchestrator, help/menu and checks. Verify
  path isolation, same-artist grouping, scope-local centering, stale mean
  diagnosis, read-only preview, guarded downstream originals and exact source/
  catalogue/cache preservation in sandbox. Recipe acceptance/crop cutover
  remains I5/I6/I12, not completed by this setup split.
  Delivered: artist wrapper plus domain setup/write guards, shared engine,
  scoped originals, separate artist index, library orchestration/help/menu/
  check wiring. Artist scoring is independently centered, so old all-library
  thresholds still require labelled acceptance; no claim of identical old
  cross-domain scores. New clean general caches carry their mean's domain.
  Ordinary content embeddings remain reusable; unstamped or mismatched saved
  means are diagnosed. Family preview still does not mutate library/cache.
- [x] **P1 ai** I17 Complete the general/Artist boundary in people overview
  and Review generation, including directly supplied scoring spaces and shared
  report callers. Exclude Artists from general discovery, centering, closest
  matches, rankings and relationship presentation, not merely visible cards.
  Replace the legacy opt-in Artist inclusion with an explicit diagnostic;
  no silent ignored flag or mixed scoring. Test direct and orchestrated paths
  on fixtures without processing current Various/gallery. Separate basic Artist
  browsing is now authorized under layout L14 (17:29 follow-up), not new matching
  rules or automatic intake permission.

**I17 delivery:** normal overview/Review callers activate general-only,
read-only scoring. Mixed supplied spaces and legacy `--artists` inclusion are
explicitly refused. Shared maintenance/routine launchers no longer request
mixed pages. Separate Artist browser L14 uses only existing Artist sources and
cached informational face results; no inference, assignment or current Various
processing. Full quick validation passes 26 suites / 631 tests plus 19/19
mutations. Browser/storage/preservation evidence and the latest raw user
authorization live in the [layout owner](2026-10-22-gallery-review-layout.md).

**I16 verification:** actual artist preview/check and general dry-run scan ran
against the existing sandbox scenario cache without rewriting it. Artist
inventory: 279 photos, 246 usable; `--check` exits 1 for 33 unusable photos.
General inventory: 2,457 photos, 2,344 usable. These inventory totals are not
quality acceptance. Captured 6,167 source/state records remain unchanged;
no category additions or new `_likeness` directory, and `_origins.json`
metadata unchanged. Focused source/discovery/centering/move/Junk/undo/
downstream-originals tests pass. Final quick launcher passes 25 suites,
609 tests and 19/19 validator mutations (native exit 0). No actual matching
apply, source moves, production operation or ComfyUI retargeting ran.

**I14/I15 verification:** 47 preparation and 11 routine tests pass; initial parent
integration separately passes 93 action/retirement/review/metadata tests.
Final `bin\validate.cmd --quick` passes all 25 suites (593 tests), including
the expanded action integration, plus 19/19 validator mutation cases with
native exit 0. Markdown lint and whitespace checks pass.
New sidecar-only report
`Working\_reports\preparation\incoming-scope-20261023-v7\index.html` contains
113 current inputs: 109 processed, four early Junk candidates. All three
summary views and five-stage traces remain; original artist/general scope and
detector/species limitations are now explicit. All 6,167 captured source/state
records are unchanged; all 114 HTML pages have valid local links, 794 padded
outputs are exactly 944x1104, and repeat preserves all 2,609 report-file hashes
and mtimes. The v6 report still checks. Actual Junk preview lists four moves,
zero holds; no actual source moves, identity assignments, production changes,
ComfyUI operations or action-undo settlement ran.

I9 is bounded implementation supporting I1/I3/I4/I8, not completion of them.
I2 still chooses durable independent raw storage and verified restore policy.
The first run's exact-byte retained copies are recovery evidence for that run,
not a replacement for an independent backup.

### Comparison views and quality decisions

The first pilot page compares an oriented control, denoise and tone alternatives;
click a photo to see the retained current input, larger candidates and their
separate padded 944x1104 examples. All are sidecars. A future verified uncropped
source is an additional role, not a relabel of the current Gallery input.
[Layout L12](2026-10-22-gallery-review-layout.md) owns linking these views from
the existing people pages after the accepted provenance manifest is integrated.
No current gallery/report refresh is required to open the sidecar pilot.

**No-op is a first-class outcome:** a clean image should not be filtered or
cropped just because it is in a batch. The pilot compares alternatives on a
sample for evaluation only; it does not select or install one. I5 must approve
issue-specific triggers and measurable safeguards before automatic operations.
Keep native prepared source separate from downstream padding, always done for
the standard 944x1104 display output.

**Failure is not successful cleanup:** preserve the input, report the attempted
operation and reason, and retain the last accepted source. If that unchanged
source is still suitable, an explicit unchanged-with-warning result can use it.
An overlay or failed/rejected enhancement does not itself hold a readable image
or require manual intervention. Continue with the unchanged original and an
explicit reason so ComfyUI can do later cleanup. Truly unreadable/corrupt inputs
remain errors, not successful originals. This Oct 23 clarification supersedes
the earlier proposal to hold unresolved overlays for manual repair.
Detected regressions reject the candidate; quality heuristics alone cannot prove
identity preservation or reconstruct missing hair. Thresholds, triggers and
publication safeguards remain I5 decisions; original fallback for usable images
is now approved. No-op and fallback both
retain provenance; they are not an excuse to skip protected-core processing.

**Gallery attributes:** record original versus enhanced separately from
matching/membership confidence. Display a reason such as clean original,
overlay left for ComfyUI, enhancement failed/rejected, or enhanced with recipe.
Do not label an unassessed photo clean. The comparison pilot now records
`sourceTreatment` (including `original-unassessed`, `original-overlay-unremoved`,
`original-enhancement-failed`) and shows it on overview/detail pages. New
comparisons use recipe v3; the existing `-03` report is immutable v2 evidence.
Existing manifests remain readable. Ordinary people-page wiring stays with L12.
In v6 filter failures retain the last safe cleanup selection with diagnostics;
earlier recipes retained control/original. Storage/verification
failures still stop publication rather than conceal missing recovery evidence.

### Pilot delivery evidence (Oct 23)

**Staged-processing follow-up (v6):**
`Working/_reports/preparation/incoming-trace-20261023-v6/index.html`
captures all 113 direct incoming photos present at apply time (the user added
files after the earlier 14/92 previews). All remain in place.

| Result | Count / interpretation |
| --- | --- |
| Face gate | 109 usable by the limited face-size test; four report-only Junk candidates (two no-face, two minimum face dimensions below 60px) |
| First crop | 86 provisional selections; 27 skipped, including all four Junk candidates |
| Eraser | 95 local mask/Telea previews, all rejected for automatic use; 18 skipped |
| Second crop | 72 right-edge previews from last selected input, all rejected pending body/outfit safeguards; 41 skipped |
| Denoise/tone | 109 comparisons each from selected cleanup; four skipped each; no automatic enhancement winner |
| Summaries | Original -> cleanup recommendation -> final source recommendation; final retains cleanup pending calibration, not a fabricated quality score |

No-face cases are `Screenshot_20260902_203835_Facebook.jpg` and its `(1)` copy.
Small-face cases are `Screenshot_20261010_123425_Facebook.jpg` (56.34px) and
`various_image_7517986669563913378.jpg` (56.78px). These are usability flags,
not deletion, subjective retirement, or proof a human face can never be found.
No Junk candidate receives crop/eraser/enhancement/padded candidates.

The two motivating screenshots now differ: `123511` selects
`[0, 326, 1080, 1688]` (top/bottom external panels); `123318` selects
`[0, 0, 1080, 2016]` (bottom panel only, hair-overlapping top retained).
Direct candidate inspection shows incomplete/artifact-prone erasing in `123511`,
supporting its nonselection. No general eraser, hair restoration, bottom
finishing-crop search or body-aware automatic acceptance is claimed.

Verification: 38 focused tests pass; 6,167 captured source/catalogue/scenario/
category records unchanged, including exact retained bytes/names/mtimes of
all 113 inputs. All 114 HTML pages' references resolve inside the report;
all 794 padded examples measure 944x1104. Exact repeat preserves hashes/mtimes
of all 2,609 report files. Local face detection uses the already-installed
model only, with its hash recorded. No recognition, matching, moves, Source/
production edits, action settlement, model download or workflow retargeting.
Required quick validation passes with native exit 0, including all 19 mutation
cases; Markdown lint, generated queue and whitespace checks pass. A first
PowerShell stderr-redirection capture misleadingly returned 1 despite passing
suites; subprocess-native exit capture confirms success in the retained log.
I10 remains user review; I11 remains broader method/calibration acceptance.

**Upstream geometry follow-up (v5):**
`Working/_reports/preparation/incoming-geometry-20261023-v5/index.html`
compares the same 14 incoming files without moving/replacing them. One qualifies
for conservative solid-border trimming; 13 retain original geometry. Eight show
the legacy fixed screenshot crop separately, never recommended or fed to filters.
The report exposes coordinates, unchanged/risk reasons, recommendation links,
four native candidates per photo plus eight UI proposals, and 64 padded views.
This is not general screenshot cleanup: overlays within the picture remain,
and the narrow detector missing an overlay is not proof the picture is clean.
The original is recommended when no strip qualifies or enhancement fails;
otherwise the border-only candidate is a provisional recommendation, not
a measured quality winner or proof of subject/hair preservation.

The only provisional border recommendation is
`Screenshot_20261010_123511_Facebook.jpg`: `[0, 34, 1080, 2340]`,
yielding 1080x2306 (34 top pixels removed; two-pixel guard retained).
It does not reconstruct hair or remove other screenshot graphics.

Verification: 30 focused tests; exact bytes, names and mtimes of 14 inputs
unchanged; catalogue and seven saved scenario files unchanged; 5,945 active
category file paths/sizes/mtimes unchanged. All 15 HTML pages' local references
resolve inside the run, all 64 padded views measure 944x1104, and repeating
the exact apply leaves all 222 output hashes/mtimes unchanged. Earlier v2/v4
reports still pass read-only checks. No matching, Gallery replacement, action
settlement, model download, production/Source or ComfyUI operation ran.
`bin\validate.cmd --quick` passes, including 19/19 mutation cases;
Markdown lint and whitespace checks pass.
I11 remains open for broader geometry/overlay acceptance; I10 owns visual review.

**14:03 incoming-only follow-up:** a separate report at
`Working/_reports/preparation/incoming-overlays-20261023-1403/index.html`
uses only the 14 direct `Various/gallery` images, preserving filenames,
bytes and placement. Eight trigger the narrow reel-overlay heuristic; six
do not (not proof they are clear). The report defines original/control/
denoise/tone/padded roles and explicitly recommends the original as a
conservative default, not a measured winner. No crop/overlay repair ran.
`--source-folder "Various\gallery" --limit 0` provides repeatable scoped runs;
recipe v4 adds labelled recommendations. Incoming geometry is now I11's first
priority: this comparison-only run is not completion of the requested cleanup.

Earlier all-category report: sandbox `Working/_reports/preparation/intake-pilot-20261023-03/index.html`.
Use this run for the 28-photo baseline, not the earlier development comparisons `-01`/`-02`.
Recipe `preparation-comparison-v2` strips copied EXIF/ICC metadata **after**
orientation and embedded-profile conversion to sRGB. The original byte copy
keeps all metadata. A real profiled-image check exposed generated ICC timestamp
differences between independent controls; the fix produces equal control hashes
across delayed decodes. New recipe refuses to overwrite an older run.

| Check | Evidence / limit |
| --- | --- |
| Active inventory | 2,699 Gallery/Review images: 494 Angels, 827 Sisters, 154 Models, 737 Prospects, 187 Potentials, 279 Artists, 21 Various |
| First sample | 28 photos, four per category; cast preparation included with no reassignment; not all-image completion or a user-labelled benchmark |
| Views | 28 exact inputs, 84 native candidates, 84 padded 944x1104 examples, thumbnails, main page and 28 detail pages |
| Outcomes | All 28 compared; none flagged by the narrow reel heuristic. This does not show overlays are absent or successfully removed |
| Preservation | Selected source hashes plus all active image path/size/mtime records and catalogue/scenario policy/cache/history hashes unchanged |
| Repeat | All 310 report files retain identical paths/hashes/mtimes when repeating the exact run |
| Validation | Focused preparation tests and `bin/validate.cmd --quick` passed, including 19/19 mutation cases; per-photo links and padded dimensions checked |
| Browser boundary | Integrated browser refused this B-drive file as outside trusted folders; automated link/hash checks are not visual acceptance |

The sample's three-way native/padded generation took about 24 seconds of recorded
variant work; not an all-library runtime estimate. It uses installed Pillow,
NumPy and OpenCV locally, no GPU model or new dependency. No quality selector,
face-feature recalculation, overlay repair, crop detector improvement, independent
raw-store rollout, Gallery publication or people-page integration is delivered
by I9. I1-I8, I10 and layout L12 remain open.

## Purpose and order

Own archive-before-processing, practical local cleanup, matching-input provenance
and measured acceptance. This is upstream of identity assignment, not an extension
of ComfyUI character generation. The [phase order](README.md#current-library-work-order-oct-23)
is authoritative for scheduling; a P1 task in a later phase does not jump this gate.

| Phase | Owner | Exit needed here |
| --- | --- | --- |
| 1 | This plan | Accepted preparation recipe, source recovery, labelled image/matching evidence |
| 2 | [Library upkeep U1/U3/U6](2026-10-22-library-upkeep.md) | Prepared-source derivatives, naming, stale-output cleanup and recovery |
| 3 | [Cast-seeded rebase](2026-10-23-cast-seeded-library-rebase.md) | Repeatable all-image sandbox trial with explicit cast seed policy |
| 4 | [Engine acceptance](2026-10-22-likeness-engine-acceptance.md) | Clean/incremental acceptance, then separately approved production |

Actions, family naming and advanced prompt migration remain live, but broad UAT
must not validate a moving intake baseline. No plan is retired merely because
its implementation order changed.

## Observed current flow, not the target

Inspected Oct 23; current changes include tested but uncommitted maintenance code.

| Surface | What it does / gap |
| --- | --- |
| `library_sync.plan` | Originals naming/scaled/head outputs, duplicates, crop/Junk, shared reconciliation, artist grouping, empty retirement, originals/check, input sync and reports; some derivatives precede matching and others follow it |
| `likeness.cmd_crop` / `screens.py` | May replace working photo with an archived-original crop; fixed screenshot rectangle and face-relative hair margin are not full hair protection; no masked overlay repair |
| `engine.Embedder` | OpenCV YuNet face detection, SFace aligned face features and normalized vectors; large images capped at 1600 maximum dimension for detection; not whole-body identity recognition |
| Clean rebase | Separate fresh-cache cast-seeded planning path, not the normal housekeeping sequence; currently retains cast Gallery photos rather than implementing the new seed-release experiment |
| `gallery_maintenance` / `derivatives` | Normalize folder prefixes, maintained padded/head/chest outputs, derivative-backed viewer; no matching or general enhancement stage |
| Recovery | Narrow action snapshots plus verified regenerable omissions/full option exist in current work; not immutable archive-on-receipt or accepted all-image preparation |

Code references: [routine](../../tools/art/library_sync.py),
[cropper](../../tools/art/likeness.py), [screenshot helper](../../tools/art/screens.py),
[face engine](../../tools/art/likeness_library/engine.py),
[rebase](../../tools/art/likeness_library/clean_rebase.py),
[maintenance](../../tools/art/gallery_maintenance.py).
The earlier dual-input write-up was the wrong source for this request.
The complete supplied enhancement note is preserved below.

## Proposed sequence and boundaries

The [agreed flow and installed crop-path inventory](../art/original-photos.md#agreed-end-to-end-flow-and-current-cutover-boundary)
is the runbook home for the Oct 23 clarification. I12 owns retiring the old
source-cleanup path; upkeep U7 owns its derivative/workflow boundary. Head/chest
framing is intentionally retained. The 944x1104 files, not native Gallery
references, are the user's normal ComfyUI inputs; preserve explicit selections.

1. Discover incoming bytes; hash and verify an independent immutable source
   archive before any image transformation or quality disposition. Preserve
   original basename/import provenance and stable photo ID. A generated derivative
   or action backup is not this archival source.
2. Decode, orient and assess screenshot/border/overlay, face visibility, blur,
   exposure and corruption. Preliminary detection may locate safe regions; this
   is not assignment to an identity. Quarantine unrecoverable/uncertain files
   recoverably; lack of a detected face alone is not automatic deletion.
3. Prepare a versioned native-detail working image: first safe per-edge crop of
   external panels/borders; targeted overlay repair only if needed and validated;
   optional finishing crop if repair leaves expendable lower/side clutter;
   then issue-specific benchmark-approved enhancements. Distinguish external
   bars from text/icons over hair/face. Preserve head/hair over lower-body
   coverage, record any context loss, and skip unnecessary operations. If repair
   is unsafe/unavailable, preserve the last safe content with an unresolved-overlay
   reason for ComfyUI rather than cutting the head or claiming successful repair.
4. Produce a conservative analysis view and record its source, recipe and bytes.
   If a display repair reconstructs identity-sensitive pixels, do not silently
   use those pixels as trusted matching/core evidence. The fallback/hold rule is
   explicit, not a success-shaped substitution.
5. Compute fresh detection/alignment/features for that analysis view, freeze the
   run's core evidence and run the shared matching/grouping/classification policy.
   Names never seed matching. Compare raw/prepared results before authorizing moves.
6. Publish the accepted prepared working source into Gallery/Review; preserve the
   raw-source link, stable ID, histories, protection and transformation record.
   Then normalize destination-folder names and generate standard padded/head/chest
   derivatives from that prepared source, followed by viewer thumbnails/index.
7. Advanced object/face reconstruction, full-body extension, artistic lighting and
   character styling remain in `0_Edit`/`1_Alpha`; no workflow retargeting occurs
   merely because an intake candidate looks improved.

Preparation should precede standard canvas padding: padding/upscaling is not
recovered detail. Native-resolution safe cleanup precedes optional evaluated
super-resolution; final analysis resize and display derivatives are explicit
consumers. One standardized decision policy may choose different operations for
different quality classes; it must not blindly denoise/color-correct every image.

All existing categories, including retained Angels/Sisters and protected photos,
must receive a preparation outcome: prepared, unchanged because already valid,
original fallback with reason, or unprocessable with reason. Membership protection is not an
image-processing exemption, but it does not authorize destructive source edits.
Existing sources that were previously cropped may not be pristine; inventory
recoverable originals and flag missing raw provenance, never claim new copies
recover already-lost hair or detail.

## Decisions to settle at their gates

| ID | Recommendation / open decision | Gate |
| --- | --- | --- |
| I-D1 | Independent content-addressed raw archive plus manifest; choose physical storage/backup placement and capacity after inventory | Before archival migration/apply |
| I-D2 | Conservative deterministic matching view; generative hair/face repairs remain separate review candidates unless independently validated | Before analysis-input change |
| I-D3 | Select enabled algorithms/strengths from measured local pilot, not all tools below | Before recipe activation |
| I-D4 | Agree acceptable visual/matching errors and runtime/disk limits on labelled cases; no invented universal score/latency target | Before rollout |

Ask one decision at a time when needed. These are proposals, not installed rules.
No model downloads, new dependencies, commercial-use assumptions or cloud uploads
are authorized by preserving the notes.

### Existing-scope reconciliation

Artist plan A5's optional local detection/masking comparison transfers to
I3-I5 (not delivered); [Artist A4](2026-10-12-artists-reset-and-auto-crop.md)
retains wing/pose-specific acceptance. Reuse tooling D5's detector work
and engine E2's existing root/caller inventory; do not build duplicate
detectors, matchers or input routines.

## Local tool shortlist to evaluate, not selected dependencies

| Candidate | Bounded role | Risk / required evidence |
| --- | --- | --- |
| Existing Pillow + NumPy | Orientation, masking, geometry, consistent encoding, conservative tone operations | Preserve color/EXIF policy; resize alone does not enhance identity detail |
| [OpenCV](https://github.com/opencv/opencv) | Border/mask heuristics, conservative denoise, local contrast, small-mask classical inpainting | Verify exact APIs/settings; hair/skin reconstruction can smear or change evidence |
| [scikit-image](https://github.com/scikit-image/scikit-image) | Compare deterministic denoise/exposure methods against existing tools | Add only if measured benefit justifies another dependency |
| [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) | Optional restoration/upscale candidate; project documents a Windows Vulkan executable | Benchmark actual hardware, tile/memory/time, checkpoint rights and hallucination; not automatic facial truth |
| OCR / segmentation / inpainting candidates | Detect UI text and subject/hair overlap; trial constrained repair | Detection is not reliable reconstruction; select model/weights/licence only after capability review |

Upstream project pages checked Oct 23. This is not a model/licence/hardware
certification. Classical methods can start CPU-first; inspect the user's actual
CPU/GPU/VRAM/free disk before promising whole-library runtime. GFPGAN-style face
restoration and diffusion repair are not default matching preprocessing.

## Work and acceptance

- [ ] **P1 ai** I1 Inventory all supported sources, current crop/Junk/preparation
  entry points, raw recoverability, cache keys, outputs, backups and ComfyUI
  consumers. Record disk/count estimates without scanning old backups as intake.
  Include Gallery, Review, Artists isolation and duplicate/import replacements.
- [ ] **P1 either** I2 Resolve I-D1, specify archive verification, stable-ID to
  raw/prepared/version lineage and recoverable Junk. Design rule -> schema ->
  validator/tooling -> implementation -> tests. Never overwrite immutable input.
- [ ] **P1 ai** I3 Assemble a labelled read-only pilot: text over hair/face,
  external black bars, atypical screenshot layouts, long/tall hair, tilt,
  multiple faces, low light/noise, blur and clean controls across categories.
  Verify expected protected subject regions with the user before automatic crops.
- [ ] **P1 ai** I4 Benchmark shortlist locally on pilot copies, recording
  algorithm/model/weight version, license evidence, CPU/GPU/VRAM, timings and
  disk, masks, crop coordinates and before/after images. Compare no-op and
  conservative alternatives; do not promise removed overlays restore real detail.
- [ ] **P1 either** I5 Choose I-D2/I-D3/I-D4 from side-by-side visual review
  and labelled detection/matching metrics. Measure missed detections, false
  matches, fragmentation, holds and identity/hair/detail changes separately.
  Use [face-analysis M1/M2](2026-10-22-face-analysis-evaluation.md), not body
  resemblance, current folder names or cosmetic appeal as identity truth.
- [ ] **P1 ai** I6 Implement accepted preparation through shared clean/incremental
  entry points, preview/check/apply launchers, explicit errors, resumable jobs
  and atomic publication. Idempotence keys raw hash + recipe/model/settings,
  not existing identity membership; recipe changes trigger explicit migration,
  never repeated enhancement of an already enhanced copy.
- [ ] **P1 ai** I7 Wire accepted analysis/prepared/display hashes and recipe
  into caches/manifests, original/prepared/repair views and diagnostics. Recompute
  cast and candidate features in the same versioned space; invalidate centering/
  scores when analysis changes. Report-only refresh cannot reassign membership.
- [ ] **P1 either** I8 Verify archive restore, interrupted/repeated runs,
  derivative/embedding invalidation, manual edits, stable IDs and active-action
  recovery; document accepted source handoff to Phase 2 and run a bounded UAT
  before Phase 3. Every photo gets an explicit outcome; no silent exclusions.

## Feedback coverage

| Source request | Disposition |
| --- | --- |
| End-to-end current versus improved order; before identity matching | Current-flow table, sequence, I1/I6/I7 |
| Independent original archive immediately on receipt; restore | I-D1, I1/I2/I8 |
| Denoise, resolution, color, background/overlay cleanup and open-source tools | Shortlist, I3/I4/I5; no blanket quality promise |
| All existing categories, local capacity, batch automation | All-image outcomes, I1/I4/I6; Phase 3 owns membership |
| Process once; new versus already identified files | Source-hash/recipe idempotence in I6; identity ID alone is insufficient |
| Junk before routing, documentation and simplified routine | Sequence, I2/I6/I8 |
| Hair preservation and limited intake versus advanced ComfyUI | Protected-region pilot and analysis/display separation |
| Begin sandbox comparisons now; cast cores processed without reassignment; recover originals later / 400+ batch | I9/I10 and follow-up boundary; Phase 3 release is separate; engine E8 accepts larger batch |
| Original/prepared/padded comparison and image-detail view | I9 pilot views; layout L12 for people-page integration |
| Already-good no-op, conditional operations and explicit failure/fallback | I5/I6 quality decision policy above; no automatic publication in pilot |
| Account for existing Gallery crop code; upstream cleanup followed by naming, standard full/head/chest outputs and selected ComfyUI inputs | I12 and upkeep U7; runbook owns full flow and installed-path inventory; cutover not yet delivered |
| Intelligent first crop, targeted magic-eraser-style repair, optional final crop; head/hair prioritized over lower-body coverage; two screenshot examples | I11 comparisons and runbook case observations; experimental method/threshold acceptance remains open |
| Per-image attempted/skipped steps, three summary images, recommended cleanup fed to enhancements, final generation-source recommendation | I13 v6 report instrument; I10/I11 user tuning and method acceptance remain open |
| Skip work on incoming no-usable-face Junk candidates | I13 face gate and separate detector errors; I14 optional automatic quarantine with retained backup/journal/undo |
| Auto-Junk early; keep later backstop; Junk stays out, retirement can return | I14; runbook and curation contract semantics; review-actions A9 owns registered manual Junk and existing photo retirement |
| Artist/animal/noisy screenshot intake uses same preparation but no mixed identity pool | I15 source-scope contract and tests; I3/I5 labelled animal false-detection acceptance; I6/I12 live integration |
| Separate artist likeness setup/entry point while sharing intake and engines | I16; canonical entry-point/state/write/recovery boundaries in likeness guide; no new engine or physical tree migration |
| Keep Artists out of normal people galleries/relationships; separate simpler Artist GUI later | I17 completes general scoring/report isolation; layout L13/L14 own presentation boundary and deferred GUI |
| Do not process Various/gallery until Artist test images are removed; identify work during review | 17:05 handoff/pause above; I10 visual feedback, I17 isolation, I1 inventory and fixture-only I12/U7/I8 preparation |
| Write today's recap and keep plans updated during work | [Oct 23 recap](../recap/2026-10-23-1708-recap.md); existing plan-at-each-pivot agreement retained, queue regenerated for this handoff |
| Keep every intake version in `gallery_intake`, move with the identity; original to `gallery_org`, best to `gallery` | I21; U7 owns the `archive_org` reconciliation |
| Link from the gallery review to a page with every version of one photo | I23 through layout L12 |
| Run intake only, review, then redo or resume | I22 |
| `Various\[person name]\gallery` becomes that identity | Delivered `likeness seed` (library step 0); I24 user verification and protection decision |
| Did we verify the recommendations; best/fully cropped not picked | Oct 24 section: honest answer, v14 selection, v14c visual table, I25 |
| Crop what we can, erase, crop once more to center the person and trim background | v15 composition step (delivered, sandbox); I25 tighter framing |
| Few edge cases; steps runnable alone or combined, named person included; Various as the one drop point | "Simple, composable flows" principle; I22; `likeness seed` as step 0 |
| Directory structure focused on females; future males, animals; reckoning | I26 proposal and decision |
| Eraser result lost by the second crop; second crop cuts hands; inspect the series and adapt | v16 section: second crop before the eraser, person-mask guard, LaMa, limb rule; I27 gaps; I29 review |
| Remove or isolate legacy pipeline code; modular pieces; decide where unsure | v16 section: `intake_library` package, `legacy.py`, removed geometry; I28 |

## User feedback (verbatim)

Source: `feedback/image_enhancement_cleanup_thoughts.md`, received Oct 23, 2026.

<!-- markdownlint-disable MD013 -->
```text
Before we get too far into some of the actions, I also want to understand more about the potential clean-up we can do with images as we run the likeness process, such as removing background noise, enhancing resolution, and correcting color imbalances. This will help ensure that the images we work with are of the highest quality and consistency prior to running them through the likeness evaluation.  We're already doing the cropping and padding and upscaling, but additional enhancements could further improve the image quality.

We've already put some thoughts into the work on this - but I just realized now that our flow might be dis-jointed in how we're doing the cropping/padding AFTER it lands in a gallery and am thinking maybe we should consider reordering the steps so that cropping, padding, and other enhancements happen before the images are added to an identity.  

Also - we probably would want to have a backup of the original files somewhere safe before any processing takes place, so that we can always revert to the unaltered versions if needed.  I don't know how we'd want to think about that and whether or not we keep the originals alongside the processed versions or move them to a separate archive.  It feels more like a separate archive would be the safer approach, ensuring that the originals are preserved independently of any processing that occurs.  So, new images get archived immediately upon receipt, before any enhancements or likeness evaluations are performed.  Then the enhanced versions are fed into the process and what lands in the gallery is the enhanced original, then the 944x1104 variations can be created from that enhanced original.  

But we're doing that AFTER the images are processed by the likeness comparison - so we need to re-think the sequence of operations to ensure that images are enhanced and cleaned up before they are evaluated for likeness.  Then we can generate the 944x1104 images from the already enhanced and cleaned-up originals, ensuring the highest quality for the final output.  Unless it makes more sense to first generate the 944x1104 images and then apply the enhancements, but that could potentially limit the effectiveness of some enhancement techniques.  So I want to know what you think is the best sequence, set of tools and how we can simplify the process.

Additionally, it would be beneficial to establish a standardized workflow for image enhancement and clean-up, so that every image undergoes the same level of processing. This could include steps like automated noise reduction, resolution upscaling, color correction, and even manual touch-ups where necessary. By doing this, we can minimize variability and improve the reliability of our likeness assessments.

I'd like to know what open source libraries or tools are available for image enhancement and clean-up. This could include libraries for noise reduction, super-resolution, color correction, and other image processing tasks. Understanding the available options will help us choose the most effective tools for our workflow.  I feel like this is a foundational piece we'd want to establish now since we're doing the rebase testing and I'd actually like to run all the existing sisters, angels, models - all identities through a clean-up if we can figure out that it's plausable and would run on my machine.  

I am using ComfyUI to clean-up and enhance images - but if the likeness process can handle some of these tasks automatically, it would be helpful to understand its capabilities and limitations. This will allow us to determine which steps need to be performed manually and which can be automated within the likeness workflow.  It can do it at scale where comfyui requires me to run them one-by-one.  If we can effectively clean-up, crop, and enhance images automatically within the likeness process, it would save significant time and effort in the long run - even if it runs slower to start.  Once an image is enhanced and put into an identity we would not need to re-run it through, so it's really just the images that are new and we don't already have an identity id established for that file.  

Finally, it would be useful to document the entire enhancement and clean-up process, including the specific techniques and tools used at each step. This documentation will serve as a reference for future projects and help maintain consistency across different teams and iterations.

In summary, by focusing on image clean-up, establishing a standardized workflow, and thoroughly documenting the process, we can significantly improve the quality and reliability of our likeness evaluations. This structured approach will ensure that all images are processed consistently and meet the required standards before being assessed.

Sorry for getting distracted and a long winded explanation, but I wanted to make sure I captured all my thoughts on the image enhancement and clean-up process.  It's clear that we do have capabilities to enhance images already so doing that first seems to make the most sense and in that initial process we could then address junk images and move them out before running the likeness process.  

I'd want you to think deeply about the end-to-end flow of the process since you've just worked on fixing up the gap in the generation of the 944x1104 images in the sandbox and now we can step back and document the existing flow and image processing from end-to-end in current state and then write up a proposed sequence for the optimized workflow, incorporating the enhancements, clean-up, and likeness evaluation steps in the most efficient and effective order.
```
<!-- markdownlint-enable MD013 -->

Oct 23, 23:01 oval-position clarification (verbatim).
Coverage: outlined shape detection in I18; measured-boundary top cropping,
head-clearance refusal and unchanged recommendation semantics in I20/v13.

<!-- markdownlint-disable MD013 -->
```text
The top "find another reel" across the hair and head is the most difficult to get rid of, but it's mainly "white and an oval in place" fairly consistently that should be able to be masked out or cropped, depending on where it is present in the image.
```
<!-- markdownlint-enable MD013 -->

Oct 23, late: version sets, intake-only runs, named folders (verbatim).
Coverage: I21 version sets and `gallery_intake`; I22 intake-only stop/resume;
I23 all-versions page; delivered `likeness seed` plus I24 verification;
recommendation honesty, v14 selection and I25 in the Oct 24 section above.

<!-- markdownlint-disable MD013 -->
```text
As we do the crops and other enhancements, I'm wondering if it'll make sense to keep them along side the gallery where the image lands as well or where would be the best place to keep them along with the renamed image that ends up in the gallery under the person?  If I think about the end-to-end pipeline these are just the first steps in getting a clean gallery image we can then run into the face comparion and identity assignment.  I don't want a flood of images, but it seems like after it's assigned to an identity that I might want to be able to see all versions of the image that went through the entire process.  I'll have to see what that does for disk space, but if we don't have to crop and erase many of them, then we won't have an exposion of them.  Maybe they would be in a gallery_intake or something instead of just thrown away.  Since these are in various to start - they can reside there until we get an identity assigned then move them along with the original to stay in gallery_org and which ever one is the "best/recommended" would end up in the gallery to genreate the 944x1104 based images automatically.  That would mean that we would want the ability to have a link in the main gallery review that shows all the images to also pull up a page that has all the crops, enhancements - the full set of images tied to that one image so I could always review them all - especially when we run the full likeness process form end-to-end and aren't just reviewing the results of intake processing, but will let the identity be assigned.  What do you think of that?  If you agree - update the related plans and you can get to work on that.  That way we don't just have to focus on the intake - but get ready to run the full end-to-end process on those images in various and see how it all fits together tomorrow.  Also - we should be able to run just the intake process and stop there with everything in various and review things there and then either do it all over or be able to resume from there.  I also want to make sure that the likeness process can handle if I drop another various/[person name]/gallery into the process it can handle using the [person name] as the identity and that all the images in there "should" be that person since I either took those or know that they are all the same person.  That's another feature and it worked early on with the process - but since we've done so many updates that could be lost and we need to recover that as I have some images of a few people I want to validate that with after we run the rebase all over again and get the sandbox galleries all cleaned up with all these intake enhancements.  Also, did you actually verify the results of the erasing, cropping and recommended photos after - as sometime it wasn't recommendeding the best one or at least wasn't picking a fully cropped version when I checked prior to these latests updates you did.   
```
<!-- markdownlint-enable MD013 -->

Oct 24 follow-up: crop sequence, simple flows, directory reckoning (verbatim).
Coverage: v15 composition; composable-flow principle and I22; I26.

<!-- markdownlint-disable MD013 -->
```text
Did you also implement the cropping suggestion I provided as well - so the series of crops, erase, crop  -- or whatever sequence provides the best approach to get to the best photo the fastest.  Basically want to make sure we crop away what we can, erase the things we can, crop one last time to get the person centered in the picture and trim additional background, etc... I didn't give approvals on that, but that's also all the right things to do in the intake.  The other part is we don't want to make too many edge scenarios in the flows and keep them so they can be run properly in steps or in a combined flow as we test - including the "named person" aspects of the flows.  In the past, I could actually drop them anywhere into the process, but I am fine if it's all through Various as the comming intake gallery holding.  In fact, we can probabaly look at the directory structure and refine it when it makes sense if you have recomendations on that as well - because what we have is focused on females - but we need to support males, animals, etc... in the future.  So there will be a directory reckoning that needs to happen as well.
```
<!-- markdownlint-enable MD013 -->

Oct 24, 23:08: eraser and second-crop tuning (verbatim).
Coverage: v16 section above (second crop before the eraser, person-mask
guard, LaMa fill on the second-crop output); I27 remaining gaps.

<!-- markdownlint-disable MD013 -->
```text
I noticed that sometimes the eraser works well, but on the second crop the icon is back and the second crop is too close and remove hands and such.  So, there's definitely tuning that needs to happen in terms of the output of the eraser and why it doesn't look like it was used and sometimes it works well sometimes not.  So you should inspect the series and adapt the logic so it's working optimal and I don't have to find the issue you can spot already by looking at what is happening in the series of steps.
```
<!-- markdownlint-enable MD013 -->

Oct 24, late: remove or isolate legacy pipeline code (verbatim).
Coverage: v16 section above (`tools\art\intake_library\` package, `legacy.py`,
removed geometry helpers and tests); I28 deletes `legacy.py` with the last old report.

<!-- markdownlint-disable MD013 -->
```text
Finally - if there are things in the pipeline cluttering it up we no longer will need and we can remove them to simplify things, that's fine - just like we split Artists out we can either isolate things that were legacy functionality and/or remove them.  The new end-to-end flow is what we want and we don't need to carry things forward we don't need or should split them into other commands we can deprecate and eventually remove.  Trying to break the code down into more maintainable and modular pieces so we can discard things easier and reduce the complexity is one of the finals aspects we need to work on as well.  So go ahead and do all the things we just discussed and you agree with - things you a unsure on, make a decisision and we can review the final results tomorrow.
```
<!-- markdownlint-enable MD013 -->

### Related chat (verbatim)

Received Oct 23, 2026. The last message requests the planning/archival pass;
its cast rebase scope is owned by Phase 3, not a second checklist here.

<!-- markdownlint-disable MD013 -->
```text
Ultimately the question is - what can we do during the likeness process to enhance and cleanup images during the initial intake of an image before I look to pull it into my ComfyUI workspaces and do the advanced workflows with them.  In my ideal world, we'd be able to clean-up screenshots that have overlays and cropping the areas is a last sort for the top/head when it's on overlay on the image instead of a black border.  This is important for ones where the hair would get cropped otherwise (which does happen now).  So I understand it's a complex scenario and there's a balance of just how much initial cleanup, enhancements, lighting, etc... we can do simply vs. the advanced work in ComfyUI that would be used in 0_Edit and 1_Alpha workflows to do the final clean-up extend the view to full body, etc... we don't need all the advanced things during likeness processing, but whatever it practical to automate at scale will help in identity matching and getting the library cleaner.

This attached document is my feedback - you can always find my notes in the docs/feedback as per our usual process.  I've also included another thought about how to handle all the existing sisters and angels pictures that are deliberately left in place during a rebase.  But if we implment the clean-up, enhancements, cropping etc... we'd want to ensure that ALL of the images are processed - without losing the core identity of those angels and sisters.  All the other categories are not "locked" so if they move around, re-pair, etc... that's a new clean rebase.  We do have the logic to try to keep an existing name of the identities that we know about, but if they shuffle around and do land into an identity gallery, the filenames need to be adjusted as well.  So read through all this - we need to writeup a docs/plan and or update an existing docs/plan that aligns to this work and I think it's now the priority work for us.  It's really a continuation of the likeness and library plans already written.  But I think I just realized this needs to be the priority and if we already have a docs/plan that includes some of this or is the foundational place to put all these thoughts about the cleaninup and rebase the entire library we can update that and it now becomes the top priority for the day.  Think deeply, read my thoughts, scan the existing plans, update them and/or make a new plan.  We want to keep the docs/plans more focused and targeted and not huge monolithic plan so if we need to break them up and identify them in phases 1, 2, 3 so we know which order to do the work that would probably help all the existing docs/plans that are somewhat interrelated but I don't know which order to tackle them now.  Hope this all makes sense.  Follow our instructions on how to handle the docs/plans and the docs/feedback -- once the feedback is completey handled in the plans we'd archive those items so we know that we've handled them.
```
<!-- markdownlint-enable MD013 -->

### Follow-up chat (verbatim)

Oct 23, 2026: implementation authorization, source recovery and comparison/no-op feedback.

<!-- markdownlint-disable MD013 -->
```text
I do have some of the original non-cropped images with overlays on the hair that were just cropped in the previous intake processing - but we can deal with that later on.  Once we are able to re-process this entire gallery in the sandbox (including the core of the sisters and angels without re-assigning them) - then the end state of a rebase ensures all images are clean-up at least one time.  We'd also ensure we have the original retained in the event I do not like the outcome of the image processing and we don't lose it like I believe we have with the current process and cropping them.  IF we do have a backup of the originals uncropped that's great, but I suspect they were replaced during the existing cropping process.  Anyway - take this input, adjust the plans and get started on the changes so I can start to see the impact of what we can and can't do effectively during this image processing.  If we didn't copy all the items to the Sandbox for originals - they may be in the production B:\Soverign Territories and we could manually bring them down to re-process them.  If not, I can figure out where my originals (kept separately on Google Drive) and we'd just send them in with the next batch of 400+ images as the ongoing maintenance of the library.

Quick thought - we can probably incorporate the review of originals into the people gallery pages as well - and could also support a side-by-side view of the original and enhanced if we have that page.  I don't know how to design that, but seems like a new people gallery .html page that can surface the original, gallery and/or the 944x1104 images together to see how they look.  It could be two or more pages - one that just shows the original and enhanced side-by-side and if you select the image you launch a new page with all the photos for that image together in larger view.  Does this incorporate well into what you were thinking about being able to validate the image enhancement and cropping processes?  One last thought as well - if we can detect that the enhancement didn't work well, what would we do - would we just fall-back and use the original directly like we do now?   Also, if the image is already clean-good and without clutter - we can just use it without doing enhancements or cropping.  So we only enhance, crop, etc... on images that are blurry, bad light, overlays, borders, etc... padding is always done for the 944x1104 so that comes after - so this is all just about the initial image that would land in the person/gallery directory and be assigned to that identity.

I would allow for things with overlays to come through - as the ComfyUI workflows can/do the clean-up so I don't want manual intervention if it can't be enhanced, just add some attribute about the image that can be displayed in the gallery to explain if it is original or enhanced and if it's original why (clean original, failed enhancement, etc...)

I put several .jpgs into B:\Sovereign Territories Sandbox\Working\Various\gallery could we process those as some have overlays and graphics and would crop the head if cropped.  Other's have borders to actually crop away.  It would be great to see how these are all handled as the ones in the existing gallery had been cropped already.  Also - I guess I am curious which image would be "recommended" by the process to take and use.  I'm unclear on the definitions of which each photo is so - can we run it on those files and generate another report?  Leaving them in place and not processing them into the gallery - just the image prep process?

I thought we already had auto-cropping built in to the image processing already?  Did we lose that or do we need to move that upstream into this process and show the cropped version as well as work on the overlay removals?  Those are the most important aspects of getting the right image to then enhance with denoise, etc...

As we do this, we also need to make sure that the existing image cropping is taken into account and we don't leave that as legagy code that was cropping the images put into person/gallery.  That said, we do need cropping and padding around the head and chest for those 944x1104 images.  So if we just get the flow corrected from start-to-finish then we can have the right cropping, overlay removal (if possible to blend it away) and restore underlying image, enhancements for denoise, etc... and once it's assigned to a gallery, the file renames and the crop and pads for the 944x1104 images.  Those are the actual images I pull into ComfyUI for the workflows - not the originals in the gallery - those are references so we don't show the borders in the person gallery.  Basically, it's a multi-step process...

So, I'm thinking as we add the attempt to remove graphics and overlays to restore hair and backgrounds (where possible) it would then feed into the cropping routine to remove what couldn't be fixed.  The other option is a first attempt at a crop and only remove the borders and if that eliminates all the text, overlays and keep the full head, hair and as much of the lower body as is useful - then it wouldn't need images.  ## Screenshot_20261010_123511_Facebook.jpg is a good example of something that could crop away all the borders and it still leave the full image (just because of how the screenshot was taken).  And in the pilot test it actually left some black border at the top.  ## Screenshot_20261010_123318_Facebook.jpg is an example of where the cropping of the bottom could be acceptable or it could at least have cropped the lower black portion and left the other overlays for attempted remove, but the top the overlay is over the hair so a crop doesn't work well.  So it's having some intelligence about cropping, then attempt overlay remove and possible a final crop if we couldn't get rid of the stuff on the bottom.  Relying on ComfyUI for hair restoration and clean-up of logos does work, but getting rid of as much noise as possible without impacting the hair and face are the most important.  Some of the body missing is somewhat acceptable as we do expand images and background in ComfyUI.  Does that make sense in how I'm thinking about how I might do it myself if I were hand-cropping, then using magic eraser to remove overlays and restore the underlying image background, hair or body parts?  Let me know what you think about that?

In worst case the right-side reaction icons could be cropped as well if they don't interfere with the actual person.  The background of the picture is less imporant and we'd just pad the image more in the later phase.  So, we could attempt the eraser (which maybe that's what we call it) and if that doesn't work either leave it or crop it depending on what it would do to the body, arms, outfit and face.  If it remove some of a dress flowing - that's not imporant.  If it crops of all legs - that may or may not be important.  You're right in that it's intelligence based and actually works with how I do it using the process I described.  I go through multiple attempts to crop, erase, re-crop, erase, etc... ultimately, I am finding that the head and chest 944x1104 images are making some of the comfyUI flows work well - but other times the gallery 944x1104 is the right one when I want to bring in aspects of that outfit, pose or pieces of the original into a ComfyUI workflow.   Basically, when I was testing the new 0_Edit templates I was using a variety of all 944x1104 to see what works the best.  It all depends on what the expected output image is and whether or not the existing pose causes more issues than using a head shot only.  Sometimes it just depends on what I am doing.  Generating an A Pose from an image with the person already in an A pose works really well.  If they are crouching or lying down, just the head works better - as long as we include our tags to describe the body, figure, pose, etc... that's why I wanted to add in the chest 944x1104 in addition to the gallery and head versions we have.  Does that all make sense - sometimes it's a bit of try it in ComfyUI - compare and see which ones are best.

Great - now what else remains in the processing - the eraser, second attempt at cropping after erasing if necessary?  I'd like to review all the images and understand how each one of the ones in the various/gallery are proceeding and show which steps are skipped and which are attempted and the results of each attempt.  So, if the image is good enough right away, skip the steps and document that in the output to the report, but show the original and then denoise.  If the image is cropped and then a good image, show that and feed to denoise as that should be the recommended photo to process.  If we also need to attempt the eraser show the image and decide if it's better or we stick with the original or initially cropped image as recommended and then if we attempt a second cropping, show that and determine if it's better or worse to feed into the denoise.  Then I can help inform you whether or not the decisions on what to attempt to crop were good enough or if we need more decision logic/configuration around how those work and tune it so it works just like I was doing.  Then we feed the "recommended" image to the denoise and enhancements for review and a final recommendation on which image to generate the 944x1104 images from.  So - at the top of the report show the original, recommended after cropping/erasing, and finally recommended after denoise/enhancements.  So it could be the original for all 3, or it could be different ones based on the logic.  Some of the ones in the flow should test each of the scenarios or I can throw in a few more images to help with tuning the logic.

We also need to deal with junk photos where there is no usable face in this phase as well ... we don't want to work on junk photos - and I've got at least a couple of them in the Various/gallery now and we'll see if the process can figure that out.
```
<!-- markdownlint-enable MD013 -->

Oct 23, 2026: early automatic Junk, manual Junk/retirement and artist test scope.

<!-- markdownlint-disable MD013 -->
```text
Assuming this works, we can probably remove or skip the later junk detection or leave that in place as a double-check in the event we're not running a full rebase like this and we do detect a junk photo.  I can't recall when the _junk was handled automatically, but also need a way for me to _junk or _retire a photo if I deem it's not worth.  Junk is just junk, retire is a photo I could bring back, but junk is junk.  If that all makes sense.  I am fine auto-junking images without a usable photo in this phase - I can also put in some that have animals and was causing issues with the cropping before as those should also be handled in this phase as well.  Just more requirements to add to the docs/plans and implement these as well.

I did put in a bunch of screenshots of "art" that include animals, lots of noise on screen and overlays ... they are from Artists and I put them into Various just to test them out - but ideally they are in the Artists/gallery when I really want to process artists (which should use the same intake, engine and padding) steps, but should not mix the face into the others.  If you want me to put them into Artists gallery for testing instead - let me know and I can do that as ideally we do support both flows so we don't mix the faces up between Artists and the rest of the images.
```
<!-- markdownlint-enable MD013 -->

Oct 23, 2026: authorize a separate artist entry point with shared implementation.

<!-- markdownlint-disable MD013 -->
```text
If it makes sense to "split" the artists off into their own special likeness_artists and just make likeness work on the other directories but everything uses the same intake, engines, etc... it's just the initial setup for the path directories and such - this would draw a firmer boundary around Artists and all the other images.   If that makes sense....you can do it along with this since we're making major modifications and it's still in the sandbox for verification.
```
<!-- markdownlint-enable MD013 -->

Oct 23, 2026, 17:05: Artist GUI deferral and intake-review handoff.

<!-- markdownlint-disable MD013 -->
```text
Great work on splitting out the Artists - that's something we'll deal with later on and they don't even need to shoe the normal people gallery or have relationships with normal people.  So that should also simplify things a bit as well.  They'd need their own artists_gallery .html gui pages - but we can build those later once we lock on the people gallery - unless there a simplified view of Artists as we don't have all the same rules as we do with the people gallery.  Either way - what else is remaining to get the entire intake process that we laid out completed so I can see it and make some decisions so we can fold it into the main flow.  I'd not want to actually process the variour/gallery until I removed those artist images.  So where are we - what can you work on while I do the review and gather feedback.

We should write up a daily recap as per our normal instructions for working on the docs/plans and ensuring the plans are always updated as we work as well.
```
<!-- markdownlint-enable MD013 -->

Oct 23, 2026, 21:21: combined visual UAT, intake and gallery continuation.
Coverage: I11/v8 visual assessment above; layout L12 owns the read-only gallery
bridge; I10 remains visual/recipe acceptance and I12 remains live cutover.
This is the primary complete verbatim copy; layout links here rather than
duplicating the note.

<!-- markdownlint-disable MD013 -->
```text
What other GUI features can you implement across all the gallery pages that are either in our plans or you think would be great additions to the pages based on what you know about our work.  Especially being able to blend in the intake image viewing of "what happened" and "why" into the final gallery pages for what images are brought into the gallery?  I feel like there is a good blend forming of what you can do for all of that so I can figure out how to review the entire process from end-to-end.  One thing I do want to also capture is that the eraser did get rid of things on the right side for the actions, but did not erase things across the top, bottom or sides of images.  I'm not trying to confuse the work we need to do with the gui, but there's defintely some work to do on the eraser as it didn't really help with erasing things on top of the hair or the bottom.  We can get more into that later one, but if you actually inspect the images yourself from the runs, I think you'll see where things didn't actually work out in the same way that I would have done as a human doing the work.  Basically the goal of the automation is to replicate what I would do to get rid of the Find Related Reels that appears in the bubble at the top, sometimes across the hair and on some images like ## angelica_image_7513772466838834360.jpg there is a logo in a corner and this one ## angelica_image_7513772617730547310.jpg that wasn't caught.  That said, some cropped images actually looked better than the recommended ones that still had the extra stuff on the images.  So I think you actually need to inspect the images and see what you think after the runs.  Sample a bunch and see if you think the decisions being made could be altered or enhanced.  You actually have a much better visual eye on the images than I do!  So go ahead and do work on both the intake and the gui to the best of your abilitities.   Update the docs/plans accordingly with your decisions, and at the very end provide an update recaps and most importantly next steps.  If you can inspect both the GUI pages and the intake images - I am sure you make a better UAT tester than I do.  Add this to the appropriate plans as the raw notes and move ahead full steam.
```
<!-- markdownlint-enable MD013 -->

Same-session follow-up (verbatim). Coverage: complete-shape masks,
hair-overlap reconstruction and crop alternatives in I18/I19/I20; no claim
that a face guard which leaves a banner constitutes a finished result.

<!-- markdownlint-disable MD013 -->
```text
Ideally we can also get rid of the banner across the hair as you look at the results and figure out it's not just the icons on the side but the banners in the hair as well as logos on the sides as well as the borders, banners and other icons that clutter a screen shot.  So far, you're doing great and figuring out how to clean-up images from what I can see in the results - so that's the work I need you to figure out and isolate how to do for all images.  I understand it may not be perfect, but there's a ton of repeating patterns on the image across what I do capture that can easily be handled like you are figuring out!  Awesome work, keep going and don't stop as long as you can continue to enhance the intake process to get to 1 final cropped, cleaned and usable image without the clutter and mess!
```
<!-- markdownlint-enable MD013 -->

Oct 24, 05:57 composition and original-storage clarification (verbatim).
Coverage: I20 subject-preserving composition and I12/upkeep U7 original/native/
derivative cutover, including the existing `*_org` housekeeping conflict.

<!-- markdownlint-disable MD013 -->
```text
I think that cropping should also be for cleaning up excess backgound while keeping the body, arms, lets in the center of the shot as well.  So maybe that's where a multi-step crop what you can, clean, crop the final will result in a closer up shot, even for a full body shot as well.  As long as the original is available for me in the gallery_org along with the gallery having the cropped and then my padded variations
```
<!-- markdownlint-enable MD013 -->

Oct 25 clean-start/staged-intake and studio-gallery clarification (verbatim).
Coverage: I21/I22/I23 and cast C2-C6; layout shared navigation/footer;
day-hygiene validation and explicit commit/push authorization.

<!-- markdownlint-disable MD013 -->
```text
I hope all the items I am giving you are incremental improvements on the plans we have written and not a major departure.  Sorry that I might be bringing in scope, but I won't be re-running a rebase to test things again until we get this sorted out so that the rebase will use the new intake processing to automatically process all images and not just the likeness matching - the rebase is a clean-start as if I just provided those images the first time.  So want to make that clear in the entire scope and scheme of things.  We can do an intake only portion of the rebase or the entire intake and matching and assignment process.  The gallery should be the one-stop-shop for where you can see verything.  If that means we also need a menu with a hamburger and more advanced features on the pages to align with industry standards we can create common .css and headers and such.  I'd also lo cool footer on the bottom - not just a basic background.  Even if just colored and it should show a version, etc... just like a professional studio gallery. But, I love how it works so far.  Keep going, think deeply, update plans, update docs - commit and push when code is clean since we have a lot outstanding right now.
```
<!-- markdownlint-enable MD013 -->
