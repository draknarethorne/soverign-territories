# Plan: tidy the library, junk and screenshots, organise people for the lower tiers

Status: active, Oct 11, 2026 (Phases 1 to 3.1 done; the classification itself, Phase 3.2, is yours and grows one element at a time)

Source: your three notes, copied word for word at the end. Report: [../art/likeness-reorg-2026-10-10.md](../art/likeness-reorg-2026-10-10.md) (the Oct 11 section). How-to: [../art/likeness.md](../art/likeness.md), [../art/original-photos.md](../art/original-photos.md).

## What you asked for

1. Do we still need the `_org` folders and other backup copies? They make it easy to pick the wrong duplicate.
2. Screenshots carry text and icons over the picture; remove it, crop it, or discard them to a `_junk` or `_recycle` place you review. Single-photo prospects look like a symptom.
3. Organise prospects and artists so you can find "a good dark-elf rogue" or "a barbarian princess" for the lower-tier cards, without opening each `z_` file; one person can have several roles, races and elements. Males and creatures will come.
4. (Added Oct 11) Prospects and artists come from different sources and must never be mixed by the likeness checks; artists are for the art, not for the angels' Prime photos.
5. (Added Oct 11) FireRed needs `head-to-toe` in the A-pose prompt, and Prime hair should not be braided.

## Decisions

| ID | Question | Answer |
| --- | --- | --- |
| P1 | Archive layout for `_org` and other old copies | A mirrored `<work>\_archive\<same path>`; moved with a manifest, undo with `originals --undo-archive`. New prunes go there too. |
| P2 | Junk folder | `<work>\_junk\<same path>`; you empty it. `likeness junk` moves, `likeness undo` puts back. |
| P3 | Screenshot text | Facebook phone screenshots have a fixed layout, so the bars are cut away exactly (`tools/art/screens.py`): the scaled copy and the headshot use the clean part. A head that reaches into the bars cannot be fixed by cropping and goes to `_junk`. Inpainting is not built (not needed for these). |
| P4 | Where race, role and element live | In the `z_` file as profile lines (`sex`, `type`, `roles`, `elements`, `tier`, `tags`; several values allowed) and in a generated table `people_index.csv` / `.md` at the library root. Folders stay by status (Angels, Sisters, Prospects, Artists). |
| P5 | Males and creatures | Not built. When they arrive they get the same layout under their own roots (for example `Brothers`, `Creatures`); `sex` and `type` already describe them. |
| P6 | Prospects and artists | Never mixed: a photo is not moved between them, nor merged (`side` and `apart` in `likeness.py`); new people split from an artist's person stay in the artist's folder. |
| P7 | Azaline | Mara Locke (Pierre) did not work out: artist images are too fantasy. Artists are for pulling art, not for Prime photos. `pairs` never picks an artist's person now, and an angel who is one (found from her `z_` history) is replaced and her photos go back to the artist. Oct 11: Azaline is now Eva Emily (0.22 against Draknira) and Remiah is Dara Yates (0.26 against Drakneta). Camaris keeps her photo (no candidate in the band). |
| P8 | Hair in the Prime | A Prime photo asks for simple hair; braids come in the later hair phase. The three heroes whose Prime hair was a braid now have another style (Haniya: side-swept over the shoulder, Sandalyn: half-up half-down, Verael: textured crop). Ponytails and pulled-back styles stay. |
| P9 | FireRed full body | The A-pose prompt says `head-to-toe` in its first line and in the "Professional head-to-toe, full-body" line, so FireRed does not return partial-body photos (both pose templates, female and male). |

## Steps

### Phase 1: the archive

