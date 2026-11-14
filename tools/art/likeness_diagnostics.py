"""Own-core/category sensitivity and bounded existing-CLIP ablations, without identity mutation."""
import argparse
import collections
import html
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.art.likeness_library import (  # noqa: E402
    appearance_context, fragment_evidence, membership_diagnostics, policy, protection,
    reformation_report, review_packet, shadow,
)
from tools.art.likeness_review_packet import output_path  # noqa: E402


def codes():
    modules = (appearance_context, fragment_evidence, membership_diagnostics, policy,
               protection, reformation_report, review_packet, shadow)
    paths = [pathlib.Path(__file__).resolve(), ROOT / "bin" / "likeness-diagnostics.cmd",
             *(pathlib.Path(m.__file__).resolve() for m in modules)]
    return {str(p): shadow.digest(p) for p in paths}


def verify(bindings):
    for path, digest in bindings.items():
        if shadow.digest(pathlib.Path(path)) != digest:
            raise ValueError(f"diagnostic evidence changed: {path}")


def load(source):
    receipt = json.loads((source / "receipt.json").read_bytes())
    if receipt["kind"] != "reformation-state-receipt" or not receipt["reverseVerified"] or receipt["libraryWrites"]:
        raise ValueError("diagnostics require a reverse-verified non-installing assessed state")
    bindings = {
        **receipt["inputs"], **receipt["code"],
        str(source / "receipt.json"): shadow.digest(source / "receipt.json"),
        **{str(review_packet.safe_path(source, name)): digest for name, digest in receipt["outputs"].items()},
    }
    verify(bindings)
    def find(name):
        found = [pathlib.Path(p) for p in receipt["inputs"] if pathlib.Path(p).name == name]
        if len(found) != 1:
            raise ValueError(f"diagnostics require exactly one bound {name}")
        return found[0]
    state = json.loads((source / "state.json").read_bytes())
    if any("membershipAssessment" not in row for row in state["rows"]):
        raise ValueError("own-membership assessment is not present")
    run, vectors, _, _ = review_packet.load_experiment(find("experiment.json").parent)
    cache = json.loads(find("likeness-cache.json").read_bytes())
    ledger = json.loads(find("ledger.json").read_bytes())
    evaluations = [
        json.loads(pathlib.Path(p).read_bytes()) for p in receipt["inputs"]
        if pathlib.Path(p).suffix == ".json" and pathlib.Path(p).name.startswith("candidate_evaluation_")
    ]
    if len(evaluations) != 1:
        raise ValueError("one bound returned candidate evaluation required")
    evaluation = evaluations[0]
    from tools.art import likeness_candidate_replay as replay
    candidates = [
        pathlib.Path(p) for p in receipt["inputs"] if pathlib.Path(p).name == "packet.json"
        and json.loads(pathlib.Path(p).read_bytes()).get("packetSHA256") == evaluation["packetSHA256"]
    ]
    if len(candidates) != 1:
        raise ValueError("review packet binding unavailable")
    packet = json.loads(candidates[0].read_bytes())
    result_path = candidates[0].parent / "candidate.json"
    replay.validate_evaluation(packet, json.loads(result_path.read_bytes()), evaluation)
    bindings[str(result_path)] = shadow.digest(result_path)
    effective = reformation_report.effective_ledger(ledger, packet, evaluation)
    checkpoints = [pathlib.Path(p) for p in bindings if pathlib.Path(p).suffix == ".safetensors"]
    if len(checkpoints) != 1:
        raise ValueError("existing local CLIP checkpoint binding ambiguous")
    return state, run, vectors, cache, effective, checkpoints[0], bindings


