"""Whole-library candidate browsing; authored fiction never feeds matching."""
import collections
import hashlib
import html
import json
import pathlib


def validate_candidate(candidate, run):
    rows = candidate["rows"]
    photos = {row["photoId"] for row in run["photos"]}
    if len(photos) != len(run["photos"]) or {row["photoId"] for row in rows} != photos or len(rows) != len(photos):
        raise ValueError("general candidate does not conserve unique receipt photos")
    identities = {item["identityId"]: item for item in candidate["identities"]}
    folders = {item["folder"] for item in candidate["identities"]}
    if len(identities) != len(candidate["identities"]) or len(folders) != len(identities):
        raise ValueError("general candidate identity IDs/folders are not unique")
    for row in rows:
        if row["currentFolder"] not in folders or row["candidateFolder"] is not None and row["candidateFolder"] not in folders:
            raise ValueError("general candidate refers to unknown identity")
        if row["execution"] != "not-authorized" or row["reconsiderable"] is not True:
            raise ValueError("general candidate must stay non-executable and reconsiderable")
        if row["origin"] not in {"explicit-intent", "automatic-hypothesis", "baseline"}:
            raise ValueError("general candidate has unknown evidence origin")
    for identity in identities.values():
        if not set(identity["referencePhotoIds"]) <= photos:
            raise ValueError("general candidate reference IDs are unknown")
    grouped = set()
    group_ids = set()
    for group in candidate["appearances"]:
        if (group["identityId"] not in identities or group["groupId"] in group_ids
                or not set(group["photoIds"]) <= photos
                or len(set(group["photoIds"])) != len(group["photoIds"])
                or grouped.intersection(group["photoIds"])):
            raise ValueError("general candidate appearance IDs or membership are invalid")
        grouped.update(group["photoIds"])
        group_ids.add(group["groupId"])
    for relation in candidate["associations"]:
        ids = relation["identityIds"]
        if (len(ids) != 2 or ids[0] == ids[1] or not set(ids) <= identities.keys()
                or relation["role"] is not None or relation["kind"] != "lookalike"):
            raise ValueError("automatic association cannot infer family roles or merge identity")


def select_photos(candidate, *, maximum=160):
    """Bound rendered pixels, never the evaluated population or browsable records."""
    if maximum < 1:
        raise ValueError("realignment display budget must be positive")
    rows = {row["photoId"]: row for row in candidate["rows"]}
    selected = []

    def add(pid):
        if pid not in rows:
            raise ValueError(f"unknown realignment display photo: {pid}")
        if pid not in selected and len(selected) < maximum:
            selected.append(pid)

    for row in candidate["rows"]:
        if row["candidateFolder"] and row["candidateFolder"] != row["currentFolder"]:
            add(row["photoId"])
            for evidence in row["evidence"]["topCandidates"][:1]:
                for pid in evidence.get("referencePhotoIds", [])[:2]:
                    add(pid)
    for identity in candidate["identities"]:
        for pid in identity["referencePhotoIds"][:1]:
            add(pid)
    for row in candidate["rows"]:
        if row["state"] in {"unresolved", "tentative"}:
            add(row["photoId"])
    return sorted(selected)


def assessment_sample(candidate, *, maximum=24):
    """Diversify a diagnostic review window without restricting evaluated candidates."""
    if maximum < 1:
        raise ValueError("assessment sample budget must be positive")
    categories = collections.defaultdict(list)
    for row in candidate["rows"]:
        if (row["origin"] == "automatic-hypothesis" and row["candidateFolder"]
                and row["candidateFolder"] != row["currentFolder"]):
            category = row["currentFolder"].split("/", 1)[0]
            categories[category].append(row)
    for rows in categories.values():
        rows.sort(key=lambda row: (len(row["blockers"]), row["photoId"]))
    selected, seen_folders = [], set()
    while len(selected) < maximum:
        added = False
        for category in sorted(categories):
            rows = categories[category]
            index = next((i for i, row in enumerate(rows) if row["currentFolder"] not in seen_folders), None)
            if index is None:
                continue
            row = rows.pop(index)
            selected.append(row["photoId"])
            seen_folders.add(row["currentFolder"])
            added = True
            if len(selected) == maximum:
                break
        if not added:
            break
    return selected


