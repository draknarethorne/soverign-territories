"""One HTML page per sandbox rebase run explaining what it planned or applied, plus an index of runs.

Reads only RUN\\run.json, the intake manifest, sibling runs and the user's expectations file (beside Working, so a
sandbox reset keeps it). It lists every photo that stayed, moved between people, moved between gallery and review,
or was renamed; Angels/Sisters gains and losses; new identities grouped by family surname with their nearest cast
member and the user's own "looks like" pick; score-band families with each member's link, score and path; review
holds; differences from other runs of the same inputs (for
example all versus core cast seeds); and whether expected photo placements happened. No library file is changed.
sandbox-rebase.cmd regenerates it after every preview, replan, apply, check and undo.
"""

import argparse
import collections
import hashlib
import html
import json
import os
import pathlib
import statistics
import sys
import urllib.parse

if __package__:
    from . import gallery_chrome
else:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
    from tools.art.likeness_library import gallery_chrome

CAST = ("Angels", "Sisters")
OUT_DIR = "rebase-recap"
EXPECTATIONS_NAME = "rebase-expectations.json"
NEW_PERSON = "new person"
UNSURE = "unsure"
HISTORY_PARTS = ("_reports", "reset-review-bundle", "rebase-runs")
MULTIFACE_NOTE = (
    "<p class=muted>Saved 2+ faces labels reflect the detector's observations. "
    "Detector observations are not confirmed people counts; inspect the photo before deciding. "
    "The saved label and quality hold are unchanged.</p>"
)


def _historical_run(run):
    return tuple(pathlib.Path(run).parent.parts[-3:]) == HISTORY_PARTS


def person_and_bucket(relative):
    """("Angels/Camaris", "gallery") for Angels/Camaris/gallery/x.jpg; ("Various", "review") for Various/review/x."""
    parts = pathlib.PurePosixPath(relative).parts
    for index, part in enumerate(parts[:-1]):
        if part in ("gallery", "review"):
            return "/".join(parts[:index]), part
    return "/".join(parts[:-1]), ""


def change_kind(row):
    old_person, old_bucket = person_and_bucket(row["source"])
    old_person = row.get("oldFolder") or old_person
    new_person, new_bucket = person_and_bucket(row["destination"])
    if old_person != new_person:
        return "moved-to-review" if new_bucket == "review" else "moved"
    if old_bucket != new_bucket:
        return "to-review" if new_bucket == "review" else "from-review"
    if row["source"] != row["destination"]:
        old_path = pathlib.PurePosixPath(row["source"])
        new_path = pathlib.PurePosixPath(row["destination"])
        if old_path.stem != new_path.stem:
            return "renamed"
        if old_path.suffix.lower() != new_path.suffix.lower():
            return "converted"
        return "path-changed"
    return "stayed"


def _placement_kind(source, destination, old_person, new_person, old_bucket, new_bucket):
    source_path = pathlib.PurePosixPath(source)
    destination_path = pathlib.PurePosixPath(destination)
    if old_person != new_person and old_bucket != new_bucket:
        return "Identity move and Review transition"
    if old_person != new_person:
        return "Identity move"
    if old_bucket != new_bucket:
        return "Review transition"
    if source == destination:
        return "No change"
    changes = []
    if source_path.stem != destination_path.stem:
        changes.append("Rename")
    if source_path.suffix.lower() != destination_path.suffix.lower():
        changes.append("Format conversion")
    if changes:
        return " + ".join(changes)
    return "Path change"


def _preparation_roots(run, plan):
    reused = plan.get("reusedPreparationFrom")
    if isinstance(reused, dict):
        reused = reused.get("run") or reused.get("path") or reused.get("root")
    if not isinstance(reused, str) or not reused:
        return []
    path = pathlib.Path(reused)
    if not path.is_absolute():
        path = run.parent / path
    return [path]


def _manifest_rows(run, plan=None):
    candidates = []
    for root in [*_preparation_roots(run, plan or {}), run]:
        candidates.extend((
            root / "inputs" / "_reports" / "preparation" / "all" / "manifest.json",
            root / "_reports" / "preparation" / "all" / "manifest.json",
            root / "manifest.json",
        ))
    for path in candidates:
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            return {row["source"]: row for row in data.get("photos", [])}, path.parent
    return {}, None


def _incoming_aliases(run, plan):
    expected = plan.get("sourceOverlaySHA256")
    if not expected or _historical_run(run):
        return []
    overlay_root = run / "source-overlay"
    reused = _preparation_roots(run, plan)
    if reused:
        original = reused[0]
        if (original.parent != run.parent or original == run
                or pathlib.Path(plan.get("sourceRoot", "")) != original / "source-overlay"):
            raise ValueError("recap continuation overlay root differs from original sibling run")
        overlay_root = original / "source-overlay"
    payload = (overlay_root / "overlay.json").read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected:
        raise ValueError("recap source overlay differs from saved plan")
    overlay = json.loads(payload)
    destinations = {row["source"]: row for row in plan["photos"]}
    aliases = []
    for row in overlay["currentVarious"]:
        if not row.get("duplicateOf"):
            continue
        canonical = destinations.get(row["target"])
        if (row["sha256"] != overlay["inputs"][row["target"]]["sha256"] or not canonical
                or canonical.get("sha256") != row["sha256"]):
            raise ValueError("recap incoming alias lacks a canonical destination")
        aliases.append({
            "arrival": row["current"], "canonical": row["target"],
            "destination": canonical["destination"],
        })
    return aliases


def collect(run):
    """Every planned/applied photo row with its change, plus grouped views; pure data, no HTML."""
    run = pathlib.Path(run)
    plan = json.loads((run / "run.json").read_text(encoding="utf-8"))
    historical = _historical_run(run)
    manifest, preparation = ({}, None) if historical else _manifest_rows(run, plan)
    rows = []
    for photo in plan["photos"]:
        old_person, old_bucket = person_and_bucket(photo["source"])
        old_person = photo.get("oldFolder") or old_person
        new_person, new_bucket = person_and_bucket(photo["destination"])
        source_name = pathlib.PurePosixPath(photo["source"]).name
        new_name = pathlib.PurePosixPath(photo["destination"]).name
        prepared = manifest.get(photo.get("preparationSource") or photo["source"]) or {}
        variants = prepared.get("variants", {})
        chosen = next((item for item in variants.values() if item.get("path") == photo.get("preparedPath")), None)
        preview = (chosen or variants.get("control") or {}).get("thumbnail")
        detail = prepared.get("detail")
        if prepared and not detail:
            detail = f"photos/{hashlib.sha256(prepared['source'].encode('utf-8')).hexdigest()}.html"
        top_cast = photo.get("topCastReferences") or photo.get("initialCastReferences")
        if not top_cast:
            top_cast = [
                {"folder": photo.get("initialBestCast"), "score": photo.get("initialBestCastScore")},
                {"folder": photo.get("initialSecondCast"), "score": photo.get("initialSecondCastScore")},
                {"folder": photo.get("initialThirdCast"), "score": photo.get("initialThirdCastScore")},
            ]
        top_cast = [item for item in top_cast if isinstance(item, dict) and item.get("folder")]
        rows.append({
            "source": photo["source"], "destination": photo["destination"],
            "originalFolder": photo.get("sourceFolder") or old_person,
            "oldPerson": old_person, "oldBucket": old_bucket, "newPerson": new_person, "newBucket": new_bucket,
            "kind": change_kind(photo),
            "placementKind": _placement_kind(
                photo["source"], photo["destination"], old_person, new_person, old_bucket, new_bucket,
            ),
            "sourcePathChanged": photo["source"] != photo["destination"],
            "renamed": pathlib.PurePosixPath(source_name).stem != pathlib.PurePosixPath(new_name).stem,
            "converted": pathlib.PurePosixPath(source_name).suffix.lower() != pathlib.PurePosixPath(new_name).suffix.lower(),
            "photoId": photo.get("photoId"), "sha256": photo.get("sha256"), "reason": photo.get("reason", ""),
            "preparedSHA256": photo.get("preparedSHA256"), "preparedPath": photo.get("preparedPath"),
            "score": photo.get("score"), "bestMatch": photo.get("bestMatch"), "bestScore": photo.get("bestScore"),
            "nearestCast": photo.get("initialBestCast"), "nearestCastScore": photo.get("initialBestCastScore"),
            "secondCast": photo.get("initialSecondCast"), "secondCastScore": photo.get("initialSecondCastScore"),
            "castMargin": photo.get("initialCastMargin"), "topCast": top_cast[:3],
            "retainedCast": photo.get("retainedCast"), "releasedCast": photo.get("releasedCast"),
            "castSeedCore": photo.get("castSeedCore"), "castSeedScore": photo.get("castSeedScore"),
            "clusterId": photo.get("clusterId"), "groupSize": photo.get("groupSize"),
            "destinationType": photo.get("destinationType"),
            "preparationOutcome": photo.get("preparationOutcome"),
            "preview": str(preparation / preview) if preparation and preview else None,
            "detail": str(preparation / detail) if preparation and detail else None,
        })
    cluster_sizes = collections.Counter(row["clusterId"] for row in rows if row["clusterId"])
    for row in rows:
        if row["groupSize"] is None and row["clusterId"]:
            row["groupSize"] = cluster_sizes[row["clusterId"]]
    old_people = {row["oldPerson"] for row in rows} | set(plan.get("referenceFolders", []))
    new_people = {row["newPerson"] for row in rows}
    final_audit = plan.get("finalMembershipAudit") or {}
    return {
        "run": str(run), "workingRoot": plan["workingRoot"], "status": plan["status"],
        "historical": historical,
        "sourceManifestSHA256": plan.get("sourceManifestSHA256"),
        "cast": sorted(person for person in old_people | new_people if person.startswith(CAST)),
        "createdAt": plan.get("createdAt"), "policy": plan.get("policy", {}).get("version")
        if isinstance(plan.get("policy"), dict) else plan.get("policy"),
        "castSeedPolicy": plan.get("castSeedPolicy", "all"),
        "recoveryMode": plan.get("recoveryMode", "full"),
        "incomingAliases": _incoming_aliases(run, plan),
        "preparationIndex": str(preparation / "index.html") if preparation else None,
        "rows": rows,
        "coreReferences": final_audit.get("coreReferences", plan.get("coreReferences")),
        "finalMembershipAudit": plan.get("finalMembershipAudit"),
        "membershipRefinement": plan.get("membershipRefinement"),
        "finalMembershipRefinement": plan.get("finalMembershipRefinement"),
        "familyNaming": plan.get("familyNaming"),
        "reassignmentStatus": plan.get("reassignmentStatus"),
        "convergenceStatus": plan.get("convergenceStatus"),
        "scoreBands": plan.get("policy", {}).get("scoreBands")
        if isinstance(plan.get("policy"), dict) else None,
        "newIdentities": sorted(new_people - old_people),
        "emptiedIdentities": sorted(person for person in old_people - new_people
                                    if person.count("/") == 1 and not person.startswith("Artists/")),
    }


