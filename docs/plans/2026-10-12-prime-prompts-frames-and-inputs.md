# Plan: Prime prompts (pose first), frame gaps, seeds and inputs

Status: active, Oct 12, 2026. A continuation of [2026-10-11-first-shot-flows.md](2026-10-11-first-shot-flows.md): that plan still owns the P1/P2/P3 decision (F1, F7) and the clean-up; this one owns what we found while testing it. The two get reconciled when the tests are done (see "Reconciling the plans").

Source: your messages of Oct 12, copied word for word at the end. Related: [../art/prime-flows.md](../art/prime-flows.md), [../art/original-photos.md](../art/original-photos.md), [../../workflows/README.md](../../workflows/README.md).

## Why we are doing this

You queued a large batch of Prime tests and found five things at once: some FireRed workflows ran with a fixed seed, some frame images were missing in ComfyUI, the frame folders do not hold a frame for every photo, the cropped Primes come back cropped (FireRed more than Qwen), and the templates are not consistent about calling out the pose.
The goal is a Prime that is reliable on cropped photos, with every test input where ComfyUI can load it, and a record of why each change was made.

## What we found (the deep dive)

| # | Finding | Evidence | State |
| --- | --- | --- | --- |
| 1 | The FireRed and MiniMax templates shipped with the seed control set to `fixed` (43 and 1). Every workflow made from them ran with the same seed | the inner KSampler and the named copy in `ST3_FireRed_Final`, `ST0_FireRed_Text`, `ST6_MiniMax_*`; 1,585 FireRed and 102 MiniMax repo workflows and about 1,500 workspace copies were fixed, Qwen was already random | fixed Oct 12 (S1) |
| 2 | `make` and `deploy` only ever kept the seed of an existing workflow, so a template fix would never have reached the copies | `patch_wf` touches the prompt and the save prefix only | fixed (S1): both now set randomize when no final record exists |
| 3 | Frame, experiment and restored images were not in the workspaces' input folders: only `inputs reset` copied images, and it refuses to run while you hold an unpulled Prime pick | 18 frame images, 0 to 1 of 16 input folders each | fixed (S2): `inputs sync` |
| 4 | `Female` (alpha/female), the first test subject, loaded a photo that no longer existed outside `_backup` and `_archive` | the Fantasy artist folder was reorganised on Oct 10; the photo is Sandalyn's review photo | fixed (S3): restored to `Various`, re-pointed |
| 5 | **Frame generation skipped reel screenshots.** `make_frames` tested the face against the whole phone screen (1080x2340, with the app bars) before cropping to the picture, so a face that is 0.127 of the screen but 0.21 of the picture counted as full length | Gavrielle: 4 gallery screenshots, 2 frames; after the fix 3 (the fourth has her head under the phone UI) | fixed (F1); 44 frames made |
| 6 | The "partial photo" threshold (`FRAME_FACE_MAX` 0.14, face brow to chin as a share of the picture) may be too high. A standing figure's face is about 0.09, so 0.11 to 0.14 means cropped at the thighs or knees, and no frame | 482 angel and sister photos: 378 above 0.14, 55 from 0.11 to 0.14, 37 from 0.09 to 0.11, 12 below. Chosen: Sammara 0.086 (full length), Draknira 0.124, Drakniya 0.133 | open: D1 |
| 7 | The library still held orphans of removed originals (a `gallery_944x1104` copy and a frame of `gavrielle_shot_20261010124337` whose original is gone). They are pruned to `_archive` by the normal `originals` run | the run of Oct 12 | done with F1 |
| 8 | The Prime prompt buries the pose. In the generated prompt the order is: intro, Critical details, camera, background, fidelity, then Standing A-pose, Figure, Skin, Wearing; and "bare feet planted flat on the floor, slightly apart, toes pointing forward" sits at the very end of the long swimsuit sentence | `pose-female-human.txt`; `Gavrielle_Alpha_1_Prime.txt` | open: decision D2 |
| 9 | The explicit feet wording you remember is real: 120 saved Prime candidates carry "bare feet planted flat on the floor, slightly apart with the toes pointing forward, natural relaxed toes, no shoes". The current Prime still has it, but only inside Wearing, and the "no shoes" half lives in the Qwen negative prompt | `workflows/_candidates/angel-primes/*/1_Alpha/1_Prime` | open: D2 |
| 10 | FireRed has no negative prompt. Everything the Prime says against shoes, heels, a cropped body or a wrong pose is invisible to it; only positive wording counts. The FireRed lock adds Face, Head and Framing in front, but the A-pose paragraph is still the ninth | `engine_prompt`, `firered-prime-face-lock.txt` | open: D2, D3 |
| 11 | The male Prime template has no Critical block at all (`pose-male-human.txt`), so the structure differs between male and female heroes | template inventory below | open: D2 |
| 12 | The experiment templates (P2, P3) carry Framing and Standing A-pose after the fidelity and identity lines, not in the Critical block, and say nothing explicit about the feet beyond the garment piece | `base-bare-human.txt`, `base-neutral-human.txt` | open: D2 |

