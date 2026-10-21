#!/usr/bin/env python3
"""A picture gallery of everyone in the photo library, with up to nine photos per person.

  python tools/art/people_gallery.py                 write <work>\\_reports\\library\\people_gallery.html and .md; full Angel candidate rankings go under comparisons\\pairings
  python tools/art/people_gallery.py --artists       also the people grouped inside the artists' folders
  python tools/art/people_gallery.py --out DIR       write somewhere else

Which photo stands for a person:
  Angels and Sisters  the photo you chose for her in workspaces.json (marked "chosen"); when there is none, the best guess below.
  Everyone else       the photo with the most promise as a Prime start. Its score is a photo-suitability heuristic, not an identity match:
                        0.35 how typical it is of her (the face against the centre of her other photos; a lone photo gets 0.5)
                        0.20 how large the face is (the face's size, up to 300 px)
                        0.25 a likely full-length framing (face height is at most 14% of the clean photo; a heuristic)
                        0.15 how sharp it is, against her sharpest photo
                        0.05 a clean headshot can be cut from it (the face is big enough and clear of a phone's app bars)
                        minus 0.15 for a second face, minus 0.10 for a landscape picture
The featured photo is shown first. Every thumbnail opens its original; the photo count opens that person's gallery folder.
"""
import argparse
import base64
import datetime
import html
import io
import json
import os
import pathlib
import re
import statistics
import sys
import types
from urllib.parse import urlencode

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflows"))
sys.path.insert(0, str(ROOT / "tools/art"))
import comfy_workflows as cw  # noqa: E402
import likeness  # noqa: E402
import originals  # noqa: E402
import people  # noqa: E402
from likeness_library.audit import audit_person, catalog_photo_flags, identity_order_key  # noqa: E402
from likeness_library.cross_reference import CATEGORY_ORDER, rank_identity_centroids, score_band  # noqa: E402
from likeness_library.metadata import content_sha256, load_catalog, photo_id_from_name  # noqa: E402
from likeness_library.thumbnails import crop_thumbnail  # noqa: E402

THUMB = (176, 220)  # match the review gallery's 4:5 portrait framing
MAX_PHOTOS = 9
SECTIONS = [
    (category, "Artists' people" if category == "Artists" else category)
    for category in CATEGORY_ORDER
]
WEIGHTS = {"typical": 0.35, "size": 0.20, "full": 0.25, "sharp": 0.15, "head": 0.05}
FULL_LENGTH_FACE_MAX = 0.14


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


def top_gallery_photos(photos, scores, *, identity_scores=None, priorities=None, sort_mode="identity"):
    """Rank overview photos using the selected identity sort."""
    identity_scores = identity_scores or {}
    priorities = priorities or {}
    if sort_mode == "score":
        return sorted(
            photos,
            key=lambda photo: (
                identity_scores.get(photo.name) is None,
                -(identity_scores.get(photo.name) or 0.0),
                photo.name.casefold(),
            ),
        )[:MAX_PHOTOS]
    if sort_mode != "identity":
        raise ValueError(f"unknown identity photo sort: {sort_mode}")
    ordered = sorted(
        photos,
        key=lambda photo: (
            *priorities.get(photo.name, identity_order_key(False, False, None, photo.name)),
        ),
    )
    return ordered[:MAX_PHOTOS]


def thumb_bytes(path, box=None, framing="chest", kind="JPEG"):
    from PIL import Image
    with Image.open(path) as im:
        im = crop_thumbnail(im, box, framing, THUMB)
    buf = io.BytesIO()
    im.save(buf, kind, quality=82)
    return buf.getvalue()


def inspect(path, box):
    """(is the framing likely full-length, is it landscape), using face size as a heuristic."""
    from PIL import Image, ImageOps
    import screens
    try:
        with Image.open(path) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
    except Exception:  # noqa: BLE001
        return False, False
    if not box:
        return False, im.width > im.height
    reel = screens.is_reel_ui(im)
    if reel and not screens.head_clear(box):
        return False, im.width > im.height
    if reel:
        x0, y0, x1, y1 = screens.clean_box(im.size)
        width, height = im.size
        box = ((box[0] * width - x0) / (x1 - x0), (box[1] * height - y0) / (y1 - y0),
               box[2] * width / (x1 - x0), box[3] * height / (y1 - y0))
    return box[3] <= FULL_LENGTH_FACE_MAX, im.width > im.height


def sister_matches(space, key, limit=3):
    """Rank the closest usable sister-folder centroids to this person's face centroid."""
    get_centroid = getattr(space, "centroid", None)
    if not callable(get_centroid):
        return []
    centroid = get_centroid(key)
    if centroid is None:
        return []
    ranked = []
    for sister in getattr(space, "keys", []):
        if not likeness.is_sister(sister):
            continue
        other = get_centroid(sister)
        if other is not None:
            ranked.append({"key": sister, "name": sister.split("/")[-1], "score": float(centroid @ other)})
    return sorted(ranked, key=lambda match: (-match["score"], match["name"].casefold()))[:limit]


def configured_pairs(st):
    pairs = dict(likeness.PAIRS)
    pairs.update((st or {}).get("pairs", {}))
    return pairs


def hero_hair_color(key):
    group, name = key.split("/", 1)
    if group != "Angels":
        return ""
    path = ROOT / "data" / "art" / "heroes" / "angel-primes" / "female" / f"{slug(name)}.json"
    if not path.is_file():
        return ""
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("art", {}).get("palette", {}).get("hairColor", "")


