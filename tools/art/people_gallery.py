#!/usr/bin/env python3
"""A picture gallery of everyone in the photo library: one card per Angel, Sister and Prospect with a headshot and a full-body photo, to survey faces and bodies at a glance.

  python tools/art/people_gallery.py                 write <work>\\_reports\\people_gallery.html (one self-contained file) and people_gallery.md (with a folder of thumbnails)
  python tools/art/people_gallery.py --artists       also the people grouped inside the artists' folders
  python tools/art/people_gallery.py --out DIR       write somewhere else

Which photo stands for a person:
  Angels and Sisters  the photo you chose for her in workspaces.json (marked "chosen"); when there is none, the best guess below.
  Prospects           the best guess: the photo with the most promise as a Prime start. It is a score of this library's own, not a measurement:
                        0.35 how typical it is of her (the face against the centre of her other photos; a lone photo gets 0.5)
                        0.20 how large the face is (the face's size, up to 300 px)
                        0.25 a full-length photo (the whole body is in the picture, so the Prime has less to invent; a frame would be needed otherwise)
                        0.15 how sharp it is, against her sharpest photo
                        0.05 a clean headshot can be cut from it (the face is big enough and clear of a phone's app bars)
                        minus 0.15 for a second face, minus 0.10 for a landscape picture
The headshot is the headshot_944x1104 copy of that photo and the body is its gallery_944x1104 copy, so run bin\\library.cmd (which runs this at the end) after photos move.
"""
import argparse
import base64
import datetime
import html
import io
import pathlib
import re
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflows"))
sys.path.insert(0, str(ROOT / "tools/art"))
import comfy_workflows as cw  # noqa: E402
import likeness  # noqa: E402
import originals  # noqa: E402
import people  # noqa: E402

THUMB = (188, 220)  # the 944x1104 shape at a fifth of the size
SECTIONS = [("Angels", "Angels"), ("Sisters", "Sisters"), ("Prospects", "Prospects"), ("Artists", "Artists' people")]
WEIGHTS = {"typical": 0.35, "size": 0.20, "full": 0.25, "sharp": 0.15, "head": 0.05}


def prime_score(typical, px, full, sharp, head, faces=1, landscape=False):
    """The promise of a photo as a Prime start (see the module doc). Every input is 0..1 except px (the face's size in pixels) and faces (how many)."""
    score = (WEIGHTS["typical"] * typical + WEIGHTS["size"] * min(px, 300) / 300 + WEIGHTS["full"] * (1.0 if full else 0.0)
             + WEIGHTS["sharp"] * sharp + WEIGHTS["head"] * (1.0 if head else 0.0))
    return score - (0.15 if faces > 1 else 0) - (0.10 if landscape else 0)


def sharpness(img):
    """The energy of an image's fine detail (variance of a Laplacian over a small grey copy)."""
    import numpy as np
    from PIL import ImageOps
    g = np.asarray(ImageOps.grayscale(img).resize((236, 276)), dtype=float)
    lap = 4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return float(lap.var())


def copies(folder, stem, size):
    """(headshot path or None, body path or None) of an original, from its scaled copies."""
    w, h = size
    head = folder / f"headshot_{w}x{h}" / f"{stem}_head_{w}x{h}.png"
    body = folder / f"gallery_{w}x{h}" / f"{stem}_{w}x{h}.png"
    return (head if head.exists() else None), (body if body.exists() else None)


def thumb_bytes(path, kind="JPEG"):
    from PIL import Image, ImageOps
    with Image.open(path) as im:
        im = ImageOps.fit(im.convert("RGB"), THUMB, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, kind, quality=82)
    return buf.getvalue()


