#!/usr/bin/env python3
"""Build a local, read-only photo review page for person galleries and Review folders."""
import argparse
import collections
import datetime
import hashlib
import html
import json
import os
import pathlib
import re
import sys
import tempfile
import types

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/art"))
import likeness  # noqa: E402
import originals  # noqa: E402
from likeness_library import domains, gallery_chrome, identity_names, metadata, person_rename, preparation_history, preparation_provenance, protection, rejections, report_assets  # noqa: E402
from likeness_library.audit import audit_person, catalog_photo_flags, core_excluded_protection, identity_order_key  # noqa: E402
from likeness_library.cross_reference import CATEGORY_ORDER, rank_identity_centroids, score_band  # noqa: E402
from likeness_library.policy import (
    default_policy,
    evaluate_photo_consistency,
    load_policy,
    render_policy_panel,
    render_score_legend,
)  # noqa: E402
from likeness_library import verification_reads  # noqa: E402

PAGE_SIZE = 100
SECTIONS = CATEGORY_ORDER
GROUP_ORDER = CATEGORY_ORDER
ACTION_ROOTS = {"Angels", "Sisters", "Models", "Prospects", "Potentials"}

CSS = """
.note{color:var(--st-muted);max-width:1100px}.warnings{color:#8a3b16}
.controls{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px 20px;align-items:end;margin:16px 0;padding:14px 16px;background:var(--st-card);border:1px solid var(--st-line);border-radius:var(--st-radius);box-shadow:var(--st-shadow)}
.filter-controls{display:grid;gap:8px;min-width:0}.search-control{display:flex;flex-direction:column;align-items:flex-start;gap:4px;width:min(100%,520px)}
.search-control input{width:100%;box-sizing:border-box}.filter-options{display:flex;justify-content:flex-start;gap:10px;flex-wrap:wrap}
.sort-controls{display:flex;justify-content:flex-end;gap:10px;flex-wrap:wrap;align-items:flex-end}
.controls input,.controls select,.controls button{font:inherit;padding:7px}
.count{color:var(--st-muted);overflow-wrap:anywhere}#grid{display:block;--card-min:260px}
.photo-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,var(--card-min)),1fr));gap:12px}
.preparation-evidence{font-size:.8em;margin-top:6px;overflow-wrap:anywhere}.preparation-evidence summary{cursor:pointer;color:#34495e}.preparation-evidence code{overflow-wrap:anywhere}
article{background:var(--st-card);border:1px solid var(--st-line);border-radius:8px;padding:8px;min-width:0;box-shadow:var(--st-shadow)}
article.primary{border:3px solid #8b6d32}
article.review-photo{border-left:5px solid #b47d25}
.photo-location-group{margin:12px 0 20px}.photo-location-group h3{font-size:1rem;margin:0 0 10px}
.destination-controls{display:grid;gap:6px;margin-top:6px}.destination-controls[hidden]{display:none}
.destination-controls label{display:block}.destination-controls select{max-width:100%}
article img{display:block;width:100%;aspect-ratio:4/5;object-fit:cover;background:#eee}
article a{color:#28527a}.name{font-weight:600;overflow-wrap:anywhere;margin:7px 0}
.relationship-list{margin:4px 0 12px;padding-left:24px}.relationship-list li{margin:4px 0}
.badge-gallery{background:#e4efff;color:#244f85}.badge-review,.badge-possible-outlier,.badge-borderline{background:#fff0d9;color:#704a12}
.badge-core-member,.badge-identity-anchor,.badge-consistent,.badge-gallery-photo{background:#d9efdc;color:#205b2a}
.badge-low-similarity,.badge-unscored{background:#f5d6d6;color:#7b2222}.badge-protected-only,.badge-protected-identity{background:#eee;color:#555}
.detail{color:#555;font-size:.88em;margin:4px 0;overflow-wrap:anywhere}
.detail-list{margin:4px 0;padding-left:22px}.detail-list li{margin:5px 0}
.detail-list .score-badge{margin-left:4px}.face-link{display:inline-block;text-decoration:none}.face-link:hover{text-decoration:underline}
.badge-review-photo{background:#fff0d9;color:#704a12}
#more{display:block;margin:18px auto;padding:8px 18px;font:inherit}
.stage{display:block;margin-top:8px;font-size:.9em}.stage select{display:block;width:100%;font:inherit;padding:5px}
.actions{display:flex;gap:10px;align-items:center;margin:14px 0}.actions button{font:inherit;padding:8px}
.person-group{margin:20px 0;padding:14px;background:#efebe3;border:1px solid var(--st-line);border-radius:var(--st-radius);width:100%;box-sizing:border-box}
.person-head{display:grid;grid-template-columns:minmax(180px,.7fr) minmax(0,1.3fr) minmax(0,1fr);gap:14px;align-items:start;margin-bottom:12px}
.identity-panel{background:var(--st-card);border:1px solid var(--st-line);border-radius:8px;padding:12px;min-width:0;overflow-wrap:anywhere}
.identity-panel h2{font-size:1.15em;margin:4px 0}
.identity-panel h3{font-size:1rem;margin:0 0 10px}
.identity-panel dl{margin:10px 0}.identity-panel dt{font-size:.8em;color:var(--st-muted);margin-top:8px}
.identity-panel dd{margin:0}.identity-panel input{width:100%;min-width:0}
.identity-panel button{margin:5px 5px 0 0;white-space:normal}
.reference{max-width:260px}.reference img{aspect-ratio:4/5;object-fit:cover}
.reference .detail{font-size:.82em}
.identity-rankings{font-size:.88em;margin:0 0 12px;overflow-wrap:anywhere}
.identity-rankings summary{cursor:pointer;color:#28527a}
.policy-panel{margin:10px 0;padding:8px 10px;background:#fff;border:1px solid #ded8ce;border-radius:6px;font-size:.84em}
.policy-panel summary{cursor:pointer;font-weight:600;color:#34495e}
.policy-panel pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:520px;overflow:auto;background:#f5f3ee;padding:10px;border-radius:4px;font-size:.9em}
@media(max-width:1050px){.controls{grid-template-columns:minmax(0,1fr)}.sort-controls{justify-content:flex-start}}
@media(max-width:1050px){.person-head{grid-template-columns:minmax(160px,.7fr) minmax(0,1.3fr)}.identity-actions{grid-column:1/-1}}
@media(max-width:600px){.person-head{grid-template-columns:minmax(0,1fr)}.identity-actions{grid-column:auto}}
"""

