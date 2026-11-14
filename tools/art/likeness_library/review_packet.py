"""Bounded visual comparisons of a saved final audit, never identity truth."""
import collections
import hashlib
import html
import io
import json
import pathlib
from urllib.parse import quote

import numpy as np
from PIL import Image, ImageOps

from . import shadow
from .thumbnails import face_thumbnail


def safe_path(root, relative):
    parts = pathlib.PurePosixPath(relative)
    if parts.is_absolute() or ".." in parts.parts or "\\" in relative or ":" in relative:
        raise ValueError(f"unsafe saved relative path: {relative}")
    path = root.joinpath(*parts.parts).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"saved path escapes root: {relative}")
    return path


def load_experiment(experiment):
    receipt = json.loads((experiment / "receipt.json").read_bytes())
    if set(receipt["outputs"]) != {"scope.json", "experiment.json"}:
        raise ValueError("unexpected shadow output contract")
    for name, expected in receipt["outputs"].items():
        if shadow.digest(experiment / name) != expected:
            raise ValueError(f"shadow evidence changed: {name}")
    inputs = receipt["provenance"]["inputs"]
    for name, binding in inputs.items():
        path = pathlib.Path(binding["path"])
        if path.name != name or shadow.digest(path) != binding["sha256"]:
            raise ValueError(f"shadow input changed: {name}")
    run_path = pathlib.Path(inputs["run.json"]["path"])
    run, vectors, _ = shadow.load_bundle(run_path.parent)
    scope = json.loads((experiment / "scope.json").read_bytes())
    return run, vectors, scope, {
        "shadowReceiptSHA256": shadow.digest(experiment / "receipt.json"),
        "runSHA256": inputs["run.json"]["sha256"],
        "scopeSHA256": receipt["outputs"]["scope.json"],
        "sourceRun": str(run_path.parent),
    }


def final_score_parity(run, vectors):
    """Reconstruct saved core arithmetic, not core selection or final routing."""
    audit = run["finalMembershipAudit"]["rows"]
    groups = collections.defaultdict(list)
    for row in audit:
        if row["coreMember"]:
            groups[shadow.folder_for(row)].append(row["photoId"])
    cores = {
        folder: shadow.nz(np.mean([vectors[pid] for pid in ids], axis=0))
        for folder, ids in groups.items()
    }
    checked = collections.Counter()
    for row in audit:
        if not row.get("qualityEligible"):
            continue
        pid, folder = row["photoId"], shadow.folder_for(row)
        vector = vectors[pid]
        for rival in row["rivals"]:
            actual = round(float(vector @ cores[rival["folder"]]), 6)
            if actual != rival["score"]:
                raise ValueError(f"saved final rival arithmetic differs: {pid} / {rival['folder']}")
            checked["rivalScores"] += 1
        if row["ownScore"] is not None:
            ids = groups[folder]
            reference = cores[folder]
            if pid in ids:
                others = [vectors[other] for other in ids if other != pid]
                if not others:
                    raise ValueError(f"singleton has a saved self-score: {pid}")
                reference = shadow.nz(np.sum(others, axis=0))
            actual = round(float(np.clip(vector @ reference, -1, 1)), 6)
            if actual != row["ownScore"]:
                raise ValueError(f"saved final own arithmetic differs: {pid}")
            checked["ownScores"] += 1
    return {
        **checked, "coreCount": len(cores), "precisionDecimals": 6,
        "boundary": "Saved final core membership reused; own/rival arithmetic verified. "
                    "Core selection, admission, continuity and routing NOT independently replayed.",
    }, groups