def summarize(data):
    rows = data["rows"]
    kinds = collections.Counter(row["kind"] for row in rows)
    return {
        "photos": len(rows), "kinds": dict(kinds),
        "renamed": sum(row["renamed"] for row in rows), "converted": sum(row["converted"] for row in rows),
        "newIdentities": len(data["newIdentities"]), "emptiedIdentities": len(data["emptiedIdentities"]),
        "review": sum(row["newBucket"] == "review" for row in rows),
        "sourcePhotos": len(rows), "finalPhotos": len(rows),
        "countConserved": len(rows) == sum(row["newBucket"] in ("gallery", "review") for row in rows),
    }


def _href(target, out_dir):
    try:
        relative = os.path.relpath(target, out_dir).replace(os.sep, "/")
    except ValueError:
        return pathlib.Path(os.path.abspath(target)).as_uri()
    return urllib.parse.quote(relative, safe="/._-~")


def _score(value):
    return "" if value is None else f"{value:.3f}"


def _score_text(value):
    return "unavailable (not recorded)" if value is None else _score(value)


def _cast_reference_table(references, data, out_dir):
    if not isinstance(references, list) or not references:
        return '<span class=muted>unavailable (not recorded)</span>'
    items = [item for item in references if isinstance(item, dict) and item.get("folder")][:3]
    if not items:
        return '<span class=muted>unavailable (not recorded)</span>'
    return '<ol>' + "".join(
        f'<li>{_person_link(str(item["folder"]), data, out_dir)}: '
        f'<span class="score-badge {_score_class(item.get("score"), data)}">'
        f'{_score_text(item.get("score"))}</span></li>' for item in items
    ) + '</ol>'


def _final_cast_by_source(data):
    audit = data.get("finalMembershipAudit")
    if not isinstance(audit, dict):
        return {}
    return {item["source"]: item["castReferences"] for item in audit.get("rows", [])
            if isinstance(item, dict) and item.get("source") and "castReferences" in item}


def _score_class(value, data):
    bands = data.get("scoreBands")
    if value is None or not isinstance(bands, dict):
        return ""
    for band in ("green", "yellow", "orange"):
        minimum = bands.get(band, {}).get("minimum")
        if isinstance(minimum, (int, float)) and value >= minimum:
            return f"score-{band}"
    return "score-red"


def _score_band_label(value, data):
    score_class = _score_class(value, data)
    return (score_class.removeprefix("score-").title() + " similarity band; comparison only, "
            "not a rename recommendation") if score_class else "similarity band unavailable (score or policy not recorded)"


def _anchor(prefix, value):
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _working_target(relative, data):
    raw = str(relative)
    path = pathlib.PurePosixPath(raw)
    if not raw or path.is_absolute() or "\\" in raw or ".." in path.parts:
        return None
    root = pathlib.Path(data["workingRoot"]).resolve()
    target = root.joinpath(*path.parts)
    try:
        target.resolve().relative_to(root)
    except (OSError, ValueError):
        return None
    return target


def _safe_link(target, label, out_dir, *, new_tab=False):
    href = html.escape(_href(target, out_dir), quote=True)
    attrs = ' target="_blank" rel="noopener noreferrer"' if new_tab else ""
    return f'<a href="{href}"{attrs}>{html.escape(label)}</a>'


def _detail_link(anchor, label):
    return (f'<a href="#{html.escape(anchor, quote=True)}" target="_blank" rel="noopener noreferrer">'
            f'{html.escape(label)}</a>')


def _person_link(person, data, out_dir, *, bucket=None):
    person = str(person or "")
    label = html.escape(person or "not recorded")
    if data.get("historical"):
        return label
    valid = data.setdefault("_person_path_validity", {})
    if person not in valid:
        valid[person] = _working_target(person, data) is not None
    if not valid[person]:
        return label
    if "_person_folders" not in data:
        data["_person_folders"] = {row["newPerson"] for row in data["rows"]}
        data["_old_person_folders"] = {row["oldPerson"] for row in data["rows"]}
        data["_gallery_person_folders"] = {
            row["newPerson"] for row in data["rows"] if row["newBucket"] == "gallery"
        }
    if person not in data["_person_folders"]:
        if person in data["_old_person_folders"]:
            return _detail_link(_anchor("continuity", person), person)
        return label
    if data["status"] != "applied":
        if person.startswith(CAST):
            anchor = _anchor("cast", person)
        elif person in data["_gallery_person_folders"] and not person.startswith("Various"):
            anchor = _anchor("id", person)
        else:
            anchor = "review"
        return _detail_link(anchor, person)
    if "_review_page" not in data:
        review = pathlib.Path(data["workingRoot"]) / "_reports" / "library" / "people_gallery_review.html"
        data["_review_page"] = (review, review.is_file())
    review, available = data["_review_page"]
    if not available:
        return label + ' <span class=muted>(Photo review unavailable)</span>'
    params = {"person": person}
    if bucket in {"gallery", "review"}:
        params["bucket"] = bucket.title()
    href = _href(review, out_dir) + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    return f'<a href="{html.escape(href, quote=True)}" target="_blank" rel="noopener noreferrer">{label}</a>'


def _file_verification(target, expected, data):
    if not expected:
        return "unverified"
    target = pathlib.Path(target)
    cache = data.setdefault("_sha256_cache", {})
    key = str(target.resolve())
    if key not in cache:
        try:
            cache[key] = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else None
        except OSError:
            cache[key] = None
    actual = cache[key]
    return "missing" if actual is None else "verified" if actual == expected else "mismatch"


def _verified_photo_link(target, expected, label, data, out_dir):
    if target is None:
        return '<span class=muted>unsafe destination link unavailable</span>'
    status = _file_verification(target, expected, data)
    if status == "verified":
        return _safe_link(target, label, out_dir, new_tab=True)
    reason = {
        "unverified": "link withheld (expected SHA-256 not recorded)",
        "missing": "photo missing",
        "mismatch": "photo bytes differ from recorded SHA-256",
    }[status]
    return f'<span class=muted>{html.escape(reason)}</span>'


def _intake_detail_link(row, data, out_dir):
    detail = row.get("detail") if row else None
    preparation = data.get("preparationIndex")
    if not detail or not preparation:
        return ""
    target = pathlib.Path(detail)
    try:
        target.resolve().relative_to(pathlib.Path(preparation).parent.resolve())
    except ValueError:
        return '<span class=muted>unsafe intake detail link unavailable</span>'
    if not target.is_file():
        return '<span class=muted>intake detail missing</span>'
    return _safe_link(target, "Intake comparison", out_dir, new_tab=True)


def _prepared_preview_target(row, data):
    preparation, relative = data.get("preparationIndex"), row.get("preparedPath")
    if not preparation or not relative:
        return None
    path = pathlib.PurePosixPath(relative)
    if path.is_absolute() or "\\" in relative or ".." in path.parts:
        return None
    root = pathlib.Path(preparation).parent.resolve()
    target = root.joinpath(*path.parts)
    try:
        target.resolve().relative_to(root)
    except (OSError, ValueError):
        return None
    return target


def _destination_links(row, data, out_dir):
    if data.get("historical"):
        return '<span class=muted>Historical destination only; photo and gallery links unavailable after reset.</span>'
    if data["status"] != "applied":
        return (_verified_photo_link(
            _prepared_preview_target(row, data), row.get("preparedSHA256"),
            "Prepared preview (bytes verified; not installed)", data, out_dir,
        ) + " · Planned photo evidence: "
            + _person_link(row["newPerson"], data, out_dir, bucket=row["newBucket"]))
    photo = _working_target(row["destination"], data)
    return ("<span class=destination-links>"
            + _verified_photo_link(
                photo, row.get("preparedSHA256") or row.get("sha256"), "Final photo (bytes verified)", data, out_dir,
            ) + " · "
            + "Photo review: " + _person_link(row["newPerson"], data, out_dir, bucket=row["newBucket"]) + "</span>")


def _source_link(source, row, data, out_dir):
    """Distinguish a missing old path from verified final bytes or genuinely missing/tampered files."""
    target = _working_target(source, data)
    if target is None or data.get("historical"):
        return '<span class=muted>source link unavailable</span>'
    if data["status"] != "applied":
        intake_link = _intake_detail_link(row, data, out_dir)
        return _destination_links(row, data, out_dir) + (f" · {intake_link}" if intake_link else "")
    if target.is_file():
        status = _file_verification(target, row.get("sha256") if row else None, data)
        if status == "verified":
            source_link = _safe_link(target, "Source photo (bytes verified)", out_dir, new_tab=True)
        elif status == "unverified":
            source_link = '<span class=muted>source exists; hash not recorded, link withheld</span>'
        else:
            source_link = '<span class=muted>source bytes differ from recorded SHA-256; link withheld</span>'
    else:
        destination = _working_target(row["destination"], data) if row else None
        final_link = _verified_photo_link(
            destination,
            (row.get("preparedSHA256") or row.get("sha256")) if row else None,
            "Verified final photo",
            data,
            out_dir,
        )
        source_link = ("<span class=muted>previous location absent from this working tree</span> · "
                       + final_link)
    intake_link = _intake_detail_link(row, data, out_dir)
    return source_link + (f" · {intake_link}" if intake_link else "")


