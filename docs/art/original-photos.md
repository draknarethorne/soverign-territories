# Original photos: pick, rename, scale, prune

How the photos you start from (the originals every angel and sister is built from) are kept, named and handed to the workflows. One command does the housekeeping; you only drop, move and delete files.

## The library

Under the work folder (`paths.workRoot` in `workflows/workspaces.json`, today `B:\Soverign Territories`):

```text
Angels\Angelica\gallery                  your originals for Angelica (jpg, png, webp, bmp)
Angels\Angelica\gallery_944x1104         made by the tool: every original on a cream 944x1104 canvas, as PNG
Angels\Angelica\headshot_944x1104        made by the tool: the face of each original, cropped around it and scaled up (see Headshots)
Angels\Angelica\review                   photos the likeness tool is not sure about (yours to look at)
Angels\Angelica\gallery\z_angelica.txt   the person's name, profile and history (written by the likeness tool; see likeness.md)
_archive\Angels\Angelica\...             old scaled copies and set-aside duplicates (the same path as the folder)
_junk\Prospects\rhea_ives_...jpg         photos the likeness tool judged unusable, flat per side (Prospects, Artists), the name is in the file name; for you to look at and empty
Sisters\Draknara\...  Prospects\Anya Sloane\...  Artists\Pierre\Mara Locke\...  Various\...   the same layout in the other roots
```

