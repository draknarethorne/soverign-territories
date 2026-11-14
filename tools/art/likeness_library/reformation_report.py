"""Publish the reformed shadow state with immutable evidence and a before/after viewer."""
import copy
import html
import json
import pathlib
import time

import numpy as np

from . import fragment_review, reformation, review_packet, shadow


REASONS = {
    "ambiguous-full-competitor-margin": "Competing grouping hypotheses are too close to choose safely.",
    "below-route-minimum": "The strongest comparison is below this experiment's similarity requirement.",
    "insufficient-independent-support": "Too few independent reference photos support this grouping.",
    "withdrawn-reference-set-insufficient": "After reference withdrawals, the remaining evidence does not qualify.",
    "no-independent-reference-hypothesis": "No usable independent comparison was available in this pass.",
    "protected": "The photo is protected against automatic placement changes.",
    "anchor": "An explicit anchor blocks automatic placement changes.",
    "workflowSelected": "The photo is selected for a workflow; automatic placement changes are blocked.",
    "identityProtected": "The existing identity is protected against automatic placement changes.",
    "quality-ineligible": "The saved face measurement did not pass the single-face quality gate.",
    "review-admission-not-implemented": "This constructor does not implement admission from Review.",
    "artist-scope-held": "Artist photos are outside this general regrouping scope.",
    "non-scoring-domain": "This location is outside the scoring scope.",
    "explicit-owner-unresolved": "Earlier feedback rejected both compared owners; no replacement owner was established.",
    "direct-different-or-uncertain-veto": "An exact-photo different/uncertain label prevents this association.",
    "direct-member-conflict": "Conflicting exact-photo labels prevent admitting these members together.",
    "metadataStale": "Saved metadata is stale; refresh evidence before considering a change.",
    "ambiguousPhotoId": "The stable photo identifier is ambiguous.",
    "rejectionHistory": "Recorded rejection evidence blocks automatic placement changes.",
    "reference-needed": "There are not enough usable independent references for this comparison.",
    "reference-boundary-incomplete": "A later reference/admission veto invalidates this view; dependent admissions are suppressed pending reassessment.",
    "insufficient-qualified-group-members": "Too few members qualify individually to propose this cluster as a new person.",
    "gallery-admission-disabled": "Policy does not authorize automatic admission to this character Gallery.",
}


def presentation(row, people):
    if "membershipAssessment" in row:
        return assessed_presentation(row, people)
    origin = row["origin"]
    if origin == "automatic":
        person = people[row["proposedPersonId"]]
        action = "AUTOMATIC GROUPING PROPOSAL - NOT INSTALLED"
        meaning = "This pass qualified a proposed grouping. It does not authorize a move or choose a final physical owner."
        proposed = person["canonicalOwner"] or " + ".join(person["lineage"])
        feedback = "Judge the proposed same-person grouping, not whether a physical move has been approved."
    elif origin == "confirmed-character-reference":
        action = "RECORDED HUMAN INTENT - NOT AN AUTOMATIC DISCOVERY"
        meaning = "This association comes from previously confirmed reference intent, not a new successful face match."
        proposed = people[row["proposedPersonId"]]["intentFolder"]
        feedback = "No repeat confirmation is required. Comment only if the recorded intent is wrong or needs clarification."
    elif origin == "held":
        action = "KEEP CURRENT PLACEMENT - CHANGE BLOCKED (HOLD)"
        meaning = "A protection, eligibility or scope restriction blocks this pass from changing placement. HOLD is not an identity verdict."
        proposed = "No new grouping assigned by this pass"
        feedback = "No review is required merely because this is HOLD. Flag a wrong identity or an inappropriate restriction if you notice one."
    elif origin == "unresolved":
        action = "KEEP CURRENT PLACEMENT - NO QUALIFIED REGROUPING"
        meaning = "The experimental pass could not establish a new grouping. Existing membership is retained, not newly confirmed or rejected."
        proposed = "No new grouping assigned by this pass"
        feedback = "No manual placement is required. Optional: explain a known split, wrong current identity or misleading comparison."
    else:
        raise ValueError(f"unknown reformation presentation origin: {origin}")
    return {
        "actionLabel": action, "actionMeaning": meaning, "proposalName": proposed,
        "retainedIdentity": row["oldFolder"], "feedbackPrompt": feedback,
        "reasonText": [REASONS.get(reason, "Additional diagnostic restriction: " + reason) for reason in row["reasons"]],
    }