def select_cases(run, vectors, scope, *, neighbours=12):
    rows = {row["photoId"]: row for row in run["finalMembershipAudit"]["rows"]}
    folders = collections.defaultdict(list)
    for row in rows.values():
        folders[shadow.folder_for(row)].append(row)
    seeds = sorted({folder for values in scope["seeds"].values() for folder in values})
    selected = {}

    def add(row, reason):
        selected.setdefault(row["photoId"], {"row": row, "selectionReasons": []})["selectionReasons"].append(reason)

    def gap(row):
        rival = row["rivals"][0]["score"] if row["rivals"] else -1.
        return rival - row["ownScore"] if row["ownScore"] is not None else 2.

    for folder in seeds:
        eligible = [
            row for row in folders[folder]
            if row.get("qualityEligible") and row["photoId"] in vectors
        ]
        if not eligible:
            raise ValueError(f"seed identity has no eligible comparison photos: {folder}")
        stable = min(eligible, key=lambda row: (gap(row), row["photoId"]))
        contested = min(eligible, key=lambda row: (-gap(row), row["photoId"]))
        add(stable, "strongest saved own-versus-rival margin in this seed (not a positive label)")
        add(contested, "weakest saved own-versus-rival margin in this seed (not a negative label)")
        remaining = [row for row in eligible if row["photoId"] not in selected]
        if remaining:
            varied = min(remaining, key=lambda row: (
                float(vectors[row["photoId"]] @ vectors[stable["photoId"]]), row["photoId"],
            ))
            add(varied, "most face-vector-different remaining view from the stable sample; pose not inferred")
    pinned = "photo:image_7513773530805044436"
    if pinned in rows and shadow.folder_for(rows[pinned]) in seeds:
        add(rows[pinned], "previous Angelica workflow-photo investigation; identity remains unlabelled")
    scope_ids = {row["photoId"] for row in scope["photos"]}
    outsiders = [
        row for row in rows.values()
        if row["photoId"] in scope_ids and shadow.folder_for(row) not in seeds
        and row.get("qualityEligible") and row["photoId"] in vectors
    ]
    # One per competing identity before taking the next: broad context, not one large folder.
    seen = set()
    for row in sorted(outsiders, key=lambda row: (-gap(row), row["photoId"])):
        folder = shadow.folder_for(row)
        if folder in seen:
            continue
        if len(seen) == neighbours:
            break
        seen.add(folder)
        add(row, "neighbour identity with a weak own-versus-rival margin; global rivals retained")
    ordered = sorted(selected.values(), key=lambda case: (
        shadow.folder_for(case["row"]) != "Angels/angelica",
        shadow.folder_for(case["row"]) not in seeds,
        shadow.folder_for(case["row"]).casefold(), case["row"]["photoId"],
    ))
    return ordered, seeds


def choose_references(folder, groups, rows, vectors, *, exclude, count=3):
    ids = [pid for pid in groups.get(folder, []) if pid != exclude]
    if not ids:
        return []
    first = min(ids, key=lambda pid: (
        not rows[pid].get("anchor"),
        -(rows[pid]["ownScore"] if rows[pid]["ownScore"] is not None else -1.), pid,
    ))
    selected = [first]
    while len(selected) < min(count, len(ids)):
        selected.append(min(
            (pid for pid in ids if pid not in selected),
            key=lambda pid: (max(float(vectors[pid] @ vectors[other]) for other in selected), pid),
        ))
    return selected


def build_packet(run, vectors, scope, binding, *, neighbours=12):
    parity, groups = final_score_parity(run, vectors)
    chosen, seeds = select_cases(run, vectors, scope, neighbours=neighbours)
    rows = {row["photoId"]: row for row in run["finalMembershipAudit"]["rows"]}
    photos = {row["photoId"]: row for row in run["photos"]}
    cases, used = [], set()
    for index, selection in enumerate(chosen, 1):
        row = selection["row"]
        pid, folder = row["photoId"], shadow.folder_for(row)
        panels = []
        targets = [{"folder": folder, "score": row["ownScore"], "kind": "Current placement"}]
        if row["rivals"]:
            targets.append({**row["rivals"][0], "kind": "Strongest saved rival"})
        for target in targets:
            refs = choose_references(target["folder"], groups, rows, vectors, exclude=pid)
            used.update(refs)
            panels.append({**target, "references": [
                {"photoId": ref, "pairScore": round(float(vectors[pid] @ vectors[ref]), 6),
                 "coreMember": True}
                for ref in refs
            ]})
        used.add(pid)
        cases.append({
            "id": f"case-{index:03d}", "photoId": pid, "folder": folder,
            "selectionReasons": selection["selectionReasons"], "panels": panels,
            "rivals": row["rivals"], "reason": row["reason"],
            "decision": row.get("refinementDecision"),
            "flags": {key: row.get(key) for key in (
                "coreMember", "protected", "anchor", "workflowSelected", "automaticProtection",
                "manualOptOut", "qualityEligible", "rejectionHistory",
            )},
            "source": photos[pid]["source"], "destination": photos[pid]["destination"],
            "initialBestCast": photos[pid].get("initialBestCast"),
            "initialBestCastScore": photos[pid].get("initialBestCastScore"),
        })
    seed_summary = [
        {"folder": folder, "photoCount": sum(shadow.folder_for(row) == folder for row in rows.values()),
         "coreCount": len(groups.get(folder, [])),
         "caseIds": [case["id"] for case in cases if case["folder"] == folder]}
        for folder in seeds
    ]
    return {
        "schemaVersion": 1, "binding": binding, "finalScoreParity": parity,
        "workingRoot": run["workingRoot"],
        "seedIdentities": seed_summary, "scopeIdentityCount": scope["identityCount"],
        "scopePhotoCount": scope["photoCount"], "cases": cases,
        "usedPhotoIds": sorted(used),
        "labels": "Every pair starts unreviewed. No surnames, references or saved groups are truth labels.",
        "heldOut": "Unallocated: label and resolve related-person/series leakage before reserving held-out groups.",
    }


