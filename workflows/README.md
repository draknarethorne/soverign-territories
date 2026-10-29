# Workflows

Workflows are generated from the prompts and stored by **set**, mirroring `prompts/`. ComfyUI workspaces are **deploy
targets tied to sets of cards**: each set has a *home* workspace, and which workspace serves which set is configuration
(`workspaces.json`), not folder structure. The repo copy is always the master.

```text
workflows/
  <set>/<Hero>/<Hero>_<Engine>_<Stage>_<Name>.json   generated: Qwen and MiniMax video (tracked in git); set = prompt group
  _templates/                                    the official ST0-ST6 stage templates; new workflows are cloned from them
  _curated/<set>/<Hero>/                         hand-tuned workflows; never regenerated (see Hand-curated workflows)
  .test/firered/<set>/<Hero>/                    generated FireRed test workflows (not in git)
  workspaces.json                                workspaces, homes (which workspace is home for which set), engines, defaults and excludes
  _archive/                                      old layouts and hand-made copies (ignored)
```

## Quick reference: the commands you will use most

**Preview by default (Oct 2026).** Every command that changes files (`deploy`, `pull`, `make`, `inputs`, `denoise`, `fork`, and the older `cleanup`, `tidy`, `setup`, `finals`) shows what it would do unless you add `--apply`; `--dry-run` still works and always previews. The `bin\*.cmd` launchers add `--apply` for you, so they do the work and `--dry-run` as the last argument previews them.

The options were simplified at the same time and the old switches are gone:
`deploy --include curated,shots,tests,staged,finals` and `--mode patch|new|existing|overwrite` replace the old `--curated --shots --tests --staged` and `--patch-only --new-only --existing --overwrite`; `pull --only shots|templates|finals` replaces `--shots` and `--templates`; `inputs status|pull|reset|fix|set HERO` replaces `inputs status|--pull|--reset|--fix|--set`. `status` also lists candidates and finals.

Run the scripts from a terminal or double-click `bin\menu.cmd` (`bin\help.cmd` lists everything). Add `--dry-run` as the last
argument to preview. STAGE is optional: `poses`, `head`, `scene`, `hair`, `motion`, `armor`, `clothing`, `video`, or `studio` for
every studio stage.

| I want to | Run |
| --- | --- |
| Check the data is valid | `bin\validate.cmd` |
| Regenerate art prompts from the JSON | `bin\prompts.cmd` |
| Build and push a hero's Qwen workflows to her home workspace | `bin\refresh.cmd Draknora scene` |
| The same for FireRed (local test copies) | `bin\refresh-firered.cmd Draknora scene` |
| Animate: video prompts, workflows, deploy | `bin\animate.cmd Drakness` |
| Regenerate only the video prompts | `bin\videoprompts.cmd` |
| See what is where | `bin\status.cmd --hero Drakness`, `bin\workspaces.cmd` |
| Deploy a set to its home workspace | `python tools\workflows\comfy_workflows.py deploy --group sovereign-dawn` (goes to Sovereign Dawn Series; nothing else needed) |
| Deploy a sister to Drakn Sisters and to Drakness | `python tools\workflows\comfy_workflows.py deploy --hero Drakness` (every home workspace gets everything; add `--mode new` to protect work in progress) |
| Put a temporary copy of a set in another workspace (reels, feeds, a scene next to the art) | `bin\publish.cmd Drakness "Sovereign Territories"`, or `python tools\workflows\comfy_workflows.py deploy --group drakn-sisters -w "Sovereign Territories" --dry-run` |
| Remove what a workspace is not home for (clone leftovers, finished temporary copies), then its empty folders | `bin\cleanup.cmd "Angel Primes"` (preview), add `--apply` (moves to backup; keeps hand-made `zz_` items, edited and undelivered files) |
| Copy a workflow so I can hand-edit it | `bin\fork.cmd WORKFLOW Tag` |
| Keep what I made or changed in ComfyUI | `bin\pull.cmd Drakness` |
| Sort loose workflows in the workspaces into folders | `python tools\workflows\comfy_workflows.py tidy` (preview), add `--apply` |
| Add the staged scenes (held back by default) | `python tools\workflows\comfy_workflows.py deploy --group drakn-sisters --class scene --include staged` |
| Put the ST templates in the templates workspace | `bin\deploy-templates.cmd` |
| Set a whole workspace up in one go: deploy its sets, tidy, clean leftovers, status (a preview until `--apply`) | `bin\setup-workspace.cmd "Angel Primes"` |
| Write or extend an angel's card set (and her signature items) | `bin\scaffold-angels.cmd [slug]`, `--coverage` for library use |
| Find or safely move an art piece and every reference to it (including `extends`) | `bin\art-refs.cmd where-used PATH` |
| Find art wording that leans illustrated (realism audit) | `bin\style-audit.cmd` (`--prompts` counts it in the generated prompts) |
| Turn text pasted into several cards into reusable pieces | `bin\extract-literals.cmd` (preview), add `--apply` |
| Run every commit hook | `bin\check.cmd` |

## Workspaces: one home per set

### Offline reference-rendering foundation

The running **Sovereign Females** clone from Angel Primes hosts
generic reference tests. Character-specific requests will explicitly select
their existing character workspace. The runner supports offline input preparation plus an explicit **bounded
manual-Qwen transport pilot**. Four clothed preservation modes can bind the
inspected single-subgraph graph, stage exact inputs, publish isolated
`Reference/BATCH/JOB` UI copies and submit selected jobs. It is not a general
UI graph converter or completed template migration.
`probe` checks a local server read-only. No command changes Female defaults,
cast identities or source photos. The separately explicit `manual-prefixes`
command backs up and corrects inherited output prefixes in this clone only.
The [rendering plan](../docs/plans/2026-10-25-reference-rendering.md) owns the
remaining capability, workspace/server and Gallery integration gates.
It remains outside the legacy hero-home workspace registry: generic setup,
deploy/pull/tidy/cleanup cannot select it by default and explicitly naming it
is refused as unknown. Use the rendering launchers for job-owned `Reference`
paths; formal registry integration remains planned, not an `accepts: ["*"]`
shortcut.

Use [the request schema](../data/schemas/reference-render-request.schema.json).
Example request (replace the hash with the exact SHA-256 of your selected file):

```json
{
  "schemaVersion": 1,
  "batchId": "female-proof-01",
  "workspace": "Sovereign Females",
  "jobs": [{
    "id": "source-one",
    "source": {
      "path": "Various/gallery/example.png",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "domain": "general"
    },
    "workflowMode": "reference",
    "recipe": "qwen-clothed-apose-v1",
    "profile": "reference-faithful",
    "seed": 42
  }]
}
```

Recipe/profile/workspace strings in an offline request express **requested
intent**, not an executable workflow or a guarantee about image preservation.
The example A-pose recipe above is not registered yet; `catalog` lists currently
supported pilot recipe IDs and disabled future stages. Reference profiles are `reference-faithful` or
`slender-fuller-bust` (future clothed adult studies); character mode requires
`character-defined`. No prompts or body/identity attributes are generated now.
Use concrete seeds; requests hold at most 64 jobs. IDs are short lowercase
letters/digits/hyphens. Paths in JSON are library-relative with `/` separators,
never absolute paths or shell commands.

```bat
bin\render-reference.cmd preview "BATCH.json" --root "B:\Photo Library" --dry-run
bin\render-reference.cmd prepare "BATCH.json" --root "B:\Photo Library" --apply
bin\render-reference.cmd check female-proof-01 --root "B:\Photo Library" --check
```

`prepare` without `--apply` previews. Preview/check are offline and write no
files. Sources must be image files in active `gallery`, `review` or maintained
`gallery_944x1104`, `headshot_944x1104`, `chest_944x1104` buckets below
Angels/Sisters/Models/Prospects/Potentials/Various/Artists. Artists require the
separate `artists` domain; other roots require `general`. Original/retained
variants outside those buckets are not supported yet. No arbitrary outside
paths, linked roots/junctions, parent traversal or underscore report trees.
PNG/JPEG/WebP/BMP bytes are copied unchanged; no enhancement or conversion.

