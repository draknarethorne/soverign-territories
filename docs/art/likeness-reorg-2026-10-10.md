# Likeness reorganisation, Oct 10, 2026

What the second pass did to your photo library (`B:\Soverign Territories`), why, and where to look next. Plan: [../plans/2026-10-10-names-ingest-headshots.md](../plans/2026-10-10-names-ingest-headshots.md). Tool guide: [likeness.md](likeness.md). The first pass is in [likeness-reorg-2026-10-09.md](likeness-reorg-2026-10-09.md).

Everything was backed up first (`_backup\2026-10-10-before-names-ingest`: the Various photos, every `z_` file, `workspaces.json`, a manifest of 3,546 files). The reports and contact sheets are in `_reports\2026-10-10-names-ingest`. Nothing was deleted: folders emptied by a merge or a re-pair are in `_retired`, and a `likeness undo` reverts the last batch of moves.

## What changed

| Area | What happened | Why |
| --- | --- | --- |
| Folder name | `Models` is now `Sisters`. The code reads both names for one cycle. | Your request (Angels, Sisters, Prospects, Artists). |
| Names | Every person folder has a `z_<name>.txt` in its `gallery`: `name: ...` then dated history lines (99 written, backfilled from the move log; 120 folders have one now). The tools write to it when they move, merge, pair or retire. | A prospect that becomes an angel keeps her name and history. An unknown name is the invented one. |
| Names bug fixed | 16 new prospects had been given the name of the sister or angel their photos were split from. Fixed in the tool (only a folder that moves out entirely passes on her name); the 16 were renamed after their folders; a test covers it. | Found while checking the files. |
| Various | The 199 new photos were renamed (`various_image_*`, `various_shot_*`), scaled, scanned and sorted: 1 to Angelica, 1 to Azaline, 1 to Drakniss, 1 to Draknoxa, the rest into about 50 new prospect folders with invented names (Dara Ives 42, Uma Dunn 19, Cleo Park 12, Dara Reyes 10 are the biggest). 2 photos have no usable face and stay in `Various`. | Matches go to the person they match; new faces become prospects. |
| Doubtful photos | 15 photos from the big new clusters went to their folder's `review` (keep score under 0.45). | They did not clearly match the rest of the folder. |
| Duplicates | Four prospect and artist people were one person and were merged: Anya Park into Angelica, Vera North and Freya Marsh into Elise Frost, Nia Nash into Mara Locke (0.61 to 0.80 against each other). | Two folders for one face would hand out the same look twice. |
| Review folders | `review --out` moved 40 photos that are clearly not her into new prospects. About 40 photos are still in review folders. | Keeps a sister's generated image from drifting to another woman. |
| Pairing | Seraphine is now Anya Sloane (0.26 against her sister Drakniss, was 0.03), Gavrielle is Wren Thorn (0.30 against Draknava, was 0.10), Sandalyn is Cleo Park (0.33 against Draknara, was 0.20). Their photos are set in `workspaces.json` and in their Angel Primes and repo `Alpha_1_Prime` workflows, and the images are in `ComfyUI-Inputs\Angel Primes`. | The pair should look like the sister without being her: 0.15 to 0.40. |
| Headshots | `headshot_944x1104` next to `gallery_944x1104`: 1,121 files, 0.86 GB (520 GB free). Made by `originals`; a choice of one as a Prime input works (`inputs set HERO --photo <name>_head_944x1104.png`). | Your Prime test idea. |

## Your questions

- **Where are the original names?** In each folder's `z_` file (see [likeness.md](likeness.md)). Sister files hold her original name; an invented prospect's file holds the invented name.
- **Would looser matching help?** Little. `likeness loosen`: lowering the assign score from 0.45 by 0.10 frees only 3 more review photos and puts nothing in `Various` to a home (it was already empty). The settings stay; the review photos need your eyes.
- **Prospects that look like a top-tier sister or angel?** `likeness lookalikes` found 23 prospect or artist folders at 0.30 or more against a sister or angel; each has a `reserved:` line in its `z_` file. Keep them off common, uncommon and rare cards.
- **Sophie Lloyd as an angel?** She is coherent (16 photos, cohesion 0.70), but her closest sister is Drakneta at only 0.08, so she is not in any pairing band. She stays a prospect, a good face for a different use.
- **Sabine Vale as a better Seraphine?** There is no folder by that name. The closest, Prospects\Sabine Jasper (one photo), scores 0.04 against Drakniss, which is a different person, so she is not a Seraphine. Seraphine is Anya Sloane by score; the Drakness review set (10 photos) is still yours to look at.

