# 2026-10-25: gallery-driven reference rendering

**Status:** active (Oct 25 overnight sandbox integration and bounded local rendering authorized; visual acceptance and production rollout remain gated)

## Oct 26 guiding principle: image-first staged progression

The user confirms the target end state is an image-first, gallery-driven flow:
ingest -> automatic intake/likeness -> review -> explicit stage selection ->
progressive generation through later stages -> selective return to Gallery with
traceable lineage. This is now the guiding principle for rendering, staging and
Gallery routing decisions across plans.

| Required behavior | Direction |
| --- | --- |
| Any eligible gallery image can be a stage input | A stage may start from original, prepared, selected-edit or selected-alpha evidence depending on recipe compatibility; never force a single chain when the user wants to branch |
| Explicit human selection between stages | Results stay in generation evidence until selected; selected outputs become eligible upstream/downstream sources with provenance checks, never implicit "newest file" promotion |
| Stage progression visibility | UI and CLI must expose stage-compatible recipes and prior-stage candidates so the user can choose what to advance into `1_Alpha`, `2_Studies`, `3_Layers`, `4_Wardrobes` and `5_Scene` |
| Structured return to Gallery | Promoted outputs return to a deterministic directory structure derived from source, stage and recipe lineage; originals/core identity evidence remain separate from synthetic derivatives |
| Fast incremental delivery | Keep this as a sequence of small, testable increments; do not block all progress on one large migration |

## Oct 25, 22:28: overnight integration authorization

The user authorizes a full **sandbox** all-image preparation/rebase and a small
real ComfyUI integration pilot, with documented implementation decisions.
This supersedes earlier permission gates for sandbox execution and selected
local pilot renders, not safeguards protecting originals, cast anchors,
manual decisions or unrelated server jobs. Production cutover remains separate.

| Request | Decision / owner |
| --- | --- |
| Prepare 100% of sandbox inputs, including new Various | Rebase C2/C4/C6; preserve immutable sources, current-curation overlay, recovery and explicit held/error counts. Retain assigned cast; do not invent an optional cast-release threshold |
| Family and three-name continuity | Existing name/family/protection policy and stable-ID migration; preserve original/current/character names, report any hold rather than dropping decisions |
| Prove manual edits before full JSON migration | Bounded supported `0c`/`0d`/`0e`/`0f` catalogue and API binding where safe; inspect actual graphs, preserve source snapshots/hashes, do not claim formal stage migration is complete |
| Correct inherited Angelica/output prefixes | Job-owned prefixes derive from displayed subject name plus short batch/job/stage IDs, never a shared Angelica prefix. Preserve manual masters; any intentional manual-prefix patch requires backup and exact inventory |
| Samples, not an automatic whole-library render | Default 2-4 selected images/jobs for proof, sequential queue submission; larger 8/16 batches explicit. Default waits for idle; explicit `--allow-busy-queue` appends one owned job at normal tail, then waits for it. No automatic hundreds-image queue, priority jump or global interrupt |
| Browse all generated outputs; keep only selections | Results remain in ComfyUI outputs, with local receipt/metadata and read-only browser links. Explicit promotion copies selected verified bytes into a separate synthetic-results area, never Gallery originals or identity-core evidence |
| Usable Gallery batching | Stage -> recipe -> selected sources/variants -> seed/sample count; export the same CLI request. Results connect to source/run and can be selected for retention |
| Any useful intermediate may feed later stages | An explicit selected pose/motion/edit result can feed a compatible scene/wardrobe recipe; no compulsory A-pose chain or implicit newest-file choice |
| Benches | Keep as optional diagnostics until recipe inventory establishes their capabilities. Group by purpose in the catalogue; do not bulk move or rename stages overnight |

### Overnight acceptance evidence

- [ ] **P1 ai** R11 Execute the recoverable all-input sandbox run and record
  preparation/matching/install totals, preserved cast/curation, holds, recovery
  and Gallery entry links in the rebase owner.
- [x] **P1 ai** R12 Bind supported manual graphs, durable scoped execution and
  display-name output prefixes; test failures/retries before a 2-4 result pilot.
  Completed the four-job pilot sequentially; each job produced one output in
  its namespaced ComfyUI output folder. User visual acceptance remains R6.
- [x] **P1 ai** R13 Provide stage-grouped request/result browsing and explicit
  synthetic-result retention, keeping unselected outputs server-side.
- [x] **P1 ai** R14 Publish a morning handoff with actual tested outputs,
  limitations, review links, decisions and remaining work; visual acceptance
  remains the user's decision. See the Oct 26 1004 recap and the completed
  pilot receipt/output paths below.
- [ ] **P2 ai** R15 Make isolated mutation validation and short Windows test
  paths an explicit supported validation mode, reusing the existing launcher.
  It must never mutate schemas being read by an active preparation job or
  require manually copying the repository for each check.
- [ ] **P1 ai** R16 Define and implement the first publishable stage-chain
  contract (`0_Edit` -> `1_Alpha` -> `2_Studies` -> `3_Layers` ->
  `4_Wardrobes` -> `5_Scene`) with explicit allowed source kinds per stage,
  stage-to-stage selection rules and deterministic promoted-output paths.
  Start with Sovereign Females and expand by validated recipe inventory.

### Implemented integration evidence

- Request/graph/execution/Gallery/Photo Review regression set: **89 passed**.
  Graph adapters support only the inspected single-level Qwen shape, flatten
  24 reachable API nodes, validate live loader/model capabilities and reject
  unknown topology/classes/bypass rather than guessing a universal conversion.
- Four jobs from two frozen 944x1104 sandbox sources were compiled/staged under
  `overnight-edit-proof-02`, with editable installed copies in `Reference`.
  All four completed and returned one verified output each after sequential
  append-one queueing. The refreshed receipt records the prompt IDs, input and
  output hashes and namespaced paths. Completion is based on server history and
  verified output files, not compilation or submission alone.
- Manual prompts contain conflicting appearance/body directions, so the pilot
  overlays explicit clothed identity/color/clothing-preserving prompts instead
  of falsely labelling the original text reference-faithful. `0d` variants and
  Alpha remain disabled. Permanent prompt acceptance/migration is separate.
- Corrected SaveImage prefixes only in **114 installed manual workflow files**,
  with exact originals/manifest in library `_generation/workspace-backups`.
  Verified all 114 original hashes and zero non-prefix differences; repeated
  preview proposes zero changes. No source prompt/template or other workspace
  was rewritten.
- Static Rendering page has source/stage/recipe selection, distinct sample
  seeds, a 16-job cap, scoped results and explicit retention-manifest export.
  Browser proof used harmless synthetic fixtures: one source -> two jobs,
  thumbnails loaded, unsupported Alpha disabled, 32-job selection blocked.
  Browser trust restrictions prevented opening the B: page inside the editor;
  this is not a claim of real-output visual acceptance.
- A completed synthetic receipt was also checked in the browser: source/output
  images loaded and selecting its result exported the exact batch/job/output
  SHA-256 manifest. No download, real-image retention or server execution was
  triggered by that browser test. Photo Review deep links now use the existing
  reports prefix, with a regression for custom/nested report destinations.
- Retained outputs require matching synthetic sidecars and can feed compatible
  pilot jobs as `selected-render`; tests prove photo guards cannot treat them
  as originals. No real output has been automatically selected or retained.
- Default source discovery explicitly refuses stale Photo Review metadata.
  The interim page uses two explicit pilot sources until the sandbox rebase
  republishes its full reports. No silent missing-source fallback is used.

### Queue/load correction during the overnight run

The first runner waited for unrelated jobs, then exited on a read-only GET
timeout with all four owned receipts still `compiled`, no prompt IDs and no
outputs. A reproduced test now distinguishes retryable GET polling from POST:
GET transport timeouts retry visibly within the existing deadline; HTTP errors,
invalid evidence and uncertain POSTs still hold. A second test proves no POST
occurs if the reads cross the deadline.

