"""Explore ordered entrance/core/retention ranges without changing installed policy."""
import argparse
import base64
import copy
import gzip
import hashlib
import html
import json
import pathlib
import shutil
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.art import likeness_diagnostics as diagnostics  # noqa: E402
from tools.art.likeness_library import (  # noqa: E402
    directed_reformation, entrance_trial, review_packet, shadow, view_reconciliation,
)
from tools.art.likeness_review_packet import output_path  # noqa: E402


def codes(*, directed=False):
    paths = (pathlib.Path(__file__).resolve(), pathlib.Path(entrance_trial.__file__).resolve(),
             pathlib.Path(view_reconciliation.__file__).resolve(),
             ROOT / "bin" / "likeness-entrance-trial.cmd")
    if directed:
        paths = (*paths, pathlib.Path(directed_reformation.__file__).resolve())
    return {**diagnostics.codes(), **{str(p): shadow.digest(p) for p in paths}}


def semantic(result):
    value = copy.deepcopy(result)
    for variant in value["variants"]:
        variant["summary"].pop("elapsedSeconds")
    return value


def display_payload(result, sources):
    unions = result.get("viewReconciliation") or {"unions": []}
    display = {"variants": [], "defaultVariant": result.get("defaultVariant", "ordered-middle"), "unionOwners": {
        row["personId"]: {"owner": row["provisionalDisplayOwner"], "names": row["originalFolders"]}
        for row in unions["unions"]
    }}
    baseline = next(v for v in result["variants"] if v["recipe"]["name"] == "ordered-middle")
    by_id = {r["photoId"]: r for r in baseline["rows"]}
    for variant in result["variants"]:
        control_name = "ordered-middle-coalesced" + ("-growth" if variant["recipe"]["growth"] else "")
        paired = next((v for v in result["variants"] if v["recipe"]["name"] == control_name), None)
        paired_rows = {r["photoId"]: r for r in paired["rows"]} if paired else {}
        rows = []
        for row in variant["rows"]:
            projected = {k: row[k] for k in (
                "photoId", "oldFolder", "membership", "proposalPersonId", "logicalRelease",
                "placementBlocks", "corePromotionStaged", "lead", "entranceBlockers",
            )}
            projected["lostAdmissionVersusMiddle"] = bool(
                by_id[row["photoId"]]["proposalPersonId"] and not row["proposalPersonId"]
            )
            previous = paired_rows.get(row["photoId"])
            projected["admissionRestoredVersusCoalesced"] = bool(
                previous and not previous["proposalPersonId"] and row["proposalPersonId"]
            )
            projected["comparisonControlName"] = control_name if paired else None
            projected["reconciledViewIds"] = row.get("reconciledViewIds", [])
            competitor = row.get("competingView")
            projected["competingView"] = None if competitor is None else {
                **{k: competitor[k] for k in (
                    "folder", "score", "active", "reconciliationStatus", "exactConflicts",
                )},
                "referencePhotoIds": competitor["referencePhotoIds"][:4],
                "exceptionPhotoIds": competitor["exceptionPhotoIds"][:4],
                "exceptionCount": len(competitor["exceptionPhotoIds"]),
            }
            for key in ("own", "best"):
                record = row[key]
                projected[key] = None if record is None else {
                    **{k: record[k] for k in ("category", "folder", "activeScore", "originalScore", "independentCount")},
                    "referencePhotoIds": record["referencePhotoIds"][:4],
                    "originalReferencePhotoIds": record["originalReferencePhotoIds"][:4],
                }
            rows.append(projected)
        display["variants"].append({"recipe": variant["recipe"], "summary": variant["summary"], "rows": rows})
    raw = json.dumps({"result": display, "sources": sources}, allow_nan=False, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(gzip.compress(raw, mtime=0)).decode("ascii")


def render(result, source, run):
    photos = {p["photoId"]: p for p in run["photos"]}
    sources = {}
    for row in source["rows"]:
        path = review_packet.safe_path(pathlib.Path(run["workingRoot"]), photos[row["photoId"]]["destination"])
        sources[row["photoId"]] = {
            "href": path.as_uri(), "filename": path.name, "oldFolder": row["oldFolder"],
            "oldDisposition": row["disposition"],
        }
    summary = []
    for variant in result["variants"]:
        r, s = variant["recipe"], variant["summary"]
        counts = s["membership"]
        unavailable = sum(n for k, n in counts.items() if k.startswith("comparison-"))
        summary.append(
            "<tr><td>" + html.escape(r["name"]) + "</td><td>"
            + " / ".join(f'{r["admission"][c]:.2f}' for c in entrance_trial.LADDER[:4])
            + "</td><td>" + str(counts.get("retention-compatible-not-identity-confirmation", 0))
            + "</td><td>" + str(unavailable) + "</td><td>" + str(s["logicalReleases"])
            + "</td><td>" + str(s["crossFolderProposals"]) + "</td><td>"
            + str(s["referenceCount"]) + " (+" + str(s["addedReferenceOccurrences"]) + ")</td><td>"
            + ("stable frozen inventory" if s["stable"] else "INCOMPLETE; automatic proposals suppressed")
            + "</td></tr>"
        )
    reconciliation = result["viewReconciliation"]
    union_summary = ""
    if reconciliation is not None:
        baseline = next(v for v in result["variants"] if v["recipe"]["name"] == "ordered-middle")
        coalesced = next(v for v in result["variants"] if v["recipe"]["name"] == "ordered-middle-coalesced")
        base_rows = {r["photoId"]: r for r in baseline["rows"]}
        gained = sum(bool(r["proposalPersonId"] and not base_rows[r["photoId"]]["proposalPersonId"])
                     for r in coalesced["rows"])
        lost = sum(bool(not r["proposalPersonId"] and base_rows[r["photoId"]]["proposalPersonId"])
                   for r in coalesced["rows"])
        union_summary = (
            '<section><h2>Paired reference-view reconciliation</h2><p>'
            + str(len(reconciliation["unions"])) + ' provisional art-identity unions from '
            + str(len(reconciliation["qualifyingEdges"])) + ' qualifying mutual-reference edges. '
            'Only participating reference views share a provisional person; other old views remain separate rivals. '
            'Every image still requires individual admission. No real-world identification, new character names or family facts.</p>'
            '<p><b>Check gains AND regressions:</b> versus ordered middle, coalescence newly qualifies '
            + str(gained) + ' photos but no longer qualifies ' + str(lost)
            + '. The latter remain physically unchanged; use the regression filter below. '
            'Reviewed positive-pair co-assignment is '
            + str(baseline["summary"]["exactPairControls"].get("sameCoassigned", 0)) + ' → '
            + str(coalesced["summary"]["exactPairControls"].get("sameCoassigned", 0))
            + '; labels are reused development controls, not blind accuracy. Negative/uncertain vetoes are enforced, not an independent purity measurement.</p>'
            '<details><summary>Original names, reference witnesses and limits</summary><pre>'
            + html.escape(json.dumps({k: v for k, v in reconciliation.items()
                                      if k != "hypothesisReconciliation"}, indent=2))
            + '</pre></details></section>'
        )
    hypothesis_summary = ""
    hypotheses = reconciliation.get("hypothesisReconciliation") if reconciliation else None
    if hypotheses:
        comparisons = []
        for variant in result["variants"]:
            if "reconciledViews" not in variant["summary"]:
                continue
            control_name = "ordered-middle-coalesced" + ("-growth" if variant["recipe"]["growth"] else "")
            control = next(v for v in result["variants"] if v["recipe"]["name"] == control_name)
            previous = {r["photoId"]: r for r in control["rows"]}
            gains = sum(bool(r["proposalPersonId"] and not previous[r["photoId"]]["proposalPersonId"])
                        for r in variant["rows"])
            losses = sum(bool(not r["proposalPersonId"] and previous[r["photoId"]]["proposalPersonId"])
                         for r in variant["rows"])
            comparisons.append(
                '<li>' + html.escape(variant["recipe"]["name"]) + ': '
                + str(gains) + ' newly qualified, ' + str(losses)
                + ' no longer qualified versus ' + html.escape(control_name) + '; '
                + str(sum(r["accepted"] for r in hypotheses["checks"])) + ' complete views reconciled.</li>'
            )
        view_rows = []
        for check in hypotheses["checks"]:
            key = check["candidateViewId"]
            forward = {r["photoId"] for c in check["comparisons"] for r in c["unsupportedReferences"]
                       if r["sourceViewId"] == key}
            reverse = {r["photoId"] for c in check["comparisons"] for r in c["unsupportedReferences"]
                       if r["sourceViewId"] != key}
            view_rows.append(
                '<tr><td>' + html.escape(check["folder"]) + '<br>' + html.escape(key)
                + '</td><td>' + str(len(check["referencePhotoIds"])) + '</td><td>'
                + ("Qualified complete view" if check["accepted"] else "Separate rival retained")
                + '</td><td>' + str(len(forward)) + '</td><td>' + str(len(reverse)) + '</td></tr>'
            )
        hypothesis_summary = (
            '<section><h2>Original-anchor multi-view reconciliation</h2>'
            '<p>Reused controls are unchanged saved scores, not fresh reruns. New variants examine only views '
            'from the three provisional unions. Every reference must have two independent witnesses in every '
            'original anchor, in both directions. Accepted candidate views must also pass each other, and '
            'the whole expanded core must qualify. Original names and every uncertified/outside rival remain.</p><ul>'
            + "".join(comparisons) + '</ul><p><b>An uncertified view is not merged.</b> One unsupported reference '
            'blocks the complete view; this is a view-certification exception, not an eviction or a different-person finding. '
            'The strongest remaining rival and example exceptions appear beside each new result. '
            'Complete witnesses and failed-reference directions are in trial.json. '
            'A small view can support the main core yet lack enough independent images to witness every core member '
            'in return. That is insufficient two-way coverage, not proof of contamination.</p>'
            '<div class="tablewrap"><table><thead><tr><th>Candidate view</th><th>References</th><th>Handling</th>'
            '<th>Candidate references lacking anchor support</th><th>Anchor/peer references lacking candidate support</th>'
            '</tr></thead><tbody>' + "".join(view_rows) + '</tbody></table></div></section>'
        )
    payload = display_payload(result, sources)
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        '<title>Entrance and core experiments — no installed changes</title><style>'
        'body{font:16px system-ui;background:#171c23;color:#eef3f8;max-width:1450px;margin:auto;padding:16px}'
        'a{color:#a7d6ff}td,th{border:1px solid #718096;padding:8px;vertical-align:top;overflow-wrap:anywhere}'
        'table{border-collapse:collapse;width:100%;min-width:880px;table-layout:fixed}.tablewrap{overflow-x:auto}'
        'img{width:160px;height:190px;max-width:100%;object-fit:contain}'
        'article,section{border:1px solid #718096;padding:14px;margin:12px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere}'
        'select,input{font:inherit;max-width:100%}.images{display:flex;flex-wrap:wrap;gap:12px}'
        '.images>a{max-width:210px;overflow-wrap:anywhere}p{overflow-wrap:anywhere}</style>'
        '<h1>Test the rules, not your ability to sort thousands of photos</h1>'
        '<section><p><b>No installed photos or settings changed. No review required now.</b> '
        'These ranges test a consistent Sisters → Angels → Models → Prospects ladder. Each category is no stricter '
        'than the category above it for entrance, core, retention and margin. Model settings no longer exceed Angel settings.</p>'
        '<p><b>Four separate decisions:</b> retaining a compatible non-core member; admitting a new member; qualifying a core reference; '
        'and blocking a physical action. Core qualification does not acquire protection. A weak score alone does not promote or move a photo.</p>'
        '<p><b>Comparison unavailable means the experiment needs better evidence.</b> It does not mean wrong person, '
        'a release, an empty Gallery, or work you must do. Logical releases require measured low own support or an exact conflict; '
        'even those are uninstalled experimental outcomes, not confirmed errors.</p>'
        '<p>Automatic core additions require an entrance-qualified member, independent original-base witnesses and no competing winner. '
        'They enter only at the next frozen boundary; no chained growth or quota-filling promotion. '
        'Original views remain visible. In the paired coalescence variants, mutually qualified reference views share a '
        'provisional art identity; other views remain separate competitors. This is not a full regrouping/rebase.</p></section>'
        '<h2>Same photos, different experimental ranges</h2><div class="tablewrap"><table><thead><tr>'
        '<th>Variant</th><th>Entrance S / A / M / P</th><th>Retain-compatible<br>not confirmation</th>'
        '<th>Comparison unavailable<br>not rejected</th><th>Logical release<br>not moved</th>'
        '<th>Cross-folder proposals<br>not moved</th><th>Reference occurrences<br>net additions</th>'
        '<th>Experiment completeness</th></tr></thead><tbody>'
        + "".join(summary) + '</tbody></table></div>' + union_summary + hypothesis_summary
        + '<p><a href="trial.json">Exact recipes, reference IDs, boundaries and development controls</a></p>'
        '<details><summary>Limits and interpretation</summary><pre>'
        + html.escape("\n".join(result["limits"])) + '</pre></details>'
        '<h2>See why a result changed</h2><label>Variant <select id="variant"></select></label> '
        '<label>Search <input id="search" placeholder="Identity, filename or photo ID"></label> '
        '<label>Filter <select id="filter"><option value="all">All photos</option>'
        '<option value="unavailable">Comparison unavailable — not rejected</option>'
        '<option value="release">Logical release — not installed</option>'
        '<option value="move">Cross-folder proposal — not installed</option>'
        '<option value="growth">Staged core addition</option></select></label>'
        '<label>New admission versus matching coalesced control <input id="restored" type="checkbox"></label> '
        '<label>Lost admission versus ordered middle <input id="regressions" type="checkbox"></label>'
        '<p id="count"></p><button id="prev">Previous 40</button> <button id="next">Next 40</button>'
        '<p id="loaderror" role="alert"></p><div id="rows"></div><script type="application/octet-stream" id="data">'
        + payload + '</script><script>' + SCRIPT + '</script></html>'
    )


