# Plan: a simpler first shot (bare or neutral base), the Prime flows, and the clean-up

Status: active, Oct 11, 2026 (the clean-up is done; the first-shot experiments are built and waiting for your tests)

Source: your messages of Oct 11, copied word for word at the end. Continued on Oct 12 in [2026-10-12-prime-prompts-frames-and-inputs.md](2026-10-12-prime-prompts-frames-and-inputs.md) (seeds, inputs, initial frame gaps, pose-first Prime; the frame flow was retired Oct 19). Earlier steps of the same thread: [2026-10-11-tidy-junk-organise.md](2026-10-11-tidy-junk-organise.md) (Phase 4), [../art/prime-flows.md](../art/prime-flows.md), [../art/original-photos.md](../art/original-photos.md).

## Why we are doing this

The chain grew by accident: original photo, then a swimsuit Prime, then a Bare edit that takes the swimsuit off and sets her build, then the swimsuit put back on in `3_Layers`. The face is the most important thing, and every edit drifts it a little.
FireRed also often returns a cropped body when the original is not full length. So we step back and ask what the shortest reliable path is from an original to the images everything else starts from: the **bare figure** (the body master) and a **swimsuit** figure, with her face intact and her build taken from the art data, not from the original.

## What each step is for (so we do not drop the wrong thing)

| Step | Role | Required? |
| --- | --- | --- |
| first shot (`1_Prime`, or an experiment below) | the original becomes a head-to-toe A-pose with her face; the build is stated in the art data (`.json`), not copied from the original | yes, one way or another |
| `2_Bare` Figure | sets her individual build and likeness on the Prime | yes, unless the first shot is already bare |
| `3_Footwear` (Barefoot, Heels), `1_Prime` swimsuit, `2_Studies`, `3_Layers` | validation: a swimsuit with footwear is a simple known thing to check; studies and layers show that the image still looks right when edited, before any wardrobe | optional; kept because they make a problem cheap to find |
| `4_Wardrobe`, `5_Scenes` and on | the product | yes |

The reasoning is also written in [../art/tutorial-art.md](../art/tutorial-art.md) ("Why the steps in between exist").

## Decisions

| ID | Question | Answer |
| --- | --- | --- |
| F1 | Which shot first? | Test three paths on the same heroes: P1 the swimsuit Prime (today, the baseline), P2 a neutral skin-tone base layer, P3 the bare figure directly. You think P3 is likely best because the bare body is what clothing contours to. |
| F2 | Where does the build come from? | The art data (`physique` in the hero `.json`), never the original. P2 uses the slender standard figure like the Prime, then Bare imposes her own build; P3 states her own build at once. |
| F3 | Where do P2 and P3 live? | Beside `1_Prime`, in `1_Alpha/1b_Experiments/<family>/`, the same convention as `2b_Experiments/celestial`: card (`_sets`), prompt, workflow and output all use that folder. A winner is promoted to `1_Prime` (`git mv`), the others are removed. Templates: `_templates/heroes/1_Alpha/experiments/`. |
| F4 | Engines | Both Qwen and FireRed get every experiment workflow. The initially built Frame variants were retired by decision on Oct 19; FireRed keeps the identity lock in front of the prompt. |
| F5 | The face from a second image (P4) | Not built: it needs a second image wired into the workflows and the model may blend badly. Decide after P2 and P3. |
| F6 | The bare-chest study and the covering experiments (pasties, contoured, paint) | Dropped (they bled into the wardrobe and swimwear shots). The celestial experiments stay: they become body armor in the wardrobe. |
| F7 | Heroes without a full-body original | Do not use frames (decision Oct 19). Use the chosen photo as-is or re-pick a full-body source based on the prompt results. A chest crop is only a possible future experiment; it is not implemented. |

## How a path is run

All three paths take the same selected source photo for the hero.

| Path | First workflow | Then |
| --- | --- | --- |
| P1 (today) | `Hero_Qwen_Alpha_1_Prime` (swimsuit A-pose) | choose the image, `inputs set HERO --prime IMAGE`, then `Alpha_2_Bare_Figure`, Footwear, Layers |
| P2 | `Hero_Qwen_Alpha_1b_NeutralBase` (skin-tone base layer, slender standard figure) | choose the image, `inputs set HERO --prime IMAGE`, then `Alpha_2_Bare_Figure` as usual |
| P3 | `Hero_Qwen_Alpha_1b_BareBase` (bare figure, her own build) | choose the image, `inputs set HERO --bare IMAGE --prime IMAGE`: it is the Bare figure, so Footwear, Layers and the rest read it. The Bare Figure step is not needed |