def impact_summary(candidate, run):
    audit = {row["photoId"]: row for row in run["finalMembershipAudit"]["rows"]}
    if len(audit) != len(run["photos"]) or set(audit) != {row["photoId"] for row in candidate["rows"]}:
        raise ValueError("realignment impact conservation differs")
    changed = [
        row for row in candidate["rows"]
        if row["candidateFolder"] and row["candidateFolder"] != row["currentFolder"]
    ]
    proposed_references = {
        item["folder"]: set(item["referencePhotoIds"]) for item in candidate["identities"]
    }
    original_references = collections.defaultdict(set)
    for row in run["finalMembershipAudit"]["rows"]:
        if row.get("coreMember"):
            folder = "/".join(pathlib.PurePosixPath(row["destination"]).parts[:-2])
            original_references[folder].add(row["photoId"])
    reference_changes = []
    for folder in sorted(proposed_references.keys() | original_references.keys()):
        before, after = original_references[folder], proposed_references.get(folder, set())
        if before != after:
            reference_changes.append({
                "folder": folder, "baselineCount": len(before), "candidateCount": len(after),
                "additionCount": len(after - before), "withdrawalCount": len(before - after),
                "interpretation": "Reconstructed provisional evidence, not proof withdrawn photos are another person.",
            })
    return {
        "crossFolderByOrigin": dict(sorted(collections.Counter(row["origin"] for row in changed).items())),
        "referenceChangedIdentityCount": len(reference_changes),
        "referenceChangeTotals": {
            "additions": sum(item["additionCount"] for item in reference_changes),
            "withdrawals": sum(item["withdrawalCount"] for item in reference_changes),
        },
        "referenceChanges": reference_changes,
        "selectedPhotoConflicts": [
            {"photoId": row["photoId"], "from": row["currentFolder"], "to": row["candidateFolder"],
             "action": "requires explicit selection invalidation/rebinding before installation"}
            for row in changed if audit[row["photoId"]]["workflowSelected"]
        ],
        "referenceNeededFolders": [item["folder"] for item in candidate["identities"] if item["referenceNeeded"]],
        "interpretation": "Candidate hypotheses, not accepted recoveries; zero installed changes.",
        "remainingGates": [
            "User review of general hypotheses, reference loss and the identity/appearance distinction.",
            "Leakage-safe labels and agreed false-merge/recovery/churn/resource acceptance before tuning or installation.",
            "Secondary appearance descriptors only if separately justified; face-view groups are not outfit/session detection.",
            "Runtime reference growth, incremental dependency closure, category/readiness and complete routing acceptance.",
            "Physical group/derivative/path migration and reversible workflow invalidation need separate consumer verification.",
        ],
    }


def comparison_photos(candidate, run):
    """Keep the questioned photo separate from both identities' reference examples."""
    photos = {row["photoId"]: row for row in run["photos"]}
    identities = {item["folder"]: item for item in candidate["identities"]}
    result = {}
    for row in candidate["rows"]:
        pid = row["photoId"]
        query = photos[pid]
        query_hash = query.get("preparedSHA256") or query.get("sha256")

        def examples(ids):
            return list(dict.fromkeys(
                ref for ref in ids if ref != pid
                and (not query_hash or (
                    photos[ref].get("preparedSHA256") or photos[ref].get("sha256")
                ) != query_hash)
            ))

        target = row["candidateFolder"]
        evidence = next(
            (item for item in row["evidence"]["topCandidates"] if item["folder"] == target), None,
        )
        result[pid] = {
            "current": examples(identities[row["currentFolder"]]["referencePhotoIds"]),
            "target": examples(
                evidence["referencePhotoIds"] if evidence is not None
                else identities[target]["referencePhotoIds"] if target else []
            ),
        }
    return result