Applying freezes `request.json`, `run.json` and `jobs/ID/input/source.EXT` under
`LIBRARY\_generation\reference\BATCH-ID`. Every source is checked before any
staging and checked again before publishing the batch directory. The manifest
states `inputs-only-not-render-ready`. An unchanged repeat verifies/reuses owned
evidence; changed/unknown files or conflicting requests refuse, never overwrite.
Check verifies frozen inputs and evidence even after a source moves, without
claiming the historical source is still currently assigned to the same identity.
Hashes detect accidental changes, not malicious rewriting of all local evidence.
Do not submit this manifest to ComfyUI or treat it as an API graph.

New batches also retain a validated storage-configuration receipt. Its frozen
paths and hashes remain historical evidence after the live configuration
changes; checking an old batch does not require today's configuration to
match it. Older receipt-less batches remain readable, but a malformed receipt
is rejected rather than ignored.

The runner is tested by `bin\test.cmd`, `bin\validate.cmd` and its focused
pre-commit hook. Menu **F** previews a request. No live library processing or
rendering is implied by the temporary-fixture tests.

#### Selected execution and results

```bat
bin\render-reference.cmd catalog
bin\render-reference.cmd compile BATCH --root "LIBRARY" --endpoint http://127.0.0.1:8188 ^
  --input-root "ACTUAL INPUT ROOT" --output-root "ACTUAL OUTPUT ROOT" --dry-run
rem Repeat the reviewed compile with --apply to stage inputs and job-owned graphs.
bin\render-reference.cmd run BATCH --root "LIBRARY" --limit 4 --timeout 5400 --apply
bin\render-reference.cmd status BATCH --root "LIBRARY"
bin\render-reference.cmd status BATCH --root "LIBRARY" --refresh
bin\render-gallery.cmd --root "LIBRARY" --apply
```

Preparation remains offline; compile explicitly contacts the selected local
server to validate node/model choices. It currently supports only Sovereign
Females reference-faithful jobs with a required `displayName` from the Gallery.
The provisional IDs include `manual-0c-cleanup-basic`, `manual-0c-cleanup`,
`manual-0e-enhance`, `manual-0f-full`, `manual-0b-background-basic` and
`manual-0d-deluxe-pose`. These reuse inspected graph/settings but
replace manual prompt conflicts with versioned, clothed-preservation pilot
prompts; they are **not exact migrated manual prompts**. The original graph is
frozen as evidence. Studies and Bench execution remains unavailable.
Alpha now supports the two shared clothed Prime outfit auditions below;
other Alpha variants remain unbound.
The intended destination is still shared JSON/templates, not permanent manual
workflow copies. No clothing-removal pilot is run.

### Shared clothed edit recipes

The Gallery and CLI catalogue also expose these generated-prompt recipes:

| Recipe ID | Shared assembly / task |
| --- | --- |
| `shared-0c-cleanup-basic` | Conservative cleanup in the source setting and outfit; default for new cleanup proposals |
| `shared-0b-background-basic` | Background-only grey studio edit |
| `shared-0d-relaxed-three-quarter` | Full-length three-quarter stance, weight on one leg, hand on hip |
| `shared-0d-grounded-three-quarter` | Both feet flat, one foot forward, forward knee bent |
| `shared-0e-enhance-basic` | Conservative exposure/detail enhancement |
| `shared-0f-full-clothed` | Full-length extension, continuing the source pose/outfit |
| `shared-1a-prime-outfit-relaxed` | `1_Alpha/1_Prime`: relaxed three-quarter view in the incoming outfit |
| `shared-1a-prime-outfit-grounded` | `1_Alpha/1_Prime`: forward-foot, bent-knee three-quarter view in the incoming outfit |
| `shared-0d-deluxe-seated` | Fully clothed seated bedroom audition |
| `shared-0d-deluxe-relaxing` | Fully clothed relaxed bedroom recline |
| `shared-0d-deluxe-side-resting` | Fully clothed side-resting bedroom audition |
| `shared-0d-deluxe-resting` | Fully clothed supine-resting bedroom audition |

Use the `shared-1a-prime-outfit-*` recipes for new three-quarter outfit
auditions. The older `shared-0d-*` and `manual-0d-deluxe-pose` IDs remain
compatible studio-pose pilots, not bedroom Deluxe scenes. Deluxe migration
is separate. A lifted heel is acceptable for the approved three-quarter
auditions; exact floor contact is not an acceptance requirement.

The four new Deluxe cards share one neutral photorealistic bedroom and soft,
even lighting. They retain only the manual series' scene/camera principle,
not its sexual posing, anatomy instructions or clothing removal. Face,
hair, physique and the incoming outfit are preserved. These are deliberately
non-explicit scene auditions, not exact migrations of the manual Bare prompts.
Generate with `bin\prompts.cmd --group angel-primes --slug female --stage edit
--family deluxe`, then preview/apply `bin\make.cmd Female edit`.
The shared cleanup default likewise freezes its generated prompt; explicit
`manual-*` recipe IDs and all already-compiled batches retain their behavior.

The Prime cards reuse the same preservation/view components with the
`prime-outfit-reference-human.txt` template under `1_Alpha`. Generate with
`bin\prompts.cmd --group angel-primes --slug female --stage alpha`, preview
`bin\make.cmd Female alpha --dry-run`, then `bin\make.cmd Female alpha`.

These are clothed reference-preserving controls, not appearance-profile
transforms or exact copies of the mixed manual drafts. Shared text comes from
`data/art/_templates/heroes/0_Edit/edit-reference-human.txt` and independent
JSON components in `data/art/edits/` and `data/art/studio/views/body/`.
Regenerate with `bin\prompts.cmd --group angel-primes --slug female --stage edit`,
preview `bin\make.cmd Female edit --dry-run`, then `bin\make.cmd Female edit`.
Never hand-edit the generated prompts.

Runtime compilation still reuses the inspected installed Qwen graph/settings,
replacing its positive and negative prompt with the generated shared text.
It freezes `prompt-source.txt` with an artifact hash alongside the exact UI/API
graphs; later source changes cannot alter a compiled job. Missing or unresolved
shared prompts fail explicitly. The separately generated repo workflows use
their normal stage-template configuration; sampler tuning in a manual graph
is not replaced by a denoise suggestion in the shared prompt header.

Refresh the Rendering page to see the new entries, preview/export a bounded
batch, then use the existing prepare/compile/run lifecycle. Compilation checks
server compatibility; a successful catalogue/generation check alone is not a
render-quality acceptance. Other appearance profiles remain blocked rather
than silently compiling as reference-faithful.

### Person-first automated paths

New compilations publish both workflows and images under
`reference/<Person_Name>/<stage>/<family>/`. The workflow basename is
`<Person_Name>_Qwen_<Edit-or-Alpha>_<recipe>__<UTC-stamp>__<batch-id>__<job-id>.json`;
SaveImage uses the same stem, then ComfyUI appends its counter and image
extension. New Prime outfit recipes sit in `1_Alpha/1_Prime/`; the older
studio-pose pilot IDs keep `0_Edit/0d_Deluxe/` for compatibility.
Batch/job IDs no longer add directories.

### Per-person sampling and source comparison

`bin\render-reference.cmd cleanup-batch --root ROOT --per-person 2 --recipe
shared-1a-prime-outfit-relaxed --samples 1 --id audition --dry-run` previews
assigned original Gallery photos across people, instead of filtering cleanup
hints. Replace `--dry-run` with `--apply` to save requests only; nothing queues.
`--sources SCAN.json` can narrow the source set first. Stable person IDs, not
display names, define groups. The ranking is pixel area, shortest side, then
source path; it is exploratory resolution-first sampling, **not face quality**.
Only exact duplicate bytes within a person are skipped. Similar faces, poses
or outfits are not deduplicated. Unassigned, synthetic and standard derivative
inputs are excluded and reported. Inspect sources before compiling/rendering.

`bin\render-reference.cmd compare BATCH --batch OTHER --root ROOT --dry-run`
previews a human-review report; `--apply` publishes
`_generation/comparison.html`, and `--check` verifies currency without writing.
It groups exact frozen sources and outputs by person, source, recipe, profile
and seed, with a matched-recipe view across people. Pending and failed jobs
stay visible. Frozen artifacts and receipt-owned output hashes are verified;
changed/missing evidence fails explicitly. It neither contacts ComfyUI nor
imports results. Regenerate after execution advances. Rendered resemblance is
an artistic review aid, never proof of source identity or kinship.

