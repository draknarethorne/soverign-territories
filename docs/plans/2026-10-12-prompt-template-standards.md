# 2026-10-12: prompt template standards

**Status:** active (drafted from your note; the first step needs your approval of D2 and D6 in the Prime plan)

Before you regenerate the Primes for all sisters and angels, every prompt template should follow the same standard: the format and the critical-to-know items up front, then a body that is clearly structured and puts the key items first.
This plan is the follow-up to D6 and T9 of [2026-10-12-prime-prompts-frames-and-inputs.md](2026-10-12-prime-prompts-frames-and-inputs.md) (the canonical paragraph order), widened into a written standard that new templates follow too.

## What the standard must cover

| Topic | What the standard says |
| --- | --- |
| Order | The canonical paragraph order of D6, for every template that builds or edits a picture: format and critical block first, then the key items beyond critical, then the rest |
| Exact likeness | When the incoming image must be reproduced (face, eyes), say so first and say what may change |
| Likeness inheritance | For an edit stage that should preserve the Prime's makeup and eye appearance, distinguish preserving the incoming appearance from reasserting character-specific eye-colour data |
| Focus areas | How to ask for a focus on the eyes, the bust, the body, the background, the action, the motion or the wardrobe, without the others drifting |
| Desired outcome | Put the requested change and its critical details first, state the exact result, then add identity and supporting details |
| Removal and positive wording | Prefer clear positive descriptions, but explicit removal is not inherently a harmful negative: when essential, put it up front and pair it with the desired replacement/result |
| Skin-tone language | Audit every character's skin-tone source wording for identity accuracy and unintended shine, gloss, glow or makeup associations; prefer neutral complexion/undertone wording unless a finish is deliberately intended |
| Cropped inputs | Treat a crop as a partial view of the intended whole figure; explicitly direct the model to complete missing parts and show the full figure |
| Full body | Name the full-body framing and placement, including feet planted on the ground where appropriate, so the output does not inherit the input crop |
| Lessons | Keep the Critical block, FireRed lock, feet and crop wording, explicit removal, and tested positive phrasing together as evidence-based lessons |
| Incremental testing | Change one section or family at a time; regenerate and test the affected Angelica workflow(s) end to end before calling a change approved or applying it broadly |

## Decisions

| ID | Question | Answer |
| --- | --- | --- |
| S1 | Does the standard live in its own file, `docs/art/prompt-template-standards.md`, next to `prompt-pattern.md` (which keeps how the generator builds a prompt)? | Proposed: yes, one home for the rules; `prompt-pattern.md` links to it |
| S2 | Do the templates change before or after the Prime test (T3)? | Proposed: the order and the feet wording (D2, D6) after T3 shows what helps; nothing is regenerated before you approve |

## Scoped Alpha wording correction (Oct 13)

A narrow regression fix was requested and applied without approving the proposed canonical prompt order in S0.
The female and male Bare templates restore the explicit source-clothing removal instruction. The shared bare-skin
descriptions again start with "nothing but", while BareBase and NeutralBase explicitly replace source clothing and
name their separate targets. NeutralBase remains a skin-tone base layer, not bare skin. Alpha prompts and repository
workflows were regenerated and published; Angelica render comparison remains pending.
This scoped fix does not approve the wording as a final standard or authorize broad template changes. The full
template audit and standardization remain gated on S0.

## Angelica Alpha 2 Bare render observations (Oct 13)

Initial four renders were inconsistent; only one was reported as having the right overall output. The outcomes noted:

- One retained the source skin tone and produced the intended body.
- One retained the right skin tone but showed heavy golden eyeshadow and missed breast anatomy. The earlier glasses report was a misidentification; gold wording is a hypothesis to inspect, not an established cause.
- One retained the right skin tone but missed breast anatomy.
- One produced the intended anatomy but made the skin much lighter.

Treat these as test observations, not approval of the prompt or evidence that any single phrase is the cause. Further
Angelica renders should check skin-tone fidelity, intended anatomy, and source accessories together before changing
wording. Keep each prompt adjustment narrow and compare the affected Qwen and FireRed workflows.

Follow-up report: four consecutive Bare Figure outputs showed golden makeup patterned around the eyes while the rest
of the body was underdeveloped or neglected. This repeated pattern strengthens the case to compare the character-
specific eye/skin block against the Prime-preserving A/B variant. It remains open why 1_Prime, which also specifies
Angelica's eyes, has not shown the same issue; its build-from-source task, image path and denoise differ from Bare,
so the eye wording alone cannot yet explain the contrast.

## Angelica Alpha 2 Bare eye and skin inheritance question (Oct 13)

The current `bare-human.txt` defaults include hair, the hero's own bust, character-specific eyes and character-specific
skin in the up-front Critical details block. Angelica's eye detail includes soft-gold iris striations; her skin
description says "luminous". Her `eyeshadowColor` is explicitly "neutral", so the gold-bleed theory is unconfirmed,
though several nearby identity details use gold wording. Older generated Bare wording instead described the eyes and
skin as the reference image's own, unchanged. This is a confirmed wording difference and a testable hypothesis for
makeup/appearance drift, not proof that either descriptor caused the golden eyeshadow or skin variation. Audit the
history and test whether Bare should preserve Prime eyes/makeup as-is, then introduce explicit eye styling in a later stage.