Each had a FireRed twin (`..._FireRed_...`) at initial build. The Frame twins were archived when the flow was retired on Oct 19. Compare active results with `bin\compare-primes.cmd` (face score against the photo) and by eye: the body is full length, the build matches the art data, no strap lines or colour cast, how often a rerun lands.

## Steps

### Clean-up

- [x] C1 Removed the bare-chest study and the covering experiments: 106 cards, 106 prompts, 212 repo workflows (106 Qwen, 106 FireRed copies); 222 workspace copies moved to `workflows/.sync/backup` (`cleanup --orphans`); the scaffolds no longer write them. The celestial experiments are kept.
- [x] C2 Docs updated (tutorial, STATUS, data/art README, workflows README).

### First-shot experiments

- [x] E1 Layout: `1_Alpha/1b_Experiments/<family>` in `art_layout.py` (families `bare-base`, `neutral-base`), role `alpha/base` = photo (`workspaces.json`).
- [x] E2 Templates `base-bare-human.txt` and `base-neutral-human.txt` in `_templates/heroes/1_Alpha/experiments/`, with their Critical-details defaults.
- [x] E3 `tools/generators/scaffold_first_shots.py`: a card of each kind next to every female hero's Prime card (44 cards).
- [x] E4 Prompts, then 160 workflows (Qwen and FireRed, normal and Frame) built (`comfy_workflows.takes_photo`) and deployed to Angel Primes and Drakn Sisters. `prime_compare --shots` covers them. The Frame variants were archived on Oct 19; only normal and P2/P3 experiment paths remain active.
- [x] E5 Tests (`FirstShotTests`, `prime_compare`, validator mutation tests); the template README and the guide.
- [x] E8 Template wording audit: the positive prompts of the Bare, Head and Polish templates and the pieces `bare-skin-study(-male)` and `skin-tone-base-layer` now state what is shown, not what is missing. The rest is listed in `docs/STATUS.md`.
- [x] E9 The leftover 3_Layers covering cards (`*-x-pose-bareskin*`: adhesive covers, contoured, paint, paint-colour; 84 cards, 84 prompts, 84 workflows, 88 workspace copies moved to backup) and their four pieces were the same experiments as C1 and are removed.
- [x] E10 Seeds (Oct 12): the FireRed templates (`ST3_FireRed_Final`, `ST0_FireRed_Text`) and both MiniMax templates shipped with `control_after_generate` = fixed (seed 43 / 1), so every FireRed and MiniMax workflow made from them ran with the same seed.
  Templates fixed (inner KSampler/RandomNoise value and the named copy); `make` and `deploy` now set randomize on every generated workflow without a final record (1,585 FireRed + 102 MiniMax repo workflows, 1,500+ workspace copies).
  The ST templates in the workspaces were replaced from the repo masters (backed up); a test fails if a template ships fixed. Finals, shots, curated and candidates are untouched.
- [x] E11 Missing input images (Oct 12): a workflow loads its image from its own workspace's input folder, and only `inputs reset` copied images there, so the Frame images (and the experiment photos) were missing from most of them.
  `bin\sync-inputs.cmd` copies what deployed workflows load without retargeting anything; `refresh` and `refresh-firered` run it. The Prime Frame images and variants were archived on Oct 19; sync-inputs continues to serve active workflows.