def assessed_presentation(row, people):
    labels = {
        "current-membership-supported": ("CURRENT MEMBERSHIP SUPPORTED", "Independent own-reference evidence and competitor separation pass this recipe."),
        "reassignment-proposed": ("REASSIGNMENT PROPOSED - NOT INSTALLED", "An alternative identity passes independent support and all-competitor separation."),
        "pooled-group-proposed": ("NEW PROVISIONAL GROUP PROPOSED", "Released/pool members form an independently supported group; no named identity is created."),
        "released-to-reassessment-pool": ("CURRENT MEMBERSHIP QUESTIONABLE - RELEASED IN SHADOW", "The available own-reference evidence does not qualify membership. Reassess without treating the old folder as truth."),
        "pooled-awaiting-evidence": ("IN REASSESSMENT POOL - NOT CERTIFIED TO OLD IDENTITY", "The photo is eligible to regroup, but no destination clears all safeguards. It is not automatically a new person."),
        "membership-ambiguous": ("MEMBERSHIP AMBIGUOUS", "Own evidence and competing identities do not separate sufficiently. No identity correctness claim."),
        "reference-needed": ("ASSESSMENT LIMITED - REFERENCES NEEDED", "The own identity lacks sufficient independent references. This is not a failed same-person verdict."),
        "assessment-unavailable": ("ASSESSMENT UNAVAILABLE", "Measurement or scope gates prevent reliable membership assessment."),
        "change-blocked": ("CHANGE BLOCKED (HOLD) - SEE SEPARATE ASSESSMENT", "Protection blocks changes; the independent own-membership assessment below is not replaced by this lock."),
        "explicit-intent": ("RECORDED HUMAN INTENT", "Confirmed reference intent is preserved separately from numeric membership assessment."),
        "direct-member-conflict": ("CONFLICT - NO AUTOMATIC MEMBERSHIP", "Exact-photo evidence prevents co-admission; the conflict remains explicit."),
    }
    if row["disposition"] not in labels:
        raise ValueError("unknown assessed disposition: " + row["disposition"])
    action, meaning = labels[row["disposition"]]
    person = people.get(row["proposedPersonId"])
    proposed = (
        person["canonicalOwner"] or "Provisional group: " + " + ".join(person["lineage"])
        if person else "No qualified destination; reassessment remains open"
    )
    own = row["membershipAssessment"]["own"]
    own_text = "No independent own-reference comparison available."
    if own:
        score = f'{own["activeScore"]:.3f}' if own["activeScore"] is not None else "unavailable"
        own_text = (
            f'Own score {score}; independent support {len(own["supportPhotoIds"])}/{own["requiredSupport"]}; '
            f'required score {own["routeMinimum"]:.3f}. '
            + " ".join(REASONS.get(reason, reason) for reason in own["blockers"])
        )
    rivals = row["membershipAssessment"]["rivals"]
    rival_text = "No rival comparison available."
    if rivals:
        rival = rivals[0]
        rival_text = (
            f'Strongest outside comparison: {rival["folder"]}, score {rival["score"]:.3f}, '
            f'independent support {len(rival["supportPhotoIds"])}/{rival["requiredSupport"]}. '
            + ("It does not qualify: " + " ".join(REASONS.get(r, r) for r in rival["blockers"])
               if rival["blockers"] else "Support/score pass; a move still requires full-competitor separation.")
        )
    return {
        "actionLabel": action, "actionMeaning": meaning, "proposalName": proposed,
        "retainedIdentity": row["oldFolder"],
        "assessmentText": "Own membership: " + row["membershipAssessment"]["status"] + ". " + own_text + " " + rival_text,
        "feedbackPrompt": "No review is required to continue development. If useful, flag incorrect membership or a known split; no answer authorizes installed moves.",
        "reasonText": [REASONS.get(reason, reason) for reason in row["reasons"]],
    }


