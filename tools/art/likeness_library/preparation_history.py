"""Static, read-only navigation over a gallery's checked intake history."""
import html
import json
import pathlib

from likeness_library import gallery_chrome


CSS = """
.history-controls{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}
.history-controls label,.history-controls input,.history-controls select{max-width:100%}
#source-context{overflow-wrap:anywhere}
.history-layout{display:grid;grid-template-columns:minmax(220px,320px) minmax(0,1fr);gap:18px}
.run-list{max-height:70vh;overflow:auto;display:flex;flex-direction:column;gap:6px}
.run-list a{display:block;padding:10px;background:white;border:1px solid var(--st-line);border-radius:6px;overflow-wrap:anywhere}
.run-list a[aria-current]{background:var(--st-accent-soft);border-color:var(--st-accent)}
.history-photos{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,240px),1fr));gap:12px}
.history-photo,.run-summary{background:white;border:1px solid var(--st-line);padding:12px;border-radius:8px;overflow-wrap:anywhere}
.history-photo img{width:100%;height:240px;object-fit:contain;background:var(--st-paper)}
.history-current{border:2px solid var(--st-accent)}
.history-photo h3{font-size:1rem}.run-summary{margin-bottom:12px}
.history-warning{border-left:4px solid #b87522;padding:10px;background:#fff0d9}
@media(max-width:700px){.history-layout{grid-template-columns:1fr}.run-list{max-height:240px}}
"""

SCRIPT = """
const runs=JSON.parse(document.getElementById("history-data").textContent)
  .sort((a,b)=>a.name.localeCompare(b.name,undefined,{numeric:true}));
for(const run of runs)run.searchText=[run.name,run.recipe,run.status,...run.photos.map(p=>p.source)].join(" ").toLowerCase();
const params=new URLSearchParams(location.search);
const source=params.get("source")||"", digest=params.get("sha256")||"";
let selected=params.get("run")||"", limit=60;
const query=document.getElementById("run-query"), recipe=document.getElementById("run-recipe");
const photoQuery=document.getElementById("photo-query"), list=document.getElementById("run-list");
const status=document.getElementById("run-status");
const linkedOnly=document.getElementById("linked-only");
const summary=document.getElementById("run-summary"), photos=document.getElementById("history-photos");
function node(tag,text,parent){const e=document.createElement(tag);if(text!==null)e.textContent=text;if(parent)parent.append(e);return e;}
for(const name of [...new Set(runs.map(r=>r.recipe).filter(Boolean))].sort()){
  const option=node("option",name,recipe);option.value=name;
}
function scopedRows(run){return run.photos.filter(p=>(!source||p.source===source)&&(!digest||p.sha256===digest));}
function matchingRuns(){
  const q=query.value.trim().toLowerCase();
  return runs.filter(r=>(!source||scopedRows(r).length)&&(!recipe.value||r.recipe===recipe.value)&&
    (!status.value||(status.value==="verified"?!r.status.startsWith("unverified"):r.status.startsWith("unverified")))&&
    (!q||r.searchText.includes(q)));
}
function renderPhotos(run){
  photos.replaceChildren();
  const q=photoQuery.value.trim().toLowerCase();
  const rows=(linkedOnly.checked?scopedRows(run):run.photos).filter(p=>!q||[p.source,p.outcome,p.reason].join(" ").toLowerCase().includes(q));
  for(const p of rows.slice(0,limit)){
    const card=node("article",null,photos);card.className="history-photo";
    if(!p.staged&&source&&p.source===source&&(!digest||p.sha256===digest)){card.classList.add("history-current");node("strong","Linked photo",card);}
    if(p.staged)node("strong","Staged/intake-only — not accepted publication",card);
    if(p.thumbnail){const image=node("img",null,card);image.src=p.thumbnail;image.alt=p.source;image.loading="lazy";
      node("p","Stored preview: "+p.preview,card);}
    else node("p","No stored preview available.",card);
    node("h3",p.source,card);node("p",p.outcome+" · "+p.decision,card);node("p",p.reason,card);
    const link=node("a","Open photo intake detail",card);link.href=p.href;
  }
  document.getElementById("photo-count").textContent=Math.min(limit,rows.length)+" of "+rows.length+" photos";
  document.getElementById("more-photos").hidden=limit>=rows.length;
  if(!rows.length)node("p","No photos match this filter.",photos);
}
function selectRun(run){
  selected=run.name;limit=60;summary.replaceChildren();
  node("h2",run.name,summary);node("p",run.recipe+" · "+run.status+" · "+scopedRows(run).length+" matching / "+run.photos.length+" domain photos",summary);
  if(run.href){const link=node("a","Open original run overview",summary);link.href=run.href;}
  node("p","Historical comparison evidence, not an accepted retained-version set or proof of publication.",summary);
  const url=new URL(location.href);url.searchParams.set("run",selected);history.replaceState(null,"",url);
  for(const a of list.querySelectorAll("a")){if(a.dataset.run===selected)a.setAttribute("aria-current","true");else a.removeAttribute("aria-current");}
  renderPhotos(run);
}
function render(){
  const visible=matchingRuns();list.replaceChildren();
  document.getElementById("run-count").textContent=visible.length+" of "+runs.length+" runs";
  for(const run of visible){
    const url=new URL(location.href);url.searchParams.set("run",run.name);
    const a=node("a",run.name+" · "+run.photos.length+" photos · "+run.status,list);
    a.href=url.href;a.dataset.run=run.name;
    a.addEventListener("click",event=>{if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;event.preventDefault();selectRun(run);});
  }
  const run=visible.find(r=>r.name===selected)||visible[0];
  if(run)selectRun(run);
  else{summary.replaceChildren();photos.replaceChildren();node("p","No runs match these filters.",summary);
    document.getElementById("photo-count").textContent="0 photos";document.getElementById("more-photos").hidden=true;}
}
query.addEventListener("input",render);recipe.addEventListener("change",render);status.addEventListener("change",render);
photoQuery.addEventListener("input",()=>{limit=60;const run=matchingRuns().find(r=>r.name===selected);if(run)renderPhotos(run);});
linkedOnly.addEventListener("change",()=>{limit=60;const run=matchingRuns().find(r=>r.name===selected);if(run)renderPhotos(run);});
document.getElementById("more-photos").addEventListener("click",()=>{limit+=60;const run=matchingRuns().find(r=>r.name===selected);if(run)renderPhotos(run);});
document.getElementById("clear-source").hidden=!source;
document.getElementById("linked-only-label").hidden=!source;
if(source)document.getElementById("source-context").textContent="Runs containing the linked photo: "+source+". All run photos are shown; the linked photo is marked.";
if(selected&&!runs.some(r=>r.name===selected&&(!source||scopedRows(r).length))){
  const warning=document.getElementById("run-link-warning");warning.hidden=false;
  warning.textContent="Requested run is unavailable in this view: "+selected+". Showing available history instead.";
}
render();
"""