def face_crop_bytes(photo, size):
    """A headshot-like crop of the scaled copy around the face box, for a photo that has no headshot file."""
    from PIL import Image, ImageOps
    body = copies(photo.path.parent.parent, photo.path.stem, size)[1]
    if not body or not photo.box:
        return None
    with Image.open(body) as im:
        im = im.convert("RGB")
        bx, by, bw, bh = photo.box
        x0, y0, x1, y1 = bx - 0.3 * bw, by - 0.45 * bh, bx + 1.3 * bw, by + 1.35 * bh
        im = im.crop((int(max(x0, 0) * im.width), int(max(y0, 0) * im.height), int(min(x1, 1) * im.width), int(min(y1, 1) * im.height)))
        im = ImageOps.fit(im, THUMB, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    return buf.getvalue()


def inspect(path, box, size):
    """(is the whole body in the picture, is it a landscape picture) of an original. A head under a phone's app bars is not counted as full length."""
    from PIL import Image, ImageOps
    import screens
    try:
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
    except Exception:  # noqa: BLE001
        return False, False
    if not box:
        return False, im.width > im.height
    if screens.is_reel_ui(im) and not screens.head_clear(box):
        return False, im.width > im.height
    return not originals.frame_photo(path, None, size, list(box)), im.width > im.height


def collect(cfg, st, work, space, groups):
    """[{status, folder, key, photos, review, chosen, score, head, body, tags, source}] one per person, in gallery order."""
    size = tuple(cfg.get("standardSize") or (944, 1104))
    chosen = likeness.chosen_keys(cfg)
    people_rows = []
    for key, folder in likeness.library_people(cfg, st, work):
        status = likeness.status_of(key)
        if status not in groups:
            continue
        ps = space.by_key.get(key, [])
        all_originals = originals.images(folder / "gallery")
        row = {"status": status, "folder": key.split("/", 1)[1], "key": key, "photos": len(all_originals), "review": len(originals.images(folder / "review")),
               "chosen": False, "score": None, "head": None, "body": None, "source": "", "tags": people.profile(folder)}
        pick, rest = None, []
        if ps:
            c = space.centroid(key) if len(ps) >= 2 else None
            scored = []
            for p in ps:
                head, body = copies(folder, p.path.stem, size)
                sharp = 0.0
                if body:
                    try:
                        from PIL import Image
                        with Image.open(body) as im:
                            sharp = sharpness(im.convert("RGB"))
                    except Exception:  # noqa: BLE001
                        sharp = 0.0
                scored.append([p, head, body, sharp])
            top = max((s[3] for s in scored), default=0.0) or 1.0
            for s in scored:
                p, head, body, sharp = s
                typical = float(p.vec @ c) if c is not None and p.vec is not None else 0.5
                full = bool(p.box) and not originals.frame_photo(p.path, None, size, list(p.box))
                landscape = False
                try:
                    from PIL import Image
                    with Image.open(p.path) as im:
                        landscape = im.width > im.height
                except Exception:  # noqa: BLE001
                    pass
                s.append(prime_score(max(typical, 0.0), p.px, full, sharp / top, head is not None, p.faces, landscape))
            for s in scored:
                if likeness.cw.photo_key(s[0].name) in chosen:
                    pick = s
                    row["chosen"] = True
            best = max(scored, key=lambda s: s[4])
            pick = pick or best
            row["score"] = pick[4]
            row["head_path"], row["body_path"], row["source"] = pick[1], pick[2], pick[0].name
            if pick[1] is None:
                row["head"] = face_crop_bytes(pick[0], size)
        elif all_originals:
            head, body = copies(folder, all_originals[0].stem, size)
            row["head_path"], row["body_path"], row["source"] = head, body, all_originals[0].name
        for kind, key_name in (("head", "head_path"), ("body", "body_path")):
            path = row.get(key_name)
            if path and row.get(kind) is None:
                row[kind] = thumb_bytes(path)
        people_rows.append(row)
    order = {s: i for i, (s, _t) in enumerate(SECTIONS)}
    people_rows.sort(key=lambda r: (order.get(r["status"], 9), r["folder"].lower()))
    return people_rows


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def caption(r):
    bits = [f"{r['photos']} photo{'s' if r['photos'] != 1 else ''}"]
    if r["review"]:
        bits.append(f"{r['review']} in review")
    bits.append("chosen photo" if r["chosen"] else f"best guess {r['score']:.2f}" if r["score"] is not None else "no usable face")
    tags = r["tags"] or {}
    for k in ("elements", "tier", "type"):
        if tags.get(k):
            bits.append(f"{k}: {', '.join(tags[k])}")
    return bits


def b64(data):
    return "data:image/jpeg;base64," + base64.b64encode(data).decode("ascii")


CSS = """body{font-family:Segoe UI,Arial,sans-serif;margin:24px;background:#faf8f3;color:#222}h1{margin:0 0 4px}h2{margin:32px 0 8px;border-bottom:2px solid #d8cfbf;padding-bottom:4px}
nav a{margin-right:16px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:14px}
.card{background:#fff;border:1px solid #e0d8c8;border-radius:6px;padding:8px;margin:0}.pair{display:flex;gap:6px}.pair img{width:calc(50% - 3px);height:auto;border-radius:3px;background:#eee}
.card b{font-size:1.05em}.meta{color:#666;font-size:.85em;margin-top:4px}.chosen{background:#2e7d32;color:#fff;border-radius:3px;padding:0 5px;font-size:.8em}.status{color:#888;font-size:.8em}
.noimg{display:flex;align-items:center;justify-content:center;width:calc(50% - 3px);aspect-ratio:188/220;background:#eee;color:#999;font-size:.8em}"""


def render_html(rows, stamp, counts):
    out = ["<!doctype html>", '<html lang="en"><head><meta charset="utf-8"><title>People gallery</title>', f"<style>{CSS}</style></head><body>", "<h1>People gallery</h1>",
           f'<p class="meta">Generated {html.escape(stamp)}. Each card: the headshot and the full photo of one person. Angels and Sisters show the photo you chose; for everyone else it is the best guess '
           '(see the notes in <code>tools/art/people_gallery.py</code>). Click the full photo to open it.</p>',
           "<nav>" + " ".join(f'<a href="#{slug(s)}">{html.escape(t)} ({counts.get(s, 0)})</a>' for s, t in SECTIONS if counts.get(s)) + "</nav>"]
    current = None
    for r in rows:
        if r["status"] != current:
            if current:
                out.append("</div>")
            current = r["status"]
            title = dict(SECTIONS)[current]
            out.append(f'<h2 id="{slug(current)}">{html.escape(title)} ({counts[current]})</h2><div class="grid">')
        imgs = []
        for kind in ("head", "body"):
            if r.get(kind):
                img = f'<img src="{b64(r[kind])}" alt="{kind}" title="{html.escape(r["source"])}">'
                if kind == "body" and r.get("body_path"):
                    img = f'<a href="{pathlib.Path(r["body_path"]).resolve().as_uri()}" target="_blank">{img}</a>'
                imgs.append(img)
            else:
                imgs.append(f'<div class="noimg">no {kind}</div>')
        flag = ' <span class="chosen">chosen</span>' if r["chosen"] else ""
        out.append(f'<figure class="card"><div class="pair">{"".join(imgs)}</div><figcaption><b>{html.escape(r["folder"])}</b>{flag} <span class="status">{html.escape(r["status"])}</span>'
                   f'<div class="meta">{html.escape(" · ".join(caption(r)))}</div></figcaption></figure>')
    if current:
        out.append("</div>")
    out.append("</body></html>")
    return "\n".join(out) + "\n"


def render_md(rows, stamp, counts, files_dir, html_name, columns=3):
    """The same gallery as a Markdown table of three people per row; the thumbnails sit in <report>_files next to it."""
    files_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# People gallery", "", f"Generated {stamp}. The same pictures as a self-contained page: [{html_name}]({html_name}). Angels and Sisters show the photo you chose; for everyone else it is the best guess.", ""]
    current, cells = None, []

    def flush():
        nonlocal cells
        if not cells:
            return
        lines.append("| " + " | ".join(["  "] * columns) + " |")
        lines.append("| " + " | ".join(["---"] * columns) + " |")
        for i in range(0, len(cells), columns):
            chunk = cells[i:i + columns] + [""] * (columns - len(cells[i:i + columns]))
            lines.append("| " + " | ".join(chunk) + " |")
        lines.append("")
        cells = []

    for r in rows:
        if r["status"] != current:
            flush()
            current = r["status"]
            lines += [f"## {dict(SECTIONS)[current]} ({counts[current]})", ""]
        parts = []
        for kind in ("head", "body"):
            if r.get(kind):
                name = f"{slug(r['status'])}_{slug(r['folder'])}_{kind[0]}.jpg"
                (files_dir / name).write_bytes(r[kind])
                parts.append(f"![{r['folder']} {kind}]({files_dir.name}/{name})")
        flag = " (chosen)" if r["chosen"] else ""
        cells.append(" ".join(parts) + f"<br>**{r['folder']}**{flag}<br>" + " · ".join(caption(r)))
    flush()
    return "\n".join(lines) + "\n"


def main(argv=None, space=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--artists", action="store_true", help="also the people grouped inside the artists' folders")
    ap.add_argument("--out", help="folder for the report (default: <work>\\_reports)")
    ap.add_argument("--root", help="the photo library folder (default: workspaces.json paths.workRoot)")
    args = ap.parse_args(argv)
    groups = ["Angels", "Sisters", "Prospects"] + (["Artists"] if args.artists else [])
    if space is None:
        cfg, st, work, _cache, space = likeness.build(types.SimpleNamespace(root=args.root, cache=None, embedder=None))
    else:
        cfg, st, work = space.cfg, space.st, space.work
    out = pathlib.Path(args.out) if args.out else work / "_reports"
    out.mkdir(parents=True, exist_ok=True)
    rows = collect(cfg, st, work, space, groups)
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    (out / "people_gallery.html").write_text(render_html(rows, stamp, counts), encoding="utf-8")
    (out / "people_gallery.md").write_text(render_md(rows, stamp, counts, out / "people_gallery_files", "people_gallery.html"), encoding="utf-8")
    size_mb = (out / "people_gallery.html").stat().st_size / 1e6
    print(f"people gallery: {len(rows)} people ({', '.join(f'{v} {k}' for k, v in counts.items())}); chosen photos {sum(r['chosen'] for r in rows)}, best guesses {sum(1 for r in rows if not r['chosen'] and r['score'] is not None)}")
    print(f"  {out / 'people_gallery.html'}  ({size_mb:.1f} MB, one file)\n  {out / 'people_gallery.md'}  (thumbnails in people_gallery_files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
