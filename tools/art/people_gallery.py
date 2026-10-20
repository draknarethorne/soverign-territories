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

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/workflows"))
sys.path.insert(0, str(ROOT / "tools/art"))
import comfy_workflows as cw  # noqa: E402
import likeness  # noqa: E402
import originals  # noqa: E402
import people  # noqa: E402

THUMB = (188, 220)  # the 944x1104 shape at a fifth of the size
MAX_PHOTOS = 9
SECTIONS = [("Sisters", "Sisters"), ("Angels", "Angels"), ("Prospects", "Prospects"), ("Potentials", "Potentials"), ("Artists", "Artists' people")]
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


def thumb_bytes(path, kind="JPEG"):
    from PIL import Image, ImageOps
    with Image.open(path) as im:
        im = ImageOps.fit(ImageOps.exif_transpose(im).convert("RGB"), THUMB, Image.LANCZOS)
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


def prior_prospect_name(folder, status):
    """Return the recorded identity name when this Angel or Sister came from Prospect processing."""
    if status not in ("Angels", "Sisters"):
        return None
    history = people.read(folder)
    if not history:
        return None
    name, events = history
    if any("promoted from Prospects" in event or "from Prospects/" in event for event in events):
        return name
    return None


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


def collect(cfg, st, work, space, groups, rend=None):
    """Build one row per person, with at most nine original-photo thumbnails."""
    st = st or likeness.SETTINGS
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
               "chosen": False, "score": None, "source": "", "tags": people.profile(folder),
               "gallery_path": folder / "gallery", "z_path": people.find(folder),
               "prospect_name": prior_prospect_name(folder, status)}
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
        ordered = sorted(all_originals, key=lambda p: (p.name != row["source"], p.name.lower()))
        row["gallery_photos"] = [{"name": p.name, "path": p, "thumb": thumb_bytes(p)} for p in ordered[:MAX_PHOTOS]]
        people_rows.append(row)
    add_pairing_navigation(people_rows)
    return people_rows


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def caption(r):
    bits = []
    if r["review"]:
        bits.append(f"{r['review']} in review")
    bits.append("chosen source photo" if r["chosen"] else f"Prime-start photo score {r['score']:.2f}" if r["score"] is not None else "no usable face" if r["photos"] else "no gallery photos")
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
nav a{margin-right:16px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.card{background:#fff;border:1px solid #e0d8c8;border-radius:6px;padding:8px;margin:0}.photos{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:3px}
.photos img{display:block;width:100%;aspect-ratio:188/220;object-fit:cover;border-radius:3px;background:#eee}
.card b{font-size:1.05em}.meta{color:#666;font-size:.85em;margin-top:4px}.chosen{background:#2e7d32;color:#fff;border-radius:3px;padding:0 5px;font-size:.8em}.status{color:#888;font-size:.8em}.identity{font-size:.82em;color:#34495e;margin-top:4px}
.summary{color:#555;font-size:.9em;margin-top:3px}.readiness{color:#555;font-size:.82em;margin-top:5px}.matches{color:#34495e;font-size:.82em;margin-top:3px}.pairing{font-size:.82em;margin-top:5px}.noimg{display:flex;align-items:center;justify-content:center;aspect-ratio:188/220;background:#eee;color:#999;font-size:.8em}"""


def render_html(rows, stamp, counts, pairing_report_href="../comparisons/pairings/angel-prospect-candidates.md"):
    out = ["<!doctype html>", '<html lang="en"><head><meta charset="utf-8"><title>People gallery</title>', f"<style>{CSS}</style></head><body>", "<h1>People gallery</h1>",
           f'<p class="meta">Generated {html.escape(stamp)}. Each card shows up to nine original photos; click a photo to open it, or the photo count to open the person\'s gallery folder. '
           'A Prime-start photo score estimates photo suitability, not identity confidence. Prospect sister matches are face-embedding similarities, not verified identities. '
           'Angel alternatives are independently ranked by fit to the configured sister pairing target (0.28); eligible prospects need at least five usable photos and 0.45 cohesion. '
           'A Prospect may therefore appear for multiple Angels; use the full report to compare candidates across the roster. '
           'Current hair colors come from canonical Angel identity data and may change. Readiness evidence does not estimate distinct poses. '
           'Sisters link to their paired Angel and top eligible Prospect alternatives; Angels are ordered by pairing fit, Prospects by photo count, and Potentials are kept separate from Angel candidates. '
           'Folder links open the local folder through the browser or its registered handler; the name links to the person\'s history file when available.</p>',
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
            title = html.escape(photo["name"], quote=True)
            imgs.append(f'<a href="{href}" target="_blank" rel="noopener noreferrer"><img src="{b64(photo["thumb"])}" alt="{title}" title="{title}"></a>')
        if not imgs:
            imgs.append('<div class="noimg">no photos</div>')
        flag = ' <span class="chosen">chosen</span>' if r["chosen"] else ""
        name = html.escape(r["folder"])
        if r.get("z_path"):
            href = html.escape(pathlib.Path(r["z_path"]).resolve().as_uri(), quote=True)
            name = f'<a href="{href}" target="_blank" rel="noopener noreferrer">{name}</a>'
        folder_href = html.escape(pathlib.Path(r["gallery_path"]).resolve().as_uri(), quote=True)
        count = f'Open folder · {r["photos"]} photo{"s" if r["photos"] != 1 else ""}'
        summary = profile_summary(r["tags"])
        summary_html = f'<div class="summary">{html.escape(summary)}</div>' if summary else ""
        readiness_html = ""
        matches_html = ""
        pairing_html = ""
        card_id = person_anchor(r["status"], r["folder"])
        if r["status"] in ("Prospects", "Potentials"):
            readiness = (f"Photo evidence: {r.get('usable', 0)}/{r['photos']} usable faces · {r.get('full_length', 0)} full-length · "
                         f"median face {r.get('median_face_px', 0)}px · {r['review']} in review")
            issues = [f"{r.get('no_face', 0)} no face", f"{r.get('too_small', 0)} too small", f"{r.get('unreadable', 0)} unreadable"]
            readiness += " · unusable: " + ", ".join(issues)
            readiness_html = f'<div class="readiness">{html.escape(readiness)}</div>'
            if r.get("sister_matches"):
                sisters = " · ".join(
                    f'<a href="#{person_anchor("Sisters", m["name"])}">{html.escape(m["name"])}</a> {m["score"]:.2f}'
                    for m in r["sister_matches"]
                )
                matches_html = f'<div class="matches">Closest sister matches (similarity): {sisters}</div>'
            best_match = r.get("best_angel_match")
            if best_match:
                angel = best_match["angel"]
                candidate = best_match["candidate"]
                fit_link = f'<a href="#{person_anchor("Angels", angel["folder"])}">{html.escape(angel["folder"])}</a>'
                pairing_html = (
                    f'<div class="pairing">Best Angel pairing fit: {fit_link} '
                    f'(rank {best_match["rank"]}, fit distance {candidate["cost"]:.3f})</div>'
                )
        elif r["status"] == "Angels":
            parts = []
            if r.get("paired_sister"):
                sister_link = f'<a href="#{person_anchor("Sisters", r["paired_sister"])}">{html.escape(r["paired_sister"])}</a>'
                parts.append(f"Paired Sister: {sister_link}")
            if r.get("hair_color"):
                parts.append(f"Current hair: {html.escape(r['hair_color'])}")
            candidates = r.get("candidate_prospects", [])
            if candidates:
                alts = " · ".join(
                    f'<a href="#{person_anchor("Prospects", c["name"])}">{html.escape(c["name"])}</a> '
                    f'{index}. adjusted fit {c["cost"]:.3f} (likeness {c["likeness_cost"]:.3f}, +{c["photo_bonus"]:.2f} variety), {c["photos"]} photos'
                    for index, c in enumerate(candidates, 1)
                )
                parts.append("Top Prospect alternatives by pairing fit: " + alts)
                command = f'bin\\likeness.cmd promote "{candidates[0]["name"]}" "{r["folder"]}"'
                parts.append(f'<span>Promotion preview: <code>{html.escape(command)}</code> (add <code>--apply</code> only after reviewing)</span>')
            if parts:
                parts.append(f'<a href="{html.escape(pairing_report_href, quote=True)}">Full Angel–Prospect rankings</a>')
                pairing_html = f'<div class="pairing">{"<br>".join(parts)}</div>'
        elif r["status"] == "Sisters":
            paired_angel = r.get("paired_angel")
            if paired_angel:
                angel_link = f'<a href="#{person_anchor("Angels", paired_angel["folder"])}">{html.escape(paired_angel["folder"])}</a>'
                parts = [f"Current Angel pairing: {angel_link}"]
                candidates = r.get("candidate_prospects", [])
                if candidates:
                    alternatives = " · ".join(
                        f'<a href="#{person_anchor("Prospects", c["name"])}">{html.escape(c["name"])}</a> '
                        f'{index}. adjusted fit {c["cost"]:.3f} (likeness {c["likeness_cost"]:.3f}, +{c["photo_bonus"]:.2f} variety), {c["photos"]} photos'
                        for index, c in enumerate(candidates, 1)
                    )
                    parts.append(f"Top Prospect alternatives: {alternatives}")
                parts.append(f'<a href="{html.escape(pairing_report_href, quote=True)}">Full Angel–Prospect rankings</a>')
                pairing_html = f'<div class="pairing">{"<br>".join(parts)}</div>'
        identity_label = f"Prospect identity: {r['prospect_name']}" if r.get("prospect_name") else ""
        caption_text = " · ".join(caption(r))
        if identity_label:
            caption_text += f" · {identity_label}" if caption_text else identity_label
        out.append(f'<figure class="card" id="{card_id}"><div class="photos">{"".join(imgs)}</div><figcaption><b>{name}</b>{flag} <span class="status">{html.escape(r["status"])}</span>'
                   f'{summary_html}<div class="meta"><strong><a href="{folder_href}" title="Open this person\'s local gallery folder">{count}</a></strong></div>'
                   f'<div class="meta">{html.escape(caption_text)}</div>{readiness_html}{matches_html}{pairing_html}</figcaption></figure>')
    if current:
        out.append("</div>")
    out.append("</body></html>")
    return "\n".join(out) + "\n"


def render_md(rows, stamp, counts, files_dir, html_name, columns=3,
              pairing_report_href="../comparisons/pairings/angel-prospect-candidates.md"):
    """A Markdown table of three people per row; thumbnails sit in <report>_files next to it."""
    files_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# People gallery", "", f"Generated {stamp}. The self-contained HTML page is [{html_name}]({html_name}); it shows up to nine photos per person.", ""]
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
            name = f"{slug(r['status'])}_{slug(r['folder'])}_{index}.jpg"
            (files_dir / name).write_bytes(photo["thumb"])
            parts.append(f"[![{r['folder']} photo {index}]({files_dir.name}/{name})]({pathlib.Path(photo['path']).resolve().as_uri()})")
        flag = " (chosen)" if r["chosen"] else ""
        folder_link = pathlib.Path(r["gallery_path"]).resolve().as_uri()
        count = f"[{r['photos']} photo{'s' if r['photos'] != 1 else ''}]({folder_link})"
        name = r["folder"]
        if r.get("z_path"):
            name = f"[{name}]({pathlib.Path(r['z_path']).resolve().as_uri()})"
        summary = profile_summary(r["tags"])
        summary_text = f"<br>{summary}" if summary else ""
        identity_label = f"Prospect identity: {r['prospect_name']}" if r.get("prospect_name") else ""
        caption_text = " · ".join(caption(r))
        if identity_label:
            caption_text += f" · {identity_label}" if caption_text else identity_label
        pairing_text = ""
        candidates = r.get("candidate_prospects", [])
        if r["status"] == "Angels" and r.get("paired_sister"):
            ranked = "; ".join(
                f'{candidate["name"]} (adjusted {candidate["cost"]:.3f}, '
                f'likeness {candidate["likeness_cost"]:.3f}, +{candidate["photo_bonus"]:.2f}, '
                f'{candidate["photos"]} photos)'
                for candidate in candidates
            )
            pairing_text = f"<br>Paired with {r['paired_sister']}"
            if ranked:
                pairing_text += f"; leading Prospect candidates: {ranked}"
            pairing_text += f" ([full rankings]({pairing_report_href}))"
        elif r["status"] == "Sisters" and r.get("paired_angel"):
            ranked = "; ".join(
                f'{candidate["name"]} (adjusted {candidate["cost"]:.3f}, '
                f'{candidate["photos"]} photos)'
                for candidate in candidates
            )
            pairing_text = f"<br>Current Angel: {r['paired_angel']['folder']}"
            if ranked:
                pairing_text += f"; leading Prospect candidates: {ranked}"
            pairing_text += f" ([full rankings]({pairing_report_href}))"
        elif r["status"] in ("Prospects", "Potentials") and r.get("best_angel_match"):
            match = r["best_angel_match"]
            candidate = match["candidate"]
            pairing_text = (
                f'<br>Best Angel pairing: {match["angel"]["folder"]} '
                f'(adjusted {candidate["cost"]:.3f}, {candidate["photos"]} photos; '
                f'[full rankings]({pairing_report_href}))'
            )
        cells.append(" ".join(parts) + f"<br>**{name}**{flag}<br>{count}{summary_text}<br>" + caption_text + pairing_text)
    flush()
    return "\n".join(lines) + "\n"


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
    ap.add_argument("--no-renders", action="store_true", help="ignore saved ComfyUI face renders, matching `likeness pairs --no-renders`")
    args = ap.parse_args(argv)
    groups = ["Angels", "Sisters", "Prospects", "Potentials"] + (["Artists"] if args.artists else [])
    if space is None:
        cfg, st, work, cache, space = likeness.build(types.SimpleNamespace(root=args.root, cache=None, embedder=None))
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
    report_href = pathlib.Path("..") / "comparisons" / "pairings" / pairing_report.name if out == reports / "library" else pathlib.Path(os.path.relpath(pairing_report, out))
    (out / "people_gallery.html").write_text(render_html(rows, stamp, counts, report_href.as_posix()), encoding="utf-8")
    (out / "people_gallery.md").write_text(render_md(rows, stamp, counts, out / "people_gallery_files", "people_gallery.html",
                                                     pairing_report_href=report_href.as_posix()), encoding="utf-8")
    size_mb = (out / "people_gallery.html").stat().st_size / 1e6
    print(f"people gallery: {len(rows)} people ({', '.join(f'{v} {k}' for k, v in counts.items())}); chosen photos {sum(r['chosen'] for r in rows)}, best guesses {sum(1 for r in rows if not r['chosen'] and r['score'] is not None)}")
    print(f"  {out / 'people_gallery.html'}  ({size_mb:.1f} MB, one file)\n  {out / 'people_gallery.md'}  (thumbnails in people_gallery_files)")
    print(f"  {pairing_report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
