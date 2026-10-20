#!/usr/bin/env python3
"""Compare the faces in the original-photo library, and sort, merge and retire photos by likeness (preview unless --apply).

Faces are found and turned into an identity vector with OpenCV's YuNet and SFace models (two small files, downloaded once to
%LOCALAPPDATA%\\sovereign-territories\\models; nothing leaves your machine). Every photo is cached by its content, so a rename or a move
costs nothing. Scores are COSINE SIMILARITY AFTER SUBTRACTING THE LIBRARY'S AVERAGE FACE: without that every glamour face looks alike to
the model. Read a score as a ranking inside your own library, not as a yes/no:

    about 0.55 and up   the same person (what a folder's own photos score against each other)
    0.30 to 0.45        very alike: you would think they were cousins; do not use both for different heroes
    below 0.15          different people

The library is <work root>/<Root>/<Name>/gallery. A folder of one person (Angels, Sisters, named Prospects) is a "person" folder;
Artists/* and Various hold many people and are "mixed": they are never used to describe a person, and Various is the pool that `sort` empties
(Various sits beside Angels; a Prospects/Various is still read). Sisters was called Models until Oct 10; both names work.
Each person folder keeps a z_ file with her name and history (see people.py; `likeness names` lists them).
Configure under "likeness" in workflows/workspaces.json (mixed, pool, assign, margin, cluster, minCluster, odd, alike, minFace).

  likeness rebaseline                 preview whole-library category changes, likely mismatches and Junk candidates
  likeness rebaseline --apply-categories  move only threshold-driven Prospect/Potential folders (back up first)
  likeness scan                       read every photo once (cached); lists photos with no usable face
  likeness calibrate                  how reliable the scores are on YOUR library (the thresholds in effect)
  likeness audit-core [NAMES]         read-only core and low-score report, with tracked anchors/protection applied
  likeness alike                      pairs of people who look alike (angel against angel, angel against sister ...), most alike first
  likeness compare Angelica azaline   how alike two folders are, and the photos that match best
  likeness folder Drakness            the photos that look like a different person from the rest of the folder
  likeness like path\\to\\photo.jpg      which folders a new photo looks like
  likeness sort                       Various: photos that match an existing person move there, clusters of one new person
                                      go to a new Prospects/<invented name> folder; the rest stay
  likeness merge Mia "Eva Emily"      move every photo of one folder into another (one person under two names)
  likeness rematch                    prospect folders that are one person under two names are merged (0.48); look-alikes of an angel or sister are listed
  likeness retire-empty               archive empty Prospect folders (preview unless --apply)
  likeness retire azaline             move a folder's photos back to Various so she can be cast again
  likeness archive-list tmp\\archive-people.md [--apply] archive listed prospects or artist people under _retired
  likeness names                      who is in each folder (the z_ files); writes the missing ones with --apply
  likeness undo                       put the last batch of moves back

Every command that moves files previews first; add --apply to do it (the bin launcher does not add it for you: moving photos is the one
thing worth a second look). After moving, the originals tool renames, scales, prunes and re-points as usual. Add --sheet FILE to any
command to save a picture of the faces involved. Photos chosen in workspaces.json are never moved by `sort` and are flagged by merge and retire.
"""
import argparse
import collections
import contextlib
import datetime
import fnmatch
import hashlib
import io
import itertools
import json
import os
import pathlib
import random
import re
import shutil
import sys
import types

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflows"))
sys.path.insert(0, str(ROOT / "tools/art"))
import comfy_workflows as cw  # noqa: E402
import originals  # noqa: E402
import screens  # noqa: E402
import people  # noqa: E402
import library_backup  # noqa: E402
from likeness_library import metadata  # noqa: E402
from likeness_library.audit import audit_person  # noqa: E402
from likeness_library.scoring import core_scores, nz  # noqa: E402

DATA = pathlib.Path(os.environ.get("LOCALAPPDATA") or (pathlib.Path.home() / ".cache")) / "sovereign-territories"
MODEL_URLS = {
    "face_detection_yunet_2023mar.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "face_recognition_sface_2021dec.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx",
}
SETTINGS = {"mixed": ["Artists/*", "Various", "Prospects/Various", "Potentials/Various"], "pool": ["Various", "Prospects/Various", "Potentials/Various"], "assign": 0.40, "margin": 0.10, "cluster": 0.25,
            "minCluster": 3, "odd": 0.15, "alike": 0.30, "minFace": 60, "multiFace": 0.3,
            # singles: a one-photo prospect joins a prospect she scores this much against (margin 0.05). rematch: two prospect folders whose centroids score this much are one person.
            # rematchCast: a prospect that scores this much against an angel or a sister is only listed (the cast is yours to change). different: pairs of folders never merged or listed, [["Prospects/Brielle Carter", "Sisters/Draknara"]].
            # Measured on this library (calibrate, leave-one-out): a match at 0.40 with a margin of 0.10 is right 98.0% of the time and finds 75% of the photos, at 0.45 98.6% and 71%, at 0.35 97.2% and 77%.
            "singles": 0.35, "rematch": 0.48, "rematchCast": 0.50, "different": [],
            # castMerge: a prospect, a new group or a single photo that scores this much against an angel or a sister IS her (the same person scores about 0.55): it joins her folder, and the z_ file remembers who it was.
            "castMerge": 0.55}
FIRST = ["Alina", "Bea", "Calla", "Dara", "Elise", "Faye", "Gia", "Hana", "Ivy", "Jade", "Kira", "Lena", "Maren", "Nia", "Odette", "Paige", "Quinn", "Rhea",
         "Sabine", "Tessa", "Una", "Vera", "Wren", "Xena", "Yara", "Zoe", "Anya", "Brynn", "Cleo", "Delia", "Esme", "Freya", "Greta", "Hollis", "Iris", "Jules",
         "Keira", "Lia", "Mara", "Neve", "Opal", "Petra", "Rina", "Sia", "Tove", "Uma", "Vienna", "Willa", "Yvette", "Zara"]
LAST = ["Ashby", "Brandt", "Calder", "Dale", "Ellery", "Fenn", "Gray", "Hale", "Ingram", "Jasper", "Keene", "Locke", "Marsh", "Nash", "Orr", "Pryce", "Quill",
        "Rowe", "Sloane", "Thorn", "Vale", "Wilde", "Yates", "Zane", "Ames", "Blythe", "Crane", "Drake", "Eden", "Frost", "Glenn", "Hart", "Ives", "Joyce",
        "Knox", "Lane", "Moss", "North", "Ogden", "Park", "Reyes", "Stone", "Tate", "Voss", "West", "Ford", "Beck", "Cole", "Dunn", "Lowe"]
FIRST.extend("""
Adelaide Ainsley Althea Amara Amelie Anika Annika Arden Ariadne Astrid Aurelia Avalon Beatrix Belle Bianca Blair Briony Cadence Celine Celeste Cerys Colette
Cordelia Dahlia Daphne Delphine Dorian Eira Elara Elodie Eloise Ember Emmeline Estelle Evangeline Fallon Farrah Fiona Florence Francesca Gwendolyn Helena Imogen Ingrid
Isadora Isolde Juno Kaia Kalista Lark Laurel Leona Lilith Linnea Lorelei Lucia Lyra Maeve Magnolia Marcella Margot Marlowe Melody Mira Mirabel Nadia Nelle Noelle
Nova Octavia Olympia Oriana Paloma Pearl Phoebe Rhiannon Romilly Rosalind Rowan Ruby Selene Serena Simone Solene Stella Sylvie Thalia Thea Valentina Vesper Viola Vivienne
Waverly Winona Xanthe Yvonne Zinnia Acacia Adara Afton Alondra Amethyst Anais Anouk April Aria Arwen Ashlyn Aviva Azalea Belen Bellamy Benedetta Briar Brisa
Calliope Camellia Carina Carmen Catarina Cecily Chandra Chiara Cressida Dahl Damaris Danica Davina Eleanora Elspeth Elva Enid Esmeralda Etta Fia Fiorella
Gaia Georgina Giselle Harlow Hestia Ilaria Iliana Ione Isabeau Jacinta Jessamine Jolie Kaori Katerina
""".split())
LAST.extend("""
Abbott Abernathy Adler Alden Alcott Albright Aldridge Amesbury Anders Anderton Archer Armitage Atwood Avery Baird Baldwin Banks Barrow Baxter Beaumont Bellamy
Bellrose Bellerose Berkley Bishop Blackwell Blanchard Bloom Bradford Branson Brantley Brawley Briarbridge Brighton Brookfield Brooks Caldwell Callahan Calloway
Camden Carlisle Carmichael Carrington Carver Chadwick Chambers Chandler Channing Chase Cheshire Cline Colebrook Collier Corbett Corbin Corwin Covington Crawford
Cross Dalton Davenant Davenport Devereux Dorsey Drayton Easton Ellington Elwood Everhart Fairchild Farley Finley Fitzgerald Fletcher Fontaine Forsythe Foster
Foxworth Garland Garrison Gentry Gilbert Godfrey Goodwin Granger Greer Hadley Hargrove Harrington Hartwell Hawthorne Hayward Hensley Holliday Holloway
Hollisworth Inglewood Irving Iverson Jameson Kendall Kingsley Kirkland Knight Langley Langston Larkspur Leighton Lennox Lockwood Lowell Madison Mallory
Manning Marlowe Merritt Middleton Montgomery Monroe Montrose Morrison Newberry Norwood Oakley Oakes Olander Pemberton Penrose Prescott Preston Radcliffe
Ramsey Rathbone Redmond Remington Renshaw Ridley Rivers Rockwell Rosenthal Rothwell Rutherford Sinclair Somerset Sterling Stratton Sutton Templeton Thorne
York
""".split())


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
        faces = None
        for thr in (0.7, 0.5):  # a close-up with heavy make-up or an odd angle scores lower: look again, less strictly, only when nothing was found
            self.det.setScoreThreshold(thr)
            _, faces = self.det.detect(small)
            if faces is not None and len(faces):
                break
        if faces is None or len(faces) == 0:
            return {"faces": 0, "t": 0.5}
        best = max(float(f[-1]) for f in faces)
        humans = human_rows(faces)
        face = max(humans, key=lambda f: f[2] * f[3])
        areas = sorted((float(f[2] * f[3]) for f in humans), reverse=True)
        vec = self.rec.feature(self.rec.alignCrop(small, face))[0]
        vec = vec / np.linalg.norm(vec)
        return {"faces": int(len(humans)), "an": int(len(faces) - len(humans)), "s": round(best, 2), "f2": round(areas[1] / areas[0], 2) if len(areas) > 1 else 0, "v": [round(float(x), 5) for x in vec],
                "box": [round(float(face[0]) / sw, 4), round(float(face[1]) / sh, 4), round(float(face[2]) / sw, 4), round(float(face[3]) / sh, 4)], "px": int(min(face[2], face[3]) / scale)}

    def faces(self, im):
        """([(x, y, w, h)] of the human faces in a PIL image, the largest first; [(x, y, w, h)] of what the detector took for a face but is not one: animals), in the picture's own pixels."""
        import cv2
        if self.det is None:
            self.load()
        img = np.asarray(im.convert("RGB"))[:, :, ::-1].copy()
        h, w = img.shape[:2]
        scale = 1600 / max(h, w) if max(h, w) > 1600 else 1.0
        small = cv2.resize(img, (int(w * scale), int(h * scale))) if scale != 1.0 else img
        self.det.setInputSize((small.shape[1], small.shape[0]))
        found = None
        for thr in (0.7, 0.5):
            self.det.setScoreThreshold(thr)
            _, found = self.det.detect(small)
            if found is not None and len(found):
                break
        rows = list(found) if found is not None else []
        humans = human_rows(rows) if rows else []
        box = lambda rs: sorted((tuple(float(v) / scale for v in r[:4]) for r in rs), key=lambda b: b[2] * b[3], reverse=True)  # noqa: E731
        return box(humans), box([r for r in rows if not any(r is hr for hr in humans)])


# The face detector also finds faces on animals (a bear, a wolf, a horse): those score lower (about 0.55 to 0.82) than a woman's face (0.9 and up).
# When a face is certain, a face scoring under HUMAN_MIN is not counted as a person; when none is certain, every face is.
HUMAN_BEST, HUMAN_MIN = 0.9, 0.85


def human_rows(rows):
    best = max(float(r[-1]) for r in rows)
    return [r for r in rows if float(r[-1]) >= HUMAN_MIN] if best >= HUMAN_BEST else list(rows)


class Cache:
    """{sha1 of the file's bytes: face data}, plus a memo of (size, mtime) -> sha1 so unchanged files are not read again."""

    def __init__(self, path):
        self.path = pathlib.Path(path)
        data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}
        self.stat, self.emb = data.get("stat", {}), data.get("emb", {})
        # a 'no face' read made before the second, less strict pass, a multi-face read made before the size of the second face was kept, and a read made before animals were told from people ("s") are read again
        self.emb = {k: v for k, v in self.emb.items() if not (v.get("faces") == 0 and "t" not in v) and not (v.get("faces", 0) > 1 and "f2" not in v) and not (v.get("v") and "s" not in v)}

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
        self.key = group if group == folder else f"{group}/{folder}"  # the Various pool is a root with a gallery of its own
        self.faces = (data or {}).get("faces", -1)
        self.f2 = (data or {}).get("f2", 0)  # area of the second largest face against the largest: a small one is a passer-by, a big one is a second person
        self.animals = (data or {}).get("an", 0)  # faces the detector found on animals
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


def is_sister(key):
    """A folder in the sisters root (Sisters, or its old name Models)."""
    return key.split("/")[0] in cw.SISTER_ROOTS


def pool_home(st):
    """The folder photos go back to when they belong nowhere: the top-level Various, or Prospects/Various where that is what the library has."""
    return st.get("poolHome") or st["pool"][0]


def side(key):
    """Where a folder's photos come from: Artists, unassigned people, or the pool; angels and sisters may take from either."""
    top = key.split("/")[0].lower()
    return "Artists" if top == "artists" else "Prospects" if top in ("prospects", "potentials", "various") else None


def apart(a, b):
    """True when a photo in folder a must never go to folder b: one is a prospect's and the other an artist's."""
    sa, sb = side(a), side(b)
    return bool(sa and sb and sa != sb)


def new_home(key, name, photo_count=1):
    """Where a new person split off folder `key` goes; unassigned groups under five become Potentials."""
    parts = key.split("/")
    return "/".join(parts[:2] + [name]) if side(key) == "Artists" and len(parts) >= 3 else unassigned_home(name, photo_count)


def unassigned_home(name, photo_count):
    return f"{'Prospects' if photo_count >= 5 else 'Potentials'}/{name}"


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

    def ranking(self, vec, skip=None, own=None, source=None):
        """[(score, key)] best first: the vector against every person folder's centroid (a photo that is in its own folder is left out of that centroid).
        source = the folder the photo is in: prospects and artists come from different places and are never mixed, so the other side is left out."""
        out = []
        for k in self.keys:
            if source and apart(source, k):
                continue
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
    def __init__(self, photo, to, reason, score=None, bucket="gallery", force=False):
        self.photo, self.to, self.reason, self.score, self.bucket, self.force = photo, to, reason, score, bucket, force  # force: a photo going home to its artist, which `apart` would otherwise stop

    def as_dict(self):
        return {"file": str(self.photo.path), "to": self.to, "bucket": self.bucket, "reason": self.reason, "score": None if self.score is None else round(self.score, 3)}


def chosen_keys(cfg):
    return {cw.photo_key(n) for n in cfg.get("photos", {}).values() if cw.photo_key(n)}


def plan_sort(space, st, cfg, taken, singles=False):
    """Moves for the pool photos: to the person folder they match confidently, or into a new folder when several look like one new person.
    With singles, a photo that matches nobody and has no look-alike in the pool gets a new folder of its own, so the pool is left holding only photos with no usable face."""
    pool = [p for p in space.photos if matches(p.key, st["pool"]) and p.usable(st["minFace"]) and not junk_reason(p, st)]
    protected = chosen_keys(cfg)
    moves, left = [], []
    for p in pool:
        if cw.photo_key(p.name) in protected:
            continue
        rank = space.ranking(p.vec, source=p.key)
        if rank and rank[0][0] >= st["assign"] and (len(rank) < 2 or rank[0][0] - rank[1][0] >= st["margin"]):
            moves.append(Move(p, rank[0][1], f"looks like {rank[0][1]} ({rank[0][0]:.2f}; next {rank[1][0]:.2f})" if len(rank) > 1 else f"looks like {rank[0][1]}", rank[0][0]))
        else:
            left.append(p)
    if left:
        vecs = np.array([p.vec for p in left])
        for g in cluster(vecs, st["cluster"]):
            if len(g) >= st["minCluster"] or singles:
                members = [left[i] for i in g]
                near = space.ranking(nz(np.mean([m.vec for m in members], axis=0)))
                if near and near[0][0] >= st["castMerge"] and (near[0][1].startswith("Angels/") or is_sister(near[0][1])):
                    moves += [Move(m, near[0][1], f"is {near[0][1]} ({near[0][0]:.2f}; a group of {len(members)})", near[0][0]) for m in members]
                    continue
                name = invent_name("|".join(sorted(m.sha for m in members)), taken | {m.to.split("/", 1)[-1] for m in moves})
                new = unassigned_home(name, len(members))
                taken = taken | {name}
                note = f"; alike {near[0][1]} ({near[0][0]:.2f})" if near and near[0][0] >= st["alike"] else ""
                what = f"one new person ({len(members)} photos{note})" if len(members) >= st["minCluster"] else f"a face that matches nobody{note}"
                for m in members:
                    moves.append(Move(m, new, what, None))
    return moves