def effective_ledger(ledger, packet, evaluation):
    result = copy.deepcopy(ledger)
    if evaluation is None:
        return result
    pairs = {tuple(sorted(row["photoIds"])): row["label"] for row in ledger["pairs"]}
    cases = {case["id"]: case for case in packet["cases"]}
    for row in evaluation["identityAnswers"]["decisions"]:
        pid = cases[row["caseId"]]["photoId"]
        for pair in row["pairs"]:
            key = tuple(sorted((pid, pair["referencePhotoId"])))
            label = pair["label"]
            pairs[key] = label if key not in pairs or pairs[key] == label else "uncertain"
        if row["currentMatch"] == row["targetMatch"] == "different":
            result["unresolved"].append({"photoId": pid})
    result["pairs"] = [{"photoIds": list(key), "label": value} for key, value in sorted(pairs.items())]
    return result


def select(state, packet, vectors=None, *, limit=40):
    rows = {r["photoId"]: r for r in state["rows"]}
    people = {p["personId"]: p for p in state["people"]}
    selected, used, panels = [], set(), {}
    queries = []
    if state["rows"] and "membershipAssessment" in state["rows"][0]:
        for disposition in ("current-membership-supported", "released-to-reassessment-pool",
                            "reassignment-proposed", "pooled-group-proposed", "reference-needed"):
            queries.extend([row["photoId"] for row in state["rows"] if row["disposition"] == disposition][:1])
    for person in state["people"]:
        if len(person["lineage"]) > 1:
            automatic = [pid for pid in person["memberPhotoIds"] if rows[pid]["origin"] == "automatic"]
            queries.extend(automatic[:1])
    queries += [case["photoId"] for case in packet["cases"]]
    queries += [row["photoId"] for row in state["rows"] if row["origin"] == "automatic"]
    for pid in queries:
        if pid in selected or len(selected) >= 12:
            continue
        row = rows[pid]
        top = row["topCandidates"][0] if row["topCandidates"] else None
        if row["origin"] == "confirmed-character-reference":
            refs = [other for other in people[row["proposedPersonId"]]["memberPhotoIds"] if other != pid]
            role = "Explicitly confirmed intent examples; NOT automatic admission evidence"
        else:
            refs = (top["supportPhotoIds"] or top["frozenReferencePhotoIds"]) if top else []
            role = ("Active independent support" if top and top["supportPhotoIds"] else
                    "Frozen comparison examples; support failed or references withdrawn")
        # Display selection only: never feeds discovery, support or admission.
        refs = sorted(refs, key=lambda rid: (
            rows[rid]["oldFolder"] == row["oldFolder"],
            -float(np.asarray(vectors[pid]) @ np.asarray(vectors[rid])) if vectors is not None else 0., rid,
        ))[:2]
        own_refs = []
        if "membershipAssessment" in row:
            own = row["membershipAssessment"]["own"]
            if own:
                own_refs = (own["supportPhotoIds"] or own["frozenReferencePhotoIds"])[:1]
            refs = list(dict.fromkeys([*own_refs, *refs[:1]]))
            role = "Labelled own-reference and strongest-comparison examples; examples are not move recommendations"
        if len(used | {pid, *refs}) > limit:
            continue
        if not top:
            continue
        selected.append(pid)
        used.update((pid, *refs))
        panels[pid] = {"referencePhotoIds": refs, "ownReferencePhotoIds": own_refs, "role": role}
    return {"usedPhotoIds": sorted(used), "queries": selected,
            "people": people, "panels": panels, "stateSHA256": fragment_review.digest(state)}


