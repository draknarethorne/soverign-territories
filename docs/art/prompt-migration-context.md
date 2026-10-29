# Prompt migration: retained rationale and evidence

**Reviewed:** 2026-10-22. This is context, not another execution plan.
The [manual migration plan](../plans/2026-10-22-manual-prompts-to-art-library.md)
owns pending decisions and work. Existing generated outputs are unchanged.

## Pipeline and boundaries

Definitions describe reusable identity, race, wardrobe, cosmetics, motion and
environment facts. Assembly cards in `_sets` select definitions/components and
a template. The prompt generator resolves tokens and inheritance; workflows
then resolve engine templates, prompt-header denoise, input roles and selected
photos. Workspace configuration owns photo/input choices, not identity truth.
Candidates/shots/curated/finals preserve different degrees of manual work.
Only explicit final promotion with an input-role choice retargets later stages.

Use [art structure](../../data/art/README.md),
[template structure](../../data/art/_templates/README.md),
[prompt pattern](prompt-pattern.md), [tutorial](tutorial-art.md) and
[workflow guide](../../workflows/README.md) for the installed pipeline.
`angel-primes` is calibration work, not a card series. Generic reusable
definitions, narrower race/theme/hero pieces and `_sets` assembly are distinct.
Do not decompose beyond meaningful reuse or independently swappable concerns.

## What the previous prompt plans established

| Context | Retained meaning / boundary |
| --- | --- |
| First-shot rationale | Repeated edits can accumulate identity drift. A least-committed base with explicit body construction and later additive wardrobe was the hypothesis; no old P1/P2/P3 winner was accepted |
| P1 / P2 / P3 | Existing swimsuit Prime, NeutralBase skin-tone two-piece layer, direct BareBase. NeutralBase is not Bare. New manual Bare may replace the `1b` experiments after validation |
| P4 / dual-image | Conditional later face pass: generated bust plus original headshot. Tidy plan 4.4 owns this, not a requirement to implement multi-inputs now. A neutral pose-frame second reference was not selected |
| Close-up fidelity | A face/bust master should not depend solely on a tiny crop of a generated full-length body; test source/face-master alternatives if needed |
| Engine differences | Qwen was more forgiving for body/framing; FireRed sometimes improved detail but cropped partial sources. These are observations, not a permanent assignment of every job to one engine |
| FireRed lock | Current identity/framing prefix exists. Removing its framing lines was conditional on a matched full-body comparison; not approved merely by drafting a new template |
| Frames | The gray partial-body frame experiment and `flows.frame` were retired Oct 19. Preserve old files/history; no new frame generation or compulsory frame bakeoff |
| Feet and framing | State head-to-toe intent, missing-body continuation and feet grounded when that stage builds a full body. Footwear is data-driven. `FEET` was a proposed token, not permission to add it without mapping current pieces |
| Section order | Existing pattern guidance and actual templates differ. Earlier D2/D6 universal order proposals were not universally approved; evaluate the tested manual order before creating a replacement standard |
| Positive wording | Say the desired visible result. Explicit removal instructions can be valid; the old absolute avoidance of removal wording is not a ban on clearly specifying an edit |
| Negatives | FireRed has no separate negative prompt. Qwen negatives and per-piece negatives have different consumers. Do not assume one engine interprets the other engine's wording/settings identically |
| Seeds | Generation uses random seeds; a chosen final records/replays its seed/denoise/input. Do not reset a user's fixed `zz_Final` seed during regeneration/deployment |
| Sync | Missing derivatives/inputs after moves are a synchronization problem, not proof of a matcher/template fault. Run the supported library/input routine; do not introduce a duplicate `inputs sync` command |
| Late input selection | Render/pull status and source picks are finals-plan work. Do not silently replace chosen input photos when migrating prompts |

## Scoped render evidence: Oct 13, not accepted standards

- Angelica Alpha 2 Bare versus Bare Figure differed in how body, eyes and
  makeup were restated. Compare with matched engine, input, denoise and seed
  before claiming the wording is the cause. Preserve versus reset must be
  explicit per attribute, not inferred from a stage label.
- Four reported `1b` BareBase renders achieved the full-body A-pose but
  returned unwanted garments. This supports investigating outcome wording,
  not a claim that framing fixes solved the entire result.
- Heavy golden eye makeup was initially mistaken for glasses. Gold,
  luminous/glossy skin wording was a possible influence, not a proven cause.
  Audit all current hero skin descriptions and Bare eye/makeup inheritance;
  don't neutralize every identity based on a few images.
- Four Angelica `2b` celestial experiment cards used a dedicated correction
  because their declared denoise differed from the shared generated header.
  The workflow reads that header. This scoped correction was a trial, not
  rollout approval, and the Oct 22 direction leaves `2b` alone.
- Keep source photo, generated prompt, engine, seed, denoise, output and
  observed failures together. A face score is one diagnostic, not visual
  acceptance of the body, framing, clothing or skin.

## Current manual-source observations

At the Oct 22 review the directory contained 31 text files, including
`female_anatomy.txt`, `naming_workflows.txt` and `prime_org.txt`. This is a
dated inventory, not a frozen accepted set; the user can continue editing.
The edit variants group Background, Cleanup, Deluxe, Enhance and Full-body
intents, alongside Prime and Bare alternatives. In the Oct 22 follow-up the
user corrected Cleanup to `0c_Cleanup` and Angelical to Angelica, and confirmed
`0l_Lighting` is a future placeholder to build during prompt work. Those are
no longer open spelling questions. The `0a` placeholder and `Of` versus `0f`
Full names still need resolution before machine paths are created; this does
not authorize editing the user's manual source.

Manual labels include Pose, Background, Lighting, Camera, Result, Likeness,
Wearing, Hair, Makeup, Eyes, Lips, Expression and several body/detail labels.
A label can recur in a critical block and a descriptive block. Map each
occurrence by meaning: a repeated Hair label may distinguish a critical color
from a hairstyle, and Eyes may distinguish color from gaze. A mechanical
one-label-to-one-token replacement would lose that distinction.

`female_anatomy.txt` is a 312-line AI-assisted working vocabulary, including
camera, facial structure, expression, hair, skin/finish, makeup, body/pose,
lighting, wardrobe/materials, hands, gaze and environment. Some statements
combine several existing data concerns. It is neither an accepted identity
definition nor a list to import wholesale. Select useful content, map
existing fields first, split independent concerns and review reuse scope.
Keeping an original note does not approve every phrase in it.

## Documentation ownership

Current work: the migration plan; source/input picks and missing renders:
[finals plan](../plans/2026-10-09-finals-and-mvp.md); conditional two-image pass:
[classification/tidy plan](../plans/2026-10-11-tidy-junk-organise.md);
library refresh/near-duplicate decisions:
[upkeep plan](../plans/2026-10-22-library-upkeep.md).
The retired source records retain complete original discussions and historical
test instructions, but no longer compete as active migration checklists.
