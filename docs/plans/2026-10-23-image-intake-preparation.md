# 2026-10-23: source-preserving image intake and preparation

**Status:** active (Phase 1; sandbox clean-start integration implemented; real recipe/flow acceptance and production cutover remain gated)

## Oct 27, 11:05: review-driven crop, erase and framing refinement

The complete `feedback/image_intake_feedback.md` is preserved at the end of
this plan; the source was individually verified and archived. The user's return to intake is the
current priority, not a reset of downstream plans or approval of the v16
recipe. The completed 2,741-outcome report is the frozen comparison baseline;
the subsequent matching preview is separate and remains unapplied.
The preparation page shows source/overlay locations, not newly accepted
identity assignments. Current Various replacements can appear under their
immutable target's older folder; show both origins when building the review.

### Questions answered by the current implementation

- `denoise: 0.314s` is elapsed processing time, not diffusion denoise strength.
  The local bilateral filter uses diameter 5, colour sigma 15 and spatial
  sigma 3, at the same native dimensions. `2.16/255` is mean absolute RGB
  channel change, not a quality score, resolution gain or identity measure.
  It can smooth noise and fine detail; neither denoise nor tone is currently
  selected as a measured improvement. Keep selected cleanup as the default
  ComfyUI candidate until matched-source quality comparisons justify another.
- LaMa fills masked pixels using surrounding context. It synthesizes plausible
  content, not the original hidden pixels. Smudging may reflect a bad mask,
  large/ambiguous reconstruction or model limitations; classify those separately.
  Improving mask precision precedes comparing reconstruction methods.
- v16 currently runs border/panel crop -> edge-clutter crop -> LaMa -> final
  composition. The screenshot app-bar exception permits up to 45% person-mask
  loss below 4.5 face heights; that is materially different from the normal
  0.5% guard. It explains an allowed mechanism for leg loss, not proof of
  the cause in every named image. I32 must compare alternatives before
  adopting a different default.
- Magenta detection uses saturation/location/size/aspect heuristics and an
  elliptical envelope, not GMW logo recognition. White-glyph detection is
  also heuristic, not general OCR. The reported false positives and missed
  coloured/cursive/Dola AI text require mask-level evidence, not wider colour
  thresholds. Useful-looking removal of flowers or lights is not automatically
  a correct clutter label.
- Composition trusts a Mask R-CNN subject box plus margins and a mid-limb
  bottom guard. It does not prove complete hair/shoe/dress coverage. Inspect
  missed subject pixels and crop coordinates before changing framing rules.

### Next bounded experiment and acceptance

Oct 27, 14:16 follow-up decision: use LaMa as the normal first eraser,
with a bounded advanced second-pass candidate for unresolved/repeated overlay
patterns or a crop that would lose visible subject content. This authorizes
testing escalation, not blindly repainting every image twice or silently
accepting invented facial detail. Preserve both the original and the first-pass
result; compare an advanced method from the cleanest retained input with a
sequential second pass so first-pass smearing is not mandatory input.

The initial crop is preparation, not overlay removal at the expense of the
person. On every side, remove only confidently separable borders/outside UI
or irrelevant margins that do not cut visible person/hair/clothing. Leave a
head-overlapping pill in place for masking/restoration before residual cropping.
An incomplete person mask or face-only margin is not adequate safety proof.
When uncertain, retain the native extent and pad later. This tightens I31/I32,
not an assertion that current v16 or the experimental first crop already meets
the rule. Existing screenshot panel heuristics can propose cuts before the
eraser; the v2 grown-mask guard still cannot prove preservation of missed hair.

I39 code slice implemented as experimental policy `erase-before-residual-v3`:
recompute full-span solid-border geometry from retained original pixels rather
than trusting frozen geometry that can already include panel cuts. Record
screenshot panel proposals but never select them as the first crop. Existing
face/subject guards still apply to solid-border candidates on all sides.
A labelled unsegmented-hair regression failed before the change (400x800
became 400x710) and passes after it with the original extent/hair preserved.
All 103 focused sequence/benchmark/preparation tests pass; default v16 remains
unchanged. No new real-image batch was run because the Fantasy review gate
is pending. I39 remains open for real bounded acceptance and border refinements,
not the implemented panel-crop prohibition.

- [ ] **P1 ai** I39 Implement/test a conservative first-crop experiment on
  all sides: separate border evidence from app-panel/overlay proposals; refuse
  subject-uncertain removal before erasing. Reproduce top-pill/hair loss with
  labelled missed-mask subject regions and border-free controls, compare exact
  retained source coordinates and preserve no-crop fallback. Reuse I30/I36
  cases and publish a new immutable bounded report, not a full rerun.
- [ ] **P2 ai** I40 Add bounded advanced-erasure escalation to I38 after
  backend/checkpoint rights and local capability checks. Trigger from explicit
  unresolved overlay or subject-threatening crop evidence, not pixel-change
  ranking or a residual miss. Compare first-pass LaMa, advanced reconstruction
  from retained pre-loss input, and optional sequential second pass on repeated
  patterns. Record masks, cumulative repainted region, feature changes, lineage,
  failure/stop reason and outside-mask preservation; no automatic identity/core
  promotion. At most one advanced pass for this experiment, then hold for review.

**Review cadence:** pause when a new reviewable result is ready and tell the
user exactly which report/candidate to inspect; wait for chat or feedback-file
response before iterating beyond that review gate. The complete Fantasy
pill/icon trial was reviewed positively at 14:28: fairly decent and better
than cropping. That closes the example-specific pause, not blanket head-repair
acceptance. Proceed to the next bounded sample, then pause for that review.

### Oct 27, 14:28: pattern verification and the next rebase gate

The user accepts the Fantasy reconstruction as a useful candidate and wants
the full gallery rebase as soon as sample evidence supports it. Its backend
was still LaMa with a complete mask; do not describe it as a tested new
advanced model. Small, well-localized opaque UI is the normal first-pass
target. Large/translucent overlays, subject-overlapping pills and large GMW
badges require verified masks and an escalated reconstruction comparison,
not automatic broad repainting. Area is routing evidence, not proof of
overlay identity; keep uncertain positives unchanged.

- [ ] **P1 ai** I41 Build a versioned reference bank from confirmed GMW
  badges and search-pill/icon examples, preserving source/hash, tight shape,
  scale, opacity/style and reviewed positive/negative labels. Store reference
  crops as detector evidence, not game art. Find the badge beyond lower
  corners, comparing multiscale appearance/shape/lettering and context rather
  than magenta alone. Test round jewellery, floral/pink garments, scenery,
  writing on outfits and pill-like objects as hard negatives. A reference
  match proposes a region; verify a complete silhouette mask and confidence
  before fill. Do not copy one rectangular mask to every differently placed,
  scaled or translucent instance. Report large/uncertain proposals visibly.
- [ ] **P2 ai** I42 Add native-resolution enhancement comparisons after
  source preparation: unchanged, denoise, tone and conservative sharpen,
  with identical input lineage and no hidden repeated processing. Assess blur
  separately from noise, under/overexposure, clipping and contrast; face-scale
  detail and texture matter. Denoising is not deblurring; sharpening does not
  recover missing detail. Test halos, oversmoothing, skin/fabric texture and
  colour/exposure shifts on labelled positives and clean controls. Quality
  measurements are diagnostics until calibrated against reviewed pairs;
  auto-recommend an enhancement only for demonstrated benefit without
  subject/identity damage, otherwise retain the prepared unenhanced image.
  Keep an explicit reason, uncertainty and manual override; synthetic head
  restoration is not automatically original/core likeness evidence.
- [ ] **P1 ai** I43 Publish one expanded immutable pre-rebase review, targeting
  about 100 hash-distinct sources in bounded chunks (existing launcher max64
  per selection remains unchanged). Include all 26 named failures/known-good
  examples, Fantasy, reviewed GMW variants across positions/scales, pills,
  border/screenshot/subject-edge cases, at least 20 clean/no-processing
  controls and separate un-tuned holdouts. Mark unavailable strata rather than
  inventing labels. Show original -> safe crop -> mask -> LaMa -> optional
  reconstruction -> composition proposal -> unchanged/denoise/tone/sharpen
  with native/padded views and the recommendation/hold reason. Require zero
  newly clipped labelled subject regions, zero false-positive repaint on
  labelled negative controls and no changed originals; report unresolved
  overlays and all failures individually. Pause at delivery for user review.
  I37 acceptance and a fresh verified rebase preview are prerequisites to
  full rerun/install; this request is not permission to apply the old preview.

The tagged manual naming inventory was read. It remains source evidence for
deferred prompt/workflow migration, not an instruction to rename those stages
or conflate intake derivatives with generated `0_Edit`/`1_Alpha` art.

Implementation continuation: `overlay-review.cmd` publishes unconfirmed source-
bound pill/logo proposals, including all-position badge-like regions; it does
not train or use these as verified repaint masks. The 100-source selection is
frozen in two 50-row chunks: 46 prior cases (including Fantasy), 20 additional
unconfirmed clean/no-processing candidates, 20 reserved holdouts and 14 extra
stratum cases. Various is included; Models has zero rows in this baseline
and is explicitly unavailable rather than silently represented. The existing
64-source launcher bound remains intact.

Reference reports `overlay-references-20261027-1` and `-2` under
`Working\_reports\eraser-compare` contain 64 and 46 unconfirmed proposals.
They retain exact source copies, annotated views, candidate crop/mask,
coordinates and hashes; apply/check passed. Confirm actual GMW examples and
reject clothing/scenery before building a confirmed reference bank. These
are proposal reviews, not evidence of improved detector precision yet.