SCRIPT = preparation_provenance.EVIDENCE_SCRIPT + """
const records=JSON.parse(document.getElementById("review-data").textContent);
const peopleData=JSON.parse(document.getElementById("people-data").textContent);
const cardUseGuidance=JSON.parse(document.getElementById("card-use-guidance").textContent);
const generationIndex=JSON.parse(document.getElementById("generation-index").textContent);
const group=document.getElementById("group"), bucket=document.getElementById("bucket");
const state=document.getElementById("state"), sort=document.getElementById("sort");
const mode=document.getElementById("mode"), person=document.getElementById("person");
const grouping=document.getElementById("grouping");
const scoreCeiling=document.getElementById("score-ceiling");
const cardSize=document.getElementById("card-size");
const framing=document.getElementById("framing");
const query=document.getElementById("query"), grid=document.getElementById("grid");
const count=document.getElementById("count"), more=document.getElementById("more");
const stagedCount=document.getElementById("staged-count"), download=document.getElementById("download");
const pageSize=100; let visible=[], shown=pageSize;
const staged=new Map();
const stagedPeople=new Map();
function appendAlignmentEvidence(article,evidence) {
  const details=document.createElement("details");details.className="preparation-evidence alignment-evidence";
  const summary=document.createElement("summary");
  summary.textContent="Exact SFace aligned input";
  details.append(summary);
  const state=document.createElement("p");state.className="detail";
  const states={
    missing:"No persisted aligned crop is available. Run likeness scan outside --check to refresh this cache entry.",
    "read-only-not-persisted":"The crop was computed for this read-only review but was not persisted. Run likeness scan outside --check to save it.",
    invalid:"Aligned-face evidence failed source or artifact verification; no crop link is shown.",
    "no-face":"No human face was selected, so SFace received no aligned crop.",
    unreadable:"No SFace crop was produced for this unreadable or unusable source."
  };
  state.textContent=states[evidence?.state]||"Exact aligned-crop evidence is unavailable.";
  details.append(state);
  if(evidence?.sourcePath) {
    const source=document.createElement("p");source.className="detail";
    source.textContent="Scored source: "+evidence.sourcePath+" · SHA-256 "+(evidence.sourceSha256||"unavailable");
    details.append(source);
  }
  if(evidence?.model) {
    const model=document.createElement("p");model.className="detail";
    model.textContent="Model identity: "+(evidence.modelId||"unavailable")+
      " · YuNet SHA-256 "+(evidence.model.detector?.sha256||"unavailable")+
      " · SFace SHA-256 "+(evidence.model.recognizer?.sha256||"unavailable")+
      " · OpenCV "+(evidence.model.opencv||"unavailable");
    details.append(model);
  }
  if(evidence?.state==="verified"&&evidence.href) {
    const crop=document.createElement("a");crop.href=evidence.href;crop.target="_blank";
    crop.rel="noopener noreferrer";crop.textContent="Open exact alignCrop PNG sent to SFace";
    details.append(crop);
    const digest=document.createElement("p");digest.className="detail";
    digest.textContent="Crop SHA-256 "+evidence.alignmentSha256+
      " · "+evidence.width+" × "+evidence.height+" · score uses this source's cached SFace vector";
    details.append(digest);
  }
  article.append(details);
}
function fill(select, values, label, sortValues=true) {
  select.replaceChildren(new Option("All "+label,""));
  const unique=[...new Set(values)];
  if(sortValues)unique.sort((a,b)=>a.localeCompare(b));
  unique.forEach(v=>select.add(new Option(v,v)));
}
const categoryOrder=JSON.parse(document.getElementById("category-order").textContent);
fill(group,categoryOrder.filter(value=>records.some(r=>r.group===value)),"groups",false);
fill(bucket,records.map(r=>r.bucket),"locations");
fill(state,records.map(r=>r.state),"states");
function fillPeople() {
  const previous=person.value;
  const folders=records.filter(r=>!group.value||r.group===group.value).map(r=>r.folder);
  fill(person,folders,"people",false);
  if(folders.includes(previous))person.value=previous;
}
fillPeople();
const folderOrder=new Map();
for(const record of records)if(!folderOrder.has(record.folder))folderOrder.set(record.folder,folderOrder.size);
const groupOrder=new Map(categoryOrder.map((value,index)=>[value,index]));
const requestedPerson=new URLSearchParams(location.search).get("person");
const requestedSort=new URLSearchParams(location.search).get("sort");
const requestedBucket=new URLSearchParams(location.search).get("bucket");
if(["identity","high","low","name"].includes(requestedSort))sort.value=requestedSort;
if(["Gallery","Review"].includes(requestedBucket))bucket.value=requestedBucket;
if(requestedPerson) {
  const target=records.find(r=>r.folder===requestedPerson);
  if(target) {
    group.value=target.group;
    fillPeople();
    person.value=target.folder;
  }
}
function compare(a,b) {
  if(sort.value==="identity") {
    return a.identityOrder-b.identityOrder ||
      (b.score??-Infinity)-(a.score??-Infinity) ||
      a.name.localeCompare(b.name);
  }
  if(a.score===null&&b.score!==null)return 1;
  if(b.score===null&&a.score!==null)return -1;
  if(sort.value==="name")return a.name.localeCompare(b.name);
  if(a.score===null)return 0;
  return sort.value==="high" ? b.score-a.score : a.score-b.score;
}
const likenessPolicy=JSON.parse(document.getElementById("likeness-policy-data").textContent);
function scoreBand(score) {
  const bands=likenessPolicy.scoreBands;
  if(score>=bands.green.minimum)return "green";
  if(score>=bands.yellow.minimum)return "yellow";
  if(score>=bands.orange.minimum)return "orange";
  return "red";
}
function scoreBadge(score, label="Likeness score") {
  if(score===null||score===undefined)return null;
  const band=scoreBand(score);
  const badge=document.createElement("span"); badge.className="score-badge score-"+band;
  badge.textContent=score.toFixed(2); badge.title=label; return badge;
}
function categoryBadge(text) {
  const badge=document.createElement("span");
  badge.className="badge category-"+String(text||"").toLowerCase();
  badge.textContent=text; return badge;
}
function personReviewLink(key, label) {
  const link=document.createElement("a");
  const query=new URLSearchParams({person:key,bucket:"Gallery",sort:"identity"});
  link.href="people_gallery_review.html?"+query.toString();
  link.target="_blank"; link.rel="noopener noreferrer"; link.textContent=label;
  return link;
}
function card(r, readOnly=false) {
  const article=document.createElement("article");
  if(readOnly)article.className="reference";
  else if(r.primaryReference)article.className="primary";
  if(!readOnly&&r.bucket==="Review")article.classList.add("review-photo");
  const link=document.createElement("a"); link.href=r.href; link.target="_blank"; link.rel="noopener noreferrer";
  const image=document.createElement("img");
  image.src=framing.value==="head"?r.thumbnailHead:r.thumbnail;
  image.dataset.chest=r.thumbnail; image.dataset.head=r.thumbnailHead; image.alt=r.name;
  image.title=r.name; image.loading="lazy"; image.decoding="async";
  link.append(image); article.append(link);
  if(r.thumbnailProvenance) {
    const sources=document.createElement("div"); sources.className="detail";
    sources.append(document.createTextNode("Standard sources: "));
    for(const mode of ["padded","chest","head"]) {
      const provenance=r.thumbnailProvenance[mode];
      if(!provenance)continue;
      const source=document.createElement("a");
      source.href=provenance.href; source.target="_blank"; source.rel="noopener noreferrer";
      source.textContent=mode+" "; source.title=provenance.recipe+" · SHA-256 "+provenance.sha256;
      sources.append(source);
    }
    article.append(sources);
  }
  appendPreparationEvidence(article,r.preparationEvidence);
  appendAlignmentEvidence(article,r.alignmentEvidence);
  if(r.generationSource) {
    const generate=document.createElement("a");
    generate.href=generationIndex+"?source="+encodeURIComponent(r.generationSource);
    generate.className="intake-detail-link";generate.textContent="Generate / Test";
    article.append(generate);
  }
  if(r.photoProtectionInfo){
    const note=document.createElement("p");note.className="detail protection-info";
    note.textContent=r.photoProtectionInfo;article.append(note);
  }
  const name=document.createElement("div"); name.className="name";
  name.textContent=readOnly?r.name:r.folder.split("/").slice(1).join("/");
  article.append(name);
  if(!readOnly) {
    const id=document.createElement("div"); id.className="detail photo-id";
    const photoId=r.photoId?r.photoId.replace(/^photo:/,"").replace(/^image_/,""):"unavailable";
    id.textContent="Photo ID: "+photoId;
    id.title="Photo ID comes from the filename; Identity ID is assigned when the folder has a likeness-catalogue record";
    article.append(id);
    const identityId=document.createElement("div"); identityId.className="detail identity-id";
    identityId.textContent="Identity ID: "+(r.personId||(r.folder==="Various"?"unassigned (Various hold)":"not catalogued"));
    identityId.title=r.personId?"Stable identity key from the likeness catalogue":
      r.folder==="Various"?"Various is an unassigned holding area, not a person identity":
      "This folder has no registered catalogue identity";
    article.append(identityId);
    if(r.identityNames){
      const names=document.createElement("div");names.className="detail identity-names";
      names.textContent="Person: "+(r.identityNames.currentPersonName||"not recorded")+
        " · Original: "+(r.identityNames.originalPersonName||"not recorded");
      article.append(names);
    }
  }
  const badges=readOnly?[r.referenceLabel]:[
    r.bucket==="Gallery"?"Gallery photo":"Review photo",
    r.workflowSelected?"Workflow-selected · protected":"",
    r.state,
    r.primaryReference?r.referenceLabel:""
  ];
  if(!readOnly)article.append(categoryBadge(r.group));
  for(const text of badges.filter(Boolean)) {
    const badge=document.createElement("span");
    badge.className="badge badge-"+String(text).toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
    badge.textContent=text; article.append(badge);
  }
  if(readOnly) {
    const detail=document.createElement("div"); detail.className="detail";
    detail.textContent="Identity anchor: "+(r.identityAnchor?"yes":"no")+
      " · workflow-selected: "+(r.workflowSelected?"yes":"no");
    article.append(detail);
    return article;
  }
  const score=document.createElement("div"); score.className="detail";
  score.append(document.createTextNode("Core similarity: "));
  const scoreMark=scoreBadge(r.score,"Similarity to this person's core");
  if(scoreMark)score.append(scoreMark); else score.append(document.createTextNode("not scored"));
  article.append(score);
  if(r.scoreContext) {
    const context=document.createElement("div"); context.className="detail score-context";
    const coreType=r.scoreContext.coreMode==="trusted"?"trusted anchors":
      r.scoreContext.coreMode==="provisional"?"provisional · no trusted anchors":"no usable core";
    context.append(document.createTextNode("Core size: "+r.scoreContext.coreSize+" photos "));
    const coreBadge=document.createElement("span");
    coreBadge.className="score-badge score-"+
      (r.scoreContext.coreMode==="trusted"?"green":
        r.scoreContext.coreMode==="provisional"?"yellow":"red");
    coreBadge.textContent=coreType;
    context.append(coreBadge);
    article.append(context);
    const face=document.createElement("div"); face.className="detail";
    face.append(document.createTextNode("Face: "));
    const facePixels=r.scoreContext.facePixels||0;
    const gate=r.scoreContext.minFace||0;
    const faceCount=Number.isFinite(r.scoreContext.faceCount)?r.scoreContext.faceCount:-1;
    const faceLabel=(facePixels>=gate?"score-green":"score-red")+" score-badge";
    const faceCountClass=faceCount===1?"score-green":faceCount>1?"score-yellow":"score-red";
    const faceValue=document.createElement("span"); faceValue.className=faceLabel;
    faceValue.textContent=facePixels+" px";
    faceValue.title="Face-size minimum: "+gate+" px";
    const countValue=document.createElement("span"); countValue.className=faceCountClass+" score-badge";
    countValue.textContent=faceCount<0?"unreadable":String(faceCount);
    countValue.title="Detected face count";
    if(r.thumbnailFace) {
      const faceLink=document.createElement("a"); faceLink.className="face-link";
      faceLink.href=r.thumbnailFace; faceLink.target="_blank";
      faceLink.rel="noopener noreferrer"; faceLink.title="Open face crop";
      faceLink.append(faceValue,document.createTextNode(" / "),countValue);
      face.append(faceLink);
    } else {
      face.append(faceValue,document.createTextNode(" / "),countValue);
    }
    article.append(face);
  }
  if(r.closestMatches?.length) {
    const closest=document.createElement("div"); closest.className="detail closest-matches";
    closest.append(document.createTextNode("Closest other identities (similarity evidence, not routing decisions):"));
    const list=document.createElement("ol");
    for(const match of r.closestMatches) {
      const line=document.createElement("li");
      line.append(personReviewLink(match.folder,match.category+": "+match.name));
      const mark=scoreBadge(match.score); if(mark)line.append(document.createTextNode(" "),mark);
      list.append(line);
    }
    closest.append(list); article.append(closest);
  } else if(r.best_other) {
    const closest=document.createElement("div"); closest.className="detail";
    const parsed=r.best_other.match(/^(.*) \\((-?\\d+(?:\\.\\d+)?)\\)$/);
    if(parsed) {
      const key=parsed[1], category=key.split("/",1)[0], name=key.slice(category.length+1);
      closest.append(document.createTextNode("Closest other: "));
      closest.append(personReviewLink(key,category+": "+name));
      const mark=scoreBadge(Number(parsed[2])); if(mark)closest.append(document.createTextNode(" "),mark);
    } else closest.textContent="Closest other: "+r.best_other;
    article.append(closest);
  }
  const rationale=document.createElement("details"); rationale.className="detail";
  const summary=document.createElement("summary"); summary.textContent="Scoring & action details"; rationale.append(summary);
  const detailTexts=[
    ...(r.scoreDetails||[]),
    r.rejectedIdentityIds?.length?"Recorded identity exclusions: "+r.rejectedIdentityIds.join(", "):"",
    r.rejectionMetadataStale?"Identity exclusions need review: photo bytes changed; automatic routing is held.":"",
    r.state==="Core member"?"":r.reason,
    r.stageReason
  ].filter(Boolean);
  if(detailTexts.length) {
    const list=document.createElement("ul"); list.className="detail-list";
    for(const text of detailTexts) {
      const line=document.createElement("li"); line.textContent=text;
      if(text.startsWith("Face gate:")) {
        line.className=(r.scoreContext?.usable?"score-green":"score-red");
      } else if(text.startsWith("Reference core:")) {
        line.className="score-"+(r.scoreContext?.coreMode==="trusted"?"green":
          r.scoreContext?.coreMode==="provisional"?"yellow":"red");
      }
      list.append(line);
    }
    rationale.append(list);
  }
  if(detailTexts.length)article.append(rationale);
  const stageLabel=document.createElement("label"); stageLabel.className="stage"; stageLabel.textContent="Stage action";
  const action=document.createElement("select"); action.setAttribute("aria-label","Stage action for "+r.name);
  action.add(new Option("No staged action",""));
  for(const [value,label] of r.stageOptions||[])action.add(new Option(label,value));
  action.disabled=!r.stageable;
  action.value=staged.get(r.photoId)?.type||"";
  const destination=document.createElement("select");
  destination.setAttribute("aria-label","Destination identity for "+r.name);
  const destinationCategory=document.createElement("select");
  destinationCategory.setAttribute("aria-label","Destination category for "+r.name);
  const destinationControls=document.createElement("div"); destinationControls.className="destination-controls";
  const categoryLabel=document.createElement("label"); categoryLabel.textContent="Destination category";
  const identityLabel=document.createElement("label"); identityLabel.textContent="Destination identity";
  categoryLabel.append(destinationCategory);identityLabel.append(destination);
  destinationControls.append(categoryLabel,identityLabel);
  const folders=[...new Set(records.filter(item=>
    /^(Sisters|Angels|Models|Prospects|Potentials)\\//.test(item.folder)&&item.folder!==r.folder&&item.personId
  ).map(item=>item.folder))].sort();
  for(const category of categoryOrder.filter(category=>folders.some(folder=>folder.startsWith(category+"/"))))
    destinationCategory.add(new Option(category,category));
  const fillDestinations=()=>{
    destination.replaceChildren();
    for(const folder of folders.filter(folder=>folder.startsWith(destinationCategory.value+"/")))
      destination.add(new Option(folder.slice(folder.indexOf("/")+1),folder));
  };
  const closest=r.best_other?.match(/^(.*) \\((-?\\d+(?:\\.\\d+)?)\\)$/)?.[1];
  const restoreDestination=()=>{
    const folder=staged.get(r.photoId)?.destinationFolder||
      (folders.includes(closest)?closest:folders[0])||"";
    destinationCategory.value=folder.split("/")[0];
    fillDestinations();destination.value=folder;
  };
  restoreDestination();
  if(!folders.length) {
    const option=[...action.options].find(item=>item.value==="match-accepted");
    if(option)option.remove();
  }
  destinationControls.hidden=action.value!=="match-accepted";
  const saveStage=()=>{
    if(action.value&&[...stagedPeople.values()].some(item=>item.type==="person-renamed")) {
      alert("Apply or cancel the standalone identity rename before staging photo actions.");
      action.value=staged.get(r.photoId)?.type||"";
      restoreDestination();destinationControls.hidden=action.value!=="match-accepted";
      return;
    }
    if(action.value&&(stagedPeople.has(r.personId)||stagedPeople.has(
      records.find(item=>item.folder===destination.value)?.personId
    )&&action.value==="match-accepted")) {
      alert("Stage identity protection separately from photo actions for that identity.");
      action.value=staged.get(r.photoId)?.type||"";
      restoreDestination();destinationControls.hidden=action.value!=="match-accepted";
      return;
    }
    if(action.value)staged.set(r.photoId,{
      type:action.value,
      ...(action.value==="match-accepted"?{
        destinationFolder:destination.value,
        destinationPersonId:records.find(item=>item.folder===destination.value)?.personId
      }:{})
    }); else staged.delete(r.photoId);
    updateStagedCount();
  };
  action.addEventListener("change",()=>{
    destinationControls.hidden=action.value!=="match-accepted";
    saveStage();
  });
  destinationCategory.addEventListener("change",()=>{fillDestinations();saveStage()});
  destination.addEventListener("change",saveStage);
  stageLabel.append(action);article.append(stageLabel,destinationControls);
  return article;
}
function updateStagedCount(){
  const total=staged.size+stagedPeople.size;
  stagedCount.textContent=total+" action(s) staged";
  download.disabled=total===0;
}
function matchesMode(r) {
  if(mode.value==="review")return r.bucket==="Review";
  if(mode.value==="low")return r.bucket==="Gallery"&&r.score!==null&&r.score<Number(scoreCeiling.value);
  return true;
}
function primaryFor(folder) {
  return records.find(r=>r.folder===folder&&r.primaryReference)||null;
}
function appendPhotoGroups(container,items) {
  const groups=grouping.value==="split"?
    ["Gallery","Review"].map(bucket=>[bucket,items.filter(item=>item.bucket===bucket)]):
    [["",items]];
  for(const [bucket,photos] of groups) {
    if(!photos.length)continue;
    const section=document.createElement("div");section.className="photo-location-group";
    if(bucket) {
      const heading=document.createElement("h3");heading.textContent=bucket+" · "+photos.length+" shown";
      section.append(heading);
    }
    const photoGrid=document.createElement("div");photoGrid.className="photo-grid";
    photoGrid.append(...photos.map(item=>card(item)));section.append(photoGrid);container.append(section);
  }
}
function groupCards(items) {
  const grouped=new Map();
  for(const item of items) {
    if(!grouped.has(item.folder))grouped.set(item.folder,[]);
    grouped.get(item.folder).push(item);
  }
  const nodes=[];
  for(const [folder,photos] of grouped) {
    const section=document.createElement("section"); section.className="person-group";
    const header=document.createElement("div"); header.className="person-head";
    const info=peopleData[folder]||{};
    function panel(label,kind) {
      const box=document.createElement("section"); box.className="identity-panel "+kind;
      box.setAttribute("aria-label",label+" for "+folder);
      const heading=document.createElement("h3");heading.textContent=label;box.append(heading);
      header.append(box);return box;
    }
    const referencePanel=panel("Reference photo","identity-reference");
    const detailsPanel=panel("Identity details","identity-details");
    const actionsPanel=panel("Manual actions","identity-actions");
    const title=document.createElement("h2"); title.textContent=folder.split("/").slice(1).join("/")||folder;
    detailsPanel.append(title,categoryBadge(info.group||folder.split("/")[0]));
    const allPhotos=records.filter(item=>item.folder===folder);
    const facts=document.createElement("dl");
    function fact(label,value) {
      const term=document.createElement("dt");term.textContent=label;
      const description=document.createElement("dd");description.textContent=value;facts.append(term,description);
    }
    const snapshot=info.personRenameAction;
    const names=info.identityNames||{};
    fact("Current person name",names.currentPersonName||snapshot?.expectedRecordedName||"Not available in this report");
    fact("Original person name",names.originalPersonName||"Not recorded");
    fact("Original-name source",names.originalNameSource||"unavailable");
    if(names.characterName)fact("Character name",names.characterName);
    if(names.familySurname)fact("Family surname",names.familySurname);
    if(names.familyReason)fact("Family evidence",names.familyReason);
    if(info.identityProtectionInfo)fact("Protection rule",info.identityProtectionInfo);
    if(/^(Angels|Sisters)\\//.test(folder))fact("Fixed cast slot",folder.split("/").slice(1).join("/"));
    fact("Identity ID",allPhotos.find(item=>item.personId)?.personId||
      (folder==="Various"?"unassigned (Various hold)":"not catalogued"));
    fact("Photos in this report",allPhotos.filter(item=>item.bucket==="Gallery").length+" Gallery · "+
      allPhotos.filter(item=>item.bucket==="Review").length+" Review");
    fact("Currently shown",photos.length+" of "+allPhotos.length+" (filters and page limit apply)");
    const core=allPhotos.find(item=>item.scoreContext)?.scoreContext;
    if(core)fact("Identity core",core.coreSize+" photos · "+
      (core.coreMode==="trusted"?"trusted anchors":core.coreMode==="provisional"?"provisional · no trusted anchors":"no usable core"));
    detailsPanel.append(facts);
    const guidance=cardUseGuidance[info.group||folder.split("/")[0]];
    if(guidance) {
      const note=document.createElement("p");note.className="detail card-use-guidance";
      note.textContent=guidance+" Not a rarity rule or automatic assignment.";detailsPanel.append(note);
    }
    const actionNote=document.createElement("p");actionNote.className="detail";
    actionNote.textContent="Stage and download only. Validate and preview with the CLI before applying. "+
      "Existing protection and standalone-batch safeguards still apply.";
    actionsPanel.append(actionNote);
    if(info.identityProtected) {
      const protectedBadge=document.createElement("span");
      protectedBadge.className="badge badge-protected-identity";
      protectedBadge.textContent="Protected identity";
      protectedBadge.title="Automatic Gallery membership and category changes are blocked; Review admission is separate";
      detailsPanel.append(protectedBadge);
    }
    if(info.personProtectionAction) {
      const decision=info.personProtectionAction;
      const label=document.createElement("label"); label.className="stage";
      label.append(document.createTextNode("Identity protection (not photo protection)"));
      const select=document.createElement("select");
      select.add(new Option("No identity change",""));
      select.add(new Option(
        decision.type==="person-protected"?"Protect identity / re-enable auto-protection":"Unprotect identity / disable auto-protection",
        decision.type
      ));
      select.value=stagedPeople.get(decision.personId)?.type===decision.type?decision.type:"";
      select.addEventListener("change",()=>{
        if(select.value&&[...stagedPeople.values()].some(item=>item.type==="person-renamed")) {
          alert("Apply or cancel the standalone rename before staging identity protection.");
          select.value=""; return;
        }
        const conflict=[...staged.entries()].some(([id,choice])=>{
          const item=records.find(record=>record.photoId===id);
          return item?.folder===folder||choice.destinationFolder===folder;
        });
        if(select.value&&conflict) {
          alert("Stage identity protection separately from photo actions for that identity.");
          select.value=stagedPeople.has(decision.personId)?decision.type:"";
          return;
        }
        if(select.value)stagedPeople.set(decision.personId,decision);
        else if(stagedPeople.get(decision.personId)?.type===decision.type)stagedPeople.delete(decision.personId);
        updateStagedCount();
      });
      label.append(select); actionsPanel.append(label);
    }
    if(info.personRenameAction) {
      const decision=info.personRenameAction;
      const label=document.createElement("label"); label.className="stage";
      label.append(document.createTextNode("Rename identity (standalone batch)"));
      const castSlot=/^(Angels|Sisters)\\//.test(folder);
      const scope=document.createElement("span");scope.className="detail";
      scope.textContent=castSlot?
        "Change the recorded person name only; keep the character slot and folder fixed.":
        "Change the person name and folder; preserve photo filenames and stable IDs.";
      const input=document.createElement("input"); input.type="text"; input.maxLength=100;
      input.setAttribute("aria-label","New name for "+folder);
      const current=stagedPeople.get(decision.personId);
      input.value=current?.type==="person-renamed"?current.newName:decision.expectedRecordedName;
      const stage=document.createElement("button"); stage.type="button"; stage.textContent="Stage rename";
      stage.addEventListener("click",()=>{
        const others=[...stagedPeople.entries()].some(([id,value])=>
          id!==decision.personId||value.type!=="person-renamed");
        if(staged.size||others) {
          alert("Rename must be staged alone. Cancel or apply other actions first."); return;
        }
        if(!input.value.trim()||input.value!==input.value.trim()||
          /[<>:"/\\\\|?*\\x00-\\x1f]/.test(input.value)||/[. ]$/.test(input.value)) {
          alert("Enter a Windows-safe name without leading/trailing whitespace."); return;
        }
        const matches=Object.entries(peopleData).filter(([key,value])=>{
          if(key===folder)return false;
          const snapshot=value.personRenameAction;
          return [key.split("/").pop(),snapshot?.expectedDisplayName,snapshot?.expectedRecordedName]
            .some(name=>name?.toLowerCase()===input.value.toLowerCase());
        });
        if(matches.length>1) {
          alert("That name is ambiguous. Resolve the duplicate identity names and refresh first.");return;
        }
        if(matches.length===1) {
          const [otherFolder,otherInfo]=matches[0], other=otherInfo.personRenameAction;
          if(!other||other.expectedRecordedName.toLowerCase()!==input.value.toLowerCase()) {
            alert("That name belongs to a fixed slot or an unavailable identity. Refresh or resolve its rename guards first.");return;
          }
          const effects=(key,snapshot,newName)=>{
            const fixed=/^(Angels|Sisters)\\//.test(key);
            return key+" ["+snapshot.personId+"]\\n"+
              snapshot.expectedRecordedName+" -> "+newName+"\\n"+
              (fixed?"Fixed cast slot, folder, display label and workflow references stay unchanged.":
                "Folder and display name become "+key.split("/")[0]+"/"+newName+".")+"\\n"+
              "Protection stays "+(snapshot.expectedProtected?"ON":"OFF")+".";
          };
          if(!confirm("Confirm standalone TWO-PERSON NAME SWAP?\\n\\n"+
            effects(folder,decision,other.expectedRecordedName)+"\\n\\n"+
            effects(otherFolder,other,decision.expectedRecordedName)+"\\n\\n"+
            "Both histories record this swap. Photos, stable IDs, membership and protection are preserved. "+
            "Download only stages the decision; CLI preview/apply is separate."))return;
          const {type,...snapshot}=other;
          stagedPeople.set(decision.personId,{...decision,newName:other.expectedRecordedName,
            swapWith:snapshot,swapConfirmed:true});
          updateStagedCount();status.textContent="Name swap staged; download and preview both identities.";
          return;
        }
        if(info.identityProtected&&!confirm(
          folder+" is protected. Stage this explicit manual name change? Automatic protection will stay enabled."
        ))return;
        stagedPeople.set(decision.personId,{...decision,newName:input.value});
        updateStagedCount(); status.textContent="Rename staged; download and preview before applying.";
      });
      const cancel=document.createElement("button"); cancel.type="button"; cancel.textContent="Cancel rename";
      const status=document.createElement("span"); status.className="detail";
      if(current?.type==="person-renamed")status.textContent="Rename staged";
      cancel.addEventListener("click",()=>{
        if(stagedPeople.get(decision.personId)?.type==="person-renamed")stagedPeople.delete(decision.personId);
        input.value=decision.expectedRecordedName;status.textContent="";updateStagedCount();
      });
      label.append(scope,input,stage,cancel,status);actionsPanel.append(label);
    } else if(info.personRenameReason) {
      const note=document.createElement("div");note.className="detail";
      note.textContent="Rename unavailable: "+info.personRenameReason;actionsPanel.append(note);
    }
    if(!info.personProtectionAction&&!info.personRenameAction) {
      const note=document.createElement("p");note.className="detail";
      note.textContent="No supported identity action is available in this report. Photo actions remain on each photo.";
      actionsPanel.append(note);
    }
    const reference=primaryFor(folder);
    if(reference) {
      referencePanel.append(card(reference,true));
      const score=document.createElement("div");score.className="detail";
      score.append(document.createTextNode("Core similarity: "));
      const mark=scoreBadge(reference.score,"Reference similarity to this person's core");
      score.append(mark||document.createTextNode("not scored"));referencePanel.append(score);
    } else {
      const note=document.createElement("span"); note.className="detail"; note.textContent="No scored Gallery reference is available for this person.";
      referencePanel.append(note);
    }
    section.append(header);
    const rankings=info.identityMatches||[];
    if(rankings.length) {
      const details=document.createElement("details"); details.className="identity-rankings";
      const summary=document.createElement("summary");
      summary.textContent="Full library likeness rankings ("+rankings.length+")";
      details.append(summary);
      const list=document.createElement("ol"); list.className="relationship-list";
      for(const match of rankings) {
        const entry=document.createElement("li");
        entry.append(personReviewLink(match.key,match.category+": "+match.name));
        const mark=scoreBadge(match.score); if(mark)entry.append(document.createTextNode(" "),mark);
        list.append(entry);
      }
      details.append(list); detailsPanel.append(details);
      const closestByCategory=new Map();
      for(const match of rankings)if(!closestByCategory.has(match.category))closestByCategory.set(match.category,match);
      const closest=document.createElement("div"); closest.className="detail";
      closest.textContent="Closest by category: ";
      for(const match of closestByCategory.values()) {
        closest.append(personReviewLink(match.key,match.category+": "+match.name));
        const mark=scoreBadge(match.score); if(mark)closest.append(document.createTextNode(" "),mark);
        closest.append(document.createElement("br"));
      }
      detailsPanel.insertBefore(closest,details);
    } else {
      const note=document.createElement("div"); note.className="identity-rankings detail";
      note.textContent="No other scored identity is available for cross-reference.";
      detailsPanel.append(note);
    }
    appendPhotoGroups(section,photos);nodes.push(section);
  }
  return nodes;
}
function render() {
  const q=query.value.trim().toLocaleLowerCase();
  visible=records.filter(r=>
    matchesMode(r) &&
    (!group.value||r.group===group.value) &&
    (!bucket.value||r.bucket===bucket.value) &&
    (!state.value||r.state===state.value) &&
    (!person.value||r.folder===person.value) &&
    (!q||(r.folder+" "+r.name+" "+r.reason).toLocaleLowerCase().includes(q))
  ).sort((a,b)=>{
    const groupDiff=(groupOrder.get(a.group)??99)-(groupOrder.get(b.group)??99);
    if(groupDiff)return groupDiff;
    const folderDiff=(folderOrder.get(a.folder)??999999)-(folderOrder.get(b.folder)??999999);
    if(folderDiff)return folderDiff;
    return compare(a,b);
  });
  shown=pageSize; draw();
}
function draw() {
  const page=visible.slice(0,shown);
  if(mode.value==="all") {
    grid.replaceChildren();appendPhotoGroups(grid,page);
  } else {
    grid.replaceChildren(...groupCards(page));
  }
  const people=new Set(visible.map(item=>item.folder)).size;
  count.textContent="Showing "+Math.min(shown,visible.length)+" of "+visible.length+
    " photos"+(mode.value==="all"?"":" across "+people+" people");
  more.hidden=shown>=visible.length;
  more.textContent="Show next "+pageSize;
}
for(const control of [bucket,state,sort,person,scoreCeiling,grouping])control.addEventListener("change",render);
group.addEventListener("change",()=>{fillPeople();render()});
cardSize.addEventListener("change",()=>{
  grid.style.setProperty("--card-min",cardSize.value);
});
framing.addEventListener("change",()=>{
  for(const image of grid.querySelectorAll("img[data-chest]"))
    image.src=framing.value==="head"?image.dataset.head:image.dataset.chest;
});
mode.addEventListener("change",()=>{
  sort.value=mode.value==="all"?"low":"high";
  render();
});
query.addEventListener("input",render);
more.addEventListener("click",()=>{shown+=pageSize;draw()});
download.addEventListener("click",()=>{
  const actions=[...staged.entries()].map(([photoId,decision])=>{
    const record=records.find(item=>item.photoId===photoId);
    return {
      ...decision, photoId, contentSha256:record.contentSha256, sourceBucket:record.bucket,
      personFolder:record.folder, ...(record.personId?{personId:record.personId}:{})
    };
  });
  actions.push(...stagedPeople.values());
  const manifest={
    manifestVersion:1, generatedAt:new Date().toISOString(),
    source:"people-gallery-review", actions
  };
  const blob=new Blob([JSON.stringify(manifest,null,2)+"\\n"],{type:"application/json"});
  const url=URL.createObjectURL(blob), link=document.createElement("a");
  link.href=url; link.download="people-gallery-actions-"+new Date().toISOString().replace(/[:.]/g,"-")+".json";
  link.click(); URL.revokeObjectURL(url);
});
updateStagedCount();
grid.style.setProperty("--card-min",cardSize.value);
render();
"""


