# Project Status

**Updated:** 2026-10-30 · This is the one working document: where the project is, what has
been decided, what is open, and what is next. Rules live in the canonical docs listed in
[README.md](README.md); this file only tracks state and decisions.

**Oct 29 final CI policy:** the user explicitly requested fast routine CI
with slower/full regression suites only on specific demand. PR/main CI now
runs hygiene/data checks and lightweight gate/isolation guards on 3.14;
no dependency fallback starts full image regressions. Explicit dispatch
retains full offline regressions/mutations and optional compatibility.
Targeted local testing and real-image sandbox acceptance remain required.
PR #2 merged at `3b7016a` after the passed fast CI run; the earlier full
3.14 run passed at a preceding code head. The final handoff records the tested
heads and run IDs; older-Python acceptance is not claimed.

**Oct 29 branch-closeout result:** PR #2 is merged and work continues on
`work/sandbox-rebase-acceptance`. This does not close unfinished plans.
Bounded D17 triage is recorded in [the plan index](plans/README.md): T6
recovery is implemented and tested; the newly identified T12 performance
decision review precedes S15 and the fresh sandbox rehearsal. No broad plan
moves, history rewrite, feedback cleanup, Production change or full intake is
part of branch closeout.

**Oct 29 performance/review clarification:** the paired 128-image v22 profile
is evidence, not final sign-off. Useful person framing must be assessed rather
than omitted for speed; this does not require restoring redundant padded
diagnostics. Workflow-sized padding belongs only
on the recommendation and denoise/tone alternatives. v23 now runs person
detection on no-proposal images and can select a guarded composition; actual
comparison output, profiling and visual review are now verified for the
authorized sandbox iteration. The fixed 128-image v23 pass took 974.34 s;
the unprofiled fixed 30 took 222.75 s. Fourteen guarded compositions are newly
recommended; padding falls from 539 eager outputs to 375 selected/denoise/tone
outputs. T12 records the slower throughput, exact artifact parity and retained
safety checks. All 32 review sheets were inspected; a definite inherited
nested-phone/UI miss remains under I60. This is not production-quality
acceptance. The new S15 inventory preview is 3,072 inputs; no moves or cast
decisions were evaluated.