- [x] E12 `Female` (alpha/female): its photo had been moved out of the Fantasy artist folder (it is Sandalyn's review photo). Restored as `Various/gallery/various_image_7500732784539999043.jpg` and pointed to it; the Female first-shot workflows load it.
E13's seven possibly missing chosen Prime renders are consolidated into T5 of the Oct 12 Prime plan; verify the current input state there rather than relying on this historical list.
- [ ] **P1 you** E6 Your tests (alpha/female, Angelica, Drakness first; then the other sisters and angels). Decision F1 and F7.
- [ ] **P1 ai** E7 After the decision: promote the winner to `1_Prime`, remove the losers, update the scaffolds, the templates README and the tutorial.

## Result

(to be written when the tests are done; the set-up is finished and waits on the ComfyUI runs of E6)

## Your messages, word for word

### On the first shot (after the opinion)

I think I would like to add the beta flows as you described, with proper prompt templates using the current .json inputs we have for the various flows instead of a hard-coded flow -but the prompt templates can drive more with both Qwen and FireRed to support the approaches that we need in each step.
I feel like P3 is likely the best for the way I am thinking about how the countour of the bare image works when clothing is applied and we get the right bust and figure adapted from the original to suit the definitions we have for the body within the .json data.
We don't want to take the exact figure of the original - in some cases it might already support the definitions, but we were doing the slender appraoch for the Prime post as simplifications because taking the existing one - in full clothing and a scene was causing issue to get the body at the same time as keeping face likeness (not exact makeup as some originals were wearing makeup we didn't want) as much as we could without the original polluting the looks we wanted to apply later.
So basically the face is the most important aspect, if the bust already supports what we want (great that made it easier)  - if it didn't we were changing it during the bare figure.
So if you can streamline and simplify the process of taking the original - which in some cases - I only have headshots and we do need to describe at least some aspect of a body in the first step, that's what I am looking for so the body doesn't come out in the first shot as unexpected or not a full body (head-to-toe) shot - which is what FireRed is doing many times when it's not a complete full body original.
Qwen images are solid, but FireRed when it works are better - but honestly I don't know if I do or don't need that for the rest of the chain.
I just worry that the face in the original -> prime (first image) is important - but maybe that's what I a missing.
As you can tell I'm just learning and hence all the experiments with many things that most experiments failed at (pasties, etc...)
Going to a straight original -> prime (in swimsuit) -> Bare Figure was working out decently ... it was just that I wanted to test FireRed and that's where things started to side-track me.
So that said - let's get setup for being able to test P2 and P3 and hopefully don't have to figure out a P4 - unless you think it's just as easy to setup all of them and test them all on sisters and angels.
I'll focus on alpha/female, then Angelica and then Drakness - and depending on those results test with all the sisters and angels as they all have varrying "photos" as their base - and you already know that some of the chosen people might not have a full body shot availble in what I have -
so it's possible for the heros that needs this - we may need to re-pick the Prospect (or I settle for one of the 3 approaches that work good enough for what originals I have)  that decision to be made after testing, but that might mean that in processing the prospects we need to identify which ones do and do not have good enough body shots vs. just face shots.
Does that all make sense?
Just more and more testing to get to a point where I can really start to move forward, but what I will say is that the original for Drakness has the Face and Bust that works the best for her and it's a full body shot - which is why she's worked out so well in the P1 flow even the way it is.
With Qwen, it's more forgiving and does produce a solid output and IF that quality is really good enough - then Qwen might be the right workflow - I just want to be sure we're doing this the most efficient way and I agree that the swimsuit on, then off to adjust body and try to keep the face, hair etc, then put the swimsuit on the new body is confusing - it just happened that way over time.
So stepping back - it's time to optimize based on learning we have and what we think should be the optimal path.

### On the clean-up

While our are doing this the bare chest study isn't necessary, it was also an experiment.
Ideally, we can drop experiments and things that don't align with how we eventually got to the Bare Figure ... just to clean some things up a bit.
That was going to happen eventually when we get the flow right.
As you can see lots of things were tried but most experiments ended up bleeding things in the bare images into the wardrobe or swimwear shots.
So those weren't working.
Keep going and if you fee like we can clean-up we can have archive for them or just remove them.
Just to clean-up the list of workflows.
We don't need to publish them to ComfyUI any more.

I take that back - the celestial ones were somewhat decent.
Sorry, just realized those need to stay as they would make it to a wardrobe in terms of a specific type of body armor.

### On why the steps in between exist

I honestly don't know about the 1_Prime/3_Footwear and if it's needed, but it was a way to get to a swimsuit with footwear to prove that things were working ... which is how this all originally started until I learned that footwear was also bleeding into barefoot scenes or wardrobes.
But we can keep that as an optional thing we test with as it helped with the 2_Studies to make sure that the output from the 1_Prime (in a swimsuit with footwear) would look well in those workflows - before jumping to 3_Layers where we put her in a wider variety of clothing - before a full 4_Wardrobe.
I hope this all makes sense into the transition in how we weren't jumping from 1_Prime all the way into a wardrobe and then fighting the fact that there was some issue in 1_Prime we could address if we did the 2_Studies and 3_Layers as validaiton.
They are not required - just that they help ensure that when we get to a 5_Scene that things look good and we're not having issues.
If that all makes sense the it's documented why somewhere.

