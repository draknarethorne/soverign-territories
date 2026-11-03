"""One HTML page per sandbox rebase run explaining what it planned or applied, plus an index of runs.

Reads only RUN\\run.json, the intake manifest, sibling runs and the user's expectations file (beside Working, so a
sandbox reset keeps it). It lists every photo that stayed, moved between people, moved between gallery and review,
or was renamed; Angels/Sisters gains and losses; new identities grouped by family surname with their nearest cast
member and the user's own "looks like" pick; review holds; differences from other runs of the same inputs (for
example all versus core cast seeds); and whether expected photo placements happened. No library file is changed.
sandbox-rebase.cmd regenerates it after every preview, replan, apply, check and undo.
"""

import argparse
import collections
import datetime
import hashlib
import html
import json
import os
import pathlib
import statistics
import urllib.parse

CAST = ("Angels", "Sisters")
OUT_DIR = "rebase-recap"
EXPECTATIONS_NAME = "rebase-expectations.json"
NEW_PERSON = "new person"
UNSURE = "unsure"


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
    return "stayed"


def _manifest_rows(run):
    path = run / "inputs" / "_reports" / "preparation" / "all" / "manifest.json"
    if not path.is_file():
        return {}, None
    data = json.loads(path.read_text(encoding="utf-8"))
    return {row["source"]: row for row in data.get("photos", [])}, path.parent


def collect(run):
    """Every planned/applied photo row with its change, plus grouped views; pure data, no HTML."""
    run = pathlib.Path(run)
    plan = json.loads((run / "run.json").read_text(encoding="utf-8"))
    manifest, preparation = _manifest_rows(run)
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
        rows.append({
            "source": photo["source"], "destination": photo["destination"],
            "originalFolder": photo.get("sourceFolder") or old_person,
            "oldPerson": old_person, "oldBucket": old_bucket, "newPerson": new_person, "newBucket": new_bucket,
            "kind": change_kind(photo),
            "renamed": pathlib.PurePosixPath(source_name).stem != pathlib.PurePosixPath(new_name).stem,
            "converted": pathlib.PurePosixPath(source_name).suffix.lower() != pathlib.PurePosixPath(new_name).suffix.lower(),
            "photoId": photo.get("photoId"), "reason": photo.get("reason", ""),
            "score": photo.get("score"), "bestMatch": photo.get("bestMatch"), "bestScore": photo.get("bestScore"),
            "nearestCast": photo.get("initialBestCast"), "nearestCastScore": photo.get("initialBestCastScore"),
            "secondCast": photo.get("initialSecondCast"), "castMargin": photo.get("initialCastMargin"),
            "retainedCast": photo.get("retainedCast"), "releasedCast": photo.get("releasedCast"),
            "destinationType": photo.get("destinationType"),
            "preparationOutcome": photo.get("preparationOutcome"),
            "preview": str(preparation / preview) if preparation and preview else None,
            "detail": str(preparation / detail) if preparation and detail else None,
        })
    old_people = {row["oldPerson"] for row in rows} | set(plan.get("referenceFolders", []))
    new_people = {row["newPerson"] for row in rows}
    return {
        "run": str(run), "workingRoot": plan["workingRoot"], "status": plan["status"],
        "sourceManifestSHA256": plan.get("sourceManifestSHA256"),
        "cast": sorted(person for person in old_people | new_people if person.startswith(CAST)),
        "createdAt": plan.get("createdAt"), "policy": plan.get("policy", {}).get("version")
        if isinstance(plan.get("policy"), dict) else plan.get("policy"),
        "castSeedPolicy": plan.get("castSeedPolicy", "all"),
        "preparationIndex": str(preparation / "index.html") if preparation else None,
        "rows": rows,
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
    }


def _href(target, out_dir):
    try:
        relative = os.path.relpath(target, out_dir).replace(os.sep, "/")
    except ValueError:
        return pathlib.Path(os.path.abspath(target)).as_uri()
    return urllib.parse.quote(relative, safe="/._-~")


def _score(value):
    return "" if value is None else f"{value:.3f}"


