"""Character-intent confirmation, distinct from pair resemblance or runtime membership."""
import collections
import html
import json

from . import shadow

CHARACTERS = (
    ("Angels/angelica", "Disputed inherited core; existing anchors and labelled lookalikes", 12),
    ("Angels/Nyxene", "Character comparison requested by the user; sample alongside Drakness", 8),
    ("Sisters/Drakness", "Character comparison requested by the user; broad inherited core", 8),
    ("Angels/Ravaelle", "Diffuse reference support and strong small-seed sensitivity", 8),
    ("Sisters/Draknara", "An original member preferred another cast reference in the source audit", 8),
    ("Sisters/Draknisa", "Higher-coherence contrast; coherence is not identity confirmation", 8),
)
CHOICES = ("unreviewed", "reference", "same-not-reference", "different", "uncertain")


def build_packet(run, vectors, effective, binding, *, characters=CHARACTERS):
    audit = {row["photoId"]: row for row in run["finalMembershipAudit"]["rows"]}
    photos = {row["photoId"]: row for row in run["photos"]}
    eligible = {
        pid: row for pid, row in audit.items()
        if row.get("qualityEligible") and pid in vectors and "/gallery/" in row["destination"]
    }
    if len(photos) != len(run["photos"]) or len(audit) != len(run["finalMembershipAudit"]["rows"]):
        raise ValueError("character packet requires unique saved photo IDs")
    pair_labels = collections.defaultdict(list)
    for pair in effective["pairs"]:
        a, b = pair["photoIds"]
        pair_labels[a].append((b, pair["label"]))
        pair_labels[b].append((a, pair["label"]))
    groups, used = [], set()
    for folder, reason, budget in characters:
        own = sorted(pid for pid, row in eligible.items() if shadow.folder_for(row) == folder)
        if not own:
            raise ValueError(f"character has no eligible installed Gallery photos: {folder}")
        seeds = sorted(pid for pid in own if photos[pid].get("castSeedAnchor"))
        selected = {}

        def add(pid, why):
            selected.setdefault(pid, []).append(why)

        def own_score(pid):
            score = eligible[pid].get("ownScore")
            return score if score is not None else -1.

        for pid in seeds:
            add(pid, "Existing configured anchor; requires your confirmation, not an automatic answer")
        disputed = [
            pid for pid in own if any(
                label == "different" and other in own for other, label in pair_labels[pid]
            )
        ]
        for pid in disputed:
            add(pid, "Previously judged different from at least one current reference here")
        if len(selected) > budget - 2:
            raise ValueError(f"mandatory character evidence exceeds budget for {folder}; expand explicitly")
        strongest = min(own, key=lambda pid: (-own_score(pid), pid))
        add(strongest, "Strong saved own-reference support; not identity truth")
        weakest = min(own, key=lambda pid: (own_score(pid), pid))
        if len(selected) < budget - 2 or weakest in selected:
            add(weakest, "Weak saved own-reference support")
        while len(selected) < min(budget - 2, len(own)):
            remaining = [pid for pid in own if pid not in selected]
            varied = min(remaining, key=lambda pid: (
                max(float(vectors[pid] @ vectors[other]) for other in selected), pid,
            ))
            add(varied, "Different face-vector view within current placement; pose not inferred")
        outside = [pid for pid in eligible if pid not in own]
        reference = shadow.nz(sum(vectors[pid] for pid in own))
        returned = sorted(
            (pid for pid in outside if photos[pid].get("oldFolder") == folder),
            key=lambda pid: (-float(vectors[pid] @ reference), pid),
        )
        if returned and len(selected) < budget:
            add(returned[0], "Originally from this character folder, now elsewhere; not an endorsed return")
        rivals = sorted(outside, key=lambda pid: (-float(vectors[pid] @ reference), pid))
        for pid in rivals:
            if len(selected) >= budget:
                break
            if pid not in selected:
                add(pid, "Strong individual face resemblance outside this folder; not an endorsed match")
        cards = []
        for pid, reasons in selected.items():
            row = eligible[pid]
            observations = [
                {"otherPhotoId": other, "label": label}
                for other, label in pair_labels[pid] if other in own
            ]
            cards.append({
                "photoId": pid, "currentFolder": shadow.folder_for(row),
                "source": photos[pid].get("source"), "reasons": reasons,
                "anchor": bool(photos[pid].get("castSeedAnchor")),
                "coreMember": bool(row.get("coreMember")),
                "pairJudgmentsWithinCurrentFolder": observations,
                "selection": "unreviewed",
            })
        groups.append({
            "folder": folder, "reason": reason, "currentGalleryCount": len(own),
            "cards": cards,
        })
        used.update(selected)
    return {
        "schemaVersion": 1, "kind": "character-reference-confirmation",
        "binding": binding, "workingRoot": run["workingRoot"],
        "characters": groups, "usedPhotoIds": sorted(used),
        "choices": list(CHOICES),
        "boundary": "Character-intent evidence only. No core, placement, protection or workflow changes.",
    }


