"""Offline, human-only comparison of explicitly selected frozen reference batches.

``publish(root, batch_ids, apply=False, check=False)`` previews without writing,
checks exact report currency read-only, or atomically publishes comparison.html.
No scoring, identity inference, selection, queue access or image derivatives.
"""
import html
import io
import pathlib
import re
import uuid

from PIL import Image

if __package__:
    from . import reference_rendering as base
    from . import reference_execution as execution
else:
    import reference_rendering as base
    import reference_execution as execution

from likeness_library import gallery_chrome

PAGE_RELATIVE = "_generation/comparison.html"
MAX_BATCHES = 32
MAX_JOBS = 2048
MAX_OUTPUTS = 4096
BATCH_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,47}$")


def _outputs(record, compiled_job, job, batch_id, job_id):
    """Verify receipt paths against the compiled namespace before reading bytes."""
    outputs = job.get("outputs", [])
    if not isinstance(outputs, list):
        raise ValueError(f"{batch_id}/{job_id}: malformed output inventory")
    if job["state"] == "completed" and not outputs:
        raise ValueError(f"{batch_id}/{job_id}: completed job has no output evidence")
    if len(outputs) > MAX_OUTPUTS:
        raise ValueError("Comparison output limit exceeded")
    root = execution.safe_root(record["outputRoot"])
    prefix = pathlib.PurePosixPath(compiled_job["prefix"])
    verified = []
    seen = set()
    for output in outputs:
        filename = output["filename"]
        subfolder = output.get("subfolder", "").replace("\\", "/")
        if (output.get("type") != "output" or "/" in filename or "\\" in filename
                or not filename.startswith(prefix.name + "_")
                or pathlib.PurePosixPath(subfolder) != prefix.parent):
            raise ValueError(f"{batch_id}/{job_id}: output is outside the compiled job namespace")
        relative = f"{subfolder}/{filename}" if subfolder else filename
        path = base.safe_path(root, relative)
        if str(path) != output["path"] or relative in seen:
            raise ValueError(f"{batch_id}/{job_id}: output path changed or duplicated")
        seen.add(relative)
        try:
            data = path.read_bytes()
        except OSError as error:
            raise ValueError(f"{batch_id}/{job_id}: missing/unreadable output: {path}") from error
        if base.digest(data) != output["sha256"]:
            raise ValueError(f"{batch_id}/{job_id}: output hash changed: {path}")
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        verified.append({"path": str(path), "uri": path.as_uri(), "sha256": output["sha256"]})
    return sorted(verified, key=lambda item: item["path"])


def _collect(root, batch_ids):
    rows = []
    receipts = {}
    output_count = 0
    for batch_id in batch_ids:
        run = base.check(root, batch_id)
        destination = base.run_path(root, batch_id)
        if (destination / "submission.lock").exists():
            raise ValueError(f"{batch_id}: execution writer is active; retry after it finishes")
        request = base.read_json(destination / "request.json")
        prepared = {job["id"]: job for job in run["jobs"]}
        compiled = record = None
        if (destination / "compiled.json").exists():
            _, compiled, record = execution.evidence(root, batch_id)
            receipts[batch_id] = (destination / "execution.json").read_bytes()
            if base.read_json(destination / "execution.json") != record:
                raise ValueError(f"{batch_id}: execution changed while reading")
            if set(compiled["jobs"]) != set(prepared):
                raise ValueError(f"{batch_id}: compiled/frozen job inventory differs")
        for job in request["jobs"]:
            frozen = prepared[job["id"]]
            state = frozen["state"]
            outputs = []
            error = ""
            if record is not None:
                compiled_job = compiled["jobs"][job["id"]]
                receipt = record["jobs"][job["id"]]
                for field in ("recipe", "seed", "displayName"):
                    if field in compiled_job and compiled_job[field] != job.get(field):
                        raise ValueError(f"{batch_id}/{job['id']}: compiled {field} differs from request")
                if compiled_job["inputSha256"] != frozen["sha256"]:
                    raise ValueError(f"{batch_id}/{job['id']}: compiled source differs from frozen input")
                state = receipt["state"]
                if not isinstance(state, str) or not state:
                    raise ValueError(f"{batch_id}/{job['id']}: missing execution state")
                outputs = _outputs(record, compiled_job, receipt, batch_id, job["id"])
                error = str(receipt.get("error", ""))
            output_count += len(outputs)
            if len(rows) >= MAX_JOBS or output_count > MAX_OUTPUTS:
                raise ValueError("Comparison job/output limit exceeded")
            source = job["source"]
            person_id = job.get("personId", "")
            name = job.get("displayName", "")
            # Missing IDs stay explicitly name-only/unassigned, never inferred.
            person_key = ("id", person_id) if person_id else ("name", name)
            source_key = (person_key, source["path"], source["sha256"],
                          source.get("kind", "photo"), source["domain"])
            rows.append({
                "personKey": person_key, "sourceKey": source_key,
                "personId": person_id, "displayName": name,
                "source": source, "sourceUri": base.safe_path(destination, frozen["input"]).as_uri(),
                "batch": batch_id, "job": job["id"], "recipe": job["recipe"],
                "profile": job["profile"], "mode": job["workflowMode"], "seed": job["seed"],
                "state": state, "error": error, "outputs": outputs,
            })
    return sorted(rows, key=lambda row: (
        row["personKey"], row["sourceKey"], row["recipe"], row["profile"],
        row["mode"], row["seed"], row["batch"], row["job"])), receipts


