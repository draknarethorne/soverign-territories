#!/usr/bin/env python3
"""Preview, verify or publish read-only Artist pages; never run matching or intake."""
import argparse
import hashlib
import html
import io
import json
import pathlib
import re
import sys
from urllib.parse import urlencode

from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import likeness  # noqa: E402
import originals  # noqa: E402
import temporary_storage  # noqa: E402
from likeness_library import domains, gallery_chrome, metadata, preparation_provenance, report_assets  # noqa: E402
from likeness_library.sandbox import is_sandbox_working_path, require_sandbox_cache  # noqa: E402

RECIPE = "artists-gallery-v1"
MANIFEST = "gallery-manifest.json"
SIZE = (240, 300)
CSS = """
h2{margin:8px 0;font-size:1.1rem}p{line-height:1.5}
.note,.detail{color:var(--st-muted)}.controls{display:flex;gap:14px;flex-wrap:wrap;align-items:end;margin:14px 0;padding:14px 16px;background:var(--st-card);border:1px solid var(--st-line);border-radius:var(--st-radius);box-shadow:var(--st-shadow)}
label{display:grid;gap:5px}input{max-width:100%}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}
article{background:var(--st-card);padding:14px;border:1px solid var(--st-line);border-radius:9px;min-width:0;overflow-wrap:anywhere;box-shadow:var(--st-shadow)}
article img{width:100%;height:280px;object-fit:contain;background:#e7e5df;border-radius:5px}
article.review{border-left:5px solid #b47d25}
.warning{background:#fff0d5;padding:8px;border-radius:5px}.detail{font-size:.85rem;overflow-wrap:anywhere}
.preparation-evidence{font-size:.82rem;margin-top:8px;overflow-wrap:anywhere}.preparation-evidence summary{cursor:pointer;color:#34495e}.preparation-evidence ul{padding-left:20px}
#more{display:block;margin:20px auto}#more[hidden]{display:none}.empty{padding:20px}
@media(max-width:600px){.grid{grid-template-columns:repeat(auto-fill,minmax(200px,1fr))}}
"""
SCRIPT = preparation_provenance.EVIDENCE_SCRIPT + """
const records=JSON.parse(document.getElementById('artist-data').textContent);
const q=document.getElementById('query'),artist=document.getElementById('artist'),folder=document.getElementById('folder'),bucket=document.getElementById('bucket');
const grid=document.getElementById('grid'),count=document.getElementById('count'),more=document.getElementById('more');
const detail=document.body.dataset.view==='detail';let limit=60;
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function options(select,values){for(const value of [...new Set(values)].sort())select.add(new Option(value,value));}
options(artist,records.map(r=>r.artist));options(folder,records.map(r=>r.folder));
const params=new URLSearchParams(location.search);
for(const [key,input] of [['artist',artist],['folder',folder],['bucket',bucket]])if([...input.options].some(o=>o.value===params.get(key)))input.value=params.get(key);
function link(label,href){const a=el('a',label);a.href=href;return a;}
function render(){
 const text=q.value.toLocaleLowerCase();
 const rows=records.filter(r=>(!artist.value||r.artist===artist.value)&&(!folder.value||r.folder===folder.value)&&(!bucket.value||(detail?r.bucket===bucket.value:(bucket.value==='Gallery'?r.gallery:r.review)>0))&&(!text||[r.artist,r.folder,r.name].join(' ').toLocaleLowerCase().includes(text)));
 grid.replaceChildren();count.textContent=rows.length+(detail?' photos':' groups')+' · showing '+Math.min(limit,rows.length);more.hidden=rows.length<=limit;
 for(const r of rows.slice(0,limit)){
  const card=el('article',undefined,r.bucket==='Review'?'review':'');
  if(r.thumbnail){const image=el('img');image.src=r.thumbnail;image.loading='lazy';image.width=240;image.height=300;image.alt=detail?r.name:r.folder;
   const a=link('',detail?r.source:r.detail);a.append(image);card.append(a);}
  card.append(el('div',r.artist,'eyebrow'),el('h2',r.label),el('span',r.bucket||'Artist group','badge'));
  if(detail){
   card.append(el('p',r.name,'detail'),el('p','Face cache: '+r.face,'detail'),link('Open current original',r.source));
   appendPreparationEvidence(card,r.preparationEvidence);
   if(r.warning)card.append(el('p',r.warning,'warning'));
  }else{card.append(el('p',r.gallery+' Gallery · '+r.review+' Review','detail'),el('p',r.preparationSummary||'Preparation: not indexed','detail'),link('Browse all photos',r.detail));}
  grid.append(card);
 }
 if(!rows.length)grid.append(el('p','No Artist photos match these filters.','empty'));
}
for(const input of [q,artist,folder,bucket])input.addEventListener('input',()=>{limit=60;render();});
more.addEventListener('click',()=>{limit+=60;render();});render();
"""


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def safe_path(root, path):
    path = pathlib.Path(path)
    if root not in path.resolve().parents:
        raise ValueError(f"Artist report path escapes library: {path}")
    for item in (path, *path.parents):
        if item.is_symlink() or (hasattr(item, "is_junction") and item.is_junction()):
            raise ValueError(f"linked Artist report path refused: {item}")
        if item == root:
            break
    return path


