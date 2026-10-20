#!/usr/bin/env python3
"""Build a local, read-only photo review page for person galleries and Review folders."""
import argparse
import collections
import datetime
import html
import json
import os
import pathlib
import sys
import tempfile
import types

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/art"))
import likeness  # noqa: E402
import originals  # noqa: E402
import people_gallery  # noqa: E402
from likeness_library import metadata  # noqa: E402
from likeness_library.audit import audit_person  # noqa: E402

PAGE_SIZE = 100
SECTIONS = ("Angels", "Sisters", "Prospects", "Potentials", "Artists")

CSS = """
body{font:15px Segoe UI,Arial,sans-serif;margin:20px;background:#faf8f3;color:#222}
h1{margin:0 0 4px}.note{color:#555;max-width:1100px}.warnings{color:#8a3b16}
.controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:16px 0}
.controls input,.controls select,.controls button{font:inherit;padding:7px}
.count{color:#555}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(235px,1fr));gap:12px}
article{background:white;border:1px solid #ded8ce;border-radius:6px;padding:8px;min-width:0}
article img{display:block;width:100%;aspect-ratio:188/220;object-fit:cover;background:#eee}
article a{color:#28527a}.name{font-weight:600;overflow-wrap:anywhere;margin:7px 0}
.badge{display:inline-block;border-radius:3px;background:#eee;padding:2px 5px;margin:0 4px 4px 0;font-size:.82em}
.detail{color:#555;font-size:.88em;margin:4px 0;overflow-wrap:anywhere}
#more{display:block;margin:18px auto;padding:8px 18px;font:inherit}
.stage{display:block;margin-top:8px;font-size:.9em}.stage select{display:block;width:100%;font:inherit;padding:5px}
.actions{display:flex;gap:10px;align-items:center;margin:14px 0}.actions button{font:inherit;padding:8px}
"""

SCRIPT = """
const records=JSON.parse(document.getElementById("review-data").textContent);
const group=document.getElementById("group"), bucket=document.getElementById("bucket");
const state=document.getElementById("state"), sort=document.getElementById("sort");
const query=document.getElementById("query"), grid=document.getElementById("grid");
const count=document.getElementById("count"), more=document.getElementById("more");
const stagedCount=document.getElementById("staged-count"), download=document.getElementById("download");
const pageSize=100; let visible=[], shown=pageSize;
const staged=new Map();
function fill(select, values, label) {
  select.replaceChildren(new Option("All "+label,""));
  [...new Set(values)].sort((a,b)=>a.localeCompare(b)).forEach(v=>select.add(new Option(v,v)));
}
fill(group,records.map(r=>r.group),"groups");
fill(bucket,records.map(r=>r.bucket),"locations");
fill(state,records.map(r=>r.state),"states");
function compare(a,b) {
  if(a.score===null&&b.score!==null)return 1;
  if(b.score===null&&a.score!==null)return -1;
  if(sort.value==="name")return (a.folder+" "+a.name).localeCompare(b.folder+" "+b.name);
  if(a.score===null)return 0;
  return sort.value==="high" ? b.score-a.score : a.score-b.score;
}
function card(r) {
  const article=document.createElement("article");
  const link=document.createElement("a"); link.href=r.href; link.target="_blank"; link.rel="noopener noreferrer";
  const image=document.createElement("img"); image.src=r.thumbnail; image.alt=r.name;
  image.title=r.name; image.loading="lazy"; image.decoding="async";
  link.append(image); article.append(link);
  const name=document.createElement("div"); name.className="name"; name.textContent=r.folder;
  article.append(name);
  for(const text of [r.group,r.bucket,r.state]) {
    const badge=document.createElement("span"); badge.className="badge"; badge.textContent=text; article.append(badge);
  }
  const details=[
    "Photo: "+r.name,
    "Core similarity: "+(r.score===null?"not scored":r.score.toFixed(2)),
    "Compared with: "+r.comparison,
    r.best_other ? "Closest other folder: "+r.best_other : "",
    r.reason,
    r.stageReason
  ];
  for(const text of details.filter(Boolean)) {
    const detail=document.createElement("div"); detail.className="detail"; detail.textContent=text; article.append(detail);
  }
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
function render() {
  const q=query.value.trim().toLocaleLowerCase();
  visible=records.filter(r=>
    (!group.value||r.group===group.value) &&
    (!bucket.value||r.bucket===bucket.value) &&
    (!state.value||r.state===state.value) &&
    (!q||(r.folder+" "+r.name+" "+r.reason).toLocaleLowerCase().includes(q))
  ).sort(compare);
  shown=pageSize; draw();
}
function draw() {
  grid.replaceChildren(...visible.slice(0,shown).map(card));
  count.textContent="Showing "+Math.min(shown,visible.length)+" of "+visible.length+" photos";
  more.hidden=shown>=visible.length;
  more.textContent="Show next "+pageSize;
}
for(const control of [group,bucket,state,sort])control.addEventListener("change",render);
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


def action_options(bucket, photo_id, *, anchor=False, protected=False, stageable=True):
    """Return actions valid for this photo's current location and metadata."""
    if not stageable or not photo_id:
        return []
    options = [
        ("photo-unprotected" if protected else "photo-protected",
         "Remove protection" if protected else "Protect photo"),
    ]
    if bucket == "Gallery":
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


