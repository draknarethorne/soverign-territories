# Prompt Pattern — Hero Card Art

One consistent block order for every stage's prompt, so results are predictable and you copy **one
template per hero** and only swap the bracketed values. Works with the Qwen / FireRed / Flux img2img
flows in [`workflows/SovereignTerritories/`](../../workflows/SovereignTerritories/README.md).
Pipeline context: [`comfyui-art-pipeline.md`](comfyui-art-pipeline.md).

## Golden rules

1. **One prompt = one stage.** Refer to the incoming image; describe ONLY what changes.
2. The **reference-fidelity** line is mandatory on every edit/final prompt — it anchors face, body, and hair.
3. Pull palette, eye, and class from the hero's **card JSON** (`art.palette`, `class`, `element`).
4. Keep the block order below **identical** across heroes/stages → consistent behaviour.
5. Negatives = a shared **baseline** + **stage-specific** extras.
6. `[BRACKETS]` = per-hero values. Copy the template, find/replace the brackets, done — don't rewrite structure.

## Block order (positive prompt)

1. **Scene & camera** — realism, shot type, background, lens/focus (85mm, sharp, soft DoF).
2. **Shot style / energy** — editorial / glamour / mid-motion *(optional, mostly edit stages)*.
3. **Reference fidelity** — "Maintain strict fidelity to the reference image's facial likeness, bone
   structure, body shape, proportions, eye colour and hair colour."
4. **Wardrobe** — the outfit / armor / weapon being applied or (final) kept.
5. **Accessories** — jewelry etc. (short lines).
6. **Footwear**.
7. **Face & detail overrides** — expression, lips, nails, eyes (`[CAST EYE]` glowing when casting), breeze.
8. **Pose / motion** — the movement/pose adjustment (short lines).
9. **(Final only) Spell VFX & environment** — magic, glow, background scene, atmosphere.

## How much to describe, per stage

| Stage | Reference | Describe | Template |
| --- | --- | --- | --- |
| **A-pose** (build base) | source face/photo | **fully** (body, skin, base look) | your `_qwen_a_pose.txt` |
| **Edit** (hair / armor / clothing) | the A-pose | **only** the new garment/hair/weapon + overrides | [`_TEMPLATE_Edit.txt`](../../prompts/_TEMPLATE_Edit.txt) |
| **Final** (scene) | near-final image | **only** pose/wind + spell + environment + overrides | [`_TEMPLATE_Final.txt`](../../prompts/_TEMPLATE_Final.txt) |

## Per-hero bracket values (from the card JSON)

`[HERO]` `[ELEMENT]` `[CLASS]` `[PRIMARY]` (e.g. Midnight Violet) `[ACCENTS]` (Vibrant Amethyst,
Polished Silver) `[EYE]` `[CAST EYE]` (glowing amethyst) `[WEAPON]` `[SPELL VFX]` `[ENVIRONMENT]`
`[OUTFIT]` `[HAIR]` `[LIP]` `[NAIL]`.

## Negative baseline

`extra people, extra limbs, extra digits, extra feet, text, watermark, logo, studio equipment`

- **Edit** adds: `crowns, head gear, pauldrons, shoulder armor` (when unwanted).
- **Final** adds: `altered face, altered armor, altered hairstyle, duplicate or second weapon`.

## Migrating the existing `.json` prompts

Your Drakness `.json` prompts already follow most of this order. To standardise: lift each positive
prompt into the matching template, replace hero specifics with brackets, and keep the block order.
Then per new hero you copy the template and find/replace the brackets from their card JSON — no
rewriting.