def angel_candidates(space, cfg, st, sister, limit=3, rend=None):
    """Eligible Prospect folders ranked by fit to the current sister pairing target."""
    sister_key = next((key for key in getattr(space, "keys", [])
                       if likeness.is_sister(key) and key.split("/")[-1].casefold() == sister.casefold()), None)
    if sister_key is None:
        return []
    sister_identity = likeness.identity(space, cfg, st, rend, sister_key)
    sister_core = likeness.identity_vec(likeness.folder_core(space, sister_key, sister_identity)[3], sister_identity)
    minimum = st.get("pairMinPhotos", 5)
    minimum_cohesion = st.get("pairMinCohesion", 0.45)
    low, high = st.get("pairLow", 0.15), st.get("pairHigh", 0.40)
    target = st.get("pairTarget", 0.28)
    ranked = []
    for key in getattr(space, "keys", []):
        if not key.startswith("Prospects/") or likeness.candidate_photo_count(space, key, st) < minimum:
            continue
        ident = likeness.identity(space, cfg, st, rend, key)
        photos, scores, _core, core = likeness.folder_core(space, key, ident)
        cohesion = float(sum(scores) / len(scores)) if len(photos) > 1 else 0.0
        if cohesion < minimum_cohesion:
            continue
        vector = likeness.identity_vec(core, ident)
        score = float(vector @ sister_core)
        usable_count = likeness.candidate_photo_count(space, key, st)
        score_parts = likeness.pairing_candidate_score(score, usable_count, target, low, high)
        ranked.append({"key": key, "name": key.split("/", 1)[1], "score": score,
                       "photos": usable_count, "cohesion": cohesion, **score_parts})
    ordered = sorted(ranked, key=lambda candidate: (candidate["cost"], -candidate["photos"], candidate["name"].casefold()))
    return ordered if limit is None else ordered[:limit]


def person_anchor(status, name):
    return f"person-{slug(status)}-{slug(name)}"


def person_name(folder, status):
    """Return the recorded person name for Angel and Sister cards."""
    if status not in ("Angels", "Sisters"):
        return None
    return people.name_of(folder)


def add_pairing_navigation(rows):
    """Link each Sister to her paired Angel and share ranked Prospect fits across the gallery."""
    sisters = {row["folder"].casefold(): row for row in rows if row["status"] == "Sisters"}
    angels = [row for row in rows if row["status"] == "Angels"]
    prospects = {row["folder"].casefold(): row for row in rows if row["status"] == "Prospects"}
    fits_by_prospect = {name: [] for name in prospects}

    for sister in sisters.values():
        sister["paired_angel"] = None
        sister["candidate_prospects"] = []
    for prospect in prospects.values():
        prospect["best_angel_match"] = None

    for angel in angels:
        sister = sisters.get(angel.get("paired_sister", "").casefold())
        angel["best_candidate_cost"] = angel["candidate_rankings"][0]["cost"] if angel.get("candidate_rankings") else None
        if sister is not None:
            sister["paired_angel"] = angel
            sister["candidate_prospects"] = angel.get("candidate_prospects", [])
        for rank, candidate in enumerate(angel.get("candidate_rankings", []), 1):
            prospect = prospects.get(candidate["name"].casefold())
            if prospect is not None:
                fits_by_prospect[candidate["name"].casefold()].append(
                    {"angel": angel, "candidate": candidate, "rank": rank}
                )

    for name, matches in fits_by_prospect.items():
        if matches:
            prospects[name]["best_angel_match"] = min(
                matches,
                key=lambda match: (match["candidate"]["cost"], match["rank"], match["angel"]["folder"].casefold()),
            )

    order = {section: index for index, (section, _title) in enumerate(SECTIONS)}

    def sort_key(row):
        section = row["status"]
        if section == "Angels":
            return order[section], row["folder"].casefold()
        if section == "Sisters":
            return order[section], row["folder"].casefold()
        if section == "Prospects":
            return order[section], -row["photos"], row["folder"].casefold()
        return order.get(section, 9), -row["photos"], row["folder"].casefold()

    rows.sort(key=sort_key)