def _thumb(row, data, out_dir):
    if data.get("historical"):
        return '<span class=muted>Historical image unavailable: compact run evidence contains no images.</span>'
    live = _working_target(row["destination"], data)
    if live is None:
        return '<span class=muted>unsafe destination path</span>'
    if data["status"] != "applied":
        live = _prepared_preview_target(row, data)
        expected = row.get("preparedSHA256")
        if live is None or _file_verification(live, expected, data) != "verified":
            return _verified_photo_link(live, expected, "Prepared preview", data, out_dir)
    image = row["preview"] or str(live)
    if data["status"] != "applied" and not pathlib.Path(image).is_file():
        image = str(live)
    title = html.escape(f"{row['source']} -> {row['destination']}", quote=True)
    return (f'<a href="{html.escape(_href(live, out_dir), quote=True)}" target="_blank" '
            f'rel="noopener noreferrer" title="{title}">'
            f'<img loading="lazy" src="{html.escape(_href(image, out_dir), quote=True)}" alt=""></a>')


def _card(row, data, out_dir, note):
    links = f' · {_safe_link(row["detail"], "intake", out_dir, new_tab=True)}' if row["detail"] else ""
    return (f'<figure>{_thumb(row, data, out_dir)}<figcaption>{html.escape(note)}'
            f'<br>{_destination_links(row, data, out_dir)}{links}</figcaption></figure>')


def _origin(row):
    if row["originalFolder"] == row["oldPerson"]:
        return row["oldPerson"]
    return f"{row['oldPerson']} (first intake {row['originalFolder']})"


def _cards(rows, data, out_dir, note):
    if not rows:
        return "<p class=muted>None.</p>"
    return '<div class=grid>' + "".join(_card(row, data, out_dir, note(row)) for row in rows) + "</div>"


def _core_reference_rows(data, person):
    recorded = data.get("coreReferences")
    if isinstance(recorded, dict) and person in recorded:
        references = recorded[person]
        plan_rows = {row["source"]: row for row in data["rows"]}
        result = []
        for item in references[:10] if isinstance(references, list) else []:
            if not isinstance(item, dict) or not item.get("destination"):
                continue
            source = item.get("source", item["destination"])
            row = dict(plan_rows.get(source, {}))
            new_person, new_bucket = person_and_bucket(item["destination"])
            row.update(source=source, destination=item["destination"], photoId=item.get("photoId"),
                       newPerson=new_person, newBucket=new_bucket, castSeedScore=item.get("score"))
            row.setdefault("preview", None)
            row.setdefault("detail", None)
            result.append(row)
        return result
    return sorted(
        (row for row in data["rows"] if row["newPerson"] == person and row["newBucket"] == "gallery"
         and row["castSeedCore"] is True),
        key=lambda row: (-(row["castSeedScore"] if row["castSeedScore"] is not None else -2), row["source"]),
    )[:10]


def _cast_section(data, out_dir):
    rows = data["rows"]
    core_people = data.get("coreReferences") or {}
    people = sorted({row["oldPerson"] for row in rows if row["oldPerson"].startswith(CAST)}
                    | {row["newPerson"] for row in rows if row["newPerson"].startswith(CAST)}
                    | {person for person in core_people if person.startswith(CAST)})
    anchors = [(_anchor("cast", person), person) for person in people]
    parts = ["<h2 id=cast>Angels and Sisters</h2>",
             '<nav class="person-nav" aria-label="Filter to an Angel or Sister">'
             + '<a href="#cast" data-cast-filter="all">All Angels and Sisters</a>'
             + "".join(f'<a href="#{anchor}" data-cast-filter="{anchor}">{html.escape(person)}</a>'
                       for anchor, person in anchors)
             + "</nav>",
             "<p class=muted>Eligible core references use the final membership audit's ordered "
             "<code>coreReferences</code> top ten when recorded. Older runs fall back to top-level "
             "<code>coreReferences</code>, then recorded <code>castSeedCore</code> members. Retained Gallery membership "
             "alone is not treated as a measured core rank.</p>",
             "<table><tr><th>Person</th><th>Kept</th><th>Lost</th><th>Gained</th><th>Now in Review</th></tr>"]
    details = []
    for person in people:
        kept = [r for r in rows if r["oldPerson"] == person and r["newPerson"] == person and r["newBucket"] == "gallery"]
        held = [r for r in rows if r["newPerson"] == person and r["newBucket"] == "review"]
        lost = [r for r in rows if r["oldPerson"] == person and r["newPerson"] != person]
        gained = [r for r in rows if r["newPerson"] == person and r["oldPerson"] != person]
        anchor = _anchor("cast", person)
        parts.append(f'<tr><td>{_detail_link(anchor, person)}</td><td>{len(kept)}</td>'
                     f'<td class={"warn" if lost else ""}>{len(lost)}</td><td>{len(gained)}</td><td>{len(held)}</td></tr>')
        eligible = _core_reference_rows(data, person)
        core = (_cards(eligible, data, out_dir, lambda r: f"Eligible core reference; score {_score_text(r['castSeedScore'])}")
                if eligible else '<p class=muted>No eligible core references recorded for this person; '
                'Gallery membership alone does not establish a measured core rank.</p>')
        details.append(
            f'<details id="{anchor}"{" open" if lost or gained else ""}><summary>{html.escape(person)}: '
            f'{len(kept)} kept, {len(lost)} lost, {len(gained)} gained, {len(held)} in Review</summary>'
            f"<p>Full Photo review: {_person_link(person, data, out_dir)}</p>"
            f"<h4>Top ten recorded eligible core references</h4>{core}"
            f"<h4>Lost</h4>{_cards(lost, data, out_dir, lambda r: f'to {r['newPerson']} ({r['newBucket']}); {r['reason']}')}"
            f"<h4>Gained</h4>{_cards(gained, data, out_dir, lambda r: f'from {_origin(r)}; cluster-to-cast score {_score_text(r['bestScore'])}; nearest cast per-photo score {_score_text(r['nearestCastScore'])}')}"
            f"<h4>Review</h4>{_cards(held, data, out_dir, lambda r: r['reason'])}"
            "</details>")
    parts.append("</table>")
    return "".join(parts + details)


def _identity_section(data, out_dir):
    rows = data["rows"]
    members = collections.defaultdict(list)
    for row in rows:
        if not row["newPerson"].startswith((*CAST, "Various")) and row["newBucket"] == "gallery":
            members[row["newPerson"]].append(row)
    families = collections.defaultdict(list)
    family_members = _family_members(data)
    for person in members:
        family = family_members.get(person)
        families[family["surname"] if family else person.rsplit("/", 1)[-1].rsplit(None, 1)[-1]].append(person)
    new = set(data["newIdentities"])
    said = data.get("expectations", {}).get("identities", {})
    choices = ["", *data["cast"], NEW_PERSON, UNSURE]
    policy_text = (
        "Family surnames come from the score-band family tree (see <a href=\"#families\">Families</a>); they are "
        "presentation only, never kinship or same-person evidence. "
        if data.get("familyNaming") else
        "This run records no family naming policy; groups are literal shared surnames and no rename is inferred. "
    )
    parts = ["<h2 id=identities>Other identities (grouped by family surname)</h2>",
             "<p class=muted>Nearest-cast values are saved per-photo similarities, not routing decisions. "
             + policy_text +
             "Paired thumbnails are representative saved destinations, not visually verified identity evidence. "
             "Use <b>Looks like</b> "
             "to record your own judgement, then <b>Save my picks</b>; this preserves the existing expectations workflow.</p>",
             "<table><tr><th>Current identity</th><th>Family naming</th><th>Photos</th><th>Came from</th>"
             "<th>Nearest cast and mean per-photo score</th><th>Paired saved images</th>"
             "<th>Looks like (yours)</th></tr>"]
    details = []
    for surname, people in sorted(families.items(), key=lambda item: (-sum(len(members[p]) for p in item[1]), item[0])):
        for person in sorted(people, key=lambda p: -len(members[p])):
            group = members[person]
            origins = collections.Counter(r["oldPerson"] for r in group)
            nearest = collections.Counter(r["nearestCast"] for r in group if r["nearestCast"])
            top, count = nearest.most_common(1)[0] if nearest else ("-", 0)
            scores = [r["nearestCastScore"] for r in group if r["nearestCast"] == top and r["nearestCastScore"] is not None]
            mean = statistics.fmean(scores) if scores else None
            representative = min(group, key=lambda r: r["source"])
            cast_rows = _core_reference_rows(data, top) if top != "-" else []
            if not cast_rows:
                cast_rows = [
                row for row in rows if row["newPerson"] == top and row["newBucket"] == "gallery"
                and row["castSeedCore"] is True
                ] if top != "-" else []
            if not cast_rows and top != "-":
                cast_rows = [row for row in rows if row["newPerson"] == top and row["newBucket"] == "gallery"
                             and row["retainedCast"] is True]
            cast_representative = cast_rows[0] if cast_rows else None
            anchor = _anchor("id", person)
            mine = said.get(person, "")
            options = "".join(
                f'<option value="{html.escape(choice, quote=True)}"{" selected" if choice == mine else ""}>'
                f"{html.escape(choice or '-')}</option>" for choice in choices + ([mine] if mine not in choices else []))
            disagrees = mine.startswith(CAST)
            member = family_members.get(person)
            if member:
                naming = (f"{html.escape(member['status'])}"
                          + (f" (was {html.escape(member['previousName'])})" if member["status"].startswith("renamed") else "")
                          + f"<br><span class=muted>via {_person_link(member.get('parentFolder') or 'root', data, out_dir)}"
                          + (f" {_score(member['score'])} {html.escape(str(member['band']))}"
                             if member.get("score") is not None else "") + "</span>")
            else:
                naming = '<span class=muted>Not in a family</span>' if data.get("familyNaming") else \
                    '<span class=muted>Not recorded</span>'
            parts.append(
                f'<tr><td>{_detail_link(anchor, person)}'
                f'<br><span class=muted>family {html.escape(surname if len(people) > 1 or member else "not grouped")}</span></td>'
                f'<td>{naming}</td>'
                f'<td>{len(group)}</td><td>{", ".join(f"{_person_link(k, data, out_dir)} {v}" for k, v in origins.most_common(4))}</td>'
                f'<td>{_person_link(top, data, out_dir)} ({count}/{len(group)}, '
                f'<span class="score-badge {_score_class(mean, data)}">{_score_text(mean)}</span>'
                f'<small>{html.escape(_score_band_label(mean, data))}</small>)</td>'
                f'<td class=paired-images><div><b>Current identity</b>{_thumb(representative, data, out_dir)}'
                f'<small>{html.escape(representative["destination"])}</small></div>'
                + (f'<div><b>Nearest cast</b>{_thumb(cast_representative, data, out_dir)}'
                   f'<small>{html.escape(cast_representative["destination"])}</small></div>'
                   if cast_representative else
                   '<div><b>Nearest cast</b><span class=muted>verified representative unavailable</span></div>')
                + '</td>'
                f'<td class="{"warn" if disagrees else ""}"><select class=pick data-identity="{html.escape(person, quote=True)}">'
                f"{options}</select></td></tr>")
            details.append(
                f'<details id="{anchor}"><summary>{html.escape(person)}: {len(group)} photos</summary>'
                f"<p>Full Photo review: {_person_link(person, data, out_dir)}</p>"
                f"{_cards(group, data, out_dir, lambda r: f'from {_origin(r)}; nearest {r['nearestCast'] or '-'} {_score(r['nearestCastScore'])}')}"
                "</details>")
    parts.append("</table><p><button id=save-picks>Save my picks</button> "
                 f"<span class=muted>Downloads {EXPECTATIONS_NAME}; put it at "
                 f"{html.escape(str(data.get('expectationsPath', '')))} (a sandbox reset keeps it).</span></p>")
    return "".join(parts + details)