def image_assets(packet, run, cache, out, *, write=False):
    root = pathlib.Path(run["workingRoot"]).resolve()
    photos = {row["photoId"]: row for row in run["photos"]}
    published = {row["path"]: row["sha256"] for row in run["publishedFiles"]}
    measurements = {
        item["alignmentEvidence"]["sourceSha256"]: item
        for item in cache["emb"].values() if item.get("alignmentEvidence", {}).get("sourceSha256")
    }
    images, outputs = {}, {}
    for pid in packet["usedPhotoIds"]:
        row = photos[pid]
        source = safe_path(root, row["destination"])
        expected = published.get(row["destination"])
        if not expected or shadow.digest(source) != expected:
            raise ValueError(f"installed photo missing or changed since baseline: {source}")
        box = measurements[row["preparedSHA256"]].get("box")
        if not box:
            raise ValueError(f"missing content-bound face box: {pid}")
        key = hashlib.sha256(pid.encode()).hexdigest()[:20]
        paths = {kind: f"images/{key}-{kind}.jpg" for kind in ("face", "full")}
        images[pid] = {
            "path": str(source), "sha256": expected, "href": source.as_uri(), **paths,
        }
        if write:
            with Image.open(source) as image:
                frames = {
                    "face": face_thumbnail(image, box, (240, 240)),
                    "full": ImageOps.contain(ImageOps.exif_transpose(image).convert("RGB"), (360, 480)),
                }
                for kind, frame in frames.items():
                    stream = io.BytesIO()
                    frame.save(stream, format="JPEG", quality=86)
                    data = stream.getvalue()
                    path = out / paths[kind]
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                    outputs[paths[kind]] = hashlib.sha256(data).hexdigest()
    return images, outputs


