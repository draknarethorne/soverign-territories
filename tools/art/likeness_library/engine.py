"""Face embeddings, cached photos, and centered identity-space operations."""

import collections
import fnmatch
import hashlib
import itertools
import json
import pathlib

import numpy as np

import comfy_workflows as cw
import originals
from likeness_library.scoring import nz


MODEL_URLS = {
    "face_detection_yunet_2023mar.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "face_recognition_sface_2021dec.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx",
}
HUMAN_BEST, HUMAN_MIN = 0.9, 0.85
SETTINGS = {
    "mixed": ["Artists/*", "Various", "Prospects/Various", "Potentials/Various"],
    "pool": ["Various", "Prospects/Various", "Potentials/Various"],
    "assign": 0.40,
    "margin": 0.10,
    "cluster": 0.25,
    "minCluster": 3,
    "odd": 0.15,
    "alike": 0.30,
    "minFace": 60,
    "multiFace": 0.3,
    # A single photo joins a person at 0.35; prospect-folder rematch is 0.48.
    "singles": 0.35,
    "rematch": 0.48,
    # Cast matches are listed for review; they do not imply a cast identity change.
    "rematchCast": 0.50,
    "different": [],
    # A confident cast match is handled by the explicit merge command.
    "castMerge": 0.55,
}


class Embedder:
    """Find faces and return normalized identity vectors using local OpenCV models."""

    def __init__(self, model_root):
        self.model_root = pathlib.Path(model_root)
        self.det = self.rec = None

    def load(self):
        import cv2

        models = self.model_root / "models"
        models.mkdir(parents=True, exist_ok=True)
        for name, url in MODEL_URLS.items():
            path = models / name
            if not path.exists():
                import urllib.request

                print(f"downloading {name} ...")
                urllib.request.urlretrieve(url, path)
        self.det = cv2.FaceDetectorYN.create(
            str(models / "face_detection_yunet_2023mar.onnx"), "", (320, 320), 0.7, 0.3, 5000
        )
        self.rec = cv2.FaceRecognizerSF.create(
            str(models / "face_recognition_sface_2021dec.onnx"), ""
        )

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
        for threshold in (0.7, 0.5):
            self.det.setScoreThreshold(threshold)
            _, faces = self.det.detect(small)
            if faces is not None and len(faces):
                break
        if faces is None or len(faces) == 0:
            return {"faces": 0, "t": 0.5}
        best = max(float(face[-1]) for face in faces)
        humans = human_rows(faces)
        face = max(humans, key=lambda row: row[2] * row[3])
        areas = sorted((float(row[2] * row[3]) for row in humans), reverse=True)
        vector = self.rec.feature(self.rec.alignCrop(small, face))[0]
        vector = vector / np.linalg.norm(vector)
        return {
            "faces": int(len(humans)),
            "an": int(len(faces) - len(humans)),
            "s": round(best, 2),
            "f2": round(areas[1] / areas[0], 2) if len(areas) > 1 else 0,
            "v": [round(float(value), 5) for value in vector],
            "box": [
                round(float(face[0]) / sw, 4),
                round(float(face[1]) / sh, 4),
                round(float(face[2]) / sw, 4),
                round(float(face[3]) / sh, 4),
            ],
            "px": int(min(face[2], face[3]) / scale),
        }

    def faces(self, image):
        """Return human and non-human face boxes in the source image's pixels."""
        import cv2

        if self.det is None:
            self.load()
        img = np.asarray(image.convert("RGB"))[:, :, ::-1].copy()
        height, width = img.shape[:2]
        scale = 1600 / max(height, width) if max(height, width) > 1600 else 1.0
        small = cv2.resize(img, (int(width * scale), int(height * scale))) if scale != 1.0 else img
        self.det.setInputSize((small.shape[1], small.shape[0]))
        found = None
        for threshold in (0.7, 0.5):
            self.det.setScoreThreshold(threshold)
            _, found = self.det.detect(small)
            if found is not None and len(found):
                break
        rows = list(found) if found is not None else []
        humans = human_rows(rows) if rows else []

        def boxes(found_rows):
            return sorted(
                (
                    tuple(float(value) / scale for value in row[:4])
                    for row in found_rows
                ),
                key=lambda box: box[2] * box[3],
                reverse=True,
            )

        return boxes(humans), boxes([row for row in rows if not any(row is human for human in humans)])


def human_rows(rows):
    best = max(float(row[-1]) for row in rows)
    return [row for row in rows if float(row[-1]) >= HUMAN_MIN] if best >= HUMAN_BEST else list(rows)


class Cache:
    """Cache face data by content hash and avoid rereading unchanged files."""

    def __init__(self, path):
        self.path = pathlib.Path(path)
        data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}
        self.stat, self.emb = data.get("stat", {}), data.get("emb", {})
        self.emb = {
            key: value
            for key, value in self.emb.items()
            if not (value.get("faces") == 0 and "t" not in value)
            and not (value.get("faces", 0) > 1 and "f2" not in value)
            and not (value.get("v") and "s" not in value)
        }

    def sha(self, path):
        stat = path.stat()
        key = str(path)
        hit = self.stat.get(key)
        if hit and hit[0] == stat.st_size and hit[1] == stat.st_mtime_ns:
            return hit[2]
        digest = hashlib.sha1(path.read_bytes()).hexdigest()
        self.stat[key] = [stat.st_size, stat.st_mtime_ns, digest]
        return digest

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"stat": self.stat, "emb": self.emb}), encoding="utf-8")