def _load_photo(path, key, cache, embed, st, space):
    group, _, folder = key.partition("/")
    sha = cache.sha(path)
    added = False
    if sha not in cache.emb:
        try:
            cache.emb[sha] = embed(path) or {"faces": -1}
        except Exception as error:  # noqa: BLE001 - one unreadable image must not stop the gallery
            print(f"  cannot read {path.name}: {error}")
            cache.emb[sha] = {"faces": -1}
        added = True
    photo = likeness.Photo(path, group, folder, sha, cache.emb[sha])
    if photo.usable(st["minFace"]):
        photo.vec = likeness.nz(photo.raw - space.mean)
    return photo, added


def _local_photo_path(path):
    return str(path.resolve()).casefold()


def action_options(bucket, photo_id, *, anchor=False, protected=False, stageable=True,
                   workflow_photo=False, workflow_selected=False, registered=False, folder=None):
    """Return actions valid for this photo's current location and metadata."""
    if not stageable or not photo_id:
        return []
    junk_option = ("photo-junked", "Junk unwanted/unusable photo to configured junk storage (explicit recovery only; no deletion)")
    retire_option = ("photo-retired", "Retire photo to configured retired storage (recoverable; excluded from matching)")
    movable = not protected and not anchor and not workflow_selected
    if folder and folder.split("/", 1)[0] not in ACTION_ROOTS:
        return [retire_option, junk_option] if movable and action_folder_supported(folder) else []
    options = [
        ("photo-unprotected" if protected else "photo-protected",
         "Unprotect / disable auto-protection" if protected else "Protect / re-enable auto-protection"),
    ]
    if bucket == "Gallery":
        if workflow_photo:
            options.insert(0, ("workflow-photo-selected", "Select as workflow photo"))
        options.insert(0, (
            "anchor-removed" if anchor else "anchor-added",
            "Remove identity anchor" if anchor else "Add identity anchor",
        ))
        options.extend([
            ("sent-to-review", "Send to Review"),
            ("rejected-to-various", "Reject to Various"),
        ])
    else:
        options.extend([
            ("rejected-to-various", "Reject to Various"),
            ("review-approved", "Approve back to Gallery"),
        ])
    if not protected and not anchor and not workflow_selected:
        if registered:
            options.append(("match-rejected", "Reject identity permanently; return to Various"))
        options.append(("match-accepted", "Move to another identity's Review (closest preselected)"))
        options.append(retire_option)
        options.append(junk_option)
    return options


