"""Build an offline, metadata-only selector and results page for reference renders.

The page exports bounded request JSON and links to existing local files. It does
not compile workflows, contact ComfyUI, copy images, or promote results.
"""
import argparse
import hashlib
import html
import json
import pathlib
import re
import sys
import tempfile
import urllib.parse


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "art"))
from likeness_library import gallery_chrome, report_assets

if __package__:
    from . import reference_execution
else:
    import reference_execution

OUTPUT_RELATIVE = pathlib.Path("_generation") / "index.html"
SAMPLE_COUNTS = (1, 2, 4, 8, 16)
MAX_INITIAL_JOBS = 64
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,47}$")
HASH_PATTERN = re.compile(r"^[a-f0-9]{64}$")
FOLDER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
SOURCE_ROOTS = {"Angels", "Sisters", "Models", "Prospects", "Potentials", "Various", "Artists"}
SUPPORTED_RECIPES = {
    "manual-0c-cleanup-basic": "0c Cleanup Basic",
    "manual-0c-cleanup": "0c Cleanup",
    "manual-0e-enhance": "0e Enhance",
    "manual-0f-full": "0f Full",
    "manual-0b-background-basic": "0b Background Basic",
    "manual-0d-deluxe-pose": "0d Deluxe Pose (clothed)",
}
SUPPORTED_STAGES = {"0_Edit", "1_Alpha", "2_Studies", "Bench"}
SOURCE_DIRECTORIES = {
    "gallery", "review", "gallery_944x1104", "headshot_944x1104", "chest_944x1104",
}
SAFE_PENDING_LABELS = {
    ("0_Edit", "0d Deluxe"): "0d Deluxe",
    ("1_Alpha", "A-pose"): "A-pose",
    ("2_Studies", "Studies"): "Studies",
    ("Bench", "Optional diagnostics"): "Optional diagnostics",
}
CLEANUP_LABELS = {
    "needs-cleanup": "Needs cleanup (overlay left)",
    "repainted": "LaMa repainted",
    "enhancement-failed": "Enhancement failed",
}


def _json_script(value):
    return json.dumps(value, ensure_ascii=True, separators=(",", ":")).replace(
        "<", "\\u003c"
    ).replace(">", "\\u003e").replace("&", "\\u0026").replace("\u2028", "\\u2028").replace(
        "\u2029", "\\u2029"
    )


def _source_path(root, relative, kind="photo"):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError(f"Invalid root-relative source path: {relative!r}")
    if kind not in {"photo", "selected-render", "pulled-render"}:
        raise ValueError("Unknown source kind")
    parts = relative.split("/")
    selected = kind == "selected-render"
    if (any(not part or part in {".", ".."} for part in parts)
            or any(re.search(r'[<>:"|?*\x00-\x1f]', part) or part.endswith((" ", "."))
                   for part in parts)):
        raise ValueError(f"Unsafe source path: {relative}")
    if kind == "pulled-render":
        if (len(parts) != 5 or parts[:2] != ["_generation", "library"]
                or not FOLDER_PATTERN.fullmatch(parts[2]) or not FOLDER_PATTERN.fullmatch(parts[3])):
            raise ValueError("Pulled render must use a _generation/library/<stage>/<workflow> path")
    elif selected:
        if (len(parts) != 5 or parts[:2] != ["_generation", "selected"]
                or not ID_PATTERN.fullmatch(parts[2]) or not ID_PATTERN.fullmatch(parts[3])):
            raise ValueError("Selected render must use a retained batch/job path")
    elif (parts[0] not in SOURCE_ROOTS or len(parts) < 3
          or any(part.startswith("_") for part in parts)
          or not any(part in SOURCE_DIRECTORIES for part in parts[1:-1])):
        raise ValueError(f"Source path is not an active root-relative photo: {relative}")
    reserved_names = {"CON", "PRN", "AUX", "NUL"}
    reserved_names.update(f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10))
    if any(part.split(".", 1)[0].upper() in reserved_names for part in parts):
        raise ValueError(f"Unsafe source path: {relative}")
    path = root.joinpath(*parts)
    for current in (path, *path.parents):
        if current == root.parent:
            break
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError(f"Linked source path is not permitted: {current}")
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise ValueError(f"Source path escapes the library root: {relative}") from error
    return path


def _inspect_selected(root, source):
    if __package__:
        from . import reference_rendering as base
    else:
        import reference_rendering as base
    try:
        base.inspect_source(root, {"source": source})
    except (OSError, ValueError, TypeError, AttributeError) as error:
        raise ValueError("Synthetic render source is held: missing or invalid provenance/image") from error


