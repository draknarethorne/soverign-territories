"""Scoped manual-Qwen pilot, not a general UI graph converter."""
import copy
import contextlib
import datetime
import io
import html.parser
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

from PIL import Image

if __package__:
    from . import reference_rendering as base
    from . import comfy_workflows as workflows
else:
    import reference_rendering as base
    import comfy_workflows as workflows

INSTALL = pathlib.Path(r"B:\Comfy-Desktop\ComfyUI-Installs\Sovereign Females\ComfyUI")
WORKFLOWS = INSTALL / "user" / "default" / "workflows"
RECIPES = {
    "manual-0c-cleanup-basic": ("0_Edit", "0c_Cleanup", "Angelica_Qwen_Edit_0c_Cleanup_Basic.json"),
    "manual-0c-cleanup": ("0_Edit", "0c_Cleanup", "Angelica_Qwen_Edit_0c_Cleanup.json"),
    "manual-0e-enhance": ("0_Edit", "0e_Enhance", "Angelica_Qwen_Edit_0e_Enhance.json"),
    "manual-0f-full": ("0_Edit", "0f_Full", "Angelica_Qwen_Edit_0f_Full.json"),
    "manual-0b-background-basic": ("0_Edit", "0b_Background", "Angelica_Qwen_Edit_0b_Background_Basic.json"),
    # The installed 0d graphs are "Bare" pose studies; only their graph/settings are reused and
    # the clothed-preservation prompt below replaces their prompt text.
    "manual-0d-deluxe-pose": ("0_Edit", "0d_Deluxe", "Angelica_Qwen_Edit_0d_Deluxe_Bare.json"),
    "shared-0b-background-basic": ("0_Edit", "0b_Background_Basic", "Angelica_Qwen_Edit_0b_Background_Basic.json"),
    "shared-0d-relaxed-three-quarter": ("0_Edit", "0d_Relaxed_Three_Quarter", "Angelica_Qwen_Edit_0d_Deluxe_Bare.json"),
    "shared-0d-grounded-three-quarter": ("0_Edit", "0d_Grounded_Three_Quarter", "Angelica_Qwen_Edit_0d_Deluxe_Bare.json"),
    "shared-0e-enhance-basic": ("0_Edit", "0e_Enhance_Basic", "Angelica_Qwen_Edit_0e_Enhance.json"),
    "shared-0f-full-clothed": ("0_Edit", "0f_Full_Clothed", "Angelica_Qwen_Edit_0f_Full.json"),
    "shared-1a-prime-outfit-relaxed": ("1_Alpha", "1_Prime", "Angelica_Qwen_Edit_0d_Deluxe_Bare.json"),
    "shared-1a-prime-outfit-grounded": ("1_Alpha", "1_Prime", "Angelica_Qwen_Edit_0d_Deluxe_Bare.json"),
    "shared-0d-deluxe-seated": ("0_Edit", "0d_Deluxe", "Angelica_Qwen_Edit_0d_Deluxe_Bare.json"),
    "shared-0d-deluxe-relaxing": ("0_Edit", "0d_Deluxe", "Angelica_Qwen_Edit_0d_Deluxe_Bare.json"),
    "shared-0d-deluxe-side-resting": ("0_Edit", "0d_Deluxe", "Angelica_Qwen_Edit_0d_Deluxe_Bare.json"),
    "shared-0d-deluxe-resting": ("0_Edit", "0d_Deluxe", "Angelica_Qwen_Edit_0d_Deluxe_Bare.json"),
    "shared-0c-cleanup-basic": ("0_Edit", "0c_Cleanup", "Angelica_Qwen_Edit_0c_Cleanup_Basic.json"),
}
SHARED_PROMPTS = {
    "shared-0b-background-basic": "0_Edit/background/Female_Edit_Background_Basic.txt",
    "shared-0d-relaxed-three-quarter": "0_Edit/pose/Female_Edit_Pose_Relaxed_Three_Quarter.txt",
    "shared-0d-grounded-three-quarter": "0_Edit/pose/Female_Edit_Pose_Grounded_Three_Quarter.txt",
    "shared-0e-enhance-basic": "0_Edit/enhance/Female_Edit_Enhance_Basic.txt",
    "shared-0f-full-clothed": "0_Edit/full/Female_Edit_Full_Clothed.txt",
    "shared-1a-prime-outfit-relaxed": "1_Alpha/1_Prime/Female_Alpha_1_Prime_Outfit_Relaxed.txt",
    "shared-1a-prime-outfit-grounded": "1_Alpha/1_Prime/Female_Alpha_1_Prime_Outfit_Grounded.txt",
    "shared-0d-deluxe-seated": "0_Edit/deluxe/Female_Edit_Deluxe_Clothed_Seated.txt",
    "shared-0d-deluxe-relaxing": "0_Edit/deluxe/Female_Edit_Deluxe_Clothed_Relaxing.txt",
    "shared-0d-deluxe-side-resting": "0_Edit/deluxe/Female_Edit_Deluxe_Clothed_Side_Resting.txt",
    "shared-0d-deluxe-resting": "0_Edit/deluxe/Female_Edit_Deluxe_Clothed_Resting.txt",
    "shared-0c-cleanup-basic": "0_Edit/cleanup/Female_Edit_Cleanup_Basic.txt",
}
SHARED_PROMPT_ROOT = base.ROOT / "prompts" / "angel-primes" / "alpha" / "Female"
ALLOWED = {
    "LoadImage", "SaveImage", "ModelSamplingAuraFlow", "VAELoader",
    "FluxKontextMultiReferenceLatentMethod", "TextEncodeQwenImageEditPlus",
    "CFGNorm", "LoraLoaderModelOnly", "PrimitiveFloat", "VAEEncode",
    "UNETLoader", "CLIPLoader", "ComfySwitchNode", "PrimitiveInt",
    "PrimitiveBoolean", "KSampler", "VAEDecode", "FluxKontextImageScale",
}
NOTES = {"Note", "MarkdownNote"}
MISSING = object()
QUEUE_CAPACITY = 200
MAX_RUN_JOBS = 64
MAX_QUEUE_DEPTH = 16
MAX_RUN_TIMEOUT = 21600


class PreflightPollUnavailable(TimeoutError):
    """A read-only submission check failed before any intent or POST."""