def sample_pairs(ledger, rows, vectors, *, max_photos=24):
    selected, used, folder_counts = [], set(), collections.Counter()
    for label in ("same", "different", "uncertain"):
        count = 0
        for pair in sorted(ledger["pairs"], key=lambda p: tuple(sorted(p["photoIds"]))):
            ids = sorted(pair["photoIds"])
            if pair["label"] != label or not set(ids) <= vectors.keys():
                continue
            folders = tuple(sorted(rows[pid]["oldFolder"] for pid in ids))
            if count >= 6 or folder_counts[(label, folders)] >= 2 or len(used | set(ids)) > max_photos:
                continue
            selected.append({"photoIds": ids, "label": label})
            folder_counts[(label, folders)] += 1
            used.update(ids)
            count += 1
    if not selected:
        raise ValueError("no content-bound labelled cue controls")
    return selected, sorted(used)


def regions(image, box):
    below = appearance_context.crop_region(image, box)
    x, y, w, h = box
    width, height = image.size
    head = (max(0, round((x-.8*w)*width)), max(0, round((y-.8*h)*height)),
            min(width, round((x+1.8*w)*width)), min(height, round((y+1.2*h)*height)))
    if head[2]-head[0] < 32 or head[3]-head[1] < 32:
        head = None
    return {"below-face": below, "head-context": head}


def descriptors(ids, run, face_cache, checkpoint, out, saved=None):
    import numpy as np
    from PIL import Image, ImageOps
    from importlib.metadata import version
    photos = {r["photoId"]: r for r in run["photos"]}
    published = {r["path"]: r["sha256"] for r in run["publishedFiles"]}
    boxes = {r["alignmentEvidence"]["sourceSha256"]: r["box"] for r in face_cache["emb"].values()
             if r.get("alignmentEvidence", {}).get("sourceSha256") and r.get("box")}
    checkpoint_hash = shadow.digest(checkpoint)
    records, model, transform, torch_module = {}, None, None, None
    extractions = decoded = 0
    start = time.perf_counter()
    for pid in ids:
        photo = photos[pid]
        path = review_packet.safe_path(pathlib.Path(run["workingRoot"]), photo["destination"])
        expected = published.get(photo["destination"])
        if not expected or shadow.digest(path) != expected:
            raise ValueError(f"cue original changed: {pid}")
        box = boxes.get(photo["preparedSHA256"])
        if box is None:
            raise ValueError(f"cue face geometry missing: {pid}")
        key = json.dumps([expected, box, checkpoint_hash, "CLIP-ViT-B-32-crops-v1",
                          {name: version(name) for name in ("open-clip-torch", "torch", "torchvision", "pillow")}],
                         sort_keys=True)
        if saved and pid in saved and saved[pid]["key"] == key:
            records[pid] = saved[pid]
            continue
        with Image.open(path) as raw:
            image = ImageOps.exif_transpose(raw).convert("RGB")
            decoded += 1
            result = {"key": key, "source": str(path), "sourceSHA256": expected, "regions": {}}
            for name, geometry in regions(image, box).items():
                if geometry is None:
                    result["regions"][name] = {"status": "unavailable", "reason": "insufficient crop pixels"}
                    continue
                if model is None:
                    import open_clip
                    import torch
                    torch_module = torch
                    torch.set_num_threads(4)
                    model, _, transform = open_clip.create_model_and_transforms(
                        "ViT-B-32", pretrained=str(checkpoint), device="cpu",
                    )
                    model.eval()
                crop = image.crop(geometry)
                with torch_module.inference_mode():
                    vector = model.encode_image(transform(crop).unsqueeze(0)).float().cpu().numpy()[0]
                norm = np.linalg.norm(vector)
                if not np.isfinite(vector).all() or not norm:
                    raise ValueError("invalid cue feature")
                filename = f'cue-{ids.index(pid):02d}-{name}.jpg'
                crop.thumbnail((384, 384))
                crop.save(out / filename, quality=88)
                result["regions"][name] = {
                    "status": "measured", "cropPixels": list(geometry), "image": filename,
                    "vector": [float(x) for x in vector/norm],
                }
                extractions += 1
            records[pid] = result
    if shadow.digest(checkpoint) != checkpoint_hash:
        raise ValueError("cue checkpoint changed during extraction")
    return records, {"extractions": extractions, "decodedImages": decoded,
                     "elapsedSeconds": time.perf_counter()-start, "checkpointSHA256": checkpoint_hash}


