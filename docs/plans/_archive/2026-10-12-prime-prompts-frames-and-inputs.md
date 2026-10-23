# Plan: Prime prompts (pose first), frames, library sync, seeds and inputs

**Status:** dropped (superseded; not completed)

## Supersession record

**Superseded:** 2026-10-22T16:34:08-05:00 (local offset recorded).

**Reason:** the Oct 22 full-plan reconciliation separates enduring rules,
dated evidence and focused execution owners. Later approved direction
supersedes conflicting older sequencing/limits; remaining work is not done.

**Context:** [live reference](../../art/prompt-migration-context.md), [full reconciliation audit](../../audits/2026-10-22-plan-feedback-audit.md).
Original user wording and historical evidence are retained below.
The source checklist is historical; formerly open items are explicitly
marked transferred, not checked off as implemented.

## Unfinished work and successors

| Source item | Live owner | Destination / disposition |
| --- | --- | --- |
| T2 | [2026-10-22-manual-prompts-to-art-library.md](../2026-10-22-manual-prompts-to-art-library.md) | P2/P4/P5/P7 |
| T4 | [2026-10-22-manual-prompts-to-art-library.md](../2026-10-22-manual-prompts-to-art-library.md) | P5/P6 |
| T5 | [2026-10-09-finals-and-mvp.md](../2026-10-09-finals-and-mvp.md) | I1 |
| T6 | [2026-10-09-finals-and-mvp.md](../2026-10-09-finals-and-mvp.md) | I2 |
| T7 | [2026-10-09-finals-and-mvp.md](../2026-10-09-finals-and-mvp.md) | I3 |
| T9 | [2026-10-22-manual-prompts-to-art-library.md](../2026-10-22-manual-prompts-to-art-library.md) | P2/P7 |
| L4 | [2026-10-22-library-upkeep.md](../2026-10-22-library-upkeep.md) | U3 |
| L7 | [2026-10-22-library-upkeep.md](../2026-10-22-library-upkeep.md) | U4 |
| T11 | [2026-10-22-manual-prompts-to-art-library.md](../2026-10-22-manual-prompts-to-art-library.md) | P9 |

## Result of reconciliation

Retired as an execution owner after task and context transfer. Archival
does not assert implementation, render approval, convergence or production
acceptance. Live owners above retain the remaining gates and questions.

## Original source record

**Original status:** active (Oct 12, 2026; Prime frame flow retired Oct 19; prompt decisions and ComfyUI tests remain open)

This records the Oct 12 Prime, input and library work, continuing [2026-10-11-first-shot-flows.md](2026-10-11-first-shot-flows.md). The Prime frame flow and its comparison were retired on Oct 19; the remaining prompt decisions and ComfyUI tests are still open. The two plans' frame-related history is reconciled below.

Source: your messages of Oct 12, copied word for word at the end. Related: [../art/prime-flows.md](../../art/prime-flows.md), [../art/original-photos.md](../../art/original-photos.md), [../art/likeness.md](../../art/likeness.md), [../../workflows/README.md](../../../workflows/README.md).

## Why we are doing this

At the time, you queued a large batch of Prime tests and found several things at once: some FireRed workflows ran with a fixed seed, some frame images were missing in ComfyUI, the frame folders did not hold a frame for every photo, the cropped Primes came back cropped (FireRed more than Qwen), and the templates were not consistent about calling out the pose.
The library then needed its scaled copies, headshots and frame images brought back in step with the galleries. The frame flow has since been retired; library sync and new-photo likeness checks remain part of the current routine.
The goal is a Prime that is reliable on cropped photos, a library whose derived images always match its galleries, every test input where ComfyUI can load it, and a record of why each change was made.

## What we found (the deep dive)

