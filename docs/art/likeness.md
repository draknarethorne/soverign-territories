# Likeness: which faces match, and sorting photos by person

`bin\likeness.cmd` compares the faces in the original-photo library ([original-photos.md](original-photos.md)). It answers three questions: which of your angels, sisters and prospects look alike, which photos belong to whom, and which photos in `Prospects\Various` are the same person. It can also move photos for you, after a preview.

## How it works

Each photo's main face is found and turned into an identity vector (OpenCV's YuNet and SFace models; two small files downloaded once to `%LOCALAPPDATA%\sovereign-territories\models`; nothing leaves your machine). The vectors are cached by the photo's content, so renaming or moving a photo costs nothing and the first scan (about 700 photos) takes a few minutes. Needs `pip install opencv-python-headless numpy pillow`.

Scores are cosine similarity after **subtracting the library's average face**. Without that every glamour face looks alike to the model. Read a score as a ranking inside your own library:

| Score | Means |
| --- | --- |
| 0.55 and up | the same person (what a folder's own photos score against each other) |
| 0.30 to 0.45 | very alike: do not use both for different heroes |
| below 0.15 | different people |

`likeness calibrate` shows how reliable this is on your library. Today: the right folder is the best match for 91% of photos, and the automatic moves (below) are about 99% right (435 confident and right, 5 confident and wrong, leave-one-out).

Folders are of two kinds. A **person folder** is one person: Angels, Models, a named Prospect, and each person grouped inside an Artist's folder (`Artists/Pierre/Mara Locke`). **Mixed** folders (the artist folders themselves, `Artists/*`, and `Prospects/Various`) hold many people: they never describe a person, are never read (except the pool) and never move on their own. `Prospects/Various` is the **pool** that `sort` empties.

Settings live under `likeness` in `workflows/workspaces.json`: `mixed`, `pool`, `assign`, `margin`, `cluster`, `minCluster`, `odd`, `alike`, `minFace`, `pairLow`, `pairHigh`, `pairs` (angel to sister) and `anchors` (`{"Angelica": ["part of a photo name", ...]}`: photos that are certainly her).

The first big run and its results are written up in [likeness-reorg-2026-10-09.md](likeness-reorg-2026-10-09.md).

## Commands

Anything that moves files previews until you add `--apply`. Add `--sheet FILE.png` to see the faces involved (a labelled grid), which is the quickest way to check a suggestion. After moving, the originals tool runs (rename after the new folder, scale, prune, re-point chosen photos).

| Command | What it does |
| --- | --- |
| `likeness alike` | every pair of people at or above 0.30, most alike first, flagged when it is two angels, an angel with her own sister (intended) or an angel who resembles a different sister; then **look-alike families** |
| `likeness compare Angelica azaline` | how alike two folders are, in words and as a percentile of all pairs, plus the closest photo pairs |
| `likeness folder Drakness` | is this folder **one person**? How many photos agree, are borderline or look like someone else; the ones to check with where each would go; for one person, who else looks like her. `--apply` moves only the "someone else" photos; `--all` lists every score |
| `likeness like path\to\photo.jpg` | which folders a new photo looks like, best first |
| `likeness clean [NAMES] [--group Models]` | the folder check for many folders at once, anchored on the chosen photo and the ComfyUI renders: a clear stranger goes to a matching person or the pool, a doubtful photo to the folder's `review` folder; the chosen photo never moves. A sister's folder only loses photos below `--sister-out` (0.05); `--keep` (0.25) is the score that keeps a photo |
| `likeness group [ARTISTS]` | splits each artist's folder by face into person folders (`Artists/Pierre/Mara Locke`, names invented, 3 or more photos each); photos that match no one stay with the artist |
| `likeness sort [--singles]` | empties `Prospects/Various`: a photo that matches a person confidently moves to her; 3 or more of one new person go to a new `Prospects/<invented name>` folder (rename it any time: the photos follow); with `--singles` a photo that matches nobody gets a folder of its own, so the pool ends empty. A chosen photo is never moved. `--plan FILE` writes the moves as JSON |
| `likeness sisters` | do the sisters read as one family around the anchor (`--anchor-sister`, Drakness)? Each sister against Drakness in photos and in renders, her place among everyone in the library, the nearest other sister, and who could replace a sister that is far out; `--md FILE` writes the table |
| `likeness pairs [--sister NAME]` | pairs each angel with the sister of her element from ALL the faces (angels, prospects, artist people); details below the table. `--apply` moves the new face into her `gallery` (old photos to `review`) and sets her photo in `workspaces.json` and the workflows. Re-run with `--sister` after changing a sister |
| `likeness merge Mia "Eva Emily"` | every photo of one folder into another (one person under two names) |
| `likeness retire azaline` | every photo of a folder back to `Prospects/Various`, so she can be cast again |
| `likeness undo` | puts the last batch of moves back (found again by content, even after the originals tool renamed them) |
| `likeness scan` / `calibrate` | read the library (and list photos with no usable face) / how reliable the scores are |

## How `pairs` chooses

The sister of each angel comes from the codex (or `likeness.pairs` in `workspaces.json`). A candidate is any person folder with 4 or more photos that agree on one face.

The pick should look like the sister without being her: 0.15 to 0.40 against her (target 0.28; the library average is 0.0 and 0.30 is already in the top 5%), and not alike any other sister, angel or fixed angel (Angelica).

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