def render(state, selection, images, run):
    escape = html.escape
    rows = {row["photoId"]: row for row in state["rows"]}
    people = selection["people"]
    root = pathlib.Path(run["workingRoot"])
    def figure(pid):
        image = images[pid]
        return (
            f'<figure><a href="{escape(image["href"], quote=True)}" target="_blank" rel="noopener">'
            f'<img src="{image["full"]}" alt="{escape(pid, quote=True)}" loading="lazy"></a>'
            f'<figcaption>{escape(rows[pid]["oldFolder"])}<br>{escape(pid)}</figcaption></figure>'
        )
    cards = []
    for pid in selection["queries"]:
        row = rows[pid]
        top = row["topCandidates"][0]
        panel = selection["panels"][pid]
        references = panel["referencePhotoIds"]
        proposed = row["proposedPersonId"]
        text = presentation(row, people)
        cards.append(
            '<article>'
            f'<h2>{escape(text["actionLabel"])}</h2>'
            f'<p>{escape(text["actionMeaning"])}</p>'
            f'<p><b>Installed location (not an identity verdict):</b> {escape(row["oldFolder"])}<br>'
            f'<b>Installed photo:</b> {escape(row["installedDestination"])}<br>'
            f'<b>Experimental grouping:</b> {escape(text["proposalName"])}<br>'
            'No file has moved. The current identity is not a new correctness certification.</p>'
            f'<p><b>Own-membership assessment:</b> {escape(text.get("assessmentText", "Not integrated in this earlier candidate."))}</p>'
            f'<p>Left: assessed photo. Right: {escape(panel["role"])}. '
            'Strongest candidate scores below do not override confirmed intent.</p>'
            f'<div class="photos">{figure(pid)}'
            + "".join(
                '<div><p>' + ("Own-reference example" if rid in panel["ownReferencePhotoIds"]
                             else "Strongest-comparison example") + "</p>" + figure(rid) + "</div>"
                for rid in references
            ) + '</div>'
            '<p><b>Why this result:</b> '
            + escape(" ".join(text["reasonText"]) or "Independent support and competitor separation passed this experimental recipe.")
            + (' Supporting diagnostics below did not decide the recorded human intent.'
               if row["origin"] == "confirmed-character-reference" else '')
            + '</p>'
            f'<p>Strongest score {top["score"]:.3f}; support {len(top["supportPhotoIds"])}/{top["requiredSupport"]}; '
            f'floor {top["routeMinimum"]:.3f}; required margin {top["routeMargin"]:.3f}; '
            f'{row["competitorPersonCount"]} competing person hypotheses.</p>'
            '<details><summary>Exact scores, references and blockers</summary><pre>'
            f'{escape(json.dumps({"ownAssessment": row.get("membershipAssessment"), "topCandidates": row["topCandidates"]}, indent=2))}</pre></details>'
            f'<p><b>Optional feedback:</b> {escape(text["feedbackPrompt"])} '
            'Agreement with keeping placement does not label the comparison photos different or confirm every current member.</p>'
            f'<label>Does this handling make sense for now? <select data-photo="{escape(pid, quote=True)}">'
            '<option value="unreviewed">Not evaluated</option><option value="agree">Agree</option>'
            '<option value="disagree">Disagree</option><option value="uncertain">Uncertain</option>'
            '</select></label>'
            f'<label>Comment <textarea data-note="{escape(pid, quote=True)}" rows="2"></textarea></label></article>'
        )
    pool_groups = {
        pid: group for group in state.get("reassessmentGroups", []) for pid in group["photoIds"]
    }
    table_rows = [{
        **row, **presentation(row, people),
        "poolText": (
            f'Logical reassessment pool: {pool_groups[row["photoId"]]["groupId"]}; '
            f'{len(pool_groups[row["photoId"]]["photoIds"])} photos, '
            f'{len(pool_groups[row["photoId"]].get("admittedPhotoIds", []))} admitted. '
            'A provisional group is not an assigned identity.'
        ) if row["photoId"] in pool_groups else "",
        "href": review_packet.safe_path(root, row["installedDestination"]).as_uri(),
        "filename": pathlib.PurePosixPath(row["installedDestination"]).name,
    } for row in state["rows"]]
    payload = json.dumps({"rows": table_rows, "stateSHA256": selection["stateSHA256"],
                          "queries": selection["queries"]}, allow_nan=False).replace("<", "\\u003c")
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Reformed identity candidate - actual proposed membership</title><style>'
        'body{font:16px system-ui;background:#171c23;color:#edf1f7;margin:20px auto;padding:0 12px;max-width:1450px}'
        'a{color:#9ed1ff}article,section{background:#242d38;padding:16px;margin:20px 0;border:1px solid #57677a}'
        '.photos{display:flex;flex-wrap:wrap;gap:12px}figure{margin:0;max-width:280px}'
        'img{width:240px;max-width:100%;height:300px;object-fit:contain}figcaption,p,td{overflow-wrap:anywhere}'
        '.ledger-photo{display:block;width:160px;height:180px;max-width:100%;object-fit:contain;margin-bottom:8px}'
        '.image-error{display:block;color:#ffca91}.image-error[hidden]{display:none}'
        'pre{white-space:pre-wrap;overflow-wrap:anywhere}select,input,textarea,button{font:inherit;max-width:100%}'
        'label{display:block;margin:10px 0}textarea{display:block;width:95%}'
        'table{border-collapse:collapse;table-layout:fixed;width:100%}td,th{text-align:left;padding:8px;border:1px solid #68778a}'
        '</style></head><body><h1>Reformed identity candidate</h1>'
        f'<p><b>Candidate status: {escape(state["status"])}. '
        + ("Reference withdrawals are still pending at the pass cap. Not ready for acceptance."
           if not state["summary"]["stable"] else "Stable under this recipe; accuracy is not accepted.")
        + '</b></p><p><b>This is an actual proposed membership state, not just rival rankings.</b> '
        'Discovery crosses old folder boundaries. Installed files, Gallery, Overview and Review are unchanged. '
        'This page has no installation controls. Scores are similarities, not probabilities.</p>'
        '<section><h2>What happens to the photos?</h2>'
        '<p><b>No photo is made unassigned by this report.</b> Every installed file stays where it is. '
        'The installed folder is lineage, not proof of supported identity membership. '
        'When own-membership assessment is enabled, logically released photos enter the reassessment pool '
        'without a physical move. Supported membership, reference eligibility and placement locks are separate.</p>'
        f'<ul><li>{state["summary"]["unresolvedPhotos"]:,}: no qualified person assignment; read the separate membership/pool assessment.</li>'
        f'<li>{state["summary"]["heldPhotos"]:,}: change blocked by a safeguard or assessment unavailable (HOLD).</li>'
        f'<li>{state["summary"]["automaticMembers"]:,}: supported existing memberships or automatic proposals, not installed moves.</li>'
        f'<li>{state["summary"]["explicitIntentMembers"]:,}: recorded human reference intent, not automatic recovery.</li></ul>'
        '<p><b>You do not need to sort the unresolved photos or answer every case.</b> Optional feedback on the sample helps '
        'identify wrong groupings, known splits and confusing explanations. Skipping a case leaves it unevaluated. '
        'No answer authorizes installation, changes a protection or automatically trains the matcher.</p></section>'
        f'<details><summary>Technical counts (unresolved means no new grouping, not no identity)</summary>'
        f'<pre>{escape(json.dumps(state["summary"], indent=2))}</pre></details>'
        '<p>Cross-folder people share a proposed person ID; canonical physical ownership can remain unresolved. '
        'Face-view clusters are not certified outfit groups. Holds are not proof that two people differ. '
        'Human-confirmed reference intent is reported separately from automatic membership.</p>'
        '<details><summary>Recipe and remaining work</summary><pre>'
        f'{escape(json.dumps(state["recipe"], indent=2))}</pre><ul>'
        + "".join(f'<li>{escape(text)}</li>' for text in state["limits"])
        + '</ul></details>'
        + ('<details><summary>Frozen reference-boundary transitions (not accepted identity accuracy)</summary><pre>'
           + escape(json.dumps(state["referenceBoundaries"], indent=2)) + '</pre></details>'
           if "referenceBoundaries" in state else "")
        + '<p><a href="state.json">Complete person / appearance / residual / transition state</a></p>'
        '<h2>Before / after for every photo</h2>'
        '<label>Search old folder, photo or proposed person <input id="filter" type="search"></label>'
        '<label>Show <select id="mode"><option value="all">All photos</option>'
        + ("".join(f'<option value="{html.escape(value, quote=True)}">{html.escape(value)}</option>'
                   for value in state["summary"]["membershipDispositions"])
           if "membershipDispositions" in state["summary"] else "")
        +
        '<option value="automatic">Automatic grouping proposals - not installed</option>'
        '<option value="confirmed-character-reference">Recorded human intent</option>'
        '<option value="held">Current placement retained - change blocked (HOLD)</option>'
        '<option value="unresolved">Current placement retained - no qualified regrouping</option></select></label>'
        '<p id="count"></p><button id="prev">Previous 100</button> <button id="next">Next 100</button>'
        '<table><thead><tr><th>Photo / filename / installed location</th><th>Experimental grouping, if qualified</th>'
        '<th>Action / explanation</th></tr></thead><tbody id="members"></tbody></table>'
        '<h2>Bounded visual sample</h2>' + "".join(cards)
        + '<button id="export">Export sample feedback</button><p id="status" role="status"></p>'
        f'<script type="application/json" id="data">{payload}</script><script>'
        + SCRIPT + '</script></body></html>'
    )


