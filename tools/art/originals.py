#!/usr/bin/env python3
"""Keep the original-photo library in step with what you drop in it (preview unless --apply).

The library is <work root>/<Root>/<Name>/gallery (your originals) and <Name>/gallery_944x1104 (what this makes), for the roots
Angels, Models, Prospects and Artists (workspaces.json paths.photoRoots). For every <Name> folder that has a gallery:

  1. RENAME  each original after the FOLDER it is in:  <name>_image_<id>.jpg, <name>_screenshot_<date>_<time>.jpg, <name>_<description>.ext.
             Move an original from Prospects/Various/gallery into Angels/Angelica/gallery and it becomes angelica_image_<id>
             (the id never changes). A rename that would overwrite another file is skipped with a warning, never forced.
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
RULES = [
    (re.compile(rf"^facebook_.*_(\d+)\.{EXT}$", re.I), lambda m, p: f"{p}_image_{m[1]}"),
    (re.compile(rf"^Screenshot_(\d{{8}})_(\d{{6}})(?:_.*)?\.{EXT}$", re.I), lambda m, p: f"{p}_screenshot_{m[1]}_{m[2]}"),
    (re.compile(rf"^.*_image_(\d+)\.{EXT}$", re.I), lambda m, p: f"{p}_image_{m[1]}"),
    (re.compile(rf"^.*_screenshot_(\d{{8}}_\d{{6}})\.{EXT}$", re.I), lambda m, p: f"{p}_screenshot_{m[1]}"),
    (re.compile(rf"^(?:Drakn\w+|[a-zA-Z0-9\-]+)\s+(Base|Face.*|Pose.*)\.{EXT}$", re.I), lambda m, p: f"{p}_" + re.sub(r"\s+", "_", m[1].lower().strip())),
]


def prefix_of(folder):
    return re.sub(r"\s+", "_", folder.lower().strip())


def standard_name(name, prefix):
    """The name an original gets in the folder with this prefix."""
    stem, ext = os.path.splitext(name[1:] if name.startswith(".") else name)
    ext = ext.lower()
    ext = ".jpg" if ext == ".jpeg" else ext
    for pattern, build in RULES:
        m = pattern.match(name[1:] if name.startswith(".") else name)
        if m:
            return build(m, prefix) + ext
    if stem.lower().startswith(prefix + "_"):
        return stem + ext
    tail = re.sub(r"\s+", "_", stem.lower().strip())
    return f"{prefix}_{tail}{ext}"


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
    sources = []
    for p in files:
        new = standard_name(p.name, prefix)
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