def collect(cfg, st, work, space, groups, rend=None, catalog=None):
    """Build one row per person, with at most nine original-photo thumbnails."""
    st = st or likeness.SETTINGS
    catalog = catalog if catalog is not None else load_catalog()
    size = tuple(cfg.get("standardSize") or (944, 1104))
    chosen = likeness.chosen_keys(cfg)
    people_rows = []
    folders = [
        (key, folder) for key, folder in likeness.library_people(cfg, st, work)
        if likeness.status_of(key) in groups
    ]
    source_records = []
    for _key, folder in folders:
        for bucket in ("gallery", "review"):
            for path in originals.images(folder / bucket):
                photo_id = photo_id_from_name(path.name)
                source_records.append((
                    photo_id,
                    content_sha256(path) if photo_id in catalog["photos"] else None,
                ))
    protected_ids, stale_ids, ambiguous_ids = catalog_photo_flags(source_records, catalog)
    catalog_by_folder = {}
    for person_id, record in catalog["people"].items():
        catalog_by_folder.setdefault(record["folder"], []).append((person_id, record))

    for key, folder in folders:
        status = likeness.status_of(key)
        ps = space.by_key.get(key, [])
        all_originals = originals.images(folder / "gallery")
        usable = [photo for photo in ps if photo.usable(st.get("minFace", 60))]
        ids = [photo_id_from_name(photo.name) for photo in usable]
        person_records = catalog_by_folder.get(key, [])
        conflict = len(person_records) > 1
        person = person_records[0][1] if len(person_records) == 1 else None
        anchors = set(person["identityAnchors"]) if person and not conflict else set()
        audit = audit_person(
            [photo.vec for photo in usable],
            ids,
            anchor_ids=anchors,
            protected_ids=protected_ids,
            stale_ids=stale_ids,
            ambiguous_ids=ambiguous_ids,
        )
        identity_by_name = {}
        for index, photo in enumerate(usable):
            photo_id = ids[index]
            is_anchor = (
                photo_id in anchors and photo_id not in stale_ids and photo_id not in ambiguous_ids
            )
            score = audit["scores"][index]
            is_core = audit["sufficient"] and index in audit["core_indices"]
            identity_by_name[photo.name] = {
                "score": score,
                "anchor": is_anchor,
                "priority": identity_order_key(is_anchor, is_core, score, photo.name),
            }
        row = {"status": status, "folder": key.split("/", 1)[1], "key": key, "photos": len(all_originals), "review": len(originals.images(folder / "review")),
               "chosen": False, "score": None, "source": "", "tags": people.profile(folder),
               "gallery_path": folder / "gallery", "source_path": None, "z_path": people.find(folder),
               "person_name": person_name(folder, status)}
        min_face = st.get("minFace", likeness.SETTINGS["minFace"])
        photos = [p for p in getattr(space, "photos", []) if p.key == key]
        row["usable"] = sum(p.usable(min_face) for p in photos)
        row["no_face"] = sum(p.faces == 0 for p in photos)
        row["too_small"] = sum(p.faces > 0 and p.raw is not None and p.px < min_face for p in photos)
        row["unreadable"] = sum(p.raw is None and p.faces != 0 for p in photos)
        row["full_length"] = 0
        row["median_face_px"] = int(statistics.median(p.px for p in photos if p.usable(min_face))) if row["usable"] else 0
        row["sister_matches"] = sister_matches(space, key) if status in ("Prospects", "Potentials") else []
        row["paired_sister"] = ""
        row["paired_angel"] = None
        row["hair_color"] = ""
        row["candidate_prospects"] = []
        row["candidate_rankings"] = []
        row["best_angel_match"] = None
        row["best_candidate_cost"] = None
        if status == "Angels":
            row["paired_sister"] = next((sister for angel, sister in configured_pairs(st).items()
                                         if angel.casefold() == row["folder"].casefold()), "")
            row["hair_color"] = hero_hair_color(key)
            if row["paired_sister"]:
                row["candidate_rankings"] = angel_candidates(space, cfg, st, row["paired_sister"], limit=None, rend=rend)
                row["candidate_prospects"] = row["candidate_rankings"][:3]
        pick = None
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
            full_length = 0
            for s in scored:
                p, head, body, sharp = s
                typical = float(p.vec @ c) if c is not None and p.vec is not None else 0.5
                full, landscape = inspect(p.path, p.box)
                full_length += full
                s.append(prime_score(max(typical, 0.0), p.px, full, sharp / top, head is not None, p.faces, landscape))
            row["full_length"] = full_length
            for s in scored:
                if likeness.cw.photo_key(s[0].name) in chosen:
                    pick = s
                    row["chosen"] = True
            best = max(scored, key=lambda s: s[4])
            pick = pick or best
            row["score"] = pick[4]
            row["source"] = pick[0].name
        elif all_originals:
            row["source"] = all_originals[0].name
            row["source_path"] = all_originals[0]
        if pick:
            row["source_path"] = pick[0].path
            row["source_identity_score"] = (
                identity_by_name.get(row["source"], {}).get("score")
            )
        scores_by_name = {entry[0].name: entry[4] for entry in scored} if ps else {}
        boxes_by_name = {entry[0].name: entry[0].box for entry in scored} if ps else {}
        identity_scores = {
            name: values["score"] for name, values in identity_by_name.items()
        }
        identity_priorities = {
            name: values["priority"] for name, values in identity_by_name.items()
        }
        ordered = top_gallery_photos(
            all_originals,
            scores_by_name,
            identity_scores=identity_scores,
            priorities=identity_priorities,
        )
        score_ordered = top_gallery_photos(
            all_originals,
            scores_by_name,
            identity_scores=identity_scores,
            priorities=identity_priorities,
            sort_mode="score",
        )
        ordered_union = list(dict.fromkeys(ordered + score_ordered))
        sha_by_name = {entry[0].name: getattr(entry[0], "sha", "") for entry in scored} if ps else {}
        gallery_photos = []
        for photo in ordered_union:
            face_box = boxes_by_name.get(photo.name)
            sha = sha_by_name.get(photo.name, "")
            stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", photo.stem).strip("._") or "photo"
            asset_base = f"people_gallery_review_files/{stem}"
            gallery_photos.append({
                "name": photo.name,
                "path": photo,
                "score": scores_by_name.get(photo.name),
                "identity_score": identity_scores.get(photo.name),
                "identity_priority": identity_priorities.get(
                    photo.name, identity_order_key(False, False, None, photo.name)
                )[0],
                "identity_anchor": identity_by_name.get(photo.name, {}).get("anchor", False),
                "thumbnail": f"{asset_base}_chest_{sha[:12]}.jpg" if sha else None,
                "thumbnail_head": f"{asset_base}_head_{sha[:12]}.jpg" if sha else None,
                "thumb": thumb_bytes(photo, face_box),
                "thumb_head": thumb_bytes(
                    photo,
                    face_box,
                    framing="head",
                ),
            })
        row["gallery_photos"] = gallery_photos
        row["gallery_photos_identity"] = ordered
        row["gallery_photos_score"] = score_ordered
        people_rows.append(row)
    add_pairing_navigation(people_rows)
    rankings = rank_identity_centroids(
        space,
        [row["key"] for row in people_rows],
        categories={row["key"]: row["status"] for row in people_rows},
    )
    for row in people_rows:
        row["identity_rankings"] = rankings[row["key"]]
        closest_by_category = {}
        for match in row["identity_rankings"]:
            closest_by_category.setdefault(match["category"], match)
        row["identity_matches_by_category"] = list(closest_by_category.values())
    return people_rows


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def caption(r):
    bits = []
    if r["review"]:
        bits.append(f"{r['review']} in review")
    if r["chosen"]:
        bits.append("chosen source photo")
    else:
        bits.append(
            f"Prime-start photo score {r['score']:.2f}"
            if r["score"] is not None else "no usable face" if r["photos"] else "no gallery photos"
        )
    return bits


def profile_summary(tags):
    """Return a compact profile summary of at most six words."""
    values = []
    seen = set()
    for key in ("type", "roles", "elements", "tier", "tags"):
        for value in (tags or {}).get(key, []):
            value = value.strip()
            if value and value.casefold() not in seen:
                seen.add(value.casefold())
                values.append(value)
    words = []
    for value in values:
        for word in value.split():
            if len(words) == 6:
                words[-1] = "..."
                return " ".join(words)
            words.append(word)
    return " ".join(words)


def b64(data):
    return "data:image/jpeg;base64," + base64.b64encode(data).decode("ascii")