def auc(pairs, field):
    same = [p[field] for p in pairs if p["label"] == "same" and p[field] is not None]
    different = [p[field] for p in pairs if p["label"] == "different" and p[field] is not None]
    if not same or not different:
        return None
    return sum((a > b) + .5*(a == b) for a in same for b in different)/(len(same)*len(different))


def cue_results(pairs, records, vectors):
    import numpy as np
    output = []
    for pair in pairs:
        a, b = pair["photoIds"]
        row = {**pair, "face": round(float(vectors[a] @ vectors[b]), 6)}
        for region in ("below-face", "head-context"):
            left, right = records[a]["regions"][region], records[b]["regions"][region]
            row[region] = round(float(np.array(left["vector"]) @ right["vector"]), 6) \
                if left["status"] == right["status"] == "measured" else None
        output.append(row)
    return {
        "pairs": output, "pairCountByLabel": dict(collections.Counter(p["label"] for p in output)),
        "developmentPairRankingAUC": {name: auc(output, name) for name in ("face", "below-face", "head-context")},
        "identityDecisionsChanged": 0,
        "limits": [
            "Small reused development labels; not independent acceptance, calibrated thresholds or proven identity gain.",
            "Head-context includes the face and is not isolated hair evidence or independent face corroboration.",
            "Below-face contains clothing/background; shared styling cannot establish identity or biological relationship.",
            "Uncertain labels stay uncertain and are excluded from same-versus-different ranking AUC.",
            "No score fusion, threshold selection or photo/category moves occur.",
        ],
    }