def _text(value):
    return html.escape(str(value), quote=True)


def _person(row):
    return (row["displayName"] or "Unnamed") + (
        f" · personId: {row['personId']}" if row["personId"] else " · no personId (name-only/unassigned)")


def _row(row):
    source = row["source"]
    source_label = ("Original photo input (frozen copy)" if source.get("kind", "photo") == "photo"
                    else f"Synthetic source — {source['kind']} (frozen copy)")
    pictures = "".join(
        f'<figure><a href="{_text(output["uri"])}" target="_blank" rel="noopener">'
        f'<img src="{_text(output["uri"])}" loading="lazy" alt="Synthetic completed render"></a>'
        f'<figcaption>Synthetic completed render<br><code>{_text(output["path"])}</code>'
        f'<br>SHA-256: <code>{output["sha256"]}</code></figcaption></figure>'
        for output in row["outputs"] if row["state"] == "completed")
    if not pictures:
        pictures = '<p class="state">No completed output. State: ' + _text(row["state"]) + "</p>"
    return (
        f'<article class="comparison-row" data-person="{_text(row["personKey"])}"'
        f' data-recipe="{_text(row["recipe"])}" data-state="{_text(row["state"])}">'
        f'<h3>{_text(_person(row))}</h3>'
        f'<p>Batch <code>{_text(row["batch"])}</code> / job <code>{_text(row["job"])}</code>'
        f' · State: <strong>{_text(row["state"])}</strong><br>'
        f'Recipe: <code>{_text(row["recipe"])}</code> · profile: {_text(row["profile"])}'
        f' · mode: {_text(row["mode"])} · seed: {row["seed"]}</p>'
        + (f'<p class="state">Receipt error: {_text(row["error"])}</p>' if row["error"] else "")
        + f'<div class="pair"><figure><a href="{_text(row["sourceUri"])}" target="_blank" rel="noopener">'
        f'<img src="{_text(row["sourceUri"])}" loading="lazy" alt="{_text(source_label)}"></a>'
        f'<figcaption>{_text(source_label)}<br>Original source path: <code>{_text(source["path"])}</code>'
        f'<br>SHA-256: <code>{source["sha256"]}</code><br>Domain: {_text(source["domain"])}'
        f'</figcaption></figure><div class="renders">{pictures}</div></div></article>'
    )