- [x] 1.1 `originals` writes prunes to `_archive`; `--archive-old` and `--undo-archive`; tests.
- [x] 1.2 Run on the library: 44 folders, 1,416 files (1.6 GB) moved out of the person folders.
- [x] 1.3 Empty shell Cleo Park (its photos went to Sandalyn's review); Kylie Voss retired.

### Phase 2: junk and screenshots

- [x] 2.1 `likeness junk`: no usable face, a face under 60 px, a real second person (second face at least 0.3 of the main one), the app's bars over her head. An angel's or sister's own gallery and a chosen photo are only reported. `_junk` is flat (`_junk\Prospects`, `_junk\Artists`; the person is in the file name). `junk --recheck` sends usable photos back to their folder. Result: 53 photos in `_junk` after the recheck.
- [x] 2.2 Reel screenshots cut to the picture in the scaled copies and headshots (91 screenshots; 58 of them had the head under the bars before the bars were measured exactly). All scaled copies and headshots rebuilt.
- [x] 2.3 `likeness singles`: a single-photo prospect that looks like another prospect (0.40 or more) is merged; two were.
- [x] 2.4 The face detector tries again less strictly when it finds nothing (the last two Various photos were found this way; Various is empty).

### Phase 3: organising for the lower tiers

- [x] 3.1 Profile lines in `people.py`; `likeness index` (CSV and markdown), `index --import`, `profile`, `who`; tests.
- [ ] **P1 you** 3.2 Classification with you, one element at a time (Darkness and Light first). Fill the profile columns of `people_index.csv` and import them, or use `likeness profile`.

### Phase 4: the Prime input and the templates (Oct 11, from your headshot-first thoughts)

- [x] 4.1 `_templates/heroes` split by stage folder (1_Alpha ... Bench) with a README and `template_path`; 5,373 prompts byte-identical.
- [x] 4.2 `originals` originally wrote `frame_944x1104` for partial-body photos. This generation was retired on Oct 19; see [the library rebaseline plan](2026-10-19-library-rebaseline-and-frame-retirement.md).
- [x] 4.2b (corrected Oct 11) The frame experiment used a separate `flows.frame` input and `_Frame` Prime workflows beside the normal workflows. That flow and its generated assets were retired and archived on Oct 19; the normal photo flow remains.
- [x] 4.2c FireRed identity lock: `engines.firered.primeFace` puts `1_Alpha/firered-prime-face-lock.txt` in front of the FireRed Prime prompt; Qwen is untouched.
- [x] 4.2d `bin\compare-primes.cmd`: newest render of each variant per hero, a picture and a face score against the photo each flow started from, with the average per variant.
The remaining active Prime-path comparison is consolidated into E6 of [the first-shot plan](2026-10-11-first-shot-flows.md): test P1/P2/P3 with Qwen and FireRed as appropriate; do not test frame variants.
- [ ] **P3 ai** 4.4 If the active Prime tests show a specific need, consider a face pass with two images (bare bust plus original headshot), a beta template and a generator change. Do not add a pose-frame input.

## Result so far

The person folders hold only what is live. `_archive` and `_junk` hold the rest. 107 person folders, all with a `z_` file. Next for you: open `people_index.csv` and start classifying; review the current `_junk` inventory through R11 in [the Oct 19 library plan](2026-10-19-library-rebaseline-and-frame-retirement.md).

## Your notes, word for word

### org_directories_remove.md

I'm wondering if we still need all the _org directories or any other backup gallery and other files that were in the directories when we started the process.
It's not a huge problem - but we have a lot of duplicate images in all the folders and I can see myself picking a wrong one if I don't pay close attention to where I am looking.
If we needed to move them all into _backups and _originals/xxxxxx with the original directory structures - maybe that's better place for things like the original versions of images and any other reference material that we might want to keep without cluttering the main directories.

### screen_shot_garbage.md

I also realized that many screenshots include text and other things overlaid on the images - I'm wondering if we can eliminate that in the process we have or if you think that it won't cause issues feeding into the prime workflow to produce the initial a pose?
If there is an easy way with the tools we have to "erase" that and make the picture look accurate for what was removed, that's awesome - if it's a potential problem, I will just see what the comfy workflow does and if it includes the text - I can discard the screenshots.
Some images might be fixed easy enough with cropping the top and bottom off - as long as the persons face is visible and we don't really need the bottom pieces.
If cropping would remove the top of a head - well that wouldn't be good as the text is a transparent background so "some" of the real person is visible.
If the text is causing problems with likeness and we can't crop or remove it then those screenshots might just need to be discarded entirely to maintain the quality of the prime workflow inputs.
Using the _junk or _recycle folders so I can do a review before actually deleting.
It'll reduce clutter of having some single images for characters as I see a few popping up in headshots with the text over their hair and I'm pretty sure that if the image were clean it would link to another prospect, angel or sister.
I'm just seeing a lot of Prospects with single images and it feels like something is driving it as I think they should be an image of someone already classified.
Not exactly sure the cause or if the image is touched up or the angle of the persons face is driving it.
Ultimately I want to avoid having images where it looks like it's actually another card because of how things render.
I'm open to testing with all these cards and circling back.
Just observations I am making along the way.
B:\Soverign Territories\Prospects\Rhea Ives is a good example as I think the angle of the face is driving it to be unique and maybe it's just not a good image to be using - or maybe the ai models will actually invent a nice face that's unique and not use generic pieces that look the same across these types of images.

### prospects_organization_.md

I'm wondering if there is a better way to organize the prospects in a way that might help me target where to use them in the future?
Once we settle on the sisters and angels, then we can create a clear structure for the remaining prospects, categorizing them based on their roles, attributes, or any other relevant criteria.
It might help me figure out for the lower tier cards if they are best suited for our planned races (dark elves, high elves, wood elves, orcs, humans, etc.)  Those lower tier cards may still be more "human-like" and just with traits of the races they belong to.
The other option is to align them to warriors or other specific archetypes that fit within our world-building framework.
I'm also wonder if the same should hold true for the Artists - even though there are less (right now, but I may bring in more artists work over time) so having some classification system or categorizing them might help.
I might bring in succubus, demons, and other fantasy creatures as separate categories to keep the organization consistent and clear.
Basically the lower cards will be all sorts and I will want to use prospects and artists to drive the prime images of those cards as well.
While we've been focused on females, I will get males as well - so yet again another classification type twist so it's easy to comb through files and when it comes time to pick, we might already know where to pick from for a card - and it'll also be obvious if I need to find more images for any gaps as we start to build out the lower portion of the decks for each element.
That's also a potential piece of data as well.
I honestly don't know what the right way to organize them is ... but it's clear to me with prospects that I have so many and the name alone isn't helping.
So it could be a combination of the directory structure and filename - as well as in the z_ file ... but I still need structure so I'm not having to read each z_ file - that would just explain "why" it was classified the way it was.
Yet again, I found another big ask for you.
If you need to read through the docs to see the types of elements, cards, etc... the bible and codex docs should help as well as the larger .json codex that has a skeleton of the deck.
We still need to build that out for all the elements and cards in the Soverign Dawn series - but things are still in flux so we can go.
It's also possible that I just choose a blank image and focus on letting AI totally drive the prime card from .json card art for things that aren't as good at finding art.
I do plan to find some dragons as the base for the elder dragons as well.
For now we might totally define them - but if we apply that onto an existing dragon - at least the frame, and some features should come through as well as the description prompt we apply.
What do you think about all that?
As we do that the B:\ directory of images will evolve - so we're just taking things a step at a time, but also reflecting on the bigger picture of ALL the art we will be doing in the future.
I'm also thinking that the z_ file could also contain who this person most looks like - if there are close similarities, so we can avoid using these cards or might use cards in tandem - like pairs of images for various elements - sort of like we are doing with pairs of sisters and angels, but maybe I figure out another way to pair cards across the decks OR avoid those pairs.
I'm also considering whether some images don't look like another person since the image might have eyes closed or the image won't actually be useful in feeding into the prime workflow.
If something scores really "low" in terms of what the person looks like, maybe those are _recycle type images in some structure and we don't put them into the actual directories and generate scaled or head-shots for them.
Basically, discarding a "junk" image that I might have grabbed - but won't be useful.
That allows me a little more freedom just to grab all sorts of images and we filter those out if we see them as they come in (or are already put into directories and we can clean things up if it's not a usable image)

## Raw notes: headshot first (Oct 11)

Your words, kept as written (only wrapped).

# Headshot-first and a pose library: my opinion (draft, no decision)

Source: [dual-input-thoughts.md](dual-input-thoughts.md).

## What actually fails today

1. A partial-body source (head and shoulders, waist up) goes into the Prime at denoise 1.0 and the edit model keeps the source's framing. Qwen re-frames; FireRed mostly does not. So the problem is **scale and framing**, not identity.
2. In a head-to-toe 944x1104 frame the face is about 130 px tall, so eyes, lips and makeup get little detail, and each later pass (Bare, studies) inherits and slightly drifts the likeness.

These are two different problems, and the document solves the second with a method that makes the first harder (a gray mannequin as a second image).

## What I would take from the document, and what I would not

| Idea | My view |
| --- | --- |
| Do the eyes, lips and makeup at close-up scale | Yes. We already have the stage (`head-human`, FireRed, 0.7 to 0.8) and the `headshot_944x1104` images. The gain is in using the **original** headshot as a second reference at the end, so the likeness does not drift through Prime and Bare |
| Separate identity from build | Yes in principle. The build is already text in the Bare prompt (`FIGURE`, per hero), so we do not need a body library for it |
| A library of three gray clay mannequins fed as image 2 | Not first. An edit model treats image 2 as content to blend, not as a strict skeleton (that needs ControlNet or OpenPose, which our workflows do not have): expect gray skin, a bald head and the mannequin's pose leaking in. Three bodies also do not cover the heroes' distinct builds, and Bare reshapes the body anyway |
| 512x768, turbo, FLUX polish | Our standard is 944x1104 and `ST4_Flux_Polish` exists; nothing to add there |

## What I would try, cheapest first

**Oct 19 update:** The frame-input experiment was retired; do not implement or test
options 1 or 4. The separate chest-crop review is tracked as R9 in the Oct 19
plan. The dual-image face pass remains only a possible follow-up to E6.

1. **Retired (Oct 19): framed input.** `originals` no longer creates partial-body
   frame images; the former Prime frame flow and its derived files are archived.
   See [the library rebaseline plan](2026-10-19-library-rebaseline-and-frame-retirement.md).
2. **Engines by job.** Qwen for Prime and Bare (framing and body); FireRed for the close-up, polish and the face pass (skin, eyes). This is what you already see.
3. **A face pass with two images (the real use of dual input).** After the Bare, crop the bare bust, then run one edit with image 1 = that bust and image 2 = the original headshot: keep the body and pose from image 1, take face, eyes, lips and makeup from image 2. Result: the bare-chest image with a proper face,
anchored on the real photo and not on a copy of a copy. The Qwen and FireRed templates already take three images; the generated workflows wire only one, so this needs a small generator change (a role `ref` for the second image) and a beta template `heroes/beta/face-lock-human.txt`.
4. **Not pursued:** a neutral A-pose plate as a second Prime input. Any future
   pose-guide input would need a separate design decision.

## Order

The framed-input comparison was dropped on Oct 19. If the active P1/P2/P3
tests in E6 show a specific face-identity problem, consider test 3 (the
dual-image face pass) on two heroes.

## What this costs

| Step | Work | Risk |
| --- | --- | --- |
| 3 face pass | wiring a second LoadImage in `comfy_workflows.py`, a role `ref` in `workspaces.json`, a beta template, tests | medium (the model may blend the face badly: that is what the test tells us) |

## Templates (done today)

`_templates/heroes` is now split by the stage folders the art sets use (1_Alpha, 2_Studies, 4_Wardrobe, 5_Scenes, 6_Finish, Bench), with a README; a beta or prototype template goes in its own sub-folder (`heroes/beta/`). All 5,373 prompts regenerate byte-identical.