class Photo:
    def __init__(self, path, group, folder, sha, data):
        self.path, self.group, self.folder, self.sha = path, group, folder, sha
        self.key = group if group == folder else f"{group}/{folder}"
        self.faces = (data or {}).get("faces", -1)
        self.f2 = (data or {}).get("f2", 0)
        self.animals = (data or {}).get("an", 0)
        self.raw = np.array(data["v"], float) if data and data.get("v") else None
        self.box = (data or {}).get("box")
        self.px = (data or {}).get("px", 0)
        self.name = path.name
        self.vec = None

    def usable(self, min_face):
        return self.raw is not None and self.px >= min_face


def settings(cfg):
    result = dict(SETTINGS)
    result.update(cfg.get("likeness", {}))
    return result


def is_sister(key):
    """Return whether a folder is under the active Sisters root."""
    return key.split("/")[0] in cw.SISTER_ROOTS


def pool_home(configuration):
    """Return the library's configured destination for unassigned photos."""
    return configuration.get("poolHome") or configuration["pool"][0]


def side(key):
    """Return the source-side family used to prevent mixing artists and prospects."""
    top = key.split("/")[0].lower()
    if top == "artists":
        return "Artists"
    if top in ("models", "prospects", "potentials", "various"):
        return "Prospects"
    return None


def apart(first, second):
    """Whether two folders belong to different non-cast source populations."""
    first_side, second_side = side(first), side(second)
    return bool(first_side and second_side and first_side != second_side)


def new_home(key, name, photo_count=1):
    """Return the folder where a split-off identity should be created."""
    parts = key.split("/")
    if side(key) == "Artists" and len(parts) >= 3:
        return "/".join(parts[:2] + [name])
    return unassigned_home(name, photo_count)


def unassigned_home(name, photo_count):
    return f"{'Prospects' if photo_count >= 5 else 'Potentials'}/{name}"


def matches(key, patterns):
    """Match a folder key against patterns with one `*` per folder segment."""
    parts = key.lower().split("/")
    for pattern in patterns:
        pattern_parts = pattern.lower().split("/")
        if len(pattern_parts) == len(parts) and all(
            fnmatch.fnmatch(part, pattern_part)
            for part, pattern_part in zip(parts, pattern_parts)
        ):
            return True
    return False


def read_library(cfg, work, cache, embed, configuration, progress=True, with_mixed=False):
    """Read person folders and the pool, optionally including other mixed folders."""
    photos, todo = [], []
    for group, name, folder in cw.photo_folders(cfg, work):
        key = f"{group}/{name}"
        if matches(key, configuration["mixed"]) and not matches(key, configuration["pool"]) and not with_mixed:
            continue
        todo.extend((path, group, name) for path in originals.images(folder / "gallery"))
    done = 0
    for path, group, folder in todo:
        digest = cache.sha(path)
        if digest not in cache.emb:
            try:
                cache.emb[digest] = embed(path) or {"faces": -1}
            except Exception as error:  # A single unreadable photo must not stop a library scan.
                print(f"  cannot read {path.name}: {error}")
                cache.emb[digest] = {"faces": -1}
            done += 1
            if progress and done % 25 == 0:
                print(f"  ... {done} new photo(s) read")
                cache.save()
        photos.append(Photo(path, group, folder, digest, cache.emb[digest]))
    if done:
        cache.save()
    return photos


class Space:
    """Centered identity vectors, folder centroids, and photo-to-folder rankings."""

    def __init__(self, photos, configuration):
        self.st = configuration
        self.photos = photos
        self.pool_keys = set()
        person = [
            photo
            for photo in photos
            if photo.usable(configuration["minFace"])
            and not matches(photo.key, configuration["mixed"])
        ]
        self.person = person
        self.mean = np.mean([photo.raw for photo in person], axis=0) if person else np.zeros(128)
        for photo in photos:
            if photo.raw is not None:
                photo.vec = nz(photo.raw - self.mean)
        self.by_key = collections.defaultdict(list)
        for photo in person:
            self.by_key[photo.key].append(photo)
        self.keys = sorted(self.by_key)

    def centroid(self, key, skip=None):
        vectors = [photo.vec for photo in self.by_key.get(key, []) if photo is not skip]
        return nz(np.mean(vectors, axis=0)) if vectors else None

    def ranking(self, vec, skip=None, own=None, source=None):
        """Rank identity centroids, excluding a photo's own folder contribution."""
        ranked = []
        for key in self.keys:
            if source and apart(source, key):
                continue
            centroid = self.centroid(key, skip=skip if key == own else None)
            if centroid is not None:
                ranked.append((float(vec @ centroid), key))
        return sorted(ranked, reverse=True)

    def pair_matrix(self):
        centroids = {key: self.centroid(key) for key in self.keys}
        scores = {
            (first, second): float(centroids[first] @ centroids[second])
            for first, second in itertools.combinations(self.keys, 2)
        }
        return centroids, scores


def cluster(vectors, threshold):
    """Average-linkage cluster indices until no pair meets the cosine threshold."""
    count = len(vectors)
    similarities = vectors @ vectors.T
    groups = [[index] for index in range(count)]
    while len(groups) > 1:
        best, first_index, second_index = -2, 0, 0
        for first in range(len(groups)):
            for second in range(first + 1, len(groups)):
                score = float(np.mean(similarities[np.ix_(groups[first], groups[second])]))
                if score > best:
                    best, first_index, second_index = score, first, second
        if best < threshold:
            break
        groups[first_index] += groups[second_index]
        del groups[second_index]
    return groups
