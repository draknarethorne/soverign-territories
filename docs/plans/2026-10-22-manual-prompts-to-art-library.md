# 2026-10-22: manual prompt migration into reusable art data

**Status:** holding (Oct 30 scheduling; tested slices retained, migration/visual acceptance unfinished)

**Stream placement:** M4 source fidelity -> M5 generic workspace -> M6 cast
art in the [execution spine](2026-11-05-priority-reset.md#execution-spine).
Select/transfer only that milestone's tasks before execution; the remaining
boxes here are deferred contracts/backlog, not another active work queue.

**Resume gate:** verified prepared-library inputs and explicit selection of
source-faithful `0_Edit`/`1_Prime` work with rendering R44. P14-P17 fidelity,
token reconciliation and set relocation remain prerequisites for that work,
not the current sandbox publication. Manual source drafts stay untouched.

## Nov 23 Beacon workflow planning companion

### Source-first reset and priorities

The user has substantially reworked `0_Edit` and `1_Alpha` on the other
machine. Restart **source discovery and migration planning**, not the
repository, workspace or library. The old 31-file inventory and existing
`0_Edit` pilot are historical evidence and prior art, not the current
source set or an accepted replacement. P10's delivered pilot remains
delivered; its existence does not satisfy the revised goal.

Work in this order, without activating holding implementation tasks merely
by recording them:

1. **User preparation:** finish and identify the intended manual `0_Edit`
   and `1_Alpha` workflows and any supporting art data. The user will set up
   a local ComfyUI workspace and identify the sources when ready. Agree on a
   private transfer/location and inspect possible embedded paths or other
   sensitive metadata; do not put private material in Git. Complete workflow
   JSON is preferred because prompts, graph connections and settings matter;
   preserve original bytes and extract text read-only for review.
2. **P14/P13, source inventory:** bind the selected actual files and hashes;
   inventory variants, prompt text/order, graph/settings, input roles and
   supported or excluded instructions. Compare existing pilot and older
   drafts as evidence, not as the authoritative new set. Resolve missing
   or conflicting sources with the user.
3. **P15/P21/P11, design and mapping:** map source instructions to reusable
   art data, components, templates and assemblies; reconcile tokens and
   deliberate emphasis with existing schema and stage inputs. Identify
   shared rules versus workspace defaults, person-specific overrides and
   per-job changes. Review each proposed mapping before implementation.
4. **P16/P4/P5/P6, implementation and acceptance:** after the applicable
   spine transfer and explicit source/implementation approval, implement
   bounded families and test prompt fidelity, graph behavior and branching.
   Compare supported recipes with the identified manual sources and obtain
   user visual acceptance under separate render authorization. Do not
   represent a test, transport pilot or generated file as visual acceptance.
5. **P17/P19/P20, static rollout:** after reviewed source fidelity and the
   relevant workspace mapping, preview regeneration and deployment of the
   selected static workflows. The user wants refreshed `0_Edit` and revised
   `1_Alpha` static workflows, with **Drakness as the first published pilot**
   for the user's verification. Confirm the exact source set, workflow
   coverage, workspace and proposed changes before applying; publication
   follows the applicable task-transfer, validation and preview gates.
   Preserve manual, curated, selected and existing workspace material until
   replacements and retention are reviewed. Publication is not a render
   or human acceptance.
6. **Later custom and dynamic integration:** P19/P20 and rendering R16/R44
   own workspace routing, source-bound jobs and lineage; P11/P12 own input
   and promoted-output contracts. Design a first-class manual/custom prompt
   path within the real phases, including user edits in ComfyUI and a
   reviewable path back into reusable templates/data. `zz_shots` supplied
   useful examples and a pullback route; eventual replacement is desired,
   but inventory, mapping, retention, verified replacement and separate
   approval precede any retirement or deletion. Do not assume a generic
   rename alone delivers this replacement.

There is no need for a new plan or to archive this one: its open tasks,
preserved sources and linked rendering owners still have independent value.
The [execution spine](2026-11-05-priority-reset.md#execution-spine) continues
to select WF1 planning only; implementation, generation, deployment, render
and library mutation are not authorized by this update.

### Phase direction and unresolved contracts

| Area | User direction; target, not a claim of current implementation |
| --- | --- |
| Selection | Choose a Gallery image, defaulting to its 944x1104 full version, with head and chest alternatives. Select one or multiple workflows. Exact directory and workspace naming remain open. |
| `0_Edit` | Optional, general exploration/preparation of varied source images before official character generation. Edits should normally work independently; a selected near-success can receive a further standard or custom correction, or proceed to Alpha. No mandatory edit chain. |
| `1_Alpha` | Prefer direct Gallery-to-Alpha generation of the desired character foundations, including bikini and bare variants; use a selected edit when the input makes direct generation unreliable. Studio background, lighting, character traits and poses matter. More than the current A-pose may be useful; default to all applicable poses, allow subsets and consider collections once the inventory is known. |
| `2_Studies` | Optional exploration of selected Alpha images, including hair, head and poses; a selected study can itself feed later work. |
| `3_Layers` and later | Layers are optional tests and possible inputs to `4_Wardrobe` and beyond. The selected Alpha Bare image often works best as the downstream default because underlayers can bleed into later art; an individual workflow can use another selected Alpha, Study or Layer result. Prime may remain the character's golden reference; exact per-role defaults are open. |
| Output | Inspect results before choosing which ones return to the person's Generated library; a viewer is desired, not assumed implemented. Preserve original photo identity through generated outputs; keep intermediate image/workflow history separately without imposing a complex filename. Exact paths, format and retention stay open. |
| Generic art | Preserve source-specific features such as hair/eye color for an identity without card art; use workspace-level generic figure defaults with selective persistent per-identity art adjustments. The user wants these library-side definitions outside Git until character/card assignment, then carried into art definitions. Field semantics, precedence, storage and promotion remain to be designed with Harbor. |
| Static and dynamic | Share underlying phase recipes. Static workflows support direct ComfyUI experimentation; the longer-term preference is on-demand generation with source-photo IDs and traceable history. Neither general dynamic execution nor workspace integration is claimed delivered. |
| Creative input choice | Let the user try an intentionally unusual image without a pose/appearance compatibility warning or block. Continue to enforce actual source integrity, safety, authorization and technical graph requirements; this does not imply every recipe produces a good result. |

Harbor owns Gallery, studio, identity metadata and Generated-library
behavior. Beacon owns workflow/ComfyUI integration; agree source IDs,
selected-input and result/lineage interfaces with Harbor before either side
implements shared behavior. Generated images do not become likeness-core
evidence. The existing safety and exclusion boundaries remain in force.

The current [art tutorial](../art/tutorial-art.md#the-image-chain-from-bare-skin-to-scene)
and [armor template](../../data/art/_templates/heroes/4_Wardrobe/armor-human.txt)
describe today's conventional A-pose/Alpha input assumptions, not proof
that revised direct-source variants work. Exact pose coverage, stage
compatibility, source-to-output lineage, naming, collections, promotion and
manual/custom workflow persistence remain open for source-backed review.

The user assigns Harbor the likeness, Gallery, studio, intake and image
processing continuation, including unresolved library-planning questions.
Beacon focuses on ComfyUI workflow generation/integration and assists
Harbor's library work only when he directly requests a bounded task. The
[handoff](../handoffs/2026-11-23-library-studio-planning/README.md)
retains the library owners and exceptions. This is a division of work,
not acceptance of pending results or permission to change shared workspaces.

The user wants to return to source-faithful `0_Edit`, `1_Prime` and
`2_Bare` workflows, but is still sorting newer refined edit prompts.
P14/P15/P16 continue to own fidelity, mapping and tested implementation;
do not treat the older 31-file inventory as the finalized new source set.
Wait for the user to identify the refined sources, then bind their actual
bytes and review supported wording/order before changing templates.

The requested direction includes static workflows for established card-art
categories such as Angels, Sisters, Bound and Dragons, alongside dynamic
on-demand generation for Models, Prospects and Potentials without a
pre-generated workflow per person. Apex may use both static and dynamic
workflows; Forge and Lab may retain some early-stage static workflows and
also use dynamic jobs for selected images. Exact stage coverage, tier
mapping, input and prompt selection, persistence and UI/CLI/API behavior
remain decisions, not delivered capability. Custom prompts and an eventual
replacement for manual `zz_shots` are in scope for planning; preserve all
existing manual/curated shots until a separately reviewed migration.

[WF1 in the spine](2026-11-05-priority-reset.md#execution-spine) selects
only a source-grounded current-versus-target map and handoff interfaces.
Reuse P17/P19/P20 for workspace mapping and P21 for section order;
[rendering R16/R44](2026-10-25-reference-rendering.md#oct-27-category-aligned-workflows-and-source-faithful-recipes)
owns source-bound job/route and stage lineage. The existing bounded
reference-job transport is prior art, not proof of a general dynamic
workflow system. Harbor owns the Gallery/library selection and generated-
result side; agree the boundary, IDs, accepted inputs, receipt/lineage and
failure behavior before either side implements shared integration.
No generation, rendering, deployment, Gallery mutation or template rewrite
is authorized by this planning lane.

**Nov 5 sequencing clarification:** Production cutover is not an additional
prerequisite. After trusted cast review/selections and explicit resumption,
use verified sandbox inputs with recorded source bindings for supported
fidelity/pilot work. Shared workspace/selection deployment retains its own
preview and approval gates. The active installation remains untouched.
The [priority map](2026-11-05-priority-reset.md#critical-path-versus-work-that-can-wait)
owns the wider sequence; PR3 still owns the later Production comparison.

**Oct 30 source coverage:** `edit_and_prime_templates.md` reinforces
P14's exact manual-nuance ledger, P15's data/component/token mapping including
camera and lighting, P16's one-workflow-at-a-time fidelity/regression checks,
and P7/P9 documentation/rationale. Review the current manual files again at
resumption; applying lessons to existing workflows requires explicit
before/after tests. This is future migration work, not permission to generate
or rewrite all templates during the rebase pause.

**Nov 2 experimental Deluxe drafts:** `prompts/_edit/deluxe` (six
`0_edit_0d_deluxe_bare_*` pose variants) is committed as the user's
experimental pose work. It was deliberately outside the historical 31-file
inventory; inclusion in the revised source set needs user selection. No tool
reads it.

- [ ] **P3 you** P18 Decide how experimental drafts such as
  `prompts/_edit/deluxe` coexist with the pipeline: stay manual-only, become
  an opt-in experimental workflow family that the generators never emit by
  default, or promote individual reviewed variants into P14/P15. Holding until
  the user chooses; until then the folder stays outside generation and
  migration.

**Nov 3 Sovereign Females workspace note** (`sovereign_females_workspace.md`,
verbatim at the end): Sovereign Females is the `referenceWorkspace` in
`workflows/workspaces.json` but has no `workspaces` entry, so generation does not
manage it. Its install holds `alpha`, `Reference` and `zz_shots` (255 workflow
JSON files; 38 `zz_` files still named `Angelica_*`). Direction: Sovereign
Females (and later Sovereign Males) become the generic experimental
workspaces; the generic female/male pair leaves Angel Primes; each workspace
receives only the workflows in its scope, chosen by configuration. Follow the
manual prompts' ordering of pose, background, camera and other details, and
check whether it should apply to all templates (P14/P15). The old Prime/Bare
`bare` examples can go once the new prompts replace them.

- [ ] **P2 either** P19 Verify the workspace inventory and old-to-new
  reference/collision map against the Nov 5 scope decisions below;
  bring remaining conflicts to the user one at a time:
  what Sovereign Females/Males contain versus Angel Primes and the Drakn
  workspaces, the phase-integrated custom-prompt replacement for `zz_shots`,
  including migration and retention, which old
  `bare`/Prime items retire, and conflicts with older docs, `_sets` and current
  generation flows.
- [ ] **P2 ai** P20 Add Sovereign Females first (Sovereign Males later,
  separately selected) to
  `workspaces.json` with scoped workflow selection (which templates or stages
  go to which workspace). Preview owned generated replacements while
  preserving curated/manual files. Review the `Angelica_*` `zz_shots`
  mapping against the eventual replacement; a generic rename is not
  replacement or permission to retire the originals. Remove the generic
  female series from Angel Primes only after the accepted female pilot; male
  removal/deployment is deferred. Use sync previews and tests. Gate: P19
  mapping and this plan's resume gate.
- [ ] **P2 ai** P21 Compare the manual prompts' section order (pose, background,
  camera and other details) with every template family, and propose an
  ordering standard as part of P7. Gate: P14 ledger.

## Nov 5 16:35: bounded workspace decisions before implementation

**Later studio direction:** the user selects original Gallery-photo workflow
inputs only from a workspace's own tier but allows generated-image inputs
from other tiers, including after Gallery pullback, while cross-tier likeness
comparison stays separate. Coordinate the future tier/workspace mapping with
[LY16/LY17/LY18](2026-11-02-library-layout.md#nov-21-multiple-studios-and-transition-proposal);
the user selects physical Generated folders per person, while generated-image
ownership and other pullback details remain open. This is a future contract,
not an implemented mapping or permission to change the current pilot or
workspace. The user selects a Sister/Angel's person as exclusive to that
character rather than also used for generic cards; coordinate the role
restriction and generated-input interactions with LY18.

Under delegated safe-planning authority, use the existing generic-first
direction rather than add another workspace scheme:

| Surface | Planning decision / implementation owner |
| --- | --- |
| Sovereign Females | Generic supported female test-bed recipes and neutral reusable shot templates only, selected explicitly in configuration; no generated per-person workflow forest (P19/P20) |
| Angel Primes / Drakn Sisters | Preserve character-specific workflow sets and input/identity bindings. Remove only the generic female series from Angel Primes after its accepted replacement is deployed and checked (P17/P20) |
| Sovereign Males | Later separate scope; do not make male setup/removal a prerequisite for the female pilot or silently deploy it with P20 |
| Generic `zz_shots` | Preserve the existing shot/template identifier, model/stage/variant distinction and references; remove misleading fixed-character naming only through an inventoried old-to-new map. Add deterministic disambiguation if generic names collide, never overwrite (P19/P20) |
| Named-person requests | On demand, bound to verified source identity/category and frozen job context; use rendering R44's shared naming builder rather than another workspace-specific output convention |
| Experimental/manual drafts | Deluxe stays manual-only and outside automatic migration/generation until P18 is deliberately selected; source drafts and curated/manual installed workflows are not disposable generated output |
| Retirement | Preview owned generated replacements/removals, retained manual/curated files and references; retire old generic examples only after accepted replacement and link/input checks |

These are scope/default choices, not implemented workspace registration or
template/output renaming. P19 stays open for the actual inventory, collision/
reference map and any conflict with sets/manual workflows. P14-P16 current
source fidelity and P6 user visual acceptance remain; no prompt wording,
art data, generators, config or installed workspace was changed here.
P20 must start with the female pilot, not interpret its older "then Males"
wording as permission for a combined reset. R44 owns executable output paths
and lineage; this section deliberately creates no competing path builder.

## Oct 27: source-faithful prompt reconciliation and Female test bed

The user's complete 11:05 chat is preserved at the end of this plan.
The [intake review owner](2026-10-23-image-intake-preparation.md#oct-27-1105-review-driven-crop-erase-and-framing-refinement)
preserves the separate feedback document and owns the immediate crop/erase/
framing benchmark. Neither new prompt renders nor the full rebase should
outrun that review. The previous shared preservation recipes were deliberately
narrow pilots, **not exact migrations of the user's manual prompts**. Their
successful transport/rendering does not accept their wording as replacements.

The manual drafts' section order, specificity and separate feature instructions
are source requirements, not suggestions to replace with a generic paragraph.
Preserve supported wording/order unless a contradiction, explicit exclusion
or user-reviewed A/B result justifies a documented deviation. The accepted
three-quarter views are additional Prime variants, not replacements for the
manual A-pose, and Deluxe remains the scene-based family.
Existing non-explicit/reference safety boundaries still apply: real-person
clothing removal and explicit sexual instructions remain excluded, recorded
as exclusions rather than silently described as exact migrations.

### Observed data/wording gap

The existing generator already separates `keyDetails`, palette/physique,
shared phrases and component slots. `bust` and `ownBust` both print `Bust:`,
but resolve different sources (shared phrase versus individual physique).
`tokens_for` omits promoted physique fields from the later figure line, so
reuse that mechanism instead of creating parallel permanent Body/Bust fields.
The generic edit template currently emits Face/Hair/Physique/Clothing/Pose/
Framing/Background policies; it is not the manual Pose/Background/Lighting/
Camera/Edit/Result/Critical-details/Likeness/feature sequence.
Generic Female also has adaptive colour language but fixed physique defaults.
Neither that placeholder nor fixed example-person colours should leak into
every dynamic person's resolved prompt.

- [ ] **P1 ai** P14 Complete the source-to-output fidelity ledger for the
  user-selected, revised `0_Edit` and `1_Alpha` source set after it is
  available and hashed. The old 31-file `prompts/_edit/female` inventory
  is historical comparison material, not the definitive new source set.
  For each supported instruction, record source file/line, exact wording,
  section/order, preserve/change intent, input role, existing field/component/
  token or proposed alias, and generated destination. Mark contradictory,
  excluded, deferred and already-tested text separately. Explicitly reconcile
  preserve-pose versus replace-pose and preserve-outfit versus change-outfit;
  never concatenate conflicting instructions or call a safe slice complete.
  Use the existing 24-file disposition inventory as a starting point, not
  evidence of line-level fidelity. Source files remain untouched.
- [ ] **P1 ai** P15 Reconcile manual labels with existing schemas/tokens before
  adding fields. Keep independently placed Bust and Body instructions where
  intended; map build/torso/arms/hips/legs, hair colour/style/texture, eyes/gaze,
  skin/finish, face/expression/makeup, pose, wardrobe, camera, lighting and
  background to their existing data homes where possible. Record ordered
  emission and intended repetition explicitly; remove accidental duplication,
  not purposeful emphasis. Propose a narrowly scoped extension only for
  a demonstrated missing concept. One person identity record owns permanent
  features; reusable defaults live in shared pieces and temporary look edits
  in a resolved job/card override. Category/cast membership is routing, not
  another copy of a person's anatomy or appearance. Specify precedence and
  visible preserve/change provenance; reject unresolved/conflicting values.
- [ ] **P1 ai** P16 Implement and test supported source-faithful template
  families after P14/P15 mapping review, preserving the manual section order
  and independently emitted features. Test two deliberately different
  person-data fixtures plus generic preserve-source mode: no fixed-person
  leakage, unintended duplicate feature blocks, unresolved tokens or mutation
  of identity data. Snapshot ordered positive/negative prompt text and assert
  every required supported source clause is covered. Then compare a small
  source-faithful versus current-pilot A/B using the same source, seed, graph,
  model and settings; document every intentional difference. Generated
  prompts come only from the pipeline, not manual edits. P6 remains visual
  acceptance; P11/P12 and rendering R16 still own branch/lineage contracts.
- [ ] **P1 ai** P17 Move the generic Female test-bed assembly from
  `data/art/_sets/angel-primes/alpha/female` to the user-requested
  `data/art/_sets/soverign-females/female`, retaining the supplied machine-path
  spelling while the workspace display name remains **Sovereign Females**.
  First inventory every card, heroArt/template/component link, generator/layout
  assumption, group/home/output mapping, default input, scaffold, validator,
  test, launcher/help/tutorial and generated/installed consumer. Show a
  previewed move/reference map; use `git mv` for tracked sources, preserve
  stable art IDs where possible, and regenerate rather than hand-move outputs.
  Decide explicitly whether the generic hero identity needs relocation;
  do not create a duplicate identity merely to mirror the new set directory.
  Add the real group/home mapping (currently absent from `workspaces.json`)
  and prove generation, role routing and deployment to only Sovereign Females.
  Preserve manual `zz_shots`, frozen receipts, selected inputs, Male/Angelo,
  other Angel Primes assets and existing rendered files. Inspect removals and
  path lengths before retiring proven-obsolete generated copies. The target
  is the skeletal test set, not bulk materialization of every library person.

P14/P15 are the immediate prompt work and refine P1-P3/QP4; P16 delivers the
remaining P4/P5/P13 fidelity work. P17 is the approved direction to plan and
execute with reference/preview gates, not a claim that the move has happened.
New dynamic workflows should use category/person paths through
[rendering R44](2026-10-25-reference-rendering.md#oct-27-category-aligned-workflows-and-source-faithful-recipes);
the old `Reference`-only publication direction is superseded for new jobs,
not retroactively for frozen batches. No other plan is closed by this change.

## Oct 25 reference-rendering handoff

The [active reference-rendering plan](2026-10-25-reference-rendering.md)
owns dedicated workspace, frozen per-image requests, batch/API execution and
Gallery results. This plan retains shared female prompt/component review,
`0_Edit` stage integration and Prime/Bare input-role semantics.
The user-created Sovereign Females clone keeps manual `zz_shots` referencing
Angelica; those bindings are historical experiments, not approved generic
appearance-preserving recipes. Offline input freezing, bounded graph binding,
scoped execution/retention and static Gallery export/results are implemented;
permanent template/graph migration remains here and in rendering R2-R5.
Its proposed reference-faithful versus slender/fuller-bust clothed profiles
require explicit preserve/change behavior; do not copy fixed character colors,
hairstyles or automatic cosmetic resets into a supposedly preserving recipe.
An ephemeral rendering context must not change the current generic Female,
cast identities or source manual text. A bounded existing-stage pilot can be
reviewed separately; it does not implement `0_Edit` or accept all flow variants.

## Oct 25, 21:36: Sovereign Females as the formal edit pilot

Use **Sovereign Females** as the first proving ground for formal `0_Edit`,
analogous to the image-processing sandbox. This refines the existing bounded
migration gate, not a separate prompt system or permission for broad deployment.
The later overnight authorization permits documented sandbox execution and
isolated pilot publication, superseding the earlier execution-only permission
gate below. It does not turn the manual binding into a shared generated recipe.
This plan remains the owner of stage/schema/layout/input-role integration;
the [rendering plan](2026-10-25-reference-rendering.md) owns isolated job
preparation, server execution and Gallery request/result actions.

1. Inventory selected manual `zz_shots` and their matching source prompts under
   P1/P2, preserving originals. Angelica bindings are examples to disentangle,
   not generic appearance defaults to copy.
2. Resolve one edit variant's intended change/preservation and exact input role.
   P4 implements the real stage across its existing consumers, rather than
   merely publishing a folder named `0_Edit`.
3. Publish generated pilot copies in a separate `Reference` area only after
   source/recipe approval and the rendering root-mapping gate. Compare exact
   input/output evidence before accepting the recipe.
4. Roll out accepted shared recipes incrementally to explicitly selected
   character workspaces under P6. Keep character overrides separate from
   reference preservation; retain existing manual flows until replacements
   are accepted. Do not change all workspaces at once.

`0_Edit` is an optional, explicit ComfyUI stage, not mandatory intake cleanup
or an automatic dependency for every Alpha job. A chosen edit result may feed
Alpha; an already suitable photo may go directly to Alpha. No new edit variant,
prompt, stage implementation or workflow publication is approved by recording
this direction alone.

## Oct 26 acceleration direction: migrate `0_Edit` first, then chain forward

The user explicitly allows a simpler/faster delivery path: prioritize bringing
manual `0_Edit` work back into shared generation (templates + reusable JSON +
workflow generation) as the first major migration, then connect staged
selection forward into Alpha/Studies/Layers/Wardrobes/Scene.

This is an acceleration of existing scope, not a scope reset. Keep migration
incremental, testable and reversible, and keep provenance boundaries that
separate originals/core evidence from synthetic generated derivatives.

- [x] **P1 ai** P10 Implement the first shared `0_Edit` data-driven migration
  slice from `prompts/_edit/female` into `data/art/_templates`, reusable JSON
  components and `_sets` assembly so generated workflows can run without manual
  `zz_shots` editing. Delivered the generic Female `0c_Cleanup_Basic` slice;
  later variants and visual acceptance remain open.
- [ ] **P1 ai** P11 Define stage-input contracts that allow user-selected branch
  progression (original or generated) instead of a mandatory single-chain path.
  Document typical inputs without warning or blocking deliberate creative
  choices; retain technical, safety and source-integrity checks. Align with
  rendering R16.
- [ ] **P1 ai** P12 Define promoted-output directory structure for selected
  generated images so Gallery lineage remains clear by stage and recipe while
  preserving existing identity-core/original boundaries.

## Oct 26 first shared `0_Edit` slice

### Oct 26, 21:48: complete edit migration and audition controls

The user requests bringing back and optimizing the full manual `0_Edit`
collection, with independent component-driven controls rather than fixed
prompts. The approved three-quarter variants include a grounded, forward-foot,
bent-knee stance. The goal is to audition character looks and select useful
Prime inputs, not always preserve the original physique.
The [rendering clarification](2026-10-25-reference-rendering.md#oct-26-2148-character-auditions-not-faithful-body-restoration)
owns the complete verbatim request, audition batch and rendered-resemblance
comparison. This plan owns reusable components, templates and input roles.

- [ ] **P1 ai** P13 Inventory every remaining manual `0_Edit` variant and map
  its preservation/change intent, input role and component slots. Optimize
  supported instructions against the user-selected revised sources; the
  older three-quarter recipe is comparative evidence, not the new baseline.
  Migrate in bounded tested families, not a blanket rewrite. Include
  independent face, physique, hair, pose, wardrobe, framing
  and lighting controls, both approved poses, and a preserve-physique control.
  Review `female_anatomy.txt` as mixed source notes, not a preset to inject;
  exclude explicit sexual content and real-person nudification. Record
  migration/visual acceptance or exclusion for every variant. Coordinate R33
  without duplicating ownership of batch execution.

Implementation continuation: five further shared edit assemblies now cover
background-only, conservative enhancement, clothed full-length extension and
the two approved three-quarter pose controls. Their common template resolves
independent face/hair/physique/wardrobe/pose/framing/background/task JSON.
Both poses have distinct reusable view pieces rather than new hard-coded
Python prompts. Generated repo workflows and Gallery/CLI bindings are present;
live visual acceptance, remaining manual-variant review and per-job design
overrides are not complete. P13 remains open rather than treating five controls
as migration of every manual draft.

At 23:12 the user clarifies the studio three-quarter views are Prime outfit
auditions, while Deluxe is a consistent bedroom scene. Two new shared Alpha
assemblies now reuse the preservation and pose pieces under `1_Alpha/1_Prime`,
with generated prompts, repository workflows and execution bindings. Old `0d`
IDs remain compatibility pilots; existing frozen batches and outputs are not
renamed. Lifted heels are accepted. The complete continuation is preserved in
the [rendering owner](2026-10-25-reference-rendering.md#oct-26-2312-continuation-finish-the-whole-pipeline).
The 63-job cast sample contains cleanup and both Prime views for 10 Sisters
and 11 Angels; visual acceptance is pending, not inferred from compilation.

The first shared cleanup assembly is now bound in the executable catalogue
and is the default for new cleanup proposals; explicit manual IDs and frozen
runs keep their behavior. Four shared Deluxe cards preserve the manual series'
bedroom/soft-even-light/wide-camera theme using neutral clothed poses, not its
explicit sexual content. An eight-job, two-character sample is prepared to
follow the running cast and intake-source pose comparisons.

### Manual edit inventory disposition (24 source files)

All paths below are under `prompts/_edit/female/`; source text remains in
place. Every source consumes an explicitly chosen photo or selected generated
reference, not identity-core evidence. "Safe slice" means deliberate shared
preservation behavior, **not** verbatim migration or visual acceptance.
The inventory is not completion of per-job physique/hair/wardrobe controls.

| Source filename | Current disposition |
| --- | --- |
| `0_edit_0b_background.txt` | Background safe slice; mixed appearance changes remain excluded from cleanup |
| `0_edit_0b_background_basic.txt` | Shared background-only assembly/binding |
| `0_edit_0b_background_bare.txt` | Real-person clothing removal excluded |
| `0_edit_0b_background_bust.txt` | Appearance-design branch deferred, not a cleanup default |
| `0_edit_0b_background_enhance.txt` | Existing separate Background and Enhance controls; combined preset not yet migrated |
| `0_edit_0b_background_plus.txt` | Mixed appearance/prop changes need independent controls; not blindly injected |
| `0_edit_0c_cleanup.txt` | Manual graph uses safe preservation override; full draft not migrated |
| `0_edit_0c_cleanup_basic.txt` | Shared cleanup safe slice is executable and default for new proposals |
| `0_edit_0c_cleanup_bare.txt` | Real-person clothing removal excluded |
| `0_edit_0c_cleanup_enhance.txt` | Separate Cleanup/Enhance controls available; combined preset remains open |
| `0_edit_0c_cleanup_plus.txt` | Prop-removal intent partly covered by shared basic; mixed appearance directions remain open |
| `0_edit_0d_deluxe_bare.txt` | Explicit content excluded; bedroom/camera theme informs neutral clothed resting slice |
| `0_edit_0d_deluxe_bare_lying.txt` | Explicit content excluded; neutral clothed side-resting slice |
| `0_edit_0d_deluxe_bare_relaxing.txt` | Explicit content excluded; neutral clothed relaxing slice |
| `0_edit_0d_deluxe_bare_resting.txt` | Explicit content excluded; neutral clothed resting slice, not anatomical posing |
| `0_edit_0d_deluxe_bare_sitting.txt` | Explicit content excluded; neutral clothed seated slice |
| `0_edit_0e_enhance.txt` | Conservative shared Enhance safe slice; appearance resets excluded |
| `0_edit_0e_enhance_basic.txt` | Shared conservative enhancement assembly/binding |
| `0_edit_0e_enhance_bare.txt` | Real-person clothing removal excluded |
| `0_edit_0e_enhance_plus.txt` | Appearance-design branch deferred; no hidden preserve/change contradiction |
| `0_edit_0e_enhance_pose.txt` | Pose/enhancement combination remains open; source-preserving control stays separate |
| `0_edit_0f_full.txt` | Full-length clothed extension safe slice; source draft's clothing removal excluded |
| `0_edit_0f_full_bare.txt` | Real-person clothing removal excluded |
| `0_edit_0f_full_bare_pose.txt` | Real-person clothing removal excluded; pose extension is a separate clothed task |

The other seven files in this source directory are Alpha drafts
(`1_prime`, `1a_prime_outfit`, `2_bare`, `2a_bare_figure`, `prime_org`),
mixed `female_anatomy` notes and `naming_workflows` notes. They are not another
seven edit recipes. New clothed Prime outfit controls use source-preserving
policies, rather than importing those drafts' fixed colors or sexual anatomy.

The generic Alpha Female `0c_Cleanup_Basic` slice now flows through the normal
art-data pipeline:

- `edit` is accepted by the card/piece schemas and is in the studio class.
- `art_layout.py` maps its cleanup family to `0_Edit/cleanup` and parses that
  path back to the edit stage.
- `edit-cleanup-human.txt` and the reusable
  `data/art/edits/cleanup/basic.json` keep preservation language in the shared
  template and task-specific positive/negative instructions in data. The
  original manual prompt also requested body, lighting and clothing changes;
  those conflicting directions were deliberately excluded from this
  appearance-preserving cleanup recipe.
- `workspaces.json` routes `edit` to `ST2_Qwen_Edit` with the selected photo as
  input. `comfy_workflows.py` recognizes the stage and generates the repository
  workflow from the canonical `Female_Edit_Cleanup_Basic.txt` prompt.
- The generated workflow is
  `workflows/angel-primes/Female/Female_Qwen_Edit_Cleanup_Basic.json`. It stays
  in the repository only: it was not deployed to a workspace or rendered.

The first generation attempt caught a missing `EDIT_TASK_NEG` value; adding
task-specific negatives to the reusable piece resolved it. The prompt was
regenerated with no unresolved tokens, and the workflow preview showed exactly
one create, no updates. A focused regression test ensures every template token
in this pilot is supplied; `bin/validate.cmd` passed all 811 tests across 29
suites. This closes only P10's first slice; it does not migrate the remaining
manual edit variants, revised Alpha, Studies or later stages.

## Oct 23 input dependency

[Intake preparation](2026-10-23-image-intake-preparation.md) now precedes
broad library/action testing. Source inventory here can continue, but QP2/QP3
must map immutable raw, conservative prepared/analysis, optional repaired display
and advanced edit outputs explicitly before migrating input roles or retargeting.
Baseline cleanup is not a new `0_Edit` variant. Advanced masked reconstruction,
full-body extension and artistic lighting remain this plan's ComfyUI work,
not mandatory automatic likeness preprocessing. Keep current selected inputs
and `2b` untouched while the upstream recipe is evaluated.

## Review and questions: 2026-10-22 16:21 -05:00

The user's Oct 22 direction replaces the older wait-for-first-shot-winner
approach. Review the manual set now; do not require another P2/P3 comparison
before inventorying it. No current draft is automatically an approved shared
template or a licence to rewrite every identity.

Ask these one at a time before implementing the affected decision:

| ID | Open question | Blocks |
| --- | --- | --- |
| QP1 | Which current variants are ready for migration, versus alternatives/working notes? The source is still evolving. | Final source manifest and first migration batch |
| QP2 | Confirm the remaining `0_Edit` variants and input roles, including the unresolved `0a` placeholder and `Of` versus `0f` Full names. The user corrected Cleanup to `0c_Cleanup` and Angelical to Angelica; `0l_Lighting` is a future placeholder to build during prompt work, not an existing tested prompt. | Schema/layout/role changes |
| QP3 | For each new Prime/Bare variant, does it start from the source photo, an edit output, or the existing Prime? Which face/makeup/skin details must be preserved versus explicitly reset? | Input-role and inheritance mapping |
| QP4 | Which changed labels become canonical token names, aliases, or component slots? A prompt label is not automatically a schema field. | Cross-template token migration |
| QP5 | Which unused AI-generated vocabulary is worth curating now, versus retaining for later? | Anatomy/library expansion, not inventory |
| QP6 | Should the later male/other-family rollout use the same approved order and tokens, or need separate render approval? | Broad rollout only |

No answer is needed to preserve sources and map candidates. Stop and ask if an
answer is needed to change templates/data or retire generated assets safely.
The user's requested `1b` retirement is approved direction, but must follow
verified replacements; `2b` is explicitly untouched.

### Follow-up clarification: Oct 22

The user's naming corrections are in their working note; do not repeat those
as open design questions or modify the manual source to enforce a new scheme.
Lighting remains planned work, not a missing file to invent during this audit.
Preserved verbatim:

<!-- markdownlint-disable MD013 -->
```text
As a side I fixed the 0c_Cleanup and Angelical mis-spelling in the naming_workflows.txt and correct the 0l_Lighting is a placeholder that we'll build new as we do the prompt work.
```
<!-- markdownlint-enable MD013 -->

## Scope and non-goals

Bring reviewed manual prompts from `prompts/_edit/female` into
`data/art/_templates` plus reusable definition JSON and `_sets` assembly cards.
Use the generator, not hand-edited generated outputs. This is a complete
prompt-to-data-to-workflow migration, not a copy of concrete Angelica phrases
into every template or a wholesale import of `female_anatomy.txt`.
Photo-library matching and game/MVP content remain separate plans.

| Decision | Direction |
| --- | --- |
| New stage | Add a real `0_Edit` production stage in `_sets`, with matching template, prompt/workflow naming, input roles and documentation |
| Prime / Bare | Revise the active `1_Alpha/1_Prime` and `1_Alpha/2_Bare` approaches from the selected manual prompts |
| `1b_Experiments` | Retire after new Bare replacements are validated; preserve reversible evidence/assets rather than deleting indiscriminately |
| `2b_Experiments` | Leave cards, templates, outputs and installed workflows unchanged; the user has not revised this work |
| Reuse | One home per fact; use existing pieces or suitable `extends` before adding another nearly identical JSON statement |
| Tags | Reconcile changed manual section labels with existing tokens/components across affected templates |
| Vocabulary | Split mixed statements into their actual data concerns; accept selected useful terms, not an entire AI-generated catalog |
| Preservation | Keep manual text, shots, candidates/finals, seeds/input choices and existing source history until incorporation is verified |
| Approval | Audit first, demonstrate one bounded generated/rendered batch, then obtain acceptance before broader rollout |

## Why the old work still matters

The purpose is reliable likeness and an explicit outcome on cropped originals
with fewer unnecessary edits. Build/pose comes from art data, not accidentally
from the source body. Studies/footwear/layers remain optional diagnostic steps,
not deleted merely because Prime/Bare changes.

Earlier evidence is retained in the
[prompt migration reference](../art/prompt-migration-context.md). It includes:
frame retirement; random seeds except chosen finals; input sync independent
of retargeting; FireRed's lack of a separate negative prompt; precise
head-to-toe/feet instructions; explicit removal plus positive outcome;
skin/eye/makeup inheritance; and scoped Angelica render failures.
An earlier universal paragraph order and automatic `FEET` token addition were
proposals, not settled standards. Reconcile them with the tested manual order.
Do not assume gold wording caused the makeup issue or that all new vocabulary
belongs in a hero's permanent identity.

## Work and evidence gates

**Oct 25 overnight clarification:** both manual `zz_shots/0_Edit` and
`zz_shots/1_Alpha` are the test bed to bring back into this normal data-driven
system. A temporary hard-coded API pilot does not complete P4/P5 or authorize
copying manual prompts forever. Rationalize tags, reusable definitions and
sequence for Prime/Bare, then apply demonstrated structural lessons to Studies
and later phases. Execution/Gallery work can progress independently but must
consume the same accepted generated recipes.

- [ ] **P1 ai** P1 Snapshot the selected manual files and record hashes,
  intent, tested status, labels, input/output role, engine and source notes.
  Include naming/workflow notes; flag contradictory text and duplicates.
  The current source directory may change during the audit: re-read before
  each migration and never delete the user's working files.
- [ ] **P1 either** P2 Resolve QP1-QP4 one at a time. Produce a source-line
  to existing/new token, component, identity field or template-static-text map.
  Separate visible labels from machine tokens and field names. Identify all
  existing consumers before aliases/renames; do not require data duplication.
- [ ] **P2 ai** P3 Rationalize selected anatomy/vocabulary with existing art
  definitions: body versus pose, complexion versus skin finish, facial
  structure versus expression, hair color/texture versus style, camera versus
  lighting/background, clothing versus material, eyes/gaze and makeup.
  Split compound statements where reusable concerns differ. Audit all current
  hero skin-tone wording; report neutral alternatives without bulk identity
  changes. Decide whether a curated vocabulary reference is useful.
- [ ] **P1 ai** P4 Define `0_Edit` stage/schema/layout and supported variants,
  assembly JSON, reusable pieces and template tokens in contract-first order.
  Update generator defaults, template lookup, scaffolds, denoise/header
  resolution, workflow role/name mapping, sync/deploy and finals/status/queue
  consumers. Avoid mistaking a folder name for an existing JSON `stage`.
- [ ] **P1 ai** P5 Implement one agreed `0_Edit` plus Prime/Bare pilot using
  selected manual references. Preserve the intended prompt section order and
  deduplicate statements through reusable data; explicitly test per-stage
  keep/reset semantics and FireRed lock behavior where applicable.
- [ ] **P1 you** P6 Render/review the pilot with the agreed source images
  and engines (Angelica, alpha/female, Drakness as appropriate). Record seed,
  input, denoise and prompt version; judge likeness, framing, intended body,
  skin, makeup/accessories and outcome separately before approving rollout.
- [ ] **P2 ai** P7 Write the accepted prompt standard and recurring audit
  checklist, then migrate approved template families/identities incrementally.
  Verify token resolution, component inheritance and all unrelated outputs by
  bytes. Validate schemas/data, generators and workflow tests through supported
  launchers; exercise preview before generation/deployment.
- [ ] **P2 ai** P8 After replacements pass, retire `1b_Experiments` across
  cards, templates only if unused, scaffolds, prompts, generated workflows,
  comparisons and installed copies with caller/reference inventory and
  recovery. Preserve hand-tuned `zz_` work. Assert `2b_Experiments` unchanged.
- [ ] **P2 either** P9 Refresh tutorials, art structure/template references,
  help and selected downstream input roles. Confirm whether old alternate
  Prime-B work is fully obsolete; do not silently replace old input picks.
- [ ] **P3 you** P10 Archive the manual source directory only after every
  selected statement is verified incorporated or explicitly retained/deferred,
  and the user confirms the working batch is no longer needed.

## Source task/context transfer ledger

Transferred tasks remain unfinished unless explicitly superseded below.

| Source plan / item | Current home or disposition |
| --- | --- |
| Oct 11 first-shot E6 | P1/P5/P6: replacement validation; not another required old P2/P3 bakeoff |
| Oct 11 first-shot E7 | P8/P9: retire `1b` after replacement, not promote a guessed winner |
| Oct 12 Prime T2, T9 | P2/P4/P5/P7: re-evaluate proposed order/feet tokens against new manual approach |
| Oct 12 Prime T4 | P5/P6: FireRed lock comparison, only shorten if validated |
| Oct 12 Prime T5, T6 | Finals plan I1/I2: current missing inputs and male source choices |
| Oct 12 Prime T7 | Finals plan I3: install-only videos/sample inputs/refresh decision |
| Oct 12 Prime L4, L7 | Library upkeep U3/U4: derived-output refresh and near duplicates |
| Oct 12 Prime T11 | P9: explicit alternate Prime-B disposition |
| Oct 12 standards T0, S0 | P1/P2/P5/P6: inventory and decide using current manual evidence |
| Oct 12 standards S1, S2, S3 | P3/P7: written standard, template/skin/inheritance audit and user batch choice |
| Oct 12 standards S4, S7, S8 | P5/P6/P7: small approved tested batches and byte preservation |
| Oct 12 standards S5, S6, S9 | P3/P7: selected vocabulary mapping and recurring audit |
| Oct 15 six open items, in order | P1, P2/P3, P5-P7, layout L10 + tooling D10, P10, P3 |

Prior exact user discussions and historical execution logs remain preserved
in their retired source records. All current constraints and unfinished
decisions needed for this migration have live homes above and in the context
reference. Archival of old plans is not completion of this migration.

## Raw user direction: Oct 25, 21:36 -05:00

Coverage: the Sovereign Females pilot section above refines P1/P2/P4/P6/P7:
inventory manual work, implement one formal stage contract, prove a bounded
generated batch, then roll accepted recipes out incrementally. Rendering owns
execution; intake acceptance remains independent.

<!-- markdownlint-disable MD013 -->
```text
Maybe this is the workspace we use to incorporate the 0_Edit as the formal beginning of the 0_Edit that will get pushed out into all the other workspaces over time as well... that's a decent thought - much like a how we're using the sandbox to test the image processing updates.
```
<!-- markdownlint-enable MD013 -->

## Raw user direction: overnight four-track clarification

Coverage: P1-P9 retain data-driven `0_Edit` and revised Alpha ownership;
the rendering plan owns dynamic execution/Gallery integration and the intake
plan owns processing. A hard-coded proof is not a replacement for this migration.

<!-- markdownlint-disable MD013 -->
```text
Ideally the 0_Edit workflows do support the same template and .json driven generation of the files and we're going to bring back the zz_shots 1_Alpha to replace our existing 1_Alpha prompts - but it needs the rationalization of the tags and etc... that we did documentin a plan.  Just want to make sure you know that my zz_shots/0_Edit and 1_Alpha are a manual test bed for what I want to bring back to our normal data driven generation - so we'd just have more generic .json files that aligned to the 0_Edit phase and 1_Alpha is more an example of the restructing of sequence and what tags are reall needed to get to the 1_Prime and 2_Bare images.  Hope this all makes sense as we're basically juggling 3 balls right now with 1) image intake/likeness processing 2) ComfyUI integration for dynamic and automatic workflow execution 3) adding 0_Edit phase and fixing 1_Alpha (and using lessons learned to adjust 2_Study and all phases for template structure) and 4) Building the GUI with so much more functionality to be the one-stop-shop for triggering the CLI and automation.  So I guess that 4 balls - lol!
```
<!-- markdownlint-enable MD013 -->

## Raw user direction: Oct 22, 16:21 -05:00

<!-- markdownlint-disable MD013 -->
```text
I do want to cover the entire docs/plans and I do want to archive plans in this iteration.  I am fine leaving plans that are active that make sense if they aren't superceeded by other newer plans - but Ideally we work through all the plans and If you have questions on the prompt/template work we started with, stop and ask me about it.  I do have those manual prompts I have worked on in the prompts\_edit\female and need to be brought back into the data/art/_templates library, with proper tokens added and the data/art .json files created to align with them based on the manual prompts.  We may need to create/update more reusable data/art .json files so we aren't duplicating the statements anywhere.  I ended up modifying my "tag" names for a few from the current templates - so we'll need to rationalize those updates across existing templates as well to reduce data redundancy in the data/art .json files that fill in the details of the prompts through the generation process.  There will be a new 0_Edit phase to the data/art/_sets and I do have updates that will change the existing 1_Alpha/1_Prime and 1_Alpha/2_Bare approaches we do use.  The 1b_Experiments can go away now as the new 2_Bare prompts should be able to replace them.  We'll leave the 2b_Experiments alone for now as I haven't worked on them.  I also have a more extensive C:\Soverign-Territories\soverign-territories\prompts\_edit\female\female_anatomy.txt we'll need to rationalize as well and bring back into the data/art for reusable .json that can feed into the images.  I didn't use many of them - but used AI to generate that entire set.  It does not align with our existing tokens and sometimes combines what we see as multiple art .json files into a single statement.  So that's a bit more extensive work - but it's all part of the prompting work I was doing to address the 1_Alpha prompts for ComfyUI in our generation process.  Does this all make sense?  Can you do it all at ones or do we need to work backwards from today and eventually get back to the 10-09 plans.  What makes most rationale sense to get entire coverage so that by tomorrow we have a refined, updates and accurate set of plans.  Any open questions about plans you can capture in a dated block at the top and we can then work through those one-by-one for any plans you do not archive.  That way we can clean-up our work so that I don't feel like we have so many loose ends and conflicting plans.
```
<!-- markdownlint-enable MD013 -->

## Oct 27 chat direction (verbatim)

Source: chat, Oct 27, 11:05 -05:00. Coverage: intake I30-I37 owns the
feedback examples, P14-P16 prompt fidelity/data reconciliation, P17 the
generic Female move, rendering R44 category-aligned dynamic paths, and
the updated recap/index preserve remaining work and immediate priorities.

<!-- markdownlint-disable MD013 -->
```text
I wrote up an initial review after looking at all the angels pictures - and some of the potentials.  I have a lot of feedback, but centers on a few themes.  Please read this and let come up with a plan for what to do about these and try to work on with the cropping, erasing, cropping and framing.  For the most part things are great - but a few comments in all of this will help find tune this and re-running specific examples I called out will help see it's working along with a sampling of other images to make sure we don't break what "was" working trying to tune the process.  Please read this .md file and update existing plans with this feedback and add more items and work to do in those plans.  I don't think we need a new plan or design document, but need to alter existing ones with this feedback and changes we propose.  Think deeply and also make sure everything else we are working on that remains is properly open in the plan and the recap calls out some critical next steps.  At this point, I am going back to the beginning and working those aspects - hoever I want to ensure that all of my templates for C:\Soverign-Territories\soverign-territories\prompts\_edit\female are brought back into the art libraries properly.  What you ahve been sending to comfyui in the workflows does not match my templates exactly - however you did find a new 3/4 pose that I liked during the process, but we need to ensure that we reconcile the tags that I am using vs. existing tags or scheme for the templates so we don't end up having a .json file for a person/angel/model/etc... with redundancy.  So this work needs to be reflected in the C:\Soverign-Territories\soverign-territories\docs\plans\2026-10-22-manual-prompts-to-art-library.md as to how my specific text and instructions need to help drive re-alignment of all the templates in terms of what I called out in what order and where the bust/body are used along with all the features of a person.  That way, it's not just generic, but pulls in the data about the person proprely.  I know I used a few different terms to specifically call out the body pieces instead of a generic block because it was critical to how it worked.  I worked with AI to come up with those manual prompts and what is there should be transposed into the templates and .json files.  Lastly - now tha we have a Soverign Females workspace - we should move the C:\Soverign-Territories\soverign-territories\data\art\_sets\angel-primes\alpha\female into the C:\Soverign-Territories\soverign-territories\data\art\_sets\soverign-females\female as the "test bed" for automating the generation of images as part of the art intake process.  That would be the skeletal set of workflows and then we can add in the dynamic creation of the angels, models, prospects, potentials as we been - but instead of putting them into Reference/[person name] we should honor the categorization of them under Models/[person name], Angels/[perrson name], Prospects/, Various/, etc...  I love the way the automation into ComfyUI is working - but we need to make some adjustments to the content of the prompts and I am ok with A/B testing with the prompts - but I want more strict adherence to the contents of my prompts and how they are written when we bring them back into the automation and art libraries.  Does this all make sense as well as the feedback docum,ent?
```
<!-- markdownlint-enable MD013 -->


## Oct 30 source snapshot: edit_and_prime_templates.md

Source: `feedback/edit_and_prime_templates.md`. Coverage: P14-P16. SHA-256: `9d9bf04b1b62bc249aa31ae028058ac82a0be4aba372b32ab72121ff22c65371`.
Captured for planning; open tasks are not implementation acceptance.

<!-- markdownlint-disable MD013 MD009 -->
````text
Just a reminder note that we need to bring back all the 0_Edit and 1_Prime work that was manually written and rationalize that back into the data/art pipeline, ensuring that it is properly integrated and utilized for future processing and organization.

We did write up most of that already, but when we get to that point we just need to re-review things to ensure the plan lays things out and we can test each of the workflows one-by-one to ensure that things work as consistent for the generated workflows as they did when I was running them with the manual prompts.

We might ahve some refinement in the way we structure and integrate the manual prompts into the automated workflows, ensuring that any nuances captured manually are not lost in the transition.  Some descriptions will need to adapt carefully into the data/art .json files and the templates will need the proper tags for accurate processing and organization.

I'll also want to review the generation code to make sure that adding these new workflows does not break existing functionality but we may need to bring some of the best practices of items in the prompts into existing workflows to declare camera settings, lighting conditions, and other relevant parameters accurately.

Additionally, we should document any changes made during this integration process to maintain a clear record of how manual prompts have been adapted and incorporated into the automated workflows. This will help future developers understand the rationale behind certain decisions and ensure consistency across the project.

This may happen in the future so we need to understand what our steps are to do this and ensure that our generation process isn't a complete mess after we do so.
````
<!-- markdownlint-enable MD013 MD009 -->

## Nov 2 chat direction (verbatim)

Coverage: commit `prompts/_edit/deluxe` -> committed Nov 2; experimental
poses kept separate and not for the entire pipeline -> the Nov 2 note
(outside the P14 ledger and generation); how to handle them -> P18.

<!-- markdownlint-disable MD013 -->
````text
You can commit the _edit/deluxe - they are more experimental with poses but I kept them separate from the other ones as they aren't really intended for the entire pipeline and only for more experimental work.  So we'll need to sort that out in how we can do that.
````
<!-- markdownlint-enable MD013 -->

## Nov 3 source: sovereign_females_workspace.md (verbatim)

Coverage: a Sovereign Females workspace with prompts, templates and drafts that
does not conflict with the pipeline -> P20; deciding which ComfyUI workflows go
into which workspace, through `workspaces.json` -> P20; generic Sovereign
Females/Males, with the generic female/male leaving Angel Primes -> P19/P20;
reset its workflows and generalise the `Angelica` `zz_shots` names -> P20;
ask questions where older docs, flows or `_sets` conflict -> P19; drop old
`bare`/Prime items the new prompts replace -> P19/P8; manual prompt ordering of
pose, background, camera and details, possibly for all templates -> P21/P7.

<!-- markdownlint-disable MD013 -->
````text
I've realized that within the workspace generation and comfy ui flows that we need to build out what will be for the sovereign females workspace specifically, ensuring that all prompts, templates, and experimental drafts are properly integrated and managed without conflicting with the existing pipeline.

We can use that workspace when working on bringing back the templates and I think what we'll want to do is plan out a way where we are conditionally deciding which comfy ui workflows go into which workspaces, since we do have quite a few and the number of generated workflows is large - but at the end of the day, we need what we need in order to generate the proper art for our selected angels, sisters, demons, etc... 

But we can have something like sovereign females that is more generic and then remove the generic female and male from the angel primes and only use a sovereign females, sovereign males and other workspaces for the experimental type work.  That way each workspace becomes clean with only what it needs for the scope of that workspace.

Soverign Females exists, but the workflows there need to be reset and the zz_shots still use Angelica in the name - even though that's not what they are intended for.  So we'd want to generalize the filenames as I took some short-cuts in naming things just to save time.

So you might need to ask me questions about how we want things organized in order to get it to a point where the generation process puts the right things into the various workspaces we do have already.  Some of this is done, but not all of it is handled in the workspaces.json file.

So, when we get to this point - we'll include this in the template and workspaces work we need to do so I can stop having my own experimental prompts and actually use the generation flow.

Also - to be clear, the bare examples are there to address the issues we did have a long time ago with how the existing templates for Prime and Bare were setup and we can get rid of some of the items that we no longer need in favor of the new prompts.

One lesson learned is that certain items need to be ordered in the manner that I have the manual prompts setup vs. our older templates in how things were working.  That might also apply to ALL our templates in terms of the priority of how the pose, background, camera and other details are provided.

Hope this helps and please make sure to ask me questions where we have conflicts in older docs, existing generation flows, _sets or whatever questions you do have.
````
<!-- markdownlint-enable MD013 -->

## Nov 23 machine split and workflow direction - verbatim chat

Coverage: machine ownership and deferred library decisions -> the
[Harbor handoff](../handoffs/2026-11-23-library-studio-planning/README.md);
Beacon's bounded workflow-planning lane -> spine WF1 and the Nov 23
companion section above. Implementation remains in its existing owners.

<!-- markdownlint-disable MD013 -->
````text
In terms of Likeness work - a) that's all going to happen with Harbor now as we did the hand-off for that and we'll just run things on this machine if Harbor requests it directly and we'll address the grouping in the 275 photos on his machine and he may ask you to validate some things.    b) Harbor will also work on the named folders implementation and all the things related to the plans we drafted.  c) Plans - we should resolve any open issues or questions or document that Harbor will need to address them when he started up that work.  d) I am trying to reduce the dual-work between machines until Harbor requests something specific and spend our time here fleshing out plans and other work we need to do.  So given that - what do we need to do here.

Let's try to close out the planning work and we can defer many questions to Harbor to clarify during the next phase of planning as long as we're giving him a direct and explicit hand-off on the planning, even for studio and gallery work.  Ideally - at this point we can transition anything related to likeness, gallery, studio, intake and processing the images to Harbor.  What I'd like to focus on here is the actual work for the generation of workflows and getting back to fixing the 1_Prime and 2_Bare existing templates based on my 0_Edit work I did start ... but I have even more refined edit prompts that I need to sort out first.  But the integration into ComfyUI and how that all works, my art templates and how we can generate images for the Models, Prospects and Potentials without having pre-generate workflows for each and every one is something I want to think about here.  Does that make sense in the split between the two machines and their purpose now.  So you - Beacon - are my beacon of hope in terms of the integration to ComfyUI workflows and assuming we get the likeness/gallery work all sorted out you can pickup on those aspects of generating workflows statically for high level card art categories (Angels/Sisters/Bound/Dragons, etc...) and dynamically for lower level card art (Models/Prospects/Potentials)  Basically the work might align to how we planned studios where the Apex is both static and dynamic workflows, Forge and Lab maybe have some static for 0_Edit, 1_Prime, 2_Bare but not higher level art defined as well as dynamic based on whatever image I want to fire.  I'll also want to support custom prompts and eventually eliminate the zz_shots and incorporate that into a better approach.  There's a lot of changes I think I'll need in terms of workflow generation both static and dynamic that we can focus on here.
````
<!-- markdownlint-enable MD013 -->

## Nov 23 source reset and phase Q&A - verbatim chat

Coverage: source readiness, revised migration and fidelity -> P13-P16;
phase/selection and chosen output -> P11/P12 and rendering R16/R44;
workspace defaults, custom workflows and `zz_shots` -> P17/P19/P20;
Gallery, identity metadata and viewer behavior -> Harbor's existing owners.
These requests do not complete the tasks or authorize execution.

<!-- markdownlint-disable MD013 -->
````text
I would choose an image from a gallery, by default it would use the gallery_944x1104 and I could chose the head or chest version if I wanted.  Then I'd need to decide which workflows to use (we can get into details later) as I might want to trigger multiple workflows.  We need to decide on the proper directory naming for how things do actually work as the initial testing we did wasn't what I wanted - so there is design work on that.  But assuming we get that sorted out, the workflows would be triggered - either using dynamic or static versions based on art.  It's sorta complicated in terms of how I first need to take the 944x1104 images and process them in 0_Edit, 1_Prime and 2_Studies - which we may need to adjust as we bring in 0_Edit officially.  Basically, all the 0_Edit prompts are defined to take in the images in the gallery which have backgrounds, people holding mugs, cups, purses, etc..., some images get expaned to full scenes with background, others change poses, outfits and such.   0_Edit is where I figured out how to take those images and get them ready.  There's a bit of work we need to do to sort out how 0_Edit, 1_Prime and 2_Studies may actually work to get better quality images through those initial phases to send into the next set of 3_xxxx, 4_xxxx phases.  Basically we need to revisit that so both the static and dynamic workflows will run the way I want.  So stepping back - we need to sort out how 0_Edit, 1_Prime and 2_Studies all work - given how things have progressed in the work I did with 0_Edit.  I would also say the initial work done to create 0_Edit did not achieve my goals and needs to be reset - but I need to get my manual prompts finalized in my workspace and THEN we can re-do all that.  Does this make sense.  We're not quite ready for the entire plan - but we do need to ensure we get the right focus on the setup of those 0, 1 and 2 phases of the process.

In an ideal world, the prompts in 1_Alpha could accomplish what happens in 0_Edit - in terms of being able to generate the images without having to go through a 0_Edit series of prompts.  But it may turn out that it's more efficient to use a 0_Edit, get one that is cleaner and send that into the 1_Alpha (which I realized I called 1_Prime before, but it's actually 1_Alpha/1_Prime and 1_Alpha/2_Bare and a few others).  Basically, there is some overlap between 0_Edit and what 1_Alpha is doing and I need to sort that out.  Meaning, if I can take an image from the gallery and generate the 1_Alpha images directly without having to go through an 0_Edit and we can get the proper poses from there - that's the most important.  0_Edit is there for me to take in images and try to see which of the ones in the gallery I like - BEFORE - I would send into 1_Alpha for "official" generation.  The 2_Studies also share some of what 0_Edit is doing in terms of hair, poses, head shots, and such.  So, first step is to settle on how those actually all work together and flow.  The important part is that in the existing 1_Alpha and 2_Studies we were taking in images from the gallery directly, with background, varying poses, sometimes head shots, etc... and the results did not always work to produce the images where it's trying to includes all the character specific traits in terms of hair color, makeup, figure as well as trying to extend the image, clean-up background, remove clothing so it doesn't bleed through etc... that's why I created 0_Edit and it has a series of sub-stages focused on testing all aspects - but it's general and uses existing outfit, hair color, etc... and doesn't apply the actual art specific changes.  Does this make sense - I'm sure it's somewhat confusing as it's also confusing to me and that's what we need to get sorted out.  BUT, I also need to go back to where I am working on all the 0_Edit workflow, get that cleaned up and then figure out how to bring all that back, deal with some of the legacy zz_Shots work and get to a point where it makes clear sense in what we're doing for 0_Edit "officially".

The 1_Prime should generate the image in a specific set of poses with all the art modifications.  This includes both the character specific bikini as well as bare and we'd want a series of poses.  Right now it's just A pose based, but I feel like it might need more - but that's  what we'll sort out.  The concept is that the character is in a studio background, proper lighting, we apply all the attributes/art to the incoming image (whether direct form the gallery - preferred - OR from the 0_Edit phase where we need to extend the background, remove the background, remove complex clothing, extend the entire image, etc...)  So the outcome of the 1_Alpha phase is we can pick the image(s) that we expect to use in the future phases where we apply more art (outfits, background, poses, weapons, magic effects, scenes, etc...).  Taking a gallery image into the more complex stages where we have so much more art was bleeding through existing background, objects in hands, making it difficult for poses, and not applying the hair color, body traits, eye color, etc... because the prompts were too much for the AI models to handle.  So that's how the 1_Alpha are targeted.

Some of the prompts have that context at the top of the templates, for example - C:\Soverign-Territories\soverign-territories\data\art\_templates\heroes\4_Wardrobe\armor-human.txt - expects an me to chose an A Pose in a bikini and it doesn't have all the prompts to deal with existing changes to background, clothing, etc.. so if I send in an image from the gallery, existing clothing, backgrounds, etc... bleed through into the generated image and not allowing it to fully render based on the art specifications. There is an existing documented approach - which needs to be revised based on this conversation and we can then finalize on how it SHOULD all work together.  When we're done with this Q&A let's re-review what we decided on and then what I need to get ready in the 0_Edit and 1_Prime workflows that I manually updated.  I'll get things cleaned up and ready.  Right now they are on the other machine in a secure location - so we'll need to discuss how I share them with you and whether you want the workflow.json or I need to pull out the prompt specifically.  Ideally, I can just get the workflow.json files copied over to a workspace on this machine for you to read and then we can remove a bunch of stuff I manually have been storing in git.

It should be focused on the 1_Alpha inputs and it's the optional area where I can play around with the 1_Alpha images to see which one I would prefer to pass into the next phases - or even choose some from 2_Studies to send in.

In an ideal world - 1_Alpha should be able to take a gallery image and generate the proper bikini and bare images.  BUT if I am having problems getting all the art specifications to apply due to what the gallery image is (which happens often with certain gallery images) I would first need to run through 0_Edit to get an image I like and pass that into 1_Alpha so it's focus is on forming the character properly with all the traits, pose and such.  So - it all depends on what the gallery image actually is.  Make sense?

Ideally each 0_Edit works indepently of the others - however, I did experiment with some 0_Edits that might just have a very simple prompt to take a previous 0_Edit and fix up one or two things - but those are more like custom/image specific prompts - maybe it's a final push to adjust the pose, remove a object in a hand that wasn't covered in the normal edit, adjust the skin tone, etc... I don't want to always have to go from edit-to-edit-to-edit and then finally to alpha.  But it all depends on what the output is from each run.  Sometimes I can run the 0_Edit 20 times and get one that is perfect.  Other times, I have one that's ALMOST perfect and it just needs a small edit before it's ready.  Other times, I might be able to just pass it to 1_Alpha and it does the final adjustments - that's all experimentation I need to do as I work on generating images.

It could be a combination of both.  Maybe I end up with a few standard edit prompts that are used to do final clean-up or maybe I need custom prompts, which I could do specifically in the ComfyUI and pull them back for that character.  It all depends on which workspace I am working in and whether or not it's a chosen character or a lower level card I am working on - but that's the complexity of the various comfyui workspaces we'll define and get setup as well.  Sorry for bleeding in more information, but the entire workflow process will work across multiple workspaces and each workspace has a defined purpose and the workflows in that workspace will differ as well.  But the general phases are important to understand.

Yes, we'd default to the golden image - but ultimately, I want to be able to bring back specific generated images into the image library under the Generated folder (with proper names and sub-folders as well) and be able to choose that one for specifc workflows.  So, really every workflow could have it's own specific workflow image and not just the golden.  I'd always first try the golden one, but if the output struggles to get what I want, then I might go back and pick a different one.  In the ideal world - the 1_Prime IS the golden image of that character, but sometimes I may need to pick a different one than the golden one.

What I have found is that using the bare image produces the best layers, wardrobe, scene, etc... why, because even with just a bikini - the bikini actually bleeds through into an outfit, like a backless dress, celestial armor, or other scenes - so it's actually the alpha bare that tends to get the best cards.

I need to pick the ones that would come back directly - because many generated aren't what I am looking for and if I generate 20, I may only get 1 that I really like so no need to bring them all back.  I might want a viewer to view them all and choose from there - instead of having to look at the filesystem version of the images and choose.  But I don't want to clutter the actual gallery with a bunch of copies of images I would just delete in ComfyUI output.

Yes, the 3_Layers are for me to be testing an image as well - but I think in most cases - I will generate several of them and possibly use them in the next phase of images.  Again, it all depends on whether the standard bare image works or I need to apply something in the studies or layer to use in the 4_ and beyond phases.

For the workspaces that don't have a defined character it would preserve their character so in the art it would say things like "same color hair", "same color eyes", etc.. but we may apply a standard bust or other figure adaptations that are more generic.  Once it's assigned to a character/card, then it'll have more explicit adaptations and we'd end up re-generating images.  I think that answers the question properly.

I'd want a default one for the workspace as a whole, but we should have all of those definitions available in case we want to adjust for a specific identity.  Meaning, maybe the identity I am working on needs longer and more slender legs than what we define and the general workspace definition isn't getting what I want.  But for the most part, I expect the general definitions per workspace are good enough for those identities - until they are assigned to a card.

I would actually probably assign it to the identity permantly - since we are keeping track of all of them already.  So if the identity needs an eye color change, hair color change, figure change - I could do that ahead of assigning to a card and would want that to carry forward into the art definition.  So, we can keep that outside of git - until I assign to a card and then it's part of data/art definitions for a character.  So we'd keep that in definitions on the B: drive where we have the galleries - and only get into the git repo when it's a character for a card.

It can be any of the attributes in the existing data/art schema that we can specify already.  We can get into the details of that when we are closer to the actual implementation - because I don't expect to apply ALL of those until I assign it to a card.  It would mainly be some very specific things I want to adjust ahead of assigning to a card.  I'm just trying to avoid assigning it to a card just to see if adjusting those work out.

By default, probably choose all poses but in some cases, just select the ones I want.  We can get more into that later as well - but it might be that I setup some collections of workflows to pick from so it's not always choosing them one-by-one if I don't want all.  But that'll probably be more clear when we define just how many workflows we have in 1_Alpha to run.

Yes - that's the basic concept.  At some point, I'd actually want everything to be dynamic - unless I am wanting to work in Comfy UI directly.  The main reason is that with dynamic we can adjust the output filename to include things like photo_id as part of the filename - so then I can track a generated image back to the actual original image that I am using.  In current state, I don't actually always remember which image was used to generate another image - and for what I have been doing that's fine.  But, it's easier to work in Comfy UI since it tiggers a batch of workflows easily and allow me freedom to see what's happening - adjust the prompt manually to see if we can improve things.  But long term that's not what I want.  Make sense?

If we track history separately, that's fine to keep track of the series of images used - as long as it's not overly complicated.

Just let me go ahead - sometimes it might be on purpose.  So not trying to overly complicate how things will be working - it's all based on what I see in the rendered output anyway.

I think I want to shift my focus into getting the 0_Edit and 1_Alpha workflows, prompts and any required art .json files re-aligned so they work.  Then we can move onto other more complex things.  So, one of my key steps is to step out of VS Code - go back to my 0_Edit and the 1_Alpha versions I did create and look at how we pull those back, create proper templates and art .json files to replicate what I am doing there.  We'll then re-generate all the statics workflows with the new 0_Edit and revised 1_Alpha workflows and we can then work more on these items.

With all this information, we need to update docs/plans and possible create a new ones and sunset old ones if needed so we have a clear set of prioirities related to the workflows and next steps.  I have the one we started for bringing things back - but as I mentioned at the start, we need to start that over as I totally revamped what I had for 0_Edit on the new machine once I could generate images faster and see how I needed to evolve things.  When I get the ComfyUI workspace setup on this machine and can point you there we can deal with how to bring them back.  Then we can deal with things like the "custom" workflows and sunset/remove the zz_Shots approach and come up with a better way to bring them back into the data/art templates, sets, .json instead of me writing the zz_shots they I was doing before.  But the zz_shots provided the way for me to bring custom prompts back for Copilot to analyze and then generate templates and art based on those.  So me manually writing prompts will still have a purpose - I just want it more incorporated into the actual phases instead of what was happening.  Does this all make sense?

Please pull, get the upstream - maybe harbor answered your question, maybe not - then you can commit all our work and push.  Then tomorrow I'll get the workspaces setup with what I consider the "latest version" of my 0_Edit and 1_Alpha workflows I curated by hand and we can figure out how to bring them back into the data/art properly - updating existing templates, adding more _sets and .json files to support them.  Then we can re-generate workflows and publish for Drakness as a starting point for me to verify.  Does that make sense in the concrete and immediate next steps for both you and me.
````
<!-- markdownlint-enable MD013 -->