def _photo_key_matches(row, key):
    key = key.casefold()
    names = {pathlib.PurePosixPath(row[field]).name.casefold() for field in ("source", "destination")}
    stems = {pathlib.PurePosixPath(name).stem for name in names}
    return key == (row["photoId"] or "").casefold() or key in names or key in stems


def expectation_results(data):
    """Each expected photo placement against the actual destination: placed, in-review, elsewhere or missing."""
    results = []
    for key, expected in data.get("expectations", {}).get("photos", {}).items():
        matches = [row for row in data["rows"] if _photo_key_matches(row, key)]
        if not matches:
            results.append({"key": key, "expected": expected, "state": "missing", "row": None})
        for row in matches:
            if row["newPerson"] == expected:
                state = "placed" if row["newBucket"] == "gallery" else "in-review"
            else:
                state = "elsewhere"
            results.append({"key": key, "expected": expected, "state": state, "row": row})
    for person, expected in data.get("expectations", {}).get("identities", {}).items():
        if not expected.startswith(CAST):
            continue
        for row in data["rows"]:
            if row["newPerson"] == person:
                results.append({"key": person, "expected": expected, "state": "identity-not-merged", "row": row})
    return results


def _expectation_section(data, out_dir):
    results = expectation_results(data)
    parts = ["<h2 id=expected>Your expectations</h2>"]
    if not results:
        return "".join(parts + [
            f"<p class=muted>No expectations yet. Pick <b>Looks like</b> values below and save them, or write "
            f"{html.escape(str(data.get('expectationsPath', EXPECTATIONS_NAME)))} by hand, for example "
            '<code>{"photos": {"image_7518033450222312269": "Angels/seraphine"}}</code> (photo ID, file name or stem). '
            "Every later rebase recap then shows whether each photo landed where you expected.</p>"])
    counts = collections.Counter(item["state"] for item in results)
    parts.append("<p>" + ", ".join(f"{state} {count}" for state, count in counts.most_common()) + "</p>")
    for state in ("elsewhere", "identity-not-merged", "in-review", "missing", "placed"):
        group = [item for item in results if item["state"] == state]
        if not group:
            continue
        found = [item["row"] for item in group if item["row"]]
        parts.append(f"<details{' open' if state != 'placed' else ''}><summary>{state}: {len(group)}</summary>")
        missing = [item["key"] for item in group if not item["row"]]
        if missing:
            parts.append("<p>" + html.escape(", ".join(missing)) + "</p>")
        expected_by_row = {id(item["row"]): item["expected"] for item in group if item["row"]}
        parts.append(_cards(found, data, out_dir, lambda r: f"expected {expected_by_row[id(r)]}; got {r['newPerson']} "
                                                            f"({r['newBucket']}); {r['reason']}"))
        parts.append("</details>")
    return "".join(parts)


def compare_runs(data, other):
    """Placement differences among safely paired source paths or unique photo IDs."""
    pairs, _, _ = _comparison_rows(data, other)
    return [(mine, theirs) for mine, theirs in pairs
            if (mine["newPerson"], mine["newBucket"]) != (theirs["newPerson"], theirs["newBucket"])]


def _comparison_rows(data, other):
    mine, theirs = list(data["rows"]), list(other["rows"])
    pairs = []
    for field in ("source", "photoId"):
        mine_counts = collections.Counter(row.get(field) for row in mine)
        their_counts = collections.Counter(row.get(field) for row in theirs)
        lookup = {row.get(field): row for row in theirs if row.get(field) and their_counts[row.get(field)] == 1}
        matched_mine, matched_theirs = set(), set()
        for row in mine:
            key = row.get(field)
            if key and mine_counts[key] == 1 and key in lookup:
                counterpart = lookup[key]
                pairs.append((row, counterpart))
                matched_mine.add(id(row))
                matched_theirs.add(id(counterpart))
        mine = [row for row in mine if id(row) not in matched_mine]
        theirs = [row for row in theirs if id(row) not in matched_theirs]
    return pairs, mine, theirs


def _same_inputs(data, other):
    def signature(value):
        rows = value["rows"]
        if not rows or any(not row.get("source") or not row.get("sha256") for row in rows):
            return None
        return sorted((row["source"], row["sha256"]) for row in rows)
    first, second = signature(data), signature(other)
    return first is not None and first == second


def _comparison_section(data, others, out_dir):
    if not others:
        return ""
    parts = ["<h2 id=compare>Compared with other runs</h2>"]
    for other in others:
        differences = compare_runs(data, other)
        pairs, added, removed = _comparison_rows(data, other)
        changed_inputs = [(mine, theirs) for mine, theirs in pairs
                          if (mine["source"], mine.get("sha256")) != (theirs["source"], theirs.get("sha256"))]
        name = pathlib.Path(other["run"]).name
        parts.append(f"<h3>{html.escape(name)} ({html.escape(other['status'])}, cast seeds "
                     f"{html.escape(other['castSeedPolicy'])}): {len(differences)} photos placed differently</h3>")
        parts.append("<p>" + ("Identical inputs verified by photo source + sha256 signature."
                              if _same_inputs(data, other) else
                              "Partial source/photo-ID comparison: inputs differ or their byte signatures are "
                              "unavailable. A shared Source manifest does not verify identical working overlays.")
                     + f" {len(pairs)} paired; {len(added)} added in this run; {len(removed)} removed from this run; "
                     f"{len(changed_inputs)} paired source/byte signatures changed.</p>")
        for label, group in (("Added in this run", added), ("Removed from this run", removed)):
            if group:
                parts.append(f"<details><summary>{label}: {len(group)}</summary><ul>" + "".join(
                    f'<li>{html.escape(row["source"])} → {html.escape(row["destination"])}</li>' for row in group
                ) + "</ul></details>")
        if changed_inputs:
            parts.append("<details><summary>Changed paired inputs</summary><ul>" + "".join(
                f'<li>{html.escape(mine["source"])} [{html.escape(str(mine.get("sha256") or "unavailable"))}] '
                f'↔ {html.escape(theirs["source"])} [{html.escape(str(theirs.get("sha256") or "unavailable"))}]</li>'
                for mine, theirs in changed_inputs
            ) + "</ul></details>")
        if other.get("historical"):
            page = out_dir / _run_page_name(other)
            parts.append("<p>Preserved reset history: "
                         + _safe_link(page, "Historical recap (images unavailable)", out_dir, new_tab=True) + "</p>")
        flows = collections.Counter(
            (mine["newPerson"], mine["newBucket"], theirs["newPerson"], theirs["newBucket"])
            for mine, theirs in differences)
        parts.append("<table><tr><th>This run</th><th>" + html.escape(name) + "</th><th>Photos</th></tr>")
        parts.extend(
            f"<tr><td>{_person_link(a, data, out_dir, bucket=ab)} ({html.escape(ab)})</td>"
            f"<td>{_safe_link(out_dir / _run_page_name(other), b, out_dir, new_tab=True)}"
            f" ({html.escape(bb)})</td><td>{count}</td></tr>"
            for (a, ab, b, bb), count in flows.most_common(60))
        parts.append("</table>")
    return "".join(parts)


def _continuity_state(old_person, rows):
    destinations = {row["newPerson"] for row in rows}
    old_sources_by_target = collections.defaultdict(set)
    for row in rows:
        old_sources_by_target[row["newPerson"]].add(row["oldPerson"])
    states = []
    if len(destinations) > 1:
        states.append("split")
    merged_targets = sorted(person for person in destinations if len(old_sources_by_target[person]) > 1)
    if merged_targets:
        states.append("merged into " + ", ".join(merged_targets))
    if old_person not in destinations:
        if (len(destinations) == 1 and len(old_sources_by_target[next(iter(destinations))]) == 1
                and next(iter(destinations)) != old_person):
            states.append("one-to-one rename candidate (not ground truth)")
        else:
            states.append("emptied")
    if not states:
        states.append("name retained")
    return "; ".join(states)