### Validation while preparation is running

Use `bin\validate.cmd --isolated --quick` for mutation tests beside a live
intake job. It copies `data` and `tools` once into a disposable short
`st-val-*` temporary workspace, executes the existing cases there with a
private ownership-checked recovery journal, propagates failure and removes
only that temporary copy. It never recovers or mutates the live self-test
journal. Omit `--quick` for all isolated cases. The regular no-argument
`bin\validate.cmd` still runs data validation, code tests and audits.
Legacy `--quick`/`--full` without `--isolated` mutate live data and must not
be used while another job reads it. Commit/push mutation hooks use isolation.

The timestamp comes from preparation of the frozen request, not the machine's
local timezone or a changing compile time. Exact source paths/hashes, seeds and
full identities remain in the receipts under `_generation/reference/<batch>/`.
Internal staged input paths retain their existing batch/job layout.
Existing compiled batches keep their original workflow/output names; no old
outputs are moved. The Outputs browser parses either layout, retaining
person/stage/family and batch/job filtering. Pull-back naming is unchanged.

`compiled.json` binds source/UI/API hashes and exact server roots.
`execution.json` records per-job intent, prompt ID, state, errors and actual
history-returned outputs. Submission persists uncertain intent before POST;
timeouts/crashes never automatically resubmit. HTTP validation rejection is
explicit; lost history holds for reconciliation.
`reconcile BATCH --root LIBRARY --job ID` previews matching exact client intent,
graph and batch/job metadata in the queue/recent 64 history entries; `--apply`
binds one unique match without POSTing again. Zero/ambiguous matches retain the
hold for operator review, never claim rejection or automatically retry.
`run` retries transient read-only GET polling failures visibly within its
deadline; it never retries a POST. Its deadline defaults to 3,600 seconds and
accepts up to 21,600 seconds (six hours), including queue wait. The longer
bounded window accommodates 63-job auditions behind existing work; it does not
raise the 64-job batch, 16-job owned queue or 200-job server limits.
Default submission waits for global idle.
When deliberately sharing a busy dedicated workspace, `--allow-busy-queue`
on `submit`/`run` appends one selected owned job at the normal queue tail and
waits for its scoped result before the next job. It never uses front/priority,
removes other jobs or interrupts execution. A deadline can leave an accepted
job queued/running; refresh/resume the same receipt rather than queue it again.
Submit, refreshed status and reconciliation serialize receipt updates through
`submission.lock` (PID/operation/time). This prevents a stale refresh from
erasing a newly accepted prompt ID. Local status remains read-only; a leftover
lock is an explicit hold requiring writer/receipt verification, not permission
to resubmit or automatically remove it. Receipt replacement uses the existing
bounded Windows permission-error retry helper; permanent failure preserves the
previous receipt and pending evidence. Gallery HTML is also published atomically,
so a failed replacement leaves the previous complete page.

