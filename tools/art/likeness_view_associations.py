"""Publish member-first non-core associations without merging reference views."""
import argparse
import base64
import gzip
import html
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.art import likeness_hypothesis_trial as previous  # noqa: E402
from tools.art.likeness_library import entrance_trial, shadow, view_associations  # noqa: E402

publisher = previous.publisher


def comparison_projection(comparison):
    if comparison is None:
        return None
    result = {**comparison}
    for key in ("originalAnchors", "outsideRival", "sharedRival", "exclusiveRival", "exclusiveOriginalAnchors"):
        record = comparison[key]
        result[key] = {
            "referenceCount": len(record["referencePhotoIds"]),
            "independentReferenceCount": len(record["independentReferencePhotoIds"]),
            "supportCount": len(record["independentSupportPhotoIds"]),
            "centroidScore": record["centroidScore"],
            "examplePhotoIds": list(dict.fromkeys(
                record["independentSupportPhotoIds"] + record["referencePhotoIds"],
            ))[:3],
        }
    return result


def codes():
    paths = (pathlib.Path(__file__).resolve(), pathlib.Path(view_associations.__file__).resolve(),
             ROOT / "bin" / "likeness-view-associations.cmd")
    return {**previous.codes(), **{str(p): shadow.digest(p) for p in paths}}


def load_baseline(directory, source):
    receipt = json.loads((directory / "receipt.json").read_bytes())
    if (receipt["kind"] != "original-anchor-hypothesis-receipt" or receipt["source"] != str(source)
            or receipt["code"] != previous.codes() or not receipt["reverseVerified"]
            or receipt["installedMoves"] or receipt["recipe"] != entrance_trial.recipes()[1]):
        raise ValueError("non-core associations require unchanged verified original-anchor analysis")
    bindings = {
        **receipt["inputs"], **receipt["code"],
        str(directory / "receipt.json"): shadow.digest(directory / "receipt.json"),
        **{str(publisher.review_packet.safe_path(directory, p)): digest for p, digest in receipt["outputs"].items()},
    }
    publisher.diagnostics.verify(bindings)
    return json.loads((directory / "trial.json").read_bytes()), bindings