def record_history(done, work):
    """done: [(Move, source folder)] that really moved. Each destination person folder gets one dated line per source (the pool, Various, keeps no file);
    a new folder takes the name its source had when the whole source moved in, else the invented one it was given."""
    groups = collections.OrderedDict()
    for m, src in done:
        groups.setdefault((m.to, m.bucket, str(src)), []).append(m)
    for (to, bucket, src), ms in groups.items():
        if to.split("/")[-1].lower() == "various" or to.startswith("_junk") or (to.startswith("Artists/") and to.count("/") == 1):
            continue  # the pool, the junk and an artist's own gallery are not people: no z_ file
        dst = pathlib.Path(work) / to
        src = pathlib.Path(src)
        whole = not any(originals.images(src / sub) for sub in ("gallery", "review"))  # only a folder that moved out entirely passes her name on; a few photos split off a sister are someone else
        inherited = None if src.name.lower() == "various" or not whole else people.name_of(src)
        where = src.relative_to(work).as_posix() if src.is_relative_to(work) else src.name
        if inherited and inherited.lower() != src.name.lower():
            where += f" ({inherited})"
        review = " into review" if bucket == "review" else ""
        people.note(dst, f"+{len(ms)}{review} from {where}: {ms[0].reason}", name=inherited or dst.name)


def execute(moves, work, apply, cache, log=True):
    """Move the files into <to>/<bucket> (gallery, or review for photos to look at; a duplicate of what is already there goes to the source folder's gallery_org in _archive, a different file with the same name is kept under a new one).
    Each destination person folder records the move in its z_ file."""
    batch = {"id": datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), "moves": []}
    made, done = 0, []
    for m in moves:
        src = m.photo.path
        if apart(m.photo.key, m.to) and not m.force:
            print(f"  kept apart: {src.name} would go from {m.photo.key} to {m.to} (prospects and artists are never mixed); it stays")
            continue
        dest_dir = pathlib.Path(work) / m.to / m.bucket
        dst = dest_dir / src.name
        if dst == src:
            continue
        if apply:
            dest_dir.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                if cache.sha(dst) == m.photo.sha:
                    keep = originals.archive_dir(src.parent.parent, work, "gallery_org")
                    keep.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(keep / src.name))
                    print(f"  duplicate already in {m.to}: {src.name} set aside in _archive")
                    continue
                dst = dest_dir / f"{src.stem}_{m.photo.sha[:6]}{src.suffix}"
            shutil.move(str(src), str(dst))
            batch["moves"].append({"from": str(src), "to": str(dst), "sha": m.photo.sha})
            done.append((m, src.parent.parent))
        made += 1
    if apply:
        record_history(done, work)
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
    st["poolHome"] = next((k for k in st["pool"] if (work / k / "gallery").is_dir()), st["pool"][0])
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


def cmd_audit_core(args):
    cfg, st, work, cache, space = build(args)
    catalog = metadata.load_catalog()
    id_counts = collections.Counter(
        photo_id for photo_id in (metadata.photo_id_from_name(p.name) for p in space.photos) if photo_id
    )
    people_by_folder = collections.defaultdict(list)
    for person_id, person in catalog["people"].items():
        people_by_folder[person["folder"]].append((person_id, person))
    ambiguous_ids = {photo_id for photo_id, count in id_counts.items() if count > 1}
    protected_ids, stale_ids = set(), set()
    for photo in space.photos:
        photo_id = metadata.photo_id_from_name(photo.name)
        if not photo_id or photo_id not in catalog["photos"] or photo_id in ambiguous_ids:
            continue
        photo_record = catalog["photos"][photo_id]
        if metadata.content_sha256(photo.path) != photo_record["contentSha256"]:
            stale_ids.add(photo_id)
        elif photo_record["protected"]:
            protected_ids.add(photo_id)

    names = {name.lower() for name in (args.names or [])}
    person_keys = sorted({photo.key for photo in space.photos if not matches(photo.key, st["mixed"])})
    keys = [
        key for key in person_keys
        if (not names or key.split("/")[-1].lower() in names)
        and (not args.group or key.split("/", 1)[0].lower() == args.group.lower())
    ]
    print(
        f"Read-only identity-core audit: {len(keys)} folder(s); "
        f"current low-score threshold {st['odd']:.2f}, keep threshold {args.keep:.2f}"
    )
    print("No images are moved. The embedding cache may be updated during the scan.")
    if not names and not args.group:
        active_folders = set(person_keys)
        for person in catalog["people"].values():
            if person["folder"] not in active_folders:
                print(
                    f"Catalogue folder not found: {person['displayName']} -> {person['folder']}; "
                    "identity decisions are not applied"
                )
    for key in keys:
        folder_photos = [p for p in space.photos if p.key == key]
        usable = [p for p in folder_photos if p.usable(st["minFace"])]
        records = people_by_folder.get(key, [])
        folder_conflict = len(records) > 1
        person = records[0][1] if len(records) == 1 else None
        anchor_ids = set(person["identityAnchors"]) if person else set()
        usable_ids = {metadata.photo_id_from_name(photo.name) for photo in usable}
        effective_anchors = (anchor_ids & usable_ids) - stale_ids - ambiguous_ids

        if folder_conflict:
            print(f"\n{key}: catalogue conflict ({len(records)} people records); anchor decisions ignored")
        else:
            mode = "trusted anchors" if effective_anchors else "provisional"
            print(f"\n{key}: {len(folder_photos)} photo(s), {len(usable)} usable; {mode} core")
        if not records:
            print("  no catalogue person record; this is a provisional audit")

        photo_ids = [metadata.photo_id_from_name(photo.name) for photo in usable]
        result = audit_person(
            np.array([photo.vec for photo in usable]),
            photo_ids,
            anchor_ids=anchor_ids if not folder_conflict else (),
            protected_ids=protected_ids,
            stale_ids=stale_ids,
            ambiguous_ids=ambiguous_ids,
        )
        present_ids = {metadata.photo_id_from_name(photo.name) for photo in folder_photos}
        missing_anchors = sorted(anchor_ids - present_ids)
        if missing_anchors:
            print(f"  catalogue anchors not found in this folder: {', '.join(missing_anchors)}")
        unusable_anchors = sorted((anchor_ids & present_ids) - set(photo_ids))
        if unusable_anchors:
            print(f"  catalogue anchors not usable for scoring: {', '.join(unusable_anchors)}")
        if result["mode"] == "none":
            print("  no eligible core; add usable photos or resolve stale/ambiguous metadata")
        else:
            kind = "trusted" if result["mode"] == "trusted" else "provisional"
            core_names = [usable[i].name for i in result["core_indices"]]
            print(
                f"  {kind} core: {len(core_names)} photo(s)"
                + ("" if result["sufficient"] else " (below the 3-photo audit minimum)")
            )
            if core_names:
                print("  core members: " + ", ".join(core_names))

        core_indices = set(result["core_indices"])
        score_by_photo = {id(photo): result["scores"][i] for i, photo in enumerate(usable)}
        index_by_photo = {id(photo): i for i, photo in enumerate(usable)}

        def photo_row(photo):
            photo_id = metadata.photo_id_from_name(photo.name)
            score = score_by_photo.get(id(photo))
            index = index_by_photo.get(id(photo))
            if photo_id in stale_ids:
                reason = "stale metadata; anchor/protection ignored"
            elif photo_id in ambiguous_ids:
                reason = "duplicate stable photo ID; excluded from core and catalogue decisions"
            elif photo_id in anchor_ids and index is None:
                reason = "anchor file not usable for scoring"
            elif index is not None and index in result["anchor_indices"]:
                reason = "trusted identity anchor"
            elif photo_id in protected_ids:
                reason = "protected-only; excluded from core"
            elif not photo.usable(st["minFace"]):
                reason = "not usable for face scoring"
            elif score is None:
                reason = "no independent core score"
            elif not result["sufficient"]:
                reason = "small core; score only, no outlier suggestion"
            elif key.startswith("Prospects/") and score < st["odd"]:
                reason = "possible Prospect outlier; report only"
            elif key.startswith("Prospects/") and score < args.keep:
                reason = "borderline Prospect; inspect only"
            elif score < st["odd"]:
                reason = "low score; inspect only, no automatic move"
            elif index in core_indices:
                reason = "provisional core member"
            else:
                reason = "consistent with core"
            return score, photo.name, reason

        ordered = sorted((photo_row(photo) for photo in folder_photos),
                         key=lambda row: (row[0] is None, row[0] if row[0] is not None else 0, row[1].casefold()))
        for rank, (score, name, reason) in enumerate(ordered, 1):
            score_text = "--" if score is None else f"{score:.2f}"
            print(f"  {rank:3}. {score_text:>5}  {name}  [{reason}]")


def cmd_calibrate(args):
    cfg, st, work, cache, space = build(args)
    right = wrong = total = ok = 0
    own, oth = [], []
    for k in space.keys:
        ps = space.by_key[k]
        if len(ps) < 2:
            continue
        for p in ps:
            rank = space.ranking(p.vec, skip=p, own=k, source=k)
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
        if "Angels" in (ga, gb) and (ga in cw.SISTER_ROOTS or gb in cw.SISTER_ROOTS):
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
    other_of = lambda p, s: next((r for r in space.ranking(p.vec, skip=p, own=key, source=key) if r[1] != key), None)  # noqa: E731
    shown = scored if args.all else odd + mid
    if shown:
        print("\n  photos to check (lowest first):")
        for s, p in shown:
            o = other_of(p, s)
            note = f"  [{p.faces} faces in the picture]" if p.faces > 1 else ""
            if s < st["odd"]:
                dest = o[1] if o and o[0] >= st["assign"] else f"{pool_home(st)} (holding)"
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
        moves.append(Move(p, o[1] if o and o[0] >= st["assign"] else pool_home(st), f"looks like someone else than the rest of {key} ({s:.2f})"))
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
    if args.assign:
        st["assign"] = args.assign
    taken = {name.split("/")[-1] for _, name, _ in cw.photo_folders(cfg, work)}
    moves = plan_sort(space, st, cfg, taken, singles=args.singles)
    origins = note_origins(work)
    home = [p for p in space.photos if matches(p.key, st["pool"]) and photo_id(p.name) in origins]
    if home:
        gone = {id(p) for p in home}
        moves = [m for m in moves if id(m.photo) not in gone]
        moves += [Move(p, f"Artists/{origins[photo_id(p.name)]}", f"came from the artist {origins[photo_id(p.name)]}", force=True) for p in home]
        print(f"{len(home)} photo(s) in the pool came from an artist and go back to that artist's gallery")
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


def cmd_pullback(args):
    """Send Prospect and Potential folders back to Various so the next `sort` places their photos again."""
    cfg, st, work, cache, space = build(args)
    chosen = chosen_keys(cfg)
    wanted = {n.lower() for n in (args.names or [])}
    keys = []
    for k in space.keys:
        if not k.startswith(("Prospects/", "Potentials/")):
            continue
        n = len(originals.images(work / k / "gallery"))
        if args.all or k.split("/")[1].lower() in wanted or (args.small is not None and n <= args.small):
            keys.append(k)
    unknown = wanted - {k.split("/")[1].lower() for k in keys}
    if unknown:
        print("not a prospect folder: " + ", ".join(sorted(unknown)))
    held = [k for k in keys if any(cw.photo_key(p.name) in chosen for p in space.by_key[k])]
    keys = [k for k in keys if k not in held]
    for k in held:
        print(f"  kept: {k} holds a chosen photo")
    moves = [Move(p, pool_home(st), f"pulled back from {k.split('/', 1)[1]} to be sorted again") for k in keys for p in space.by_key[k]]
    print(f"{len(keys)} prospect folder(s), {len(moves)} photo(s) go back to {pool_home(st)}: " + ", ".join(k.split("/", 1)[1] for k in keys[:20]) + (" ..." if len(keys) > 20 else ""))
    if not moves:
        return
    if not args.apply:
        print("preview only; add --apply to move them, then run `likeness sort --singles` (or bin\\library.cmd)")
        return
    n = execute(moves, work, True, cache)
    gone = retire_empty(work, keys)
    if gone:
        print("emptied folders moved to _retired: " + ", ".join(gone))
    print(f"{n} photo(s) moved")
    after_moves(args, n > 0)


def cmd_merge(args, retire=False):
    cfg, st, work, cache, space = build(args)
    src, photos = whole_folder(space, cfg, args.a if not retire else args.name)
    to = pool_home(st) if retire else folder_key(space, args.b)
    if to == src:
        sys.exit("source and destination are the same folder")
    chosen = chosen_keys(cfg)
    if apart(src, to):
        sys.exit(f"{src} and {to} are not merged: prospects and artists come from different places and are kept apart")
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
        if not retire:
            gone = retire_empty(work, [src], keep={k for k in space.keys if k.startswith("Angels/") or is_sister(k)})
            if gone:
                print("emptied folder moved to _retired: " + ", ".join(gone))
        after_moves(args, n > 0)
    else:
        print("preview only; add --apply to move them")


def cmd_archive_list(args):
    """Archive listed Prospect or Artist people as whole folders, preserving photos, derived files and z_ history."""
    cfg = cw.load_cfg()
    work = pathlib.Path(args.root) if args.root else cw.work_root(cfg)
    list_path = pathlib.Path(args.list)
    if not list_path.is_file():
        sys.exit(f"archive list not found: {list_path}")
    lines = list_path.read_text(encoding="utf-8-sig").splitlines()
    entries, seen = [], set()
    for line_number, line in enumerate(lines):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"\s*-\s+\[([ xX])\]\s+(.+?)\s*", line)
        if not match:
            sys.exit(f"{list_path}:{line_number + 1}: expected a Markdown checkbox such as '- [ ] Prospects/Name'")
        if match[1].lower() == "x":
            continue
        relative = pathlib.Path(match[2].strip().strip("`"))
        parts = relative.parts
        is_prospect = len(parts) == 2 and parts[0].casefold() in ("prospects", "potentials") and parts[1].casefold() != "various"
        is_artist_person = len(parts) == 3 and parts[0].casefold() == "artists"
        if relative.is_absolute() or ".." in parts or not (is_prospect or is_artist_person):
            sys.exit(f"{list_path}:{line_number + 1}: use Prospects/Name, Potentials/Name or Artists/Artist/Person")
        key = "/".join(parts).casefold()
        if key in seen:
            sys.exit(f"{list_path}:{line_number + 1}: duplicate folder {relative.as_posix()}")
        seen.add(key)
        source = (work / relative).resolve()
        if not source.is_relative_to(work.resolve()):
            sys.exit(f"{list_path}:{line_number + 1}: folder is outside the photo library")
        if not source.is_dir():
            sys.exit(f"{list_path}:{line_number + 1}: active person folder not found: {relative.as_posix()}")
        destination = work / "_retired" / relative
        if destination.exists():
            sys.exit(f"{list_path}:{line_number + 1}: archive destination already exists: {destination}")
        entries.append({"line": line_number, "relative": relative, "source": source, "destination": destination})

    if not entries:
        print("no unchecked people to archive")
        return

    selected = collections.defaultdict(list)

    def register_selection(ref, name):
        key = cw.photo_key(name)
        if key:
            selected[("key", key)].append(ref)
        selected[("name", pathlib.Path(name).name.casefold())].append(ref)

    for hero, name in cfg.get("photos", {}).items():
        register_selection(hero, name)
    for flow, spec in cfg.get("flows", {}).items():
        for hero, name in spec.get("photos", {}).items():
            register_selection(f"{flow}/{hero}", name)

    for entry in entries:
        photos = [p for bucket in ("gallery", "review") for p in originals.images(entry["source"] / bucket)]
        refs = set()
        for photo in photos:
            key = cw.photo_key(photo.name)
            if key:
                refs.update(selected.get(("key", key), []))
            refs.update(selected.get(("name", photo.name.casefold()), []))
        if refs:
            sys.exit(f"{entry['relative'].as_posix()} has a photo selected by active workflows ({', '.join(sorted(refs))}); change those inputs first")
        entry["photos"] = len(photos)

    print(f"{len(entries)} person folder(s) to archive:")
    for entry in entries:
        print(f"  {entry['relative'].as_posix()} -> _retired/{entry['relative'].as_posix()} ({entry['photos']} photo(s))")
    if not args.apply:
        print("preview only; add --apply to move the folders and mark the list entries complete")
        return

    temp_list = list_path.with_name(list_path.name + ".tmp")
    if temp_list.exists():
        sys.exit(f"cannot archive: checklist temporary file already exists: {temp_list}")
    updated = list(lines)
    for entry in entries:
        updated[entry["line"]] = re.sub(r"^(\s*-\s*)\[\s*\]", r"\1[x]", updated[entry["line"]], count=1)
    try:
        temp_list.write_text("\n".join(updated) + "\n", encoding="utf-8")
    except OSError as exc:
        sys.exit(f"cannot stage checklist update: {exc}")

    cache = Cache(args.cache or DATA / "likeness_cache.json")
    retired_hashes = set()
    source_paths = [entry["source"] for entry in entries]
    for entry in entries:
        for bucket in ("gallery", "review"):
            for photo in originals.images(entry["source"] / bucket):
                retired_hashes.add(hashlib.sha1(photo.read_bytes()).hexdigest())

    moved = []
    try:
        for entry in entries:
            entry["destination"].parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(entry["source"]), str(entry["destination"]))
            moved.append(entry)
        for cached_path in list(cache.stat):
            path = pathlib.Path(cached_path)
            if any(path == source or path.is_relative_to(source) for source in source_paths):
                cache.stat.pop(cached_path, None)
        for sha in retired_hashes:
            cache.emb.pop(sha, None)
        cache.save()
        temp_list.replace(list_path)
    except OSError as exc:
        rollback_errors = []
        for entry in reversed(moved):
            try:
                if entry["destination"].exists():
                    entry["source"].parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(entry["destination"]), str(entry["source"]))
            except OSError as rollback_error:
                rollback_errors.append(f"{entry['relative'].as_posix()}: {rollback_error}")
        if temp_list.exists():
            temp_list.unlink()
        if rollback_errors:
            sys.exit(f"archive stopped ({exc}); rollback also failed: {'; '.join(rollback_errors)}")
        sys.exit(f"archive stopped and moved folders were restored: {exc}")

    print(f"{len(entries)} person folder(s) archived; checklist updated: {list_path}")