An isolated A/B card, `Angelica_Alpha_2_Bare.txt`, sits beside the unchanged
`Angelica_Alpha_2_Bare_Figure.txt`. Within each engine, it uses the exact input image and denoise of the installed
Bare Figure workflow, with the same individual build and negative prompt. It removes the positive
character-specific Critical details block, describes skin tone as matching the Prime rather than naming its colour,
and explicitly preserves the Prime's face, eyes and makeup. Compare matched Qwen/FireRed runs before drawing conclusions.

## Character skin-tone language audit (Oct 13)

Audit the skin-tone descriptions for all 44 hero identity records, including wording such as "golden", "radiant",
"luminous" and "glowing". Record the exact source phrase, whether the adjective describes undertone or visible
surface finish, and where it enters generated prompts. Report findings and candidate neutral wording only; make no
bulk data edits until Angelica renders and the user's review support a specific change.

## Current checkpoint and next work (Oct 14)

The user is running Angelica comparisons in ComfyUI and saving personal refinements under `zz_Shots`. The new
`Angelica_Alpha_2_Bare.txt` variant is intended to compare with the unchanged `Bare_Figure` using the same
engine-specific input and denoise. The test series also includes Prime, BareBase and the scoped 2b experiment.
No general prompt or identity-data changes are approved while these tests are in progress.

The user is using `B:\Sovereign Territories\_prompts\female\female_anatomy.txt` as a working vocabulary source
while refining bust, pelvic, body, makeup and related descriptions for JSON inputs. It is external to the repo,
user-maintained and not yet a project standard. It includes a broad mix of anatomy, skin finish, makeup, fashion,
lighting, posing and styling language. First compare selected useful terms against current JSON and templates;
do not copy the whole file or bulk-simplify metadata before that review. After the audit, decide whether a curated
`docs/art/` reference would help, and include only vocabulary that is useful, appropriate and consistent with
the approved data model.

## Angelica Alpha 1b BareBase render observations (Oct 13)

All four reported renders produced the intended head-to-toe A-pose, but none produced the intended bare result:
each generated large top and panty garments. Two substituted nude-coloured clothing for the source's complex top
and miniskirt; one produced a black two-piece. This suggests the framing and pose instructions are working while
the clothing-removal and bare-skin outcome is not reliable yet. It is evidence to investigate the outcome wording,
not a confirmed cause or approval to edit the prompt.

Current hands-on test focus: Angelica's Alpha 1 Prime, Alpha 2 Bare Figure, Alpha 1b BareBase and the scoped Alpha
2b celestial experiment trial below. NeutralBase is deferred until it is tested. Track each output by workflow/engine
and seed where available, and assess framing, clothing removal, skin tone, anatomy and likeness/accessories separately.

## Angelica Alpha 2b experiment correction (Oct 13)

The 2b cards declare denoise `~0.5-0.7`, but their shared Bare template advertised `~0.8-0.9` in the generated
prompt header. Workflow generation reads that header, so the card setting was not reaching the workflow. A
dedicated celestial-experiment template corrects the header, clarifies the direct armor replacement result, and
is assigned to Angelica's four 2b cards only. This is a test change, not an approved standard or a wider rollout;
review Angelica's Qwen and FireRed renders before applying it to other heroes.

## Steps

- [ ] **P1 you** T0 Finish the current Angelica comparisons; save candidate prompt refinements and outputs in `zz_Shots`. Track workflow, engine, input image, seed/settings where available, and results for Prime, Bare Figure vs Bare, BareBase and 2b.
- [ ] **P1 you** S0 Approve or change the Prime v2 structure and the canonical order (D2 and D6 of the Prime plan, T2 and T9 there). This unblocks everything below.
- [ ] **P2 ai** S1 After S0: write `docs/art/prompt-template-standards.md` from the topics above and the lessons in the Prime plan; link it from `prompt-pattern.md` and `docs/README.md`.
- [ ] **P3 ai** S2 After T0 and S1: audit every template in `data/art/_templates` and `workflows/_templates` against the agreed standard. Include Bare eye/makeup inheritance and a source-to-output review of all 44 hero skin-tone descriptions. Report first, no edits.
- [ ] **P2 you** S3 Read the audit and mark the templates to bring in line (all, or family by family).
- [ ] **P2 either** S4 Work in small batches: change one section or family, regenerate only affected outputs, and verify unrelated outputs did not change.
- [ ] **P2 either** S5 After T0, compare selected `female_anatomy.txt` terms with the relevant JSON inputs and generated prompts for bust, pelvic, body, makeup and skin. Report mappings and possible simplifications; do not edit data.
- [ ] **P3 either** S6 Decide from that audit whether to create a curated `docs/art/` vocabulary reference. If useful, write only the reviewed reusable terms and explain how they map to JSON fields; keep the external source non-canonical.
- [ ] **P2 you** S7 Approve each tested prompt/data batch before it is described as approved or rolled out to other heroes/templates; do not commit prompt-standard changes as approved before this gate.
- [ ] **P2 ai** S8 After batch approval: complete the chosen template work, checking by bytes that unaffected outputs did not change; regenerate, run `make --engine both`, and validators.
- [ ] **P3 ai** S9 Add a recurring check: when a template is added, run the audit against the standard (a validator rule or a line in the checklist of `docs/art/tutorial-art.md`).