## Decisions

| ID | Question | Recommendation | Answer |
| --- | --- | --- | --- |
| D1 | Lower `FRAME_FACE_MAX` from 0.14 to about 0.11 so thigh and knee shots get a frame? | Yes, and see what it adds: 55 more originals (angels and sisters). The frame is cheap (0.18 GB for 700) and you are still testing whether frames matter | open |
| D2 | Put **Pose, Framing and Feet** at the top, inside the Critical block, for the Prime, the male Prime and the P2/P3 experiments? Draft wording below | Yes: it is the strongest lever we have and costs no new data. Keep the feet line data-driven from the footwear piece | open: needs your approval before any template is edited |
| D3 | Once D2 is in, shorten the FireRed lock to the identity lines (Face, Head) and let the template carry Framing, so the two engines get the same pose wording? | Yes, after one test that shows FireRed keeps the full body | open |
| D4 | Keep, retire or extend the frame flow? | Hold (your call Oct 12): compare at least one angel with and without a frame first. If the Prime with the pose first works on the full photo, retire the whole frame process (images, flows, workflows, `originals` frames, docs) | open until the test |
| D5 | Should a hero whose chosen photo has no body at all be flagged? | Later, with F7 of the first plan: a face-only vs body-shot tag when the prospects are classified | deferred |

## Prime v2: the proposed structure (draft, nothing edited yet)

The idea: the Critical block already works for hair, bust, eyes, skin and legs ("these must be clearly visible"). Add the three things that fail on a cropped photo to the same block, first, so both engines read them before anything else.

```text
Modify the subject from the reference image into a clean, full-length, photorealistic portrait photograph.

Critical details - these must be clearly visible:
Pose: standing A-pose, upright, arms relaxed slightly away from the sides, open hands; head level and facing the camera squarely (replace the source photo's pose, head tilt and body angle entirely).
Framing: the whole body from the top of the head to the soles of the feet, with the floor visible beneath them; where the reference shows only her head and upper body, continue the figure downward to the feet.
Feet: {{FEET}}.
Hair: ...  Bust: ...  Eyes: ...  Skin: ...  Legs: ...
```

- `{{FEET}}` would come from the footwear piece (for the Prime: "bare feet planted flat on the floor, slightly apart with the toes pointing forward, natural relaxed toes"), so heels or boots stay a data choice. Wearing then stops carrying the feet.
- The later "Standing A-pose" paragraph is removed (one home per fact). The Qwen negative prompt keeps its footwear negatives.
- Wording stays positive (the Oct 11 rule): the feet and framing are stated as what the picture shows.
- Applies to `pose-female-human`, `pose-male-human` (which also gains the Critical block), `base-bare-human` and `base-neutral-human`. The Bare, Barefoot and Heels edits take the pose from the incoming image and stay as they are.

## Template review (all families)

