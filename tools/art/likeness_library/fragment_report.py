"""Guided fragment comparisons with separate identity, pair and context judgments."""
import json


def render(packet, images, context):
    payload = json.dumps({"packet": packet, "images": images, "context": context}, allow_nan=False).replace("<", "\\u003c")
    return TEMPLATE.replace("{{DATA}}", payload)


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Split identities and mixed references</title>
<style>
body{background:#151b23;color:#e5edf6;font:16px system-ui;line-height:1.5;margin:20px}
main{max-width:1450px;margin:auto}button,select,textarea{font:inherit;padding:9px;max-width:100%}
button{cursor:pointer}button:disabled{opacity:.5;cursor:default}a{color:#a6d9ff}
.notice{background:#283445;padding:12px;border-left:4px solid #e0b15a}
.toolbar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:14px 0}
.toolbar>*{min-width:0;max-width:100%}
.columns{display:grid;grid-template-columns:1fr 1fr 1.5fr;gap:14px}.panel{background:#222e3c;padding:12px;min-width:0}
.refs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
figure{margin:0;overflow-wrap:anywhere}img{width:100%;height:330px;object-fit:contain}
#query img{height:440px}.pair img{height:280px}.crop img{height:220px}
figcaption{font-size:13px}small{display:block;color:#c1d0df}pre{white-space:pre-wrap;overflow-wrap:anywhere}
details{margin:18px 0}summary{cursor:pointer;font-weight:600}.primary{background:#b9ddff;color:#15202e}
textarea{display:block;width:95%}[hidden]{display:none!important}
@media(max-width:850px){.columns{grid-template-columns:1fr}.refs{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style></head><body><main>
<h1>Split identities or mixed references?</h1>
<p>Some folders may show the <strong>same person under different identities</strong>; some may contain <strong>different people mixed together</strong>.
This review separates those problems. A match does not mean the photo should move.</p>
<p class="notice"><strong>No group merges, photo moves or new locks.</strong>
Face evidence is the starting point. We also test an additional, separate below-face context check.
It can respond to clothing/background—not identity. It cannot overrule your answer.</p>
<p id="scope"></p>
<ol><li>Compare the query photo with the current and suggested identities. <strong>Both can be correct.</strong></li>
<li>Label <strong>each pictured reference</strong> Same person / Different person / Cannot tell relative to the query.
This identifies mixed references without condemning a whole folder.</li>
<li>Answer whether the query fits each intended identity. Use Both if split identities represent the same person,
or Cannot tell if the examples are insufficient. Answer the context question, then Record &amp; next.</li>
<li>Export whenever stopping, even partway. Keep/send the JSON. No new question is prefilled from an earlier group-level answer.</li></ol>
<div class="toolbar"><button id="back">Back</button><label>Case <select id="case"></select></label>
<button id="next">Next / skip</button><button id="unanswered">Next unanswered</button>
<label>Images <select id="mode"><option value="full">Full photos</option><option value="face">Face crops</option></select></label></div>
<p id="progress" role="status"></p><h2 id="question"></h2><p id="reason"></p>
<p id="prior" class="notice"></p>
<div class="columns">
<section class="panel"><h3>Photo being checked</h3><div id="query"></div></section>
<section class="panel"><h3>Current identity — not assumed right</h3><p id="current-name"></p><div id="current"></div></section>
<section class="panel"><h3>Suggested identity — may contain exceptions</h3><p id="target-name"></p><div id="target" class="refs"></div></section>
</div>
<section><h2>Which intended identities fit the query?</h2>
<p>These are not move/merge approvals. Judge the intended person even if you marked a reference exception above.</p>
<div class="toolbar">
<label>Current identity <select id="current-match"><option value="unreviewed">Choose…</option><option value="same">Same intended person</option>
<option value="different">Different intended person</option><option value="uncertain">Cannot tell</option></select></label>
<label>Suggested identity <select id="target-match"><option value="unreviewed">Choose…</option><option value="same">Same intended person</option>
<option value="different">Different intended person</option><option value="uncertain">Cannot tell</option></select></label></div>
<div class="toolbar"><button data-fit="current">Current only</button><button data-fit="target">Suggested only</button>
<button data-fit="both">Both — same person split across identities</button><button data-fit="neither">Neither</button>
<button data-fit="uncertain">Cannot tell for either</button></div>
<p>Quick buttons set only the two identity answers. They do not fill individual reference labels.</p></section>
<section><h2>Additional check: below-face appearance/context</h2>
<p>The crop excludes the saved face box. It may show clothing, pose and background; it does not measure body proportions
or establish identity. The same person can change outfits; different people can share outfits or a setting.</p>
<div id="context" class="refs"></div>
<label>Did this extra context help distinguish the examples? <select id="context-answer">
<option value="unreviewed">Choose…</option><option value="helpful">Helpful visual context</option>
<option value="misleading">Misleading resemblance / outfit or background dominates</option>
<option value="unavailable">Unavailable / not enough visible context</option><option value="uncertain">Cannot tell yet</option></select></label>
<details><summary>Machine evidence and experimental limits (optional)</summary>
<p>Face score and CLIP context score are not probabilities or directly comparable scales. No combined score or automatic identity decision is made.</p>
<pre id="evidence"></pre></details></section>
<div class="toolbar"><button id="save" class="primary">Record &amp; next</button>
<button id="export">Export answers / download JSON</button></div>
<p id="status" role="status"></p>
<details id="transfer"><summary>Copy / import answers to resume</summary>
<p>Export and retain the file or copy the text before closing. Import replaces in-page answers after validation.
Exports from the previous 24-case review use a different question schema; they remain preserved separately.</p>
<textarea id="json" rows="7"></textarea><button id="import">Import validated answers</button></details>
<details><summary>What this experiment changes</summary><pre id="limits"></pre></details>
</main><script id="data" type="application/json">{{DATA}}</script><script>
"use strict";
const data=JSON.parse(document.getElementById("data").textContent),p=data.packet,el=id=>document.getElementById(id);
let index=0,answers=[],dirty=false;
const labels=["same","different","uncertain"],contexts=["helpful","misleading","unavailable","uncertain"];
const cases=new Map(p.cases.map(c=>[c.id,c]));
const write=(id,t)=>{el(id).textContent=typeof t==="string"?t:JSON.stringify(t,null,2);};
for(const [i,c] of p.cases.entries()){const o=document.createElement("option");o.value=String(i);o.textContent=(i+1)+". "+c.currentFolder+" → "+c.targetFolder;el("case").append(o);}
write("scope",p.summary.caseCount+" comparisons / "+p.summary.distinctPhotoCount+" distinct full photos (reused across comparisons). "+
 p.summary.developmentCaseCount+" prior development queries; "+p.summary.unreviewedQueryCount+" additional queries. Selected coverage, not an accuracy estimate.");
write("limits",{packet:p.limits,context:data.context.limits,contextModel:data.context.model});
function refs(c){return [...new Set([c.currentReferenceId,...c.targetReferenceIds])];}
function photo(id,body,kind="full"){
 const record=data.images[id],fig=document.createElement("figure"),link=document.createElement("a"),img=document.createElement("img"),cap=document.createElement("figcaption");
 if(!record){fig.textContent="Missing image record: "+id;body.append(fig);return;}
 link.href=record.href;link.target="_blank";link.rel="noopener";
 img.src=record[kind]||record.full;img.alt=kind+" photo "+id;img.loading="lazy";
 cap.textContent=id;img.onerror=()=>{img.hidden=true;link.textContent="Open original source";cap.textContent="Image unavailable: "+id+". Do not infer identity from a missing image.";};
 link.append(img);fig.append(link,cap);body.append(fig);
}
function exactPair(id,body,saved){
 const box=document.createElement("div");box.className="pair";photo(id,box,el("mode").value);
 const label=document.createElement("label");label.textContent="Compared with query: ";
 const select=document.createElement("select");select.dataset.ref=id;
 for(const [value,title] of [["unreviewed","Choose…"],["same","Same person"],["different","Different person"],["uncertain","Cannot tell"]]){
  const o=document.createElement("option");o.value=value;o.textContent=title;select.append(o);
 }
 select.value=saved?.pairs.find(pair=>pair.referencePhotoId===id)?.label||"unreviewed";
 select.onchange=()=>{dirty=true;};label.append(select);box.append(label);body.append(box);
}
function progress(){
 write("progress","Case "+(index+1)+" of "+p.cases.length+" | "+answers.length+" recorded / "+p.cases.length+".");
 el("case").value=String(index);el("back").disabled=index===0;el("next").disabled=index===p.cases.length-1;
 el("unanswered").disabled=answers.length===p.cases.length;
}
function show(){
 const c=p.cases[index],saved=answers.find(a=>a.caseId===c.id);
 write("question","Does the query fit "+c.currentFolder+", "+c.targetFolder+", both, or neither?");
 write("reason",c.selectionReason);
 write("prior",c.priorJudgment?"Prior answer: "+c.priorJudgment.judgment+
  " toward "+c.priorJudgment.candidateFolder+". That was NOT a preferred folder or pair-level answer; these new questions start unanswered.":
  "Additional query: no prior answer is assumed. A named fragment association does not certify every member.");
 write("current-name",c.currentFolder);write("target-name",c.targetFolder);
 for(const id of ["query","current","target","context"])el(id).replaceChildren();
 photo(c.photoId,el("query"),el("mode").value);
 exactPair(c.currentReferenceId,el("current"),saved);
 for(const id of c.targetReferenceIds){
  if(id===c.currentReferenceId)photo(id,el("target"),el("mode").value);
  else exactPair(id,el("target"),saved);
 }
 for(const id of [c.photoId,...refs(c)]){
  const box=document.createElement("div");box.className="crop";
  const heading=document.createElement("small");heading.textContent=id===c.photoId?"Query context":id===c.currentReferenceId?"Current reference context":"Suggested reference context";box.append(heading);
  if(data.context.photos[id].status==="measured")photo(id,box,"context");
  else{const message=document.createElement("p");message.textContent="Context unavailable: "+data.context.photos[id].reason;box.append(message);}
  el("context").append(box);
 }
 for(const [id,key] of [["current-match","currentMatch"],["target-match","targetMatch"],["context-answer","context"]])el(id).value=saved?.[key]||"unreviewed";
 write("evidence",{faceEvidence:c.faceEvidence,baselineTarget:c.baselineTarget,
  contextPairs:data.context.pairs.filter(r=>r.caseId===c.id)});
 progress();write("status",saved?"Recorded answer restored; revise and Record to replace.":"Not recorded. Answer each reference, both identity questions and context question.");
}
function draft(){
 return {caseId:p.cases[index].id,currentMatch:el("current-match").value,targetMatch:el("target-match").value,
  pairs:[...document.querySelectorAll("select[data-ref]")].map(s=>({referencePhotoId:s.dataset.ref,label:s.value})),
  context:el("context-answer").value};
}
function valid(list){
 if(!Array.isArray(list))throw Error("Decisions must be a list");
 const seen=new Set();
 for(const a of list){
  const c=cases.get(a?.caseId);
  if(!c||Object.keys(a).sort().join(",")!=="caseId,context,currentMatch,pairs,targetMatch"||seen.has(a.caseId)||
   !labels.includes(a.currentMatch)||!labels.includes(a.targetMatch)||!contexts.includes(a.context)||!Array.isArray(a.pairs))throw Error("Missing/invalid identity or context answers");
  seen.add(a.caseId);const expected=new Set(refs(c)),got=new Set();
  for(const pair of a.pairs){
   if(Object.keys(pair).sort().join(",")!=="label,referencePhotoId"||!expected.has(pair.referencePhotoId)||
    got.has(pair.referencePhotoId)||!labels.includes(pair.label))throw Error("Label every pictured reference independently");
   got.add(pair.referencePhotoId);
  }
  if(expected.size!==got.size)throw Error("Missing reference-pair answers");
 }
}
function record(advance){
 const a=draft();try{valid([a]);}catch(error){write("status","Not recorded: "+error.message+". Use Cannot tell where needed.");return false;}
 answers=answers.filter(x=>x.caseId!==a.caseId);answers.push(a);dirty=true;
 if(advance&&index<p.cases.length-1)index++;
 show();write("status",answers.length+" answers recorded in page. "+
  (answers.length===p.cases.length?"Review complete. ":"")+"Export before stopping.");
 return true;
}
el("save").onclick=()=>{if(record(true))el("progress").scrollIntoView();};
for(const b of document.querySelectorAll("[data-fit]"))b.onclick=()=>{
 const values={current:["same","different"],target:["different","same"],both:["same","same"],neither:["different","different"],uncertain:["uncertain","uncertain"]}[b.dataset.fit];
 el("current-match").value=values[0];el("target-match").value=values[1];dirty=true;
};
for(const id of ["current-match","target-match","context-answer"])el(id).onchange=()=>{dirty=true;};
function hasDraft(){return draft().pairs.some(x=>x.label!=="unreviewed")||
 [el("current-match").value,el("target-match").value,el("context-answer").value].some(x=>x!=="unreviewed");}
function navigate(next){
 const c=p.cases[index],saved=answers.find(a=>a.caseId===c.id);
 if(hasDraft()&&JSON.stringify(saved)!==JSON.stringify(draft())&&!record(false))return;
 index=next;show();
}
el("back").onclick=()=>navigate(index-1);el("next").onclick=()=>navigate(index+1);
el("case").onchange=()=>{const next=Number(el("case").value);el("case").value=String(index);navigate(next);};
el("unanswered").onclick=()=>{const next=p.cases.findIndex(c=>!answers.some(a=>a.caseId===c.id));if(next>=0)navigate(next);};
el("mode").onchange=()=>{
 // Preserve unsaved answers while switching image framing.
 const d=draft(),saved=answers.find(a=>a.caseId===d.caseId);
 answers=answers.filter(a=>a.caseId!==d.caseId);answers.push(d);show();
 answers=answers.filter(a=>a.caseId!==d.caseId);if(saved)answers.push(saved);progress();
 write("status",saved?"Recorded answer restored; any revisions still need Record.":"Image framing changed; draft answers preserved but not recorded.");
};
el("export").onclick=()=>{
 if(hasDraft()&&!record(false))return;
 const value={schemaVersion:1,kind:"identity-fragment-answers",packetSHA256:p.packetSHA256,
  decisions:[...answers].sort((a,b)=>a.caseId.localeCompare(b.caseId))};
 const text=JSON.stringify(value,null,2);el("json").value=text;el("transfer").open=true;
 let url;
 try{
  url=URL.createObjectURL(new Blob([text],{type:"application/json"}));
  const a=document.createElement("a");a.href=url;a.download="fragment_answers_"+p.packetSHA256.slice(0,12)+".json";
  document.body.append(a);a.click();a.remove();
  write("status","Export contains "+answers.length+" recorded cases. Verify your download, or copy the JSON below if this browser blocks downloads.");
 }catch(error){write("status","Download failed: "+error.message+". Copy the export below; answers remain in page.");}
 finally{if(url)setTimeout(()=>URL.revokeObjectURL(url),1000);}
};
el("import").onclick=()=>{
 try{
  const d=JSON.parse(el("json").value);
  if(Object.keys(d).sort().join(",")!=="decisions,kind,packetSHA256,schemaVersion"||
   d.schemaVersion!==1||d.kind!=="identity-fragment-answers"||d.packetSHA256!==p.packetSHA256)throw Error("Packet/schema mismatch");
  valid(d.decisions);answers=d.decisions;dirty=false;
  const next=p.cases.findIndex(c=>!answers.some(a=>a.caseId===c.id));index=next<0?0:next;show();
  write("status",answers.length+" validated answers imported. No library changes.");
 }catch(error){write("status","Import refused: "+error.message+". Existing answers unchanged.");}
};
addEventListener("beforeunload",event=>{if(dirty){event.preventDefault();event.returnValue="";}});
show();
</script></body></html>
"""
