# Likeness reorganisation, Oct 9, 2026: what was done, why, and where to look next

Everything in your photo library (`B:\Soverign Territories`: Angels, Models, Prospects, Artists) was sorted by the face in each photo. The sisters were checked as a family with Drakness as the anchor, and the angels were paired to the sisters. The folders on disk are already in their new shape, every name follows its folder, and the scaled 944x1104 copies are made. The angel photos are set in `workspaces.json` and in the Angel Primes workflows.

This page records what happened and what is left for you to judge. The tool is described in [likeness.md](likeness.md); photo naming is in [original-photos.md](original-photos.md).

## Short version

| Question | Answer |
| --- | --- |
| Are the sisters one family? | Mostly. Drakness (the anchor) is the middle of a spread; **Drakneta** is the one furthest from her (her photos score -0.41 against Drakness, the lowest of any person in the library), **Drakniya** is also in the bottom 10%. No sister was swapped (see "Sisters"). |
| Did the sister folders hold other people? | Yes, in one case. **Draknoxa**: 24 of her 39 photos were clearly another woman. They left her folder (she keeps 4, with 12 set aside to review). That other woman is now **Ravaelle's** face. |
| Angels | 7 of 10 angel slots got a new face paired to her sister (Ravaelle, Haniya, Gavrielle, Sandalyn, Remiah, Sammara, Nyxene); 3 have no good candidate yet and stayed as they were (Seraphine, Azaline, Camaris). Angelica was left alone. |
| `Prospects\Various` | Empty. Every photo with a usable face is in a named person folder (invented names where needed). |
| Artists | Grouped by face into people inside each artist's folder (20 people, e.g. `Pierre\Mara Locke`). |
| Safety | A full copy of every folder as it was is in `_backup\2026-10-09-before-likeness-reorg`. Nothing was deleted. |

## Safety net

- **Backup:** `B:\Soverign Territories\_backup\2026-10-09-before-likeness-reorg` holds all 990 photos (galleries, `gallery_org`, `review`) exactly as they were, with `manifest.json` (path, size and hash of each file) and the old `workspaces.json`.
- **`review` folders:** a photo that was doubtful stayed with its person, in a `review` folder next to `gallery` (Drakness 14, Draknoxa 12, Drakneta 8, Draknava 6, and a few elsewhere). Look at these first; move the good ones back into `gallery` and run `bin\originals.cmd`.
- **`_retired`:** a person folder that was emptied (because all her photos became an angel) was moved to `B:\Soverign Territories\_retired`, not deleted: Prospects Adrianna Cruz, Tove North, Iris Nash, Lia Joyce, and Artists Fantasy\Jade Beck and Pierre\Xena Orr.
- **`gallery_944x1104_org`:** scaled copies of anything that moved are archived here. **Undo:** `bin\likeness.cmd undo --apply` puts back the last batch of moves (each batch is logged); the backup restores everything.
- **Reports and contact sheets** (the face grids): `B:\Soverign Territories\_reports\2026-10-09-likeness-reorg`.

## What was done, in order, and why

1. **Backup first** (above), then the tool was extended: `clean`, `group`, `sisters`, `pairs` and `sort --singles`, with tests. The reasoning behind each is below.
2. **Calibrated the scores on your library.** The face model rates almost every glamour face as alike unless the library's average face is subtracted; with that done, the right folder is the best match for 91% of photos. All scores below use that, so read them as a ranking inside your library (0.55 and up is the same person; 0.30 to 0.45 is very alike; below 0.15 is different people).
3. **Anchored each person on what you chose**, not on the folder's average, so a few strangers cannot drag her identity away. Her chosen photo and her ComfyUI renders (the sisters' old `X_Pose` renders, the angels' saved candidates) are the anchor. Angelica's anchor is the three photos you named (`likeness.anchors` in `workspaces.json`). If her renders look like someone else than her chosen photo, nothing is sent away; the doubtful photos go to `review` instead.
4. **Cleaned the sisters** (`clean --group Models`). A sister's folder only loses a photo that is clearly someone else (score below 0.05); photos in between go to her `review` folder. Result: 26 left the sister folders for the pool, 47 went to `review`.
5. **Cleaned the angels and prospects** the same way (6 and 12 photos). Angelica's 9 photos all agree with your three anchors, so she did not change.
6. **Grouped each Artist folder by face** (`group`): Fantasy 10 people, Her Legends 1, Maridos 2, Pierre 7. A group needs 3 or more photos; anything else stays with the artist. The names are invented but stable, and renaming a folder renames its files.
7. **Emptied `Prospects\Various`** (`sort --singles`): 72 photos (the original 44, plus the 26 sent away from the sisters, plus 2). 3 matched an existing angel (2 to Angelica, 1 to Remiah); the rest became new Prospect folders, 12 of them with a single photo each because that face appears once.
8. **Checked the sisters as a family** (`sisters`), then **paired the angels** (`pairs`): see below.
9. **Ran the rename script** (`originals`) after every step, so all names follow their folders, the scaled copies are current, and the chosen photos are re-pointed.