The responsive server later reported **1 running / 51 pending unrelated jobs**.
Waiting for global idle could starve a small selected pilot indefinitely.
Under the user's overnight authority, use the new explicit append-one option
for this batch: normal ComfyUI queue position, one owned job outstanding, never
front/priority, cancellation or interruption. Default behavior remains wait-idle.
The old waiting wrapper was stopped, not the server or any queued workflow;
durable receipts are checked before resuming the same batch.
Submission, refresh and reconciliation now share a receipt-writer lock with
PID/operation/time metadata. A deterministic interleaving test reproduced a
stale refresh overwriting a newly accepted prompt; the lock prevents that
rollback and duplicate risk. A leftover lock holds for verified operator
recovery; it is never automatically broken.

Windows permission-error failures during isolated validation exposed raw atomic
replacement in new receipts. Reuse the existing bounded `report_assets` retry
helper instead of adding another retry policy. Tests cover transient recovery,
permanent failure with pending evidence, and failed Gallery publication retaining
the previous whole page. A later isolated preparation failure was traced to an
overlong test TEMP path; validation uses a short dedicated TEMP directory rather
than changing the image pipeline or treating that harness failure as acceptance.

### Oct 26 live pilot completion

The accepted `angelica-cleanup` prompt completed with one output. The remaining
three compiled jobs were then run one at a time at the normal queue tail; no
unrelated jobs were cancelled, interrupted or reprioritized. A read-only status
refresh confirmed all four jobs `completed` with one output each:

| Job | Recipe / variant | Result |
| --- | --- | --- |
| `angelica-cleanup` | `manual-0c-cleanup-basic` / `0c_Cleanup` | GMW mark removed; source framing, clothing and background remain broadly consistent, with generative facial/detail variation |
| `angelica-enhance` | `manual-0e-enhance` / `0e_Enhance` | One output; compare against source for edge seams and subtle appearance drift |
| `draknava-cleanup` | `manual-0c-cleanup` / `0c_Cleanup` | Signature mark removed; pose and clothing remain broadly consistent |
| `draknava-full` | `manual-0f-full` / `0f_Full` | Full figure extended from the partial-body input, but pose and outfit changed; do not treat it as source-preserving |

The output PNGs remain in ComfyUI's `Sovereign Females` output tree. None was
promoted to Gallery or retained as identity/core evidence. The visual notes are
screening observations, not user approval: review face, proportions, clothing,
background seams and whether each variant is useful before retaining anything.
The batch receipt and exact output hashes remain under the sandbox's
`_generation/reference/overnight-edit-proof-02/`.

## Oct 26: cleanup batches, multi-select, output browsing and pull-back

The user confirmed a live cleanup render, gave the server queue capacity
(**200 jobs**) and asked for optional ComfyUI cleanup of intake images that
crop/LaMa could not finish, multi-select batching, browsing all ComfyUI
outputs, full-size viewing, normalized pull-back and, later, launching the CLI
from a button. Decisions taken under the standing authority (rationale inline):

| ID | Decision | Rationale |
| --- | --- | --- |
| C1 | Cleanup candidates come from the intake evidence already published with Photo Review: `sourceTreatment` `*-overlay-unremoved` = **needs cleanup**; LaMa `eraser` selection = **repainted, review**; `original-enhancement-failed` = **enhancement failed** | No new scan or guess; the preparation pipeline already records what it could not remove and says "left for ComfyUI" |
| C2 | The Rendering page filters by those hints, selects all visible, and builds jobs as sources x recipes x samples | Google-Drive-style multi-select over a filtered set; several workflows per batch instead of one |
| C3 | `render-reference.cmd cleanup-batch` writes a **proposal** request for every candidate (default `manual-0c-cleanup-basic`, 2 samples) under `_generation/proposals/`; preview by default, nothing queued | Keeps the optional "advanced cleanup" a reviewed choice; the same JSON runs through the normal prepare/compile/run |
| C4 | Queue capacity 200 is a hard guard: submission refuses when running+pending would exceed it. `run --queue-depth N` (1-16) keeps up to N owned jobs queued at the normal tail; default stays one. Batch/run job cap rises from 16 to 64 | Lets a reviewed batch fill the queue without starving it or overflowing; still never cancels, interrupts or reprioritizes |
| C5 | `render-reference.cmd outputs` publishes `_generation/outputs.html`: every PNG in the configured ComfyUI output roots, filterable by workspace, stage, workflow variant and subject name, paginated, full-size lightbox (original file scaled by the browser, no thumbnails), multi-select and pull-back manifest export | Browse ALL renders, including manual ones, without copying anything |
| C6 | `render-reference.cmd pull MANIFEST` copies selected outputs into `_generation/library/<stage>/<variant>/` as `<name>_comfy_<variant>_<hash8>.png` plus a cream-padded `..._944x1104.png` and a JSON sidecar (source output, SHA-256, ComfyUI PNG metadata, receipt lineage, personId/photo where known, `synthetic: true`) | Same `<name>_<type>_<id>` shape as `_image_`/`_shot_`/`_pic_`, with `comfy` and the variant showing it is a render. Outside person folders because clean rebases rebuild category folders and identity merges relocate unknown subfolders; never scanned by likeness/intake |
| C7 | Pulled renders appear as selectable sources of their own kind, `pulled-render` (sidecar-checked like `selected-render`), and will be listed per person by `personId`, not by folder | Gallery integration by stable ID; the storage location stays rebase-safe; a separate kind keeps "retained from a receipt" and "pulled from any output" distinguishable |
| C8 | Automatic "best of N" is a **ranking suggestion** first (face similarity to the source); automatic pull-back only with an explicit flag after the ranking is validated | Generative output can lose identity; a score is evidence, not approval |
| C9 | Button-launched CLI uses a later loopback-only local service with a per-session token that runs only the whitelisted `render-reference` subcommands on files under the library | A static `file://` page cannot start processes; the CLI stays the single execution path for any GUI |

- [x] **P1 ai** R17 Cleanup-candidate metadata, filters, select-all and
  multi-recipe batches on the Rendering page; `cleanup-batch` proposal command.
- [x] **P1 ai** R18 Queue capacity guard (200) and `--queue-depth`; 64-job cap.
- [x] **P1 ai** R19 Output browser over all ComfyUI output roots with filters,
  pagination, full-size view and pull-back manifest export.
- [x] **P1 ai** R20 `pull` command: verified copy, standard naming, 944x1104
  padded copy and lineage sidecar; pulled renders selectable as sources.
- [ ] **P1 you** R21 Try the flow on real images: filter "Needs cleanup",
  select some, export, run, browse outputs, pull one back; report naming or
  folder changes you want.
- [ ] **P2 ai** R22 Face-similarity ranking of each job's outputs against its
  source (suggest best of N); auto-pull stays opt-in.
- [ ] **P2 ai** R23 Loopback local service so Gallery buttons run the
  whitelisted CLI steps (prepare/compile/run/status/pull) and refresh pages.
- [ ] **P2 ai** R24 Show pulled renders in the People drill-down per person and
  in intake run views.

### Oct 26 implementation evidence (R17-R20)

- Code: `tools/workflows/reference_outputs.py` (new: scan, parse, outputs page,
  pull), `reference_execution.py` (`CLEANUP_HINTS`, `cleanup_hint`,
  `cleanup_batch`, capacity guard, `_run_pipelined`), `reference_gallery.py`
  (hint badges and filter, stage filter, multi-recipe checkboxes, select
  visible, 64-job cap), `reference_rendering.py` (CLI `cleanup-batch`,
  `outputs`, `pull`, `--queue-depth`, `pulled-render` source checks), schema
  `kind` enum and `maxItems` 64, masthead **Outputs** (Gallery UI
  v2026.10.26.1), menu **O**.
- Tests: new `test_reference_outputs.py`; new execution tests for capacity,
  owned-prompt busy checks, pipelined depth, held states, hint mapping and
  chunked proposals; CLI flag scoping; all registered in `test.cmd`,
  `check.cmd`, `validate.cmd`.
- Live sandbox: `outputs --apply` scanned 6,758 images (Angel Primes 2,786,
  Sovereign Females 140, Sovereign Territories 3,832) in about 19 s into a
  2.9 MB page. Legacy `drakn-sisters/NAME/poses` folders are parsed as subject
  and workflow.