def cmd_promote(args):
    """Swap a Prospect into an Angel folder and return the existing person to Prospects or Potentials by usable count."""
    cfg, st, work, cache, space = build(args)
    prospect = folder_key(space, args.prospect)
    if not prospect.startswith("Prospects/") or prospect == "Prospects/Various":
        sys.exit("promotion source must be a named Prospects folder")
    hero = next((name for name in cfg.get("photos", {}) if name.casefold() == args.hero.casefold()), None)
    if not hero:
        sys.exit(f"unknown hero '{args.hero}'; known: {', '.join(cfg.get('photos', {}))}")
    source = work / prospect
    current = work / "Angels" / hero
    if not current.is_dir():
        sys.exit(f"current Angel folder not found: {current}")
    if source.resolve() == current.resolve():
        sys.exit("the Prospect and Angel folders are the same")
    current_name = people.name_of(current) or current.name
    current_key = f"Angels/{hero}"
    returned_root = "Prospects" if candidate_photo_count(space, current_key, st) >= 5 else "Potentials"
    returned = work / returned_root / current_name
    if returned.resolve() == source.resolve():
        sys.exit(f"cannot swap folders: the current Angel and source Prospect would share {returned}")
    if returned.exists():
        sys.exit(f"cannot return the current Angel: Prospect folder already exists: {returned}")
    centroid = space.centroid(prospect)
    chosen = best_photo(space, prospect, centroid) if centroid is not None else None
    if chosen is None:
        sys.exit(f"no usable source photo found in {prospect}")
    old_photo = cfg["photos"][hero]
    old_flow_photos = {
        flow: spec["photos"][hero]
        for flow, spec in cfg.get("flows", {}).items()
        if hero in spec.get("photos", {})
    }
    print(f"{prospect} -> Angels/{hero} ({len(originals.images(source / 'gallery'))} gallery photo(s))")
    print(f"Angels/{hero} -> {returned_root}/{current_name} ({len(originals.images(current / 'gallery'))} gallery photo(s))")
    print(f"  selected source photo: {chosen.name}")
    if old_flow_photos:
        print(f"  flow-specific inputs to refresh: {', '.join(old_flow_photos)}")
    if not args.apply:
        print("preview only; add --apply to swap folders, update photo selections, refresh inputs and regenerate derived copies")
        return

    sha = chosen.sha
    moved_current = False
    try:
        returned.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(current), str(returned))
        moved_current = True
        shutil.move(str(source), str(current))
    except OSError as exc:
        if moved_current:
            try:
                shutil.move(str(returned), str(current))
            except OSError as rollback_error:
                sys.exit(f"promotion stopped ({exc}); current Angel rollback failed: {rollback_error}")
        sys.exit(f"promotion stopped; folder moves were rolled back: {exc}")

    people.note(current, f"now the Angel {hero}; promoted from Prospects")
    people.note(returned, f"returned to {returned_root}; replaced as {hero} by {people.name_of(current) or prospect.split('/')[-1]}")
    for cached_path in list(cache.stat):
        path = pathlib.Path(cached_path)
        if path == source or path.is_relative_to(source) or path == current or path.is_relative_to(current) or path == returned or path.is_relative_to(returned):
            cache.stat.pop(cached_path, None)
    cache.save()

    print("\nrunning originals (rename, scale, prune, re-point) ...")
    originals.main(["--apply", "--root", str(work), "--only", hero, "--only", current_name])
    chosen_path = next((p for p in originals.images(current / "gallery") if hashlib.sha1(p.read_bytes()).hexdigest() == sha), None)
    if chosen_path is None:
        sys.exit(f"promotion folders updated, but selected photo {chosen.name} was not found after originals; choose a photo with inputs set {hero}")
    width, height = cfg.get("standardSize") or (944, 1104)
    scaled = current / f"gallery_{width}x{height}" / f"{chosen_path.stem}_{width}x{height}.png"
    if not scaled.is_file():
        sys.exit(f"promotion folders updated, but selected scaled photo is missing: {scaled}")

    cfg = cw.load_cfg()
    cw.repoint_photos(cfg, {hero: (old_photo, scaled)}, False)
    refreshed_cfg = cw.load_cfg()
    for flow, previous in old_flow_photos.items():
        if cw.photo_key(previous) != cw.photo_key(old_photo):
            continue
        frame = current / f"frame_{width}x{height}" / f"{chosen_path.stem}_frame_{width}x{height}.png"
        if not frame.is_file():
            print(f"  WARNING flow {flow}: new frame image is missing ({frame}); its previous photo setting was retained")
            continue
        refreshed_cfg.setdefault("flows", {}).setdefault(flow, {}).setdefault("photos", {})[hero] = frame.name
    cw.write_cfg(refreshed_cfg)
    reset_args = types.SimpleNamespace(root=None, hero=hero, stage=None, match=None, dry_run=False, force=True)
    cw.reset_inputs(refreshed_cfg, reset_args)
    print(f"promotion complete: run bin\\refresh.cmd {hero} to regenerate and deploy workflows to the home workspace")


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
    g = key.split("/")[0]
    return "sister" if g in cw.SISTER_ROOTS else "angel" if g == "Angels" else None


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
        out_thr = args.sister_out if is_sister(key) else st["odd"]  # a sister's folder only loses photos that are clearly someone else
        mine, keep = [], 0
        for p, s in zip(ps, scores):
            if id(p) in protected or s >= args.keep:
                keep += 1
            elif s >= out_thr or p.faces > 1 or ident["conflict"]:
                mine.append(Move(p, key, f"borderline for {key} ({s:.2f})", s, bucket="review"))
            else:
                rank = [r for r in space.ranking(p.vec, skip=p, own=key, source=key) if r[1] != key]
                dest = rank[0][1] if rank and rank[0][0] >= st["assign"] and (len(rank) < 2 or rank[0][0] - rank[1][0] >= st["margin"]) else pool_home(st)
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


PHOTO_ID = re.compile(r"(image_\d+|shot_\d{14}|pic_[0-9a-f]+)", re.I)


def photo_id(name):
    m = PHOTO_ID.search(name)
    return m[1].lower() if m else None


def note_origins(work, extra=None):
    """{photo id: artist} kept in <work>/_origins.json: which artist every photo of an artist came from. The id survives a rename, a move into a person's folder and a crop, so a photo that
    turns up again in Various, or in _junk, can go back to its artist. The first artist recorded for an id wins. extra: more {id: artist} (a backup)."""
    path = pathlib.Path(work) / "_origins.json"
    known = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    seen = dict(extra or {})
    root = pathlib.Path(work) / "Artists"
    for g in sorted(root.glob("*/gallery")) + sorted(root.glob("*/*/gallery")):
        artist = g.relative_to(root).parts[0]
        for f in originals.images(g):
            if photo_id(f.name):
                seen.setdefault(photo_id(f.name), artist)
    new = {k: v for k, v in seen.items() if k not in known}
    if new:
        known.update(new)
        path.write_text(json.dumps(dict(sorted(known.items())), indent=0), encoding="utf-8")
    return known


def cmd_group(args):
    cfg, st, work, cache, space = build(args, with_mixed=True)
    note_origins(work)
    taken = {name.split("/")[-1] for _, name, _ in cw.photo_folders(cfg, work)}
    minc = args.min_photos or st["minCluster"]
    names = [n.lower() for n in (args.names or [])]
    artists = sorted({p.key for p in space.photos if p.key.startswith("Artists/") and p.key.count("/") == 1})
    moves, sheet = [], []
    for ak in artists:
        if names and ak.split("/")[1].lower() not in names:
            continue
        ps = [p for p in space.photos if p.key == ak and p.usable(st["minFace"]) and not p.animals and not (p.faces > 1 and p.f2 >= st["multiFace"])]
        if len(ps) < (1 if args.singles else 2):
            continue
        groups = [g for g in cluster(np.array([p.vec for p in ps]), args.cluster or st["cluster"]) if len(g) >= 2]
        grouped = sum(len(g) for g in groups)
        print(f"{ak}: {len(ps)} usable photos -> {len(groups)} group(s) of 2+ ({grouped} photos); a new person needs {minc}+ photos that agree ({args.cohesion})")
        left = 0
        handled = set()
        for g in sorted(groups, key=len, reverse=True):
            members = [ps[i] for i in g]
            near = space.ranking(nz(np.mean([m.vec for m in members], axis=0)))
            same = next(((s, k) for s, k in near if k.startswith(ak + "/")), None)
            if same and same[0] >= args.join:  # the same woman as someone already in this artist's folder
                print(f"    {same[1]}: +{len(members)} photos ({same[0]:.2f})")
                moves += [Move(m, same[1], f"looks like {same[1]} ({same[0]:.2f}; a group of {len(members)} in {ak})", same[0]) for m in members]
                handled.update(id(m) for m in members)
                continue
            sims = np.array([m.vec for m in members]) @ np.array([m.vec for m in members]).T
            coh = float((sims.sum() - len(members)) / (len(members) * (len(members) - 1)))
            if len(members) < minc or coh < args.cohesion:
                print(f"    (left in the gallery: {len(members)} photos, agree {coh:.2f}{'; alike ' + near[0][1] + ' (%.2f)' % near[0][0] if near and near[0][0] >= st['alike'] else ''})")
                left += len(members)
                continue
            name = invent_name("|".join(sorted(m.sha for m in members)), taken)
            taken = taken | {name}
            note = f"; alike {near[0][1]} ({near[0][0]:.2f})" if near and near[0][0] >= st["alike"] else ""
            print(f"    {ak}/{name}: {len(members)} photos, agree {coh:.2f}{note}")
            moves += [Move(m, f"{ak}/{name}", f"one person in {ak} ({len(members)} photos{note})") for m in members]
            handled.update(id(m) for m in members)
            sheet.append((name, members[:10]))
        if left:
            print(f"    {left} photo(s) in groups too small or too loose {'are placed one by one' if args.singles else 'stay in the gallery'}")
        if args.singles:
            joined = new_single = 0
            for p in ps:
                if id(p) in handled or junk_reason(p, st) or cw.photo_key(p.name) in chosen_keys(cfg):
                    continue
                rank = [(s, k) for s, k in space.ranking(p.vec) if k.startswith(ak + "/")]
                if rank and rank[0][0] >= args.single_join and (len(rank) < 2 or rank[0][0] - rank[1][0] >= 0.05):
                    moves.append(Move(p, rank[0][1], f"a single photo that looks like {rank[0][1].split('/')[-1]} ({rank[0][0]:.2f}; from the gallery of {ak})", rank[0][0]))
                    joined += 1
                    continue
                name = invent_name(p.sha, taken)
                taken = taken | {name}
                moves.append(Move(p, f"{ak}/{name}", f"a single photo of one person in {ak}; nobody there looks like her"))
                new_single += 1
            print(f"    singles: {joined} joined a person of this artist, {new_single} got a folder of their own")
    if args.sheet and sheet:
        make_sheet(sheet, args.sheet)
    if args.apply and moves:
        n = execute(moves, work, True, cache)
        print(f"{n} photo(s) moved")
        after_moves(args, n > 0)
    elif moves:
        print("preview only; add --apply to group them")


def plan_artists(space, st, origin, assign, keep, margin, only=None):
    """Moves that put every artist photo under the artist it came from (origin: {sha: artist}) and then under the person of that artist it looks like.
    A person is the core of the photos that came from her artist; a photo with a second face, no usable face or no clear match stays in the artist's own gallery.
    A photo already in a person's folder stays there when it still looks like her (keep) and nobody else does."""
    ph = [p for p in space.photos if p.key.startswith("Artists/")]
    home = {p.sha: origin.get(p.sha) or origin.get(photo_id(p.name)) or p.key.split("/")[1] for p in ph}
    solo = lambda p: p.usable(st["minFace"]) and not p.animals and not (p.faces > 1 and p.f2 >= st["multiFace"])  # noqa: E731
    people_of = collections.defaultdict(dict)  # artist -> {person folder name: (core photos, centroid)}
    by_folder = collections.defaultdict(list)
    for p in ph:
        if p.key.count("/") == 2:
            by_folder[p.key].append(p)
    for key, ps in by_folder.items():
        counts = collections.Counter(home[p.sha] for p in ps)
        artist = counts.most_common(1)[0][0]
        mine = [p for p in ps if home[p.sha] == artist and solo(p)]
        if len(mine) >= 2:
            _, core, c = core_scores(np.array([p.vec for p in mine]))
            people_of[artist][key.split("/")[2]] = ([mine[i] for i in core], c)
    moves, stay, rows = [], collections.Counter(), collections.defaultdict(collections.Counter)
    for p in ph:
        if only is not None and p.sha not in only:
            continue
        artist = home[p.sha]
        dest, why, score = f"Artists/{artist}", "no clear person", None
        if not p.usable(st["minFace"]):
            why = "no usable face"
        elif not solo(p):
            why = "more than one person"
        else:
            rank = []
            for name, (core, c) in people_of[artist].items():
                mine = [q for q in core if q is not p]
                cc = nz(np.mean([q.vec for q in mine], axis=0)) if mine and len(mine) != len(core) else c
                rank.append((float(p.vec @ cc), name))
            rank.sort(reverse=True)
            if rank:
                best, name = rank[0]
                gap = best - rank[1][0] if len(rank) > 1 else 1.0
                here = p.key == f"Artists/{artist}/{name}"
                if gap >= margin and (best >= assign or (here and best >= keep)):
                    dest, why, score = f"Artists/{artist}/{name}", f"looks like {name} ({best:.2f}; next {rank[1][0]:.2f})" if len(rank) > 1 else f"looks like {name} ({best:.2f})", best
        rows[artist][dest.split("/", 2)[2] if dest.count("/") == 2 else "(artist gallery)"] += 1
        if dest == p.key:
            stay[artist] += 1
        else:
            moves.append(Move(p, dest, f"{why}; from {p.key}", score))
    return moves, rows, stay


def cmd_artists(args):
    """Reset the artists' folders: every photo goes back under the artist it came from in the backup, then to the person of that artist it looks like."""
    cfg, st, work, cache, space = build(args, with_mixed=True)
    src = pathlib.Path(args.origin)
    if not src.is_dir():
        sys.exit(f"{src} is not a folder; pass the backup's Artists folder with --from")
    origin = {}
    for d, _, files in os.walk(src):
        for f in files:
            p = pathlib.Path(d) / f
            if p.suffix.lower() in originals.IMAGE_EXT:
                artist = pathlib.Path(d).relative_to(src).parts[0]
                origin[cache.sha(p)] = artist
                if photo_id(p.name):
                    origin[photo_id(p.name)] = artist
    origin.update(note_origins(work, {k: v for k, v in origin.items() if not len(k) == 40}))
    only = None
    if args.junk:
        back = [(f, origin.get(cache.sha(f)) or origin.get(photo_id(f.name))) for f in originals.images(work / "_junk" / "Artists")]
        back = [(f, a) for f, a in back if a]
        print(f"{len(back)} photo(s) in _junk/Artists came from a known artist and {'go back' if args.apply else 'would go back'} to that artist's gallery (run `likeness junk` afterwards to set aside again what the rules still call junk)")
        if not args.apply:
            return
        only = {cache.sha(f) for f, _ in back}
        for f, artist in back:
            dest = work / "Artists" / artist / "gallery"
            dest.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(dest / f.name))
        cfg, st, work, cache, space = build(args, with_mixed=True)
    if args.gallery:
        only = (only or set()) | {p.sha for p in space.photos if p.key.startswith("Artists/") and p.key.count("/") == 1}
    moves, rows, stay = plan_artists(space, st, origin, args.assign or st["assign"], args.keep, args.margin, only)
    for artist in sorted(rows):
        print(f"{artist}: {stay[artist]} photo(s) stay, {sum(rows[artist].values()) - stay[artist]} move")
        for name, n in rows[artist].most_common():
            print(f"    {name}: {n}")
    print(f"\n{len(moves)} photo(s) to move")
    if args.apply and (moves or only):
        n = execute(moves, work, True, cache) if moves else 0
        print(f"{n} photo(s) moved")
        after_moves(args, True)
    elif moves:
        print("preview only; add --apply to move them")