def render(candidate, images, run, *, evaluation):
    root = pathlib.Path(run["workingRoot"])
    sources = {}
    for row in run["photos"]:
        destination = pathlib.PurePosixPath(row["destination"])
        if destination.is_absolute() or ".." in destination.parts:
            raise ValueError("unsafe realignment source destination")
        sources[row["photoId"]] = root.joinpath(*destination.parts).as_uri()
    payload = {
        "candidate": candidate, "images": images, "sources": sources,
        "evaluation": evaluation, "impact": impact_summary(candidate, run),
        "assessmentSample": assessment_sample(candidate),
        "comparisons": comparison_photos(candidate, run),
    }
    digest = hashlib.sha256(json.dumps(candidate, sort_keys=True).encode()).hexdigest()
    payload["candidateSHA256"] = digest
    data = json.dumps(payload, allow_nan=False).replace("<", "\\u003c")
    summary = html.escape(json.dumps(candidate["summary"], indent=2))
    return TEMPLATE.replace("{{DATA}}", data).replace("{{SUMMARY}}", summary)


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Review proposed photo matches</title><style>
body{background:#15191f;color:#e3e8ef;font:16px system-ui;line-height:1.45;margin:20px}
main{max-width:1450px;margin:auto}a{color:#8fceff}button,input,select,textarea{font:inherit;padding:7px;max-width:100%}
nav{position:sticky;top:0;background:#252e39;z-index:2;padding:10px;display:flex;flex-wrap:wrap;gap:12px}
.notice{border-left:4px solid #dfb55d;background:#272c34;padding:12px}.scroll{max-height:520px;overflow:auto}
table{border-collapse:collapse;font-size:14px;width:100%}td,th{border:1px solid #536071;padding:7px;text-align:left}
tbody tr{cursor:pointer}tbody tr:hover{background:#283849}pre{white-space:pre-wrap;overflow-wrap:anywhere}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
figure{margin:0;padding:10px;background:#222a34;overflow-wrap:anywhere}img{object-fit:contain;max-width:100%;height:280px}
small{display:block;color:#b9c9dc}section{margin:22px 0}[hidden]{display:none!important}.active{outline:2px solid #93d0ff}
.comparison{display:grid;grid-template-columns:1fr 1.3fr 1fr;gap:16px}
.comparison>section{min-width:0;background:#1d2630;padding:12px;margin:12px 0}
.comparison .grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.comparison img{height:240px;width:100%}.comparison #query-photos img{height:480px}
.comparison #query-photos{display:block}.toolbar,.answers{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.answers button{padding:14px;font-weight:600;flex:1;min-width:200px}
button{cursor:pointer}button:disabled{cursor:default;opacity:.5}button[aria-pressed="true"]{outline:3px solid #93d0ff}
.primary{background:#b4dbff;color:#101923;border:1px solid #b4dbff}
details{margin:16px 0}summary{cursor:pointer;font-weight:600}
#review-question{font-size:1.35rem}#review-progress{font-weight:600}
#assessment-json,#family-json{display:block;width:95%}
@media(max-width:850px){.comparison{grid-template-columns:1fr}.comparison #query-photos img{height:360px}}
</style></head><body><main>
<h1>Review proposed photo matches</h1>
<p><strong>Your task: decide whether the photo being checked shows the same person as the suggested identity.</strong>
We are testing whether the system finds real scattered appearances or just similar-looking people.</p>
<p class="notice"><strong>No photos will move and no Review locks will be added.</strong>
These suggestions are not approved matches. Your answers help identify which matching rules need work;
they do not automatically change or train the matcher.</p>
<ol><li>Compare the <strong>photo being checked</strong> with the <strong>suggested identity examples</strong>.
The current identity is shown separately for context, not as ground truth.</li>
<li>Choose <strong>Same person</strong>, <strong>Different person</strong> or <strong>Cannot tell</strong>.
Each answer is recorded in this page and advances to the next case. Back lets you revise.</li>
<li>Use <strong>Download answers</strong> whenever you stop, even partway through.
Keep that JSON file and send it back. Unexported answers are lost if you close or refresh.</li></ol>
<section id="guided-review" aria-label="Guided photo comparison">
<div class="toolbar"><button id="review-back">Back</button>
<label>Case <select id="review-case"></select></label>
<button id="review-next">Next / skip without answering</button>
<button id="review-resume">Next unanswered</button>
<label>Images <select id="image-mode"><option value="full">Full photos</option><option value="face">Face crops when available</option></select></label></div>
<p id="review-progress" role="status"></p><p id="review-proposal"></p>
<p id="review-status" class="notice"></p>
<h2 id="review-question"></h2>
<p>Examples are a small sample of the matching references, not verified identity truth.
Click any image to open its original. If the examples disagree or are insufficient, choose Cannot tell.</p>
<div id="photos" class="comparison">
<section><h3>1. Photo being checked</h3><div id="query-photos"></div><small id="query-caption"></small></section>
<section><h3>2. Suggested identity examples</h3><p id="target-caption"></p>
<div id="target-photos" class="grid"></div><button id="target-more">Show all suggested references</button></section>
<section><h3>3. Current identity examples (context only)</h3><p id="current-caption"></p>
<div id="current-photos" class="grid"></div><button id="current-more">Show all current references</button></section>
</div>
<p id="assessment-selected"></p>
<div class="answers"><button data-judgment="support">Same person — record &amp; next</button>
<button data-judgment="reject">Different person — record &amp; next</button>
<button data-judgment="uncertain">Cannot tell — record &amp; next</button></div>
<p>Same person supports only the suggested match. Different person rejects only that match—it does not confirm the current folder.
Cannot tell records uncertainty, not a rejection. These are identity judgments, not family relationships.</p>
<p id="assessment-status" role="status">No answers recorded. Download before closing or refreshing.</p>
<div class="toolbar"><button id="assessment-download" class="primary">Download answers</button>
<button id="assessment-export">Show answer JSON to copy</button></div>
<details id="answer-transfer"><summary>Resume from exported JSON / copy answers manually</summary>
<p>Paste a previous export below and import it to resume. Import replaces the answers currently in the page;
export your current work first. Exports from candidate-05 also work when the candidate binding is unchanged.</p>
<label>Answer JSON <textarea id="assessment-json" rows="6"></textarea></label>
<button id="assessment-import">Import validated answers</button></details>
<details><summary>Why the system suggested this / technical evidence</summary>
<p>Scores are similarities, not percentages or probabilities. A tentative suggestion may fail several safety checks.
Do not treat a high score as a correct match.</p><pre id="detail"></pre></details>
</section>
<details id="advanced"><summary>Optional: explore the whole library, reference changes and fictional relationships</summary>
<p>The guided sample above is the review task. Everything below is optional technical context.
The sample spans distinct current identities and prioritizes fewer blockers; it is not a random accuracy estimate.</p>
<h2>The outcome layers</h2><ol>
<li><strong>Identity:</strong> the current person/candidate identity remains a first-class record, not a character-only slot.</li>
<li><strong>References:</strong> independently proposed matching evidence, not all Gallery photos and not placement protection.</li>
<li><strong>Appearances:</strong> bounded face-view hypotheses within the current identity. Not measured outfits/sessions or verified same-person albums.</li>
<li><strong>Associations:</strong> resemblance between separate identities; fictional family roles are authored, never inferred kinship.</li>
<li><strong>Too close to call:</strong> reconsiderable uncertainty; no new Review bucket or automatic lock is created.</li></ol>
<h2>Start here</h2><p id="headline"></p>
<ol><li>Use <strong>Cross-folder proposals</strong> and origin <strong>automatic-hypothesis</strong>
to see new machine proposals, separate from your earlier answers. Select a row to compare the photo and references.</li>
<li>Select an identity to see its matching references, face-view groups, unresolved members and links to separate lookalikes.</li>
<li>Assess whether this candidate is moving toward your intended organization. It is not ready to install merely because it runs.</li></ol>
<p><a href="realignment.json">Complete candidate JSON</a> |
<a href="evaluation.json">Evidence-blinded diagnostic</a> |
<a href="index.html">Earlier frozen-reference control</a></p>
<details><summary>Counts, experimental recipe, costs and limits</summary><pre>{{SUMMARY}}</pre><pre id="recipe"></pre>
<pre id="limits"></pre></details>
<section><h2>What changed, and what still needs acceptance</h2><p id="impact-headline"></p>
<p>Inspect automatic cross-folder hypotheses and identities losing reference support first.
No category/name, physical group folder, selection or production change is installed.
New appearance descriptors, full incremental/routing acceptance and physical-path compatibility remain separately gated.</p>
<details><summary>Per-identity reference changes, workflow conflicts and remaining gates</summary><pre id="impacts"></pre></details>
<details><summary>Label-blinded evaluation (not independent series-held-out accuracy)</summary><pre id="evaluation"></pre></details></section>
<nav><label>Identity <select id="identity"><option value="">All identities</option></select></label>
<label>Member state <select id="state"><option value="">All states</option></select></label>
<label>Origin <select id="origin"><option value="">All origins</option><option>automatic-hypothesis</option>
<option>explicit-intent</option><option>baseline</option></select></label>
<label>Search <input id="search" type="search" placeholder="Photo, folder, group or reason"></label>
<button id="changes">Cross-folder proposals</button><button id="sample">Suggested assessment sample</button>
<button id="reset">Reset</button></nav>
<section><h2>Identity and reference landscape</h2><p id="identity-count" role="status"></p><div class="scroll">
<table><thead><tr><th>Identity / current folder</th><th>References</th><th>Status</th><th>Reference needed</th>
<th>Face-view groups</th></tr></thead><tbody id="identities"></tbody></table></div></section>
<section><h2>Members: current home versus candidate</h2><p id="member-count" role="status"></p><div class="scroll">
<table><thead><tr><th>Photo</th><th>Current identity</th><th>Candidate identity</th><th>State / origin</th>
<th>Reference eligible</th><th>Reason / safeguards</th></tr></thead><tbody id="members"></tbody></table></div>
</section>
<section><h2>Face-view appearance hypotheses</h2><p>No whole group is automatically merged or admitted.
Groups preserve current identity lineage; a cross-folder member proposal does not silently relocate its group.</p>
<div class="scroll"><table><thead><tr><th>Group</th><th>Identity</th><th>Photos</th><th>Evidence</th></tr></thead>
<tbody id="appearances"></tbody></table></div></section>
<section><h2>Separate lookalikes and fictional associations</h2>
<p>These are links between separate identity records, not merges. Suggested resemblance is not a real family relationship.
You may author fictional sister, mother, daughter or cousin roles for the game world. Saving/exporting a draft never changes matching.</p>
<div class="scroll"><table><thead><tr><th>Identity A</th><th>Identity B</th><th>Evidence / role</th></tr></thead>
<tbody id="associations"></tbody></table></div>
<h3>Optional authored fictional relationship draft</h3>
<label>From <select id="family-from"></select></label> <label>To <select id="family-to"></select></label>
<label>Fictional role of From relative to To <select id="family-role"><option value="sister">Sister</option>
<option value="mother">Mother</option><option value="daughter">Daughter</option><option value="cousin">Cousin</option></select></label>
<button id="family-add">Add / replace authored draft</button><button id="family-clear">Clear draft</button>
<button id="family-export">Export draft to text</button>
<p id="family-status" role="status">No roles inferred. Draft export is optional, not another required review assignment.</p>
<pre id="family-draft"></pre><label>Export/import JSON <textarea id="family-json" rows="5"></textarea></label>
<button id="family-import">Import validated draft</button>
<p>Copy an optional export into feedback. It is not automatically applied to the library or interpreted as biological kinship.</p></section>
<p>Fictional relationship edits live only in this page until exported; refresh discards unexported drafts.
They never change reference eligibility, membership, categories or protection.</p>
<pre id="explorer-detail">Select an identity, group or association to inspect its technical record.</pre>
</details></main><script id="data" type="application/json">{{DATA}}</script><script>
"use strict";
const data=JSON.parse(document.getElementById("data").textContent),c=data.candidate;
const el=id=>document.getElementById(id),text=(id,value)=>{
 const content=typeof value==="string"?value:JSON.stringify(value,null,2);
 if(el(id).tagName==="TEXTAREA")el(id).value=content;else el(id).textContent=content;
};
const identities=new Map(c.identities.map(i=>[i.identityId,i])),byPhoto=new Map(c.rows.map(r=>[r.photoId,r]));
let changesOnly=false,sampleOnly=false,authored=[],selectedPhoto=null,assessments=[],dirty=false;
let allTarget=false,allCurrent=false;
const sampleIds=new Set(data.assessmentSample);
function option(select,value,label){const o=document.createElement("option");o.value=value;o.textContent=label;select.append(o);}
for(const i of c.identities){
 option(el("identity"),i.folder,i.folder);option(el("family-from"),i.identityId,i.folder);option(el("family-to"),i.identityId,i.folder);
}
for(const state of [...new Set(c.rows.map(r=>r.state))].sort())option(el("state"),state,state);
option(el("review-case"),"","Outside guided sample");
for(const [i,pid] of data.assessmentSample.entries()){
 const r=byPhoto.get(pid);option(el("review-case"),pid,(i+1)+". "+r.currentFolder+" → "+r.candidateFolder);
}
if(el("family-to").options.length>1)el("family-to").selectedIndex=1;
text("recipe",c.recipe);text("limits",c.limits);text("impacts",data.impact);text("evaluation",data.evaluation);
text("impact-headline",data.impact.referenceChangedIdentityCount+" identities have changed provisional reference sets; "+
 data.impact.referenceChangeTotals.additions+" proposed reference additions and "+
 data.impact.referenceChangeTotals.withdrawals+" withdrawals. Withdrawals are not automatically different-person judgments. "+
 data.impact.selectedPhotoConflicts.length+" managed workflow selections have cross-folder candidate conflicts.");
const cross=c.rows.filter(r=>r.candidateFolder&&r.candidateFolder!==r.currentFolder);
text("headline",c.rows.length+" photos across "+c.identities.length+" current identities; "+
 c.appearances.length+" face-view groups; "+
 cross.filter(r=>r.origin==="automatic-hypothesis").length+" automatic cross-folder hypotheses and "+
 cross.filter(r=>r.origin==="explicit-intent").length+" explicit-answer cross-folder proposals. "+
 cross.filter(r=>r.origin==="automatic-hypothesis"&&!r.blockers.length).length+
 " automatic proposals clearing every safeguard. "+
 c.identities.filter(i=>i.referenceNeeded).length+" identities need stronger reference support. No installed moves.");
function tableRow(body,values,click){const tr=document.createElement("tr");for(const value of values){
 const td=document.createElement("td");td.textContent=String(value??"");tr.append(td);}
 if(click){tr.tabIndex=0;tr.onclick=click;tr.onkeydown=e=>{if(e.key==="Enter")click();};}body.append(tr);return tr;}
function progress(message){
 const done=data.assessmentSample.filter(pid=>assessments.some(a=>a.photoId===pid)).length;
 const index=data.assessmentSample.indexOf(selectedPhoto);
 text("review-progress",(index<0?"Outside guided sample":"Case "+(index+1)+" of "+sampleIds.size)+
  " | "+done+" of "+sampleIds.size+" sample cases answered | "+assessments.length+" answers in this page.");
 text("assessment-status",message||(
  done===sampleIds.size&&sampleIds.size?"Sample complete. Download your answers to keep and return them.":
  "You can stop at any point. Download your answers before closing or refreshing."));
 el("review-case").value=index<0?"":selectedPhoto;
 el("review-back").disabled=index<=0;el("review-next").disabled=index<0||index>=sampleIds.size-1;
 el("review-resume").disabled=done===sampleIds.size;
 el("assessment-download").disabled=!assessments.length;
 for(const button of document.querySelectorAll("[data-judgment]")){
  const saved=assessments.find(a=>a.photoId===selectedPhoto);
  button.disabled=!byPhoto.get(selectedPhoto)?.candidateFolder;
  button.setAttribute("aria-pressed",String(saved?.judgment===button.dataset.judgment));
 }
}
function figure(id,body){
 const source=data.sources[id],fig=document.createElement("figure"),cap=document.createElement("figcaption");
 if(!source){cap.textContent="Image source unavailable: "+id;fig.append(cap);body.append(fig);return;}
 const link=document.createElement("a"),img=document.createElement("img");
 link.href=source;link.target="_blank";link.rel="noopener";
 const face=el("image-mode").value==="face";
 img.src=(face?data.images[id]?.face:data.images[id]?.full)||data.images[id]?.full||source;
 img.alt=(face&&data.images[id]?.face?"Face crop ":"Full photo ")+id;img.loading="lazy";
 link.append(img);cap.textContent=id+(face&&!data.images[id]?.face?" — No face crop available; showing full photo.":"");
 img.onerror=()=>{img.hidden=true;cap.textContent="Image unavailable: "+id+". Use the source link; no substitute image was selected.";link.textContent="Open original source";};
 fig.append(link,cap);body.append(fig);
}
function drawComparison(){
 const r=byPhoto.get(selectedPhoto);if(!r)return;
 const refs=data.comparisons[selectedPhoto];
 el("query-photos").replaceChildren();figure(selectedPhoto,el("query-photos"));
 for(const [side,ids,all] of [["target",refs.target,allTarget],["current",refs.current,allCurrent]]){
  const body=el(side+"-photos");body.replaceChildren();
  for(const id of all?ids:ids.slice(0,4))figure(id,body);
  if(!ids.length){const p=document.createElement("p");p.textContent="No other usable reference examples. Do not infer identity from the folder name; Cannot tell is appropriate.";body.append(p);}
  el(side+"-more").hidden=ids.length<=4;
  el(side+"-more").textContent=all?"Show fewer references":"Show all "+ids.length+" references";
 }
 text("query-caption","Currently filed under "+r.currentFolder+". This location may be wrong.");
 text("target-caption",r.candidateFolder||"No suggested identity");
 text("current-caption",r.currentFolder+" — not assumed correct");
}
function showPhoto(pid){
 const r=byPhoto.get(pid);text("detail",r);
 selectedPhoto=pid;allTarget=false;allCurrent=false;
 text("review-proposal","Currently: "+r.currentFolder+" → Suggested: "+(r.candidateFolder||"unresolved"));
 text("review-question",r.candidateFolder?"Does the photo being checked show the same person as "+r.candidateFolder+"?":
  "No target is proposed for this photo. There is no match to judge.");
 text("review-status",r.origin==="automatic-hypothesis"?
  (r.blockers.length?"Tentative computer suggestion — NOT approved. "+r.blockers.length+
   " safety checks block automatic placement. Your task is visual identity comparison, not approval of those checks.":
   "Computer suggestion clears the experimental checks, but no move is authorized. Your visual judgment is still needed."):
  r.origin==="explicit-intent"?"This proposal comes from your earlier answers, not a new automatic discovery.":
  "This is baseline placement information, not a newly discovered automatic match.");
 const saved=assessments.find(a=>a.photoId===pid);
 const labels={support:"Same person",reject:"Different person",uncertain:"Cannot tell"};
 text("assessment-selected",!r.candidateFolder?"No proposed match to judge. Use Next unanswered to return to the sample.":
  saved?"Your recorded answer: "+labels[saved.judgment]+". You can change it below.":"Not answered yet. Choose one answer below, or skip.");
 drawComparison();progress();
}
el("image-mode").onchange=drawComparison;
el("target-more").onclick=()=>{allTarget=!allTarget;drawComparison();};
el("current-more").onclick=()=>{allCurrent=!allCurrent;drawComparison();};
el("review-case").onchange=()=>{if(el("review-case").value)showPhoto(el("review-case").value);};
el("review-back").onclick=()=>showPhoto(data.assessmentSample[data.assessmentSample.indexOf(selectedPhoto)-1]);
el("review-next").onclick=()=>showPhoto(data.assessmentSample[data.assessmentSample.indexOf(selectedPhoto)+1]);
el("review-resume").onclick=()=>{
 const pid=data.assessmentSample.find(id=>!assessments.some(a=>a.photoId===id));if(pid)showPhoto(pid);
};
function refresh(){
 const folder=el("identity").value,state=el("state").value,origin=el("origin").value,q=el("search").value.trim().toLowerCase();
 const visible=c.rows.filter(r=>(!folder||r.currentFolder===folder||r.candidateFolder===folder)&&
  (!state||r.state===state)&&(!origin||r.origin===origin)&&
  (!changesOnly||r.candidateFolder&&r.candidateFolder!==r.currentFolder)&&
  (!sampleOnly||sampleIds.has(r.photoId))&&
  (!q||JSON.stringify(r).toLowerCase().includes(q)));
 el("members").replaceChildren();
 for(const r of visible)tableRow(el("members"),[r.photoId,r.currentFolder,r.candidateFolder||"Unresolved",
  r.state+" / "+r.origin,r.referenceEligible,r.reason+" | "+r.blockers.join(", ")],()=>{
   showPhoto(r.photoId);el("guided-review").scrollIntoView();
  });
 text("member-count",visible.length+" / "+c.rows.length+" members. Cross-folder filter: "+changesOnly+
  ". Assessment sample: "+sampleOnly+". Zero installed moves.");
 const ids=c.identities.filter(i=>!folder||i.folder===folder);el("identities").replaceChildren();
 for(const i of ids)tableRow(el("identities"),[i.folder,i.referencePhotoIds.length,i.referenceStatus,i.referenceNeeded,i.appearanceGroupIds.length],
  ()=>{el("identity").value=i.folder;refresh();text("explorer-detail",i);});
 text("identity-count",ids.length+" / "+c.identities.length+" current identity records; reference reconstruction is provisional.");
 el("appearances").replaceChildren();
 for(const g of c.appearances){const identity=identities.get(g.identityId);if(folder&&identity?.folder!==folder)continue;
  tableRow(el("appearances"),[g.groupId,identity?.folder||g.identityId,g.photoIds.length,g.evidenceKind],()=>{
   text("explorer-detail",g);if(g.photoIds.length)showPhoto(g.photoIds[0]);
  });
 }
 el("associations").replaceChildren();
 for(const a of c.associations){
  const names=(a.identityIds||[]).map(id=>identities.get(id)?.folder||id);
  if(folder&&!names.includes(folder))continue;
  tableRow(el("associations"),[names[0]||"",names[1]||"",a.kind+"; fictional role: "+(a.role||"unassigned")],()=>text("explorer-detail",a));
 }
}
for(const id of ["identity","state","origin"])el(id).onchange=refresh;
el("search").oninput=refresh;el("changes").onclick=()=>{changesOnly=true;refresh();};
el("sample").onclick=()=>{
 for(const id of ["identity","state","origin","search"])el(id).value="";
 changesOnly=false;sampleOnly=true;refresh();
};
el("reset").onclick=()=>{for(const id of ["identity","state","origin","search"])el(id).value="";changesOnly=false;sampleOnly=false;refresh();};
for(const button of document.querySelectorAll("[data-judgment]"))button.onclick=()=>{
 const r=byPhoto.get(selectedPhoto);
 if(!r?.candidateFolder){text("assessment-status","Select a member with a proposed target. Nothing changed.");return;}
 assessments=assessments.filter(a=>a.photoId!==r.photoId);
 assessments.push({photoId:r.photoId,candidateFolder:r.candidateFolder,judgment:button.dataset.judgment});
 dirty=true;
 const index=data.assessmentSample.indexOf(r.photoId);
 if(index>=0&&index<data.assessmentSample.length-1)showPhoto(data.assessmentSample[index+1]);else showPhoto(r.photoId);
 progress("Answer recorded for "+(index<0?r.photoId:"case "+(index+1))+
  ". "+assessments.length+" answers in page only. "+
  (data.assessmentSample.every(id=>assessments.some(a=>a.photoId===id))?"Sample complete. ":"")+
  "Download answers before closing or refreshing.");
 el("review-progress").scrollIntoView({block:"start"});
};
function answerExport(){return {schemaVersion:1,kind:"realignment-hypothesis-assessments",candidateSHA256:data.candidateSHA256,
 assessments:[...assessments].sort((a,b)=>a.photoId.localeCompare(b.photoId))};}
el("assessment-export").onclick=()=>{
 text("assessment-json",answerExport());el("answer-transfer").open=true;
 text("assessment-status","Copy the exported JSON to retain "+assessments.length+" judgments. No library changes.");
};
el("assessment-download").onclick=()=>{
 let url;
 try{
  const content=JSON.stringify(answerExport(),null,2);
  text("assessment-json",content);el("answer-transfer").open=true;
  url=URL.createObjectURL(new Blob([content],{type:"application/json"}));
  const a=document.createElement("a");a.href=url;
  a.download="realignment_answers_"+data.candidateSHA256.slice(0,12)+".json";
  document.body.append(a);a.click();a.remove();
  text("assessment-status","Download requested for "+assessments.length+
   " answers. Check your Downloads folder and keep/send the JSON file. "+
   "The export text is also open below: if this browser does not download files, copy that JSON instead.");
 }catch(error){text("assessment-status","Download failed: "+error.message+". Use Show answer JSON to copy; answers remain in this page.");}
 finally{if(url)setTimeout(()=>URL.revokeObjectURL(url),1000);}
};
addEventListener("beforeunload",event=>{if(dirty){event.preventDefault();event.returnValue="";}});
el("assessment-import").onclick=()=>{
 try{
  const d=JSON.parse(el("assessment-json").value);
  if(Object.keys(d).sort().join(",")!=="assessments,candidateSHA256,kind,schemaVersion"||
    d.schemaVersion!==1||d.kind!=="realignment-hypothesis-assessments"||
    d.candidateSHA256!==data.candidateSHA256||!Array.isArray(d.assessments))throw Error("Assessment binding/schema mismatch");
  const seen=new Set();
  for(const a of d.assessments){
   const r=byPhoto.get(a.photoId);
   if(Object.keys(a).sort().join(",")!=="candidateFolder,judgment,photoId"||!r?.candidateFolder||
     r.candidateFolder!==a.candidateFolder||!["support","reject","uncertain"].includes(a.judgment)||
     seen.has(a.photoId))throw Error("Invalid or duplicate assessment");
   seen.add(a.photoId);
  }
  assessments=d.assessments;
  dirty=false;
  if(selectedPhoto)showPhoto(selectedPhoto);
  progress(assessments.length+" validated answers imported. Use Next unanswered to resume. No library changes.");
 }catch(error){text("assessment-status","Import refused: "+error.message+". Existing judgments unchanged.");}
};
function draft(){text("family-draft",authored);}
el("family-add").onclick=()=>{
 const from=el("family-from").value,to=el("family-to").value,role=el("family-role").value;
 if(from===to){text("family-status","Choose two distinct identities. Nothing changed.");return;}
 authored=authored.filter(r=>r.from!==from||r.to!==to);
 authored.push({from,to,role,provenance:"user-authored-fiction",status:"draft"});
 draft();text("family-status","Authored fictional draft only. No matching, identity or protection change.");
};
el("family-clear").onclick=()=>{authored=[];draft();text("family-status","Draft cleared; library unchanged.");};
el("family-export").onclick=()=>{
 text("family-json",{schemaVersion:1,kind:"fictional-association-draft",candidateSHA256:data.candidateSHA256,relationships:authored});
 text("family-status","Copy the JSON if you want to retain this optional draft. No library changes.");
};
el("family-import").onclick=()=>{
 try{
  const d=JSON.parse(el("family-json").value),keys=Object.keys(d).sort().join(",");
  if(keys!=="candidateSHA256,kind,relationships,schemaVersion"||d.schemaVersion!==1||d.kind!=="fictional-association-draft"||
    d.candidateSHA256!==data.candidateSHA256||!Array.isArray(d.relationships))throw Error("Draft binding/schema mismatch");
  const seen=new Set();
  for(const r of d.relationships){
   if(Object.keys(r).sort().join(",")!=="from,provenance,role,status,to"||!identities.has(r.from)||!identities.has(r.to)||r.from===r.to||
    !["sister","mother","daughter","cousin"].includes(r.role)||r.provenance!=="user-authored-fiction"||r.status!=="draft")throw Error("Invalid fictional relationship");
   const k=r.from+"|"+r.to;if(seen.has(k))throw Error("Duplicate relationship");seen.add(k);
  }
  authored=d.relationships;draft();text("family-status","Validated draft imported. No library changes.");
 }catch(error){text("family-status","Import refused: "+error.message+". Existing draft unchanged.");}
};
refresh();draft();
if(data.assessmentSample.length)showPhoto(data.assessmentSample[0]);
else{
 text("review-question","No automatic cross-folder cases are available in this sample.");
 progress("No sample to review. The optional whole-library explorer remains available.");
}
</script></body></html>
"""