def render(diagnostic, cues, records, run):
    root = pathlib.Path(run["workingRoot"])
    rows = []
    for row in diagnostic["rows"]:
        rows.append({**row, "href": review_packet.safe_path(root, row["installedDestination"]).as_uri(),
                     "filename": pathlib.PurePosixPath(row["installedDestination"]).name})
    payload = json.dumps(rows, allow_nan=False).replace("<", "\\u003c")
    samples = []
    for pair in cues["pairs"]:
        pictures = []
        for pid in pair["photoIds"]:
            record = records[pid]
            pictures.append('<div><p>' + html.escape(pid) + '</p>'
                + "".join('<figure><img loading="lazy" src="' + r["image"] + '" alt="' + name
                          + ' crop"><figcaption>' + name + '</figcaption></figure>'
                          for name, r in record["regions"].items() if r["status"] == "measured")
                + '<a href="' + html.escape(pathlib.Path(record["source"]).as_uri(), quote=True) + '">'
                + html.escape(pathlib.Path(record["source"]).name) + '</a></div>')
        samples.append('<article><h3>Existing exact-pair label: ' + pair["label"] + '</h3><div class="pair">'
                       + "".join(pictures) + '</div><pre>' + html.escape(json.dumps(pair, indent=2)) + '</pre></article>')
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        '<title>Why photos are held — own-core and category evidence</title><style>'
        'body{font:16px system-ui;max-width:1450px;margin:auto;padding:16px;background:#171c23;color:#edf1f7}'
        'a{color:#9ed1ff}article,section{padding:16px;margin:12px 0;border:1px solid #718096}'
        'img{width:160px;height:190px;max-width:100%;object-fit:contain}td,th{padding:8px;vertical-align:top;overflow-wrap:anywhere}'
        'table{width:100%;table-layout:fixed;border-collapse:collapse}td,th{border:1px solid #718096}'
        'pre{white-space:pre-wrap;overflow-wrap:anywhere}.pair{display:flex;flex-wrap:wrap;gap:12px}'
        '.pair>div{max-width:45%;overflow-wrap:anywhere}figure{display:inline-block;margin:4px}input,select{max-width:100%;font:inherit}'
        'p{overflow-wrap:anywhere}@media(max-width:600px){.pair>div{max-width:100%}}</style>'
        '<h1>Why a photo is held: evidence versus action</h1>'
        '<section><p><b>Staying on disk is not confirmation of identity.</b> This experiment never moves installed photos. '
        'Protection may block an action even when the score is low. A photo can also be a valid non-core member: '
        'existing-member retention is not a new automatic join, and reference eligibility is a third question.</p>'
        '<p><b>The shadow experiment was stricter than the maintained category core rules.</b> It used the automatic-protection '
        '0.55 floor to qualify reference sets. Losing those references can make own membership unmeasurable; '
        'that is not a different-person finding. The separate reference-sensitivity data measures this coupling.</p>'
        '<p>The table applies four categories to the <b>same active reference evidence</b>, ignoring physical locks for the numeric test. '
        'It does not rerun grouping, authorize admission or replace explicit intent. '
        'Saved installed score, active reassessed score and original-view score use different reference sets.</p>'
        '<p>The reference-sensitivity JSON compares category-floor-only versus strict-numeric construction using identical '
        'four-independent-support and four-pass limits. Both ignore explicit intent, final member vetoes and later boundaries '
        'to isolate the numerical floor. Neither is an approved core, and neither replaces the final shadow inventory.</p></section>'
        '<details><summary>Counts and limitations</summary><pre>'
        + html.escape(json.dumps({"summary": diagnostic["summary"], "limits": diagnostic["limits"]}, indent=2))
        + '</pre></details><p><a href="diagnostics.json">Exact own scores, reference IDs, counterfactuals and reference sensitivity</a></p>'
        '<label>Search filename, photo ID or identity <input id="filter"></label> '
        '<label>Show <select id="mode"><option value="all">All</option><option value="cast">Sisters / Angels</option>'
        '<option value="disagreement">Retainable but fails new-join recipe</option>'
        '<option value="starved">Only original-view score available</option></select></label>'
        '<p id="count"></p><button id="prev">Previous 50</button> <button id="next">Next 50</button>'
        '<table><thead><tr><th>Image / installed filename</th><th>Own-core evidence / why held</th>'
        '<th>Same evidence under other categories</th></tr></thead><tbody id="rows"></tbody></table>'
        '<h2>Bounded existing-CLIP region ablation</h2><p>No new model downloads or identity decisions. '
        'Head-context includes the face; below-face describes clothing/background, not identity. '
        'Same/different are previously supplied exact-photo labels, not new AI review.</p><pre>'
        + html.escape(json.dumps({k: v for k, v in cues.items() if k != "pairs"}, indent=2)) + '</pre>'
        + "".join(samples) + '<script type="application/json" id="data">' + payload + '</script><script>'
        + SCRIPT + '</script></html>'
    )