## Where to look next

| Where | What to decide |
| --- | --- |
| Angels that moved | Seraphine, Gavrielle and Sandalyn: run the Prime in ComfyUI with the new photo (and try a headshot). Their old photos are in their `review` folders. |
| Azaline, Camaris | Camaris has no candidate in the band and keeps her face (Azaline became Mara Locke on Oct 11, below). |
| Review folders (about 40) | Drakness 10, Drakneta 4, Draknava 3, Brielle Carter 4, the rest 1 to 3 each. Move what you recognise. |
| Same person as a sister? | Confirmed by you and merged: Una Beck into Draknoxa (4 photos), Dara Reyes into Paige Rowe (7 photos, now 13 and one person). Brielle Carter is not Draknara (you checked); she stays a prospect, still on the reserved list. Ivy Rowe and Petra Wilde against Angelica (0.49, 0.40) and Amira Vale against sammara (0.46, 21 photos) are the next closest. |
| Two prospects that may be one | Bea Cole and Paige Rowe (0.49), Esme Marsh and Paige Rowe (0.43), Yvette Reyes and Paige Rowe (0.42): the Paige Rowe family. `likeness merge` joins them. |
| Reserved list | The 23 folders and what they look like: `_reports\2026-10-10-names-ingest\lookalikes.txt`. |
| Alternate Primes | Design in the plan (Phase 5). It needs your approval, and which hero gets a Prime B first. |

## Oct 11: tidy, junk, kept apart, Azaline

Plan: [../plans/2026-10-11-tidy-junk-organise.md](../plans/2026-10-11-tidy-junk-organise.md).

| Area | What happened |
| --- | --- |
| Sophie Lloyd and Azaline | Sophie scores -0.19 against Azaline's sister Draknira, so she cannot be that pair. Azaline was a near twin of Angelica (0.45), so she was re-paired with Pierre's Mara Locke (106 photos, one coherent face): now -0.26 against Angelica and 0.11 against Draknira. Her photo is set in `workspaces.json` and the Angel Primes workflows; try a Prime and tell me. |
| Archive | 44 `_org` folders (1,416 files, 1.6 GB) moved out of the person folders into `_archive` with the same paths; new prunes go there too. |
| Junk | 89 photos in `_junk`: 29 whose head lay under a phone app's bars, 60 with a second person in the picture (Elise Frost had 12 of 24). Angel and sister galleries are only reported (54 photos). |
| Screenshots | 91 Facebook screenshots are cut to the picture in every scaled copy and headshot, so the text is gone from them (checked on Rhea Ives). |
| Prospects and artists | Kept apart in the tool. 8 photos that had crossed into Elise Frost (5 of Vera North, one each of Rachel Pizzilato, Drakness, Draknava) were put back. Vera North was brought back from `_retired`. |
| Single-photo prospects | 36 had one photo; two were merged into the prospect they look like (0.40 or more). The rest stay; `likeness singles` shows who each looks most like (Gia Park and Paige Locke look like Bea Ellery at 0.37). |
| Detector | It now looks again, less strictly, when it finds no face; the last two Various photos were found that way and sorted. Various is empty. |
| Index | `people_index.csv` and `.md` at the library root: 107 people with photos, best Prime photo, who each looks like, reserved, and empty profile columns for you to fill. `likeness who --roles rogue` and `likeness profile` work from the same `z_` lines. |

Open: classify (Darkness and Light first); look in `_junk` for anything you want back (`likeness undo` reverses the last move, or move the file back and run `originals`); the people who look alike (Ivy Rowe and Petra Wilde against Angelica, Amira Vale against Sammara, Bea Cole, Esme Marsh and Yvette Reyes against Paige Rowe).

## Still not tested by you

The ComfyUI side: renders from the new Angel Primes photos, the FireRed 944x1104 size, seed replay and the video templates.