def render(result, run):
    photos = {p["photoId"]: p for p in run["photos"]}
    shown = {r["photoId"] for r in result["rows"]}
    for row in result["rows"]:
        for anchor in row["anchorEvidence"]:
            shown.update(anchor["supportPhotoIds"][:2])
        if row["outsideRival"]:
            shown.update(row["outsideRival"]["referencePhotoIds"][:4])
        comparison = comparison_projection(row["rivalReferenceComparison"])
        if comparison:
            for key in ("sharedRival", "exclusiveRival", "exclusiveOriginalAnchors"):
                shown.update(comparison[key]["examplePhotoIds"])
    sources = {}
    for pid in sorted(shown):
        path = publisher.review_packet.safe_path(pathlib.Path(run["workingRoot"]), photos[pid]["destination"])
        sources[pid] = {"href": path.as_uri(), "filename": path.name}
    projected = []
    for row in result["rows"]:
        item = {**row, "anchorEvidence": [
            {**a, "supportCount": len(a["supportPhotoIds"]), "supportPhotoIds": a["supportPhotoIds"][:2]}
            for a in row["anchorEvidence"]
        ]}
        item["entranceSupportCount"] = len(row["entranceSupportPhotoIds"])
        item.pop("entranceSupportPhotoIds")
        item["rivalReferenceComparison"] = comparison_projection(row["rivalReferenceComparison"])
        if row["outsideRival"]:
            item["outsideRival"] = {
                **row["outsideRival"], "referencePhotoIds": row["outsideRival"]["referencePhotoIds"][:4],
            }
        projected.append(item)
    payload = base64.b64encode(gzip.compress(
        json.dumps({
            "rows": projected, "sources": sources, "groups": [{
                key: g[key] for key in ("groupId", "sourceFolder", "sourceViewId", "displayOwner")
            } for g in result["groups"]],
        }, separators=(",", ":"), allow_nan=False).encode("utf-8"),
        mtime=0,
    )).decode("ascii")
    summary = html.escape(json.dumps(result["summary"], indent=2))
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        '<title>Non-core view associations — no installed changes</title><style>'
        'body{font:16px system-ui;background:#171c23;color:#eef3f8;max-width:1300px;margin:auto;padding:16px}'
        'a{color:#a7d6ff}article,section{border:1px solid #718096;padding:14px;margin:12px 0}'
        'p,pre{overflow-wrap:anywhere}pre{white-space:pre-wrap}input,select{font:inherit;max-width:100%}'
        'img{width:160px;height:190px;max-width:100%;object-fit:contain}'
        '.images{display:flex;flex-wrap:wrap;gap:12px}.images>a{max-width:210px;overflow-wrap:anywhere}</style>'
        '<h1>Smaller views: member evidence without a core merger</h1>'
        '<section><p><b>No installed changes. No review required now.</b> '
        'This constructs non-core association state, not new physical identity folders.</p>'
        '<p><b>Tentative non-core:</b> the photo passes forward evidence against every original anchor, '
        'but an outside score or action guard still blocks automatic admission. It is not assigned to the '
        'target person, does not acquire reference influence, and is not a certified appearance.</p>'
        '<p><b>Unsupported association:</b> this particular target lacks sufficient evidence or has an exact veto. '
        'It does not mean the existing placement is wrong. '
        '<b>Already qualified:</b> the saved baseline already proposed that person. '
        '<b>Qualified non-core proposal:</b> all per-member guards pass, but it is still NOT installed.</p>'
        '<p>The old view remains an outside competitor. No margin is waived because of an old folder. '
        'Witnesses come only from surviving original anchors, never other tentative photos.</p>'
        '<p><b>Reference overlap:</b> shared and exclusive reference examples explain why related hypotheses '
        'compete. Equal-content copies count as shared content, not new independent evidence. Subset scores '
        'are diagnostic centroids, not replacement margins or proof of a shared person.</p>'
        '<pre>' + summary + '</pre><a href="associations.json">Complete groups, photo-state ledger and exact evidence</a>'
        '<details><summary>Scope and limits</summary><pre>' + html.escape("\n".join(result["limits"]))
        + '</pre></details></section><label>Search <input id="search" placeholder="Folder, filename or photo ID"></label> '
        '<label>State <select id="state"><option value="all">All association candidates</option>'
        '<option value="tentative-non-core">Tentative non-core — not assigned</option>'
        '<option value="unsupported-association">Unsupported association — not a rejection</option>'
        '<option value="already-qualified-membership">Already qualified in baseline</option>'
        '<option value="qualified-non-core-proposal">New qualified non-core proposal — not installed</option>'
        '</select></label> <label>Candidate source group <select id="group">'
        '<option value="all">All candidate groups — not certified appearances</option></select></label>'
        '<p id="count"></p><button id="prev">Previous 20</button> '
        '<button id="next">Next 20</button><p id="loaderror" role="alert"></p><div id="rows"></div>'
        '<script id="data" type="application/octet-stream">' + payload + '</script><script>' + SCRIPT + '</script></html>'
    )


