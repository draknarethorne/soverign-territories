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

Group names match your `Drakness_Qwen_<group>` / `Drakness_X_<group>` workflows. Templates live in
[`prompts/_templates/`](../../prompts/_templates/); per-hero prompts go in `prompts/<Hero>/`.

| Group | Reference | Preserve | Change | Background | Template |
| --- | --- | --- | --- | --- | --- |
| **X_Pose** (A-pose base) | source photo | likeness | build full base + figure + bikini underlayer | studio | [`_TEMPLATE_Pose.txt`](../../prompts/_templates/_TEMPLATE_Pose.txt) |
| **X_Head** (close-up) | A-pose | face + hair | framing (chest-up) | studio | [`_TEMPLATE_Head.txt`](../../prompts/_templates/_TEMPLATE_Head.txt) |
| **Hair** | A-pose | outfit + face + body | hairstyle only | studio | [`_TEMPLATE_Hair.txt`](../../prompts/_templates/_TEMPLATE_Hair.txt) |
| **Motion** | A-pose (chosen hair) | outfit + hair + face | pose/motion only | studio | [`_TEMPLATE_Motion.txt`](../../prompts/_templates/_TEMPLATE_Motion.txt) |
| **Clothing** | A-pose (bikini base) | face + body + hair | apply gown/dress | studio | [`_TEMPLATE_Clothing.txt`](../../prompts/_templates/_TEMPLATE_Clothing.txt) |
| **Armor** | A-pose (bikini base) | face + body + hair | apply armor + weapon | studio | [`_TEMPLATE_Armor.txt`](../../prompts/_templates/_TEMPLATE_Armor.txt) |
| **Fantasy** *(optional, pre-final)* | photoreal near-final | face + outfit + hair + pose | add fantasy makeup + glowing eyes + subtle magic | cream / soft gradient | [`_TEMPLATE_Fantasy.txt`](../../prompts/_templates/_TEMPLATE_Fantasy.txt) |
| **Final** | near-final | everything | scene + spell + pose/wind | in-world | [`_TEMPLATE_Final.txt`](../../prompts/_templates/_TEMPLATE_Final.txt) |
| **Weapons** *(utility)* | — | — | a standalone weapon prop (multi-image ref) | plain | [`_TEMPLATE_Weapons.txt`](../../prompts/_templates/_TEMPLATE_Weapons.txt) |
| **Background** *(utility)* | — | — | a standalone scene plate | — | [`_TEMPLATE_Background.txt`](../../prompts/_templates/_TEMPLATE_Background.txt) |
| **Pets** *(utility)* | — | — | a summon/companion (multi-image ref) | plain | [`_TEMPLATE_Pets.txt`](../../prompts/_templates/_TEMPLATE_Pets.txt) |

## Craft notes & theme alignment

Improvements from reviewing the Drakness prompts — apply these for more consistent output:

- **Baseline = photoreal "catwalk" glamour.** Every cream-background stage (Pose, Hair, Motion,
  Clothing, Armor) should read like a **real supermodel photo** of the hero in the outfit -
  **natural, minimal makeup** (lips, nails, eye colour only; no heavy eyeshadow/blush). The goal is
  to judge the wardrobe and pose, not the fantasy. Default lips/nails to a **light** tone (e.g. Light
  Violet); use Deep or Red only when you intentionally match a darker outfit.
- **Makeup ladder.** The A-Pose is a **bare-face reset** (natural lips + a light `[ACCENT]` eyeshadow
  wash) so a heavily-made-up source photo doesn't leak through. Each outfit then adds a **`Makeup:`**
  line - eyeshadow matched to the feel (soft shimmer for light looks, smoky for dark armor). Fantasy /
  Final carry the heaviest makeup + glowing eyes.
- **Blush compounds; eyeshadow & lipstick swap.** This is the key rule. **No stage resets blush**, so it
  *accumulates* down the chain — a noticeable base flush deepens into over-rouged cheeks by the Final.
  Keep the **A-Pose blush barely-there** ("only the faintest hint of natural blush") and add
  over-rouged terms to the negative. Eyeshadow and lipstick are **replacements** — the last stage that
  names them wins — so escalating A-Pose "light wash" → Armor "smoky" is *replacing*, not stacking, and
  is safe. Introduce real blush only at the **Fantasy/Final** stage, where it's intentional.
- **Hair & Motion carry makeup from the incoming image — keep it that way.** Hair stages set **no**
  makeup (good); Motion sets no blush/eyeshadow (a few set lipstick, which merely swaps). Don't add a
  `Makeup:` line to Hair/Motion — they should inherit the A-Pose face so nothing compounds before the
  outfit stage. (`Kiss` deliberately uses Bright Red lipstick — a palette deviation, fine for that shot
  only.)