## Raw notes: prompt structure (Oct 12)

Your words, kept as written (only wrapped).

I'm thinking that we might want to revisit every prompt in our _templates and ensure that it follows the same standards of having the format, critical to know sections up front and then the entire prompt body clearly structured in a way that prioritizes the key items beyond critical and that if we need to ensure taking exact likeness of incoming image or focus on eyes or bust or body or background or action or motion or wardrobe --- that we have the templates organized properly.
I honestly don't know if we have a prompt_template_standards.md that outlines that in detail enough so we could do a recurring reflection on additional templates as we add them so that we get consistency in how the prompt templates flow from first statements to the bottom.
It should also include tidbits about informing the AI how to handle any cropped images where feet or other parts are not present and that any input data fully describes entire body (if it's intended to be a full body shot) and we don't leave off things like "feet firmly planted on the ground" or other things to ensure AI doesn't just use the portion of the image that it has.
There are so many lessons we have learned about writing prompts - now is the time to re-visit all the prompts before I circle back and start regenerting images for prime workflows for ALL the sisters and angels.

## Raw notes: prompt wording and incremental testing (Oct 13)

Your words, kept as written.

The key lessons learned the past few days, when removing clothing and dealing with cropped originals, we need to be more explicit in the outcome we want and try to use positive phrases even when removing items - removing is not a negative as long as it's right up front and clear instructions to the Comfy AI model on what we expect.
Just positive wording was bleeding things from the original or not making sure it was a head-to-toe shot and explaining the full body placement - like feet planted on the ground (to ensure he does have feet created if they are not visible).
So the real test of the focus on the 1_Alpha prompts are ensuring we do have the right things up front, explicit in what we want, critical details for things we're changing in the image followed by the remainder of the items.
This is all learning to feed into the standardization of the prompts and proper sequence of all the sections in the templates to drive the point home of what each prompt is trying to achieve.
What this is also telling me is that we need to do things incrementally and test things along the way and not sweeping changes across all templates without proper end-to-end testing.
This means we'll want to make changes and ensure I do actually test the workflows impacted for Angelica before we commit any of them as "approved" changes.

## Raw notes: Alpha 2 Bare eye and skin observations (Oct 13)

Your words, kept as written.

I also have a correction - it wasn't glasses on the picture, it was heavy golden eye shadow - I think the "golden" keyword might be
being picked up.  We might want to look at the way we describe skin tones and ensure they aren't "too strong" in terms of
using glossey or shiny or luminous type words there as well as hallucinations happen in those cases.  It's not always - and
since I did just a small sample, I will let you know later - but an audit of how we describe the skin tones for all the
characters would also be useful and incorporate that into the plans for work on the prompts.  I also see the reference to
the eyes in Bare Figure seems to be calling out the color of the eyes for the character - at one point it was a more
neutral piece in the prompt as we'd focus on the eyes after the Bare Figure -- I think that might also be why her facial
makeup and eyes are changing from the original prime pose.  Bascailly with 2_Bare they expect that the original 1_Prime
had those and if you look back at history farther - you might see where we weren't even suggesting character specific
eye colors.  The 2_Bare was much more about keeping what was in the reference.  Just more for you to look into.

## Raw notes: current tests and female anatomy reference (Oct 14)

Your words, kept as written.

Can you make sure to commit to memory where we are, update the plan with what is next to do.  I am running the
comparisons and actually making my own zz_shots to test out refinements to the prompts and also to the language we
use for bust, pelvic, body, makeup and other things in this female_anatomy.txt that I used AI to generate for me to
help with refining the inputs in our .json files to the prompt generation.  It's helped tremendously in ensuring
that we're getting the right output for the character.  There are still things in the prompts that I am working
on to handle the explicit instructions on what each of the workflows is supposed to be doing so it sticks to the
objective of the workflow that the image we're working to get produced.  I believe all of what is in here is
appropriate as AI generated the prompts for me and it told me it could not suggest inappropriate items and these
are the statements it came up with.  We'll want to catalog this and prepare to look at it and compare against our
.json inputs and prompt templates where we specify things.  We might need to turn this into a formal .md file
within docs/art so we keep it as a reference - and we can audit against the existing meta-data we're using to see
if we can't simplify some of our tags (if we can use this more concise approach).  It incorporates all high-end
fashion and might be useable in many cases in our data/art files.  If the audit is too much to do right now - then
we can just propose we do that audit later on so we can move onto another topic/thread I need to work on.