## Sisters

Drakness is the anchor, as in the story. A sister is flagged "vastly unlike" when she is in the bottom 10% of the library against Drakness; the sisters are different women, so only the extremes matter.

| Sister | Photos | Her old renders match her photos | Photos vs Drakness | Library percentile | Verdict |
| --- | --- | --- | --- | --- | --- |
| Drakness | 78 | 0.67 | anchor | - | ok |
| Draknara | 40 | 0.60 | -0.15 | 25% | ok; looks like Draknoxa 0.35 |
| Draknava | 41 | 0.60 | -0.06 | 52% | ok |
| Drakneta | 32 | **0.25** | -0.41 | **0%** | far from Drakness; her renders do not match her photos |
| Draknira | 34 | 0.42 | -0.03 | 57% | ok; looks like Draknisa 0.37 |
| Draknisa | 28 | 0.73 | -0.14 | 30% | ok |
| Drakniss | 55 | 0.70 | -0.08 | 42% | ok |
| Drakniya | 24 | 0.67 | -0.27 | 10% | far from Drakness |
| Draknora | 26 | 0.55 | 0.03 | 78% | ok; the closest to Drakness |
| Draknoxa | 4 (+12 to review) | 0.63 | 0.04 | 78% | ok, but a thin folder now |

What to know:

- **Draknoxa** lost most of her folder: the 24 photos that did not match her chosen photo or her renders were another woman. Her real set is 4 clear photos and 12 in `review`. If you want more of her, look at `Models\Draknoxa\review`.
- **Drakneta** is the biggest decision. Her photos are blonde and fair and score lowest against Drakness. The renders you liked for her look like a different woman than her photos (0.25), so her chosen photo may not be the one behind those renders. Nothing moved. For a family resemblance, the closest faces to Drakness that are not another sister are `Artists\Pierre\Mara Locke` (0.16) and `Artists\Fantasy\Nia Nash` (0.13); neither is close, and the model is less reliable on illustrations.
- **Drakniya** is in the bottom 10%; treat like Drakneta if you want a tighter family.
- The renders the sisters made look like their own photos at 0.55 to 0.73, so the Qwen workflow keeps the face reasonably well; for Drakneta and Draknira (0.25, 0.42) it drifts.

## Angels

Each angel is paired to the sister of her element (from the codex). The target is similar but not the same: 0.15 to 0.40 against the sister (the library average is 0.0, and 0.30 is already in the top 5% of pairs); not alike any other angel or sister; coherent (a person needs 4 or more photos that agree on one face). An angel only changed when the replacement is in that band. An angel who was a near twin of a fixed angel (Angelica) was replaced even below the band.

| Angel | Sister | Was (vs sister) | Now (vs sister) | Source of the new face | Note |
| --- | --- | --- | --- | --- | --- |
| Angelica | none (neutral herald) | unchanged | unchanged | your 3 photos | all 9 photos agree; resembles Draknoxa 0.33 |
| Seraphine | Drakniss | 0.03 | 0.03 | unchanged | **no candidate in the band**; closest is Draknisa 0.37 (a different sister) |
| Ravaelle | Draknisa | 0.03 | 0.14 | Prospects\Lia Joyce (23 photos) | was 0.68 like Angelica; new face is the woman who was in Draknoxa's folder |
| Haniya | Drakniya | 0.04 | 0.23 | Prospects\Kylie Voss (6) | |
| Gavrielle | Draknava | -0.03 | 0.11 | Prospects\Iris Nash (6) | was 0.54 like Angelica and 0.49 like Draknoxa; below the band |
| Sandalyn | Draknara | 0.16 | 0.21 | Artists\Fantasy\Jade Beck (5) | AI art; check |
| Remiah | Drakneta | -0.11 | 0.19 | Artists\Pierre\Xena Orr (6) | stylised silver-haired art; check |
| Azaline | Draknira | -0.10 | -0.10 | unchanged | **no candidate in the band** (best Pierre\Mara Locke 0.13) |
| Camaris | Draknora | -0.04 | -0.04 | unchanged | **no candidate in the band** (best Xena Quill 0.05) |
| Sammara | Draknoxa | 0.50 | 0.33 | Prospects\Adrianna Cruz (6) | was too alike her sister |
| Nyxene | Drakness | 0.09 | 0.28 | Prospects\Tove North (6) | close to Drakness on purpose; check she is not too close |