def pilot_prompts(recipe):
    if recipe in SHARED_PROMPTS:
        return shared_prompt(recipe)[1]
    common = (
        "Edit this photograph conservatively. Preserve the same person's face, expression, "
        "hair style and color, eye color, skin tone, visible body proportions, and existing clothing. "
        "Keep the person fully clothed in the same outfit. Preserve hands, fingers and feet that "
        "are visible, and do not crop limbs. Do not add people or redesign the person's body. "
        "Keep natural photographic skin texture. "
    )
    instructions = {
        "manual-0c-cleanup-basic": "Remove only text, watermarks, icons and screenshot borders. Keep the original background and pose.",
        "manual-0c-cleanup": "Remove distracting text, icons and background clutter. Use a simple neutral studio background; preserve the existing pose.",
        "manual-0e-enhance": "Improve exposure, neutral lighting and fine photographic detail modestly. Preserve the original background, framing and pose.",
        "manual-0f-full": "Create a head-to-toe full-length photograph on a neutral studio background, extending unseen areas conservatively in the same clothing. Preserve the pose and visible identity. Unseen areas are synthesized, not recovered.",
        "manual-0b-background-basic": "Replace only the background with a plain light-grey seamless studio backdrop and soft even lighting. Remove any text, icons or screen elements. Keep the person, clothing, pose and framing unchanged.",
        "manual-0d-deluxe-pose": "Show the same person in a new relaxed full-length standing fashion pose: weight on one leg, one hand resting on the hip, body turned slightly toward the camera, on a plain light-grey seamless studio backdrop. Same outfit, fully clothed. Remove any text, icons or screen elements.",
    }
    if recipe not in instructions:
        raise ValueError("No reviewed clothed pilot prompt for this recipe")
    return common + instructions[recipe], (
        "changed identity, changed hair color, changed eye color, changed skin tone, "
        "removed clothing, revealing outfit, distorted body, cropped hands, cropped feet, "
        "extra people, extra limbs, extra fingers, text, watermark, logo, plastic skin"
    )


def shared_prompt(recipe):
    path = SHARED_PROMPT_ROOT / SHARED_PROMPTS[recipe]
    text = path.read_text(encoding="utf-8")
    if "{{" in text or "}}" in text:
        raise ValueError(f"Unresolved shared prompt tokens: {path}; regenerate with bin\\prompts.cmd")
    return text, workflows.split_prompt(text)


def reference_paths(job, batch_id, stamp):
    person = slug(job["displayName"])
    stage, variant, _ = RECIPES[job["recipe"]]
    family = "0d_Deluxe" if job["recipe"].startswith("shared-0d-") else variant
    recipe_name = job["recipe"].split("-", 1)[1].replace("-", "_")
    operation = "Alpha" if stage == "1_Alpha" else "Edit"
    stem = f"{person}_Qwen_{operation}_{recipe_name}__{stamp}__{batch_id}__{job['id']}"
    prefix = f"reference/{person}/{stage}/{family}/{stem}"
    return prefix, prefix + ".json"


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def atomic_json(path, value):
    temporary = path.with_name(path.name + ".pending")
    with temporary.open("xb") as stream:
        stream.write(base.encode(value))
    base.report_assets.replace_file(temporary, path)


@contextlib.contextmanager
def receipt_lock(destination, operation):
    lock = destination / "submission.lock"
    try:
        stream = lock.open("x")
    except FileExistsError as error:
        raise ValueError(f"Execution metadata is locked: {lock}; verify the active writer before retrying") from error
    with stream:
        json.dump({"operation": operation, "pid": os.getpid(), "createdAt": now()}, stream)
    try:
        yield
    finally:
        lock.unlink()


def owned_write(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Refusing to replace different bytes: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def connection(endpoint):
    parsed = urllib.parse.urlsplit(endpoint)
    if (parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "::1"}
            or not parsed.port or parsed.username or parsed.password
            or parsed.path not in {"", "/"} or parsed.query or parsed.fragment):
        raise ValueError("Execution requires explicit HTTP loopback IP/port, no credentials or path")
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), base.NoRedirect())


def post_json(opener, endpoint, route, value):
    request = urllib.request.Request(endpoint.rstrip("/") + route, data=base.encode(value),
                                     headers={"Content-Type": "application/json"}, method="POST")
    with opener.open(request, timeout=30) as response:
        data = response.read(2 * 1024 * 1024 + 1)
    if len(data) > 2 * 1024 * 1024:
        raise ValueError("Submission response exceeds limit; reconcile before retry")
    result = json.loads(data)
    if not isinstance(result, dict):
        raise ValueError("Malformed submission reply; reconcile before retry")
    return result


def safe_root(value):
    return base.library_root(value)


def slug(value):
    text = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")[:64]
    if not text:
        raise ValueError("Displayed subject name cannot form an output filename")
    base.safe_path(pathlib.Path.cwd(), text)
    return text


def recipe_path(recipe):
    if recipe not in RECIPES:
        raise ValueError(f"Unsupported pilot recipe: {recipe}")
    matches = list((WORKFLOWS / "zz_shots").rglob(RECIPES[recipe][2]))
    if len(matches) != 1:
        raise ValueError(f"Expected one exact manual recipe: {recipe}, found {len(matches)}")
    relative = matches[0].relative_to(WORKFLOWS).as_posix()
    return base.safe_path(WORKFLOWS, relative)


def catalog():
    entries = []
    for recipe, (stage, variant, _) in RECIPES.items():
        label = variant + (" Basic" if recipe.endswith("-basic") and not variant.lower().endswith("basic") else "")
        if recipe.startswith("shared-1a-prime-outfit-"):
            label = "Prime outfit " + recipe.rsplit("-", 1)[1] + " (clothed)"
        elif recipe.startswith("shared-0d-deluxe-"):
            label = "Deluxe bedroom " + recipe.removeprefix("shared-0d-deluxe-") + " (clothed)"
        try:
            path = recipe_path(recipe)
            if recipe in SHARED_PROMPTS:
                shared_prompt(recipe)
            entries.append({"id": recipe, "label": label, "stage": stage,
                            "available": True, "sha256": base.digest(path.read_bytes())})
        except (ValueError, OSError) as error:
            entries.append({"id": recipe, "label": label, "stage": stage,
                            "available": False, "reason": str(error)})
    for stage, label in (("1_Alpha", "A-pose"),
                         ("2_Studies", "Studies"), ("Bench", "Optional diagnostics")):
        entries.append({"id": "pending-" + slug(label).lower(), "label": label,
                        "stage": stage, "available": False,
                        "reason": "Not bound/reviewed for the clothed manual pilot"})
    return entries


CLEANUP_HINTS = {
    "needs-cleanup": "Overlay detected that intake left in place for ComfyUI",
    "repainted": "LaMa repainted clutter during intake; review the repaint",
    "enhancement-failed": "Enhancement failed during intake; the original was kept",
}


def cleanup_hint(evidence):
    """Map published intake preparation evidence to an optional ComfyUI cleanup hint."""
    if not isinstance(evidence, dict) or evidence.get("state") not in {"verified", "ambiguous"}:
        return None
    hints = set()
    for match in evidence.get("matches") or []:
        if not isinstance(match, dict):
            continue
        treatment = str(match.get("treatment", ""))
        decision = str(match.get("decision", ""))
        if decision.startswith("eraser"):
            hints.add("repainted")
        elif treatment.endswith("overlay-unremoved"):
            hints.add("needs-cleanup")
        if treatment == "original-enhancement-failed":
            hints.add("enhancement-failed")
    for hint in CLEANUP_HINTS:
        if hint in hints:
            return hint
    return None


