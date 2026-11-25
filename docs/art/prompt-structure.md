# Prompt structure and shared vocabulary

This is the working structure for source-bound art prompt migration. It
guides new and revised templates; it does not assert that every existing
template has been migrated. The [art data reference](../../data/art/README.md)
owns the data layout and generator contract. The
[workflow plan](../plans/2026-10-22-manual-prompts-to-art-library.md)
owns source comparisons, pending changes and acceptance gates.
The [omissions ledger](prompt-migration-omissions.md) records known
adaptations, exclusions and source comparisons still to do.

## Purpose and ordering

The user organizes prompts to establish the stage's goal early, cascade
from the overall composition into changes and identity details, and sometimes
repeat a critical instruction at the end as an anchor. This is an observed
working approach, not a measured guarantee about Qwen attention or output.
Compare order and repetition against the selected manual source and the
purpose of each phase; do not mechanically force all phases into one order.

For the currently migrated Edit and Alpha reference pilots, the positive
prompt normally proceeds through:

1. Pose or selected view.
2. Background, separately selected lighting and photography.
3. Camera or framing when selected.
4. The edit task and intended result.
5. Selected identity details, body and likeness.
6. Optional outfit, footwear and appearance details.
7. An optional final preservation anchor where the assembly selects one.

The Edit and Alpha templates are separate: their tasks, source images and
optional sections are not identical. A deliberate repeated instruction must
agree with the earlier instruction and the selected changes. Do not copy
an anchor into every prompt or describe model behavior as proven without
controlled comparisons and visual review.

## Selection and reuse

- The assembly selects pieces for its purpose; a missing optional section
  should not invent an outfit, pose, makeup or other instruction.
- Use `WEARING` when an outfit is explicitly preserved, adapted or replaced.
  Leave it absent when the edit is not directing clothing. State replacement
  and relevant source-remnant negatives only when replacement is intended.
  An outfit-neutral Edit may instead select `RESULT_OUTFIT` to preserve
  incoming clothing if present without directing the model to add clothing.
- Prefer reusable pose, background, lighting, camera, appearance and
  wardrobe pieces across stages when their actual meaning and
  `compatibleStages` agree. A genuinely stage-specific policy can remain
  scoped. Source color-only and source fabric-and-color are different choices.
- Keep background and lighting independently selectable where the
  migrated assembly supports it. Older bundled pieces remain available to
  existing consumers until their transition is reviewed.
- Place source-versus-identity choices in the assembly and selected pieces.
  Preserve source details unless a particular workflow selects a change.
- The ordered Edit and Alpha shells can select `SKIN_EDIT` for an independent
  skin finish. Select the source or identity tone separately and avoid
  conflicting finish or tone instructions.
- Their optional `GESTURE` slot emits an independently selected hand detail
  after the pose. Choose a compatible view and expression; a gesture must not
  contradict a whole-pose hand placement or held-item cleanup.
- The optional `NECK_SHOULDERS` slot selects a neck, collarbone or shoulder
  detail independently of the overall frame. Choose it only when compatible
  with the selected identity, pose, clothing and framing.
- A component's negatives must agree with the intended positive change,
  chosen pose, outfit and framing. Intentional repetition is not a license
  to introduce contradictory instructions.
- Keep negative prompts concise and focused on important failure modes.
  Avoid accumulating overlapping exclusions merely because they appear in
  different pieces or in a source. The user observed poorer results from
  overloaded negatives; this is not a controlled performance measurement.
  The ordered Edit and Alpha reference shells deduplicate exact component
  negative phrases in template order, without splitting phrases or changing
  positive anchors. Static template negatives and other shells are not
  automatically deduplicated.

`components.<slot>` names become template tokens such as `{{WEARING}}`.
The [field vocabulary](../../data/art/_schema/field-vocabulary.json)
governs content fields inside pieces, not every possible template slot.
Piece `tags` are metadata, not prompt substitutions; some edit-task tags
also select a family directory. Check existing defaults, aliases, optional
lines and negative-token behavior before adding or merging names.
In particular, identity `FIGURE` and motion `BODY`, and Studies `VIEW` and
motion `POSE`, are not automatically interchangeable.

## Current coverage and audit

All 22 current generic Female Edit assemblies now select the ordered
[`edit-cleanup-human.txt`](../../data/art/_templates/heroes/0_Edit/edit-cleanup-human.txt)
shell. The original four Deluxe and two three-quarter pose pilots select their own
identity, environment, framing and optional footwear pieces and deliberately
repeat their face-preservation instruction at the end. This is fixture-tested
source adaptation, not visual acceptance. Legacy templates and generated
files remain in place.
The Background Bust audition selects a separate neutral figure detail rather
than an entire body profile; its source comparison remains open.
Where a selected figure detail sits between identity hair and eye details,
the ordered Edit and Alpha shells split the generated critical-details block
around it. Other templates and cards without that selection retain their
existing block. Literal custom blocks must explicitly provide their own
post-detail content.

Generic Female Prime and all 15 current outfit assemblies use
[`alpha-reference-human.txt`](../../data/art/_templates/heroes/1_Alpha/alpha-reference-human.txt).
The shell accepts gaze separately from eye detail and expression. The 14
source-inspired auditions select camera gaze; the two physique-preserving
outfit auditions do not select a new gaze.
The older Prime-outfit reference template remains in place for compatibility;
other Alpha templates still have consumers. Named Prime, footwear and experimental/bare families require
separate source, identity, default-input and negative review before changing
them; generic Female is not a substitute for named character data.