def action_folder_supported(folder):
    """Whether a folder supports identity actions or bounded terminal photo staging."""
    return folder.split("/", 1)[0] in ACTION_ROOTS | {"Artists", "Various"}


def score_context(photo, *, bucket, core_size, core_mode, core_member, sufficient,
                  min_face, group, keep, odd, category_policy=None):
    """Describe the evidence and thresholds behind a displayed photo score."""
    face_count = "unreadable" if photo.faces < 0 else str(photo.faces)
    details = [
        f"Face gate: {min_face}px minimum; this image "
        f"{'meets' if photo.usable(min_face) else 'does not meet'} the gate.",
        (
            f"Reference core: {'meets' if sufficient else 'below'} the "
            f"{category_policy['minimumUsablePhotosForOutlierActions'] if category_policy else 3}-photo "
            "minimum for this category's outlier actions."
        ),
        "Similarity is the centered face-vector cosine score.",
        (
            "Score method: leave this photo out when it is a core member; otherwise compare it with the full active core."
            if bucket == "Gallery" else
            "Score method: compare with the active Gallery core; Review photos are excluded from the core."
        ),
    ]
    if bucket == "Gallery" and category_policy:
        details.append(
            f"Identity core includes scores at or above "
            f"{category_policy['identityCoreMinimumSimilarity']:.2f}; "
            "a single usable photo remains the provisional core."
        )
        details.append(
            f"Review suggestion: below "
            f"{category_policy['reviewSuggestionBelowSimilarity']:.2f}; "
            f"split candidate below {category_policy['splitCandidateBelowSimilarity']:.2f} "
            f"after {category_policy['minimumUsablePhotosForOutlierActions']} usable photos."
        )
    if category_policy:
        details.append(
            f"Core eligibility uses this category's configured "
            f"{category_policy['identityCoreMinimumSimilarity']:.2f} similarity threshold "
            "with iterative core/leave-one-out checks, not the displayed Review score alone. "
            "Usable, unambiguous Gallery photos are candidates; valid anchors seed the core. "
            "A remaining single eligible photo is provisional, not a confirmed identity."
        )
    details.extend([
        "Approve back to Gallery changes location only; it does not add photo protection or an identity anchor. "
        "Core eligibility is recomputed when the report or matcher next runs.",
        "Protect photo does not approve a Review photo or make it an anchor. "
        "Review is never core. A manually protected Gallery photo is excluded unless it is also a valid anchor; automatic protection preserves only prior eligible core status.",
        "Identity protection blocks automatic Gallery membership/category changes; "
        "it does not change similarity scores or confirm a photo's identity.",
    ])
    return {
        "coreSize": core_size,
        "coreMode": core_mode,
        "coreMember": core_member,
        "facePixels": photo.px,
        "faceCount": photo.faces,
        "minFace": min_face,
        "usable": photo.usable(min_face),
        "details": details,
    }