def _continuity_section(data, out_dir):
    rows = data["rows"]
    old_counts = collections.Counter(row["oldPerson"] for row in rows)
    final_gallery = collections.Counter(row["newPerson"] for row in rows if row["newBucket"] == "gallery")
    final_review = collections.Counter(row["newPerson"] for row in rows if row["newBucket"] == "review")
    outgoing = collections.defaultdict(list)
    for row in rows:
        outgoing[row["oldPerson"]].append(row)
    flows = collections.defaultdict(list)
    for row in rows:
        flows[(row["oldPerson"], row["newPerson"], row["newBucket"])].append(row)
    parts = [
        "<h2 id=continuity>Identity membership and name continuity</h2>",
        f"<p>{len(rows)} source photo rows → {sum(final_gallery.values())} final Gallery + "
        f"{sum(final_review.values())} final Review = {len(rows)} accounted destinations. Counts are row counts, "
        "not verified identities. Saved reason text is evidence, not a continuity verdict.</p>",
        "<table><tr><th>Old identity</th><th>Old rows</th><th>Retained in Gallery</th><th>Arrivals</th>"
        "<th>Departures</th><th>Final Gallery</th><th>Final Review</th><th>Observed name flow</th></tr>",
    ]
    for person in sorted(old_counts, key=str.casefold):
        source_rows = outgoing[person]
        retained = sum(r["oldPerson"] == person and r["newPerson"] == person and r["newBucket"] == "gallery"
                       for r in rows)
        arrivals = sum(r["newPerson"] == person and r["oldPerson"] != person and r["newBucket"] == "gallery"
                       for r in rows)
        departures = sum(r["oldPerson"] == person and (r["newPerson"] != person or r["newBucket"] == "review")
                         for r in rows)
        parts.append(
            f'<tr id="{_anchor("continuity", person)}"><td>{_person_link(person, data, out_dir)}'
            + ("<br>Final destinations: " + ", ".join(
                _person_link(target, data, out_dir) for target in sorted({r["newPerson"] for r in source_rows})
            ) if not final_gallery[person] and not final_review[person] else "")
            + "</td>"
            f"<td>{old_counts[person]}</td><td>{retained}</td>"
            f"<td>{arrivals}</td><td>{departures}</td><td>{final_gallery[person]}</td>"
            f"<td>{final_review[person]}</td><td>{html.escape(_continuity_state(person, source_rows))}</td></tr>"
        )
    parts.append("</table><h3>Old identity → final destination counts</h3>"
                 "<table><tr><th>Old identity</th><th>Final identity / bucket</th><th>Photos</th>"
                 "<th>Saved reasons and destination links</th></tr>")
    for (old, new, bucket), group in sorted(flows.items(), key=lambda item: (-len(item[1]), item[0])):
        reasons = collections.Counter(row["reason"].split(";")[0] for row in group)
        reason_text = "; ".join(f"{html.escape(reason)} ({count})" for reason, count in reasons.most_common())
        links = _destination_links(group[0], data, out_dir)
        parts.append(f"<tr><td>{_person_link(old, data, out_dir)}</td>"
                     f"<td>{_person_link(new, data, out_dir, bucket=bucket)} ({html.escape(bucket)})</td>"
                     f"<td>{len(group)}</td><td>{reason_text}<br>{links}</td></tr>")
    parts.append("</table>")
    if data["emptiedIdentities"]:
        parts.append("<h3>Empty final identities</h3><ul>"
                     + "".join(f"<li>{_person_link(person, data, out_dir)} — no rows now land in this identity.</li>"
                               for person in data["emptiedIdentities"]) + "</ul>")
    return "".join(parts)


def _refinement_section(data):
    evidence = data.get("membershipRefinement")
    parts = ["<h2 id=refinement>Bounded refinement (photo moves and identity merges)</h2>"]
    if not isinstance(evidence, dict):
        return "".join(parts + ["<p class=muted>Unavailable in this run: no membershipRefinement was saved; "
                                "this run predates in-place refinement.</p>"])
    esc = lambda value: html.escape(str(value))
    parts.append(
        f"<p>{esc(evidence.get('passCount'))} pass(es) of at most {esc(evidence.get('maxPasses'))}; "
        f"stop reason <b>{esc(evidence.get('stopReason'))}</b>; {esc(evidence.get('moveCount'))} photo move(s), "
        f"{esc(evidence.get('mergeCount'))} identity merge(s), {esc(evidence.get('dissolvedCount', 0))} dissolved; "
        f"{len(evidence.get('unresolved', []))} unresolved. References are frozen per pass; merged identities "
        "choose the oldest recorded original name afterwards.</p>"
    )
    for item in evidence.get("passes", []):
        rows = [
            (move.get("kind"), move.get("photoId", ""), move.get("from"), move.get("to"),
             f"own {_score_text(move.get('ownScore'))}, rival {_score_text(move.get('rivalScore'))}, "
             f"lead {_score_text(move.get('lead'))}")
            for move in item.get("moves", [])
        ] + [
            ("identity-merge", f"{merge.get('photoCount')} photo(s)", merge.get("loser"), merge.get("survivor"),
             f"similarity {_score_text(merge.get('similarity'))}, lead {_score_text(merge.get('lead'))}")
            for merge in item.get("merges", [])
        ] + [
            ("identity-dissolved", "", entry.get("folder"), "Review", entry.get("reason"))
            for entry in item.get("dissolved", [])
        ] + [
            ("reclassified", "", entry.get("from"), entry.get("to"), "")
            for entry in item.get("reclassified", [])
        ]
        parts.append(f"<h3>Pass {esc(item.get('pass'))}: {len(rows)} change(s)</h3>")
        if rows:
            parts.append("<table><tr><th>Kind</th><th>Photo</th><th>From</th><th>To</th><th>Evidence</th></tr>"
                         + "".join("<tr>" + "".join(f"<td>{esc(value)}</td>" for value in row) + "</tr>"
                                   for row in rows) + "</table>")
    unresolved = evidence.get("unresolved", [])
    if unresolved:
        parts.append("<h3>Unresolved (left in place for review)</h3><table><tr><th>Pass</th><th>Kind</th>"
                     "<th>Subject</th><th>Detail</th></tr>" + "".join(
                         f"<tr><td>{esc(row.get('pass'))}</td><td>{esc(row.get('kind'))}</td>"
                         f"<td>{esc(row.get('photoId') or (str(row.get('loser')) + ' -> ' + str(row.get('survivor'))))}</td>"
                         f"<td>{esc(row.get('detail'))}</td></tr>" for row in unresolved) + "</table>")
    final = data.get("finalMembershipRefinement")
    if isinstance(final, dict):
        parts.append(
            "<h3>Audit-aligned final-membership refinement</h3>"
            f"<p>{esc(final['passCount'])} pass(es); stop reason <b>{esc(final['stopReason'])}</b>; "
            f"{esc(final['moveCount'])} photo move(s). No new protection is acquired during these "
            "comparisons. Stable means no further admitted moves, not zero higher rivals.</p>"
            "<details><summary>Final-membership moves and residual hold reasons</summary><pre>"
            + html.escape(json.dumps(final, indent=2, sort_keys=True)) + "</pre></details>"
        )
    else:
        parts.append("<p class=muted>No audit-aligned final-membership refinement was saved in this run.</p>")
    return "".join(parts)


def _family_members(data):
    evidence = data.get("familyNaming")
    lookup = {}
    for family in (evidence or {}).get("families", []) if isinstance(evidence, dict) else []:
        for member in family.get("members", []):
            if member.get("folder"):
                lookup[member["folder"]] = {**member, "surname": family.get("surname")}
    return lookup


def _family_section(data, out_dir=None):
    evidence = data.get("familyNaming")
    parts = ["<h2 id=families>Families (score-band family tree)</h2>"]
    if not isinstance(evidence, dict):
        return "".join(parts + ["<p class=muted>Unavailable in this run: no familyNaming was saved; this run "
                                "predates score-band family naming.</p>"])
    esc = lambda value: html.escape(str(value))
    if ("directCastMinimumSimilarity" in evidence
            or "secondaryMinimumSimilarityExclusive" in evidence):
        thresholds = (
            "Direct-cast minimum similarity "
            f"&ge; {_score(evidence.get('directCastMinimumSimilarity'))}; "
            + ("secondary minimum similarity "
               f"&gt; {_score(evidence.get('secondaryMinimumSimilarityExclusive'))}"
               if evidence.get("secondarySurnameLinksEnabled", True)
               else "secondary surname links disabled (direct cast only)")
        )
    else:
        thresholds = (f"Link band <b>{esc(evidence.get('linkBand'))}</b> "
                      f"(score at least {_score(evidence.get('linkMinimum'))})")
    parts.append(
        f"<p>{thresholds}; "
        f"{len(evidence.get('families', []))} families, {esc(evidence.get('linkedIdentityCount'))} linked identities, "
        f"{esc(evidence.get('renamedIdentityCount'))} surname change(s), "
        f"{esc(evidence.get('displacedFamilyCount', 0))} given a fresh surname because theirs belongs to another family, "
        f"{esc(evidence.get('unlinkedIdentityCount'))} unlinked. {esc(evidence.get('rule'))}</p>"
    )
    for family in sorted(evidence.get("families", []),
                         key=lambda item: (item.get("rootKind") != "cast", -len(item.get("members", [])),
                                           str(item.get("rootFolder")))):
        cast = (evidence.get("cast") or {}).get(family.get("root"), {})
        person_link = lambda person: _person_link(person, data, out_dir) if out_dir is not None else esc(person)
        heading = (f"{person_link(family.get('rootFolder'))}: {esc(family.get('surname'))}"
                   f" <span class=muted>({esc(family.get('surnameSource'))}; "
                   f"{len(family.get('members', []))} member(s))</span>")
        parts.append(f"<h3>{heading}</h3>")
        if family.get("displacedFrom"):
            parts.append(f"<p>Surname {esc(family['displacedFrom'].get('surname'))} belongs to the family of "
                         f"{person_link(family['displacedFrom'].get('owner'))}, so this unrelated identity gets "
                         f"<b>{esc(family.get('surname'))}</b>.</p>")
        if cast:
            parts.append(f"<p>Cast person name: {esc(cast.get('recordedPersonName') or 'not recorded')} &rarr; "
                         f"<b>{esc(cast.get('currentPersonName'))}</b></p>")
        if family.get("members"):
            parts.append(
                "<table><tr><th>Identity</th><th>Status</th><th>Linked to</th><th>Score</th><th>Path to root</th></tr>"
                + "".join(
                    f"<tr><td>{person_link(member.get('folder'))}"
                    + (f"<br><span class=muted>was {esc(member.get('previousName'))}</span>"
                       if str(member.get("status", "")).startswith("renamed") else "")
                    + f"</td><td>{esc(member.get('status'))}</td>"
                    f"<td>{person_link(member.get('parentFolder') or 'root')} <span class=muted>{esc(member.get('tier'))}</span></td>"
                    f"<td>{_score(member['score']) + ' ' + esc(member.get('band')) if member.get('score') is not None else '-'}</td>"
                    f"<td>{' &rarr; '.join(person_link(step.get('toFolder')) + ' ' + _score(step.get('score')) for step in member.get('path', [])) or '-'}</td></tr>"
                    for member in family["members"]
                ) + "</table>"
            )
            if out_dir is not None and not data.get("historical"):
                people = list(dict.fromkeys([family.get("rootFolder"),
                                             *(m.get("folder") for m in family["members"])]))
                parts.append('<details class=family-comparison><summary>Compare family members: up to five '
                             'saved photos each</summary><p class=muted>Deterministic Gallery samples, '
                             'then Review if no Gallery exists; not a measured core ranking or identity verdict.</p>'
                             '<template class=family-samples>')
                for person in people:
                    if not person:
                        continue
                    members = [r for r in data["rows"] if r["newPerson"] == person]
                    gallery = [r for r in members if r["newBucket"] == "gallery"]
                    sample = sorted(gallery or members, key=lambda r: r["source"])[:5]
                    parts.append(f"<div class=family-member><h4>{person_link(person)}</h4>"
                                 + ('<div class=grid>' + "".join(_thumb(r, data, out_dir) for r in sample) + "</div>"
                                    if sample else '<p class=muted>No saved member photos available.</p>')
                                 + "</div>")
                parts.append("</template></details>")
    return "".join(parts)