CSS = """body{font-family:Segoe UI,Arial,sans-serif;margin:24px;background:#faf8f3;color:#222}h1{margin:0 0 4px}h2{margin:32px 0 8px;border-bottom:2px solid #d8cfbf;padding-bottom:4px}
.page-header{display:flex;justify-content:space-between;align-items:flex-start;gap:24px;padding:16px 18px;background:#fff;border:1px solid #e0d8c8;border-radius:10px;margin-bottom:12px}.page-header p{margin:5px 0 0}.header-side{text-align:right}.header-label{font-size:.75em;color:#666;text-transform:uppercase;letter-spacing:.06em}.score-legend{display:flex;justify-content:flex-end;gap:6px;flex-wrap:wrap;margin-top:5px}.page-note{font-size:.84em;color:#666}
nav a{margin-right:16px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.card{background:#fff;border:1px solid #e0d8c8;border-radius:6px;padding:8px;margin:0}.photos{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:3px}.photos a:nth-child(n+10){display:none}
.photos img{display:block;width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:3px;background:#eee}
.photos a.workflow-photo{outline:4px solid #8b6d32;outline-offset:-4px;border-radius:3px;background:transparent;color:inherit}.photos a.workflow-photo.score-green{outline-color:#2e7d32}.photos a.workflow-photo.score-yellow{outline-color:#b38b00}.photos a.workflow-photo.score-orange{outline-color:#c46b16}.photos a.workflow-photo.score-red{outline-color:#a52d2d}
.card b{font-size:1.05em}.meta{color:#666;font-size:.85em;margin-top:4px}.chosen{background:#2e7d32;color:#fff;border-radius:3px;padding:0 5px;font-size:.8em}.category-badge,.score-badge{display:inline-block;border-radius:4px;padding:2px 6px;font-size:.78em;font-weight:600}.category-sisters{background:#e8e0f2;color:#493365}.category-angels{background:#e4efff;color:#244f85}.category-models{background:#e4f2e5;color:#285b31}.category-prospects{background:#fff0d9;color:#704a12}.category-potentials{background:#eee;color:#555}.score-green{background:#d9efdc;color:#205b2a}.score-yellow{background:#fff1bd;color:#6b5200}.score-orange{background:#ffe0c2;color:#7a3f00}.score-red{background:#f5d6d6;color:#7b2222}.status{color:#888;font-size:.8em}.identity{font-size:.82em;color:#34495e;margin-top:4px}
.summary{color:#555;font-size:.9em;margin-top:3px}.readiness{color:#555;font-size:.82em;margin-top:5px}.matches,.pairing{font-size:.82em;margin-top:5px}.relationship-row{margin:3px 0}.gallery-jump{margin-left:5px;text-decoration:none;font-weight:700}.pairing-subsection{margin-top:9px;padding-top:7px;border-top:1px solid #e7e0d4}.fit-detail{margin-left:4px}.noimg{display:flex;align-items:center;justify-content:center;aspect-ratio:4/5;background:#eee;color:#999;font-size:.8em}.gallery-controls{display:flex;justify-content:flex-end;gap:12px;flex-wrap:wrap;margin:12px 0}.history,.photo-count{font-size:.78em;margin-left:4px;background:#eee;color:#555;border-radius:4px;padding:2px 6px}.person-title{display:flex;align-items:center;gap:5px}.identity-tags{display:flex;align-items:center;gap:5px;flex-wrap:wrap;margin-top:5px}.source-photo{margin-left:5px}.full-details{font-size:.82em;margin-top:5px}.full-details ol{margin:4px 0;padding-left:24px}body[data-detail-level="summary"] .full-details{display:none}@media(max-width:700px){body{margin:12px}.page-header{display:block}.header-side{text-align:left;margin-top:12px}.score-legend{justify-content:flex-start}}"""


def score_badge(score, title="Likeness score"):
    return (
        f'<span class="score-badge score-{score_band(score)}" '
        f'title="{html.escape(title, quote=True)}">{score:.2f}</span>'
    )


def fit_badge(cost, title="Adjusted fit cost; lower is better"):
    band = "green" if cost <= 0.05 else "yellow" if cost <= 0.10 else "orange" if cost <= 0.20 else "red"
    return (
        f'<span class="score-badge score-{band}" '
        f'title="{html.escape(title, quote=True)}">{cost:.3f}</span>'
    )


def identity_match_score(row, category, name):
    return next((
        match["score"] for match in row.get("identity_rankings", [])
        if match.get("category") == category and match.get("name", "").casefold() == name.casefold()
    ), None)


def relationship_link(category, name, review_href, score=None):
    key = f"{category}/{name}"
    review_url = f'{review_href}?{urlencode({"person": key, "bucket": "Gallery", "sort": "identity"})}'
    if score is None:
        icon, icon_class, icon_title = "↗", "", "Jump to this person in the overview"
    else:
        icon = "▲" if score >= 0.55 else "▶" if score >= 0.30 else "▼"
        icon_class = f" score-{score_band(score)}"
        icon_title = f"Jump to this person · likeness {score:.2f}"
    return (
        f'<a href="{html.escape(review_url, quote=True)}" target="_blank" rel="noopener noreferrer">'
        f'{html.escape(category)}: {html.escape(name)}</a> '
        f'<a class="gallery-jump{icon_class}" href="#{person_anchor(category, name)}" '
        f'aria-label="Stay in People gallery at {html.escape(name, quote=True)}" '
        f'title="{html.escape(icon_title, quote=True)}">{icon}</a>'
    )