def crop_box(size, main, others, min_ratio=0.1, aspect=(0.45, 1.8)):
    """The largest rectangle (left, top, right, bottom) of a picture that keeps the main face with its hair and shoulders and cuts away every other face, or None.
    main and others are (x, y, w, h) in pixels. A cut runs half way between the faces; a face much smaller than the main one (a passer-by) is not cut away."""
    W, H = size
    x, y, w, h = main
    need = (max(0, x - 0.35 * w), max(0, y - 0.6 * h), min(W, x + 1.35 * w), min(H, y + 1.8 * h))
    blocks = [(ox - 0.1 * ow, oy - 0.1 * oh, ox + 1.1 * ow, oy + 1.1 * oh) for ox, oy, ow, oh in others if ow * oh >= min_ratio * w * h]
    if len(blocks) > 5:
        return None
    options = []
    for b in blocks:
        opts = []
        if b[2] <= need[0]:
            opts.append(("l", (b[2] + need[0]) / 2))
        if b[0] >= need[2]:
            opts.append(("r", (b[0] + need[2]) / 2))
        if b[3] <= need[1]:
            opts.append(("t", (b[3] + need[1]) / 2))
        if b[1] >= need[3]:
            opts.append(("b", (b[1] + need[3]) / 2))
        if not opts:
            return None
        options.append(opts)
    best, area = None, 0
    for combo in itertools.product(*options):
        r = [0, 0, W, H]
        for side, at in combo:
            i = "ltrb".index(side)
            r[i] = max(r[i], at) if side in "lt" else min(r[i], at)
        cw_, ch_ = r[2] - r[0], r[3] - r[1]
        if cw_ <= 0 or ch_ <= 0 or not aspect[0] <= cw_ / ch_ <= aspect[1]:
            continue
        if cw_ * ch_ > area:
            best, area = r, cw_ * ch_
    return tuple(int(round(v)) for v in best) if best else None


def person_box(size, face, keep=0.7):
    """The part of a picture worth keeping around the main face (x, y, w, h in pixels): the hair above her, as much body as the picture has below, and about three and a half face widths either side
    (arms, a dress, a wide stance), so the background beside her goes. None when that is most of the picture anyway (keep: the share of the picture above which nothing is cut), and when her head
    is not in the upper part of the picture (she is lying or sitting low, or the picture is turned): then there is no telling where the body is."""
    W, H = size
    x, y, w, h = face
    if y + h / 2 > 0.4 * H:
        return None
    left, right = max(0.0, x + w / 2 - 3.6 * w), min(float(W), x + w / 2 + 3.6 * w)
    top = max(0.0, y - 1.2 * h)
    if (right - left) * (H - top) >= keep * W * H:
        return None
    return int(left), int(top), int(round(right)), H


def cmd_crop(args):
    """Cut a photo down to the person: the app's bars of a phone screenshot, other people and animals, and the background beside and above her. All of the body that is in the picture stays.
    The uncropped original is kept in _archive (gallery_uncropped), the cropped one takes its place under the same name. A prospect's photo whose other subject cannot be cut away is set aside in her review folder."""
    from PIL import Image
    cfg, st, work, cache, space = build(args, with_mixed=True)
    embed = args.embedder or Embedder()
    if args.undo:
        return undo_crop(work, args.apply)
    done, stuck = [], []
    for p in space.photos:
        if p.box is None or p.px < st["minFace"] or p.key.startswith("_"):
            continue
        reel = "_shot_" in p.name
        multi = p.faces > 1 and p.f2 >= st["multiFace"]
        try:
            with Image.open(p.path) as src:
                im = src.convert("RGB")
        except OSError:
            continue
        W, H = im.size
        why, region = [], (0, 0, W, H)
        if reel and screens.is_reel_ui(im):
            if not screens.head_clear(p.box):
                stuck.append((p, "the app's bars cover her head"))
                continue
            region = screens.clean_box(im.size)
            why.append("the app's bars")
        cut = im.crop(region)
        if multi or p.animals or region != (0, 0, W, H):
            humans, animals = embed.faces(cut)
        else:
            humans, animals = [(p.box[0] * W, p.box[1] * H, p.box[2] * W, p.box[3] * H)], []
        if not humans:
            continue
        main = humans[0]
        others = [f for f in humans[1:] if f[2] * f[3] >= st["multiFace"] * main[2] * main[3]] + animals
        if others:
            box = crop_box(cut.size, main, others)
            if box is None:
                stuck.append((p, "another person or an animal overlaps her"))
                continue
            if box != (0, 0) + cut.size:
                main = (main[0] - box[0], main[1] - box[1], main[2], main[3])
                region = (region[0] + box[0], region[1] + box[1], region[0] + box[2], region[1] + box[3])
                cut = cut.crop(box)
                why.append("other people and animals" if animals and len(humans) > 1 else "animals" if animals else "other people")
        bg = None if args.no_background else person_box(cut.size, main)
        if bg:
            region = (region[0] + bg[0], region[1] + bg[1], region[0] + bg[2], region[1] + bg[3])
            why.append("background")
        if why:
            done.append((p, region, " and ".join(why)))
    for p, region, why in done:
        print(f"  {p.key}/{p.name}: cut {why}  ->  {region[2] - region[0]}x{region[3] - region[1]}")
    review = [(p, r) for p, r in stuck if p.key.count("/") == 1 and p.key.split("/")[0] == "Prospects"]
    back = [(p, r) for p, r in stuck if p.key.count("/") == 2 and p.key.split("/")[0] == "Artists"]  # an artist's person: it goes back to the artist's own gallery
    for p, r in stuck:
        where = "  (set aside in her review folder)" if (p, r) in review else "  (back to the artist's gallery)" if (p, r) in back else ""
        print(f"  left as it is: {p.key}/{p.name}: {r}{where}")
    print(f"\n{len(done)} photo(s) to crop (the uncropped originals go to _archive); {len(review)} prospect photo(s) to her review folder; {len(back)} artist photo(s) back to the artist's gallery; {len(stuck) - len(review) - len(back)} left as they are")
    if not args.apply or not (done or review or back):
        if done or review or back:
            print("preview only; add --apply to do it")
        return
    batch = []
    log = DATA / "likeness_crops.json"
    DATA.mkdir(parents=True, exist_ok=True)
    old_log = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    entry = {"id": datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), "crops": batch}
    for p, region, why in done:
        with Image.open(p.path) as src:
            cut = src.convert("RGB").crop(region)
        keep = originals.archive_dir(p.path.parent.parent, work, "gallery_uncropped")
        keep.mkdir(parents=True, exist_ok=True)
        old = keep / p.path.name
        if old.exists():
            old = keep / f"{p.path.stem}_{p.sha[:6]}{p.path.suffix}"
        shutil.copy2(p.path, old)
        part = p.path.with_name(p.path.name + ".part")  # written whole, then swapped in: an interrupted run never leaves half a picture
        if p.path.suffix.lower() in (".jpg", ".jpeg"):
            cut.save(part, "JPEG", quality=95)
        else:
            cut.save(part, "PNG" if p.path.suffix.lower() == ".png" else None)
        os.replace(part, p.path)
        batch.append({"file": str(p.path), "kept": str(old)})
        log.write_text(json.dumps(old_log + [entry], indent=1), encoding="utf-8")  # after every photo: a run that is stopped loses no record of a crop
        if p.key.count("/") >= 1 and p.key != "Prospects/Various" and p.key.split("/")[0] != "Various" and not (p.key.startswith("Artists/") and p.key.count("/") == 1):
            people.note(work / p.key, f"cropped {p.name}: {why} cut away; the uncropped one is in _archive")
    print(f"{len(batch)} photo(s) cropped")
    if review:
        cleanup_hold(work, [p.sha for p, _ in review])
        n = execute([Move(p, p.key, f"needs a clean-up: {r}", bucket="review") for p, r in review], work, True, cache)
        print(f"{n} photo(s) set aside in their person's review folder")
    if back:
        n = execute([Move(p, "/".join(p.key.split("/")[:2]), f"could not be cleaned up ({r}); back to the artist's gallery for you to look at", force=True) for p, r in back], work, True, cache)
        print(f"{n} photo(s) back in their artist's gallery")
    after_moves(args, True)


def undo_crop(work, apply):
    log = DATA / "likeness_crops.json"
    data = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    if not data:
        print("no crops to undo")
        return
    batch = data[-1]
    print(f"last batch {batch['id']}: {len(batch['crops'])} photo(s) get their uncropped original back")
    if not apply:
        print("preview only; add --apply to put them back")
        return
    for c in batch["crops"]:
        if pathlib.Path(c["kept"]).exists():
            shutil.copy2(c["kept"], c["file"])
    log.write_text(json.dumps(data[:-1], indent=1), encoding="utf-8")
    after_moves(types.SimpleNamespace(no_originals=False, root=None), True)


def cmd_crops(args):
    """A page to look at every crop: the uncropped original next to the cropped photo, by root, from the crop log. `likeness crop --undo` reverses the last batch."""
    import base64
    import html
    import io
    from PIL import Image, ImageOps
    cfg = cw.load_cfg()
    work = pathlib.Path(args.root) if args.root else cw.work_root(cfg)
    log = DATA / "likeness_crops.json"
    batches = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    rows = collections.OrderedDict()
    for b in batches:
        for c in b["crops"]:
            f, k = pathlib.Path(c["file"]), pathlib.Path(c["kept"])
            if f.exists() and k.exists():
                try:
                    rel = f.relative_to(work)
                except ValueError:
                    continue
                rows.setdefault(rel.parts[0], {})[str(f)] = (rel.as_posix(), f, k)

    def thumb(path):
        with Image.open(path) as im:
            im = ImageOps.fit(ImageOps.exif_transpose(im).convert("RGB"), (150, 200), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=75)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    out = ["<!doctype html><html><head><meta charset='utf-8'><title>Crops</title><style>body{font-family:Segoe UI,Arial;margin:20px;background:#faf8f3}.p{display:inline-block;margin:6px;padding:6px;background:#fff;border:1px solid #ddd;font-size:11px;width:312px}.p img{width:150px;height:200px;margin-right:4px}</style></head><body><h1>Cropped photos</h1>",
           "<p>Left: the uncropped original (kept in _archive, gallery_uncropped). Right: what is in the library now. Undo the last batch with <code>likeness crop --undo --apply</code>.</p>"]
    total = 0
    for root, items in rows.items():
        out.append(f"<h2>{html.escape(root)} ({len(items)})</h2>")
        for rel, f, k in items.values():
            try:
                out.append(f"<div class='p'><img src='{thumb(k)}'><img src='{thumb(f)}'><br>{html.escape(rel.split('/', 1)[1])}</div>")
                total += 1
            except Exception:  # noqa: BLE001
                continue
    out.append("</body></html>")
    dest = pathlib.Path(args.out) if args.out else work / "_reports" / "library" / "crop_review.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(out), encoding="utf-8")
    print(f"{total} cropped photo(s) in {sum(len(v) for v in rows.values())} logged; written to {dest}")


def cmd_crosscheck(args):
    """Who looks like whom across the lines that are kept apart: one artist's people against another artist's, and prospects against artists' people. Nothing is moved."""
    cfg, st, work, cache, space = build(args)
    thr = args.min if args.min is not None else st["alike"]
    cents, pairs = space.pair_matrix()

    def artist(k):
        parts = k.split("/")
        return parts[1] if parts[0] == "Artists" and len(parts) == 3 else None
    rows = []
    for (a, b), s in pairs.items():
        if s < thr:
            continue
        aa, ab = artist(a), artist(b)
        if aa and ab and aa != ab:
            rows.append((s, "artist ~ artist", a, b))
        elif (aa and b.startswith(("Prospects/", "Potentials/"))) or (ab and a.startswith(("Prospects/", "Potentials/"))):
            rows.append((s, "prospect ~ artist", a, b))
    rows.sort(reverse=True)
    lines = [f"# Likeness across the lines that are kept apart ({datetime.date.today()})", "",
             f"Pairs of people from different artists, or a prospect and an artist's person, scoring {thr:.2f} or more (0.55 is about the same person; 0.30 to 0.45 very alike). Nothing was moved.", "",
             "| score | kind | one | other |", "| --- | --- | --- | --- |"]
    for s, kind, a, b in rows:
        lines.append(f"| {s:.2f} | {kind} | {a} ({len(space.by_key[a])}) | {b} ({len(space.by_key[b])}) |")
        print(f"  {s:.2f}  {kind:18} {a}  ~  {b}")
    out = pathlib.Path(args.out) if args.out else work / "_reports" / "library" / "crosscheck.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(rows)} pair(s); written to {out}")


def cmd_sisters(args):
    """Do the sisters read as one family? Drakness is the anchor; a sister who is too different (or too alike another) is a candidate to replace."""
    cfg, st, work, cache, space = build(args)
    rend = None if args.no_renders else Renders(cfg, cache, args.embedder or Embedder(), st, space)
    keys = [k for k in space.keys if is_sister(k)]
    anchor = next((k for k in keys if k.split("/")[-1].lower() == args.anchor_sister.lower()), "")
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
        cands = [k for k in space.keys if not is_sister(k) and len(space.by_key[k]) >= 3]
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


def cmd_retire_empty(args):
    """Archive empty Prospect and Potential folders with no original photos in gallery or review."""
    cfg = cw.load_cfg()
    st = settings(cfg)
    work = pathlib.Path(args.root) if args.root else cw.work_root(cfg)
    pool = {p.lower() for p in st["pool"]}
    keys = []
    for root_name in ("Prospects", "Potentials"):
        root = work / root_name
        folders = sorted(root.iterdir(), key=lambda folder: folder.name.casefold()) if root.is_dir() else []
        keys.extend(f"{root_name}/{folder.name}" for folder in folders
                    if folder.is_dir() and f"{root_name}/{folder.name}".lower() not in pool)
    candidates = []
    for key in keys:
        folder = work / key
        nested = any(child.is_dir() and (child / "gallery").is_dir() for child in folder.iterdir())
        if not nested and not any(originals.images(folder / sub) for sub in ("gallery", "review")):
            candidates.append(key)
    if not candidates:
        print("no empty Prospect or Potential folders")
        return 0
    print(("would archive" if not args.apply else "archiving") + " empty Prospect/Potential folders (no gallery or review photos):")
    for key in candidates:
        print(f"  {key} -> _retired/{key}")
    if args.apply:
        done = retire_empty(work, candidates)
        print(f"{len(done)} empty prospect folder(s) archived; nothing was deleted")
    else:
        print(f"{len(candidates)} folder(s); preview only (add --apply to archive)")
    return 0


def prime_score(p, c, size):
    """How good this photo is as the input of a 1_Prime (the photo becomes an A-pose figure): her face (score against her core), one clear face, some of the body in view,
    portrait, and enough pixels. Returns (score, notes)."""
    w, h = size
    face_h = (p.box[3] if p.box else 0.4)
    ident = float(p.vec @ c)
    clarity = min(p.px, 300) / 300 * 0.15
    body = (1 - min(1.0, face_h / 0.45)) * 0.12            # a head-and-shoulders crop gives the model less to work with than a half or full figure
    shape = -0.12 if w > h else -abs(w / h - 0.78) * 0.15
    res = min(1.0, (w * h) / (1000 * 1300)) * 0.08
    multi = -0.30 if p.faces > 1 else 0.0
    return ident + clarity + body + shape + res + multi, f"face {ident:.2f}, {p.px}px, {w}x{h}" + (", 2+ faces" if p.faces > 1 else "")


def cleanup_hold(work, add=()):
    """Content hashes of photos `crop` set aside in a review folder because they need a clean-up it could not do: `review` leaves them there (they look like her, which is why they are there)."""
    path = pathlib.Path(work) / "_cleanup_hold.json"
    held = set(json.loads(path.read_text(encoding="utf-8")) if path.exists() else [])
    if set(add) - held:
        held |= set(add)
        path.write_text(json.dumps(sorted(held)), encoding="utf-8")
    return held


def load_review(cfg, work, space, cache, embed, st, wanted=()):
    """[(folder key, file, Photo or None)] for every file in a person folder's review folder; None when the file has no usable face. Photos held for a clean-up (see cleanup_hold) are not listed."""
    out = []
    held = cleanup_hold(work)
    for group, name, folder in cw.photo_folders(cfg, work):
        key = f"{group}/{name}"
        if key not in space.by_key or (wanted and name.split("/")[-1].lower() not in wanted):
            continue
        for f in originals.images(folder / "review"):
            sha = cache.sha(f)
            if sha in held:
                continue
            if sha not in cache.emb:
                cache.emb[sha] = embed(f) or {"faces": -1}
            ph = Photo(f, group, name, sha, cache.emb[sha])
            if ph.usable(st["minFace"]):
                ph.vec = nz(ph.raw - space.mean)
            else:
                ph = None
            out.append((key, f, ph))
    cache.save()
    return out