The sequence launcher now accepts `--enhancements`, adding independent
native denoise/tone/restrained-sharpen panels from the guarded final.
Diagnostics are luminance, extreme-pixel fractions and Laplacian variance,
not calibrated automatic blur/quality rankings. The unenhanced result remains
recommended; ineligible face assessments explicitly skip these operations.
The first larger batch exposed an ineligible row without geometry; publication
stopped without a partial run, then the eligibility guard was fixed and
covered by a regression. No synthetic head reconstruction enters matching/
core evidence or automatically becomes the recommendation.

The expanded sequence reports `expanded-intake-20261027-1` and `-2` are now
published and check successfully: 50 rows each, 100 articles total, no missing
local image assets or recorded detector errors. Ninety-nine usable rows have
three enhancement comparisons; one ineligible row explicitly skips them.
Final experimental counts are 66 control, 28 erased, five first-crop and one
residual-crop. Enhancement recommendations all retain their unenhanced final;
no full rebase or automatic face reconstruction selection occurred.
Normal validation passed 940 tests across 30 suites, followed by the new
ineligible-row regression and focused suite pass. This is now the next user
review gate. I41-I46 and rebase C8/C9 remain open where calibration, actual
Junk routing, verified references or full acceptance is not implemented.

### Oct 27, 15:23: first expanded-review feedback

The user explicitly supplied the archived `experimental_erase_feedback.md`;
read it by that explicit request, without treating its archive location as
evidence of prior incorporation. Its complete text is preserved below.
The Angelica `20261010125309` report confirms the concern: experimental
final is `eraser`, first crop only removes 34 top pixels, composition is
rejected, and all enhancements consume `eraser`. The complete head-overlay
reconstruction runs independently from the original and never feeds those
downstream stages. The saved v16 image is historical baseline, not the current
experimental recommendation. This is both a display defect and an incomplete
experimental branch, not merely user confusion.

- [x] **P1 ai** I47 Correct the comparison display: first three summary panels
  must be original, saved-v16 baseline and explicitly named current experimental
  final/recommendation. Mark every remaining image selected/intermediate/
  diagnostic/rejected/comparison-only with visible text and distinct border,
  not colour alone. Show source input and downstream consumers on panels,
  and distinguish unselected reconstruction from a visually rejected result.
  Preserve old immutable reports; publish revised pages as a new verified run.
- [ ] **P1 ai** I48 Reopened after the Oct 27, 16:29 review: for the Angelica
  head-overlay example, finish and visually validate the composed downstream
  result, not just a reconstruction feeding enhancements. Build a
  separate integrated candidate branch from the verified retained/pre-loss
  image: safe crop -> localized cleanup -> full-pill reconstruction ->
  guarded composition proposal -> native enhancement comparisons. Do not
  substitute the independent original-based reconstruction and lose prior
  cleanup. Preserve source-coordinate masks across crops and cumulative
  changed-region/outside-mask evidence. Report branch selection explicitly;
  restoration stays synthetic and requires visual acceptance, not original
  likeness/core promotion. Subject-free margin tuning is still open in I49,
  not completed by this branch integration. The single example was verified
  first; the Oct 27, 15:40 user instruction then explicitly authorized the
  same 100-image rerun instead of pausing after that example.
- [ ] **P1 ai** I49 Revisit confidently subject-free UI margins on all sides,
  without reinstating face-margin-only panel cropping or losing hair/body.
  Angelica's integrated recommendation still retains black panels and some
  captions/icons; integration is not acceptance of these residual overlays.
  Compare actual original/crop/mask/final pixels and controls before loosening
  first-crop or composition selection. Carry any remaining logo/mask misses
  into I41 rather than treating successful reconstruction as a clean-image test.
- [x] **P1 you** I50 Review the single `angelica-flow-v7-20261027` example,
  including first crop, full UI mask, repaired hair, selected composition
  and all three enhancements. Confirm the repainted handbag/background and
  caption area, not only UI disappearance. Only then extend the corrected
  crop/complete-mask/composition recipe to known hair/feet failures and clean
  controls before another 100-image rerun. I48/I49 remain open for acceptance
  and cross-image calibration; successful tests alone do not close them.
  Oct 27, 17:24: the user approved this example as "perfect", accepting the
  synthetic handbag/hand area as the necessary cost of removing the UI. This
  accepts one dense-screenshot scenario only, not GMW logos or other layouts.
- [x] **P1 ai** I51 Test the v7 recipe beyond Angelica: rerun the frozen
  screenshot/GMW cases and clean controls, then incoming GMW/screenshot
  images. Inspect every stage and enlarged native final regions per row, not
  only previews or lineage checks. Record heuristics that fail to generalize;
  do not tune thresholds to a single image.
  Oct 27, 17:52 first sample, `sample10-v7-20261027` (10 rows, every stage
  and native close-ups inspected): the picture-box detector fired on none of
  the seven other phone-reel screenshots, whose picture runs under the
  status bar (no black top panel). All seven kept the status bar, comment
  panel and nav bar; rails and captions were partly erased into garbled
  text, and the Facebook pill was half erased. The standalone GMW logo was
  removed cleanly. A pink rose (Drakness) was a false-positive emblem and
  was washed out. The clean control was untouched. Conclusion: reel layouts
  need layout profiles anchored on the comment panel/nav bar, and emblem
  erasing needs a confirmed GMW reference match (I41) before filling.
  Oct 27, evening, done: with the I52 pattern profiles the same 10 rows pass
  (`sample10-v9-20261027`, every row inspected): all seven reels have their
  picture box (boxed and full-bleed), status bar, pill, rail, slider,
  sticker, avatar and caption filled and the panels cropped; the GMW logo is
  removed on its own and on two reels; the rose and the clean controls are
  untouched. Residue left for ComfyUI: a pale smear where the Following
  button sat (Camaris) and a faint chevron (Paige Rowe). v8 refused Amara's
  reconstruction at 22% coverage; the reconstruction branch now allows 30%
  for pattern-confirmed UI, and full-bleed compositions drop the status band
  when the person starts below it.
- [ ] **P1 ai** I52 Oct 27, 18:56: make overlay handling a reusable pattern
  library: a data-driven profile file (phone reel frame anchored on the nav
  bar/comment panel, boxed screenshot, side masking bands, oval/reel pill,
  black borders, icon clusters, GMW badge/avatar, text watermarks such as
  "Dora AI") plus a reference bank of confirmed crops outside git. A logo is
  erased only after a reference/structure confirmation; uncertain matches are
  refused, not filled. New patterns are added as data, not code. Simple
  residue may slip through for ComfyUI; hair, face and feet must not be lost.
  Oct 27 progress: `tools/art/intake_library/overlay_profiles.json` holds the
  phone-reel frame (bottom-panel anchor, boxed/full-bleed, zones for top
  controls, rail and caption), the `corner-text` watermark ("Dola AI" on
  Seraphine; thin bright strokes, several letters, not touching the edge)
  and the `gmw` badge (closed magenta ring with silver lettering; 5 true,
  0 false on 41 labelled proposals). `overlays.py` reads it; the
  experimental flow uses it on every image and colour-blob logos are no
  longer erased. Still open: the reference bank of confirmed crops, side
  masking bands and other layouts as they appear.
  Oct 27, late, from the `full100-v9` inspection: added `corner-sparkle`
  (pale four-point star, Brielle Carter), `letterbox` (flat dark blurred bars
  ending at a sharp edge, Seraphine), caption blocks (stacked centred lines
  with their title, Ravaelle "Goodnight ... x Aria"), a baseline and
  minimum-height check on watermark letters (carpet pile on Uma Dunn was a
  false hit) and a lower glyph brightness (the semi-transparent "Dola AI" on
  Harlow Chase was missed). Boxed reels now end where the black under the
  picture starts (Fia Oakes, Ruby Eden kept a black band), and a reel's own
  avatar face no longer refuses its avatar part (Nova Foxworth, Eloise
  Bishop). Left for the reference bank or ComfyUI: the rotated "ORDINARY"
  music sticker on Afton Voss and the ornate "Echoes of Fantasia" artist
  logo on Wren Ellery.
  Oct 27, night, from the `full100-v10` inspection: both are now handled.
  `tilted-sticker` finds rotated pale lettered cards (both Afton stickers,
  the music one with its album thumbnail) and masks the rotated polygon; the
  reference bank lives in git as `overlay_references/` (small logo crops
  only; first: `echoes-of-fantasia`, 0.94 match against 0.59 for the next
  best image, also found at 75% size); `viewer-corner-icons` removes a
  viewer's close X and "..." dots (Harlow Chase). Boxed reels with a tall
  black top panel now crop past the 12% cap through fully black rows (Fia
  Oakes, Ruby Eden: top 280 -> 327). None of them hits another of the 100
  rows except the "..." dots on three full-bleed reels, which are UI.
- [ ] **P1 ai** I53 Iterate on the frozen 100-image sample (after the 10-row
  sample passes) until every row is clean, inspecting each row's stages and
  native close-ups; clean controls must stay untouched. Pause for user review.