SCRIPT = r"""
const data=JSON.parse(document.getElementById("data").textContent);
const el=id=>document.getElementById(id);let page=0,filtered=[];
function refresh(reset=false){
 if(reset)page=0;const term=el("filter").value.toLowerCase(),mode=el("mode").value;
 filtered=data.rows.filter(r=>(mode==="all"||r.origin===mode||r.disposition===mode)&&
  (r.photoId+" "+r.oldFolder+" "+r.proposalName+" "+r.proposedPersonId).toLowerCase().includes(term));
 page=Math.min(page,Math.max(0,Math.ceil(filtered.length/100)-1));
 el("members").replaceChildren();
 for(const row of filtered.slice(page*100,(page+1)*100)){
  const tr=document.createElement("tr"),photo=document.createElement("td"),a=document.createElement("a");
  const imageLink=document.createElement("a"),image=document.createElement("img"),error=document.createElement("span");
  imageLink.href=row.href;imageLink.target="_blank";imageLink.rel="noopener";
  image.src=row.href;image.alt=row.filename+" / "+row.photoId;image.loading="lazy";image.decoding="async";
  image.className="ledger-photo";imageLink.append(image);
  error.className="image-error";error.hidden=true;
  image.onerror=()=>{error.hidden=false;error.textContent="Image unavailable at installed path; use filename link to inspect. This is not an identity verdict.";};
  a.href=row.href;a.textContent=row.filename;a.target="_blank";a.rel="noopener";
  const location=document.createElement("p");location.textContent=row.photoId+" / "+row.oldFolder;
  photo.append(imageLink,error,a,location);tr.append(photo);
  for(const text of [row.proposalName,
   row.actionLabel+". "+row.actionMeaning+" "+(row.assessmentText||"")+" "+(row.poolText||"")+" "+row.reasonText.join(" ")]){
   const td=document.createElement("td");td.textContent=text;tr.append(td);
  }el("members").append(tr);
 }
 el("count").textContent=filtered.length+" photos; page "+(page+1);
 el("prev").disabled=page===0;el("next").disabled=(page+1)*100>=filtered.length;
}
el("filter").oninput=()=>refresh(true);el("mode").onchange=()=>refresh(true);
el("prev").onclick=()=>{page--;refresh()};el("next").onclick=()=>{page++;refresh()};refresh();
el("export").onclick=()=>{
 const decisions=[...document.querySelectorAll("select[data-photo]")].filter(s=>s.value!=="unreviewed").map(s=>({
  photoId:s.dataset.photo,judgment:s.value,
  reason:[...document.querySelectorAll("textarea[data-note]")].find(t=>t.dataset.note===s.dataset.photo).value
 }));
 if(decisions.some(r=>r.judgment==="disagree"&&!r.reason.trim())){
  el("status").textContent="Add a reason for each disagreement.";return;
 }
 const value={schemaVersion:1,kind:"reformation-state-evaluation",stateSHA256:data.stateSHA256,decisions};
 const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:"application/json"}));
 const a=document.createElement("a");a.href=url;a.download="reformation_evaluation_"+data.stateSHA256.slice(0,12)+".json";
 a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);el("status").textContent="Exported "+decisions.length+" evaluations.";
};
"""


