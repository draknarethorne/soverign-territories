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

1. Drop originals into a hero's `gallery`, or into `Various\gallery` and let `likeness sort --singles` file them (or move them from another hero's folder).
2. Delete the ones that did not work out (in `gallery`; the tool tidies the rest).
3. Run `bin\originals.cmd` (`bin\originals.cmd --dry-run` previews first; `--only Angelica` does one folder).
4. Choose the photo for a hero: `bin\inputs.cmd set Angelica --photo angelica_image_<id>_944x1104.png`, then `bin\inputs.cmd reset --hero Angelica`.

## What `originals` does

| Step | What |
| --- | --- |
| Rename | Every original is named after the **folder it is in**, so you can shuffle freely between angels, sisters, prospects and artists. The id in the name is kept; only the prefix changes (details below the table). If the new name is taken the file is left alone with a warning. |
| Scale | Each original is fitted inside 944x1104 (the shape is kept, EXIF rotation applied), centred on cream, saved as `<name>_944x1104.png`. A phone screenshot of Facebook (tall, with the app's light navigation bar along the bottom) is first cut down to the picture itself, without the bars, caption and icons (`tools/art/screens.py`), unless her head reaches into them. A copy already newer than its original is skipped (`--force` redoes all). |
| Headshots | Each original with a clear face also gets `headshot_944x1104\<name>_head_944x1104.png` (see Headshots). `--no-headshots` skips this step. |
| Prune | A scaled copy that no original in that folder makes any more is **moved to `_archive\<the folder's path>\gallery_944x1104_org`**, never deleted (a headshot goes to the matching `headshot_944x1104_org`), so the person folders stay free of old copies. `originals --archive-old --apply` moves the `_org` folders that were left in the library (with a manifest; `--undo-archive` reverses it). Other files in the scaled folder are left alone. |
| Re-point | With the work done, a chosen photo (`photos` in `workspaces.json`) that was renamed is found again by its id: `workspaces.json`, the generated workflows that load it (repo and workspaces; a changed workspace file is backed up first) and the workspace input folders are updated. The same step is available alone as `bin\inputs.cmd photos` (preview with `--dry-run`). |

### Frames (a Prime input for partial-body photos)

Most originals are head-and-shoulders or waist-up, and an edit model keeps the framing of what it is given, so the Prime comes back cropped (FireRed most of all). For every original whose face is taller than 14% of the picture, `originals` also writes `frame_944x1104\<name>_frame_944x1104.png`: the photo shrunk so the face has the size of a standing figure's (about 9% of the height), placed at the top centre of the cream canvas, the rest left empty.

The Prime then draws the body below at the right scale. A full-length original gets none (use its `gallery_944x1104` copy); a screenshot is cut to its picture first, as above. `--no-frames` skips it; about 0.2 GB for the library.

The frame is a second **flow** beside the normal one, not a replacement: each hero keeps her normal photo and Prime workflows, and also gets Prime workflows that start from the frame (`Haniya_Qwen_Alpha_1_Prime_Frame`, and the FireRed pair).

How the flows work, where their images are stored and how to compare them: [prime-flows.md](prime-flows.md). To change a hero's frame image: `bin\inputs.cmd set Haniya --flow frame --photo haniya_image_<id>_frame_944x1104.png`. `inputs photos` leaves a chosen frame alone.

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