- [ ] **P1 you** I57 Review the v11 100-image proof (`full100-v11b-20261027-1`,
  `full100-v11-20261027-2`) and decide how I54 installs it: the gallery photo
  becomes `processing.final`, which likeness reads, while reconstructed rows
  (head overlay, logo, sticker) contain synthetic pixels that the plan keeps out
  of likeness/core evidence. Options: (a) install the reconstruction as the
  gallery photo but match likeness on the guarded (crop/erase-only) image;
  (b) install the guarded image and keep the reconstruction as a review
  variant; (c) install the reconstruction everywhere.
- [ ] **P1 ai** I54 Promote the accepted recipe into library intake and rerun
  the full sandbox rebase (rebase plan C8/C9 rules).
- [ ] **P2 ai** I55 Send 20-30 rebased images through the ComfyUI Prime pose
  workflows, including the new 3/4 pose, 1-2 images per workflow, and pull the
  results back into `gallery_generated` beside the gallery variations.
- [ ] **P3 either** I56 Vision: one command (or a GUI pick) takes a new image
  through intake, likeness, assignment, Prime/Prime Bare and onward into
  2_Studies, 3_Layers, 4_ and 5_ workflows without manual iteration.

The expanded 100-image review is not accepted. The initial border-only rule
was intentionally conservative; the required follow-up is proven subject-free
margin handling, not simply making its thresholds more aggressive.

### Oct 27, 15:40 continuation: updated 100-image run delivered

The user's instruction below supersedes only the single-example pause, not
the safety guards or the visual acceptance gate. The integrated Angelica run
was applied/checked first. Reconstruction now consumes its guarded `eraser`
image (including the 34-pixel source offset), preserving earlier cleanup;
its composition proposal and all three enhancements consume that restored
branch. The cumulative source-coordinate mask has 281,130 pixels and the
retained original agrees exactly outside it. Restoration is synthetic and
excluded from original/core likeness evidence, not automatically installed.

All 100 identical frozen selections were then reprocessed in two chunks.
New `expanded-intake-v2-20261027-1` / `-2` preserve the rerendered evidence.
Browser validation caught long source headings overflowing narrow screens;
`expanded-intake-v3-20261027-1` / `-2` publish the responsive HTML revision
over exact copies of those verified image results, without another model run
or changing v2. Both final reports check successfully. Earlier original
`expanded-intake-20261027-1` / `-2` still check without rewriting.

Review locations under `Working\_reports\eraser-compare`:

- `expanded-intake-v3-20261027-1\index.html`: first 50, starting with Angelica.
- `expanded-intake-v3-20261027-2\index.html`: remaining 50.

The first three panels are original, historical v16 baseline and the named
recommendation **for review**. Visible status text/borders and input/consumer
labels distinguish rejected crops, masks and unselected filter comparisons.
The branch is not labelled visually rejected merely because it is synthetic.
There are 100 unique sources, matching frozen selection bytes, no missing
local image assets and no detector errors. Finals: four integrated synthetic
head reconstructions, 66 controls, five first-crops, 24 ordinary erasures and
one residual crop. All four reconstructed results pass cumulative outside-mask
checks; 96 rows explicitly skip head reconstruction. Ninety-nine eligible
rows have three enhancement candidates from their actual final; one row
explicitly skips enhancement. No automatic enhancement ranking was introduced.

This fixes I47 and the I48 flow, not all intake quality concerns. Initial
cropping remains conservative (I49); residual UI/logo coverage, confirmed
references, enhancement calibration, early/final Junk and replacement gates
remain open. No full rebase, matching install, original-name change or
production-library modification occurred. Pause for the updated sample review.

### Oct 27, 16:29 correction: inspect every Angelica stage

The user rejected the updated sample's first Angelica output. I48 was marked
complete too early: the generated reconstructed composition was rejected,
so enhancements still consumed the uncomposed restoration. Passing lineage,
hash and asset tests did not establish clean or correctly framed output.
The assistant had inspected original/reconstruction previews, not every stage
closely enough. I48 is reopened and I49 remains open.

Single-source runs `angelica-flow-v4-20261027` through `-v7-` were kept as
immutable iteration evidence, not overwritten. The latest review is
`Working\_reports\eraser-compare\angelica-flow-v7-20261027\index.html`.
No new 100-image run was started.

The first crop now uses paired observed screenshot picture/panel transitions,
not face margins or a body-box crop. Angelica's measured picture rectangle
is `[0,163,1080,1853]`; first crop is `[0,121,1080,1853]` (1080x1732),
retaining the complete overlapping pill and removing the bottom app panels.
Pill reconstruction occurs on that cleaned input; final composition selects
the observed picture rectangle (1080x1690) from the reconstruction. Denoise,
tone and sharpen all consume `head-overlay-composition`, not `eraser` or
the uncomposed head reconstruction. The report checker verifies both the
composition's exact pixels against the reconstructed crop and its lineage.

Stage-by-stage browser screenshots included original, saved baseline, control,
first crop, localized mask/fill, expanded reconstruction mask/fill, cumulative
source mask, selected composition and every enhancement. Enlarged upper/lower
inspection of the actual unenhanced recommendation caught defects that padded
previews hid: a partial back arrow, bookmark side strokes and caption gaps.
The masks were iterated to complete icon envelopes and a joined caption
envelope; source badge evidence is retained across the crop. New regressions
cover those gaps, source offsets and actual composed enhancement input.
The latest upper/lower inspection no longer shows those UI fragments or the
large black app panels. The reconstruction mask is about 14.22% of its input,
below the existing 20% cap; unchanged pixels pass cumulative source-mask checks.
Validation: 162 preparation/retention/benchmark/sequence/reference tests pass,
including 62 focused sequence/benchmark/reference tests. New and previous
50-row reports pass read-only launcher checks; all 13 single-example image
artifacts exist. Markdownlint and `git diff --check` pass. Syntax checks pass.

This is still a synthetic repair, not recovered source detail. The enlarged
lower view shows synthesized background/handbag texture where the rail was;
user acceptance of that trade-off is required. Paired boundaries and sidebar
envelopes are screenshot heuristics, not semantic guarantees. No blanket
relaxation of body crops, confirmed GMW classifier, default v16 change,
original/core promotion or production install was made. Pause at I50.

### Oct 27: unusable faces, final Junk and replacement continuity

- [ ] **P1 ai** I44 Audit first-pass and final prepared-image face usability
  gates together. Obvious no-visible-face/torso/arm-only images, unusably small
  faces and independently verified unrepairable blur must not become new
  Potentials or matching/core seeds. Reassess the actual final candidate:
  an erased overlay leaving a smeared/unusable face does not pass merely
  because the original had a detection. A back/profile pose is not automatically
  Junk; distinguish a usable visible face from genuinely absent/unusable
  identity evidence. Detection/model failure or uncertain quality is a
  diagnostic hold/Review, not proof of Junk. Synthetic face completion cannot
  supply original likeness evidence. Find the reported Drakness/Drakniss/Nyxene
  body/arm-only photo by bounded catalogue audit rather than guessing which
  identity; include it in regression/review evidence.
- [ ] **P1 ai** I45 Wire verified Junk outcomes through existing reversible
  quarantine and gallery filtering, at intake and after final reconstruction/
  enhancement. Keep originals, reason, source/final previews, provenance and
  restore/undo. Junk is hidden by default but explicitly viewable, distinct
  from Review/uncertainty. Existing cast/protected/selected references must
  surface a conflict and replacement decision rather than silently deleting
  a workflow source or bypassing protection. Repeated intake/checks must not
  re-promote quarantined junk or reprocess it without explicit retry.
- [ ] **P2 ai** I46 Re-test duplicate and incoming-replacement continuity with
  the prepared-image pipeline. Exact byte duplicates, same stable-photo-ID
  new versions and merely similar renderings are different cases. When a
  deliberate incoming replacement is accepted as preferable, keep it current
  and archive the older version in the existing duplicate/recovery mechanism,
  retaining stable identity, selected-input bindings and exact undo; do not
  always reject the incoming version. If distinct originals produce identical
  prepared pixels, preserve both provenance records and propose deduplication
  rather than silently merge people. Quality preference needs explicit
  selection or calibrated evidence, not newest timestamp alone. Junk gates
  take priority over replacement: a newer unusable image must not displace
  a usable protected/current reference.

These are final intake acceptance requirements, not claims that a no-face
detector or an arbitrary blur threshold proves irreparability. Reuse existing
Junk/duplicate/replacement tooling; do not introduce a second disposition store.
The user wants cast seeding limited to accepted high-confidence core evidence
and/or explicitly selected workflow references, then fresh grouping/merging
and family proposal rules. The numeric `x.xx` threshold is unspecified; use
the owning policy's approved values and display the actual values in the
preview, never invent a new cutoff from this message. Sandbox acceptance and
original-name corrections precede any equivalent production-library cutover.

Oct 27, 13:26 review: the user prefers LaMa over Telea/Navier-Stokes across
the inspected same-mask comparisons. Retain the classical methods as evidence,
not the preferred replacement. This is method preference, not acceptance of
the existing masks or crop recipe.

The additional mandatory case is
`Artists/Fantasy/gallery/fantasy_shot_20260902204526.jpg` (1080x2016).
Direct inspection confirms a wide "Find related reels" pill over the upper
face/hair, plus a separate top-right paper-plane icon. The frozen v16 trace
actually detects `search-bubble` at [32,127,932,246] and marks it `refused-face`;
it is not simply an oval-detection miss. A glyph at [520,160,654,209] is also
refused at the face, while other lettering is filled separately. Trace the
paper-plane icon independently; do not assume the pill mask covers it.