def _thumb(row, data, out_dir):
    live = pathlib.Path(data["workingRoot"]) / row["destination"]
    image = row["preview"] or str(live)
    title = html.escape(f"{row['source']} -> {row['destination']}", quote=True)
    return (f'<a href="{_href(live, out_dir)}" title="{title}">'
            f'<img loading="lazy" src="{_href(image, out_dir)}" alt=""></a>')


def _card(row, data, out_dir, note):
    links = f' <a href="{_href(row["detail"], out_dir)}">intake</a>' if row["detail"] else ""
    return (f'<figure>{_thumb(row, data, out_dir)}<figcaption>{html.escape(note)}{links}</figcaption></figure>')


def _origin(row):
    if row["originalFolder"] == row["oldPerson"]:
        return row["oldPerson"]
    return f"{row['oldPerson']} (first intake {row['originalFolder']})"


def _cards(rows, data, out_dir, note):
    if not rows:
        return "<p class=muted>None.</p>"
    return '<div class=grid>' + "".join(_card(row, data, out_dir, note(row)) for row in rows) + "</div>"


def _cast_section(data, out_dir):
    rows = data["rows"]
    people = sorted({row["oldPerson"] for row in rows if row["oldPerson"].startswith(CAST)}
                    | {row["newPerson"] for row in rows if row["newPerson"].startswith(CAST)})
    parts = ["<h2 id=cast>Angels and Sisters</h2>",
             "<table><tr><th>Person</th><th>Kept</th><th>Lost</th><th>Gained</th><th>Now in Review</th></tr>"]
    details = []
    for person in people:
        kept = [r for r in rows if r["oldPerson"] == person and r["newPerson"] == person and r["newBucket"] == "gallery"]
        held = [r for r in rows if r["newPerson"] == person and r["newBucket"] == "review"]
        lost = [r for r in rows if r["oldPerson"] == person and r["newPerson"] != person]
        gained = [r for r in rows if r["newPerson"] == person and r["oldPerson"] != person]
        anchor = "cast-" + person.replace("/", "-").replace(" ", "_")
        parts.append(f'<tr><td><a href="#{anchor}">{html.escape(person)}</a></td><td>{len(kept)}</td>'
                     f'<td class={"warn" if lost else ""}>{len(lost)}</td><td>{len(gained)}</td><td>{len(held)}</td></tr>')
        details.append(
            f'<details id="{anchor}"{" open" if lost or gained else ""}><summary>{html.escape(person)}: '
            f'{len(kept)} kept, {len(lost)} lost, {len(gained)} gained, {len(held)} in Review</summary>'
            f"<h4>Lost</h4>{_cards(lost, data, out_dir, lambda r: f'to {r['newPerson']} ({r['newBucket']}); {r['reason']}')}"
            f"<h4>Gained</h4>{_cards(gained, data, out_dir, lambda r: f'from {_origin(r)}; score {_score(r['score'])}; nearest cast {r['nearestCast'] or '-'} {_score(r['nearestCastScore'])}')}"
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
    for person in members:
        families[person.rsplit("/", 1)[-1].rsplit(None, 1)[-1]].append(person)
    new = set(data["newIdentities"])
    said = data.get("expectations", {}).get("identities", {})
    choices = ["", *data["cast"], NEW_PERSON, UNSURE]
    parts = ["<h2 id=identities>Other identities (grouped by family surname)</h2>",
             "<p class=muted>Nearest cast is the cast member each photo scored closest to before assignment. "
             "Many photos pointing at the same cast member with similar scores suggest the identity may really be "
             "that cast member; a shared surname means the identities were detected as one family. "
             "Use <b>Looks like</b> to record your own judgement, then <b>Save my picks</b>; the saved file is read by "
             "every later recap and compared with what the rebase did.</p>",
             "<table><tr><th>Family</th><th>Identity</th><th>New</th><th>Photos</th><th>Came from</th>"
             "<th>Nearest cast (share, mean score)</th><th>Looks like (yours)</th></tr>"]
    details = []
    for surname, people in sorted(families.items(), key=lambda item: (-sum(len(members[p]) for p in item[1]), item[0])):
        for person in sorted(people, key=lambda p: -len(members[p])):
            group = members[person]
            origins = collections.Counter(r["oldPerson"] for r in group)
            nearest = collections.Counter(r["nearestCast"] for r in group if r["nearestCast"])
            top, count = nearest.most_common(1)[0] if nearest else ("-", 0)
            scores = [r["nearestCastScore"] for r in group if r["nearestCast"] == top and r["nearestCastScore"] is not None]
            mean = statistics.fmean(scores) if scores else None
            anchor = "id-" + person.replace("/", "-").replace(" ", "_")
            mine = said.get(person, "")
            options = "".join(
                f'<option value="{html.escape(choice, quote=True)}"{" selected" if choice == mine else ""}>'
                f"{html.escape(choice or '-')}</option>" for choice in choices + ([mine] if mine not in choices else []))
            disagrees = mine.startswith(CAST)
            parts.append(
                f'<tr><td>{html.escape(surname if len(people) > 1 else "")}</td>'
                f'<td><a href="#{anchor}">{html.escape(person)}</a></td><td>{"yes" if person in new else ""}</td>'
                f"<td>{len(group)}</td><td>{html.escape(', '.join(f'{k} {v}' for k, v in origins.most_common(4)))}</td>"
                f"<td>{html.escape(top)} ({count}/{len(group)}, {_score(mean)})</td>"
                f'<td class="{"warn" if disagrees else ""}"><select class=pick data-identity="{html.escape(person, quote=True)}">'
                f"{options}</select></td></tr>")
            details.append(
                f'<details id="{anchor}"><summary>{html.escape(person)}: {len(group)} photos</summary>'
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
    """Photos placed differently by another run of the same inputs, keyed by photo ID or source."""
    def key(row):
        return row["photoId"] or row["source"]
    theirs = {key(row): row for row in other["rows"]}
    return [(row, theirs[key(row)]) for row in data["rows"]
            if key(row) in theirs and (row["newPerson"], row["newBucket"]) != (theirs[key(row)]["newPerson"],
                                                                               theirs[key(row)]["newBucket"])]


def _comparison_section(data, others, out_dir):
    if not others:
        return ""
    parts = ["<h2 id=compare>Compared with other runs of the same inputs</h2>"]
    for other in others:
        differences = compare_runs(data, other)
        name = pathlib.Path(other["run"]).name
        parts.append(f"<h3>{html.escape(name)} ({html.escape(other['status'])}, cast seeds "
                     f"{html.escape(other['castSeedPolicy'])}): {len(differences)} photos placed differently</h3>")
        flows = collections.Counter(
            (mine["newPerson"] + (" (review)" if mine["newBucket"] == "review" else ""),
             theirs["newPerson"] + (" (review)" if theirs["newBucket"] == "review" else ""))
            for mine, theirs in differences)
        parts.append("<table><tr><th>This run</th><th>" + html.escape(name) + "</th><th>Photos</th></tr>")
        parts.extend(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td><td>{count}</td></tr>"
                     for (a, b), count in flows.most_common(60))
        parts.append("</table>")
    return "".join(parts)


def _review_section(data, out_dir):
    rows = [row for row in data["rows"] if row["newBucket"] == "review"]
    reasons = collections.defaultdict(list)
    for row in rows:
        reasons[row["reason"].split(";")[0]].append(row)
    parts = [f"<h2 id=review>Review holds ({len(rows)})</h2>"]
    for reason, group in sorted(reasons.items(), key=lambda item: -len(item[1])):
        parts.append(
            f"<details><summary>{html.escape(reason)}: {len(group)}</summary>"
            f"{_cards(group, data, out_dir, lambda r: f'{r['newPerson']}; was {r['oldPerson']}; {r['reason']}')}"
            "</details>")
    return "".join(parts)


def _flow_section(data):
    flows = collections.Counter((row["oldPerson"], row["newPerson"], row["newBucket"])
                                for row in data["rows"] if row["kind"] != "stayed")
    parts = ["<h2 id=flows>Where photos went</h2><table><tr><th>From</th><th>To</th><th>Count</th></tr>"]
    for (old, new, bucket), count in flows.most_common():
        target = new + (" (review)" if bucket == "review" else "")
        parts.append(f"<tr><td>{html.escape(old)}</td><td>{html.escape(target)}</td><td>{count}</td></tr>")
    parts.append("</table>")
    if data["emptiedIdentities"]:
        parts.append("<h3>Identities emptied by the rebase</h3><ul>"
                     + "".join(f"<li>{html.escape(p)}</li>" for p in data["emptiedIdentities"]) + "</ul>")
    return "".join(parts)


def _all_rows(data, out_dir):
    parts = ["<h2 id=all>Every photo</h2><p><input id=filter placeholder='Filter: name, person, reason...' size=50> "
             "<label><input type=checkbox id=changed checked> changed only</label></p>",
             "<table id=photos><tr><th>Photo</th><th>Change</th><th>Before</th><th>After</th><th>Score</th>"
             "<th>Nearest cast</th><th>Reason</th></tr>"]
    for row in sorted(data["rows"], key=lambda r: (r["kind"] == "stayed", r["oldPerson"], r["source"])):
        kind = row["kind"] + (" renamed" if row["renamed"] else "")
        detail = f'<br><a href="{_href(row["detail"], out_dir)}">intake</a>' if row["detail"] else ""
        parts.append(
            f'<tr data-kind="{row["kind"]}"><td class=t>{_thumb(row, data, out_dir)}{detail}</td><td>{html.escape(kind)}</td>'
            f"<td>{html.escape(row['source'])}</td><td>{html.escape(row['destination'])}</td>"
            f"<td>{_score(row['score'])}</td><td>{html.escape(row['nearestCast'] or '')} {_score(row['nearestCastScore'])}</td>"
            f"<td>{html.escape(row['reason'])}</td></tr>")
    parts.append("</table>")
    return "".join(parts)


STYLE = """body{font-family:Segoe UI,Arial,sans-serif;margin:16px;color:#222}table{border-collapse:collapse;margin:8px 0}
td,th{border:1px solid #ccc;padding:3px 6px;font-size:13px;vertical-align:top}th{background:#eee}.muted{color:#666}
.warn{background:#fde2e2}.grid{display:flex;flex-wrap:wrap;gap:6px}figure{margin:0;width:132px;font-size:11px}
figure img,td.t img{width:128px;height:150px;object-fit:cover;border:1px solid #bbb}td.t img{width:80px;height:94px}
.cards{display:flex;gap:10px;flex-wrap:wrap}.cards div{border:1px solid #ccc;padding:8px 12px;border-radius:6px}
.cards b{font-size:20px;display:block}summary{cursor:pointer;margin:4px 0}nav a{margin-right:12px}"""

SCRIPT = """const f=document.getElementById('filter'),c=document.getElementById('changed');
function apply(){const q=f.value.toLowerCase();for(const r of document.querySelectorAll('#photos tr[data-kind]')){
r.style.display=(c.checked&&r.dataset.kind==='stayed')||(q&&!r.textContent.toLowerCase().includes(q))?'none':''}}
f.addEventListener('input',apply);c.addEventListener('change',apply);apply();
const saved=__EXPECTATIONS__;
document.getElementById('save-picks').addEventListener('click',()=>{
const identities={...(saved.identities||{})};
for(const s of document.querySelectorAll('select.pick')){if(s.value)identities[s.dataset.identity]=s.value;else delete identities[s.dataset.identity]}
const body=JSON.stringify({identities,photos:saved.photos||{}},null,2);
const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([body],{type:'application/json'}));
a.download='rebase-expectations.json';a.click()});"""


def render(data, out_path, others=()):
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
    kinds = summary["kinds"]
    applied = data["status"] == "applied"
    cards = [("Photos", summary["photos"]), ("Stayed", kinds.get("stayed", 0)),
             ("Moved between people", kinds.get("moved", 0) + kinds.get("moved-to-review", 0)),
             ("Gallery to Review", kinds.get("to-review", 0) + kinds.get("moved-to-review", 0)),
             ("Review to Gallery", kinds.get("from-review", 0)), ("Renamed", summary["renamed"]),
             ("Converted to PNG", summary["converted"]), ("New identities", summary["newIdentities"]),
             ("Emptied identities", summary["emptiedIdentities"])]
    body = [
        f"<h1>Sandbox rebase recap: {html.escape(pathlib.Path(data['run']).name)}</h1>",
        f"<p>Status <b>{html.escape(data['status'])}</b>{'' if applied else ' (planned; nothing applied yet)'}; "
        f"policy {html.escape(str(data['policy']))}; cast seeds {html.escape(data['castSeedPolicy'])}; "
        f"plan created {html.escape(str(data['createdAt']))}; page generated "
        f"{datetime.datetime.now():%Y-%m-%d %H:%M}.</p>",
        "<nav>" + "".join(f'<a href="{_href(path, out_dir)}">{label}</a>' for path, label in links) + "</nav>",
        "<nav><a href=#expected>Your expectations</a><a href=#flows>Where photos went</a><a href=#cast>Angels and Sisters</a>"
        "<a href=#identities>Other identities</a><a href=#review>Review holds</a>"
        + ("<a href=#compare>Other runs</a>" if others else "") + "<a href=#all>Every photo</a></nav>",
        '<div class=cards>' + "".join(f"<div><b>{value}</b>{label}</div>" for label, value in cards) + "</div>",
        "<p class=muted>Thumbnails are the prepared intake image used for matching; click one to open the photo in its "
        "new place, or 'intake' for the full comparison page. Undo with sandbox-rebase.cmd ... --undo.</p>",
        _expectation_section(data, out_dir), _flow_section(data), _cast_section(data, out_dir),
        _identity_section(data, out_dir), _review_section(data, out_dir),
        _comparison_section(data, others, out_dir), _all_rows(data, out_dir),
    ]
    script = SCRIPT.replace("__EXPECTATIONS__", json.dumps(data.get("expectations", {})).replace("</", "<\\/"))
    return ("<!doctype html><html><head><meta charset=utf-8><title>Sandbox rebase recap</title>"
            f"<style>{STYLE}</style></head><body>{''.join(body)}<script>{script}</script></body></html>")


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
    return recap_dir(data) / f"{pathlib.Path(data['run']).name}.html"


def sibling_runs(run):
    """Other runs beside this one; only those built from the same source manifest are comparable."""
    run = pathlib.Path(run)
    return sorted(path for path in run.parent.iterdir()
                  if path != run and path.is_dir() and (path / "run.json").is_file())


def render_index(entries, out_dir):
    rows = "".join(
        f'<tr><td><a href="{_href(page, out_dir)}">{html.escape(name)}</a></td><td>{html.escape(status)}</td>'
        f"<td>{html.escape(seeds)}</td><td>{html.escape(str(created))}</td><td>{summary['photos']}</td>"
        f"<td>{summary['photos'] - summary['kinds'].get('stayed', 0)}</td><td>{summary['review']}</td>"
        f"<td>{summary['newIdentities']}</td></tr>"
        for name, status, seeds, created, summary, page in entries)
    return ("<!doctype html><html><head><meta charset=utf-8><title>Sandbox rebase runs</title>"
            f"<style>{STYLE}</style></head><body><h1>Sandbox rebase runs</h1>"
            "<p class=muted>Regenerated by every sandbox-rebase.cmd preview, replan, apply, check or undo.</p>"
            "<table><tr><th>Run</th><th>Status</th><th>Cast seeds</th><th>Plan created</th><th>Photos</th>"
            f"<th>Changed</th><th>In Review</th><th>New identities</th></tr>{rows}</table></body></html>")


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
    for sibling in sibling_runs(run):
        try:
            other = collect(sibling)
        except (OSError, ValueError, KeyError) as exc:
            print(f"Skipped {sibling.name}: {exc}")
            continue
        if other["sourceManifestSHA256"] == data["sourceManifestSHA256"]:
            others.append(other)
        page = out.parent / f"{sibling.name}.html"
        if page.is_file():
            entries.append((sibling.name, other["status"], other["castSeedPolicy"], other["createdAt"],
                            summarize(other), page))
    _write(out, render(data, out, others))
    entries.append((run.name, data["status"], data["castSeedPolicy"], data["createdAt"], summary, out))
    entries.sort(key=lambda entry: str(entry[3]), reverse=True)
    _write(out.parent / "index.html", render_index(entries, out.parent))
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
