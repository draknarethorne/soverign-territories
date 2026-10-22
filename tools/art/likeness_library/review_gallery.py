#!/usr/bin/env python3
"""Build a local, read-only photo review page for person galleries and Review folders."""
import argparse
import collections
import datetime
import html
import io
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
from likeness_library import metadata  # noqa: E402
from likeness_library.audit import audit_person, catalog_photo_flags, identity_order_key  # noqa: E402
from likeness_library.cross_reference import CATEGORY_ORDER, rank_identity_centroids, score_band  # noqa: E402
from likeness_library.policy import (
    default_policy,
    evaluate_photo_consistency,
    load_policy,
    render_policy_panel,
    render_score_legend,
)  # noqa: E402
from likeness_library.thumbnails import crop_thumbnail, face_thumbnail  # noqa: E402

PAGE_SIZE = 100
SECTIONS = CATEGORY_ORDER
GROUP_ORDER = CATEGORY_ORDER
ACTION_ROOTS = {"Angels", "Sisters", "Models", "Prospects", "Potentials"}

CSS = """
body{font:15px Segoe UI,Arial,sans-serif;margin:20px;background:#faf8f3;color:#222}
h1{margin:0 0 4px}.note{color:#555;max-width:1100px}.warnings{color:#8a3b16}
.page-header{display:flex;justify-content:space-between;align-items:flex-start;gap:24px;padding:16px 18px;background:#fff;border:1px solid #ded8ce;border-radius:10px}.page-header p{margin:5px 0 0}.header-side{text-align:right}.header-label{font-size:.75em;color:#666;text-transform:uppercase;letter-spacing:.06em}.score-legend{display:flex;justify-content:flex-end;gap:6px;flex-wrap:wrap;margin-top:5px}
.controls{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px 20px;align-items:end;margin:16px 0}
.filter-controls{display:grid;gap:8px;min-width:0}.search-control{display:flex;flex-direction:column;align-items:flex-start;gap:4px;width:min(100%,520px)}
.search-control input{width:100%;box-sizing:border-box}.filter-options{display:flex;justify-content:flex-start;gap:10px;flex-wrap:wrap}
.sort-controls{display:flex;justify-content:flex-end;gap:10px;flex-wrap:wrap;align-items:flex-end}
.controls input,.controls select,.controls button{font:inherit;padding:7px}
.count{color:#555;white-space:nowrap}#grid{display:block;--card-min:260px}
.photo-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(var(--card-min),1fr));gap:12px}
article{background:white;border:1px solid #ded8ce;border-radius:6px;padding:8px;min-width:0}
article.primary{border:3px solid #8b6d32}
article img{display:block;width:100%;aspect-ratio:4/5;object-fit:cover;background:#eee}
article a{color:#28527a}.name{font-weight:600;overflow-wrap:anywhere;margin:7px 0}
.badge{display:inline-block;border-radius:4px;background:#eee;padding:2px 6px;margin:0 4px 4px 0;font-size:.82em;font-weight:600}
.category-sisters{background:#e8e0f2;color:#493365}.category-angels{background:#e4efff;color:#244f85}
.category-models{background:#e4f2e5;color:#285b31}.category-prospects{background:#fff0d9;color:#704a12}
.category-potentials{background:#eee;color:#555}.score-green{background:#d9efdc;color:#205b2a}
.score-yellow{background:#fff1bd;color:#6b5200}.score-orange{background:#ffe0c2;color:#7a3f00}
.score-red{background:#f5d6d6;color:#7b2222}.score-badge{display:inline-block;border-radius:4px;padding:2px 6px;font-size:.82em;font-weight:600}
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
.person-group{margin:20px 0;padding:14px;background:#f0ede6;border-radius:8px;width:100%;box-sizing:border-box}
.person-head{display:flex;gap:14px;align-items:flex-start;flex-wrap:wrap;margin-bottom:12px}
.person-head h2{font-size:1.15em;margin:4px 0;min-width:190px}
.reference{max-width:190px}.reference img{aspect-ratio:4/5;object-fit:cover}
.reference .detail{font-size:.82em}
.identity-rankings{font-size:.88em;margin:0 0 12px;overflow-wrap:anywhere}
.identity-rankings summary{cursor:pointer;color:#28527a}
.policy-panel{margin:10px 0;padding:8px 10px;background:#fff;border:1px solid #ded8ce;border-radius:6px;font-size:.84em}
.policy-panel summary{cursor:pointer;font-weight:600;color:#34495e}
.policy-panel pre{white-space:pre-wrap;overflow-wrap:anywhere;max-height:520px;overflow:auto;background:#f5f3ee;padding:10px;border-radius:4px;font-size:.9em}
@media(max-width:1050px){.controls{grid-template-columns:minmax(0,1fr)}.sort-controls{justify-content:flex-start}}
@media(max-width:760px){body{margin:12px}.page-header{display:block}.header-side{text-align:left;margin-top:12px}.score-legend{justify-content:flex-start}}
"""

