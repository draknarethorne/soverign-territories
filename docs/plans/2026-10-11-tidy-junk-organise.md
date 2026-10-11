# Plan: tidy the library, junk and screenshots, organise people for the lower tiers

Status: active, Oct 11, 2026 (Phases 1 to 3.1 done; the classification itself, Phase 3.2, is yours and grows one element at a time)

Source: your three notes, copied word for word at the end. Report: [../art/likeness-reorg-2026-10-10.md](../art/likeness-reorg-2026-10-10.md) (the Oct 11 section). How-to: [../art/likeness.md](../art/likeness.md), [../art/original-photos.md](../art/original-photos.md).

## What you asked for

1. Do we still need the `_org` folders and other backup copies? They make it easy to pick the wrong duplicate.
2. Screenshots carry text and icons over the picture; remove it, crop it, or discard them to a `_junk` or `_recycle` place you review. Single-photo prospects look like a symptom.
3. Organise prospects and artists so you can find "a good dark-elf rogue" or "a barbarian princess" for the lower-tier cards, without opening each `z_` file; one person can have several roles, races and elements. Males and creatures will come.
4. (Added Oct 11) Prospects and artists come from different sources and must never be mixed by the likeness checks; Azaline may become Mara Locke.

## Decisions

| ID | Question | Answer |
| --- | --- | --- |
| P1 | Archive layout for `_org` and other old copies | A mirrored `<work>\_archive\<same path>`; moved with a manifest, undo with `originals --undo-archive`. New prunes go there too. |
| P2 | Junk folder | `<work>\_junk\<same path>`; you empty it. `likeness junk` moves, `likeness undo` puts back. |
| P3 | Screenshot text | Facebook phone screenshots have a fixed layout, so the bars are cut away exactly (`tools/art/screens.py`): the scaled copy and the headshot use the clean part. A head that reaches into the bars cannot be fixed by cropping and goes to `_junk`. Inpainting is not built (not needed for these). |
| P4 | Where race, role and element live | In the `z_` file as profile lines (`sex`, `type`, `roles`, `elements`, `tier`, `tags`; several values allowed) and in a generated table `people_index.csv` / `.md` at the library root. Folders stay by status (Angels, Sisters, Prospects, Artists). |
| P5 | Males and creatures | Not built. When they arrive they get the same layout under their own roots (for example `Brothers`, `Creatures`); `sex` and `type` already describe them. |
| P6 | Prospects and artists | Never mixed: a photo is not moved between them, nor merged (`side` and `apart` in `likeness.py`); new people split from an artist's person stay in the artist's folder. |
| P7 | Azaline | Now Mara Locke (Pierre's one coherent face, 106 photos): 0.45 against Angelica before, -0.26 now. Her sister Draknira scores 0.11 to 0.16. |

## Steps

### Phase 1: the archive

- [x] 1.1 `originals` writes prunes to `_archive`; `--archive-old` and `--undo-archive`; tests.
- [x] 1.2 Run on the library: 44 folders, 1,416 files (1.6 GB) moved out of the person folders.
- [x] 1.3 Empty shell Cleo Park (its photos went to Sandalyn's review); Kylie Voss retired.

### Phase 2: junk and screenshots

- [x] 2.1 `likeness junk`: no usable face, a face under 60 px, 2 or more faces (prospects and artists only), the app's bars over her head. An angel's or sister's own gallery and a chosen photo are only reported. Result: 29 + 60 photos in `_junk`.
- [x] 2.2 Reel screenshots cut to the picture in the scaled copies and headshots (91 screenshots; 58 of them had the head under the bars before the bars were measured exactly). All scaled copies and headshots rebuilt.
- [x] 2.3 `likeness singles`: a single-photo prospect that looks like another prospect (0.40 or more) is merged; two were.
- [x] 2.4 The face detector tries again less strictly when it finds nothing (the last two Various photos were found this way; Various is empty).

### Phase 3: organising for the lower tiers

- [x] 3.1 Profile lines in `people.py`; `likeness index` (CSV and markdown), `index --import`, `profile`, `who`; tests.
- [ ] 3.2 Classification with you, one element at a time (Darkness and Light first). Fill the profile columns of `people_index.csv` and import them, or use `likeness profile`.

## Result so far

The person folders hold only what is live. `_archive` and `_junk` hold the rest. 107 person folders, all with a `z_` file. Next for you: open `people_index.csv`, review `_junk`, and start classifying.

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
