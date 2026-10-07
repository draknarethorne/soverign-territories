# Prompt Pattern — Hero Card Art

One consistent block order for every stage's prompt, so results are predictable across heroes and
cards. **The generator (`tools/generators/gen_prompt.py`) is the canonical production path** — it
compiles a hero/dragon definition (`data/art/heroes/<group>/<slug>-thorne.json` or
`data/art/dragons/elder-dragons/<slug>.json`) + reusable component(s) (`data/art/{races,wardrobe,
motion}/**/*.json`, via a card's `component`/`components` field) + a stage template
(`data/art/_templates/<archetype>/*.txt`) into the final prompt `.txt` under
`prompts/<group>/<Hero>/<phase>/<family>/`. Edit the **template / component / card**, never a
generated `.txt` by hand — regenerate instead: `python tools/generators/gen_prompt.py <card.json>`.
See [`data/art/README.md`](../../data/art/README.md) for the full directory/architecture reference.

> The old hand-copied `[BRACKETS]`-per-hero system (`prompts/_templates/`, `prompts/<Hero>/`) is
> retired and archived under `prompts/_archive/` — good historical reference for wording, but no
> longer live. Armor, Clothing, and Scene are now fully componentized (see the stage table below) —
> Fantasy/Weapons(standalone)/Background(standalone)/Pets(standalone) utility stages remain
> archive-only, not yet needed as their own generator stage.

## Golden rules

1. **One prompt = one stage.** Refer to the incoming image; describe ONLY what changes.
2. The **reference-fidelity** line is mandatory on every edit/final prompt — it anchors face, body, hair.
3. Hero-specific values (palette, eye colour, physique) come from `data/art/heroes/<hero>-thorne.json`,
   not from hand-typed values in a prompt.
4. Keep the block order **identical** across heroes/stages → consistent behaviour (see below).
5. **Blank line between blocks** is your delimiter (keep doing this — it works, and it's what makes a
   generated prompt easy to scan: one field, one paragraph).
6. Negatives = **three tiers**: universal (baked into the template), hero-derived (`eyeColorNegatives`,
   `skinColorNegatives`, `negatives` on the hero def), and a rare per-card override
   (`overrides.negativeAdd` / `negativeRemove`). Never hand-edit a generated negative line directly.
7. `{{TOKENS}}` are filled by the generator. Add a new style/pose by adding a **component JSON**, not
   by writing a new `.txt` from scratch.

## Block order (positive prompt)

Universal shape, top to bottom:

1. **Camera & quality** — realism, shot type, lens/focus (85mm, sharp, soft DoF). *(No background here.)*
2. **Background / Environment** — studio backdrop for base/edit stages; the in-world scene for final.
3. **Shot style / energy** *(optional)* — editorial / glamour / mid-motion (edit & motion stages).
4. **Reference fidelity** — "Maintain strict fidelity to the reference image's facial likeness, bone
   structure, body shape, proportions, eye colour, iris pattern, hair colour, skin tone, tattoos/marks."
5. **Preserve** *(edit stages only)* — "Maintain the existing outfit/hairstyle expressly."
6. **Breeze** *(when present)* — environmental; stated before the anatomical attributes it affects.
7. **Anatomical attributes, head-down** — this is the part that must stay consistent across stages:
   - **Figure** (whole-body shape/proportions)
   - **Skin** / general **Body** description (whole-body — skin tone at the Build stage; the literal
     body-positioning sentence at the Motion stage)
   - **Wearing** (clothing — spans the whole body; sits between the body-level attributes above and
     the head-down detail below)
   - **Hair** (topmost of the head-down group — always before Makeup/Eyes/Lips)
   - **Makeup** (face-wide)
   - **Eyes**
   - **Lips**
   - **Legs** *(only when Figure isn't restated in full — a short reinforcement line, e.g. Hair stage)*
8. **Pose / motion specifics** *(Motion only)* — Head / Gaze / Expression, then the capstone `Pose:`
   line last — deliberately last, since it's what the stage is actually for.
9. **Spell VFX** *(final only, not yet componentized)* — magic, glow around hand/weapon.

Each stage only includes the fields it actually needs — Hair stage has no Figure/Makeup line (it never
restates bust/face), Head stage only restates Hair + Eyes. What's shared must keep the same relative
order; what's stage-specific can simply be absent.

### Wardrobe slots — keep the blank lines (Armor/Clothing, not yet componentized)

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

Group names match the `Drakness_Qwen_<group>` / `Drakness_X_<group>` ComfyUI workflows.
**Componentized stages** (Pose, Head, Hair, Motion, Clothing, Armor, Scene) generate from
`data/art/_templates/<archetype>/*.txt` via `gen_prompt.py`, output to
`prompts/<group>/<Hero>/<phase>/<family>/`. **Not yet their own generator stage** (Fantasy,
standalone Weapons/Background/Pets plates) still only exist as hand-crafted reference text,
archived under `prompts/_archive/` — treat as reference wording, not a live template.

| Group | Reference | Preserve | Change | Background | Status | Template |
| --- | --- | --- | --- | --- | --- | --- |
| **X_Pose** (A-pose base) | source photo | likeness | build full base + figure + bikini underlayer | studio | ✅ componentized | [`pose-female-human.txt`](../../data/art/_templates/heroes/pose-female-human.txt) / [`pose-male-human.txt`](../../data/art/_templates/heroes/pose-male-human.txt) |
| **X_Head** (close-up) | A-pose | face + hair | framing (chest-up) | studio | ✅ componentized | [`head-human.txt`](../../data/art/_templates/heroes/head-human.txt) |
| **Hair** | A-pose | outfit + face + body | hairstyle only | studio | ✅ componentized (44 styles) | [`hair-human.txt`](../../data/art/_templates/heroes/hair-human.txt) |
| **Motion** | A-pose (chosen hair) | outfit + hair + face | pose/motion only | studio | ✅ componentized (26 poses, 'faceless' — gaze/expression are their own overridable concern) | [`motion-human.txt`](../../data/art/_templates/heroes/motion-human.txt) |
| **Clothing** | A-pose (bikini base) | face + body + hair | apply gown/dress | studio | ✅ componentized | [`clothing-human.txt`](../../data/art/_templates/heroes/clothing-human.txt) |
| **Armor** | A-pose (bikini base) | face + body + hair | apply armor + weapon | studio | ✅ componentized | [`armor-human.txt`](../../data/art/_templates/heroes/armor-human.txt) |
| **Scene** (final card art) | A-pose, or a prior stage's output | likeness (+ outfit, for the two-stage path) | full scene: background, pose, effects, weapon/companion | in-world | ✅ componentized — 5 template variants for different outfit shapes (preserve/direct-describe/+companion/minimal/combat) | [`scene-human.txt`](../../data/art/_templates/heroes/scene-human.txt), [`scene-with-outfit-human.txt`](../../data/art/_templates/heroes/scene-with-outfit-human.txt), [`scene-with-companion-human.txt`](../../data/art/_templates/heroes/scene-with-companion-human.txt), [`scene-minimal-human.txt`](../../data/art/_templates/heroes/scene-minimal-human.txt), [`scene-combat-human.txt`](../../data/art/_templates/heroes/scene-combat-human.txt) |
| **Dragon Pose/Head** | none — text-to-image | n/a | full dragon, generated from its own description | studio | ✅ componentized | [`pose-dragon.txt`](../../data/art/_templates/dragons/pose-dragon.txt), [`head-dragon.txt`](../../data/art/_templates/dragons/head-dragon.txt) |
| **Fantasy** *(optional, pre-scene)* | photoreal near-final | face + outfit + hair + pose | add fantasy makeup + glowing eyes + subtle magic | cream / soft gradient | ⬜ not yet componentized | archived: [`_TEMPLATE_Fantasy.txt`](../../prompts/_archive/_TEMPLATE_Fantasy.txt) |
| **Weapons** *(standalone utility)* | — | — | a standalone weapon prop (multi-image ref) | plain | ⬜ not yet componentized as its own stage (signature weapons instead live as `holding` pieces under `heroes/<group>/<slug>/weapons/`) | archived: [`_TEMPLATE_Weapons.txt`](../../prompts/_archive/_TEMPLATE_Weapons.txt) |
| **Background** *(standalone utility)* | — | — | a standalone scene plate | — | ⬜ not yet componentized as its own stage (backgrounds instead live under `data/art/backgrounds/`, wired into the Scene stage) | archived: [`_TEMPLATE_Background.txt`](../../prompts/_archive/_TEMPLATE_Background.txt) |
| **Pets** *(standalone utility)* | — | — | a summon/companion (multi-image ref) | plain | ⬜ not yet componentized as its own stage (dragons/bonded pets instead described inline or via `companion`/`dragons/` pieces) | archived: [`_TEMPLATE_Pets.txt`](../../prompts/_archive/_TEMPLATE_Pets.txt) |

## Component library, reuse, and the twin-pair convention

Hair and Motion styles are **hero-agnostic, reusable components** —
`data/art/races/human/cosmetics/hair/<family>/<slug>.json` and `data/art/motion/<family>/<slug>.json`.
An assembly card (`data/art/_sets/<group>/<slug>/<phase>/<family>/<slug>.json`) just points a hero
+ a component at a template; any hero can reference any style with a one-line swap.

**Twin-pair convention.** Many styles should exist as a **plain** version and a **decorated** version
of the same base style (e.g. a ponytail with vs. without loose face-framing tendrils), so the choice
is made per-shot/per-hero at generation time instead of being baked into one fixed variant. Apply this
plain + decorated pattern whenever it's natural for the style family.

**Descriptive vs. reference-bound components (future).** Today every component is purely descriptive
— full text, because there's no other source of truth for what it looks like, and natural variance
across renders is fine (even desirable for common-tier, mass-produced items). Once multi-image /
reference conditioning is available, a component can *graduate* to a locked signature asset by adding
an `assetImage` + binding-instruction field — opt-in, per hero/per-item, never required. Non-hero cards
should generally stay descriptive-only; natural variance there is thematically correct, not a bug.

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
- **Fidelity preserve-list (what every downstream stage must hold from the A-pose).** The
  `Maintain strict fidelity to...` line carries identity through each edit at ~0.5–0.7 denoise. It must
  list: **facial likeness, facial bone structure, body shape, proportions, eye colour, iris pattern,
  hair colour, skin tone, and any existing tattoos / body markings / beauty marks.** Rules:
  - **Anything set once at the A-pose that can drift must be in this line** — skin tone and iris pattern
    were both silent gaps that let the tan wash out and the signature iris simplify downstream.
  - **Signature marks (tattoo, birthmark, beauty mark) must be *defined* at the A-pose** (there's a
    `Distinguishing marks:` slot in `_TEMPLATE_Pose`) **and** named in the fidelity line, or the first
    edit will drop them. The generic "any existing …" clause preserves them when present, harmlessly
    when absent.
  - **Don't bloat it.** The line works by *concentrating* attention — every term dilutes the rest. Only
    add attributes that are both signature identity *and* actually drift; don't turn it into a laundry
    list of per-stage things (makeup, outfit, nails) that are meant to change.
- **Don't duplicate blocks.** Qwen reads instructions once; a repeated pose block (seen in Motion) adds
  nothing and can confuse. One block each.
- **Natural language, no weights.** Qwen-Image-Edit follows plain sentences — skip SD-style `(())`
  weighting or `:1.2` syntax.
- **Always negate rendered text.** Keep `text, wording, watermark, logo` in every negative (card art).
- **One canonical eye string per hero** (from the art identity's `palette.eyeColor`) — reuse it verbatim across
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

`extra people, extra limbs, extra digits, deformed hands, extra feet, recolored eyes, flat chest,
small bust, narrow bust, flattened breasts, wide-set breasts, wide cleavage gap, reduced bust size,
text, wording, watermark, logo, studio equipment`

Eye-colour negatives (`blue eyes, green eyes, ...`) and skin-tone negatives are **hero-derived, not a
fixed list** — each hero's def (`eyeColorNegatives`, `skinColorNegatives`) omits whatever family
matches her own iris/skin, so a hero is never banned from having her own colouring. (This is a real
bug we hit and fixed: a hero with forest-green/emerald eyes was being blocked by a universal "green
eyes" negative baked into the shared template.)

- **Edit / Hair / Pose** often add: `crowns, head gear, pauldrons, shoulder armor` —
  **but remove `pauldrons, shoulder armor` when the outfit is meant to have them** (as Armor_Bone
  does, via `overrides.negativeRemove` on that specific card).
- **Motion** often adds: `mismatched footwear`.
- **Final** adds: `altered face, altered armor, altered hairstyle, duplicate or second weapon`.
- **Bust/cleavage drift** is the other recurring failure mode — fixed by restating the figure with
  explicit, technical wording (push-up-bra-style contour, narrow décolletage, explicit "not
  flattened/reduced" negation) everywhere Figure is restated (Pose, Motion), *and* negating the drift
  terms above in the same stages.

## Persistence anchors (make attributes stick)

Some attributes drift when the model redraws (the bust / eye-colour problem). Lock them:

- **Restate** the critical attributes (eye colour, bust/figure, skin) in every stage that touches
  them, in the stage's established block position (see Block order above) — consistent positioning
  matters more than being literally last.
- **Negate the off-values** (strongest lever): hero-derived eye/skin negatives keep her own colouring;
  `flat chest, small bust, narrow bust, wide cleavage gap` keep the figure. Baked into every template.
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

## Adding a new hairstyle / motion pose

1. Add an entry to `tools/generators/scaffold_hair_motion.py` (preferred for anything following an
   existing family's pattern, though its output paths predate the `_sets`/`races` reorg and may
   need a quick check before trusting it), or hand-author the component + assembly card JSON
   directly for a one-off.
2. Run the script — it writes the component (`data/art/races/human/cosmetics/hair|motion/<family>/
   <slug>.json`) and the Drakness assembly card (`data/art/_sets/drakn-sisters/drakness/<stage>/
   <family>/<slug>.json`). It's idempotent: re-running overwrites existing entries with identical
   content and only adds new ones.
3. Generate: `python tools/generators/gen_prompt.py <card.json>`, or loop over
   `data/art/_sets/drakn-sisters/drakness/<stage>/**/*.json` to regenerate everything for that stage.
4. Validate before committing: no `{{UNRESOLVED}}` tokens, no stray `", ,"`, all JSON still valid,
   and X_Pose/X_Head (hand-authored, not script-managed) still generate cleanly.