def _validate_sources(root, sources):
    if not isinstance(sources, list):
        raise ValueError("Sources must be a JSON array")
    cleaned = []
    seen = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("Each source must be an object")
        path = source.get("path")
        if isinstance(path, str) and len(path) > 500:
            raise ValueError("Source path exceeds 500 characters")
        kind = source.get("kind", "photo")
        file_path = _source_path(root, path, kind)
        digest = source.get("sha256")
        domain = source.get("domain")
        display_name = source.get("displayName")
        if not isinstance(digest, str) or not HASH_PATTERN.fullmatch(digest):
            raise ValueError(f"Invalid source SHA-256: {path}")
        if domain not in {"general", "artists"}:
            raise ValueError(f"Invalid source domain: {path}")
        if kind == "photo" and (path.split("/", 1)[0] == "Artists") != (domain == "artists"):
            raise ValueError(f"Source domain mismatch: {path}")
        if display_name is not None and (
                not isinstance(display_name, str) or not display_name or len(display_name) > 100):
            raise ValueError(f"Invalid displayName: {path}")
        person_id = source.get("personId")
        if person_id is not None and (
                not isinstance(person_id, str) or not person_id or len(person_id) > 100):
            raise ValueError(f"Invalid personId: {path}")
        if path.casefold() in seen:
            raise ValueError(f"Duplicate source path: {path}")
        seen.add(path.casefold())
        cleanup = source.get("cleanup")
        if cleanup is not None and cleanup not in reference_execution.CLEANUP_HINTS:
            raise ValueError(f"Unknown cleanup hint: {path}")
        if kind in {"selected-render", "pulled-render"}:
            _inspect_selected(root, {
                "path": path, "sha256": digest, "domain": domain, "kind": kind,
            })
        cleaned.append({
            "path": path,
            "sha256": digest,
            "domain": domain,
            **({"kind": kind} if "kind" in source or kind != "photo" else {}),
            "displayName": display_name,
            "personId": person_id,
            "cleanup": cleanup,
            "exists": file_path.is_file(),
        })
    return cleaned


def _validate_recipes(recipes):
    if not isinstance(recipes, list):
        raise ValueError("Recipes must be a JSON array")
    cleaned = []
    seen = set()
    for index, recipe in enumerate(recipes):
        if not isinstance(recipe, dict):
            raise ValueError("Each recipe must be an object")
        recipe_id = recipe.get("id")
        label = recipe.get("label")
        stage = recipe.get("stage")
        available = recipe.get("available")
        reason = recipe.get("reason", "")
        if not isinstance(recipe_id, str) or not recipe_id or len(recipe_id) > 150:
            raise ValueError("Each recipe needs an id no longer than 150 characters")
        if not isinstance(label, str) or not label:
            raise ValueError(f"Recipe {recipe_id!r} needs a label")
        if not isinstance(stage, str) or not stage:
            raise ValueError(f"Recipe {recipe_id!r} needs a stage")
        if not isinstance(available, bool):
            raise ValueError(f"Recipe {recipe_id!r} needs a boolean available value")
        if not isinstance(reason, str):
            raise ValueError(f"Recipe {recipe_id!r} has an invalid reason")
        if recipe_id.casefold() in seen:
            raise ValueError(f"Duplicate recipe id: {recipe_id}")
        seen.add(recipe_id.casefold())
        supported = recipe_id in SUPPORTED_RECIPES and stage == "0_Edit"
        pending_label = SAFE_PENDING_LABELS.get((stage, label))
        is_safe_pending = recipe_id.startswith("pending-") and pending_label is not None
        cleaned.append({
            "id": recipe_id if supported or is_safe_pending else f"unavailable-recipe-{index + 1}",
            "label": (SUPPORTED_RECIPES[recipe_id] if supported else
                      pending_label if is_safe_pending else "Unavailable recipe"),
            "stage": stage if stage in SUPPORTED_STAGES else "Other",
            "available": supported and available,
            "reason": ("" if supported and available else
                       "Recipe unavailable in the current environment" if supported else
                       "Not one of the four supported clothed-preservation modes"),
            "kind": ("provisional clothed transport pilot; not exact manual prompt migration"
                     if supported else "target recipe" if is_safe_pending else "unavailable"),
            "promptPolicy": "clothed-preservation-pilot-v1" if supported else "",
        })
    return cleaned


def _root_relative_uri(relative):
    quoted = "/".join(urllib.parse.quote(part, safe="") for part in relative.split("/"))
    return "../" + quoted


def _reject_linked_path(root, path):
    root = root.resolve()
    path = pathlib.Path(path)
    current = path
    while current != root and root in current.parents:
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError(f"Linked gallery path is not permitted: {current}")
        current = current.parent
    try:
        path.resolve().relative_to(root)
    except (OSError, ValueError) as error:
        raise ValueError(f"Gallery path escapes the library root: {path}") from error


def _absolute_file_uri(value, allowed_root):
    if not isinstance(value, str) or not value:
        return None
    path = pathlib.Path(value)
    output_root = pathlib.Path(allowed_root) if isinstance(allowed_root, str) else None
    if not path.is_absolute() or output_root is None or not output_root.is_absolute():
        return None
    try:
        if not path.is_file():
            return None
        resolved_path = path.resolve()
        resolved_path.relative_to(output_root.resolve())
        return resolved_path.as_uri()
    except (OSError, ValueError):
        return None


def _frozen_input_uri(root, batch_id, job_id, run_job):
    relative = run_job.get("input") if isinstance(run_job, dict) else None
    if not isinstance(relative, str):
        return None
    parts = relative.split("/")
    if (len(parts) != 4 or parts[0] != "jobs" or parts[1] != job_id
            or parts[2] != "input" or any(part in {"", ".", ".."} for part in parts)
            or any(re.search(r'[<>:"\\|?*\x00-\x1f]', part) for part in parts)):
        return None
    base = root / "_generation" / "reference" / batch_id
    path = base.joinpath(*parts)
    try:
        _reject_linked_path(base, path)
        if not path.is_file():
            return None
        quoted = "/".join(urllib.parse.quote(part, safe="") for part in
                          ("reference", batch_id, *parts))
        return quoted
    except (OSError, ValueError):
        return None


