# 2026-10-22: manual prompt migration into reusable art data

**Status:** active (design and migration audit approved; no asset migration applied)

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
  Document compatibility/guards per stage and align with rendering R16.
- [ ] **P1 ai** P12 Define promoted-output directory structure for selected
  generated images so Gallery lineage remains clear by stage and recipe while
  preserving existing identity-core/original boundaries.

## Oct 26 first shared `0_Edit` slice

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