def gallery_sources(root):
    """Use the Gallery's name/identity presentation, not a filename-based identity guess."""
    report = base.safe_path(root, "_reports/library/people_gallery_review.html")
    if not report.is_file():
        raise ValueError("Publish People Photo Review first; no authoritative source/name inventory exists")

    class ReviewData(html.parser.HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.active = False
            self.chunks = []
            self.count = 0

        def handle_starttag(self, tag, attrs):
            if tag == "script" and dict(attrs).get("id") == "review-data":
                self.active = True
                self.count += 1

        def handle_endtag(self, tag):
            if tag == "script":
                self.active = False

        def handle_data(self, data):
            if self.active:
                self.chunks.append(data)
    parser = ReviewData()
    parser.feed(report.read_text(encoding="utf-8-sig"))
    if parser.count != 1:
        raise ValueError("Photo Review must contain one supported source inventory")
    records = json.loads("".join(parser.chunks))
    if not isinstance(records, list):
        raise ValueError("Photo Review source inventory is malformed")
    sources = {}
    for item in records:
        if item.get("bucket") not in {"Gallery", "Review"}:
            continue
        folder, name = item.get("folder"), item.get("name")
        if not isinstance(folder, str) or not isinstance(name, str):
            raise ValueError("Photo Review source lacks folder/name")
        relative = item.get("generationSource")
        if relative is None:
            href = urllib.parse.urlsplit(item.get("href", ""))
            if href.netloc or not href.path or href.scheme not in {"", "file"}:
                raise ValueError("Photo Review lacks a supported local source link; republish it")
            if href.scheme == "file":
                linked = pathlib.Path(urllib.request.url2pathname(href.path)).resolve()
            else:
                linked = (report.parent / urllib.parse.unquote(href.path)).resolve()
            relative = linked.relative_to(root.resolve()).as_posix()
        path = base.safe_path(root, relative)
        if not path.is_file():
            raise ValueError(f"Photo Review is stale; republish missing source: {relative}")
        data = path.read_bytes()
        sha = base.digest(data)
        if item.get("contentSha256") and item["contentSha256"] != sha:
            raise ValueError(f"Photo Review hash is stale; republish source: {relative}")
        names = item.get("identityNames") or {}
        displayed = names.get("characterName") or names.get("currentPersonName") or folder.split("/")[-1]
        source = {"path": relative, "sha256": sha, "domain": "general", "displayName": displayed}
        if item.get("personId"):
            source["personId"] = item["personId"]
        hint = cleanup_hint(item.get("preparationEvidence"))
        if hint:
            source["cleanup"] = hint
        sources[relative] = source
    selected_root = base.safe_path(root, "_generation/selected")
    if selected_root.exists():
        for metadata in sorted(selected_root.glob("*/*/*.json")):
            image = metadata.with_suffix("")
            relative = image.relative_to(root).as_posix()
            base.safe_path(root, metadata.relative_to(root).as_posix())
            record = base.read_json(metadata)
            source = {"path": relative, "kind": "selected-render", "sha256": record["sha256"],
                      "domain": record.get("domain", "general")}
            base.inspect_source(root, {"source": source})
            result = {**source, "displayName": record["displayName"]}
            if record.get("personId"):
                result["personId"] = record["personId"]
            sources[relative] = result
    library = root / "_generation" / "library"
    if library.is_dir():
        for metadata in sorted(library.glob("*/*/*.json")):
            relative = metadata.with_suffix("").relative_to(root).as_posix()
            base.safe_path(root, metadata.relative_to(root).as_posix())
            record = base.read_json(metadata)
            source = {"path": relative, "kind": "pulled-render", "sha256": record["sha256"],
                      "domain": record.get("domain", "general")}
            base.inspect_source(root, {"source": source})
            result = {**source, "displayName": record["displayName"]}
            if record.get("personId"):
                result["personId"] = record["personId"]
            sources[relative] = result
    return sorted(sources.values(), key=lambda item: (item["displayName"].casefold(), item["path"]))


def widget_values(node):
    fields = [item["name"] for item in node.get("inputs", []) if item.get("widget")]
    values = list(node.get("widgets_values", []))
    if node["type"] == "KSampler":
        if len(values) != len(fields) + 1 or values[1] not in {"fixed", "randomize", "increment", "decrement"}:
            raise ValueError("Unsupported KSampler widget serialization")
        values.pop(1)
    elif node["type"] == "PrimitiveInt":
        if len(values) != 2 or values[1] not in {"fixed", "randomize", "increment", "decrement"}:
            raise ValueError("Unsupported PrimitiveInt widget serialization")
        values.pop(1)
    elif node["type"] == "LoadImage":
        return {"image": values[0]}
    if len(fields) != len(values):
        raise ValueError(f"Unsupported widget serialization for {node['type']}")
    return dict(zip(fields, values))


def compile_ui(workflow, source, prefix, seed):
    """Only the inspected single-subgraph Qwen edit topology is supported."""
    ui = copy.deepcopy(workflow)
    definitions = ui.get("definitions", {}).get("subgraphs", [])
    if len(definitions) != 1:
        raise ValueError("Pilot requires exactly one Qwen subgraph")
    subgraph = definitions[0]
    outer = [node for node in ui["nodes"] if node["type"] not in NOTES]
    groups = [node for node in outer if node["type"] == subgraph["id"]]
    loaders = [node for node in outer if node["type"] == "LoadImage"]
    savers = [node for node in outer if node["type"] == "SaveImage"]
    if len(groups) != 1 or len(loaders) != 1 or len(savers) != 1 or len(outer) != 3:
        raise ValueError("Pilot requires one input, one subgraph and one output")
    group, loader, saver = groups[0], loaders[0], savers[0]
    loader["widgets_values"][0] = source
    saver["widgets_values"][0] = prefix
    group_fields = [item["name"] for item in group["inputs"] if item.get("widget")]
    if "seed" not in group_fields:
        raise ValueError("Manual graph lacks exposed seed")
    group["widgets_values"][group_fields.index("seed")] = seed
    outer_values = widget_values(group)
    top_links = {link[0]: link for link in ui["links"]}
    nodes = {node["id"]: node for node in subgraph["nodes"] if node["type"] not in NOTES}
    links = {link["id"]: link for link in subgraph["links"]}
    if len(nodes) != len([node for node in subgraph["nodes"] if node["type"] not in NOTES]):
        raise ValueError("Duplicate internal node IDs")
    for node in [*nodes.values(), loader, saver, group]:
        if node.get("mode", 0) != 0:
            raise ValueError("Bypassed/muted graph nodes are not supported")
    if any(node["type"] not in ALLOWED for node in nodes.values()):
        raise ValueError("Graph contains an unreviewed node class")
    graph = {}
    for node in nodes.values():
        values = widget_values(node)
        inputs = {}
        for item in node.get("inputs", []):
            value = values.get(item["name"], MISSING)
            if item.get("link") is not None:
                link = links[item["link"]]
                if link["target_id"] != node["id"]:
                    raise ValueError("Subgraph link target mismatch")
                if link["origin_id"] == -10:
                    exposed = group["inputs"][link["origin_slot"]]
                    if exposed.get("link") is not None:
                        top = top_links[exposed["link"]]
                        if top[1] != loader["id"] or top[2] != 0:
                            raise ValueError("Only the exact selected image may feed the pilot")
                        value = ["input", 0]
                    else:
                        value = outer_values.get(exposed["name"], MISSING)
                else:
                    if link["origin_id"] not in nodes:
                        raise ValueError("Unsupported internal link")
                    value = [str(link["origin_id"]), link["origin_slot"]]
            if value is not MISSING:
                inputs[item["name"]] = value
        graph[str(node["id"])] = {"class_type": node["type"], "inputs": inputs}
    output_links = subgraph["outputs"][0].get("linkIds", [])
    if len(subgraph["outputs"]) != 1 or len(output_links) != 1:
        raise ValueError("Unsupported subgraph output")
    output = links[output_links[0]]
    save_link = top_links[saver["inputs"][0]["link"]]
    if save_link[1] != group["id"] or save_link[2] != 0:
        raise ValueError("SaveImage is not bound to the reviewed subgraph output")
    graph["input"] = {"class_type": "LoadImage", "inputs": {"image": source}}
    graph["save"] = {"class_type": "SaveImage", "inputs": {
        "images": [str(output["origin_id"]), output["origin_slot"]], "filename_prefix": prefix}}
    # Discard disconnected diagnostic nodes just as execution from SaveImage does.
    reachable = set()

    def visit(key):
        if key in reachable:
            return
        if key not in graph:
            raise ValueError(f"Missing API node: {key}")
        reachable.add(key)
        for value in graph[key]["inputs"].values():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
                visit(value[0])
    visit("save")
    return ui, {key: value for key, value in graph.items() if key in reachable}


def validate_graph(graph, objects):
    for key, node in graph.items():
        info = objects.get(node["class_type"])
        if info is None:
            raise ValueError(f"Missing server node: {node['class_type']}")
        fields = info.get("input", {})
        required = fields.get("required", {})
        optional = fields.get("optional", {})
        if set(required) - node["inputs"].keys():
            raise ValueError(f"Missing required inputs at {key}: {set(required) - node['inputs'].keys()}")
        for name, value in node["inputs"].items():
            if name not in required and name not in optional:
                raise ValueError(f"Unknown server input {node['class_type']}.{name}")
            spec = (required | optional)[name]
            linked = isinstance(value, list) and len(value) == 2 and isinstance(value[0], str)
            # LoadImage's dynamic list is captured before the exact input copy;
            # its bytes/path are checked locally and then by server submission.
            dynamic_image = node["class_type"] == "LoadImage" and name == "image"
            if isinstance(spec[0], list) and not linked and not dynamic_image and value not in spec[0]:
                raise ValueError(f"Unavailable model/choice at {node['class_type']}.{name}: {value}")


def compile_batch(root, batch_id, endpoint, input_root, output_root, apply=False):
    run = base.check(root, batch_id)
    destination = base.run_path(root, batch_id)
    request = base.read_json(destination / "request.json")
    if request["workspace"] != "Sovereign Females":
        raise ValueError("Pilot only deploys to Sovereign Females")
    inputs, outputs = safe_root(input_root), safe_root(output_root)
    if (destination / "compiled.json").is_file():
        existing = base.read_json(destination / "compiled.json")
        if (existing["endpoint"] != endpoint.rstrip("/") or existing["inputRoot"] != str(inputs)
                or existing["outputRoot"] != str(outputs)):
            raise ValueError("Compiled batch already owns different server roots or endpoint")
        return existing
    probe = base.probe_server(endpoint, str(inputs), str(outputs))
    if probe["blockers"]:
        raise ValueError("; ".join(probe["blockers"]))
    opener = connection(endpoint)
    objects = base.server_json(opener, endpoint, "/object_info")
    stamp = datetime.datetime.fromtimestamp(
        (destination / "request.json").stat().st_mtime, datetime.timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")
    artifacts = {}
    staged_inputs = {}
    jobs = {}
    for job in request["jobs"]:
        if job["workflowMode"] != "reference" or job["profile"] != "reference-faithful":
            raise ValueError("Manual pilot supports only reference-faithful; character/profile compilation is pending")
        if not job.get("displayName"):
            raise ValueError("Executable jobs require the Gallery displayName")
        path = recipe_path(job["recipe"])
        frozen = path.read_bytes()
        workflow = json.loads(frozen)
        definitions = workflow.get("definitions", {}).get("subgraphs", [])
        if len(definitions) != 1:
            raise ValueError("Pilot requires one reviewed subgraph")
        group = next((node for node in workflow["nodes"]
                      if node["type"] == definitions[0]["id"]), None)
        if group is None:
            raise ValueError("Manual prompt binding is missing")
        fields = [item["name"] for item in group["inputs"] if item.get("widget")]
        if not {"prompt", "prompt_1"} <= set(fields):
            raise ValueError("Pilot prompt binding has changed")
        prompt_text = None
        if job["recipe"] in SHARED_PROMPTS:
            prompt_text, (positive, negative) = shared_prompt(job["recipe"])
        else:
            positive, negative = pilot_prompts(job["recipe"])
        group["widgets_values"][fields.index("prompt")] = positive
        group["widgets_values"][fields.index("prompt_1")] = negative
        stage, variant, _ = RECIPES[job["recipe"]]
        prepared = next(value for value in run["jobs"] if value["id"] == job["id"])
        data = base.safe_path(destination, prepared["input"]).read_bytes()
        input_relative = f"reference/{batch_id}/{job['id']}/{pathlib.PurePosixPath(prepared['input']).name}"
        prefix, workflow_relative = reference_paths(job, batch_id, stamp)
        output_path = base.safe_path(outputs, prefix + "_00001_.png")
        workflow_path = base.safe_path(WORKFLOWS, workflow_relative)
        if max(len(str(output_path)), len(str(workflow_path))) >= 240:
            raise ValueError("Planned output path is too long for the pilot; shorten batch/job IDs or display label")
        ui, graph = compile_ui(workflow, input_relative, prefix, job["seed"])
        validate_graph(graph, objects)
        files = {
            f"jobs/{job['id']}/manual-source.json": frozen,
            f"jobs/{job['id']}/workflow-ui.json": base.encode(ui),
            f"jobs/{job['id']}/workflow-api.json": base.encode(graph),
        }
        if prompt_text is not None:
            files[f"jobs/{job['id']}/prompt-source.txt"] = prompt_text.encode("utf-8")
        artifacts.update(files)
        jobs[job["id"]] = {
            "state": "compiled", "displayName": job["displayName"], "recipe": job["recipe"],
            "stage": stage, "variant": variant, "seed": job["seed"], "prefix": prefix,
            "workspaceWorkflow": workflow_relative, "namingPolicy": "person-first-v2",
            "input": input_relative, "inputSha256": base.digest(data),
            "manualSource": str(path), "manualSha256": base.digest(frozen),
            "promptPolicy": ("shared-clothed-reference-v1" if prompt_text is not None
                             else "clothed-preservation-pilot-v1"),
            "promptOverride": ("Generated shared prompt replaces manual text; source graph/settings retained"
                               if prompt_text is not None else
                               "Neutral preservation prompts replace manual body/color/clothing conflicts; source graph/settings retained"),
            "artifacts": {name: base.digest(value) for name, value in files.items()}, "outputs": [],
        }
        staged_inputs[input_relative] = data
    evidence = {"schemaVersion": 1, "batchId": batch_id, "endpoint": endpoint.rstrip("/"),
                "inputRoot": str(inputs), "outputRoot": str(outputs), "jobs": jobs}
    if apply:
        for relative, data in staged_inputs.items():
            owned_write(base.safe_path(inputs, relative), data)
        compiled = destination / "compiled.json"
        owned_write(compiled, base.encode(evidence))
        for relative, data in artifacts.items():
            owned_write(base.safe_path(destination, relative), data)
        for job in request["jobs"]:
            relative = jobs[job["id"]]["workspaceWorkflow"]
            owned_write(base.safe_path(WORKFLOWS, relative),
                        artifacts[f"jobs/{job['id']}/workflow-ui.json"])
        execution = destination / "execution.json"
        if not execution.exists():
            owned_write(execution, base.encode(evidence))
    return evidence


def evidence(root, batch_id):
    destination = base.run_path(root, batch_id)
    compiled = base.read_json(base.safe_path(destination, "compiled.json"))
    if compiled["batchId"] != batch_id:
        raise ValueError("Compiled batch ID mismatch")
    for job in compiled["jobs"].values():
        for relative, sha in job["artifacts"].items():
            if base.digest(base.safe_path(destination, relative).read_bytes()) != sha:
                raise ValueError(f"Compiled artifact changed: {relative}")
        input_path = base.safe_path(safe_root(compiled["inputRoot"]), job["input"])
        if base.digest(input_path.read_bytes()) != job["inputSha256"]:
            raise ValueError("Staged ComfyUI input changed")
    execution = base.read_json(base.safe_path(destination, "execution.json"))
    for field in ("batchId", "endpoint", "inputRoot", "outputRoot"):
        if execution[field] != compiled[field]:
            raise ValueError(f"Execution target changed: {field}")
    if execution["jobs"].keys() != compiled["jobs"].keys():
        raise ValueError("Execution job inventory changed")
    for key, job in compiled["jobs"].items():
        for field in ("prefix", "input", "artifacts", "inputSha256"):
            if execution["jobs"][key][field] != job[field]:
                raise ValueError(f"Execution binding changed: {key}/{field}")
    return destination, compiled, execution


def queue_items(queue):
    return list(queue.get("queue_running") or []) + list(queue.get("queue_pending") or [])


def foreign_items(queue, owned_prompts=()):
    owned = set(owned_prompts)
    return [item for item in queue_items(queue)
            if not (isinstance(item, list) and len(item) > 1 and item[1] in owned)]


def submit(root, batch_id, job_id, apply=False, *, allow_busy_queue=False, owned_prompts=()):
    destination, compiled, execution = evidence(root, batch_id)
    if job_id not in execution["jobs"]:
        raise ValueError("Select an existing job ID")
    job = execution["jobs"][job_id]
    if job["state"] != "compiled":
        raise ValueError(f"Job is {job['state']}; never blindly resubmit")
    endpoint = execution["endpoint"]
    opener = connection(endpoint)
    try:
        probe = base.probe_server(endpoint, execution["inputRoot"], execution["outputRoot"])
        if probe["blockers"]:
            raise ValueError("; ".join(probe["blockers"]))
        queue = base.server_json(opener, endpoint, "/queue")
        if len(queue_items(queue)) + 1 > QUEUE_CAPACITY:
            raise ValueError(f"Server queue is at its {QUEUE_CAPACITY}-job capacity; wait, never cancel other jobs")
        if not allow_busy_queue and foreign_items(queue, owned_prompts):
            raise ValueError("Server queue is occupied; wait without cancelling unrelated jobs")
        graph = base.read_json(destination / "jobs" / job_id / "workflow-api.json")
        validate_graph(graph, base.server_json(opener, endpoint, "/object_info"))
    except (TimeoutError, urllib.error.URLError) as error:
        if isinstance(error, urllib.error.HTTPError):
            raise
        raise PreflightPollUnavailable(f"Read-only submission preflight unavailable: {error}") from error
    if not apply:
        return {"state": "submission-preview", "job": job_id, "prefix": job["prefix"],
                "queuePolicy": "append-one" if allow_busy_queue else "wait-idle"}
    with receipt_lock(destination, f"submit:{job_id}"):
        # Persist intent before POST. Any crash after this point holds resubmission.
        latest = base.read_json(destination / "execution.json")
        if latest != execution:
            raise ValueError("Execution changed before submission")
        job["state"] = "submission-uncertain"
        job["submissionIntentAt"] = now()
        job["clientId"] = uuid.uuid4().hex
        job["queuePolicy"] = "append-one" if allow_busy_queue else "wait-idle"
        atomic_json(destination / "execution.json", execution)
        try:
            reply = post_json(opener, endpoint, "/prompt", {
                "prompt": graph, "client_id": job["clientId"],
                "extra_data": {"extra_pnginfo": {"reference_batch": batch_id, "reference_job": job_id}},
            })
        except urllib.error.HTTPError as error:
            if error.code == 400:
                job["state"] = "rejected"
                job["error"] = error.read(64 * 1024).decode("utf-8", errors="replace")
                atomic_json(destination / "execution.json", execution)
            raise
        except (OSError, ValueError) as error:
            job["error"] = f"Submission uncertain: {error}; reconcile before any retry"
            atomic_json(destination / "execution.json", execution)
            raise
        if not isinstance(reply.get("prompt_id"), str) or reply.get("node_errors"):
            job["error"] = json.dumps(reply)
            atomic_json(destination / "execution.json", execution)
            raise ValueError("Submission reply requires reconciliation; not resubmitting")
        job.update(state="queued", promptId=reply["prompt_id"], submittedAt=now())
        atomic_json(destination / "execution.json", execution)
    return job


def status(root, batch_id, refresh=False):
    if not refresh:
        return evidence(root, batch_id)[2]
    with receipt_lock(base.run_path(root, batch_id), "status-refresh"):
        destination, _, execution = evidence(root, batch_id)
        opener = connection(execution["endpoint"])
        for job_id, job in execution["jobs"].items():
            if job["state"] not in {"queued", "running"}:
                continue
            history = base.server_json(opener, execution["endpoint"], "/history/" + urllib.parse.quote(job["promptId"], safe=""))
            result = history.get(job["promptId"])
            if result is None:
                queue = base.server_json(opener, execution["endpoint"], "/queue")
                running = any(item[1] == job["promptId"] for item in queue.get("queue_running", []))
                pending = any(item[1] == job["promptId"] for item in queue.get("queue_pending", []))
                job["state"] = "running" if running else "queued"
                if not running and not pending:
                    job["state"] = "history-missing"
                    job["error"] = "Server lost prompt history/queue entry; reconcile manually, do not resubmit"
                continue
            state = result.get("status", {})
            if state.get("status_str") == "error":
                job.update(state="failed", error=json.dumps(state.get("messages", [])))
                continue
            if not state.get("completed"):
                continue
            outputs = []
            for output in result.get("outputs", {}).values():
                for image in output.get("images", []):
                    if image.get("type") != "output":
                        raise ValueError("Unexpected non-output history image")
                    subfolder = image.get("subfolder", "").replace("\\", "/")
                    relative = (subfolder.rstrip("/") + "/" + image["filename"]).lstrip("/")
                    parent = pathlib.PurePosixPath(job["prefix"]).parent.as_posix()
                    if pathlib.PurePosixPath(relative).parent.as_posix() != parent:
                        raise ValueError("Server returned an output outside this job namespace")
                    if not image["filename"].startswith(pathlib.PurePosixPath(job["prefix"]).name + "_"):
                        raise ValueError("Returned filename does not belong to selected subject/job")
                    path = base.safe_path(safe_root(execution["outputRoot"]), relative)
                    data = path.read_bytes()
                    with Image.open(io.BytesIO(data)) as picture:
                        picture.verify()
                    outputs.append({**image, "subfolder": subfolder,
                                    "serverSubfolder": image.get("subfolder", ""),
                                    "path": str(path), "sha256": base.digest(data)})
            if not outputs:
                job.update(state="failed", error="Completed prompt returned no owned output images")
            else:
                job.update(state="completed", outputs=outputs, completedAt=now())
        atomic_json(destination / "execution.json", execution)
        return execution


def run_batch(root, batch_id, apply=False, limit=4, timeout=3600, interval=10, *,
              allow_busy_queue=False, queue_depth=1):
    if (not 1 <= limit <= MAX_RUN_JOBS or not 1 <= interval <= 60 or not 1 <= timeout <= MAX_RUN_TIMEOUT
            or not 1 <= queue_depth <= MAX_QUEUE_DEPTH):
        raise ValueError(f"Run requires limit 1..{MAX_RUN_JOBS}, queue depth 1..{MAX_QUEUE_DEPTH}, "
                         f"interval 1..60s, timeout 1..{MAX_RUN_TIMEOUT}s")
    _, _, record = evidence(root, batch_id)
    if len(record["jobs"]) > limit:
        raise ValueError("Batch exceeds explicit run limit; reduce selections or raise --limit")
    policy = "append-one" if allow_busy_queue else "wait-idle"
    if not apply:
        return {"state": "run-preview", "batchId": batch_id, "jobs": list(record["jobs"]),
                "limit": limit, "timeoutSeconds": timeout, "queueDepth": queue_depth,
                "queueCapacity": QUEUE_CAPACITY, "queuePolicy": policy}
    deadline = time.monotonic() + timeout
    if queue_depth > 1:
        return _run_pipelined(root, batch_id, deadline, interval, queue_depth, allow_busy_queue)
    for job_id in record["jobs"]:
        while True:
            if time.monotonic() >= deadline:
                raise TimeoutError("Run deadline reached; receipts retained, no cancellation or resubmission")
            try:
                current = status(root, batch_id, True)
                state = current["jobs"][job_id]["state"]
                queue = (base.server_json(connection(current["endpoint"]), current["endpoint"], "/queue")
                         if state == "compiled" else {})
            except (TimeoutError, urllib.error.URLError) as error:
                if isinstance(error, urllib.error.HTTPError):
                    raise
                print(f"{now()} Read-only server poll unavailable: {error}; retrying within run deadline",
                      flush=True)
                time.sleep(interval)
                continue
            print(f"{now()} {job_id}: {state}", flush=True)
            if state == "completed":
                break
            if state == "compiled":
                if len(queue_items(queue)) + 1 > QUEUE_CAPACITY:
                    print(f"{now()} Server queue at its {QUEUE_CAPACITY}-job capacity; waiting", flush=True)
                elif allow_busy_queue or (not queue.get("queue_running") and not queue.get("queue_pending")):
                    if time.monotonic() >= deadline:
                        raise TimeoutError("Run deadline reached before submission; no POST made")
                    try:
                        if allow_busy_queue:
                            submit(root, batch_id, job_id, True, allow_busy_queue=True)
                        else:
                            submit(root, batch_id, job_id, True)
                    except PreflightPollUnavailable as error:
                        print(f"{now()} {error}; no POST made; retrying within run deadline", flush=True)
                else:
                    print(f"{now()} Waiting for existing server queue: "
                          f"{len(queue.get('queue_running', []))} running, "
                          f"{len(queue.get('queue_pending', []))} pending", flush=True)
            elif state not in {"queued", "running"}:
                raise ValueError(f"Job held in {state}; review receipt before continuing")
            time.sleep(interval)
    return status(root, batch_id)


def _run_pipelined(root, batch_id, deadline, interval, depth, allow_busy_queue):
    """Keep up to `depth` owned jobs at the normal queue tail; never cancel or reorder."""
    while True:
        if time.monotonic() >= deadline:
            raise TimeoutError("Run deadline reached; receipts retained, no cancellation or resubmission")
        try:
            current = status(root, batch_id, True)
            queue = base.server_json(connection(current["endpoint"]), current["endpoint"], "/queue")
        except (TimeoutError, urllib.error.URLError) as error:
            if isinstance(error, urllib.error.HTTPError):
                raise
            print(f"{now()} Read-only server poll unavailable: {error}; retrying within run deadline", flush=True)
            time.sleep(interval)
            continue
        jobs = current["jobs"]
        held = {key: job["state"] for key, job in jobs.items()
                if job["state"] not in {"compiled", "queued", "running", "completed"}}
        if held:
            raise ValueError(f"Jobs held {held}; review receipts before continuing")
        if all(job["state"] == "completed" for job in jobs.values()):
            return status(root, batch_id)
        owned = {job["promptId"] for job in jobs.values()
                 if job["state"] in {"queued", "running"} and job.get("promptId")}
        total = len(queue_items(queue))
        counts = {state: sum(job["state"] == state for job in jobs.values())
                  for state in ("compiled", "queued", "running", "completed")}
        print(f"{now()} {batch_id}: {counts}; server queue {total}/{QUEUE_CAPACITY}", flush=True)
        for job_id in [key for key, job in jobs.items() if job["state"] == "compiled"]:
            if len(owned) >= depth:
                break
            if not allow_busy_queue and foreign_items(queue, owned):
                print(f"{now()} Waiting for other server jobs to finish", flush=True)
                break
            if total + 1 > QUEUE_CAPACITY:
                print(f"{now()} Server queue at capacity; waiting", flush=True)
                break
            if time.monotonic() >= deadline:
                raise TimeoutError("Run deadline reached before submission; no POST made")
            try:
                submitted = submit(root, batch_id, job_id, True, allow_busy_queue=allow_busy_queue,
                                   owned_prompts=owned)
            except PreflightPollUnavailable as error:
                print(f"{now()} {error}; no POST made; retrying within run deadline", flush=True)
                break
            owned.add(submitted["promptId"])
            total += 1
        time.sleep(interval)


def reconcile(root, batch_id, job_id, apply=False):
    destination, _, record = evidence(root, batch_id)
    if (destination / "submission.lock").exists():
        raise ValueError("Submission is in progress; do not reconcile concurrently")
    job = record["jobs"].get(job_id)
    if not job or job["state"] not in {"submission-uncertain", "history-missing"}:
        raise ValueError("Reconcile requires one uncertain or history-missing job")
    endpoint = record["endpoint"]
    opener = connection(endpoint)
    queue = base.server_json(opener, endpoint, "/queue")
    history = base.server_json(opener, endpoint, "/history?max_items=64")
    candidates = list(queue.get("queue_running", [])) + list(queue.get("queue_pending", []))
    candidates.extend(value["prompt"] for value in history.values()
                      if isinstance(value, dict) and isinstance(value.get("prompt"), list))
    expected = base.read_json(destination / "jobs" / job_id / "workflow-api.json")
    matches = set()
    for candidate in candidates:
        if not isinstance(candidate, list) or len(candidate) < 4 or not isinstance(candidate[3], dict):
            continue
        extra = candidate[3]
        meta = extra.get("extra_pnginfo", {})
        if (isinstance(meta, dict) and meta.get("reference_batch") == batch_id
                and meta.get("reference_job") == job_id
                and extra.get("client_id") == job.get("clientId")
                and candidate[2] == expected and isinstance(candidate[1], str)):
            matches.add(candidate[1])
    if len(matches) != 1:
        raise ValueError(f"Reconciliation found {len(matches)} exact scoped matches; retain hold, never blindly resubmit")
    prompt_id = matches.pop()
    if apply:
        with receipt_lock(destination, f"reconcile:{job_id}"):
            if evidence(root, batch_id)[2] != record:
                raise ValueError("Execution changed during reconciliation; preview again")
            job.update(state="queued", promptId=prompt_id, reconciledAt=now())
            job.pop("error", None)
            atomic_json(destination / "execution.json", record)
    return {"state": "reconciled" if apply else "reconciliation-preview",
            "job": job_id, "promptId": prompt_id, "submittedAgain": False}


def retain(root, batch_id, job_id, output_sha, apply=False):
    destination, _, execution = evidence(root, batch_id)
    job = execution["jobs"].get(job_id)
    if not job or job["state"] != "completed":
        raise ValueError("Only a completed, selected output may be retained")
    matches = [item for item in job["outputs"] if item["sha256"] == output_sha]
    if len(matches) != 1:
        raise ValueError("Select one exact output hash")
    output = matches[0]
    relative = (output.get("subfolder", "").rstrip("/") + "/" + output["filename"]).lstrip("/")
    path = base.safe_path(safe_root(execution["outputRoot"]), relative)
    data = path.read_bytes()
    if base.digest(data) != output_sha:
        raise ValueError("Server output changed since review")
    relative_target = f"_generation/selected/{batch_id}/{job_id}/{output['filename']}"
    target = base.safe_path(root, relative_target)
    record = {"schemaVersion": 1, "batchId": batch_id, "jobId": job_id,
              "displayName": job["displayName"], "sourceOutput": str(path),
              "sha256": output_sha, "synthetic": True, "identityCoreEligible": False}
    frozen_request = destination / "request.json"
    if frozen_request.is_file():
        source_job = next(item for item in base.read_json(frozen_request)["jobs"] if item["id"] == job_id)
        record["domain"] = source_job["source"]["domain"]
        record["source"] = source_job["source"]
        if source_job.get("personId"):
            record["personId"] = source_job["personId"]
    if apply:
        owned_write(target, data)
        owned_write(target.with_suffix(target.suffix + ".json"), base.encode(record))
    return {**record, "destination": str(target), "applied": apply}


def manual_prefixes(root, apply=False):
    changes = []
    for folder in ("zz_shots", "alpha"):
        directory = base.safe_path(WORKFLOWS, folder)
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.json")):
            relative = path.relative_to(WORKFLOWS).as_posix()
            base.safe_path(WORKFLOWS, relative)
            data = path.read_bytes()
            workflow = json.loads(data)
            nodes = list(workflow.get("nodes", []))
            for subgraph in workflow.get("definitions", {}).get("subgraphs", []):
                nodes.extend(subgraph.get("nodes", []))
            updates = []
            for node in nodes:
                if node.get("type") != "SaveImage" or not node.get("widgets_values"):
                    continue
                old = node["widgets_values"][0]
                if not isinstance(old, str):
                    raise ValueError(f"Unknown SaveImage prefix in {relative}")
                normalized = old.replace("\\", "/")
                match = re.match(r"^angels?-primes/(?:shots/)?(.+)$", normalized, re.IGNORECASE)
                if match:
                    new = "reference/manual/" + match.group(1)
                    base.safe_path(root, new)
                    node["widgets_values"][0] = new
                    updates.append({"old": old, "new": new})
            if updates:
                changes.append({"relative": relative, "sha256": base.digest(data),
                                "before": data, "after": base.encode(workflow), "prefixes": updates})
    summary = {"changedFiles": len(changes), "changes": [
        {key: value for key, value in item.items() if key not in {"before", "after"}}
        for item in changes], "applied": apply}
    if not apply or not changes:
        return summary
    backup_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    backup = base.safe_path(root, f"_generation/workspace-backups/{backup_id}")
    for item in changes:
        owned_write(base.safe_path(backup, item["relative"]), item["before"])
    owned_write(backup / "manifest.json", base.encode(summary))
    changed = []
    try:
        for item in changes:
            path = base.safe_path(WORKFLOWS, item["relative"])
            if base.digest(path.read_bytes()) != item["sha256"]:
                raise ValueError(f"Manual workflow changed since preview: {item['relative']}")
            temporary = path.with_name(path.name + ".reference-pending")
            with temporary.open("xb") as stream:
                stream.write(item["after"])
            base.report_assets.replace_file(temporary, path)
            changed.append(item)
    except (OSError, ValueError):
        for item in reversed(changed):
            path = base.safe_path(WORKFLOWS, item["relative"])
            if path.read_bytes() != item["after"]:
                raise ValueError(f"Concurrent manual edit blocks rollback; backup: {backup}")
            temporary = path.with_name(path.name + ".reference-restore")
            with temporary.open("xb") as stream:
                stream.write(item["before"])
            base.report_assets.replace_file(temporary, path)
        raise
    return {**summary, "backup": str(backup)}


def overlay_scan(root, inputs, apply=False, *, scan_id=None):
    """Re-run intake's overlay heuristic over a raw intake mirror and map hits to Gallery sources.

    Read-only for images; the scan result is the only write. Raw hits are tied to the current
    Gallery copy by stable photo key, because that copy may already be cropped or repainted.
    """
    tools = pathlib.Path(__file__).resolve().parents[1]
    for folder in (tools / "workflows", tools / "art"):
        if str(folder) not in sys.path:
            sys.path.insert(0, str(folder))
    import comfy_workflows
    import preparation_geometry
    from PIL import ImageOps
    root = safe_root(root)
    inputs = pathlib.Path(inputs).resolve()
    if not inputs.is_dir() or not inputs.is_relative_to(root.resolve()):
        raise ValueError("Scan inputs must be an existing folder inside the library root")
    scan_id = scan_id or "overlay-scan-" + datetime.datetime.now().strftime("%Y%m%d-%H%M")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,40}", scan_id):
        raise ValueError("Invalid scan ID")
    by_key = {}
    for source in gallery_sources(root):
        if source.get("kind"):
            continue
        key = comfy_workflows.photo_key(pathlib.PurePosixPath(source["path"]).name)
        if key:
            by_key.setdefault(key, []).append(source)
    scanned, mapped, unmapped, errors = 0, [], [], []
    for path in sorted(inputs.rglob("*")):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"} or not path.is_file():
            continue
        scanned += 1
        raw = path.relative_to(inputs).as_posix()
        try:
            with Image.open(path) as opened:
                image = ImageOps.exif_transpose(opened).convert("RGB")
            detected = preparation_geometry.plan(image)["overlayDetected"]
        except (OSError, ValueError, Image.DecompressionBombError) as error:
            errors.append({"raw": raw, "error": str(error)})
            continue
        if not detected:
            continue
        key = comfy_workflows.photo_key(path.name)
        matches = by_key.get(key, []) if key else []
        if not matches:
            unmapped.append({"raw": raw, "photoKey": key})
        for source in matches:
            mapped.append({"path": source["path"], "displayName": source["displayName"],
                           "photoKey": key, "raw": raw, "rawSha256": base.digest(path.read_bytes())})
    destination = base.safe_path(root, f"_generation/proposals/{scan_id}")
    result = {"schemaVersion": 1, "scanId": scan_id, "createdAt": now(), "inputs": str(inputs),
              "heuristic": "preparation_geometry.plan overlayDetected", "scanned": scanned,
              "detected": len(mapped) + len(unmapped), "mapped": mapped, "unmapped": unmapped,
              "errors": errors, "file": str(destination / "overlay-scan.json"), "applied": apply}
    if apply:
        owned_write(destination / "overlay-scan.json", base.encode(result))
    return result


def person_samples(root, sources, count):
    """Resolution-first exploratory samples, not a facial-quality or outfit classifier."""
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 64:
        raise ValueError("--per-person must be between 1 and 64")
    groups, excluded = {}, []
    for source in sources:
        parts = source["path"].split("/")
        if (source.get("kind") or not source.get("personId") or parts[0] == "Various"
                or "gallery" not in parts[1:-1]):
            excluded.append(source["path"])
            continue
        path = base.safe_path(root, source["path"])
        if base.digest(path.read_bytes()) != source["sha256"]:
            raise ValueError(f"Sample source hash changed; refresh Photo Review: {source['path']}")
        with Image.open(path) as image:
            width, height = image.size
        groups.setdefault((source["domain"], source["personId"]), []).append(
            (-(width * height), -min(width, height), source["path"], source))
    selected, duplicates = [], []
    for key in sorted(groups):
        seen, kept = set(), 0
        for _, _, _, source in sorted(groups[key]):
            if source["sha256"] in seen:
                duplicates.append(source["path"])
                continue
            seen.add(source["sha256"])
            if kept < count:
                selected.append(source)
                kept += 1
    return selected, {
        "perPerson": count, "personCount": len(groups),
        "ranking": "pixel-area descending, shortest-side descending, source-path ascending",
        "scope": "assigned original gallery photos only; exact bytes deduplicated within each person",
        "limitations": "Resolution is not face quality. No near-duplicate or outfit elimination; review the sample.",
        "excluded": excluded, "exactDuplicates": duplicates,
    }


def cleanup_batch(root, recipes=("shared-0c-cleanup-basic",), samples=2, hints=("needs-cleanup",),
                  apply=False, *, proposal_id=None, seeds=None, source_file=None, per_person=None):
    """Propose (never queue) request JSON for intake images that intake left for ComfyUI cleanup.

    source_file: an overlay-scan.json (or any JSON with a "mapped" list of {"path"}) that
    replaces the published hints as the candidate list.
    """
    if __package__:
        from . import reference_gallery as gallery
    else:
        import reference_gallery as gallery
    unknown = set(hints) - set(CLEANUP_HINTS)
    if not hints or unknown:
        raise ValueError(f"Choose cleanup hints from: {', '.join(CLEANUP_HINTS)}")
    entries = {entry["id"]: entry for entry in catalog()}
    chosen = []
    for recipe in recipes:
        entry = entries.get(recipe)
        if not entry or not entry.get("available"):
            raise ValueError(f"Recipe is not available: {recipe}")
        chosen.append(entry)
    per_source = len(chosen) * samples
    if samples not in gallery.SAMPLE_COUNTS or per_source > MAX_RUN_JOBS:
        raise ValueError(f"Samples must be one of {gallery.SAMPLE_COUNTS} and fit {MAX_RUN_JOBS} jobs per source")
    if source_file is not None:
        listed = base.read_json(pathlib.Path(source_file)).get("mapped")
        if not isinstance(listed, list) or not all(isinstance(item, dict) and isinstance(item.get("path"), str)
                                                   for item in listed):
            raise ValueError("Source file needs a 'mapped' list of {\"path\": ...} entries")
        wanted = {item["path"] for item in listed}
        candidates = [{**source, "cleanup": "needs-cleanup"} for source in gallery_sources(root)
                      if source["path"] in wanted and not source.get("kind")]
        missing = wanted - {source["path"] for source in candidates}
        if missing:
            raise ValueError(f"Source file lists {len(missing)} path(s) that are not current Gallery sources; rescan")
    elif per_person is not None:
        candidates = gallery_sources(root)
    else:
        candidates = [source for source in gallery_sources(root) if source.get("cleanup") in hints]
    selection = None
    if per_person is not None:
        candidates, selection = person_samples(root, candidates, per_person)
    proposal_id = proposal_id or "cleanup-" + datetime.datetime.now().strftime("%Y%m%d-%H%M")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,40}", proposal_id):
        raise ValueError("Invalid proposal ID")
    chunk = MAX_RUN_JOBS // per_source
    batches = []
    for start in range(0, len(candidates), chunk):
        part = candidates[start:start + chunk]
        batch_id = f"{proposal_id}-{len(batches) + 1:02d}"
        count = len(part) * per_source
        batch_seeds = (seeds[start * per_source:start * per_source + count] if seeds is not None
                       else [int.from_bytes(os.urandom(6), "big") for _ in range(count)])
        request = gallery.make_request(root, part, chosen, samples, batch_id, batch_seeds)
        batches.append({"batchId": batch_id, "request": f"{batch_id}.json", "jobs": count,
                        "sources": [source["path"] for source in part], "body": request})
    destination = base.safe_path(root, f"_generation/proposals/{proposal_id}")
    summary = {
        "schemaVersion": 1, "proposalId": proposal_id, "createdAt": now(), "hints": list(hints),
        "sourceFile": str(source_file) if source_file is not None else None,
        "selection": selection,
        "recipes": [entry["id"] for entry in chosen], "samplesPerWorkflow": samples,
        "sourceCount": len(candidates), "jobCount": sum(item["jobs"] for item in batches),
        "queueCapacity": QUEUE_CAPACITY, "destination": str(destination),
        "batches": [{key: value for key, value in item.items() if key != "body"} for item in batches],
        "next": ("Review the sources, then per batch: render-reference.cmd prepare REQUEST --root ROOT --apply; "
                 "compile; run --queue-depth N --apply; then browse outputs and pull selected images."),
        "applied": apply,
    }
    if apply and batches:
        if destination.exists():
            raise ValueError(f"Proposal already exists: {destination}")
        for item in batches:
            owned_write(destination / item["request"], base.encode(item["body"]))
        owned_write(destination / "proposal.json", base.encode(summary))
    return summary
