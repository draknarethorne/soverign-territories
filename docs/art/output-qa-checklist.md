# Output QA Checklist — Historical Prompt Cues

This checklist preserves observations from earlier prompt experiments; it is not a specification
for every hero or stage. The active manual prompt migration is still in progress, so verify each
cue against the current card, generated prompt, and intended keep/reset behavior before changing
data. Check values against the hero's identity rather than assuming the Drakness-specific examples
below apply universally. Companion context: [`prompt-pattern.md`](prompt-pattern.md) and the
[active migration plan](../plans/2026-10-22-manual-prompts-to-art-library.md).

## Identity & consistency

| Improvement | Watch for in the render | Lever if off |
| --- | --- | --- |
| Reference fidelity line | Face, body, and hair match the incoming image | Lower denoise; keep the fidelity line |
| Eye-colour persistence | Eyes retain the value specified for this hero and stage | Check the identity and stage intent first; use only approved, hero-appropriate wording |
| Figure persistence | Figure matches the intended preserve/reset behavior for this stage | Check the source card and current migration decision; do not assume every stage preserves the same figure |
| Skin and figure continuity | Matches the hero's identity and the stage's preserve/reset intent | Confirm which source/card owns the value; do not assume a shared skin tone or figure |

## Makeup & grooming (the "catwalk makeup" ladder)

| Improvement | Watch for | Lever if off |
| --- | --- | --- |
| A-Pose makeup behavior | Matches the approved makeup intent for the current Prime/Bare prompt | Check the migration plan and current generated prompt before changing the reset |
| Eyeshadow per outfit | Matches the intended look for this hero and card | Adjust the current makeup source only after checking stage behavior |
| Lipstick (historical Drakness examples) | The selected look matches the current card and hero palette | The Light Violet/Deep/Red examples were outfit-specific, not universal rules |
| Toenails (when visible) | Matches the card's footwear and grooming intent | Check the current card and crop; this is not a requirement for every stage |
| Blush + brows | Soft natural blush, groomed brows at base | A-Pose makeup line |

## Expression & pose

| Improvement | Watch for | Lever if off |
| --- | --- | --- |
| **Mouth state named** | Matches purpose: parted (editorial), softly together (Gown/regal), hint of teeth (High) | Set the mouth words in that file |
| **Body/head/gaze orientation** | Real angles (3/4, over-shoulder, profile) — **not flat forward** | Name concrete angles; **drop "face focused on camera"** |
| Forward-lock removed | Turned-head poses actually turn | Remove any "Face remains focused on camera" line |
| Glamour line | Long neck, shoulders back, contrapposto, pointed toes | Add a Glamour-boosters phrase |

## Outfit & scene

| Improvement | Watch for | Lever if off |
| --- | --- | --- |
| Background split | Clean **light-grey studio backdrop** (baseline stages) | Keep Background on its own line |
| Wardrobe slots | Every piece present (torso, arms, jewelry, back, legs, weapon) | Check the slot is filled in that file |
| Outfit movement (Gown) | Hem / slit **sways with the step** | Add a movement phrase |
| Outfit-aware details | Required armor pieces are present and unintended pieces are absent | Check the current outfit/card and its applicable negatives |

## Cleanliness (negatives)

| Improvement | Watch for | Lever if off |
| --- | --- | --- |
| Text/logo lock | **No rendered text, watermark, or logo** | Negative already has `text, wording, watermark, logo` |
| Hands | Clean hands, five fingers | Negative has `deformed hands, extra digits`; lower denoise |
| Catwalk dedup | (prompt cleanliness — removed a doubled walk block) | — |

## Pipeline / stage

| Improvement | Watch for | Lever if off |
| --- | --- | --- |
| Baseline = photoreal | Grey studio renders look like a **real photo** (not fantasy) | Keep fantasy out of baseline |
| Stage-appropriate effects | Glow and magic match the intended scene and card | Do not assume a separate Fantasy stage exists; follow the current template/card |
| Dynamism | Variety across runs | **Roll the seed**; raise denoise; lower CFG a notch |