def _page(root, rows, batch_ids):
    source_groups = {}
    recipe_groups = {}
    for row in rows:
        source_groups.setdefault(row["sourceKey"], []).append(row)
        recipe_groups.setdefault((row["recipe"], row["profile"], row["mode"]), []).append(row)
    by_source = "".join(
        '<section class="comparison-group"><h2>' + _text(_person(group[0]))
        + '</h2><p>Exact source: <code>' + _text(group[0]["source"]["path"])
        + "</code> · SHA-256: <code>" + group[0]["source"]["sha256"] + "</code></p>"
        + "".join(_row(row) for row in group) + "</section>"
        for group in source_groups.values())
    by_recipe = "".join(
        '<section class="comparison-group"><h2>Matched recipe: ' + _text(key[0])
        + " · profile: " + _text(key[1]) + " · mode: " + _text(key[2])
        + '</h2><p>Same recipe/profile/mode across people; seeds and sources may differ. '
        'Not a controlled experiment or an identity comparison.</p><div class="matched-grid">'
        + "".join(_row(row) for row in group) + "</div></section>"
        for key, group in sorted(recipe_groups.items()))
    person_labels = {str(row["personKey"]): _person(row) for row in rows}

    def options(values):
        return "".join(f'<option value="{_text(key)}">{_text(label)}</option>'
                       for key, label in sorted(values.items()))

    cfg = execution.workflows.load_cfg()
    generation = execution.workflows.storage_root(cfg, "generation", root=root)
    reports = execution.workflows.storage_root(cfg, "reports", root=root)
    prefix = gallery_chrome.reports_prefix(generation, reports)
    section_links = gallery_chrome.configured_sections(root, cfg)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sovereign Territories — Source/render comparison</title><style>
{gallery_chrome.CSS}
.controls {{ display:flex; flex-wrap:wrap; gap:1rem; margin:1rem 0; }}
.controls label {{ display:grid; gap:.3rem; }}
.comparison-row {{ background:var(--st-card); border:1px solid var(--st-line);
border-radius:var(--st-radius); padding:1rem; margin:1rem 0; min-width:0; }}
.comparison-row p,figcaption {{ overflow-wrap:anywhere; }}
.pair {{ display:grid; grid-template-columns:minmax(180px,1fr) minmax(180px,2fr); gap:1rem; }}
figure {{ margin:0; min-width:0; }} figcaption {{ font-size:.8rem; }}
.renders {{ display:flex; flex-wrap:wrap; gap:1rem; }}
.renders figure {{ flex:1 1 200px; }}
.comparison-row img {{ width:100%; height:320px; object-fit:contain; background:#bebebe; }}
.matched-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:1rem; }}
.matched-grid .pair {{ grid-template-columns:1fr 1fr; }}
.state {{ font-weight:600; }} [hidden] {{ display:none !important; }}
@media(max-width:600px) {{ .pair,.matched-grid,.matched-grid .pair {{ grid-template-columns:1fr; }} }}
</style></head><body id="top">
{gallery_chrome.masthead(
    "Comparison", prefix, "Source/render comparison · human review only",
    section_links=section_links,
)}
<div class="site-page"><main><h1>Source/render comparison</h1>
<p>Explicit batches: <code>{_text(", ".join(batch_ids))}</code>. {len(rows)} jobs.
Frozen inputs and receipt-owned outputs only. Images are browser-scaled originals; no derivatives created.</p>
<p><strong>Human review only; partial R39/R41 support, not automated ranking.</strong>
Review technical quality, source fidelity and character resemblance separately.
Resemblance is not evidence of identity or kinship. Synthetic anatomy, unseen areas and poses
are generated, not recovered. No face scores, embeddings, identity claims or automatic selections.</p>
<div class="controls">
<label>View<select id="view"><option value="sources">Person and exact source</option>
<option value="recipes">Matched recipe across people</option></select></label>
<label>Person<select id="person"><option value="">All people</option>{options(person_labels)}</select></label>
<label>Recipe<select id="recipe"><option value="">All recipes</option>
{options({row["recipe"]: row["recipe"] for row in rows})}</select></label>
<label>State<select id="state"><option value="">All states</option>
{options({row["state"]: row["state"] for row in rows})}</select></label>
</div><p id="visible-count" role="status"></p>
<div id="sources">{by_source}</div><div id="recipes" hidden>{by_recipe}</div>
</main>
{gallery_chrome.footer("Read-only human comparison; no source, identity, family or queue changes.")}
</div><script>
const filters = ["person", "recipe", "state"];
function update() {{
  const active = document.getElementById("view").value;
  for (const id of ["sources", "recipes"]) {{
    const pane = document.getElementById(id);
    pane.hidden = id !== active;
    for (const row of pane.querySelectorAll(".comparison-row")) {{
      row.hidden = filters.some(key => {{
        const value = document.getElementById(key).value;
        return value && row.dataset[key] !== value;
      }});
    }}
    for (const group of pane.querySelectorAll(".comparison-group")) {{
      group.hidden = ![...group.querySelectorAll(".comparison-row")].some(row => !row.hidden);
    }}
  }}
  const count = [...document.getElementById(active).querySelectorAll(".comparison-row")]
    .filter(row => !row.hidden).length;
  document.getElementById("visible-count").textContent = count + " matching jobs";
}}
for (const id of ["view", ...filters]) document.getElementById(id).addEventListener("change", update);
update();
</script></body></html>
"""


def publish(root: pathlib.Path, batch_ids: list[str], apply=False, check=False):
    """Return page/current/sources/outputs/jobs counts; only apply writes a page."""
    if apply and check:
        raise ValueError("Choose apply or read-only check, not both")
    root = base.library_root(root)
    if (not isinstance(batch_ids, list) or not 1 <= len(batch_ids) <= MAX_BATCHES
            or any(not isinstance(value, str) or not BATCH_ID.fullmatch(value) for value in batch_ids)
            or len(set(batch_ids)) != len(batch_ids)):
        raise ValueError(f"Select 1..{MAX_BATCHES} unique explicit batch IDs")
    batch_ids = sorted(batch_ids)
    rows, receipts = _collect(root, batch_ids)
    payload = _page(root, rows, batch_ids).encode("utf-8")
    generation = execution.workflows.storage_root(
        execution.workflows.load_cfg(), "generation", root=root
    )
    target = generation / "comparison.html"
    current = target.is_file() and target.read_bytes() == payload
    if apply and not current:
        # Revalidate immediately before publication; execution may have advanced.
        refreshed, refreshed_receipts = _collect(root, batch_ids)
        if rows != refreshed or receipts != refreshed_receipts:
            raise ValueError("Reference evidence changed during comparison; retry")
        target.parent.mkdir(parents=True, exist_ok=True)
        pending = generation / f".comparison-{uuid.uuid4().hex}.pending"
        try:
            with pending.open("xb") as stream:
                stream.write(payload)
            base.report_assets.replace_file(pending, target)
        finally:
            if pending.exists():
                pending.unlink()
        current = True
    return {
        "page": str(target), "current": current, "applied": apply, "batches": batch_ids,
        "sources": len({row["sourceKey"] for row in rows}),
        "outputs": sum(len(row["outputs"]) for row in rows), "jobs": len(rows),
        "people": len({row["personKey"] for row in rows}),
        "states": {state: sum(row["state"] == state for row in rows)
                   for state in sorted({row["state"] for row in rows})},
    }
