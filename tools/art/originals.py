#!/usr/bin/env python3
"""Keep the original-photo library in step with what you drop in it (preview unless --apply).

The library is <work root>/<Root>/<Name>/gallery (your originals) and <Name>/gallery_944x1104 (what this makes), for the roots
Angels, Sisters, Prospects, Artists and Various (workspaces.json paths.photoRoots; the old name Models is still read). For every <Name> folder that has a gallery:

  1. RENAME  each original after the FOLDER it is in. Whatever it was called before (another angel, a sister, a prospect, an artist, a facebook
             download, a phone screenshot), its id is kept and only the prefix changes. Rename the folder itself and every name follows.
             The convention is  <name>_image_<facebook id>,  <name>_shot_<yyyymmddhhmmss>  (a screenshot) and  <name>_pic_<8 hex>  (anything with
             no id, such as a Google image; the id is made from the picture's bytes, so it is unique and stays the same when you move it on):
               azaline_image_123.jpg, eva_emily_image_123.jpg, various_image_123.jpg, facebook_<time>_123.jpg  ->  angelica_image_123.jpg
               Screenshot_<date>_<time>_Facebook.jpg, drakneta_screenshot_<date>_<time>.jpg                   ->  angelica_shot_<date><time>.jpg
               images (3).jpeg, download.jpg                                                                  ->  angelica_pic_<8 hex>.jpg
               azaline_photo_wings.jpg (another folder's prefix)                                              ->  angelica_photo_wings.jpg
             A rename that would overwrite another file is skipped with a warning, never forced; two files with the same picture id are flagged as
             probable duplicates.
  2. SCALE   each original onto a light-grey 944x1104 canvas (shape kept, EXIF rotation applied) as <name>_..._944x1104.png.
             A copy that is already newer than its original is left alone (--force makes them all again).
  3. PRUNE   every image in gallery_944x1104 that no original in that folder's gallery makes any more (you deleted or moved the
             original, or it has an old name). They are moved into <work root>/_archive/<the folder's path>/gallery_944x1104_org, never
             deleted, so the person folders hold only what is live; other files are never touched.
  4. REPOINT (with --apply) a photo you chose in workspaces.json ("photos") that was renamed or moved is pointed at its new name in
             workspaces.json and in the workflows; the same as `inputs photos`.

The routine: drop or move originals, delete the ones that did not work out, run originals.cmd.

  python tools/art/originals.py                    # preview everything
  python tools/art/originals.py --apply
  python tools/art/originals.py --only Angelica --apply
  python tools/art/originals.py --archive-old      # move the *_org folders already in the library into _archive (--apply; --undo-archive reverses it)
"""
import argparse
import datetime
import fnmatch
import json
import os
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflows"))
import comfy_workflows as cw  # noqa: E402
import screens  # noqa: E402

# Neutral light grey, the studio backdrop the 0_Edit renders and studio prompts use (was cream until Oct 26, 2026).
STUDIO_GREY = (190, 190, 190)
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
EXT = r"(?:jpe?g|png|webp|bmp)"
# Names that carry their own unique id keep it, whatever prefix they had before: the prefix is simply swapped for the folder's.
RULES = [
    (re.compile(rf"^facebook_.*_(\d+)\.{EXT}$", re.I), lambda m, p: f"{p}_image_{m[1]}"),
    (re.compile(rf"^(?:.*_)?image_(\d+)\.{EXT}$", re.I), lambda m, p: f"{p}_image_{m[1]}"),
    # a screenshot: old spellings (screenshot, date_time, an app name) all become shot_<date><time>
    (re.compile(rf"^(?:.*[_-])?(?:screenshot|shot)[_-](\d{{8}})[_-]?(\d{{6}})(?:[_-].*?)?\.{EXT}$", re.I), lambda m, p: f"{p}_shot_{m[1]}{m[2]}"),
    (re.compile(rf"^(?:.*_)?pic_([0-9a-f]{{8}})\.{EXT}$", re.I), lambda m, p: f"{p}_pic_{m[1].lower()}"),
    (re.compile(rf"^(?:Drakn\w+|[a-zA-Z0-9\-]+)\s+(Base|Face.*|Pose.*)\.{EXT}$", re.I), lambda m, p: f"{p}_" + re.sub(r"\s+", "_", m[1].lower().strip())),
]
# the part of a name before its id, i.e. the prefix an original carried in the folder it came from
OLD_PREFIX = re.compile(r"^(.+?)_(?:image_\d|shot_\d|screenshot_\d|pic_[0-9a-f]{8})", re.I)
SLUG_MAX = 24