def reuse_state(directory, bindings, code):
    receipt = json.loads((directory / "receipt.json").read_bytes())
    publisher_names = {"likeness_candidate_replay.py", "reformation_report.py"}
    analysis = lambda values: {p: h for p, h in values.items() if pathlib.Path(p).name not in publisher_names}
    if (receipt["kind"] != "reformation-state-receipt" or receipt["inputs"] != bindings
            or analysis(receipt["code"]) != analysis(code) or receipt["reverseVerified"] is not True
            or receipt["libraryWrites"] != 0
            or not {"state.json", "display.json", "index.html"} <= receipt["outputs"].keys()):
        raise ValueError("reformation reuse analysis/input contract changed")
    for path, digest in {**bindings, **analysis(code)}.items():
        if shadow.digest(pathlib.Path(path)) != digest:
            raise ValueError("reformation reuse source/analysis changed")
    for name, digest in receipt["outputs"].items():
        if shadow.digest(review_packet.safe_path(directory, name)) != digest:
            raise ValueError("reformation reuse output changed: " + name)
    for image in json.loads((directory / "display.json").read_bytes()).values():
        if shadow.digest(pathlib.Path(image["path"])) != image["sha256"]:
            raise ValueError("reformation reuse displayed source changed")
    return json.loads((directory / "state.json").read_bytes()), {
        **bindings, str(directory / "receipt.json"): shadow.digest(directory / "receipt.json"),
        **{str(directory / name): digest for name, digest in receipt["outputs"].items()},
    }