**Oct 30 sandbox checkpoint:** tested recovery preceded the full v23 intake:
3,072 outcomes, no assessment errors, and an independent launcher check passed.
The revised core-cast preview accounts for 2,793 people separately from 279
Artist outcomes: 1,218 cast retained, 48 eligible releases and 99 Review holds.
A reproduced/tested incoming-download naming fix recognizes 352 existing
filename IDs without altering frozen sources or thresholds; 67 focused tests
passed. Recovery and the fix are pushed as `19e4f76` and `1d9d738`.
All changed-output sheets, non-retained destinations and release triples
received AI screening; all measured exact-face/source/model bindings verify.
The [cast owner](plans/2026-10-23-cast-seeded-library-rebase.md#revised-v23-preview-and-first-pass-audit)
records the evidence and human review priorities. A complete 72,991-file
pre-install snapshot passed verification. Installation began at 00:54 -05:00;
its slow derivative stage exposed repeated configuration/root resolution.
A live sample and regression identified the cause; the narrow native-owner
fix passes 68 focused tests and reduces one identical real guard check from
5.602 s to 0.597 s. The first attempt was stopped before publication, all
2,868 Working input hashes/catalogue verified unchanged, and staging preserved
with a durable receipt. Apply correctly refused the old engine hashes;
supported measurement-reusing replan now rebinds the preserved preview,
without repeating intake or bypassing the guard. Compare all assignments
before retrying apply. Independent installed check and actual viewers remain
pending; [performance T16](plans/2026-10-28-intake-performance.md#oct-30-measured-installation-blocker)
owns the real retry measurement.

**Oct 30 install blocker:** the engine-bound retry completed all 2,793
derivative sets and retained details but exited at 08:15 -05:00 before
publication on unowned legacy cast derivatives (1,218 padded and 1,183 head).
The plan remains `preview`, `previous` is empty, and complete staging is
preserved. These old files are not proven reproducible. Guarded completed-stage
verification/reuse and explicit exact-byte legacy preservation are implemented,
regression-tested and pushed as `81325da1f`. At the user's 09:22 pause,
the measurement-reusing replan was stopped before publishing a new preview;
the completed stage remains intact, `previous` empty, and plan `preview`.
The user resumed work at 09:53 to reach human review. Supported replan
completed at 10:03:30: all 2,793 rows and frozen input/policy/catalogue bindings
are exactly unchanged. The completed-stage read-only check passed at 10:45:35
(2,793 photos, 48,792 files). Apply reverified the full backup and stage,
then rolled back at 11:46:33 when Explorer's handles on `Various/gallery`
blocked the category rename. All 2,868 Working input hashes and the source
catalogue independently verify unchanged; the plan remains `preview`.
Complete staging and file-empty rollback scaffolding are preserved. No apply
is running; Explorer still held two handles at 11:57. Release that lock before
retrying; never force-close handles or bypass integrity guards. The native
intake report is available for human image-quality feedback, but actual
installed viewers remain pending. The
[11:57 checkpoint](recap/2026-10-30-1157-recap.md) records the current blocker.
The [pause recap](recap/2026-10-30-0922-recap.md) records the earlier pause,
not the current running state. See the
[recovery runbook](art/likeness.md#running-and-observing-a-long-rebase).

**Oct 30 remaining boundaries:** native inspection confirms two cleanup
limitations: the inherited nested-phone/UI miss and the newly reported
Angelica bottom-navigation strip. No proposal is not proof of clean pixels.
Artists remain outside general people matching; the suggested physical
Artists/Humans/Animals split and `_Intake` rename are unapproved proposals,
not changes to make during this installation. Denoise/tone remain
comparison-only pending a calibrated quality/detail-preservation selector.
No plans were falsely closed or raw feedback removed. Production and
historical Source remain outside the operation.

**Oct 29 CI cost correction:** routine PR/main checks use Python 3.14 only;
exhaustive mutations and optional 3.12/3.13 compatibility are explicit
dispatch coverage. No duplicate feature-push CI. The failed PR matrix spent
298-358 s per runtime on exhaustive mutations, then exposed three tests
depending on a locally installed cleanup recipe. Their fixtures now install
their own tiny recipe; 77 focused tests passed. The later fast CI run passed;
this is not a full-suite result for every later documentation/policy change.

**Oct 29 quality-gate decision:** routine commits retain hygiene, script
analysis and data validity, not unit/mutation suites. Push no longer repeats
checks. Deep suites run explicitly through `bin\check.cmd --deep` and in CI;
targeted tests remain required during development. Representative schema/code
checks measured 12.95 s, empty push selection 1.05 s. The CI coverage follow-up
adds branch pushes, all five omitted offline modules and a test-inventory
guard; full mutations run once, and unit regressions no longer repeat through
both manual hooks and the launcher. The consolidated launcher passed 1,125
tests locally. CLI GitHub authentication fails, but the authenticated
integration can read runs; remote matrix acceptance remains tooling D20.
Change-aware follow-up: local `validate --changed BASE` and CI share a
conservative selector. Workflow-only work no longer runs image/library
suites; shared/infrastructure dependencies expand coverage, main/manual
acceptance remains full, and isolated mutations run for schema/validator
changes or full fallback. Test launchers now scope default temporary files
under ignored repository `tmp`; the retained fixture's explicit root scratch
bug is fixed. No Git history rewrite, merge, cache/session deletion or
Production operation is part of this fix.
See the
[quality contract](QUALITY-GATES.md) and tooling D18.

**Oct 29, overlay-first checkpoint (v22):** the prior preparation recipe
checked overlay/border proposals before person segmentation. A paired 128-image worker profile
took 524.48 s eager versus 302.50 s gated (42.3% less elapsed), avoiding 90 of
125 subject calls. All 128 recommendations and 1,569 shared image-artifact
hashes agree; 16 composition comparisons (48 artifacts) were omitted. This is
historical v22 evidence, not acceptance of suppressing useful composition.
Both fill stages and their 43 calls / 116 neural patches remain unchanged.
Two unprofiled 30-image repeats average 77.32 s versus 122.76 s eager.
Detailed substeps, input-path costs and overlapping erase/reconstruction masks
are recorded in the [performance plan](plans/2026-10-28-intake-performance.md).
Reconstruction currently also accepts confirmed background marks: whether to
restrict it to person overlap is discussion T8, not an implemented rule change.
No full intake or fresh sandbox rebase is running; T6 recovery is implemented,
and T12's current measured disposition now permits the intake-only sandbox
iteration, not installation or Production cutover.

**Oct 29, T6 recovery implementation:** per-image checkpoints bind the ordered
source paths and hashes, recipe, configuration receipt and every artifact.
The report staging tree persists across retries, while completed worker
artifacts are removed as their rows are safely materialized. The 74 focused
image-preparation tests and 11 temporary-storage tests pass, including changed
evidence rejection and lock reacquisition after a subprocess exit. Review's
26 tests also pass after shortening Windows temporary evidence filenames that
exceeded `MAX_PATH`. The subsequent focused launcher test environment resolves the earlier
`comfy_workflows` import failure; 216 current focused regressions and 19/19
isolated validator cases pass, including v23 selective-padding recovery and
downstream retained/staged-history compatibility.

The follow-up v22 cProfile locates 114.85 summed worker seconds in the
proposal bank and 59.30 in glyph checks, with overlapping detector times. A
bounded A/B on the same 128 sandbox inputs confirms exact glyph-output parity
and 51.3% lower glyph-only time (25.806 s to 12.573 s) from RGB-bound and
component-mask reuse; it does not measure full-intake wall time. Person
inference and LaMa fill remain the largest behavior-sensitive targets.

**Oct 29 v23 composition and padding:** no-proposal rows now run person
detection. A composition is selected only when the grown-subject mask-loss
guard passes; segmentation can still omit hair or feet, so review remains
necessary. Other composition suggestions on proposal paths remain
comparison-only. Padding is limited to the recommendation and denoise/tone
alternatives; masks and interim candidates stay native-sized. A focused v23
regression exercises selected composition and exact-retained-source padding.
The bounded rerun, actual PNG/padded-image review and measured repeat now pass
as recorded in T12. Full-run I60/C8/C9 and actual viewer acceptance remain
open; no Production cutover is implied.

**Oct 29, 08:45 historical checkpoint:** the earlier fresh intake stopped without
a receipt after 1,445 ordered outcomes; its cause is not established.
The restart was deliberately stopped for bounded profiling. T6 was still a
prerequisite at this checkpoint. No full intake was running. A fixed 30-image worker profile identifies subject
detection and masked repainting as about two-thirds of image-worker time;
original read/copy/hash work is small. One exact-integer overlay optimization
averages 2.8% less elapsed time over two A/B pairs, with identical decisions
and 408 image artifacts; 133 targeted tests pass. Earlier running statements
below are historical checkpoints, not current process status.

## Where we are

Design and art are ahead of gameplay data. The repo has no Unity project yet.

| Area | State |
| --- | --- |
| Art pipeline | Working. `data/art/` identities + pieces + templates compile to prompts via `tools/generators/gen_prompt.py`. Core wardrobe plus six theme packs (Greek, Roman, Egyptian, Norse, Celtic, Thanksgiving). Every sister has Signature, Glamour, Elegant Casting, Staged Enchanted Evening, **The Dawn** (rising in her homeland) and **Robe** scenes, each with its own background. How to add to it: [art/tutorial-art.md](art/tutorial-art.md). |
| ComfyUI workflows | Automated prompt/workflow generation and home-workspace sync. Qwen and MiniMax are tracked; FireRed tests are local. `ST0`–`ST6` are the masters; curated workflows are never regenerated. See [the workflow model](../workflows/README.md). |
| Face likeness | Local inspection, shared reconciliation, staged actions and prepared sandbox clean-start use supported launchers. Rules/recovery: [likeness guide](art/likeness.md). Draft policy blocks production matching; real acceptance is unfinished. |
| Original photos | Prepared sandbox publication retains originals/variants and maintained derivatives. Legacy `originals`/incremental `library` cutover and selected-input acceptance remain gated. Choose the supported flow in the [photo-library runbook](art/original-photos.md#choose-the-right-flow). |
| Video | First pipeline built: `data/animation` cards (actions as `Motion:`/`Scene:` blocks with transitions) -> `gen_animation.py` -> MiniMax H3 workflow from `ST6_MiniMax_Reel` (9:16, the default) or `ST6_MiniMax_Match`. Three Drakness example clips are deployed; none rendered yet. Guide: [art/tutorial-video.md](art/tutorial-video.md). |
| Sister variants | Every sister has a **Signature Shiny** (`<slug>-scene-signature-shiny`: the Signature card with a prismatic `overrides.palette` and a glitter-sheen effects line), a **Battle** scene (war gear piece plus homeland battlefield), a **Bond** scene (first meeting with her Elder Dragon) and a **Dawn Rising** video card. First new culture pack: `themes/danish` (Snow Queen inspired) with `draknira-scene-danish`. Prompts and workflows built; none rendered yet. |
| Vision roster | 30 cards (10 Drakn sisters, 10 bound heroes, 10 Elder Dragons) plus 10 pets, all with art identities; prompts generated. |
| Gameplay cards | `data/cards/sovereign-dawn/`: 219 cards, ids `SD-001`..`SD-219`. `SD-041`+ is legacy content (Fire/Water/Earth + Neutral). |
| Validation | Routine commits check schemas/card-art links, not mutations or unit suites; push does not repeat hooks. Local/CI dependency-selected suites and explicit isolated full validation follow [QUALITY-GATES.md](QUALITY-GATES.md). Mutations operate on a disposable copy, not live data. |
| Starter decks, packs, manifests | **Broken** (see Data debt). |
| Unity client, backend | Not started. |

## Plans and the queue

The plans, their status and what each is are listed in [plans/README.md](plans/README.md); what is open, by priority and owner (what needs you first), is [todo.md](todo.md), generated from them. This document holds only what is decided and what is still a question.

**Oct 28 prepared-image decision:** final intake recommendations now supply
Gallery, likeness and ComfyUI; the obscured original is not preferred merely
because it is original. Keep exact originals, processing history/masks and the
exact aligned face used by SFace accessible per photo. Reconstructed pixels
remain labelled synthetic; assignment is not automatic replacement of a
protected identity anchor. Full sandbox iteration is authorized, including
non-core cast release and family regrouping under existing thresholds.
Investigate Review volume and inspect moves; do not lower thresholds to force
zero Review. Production remains separate.

**Oct 28 storage decision:** after the storage roots and writer routing are
structured, the user prefers to recreate the sandbox Working tree wholesale
from the verified Production/Source baseline rather than manually retain or
prune old sandbox reports, run outputs, backups or undo data. Sandbox recovery
copies are not required. This does not authorize deleting the sibling immutable
`Source` snapshot, Production, or active source photos that exist only in the
current Working tree. Inventory those source deltas and confirm the exact reset
boundary before applying it. The Oct 21 Source snapshot still matches all
8,842 shared Production files, but Production has 358 additions and three
removed `_junk` files, so it is not the current baseline. A hash comparison
found 89 Working-only `Various` JPEGs and 17 gallery metadata files (none in
Source); preserve the photos and carry the metadata for review before any
Working rebuild. See the [storage and retention plan](plans/2026-10-28-storage-operations-and-retention.md).

Storage-path migration is underway, not complete. The shared resolver rejects
unknown, overlapping, escaping, active-category-overlapping, reserved
`_archive`-overlapping, and reparse-point destinations. Reference workflows,
selected reports, likeness caches/evidence, retained action journals,
junk/retired operations and readers, and incoming duplicate checks now route
through configured roots. Likeness reports, eraser/intake-sequence benchmarks,
and overlay-review reports now also resolve configured destinations; nested
intake validation handles configured sandbox-state roots at arbitrary depth.
Focused verification passed: 74 duplicate/likeness tests, a 77-test
storage-root regression set, and seven targeted regressions for the latest
report routing. The full `bin\test.cmd` launcher passed after those changes
(339 tests across seven suites). The configuration schema/receipt contract
and full writer/reader inventory remain open. That checkpoint preceded the
Oct 29 reset recorded below; its Production baseline and read-only full-reset
preview were verified.

**Oct 29 storage configuration progress:** the versioned schema now covers
the reference ComfyUI workspace and the Production, sandbox, model-cache,
install, input/output and shared roots. Those roots have matching environment
overrides and runtime checks for absolute paths, overlap, escaping workflow
subpaths, and safe workspace names. Workflow deployment, input synchronization,
backdrop workspaces, reference execution and output browsing use the shared
resolvers; workspace configuration edits validate and publish atomically from
owner-locked staging under ignored `tmp`. Configuration receipts are now
included in full reset previews, library-backup manifests and
image-preparation manifests. Focused coverage passed for workflow
configuration (77 tests), preparation/backup (40 tests), and sandbox reset
(13 tests); the full `bin\test.cmd` launcher passed 358 tests across eight
suites.

The refreshed read-only `sandbox-reset --full` preview confirms the exact
Working target and current managed Production baseline of 9,200 files
(5,614,845,723 bytes), excluding 56,059 files (21,429,886,503 bytes) in the
configured operational roots `_actions`, `_archive`, `_backup`, `_generation`,
`_likeness`, `_reports`, `_sandbox-state` and `_tmp`. Production `_junk` and
`_retired` remain in the baseline because they hold user-dispositioned photos
and provenance. The preview found 358 Production additions, 3 removed `_junk`
files, no changed or unclassified paths, and the expected 89 Working-only
photos plus 17 metadata files to preserve. Its receipt contains both
64-character configuration hashes; reset readiness is true with no blockers.
The verified report is
`tmp\storage\full-reset-preview-protected-photo-roots-20261029.json`. S3, S10,
S12 and S13 are complete. The versioned retention ledger
automatically registers new intake/rebase runs; unregistered or incomplete
runs default to keep, only applied runs can be accepted, and only older
accepted runs can reach explicit prune approval. Pruning rechecks a complete
tree fingerprint and Working text dependencies, writes a receipt, and
refreshes regenerable intake-history pages; a report-only repair command can
close an interrupted history publication without restoring deleted run data.
The full fast suite passed 363
tests across eight suites; the latest retention/history-refresh and
auto-registration regressions passed 6 tests.
The live read-only B: retention preview found 10 unregistered runs, kept all,
and wrote nothing. After removing unnecessary tree/reference scans for
no-candidate previews, the measured preview duration fell from 162 seconds to
0.59 seconds. No existing Working run has been registered or deleted. A read-only duplicate
measurement covered 270,191 files / 146,857,778,934 bytes and found 81,028,741,928
bytes of exact duplicates; no deduplication was applied, and S11 remains open
for storage-sharing/recovery validation and B: I/O measurement. S4-S5,
remaining storage receipts and the writer/reader inventory remain open; the
Working rebuild is now verified below. `ST-v9` remains a self-contained historical
bundle; the current retention tool is scoped to the exact sandbox Working
root, so `ST-v9` remains untouched.

The Oct 29 routing follow-up now sends ComfyUI config staging through the
configured temporary root under ignored `tmp`; workflow backup writers use the
configured backup root and record source/destination paths in per-stamp
receipts. Original-photo rename maps use the configured actions root with a
receipt and legacy-read fallback. Likeness diagnostics restrict explicit
`--out` paths to the configured reports root and publish a receipt. The full
`bin\test.cmd` suite passed 363 tests; focused routing checks also passed.
These checks used temporary roots only. The configured active root still
defaults to Production.

The full-reset apply is implemented with configured-root exclusions, staged
hash verification, a receipt, an owner lock, and rollback/recovery tests.
**The clean Working reset is now installed and hash-verified.** Explorer's
hidden handles to `_reports\library` caused the two original denied swaps.
Gracefully closing its window released them. The next swap committed, then
hit Windows MAX_PATH while removing nested old backups. Reusing the backup
extended-path helper fixed cleanup; committed recovery now returns the existing
receipt without starting a second reset. Reset/staging regressions pass
28 tests.

The exact fresh baseline was 9,307 files / 5,694,510,002 bytes: 9,200 managed
Production files, all 89 sandbox-only active photos, 17 metadata files in
`_reports\reset-review-bundle`, and its receipt. Six operational roots,
including the temporary root, were empty after cleanup. This removes 260,884 old
files and 131.47 GiB of logical bytes. Source reverified all 8,845 historical
files; Production and ST-v9 remain untouched. See storage S14 for timings.

Fresh rehearsal uses new `--baseline working`, not the historical Source
default: current assigned galleries plus current Various are frozen in a
hash-bound run-local overlay. The supported dry-run counted 3,072 outcomes
(2,700 assigned inputs plus 372 additions; 75 newer-byte substitutions).
The full v21 intake is running as `fresh-r21-20261029` with three workers.
Source stays immutable. Generated reports are not input candidates; their old
volume affects recursive inventories/history verification, not the canonical
candidate enumeration. Overlay/input-copy and receipt staging now use owned
configured temporary roots; verified complete mirrors/reports can resume after
a receipt interruption. S4-S5 lifecycle/publication gaps, fresh-run validation,
matching/move/visual audits and final performance comparison remain open.

The v11 sequence is promoted as preparation recipe v17 through shared masked
reconstruction code; published v16 evidence remains readable. The new
`r17-20261028` sandbox run previews 2,741 outcomes (2,700 immutable images plus
41 additions, 74 newer-byte replacements). Intake-only preparation and its
artifact check completed: 2,294 original recommendations, 436 prepared outputs
and 11 junk candidates; no processing-error outcomes. Full visual/move audit
and installation remain pending; successful artifact verification is not
visual acceptance.
The core-cast matching preview completed; audit found and fixed quality checks
mixing original pixels with prepared-image face coordinates. A matching-only
replan using unchanged measurements/thresholds reduces Review from 158 to 89
and removes all 55 stale app-bar holds. Thirteen non-core cast photos are
released in the preview; none have moved. Remaining cleanup misses and
destination/core/family audits still gate installation and new Prime samples.
Targeted v18 proofs now remove the two missed transparent GMW logos and three
missed outlined search pills, while preserving clean photo controls. A
bottom-panel flatness guard also stops two clean portraits being cropped as
phone UI. All 186 integrated tests and a real preparation-launcher proof pass;
v17 reports remain readable. This is bounded correction evidence, not a new
all-image v18 rebuild or full cleanup acceptance. Focused visual review,
remaining residuals and assignment audits still gate the next rebuild/install.
Before starting, validation found 134 unlisted additions in immutable Source.
All 8,845 original manifest entries were byte-exact and all extra bytes appeared
in the prior intake receipt. The extras were moved without deletion to
`B:\Sovereign Territories Sandbox\_source-recovery\20261028-v17` with a hash-bound
receipt; the original manifest was unchanged and full snapshot validation passed.
This recovery is not a new identity decision or a production write.

**Oct 28 v20 targeted PiP proof:** preparation recipe v20 adds a conservative
lower-left inset detector inside a confirmed phone-reel frame. It requires a
small secondary face plus bilateral edge, top-bezel and dark-header evidence;
the mask is clipped at the detected picture boundary. A fresh eight-image
report over exact `r17-20261028` inputs detects Ruby Eden's inset at
`[88, 1579, 308, 1738]`, records outside-mask identity, and leaves the three
clean controls Haniya, Draknora and Odette pixel-identical. Full-size review
shows a soft synthetic patch by Ruby's hand/field; Harlow's chest patch also
remains unresolved. The current Working Ruby replacement has a different hash
and no confirmed reel frame, so this rule does not activate there. User review
must decide whether to broaden detection to non-reel phone overlays. The report
is at `B:\Sovereign Territories Sandbox\Working\_reports\ruby-pip-v20-p3\Working\_reports\preparation\ruby-pip-v20-p3\index.html`.
No full v20 preparation, rebase, install, production change or Prime submission
has run.

**Oct 27, 11:05 review pivot:** intake visual tuning is the immediate priority.
The user's Angels/Potentials review is preserved in the intake plan, with all
26 named examples mapped to border, mask, erase-order, framing and quality
checks. Compare a bounded sample plus controls before changing the recipe;
preserve the completed full-input report and leave its matching preview
uninstalled. Crop-before-erase and the app-bar leg-loss exception are under
review, not accepted defaults. Prompt migration must reconcile the manual
wording, section order and independently placed features with existing person
data, not substitute generic preservation policies as an exact migration.
The requested generic Female move into the Sovereign Females test bed and
category/person workflow paths are planned with reference/compatibility gates;
no set, installed workflow or old receipt was moved by this documentation pass.
Supported non-explicit wording remains the migration scope.

**Oct 27 naming clarification:** after intake tuning, an explicit forced
correction must replace a misassigned effective original name, not merely add
an alias. Preserve the erroneous old value only in audit/undo history.
Later family/current first/last-name changes remain separate from that corrected
original identity; stable person IDs and locked cast slots do not change merely
because a name is corrected. This decision resolves N11; implementation N12
and family acceptance remain open. No existing identity was renamed here.

**Oct 27 intake implementation:** all eight current feedback notes have been
preserved, coverage-checked and individually archived. The preparation options
table now includes unselected UI proposals and diagnostic masks; 61 focused
tests pass. A new read-only-comparison launcher publishes saved-LaMa versus
Telea/Navier-Stokes on the frozen masks: 46 selected rows, 22 compared and
24 explicit skips, with apply/check successful. Report:
`Working\_reports\eraser-compare\intake-20261027-46\index.html`.
This does not fix or accept crop ordering, false masks or framing, and does
not replace the v16 baseline or install its matching preview.

**Oct 27 erase-first iteration:** the opt-in sequence experiment now compares
all 46 frozen sources using localized erase before one guarded residual crop.
Real output inspection caught missed hair/toes despite zero segmentation loss;
composition proposals are therefore comparison-only, retaining the cleaned
full input plus padding. The corrected v2 report preserves original dimensions
for all six named hair/feet/shoes/dress/leg checks, including exact original
RGB for Angelica's feet and Camaris's bun. Selected crop mask loss is at most
0.3897%, with no large screenshot-loss exception or repeated fill loop.
Report: `Working\_reports\eraser-compare\intake-sequence-v2-20261027-46\index.html`.
Mask/border tuning and human acceptance are still open; default v16 is unchanged.

**Oct 27, 14:16 direction:** first crop must only remove confidently
subject-free borders/outside clutter on any side; do not sacrifice hair/head
to remove a pill before restoration. LaMa remains the normal eraser, with a
bounded advanced second-pass experiment for difficult cases, not repeated
unconditional repainting. Preserve pre-loss input for alternate reconstruction.
Pause at each new reviewable result. At 14:28 the user positively reviewed
the Fantasy complete-pill/icon LaMa trial, releasing that example's pause.
Next is one larger bounded sample with confirmed GMW/pill references,
hard negatives/clean controls and unchanged/denoise/tone/sharpen comparisons.
The user wants the full rebase promptly after sample confidence and review,
not immediate installation of the old preview. Reference-based detection,
advanced backend and calibrated enhancement recommendation remain open;
the accepted trial used LaMa, not a separately tested advanced model.

**Oct 27 Junk/replacement clarification:** assess usable visible faces before
matching and again on the final prepared candidate. Obvious unusable inputs/
failed restorations belong in reversible, normally hidden Junk; detector
failure or uncertainty belongs in diagnostic hold/Review. Preserve selected/
protected references and surface conflicts. Intentional accepted incoming
replacements may supersede old versions with duplicate/recovery provenance;
newer does not automatically mean better. Next rebase preview must expose
approved core thresholds and explicitly selected workflow seeds, then group/
merge/family rules. Full sandbox verification and original-name correction
precede production cutover; no new numeric threshold or production apply
was authorized.

**Expanded review ready:** 100 frozen inputs in two 50-row sequence reports
(`expanded-intake-20261027-1` / `-2` under `Working\_reports\eraser-compare`).
Ninety-nine usable rows compare denoise/tone/sharpen, one ineligible row
explicitly skips them; unenhanced recommendations retained. Separate
`overlay-references-20261027-1` / `-2` reports show 110 unconfirmed reference
proposals, not automatic GMW labels. All four apply/check workflows passed;
full normal validation passed 940 tests/30 suites, plus focused final
regressions. These original reports remain historical evidence.

**Oct 27, 15:40 follow-up implemented:** the user authorized updating and
rerunning all 100 after the first feedback, replacing the single-example
pause. The corrected report names the recommendation third, with explicit
status and lineage. Synthetic pill reconstruction now retains guarded cleanup
and feeds its composition proposal and enhancement comparisons; it is only a
review recommendation, never original/core likeness evidence. The same 100
were reprocessed; the final responsive review pages are
`Working\_reports\eraser-compare\expanded-intake-v3-20261027-1\index.html`
and `expanded-intake-v3-20261027-2\index.html`. The v3 pages reuse exact verified
v2 rerendered images, correcting heading overflow without another model run.
All runs check; four integrated head results pass cumulative outside-mask
preservation, 99 rows have correctly sourced enhancements, one skips, and no
detector errors or missing image assets were found. First-crop/UI-margin
tuning and remaining overlay coverage are still open (I49/I41); Junk,
replacement and quality-ranking gates are not implemented by this rerun.
Pause for review of the revised sample; no full rebase or production apply.

**Oct 27, 16:29 review correction:** the previous first-Angelica result is
not accepted. The initial crop retained app panels; composition was unselected
and enhancements therefore used reconstruction, not composed output. I48 was
closed prematurely and is reopened. The new single-source review is
`Working\_reports\eraser-compare\angelica-flow-v7-20261027\index.html`.
Paired observed picture boundaries now remove external UI while retaining
the complete pill for fill. Whole caption/icon envelopes fix residual text,
bookmark strokes and the back arrow exposed by enlarged inspection.
Selected `head-overlay-composition` now consumes reconstruction and feeds all
three enhancements; final geometry is 1080x1690, retaining the observed picture.
Every stage and enlarged upper/lower recommendation regions were inspected,
not just lineage tests. Synthetic handbag/background quality still needs user
acceptance. Pause at I50; I48/I49 and broader intake calibration remain open.
No new 100-image run or library installation followed this correction.

**Oct 27, 17:24:** the user approved the Angelica v7 result, including its
synthetic handbag/hand area. One dense-screenshot scenario is accepted; GMW
logos and other layouts are untested with this recipe (I51).

**Oct 27, night (I52/I53):** overlay handling is a data-driven pattern
library (`tools/art/intake_library/overlay_profiles.json` plus `overlays.py`):
phone-reel frames, corner text and caption blocks, sparkles, letterbox bars,
tilted stickers (polygon masks), viewer corner icons, GMW badges and a
reference bank of logo crops in `overlay_references/`. The 100-image proof
`full100-v11` (`full100-v11b-20261027-1`, `full100-v11-20261027-2`) changed
only the intended rows versus v10; waiting for user review before the
recipe is promoted into intake (I54).

**Oct 25 overnight rendering integration:** Sovereign Females is running at
`127.0.0.1:8188` (ComfyUI 0.38.2, 970 node types). Request preview/prepare/check,
four bounded clothed-preservation edit graph bindings, capability/model checks,
isolated workspace staging, durable submit/run/status/reconcile and explicit
selected-output retention are implemented. Static Gallery selection exports the
same CLI request and displays scoped results; it does not directly launch a CLI.
Selected renders remain synthetic, excluded from original/core evidence, and
can feed compatible pilot jobs with verified sidecars. The combined rendering
and Photo Review regression set passed 89 tests, including timeout, deadline,
queue-order and receipt-writer interleaving cases.

The pilot explicitly uses the running clone's misspelled input root
`Sovereigh Females`; its output root is correctly `Sovereign Females`.
No configuration edit or restart was made. Four jobs from two frozen sandbox
sources were compiled/staged, with editable copies under `Reference`. All four
jobs completed sequentially at the normal queue tail and returned one output
each. Their receipt and hashes remain under
`Working\_generation\reference\overnight-edit-proof-02`; no output was promoted
to Gallery or identity/core evidence. The first cleanup output visibly removed
the source GMW mark; generative detail/pose/proportion changes still require
user review. The server had 1 running / 13 pending unrelated jobs before the
remaining samples were appended; none was cancelled, interrupted or reprioritized.
Default waits for idle; the explicitly authorized append-one option puts one
owned job at the normal tail and waits for it, without priority or interruption.
Transient GET polling failures retry within the deadline, never POSTs.
Backup-first correction changed only SaveImage
prefixes in 114 installed manual workflows; all originals were hash-verified
and all non-prefix data compared equal. Repeated preview proposes zero changes.
Generic Female and other workspaces remain untouched.

Four coordinated tracks remain separate: intake/likeness acceptance; dynamic
execution; shared data-driven `0_Edit`/Prime/Bare/template migration; Gallery GUI.

**Oct 26 outputs browser, cleanup batches and pull-back (R17-R20):** the server
queue capacity is 200 jobs; `run` refuses to submit when it would exceed it and
can pipeline with `--queue-depth`. One request is capped at 64 jobs. Gallery
selection is multi-select, can pick several recipes per stage and filter by
cleanup hint. `cleanup-batch` writes requests for intake photos flagged for
ComfyUI cleanup and never queues. Hints come only from verified/ambiguous new
preparation traces, so the sandbox has none until the R11 full preparation run.
`render-reference.cmd outputs` publishes `_generation/outputs.html` (Masthead
**Outputs**), which browses every ComfyUI output by workspace, stage, variant or
subject, with full view and a pull-manifest export. `pull` copies only the
chosen outputs to `_generation/library/<stage>/<variant>/` with a standard
name (`<name>_comfy_<variant>_<sha8>`), a 944x1104 padded copy and a sidecar.
Pulled renders are their own synthetic `pulled-render` source kind, which is
never identity/core evidence. An empty aborted preparation-run folder no longer
marks every photo `unverified`. A live sandbox pull of the Draknava `0c_Cleanup`
pilot output was verified, and repeating it is reported as `already-pulled`.
Manual `zz_shots` graphs are temporary transport proof, not the permanent prompt
architecture. The first generic Female `0c_Cleanup_Basic` is now data-driven and
generates a repository-only Qwen workflow; it was not deployed or rendered.

**Oct 26 large cleanup run (R25-R28):** `render-reference.cmd overlay-scan`
reruns intake's overlay heuristic over a raw intake mirror and maps hits to
Gallery sources by photo key (2,741 scanned, 107 overlays, 74 mapped);
`cleanup-batch --sources` turns the scan into requests. New bound recipes:
`0b Background Basic` and `0d Deluxe Pose`. The `0d` recipe reuses the "Bare"
graph's settings with a clothed re-pose prompt only; unclothed renders of
intake photos are never produced. 190/190 jobs completed unattended on Sovereign
Females in 7 h 16 min; all 74 `0c Cleanup Basic` outputs were pulled back
automatically, and the other 116 wait for your choice on the Outputs page.
The sandbox Rendering page waits on a stale Photo Review (R30).

**Oct 26 evening, light-grey studio standard (R29 decided):** every studio
prompt now asks for a plain neutral light-grey seamless backdrop
(`backgrounds/studio/grey-even` is the default; cream stays as an option), and
the 944x1104 padding is `originals.STUDIO_GREY` (190, 190, 190). New
`bin\backdrop.cmd` swapped the old cream wording, with backups, in 4,788
hand-made and installed workflows and prompts, including every `zz_Shots`
item; `--check` reports all grey. Existing padded copies change when the
rebase regenerates them. Design positions for the three-quarter Prime pose,
render-assisted identity (query only, never evidence), body edits (a design
branch, not cleanup) and staged per-person ComfyUI preparation (instead of
rendering every photo before assignment) are in the rendering plan (R31-R39).
**Oct 26, 21:48 clarification:** the three-quarter variants are approved,
including both feet grounded with one foot forward and its knee bent.
Preparation is also a character audition: independent face/physique/hair/pose
controls, not mandatory original-body preservation. Source-person identity
and rendered-character resemblance are separate reviews; generated lookalikes
can inform intentional virtual-family/casting choices, never source merges.
A hard source-likeness rejection is not the universal artistic ranking rule.
Full edit migration is P13; a bounded comparison and rendered-resemblance
review are R40-R41. These are planned, not new rendered or deployed recipes.
**Implementation continuation:** both approved poses and shared background,
enhancement and clothed full-length controls now have JSON assemblies,
reusable policy components, generated prompts and Qwen repo workflows.
Five `shared-*` recipes are wired to the Gallery/CLI and freeze their generated
prompt as a hashed compilation artifact. Runtime graph/settings transport is
still manual-Qwen; user visual acceptance remains open. Per-job
appearance changes, Prime execution and rendered-family review remain pending.
New automatic compilations now use person-first workflow/output directories:
`reference/<Person_Name>/<stage>/<family>/`, with recipe, UTC preparation
timestamp and unique batch/job IDs in each filename. Existing compiled
batches retain their old layout; the Outputs browser supports both. Internal
receipts/input staging and Gallery pull-back locations remain unchanged.
Four live shared-pose pilot renders completed and verified the new paths.
The relaxed pose is a useful candidate; grounded candidates still raise a
heel despite two prompt versions. The user explicitly accepts a lifted heel
at 23:12, so this is not a remaining acceptance blocker.
The broader `p1026` comparison has 42 jobs across 21 inspected clothed sources
and is running detached at queue depth 8 (initial check: one running, seven
pending; 34 not yet submitted). The worker refreshes both results pages after
completion and never auto-pulls these pose auditions. Photo Review and
Rendering were republished (R30 resolved); Outputs
now lists 6,968 images before the broader batch. No pose render was pulled.
Later edit variants, formal stage-input/promoted-output contracts and
Alpha/Studies recipes remain manual-migration work. Edits stay optional before
Alpha; user visual acceptance and production rollout remain gated.
The late continuation adds two correctly staged shared clothed Prime outfit
recipes under `1_Alpha/1_Prime`, preserving the old studio-pose IDs and their
frozen paths. Deluxe is a bedroom-scene family, not the grey studio poses.
`cleanup-batch --per-person N` now samples assigned original Gallery photos by
resolution and stable person ID, skipping only exact duplicate bytes.
`render-reference.cmd compare` publishes frozen source/output comparisons by
person/source or matched recipe, with incomplete states and exact lineage.
This is human review support, not automated identity/kinship inference.
Rendering and Outputs now use the same shared header/footer wrapper.
The detached `cast1027-01` worker is waiting behind existing queue work:
63 jobs across 10 Sisters and 11 Angels (cleanup and two Prime outfit views),
no auto-pull. A six-hour maximum bounded deadline now accommodates queue wait
plus large selected batches; queue and batch limits are unchanged.
Fresh intake-only preparation of all 2,741 inputs is also running under
`clean-rebase-20261027-full-intake`; first verified progress 101/2,741.
No matching, installation or production change is claimed.
The later snapshot at 05:30 UTC is 669/2,741 intake outcomes and 11/63 cast
renders completed. The original `p1026` controller stopped on a submission
preflight GET timeout; verified history recovered 15 completed / 27 compiled,
without uncertain jobs. A replacement controller waits behind the cast run
and resumes only the remaining compiled jobs. Typed preflight polling failures
now retry within the deadline; uncertain POSTs still never retry.
Four correctly themed clothed Deluxe bedroom variants are implemented, and
eight frozen samples for Draknara/Angelica wait until both render batches
complete. Their supervisor then republishes a five-batch comparison.
A separate supervisor waits for a verified, error-free intake receipt before
saving a matching preview only; no installation or cast reassignment is
scheduled. The shared generated Cleanup Basic is now the default for new
cleanup proposals, preserving older explicit manual IDs and frozen runs.
Isolated mutation validation is supported through
`bin\validate.cmd --isolated --quick`: 19/19 cases pass with the live schema
hash unchanged. The configured normal validation passed 881 tests in
29 suites including the final shared-cleanup binding. Commit/push mutation
hooks now use isolation too, avoiding live intake readers.
The older cast controller subsequently hit the same preflight issue; verified
recovery found 23 completed and 40 outstanding jobs without uncertain states.
One corrected recovery worker is active, with a verified GET-only retry
heartbeat. Rendering, Outputs, People Review and Artist reports have the new
navigation; a five-batch Comparison refresh correctly waits for active receipt
writers to finish, rather than overriding their lock.
The final queue handoff uses one detached sequencer: wait for cast (eight-hour
bound), resume the same pose receipt with a fresh six-hour execution deadline,
then run Deluxe and publish the combined comparison. Only idle controller
wrappers were replaced; no accepted GPU job was cancelled. This prevents
queue waiting from consuming pose's execution budget. All seven report
surfaces now have verified shared chrome; Comparison currently shows the four
completed pilot outputs pending the final five-batch publication.

Oct 27 continuation: all 2,741 preparation outcomes are verified with no
assessment errors. Matching preview caught a verified-original/newer-Various
duplicate-ID edge case; a narrow recovery-bound curation fix passes 47 related
tests. Subsequent naming-only continuity collisions retain current stable
labels without changing matching, and 22 missing-ID Review holds with 11
colliding filenames retain separate deterministic source-bound names.
Incomplete matching can resume with `--replan` from verified intake and
hash-keyed measurements; it never installs. The final retry saved a
**preview**: 279 Artist inputs excluded from general matching, 1,266 retained
cast photos, and 1,196 accounted non-cast inputs (1,048 non-cast gallery
destinations, 40 proposed cast Review additions, 108 Various Review holds).
The immutable manifest, overlay and live catalogue hashes remain unchanged.
Reversible installation and curation acceptance remain gated in the rebase
owner; the preview has not changed assignments.
All 63 cast, 42 pose and eight Deluxe jobs completed. The published five-batch
Comparison includes those 113 new outputs plus four pilots: **117/117
completed**, 42 sources and 39 people, verified by read-only launcher check.
Outputs indexes 7,081 images; Rendering is refreshed too. No new audition
was imported. Deluxe uses the consistent clothed bedroom theme, but Angelica's
seated output retains a top-cropped face; synthesized unseen details and
wardrobe changes remain visual-review limitations, not accepted identity.
Normal validation passes **885 tests in 29 suites**.
The downstream sequencer now holds, rather than fails, on a transient persisted
submission intent; it never advances until every prerequisite is completed.
The agreed guiding principle is now image-first staged progression: automatic
intake/likeness to gallery, explicit user stage selection/branching, and
deterministic promoted-output lineage back into Gallery by stage/recipe.

**Oct 25/26 sandbox execution:** the authorized all-input preparation run
`clean-rebase-20261025-overnight` stopped at 1,302/2,741 outcomes with a
`MemoryError` while Pillow encoded a padded PNG into an in-memory buffer.
It has no complete preparation manifest or `intake.json`; matching preview,
backup/install and fresh full-library Gallery publication were not reached.
Its partial `inputs` tree is preserved. There is no active clean-rebase process,
and the launcher refuses in-place continuation when staging exists without a
receipt; use a new run directory after re-inventory. The writer now streams
copies/hashes and PNG saves to disk and computes image differences in chunks;
`bin\validate.cmd` passed 811 tests across 29 suites after that change. This
does not prove full-run completion. The run originally counted 2,700 immutable
inputs plus 41 additional preparation inputs; 74 mapped inputs use newer
Working Various bytes with both raw versions preserved. This does not mean 41
new people. Earlier exploratory `125/86/9` counts were not reconciled and are
not combined with the saved overlay receipt. The rebase plan owns completion
and recovery.

**Oct 25 Python runtime:** the launchers already use regular 64-bit Python
3.14.3 and a working modern CPU image stack. Added direct core/intake dependency
requirements and extended Windows CI from 3.12 to 3.12/3.13/3.14, retaining the
3.12 compatibility baseline. No global interpreter, ComfyUI environment, GPU
stack or image recipe changed. Runtime setup and local-versus-CI evidence live
in the [photo-library guide](art/original-photos.md#python-runtime-and-dependencies).

**Oct 25 prepared clean-start delivery:** the existing sandbox launcher now
offers read-only inventory, intake-only prepare/check, resume into fresh-cache
matching preview, reviewed install and exact undo. All cast images are prepared
with membership retained; loose/named Various use the same planner and Artists
remain preparation-only in their domain. Exact originals/retained alternatives
follow assigned images; gallery detail has checked current/derivative/return
links. Prepared natives no longer undergo legacy screenshot cleanup again.
This bypass applies to the prepared installer, maintained derivatives and
guarded likeness crop, not every direct legacy `originals` caller.
One-to-one stable-ID decisions migrate only with verified continuity; missing,
unknown, ambiguous, stale or concurrently edited inputs hold. Existing owned
cast outputs and previous categories have checked reversible replacement.
This supersedes the integration-gap statements in earlier Oct 25 checkpoints
below. The later overnight sandbox preparation stopped during encoding as
recorded above; matching and installation remain unverified. No production
change ran; visual/threshold acceptance, optional cast release and incremental
production cutover remain gated.

**Oct 25 automatic-protection/name direction:** the user requests confidence-based
photo protection inside protected people and automatic protection of sufficiently
established identities, alongside family naming that preserves original names.
Engine E13 owns pending calibrated gates and manual opt-out semantics; family
N9/N10 owns original/current/character-name provenance and gallery presentation.
Draft `draft-2026-10-25.1` now implements independent leave-one-out protection,
persistent manual opt-out/re-enable, original/current-name provenance and
conservative direct-reference family association. Shared reconciliation applies
combined metadata patches with source checks, backup and exact undo. Galleries
show the three names and protection reasons. Thresholds remain uncalibrated
working defaults; no real matching, catalogue migration or live change has run.

**Oct 25 clean-start and studio-gallery clarification:** these are incremental
extensions to the existing pipeline, not a new rebuild mode. The next rebase
must prepare all supplied originals first, support intake-only review/resume or
full matching/assignment, and retain verified original/variant/name/override
lineage. No rebase is to run before that integration is ready. The prepared clean-start delivery above now implements the sandbox combined
flow; loss-prevention guards alone are still not migration acceptance.
Shared gallery chrome now includes a native mobile Menu and colored/versioned
studio footer. Commit/push is authorized after clean validation and day hygiene.

**Oct 25 gallery continuation:** Review has separate responsive Reference,
Identity details and Manual actions panels. The primary reference stays visible
under filters and alongside its actionable grid copy. Overview Review-count
badges open the person's Review-only filter; category-use guidance is descriptive,
not assignment or rarity policy. Tested with synthetic browser fixtures; actual
People/Artist republishing and full overview-stat parity remain open. No intake,
scores, action permissions, protection or library files changed. The
[layout plan](plans/2026-10-22-gallery-review-layout.md) owns remaining work.

**Oct 25 intake-detail navigation:** Review and Artist Review now share a
single preparation-evidence renderer, with a direct intake-detail entry or
an explicit all-runs comparison. The v9 read-only integration preview shows
all 12 incoming photos with 84 checked trace alternatives; sources and the
v16 manifest are unchanged. Real People/Artist republishing remains acceptance work; verified
post-assignment lineage is now implemented by the continuation above. Documentation classification and
safe CLI/refactoring work may continue during intake review; template/generation
work follows the image-processing milestone, not this GUI checkpoint.

**Oct 25 gallery-first clarification:** the target starts at a main gallery,
with separate Intake/Various and assigned-person browsing and per-image detail
reachable from each. After assignment, detail follows verified image lineage
and shows all actually retained versions, including denoise/lighting alternatives,
not discarded intake candidates or an undifferentiated list of old experiments.
The comparison bridge alone did not provide that continuity. Layout L19/L12 and
intake I21/I23 originally owned that integration; the prepared installer now supplies
verified retained-detail continuity. L19's separate Intake landing/real UAT and
L12's broader acceptance remain open. Manual-action A8 holds the future image-centred ComfyUI
execution idea pending the user's write-up. No workflow execution is authorized.

**Oct 25 run-history browser:** gallery navigation now includes **Intake runs**.
Multiple exact traces open a separate searchable run/photo browser rather than
an expanding chooser. The generator publishes it alongside People and Artist
pages; the real v9 preview covers seven runs/84 traces. History checks runs
individually beyond the continuity index's global budget, without relaxing
current-source evidence or domain rules. Invalid runs stay diagnostic/unlinked.
This is historical comparison browsing, not accepted retained-set publication.
Run pruning remains a separate explicit-policy task; nothing is deleted.

**Oct 25 documentation reconciliation:** all 21 active art documents were read
in full and classified before the new review-first daily recap. Current guides
now distinguish v16 prepared sandbox behavior, historical report recipes,
proposal-only features and the still-paused incremental/production route.
The tooling-debt D13 ledger records each disposition; unfinished acceptance is
not closed by documentation cleanup. No sources, real rebase, identities,
ComfyUI jobs or feedback notes changed.

## Earlier checkpoints (dated evidence, not current command authority)

The current delivery/acceptance boundary is above. Statements such as
"not shipped" below describe their dated checkpoint; the current guides and
owning plans resolve subsequent changes.

**Oct 24 composition clarification:** preparation should reduce excess
background and center the full visible subject, not only remove overlays.
Target sequence and storage: exact accessible original in `gallery_org` ->
safe crop/cleanup/final composition -> accepted native image in `gallery` ->
full/head/chest padded derivatives. Preserve visible limbs and head/hair in
full-body references; padding, not limb-cutting, supplies the standard canvas.
This is agreed direction, not delivered live behavior. Existing `*_org`
archiving must be reconciled before cutover. The
[photo-library runbook](art/original-photos.md#agreed-end-to-end-flow-and-current-cutover-boundary)
owns the target; intake I20 owns composition and I12/upkeep U7 the storage/
provenance cutover. No live files were changed for this clarification.

**Oct 23 current priority:** source-preserving image preparation now precedes
broad action UAT. Agreed work order: evaluate practical local cleanup and
immutable-source recovery, integrate downstream derivatives/viewers, test an
explicit configurable cast-seeded all-library rebase, then engine/incremental
acceptance and separately approved production. Exact algorithms, archive
placement, seed counts/thresholds and error/runtime targets remain undecided.
All images, including retained Angel/Sister seeds, need a preparation outcome;
that does not promise every image can be repaired or authorize ordinary
automation to strip protected cast. Whole-body matching is not implemented.
Current analysis is aligned-face YuNet/SFace. See the
[ordered work and ownership](plans/README.md#current-library-work-order-oct-23).

**Oct 23 sandbox preparation pilot delivered:** `bin\prepare-images.cmd`
now previews, creates sidecar comparisons or verifies an existing run.
Initial all-category output is sandbox `Working\_reports\preparation\intake-pilot-20261023-03\index.html`:
28 retained inputs (four/category including Angels/Sisters), control/denoise/tone
alternatives, larger per-photo pages and 84 separate padded 944x1104 examples.
Exact source bytes are retained before decoding; current bytes may already
be cropped, so raw provenance is not assumed. All active image inventories
and captured catalogue/cache/policy/history hashes remain unchanged; repeating
the run leaves all 310 report files unchanged. Focused tests and quick validation
passed including 19/19 mutation cases. User visual/quality acceptance remains.
No new model, overlay repair, automatic enhancement selection, Gallery
replacement, core reassignment or ComfyUI retargeting ran. Existing people-page
comparison integration is planned, not shipped. Already-good images should take
an explicit no-op path; rejected enhancements preserve the last accepted source
with explicit diagnostic/reason semantics, not a silent successful-cleanup fallback.
Latest user clarification: readable images with overlays or failed enhancements
continue unchanged without manual intervention; display original/enhanced and
the reason. Overlays alone are not preparation holds. New pilot code exposes
`sourceTreatment`; existing `-03` comparisons remain unchanged v2 evidence.
Normal people-page integration and automatic quality selection remain planned.
Older-original recovery can follow later, potentially in the next 400+ batch.
See the [pilot evidence and open gates](plans/2026-10-23-image-intake-preparation.md#pilot-delivery-evidence-oct-23).

**Oct 23 upstream geometry comparison delivered:** recipe v5 runs conservative
solid-border planning before denoise/tone, retaining exact input bytes.
New sandbox report:
`Working\_reports\preparation\incoming-geometry-20261023-v5\index.html`.
Fourteen incoming files: one border-only crop, 13 unchanged geometry, eight
separate legacy screenshot-crop proposals (never recommended or fed to filters),
64 padded views. Recommendations link original or border-only geometry, not an
unmeasured enhancement winner. Overlay reconstruction and semantic hair-safety
validation remain open; overlaid content passes through for ComfyUI, without a
manual hold. All 14 input hashes/mtimes, catalogue/seven scenario files and
5,945 active category file paths/sizes/mtimes remain unchanged; exact repeat
preserves all 222 report files. All local links and padded dimensions verified;
30 focused regressions and quick validation (19/19 mutation cases) pass;
Markdown lint/whitespace checks pass, earlier reports still check. No production,
source replacement, matching, new model or ComfyUI operation ran.

**Oct 23 staged processing/face gate (v6):** new sidecar report
`Working\_reports\preparation\incoming-trace-20261023-v6\index.html` captures
113 current incoming files, with original/cleanup/final summaries and explicit
five-step traces. Four report-only Junk candidates skip all transforms (two
no-face, two below existing 60px threshold); detector failures remain errors,
not Junk. Of 109 processed inputs, 86 have provisional border/panel crops,
95 show rejected eraser/mask previews and 72 rejected right-side crop previews.
Denoise/tone consume selected cleanup, with no automatic enhancement winner;
final retains cleanup. This is review instrumentation, not a reliable hair/
body eraser or live crop-path cutover. All 113 inputs and captured state stay
unchanged; 114 HTML pages/794 padded dimensions verified; exact repeat preserves
all 2,609 report files. 38 focused tests and quick validation (native exit 0,
19/19 mutation cases) pass; Markdown/whitespace checks pass. See the
[current pilot evidence and limits](plans/2026-10-23-image-intake-preparation.md#pilot-delivery-evidence-oct-23).

**Oct 23, 21:21 visual UAT continuation (v8):** actual comparisons confirm the
right-only eraser missed colored corner logos, top search bubbles and lower
captions. New comparison-only run
`_reports/preparation/visual-uat-20261023-v8/index.html` attempts four-edge
strokes and bounded corner/top-bubble masks. 107 of 109 usable inputs now have
eraser trials; all remain rejected for automatic use. Direct image inspection
finds remaining logo fragments, smeared fabric/marble and partially erased
bubbles where the hair guard excludes pixels. This is broader diagnostic
coverage, not successful faithful reconstruction or an accepted new winner.
50 preparation tests pass; preview/apply/check and old v7 check exit 0.
All 113 input hashes/mtimes, catalogue/cache and 6,044 active file metadata
records remain unchanged. New comparison evidence costs 1,991,511,772 bytes /
2,714 files. The user authorized renewed bounded sidecar UAT, not live moves,
quarantine, assignment, source replacement or production. The
[visual findings and next work](plans/2026-10-23-image-intake-preparation.md#v8-result-and-direct-visual-acceptance-boundary)
own the mask benchmark, stronger reconstruction comparison and multi-edge
finishing-crop gaps.

**Late bounded replay (v10):** 12 exact retained inputs were replayed at
`B:\ST-v9\Sovereign Territories Sandbox\Working\_reports\preparation\v10`.
Complete detected neutral bubbles can now be attempted across hair while
refusing detected-face intersections; left/right/bottom mask-directed crop
comparisons replace the fixed right-only trial. Direct visual inspection finds
the motivating hair banner removed but replaced by an unacceptable streaked
hair cap, and corner fills still smear. Experimental repairs/finishing crops remain automatically
rejected; the goal of one genuinely clean final source is not complete.
54 preparation tests and actual preview/apply/check pass; v8/v9 still verify.
Final baseline comparison confirms all 113 live input hashes/sizes/mtimes and
two catalogue/cache records unchanged. v9/v10 together add about 363 MB of
retained comparison evidence. I18/I20 are partial; I19 needs an available
stronger-reconstruction slot without interrupting the busy ComfyUI queue.
The [late recap](recap/2026-10-23-2121-recap.md) records GUI delivery,
visual failures, verification and next steps.

**Same-mask continuation (v11):** the preparation report now compares installed
OpenCV Telea and Navier-Stokes on identical masks/inputs, with explicit
rejected/failure lineage. The actual 12-input v11 replay verifies; direct
inspection finds neither local method restores convincing hair/fabric/marble.
Final full quick validation passes 27 suites / 659 tests plus 19/19 mutations.
Live 113-input/state preservation checks still pass. v11 adds about 206 MB
retained evidence. The ComfyUI queue remains busy (one running / 85 pending);
stronger reconstruction and the genuinely clean final-source goal remain open.

**CPU-only outlined-banner follow-up (v12):** bounded closed outlines now
catch the previously missed translucent top banner in `204050`, merged with
neutral hypotheses before face refusal. Actual repair removes the banner
but stretches the architecture, so remains rejected. 60 focused preparation
tests, replay preview/apply/check, 822 local references and responsive browser
UAT pass; all captured live input/state records remain unchanged. No new GPU
jobs. The [owning plan](plans/2026-10-23-image-intake-preparation.md#cpu-only-continuation-outlined-translucent-banners)
records the delivered safe iteration and remaining acceptance gates.

**23:01 position-aware oval crop (v13):** finishing-crop comparisons can now
use a detected oval's measured lower edge for a guarded top cut, only with
face evidence and clearance above every expanded head margin. Rejected
repairs never feed this crop; no new automatic selection. 62 preparation
tests pass, including end-to-end positive-clearance and overlap/multiple-face
refusal. Saved real examples still overlap the conservative head guard, so
remain unresolved rather than cropping off hair. No extra large report batch,
source changes or GPU jobs were needed.

**Oct 25 v16 intake (AI decisions, to review in I29):** the second crop now
runs before any repaint and is guarded by a Mask R-CNN person mask (at most
0.5% of the person lost). LaMa repaints the remaining clutter on the
second-crop output, and its result is selected. Composition frames the whole
person and keeps the bottom when the mask stops mid-leg. The 12-photo sandbox
run (`v16`, 155 MB) removes every GMW logo, the right icon rails, the search
bubble and an on-body caption. Gaps (I27): picture-in-picture thumbnails,
round avatars, a translucent ad card. The intake code is now the package
`tools\art\intake_library\`; retired v5–v15 geometry is removed and
`legacy.py` only lets old reports verify.

**Oct 24 v14/v15 crop sequence and named folders:** earlier recipes (v6–v13)
never auto-selected a second crop, so recommendations stayed at the original or
the panel geometry. v14 selects a pure overlay crop that:

- removes at least 95% of the mask;
- loses at most 25% of the area;
- keeps a body frame around every face;
- has screenshot evidence, or the mask is one compact corner logo.

Both GMW-logo samples were selected. v15 adds the agreed final framing crop
(the gallery's existing `person_box` rule), so intake runs crop → eraser trial
→ overlay crop → framing → enhancement comparisons. The `123511` reel is now
framed from hair to feet without its icon rail.

`likeness seed` (step 0 of `library.cmd`) restores the
`Various\<Name>\gallery` drop. Before it, the folder scan treated Various as a
single pool and ignored named folders.

Proposed and awaiting decisions:

- retained version sets (`gallery_intake`);
- intake-only stop/resume;
- an all-versions page;
- a directory reckoning for future male/animal subjects (intake plan I21–I26).

Tests: 67 preparation, 58 likeness, 12 library routine. Sandbox only: no source
moves, commits or GPU jobs.

**Oct 23 early Junk/artist scope:** recipe v7 records original artist/general
scope, validated against source paths. Artists share preparation and padding,
not identity assignment pools. Copies in Various can stay for these nonmatching
tests; real intake uses `Artists/<artist>/gallery`. Face confidence filtering is
not species classification: no usable human face stops transforms, while a
human plus an animal is not automatically rejected.
An explicit `prepare-images.cmd --quarantine-junk` mode previews or, with
`--apply`, verifies a scoped backup and moves eligible loose intake to nested
`_junk/<original-path>` with journal and exact `--undo-junk`. Default comparison
apply stays sidecar-only. Registered/catalogued/selected evidence is held for
guarded staged actions; stale paths/bytes and collisions refuse. The actual
113-input v6 batch preview finds four candidates, zero holds; no source moves
ran. Ordinary library runs no longer implicitly `junk --recheck`; the later
active-photo check remains a backstop, explicit legacy retry stays available.
Junk is not routine repair/resubmit; photo retirement is a separately recoverable
state, neither implies deletion. Focused parent tests pass: 47 preparation,
11 library routine and 93 action/retirement/review/metadata tests (including
PersonProtection). Manual `photo-junked` now stages from supported gallery
controls/CLI manifests beside photo retirement, with distinct destinations,
typed history and existing guarded apply/undo. No identity is invented for
Artists/Various; loose ID-less intake uses early automatic eligibility rather
than fabricated manual IDs. New report
`Working\_reports\preparation\incoming-scope-20261023-v7\index.html` retains
113 inputs; all 6,167 source/state records are unchanged, 114 local HTML pages
and 794 padded dimensions verify, exact repeat preserves 2,609 report files,
and v6 still checks. Final quick validation passes all 25 suites (593 tests)
plus 19/19 mutation cases, native exit 0. Markdown lint/whitespace checks pass.
Live crop cutover and species-error acceptance remain open.
See the [early Junk runbook](art/original-photos.md#early-junk-disposition-explicit-sandbox-opt-in)
and intake I14/I15; registered manual Junk delivery is review-actions A9.

**Oct 23 artist likeness boundary:** `bin\likeness-artists.cmd` is a thin
entry into the same implementation, limited to Artists; ordinary likeness
excludes Artists. Intake, models, crop/Junk rules, grouping and derivatives
are shared, not copied. Default state is split into library-local
`_likeness/general` and `_likeness/artists`; artist centering cannot borrow
general/cast evidence, and stale/unstamped saved means are explicitly diagnosed.
Legacy mixed-domain transfers/undo refuse before any moves. Scoped post-move
originals uses `--no-repoint`; selected workflow refresh stays explicit.
Shared library housekeeping still covers both roots, but calls the artist
entry for artist crop/Junk/grouping, face checks and its separate index.
Sandbox read-only previews see 279 Artist versus 2,457 general photos.
Artist check reports 33 unusable images (exit 1), not a successful-cleanup
claim. Captured 6,167 source/state records remain unchanged, no new state
directory was created and existing cache/origin metadata remains unchanged.
Initial 102 focused tests and final quick validation pass: 25 suites,
609 tests plus 19/19 validator mutations, native exit 0. Family-preview's
no-library-mutation contract is preserved with read-only cache handling.
No artist/general source move, production
apply or ComfyUI retargeting ran. See the
[entry-point boundaries](art/likeness.md#general-and-artist-entry-points)
and intake I16; crop cutover and real quality/threshold acceptance stay open.

**Oct 23, 17:05 review handoff:** Artists will not appear in normal people
galleries or have general/cast relationship comparisons. A separate, possibly
simplified Artist GUI is deferred until the people gallery is settled. The CLI
split is delivered; direct people-page builds still need general-domain scoring
and removal of legacy Artist inclusion (intake I17/layout L13), so gallery
isolation is not yet complete. Leave Various/gallery unprocessed until the user
removes Artist test copies and confirms readiness. Existing v7 comparisons
remain reviewable. Isolation and disposable-fixture integration/recovery tests
can proceed without accepting cleanup recipes or touching that incoming batch.
See the [review handoff](plans/2026-10-23-image-intake-preparation.md#oct-23-1705-review-handoff-and-incoming-batch-pause).

**Oct 23, 17:29 follow-up delivered:** the later authorization supersedes
Artist GUI deferral. Separate read-only Artist overview/photo-review pages now
exist at sandbox `Working\_reports\artists`, with search, artist/group/location
filters, lazy thumbnails, 60-card pagination and shared navigation/footer
styling. Four artists, 71 groups, 279 photos; 279 shared 240x300 JPEG thumbnails
use 4,427,932 bytes, complete output 4,670,943 bytes. Actual launcher
preview/apply/check/repeat and narrow/wide browser navigation pass. Artist
sources/metadata/derivatives (853 captured records), cache/catalogue/origin
state stay unchanged. General people pages now build in the general scoring
domain and explicitly refuse old mixed Artist options/spaces. Their shared
navigation/footer code is tested; real people reports were not refreshed while
Various/gallery is being reviewed. Detailed single-photo intake drilldown is
specified in L12, not implemented by this browser.
Routine backups can omit exactly manifest-owned unchanged browser payloads;
ownership manifests, caches, original placement and identity/history metadata
remain included. Unknown/edited/unmanifested outputs stay included; FULL and
transaction snapshots keep generated browser files. Existing People report
tree measures 249,127,759 bytes (199,959,674 thumbnail bytes), not a new
generation or a claim all old files can be omitted. Full quick validation:
26 suites / 631 tests, 19/19 mutation cases, native exit 0.
See the [Artist browser guide](art/likeness.md#separate-artist-browser)
and [generated-report recovery rules](art/original-photos.md#generated-browser-reports-and-backups).

**Oct 23 shared gallery theme:** all gallery pages (People overview/Review,
Artists, family preview, new intake preparation runs) now share one theme in
`gallery_chrome.py` with a banner cropped from the ComfyUI title art and
published once to `_reports/_assets/gallery-banner.jpg` (54 KB, replaceable,
never overwritten). Artist pages were refreshed; real People pages were not
(regeneration re-scores the library); themed copies are in sandbox
`_reports/library-style-preview` for review. See
[layout L16/L17](plans/2026-10-22-gallery-review-layout.md) and the
[theme guide](art/likeness.md#shared-gallery-theme-and-banner).

**Oct 23, 19:36 continuation:** shared badge styles now have one owner, linked
tags have hover/focus affordances, and compact page navigation is sticky only
on wide/tall screens. Narrow-screen count and Large-tile overflow are fixed.
Browser checks pass at 1440/760/375/320px; 113 focused tests pass. Historical
People preview copies retain their old evidence/scripts (including Artist rows);
they are presentation previews, not fresh general-domain reports. Incoming
images, cache and live People reports remain untouched; L7 count-color
thresholds and action decisions remain open.

**Oct 23, 20:18 GUI continuation:** Review now has independent Mixed/Split
Gallery/Review grouping and category-first move destinations (layout L8/L9).
Existing ordering, pagination, stable-ID/hash export and staging safeguards are
preserved. 135 focused tests and 50 synthetic browser assertions pass; Split/
Large views fit at 1440/760/375/320px. Only the historical Review preview was
rerendered from saved evidence, with old Artist entries excluded and an explicit
stale-evidence warning; the overview remains the older preview. No rescan,
intake processing, action apply, live-report rebuild or cache/source change.
Protected unlock/relock behavior and broader identity actions remain undecided.

**Oct 23 full-flow clarification:** source preparation and derivative framing
are separate. Agreed sequence: retain original -> prepare native source ->
fresh likeness evidence/assignment -> publish/normalize Gallery reference ->
944x1104 full/head/chest outputs -> derivative-backed viewers and explicitly
selected ComfyUI input sync. The user uses these derivatives, not native Gallery
files, as workflow inputs. Intake I12/upkeep U7 must retire the current
source-overwriting crop route and account for independent screenshot crops in
originals/maintained derivatives/viewer inspection, without removing head/chest
framing. Cutover, chest workflow support and overlay repair are not delivered
by the sidecar report. See the
[full flow and installed-path inventory](art/original-photos.md#agreed-end-to-end-flow-and-current-cutover-boundary).

**Oct 23 delivery versus acceptance:** standard padded/head/chest maintenance,
derivative-backed viewers, stale-output handling and verified lean/FULL backup
support have tested but uncommitted changes. Parent integration: 198 tests;
FULL follow-up: 105 focused tests; normal-temp quick validation passed including
19/19 mutation cases. Real sandbox maintenance was not applied; the final full
preview did not finish. No whole-library output count/visual acceptance is
claimed. Amelia's existing action undo is not settled and the pending
Draknoxa/Lia Joyce swap is not applied. The earlier planning pass did not process
photos; the later authorized sidecar pilot above does not replace library
sources, alter production/Source, download models or retarget ComfyUI inputs.

**Oct 22 full-plan reconciliation:** all current plans were reviewed.
Eight superseded execution plans were archived with dated reasons, preserved
discussions, explicit task/context destinations and not-completed disclaimers.
Focused successors are active; independent older work is retained with dated
questions. The [audit](audits/2026-10-22-plan-feedback-audit.md) records coverage,
not new runtime acceptance. Implementation/image processing remain paused.
All-category manual identity actions and protected-action unlock remain
unfinished; current protected rename still uses confirmation.
The user's manual prompt direction is captured for source/token/data review:
new `0_Edit`, revised Prime/Bare, retire `1b` after verified replacement and
leave `2b` untouched. No templates, art JSON, prompts or image placements were
changed by this documentation pass.

**Oct 22 18:04 current rename acceptance:** Draknisa's recorded person is now
Amelia Morgan in the sandbox. Fixed-slot cast rename apply/undo now use verified
transaction snapshots; this one contains two files totaling 44,318 bytes.
All 275 images remain byte/path-identical; cast IDs/slot/protection, photo
metadata, shared config and production guards are unchanged. Read-only undo
preview passed. Index and both galleries are refreshed using the saved `.3`
policy/cache (232 people, 2,667 review photos). HTML/index/history checks pass;
user visual acceptance remains. Focused tests: 113 passed; final quick launcher
validation: 495 tests plus 19/19 mutation cases passed. Other operations still
use full backups; retention and broader write-set recovery remain planned.
See the [latest recap](recap/2026-10-22-1640-recap.md).
No matching/rebase/normalization or production operation ran.

**Oct 22 22:30 confirmed name swaps:** the existing Review rename control now
offers an explicit two-person confirmation for a uniquely occupied name.
Both participants are bound in one guarded action, with swap history,
transaction snapshots, checked pair apply/undo/rollback and fixed cast slots.
101 focused tests and full quick validation passed, including 19/19 mutation
cases. Sandbox galleries are refreshed; Draknoxa/Sydney Sky and Prospect
Lia Joyce remain unchanged so the user can stage their name exchange in UAT.
No production apply, global matching or normalization ran.

**Earlier Oct 22 17:50 rename-test checkpoint (superseded above):** the authorized sandbox Draknisa
recorded-name correction is still unapplied. Its first attempt stopped during
full-backup creation on a long destination path, before the rename.
The extended-path fix passes a real Windows regression, 64 focused tests,
local-fixture launcher preview/create/verify and `bin\validate.cmd --quick`.
A verified 276-file retry preflight passed, but the subsequent read-only
full-backup inventory was stopped after slow filesystem metadata traversal.
No worker remains running; reports and production are unchanged. Action-scoped
recovery/retention are planned, not implemented. See the
[latest recap follow-up](recap/2026-10-22-1640-recap.md#follow-up-2026-10-22-1750--0500-rename-test-safely-paused).
The user's Cleanup/Angelica naming fixes are resolved; Lighting remains
a future prompt-stage placeholder.

**Oct 22 current likeness state:** a new true clean sandbox trial is installed
and check-verified; the previous fragmentation run was undone first. Candidate
formation, tier matching, category classification and write authorization are
separate policy decisions. Both clean rebuilding and ordinary incoming/Review
processing now use the shared planner. Runtime defaults no longer live in
`engine.py`; conflicting workspace overrides fail. Draft production apply is
blocked before housekeeping, while preview still shows qualified evidence.
Only sandbox outputs changed; production and the immutable Source remain
untouched. The generated galleries use stable sandbox identity IDs, explicit
holds and the saved clean-run centering context.

The [installed-trial results and limits](art/likeness-sandbox-trial.md#installed-unified-sandbox-trial-oct-22)
are the current evidence, superseding the older run counts below. Fia and
Amara are now Angelica Review candidates, not trusted core additions. The
ordinary post-run preview is not empty and was not applied. Reciprocal
whole-identity merges, red-outlier splits, ID-preserving category transitions
and manual Review reassignment now have tested transaction paths. Apply
performs one read-only affected-core check without cascading moves. The
current `.4` draft's diversity heuristic is not calibrated acceptance.
Registered Models/Prospects now have a separate staged identity-protection
control with stable-ID/state validation, verified-backup apply and undo.
It does not change scores or borrow a photo ID. Synthetic browser export,
cancel/conflict checks and actual sandbox payload checks pass.
Registered identities now also have standalone staged manual rename in the
Review People heading, preserving stable IDs, photo filenames and recorded
history through backup/apply/undo. Angels/Sisters change the recorded person's
name only; their fixed character slot, folder and workflow references remain.
Protection blocks automation, not explicit manual correction, with a staging
confirmation for protected identities. Collisions,
stale inventories and unsupported workflow/workspace references are refused.
Whole-person merge/retire/reject, name swaps and family-link changes remain open.
Family naming, incremental-batch acceptance, global convergence and full CLI
modularization remain unfinished.
A new read-only `family-preview` command now exposes direct reference scores,
surname reuse and collision-aware naming proposals from the saved sandbox
scenario; see the [family/name preview evidence](art/likeness-sandbox-trial.md#naming-and-action-follow-up).
Suggestions do not establish family membership or authorize renames.
Individual photo retirement is now staged separately from rejection: a
verified, undoable original-file archive under `_retired/photos`, excluded
from matching. Protected/anchored/workflow-selected originals are refused.
The regenerated sandbox page exposes eligible Gallery and Review choices;
whole-person retirement remains open. Permanent rejected-identity exclusions
now have a separate staged action, content-bound stable IDs, merged-successor
guards and shared individual/group routing exclusions. Ordinary Reject to
Various remains a nonpersistent pool operation. Stale bytes are held; legacy
moves refuse exclusions they cannot honor, and clean rebuilding refuses
non-cast exclusions until stable-ID migration is supported. Synthetic browser
export/cancel passes; no real rejection was applied.
The overview now keeps an otherwise hidden workflow photo in slot nine with
a dashed score-colored border; sorting recalculates the display pin.
The reported Uma Merritt 0.53 Various hold is traced in the
[installed trial evidence](art/likeness-sandbox-trial.md#installed-unified-sandbox-trial-oct-22):
its initial cast ambiguity and unapplied post-build assignment are distinct.
The separate production clean-full rebuild is still required after acceptance
and approval; there is no production adapter yet. Gallery visual acceptance
also remains open because the integrated browser refused the external B:
location. Review the actual local HTML without treating aggregate counts as
identity correctness.
The latest working-day reflection is the
[Oct 22, 16:40 reconciliation recap](recap/2026-10-22-1640-recap.md);
the overnight recap retains the detailed historical sequence.

Oct 14 photo-library follow-up: the people gallery now shows prospect-to-sister face matches and observable photo-readiness evidence; the standard library routine archives Prospect folders with no gallery or review originals under `_retired`. Pose diversity is not scored; a calibrated readiness ranking remains open in [plans/2026-10-12-tooling-debt.md](plans/2026-10-12-tooling-debt.md).

Oct 14 report update: `_reports` is organized into `library`, `runs`, `comparisons` and `analysis`; the gallery now shows each paired Angel's Sister, canonical hair color and top three eligible Prospect alternatives, with all eligible candidates ranked in `comparisons/pairings/angel-prospect-candidates.md`. Promotion remains a previewable CLI operation, not a browser action.

Oct 15 historical state: the photo-library run was in sync and reports ready for review. Manual drafts under `prompts/_edit/female` remain working references, not generated outputs or approved template changes. The [current migration plan](plans/2026-10-22-manual-prompts-to-art-library.md) supersedes the earlier wait-for-readiness sequence.

Oct 19 working state: the verified pre-run snapshot is `B:\Sovereign Territories\_backup\library-20261019-125822`; the retry snapshot is
`library-20261019-140638` (7,107 files / 3,868,753,524 bytes). Prime frame generation/configuration is removed and 972 library images, 9
input copies, and the corresponding workflows are archived, not deleted. Six updated Angelica shots were pulled before publishing. The
787-photo ingest is complete; 38 new Prospect folders were created, 24 replaced originals were preserved, 3 older same-ID imports remain in
`Various\duplicates`, and 3 problem photos are in `_junk`. The later 916-photo ingest used verified snapshot `library-20261019-171329`
(8,287 files / 4,088,450,098 bytes): 70 exact copies were archived, 39 Prospect folders were created, and 3 incoming multi-face photos went
to `_junk`. The final library check reports an empty pool, 0 active duplicate pairs, 0 ID conflicts, `IN SYNC`, and `NOTHING WAITING`;
`_archive\Various\gallery_duplicates` now has 332 files including earlier history, and `_junk` contains 6 photos total. The reports were
regenerated for 265 people; Camaris's current top candidates are Helena Stratton, Sabine Vale, and Uma Dunn. The Sister-first gallery
cross-links remain active: Angel cards are ordered by pairing fit, while Prospect cards are ordered by descending gallery photo count (name
breaks ties). See the [tooling-debt plan](plans/2026-10-12-tooling-debt.md) for gallery behavior and the [Oct 19 library
plan](plans/2026-10-22-library-upkeep.md) for batch details. The sync-input step still reports missing/placeholder
workspace assets and a selected Female photo now in Fantasy; these were not changed. The chest crop is deferred pending a visual sample
review. This work was subsequently separated into topic commits, pushed to
`art/curation-and-workspaces`, and the branch is clean and in sync with its remote.

Oct 19 library-management decisions: Prospects have 5+ usable photos; Potentials
are a separate active root for 1–4, and remain matchable as later downloads
arrive. Junk remains the repair-and-resubmit path. Retired is for photos judged
unusable, not good unmatched photos. Sisters stay fixed. Current Angel
alternatives are report-only; the four Angel choices were made manually and
slot names remain fixed. Automatic pairing/swapping is deferred until the
future Demon phase and its counterpart rules are agreed. See the
[library-management rebaseline](plans/2026-10-22-library-upkeep.md).

Oct 20 closeout: the explicit choices are Aria Muse → Gavrielle, Ruby Eden →
Camaris, Amethyst Montgomery → Ravaelle, and Sabine Vale → Nyxene; Angel slot
names remain fixed. The verified backup preceded the 135 Prospects-to-Potentials
moves. Identity mismatches and Junk matches remain review-only. People Gallery
and Angel Prime workflows were regenerated, saved Angel Primes shots were
preserved, and the accumulated work was committed in four topic groups and
pushed to `origin/art/curation-and-workspaces` (tip `691169850`).

The plan audit found 11 active plans and one proposed plan; the approved
likeness-workflow, art-tools-structure, and rebaseline/family-naming plans
bring the current count to 14 active plans and one proposed plan. No other
plan was ready to archive. The current recap is
[Oct 20](recap/2026-10-20-0150-recap.md).
The immediate user task is to finish the manual `0_Edit`/`1_Alpha` prompt set;
do not update shared templates or regenerate their outputs until the user's
batch is ready and reviewed.

Oct 20 likeness direction: a new active plan covers a git-tracked identity
metadata catalogue, separate from ComfyUI photo selection; a focused review
gallery that exports validated CLI manifests; explicit Review versus
Reject-to-Various behavior; combined Review/Various matching with same-run
candidate clusters; and guarded Prospect self-healing. Its metadata, stable
ID, gallery, manifest, backup, and undo foundations remain active there.
Angels and Sisters remain protected from automatic gallery moves. The Oct 21
rebaseline plan now owns rebaseline, family naming, matcher simplification,
and validated routing. Implementation proceeds in tested, documented
increments; no production thresholds change before action-specific validation.
Broader art-authoring and ComfyUI execution UIs are future scope.

Oct 21 likeness decision: Option A is approved—keep the existing category
folders and represent families/lookalikes as virtual groups in the people
gallery. Use shared surnames for identities automatically associated by an
approved looks-like threshold, with distinct first names; names are
human-facing only and never matching evidence. Real end-to-end moves and
family-name assignment may be tested on an isolated copy such as
`B:\Sovereign Territories Sandbox\`, inspected in the viewer, and rerun there
as needed. The normal library remains a separate, reviewed and backed-up run.
Before implementation, the new
[rebaseline and family-naming plan](art/likeness-processing-contract.md)
coordinates current-plan prerequisites, source-scope and code-simplification
audits (including Artists and legacy Model folders), name/history review,
visual no-move scenarios, real sandbox iterations, validated routing, and a
guarded rebaseline. No production thresholds, names, folders, or photos
changed with this decision.

Oct 21 likeness POC direction: add a rebaseline flag and validated,
data-driven JSON config so the complete selected library can be reprocessed
into real category directories in an isolated sandbox. Each run starts from
the same immutable snapshot and rebuilds identity references from Angels and
Sisters only by default; an option includes eligible low-own-core-score cast
photos as candidates. Reset only generated sandbox outputs and run-scoped
identity state, then inspect actual Models/Prospects/Potentials directories
and the gallery; config/threshold changes can be rerun without per-photo
approval. The proposed Model tier is 5+ usable photos and cast resemblance in
the calibrated below-merge band (initially 0.40 to below 0.55); other 5+ groups
are Prospects, and one-to-four remain Potentials with visible likeness scores.
Classification is tied to stable identity and directory placement; gallery
toggles affect presentation only. Production roots remain prohibited to the
sandbox reset path, and the normal-library rebaseline remains a separate
reviewed, backed-up operation. Existing production category rules have not
changed.

Oct 21 sandbox prerequisite: the full-name audit covered 265 active identities
in Angels, Sisters, Prospects, Potentials, and Artist-person folders. Four
incomplete `z_` records were completed: Angelica Vale (user-approved),
Potential Camaris Bloom, Mia Wolfe, and Draknora's recorded identity Jade
Santos. A second audit verified all 265 have exactly one full-name record
whose filename matches the name; no person folders or photos were moved.
Vale is now used by seven active identities; surname reuse alone does not
establish a family link. The sandbox now exists at
`B:\Sovereign Territories Sandbox\`. Its `Source` snapshot and `Working` copy
each contain 8,845 files / 5,570,978,132 bytes; `source-manifest.json` records
each file's relative path, size, and SHA-256. All included file hashes match
across the production source, snapshot, and working copy. `_backup`,
`_archive`, and `_reports` were excluded; `_junk` and `_retired` are retained
only as inert reference data, not matching inputs or reset targets. The
remaining gate is to prove processing/reset commands are confined to the
sandbox before running a rebase. A temporary-storage benchmark excluded C:
because it is the OS drive: B: (Samsung T7 USB SSD, exFAT) led durable
sequential writes at 296.3 MiB/s versus A: (ADATA SP900 SATA SSD, NTFS) at
155.4 MiB/s and D: (Toshiba USB drive, NTFS) at 65.8 MiB/s. Creating/writing
512 small files took 0.20 seconds on both A: and B:, and 4.14 seconds on D:.
Benchmark files and the C: scratch copy were removed; B: is the current
choice for sandbox temp outputs and reports.

Oct 21 gallery refinement: both People Gallery pages now share the
Sisters → Angels → Models → Prospects → Potentials hierarchy, concise copy,
line-separated relationships, consistent category/score badges, and Review
links with a separate in-gallery jump. The overview is for relationships and
a nine-photo scan; Review remains the complete photo/action workspace. Score
colors are display cues only. Both pages were regenerated in
`B:\Sovereign Territories Sandbox\Working\_reports\library` from the
sandbox-local cache with ComfyUI renders disabled: 265 overview cards, 2,667
Review photos across 261 identities, and 6,055 cached thumbnails. Their
embedded scripts and category order were validated. Person-wide protection
for Models/Prospects remains a separate planned identity action from existing
photo protection. No rebase or production move is authorized.

Oct 21 gallery scoring refinement: Review now displays the filename-derived
Photo ID separately from the stable person Identity ID, alongside core mode
and size, membership, face size/count, centered-similarity method, and applicable
thresholds. The People Gallery uses colored adjusted-fit badges and
score-direction jump triangles, and links a chosen source photo even when it
falls outside the nine thumbnails. These are presentation and navigation
changes only; fit colors do not alter matching or routing. Both pages were
regenerated in the B: sandbox with its local cache and renders disabled:
265 overview cards, 2,667 Review photos, 6,055 cached thumbnails. Person-wide
protection remains open; no rebase or production move was run.

Oct 21 gallery follow-up: the People Gallery now shows the workflow photo's
likeness badge, links it directly, and highlights it with a thick score-colored
border when visible in the nine-photo grid. Review uses separate category,
location, and state badges; its identity heading omits the category prefix,
face details link to cached face crops, and expanded scoring evidence is
bullet-form with color cues. Review can stage workflow-photo selection for a
Gallery photo in a configured Angel/Sister; applying uses the existing
workflow-repoint helper, verified backup, audit record, stale checks, and
undo. Flow-specific overrides are untouched, and apply/undo refuse an isolated
sandbox root. Only the pages and documentation were refreshed; no production
workflow selection, rebase, or photo move was applied.

Oct 21 rebase diagnostic decision: each sandbox rebase should rerun
library-wide calibration, eligible per-folder consistency checks across
Sisters, Angels, Models, Prospects, and Potentials, and the existing
identity-core audit. Record separate evidence and elapsed times; publish CSV
detail plus a readable Markdown report linked from the run manifest. Both
gallery pages should consume the saved evidence: library-wide quality in the
overview, concise per-person results on both the overview card and Review
heading, and separately labelled per-photo detail in Review. Measure added
runtime before deciding whether any diagnostic needs an opt-out. Diagnostics
do not independently cause moves or establish identity.

Oct 21 diagnostics/reset groundwork: `likeness diagnostics` now writes a
Markdown report plus four CSVs from one library load. A warm-cache pre-rebase
baseline in
`B:\Sovereign Territories Sandbox\Working\_reports\diagnostics\sandbox-baseline-20261021-161618`
covered 2,543 calibration comparisons and 89 of 194 active folders in 15.22
seconds (0.73 load/cache, 14.49 scoring). It does not yet include the
identity-core audit or attach results to a classifier run. The new
`likeness sandbox-reset` preview verified all 8,845 Source files (5.57 GB)
against the manifest and listed only Models, Prospects, and Potentials for
restoration; the reset was not applied. Unit tests cover preview/apply
boundaries and tampered manifests. The old `rebaseline --apply-categories`
path remains unsafe and unused; classifier isolation, per-run identity state,
and diagnostics integration remain open. No sandbox category reset or
classification, production change, or photo move was performed.

Oct 21 People Gallery follow-up: `Person:` now uses each recorded person name
for all Angels and Sisters, not only identities with Prospect-promotion
history. The renderer is shared, so the label applies to every matching card
in both generated libraries.

Oct 21 likeness engine decision: the approved action boundary applies to one
shared engine for both clean rebase and ordinary incremental intake. Unprotected
Potentials/Prospects can merge and split organically under lower configurable
thresholds; Models use an intermediate policy with more Review; Angels/Sisters
remain conservative. Category order, thresholds, action permissions, and
supported category definitions are declarative so future categories such as
Demons can use the same engine. Sandbox and production share the engine and
default policy; any sandbox override is explicit and recorded.

Identity Protection blocks automatic moves into or out of the identity.
Photo Protection blocks automatic removal and Review routing, while the
protected photo can still be excluded from identity-core construction and
remain available for workflow use. Explicit identity protection is now shown
in both gallery surfaces; photo-level protection remains separately tagged.

Oct 21 draft likeness policy: the versioned policy and schema now define the
shared score bands, categories, routing/action thresholds, lookalike cue, and
protection semantics. The draft preserves green >=0.55, yellow >=0.30, orange
>=0.15, red <0.15; >=0.30 is a visual lookalike cue only, while same-identity
clustering uses a separate draft >=0.55 threshold. Draft status blocks
automatic routing/merge/split and keeps rebaseline apply gated pending user
review. The verified current Working backup is
`B:\Sovereign Territories Sandbox\Working\_backup\library-20261021-172221`
(17,582 files / 5,827,811,555 bytes). Policy tests, focused reconciliation
and gallery tests, the schema check, and `bin\validate.cmd --quick` pass.
Both Models-aware sandbox gallery pages have now been regenerated and checked.
The old
`rebaseline --apply-categories` path now requires an approved policy and a
verified Working backup, but this is not a full clean-rebuild engine.

After reviewing the draft values in the gallery, the agreed validation is to preview
the ordinary likeness process immediately, then add the separate 200+ photo
batch and test incremental growth without another full rebase. No thresholds
or production policy values have been selected.
The separately saved logo-detection/cleanup idea remains outside this
likeness-engine scope; no cleanup implementation or crop change was made.

Oct 21 sandbox category-only rebaseline: the immutable source snapshot and
Working backup were reverified before reset. A clean reset restored Models,
Prospects, and Potentials; the explicit draft override then applied only
category-folder moves in sandbox Working: 13 Prospects to Models and
Potentials/Lia Joyce to Prospects. The report covers 2,667 photos across 261
folders; it still lists five photo-routing and three Junk candidates, and 208
lookalike pairs, as suggestions only. No photo routing, Review/Junk move,
identity merge/split, or production operation was applied. The post-move
calibration/folder diagnostics took 15.73 seconds (2,543 calibration photos,
89/194 eligible folder checks, 2,265 per-photo folder scores); the identity
core audit covered 261 folders and is saved alongside the diagnostic bundle.
The overview shows 265 people (10 Sisters, 11 Angels, 13 Models, 23 Prospects,
137 Potentials, 71 Artists); Review has 2,667 photos across 261 folders and
8,722 cached thumbnails. Both pages were generated from the sandbox-local
cache with renders disabled. See
`B:\Sovereign Territories Sandbox\Working\_reports\library\rebaseline.md` and
`B:\Sovereign Territories Sandbox\Working\_reports\diagnostics\diagnostics-20261021T233723319309Z\diagnostics.md`.
This is an isolated category-classification baseline, not the complete
photo-routing rebase. The read-only reconciliation preview found seven
existing Review candidates and held all seven under the draft policy; no pool
photos were present. A one-photo smoke preview used a temporary copy of an
existing Potential photo: against 261 frozen cores it ranked
`Potentials/Amara Madison` first at 0.9483, but held it for visual review
because policy status is still draft. The probe copy was removed; its report
remains under `Working\_reports\reconciliation`. These previews changed no
photo destinations or production files.

Oct 21 modularization follow-up: cached face embedding, embedding-cache
handling, photo records, centered identity-space scoring, category/home rules,
library reads, and average-linkage clustering now live in
`tools/art/likeness_library/engine.py`; ComfyUI render indexing and
photo/render identity-core composition live in `rendering.py` and
`identity.py`. The existing `likeness.py` CLI remains the stable entry point
and re-exports the public names used by gallery, originals, and test callers.
Focused tests are included in `bin\validate.cmd`. These are bounded
extractions, not a completed split: command orchestration remains in the large
CLI module. The
[art-tools structure plan](plans/2026-10-20-art-tools-structure.md) tracks the
next extraction slices and the package-name decision.

Oct 21 sandbox score investigation: the saved leave-one-out diagnostics
contain 2,265 per-photo folder scores. These are retrospective comparisons
against identities present in the post-category sandbox, not assignment-time
evidence from the earlier pool-clustering run. In `Prospects/Sophie Lloyd`, 8
of 39 photos now score higher against another existing identity than against
Sophie's leave-one-out core; four meet the current 0.40 assignment plus 0.10
margin test. The alternatives include `Potentials/Belle Channing` and
`Prospects/Opal Vale`, identities that were not references in a clean
Prospect/Potential rebuild. They are not evidence that the original run
assigned those photos incorrectly. A 0.29 own-core score versus 0.35 to Lucia
Reyes likewise describes the current state only. Draft policy has not applied
photo routing.

In the post-category snapshot, `Potentials/Fia Hadley` has four usable photos,
and its current best cast score is 0.461 against
`Angels/angelica`; all four photos' cast-audit best match is Angelica
(0.315–0.464). This says how the current folder scores; it does not explain
how the earlier run formed the folder. `Amara Berkley` likewise has four
photos and a best current cast score of 0.456. The detailed post-state evidence
is in `Working\_reports\library\prospect-cast-audit.csv` and
`Working\_reports\diagnostics\diagnostics-20261021T233723319309Z\`.

The review page now calculates and displays the closest eligible other
identity for every usable Gallery and Review photo, using each photo's
centered vector against the policy core centroids; it is separate from the
current-folder core score and does not imply a route. `Identity ID: not
catalogued` is expected while `data/art/likeness-library.json` has empty
people/photos/actions maps. “Provisional” means the core is calculated from
that folder's usable photos without a trusted catalogue anchor; it is not
identity verification. These are the next evidence views to inspect before
changing thresholds or applying any photo moves.

The sandbox Review Gallery was regenerated from its local cache: all 2,552
scored records have a closest-other match and none are missing one. Fia's four
photos now visibly show Angelica at 0.32–0.46; Sophie's
`sophie_lloyd_image_7517978830184149119.jpg` shows own-core 0.29 versus
`Prospects/Lucia Reyes` at 0.35, labeled Review suggested while remaining in
Gallery. No photo files or category folders were moved.

Correction: the immutable Oct 21 `Source` snapshot already contains
`Potentials/Fia Hadley`; the sandbox operation described above was
category-only and did not create that cluster or route its photos. It is not
the pre-cluster state from the earlier run. To test the user's hypothesis
without using Fia as a reference identity, the four source photos were
counterfactually treated as incoming Pool candidates against Angel/Sister
cores only. Their within-group pairwise scores are 0.602–0.795; the four-photo
cluster centroid scores 0.461 to `Angels/angelica`, with the next Angel/Sister
core (`Sisters/Draknara`) at 0.159. Thus the hypothesis is consistent with
the numbers: a 0.55 cast-match gate would miss this group, and the old
1–4-photo fallback could classify it as a Potential. The available artifacts
do not record the exact earlier assignment-time candidate set or thresholds,
so this is a counterfactual, not proof of the historical route.

The shared reconciliation was then run as a read-only counterfactual with
Fia absent from identity cores and all four photos treated as Pool input. The
draft 0.40 small-group cast-review experiment held all four for
`Angels/angelica/review`; no assignment or file move was applied. The same
test on source groups yielded a 7-photo Jacinta cluster as a Model at 0.484
to Angelica, a 5-photo Jacinta cluster as a Prospect at 0.392, and Freya's
6-photo cluster as a Model at 0.535. Sophie split into 14-, 16-, and 8-photo
Prospect clusters with best cast scores 0.157–0.236, plus one held single.
These reruns exclude the current Prospect/Potential cores; cluster names are
synthetic and outputs are suggestions, not applied assignments. They show
that Jacinta/Freya's groups can qualify as distinct Models while Fia's
four-photo cluster is held for Angelica review. The original run's exact
reason still requires its original run manifest/log, which is not present in
the current sandbox evidence.

Oct 21 hierarchy-rule experiment: the previous classifier applied the 1–4
usable-photo Potential rule before the 5+ Model rule. Draft policy
`2026-10-21.2` now tests a separate `smallGroupCastReviewMinimum` of 0.40,
matching the existing lower edge of the Model band. A 1–4-photo group at or
above 0.40 becomes a Review hold candidate before Potential classification;
the best cast folder is recorded as a proposed `<identity>/review`
destination. Five-or-more-photo groups at 0.40–<0.55 can still classify as
Models, and groups below 0.40 keep the current Potential rule (with the
existing >=0.30 visual-review flag). This is deliberately a draft experiment,
not a claim that score proves same-person identity. A second cast match within
the configured 0.10 margin makes the candidate ambiguous instead of selecting
one Review destination. The read-only post-state preview identifies 19 small
groups with one proposed cast Review destination and 5 ambiguous groups; it
does not change folders or files. The shared evaluator also changed
reconciliation so blocked Angel/Sister candidates remain available to form a
candidate cluster instead of being prematurely held one photo at a time.
The Fia/Jacinta/Freya/Sophie counterfactuals above exercise the incoming-pool
path; all proposed placements remain unapplied.

Oct 21 correction completed: a **true clean sandbox rebuild** is now installed
and hash-checked in Working. Run
`_sandbox-state\clean-rebase-20261021-2210` started an empty embedding cache,
used only 21 Angel/Sister identity cores, and flattened all 1,155 source
Model/Prospect/Potential photos before matching. Old memberships were not
references, including for held photos; old names were retained only after
grouping. An initial preview was corrected and replanned from its own fresh
measurements, not an older identity cache. The saved `run.json`, `photos.csv`,
and `report.md` record the exact inputs, settings, destinations, hashes,
initial per-photo cast matches, and decision reasons. Previous category
trees remain under the run's `previous` directory; undo is available.

Actual output: 35 candidates entered Angel Review, 17 entered Sister Review,
317 entered Prospects, and 786 entered Potentials. There are 27 Prospect and
698 Potential folders, with no Models under these exact draft values.
This 0.55 clustering baseline is heavily fragmented and is
**not accepted production behavior**; structural planning/integration defects
also contribute, so lowering one threshold is not a complete fix.
Of the 1,155 photos, 591 are in Gallery
and 564 are in Review. Fia Hadley's four photos are all physically in
Angelica Review, excluded from her core; their cluster's cast score was
0.4294 in this global clean-run scoring space. Three of Amara Berkley's four
photos also entered Angelica Review; one remained a separate Potential.
Sophie's 39 source photos no longer remain one identity: 9 are in the
retained-name Sophie Prospect, 2 joined Neve Granger, 4 formed another
Potential, and the remaining photos were held or separated individually.
These are actual global-run outcomes, not the earlier isolated counterfactuals.

Both sandbox galleries were regenerated: 817 displayed identities and 2,667
photos. All 1,947 photos with an own-core score have a closest-other match;
Review-only identities can have no own core. The ordinary reconciliation
preview immediately afterward examined 564 Review candidates and proposed
zero assignments under the draft policy; nothing further was applied. This
is not proof of incremental convergence, because draft status blocks automatic
routing. Post-rebase calibration/folder diagnostics took 13.03 seconds
(1,894 calibrated photos, 86/243 eligible folders evaluated, 1,700 per-photo
folder scores); the full identity-core audit is saved beside them. Review
scores use their current library/core context and must not be substituted
for the recorded assignment-time scores. Production and immutable Source
were not changed.

Oct 21 scope reconciliation: the
[Oct 21 plan's unified contract](art/likeness-processing-contract.md#unified-processing-contract-oct-21-reconciliation)
now owns engine behavior across clean rebuilding and incremental intake.
Grouping, photo/group matching, classification, core evidence and action
authorization are separate decisions; cast protection is not a clustering
floor. The Oct 20 plan retains metadata, staged actions, UI and recovery
foundations, with integration/configuration work transferred rather than
duplicated. A clean-full production rebuild is a required, separately approved
deliverable after sandbox clean and incremental acceptance. The documented
repair order addresses configuration ownership, lost pair evidence, suppressed
proposals, artificial Review-only identities and legacy routine wiring before
another installed threshold trial. Values remain calibration candidates, not
production approval. This reconciliation changed documentation only; it did
not fix the engine, alter policy JSON or move any photos.

The catalogue foundation now has strict schema/reference validation plus
atomic read/write helpers. A read-only `likeness audit-core` command reports
trusted/provisional cores, score order and Prospect outlier candidates; it
does not move images and may update only the existing embedding cache. The
catalogue remains empty, so current matching behavior is unchanged.
The audit tests now cover stale crop hashes, duplicate source IDs, moved
catalogue folders, protected-only photos, small cores, and conflicting folder
or anchor ownership. Stable source IDs are verified through move/name-prefix
changes, scaled suffixes, crop-with-new-content, duplicate rejection and a
verified backup-copy/restore. Identity continuity is closed for these
originals-managed operations; transformations that discard source IDs remain
unsupported until explicitly mapped. No production thresholds or library
photos have changed.
The separate `people_gallery_review.html` view is available through
`bin\people-gallery-review.cmd`; it is local and read-only, includes Gallery
and Review photos, and provides score sorting, filters and content-cached
lazy thumbnails. It can stage identity-anchor, protection, Review,
Reject-to-Various and Review-approval actions to a versioned JSON download.
The view now defaults to person-grouped inspection, sorting each person's
photos from highest to lowest similarity. Review-only, low-score, per-person
and flat all-photo views are available; the low-score cutoff is adjustable.
Each group retains a visible comparison photo when filters hide it, while
workflow-selected photos, confirmed identity anchors and provisional
score-ranked references have distinct labels. The report remains read-only.
The review page has category-driven person selection, responsive
small/medium/large tiles, selectable head or chest-up crops named from each
master image stem and content key, and closest-other-folder evidence for
Potentials. The overview and full review now share identity sort modes:
Core identity first (anchors, then core members, then other scored photos)
and Highest identity score. The overview's first nine match the filtered
Gallery view in the review page; both use the same cached head/chest crops,
and its framing and sorting controls do not require a second thumbnail set.
Person links open the matching Gallery view in a new tab. Both pages use the
same category/person order, and `bin\people-gallery.cmd` refreshes them
together. Prime-start suitability remains separate from identity ranking.
Staged person renaming and explicit name swaps remain in progress.
The paired report was regenerated in place at
`B:\Sovereign Territories\_reports\likeness-review-20261020-final-grid`:
265 overview cards, all 2,667 full-review photos, and 5,334 cached head/chest
thumbnails. The overview links all 265 names to the correct person-filtered
review URL; all 853 displayed photos use the exact same head/chest cache
paths as the review data. Its HTML is 0.9 MB, with no missing referenced
crops. All 261 overview cards with photos were verified against their
person-filtered Gallery review order; four empty cards correctly have no
thumbnails. Both embedded scripts pass `node --check`. The older dated report
remains intact.
The read-only `likeness folder "Harlow Chase" --all` audit reports 100 usable
photos (97 agreeing, two borderline, one below 0.15). Its two-face photo
scored 0.00; one other image scores 0.39 against Harlow and 0.46 against
Camaris. Camaris's identity history records prior Prospect merges at 0.55,
0.49 and 0.49. These are good manual-review targets, not conclusive evidence
of incorrect identities; the identity catalogue has no confirmed anchors yet.
No thresholds or real-library photos were changed.

Oct 20 prospect-sprawl priority: the first read-only, per-photo Prospect/
Potential cast audit is complete; keep new ingest paused until its evidence
and uncertain-cast routing are reviewed. The report is
`B:\Sovereign Territories\_reports\library\rebaseline-20261020-cast-audit.md`;
its companion `prospect-cast-audit.csv` has 1,146 usable gallery photos.
`Angels/angelica` ranks first for 67 photos (12 scores at least 0.40, four at
least 0.45, two at least 0.50, none at least 0.55). It ranks first for all
four photos in Potentials/Fia Hadley and Potentials/Amara Berkley, three of
five in Prospects/Petra Wilde, and ten of fourteen in Prospects/Jacinta Alden. These
are provisional folder-centroid comparisons, not identity confirmation; a
photo's current peer-folder score is often higher. The whole-library preview
also flags Potentials/Lia Joyce (35 usable photos) for the five-photo category
boundary and Potentials/Wren Thorn (one usable photo) for former-cast history.
No photo or category changes were applied; thresholds are unchanged.
The report also contains 26 threshold-based reassignment suggestions and
three Junk candidates, all unapplied. The next work is visual review and
designing source-grouped staged Review routing; cross-Prospect/Potential
reassignment remains a later pass. The existing `likeness reconcile` input is
Review plus Various and still does not audit ordinary Prospect/Potential
Gallery photos.
The Oct 20 library report for review is
`B:\Sovereign Territories\_reports\likeness-review-20261020-1339\people_gallery_review.html`:
2,668 photos, 2,668 cached thumbnails; initial build 88.3 s and cached
regeneration 7.6 s. The grouped refresh is
`B:\Sovereign Territories\_reports\likeness-review-20261020-grouped\people_gallery_review.html`:
2,668 photos and thumbnails across 261 folders; 146 folders have a usable
primary reference and 21 images are selected by a workflow. The identity
catalogue remains empty, so no stored identity anchors are expected yet.
A real-library staged Review preview passed and confirmed
the source hash was unchanged; it was not applied. That run also caught and
fixed the SHA-1/SHA-256 manifest mismatch in the gallery export.
`bin\likeness-actions.cmd validate|preview` checks manifest schema, photo IDs,
content hashes, current folders, catalogue ownership and action conflicts.
`apply FILE.json --apply` now creates and verifies a backup of active library
files, configured inputs, workspace configuration and the catalogue before
revalidating and applying staged moves or metadata decisions. Every operation
is recorded with before/after metadata snapshots, and `undo [BATCH_ID]`
previews a reversal by default; explicit `--apply` backs up and reverses only
the newest unchanged batch. Tests cover file and metadata-only actions,
rollback on catalogue-save failure, stale state, selected workflow photos,
protected anchors, path containment and backup inclusion. No action was
applied to the real photo library; the tracked likeness catalogue remains
empty, and matching thresholds are unchanged. Folders outside the catalogue's
supported roots are view-only.
Oct 20 reconciliation increment: `likeness reconcile [--out FILE.json]`
provides a read-only combined preview of usable Review and Various candidates
against frozen trusted/provisional identity cores. It clusters both sources
together, supports Review-only runs, and can resolve remaining candidates
against fixed provisional clusters. Protected and duplicate-ID photos, plus
ambiguous or unresolved matches, remain held. The report does not include
Prospect outliers yet; those wait for Phase F1's report-only evidence. Focused
planner/CLI tests pass. No real-library reconciliation or photo move was run.
Phases E2-E4 are complete; E1 and E5 remain open.
The later Phase I covers Prospect/Potential name recovery and renaming.
Initial code trace: promotion keeps a recorded `z_` name when one
exists, but falls back to the fixed Angel slot name if it is missing; the
rename CLI is limited to Prospect/Potential folders and has no explicit
two-person name-swap flow. `people_index.csv` and `.md` are written by the
explicit `likeness index` command, not refreshed by rename or promotion. No
promotion regression test was found in the relevant art test modules. These
are investigation leads, not a confirmed cause for the reported name loss;
Phase I will reproduce and test before making behavior changes.
The user also reports that some original Angel/Sister `z_` files were created
empty, without a `name:` header; Draknora is one example. The current reader
falls back to the `z_` filename slug, but `likeness names` treats any readable
`z_` file as already present. Phase I will verify whether those legacy files
retain enough identity evidence and ensure promotion/return does not replace
that name with the fixed cast-slot name.

Oct 20 tooling structure: the new likeness metadata module and tests are in
`tools/art/likeness_library/`, wired into `bin\validate.cmd`. The initial
inventory found 32 top-level art Python modules, 29 internal imports and 19
launchers. The independent codex roster audit and its tests are now grouped
under `tools/art/audits/`; both focused test suites are wired into the standard
validation launcher and pre-commit. The connected likeness/library/gallery
cluster will be reorganized one tested subsystem at a time rather than moved wholesale.
Retirement is explicitly granular: retiring one unusable photo archives it
under `_retired/photos/`; retiring a person uses the existing operation to
return all photos to `Various`; `archive-list` remains a distinct whole-folder
archive. Markdownlint's maximum line length is now 1,000 characters.

## Decisions made

- **A card is defined once, in the codex** (`data/cards/**`, `codex-schema.json`). Art is built for it and linked by
  `cardId`. Gameplay and art data never define the same attribute; see `data/art/README.md`.
- **First series is Sovereign Dawn.** `cardId` (machine, stable) is separate from `collectionNumber` (`SD-###`, human).
  Products reference card ids or pools; they never copy card definitions.
- **10 elements plus Neutral, released in stages (revised Oct 9, 2026).** The MVP is **Darkness and Light only**, a small
  playable beta to test the whole flow with friends. The next cycle is **Fire, Grass, Water and Earth** (Grass joins the
  Fire/Water/Earth primal group), added as part of the real release; Ice, Lightning, Wind and Poison follow in story order.
  Elements are cosmetic identity in the MVP; the only matchup is the Light and Darkness duality.
- **8 rarity tiers** (Basic 0, Common 1, Uncommon 2, Rare 4, Epic 8, Legendary 16, Mythic 32, Transcendent 64 points).
- **Starter decks stay low-rarity (Oct 2026).** Starter heroes are Rare-Legendary "lower-level" heroes under the
  40-point budget. Bound heroes and dragons (Mythic) and sisters (Transcendent) are earned from packs, campaign
  rewards, or story beats; sisters are apex showcase cards. The budget does not change.
- Player-facing title is **Sovereign**, not "Player".
- **Angel pairing uses a shared two-stage Prospect score (Oct 19, 2026).** Candidates need at least five
  usable photos and 0.45 cohesion; the ranking combines likeness fit with a bounded photo-variety bonus
  (+0.02 at 10 photos, +0.04 at 15, +0.06 at 20+). The preferred likeness band remains 0.15–0.40.
  The pairing command, rebaseline preview, People Gallery, and full candidate report use the same score
  and saved-render evidence. Photo count is a proxy for available material, not pose variety. The score
  is generic for future faction pairings; Demon counterpart direction and bands remain undecided.
- **Art and video are data-driven (Oct 2026).** Pieces, cards and animation cards generate prompts; prompts generate workflows. Prompts
  are never hand-edited. Work is **studio** (light-grey backdrop since Oct 26: poses, heads, hair, armor) or **scene** (realm, background, effects; video
  counts as scene); everything goes to the one workspace per group (see the pipeline phases below).
- **Workspaces are tied to sets of cards (Oct 2026).** Each set has a *home* workspace (`homes` in `workflows/workspaces.json`): `Drakn Sisters`
  (the whole sister pipeline; final art is made there), `Sovereign Dawn Series` (the Sovereign Dawn card set), `Sovereign Territories` (the art and brand set and the `ST?_` templates),
  `Angel Primes`, and the planned `Drakn Bound` and `Elder Dragons`. A deploy goes to the set's home and nowhere else; a set with no home stops the command (a missing home once
  silently filled the brand workspace with 174 card workflows, and the workspaces cloned from it carried the leftovers). A workspace may also take a set on request, for a while, if it lists it under `accepts`:
  `Sovereign Territories` accepts any set (promotional videos for reels and feeds, a scene kept next to the art), `Sovereign Dawn Series` accepts the Drakn sets; you ask with `deploy -w` and remove the copy
  with `cleanup -w` when you are done, and a workspace that neither homes nor accepts a set is refused. Only `active` workspaces with an install are written to. `Drakness` stays as a deliberate second copy of one
  sister for working through issues with `zz_` items, and any sister can get a temporary one. Hand-made `zz_Shots`, `zz_Curated` and `zz_Test` workflows are mastered in the workspace and never replaced, moved or
  removed by deploy, cleanup or tidy. `cleanup -w` removes what a workspace is not home for (only when the home workspace has an identical copy; to backup; empty folders pruned). Details and rules:
  [../workflows/README.md](../workflows/README.md#workspaces-one-home-per-set).
- **A hand-made workflow is never overwritten.** Anything tuned by hand is forked or pulled into `workflows/_curated/`; patterns that
  recur graduate into pieces, motions, transitions or templates.
- Prompt injection into ComfyUI workflows is automated; delivering rendered images back to cards is still manual (C1).
- **Variants are art editions of one card (Oct 2026).** `SD-001` stays the only definition; `art.variants` on the card lists editions
  (`shiny`, `holo`; tiers in `data/art/_schema/finishes.json`), each pointing at an art card that carries the same `finish`. A variant
  never changes gameplay; its code is `<collectionNumber>-<SUFFIX>` (`SD-001-HOLO`), derived, never stored. Shiny = recolour and sheen
  for every card hero; Holo = a re-authored edition with a title, ascended pose, upgraded items and a video. The foil/holo shader belongs
  to the client, not the baked art. Every card hero has a Holo (the ascended weapon descriptions are a start for equipment art).
- **One workspace per group, hero first, by pipeline phase (Oct 2026, replaces the per-sister workspaces).** `Drakn Sisters` holds every sister laid out
  `<Hero>/<phase>/...`: `1_Alpha`, `2_Studies`, `3_Layers`, `4_Wardrobe`, `5_Scenes`, `6_Finish` (`polish`, `final` skeletons per sister; upscale is not built yet),
  `7_Video`, and `Bench/motion` (a test run on any phase's image, not a phase). The other permanent workspaces are Angel Primes, Drakn Bound, Elder Dragons, Sovereign Dawn Series and
  Sovereign Territories (brand). A single-sister workspace is spun up only while needed and discarded; only `Drakness` is kept (and kept in sync) until her
  hand-made armor, clothing and scenes are covered by the generated set. The chosen image of each later phase is named `_00000` too (`<Hero>_Qwen_Scene_00000.png`
  feeds Polish, `_Polish_00000.png` feeds Final), so a skipped phase shows as a missing image. The card folders (`data/art/_sets/`), the prompts and the output all use these same phase folders (one layout everywhere). `comfy_workflows.py cleanup -w` previews (and with `--apply` moves to backup) the workflows a workspace is not meant to hold. Every sister has
  a studio kit; first proven with Draknara: a studio kit (`data/art/_kits/<slug>.json`, built by `tools/generators/scaffold_sister_studio.py`) lists the A-pose
  bases, outfits, armor, motions and showcase shots that suit her class and element.
- **Three kinds of hand-made workflow (Oct 2026).** `zz_Curated` = older hand-written workflows and new ones written from scratch; `zz_Shots` =
  workflows tuned for a render (seed, Turbo or not), kept in the repo under `workflows/_shots/<set>/<Hero>/` with their subfolders;
  `zz_Test` = temporary. Generated workflows are never edited by hand.
- **A-pose bleed tests and real-world showcases (Oct 2026, in progress).** Celestial armor showcases let the A-pose swimsuit bleed through. Options
  under test: a `strip` instruction (`wardrobe/effects/strip/remove-original`, `replace-original`; the celestial strip-test cards were retired, the pieces and the optional `?{{STRIP}}` template line stay for other edits),
  a neutral base-layer A-pose (`<slug>-x-pose-base-layer`) and the user's own nude A-pose workflow (a shot). Also 13 real-world photo showcases per sister
  (`showcase/photo/glamour|romantic|daily`: catwalk, grand staircase, bed, beach, city street, bathroom selfie ...) to see how realistic she stays;
  template `showcase-photo-human.txt`, locations in `backgrounds/modern/`. Whether Turbo is worth it for the A-pose is a render question, recorded as shots.
- **Footwear in the A-pose (Oct 2026, decided).** The A-pose is barefoot by default, which keeps shoes out of every later outfit. One switch,
  `data/art/_settings/studio.json` `aPoseFootwear` (`barefoot` today, `signature` to bring back each sister's heels after a regenerate),
  plus `<slug>-x-pose-heels` cards for glamour work. Showcases are filed in families (`celestial`, `elemental`, `studio`, `editorial`, `photo/<mood>`).
- **Output folders follow card families (Oct 2026).** Cards, prompts and ComfyUI output folders are grouped by family below the stage
  (`scene/signature`, `scene/glamour`, `poses/lingerie`, `clothing/gowns` ...) and the output folder starts with the set and hero
  (`drakn-sisters/Draknara/scenes/signature/...`), mirroring `prompts/`; the rule lives in `tools/generators/art_layout.py` and is
  validated. A variant such as shiny or holo sits beside its main card, and one-card groups stay flat. See `data/art/README.md`.
- **Folders outside the repo (Oct 2026).** Originals live in `B:\Sovereign Territories\Sisters` (and Angels, Prospects, Artists, Various), hand-picked keepers in `...\Masters`;
  everything under `B:\Comfy-Desktop` is a transient copy. Each ComfyUI workspace has its own inputs (`ComfyUI-Inputs\<Workspace>`) and
  writes to a project output folder (`Sovereign Territories`, `Angel Primes` as a test bed, `Sovereign Dawn Series` for production), set
  in `workflows/workspaces.json`. The brand and marketing set (title, logos, icons, key art) will be the `sovereign-territories` set.
- **Brand, card art and video pieces (Oct 2026).** The brand set (key art, plates, title, logo, icons, two videos) lives in
  `data/art/brand/` and `_sets/sovereign-territories/`. Non-hero gameplay cards (units, pets, buildings, tactics, equipment, workers; 174)
  get mechanical card-art prompts from their own name, element and lore (`data/art/cards/sovereign-dawn.json`,
  `tools/generators/scaffold_card_art.py`, stage `card`); they are first drafts, not hand-directed art. Reusable video effect pieces
  (ambient, element, theme) in `data/animation/motions/` feed ten theme scene videos. Nothing from these has been rendered yet.
- **Showcase stage:** a studio-class shot on a coloured or magical backdrop (`backgrounds/studio/*`) with an effects line, between a grey
  studio render and a full scene.
- **Celestial armor and the Celestial finish (design, Oct 2026).** Every sister has her own signature celestial armor
  (`heroes/drakn-sisters/<slug>/armor/celestial-armor.json`): small ornate filigree plates in her metal and class/element motif, each a
  different shape (crescents, flames, leaves, snowflakes, shells, sunbursts ...), covering the area of a small bikini cup and a small
  front hip piece, held by magic alone with no straps or wire. The `celestial` finish (`SD-001-CELESTIAL`, rank 3 in
  `finishes.json`) is the earned top edition: unlocked by a sister's celestial quest chain rather than drawn from a pack, with some
  held back in packs for a small chance (rules are open decision O3). The codex shows a silhouette or masked teaser until it is owned.
- **Body contour on by default (Oct 2026).** `bodyContour` in `data/art/_settings/studio.json` adds a fit-to-the-incoming-body line (`fitted-contour`; `armor-contour` for the armor stage)
  to every outfit, armor, showcase and scene prompt for the female sisters; a card sets `components.body_contour` to another piece (`sheer-contour`) or `"off"` to change or skip it.
- **Key learning: the incoming image decides what bleeds through (Oct 2026).** Outfits fed a bikini A-pose kept the bikini (low-cut dresses were not low cut; celestial armor kept the
  straps). The chain is therefore: original photo, then the standard X Pose (a clean metallic-bikini, barefoot A-pose that also sets the bust and pose), then an edit-only `bare` stage
  (removal plus a small covering or none), then the other poses fed the bare image with the body contour on, then
  outfit, armor, showcase and scene, each fed the incoming image that gives the wanted result; documented in `docs/art/tutorial-art.md`. Complete scenes describe the outfit,
  staged scenes take a dressed image, and a semi-staged scene is a complete scene fed an A-pose that already wears a layer. FireRed versions of the bare study and celestial
  steps exist for overnight non-Turbo comparison; the best bare A-poses become the input for everything else.
- **Standard size and denoise defaults (Oct 2026, provisional).** Originals are padded to 944x1104 (`standardSize`), a Kontext bucket, so the Qwen chain keeps one size;
  FireRed's 1 MP resize lands on the same size. Generated workflows start at the high end of the range in their stage template (1.0 only for the Prime from the original
  photo; `denoise` in `workspaces.json`, tool `comfy_workflows.py denoise`); the edit stages now run at 0.8 to 0.95, see the Oct 8 decision below. Tuning rules:
  [art/comfyui-art-pipeline.md](art/comfyui-art-pipeline.md#denoise-is-the-key-lever).
- **The Alpha stage (Oct 2026).** The first workflows of a hero are not poses: they create her likeness, so they have their own stage and folder, `alpha/`
  (sorts first). Alpha 1 Prime (original photo to the bikini A-pose, standard figure), Alpha 2 Bare (Prime to bare skin: individual build, hair, eyes, skin and
  bust re-asserted; the figure look sits flat in `1_Alpha/2_Bare/`, next to the hand-made `Alpha_2_Bare_Skin` shots; the celestial experiment (kept: it becomes body armor) is Alpha 2b in `alpha/bare/celestial/`; the bare-chest study and the covering experiments were dropped Oct 11) and Alpha 3 Barefoot and Heels (Bare image back into the bikini on her own figure, `alpha/footwear/`).
  `Alpha_2_Bare_Figure` is the intended Bare step; the hand-made `Alpha_2_Bare_Skin` shots are temporary while it is tuned and are not kept long term.
  Bare, Barefoot and Heels are the three golden images, named `<Hero>_Qwen_Alpha_1_Prime|Alpha_2_Bare|Alpha_3_Barefoot|Alpha_3_Heels_00000.png` (the `_00000`
  sorts above the numbered renders); `poses/` now holds only variations fed the Bare image. Input roles: `photo`, `prime`, `bare`, `apose` (the Barefoot image), `heels`
  (`workspaces.json` `inputRoles` and `inputs`, `inputs set --prime`). Sisters and Angel Primes (Angelica and Angelo included) use it; dragons and bound heroes keep their X Pose in `poses/` for now. The Barefoot and
  Heels cards still use the photo-oriented `pose-female-human.txt`; an edit-focused template for them is open, as is the same for the other stages.
- **Individual physique, standard X Pose (Oct 2026).** The 10 sisters and 10 bound heroes each carry their own build (`physique`: `torso` and `arms` are new optional fields; the male
  schema stays `chest`/`waist` plus `arms`), merged from an external review (`docs/codex/heroes/*_physique.md`, `elder_dragons_details.md`); its colours, metals, prompt-assembly sections and
  invented ids were not adopted. The X Pose from the original photo keeps the standard lithe, slender figure (`figureProfile: standard`, text in `data/art/_settings/phrases.json`); the
  individual build is applied from the Bare stage on (`Body:` line), so it never fights the original photo, clothes or background. The 10 Elder Dragons gain structured morphology
  (`silhouette`, `scaleTexture`, `wingMembrane`, `hornsAndCrest`, `elementalVenting`) in our own palettes. Studio smile: new `studio-soft-smile` (A-pose and head default).
- **Two celestial looks and a two-step core (Oct 2026, ideation).** The original larger plates are kept as `celestial-plate-armor`; the new
  `celestial-skin-armor` is thin metallic design formed on the skin by magic (open filigree, form-fitting, skin showing through, her class and element
  motif). The `bare` stage (`Bare_*`) is an edit-only pass on a finished A-pose; `Bare_CelestialPlate` and `Bare_CelestialCore` (skin) produce a
  "celestial A-pose" that can be fed into scenes, showcases or other outfits to carry her celestial form into the picture. Later: Shiny and Holo
  editions add glow, a little more coverage and accessories, probably as a second pass on that image.
- **Theme scenes have two paths over one library (Oct 2026).** Every outfit, armor, jewelry, footwear, headwear and weapon item is a
  library piece, never inline text in a card (generic fillers such as "bare arms" excepted), so a scene can be built either way: a
  *complete* scene (`<hero>-scene-<theme>`) names all the pieces so the model has freedom and a scene can be tested at once, or a
  *pre-staged* path where a studio outfit card (`<hero>-armor|clothing-<theme>`) is rendered first and the `-scene-staged-<theme>`
  card only adds scene, effects and pose. Each sister has six themes (the 12 new packs plus the older ones); effects, expression and pose
  stay literal text on the card. Raven armor is now pieces (`heroes/drakn-sisters/drakness/armor/raven-*`).
- **Every bust is full, firm and lifted, on purpose (Oct 2026).** Clothing and armor that is applied to a flatter or lower body loses the bust line, so the Alpha images
  establish a lifted, crisp cleavage for every sister (shared `bustKey` for the Prime, each sister's own `bust` line for the Bare step through the `ownBust` key; the
  lines differ in shape and detail, not in lift), and the standard `fitted-contour` / `armor-contour` pieces (also `-male` variants, applied to male heroes) tell every
  outfit to follow and support the bust, waist and hips unless a card opts out. Explicit anatomical wording stays in the hand-made `zz_Shots`, never in generated files.
- **Angel Primes is the clean test bed (Oct 2026).** Twenty angels (ten female, ten male, humans only, no card, `testBed`) on a good-to-evil spectrum, one female and one male
  per element in each of ten pairs, each with a bonded non-dragon pet (`data/art/pets/angel-primes/`). New things (themes, backgrounds, creatures, clothing, weapons,
  motions) are tried here and only the ones that work are pulled into the Drakn workspaces; Drakness is no longer the test-everything hero. Roster, kits and the full
  set (about 179 prompts per female angel and about 105 per male angel) are in [../data/art/README.md](../data/art/README.md#angel-primes-the-clean-test-bed). Angelica and Angelo stay as the older pair
  (the only ones named Prime; their art slugs are `angelica` and `angelo`, like every other angel); every other angel has a family name, shared by the pair. Every angel owns signature items
  (weapon, armor, gown or attire, circlet, jewelry, elemental drift) under `heroes/angel-primes/<division>/<slug>/`, each built with `extends` on a library piece plus her element and alignment
  (written by `scaffold_angel_library.py`; her signature, battle, spell-calling, armor-stand and elegant-casting cards use them). The male angels now have the full set too (see the male wardrobe pack decision below).
- **Pieces can extend pieces (Oct 2026).** A piece may name a base (`"extends"`), carry only what differs, and use `{{BASE}}` or a leading `+` to splice the base text in: a standard
  silver necklace plus a hero's own details instead of a second full description. Validator-checked (exists, same kind, no cycle) and tested (`tools/generators/test_gen_prompt_extends.py`).
  `tools/art/extract_literals.py` moved repeated inline sentences (jewelry, anklets, effects, companions) out of 1,604 card slots into 67 pieces with every prompt unchanged. Still inline by design:
  generic fillers ("bare arms", "empty hands") and the long pose literals of the sisters' scenes (a motion piece needs many fields); converting more sister signature items to `extends` is open.
- **Frames, designs and shared poses (Oct 2026).** A base piece can be a frame with named gaps (`[[SLOT]]`); a piece that extends it fills them with `vars`, or takes them from one design file
  (`"varsFrom"`, kind `design`) so several pieces of one hero share one set of values. The ten sisters' four celestial armor pieces (plate, fitted plate, skin armor, skin suit) are now four frames
  in `wardrobe/armor/celestial/frame/` plus one `celestial-design.json` per sister (metal, breast and hip shapes, engraving, gem); every prompt is unchanged. Repeated scene poses and expressions became
  pieces too (kinds `pose` and `expression` in `motion/scene/` and `motion/expressions/scene/`, or in a hero's own folder): the 405-character lineup pose, the battle leap and the bond pose that all
  ten sisters (and every angel) carried inline. Still inline by design: generic fillers ("bare arms", "empty hands"), one-off pose sentences and each sister's own gown, robe and regalia wording (a frame fits
  them, but their grammar differs; do it when one is rewritten anyway).
- **Realism is a setting, not a rewrite (Oct 2026).** The default realm line says "a high-fantasy, Dungeons & Dragons-style realm ... living magic", which pulls Qwen toward illustrated, game-box art. A second realm,
  `realms/fantasy-cinematic`, describes the same fantasy backgrounds as a film still shot on location (real materials, natural light, subtle magic, with bans on cartoon, illustration and cel shading). A realm is
  chosen per card (`components.realm`), per hero (`art.defaultRealm`) or for a whole group (`_settings/studio.json` `realmByGroup`). Angel Primes, the test bed, uses the cinematic realm and grounded versions of
  the ten elemental realms (`backgrounds/fantasy/elemental/grounded/`); each angel also has a Signature (illustrated) twin in the old realm so the two looks sit side by side. The sisters are unchanged until
  you have compared renders. `python tools/art/style_audit.py` ranks the pieces that lean illustrated (the realm line, the elemental realms, forests, caves and libraries score highest; most other
  backgrounds are already grounded). Open: pick the look per set after the first comparison, rewrite the worst-scoring backgrounds, and decide where a card-like (cartoon) look is wanted on purpose.
- **Default images are pulled back from the workspaces (Oct 2026).** The photo and golden images a workflow loads are chosen inside ComfyUI (Load Image node) and live in `workspaces.json` (`photos`, `inputs`). `inputs pull` reads the choices back
  (generated Qwen workflows only; placeholders and other heroes' images ignored; unanimous per hero and role, otherwise `MIXED`), `status` flags `inputs-changed`, `setup` pulls first and `inputs reset` stops until a choice is pulled, so a reset cannot undo it.
  The ten women's photos and Angelica's were pulled this way. Angelica and Angelo now have the same Phase 1 and 2 as every other angel (the old `X_Pose` card and workflow are retired; her pastel bikini no longer carries heels).
- **Male wardrobe pack (Oct 2026).** Ten swimwear and underlayer pieces, twelve clothing sets (tuxedo, suit, military dress, trench coat ...) and one man's outfit for each of the 26 theme packs, written in
  realistic tailoring terms. The male angels now get wardrobe, theme, showcase and scene cards (about 105 prompts each, up from 57). Library pieces are written for women, so for a male hero the generator turns
  she/her into he/his/him in the finished prompt (`masculine()` in `gen_prompt.py`); before this the male angels' motion and hair prompts said "her". Male-angel themes use only male or unisex outfits,
  armor, headwear and jewelry; footwear, props and weapons unless tagged female.
- **One tree in every layer, with divisions (Oct 2026).** A group listed in `data/art/_settings/groups.json` files its work below a division folder
  (`angel-primes`: `female`, `male`, `pets`, `units`, `buildings`, `equipment`, `tactics`, `workers`, the Sovereign Dawn card categories with heroes split by sex). The same path is used for the identity
  (`data/art/heroes/angel-primes/female/seraphine.json`), the cards (`_sets/angel-primes/female/seraphine/...`), the prompts
  (`prompts/angel-primes/female/Seraphine/...`) and the ComfyUI output and workspace folders (`female/Seraphine/1_Alpha/...`), so the Angel Primes workspace is one tree for a
  whole test deck instead of a workspace per kind. The Drakn groups and the Elder Dragons stay as separate groups and workspaces (decided Oct 2026: ten story characters each, they
  will not grow); the Sovereign Territories set is expected to use the division scheme.

## Planned workspaces: what is left

The workspace tool skips any workspace whose `status` is not `active` or whose install folder is missing, so these can be prepared in the repo first.

| Workspace | Home of | Ready in the repo | Still to do |
| --- | --- | --- | --- |
| Drakn Bound | the ten bound heroes | identities and the `homes` rule | art sets and prompts (clone the sister kit: `scaffold-sister`), an install (clone Drakn Sisters, then `cleanup` it), set `status` to `active`, then `setup-workspace "Drakn Bound" --apply` |
| Elder Dragons | the ten dragons (text-to-image plates, heads, lairs) | identities, lair backgrounds, the `homes` rule | dragon card sets (heads, lairs, a plate stage), the install, `active`, `setup-workspace` |
| FireRed workspace | the photoreal engine's copies (today local test files, not in git) | `--engine firered` builds, `refresh-firered` | decide whether it gets its own install or stays a folder in each home; a FireRed template check |
| Sovereign Territories set | title, logo, icons, key art, plates | 22 workflows, 4 curated pulled into the repo | divisions for units, buildings, tactics art; the Drakn videos are not published there (publish a set only when you want it: `publish`) |

Order: Drakn Bound first (its heroes mirror the sisters, so the generators already fit), then Elder Dragons.

## Open decisions

| ID | Question | Notes |
| --- | --- | --- |
| O1 | ~~3 or 5 elements in the first public release?~~ Answered Oct 9 | The MVP is Darkness and Light only; Fire, Grass, Water and Earth are the next cycle, added for the real release. The cost of one full element (seen from the sisters and angels) is the reason. |
| O2 | Does "exactly one hero per formation" survive? | Written before the art pipeline made a larger roster cheap. Revisit after a playtest. |
| O3 | How are vision cards obtained? | All 30 have empty `acquisition` today. Needs pack/reward/campaign rules, including the quest-earned Celestial edition, the pack-chance share and the codex teaser. |
| O4 | Transcendent format legality | 64 points exceeds any starter budget; decide special formats (Phase 2+). |
| O5 | Deck rule for Neutral cards | Neutral cards (tactics, items, utility, lower-tier cards, and the Angel Primes herald pair Angelica and Angelo) are meant to be playable in any deck. Write the rule (always legal, count limits, can a Neutral hero lead a deck) into the deck and combat docs. |
| O6 | Angel Primes spells and abilities | Not defined for any angel. The nearest art-side hooks are the signature weapon and the element's magic colour. |
| O7 | Story link between each angel and the same-element Drakn sister | Ally, mirror or rival; the alignment ladder (1 radiant to 10 fallen) is only the starting material. |
| O8 | Adopt `AP-###` into data | Proposal: women AP-001 to AP-011, men AP-012 to AP-022 (Angelica AP-001, Angelo AP-012). Needs a series entry and cards. |
| O9 | Roster page names | `sovereign_dawn_codex.md`, `angel_primes_codex.md` are rosters, not the codex (the JSON is). Rename to `*_roster.md`? |
| O10 | Wording to fix in Draknara | Her arms say "toned forearms without bulk" (a negation that names bulk). Left unchanged until you decide. |
| O12 | Video size and duration | Decided Oct 9: two templates, `ST6_MiniMax_Reel` (9:16 for Facebook reels, the default) and `ST6_MiniMax_Match` (the still's shape), picked by the card's `format`; 8 s, turbo on. The old 640x960 default squeezed the 944x1104 stills about 22% because the video model stretches its first frame. To do: try one clip from each (plan 8.5). Analysis in `docs/art/minimax-h3-video-templates.md`. |
| O11 | Move the Drakn Bound men to the 1_Alpha chain | They still use the older single `X_Pose` Prime card; the sisters and angels use standard figure at 1_Prime and the individual build at 2_Bare. |

## Agreed next steps (Oct 8, 2026)

Five steps (0 to 4), done in this order. Each one ends with a pause: a summary of what was done, then the go-ahead for the next. Step 3 is itself split into phases (3a to 3d) with a pause after each.

| Step | What | Plan |
| --- | --- | --- |
| 0 | **Done (Oct 8).** Commit and push everything | Four commits on `ideation/hero-roster-10-elements`: (1) tooling, schemas, launchers and docs, (2) art and animation data, (3) generated prompts, (4) workflows and `workspaces.json`; then push to GitHub. Backups (`workflows/.sync/`) stay ignored. |
| 1 | **Done (Oct 8).** Alpha test sets: `angel-primes/alpha/female` and `alpha/male` | Two reusable test-bed heroes in a new `alpha` division, so any photo can be tried as an angel without touching a real angel's folders or output. A small version of the phases (see below). |
| 2 | **Done (Oct 8), rolled out to the repo and Angel Primes; Drakn workspaces pending.** Higher denoise for edits that change a lot | Raise the denoise of the Bare, footwear, pose, motion and scene edits (0.7 holds the pose too tight); let the prompt's positive likeness text carry the likeness. Find what you actually used in the Drakness `zz_Shots` first. |
| 3 | **In progress: 3a done (Oct 8).** Signature items for Angelica and Angelo | The same definition and art as the other twenty angels: element and alignment, wings, pet, signature weapon, armor, gown or attire, circlet, jewelry, elemental drift, and the cards that use them. |
| 4 | Sisters' companions from the Elder Dragon definitions | The sisters' dragon companions are text copied into companion pieces and cards; the Elder Dragon identity files are not used. Make one canonical companion piece per dragon from its identity and let each sister's piece extend it with only the scene placement. See below. |

### Step 1: alpha test sets

- **Where:** division `alpha` of group `angel-primes`, one test-bed hero per sex (`data/art/heroes/angel-primes/alpha/<slug>.json`, `_sets/angel-primes/alpha/<slug>/`, `prompts/angel-primes/alpha/<Hero>/`, workspace and output folder `alpha/<Hero>/...`). Their identity is as generic as Angelica's and Angelo's (the reference photo's own face, hair and eyes, no fixed look), so any photo works.
- **What is in the small set:** Phase 1 complete (Prime, Bare, Bare chest, Barefoot and Heels for the woman; Prime and Bare for the man), Phase 2 core (head, face close-up, a few head and body views, two hairstyles), two layer tests, one clothing and one armor card, a few motions and two scenes. Enough to see whether a photo makes a better angel; not the 180-card suite.
- **Using it:** put the photo in the `Angel Primes` input folder, pick it in the Prime workflow's Load Image node, run Phase 1 and 2, and compare. If it wins, give that photo to an angel (`inputs --set` or the same pick in her Prime workflow, then `inputs pull`). `inputs pull` also picks up the test photo, so it never overwrites an angel's.
- **Built (Oct 8):** hero names `Female` and `Male` (folders `alpha/Female/...`, `alpha/Male/...`), made by `scaffold_angel_set.py --alpha` (`bin\scaffold-angels.cmd --alpha`) from library pieces only, with a short studio library (`scaffold_studio_library.py --small`) and a shared `wardrobe/capes/wings/white-angel-wings`.
  The woman has 23 cards and workflows (+2 FireRed scenes), the man 20 (+2): Phase 1 (Prime, Bare, and for her Bare chest, Barefoot, Heels; no 2b experiments), Phase 2 (head, face close-up, 2 head views, 3 body views, 2 hairstyles), 2 layer tests, 1 outfit, 1 armor,
  Glamour and Signature scenes (cinematic realm), 3 motions. Their inputs and photos are in `workspaces.json` (`alpha_female_photo_944x1104.png` and `alpha_male_photo_944x1104.png` are placeholders: pick a photo in the Prime workflow, then `inputs pull`).
  `gen_prompt.py --slug` now matches the hero folder only, so `--slug female` no longer means the whole `female` division. Not touched: every angel's folders, prompts, workflows, photos and output.

### Step 2: denoise

- **Today:** each card carries a hint (`~0.5-0.7`) and `denoise_for` picks the high end (0.7); a full redraw from the photo is 1.0 and drops to 0.7 when fed a golden image. At 0.7 the edit keeps the person and also the pose.
- **Plan:**
  - (a) Read the denoise values saved in the Drakness `zz_Shots` and curated workflows (Drakn Sisters and Drakness) to see what you settled on.
  - (b) Set the new values per stage in one table in `workspaces.json` (`denoise.stages`, over the card hints); proposed starting points are about 0.9 for Bare and footwear edits, motions and scene edits,
    tuned on one angel set first.
  - (c) Strengthen the likeness wording in the positive "Critical details" and fidelity paragraphs of the edit templates, because a higher denoise leans on the prompt.
  - (d) Apply with `denoise --reset` (preview first), which changes only the denoise widget in the repo and the workspaces, so seeds and inputs stay.
- **Risk to watch:** higher denoise loosens the likeness; compare a few renders per stage before regenerating everything, and keep hand-made `zz_` workflows untouched.
- **What you had used (read from the workspaces):** your hand-made Drakness armor edits (`zz_Curated_Drakness_Qwen_Armor_Bikini`, `..._Armor_Bone`) run at 0.9, and the Drakn Sisters `Alpha_2_Bare` shots at 0.8
  (one in the workspace); the older curated ones are at the template default. The generated defaults were 0.7 for edits and scenes, 0.6 for motion, head and hair.
- **Built and applied (Oct 8):** the range is in each stage template, not on the cards (the card `denoise` field is only a note), so the change is 16 template lines plus `denoise.golden` 0.7 to 0.9. New defaults (high end of the range):
  Bare, outfit, armor, clothing, scenes, showcases, body views and the golden-fed Barefoot, Heels and layer tests **0.9**; motion **0.95**; head and hair **0.8**; staged scenes **0.8**; Prime 1.0, final 0.8 and polish 0.4 unchanged.
  Full table in [art/comfyui-art-pipeline.md](art/comfyui-art-pipeline.md#denoise-is-the-key-lever).
- **Likeness in the positive prompt:** the Critical details block (hair, eyes, skin and the hero's own bust line, the same lines as the Prime) is now switched on for every edit stage in
  `TEMPLATE_KEY_DEFAULTS` (hair edits leave out the hair line, staged scenes keep eyes and skin only), and the `hair` and `scene-staged` templates got the slot.
  All 4,996 prompts were regenerated: 4,147 changed, and every changed line is the `Denoise` header or the added Critical details block (checked against git: 0 other lines).
- **Safety:** `denoise --reset` now keeps a denoise you set by hand in a workspace (a workspace file that differs from its repo copy is listed as `KEPT`; `--force` overwrites, with a backup) and takes `-w` to limit the workspaces. 5 new tests (43 in all).
- **Applied so far:** all repo workflows (5,274 denoise values, 3,883 prompt texts), the Angel Primes workspace (prompt text and 3,091 denoise values) and, on Oct 8, Drakn Sisters (1,911 aligned; 1,843 denoise values reset). **Not yet applied:** Drakness and Sovereign Dawn Series, which hold final art and may be in use. Per workspace, preview then apply:
  `comfy_workflows.py setup -w "<workspace>"` then `--apply`, then `comfy_workflows.py denoise --reset -w "<workspace>" --dry-run` and without `--dry-run`.
  `setup` only patches prompt text, so the workspace keeps its old denoise and `denoise --reset` lists nearly everything as KEPT (a hand-set guess).
  Compare against the repo's pre-Oct-8 values (`git show 2d23454d0:<path>`) to find the few that really were hand-set, then run `denoise --reset --force` (each changed file is backed up first) and put those back.
  In Drakn Sisters the only one was `Drakness_Qwen_Alpha_2_Bare_Figure` at 0.8, which was kept.
- **To check on renders:** that the 0.9 and 0.95 edits keep the face (if not, lower that stage's range in its template, regenerate, `update`, `denoise --reset`), and that the Critical details lines read well in the finished prompts.

### Step 3: signature items for Angelica and Angelo

- **3a. Definition. Done (Oct 8).** No cards are generated yet; this is only the definition, for you to review.
  - **Element and alignment:** Neutral (the eleventh element; added to the hero and pet schemas) and Balanced (neutral good), rank 5, as an eleventh pair beside the ten. Their palette is already pearl white and champagne gold, so the tone is "clean, with a quiet shine".
    A new `rotation` key (10) in their kits makes them take their own slice of every library pool instead of repeating Sandalyn and Baracel's rank-5 picks.
  - **Element tables:** material (soft white light, drifting pale feathers), motif (a single white feather within a plain ring), weapon family (polearms), the animation motion `feathers-drift`, and a new realm: `backgrounds/fantasy/elemental/meridian-vale-realm` (a high white-stone plateau) with its grounded twin.
  - **Identity:** each has a `profile` like the other angels (archetype: the first herald and the first sentinel; inspired by the messenger and the guardian angels; wings; pair; pet).
  - **Wings and pets:** pearl-white wings edged in champagne gold (his with dove-grey primaries); pets Plume (a pearl-white dove) and Ward (a lean pale hound), neither a dragon, with `companion` pieces for the scene slot and the two-way links to their angels.
  - **Kits** (`_kits/angel-primes/angelica.json`, `angelo.json`): three underlayers, three outfits, two armors, four motions, heels and a signature scene, picked to differ from the layers and clothing they already have; the paladin plate for her, the parade plate for him.
  - **Generators:** once a kit exists the normal kit builder takes over for them (it only adds what is missing, so their hand-picked cards stay); the "keep it pure" filter for lawful angels also skips shadow, umbral and raven pieces.
  - **To confirm before 3b:** Neutral at rank 5 for the pair, the two pets, and the wings.
- **3b. Signature pieces. Done (Oct 8).** The same six signature pieces as every angel (weapon, armor, gown or attire, circlet, jewelry, elemental drift), each extending a library piece plus their element and alignment tone, and the signature armor and gown wardrobe cards.
- **3c. Cards. Done (Oct 8).** The rest of the angel suite around those pieces (showcases, signature, battle, spell-calling and glamour scenes, theme scenes, video), keeping their hand-picked layers, clothing and modern scenes.
- **3d. Regenerate and verify. Done (Oct 8).** Angelica has 164 cards and Angelo 89, with the same signature pieces as every angel (picked by the kit's `signature` override: her paladin holy plate, spear, column gown and silver circlet; his full plate, halberd, long coat and laurel wreath).
  Validator OK, prompts generated (0 failures, no she/her in Angelo's prompts), workflows made for Qwen, FireRed and MiniMax, deployed to Angel Primes (3,386 aligned, 0 stale, 0 missing), Phase 1 and 2 audit 0 problems.

### Step 4: the sisters' companions from the Elder Dragon definitions. Done (Oct 8)

- **Result:** each dragon has two frames, `data/art/dragons/elder-dragons/<slug>/companion/<slug>-companion.json` (the identity's description, with `[[PLACEMENT]]` and `[[DETAIL]]` gaps) and `<slug>-companion-distant.json` (the opening and name only, for scenes that word the dragon themselves).
  The 20 sister companion pieces and the 20 sentences that scene cards carried inline (now 20 new pieces, 40 in all) extend a frame and fill the gaps with `vars`; the cards name the piece. `tools/art/dragon_companions.py` writes it all (re-runnable; `--apply`), and every conversion is asserted to join back to the old text.
  All 5,271 prompts came out byte-identical, so nothing changed in the images' wording yet; the gain is that an edit to a dragon's identity now reaches the frames, and the full-frame scenes through them.
- **Validator:** a sister's companion piece must extend a piece under `data/art/dragons/`, and a sister scene must name its companion as a piece, not type the dragon (2 mutation cases, both in `--quick`). Pieces under `dragons/<group>/<slug>/` are now validated as pieces.
- **Still hand-worded:** 23 scene texts describe the dragon their own way (distant silhouettes, close-ups), and 10 of them cite only one of its colours or miss one (for example Venomis, tarnished brass). They use the distant frame; review them when you want the dragons to match their identities exactly (`dragon_companions.py` lists them).
- **Original plan, kept for the record:**

- **Today:** each sister has two companion pieces (`heroes/drakn-sisters/<slug>/companion/`, for example "her aligned Elder Dragon, Terrador, a vast distant silhouette on the far ridge...") and some scene cards, such as the Draknara Bond scene, carry the dragon as an inline sentence.
  The Elder Dragon identity files (`data/art/dragons/elder-dragons/<slug>.json`: description, silhouette, scale texture, wing membrane, horns and crest, elemental venting) are not used by them, so the same dragon is described several ways and an edit to the dragon changes nothing in the scenes.
- **Proposed reconciliation:** (1) audit every sister companion piece and inline companion sentence against the dragon's identity; (2) one canonical companion piece per dragon, written from the identity (`data/art/dragons/elder-dragons/<slug>/companion/`, kind `companion`, the dragon as it looks in a scene);
  (3) each sister's companion pieces `extend` it and add only the scene placement with `+` (a distant silhouette on the ridge, towering beside her with its head lowered, ...), and the cards reference pieces instead of carrying sentences; (4) a validator check that a sister's companion piece extends her dragon's; (5) regenerate and review the prompt differences, which will be intentional wording changes where the dragon's own description now shows through.
- **Why this way:** the dragon stays defined once, in its identity, and what a sister adds is only what changes from scene to scene. The alternative, a generator that builds the companion text from the identity at prompt time, hides the wording and cannot be adapted per scene.
- **To decide at the start:** whether the canonical piece is written by hand from the identity or generated by a small tool (proposed: a tool, re-runnable, so a change to a dragon reaches the pieces), and how much of the identity belongs in a scene (proposed: silhouette, scales, wings, horns and venting, not the lore).

## Workspace sync and the zz_ reconcile (Oct 8)

| Workspace | State | What is left |
| --- | --- | --- |
| Sovereign Territories | 18 aligned, 0 stale | its 4 `zz_Curated` items are identical to the repo and their prompts are fully covered by the art data: safe to delete from the workspace |
| Drakn Sisters | 1,987 aligned, 0 stale | its 38 `zz_Curated` are identical to the repo; 25 shots kept; `zz_Shots/alpha/bare/Drakness_Qwen_Alpha_2_Bare_Skin` is a different seed from the Drakness workspace copy (see below) |
| Drakness | 284 aligned, 0 stale | refreshed and its denoise reset to the repo values (Oct 8); 37 `zz_Curated` and 5 shots are identical to the repo and now covered by the art data (see the reconcile below); `Armor_Bikini_00001` is in the repo and was added back |
| Angel Primes | 3,650 aligned, 0 stale, 0 missing, 0 install-only | 35 numbered saves are shots in the repo; the 62 clone leftovers were moved to `workflows/.sync/backup` (22 male `X_Pose` files with no prompt, and 40 MiniMax videos that were rebuilt from the `7_Video` prompts, which come from `data/animation`) |
| Sovereign Dawn Series | 174 aligned | nothing |
| Drakn Bound, Elder Dragons | planned, no install | see the planned workspaces table |

- **Numbered saves are candidates (revised Oct 9).** A workflow ComfyUI saved from a render (`Azaline_Qwen_Alpha_1_Prime_00004_.json`) keeps that render's seed. Left loose in the list it is a candidate
  (see the plan `plans/2026-10-09-finals-and-mvp.md`): `pull` keeps it in `workflows/_candidates/<set>/<Hero>/<phase>/` and `finals sort` files it in `zz_Candidates`; shots are what you save into `zz_Shots`. Moving a good seed into the art data (so the generated workflows carry it) is Phase 3 of that plan.
- **Two seeds, one name.** `Drakness_Qwen_Alpha_2_Bare_Skin` exists as a shot in Drakn Sisters (seed 517397163969845) and in Drakness (seed 119517098111188). A repo shot holds one, so `pull --only shots` now keeps the first and reports `CONFLICT`; rename one in its workspace to keep both.
- **The zz_Curated reconcile (Oct 8).** Every curated prompt was compared with `data/art`. Result: **hair 12 of 12** and **motion 8 of 8** trace to art pieces by their `sourceVariant`; the Bone, Raven, Iridescent and Gown armor and clothing were already folded in (the pieces note the prompt they came from); the X_Head and both X_Pose prompts are replaced by the Prime, Bare and head cards; the 4 Sovereign Territories prompts are fully covered.
  Four designs were missing and are now art: the violet **Chain Bikini** armor, the **Elegant** armor (ornate bikini armor under glowing waist drapes) with an **Elegant Pointed Toe** variant, and the **Bikini-Strap Gown**.
  They are reusable wardrobe pieces (`armor/bikini/chain-disc-bikini`, `ornate-bikini-armor`, `capes/drapes/ethereal-waist-drapes`, three heels, `clothing/gowns/bikini-strap-evening-gown`) in her palette tokens, plus four Drakness cards, with prompts and Qwen workflows deployed. The Raven boots gained the matching upper-left thigh band.
  **Not captured, to decide:** the per-outfit lipstick and nail colours (the curated prompts use Deep, Light or Midnight Violet by outfit; the identity holds one value each); the dimples line of `X_Pose_Original`; the Raven and Bone *battle stance* poses and the Gown_Pose wording (the closest are the Bench motion cards).
- **FireRed 1_Alpha everywhere (new).** Every 1_Alpha step (Prime, Bare, Footwear, 2b experiments) of every hero has a FireRed workflow beside the Qwen one (244 built), and the Angel Primes `alpha/female` and `alpha/male` sets carry the whole suite in both engines (23 and 20 each), all deployed to Angel Primes and Drakn Sisters (and the 9 for Drakness).
  The FireRed steps read the same input images as their Qwen twins, so a FireRed Bare starts from the Qwen Prime; pick another image in ComfyUI to run a pure FireRed chain. Which engine each phase should use is still a test, and the documents that name one are assumptions until you decide.
- **Filename case (Oct 8).** Git tracked 20 older-angel prompts and workflows as `Head_Face_Closeup` while the generator writes `Head_face_closeup`; a branch switch rewrote them and Angel Primes showed 20 missing. They are renamed to the generator's case. Many "missing" and "install-only" pairs that differ only by case point to this.

## Negations in prompts (Oct 9)

"Do not recolour" recoloured and "no pale areas" paled: a model reads a negation as the thing it names. A scan of all 5,475 positive prompts found **39,755 negation hits**, nearly all from a few shared sources (the angels' palette strings, the eye-effect pieces, the contour pieces, the sisters' build text, the studio lighting, the realms and the shared templates).
They are removed at the source (243 data files plus the hair-motion scaffold; about 50 rules, each dropping a tail whose positive half was already in the sentence) and all prompts regenerated: **0 command phrases ("do not", "never", "avoid") and 0 flip-risk phrases are left**; the generic review list fell from about 31,000 hits to about 360 (descriptive ones such as "without bulk"), plus 1,428 in allowlisted video prompts.
Examples: `do not recolour` (5,687), `do not alter undertone` (3,260), `no backlight or rim light` (3,300), `no gap between them ... rather than drooping` (2,540), `not glowing` (1,886), `no pale areas` (1,447), `no footwear` (1,299), `not squinting` and `no squint` (about 2,500), `nothing from the modern world` (929), `no breeze` became `still air`, and "Change nothing else: keep" became "Keep".
`tools/art/negation_audit.py` (`bin\negation-audit.cmd`) now keeps it that way: `validate.cmd` runs it in check mode, and the rules and allowlist are in `data/art/_settings/negation-audit.json`. The README rule is "Write positives, not negations".
**Left on purpose:** the video prompts (no negative prompt on the video model), gameplay-card lore (the card owns it), brand text ("no text"). (The 2b covering experiments, which said "only these three coverings", were dropped Oct 11.)
**Also done (Oct 9):** "lightly enhanced" and "gently enhanced" in the angels' skin, hair and eye strings (24 identities) invited change as much as the old negatives did, so they now say "exactly as in the reference image".
They keep only the detail (evenly toned, healthy shine and dimension, crisp definition).
The eye string is now "irises in their natural colour ..." so it also reads correctly inside the glow pieces (it used to say "natural natural"). 3,260 angel prompts regenerated and deployed.
If one photo needs brightening, do it on that angel's own identity, not as a default.

### Positive-wording pass (Oct 11): what is fixed, what is flagged

The audit tool is a fixed word list and is **not exhaustive**, so the templates and the Alpha-path pieces were also read line by line. Fixed (positive text in the positive prompt, negatives left to the negative prompt):
the Bare templates ("remove all clothing, swimwear, straps ..." became "the subject appears exactly as described in the Result"), `head-human` and `polish-human` ("keep the wardrobe unchanged", "without changing it"), `scene-staged-human` ("unchanged"),
the pieces `bare-skin-study(-male)` ("nothing but", "unretouched"), `skin-tone-base-layer` ("shows no straps ..."), the celestial suit and armor pieces ("Not covered", "none is a cup", "unchanged natural skin"),
and about 15 one-off pieces and cards ("no headwear", "no visible pupil", "without bulk", "nothing in hand", "no bigger than a hand", "without fear", ...). The audit's REVIEW list is now 0.
**Flagged for a later pass (not changed, outside the Alpha path):**

| Where | Wording | Why left |
| --- | --- | --- |
| 20 drakn-bound cards (`_sets/drakn-bound/*/4_Wardrobe/armor/*-armor-default.json`, `5_Scenes/*-scene-signature.json`) | `"jewelry": "none, unadorned"` | a bulk edit of 20 cards; the heroes are not on the current path. Use a positive piece ("bare neck, wrists and fingers") when they come up |
| `wardrobe/effects/contour/*` (4 pieces) | "... unless this prompt says otherwise: ..." (2,629 prompts) | a conditional, not a negation, but it asks the model to reason about its own prompt; needs a test render before changing |
| `_templates/brand/harmonize.txt` | "must not change", "Do not add, remove or merge people" | a command in a positive prompt; brand text is allowlisted, rewrite when the brand set is rerun |
| Brand and icon prompts | "No text, no lettering" | left on purpose: a text-to-image prompt has no other tool |
| `Wearing: only a ...` (406 Alpha prompts) | "only" restricts rather than negates | it is how the Prime keeps one garment; review if the swimsuit bleeds |
| Every template negative prompt | long lists | the Qwen negative prompts are fine; FireRed has none, so test the FireRed output before adding more |

## Angel Primes: builds, colours, roster docs (Oct 9)

- **No body-builder women.** Camaris, Sandalyn, Remiah, Nyxene, Ravaelle and Haniya had strength wording (Sandalyn came out "ape" muscular). The women now vary by height, leg length, softness, curve and visible tone (petite Haniya; tall Gavrielle, Nyxene and Seraphine; curvy Camaris, Ravaelle and Sandalyn; medium Angelica; crisp abs on Remiah and Nyxene, soft on Ravaelle and Seraphine).
  None uses bulk words. Toned abs, arms and legs are wanted; the limit is a body-builder look. The men stay a deliberate mix of lean, heroic and heavy.
- **Sisters audited, not changed.** None of the ten uses body-builder wording and their tone vocabulary is kept. Only Draknara's "toned forearms without bulk" is flagged (a negation that names bulk). `drakn_sisters_physique.md` now mirrors the identity JSON (its palette and build text was out of date) and has a rationale and audit section.
- **Numbering and Neutral.** The angels are grouped women AP-001 to AP-011 and men AP-012 to AP-022 (Angelica AP-001, Angelo AP-012). Neutral is recorded in `sovereign_dawn_codex.md` as a deliberate element slot with no sisters, bound heroes or Elder Dragons, used for cross-element cards and the herald pair; the deck rule for it is an open question.
- **Colours forced.** All 22 angels now define hair, eye and skin colour (plus their negative lists), so the 1_Prime and 2_Bare prompts change the photo to match. Angelica and Angelo used to follow the photo; their colours are a first choice that can be edited. The bound heroes gained `hairColorNegatives` (they already forced hair, eyes and skin).
- **Standard male figure.** Male Prime cards get `figureProfile: standard` like the women (`standardFigure.male` in `phrases.json`; the scaffold sets it for both sexes). The individual build is applied at 2_Bare.
- **Audit.** `python tools/art/identity_audit.py` (`bin\identity-audit.cmd`, run by `validate.cmd`) checks every angel, sister and bound hero: colours defined and carried by the Prime prompt, the Bare prompt applies the build, no strength words on a female angel. The alpha test heroes follow the photo on purpose. Bound heroes still use the older `X_Pose` Prime card.
- **Docs.** New `angel_primes_codex.md` and `angel_primes_physique.md`; `ideation_codex.md` is now `sovereign_dawn_codex.md`. Series IDs fixed: Sovereign Dawn is `SD-###` (the roster wrongly said `ST-###`); the angels are planned as `AP-###` (proposal: women AP-001 to AP-011, men AP-012 to AP-022). The roster tables no longer carry art-progress columns; use `python tools/workflows/comfy_workflows.py inputs status`.
- **Angelica and Angelo keep their look.** Her Prime still wears the iridescent pastel colour-blocked bikini (rose, sky blue, mint, lilac) and nothing in the colour work touched it. His trunks said "iridescent" too; they now say "softly pearlescent" so the sheen is lighter on a male (tune `angelic-pastel-trunks.json` if they look odd when rendered; no male Prime has been rendered yet). Their identity notes were rewritten (they said the colours followed the photo).
- **Roster pages now match the data (Oct 9).** The pages in `docs/codex/heroes` had drifted from the JSON:
  the sisters' and bound men's palette and build text, the dragons' morphology, the pet column (the card's `companion` is the Elder Dragon's name), the dragon race, and the "prompt assembly" sections (the real prompt comes from the templates, bare feet are the A-pose default, the men wear a swim brief). All were brought into line, with the reason for each build written down (`drakn_sisters_physique.md` section 5, `drakn_bound_physique.md` section 5).
  `bin\codex-drift.cmd` (run by `validate.cmd`) now compares the roster tables, the sister, bound, dragon and angel pages with the cards and identities, so a change in the JSON that is not carried into the page fails the check.
- **FireRed refresh fixed.** `comfy_workflows.py make --engine firered` only refreshed the scene class, so the FireRed Alpha cards (1_Prime, Bare, Barefoot, Heels, 2b) and Finals stayed stale after every prompt change. It now refreshes every FireRed workflow that already exists (the class list only limits `--create`). 436 stale FireRed workflows were updated and 351 missing ones created under `workflows/.test/firered` (a local test engine, kept out of git).
- **Open decisions** are listed under O5 to O11 in the table above.

## Library gaps (audit of Oct 8)

`tools/art/library_audit.py` (`bin\library-audit.cmd`) measures where the library is thin, over-used or built from shortcuts, and is meant to be re-run as the library grows. **Over-use is the signal, not unused pieces** (pieces are written ahead of their scenes):
a piece doing most of a folder's work for many heroes means the look repeats, unless it is on purpose (a studio default, ten sisters in one base robe), which is recorded with its reason in `data/art/_settings/library-audit.json`. What it found, in the order to work through it:

| Order | Gap | Result | Still open |
| --- | --- | --- | --- |
| 1 | Robes | **Done.** 15 robes; each angel's robe scene matched to element | more robe families when a theme needs them |
| 2 | Over-used pieces | **Done for the angels.** Modern backgrounds (32, was 14), shared scene effects (18), flats and sandals (10 each), staves (8), wands (7) and the six armor families (+3 each) were filled and spread across the angel cards by element or rotation (238 cards); the audit is clean except for the allowlisted sharing | the Drakn Sisters still share their scenes on purpose (recorded in the allowlist); pieces nothing uses yet (8 helms, 7 cloaks, 6 bracers) are information only |
| 3 | Jewelry | **Done for the angels' occasion showcases.** 31 atomic pieces and nine sets; editorial, glamour and city-street showcases wear a set in each angel's own metal and gem (121 cards); the sets carry no belly ring so they suit gowns | move the remaining cards off the old bundles (`library_audit.py` lists them under SHORTCUTS); belly rings go on bikini and armor cards one by one; grow headwear (circlets, hats, hoods are 3 each) |
| 4 | Makeup and highlights | **Done to start.** 50 makeup looks (was 3) and 20 highlights (was 14); the female angels' 200 occasion showcases each wear a look, spread so no family repeats one | per-outfit lip and nail colour is not supported (one value per identity); only showcase and scene templates render makeup; more looks as trends move |
| 5 | Hair | 10 short styles added (6 male, 4 female) | the male angels' default hair is still the textured crop (allowlisted until their photos are chosen); add hair study cards for the new styles |
| 6 | Races | not started: seven non-human races are one `race.json` each | flesh out when the `{{RACE}}` slot is wired for bound heroes |

## Scenes: series, character and theme (Oct 8)

Scenes now have three tiers (explained in [data/art/README.md](../data/art/README.md#scenes-series-character-theme)): a **series** the whole cast shares for the marketing pictures (Lineup, The Dawn, The Bond, Robe, Casting, Battle, Enchanted Evening, Signature), **character** scenes unique to each hero, and **theme** scenes.

| Added | For | Count |
| --- | --- | --- |
| **Lineup** (the flat-backdrop group cut-out the sisters already had) | the 22 angels | 22 |
| **Duty** and **Quiet**, from the alignment rank: Vigil, Blessing, Judgment, Reckoning, Exile; Cloister, Garden, Study, Watch Fire, Ruin | the 22 angels | 44 |
| **Domain**: the element at work in its realm (11 recipes) | angels and sisters | 32 |
| **Craft**: what the class does (Shaman, Shadow Knight, Bard, Necromancer, Summoner, Wizard, Enchanter, Cleric, Druid, Magician, Alchemist) | the 10 sisters | 10 |
| **Celebration** from a new theme pack, by element: coronation, masquerade ball, midwinter festival, siege defense, victory feast | angels and sisters | 32 |

That is 140 new cards, each with a prompt, a Qwen and a FireRed workflow, deployed to Angel Primes, Drakn Sisters and Drakness. The recipes live in `data/art/_settings/scene-recipes.json` (add a scene type there, then `bin\scaffold-characters.cmd`); the validator checks every rank, element and sister class has one.
Also new: two realms (`fantasy-gothic` for the fallen and grieving, `fantasy-pastoral` for gentle scenes) and five theme packs (31 in all, with a new `ceremony` group).

**Realistic realms for every element and class (Oct 8).** Each sister now has her own country and place, in the library so the males and later common and uncommon cards can use the same ones:
- **11 element homelands** (`realms/<element>-lands`): red-rock canyonlands (Draknara), ashen volcanic badlands (Draknora), tidal coast and reefs (Draknisa), glacial highlands (Draknira), windswept highlands (Draknava), storm plains (Drakneta), ancient greenwood (Drakniya), mangrove bayou (Draknoxa), radiant uplands (Drakniss), fogbound moors and crypts (Draknare and Drakness) and the meridian highlands (the neutral pair).
- **55 country environments** (`backgrounds/fantasy/country/<element>/`, five per element, tagged establishing, road, settlement, weather and night) and **33 class haunts** (`backgrounds/fantasy/haunts/<class>/`, three per class, eleven classes).
- **A realm series for the sisters** (`5_Scenes/realm/`): Homeland, Wayfarer, Settlement, Weather and Nightfall in her own country, plus her class's Haunt, 60 cards; her Craft scene now also uses her class's haunt and her element's realm. All have prompts, Qwen and FireRed workflows, deployed to Drakn Sisters and Drakness.
- **The angels can opt in** to the same series (`scaffold_angel_set.py --realm`, 110 cards); not run yet, to keep Angel Primes quiet while you test.

**Marketing series, still to decide:** the series scenes are the same pose and template for everyone but each hero stands in her own element realm, so a composite needs either the Lineup (flat backdrop) or a shared backdrop per series scene. A "series cut-out" variant of The Dawn, The Bond, Robe and Casting on one common backdrop would make them composable like the Lineup; say if you want it.

**Still open (needs your thinking):**
- **More character scenes.** Each hero could have more: a scene per sister's lore, the pair (an angel with her paired angel), the pet's own scene, seasonal portraits at home, travel and adventure, sports and action, night city.
- **More realms.** Noir city, historic, desert and storm, and a place for each of the sisters' pets and dragons' lairs in the same realistic style; each with backgrounds, effects and wording of its own.
- **More themes.** Valentine, lunar new year, slavic winter, fey court, gaslamp, circus, jungle explorer; the audit does not cover themes yet, and theme makeup, jewelry and robes could extend the new library pieces.
- **Moving over.** The sisters' pieces and the older bundles can be rebuilt on the atomic pieces whenever you want; that changes their prompts, so it is a choice.

## Next work

The MVP data track (G1 Darkness and Light set, D3 starter decks, D2 rule reconciliation, G2 the next cycle), steps 3 and 4 of the Oct 8 steps and the art and video track are in [plans/2026-10-12-roadmap-and-mvp-data.md](plans/2026-10-12-roadmap-and-mvp-data.md), and so in [todo.md](todo.md).

## Data debt

- `data/decks/starter/starter-decks.json` has 26 card ids that do not exist and is built on the retired Fire/Water/Earth
  trio (old heroes Aria, Thalor, Gaia).
- `mythic-pack` and `monthly-reward-pack` reference nonexistent `HERO_MALAKAR_DEMON_OVERLORD`; packs name seven `cardPool`
  ids defined nowhere.
- `data/manifests/series-manifest.json` still describes the old elements and factions;
  `sovereign-dawn-card-list-mvp.json` says `cardCount: 131` but lists 135 ids.
- None of the 30 vision cards is in a deck, box, or MVP list (only the marquee list and collection checklist).
- `card-schema.json` was retired Oct 2026; `data/schemas/codex-schema.json` is the card schema.

### Generator and automation debt (hidden wording and defaults)

Fixed Oct 2026: the hero prompt wording that lived in `gen_prompt.py` (keep line, bust key, figure negatives, makeup and grooming lines, default breeze,
hairFrom text, "slim waist" and "slim, tapering thighs", card-art grandeur) is now in `data/art/_settings/phrases.json`. Still open:

- `SLOT_DEFAULTS` in `gen_prompt.py` (default expression, underlayer, footwear, sheen, background, framing by stage and sex) is code, not data; move it to a settings file.
- `TEMPLATE_KEY_DEFAULTS` (which details each template calls out up front) and the `FIGURE_FIELDS_*` order are code constants.
- `tokens_for_brand` hard-codes "a woman in ..." for the lineup; `tokens_for_cardart` and the card-art `SIZE` in `scaffold_card_art.py` hold wording and size in code.
- `comfy_workflows.py` `engine_prompt()` rewrites FireRed prompts (environment-first, magic `fx` line) outside the prompt files; its text is in `workspaces.json` but the rewrite is invisible in `prompts/`.
- Defaults derived in code rather than stated: nail colour ("Light <last word of primary>"), eyeshadow, magic and gem colours from the first accent when a hero omits them.
- The three templates still hold some fixed prose by design (studio lines, negatives); a template change is a deliberate edit, not hidden.
- The older studio and glamour expression pieces, and `motion/*` default expressions, still carry closed-mouth or sultry wording; only the A-pose and head defaults were changed.

### Schemas still to write

The validator's coverage report lists data with no fitting schema: packs (16 files, `pack-schema` matches none), boxes (3),
rewards (1), starter decks (1), manifests (4), collection checklist (1), card element-lists (7). For each, decide
whether to rewrite the schema to the data or the data to the schema; do it alongside D3.
Another ~30 schemas in `data/schemas/` (map, player, alliance, store, ...) have no data yet and are not needed
before the systems they describe; `docs/specs/*.md` holds their narrative notes.

## Deferred

- **Several input images per workflow (Oct 9).** The Qwen and FireRed templates accept three images, but the generated workflows wire one. Rendering weapons, backgrounds and wardrobe as separate images is a next phase of artwork, only if scenes as they are made today do not work; see Phase 3.8 of `plans/2026-10-09-finals-and-mvp.md`.
- **Asset delivery (C1).** The chain now reaches a ready ComfyUI workflow; it stops at the rendered image. Needs: where rendered PNGs live and how they are named,
  how the card's `portraitAsset`/`fullArtAsset` and each variant's `fullArtAsset`/`videoAsset` fields point at them, how Unity loads them (provisional
  card-art target 512x768, 2:3), and a validator check that referenced files exist. Running workflows through the ComfyUI API is
  still an option, see [art/comfyui-automation-proposal.md](art/comfyui-automation-proposal.md).
- **Animated card art:** static, animated (looping PNG or WebP) and video trailers are separate outputs; animated art plans are to be
  revisited. Videos are for reels, not the card.
- **Game animation in Unity (Oct 9).** Animated cards and in-game cut-scenes are a different approach from the Facebook-reel clips: PNG (frame) sequences that Unity plays, so each animation needs its own frame workflow and Unity import. Down the road, after the reel videos and the art phases; see Phase 8.7 of `plans/2026-10-09-finals-and-mvp.md`.
- **Foil shader (C2).** Variants are modelled (see Decisions); still open: the in-client holo/foil shader and its mask, finish drop rates
  (with O3), and a reserved tier above Holo.
- **Beyond-card art:** frames, icons, map tiles, battle UI, menus. Rendering quality is checked by hand with
  [art/output-qa-checklist.md](art/output-qa-checklist.md); the generator cannot judge images.
- **Thorne Art Studio:** a Windows tool for editing art JSON, previewing prompts and driving ComfyUI; assessed in
  [art/thorne-art-studio-proposal.md](art/thorne-art-studio-proposal.md). Build the command-line pieces first.
- **Art packs and dynamic ComfyUI prompts (Oct 2026):** zip packs of art JSON and custom nodes that assemble a prompt from a template plus
  chosen pieces at run time, both on one shared prompt library; proposal in
  [art/art-packs-and-comfy-node-proposal.md](art/art-packs-and-comfy-node-proposal.md). Recommended before the Studio app.
- Unity project scaffolding; mining signature pieces back into shared wardrobe/background components.

## Readiness gates

Do not say "MVP ready for Unity" until all pass:

- [ ] MVP, combat, deck, tutorial, and hub docs agree on the baseline.
- [ ] Data contracts in `data/schemas/` are mapped to the selected MVP subset.
- [ ] Starter deck, card inventory, encounters, and rewards validate against real files (blocked by Data debt).
- [ ] A small playtestable vertical slice exists with measurable acceptance checks.
- [ ] Phase 1.1+ work is kept separate from MVP work.

Optional later gates, not MVP: fusion, persistent HP/Mana recovery, equipment, crafting, PvP, complex stores, map
exploration, economy deployment, backend services.

## Documentation rule

One home per fact. Superseded docs are moved (`git mv`) into an `_archive` folder, never kept beside the current
version; `_archive` content is a recycle bin that is ignored as documentation and purged later (see
[README.md](README.md#the-_archive-convention)).
