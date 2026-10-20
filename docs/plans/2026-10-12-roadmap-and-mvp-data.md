# 2026-10-12: roadmap and MVP data track

**Status:** active (moved here from `STATUS.md` so that one queue, [../todo.md](../todo.md), shows everything open)

The game-design and data work that was a list in `STATUS.md` ("Next work", "Art and video track", steps 3 and 4 of the Oct 8 agreed steps).
The decisions behind it stay in `STATUS.md` (the MVP is Darkness and Light, the 8 rarity tiers, the open decisions O1 to O12). The art-pipeline work is in the other plans.

## The MVP data track

- [ ] **P1 either** R1 G1 Darkness and Light set (the MVP). Only 4 Darkness and 4 Light cards exist (sister, bound hero, dragon, pet each) and no legacy heroes; Fire has 53, Water 46. Define heroes, units and tactics for both in the codex, then art. The best end-to-end test of the card to art to prompt flow, and the beta's content. Card design choices are yours; the assistant writes the data and runs the validators.
- [ ] **P2 either** R2 D3 Starter decks and products. Rebuild `data/decks`, `data/products` and `data/manifests` around Darkness and Light (plus Neutral cards) using the starter-hero decision; include lower-level heroes and decide where bound heroes and dragons enter (O3). This fixes the data debt (26 card ids that do not exist, packs built on the retired elements).
- [ ] **P2 ai** R3 D2 Rule reconciliation. Re-check `combat-calculation-spec.md` and `deck-progression-rules.md` against the 8-tier model and the MVP elements (the Light and Darkness duality, Neutral normal). The docs audit also found the MVP and design docs still carry July 2026 text.
- [ ] **P3 you** R4 G2 Plan the next cycle (Fire, Grass, Water, Earth) once the Darkness and Light beta has shown what a full element costs.
- [ ] **P3 either** R5 Art for the 15 legacy heroes that lack art identities, plus full sets for Darkness and Light first, then Grass, Fire, Water and Earth.
- [ ] **P2 you** R6 Answer or deliberately defer the remaining `STATUS.md` decisions O2–O11: vision-card acquisition, Transcendent legality, the Neutral deck rule, the angels' spells, the story link angel to sister, `AP-###`, roster page names, Draknara wording, and the Drakn Bound men in the 1_Alpha chain. O12 video format and duration are decided; the render test is tracked once at 8.5 of the finals plan.

## Steps 3 and 4 of the Oct 8 agreed steps

- [ ] **P2 ai** R7 Step 3, after 3a: signature items for Angelica and Angelo (element and alignment, wings, pet, signature weapon, armor, gown, circlet, jewelry, elemental drift, the cards that use them), the same as the other twenty angels. Phases 3b to 3d, with a pause after each.
- [ ] **P2 ai** R8 Step 4: one canonical companion piece per Elder Dragon from its identity file, and each sister's piece extends it with only the scene placement (today the sisters' dragon companions are copied text).

## Art and video track (alongside)

- [ ] **P3 either** R9 Library gaps: the map in `data/art/README.md` (backgrounds, props, races, creatures, unit, building and tactic art, theme gear). Do them as the sisters' scenes show what is missing, not as one big push.
- [ ] **P2 you** R11 Compare Qwen and FireRed on scenes; decide how the two (or a FireRed render plus a Qwen polish pass) are used.
- [ ] **P3 you** R12 Underlayer tests for Drakness (string, push-up, balconette, bralette, sports, armor, lace, lace bodysuit, the backless set) to choose the A-pose look that blends best.
- [ ] **P3 either** R13 Title and key-art scene from the text-to-image templates (`ST0_*_Text`) as a card in the pipeline; an item stage for weapons and armor; use the other `ST` templates (polish, finals) to generate their own prompts.
- [ ] **P2 ai** R14 The documentation audit's other items that are not decisions, and a launcher check, now with the art and video tutorials (the audit is in `docs/audits/2026-10-12-docs-audit.md`).

Video rendering and review is tracked once in [the finals plan](2026-10-09-finals-and-mvp.md), step 8.5.