def render_html(rows, stamp, counts, pairing_report_href="../comparisons/pairings/angel-prospect-candidates.md",
                review_href="people_gallery_review.html", thumbnail_dir=None,
                identity_report_href="identity-rankings.md"):
    photo_count = sum(row.get("photos", 0) for row in rows)
    people_label = "person" if len(rows) == 1 else "people"
    photos_label = "photo" if photo_count == 1 else "photos"
    out = ["<!doctype html>", '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>People gallery</title>', f"<style>{CSS}</style></head><body>",
           '<header class="page-header"><div><h1>People gallery</h1>'
           f'<p class="meta">Generated {html.escape(stamp)} · {len(rows)} {people_label} · {photo_count} {photos_label}</p>'
           f'           <p class="page-note">Names open Review; score markers jump within Gallery · <a href="{html.escape(identity_report_href, quote=True)}">Full library rankings</a> · Up to nine photos per person</p></div>'
           '<div class="header-side"><div class="header-label">Likeness</div>'
           '<div class="score-legend"><span class="score-badge score-green">≥0.55</span><span class="score-badge score-yellow">≥0.30</span><span class="score-badge score-orange">≥0.15</span><span class="score-badge score-red">&lt;0.15</span></div></div></header>',
           '<div class="gallery-controls"><label>Details <select id="detail-level"><option value="summary">Summary</option><option value="full">Full details</option></select></label> '
           '<label>Photo order <select id="gallery-sort"><option value="identity">Core identity first</option><option value="high">Highest identity score</option></select></label> '
           '<label>Thumbnail <select id="thumbnail-framing"><option value="chest">Chest-up</option><option value="head">Head</option></select></label></div>',
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
        for photo in r["gallery_photos"]:
            href = html.escape(pathlib.Path(photo["path"]).resolve().as_uri(), quote=True)
            score_title = (
                f' · Identity score {photo["identity_score"]:.3f}'
                if photo.get("identity_score") is not None else
                f' · Prime-start score {photo["score"]:.3f}' if photo.get("score") is not None else ""
            )
            title = html.escape(photo["name"] + score_title, quote=True)
            chest_path = thumbnail_dir / photo["thumbnail"] if thumbnail_dir and photo.get("thumbnail") else None
            head_path = thumbnail_dir / photo["thumbnail_head"] if thumbnail_dir and photo.get("thumbnail_head") else None
            chest_src = (
                html.escape(pathlib.Path(photo["thumbnail"]).as_posix(), quote=True)
                if chest_path and chest_path.is_file() else b64(photo["thumb"])
            )
            head_src = (
                html.escape(pathlib.Path(photo["thumbnail_head"]).as_posix(), quote=True)
                if head_path and head_path.is_file() else b64(photo.get("thumb_head", photo["thumb"]))
            )
            is_workflow_photo = r["chosen"] and photo["name"] == r["source"]
            workflow_score_class = (
                f' score-{score_band(photo.get("identity_score"))}'
                if is_workflow_photo and photo.get("identity_score") is not None else ""
            )
            workflow_class = (
                f' class="workflow-photo{workflow_score_class}"'
                if is_workflow_photo else ""
            )
            image_title = "Workflow photo" if is_workflow_photo else html.escape(photo["name"], quote=True)
            imgs.append(
                f'<a{workflow_class} href="{href}" target="_blank" rel="noopener noreferrer"'
                f' title="{image_title}">'
                f'<img src="{chest_src}" data-head="{head_src}" '
                f'data-identity-priority="{photo.get("identity_priority", 3)}" '
                f'data-identity-score="{photo.get("identity_score") if photo.get("identity_score") is not None else ""}" '
                f'data-prime-score="{photo.get("score") if photo.get("score") is not None else ""}" '
                f'data-photo-name="{html.escape(photo["name"], quote=True)}" '
                f'alt="{title}" title="{title}"></a>'
            )
        if not imgs:
            imgs.append('<div class="noimg">no photos</div>')
        flag = '<span class="chosen">workflow</span>' if r["chosen"] else ""
        name = html.escape(r["folder"])
        key = r.get("key", f'{r["status"]}/{r["folder"]}')
        review_url = f'{review_href}?{urlencode({"person": key, "bucket": "Gallery", "sort": "identity"})}'
        name = f'<a class="person-review-link" href="{html.escape(review_url, quote=True)}" target="_blank" rel="noopener noreferrer" title="Open this person in Review">{name}</a>'
        history_link = ""
        if r.get("z_path"):
            href = html.escape(pathlib.Path(r["z_path"]).resolve().as_uri(), quote=True)
            history_link = f' <a class="history" href="{href}" target="_blank" rel="noopener noreferrer">history</a>'
        count = f'<span class="category-badge photo-count">{r["photos"]} photo{"s" if r["photos"] != 1 else ""}</span>'
        summary = profile_summary(r["tags"])
        summary_html = f'<div class="summary">{html.escape(summary)}</div>' if summary else ""
        category_matches = r.get("identity_matches_by_category", [])
        if category_matches:
            match_parts = "".join(
                f'<div class="relationship-row">{relationship_link(m["category"], m["name"], review_href, m["score"])}'
                f'{score_badge(m["score"])}</div>'
                for m in category_matches
            )
            matches_html = '<div class="matches">Closest by category:<br>' + match_parts + "</div>"
        else:
            matches_html = ""
        readiness_html = ""
        pairing_html = ""
        card_id = person_anchor(r["status"], r["folder"])
        full_rankings = r.get("identity_rankings", [])
        if full_rankings:
            ranking_items = "".join(
                f'<li>{relationship_link(m["category"], m["name"], review_href, m["score"])}{score_badge(m["score"])}</li>'
                for m in full_rankings
            )
            matches_html += (
                f'<details class="full-details"><summary>Full library rankings ({len(full_rankings)})</summary>'
                f'<ol>{ranking_items}</ol></details>'
            )
        if r["status"] in ("Prospects", "Potentials"):
            readiness = f"Usable faces: {r.get('usable', 0)}/{r['photos']} · Review: {r['review']}"
            issues = [f"{r.get('no_face', 0)} no face", f"{r.get('too_small', 0)} too small", f"{r.get('unreadable', 0)} unreadable"]
            readiness_html = f'<div class="readiness">{html.escape(readiness)}<span class="full-details"> · Unusable: {html.escape(", ".join(issues))} · Full-length: {r.get("full_length", 0)} · Median face: {r.get("median_face_px", 0)}px</span></div>'
            if r.get("sister_matches"):
                sisters = "".join(
                    f'<div class="relationship-row">{relationship_link("Sisters", m["name"], review_href, m["score"])}'
                    f'{score_badge(m["score"])}</div>'
                    for m in r["sister_matches"]
                )
                matches_html += f'<div class="matches">Closest Sisters:<br>{sisters}</div>'
            best_match = r.get("best_angel_match")
            if best_match:
                angel = best_match["angel"]
                candidate = best_match["candidate"]
                angel_score = candidate.get("score")
                fit_link = relationship_link(
                    "Angels", angel["folder"], review_href, angel_score
                )
                angel_score_badge = (
                    " " + score_badge(angel_score, "Best Angel likeness score")
                    if angel_score is not None else ""
                )
                pairing_html = (
                    f'<div class="pairing">Best Angel: {fit_link}{angel_score_badge} '
                    f'<span class="score-badge">#{best_match["rank"]}</span> '
                    f'Fit {fit_badge(candidate["cost"])}</div>'
                )
        elif r["status"] == "Angels":
            parts = []
            if r.get("paired_sister"):
                sister_score = identity_match_score(r, "Sisters", r["paired_sister"])
                sister_link = relationship_link(
                    "Sisters", r["paired_sister"], review_href, sister_score
                )
                sister_score_badge = (
                    " " + score_badge(sister_score, "Paired Sister likeness score")
                    if sister_score is not None else ""
                )
                parts.append(f"Paired Sister: {sister_link}{sister_score_badge}")
            candidates = r.get("candidate_prospects", [])
            if candidates:
                alts = "".join(
                    f'<div>{index}. {relationship_link("Prospects", c["name"], review_href, c["score"])} '
                    f'{score_badge(c["score"], "Prospect likeness to Sister")} '
                    f'<span class="fit-detail">Fit {fit_badge(c["cost"])} · '
                    f'Like {fit_badge(c["likeness_cost"], "Likeness fit cost; lower is better")} · '
                    f'Variety <span class="score-badge score-green" title="Variety bonus reduces adjusted fit cost">+{c["photo_bonus"]:.2f}</span> · '
                    f'{c["photos"]} photos</span></div>'
                    for index, c in enumerate(candidates, 1)
                )
                parts.append('<div class="pairing-subsection">Top Prospect alternatives:<br>' + alts + "</div>")
            if parts:
                parts.append(f'<a href="{html.escape(pairing_report_href, quote=True)}">Full Angel–Prospect rankings</a>')
                pairing_html = f'<div class="pairing">{"<br>".join(parts)}</div>'
        elif r["status"] == "Sisters":
            paired_angel = r.get("paired_angel")
            if paired_angel:
                angel_score = identity_match_score(r, "Angels", paired_angel["folder"])
                angel_link = relationship_link(
                    "Angels", paired_angel["folder"], review_href, angel_score
                )
                angel_score_badge = (
                    " " + score_badge(angel_score, "Current Angel likeness score")
                    if angel_score is not None else ""
                )
                parts = [f"Current Angel: {angel_link}{angel_score_badge}"]
                candidates = r.get("candidate_prospects", [])
                if candidates:
                    alternatives = "".join(
                        f'<div>{index}. {relationship_link("Prospects", c["name"], review_href, c["score"])} '
                        f'{score_badge(c["score"], "Prospect likeness to Sister")} '
                        f'<span class="fit-detail">Fit {fit_badge(c["cost"])} · '
                        f'Like {fit_badge(c["likeness_cost"], "Likeness fit cost; lower is better")} · '
                        f'Variety <span class="score-badge score-green" title="Variety bonus reduces adjusted fit cost">+{c["photo_bonus"]:.2f}</span> · '
                        f'{c["photos"]} photos</span></div>'
                        for index, c in enumerate(candidates, 1)
                    )
                    parts.append(f'<div class="pairing-subsection">Top Prospect alternatives:<br>{alternatives}</div>')
                parts.append(f'<a href="{html.escape(pairing_report_href, quote=True)}">Full Angel–Prospect rankings</a>')
                pairing_html = f'<div class="pairing">{"<br>".join(parts)}</div>'
        identity_html = (
            f'<div class="identity">Person: {html.escape(r["person_name"])}</div>'
            if r.get("person_name") else ""
        )
        caption_html = " · ".join(html.escape(part) for part in caption(r))
        if r.get("chosen") and r.get("source_path"):
            source_href = html.escape(pathlib.Path(r["source_path"]).resolve().as_uri(), quote=True)
            visible_names = {photo["name"] for photo in r.get("gallery_photos", [])[:9]}
            source_label = "Workflow photo"
            source_link = (
                f'<a href="{source_href}" target="_blank" rel="noopener noreferrer">{source_label}</a>'
            )
            source_score = r.get("source_identity_score")
            source_badge = (
                " " + score_badge(source_score, "Workflow photo likeness score")
                if source_score is not None else ""
            )
            source_visibility = ""
            if r["source"] not in visible_names:
                source_visibility = ' <span class="status">(not shown)</span>'
            caption_html = " · ".join(
                source_link + source_badge + source_visibility
                if part == "chosen source photo" else html.escape(part)
                for part in caption(r)
            )
        category_class = slug(r["status"])
        out.append(f'<figure class="card" id="{card_id}"><div class="photos">{"".join(imgs)}</div><figcaption><div class="person-title"><b>{name}</b></div><div class="identity-tags"><span class="category-badge category-{category_class}">{html.escape(r["status"])}</span>{flag}{history_link}{count}</div>'
                   f'{summary_html}{identity_html}'
                   f'<div class="meta">{caption_html}</div>{readiness_html}{matches_html}{pairing_html}</figcaption></figure>')
    if current:
        out.append("</div>")
    out.append("""<script>
document.getElementById("detail-level").addEventListener("change",event=>{
  document.body.dataset.detailLevel=event.target.value;
});
document.body.dataset.detailLevel="summary";
for(const image of document.querySelectorAll(".photos img[data-head]"))image.dataset.chest=image.src;
function galleryCompare(a,b,mode){
  if(mode==="identity"){
    return Number(a.dataset.identityPriority)-Number(b.dataset.identityPriority) ||
      (Number(b.dataset.identityScore||-Infinity)-Number(a.dataset.identityScore||-Infinity)) ||
      a.dataset.photoName.localeCompare(b.dataset.photoName);
  }
  return Number(b.dataset.identityScore||-Infinity)-Number(a.dataset.identityScore||-Infinity) ||
    a.dataset.photoName.localeCompare(b.dataset.photoName);
}
const gallerySort=document.getElementById("gallery-sort");
gallerySort.addEventListener("change",event=>{
  const mode=event.target.value;
  for(const grid of document.querySelectorAll(".photos")){
    [...grid.querySelectorAll("a")].sort((a,b)=>galleryCompare(a.querySelector("img"),b.querySelector("img"),mode)).forEach(link=>grid.append(link));
  }
  for(const link of document.querySelectorAll(".person-review-link")){
    const url=new URL(link.href,location.href);url.searchParams.set("sort",mode);link.href=url.toString();
  }
});
document.getElementById("thumbnail-framing").addEventListener("change",event=>{
  for(const image of document.querySelectorAll(".photos img[data-head]"))image.src=event.target.value==="head"?image.dataset.head:image.dataset.chest;
});
</script>""")
    out.append("</body></html>")
    return "\n".join(out) + "\n"


def render_md(rows, stamp, counts, files_dir, html_name, columns=3,
              pairing_report_href="../comparisons/pairings/angel-prospect-candidates.md",
              review_href="people_gallery_review.html",
              identity_report_href="identity-rankings.md"):
    """A Markdown table of three people per row; thumbnails sit in <report>_files next to it."""
    files_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# People gallery", "",
        f"Generated {stamp}. The HTML page is [{html_name}]({html_name}) and uses the sibling review-thumbnail cache; it shows up to nine photos per person.",
        f"Full library likeness rankings: [{identity_report_href}]({identity_report_href}). Scores are centroid similarities, not proof of identity.",
        "",
    ]
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
        for index, photo in enumerate(r["gallery_photos"], 1):
            thumbnail = photo.get("thumbnail")
            if not thumbnail or not (files_dir.parent / thumbnail).is_file():
                name = f"{slug(r['status'])}_{slug(r['folder'])}_{index}.jpg"
                (files_dir / name).write_bytes(photo["thumb"])
                thumbnail = f"{files_dir.name}/{name}"
            parts.append(f"[![{r['folder']} photo {index}]({thumbnail})]({pathlib.Path(photo['path']).resolve().as_uri()})")
        tags = [f'{r["photos"]} photo{"s" if r["photos"] != 1 else ""}']
        if r["chosen"]:
            tags.append("workflow")
        if r.get("z_path"):
            tags.append(f'[history]({pathlib.Path(r["z_path"]).resolve().as_uri()})')
        tag_line = " · ".join(tags)
        key = r.get("key", f'{r["status"]}/{r["folder"]}')
        review_link = f'{review_href}?{urlencode({"person": key, "bucket": "Gallery", "sort": "identity"})}'
        name = f"[{r['folder']}]({review_link})"
        summary = profile_summary(r["tags"])
        summary_text = f"<br>{summary}" if summary else ""
        closest = r.get("identity_matches_by_category", [])
        if closest:
            matches_text = "<br>Closest by category: " + "; ".join(
                f'{match["category"]}: {match["name"]} ({match["score"]:.2f})'
                for match in closest
            )
        else:
            matches_text = ""
        identity_label = f"<br>Person: {r['person_name']}" if r.get("person_name") else ""
        caption_parts = caption(r)
        if r.get("chosen") and r.get("source_path"):
            visible_names = {photo["name"] for photo in r.get("gallery_photos", [])[:9]}
            source_label = "workflow photo"
            if r.get("source_identity_score") is not None:
                source_label += f" · likeness {r['source_identity_score']:.2f}"
            if r["source"] not in visible_names:
                source_label += " (not shown)"
            source_uri = pathlib.Path(r["source_path"]).resolve().as_uri()
            caption_parts = [
                f"[{source_label}]({source_uri})" if part == "chosen source photo" else part
                for part in caption_parts
            ]
        caption_text = " · ".join(caption_parts)
        pairing_text = ""
        candidates = r.get("candidate_prospects", [])
        if r["status"] == "Angels" and r.get("paired_sister"):
            sister_score = identity_match_score(r, "Sisters", r["paired_sister"])
            ranked = "<br>".join(
                f'{index}. {candidate["name"]} (adjusted {candidate["cost"]:.3f}, '
                f'{"likeness %.2f, " % candidate["score"] if candidate.get("score") is not None else ""}'
                f'fit {candidate["likeness_cost"]:.3f}, +{candidate["photo_bonus"]:.2f}, '
                f'{candidate["photos"]} photos)'
                for index, candidate in enumerate(candidates, 1)
            )
            pairing_text = f"<br>Paired Sister: {r['paired_sister']}"
            if sister_score is not None:
                pairing_text += f" ({sister_score:.2f})"
            if ranked:
                pairing_text += f"<br>Top Prospect alternatives:<br>{ranked}"
            pairing_text += f" ([full rankings]({pairing_report_href}))"
        elif r["status"] == "Sisters" and r.get("paired_angel"):
            ranked = "<br>".join(
                f'{index}. {candidate["name"]} ('
                f'{"likeness %.2f, " % candidate["score"] if candidate.get("score") is not None else ""}'
                f'fit {candidate["cost"]:.3f}, {candidate["photos"]} photos)'
                for index, candidate in enumerate(candidates, 1)
            )
            angel_name = r["paired_angel"]["folder"]
            angel_score = identity_match_score(r, "Angels", angel_name)
            pairing_text = f"<br>Current Angel: {angel_name}"
            if angel_score is not None:
                pairing_text += f" ({angel_score:.2f})"
            if ranked:
                pairing_text += f"<br>Top Prospect alternatives:<br>{ranked}"
            pairing_text += f" ([full rankings]({pairing_report_href}))"
        elif r["status"] in ("Prospects", "Potentials") and r.get("best_angel_match"):
            match = r["best_angel_match"]
            candidate = match["candidate"]
            pairing_text = (
                f'<br>Best Angel: {match["angel"]["folder"]} '
                f'({candidate["score"]:.2f} likeness, adjusted {candidate["cost"]:.3f}, '
                f'{candidate["photos"]} photos; '
                f'[full rankings]({pairing_report_href}))'
            )
        cells.append(" ".join(parts) + f"<br>**{name}**<br>{tag_line}{identity_label}{summary_text}<br>" + caption_text + matches_text + pairing_text)
    flush()
    return "\n".join(lines) + "\n"