### On keeping track

Finish the clean-up stuff, but don't forget about the flows for P2 and P3 we need as well - sorry I distracted you with some clean-up as you were working on all that.
I also should have told you to write-up the docs/plan as part of this, if you didn't already so we can keep track of everything we're doing and why.
So keep going with all we have discussed and update the plan along the way.
You're great at remembering, but I am not so we need this all documented for when I as "why did we do this"???

Again - don't forget what we are doing - but now that you know about all the details of how the art .json, templates and workflows work - make sure that where you put things for P2 and P3 make sense in how things are organized.
Sometimes stuff is just put out there and later we have to totally restructure things as it doesn't make sense after we are done with the testing/validation of the phases.

## Raw notes: which shot to make first (Oct 11)

Your words, kept as written (only wrapped).

# Which shot first: swimsuit Prime, neutral base, or bare (draft, no decision)

## Today

`photo -> 1_Prime (coloured string bikini, A-pose, denoise 1.0) -> 2_Bare (remove all clothing, individual build, ~0.9) -> Bare_Chest and Bare_Figure -> 3_Barefoot / Heels -> swimsuits and the rest (3_Layers)`.

The swimsuit is made first, taken off, and put back on later.

## The three images everything should hang on

1. **Bare figure**: full length, neutral stance, her build. The body master.
2. **Bare chest**: a bust close-up with a proper face (eyes, lips, makeup). The face master.
3. **Swimsuit figure**: the first wardrobe pass.

## Opinion

- A base should be the **least committed** state of the character (studios use a nude or fit-model garment, like a base mesh); every outfit is then an **additive** pass on it. Today's order is subtractive for the swimsuit: it makes a coloured, hero-specific bikini, then asks a high-denoise edit to erase straps and
strings and re-shape the body, and later puts a swimsuit back. That costs steps and leaves traces (strap lines, colour cast, a second drift of the face).
- The swimsuit should come **after** the bare figure, as an additive edit. Edit models are much better at "put this on her" than at "remove this and keep everything else".
- The bare chest is a **close-up**: it should come from the face master (headshot or frame), not be a crop of the full figure, where the face is about 130 px.
- Risk of going straight to bare: open edit models handle a bare torso unevenly (the repo's `2b_Experiments` on paint, pasties and skin suits suggests this). So test it, with a neutral nude-tone two-piece as the fallback first shot.

## Which original is the first shot

Choose the input by what the original shows, not by one rule:

| Original | Body source | Face source |
| --- | --- | --- |
| full or nearly full length | the photo | the photo |
| partial body | the frame (the body is invented anyway) | the headshot of the same photo |
| head only | the frame | the headshot |

The best photo of a hero is the one `likeness photos` already ranks: her face, one clear face, some body in view, portrait. The best headshot is the front-facing, even-lit one, which may be a different photo.

## Minimal chain

```text
original -> BASE (bare or neutral figure, her build)  --+--> Bare chest (bust, face pass from the headshot)
                                                         +--> Swimsuit (additive)
                                                         +--> Barefoot / Heels (additive)
```

One generation from the original, three derived images, each one step from the base.

## Paths to test (same hero, same seed, several heroes)

| Path | First shot | Then | What it tells us |
| --- | --- | --- | --- |
| P1 (today) | swimsuit Prime | Bare, then Bare chest | baseline |
| P2 | neutral nude-tone two-piece | Bare (light edit) or use as the base, swimsuit additive | does a neutral first shot beat a coloured one |
| P3 | bare figure directly | bust from the headshot, swimsuit additive | can the model do a clean bare base |
| P4 | P2 or P3, plus a face pass with the headshot as the second image | | does the real photo's face hold up across the chain |

Judge with `compare-primes` (face score against the source) and by eye: straps or lines left, colour cast, the face at the bust, step count, how often a rerun lands.

## What an AI studio would add

For the main heroes (sisters, angels) a studio would not chain edits to keep a face: it would train a small identity LoRA or use a face-embedding adapter from the 20 to 70 photos we already have per hero, and run every image from that, with pose and wardrobe controlled separately. That is the larger investment and
removes the Prime as a bottleneck; worth planning after the paths above, for the heroes we keep.