def validate_answers(packet, answers):
    if (not isinstance(answers, dict)
            or type(answers.get("schemaVersion")) is not int or answers["schemaVersion"] != 1
            or answers.get("kind") != "character-reference-answers"
            or answers.get("packetSHA256") != packet["packetSHA256"]
            or answers.get("binding") != packet["binding"]):
        raise ValueError("character answer packet/binding mismatch")
    expected = {
        group["folder"]: {card["photoId"] for card in group["cards"]}
        for group in packet["characters"]
    }
    groups = answers.get("characters")
    if not isinstance(groups, list) or len(groups) != len(expected):
        raise ValueError("character answer group coverage differs")
    seen = set()
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("folder"), str):
            raise ValueError("invalid character answer group")
        folder = group["folder"]
        if folder in seen or folder not in expected:
            raise ValueError(f"duplicate or unknown character: {folder}")
        seen.add(folder)
        decisions = group.get("decisions")
        if (not isinstance(decisions, list)
                or any(not isinstance(item, dict)
                       or not isinstance(item.get("photoId"), str)
                       or not isinstance(item.get("choice"), str) for item in decisions)
                or len(decisions) != len(expected[folder])
                or {item["photoId"] for item in decisions} != expected[folder]):
            raise ValueError(f"character photo coverage differs: {folder}")
        if any(item["choice"] not in CHOICES for item in decisions):
            raise ValueError(f"unknown character decision: {folder}")
    return answers


