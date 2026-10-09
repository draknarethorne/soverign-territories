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
    return any(fnmatch.fnmatch(key.lower(), p.lower()) for p in patterns)


def read_library(cfg, work, cache, embed, st, progress=True, only=None):
    """Every original in the person folders and the pool (other mixed folders are skipped: many people, never used)."""
    photos, todo = [], []
    for root in cw.photo_roots(cfg, work):
        for folder in sorted(p for p in root.iterdir() if p.is_dir()):
            key = f"{root.name}/{folder.name}"
            if not (folder / "gallery").is_dir():
                continue
            if matches(key, st["mixed"]) and not matches(key, st["pool"]):
                continue
            for p in originals.images(folder / "gallery"):
                todo.append((p, root.name, folder.name))
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
    def __init__(self, photo, to, reason, score=None):
        self.photo, self.to, self.reason, self.score = photo, to, reason, score

    def as_dict(self):
        return {"file": str(self.photo.path), "to": self.to, "reason": self.reason, "score": None if self.score is None else round(self.score, 3)}


def chosen_keys(cfg):
    return {cw.photo_key(n) for n in cfg.get("photos", {}).values() if cw.photo_key(n)}


def plan_sort(space, st, cfg, taken):
    """Moves for the pool photos: to the person folder they match confidently, or into a new folder when several look like one new person."""
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
            if len(g) >= st["minCluster"]:
                members = [left[i] for i in g]
                name = invent_name("|".join(sorted(m.sha for m in members)), taken | {m.to.split("/", 1)[-1] for m in moves})
                new = f"Prospects/{name}"
                taken = taken | {name}
                near = space.ranking(nz(np.mean([m.vec for m in members], axis=0)))
                note = f"; alike {near[0][1]} ({near[0][0]:.2f})" if near and near[0][0] >= st["alike"] else ""
                for m in members:
                    moves.append(Move(m, new, f"one new person ({len(members)} photos{note})", None))
    return moves


def execute(moves, work, apply, cache, log=True):
    """Move the files into <to>/gallery (a duplicate of what is already there goes to the source folder's gallery_org, a different file with the same name is kept under a new one)."""
    batch = {"id": datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), "moves": []}
    made = 0
    for m in moves:
        src = m.photo.path
        dest_dir = pathlib.Path(work) / m.to / "gallery"
        dst = dest_dir / src.name
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


def print_plan(moves, space):
    by = collections.defaultdict(list)
    for m in moves:
        by[m.to].append(m)
    for to, ms in sorted(by.items()):
        new = to not in space.by_key
        print(f"  -> {to}{'  (NEW folder)' if new else ''}: {len(ms)} photo(s)")
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

def build(args):
    cfg = cw.load_cfg()
    st = settings(cfg)
    work = pathlib.Path(args.root) if args.root else cw.work_root(cfg)
    cache = Cache(args.cache or DATA / "likeness_cache.json")
    embed = args.embedder or Embedder()
    photos = read_library(cfg, work, cache, embed, st)
    return cfg, st, work, cache, Space(photos, st)


def folder_key(space, name):
    hits = [k for k in space.keys if k.lower() == name.lower() or k.split("/", 1)[1].lower() == name.lower()]
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
        note = "  <- an angel and a sister: do not use both" if {ga, gb} == {"Angels", "Models"} else "  <- two angels" if ga == gb == "Angels" else ""
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
        sys.exit(f"{key} has {len(ps)} usable photo(s); need 3 or more to say which one is the odd one")
    print(f"{key}: {len(ps)} photos; each against the others in the folder (a photo below {st['odd']} may be another person):")
    odd = []
    for p in sorted(ps, key=lambda p: float(p.vec @ space.centroid(key, skip=p))):
        s = float(p.vec @ space.centroid(key, skip=p))
        rank = space.ranking(p.vec, skip=p, own=key)
        other = next((r for r in rank if r[1] != key), None)
        flag = "  <- odd one out" if s < st["odd"] else ""
        print(f"  {s:5.2f}  {p.name}   (closest other folder: {other[1]} {other[0]:.2f}){flag}")
        if s < st["odd"]:
            odd.append((p, other))
    if args.sheet:
        make_sheet([(key.split("/", 1)[1], ps[:10])] + [(f"odd: {o[0].name[-12:]}", [o[0]]) for o in odd], args.sheet)
    moves = [Move(p, o[1] if o and o[0] >= st["assign"] else "Prospects/Various", f"odd one out of {key}") for p, o in odd]
    if moves:
        print("\nwould move the odd ones:")
        print_plan(moves, space)
        if args.apply:
            execute(moves, work, True, cache)
            after_moves(args, True)
        else:
            print("preview only; add --apply to move them")


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
    taken = {p.name for r in cw.photo_roots(cfg, work) for p in r.iterdir() if p.is_dir()}
    moves = plan_sort(space, st, cfg, taken)
    pool = [p for p in space.photos if matches(p.key, st["pool"])]
    print(f"{len(pool)} photo(s) in the pool; {len(moves)} would move (assign >= {st['assign']} with a margin of {st['margin']}, or a new person of {st['minCluster']}+ photos at {st['cluster']}):")
    print_plan(moves, space)
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
    add("folder", cmd_folder, "name", apply=True, sheet=True)
    add("like", cmd_like).add_argument("paths", nargs="+")
    s = add("sort", cmd_sort, apply=True, sheet=True)
    s.add_argument("--plan", help="also write the moves to this JSON file")
    add("merge", cmd_merge, "a", "b", apply=True, sheet=True)
    add("retire", lambda a: cmd_merge(a, retire=True), "name", apply=True, sheet=True)
    add("undo", cmd_undo, apply=True)
    args = ap.parse_args(argv)
    args.embedder = embedder
    for k in ("apply", "sheet", "plan"):
        if not hasattr(args, k):
            setattr(args, k, None if k != "apply" else False)
    args.fn(args)


if __name__ == "__main__":
    main()