def _audit_section(data, out_dir):
    audit = data.get("finalMembershipAudit")
    parts = ["<h2 id=audit>Final own-versus-rival membership audit</h2>"]
    if not isinstance(audit, dict):
        return "".join(parts + [
            "<p class=muted>Unavailable in this run: no finalMembershipAudit was saved. "
            "Reassignment/convergence status is not inferred.</p>",
        ])
    summary = audit.get("summary") if isinstance(audit.get("summary"), dict) else {}
    passed = summary.get("passed", audit.get("passed"))
    state = summary.get("status", summary.get("state", audit.get("status", audit.get("state"))))
    if passed is not None:
        state = "passed" if passed else "failed"
    reassignment = audit.get("reassignmentStatus", data.get("reassignmentStatus")) or "not recorded"
    convergence = audit.get("convergenceStatus", data.get("convergenceStatus")) or "not recorded"
    parts.append(f"<p>Audit state: <b>{html.escape(str(state or 'recorded; result not stated'))}</b>. "
                 f"Reassignment: {html.escape(str(reassignment))}; "
                 f"convergence: {html.escape(str(convergence))}.</p>")
    if audit.get("state") == "audited" and audit.get("automaticMoves") == 0:
        parts.append("<p><b>The audit itself is read-only; it performs no extra moves.</b> "
                     "Recorded refinement passes above are separate. Higher-rival and follow-up "
                     "candidates are diagnostics, not completed reassignments.</p>")
    audit_rows = [item for item in audit.get("rows", []) if isinstance(item, dict)]
    decisions = [row.get("refinementDecision") for row in audit_rows]
    if decisions and all(isinstance(item, dict) and item.get("decision") in {"hold", "move"}
                         for item in decisions):
        eligible = sum(item["decision"] == "move" for item in decisions)
        holds = collections.Counter(
            row.get("refinementHoldReason") or row["refinementDecision"].get("reason") or "reason not recorded"
            for row in audit_rows if row.get("followupCandidate")
            and row["refinementDecision"]["decision"] == "hold"
        )
        parts.append(f"<p><b>Eligible automatic moves remaining: {eligible}.</b> "
                     "This is the saved final evaluator result, not a fresh re-evaluation under changed policy. "
                     "A higher rival alone does not pass quality, protection, admission and margin gates.</p>")
        if holds:
            parts.append("<p>Blocked follow-ups (not missed automatic moves):</p><ul>" + "".join(
                f"<li>{html.escape(str(reason))}: {count}</li>" for reason, count in sorted(holds.items())
            ) + "</ul>")
    else:
        parts.append("<p class=muted>Eligible automatic moves remaining: unavailable; "
                     "this run did not save a complete per-photo refinement decision set.</p>")
    if "nextPassNeeded" in audit:
        parts.append("<p class=muted>Legacy <code>nextPassNeeded</code> records review/follow-up evidence "
                     "or pending continuity work; it does not by itself mean another automatic pass can move "
                     "these photos. The saved field is preserved below.</p>")
    if any("higherRival" in item or "followupCandidate" in item for item in audit_rows):
        higher = sum(item.get("higherRival") is True for item in audit_rows)
        followup_only = sum(
            item.get("followupCandidate") is True and item.get("higherRival") is not True
            for item in audit_rows
        )
        parts.append(
            f"<p>Per-photo audit flags: {higher} photo(s) with a higher rival; "
            f"{followup_only} additional follow-up-only photo(s), not counted above. "
            "These disjoint counts describe review signals, not moves.</p>"
        )
    else:
        parts.append("<p class=muted>Disjoint higher-rival and follow-up-only counts unavailable: "
                     "per-photo flags were not recorded.</p>")
    fields = (
        "reference", "pass", "state", "higherRivalCount", "followupCandidateCount", "nextPassNeeded",
        "automaticMoves", "automaticMerges", "refinementPasses", "refinementStopReason",
        "automaticPhotoProtectionCount", "automaticIdentityProtectionCount",
        "finalRefinementPasses", "finalRefinementMoves", "finalRefinementStopReason",
        "postContinuityPendingCount",
    )
    parts.append("<ul>" + "".join(
        f"<li>{field}: {html.escape(str(audit[field]))}</li>" for field in fields if field in audit
    ) + "</ul>")
    for field in ("protectionEvidence", "diagnostics"):
        if field in audit:
            parts.append(f"<details><summary>{field}</summary><pre>"
                         f"{html.escape(json.dumps(audit[field], indent=2, sort_keys=True))}</pre></details>")
    if summary:
        parts.append("<ul>" + "".join(f"<li>{html.escape(str(key))}: {html.escape(str(value))}</li>"
                                       for key, value in sorted(summary.items())) + "</ul>")
    plan_rows = {row["source"]: row for row in data["rows"]}
    if not audit_rows:
        parts.append("<p class=muted>No per-photo audit rows were saved.</p>")
        return "".join(parts)
    parts.append("<p class=muted>FINAL photo-to-cast references compare each photo against frozen FINAL cast cores. "
                 "Own-cast comparisons use leave-one-out ownScore; singleton own scores remain unavailable. "
                 "These are separate from initial group scores and rivals across all categories.</p>"
                 "<table><tr><th>Source</th><th>Final destination</th><th>Own score</th><th>Rivals (all categories)</th>"
                 "<th>FINAL photo-to-cast references</th>"
                 "<th>Higher rival?</th><th>Protection / follow-up</th><th>Reason</th></tr>")
    for item in audit_rows:
        if not isinstance(item, dict):
            continue
        source = str(item.get("source", ""))
        row = plan_rows.get(source)
        destination = str(item.get("destination", row["destination"] if row else ""))
        source_link = _source_link(source, row, data, out_dir)
        new_person, new_bucket = person_and_bucket(destination)
        final_links = _destination_links(
            {
                "destination": destination, "newPerson": new_person, "newBucket": new_bucket,
                "sha256": row.get("sha256") if row else None,
                "preparedSHA256": row.get("preparedSHA256") if row else item.get("preparedSHA256"),
            },
            data,
            out_dir,
        ) if destination else "unavailable"
        rivals = item.get("rivals", [])
        rival_text = ", ".join(
            f"{_person_link(rival.get('folder', ''), data, out_dir)}: {_score_text(rival.get('score'))}"
            for rival in rivals if isinstance(rival, dict)
        ) or "none recorded"
        parts.append(
            f"<tr><td>{source_link}<br>{html.escape(source)}</td><td>{final_links}</td>"
            f"<td>{_score_text(item.get('ownScore'))}</td><td>{rival_text}</td>"
            f"<td>{_cast_reference_table(item.get('castReferences'), data, out_dir)}</td>"
            f"<td>{html.escape(str(item.get('higherRival', 'not recorded')))}</td>"
            "<td>" + "<br>".join(
                f"{field}: {html.escape(str(item.get(field, 'not recorded')))}"
                for field in ("protected", "anchor", "workflowSelected", "followupCandidate", "coreMember",
                              "automaticProtection", "manualOptOut", "rivalMargin",
                              "independentProtectionSupport", "protectionReason", "refinementHoldReason")
            ) + "</td>"
            f"<td>{html.escape(str(item.get('reason', '')))}</td></tr>"
        )
    parts.append("</table>")
    return "".join(parts)


def _review_section(data, out_dir):
    rows = [row for row in data["rows"] if row["newBucket"] == "review"]
    reasons = collections.defaultdict(list)
    for row in rows:
        reasons[row["reason"].split(";")[0]].append(row)
    parts = [f"<h2 id=review>Review holds ({len(rows)})</h2>"]
    if any("2+ faces" in row["reason"] for row in rows):
        parts.append(MULTIFACE_NOTE)
    for reason, group in sorted(reasons.items(), key=lambda item: -len(item[1])):
        parts.append(
            f"<details><summary>{html.escape(reason)}: {len(group)}</summary>"
            f"{_cards(group, data, out_dir, lambda r: f'{r['newPerson']} ({r['newBucket']}); was {r['oldPerson']}; {r['reason']}')}"
            "</details>")
    return "".join(parts)


