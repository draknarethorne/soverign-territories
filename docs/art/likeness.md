# Likeness: which faces match, and sorting photos by person

`bin\likeness.cmd` compares the faces in the original-photo library ([original-photos.md](original-photos.md)). It answers three questions: which of your angels, sisters and prospects look alike, which photos belong to whom, and which photos in `Various` are the same person. It can also move photos for you, after a preview.

## How it works

Each photo's main face is found and turned into an identity vector (OpenCV's YuNet and SFace models; two small files downloaded once to `%LOCALAPPDATA%\sovereign-territories\models`; nothing leaves your machine). The vectors are cached by the photo's content, so renaming or moving a photo costs nothing and the first scan (about 700 photos) takes a few minutes. Needs `pip install opencv-python-headless numpy pillow`.

Scores are cosine similarity after **subtracting the library's average face**. Without that every glamour face looks alike to the model. Read a score as a ranking inside your own library:

| Score | Means |
| --- | --- |
| 0.55 and up | the same person (what a folder's own photos score against each other) |
| 0.30 to 0.45 | very alike: do not use both for different heroes |
| below 0.15 | different people |

`likeness calibrate` shows how reliable this is on your library. Today: the right folder is the best match for 91% of photos, and the automatic moves (below) are about 99% right (435 confident and right, 5 confident and wrong, leave-one-out).

Folders are of two kinds. A **person folder** is one person: Angels, Sisters (formerly Models), a named Prospect, and each person grouped inside an Artist's folder (`Artists/Pierre/Mara Locke`). **Mixed** folders (the artist folders themselves, `Artists/*`, and `Various`) hold many people: they never describe a person, are never read (except the pool) and never move on their own.

`Various` (top level, next to Prospects) is the **pool** that `sort` empties; drop new photos into `Various\gallery` and run `bin\library.cmd`, which does `originals`, `duplicates`, `likeness junk`, `review`, `sort --singles` and `singles --min 0.45`, then brings the scaled copies, headshots and frames back in step ([original-photos.md](original-photos.md#the-routine)). The commands below are what it runs, for when you want to look closer at one step.

## Names and history

Every person folder has a `z_<name>.txt` in its `gallery` (the `z_` keeps it at the end of the list; the image tools ignore it). The first line is `name: First Last`; after it come dated lines that the tools write when the folder is created, merged, paired, retired or marked reserved (`2026-10-10 reserved: looks like Sisters/Draknoxa (0.56); keep off cards below the top tier`). The name is her real name when you know it, otherwise the invented one the tool gave her.

The file travels with the folder, so a prospect who becomes an angel (or the reverse) keeps her history, and `pairs --apply` logs "was Anya Sloane" in the angel's file. `likeness names` shows every folder's name and writes the missing files (preview unless `--apply`); a folder is never named after the pool or another angel, and photos split off a sister do not take her name. Edit the first line by hand any time.

Settings live under `likeness` in `workflows/workspaces.json`: `mixed`, `pool`, `assign`, `margin`, `cluster`, `minCluster`, `odd`, `alike`, `minFace`, `pairLow`, `pairHigh`, `pairs` (angel to sister), `keepPhoto` (heroes whose photo never changes: Drakness, Angelica, Drakneta) and `anchors` (`{"Angelica": ["part of a photo name", ...]}`: photos that are certainly her).

The big runs and their results are written up in [likeness-reorg-2026-10-09.md](likeness-reorg-2026-10-09.md) and [likeness-reorg-2026-10-10.md](likeness-reorg-2026-10-10.md).

## Commands

Anything that moves files previews until you add `--apply`. Add `--sheet FILE.png` to see the faces involved (a labelled grid), which is the quickest way to check a suggestion. After moving, the originals tool runs (rename after the new folder, scale, prune, re-point chosen photos).

| Command | What it does |
| --- | --- |
| `likeness alike` | every pair of people at or above 0.30, most alike first, flagged when it is two angels, an angel with her own sister (intended) or an angel who resembles a different sister; then **look-alike families** |
| `likeness compare Angelica azaline` | how alike two folders are, in words and as a percentile of all pairs, plus the closest photo pairs |
| `likeness folder Drakness` | is this folder **one person**? How many photos agree, are borderline or look like someone else; the ones to check with where each would go; for one person, who else looks like her. `--apply` moves only the "someone else" photos; `--all` lists every score |
| `likeness like path\to\photo.jpg` | which folders a new photo looks like, best first |
| `likeness clean [NAMES] [--group Sisters]` | the folder check for many folders at once, anchored on the chosen photo and the ComfyUI renders: a clear stranger goes to a matching person or the pool, a doubtful photo to the folder's `review` folder; the chosen photo never moves. A sister's folder only loses photos below `--sister-out` (0.05); `--keep` (0.25) is the score that keeps a photo |
| `likeness group [ARTISTS]` | splits each artist's folder by face into person folders (`Artists/Pierre/Mara Locke`, names invented, 3 or more photos each); photos that match no one stay with the artist |
| `likeness sort [--singles]` | empties `Various`: a photo that matches a person confidently moves to her; 3 or more of one new person go to a new `Prospects/<invented name>` folder (rename it any time: the photos follow); with `--singles` a photo that matches nobody gets a folder of its own, so the pool ends empty (photos with no usable face stay). A chosen photo is never moved. `--plan FILE` writes the moves as JSON |
| `likeness sisters` | do the sisters read as one family around the anchor (`--anchor-sister`, Drakness)? Each sister against Drakness in photos and in renders, her place among everyone in the library, the nearest other sister, and who could replace a sister that is far out; `--md FILE` writes the table |
| `likeness pairs [--sister NAME]` | pairs each angel with the sister of her element from ALL the faces (angels, prospects, artist people); details below the table. `--apply` moves the new face into her `gallery` (old photos to `review`) and sets her photo in `workspaces.json` and the workflows. Re-run with `--sister` after changing a sister |
| `likeness review [NAMES] [--out]` | the photos set aside in `review` folders, each against her own folder and everyone else: one that is probably her (0.20 or more, `--back`) goes back to her gallery, one that clearly looks like someone else goes to that person, the rest stay. With `--out`, a photo that is clearly not her and matches nobody becomes a new prospect (photos that look alike share one; its history says where it came from). Preview unless `--apply` |
| `likeness loosen` | what looser settings would do, measured and not applied: at 0.05, 0.10 and 0.15 below today's assign score, how many Various and review photos would move, which would go where, and which folders may be one person (same person is about 0.55 and up). Read-only |
| `likeness lookalikes [--min 0.30]` | the guard for low-tier cards: every prospect or artist person scoring at least 0.30 against a sister or angel, most alike first. `--apply` writes a `reserved:` line into her `z_` file. Keep reserved people off cards below the top tier |
| `likeness names` | every folder's name and history file; `--apply` writes the missing ones (from the move log, or the invented name) |
| `likeness junk [--keep-multi] [--recheck]` | photos that cannot feed a Prime go to `<work>\_junk\Prospects` or `_junk\Artists` (flat, the person is in the file name; you empty it): no usable face, a face under 60 px, a second person in the picture, or a phone screenshot whose head lies under the app's bars. An angel's or sister's own gallery and a chosen photo are only reported. `--recheck` sends photos that are usable now back to their folder. `likeness undo` puts the last batch back |
| `likeness singles [--min 0.40]` | the prospects that have one photo, each with the prospect she looks most like; one at or above `--min` (default: assign less 0.10) with a margin of 0.05 over the next is merged into her. Prospects only |
| `likeness index [--import FILE]` | the table to pick from, `<work>\people_index.csv` (a spreadsheet) and `.md`: one row per person with her photos, headshots, review count, best Prime photo, who she looks like, reserved, and the profile columns. `--import` reads the profile columns of an edited CSV back into the `z_` files (preview unless `--apply`) |
| `likeness profile NAME... --type "dark elf" --roles rogue,assassin --elements Darkness` | sets the profile of one or more people (`--sex --type --roles --elements --tier --tags`; several values with commas; `-` clears a key) |
| `likeness who --roles rogue --elements Darkness` | who matches: every filter must match, a word matches inside a value; prospects and artists unless `--all`; with no filter, the people still to classify; reserved people are marked |
| `likeness photos [NAMES]` | picks the 1_Prime photo for every angel: her best-scoring photo (her face, one clear face, some body in view, portrait, enough pixels). `likeness.keepPhoto` heroes (Drakness, Angelica, Drakneta) never change, and a chosen photo only changes when the best scores 0.12 higher. A sister's photo is only reported; `--sisters` changes them too. `--apply` sets it in `workspaces.json` and the workflows |
| `likeness merge Mia "Eva Emily"` | every photo of one folder into another (one person under two names); the emptied folder is moved to `_retired` and the history says what happened |
| `likeness retire azaline` | every photo of a folder back to `Various`, so she can be cast again |
| `likeness undo` | puts the last batch of moves back (found again by content, even after the originals tool renamed them) |
| `likeness scan` / `calibrate` | read the library (and list photos with no usable face) / how reliable the scores are |

## Profile: who could play what

Under the name, a `z_` file can hold profile lines: `sex`, `type` (human, dark elf, high elf, wood elf, orc, succubus, demon, creature ...), `roles` (rogue, barbarian, princess ...), `elements`, `tier` and `tags`. Each can hold several values, separated by commas (`roles: rogue, assassin`). They are yours to set; the tools never guess them.

The `z_` file is the why (add a line saying why by hand if you like); `people_index.csv` is how you look at everyone at once and `who` answers "who makes a good dark-elf rogue". Edit the table in a spreadsheet, then `likeness index --import people_index.csv --apply`.

## The cache: what happens when you clean up

The cache (`%LOCALAPPDATA%\sovereign-territories\likeness_cache.json`) holds only what the face detector found in a file (the face's box, size, how many faces, and its identity vector), keyed by the file's **content**. It never holds a decision: who a photo belongs to, a folder's average face, a score. Those are worked out again from the files that are in the folders at the time of every run.

- **Delete, move or rename a photo:** nothing to clear. A deleted photo is simply not read any more (its cache entry stays, unused and harmless); a moved or renamed photo keeps its entry, so it costs nothing and is not detected again. The very next run sees the cleaned folder.
- **Edit a photo (crop it, paint over it):** its content changes, so it is detected again as a new photo.
- **A rule changed in the tool** (the second-face size, a less strict face search): the affected entries are dropped and read again by themselves.
- **Clearing the cache by hand** is never needed; it only makes the next run slower (a few minutes). Delete `likeness_cache.json` if you ever want a completely fresh read.

## A photo of two people

The detector finds every face, and the largest is the one that is compared. When a woman and a man are in one photo and his face is the larger, a man's face lands in her folder and nudges her average face, so other men start to look like her (the Elise Frost problem). Two defences:

1. `likeness junk` sets such a photo aside (`_junk`) when a second face is at least 0.3 of the main face's size (`likeness.multiFace`); a small passer-by in the background is not a problem and stays. Run it after every big import (it previews first), then `likeness clean` as before for whole folders.
2. `likeness junk --recheck` looks at `_junk` again with the current rules and sends the usable photos back to the folder their file name says (or to `Various` when a prospect's folder is gone). Drag a photo from `_junk` into `Various` yourself and it is sorted like any new photo.

## Prospects and artists are kept apart

Prospects come from what you pick, artists from an artist's work, so the checks never mix them: a photo is not sent from one side to the other, they are not merged, and a new person split off an artist's person stays in that artist's folder. Angels and sisters can take from either. (Oct 10 the tool had moved 6 photos across; they were put back.)

## The archive and `_junk`

The old scaled copies (`_org`) and set-aside duplicates are in `<work>\_archive\<same path>` and out of the person folders; `originals --archive-old --apply` moved the ones that were there (`--undo-archive` reverses it). Photos that cannot feed a Prime are in `<work>\_junk\Prospects`, `_junk\Artists` (and `Sisters`, `Angels`), flat, so you can scan them in one view; the person is in the file name. Nothing is deleted until you do it.

## How `pairs` chooses

The sister of each angel comes from the codex (or `likeness.pairs` in `workspaces.json`). A candidate is any person folder with 4 or more photos that agree on one face.

The pick should look like the sister without being her: 0.15 to 0.40 against her (target 0.28; the library average is 0.0 and 0.30 is already in the top 5%), and not alike any other sister, angel or fixed angel (Angelica).

Candidates are angels and prospects only: an artist's person is never chosen (the artists' faces are for the art, and too fantasy for a Prime photo). An angel whose `z_` file says she came from an artist (`+N from Artists/...`, still under that name) is replaced and her photos go back to the artist.

An angel changes only when the replacement is inside that band, or when she is a near twin of Angelica; otherwise she stays and the slot waits for better candidates. Her old photos go to her `review` folder and the emptied source folder to `_retired`.

## Choosing between look-alikes

1. `likeness alike --sheet alike.png`, then look at the sheet.
2. Pick the one you like best of each family. For the others: `likeness retire NAME --apply` returns their photos to the pool; `sort` can then give them to someone they match or to a new prospect.
3. A retired angel with a chosen photo loses it (`inputs photos` reports it); pick another with `inputs set`, or run `pairs --sister NAME` to pick one from the library.
4. Check the other direction too: a prospect that matches a sister (the `alike` list) should not become an angel.

## Notes and limits

- The model was trained on real photos. For this library it separates people well but not perfectly: treat the suggestions as a first pass and look at the sheet, especially for clusters of 3 or 4.
- A photo with no face, or a face smaller than 60 px, is left out (`likeness scan` lists them). Only the largest face in a photo is used.
- Same-person clusters are cut at 0.25 average similarity (95% pure on your folders); raise `cluster` for stricter groups.
- Nothing is deleted. A duplicate already in the destination is set aside in the source folder's `gallery_org`.