def prefix_of(folder):
    return re.sub(r"\s+", "_", folder.lower().strip())


def content_id(path):
    """A short id from the picture's bytes: the same picture keeps it when it is renamed or moved, two different pictures never share it."""
    import hashlib
    return hashlib.sha1(pathlib.Path(path).read_bytes()).hexdigest()[:8]


def folder_prefixes(names, prefix):
    """The prefixes the originals in one folder still carry from before (the folder was renamed, or they came from another one), read from the ids in their names."""
    out = set()
    for n in names:
        m = OLD_PREFIX.match(n)
        if m and m[1].lower() != prefix and m[1].lower() != "facebook":
            out.add(m[1].lower())
    return out


def standard_name(name, prefix, known=(), digest=None):
    """The name an original gets in the folder with this prefix.

    An id in the name (a facebook id, `..._image_<id>`, a screenshot's date and time, `pic_<hex>`) is kept and only the prefix changes, so an original moved between an
    angel, a sister, a prospect or an artist, or kept in a folder you renamed, follows the folder. A name that starts with another known prefix (`azaline_photo_x`)
    swaps that prefix. Anything else (a Google download, `images (3).jpeg`) becomes <prefix>_pic_<id from the picture's bytes>: unique, and the same wherever it is moved.
    `known` are the other prefixes in the library (longest first); `digest` is that id, or a function that makes it."""
    plain = name[1:] if name.startswith(".") else name
    stem, ext = os.path.splitext(plain)
    ext = ext.lower()
    ext = ".jpg" if ext == ".jpeg" else ext
    for pattern, build in RULES:
        m = pattern.match(plain)
        if m:
            return build(m, prefix) + ext
    low = stem.lower()
    if low.startswith(prefix + "_"):
        return stem + ext
    for other in known:
        if low.startswith(other + "_") and len(low) > len(other) + 1:
            return f"{prefix}_{stem[len(other) + 1:]}{ext}"
    ident = digest() if callable(digest) else digest
    if ident:
        return f"{prefix}_pic_{ident}{ext}"
    slug = re.sub(r"[^a-z0-9]+", "_", low).strip("_")[:SLUG_MAX].strip("_") or "image"
    return f"{prefix}_{slug}{ext}"


def images(folder):
    if not folder.is_dir():
        return []
    return sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXT), key=lambda p: p.name.lower())


ARCHIVE = "_archive"


def archive_dir(folder, work, name):
    """Where the old copies of a library folder go: <work>/_archive/<the folder's own path>/<name>, so the person folders hold only what is live."""
    try:
        rel = pathlib.Path(folder).relative_to(work)
    except ValueError:
        return pathlib.Path(folder) / name
    return pathlib.Path(work) / ARCHIVE / rel / name


def move_into(src, dst):
    """Move a folder to dst; when dst exists the files are merged (a name already there is kept, and the source copy dropped when identical). Returns [(from, to)] of the files moved."""
    done = []
    for p in sorted(src.rglob("*")):
        if p.is_file():
            target = dst / p.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if target.stat().st_size == p.stat().st_size:
                    p.unlink()
                    continue
                target = target.with_name(f"{target.stem}_{content_id(p)}{target.suffix}")
            os.replace(p, target)
            done.append((str(p), str(target)))
    shutil.rmtree(src, ignore_errors=True)
    return done


