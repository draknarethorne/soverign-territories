# Original photos: pick, rename, scale, prune

How the photos you start from (the originals every angel and sister is built from) are kept, named and handed to the workflows. One command does the housekeeping; you only drop, move and delete files.

## The library

Under the work folder (`paths.workRoot` in `workflows/workspaces.json`, today `B:\Soverign Territories`):

```text
Angels\Angelica\gallery                  your originals for Angelica (jpg, png, webp, bmp)
Angels\Angelica\gallery_944x1104         made by the tool: every original on a cream 944x1104 canvas, as PNG
Angels\Angelica\gallery_944x1104_org     archive: the previous scaled copies, and any copy whose original you removed
Models\Draknara\...  Prospects\Various\...  Artists\Fantasy\...   the same layout in the other roots
```

The roots are Angels, Models (the sisters), Prospects (candidates not yet assigned; `Various` is the holding pen) and Artists; `paths.photoRoots` in `workspaces.json` changes the list.

## The routine

1. Drop originals into a hero's `gallery`, or move them there from `Prospects\Various\gallery` (or from another hero's folder).
2. Delete the ones that did not work out (in `gallery`; the tool tidies the rest).
3. Run `bin\originals.cmd` (`bin\originals.cmd --dry-run` previews first; `--only Angelica` does one folder).
4. Choose the photo for a hero: `bin\inputs.cmd set Angelica --photo angelica_image_<id>_944x1104.png`, then `bin\inputs.cmd reset --hero Angelica`.

## What `originals` does

| Step | What |
| --- | --- |
| Rename | Every original is named after the **folder it is in**, so you can shuffle freely between angels, sisters, prospects and artists. The unique id in the name is kept and only the prefix before it changes: `azaline_image_123.jpg`, `eva_emily_image_123.jpg`, `various_image_123.jpg` or `facebook_<time>_123.jpg` all become `angelica_image_123.jpg` in Angelica's folder; a phone screenshot `Screenshot_<date>_<time>_Facebook.jpg` becomes `angelica_screenshot_<date>_<time>_facebook.jpg`; a `Base`, `Face ...` or `Pose ...` file keeps that word; any other name that starts with another folder's prefix (`azaline_photo_wings.jpg`) just swaps it. A name with **no id at all** (a Google image, `images (3).jpeg`, `download.jpg`) becomes `angelica_images_3_h<8 hex>.jpg`: its words plus an id made from the picture's bytes, so it is unique and keeps the same id wherever you move it. If the new name is taken the file is left alone with a warning, and two files with the same picture id are flagged as probable duplicates. |
| Scale | Each original is fitted inside 944x1104 (the shape is kept, EXIF rotation applied), centred on cream, saved as `<name>_944x1104.png`. A copy already newer than its original is skipped (`--force` redoes all). |
| Prune | A scaled copy that no original in that folder makes any more is **moved to `gallery_944x1104_org`**, never deleted. This is how deleting or moving an original cleans up after itself. Other files in the scaled folder are left alone. |
| Re-point | With the work done, a chosen photo (`photos` in `workspaces.json`) that was renamed is found again by its id: `workspaces.json`, the generated workflows that load it (repo and workspaces; a changed workspace file is backed up first) and the workspace input folders are updated. The same step is available alone as `bin\inputs.cmd photos` (preview with `--dry-run`). |

A chosen photo whose original is in another hero's folder, or is gone, is reported (`ELSEWHERE`, `MISSING`), never guessed. A hero whose photo is still a placeholder name is listed as `NO PHOTO`.

## Notes

- It needs Pillow (`pip install pillow`); WebP is read too.
- `rename_originals.py` and `rename_inputs.py` (a rename map for the old facebook/Screenshot names, Models only) are superseded by this; nothing calls them.
- A scaled image becomes a workflow input only when you choose it (`inputs set`) or run `inputs photos`; `sync-inputs.cmd` and `inputs reset` also find images in the library.
- The old `scale_rename_prune_images.ps1` in the work folder now only forwards to `bin\originals.cmd`.