- **Published:** the angel's folder (`Angels\<name>\gallery`) holds all the photos of the new face, and `Angels\<name>\review` holds the photos she had before. The best single photo of the new face (clear, single face, large, portrait) was set as the angel's photo in `workspaces.json`, copied to `ComfyUI-Inputs\Angel Primes`, and written into the repo and Angel Primes `Alpha_1_Prime` workflows. Check: all 11 angel workflows load the photo named in the config, and all 11 files exist in the input folder.
- **Hand-made workflows** (candidates, finals, curated, shots) were not changed, so your saved candidates still load the photos you used.
- **Male angels** were not touched: no photos yet, and the pairing is woman-to-sister only.
- The sheet `pairs_final.png` shows each sister above her angel's photos.

## The library now

- **Angels** (all 11 folders keep their names): Angelica 11, Ravaelle 23, Sammara 10, Haniya 7, Gavrielle 6, Nyxene 6, Remiah 6, Sandalyn 5, Seraphine 1, Azaline 1, Camaris 1.
- **Models** (sisters): Drakness 78, Draknava 41, Draknara 40, Drakniss 55, Draknisa 28, Draknora 26, Draknira 34, Drakneta 32, Drakniya 24, Draknoxa 4.
- **Prospects:** about 29 named people; the larger ones are Mia 36, Amira Vale 21, Brielle 23, Rachel Pizzilato 21, Aria Muse 20, Eva Emily 18, Sophie 16, Elria Monroe 9, Charlotte Hayes 8, and about 18 small new folders with invented names. `Various` is empty.
- **Artists:** each artist folder keeps the photos that matched no one; the people are inside (e.g. Pierre: Mara Locke 98, Elise Frost 14, Gia West 9, Vera Lane 4, Xena Orr 6 now retired, Jules Thorn 3, Maren Cole 3; Maridos: Odette Hart 38, Freya Marsh 10; Fantasy: 10 people of 3 to 9).
- 917 photos in galleries in total.

## Where to look next (in this order)

1. **Review the pairs** in `pairs_final.png`: are the new angel faces what you want next to their sisters? Anything you dislike, send back with `likeness retire NAME` (or move photos by hand) and run `bin\likeness.cmd pairs --sister <Sister> --apply` to pick again.
2. **Bring candidates for Seraphine, Azaline and Camaris**, and better ones for Ravaelle and Gavrielle (below the band). Drop new photos into `Prospects\Various\gallery`, then `bin\likeness.cmd sort --singles --apply`, then `pairs`.
3. **Decide Drakneta** (and Drakniya): keep, or choose a different woman. If you change her photo, `bin\likeness.cmd pairs --sister Drakneta` re-checks her angel.
4. **Open the `review` folders** (Drakness 14, Draknoxa 12, Drakneta 8, Draknava 6) and move the good ones back to `gallery`.
5. **Draknoxa:** decide if 4 clear photos are enough.
6. **Run a few renders** in ComfyUI for the 7 angels whose photo changed (Ravaelle, Haniya, Gavrielle, Sandalyn, Remiah, Sammara, Nyxene): their Alpha 1 Prime workflows load the new photo already.
7. **Check the two AI-art faces** (Sandalyn and Remiah): the face model is less reliable on illustration, so look at them yourself.
8. The 5 Artist groups below 0.45 agreement were not used as candidates (Nia Nash, Una Ames, Wren Ellery, Gia West, Vera Lane): they may be more than one person.

## Doing it again

| You want to | Command |
| --- | --- |
| Is this folder one person, and who else looks like her | `bin\likeness.cmd folder NAME` |
| Clean one folder (a stranger goes to the pool, a doubtful photo to `review`) | `bin\likeness.cmd clean NAME --apply` |
| Sort a new batch dropped into `Prospects\Various` | `bin\likeness.cmd sort --singles --apply` |
| Split an Artist's photos into people | `bin\likeness.cmd group --apply` |
| Check the sisters as a family | `bin\likeness.cmd sisters` |
| Re-pair one angel after you change her sister | `bin\likeness.cmd pairs --sister Drakneta` (then `--apply`) |
| Put the last batch of moves back | `bin\likeness.cmd undo --apply` |

## Limits

- The face model was trained on real photos. It separates the people in this library well (91% right) but is less reliable on illustrated or heavily stylised art, closed eyes and turned heads; two faces in a picture are marked "unsure".
- "Similar but not the same" is a score band (0.15 to 0.40), not a judgement of looks; change `pairLow`, `pairHigh` or `--target` to move it. A face that looks right to you at 0.10 or 0.35 is allowed.
- Hair colour, outfit and background are ignored on purpose: the angel prompts set hair and eye colours themselves, so only the face is compared.
