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

Folders are of two kinds. A **person folder** is one person: Angels, Sisters (formerly Models), a Prospect, a Potential, and each person
grouped inside an Artist's folder (`Artists/Pierre/Mara Locke`). Prospects have at least five usable photos; Potentials have one to four and
stay active for future matching. Only Prospects qualify as Angel replacement candidates. **Mixed** folders (the artist folders themselves,
`Artists/*`, and `Various`) hold many people: they never describe a person, are never read (except the pool) and never move on their own.

`Various` (top level, next to Prospects and Potentials) is the **pool** that `sort` empties; drop new photos into `Various\gallery` and run
`bin\library.cmd`, which does `originals`, `duplicates`, `likeness crop`, `junk`, `review`, `sort --singles`, `group --singles`, `singles`,
`rematch`, then brings the scaled copies and headshots back in step ([original-photos.md](original-photos.md#the-routine)). `likeness
rebaseline` is a read-only whole-library preview; it does not move files.
After reviewing the category table and creating a verified library backup,
`likeness rebaseline --apply-categories` moves only complete Prospect/Potential
folders across the five-usable-gallery-photo boundary. It refuses the entire
batch if any destination collides or a source/root is missing, then regenerates
the preview and pairing reports. It does not apply identity reassignment, Junk,
Retired, or Angel-pairing suggestions.

## Names and history

Every person folder has a `z_<name>.txt` in its `gallery` (the `z_` keeps it at the end of the list; the image tools ignore it). The first line is `name: First Last`; after it come dated lines that the tools write when the folder is created, merged, paired, retired or marked reserved (`2026-10-10 reserved: looks like Sisters/Draknoxa (0.56); keep off cards below the top tier`). The name is her real name when you know it, otherwise the invented one the tool gave her.

The file travels with the folder, so a prospect who becomes an angel (or the reverse) keeps her history, and
an explicitly approved `pairs --apply` logs "was Anya Sloane" in the angel's file. `likeness names` shows every folder's name and writes
the missing files (preview unless `--apply`); a folder is never named after the pool or another angel, and photos
split off a sister do not take her name. Use `likeness rename "Old Prospect" "New Name"` to preview renaming a
prospect folder and its recorded name; add `--apply` to create a full snapshot, preserve the history, update
configured prospect exclusions, and repoint renamed photo inputs.

Settings live under `likeness` in `workflows/workspaces.json`: `mixed`, `pool`, `assign`, `margin`, `cluster`, `minCluster`, `odd`, `alike`, `minFace`, `pairLow`, `pairHigh`, `pairs` (angel to sister), `keepPhoto` (heroes whose photo never changes: Drakness, Angelica, Drakneta) and `anchors` (`{"Angelica": ["part of a photo name", ...]}`: photos that are certainly her).

The approved identity-metadata work is tracked in
[`2026-10-20-likeness-library-self-healing.md`](../plans/2026-10-20-likeness-library-self-healing.md).
Its versioned catalogue is [`data/art/likeness-library.json`](../../data/art/likeness-library.json),
validated by [`likeness-library.schema.json`](../../data/art/_schema/likeness-library.schema.json).
Person IDs are opaque and stable across folder renames or promotions. Photo IDs
use the normalized source ID in originals-managed names, independent of the
folder prefix; the current SHA-256 is a stale-file check, not the identity key.
This initial catalogue is empty and does not change current matching behavior.

The big runs and their results are written up in [likeness-reorg-2026-10-09.md](likeness-reorg-2026-10-09.md) and [likeness-reorg-2026-10-10.md](likeness-reorg-2026-10-10.md).

## Commands

Anything that moves files previews until you add `--apply`. Add `--sheet FILE.png` to see the faces involved (a labelled grid), which is the quickest way to check a suggestion. After moving, the originals tool runs (rename after the new folder, scale, prune, re-point chosen photos).

| Command | What it does |
| --- | --- |
| `likeness rebaseline [--apply-categories]` | whole-library preview of category changes, confident out-of-folder photos, current Junk-rule matches, unreadable files, Prospect/Potential pairs, and report-only alternatives for Angels below five usable photos; applying categories moves only complete Prospect/Potential folders across the five-photo threshold, after a verified backup |
| `likeness alike` | every pair of people at or above 0.30, most alike first, flagged when it is two angels, an angel with her own sister (intended) or an angel who resembles a different sister; then **look-alike families** |
| `likeness compare Angelica azaline` | how alike two folders are, in words and as a percentile of all pairs, plus the closest photo pairs |
| `likeness folder Drakness` | is this folder **one person**? How many photos agree, are borderline or look like someone else; the ones to check with where each would go; for one person, who else looks like her. `--apply` moves only the "someone else" photos; `--all` lists every score |
| `likeness like path\to\photo.jpg` | which folders a new photo looks like, best first |
| `likeness clean [NAMES] [--group Sisters]` | the folder check for many folders at once, anchored on the chosen photo and the ComfyUI renders: a clear stranger goes to a matching person or the pool, a doubtful photo to the folder's `review` folder; the chosen photo never moves. A sister's folder only loses photos below `--sister-out` (0.05); `--keep` (0.25) is the score that keeps a photo |
| `likeness artists --from BACKUP\Artists` | resets the artists' folders from a flat backup: every photo back under the artist it came from, then to that artist's person it looks like; the rest stay in the artist's `gallery`. `--junk`, `--gallery`, `--assign`, `--keep`, `--margin`; see [The artists](#the-artists-the-pool-and-cropping) |
| `likeness group [ARTISTS] [--singles]` | empties an artist's own gallery into that artist's people (`--join`, `--min-photos`, `--cohesion`, `--single-join`); with `--singles` every good photo gets a person, new ones included. Never across artists |
| `likeness crop [--no-background] [--undo]` | cuts every photo down to the person: the app's bars, other people, animals and the background beside her. The uncropped original is kept in `_archive\<folder>\gallery_uncropped` |
| `likeness crosscheck` | who looks like whom across the lines kept apart (artist against artist, prospect against an artist's person) to `<work>\_reports\library\crosscheck.md`; nothing moves |
| `likeness pullback NAME ... [--small 2] [--all]` | sends prospect folders back to `Various` so `sort` places their photos again; a folder with a chosen photo stays; `likeness undo` reverses it |
| `likeness sort [--singles] [--assign 0.35]` | empties `Various`: a photo of an artist goes home, a confident match moves to that person (angels and sisters too), a new group becomes a Prospect at five or more photos or a Potential below five, or joins an angel or sister it is the same woman as (0.55) |
| `likeness junk [--keep-multi] [--recheck] [--reset]` | sets aside in `<work>\_junk\Prospects` or `_junk\Artists` what cannot feed a Prime (no usable face, a face under 60 px, a second person that `crop` could not cut away, bars over her head). `--recheck`: usable ones go back. `--reset`: everything goes back through the crop and the rules. `likeness undo` reverses the last batch |
| `likeness rematch [--min 0.48]` | compares Prospect and Potential folders and previews likely same-person merges; cast matches are reported for review |
| `likeness singles [--min 0.40]` | a one-photo Prospect or Potential joins the person she matches with the required margin |
| `likeness retire-empty` | preview empty Prospect and Potential folders with no gallery or review originals; `--apply` moves those folders intact to `_retired` |
| `likeness sisters` | do the sisters read as one family around the anchor (`--anchor-sister`, Drakness)? Each sister against Drakness in photos and in renders, her place among everyone in the library, the nearest other sister, and who could replace a sister that is far out; `--md FILE` writes the table |
| `likeness pairs [--sister NAME]` | previews Angel candidates against configured counterparts using the shared score; eligibility, likeness band and variety weights are detailed below. Current Angel changes are manual: do not apply a score-ranked replacement without the user's explicit choice. `--apply` changes photos and workflow inputs; automated pairing/swapping is deferred to the future Demon phase. |
| `likeness review [NAMES] [--out]` | the photos set aside in `review` folders, each against her own folder and everyone else: one that is probably her (0.20 or more, `--back`) goes back to her gallery, one that clearly looks like someone else goes to that person, the rest stay. With `--out`, a photo that is clearly not her and matches nobody becomes a new prospect (photos that look alike share one; its history says where it came from). Preview unless `--apply` |
| `likeness loosen` | what looser settings would do, measured and not applied: at 0.05, 0.10 and 0.15 below today's assign score, how many Various and review photos would move, which would go where, and which folders may be one person (same person is about 0.55 and up). Read-only |
| `likeness lookalikes [--min 0.30]` | the guard for low-tier cards: every prospect or artist person scoring at least 0.30 against a sister or angel, most alike first. `--apply` writes a `reserved:` line into her `z_` file. Keep reserved people off cards below the top tier |
| `likeness names` | every folder's name and history file; `--apply` writes the missing ones (from the move log, or the invented name) |
| `likeness rename "Old Prospect" "New Name"` | renames a prospect folder and its recorded name; previews by default, and `--apply` first creates a full snapshot, preserves history, updates configured exclusions, and repoints photo inputs |
| `likeness index [--import FILE]` | the table to pick from, `<work>\people_index.csv` (a spreadsheet) and `.md`: one row per person with her photos, headshots, review count, best Prime photo, who she looks like, reserved, and the profile columns. `--import` reads the profile columns of an edited CSV back into the `z_` files (preview unless `--apply`) |
| `likeness profile NAME... --type "dark elf" --roles rogue,assassin --elements Darkness` | sets the profile of one or more people (`--sex --type --roles --elements --tier --tags`; several values with commas; `-` clears a key) |
| `likeness who --roles rogue --elements Darkness` | who matches: every filter must match, a word matches inside a value; prospects and artists unless `--all`; with no filter, the people still to classify; reserved people are marked |
| `likeness photos [NAMES]` | picks the 1_Prime photo for every angel: her best-scoring photo (her face, one clear face, some body in view, portrait, enough pixels). `likeness.keepPhoto` heroes (Drakness, Angelica, Drakneta) never change, and a chosen photo only changes when the best scores 0.12 higher. A sister's photo is only reported; `--sisters` changes them too. `--apply` sets it in `workspaces.json` and the workflows |
| `likeness merge Mia "Eva Emily"` | every photo of one folder into another (one person under two names); the emptied folder is moved to `_retired` and the history says what happened |
| `likeness retire azaline` | every photo of a folder back to `Various`, so she can be cast again |
| `likeness archive-list tmp\archive-people.md` | preview a Markdown checklist of `Prospects/Name` or `Artists/Artist/Person` folders to archive whole under `_retired`; `--apply` moves each folder with its photos, derived files and `z_` history and checks it off. Refuses people whose photos are selected by an active workflow, and removes archived photos from the likeness cache |
| `likeness promote "Dara Ives" Nyxene` | preview a Prospect-to-Angel swap; `--apply` returns the current Angel to `Prospects/<z_ name>`, promotes the Prospect, preserves and appends both histories, selects a suitable source photo, regenerates scaled/headshot/frame files, updates `workspaces.json` and generated workflow inputs, and copies needed images into ComfyUI workspace input folders. Run `bin\refresh.cmd Nyxene` afterward to regenerate prompts/workflows and deploy the latest set |
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

The detector finds every face, and the largest *person* is the one that is compared. It also finds faces on animals (a bear, a wolf, a horse); they score lower (about 0.55 to 0.82) than a woman's face (0.9 and up), so when a face is certain, lower-scoring ones are animals and do not count as a person (the face data records them as `an`).
When a woman and a man are in one photo and his face is the larger, a man's face lands in her folder and nudges her average face, so other men start to look like her (the Elise Frost problem). Three defences:

1. `likeness crop` cuts the other person or animal away when there is a clean line between them and her (and keeps the uncropped original in `_archive`). Most such photos become usable this way.
2. When the other subject overlaps her, a prospect's photo is set aside in her `review` folder; in an artist's gallery or `Various` it is left, and `likeness junk` sets it aside (`_junk`) when a second face is at least 0.3 of the main face's size (`likeness.multiFace`); a small passer-by in the background is not a problem and stays.
3. `likeness junk --recheck` looks at `_junk` again with the current rules and sends the usable photos back to the folder their file name says (or to `Various` when a prospect's folder is gone); `--reset` sends all of it back through the crop and the rules. Drag a photo from `_junk` into `Various` yourself and it is sorted like any new photo.

## Prospects and artists are kept apart

Prospects come from what you pick, artists from an artist's work, so the checks never mix them: a photo is not sent from one side to the other, they are not merged, and a new person split off an artist's person stays in that artist's folder.
Artists are also kept apart from each other: a photo stays with the artist it came from (`_origins.json` records it by photo id), and the people of one artist are never merged with another's, even when they look alike.
`likeness crosscheck` lists those look-alikes, and prospects that look like an artist's person, in `<work>\_reports\library\crosscheck.md` so you can decide.
The people gallery at `<work>\_reports\library\people_gallery.html` shows each Angel's paired Sister,
canonical hair color and top eligible Prospect alternatives by the shared likeness-plus-photo-variety score.
The complete ranked comparisons at `<work>\_reports\comparisons\pairings\angel-prospect-candidates.md`
show similarity, usable photo count, likeness cost, photo bonus and adjusted cost. Rebaseline uses the same
score and saved-render evidence as `likeness pairs`; its global assignment can differ from independent
per-Angel ranks because it prevents duplicate assignments and penalizes clashes. Photo count is a proxy for
available material, not a measurement of distinct poses or outfits.

Prospects regroup freely among themselves, and angels and sisters can take from prospects: a prospect who is the same woman as an angel or sister (0.55 and up) is one person with her, and the `z_` file of the angel or sister remembers who the prospect was, so she can be given back when you swap the cast.
(Oct 10 the tool had moved 6 photos across; they were put back.)

## The artists, the pool and cropping

- **Artists.** `likeness group --singles` takes everything loose in `Artists\<A>\gallery`: a group that is the same woman as one of A's people joins her, other groups and single photos become new people of A (named by the tool, rename any time: the photos follow). Only a photo with no usable face, a second person that cannot be cut away, or the app's bars over her head stays in A's gallery.
- **The artists' reset.** `likeness artists --from <backup>\Artists` rebuilds from a flat backup of the artists' folders (the Oct 9 one is `_backup\2026-10-09-before-likeness-reorg\Artists`); it records every photo's artist in `_origins.json` by photo id.
- **The pool.** A photo dropped into `Various` that came from an artist goes back to that artist; otherwise `sort` places it as above. To redo prospects: `likeness pullback NAME ...` (or `--small 2`, or `--all`) sends them to `Various` and the routine sorts them again, and `likeness sort --assign 0.35` takes a looser second look at the pool (preview first, so that big folders are not cross-pollinated).
- **Cropping.** `likeness crop` cuts every photo (Angels, Sisters, chosen photos, Prospects, Artists, `Various`) down to the person: the app's bars, other people and animals when there is a clean line between them and her, and the background about three and a half face widths either side, above the hair and beside the body, keeping all of the body in the picture. A close-up, a photo with little to cut, and a photo with her head low in the frame are left alone.
  The uncropped original is kept in `_archive\<folder>\gallery_uncropped` (`likeness crop --undo` puts the last batch back). A prospect's photo that cannot be cleaned up (the other subject overlaps her, or her head is under the app's bars) goes to her `review` folder and `review` leaves it there (`_cleanup_hold.json`).
A photo of an artist's person that cannot be cleaned up, with an animal or another person in the way, goes back to that artist's own gallery for you to look at, and the grouping does not pick it up again. In `Various` it is left for `junk`.

## The archive and `_junk`

The old scaled copies (`_org`) and set-aside duplicates are in `<work>\_archive\<same path>` and out of the person folders; `originals --archive-old --apply` moved the ones that were there (`--undo-archive` reverses it). Photos that cannot feed a Prime are in `<work>\_junk\Prospects`, `_junk\Artists` (and `Sisters`, `Angels`), flat, so you can scan them in one view; the person is in the file name. Nothing is deleted until you do it.

## How Angel candidate rankings work

The codex (or `likeness.pairs` in `workspaces.json`) defines the fixed Angel-to-Sister counterpart. Candidate eligibility requires at least five usable photos and folder cohesion of at least 0.45. Potentials do not qualify as Angel candidates.

Ranking is two-stage: likeness-fit cost against the counterpart, then a bounded variety adjustment of 0.02 at 10 usable photos, 0.04 at 15, and 0.06 at 20 or more. The target fit is 0.28 within the preferred 0.15–0.40 likeness band; photo count can break a close ranking but cannot establish identity or qualify an out-of-band candidate. Global pairing also avoids assigning one person twice and penalizes clashes among selected candidates.

The People Gallery and rebaseline reports show alternatives only. Current Angel replacements are user-selected; do not automatically change an Angel identity from a score.
The four current choices are recorded in the [library-management rebaseline](../plans/2026-10-19-library-management-rebaseline.md). Revisit automated pairing or swapping for the future Demon phase only after its counterpart mapping and direction-specific likeness rules are agreed. Sisters remain fixed unless the user chooses otherwise.

Artists' people are not Angel candidates. When an explicit promotion is chosen and applied, the tool preserves the person's `z_` history and returns the outgoing identity to its appropriate active category; it does not delete photos.

## Choosing between look-alikes

1. `likeness alike --sheet alike.png`, then look at the sheet.
2. Pick the one you like best of each family. For the others: `likeness retire NAME --apply` returns their photos to the pool; `sort` can then give them to someone they match or to a new prospect.
3. A retired angel with a chosen photo loses it (`inputs photos` reports it); pick another with `inputs set`, or run `pairs --sister NAME` to preview candidates. Apply a replacement only after the user explicitly chooses it.
4. Check the other direction too: a prospect that matches a sister (the `alike` list) should not become an angel.

To deactivate a Prospect or an artist's person without returning her photos to the active pool, write unchecked Markdown items in `tmp\archive-people.md`:

```md
- [ ] Prospects/Name
- [ ] Artists/Artist/Person
```

Run `bin\likeness.cmd archive-list tmp\archive-people.md` to preview, then add `--apply` to move the complete person folders into `_retired` and mark the items done. The likeness cache entries for their photos are removed. Archived people can be restored by moving their folder back; the tool will calculate fresh likeness data when next scanned.

## Notes and limits

- The model was trained on real photos. For this library it separates people well but not perfectly: treat the suggestions as a first pass and look at the sheet, especially for clusters of 3 or 4.
- A photo with no face, or a face smaller than 60 px, is left out (`likeness scan` lists them). Only the largest face in a photo is used.
- Same-person clusters are cut at 0.25 average similarity (95% pure on your folders); raise `cluster` for stricter groups.
- Nothing is deleted. A duplicate already in the destination is set aside in the source folder's `gallery_org`.
