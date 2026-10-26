"""Browse every ComfyUI output and pull explicitly chosen renders back into the library.

`outputs` writes a static page (`_generation/outputs.html`) listing images under the
ComfyUI output root, with filters, paging, a full-size viewer and a pull manifest
export. Nothing is copied or thumbnailed. `pull` copies only the manifest's files into
`_generation/library/<stage>/<variant>/` with the standard `<name>_comfy_<variant>_<id>`
name, a cream-padded 944x1104 copy and a lineage sidecar; they are synthetic and never
identity evidence.
"""
import datetime
import hashlib
import html
import io
import json
import os
import pathlib
import re
import sys

from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "art"))
from likeness_library import gallery_chrome, report_assets  # noqa: E402

if __package__:
    from . import reference_rendering as base
else:
    import reference_rendering as base

WORKSPACES = ROOT / "workflows" / "workspaces.json"
PAGE_RELATIVE = "_generation/outputs.html"
LIBRARY_RELATIVE = "_generation/library"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
STANDARD_SIZE = (944, 1104)
CREAM = (245, 240, 230)
STAGE = re.compile(r"^(?:\d[a-z]?_[A-Za-z][A-Za-z0-9_-]*|Bench|Hero)$")
FOLDER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
MAX_PULL = 64
PAGE_SIZES = (60, 120, 240)


def configured_output_root():
    return pathlib.Path(base.read_json(WORKSPACES)["paths"]["outputRoot"])


def output_root(value=None):
    path = pathlib.Path(value) if value else configured_output_root()
    if not path.is_absolute() or not path.is_dir():
        raise ValueError(f"ComfyUI output root must be an existing absolute directory: {path}")
    return path.resolve()


def parse(relative):
    """Read workspace, stage, variant, subject and batch/job from a ComfyUI output path."""
    parts = relative.split("/")
    folders, filename = parts[:-1], parts[-1]
    info = {"workspace": parts[0] if len(parts) > 1 else "", "stage": "", "variant": "",
            "subject": "", "batch": "", "job": ""}
    inner = folders[1:]
    for index, part in enumerate(inner):
        if STAGE.fullmatch(part):
            info["stage"] = part
            if index + 1 < len(inner):
                info["variant"] = inner[index + 1]
            break
    if len(inner) >= 4 and inner[0] == "reference" and inner[1] != "manual":
        info.update(subject=inner[1], batch=inner[2], job=inner[3])
    elif not info["stage"] and len(inner) >= 3:
        # Legacy pre-stage layout: <set>/<Name>/<category>/..., e.g. drakn-sisters/Draknara/poses.
        info.update(subject=inner[1], variant=inner[2])
    else:
        for marker in ("shots", "manual"):
            if marker in inner and inner.index(marker) + 1 < len(inner):
                candidate = inner[inner.index(marker) + 1]
                if not STAGE.fullmatch(candidate):
                    info["subject"] = candidate
                break
    if not info["subject"]:
        info["subject"] = re.split(r"[_\s-]", filename, maxsplit=1)[0]
    return info


def scan(root, workspaces=None):
    """Every image below the output root, newest first; workspaces limit the top folders."""
    items = []
    wanted = {name.casefold() for name in workspaces or ()}
    for top in sorted(root.iterdir(), key=lambda item: item.name.casefold()):
        if not top.is_dir() or top.is_symlink() or (wanted and top.name.casefold() not in wanted):
            continue
        for directory, subdirectories, files in os.walk(top):
            subdirectories[:] = sorted(name for name in subdirectories
                                       if not (pathlib.Path(directory) / name).is_symlink())
            for name in files:
                if pathlib.Path(name).suffix.lower() not in IMAGE_SUFFIXES:
                    continue
                path = pathlib.Path(directory) / name
                stat = path.stat()
                relative = path.relative_to(root).as_posix()
                items.append({"path": relative, "size": stat.st_size, "mtime": int(stat.st_mtime),
                              "uri": path.as_uri(), **parse(relative)})
    items.sort(key=lambda item: (-item["mtime"], item["path"].casefold()))
    return items