def inventory(root):
    base = root / "Artists"
    if not base.is_dir():
        raise ValueError(f"Artist root does not exist: {base}")
    safe_path(root, base)
    result = []
    for artist in sorted(base.iterdir()):
        if not artist.is_dir() or artist.name.startswith("_"):
            continue
        safe_path(root, artist)
        folders = [artist] + sorted(
            child for child in artist.iterdir()
            if child.is_dir() and not child.name.startswith("_")
            and child.name not in {"gallery", "review"}
            and not any(child.name.startswith(prefix) for prefix in ("gallery_", "headshot_", "chest_"))
        )
        for folder in folders:
            safe_path(root, folder)
            for bucket in ("gallery", "review"):
                location = folder / bucket
                safe_path(root, location)
                for source in originals.images(location):
                    safe_path(root, source)
                    result.append((artist.name, folder, bucket.title(), source))
    return result


def page(records, *, detail, stats, section_links=None):
    title = "Artist photo review" if detail else "Artists gallery"
    current = "Photo review" if detail else "Overview"
    links = [("Overview", "artists_gallery.html"), ("Photo review", "artists_gallery_review.html"),
             ("Intake runs", "intake_runs.html")]
    payload = json.dumps(records, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{gallery_chrome.CSS}{CSS}</style></head>
<body id="top" data-view="{'detail' if detail else 'overview'}">
{gallery_chrome.masthead(
    "Artists", "../", "Artist library", section_links=section_links
)}
<div class="site-page">
<header class="page-header"><div><div class="eyebrow">Artist library · separate from People</div><h1>{title}</h1>
<p>Browse Artist-local folders and originals. No people relationships, matching, staged actions or source changes.</p>
<p class="note">{html.escape(stats)} · One shared 240x300 thumbnail per distinct image. Full originals open only on request.</p></div></header>
{gallery_chrome.navigation(links, current)}
<main><div class="controls">
<label>Search <input id="query" type="search" placeholder="artist, group, filename"></label>
<label>Artist <select id="artist"><option value="">All artists</option></select></label>
<label>Group <select id="folder"><option value="">All groups</option></select></label>
<label>Location <select id="bucket"><option value="">Gallery and Review</option><option>Gallery</option><option>Review</option></select></label>
<span id="count" role="status"></span></div>
<noscript>Enable JavaScript for local filtering and navigation. No network service is used.</noscript>
<div class="grid" id="grid"></div><button id="more" type="button">Show next 60</button></main>
{gallery_chrome.footer('Read-only prototype · Layout for review, not adopted people-page rules')}
<script id="artist-data" type="application/json">{payload}</script><script>{SCRIPT}</script>
</div></body></html>
""".encode("utf-8")


def prepare(root, sources, cache, provenance):
    assets, records, inputs, diagnostics = {}, [], {}, []
    section_links = gallery_chrome.configured_sections(
        root, getattr(provenance, "cfg", None)
    )
    for artist, folder, bucket, source in sources:
        payload = source.read_bytes()
        sha = digest(payload)
        inputs[source.relative_to(root).as_posix()] = sha
        thumbnail = f"thumbnails/{sha}.jpg"
        warning = ""
        if thumbnail not in assets:
            try:
                with Image.open(io.BytesIO(payload)) as image:
                    image = ImageOps.exif_transpose(image).convert("RGB")
                    image = ImageOps.pad(image, SIZE, color=originals.STUDIO_GREY, method=Image.Resampling.LANCZOS)
                    output = io.BytesIO()
                    image.save(output, "JPEG", quality=80, optimize=True)
                assets[thumbnail] = output.getvalue()
            except (OSError, ValueError, Image.DecompressionBombError) as exc:
                warning = f"Thumbnail unavailable: {exc}"
                diagnostics.append(f"{source.relative_to(root)}: {warning}")
                thumbnail = None
        entry = cache.get("emb", {}).get(hashlib.sha1(payload).hexdigest(), {})
        face = "unassessed (no cached face result)"
        if entry:
            face = f"{entry.get('faces', 'unknown')} detected · {entry.get('px', 0):.0f}px"
        key = folder.relative_to(root).as_posix()
        records.append({
            "artist": artist, "folder": key, "label": folder.name, "bucket": bucket,
            "name": source.name, "source": source.as_uri(), "thumbnail": thumbnail,
            "face": face, "warning": warning,
            "preparationEvidence": provenance.evidence(source, metadata.photo_id_from_name(source.name)),
        })
    groups = []
    for key in sorted({record["folder"] for record in records}):
        members = [record for record in records if record["folder"] == key]
        first = next((record for record in members if record["thumbnail"]), members[0])
        groups.append({
            "artist": first["artist"], "folder": key, "label": first["label"],
            "bucket": "", "thumbnail": first["thumbnail"],
            "gallery": sum(record["bucket"] == "Gallery" for record in members),
            "review": sum(record["bucket"] == "Review" for record in members),
            "preparationSummary": "Preparation: " + " · ".join(
                f"{sum(record['preparationEvidence']['state'] == state for record in members)} {state}"
                for state in ("verified", "ambiguous", "stale", "unverified", "missing")
                if any(record["preparationEvidence"]["state"] == state for record in members)
            ),
            "detail": "artists_gallery_review.html?" + urlencode({"folder": key}),
        })
    thumb_bytes = sum(len(value) for value in assets.values())
    stats = f"{len(groups)} groups · {len(records)} photos · {len(assets)} thumbnails / {thumb_bytes / 1048576:.2f} MiB"
    assets["artists_gallery.html"] = page(
        groups, detail=False, stats=stats, section_links=section_links
    )
    assets["artists_gallery_review.html"] = page(
        records, detail=True, stats=stats, section_links=section_links
    )
    manifest = {
        "formatVersion": 1, "recipe": RECIPE, "inputs": inputs,
        "files": {name: digest(value) for name, value in sorted(assets.items())},
        "thumbnailBytes": thumb_bytes, "thumbnailCount": len(assets) - 2,
        "diagnostics": diagnostics,
    }
    return assets, manifest


def run(args):
    cfg = likeness.cw.load_cfg()
    root = pathlib.Path(args.root or likeness.cw.work_root(cfg)).expanduser().resolve(strict=True)
    reports_root = likeness.cw.storage_root(cfg, "reports", root=root)
    out = safe_path(root, reports_root / "artists")
    cache_path = (
        pathlib.Path(args.cache)
        if args.cache
        else likeness.cw.storage_root(cfg, "likeness", root=root) / "artists" / "cache.json"
    )
    if is_sandbox_working_path(root):
        require_sandbox_cache(root, cache_path)
    safe_path(root, cache_path)
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.is_file() else {}
    sources = inventory(root)
    print(f"Artist-only report: {len(sources)} source photos; output {out}")
    if not args.apply and not args.check:
        print("Preview only: no images decoded, no inference, no files written. Use --apply to publish pages.")
        return 0
    provenance = preparation_provenance.build_index(
        root,
        out,
        [(source, metadata.photo_id_from_name(source.name)) for _, _, _, source in sources],
        "artists",
    )
    assets, manifest = prepare(root, sources, cache, provenance)
    assets["intake_runs.html"] = provenance.history_html().encode("utf-8")
    manifest["files"]["intake_runs.html"] = digest(assets["intake_runs.html"])
    manifest_bytes = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    assets[MANIFEST] = manifest_bytes
    for name in assets:
        safe_path(root, out / name)
    stale = [name for name, value in assets.items()
             if not (out / name).is_file() or (out / name).read_bytes() != value]
    print(f"{manifest['thumbnailCount']} shared thumbnails / {manifest['thumbnailBytes']} bytes; "
          f"{sum(map(len, assets.values()))} total generated bytes; {len(stale)} pending files")
    for diagnostic in manifest["diagnostics"]:
        print("DIAGNOSTIC: " + diagnostic)
    if args.check:
        return int(bool(stale or manifest["diagnostics"]))
    out.mkdir(parents=True, exist_ok=True)
    gallery_chrome.publish_banner(safe_path(root, reports_root))
    previous_path = out / MANIFEST
    previous = json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.is_file() else {}
    for name in stale:
        target = out / name
        if target.exists() and name != MANIFEST and (
            previous.get("recipe") != RECIPE
            or previous.get("files", {}).get(name) != digest(target.read_bytes())
        ):
            raise ValueError(f"preserved edited/unowned report file; choose how to recover it before refresh: {target}")
    temporary_root = likeness.cw.storage_root(cfg, "temporary", root=root)
    with temporary_storage.staging_directory(temporary_root, ".artists-stage-") as stage:
        for name in stale:
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(assets[name])
        for name in stale:
            target = out / name
            target.parent.mkdir(parents=True, exist_ok=True)
            report_assets.replace_file(stage / name, target)
    if previous.get("recipe") == RECIPE:
        for name, expected in previous.get("files", {}).items():
            if name in assets or not re.fullmatch(r"thumbnails/[0-9a-f]{64}\.jpg", name):
                continue
            path = safe_path(root, out / name)
            if path.is_file() and digest(path.read_bytes()) == expected:
                path.unlink()
            elif path.exists():
                print(f"DIAGNOSTIC: preserved edited/unrecognized obsolete thumbnail: {path}")
    return int(bool(manifest["diagnostics"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="library root; only Artists is inventoried")
    parser.add_argument("--cache", help="existing Working-local face cache; read only, no model execution")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true", help="preview (default), without image decoding")
    modes.add_argument("--apply", action="store_true", help="publish generated pages/thumbnails only")
    modes.add_argument("--check", action="store_true", help="read-only exact report verification")
    args = parser.parse_args(argv)
    try:
        with domains.activate("artists", read_only=True):
            return run(args)
    except (OSError, ValueError, KeyError) as exc:
        print(f"Artist gallery refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