def publish_staged(root, output_dir, *, domain="general"):
    """Refresh intake navigation only; no matching, preparation or photo writes."""
    from .preparation_provenance import build_index
    from .retained_preparation import _safe

    root = pathlib.Path(root).absolute()
    output_dir = pathlib.Path(output_dir).absolute()
    relative = output_dir.relative_to(root).as_posix()
    output = _safe(root, relative + "/intake_runs.html")
    payload = build_index(root, output_dir, [], domain).history_html()
    output.parent.mkdir(parents=True, exist_ok=True)
    pending = _safe(root, relative + "/intake_runs.pending.html")
    if pending.exists():
        raise ValueError("unfinished intake history publication exists")
    try:
        with pending.open("x", encoding="utf-8") as stream:
            stream.write(payload)
        pending.replace(output)
    finally:
        if pending.exists():
            pending.unlink()
    return output


def render(index, *, standalone=False):
    """Use already verified records; never run preparation, infer identity or prune."""
    runs = [run for run in index.history_runs if run["photos"] or run["status"].startswith("unverified")]
    payload = json.dumps(runs, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    prefix = gallery_chrome.reports_prefix(index.page_dir, index.root / "_reports")
    masthead_prefix = None if standalone else prefix
    overview = "artists_gallery.html" if index.domain == "artists" else "people_gallery.html"
    back_label = "Overview"
    if standalone:
        overview = "artists_gallery_review.html" if index.domain == "artists" else "people_gallery_review.html"
        back_label = "Photo review"
    warning = ""
    if index.incomplete or index._errors:
        warning = '<p class="history-warning">Gallery source-continuity index diagnostics: ' + html.escape(
            " · ".join(index._errors)
        ) + ". History checks each discovered run separately; this does not extend source-continuity claims.</p>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Intake runs</title><style>{gallery_chrome.CSS}{CSS}</style></head><body id="top">
{gallery_chrome.masthead("Artists" if index.domain == "artists" else "People", masthead_prefix)}
<div class="site-page"><header class="page-header"><div><h1>Intake runs</h1>
<p>Search run names, recipes and source filenames. Select a run to browse its photos.</p>
<p>Read-only history. No processing, assignment or pruning is performed.</p></div></header>
{gallery_chrome.navigation([(back_label, overview), ("Intake runs", "intake_runs.html")], "Intake runs")}
{warning}<p id="run-link-warning" class="history-warning" role="status" hidden></p>
<a id="clear-source" href="intake_runs.html">Show history for all photos</a>
<p id="source-context"></p>
<div class="history-controls"><label>Find runs <input id="run-query" type="search"></label>
<label>Recipe <select id="run-recipe"><option value="">All recipes</option></select></label>
<label>Verification <select id="run-status"><option value="">All states</option>
<option value="verified">Verified artifacts</option><option value="unverified">Unverified / unavailable</option></select></label>
<span id="run-count" role="status"></span></div>
<noscript>Enable JavaScript to select and filter local intake runs.</noscript>
<main class="history-layout"><nav id="run-list" class="run-list" aria-label="Intake runs"></nav>
<section aria-label="Selected intake run"><div id="run-summary" class="run-summary"></div>
<div class="history-controls"><label>Find photos <input id="photo-query" type="search"></label>
<label id="linked-only-label" hidden><input id="linked-only" type="checkbox"> Linked photo only</label>
<span id="photo-count" role="status"></span></div><div id="history-photos" class="history-photos"></div>
<button id="more-photos" type="button" hidden>Show next 60 photos</button></section></main>
{gallery_chrome.footer("History only · Keep/prune policy requires a separate decision")}
<script id="history-data" type="application/json">{payload}</script><script>{SCRIPT}</script></div></body></html>"""