- [ ] **P1 ai** I38 Add this Fantasy case to the next immutable benchmark
  selection (do not edit the existing 46-source runs). Separate detected-but-
  refused face overlap, incomplete pill/text mask and missed icon. Compare a
  complete reviewed UI silhouette mask with the existing clipped/fragmented
  mask. Keep no-crop/no-face-repaint as the automatic fallback. Test head-
  overlapping fill only as an explicit synthetic-reconstruction candidate,
  never recovered original or unreviewed likeness evidence; record changed
  features and outside-mask preservation. Evaluate automated text/UI location
  plus shape segmentation to avoid hand-drawing each repeated pill. Review
  model/checkpoint rights and local hardware before adding a learned backend.

Relevant source-available approaches: Inpaint Anything composes segmentation
with LaMa or diffusion; SAM proposes masks but does not inherently know that
a search bar is unwanted. IOPaint is a self-hosted application/backend
collection, not a single automatic eraser model. Its documented diffusion
options include SDXL inpainting/PowerPaint. MAT is a learned large-hole
alternative but the upstream license is CC BY-NC 4.0, so it is not a
drop-in commercially cleared game-production dependency. Code and checkpoint
licenses require separate checks. No alternative was installed or run here.

Sources checked: [Inpaint Anything](https://github.com/geekyutao/Inpaint-Anything),
[IOPaint](https://github.com/Sanster/IOPaint),
[MAT](https://github.com/fenglinglwb/MAT) and
[MAT license](https://github.com/fenglinglwb/MAT/blob/main/LICENSE).
No claim is made about the proprietary implementation behind Google's eraser.

I38 implementation evidence: the opt-in `--sequence --head-overlay` mode
automatically proposes the complete pill and constrained nearby outlined-icon
mask, renders a separate LaMa candidate and records face-guard bypass,
coverage, unchanged outside-mask pixels and explicit non-selection. It never
changes the normal guarded final or default pipeline. The first run exposed
a missed icon, so the second adds a tested bounded bright-outline proposal
beside a detected pill, rather than broadly erasing white scenery.

Published/checked report:
`Working\_reports\eraser-compare\fantasy-head-overlay-icons-20261027\index.html`.
The real mask contains the pill [32,127,932,246] and icon proposal
[962,154,1038,224], 113893 pixels / 4.5067% of the native image.
Outside-mask RGB is verified identical. Direct inspection confirms the pill
and paper-plane are removed, but the obscured hair/forehead is synthesized
and not established as faithful anatomy/identity. This is a review candidate,
not automatic acceptance or proof of recovered head detail. Forty-one
focused benchmark/sequence tests pass. No new model/dependency was installed.
Remaining I38 work is evaluating semantic/generative alternatives and user
quality acceptance; this implementation does not claim Google's quality.

Oct 27, 11:44 execution authorization: start intake implementation and bounded
A/B testing after the raw-feedback preservation/archival pass; templates
remain deferred. I35 also compares precise versus envelope masks, native
patch resolution and, if a repeated translucent overlay can be reliably
modelled, alpha separation. Validate on clean originals with synthetic
overlays so accuracy is measurable. Opaque areas still require invented
reconstruction; no library can recover their exact hidden content from a
single image. Add a learned model only after existing-method comparisons
demonstrate a gap and rights/runtime requirements are checked.

- [ ] **P1 ai** I30 Freeze a review manifest of every example below, resolving
  exact source/overlay bytes and v16 artifact hashes; include a Various-origin
  view even when replacement paths name an Angel/Potential. Publish source,
  first crop, detections/mask, second crop, erase, final frame, native and
  944x1104 previews with input/output coordinates, dimensions, retained area
  and selection reasons. Every generated candidate, including
  `ui-crop-proposal`, must appear in the options table as selected, comparison,
  refused or failed, with a reason; image-only candidates are insufficient.
- [ ] **P1 ai** I31 Refine solid-border detection on the named top/side/bottom
  residuals, including partially hand-cropped sources. Preserve true dark
  scenery/hair and compare with border-free controls. Diagnose the two-pixel
  guard and split border rather than globally trimming extra pixels.
- [ ] **P1 ai** I32 A/B v16 against border crop -> precise masked erase ->
  guarded residual crop -> final framing on identical inputs. Record content
  preserved, overlay remnants, mask damage, reconstruction artifacts, runtime
  and every crop's subject loss. Evaluate the leg-cutting app-bar exception
  explicitly; do not make erase-first universal or auto-select a lossy crop.
  Try at most one additional residual-detection/erase pass as a labelled
  candidate, with cumulative mask/face/subject guards and a visible stop
  reason; no unbounded repaint loop or claim that redetection proves clean.
- [ ] **P1 ai** I33 Build positive/negative clutter masks from the examples:
  actual GMW badges versus floral/pink/red garments, flowers and lights;
  white/coloured/cursive/Dola AI overlay text versus writing on clothing.
  Test shape/context evidence before expanding colour thresholds. Separate
  unwanted background-object editing from automatic overlay removal; do not
  repaint a garment merely because one background false positive looked good.
  Keep ambiguous areas unmodified with a visible diagnostic. This refines
  I18/I27 rather than replacing their earlier bubble/PIP/ad-card cases.
- [ ] **P1 ai** I34 Refine full-subject framing with evidence for high hair,
  hands, feet/shoes, dress edges and off-centre people; test horizontal and
  vertical positioning independently. Prefer preserved content plus padding
  or a skipped crop when coverage is uncertain. Target 944x1104 in the
  derivative, not by forcing native crops that amputate visible content.
  Record mask/fallback and missed-region limitations. This is I20 follow-up.
- [ ] **P2 ai** I35 Compare LaMa with existing local classical fills on the
  same reviewed masks and inputs; distinguish texture/detail preservation
  from smooth but invented content. Label face artifacts/blur/blockiness as
  quality warnings, separately from identity and overlay detection. Compare
  cleanup/denoise/tone on identical native and padded views; do not promise
  recovered face detail or auto-select enhancements from pixel-change values.
  New restoration models/dependencies require a measured need and rights/
  hardware review; face-analysis M1/M2 remains the explanation/evaluation owner.
- [ ] **P1 ai** I36 Run the named-case benchmark plus a deterministic,
  hash-deduplicated control sample of at least 20 additional images, spanning
  Various, other identities, Artists, clean/no-border photos, genuine logos,
  screenshots, full figures and unusual poses. Keep the two explicitly good
  controls below. Label expected preserve/remove/uncertain regions before
  tuning and keep separate holdouts. Require zero newly clipped labelled
  subject regions and zero newly repainted labelled garment/face regions;
  report remaining overlays, false positives and uncertain cases individually,
  not just an aggregate score. Run focused regressions and existing validators
  before a reviewable new run; never overwrite v16 or rerun all 2,741 first.
- [ ] **P1 you** I37 Review the bounded A/B report and approve/reject specific
  crop/erase/framing rules after I30-I36. No further full-input processing,
  revised matching, installation or production cutover until this gate.
  I29 remains partial review, not blanket recipe acceptance.

### Named-case coverage ledger

Implementation checkpoint: all 26 exact case-insensitive source paths resolved
against the frozen manifest, plus 20 additional deterministic hash-distinct
controls (46 records). Selection/evidence JSON is retained in the session files;
controls still need visual preserve/remove/uncertain labels and separate
holdouts before any acceptance claim. The missing-options-table regression
failed before the report fix, then all 61 preparation tests passed. New reports
list UI proposals and diagnostic masks without changing processing selection.
The frozen v16 report remains unchanged; erase-order and framing fixes are
still open.

The first same-mask reconstruction comparison is published and checked at
`Working\_reports\eraser-compare\intake-20261027-46\index.html`.
It binds the frozen v16 report/receipt and exact selected input/mask hashes:
22 rows compare saved LaMa against OpenCV Telea and Navier-Stokes (radius 3);
24 explicitly skip (17 no detected clutter, six nothing left after crop,
one face-size Junk hold). A skip does not prove a clean image. All 46 rows
appear in the HTML, with 242 resolved local image references and shared
header/footer. The launcher check verifies all saved output hashes.
No candidate is selected and no original, identity or baseline report changes.

This is the post-crop reconstruction slice of I35, not I32's erase-first
experiment or acceptance of the masks. On the first Angelica example, direct
inspection shows conspicuous Telea smearing in the right-edge masked areas
where the saved LaMa result looks smoother; this is one observation, not an
aggregate method ranking or proof of recovered detail. Precise mask labels,
ordering/border/framing fixes, synthetic-overlay ground truth and holdouts
remain open. The integrated browser refused this B: location as untrusted;
HTML asset validation and direct PNG inspection succeeded, but browser visual
acceptance is not claimed.

### Erase-first implementation and measured framing failure

The opt-in `eraser-compare.cmd --sequence` mode leaves v16/default preparation
unchanged. It binds the same frozen report and 46-source selection, then
compares first crop -> guarded localized LaMa -> at most one residual
detection/strict crop -> framing. The screenshot 45%-loss exception is not
used. Coverage/face/body/unknown-kind refusals and errors remain explicit;
failed model output cannot silently become a successful candidate.

The first experimental run, `intake-sequence-20261027-46`, completed and
hash-checked all 46 rows with no detector errors and at most one redetection.
It preserved Afton's native 1080x2340 instead of the saved 1080x1776 result;
the first crop was refused at 1.0618% grown-mask loss. Seraphine's named
dress case retained 1105x1685 instead of 1105x1560, and Haniya's red-dress
case retained 1086x1448 instead of 1064x1448. These are geometry observations,
not proof that every overlay or false positive was fixed.

Direct comparison found a decisive failure: Angelica's named feet case and
Camaris's high-bun case still lost visible toes/hair during composition even
though calculated mask loss was zero. This is measured evidence that the
person mask omits real subject content, not a crop-threshold problem. Do not
adopt that experimental run. Retain the composition proposal for inspection,
but keep the pre-composition cleaned image as the experimental final until
complete visible-subject coverage is established. This safe fallback implements
I34's preserve-plus-padding preference without pretending to solve segmentation.
The first run remains immutable evidence; publish the corrected policy under
a new run name.

The corrected `erase-before-residual-v2` policy is published and checked at
`Working\_reports\eraser-compare\intake-sequence-v2-20261027-46\index.html`.
All 46 rows are present; selected grown-mask crop loss is at most 0.3897%
(limit 0.5%), maximum redetections is one, detector errors zero. Nine
proposals are rejected and three refused; these are not counted as accepted
crops. Composition remains available as a comparison, never the final.
Final counts: 20 erased, 20 control, five first-crop, one residual-crop.

The six named preservation checks now retain their original dimensions:
Angelica feet 1080x1954, Camaris bun 1080x1920, Sammara shoes 1008x1792,
Haniya red dress 1086x1448, Seraphine dress 1105x1685 and Afton 1080x2340.
Angelica and Camaris finals are verified RGB-identical to their full original
views, not merely zero loss against an incomplete mask. This verifies their
reported clipping is avoided by the conservative fallback. It does not
prove that every detected overlay/garment mask is correct or that all other
subject regions are labelled. All HTML image assets resolve; shared
header/footer and 46 articles are verified. The older experimental run still
passes read-only check. Ninety-nine focused tests pass.

I30/I32/I34/I35 now have runnable bounded evidence, not blanket completion:
mask labels, coloured/cursive/Dola text detection, border-specific tuning,
synthetic-overlay ground truth, independent holdouts and the I37 human
acceptance gate remain open. No default recipe, full rebase, matching
assignment or original-name metadata has been changed.

Paths below are the feedback's source paths, not assertions about identity.
Every row is mandatory in I30/I36, including observations with pleasing results.

| Source relative path | Expected investigation / control |
| --- | --- |
| `Angels/angelica/gallery/angelica_shot_20261010125309.jpg` | I31 split black border; I32 erase-first versus top/bottom overlay crop, preserve successful corner erase |
| `Angels/angelica/gallery/angelica_shot_20261019151702.jpg` | I34 visible feet lost during composition |
| `Angels/angelica/gallery/angelica_shot_20261019152041.jpg` | I31 left/right residual borders |
| `Angels/azaline/gallery/azaline_image_7514006418998039315.jpg` | I33 explain both logo masks; no assumed logo truth |
| `Angels/Camaris/gallery/camaris_image_7514748052075708923.jpg` | I34 protect high bun/hair above detected person |
| `Angels/Camaris/gallery/camaris_image_7514748135775865528.jpg` | Known-good framing control; preserve successful centring |
| `Angels/Camaris/gallery/camaris_shot_20260922114030.jpg` | I30 list UI proposal in table; I32 residual pass versus crop on complex clutter |
| `Angels/Gavrielle/gallery/gavrielle_image_7513253800075950209.jpg` | I33 expose unexplained erase masks |
| `Angels/Gavrielle/gallery/gavrielle_image_7513253926403921493.jpg` | I35 choppy/blended face quality, not proof of denoise benefit |
| `Angels/Gavrielle/gallery/gavrielle_image_7513253948677345758.jpg` | I35 second face-quality case |
| `Angels/Gavrielle/gallery/gavrielle_image_7513254229434089023.jpg` | I33 flowers are not a logo even if removal was liked |
| `Angels/haniya/gallery/haniya_image_7513256089848621472.jpg` | I33 preserve floral garment; distinguish actual circular badge |
| `Angels/haniya/gallery/haniya_image_7517983182019263595.jpg` | I33 background-light false positive; preferred edit is separate intent |
| `Angels/haniya/gallery/haniya_image_7517985401479370775.jpg` | I33 protect red dress on arm |
| `Angels/haniya/gallery/haniya_image_7517987028560998931.jpg` | I34 diagnose horizontal imbalance and side padding |
| `Angels/Nyxene/gallery/nyxene_shot_20260830115237.jpg` | I31 residual manually cropped bottom border |
| `Angels/Nyxene/gallery/nyxene_shot_20260830115304.jpg` | I33 protect pink dress |
| `Angels/Ravaelle/gallery/ravaelle_image_7517982505816218878.jpg` | I33 coloured/cursive lower-left overlay text; protect subject/clothing text |
| `Angels/sammara/gallery/sammara_image_7513253419079900707.jpg` | I34 preserve visible shoes |
| `Angels/seraphine/gallery/seraphine_image_7515814455928183144.jpg` | I33 Dola AI text positive, not white-region removal |
| `Angels/seraphine/gallery/seraphine_image_7515814642642047791.jpg` | I33 second Dola AI text positive |
| `Angels/seraphine/gallery/seraphine_image_7518030909567781676.jpg` | I34 protect dress/body extent |
| `Angels/seraphine/gallery/seraphine_image_7518031624882793107.jpg` | I31 bottom border; preserve successful top composition |
| `Potentials/Afton Voss/gallery/afton_voss_shot_20260922114007.jpg` | I32 leg-preserving erase-first comparison |
| `Potentials/Amara Berkley/gallery/amara_berkley_shot_20261010125440.jpg` | I32 right overlay erase versus crop |
| `Potentials/Fia Hadley/gallery/fia_hadley_shot_20261010125509.jpg` | Known-good crop/erase/text/leg-preservation control |

General Angelica cleanup approval is positive evidence for those inspected
results only. It does not accept unknown logo masks or leg/hair loss.
Prompt fidelity, person-data deduplication and the Sovereign Females test-bed
move belong to [manual migration](2026-10-22-manual-prompts-to-art-library.md#oct-27-source-faithful-prompt-reconciliation-and-female-test-bed);
dynamic category paths belong to rendering R44, not native intake renaming.

## Oct 26 guiding boundary for intake

Intake remains the automatic source-preparation and likeness-entry point for the
later staged generation flow. Its job is to publish trustworthy prepared/source
evidence and gallery lineage, not to force a single downstream render sequence.
Downstream stage routing (`0_Edit` onward) is owned by rendering/manual migration,
but intake outputs must remain selectable as valid stage inputs with verified
path/hash lineage.

## Oct 25 continuation: one prepared clean-start flow

I21/I22/I23 now have sandbox implementation, not just separate commands:

- `sandbox-rebase.cmd --dry-run` inventories immutable inputs without models,
  reports or writes. `--intake-only --apply` prepares every supplied image and
  stops; the same run without flags resumes into a fresh-cache matching preview.
  `--apply` installs only that saved preview. See the exact command sequence in
  [the likeness guide](../art/likeness.md#clean-sandbox-rebuild-versus-category-reclassification).
- All retained cast images are prepared without changing cast membership.
  Loose and named Various inputs enter the same planner; explicit names reuse
  the existing seeding helper. Artists receive preparation evidence but are not
  general matching/assignment candidates. Optional cast release is still C1/C3.
- Selected prepared bytes feed embeddings and final native images. Exact
  originals stay in `gallery_org`; kept variants, masks, thumbnails and detail
  stay in checked `gallery_intake` sets. No pruning/subset decision is invented.
  Routine backup preserves these auxiliaries; only proven standard regenerable
  derivatives use the existing omission rules.
- Prepared natives bypass legacy source cropping and screenshot stripping in
  full/head/chest rendering. Framing and minimum-quality checks remain active.
  Changing a source's prepared status invalidates an old derivative proof.
- Gallery evidence prefers the exact verified retained set, not a historical
  experiment. Detail distinguishes retained evidence from pilot output and
  returns to the main gallery, Review, Intake runs and current native; available
  maintained derivatives are linked. Historical staged runs remain separate.
- Photo moves/renames, manual actions and undo carry retained sets. Unsupported
  whole-identity operations with overlapping auxiliaries hold explicitly.
  Edited/missing/unknown retained assets are not silently discarded.
- Stable identity/name/family/override decisions migrate only with verified
  one-to-one membership continuity after matching. Missing catalogued inputs,
  unknown current photos and ambiguous decisions refuse before reset.
  Current native/category/auxiliary hashes are frozen across staging.
  Existing owned cast outputs are replaced reversibly, including another
  clean start from already-prepared inputs; unknown/edited outputs hold.

At the time this integration was delivered, no real library rebase, matching
or source replacement had run. The later all-input sandbox attempt and its
incomplete outcome are recorded below. Synthetic end-to-end tests cover
stop/check/resume, named/loose intake, retained links, existing derivatives,
repeated rebuilds, concurrent edits and exact undo. Real visual acceptance
remains I29/C7; incremental production integration remains I12/upkeep U7, not
permission to run `library.cmd` against production.

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

The continuation above delivers the sandbox I21/I22/I23 wiring. Its explicit
acceptance and production boundaries supersede the earlier integration gap;
the old matcher-only run is not evidence for this prepared-image flow.

## Oct 26 all-input run stopped during preparation

The authorized all-input run `clean-rebase-20261025-overnight` reached
1,302/2,741 preparation outcomes, then stopped with `MemoryError` while Pillow
encoded a padded PNG into an in-memory buffer. It did not produce the completed
preparation manifest or `intake.json`; matching preview, backup/install and
fresh Gallery publication were not reached. The existing partial `inputs`
staging tree is preserved as evidence, and no clean-rebase process remains
active.

The memory fix now streams image copies/hashes and PNG outputs to disk, and
computes pixel-change measurements in chunks. The complete repository
validation launcher passed 29 suites / 811 tests after this change. Inspection
of `clean_preparation.prepare` confirms that a partial `inputs` directory
without its receipt is intentionally refused as unfinished staging; do not
resume or clean this run in place. A future attempt must use a new run directory
and re-inventory the immutable snapshot/current-Various overlay. At the state
check, B: had 402.09 GB free. The full run remains unverified; this fix is not
evidence that all 2,741 images now complete successfully.

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

- [x] **P1 either** I21 Implement sandbox retained version sets (`gallery_intake`):
   preserve all currently kept alternatives and exact originals; verified moves,
   backup and undo retain them. No automatic pruning. Live cutover stays with U7.
- [x] **P1 ai** I22 Add intake-only stop/check/resume to the existing clean-start
   launcher, keyed by immutable source and full recipe, using the shared preparation
   runner. Incremental `library.cmd` cutover remains I12/U7.
- [x] **P1 ai** I23 Link checked retained all-versions detail from People/Review,
   including post-assignment moves and current/derivative return links. Historical
   comparisons remain distinct; missing or stale evidence is diagnostic.
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

**Oct 25, 20:44 clarification:** the
[reference-rendering plan](2026-10-25-reference-rendering.md#various-subject-profiles-and-future-support)
recommends keeping Various neutral while using dedicated rendering workspaces
such as the user-chosen Sovereign Females (later Oct 25 decision, replacing
proposed Reference Female). Do not rename Various to Female or add subject-kind
children to its named-person discovery without a validated migration: a folder
called Female could otherwise be interpreted as a supplied identity name.
I26 still owns physical intake/category migration. Rendering-profile selection
is independent metadata, not a sex/gender inference or directory move.
Current human-face/no-face Junk rules are not animal-intake support; a future
animal path must bypass those human-only decisions explicitly before use.

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

## Eraser escalation and conservative first crop, Oct 27, 14:16 (verbatim)

Coverage: I39 owns conservative initial cropping; I40 owns advanced second-pass
testing; I37 and the review cadence above own pause/review. This does not claim
these implementation items are complete.

<!-- markdownlint-disable MD013 -->
```text
I agree that we default to the LaMa for many items, but for items that require more advance work we'd do a second eraser pass on those items with the more advanced techniques and processing.  Being able to test how those work to get that right on the images where we have same sort of pattern would be great.  Sometimes we crop the pill away and lose a little hair so being able to deal with this before cropping would be great if we can get the right restoration of the underlying image.  We're already making multiple passes at cropping, so multiple passes at erasing with different techniques can improve the overall image we recommend.
```

```text
One thing I am noticing is that the initial crop isn't always detecting the oval/pill at the top and sometimes it crops away the portion that would later be saved.  I think that initial crop needs to focus on the initial cropping of items that are not also cropping part of the person, hail, etc... it's an intended so that the eraser doesn't deal with that noise.  Maybe you've checked that already, but seems like we also need to ensure the first crop is less aggressive and only focus on boder and outlier items not needed for the image.  It can be all sides to simplify the eraser portion and lead into the second crop. Hope this all makes sense with everything going on.  Also, whenever you have something else for me to review, please pause and let me know about that item and I'll review and provide feedback in chat or write up a document if a lot of extra feedback.
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

## Oct 27 intake review (verbatim)

Source: `feedback/image_intake_feedback.md`, received Oct 27, 11:05 -05:00.
Coverage: I30-I37 and the named-case ledger above; general observations and
questions are answered in the implementation explanation. The source remains
in place for further review; no feedback deletion is requested.

<!-- markdownlint-disable MD013 MD009 -->
```text
# Intake Review and Feedback - 10/27/2026

I am reviewing the full intake crop/erase/crop review and have some observations.

## Observations

In general, I love most of the processing of images and how it's all working in the complate intake and review.  What I am wondering is whether or not this page also represent the assignments of the images or this is just taking everything and processing it based on it's current assignments of the identities?  I am guessing that's the case - but just wanted to confirm that.

### Denoise Question

I have a simple question about the denoise that I would like confirmed.

denoise: 0.314s; pixel change 2.16/255

So what impact does this have on the quality, scale or results of the image?  In looking at them, I tend to like them just as much as the results after cropping/erasing, but want to understand which of the images are better quality to feed into the pipeline for comfyui?  What did the denoise actually do with the image?

### Erasing

What is the technique used in erasing.  Sometimes it seems to bring the background back perfectly and other times it looks more like a smudge.  It's still better to have the logo's remove in general, but I don't know if there are things we can do to make it less smudge and more bring back the original part of the image more accurately.  Are there other techniques of erasing we could compare and contrast together?

## Angels General Feedback

I like how the erases is working to revmove the circle logo on those various pictures and would agree with the recommended images after the sequence.  Most don't need cropping so those being skipped are all good.  So I am pretty happy with Angelica's output overall.

## Angels/angelica/gallery/angelica_shot_20261010125309.jpg

- The first crop to geometry didn't entirely take the black border out, it split it leaving a small portion still visible.  
- The second crop then took the overlay pieces on top and bottom and it remove those pieces without trying to erase and preserve the content underneath.  It did recognize it in the "Trimmed [0, 211, 1080, 1673] of the first crop: top 9 part(s), person lost 0.4%; bottom 18 part(s), person lost 7.3% (screen-wide app bar below the hips). A pure crop: no pixels invented; the person and a margin are kept." comment, which indicates that the crop was intended to remove the overlay without affecting the person significantly.
  - But my question is whether or not we should have attempted to erase that overlay instead of cropping it, to see if we could preserve more of the original image content underneath?
- The erase step did a good job of removing the remaining icons on the right bottom corner without affecting the underlying content.
- The recommended photo is decent and it's not a huge loss - I just want to understand if there is some potential for preserving more of the original image content by using erasing instead of cropping in certain situations.

### Cropping and Erasing A/B Testing

- This cropping and erasing sequence makes me wondering if we should consider trying to erase overlays first before resorting to cropping, to see if we can preserve more of the original image content.  If we could run some A/B Testing on scenarios where overlays are present, we might be able to determine the best approach for maintaining image quality and content integrity.
  
## Angels/angelica/gallery/angelica_shot_20261019151702.jpg

- This one seemed to crop off her feet in the composition to position her body more centrally.  What would be the cause of that as her bare feed are visible in the main picture and then cropped out at that point?  It's not a big deal, just more curious what is happening in this case as it doesn't always do that.

## Angels/angelica/gallery/angelica_shot_20261019152041.jpg

- There's some black borders on the right side of this picture that aren't detected and cropped away entirely it left a small strip on the right and left sides.  "Only near-solid external black/white strips removed; two-pixel boundary guard retained." We don't have many images with side borders, but looks like in this case we didn't get them all and the other checks also did not catch them after the first crop.

## Angels/azaline/gallery/azaline_image_7514006418998039315.jpg

- This one did some erasing on areas where I don't actually see a logo present to erase.  "LaMa repainted 2 clutter shape(s) (logo), 3.26% of the image; face boxes are never repainted. Repainted areas are plausible, not recovered; compare with the original." But I don't know what it saw in the image to trigger that as visually I don't see anything there.

## Angels/Camaris/gallery/camaris_image_7514748052075708923.jpg

- This one cropped the top of her hair during composition to frame the person "Framed the person [105, 343, 1074, 1920] with a small margin, widened toward 944x1104: [0, 233, 1080, 1920]. The person mask ends mid-limb, so the bottom is kept to the frame edge. Pure crop of the cleaned image." and didn't realize that it was cropping her hair that is up in a top bun or styled above her head.  It's interesting to see how the framing logic prioritizes the person's body over other elements like hair in the composition.

## Angels/Camaris/gallery/camaris_image_7514748135775865528.jpg

- This one did a good job at composing the image to frame the person appropriately without cutting off important elements like hair or extremities.  It seems to have balanced the framing logic well in this case, maintaining the integrity of the subject's appearance while still centering the composition effectively.  It got rid of some of the top of the picture that was causing things to be off center.  So this was a good framing.

## Angels/Camaris/gallery/camaris_shot_20260922114030.jpg

- This one was complex and the cropping and erasing didn't actually get rid of all the clutter and the recommended image still has stuff on it.  It does show a "ui-crop-proposal: 0.280s; pixel change not comparable (different crop dimensions)" which is actually better, but it was just a crop of the stuff that was not found on the image.
- This feeds back to the A/B testing of cropping and erasing.  I am wondering if we might also need a second pass with erasing to check for remaining clutter not found in the first pass.  It seems that relying solely on the initial detection and cropping might leave some residual clutter that could be addressed with an additional erasing step.
- Ultimately the "ui-crop-proposal: 0.280s; pixel change not comparable (different crop dimensions)" would have been the best proposal - but I don't see it listed in the table of options for this image.  Just as an image in the bottom section of all the images.  
- This one needs more digging as it's one of the complex images we need to process.

## Angels/Gavrielle/gallery/gavrielle_image_7513253800075950209.jpg

- This one the eraser also found things to erase that I don't see a logos.  Is it just finding patterns or textures that it interprets as clutter or logos, even if they are not visually obvious to me?  It would be helpful to understand the criteria it uses to identify areas for erasing in such cases.

## Angels/Gavrielle/gallery/gavrielle_image_7513253926403921493.jpg

- This one her face is not well blended and a bit choppy.  It might benefit from additional blending or touch-up to ensure a smoother and more natural appearance, but not sure if we have any potential to check for photo/face quality of the images and improve them in the enhancements portion along with denoise and tone.  Neither of them caught the quality issue in this photo.

## Angels/Gavrielle/gallery/gavrielle_image_7513253948677345758.jpg

- Same image quality issue with this one for what her face looks like.

## Angels/Gavrielle/gallery/gavrielle_image_7513254229434089023.jpg

- This one erased some flowers on the image as clutter - which is actually fine.  So just more an observation that it found the same pink/purple flowers as is the main circle overlay for GMW and treated the flowers as a logo.  But that's ok and maybe that's what's happening in the other places where it find some underlying colors that are similar and blends them away.

## Angels/haniya/gallery/haniya_image_7513256089848621472.jpg

- This one was a bit more destructive to her outfit as it blended away what it considered junk which was just part of her flowered outfit in those same pink/purple colors.  So we may need to adapt the junk to look for more specific circular logo for GMW in the colors.  That might be what is needed for a photo like this.  I don't want to change it so it missed the logo in other images - but this is a case where it was overly agressive on the erasing.

## Angels/haniya/gallery/haniya_image_7517983182019263595.jpg

- This one picked up a solid white light in the background and treated it as the overlay icons, so it's likely the same color in the background, but I like how it erased it as it makes a better picture.  So this is also an example of extra erasing, but in this case it was a good outcome.

## Angels/haniya/gallery/haniya_image_7517985401479370775.jpg

- This one also erased part of her red dress on her arm in the lower right of the image.  It's not clutter and didn't need to be erased.

## Angels/haniya/gallery/haniya_image_7517987028560998931.jpg

- This one she's on the very far right of the image and it seems like the composition could have cropped some of the excess of the right side.  It's doing a great job getting rid of stuff at the top to bring the face and body into vertical postion, but the horizontal composition isn't as good.  It would ultimately result in padding a ton of the gray on the sides, but then she'd end up more in the center of that final.  This is likely happening on many other images as well, so we can use this to verify the logic on the left/right positioning of the person in the image.

## Angels/Nyxene/gallery/nyxene_shot_20260830115237.jpg

- This one did clean-up the bottom of the image, but it left some black border there that could have been cropped.  This was a case where I attempted to manually crop it a while ago and left some small residual on the bottom and it didn't get it all in this processing.

## Angels/Nyxene/gallery/nyxene_shot_20260830115304.jpg

- This one also found part of pink dress and treated it as a logo and erased it.  So I do think our logo detection needs to be tightned up.  One more example for you to inspect.  There are more I see as I scan - but I won't call them all out again, we have enough samples to work with to try and adjust how it's working compared to ones where it necessary.

## Angels/Ravaelle/gallery/ravaelle_image_7517982505816218878.jpg

- This one has some text on the screen in the lower left that wasn't caught as overlay.  It's a slightly different color than the typical overlay icons, so it may have been missed for that reason.  That said, I don't want to over-correct and start erasing non-text in the same colors so the type of overlay pattern for something like this need to understand it's text and not just any similarly colored area.  This may also help with blending away the overlay on the top of the screens on screenshots if we can ensure we get the right shape of overlay text or the oval areas around it.

- This one was cursive writing of some comments about the image.  Again, finding "text" written would be fine to remove as overly, but not if it's on an outfit or part of the subject itself.

## Angels/sammara/gallery/sammara_image_7513253419079900707.jpg

- This one cropped some of her shoes off in the composition to frame her in the image.  Not sure if it's a big deal, but seems like some tuning here might be helpful in ensuring the entire both if present in the image is not cropped during the composition to frame her.  

## Angels/seraphine/gallery/seraphine_image_7515814455928183144.jpg

- This one missed some text on the lower right of the screen, some white "Dola AI" is written there.  Again, if we add this into the junk patter, I only want it to find text.

## Angels/seraphine/gallery/seraphine_image_7515814642642047791.jpg

- Same "Dola AI".  There are several more like that as well, I won't call them all out, but it's another specific patter we can find and potentially add to our junk pattern for text detection.

## Angels/seraphine/gallery/seraphine_image_7518030909567781676.jpg

- This one cropped some of her dress/body off in the composition/framing, so fine tuning for why or at least understanding why it chose to do that is interesting.


## Angels/seraphine/gallery/seraphine_image_7518031624882793107.jpg

- This one cropped the top properly in composition, but missed a black bottom border during the initial cropping phase.

## Potentials/Afton Voss/gallery/afton_voss_shot_20260922114007.jpg

- This one more agressively cropped some of the bottom of the image, potentially cutting off part of the subject's legs.  Fine tuning the cropping logic to avoid removing important parts of the subject while still handling overlays correctly would be beneficial.  I think this is an example where erasing ahead of that second crop could help preserve more of the subject while still managing the overlay effectively.

## Potentials/Amara Berkley/gallery/amara_berkley_shot_20261010125440.jpg

- This one seems to cropped more of the right overlays without attempting to erase them, which also suggests that erasing before the second crop would be more effective in preserving the subject while still handling overlays correctly.

## Potentials/Fia Hadley/gallery/fia_hadley_shot_20261010125509.jpg

- This one did a great job of cropping the overlay and the eraser did a good job of finding the text and blending it way instead of cropping off the legs.  It demonstrates a good balance between overlay removal and preserving the subject in the image.  This is a solid one to ensure we don't break when making other adjustments to the cropping and overlay removal logic.
```
<!-- markdownlint-enable MD013 MD009 -->

## Intake restart and feedback handling, Oct 27, 11:44 (verbatim)

Coverage: feedback disposition is in the plan index; I30-I37 own intake
implementation/A-B work; template migration is deferred. N11/N12 own the
original-name conflict subsequently resolved by the user's clarification.

<!-- markdownlint-disable MD013 -->
```text
I would like to start on implementing the changes we need for fixing, A/B texting, etc... for the intake, we can defer work on the templates until later and I have other feedback items in the C:\Soverign-Territories\soverign-territories\feedback that I wrote up as well. Ideally, we look at that directory and ensure all feedback items are incorporated and the ones we have in docs/plans would be _archived like the others as part of our working agreement so I know what feedback has been taken and what is still "live" feedback unhandled.  Can we first take care of the C:\Soverign-Territories\soverign-territories\feedback files and then get started on the implementation of the feedback items from today.  If more recent feedback supercedes any previous feedback items - please stop and ask me about them.  Ideally the everything in the feedback is cleaned up and only have open items you have not handled active.  Which there can be a few that I just wrote and we haven't discussed.  But if it's just a question and it's answered, please update those feedback items with proper information and archive them - like the others are archived.
```
<!-- markdownlint-enable MD013 -->

## Eraser preference and face-overlapping oval, Oct 27, 13:26 (verbatim)

Coverage: method preference recorded above; I38 owns the additional case,
automatic UI-mask proposal and isolated reconstruction experiment.

<!-- markdownlint-disable MD013 -->
```text
LaMa seems the best in reviewing all the images - the others don't seem to capture enough of what the image is in the section to know how to paint it properly with removing things.  Not sure if there are other open source techniques to try as well.
```

```text
## Artists/Fantasy/gallery/fantasy_shot_20260902204526.jpg misses the oval entirely that spans the entire top and her head is covered by that oval and the arrorw icon at the top right.  So this is where the overlay on the oval detection is a good thing to look at.  There's others that just crop that way, which is fine when it doesn't cut the head off - but figuring out how the eraser can actually replace that would be awesome.  I am using the magic eraser in the google files edit application and I know it uses some AI behind the scenes to handle the erasing - there's where I was wondering if there isn't a library that does exactly that available instead of me having to select that oval by hand and let it bring back the picture and her head.
```
<!-- markdownlint-enable MD013 -->

## Sample acceptance and reference-based detection, Oct 27, 14:28 (verbatim)

Coverage: example-specific acceptance/review gate above; I38/I40 escalation,
I41 references/false positives, I42 enhancement recommendation, I43 expanded
sample and I37/rebase acceptance. Implementation remains open where indicated.

<!-- markdownlint-disable MD013 -->
```text
I think the head overlay reconstruction is fairly decent and much better than just cropping it.  So the series of crop, erase, reconstruction, composition to get to a recommended gallery photo are good for those photos that need it rather than cropping parts of the body.  I also think that some cases the advanced reconstruction even of the GMW logo could help that as well.  Using the initial simple erase should focus on areas of small icons, text and pieces that aren't large or aren't transparent of have an overlay.  Also the larger GMW circle is in other places on the image in some cases and I noticed in the larger gallery it was missed as well.  The other thing is making sure it's not a false-positive on the overlay might also be good when it's a large area it finds or thinks it finds.  We could alway keep an original of the GMW logo somewhere to check.  Same with the oval pill - just to ensure we are detecting things properly and not false positives in over lays.  What do you think about that.  I'd actually like to see the full gallery rebase done as soon as we're confident in all the updates via the samples.  If we need one more larger sampling of known images we need to test with as well as other sample of the good images that don't need any processing to make sure all the detection, cropping, erasing, recontructing and composition of the photo for the gallery are good as well as the denoise, tone and sharpen approaches to try to get to all those enhancements so I can start to figure out if any of those other enhancements after the initial cropping are necessary or not.  Ideally, if we can auto-detect blurry, figure out if denoise or tone are better due to lighting issues - we can make the final recommendation the "best" one we can detect as part of the intake.  Make sense what I want?
```
<!-- markdownlint-enable MD013 -->

## Face usability, Junk, duplicates and cutover follow-up (verbatim)

Coverage: I44/I45 usability/Junk, I46 replacement/duplicates; rebase C8/C9
core seeds and sandbox/production gates; family N7/N9/N12 grouping/name
correction. Original wording is retained; implementation is not implied.

<!-- markdownlint-disable MD013 -->
```text
Finally - if we find an image without a usable face those should also be detected and put into the _junk appropriately.  That could be a completely blurry one we can't sharpen.  A photo where the person is looking away from the camera and the face is not shown well and results in a potential without matches or matches other like faces that aren't really usable.  I don't need to have potentials where ultimately they aren't usable.  That's what the _junk was for and I think maybe we lost that somewhere as I see one picture for Drakness or Drakniss or Nyxene - I forget which one - that is in the library and doesn't even have a face it's like a cropped middle body or arm.  So that detection is also something needed at the first pass of the intake to see obvious junk as well as at the end where we just can't get a decent picture even after all the steps - like if the overlay covers the face and what we get after all the processing is a blur of a face - and cropping doesn't save it either.  That's just _junk I don't need if we can't get it right.  That's probably the final aspect of the intake processing.  It should show in the gallery if I want to see the junk as well - but most of the time I don't care about them other than making sure junk is truly junk and not a review.  Finally duplicate processing was also in place either if I drop the same image in again by accident or somehow I have two images that results in the same image.  The duplicates is probably less important than junk - but sometimes a duplicate may be that I want to just send an image back through and replace the other one if by change it comes out better.  So the older one already in a library would move to the duplicate instead of rejecting the new one.  Update the plans with this and I think we're nearly 100% complete with the intake processing and being able to do a rebase with only keeping core images with x.xx and above assigned to the Angels/Sisters or the photo workflow photo I have picked to keep those likenesses and then let the rest of the rules play out the right way - likeness grouping, auto merging in/out, family naming based on likeness groupings that don't auto merge but are so close we need to have them as models with family names tied to the angel or sister they align to.  Finally - then I can go back and work on renaming the originals that are not named correctly and getting the sandbox 100% validated so we can then re-run the processing on the production library to get that 100% accurate.
```
<!-- markdownlint-enable MD013 -->

## Experimental erase first review, Oct 27, 15:23 (verbatim)

Source: user-tagged `feedback/_archive/experimental_erase_feedback.md`.
Coverage: I47 display and I48 integrated single-example branch. No source
move or alteration was performed.

<!-- markdownlint-disable MD013 -->
```text
# Experimental Erase Feedback

In general, I'm not entirely sure what the final output recommended image is in the .html page.  I see the original, saved V16 version, control, etc... but I honestly don't know what the final one from the intake is in the report.  Would be nice to see that one as the 3rd image ... unless that's what the V16 version is - but if that's the case, then sometimes it doesn't pick the right one based on my visual.

Something is off in the flow and I'm unclear what based on the output.  Here's feedback on a single one and we might have to look at this and re-do the output or check the flow to make sure things are clear to me on which images flow downstream and which are rejected.  Maybe somehow indicating that as some icon on the image or border thick red to show it's rejected so it makes more sense in how the images are shown and explained.  Maybe even wording underneath the image to indicate its status would help.  The table is clear, but confusing when I look at the images.

## Angels/angelica/gallery/angelica_shot_20261010125309.jpg

- It seems the first crop didn't really remove anything significant; the intended area for erasure is still visible.
- The eraser mask did get some stuff, but because the first crop didn't pull some of the things off like the bottom controls or other pieces on the bottom and top of the image the eraser mask did have a lot to deal with.  I understand we want to leave the actual image intact, but it makes the eraser's job more challenging and less effective.  I did ask for more concervative first crop, but this might have been a bit too conservative.
- The head reconstruction of the hair and the top bubble were actually effective, however that image did not go into composition for the final crop and getting the right picture to denoise, tone and shapen.
```
<!-- markdownlint-enable MD013 -->

## Updated sample rerun authorization, Oct 27, 15:40 (verbatim)

Coverage: I47/I48 implementation and the updated 100-image run above.
This explicitly replaces the prior single-example-only pause; I49 and the
other unresolved quality/acceptance gates remain open.

<!-- markdownlint-disable MD013 -->
```text
Well - I do want the latest feedback to drive updates necessary and to re-do the run of the 100 images so I can very those updates and continue the validation process as a whole.
```
<!-- markdownlint-enable MD013 -->

## First Angelica flow correction, Oct 27, 16:29 (verbatim)

Coverage: reopened I48, first-crop/complete-overlay work I49, and single-example
acceptance gate I50. This review rejects treating the previous integrated
reconstruction as finished composition or visually validated clean output.

<!-- markdownlint-disable MD013 -->
```text
In looking at the updated review - I still see the first crop is leaving a ton of items at the top and bottom that aren't part of the image or the bubble.  So the eraser doesn't find all the things it needs to erase and wastes time on items that would have easily been cropped on the bottom.  Now there is text and a small ball on the lower right above the black borders (that should have been cropped) that do need erasing as well as text across her thighs at the bottom.  Plus the icons on the lower right side.  So until we get the first crop reset to doing it's job - the remainder are less relaiable.  Lastly the final recommended image carrys forward those black border at the top and bottom - so while the reconstruction works - it's not cropping away all things through the process and the eraser has missed stuff due to the first crop and the final composition is still getting an image from eraser and not the reconstructed version.  The enhance denoise is not getting the headoverlay composition and looks like those enhance phases are still taking the headoverlay construction, not composition - which does attempt to crop some stuff, but since the previous stages left so much the headoverlay image still has a lot of stuff on it.  Are you actually inspecting each image yourself to ensure you believe it's makint the right choices?  Seems like you are only cherry picking some things and not actually following the output and reading the notes properly.  Please ensure you inspect each one with this feedback for the first angelica image and then we need to fix the flow again.
```
<!-- markdownlint-enable MD013 -->

## Reusable patterns, 100-image proof and Comfy end to end, Oct 27, 18:56 (verbatim)

Coverage: I52 (pattern library), I53 (100-image proof), I54 (rebase), I55
(Comfy Prime sample), I56 (end-to-end vision).

<!-- markdownlint-disable MD013 -->
```text
Yes, we want to save what we can when we see patterns and make that a resuable approach so we can extend to other patterns we will encounter as we run through the 2000+ images.  Many are clean - but some do have variations on the patterns Dora AI as one I mentioned earlier for Seraphine and other writings on some.  It doesn't have to be 100%, but it needs to be capable of handling patterns and only allowing simlple things to slip through for ComfyUI to eventually handle.  So, go ahead and do everything that's necessary to get these 100 through and proof each of the 100 as that'll find out if we really hit all the pieces.  The larger masking areas along the sides are likey a common pattern, the oval/reel bubble, the common black borders and sometimes just icons, the GMW icon and I'm guessing others will show up over time.  Keep iterating until 100 are clean and then I think you can run the entire rebase all over again and send just 20-30 through to Comfy for the Prime pose renderings - including the new 3/4 pose.  Just 1-2 images per workflow are fine to see that image do get generated properly that we could pull back into the gallery_generated images alongside the gallery and it's other variations for use within other later stage workflows in Comfy.  Basically then we can actually take a new image, pull it in, run likeness, assign it to a person, send it through the Prime flows - take the Prime and Prime Bare and run it into 2_Studies, 3_Layers, and 4_ and 5_ for example.  Getting an end-to-end generation for a new image (or one I pick in the GUI to push the same process) and see the final scene without me having to run all the iterations by hand.  That's vision man!  Automation at work!
```
<!-- markdownlint-enable MD013 -->

## Ten-image sample request, Oct 27, 17:52 (verbatim)

Coverage: I51 first sample (`sample10-v7-20261027`) and the reference-pattern
question (I41 and reel layout profiles).

<!-- markdownlint-disable MD013 -->
```text
Have you re-run the 100 images we had planned to run originally through the process to prove the image processing?  You could probably run 10 of them and do the same level of inspection you just did for the one Angelica photo to see how things are progressing and whether or not we need to capture existing images for erasing patterns or if we're getting good at it without all that.
```
<!-- markdownlint-enable MD013 -->

## Angelica v7 approval, Oct 27, 17:24 (verbatim)

Coverage: I50 closed for this one example; generalization is I51.

<!-- markdownlint-disable MD013 -->
```text
That one actually looks perfect.  I understand that the area near the handbag and her hand is blurred or synthetic, but the icons and clutter had to be removed to get a clean image.  This is a very positive sign, but this is only one scenario of the overlays - but it's actually a solid test of a screenshot with a lot of extra stuff on it and the need to reconstruct the head/hair as well as cropping and erasing properly.  Once we get this done - hopefully the fixes translate to other images and aren't so specific to this one image.  But we can test that as well looking at the next series as there are several more coming in that are with the GMW logos or screenshots.
```
<!-- markdownlint-enable MD013 -->