| Family | Critical block | Pose / framing | Feet | Finding and proposal |
| --- | --- | --- | --- | --- |
| `1_Alpha/pose-female-human` (Prime) | yes | 6th paragraph | end of Wearing | D2: pose, framing and feet into the Critical block |
| `1_Alpha/pose-male-human` (Prime) | **no** | 5th paragraph | none | D2: add the Critical block, same pose lines |
| `1_Alpha/experiments/base-*-human` (P2, P3) | yes | after fidelity and identity | in the piece | D2: same as the Prime |
| `1_Alpha/bare-human`, `bare-male-human` | yes | none, takes the incoming pose | in the piece | fine; "keep the framing from the incoming image" is already there |
| `1_Alpha/firered-prime-face-lock` | n/a | Framing, 3rd line | none | D3: identity only once D2 is tested |
| `2_Studies/head-human`, `hair-human`, `pose-view-human` | yes | per view | pose-view only | fine; the view templates should say "feet planted" for the full-body views (check when the studies are run) |
| `4_Wardrobe/clothing-human`, `armor-human`, `showcase-*` | yes (optional line) | `{{POSE}}` from data | `Legs & feet:` line | fine; the incoming image carries the full body |
| `5_Scenes/*` | yes (optional line) | `{{POSE}}` from data | `Legs & feet:` line | fine; scene-staged carries no feet line by design |
| `6_Finish/polish`, `final` | n/a | "as in the incoming image" | n/a | fine |
| `Bench/motion-human` | yes | per motion | none | fine |
| `brand/*`, `cards/*`, `dragons/*` | no (one block) | n/a | n/a | out of scope; the dragon pose template has no Critical block, flagged only |

Rule for the review: a stage that builds the body (Prime, P2, P3) states pose, framing and feet explicitly and first; a stage that edits an existing image keeps them from the incoming image.

## Steps

### Done today (Oct 12)