def closest_matches(photo, folder, identity_centroids, min_face):
    """Return the top three same-side photo-to-core similarities, not routing decisions."""
    if not photo.usable(min_face):
        return []
    ranking = sorted(
        (
            (float(photo.vec @ vector), candidate)
            for candidate, vector in identity_centroids.items()
            if candidate != folder and not likeness.apart(folder, candidate)
        ),
        key=lambda row: (-row[0], row[1].casefold()),
    )
    return [
        {
            "folder": candidate, "category": candidate.split("/", 1)[0],
            "name": candidate.split("/", 1)[1], "score": score,
        }
        for score, candidate in ranking[:3]
    ]


def closest_other(photo, folder, identity_centroids, min_face):
    """Preserve the existing single-match label and public helper contract."""
    matches = closest_matches(photo, folder, identity_centroids, min_face)
    return f"{matches[0]['folder']} ({matches[0]['score']:.2f})" if matches else ""


def assign_primary_references(items):
    """Mark one workflow, trusted, core-ranked or provisional reference per person."""
    by_folder = collections.defaultdict(list)
    for item in items:
        by_folder[item["folder"]].append(item)
    for folder_items in by_folder.values():
        gallery_items = [item for item in folder_items if item["bucket"] == "Gallery"]
        workflows = [item for item in folder_items if item["workflowSelected"]]
        anchors = [item for item in gallery_items if item["identityAnchor"]]
        core = [item for item in gallery_items if item["state"] == "Core member"]
        if workflows:
            reference = min(workflows, key=lambda item: item["name"].casefold())
            label = "Workflow-selected photo"
        elif anchors:
            reference = min(
                anchors,
                key=lambda item: (
                    -(item["score"] if item["score"] is not None else float("-inf")),
                    item["name"].casefold(),
                ),
            )
            label = "User-confirmed identity anchor"
        elif core:
            reference = min(
                core,
                key=lambda item: (
                    -(item["score"] if item["score"] is not None else float("-inf")),
                    item["name"].casefold(),
                ),
            )
            label = "Score-ranked provisional core member"
        else:
            scored = [item for item in gallery_items if item["score"] is not None]
            reference = min(
                scored,
                key=lambda item: (-item["score"], item["name"].casefold()),
                default=None,
            )
            label = "Score-ranked reference · provisional, not confirmed"
        if reference:
            reference["primaryReference"] = True
            reference["referenceLabel"] = label


