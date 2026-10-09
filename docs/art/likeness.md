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

Folders are of two kinds. A **person folder** (Angels, Models, a named Prospect) is one person. **Mixed** folders (`Artists/*`, `Prospects/Various`) hold many people: they never describe a person, are never read (except the pool) and never move on their own. `Prospects/Various` is the **pool** that `sort` empties. Change these under `likeness` in `workflows/workspaces.json` (`mixed`, `pool`, `assign`, `margin`, `cluster`, `minCluster`, `odd`, `alike`, `minFace`).

## Commands

Anything that moves files previews until you add `--apply`. Add `--sheet FILE.png` to see the faces involved (a labelled grid), which is the quickest way to check a suggestion. After moving, the originals tool runs (rename after the new folder, scale, prune, re-point chosen photos).

| Command | What it does |
| --- | --- |
| `likeness alike` | every pair of people at or above 0.30, most alike first, flagged when it is two angels or an angel and a sister; then **look-alike families** (alike on average), with each folder's photo count and whether it has a chosen photo |
| `likeness compare Angelica azaline` | how alike two folders are, in words and as a percentile of all pairs, plus the closest photo pairs |
| `likeness folder Drakness` | the first thing to run on a folder: is it **one person**? Says how many photos agree, how many are borderline and how many look like someone else, lists only the ones to check with where each would go (the person it looks like if that is clear, otherwise `Prospects/Various` as a holding place), and, when the folder is one person, who else in the library looks like her. `--apply` moves only the "someone else" photos; `--all` lists every score; `--outside` always shows the library look-alikes |
| `likeness like path\to\photo.jpg` | which folders a new photo looks like, best first |
| `likeness sort` | for `Prospects/Various`: a photo that matches an existing person confidently (0.45 with a margin of 0.10 over the next) moves to that folder; 3 or more photos of one new person go to a new `Prospects/<invented name>` folder (rename it any time: the originals tool renames the photos); the rest stay. A note says when a new person looks like an existing one. A photo chosen in `workspaces.json` is never moved. `--plan FILE` also writes the moves as JSON |
| `likeness merge Mia "Eva Emily"` | every photo of one folder into another (one person under two names) |
| `likeness retire azaline` | every photo of a folder back to `Prospects/Various`, so she can be cast again |
| `likeness undo` | puts the last batch of moves back (found again by content, even after the originals tool renamed them) |
| `likeness scan` / `calibrate` | read the library (and list photos with no usable face) / how reliable the scores are |

## Choosing between look-alikes

1. `likeness alike --sheet alike.png`, then look at the sheet.
2. Pick the one you like best of each family. For the others: `likeness retire NAME --apply` returns their photos to the pool; `sort` can then give them to someone they match or to a new prospect.
3. A retired angel with a chosen photo loses it (`inputs photos` reports it); pick another with `inputs set`, or leave her until you cast someone new.
4. Check the other direction too: a prospect that matches a sister (the `alike` list) should not become an angel.

## Notes and limits

- The model was trained on real photos. For this library it separates people well but not perfectly: treat the suggestions as a first pass and look at the sheet, especially for clusters of 3 or 4.
- A photo with no face, or a face smaller than 60 px, is left out (`likeness scan` lists them). Only the largest face in a photo is used.
- Same-person clusters are cut at 0.25 average similarity (95% pure on your folders); raise `cluster` for stricter groups.
- Nothing is deleted. A duplicate already in the destination is set aside in the source folder's `gallery_org`.