def archive_old(work, roots, apply):
    """Move every *_org folder inside the library (gallery_944x1104_org, headshot_944x1104_org, gallery_org) into <work>/_archive, mirroring the path; a manifest of the files is written so it can be undone."""
    found = []
    for root in roots:
        found += [d for d in sorted(root.rglob("*_org"))
                  if d.is_dir() and d.name.casefold() != "gallery_org"]
    moves, files = [], 0
    for d in found:
        n = sum(1 for p in d.rglob("*") if p.is_file())
        files += n
        dst = archive_dir(d.parent, work, d.name)
        print(f"  {'MOVED' if apply else 'move '} {d.relative_to(work).as_posix()}  ({n} files)  ->  {dst.relative_to(work).as_posix()}")
        if apply:
            moves += move_into(d, dst)
    print(f"{len(found)} folder(s), {files} file(s) " + ("moved to _archive" if apply else "would move to _archive (preview; use --apply)"))
    if apply and moves:
        manifest = pathlib.Path(work) / ARCHIVE / f"manifest-{datetime.datetime.now():%Y%m%d-%H%M%S}.json"
        manifest.write_text(json.dumps(moves, indent=0), encoding="utf-8")
        print(f"manifest: {manifest} (python tools/art/originals.py --undo-archive puts them back)")


def undo_archive(work, apply):
    """Put the files of the newest archive manifest back where they came from."""
    manifests = sorted((pathlib.Path(work) / ARCHIVE).glob("manifest-*.json"))
    if not manifests:
        sys.exit("no archive manifest found")
    moves = json.loads(manifests[-1].read_text(encoding="utf-8"))
    back = 0
    for src, dst in moves:
        if pathlib.Path(dst).exists():
            back += 1
            if apply:
                pathlib.Path(src).parent.mkdir(parents=True, exist_ok=True)
                os.replace(dst, src)
    print(f"{back} of {len(moves)} file(s) {'put back' if apply else 'would go back'} ({manifests[-1].name})" + ("" if apply else " (preview; use --apply)"))
    if apply:
        manifests[-1].rename(manifests[-1].with_suffix(".undone"))