SCRIPT = """
const records=JSON.parse(document.getElementById("review-data").textContent);
const peopleData=JSON.parse(document.getElementById("people-data").textContent);
const group=document.getElementById("group"), bucket=document.getElementById("bucket");
const state=document.getElementById("state"), sort=document.getElementById("sort");
const mode=document.getElementById("mode"), person=document.getElementById("person");
const scoreCeiling=document.getElementById("score-ceiling");
const cardSize=document.getElementById("card-size");
const framing=document.getElementById("framing");
const query=document.getElementById("query"), grid=document.getElementById("grid");
const count=document.getElementById("count"), more=document.getElementById("more");
const stagedCount=document.getElementById("staged-count"), download=document.getElementById("download");
const pageSize=100; let visible=[], shown=pageSize;
const staged=new Map();
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
  const link=document.createElement("a"); link.href=r.href; link.target="_blank"; link.rel="noopener noreferrer";
  const image=document.createElement("img");
  image.src=framing.value==="head"?r.thumbnailHead:r.thumbnail;
  image.dataset.chest=r.thumbnail; image.dataset.head=r.thumbnailHead; image.alt=r.name;
  image.title=r.name; image.loading="lazy"; image.decoding="async";
  link.append(image); article.append(link);
  const name=document.createElement("div"); name.className="name";
  name.textContent=readOnly?r.name:r.folder.split("/").slice(1).join("/");
  article.append(name);
  if(!readOnly) {
    const id=document.createElement("div"); id.className="detail photo-id";
    const photoId=r.photoId?r.photoId.replace(/^photo:/,"").replace(/^image_/,""):"unavailable";
    id.textContent="Photo ID: "+photoId+
      " · Identity ID: "+(r.personId||"not assigned");
    id.title="Photo ID comes from the filename; Identity ID belongs to the person";
    article.append(id);
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
      r.scoreContext.coreMode==="provisional"?"provisional":"no usable core";
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
  if(r.best_other) {
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
  action.value=staged.get(r.photoId)||"";
  action.addEventListener("change",()=>{
    if(action.value)staged.set(r.photoId,action.value); else staged.delete(r.photoId);
    updateStagedCount();
  });
  stageLabel.append(action); article.append(stageLabel);
  return article;
}
function updateStagedCount(){
  stagedCount.textContent=staged.size+" action(s) staged";
  download.disabled=staged.size===0;
}
function matchesMode(r) {
  if(mode.value==="review")return r.bucket==="Review";
  if(mode.value==="low")return r.bucket==="Gallery"&&r.score!==null&&r.score<Number(scoreCeiling.value);
  return true;
}
function primaryFor(folder) {
  return records.find(r=>r.folder===folder&&r.primaryReference)||null;
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
    const title=document.createElement("h2"); title.textContent=folder+" · "+photos.length+" shown"; header.append(title);
    const info=peopleData[folder]||{};
    header.append(categoryBadge(info.group||folder.split("/")[0]));
    if(info.identityProtected) {
      const protectedBadge=document.createElement("span");
      protectedBadge.className="badge badge-protected-identity";
      protectedBadge.textContent="Protected identity";
      protectedBadge.title="Automatic moves into or out of this identity are blocked";
      header.append(protectedBadge);
    }
    const reference=primaryFor(folder);
    if(reference) {
      if(!photos.some(item=>item.photoId===reference.photoId))header.append(card(reference,true));
    } else {
      const note=document.createElement("span"); note.className="detail"; note.textContent="No scored Gallery reference is available for this person.";
      header.append(note);
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
      details.append(list); section.append(details);
      const closestByCategory=new Map();
      for(const match of rankings)if(!closestByCategory.has(match.category))closestByCategory.set(match.category,match);
      const closest=document.createElement("div"); closest.className="detail";
      closest.textContent="Closest by category: ";
      for(const match of closestByCategory.values()) {
        closest.append(personReviewLink(match.key,match.category+": "+match.name));
        const mark=scoreBadge(match.score); if(mark)closest.append(document.createTextNode(" "),mark);
        closest.append(document.createElement("br"));
      }
      section.insertBefore(closest,details);
    } else {
      const note=document.createElement("div"); note.className="identity-rankings detail";
      note.textContent="No other scored identity is available for cross-reference.";
      section.append(note);
    }
    const photoGrid=document.createElement("div"); photoGrid.className="photo-grid";
    photoGrid.append(...photos.map(item=>card(item)));
    section.append(photoGrid); nodes.push(section);
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
    const photoGrid=document.createElement("div"); photoGrid.className="photo-grid";
    photoGrid.append(...page.map(item=>card(item)));
    grid.replaceChildren(photoGrid);
  } else {
    grid.replaceChildren(...groupCards(page));
  }
  const people=new Set(visible.map(item=>item.folder)).size;
  count.textContent="Showing "+Math.min(shown,visible.length)+" of "+visible.length+
    " photos"+(mode.value==="all"?"":" across "+people+" people");
  more.hidden=shown>=visible.length;
  more.textContent="Show next "+pageSize;
}
for(const control of [bucket,state,sort,person,scoreCeiling])control.addEventListener("change",render);
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
  const actions=[...staged.entries()].map(([photoId,type])=>{
    const record=records.find(item=>item.photoId===photoId);
    return {
      type, photoId, contentSha256:record.contentSha256, sourceBucket:record.bucket,
      personFolder:record.folder, ...(record.personId?{personId:record.personId}:{})
    };
  });
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
                   workflow_photo=False):
    """Return actions valid for this photo's current location and metadata."""
    if not stageable or not photo_id:
        return []
    options = [
        ("photo-unprotected" if protected else "photo-protected",
         "Remove protection" if protected else "Protect photo"),
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
    return options


def action_folder_supported(folder):
    """Whether a folder can be represented by the current identity catalogue schema."""
    return folder.split("/", 1)[0] in ACTION_ROOTS


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
    policy = policy or default_policy()
    category_order = tuple(policy["categoryOrder"])
    groups = set(
        category_order
        if include_artists
        else (category for category in category_order if category != "Artists")
    )
    group_order = {group: index for index, group in enumerate(category_order)}
    folders = [
        (key, folder) for key, folder in likeness.library_people(cfg, st, work)
        if likeness.status_of(key) in groups
    ]
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
        for path in originals.images(folder / "gallery"):
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
            protected_ids=protected_ids,
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
        identity_protected = bool(person and person.get("protected"))
        person_id = records[0][0] if len(records) == 1 else None
        anchors = set(person["identityAnchors"]) if person else set()
        category_policy = policy["categoryPolicies"].get(likeness.status_of(key), {})
        usable = [photo for photo in gallery if photo.usable(st["minFace"])]
        photo_ids = [metadata.photo_id_from_name(photo.name) for photo in usable]
        result = audit_person(
            [photo.vec for photo in usable],
            photo_ids,
            anchor_ids=anchors if not conflict else (),
            protected_ids=protected_ids,
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

        def best_other(photo):
            if not photo.usable(st["minFace"]):
                return ""
            ranking = sorted(
                (
                    (float(photo.vec @ vector), candidate)
                    for candidate, vector in policy_centroids.items()
                    if candidate != key and not likeness.apart(key, candidate)
                ),
                key=lambda row: (-row[0], row[1].casefold()),
            )
            other = ranking[0] if ranking else None
            return f"{other[1]} ({other[0]:.2f})" if other else ""

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
            match = best_other(photo) if (
                score is not None and (
                    score < keep or likeness.status_of(key) == "Potentials"
                )
            ) else ""
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
                "personId": person_id,
                "identityProtected": identity_protected,
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
                    "Gallery", photo_id, anchor=photo_id in anchors and photo_id not in stale_ids,
                    protected=photo_id in protected_ids,
                    workflow_photo=workflow_photo_available,
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
                state, reason = "Review", "Candidate is outside the active gallery and never enters its core"
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
                "personId": person_id,
                "identityProtected": identity_protected,
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
                    "Review", photo_id, protected=photo_id in protected_ids,
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
                "best_other": best_other(photo),
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


def write_thumbnails(items, out):
    """Write/reuse named, content-keyed head and chest-up derivatives."""
    from PIL import Image

    thumb_dir = out / "people_gallery_review_files"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    public_items = []

    def thumbnail_bytes(photo, framing):
        size = (320, 400)
        with Image.open(photo.path) as source:
            crop = crop_thumbnail(source, photo.box, framing, size)
        output = io.BytesIO()
        crop.save(output, "JPEG", quality=84)
        return output.getvalue()

    for item in items:
        photo = item["_photo"]
        stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", photo.path.stem).strip("._") or "photo"
        targets = {}
        for framing in ("chest", "head"):
            target = thumb_dir / f"{stem}_{framing}_{photo.sha[:12]}.jpg"
            if not target.exists():
                data = thumbnail_bytes(photo, framing)
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
        face_target = None
        if photo.box:
            target = thumb_dir / f"{stem}_face_{photo.sha[:12]}.jpg"
            if not target.exists():
                with Image.open(photo.path) as source:
                    crop = face_thumbnail(source, photo.box)
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(
                        mode="wb",
                        prefix=f".{stem}_face_",
                        suffix=".tmp",
                        dir=thumb_dir,
                        delete=False,
                    ) as output:
                        temporary = pathlib.Path(output.name)
                        crop.save(output, "JPEG", quality=84)
                        output.flush()
                        os.fsync(output.fileno())
                    os.replace(temporary, target)
                finally:
                    if temporary is not None and temporary.exists():
                        temporary.unlink()
            targets["face"] = (pathlib.Path(thumb_dir.name) / target.name).as_posix()
        public = {key: value for key, value in item.items() if key != "_photo"}
        public["thumbnail"] = targets["chest"]
        public["thumbnailHead"] = targets["head"]
        if "face" in targets:
            public["thumbnailFace"] = targets["face"]
        public["href"] = photo.path.resolve().as_uri()
        public_items.append(public)
    return public_items, thumb_dir


def render_html(items, stamp, warnings=(), policy=None):
    """Render a local page with client-side filters and bounded card rendering."""
    policy = policy or default_policy()
    people_count = len({item["folder"] for item in items})
    people_label = "person" if people_count == 1 else "people"
    photos_label = "photo" if len(items) == 1 else "photos"
    people_data = {}
    for item in items:
        people_data.setdefault(item["folder"], {
            "group": item.get("group"),
            "identityMatches": item.get("identityMatches", []),
            "identityProtected": item.get("identityProtected", False),
        })
    public_items = [
        {key: value for key, value in item.items() if key != "identityMatches"}
        for item in items
    ]
    payload = json.dumps(public_items, ensure_ascii=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    people_payload = json.dumps(people_data, ensure_ascii=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    policy_payload = json.dumps(policy, ensure_ascii=True).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    warning_html = ""
    if warnings:
        entries = "".join(f"<li>{html.escape(message)}</li>" for message in warnings)
        warning_html = f'<ul class="warnings">{entries}</ul>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>People gallery review</title><style>{CSS}</style></head><body>
<header class="page-header"><div><h1>People gallery review</h1>
<p class="note">Generated {stamp} · {people_count} {people_label} · {len(items)} {photos_label}</p>
<p class="note">Stage actions here, then download the manifest to review and apply separately.</p></div>
<div class="header-side"><div class="header-label">Likeness</div>
<div class="score-legend">{render_score_legend(policy)}</div></div></header>
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
<script id="review-data" type="application/json">{payload}</script>
<script id="people-data" type="application/json">{people_payload}</script>
<script id="category-order" type="application/json">{json.dumps(policy["categoryOrder"])}</script>
<script>{SCRIPT}</script>
</body></html>
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artists", action="store_true", help="include people grouped inside artists' folders")
    parser.add_argument("--keep", type=float, default=0.25, help="Prospect borderline score (default: 0.25)")
    parser.add_argument("--out", help="report directory (default: <work>\\_reports\\library)")
    parser.add_argument("--root", help="photo library folder (default: workspaces.json paths.workRoot)")
    parser.add_argument("--cache", help="embedding cache file (default: the user-local likeness cache)")
    parser.add_argument("--policy", help="versioned likeness policy JSON")
    parser.add_argument(
        "--no-renders",
        action="store_true",
        help="accepted by the shared gallery launcher; this page does not load ComfyUI renders",
    )
    args = parser.parse_args(argv)
    policy = load_policy(args.policy)
    cfg, st, work, cache, space = likeness.build(
        types.SimpleNamespace(root=args.root, cache=args.cache, embedder=None)
    )
    catalog = metadata.load_catalog()
    items, warnings = collect_items(
        cfg, st, work, cache, space, catalog,
        include_artists=args.artists, keep=args.keep, policy=policy
    )
    out = pathlib.Path(args.out) if args.out else pathlib.Path(work) / "_reports" / "library"
    out.mkdir(parents=True, exist_ok=True)
    public_items, thumb_dir = write_thumbnails(items, out)
    report = out / "people_gallery_review.html"
    report.write_text(
        render_html(
            public_items,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            warnings,
            policy=policy,
        ),
        encoding="utf-8",
    )
    print(f"people gallery review: {len(public_items)} photo(s)")
    print(f"  {report}")
    print(f"  {thumb_dir} ({len(list(thumb_dir.glob('*.jpg')))} cached thumbnails)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