SCRIPT = r"""
async function start(){
const bytes=Uint8Array.from(atob(document.getElementById("data").textContent),c=>c.charCodeAt(0));
const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
const {result,sources}=JSON.parse(await new Response(stream).text()),el=id=>document.getElementById(id);
let pageNumber=0,filtered=[];
const score=value=>value===null||value===undefined?"unavailable":value.toFixed(3);
const add=(parent,text)=>{const p=document.createElement("p");p.textContent=text;parent.append(p);return p;};
function picture(parent,pid){
 const src=sources[pid];if(!src){add(parent,"Reference source unavailable: "+pid);return;}
 const a=document.createElement("a"),img=document.createElement("img");a.href=src.href;a.target="_blank";a.rel="noopener";
 img.src=src.href;img.alt=src.filename;img.loading="lazy";img.decoding="async";
 img.onerror=()=>{img.replaceWith(document.createTextNode("Image unavailable; original filename link retained."));};
 a.append(img,document.createElement("br"),document.createTextNode(src.filename));parent.append(a);
}
for(const variant of result.variants){const option=document.createElement("option");option.value=variant.recipe.name;
 option.textContent=variant.recipe.name;el("variant").append(option);}
el("variant").value=result.defaultVariant;
function draw(reset=false){
 if(reset)pageNumber=0;const variant=result.variants.find(v=>v.recipe.name===el("variant").value);
 const term=el("search").value.toLowerCase(),mode=el("filter").value;
 filtered=variant.rows.filter(r=>(r.photoId+" "+r.oldFolder+" "+sources[r.photoId].filename).toLowerCase().includes(term)&&
 (mode==="all"||(mode==="unavailable"&&r.membership.startsWith("comparison-"))||(mode==="release"&&r.logicalRelease)||
 (mode==="move"&&r.proposalPersonId&&r.best.folder!==r.oldFolder)||(mode==="growth"&&r.corePromotionStaged))&&
 (!el("regressions").checked||r.lostAdmissionVersusMiddle)&&
 (!el("restored").checked||r.admissionRestoredVersusCoalesced));
 pageNumber=Math.min(pageNumber,Math.max(0,Math.ceil(filtered.length/40)-1));el("rows").replaceChildren();
 for(const r of filtered.slice(pageNumber*40,(pageNumber+1)*40)){
  const article=document.createElement("article"),images=document.createElement("div");images.className="images";
  picture(images,r.photoId);article.append(images);
  add(article,r.oldFolder+" / "+r.photoId);
  add(article,"Existing membership: "+r.membership+". Original shadow action: "+sources[r.photoId].oldDisposition+".");
  add(article,"Own score: "+score(r.own?.activeScore)+"; original-view score: "+score(r.own?.originalScore)+
   "; independent own references: "+(r.own?.independentCount??0)+".");
  const category=r.own?.category??r.oldFolder.split("/")[0],recipe=variant.recipe;
  if(recipe.retain[category]!==undefined)add(article,"This category: retention floor "+recipe.retain[category]+
   "; core floor "+recipe.core[category]+" with "+recipe.coreSupport+" independent witnesses; entrance floor "+
   recipe.admission[category]+" with "+recipe.joinSupport+" witnesses; lead "+recipe.margin[category]+".");
  const union=result.unionOwners[r.proposalPersonId];
  add(article,"Entrance proposal: "+(r.proposalPersonId?(union?union.owner+" — provisional shared art identity":r.best.folder)+" — NOT installed":"none")+
   "; best active comparison "+(r.best?.folder??"unavailable")+" "+score(r.best?.activeScore)+
   "; signed lead over every outside art-identity hypothesis "+score(r.lead)+". Blockers: "+r.entranceBlockers.join(", ")+".");
  if(union)add(article,"Preserved original names: "+union.names.join(" / ")+". Display owner is not a physical rename or an identity fact.");
  if(r.competingView){
   const rival=r.competingView;
   add(article,"Strongest outside rival: "+rival.folder+" "+score(rival.score)+
    " ("+(rival.active?"active":"original/unqualified fallback")+"). View handling: "+rival.reconciliationStatus+
    "; "+rival.exceptionCount+" reference exceptions; exact conflicts: "+rival.exactConflicts.length+
    ". A rival is not a recommended destination.");
  }
  if(r.reconciledViewIds.length)add(article,"Target includes "+r.reconciledViewIds.length+
   " additional fully witnessed view(s); no other old views were carried along.");
  if(r.admissionRestoredVersusCoalesced)add(article,"Newly qualified versus "+r.comparisonControlName+
   ". Still a proposal only; no installed move.");
  if(r.lostAdmissionVersusMiddle)add(article,"Regression to inspect: ordered middle qualified an admission here; this variant does not. This does not evict or move the photo.");
  add(article,"Logical release: "+r.logicalRelease+"; core addition staged: "+r.corePromotionStaged+
   "; physical locks: "+(r.placementBlocks.join(", ")||"none")+". No files moved.");
  const details=document.createElement("details"),summary=document.createElement("summary");
  summary.textContent="Own-core / proposed-target reference examples";details.append(summary);let built=false;
  details.ontoggle=()=>{if(!details.open||built)return;built=true;
   for(const [name,comparison] of [["Own",r.own],["Best active comparison, not necessarily a proposal",r.best]]){
    if(!comparison)continue;const refs=comparison.referencePhotoIds.length?comparison.referencePhotoIds:comparison.originalReferencePhotoIds;
    add(details,name+": "+comparison.folder+"; "+(comparison.activeScore===null?"original/unqualified examples":"active reference examples"));
    const pictures=document.createElement("div");pictures.className="images";for(const pid of refs.slice(0,4))picture(pictures,pid);details.append(pictures);
   }
   if(r.competingView){
    for(const [name,refs] of [["Strongest rival reference examples",r.competingView.referencePhotoIds],
     ["View-certification exception examples, not rejected photos",r.competingView.exceptionPhotoIds]]){
     if(!refs.length)continue;add(details,name);const pictures=document.createElement("div");pictures.className="images";
     for(const pid of refs)picture(pictures,pid);details.append(pictures);
    }
   }};article.append(details);el("rows").append(article);
 }
 el("count").textContent=filtered.length+" photos; page "+(pageNumber+1)+"; "+(variant.summary.stable?"frozen inventory stable — accuracy not accepted":"INCOMPLETE experiment");
 el("prev").disabled=!pageNumber;el("next").disabled=(pageNumber+1)*40>=filtered.length;
}
el("variant").onchange=()=>draw(true);el("search").oninput=()=>draw(true);el("filter").onchange=()=>draw(true);
el("regressions").onchange=()=>draw(true);
el("restored").onchange=()=>draw(true);
el("prev").onclick=()=>{pageNumber--;draw()};el("next").onclick=()=>{pageNumber++;draw()};draw();
}
start().catch(error=>{
 document.getElementById("loaderror").textContent="Unable to load experiment display: "+error.message+
 ". Complete scored evidence is available in trial.json; this is a viewer error, not an identity result.";
 console.error(error);
});
"""