`run` defaults to four jobs, accepts an explicit limit up to 64 and a deadline
up to two hours. With the default `--queue-depth 1` it submits one selected job
at a time. `--queue-depth N` (2..16) keeps up to N of the batch's own jobs at the
normal queue tail so ComfyUI never idles between them; it still waits for other
callers' jobs unless `--allow-busy-queue` is given. Every submission refuses when
the server queue holds its 200-job capacity (ComfyUI's limit on this machine).
It never clears the queue, interrupts other jobs or guesses a numbered output
filename. `submit BATCH --job ID --apply` is available for one explicit job instead.

Save prefixes use `reference/DISPLAY-NAME/BATCH/JOB/STAGE/VARIANT/...`, preserving
the Gallery name in metadata and a filesystem-safe name in paths. They never
route automation through `angel-primes/shots/Angelica`. `manual-prefixes --root
LIBRARY --dry-run` previews replacing only inherited SaveImage roots under the
clone's `zz_shots` and `alpha`; `--apply` first saves exact originals and a map
under `_generation/workspace-backups`. It preserves all prompt/widget content
except the changed prefixes; repeat is a no-op. Manual recipes keep their
explicit static subject name; only job execution dynamically supplies a subject.

Rendering is a static batch-first GUI at `LIBRARY\_generation\index.html`,
reachable through the shared masthead. It uses the existing Photo Review's
checked source/name metadata and stage-grouped catalogue. Source hashing is
local, not a new likeness scan. It exports requests; it does not execute a shell
or pretend a static browser page can run the CLI. Review cards link to the
selector for the exact source. Republish Photo Review after source moves before
refreshing the selector; stale source/hash errors are explicit.

Selection works like a file browser: filter the sources (text, stage, cleanup
hint), **Select visible** ticks every match, and several workflows can be ticked
at once. One request holds sources x workflows x samples (1, 2, 4, 8 or 16), at
most 64 jobs, in that order; export is disabled above the cap rather than
truncating. Cards carry an intake cleanup hint when the published preparation
evidence is verified: **Overlay left** (intake kept a logo/text overlay),
**Repainted** (LaMa erased clutter; check the repaint) or **Enhancement failed**.

`cleanup-batch` turns those hints into ready request files without queueing:

```bat
bin\render-reference.cmd cleanup-batch --root "LIBRARY" --dry-run
bin\render-reference.cmd cleanup-batch --root "LIBRARY" --hint needs-cleanup --hint repainted ^
  --recipe manual-0c-cleanup-basic --samples 2 --apply
```

It writes `_generation\proposals\cleanup-YYYYMMDD-HHMM\` with one request per
64 jobs plus `proposal.json`, and never overwrites an existing proposal. Each
request then goes through the normal prepare, compile and run steps.

When no published hints exist yet (before a new-format preparation run),
`overlay-scan` re-runs intake's overlay heuristic over a raw intake mirror,
read-only, and maps each hit to the current Gallery copy by its stable photo
key. The Gallery copy may already be cropped or repainted, and hits that are not
Gallery sources yet are listed as `unmapped`. Feed the scan to `cleanup-batch`
with `--sources`:

```bat
bin\render-reference.cmd overlay-scan --root "LIBRARY" --inputs "LIBRARY\_sandbox-state\RUN\inputs" --id overlay-scan-DATE --apply
bin\render-reference.cmd cleanup-batch --root "LIBRARY" --sources "LIBRARY\_generation\proposals\overlay-scan-DATE\overlay-scan.json" ^
  --recipe manual-0c-cleanup-basic --recipe manual-0d-deluxe-pose --samples 1 --id cleanup-DATE --apply
```

Bound `0_Edit` recipes: `manual-0b-background-basic`, `manual-0c-cleanup-basic`,
`manual-0c-cleanup`, `manual-0d-deluxe-pose`, `manual-0e-enhance` and
`manual-0f-full`. Each reuses one installed `zz_shots/Angelica/0_Edit` graph for
its model and settings, but its prompt is always replaced by the reviewed
clothed-preservation prompt. `0d-deluxe-pose` reuses the full-denoise
`0d_Deluxe_Bare` graph to re-pose the person in the same outfit; it never
produces unclothed images of intake photos.

Results reference files in the configured ComfyUI output root. They are **not
all copied back**. To keep one selected verified output outside ComfyUI:

```bat
bin\render-reference.cmd retain BATCH --root "LIBRARY" --job JOB --output-sha SHA --dry-run
rem After review, repeat with --apply.
```

Selected bytes and provenance go to `_generation\selected\BATCH\JOB`, marked
synthetic and ineligible for identity cores. They do not become Gallery
originals, anchors, protection evidence or global input defaults.
This initial storage preserves batch/job association and displayed subject
names without guessing a current person folder after reassignment. Retained
results appear in the Rendering selector as `source.kind: selected-render` and
can feed another compatible pilot edit job. The input guard requires the
retention sidecar, exact image hash, batch/job association and synthetic/core
exclusion flags; an arbitrary `_generation` file is not accepted.
Scene/wardrobe recipe support and a dedicated per-person synthetic collection
remain future integration; automatic pruning is not implemented.

#### Browsing every ComfyUI output and pulling chosen renders back

```bat
bin\render-reference.cmd outputs --root "LIBRARY" --dry-run
bin\render-reference.cmd outputs --root "LIBRARY" --apply
bin\render-reference.cmd pull "Downloads\pull-YYYYMMDDHHMMSS.json" --root "LIBRARY" --dry-run
bin\render-reference.cmd pull "Downloads\pull-YYYYMMDDHHMMSS.json" --root "LIBRARY" --apply
```

`outputs` scans the configured output root (`workspaces.json` `paths.outputRoot`,
or `--output-root`; `--workspace NAME` limits it) and publishes
`_generation\outputs.html` (masthead **Outputs**). It covers manual, automated
and legacy layouts, newest first, with filters for workspace, stage, workflow,
subject, age and text, paging, and a full-size viewer (arrow keys, Esc). Images
load from ComfyUI's own folders, scaled by the browser; nothing is copied or
thumbnailed. `--check` reports whether the page is current. Tick renders, give
an optional Gallery name (else the render's own subject), and export a pull
manifest (up to 64 images).

`pull` verifies each file's size and time against the page, then copies its exact
bytes to `_generation\library\STAGE\WORKFLOW\NAME_comfy_WORKFLOW_ID.EXT`. Legacy
outputs without a stage go under `Other`. It also writes a grey-padded
`..._944x1104.png` and a `.json` sidecar. The sidecar records `kind:
pulled-render`, the SHA-256, the source output, the PNG's prompt/workflow hashes,
SaveImage prefixes and batch/job, plus the request receipt when the batch is
known. The `comfy` token keeps a render distinguishable from a photo while the
name follows Gallery naming. Pulled renders are synthetic and never identity
evidence. They appear in the Rendering selector as `source.kind: pulled-render`,
so any of them can feed the next stage. A repeat pull of the same bytes reports
`already-pulled`, and different bytes at an existing name refuse.

#### Read-only server diagnostics

Use the exact endpoint from the running workspace, not a guessed port:

```bat
bin\render-reference.cmd probe http://127.0.0.1:8188 ^
  --input-root "B:\Comfy-Desktop\ComfyUI-Inputs\Sovereign Females" ^
  --output-root "B:\Comfy-Desktop\ComfyUI-Outputs\Sovereign Females" ^
  --require-node LoadImage --require-node SaveImage --require-node UNETLoader
```

This explicit online command only uses GET `/system_stats` and `/object_info`,
with bounded responses, timeouts, no redirects/proxy and an HTTP loopback IP
plus explicit port. It reports runtime input/output arguments, node availability
and loader model choices. Root mismatches or missing required nodes return
exit 1 with blockers. A passing connection is **not render readiness**: it does
not prove shared-folder round trips, validate a recipe's graph/models or upload
anything. Do not use another workspace's endpoint as a substitute.

The Oct 25 live check reached ComfyUI 0.38.2 with 970 node types and the basic
load/save/Qwen loader classes, but found the input root configured as
`Sovereigh Females` instead of `Sovereign Females`. The configured output root
matched. The correctly spelled input directory did not exist. Correct or
explicitly approve the intended mapping before staging inputs; the runner
does not rename directories, edit launcher settings or restart the server.
For the explicitly authorized overnight pilot, the actual runtime spelling
`Sovereigh Females` is intentionally bound as the input root in the receipt,
instead of renaming it or restarting the workspace. Output stays in
`Sovereign Females`. A future spelling cleanup must update server configuration
and new job profiles together; historical receipts retain their original roots.

A workspace is tied to a set of cards. `homes` in `workspaces.json` says which workspace is home for which set; a deploy goes to those home workspaces and nowhere else, unless you name another
workspace with `-w` that **accepts** the set (see below).
There is no catch-all workspace and no fallback: a set with no home stops the command with a message instead of landing somewhere else (that silent fallback once filled the brand workspace with 174 card workflows).

| Workspace | Home of | Also accepts, on request |
| --- | --- | --- |
| `Drakn Sisters` | the ten sisters (`drakn-sisters`): the whole image pipeline, Alpha to Video; final art is made here; `zz_Shots`, `zz_Curated`, `zz_Test` are mastered here | |
| `Drakness` | Drakness, as a second copy beside Drakn Sisters, kept in sync on purpose (see below) | |
| `Sovereign Dawn Series` | the Sovereign Dawn cards (`sovereign-dawn`: units, pets, buildings, equipment, tactics, workers) | the Drakn sets |
| `Sovereign Territories` | the art and brand set (`sovereign-territories`: title, logo, icons, key art, plates) and the `ST?_` stage templates | **any set**: promotional videos for reels and feeds, a scene kept next to the art, media for posts |
| `Angel Primes` | the angel test bed (`angel-primes`); it never produces final artwork | |
| `Drakn Bound`, `Elder Dragons` | their own sets; `planned`, so skipped by every command until the install exists and the status is `active` | |

Home rules match on `groups` and/or `heroes`, and `{hero}` stands for the hero's name. A rule may also carry `"class": "studio"` or `"scene"` and then applies only to
stages of that class (the class of each stage folder is defined in `data/art/_schema/stages.json`; anything that is not a scene is studio). `list` shows the home of every hero and what each workspace accepts.

- **Homes and temporary copies.** Every set has a home (the default of every command). Any workspace whose `accepts` list names the set (or `"*"` for any set) may also be given a
  copy on request: `deploy --group G -w "Workspace"` (or `bin\publish.cmd`). A workspace that is neither home for nor accepts a set is refused, so a set can never land in the wrong place.
  The copy is temporary: when you are done, `cleanup -w "Workspace"` removes it. Nothing is ever published automatically.
- **Duplicates in Drakness and Drakn Sisters are intentional.** While we work on one sister, a deploy puts her in both workspaces (the `Drakness` rule has a `heroes` filter), so we can
  work through issues with `zz_Shots`, `zz_Curated` or test items in her own workspace without polluting Drakn Sisters. Any other sister can get a temporary workspace the same way
  (add a `homes` rule with `heroes`, create the install, set it `active`) and be discarded afterwards. `cleanup` never treats these as duplicates to remove.
- **Only active workspaces with an install are written to.** A workspace whose status is `planned`, or whose install folder does not exist, is skipped with a message by deploy, pull,
  cleanup, tidy, denoise and the input reset. Create the install, then set its `status` to `active`. Groups listed under `skipGroups` (today Drakn Bound and Elder Dragons) have no generated workflows yet.
- **Hand-made items are mastered in the workspace.** Anything under a `zz_` folder (`zz_Curated`, `zz_Test`, `zz_Shots`) or named `zz_Curated_...` / `test_...` is never replaced, moved or removed by `deploy` (even with
  `--overwrite`), `cleanup`, `cleanup --orphans`, `tidy` or the input and denoise resets. That is what lets you refine a prompt directly in ComfyUI, fix the art JSON afterwards and redeploy without
  losing the hand-tuned version. Bring one into the repo with `pull` (`pull --only shots` for shots); delete one yourself if you want it gone.
- **`cleanup -w WORKSPACE`** removes the generated workflows that workspace is not home for (a clone's leftovers, or copies you published and are finished with), but only when their home workspace holds an
  identical copy and the repo has the master; everything goes to `workflows/.sync/backup/` and the empty folders are pruned afterwards (never a top-level `zz_` folder, never a folder with any file in it).
  Preview first. `status` shows `published` (a temporary copy of a set whose home is elsewhere) and `unrouted` (the workspace is neither home for it nor accepts it) next to the usual counts.

All workspaces that share an output project folder (see Where files live) write there, and the `SaveImage` prefix (`<set>/<Hero>/<phase>/...`) sorts renders into hero folders whichever workspace ran them.

### Stage templates

| Template | Stage | Used by `make --create` |
| --- | --- | --- |
| `ST0_Qwen_Text` | text to image, no reference image (4:5 portrait) | `templates.text` (title and key art; not yet automated) |
| `ST0_FireRed_Text` | the same with FireRed (more photoreal) | none yet |
| `ST1_Qwen_A_Pose` | A-pose from the source photo | `templates.poses` |
| `ST1_Qwen_B_Pose` | A-pose, Qwen 2.1 variant | none |
| `ST2_Qwen_Edit` | every edit after the A-pose: hair, motion, armor, scenes | `templates.default` |
| `ST2_MageFlow_Edit` | edit with Mage-Flow Turbo | none |
| `ST3_FireRed_Final` | FireRed final (the FireRed test engine) | `engines.firered.template` |
| `ST3_Flux_Final` | Flux final | none |
| `ST4_Qwen_Polish` | Qwen polish (int8) | none |
| `ST4_Flux_Polish` | Flux polish | none |
| `ST6_MiniMax_Reel` | MiniMax H3 image to video, 9:16 for Facebook reels (640x1152, still cover-cropped, 8 s, turbo) | `engines.minimax.templates.reel` (the default format) |
| `ST6_MiniMax_Match` | the same, the video keeps the still's shape (944x1104 gives 928x1088) | `engines.minimax.templates.match` |

### FireRed test engine (not in git)

Scenes can also be built for FireRed to compare with Qwen, and **every 1_Alpha step (Prime, Bare, Footwear, the 2b experiments) is built for FireRed too**, for every hero in every set, so the first images can be
compared engine against engine. The Angel Primes test sets `alpha/female` and `alpha/male` carry the **whole suite in both engines** (23 and 20 workflows each). They are generated into `workflows/.test/firered/` (ignored by
git), named `<Hero>_FireRed_<Stage>_<Name>.json`, from the template in `workspaces.json` under `engines`. They carry the
positive prompt only and read the same input images as their Qwen twins (so a FireRed Bare reads the Qwen Prime, until you pick another image in ComfyUI), and they deploy next to the Qwen ones by the same
routing. `--engine qwen|firered` limits any command to one engine. FireRed workflows default to **turbo** (`engines.firered.turbo`;
untick the switch on one workflow for a slow run) and the engine adds a real-then-magic effects instruction to the prompt
(`engines.firered.fx`, for the scenes in `fxScenes`, `"*"` meaning all).

```bash
python tools/workflows/comfy_workflows.py make --group drakn-sisters --engine firered --create --apply
python tools/workflows/comfy_workflows.py deploy --hero Drakness --engine firered --dry-run
# FireRed for every 1_Alpha step of every hero (what `setup` then deploys):
python tools/workflows/comfy_workflows.py make --engine firered --stage alpha --create --apply
# the whole suite of an alpha test set in FireRed (studio stages; its scenes are built by default):
python tools/workflows/comfy_workflows.py make --engine firered --group angel-primes --hero Female --class studio --create --apply
# FireRed versions of just the bare study and celestial steps (a regex needs a trailing $):
python tools/workflows/comfy_workflows.py make --engine firered --group drakn-sisters --stage alpha --match "Alpha_2_Bare_(Figure|Chest)$|Alpha_2b_Celestial[A-Za-z]*$" --create --apply
```

FireRed carries the positive prompt only, so the negative terms in a card do not apply to it; word the removal in the positive prompt. How the stages feed
each other (bare, A-pose with an underlayer, outfit, scene) is in [docs/art/tutorial-art.md](../docs/art/tutorial-art.md#the-image-chain-from-bare-skin-to-scene).

### Folders inside a workspace

A new workflow is saved in the workspace under its output folder, hero first and then the pipeline phase: `<Hero>/<phase>/...` in every shared workspace (`Draknara/1_Alpha/2_Bare/`, `Draknara/4_Wardrobe/armor/wardrobe/`, `Draknara/5_Scenes/themes/`), and `<phase>/...` in a single-hero workspace such as `Drakness`. The phases follow the pipeline in order:

| Phase folder | Holds |
| --- | --- |
| `1_Alpha` | `1_Prime`, `2_Bare` (Figure), `2b_Experiments/celestial`, `3_Footwear` (Barefoot, Heels): creates her likeness and the three golden images; Prime, Footwear, `2_Studies` and `3_Layers` are optional validation steps (see `docs/art/tutorial-art.md`) |
| `2_Studies` | `head` (close-ups, views), `hair`, `body` (turnaround views): studies on the goldens |
| `3_Layers` | the underlayer tests: `base`, `bikini`, `lingerie`, `swimwear`, `athletic`, `one-piece`, `backless` |
| `4_Wardrobe` | `clothing`, `armor`, `showcase` |
| `5_Scenes` | `signature`, `glamour`, `story`, `themes` |
| `6_Finish` | `polish` (Qwen detail pass, input role `scene`), `final` (FireRed look, input role `polish`); upscale is not built yet |
| `7_Video` | animation of a finished image |
| `Bench` | `motion`: a point-in-time test run on any phase's image, not a phase |

The card folders, the prompts and the ComfyUI output all use these phase folders (`art_layout.phase_path` maps a stage and family to its phase, `parse_dirs` goes back); the SaveImage prefix is the prompt's folder.
ComfyUI shows these as folders.
`tidy` moves loose files into them (and removes folders it empties); curated files go to a `zz_Curated/` folder, test files to `zz_Test/` and shots to `zz_Shots/`, which sort after every stage folder (flat in a single-hero workspace, one folder per hero in a shared one). Staged scenes (`Scene_Staged_*`) are built and kept in the repo but only added to a workspace with `deploy --include staged`, so the lists hold the scenes you are working on.

### Default incoming images

Every generated workflow opens with a default incoming image, chosen by its stage in `workspaces.json` (`inputRoles`, and the hero's images under `inputs`):
`alpha/` (Alpha 1 Prime) loads the original photo (`photos`); `alpha/bare/` (Alpha 2) loads the Prime image (`prime`); `head/` and `motion/` load the hero's
barefoot golden A-pose (`apose`); everything else (`alpha/footwear/`, `poses/<family>/`, armor, clothing, hair, scenes, showcase) loads her bare-skin image (`bare`). A hero without role inputs keeps the older
behaviour (the A-pose most of her workflows already read). Images are plain names, so each workspace needs the file in its own input folder.

```bash
python tools/workflows/comfy_workflows.py inputs reset --hero Drakness --dry-run   # preview: repo and every workspace; copies missing images into each workspace's inputs
python tools/workflows/comfy_workflows.py deploy --hero Drakness --mode patch --apply          # deploy the prompts only; point the inputs back with: inputs reset --apply
```

During a session you can point a workflow at any other image; a reset (or `inputs reset`) puts it back. To keep a custom input, save the workflow under
`zz_Shots/`.

**Choosing a default inside ComfyUI.** Open the generated workflow (for example `<Hero>_Qwen_Alpha_1_Prime`), pick the image in its Load Image node and save it; that is how you set a hero's photo
or golden image. Then bring the choice back into `workspaces.json` so it survives a rebuild or a reset:

```bash
python tools/workflows/comfy_workflows.py inputs pull --dry-run -w "Angel Primes"   # preview: which defaults you changed in the workspace
python tools/workflows/comfy_workflows.py inputs pull -w "Angel Primes" --apply  # write them into photos / inputs in workspaces.json
python tools/workflows/comfy_workflows.py inputs reset --hero Seraphine --apply  # push them into the repo copies (and the rest of her workflows)
```

`--pull` reads only the generated Qwen workflows, ignores the tool's own `..._00001_` placeholders and images named for another hero, and takes a default only when all the workflows of that role agree
(otherwise it reports `MIXED` and leaves it to `inputs --set`). `status` shows `inputs-changed` for any default you set in a workspace that `workspaces.json` does not hold yet, `setup` pulls first, and
`inputs reset` **stops** while such a choice is unpulled (`--force` overrides it, with a backup) so a reset can never silently undo your pick. The golden images are named by step with a `_00000` counter, so they sort above the numbered renders: `<Hero>_Qwen_Alpha_1_Prime_00000.png`,
`<Hero>_Qwen_Alpha_2_Bare_00000.png`, `<Hero>_Qwen_Alpha_3_Barefoot_00000.png` and `<Hero>_Qwen_Alpha_3_Heels_00000.png`. These are already the names in `inputs`, so
dropping a chosen render into a workspace's input folder under that name is all it takes; `inputs reset` repoints every workflow (a missing file is reported, not copied).

The **original photos** come from the library that `bin\originals.cmd` keeps (names follow the folder, scaled to 944x1104, see [docs/art/original-photos.md](../docs/art/original-photos.md)). When it renames a photo you had chosen, `inputs photos`
(run by `originals` itself) finds it again by its id and re-points `photos` in `workspaces.json`, the generated workflows that load it (a changed workspace file is backed up) and the workspaces' input folders; a photo whose original
moved to another hero's folder or was removed is reported, not guessed (`--dry-run` previews).
Retire the temporary `Alpha_2_Bare_Skin` shots once `Alpha_2_Bare_Figure` is tuned.

**Angel Primes.** The `Angel Primes` workspace is one tree for a whole test deck: `female/<Hero>/<phase>/...`, `male/<Hero>/<phase>/...`, and later `pets/`, `units/`, `buildings/`, `equipment/`, `tactics/` and `workers/`
(the divisions in `data/art/_settings/groups.json`; the repo copies of the workflows stay flat per hero). The twenty angels use the same golden-image names. Their original photo is expected as `<slug>_photo_944x1104.png` (`seraphine_photo_944x1104.png`, `auriel_photo_944x1104.png` ...) in the
`Angel Primes` input folder, already padded to the standard size; change a name with `inputs set Seraphine --photo <file>`. The male angels have no Barefoot or Heels step, so their `apose`
role points at the Alpha 2 Bare image and their golden image is the Bare. The ten women's photos are the `various_image_...` files you chose in ComfyUI, pulled into `photos`.
Angelica and Angelo follow the same Phase 1 and Phase 2 as every other angel (Alpha 1 Prime, 2 Bare, 3 Footwear and the 2b experiments for her; Prime and Bare for him; heads, views, body views and hair for both);
their old single `X_Pose` workflow was retired (its photo went into `photos`, and the file is in `workflows/_archive/legacy-x-pose/`). The workspace is `active`; a clone of another install is cleaned with `cleanup -w "Angel Primes"` (preview first).

**Alpha test sets.** `alpha/Female` and `alpha/Male` in the `Angel Primes` workspace (`prompts/angel-primes/alpha/<Hero>/`, output `Angel Primes/alpha/<Hero>/...`) are two generic test heroes for trying a photo before giving it to an angel, in a short version
of the phases (the woman has 23 workflows, the man 20): Phase 1 (Prime, Bare, and for her Bare chest, Barefoot and Heels), Phase 2 (head, face close-up, two head views, three body views, two hairstyles), two layer tests, one outfit, one armor, a Glamour
and a Signature scene with generic white wings, and three motions. Nothing of them touches an angel's folders, images or `photos`. To use one: copy the photo into the `Angel Primes` input folder, open `alpha/Female/1_Alpha/1_Prime/Female_Qwen_Alpha_1_Prime`
and pick it in the Load Image node, run Phase 1 and 2 and compare with the angel you have. If the photo wins, pick it in that angel's Prime workflow instead and run `inputs pull -w "Angel Primes"` (it then holds the new photo for her, and the test
set stays free for the next photo). `bin\scaffold-angels.cmd --alpha` rewrites the cards, then `refresh-group angel-primes` (or `setup-workspace "Angel Primes"`) builds and deploys them.

**Standard size (Oct 2026, provisional).** `standardSize` in `workspaces.json` is `[944, 1104]`: every original is scaled to fit and padded (not cropped) to that size
before the first X Pose, and the X Pose, Bare Skin and Barefoot images are expected at the same size. 944x1104 is one of the Kontext scaler's buckets, so the Qwen
templates pass it through unchanged; FireRed resizes to 1 MP (947x1107) and the VAE trims it back. The reset sequence for a hero:

```bash
python tools/workflows/comfy_workflows.py inputs status                       # every hero's photo / A-pose / bare image: where found, size, ok or WRONG SIZE or MISSING
python tools/workflows/comfy_workflows.py inputs set Draknara --photo Draknara_Photo_944x1104.png --prime Draknara_Alpha_Prime.png --bare Draknara_Qwen_Bare_Golden.png --apply
python tools/workflows/comfy_workflows.py inputs reset --hero Draknara --dry-run   # then with --apply; --reset also finds images under the output folders and copies them into each workspace's inputs
```

`--set` only needs the roles you give it (`--photo`, `--apose`, `--bare`); with `--dry-run` it prints and writes nothing. Workflows in `zz_Shots/` are never reset.

`bin\sync-inputs.cmd` (preview; `--apply` copies) puts every image a deployed workflow loads into the input folder of its workspace when it is missing: the selected Prime photos, first-shot experiment photos, or a restored photo. It changes no workflow and no setting, so a Prime you chose stays chosen, which `inputs reset` cannot promise (it stops while a choice is unpulled).
Run it after `make --create` and `deploy` when ComfyUI says an image is missing (`refresh` and `refresh-firered` do it). Placeholder names (`..._00000.png`, "not chosen yet") are counted, and what it cannot find anywhere is listed as NOT FOUND.

### Seeds

Every generated workflow draws a new seed on each run (`control_after_generate` = randomize), in the Qwen, FireRed, Flux and MiniMax templates alike. Only a final fixes a seed: a workflow in `zz_Final`, or a record replayed by `make` (see below).
`make` sets randomize on every generated workflow it builds or refreshes, and `deploy` does the same on the workspace copies (the seed value, prompt and input stay; a workflow that has a final record is skipped). Hand-made workflows (`zz_Shots`, `zz_Curated`, `zz_Candidates`, `zz_Final`) are never touched. `tools/workflows/test_comfy_workflows.py` fails if a template ships with a fixed seed.

### Image size (templates)

Stills keep the standard size (`standardSize` in `workspaces.json`, 944x1104) until the final upscale. Qwen snaps 944x1104 to itself (`FluxKontextImageScale`); FireRed and Flux rescale to a total number of pixels. ComfyUI counts a megapixel as 1024 x 1024, so the old value 1.0 turned 944x1104 into 947x1107; it is now 0.993896, which gives exactly 944x1104.
`python tools/workflows/align_templates.py --apply` sets that in the repo templates, `make` applies it to every edit workflow it builds or refreshes, and `deploy` applies it to the workflows a workspace holds (prompt, seed and input untouched, a backup first).
`tools/workflows/test_templates.py` fails if a template pulled back from a workspace undoes it. Text-to-image templates (1024x1280, 4:5) take their size from each prompt's `Size:` line. Video clips are sized by the `ST6_MiniMax_Reel` and `ST6_MiniMax_Match` templates themselves (the card's `format` picks one; see [docs/art/tutorial-video.md](../docs/art/tutorial-video.md)), and their length comes from the animation card.

### Denoise defaults

New generated workflows start at the high end of the range in their stage template (`Denoise ~0.8-0.9.` in `data/art/_templates/heroes/<stage>/*.txt`; 1.0 only for the Prime from the original photo), not at 1.0. Since Oct 2026 the edit stages run at 0.8 to 0.95
(0.7 held the pose too tight) and state the likeness in a Critical details block. `make --create` sets it, `comfy_workflows.py denoise` previews the plan and `denoise --reset` applies it to the repo and every workspace (backups first; `zz_Shots` and curated
workflows are never touched, and a denoise you set by hand in a workspace is listed as `KEPT`, not overwritten, unless you add `--force`).
The table and the tuning rules are in [docs/art/comfyui-art-pipeline.md](../docs/art/comfyui-art-pipeline.md#denoise-is-the-key-lever).

### Shots (zz_Shots)

A shot is a workflow you tuned for one render: a chosen seed, Turbo on or off, a changed input. Save it in the workspace under `zz_Shots/`, in any subfolders you like (`zz_Shots/armor/`, `zz_Shots/poses/` ...).
`pull --only shots` (`bin\pull-shots.cmd HERO`) keeps it in the repo under `workflows/_shots/<set>/<Hero>/` with the same subfolders and captures later edits; its file name and output prefix stay as you set them.
`deploy --include shots` (`bin\deploy-shots.cmd HERO`) copies kept shots to a workspace that lacks them and never overwrites a differing copy.
`status` shows `shots`, `shots-new` (pull it), `shots-changed` and `shots-missing`.
**Numbered saves are candidates, not shots.** A workflow ComfyUI saves from a render keeps a counter in its name (`Azaline_Qwen_Alpha_1_Prime_00004_.json`) and the seed of that render. Left loose in the workflow list it is a *candidate* (see below), not a shot, not an install-only and not a curated workflow.
If two workspaces hold a different shot under one file name (another seed), `pull --only shots` keeps the first one pulled and prints `CONFLICT` for the other; rename one of them to keep both.
Later, a seed worth keeping can move from a shot into the art data, so the Qwen and FireRed workflows are built with it (not built yet).
A shot is not a curated workflow: curated ones are the older hand-written workflows (and new ones written from scratch to test a concept), shots are the ones in use. Shots are captured even from a legacy workspace such as Drakness.

### Candidates and finals (zz_Candidates, zz_Final)

| Folder | What it is | Repo copy |
| --- | --- | --- |
| `zz_Candidates` | A generated workflow kept for a render with only small changes (seed, denoise, input image, Turbo, toggles). Every numbered save is one. Provisional | `workflows/_candidates/<set>/<Hero>/<phase>/` |
| `zz_Shots` | Started from a generated prompt, then edited more heavily (may carry explicit wording). Different from a candidate | `workflows/_shots/<set>/<Hero>/` |
| `zz_Curated` | The older originals, or hand-written from scratch | `workflows/_curated/` |
| `zz_Final` | The candidate or shot you chose, **from any stage** (Prime, Bare, a scene, a theme ...): one per hero, engine and stage. Holds the seed, denoise and input | `workflows/_final/<set>/<Hero>/<phase>/` |

All of them are hand-made, so `deploy`, `cleanup`, `tidy` and `denoise --reset` never touch them. They are arranged like the main tree (`zz_Final/female/Remiah/1_Alpha/1_Prime/...`), and **the file name decides where a file belongs**, so a save in the wrong place is fine:

```bash
python tools/workflows/comfy_workflows.py finals status -w "Angel Primes"             # candidates, finals, and which slots still lack a final
python tools/workflows/comfy_workflows.py finals sort -w "Angel Primes" --apply      # file them where their name says (preview without --apply)
python tools/workflows/comfy_workflows.py finals promote Remiah_Qwen_Alpha_1_Prime_00015 -w "Angel Primes" --apply   # make it the final; the earlier final is archived in zz_Final/_previous
python tools/workflows/comfy_workflows.py finals deploy -w "Angel Primes" --apply    # put repo candidates and finals the workspace lacks into their folders
python tools/workflows/comfy_workflows.py finals promote Remiah_Qwen_Alpha_1_Prime_00015 -w "Angel Primes" --use-as prime --apply   # also make its render the hero's default Prime image (copied to her workspaces' input folders and workspaces.json; then inputs reset --hero Remiah --apply)
python tools/workflows/comfy_workflows.py finals reclassify --apply                  # clean the repo with the same rules (preview without --apply)
python tools/workflows/comfy_workflows.py finals record --apply                      # write each final's seed, denoise and inputs into data/art/finals/<set>.json (after pull)
```

(`bin\finals.cmd` wraps these.) `pull` keeps candidates and finals in the repo as part of its normal run, and `setup` sorts and deploys them, so the loop is: save anywhere, `pull`, `setup` (or `finals sort`).

- **A misspelled hero, engine or stage** (`Remaih_Qwn_Alpha_1_Prim_00004_`), the wrong case, a wrong folder or a drop straight into the `zz_Final` root is matched to the closest known workflow and filed (the file name is corrected to the real one). An ambiguous match is refused, never guessed.
- **A renamed stage** still resolves: `X_Pose` saves are filed as the Prime (`finals.aliases` in `workspaces.json`) and keep their own file name.
- **Nothing is deleted.** An identical duplicate goes to `workflows/.sync/backup/`; a different file at the same place is reported as a `CONFLICT` and left alone.
- **What cannot be placed is left exactly where it is** (never moved to another folder) and is listed as `not placeable`. The same applies in the repo, and to `zz_Curated`, which is not rearranged. A shot you saved into a subfolder of your own stays there; one saved straight into `zz_Shots` is filed by phase, keeping its name.
- **`finals reclassify`** does the same for what is already in git: numbered saves at the top of a hero's `_shots` folder were candidates and move to `_candidates`, and everything is moved to its proper path. Run it, then `pull` and `setup` a few times, and the repo and the workspaces converge on one structure.
- **A final keeps its image.** `pull` (or `finals images --apply`) copies the render a final was saved from (`<output project>/<SaveImage prefix>_<counter>_.png`) into `assets/art/<set>/<Hero>/<phase>/<Hero>_<Engine>_<Stage>.png`, the prompt-path convention in [data/art/README.md](../data/art/README.md#where-rendered-images-live-convention) with the engine in the name so a Qwen and a FireRed final stay apart.
  A newer final of the same stage replaces the image (the old one is copied to backup first).
  **Only finals get an image**: candidates and shots never do. Watch the size with `finals images` (it prints the PNG total of `assets/art`); the convention allows Git LFS or external storage if it grows.
- **A final's settings are replayed by `make`.** `finals record --apply` reads every final kept in the repo (`workflows/_final`) and writes its seed, denoise, turbo (the Lightning LoRA), steps, cfg, sampler and the images it loaded into `data/art/finals/<set>.json`, one record per workflow name (so a Qwen and a FireRed final of a stage each have their own).
  `make` then builds or refreshes that stage's workflow with the record's **seed (its control set to fixed), denoise and turbo** and the new prompt, so a regenerated stage keeps the composition you chose.
  Not replayed: the input image (nothing is forced, you pick inputs yourself) and steps and cfg (the template sets them from turbo).
  A record you edited by hand is kept while the render it came from is still the final (`--force` replaces it).
  `deploy` otherwise keeps a workspace workflow's seed value (it only sets the control to randomize on a generated workflow that has no record), so a final's seed survives; a workflow a workspace lacks (or `deploy --mode overwrite`) comes from the repo copy with the record applied.
  If ComfyUI still changes the seed after a run, set the seed widget's control to `fixed` once in the UI and tell me.
- `finals.slots` in `workspaces.json` (optional) sets which stages `finals status` lists as slots to fill (any stage can still be a final, and counts as `+N other`); the default is Prime (`Alpha_1_Prime`, `X_Pose`), Bare (`Alpha_2_Bare_Figure`, `Alpha_2_Bare_Skin`) and golden pose (`Alpha_3_Barefoot`).

### Hand-curated workflows

Curated workflows write to their own output folder, `<set>/<Hero>/_curated/<name>` (for example `drakn-sisters/Drakness/_curated/`), so hand-tuned renders never mix with the generated families. `fork` and `pull` set this prefix for you (and patch the workspace copy to match); only the SaveImage prefix changes.
Curated files are named `zz_Curated_<Hero>_...` so they sort to the bottom of a workspace list and are never mistaken for generated ones; a workflow you captured from a render keeps its counter name (`..._00001`) and is left as it is.
Test workflows (experiments, A/B and bisect variants) are named `test_<Hero>_...` and live in `workflows/_test/<set>/<Hero>/`, writing renders to `<set>/<Hero>/_test/`. They are not kept in workspaces: put them there when needed with `deploy --include tests --hero H --match test_`, and `pull` saves new or edited ones back to `_test` before you remove them from the workspace. Prefix summary: no prefix is generated, `zz_Curated_` is hand-tuned and kept, `test_` is temporary.

Generated workflows are rebuilt from prompts, so a hand edit to one would be overwritten. Anything you tune by hand lives in
`workflows/_curated/<set>/<Hero>/` instead. `make` and `deploy` never touch that folder.

| You want to | Run | What happens |
| --- | --- | --- |
| Start from a generated workflow and tune it | `fork NAME --as Tag` (`bin\fork.cmd`) | Copies it to `_curated` as `zz_Curated_NAME_Tag` (its output folder uses `NAME_Tag`, and it records what it came from), and puts it in the hero's home workspace(s) |
| Keep what you did in ComfyUI | `pull --hero H` (`bin\pull.cmd`) | A workflow that exists only in the workspace is kept as curated (and renamed `zz_Curated_...` in both places); edits to a curated one are captured |
| Put curated workflows in another workspace | `deploy --include curated --hero H` (`bin\deploy-curated.cmd`) | Copies the ones the workspace lacks; a copy there that differs is skipped, never overwritten, unless you add `--overwrite` |
| See what is where | `status --hero H` | Shows `curated`, `curated-changed` (pull it) and `curated-missing` (deploy it) next to the generated counts, and `install-only` for anything not yet kept |

Name a curated workflow with the hero first (`Drakness_...`) so the tool can route it (the `zz_Curated_` prefix is added for you); the generated names are
`<Hero>_<Engine>_<Stage>_<Name>`, so adding a tag at the end never collides. If a curated idea turns out to be worth
automating, move what it does into a motion, transition, template or card piece, regenerate, and retire the curated copy.

### Video (MiniMax)

`data/animation/_sets/<group>/<hero>/*.json` cards turn a finished image into a short video prompt. A card names the hero,
the source (`artCard` for art we generated, so the intro is summarised from what we asked for, or `describe` for any outside
image), a look, and a list of `actions`. Each action becomes its own `Motion:` or `Scene:` block with a time range, joined to
the one before by a transition (`flow`, `blend`, `settle`, `hold`, `cut`, or any sentence you type). An action is a reusable
piece (`motion`, `scene`), literal text (a plain string or `beat`), and can carry `with` (things that happen together).

```bash
python tools/generators/gen_animation.py                                   # cards -> prompts/<group>/<Hero>/video/
python tools/workflows/comfy_workflows.py make --engine minimax --create --apply  # prompts -> workflows/<set>/<Hero>/ (ST6 template, tracked in git)
python tools/workflows/comfy_workflows.py deploy --hero Drakness --engine minimax --apply
```

Files are named `<Hero>_Video_<scene or pose it animates>_<Name>`, for example `Drakness_Video_Scene_Staged_EnchantedEvening_Awakening`.

### Working on one sister: Drakness beside Drakn Sisters

Every command takes `--class studio|scene` (all studio stages, or just scenes), `--stage`, `--match` and `--dry-run`. `deploy` **copies** to every home workspace of the hero, or to the workspace you name with `-w`.

```bash
# put one sister's scenes in her workspaces (Drakn Sisters and, for Drakness, her own), keeping what is there
python tools/workflows/comfy_workflows.py deploy --hero Drakness --class scene --mode new --dry-run
# put a temporary copy of her videos where promotional media is kept, then remove it when done
python tools/workflows/comfy_workflows.py deploy --hero Drakness --stage video -w "Sovereign Territories" --dry-run
python tools/workflows/comfy_workflows.py cleanup -w "Sovereign Territories"
```

## The loop

1. `bin\refresh.cmd HERO [STAGE]` regenerates prompts, creates or refreshes the repo workflows and deploys them to the hero's home workspace(s).
2. Run and refine there. Change the input image, seed or prompts as needed. Save a render-specific tuning under `zz_Shots/` or a hand-written one under `zz_Curated/`; both are guarded.
3. `bin\pull.cmd HERO` keeps what you made or edited in ComfyUI: new workflows become curated, edits to curated ones and shots are captured in the repo. Fix the art JSON, regenerate and redeploy: generated workflows follow
   the new prompts, and the hand-made ones stay as they are.
4. Need the set somewhere else for a while (reels, feeds, a scene next to the art)? `publish HERO "Workspace"` puts a copy there if that workspace accepts it; `cleanup "Workspace"` removes it when you are done.

If a destination workspace is not active or its install does not exist, the workflow is left where it is (skipped, with a message).

## Scripts

Run these from a terminal, or double-click `bin\menu.cmd`. `bin\help.cmd` lists them all.

```text
bin\refresh.cmd Draknara scene           prompts + workflows + deploy to the home workspace
bin\refresh-firered.cmd Draknora scene       the same for FireRed (local test workflows)
bin\animate.cmd Drakness                     video prompts + MiniMax workflows + deploy to the home workspace
bin\deploy.cmd HERO [STAGE]              deploy to the hero's home workspace(s)
bin\publish.cmd HERO "Workspace" [STAGE]     a temporary copy in a workspace that accepts the set
bin\cleanup.cmd "Workspace" [--apply]        remove what that workspace is not home for (preview unless --apply)
bin\setup-workspace.cmd "Workspace" [--apply]   deploy its sets, tidy, cleanup and status in one go
bin\fork.cmd | pull.cmd | deploy-curated.cmd      hand-curated workflows
bin\status.cmd | workspaces.cmd | inputs.cmd
bin\prompts.cmd | videoprompts.cmd | validate.cmd | check.cmd | style-audit.cmd | extract-literals.cmd
```

Add `--dry-run` as the last argument to preview. The tool behind them is `tools/workflows/comfy_workflows.py`; its tests (`python tools/workflows/test_comfy_workflows.py`) run in pre-commit and pin the homes, the `accepts` rule and the `zz_` guards.

## Rules worth knowing

- **Deploy needs a filter** (hero, group, stage or match), or `--all`. A set with no home workspace stops the command, and a workspace given with `-w` must be home for the set or accept it.
- **Deploy keeps your tuning.** An existing workflow only gets its positive prompt, negative prompt and filename prefix
  updated; input image, seed and toggles stay. `--overwrite` replaces the whole file. A `legacy` workspace (Drakness, which
  still holds hand-made experiments) always gets whole-file replacement. Hand-made `zz_` items are never touched either way.
- **Nothing is deleted;** anything changed, moved or cleaned out of a workspace is first copied to `workflows/.sync/backup/`.
- **Input images:** new workflows read the A-pose the hero's other workflows already use (`inputs`). Pin one in
  `workspaces.json` under `inputs` once you choose a golden pose.
- **Stage templates:** `deploy-templates` puts the `ST?_` templates in the workspace flagged `"templates": true` (Sovereign Territories). They are the only templates: `make --create` clones
  them (`templates` and `engines` in `workspaces.json`), so tune one there, `pull --only templates` it back, and every new workflow follows.
- **`X_*` files are never mirrored** (`exclude` in `workspaces.json`, plus `.gitignore`).
- `pull -w <Workspace>` brings workflows that only exist in a workspace into the repo; it is off for `legacy` workspaces.
- **A new install is a clone, so clean it:** cloning a workspace copies everything it holds. Add its `homes` rule, set it `active`, deploy its set, then `cleanup -w "<Workspace>"` (preview, then `--apply`).
- **Studio backdrop is light grey (Oct 26, 2026).** Generated prompts take it from `backgrounds/studio/grey-even`. Hand-made items
  (`zz_Shots`, curated, captured shots, `_candidates`, `prompts/_edit`) are never regenerated, so `bin\backdrop.cmd` swaps the six
  old cream phrases for the grey wording in place, as text: seed, inputs and toggles stay. Use `--repo`, `-w "WS"` or `--workspaces`,
  with `--dry-run` to preview or `--check` (read only, exit 1 while any remain). Backups go to `.sync/backup/<stamp>/backdrop/`.
  Reload ComfyUI tabs that were open during the swap; saving an old tab writes cream back.

## Where files live

Folder locations are set once in `workspaces.json` under `paths`; the tools read them from there.

```text
B:\Sovereign Territories\Models        original reference photos: the source, never an upload target
B:\Sovereign Territories\Masters       hand-picked keepers copied from the output (what the backup script protects)
B:\Comfy-Desktop\ComfyUI-Installs      the workspaces (code and workflows)
B:\Comfy-Desktop\ComfyUI-Inputs\<Workspace>   that workspace's own input images: transient copies
B:\Comfy-Desktop\ComfyUI-Outputs\<Project>   raw output, one folder per project; the prefix sorts it by <set>/<Hero>/<phase>/...
```

Each workspace writes to the project folder named by its `output` setting in `workspaces.json` (set in ComfyUI as that install's
output directory), and the prefix inside it does not change:

| Output project folder | Written by | Sets inside |
| --- | --- | --- |
| `Sovereign Territories` | Drakn Sisters, Drakness, Drakn Bound, Elder Dragons and the Sovereign Territories brand workspace | `drakn-sisters`, `drakn-bound`, `elder-dragons`, `sovereign-territories` |
| `Angel Primes` | the Angel Primes workspace (a test bed; it never produces final artwork) | `angel-primes` |
| `Sovereign Dawn Series` | the Sovereign Dawn Series workspace: the card set, kept apart from experiments | `sovereign-dawn` |

Everything under `Comfy-Desktop` is a transient copy of something that lives in the repo or on the working drive.
`python tools\workflows\sync_inputs.py` copies, into each workspace's own folder, exactly the images that workspace's workflows load
(preview first, then `--apply`). `python tools\workflows\organize_outputs.py` moves images rendered earlier (the old shared output) into `<project>/<set>/<Hero>/...`. Set each install's input and output folders in ComfyUI (the `--input-directory` and
`--output-directory` launch arguments), then retire the old shared folders. Until a folder exists, the tools fall back to the
old shared one.