- Found while testing: every sandbox Review item was `unverified`, so no
  cleanup hint could be shown, because one empty aborted run folder
  (`_reports/preparation/visual-uat-20261023-v9`, no files) raised "no
  manifest" for the whole index. The index now records a completely empty run
  folder as "empty folder; ignored". A folder with any file and no manifest
  still makes everything unverified (test added).
- Page behaviour (jsdom drive of the live sandbox page, since the integrated
  browser refuses `file://` on B:): 6,774 outputs, 57 pages; the Sovereign
  Females filter showed 156, and the text `0c_` filter showed 2; select-visible
  enabled the export; the viewer opened, arrow keys stepped and Esc closed it;
  the exported manifest carried output, size, mtime, the name override and
  `outputRoot`.
- Live pull: the Draknava `0c_Cleanup` pilot output previewed, then was applied
  to `_generation/library/0_Edit/0c_Cleanup/draknava_comfy_0c_cleanup_1e81dacd.png`
  with a 944x1104 copy and a sidecar. A repeated pull reported `already-pulled`.
  The republished Rendering page lists it as a `pulled-render` source.

## Oct 26 afternoon: large unattended cleanup and pose run

Asked: run everything that still needs cleanup after intake through ComfyUI
(up to the 200-job queue), add `0d` poses for each cleanup image and several
`0b`/`0c` runs, 1-2 samples each, automate the cleanup, document it.

Finding the cleanup set. Published cleanup hints were empty (preparation
evidence is unverified until R11), and a rescan of the 2,420 Gallery copies
found 0 overlays, because legacy preparation had already cropped or repainted
them. A spot check showed that leftover phone-UI pieces (inset thumbnails,
icons, black bars) were still visible. So intake's overlay heuristic was rerun over
the raw intake mirror of the overnight run (read-only):

| Step | Count |
| --- | --- |
| Raw intake images scanned | 2,741 (82 s) |
| Overlay detected | 107 |
| Mapped to a current Gallery source by photo key | 74 (37 people: Potentials 28, Prospects 23, Angels 10, Models 7, Sisters 6) |
| Unmapped | 33: 23 `Various\gallery` screenshots not yet in Photo Review, 10 `Artists\Fantasy` |

Decisions (made unattended, reversible, for review):