def collect_items(
    cfg, st, work, cache, space, catalog, *,
    include_artists=False, embed=None, keep=0.25, policy=None,
):
    """Build scored image records; Review candidates never enter an identity core."""
    if include_artists:
        raise ValueError("Artists have a separate browser; use bin\\artists-gallery.cmd")
    domains.require_general_space(space)
    policy = policy or default_policy()
    catalog = metadata.with_configured_anchors(catalog, cfg, space.photos)
    category_order = (*(category for category in policy["categoryOrder"] if category != "Artists"), "Various")
    groups = set(category_order)
    group_order = {group: index for index, group in enumerate(category_order)}
    folders = [
        (key, folder) for key, folder in likeness.library_people(cfg, st, work)
        if likeness.status_of(key) in groups
    ]
    if (pathlib.Path(work) / "Various" / "review").is_dir() and originals.images(
        pathlib.Path(work) / "Various" / "review"
    ):
        folders.append(("Various", pathlib.Path(work) / "Various"))
    selected_names = list(cfg.get("photos", {}).values())
    base_selected_by_hero = {
        hero.casefold(): metadata.photo_id_from_name(name)
        for hero, name in cfg.get("photos", {}).items()
        if isinstance(name, str)
    }
    for flow in cfg.get("flows", {}).values():
        selected_names.extend(flow.get("photos", {}).values())
    selected_ids = {
        photo_id for name in selected_names if isinstance(name, str)
        if (photo_id := metadata.photo_id_from_name(name))
    }
    active_by_path = {_local_photo_path(photo.path): photo for photo in space.photos}
    gallery_by_key, review_by_key = {}, {}
    added_embeddings = False
    embed = embed or likeness.Embedder()
    held = likeness.cleanup_hold(work)

    for key, folder in folders:
        gallery = []
        for path in originals.images(folder / "gallery") if key != "Various" else ():
            photo = active_by_path.get(_local_photo_path(path))
            if photo is None:
                photo, added = _load_photo(path, key, cache, embed, st, space)
                added_embeddings |= added
            gallery.append(photo)
        reviews = []
        for path in originals.images(folder / "review"):
            photo, added = _load_photo(path, key, cache, embed, st, space)
            added_embeddings |= added
            reviews.append((photo, photo.sha in held))
        gallery_by_key[key] = gallery
        review_by_key[key] = reviews
    if added_embeddings:
        cache.save()

    folders.sort(key=lambda entry: (
        group_order[likeness.status_of(entry[0])],
        -len(gallery_by_key[entry[0]]) if likeness.status_of(entry[0]) not in ("Sisters", "Angels") else 0,
        entry[0].casefold(),
    ))
    person_order = {key: index for index, (key, _folder) in enumerate(folders)}
    all_photos = list(space.photos)
    all_photos.extend(photo for records in review_by_key.values() for photo, _ in records)
    content_hashes = {}

    def manifest_hash(photo):
        key = _local_photo_path(photo.path)
        if key not in content_hashes:
            content_hashes[key] = metadata.content_sha256(photo.path)
        return content_hashes[key]

    def rejection_context(photo, photo_id):
        state = rejections.candidate_state(catalog, photo_id, manifest_hash(photo))
        return {
            "rejectedIdentityIds": catalog["photos"].get(photo_id, {}).get("rejectedPersonIds", []),
            "rejectionMetadataStale": state.get("rejectionMetadataStale", False),
        }

    photo_records = [
        (
            metadata.photo_id_from_name(photo.name),
            metadata.content_sha256(photo.path) if metadata.photo_id_from_name(photo.name) in catalog["photos"] else None,
        )
        for photo in all_photos
    ]
    protected_ids, stale_ids, ambiguous_ids = catalog_photo_flags(photo_records, catalog)

    people_by_folder = collections.defaultdict(list)
    for person_id, person in catalog["people"].items():
        people_by_folder[person["folder"]].append((person_id, person))

    policy_centroids = {}
    for key, _folder in folders:
        records = people_by_folder.get(key, [])
        person = records[0][1] if len(records) == 1 else None
        usable = [
            photo for photo in gallery_by_key[key]
            if photo.usable(st["minFace"])
        ]
        category_policy = policy["categoryPolicies"].get(likeness.status_of(key), {})
        audit = audit_person(
            [photo.vec for photo in usable],
            [metadata.photo_id_from_name(photo.name) for photo in usable],
            anchor_ids=person["identityAnchors"] if person else (),
            protected_ids=core_excluded_protection(catalog, protected_ids),
            stale_ids=stale_ids,
            ambiguous_ids=ambiguous_ids,
            minimum_core=category_policy.get("minimumUsablePhotosForOutlierActions", 3),
            core_minimum=category_policy.get("identityCoreMinimumSimilarity", 0.3),
            seed_floor=category_policy.get("identityCoreMinimumSimilarity", 0.3),
        )
        if audit["core_vector"] is not None:
            policy_centroids[key] = audit["core_vector"]
    identity_rankings = rank_identity_centroids(
        space,
        [key for key, _folder in folders],
        categories={key: likeness.status_of(key) for key, _folder in folders},
        centroids=policy_centroids,
        category_order=category_order,
    )

    items, warnings = [], []
    active_keys = {key for key, _ in folders}
    for person in catalog["people"].values():
        if person["folder"] not in active_keys:
            warnings.append(f"Catalogue folder not found: {person['displayName']} → {person['folder']}")
    for key, folder in folders:
        gallery = gallery_by_key[key]
        reviews = review_by_key[key]
        records = people_by_folder.get(key, [])
        conflict = len(records) > 1
        person = records[0][1] if len(records) == 1 else None
        identity_protected = bool(
            (person and person.get("protected"))
            or policy["categoryPolicies"].get(likeness.status_of(key), {}).get("identityProtectedByDefault")
        )
        person_id = records[0][0] if len(records) == 1 else None
        rename_action, rename_reason = person_rename.decision(work, key, person_id, person, cfg)
        anchors = set(person["identityAnchors"]) if person else set()
        category_policy = policy["categoryPolicies"].get(likeness.status_of(key), {})
        usable = [photo for photo in gallery if photo.usable(st["minFace"])]
        photo_ids = [metadata.photo_id_from_name(photo.name) for photo in usable]
        result = audit_person(
            [photo.vec for photo in usable],
            photo_ids,
            anchor_ids=anchors if not conflict else (),
            protected_ids=core_excluded_protection(catalog, protected_ids),
            stale_ids=stale_ids,
            ambiguous_ids=ambiguous_ids,
            minimum_core=category_policy.get("minimumUsablePhotosForOutlierActions", 3),
            core_minimum=category_policy.get("identityCoreMinimumSimilarity", 0.3),
            seed_floor=category_policy.get("identityCoreMinimumSimilarity", 0.3),
        )
        if conflict:
            warnings.append(f"Conflicting catalogue records for {key}; identity anchors were ignored")
        scores = {id(photo): result["scores"][i] for i, photo in enumerate(usable)}
        indices = {id(photo): i for i, photo in enumerate(usable)}
        core = set(result["core_indices"])
        comparison = "trusted-anchor-seeded core" if result["mode"] == "trusted" else "provisional core"
        if result["mode"] == "none":
            comparison = "no usable identity core"

        for photo in gallery:
            photo_id = metadata.photo_id_from_name(photo.name)
            hero = key.split("/", 1)[1]
            workflow_photo_available = (
                likeness.status_of(key) in ("Angels", "Sisters")
                and hero.casefold() in base_selected_by_hero
                and base_selected_by_hero[hero.casefold()] != photo_id
            )
            index = indices.get(id(photo))
            score = scores.get(id(photo))
            consistency = evaluate_photo_consistency(
                likeness.status_of(key),
                score=score,
                usable_photo_count=max(1, len(usable)),
                identity_protected=identity_protected,
                photo_protected=photo_id in protected_ids,
                workflow_selected=photo_id in selected_ids,
                policy=policy,
            )
            if conflict:
                state, reason = "Catalogue conflict", "Folder is claimed by more than one person record"
            elif photo_id in stale_ids:
                state, reason = "Stale metadata", "Content hash changed; stored anchor/protection decisions are ignored"
            elif photo_id in ambiguous_ids:
                state, reason = "Ambiguous ID", "Duplicate source ID; excluded from the identity core"
            elif index is not None and index in result["anchor_indices"]:
                state, reason = "Identity anchor", "User-selected trusted likeness anchor"
            elif photo_id in protected_ids:
                state, reason = "Protected only", "Kept in the gallery but excluded from the identity core"
            elif not photo.usable(st["minFace"]):
                state, reason = "Unscored", "No usable face vector"
            elif consistency["decision"] == "split-review":
                state, reason = "Split candidate", consistency["reason"]
            elif consistency["decision"] == "review":
                state, reason = "Review suggested", consistency["reason"]
            elif (
                index is not None
                and index not in core
                and score is not None
                and score < category_policy.get("identityCoreMinimumSimilarity", 0.3)
            ):
                state = "Excluded from core"
                reason = (
                    "Below this category's identity-core threshold; "
                    "the photo remains in Gallery unless a separate action is approved"
                )
            elif not result["sufficient"]:
                state, reason = "Small core", "Too few usable photos for this category's outlier actions"
            elif photo_id in selected_ids:
                state, reason = "Workflow-protected", "Selected for a workflow; automatic Review routing is blocked"
            elif index in core:
                state, reason = "Core member", "Included in the trusted-seeded or provisional core"
            else:
                state, reason = "Consistent", "Similarity is measured against the current person core"
            match = closest_other(photo, key, policy_centroids, st["minFace"])
            context = score_context(
                photo,
                bucket="Gallery",
                core_size=len(core),
                core_mode=result["mode"],
                core_member=index in core if index is not None else False,
                sufficient=result["sufficient"],
                min_face=st["minFace"],
                group=likeness.status_of(key),
                keep=keep,
                odd=st["odd"],
                category_policy=category_policy,
            )
            items.append({
                "folder": key,
                "group": likeness.status_of(key),
                "identityMatches": identity_rankings.get(key, []),
                "groupOrder": group_order[likeness.status_of(key)],
                "personOrder": person_order[key],
                "bucket": "Gallery",
                "name": photo.name,
                "photoId": photo_id,
                "contentSha256": manifest_hash(photo),
                **rejection_context(photo, photo_id),
                "personId": person_id,
                "identityProtected": identity_protected,
                "personProtectionAction": person_protection_action(key, person_id, person),
                "personRenameAction": rename_action,
                "identityNames": identity_names.presentation(person, folder, catalog=catalog),
                "identityProtectionInfo": protection.describe(person),
                "photoProtectionInfo": protection.describe(catalog["photos"].get(photo_id)),
                "personRenameReason": rename_reason,
                "workflowSelected": photo_id in selected_ids,
                "identityAnchor": bool(
                    photo_id in anchors and photo_id not in stale_ids and photo_id not in ambiguous_ids
                ),
                "identityOrder": identity_order_key(
                    photo_id in anchors and photo_id not in stale_ids and photo_id not in ambiguous_ids,
                    index in core,
                    score,
                    photo.name,
                )[0],
                "primaryReference": False,
                "referenceLabel": "",
                "stageable": bool(
                    photo_id and photo_id not in ambiguous_ids and not conflict
                    and action_folder_supported(key)
                ),
                "stageOptions": action_options(
                    "Gallery", photo_id, folder=key, anchor=photo_id in anchors and photo_id not in stale_ids,
                    protected=photo_id in protected_ids,
                    registered=bool(person_id),
                    workflow_photo=workflow_photo_available,
                    workflow_selected=photo_id in selected_ids,
                    stageable=(
                        photo_id not in ambiguous_ids and not conflict
                        and action_folder_supported(key)
                    ),
                ),
                "stageReason": (
                    "Actions are disabled for this folder because the identity catalogue schema does not support its root"
                    if not action_folder_supported(key) else
                    "Actions require a unique stable photo ID and an unambiguous person folder"
                    if not photo_id or photo_id in ambiguous_ids or conflict else ""
                ),
                "score": score,
                "scoreContext": context,
                "scoreDetails": context["details"],
                "state": state,
                "comparison": comparison,
                "reason": reason,
                "best_other": match,
                "closestMatches": closest_matches(photo, key, policy_centroids, st["minFace"]),
                "_photo": photo,
            })

        for photo, cleanup_held in reviews:
            photo_id = metadata.photo_id_from_name(photo.name)
            score = None
            if photo.usable(st["minFace"]) and result["core_vector"] is not None:
                score = float(photo.vec @ result["core_vector"])
            if cleanup_held:
                state, reason = "Review · cleanup held", "Held for manual crop clean-up"
            else:
                state, reason = (
                    ("Hold", "Unresolved candidate; not a named identity or active core")
                    if key == "Various" else
                    ("Review", "Candidate is outside the active gallery and never enters its core")
                )
            if photo_id in stale_ids:
                reason += "; stored metadata is stale"
            elif photo_id in ambiguous_ids:
                reason += "; duplicate source ID is ambiguous"
            elif photo_id in anchors:
                reason += "; still registered as an anchor, but not used while in Review"
            elif photo_id in protected_ids:
                reason += "; protection remains recorded, but this photo is not in the active core"
            if score is None and not cleanup_held:
                reason += "; no usable score"
            context = score_context(
                photo,
                bucket="Review",
                core_size=len(core),
                core_mode=result["mode"],
                core_member=False,
                sufficient=result["sufficient"],
                min_face=st["minFace"],
                group=likeness.status_of(key),
                keep=keep,
                odd=st["odd"],
                category_policy=category_policy,
            )
            items.append({
                "folder": key,
                "group": likeness.status_of(key),
                "identityMatches": identity_rankings.get(key, []),
                "groupOrder": group_order[likeness.status_of(key)],
                "personOrder": person_order[key],
                "bucket": "Review",
                "name": photo.name,
                "photoId": photo_id,
                "contentSha256": manifest_hash(photo),
                **rejection_context(photo, photo_id),
                "personId": person_id,
                "identityProtected": identity_protected,
                "personProtectionAction": person_protection_action(key, person_id, person),
                "personRenameAction": rename_action,
                "identityNames": identity_names.presentation(person, folder, catalog=catalog),
                "identityProtectionInfo": protection.describe(person),
                "photoProtectionInfo": protection.describe(catalog["photos"].get(photo_id)),
                "personRenameReason": rename_reason,
                "workflowSelected": photo_id in selected_ids,
                "identityAnchor": bool(
                    photo_id in anchors and photo_id not in stale_ids and photo_id not in ambiguous_ids
                ),
                "identityOrder": identity_order_key(False, False, score, photo.name)[0],
                "primaryReference": False,
                "referenceLabel": "",
                "stageable": bool(
                    photo_id and photo_id not in ambiguous_ids and not conflict
                    and action_folder_supported(key)
                ),
                "stageOptions": action_options(
                    "Review", photo_id, folder=key, protected=photo_id in protected_ids,
                    registered=bool(person_id),
                    workflow_selected=photo_id in selected_ids,
                    stageable=(
                        photo_id not in ambiguous_ids and not conflict
                        and action_folder_supported(key)
                    ),
                ),
                "stageReason": (
                    "Actions are disabled for this folder because the identity catalogue schema does not support its root"
                    if not action_folder_supported(key) else
                    "Actions require a unique stable photo ID and an unambiguous person folder"
                    if not photo_id or photo_id in ambiguous_ids or conflict else ""
                ),
                "score": score,
                "scoreContext": context,
                "scoreDetails": context["details"],
                "state": state,
                "comparison": comparison,
                "reason": reason,
                "best_other": closest_other(photo, key, policy_centroids, st["minFace"]),
                "closestMatches": closest_matches(photo, key, policy_centroids, st["minFace"]),
                "_photo": photo,
            })

    assign_primary_references(items)

    items.sort(key=lambda item: (
        item["groupOrder"],
        item["personOrder"],
        *identity_order_key(
            item["identityOrder"] == 0,
            item["identityOrder"] == 1,
            item["score"],
            item["name"],
        ),
    ))
    return items, warnings


