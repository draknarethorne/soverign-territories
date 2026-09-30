# Prompt Pattern — Hero Card Art

One consistent block order for every stage's prompt, so results are predictable and you copy **one
template per stage** and only swap bracketed values per hero. Works with the Qwen / FireRed / Flux
img2img flows in [`workflows/SovereignTerritories/`](../../workflows/SovereignTerritories/README.md).

> Your existing prompts already give solid output and mostly follow this order — the refinements
> below are **incremental** (split background out, add a preserve block, formalise wardrobe slots),
> not a revamp.

## Golden rules

1. **One prompt = one stage.** Refer to the incoming image; describe ONLY what changes.
2. The **reference-fidelity** line is mandatory on every edit/final prompt — it anchors face, body, hair.
3. Pull palette, eye, and class from the hero's **card JSON** (`art.palette`, `class`, `element`).
4. Keep the block order **identical** across heroes/stages → consistent behaviour.
5. **Blank line between blocks** is your delimiter (keep doing this — it works).
6. Negatives = shared **baseline** + **stage-specific**; never negate something the outfit intentionally has.
7. `[BRACKETS]` = per-hero values. Copy the template, find/replace, done — don't rewrite structure.

## Block order (positive prompt)

1. **Camera & quality** — realism, shot type, lens/focus (85mm, sharp, soft DoF). *(No background here.)*
2. **Background / Environment** — studio backdrop for A-pose/edit intermediates; the in-world scene for final.
3. **Shot style / energy** — editorial / glamour / mid-motion *(optional; edit & motion stages)*.
4. **Reference fidelity** — "Maintain strict fidelity to the reference image's facial likeness, bone
   structure, body shape, proportions, eye colour and hair colour."
5. **Preserve** — for intermediate edits only: "Maintain the existing outfit/hairstyle expressly."
6. **Wardrobe** *(A-pose / Edit)* — one blank-line group per garment slot (below).
7. **Face & detail overrides** — expression, lips, nails, eyes (`[CAST EYE]` glowing when casting), breeze.
8. **Pose / motion** — the movement/pose adjustment (short lines).
9. **Spell VFX** *(final only)* — magic, glow around hand/weapon.

### Wardrobe slots (block 6) — keep the blank lines

```
Wearing [TORSO / main piece] in [PRIMARY] with [ACCENTS], [coverage notes].

Arms: [bracers / pauldrons / gauntlets, or none].

Jewelry: [necklace / earrings / rings / piercings] in [ACCENTS].

Back: [cape / cloak / wings, or none].

Legs & feet: [greaves / stockings / footwear] in [PRIMARY]/[ACCENTS].

Holding [WEAPON] - [material, detail, which hand].

Overall, [aesthetic] aesthetic.
```

## What each stage references / preserves / changes

| Stage | Reference | Preserve | Change | Background | Template |
| --- | --- | --- | --- | --- | --- |
| **A-pose** | source photo | likeness | build full base + bikini underlayer | studio | [`_TEMPLATE_APose.txt`](../../prompts/_TEMPLATE_APose.txt) |
| **Head/close-up** | A-pose | face + hair | framing (chest-up) | studio | your `_qwen_a_head.txt` |
| **Hair** | A-pose | outfit + face + body | hairstyle only | studio | [`_TEMPLATE_Hair.txt`](../../prompts/_TEMPLATE_Hair.txt) |
| **Pose/Motion** | A-pose (chosen hair) | outfit + hair + face | pose/motion only | studio | [`_TEMPLATE_Pose.txt`](../../prompts/_TEMPLATE_Pose.txt) |
| **Edit** (armor/clothing) | A-pose (bikini base) | face + body + hair | apply wardrobe + weapon | studio | [`_TEMPLATE_Edit.txt`](../../prompts/_TEMPLATE_Edit.txt) |
| **Final** | near-final | everything | scene + spell + pose/wind | in-world | [`_TEMPLATE_Final.txt`](../../prompts/_TEMPLATE_Final.txt) |

## Section cues — how to help the model parse (your question)

- **Blank lines are your main delimiter** — keep them; they already work.
- **Lead each block with its natural keyword** — `Background:`, `Wearing`, `Arms:`, `Jewelry:`,
  `Holding`, `Pose:`, `Eyes`. These double as soft section labels the model understands **without**
  risking rendered text. (Qwen-Image-Edit follows instruction-style phrasing well.)
- **Don't over-label.** Avoid ALL-CAPS tags on every line — too many can confuse the model or bleed
  into the image. A short lead-in on Background / Wardrobe slots / Pose / Eyes is the sweet spot.
- **Test one change at a time.** e.g. split Background first, run it, confirm it's still clean, then
  add slot lead-ins. Don't change five things at once or you won't know what helped.

## Negative baseline (+ stage extras)

`extra people, extra limbs, extra digits, extra feet, text, watermark, logo, studio equipment`

- **Edit / Hair / Pose** often add: `crowns, head gear, pauldrons, shoulder armor` —
  **but remove `pauldrons, shoulder armor` when the outfit is meant to have them** (as your Armor_Bone does).
- **Motion** often adds: `mismatched footwear`.
- **Final** adds: `altered face, altered armor, altered hairstyle, duplicate or second weapon`.

## Migrating your existing `.json` prompts

They already follow most of this. To standardise: lift each positive prompt into the matching
template, pull `background` out of the camera line into block 2, group wardrobe into the slots above,
and replace hero specifics with `[BRACKETS]`. Then per new hero you copy the template and find/replace
from their card JSON — no rewriting.