SCRIPT = r"""
const data=JSON.parse(document.getElementById("data").textContent),el=id=>document.getElementById(id);
const byId=new Map(data.map(r=>[r.photoId,r]));
let page=0,filtered=[];const score=n=>n===null?"unavailable":n.toFixed(3);
function refresh(reset=false){
 if(reset)page=0;const term=el("filter").value.toLowerCase(),mode=el("mode").value;
 filtered=data.filter(r=>(r.photoId+" "+r.oldFolder+" "+r.filename).toLowerCase().includes(term)&&
 (mode==="all"||(mode==="cast"&&/^(Sisters|Angels)\//.test(r.oldFolder))||
 (mode==="disagreement"&&r.retentionAdmissionDisagreement)||
 (mode==="starved"&&r.activeOwnScore===null&&r.bestOriginalViewScore!==null)));
 page=Math.min(page,Math.max(0,Math.ceil(filtered.length/50)-1));el("rows").replaceChildren();
 for(const r of filtered.slice(page*50,(page+1)*50)){
  const tr=document.createElement("tr"),photo=document.createElement("td"),a=document.createElement("a"),img=document.createElement("img");
  img.src=r.href;img.alt=r.filename;img.loading="lazy";img.decoding="async";a.href=r.href;a.target="_blank";a.rel="noopener";
  a.append(img,document.createElement("br"),document.createTextNode(r.filename));photo.append(a);
  const location=document.createElement("p");location.textContent=r.photoId+" / "+r.oldFolder;photo.append(location);
  img.onerror=()=>{const p=document.createElement("p");p.textContent="Image unavailable at installed path; filename link retained.";photo.append(p);};
  const evidence=document.createElement("td");
  evidence.textContent="Active reassessed own-core: "+score(r.activeOwnScore)+". Saved installed own-core: "+
   score(r.savedInstalledOwnScore)+". Best original own-view: "+score(r.bestOriginalViewScore)+
   " (not necessarily qualified). Active independent reference candidates: "+r.activeOwnReferencePhotoIds.length+
   ". Own minus strongest rival hypothesis: "+score(r.ownLeadOverAllHypotheses)+". Shadow verdict: "+r.assessmentStatus+
   "; action: "+r.disposition+". Physical action locks: "+(r.placementBlocks.join(", ")||"none")+
   ". Other reasons: "+(r.scopeAndDecisionReasons.join(", ")||"none")+". No file moves in this experiment.";
  if(r.rival){const p=document.createElement("p");p.textContent="Strongest rival hypothesis: "+r.rival.folder+
   "; score "+score(r.rival.score)+"; "+(r.rival.activeScore===null?"original/unqualified view, NOT an eligible receiving identity":
   "active view; admission still requires all safeguards")+". It is not a recommended move.";evidence.append(p);}
  const examples=document.createElement("details"),summary=document.createElement("summary");
  summary.textContent="Show own-core and strongest-rival reference examples (not a move recommendation)";examples.append(summary);
  let built=false;examples.ontoggle=()=>{
   if(!examples.open||built)return;built=true;
   const ownIds=r.activeOwnReferencePhotoIds.length?r.activeOwnReferencePhotoIds:r.bestOriginalViewReferences;
   const rivalIds=r.rival?(r.rival.referencePhotoIds.length?r.rival.referencePhotoIds:r.rival.frozenReferencePhotoIds):[];
   for(const [label,ids] of [[r.activeOwnReferencePhotoIds.length?"Active own-core examples":"Original-view examples; NOT qualified active support",ownIds],
                             [r.rival?.referencePhotoIds.length?"Strongest rival active examples; NOT a recommendation":
                              "Strongest rival original/unqualified examples; NOT receiving support",rivalIds]]){
    const h=document.createElement("p");h.textContent=label;examples.append(h);
    for(const id of ids.slice(0,4)){const ref=byId.get(id);if(!ref)continue;
     const a=document.createElement("a"),img=document.createElement("img");
     a.href=ref.href;a.target="_blank";a.rel="noopener";img.src=ref.href;img.alt=ref.filename;img.loading="lazy";
     img.onerror=()=>{img.replaceWith(document.createTextNode("Reference image unavailable; filename link retained."));};
     a.append(img,document.createElement("br"),document.createTextNode(ref.filename));examples.append(a);
    }
   }
  };evidence.append(examples);
  const compare=document.createElement("td");
  for(const c of r.categoryComparisons){
   const p=document.createElement("p");p.textContent=c.category+": new-join numeric gate "+(c.numericJoinPass?"PASS":"FAIL")+
    "; score floor "+c.joinFloor.toFixed(2)+"; support "+c.supportPhotoIds.length+"/"+c.requiredSupport+
    "; lead required "+c.joinMargin.toFixed(2)+". Existing-member handling (no locks): "+
    c.existingMemberConsistencyIgnoringLocks.decision+"; category core eligible: "+(c.categoryCoreEligible===null?"not measured":c.categoryCoreEligible)+
    ". "+c.numericJoinBlockers.join(", ")+". This is not a move recommendation.";compare.append(p);
  }tr.append(photo,evidence,compare);el("rows").append(tr);
 }
 el("count").textContent=filtered.length+" photos; page "+(page+1);el("prev").disabled=!page;el("next").disabled=(page+1)*50>=filtered.length;
}
el("filter").oninput=()=>refresh(true);el("mode").onchange=()=>refresh(true);
el("prev").onclick=()=>{page--;refresh()};el("next").onclick=()=>{page++;refresh()};refresh();
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        if not args.source.is_absolute():
            raise ValueError("--source must be absolute")
        out = output_path(args.out)
        if args.check or args.apply and out.exists():
            receipt = json.loads((out / "receipt.json").read_bytes())
            if receipt["source"] != str(args.source) or receipt["code"] != codes():
                raise ValueError("diagnostic source/code contract changed")
            verify({**receipt["inputs"], **receipt["code"]})
            verify({str(review_packet.safe_path(out, name)): digest for name, digest in receipt["outputs"].items()})
            print(f"Verified own-core/category and cue evidence: {out}")
            return 0
        state, run, vectors, cache, ledger, checkpoint, bindings = load(args.source)
        pairs, ids = sample_pairs(ledger, {r["photoId"]: r for r in state["rows"]}, vectors)
        print(f"Preview: {len(state['rows'])} own-core category comparisons; {len(pairs)} labelled cue controls, "
              f"{len(ids)} images, two regions; existing local CLIP only. No moves, new thresholds, LLM or human labels.")
        if not args.apply:
            return 0
        start = time.perf_counter()
        diagnostic = membership_diagnostics.build(state, run, vectors)
        reversed_state = {**state, "rows": list(reversed(state["rows"])),
                          "appearances": list(reversed(state["appearances"]))}
        reverse = membership_diagnostics.build(reversed_state, run, vectors)
        reverse["referenceSensitivity"].sort(key=lambda r: (r["appearanceId"], r["counterfactualCategory"]))
        diagnostic["referenceSensitivity"].sort(key=lambda r: (r["appearanceId"], r["counterfactualCategory"]))
        if diagnostic != reverse:
            raise ValueError("diagnostics differ under reverse ordering")
        staging = out.with_name(out.name + ".partial")
        staging.mkdir(parents=True, exist_ok=False)
        records, cold = descriptors(ids, run, cache, checkpoint, staging)
        (staging / "descriptors.json").write_text(json.dumps(records, allow_nan=False), encoding="utf-8")
        warm_records, warm = descriptors(
            list(reversed(ids)), run, cache, checkpoint, staging,
            saved=json.loads((staging / "descriptors.json").read_bytes()),
        )
        if records != warm_records or warm["extractions"] or warm["decodedImages"]:
            raise ValueError("unchanged warm cue extraction failed exact reuse")
        cues = {**cue_results(pairs, records, vectors), "cold": cold, "warm": warm}
        for name, value in (("diagnostics.json", diagnostic), ("cues.json", cues), ("descriptors.json", records)):
            (staging / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        (staging / "index.html").write_text(render(diagnostic, cues, records, run), encoding="utf-8")
        outputs = {p.name: shadow.digest(p) for p in staging.iterdir() if p.is_file()}
        selected = {p["photoId"]: p for p in run["photos"]}
        for pid in ids:
            path = review_packet.safe_path(pathlib.Path(run["workingRoot"]), selected[pid]["destination"])
            bindings[str(path)] = records[pid]["sourceSHA256"]
        receipt = {"source": str(args.source), "inputs": bindings, "code": codes(), "outputs": outputs,
                   "reverseVerified": True, "libraryWrites": 0, "identityDecisionsChanged": 0,
                   "elapsedSeconds": time.perf_counter()-start}
        verify({**bindings, **receipt["code"]})
        (staging / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        staging.rename(out)
        print("Own-core/category evidence:", diagnostic["summary"])
        print("Cue development ranking (not acceptance):", cues["developmentPairRankingAUC"])
        print(f"Published {out / 'index.html'} ({receipt['elapsedSeconds']:.3f}s).")
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(f"Likeness diagnostics failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