def cmd_review(args):
    """The photos set aside in review folders: each one against her own folder and against everyone else, with a suggested action. A photo that is probably her goes back to her gallery (--back),
    one that clearly looks like someone else goes to that person (--send); the rest stay in review. With --out, a photo that is clearly not her (below the 'odd' score) and matches nobody
    becomes a new prospect (photos that look alike share one), whose z_ file says where she came from. Preview unless --apply."""
    cfg, st, work, cache, space = build(args)
    embed = args.embedder or Embedder()
    wanted = {n.lower() for n in (args.names or [])}
    moves, rows, sheet, strays = [], [], [], []
    for key, f, ph in load_review(cfg, work, space, cache, embed, st, wanted):
        if ph is None:
            rows.append((key, f.name, None, None, None, "no usable face: stays in review"))
            continue
        c = space.centroid(key)
        own = float(ph.vec @ c)
        rank = [r for r in space.ranking(ph.vec, source=key) if r[1] != key]
        other = rank[0] if rank else (0.0, "")
        second = rank[1][0] if len(rank) > 1 else -1.0
        if own >= args.back and own >= other[0]:
            action = f"back to {key.split('/', 1)[1]}"
            moves.append(Move(ph, key, f"review: probably {key.split('/', 1)[1]} ({own:.2f})", own))
        elif other[0] >= st["assign"] and other[0] - max(second, own) >= st["margin"]:
            action = f"send to {other[1]}"
            moves.append(Move(ph, other[1], f"review: looks like {other[1]} ({other[0]:.2f}; her own folder {own:.2f})", other[0]))
        elif args.out and own < st["odd"] and other[0] < st["assign"]:
            action = "new prospect"
            strays.append((key, ph, own))
        else:
            action = "stays in review"
        rows.append((key, f.name, own, other[1], other[0], action))
        sheet.append(ph)
    if strays:
        taken = {name.split("/")[-1] for _, name, _ in cw.photo_folders(cfg, work)}
        for g in cluster(np.array([p.vec for _, p, _ in strays]), st["cluster"]):
            members = [strays[i] for i in g]
            name = invent_name("|".join(sorted(p.sha for _, p, _ in members)), taken | {m.to.split("/", 1)[-1] for m in moves})
            taken = taken | {name}
            for key, ph, own in members:
                moves.append(Move(ph, new_home(key, name, len(members)), f"from {key.split('/', 1)[1]} review: clearly not her ({own:.2f})", None))
    print(f"{'folder':26} {'photo':44} {'her':>5}  {'looks most like':32} {'score':>5}  action")
    for key, fn, own, o, os_, act in rows:
        print(f"{key:26} {fn[:44]:44} {('%.2f' % own) if own is not None else '-':>5}  {(o or '-'):32} {('%.2f' % os_) if os_ is not None else '-':>5}  {act}")
    by = collections.Counter(r[5].split(" to ")[0] if " to " in r[5] else r[5] for r in rows)
    print(f"\n{len(rows)} photo(s) in review folders: " + ", ".join(f"{v} {k}" for k, v in by.most_common()))
    if args.sheet and sheet:
        make_sheet([(f"{p.key.split('/', 1)[1]}", [p]) for p in sheet[:40]], args.sheet)
    if not moves:
        return
    print_plan(moves, space, work)
    if args.apply:
        n = execute(moves, work, True, cache)
        print(f"{n} photo(s) moved")
        after_moves(args, n > 0)
    else:
        print("preview only; add --apply to move them")


def cmd_photos(args):
    """Pick the 1_Prime photo for every angel and sister: the best-scoring photo of the person in her folder. Favourites (likeness.keepPhoto) never change; others switch only when clearly better."""
    from PIL import Image
    cfg, st, work, cache, space = build(args)
    rend = None if args.no_renders else Renders(cfg, cache, args.embedder or Embedder(), st, space)
    keep = {h.lower() for h in st.get("keepPhoto", [])}
    chosen = cfg.get("photos", {})
    wanted = {n.lower() for n in (args.names or [])}
    rows, renames = [], {}
    for key in space.keys:
        group, hero = key.split("/")[0], key.split("/")[-1]
        if group not in ("Angels", *cw.SISTER_ROOTS) or (args.group and group.lower() != args.group.lower()) or (wanted and hero.lower() not in wanted):
            continue
        name = next((h for h in chosen if h.lower() == hero.lower()), None)
        if not name:
            continue
        ident = identity(space, cfg, st, rend, key)
        ps, scores, core, c = folder_core(space, key, ident)
        sizes = {}
        for p in ps:
            try:
                with Image.open(p.path) as im:
                    sizes[id(p)] = im.size
            except Exception:  # noqa: BLE001
                sizes[id(p)] = (1000, 1300)
        ranked = sorted(((prime_score(p, c, sizes[id(p)]), p) for p in ps), key=lambda t: -t[0][0])
        cur_key = cw.photo_key(chosen[name])
        cur = next(((s, p) for s, p in ranked if cw.photo_key(p.name) == cur_key), None)
        best_s, best = ranked[0]
        if hero.lower() in keep:
            rows.append((name, chosen[name], "kept: your favourite", cur[0][1] if cur else "", "", ""))
            continue
        why = ""
        if cur and (best_s[0] - cur[0][0]) < args.margin:
            rows.append((name, chosen[name], "kept (already one of the best)", cur[0][1], best.name, f"{best_s[0] - cur[0][0]:+.2f}"))
            continue
        if cur is None:
            why = "her chosen photo is not in her folder"
        if group in cw.SISTER_ROOTS and not args.sisters:
            alt = f"; the best other photo in her folder scores {best_s[0] - cur[0][0]:+.2f} but is a different look: {best.name}" if cur and best_s[0] - cur[0][0] >= args.margin else ""
            rows.append((name, chosen[name], "kept: the sister's photo is your choice" + alt, cur[0][1] if cur else "", "", ""))
            continue
        scaled = best.path.parent.parent / f"gallery_{cfg['standardSize'][0]}x{cfg['standardSize'][1]}" / f"{best.path.stem}_{cfg['standardSize'][0]}x{cfg['standardSize'][1]}.png"
        rows.append((name, chosen[name], f"-> {best.name}", best_s[1], best.name, ("%+.2f" % (best_s[0] - cur[0][0])) if cur else why))
        if scaled.exists() and scaled.name != chosen[name]:
            renames[name] = (chosen[name], scaled)
    print(f"{'hero':10} {'now':46} {'decision':52} detail")
    for name, now, dec, detail, best, gain in rows:
        print(f"{name:10} {now[:46]:46} {dec[:52]:52} {detail}  {gain}")
    if args.sheet:
        sheet = []
        for name, (old, new) in renames.items():
            k = next((k for k in space.keys if k.split("/")[-1].lower() == name.lower()), None)
            now_p = next((p for p in space.by_key.get(k, []) if cw.photo_key(p.name) == cw.photo_key(old)), None)
            new_p = next((p for p in space.by_key.get(k, []) if cw.photo_key(p.name) == cw.photo_key(new.name)), None)
            sheet.append((f"{name}: now / new", [x for x in (now_p, new_p) if x]))
        if sheet:
            make_sheet(sheet, args.sheet)
    if not renames:
        print("\nnothing to change")
        return
    if not args.apply:
        print(f"\n{len(renames)} photo(s) would change; preview only, add --apply to set them in workspaces.json and the workflows")
        return
    touched = cw.repoint_photos(cfg, renames, False)
    print(f"\n{len(renames)} photo(s) set; workflows changed: " + (", ".join(f"{v} in {k}" for k, v in touched.items()) or "none"))


def artist_origin(work, key):
    """The artist person an angel folder was made from ('Artists/Pierre/Mara Locke'), or None: her z_ file says '+N from Artists/<artist>/<name>' and she still carries that name."""
    got = people.read(pathlib.Path(work) / key)
    if not got:
        return None
    name = got[0].lower()
    for ln in reversed(got[1]):
        m = re.search(r"\+\d+ from (Artists/[^:(]+?)(?: \(|:|$)", ln)
        if m and m[1].split("/")[-1].strip().lower() == name:
            return m[1].strip()
    return None


def cmd_pairs(args):
    """Pair every angel with the sister of her element from ALL the faces in the library (angels, prospects, grouped artists), similar to the sister but not the same, and not like anyone else."""
    cfg, st, work, cache, space = build(args)
    rend = None if args.no_renders else Renders(cfg, cache, args.embedder or Embedder(), st, space)
    pairs = dict(PAIRS)
    pairs.update(st.get("pairs", {}))
    low, high = st.get("pairLow", 0.15), st.get("pairHigh", 0.40)
    target = args.target if args.target is not None else st.get("pairTarget", 0.28)
    min_photos = args.min_photos if args.min_photos is not None else st.get("pairMinPhotos", 5)
    min_cohesion = args.min_cohesion if args.min_cohesion is not None else st.get("pairMinCohesion", 0.45)
    sis_key = {s: k for k in space.keys if is_sister(k) for s in [k.split("/")[-1]] if s in set(pairs.values())}
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
    # an angel who is an artist's person (Pierre's fantasy faces are for the art, not for the Prime photos) is replaced, and her photos go back to the artist
    artist_of = {k: a for k in angel_dir.values() for a in [artist_origin(work, k)] if a}
    sis_vec = {s: vec_of(k) for s, k in sis_key.items()}
    wanted = {s.lower() for s in (args.sister or [])}
    slots = [a for a, s in pairs.items() if s in sis_vec and (not wanted or s.lower() in wanted)]
    if args.low_photo_only:
        slots = [a for a in slots if not angel_dir.get(a.lower()) or candidate_photo_count(space, angel_dir[a.lower()], st) < min_photos]
    fixed_keys = [angel_dir[a.lower()] for a in FIXED_ANGELS if a.lower() in angel_dir]
    kept = [angel_dir[a.lower()] for a in pairs if a not in slots and a.lower() in angel_dir]
    for a in pairs:
        if a not in slots and angel_dir.get(a.lower()) in artist_of:
            print(f"  NOTE {a} is an artist's person ({artist_of[angel_dir[a.lower()]]}); add --sister {pairs[a]} to replace her")
    cands = [k for k in space.keys if not is_sister(k) and k not in fixed_keys and k not in kept and k not in artist_of and side(k) != "Artists" and candidate_photo_count(space, k, st) >= min_photos]
    weak = [k for k in cands if (vec_of(k) is not None) and cohesion[k] < min_cohesion and k not in {angel_dir.get(a.lower()) for a in slots}]
    if weak:
        print(f"left out ({len(weak)}): too few photos that agree on one face (cohesion below {min_cohesion}): " + ", ".join(f"{k.split('/', 1)[1]} {cohesion[k]:.2f}" for k in weak[:12]))
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
    n_photos = np.array([candidate_photo_count(space, k, st) for k in cands])

    def pair_score(ci, slot):
        sname = pairs[slot]
        s = sim_cs[ci, sv_names.index(sname)]
        score = pairing_candidate_score(float(s), int(n_photos[ci]), target, low, high)
        cost = score["cost"]
        others = [sim_cs[ci, j] for j, nme in enumerate(sv_names) if nme != sname]
        cost += 2.0 * max(0.0, max(others) - 0.28) if others else 0.0
        if cands[ci] == angel_dir.get(slot.lower()):
            cost -= args.keep_bonus
        return cost, score

    def pair_cost(ci, slot):
        return pair_score(ci, slot)[0]

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
    print("  ranking: likeness fit, then a bounded photo-variety bonus (+0.02 at 10, +0.04 at 15, +0.06 at 20 usable photos)")
    print(f"  {'angel':10} {'sister':10}  {'now':32} {'now fit':>8}   {'recommended':28} {'similarity':>10} {'photos':>6} {'fit cost':>9} {'bonus':>7} {'adjusted':>9} {'global':>9}  clashes with / note")
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
        if cur and rec != cur and not low <= s <= high and twin < args.twin and cur not in artist_of:
            note = f"no candidate in the band yet (best {rec.split('/', 1)[1]} {s:.2f}); kept. {note}"
            rec, s = cur, cur_s if cur_s is not None else 0.0
        elif cur in artist_of and rec != cur:
            note = f"{cur.split('/', 1)[1]} is an artist's person ({artist_of[cur]}): replaced by the best prospect" + ("" if s >= low else f", even though {s:.2f} is below the band") + f". {note}"
        elif cur and rec != cur and twin >= args.twin:
            note = f"{cur.split('/', 1)[1]} is a near twin of a fixed angel ({twin:.2f}); replaced by the best available even though it is below the band. {note}"
        score_parts = pairing_candidate_score(s, candidate_photo_count(space, rec, st), target, low, high)
        recommended_photos = candidate_photo_count(space, rec, st)
        global_cost = pair_cost(ci, slot) + fixed_clash(ci) + sum(
            clash(ci, other_ci) for other_slot, other_ci in best_assign.items() if other_slot != slot
        )
        global_adjustment = global_cost - score_parts["cost"] if rec == cands[ci] else 0.0
        mark = "(keep)" if rec == cur else ""
        print(f"  {slot:10} {sname:10}  {cur or '(no folder)':32} {('%.2f' % cur_s) if cur_s is not None else '-':>8}   {rec + ' ' + mark:28} {s:10.2f} {recommended_photos:6} {score_parts['likeness_cost']:9.3f} {score_parts['photo_bonus']:7.2f} {score_parts['cost']:9.3f} {global_adjustment:9.3f}  {note}")
        result.append({"slot": slot, "sister": sname, "now": cur, "now_s": cur_s, "rec": rec, "rec_s": s, "alts": alt_names, "note": note,
                       "photos": recommended_photos, "global_adjustment": global_adjustment, **score_parts})
        md.append((slot, sname, cur or "-", cur_s, rec, s, recommended_photos, score_parts["likeness_cost"],
                   score_parts["photo_bonus"], score_parts["cost"], global_adjustment,
                   ", ".join(c.split("/", 1)[1] for c in alt_names), note))
    if args.sheet:
        rows = []
        for r in result:
            rows.append((f"{r['sister']} (sister)", space.by_key[sis_key[r['sister']]][:6]))
            rows.append((f"-> {r['slot']}: {r['rec'].split('/', 1)[1]}", space.by_key[r["rec"]][:6]))
        make_sheet(rows, args.sheet)
    if args.md:
        lines = [
            "# Angel pairing preview", "",
            "Scoring is shared with the People Gallery, its full candidate report, and the library rebaseline. Candidates need the configured minimum usable-photo count (default 5) and cohesion (default 0.45). The ranking combines likeness fit with a bounded variety bonus: +0.02 at 10 photos, +0.04 at 15, and +0.06 at 20+. Replacements must remain in the preferred likeness band unless replacing an Angel who is an artist's person or a near-twin of a fixed Angel.",
            "The displayed adjusted cost is the per-candidate likeness cost minus the photo bonus. Global adjustment adds counterpart/fixed-cast similarity penalties, conflicts with other selected replacements, and any keep bonus. The global assignment avoids duplicate people, so it may differ from independent candidate-report ordering. Saved ComfyUI renders are included unless `--no-renders` is specified.", "",
            "| Angel | Sister | Folder now | Now vs sister | Recommended | Similarity | Usable photos | Likeness cost | Photo bonus | Adjusted cost | Global adjustment | Alternatives | Note |",
                 "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |"]
        for slot, sname, cur, cs, rec, s, photos, likeness_cost, photo_bonus, adjusted_cost, global_adjustment, alts, note in md:
            lines.append(f"| {slot} | {sname} | {cur} | {('%.2f' % cs) if cs is not None else '-'} | {rec} | {s:.2f} | {photos} | {likeness_cost:.3f} | {photo_bonus:.2f} | {adjusted_cost:.3f} | {global_adjustment:.3f} | {alts} | {note} |")
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
        if cur in artist_of and cur in {r["now"] for r in result if r["rec"] != r["now"]}:
            moves += [Move(p, artist_of[cur], f"{slot} was an artist's person; her photos go back to the artist", bucket="gallery") for p in space.by_key[cur]]
        elif cur and cur not in chosen_for:
            moves += [Move(p, cur, f"{slot}'s earlier photos, set aside for the new {slot}", bucket="review") for p in space.by_key[cur]]
    who = {}
    for r in result:
        to = dir_of[r["slot"].lower()]
        if r["rec"] != to:
            who[to] = (people.name_of(work / r["rec"]) or r["rec"].split("/")[-1], r)
    n = execute(moves, work, True, cache)
    print(f"\n{n} photo(s) moved")
    for to, (nm, r) in who.items():
        people.adopt(work / to, nm, f"now the angel {r['slot']}: paired with {r['sister']} ({r['rec_s']:.2f})")
    gone = retire_empty(work, [m.photo.key for m in moves], keep={cur for cur in angel_dir.values()} | {k for k in space.keys if is_sister(k) or k.startswith("Angels/")})
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