def _flow_section(data, out_dir):
    flows = collections.Counter((row["oldPerson"], row["newPerson"], row["newBucket"])
                                for row in data["rows"] if row["kind"] != "stayed")
    parts = ["<h2 id=flows>Where photos went</h2><table><tr><th>From</th><th>To</th><th>Count</th></tr>"]
    for (old, new, bucket), count in flows.most_common():
        target = _person_link(new, data, out_dir, bucket=bucket) + (" (review)" if bucket == "review" else "")
        parts.append(f"<tr><td>{_person_link(old, data, out_dir)}</td><td>{target}</td><td>{count}</td></tr>")
    parts.append("</table>")
    if data["emptiedIdentities"]:
        parts.append("<h3>Identities emptied by the rebase</h3><ul>"
                     + "".join(f"<li>{_person_link(p, data, out_dir)}</li>"
                               for p in data["emptiedIdentities"]) + "</ul>")
    return "".join(parts)


def _all_rows(data, out_dir):
    final_cast = _final_cast_by_source(data)
    parts = ["<h2 id=all>Every photo</h2>"
             "<p class=muted>Saved <code>bestScore</code> is the planned group-to-frozen-core match score; "
             "<code>initialBestCastScore</code> is an INITIAL per-photo comparison. Recorded audit "
             "<code>castReferences</code> are FINAL photo-to-cast comparisons against frozen FINAL cores, "
             "including leave-one-out own-cast scores (singleton own scores unavailable). "
             "They are different evidence. Missing values are explicitly unmeasured/unavailable.</p>"
             "<p><input id=filter placeholder='Filter: name, person, reason...' size=50> "
             "<label><input type=checkbox id=changed checked> changed only</label></p>",
             "<table id=photos><tr><th>Photo</th><th>Change state</th><th>Before</th><th>Final destination</th>"
             "<th>Group size</th><th>Group-to-core score</th><th>Top three per-photo cast references</th>"
             "<th>Saved reason</th></tr>"]
    if any("2+ faces" in row["reason"] for row in data["rows"]):
        parts.insert(1, MULTIFACE_NOTE)
    for row in sorted(data["rows"], key=lambda r: (r["kind"] == "stayed", r["oldPerson"], r["source"])):
        distinctions = [row["placementKind"]]
        if row["renamed"] and "Rename" not in distinctions[0]:
            distinctions.append("filename renamed")
        if row["converted"]:
            distinctions.append("format converted")
        is_final = row["source"] in final_cast
        top = final_cast[row["source"]] if is_final else row["topCast"]
        refs = ("<b>FINAL photo-to-cast references</b>" if is_final else
                "<b>INITIAL per-photo cast references</b><p class=muted>FINAL references unavailable in this run.</p>")
        refs += _cast_reference_table(top, data, out_dir)
        if top and len(top) < 3:
            refs += '<p class=muted>Remaining cast references unavailable (only partial ranking saved).</p>'
        group_size = str(row["groupSize"]) if row["groupSize"] is not None else "unavailable (not recorded)"
        detail = f'<br>{_safe_link(row["detail"], "intake", out_dir, new_tab=True)}' if row["detail"] else ""
        parts.append(
            f'<tr data-kind="{row["kind"]}"><td class=t>{_thumb(row, data, out_dir)}{detail}</td>'
            f'<td>{html.escape("; ".join(distinctions))}</td>'
            f'<td>{_person_link(row["oldPerson"], data, out_dir)}<br>{html.escape(row["source"])}</td>'
            f'<td>{_person_link(row["newPerson"], data, out_dir, bucket=row["newBucket"])}'
            f'<br>{html.escape(row["destination"])}<br>{_destination_links(row, data, out_dir)}</td>'
            f'<td>{html.escape(group_size)}</td><td>{_score_text(row["bestScore"])}</td>'
            f'<td>{refs}</td><td>{html.escape(row["reason"])}</td></tr>')
    parts.append("</table>")
    return "".join(parts)


STYLE = """.recap-content{max-width:1680px;margin:auto;padding:18px 24px 8px}
.recap-content>section{margin:12px 0;padding:16px 20px;background:var(--st-card);border:1px solid var(--st-line);
border-radius:var(--st-radius);box-shadow:var(--st-shadow);overflow:auto}
table{border-collapse:collapse;width:100%;margin:8px 0}td,th{border:1px solid var(--st-line);padding:6px 8px;
font-size:13px;vertical-align:top;text-align:left}th{background:var(--st-accent-soft);position:sticky;top:0;z-index:1}
.muted{color:var(--st-muted)}.warn{background:#fde2e2}.grid{display:flex;flex-wrap:wrap;gap:8px}
figure{margin:0;width:160px;font-size:12px;overflow-wrap:anywhere}figure img{width:150px;height:150px;
object-fit:cover;border:1px solid var(--st-line);border-radius:6px}
.family-member{margin:12px 0}.family-member img{width:110px;height:130px;object-fit:cover;border-radius:6px}
td.t img{width:80px;height:94px;object-fit:cover;border:1px solid var(--st-line)}
details{margin:8px 0;padding:8px 12px;border:1px solid var(--st-line);border-radius:var(--st-radius);background:var(--st-card)}
summary{cursor:pointer;margin:4px 0;font-weight:600}.cards{display:flex;gap:10px;flex-wrap:wrap}
.summary-cards>div{border:1px solid var(--st-line);padding:8px 12px;border-radius:var(--st-radius);background:var(--st-card)}
.summary-cards b{font-size:20px;display:block}.person-nav{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
.person-nav a,.destination-links a{display:inline-block;margin:2px}.paired-images{display:flex;gap:8px;min-width:280px}
.paired-images>div{display:flex;flex-direction:column;gap:3px;max-width:130px}.paired-images img{width:110px;height:110px;
object-fit:cover;border:1px solid var(--st-line);border-radius:6px}.paired-images small{overflow-wrap:anywhere}
ol{margin:0;padding-left:22px}.score-badge{white-space:nowrap}#photos td{min-width:120px}
@media(max-width:760px){.recap-content{padding:10px}.recap-content>section{padding:12px}}
"""

SCRIPT = """const f=document.getElementById('filter'),c=document.getElementById('changed');
function apply(){const q=f.value.toLowerCase();for(const r of document.querySelectorAll('#photos tr[data-kind]')){
r.style.display=(c.checked&&r.dataset.kind==='stayed')||(q&&!r.textContent.toLowerCase().includes(q))?'none':''}}
f.addEventListener('input',apply);c.addEventListener('change',apply);apply();
function filterCast(){const selected=location.hash.slice(1);const links=[...document.querySelectorAll('[data-cast-filter]')];
const active=links.find(a=>a.dataset.castFilter!=='all'&&a.dataset.castFilter===selected);
for(const d of document.querySelectorAll('details[id^="cast-"]')){d.hidden=!!active&&d.id!==active.dataset.castFilter;
if(active&&d.id===active.dataset.castFilter)d.open=true}}
function openTarget(){filterCast();const id=location.hash.slice(1);
const target=document.getElementById(id);if(!target)return;
for(let node=target;node;node=node.parentElement){if(node.tagName==='DETAILS')node.open=true}
if(target.tagName==='DETAILS')target.open=true;
requestAnimationFrame(()=>target.scrollIntoView({block:'start',behavior:'instant'}))}
window.addEventListener('hashchange',openTarget);openTarget();
window.addEventListener('load',openTarget,{once:true});
for(const panel of document.querySelectorAll('details.family-comparison')){
panel.addEventListener('toggle',()=>{const template=panel.querySelector('template.family-samples');
if(panel.open&&template){panel.append(template.content.cloneNode(true));template.remove()}})}
const saved=__EXPECTATIONS__;
document.getElementById('save-picks').addEventListener('click',()=>{
const identities={...(saved.identities||{})};
for(const s of document.querySelectorAll('select.pick')){if(s.value)identities[s.dataset.identity]=s.value;else delete identities[s.dataset.identity]}
const body=JSON.stringify({identities,photos:saved.photos||{}},null,2);
const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([body],{type:'application/json'}));
a.download='rebase-expectations.json';a.click()});"""