def publish(args, out, reused, candidate, run, vectors, cache, ledger, codes, validate_evaluation):
    if not reused or args.prior_answers or args.answers or args.evaluation:
        raise ValueError("--reform requires --reuse-result and no prior/answer/evaluation options")
    _, packet, _, bindings = reused
    evaluation = None
    if args.split_evaluation:
        if not args.split_evaluation.is_absolute():
            raise ValueError("--split-evaluation must be absolute")
        evaluation = json.loads(args.split_evaluation.read_bytes())
        validate_evaluation(packet, reused[0], evaluation)
        bindings = {**bindings, str(args.split_evaluation): shadow.digest(args.split_evaluation)}
    effective = effective_ledger(ledger, packet, evaluation)
    module_paths = [pathlib.Path(__file__), pathlib.Path(reformation.__file__)]
    assess = getattr(args, "assess_membership", False) is True
    if assess:
        from . import membership_reassessment
        module_paths.append(pathlib.Path(membership_reassessment.__file__))
    code = {**codes(), **{str(p.resolve()): shadow.digest(p) for p in module_paths}}
    view_source = getattr(args, "reform_view", None)
    reused_state = None
    if view_source:
        if not view_source.is_absolute() or view_source.resolve() == out.resolve():
            raise ValueError("--reform-view must be absolute and distinct from --out")
        reused_state, bindings = reuse_state(view_source, bindings, code)
    def verify(directory):
        receipt = json.loads((directory / "receipt.json").read_bytes())
        if (receipt["kind"] != "reformation-state-receipt" or receipt["inputs"] != bindings
                or receipt["code"] != code or receipt["reverseVerified"] is not True
                or receipt["libraryWrites"] != 0
                or not {"state.json", "display.json", "index.html"} <= receipt["outputs"].keys()):
            raise ValueError("reformation report input/code/output contract changed")
        for path, digest in {**bindings, **code}.items():
            if shadow.digest(pathlib.Path(path)) != digest:
                raise ValueError("reformation report source/code changed")
        for name, digest in receipt["outputs"].items():
            if shadow.digest(review_packet.safe_path(directory, name)) != digest:
                raise ValueError(f"reformation report output changed: {name}")
        for row in json.loads((directory / "display.json").read_bytes()).values():
            if shadow.digest(pathlib.Path(row["path"])) != row["sha256"]:
                raise ValueError("reformation displayed source changed")
    if args.check or args.apply and out.exists():
        verify(out)
        print(f"Verified reformation state: {out / 'index.html'}")
        return 0
    if not args.apply:
        if reused_state is not None:
            print("Preview: republish verified unchanged reformation state with clarified placement/action wording; "
                  "no scoring, model calls or installed changes.")
            return 0
        print(("Preview: own-reference assessment, category-aware alternatives and released-pool regrouping. "
               if assess else "Preview: ")
              + f"Reconstruct cross-folder person state from {len(run['photos'])} saved photos; "
              "full competitors, frozen leave-one-out support, bounded withdrawal passes and reverse check. "
              "Publication only; no models, downloads, installed writes or intake.")
        return 0
    start = time.perf_counter()
    if reused_state is not None:
        state = reused_state
    else:
        state = reformation.build(
            candidate, run, vectors, effective, progress=lambda text: print(text, flush=True),
            **({"assess_membership": True} if assess else {}),
        )
        reversed_run, reversed_candidate = copy.deepcopy(run), copy.deepcopy(candidate)
        reversed_run["photos"].reverse()
        reversed_run["finalMembershipAudit"]["rows"].reverse()
        for key in ("rows", "identities", "appearances"):
            reversed_candidate[key].reverse()
        reverse_ledger = copy.deepcopy(effective)
        for key in ("pairs", "referenceProposals", "unresolved"):
            reverse_ledger[key].reverse()
        if state != reformation.build(
            reversed_candidate, reversed_run, vectors, reverse_ledger,
            progress=lambda text: print("Reverse check: " + text, flush=True),
            **({"assess_membership": True} if assess else {}),
        ):
            raise ValueError("reformation state differs under reversed inputs")
    split_cases = {
        row["caseId"] for row in evaluation["identityAnswers"]["decisions"]
        if row["currentMatch"] == row["targetMatch"] == "same"
    } if evaluation else set()
    display_packet = {**packet, "cases": sorted(
        packet["cases"], key=lambda case: (case["id"] not in split_cases, case["id"]),
    )}
    selection = select(state, display_packet, vectors)
    review_packet.image_assets(selection, run, cache, out, write=False)
    staging = out.with_name(out.name + ".partial")
    staging.mkdir(parents=True, exist_ok=False)
    images, outputs = review_packet.image_assets(selection, run, cache, staging, write=True)
    for name, value in (("state.json", state), ("display.json", images)):
        (staging / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        outputs[name] = shadow.digest(staging / name)
    (staging / "index.html").write_text(render(state, selection, images, run), encoding="utf-8")
    outputs["index.html"] = shadow.digest(staging / "index.html")
    receipt = {"schemaVersion": 1, "kind": "reformation-state-receipt", "inputs": bindings,
               "code": code, "outputs": outputs, "reverseVerified": True, "libraryWrites": 0,
               "modelCalls": 0, "elapsedSeconds": time.perf_counter() - start,
               "reusedResult": str(args.reuse_result), "stable": state["summary"]["stable"]}
    receipt["reusedState"] = str(view_source) if view_source else None
    receipt["scoringPasses"] = 0 if reused_state is not None else 2
    (staging / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    verify(staging)
    staging.rename(out)
    print("Reformation:", state["summary"], flush=True)
    print(f"Published actual proposed state: {out / 'index.html'} ({receipt['elapsedSeconds']:.3f}s)", flush=True)
    return 0