def cmd_loosen(args):
    """What would change if the comparison were looser: counts and examples at lower thresholds, for the photos waiting for a home (Various and the review folders) and for prospects that might be one person. Nothing moves."""
    cfg, st, work, cache, space = build(args)
    embed = args.embedder or Embedder()
    items = [(p.key, p, False) for p in space.photos if matches(p.key, st["pool"]) and p.usable(st["minFace"])]
    items += [(key, ph, True) for key, f, ph in load_review(cfg, work, space, cache, embed, st) if ph]
    info = []
    for key, ph, rev in items:
        rank = [r for r in space.ranking(ph.vec, source=key) if r[1] != key]
        own = float(ph.vec @ space.centroid(key)) if rev and space.centroid(key) is not None else None
        top = rank[0] if rank else (-1.0, "")
        second = max(rank[1][0] if len(rank) > 1 else -1.0, own if own is not None else -1.0)
        info.append({"rev": rev, "key": key, "ph": ph, "own": own, "top": top, "gap": top[0] - second})
    steps = [0.0, 0.05, 0.10, 0.15]
    pool, rev = [i for i in info if not i["rev"]], [i for i in info if i["rev"]]
    print(f"photos waiting for a home: {len(pool)} in Various, {len(rev)} in review folders (with a face)\n")
    print(f"{'setting':44}" + "".join(f"{'now' if s == 0 else '-%.2f' % s:>8}" for s in steps))
    print(f"{'assign (a match must score at least):':44}" + "".join(f"{st['assign'] - s:8.2f}" for s in steps))

    def placed(group, t):
        return [i for i in group if i["top"][0] >= t and i["gap"] >= st["margin"]]

    print(f"{'Various photos that get a home':44}" + "".join(f"{len(placed(pool, st['assign'] - s)):8}" for s in steps))
    print(f"{'review photos sent to someone else':44}" + "".join(f"{len(placed(rev, st['assign'] - s)):8}" for s in steps))
    print(f"{'review photos back to her (--back ' + str(0.20) + ')':44}" + "".join(f"{sum(1 for i in rev if i['own'] is not None and i['own'] >= 0.20 - s and i['own'] >= i['top'][0]):8}" for s in steps))
    print(f"{'review photos clearly not her (--out, odd):':44}" + "".join(f"{sum(1 for i in rev if i['own'] is not None and i['own'] < st['odd'] - s and i['top'][0] < st['assign'] - s):8}" for s in steps))
    now = {id(i) for i in placed(info, st["assign"])}
    extra = [i for i in placed(info, st["assign"] - 0.10) if id(i) not in now]
    print(f"\nat -0.10 these {len(extra)} more would move (the first 12, best match first):")
    for i in sorted(extra, key=lambda i: -i["top"][0])[:12]:
        print(f"  {i['top'][0]:.2f}  {i['key']}/{i['ph'].name[-34:]}  ->  {i['top'][1]}" + (f"   (her own folder {i['own']:.2f})" if i["own"] is not None else ""))
    dest = collections.Counter(i["top"][1] for i in extra)
    if dest:
        print("  where they would go: " + ", ".join(f"{k} {v}" for k, v in dest.most_common(8)))
    # people who may be one person under two folder names
    persons = [k for k in space.keys if len(space.by_key[k]) >= 3 and not k.startswith("Angels/") and not is_sister(k)]
    cents = {k: space.centroid(k) for k in space.keys if len(space.by_key[k]) >= 3}
    pairs = sorted(((float(cents[a] @ cents[b]), a, b) for a, b in itertools.combinations(sorted(cents), 2) if a in persons or b in persons), reverse=True)
    print(f"\nfolders that may be one person (centroid score; the same person is about 0.55 and up):")
    for t in (0.55, 0.45, 0.40, 0.35):
        print(f"  {t:.2f} and up: {sum(1 for s, _, _ in pairs if s >= t)} pair(s)")
    for s, a, b in [p for p in pairs if p[0] >= 0.40][:15]:
        print(f"  {s:.2f}  {a}  ~  {b}")


def cmd_lookalikes(args):
    """Prospects and artist people who look like a sister or an angel (the top tier). Such a person is 'reserved': cards below the top tier should not use her face, or players see two near-identical characters.
    With --apply each gets a line in her z_ file saying so."""
    cfg, st, work, cache, space = build(args)
    thr = args.min if args.min is not None else st["alike"]
    top = [k for k in space.keys if k.startswith("Angels/") or is_sister(k)]
    rows = []
    for k in space.keys:
        if k in top or len(space.by_key[k]) < 3:
            continue
        c = space.centroid(k)
        best = max(((float(c @ space.centroid(t)), t) for t in top if len(space.by_key[t]) >= 3), default=(-1.0, ""))
        if best[0] >= thr:
            rows.append((best[0], k, best[1]))
    rows.sort(reverse=True)
    print(f"{len(rows)} prospect/artist folder(s) score {thr:.2f} or more against a sister or an angel:")
    for s, k, t in rows:
        print(f"  {s:.2f}  {k:34} looks like {t}  ({len(space.by_key[k])} photos)" + ("   [reserved]" if people.reserved(work / k) else ""))
        if args.apply and not any(f"looks like {t} (" in ln for ln in people.reserved(work / k)):
            people.note(work / k, f"reserved: looks like {t} ({s:.2f}); keep off cards below the top tier")
    if not args.apply and rows:
        print("preview only; add --apply to write the reserved lines into the z_ files")


def junk_reason(p, st, multi=True):
    """Why a photo is no use as the input of a Prime, or None: no face, a face too small to work with, a second person in the picture, or (a phone screenshot) the app's bars lying over her head."""
    if p.raw is None:
        return "no face found" if p.faces == 0 else "cannot be read"
    if p.px < st["minFace"]:
        return f"face too small ({p.px}px)"
    if multi and p.faces > 1 and p.f2 >= st.get("multiFace", 0.3):
        return "2+ faces: someone else is in the picture"
    if "_shot_" in p.name and p.box:
        from PIL import Image
        try:
            with Image.open(p.path) as im:
                if screens.is_reel_ui(im.convert("RGB")) and not screens.head_clear(p.box):
                    return "the app's bars cover her head (screenshot)"
        except OSError:
            return "cannot be read"
    return None


def candidate_photo_count(space, key, st):
    count = 0
    for photo in space.by_key.get(key, []):
        if hasattr(photo, "usable"):
            if not photo.usable(st["minFace"]):
                continue
            if junk_reason(photo, st):
                continue
        count += 1
    return count


def pairing_candidate_score(similarity, photo_count, target, low, high):
    """Return likeness fit, a bounded photo-variety bonus, and their combined ranking cost."""
    likeness_cost = abs(similarity - target) + 2 * max(0.0, low - similarity) + 2 * max(0.0, similarity - high)
    photo_bonus = 0.06 if photo_count >= 20 else 0.04 if photo_count >= 15 else 0.02 if photo_count >= 10 else 0.0
    return {
        "likeness_cost": likeness_cost,
        "photo_bonus": photo_bonus,
        "cost": likeness_cost - photo_bonus,
    }


def cmd_rebaseline(args):
    """Read-only whole-library review: propose category changes, confident reassignment, Junk and Retired candidates, and low-photo Angel pairings."""
    cfg, st, work, cache, space = build(args)
    embed = args.embedder or Embedder()
    chosen = chosen_keys(cfg)
    anchors = [a.lower() for values in cfg.get("likeness", {}).get("anchors", {}).values() for a in values]
    items = [(p, p.key, "gallery") for p in space.photos]
    for group, name, folder in cw.photo_folders(cfg, work):
        key = f"{group}/{name}"
        if matches(key, st["mixed"]) and not matches(key, st["pool"]):
            continue
        for path in originals.images(folder / "review"):
            sha = cache.sha(path)
            if sha not in cache.emb:
                cache.emb[sha] = embed(path) or {"faces": -1}
            items.append((Photo(path, group, name, sha, cache.emb[sha]), key, "review"))
    cache.save()

    centroids = {key: space.centroid(key) for key in space.keys}
    junk_rows, retirement_rows, category_rows, reassignment_rows = [], [], [], []
    counts = collections.Counter()
    for photo, key, bucket in items:
        reason = junk_reason(photo, st)
        if reason:
            protected = cw.photo_key(photo.name) in chosen or any(anchor in photo.name.lower() for anchor in anchors)
            row = (key, bucket, photo.name, reason, protected)
            if reason == "cannot be read":
                retirement_rows.append(row)
            else:
                junk_rows.append(row)
            continue
        counts[key] += 1
        if not photo.usable(st["minFace"]) or photo.vec is None:
            continue
        top = key.split("/", 1)[0]
        if top in ("Prospects", "Potentials"):
            other = sorted(((float(photo.vec @ centroid), candidate) for candidate, centroid in centroids.items()
                            if candidate != key and centroid is not None and not apart(key, candidate)), reverse=True)
            own_centroid = space.centroid(key, skip=photo)
            own_score = float(photo.vec @ own_centroid) if own_centroid is not None else None
            if other and other[0][0] >= st["assign"] and (
                    own_score is None or other[0][0] - own_score >= st["margin"]):
                protected = cw.photo_key(photo.name) in chosen
                reassignment_rows.append((other[0][0], key, bucket, photo.name, other[0][1], own_score, protected))

    for key in space.keys:
        root = key.split("/", 1)[0]
        if root not in ("Prospects", "Potentials"):
            continue
        gallery_count = sum(1 for photo, source, bucket in items if source == key and bucket == "gallery" and not junk_reason(photo, st))
        target = "Prospects" if gallery_count >= 5 else "Potentials"
        counts.setdefault(key, gallery_count)
        destination = f"{target}/{key.split('/', 1)[1]}"
        if root != target:
            collision = (work / destination).exists()
            category_rows.append((key, destination, gallery_count, collision))

    if args.apply_categories:
        moved = apply_category_changes(work, category_rows)
        print(f"Applied {moved} Prospect/Potential folder change(s)")
        args.apply_categories = False
        return cmd_rebaseline(args)

    taken = {name.split("/")[-1] for _, name, _ in cw.photo_folders(cfg, work)}
    pool_moves = plan_sort(space, st, cfg, taken, singles=True)
    different = {frozenset(x.casefold() for x in pair) for pair in st.get("different", [])}
    _centroids, pairs = space.pair_matrix()
    candidate_pairs = sorted(
        ((score, a, b) for (a, b), score in pairs.items()
         if a.startswith(("Prospects/", "Potentials/")) and b.startswith(("Prospects/", "Potentials/"))
         and score >= st["rematch"] and frozenset((a.casefold(), b.casefold())) not in different),
        reverse=True,
    )
    angels = []
    for key in space.keys:
        if not key.startswith("Angels/"):
            continue
        usable = candidate_photo_count(space, key, st)
        if usable < 5:
            angels.append((key, usable))

    pair_report = work / "_reports" / "library" / "rebaseline-angel-pairings.md"
    pair_output = io.StringIO()
    pair_args = types.SimpleNamespace(
        root=str(work), cache=args.cache, embedder=embed, no_renders=args.no_renders, sister=None, target=0.28,
        keep_bonus=0.06, min_photos=5, min_cohesion=0.45, twin=0.45, trials=1500,
        sheet=None, md=str(pair_report), apply=False, low_photo_only=True, no_originals=True,
    )
    with contextlib.redirect_stdout(pair_output):
        try:
            cmd_pairs(pair_args)
        except SystemExit as exc:
            pair_output.write(str(exc))

    report = pathlib.Path(args.out) if args.out else work / "_reports" / "library" / "rebaseline.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Whole-library rebaseline preview", "",
        f"Read-only preview of {len(items)} gallery and review photos in {len(space.keys)} person folders. "
        "No photos or folders were moved. Face embeddings may be added to the local cache.", "",
        "## Proposed category changes", "",
        "The boundary uses usable gallery photos that do not currently trigger the Junk rules. "
        "Potentials have 1–4; Prospects have 5 or more.", "",
        "| Current folder | Proposed folder | Usable gallery photos | Result |",
        "| --- | --- | ---: | --- |",
    ]
    for src, dst, count, collision in category_rows:
        lines.append(f"| `{src}` | `{dst}` | {count} | {'blocked: destination exists' if collision else 'proposed'} |")
    if not category_rows:
        lines.append("| No Prospect/Potential folder crosses the threshold | - | - | - |")
    lines += ["", "## Confidently mismatched Prospect/Potential photos", "",
              f"Proposed only when the best other folder scores at least {st['assign']:.2f} "
              f"and beats the photo's own-folder score by {st['margin']:.2f}.", "",
              "| Score | Current folder | Photo | Best other folder | Own-folder score |",
              "| ---: | --- | --- | --- | ---: |"]
    for score, key, bucket, name, dest, own, protected in sorted(reassignment_rows, reverse=True):
        note = " (selected; do not move automatically)" if protected else ""
        lines.append(f"| {score:.3f} | `{key}/{bucket}` | `{name}`{note} | `{dest}` | {own:.3f} |" if own is not None
                     else f"| {score:.3f} | `{key}/{bucket}` | `{name}`{note} | `{dest}` | no peer photos |")
    if not reassignment_rows:
        lines.append("| No confident out-of-folder matches | - | - | - | - |")
    lines += ["", "## Photos matching Junk rules", "",
              "These are cleanup/reprocess candidates, not identity-based retirements. Selected source/anchor photos are protected.", "",
              "| Current folder | Bucket | Photo | Rule | Handling |",
              "| --- | --- | --- | --- | --- |"]
    for key, bucket, name, reason, protected in sorted(junk_rows):
        handling = "keep selected source/anchor" if protected else f"send to `_junk/{status_of(key)}` for cleanup"
        lines.append(f"| `{key}` | {bucket} | `{name}` | {reason} | {handling} |")
    if not junk_rows:
        lines.append("| No photos match current Junk rules | - | - | - | - |")
    lines += ["", "## Unreadable files", "",
              "Unreadable files are the only automatic Retired candidates in this preview; they cannot be face-matched. "
              "They are proposed for archive under `_retired/photos`, never deleted. Confirm they are genuinely unreadable before applying.", "",
              "| Current folder | Bucket | Photo | Handling |",
              "| --- | --- | --- | --- |"]
    for key, bucket, name, _reason, protected in sorted(retirement_rows):
        handling = "keep selected source/anchor" if protected else "archive under `_retired/photos`"
        lines.append(f"| `{key}` | {bucket} | `{name}` | {handling} |")
    if not retirement_rows:
        lines.append("| No unreadable files | - | - | - |")
    lines += ["", "## Existing Various pool", "",
              f"{len([p for p in space.photos if matches(p.key, st['pool'])])} pool photo(s); "
              f"{len(pool_moves)} currently have a confident destination or form a group. No files were moved.", "",
              "| Photo | Proposed destination | Reason |", "| --- | --- | --- |"]
    for move in pool_moves:
        lines.append(f"| `{move.photo.name}` | `{move.to}` | {move.reason} |")
    if not pool_moves:
        lines.append("| No pool moves proposed | - | - |")
    lines += ["", "## Prospect/Potential folder pairs", "",
              f"{len(candidate_pairs)} pair(s) at or above the current rematch threshold ({st['rematch']:.2f}); suggestions only.", "",
              "| Similarity | Folder A | Folder B |", "| ---: | --- | --- |"]
    for score, a, b in candidate_pairs:
        lines.append(f"| {score:.3f} | `{a}` | `{b}` |")
    if not candidate_pairs:
        lines.append("| No candidate pairs | - | - |")
    lines += ["", "## Low-photo Angels", "",
              "The paired report considers only Angels below five usable photos and candidates with at least five; "
              "Sisters remain fixed. This is a preview, not an automatic swap.", ""]
    lines.extend(f"- `{key}`: {count} usable photo(s)" for key, count in angels)
    if not angels:
        lines.append("- No Angel is below five usable photos.")
    lines += ["", f"See [{pair_report.name}]({pair_report.name}) for the low-photo Angel pairing preview.",
              "", "## Limits", "",
              "Face likeness cannot reliably determine closed eyes or whether an angle is aesthetically unusable. "
              "Those photos are not auto-retired by this report. Existing objective Junk rules route no-face, too-small, "
              "multi-face, and obstructed-head photos to Junk for your cleanup. No identity match is treated as proof "
              "that a photo is bad.", ""]
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"whole-library preview: {len(items)} photos; {len(category_rows)} category change(s), "
          f"{len(reassignment_rows)} confident reassignment(s), {len(junk_rows)} Junk candidate(s), "
          f"{len(retirement_rows)} unreadable Retired candidate(s), {len(candidate_pairs)} likely folder pair(s), "
          f"{len(angels)} low-photo Angel(s)")
    print(f"report: {report}")
    print(f"Angel pairing preview: {pair_report}")


def apply_category_changes(work, category_rows):
    """Move whole Prospect/Potential folders after validating the entire batch."""
    moves = []
    for source_key, destination_key, _count, collision in category_rows:
        source_parts = pathlib.PurePosixPath(source_key).parts
        destination_parts = pathlib.PurePosixPath(destination_key).parts
        if (len(source_parts) != 2 or len(destination_parts) != 2
                or source_parts[0] not in ("Prospects", "Potentials")
                or destination_parts[0] not in ("Prospects", "Potentials")
                or source_parts[0] == destination_parts[0]
                or source_parts[1] != destination_parts[1]):
            raise ValueError(f"invalid Prospect/Potential category move: {source_key} -> {destination_key}")
        source, destination = work.joinpath(*source_parts), work.joinpath(*destination_parts)
        if collision or destination.exists():
            raise FileExistsError(f"category destination already exists: {destination}")
        if not source.is_dir():
            raise FileNotFoundError(f"category source folder is missing: {source}")
        if not destination.parent.is_dir():
            raise FileNotFoundError(f"category root is missing: {destination.parent}")
        moves.append((source, destination))

    completed = []
    try:
        for source, destination in moves:
            source.rename(destination)
            completed.append((source, destination))
    except OSError as error:
        for source, destination in reversed(completed):
            destination.rename(source)
        raise OSError(f"category migration stopped and prior folder moves were rolled back: {error}") from error
    return len(completed)


def reset_junk(args, cfg, st, work, cache, embed):
    """Everything in _junk goes back to be looked at again: prospects' photos to the pool (Various), an artist's photos to that artist's gallery (the _origins.json record knows which).
    Run `likeness crop` and `likeness junk` (or bin\\library.cmd) afterwards: what the rules still call junk goes back to _junk, what they can use is sorted."""
    origins = note_origins(work)
    moves, stay = [], []
    for side_dir in sorted(p for p in (work / "_junk").iterdir() if p.is_dir()) if (work / "_junk").is_dir() else []:
        for f in originals.images(side_dir):
            sha = cache.sha(f)
            ph = Photo(f, "_junk", side_dir.name, sha, cache.emb.get(sha) or {"faces": -1})
            if side_dir.name == "Artists":
                artist = origins.get(photo_id(f.name) or "")
                if artist:
                    moves.append(Move(ph, f"Artists/{artist}", "back from _junk to be looked at again", force=True))
                else:
                    stay.append(f.name)
            else:
                moves.append(Move(ph, pool_home(st), "back from _junk to be looked at again"))
    print(f"{len(moves)} photo(s) in _junk go back" + (f"; {len(stay)} artist photo(s) stay (no record of their artist): {', '.join(stay[:5])}" if stay else ""))
    if not moves or not args.apply:
        if moves:
            print("preview only; add --apply to move them")
        return
    n = execute(moves, work, True, cache)
    print(f"{n} photo(s) moved")
    after_moves(args, n > 0)