A separate Alpha gown replacement audition explicitly discards the previous
garment design while reusing its colors and fabric if present. It is an
alternative to the existing adaptation, not proof that garment remnants are
eliminated.

Two separate Alpha footwear auditions preserve the selected Prime, its
clothing, identity and setting while changing footwear. A minimal foot
adjustment is allowed for the selected footwear. They use the configured
Prime input rather than the legacy Bare input and do not replace the legacy
footwear workflows. Their inputs and visual results remain unverified.

The first later-phase inventory shows different, purposeful emphasis:

| Phase | Current structure to review |
| --- | --- |
| `2_Studies` body and head | Photography and background precede reference preservation; head adds framing/view and eye details. |
| `2_Studies` hair | Preservation precedes the selected hair change and its end placement. |
| `3_Layers` | Existing pose templates are shared with Alpha; changes affect both. |
| `2_Studies/motions` | Body, head, gaze and expression lead into the selected pose near the end. |
| `4_Wardrobe` | Preservation and outfit/gear assembly lead to the selected aesthetic and eyes. |
| `5_Scenes` | Identity and outfit precede pose/effects and the environment. |

These are a bounded structural inventory, not completed per-card or
source-fidelity audits. Preserve phase-specific semantics when each family
is selected for work. Older comparative guidance remains in
[Prompt Pattern](prompt-pattern.md), not a second universal ordering rule.

The newer later-phase shells are not all equivalent to the ordered Edit and
Alpha vocabulary. Wardrobe replacement now selects `VIEW`, `BACKGROUND` and
`LIGHTING` independently. Its two current auditions select a standing A-pose
with empty hands and neutral studio; other selections need their own compatible
pieces and review. Studies hair preservation selects a hair change while
retaining the source pose and setting, and its header no longer requires an
A-pose. Its two current workflows still select the configured Prime input.
These are not proof that arbitrary source poses are visually preserved. The
later-phase shells also
use different negative layouts; compare selected pieces and actual outputs
before adding slots or changing shared consumers.

Two separate Layers auditions use
[`layer-preserve-reference-human.txt`](../../data/art/_templates/heroes/3_Layers/layer-preserve-reference-human.txt)
to retain the incoming pose, appearance, setting and lighting while selecting
an outfit. Their provisional graph input is the configured Prime, not the
legacy Bare default; exact per-workflow role overrides retain that selection
on creation and input reset. The configured filename still must be available
in the workspace's input folder before rendering.
They do not replace the A-pose construction templates or prove visual
acceptance.

Three separate generic body Studies auditions use
[`pose-direction-reference-human.txt`](../../data/art/_templates/heroes/2_Studies/pose-direction-reference-human.txt)
for back, profile and three-quarter views. They preserve identity and incoming
clothing without requiring a replacement expression. The original
Studies template and reference workflows remain intact. These are unrendered
alternatives, not an accepted replacement for the existing views.

Four separate generic head auditions use
[`head-direction-reference-human.txt`](../../data/art/_templates/heroes/2_Studies/head-direction-reference-human.txt)
to retain the selected view and incoming expression. The profile does not
require both eyes or a camera-facing gaze; the frontal and three-quarter views
select camera gaze. They are unrendered alternatives, not replacements for
the legacy head references.

Two separate generic hairstyle auditions use
[`hair-preserve-reference-human.txt`](../../data/art/_templates/heroes/2_Studies/hair-preserve-reference-human.txt)
to lead with pose and environment preservation, then select a hairstyle and
anchor identity and outfit. They retain source hair colors, use concise
negatives and select the configured Prime input through workflow-specific
overrides. They are unrendered alternatives; older hairstyle graphs remain.

Two generic Wardrobe auditions use
[`outfit-replace-reference-human.txt`](../../data/art/_templates/heroes/4_Wardrobe/outfit-replace-reference-human.txt)
to replace a selected source photo's outfit and background with a selected
studio look, rather than assuming an underlayer. Their selected view replaces
the incoming pose; background and lighting are independent choices. They select the configured
photo role and retain identity attributes. These auditions are not replacements
for the legacy Wardrobe templates, and outfit/background removal is not
visually verified.

Two generic Scene auditions use
[`scene-replace-reference-human.txt`](../../data/art/_templates/heroes/5_Scenes/scene-replace-reference-human.txt)
to lead with the selected pose and environment, replace the previous setting
and outfit, then anchor source identity. An opt-in eye-effect piece preserves
the source iris color around the selected glow. They use the configured photo
role and do not replace the legacy scene templates or establish visual results.
The shell also accepts optional independent `LIGHTING` and `LIGHTING_NEG`
selections; the existing two cards do not select them. Their backgrounds
already describe light, so any added lighting must be compatible with the
selected environment and realm.

Three generic motion-study auditions use
[`motion-preserve-reference-human.txt`](../../data/art/_templates/heroes/2_Studies/motion-preserve-reference-human.txt)
to lead with the selected motion and expression while retaining the incoming
identity, outfit and setting. Their exact workflow overrides select Prime; the
twirl's separate motion piece does not assume a skirt or drape. These are
unrendered alternatives and do not replace the existing motion workflows.

## Verification and release

Fixture-render affected assemblies without overwriting generated outputs.
Check order, selected and omitted sections, deliberate anchors, identity
overrides, per-piece negatives, denoise and paths; test shared consumers for
unchanged behavior. Validate art data and run the applicable quality gates.
Prompt generation, workflow creation, workspace publication, rendering and
human visual acceptance are separate actions and evidence. Preserve manual
sources and existing reference-job bindings during transitions.