def _diagnostic_batch(batch_id, message):
    return {"id": batch_id, "diagnostic": message, "jobs": []}


def _execution_batches(root):
    batches_dir = root / "_generation" / "reference"
    _reject_linked_path(root, batches_dir)
    if not batches_dir.is_dir():
        return []
    batches = []
    for directory in sorted(batches_dir.iterdir(), key=lambda item: item.name.casefold()):
        if (not ID_PATTERN.fullmatch(directory.name) or not directory.is_dir()
                or directory.is_symlink()
                or (hasattr(directory, "is_junction") and directory.is_junction())):
            continue
        execution_path = directory / "execution.json"
        request_path = directory / "request.json"
        run_path = directory / "run.json"
        if not execution_path.exists():
            try:
                run_evidence = json.loads(run_path.read_text(encoding="utf-8-sig"))
            except (OSError, ValueError, UnicodeError):
                run_evidence = {}
            if (isinstance(run_evidence, dict)
                    and run_evidence.get("state") == "inputs-only-not-render-ready"):
                batches.append(_diagnostic_batch(
                    directory.name, "Inputs prepared; no executable receipt yet"
                ))
            else:
                batches.append(_diagnostic_batch(directory.name, "Missing execution.json receipt"))
            continue
        if execution_path.is_symlink() or (hasattr(execution_path, "is_junction") and execution_path.is_junction()):
            batches.append(_diagnostic_batch(directory.name, "Linked execution receipt refused"))
            continue
        if not request_path.is_file() or request_path.is_symlink():
            batches.append(_diagnostic_batch(directory.name, "Missing or linked frozen request.json"))
            continue
        if run_path.exists() and (run_path.is_symlink()
                                  or (hasattr(run_path, "is_junction") and run_path.is_junction())):
            batches.append(_diagnostic_batch(directory.name, "Linked frozen run.json refused"))
            continue
        try:
            execution = json.loads(execution_path.read_text(encoding="utf-8-sig"))
            request = json.loads(request_path.read_text(encoding="utf-8-sig"))
            run = json.loads(run_path.read_text(encoding="utf-8-sig")) if run_path.is_file() else {}
        except (OSError, ValueError, UnicodeError):
            batches.append(_diagnostic_batch(directory.name, "Unreadable or corrupt batch metadata JSON"))
            continue
        if (not isinstance(execution, dict) or execution.get("schemaVersion") != 1
                or execution.get("batchId") != directory.name
                or not isinstance(execution.get("jobs"), dict)
                or not isinstance(request, dict) or request.get("batchId") != directory.name
                or not isinstance(request.get("jobs"), list)):
            batches.append(_diagnostic_batch(directory.name, "Invalid execution receipt or frozen request shape"))
            continue
        frozen_jobs = {job.get("id"): job for job in request["jobs"]
                       if isinstance(job, dict) and isinstance(job.get("id"), str)}
        output_root = execution.get("outputRoot")
        run_jobs = {}
        if isinstance(run, dict) and isinstance(run.get("jobs"), list):
            run_jobs = {job.get("id"): job for job in run["jobs"]
                        if isinstance(job, dict) and isinstance(job.get("id"), str)}
        batch_jobs = []
        for job_id, frozen in frozen_jobs.items():
            execution_job = execution["jobs"].get(job_id)
            if not isinstance(execution_job, dict):
                execution_job = {"state": "missing execution status"}
            source = frozen.get("source", {})
            source_path = source.get("path") if isinstance(source, dict) else None
            try:
                source_file = (_source_path(root, source_path, source.get("kind", "photo"))
                               if isinstance(source_path, str) else None)
                if source_file is not None and source.get("kind") in {"selected-render", "pulled-render"}:
                    _inspect_selected(root, source)
            except ValueError:
                source_file = None
            outputs = execution_job.get("outputs", [])
            if not isinstance(outputs, list):
                outputs = []
            safe_outputs = []
            for output in outputs:
                if not isinstance(output, dict):
                    continue
                path = output.get("path")
                uri = _absolute_file_uri(path, output_root)
                sha256 = output.get("sha256")
                safe_outputs.append({
                    "filename": output.get("filename") if isinstance(output.get("filename"), str) else "",
                    "subfolder": output.get("subfolder") if isinstance(output.get("subfolder"), str) else "",
                    "type": output.get("type") if isinstance(output.get("type"), str) else "",
                    "path": path if isinstance(path, str) else "",
                    "uri": uri,
                    "sha256": sha256 if isinstance(sha256, str) and HASH_PATTERN.fullmatch(sha256) else "",
                    "exists": uri is not None,
                })
            batch_jobs.append({
                "id": job_id,
                "displayName": frozen.get("displayName") if isinstance(frozen.get("displayName"), str) else "",
                "sourcePath": source_path if isinstance(source_path, str) else "",
                "sourceUri": (_root_relative_uri(source_path)
                              if source_file is not None and source_file.is_file() else ""),
                "historicalUri": ("" if source_file is not None and source_file.is_file() else
                                  _frozen_input_uri(root, directory.name, job_id, run_jobs.get(job_id)) or ""),
                "recipe": (frozen.get("recipe") if isinstance(frozen.get("recipe"), str)
                           and frozen.get("recipe") in SUPPORTED_RECIPES else "Unsupported recipe"),
                "seed": (frozen.get("seed") if isinstance(frozen.get("seed"), int)
                         and not isinstance(frozen.get("seed"), bool) else "unknown"),
                "input": ("frozen source image available"
                          if _frozen_input_uri(root, directory.name, job_id, run_jobs.get(job_id))
                          else "not recorded"),
                "state": (execution_job.get("state") if isinstance(execution_job.get("state"), str)
                          and execution_job.get("state") in {
                    "queued", "running", "completed", "failed", "cancelled", "interrupted"
                } else "unknown"),
                "error": "Job execution reported an error." if execution_job.get("error") else "",
                "promptPolicy": (execution_job.get("promptPolicy")
                                 if execution_job.get("promptPolicy") == "clothed-preservation-pilot-v1"
                                 else ""),
                "promptOverrideRecorded": bool(execution_job.get("promptOverride")),
                "outputs": safe_outputs,
            })
        batches.append({
            "id": directory.name,
            "jobs": batch_jobs,
        })
    return batches