def recheck_junk(args, cfg, st, work, cache, embed):
    """Look at what is in _junk again with the current rules: a photo that is no longer junk (a passer-by's small face, a face found on the second look) goes back to the person folder its file name says
    (prospects to Prospects, artists to Artists: they are kept apart), or to the pool, Various, when a prospect's folder is gone. An artist's photo whose folder is gone stays."""
    prefixes = {}
    for group, name, folder in cw.photo_folders(cfg, work):
        key = f"{group}/{name}"
        if not matches(key, st["mixed"]):
            prefixes[(status_of(key), originals.prefix_of(name.split("/")[-1]))] = key
    moves, kept, stuck = [], 0, []
    for side_dir in sorted(p for p in (work / "_junk").iterdir() if p.is_dir()) if (work / "_junk").is_dir() else []:
        for f in originals.images(side_dir):
            sha = cache.sha(f)
            if sha not in cache.emb:
                cache.emb[sha] = embed(f) or {"faces": -1}
            ph = Photo(f, "_junk", side_dir.name, sha, cache.emb[sha])
            if junk_reason(ph, st, not args.keep_multi):
                kept += 1
                continue
            m = originals.OLD_PREFIX.match(f.name)
            to = prefixes.get((side_dir.name, m[1].lower() if m else ""))
            if not to and side_dir.name == "Prospects":
                to = pool_home(st)
            if not to:
                stuck.append(f.name)
                continue
            moves.append(Move(ph, to, "was in _junk, usable under the current rules", None))
    cache.save()
    print(f"{len(moves)} photo(s) in _junk are usable now and would go back; {kept} are still junk" + (f"; {len(stuck)} stay (their folder is gone)" if stuck else ""))
    for m in moves:
        print(f"       {m.photo.name}  ->  {m.to}")
    if not moves or not args.apply:
        if moves:
            print("preview only; add --apply to move them")
        return
    n = execute(moves, work, True, cache)
    print(f"{n} photo(s) moved")
    after_moves(args, n > 0)


def cmd_junk(args):
    """Photos that cannot feed a Prime (no usable face, a face too small, the phone app's bars over her head) go to <work>/_junk/<same path>, to be looked at and emptied by you; nothing is deleted.
    An angel's or sister's own gallery is never touched (listed only), nor is a chosen or anchor photo. A folder that is left empty is retired. Preview unless --apply; `likeness undo` puts them back."""
    cfg, st, work, cache, space = build(args)
    embed = args.embedder or Embedder()
    if args.reset:
        return reset_junk(args, cfg, st, work, cache, embed)
    if args.recheck:
        return recheck_junk(args, cfg, st, work, cache, embed)
    protected = chosen_keys(cfg)
    anchors = [a.lower() for v in cfg.get("likeness", {}).get("anchors", {}).values() for a in v]
    items = [(p.key, p, "gallery") for p in space.photos]
    for group, name, folder in cw.photo_folders(cfg, work):
        key = f"{group}/{name}"
        if matches(key, st["mixed"]) and not matches(key, st["pool"]):
            continue
        for f in originals.images(folder / "review"):
            sha = cache.sha(f)
            if sha not in cache.emb:
                cache.emb[sha] = embed(f) or {"faces": -1}
            items.append((key, Photo(f, group, name, sha, cache.emb[sha]), "review"))
    cache.save()
    moves, left, by = [], [], collections.defaultdict(list)
    for key, p, bucket in items:
        why = junk_reason(p, st, not args.keep_multi)
        if not why:
            continue
        if cw.photo_key(p.name) in protected or any(a in p.name.lower() for a in anchors) or (bucket == "gallery" and (key.startswith("Angels/") or is_sister(key))):
            left.append((key, p.name, why))
            continue
        moves.append(Move(p, f"_junk/{status_of(key)}", why, None, bucket=""))
        by[why.split(" (")[0]].append(p)
    for why, ps in sorted(by.items(), key=lambda kv: -len(kv[1])):
        print(f"{len(ps):4}  {why}")
    for m in moves:
        print(f"       {m.photo.key}/{m.bucket}/{m.photo.name}   {m.reason}")
    if left:
        print(f"\n{len(left)} photo(s) with a problem are left where they are (an angel's or sister's own gallery, or a chosen photo):")
        for key, name, why in left[:20]:
            print(f"       {key}/{name}   {why}")
    print(f"\n{len(moves)} photo(s) would go to _junk" if not args.apply else f"\n{len(moves)} photo(s) to _junk")
    if args.sheet and moves:
        make_sheet([(why, ps[:10]) for why, ps in by.items()], args.sheet)
    if not moves or not args.apply:
        if moves:
            print("preview only; add --apply to move them")
        return
    n = execute(moves, work, True, cache)
    for key, ms in itertools.groupby(sorted(moves, key=lambda m: m.photo.key), key=lambda m: m.photo.key):
        ms = list(ms)
        if key.split("/")[-1].lower() != "various":
            people.note(work / key, f"junk: {len(ms)} photo(s) set aside in _junk ({'; '.join(sorted({m.reason.split(' (')[0] for m in ms}))})")
    gone = retire_empty(work, [m.photo.key for m in moves], keep={k for k in space.keys if k.startswith("Angels/") or is_sister(k)} | set(st["pool"]))
    if gone:
        print("emptied folders moved to _retired: " + ", ".join(gone))
    print(f"{n} photo(s) moved")
    after_moves(args, n > 0)


def cmd_singles(args):
    """A prospect with a single photo is probably someone already in the library whose photo is odd (an angle, a screenshot): this lists, for each, the prospect she looks most like.
    One that scores at least --min (default: settings `singles`, 0.35) with a margin over the next goes into that prospect's folder. Prospects only: never an artist's person (they are kept apart), nor an angel or a sister."""
    cfg, st, work, cache, space = build(args)
    thr = args.min if args.min is not None else st["singles"]
    protected = chosen_keys(cfg)
    rows, moves = [], []
    for k in space.keys:
        ps = space.by_key[k]
        if not k.startswith(("Prospects/", "Potentials/")) or len(ps) != 1 or len(originals.images(work / k / "review")):
            continue
        p = ps[0]
        rank = [r for r in space.ranking(p.vec, source=k) if r[1] != k and ((r[1].startswith(("Prospects/", "Potentials/")) and len(space.by_key[r[1]]) >= 2) or r[1].startswith("Angels/") or is_sister(r[1]))]
        top, second = (rank[0] if rank else (-1.0, "")), (rank[1][0] if len(rank) > 1 else -1.0)
        need = st["castMerge"] if top[1].startswith("Angels/") or is_sister(top[1]) else thr  # an angel or a sister is only joined when it is clearly the same woman
        ok = top[0] >= need and top[0] - second >= args.margin and cw.photo_key(p.name) not in protected
        rows.append((top[0], k, top[1], second, ok, p))
        if ok:
            moves.append(Move(p, top[1], f"a single photo that looks like {top[1].split('/', 1)[1]} ({top[0]:.2f}; next {second:.2f})", top[0]))
    rows.sort(key=lambda r: -r[0])
    print(f"{len(rows)} prospect(s) with one photo; merge at {thr:.2f} or more with a margin of {args.margin:.2f}:")
    for s, k, t, sec, ok, p in rows:
        print(f"  {s:5.2f}  {k.split('/', 1)[1]:22} looks most like {t.split('/', 1)[1] if t else '-':22} (next {sec:.2f})  {'-> merge' if ok else ''}")
    print(f"\n{len(moves)} would merge, {len(rows) - len(moves)} stay as they are")
    if args.sheet and moves:
        make_sheet([(m.to.split("/", 1)[1], [m.photo]) for m in moves], args.sheet)
    if not moves:
        return
    if not args.apply:
        print("preview only; add --apply to merge them")
        return
    n = execute(moves, work, True, cache)
    gone = retire_empty(work, [m.photo.key for m in moves])
    if gone:
        print("emptied folders moved to _retired: " + ", ".join(gone))
    print(f"{n} photo(s) moved")
    after_moves(args, n > 0)


def cmd_rematch(args):
    """Prospect folders that are one person under two names. Two prospect folders whose centroids score at least --min (default: settings `rematch`, 0.48; at 0.45 a folder of six different-looking women was merged into another) are merged, the smaller into the larger
    (a folder that was merged is not merged again in the same run). A prospect that scores at least `rematchCast` (0.50) against an angel or a sister is only listed: the cast is yours to change
    (`likeness merge PROSPECT ANGEL`). Pairs under `different` in workspaces.json are never merged or listed. Artists are kept apart. Run it again after a merge: the centroids moved."""
    cfg, st, work, cache, space = build(args)
    thr = args.min if args.min is not None else st["rematch"]
    different = {frozenset(x.lower() for x in pair) for pair in st.get("different", [])}
    _cents, pairs = space.pair_matrix()
    prospects = {k for k in space.keys if k.startswith(("Prospects/", "Potentials/"))}
    size = {k: len(space.by_key[k]) for k in prospects}
    chosen = chosen_keys(cfg)
    held = {k for k in prospects if any(cw.photo_key(p.name) in chosen for p in space.by_key[k])}
    rows = sorted(((s, a, b) for (a, b), s in pairs.items() if a in prospects and b in prospects and s >= thr and frozenset((a.lower(), b.lower())) not in different), reverse=True)
    into, plan = {}, []

    def home(k):
        while k in into:
            k = into[k]
        return k

    for s, a, b in rows:
        ra, rb = home(a), home(b)
        if ra == rb or ra in held and rb in held:
            continue
        src = sorted((ra, rb), key=lambda k: (k in held, size[k], k))[0]
        dst = rb if src == ra else ra
        into[src] = dst
        size[dst] += size[src]
        plan.append((s, src, dst))
    cast_keys = [k for k in space.keys if k.startswith("Angels/") or is_sister(k)]
    for k in sorted(prospects):
        if k in into:
            continue
        best = max(((pairs.get((k, c), pairs.get((c, k), -1.0)), c) for c in cast_keys if frozenset((k.lower(), c.lower())) not in different), default=(-1.0, ""))
        if best[0] >= st["castMerge"]:
            into[k] = best[1]
            plan.append((best[0], k, best[1]))
    print(f"{len(prospects)} prospect folder(s); {len(plan)} merge(s) at {thr:.2f} or more (the same person scores about 0.55):")
    for s, src, dst in plan:
        print(f"  {s:.2f}  {src.split('/', 1)[1]:22} ({len(space.by_key[src])}) -> {dst.split('/', 1)[1]:22} ({len(space.by_key[dst])} before)")
    cast = sorted(((s, a, b) for (a, b), s in pairs.items() if st["rematchCast"] <= s < st["castMerge"] and ((a in prospects) != (b in prospects)) and frozenset((a.lower(), b.lower())) not in different
                   and any(k.startswith("Angels/") or is_sister(k) for k in (a, b))), reverse=True)
    if cast:
        print(f"\nprospects that look like an angel or a sister at {st['rematchCast']:.2f} to {st['castMerge']:.2f} (not merged: very alike, not the same person; yours to decide with `likeness merge PROSPECT NAME`, or add the pair to `different`):")
        for s, a, b in cast:
            print(f"  {s:.2f}  {a}  ~  {b}")
    moves = []
    for _s, src, dst in plan:
        final = home(dst)
        moves += [Move(p, final, f"folder merged: {src.split('/', 1)[1]} looks like {final.split('/', 1)[1]} ({_s:.2f})", _s) for p in space.photos if p.key == src]
    if args.sheet and plan:
        make_sheet([(f"{s.split('/', 1)[1]} -> {d.split('/', 1)[1]}", space.by_key[s][:5] + space.by_key[d][:5]) for _sc, s, d in plan], args.sheet)
    if not moves:
        print("\nnothing to merge")
        return
    if not args.apply:
        print("\npreview only; add --apply to merge them")
        return
    n = execute(moves, work, True, cache)
    gone = retire_empty(work, [src for _s, src, _d in plan])
    if gone:
        print("emptied folders moved to _retired: " + ", ".join(gone))
    print(f"{n} photo(s) moved")
    after_moves(args, n > 0)


INDEX_COLUMNS = ["status", "folder", "name", "photos", "headshots", "review", "best_prime_photo", "looks_like", "looks_like_score", "reserved", *people.PROFILE_KEYS]


def library_people(cfg, st, work):
    """[(key, path)] of every person folder (angel, sister, prospect, an artist's person), not the pool or an artist's own mixed folder."""
    out = []
    for group, name, folder in cw.photo_folders(cfg, work):
        key = f"{group}/{name}"
        if matches(key, st["mixed"]):
            continue
        out.append((key, folder))
    return out


def status_of(key):
    top = key.split("/")[0]
    return "Sisters" if top in cw.SISTER_ROOTS else top


def cmd_index(args):
    """The table to pick from: one row per person (angel, sister, prospect, an artist's person) with her name, photo counts, best Prime photo, who she looks like, whether she is reserved, and the profile you set
    (sex, type, roles, elements, tier, tags). Written to <work>/people_index.csv (opens in a spreadsheet) and .md. Edit the profile columns in the spreadsheet and run `index --import people_index.csv --apply`
    to write them back into the z_ files; the z_ file keeps the why."""
    cfg, st, work, cache, space = build(args)
    if args.imp:
        return import_profiles(args, cfg, st, work)
    top = [k for k in space.keys if k.startswith("Angels/") or is_sister(k)]
    rows = []
    for key, folder in library_people(cfg, st, work):
        pf = people.profile(folder)
        ps = space.by_key.get(key, [])
        c = space.centroid(key) if ps else None
        best = best_photo(space, key, folder_core(space, key)[3]) if len(ps) >= 2 else (ps[0] if ps else None)
        like = max(((float(c @ space.centroid(t)), t) for t in top if t != key and space.by_key.get(t)), default=(None, ""), key=lambda r: r[0]) if c is not None else (None, "")
        rows.append({
            "status": status_of(key), "folder": key.split("/", 1)[1], "name": people.name_of(folder) or "",
            "photos": len(originals.images(folder / "gallery")), "headshots": len(list((folder / f"headshot_{cfg.get('standardSize', [944, 1104])[0]}x{cfg.get('standardSize', [944, 1104])[1]}").glob("*.png"))),
            "review": len(originals.images(folder / "review")), "best_prime_photo": best.name if best else "",
            "looks_like": like[1].split("/", 1)[1] if like[1] and like[0] is not None and like[0] >= 0.20 else "", "looks_like_score": f"{like[0]:.2f}" if like[0] is not None and like[0] >= 0.20 else "",
            "reserved": "yes" if people.reserved(folder) else "",
            **{k: "; ".join(pf.get(k, [])) for k in people.PROFILE_KEYS},
        })
    order = {"Angels": 0, "Sisters": 1, "Prospects": 2, "Potentials": 3, "Artists": 4}
    rows.sort(key=lambda r: (order.get(r["status"], 9), r["folder"].lower()))
    import csv
    csv_path, md_path = work / "people_index.csv", work / "people_index.md"
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=INDEX_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    classified = [r for r in rows if r["type"] or r["roles"] or r["elements"]]
    lines = ["# People index", "", f"{len(rows)} people; {len(classified)} classified. Edit the profile columns (sex, type, roles, elements, tier, tags) in `people_index.csv` and run `likeness index --import people_index.csv --apply`.", "",
             "| status | folder | name | photos | head | review | looks like | reserved | sex | type | roles | elements | tier | tags |", "| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        lines.append(f"| {r['status']} | {r['folder']} | {r['name']} | {r['photos']} | {r['headshots']} | {r['review']} | {(r['looks_like'] + ' ' + r['looks_like_score']).strip()} | {r['reserved']} | {r['sex']} | {r['type']} | {r['roles']} | {r['elements']} | {r['tier']} | {r['tags']} |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(rows)} people ({len(classified)} classified): {csv_path}\n  and {md_path}")


def split_values(cell):
    """'a; b' or 'a, b' -> ['a', 'b']; '-' alone means nothing (clears the key)."""
    vals = [v.strip() for v in re.split(r"[;,]", cell or "") if v.strip()]
    return [] if vals == ["-"] else vals


def import_profiles(args, cfg, st, work):
    import csv
    path = pathlib.Path(args.imp)
    path = path if path.exists() else work / args.imp
    by_folder = {(status_of(k) + "/" + k.split("/", 1)[1]).lower(): f for k, f in library_people(cfg, st, work)}
    changed = unknown = 0
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            folder = by_folder.get(f"{row.get('status', '')}/{row.get('folder', '')}".lower())
            if folder is None:
                unknown += 1
                print(f"  not a person folder: {row.get('status')}/{row.get('folder')}")
                continue
            values = {k: split_values(row.get(k)) for k in people.PROFILE_KEYS if k in row}
            old = people.profile(folder)
            if all(values.get(k, []) == old.get(k, []) for k in people.PROFILE_KEYS if k in values):
                continue
            changed += 1
            print(f"  {row['status']}/{row['folder']}: " + "; ".join(f"{k}={', '.join(v) or '-'}" for k, v in values.items() if v != old.get(k, [])))
            if args.apply:
                people.set_profile(folder, values)
    print(f"{changed} profile(s) " + ("written" if args.apply else "would change (preview; add --apply)") + (f", {unknown} unknown row(s)" if unknown else ""))


