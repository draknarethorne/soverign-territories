#!/usr/bin/env python3
"""Compare the faces in the original-photo library, and sort, merge and retire photos by likeness (preview unless --apply).

Faces are found and turned into an identity vector with OpenCV's YuNet and SFace models (two small files, downloaded once to
%LOCALAPPDATA%\\sovereign-territories\\models; nothing leaves your machine). Every photo is cached by its content, so a rename or a move
costs nothing. Scores are COSINE SIMILARITY AFTER SUBTRACTING THE LIBRARY'S AVERAGE FACE: without that every glamour face looks alike to
the model. Read a score as a ranking inside your own library, not as a yes/no:

    about 0.55 and up   the same person (what a folder's own photos score against each other)
    0.30 to 0.45        very alike: you would think they were cousins; do not use both for different heroes
    below 0.15          different people

The library is <work root>/<Root>/<Name>/gallery. A folder of one person (Angels, Models, named Prospects) is a "person" folder;
Artists/* and Prospects/Various hold many people and are "mixed": they are never used to describe a person, and Prospects/Various is the
pool that `sort` empties. Configure under "likeness" in workflows/workspaces.json (mixed, pool, assign, margin, cluster, minCluster, odd, alike, minFace).

  likeness scan                       read every photo once (cached); lists photos with no usable face
  likeness calibrate                  how reliable the scores are on YOUR library (the thresholds in effect)
  likeness alike                      pairs of people who look alike (angel against angel, angel against sister ...), most alike first
  likeness compare Angelica azaline   how alike two folders are, and the photos that match best
  likeness folder Drakness            the photos that look like a different person from the rest of the folder
  likeness like path\\to\\photo.jpg      which folders a new photo looks like
  likeness sort                       Prospects/Various: photos that match an existing person move there, clusters of one new person
                                      go to a new Prospects/<invented name> folder; the rest stay
  likeness merge Mia "Eva Emily"      move every photo of one folder into another (one person under two names)
  likeness retire azaline             move a folder's photos back to Prospects/Various so she can be cast again
  likeness undo                       put the last batch of moves back

Every command that moves files previews first; add --apply to do it (the bin launcher does not add it for you: moving photos is the one
thing worth a second look). After moving, the originals tool renames, scales, prunes and re-points as usual. Add --sheet FILE to any
command to save a picture of the faces involved. Photos chosen in workspaces.json are never moved by `sort` and are flagged by merge and retire.
"""
import argparse
import collections
import datetime
import fnmatch
import hashlib
import itertools
import json
import os
import pathlib
import random
import re
import shutil
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflows"))
sys.path.insert(0, str(ROOT / "tools/art"))
import comfy_workflows as cw  # noqa: E402
import originals  # noqa: E402

DATA = pathlib.Path(os.environ.get("LOCALAPPDATA") or (pathlib.Path.home() / ".cache")) / "sovereign-territories"
MODEL_URLS = {
    "face_detection_yunet_2023mar.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "face_recognition_sface_2021dec.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx",
}
SETTINGS = {"mixed": ["Artists/*", "Prospects/Various"], "pool": ["Prospects/Various"], "assign": 0.45, "margin": 0.10, "cluster": 0.25,
            "minCluster": 3, "odd": 0.15, "alike": 0.30, "minFace": 60}
FIRST = ["Alina", "Bea", "Calla", "Dara", "Elise", "Faye", "Gia", "Hana", "Ivy", "Jade", "Kira", "Lena", "Maren", "Nia", "Odette", "Paige", "Quinn", "Rhea",
         "Sabine", "Tessa", "Una", "Vera", "Wren", "Xena", "Yara", "Zoe", "Anya", "Brynn", "Cleo", "Delia", "Esme", "Freya", "Greta", "Hollis", "Iris", "Jules",
         "Keira", "Lia", "Mara", "Neve", "Opal", "Petra", "Rina", "Sia", "Tove", "Uma", "Vienna", "Willa", "Yvette", "Zara"]
LAST = ["Ashby", "Brandt", "Calder", "Dale", "Ellery", "Fenn", "Gray", "Hale", "Ingram", "Jasper", "Keene", "Locke", "Marsh", "Nash", "Orr", "Pryce", "Quill",
        "Rowe", "Sloane", "Thorn", "Vale", "Wilde", "Yates", "Zane", "Ames", "Blythe", "Crane", "Drake", "Eden", "Frost", "Glenn", "Hart", "Ives", "Joyce",
        "Knox", "Lane", "Moss", "North", "Ogden", "Park", "Reyes", "Stone", "Tate", "Voss", "West", "Ford", "Beck", "Cole", "Dunn", "Lowe"]


# ---------- faces ----------

class Embedder:
    """Finds the main face in a picture and returns its identity vector (loads the models on first use, downloading them once)."""

    def __init__(self):
        self.det = self.rec = None

    def load(self):
        import cv2
        DATA.joinpath("models").mkdir(parents=True, exist_ok=True)
        for name, url in MODEL_URLS.items():
            path = DATA / "models" / name
            if not path.exists():
                import urllib.request
                print(f"downloading {name} ...")
                urllib.request.urlretrieve(url, path)
        self.det = cv2.FaceDetectorYN.create(str(DATA / "models" / "face_detection_yunet_2023mar.onnx"), "", (320, 320), 0.7, 0.3, 5000)
        self.rec = cv2.FaceRecognizerSF.create(str(DATA / "models" / "face_recognition_sface_2021dec.onnx"), "")

    def __call__(self, path):
        import cv2
        if self.det is None:
            self.load()
        img = cv2.imdecode(np.fromfile(str(path), np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return None
        h, w = img.shape[:2]
        scale = 1600 / max(h, w) if max(h, w) > 1600 else 1.0
        small = cv2.resize(img, (int(w * scale), int(h * scale))) if scale != 1.0 else img
        sh, sw = small.shape[:2]
        self.det.setInputSize((sw, sh))
        _, faces = self.det.detect(small)
        if faces is None or len(faces) == 0:
            return {"faces": 0}
        face = max(faces, key=lambda f: f[2] * f[3])
        vec = self.rec.feature(self.rec.alignCrop(small, face))[0]
        vec = vec / np.linalg.norm(vec)
        return {"faces": int(len(faces)), "v": [round(float(x), 5) for x in vec], "box": [round(float(face[0]) / sw, 4), round(float(face[1]) / sh, 4), round(float(face[2]) / sw, 4), round(float(face[3]) / sh, 4)],
                "px": int(min(face[2], face[3]) / scale)}


class Cache:
    """{sha1 of the file's bytes: face data}, plus a memo of (size, mtime) -> sha1 so unchanged files are not read again."""

    def __init__(self, path):
        self.path = pathlib.Path(path)
        data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}
        self.stat, self.emb = data.get("stat", {}), data.get("emb", {})

    def sha(self, p):
        st = p.stat()
        key = str(p)
        hit = self.stat.get(key)
        if hit and hit[0] == st.st_size and hit[1] == st.st_mtime_ns:
            return hit[2]
        sha = hashlib.sha1(p.read_bytes()).hexdigest()
        self.stat[key] = [st.st_size, st.st_mtime_ns, sha]
        return sha

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"stat": self.stat, "emb": self.emb}), encoding="utf-8")


class Photo:
    def __init__(self, path, group, folder, sha, data):
        self.path, self.group, self.folder, self.sha = path, group, folder, sha
        self.key = f"{group}/{folder}"
        self.faces = (data or {}).get("faces", -1)
        self.raw = np.array(data["v"], float) if data and data.get("v") else None
        self.box = (data or {}).get("box")
        self.px = (data or {}).get("px", 0)
        self.name = path.name
        self.vec = None  # centred, set by Space

    def usable(self, min_face):
        return self.raw is not None and self.px >= min_face


def settings(cfg):
    out = dict(SETTINGS)
    out.update(cfg.get("likeness", {}))
    return out


def matches(key, patterns):
    """Does a folder key like 'Artists/Pierre' match a pattern like 'Artists/*'? A star stands for one folder name, so 'Artists/*' is the artist folders and not the people grouped inside them."""
    parts = key.lower().split("/")
    for p in patterns:
        pp = p.lower().split("/")
        if len(pp) == len(parts) and all(fnmatch.fnmatch(a, b) for a, b in zip(parts, pp)):
            return True
    return False