| # | Finding | Evidence | State |
| --- | --- | --- | --- |
| 1 | The FireRed and MiniMax templates shipped with the seed control set to `fixed` (43 and 1). Every workflow made from them ran with the same seed | the inner KSampler and the named copy in `ST3_FireRed_Final`, `ST0_FireRed_Text`, `ST6_MiniMax_*`; 1,585 FireRed and 102 MiniMax repo workflows and about 1,500 workspace copies were fixed, Qwen was already random | fixed Oct 12 (S1) |
| 2 | `make` and `deploy` only ever kept the seed of an existing workflow, so a template fix would never have reached the copies | `patch_wf` touches the prompt and the save prefix only | fixed (S1): both now set randomize when no final record exists |
| 3 | Frame, experiment and restored images were not in the workspaces' input folders: only `inputs reset` copied images, and it refuses to run while you hold an unpulled Prime pick | 18 frame images, 0 to 1 of 16 input folders each | fixed (S2): `bin\sync-inputs.cmd` |
| 4 | `Female` (alpha/female), the first test subject, loaded a photo that no longer existed outside `_backup` and `_archive` | the Fantasy artist folder was reorganised on Oct 10; the photo is Sandalyn's review photo | fixed (S3): restored to `Various`, re-pointed |
| 5 | **Frame generation skipped reel screenshots.** `make_frames` tested the face against the whole phone screen (1080x2340, with the app bars) before cropping to the picture, so a face that is 0.127 of the screen but 0.21 of the picture counted as full length | Gavrielle: 4 gallery screenshots, 2 frames; after the fix 3 (the fourth has her head under the phone UI) | fixed at the time; frame generation retired Oct 19 |
| 6 | The "partial photo" threshold (`FRAME_FACE_MAX` 0.14, face brow to chin as a share of the picture) may be too high. A standing figure's face is about 0.09, so 0.11 to 0.14 means cropped at the thighs or knees, and no frame | 482 angel and sister photos: 378 above 0.14, 55 from 0.11 to 0.14, 37 from 0.09 to 0.11, 12 below. Chosen: Sammara 0.086 (full length), Draknira 0.124, Drakniya 0.133 | superseded: frame flow retired Oct 19 |
| 7 | The library still held orphans of removed originals (a `gallery_944x1104` copy and a frame of `gavrielle_shot_20261010124337` whose original is gone). They are pruned to `_archive` by the normal `originals` run | the run of Oct 12 | done with F1 |
| 8 | The Prime prompt buries the pose. In the generated prompt the order is: intro, Critical details, camera, background, fidelity, then Standing A-pose, Figure, Skin, Wearing; and "bare feet planted flat on the floor, slightly apart, toes pointing forward" sits at the very end of the long swimsuit sentence | `pose-female-human.txt`; `Gavrielle_Alpha_1_Prime.txt` | open: decision D2 |
| 9 | The explicit feet wording you remember is real: 120 saved Prime candidates carry "bare feet planted flat on the floor, slightly apart with the toes pointing forward, natural relaxed toes, no shoes". The current Prime still has it, but only inside Wearing, and the "no shoes" half lives in the Qwen negative prompt | `workflows/_candidates/angel-primes/*/1_Alpha/1_Prime` | open: D2 |
| 10 | FireRed has no negative prompt. Everything the Prime says against shoes, heels, a cropped body or a wrong pose is invisible to it; only positive wording counts. The FireRed lock adds Face, Head and Framing in front, but the A-pose paragraph is still the ninth | `engine_prompt`, `firered-prime-face-lock.txt` | open: D2, D3 |
| 11 | The male Prime template has no Critical block at all (`pose-male-human.txt`), so the structure differs between male and female heroes | template inventory below | open: D2 |
| 12 | The experiment templates (P2, P3) carry Framing and Standing A-pose after the fidelity and identity lines, not in the Critical block, and say nothing explicit about the feet beyond the garment piece | `base-bare-human.txt`, `base-neutral-human.txt` | open: D2 |
| 13 | **The derived images were out of step with the galleries.** Before the Oct 12 run the library needed 6 renames, 6 scaled copies, 6 headshots and 44 frames, and had 1 orphan (a copy of a photo you moved away). Root cause: `originals` was not run after the likeness reviews and file moves | the preview of Oct 12 before `--apply` | library sync fixed; frame generation retired Oct 19 |
| 14 | Not every gallery photo has a headshot, by design: of 1,114 galleries 63 had a face too small to enlarge to 944x1104 without mush (a crop under 30% of the output height) and 10 had the head under the phone's app bars. The Oct 12 audit reported scaled, headshot and (then-existing) frame copies | audit of Oct 12 after the run | historical count; frame flow retired Oct 19 |
| 15 | One gallery photo had no scaled copy: `Various/gallery/sandalyn_image_7500732784539999043.jpg` was the same picture as `various_image_7500732784539999043.jpg` (Female's photo). The new `duplicates` step found it and 14 more identical pairs under different ids | `bin\duplicates.cmd` (Drakness 2, Drakneta, Draknira, Draknisa 2, Dara Ives, Greta Hart, Mia Wolfe 4, Rachel Pizzilato, Uma Dunn) | fixed (L6): the extra copies are in `_archive\...\gallery_duplicates` |
| 16 | The new photos are in `Various\gallery` (the pool `likeness sort` empties), not in `Prospects\gallery`, which does not exist. The review folders had been emptied into it: 32 photos | folder listing | handled (L2) |
| 17 | The prompt sequence differs from template to template (position of the Critical block, of the background, of the pose). See the ordering table below | all 31 hero templates read | open: D6 |

## Decisions

| ID | Question | Recommendation | Answer |
| --- | --- | --- | --- |
| D1 | Lower `FRAME_FACE_MAX` from 0.14 to about 0.11 so thigh and knee shots get a frame? | No longer applicable: the frame flow is retired by decision on Oct 19; see [2026-10-19-library-rebaseline-and-frame-retirement.md](2026-10-19-library-rebaseline-and-frame-retirement.md). | resolved |
| D2 | Put **Pose, Framing and Feet** at the top, inside the Critical block, for the Prime, the male Prime and the P2/P3 experiments? Draft wording below | Yes: it is the strongest lever we have and costs no new data. Keep the feet line data-driven from the footwear piece | open: needs your approval before any template is edited |
| D3 | Once D2 is in, shorten the FireRed lock to the identity lines (Face, Head) and let the template carry Framing, so the two engines get the same pose wording? | Yes, after one test that shows FireRed keeps the full body | open |
| D4 | Keep, retire or extend the frame flow? | Retire it (user decision, Oct 19); preserve existing files in archives. Implementation is tracked in [2026-10-19-library-rebaseline-and-frame-retirement.md](2026-10-19-library-rebaseline-and-frame-retirement.md). | decided |
| D5 | Should a hero whose chosen photo has no body at all be flagged? | Later, with F7 of the first plan: a face-only vs body-shot tag when the prospects are classified | deferred |
| D6 | Any template may have a Critical details block. Agree one **canonical paragraph order** for every template that builds or edits a picture, then bring each template to it? Proposal below | Yes, stage by stage with a byte-for-byte check of what did not change, Prime first | open: you said you are fine with the in-depth analysis |
| D7 | The likeness run of Oct 12 (L2): keep the 19 new prospect folders and the 2 merges, and review the suspects (Zara Lane, Tove Wilde, Delia Ames) before anything is cast? | Keep; nothing is cast from them until you look. `likeness merge` fixes a wrong split | open |

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

## Prompt sequence: what the templates do today and a canonical order (D6)

The order of the paragraphs is read from the templates themselves (`{X}` is a data tag, `K` is the Critical block). Models weigh what comes first, and a late paragraph is the first to be dropped.

| Template | Order today |
| --- | --- |
| Prime female | task > K > camera > Background > fidelity > **A-pose** > Figure > Skin > Wearing > Hair > makeup > Eyes > Lips > Expression |
| Prime male | task > camera > Background > fidelity > **A-pose** > Figure > Skin > Wearing > Hair > makeup > Eyes > Expression (no K, no Lips) |
| P2, P3 | task > K > camera > Background > fidelity > Face > From the reference > Head > Framing > **A-pose** > Figure or Body > Skin > Wearing > Hair > makeup > Eyes > Lips > Expression |
| Bare, Bare male | task > Result > K > Body > keep line (no shared keep line) |
| hair study | task > Background > fidelity > K > keep outfit > breeze > hair change > extras |
| head study | task > Background > Framing > View > keep line > K > Expression > Eyes |
| pose views | task > Background > keep line > K > **A-pose** > View > keep outfit > Eyes > Expression |
| clothing, armor | task > Background > keep line > K > Strip > Contour > Wearing > Headwear > Arms > Jewelry > (Back) > Legs & feet > Overall > Eyes |
| showcase (studio, photo) | task > keep line > K > Strip > Contour > Wearing > pieces > **Pose** > Holding > Effects > Eye effect > Makeup > Backdrop or Realm |
| scenes (outfit, companion, glamour, combat, minimal) | task > keep line > K > Contour > Wearing > pieces > **Pose** > Holding > Effects > Eye effect > Makeup > Companion > Environment > Realm |
| scene staged | task > K > Pose > Effects > Eye effect > Companion > Environment > Realm > breeze > Palette > framing |
| motion bench | task > Background > Editorial > keep line > K > keep outfit > breeze > Body > Head > Gaze > Expression > Eyes > Pose > extras |
| polish, final | task > keep line > keep pose, outfit, framing |

What stands out: the Critical block is the 2nd, 3rd, 4th, 5th or 6th paragraph depending on the template; Background comes before the Critical block in six of them and last in two; the pose is a late paragraph in the Prime and in every showcase and scene, and appears in no Critical block; the male Prime has no Critical block at all.

Proposed canonical order, in two flavours (nothing is edited until you agree):

| Flavour | Order |
| --- | --- |
| Builds the body (Prime, P2, P3, male Prime) | task > **Critical details: Pose, Framing, Feet, then Hair, Bust, Eyes, Skin, Legs** > fidelity and identity > camera and Background > Figure > Skin > Wearing > Hair > makeup > Eyes > Lips > Expression |
| Edits an existing image (studies, wardrobe, showcase, scenes, motion) | task > **Critical details** > keep line > camera and studio Background > the change itself (view, hair, strip and contour, Wearing and pieces) > Pose > Holding and Effects > eyes and makeup > the scene Environment and Realm last |

Notes: a scene's Environment stays last because it is the content of the scene, but a studio Background is camera set-up and moves behind the Critical block and the keep line. Each template keeps its own optional lines (`?` lines). Once an order is agreed, each family is changed in its own step, regenerated, and the prompts that should not have changed are checked byte for byte (the Oct 11 stage-folder move did this for 5,373 prompts).

## Steps

### Done today (Oct 12)

- [x] S1 Seeds: templates fixed (`ST3_FireRed_Final`, `ST0_FireRed_Text`, `ST6_MiniMax_Reel`, `ST6_MiniMax_Match`), `randomize_seed` in `make` and `deploy`, workspace template copies replaced from the masters (backed up), a test that fails on a fixed template. Commit `ff3e274c4`. See E10 of the first plan.
- [x] S2 `bin\sync-inputs.cmd` (it already existed; I had written a duplicate `inputs sync` first and removed it, lesson in "How we work" below) copies the images the deployed workflows load into each workspace's input folder; it now counts the `_00000` placeholders apart from the NOT FOUND list; `refresh` and `refresh-firered` run it. The 18 then-configured frame images were in place at the time and were archived with the flow on Oct 19. E11.
- [x] S3 `Female` photo restored to `Various/gallery` and re-pointed; the chosen Female Prime (00020) kept. E12.
- [x] F1 Frame generation was judged on the picture inside a phone screenshot, not the whole screen (`originals.make_frames`), with a regression test; `originals --apply` made the missing frames and pruned the orphans. At the time every angel, sister and prospect original was either framed or had a stated reason; the generation and Prime flow were retired on Oct 19.
- [x] F2 Review of the outstanding items of all four earlier plans (below).
- [x] L1 Library sync: `originals --apply` brought the scaled copies, headshots and then-configured frames in step with every gallery (6
  renames, scaled copies, headshots, 44 frames, orphans to `_archive`), and a new `originals --check` (also `bin\originals.cmd --check`)
  says IN SYNC or OUT OF SYNC and exits 1 when anything is left, with a test. Audit afterwards: 1,114 galleries, no orphans, the only gaps
  are the by-design headshot skips (finding 14) and one duplicate (finding 15). Frame generation was retired on Oct 19.
- [x] L2 Likeness on the new photos (the pool is `Various\gallery`): `likeness sort --singles` moved 30 of the 32 photos (19 new prospect folders, 1 into Vera North; the plan is saved in `_reports\sort_plan.json`).
  `likeness singles --min 0.45` merged Zoe Dale into Zara Lane (the stricter 0.45 instead of the default 0.35 so only confident merges happen; 45 single-photo prospects are left for you), then `originals --apply` and `--check` (IN SYNC) and `likeness index`. 4 photos with no usable face stay in `Various`.
- [x] P0 Analysis of the prompt order of all 31 hero templates (table above) and the canonical order proposal (D6).
- [x] L5 **`bin\library.cmd`**, the one command for the photo routine (`tools/art/library_sync.py`): originals, duplicates, likeness junk (and `--recheck`), review, sort --singles, singles --min 0.45, then duplicates and originals again, `originals --check`, `sync-inputs`, `likeness index`.
  It prints a before and after summary and writes a log in `_reports`. `bin\library-preview.cmd` previews every step, `bin\library-check.cmd` is read only (exit 1 when work is waiting).
  Run end to end through the launchers on Oct 12 (first full run: 15 duplicate pairs archived, 10 photos to `_junk`, Sabine Jasper merged into Tove Wilde at 0.45, 6 review photos stay in review, the result IN SYNC); tests in `test_library_sync.py`; in `bin\help.cmd`, `bin\menu.cmd` (L, C), `docs/art/original-photos.md` and `likeness.md`.
- [x] L6 **`bin\duplicates.cmd`** (`tools/art/duplicates.py`): identical pictures under different names or in different folders (by bytes,
  so a moved photo with a new name and the same id is caught too; the same id with different bytes is listed for you). One copy is kept (a
  chosen photo first, a gallery over review, Angels, Sisters, Prospects, Artists, Various), the rest go to
  `_archive\<folder>\gallery_duplicates`. First run: 15 pairs found and moved; tests in `test_duplicates.py`.
- [x] W1 How we work: `.github/copilot-instructions.md` now says to run the `bin\*.cmd` launchers (not raw Python), to read `bin\help.cmd` before writing anything new, and to turn any multi-command routine into a launcher with a preview and a check. A duplicate `inputs sync` that I had written next to the existing `sync-inputs.cmd` was removed for exactly this reason.

### Open

- [x] **P2 you** T1 D1: frame threshold and frame generation are superseded by the Oct 19 decision to retire the frame flow; see [2026-10-19-library-rebaseline-and-frame-retirement.md](2026-10-19-library-rebaseline-and-frame-retirement.md).
- **Transferred, not completed:** **P1 you** T2 D2: your approval of the Prime v2 structure and the feet wording, then edit the four templates, add `FEET` to `gen_prompt.py` (with the footwear piece as its source), regenerate, `make --engine both`, deploy, `bin\sync-inputs.cmd --apply`, tests, validators.
- [x] **P1 you** T3 The proposed frame-vs-normal comparison is dropped by the Oct 19 decision to retire frames; the unrelated prompt tests remain in T2/T9 and the active manual-prompt plan.
- **Transferred, not completed:** **P2 you** T4 D3: test and, if warranted, shorten the FireRed lock.
- **Transferred, not completed:** **P1 you** T5 Recheck current Angel Primes inputs after the selected-photo changes and resolve only the Prime renders still missing from an input or output folder. The seven names and render IDs recorded here are an Oct 12 snapshot; the four explicitly chosen replacements are Aria Muse → Gavrielle, Ruby Eden → Camaris, Amethyst Montgomery → Ravaelle, and Sabine Vale → Nyxene. Re-render or re-pick only if the current status confirms it is needed, then pull the input.
- **Transferred, not completed:** **P1 you** T6 The male angels and `Male` still have placeholder photos; put originals in their library folders, run `originals`, `inputs set`. Owner: you.
- **Transferred, not completed:** **P3 you** T7 Close the loose ends the audit found: the two old Drakness `X_Pose` MiniMax videos are install-only (pull them as curated or delete); the Sovereign Dawn sample workflows load images that do not exist; decide whether `refresh` should also run `originals`.
- [x] **P2 ai** T8 Reconcile the frame-related decisions with the first-shot plan after T3 was dropped. Completed Oct 19; both plans remain active for their unrelated, unfinished Prime tests and user decisions.
- **Transferred, not completed:** **P2 you** T9 D6: your approval of the canonical order, then change the templates family by family (Prime first with D2, then the male Prime, P2/P3, studies, wardrobe, scenes, motion), regenerating and checking byte for byte what should not change. Owner: me after your approval.
The old T10 prospect names and scores are stale after later library runs; review the current photo outcomes through R11 and candidate rankings through D10 instead.
- **Transferred, not completed:** **P3 either** L4 Decide whether `likeness pairs --apply` and `merge` should also finish by running `originals` (today only `library.cmd` ties the steps together). Owner: you (decision), me.
- **Transferred, not completed:** **P3 ai** L7 Later: `duplicates` compares bytes, so the same picture saved at another size or quality is not caught (it would show as two look-alike photos in one folder). A face-embedding check inside one folder (a score above about 0.98) could list them. Owner: me when you want it.
- **Transferred, not completed:** **P3 you** T11 Confirm that the variant Primes of the Oct 10 plan (5.2, a Prime B per hero) are dropped: the Prime flows replaced them. That plan is closed and archived on this assumption.

## The routine when photos move

Drop new photos into `Various\gallery` and run `bin\library.cmd` (details in [../art/original-photos.md](../../art/original-photos.md#the-routine)). `bin\library-check.cmd` before a batch of tests says whether the library is in step. Anything done by hand (moving a photo between folders, `likeness merge`, `retire`, `pairs --apply`) is followed by `bin\library.cmd --no-likeness` (names, duplicates, scaled copies, headshots, frames, check).

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

## Preserved original discussions (verbatim)

<!-- markdownlint-disable MD013 -->
````text
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

### On the plan, the headshots, the Critical block and the new photos

Make sure you decide on which plan .md we're working from with all the items for today and update that.  Don't forget anything we've done or what we need to do.  I feel like the same might be true for headshots as was with frames - not being in sync with the generated gallery.
So - if you found root cause for frames - likely issues with headshots.  We need to ensure that all 3 scaled and padded outputs are in sync with their respective gallery as we move files in and out based on the reviews.  It's likely that's the cause - we didn't run the generation after we did the likeness reviews and shuffling of files.
Lastly - when it comes to the templates, any of them can have Critical Details section where we put the most important pieces of the prompt and then follow with the remaining pieces.  So - I'm ok if we do a more in depth analysis of prompt sequence ordering for the purpose of the prompts and we get the right order.
Finally, I have put a bunch more photos into the B:\Sovereign Territories\Prospects\gallery so we can run the likeness checks to see where those need to be put as they were all in review somewhere and might actually match now with an Angel, Sister or Prospect.  So - we can re-run the likeness checks, have the files moved and then re-run the entire generation of the 944x1104 images and get the entire structure in sync.
Sorry for disturbing you, but lots of stuff happening right now.

### On the repeatable library command and how we work together

I need a repeatable bin .cmd that can run the entire process when I drop in new images to the Various directory and want to do a complete end-to-end likeness process and then re-generate all the scaled and padded images.
It should also look for duplicates across the directories in case I do have multiple of the same image that happens through the process.  I am guessing that could happen based on moving an image between prospects and the name changed, but the guid is the same.
Ultimately I plan on iterating on prospects - over and over as time goes on.  So want something that repeats and doesn't require as much intervention, re-running and processing so many commands.
Maybe we need multiple complex .cmd files that just allow me to run a simple command without a lot of arguments to make things happen.  That way I don't need to remember the arguments.
There might be some already in bin and ideally your instructions should have you running the .cmd files to always ensure they are working.  So that's yet another optimization in how we work together to ensure that both you and I can do the same thing together.
Don't forget where you are - but take this all into account after you get through the process.
````
<!-- markdownlint-enable MD013 -->