def make_request(root, selected_sources, recipe, sample_count, batch_id, seeds=None):
    """Create a bounded request: each source x each recipe x samples, in that order."""
    if sample_count not in SAMPLE_COUNTS:
        raise ValueError("Samples per source must be " + ", ".join(map(str, SAMPLE_COUNTS)))
    if not selected_sources:
        raise ValueError("Select at least one source")
    chosen_recipes = recipe if isinstance(recipe, list) else [recipe]
    if not chosen_recipes:
        raise ValueError("Select at least one recipe")
    total_jobs = len(selected_sources) * len(chosen_recipes) * sample_count
    if total_jobs > MAX_INITIAL_JOBS:
        raise ValueError(f"Batch limit is {MAX_INITIAL_JOBS} jobs; selected sources would create {total_jobs}")
    if not isinstance(batch_id, str) or not ID_PATTERN.fullmatch(batch_id):
        raise ValueError("Invalid batch ID")
    if seeds is not None and len(seeds) != total_jobs:
        raise ValueError(f"Provide exactly {total_jobs} seeds")
    available_recipes = _validate_recipes(chosen_recipes)
    for item in available_recipes:
        if not item["available"]:
            raise ValueError(f"Recipe is unavailable: {item['reason']}")
    sources = _validate_sources(root, selected_sources)
    jobs = []
    for source in sources:
        path = _source_path(root, source["path"], source.get("kind", "photo"))
        if not path.is_file():
            raise ValueError(f"Source file is missing: {source['path']}")
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != source["sha256"]:
            raise ValueError(f"Source hash changed: {source['path']}")
        for item in available_recipes:
            for _sample_index in range(sample_count):
                index = len(jobs) + 1
                seed = seeds[index - 1] if seeds is not None else index
                if not isinstance(seed, int) or isinstance(seed, bool) or not 0 <= seed <= 9007199254740991:
                    raise ValueError("Seed must be a non-negative safe integer")
                job = {
                    "id": f"job-{index:02d}",
                    "source": {key: source[key] for key in ("path", "sha256", "domain")},
                    "workflowMode": "reference",
                    "recipe": item["id"],
                    "profile": "reference-faithful",
                    "seed": seed,
                }
                if "kind" in source:
                    job["source"]["kind"] = source["kind"]
                if source["displayName"] is not None:
                    job["displayName"] = source["displayName"]
                if source["personId"] is not None:
                    job["personId"] = source["personId"]
                jobs.append(job)
    return {
        "schemaVersion": 1,
        "batchId": batch_id,
        "workspace": "Sovereign Females",
        "jobs": jobs,
    }


