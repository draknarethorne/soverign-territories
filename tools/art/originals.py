#!/usr/bin/env python3
"""Keep the original-photo library in step with what you drop in it (preview unless --apply).

The library is <work root>/<Root>/<Name>/gallery (your originals) and <Name>/gallery_944x1104 (what this makes), for the roots
Angels, Models, Prospects and Artists (workspaces.json paths.photoRoots). For every <Name> folder that has a gallery:

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
  2. SCALE   each original onto a cream 944x1104 canvas (shape kept, EXIF rotation applied) as <name>_..._944x1104.png.
             A copy that is already newer than its original is left alone (--force makes them all again).
  3. PRUNE   every image in gallery_944x1104 that no original in that folder's gallery makes any more (you deleted or moved the
             original, or it has an old name). They are moved into gallery_944x1104_org, never deleted; other files are never touched.
  4. REPOINT (with --apply) a photo you chose in workspaces.json ("photos") that was renamed or moved is pointed at its new name in
             workspaces.json and in the workflows; the same as `inputs photos`.

The routine: drop or move originals, delete the ones that did not work out, run originals.cmd.

  python tools/art/originals.py                    # preview everything
  python tools/art/originals.py --apply
  python tools/art/originals.py --only Angelica --apply
"""
import argparse
import fnmatch
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflows"))
import comfy_workflows as cw  # noqa: E402

CREAM = (245, 240, 230)
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


def fit(src, dest, size):
    """Scale src to fit inside size (shape kept), centre it on the cream canvas and write a PNG (through a temporary file)."""
    from PIL import Image, ImageOps
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        rgba = im.convert("RGBA")
    w, h = size
    scale = min(w / rgba.width, h / rgba.height)
    nw, nh = max(1, round(rgba.width * scale)), max(1, round(rgba.height * scale))
    small = rgba.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", size, CREAM)
    canvas.paste(small, ((w - nw) // 2, (h - nh) // 2), small)
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
                if case_only:
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
            fit(path, dest, size)
            made += 1
        except Exception as e:  # noqa: BLE001 - an unreadable image must not stop the rest
            print(f"  WARNING cannot read {final}: {e}")
            tally["skipped"] += 1
    stale = [p for p in images(out_dir) if p.name.lower() not in wanted]
    archive = folder / f"gallery_{size[0]}x{size[1]}_org"
    for p in stale:
        why = "original gone" if p.name.lower().startswith(prefix + "_") else "old name or another folder"
        print(f"  {'PRUNED' if args.apply else 'prune  '} {p.name}  ({why}; kept in {archive.name})")
        if args.apply:
            archive.mkdir(exist_ok=True)
            if (archive / p.name).exists():
                p.unlink()  # an identical archived copy already exists
            else:
                os.replace(p, archive / p.name)
    print(f"  {made} {'made' if args.apply else 'to make'}, {len(stale)} {'pruned' if args.apply else 'to prune'}")
    tally["made"] += made
    tally["pruned"] += len(stale)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="really do it (default: preview only)")
    ap.add_argument("--dry-run", action="store_true", help="preview (the bin launcher adds --apply itself)")
    ap.add_argument("--only", action="append", help="a folder name or pattern, e.g. Angelica or 'Drakn*' (repeatable)")
    ap.add_argument("--root", help="the folder that holds Angels, Models, Prospects and Artists (default: workspaces.json paths.workRoot)")
    ap.add_argument("--force", action="store_true", help="make every copy again, even ones newer than their original")
    ap.add_argument("--no-repoint", action="store_true", help="do not re-point chosen photos in workspaces.json and the workflows")
    args = ap.parse_args(argv)
    if args.dry_run:
        args.apply = False
    try:
        import PIL  # noqa: F401
    except ImportError:
        sys.exit("originals needs Pillow:  pip install pillow")
    cfg = cw.load_cfg()
    size = tuple(cfg.get("standardSize") or (944, 1104))
    roots = cw.photo_roots(cfg, args.root)
    if not roots:
        sys.exit(f"No photo folders found under {args.root or cw.work_root(cfg)}")
    print(f"library: {', '.join(r.name for r in roots)}   size {size[0]}x{size[1]}   " + ("" if args.apply else "(preview; use --apply)"))
    # every folder's prefix, longest first: an original that still carries another folder's prefix gets this folder's instead
    args.known = sorted({prefix_of(f.name) for r in roots for f in r.iterdir() if f.is_dir()} | {"various"}, key=len, reverse=True)
    tally = {"renamed": 0, "made": 0, "pruned": 0, "skipped": 0}
    for root in roots:
        for folder in sorted(p for p in root.iterdir() if p.is_dir()):
            if args.only and not any(fnmatch.fnmatch(folder.name.lower(), pat.lower()) for pat in args.only):
                continue
            if (folder / "gallery").is_dir():
                process_folder(folder, f"{root.name}/{folder.name}", size, args, tally)
    print("==========================================================")
    print(f"{tally['renamed']} renamed, {tally['made']} {'made' if args.apply else 'to make'}, {tally['pruned']} {'pruned' if args.apply else 'to prune'}, {tally['skipped']} skipped" + ("" if args.apply else " (preview)"))
    if args.no_repoint:
        return
    if args.apply:
        cw.reconcile_photos(cw.load_cfg(), dry_run=False, work=args.root)
    else:
        print("With --apply this also re-points any photo you chose in workspaces.json that was renamed (see: inputs photos).")


if __name__ == "__main__":
    main()