def render(packet):
    escape = html.escape
    images = packet["images"]
    review = pathlib.Path(packet["workingRoot"]) / "_reports" / "library" / "people_gallery_review.html"

    def person_link(folder):
        if not review.is_file():
            return "<small>Full installed Photo review unavailable.</small>"
        uri = review.as_uri() + "?person=" + quote(folder, safe="")
        return f'<a href="{escape(uri, quote=True)}" target="_blank" rel="noopener">Open all current photos</a>'

    def image(pid, *, reference=False, case_id=""):
        record = images[pid]
        controls = ""
        if reference:
            pair = f"{case_id}|{pid}"
            controls = (
                f'<label>Compared with the subject: <select data-pair="{escape(pair, quote=True)}">'
                '<option value="unreviewed">Not reviewed</option><option value="same">Same person</option>'
                '<option value="different">Different person</option><option value="uncertain">Uncertain</option>'
                '</select></label>'
            )
        return (
            '<figure>'
            f'<a href="{escape(record["href"], quote=True)}" target="_blank" rel="noopener">'
            f'<img class="face" src="{record["face"]}" loading="lazy" alt="Face: {escape(pid)}">'
            f'<img class="full" src="{record["full"]}" loading="lazy" alt="Full photo: {escape(pid)}"></a>'
            f'<figcaption>{escape(pid)}</figcaption>{controls}</figure>'
        )

    cards = []
    for case in packet["cases"]:
        panels = []
        for panel in case["panels"]:
            refs = "".join(
                f'<div class="reference">{image(ref["photoId"], reference=True, case_id=case["id"])}'
                f'<small>Photo-to-photo cosine: {ref["pairScore"]:.3f}</small></div>'
                for ref in panel["references"]
            )
            score = "unavailable" if panel["score"] is None else f'{panel["score"]:.3f}'
            panels.append(
                f'<section class="panel"><h3>{escape(panel["kind"])}: {escape(panel["folder"])}</h3>'
                f'{person_link(panel["folder"])}'
                f'<p>Subject-to-core score: <strong>{score}</strong>. '
                'Current own score leaves the subject out when it is a core member.</p>'
                f'<div class="references">{refs or "<p>No independent core reference photos available.</p>"}</div></section>'
            )
        flags = ", ".join(f"{key}={value}" for key, value in case["flags"].items())
        cards.append(
            f'<article id="{case["id"]}" data-folder="{escape(case["folder"], quote=True)}">'
            f'<h2>{case["id"]} - {escape(case["folder"])}</h2>'
            f'<p>{"; ".join(escape(reason) for reason in case["selectionReasons"])}</p>'
            f'<div class="comparison"><section class="subject"><h3>Subject photo</h3>{image(case["photoId"])}'
            f'<p>Baseline home: {escape(case["destination"])}</p>'
            f'<p>Core contributor: {case["flags"]["coreMember"]}<br>'
            f'Photo protected: {case["flags"]["protected"]}<br>'
            f'Anchor: {case["flags"]["anchor"]}<br>'
            f'Workflow selected: {case["flags"]["workflowSelected"]}</p></section>'
            f'<div class="panels">{"".join(panels)}</div></div>'
            f'<label>Notes (optional)<textarea data-note="{case["id"]}" rows="2" '
            'placeholder="Expression/angle, mixed reference panel, obvious series, or uncertainty"></textarea></label>'
            '<details><summary>Why it stayed here / provenance</summary>'
            f'<p>{escape(case["reason"])}</p><p>{escape(json.dumps(case["decision"]))}</p>'
            f'<p>{escape(flags)}</p><p>Original source: {escape(case["source"])}</p>'
            f'<p>Initial cast match: {escape(str(case["initialBestCast"]))}; '
            f'score {escape(str(case["initialBestCastScore"]))}. This is a different stage.</p>'
            f'<pre>{escape(json.dumps(case["rivals"], indent=2))}</pre></details></article>'
        )
    options = "".join(
        f'<option value="{escape(row["folder"], quote=True)}">{escape(row["folder"])} '
        f'({row["photoCount"]} photos, {row["coreCount"]} saved core)</option>'
        for row in packet["seedIdentities"]
    )
    payload = json.dumps({
        "binding": packet["binding"], "packetSHA256": packet["packetSHA256"],
        "cases": [{"id": case["id"], "photoId": case["photoId"],
                   "references": [ref["photoId"] for panel in case["panels"] for ref in panel["references"]]}
                  for case in packet["cases"]],
    }).replace("<", "\\u003c")
    return TEMPLATE.replace("{{OPTIONS}}", options).replace("{{CARDS}}", "".join(cards)).replace(
        "{{DATA}}", payload,
    ).replace("{{COUNT}}", str(len(packet["cases"]))).replace(
        "{{PARITY}}", escape(json.dumps(packet["finalScoreParity"])),
    )


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Likeness reassessment - baseline visual review</title>
<style>
body{font:16px system-ui;background:#15191f;color:#e3e8ef;margin:0;padding:24px;line-height:1.45}
a{color:#8fceff}header,article{max-width:1550px;margin:0 auto 24px}h1{margin-top:0}
.notice{border-left:4px solid #e6b458;background:#282c32;padding:12px}
nav{position:sticky;top:0;background:#20262e;padding:12px;z-index:2;border:1px solid #58616d;display:flex;gap:12px;flex-wrap:wrap;max-width:1550px;margin:0 auto 24px}
button,select,input,textarea{font:inherit;background:#f3f5f8;color:#16202b;border-radius:4px;padding:6px;max-width:100%}
button{cursor:pointer}article{background:#20262e;padding:16px;border:1px solid #536071;border-radius:8px;scroll-margin-top:100px}
.comparison{display:grid;grid-template-columns:280px 1fr;gap:18px}.subject{border-right:1px solid #546173;padding-right:14px;position:sticky;top:150px;align-self:start;overflow-wrap:anywhere}
.references{display:grid;grid-template-columns:repeat(3,minmax(140px,1fr));gap:10px}
figure{margin:0}figure a{display:flex;gap:4px;align-items:start}img{object-fit:contain;max-width:100%;background:#101317}
.face{width:100%;max-height:240px}.full{display:none;width:100%;max-height:480px}
body.full-mode .face{display:none}body.full-mode .full{display:block}
figcaption{font-size:11px;overflow-wrap:anywhere}label{display:block}figure label{font-size:13px;margin-top:8px}
.panel{margin-bottom:20px}h3{margin:4px 0 8px}textarea{width:95%}pre{white-space:pre-wrap}small{color:#b7c8db}
[hidden]{display:none!important}.status{font-weight:bold}details{margin-top:12px}
@media(max-width:850px){.comparison{grid-template-columns:1fr}.subject{border:0;position:static}.references{grid-template-columns:repeat(3,minmax(100px,1fr))}}
</style></head><body><header>
<h1>Likeness reassessment: what the baseline currently does</h1>
<p class="notice"><strong>No new grouping rules have run. No photos have moved.</strong>
This is a review packet of final preview11 placements, not proposed replacements or an improved result.</p>
<h2>Start here</h2><ol>
<li>Start with Angelica, then choose Mira, Freya, Uma, Gaia or another Vale from the selector.
Every named seed has examples; neighbour cases broaden the context.</li>
<li>Compare the subject at left with each reference at right. Switch to full photos for outfit/hair context;
click any image for the installed original. Face-vector diversity is not a measured pose label.</li>
<li>Optionally mark a few individual pairs Same person / Different person / Uncertain.
References may themselves be mixed; judge each pair, not the entire folder.
You do not need to review all {{COUNT}} cases.</li>
<li>Export your labels before closing. Export prepares visible JSON you can copy, plus a download link
if your browser supports local downloads. Nothing is saved automatically and no choice changes the library.
You can import the exported JSON later into this same packet.</li></ol>
<p>Names and family associations are search seeds, not truth. Scores are cosine similarity, not confidence percentages.
Own scores use leave-one-out evidence; rival scores use frozen final cores. Individual reference-pair scores are a third,
separately labelled comparison. These may disagree without being the same measurement.</p>
<p>No clothing, hairstyle or apparent-age classifier ran. Supported different views are selected by stored face-vector
diversity only. Labels/held-out groups and numeric acceptance criteria are still to be agreed before tuning.</p>
<details><summary>Verified numerical boundary</summary><p>{{PARITY}}</p>
<p>All eligible baseline identities remain in final audit competition, not only Vales. Saved rivals list only the top three.
The packet samples those results; it does not rerun final routing or certify current identities.</p></details></header>
<nav><label>Show <select id="filter"><option value="Angels/angelica">Start: Angelica</option>
<option value="all">All cases</option><option value="neighbours">Neighbour cases</option>{{OPTIONS}}</select></label>
<button id="mode" type="button">Show full photos</button><button id="previous" type="button">Previous</button>
<button id="next" type="button">Next</button><span id="position"></span>
<button id="export" type="button">Export labels</button><label>Import labels <input id="import" type="file" accept=".json"></label>
<span id="progress" class="status"></span><span id="message" role="status"></span></nav>
<details id="export-panel" style="max-width:1550px;margin:0 auto 24px"><summary>Prepared label export</summary>
<p><a id="download" download="likeness-review-labels.json">Download JSON</a>, or copy the text below into a JSON file.
Downloads may be blocked by an embedded browser; the visible text contains the same complete labels.</p>
<textarea id="export-json" readonly rows="8" aria-label="Exported label JSON"></textarea></details>
<main>{{CARDS}}</main><script type="application/json" id="packet-data">{{DATA}}</script>
<script>
"use strict";
const data=JSON.parse(document.getElementById("packet-data").textContent);
const cards=[...document.querySelectorAll("article")], filter=document.getElementById("filter");
const seedFolders=new Set([...filter.options].slice(3).map(o=>o.value));
let offset=0;const pageSize=3;
function show(){
 const eligible=cards.filter(c=>filter.value==="all"||(filter.value==="neighbours"?!seedFolders.has(c.dataset.folder):c.dataset.folder===filter.value));
 if(offset>=eligible.length)offset=0;
 cards.forEach(c=>c.hidden=true);eligible.slice(offset,offset+pageSize).forEach(c=>c.hidden=false);
 document.getElementById("position").textContent=eligible.length?`${offset+1}-${Math.min(offset+pageSize,eligible.length)} / ${eligible.length} cases`:"No cases";
 document.getElementById("previous").disabled=offset===0;
 document.getElementById("next").disabled=offset+pageSize>=eligible.length;
}
filter.addEventListener("change",()=>{offset=0;show()});
document.getElementById("previous").onclick=()=>{offset=Math.max(0,offset-pageSize);show()};
document.getElementById("next").onclick=()=>{offset+=pageSize;show()};
document.getElementById("mode").onclick=e=>{
 const full=document.body.classList.toggle("full-mode");e.target.textContent=full?"Show face crops":"Show full photos";
};
function progress(){
 const done=[...document.querySelectorAll("[data-pair]")].filter(s=>s.value!=="unreviewed").length;
 document.getElementById("progress").textContent=`${done} pairs reviewed (optional)`;
}
document.querySelectorAll("[data-pair]").forEach(s=>s.addEventListener("change",progress));
function labels(){
 return {schemaVersion:1,packetSHA256:data.packetSHA256,binding:data.binding,decisions:data.cases.map(c=>({
  caseId:c.id,photoId:c.photoId,pairs:c.references.map(pid=>({
   referencePhotoId:pid,label:[...document.querySelectorAll("[data-pair]")].find(s=>s.dataset.pair===`${c.id}|${pid}`).value
  })),note:document.querySelector(`[data-note="${c.id}"]`).value
 }))};
}
let exportURL=null;
document.getElementById("export").onclick=()=>{
 const text=JSON.stringify(labels(),null,2)+"\n";
 document.getElementById("export-json").value=text;
 if(exportURL)URL.revokeObjectURL(exportURL);
 exportURL=URL.createObjectURL(new Blob([text],{type:"application/json"}));
 document.getElementById("download").href=exportURL;
 document.getElementById("export-panel").open=true;
 document.getElementById("message").textContent="Export prepared below. Download JSON or copy the text; nothing has been saved automatically.";
 document.getElementById("export-panel").scrollIntoView({block:"start"});
};
document.getElementById("import").onchange=async e=>{
 try{
  const file=e.target.files[0];if(!file)return;
  const incoming=JSON.parse(await file.text()), allowed=new Set(["unreviewed","same","different","uncertain"]);
  if(incoming.schemaVersion!==1||incoming.packetSHA256!==data.packetSHA256||
     JSON.stringify(incoming.binding)!==JSON.stringify(data.binding))throw Error("Labels belong to a different packet.");
  if(!Array.isArray(incoming.decisions)||incoming.decisions.length!==data.cases.length)throw Error("Case count differs.");
  const staged=[],seen=new Set();
  for(const entry of incoming.decisions){
   const expected=data.cases.find(c=>c.id===entry.caseId);
   if(!expected||seen.has(entry.caseId)||expected.photoId!==entry.photoId||typeof entry.note!=="string"||
      !Array.isArray(entry.pairs)||entry.pairs.length!==expected.references.length)throw Error("Case binding differs.");
   seen.add(entry.caseId);const refs=new Set();
   for(const pair of entry.pairs){
    if(!expected.references.includes(pair.referencePhotoId)||refs.has(pair.referencePhotoId)||!allowed.has(pair.label))throw Error("Invalid pair label.");
    refs.add(pair.referencePhotoId);
   }staged.push(entry);
  }
  for(const entry of staged){
   document.querySelector(`[data-note="${entry.caseId}"]`).value=entry.note;
   for(const pair of entry.pairs)[...document.querySelectorAll("[data-pair]")].find(s=>s.dataset.pair===`${entry.caseId}|${pair.referencePhotoId}`).value=pair.label;
  }progress();document.getElementById("message").textContent="Labels imported. No library changes.";
 }catch(error){document.getElementById("message").textContent=`Import refused: ${error.message}`;}
};
show();progress();
</script></body></html>
"""