def build_page(root, sources, recipes):
    """Render the self-contained selector and read-only results gallery."""
    root = pathlib.Path(root).resolve()
    sources = _validate_sources(root, sources)
    recipes = _validate_recipes(recipes)
    stages = sorted({recipe["stage"] for recipe in recipes}, key=str.casefold)
    source_cards = []
    for index, source in enumerate(sources):
        display_name = source["displayName"] or "Unnamed source"
        person_id = source["personId"]
        preview = ""
        if source["exists"]:
            preview = (
                f'<img loading="lazy" src="{html.escape(_root_relative_uri(source["path"]), quote=True)}" '
                f'alt="Source preview for {html.escape(display_name, quote=True)}">'
            )
        else:
            preview = '<div class="missing-preview">Source file is missing</div>'
        source_cards.append(
            f'<article class="source-card" data-source-index="{index}">'
            f'<label class="selection"><input type="checkbox" class="source-choice" '
            f'{"disabled " if not source["exists"] else ""}'
            f'value="{index}" aria-label="Select {html.escape(display_name, quote=True)}">'
            f'<span>Select</span></label>{preview}'
            f'<h3>{html.escape(display_name)}</h3>'
            f'<p class="source-path">{html.escape(source["path"])}</p>'
            f'<p>Domain: {html.escape(source["domain"])}'
            + (f' · Person ID: {html.escape(person_id)}' if person_id else "")
            + "</p>"
            + ('<p class="notice">Synthetic selected render · Never an identity original or identity-core evidence</p>'
               if source.get("kind") == "selected-render" else "")
            + ('<p class="notice">Synthetic pulled render · Never an identity original or identity-core evidence</p>'
               if source.get("kind") == "pulled-render" else "")
            + (f'<p class="hint hint-{html.escape(source["cleanup"], quote=True)}">'
               f'{html.escape(CLEANUP_LABELS[source["cleanup"]])}</p>' if source.get("cleanup") else "")
            + "</article>"
        )
    stages_html = "".join(
        f'<option value="{html.escape(stage, quote=True)}">{html.escape(stage)}</option>'
        for stage in stages
    )
    recipe_groups = []
    for stage in stages:
        boxes = "".join(
            f'<label class="recipe-option" data-stage="{html.escape(recipe["stage"], quote=True)}">'
            f'<input type="checkbox" class="recipe-choice" value="{html.escape(recipe["id"], quote=True)}" '
            f'data-available="{str(recipe["available"]).lower()}" '
            f'{"disabled " if not recipe["available"] else ""}>'
            f'{html.escape(recipe["label"])} [{html.escape(recipe["kind"])}]'
            f'{(" (Unavailable: " + html.escape(recipe["reason"]) + ")") if not recipe["available"] else ""}'
            f'</label>'
            for recipe in recipes if recipe["stage"] == stage
        )
        recipe_groups.append(
            f'<fieldset class="recipe-group" data-stage="{html.escape(stage, quote=True)}">'
            f'<legend>{html.escape(stage)}</legend>{boxes}</fieldset>'
        )
    recipe_options = "".join(recipe_groups)
    hint_options = "".join(
        f'<option value="{html.escape(key, quote=True)}">{html.escape(CLEANUP_LABELS[key])}</option>'
        for key in reference_execution.CLEANUP_HINTS
    )
    result_batches = _execution_batches(root)
    results_json = _json_script(result_batches)
    sources_json = _json_script(sources)
    recipes_json = _json_script(recipes)
    source_cards_html = "".join(source_cards) or '<p class="empty">No source cards supplied.</p>'
    reports_prefix = gallery_chrome.reports_prefix(
        root / "_generation", root / "_reports"
    )
    if reports_prefix is None:
        reports_prefix = "../_reports/"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sovereign Females — Reference Gallery</title>