- [x] S1 Seeds: templates fixed (`ST3_FireRed_Final`, `ST0_FireRed_Text`, `ST6_MiniMax_Reel`, `ST6_MiniMax_Match`), `randomize_seed` in `make` and `deploy`, workspace template copies replaced from the masters (backed up), a test that fails on a fixed template. Commit `ff3e274c4`. See E10 of the first plan.
- [x] S2 `inputs sync` (copies the images deployed workflows load into each workspace's input folder; changes nothing else); `refresh` and `refresh-firered` run it; all 18 frame images are in place. E11.
- [x] S3 `Female` photo restored to `Various/gallery` and re-pointed; the chosen Female Prime (00020) kept. E12.
- [x] F1 Frame generation judged on the picture inside a phone screenshot, not the whole screen (`originals.make_frames`), with a regression test; `originals --apply` made the missing frames and pruned the orphans. Every angel, sister and prospect original is now either framed or has a stated reason (full length, head under the phone UI, no face).
- [x] F2 Review of the outstanding items of all four earlier plans (below).

### Open

- [ ] T1 D1: threshold decision, then `originals --apply` and a count of the new frames. Owner: you (decision), me.
- [ ] T2 D2: your approval of the Prime v2 structure and the feet wording, then edit the four templates, add `FEET` to `gen_prompt.py` (with the footwear piece as its source), regenerate, `make --engine both`, deploy, `inputs sync`, tests, validators.
- [ ] T3 Your test of one angel (suggest Angelica or Haniya, whose photos are partial) with and without the frame, old prompt against the new, on Qwen and FireRed: is the body full length, are the feet bare and on the floor, does the face hold (`bin\compare-primes.cmd --shots all HERO`). Owner: you.
- [ ] T4 D3 and D4 from the result: shorten the FireRed lock, and keep or retire the frame process.
- [ ] T5 The 7 angels whose chosen Prime render is in no input or output folder (Camaris 00007, Gavrielle 00007, Nyxene 00019, Ravaelle 00005, Remiah 00005, Sammara 00009, Sandalyn 00006): re-render or re-pick, then `inputs pull`. Owner: you.
- [ ] T6 The male angels and `Male` still have placeholder photos; put originals in their library folders, run `originals`, `inputs set`. Owner: you.
- [ ] T7 Close the loose ends the audit found: the two old Drakness `X_Pose` MiniMax videos are install-only (pull them as curated or delete); the Sovereign Dawn sample workflows load images that do not exist; decide whether `refresh` should also run `originals`.
- [ ] T8 Reconcile this plan with the first-shot plan when T3 is done, then close both.

## Reconciling the plans

What each plan still holds open, and where I think it belongs. Nothing here is moved until you agree.

| Plan | Open item | Proposal |
| --- | --- | --- |
| 2026-10-11-first-shot-flows | E6 your tests, E7 promote the winner | stays; E6 is the same test as T3 here |
| 2026-10-11-first-shot-flows | F5 face pass with a second image (P4) | stays deferred |
| 2026-10-11-tidy-junk-organise | 4.3 compare the Prime flows | same test as T3; close when T3 is done |
| 2026-10-11-tidy-junk-organise | 4.4 two-image face pass | merge into F5, drop here |
| 2026-10-11-tidy-junk-organise | 3.2 classify prospects and artists | stays; independent of the Prime work |
| 2026-10-10-names-ingest-headshots | 5.2 "approval, then the build" of alternate Primes | obsolete: the Prime flows, P2, P3 and the FireRed lock are built; close it with a pointer to the first-shot plan |
| 2026-10-09-finals-and-mvp | photo picks, 12 heroes without a photo, review of the angel pairs | stays; T5 and T6 here are its practical steps |
| 2026-10-09-finals-and-mvp | 5b `mixed` Primes in Angel Primes | same cause as T5; resolve together |
| 2026-10-09-finals-and-mvp | 7.3, 8.5 your FireRed size and video checks | stays |
| 2026-10-09-finals-and-mvp | 3.8, 8.6, 8.7, 6.3b, 6.5, 6.6 and the finals-size note | deferred or low priority; keep as they are |

## Your messages, word for word

### On the frames

I don't see all the \_\_frame\_\_ as input to all of the angels prime angels?  What's up with that?  Only some have \_\_frame\_\_ images set for testing

Remind me again what the frame images was to be used for?  Maybe we don't really need it any more?

Let's hold off on removing - I do want to ensure that I do a comparison of at least one angel with frame to see what it actually does.  If we really don't need - then we'll clean up the entire frame process.

I'm spot checking and I don't see \_\_frames\_\_ for all the images for angels - so seems like something is not working with the frame generation for all the angels, prospects, etc... ideally we have it working - even if we retire it.
Just seems like a few gaps in the frames for all workflows we have setup with frames and what data is in the 944x1104 directories and copied into ComfyUI Inputs

### On the seed

I am also realize that somehow the seed for the FireRed template must be set to fixed number 43 instead of random.  I want them all to be random and I'll only fix the see on any workflows as part of the zz_Final workflows.  I thought we changed that - but maybe the template is wrong.
Some of them are saved properly in the ComfyUI workspace and others are not - so that's a problem with a ton of tests I just queue'd up.  Likely in all workspaces and the template.  Do a deep analysis and see what you find.
Don't forget all the little things we're working on today as there's still a bunch of clean-up and things we need to make right as it looks like a few loose ends from work the other day and we're not 100% consistent across angels, sisters and how we're testing

### On the Prime prompts

I checked B:\Soverign Territories\Angels\gavrielle\frame_944x1104 and I don't see frames for all the images in her gallery.  So there's something not generating there - that could be with more Angels or Prospects.
I also noticed in the past is that if we ensure we mention bare feet and that her feet are planted on the ground for the Prime workflows that are taking cropped images that it can trigger things properly.  Somewhere we have a prompt - maybe one of the archived workflows or maybe prompts - where it's more explicit.
Also that's why in some of the other workflows you see a "Critical" section that calls out the key items at the top in a way that reminds the AI model to generate the image properly.  Let's evaluate all the prompt templates and I think there is opportunity with the Prime ones to adopt some of that as well.
Moving the pose up to the top because that's one things that's the biggest issue with the cropped versions coming in.  I am still testing the frames to see if that matters - but I suspect that we're just not making the full A Pose properly called out to FireRed and Qwen is more fogiving about that.
Please do a deep dive review, write up a plan for all the work we are doing today so we don't lose something.  It's a continuation of yesterdays plan - so if you want to adapt that we can do that - but we've got a few new things we're seeing and eventually we do need to reconcile the plans from yesterday and the plans for today.