def _alias_section(data, out_dir):
    aliases = data.get("incomingAliases", [])
    if not aliases:
        return ""
    rows = []
    for alias in aliases:
        destination = _working_target(alias["destination"], data)
        link = (_safe_link(destination, alias["destination"], out_dir, new_tab=True)
                if destination else html.escape(alias["destination"]))
        rows.append(f"<tr><td>{html.escape(alias['arrival'])}</td>"
                    f"<td>{html.escape(alias['canonical'])}</td><td>{link}</td></tr>")
    return (f'<h2 id="aliases">Exact incoming aliases: {len(aliases)}</h2>'
            "<p>These additional arrivals share verified input bytes. They do not add preparation or "
            "matching votes; their canonical photo and its destination account for them.</p>"
            "<table><thead><tr><th>Duplicate arrival</th><th>Canonical input</th><th>Destination</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


def render(data, out_path, others=()):
    data = {key: value for key, value in data.items()
            if key not in {"_person_path_validity", "_person_folders", "_old_person_folders", "_review_page"}}
    out_dir = pathlib.Path(out_path).parent
    summary = summarize(data)
    work = pathlib.Path(data["workingRoot"])
    library = work / "_reports" / "library"
    links = [(library / "people_gallery.html", "People gallery (Overview)"),
             (library / "people_gallery_review.html", "Review gallery"),
             (library / "intake_runs.html", "Intake history"),
             (pathlib.Path(data["run"]) / "report.md", "Run report"),
             (pathlib.Path(data["run"]) / "photos.csv", "photos.csv"),
             (out_dir / "index.html", "All rebase runs")]
    if data["preparationIndex"]:
        links.insert(2, (pathlib.Path(data["preparationIndex"]), "Intake comparisons"))
    if data.get("historical"):
        links = [(pathlib.Path(data["run"]) / "run.json", "Preserved run.json"),
                 (out_dir / "index.html", "All rebase runs")]
    kinds = summary["kinds"]
    applied = data["status"] == "applied"
    cards = [("Photos", summary["photos"]), ("Stayed", kinds.get("stayed", 0)),
             ("Moved between people", kinds.get("moved", 0) + kinds.get("moved-to-review", 0)),
             ("Gallery to Review", kinds.get("to-review", 0) + kinds.get("moved-to-review", 0)),
             ("Review to Gallery", kinds.get("from-review", 0)), ("Renamed", summary["renamed"]),
             ("Path changed", kinds.get("path-changed", 0)), ("Converted format", summary["converted"]),
             ("New identities", summary["newIdentities"]),
             ("Emptied identities", summary["emptiedIdentities"])]
    body = [
        f'<section class=page-header><div><h1>Sandbox rebase recap: {html.escape(pathlib.Path(data["run"]).name)}</h1>',
        f"<p>Status <b>{html.escape(data['status'])}</b>{'' if applied else ' (planned; nothing applied yet)'}; "
        f"policy {html.escape(str(data['policy']))}; cast seeds {html.escape(str(data['castSeedPolicy']))}; "
        f"plan created {html.escape(str(data['createdAt']))}. The page is deterministic for this saved run.</p></div>",
        '<div class=header-side><span class=header-label>Saved plan evidence</span></div></section>',
        "<section><p><b>Historical reset evidence.</b> These placements describe the prior run, not current "
        "membership. Compact evidence preserves no intake or photo files; historical image/gallery links "
        "are unavailable. This evidence is not matching input or cast seeds.</p></section>"
        if data.get("historical") else "",
        '<section class=summary-cards><div class=cards>'
        + "".join(f"<div><b>{value}</b>{html.escape(label)}</div>" for label, value in cards) + "</div>"
        + f'<p class=muted>Count conservation: {summary["sourcePhotos"]} source rows → '
        f'{summary["finalPhotos"]} final destinations; {"verified" if summary["countConserved"] else "not conserved"}.</p>'
        + "</section>",
        '<section><h2>Run and report links</h2><nav class="person-nav" aria-label="Related run pages">'
        + "".join(_safe_link(path, label, out_dir, new_tab=True) if path == out_dir / "index.html" or path.is_file()
                  else f'<span class=muted>{html.escape(label)} unavailable</span>'
                  for path, label in links) + "</nav>"
        + ("<p class=muted>Historical run.json is preserved evidence only; no historical photo or intake links "
           "are offered and this reset-history copy cannot be used to undo.</p></section>"
           if data.get("historical") else
           "<p class=muted>Thumbnails show the prepared intake image when saved; the final-photo and report links "
           "open in new tabs. "
           + ("Disposable sandbox: no undo; recover by full sandbox reset."
              if data.get("recoveryMode") == "disposable"
              else "Undo only through sandbox-rebase.cmd ... --undo.")
           + "</p></section>"),
        '<section><h2>Recap sections</h2>'
        + gallery_chrome.navigation([
            ("Expectations", "#expected"), ("Where photos went", "#flows"), ("Identity continuity", "#continuity"),
            ("Angels and Sisters", "#cast"), ("Other identities", "#identities"), ("Families", "#families"),
            ("Review holds", "#review"),
            *([("Incoming aliases", "#aliases")] if data.get("incomingAliases") else []),
            ("Refinement", "#refinement"), ("Final audit", "#audit"), *(([("Other runs", "#compare")] if others else [])), ("Every photo", "#all"),
        ], "Sandbox rebase recap") + "</section>",
        f"<section>{_expectation_section(data, out_dir)}</section>",
        f"<section>{_flow_section(data, out_dir)}</section>",
        f"<section>{_alias_section(data, out_dir)}</section>" if data.get("incomingAliases") else "",
        f"<section>{_continuity_section(data, out_dir)}</section>",
        f"<section>{_cast_section(data, out_dir)}</section>",
        f"<section>{_identity_section(data, out_dir)}</section>",
        f"<section>{_family_section(data, out_dir)}</section>",
        f"<section>{_review_section(data, out_dir)}</section>",
        f"<section>{_refinement_section(data)}</section>",
        f"<section>{_audit_section(data, out_dir)}</section>",
        f"<section>{_comparison_section(data, others, out_dir)}</section>" if others else "",
        f"<section>{_all_rows(data, out_dir)}</section>",
    ]
    script = SCRIPT.replace("__EXPECTATIONS__", json.dumps(data.get("expectations", {})).replace("</", "<\\/"))
    prefix = "../../"
    masthead = gallery_chrome.masthead(tagline="Sandbox rebase recap", prefix=prefix)
    return ("<!doctype html><html><head><meta charset=utf-8><title>Sandbox rebase recap</title>"
            f"<style>{gallery_chrome.CSS}{STYLE}</style></head><body id=top>{masthead}"
            f'<main class=recap-content>{"".join(body)}{gallery_chrome.footer("Saved run evidence only · No new intake or identity decision")}'
            f"</main><script>{script}</script></body></html>")


def expectations_path(data):
    """Beside Working, so a full sandbox reset (which replaces Working) keeps the user's judgements."""
    return pathlib.Path(data["workingRoot"]).parent / EXPECTATIONS_NAME


def load_expectations(path):
    path = pathlib.Path(path)
    if not path.is_file():
        return {"identities": {}, "photos": {}}
    raw = json.loads(path.read_text(encoding="utf-8"))
    for section in ("identities", "photos"):
        if not isinstance(raw.get(section, {}), dict):
            raise ValueError(f"{path}: '{section}' must map names to a person folder")
    return {"identities": dict(raw.get("identities", {})), "photos": dict(raw.get("photos", {}))}


def recap_dir(data):
    return pathlib.Path(data["workingRoot"]) / "_reports" / "library" / OUT_DIR


def default_out(data):
    return recap_dir(data) / _run_page_name(data)


def _run_page_name(data):
    name = pathlib.Path(data["run"]).name
    return f"history-{name}-{hashlib.sha256(name.encode()).hexdigest()[:12]}.html" if data.get("historical") else f"{name}.html"


def sibling_runs(run, working_root=None):
    """Discover live sibling runs and compact reset history, never matching inputs."""
    run = pathlib.Path(run)
    candidates = set(run.parent.iterdir())
    if working_root is not None:
        work = pathlib.Path(working_root)
        for directory in (work / "_sandbox-state", work.joinpath(*HISTORY_PARTS)):
            if directory.is_dir():
                candidates.update(directory.iterdir())
    return sorted(path for path in candidates
                  if path != run and path.is_dir() and not path.is_symlink() and (path / "run.json").is_file())


def render_index(entries, out_dir):
    rows = "".join(
        f'<tr><td><a href="{_href(page, out_dir)}">{html.escape(name)}</a></td><td>{html.escape(status)}</td>'
        f"<td>{html.escape(seeds)}</td><td>{html.escape(str(created))}</td><td>{summary['photos']}</td>"
        f"<td>{summary['photos'] - summary['kinds'].get('stayed', 0)}</td><td>{summary['review']}</td>"
        f"<td>{summary['newIdentities']}</td></tr>"
        for name, status, seeds, created, summary, page in entries)
    return ("<!doctype html><html><head><meta charset=utf-8><title>Sandbox rebase runs</title>"
            f"<style>{gallery_chrome.CSS}{STYLE}</style></head><body id=top>"
            f'{gallery_chrome.masthead(tagline="Sandbox rebase runs", prefix="../../")}'
            '<main class=recap-content><section><h1>Sandbox rebase runs</h1>'
            "<p class=muted>Regenerated by every sandbox-rebase.cmd preview, replan, apply, check or undo.</p>"
            "<table><tr><th>Run</th><th>Status</th><th>Cast seeds</th><th>Plan created</th><th>Photos</th>"
            f"<th>Changed</th><th>In Review</th><th>New identities</th></tr>{rows}</table></section>"
            f'{gallery_chrome.footer("Saved run summaries · No new intake or identity decision")}</main></body></html>')


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", help="the sandbox run directory holding run.json")
    parser.add_argument("--out", help=f"HTML file (default: WORKING\\_reports\\library\\{OUT_DIR}\\RUN.html)")
    parser.add_argument("--expectations", help=f"your placements/look-alikes JSON (default: beside Working, {EXPECTATIONS_NAME})")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="print the counts only; write nothing")
    mode.add_argument("--check", action="store_true", help="verify the page exists and is newer than run.json and expectations")
    args = parser.parse_args(argv)
    run = pathlib.Path(args.run)
    if not (run / "run.json").is_file():
        parser.error(f"no run.json in {run}")
    data = collect(run)
    data["expectationsPath"] = pathlib.Path(args.expectations) if args.expectations else expectations_path(data)
    data["expectations"] = load_expectations(data["expectationsPath"])
    out = pathlib.Path(args.out) if args.out else default_out(data)
    summary = summarize(data)
    results = collections.Counter(item["state"] for item in expectation_results(data))
    print(f"{data['status']}: {summary['photos']} photos; {json.dumps(summary['kinds'])}; "
          f"{summary['renamed']} renamed; {summary['review']} in Review; {summary['newIdentities']} new identities; "
          f"{summary['emptiedIdentities']} emptied; expectations {dict(results) or 'none'}")
    if args.dry_run:
        print(f"Would write {out} and its run index")
        return 0
    if args.check:
        sources = [run / "run.json", data["expectationsPath"]]
        newest = max(path.stat().st_mtime for path in sources if path.is_file())
        if not out.is_file() or out.stat().st_mtime < newest:
            print(f"Recap missing or older than run.json/expectations: {out}")
            return 1
        print(f"Recap current: {out}")
        return 0
    others, entries = [], []
    for sibling in sibling_runs(run, data["workingRoot"]):
        try:
            other = collect(sibling)
        except (OSError, ValueError, KeyError) as exc:
            print(f"Skipped {sibling.name}: {exc}")
            continue
        others.append(other)
        page = out.parent / _run_page_name(other)
        if other.get("historical"):
            other["expectationsPath"] = data["expectationsPath"]
            other["expectations"] = data["expectations"]
            _write(page, render(other, page, [data]))
        if page.is_file():
            label = sibling.name + (" (historical; images unavailable)" if other.get("historical") else "")
            entries.append((label, other["status"], other["castSeedPolicy"], other["createdAt"],
                            summarize(other), page))
    _write(out, render(data, out, others))
    entries.append((run.name, data["status"], data["castSeedPolicy"], data["createdAt"], summary, out))
    entries.sort(key=lambda entry: str(entry[3]), reverse=True)
    _write(out.parent / "index.html", render_index(entries, out.parent))
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