def cmd_profile(args):
    """Set the profile of one or more people: likeness profile "Rhea Ives" "Mara Lowe" --type "dark elf" --roles rogue,assassin --elements Darkness --sex f (values replace; an empty value clears the key)."""
    cfg = cw.load_cfg()
    st = settings(cfg)
    work = pathlib.Path(args.root) if args.root else cw.work_root(cfg)
    people_ = library_people(cfg, st, work)
    values = {k: split_values(getattr(args, k)) for k in people.PROFILE_KEYS if getattr(args, k) is not None}
    if not values:
        sys.exit("give at least one of --" + ", --".join(people.PROFILE_KEYS))
    for n in args.names:
        hits = [(k, f) for k, f in people_ if n.lower() in (k.lower(), k.split("/", 1)[1].lower(), k.split("/")[-1].lower())]
        if len(hits) != 1:
            sys.exit(f"'{n}' matches {len(hits)} people: {[k for k, _ in hits]}")
        k, folder = hits[0]
        print(f"{k}: " + ("changed" if people.set_profile(folder, values) else "already so"))


def cmd_who(args):
    """Who could play a part: filter the profile by sex, type, roles, elements, tier or tag (a word matches inside a value; every filter must match). Prospects and artists by default; --all adds angels and sisters.
    Reserved people (they look like a top-tier angel or sister) are marked: keep them off cards below the top tier."""
    cfg = cw.load_cfg()
    st = settings(cfg)
    work = pathlib.Path(args.root) if args.root else cw.work_root(cfg)
    want = {k: getattr(args, k).lower() for k in people.PROFILE_KEYS if getattr(args, k)}
    shown = 0
    for key, folder in library_people(cfg, st, work):
        if not args.all and status_of(key) not in ("Prospects", "Artists"):
            continue
        pf = people.profile(folder)
        if any(not any(w in v.lower() for v in pf.get(k, [])) for k, w in want.items()):
            continue
        if not want and pf:
            continue  # with no filter: the people still to classify
        shown += 1
        print(f"  {status_of(key):9} {key.split('/', 1)[1]:26} {people.name_of(folder) or '':20} {len(originals.images(folder / 'gallery')):3} photos  "
              + "  ".join(f"{k}: {', '.join(v)}" for k, v in pf.items()) + ("   [reserved]" if people.reserved(folder) else ""))
    print(f"{shown} " + ("match" if want else "still to classify"))


def cmd_names(args):
    """Who is in each folder: the z_ file of every person folder. A folder without one gets it made from the move log (the name of the person most of its photos came from, else its own name)."""
    cfg, st, work, cache, space = build(args)
    log = DATA / "likeness_moves.json"
    batches = json.loads(log.read_text(encoding="utf-8")) if log.exists() else []
    came = collections.defaultdict(lambda: collections.defaultdict(int))  # folder -> (date, source folder) -> photos
    for b in batches:
        date = f"{b['id'][:4]}-{b['id'][4:6]}-{b['id'][6:8]}"
        for mv in b["moves"]:
            src, dst = pathlib.Path(mv["from"]), pathlib.Path(mv["to"])
            if not (src.is_relative_to(work) and dst.is_relative_to(work)):
                continue
            s, d = src.parent.parent.relative_to(work).as_posix(), dst.parent.parent.relative_to(work).as_posix()
            if s != d:
                came[d][(date, s)] += 1
    rows = []
    for key in sorted(space.keys):
        folder = work / key
        got = people.read(folder)
        if got:
            rows.append((key, got[0], len(got[1]), "has z_ file"))
            continue
        srcs = collections.defaultdict(int)
        for (date, s), n in came.get(key, {}).items():
            srcs[s] += n
        eligible = [s for s in srcs if not matches(s, st["pool"] + st["mixed"]) and s.split("/")[0] not in ("Angels", *cw.SISTER_ROOTS)]  # a person's name comes from a prospect or an artist's person, never from the pool or another angel
        best = max(eligible, key=lambda s: srcs[s], default=None)
        own = key.split("/")[-1]
        name = (people.name_of(work / best) if best and (work / best).is_dir() else None) or (best.split("/")[-1] if best else own.title() if own.islower() else own)
        hist = [f"{date} +{n} from {s}" for (date, s), n in sorted(came.get(key, {}).items())]
        rows.append((key, name, len(hist), "new z_ file"))
        if args.apply:
            people.write(folder, name, hist)
    print(f"{'folder':32} {'name':26} history  note")
    for key, name, n, note in rows:
        print(f"{key:32} {name:26} {n:7}  {note}")
    made = sum(1 for r in rows if r[3] == "new z_ file")
    print(f"\n{len(rows)} person folder(s); {made} without a z_ file" + ("; written" if args.apply and made else ("; add --apply to write them" if made else "")))


def cmd_rename(args):
    """Rename a Prospect or Potential folder and its recorded name, preserving history and updating photo names."""
    cfg = cw.load_cfg()
    work = pathlib.Path(args.root) if args.root else cw.work_root(cfg)
    requested = args.prospect.strip()
    requested_root = next((root for root in ("Prospects", "Potentials")
                           if requested.casefold().startswith(f"{root.casefold()}/")), None)
    if requested_root:
        requested = requested[len(requested_root) + 1:]
    new_name = args.new_name.strip()
    invalid = '<>:"/\\|?*'
    if (not requested or not new_name or new_name != args.new_name
            or any(ch in invalid or ord(ch) < 32 for ch in new_name)
            or new_name.endswith((".", " "))):
        sys.exit("use a non-empty folder name without Windows path or filename characters")
    roots = [work / requested_root] if requested_root else [work / "Prospects", work / "Potentials"]
    matches = [p for root in roots if root.is_dir() for p in root.iterdir()
               if p.is_dir() and p.name.casefold() == requested.casefold()]
    if len(matches) != 1 or matches[0].name.casefold() == "various":
        sys.exit(f"not one Prospect or Potential person folder: {args.prospect}")
    folder = matches[0]
    root_name = folder.parent.name
    destination = folder.with_name(new_name)
    if destination != folder and destination.exists():
        sys.exit(f"Prospect folder already exists: {destination.name}")
    if destination == folder:
        print(f"Prospect already has this folder name: {new_name}")
        return
    old_recorded_name = people.name_of(folder) or folder.name
    print(f"{root_name}/{folder.name} -> {root_name}/{new_name}")
    print(f"  recorded name: {old_recorded_name} -> {new_name}")
    if not args.apply:
        print("preview only; add --apply to create a full backup and rename the folder")
        return

    backup = library_backup.create_backup(
        work,
        cfg.get("paths", {}).get("inputsRoot"),
        ROOT / "workflows" / "workspaces.json",
        apply=True,
    )
    print(f"full pre-rename snapshot: {backup}")
    old_record = people.find(folder)
    old_record_bytes = old_record.read_bytes() if old_record else None
    folder.rename(destination)
    try:
        people.adopt(destination, new_name, f"renamed prospect from {old_recorded_name}")
        old_key, new_key = f"{root_name}/{folder.name}", f"{root_name}/{new_name}"
        different = cfg.get("likeness", {}).get("different", [])
        changed = False
        for pair in different:
            for index, value in enumerate(pair):
                if value.casefold() == old_key.casefold():
                    pair[index] = new_key
                    changed = True
        if changed:
            cw.write_cfg(cfg)
    except Exception:
        destination.rename(folder)
        for record in (folder / "gallery").glob("z_*.txt"):
            if not old_record or record.name != old_record.name:
                record.unlink()
        if old_record_bytes is not None:
            (folder / "gallery" / old_record.name).write_bytes(old_record_bytes)
        raise
    after_moves(args, True)


def main(argv=None, embedder=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", help="the folder that holds Angels, Sisters, Prospects, Potentials, Artists and Various (default: workspaces.json paths.workRoot)")
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
    s = add("audit-core", cmd_audit_core)
    s.add_argument("names", nargs="*", help="folders to audit (default: all person folders)")
    s.add_argument("--group", help="only folders under this group, such as Prospects or Angels")
    s.add_argument("--keep", type=float, default=0.25, help="score below which a Prospect is marked borderline (default: 0.25)")
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
    s.add_argument("--assign", type=float, help="score that makes a match for this run (default: settings assign, 0.40); a lower one is a looser second look, best used after `pullback`")
    add("merge", cmd_merge, "a", "b", apply=True, sheet=True)
    add("retire", lambda a: cmd_merge(a, retire=True), "name", apply=True, sheet=True)
    add("retire-empty", cmd_retire_empty, apply=True)
    s = add("archive-list", cmd_archive_list, apply=True)
    s.add_argument("list", help="Markdown checklist of Prospects/Name or Artists/Artist/Person folders to archive")
    add("promote", cmd_promote, "prospect", "hero", apply=True)
    add("rename", cmd_rename, "prospect", "new_name", apply=True)
    s = add("clean", cmd_clean, apply=True, sheet=True)
    s.add_argument("names", nargs="*", help="folders to clean (default: every person folder; with --group, that kind)")
    s.add_argument("--group", help="Angels, Sisters or Prospects")
    s.add_argument("--keep", type=float, default=0.25, help="photos scoring at least this against the folder's core are kept (default 0.25); between the 'odd' score and this they go to the folder's review folder")
    s.add_argument("--sister-out", type=float, default=0.05, help="in a sister's folder only photos scoring below this leave it (default 0.05); the rest of the doubtful ones go to her review folder")
    s.add_argument("--anchor", action="append", help="HERO=part of a photo's name that is certainly her (repeatable); the chosen photo and `likeness.anchors` in workspaces.json are used too")
    s.add_argument("--no-renders", action="store_true", help="ignore the ComfyUI renders when deciding what she looks like")
    s = add("group", cmd_group, apply=True, sheet=True)
    s.add_argument("names", nargs="*", help="artist folders (default: all)")
    s.add_argument("--cluster", type=float, help="average similarity needed to be one person (default: settings cluster)")
    s.add_argument("--min-photos", type=int, help="photos a new person needs (default: settings minCluster, 3); a pair can still join a person who is already there")
    s.add_argument("--cohesion", type=float, default=0.40, help="a new person's photos must score this well against each other on average (default 0.40; one person's own photos score 0.55 and up)")
    s.add_argument("--singles", action="store_true", help="every other usable photo in the gallery is placed too: with a person of this artist she scores --single-join against, else in a folder of her own; only photos with no usable face, a second person or the app's bars stay")
    s.add_argument("--single-join", type=float, default=0.35, help="score that makes a single photo one of the artist's people (default 0.35, with a margin of 0.05 over the next)")
    s.add_argument("--join", type=float, default=0.45, help="a group this alike a person already in the same artist's folder joins her instead of becoming a new person (default 0.45)")
    s = add("artists", cmd_artists, apply=True)
    s.add_argument("--from", dest="origin", required=True, help="the Artists folder of a backup, flat per artist: it says which artist each photo came from")
    s.add_argument("--assign", type=float, help="score that makes a photo one of an artist's people (default: settings assign, 0.40)")
    s.add_argument("--keep", type=float, default=0.25, help="a photo already in a person's folder stays when it scores at least this against her (default 0.25)")
    s.add_argument("--margin", type=float, default=0.10, help="she must score this much better than the next person of that artist (default 0.10)")
    s.add_argument("--junk", action="store_true", help="first bring the photos in _junk/Artists back to the gallery of the artist they came from, to be sorted again")
    s.add_argument("--gallery", action="store_true", help="only place the photos loose in an artist's own gallery (people already grouped are left as they are)")
    s = add("crop", cmd_crop, apply=True)
    s.add_argument("--undo", action="store_true", help="put the last batch's uncropped originals back")
    s.add_argument("--no-background", action="store_true", help="only cut the app's bars, other people and animals, not the background beside her")
    s = add("pullback", cmd_pullback, apply=True)
    s.add_argument("names", nargs="*", help="prospect folders to send back to Various (to be sorted again)")
    s.add_argument("--small", type=int, help="also every prospect folder with this many photos or fewer")
    s.add_argument("--all", action="store_true", help="every prospect folder (a full re-sort of the prospects); folders holding a chosen photo are never pulled back")
    s = add("crops", cmd_crops)
    s.add_argument("--out", help="write the page here (default: <work>/_reports/library/crop_review.html)")
    s = add("crosscheck", cmd_crosscheck)
    s.add_argument("--min", type=float, help="report pairs at or above this score (default: settings alike, 0.30)")
    s.add_argument("--out", help="write the report here (default: <work>/_reports/library/crosscheck.md)")
    s = add("sisters", cmd_sisters, sheet=True)
    s.add_argument("--anchor-sister", default="Drakness")
    s.add_argument("--no-renders", action="store_true")
    s.add_argument("--md", help="also write the table as markdown to this file")
    s = add("pairs", cmd_pairs, apply=True, sheet=True)
    s.add_argument("--sister", action="append", help="only (re-)pair the angel of this sister (repeatable); the other angels stay as they are")
    s.add_argument("--target", type=float, help="how alike a candidate should be to her configured counterpart (default: settings pairTarget or 0.28)")
    s.add_argument("--keep-bonus", type=float, default=0.06, help="how much better a replacement must be than the angel already in the folder")
    s.add_argument("--min-photos", type=int, help="a candidate needs this many usable photos to be considered (default: settings pairMinPhotos or 5)")
    s.add_argument("--min-cohesion", type=float, help="candidate photos must agree on one face this well (default: settings pairMinCohesion or 0.45)")
    s.add_argument("--twin", type=float, default=0.45, help="an angel this alike a fixed angel (Angelica) is replaced even when no candidate is in the band")
    s.add_argument("--low-photo-only", action="store_true", help="only re-pair Angels with fewer than --min-photos; keep other Angel slots fixed")
    s.add_argument("--trials", type=int, default=1500)
    s.add_argument("--no-renders", action="store_true")
    s.add_argument("--md", help="also write the table as markdown to this file")
    s = add("rebaseline", cmd_rebaseline)
    s.add_argument("--out", help="write the read-only whole-library report here (default: <work>\\_reports\\library\\rebaseline.md)")
    s.add_argument("--no-renders", action="store_true", help="ignore saved ComfyUI face renders when scoring Angel pairings")
    s.add_argument("--apply-categories", action="store_true", help="move only threshold-driven Prospect/Potential folders; create and verify a library backup first")
    s = add("review", cmd_review, apply=True, sheet=True)
    s.add_argument("names", nargs="*", help="folders whose review photos to look at (default: all)")
    s.add_argument("--back", type=float, default=0.20, help="a review photo scoring at least this against her own folder goes back to her gallery (default 0.20)")
    s.add_argument("--out", action="store_true", help="a review photo that is clearly not her and matches nobody becomes a new prospect (alike photos share one)")
    add("loosen", cmd_loosen)
    s = add("junk", cmd_junk, apply=True, sheet=True)
    s.add_argument("--keep-multi", action="store_true", help="do not treat a photo with a second person (a second face at least `multiFace`, 0.3, of the main face's size) as junk")
    s.add_argument("--recheck", action="store_true", help="look at what is in _junk again: photos that are usable under the current rules go back to Various to be sorted")
    s.add_argument("--reset", action="store_true", help="send everything in _junk back (prospects' photos to Various, an artist's to that artist's gallery) to be cropped and sorted again; what is still junk returns to _junk")
    s = add("singles", cmd_singles, apply=True, sheet=True)
    s.add_argument("--min", type=float, help="score that makes a single photo one of an existing prospect (default: assign less 0.10)")
    s.add_argument("--margin", type=float, default=0.05, help="she must score this much better against that prospect than against the next (default 0.05)")
    s = add("rematch", cmd_rematch, apply=True, sheet=True)
    s.add_argument("--min", type=float, help="score at which two prospect folders are one person (default: settings rematch, 0.48)")
    s = add("lookalikes", cmd_lookalikes, apply=True)
    s.add_argument("--min", type=float, help="score against a sister or angel that makes a prospect or artist person 'reserved' (default: settings alike, 0.30)")
    s = add("photos", cmd_photos, apply=True, sheet=True)
    s.add_argument("names", nargs="*", help="heroes (default: every angel and sister)")
    s.add_argument("--group", help="Angels or Sisters")
    s.add_argument("--margin", type=float, default=0.12, help="a hero's chosen photo only changes when the best one scores this much higher (default 0.12)")
    s.add_argument("--sisters", action="store_true", help="also change the sisters' photos (by default they are only reported: a sister's photo is your choice)")
    s.add_argument("--no-renders", action="store_true")
    add("undo", cmd_undo, apply=True)
    add("names", cmd_names, apply=True)
    s = add("index", cmd_index, apply=True)
    s.add_argument("--import", dest="imp", help="read the profile columns of this CSV (as written by index) back into the z_ files")
    s = add("profile", cmd_profile)
    s.add_argument("names", nargs="+", help="folders")
    for k in people.PROFILE_KEYS:
        s.add_argument(f"--{k}", help=f"{k}: one or more values separated by commas")
    s = add("who", cmd_who)
    for k in people.PROFILE_KEYS:
        s.add_argument(f"--{k}", help=f"only people whose {k} contains this word")
    s.add_argument("--all", action="store_true", help="also angels and sisters")
    args = ap.parse_args(argv)
    args.embedder = embedder
    for k in ("apply", "sheet", "plan", "all", "outside"):
        if not hasattr(args, k):
            setattr(args, k, None if k not in ("apply", "all", "outside") else False)
    args.fn(args)


if __name__ == "__main__":
    main()