def render(packet):
    options, sections = [], []
    for index, group in enumerate(packet["characters"]):
        folder = group["folder"]
        options.append(f'<option value="{index}">{html.escape(folder)} ({len(group["cards"])} photos)</option>')
        cards = []
        for card in group["cards"]:
            pid = card["photoId"]
            image = packet["images"][pid]
            counts = collections.Counter(
                item["label"] for item in card["pairJudgmentsWithinCurrentFolder"]
            )
            card_options = "".join(
                f'<option value="{value}">{text}</option>' for value, text in (
                    ("unreviewed", "Not reviewed"),
                    ("reference", "Defines this character - use as reference"),
                    ("same-not-reference", "Same character - not a reference"),
                    ("different", "Different person from intended character"),
                    ("uncertain", "Uncertain - do not use as reference"),
                )
            )
            cards.append(
                f'<article><a href="{html.escape(image["href"], quote=True)}" target="_blank" rel="noopener">'
                f'<img class="full" src="{image["full"]}" alt="Full photo {html.escape(pid)}">'
                f'<img class="face" src="{image["face"]}" alt="Face {html.escape(pid)}"></a>'
                f'<small>{html.escape(pid)}</small>'
                f'<p>Current home: {html.escape(card["currentFolder"])}<br>'
                f'Configured anchor: {card["anchor"]}; saved core: {card["coreMember"]}</p>'
                f'<p>{"; ".join(html.escape(why) for why in card["reasons"])}</p>'
                f'<p>Previous pair judgments against photos here: {html.escape(str(dict(counts)))}. '
                'Pair judgments do not define the character name.</p>'
                f'<label>Your intended {html.escape(folder)}:'
                f'<select data-character="{index}" data-photo="{html.escape(pid, quote=True)}">'
                f'{card_options}</select></label></article>'
            )
        sections.append(
            f'<section data-group="{index}"{" hidden" if index else ""}>'
            f'<h2>{html.escape(folder)}</h2><p>{html.escape(group["reason"])}. '
            f'{group["currentGalleryCount"]} current eligible Gallery photos; this is a shortlist.</p>'
            f'<div class="grid">{"".join(cards)}</div></section>'
        )
    payload = json.dumps(packet, separators=(",", ":")).replace("<", "\\u003c")
    return TEMPLATE.replace("{{OPTIONS}}", "".join(options)).replace(
        "{{SECTIONS}}", "".join(sections),
    ).replace("{{DATA}}", payload)


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Character reference confirmation</title><style>
body{background:#15191f;color:#e3e8ef;font:16px system-ui;margin:20px;line-height:1.45}
header,main{max-width:1450px;margin:auto}a{color:#8fceff}h1{margin-top:0}
.notice{border-left:4px solid #e6b458;padding:12px;background:#282c32}
nav{position:sticky;top:0;background:#20262e;padding:12px;z-index:2;display:flex;gap:12px;flex-wrap:wrap}
button,select,textarea{font:inherit;padding:8px;max-width:100%}button{cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
article{background:#20262e;border:1px solid #536071;padding:12px;border-radius:6px;overflow-wrap:anywhere}
article a{display:flex;gap:6px;align-items:start}img{object-fit:contain;max-width:100%}
.full{width:72%;height:360px}.face{width:26%;height:150px}body.faces .full{display:none}
body.faces .face{width:100%;height:300px}small{display:block;color:#b7c8db}label{display:block}
label select{width:100%}textarea{width:95%;min-height:160px}[hidden]{display:none!important}
#status{font-weight:bold}#error{color:#ffb4a9;white-space:pre-wrap}
@media(max-width:850px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:550px){.grid{grid-template-columns:1fr}}
</style></head><body><header>
<h1>Which photos define your intended character?</h1>
<p class="notice"><strong>No photos have moved. No references or matching rules have changed.</strong>
This is a new task, separate from your completed 70-case pair review. The previous answers remain unchanged.</p>
<ol>
<li>Start with Angelica. Compare the full photos, with face crops alongside. Click an image for the installed original.</li>
<li>Choose <strong>Defines this character</strong> only for clear identity-defining examples.
Choose a few supported different views if available; there is no required 2-3 photo quota.</li>
<li>Use <strong>Same character - not a reference</strong> for an associated photo you do not want defining the core.
Use Different or Uncertain for lookalikes. It is fine if none of the shortlist defines the character.</li>
<li>Then sample Nyxene, Drakness, Ravaelle, Draknara and Draknisa.
Their existing groups and apparent coherence are not verified identity truth.</li>
<li>Export when pausing or finishing. Export includes <strong>all characters</strong>, including unfinished ones.
Copy the JSON into feedback or download it. Browser autosave is a convenience, not a durable handoff.</li>
</ol>
<p>Decisions concern the named fictional character you intend, not biological relationships.
They do not automatically move photos, protect placements, select art or install references.
Appearance coverage is visual for now; no hair, age, body or outfit classifier has run.</p>
</header><main><nav><label>Character <select id="character">{{OPTIONS}}</select></label>
<button id="next">Next character</button><button id="view">Face crops only / full + face</button>
<button id="export">Export all answers</button><label>Import answers <input id="import" type="file" accept=".json,application/json"></label>
<span id="status"></span></nav><p id="error" role="alert"></p>
<details id="export-panel"><summary>Copyable export (all characters)</summary>
<p>Downloads may be blocked. Copy everything below into a JSON file in feedback.</p>
<textarea id="export-json" readonly aria-label="Exported character JSON"></textarea></details>
{{SECTIONS}}</main><script>
"use strict";
const data={{DATA}};
const controls=[...document.querySelectorAll("select[data-photo]")];
const key="character-reference:"+data.packetSHA256;
function answers(){return {schemaVersion:1,kind:"character-reference-answers",packetSHA256:data.packetSHA256,
 binding:data.binding,characters:data.characters.map((g,i)=>({folder:g.folder,decisions:controls
 .filter(e=>Number(e.dataset.character)===i).map(e=>({photoId:e.dataset.photo,choice:e.value}))}))};}
function validate(value){
 if(!value||value.schemaVersion!==1||value.kind!=="character-reference-answers"||
 value.packetSHA256!==data.packetSHA256||JSON.stringify(value.binding)!==JSON.stringify(data.binding)||
 !Array.isArray(value.characters)||value.characters.length!==data.characters.length)throw Error("Answer packet/binding mismatch.");
 const plan=[],seen=new Set();
 for(const group of value.characters){
  const index=data.characters.findIndex(g=>g.folder===group.folder);
  if(index<0||seen.has(index))throw Error("Duplicate or unknown character.");seen.add(index);
  const expected=controls.filter(e=>Number(e.dataset.character)===index), photos=new Set();
  if(!Array.isArray(group.decisions)||group.decisions.length!==expected.length)throw Error("Photo coverage differs.");
  for(const item of group.decisions){
   const control=expected.find(e=>e.dataset.photo===item.photoId);
   if(!control||photos.has(item.photoId)||!data.choices.includes(item.choice))throw Error("Unknown/duplicate photo or decision.");
   photos.add(item.photoId);plan.push([control,item.choice]);
  }
 }return plan;
}
function apply(value){const plan=validate(value);for(const [control,choice] of plan)control.value=choice;}
function progress(){
 const index=Number(document.getElementById("character").value);
 const current=controls.filter(e=>Number(e.dataset.character)===index);
 document.getElementById("status").textContent=`This character: ${current.filter(e=>e.value!=="unreviewed").length}/${current.length}; all: ${controls.filter(e=>e.value!=="unreviewed").length}/${controls.length}`;
 const box=document.getElementById("export-json");if(box.value)box.value=JSON.stringify(answers(),null,2);
}
function save(){try{localStorage.setItem(key,JSON.stringify(answers()));}catch(error){
 document.getElementById("error").textContent="Browser autosave unavailable: "+error.message+". Export before closing.";}progress();}
function show(){const index=Number(document.getElementById("character").value);
 for(const section of document.querySelectorAll("[data-group]"))section.hidden=Number(section.dataset.group)!==index;
 document.getElementById("next").disabled=index===data.characters.length-1;progress();}
for(const control of controls)control.addEventListener("change",save);
document.getElementById("character").onchange=show;
document.getElementById("next").onclick=()=>{document.getElementById("character").selectedIndex++;show();};
document.getElementById("view").onclick=()=>document.body.classList.toggle("faces");
document.getElementById("export").onclick=()=>{
 const text=JSON.stringify(answers(),null,2);document.getElementById("export-json").value=text;
 document.getElementById("export-panel").open=true;
 const url=URL.createObjectURL(new Blob([text],{type:"application/json"})),a=document.createElement("a");
 a.href=url;a.download="character_reference_answers.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);
};
document.getElementById("import").onchange=async event=>{
 document.getElementById("error").textContent="";
 try{const file=event.target.files[0];if(!file)return;apply(JSON.parse(await file.text()));save();}
 catch(error){document.getElementById("error").textContent="Import rejected; answers unchanged: "+error.message;}
 event.target.value="";
};
try{const saved=localStorage.getItem(key);if(saved)apply(JSON.parse(saved));}
catch(error){document.getElementById("error").textContent="Saved answers could not be restored: "+error.message+". Import an exported copy.";}
show();
</script></body></html>
"""