def _json_script(value):
    return json.dumps(value, ensure_ascii=True, separators=(",", ":")).replace(
        "<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def people(root):
    if __package__:
        from . import reference_execution
    else:
        import reference_execution
    try:
        sources = reference_execution.gallery_sources(root)
    except (OSError, ValueError):
        return []
    seen = {}
    for source in sources:
        if source.get("kind"):
            continue
        key = (source["displayName"], source.get("personId", ""))
        seen[key] = {"displayName": key[0], "personId": key[1]}
    return sorted(seen.values(), key=lambda item: item["displayName"].casefold())


def build_page(root, comfy_root, items, known_people):
    reports_prefix = gallery_chrome.reports_prefix(root / "_generation", root / "_reports") or "../_reports/"
    options = lambda key: "".join(  # noqa: E731
        f'<option value="{html.escape(value, quote=True)}">{html.escape(value)}</option>'
        for value in sorted({item[key] for item in items if item[key]}, key=str.casefold))
    names = "".join(
        f'<option value="{html.escape(person["displayName"], quote=True)}">'
        f'{html.escape(person["personId"])}</option>' for person in known_people)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sovereign Territories — ComfyUI Outputs</title>
<style>
{gallery_chrome.CSS}
.controls {{ display: flex; flex-wrap: wrap; gap: .7rem 1rem; align-items: end; margin: 1rem 0; }}
label.control {{ display: grid; gap: .25rem; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill,minmax(200px,1fr)); gap: .9rem; }}
.output-card {{ background: var(--st-card); border: 1px solid var(--st-line); border-radius: var(--st-radius); padding: .6rem; min-width: 0; box-shadow: var(--st-shadow); }}
.output-card.is-selected {{ outline: 3px solid var(--st-gold); }}
.output-card img {{ display: block; width: 100%; height: 260px; object-fit: contain; background: #e7e4de; cursor: zoom-in; }}
.output-card p {{ margin: .3rem 0 0; font-size: .86rem; overflow-wrap: anywhere; }}
.muted {{ color: var(--st-muted); }}
.pager {{ display: flex; gap: .6rem; align-items: center; margin: 1rem 0; }}
.pull-panel {{ background: var(--st-card); border: 1px solid var(--st-line); border-radius: var(--st-radius); padding: .8rem 1rem; margin: 1rem 0; }}
#viewer {{ position: fixed; inset: 0; background: rgba(8,10,18,.92); display: none; z-index: 10; color: #fff; }}
#viewer.open {{ display: grid; grid-template-rows: auto 1fr; }}
#viewer header {{ display: flex; gap: .8rem; align-items: center; padding: .6rem 1rem; flex-wrap: wrap; }}
#viewer img {{ max-width: 100%; max-height: 100%; margin: auto; object-fit: contain; display: block; }}
#viewer .stage {{ display: grid; place-items: center; overflow: hidden; padding: 0 1rem 1rem; min-height: 0; }}
#viewer-caption {{ flex: 1; overflow-wrap: anywhere; }}
</style>
</head>
<body id="top">
{gallery_chrome.masthead("Outputs", reports_prefix, "ComfyUI outputs · browse and pull back")}
<div class="site-page">
<header class="page-header"><div>
<h1>ComfyUI outputs</h1>
<p>{len(items)} images under <code>{html.escape(str(comfy_root))}</code>, newest first. Images are shown from
ComfyUI's own folders, scaled by the browser; nothing is copied or thumbnailed. Tick the renders worth keeping,
export the pull manifest and run <code>render-reference.cmd pull MANIFEST --root ROOT --apply</code>.</p>
</div></header>
{gallery_chrome.navigation([("People", reports_prefix + "library/people_gallery.html"),
                             ("Rendering", "index.html"), ("Outputs", "outputs.html")], "Outputs")}
<main>
<div class="controls">
<label class="control">Workspace<select id="f-workspace"><option value="">All</option>{options("workspace")}</select></label>
<label class="control">Stage<select id="f-stage"><option value="">All</option>{options("stage")}</select></label>
<label class="control">Workflow<select id="f-variant"><option value="">All</option>{options("variant")}</select></label>
<label class="control">Subject<select id="f-subject"><option value="">All</option>{options("subject")}</select></label>
<label class="control">Search<input id="f-text" type="search" placeholder="Path, batch, file name"></label>
<label class="control">Age<select id="f-age"><option value="">Any time</option><option value="1">Last day</option>
<option value="7">Last 7 days</option><option value="30">Last 30 days</option></select></label>
<label class="control">Per page<select id="f-size">{"".join(f'<option value="{size}"{" selected" if size == 120 else ""}>{size}</option>' for size in PAGE_SIZES)}</select></label>
</div>
<div class="pull-panel">
<strong id="selection-count">0 selected</strong>
<button id="select-page" type="button">Select page</button>
<button id="clear" type="button">Clear selection</button>
<label class="control">Pull as (optional, else the render's own subject)
<input id="pull-name" list="people" placeholder="Gallery name" maxlength="100"></label>
<datalist id="people">{names}</datalist>
<button id="export" type="button" disabled>Export pull manifest</button>
<p class="muted">Pull copies the exact file into <code>_generation/library/&lt;stage&gt;/&lt;workflow&gt;/</code> as
<code>&lt;name&gt;_comfy_&lt;workflow&gt;_&lt;id&gt;</code> plus a cream-padded 944x1104 copy and a sidecar. Pulled renders
are synthetic, never identity evidence, and become selectable sources on the Rendering page.</p>
</div>
<p class="pager"><button id="prev" type="button">Previous</button><span id="page-label"></span>
<button id="next" type="button">Next</button></p>
<div class="grid" id="grid"></div>
</main>
</div>
<div id="viewer" role="dialog" aria-modal="true" aria-label="Full-size view">
<header><button id="v-prev" type="button">&larr;</button><button id="v-next" type="button">&rarr;</button>
<label><input id="v-select" type="checkbox"> Select</label><span id="viewer-caption"></span>
<button id="v-close" type="button">Close (Esc)</button></header>
<div class="stage"><img id="viewer-image" alt=""></div>
</div>
{gallery_chrome.footer("ComfyUI outputs · Browsing only; pull copies just the files you export")}
<script>
"use strict";
const outputRoot = {_json_script(str(comfy_root))};
const items = {_json_script(items)};
const people = {_json_script(known_people)};
const selected = new Set();
let page = 0, filtered = items, viewerIndex = -1;
const $ = id => document.getElementById(id);
function matches(item) {{
  const text = $("f-text").value.trim().toLocaleLowerCase();
  const age = Number($("f-age").value);
  return (!$("f-workspace").value || item.workspace === $("f-workspace").value)
    && (!$("f-stage").value || item.stage === $("f-stage").value)
    && (!$("f-variant").value || item.variant === $("f-variant").value)
    && (!$("f-subject").value || item.subject === $("f-subject").value)
    && (!age || item.mtime * 1000 >= Date.now() - age * 86400000)
    && (!text || item.path.toLocaleLowerCase().includes(text));
}}
function card(item, index) {{
  const node = document.createElement("article");
  node.className = "output-card" + (selected.has(item.path) ? " is-selected" : "");
  const image = document.createElement("img");
  image.loading = "lazy"; image.src = item.uri; image.alt = item.path;
  image.addEventListener("click", () => openViewer(index));
  const label = document.createElement("label");
  const box = document.createElement("input");
  box.type = "checkbox"; box.checked = selected.has(item.path);
  box.addEventListener("change", () => toggle(item, box.checked));
  label.append(box, document.createTextNode(" Select"));
  const title = document.createElement("p");
  title.textContent = [item.subject, item.stage, item.variant].filter(Boolean).join(" · ");
  const meta = document.createElement("p");
  meta.className = "muted";
  meta.textContent = `${{item.workspace}} · ${{new Date(item.mtime * 1000).toLocaleString()}}`;
  const link = document.createElement("a");
  link.href = item.uri; link.target = "_blank"; link.rel = "noopener"; link.textContent = "Open file";
  node.append(label, image, title, meta, link);
  return node;
}}
function render() {{
  const size = Number($("f-size").value);
  const pages = Math.max(1, Math.ceil(filtered.length / size));
  page = Math.min(page, pages - 1);
  const grid = $("grid");
  grid.replaceChildren(...filtered.slice(page * size, page * size + size)
    .map((item, offset) => card(item, page * size + offset)));
  $("page-label").textContent = `Page ${{page + 1}} of ${{pages}} · ${{filtered.length}} matching`;
  $("prev").disabled = page === 0; $("next").disabled = page >= pages - 1;
  $("selection-count").textContent = `${{selected.size}} selected`;
  $("export").disabled = selected.size === 0 || selected.size > {MAX_PULL};
}}
function refilter() {{ filtered = items.filter(matches); page = 0; render(); }}
function toggle(item, on) {{ if (on) selected.add(item.path); else selected.delete(item.path); render(); }}
function openViewer(index) {{
  viewerIndex = index;
  const item = filtered[index];
  if (!item) return;
  $("viewer-image").src = item.uri;
  $("viewer-image").alt = item.path;
  $("viewer-caption").textContent = item.path;
  $("v-select").checked = selected.has(item.path);
  $("viewer").classList.add("open");
}}
function closeViewer() {{ $("viewer").classList.remove("open"); $("viewer-image").removeAttribute("src"); viewerIndex = -1; }}
["f-workspace", "f-stage", "f-variant", "f-subject", "f-age", "f-size"].forEach(id => $(id).addEventListener("change", refilter));
$("f-text").addEventListener("input", refilter);
$("prev").addEventListener("click", () => {{ page--; render(); }});
$("next").addEventListener("click", () => {{ page++; render(); }});
$("select-page").addEventListener("click", () => {{
  const size = Number($("f-size").value);
  filtered.slice(page * size, page * size + size).forEach(item => selected.add(item.path));
  render();
}});
$("clear").addEventListener("click", () => {{ selected.clear(); render(); }});
$("v-prev").addEventListener("click", () => openViewer(Math.max(0, viewerIndex - 1)));
$("v-next").addEventListener("click", () => openViewer(Math.min(filtered.length - 1, viewerIndex + 1)));
$("v-close").addEventListener("click", closeViewer);
$("v-select").addEventListener("change", event => toggle(filtered[viewerIndex], event.target.checked));
document.addEventListener("keydown", event => {{
  if (viewerIndex < 0) return;
  if (event.key === "Escape") closeViewer();
  if (event.key === "ArrowLeft") openViewer(Math.max(0, viewerIndex - 1));
  if (event.key === "ArrowRight") openViewer(Math.min(filtered.length - 1, viewerIndex + 1));
}});
$("export").addEventListener("click", () => {{
  const name = $("pull-name").value.trim();
  const person = people.find(entry => entry.displayName === name);
  const chosen = items.filter(item => selected.has(item.path)).map(item => {{
    const entry = {{output: item.path, size: item.size, mtime: item.mtime}};
    if (name) entry.displayName = name;
    if (person && person.personId) entry.personId = person.personId;
    return entry;
  }});
  const blob = new Blob([JSON.stringify({{schemaVersion: 1, outputRoot, items: chosen}}, null, 2) + "\\n"],
    {{type: "application/json"}});
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `pull-${{new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14)}}.json`;
  link.click();
  URL.revokeObjectURL(link.href);
}});
refilter();
</script>
</body>
</html>
"""


def publish(root, comfy_root, workspaces=None, apply=False, check=False):
    items = scan(comfy_root, workspaces)
    page = build_page(root, comfy_root, items, people(root))
    target = base.safe_path(root, PAGE_RELATIVE)
    summary = {"page": str(target), "images": len(items), "outputRoot": str(comfy_root),
               "workspaces": sorted({item["workspace"] for item in items}, key=str.casefold)}
    if check:
        summary["current"] = target.is_file() and target.read_text(encoding="utf-8") == page
    elif apply:
        target.parent.mkdir(parents=True, exist_ok=True)
        pending = target.with_name(target.name + ".pending")
        pending.write_text(page, encoding="utf-8")
        report_assets.replace_file(pending, target)
    return {**summary, "applied": apply}


def _folder(value, default):
    text = re.sub(r"[^A-Za-z0-9_-]+", "_", value or "").strip("_-")[:64]
    return text if text and FOLDER.fullmatch(text) else default


def name_prefix(display_name):
    prefix = re.sub(r"[^a-z0-9]+", "_", display_name.lower()).strip("_")[:48]
    if not prefix:
        raise ValueError(f"Display name cannot form a file name: {display_name!r}")
    return prefix


def png_lineage(data):
    """ComfyUI embeds the prompt/workflow and our extra_pnginfo as PNG text chunks."""
    lineage = {}
    with Image.open(io.BytesIO(data)) as image:
        info = dict(getattr(image, "text", {}) or {})
    for key in ("prompt", "workflow"):
        if isinstance(info.get(key), str):
            lineage[key + "Sha256"] = hashlib.sha256(info[key].encode("utf-8")).hexdigest()
    for key, field in (("reference_batch", "batchId"), ("reference_job", "jobId")):
        if isinstance(info.get(key), str):
            lineage[field] = info[key].strip('"')
    if isinstance(info.get("prompt"), str):
        try:
            graph = json.loads(info["prompt"])
            prefixes = sorted({node["inputs"]["filename_prefix"] for node in graph.values()
                               if isinstance(node, dict) and node.get("class_type") == "SaveImage"
                               and isinstance(node.get("inputs", {}).get("filename_prefix"), str)})
            if prefixes:
                lineage["filenamePrefixes"] = prefixes
        except (ValueError, AttributeError, TypeError):
            pass
    lineage["pngInfoKeys"] = sorted(info)
    return lineage


def _receipt_job(root, batch_id, job_id):
    if not batch_id or not job_id or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", batch_id):
        return None
    try:
        request = base.read_json(base.safe_path(root, f"_generation/reference/{batch_id}/request.json"))
    except (OSError, ValueError):
        return None
    return next((job for job in request.get("jobs", []) if job.get("id") == job_id), None)


def padded(data):
    with Image.open(io.BytesIO(data)) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGBA")
            canvas = Image.new("RGBA", image.size, CREAM + (255,))
            canvas.alpha_composite(image)
            image = canvas
        fitted = ImageOps.contain(image.convert("RGB"), STANDARD_SIZE, Image.Resampling.LANCZOS)
    result = Image.new("RGB", STANDARD_SIZE, CREAM)
    result.paste(fitted, ((STANDARD_SIZE[0] - fitted.width) // 2, (STANDARD_SIZE[1] - fitted.height) // 2))
    stream = io.BytesIO()
    result.save(stream, "PNG")
    return stream.getvalue()


def _existing_pulls(root):
    library = root / pathlib.Path(LIBRARY_RELATIVE)
    found = {}
    if library.is_dir():
        for sidecar in library.glob("*/*/*.json"):
            try:
                record = base.read_json(sidecar)
            except (OSError, ValueError):
                continue
            if isinstance(record.get("sha256"), str):
                found[record["sha256"]] = sidecar.with_suffix("").relative_to(root).as_posix()
    return found


def _write_new(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Refusing to replace different bytes: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def pull(root, manifest_path, comfy_root, apply=False):
    manifest = base.read_json(manifest_path)
    if not isinstance(manifest, dict) or manifest.get("schemaVersion") != 1 or not isinstance(manifest.get("items"), list):
        raise ValueError("Pull manifest must be {schemaVersion: 1, outputRoot, items: [...]}")
    if pathlib.Path(manifest.get("outputRoot", "")).resolve() != comfy_root:
        raise ValueError("Manifest output root differs from the configured ComfyUI output root")
    if not 1 <= len(manifest["items"]) <= MAX_PULL:
        raise ValueError(f"Pull 1..{MAX_PULL} images per manifest")
    existing = _existing_pulls(root)
    planned, results = [], []
    for entry in manifest["items"]:
        relative = entry.get("output") if isinstance(entry, dict) else None
        if not isinstance(relative, str) or pathlib.PurePosixPath(relative).suffix.lower() not in IMAGE_SUFFIXES:
            raise ValueError(f"Manifest entry needs an image output path: {entry!r}")
        source = base.safe_path(comfy_root, relative)
        stat = source.stat()
        if stat.st_size != entry.get("size") or int(stat.st_mtime) != entry.get("mtime"):
            raise ValueError(f"Output changed since the page was published: {relative}")
        data = source.read_bytes()
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        sha = hashlib.sha256(data).hexdigest()
        if sha in existing:
            results.append({"output": relative, "state": "already-pulled", "destination": existing[sha]})
            continue
        info = parse(relative)
        lineage = png_lineage(data)
        batch_id = info["batch"] or lineage.get("batchId", "")
        job_id = info["job"] or lineage.get("jobId", "")
        job = _receipt_job(root, batch_id, job_id)
        display = entry.get("displayName") or (job or {}).get("displayName") or info["subject"]
        if not isinstance(display, str) or not display or len(display) > 100:
            raise ValueError(f"Invalid display name for {relative}")
        person = entry.get("personId") or (job or {}).get("personId")
        if person is not None and (not isinstance(person, str) or len(person) > 100):
            raise ValueError(f"Invalid person ID for {relative}")
        stage = _folder(info["stage"], "Other")
        variant = _folder(info["variant"], "unsorted")
        suffix = pathlib.PurePosixPath(relative).suffix.lower().replace(".jpeg", ".jpg")
        stem = f"{name_prefix(display)}_comfy_{variant.lower()}_{hashlib.sha1(data).hexdigest()[:8]}"
        folder = f"{LIBRARY_RELATIVE}/{stage}/{variant}"
        target = base.safe_path(root, f"{folder}/{stem}{suffix}")
        square = padded(data)
        record = {
            "schemaVersion": 1, "kind": "pulled-render", "synthetic": True, "identityCoreEligible": False,
            "domain": "general", "sha256": sha, "displayName": display, "stage": stage, "variant": variant,
            "workspace": info["workspace"], "sourceOutput": str(source), "outputRelative": relative,
            "outputSize": stat.st_size, "outputMtime": int(stat.st_mtime), "pulledAt": datetime.datetime.now(
                datetime.timezone.utc).isoformat(),
            "padded": {"file": f"{stem}_944x1104.png", "sha256": hashlib.sha256(square).hexdigest(),
                       "size": list(STANDARD_SIZE)},
            "comfy": lineage,
        }
        if person:
            record["personId"] = person
        if job:
            record["receipt"] = {"batchId": batch_id, "jobId": job_id, "recipe": job.get("recipe"),
                                 "seed": job.get("seed"), "source": job.get("source")}
        planned.append((target, data, square, record))
        existing[sha] = target.relative_to(root).as_posix()
        results.append({"output": relative, "state": "pulled" if apply else "pull-preview",
                        "destination": target.relative_to(root).as_posix(), "displayName": display,
                        "personId": person, "stage": stage, "variant": variant})
    if apply:
        for target, data, square, record in planned:
            _write_new(target, data)
            _write_new(target.with_name(record["padded"]["file"]), square)
            _write_new(target.with_suffix(target.suffix + ".json"), base.encode(record))
    return {"applied": apply, "count": len(planned), "items": results}