The roots are Angels, Sisters (the old name, Models, is still read), Prospects (people who are not yet an angel or sister), Artists (an artist's photos, grouped into people) and `Various`, the pool of photos not sorted yet, at the top level next to them. `paths.photoRoots` in `workspaces.json` changes the list.

## The routine

**Ingest runbook (new photos): three commands.**

1. Drop the new photos into `Various\gallery` (any name; a photo that came from an artist and is dropped again goes back to that artist by its id, see below).
2. `bin\library-preview.cmd` shows what would happen, step by step, and moves nothing. Optional.
3. `bin\library.cmd` does it. Read the summary at the end; the log is `<work>\_reports\runs\library_sync_<time>.log`.

The preview runs each step independently against the current folders; it does not simulate the earlier steps' proposed moves. A file may therefore appear in more than one step's preview even though the real run moves it in sequence. Treat preview counts as current-state counts and use the completed run log for final results.

Then look at where everything landed: `bin\people-gallery.cmd` builds both
`<work>\_reports\library\people_gallery.html` and
`people_gallery_review.html` with the shared thumbnail cache beside them. The overview and filtered review use the same
identity sort modes and first-nine order, plus shared Chest-up and Head
thumbnail files. Prime-start suitability remains a photo-quality score,
not identity confidence. Sisters and Angels
are alphabetical, while Prospects and Potentials are ordered by usable
gallery-photo count, largest first. Click a thumbnail to open its source, or
the person name to open the complete review gallery filtered to that person.
The separate history link opens the person's `z_` file. Angel cards show their paired Sister,
current canonical hair color and three eligible Prospect alternatives ranked by pairing fit. The full all-candidate
rankings for every paired Angel are in `<work>\_reports\comparisons\pairings\angel-prospect-candidates.md`.
Chosen Angels and Sisters that came through Prospect processing also show their recorded Prospect identity beside
the chosen-photo status.
For high-volume maintenance, run `bin\people-gallery-review.cmd` when only
the review page needs refreshing. That page includes every Gallery and
Review photo, core-similarity ordering, identity/protection state, filters and
content-cached lazy-loaded thumbnails. Per-photo controls stage anchor,
protection, Review, Reject-to-Various or Review-approval actions; use the
downloaded manifest with `bin\likeness-actions.cmd validate FILE.json` or
`preview FILE.json` to check it against the current library. After reviewing
the preview, `bin\likeness-actions.cmd apply FILE.json --apply` makes a
verified backup before moving photos or updating the catalogue.
`bin\likeness-actions.cmd undo [BATCH_ID]` is preview-only;
`bin\likeness-actions.cmd undo [BATCH_ID] --apply` backs up and reverses the
newest active batch only if the recorded files and metadata are unchanged.
Run `bin\library.cmd` afterward to refresh derived files and reports. Folders
outside the catalogue's supported roots are view-only.
The Angel card prints a preview command for the top candidate; browser pages cannot safely launch filesystem
promotion commands, so run it in a terminal and review it before adding `--apply`. The Prime-start photo score describes
photo suitability, not identity confidence. Prospect cards also show the closest face-embedding matches among
sisters and readiness evidence (usable faces, full-length framing, face size, review and unusable-photo counts).
Those similarity values are candidates to inspect, not verified identities; framing counts do not measure pose
variety. `<work>\_reports\library\crop_review.html` shows every cropped photo beside
its uncropped original, and `<work>\_reports\library\crosscheck.md` who looks like whom across the lines that are kept
apart; `bin\likeness.cmd names` and `index` list the people. Run it again whenever you like: it repeats safely,
nothing is deleted, and a second run on a finished library changes nothing.
`bin\library.cmd --retry-junk` first sends everything in `_junk` back (prospects' photos to `Various`, an artist's photos to that artist's gallery) so the cropping and the rules look at it again; what is still junk returns to `_junk`.
`bin\library-check.cmd` is read only and says whether anything is waiting (exit 1 when it is).

### Report folders

`<work>\_reports` is grouped by purpose. The library routine keeps its current reports in `library`,
dated run logs in `runs`, Angel/Sister/Prospect likeness work in `comparisons\pairings`, historical
comparison material in `comparisons\history`, comparison sheets in `comparisons\images`, Prime sheets
in `comparisons\primes`, and move plans in `analysis`. Routine commands overwrite their current reports;
dated logs are retained. Old reports have been moved into these folders without deleting them.

**Backups before a real run.** `bin\library.cmd` creates a dated snapshot before changing files; if backup
fails, the routine stops before processing. The snapshot is written under `_backup\library-<timestamp>` and
contains the work root except `_archive` and older `_backup` snapshots, the configured ComfyUI inputs, and
`workflows\workspaces.json`. Its `manifest.json` lists each copied file with size and SHA-256; every run verifies
the copied file list, sizes and hashes before proceeding. ComfyUI output
renders are not included because the library routine does not modify them. To make a snapshot on demand,
`bin\library-backup.cmd` previews by default; add `--apply` to create it, or `--verify <snapshot>` to recheck one.
A failed copy is marked `INCOMPLETE.txt` and is not a usable snapshot.
On Windows, snapshot copy and verification use extended-length paths so
retained nested sandbox state can be backed up even when Windows long-path
support is disabled. This does not exclude old run evidence or weaken hash
verification; a failed snapshot remains incomplete and is never reused.
Standalone fixed-slot Angel/Sister recorded-name changes are narrower:
their action executor snapshots only the catalogue/history write set and
records the identity inventory hash, without copying unchanged images.
These transaction snapshots are verified by the same launcher but are not
eligible as full-library recovery baselines. Other actions retain full backup.
See [whole-person rename](likeness.md#whole-person-rename) for the boundary.

**The short way: `bin\library.cmd`** runs, in order:

While the shared likeness policy is draft, a likeness-enabled real run refuses
before backup, renaming, cropping or other housekeeping. Preview and check
remain available. Do not approve production merely to bypass this gate:
sandbox acceptance and the separate clean-full production rebuild are still
required. Threshold changes belong in the versioned policy, not `--min`.

| Step | What | Where the originals of a change are kept |
| --- | --- | --- |
| 1 `originals` | names every original after its folder, makes the scaled copy and headshot | old scaled copies: `_archive\<folder>\gallery_944x1104_org`; old headshots: `_archive\<folder>\headshot_944x1104_org` |
| 2 `duplicates` | the same picture twice (any folder, any name) | the extra copy: `_archive\<folder>\gallery_duplicates` |
| 3 `likeness crop` | cuts every photo down to the person: a phone's app bars, other people, animals and the background beside her; all the body in the picture stays | the uncropped photo: `_archive\<folder>\gallery_uncropped` (`likeness crop --undo` puts the last batch back) |
| 3 `likeness junk` | a photo that cannot feed a Prime (no usable face, a second person that cannot be cut away, bars over her head) goes to `_junk`. A prospect's or hero's photo that only needs clean-up goes to her `review` folder instead | `_junk\<side>`, her `review` |
| 4 `likeness reconcile` | shared incoming/Review proposal with frozen cores, tier permissions, preserved small groups and explicit holds; approved apply revalidates after a verified backup | `_reports\runs\reconcile_*.json`, full snapshot; `likeness reconcile --undo JOURNAL --apply` |
| 5 `likeness group --singles` | the artists' own galleries are emptied the same way, never across artists: into one of that artist's people, or a folder of their own. Only photos with no usable face, a second person or the app's bars stay | `likeness undo` |
| 6 `likeness retire-empty` | prospect folders with no original photos in either `gallery` or `review` are moved intact to `_retired`; folders with review photos and the `Various` pool are left alone | `_retired` |
| 7 `duplicates`, `originals` again | the moves create new names; `originals --check` must say IN SYNC | |
| 8 `sync-inputs`, 9 `crosscheck`, `index` | workflow inputs; the look-alike report; the people index | |

**Prime partial-body frame flow retired (Oct 19).** See [Retired frame images](#retired-prime-partial-body-frames) for what changed and where the preserved files went. The proposed `chest_944x1104` crop is not implemented; it remains a separate visual-review task.

The former `review`/`sort`/`singles`/`rematch` decision chain is no longer run
automatically. Reconciliation now also proposes reciprocal whole-identity
merges, qualified red-outlier splits and ID-preserving category transitions;
see [established-identity maintenance](likeness.md#established-identity-maintenance)
for policy controls, recovery and the bounded read-only final-core check.
Those paths have synthetic apply/undo tests, not completed real-batch
acceptance or demonstrated global convergence. A journal
undo requires its recorded photos and catalogue to remain unchanged; after
subsequent renaming or user decisions, use the verified snapshot/reviewed
recovery path rather than forcing stale destinations.

**The rules the routine keeps.** An artist's photos never cross to another artist, even when two people look alike (that is only reported). Prospects and artists never mix (also only reported). Cast Gallery protection and incoming Review admission are separate; similarity never grants automatic cast Gallery membership. The `_origins.json` file in the work folder records which artist every photo came from (by its id, which survives a rename and a crop).

**To start a part over.** `likeness pullback NAME ...` (or `--small 2`, or `--all`) sends prospect folders back to `Various`, and the routine sorts them again; a folder with a chosen photo is never pulled back. A looser second look at the pool: `likeness sort --assign 0.35` (preview first). The artists can be rebuilt from a flat backup of their folders: `likeness artists --from <backup>\Artists`.

**What `duplicates` does** (`bin\duplicates.cmd`, also step 2): the same picture can sit in two folders or twice in one under different ids (a download saved twice, a photo moved between prospects). It finds identical bytes in every `gallery` and `review` folder and keeps one copy.
The kept copy is a chosen photo first, then a gallery photo over a review photo, then Angels, Sisters, Prospects,
Artists, Various, then a name that already carries its folder's prefix. The others move to
`_archive\<their folder>\gallery_duplicates` (`originals` then prunes their scaled copies). A standalone
duplicate check only lists files with the same id but different bytes (a resaved copy); it does not move them.
During `library.cmd` ingest, when multiple incoming photos in `Various\gallery` share an ID but have different bytes, the file with the
uniquely newest last-modified timestamp stays in the gallery; the older incoming copies move to `Various\duplicates` with their names
preserved. That folder is outside the gallery/review buckets, so those photos wait for you to compare and sort manually rather than entering
likeness processing. If the newest timestamps tie, none of that ID's files are moved or used to replace an existing copy; the conflict is
reported for you to resolve. Once the incoming set has one unambiguous file, older matching gallery, review or `_junk` copies are moved to
`_archive\<their folder>\gallery_replaced`, and the incoming copy stays in the pool to be classified again. Byte-identical copies remain
ordinary duplicates. A changed file with a different ID cannot be recognized as a replacement automatically.

By hand, one step at a time:

1. Drop originals into a hero's `gallery`, or into `Various\gallery` and let `likeness sort --singles` file them (or move them from another hero's folder).
2. Delete the ones that did not work out (in `gallery`; the tool tidies the rest).
3. Run `bin\originals.cmd` (`bin\originals.cmd --dry-run` previews first; `--only Angelica` does one folder). `bin\originals.cmd --check` only asks: IN SYNC or OUT OF SYNC, exit 1. Run it after every move of files.
4. Choose the photo for a hero: `bin\inputs.cmd set Angelica --photo angelica_image_<id>_944x1104.png`, then `bin\inputs.cmd reset --hero Angelica`.

Not every photo has a headshot, by design: a headshot needs a face big enough to enlarge to 944x1104 without mush (a crop of at least 30% of the output height) and not hidden under a phone's app bars.

## What `originals` does

| Step | What |
| --- | --- |
| Rename | Every original is named after the **folder it is in**, so you can shuffle freely between angels, sisters, prospects and artists. The id in the name is kept; only the prefix changes (details below the table). If the new name is taken the file is left alone with a warning. |
| Scale | Each original is fitted inside 944x1104 (the shape is kept, EXIF rotation applied), centred on cream, saved as `<name>_944x1104.png`. A phone screenshot of Facebook (tall, with the app's light navigation bar along the bottom) is first cut down to the picture itself, without the bars, caption and icons (`tools/art/screens.py`), unless her head reaches into them. A copy already newer than its original is skipped (`--force` redoes all). |
| Headshots | Each original with a clear face also gets `headshot_944x1104\<name>_head_944x1104.png` (see Headshots). `--no-headshots` skips this step. |
| Prune | A scaled copy that no original in that folder makes any more is **moved to `_archive\<the folder's path>\gallery_944x1104_org`**, never deleted (a headshot goes to the matching `headshot_944x1104_org`), so the person folders stay free of old copies. `originals --archive-old --apply` moves the `_org` folders that were left in the library (with a manifest; `--undo-archive` reverses it). Other files in the scaled folder are left alone. |
| Re-point | With the work done, a chosen photo (`photos` in `workspaces.json`) that was renamed is found again by its id: `workspaces.json`, the generated workflows that load it (repo and workspaces; a changed workspace file is backed up first) and the workspace input folders are updated. The same step is available alone as `bin\inputs.cmd photos` (preview with `--dry-run`). |

### Retired: Prime partial-body frames

The Prime frame experiment was retired on Oct 19. `originals` does not generate
`frame_944x1104` images, and no Prime frame input flow is configured. The
previous library images and ComfyUI input copies were preserved in
`B:\Sovereign Territories\_archive\frame-retirement-20261019`; generated repo
workflows are under `workflows/_archive/frame-retirement-20261019`, while
installed workflow copies are in `workflows/.sync/backup/frame-retirement-20261019`.
Do not restore these as part of the standard library run. Partial-body photos
use the normal scaled photo as the Prime input. A possible chest crop remains
unimplemented pending visual review; see [prime-flows.md](prime-flows.md).

### Headshots

A headshot is the face of an original, found with the likeness tool's face detector (the same cache, so a photo is only looked at once), cropped to about 2.5 face heights around it in the standard 944x1104 shape and scaled up; it is never letterboxed. A photo with no face, a face under 60 px, or a crop too small to scale up without turning to mush gets none (the run reports how many were skipped). The whole library is about 0.9 GB.

To try one as a Prime input: `bin\inputs.cmd set Seraphine --photo seraphine_image_<id>_head_944x1104.png`, then `bin\inputs.cmd reset --hero Seraphine`. `inputs photos` leaves a chosen headshot alone; it never swaps it back for the full photo.

### How names are decided

The first rule that fits wins; `<n>` is the folder's name in lower case with underscores.

| The file is called | It becomes | Why |
| --- | --- | --- |
| `azaline_image_123.jpg`, `eva_emily_image_123.jpg`, `various_image_123.jpg`, `facebook_<time>_123.jpg` | `<n>_image_123.jpg` | the id (a Facebook id) is kept, the prefix is swapped |
| `Screenshot_<date>_<time>_Facebook.jpg`, `drakneta_screenshot_<date>_<time>.jpg` (any older spelling) | `<n>_shot_<yyyymmddhhmmss>.jpg` | the date and time are the id, written together with no `_`; the app name is dropped |
| `Draknara Base.jpg`, `Draknara Face left.jpg`, `Draknara Pose 2.jpg` | `<n>_base.jpg`, `<n>_face_left.jpg`, `<n>_pose_2.jpg` | the descriptor is kept |
| `<n>_anything.jpg` | unchanged | already right |
| `azaline_photo_wings.jpg` (another folder's prefix, no id) | `<n>_photo_wings.jpg` | the other folder's prefix is swapped |
| `images (3).jpeg`, `download.jpg`, any Google or web name | `<n>_pic_<8 hex>.jpg` | an id made from the picture's bytes: unique, and the same wherever you move it |

Three forms, then: `<n>_image_<facebook id>`, `<n>_shot_<yyyymmddhhmmss>` and `<n>_pic_<8 hex>`. Rename a folder (Pierre to `Awesome Fantasy`) and the next run renames everything in it, including descriptive names that still carry the old prefix (read from the ids in the folder's other files); move files out and they take the new folder's prefix, move them back and they take the first folder's again.

Two files with the same picture id in one folder (the same screenshot saved twice) are flagged as probable duplicates; delete one.

A chosen photo whose original is in another hero's folder, or is gone, is reported (`ELSEWHERE`, `MISSING`), never guessed. A hero whose photo is still a placeholder name is listed as `NO PHOTO`.

## Notes

- It needs Pillow (`pip install pillow`); WebP is read too.
- `rename_originals.py` and `rename_inputs.py` (a rename map for the old facebook/Screenshot names, sisters only) are superseded by this; nothing calls them.
- A scaled image becomes a workflow input only when you choose it (`inputs set`) or run `inputs photos`; `sync-inputs.cmd` and `inputs reset` also find images in the library.
- The old `scale_rename_prune_images.ps1` in the work folder now only forwards to `bin\originals.cmd`.