SCRIPT = r"""
async function start(){
const bytes=Uint8Array.from(atob(document.getElementById("data").textContent),c=>c.charCodeAt(0));
const decoded=new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
const {rows,sources,groups}=JSON.parse(await new Response(decoded).text()),el=id=>document.getElementById(id);
for(const g of groups){
 const option=document.createElement("option");option.value=g.groupId;
 option.textContent=g.sourceFolder+" → "+g.displayOwner+" ["+g.sourceViewId+"]";el("group").append(option);
}
let current=0; const score=v=>v===null||v===undefined?"unavailable":v.toFixed(3);
function add(parent,text){const p=document.createElement("p");p.textContent=text;parent.append(p);}
function picture(parent,pid){
 const src=sources[pid];if(!src){add(parent,"Source unavailable: "+pid);return;}
 const a=document.createElement("a"),img=document.createElement("img");a.href=src.href;a.target="_blank";a.rel="noopener";
 img.src=src.href;img.alt=src.filename;img.loading="lazy";img.decoding="async";
 img.onerror=()=>img.replaceWith(document.createTextNode("Image unavailable; original filename link retained."));
 a.append(img,document.createElement("br"),document.createTextNode(src.filename));parent.append(a);
}
function draw(reset=false){
 if(reset)current=0;const term=el("search").value.toLowerCase(),state=el("state").value,group=el("group").value;
 const filtered=rows.filter(r=>(state==="all"||r.status===state)&&(group==="all"||r.groupId===group)&&
  (r.photoId+" "+r.oldFolder+" "+r.displayOwner+" "+sources[r.photoId].filename).toLowerCase().includes(term));
 current=Math.min(current,Math.max(0,Math.ceil(filtered.length/20)-1));el("rows").replaceChildren();
 for(const r of filtered.slice(current*20,(current+1)*20)){
  const article=document.createElement("article"),images=document.createElement("div");images.className="images";
  picture(images,r.photoId);article.append(images);add(article,r.oldFolder+" / "+r.photoId);
  add(article,"State: "+r.status+". Candidate association: "+r.displayOwner+" — NOT installed.");
  add(article,"Original names: "+r.originalFolders.join(" / ")+". Source view: "+r.sourceViewId+".");
  add(article,"Saved own-core score: "+score(r.baselineOwnScore)+". Saved membership: "+r.baselineMembership+".");
  add(article,"Receiving comparison: "+(r.target?.folder??"unavailable")+" "+score(r.target?.score)+
   "; entrance floor "+(r.target?.admissionFloor??"unavailable")+"; independent original witnesses "+
   r.entranceSupportCount+"; signed lead "+score(r.lead)+"; required lead "+(r.target?.marginRequired??"unavailable")+".");
  if(r.outsideRival)add(article,"Strongest outside rival: "+r.outsideRival.folder+" "+score(r.outsideRival.score)+
   " ("+(r.outsideRival.active?"active":"original/unqualified fallback")+"). A rival is not a recommended destination.");
  const c=r.rivalReferenceComparison;
  if(c)add(article,"Reference overlap: "+c.kind+"; "+c.exactSharedPhotoIds.length+" exact shared IDs, "+
   c.equalContentSharedRivalPhotoIds.length+" additional equal-content rival IDs; "+
   c.exclusiveRival.referenceCount+" exclusive rival references. Diagnostic only; full margin unchanged.");
  add(article,"Evidence blockers: "+(r.supportBlockers.join(", ")||"none")+
   ". Action blockers: "+(r.actionBlockers.join(", ")||"none")+". Core use: forbidden; no files moved.");
  const details=document.createElement("details"),summary=document.createElement("summary");
  summary.textContent="Original-anchor witnesses and outside rival images";details.append(summary);let built=false;
  details.ontoggle=()=>{
   if(!details.open||built)return;built=true;
   for(const a of r.anchorEvidence){
    add(details,a.folder+": "+a.supportCount+" independent witnesses at "+a.floor+"; requires "+a.required+".");
    const pictures=document.createElement("div");pictures.className="images";
    for(const pid of a.supportPhotoIds)picture(pictures,pid);details.append(pictures);
   }
   if(r.outsideRival){
    add(details,"Strongest outside rival reference examples");const pictures=document.createElement("div");pictures.className="images";
    for(const pid of r.outsideRival.referencePhotoIds)picture(pictures,pid);details.append(pictures);
   }
   if(c){
    add(details,"Subset centroids/support at "+c.supportFloor+
     " are diagnostics, not new admission gates. Support is independent within each subset, not additive across subsets.");
    for(const [key,label] of [["originalAnchors","All surviving original anchors"],["outsideRival","Full outside rival"],
      ["sharedRival","Shared-content rival references"],["exclusiveRival","Exclusive rival references"],
      ["exclusiveOriginalAnchors","Exclusive original-anchor references"]]){
     const v=c[key];add(details,label+": "+v.referenceCount+" references; "+v.independentReferenceCount+
      " independent; "+v.supportCount+" independent query supporters; centroid "+score(v.centroidScore)+".");
     if(["sharedRival","exclusiveRival","exclusiveOriginalAnchors"].includes(key)){
      const pictures=document.createElement("div");pictures.className="images";
      for(const pid of v.examplePhotoIds)picture(pictures,pid);details.append(pictures);
     }
    }
   }else add(details,"Reference overlap unavailable: no eligible receiving comparison and outside rival.");
  };article.append(details);el("rows").append(article);
 }
 el("count").textContent=filtered.length+" association rows; page "+(current+1)+
  ". A photo may have multiple candidate associations; counts are not new assigned photos.";
 el("prev").disabled=!current;el("next").disabled=(current+1)*20>=filtered.length;
}
el("search").oninput=()=>draw(true);el("state").onchange=()=>draw(true);el("group").onchange=()=>draw(true);
el("prev").onclick=()=>{current--;draw()};el("next").onclick=()=>{current++;draw()};draw();
}
start().catch(error=>{
 document.getElementById("loaderror").textContent="Unable to load association viewer: "+error.message+
 ". Complete evidence is in associations.json; this is a viewer error, not an identity result.";console.error(error);
});
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--baseline", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if not args.source.is_absolute() or not args.baseline.is_absolute():
            raise ValueError("--source and --baseline must be absolute")
        out = publisher.output_path(args.out)
        if out.resolve() in (args.source.resolve(), args.baseline.resolve()):
            raise ValueError("output must be separate from both inputs")
        if args.check or args.apply and out.exists():
            receipt = json.loads((out / "receipt.json").read_bytes())
            if (receipt["kind"] != "non-core-view-association-receipt"
                    or receipt["source"] != str(args.source) or receipt["baseline"] != str(args.baseline)
                    or receipt["code"] != codes() or not receipt["reverseVerified"]
                    or receipt["installedMoves"] or receipt["recipe"] != entrance_trial.recipes()[1]):
                raise ValueError("association source/code/recipe contract changed")
            publisher.diagnostics.verify({**receipt["inputs"], **receipt["code"]})
            publisher.diagnostics.verify({
                str(publisher.review_packet.safe_path(out, p)): digest for p, digest in receipt["outputs"].items()
            })
            print(f"Verified non-core view associations: {out}")
            return 0
        baseline, bindings = load_baseline(args.baseline, args.source)
        state, run, vectors, _, ledger, _, source_bindings = publisher.diagnostics.load(args.source)
        bindings.update(source_bindings)
        published = {p["path"]: p["sha256"] for p in run["publishedFiles"]}
        for photo in run["photos"]:
            path = publisher.review_packet.safe_path(pathlib.Path(run["workingRoot"]), photo["destination"])
            expected = published.get(photo["destination"])
            if not expected or shadow.digest(path) != expected:
                raise ValueError(f"installed viewer source differs: {photo['photoId']}")
            bindings[str(path)] = expected
        code = codes()
        print(
            f"Preview: {len(state['rows'])} conserved photos; only uncertified union-lineage views. "
            "Frozen original-anchor witnesses, unchanged full rivals, per-photo non-core association state. "
            "No new core references, installed moves, models, editing, 944x1104 generation or intake.",
            flush=True,
        )
        if not args.apply:
            return 0
        start = time.perf_counter()
        result = view_associations.build(state, run, vectors, ledger, baseline)
        reverse = view_associations.build(
            {**state, "rows": state["rows"][::-1], "appearances": state["appearances"][::-1]},
            run, dict(reversed(list(vectors.items()))), {**ledger, "pairs": ledger["pairs"][::-1]}, baseline,
        )
        if result != reverse:
            raise ValueError("non-core associations differ under reversed inputs")
        stage = out.with_name(out.name + ".partial")
        stage.mkdir(parents=True, exist_ok=False)
        (stage / "associations.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        (stage / "index.html").write_text(render(result, run), encoding="utf-8")
        outputs = {p.name: shadow.digest(p) for p in stage.iterdir()}
        publisher.diagnostics.verify({**bindings, **code})
        receipt = {
            "kind": "non-core-view-association-receipt", "source": str(args.source),
            "baseline": str(args.baseline), "inputs": bindings, "code": code, "outputs": outputs,
            "recipe": entrance_trial.recipes()[1], "reverseVerified": True, "installedMoves": 0,
            "elapsedSeconds": time.perf_counter() - start,
        }
        (stage / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        stage.rename(out)
        print(f"Published {out / 'index.html'} ({receipt['elapsedSeconds']:.3f}s): {result['summary']}")
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(f"Non-core association trial failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
