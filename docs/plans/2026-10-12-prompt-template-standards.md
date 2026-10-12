# 2026-10-12: prompt template standards

**Status:** active (drafted from your note; the first step needs your approval of D2 and D6 in the Prime plan)

Before you regenerate the Primes for all sisters and angels, every prompt template should follow the same standard: the format and the critical-to-know items up front, then a body that is clearly structured and puts the key items first.
This plan is the follow-up to D6 and T9 of [2026-10-12-prime-prompts-frames-and-inputs.md](2026-10-12-prime-prompts-frames-and-inputs.md) (the canonical paragraph order), widened into a written standard that new templates follow too.

## What the standard must cover

| Topic | What the standard says |
| --- | --- |
| Order | The canonical paragraph order of D6, for every template that builds or edits a picture: format and critical block first, then the key items beyond critical, then the rest |
| Exact likeness | When the incoming image must be reproduced (face, eyes), say so first and say what may change |
| Focus areas | How to ask for a focus on the eyes, the bust, the body, the background, the action, the motion or the wardrobe, without the others drifting |
| Cropped inputs | Tell the model how to handle an input where the feet or other parts are missing: the picture is part of a whole figure, and the output must show the whole figure |
| Full body | A shot meant to be full body names the whole body (including "feet firmly planted on the ground" and the like), so the model does not use only the part it was given |
| Lessons | The wording lessons learned so far (the Critical block, the FireRed lock, the feet wording, negative vs positive wording) in one place |

## Decisions

| ID | Question | Answer |
| --- | --- | --- |
| S1 | Does the standard live in its own file, `docs/art/prompt-template-standards.md`, next to `prompt-pattern.md` (which keeps how the generator builds a prompt)? | Proposed: yes, one home for the rules; `prompt-pattern.md` links to it |
| S2 | Do the templates change before or after the Prime test (T3)? | Proposed: the order and the feet wording (D2, D6) after T3 shows what helps; nothing is regenerated before you approve |

## Steps

- [ ] **P1 you** S0 Approve or change the Prime v2 structure and the canonical order (D2 and D6 of the Prime plan, T2 and T9 there). This unblocks everything below.
- [ ] **P2 ai** S1 After S0: write `docs/art/prompt-template-standards.md` from the topics above and the lessons in the Prime plan; link it from `prompt-pattern.md` and `docs/README.md`.
- [ ] **P2 ai** S2 Audit every template in `data/art/_templates` and `workflows/_templates` against the standard: a table of what differs, per template and family. Report first, no edits.
- [ ] **P2 you** S3 Read the audit and mark the templates to bring in line (all, or family by family).
- [ ] **P2 ai** S4 Bring the chosen templates in line, family by family, checking by bytes that the ones that should not change did not; regenerate, `make --engine both`, validators.
- [ ] **P3 ai** S5 Add a recurring check: when a template is added, run the audit against the standard (a validator rule or a line in the checklist of `docs/art/tutorial-art.md`).

## Raw notes: prompt structure (Oct 12)

Your words, kept as written (only wrapped).

I'm thinking that we might want to revisit every prompt in our _templates and ensure that it follows the same standards of having the format, critical to know sections up front and then the entire prompt body clearly structured in a way that prioritizes the key items beyond critical and that if we need to ensure taking exact likeness of incoming image or focus on eyes or bust or body or background or action or motion or wardrobe --- that we have the templates organized properly.
I honestly don't know if we have a prompt_template_standards.md that outlines that in detail enough so we could do a recurring reflection on additional templates as we add them so that we get consistency in how the prompt templates flow from first statements to the bottom.
It should also include tidbits about informing the AI how to handle any cropped images where feet or other parts are not present and that any input data fully describes entire body (if it's intended to be a full body shot) and we don't leave off things like "feet firmly planted on the ground" or other things to ensure AI doesn't just use the portion of the image that it has.
There are so many lessons we have learned about writing prompts - now is the time to re-visit all the prompts before I circle back and start regenerting images for prime workflows for ALL the sisters and angels.