- **Nails = fingernails *and* toenails.** Toes show in open-toed heels (the A-Pose wears them), so set
  both at the A-Pose and restate per outfit; harmless to state under boots (just won't show).
- **Fantasy comes at the end.** Eyeshadow, blush, glowing eyes, necrotic glow, and any painterly
  treatment go in the optional **Fantasy** pass and/or the **Final** scene - never the baseline.

- **Set the figure once, at A-pose.** Define bust/waist/hips/legs/skin in `X_Pose` only. Downstream
  edits should **preserve** proportions (via the fidelity + "maintain outfit" lines), not re-issue
  "enhance breasts" — re-sculpting downstream fights the fidelity line and drifts the body.
- **Don't duplicate blocks.** Qwen reads instructions once; a repeated pose block (seen in Motion) adds
  nothing and can confuse. One block each.
- **Natural language, no weights.** Qwen-Image-Edit follows plain sentences — skip SD-style `(())`
  weighting or `:1.2` syntax.
- **Always negate rendered text.** Keep `text, wording, watermark, logo` in every negative (card art).
- **One canonical eye string per hero** (from card `art.palette.eyeColor`) — reuse it verbatim across
  stages so eyes stay consistent.
- **Theme alignment (Drakness = Darkness / Necromancer / Dark Elf):**
  - *Skin* — "very tan" doesn't fit a Dark Elf; consider a **dusky / ashen** or **pale gothic**
    complexion (your call; set it once at A-pose).
  - *Render* — the photoreal "fashion photography" framing is great for consistent A-pose/edit plates,
    but the **Final** card may read better with a light **cinematic dark-fantasy / painterly** cue.
  - *Motifs* — weave the same cues everywhere: amethyst necrotic glow, gothic filigree, skull accents,
    drifting shadow/smoke. Keeps the set feeling like one character, not a fashion shoot.


## Section cues — how to help the model parse (your question)

- **Blank lines are your main delimiter** — keep them; they already work.
- **Lead each block with its natural keyword** — `Background:`, `Wearing`, `Arms:`, `Jewelry:`,
  `Holding`, `Pose:`, `Eyes`. These double as soft section labels the model understands **without**
  risking rendered text. (Qwen-Image-Edit follows instruction-style phrasing well.)
- **Don't over-label.** Avoid ALL-CAPS tags on every line — too many can confuse the model or bleed
  into the image. A short lead-in on Background / Wardrobe slots / Pose / Eyes is the sweet spot.
- **Test one change at a time.** e.g. split Background first, run it, confirm it's still clean, then
  add slot lead-ins. Don't change five things at once or you won't know what helped.

## Figure & glamour phrasing (tasteful equivalents)

Keep the art-direction intent (attractive, curvy, glamorous, revealing fantasy wardrobe) with
professional wording. Swap overtly explicit lines for these - the model still leans the same way and
the instruction isn't dropped:

| Intent | Instead of | Use |
| --- | --- | --- |
| Fuller bust | "enlarge / enhance her breasts" | full, hourglass figure; generous bust, softly emphasized |
| Visible detail | "nipples hard" | thin, form-defining fabric *(or omit)* |
| Revealing top | "breasts exposed / uncovered", "cleavage exposed" | plunging, low-cut neckline; bold décolletage |
| Revealing overall | "skimpy, hips bare" | revealing, high-cut design; bare midriff and high leg |
| Alluring look | "seductive", "come-to-me eyes and lips" | alluring, confident smile; an inviting gaze |
| Alluring hand | "hand in erotic / seductive position" | free hand posed gracefully at her hip; an elegant, alluring gesture |
| Sultry brows | "brows sensual" | expressive, sultry brows |
| Glamour pose | "back arched, hips swayed, leaning forward" | *keep - standard contrapposto / glamour posing* |

Fine to keep as-is (standard fantasy art): bare midriff, high slit, low-cut, bikini armor, full
figure, long slender legs, hourglass, seductive / sultry / alluring, contrapposto poses.

## Negative baseline (+ stage extras)

`extra people, extra limbs, extra digits, deformed hands, extra feet, recolored eyes, blue eyes,
green eyes, brown eyes, flat chest, small bust, text, wording, watermark, logo, studio equipment`

- **Edit / Hair / Pose** often add: `crowns, head gear, pauldrons, shoulder armor` —
  **but remove `pauldrons, shoulder armor` when the outfit is meant to have them** (as your Armor_Bone does).
- **Motion** often adds: `mismatched footwear`.
- **Final** adds: `altered face, altered armor, altered hairstyle, duplicate or second weapon`.

## Persistence anchors (make attributes stick)

Some attributes drift when the model redraws (the bust / eye-colour problem). Lock them:

- **Restate** the critical attributes (eye colour, bust/figure, skin) in every edit - keep them
  **last** so they're the final word.
- **Negate the off-values** (strongest lever): `recolored eyes, blue eyes, green eyes, brown eyes`
  keeps violet; `flat chest, small bust` keeps the figure. Baked into every template negative.
- **Lower denoise** when you can - less redraw means more of the reference persists.

## Glamour boosters (sprinkle into pose / expression blocks)

Concrete phrases that add glamour without changing the wardrobe:

- **Gaze:** chin slightly down, eyes up to camera (model gaze); an inviting, confident look.
- **Line:** long neck, shoulders back, chest lifted; a confident S-curve / contrapposto; weight on
  the back leg; pointed toes.
- **Detail:** hair swept over one shoulder; slightly parted lips; crisp catchlights in the eyes.
- **Light:** soft rim / back light for a glamour edge; a faint dewy skin sheen.
- **Energy:** mid-motion, caught candidly; relaxed but poised.
- **Mouth (always name it):** pick a state so teeth/opening stay consistent - *lips softly together*
  (demure/regal), *lips slightly parted* (editorial glamour - the flattering default), *a soft smile
  with a hint of teeth* (upbeat), or *open / laughing* (playful). Vague = random teeth.

## Expression by purpose

Match the face to the outfit's job:

- **Elegant / regal** (gown, formal armor) - composed; lips softly together or barely parted; serene.
- **Editorial glamour** (catwalk, most looks) - confident; lips slightly parted; direct model gaze.
- **Playful / upbeat** - soft smile with a hint of teeth.
- **Sultry / come-hither** (motion variants) - lidded eyes; lips parted; chin down.
- **Fierce / commanding** (final, casting) - intense; jaw set; a slight knowing curl.

## Outfit polish (runway details that elevate a look)

When an outfit feels flat for the catwalk, add one or two - not all:

- **One statement piece** (a bold choker, a dramatic pauldron, the signature weapon) as the focal point.
- **Cohesive metals / palette** - keep silver + amethyst consistent so it reads as one designed look.
- **Texture contrast** - matte vs. sheen, sheer vs. solid, hard armor vs. soft drape.
- **Silhouette lines** - a high slit or high-cut leg to elongate; a defined waist; a train or cape for movement.
- **Movement** - fabric and hair caught mid-step so it doesn't look static.
- **Footwear that elongates** - heels that extend the leg line, coordinated with the palette.

## Body & head orientation (break the forward-facing lock)

Vague direction ("face any direction") makes the model default to the safe pose - upright, facing
camera. To get variety, **name a concrete angle**, and specify three axes separately (they can
differ - that's what makes a pose glamorous, not flat):

- **Body / torso:** front - **3/4 turn (~45 deg)** - profile (side) - 3/4 back - back to camera.
- **Head / face:** to camera - turned 3/4 - profile - **over the shoulder** - tilted up / down.
- **Gaze / eyeline:** to camera - off-camera into the distance - down - up.

**Key:** drop "Face remains focused on camera" when you want a turned head - that line locks it
forward. The classic glamour look is **body 3/4, head turned to camera, chin slightly down, eyes to
camera** - not flat front-on.

Ready orientations to drop in:

- **Classic 3/4:** body angled ~45 deg to camera, weight on the back leg; head turned to camera, chin
  down; eyes to camera.
- **Over-the-shoulder:** back toward camera, head turned over the shoulder, eyes to camera; hand at the hip.
- **Profile:** full side profile, chin lifted, gaze off-camera into the distance.
- **Aloof editorial:** body front, face turned to 3/4, eyes off-camera.
- **Contrapposto walk:** mid-step, hips and shoulders counter-rotated (S-curve), head leading the turn.

## Denoise in plain terms

Denoise (img2img) = **how much of the input image to repaint**:

- **1.0** - ignore the input, generate fresh. Use for the **A-Pose base**.
- **~0.5-0.7** - a big change while keeping identity. Use to **apply an outfit / armor**.
- **~0.4-0.6** - change **one** thing (hair, pose, a stance).
- **~0.2-0.4** - enhance without redrawing. Use for **polish / fantasy**.
- **0.0** - return the input unchanged.

Feel it: if the change didn't take (outfit not applied) **raise** it; if the face / identity drifted
too far **lower** it. It's one dial between *faithful to the input* (low) and *changed / creative* (high).

## Dynamism & variety (how to actually get it)

Variety comes from the **seed**, not from vague words:

- **Seed = randomness.** Same prompt + different seed = a different result. Roll / randomize the seed
  and batch a few, then pick. "Any direction" does *not* randomize - it defaults to forward.
- **Variety = a library of concrete poses**, not one vague prompt (see the directional pose files).
- **Denoise** = how far it moves from the input: higher = more change, lower = more faithful (~0.5-0.7
  for a real pose change).
- **CFG / guidance:** slightly lower lets the model add its own motion; higher sticks to the words.
- **Energy words help inside a concrete frame:** mid-motion, caught candidly, off-balance, wind-caught,
  unposed - but still name the body / head / gaze angle.

## Migrating your existing `.json` prompts

They already follow most of this. To standardise: lift each positive prompt into the matching
template, pull `background` out of the camera line into block 2, group wardrobe into the slots above,
and replace hero specifics with `[BRACKETS]`. Then per new hero you copy the template and find/replace
from their card JSON — no rewriting.