<style>
{gallery_chrome.CSS}
.notice {{ border-left: 4px solid var(--st-gold); background: var(--st-card); padding: .8rem 1rem; }}
.controls {{ display: flex; flex-wrap: wrap; gap: .8rem 1.2rem; align-items: end; margin: 1rem 0; }}
label.control {{ display: grid; gap: .25rem; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill,minmax(220px,1fr)); gap: 1rem; }}
.source-card, .result-job {{ background: var(--st-card); border: 1px solid var(--st-line); border-radius: var(--st-radius); padding: .8rem; min-width: 0; box-shadow: var(--st-shadow); }}
.source-card img, .result-job img {{ display: block; width: 100%; max-height: 280px; object-fit: contain; background: #e7e4de; }}
.missing-preview {{ display: grid; place-items: center; min-height: 120px; background: #f5d6d6; color: #7b2222; }}
.selection {{ display: flex; gap: .4rem; align-items: center; margin-bottom: .4rem; }}
.source-path, .muted {{ color: var(--st-muted); overflow-wrap: anywhere; font-size: .9rem; }}
.batch {{ border-top: 1px solid var(--st-line); padding-top: 1rem; margin-top: 1.5rem; }}
.result-output {{ border-top: 1px solid var(--st-line); margin-top: .8rem; padding-top: .7rem; overflow-wrap: anywhere; }}
.error {{ color: #7b2222; white-space: pre-wrap; overflow-wrap: anywhere; }}
.empty, .diagnostic {{ color: var(--st-muted); }}
.source-card.is-deep-link {{ outline: 4px solid var(--st-gold); outline-offset: 3px; }}
.recipes {{ display: flex; flex-wrap: wrap; gap: .8rem; margin: 0 0 1rem; }}
.recipe-group {{ border: 1px solid var(--st-line); border-radius: var(--st-radius); background: var(--st-card); padding: .4rem .8rem .6rem; }}
.recipe-group legend {{ font-weight: 700; padding: 0 .3rem; }}
.recipe-option {{ display: block; margin: .2rem 0; }}
.hint {{ display: inline-block; border-radius: 999px; padding: .1rem .6rem; font-size: .85rem; background: #f4e3b5; color: #5a4300; }}
.hint-repainted {{ background: #dfe9f7; color: #1d3f6e; }}
.hint-enhancement-failed {{ background: #f5d6d6; color: #7b2222; }}
code {{ overflow-wrap: anywhere; }}
</style>
</head>
<body id="top">
{gallery_chrome.masthead("Rendering", reports_prefix, "Sovereign Females · Rendering")}
<div class="site-page">
<header class="page-header"><div>
<h1>Sovereign Females — Reference Gallery</h1>
<p class="notice">Offline metadata gallery. Export creates request JSON only; it does not compile workflows,
contact ComfyUI, copy images, or promote results. Existing result links point to files in ComfyUI Outputs.</p>
<p class="muted">Four coordinated tracks: image intake, dynamic ComfyUI execution, stage/template migration,
and this integrated GUI. The four enabled entries are provisional clothed transport pilots; they are not
exact manual prompt migrations. Manual source prompts may contain contradictory instructions and are never
previewed or copied here. After tag rationalization these modes are intended to migrate into normal shared
templates/JSON; other catalogue entries, including 0d, stay disabled until separately graph-bound and reviewed.</p>
<p>Browse <a href="{html.escape(reports_prefix + 'library/people_gallery.html', quote=True)}">People</a> or
<a href="{html.escape(reports_prefix + 'artists/artists_gallery.html', quote=True)}">Artists</a> galleries.</p>
</div></header>
{gallery_chrome.navigation([("People", reports_prefix + "library/people_gallery.html"),
                             ("Artists", reports_prefix + "artists/artists_gallery.html"),
                             ("Rendering", "index.html"), ("Outputs", "outputs.html")], "Rendering")}
<main>
<section aria-labelledby="select-heading">
<h2 id="select-heading">Select sources</h2>
<div class="controls">
<label class="control" for="stage">Show stage
<select id="stage"><option value="">All stages</option>{stages_html}</select></label>
<label class="control" for="sample-count">Samples per workflow
<select id="sample-count">{''.join(f'<option value="{count}"{" selected" if count == 2 else ""}>{count} samples/workflow</option>' for count in SAMPLE_COUNTS)}</select></label>
<label class="control" for="source-filter">Filter sources
<input id="source-filter" type="search" placeholder="Name, person ID, or path"></label>
<label class="control" for="cleanup-filter">Intake cleanup
<select id="cleanup-filter"><option value="">All sources</option><option value="any">Any cleanup hint</option>{hint_options}</select></label>
<button id="select-visible" type="button">Select all visible</button>
<button id="clear-selection" type="button">Clear selection</button>
<span id="selection-count" aria-live="polite">0 sources · 0 workflows · 0 jobs</span>
<button id="export-request" type="button" disabled>Export request JSON</button>
</div>
<div class="recipes" id="recipes">{recipe_options}</div>
<p class="muted">Tick one or more workflows (grouped by stage) and select sources; use the filters and
<em>Select all visible</em> for whole sets. Every selected source is expanded in display order, then workflow
order, then sample order. A batch is capped at {MAX_INITIAL_JOBS} jobs and export is disabled above the cap;
the ComfyUI queue holds 200 jobs, and <code>run --queue-depth</code> controls how many are queued at once.
Offline prepare must recheck source hashes. Cleanup hints come from intake preparation evidence:
<code>render-reference.cmd cleanup-batch --root ROOT</code> proposes the same batches from the CLI.</p>
<div class="grid" id="sources">{source_cards_html}</div>
</section>
<section aria-labelledby="results-heading">
<h2 id="results-heading">Execution results</h2>
<p class="muted">This page reads frozen request metadata and execution.json receipts only. Missing output files are
shown as missing; images are not copied into the library.</p>
<div id="results"></div>
<button id="export-promotion" type="button" disabled>Export selected promotion manifest</button>
<p class="muted">Manifest export records explicit selections only. This page does not promote or retain files.</p>
<p class="muted">CLI retention command: <code>render-reference.cmd retain BATCH-ID --root ROOT --job JOB-ID --output-sha HASH --apply</code>.
Use only after checking the output; this page does not run that command.</p>
</section>
</main>
</div>
{gallery_chrome.footer("Reference rendering · Metadata only; images remain in their existing roots")}
<script>
"use strict";
const sources = {sources_json};
const recipes = {recipes_json};
const batches = {results_json};
const stageSelect = document.getElementById("stage");
const countSelect = document.getElementById("sample-count");
const exportButton = document.getElementById("export-request");
const selectedCount = document.getElementById("selection-count");
const selectedSources = () => Array.from(document.querySelectorAll(".source-choice:checked"))
  .map(box => sources[Number(box.value)]).filter(Boolean);
const selectedRecipes = () => Array.from(document.querySelectorAll(".recipe-choice:checked"))
  .map(box => recipes.find(item => item.id === box.value && item.available)).filter(Boolean);
function refreshRecipes() {{
  const stage = stageSelect.value;
  document.querySelectorAll(".recipe-group").forEach(group => {{
    group.hidden = Boolean(stage) && group.dataset.stage !== stage;
  }});
  refreshSelection();
}}
function refreshSelection() {{
  const count = document.querySelectorAll(".source-choice:checked").length;
  const workflows = selectedRecipes().length;
  const jobs = count * workflows * Number(countSelect.value);
  selectedCount.textContent = `${{count}} sources · ${{workflows}} workflows · ${{jobs}} jobs`;
  exportButton.disabled = workflows < 1 || count < 1 || jobs > {MAX_INITIAL_JOBS};
}}
function refreshSourceFilter() {{
  const query = document.getElementById("source-filter").value.trim().toLocaleLowerCase();
  const hint = document.getElementById("cleanup-filter").value;
  document.querySelectorAll(".source-card").forEach(card => {{
    const source = sources[Number(card.dataset.sourceIndex)];
    const searchable = [source.displayName, source.personId, source.path].filter(Boolean).join(" ").toLocaleLowerCase();
    const hintMatches = !hint || (hint === "any" ? Boolean(source.cleanup) : source.cleanup === hint);
    card.hidden = (Boolean(query) && !searchable.includes(query)) || !hintMatches;
  }});
}}
function downloadJson(name, data) {{
  const blob = new Blob([JSON.stringify(data, null, 2) + "\\n"], {{type: "application/json"}});
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = name;
  link.click();
  URL.revokeObjectURL(link.href);
}}
function makeBatchId() {{
  const random = Math.floor(Math.random() * 0x1000000).toString(16).padStart(6, "0");
  return `gallery-${{new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14)}}-${{random}}`;
}}
function seed() {{
  return Math.floor(Math.random() * Number.MAX_SAFE_INTEGER);
}}
stageSelect.addEventListener("change", refreshRecipes);
countSelect.addEventListener("change", refreshSelection);
document.querySelectorAll(".recipe-choice").forEach(box => box.addEventListener("change", refreshSelection));
document.querySelectorAll(".source-choice").forEach(box => box.addEventListener("change", refreshSelection));
document.getElementById("source-filter").addEventListener("input", refreshSourceFilter);
document.getElementById("cleanup-filter").addEventListener("change", refreshSourceFilter);
document.getElementById("select-visible").addEventListener("click", () => {{
  document.querySelectorAll(".source-card:not([hidden]) .source-choice:not(:disabled)")
    .forEach(box => {{ box.checked = true; }});
  refreshSelection();
}});
document.getElementById("clear-selection").addEventListener("click", () => {{
  document.querySelectorAll(".source-choice:checked").forEach(box => {{ box.checked = false; }});
  refreshSelection();
}});
exportButton.addEventListener("click", () => {{
  const chosenRecipes = selectedRecipes();
  const samples = Number(countSelect.value);
  const chosen = selectedSources();
  const totalJobs = chosen.length * chosenRecipes.length * samples;
  if (!chosenRecipes.length || !chosen.length || totalJobs > {MAX_INITIAL_JOBS}
      || ![{", ".join(map(str, SAMPLE_COUNTS))}].includes(samples)) return;
  const jobs = [];
  for (const source of chosen) for (const recipe of chosenRecipes) for (let sample = 0; sample < samples; sample++) {{
    const job = {{
      id: `job-${{String(jobs.length + 1).padStart(2, "0")}}`,
      source: {{path: source.path, sha256: source.sha256, domain: source.domain}},
      workflowMode: "reference",
      recipe: recipe.id,
      profile: "reference-faithful",
      seed: seed()
    }};
    if (source.kind !== undefined) job.source.kind = source.kind;
    if (source.displayName !== null && source.displayName !== undefined) job.displayName = source.displayName;
    if (source.personId !== null && source.personId !== undefined) job.personId = source.personId;
    jobs.push(job);
  }}
  const batchId = makeBatchId();
  downloadJson(`${{batchId}}.json`, {{
    schemaVersion: 1, batchId, workspace: "Sovereign Females", jobs
  }});
}});
const resultsRoot = document.getElementById("results");
const promotionSelection = new Map();
function element(tag, className, text) {{
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}}
function renderResults() {{
  for (const batch of batches) {{
    const section = element("section", "batch");
    section.appendChild(element("h3", "", `Batch ${{batch.id}}`));
    if (batch.diagnostic) {{
      section.appendChild(element("p", "diagnostic", `Batch diagnostic: ${{batch.diagnostic}}`));
      resultsRoot.appendChild(section);
      continue;
    }}
    const grid = element("div", "grid");
    for (const job of batch.jobs) {{
      const card = element("article", "result-job");
      card.appendChild(element("h4", "", job.displayName || job.id));
      card.appendChild(element("p", "muted", `Recipe: ${{job.recipe || "unknown"}} · Seed: ${{job.seed ?? "unknown"}}`));
      card.appendChild(element("p", "muted", `Status: ${{job.state}}`));
      if (job.promptPolicy) card.appendChild(element("p", "muted", `Prompt policy: ${{job.promptPolicy}}`));
      if (job.promptOverrideRecorded) card.appendChild(element("p", "muted", "Pilot prompt override recorded; text withheld."));
      if (job.sourceUri) {{
        const sourceImage = element("img");
        sourceImage.loading = "lazy";
        sourceImage.src = job.sourceUri;
        sourceImage.alt = `Source: ${{job.displayName || job.id}}`;
        card.appendChild(sourceImage);
        const sourceLink = element("a", "", "View source");
        sourceLink.href = job.sourceUri;
        sourceLink.target = "_blank";
        sourceLink.rel = "noopener";
        card.appendChild(sourceLink);
      }} else if (job.historicalUri) {{
        const historicalImage = element("img");
        historicalImage.loading = "lazy";
        historicalImage.src = job.historicalUri;
        historicalImage.alt = `Historical prepared source snapshot: ${{job.displayName || job.id}}`;
        card.appendChild(historicalImage);
        const historicalLink = element("a", "", "View historical prepared input snapshot");
        historicalLink.href = job.historicalUri;
        historicalLink.target = "_blank";
        historicalLink.rel = "noopener";
        card.appendChild(historicalLink);
        card.appendChild(element("p", "muted", "Historical snapshot; the original source is no longer present."));
      }} else card.appendChild(element("p", "error", `Source and safe historical snapshot missing: ${{job.sourcePath}}`));
      card.appendChild(element("p", "muted", `Prepared input: ${{job.input || "not recorded"}}`));
      if (job.error) card.appendChild(element("p", "error", `Error: ${{job.error}}`));
      if (!job.outputs.length) card.appendChild(element("p", "error", "No output was recorded."));
      for (let index = 0; index < job.outputs.length; index++) {{
        const output = job.outputs[index];
        const outputBox = element("div", "result-output");
        outputBox.appendChild(element("strong", "", output.filename || "Output"));
        outputBox.appendChild(element("p", "muted", `${{output.subfolder || ""}} · ${{output.type || "output"}}`));
        if (output.exists && output.uri) {{
          const outputImage = element("img");
          outputImage.loading = "lazy";
          outputImage.src = output.uri;
          outputImage.alt = `Output: ${{output.filename || job.id}}`;
          outputBox.appendChild(outputImage);
          const link = element("a", "", "Open existing ComfyUI output");
          link.href = output.uri;
          link.target = "_blank";
          link.rel = "noopener";
          outputBox.appendChild(link);
        }} else outputBox.appendChild(element("p", "error", `Output file missing: ${{output.path || output.filename || "unknown"}}`));
        if (output.sha256 && output.exists) {{
          const key = `${{batch.id}}/${{job.id}}/${{output.sha256}}`;
          const label = element("label", "selection");
          const checkbox = document.createElement("input");
          checkbox.type = "checkbox";
          checkbox.checked = promotionSelection.has(key);
          checkbox.addEventListener("change", () => {{
            if (checkbox.checked) promotionSelection.set(key, {{
              schemaVersion: 1, batchId: batch.id, jobId: job.id, outputSha256: output.sha256
            }});
            else promotionSelection.delete(key);
            document.getElementById("export-promotion").disabled = promotionSelection.size === 0;
          }});
          label.append(checkbox, document.createTextNode(" Select for explicit promotion manifest"));
          outputBox.appendChild(label);
        }}
        card.appendChild(outputBox);
      }}
      grid.appendChild(card);
    }}
    section.appendChild(grid);
    resultsRoot.appendChild(section);
  }}
  if (!batches.length) resultsRoot.appendChild(element("p", "empty", "No execution receipts found."));
}}
document.getElementById("export-promotion").addEventListener("click", () => {{
  if (!promotionSelection.size) return;
  downloadJson("reference-promotion-manifest.json", Array.from(promotionSelection.values()));
}});
const requestedSource = new URLSearchParams(window.location.search).get("source");
if (requestedSource) {{
  const matchIndex = sources.findIndex(source => source.path === requestedSource);
  if (matchIndex >= 0) {{
    const card = document.querySelector(`.source-card[data-source-index="${{matchIndex}}"]`);
    const checkbox = card && card.querySelector(".source-choice");
    if (checkbox && !checkbox.disabled) {{
      checkbox.checked = true;
      card.classList.add("is-deep-link");
      card.tabIndex = -1;
      card.focus();
      card.scrollIntoView({{behavior: "smooth", block: "center"}});
    }}
  }}
}}
refreshRecipes();
refreshSourceFilter();
refreshSelection();
renderResults();
</script>
</body>
</html>
"""


def _load_array(path, key):
    value = json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig"))
    if isinstance(value, dict):
        value = value.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{path} must contain a JSON array" + (f" or a {key} array" if key else ""))
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Absolute library root")
    parser.add_argument("--catalog", help="Optional recipe catalogue JSON override (array or {recipes: [...]})")
    parser.add_argument("--sources", help="Optional source JSON override (array or {sources: [...]})")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true", help="Render/validate without writing (default)")
    modes.add_argument("--apply", action="store_true", help="Write _generation/index.html")
    modes.add_argument("--check", action="store_true", help="Read-only compare with existing generated page")
    args = parser.parse_args(argv)
    try:
        root = pathlib.Path(args.root)
        if not root.is_absolute() or not root.is_dir():
            raise ValueError("--root must be an existing absolute directory")
        for parent in (root, *root.parents):
            if parent.is_symlink() or (hasattr(parent, "is_junction") and parent.is_junction()):
                raise ValueError(f"Linked root is not permitted: {parent}")
        root = root.resolve()
        sources = (_load_array(args.sources, "sources") if args.sources
                   else reference_execution.gallery_sources(root))
        recipes = (_load_array(args.catalog, "recipes") if args.catalog
                   else reference_execution.catalog())
        page = build_page(root, sources, recipes)
        output = root / OUTPUT_RELATIVE
        _reject_linked_path(root, output)
        if args.check:
            if not output.is_file():
                raise ValueError(f"Gallery page is missing: {output}")
            if output.read_text(encoding="utf-8") != page:
                raise ValueError(f"Gallery page is out of date: {output}")
            print(f"Gallery page is current: {output}")
        elif args.apply:
            output.parent.mkdir(parents=True, exist_ok=True)
            stage = None
            try:
                with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".render-gallery-",
                                                 suffix=".tmp", delete=False) as stream:
                    stage = pathlib.Path(stream.name)
                    stream.write(page.encode("utf-8"))
                report_assets.replace_file(stage, output)
            finally:
                if stage is not None and stage.exists():
                    stage.unlink()
            print(f"Wrote metadata-only gallery: {output}")
        else:
            print(f"Validated {len(sources)} sources and {len(recipes)} recipes; "
                  f"would write {output} ({len(page)} characters). No files changed.")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Reference gallery: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
