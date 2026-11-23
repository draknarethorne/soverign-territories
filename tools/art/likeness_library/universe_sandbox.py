"""Identity-universe sandboxes: a small, disposable Sandbox Working built from verified evidence.

IU1 selects a named identity's related "universe" from the clean pre-rebase
inventory, the latest Sandbox placement and saved face vectors, then copies
byte-verified pre-rebase originals into a separate
``...\\Sovereign Territories Sandbox\\Working`` root outside the main Sandbox.
IU6 ``--mode empty`` creates the same valid layout with no photos.

Production and the main Sandbox are only read. Preview (the default) writes
nothing; ``--apply`` builds the new Working in a sibling staging folder and
renames it into place; ``--check`` rehashes every recorded copy.

Scores (documented in the report): each pre-rebase source is measured on its
sealed-preparation selected native, looked up in the engine cache by that
native's content digest (``engine.Cache.sha``). Vectors are centred with the
cache's saved ``centeringMean`` and normalised (``scoring.nz``), exactly as
``engine.Space`` does; centroids are normalised means of usable members
(``minFace`` from the policy). An identity joins at hop 1 when its centroid,
any member photo, or any seed photo against its centroid reaches the
``--expand-band`` minimum (default yellow) against the seed centroid/seed
photos. Scores compare distinct photos only: an identity whose pre-rebase
member now sits in the seed is included as ``shares-N-seed-photo(s)`` instead
of scoring that photo against itself. Hop 2 repeats from the hop-1 identities
at ``--hop2-band`` (default green). Various photos join when they reach the
band against the seed centroid. ``--include`` identities are hop-0 content;
only ``--seed`` photos are the expansion reference.

``--mode empty`` with ``--source-folder DIR`` copies every top-level image in
DIR (read-only) into ``Various/gallery`` with its name and times, verifies
each copy by SHA-256 and records a manifest; ``--check`` rehashes them.
``--source-various DIR`` instead reads a hand-sorted Various tree: ``DIR\\gallery``
becomes ``Various/gallery`` and every other ``DIR\\<Name>`` (or its ``gallery``)
becomes protected named intake ``Various/<Name>/gallery``.
"""
import argparse
import base64
import collections
import datetime
import hashlib
import html
import io
import json
import os
import pathlib
import re
import shutil
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
for _path in (ROOT, ROOT / "tools" / "art", ROOT / "tools" / "workflows"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
if not __package__:
    __package__ = "tools.art.likeness_library"

from tools.art.likeness_library import engine, metadata, sandbox  # noqa: E402
from tools.art.likeness_library.policy import effective_settings, load_policy  # noqa: E402
from tools.art.likeness_library.scoring import nz  # noqa: E402
from tools.workflows import comfy_workflows as cw  # noqa: E402

SCHEMA_VERSION = 1
MANIFEST_KIND = "identity-universe-sandbox"
UNIVERSE_REPORTS = ("library", "universe")
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
BANDS = ("green", "yellow", "orange")
LOWER_BAND = {"green": "yellow", "yellow": "orange", "orange": None}
SOURCE_STATUSES = ("eligible", "same-content-nonvoting", "confirmed-no-face-junk", "duplicate-archive")
STAGING_SUFFIX = ".universe-staging"
IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp", ".bmp"})
PRISTINE = "Universe-Source"
CHUNK = 1024 * 1024
THUMB = (96, 120)

# Read-only evidence defaults, relative to the configured main Sandbox. Every
# one can be overridden on the command line.
PRE_WORKING = "Working-before-post-intake-fresh-20261122-01"
PRE_RECEIPT = "_reports/runs/normal-rebase-simple-newpc-lean-20261121-03.json"
PRE_BACKUP = "_backup/library-20261121-020152"
CURRENT_RECEIPT = "_reports/runs/normal-rebase-feedback-rebase-20261122-02.json"
CURRENT_REVIEW = "_reports/library/people_gallery_review.html"
CACHE = "_likeness/general/simple-newpc-lean-20261121-03-cache.json"
FACE_EVIDENCE = "_likeness/general/face-evidence"
PREPARATION = (
    "_reports/runs/normal-rebase-simple-newpc-lean-20261120-02-preview/preparation/inputs"
    "/_reports/preparation/selected"
)
PREPARATION_SHA256 = "3545dd20e4c9b8df4972041590116cfcb46111011eb9b1a20dcd8413966cf0dc"


class UniverseError(ValueError):
    """A refused universe operation; nothing beyond staging was written."""


# ----------------------------------------------------------------- utilities

def _sha256(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def _copy_verified(source, destination, expected=None):
    """Stream-copy with a read hash, preserve times, then rehash the copy."""
    source, destination = pathlib.Path(source), pathlib.Path(destination)
    if sandbox._is_reparse_point(source) or not source.is_file():
        raise UniverseError(f"refusing missing or linked source: {source}")
    if destination.exists():
        raise UniverseError(f"refusing to overwrite: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with source.open("rb") as reader, destination.open("xb") as writer:
        for block in iter(lambda: reader.read(CHUNK), b""):
            digest.update(block)
            writer.write(block)
    shutil.copystat(source, destination)
    value = digest.hexdigest()
    if expected is not None and value != expected:
        raise UniverseError(f"source bytes differ from the recorded SHA-256: {source}")
    if _sha256(destination) != value:
        raise UniverseError(f"copy verification failed: {destination}")
    return value, destination.stat().st_size


def _overlaps(first, second):
    first, second = pathlib.Path(first).resolve(), pathlib.Path(second).resolve()
    return first == second or first in second.parents or second in first.parents


def _identity_name(key):
    return key.split("/", 1)[1] if "/" in key else key


def _band_minimum(policy, band):
    try:
        return float(policy["scoreBands"][band]["minimum"])
    except (KeyError, TypeError, ValueError) as exc:
        raise UniverseError(f"policy scoreBands has no {band} minimum") from exc


def default_paths(cfg):
    working = pathlib.Path(cw.sandbox_work_root(cfg))
    main = working.parent
    pre = main / PRE_WORKING
    return {
        "mainSandbox": main,
        "preReceipt": pre / PRE_RECEIPT,
        "currentReceipt": working / CURRENT_RECEIPT,
        "currentReview": working / CURRENT_REVIEW,
        "cache": working / CACHE,
        "faceEvidence": working / FACE_EVIDENCE,
        "preparation": working / PREPARATION,
        "originals": [main / "Source", pre / PRE_BACKUP],
        "universes": main.parent / "Sovereign Territories Universes",
    }


def validate_out_root(out_root, cfg, *, main_sandbox=None):
    """A Sandbox Working outside Production and the main Sandbox."""
    path = pathlib.Path(out_root).expanduser()
    if not path.is_absolute():
        raise UniverseError("--out-root must be absolute")
    if not sandbox.is_sandbox_working_path(path):
        raise UniverseError("--out-root must end with 'Sovereign Territories Sandbox\\Working'")
    for candidate in (path, *path.parents):
        if sandbox._is_reparse_point(candidate):
            raise UniverseError(f"refusing linked out-root component: {candidate}")
    main = pathlib.Path(main_sandbox or pathlib.Path(cw.sandbox_work_root(cfg)).parent)
    production = pathlib.Path(cw.production_root(cfg))
    if _overlaps(path.parent, main):
        raise UniverseError(f"universe Sandbox must be outside the main Sandbox: {main}")
    if _overlaps(path.parent, production):
        raise UniverseError(f"universe Sandbox must be outside Production: {production}")
    if any(parent.name.casefold() == "sovereign territories" for parent in path.parents):
        raise UniverseError("universe Sandbox must not be inside a Production library")
    return path.resolve()


# ------------------------------------------------------------------ evidence

def load_pre_rows(path):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if data.get("kind") != "normal-rebase-receipt" or data.get("status") != "applied":
        raise UniverseError(f"pre-rebase inventory is not an applied rebase receipt: {path}")
    rows = data.get("plan", {}).get("sourceRows") or data.get("sourceRows")
    if not isinstance(rows, list) or not rows:
        raise UniverseError("pre-rebase receipt has no sourceRows")
    return rows


def load_review_records(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    match = re.search(r'<script[^>]*id="review-data"[^>]*>(.*?)</script>', text, re.S)
    if not match:
        raise UniverseError(f"no review-data block in {path}")
    records = json.loads(match.group(1))
    if not isinstance(records, list):
        raise UniverseError("review-data is not a list of records")
    return records


def load_current_moves(path):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if data.get("kind") != "normal-rebase-receipt" or data.get("status") != "applied":
        raise UniverseError(f"current state is not an applied rebase receipt: {path}")
    return data.get("moves", [])


def _folder_of(relative):
    parts = pathlib.PurePosixPath(relative).parts
    if len(parts) >= 3 and parts[-2] in ("gallery", "review"):
        return "/".join(parts[:-2]), parts[-2]
    return "/".join(parts[:-1]), None


def current_placements(records, moves):
    """photoId -> current folder/bucket/score; Review data wins over receipt moves."""
    placements = {}
    for move in moves:
        folder, bucket = _folder_of(move["destination"])
        placements[move["photoId"]] = {
            "folder": folder, "bucket": (bucket or "").capitalize() or None,
            "score": None, "closest": [], "evidence": "latest-receipt-move",
        }
    for record in records:
        photo_id = record.get("photoId")
        if not photo_id:
            continue
        placements[photo_id] = {
            "folder": record.get("folder"), "bucket": record.get("bucket"),
            "score": record.get("score"),
            "closest": [
                {"folder": row.get("folder"), "score": row.get("score")}
                for row in (record.get("closestMatches") or [])[:3]
            ],
            "evidence": "review-data",
        }
    return placements


def load_preparation(output, expected_sha256):
    output = pathlib.Path(output)
    manifest = output / "manifest.json"
    if _sha256(manifest) != expected_sha256:
        raise UniverseError("sealed preparation manifest SHA-256 differs from the requested seal")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    by_hash = collections.defaultdict(list)
    for row in data["photos"]:
        by_hash[row["sourceSha256"]].append(row)
    return data, by_hash


def selected_relative(row):
    """The selected native's relative path (same rule as clean_preparation.selected_path).

    Bytes are not rehashed here; preview scoring trusts the engine cache's
    stat-bound digest, and apply/rebase rehash every copied artifact.
    """
    use = row.get("recommendation", {}).get("use", "none")
    if use in ("original", "none"):
        return row["retained"]
    variant = row["variants"].get(use)
    if not variant:
        raise UniverseError(f"recommended preparation output is missing: {row['source']}")
    return variant["path"]


class Vectors:
    """Centred, normalised cache vectors for pre-rebase rows."""

    def __init__(self, cache, preparation_output, preparation_rows, min_face):
        self.cache = cache
        self.output = pathlib.Path(preparation_output)
        self.rows = preparation_rows
        self.min_face = min_face
        mean = cache.centering_mean
        self.mean = np.asarray(mean, float) if mean is not None else None
        self.mean_source = "cache centeringMean" if mean is not None else None
        self._vectors = {}

    def measure(self, sources):
        raw = {}
        for source in sources:
            row = self.rows.get(source)
            if row is None:
                continue
            native = self.output.joinpath(*pathlib.PurePosixPath(selected_relative(row)).parts)
            if not native.is_file():
                continue
            data = self.cache.emb.get(self.cache.sha(native)) or {}
            if data.get("v") and data.get("px", 0) >= self.min_face:
                raw[source] = np.asarray(data["v"], float)
        if self.mean is None:
            if not raw:
                raise UniverseError("no usable cached vectors and no saved centering mean")
            self.mean = np.mean(list(raw.values()), axis=0)
            self.mean_source = "mean of usable pre-rebase vectors (cache had no centeringMean)"
        self._vectors = {source: nz(value - self.mean) for source, value in raw.items()}
        return self._vectors

    def get(self, source):
        return self._vectors.get(source)


def _centroid(vectors):
    vectors = [vector for vector in vectors if vector is not None]
    return nz(np.mean(vectors, axis=0)) if vectors else None


def _relation(members, centroid, ref_members, ref_centroid):
    """Best of centroid-centroid, member->reference centroid, reference member->centroid."""
    best = (None, None)
    if centroid is not None and ref_centroid is not None:
        best = max(best, (float(centroid @ ref_centroid), "centroid"), key=_score_key)
    if ref_centroid is not None and members:
        value = max(float(vector @ ref_centroid) for vector in members)
        best = max(best, (value, "member-vs-seed-centroid"), key=_score_key)
    if centroid is not None and ref_members:
        value = max(float(vector @ centroid) for vector in ref_members)
        best = max(best, (value, "seed-member-vs-centroid"), key=_score_key)
    return best


def _score_key(pair):
    return -2.0 if pair[0] is None else pair[0]


# ----------------------------------------------------------------- selection

def resolve_names(requested, known):
    """Map CATEGORY/Name requests onto known identity keys (casefold, then name only)."""
    by_key = collections.defaultdict(set)
    by_name = collections.defaultdict(set)
    for key in known:
        by_key[key.casefold()].add(key)
        by_name[_identity_name(key).casefold()].add(key)
    resolved, missing = {}, []
    for request in requested:
        exact = sorted(by_key.get(request.casefold(), ()))
        matches = exact or sorted(by_name.get(_identity_name(request).casefold(), ()))
        if matches:
            resolved[request] = matches
        else:
            missing.append(request)
    return resolved, missing


def select_universe(pre_rows, placements, preparation_by_hash, vectors_factory, policy, *,
                    seeds, includes, band="yellow", hop2_band=None, hops=1, max_photos=1500):
    """Deterministic universe selection; returns the plan without touching disk."""
    if hops not in (0, 1, 2):
        raise UniverseError("--hops must be 0, 1 or 2")
    band_min = _band_minimum(policy, band)
    hop2_band = hop2_band or "green"
    hop2_min = _band_minimum(policy, hop2_band)
    lower = LOWER_BAND[band]
    lower_min = _band_minimum(policy, lower) if lower else None

    rows = [row for row in pre_rows if row.get("sourceStatus") in SOURCE_STATUSES]
    by_photo = collections.defaultdict(list)
    for row in rows:
        by_photo[row["photoId"]].append(row)

    def current_of(row):
        return placements.get(row["photoId"]) or {}

    owners = sorted({row["owner"] for row in rows})
    current_folders = sorted({value["folder"] for value in placements.values() if value.get("folder")})
    known = sorted(set(owners) | set(current_folders))
    seed_map, seed_missing = resolve_names(seeds, known)
    include_map, include_missing = resolve_names(includes, known)
    seed_keys = sorted({key for keys in seed_map.values() for key in keys})
    include_keys = sorted({key for keys in include_map.values() for key in keys} - set(seed_keys))
    if seeds and not seed_keys:
        raise UniverseError(f"no seed identity found: {', '.join(seeds)}")

    reasons = collections.defaultdict(list)
    hop_of = {}

    def add(row, reason, hop):
        if reason not in reasons[row["source"]]:
            reasons[row["source"]].append(reason)
        hop_of[row["source"]] = min(hop, hop_of.get(row["source"], hop))

    for label, keys, hop in (("seed", seed_keys, 0), ("include", include_keys, 0)):
        lowered = {key.casefold() for key in keys}
        for row in rows:
            if row["owner"].casefold() in lowered:
                add(row, f"{label}-original-owner:{row['owner']}", hop)
            folder = (current_of(row).get("folder") or "")
            if folder.casefold() in lowered:
                add(row, f"{label}-current-placement:{folder}/{current_of(row).get('bucket')}", hop)

    vectors = vectors_factory([row["source"] for row in rows])
    seed_sources = [row["source"] for row in rows if any(r.startswith("seed-") for r in reasons.get(row["source"], ()))]
    seed_members = [vectors.get(source) for source in seed_sources if vectors.get(source) is not None]
    seed_centroid = _centroid(seed_members)

    identity_members = collections.defaultdict(list)
    for row in rows:
        if row["group"] != "Various":
            identity_members[row["owner"]].append(row)
    centroids = {
        owner: _centroid([vectors.get(row["source"]) for row in members])
        for owner, members in identity_members.items()
    }
    universe_keys = {key.casefold() for key in seed_keys + include_keys}
    identities = []
    for key in seed_keys:
        identities.append({"identity": key, "hop": 0, "reason": "seed", "bestScore": None,
                           "scoreBasis": None, "via": None})
    for key in include_keys:
        identities.append({"identity": key, "hop": 0, "reason": "user-include", "bestScore": None,
                           "scoreBasis": None, "via": None})

    candidates = []
    interesting = []
    seed_source_set = set(seed_sources)
    shared_owner = {}
    if hops >= 1 and seed_centroid is not None:
        relations = {}
        for owner, members in identity_members.items():
            if owner.casefold() in universe_keys:
                continue
            # A photo that is both a seed photo (it now sits in the seed) and a
            # member of this identity would score 1.0 against itself; scores
            # compare only distinct photos, and the shared photo is recorded.
            shared = {row["source"] for row in members} & seed_source_set
            member_vectors = [vectors.get(row["source"]) for row in members
                              if row["source"] not in shared and vectors.get(row["source"]) is not None]
            reference = [vectors.get(source) for source in seed_sources
                         if source not in shared and vectors.get(source) is not None]
            own_centroid = _centroid([vectors.get(row["source"]) for row in members if row["source"] not in shared])
            score, basis = _relation(member_vectors, own_centroid, reference, _centroid(reference))
            if shared and (score is None or score < band_min):
                shared_owner[owner] = len(shared)
                basis = f"shares-{len(shared)}-seed-photo(s)"
            relations[owner] = (score, basis)

        def sort_value(owner):
            return relations[owner][0] if relations[owner][0] is not None else -1.0

        hop1 = sorted(
            (owner for owner, (score, _basis) in relations.items()
             if owner in shared_owner or (score is not None and score >= band_min)),
            key=lambda owner: (-sort_value(owner), owner),
        )
        for owner in hop1:
            candidates.append((1, -sort_value(owner), owner, relations[owner][1], "seed"))
        if lower_min is not None:
            interesting = sorted(
                ({"identity": owner, "bestScore": round(score, 4), "scoreBasis": basis,
                  "band": lower, "photos": len(identity_members[owner])}
                 for owner, (score, basis) in relations.items()
                 if owner not in shared_owner and score is not None and lower_min <= score < band_min),
                key=lambda row: (-row["bestScore"], row["identity"]),
            )
        if hops >= 2:
            taken = set(hop1) | {key for key in identity_members if key.casefold() in universe_keys}
            second = {}
            for via in hop1:
                via_members = [vectors.get(row["source"]) for row in identity_members[via]
                               if vectors.get(row["source"]) is not None]
                for owner, members in identity_members.items():
                    if owner in taken:
                        continue
                    member_vectors = [vectors.get(row["source"]) for row in members
                                      if vectors.get(row["source"]) is not None]
                    score, basis = _relation(member_vectors, centroids[owner], via_members, centroids[via])
                    if score is not None and score >= hop2_min and (
                        owner not in second or score > second[owner][0]
                    ):
                        second[owner] = (score, basis, via)
            for owner, (score, basis, via) in sorted(second.items(), key=lambda item: (-item[1][0], item[0])):
                candidates.append((2, -score, owner, basis, via))
        for row in rows:
            if row["group"] != "Various" or row["source"] in reasons:
                continue
            vector = vectors.get(row["source"])
            if vector is not None:
                score = float(vector @ seed_centroid)
                if score >= band_min:
                    candidates.append((1, -score, row["source"], "various-vs-seed-centroid", "seed"))

    # Hop-0 content first, then bounded expansion in (hop, score) order.
    def coverage(row):
        return row["sourceHash"] in preparation_by_hash

    def chosen_sources():
        return {source for source in reasons}

    bounded_out = []
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    by_source = {row["source"]: row for row in rows}
    for hop, negative, key, basis, via in candidates:
        best = round(-negative, 4) if negative < 1.0 else None  # None: no distinct usable vectors
        if key in identity_members:
            members = identity_members[key]
            new = [row for row in members if row["source"] not in reasons]
            if len(chosen_sources()) + len(new) > max_photos:
                bounded_out.append({"identity": key, "hop": hop, "bestScore": best,
                                    "photos": len(members)})
                continue
            identities.append({"identity": key, "hop": hop, "reason": f"hop{hop}-{basis}",
                               "bestScore": best, "scoreBasis": basis, "via": via,
                               "sharedSeedPhotos": shared_owner.get(key, 0)})
            for row in members:
                add(row, f"hop{hop}-identity:{key}", hop)
        else:
            if len(chosen_sources()) + 1 > max_photos:
                bounded_out.append({"photo": key, "hop": hop, "bestScore": round(-negative, 4)})
                continue
            add(by_source[key], f"hop{hop}-various:{round(-negative, 4)}", hop)

    # Content-level dedupe and preparation coverage.
    photos, excluded = [], []
    by_hash = collections.defaultdict(list)
    for source in reasons:
        by_hash[by_source[source]["sourceHash"]].append(by_source[source])
    status_rank = {status: index for index, status in enumerate(SOURCE_STATUSES)}
    for digest, group in sorted(by_hash.items()):
        group.sort(key=lambda row: (status_rank[row["sourceStatus"]], row["source"].casefold()))
        keeper = group[0]
        for other in group[1:]:
            excluded.append({"source": other["source"], "photoId": other["photoId"],
                             "reason": f"identical content kept once as {keeper['source']}"})
        if not coverage(keeper):
            excluded.append({"source": keeper["source"], "photoId": keeper["photoId"],
                             "reason": "no sealed-preparation row for this content; reuse would fail"})
            continue
        current = current_of(keeper)
        vector = vectors.get(keeper["source"])
        merged = []
        for row in group:
            merged.extend(reason for reason in reasons[row["source"]] if reason not in merged)
        photos.append({
            "photoId": keeper["photoId"], "preSource": keeper["source"],
            "sourceSha256": digest, "originalOwner": keeper["owner"],
            "preBucket": keeper["bucket"], "preStatus": keeper["sourceStatus"],
            "originalName": pathlib.PurePosixPath(keeper["source"]).name,
            "currentFolder": current.get("folder"), "currentBucket": current.get("bucket"),
            "currentScore": current.get("score"), "currentEvidence": current.get("evidence"),
            "currentClosest": current.get("closest", []),
            "hop": min(hop_of[row["source"]] for row in group),
            "reasons": merged,
            "seedScore": None if vector is None or seed_centroid is None else round(float(vector @ seed_centroid), 4),
            "usableVector": vector is not None,
        })
    # Same stable ID with different bytes cannot coexist in one blank Various.
    by_id = collections.defaultdict(list)
    for photo in photos:
        by_id[photo["photoId"]].append(photo)
    for photo_id, group in by_id.items():
        if len(group) > 1:
            group.sort(key=lambda row: (row["hop"], row["preStatus"] != "eligible", row["preSource"].casefold()))
            for other in group[1:]:
                photos.remove(other)
                excluded.append({"source": other["preSource"], "photoId": photo_id,
                                 "reason": f"same photo ID with different content; kept {group[0]['preSource']}"})
    photos.sort(key=lambda row: row["preSource"].casefold())
    return {
        "seeds": seed_map, "includes": include_map,
        "notFound": seed_missing + include_missing,
        "band": band, "bandMinimum": band_min, "hop2Band": hop2_band, "hop2Minimum": hop2_min,
        "hops": hops, "maxPhotos": max_photos,
        "centering": vectors.mean_source,
        "seedVectorCount": len(seed_members),
        "identities": identities, "interestingNotIncluded": interesting,
        "boundedOut": bounded_out, "excluded": sorted(excluded, key=lambda row: row["source"]),
        "photos": photos,
    }


def assign_destinations(photos, mode, seed_names=()):
    """Every photo goes to Various/gallery under its original name; collisions get _uN."""
    taken = set()
    for photo in photos:
        name = photo["originalName"]
        stem, suffix = os.path.splitext(name)
        candidate, counter = name, 1
        while candidate.casefold() in taken:
            counter += 1
            candidate = f"{stem}_u{counter}{suffix}"
        if metadata.photo_id_from_name(candidate) not in (None, photo["photoId"]):
            raise UniverseError(f"renamed copy would change its photo ID: {candidate}")
        taken.add(candidate.casefold())
        photo["destination"] = f"Various/gallery/{candidate}"
    staging = [f"Various/{name}/gallery" for name in seed_names] if mode == "named" else []
    return staging


# --------------------------------------------------------------- byte lookup

class Originals:
    """Find pre-rebase bytes by SHA-256: preparation, then Source, then backup."""

    def __init__(self, preparation_output, preparation_data, preparation_by_hash, originals_roots):
        self.output = pathlib.Path(preparation_output)
        self.mirror = self.output.parents[2]
        self.by_hash = preparation_by_hash
        self.roots = [pathlib.Path(root) for root in originals_roots]
        self._backup = None

    def _backup_index(self):
        if self._backup is None:
            self._backup = {}
            for root in self.roots:
                manifest = root / "manifest.json"
                if not manifest.is_file():
                    continue
                data = json.loads(manifest.read_text(encoding="utf-8"))
                for entry in data.get("entries", ()):
                    if isinstance(entry.get("sha256"), str) and entry.get("backup"):
                        self._backup.setdefault(
                            entry["sha256"], root.joinpath(*pathlib.PureWindowsPath(entry["backup"]).parts),
                        )
        return self._backup

    def candidates(self, photo):
        digest = photo["sourceSha256"]
        for row in self.by_hash.get(digest, ()):
            yield "preparation-retained-original", self.output.joinpath(
                *pathlib.PurePosixPath(row["retained"]).parts)
            yield "preparation-input-mirror", self.mirror.joinpath(
                *pathlib.PurePosixPath(row["source"]).parts)
        for root in self.roots:
            if not (root / "manifest.json").is_file():
                yield f"source:{root}", root.joinpath(*pathlib.PurePosixPath(photo["preSource"]).parts)
        backup = self._backup_index().get(digest)
        if backup is not None:
            yield "backup", backup

    def find(self, photo):
        for origin, path in self.candidates(photo):
            if path.is_file() and not sandbox._is_reparse_point(path) and _sha256(path) == photo["sourceSha256"]:
                return origin, path
        return None, None


# ------------------------------------------------------------------- reports

def _thumbnail(path):
    try:
        from PIL import Image, ImageOps

        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            image = ImageOps.fit(image, THUMB, Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            image.save(buffer, "JPEG", quality=72)
        return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
    except Exception as exc:  # A bad thumbnail must not hide a selected photo.
        print(f"  thumbnail unavailable for {path}: {exc}")
        return ""


def _esc(value):
    return html.escape("" if value is None else str(value))


def membership_html(manifest, thumbs):
    selection = manifest["selection"]
    photos = selection["photos"]
    counts = manifest["counts"]

    def table(rows, columns):
        head = "".join(f"<th>{_esc(label)}</th>" for label, _key in columns)
        body = "".join(
            "<tr>" + "".join(f"<td>{_esc(row.get(key))}</td>" for _label, key in columns) + "</tr>"
            for row in rows
        )
        return f"<table><thead><tr>{head}</tr></thead><tbody>{body or '<tr><td>none</td></tr>'}</tbody></table>"

    def groups(key):
        grouped = collections.defaultdict(list)
        for photo in photos:
            label = photo.get(key) or "(none)"
            if key == "currentFolder" and photo.get("currentBucket"):
                label = f"{label} / {photo['currentBucket']}"
            grouped[label].append(photo)
        parts = []
        for label in sorted(grouped, key=str.casefold):
            cards = "".join(
                f'<figure title="{_esc(photo["preSource"])}"><img data-id="{_esc(photo["photoId"])}" alt="">'
                f'<figcaption>{_esc(photo["photoId"].split(":", 1)[-1][-10:])}<br>'
                f'seed {_esc(photo["seedScore"])} | hop {photo["hop"]}</figcaption></figure>'
                for photo in grouped[label]
            )
            parts.append(f"<section><h3>{_esc(label)} ({len(grouped[label])})</h3><div class=grid>{cards}</div></section>")
        return "".join(parts)

    summary = "".join(f"<li>{_esc(key)}: {_esc(value)}</li>" for key, value in counts.items())
    parameters = "".join(f"<li>{_esc(key)}: {_esc(value)}</li>" for key, value in manifest["parameters"].items())
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Universe {_esc(manifest['name'])}</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;margin:16px;background:#fafafa}}table{{border-collapse:collapse;margin:8px 0}}
td,th{{border:1px solid #ccc;padding:3px 6px;font-size:13px}}.grid{{display:flex;flex-wrap:wrap;gap:6px}}
figure{{margin:0;width:{THUMB[0]}px;font-size:11px;text-align:center}}img{{width:{THUMB[0]}px;height:{THUMB[1]}px;background:#ddd}}
h3{{margin:14px 0 4px}}</style></head><body>
<h1>Identity universe: {_esc(manifest['name'])}</h1>
<p>Mode <b>{_esc(manifest['mode'])}</b>. Scores: cache vectors of each sealed-preparation native, centred with
{_esc(selection['centering'])}, normalised; identity = original pre-rebase owner. Band {_esc(selection['band'])}
&ge; {_esc(selection['bandMinimum'])}; hop 2 {_esc(selection['hop2Band'])} &ge; {_esc(selection['hop2Minimum'])}.</p>
<h2>Counts</h2><ul>{summary}</ul><h2>Parameters</h2><ul>{parameters}</ul>
<h2>Names not found</h2><p>{_esc(', '.join(selection['notFound']) or 'none')}</p>
<h2>Included identities</h2>{table(selection['identities'], [('Identity', 'identity'), ('Hop', 'hop'), ('Reason', 'reason'), ('Best score', 'bestScore'), ('Via', 'via')])}
<h2>Interesting, not included</h2>{table(selection['interestingNotIncluded'], [('Identity', 'identity'), ('Best score', 'bestScore'), ('Basis', 'scoreBasis'), ('Band', 'band'), ('Photos', 'photos')])}
<h2>Bounded out</h2>{table(selection['boundedOut'], [('Identity', 'identity'), ('Photo', 'photo'), ('Hop', 'hop'), ('Best score', 'bestScore')])}
<h2>Excluded photos</h2>{table(selection['excluded'], [('Source', 'source'), ('Photo ID', 'photoId'), ('Reason', 'reason')])}
<h2>By original owner (pre-rebase)</h2>{groups('originalOwner')}
<h2>By current owner (latest Sandbox)</h2>{groups('currentFolder')}
<script id="thumbs" type="application/json">{json.dumps(thumbs).replace('</', '<\\/')}</script>
<script>const T=JSON.parse(document.getElementById('thumbs').textContent);
document.querySelectorAll('img[data-id]').forEach(i=>{{if(T[i.dataset.id])i.src=T[i.dataset.id];}});</script>
</body></html>
"""


def empty_readme(out_root, cfg_policy, name, named_folders=0):
    root = str(out_root)
    cache = str(pathlib.Path(out_root) / "_likeness" / "general" / "cache.json")
    seed_step = f"""
   This universe has {named_folders} named folder(s). The SIMPLE rebase reads only
   `Various\\gallery`, so first turn each named folder into its Prospect or
   Potential (no face matching; preview, then apply):

```text
python tools\\art\\likeness.py --root "{root}" --no-originals seed
python tools\\art\\likeness.py --root "{root}" --no-originals seed --apply
```
""" if named_folders else ""
    return f"""# Empty universe Sandbox: {name}

This Working has the Sandbox layout but no photos, catalogue, cache,
preparation or history.

1. Copy your originals into `Various\\gallery` (unnamed intake), or into
   `Various\\<Name>\\gallery` when every photo in that folder is one person
   (named intake: run `likeness.py seed` before the rebase).
{seed_step}
2. Preview, apply and check a SIMPLE rebase (no `--reuse-preparation`; the
   first preview prepares and measures every photo):

```text
cmd /c bin\\normal-rebase.cmd --root "{root}" --cache "{cache}" --policy "{cfg_policy}" --profile lean --run-id {name}-01 --dry-run
cmd /c bin\\normal-rebase.cmd --root "{root}" --cache "{cache}" --policy "{cfg_policy}" --profile lean --run-id {name}-01 --apply --sandbox-apply-draft
cmd /c bin\\normal-rebase.cmd --root "{root}" --cache "{cache}" --policy "{cfg_policy}" --profile lean --run-id {name}-01 --check
```

Run commands from the repository root. Preview is always the default.
"""


# --------------------------------------------------------------------- apply

def _working_tree_files(root):
    for path in sorted(pathlib.Path(root).rglob("*")):
        if path.is_file():
            yield path


def build(args, cfg, policy, paths, *, apply):
    started = time.perf_counter()
    out_root = validate_out_root(args.out_root, cfg, main_sandbox=paths["mainSandbox"])
    sandbox_dir = out_root.parent
    staging = sandbox_dir / (out_root.name + STAGING_SUFFIX)
    pristine_root = sandbox_dir / PRISTINE
    for path in (out_root, staging, pristine_root):
        if path.exists():
            raise UniverseError(f"refusing to reuse an existing path; choose a new --name/--out-root: {path}")
    parameters = {
        "name": args.name, "mode": args.mode, "outRoot": str(out_root),
        "seeds": args.seed, "includes": args.include,
        "expandBand": args.expand_band,
        "hop2Band": args.hop2_band, "hops": args.hops, "maxPhotos": args.max_photos,
    }
    if args.mode == "empty":
        return _build_empty(args, cfg, out_root, staging, pristine_root, parameters, apply=apply, started=started)

    sources = {
        "preReceipt": pathlib.Path(args.pre_receipt or paths["preReceipt"]),
        "currentReceipt": pathlib.Path(args.current_receipt or paths["currentReceipt"]),
        "currentReview": pathlib.Path(args.current_review or paths["currentReview"]),
        "cache": pathlib.Path(args.source_cache or paths["cache"]),
        "faceEvidence": pathlib.Path(args.face_evidence or paths["faceEvidence"]),
        "preparation": pathlib.Path(args.preparation or paths["preparation"]),
    }
    originals_roots = [*map(pathlib.Path, paths["originals"]), *map(pathlib.Path, args.originals or ())]
    for label, path in sources.items():
        if not path.exists():
            raise UniverseError(f"missing {label}: {path}")
        if _overlaps(path, out_root.parent):
            raise UniverseError(f"{label} must not be inside the universe Sandbox: {path}")
    print("reading evidence ...", flush=True)
    pre_rows = load_pre_rows(sources["preReceipt"])
    placements = current_placements(load_review_records(sources["currentReview"]),
                                    load_current_moves(sources["currentReceipt"]))
    prep_data, prep_by_hash = load_preparation(sources["preparation"], args.preparation_sha256)
    prep_by_source = {}
    for row in pre_rows:
        candidates = prep_by_hash.get(row["sourceHash"], ())
        exact = [item for item in candidates if item["source"] == row["source"]]
        if exact or candidates:
            prep_by_source[row["source"]] = (exact or sorted(candidates, key=lambda item: item["source"]))[0]
    cache = engine.Cache(sources["cache"])
    settings = effective_settings(cfg, policy)
    vectors = Vectors(cache, sources["preparation"], prep_by_source, settings["minFace"])

    def factory(all_sources):
        vectors.measure(all_sources)
        return vectors

    selection = select_universe(
        pre_rows, placements, prep_by_hash, factory, policy,
        seeds=args.seed, includes=args.include,
        band=args.expand_band, hop2_band=args.hop2_band,
        hops=args.hops, max_photos=args.max_photos,
    )
    seed_names = sorted({_identity_name(key) for keys in selection["seeds"].values() for key in keys})
    staging_folders = assign_destinations(selection["photos"], args.mode, seed_names)
    lookup = Originals(sources["preparation"], prep_data, prep_by_hash, originals_roots)
    missing = []
    for photo in selection["photos"]:
        origin, path = lookup.find(photo)
        photo["bytesFrom"] = origin
        photo["bytesPath"] = None if path is None else str(path)
        if path is None:
            missing.append(photo["preSource"])
    counts = _counts(selection, staging_folders)
    _print_preview(selection, counts, missing, time.perf_counter() - started)
    if missing:
        raise UniverseError(f"{len(missing)} selected photo(s) have no verified pre-rebase bytes; refusing")
    if not apply:
        return 0

    manifest = {
        "kind": MANIFEST_KIND, "schemaVersion": SCHEMA_VERSION, "name": args.name, "mode": args.mode,
        "createdAt": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "parameters": parameters,
        "implementationSHA256": metadata.content_sha256(pathlib.Path(__file__)),
        "evidence": {
            label: {"path": str(path), "sha256": _sha256(path) if path.is_file() else None}
            for label, path in sources.items()
        },
        "preparationManifestSHA256": args.preparation_sha256,
        "originalsRoots": [str(path) for path in originals_roots],
        "counts": counts, "selection": selection, "stagingFolders": staging_folders, "files": [],
    }
    files = manifest["files"]
    thumbs = {}
    try:
        staging.mkdir(parents=True)
        (staging / "Various" / "gallery").mkdir(parents=True)
        for folder in staging_folders:
            (staging / pathlib.PurePosixPath(folder)).mkdir(parents=True, exist_ok=True)
        print(f"copying {len(selection['photos'])} verified originals ...", flush=True)
        for photo in selection["photos"]:
            relative = pathlib.PurePosixPath(photo["destination"])
            digest, size = _copy_verified(photo["bytesPath"], staging.joinpath(*relative.parts), photo["sourceSha256"])
            files.append({"kind": "working-photo", "path": f"Working/{relative}", "sha256": digest, "bytes": size})
            pristine = pristine_root.joinpath(*relative.parts)
            digest, size = _copy_verified(photo["bytesPath"], pristine, photo["sourceSha256"])
            files.append({"kind": "universe-source", "path": f"{PRISTINE}/{relative}", "sha256": digest, "bytes": size})
            thumbs[photo["photoId"]] = _thumbnail(pristine)
        reports_relative = cw.storage_root(cfg, "reports", root=out_root).relative_to(out_root)
        likeness_relative = cw.storage_root(cfg, "likeness", root=out_root).relative_to(out_root)
        prep = sources["preparation"]
        run_dir = prep.parents[4]
        complete_seal = run_dir / "preparation-origin.complete.json"
        sealed_root = (
            pathlib.Path(json.loads(complete_seal.read_text(encoding="utf-8"))["root"])
            if complete_seal.is_file() else run_dir.parents[2]
        )
        # Same path relative to Working as sealed, so the rebase can verify the relocation.
        prep_run_relative = run_dir.relative_to(sealed_root)
        print(f"copying sealed preparation {run_dir.name} (verifying every file) ...", flush=True)
        for seal in ("preparation-origin.start.json", "preparation-origin.complete.json"):
            if (run_dir / seal).is_file():
                digest, size = _copy_verified(run_dir / seal, staging / prep_run_relative / seal)
                files.append({"kind": "preparation", "path": f"Working/{(prep_run_relative / seal).as_posix()}",
                              "sha256": digest, "bytes": size})
        for path in _working_tree_files(run_dir / "preparation"):
            relative = prep_run_relative / path.relative_to(run_dir)
            digest, size = _copy_verified(path, staging / relative)
            files.append({"kind": "preparation", "path": f"Working/{relative.as_posix()}", "sha256": digest, "bytes": size})
        if _sha256(staging / prep_run_relative / prep.relative_to(run_dir) / "manifest.json") != args.preparation_sha256:
            raise UniverseError("copied preparation manifest differs from the requested seal")
        cache_relative = likeness_relative / "general" / sources["cache"].name
        for target_root, kind, prefix in ((staging, "working-likeness", "Working"),
                                          (pristine_root, "universe-source", PRISTINE)):
            digest, size = _copy_verified(sources["cache"], target_root / cache_relative)
            files.append({"kind": kind, "path": f"{prefix}/{cache_relative.as_posix()}", "sha256": digest, "bytes": size})
            for path in _working_tree_files(sources["faceEvidence"]):
                relative = likeness_relative / "general" / "face-evidence" / path.relative_to(sources["faceEvidence"])
                digest, size = _copy_verified(path, target_root / relative)
                files.append({"kind": kind, "path": f"{prefix}/{relative.as_posix()}", "sha256": digest, "bytes": size})
        universe_dir = staging / reports_relative.joinpath(*UNIVERSE_REPORTS)
        universe_dir.mkdir(parents=True)
        manifest["preparationReuse"] = {
            "path": str(out_root / prep_run_relative / prep.relative_to(run_dir)),
            "sha256": args.preparation_sha256,
            "cache": str(out_root / cache_relative),
        }
        manifest["elapsedSeconds"] = round(time.perf_counter() - started, 1)
        (universe_dir / "index.html").write_text(membership_html(manifest, thumbs), encoding="utf-8")
        if args.mode == "named":
            (universe_dir / "README-named-staging.md").write_text(_named_readme(selection, staging_folders), encoding="utf-8")
        manifest_path = universe_dir / "universe-manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
        staging.rename(out_root)
    except BaseException:
        print(f"universe build stopped; partial staging preserved for inspection: {staging}"
              f"{' and ' + str(pristine_root) if pristine_root.exists() else ''}", file=sys.stderr)
        raise
    print(f"universe applied: {out_root}")
    print(f"manifest: {out_root / reports_relative.joinpath(*UNIVERSE_REPORTS) / 'universe-manifest.json'} "
          f"(sha256 {_sha256(out_root / reports_relative.joinpath(*UNIVERSE_REPORTS) / 'universe-manifest.json')})")
    print(f"membership report: {out_root / reports_relative.joinpath(*UNIVERSE_REPORTS) / 'index.html'}")
    print(f"reuse: --reuse-preparation \"{manifest['preparationReuse']['path']}\" "
          f"--reuse-preparation-sha256 {args.preparation_sha256} --cache \"{manifest['preparationReuse']['cache']}\"")
    print(f"elapsed {time.perf_counter() - started:.1f}s")
    return 0


def _named_readme(selection, staging_folders):
    lines = ["# Named hand-pick staging", "",
             "Move the photos you are sure are this person from `Various/gallery` into the folder below.",
             "That folder is protected named intake: the next SIMPLE rebase keeps it together.", ""]
    lines += [f"- `{folder}`" for folder in staging_folders]
    lines += ["", "## Candidates (seed score, original owner, current owner)", ""]
    for photo in sorted(selection["photos"], key=lambda row: -(row["seedScore"] or -1)):
        lines.append(f"- `{photo['destination']}`: {photo['seedScore']} | {photo['originalOwner']} | "
                     f"{photo['currentFolder']}/{photo['currentBucket']}")
    return "\n".join(lines) + "\n"


def _validated_source(folder, out_root, cfg, option):
    folder = pathlib.Path(folder).expanduser()
    if not folder.is_absolute():
        raise UniverseError(f"{option} must be absolute")
    if not folder.is_dir() or sandbox._is_reparse_point(folder):
        raise UniverseError(f"{option} is not a plain folder: {folder}")
    folder = folder.resolve()
    if _overlaps(folder, out_root.parent):
        raise UniverseError(f"{option} must be outside the universe Sandbox")
    if _overlaps(folder, pathlib.Path(cw.production_root(cfg))):
        raise UniverseError(f"{option} must not be in Production (no new intake from Production)")
    return folder


def _top_level_images(folder, label, subfolder_reason):
    images, skipped = [], []
    for path in sorted(folder.iterdir(), key=lambda item: item.name.casefold()):
        name = f"{label}/{path.name}" if label else path.name
        if sandbox._is_reparse_point(path):
            skipped.append({"name": name, "reason": "linked entry"})
        elif path.is_dir():
            skipped.append({"name": name, "reason": subfolder_reason})
        elif path.suffix.casefold() not in IMAGE_EXTENSIONS:
            skipped.append({"name": name, "reason": "not an image"})
        else:
            images.append(path)
    return images, skipped


def source_folder_plan(folder, out_root, cfg):
    """Top-level images of a read-only folder; anything else is listed and skipped."""
    folder = _validated_source(folder, out_root, cfg, "--source-folder")
    images, skipped = _top_level_images(folder, "", "subfolder (only top-level images are copied)")
    return folder, [(path, f"Various/gallery/{path.name}") for path in images], skipped


def source_various_plan(folder, out_root, cfg):
    """A hand-sorted ``Various`` tree: ``gallery`` stays unnamed; each other subfolder is named intake.

    ``DIR/gallery/*`` -> ``Various/gallery``; ``DIR/<Name>/*`` and ``DIR/<Name>/gallery/*`` ->
    ``Various/<Name>/gallery``. Top-level files of DIR and deeper folders are skipped and listed.
    """
    folder = _validated_source(folder, out_root, cfg, "--source-various")
    planned, skipped = [], []
    for entry in sorted(folder.iterdir(), key=lambda item: item.name.casefold()):
        if sandbox._is_reparse_point(entry):
            skipped.append({"name": entry.name, "reason": "linked entry"})
            continue
        if not entry.is_dir():
            skipped.append({"name": entry.name, "reason": "top-level file (use gallery or a named folder)"})
            continue
        if entry.name.casefold() == "gallery":
            images, extra = _top_level_images(entry, entry.name, "nested folder inside gallery")
            planned += [(path, f"Various/gallery/{path.name}") for path in images]
            skipped += extra
            continue
        if entry.name.startswith((".", "_")) or entry.name != entry.name.strip():
            skipped.append({"name": entry.name, "reason": "not a usable identity folder name"})
            continue
        images, extra = _top_level_images(entry, entry.name, "nested folder (only <Name>/gallery is read)")
        inner = entry / "gallery"
        if inner.is_dir() and not sandbox._is_reparse_point(inner):
            extra = [row for row in extra if row["name"] != f"{entry.name}/gallery"]
            more, deeper = _top_level_images(inner, f"{entry.name}/gallery", "nested folder inside gallery")
            images += more
            extra += deeper
        names = collections.Counter(path.name.casefold() for path in images)
        clashes = sorted(name for name, count in names.items() if count > 1)
        if clashes:
            raise UniverseError(f"{entry.name}: same file name at both levels: {', '.join(clashes[:5])}")
        planned += [(path, f"Various/{entry.name}/gallery/{path.name}") for path in images]
        skipped += extra
    return folder, planned, skipped


def workflow_selected_arrivals(images, cfg):
    """Arrivals whose stable ID is a workflow-selected photo and whose name is not yet ID-bearing.

    The SIMPLE rebase refuses to move (rename) a workflow-selected photo, so
    stable-ID filename normalization of such an arrival stops its preview.
    This is reported only; the tool does not rename or skip anything.
    """
    from tools.art import originals
    from tools.art.likeness_library import normal_import

    names = list(cfg.get("photos", {}).values())
    for flow in cfg.get("flows", {}).values():
        names.extend(flow.get("photos", {}).values())
    selected = {}
    for name in names:
        photo_id = metadata.photo_id_from_name(name) if isinstance(name, str) else None
        if photo_id:
            selected[photo_id] = name
    found = []
    for path in images:
        if metadata.photo_id_from_name(path.name):
            continue
        try:
            photo_id = metadata.photo_id_from_name(normal_import._arrival_name(path, originals, metadata))
        except ValueError:
            continue
        if photo_id in selected:
            found.append({"name": path.name, "photoId": photo_id, "workflowPhoto": selected[photo_id]})
    return found


def _build_empty(args, cfg, out_root, staging, pristine_root, parameters, *, apply, started):
    parameters = {key: parameters[key] for key in ("name", "mode", "outRoot")}
    parameters["sourceFolder"] = args.source_folder
    parameters["sourceVarious"] = args.source_various
    if args.source_various:
        folder, images, skipped = source_various_plan(args.source_various, out_root, cfg)
    elif args.source_folder:
        folder, images, skipped = source_folder_plan(args.source_folder, out_root, cfg)
    else:
        folder, images, skipped = None, [], []
    planned = []
    for path, destination in images:
        stat = path.stat()
        planned.append({"name": path.name, "source": str(path), "destination": destination,
                        "sha256": _sha256(path), "bytes": stat.st_size, "mtimeNs": stat.st_mtime_ns})
    duplicates = sum(count - 1 for count in collections.Counter(row["sha256"] for row in planned).values())
    selected_arrivals = workflow_selected_arrivals([path for path, _ in images], cfg)
    by_folder = collections.Counter(row["destination"].rsplit("/", 1)[0] for row in planned)
    print(f"empty universe Sandbox preview: {out_root}")
    print("  layout: Various/gallery, reports root with universe manifest; no catalogue, cache, preparation or history")
    if folder is not None:
        print(f"  source folder (read-only): {folder}")
        print(f"  images to copy: {len(planned)} "
              f"({sum(row['bytes'] for row in planned) / 1048576:.1f} MiB; byte-identical extra copies: {duplicates})")
        for name, count in sorted(by_folder.items(), key=lambda item: (item[0] != "Various/gallery", item[0])):
            print(f"    {name}: {count}")
        print(f"  skipped entries: {len(skipped)}")
        for row in skipped[:20]:
            print(f"    {row['name']}: {row['reason']}")
        for row in selected_arrivals:
            print(f"  WARNING workflow-selected photo {row['photoId']} ({row['workflowPhoto']}) arrives as "
                  f"{row['name']}; a SIMPLE rebase refuses to rename it (protected or workflow-selected photo "
                  f"cannot move), so hold it out of Various/gallery before the rebase or keep it in Production only")
    print(f"  preview {time.perf_counter() - started:.1f}s")
    if not apply:
        return 0
    reports_relative = cw.storage_root(cfg, "reports", root=out_root).relative_to(out_root)
    universe_relative = reports_relative.joinpath(*UNIVERSE_REPORTS)
    files = []
    staging.mkdir(parents=True)
    try:
        (staging / "Various" / "gallery").mkdir(parents=True)
        (staging / universe_relative).mkdir(parents=True)
        if planned:
            print(f"copying {len(planned)} originals (SHA-256 verified) ...", flush=True)
        for row in planned:
            relative = pathlib.PurePosixPath(row["destination"])
            for target_root, kind, prefix in ((staging, "working-photo", "Working"),
                                              (pristine_root, "universe-source", PRISTINE)):
                digest, size = _copy_verified(row["source"], target_root.joinpath(*relative.parts), row["sha256"])
                if (target_root.joinpath(*relative.parts)).stat().st_mtime_ns != row["mtimeNs"]:
                    raise UniverseError(f"copy did not preserve the modified time: {relative}")
                files.append({"kind": kind, "path": f"{prefix}/{relative}", "sha256": digest, "bytes": size,
                              "source": row["source"], "mtimeNs": row["mtimeNs"]})
        policy_path = pathlib.Path(args.policy) if args.policy else ROOT / "data" / "art" / "likeness-engine-policy.json"
        named_folders = sum(1 for key in by_folder if key != "Various/gallery")
        (staging / "README-universe.md").write_text(
            empty_readme(out_root, policy_path, args.name, named_folders), encoding="utf-8")
        manifest = {
            "kind": MANIFEST_KIND, "schemaVersion": SCHEMA_VERSION, "name": args.name, "mode": "empty",
            "createdAt": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "parameters": parameters,
            "implementationSHA256": metadata.content_sha256(pathlib.Path(__file__)),
            "sourceFolder": None if folder is None else str(folder),
            "sourceLayout": "various" if args.source_various else "flat",
            "foldersCopied": dict(sorted(by_folder.items())),
            "skipped": skipped,
            "workflowSelectedArrivals": selected_arrivals,
            "counts": {"photos": len(planned), "byteIdenticalExtraCopies": duplicates, "skipped": len(skipped)},
            "files": files,
            "elapsedSeconds": round(time.perf_counter() - started, 1),
        }
        (staging / universe_relative / "universe-manifest.json").write_text(
            json.dumps(manifest, indent=1), encoding="utf-8")
        staging.rename(out_root)
    except BaseException:
        print(f"empty universe build stopped; partial staging preserved for inspection: {staging}"
              f"{' and ' + str(pristine_root) if pristine_root.exists() else ''}", file=sys.stderr)
        raise
    manifest_path = out_root / universe_relative / "universe-manifest.json"
    print(f"empty universe applied: {out_root} ({len(planned)} photo(s) in {len(by_folder)} Various folder(s))")
    print(f"manifest: {manifest_path} (sha256 {_sha256(manifest_path)})")
    print(f"next steps: {out_root / 'README-universe.md'}")
    print(f"elapsed {time.perf_counter() - started:.1f}s")
    return 0


def _counts(selection, staging_folders):
    photos = selection["photos"]
    reasons = collections.Counter(photo["reasons"][0].split(":", 1)[0] for photo in photos)
    return {
        "identities": len(selection["identities"]),
        "identitiesByHop": dict(sorted(collections.Counter(row["hop"] for row in selection["identities"]).items())),
        "photos": len(photos),
        "photosByHop": dict(sorted(collections.Counter(photo["hop"] for photo in photos).items())),
        "photosByPrimaryReason": dict(sorted(reasons.items())),
        "photosWithUsableVector": sum(photo["usableVector"] for photo in photos),
        "interestingNotIncluded": len(selection["interestingNotIncluded"]),
        "boundedOut": len(selection["boundedOut"]),
        "excluded": len(selection["excluded"]),
        "notFound": len(selection["notFound"]),
        "namedStagingFolders": len(staging_folders),
    }


def _print_preview(selection, counts, missing, seconds):
    print(f"universe selection ({selection['band']} >= {selection['bandMinimum']}, hops={selection['hops']}, "
          f"hop2 {selection['hop2Band']} >= {selection['hop2Minimum']}; centering: {selection['centering']})")
    for request, keys in {**selection["seeds"], **selection["includes"]}.items():
        print(f"  resolved {request} -> {', '.join(keys)}")
    for name in selection["notFound"]:
        print(f"  NOT FOUND: {name}")
    for row in selection["identities"]:
        print(f"  identity hop{row['hop']} {row['identity']}: {row['reason']} best={row['bestScore']} via={row['via']}")
    for row in selection["interestingNotIncluded"][:40]:
        print(f"  interesting (not included) {row['identity']}: {row['bestScore']} [{row['scoreBasis']}] photos={row['photos']}")
    if len(selection["interestingNotIncluded"]) > 40:
        print(f"  ... {len(selection['interestingNotIncluded']) - 40} more interesting identities in the report")
    for row in selection["boundedOut"]:
        print(f"  bounded out: {row}")
    for key, value in counts.items():
        print(f"  {key}: {value}")
    print(f"  missing verified bytes: {len(missing)}")
    for source in missing[:20]:
        print(f"    {source}")
    print(f"  preview {seconds:.1f}s")


def check(args, cfg):
    out_root = validate_out_root(args.out_root, cfg)
    if not out_root.is_dir():
        raise UniverseError(f"no universe Working at {out_root}")
    reports = cw.storage_root(cfg, "reports", root=out_root)
    manifest_path = reports.joinpath(*UNIVERSE_REPORTS) / "universe-manifest.json"
    if not manifest_path.is_file():
        raise UniverseError(f"no universe manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("kind") != MANIFEST_KIND or manifest.get("schemaVersion") != SCHEMA_VERSION:
        raise UniverseError("not a universe manifest")
    receipts = sorted((reports / "runs").glob("normal-rebase-*.json"))
    applied = sorted(
        path.name for path in receipts
        if not path.name.endswith("-preview.json")
        and json.loads(path.read_text(encoding="utf-8")).get("status") == "applied"
    )
    results = collections.Counter()
    failures = []
    base = out_root.parent
    for entry in manifest["files"]:
        path = base.joinpath(*pathlib.PurePosixPath(entry["path"]).parts)
        ok = path.is_file() and path.stat().st_size == entry["bytes"] and _sha256(path) == entry["sha256"]
        if ok:
            results[f"{entry['kind']}:verified"] += 1
        elif entry["kind"] == "working-photo" and applied:
            # An applied rebase moves and renames Working photos; Universe-Source keeps the originals.
            results[f"{entry['kind']}:moved-by-applied-rebase"] += 1
        elif entry["kind"] == "working-likeness" and receipts:
            # Any rebase preview or apply may extend the Working cache.
            results[f"{entry['kind']}:updated-by-rebase"] += 1
        else:
            results[f"{entry['kind']}:FAILED"] += 1
            failures.append(entry["path"])
    evidence = collections.Counter()
    for label, row in (manifest.get("evidence") or {}).items():
        path = pathlib.Path(row["path"])
        if row.get("sha256") is None:
            evidence["folder-not-hashed"] += 1
        elif path.is_file() and _sha256(path) == row["sha256"]:
            evidence["unchanged"] += 1
        else:
            evidence["changed-since-creation"] += 1
            print(f"  note: read-only evidence changed since creation (not a failure): {label} {path}")
    print(f"universe check: {manifest['name']} ({manifest['mode']}); manifest sha256 {_sha256(manifest_path)}")
    print(f"  Various/gallery present: {(out_root / 'Various' / 'gallery').is_dir()}")
    print(f"  rebase receipts: {len(receipts)}; applied: {', '.join(applied) or 'none'}")
    for key, value in sorted(results.items()):
        print(f"  {key}: {value}")
    for key, value in sorted(evidence.items()):
        print(f"  evidence {key}: {value}")
    for path in failures[:20]:
        print(f"  FAILED {path}")
    if not manifest["files"] and not (out_root / "Various" / "gallery").is_dir():
        failures.append("Working/Various/gallery")
    return 1 if failures else 0


def _parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", action="append", default=[], help="seed identity CATEGORY/Name; repeatable")
    parser.add_argument("--include", action="append", default=[], help="extra identity CATEGORY/Name; repeatable")
    parser.add_argument("--name", required=True, help="universe ID, e.g. angelica-20261122")
    parser.add_argument("--out-root", help="new ...\\Sovereign Territories Sandbox\\Working outside the main Sandbox")
    parser.add_argument("--expand-band", choices=BANDS, default="yellow", help="hop-1 band (default yellow)")
    parser.add_argument("--hop2-band", choices=BANDS, default="green", help="hop-2 band (default green)")
    parser.add_argument("--hops", type=int, choices=(0, 1, 2), default=1)
    parser.add_argument("--mode", choices=("blank", "named", "empty"), default="blank")
    parser.add_argument("--max-photos", type=int, default=1500, help="upper bound on selected photos")
    parser.add_argument("--policy", help="likeness policy JSON (score bands, minFace)")
    parser.add_argument("--pre-receipt", help="pre-rebase applied receipt with plan.sourceRows")
    parser.add_argument("--current-receipt", help="latest applied main-Sandbox rebase receipt")
    parser.add_argument("--current-review", help="latest people_gallery_review.html")
    parser.add_argument("--source-cache", help="face-vector cache to read and copy")
    parser.add_argument("--face-evidence", help="face-evidence folder to copy")
    parser.add_argument("--preparation", help="sealed selected-preparation folder to reuse")
    parser.add_argument("--preparation-sha256", default=PREPARATION_SHA256)
    parser.add_argument("--originals", action="append", help="extra original-bytes roots (Source or backup); repeatable")
    parser.add_argument("--source-folder", help="--mode empty: read-only folder whose top-level images are copied "
                                                "into Various/gallery")
    parser.add_argument("--source-various", help="--mode empty: read-only hand-sorted Various tree; gallery -> "
                                                 "Various/gallery, every other <Name> -> Various/<Name>/gallery")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="preview only (the default)")
    mode.add_argument("--apply", action="store_true", help="build the universe Sandbox")
    mode.add_argument("--check", action="store_true", help="rehash every recorded copy")
    return parser


def main(argv=None):
    parser = _parser()
    args = parser.parse_args(argv)
    if not NAME.fullmatch(args.name):
        parser.error("--name must be letters, digits, dot, underscore or hyphen")
    if args.mode != "empty" and not args.seed and not args.check:
        parser.error("--seed is required unless --mode empty")
    if args.mode == "empty" and (args.seed or args.include):
        parser.error("--mode empty takes no --seed/--include")
    if args.source_folder and args.mode != "empty":
        parser.error("--source-folder requires --mode empty")
    if args.source_various and args.mode != "empty":
        parser.error("--source-various requires --mode empty")
    if args.source_folder and args.source_various:
        parser.error("use either --source-folder or --source-various")
    if args.max_photos < 1:
        parser.error("--max-photos must be positive")
    if not re.fullmatch(r"[0-9a-f]{64}", args.preparation_sha256.lower()):
        parser.error("--preparation-sha256 must be 64 hex digits")
    args.preparation_sha256 = args.preparation_sha256.lower()
    try:
        cfg = cw.load_cfg()
        paths = default_paths(cfg)
        if not args.out_root:
            args.out_root = str(paths["universes"] / args.name / "Sovereign Territories Sandbox" / "Working")
        if args.check:
            return check(args, cfg)
        policy = load_policy(args.policy)
        return build(args, cfg, policy, paths, apply=args.apply)
    except (OSError, ValueError, KeyError) as exc:
        print(f"universe sandbox stopped safely: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