def read_library(cfg, work, cache, embed, st, progress=True, with_mixed=False):
    """Every original in the person folders and the pool. The other mixed folders (many people, never used to describe one) are skipped unless with_mixed."""
    photos, todo = [], []
    for group, name, folder in cw.photo_folders(cfg, work):
        key = f"{group}/{name}"
        if matches(key, st["mixed"]) and not matches(key, st["pool"]) and not with_mixed:
            continue
        for p in originals.images(folder / "gallery"):
            todo.append((p, group, name))
    done = 0
    for p, group, folder in todo:
        sha = cache.sha(p)
        if sha not in cache.emb:
            try:
                cache.emb[sha] = embed(p) or {"faces": -1}
            except Exception as e:  # noqa: BLE001 - one bad file must not stop the scan
                print(f"  cannot read {p.name}: {e}")
                cache.emb[sha] = {"faces": -1}
            done += 1
            if progress and done % 25 == 0:
                print(f"  ... {done} new photo(s) read")
                cache.save()
        photos.append(Photo(p, group, folder, sha, cache.emb[sha]))
    if done:
        cache.save()
    return photos


# ---------- the space ----------

def nz(a):
    n = np.linalg.norm(a, axis=-1, keepdims=True)
    return a / np.where(n == 0, 1, n)


class Space:
    """Centred identity vectors for the person folders: centroids per folder, scores of a photo against them."""

    def __init__(self, photos, st):
        self.st = st
        self.photos = photos
        self.pool_keys = set()
        person = [p for p in photos if p.usable(st["minFace"]) and not matches(p.key, st["mixed"])]
        self.person = person
        self.mean = np.mean([p.raw for p in person], axis=0) if person else np.zeros(128)
        for p in photos:
            if p.raw is not None:
                p.vec = nz(p.raw - self.mean)
        self.by_key = collections.defaultdict(list)
        for p in person:
            self.by_key[p.key].append(p)
        self.keys = sorted(self.by_key)

    def centroid(self, key, skip=None):
        vs = [p.vec for p in self.by_key.get(key, []) if p is not skip]
        return nz(np.mean(vs, axis=0)) if vs else None

    def ranking(self, vec, skip=None, own=None):
        """[(score, key)] best first: the vector against every person folder's centroid (a photo that is in its own folder is left out of that centroid)."""
        out = []
        for k in self.keys:
            c = self.centroid(k, skip=skip if k == own else None)
            if c is not None:
                out.append((float(vec @ c), k))
        return sorted(out, reverse=True)

    def pair_matrix(self):
        cents = {k: self.centroid(k) for k in self.keys}
        return cents, {(a, b): float(cents[a] @ cents[b]) for a, b in itertools.combinations(self.keys, 2)}


def cluster(vecs, threshold):
    """Average-linkage clusters of the rows of vecs (cosine): indices lists, most alike merged first until the best link falls below threshold."""
    n = len(vecs)
    sim = vecs @ vecs.T
    groups = [[i] for i in range(n)]
    while len(groups) > 1:
        best, bi, bj = -2, 0, 0
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                s = float(np.mean(sim[np.ix_(groups[i], groups[j])]))
                if s > best:
                    best, bi, bj = s, i, j
        if best < threshold:
            break
        groups[bi] += groups[bj]
        del groups[bj]
    return groups


def invent_name(seed, taken):
    """A made-up first and last name, the same for the same seed, that no existing folder (or its prefix) already uses."""
    h = int(hashlib.sha1(seed.encode()).hexdigest(), 16)
    used = {originals.prefix_of(t) for t in taken}
    for i in range(len(FIRST) * len(LAST)):
        n = (h + i * 7919) % (len(FIRST) * len(LAST))
        name = f"{FIRST[n % len(FIRST)]} {LAST[(n // len(FIRST)) % len(LAST)]}"
        if originals.prefix_of(name) not in used:
            return name
    return f"Prospect {h % 10000}"


# ---------- plans ----------

class Move:
    def __init__(self, photo, to, reason, score=None, bucket="gallery"):
        self.photo, self.to, self.reason, self.score, self.bucket = photo, to, reason, score, bucket

    def as_dict(self):
        return {"file": str(self.photo.path), "to": self.to, "bucket": self.bucket, "reason": self.reason, "score": None if self.score is None else round(self.score, 3)}


def chosen_keys(cfg):
    return {cw.photo_key(n) for n in cfg.get("photos", {}).values() if cw.photo_key(n)}


def plan_sort(space, st, cfg, taken, singles=False):
    """Moves for the pool photos: to the person folder they match confidently, or into a new folder when several look like one new person.
    With singles, a photo that matches nobody and has no look-alike in the pool gets a new folder of its own, so the pool is left holding only photos with no usable face."""
    pool = [p for p in space.photos if matches(p.key, st["pool"]) and p.usable(st["minFace"])]
    protected = chosen_keys(cfg)
    moves, left = [], []
    for p in pool:
        if cw.photo_key(p.name) in protected:
            continue
        rank = space.ranking(p.vec)
        if rank and rank[0][0] >= st["assign"] and (len(rank) < 2 or rank[0][0] - rank[1][0] >= st["margin"]):
            moves.append(Move(p, rank[0][1], f"looks like {rank[0][1]} ({rank[0][0]:.2f}; next {rank[1][0]:.2f})" if len(rank) > 1 else f"looks like {rank[0][1]}", rank[0][0]))
        else:
            left.append(p)
    if left:
        vecs = np.array([p.vec for p in left])
        for g in cluster(vecs, st["cluster"]):
            if len(g) >= st["minCluster"] or singles:
                members = [left[i] for i in g]
                name = invent_name("|".join(sorted(m.sha for m in members)), taken | {m.to.split("/", 1)[-1] for m in moves})
                new = f"Prospects/{name}"
                taken = taken | {name}
                near = space.ranking(nz(np.mean([m.vec for m in members], axis=0)))
                note = f"; alike {near[0][1]} ({near[0][0]:.2f})" if near and near[0][0] >= st["alike"] else ""
                what = f"one new person ({len(members)} photos{note})" if len(members) >= st["minCluster"] else f"a face that matches nobody{note}"
                for m in members:
                    moves.append(Move(m, new, what, None))
    return moves


def execute(moves, work, apply, cache, log=True):
    """Move the files into <to>/<bucket> (gallery, or review for photos to look at; a duplicate of what is already there goes to the source folder's gallery_org, a different file with the same name is kept under a new one)."""
    batch = {"id": datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), "moves": []}
    made = 0
    for m in moves:
        src = m.photo.path
        dest_dir = pathlib.Path(work) / m.to / m.bucket
        dst = dest_dir / src.name
        if dst == src:
            continue
        if apply:
            dest_dir.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                if cache.sha(dst) == m.photo.sha:
                    keep = src.parent.parent / "gallery_org"
                    keep.mkdir(exist_ok=True)
                    shutil.move(str(src), str(keep / src.name))
                    print(f"  duplicate already in {m.to}: {src.name} set aside in {keep.name}")
                    continue
                dst = dest_dir / f"{src.stem}_{m.photo.sha[:6]}{src.suffix}"
            shutil.move(str(src), str(dst))
            batch["moves"].append({"from": str(src), "to": str(dst), "sha": m.photo.sha})
        made += 1
    if apply and log and batch["moves"]:
        path = DATA / "likeness_moves.json"
        old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        DATA.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(old + [batch], indent=1), encoding="utf-8")
    return made


def print_plan(moves, space, work=None):
    by = collections.defaultdict(list)
    for m in moves:
        by[(m.to, m.bucket)].append(m)
    for (to, bucket), ms in sorted(by.items()):
        new = to not in space.by_key and not (work and (pathlib.Path(work) / to).is_dir())
        print(f"  -> {to}{'/review' if bucket == 'review' else ''}{'  (NEW folder)' if new else ''}: {len(ms)} photo(s)")
        for m in ms:
            print(f"       {m.photo.key}/{m.photo.name}   {m.reason}")


def after_moves(args, applied):
    if applied and not args.no_originals:
        print("\nrunning originals (rename, scale, prune, re-point) ...")
        originals.main(["--apply"] + (["--root", args.root] if args.root else []))


# ---------- sheet ----------