def fit(src, dest, size, box=None, *, cleanup=True):
    """Scale src to fit inside size (shape kept), centre it on the light-grey canvas and write a PNG (through a temporary file).
    Unless cleanup=False, a Facebook screenshot is cut to the picture (screens.py)
    when the head clears its bars (box = face fractions). Prepared natives disable cleanup."""
    from PIL import Image, ImageOps
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
    if cleanup and screens.is_reel_ui(im) and (not box or screens.head_clear(box)):
        im = screens.clean(im)
    rgba = im.convert("RGBA")
    w, h = size
    scale = min(w / rgba.width, h / rgba.height)
    nw, nh = max(1, round(rgba.width * scale)), max(1, round(rgba.height * scale))
    small = rgba.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", size, STUDIO_GREY)
    canvas.paste(small, ((w - nw) // 2, (h - nh) // 2), small)
    if hasattr(dest, "write"):
        canvas.save(dest, format="PNG")
        return
    tmp = dest.with_name(dest.name + ".tmp")
    try:
        canvas.save(tmp, format="PNG")
        os.replace(tmp, dest)
    finally:
        if tmp.exists():
            tmp.unlink()


def is_fresh(src, dest, size):
    if not dest.exists() or dest.stat().st_mtime < src.stat().st_mtime:
        return False
    return cw.image_size(dest) == tuple(size)


FACE_SPAN = 2.5  # the crop is this many face heights tall: head, hair and shoulders
MIN_FACE_PX = 60  # a smaller face (in the original's pixels) would only be blown up into a blur


def headshot_box(img_size, box, size):
    """(left, top, right, bottom) in the source: a crop of the standard shape centred on the face (box = x, y, w, h as fractions of the picture), moved or shrunk to stay inside it."""
    W, H = img_size
    fw, fh = box[2] * W, box[3] * H
    cx, cy = (box[0] + box[2] / 2) * W, (box[1] + box[3] / 2) * H - 0.12 * fh  # a little up: the box stops at the brow, the hair is above it
    ch = fh * FACE_SPAN
    cw_ = ch * size[0] / size[1]
    shrink = min(1.0, W / cw_, H / ch)
    cw_, ch = cw_ * shrink, ch * shrink
    x0 = min(max(cx - cw_ / 2, 0), W - cw_)
    y0 = min(max(cy - ch / 2, 0), H - ch)
    return round(x0), round(y0), round(x0 + cw_), round(y0 + ch)


def headshot(src, dest, size, box, *, cleanup=True):
    """Frame the face as PNG; False when too small. cleanup=False skips screenshot stripping only."""
    from PIL import Image, ImageOps
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
    if cleanup and screens.is_reel_ui(im):
        # the app's bars are cut away, and a head that reaches into them gets no headshot (the bar would be in it)
        if not screens.head_clear(box):
            return False
        x0, y0, x1, y1 = screens.clean_box(im.size)
        W, H = im.size
        box = [(box[0] * W - x0) / (x1 - x0), (box[1] * H - y0) / (y1 - y0), box[2] * W / (x1 - x0), box[3] * H / (y1 - y0)]
        im = im.crop((x0, y0, x1, y1))
    crop = headshot_box(im.size, box, size)
    if crop[3] - crop[1] < size[1] * 0.3:
        return False
    if dest is None:
        return True  # a check only
    out = im.crop(crop).resize(size, Image.LANCZOS)
    if hasattr(dest, "write"):
        out.save(dest, format="PNG")
        return True
    tmp = dest.with_name(dest.name + ".tmp")
    try:
        out.save(tmp, format="PNG")
        os.replace(tmp, dest)
    finally:
        if tmp.exists():
            tmp.unlink()
    return True


class Faces:
    """Where the main face is in each photo: the likeness tool's cache (by file content), asking its detector only for photos it has not seen."""

    def __init__(self):
        import likeness
        self.likeness = likeness
        self.cache = likeness.Cache(likeness.DATA / "likeness_cache.json")
        self.embed = None

    def of(self, path):
        """(box, face size in pixels), or (None, 0) when there is no face."""
        sha = self.cache.sha(path)
        data = self.cache.emb.get(sha)
        if data is None:
            self.embed = self.embed or self.likeness.Embedder()
            try:
                data = self.embed(path) or {"faces": -1}
            except Exception:  # noqa: BLE001 - one unreadable photo must not stop the rest
                data = {"faces": -1}
            self.cache.emb[sha] = data
        return data.get("box"), data.get("px", 0)

    def save(self):
        self.cache.save()


def make_headshots(sources, folder, size, args, tally, faces):
    """headshot_<W>x<H>/<name>_<W>x<H>.png for every original with a usable face (not made again while newer than the original); copies whose original is gone, or has no face, are moved to the _archive copy of headshot_<W>x<H>_org."""
    out_dir, archive = folder / f"headshot_{size[0]}x{size[1]}", archive_dir(folder, args.work, f"headshot_{size[0]}x{size[1]}_org")
    wanted, made, skipped = set(), 0, 0
    for path, final in sources:
        name = f"{re.sub(r'_[0-9]+x[0-9]+$', '', os.path.splitext(final)[0])}_head_{size[0]}x{size[1]}.png"  # _head_ keeps it apart from the full photo's copy in a ComfyUI input folder
        box, px = faces.of(path)
        if not box or px < MIN_FACE_PX:
            skipped += 1
            continue
        wanted.add(name.lower())
        dest = out_dir / name
        if not args.force and is_fresh(path, dest, size):
            continue
        if not args.apply:
            if headshot(path, None, size, box):
                made += 1
            else:
                skipped += 1
                wanted.discard(name.lower())
            continue
        out_dir.mkdir(exist_ok=True)
        try:
            ok = headshot(path, dest, size, box)
        except Exception as e:  # noqa: BLE001
            print(f"  WARNING no headshot for {final}: {e}")
            ok = False
        made += ok
        skipped += not ok
        if not ok:
            wanted.discard(name.lower())
    stale = [p for p in images(out_dir) if p.name.lower() not in wanted]
    for p in stale:
        print(f"  {'PRUNED' if args.apply else 'prune  '} headshot {p.name}  (original gone or no usable face; kept in {archive.name})")
        if args.apply:
            archive.mkdir(parents=True, exist_ok=True)
            if (archive / p.name).exists():
                p.unlink()
            else:
                os.replace(p, archive / p.name)
    if made or stale or skipped:
        print(f"  headshots: {made} {'made' if args.apply else 'to make'}, {skipped} skipped (no usable face), {len(stale)} {'pruned' if args.apply else 'to prune'}")
    tally["headshots"] = tally.get("headshots", 0) + made
    tally["headshots_pruned"] = tally.get("headshots_pruned", 0) + len(stale)


def process_folder(folder, label, size, args, tally):
    gallery, out_dir = folder / "gallery", folder / f"gallery_{size[0]}x{size[1]}"
    prefix = prefix_of(folder.name)
    print(f"----------------------------------------------------------\n>>> {label}   (prefix: {prefix})")
    files = images(gallery)
    taken = {p.name.lower() for p in files}
    # prefixes these files still carry (the folder was renamed, or they came from another one) are swapped like any other folder's
    known = sorted(set(args.known) | folder_prefixes([p.name for p in files], prefix), key=len, reverse=True)
    sources = []
    for p in files:
        new = standard_name(p.name, prefix, known, lambda p=p: content_id(p))
        path, final = p, p.name
        if p.name != new:
            case_only = p.name.lower() == new.lower()
            if new.lower() in taken and not case_only:
                print(f"  WARNING not renamed: {p.name} -> {new} (that name is already used)")
                tally["skipped"] += 1
                continue  # not converted either: a copy without the prefix would only be pruned on the next run
            if args.apply:
                from likeness_library import retained_preparation

                retained = folder / "gallery_intake"
                if retained.exists():
                    retained_preparation.rename_photo(args.work, p, gallery / new)
                elif case_only:
                    hop = p.with_name(p.name + ".rename_tmp")
                    p.rename(hop)
                    hop.rename(gallery / new)
                else:
                    p.rename(gallery / new)
                path = gallery / new
            print(f"  {'RENAMED' if args.apply else 'rename '} {p.name} -> {new}")
            taken.discard(p.name.lower())
            taken.add(new.lower())
            final = new
            tally["renamed"] += 1
        sources.append((path, final))
    ids = {}
    for _, final in sources:
        k = cw.photo_key(final)
        if k:
            ids.setdefault(k, []).append(final)
    for names in ids.values():
        if len(names) > 1:
            print(f"  WARNING the same picture id is in {len(names)} files, probably duplicates (delete one): {', '.join(names)}")

    wanted, made = {}, 0
    for path, final in sources:
        base = re.sub(r"_\d+x\d+$", "", os.path.splitext(final)[0])
        out_name = f"{base}_{size[0]}x{size[1]}.png"
        if out_name.lower() in wanted:
            print(f"  WARNING skipped {final}: another image already makes {out_name}")
            tally["skipped"] += 1
            continue
        wanted[out_name.lower()] = out_name  # kept even if it cannot be read now, so its old copy is not pruned
        dest = out_dir / out_name
        if not args.apply:
            if args.force or not is_fresh(path, dest, size):
                print(f"  convert {final} -> {out_name}")
                made += 1
            continue
        if not args.force and is_fresh(path, dest, size):
            continue
        out_dir.mkdir(exist_ok=True)
        try:
            fit(path, dest, size, args.faces.of(path)[0] if getattr(args, "faces", None) else None)
            made += 1
        except Exception as e:  # noqa: BLE001 - an unreadable image must not stop the rest
            print(f"  WARNING cannot read {final}: {e}")
            tally["skipped"] += 1
    stale = [p for p in images(out_dir) if p.name.lower() not in wanted]
    archive = archive_dir(folder, args.work, f"gallery_{size[0]}x{size[1]}_org")
    for p in stale:
        why = "original gone" if p.name.lower().startswith(prefix + "_") else "old name or another folder"
        print(f"  {'PRUNED' if args.apply else 'prune  '} {p.name}  ({why}; kept in _archive)")
        if args.apply:
            archive.mkdir(parents=True, exist_ok=True)
            if (archive / p.name).exists():
                p.unlink()  # an identical archived copy already exists
            else:
                os.replace(p, archive / p.name)
    print(f"  {made} {'made' if args.apply else 'to make'}, {len(stale)} {'pruned' if args.apply else 'to prune'}")
    tally["made"] += made
    tally["pruned"] += len(stale)
    if getattr(args, "faces", None):
        make_headshots(sources, folder, size, args, tally, args.faces)


def main(argv=None, faces=None, *, configuration=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="really do it (default: preview only)")
    ap.add_argument("--dry-run", action="store_true", help="preview (the bin launcher adds --apply itself)")
    ap.add_argument("--only", action="append", help="a folder name or pattern, e.g. Angelica or 'Drakn*' (repeatable)")
    ap.add_argument("--root", help="the folder that holds Angels, Sisters, Prospects, Artists and Various (default: workspaces.json paths.productionRoot)")
    ap.add_argument("--force", action="store_true", help="make every copy again, even ones newer than their original")
    ap.add_argument("--no-repoint", action="store_true", help="do not re-point chosen photos in workspaces.json and the workflows")
    ap.add_argument("--no-headshots", action="store_true", help="do not make the headshot_944x1104 copies (the face, cropped and scaled up)")
    ap.add_argument("--check", action="store_true", help="preview only, then say IN SYNC or OUT OF SYNC (exit 1): is every gallery's scaled copy and headshot there, and nothing left over? Run it after moving photos about")
    ap.add_argument("--archive-old", action="store_true", help="move the *_org folders already in the library into <work root>/_archive (mirrored paths, with a manifest)")
    ap.add_argument("--undo-archive", action="store_true", help="put the files of the last --archive-old back")
    args = ap.parse_args(argv)
    if configuration is not None and args.apply and not (args.no_repoint or args.dry_run or args.check):
        ap.error("scoped originals requires --no-repoint; refresh selected inputs explicitly")
    args.faces = None if args.no_headshots or args.archive_old or args.undo_archive else (faces or Faces())
    if args.dry_run or args.check:
        args.apply = False
    try:
        import PIL  # noqa: F401
    except ImportError:
        sys.exit("originals needs Pillow:  pip install pillow")
    cfg = configuration if configuration is not None else cw.load_cfg()
    size = tuple(cfg.get("standardSize") or (944, 1104))
    roots = cw.photo_roots(cfg, args.root)
    if not roots:
        sys.exit(f"No photo folders found under {args.root or cw.work_root(cfg)}")
    args.work = pathlib.Path(args.root) if args.root else cw.work_root(cfg)
    if args.archive_old or args.undo_archive:
        (undo_archive if args.undo_archive else lambda w, a: archive_old(w, roots, a))(args.work, args.apply)
        return
    print(f"library: {', '.join(r.name for r in roots)}   size {size[0]}x{size[1]}   " + ("" if args.apply else "(preview; use --apply)"))
    folders = cw.photo_folders(cfg, args.root)
    # every folder's prefix, longest first: an original that still carries another folder's prefix gets this folder's instead
    args.known = sorted({prefix_of(d.name) for _, _, d in folders} | {"various"}, key=len, reverse=True)
    tally = {"renamed": 0, "made": 0, "pruned": 0, "skipped": 0}
    for group, name, folder in folders:
        if args.only and not any(fnmatch.fnmatch(folder.name.lower(), pat.lower()) or fnmatch.fnmatch(name.lower(), pat.lower()) for pat in args.only):
            continue
        process_folder(folder, f"{group}/{name}", size, args, tally)
    if getattr(args, "faces", None):
        args.faces.save()
    print("==========================================================")
    print(f"{tally['renamed']} renamed, {tally['made']} {'made' if args.apply else 'to make'}, {tally['pruned']} {'pruned' if args.apply else 'to prune'}, {tally['skipped']} skipped" + ("" if args.apply else " (preview)")
          + (f", {tally.get('headshots', 0)} headshot(s) {'made' if args.apply else 'to make'}" if args.faces else ""))
    if args.check:
        todo = {"renamed": tally["renamed"], "scaled copies to make": tally["made"], "scaled copies to prune": tally["pruned"], "headshots to make": tally.get("headshots", 0),
                "headshots to prune": tally.get("headshots_pruned", 0)}
        todo = {k: v for k, v in todo.items() if v}
        print("IN SYNC: every gallery has its scaled copy and headshot, and nothing is left over." if not todo
              else "OUT OF SYNC: " + ", ".join(f"{v} {k}" for k, v in todo.items()) + ".  Run bin\\originals.cmd to bring them in step.")
        return 1 if todo else 0
    if args.no_repoint:
        return
    if args.apply:
        cw.reconcile_photos(cw.load_cfg(), dry_run=False, work=args.root)
    else:
        print("With --apply this also re-points any photo you chose in workspaces.json that was renamed (see: inputs photos).")


if __name__ == "__main__":
    sys.exit(main() or 0)