def collect_items(cfg, st, work, cache, space, catalog, *, include_artists=False, embed=None, keep=0.25):
    """Build scored image records; Review candidates never enter an identity core."""
    groups = set(SECTIONS if include_artists else SECTIONS[:-1])
    folders = [
        (key, folder) for key, folder in likeness.library_people(cfg, st, work)
        if likeness.status_of(key) in groups
    ]
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

    all_photos = list(space.photos)
    all_photos.extend(photo for records in review_by_key.values() for photo, _ in records)
    id_counts = collections.Counter(
        photo_id for photo_id in (metadata.photo_id_from_name(p.name) for p in all_photos) if photo_id
    )
    ambiguous_ids = {photo_id for photo_id, count in id_counts.items() if count > 1}
    protected_ids, stale_ids = set(), set()
    for photo in all_photos:
        photo_id = metadata.photo_id_from_name(photo.name)
        if not photo_id or photo_id not in catalog["photos"] or photo_id in ambiguous_ids:
            continue
        record = catalog["photos"][photo_id]
        if metadata.content_sha256(photo.path) != record["contentSha256"]:
            stale_ids.add(photo_id)
        elif record["protected"]:
            protected_ids.add(photo_id)

    people_by_folder = collections.defaultdict(list)
    for person_id, person in catalog["people"].items():
        people_by_folder[person["folder"]].append((person_id, person))

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
        person_id = records[0][0] if len(records) == 1 else None
        anchors = set(person["identityAnchors"]) if person else set()
        usable = [photo for photo in gallery if photo.usable(st["minFace"])]
        photo_ids = [metadata.photo_id_from_name(photo.name) for photo in usable]
        result = audit_person(
            [photo.vec for photo in usable],
            photo_ids,
            anchor_ids=anchors if not conflict else (),
            protected_ids=protected_ids,
            stale_ids=stale_ids,
            ambiguous_ids=ambiguous_ids,
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
            ranking = space.ranking(photo.vec, own=key, skip=photo if photo in space.photos else None, source=key)
            other = next(((score, name) for score, name in ranking if name != key), None)
            return f"{other[1]} ({other[0]:.2f})" if other else ""

        for photo in gallery:
            photo_id = metadata.photo_id_from_name(photo.name)
            index = indices.get(id(photo))
            score = scores.get(id(photo))
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
            elif not result["sufficient"]:
                state, reason = "Small core", "Score only; too few core photos for an outlier suggestion"
            elif key.startswith("Prospects/") and score < st["odd"]:
                state, reason = "Possible outlier", "Low similarity to the current core; report only"
            elif key.startswith("Prospects/") and score < keep:
                state, reason = "Borderline", "Review suggested; no move is proposed"
            elif index in core:
                state, reason = "Core member", "Included in the trusted-seeded or provisional core"
            elif score is not None and score < st["odd"]:
                state, reason = "Low similarity", "Inspect only; no automatic move"
            else:
                state, reason = "Consistent", "Similarity is measured against the current person core"
            match = best_other(photo) if score is not None and score < keep else ""
            items.append({
                "folder": key,
                "group": likeness.status_of(key),
                "bucket": "Gallery",
                "name": photo.name,
                "photoId": photo_id,
                "contentSha256": photo.sha,
                "personId": person_id,
                "stageable": bool(
                    photo_id and photo_id not in ambiguous_ids and not conflict
                    and not key.startswith("Artists/")
                ),
                "stageOptions": action_options(
                    "Gallery", photo_id, anchor=photo_id in anchors and photo_id not in stale_ids,
                    protected=photo_id in protected_ids,
                    stageable=(
                        photo_id not in ambiguous_ids and not conflict
                        and not key.startswith("Artists/")
                    ),
                ),
                "stageReason": (
                    "Actions are disabled for artist galleries because the identity catalogue does not yet model them"
                    if key.startswith("Artists/") else
                    "Actions require a unique stable photo ID and an unambiguous person folder"
                    if not photo_id or photo_id in ambiguous_ids or conflict else ""
                ),
                "score": score,
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
            items.append({
                "folder": key,
                "group": likeness.status_of(key),
                "bucket": "Review",
                "name": photo.name,
                "photoId": photo_id,
                "contentSha256": photo.sha,
                "personId": person_id,
                "stageable": bool(
                    photo_id and photo_id not in ambiguous_ids and not conflict
                    and not key.startswith("Artists/")
                ),
                "stageOptions": action_options(
                    "Review", photo_id, protected=photo_id in protected_ids,
                    stageable=(
                        photo_id not in ambiguous_ids and not conflict
                        and not key.startswith("Artists/")
                    ),
                ),
                "stageReason": (
                    "Actions are disabled for artist galleries because the identity catalogue does not yet model them"
                    if key.startswith("Artists/") else
                    "Actions require a unique stable photo ID and an unambiguous person folder"
                    if not photo_id or photo_id in ambiguous_ids or conflict else ""
                ),
                "score": score,
                "state": state,
                "comparison": comparison,
                "reason": reason,
                "best_other": best_other(photo),
                "_photo": photo,
            })

    items.sort(key=lambda item: (
        item["score"] is None,
        item["score"] if item["score"] is not None else 0,
        item["folder"].casefold(),
        item["name"].casefold(),
    ))
    return items, warnings


def write_thumbnails(items, out):
    """Write/reuse content-keyed local thumbnails beside the HTML report."""
    thumb_dir = out / "people_gallery_review_files"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    public_items = []
    for item in items:
        photo = item["_photo"]
        target = thumb_dir / f"{photo.sha}.jpg"
        if not target.exists():
            data = people_gallery.thumb_bytes(photo.path)
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    prefix=f".{photo.sha}.",
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
        public = {key: value for key, value in item.items() if key != "_photo"}
        public["thumbnail"] = (pathlib.Path(thumb_dir.name) / target.name).as_posix()
        public["href"] = photo.path.resolve().as_uri()
        public_items.append(public)
    return public_items, thumb_dir


def render_html(items, stamp, warnings=()):
    """Render a local page with client-side filters and bounded card rendering."""
    payload = json.dumps(items, ensure_ascii=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    warning_html = ""
    if warnings:
        entries = "".join(f"<li>{html.escape(message)}</li>" for message in warnings)
        warning_html = f'<ul class="warnings">{entries}</ul>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>People gallery review</title><style>{CSS}</style></head><body>
<h1>People gallery review</h1>
<p class="note">Generated {stamp} with {len(items)} indexed photos. This local page only stages decisions into a versioned JSON download; it never changes source photos or catalogue data. Photos are sorted by similarity to the active person core (lowest first). Similarity is evidence, not certainty; outlier labels are suggestions only. Review photos are compared with their source core but excluded from it.</p>
{warning_html}
<div class="controls">
<label>Search <input id="query" type="search" placeholder="folder, filename, reason"></label>
<label>Group <select id="group"></select></label>
<label>Location <select id="bucket"></select></label>
<label>State <select id="state"></select></label>
<label>Order <select id="sort"><option value="low">Lowest score first</option><option value="high">Highest score first</option><option value="name">Name</option></select></label>
<span class="count" id="count"></span>
</div>
<div class="actions"><button id="download" type="button" disabled>Download staged actions</button><span id="staged-count">0 actions staged</span></div>
<div class="grid" id="grid"></div><button id="more" type="button">Show next {PAGE_SIZE}</button>
<script id="review-data" type="application/json">{payload}</script>
<script>{SCRIPT}</script>
</body></html>
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artists", action="store_true", help="include people grouped inside artists' folders")
    parser.add_argument("--keep", type=float, default=0.25, help="Prospect borderline score (default: 0.25)")
    parser.add_argument("--out", help="report directory (default: <work>\\_reports\\library)")
    parser.add_argument("--root", help="photo library folder (default: workspaces.json paths.workRoot)")
    args = parser.parse_args(argv)
    cfg, st, work, cache, space = likeness.build(
        types.SimpleNamespace(root=args.root, cache=None, embedder=None)
    )
    catalog = metadata.load_catalog()
    items, warnings = collect_items(
        cfg, st, work, cache, space, catalog, include_artists=args.artists, keep=args.keep
    )
    out = pathlib.Path(args.out) if args.out else pathlib.Path(work) / "_reports" / "library"
    out.mkdir(parents=True, exist_ok=True)
    public_items, thumb_dir = write_thumbnails(items, out)
    report = out / "people_gallery_review.html"
    report.write_text(
        render_html(public_items, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), warnings),
        encoding="utf-8",
    )
    print(f"people gallery review: {len(public_items)} photo(s)")
    print(f"  {report}")
    print(f"  {thumb_dir} ({len(list(thumb_dir.glob('*.jpg')))} cached thumbnails)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