def render_identity_report(rows, stamp):
    lines = [
        "# Full library likeness rankings",
        "",
        f"Generated {stamp}. Each identity is ranked against every other identity included in this gallery. Scores compare folder centroids and are likeness evidence, not same-person verification or family confirmation.",
        "",
    ]
    for row in rows:
        lines += [
            f"## {row['status']}: {row['folder']}",
            "",
            "| Rank | Category | Identity | Similarity |",
            "| ---: | --- | --- | ---: |",
        ]
        matches = row.get("identity_rankings", [])
        for index, match in enumerate(matches, 1):
            lines.append(
                f"| {index} | {match['category']} | {match['name']} | {match['score']:.3f} |"
            )
        if not matches:
            lines.append("| - | - | No other scored identity | - |")
        lines.append("")
    return "\n".join(lines)


def render_pairing_report(rows, stamp):
    lines = [
        "# Angel–Prospect candidates by sister pairing",
        "",
        f"Generated {stamp}. Each eligible candidate is scored against the configured counterpart using the same shared scoring function as `likeness pairs` and the rebaseline report.",
        "Stage 1 requires at least five usable photos and 0.45 folder cohesion. Stage 2 combines likeness fit with a bounded variety bonus: +0.02 at 10 photos, +0.04 at 15, and +0.06 at 20. The bonus subtracts from fit cost; it lets a larger, coherent group edge ahead when likeness fits are reasonably close, but does not remove the preferred likeness band.",
        "The target similarity is 0.28 (preferred band 0.15–0.40). Candidates are ranked independently per Angel, so the same Prospect may appear more than once. The global `likeness pairs` preview additionally prevents duplicate assignments and penalizes clashes with other selected Angels. Scores are relative likeness evidence, not verified identity. No files or assignments are changed.",
        "",
    ]
    for angel in (row for row in rows if row["status"] == "Angels" and row.get("paired_sister")):
        lines += [
            f"## {angel['folder']} → {angel['paired_sister']}",
            "",
            f"Current hair color: {angel.get('hair_color') or 'not specified in canonical identity data'}",
            "",
            "| Rank | Prospect | Similarity | Usable photos | Cohesion | Likeness cost | Variety bonus | Adjusted cost |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        candidates = angel.get("candidate_rankings", [])
        for index, candidate in enumerate(candidates, 1):
            lines.append(
                f"| {index} | {candidate['name']} | {candidate['score']:.3f} | {candidate['photos']} | "
                f"{candidate['cohesion']:.3f} | {candidate['likeness_cost']:.3f} | {candidate['photo_bonus']:.2f} | {candidate['cost']:.3f} |"
            )
        if not candidates:
            lines.append("| - | No eligible Prospect folders | - | - | - | - |")
        lines.append("")
    return "\n".join(lines)


def main(argv=None, space=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--artists", action="store_true", help="also the people grouped inside the artists' folders")
    ap.add_argument("--out", help="folder for the report (default: <work>\\_reports\\library)")
    ap.add_argument("--root", help="the photo library folder (default: workspaces.json paths.workRoot)")
    ap.add_argument("--cache", help="embedding cache file (default: the user-local likeness cache)")
    ap.add_argument("--no-renders", action="store_true", help="ignore saved ComfyUI face renders, matching `likeness pairs --no-renders`")
    args = ap.parse_args(argv)
    groups = ["Angels", "Sisters", "Models", "Prospects", "Potentials"] + (["Artists"] if args.artists else [])
    if space is None:
        cfg, st, work, cache, space = likeness.build(types.SimpleNamespace(root=args.root, cache=args.cache, embedder=None))
        rend = None if args.no_renders else likeness.Renders(cfg, cache, likeness.Embedder(), st, space)
    else:
        cfg, st, work = space.cfg, space.st, space.work
        rend = None if args.no_renders else getattr(space, "renders", None)
    reports = work / "_reports"
    out = pathlib.Path(args.out) if args.out else reports / "library"
    out.mkdir(parents=True, exist_ok=True)
    rows = collect(cfg, st, work, space, groups, rend=rend)
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    pairing_dir = reports / "comparisons" / "pairings"
    pairing_dir.mkdir(parents=True, exist_ok=True)
    pairing_report = pairing_dir / "angel-prospect-candidates.md"
    pairing_report.write_text(render_pairing_report(rows, stamp), encoding="utf-8")
    identity_report = out / "identity-rankings.md"
    identity_report.write_text(render_identity_report(rows, stamp), encoding="utf-8")
    report_href = pathlib.Path("..") / "comparisons" / "pairings" / pairing_report.name if out == reports / "library" else pathlib.Path(os.path.relpath(pairing_report, out))
    (out / "people_gallery.html").write_text(
        render_html(
            rows, stamp, counts, report_href.as_posix(), thumbnail_dir=out,
            identity_report_href=identity_report.name,
        ),
        encoding="utf-8",
    )
    (out / "people_gallery.md").write_text(render_md(rows, stamp, counts, out / "people_gallery_review_files", "people_gallery.html",
                                                     pairing_report_href=report_href.as_posix(),
                                                     identity_report_href=identity_report.name), encoding="utf-8")
    size_mb = (out / "people_gallery.html").stat().st_size / 1e6
    print(f"people gallery: {len(rows)} people ({', '.join(f'{v} {k}' for k, v in counts.items())}); chosen photos {sum(r['chosen'] for r in rows)}, best guesses {sum(1 for r in rows if not r['chosen'] and r['score'] is not None)}")
    print(f"  {out / 'people_gallery.html'}  ({size_mb:.1f} MB, thumbnails in people_gallery_review_files)\n  {out / 'people_gallery.md'}  (uses the shared people_gallery_review_files cache)")
    print(f"  {pairing_report}")
    print(f"  {identity_report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