def make_sheet(rows, out, size=(112, 140)):
    """rows: [(label, [Photo])] -> a PNG of the faces, one labelled row per entry."""
    from PIL import Image, ImageDraw, ImageOps
    per = 10
    lines = [(lab, ps[i:i + per]) for lab, ps in rows for i in range(0, max(len(ps), 1), per)]
    W, H = size
    sheet = Image.new("RGB", (160 + W * per, (H + 18) * len(lines)), (250, 250, 250))
    d = ImageDraw.Draw(sheet)
    for r, (lab, ps) in enumerate(lines):
        y = r * (H + 18)
        d.text((6, y + H // 2 - 6), lab[:24], fill=(0, 0, 0))
        for c, p in enumerate(ps):
            try:
                im = ImageOps.exif_transpose(Image.open(p.path)).convert("RGB")
                if p.box:
                    bx, by, bw, bh = p.box
                    x0, y0, x1, y1 = bx - 0.3 * bw, by - 0.45 * bh, bx + 1.3 * bw, by + 1.35 * bh
                    im = im.crop((int(max(x0, 0) * im.width), int(max(y0, 0) * im.height), int(min(x1, 1) * im.width), int(min(y1, 1) * im.height)))
                sheet.paste(ImageOps.fit(im, size), (160 + c * W, y))
                d.text((160 + c * W + 2, y + H + 2), p.name[-18:], fill=(90, 90, 90))
            except Exception:  # noqa: BLE001
                pass
    sheet.save(out)
    print(f"sheet saved: {out}")


# ---------- commands ----------

def build(args, with_mixed=False):
    cfg = cw.load_cfg()
    st = settings(cfg)
    work = pathlib.Path(args.root) if args.root else cw.work_root(cfg)
    cache = Cache(args.cache or DATA / "likeness_cache.json")
    embed = args.embedder or Embedder()
    photos = read_library(cfg, work, cache, embed, st, with_mixed=with_mixed)
    return cfg, st, work, cache, Space(photos, st)


def folder_key(space, name):
    n = name.lower()
    hits = [k for k in space.keys if k.lower() == n or k.split("/", 1)[1].lower() == n]
    if not hits:
        hits = [k for k in space.keys if k.split("/")[-1].lower() == n]
    if len(hits) != 1:
        sys.exit(f"'{name}' matches {hits or 'no person folder'}; known: {', '.join(k.split('/', 1)[1] for k in space.keys)}")
    return hits[0]


def cmd_scan(args):
    cfg, st, work, cache, space = build(args)
    bad = [p for p in space.photos if not p.usable(st["minFace"])]
    print(f"{len(space.photos)} photo(s) in {len(space.keys)} person folder(s) and the pool; {len(space.person)} usable")
    for p in bad:
        why = "no face found" if p.faces == 0 else "unreadable" if p.faces < 0 else f"face too small ({p.px}px)"
        print(f"  not usable: {p.key}/{p.name}  ({why})")


def cmd_calibrate(args):
    cfg, st, work, cache, space = build(args)
    right = wrong = total = ok = 0
    own, oth = [], []
    for k in space.keys:
        ps = space.by_key[k]
        if len(ps) < 2:
            continue
        for p in ps:
            rank = space.ranking(p.vec, skip=p, own=k)
            mine = next(s for s, key in rank if key == k)
            best_other = next((s, key) for s, key in rank if key != k)
            own.append(mine)
            oth.append(best_other[0])
            total += 1
            ok += mine > best_other[0]
            if mine >= st["assign"] and mine - best_other[0] >= st["margin"]:
                right += 1
            if best_other[0] >= st["assign"] and best_other[0] - mine >= st["margin"]:
                wrong += 1
    print(f"{len(space.person)} photos in {len(space.keys)} person folders; leave-one-out against folders with 2 or more photos ({total} photos):")
    print(f"  the right folder is the best match: {ok}/{total} = {ok / total:.0%}")
    print(f"  own folder score  p10 {np.percentile(own, 10):.2f}  median {np.median(own):.2f}  p90 {np.percentile(own, 90):.2f}")
    print(f"  best other folder p10 {np.percentile(oth, 10):.2f}  median {np.median(oth):.2f}  p90 {np.percentile(oth, 90):.2f}")
    print(f"  with assign >= {st['assign']} and margin >= {st['margin']} (what `sort` moves on its own): {right} confidently right, {wrong} confidently wrong")
    _, pairs = space.pair_matrix()
    v = np.array(list(pairs.values()))
    print(f"folder against folder (different people), {len(v)} pairs: median {np.median(v):.2f}  p90 {np.percentile(v, 90):.2f}  p95 {np.percentile(v, 95):.2f}  max {v.max():.2f}   alike >= {st['alike']}")
    same, diff = [], []
    for k in space.keys:
        ps = space.by_key[k]
        same += [float(a.vec @ b.vec) for a, b in itertools.combinations(ps, 2)]
    ks = space.keys
    for a, b in itertools.combinations(ks, 2):
        diff += [float(x.vec @ y.vec) for x in space.by_key[a][:4] for y in space.by_key[b][:4]]
    print(f"photo against photo: same folder median {np.median(same):.2f} (p10 {np.percentile(same, 10):.2f}); different folders median {np.median(diff):.2f} (p90 {np.percentile(diff, 90):.2f}, p99 {np.percentile(diff, 99):.2f}); cluster >= {st['cluster']}")


def cmd_alike(args):
    cfg, st, work, cache, space = build(args)
    cents, pairs = space.pair_matrix()
    v = np.array(list(pairs.values()))
    rows = sorted(((s, a, b) for (a, b), s in pairs.items() if s >= (args.min if args.min is not None else st["alike"])), reverse=True)
    print(f"{len(rows)} pair(s) at or above {args.min if args.min is not None else st['alike']} (median pair {np.median(v):.2f}, p95 {np.percentile(v, 95):.2f}):")
    for s, a, b in rows:
        ga, gb = a.split("/")[0], b.split("/")[0]
        note = ""
        if {ga, gb} == {"Angels", "Models"}:
            angel, sister = (a, b) if ga == "Angels" else (b, a)
            mine = PAIRS.get(angel.split("/")[-1].capitalize()) or PAIRS.get(angel.split("/")[-1])
            note = "  <- her own sister: the intended pair" if mine and mine.lower() == sister.split("/")[-1].lower() else "  <- an angel who resembles a DIFFERENT sister"
        elif ga == gb == "Angels":
            note = "  <- two angels"
        print(f"  {s:.2f}  {a}  ~  {b}  (percentile {np.mean(v <= s):.0%}){note}")
    chosen_heroes = {h.lower() for h in cfg.get("photos", {})}
    thr = args.min if args.min is not None else st["alike"]
    keys = space.keys
    fams = [sorted(keys[i] for i in g) for g in cluster(np.array([cents[k] for k in keys]), thr) if len(g) > 1]
    if fams:
        print(f"\nlook-alike families (everyone alike on average at {thr}); keep one per family and retire the rest with: likeness retire NAME")
        for g in sorted(fams, key=len, reverse=True):
            print("  " + "  ~  ".join(f"{k} ({len(space.by_key[k])}{', has a chosen photo' if k.split('/', 1)[1].lower() in chosen_heroes else ''})" for k in g))
    if args.sheet:
        make_sheet([(k.split("/", 1)[1], space.by_key[k][:10]) for g in fams for k in g], args.sheet)


def cmd_compare(args):
    cfg, st, work, cache, space = build(args)
    a, b = folder_key(space, args.a), folder_key(space, args.b)
    _, pairs = space.pair_matrix()
    v = np.array(list(pairs.values()))
    s = pairs.get((a, b)) if (a, b) in pairs else pairs.get((b, a))
    verdict = "the same person" if s >= 0.55 else "very alike" if s >= st["alike"] else "different people" if s < st["odd"] else "somewhat alike"
    print(f"{a}  vs  {b}: {s:.2f}   ({verdict}; more alike than {np.mean(v <= s):.0%} of all pairs)")
    xs = sorted(((float(x.vec @ y.vec), x, y) for x in space.by_key[a] for y in space.by_key[b]), key=lambda t: -t[0])[:5]
    for sc, x, y in xs:
        print(f"    {sc:.2f}  {x.name}  ~  {y.name}")
    if args.sheet:
        make_sheet([(a.split("/", 1)[1], space.by_key[a][:10]), (b.split("/", 1)[1], space.by_key[b][:10])], args.sheet)


def cmd_folder(args):
    cfg, st, work, cache, space = build(args)
    key = folder_key(space, args.name)
    ps = space.by_key[key]
    if len(ps) < 3:
        sys.exit(f"{key} has {len(ps)} usable photo(s); need 3 or more to say whether they are one person")
    scored = sorted(((float(p.vec @ space.centroid(key, skip=p)), p) for p in ps), key=lambda t: t[0])
    odd = [(s, p) for s, p in scored if s < st["odd"]]
    mid = [(s, p) for s, p in scored if st["odd"] <= s < 0.25]
    good = len(scored) - len(odd) - len(mid)
    agree = good / len(scored)
    one = agree >= 0.9 and len(odd) <= max(1, len(scored) // 20)
    print(f"{key}: {len(ps)} usable photos (each scored against the rest of the folder; {st['odd']} and up is the same person as the rest, 0.25+ is solid)")
    print(f"  {good} agree, {len(mid)} borderline ({st['odd']} to 0.25), {len(odd)} look like someone else (below {st['odd']})")
    print("  VERDICT: " + ("one person." if one else "probably more than one person: see the photos below." if len(odd) > len(scored) // 10 else "mostly one person, a few photos to check."))
    other_of = lambda p, s: next((r for r in space.ranking(p.vec, skip=p, own=key) if r[1] != key), None)  # noqa: E731
    shown = scored if args.all else odd + mid
    if shown:
        print("\n  photos to check (lowest first):")
        for s, p in shown:
            o = other_of(p, s)
            note = f"  [{p.faces} faces in the picture]" if p.faces > 1 else ""
            if s < st["odd"]:
                dest = o[1] if o and o[0] >= st["assign"] else "Prospects/Various (holding)"
                where = f"suggest -> {dest}"
            else:
                where = "keep for now" if s >= st["odd"] else ""
            print(f"    {s:5.2f}  {p.name}   closest elsewhere: {o[1] if o else '-'} {o[0] if o else 0:.2f}   {where}{note}")
    outside = []
    if one or args.outside:
        cen = space.centroid(key)
        rows = sorted(((float(p.vec @ cen), p) for p in space.photos if p.key != key and p.vec is not None and p.usable(st["minFace"])), key=lambda t: -t[0])
        outside = rows[:8]
        best = rows[0][0] if rows else 0
        print(f"\n  who else in the library looks like {key.split('/', 1)[1]} (a photo of her would score 0.45 or more):")
        print("    " + ("nobody clearly: the closest is " + f"{best:.2f}" if best < st["assign"] else "these may be her:"))
        for s, p in outside:
            print(f"    {s:5.2f}  {p.key}/{p.name}")
    if args.sheet:
        rows = [(key.split("/", 1)[1], ps[:10])] + [(f"{s:.2f} low", [p]) for s, p in odd + mid[:6]] + [(f"{s:.2f} {p.key.split('/')[1][:11]}", [p]) for s, p in outside[:6]]
        make_sheet(rows, args.sheet)
    moves = []
    for s, p in odd:
        o = other_of(p, s)
        moves.append(Move(p, o[1] if o and o[0] >= st["assign"] else "Prospects/Various", f"looks like someone else than the rest of {key} ({s:.2f})"))
    if moves:
        print(f"\n  would move the {len(moves)} that look like someone else (the borderline ones stay):")
        print_plan(moves, space, work)
        if args.apply:
            execute(moves, work, True, cache)
            after_moves(args, True)
        else:
            print("  preview only; add --apply to move them")


def cmd_like(args):
    cfg, st, work, cache, space = build(args)
    embed = args.embedder or Embedder()
    for path in args.paths:
        data = embed(pathlib.Path(path))
        if not data or not data.get("v"):
            print(f"{path}: no face found")
            continue
        vec = nz(np.array(data["v"]) - space.mean)
        print(f"{path}:")
        for s, k in space.ranking(vec)[:6]:
            print(f"    {s:.2f}  {k}")


def cmd_sort(args):
    cfg, st, work, cache, space = build(args)
    taken = {name.split("/")[-1] for _, name, _ in cw.photo_folders(cfg, work)}
    moves = plan_sort(space, st, cfg, taken, singles=args.singles)
    pool = [p for p in space.photos if matches(p.key, st["pool"])]
    print(f"{len(pool)} photo(s) in the pool; {len(moves)} would move (assign >= {st['assign']} with a margin of {st['margin']}, or a new person of {st['minCluster']}+ photos at {st['cluster']}):")
    print_plan(moves, space, work)
    if args.sheet:
        rows = []
        for to in sorted({m.to for m in moves}):
            rows.append((f"-> {to.split('/', 1)[-1]}", [m.photo for m in moves if m.to == to]))
            if to in space.by_key:
                rows.append((f"   is {to.split('/', 1)[-1]}", space.by_key[to][:10]))
        make_sheet(rows, args.sheet)
    if not moves:
        return
    if args.plan:
        pathlib.Path(args.plan).write_text(json.dumps([m.as_dict() for m in moves], indent=1), encoding="utf-8")
        print(f"plan written: {args.plan}")
    if args.apply:
        n = execute(moves, work, True, cache)
        print(f"{n} photo(s) moved")
        after_moves(args, n > 0)
    else:
        print("preview only; add --apply to move them")


def whole_folder(space, cfg, name):
    key = folder_key(space, name)
    return key, [p for p in space.photos if p.key == key]


def cmd_merge(args, retire=False):
    cfg, st, work, cache, space = build(args)
    src, photos = whole_folder(space, cfg, args.a if not retire else args.name)
    to = "Prospects/Various" if retire else folder_key(space, args.b)
    if to == src:
        sys.exit("source and destination are the same folder")
    chosen = chosen_keys(cfg)
    hero_hit = [p.name for p in photos if cw.photo_key(p.name) in chosen]
    moves = [Move(p, to, f"{'retired' if retire else 'merged'} from {src}") for p in photos]
    print(f"{src} -> {to}: {len(moves)} photo(s)")
    for h in hero_hit:
        print(f"  NOTE {h} is a photo chosen in workspaces.json; after the move run: inputs photos (it will say where it went), then choose another with inputs set")
    if args.sheet:
        make_sheet([(src.split("/", 1)[1], photos[:10])], args.sheet)
    if args.apply:
        n = execute(moves, work, True, cache)
        print(f"{n} photo(s) moved")
        after_moves(args, n > 0)
    else:
        print("preview only; add --apply to move them")


def cmd_undo(args):
    path = DATA / "likeness_moves.json"
    log = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    batch = next((b for b in reversed(log) if not b.get("undone")), None)
    if not batch:
        sys.exit("nothing to undo")
    cfg = cw.load_cfg()
    work = pathlib.Path(args.root) if args.root else cw.work_root(cfg)
    cache = Cache(args.cache or DATA / "likeness_cache.json")
    print(f"batch {batch['id']}: {len(batch['moves'])} move(s) " + ("being undone" if args.apply else "would be undone (preview; add --apply)"))
    back = 0
    for m in batch["moves"]:
        dest = pathlib.Path(m["to"]).parent
        found = next((p for p in originals.images(dest) if cache.sha(p) == m["sha"]), None)
        src = pathlib.Path(m["from"])
        if not found:
            print(f"  not found any more: {src.name}")
            continue
        print(f"  {found.parent.parent.name}/{found.name} -> {src.parent.parent.name}/{src.name}")
        if args.apply:
            src.parent.mkdir(parents=True, exist_ok=True)
            target = src if not src.exists() else src.with_name(f"{src.stem}_{m['sha'][:6]}{src.suffix}")
            shutil.move(str(found), str(target))
        back += 1
    if args.apply:
        batch["undone"] = True
        path.write_text(json.dumps(log, indent=1), encoding="utf-8")
        cache.save()
        after_moves(args, back > 0)


# ---------- renders, identities, cleaning, grouping, pairing ----------

# each angel and the Drakn sister of her element (the codex's pairs); Angelica is the Neutral herald and has no sister
PAIRS = {"Seraphine": "Drakniss", "Ravaelle": "Draknisa", "Haniya": "Drakniya", "Gavrielle": "Draknava", "Sandalyn": "Draknara",
         "Remiah": "Drakneta", "Azaline": "Draknira", "Camaris": "Draknora", "Sammara": "Draknoxa", "Nyxene": "Drakness"}
FIXED_ANGELS = ["Angelica"]
SAME_LOOK = 0.35  # a render and a photo of the same person score at least this


def core_scores(vecs, seed=None, first=0.2, thr=0.3, rounds=3):
    """(scores, core indices, core centroid): each row of vecs scored against the centroid of the rows that belong together (a photo is left out of its own centroid).
    The core starts from seed (a chosen photo, say) or the folder's average and is refined a few times, so a few photos of other people cannot drag it away."""
    vecs = np.asarray(vecs)
    c = nz(seed) if seed is not None else nz(vecs.mean(0))
    core = list(range(len(vecs)))
    for r in range(rounds):
        sc = vecs @ c
        core = [i for i, s in enumerate(sc) if s >= (first if seed is not None and r == 0 else thr)] or core
        c = nz(vecs[core].mean(0))
    total = vecs[core].sum(0)
    inside = set(core)
    scores = [float(v @ nz(total - v if i in inside and len(core) > 1 else total)) for i, v in enumerate(vecs)]
    return scores, core, c


class Renders:
    """The pictures ComfyUI made, whose faces say which look you chose: the sisters' old X_Pose renders and the renders you saved as candidates for the angels."""

    def __init__(self, cfg, cache, embed, st, space, limit=40):
        self.cfg, self.cache, self.embed, self.st, self.space, self.limit, self.memo = cfg, cache, embed, st, space, limit, {}
        self.files = {}
        roots = []
        try:
            roots.append(cw.output_root(cfg))
            roots.append(pathlib.Path(cfg.get("sharedOutput", "")))
        except (KeyError, TypeError):
            pass
        for r in roots:
            if r and r.is_dir():
                for f in r.rglob("*.png"):
                    self.files.setdefault(f.name, f)

    def sister_files(self, hero):
        pre = (f"{hero}_Qwen_X_Pose_", f"{hero}_Qwen_Alpha_1_Prime_")
        return sorted(f for n, f in self.files.items() if n.startswith(pre))

    def angel_files(self, hero):
        d = cw.WF / "_candidates" / "angel-primes" / hero
        names = {p.stem + ".png" for p in d.rglob("*.json")} if d.is_dir() else set()
        return sorted(self.files[n] for n in names if n in self.files)

    def centroid(self, hero, kind):
        """(centroid of the faces in that hero's renders, how many), or None. Centred like the photos, so it can be set against them."""
        got = self._load(hero, kind)
        return got and (got[0], got[1])

    def _load(self, hero, kind):
        key = (hero.lower(), kind)
        if key not in self.memo:
            files = self.sister_files(hero) if kind == "sister" else self.angel_files(hero)
            if len(files) > self.limit:
                files = [files[i] for i in np.linspace(0, len(files) - 1, self.limit).astype(int)]
            raws, added = [], False
            for f in files:
                sha = self.cache.sha(f)
                if sha not in self.cache.emb:
                    self.cache.emb[sha] = self.embed(f) or {"faces": -1}
                    added = True
                d = self.cache.emb[sha]
                if d.get("v") and d.get("px", 0) >= self.st["minFace"]:
                    raws.append(np.array(d["v"]))
            if added:
                self.cache.save()
            self.memo[key] = None
            if raws:
                vs = np.array([nz(r - self.space.mean) for r in raws])
                _, core, c = core_scores(vs)
                self.memo[key] = (c, len(core), np.array(raws), core)
        return self.memo[key]

    def render_space(self, heroes, kind):
        """{hero: unit vector} of each hero's renders centred on the average of ALL these renders. Renders share a look of their own (the model's), which centring on photos leaves in;
        set renders against each other only in this space."""
        got = {h: self._load(h, kind) for h in heroes}
        got = {h: g for h, g in got.items() if g}
        if not got:
            return {}
        mean = np.vstack([g[2] for g in got.values()]).mean(0)
        out = {}
        for h, g in got.items():
            vs = nz(g[2] - mean)
            _, core, c = core_scores(vs)
            out[h] = c
        return out


def kind_of(key):
    return {"Models": "sister", "Angels": "angel"}.get(key.split("/")[0])


def identity(space, cfg, st, rend, key, extra=()):
    """What a person folder is: her chosen photo (and any anchors from `likeness.anchors` or --anchor), her renders when they agree with it, and a seed made of both."""
    ps = space.by_key.get(key, [])
    hero = key.split("/")[-1]
    parts = list(extra) + list(st.get("anchors", {}).get(hero, []))
    chosen = {cw.photo_key(n) for h, n in cfg.get("photos", {}).items() if h.lower() == hero.lower() and cw.photo_key(n)}
    anchors = [p for p in ps if cw.photo_key(p.name) in chosen or any(a and a in p.name for a in parts)]
    a = nz(np.mean([p.vec for p in anchors], axis=0)) if anchors else None
    got = rend.centroid(hero, kind_of(key)) if rend and kind_of(key) else None
    r = got[0] if got else None
    seeds, conflict = [], False
    if a is not None:
        seeds.append(a)
    if r is not None:
        if a is None or float(a @ r) >= SAME_LOOK:
            seeds.append(r)
        else:
            conflict = True
    return {"anchors": anchors, "a": a, "r": r, "nr": got[1] if got else 0, "seed": nz(np.sum(seeds, axis=0)) if seeds else None, "conflict": conflict}


def folder_core(space, key, ident=None):
    ps = space.by_key[key]
    scores, core, c = core_scores(np.array([p.vec for p in ps]), ident["seed"] if ident else None)
    return ps, scores, core, c


def identity_vec(c, ident):
    """The vector that stands for a person: her photos' core, joined with her renders when those are the same person."""
    r = ident["r"] if ident else None
    return nz(c + r) if r is not None and float(c @ r) >= SAME_LOOK else c


def anchor_args(values):
    out = collections.defaultdict(list)
    for v in values or []:
        h, _, part = v.partition("=")
        out[h.lower()].append(part)
    return out


def cmd_clean(args):
    cfg, st, work, cache, space = build(args)
    rend = None if args.no_renders else Renders(cfg, cache, args.embedder or Embedder(), st, space)
    extra = anchor_args(args.anchor)
    names = [n.lower() for n in (args.names or [])]
    keys = [k for k in space.keys if (not names or k.split("/")[-1].lower() in names) and (not args.group or k.split("/")[0].lower() == args.group.lower())]
    moves, rows, sheet = [], [], []
    for key in keys:
        ident = identity(space, cfg, st, rend, key, extra.get(key.split("/")[-1].lower(), []))
        ps = space.by_key[key]
        if len(ps) < 3 and ident["seed"] is None:
            rows.append((key, len(ps), "skipped: fewer than 3 photos and nothing to compare them with"))
            continue
        ps, scores, core, c = folder_core(space, key, ident)
        protected = {id(p) for p in ident["anchors"]}
        out_thr = args.sister_out if key.startswith("Models/") else st["odd"]  # a sister's folder only loses photos that are clearly someone else
        mine, keep = [], 0
        for p, s in zip(ps, scores):
            if id(p) in protected or s >= args.keep:
                keep += 1
            elif s >= out_thr or p.faces > 1 or ident["conflict"]:
                mine.append(Move(p, key, f"borderline for {key} ({s:.2f})", s, bucket="review"))
            else:
                rank = [r for r in space.ranking(p.vec, skip=p, own=key) if r[1] != key]
                dest = rank[0][1] if rank and rank[0][0] >= st["assign"] and (len(rank) < 2 or rank[0][0] - rank[1][0] >= st["margin"]) else "Prospects/Various"
                mine.append(Move(p, dest, f"does not look like {key} ({s:.2f})", s))
        rev = sum(1 for m in mine if m.bucket == "review")
        note = ""
        if ident["conflict"]:
            note = f"  NOTE: her renders look like someone else than her chosen photo (render~photo {float(ident['a'] @ ident['r']):.2f}); nothing sent away, only set aside to review"
        elif ident["r"] is not None:
            note = f"  (renders: {ident['nr']} faces, {float(c @ ident['r']):.2f} like her photos)"
        rows.append((key, len(ps), f"keep {keep}, review {rev}, out {len(mine) - rev}{note}"))
        moves += mine
        if mine:
            sheet += [(key.split("/")[-1], [ps[i] for i in core][:10]), ("  set aside", [m.photo for m in mine][:10])]
    for key, n, text in rows:
        print(f"  {key:32} {n:3} photos: {text}")
    dests = collections.Counter((m.to + ("/review" if m.bucket == "review" else "")) for m in moves)
    print(f"\n{len(moves)} photo(s) to move: " + ", ".join(f"{v} -> {k}" for k, v in dests.most_common(12)))
    if args.sheet and sheet:
        make_sheet(sheet, args.sheet)
    if args.apply and moves:
        n = execute(moves, work, True, cache)
        print(f"{n} photo(s) moved")
        after_moves(args, n > 0)
    elif moves:
        print("preview only; add --apply to move them")


def cmd_group(args):
    cfg, st, work, cache, space = build(args, with_mixed=True)
    taken = {name.split("/")[-1] for _, name, _ in cw.photo_folders(cfg, work)}
    names = [n.lower() for n in (args.names or [])]
    artists = sorted({p.key for p in space.photos if p.key.startswith("Artists/") and p.key.count("/") == 1})
    moves, sheet = [], []
    for ak in artists:
        if names and ak.split("/")[1].lower() not in names:
            continue
        ps = [p for p in space.photos if p.key == ak and p.usable(st["minFace"])]
        if len(ps) < st["minCluster"]:
            continue
        groups = [g for g in cluster(np.array([p.vec for p in ps]), args.cluster or st["cluster"]) if len(g) >= st["minCluster"]]
        grouped = sum(len(g) for g in groups)
        print(f"{ak}: {len(ps)} usable photos -> {len(groups)} group(s) of {st['minCluster']}+ ({grouped} photos); {len(ps) - grouped} stay where they are")
        for g in sorted(groups, key=len, reverse=True):
            members = [ps[i] for i in g]
            name = invent_name("|".join(sorted(m.sha for m in members)), taken)
            taken = taken | {name}
            near = space.ranking(nz(np.mean([m.vec for m in members], axis=0)))
            note = f"; alike {near[0][1]} ({near[0][0]:.2f})" if near and near[0][0] >= st["alike"] else ""
            print(f"    {ak}/{name}: {len(members)} photos{note}")
            moves += [Move(m, f"{ak}/{name}", f"one person in {ak} ({len(members)} photos{note})") for m in members]
            sheet.append((name, members[:10]))
    if args.sheet and sheet:
        make_sheet(sheet, args.sheet)
    if args.apply and moves:
        n = execute(moves, work, True, cache)
        print(f"{n} photo(s) moved")
        after_moves(args, n > 0)
    elif moves:
        print("preview only; add --apply to group them")


def cmd_sisters(args):
    """Do the sisters read as one family? Drakness is the anchor; a sister who is too different (or too alike another) is a candidate to replace."""
    cfg, st, work, cache, space = build(args)
    rend = None if args.no_renders else Renders(cfg, cache, args.embedder or Embedder(), st, space)
    keys = [k for k in space.keys if k.startswith("Models/")]
    anchor = f"Models/{args.anchor_sister}"
    if anchor not in keys:
        sys.exit(f"anchor sister {args.anchor_sister} not found; sisters: {', '.join(k.split('/')[1] for k in keys)}")
    info = {}
    for k in keys:
        ident = identity(space, cfg, st, rend, k)
        ps, scores, core, c = folder_core(space, k, ident)
        info[k] = {"vec": identity_vec(c, ident), "c": c, "r": ident["r"], "nr": ident["nr"], "n": len(ps), "core": len(core)}
    rspace = rend.render_space([k.split("/")[1] for k in keys], "sister") if rend else {}
    # where each sister falls, against Drakness, among ALL the people in the library (photo space): a sister near the bottom is vastly unlike her
    others_all = [k for k in space.keys if k not in keys and len(space.by_key[k]) >= 3]
    pool = np.array([float(nz(np.mean([p.vec for p in space.by_key[k]], axis=0)) @ info[anchor]["c"]) for k in others_all]) if others_all else np.zeros(1)

    def pct(x):
        return float(np.mean(pool <= x))
    print(f"{len(keys)} sisters; {args.anchor_sister} is the anchor. Her sisters are different women, so the question is whether any is VASTLY unlike her: the bottom 10% of the library against her.")
    print(f"  {'sister':10} {'photos':>6} {'renders~photos':>15} {'photos vs ' + args.anchor_sister[:4]:>15} {'(library %ile)':>14} {'renders vs ' + args.anchor_sister[:4]:>17}  nearest other sister (photos)   verdict")
    flagged, md = [], []
    for k in sorted(keys, key=lambda k: (k != anchor, k)):
        v, name = info[k], k.split("/")[1]
        to_p = float(v["c"] @ info[anchor]["c"]) if k != anchor else 1.0
        rk = name in rspace and args.anchor_sister in rspace
        to_a = float(rspace[name] @ rspace[args.anchor_sister]) if rk and k != anchor else (1.0 if rk else None)
        others = sorted(((float(v["c"] @ info[o]["c"]), o.split("/")[1]) for o in keys if o != k), reverse=True)
        rp = float(v["c"] @ v["r"]) if v["r"] is not None else None
        verdict = []
        if k != anchor and pct(to_p) <= 0.10:
            verdict.append(f"VASTLY UNLIKE {args.anchor_sister} (bottom {pct(to_p):.0%} of the library)")
        if others and others[0][0] >= 0.45:
            verdict.append(f"TOO ALIKE {others[0][1]}")
        if rp is not None and rp < SAME_LOOK:
            verdict.append("her old renders do not match her photos")
        if verdict and k != anchor:
            flagged.append(k)
        txt = ", ".join(verdict) or "ok"
        print(f"  {name:10} {v['n']:6} {('%.2f' % rp) if rp is not None else '-':>15} {to_p:15.2f} {('%.0f%%' % (pct(to_p) * 100)) if k != anchor else '-':>14} {('%.2f' % to_a) if to_a is not None else '-':>17}  {others[0][1]:10} {others[0][0]:5.2f}            {txt}")
        md.append((name, v["n"], rp, to_p, (pct(to_p) if k != anchor else None), to_a, f"{others[0][1]} {others[0][0]:.2f}", txt))
    order = sorted(((float(info[k]["c"] @ info[anchor]["c"]), k.split("/")[1]) for k in keys if k != anchor), reverse=True)
    print(f"\nclosest to {args.anchor_sister} by photos: " + ", ".join(f"{n} {s:.2f}" for s, n in order[:4]) + "; furthest: " + ", ".join(f"{n} {s:.2f}" for s, n in order[-3:]))
    if rspace:
        ro = sorted(((float(rspace[k.split('/')[1]] @ rspace[args.anchor_sister]), k.split("/")[1]) for k in keys if k != anchor and k.split("/")[1] in rspace), reverse=True)
        print(f"closest to {args.anchor_sister} by renders (compared only with other renders): " + ", ".join(f"{n} {s:.2f}" for s, n in ro[:3]) + "; furthest: " + ", ".join(f"{n} {s:.2f}" for s, n in ro[-3:]))
    if flagged:
        print("\nif you would swap a flagged sister, these look most like Drakness's sister (similar, not the same) and are not another sister:")
        cands = [k for k in space.keys if not k.startswith("Models/") and len(space.by_key[k]) >= 3]
        for k in flagged:
            rows = []
            for c in cands:
                vc = nz(np.mean([p.vec for p in space.by_key[c]], axis=0))
                s = float(vc @ info[anchor]["c"])
                worst = max(float(vc @ info[o]["c"]) for o in keys if o != anchor and o != k)
                rows.append((abs(s - 0.28) + 2 * max(0.0, worst - 0.30), s, worst, c))
            print(f"  instead of {k.split('/')[1]}: " + "; ".join(f"{c} ({s:.2f} to {args.anchor_sister}, {w:.2f} to another sister)" for _, s, w, c in sorted(rows)[:3]))
    if args.sheet:
        make_sheet([(k.split("/")[1], space.by_key[k][:8]) for k in sorted(keys, key=lambda k: (k != anchor, k))], args.sheet)
    if args.md:
        lines = ["| Sister | Photos | Old renders match her photos | Photos vs Drakness | Library percentile | Renders vs Drakness | Nearest other sister | Verdict |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for name, n, rp, to_p, pc, to_a, near, txt in md:
            lines.append(f"| {name} | {n} | {('%.2f' % rp) if rp is not None else '-'} | {to_p:.2f} | {('%.0f%%' % (pc * 100)) if pc is not None else '-'} | {('%.2f' % to_a) if to_a is not None else '-'} | {near} | {txt} |")
        pathlib.Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"table written: {args.md}")


def best_photo(space, key, c):
    """The photo of this person to start a render from: a clear single face that looks like her, large, portrait."""
    from PIL import Image
    best = None
    for p in space.by_key[key]:
        try:
            with Image.open(p.path) as im:
                w, h = im.size
        except Exception:  # noqa: BLE001
            continue
        score = float(p.vec @ c) + min(p.px, 500) / 2500 - (0.15 if p.faces > 1 else 0) - (0.10 if w > h else 0)
        if best is None or score > best[0]:
            best = (score, p)
    return best[1] if best else None


def retire_empty(work, keys, keep=()):
    """A person folder whose gallery and review folders are now empty is moved to <work>/_retired/<its path>, with its scaled copies and archives, so it stops showing up as a person. Nothing is deleted."""
    done = []
    for key in sorted(set(keys)):
        if key in keep:
            continue
        d = pathlib.Path(work) / key
        if not d.is_dir():
            continue
        left = [p for sub in ("gallery", "review") for p in originals.images(d / sub)]
        nested = [s for s in d.iterdir() if s.is_dir() and (s / "gallery").is_dir()]
        if left or nested:
            continue
        dest = pathlib.Path(work) / "_retired" / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            dest = dest.with_name(dest.name + "_" + datetime.datetime.now().strftime("%H%M%S"))
        shutil.move(str(d), str(dest))
        done.append(key)
    return done


def cmd_pairs(args):
    """Pair every angel with the sister of her element from ALL the faces in the library (angels, prospects, grouped artists), similar to the sister but not the same, and not like anyone else."""
    cfg, st, work, cache, space = build(args)
    rend = None if args.no_renders else Renders(cfg, cache, args.embedder or Embedder(), st, space)
    pairs = dict(PAIRS)
    pairs.update(st.get("pairs", {}))
    low, high, target = st.get("pairLow", 0.15), st.get("pairHigh", 0.40), args.target
    sis_key = {s: f"Models/{s}" for s in set(pairs.values()) if f"Models/{s}" in space.by_key}
    angel_dir = {}
    for k in space.keys:
        if k.startswith("Angels/"):
            angel_dir[k.split("/")[-1].lower()] = k
    ident_of = {}
    cohesion = {}

    def vec_of(key):
        if key not in ident_of:
            ident = identity(space, cfg, st, rend, key)
            ps, scores, core, c = folder_core(space, key, ident)
            ident_of[key] = (identity_vec(c, ident), c)
            cohesion[key] = float(np.mean(scores)) if len(ps) > 1 else 0.0
        return ident_of[key][0]
    sis_vec = {s: vec_of(k) for s, k in sis_key.items()}
    wanted = {s.lower() for s in (args.sister or [])}
    slots = [a for a, s in pairs.items() if s in sis_vec and (not wanted or s.lower() in wanted)]
    fixed_keys = [angel_dir[a.lower()] for a in FIXED_ANGELS if a.lower() in angel_dir]
    kept = [angel_dir[a.lower()] for a in pairs if a not in slots and a.lower() in angel_dir]
    cands = [k for k in space.keys if not k.startswith("Models/") and k not in fixed_keys and k not in kept and len(space.by_key[k]) >= args.min_photos]
    weak = [k for k in cands if (vec_of(k) is not None) and cohesion[k] < args.min_cohesion and k not in {angel_dir.get(a.lower()) for a in slots}]
    if weak:
        print(f"left out ({len(weak)}): too few photos that agree on one face (cohesion below {args.min_cohesion}): " + ", ".join(f"{k.split('/', 1)[1]} {cohesion[k]:.2f}" for k in weak[:12]))
    cands = [k for k in cands if k not in weak]
    if not slots or not cands:
        sys.exit("nothing to pair: need sisters with photos and candidate people with enough photos")
    cv = np.array([vec_of(k) for k in cands])
    ca = {k: i for i, k in enumerate(cands)}
    sv_names = list(sis_vec)
    SV = np.array([sis_vec[s] for s in sv_names])
    sim_cs = cv @ SV.T
    sim_cc = cv @ cv.T
    fixed_vec = [vec_of(k) for k in fixed_keys + kept]
    sim_cf = cv @ np.array(fixed_vec).T if fixed_vec else np.zeros((len(cands), 0))
    n_photos = np.array([len(space.by_key[k]) for k in cands])

    def pair_cost(ci, slot):
        sname = pairs[slot]
        s = sim_cs[ci, sv_names.index(sname)]
        cost = abs(s - target) + 2 * max(0.0, low - s) + 2 * max(0.0, s - high)
        others = [sim_cs[ci, j] for j, nme in enumerate(sv_names) if nme != sname]
        cost += 2.0 * max(0.0, max(others) - 0.28) if others else 0.0
        cost += 0.02 * max(0, 6 - n_photos[ci])
        if cands[ci] == angel_dir.get(slot.lower()):
            cost -= args.keep_bonus
        return cost

    def clash(ci, cj):
        return 4.0 * max(0.0, sim_cc[ci, cj] - 0.22)

    def fixed_clash(ci):
        return sum(4.0 * max(0.0, x - 0.30) for x in sim_cf[ci])

    def total(assign):
        t = sum(pair_cost(ci, a) + fixed_clash(ci) for a, ci in assign.items())
        return t + sum(clash(x, y) for x, y in itertools.combinations(assign.values(), 2))

    rng = random.Random(7)
    best_assign, best_total = None, 1e9
    for trial in range(args.trials):
        order = slots[:]
        rng.shuffle(order)
        assign = {}
        for slot in order:
            opts = [(pair_cost(ci, slot) + fixed_clash(ci) + sum(clash(ci, cj) for cj in assign.values()) + (rng.random() * 0.08 if trial else 0), ci) for ci in range(len(cands)) if ci not in assign.values()]
            assign[slot] = min(opts)[1]
        t = total(assign)
        if t < best_total:
            best_assign, best_total = dict(assign), t
    improved = True
    while improved:
        improved = False
        for slot in slots:
            for ci in range(len(cands)):
                if ci in best_assign.values():
                    continue
                trial_assign = dict(best_assign)
                trial_assign[slot] = ci
                t = total(trial_assign)
                if t < best_total - 1e-9:
                    best_assign, best_total, improved = trial_assign, t, True
    print(f"pairing {len(slots)} angel(s) with their sisters from {len(cands)} people (target {target:.2f} against the sister; {low} to {high} is the band); {len(fixed_keys)} fixed ({', '.join(FIXED_ANGELS)}), {len(kept)} kept as they are")
    print(f"  {'angel':10} {'sister':10}  {'now':32} {'to sister':>9}   {'recommended':34} {'to sister':>9}  clashes with / note")
    result, md = [], []
    for slot in slots:
        sname = pairs[slot]
        j = sv_names.index(sname)
        cur = angel_dir.get(slot.lower())
        cur_s = float(vec_of(cur) @ SV[j]) if cur else None
        ci = best_assign[slot]
        rec = cands[ci]
        s = float(sim_cs[ci, j])
        near = sorted(((float(sim_cc[ci, ca[cands[cj]]]), cands[cj].split("/", 1)[1]) for slot2, cj in best_assign.items() if slot2 != slot), reverse=True)[:1]
        note = f"{near[0][1]} {near[0][0]:.2f}" if near else ""
        alts = sorted(((pair_cost(c2, slot) + fixed_clash(c2), c2) for c2 in range(len(cands)) if c2 != ci))[:3]
        alt_names = [cands[c2] for _, c2 in alts]
        # a replacement only counts when it is inside the band; otherwise the angel already in the folder stays and the slot waits for better candidates
        # (unless she is a near twin of a fixed angel such as Angelica: then even a candidate below the band is better)
        twin = max((float(vec_of(cur) @ fv) for fv in fixed_vec), default=-1.0) if cur and fixed_vec else -1.0
        if cur and rec != cur and s < low and (cur_s is None or cur_s <= high) and twin < args.twin:
            note = f"no candidate in the band yet (best {rec.split('/', 1)[1]} {s:.2f}); kept. {note}"
            rec, s = cur, cur_s if cur_s is not None else 0.0
        elif cur and rec != cur and twin >= args.twin:
            note = f"{cur.split('/', 1)[1]} is a near twin of a fixed angel ({twin:.2f}); replaced by the best available even though it is below the band. {note}"
        mark = "(keep)" if rec == cur else ""
        print(f"  {slot:10} {sname:10}  {cur or '(no folder)':32} {('%.2f' % cur_s) if cur_s is not None else '-':>9}   {rec + ' ' + mark:34} {s:9.2f}  {note}")
        result.append({"slot": slot, "sister": sname, "now": cur, "now_s": cur_s, "rec": rec, "rec_s": s, "alts": alt_names, "note": note})
        md.append((slot, sname, cur or "-", cur_s, rec, s, ", ".join(c.split("/", 1)[1] for c in alt_names), note))
    if args.sheet:
        rows = []
        for r in result:
            rows.append((f"{r['sister']} (sister)", space.by_key[sis_key[r['sister']]][:6]))
            rows.append((f"-> {r['slot']}: {r['rec'].split('/', 1)[1]}", space.by_key[r["rec"]][:6]))
        make_sheet(rows, args.sheet)
    if args.md:
        lines = ["| Angel | Sister | Folder now | Now vs sister | Recommended | Vs sister | Alternatives | Note |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for slot, sname, cur, cs, rec, s, alts, note in md:
            lines.append(f"| {slot} | {sname} | {cur} | {('%.2f' % cs) if cs is not None else '-'} | {rec} | {s:.2f} | {alts} | {note} |")
        pathlib.Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"table written: {args.md}")
    if not args.apply:
        print("\npreview only; add --apply to arrange the folders, set the recommended photos and re-point the workflows")
        return
    # arrange: each photo of a chosen person goes to the gallery of the angel it was chosen for; an angel folder nobody chose goes to that angel's review folder
    chosen_for = {r["rec"]: r["slot"] for r in result}
    moves, pick = [], {}
    dir_of = {a.lower(): angel_dir.get(a.lower(), f"Angels/{a}") for a in pairs}
    for r in result:
        slot, rec = r["slot"], r["rec"]
        to = dir_of[slot.lower()]
        ident = identity(space, cfg, st, rend, rec)
        ps, scores, core, c = folder_core(space, rec, ident)
        bp = best_photo(space, rec, c) if rec != r["now"] else None  # a kept angel keeps the photo you chose
        pick[slot] = bp.sha if bp else None
        if rec != to:
            moves += [Move(p, to, f"{rec.split('/', 1)[1]} is the new {slot} (paired with {r['sister']}, {r['rec_s']:.2f})") for p in space.by_key[rec]]
    for slot in slots:
        cur = angel_dir.get(slot.lower())
        if cur and cur not in chosen_for:
            moves += [Move(p, cur, f"{slot}'s earlier photos, set aside for the new {slot}", bucket="review") for p in space.by_key[cur]]
    n = execute(moves, work, True, cache)
    print(f"\n{n} photo(s) moved")
    gone = retire_empty(work, [m.photo.key for m in moves], keep={cur for cur in angel_dir.values()} | {k for k in space.keys if k.startswith(("Models/", "Angels/"))})
    if gone:
        print("emptied folders moved to _retired: " + ", ".join(gone))
    after_moves(args, n > 0)
    # set the recommended photo and point the angel's workflows at it
    cfg2 = cw.load_cfg()
    cache2 = Cache(args.cache or DATA / "likeness_cache.json")
    renames = {}
    for slot, sha in pick.items():
        if not sha:
            continue  # a kept angel keeps her photo
        folder = work / dir_of[slot.lower()] / "gallery"
        found = next((p for p in originals.images(folder) if cache2.sha(p) == sha), None) if sha else None
        hero = next((h for h in cfg2.get("photos", {}) if h.lower() == slot.lower()), None)
        if not found or not hero:
            print(f"  no photo set for {slot} ({'photo not found' if not found else 'not in workspaces.json photos'})")
            continue
        scaled = found.parent.parent / f"gallery_{cfg2['standardSize'][0]}x{cfg2['standardSize'][1]}" / f"{found.stem}_{cfg2['standardSize'][0]}x{cfg2['standardSize'][1]}.png"
        if scaled.exists() and cfg2["photos"][hero] != scaled.name:
            renames[hero] = (cfg2["photos"][hero], scaled)
            print(f"  photo for {slot}: {cfg2['photos'][hero]} -> {scaled.name}")
    if renames:
        touched = cw.repoint_photos(cfg2, renames, False)
        print("workflows changed: " + (", ".join(f"{v} in {k}" for k, v in touched.items()) or "none"))


def main(argv=None, embedder=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="the folder that holds Angels, Models, Prospects and Artists (default: workspaces.json paths.workRoot)")
    ap.add_argument("--cache", help=argparse.SUPPRESS)
    ap.add_argument("--no-originals", action="store_true", help="after moving, do not run the originals tool")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, *positional, apply=False, sheet=False, **kw):
        s = sub.add_parser(name, **kw)
        for a in positional:
            s.add_argument(a)
        if apply:
            s.add_argument("--apply", action="store_true", help="really move the files (default: preview only)")
        if sheet:
            s.add_argument("--sheet", help="save a picture of the faces involved to this PNG")
        s.set_defaults(fn=fn)
        return s

    add("scan", cmd_scan)
    add("calibrate", cmd_calibrate)
    add("alike", cmd_alike, sheet=True).add_argument("--min", type=float, help="show pairs at or above this score (default: settings alike)")
    add("compare", cmd_compare, "a", "b", sheet=True)
    s = add("folder", cmd_folder, "name", apply=True, sheet=True)
    s.add_argument("--all", action="store_true", help="list every photo's score, not just the ones to check")
    s.add_argument("--outside", action="store_true", help="always list who else in the library looks like this folder (done automatically when the folder is one person)")
    add("like", cmd_like).add_argument("paths", nargs="+")
    s = add("sort", cmd_sort, apply=True, sheet=True)
    s.add_argument("--plan", help="also write the moves to this JSON file")
    s.add_argument("--singles", action="store_true", help="a photo that matches nobody and has no look-alike in the pool gets a new folder of its own, so the pool ends up holding only photos with no usable face")
    add("merge", cmd_merge, "a", "b", apply=True, sheet=True)
    add("retire", lambda a: cmd_merge(a, retire=True), "name", apply=True, sheet=True)
    s = add("clean", cmd_clean, apply=True, sheet=True)
    s.add_argument("names", nargs="*", help="folders to clean (default: every person folder; with --group, that kind)")
    s.add_argument("--group", help="Angels, Models or Prospects")
    s.add_argument("--keep", type=float, default=0.25, help="photos scoring at least this against the folder's core are kept (default 0.25); between the 'odd' score and this they go to the folder's review folder")
    s.add_argument("--sister-out", type=float, default=0.05, help="in a sister's folder only photos scoring below this leave it (default 0.05); the rest of the doubtful ones go to her review folder")
    s.add_argument("--anchor", action="append", help="HERO=part of a photo's name that is certainly her (repeatable); the chosen photo and `likeness.anchors` in workspaces.json are used too")
    s.add_argument("--no-renders", action="store_true", help="ignore the ComfyUI renders when deciding what she looks like")
    s = add("group", cmd_group, apply=True, sheet=True)
    s.add_argument("names", nargs="*", help="artist folders (default: all)")
    s.add_argument("--cluster", type=float, help="average similarity needed to be one person (default: settings cluster)")
    s = add("sisters", cmd_sisters, sheet=True)
    s.add_argument("--anchor-sister", default="Drakness")
    s.add_argument("--no-renders", action="store_true")
    s.add_argument("--md", help="also write the table as markdown to this file")
    s = add("pairs", cmd_pairs, apply=True, sheet=True)
    s.add_argument("--sister", action="append", help="only (re-)pair the angel of this sister (repeatable); the other angels stay as they are")
    s.add_argument("--target", type=float, default=0.28, help="how alike an angel should be to her sister (similar, not the same)")
    s.add_argument("--keep-bonus", type=float, default=0.06, help="how much better a replacement must be than the angel already in the folder")
    s.add_argument("--min-photos", type=int, default=4, help="a person needs this many photos to be considered")
    s.add_argument("--min-cohesion", type=float, default=0.45, help="and their photos must agree on one face this well (average score against the person's own core)")
    s.add_argument("--twin", type=float, default=0.45, help="an angel this alike a fixed angel (Angelica) is replaced even when no candidate is in the band")
    s.add_argument("--trials", type=int, default=1500)
    s.add_argument("--no-renders", action="store_true")
    s.add_argument("--md", help="also write the table as markdown to this file")
    add("undo", cmd_undo, apply=True)
    args = ap.parse_args(argv)
    args.embedder = embedder
    for k in ("apply", "sheet", "plan", "all", "outside"):
        if not hasattr(args, k):
            setattr(args, k, None if k not in ("apply", "all", "outside") else False)
    args.fn(args)


if __name__ == "__main__":
    main()