def load_reuse(directory, source, coalesce):
    receipt = json.loads((directory / "receipt.json").read_bytes())
    publisher = str(pathlib.Path(__file__).resolve())
    current = {p: digest for p, digest in codes().items() if p != publisher}
    previous = {p: digest for p, digest in receipt["code"].items() if p != publisher}
    if (receipt["kind"] != "entrance-range-trial-receipt" or receipt["source"] != str(source)
            or receipt["coalesce"] != coalesce or not receipt["reverseVerified"]
            or receipt["installedMoves"] or receipt["recipes"] != entrance_trial.recipes()
            or previous != current):
        raise ValueError("reuse requires identical source, recipes and analysis; only publisher may change")
    inputs = {
        **receipt["inputs"], **previous,
        str(directory / "receipt.json"): shadow.digest(directory / "receipt.json"),
        **{str(review_packet.safe_path(directory, name)): digest for name, digest in receipt["outputs"].items()},
    }
    diagnostics.verify(inputs)
    return json.loads((directory / "trial.json").read_bytes()), inputs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    parser.add_argument("--coalesce", action="store_true", help="Add paired mutual-reference-view union variants")
    parser.add_argument("--directed", action="store_true",
                        help="Compare bounded directed reformation recipes; report only, never install")
    parser.add_argument("--reuse-result", type=pathlib.Path, help="Republish unchanged verified scores after publisher-only changes")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if not args.source.is_absolute():
            raise ValueError("--source must be absolute")
        if args.directed and (args.coalesce or args.reuse_result):
            raise ValueError("--directed is an independent report mode; it cannot coalesce or reuse entrance results")
        out = output_path(args.out)
        code = codes(directed=args.directed)
        if args.check or args.apply and out.exists():
            receipt = json.loads((out / "receipt.json").read_bytes())
            if args.directed:
                if (receipt.get("kind") != "directed-reformation-shadow-receipt"
                        or receipt.get("source") != str(args.source)
                        or receipt.get("code") != code
                        or receipt.get("recipes") != directed_reformation.recipes()
                        or not receipt.get("reverseVerified") or receipt.get("installedMoves") != 0
                        or receipt.get("libraryWrites") != 0 or receipt.get("imageReads") != 0
                        or receipt.get("modelCalls") != 0):
                    raise ValueError("directed shadow source/code/recipe contract changed")
                state, run, _, _, _, _ = directed_reformation.load_saved_source(args.source)
                locations = directed_reformation.resolve_photo_locations(state, run)
                location_hash = hashlib.sha256(json.dumps(locations, sort_keys=True).encode("utf-8")).hexdigest()
                if receipt.get("imageLocationSHA256") != location_hash:
                    raise ValueError("directed viewer current location map changed; historical report is preserved")
            else:
                if (receipt["kind"] != "entrance-range-trial-receipt" or receipt["source"] != str(args.source)
                        or receipt["code"] != code or receipt["recipes"] != entrance_trial.recipes()
                        or receipt["coalesce"] != args.coalesce
                        or not receipt["reverseVerified"] or receipt["installedMoves"]):
                    raise ValueError("entrance trial source/code/recipe contract changed")
                if receipt.get("reuseResult") != (str(args.reuse_result) if args.reuse_result else None):
                    raise ValueError("entrance trial reuse-source contract changed")
            diagnostics.verify({**receipt["inputs"], **receipt["code"]})
            diagnostics.verify({str(review_packet.safe_path(out, p)): digest for p, digest in receipt["outputs"].items()})
            print(f"Verified {'directed reformation shadow' if args.directed else 'ordered entrance/core trial'}: {out}")
            return 0
        if args.directed:
            state, run, vectors, ledger, bindings, source_integrity = \
                directed_reformation.load_saved_source(args.source)
            for recipe in directed_reformation.recipes():
                directed_reformation.validate_recipe(recipe)
            print(
                f"Preview: {len(state['rows'])} saved photos, current ordered-middle control and "
                f"{len(directed_reformation.recipes())} directed paired recipes. "
                "Mutual-subset reconciliation and capped frozen evidence recovery; no photo reads/copies, image processing, model calls, "
                f"library writes or installed moves. Historical code drift: "
                f"{len(source_integrity['historicalImplementationDrift'])} bound implementation(s); "
                "saved vectors are reused without historical algorithm replay.",
                flush=True,
            )
            if not args.apply:
                return 0
            start = time.perf_counter()
            result = directed_reformation.run_sweep(
                state, run, vectors, ledger,
                progress=lambda message: print(f"[{time.perf_counter() - start:.1f}s] {message}", flush=True),
                source_integrity=source_integrity,
            )
            report_result = directed_reformation.compact_for_report(result)
            page_result = directed_reformation.summary_for_page(report_result)
            photo_locations = directed_reformation.resolve_photo_locations(state, run)
            catalog_path = pathlib.Path(run["workingRoot"]) / ".likeness-library.json"
            if catalog_path.is_file():
                bindings[str(catalog_path)] = shadow.digest(catalog_path)
            unavailable = sorted(
                pid for pid, item in photo_locations.items() if item["status"] != "available"
            )
            page_result["imageAvailability"] = {
                "resolver": "unique current stable photo ID + current catalogue content binding; historical destination fallback",
                "destinationCount": len(photo_locations),
                "availableCount": len(photo_locations) - len(unavailable),
                "missingOrUnsafeCount": len(unavailable),
                "missingOrUnsafePhotoIds": unavailable,
                "imageBytesReadOrCopied": 0,
            }
            staging = out.with_name(out.name + ".partial")
            staging.mkdir(parents=True, exist_ok=False)
            detail_bytes = json.dumps(report_result, indent=2, allow_nan=False).encode("utf-8")
            (staging / "directed-details.json.gz").write_bytes(
                gzip.compress(detail_bytes, compresslevel=6, mtime=0),
            )
            (staging / "directed.json").write_text(
                json.dumps(page_result, indent=2, allow_nan=False) + "\n", encoding="utf-8",
            )
            (staging / "index.html").write_text(
                directed_reformation.render(report_result, photo_locations), encoding="utf-8",
            )
            outputs = {path.name: shadow.digest(path) for path in staging.iterdir()}
            diagnostics.verify({**bindings, **code})
            receipt = {
                "kind": "directed-reformation-shadow-receipt", "source": str(args.source),
                "inputs": bindings, "code": code, "outputs": outputs,
                "recipes": directed_reformation.recipes(),
                "reverseVerified": result["verification"]["reverseOrderVerified"],
                "imageLocationSHA256": hashlib.sha256(
                    json.dumps(photo_locations, sort_keys=True).encode("utf-8")
                ).hexdigest(),
                "installedMoves": 0, "libraryWrites": 0, "imageReads": 0, "modelCalls": 0,
                "elapsedSeconds": time.perf_counter() - start,
            }
            (staging / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            staging.rename(out)
            print(f"Published {out / 'index.html'} ({receipt['elapsedSeconds']:.3f}s).")
            return 0
        state, run, vectors, _, ledger, _, bindings = diagnostics.load(args.source)
        for recipe in entrance_trial.recipes():
            entrance_trial.validate_recipe(recipe)
        published = {p["path"]: p["sha256"] for p in run["publishedFiles"]}
        for photo in run["photos"]:
            path = review_packet.safe_path(pathlib.Path(run["workingRoot"]), photo["destination"])
            expected = published.get(photo["destination"])
            if not expected or shadow.digest(path) != expected:
                raise ValueError(f"installed viewer source differs: {photo['photoId']}")
            bindings[str(path)] = expected
        reused = None
        if args.reuse_result:
            if not args.reuse_result.is_absolute() or args.reuse_result.resolve() == out:
                raise ValueError("--reuse-result must be a different absolute verified report directory")
            reused, reused_bindings = load_reuse(args.reuse_result, args.source, args.coalesce)
            bindings.update(reused_bindings)
        print(f"Preview: {len(state['rows'])} saved photos, eight ordered same-input range variants"
              + (" plus two paired reference-view coalescence variants; " if args.coalesce else "; ")
              +
              "separate retention/entrance/core/protection, one staged growth boundary. "
              "All original rivals; no models, downloads, installed writes or intake.", flush=True)
        if reused:
            print("Reuse verified numerical results: publisher only; no scoring or model calls.", flush=True)
        if not args.apply:
            return 0
        start = time.perf_counter()
        result = reused
        if result is None:
            result = entrance_trial.run_sweep(
                state, run, vectors, ledger, progress=lambda s: print(s, flush=True), coalesce=args.coalesce,
            )
            reverse_state = {**state, "rows": list(reversed(state["rows"])),
                             "appearances": list(reversed(state["appearances"]))}
            reverse = entrance_trial.run_sweep(
                reverse_state, run, dict(reversed(list(vectors.items()))),
                {**ledger, "pairs": list(reversed(ledger["pairs"]))},
                coalesce=args.coalesce,
            )
            if semantic(result) != semantic(reverse):
                raise ValueError("entrance sweep differs under reversed inputs")
        staging = out.with_name(out.name + ".partial")
        staging.mkdir(parents=True, exist_ok=False)
        if args.reuse_result:
            shutil.copyfile(args.reuse_result / "trial.json", staging / "trial.json")
        else:
            (staging / "trial.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        (staging / "index.html").write_text(render(result, state, run), encoding="utf-8")
        outputs = {p.name: shadow.digest(p) for p in staging.iterdir()}
        diagnostics.verify({**bindings, **code})
        receipt = {
            "kind": "entrance-range-trial-receipt", "source": str(args.source),
            "inputs": bindings, "code": code, "outputs": outputs, "recipes": entrance_trial.recipes(),
            "coalesce": args.coalesce,
            "reuseResult": str(args.reuse_result) if args.reuse_result else None,
            "reverseVerified": True, "installedMoves": 0, "elapsedSeconds": time.perf_counter() - start,
        }
        (staging / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        staging.rename(out)
        print(f"Published {out / 'index.html'} ({receipt['elapsedSeconds']:.3f}s).")
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(f"Entrance trial failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