def alignment_evidence(photo, work, out):
    """Expose only a source- and artifact-verified persisted alignCrop image."""
    data = getattr(photo, "alignment_evidence", None)
    if work is None:
        return {"state": "missing"}
    try:
        source_path = photo.path.resolve().relative_to(pathlib.Path(work).resolve()).as_posix()
        source_sha256 = metadata.content_sha256(photo.path)
    except (OSError, ValueError):
        return {"state": "invalid"}
    result = {
        "state": "missing",
        "sourcePath": source_path,
        "sourceSha256": source_sha256,
    }
    if photo.faces == 0:
        result["state"] = "no-face"
        return result
    if photo.faces < 0:
        result["state"] = "unreadable"
        return result
    if not isinstance(data, dict):
        return result
    result.update({
        "model": data.get("model"),
        "modelId": data.get("modelId"),
        "alignmentSha256": data.get("alignmentSha256"),
        "width": data.get("width"),
        "height": data.get("height"),
    })
    if data.get("state") == "read-only-not-persisted":
        result["state"] = "read-only-not-persisted"
        return result
    model_id = data.get("modelId")
    artifact = data.get("artifact")
    model = data.get("model")
    detector = model.get("detector") if isinstance(model, dict) else None
    recognizer = model.get("recognizer") if isinstance(model, dict) else None
    try:
        expected_model_id = hashlib.sha256(
            json.dumps(model, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
    except (TypeError, ValueError):
        expected_model_id = None
    if (
        data.get("state") != "persisted"
        or data.get("sourceSha256") != source_sha256
        or not isinstance(detector, dict)
        or detector.get("name") != "YuNet"
        or not isinstance(recognizer, dict)
        or recognizer.get("name") != "SFace"
        or model.get("alignment") != "FaceRecognizerSF.alignCrop"
        or not isinstance(model.get("opencv"), str)
        or not isinstance(model_id, str)
        or not re.fullmatch(r"[0-9a-f]{64}", model_id)
        or model_id != expected_model_id
        or artifact != f"{source_sha256}-{model_id}.png"
        or data.get("artifactSha256") != data.get("alignmentSha256")
    ):
        result["state"] = "invalid"
        return result
    domain = "artists" if photo.group == "Artists" else "general"
    library_root = pathlib.Path(work).resolve()
    likeness_root = likeness.cw.storage_root(
        likeness.cw.load_cfg(), "likeness", root=library_root
    )
    evidence_root = likeness_root / domain / "face-evidence"
    target = evidence_root / artifact
    try:
        evidence_root.resolve().relative_to(library_root)
        if (
            any(likeness.cw.is_reparse_point(path) for path in (
                likeness_root,
                likeness_root / domain,
                evidence_root,
                target,
            ))
            or target.resolve().parent != evidence_root.resolve()
            or not target.is_file()
            or hashlib.sha256(target.read_bytes()).hexdigest() != data["artifactSha256"]
        ):
            result["state"] = "invalid"
            return result
    except (OSError, ValueError):
        result["state"] = "invalid"
        return result
    relative = os.path.relpath(target, out).replace(os.sep, "/")
    from urllib.parse import quote

    result.update(
        state="verified",
        href=quote(relative, safe="/._-"),
        alignmentSha256=data["alignmentSha256"],
    )
    return result


def write_thumbnails(items, out, work=None):
    """Write/reuse named, content-keyed head and chest-up derivatives."""
    from likeness_library.derivatives import thumbnail, verified

    thumb_dir = out / "people_gallery_review_files"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    public_items = []
    generated = {}

    for item in items:
        photo = item["_photo"]
        stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", photo.path.stem).strip("._") or "photo"
        targets = {}
        diagnostics = []
        provenance = {}
        for framing in ("chest", "head", "face"):
            data, key, diagnostic = thumbnail(
                photo.path, "head" if framing == "face" else framing, photo.box,
                (320, 320) if framing == "face" else (320, 400))
            if diagnostic:
                diagnostics.append(diagnostic)
            else:
                source, record = verified(photo.path, "head" if framing == "face" else framing, photo.box)
                provenance[framing] = {"href": source.resolve().as_uri(),
                                       "sha256": record["sha256"], "recipe": record["recipe"],
                                       "sourceSha256": record["sourceSha256"]}
            target = thumb_dir / f"{stem}_{framing}_{key}.jpg"
            if not target.exists():
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(
                        mode="wb",
                        prefix=f".{stem}_{framing}_",
                        suffix=".tmp",
                        dir=thumb_dir,
                        delete=False,
                    ) as output:
                        temporary = pathlib.Path(output.name)
                        output.write(data)
                        output.flush()
                        os.fsync(output.fileno())
                    os.replace(temporary, target)
                finally:
                    if temporary is not None and temporary.exists():
                        temporary.unlink()
            targets[framing] = (pathlib.Path(thumb_dir.name) / target.name).as_posix()
            generated[targets[framing]] = data
        try:
            source, record = verified(photo.path, "padded")
            provenance["padded"] = {"href": source.resolve().as_uri(),
                                    "sha256": record["sha256"], "recipe": record["recipe"],
                                    "sourceSha256": record["sourceSha256"]}
        except (OSError, ValueError, KeyError) as exc:
            diagnostics.append(str(exc))
        public = {key: value for key, value in item.items() if key != "_photo"}
        public["derivativeDiagnostics"] = diagnostics
        public["thumbnailProvenance"] = provenance
        public["alignmentEvidence"] = alignment_evidence(photo, work, out)
        public["reason"] = "; ".join([public.get("reason", ""), *diagnostics]).strip("; ")
        public["thumbnail"] = targets["chest"]
        public["thumbnailHead"] = targets["head"]
        public["thumbnailFace"] = targets["face"]
        public["href"] = photo.path.resolve().as_uri()
        public_items.append(public)
    report_assets.record(out, generated)
    return public_items, thumb_dir


def person_protection_action(folder, person_id, person):
    """Only registered, active Models/Prospects have an identity toggle."""
    if (
        folder.split("/", 1)[0] not in {"Models", "Prospects"}
        or not person_id or not person or person.get("mergedInto")
    ):
        return None
    protected = bool(person.get("protected", False))
    return {
        "type": "person-unprotected" if protected else "person-protected",
        "personId": person_id, "personFolder": folder, "expectedProtected": protected,
    }


def render_html(
    items, stamp, warnings=(), policy=None, reports_prefix="../", section_links=None,
):
    """Render a local page with client-side filters and bounded card rendering."""
    if section_links is None:
        cfg = likeness.cw.load_cfg()
        section_links = gallery_chrome.configured_sections(
            likeness.cw.work_root(cfg), cfg
        )
    policy = policy or default_policy()
    people_count = len({item["folder"] for item in items if item.get("group") != "Various"})
    people_label = "person" if people_count == 1 else "people"
    photos_label = "photo" if len(items) == 1 else "photos"
    people_data = {}
    for item in items:
        people_data.setdefault(item["folder"], {
            "group": item.get("group"),
            "identityMatches": item.get("identityMatches", []),
            "identityProtected": item.get("identityProtected", False),
            "personProtectionAction": item.get("personProtectionAction"),
            "personRenameAction": item.get("personRenameAction"),
            "identityNames": item.get("identityNames"),
            "identityProtectionInfo": item.get("identityProtectionInfo"),
            "personRenameReason": item.get("personRenameReason", ""),
        })
    public_items = [
        {key: value for key, value in item.items() if key != "identityMatches"}
        for item in items
    ]
    payload = json.dumps(public_items, ensure_ascii=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    people_payload = json.dumps(people_data, ensure_ascii=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    guidance_payload = json.dumps(gallery_chrome.CARD_USE_GUIDANCE, ensure_ascii=True)
    generation_link = next(
        (href for label, href in (section_links or ()) if label == "Rendering"), None
    )
    generation_href = (
        reports_prefix + generation_link
        if reports_prefix is not None and generation_link is not None
        else ""
    )
    generation_payload = json.dumps(generation_href, ensure_ascii=True).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    policy_payload = json.dumps(policy, ensure_ascii=True).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    warning_html = ""
    if warnings:
        entries = "".join(f"<li>{html.escape(message)}</li>" for message in warnings)
        warning_html = f'<ul class="warnings">{entries}</ul>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>People gallery review</title><style>{gallery_chrome.CSS}{CSS}</style></head><body id="top">
{gallery_chrome.masthead(
    "People", reports_prefix, "People library", section_links=section_links
)}
<div class="site-page">
<header class="page-header"><div><h1>People gallery review</h1>
<p class="note">Generated {stamp} · {people_count} {people_label} · {len(items)} {photos_label}</p>
<p class="note">Stage actions here, then download the manifest to review and apply separately.</p></div>
<div class="header-side"><div class="header-label">Likeness</div>
<div class="score-legend">{render_score_legend(policy)}</div></div></header>
{gallery_chrome.navigation([("Overview", "people_gallery.html"), ("Photo review", "people_gallery_review.html"), ("Intake runs", "intake_runs.html")], "Photo review")}
{render_policy_panel(policy)}
<script type="application/json" id="likeness-policy-data">{policy_payload}</script>
{warning_html}
<div class="controls">
<div class="filter-controls">
<label class="search-control">Search <input id="query" type="search" placeholder="folder, filename, reason"></label>
<div class="filter-options">
<label>View <select id="mode"><option value="people">People</option><option value="review">Review queue</option><option value="low">Low scores</option><option value="all">All photos (flat)</option></select></label>
<label>Category <select id="group"></select></label>
<label>Person <select id="person"></select></label>
<label>Thumbnail <select id="framing"><option value="chest">Chest-up</option><option value="head">Head</option></select></label>
<label>Tile size <select id="card-size"><option value="170px">Small</option><option value="260px" selected>Medium</option><option value="340px">Large</option></select></label>
<label>Location <select id="bucket"></select></label>
<label>Grouping <select id="grouping"><option value="mixed">Mixed</option><option value="split">Split Gallery / Review</option></select></label>
<label>State <select id="state"></select></label>
</div>
</div>
<div class="sort-controls">
<span class="count" id="count"></span>
<label>Order <select id="sort"><option value="identity">Core identity first</option><option value="high">Highest identity score</option><option value="low">Lowest identity score</option><option value="name">Name</option></select></label>
<label>Low-score cutoff <input id="score-ceiling" type="number" min="-1" max="1" step="0.01" value="0.25"></label>
</div>
</div>
<div class="actions"><button id="download" type="button" disabled>Download staged actions</button><span id="staged-count">0 actions staged</span></div>
<div id="grid"></div><button id="more" type="button">Show next {PAGE_SIZE}</button>
{gallery_chrome.footer("Stage and export here · Apply reviewed actions separately")}
<script id="review-data" type="application/json">{payload}</script>
<script id="people-data" type="application/json">{people_payload}</script>
<script id="card-use-guidance" type="application/json">{guidance_payload}</script>
<script id="generation-index" type="application/json">{generation_payload}</script>
<script id="category-order" type="application/json">{json.dumps([category for category in policy["categoryOrder"] if category != "Artists"] + ["Various"])}</script>
<script>{SCRIPT}</script>
</div></body></html>
"""


def main(argv=None):
    with domains.activate("general", read_only=True):
        return _main(argv)


def _main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-only", action="store_true", help="refresh only checked intake history; preview unless --apply")
    history_mode = parser.add_mutually_exclusive_group()
    history_mode.add_argument("--dry-run", action="store_true")
    history_mode.add_argument("--check", action="store_true")
    history_mode.add_argument("--apply", action="store_true")
    parser.add_argument("--artists", action="store_true", help="retired: use artists-gallery.cmd")
    parser.add_argument("--keep", type=float, default=0.25, help="Prospect borderline score (default: 0.25)")
    parser.add_argument("--out", help="report folder under the configured reports root (relative paths start there)")
    parser.add_argument("--root", help="photo library folder (default: workspaces.json paths.productionRoot)")
    parser.add_argument("--cache", help="embedding cache file (default: the user-local likeness cache)")
    parser.add_argument("--policy", help="versioned likeness policy JSON")
    parser.add_argument(
        "--no-renders",
        action="store_true",
        help="accepted by the shared gallery launcher; this page does not load ComfyUI renders",
    )
    args = parser.parse_args(argv)
    if args.artists:
        parser.error("--artists no longer mixes Artists into people pages; use bin\\artists-gallery.cmd")
    if not args.history_only and (args.dry_run or args.check or args.apply):
        parser.error("--dry-run/--check/--apply require --history-only")
    policy = load_policy(args.policy)
    cfg, st, work, cache, space = likeness.build(
        types.SimpleNamespace(root=args.root, cache=args.cache, embedder=None, policy=args.policy)
    )
    reports = likeness.cw.storage_root(cfg, "reports", root=work)
    out = likeness.cw.storage_output_path(cfg, "reports", args.out or "library", root=work)
    if args.history_only:
        if args.apply:
            report = preparation_history.publish_staged(work, out, cfg=cfg)
            report_assets.record(out, {report.name: report.read_bytes()})
            print(f"Refreshed checked intake history only: {report}")
            return 0
        payload = preparation_provenance.build_index(work, out, [], cfg=cfg).history_html()
        report = out / "intake_runs.html"
        current = report.is_file() and report.read_text(encoding="utf-8") == payload
        print(f"Intake history {'current' if current else 'needs refresh'}: {report}")
        return int(args.check and not current)
    catalog = metadata.load_catalog(metadata.path_for_root(work))
    items, warnings = collect_items(
        cfg, st, work, cache, space, catalog,
        include_artists=args.artists, keep=args.keep, policy=policy
    )
    out.mkdir(parents=True, exist_ok=True)
    provenance = preparation_provenance.build_index(
        work,
        out,
        [(item["_photo"].path, item.get("photoId")) for item in items],
        "general",
    )
    history = provenance.history_html().encode("utf-8")
    with verification_reads.session(work, label="Review inputs"):
        for item in items:
            item["preparationEvidence"] = provenance.evidence(
                item["_photo"].path, item.get("photoId"),
            )
            item["generationSource"] = item["_photo"].path.relative_to(work).as_posix()
        public_items, thumb_dir = write_thumbnails(items, out, work)
    gallery_chrome.publish_banner(reports)
    report = out / "people_gallery_review.html"
    report.write_text(
        render_html(
            public_items,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            warnings,
            policy=policy,
            reports_prefix=gallery_chrome.reports_prefix(out, reports),
            section_links=gallery_chrome.configured_sections(work, cfg),
        ),
        encoding="utf-8",
    )
    (out / "intake_runs.html").write_bytes(history)
    report_assets.record(out, {report.name: report.read_bytes(), "intake_runs.html": history})
    print(f"people gallery review: {len(public_items)} photo(s)")
    print(f"  {report}")
    print(f"  {thumb_dir} ({len(list(thumb_dir.glob('*.jpg')))} cached thumbnails)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