- `0d_Deluxe` installed graphs are all "Bare" variants. The recipe
  `manual-0d-deluxe-pose` reuses only the graph and settings (full denoise);
  its prompt is replaced by a clothed re-pose prompt ("same outfit, fully
  clothed"). Unclothed renders of real people from intake photos are never
  produced.
- `manual-0b-background-basic` binds `0b_Background_Basic` with a plain
  light-grey backdrop prompt.
- `0c Cleanup Basic` is the automated cleanup: its outputs are the ones
  pulled back automatically (see results). `0d`, `0b` and full `0c` are left
  for the user to choose on the Outputs page.

Batches (all via `bin\render-reference.cmd`, one sample each):

| Proposal | Sources x recipes | Jobs | Batches |
| --- | --- | --- | --- |
| `cleanup-0c0d-20261026` | 74 x [`0c-cleanup-basic`, `0d-deluxe-pose`] | 148 | -01 (64), -02 (64), -03 (20) |
| `cleanup-0b0c-20261026` | 21 (first source per person) x [`0b-background-basic`, `0c-cleanup`] | 42 | -01 |

- [x] **P1 ai** R25 `overlay-scan` command and `cleanup-batch --sources/--id`
  (tests: source list replaces hints and refuses stale paths; scan maps by
  photo key and writes only with `--apply`; every bound recipe has a clothed
  prompt; CLI flag scoping).
- [x] **P1 ai** R26 Bind `0b Background Basic` and `0d Deluxe Pose (clothed)`.
- [ ] **P1 you** R27 Review the large run on the Outputs page (filter batch
  `cleanup-0c0d-20261026` / `cleanup-0b0c-20261026`): judge the auto-pulled
  `0c` cleanups, pick any `0d` poses or `0b`/`0c` results worth pulling, and
  accept or change the clothed-only `0d` rule.
- [ ] **P2 either** R28 Take the 23 unmapped `Various\gallery` screenshots
  through intake into Photo Review, then rerun `overlay-scan`.
- [ ] **P2 you** R29 Choose the standard studio backdrop for the preparation
  stages (`0_Edit`, `1_Alpha`, `2_Studies`, `3_Layers`).
  - The `0b`/`0d` prompts ask for light grey, and the renders measure about
    RGB 172-202 (`#BEBEBE`). The current default, `studio/cream-even`, is
    cream, and so is the intake padding (`originals.CREAM` 245,240,230).
  - Recommended: neutral light grey for every preparation stage. It casts no
    colour onto skin or hair, separates blonde hair and cream, white or black
    outfits, leaves no warm halo when composited into scenes, and is the
    studio convention for reference shots. Cream and the other backdrops stay
    as deliberate `4_Wardrobe` showcase choices.
  - Option: A/B the same sources on grey and on cream first.
  - The intake padding of real photos is a separate choice (keep cream,
    switch to the same grey, or try blurred edge extension) because changing
    it regenerates every 944x1104 derivative. Not changed yet.

### Large run results

| Batch | Completed | Notes |
| --- | --- | --- |
| `cleanup-0c0d-20261026-01` | 64/64 | 11:46-14:18 |
| `cleanup-0c0d-20261026-02` | 64/64 | 14:18-16:42 |
| `cleanup-0c0d-20261026-03` | 20/20 | 16:42-17:26 |
| `cleanup-0b0c-20261026-01` | 42/42 | 17:26-19:02 |

- 190/190 jobs completed, one output each, with no held or failed jobs, in
  7 h 16 min: about 2.3 min per job at queue depth 16. The runner's two-hour
  timeout was reached twice; the driver resumed from the receipts without
  resubmitting.
- Automated cleanup: all 74 `0c Cleanup Basic` outputs were pulled back in
  two manifests (64 + 10) to `_generation/library/0_Edit/0c_Cleanup/`, each
  with a 944x1104 copy and a sidecar. The dry-run preview was all
  `pull-preview`, and the apply was all `pulled`. The other 116 outputs stay
  in ComfyUI for the user to choose.
- Outputs page republished: 6,964 images. The Rendering page refused to
  republish because Photo Review is stale: it lists a source that no longer
  exists (`Various/review/afton_north_image_7518027271200184433.jpg`). The
  pulled renders appear there after Photo Review is republished.
- Quality from contact sheets (not user acceptance):
  - `0c Cleanup Basic` keeps the framing, outfit and face and removes
    overlays. A soft-focus face can come back sharper.
  - `0d` gives a clean full-length grey-studio pose in the same outfit,
    barefoot, fully clothed: a good prepared input for `1_Alpha`.
  - `0b` swaps in a grey backdrop and removes inset thumbnails and black
    bars. It usually keeps the pose but sometimes extends the framing to full
    length.
  - Full `0c` also produces a grey backdrop and can re-frame: a cut-off face
    was re-centred (invented), and one person's hair shifted toward
    blue-black. Treat both as synthetic.
- [ ] **P2 either** R30 Republish Photo Review in the sandbox (the stale
  `afton_north` source), then republish the Rendering page so that the 74
  pulled cleanups are listed as `pulled-render` sources.

## Outcome

Select a source in Intake, People, Review or scoped Artist browsing, choose a
compatible female recipe and appearance profile, export a batch, then run it
through one CLI into a dedicated ComfyUI workspace. Return exact inputs,
settings and results to the same gallery journey. No cast slot or permanent
per-person workflow collection is required.

**Oct 25 clarification: four parallel tracks.** Intake/likeness, dynamic
ComfyUI execution, shared data-driven stage/template migration, and Gallery GUI
integration each have their existing owner. Installed `zz_shots/0_Edit` and
`zz_shots/1_Alpha` are experimental sources, not the permanent execution model.
Manual graph binding is a temporary transport proof with source hashes; accepted
recipes must return to normal templates/components/assembly JSON after tag,
sequence and preservation rationalization. `1_Prime`/`2_Bare` restructuring
and lessons for Studies/later templates remain manual migration P1-P9, not
silently replaced by the runner.

This is the focused successor to generation exploration A8 in the
[manual-action plan](2026-10-22-review-actions.md#oct-25-1734-gallery-driven-generation-exploration-a8).
That discussion and its raw words stay intact as rationale. This plan owns
render requests, workspace isolation, input staging, execution receipts and
generation results. It does not take over intake acceptance, identity matching,
all manual actions or the whole art-authoring UI.

## Decisions and remaining approval boundaries

The user chose Sovereign Females and authorized the offline foundation on
Oct 25, then authorized the bounded overnight pilot. That pilot implements
reference-faithful clothed edit modes only; broader recipe/profile acceptance
and permanent template migration are not implied.

| ID | Recommendation | Boundary |
| --- | --- | --- |
| D1 | Workspace **Sovereign Females**; male/animal names remain undecided | User-selected Oct 25, superseding proposed Reference Female/Reference Lab. The user clones Angel Primes, retargets input/output roots and later cleans saved copies; the runner must not clean the clone |
| D2 | Keep `Various` as the neutral incoming root for now | Do not rename it Female or create nested category trees before discovery/migration support exists |
| D3 | Preserve reference face, hair color, eye color and skin tone; preserve hairstyle/makeup unless a recipe explicitly declares a change | Preservation is the requested intent, not a guarantee from a generative model; show unavoidable/conflicting behavior before queueing |
| D4 | Offer **Reference faithful** and **Slender / fuller bust** as distinct selectable adult female design profiles | The latter is a non-explicit silhouette/proportion choice for clothed studies, not an identity fact or automatic modification of every photo |
| D5 | JSON batch -> offline CLI -> frozen source evidence -> isolated compile -> explicit bounded run -> scoped results/retention | Static Gallery export/results implemented; direct browser execution remains later |
| D6 | Overnight proof: four clothed edit modes over two selected sources, reference-faithful only | This supersedes the initial proposed two-profile A-pose proof for transport testing, not final appearance acceptance; additional profiles/Alpha remain open |
| D7 | Library-local `_generation` holds job evidence; ComfyUI roots hold namespaced staged inputs/render outputs | No originals moved, no outputs inserted into Gallery/core, no automatic candidate/final promotion or cleanup |

## Four coordinated tracks, not one blocking project

| Track | Work possible now | What remains gated |
| --- | --- | --- |
| Intake/likeness | Authorized recoverable sandbox all-input run; user review of retained-detail/identity/protection evidence | Visual calibration and incremental production cutover keep their gates |
| Rendering execution | Isolated graph binding, bounded submission, receipts, explicit retention | Real outputs/appearance must be checked; only the small pilot is authorized |
| Shared templates/JSON | Inventory manual edit/Alpha examples, rationalize sections, sequence and input roles | Formal stage/consumer integration and accepted generated replacements remain migration P1-P9 |
| Gallery GUI | Stage-grouped export, source links and read-only scoped results | Direct browser execution/service and broader workspace recipes remain later |

The rendering proof can use selected known-good existing derivatives without
waiting for a whole-library rebase or directory migration. It must label whether
the source came through accepted preparation, provisional preparation or a
legacy/manual path. Using a provisional source does not accept intake.

## Current machinery to reuse, not bypass

- [Workflow configuration](../../workflows/workspaces.json) owns installed
  workspace paths, engines and existing set homes. Existing defaults are
  hero-scoped; they are not per-person experiment state.
- [Workflow materializer](../../tools/workflows/comfy_workflows.py) already
  handles production prompt patching, master selection and engine differences.
  The pilot's API adapter binds only one inspected frozen manual subgraph shape;
  it is not another production workflow generator or a universal UI converter.
  As shared migration lands, consume its validated exports rather than grow
  this temporary binding into a parallel template system.
- [Prompt generator](../../tools/generators/gen_prompt.py) resolves identities,
  components and design profiles. Add a validated ephemeral reference context,
  not edits to Female's saved identity or shared hero `photos`/`inputs`.
- [Input sync](../../tools/workflows/sync_inputs.py) is legacy basename discovery.
  The new runner stages a verified explicit source; it must not search by
  basename or trust a pre-existing input file merely because the name exists.
- Editable ST masters contain UI graphs/subgraphs. Derive and validate API
  exports for reviewed graph shapes, bound to master/export hashes. Retain
  editable UI job copies for manual inspection; do not submit UI JSON to `/prompt`
  or introduce an untested universal graph converter.
- [Manual prompt migration](2026-10-22-manual-prompts-to-art-library.md) owns
  `0_Edit`, revised Prime/Bare and token semantics. Its source text is not
  automatically accepted as a reusable reference recipe.

## Workspace setup and exact paths

For D1, the user clones the ComfyUI install/workspace **Sovereign Females**.
The proposed local layout follows existing configured roots:

```text
B:\Comfy-Desktop\ComfyUI-Installs\Sovereign Females\ComfyUI\
  user\default\workflows\Reference\<run-short>\<job-short>\1_Alpha\...

B:\Comfy-Desktop\ComfyUI-Inputs\Sovereign Females\
  reference\<run-short>\<job-short>\source.png

B:\Comfy-Desktop\ComfyUI-Outputs\Sovereign Females\
  reference\<run-short>\<job-short>\1_Alpha\<actual-server-output>.png
```

The selected server must actually be configured to use those input/output
roots. A folder named like a workspace does not prove that configuration.
Preflight checks an explicit server profile and verifies the input/output
mapping; it does not guess ports, start another ComfyUI or modify an install.
Use the same relative input namespace when upload is used instead of local copy.
Server-relative paths use ComfyUI's separator convention, not Windows drive paths.

Do not grant the workspace `accepts: ["*"]` or repoint Female's globals.
The user is copying Angel Primes, including saved workflows and `zz_shots`;
preserve them all. Retire generic Female from Angel Primes only after the
replacement is accepted, as a separate reviewed change.
Register the reference target with explicit ownership.
Generic `setup`, deploy, pull, tidy and cleanup must either understand that
ownership or visibly refuse to manage job-owned paths; a new workspace entry
alone would leave existing home/cleanup assumptions incomplete.
User-curated/manual edits are never overwritten by job refresh.

Workspace installation and engine availability remain separate from the
server endpoint, which must be explicitly configured and checked. Start with
one approved local endpoint; remote originals/uploads are a separate permission.

## Appearance contract: preserve identity, choose design

Every recipe exposes its input role and supported preserve/change controls.
Resolve effective settings once into the job before compilation.

| Concern | Reference faithful | Slender / fuller bust |
| --- | --- | --- |
| Face/identity | Preserve reference facial appearance | Same |
| Hair/eye color, skin tone | Preserve; no guessed numerical color from likeness embeddings | Same |
| Hairstyle and makeup | Preserve unless explicitly changed by the chosen recipe | Same, independently selectable |
| Body proportions | Preserve visible reference proportions where possible | Apply reviewed slender-build and fuller-bust components to a clothed silhouette |
| Pose | Recipe may change to A-pose; clearly declared | Same |
| Clothing/background | Recipe-specific explicit choice | Same; no implicit palette/body defaults borrowed from Angelica |
| Unseen features | Unknown/inferred, not claimed recovered | Same; full-body expansion is synthesis, not original-photo restoration |

Use independent `preserve`, `preset` or explicit validated override modes per
supported concern. A user can keep build but change bust, or keep both and
change wardrobe; a combined preset is just a convenience expansion into fields.
Record profile ID/version and resolved components, not only a human label.
Precedence: explicit per-job choices -> selected profile -> recipe defaults;
the compiler must reject mutually contradictory preservation/reset instructions.
Freeze fully resolved choices in the preview so later preset edits cannot
silently alter a reviewed request.

No learned face-analysis field supplies these design attributes. No sex/gender,
age, body shape or identity is inferred as fact from a filename or likeness score.
Use an explicitly selected adult reference profile for these clothed design tests;
unknown/ineligible source-use conditions block that recipe rather than guessing.
Artistic changes never update catalogue identity attributes automatically.

### Adapting the existing female flows

Inventory every current generic Female flow with engine, master, prompt
components, input role, preserve/reset behavior and tested status. Expose them
in a catalogue, including disabled entries with their blocking reason.

- Start with `1_Alpha` A-pose, with the appearance contract above; remove
  conflicting hairstyle/color/reset wording from the ephemeral recipe only.
  Existing cast workflows and manual source text remain unchanged.
- Broaden to studies, wardrobe and scenes with explicit input bindings.
  A compatible direct-image recipe may accept the selected source; a recipe
  requiring a chosen Prime/A-pose must receive that result, not Female's default.
- Add `0_Edit` only through migration P4's schema/layout/role changes. Do not
  relabel the intake crop/LaMa pipeline as `0_Edit`, or run an edit implicitly
  before every render.
  The user's Oct 25, 21:36 suggestion makes Sovereign Females the first formal
  edit proving ground, analogous to the intake sandbox. The
  [manual migration pilot](2026-10-22-manual-prompts-to-art-library.md#oct-25-2136-sovereign-females-as-the-formal-edit-pilot)
  owns selecting/migrating a manual variant and gradual accepted rollout.
  The initial A-pose proof above is not a prerequisite to inventorying edits;
  choose the first executable pilot after the variant/input-role review.
  This runner supplies isolated execution, not a workspace-only stage fork.
- Never promise engine equivalence: FireRed's positive-only behavior and
  face-lock logic require their own reviewed compilation/render proof.
- Chained stages pause for selection. No automatic use of the newest numbered
  file, guessed `_00000` output or another person's successful result.

## Source selection and input staging

Any supported user-selected photo may request a compatible recipe regardless
of cast assignment, catalogue category or face score. "Any" does not include
arbitrary filesystem/network paths, unknown source-use rights or incompatible
subjects. Artist jobs retain their separate provenance; unsupported animal
inputs are not passed to human face gates or female recipes.

1. Resolve an exact library-relative source reference, domain, photo ID where
   available, person ID if assigned, content hash and treatment/retained-set
   evidence. Unassigned images receive a stable source reference, not a fake person.
2. Choose an explicit version and framing. Normal input is the maintained
   944x1104 full/head/chest derivative when valid; retained denoise/tone/raw
   variants require explicit experimental selection and recorded conversion.
   Missing/stale derivatives block that choice; no silent full/head substitution.
3. Preview all source/output paths and check image dimensions/recipe constraints.
   Source prep/derivative creation is a separate supported step, not a hidden crop.
4. Stage to a unique run/job namespace using a temporary file and verified
   publication. Copy exact selected bytes, or record original hash plus the
   explicit deterministic conversion and staged hash when PNG conversion is needed.
5. Rehash before submission. Existing identical owned files may be reused;
   different/unowned bytes refuse. No moves from Gallery/Various, no basename
   search and no overwriting another job's `source.png`.

Once staged, a job may execute its verified frozen snapshot even if the current
library photo is renamed/moved; mark the changed current association explicitly.
If the original changes before staging, require a fresh preview. Frozen job
history does not rewrite itself to follow today's source bytes.

## Batch-first execution interface

Implemented launcher: `bin\render-reference.cmd`, a thin entry to one Python
runner shared by GUI/service callers. Input freezing remains offline; separate
explicit commands compile/stage supported graphs and submit bounded jobs.
Operational examples and the current schema live in the
[workflow runbook](../../workflows/README.md#offline-reference-rendering-foundation).

```bat
rem Offline input evidence.
bin\render-reference.cmd preview "BATCH.json" --root "LIBRARY" --dry-run
bin\render-reference.cmd prepare "BATCH.json" --root "LIBRARY" --apply
bin\render-reference.cmd check "BATCH-ID" --root "LIBRARY" --check
rem Explicit execution after compile and verified workspace mapping.
bin\render-reference.cmd run "BATCH-ID" --root "LIBRARY" --limit 4 --apply
bin\render-reference.cmd status "BATCH-ID" --root "LIBRARY" --refresh
bin\render-gallery.cmd --root "LIBRARY" --apply
```

`preview` is read-only/offline. Current `prepare` validates the entire batch and
writes exact frozen inputs and request/run evidence; it never queues. `compile`
separately validates executable recipe/profile/workspace capabilities and writes
resolved UI/API job graphs. `submit` queues one explicit compiled job;
`run` waits for the existing queue and handles a bounded selection sequentially.
`status` reads local receipts by default; online refresh is explicit.
Refresh verifies scoped history/output bytes but leaves images server-side.
`retain` previews/copies only explicitly selected output hashes into synthetic
storage. `reconcile` can bind one exact uncertain client-intent/history match
without another POST. `check` verifies local evidence offline.
Every mutation previews by default without `--apply`; repeat never silently
queues twice or replaces completed outputs. No shell commands inside manifests.

### Request shape and durable state

The versioned schema will distinguish editable requests from immutable resolved
jobs and mutable execution receipts. Required concepts, not final field names:

| Record | Required information |
| --- | --- |
| Batch request | Schema version, batch ID, library/root binding, target profile, bounded jobs and count; generated by CLI first, browser export later |
| Per-job request | Unique ID, exact source reference/hash, domain and optional person ID, version/framing, recipe/version, appearance choices, engine, concrete seed, sample count and optional explicitly selected parent result |
| Resolved job | Request hash, input hash/dimensions, resolved components/prompts, master/API graph hashes, actual settings/model identifiers, planned relative destinations |
| Receipt | Preparation/submission timestamps, endpoint identity, ComfyUI prompt ID, lifecycle/events/errors, actual returned outputs with hashes, collection state and current-source association |

Resolve random seeds during preparation, not independently on retries. Expand
multiple samples into individually identifiable jobs with concrete seeds.
Use short directory IDs and full evidence in manifests to avoid prior Windows
path-length failures. If a model file hash is unavailable, record that limitation;
same seed/settings alone is not a guarantee of identical future pixels.

Lifecycle: requested -> prepared -> submitting -> queued -> running ->
completed/failed/cancelled, with explicit submission-uncertain and collection-failed
states. A connection timeout after POST does not prove rejection. Persist intent
before POST and prompt ID immediately afterward; reconcile uncertain submissions
with server history/operator review, never automatically retry into a duplicate.
ComfyUI history is not our durable job ledger.

Validate all offline batch entries before staging; stage atomically per job.
Network submission of a batch is not an all-or-nothing transaction: retain
receipts for accepted jobs and visibly hold unsubmitted/failed entries.
Start with one outstanding submitted job at a time; larger counts require an
explicit reviewed limit. Cancellation may remove our pending jobs, but must not
globally interrupt an unrelated manually running workflow.

## Generation storage and Gallery experience

Implemented durable root: `<selected-library>\_generation\reference\<run-short>\`.

```text
request.json                   frozen source request
run.json                       versioned frozen input evidence
compiled.json                  immutable graph/staging evidence
execution.json                 mutable scoped prompt/output/error receipt
jobs\<job-short>\
  input\source.png             verified frozen workflow input
  manual-source.json           exact inspected manual source snapshot
  workflow-ui.json             inspectable job, not a shared master
  workflow-api.json            bound reviewed API representation
```

Full prompt/settings evidence is in the UI/API graphs and compiled manifest.
Outputs stay in the returned server namespace. Only explicit selections copy to
`_generation/selected/BATCH/JOB/file` with a hash-bound synthetic sidecar; these
appear in the selector and can feed another compatible pilot job. They never
become original photos or core observations. Do not prune either location.
Later storage optimization requires an explicit retention/
recovery policy, not a filename rule. Job roots must be outside active photo
buckets and excluded from likeness/intake discovery; tests prove that exclusion.
Backups of generation evidence need an explicit inclusion/budget decision before
large runs. Existing whole-library snapshot behavior is not assumed here.

Gallery selection -> Generate/Test panel -> export JSON -> CLI preview/prepare/
compile/run -> supported read-only result-report refresh is the first GUI loop.
Browser downloads still use the normal download location; do not promise an
automatic arbitrary filesystem save.

The current panel offers compatible stage/recipe choices, reference-faithful
profile, source selection, seeds/sample count and explicit disabled entries.
Additional appearance profiles/overrides are not yet executable.
The results page shows input versus output, recipe/settings, phase, errors and
parent/child links. Search by current person/category or historical display name;
key records by IDs/source hashes, not mutable names.
If identity assignment later changes, historical evidence remains; current
gallery association uses checked lineage, not a basename or family-surname match.

Generated images are separate synthetic assets. They do not become original
photos, identity-core observations, automatic protection support or workflow
defaults. Promote a result only through a separate reviewed action.
Direct Gallery queueing can later call a loopback-only validated service over
the same runner; no browser shell, arbitrary path execution or unrestricted
network server is part of the first milestone.

## Various, subject profiles and future support

Keep `Various\gallery` and `Various\<Name>\gallery` working unchanged.
Do not add `Various\Female\...` now: current discovery can treat a child name
as a supplied person and accidentally seed an identity called Female.
The workspace's selected rendering profile is not a filesystem sex classifier.

Long-term concerns are independent:

| Concern | Example | Where it belongs |
| --- | --- | --- |
| Processing state | Incoming, accepted, Review, Junk | Intake lifecycle |
| Identity category/role | Model, Prospect, Potential, cast slot | Existing catalogue, not a generation workspace |
| Subject kind | Human, animal, creature, unknown | Explicit metadata and compatible processing profile |
| Rendering design profile | Adult female, adult male, species-specific recipe | Explicit per-job recipe selection, not inferred gender/identity truth |
| Provenance domain | General photographs, a specific Artist | Retained source/matching permissions |

Future neutral intake naming and People/Animals roots stay intake I26.
Introduce and validate metadata/discovery before any physical migration.
Human face matching and current no-human-face Junk rules are not animal identity
support. Animal intake needs a separate guarded route before such sources can
enter routine auto-Junk/crop/matching; no female body recipe or forced human
identity should run on them. Reserve workspace naming, not a false promise that
current YuNet/SFace or v16 person masks support all species.

## Milestones and acceptance

The offline input-request slice is active. Remaining milestones retain their
explicit gates. Real deployment/rendering requires its specific reviewed batch;
foundation approval does not authorize a whole-library run.

- [x] **P1 you** R0 Choose the first workspace: Sovereign Females, cloned by the user.
- [x] **P1 ai** R0a Deliver offline input-request schema/preview/prepare/check,
  launcher/help/menu and isolation tests. Freeze exact selected bytes under the
  library's `_generation`; no install/workspace/shared-default writes or network.
  Reference and explicit character modes are recorded, not compiled.
- [x] **P1 you** R1a Create/start Sovereign Females and clean unwanted cloned
  workflows. User reports remaining Alpha and manual `zz_shots` (still referencing
  Angelica); preserve both. New generated experiments belong under `Reference`.
- [x] **P1 ai** R1b Implement read-only server probe and verify communications.
  Live endpoint `http://127.0.0.1:8188` came from the clone's current log.
  GET system stats/object info returned ComfyUI 0.38.2, 970 node types, basic
  LoadImage/SaveImage/UNETLoader/CLIPLoader/VAELoader and Qwen/FireRed model choices.
  This does not prove a recipe is executable or the workspace roots round-trip.
- [x] **P1 ai** R1 Resolve the pilot input mapping before deployment: runtime argv
  uses `B:\Comfy-Desktop\ComfyUI-Inputs\Sovereigh Females` (existing), while
  `...\Sovereign Females` is missing. Output maps to the correctly spelled
  Sovereign Females directory. Under overnight authority the pilot explicitly
  binds the actual misspelled root, recording it in compile/execution evidence;
  no rename, settings edit or server restart. Later Male/Animals names are undecided.
- [ ] **P2 either** R1c Correct the workspace input-directory spelling during a
  deliberately stopped maintenance window, then re-probe/rebind future jobs.
  Preserve the pilot's historical mapping and staged input evidence.
- [ ] **P1 ai** R2 Define request/resolved/receipt schemas, recipe capabilities,
  appearance modes, root/domain binding and lifecycle; add validator tests before
  runtime. Request schema, frozen/compiled evidence checks, capability validation
  and execution receipts are implemented/tested for the pilot. Broader recipe
  appearance modes and permanent resolved/receipt schema contracts remain open.
  Preserve old defaults and stable source/identity semantics.
- [ ] **P1 either** R3 Review the two proposed clothed A-pose profiles and
  their preserve/reset behavior from actual resolved prompts; approve the first
  recipe and sample sources. Manual migration owns shared template/token changes.
- [ ] **P1 ai** R4 Implement offline preview/prepare/check and the thin launcher
  for render-ready jobs after R2/R3; R0a is the input-only subset. Clone job-owned
  UI workflows and explicitly stage workspace inputs. Register
  workspace job ownership and guard generic cleanup/pull/reset/deploy behavior.
  Prove no writes to existing cast/Female/Male configuration or source trees.
  Pilot graph/staging and isolation tests are delivered. The workspace remains
  intentionally outside the legacy hero-home registry: generic explicit
  maintenance refuses it as unknown, default maintenance cannot select it.
  Formal ownership registration/maintenance integration remains open here.
- [ ] **P1 ai** R5 Bind one reviewed Qwen API graph to its master, preflight
  endpoint/model/node capabilities, then implement explicit submit/status/collect
  and durable uncertain-submission recovery. Depend on R4 and verified R1 mapping;
  start with mocked transport and one explicitly approved real job. Binding,
  failure/uncertain/reconcile tests, scoped status/retention and four completed
  live outputs are implemented; user visual acceptance remains R6.
- [ ] **P1 you** R6 Accept the bounded transport pilot: two selected sources,
  four clothed edit jobs, controlled recorded seeds/settings and no cross-job
  input/result mixup. Inspect face/hair/eye/skin preservation, framing and
  hands/feet. The proposed second appearance profile still needs R3/R2 before
  a separate body-design comparison; this faithful-only pilot cannot prove it.
  A passed API transaction is not visual acceptance.
- [ ] **P2 ai** R7 Add compatible female flow catalogue coverage and explicit
  selected-result continuation after the pilot; inventory every unsupported
  entry with a reason. Four pilot modes and hash/provenance-verified retained
  continuation are implemented; broader catalogue remains open.
  Coordinate `0_Edit` with migration P4; do not alter `2b`.
- [ ] **P2 ai** R8 Add Gallery export and read-only generation results through
  shared UI/data helpers after R4 receipts exist; submission stays CLI first.
  Cover assigned/unassigned/Artist provenance, stale sources and mobile navigation.
  Static export/results, People masthead and exact Photo Review deep links are
  implemented/tested; full fresh sandbox publication, Artist entry integration
  and real-page user acceptance remain open.
- [ ] **P2 either** R9 Agree storage/backup/retention limits and safe run filing
  before broader batches; then decide whether direct local-service execution is
  worthwhile. No automatic pruning, remote upload or server exposure.
- [ ] **P3 either** R10 Extend to male/animal recipe profiles only after suitable
  sources, algorithms and render acceptance; coordinate I26 metadata/discovery
  migration separately. Reuse the runner, not another engine or duplicated CLI.

### Required verification cases

- Two same-basename photos, distinct IDs with identical bytes, named/loose Various,
  moved/renamed source, stale derivative, missing preset and Artist-domain mismatch.
- Preserve-color profile cannot emit contradictory fixed-color/hairstyle/reset
  instructions; profile overrides do not mutate canonical identities/components.
- Stable seeds on retry, no global Female/default changes, missing parent result,
  wrong subject profile and unsupported stage/engine block explicitly.
- Preview/check create no files, download no models and contact no server.
  Repeated prepare verifies exact evidence; unknown/edited outputs never overwrite.
- Missing server nodes/models, API validation errors, timeout before/after accepted
  POST, server restart/history loss, partial batch and collection failure remain
  visible and recoverable without duplicate jobs or false completion.
- Generic workspace maintenance preserves/refuses job paths; generated trees never
  enter likeness cores/intake, and the first end-to-end mock covers export to results.

## Scope transfer and dependencies

| Source | Disposition |
| --- | --- |
| A8 generation exploration | Detailed execution design moves here; original rationale/raw chat remains there. A8 is marked transferred, not implemented |
| A7 manual-action execution UX | Stays with actions; photo actions are not render jobs and use separate manifests |
| Manual migration P1-P6 | Keeps current female prompt source audit, shared components, `0_Edit` and Prime/Bare semantics; this runner consumes approved recipes |
| Intake I12/I26/I29, upkeep U7 | Keep preparation/real acceptance, subject directory migration and maintained derivative handoff; a render does not accept them |
| Layout | Keeps common presentation/navigation; this owner specifies the generation request/result payload and lifecycle |

## User request (verbatim)

Source: chat, Oct 25, 2026, 20:44 -05:00.
Coverage: D1-D7, appearance profiles, exact staging, batch-first CLI, parallel
milestones, Various/I26 boundaries, later male/animal support and GUI integration.

<!-- markdownlint-disable MD013 -->
```text
I know we need to finish off other things in the flow to prove early versions of the intake, but wish to start to implement the process to generate the rendering of an image in ComfyUI via a dedicated workspace.  So need a concrete plan of what the workspace will be named, how we'll push photos to the inputs for it as well as how it would work to trigger ANY image as you suggested could be send into the workspace to render any of the current female flows.  But we'd want to adapt them not to override the hair, eye color etc ... but I may want to override the bust, body and a few others because many prospects may not posess those attributes that I would want in the long run.  So there may be a base of the larger bust and slender body style we do want ComfyUI to pick from.  So there's a hybrid in just taking the original vs. also seeing how the body shaping works when creating an A Pose for that person, etc... So, that's something I want to figure out and how it might impact our Various directory - not being female specific as well or naming Various to Female or something like that so we can support additional Males, Animals and other intakes and not just be oriented to the cards and images I am currently working on.  Does that all make sense.  Having a much more robust and solid proposal would help me while I need to take the time to review the other pieces and we can work both parts of the plan in parallel.  So, again, think deeply about how we can start to align the work with incremental and small changes to get to a target state where I ingest new images, get them cropped, enhanced, assigned to identities based on likeness and can then support rendering images in ComfyUI in an easier manner than having to manually to pick them from the gallery and abuse some of the current workspaces and workflows to do so.  I can setup a workspace for Females specifically so we can orient to that and later one for men, kind of like the separation for the main assigned characters, but a more generic one for unassigned Females, Males, etc...   I think we're onto something here - and even if it's generating a batch .json file for a CLI run to execute all the files moves and calls to ComfyUI for that workspace - that's till a plus.
```
<!-- markdownlint-enable MD013 -->

## Workspace available and curated (verbatim)

Coverage: R1a records user completion of cloning/cleanup; R1b tests communication,
R1 retains the observed input-root blocker. R4 owns a separate generated
`Reference` area; manual `zz_shots` are preserved rather than automatically
imported. Shared `0_Edit` migration still belongs to manual migration P4.
No images were uploaded, workflows published or renders queued during the probe.

<!-- markdownlint-disable MD013 -->
```text
I have cloned and started the Sovereign Females workspace if you want to test out any of the communications with the ComfyUI server and workspace to see how that works as well.  I did not copy any inputs, so all existing workflows point to input that don't exist - and I still need to clean-up the existing workflows - unless you can automate some of that as well - but that's less important.  We haven't yet incorporated all my 0_Edit flows into the system yet, so they are still on zz_shots as manual flows.  But if you publish new workflows under a new area that is also fine as well - just for initial testing purposes.  Since this workspace is a clone of Angel Primes and it's not a real used workspace.

Actually - I cleaned up the workflows and left my zz_shots and alpha workflows - the other female and male workflows for the Angels no longer exist there.  But my zz_shots reference Angelica - but that was just for me to bound to something concrete and not be generic.  So we can adapt this Sovereign Females workspace into what we want the workflows to be for this work.
```
<!-- markdownlint-enable MD013 -->

## Oct 25 continuation (verbatim)

Coverage: D1/R0 records the chosen clone; R0a starts offline work independently
of intake acceptance. R2/R4/R5 own reference versus explicit character context,
workspace mapping, server capability checks and CLI execution. R7/R8 own
catalogue/Gallery actions. Clone cleanup and generic Female retirement wait for
accepted replacement; neither is performed by this foundation.

<!-- markdownlint-disable MD013 -->
```text
Ok - so after all the discussions I a cloning the Angel Primes workspace to be a Sovereign Females workspace where we could get it setup to run those jobs.  It'll copy all the workflows, but I'll change the inputs/output directories to align to the Sovereign Females instead of Angel Primes, but that'll includes all my saved workflows, zz_shots and others that I can clean-up afterwards, then we can figure out what to publish there and potentially then remove the generic "female" flows from Angel Primes - once we get this all going.  So what can you do in the meantime to get this started - assuming that I will approve the image intake changes and all those items.  This would be an extension of the existing gallery pages to make some actionable flows to generate from either the "females" workspace or the respective character workspaces (Angel Primes, Draken Sisters, Draken Bound, etc... )  So in the end, if I want to push something through that uses a character specific workflow I can - or I can push it through the "reference" Sovereign Female workflow just to test out basics without all the hair, eye, etc... changes that happen.  That would be an awesome capabilty - and the checks to make sure the comfy server for that workspace is running will be key to ensuring that the two pieces can work together.  Eventually, I am thinking a more advanced UI would be more integrated, but this is a first step as I always view the CLI's as the way to make all things happen from any GUI.  Whether more real-time or batch.
```
<!-- markdownlint-enable MD013 -->

## Oct 26 acceleration and end-state (verbatim)

Coverage: guiding-principle section and R16 own the requested end-state:
automatic intake/likeness to gallery, explicit stage selection/branching, and
deterministic promoted-output structure. Manual migration P10-P12 owns shared
`0_Edit` template/JSON restoration and stage-input contracts.

<!-- markdownlint-disable MD013 -->
```text
If it's simpler to just bring back the 0_Edit work I have done into the generation of comfyUI workflows and create the data/art .json files to support it, add the templates, etc... that would be fine.  As the overnight work - you can do as much as you like and deem possible.  I'd like to advance this as fast as possible and get to the end state we scoped here.  Including anything from any docs/plans that is written up.  Those all guide us here - in incremental pieces - but my end state is that I want to bring in new images, auto process them in the intake and likeness to a gallery.  Inspect the, choose some for basic 0_Edit processing, view them, select some for 1_Alpha.  Then select some from 0_Edit and 1_Alpha into the 2_Studies and 3_Layers and 4_Wardrobes - basically trying to see which ones work and if I pick ones I like - pull them back to the gallery (in the proper directory strucuture that aligns with the workflows that generated them, which you need to define) and continue to a point where I can run a 5_Scene for an image I choose from the gallery (which could be any, even an original)  It all depends on what I want to try.  But to test - you can make the choices I might make, depending on the results of the image output at any step in our end-to-end flow.  If this isn't captured somewhere - we need to capture it as the guiding principle in the work we're doing here with all the docs/plans.
```
<!-- markdownlint-enable MD013 -->

## Overnight user request (verbatim)

Coverage: the decision table and R11-R14 above account for sandbox preparation,
cast/curation continuity, bounded manual workflow execution, subject-based
prefixes, stage-grouped GUI batching, server-side browsing, selective promotion,
explicit intermediate reuse and deferred Bench classification.

<!-- markdownlint-disable MD013 -->
```text
So, while I go get some rest tonight, what can you build out and test - I will leave ComfyUI up and running and you can iterate on working to see if we can't get a full pipeline going and even if you need to update the sandbox entirely with the new Various and all the updates we wanted to try out and completely rebase it with the new process, I would be fine doing a big-bang type of activity overnight and review the complete and final results in the morning.  With the rebase - I would actually want 100% of the existing images to go through the new intake process and get updated, but I still want the anchors and core images core the assigned characters of the Sister, Angels to take hold.  Ideally this would have also included the Family related changes, name changes, tracking the 3 various names we indicated earlier and all of the updates and run several of the iterations of chahracters through all a sample of the 0_Edit flows.  This doesn't require the .json data values and are all hard-coded flows right now - but that is fine just to prove the ComfyUI integration works.  The main thing I'd want to see in the execution of the workflows is that we adapt the filename_prefix to indicate the same name as we show in the gallery - instead of always being Angelica.  I also realized that I am still using the angels-primes/shots in all my outputs so that's also a piece to fix up in the workflows that do exist if I do anything manually.  That's a bunch of workflows and it's been on of the things I dislike about the way things work and need to re-think anyway.  The reason they exist has to so with the shared concept of workflows across workspaces, but maybe that is one additional area to fix up as we do this automation from complete end to end using our Gallery GUI...and me doing things less manually in ComfyUI to run a workflow for a sister, angel, model, prospect, etc... TBH - you can do as much as you can figure out how to do, adapt and make your own recommendations on how to proceed.  I give you full authority to make changes, as long as you document it in the plans with rationale and we can review that tomorrow or the following days as I do start to test and review things end to end.  But the most important part as we have progressed the past few days is the vision for the end-game in terms of how I can simplify my life with being able to test which image for a person makes the best A Pose - whether or not I need to use the 0_Edit to remove the background first, how they look in various versions of the 0_Edit, especially some of the 0c_, 0d_ , 0e_ and 0f_ flows.  These tell me whether or not the incoming image is good enough to use in 1_Alpha or beyond...which will be more .json based.  Basically 0_Edit, 1_Alpha, and 2_Studies are the proving grounds for an image generated to pull back into the gallery and use is for the card art we need with all the bells and whistles in those images in the next 3-5 phases.  Even the Benches (which need may need to be brought into the 0_Edit as something that can happen with ANY image and also aren't part of the prescribed flow - they were also a proving ground for the 1_ and 2_ phases as well).  Or maybe they do fit later in the pipeline.  It's just a matter of where to put them as well.  Basically, with the 0_Edit I am incorporating many aspects of just proving that a image or another generated can be used in some of the final art.  So if I get a good pose, motion, etc... I may use that one specifically into a scene or wardrobe to force/push that image into it vs. the A Pose - because of how the AI tends to favor the incoming image instead of just the prompt.  That's the lesson I have learned.  So generating images without a background, in bare form, in a pose, with specific body shape, bust, etc... the more I prepare the incoming image for a scene that aligns - the more that AI can focus on the scene and less on the person, their shape, expression, etc... it'll take that from the incoming image and make a much richer scene.  At least that's what I seem to understand.  So, yes - it takes more iterations on getting those prepared ahead of the scene - but I think the end results are best.  So, what this means is we don't bring back every single image into the gallery that we create with Comfy - we may ask for 2, 4, 8, 16 workflows to run - I'd like to see them from the ComfyUI-Outputs and if I choose one to copy back to the gallery for a person, then it's something we save for use - otherwise it just sits in the Comfy UI directory and eventually  - the get removed.  Does this all make sense in how I am thinking about the automatation in triggering the workflows.  Ideally we generate 2-4 images as a preliminary for sampling.  Then I can review those and see how things work.  It takes 2-3 minutes for the Qwen turbo mode to generate images, so if I have hundreds of intake images - we can't schedule them all at once - I need to choose which ones from the GUI to run through a batch - but that batch results should be viewable in the GUI and I could pick some to pull back to the gallery (into a proper directory - which we need to figure out) so that we save the outside of the ComfyUI directory and can use them in a scene or other workflow.  The GUI to select which workflow to send to also needs to be usable and not a single list of the dozens of workflows - but based on stage, etc.... so it's easy for me to create batches.  I know this isn't well thought out, but I am sure you can piece it all together.  Save these comments into a docs/plan that is appropriate for this work and get started on what you can do.  Iterate, test, verify with your own results - just be aware that if you trigger comfyui to run - it does take time to generate the image and it's not fast on this machine.
```
<!-- markdownlint-enable MD013 -->

## Oct 26 cleanup batches and output browsing (verbatim)

Source: chat, Oct 26, 2026, about 10:10 -05:00.
Coverage: C1-C9 and R17-R24 above.

<!-- markdownlint-disable MD013 -->
```text
the queue limit for comfy is 200 jobs

I did confirm a clean-up job did run properly.  I'm actually thinking that during the intake if we can't properly clean-up some files and comfy sovereign females workspace is running we could queue/schedule some jobs to render those items and run another job to view them and allow me to pull them back.  Or create a batch and ask me if we want to run the comfyui clean-up to attempt to remove the logos, etc... and/or other clean-up jobs.  Basically, keep some meta-data about the incoming images that need more clean-up in a generated batch.  Basically an advanced clean-up that is optional if I wish to run that batch and select from those files to bring one back - or you could even inspect them and bring the best of 4 back automated manner.  That might be a great way to put final touches on the images post the likeness process without me having to find or figure out which ones.  The other option is we use the meta-data to display them all as a filter in review gallery and I can select them some or all for clean-up.  Which means I might want a multi-type select and "select all" type setup like is available in google drive when you are viewing files.  vs. just actions on single photos.  These are all options for you to think about what fits best in our gallery views and how best to accomodate this type of automated integration with comfyui - even if it's still requires me to click a few buttons, check boxes, drop-downs, etc... But I love the integration and want to be able to use it in many different approaches.  It would allow me to select those batches of images, pick the workflows for that batch, select a number of runs for the workflows, and ultimately I'd love to be able to launch the cli with a button instead of just downloading the batch and running the command manually.  Then have another button to then review all the images in comfy, etc... we can figure out the right approach on what can be automated, what can pick best images to bring back or if I have to choose which ones to send to comfy and which to bring back - those are all great options.  I'd even like to browse ALL images in Comfy as well or filter them by workflow name or even if we can use the character names in the files to filter just for one person.  Many, many different options.  Would also like to be able to full view the images ahead of pulling them back.  We don't need to generate thumbnails, just show them scaled in the viewer until we bring them back into the gallery.  If I do bring some back, we'd need to pad/crop them to the 944x1104 versions as well, not just put into the gallery.  I'll want the files in the gallery to use the standard naming and not the workflow naming or some adaptation of it - or we need the filenames in the workflow to be more aligned to our image naming and not the way I have them named today.  Just more to think about as we work on it, there is probably something useful about the pose/workflow name to be used in the gallery so I know it's a comfy file rather than a normal original from facebook or a screenshot.  More to think about, document and execute on without my intervention.
```
<!-- markdownlint-enable MD013 -->

## Oct 26 large cleanup run (verbatim)

Source: chat, Oct 26, 2026, about 11:00 -05:00.
Coverage: R25-R28 and the large run section above; the combined recap.

<!-- markdownlint-disable MD013 -->
```text
Also, go ahead and run a bunch of jobs on the images in various that still need clean-up after the intake and let's see what happens in a larger batch.  I'll be gone so you can render up to 200 images in the queue.  So, don't stop, run the process end to end and automate the clean-up and also generate some additional 0d_ related images for each one that is in cleanup.  Run several 0_b and 0_c workflows as well.  You can run just 1 or 2 instead of 4 of each.  Whatever makes the most sense in an end-to-end run.  Cleanup usually doesn't require many iterations.  It's more the poses that drive more iterations.  So keep going, document everything and write a combined recap for the past 3 days of work into a single recap for me today with all outstanding items that require my attention, similar to yesterday but now with the additional items I need to do.
```
<!-- markdownlint-enable MD013 -->

## Oct 26 studio backdrop question (verbatim)

Source: chat, Oct 26, 2026, 15:51 -05:00.
Coverage: R29.

<!-- markdownlint-disable MD013 -->
```text
What color background are you using for the deluxe, I wonder if that shouldn't be the background color we use for all our processing - a gray based instead cream colored like is done in the cropping and all of my .json file prompts and such.  What do you think is the best studio background color to be using for those shots in the long run???
```
<!-- markdownlint-enable MD013 -->
