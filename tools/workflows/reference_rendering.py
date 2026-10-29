"""Source-bound input requests and read-only local ComfyUI diagnostics."""
import argparse
import hashlib
import http.client
import io
import json
import os
import pathlib
import re
import sys
import urllib.parse
import urllib.request

import jsonschema
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "data" / "schemas" / "reference-render-request.schema.json"
sys.path.insert(0, str(ROOT / "tools" / "art"))
import temporary_storage  # noqa: E402
from likeness_library import report_assets
if __package__:
    from . import comfy_workflows as cw
else:
    import comfy_workflows as cw


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Server probe refuses redirects")


def server_json(opener, endpoint, route):
    with opener.open(endpoint + route, timeout=5) as response:
        data = response.read(16 * 1024 * 1024 + 1)
    if len(data) > 16 * 1024 * 1024:
        raise ValueError(f"Server response too large: {route}")
    result = json.loads(data)
    if not isinstance(result, dict):
        raise ValueError(f"Expected server JSON object: {route}")
    return result


def probe_server(endpoint, expected_input, expected_output, required_nodes=()):
    """Read-only capability diagnostics, never a render-ready assertion."""
    parsed = urllib.parse.urlsplit(endpoint)
    if (parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "::1"}
            or not parsed.port or parsed.username or parsed.password
            or parsed.path not in {"", "/"} or parsed.query or parsed.fragment):
        raise ValueError("Probe requires an explicit HTTP loopback IP and port, without credentials/path")
    if not expected_input or not expected_output:
        raise ValueError("Probe requires --input-root and --output-root")
    if not all(pathlib.PureWindowsPath(value).is_absolute()
               for value in (expected_input, expected_output)):
        raise ValueError("Expected ComfyUI roots must be absolute Windows paths")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    endpoint = endpoint.rstrip("/")
    stats = server_json(opener, endpoint, "/system_stats")
    system = stats.get("system")
    if not isinstance(system, dict):
        raise ValueError("Server lacks system statistics")
    argv = system.get("argv")
    if not isinstance(argv, list) or not all(isinstance(arg, str) for arg in argv):
        raise ValueError("Server does not expose usable argv; workspace roots cannot be checked")
    flags = {}
    for index, arg in enumerate(argv):
        for name in ("input-directory", "output-directory", "user-directory", "base-directory"):
            if arg == f"--{name}" and index + 1 < len(argv):
                if name in flags:
                    raise ValueError(f"Ambiguous runtime --{name}")
                flags[name] = argv[index + 1]
            elif arg.startswith(f"--{name}="):
                if name in flags:
                    raise ValueError(f"Ambiguous runtime --{name}")
                flags[name] = arg.split("=", 1)[1]
    blockers = []
    for name, expected in (("input-directory", expected_input), ("output-directory", expected_output)):
        actual = flags.get(name)
        if actual is None or pathlib.PureWindowsPath(actual) != pathlib.PureWindowsPath(expected):
            blockers.append(f"Runtime --{name} does not match expected root")
    objects = server_json(opener, endpoint, "/object_info")
    if not objects or not all(isinstance(value, dict) for value in objects.values()):
        raise ValueError("Server node catalogue is missing or malformed")
    missing = sorted(set(required_nodes) - objects.keys())
    blockers.extend(f"Required node unavailable: {node}" for node in missing)
    model_choices = {}
    for node, field in (("UNETLoader", "unet_name"), ("CLIPLoader", "clip_name"),
                        ("VAELoader", "vae_name"), ("LoraLoader", "lora_name")):
        inputs = objects.get(node, {}).get("input", {})
        if not isinstance(inputs, dict) or not isinstance(inputs.get("required", {}), dict):
            raise ValueError(f"Malformed server node inputs: {node}")
        choices = inputs.get("required", {}).get(field)
        if isinstance(choices, list) and choices and isinstance(choices[0], list):
            model_choices[node] = [value for value in choices[0] if isinstance(value, str)]
    return {
        "state": "blocked" if blockers else "communications-checked-not-render-ready",
        "endpoint": endpoint, "comfyuiVersion": system.get("comfyui_version"),
        "runtimeRoots": flags, "expectedInput": expected_input, "expectedOutput": expected_output,
        "nodeCount": len(objects), "requiredNodes": list(required_nodes),
        "modelChoices": model_choices, "blockers": blockers,
        "limitations": [
            "Only GET /system_stats and GET /object_info were used",
            "Roots are compared with runtime argv, not proven by upload/output round trip",
            "No recipe graph/model compatibility or render was tested",
        ],
    }


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique)


def safe_path(root, relative):
    parts = relative.split("/")
    if any(
        not part or part in (".", "..") or re.search(r'[<>:"\\|?*\x00-\x1f]', part)
        or part.endswith((" ", "."))
        or part.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL",
                                         *[f"COM{i}" for i in range(1, 10)],
                                         *[f"LPT{i}" for i in range(1, 10)]}
        for part in parts
    ):
        raise ValueError(f"Unsafe relative path: {relative}")
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise ValueError(f"Linked path is not permitted: {path}")
    path.resolve().relative_to(root.resolve())
    return path


def library_root(value):
    path = pathlib.Path(value)
    if not path.is_absolute() or not path.is_dir():
        raise ValueError("Library root must be an existing absolute directory")
    for parent in (path, *path.parents):
        if parent.is_symlink() or (hasattr(parent, "is_junction") and parent.is_junction()):
            raise ValueError(f"Linked library root is not permitted: {parent}")
    return path.resolve()


def inspect_source(root, job):
    relative = job["source"]["path"]
    parts = relative.split("/")
    kind = job["source"].get("kind", "photo")
    allowed = {"Angels", "Sisters", "Models", "Prospects", "Potentials", "Various", "Artists"}
    pulled = kind == "pulled-render"
    selected = kind == "selected-render" or pulled
    generation_parts = cw.storage_root(
        cw.load_cfg(), "generation", root=root
    ).relative_to(root).parts
    if pulled:
        stage_index = len(generation_parts) + 1
        if (len(parts) != len(generation_parts) + 4
                or tuple(parts[:len(generation_parts)]) != generation_parts
                or parts[len(generation_parts)] != "library"):
            raise ValueError("Pulled render must live under the configured generation library")
    elif selected:
        batch_index = len(generation_parts) + 1
        if (len(parts) != len(generation_parts) + 4
                or tuple(parts[:len(generation_parts)]) != generation_parts
                or parts[len(generation_parts)] != "selected"):
            raise ValueError("Selected render must be an explicitly retained output")
    elif parts[0] not in allowed or any(p.startswith("_") for p in parts):
        raise ValueError(f"Source is outside active photo roots: {relative}")
    if not selected and not any(p in {"gallery", "review", "gallery_944x1104",
                     "headshot_944x1104", "chest_944x1104"} for p in parts[1:-1]):
        raise ValueError(f"Source must be an active photo or standard derivative: {relative}")
    if not selected and (parts[0] == "Artists") != (job["source"]["domain"] == "artists"):
        raise ValueError(f"Source domain mismatch: {relative}")
    path = safe_path(root, relative)
    data = path.read_bytes()
    if digest(data) != job["source"]["sha256"]:
        raise ValueError(f"Source hash changed: {relative}")
    if pulled:
        provenance = read_json(safe_path(root, relative + ".json"))
        if (provenance.get("kind") != "pulled-render" or provenance.get("synthetic") is not True
                or provenance.get("identityCoreEligible") is not False
                or provenance.get("sha256") != job["source"]["sha256"]
                or provenance.get("stage") != parts[stage_index]
                or provenance.get("variant") != parts[stage_index + 1]
                or provenance.get("domain", "general") != job["source"]["domain"]):
            raise ValueError("Pulled-render provenance does not match the library copy")
    elif selected:
        provenance = read_json(safe_path(root, relative + ".json"))
        if (provenance.get("synthetic") is not True
                or provenance.get("identityCoreEligible") is not False
                or provenance.get("sha256") != job["source"]["sha256"]
                or provenance.get("batchId") != parts[batch_index]
                or provenance.get("jobId") != parts[batch_index + 1]
                or provenance.get("domain", "general") != job["source"]["domain"]):
            raise ValueError("Selected-render provenance does not match the retained output")
    with Image.open(io.BytesIO(data)) as image:
        image.verify()
    with Image.open(io.BytesIO(data)) as image:
        size = list(image.size)
        image_format = image.format
    return data, size, image_format


def validate_request(request):
    jsonschema.Draft202012Validator(read_json(SCHEMA)).validate(request)
    ids = [job["id"].casefold() for job in request["jobs"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Job IDs must be unique, ignoring case")


def request_plan(request, root):
    validate_request(request)
    destination = run_path(root, request["batchId"])
    artifacts = {"request.json": encode(request)}
    jobs = []
    for job in request["jobs"]:
        data, size, image_format = inspect_source(root, job)
        extension = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp", "BMP": ".bmp"}.get(image_format)
        if extension is None:
            raise ValueError(f"Unsupported source image format: {image_format}")
        relative = f"jobs/{job['id']}/input/source{extension}"
        safe_path(destination, relative)
        artifacts[relative] = data
        jobs.append({
            "id": job["id"], "input": relative, "sha256": digest(data),
            "dimensions": size, "workspace": request["workspace"],
            "workflowMode": job["workflowMode"], "recipe": job["recipe"],
            "profile": job["profile"], "seed": job["seed"],
            "state": "input-prepared",
        })
    run = {
        "schemaVersion": 1, "batchId": request["batchId"],
        "libraryRoot": str(root), "state": "inputs-only-not-render-ready",
        "requestSha256": digest(artifacts["request.json"]), "jobs": jobs,
        "artifacts": {name: digest(data) for name, data in artifacts.items()},
        "configurationReceipt": cw.storage_configuration_receipt(
            cw.load_cfg(), root, {"referenceRunDirectory": run_path(root, request["batchId"])},
        ),
    }
    return run, artifacts


def run_path(root, batch_id):
    relative = cw.storage_root(
        cw.load_cfg(), "generation", root=root
    ).relative_to(root).as_posix()
    return safe_path(root, f"{relative}/reference/{batch_id}")


def check(root, batch_id):
    destination = run_path(root, batch_id)
    safe_path(destination, "request.json")
    safe_path(destination, "run.json")
    request = read_json(destination / "request.json")
    validate_request(request)
    if (destination / "request.json").read_bytes() != encode(request):
        raise ValueError("Frozen request bytes changed")
    if request["batchId"] != batch_id:
        raise ValueError("Saved batch ID does not match run directory")
    # Reconstruct solely from frozen inputs: a later source move must not rewrite history.
    jobs = []
    artifacts = {"request.json": encode(request)}
    for job in request["jobs"]:
        directory = safe_path(destination, f"jobs/{job['id']}/input")
        files = list(directory.iterdir())
        if len(files) != 1 or not files[0].is_file():
            raise ValueError(f"Frozen input inventory changed: {job['id']}")
        relative = files[0].relative_to(destination).as_posix()
        data = safe_path(destination, relative).read_bytes()
        if digest(data) != job["source"]["sha256"]:
            raise ValueError(f"Frozen input hash changed: {job['id']}")
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            size = list(image.size)
            expected_extension = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp", "BMP": ".bmp"}.get(image.format)
        if files[0].name != f"source{expected_extension}":
            raise ValueError(f"Frozen input filename changed: {job['id']}")
        artifacts[relative] = data
        jobs.append({
            "id": job["id"], "input": relative, "sha256": digest(data),
            "dimensions": size, "workspace": request["workspace"],
            "workflowMode": job["workflowMode"], "recipe": job["recipe"],
            "profile": job["profile"], "seed": job["seed"], "state": "input-prepared",
        })
    expected = {
        "schemaVersion": 1, "batchId": batch_id, "libraryRoot": str(root),
        "state": "inputs-only-not-render-ready", "requestSha256": digest(artifacts["request.json"]),
        "jobs": jobs, "artifacts": {name: digest(data) for name, data in artifacts.items()},
    }
    saved = read_json(destination / "run.json")
    if "configurationReceipt" in saved:
        receipt = saved["configurationReceipt"]
        jsonschema.validate(receipt, {
            "type": "object",
            "additionalProperties": False,
            "required": ["configurationPath", "sourceConfigurationSha256",
                         "effectiveConfigurationSha256", "environmentOverrides", "resolvedPaths"],
            "properties": {
                "configurationPath": {"type": "string", "minLength": 1},
                "sourceConfigurationSha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "effectiveConfigurationSha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "environmentOverrides": {"type": "object", "additionalProperties": {"type": "string"}},
                "resolvedPaths": {"type": "object", "additionalProperties": {"type": "string"}},
            },
        })
        if (not pathlib.Path(receipt["configurationPath"]).is_absolute()
                or not all(pathlib.Path(path).is_absolute() for path in receipt["resolvedPaths"].values())
                or receipt["resolvedPaths"].get("libraryRoot") != str(root.resolve())
                or receipt["resolvedPaths"].get("referenceRunDirectory") != str(destination.resolve())):
            raise ValueError("Saved configuration receipt paths changed or are invalid")
        expected["configurationReceipt"] = receipt
    if saved != expected:
        raise ValueError("Saved run evidence changed")
    if (destination / "run.json").read_bytes() != encode(expected):
        raise ValueError("Frozen run bytes changed")
    actual = set()
    for path in destination.rglob("*"):
        relative = path.relative_to(destination).as_posix()
        safe_path(destination, relative)
        if path.is_file():
            actual.add(relative)
    lifecycle = {"compiled.json", "execution.json", "execution.json.pending", "submission.lock"}
    for job in request["jobs"]:
        lifecycle.update(f"jobs/{job['id']}/{name}" for name in (
            "manual-source.json", "workflow-ui.json", "workflow-api.json", "prompt-source.txt"))
    if not (set(artifacts) | {"run.json"}) <= actual or actual - set(artifacts) - {"run.json"} - lifecycle:
        raise ValueError("Saved run file inventory changed")
    if "compiled.json" in actual:
        if __package__:
            from . import reference_execution as execution
        else:
            import reference_execution as execution
        execution.evidence(root, batch_id)
    elif actual & lifecycle:
        raise ValueError("Execution artifacts exist without compiled ownership evidence")
    return expected


def prepare(request, root):
    run, artifacts = request_plan(request, root)
    destination = run_path(root, request["batchId"])
    if destination.exists():
        checked = check(root, request["batchId"])
        if ({key: value for key, value in checked.items() if key != "configurationReceipt"}
                != {key: value for key, value in run.items() if key != "configurationReceipt"}):
            raise ValueError("Batch ID is already owned by a different request")
        return checked
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_root = cw.storage_root(cw.load_cfg(), "temporary", root=root)
    with temporary_storage.staging_directory(temporary_root, ".reference-") as staging:
        for relative, data in {**artifacts, "run.json": encode(run)}.items():
            target = staging / pathlib.PurePosixPath(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        # All source checks precede publication; do not publish a partial batch.
        if request_plan(request, root)[0] != run:
            raise ValueError("Inputs changed during preparation")
        os.rename(staging, destination)
    return check(root, request["batchId"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preview", "prepare", "check", "probe", "catalog",
                                            "compile", "submit", "status", "retain", "run", "reconcile", "manual-prefixes",
                                            "cleanup-batch", "overlay-scan", "outputs", "pull", "compare"))
    parser.add_argument("request", nargs="?", help="Batch JSON, batch ID, or explicit server URL for probe")
    parser.add_argument("--root", help="Absolute library root (offline commands)")
    parser.add_argument("--input-root", help="Expected absolute ComfyUI input root (probe only)")
    parser.add_argument("--output-root", help="Expected absolute ComfyUI output root (probe only)")
    parser.add_argument("--require-node", action="append", default=[], help="Required server node class (probe only)")
    parser.add_argument("--endpoint", help="Explicit local endpoint for compile")
    parser.add_argument("--job", help="One exact job ID for submit/retain")
    parser.add_argument("--output-sha", help="Exact reviewed output SHA-256 for retain")
    parser.add_argument("--refresh", action="store_true", help="Explicit online receipt refresh for status")
    parser.add_argument("--limit", type=int, default=4, help="Maximum selected jobs for run, default 4")
    parser.add_argument("--timeout", type=int, default=3600, help="Bounded run deadline in seconds")
    parser.add_argument("--interval", type=int, default=10, help="Run polling interval in seconds")
    parser.add_argument("--allow-busy-queue", action="store_true",
                        help="Explicitly append one selected job behind existing jobs; submit/run only")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check", action="store_true", help="Read-only verification; check command only")
    parser.add_argument("--queue-depth", type=int, help="Owned jobs kept queued at once; run only (1..16, default 1)")
    parser.add_argument("--recipe", action="append", default=[], help="Recipe ID for cleanup-batch (repeatable)")
    parser.add_argument("--samples", type=int, help="Samples per workflow for cleanup-batch (1, 2, 4, 8, 16)")
    parser.add_argument("--hint", action="append", default=[], help="Cleanup hint for cleanup-batch (repeatable)")
    parser.add_argument("--sources", help="overlay-scan.json whose mapped paths replace hints (cleanup-batch only)")
    parser.add_argument("--per-person", type=int,
                        help="Sample N assigned originals per person by resolution, not cleanup hints")
    parser.add_argument("--inputs", help="Raw intake mirror folder inside the root to rescan (overlay-scan only)")
    parser.add_argument("--id", help="Proposal or scan ID (cleanup-batch, overlay-scan)")
    parser.add_argument("--workspace", action="append", default=[], help="Output workspace folder for outputs (repeatable)")
    parser.add_argument("--batch", action="append", default=[], help="Additional batch ID for compare (repeatable)")
    args = parser.parse_args(argv)
    try:
        if args.queue_depth is not None and args.command != "run":
            raise ValueError("--queue-depth requires run")
        if args.batch and args.command != "compare":
            raise ValueError("--batch requires compare")
        if (args.recipe or args.samples is not None or args.hint or args.sources
                or args.per_person is not None) and args.command != "cleanup-batch":
            raise ValueError("--recipe/--samples/--hint/--sources/--per-person require cleanup-batch")
        if args.per_person is not None and args.hint:
            raise ValueError("--per-person samples assigned originals, not cleanup hints; use --sources to narrow")
        if args.inputs and args.command != "overlay-scan":
            raise ValueError("--inputs requires overlay-scan")
        if args.id and args.command not in {"cleanup-batch", "overlay-scan"}:
            raise ValueError("--id requires cleanup-batch or overlay-scan")
        if args.workspace and args.command != "outputs":
            raise ValueError("--workspace requires outputs")
        if args.command == "compare":
            if (not args.root or not args.request or args.apply and (args.dry_run or args.check)
                    or any((args.endpoint, args.job, args.output_sha, args.refresh,
                            args.input_root, args.output_root, args.require_node, args.allow_busy_queue))):
                raise ValueError("compare takes batch ID, optional --batch, --root and --apply/--dry-run/--check only")
            if __package__:
                from . import reference_comparison as comparison
            else:
                import reference_comparison as comparison
            result = comparison.publish(library_root(args.root), [args.request, *args.batch],
                                        apply=args.apply, check=args.check)
            print(json.dumps(result, indent=2))
            return 1 if args.check and not result["current"] else 0
        if args.command in {"cleanup-batch", "overlay-scan", "outputs", "pull"}:
            if __package__:
                from . import reference_execution as execution, reference_outputs as outputs
            else:
                import reference_execution as execution
                import reference_outputs as outputs
            if not args.root or args.apply and args.dry_run or any((
                    args.endpoint, args.job, args.output_sha, args.refresh, args.input_root,
                    args.require_node, args.allow_busy_queue)):
                raise ValueError(f"{args.command} takes --root and --apply/--dry-run only")
            root = library_root(args.root)
            if args.command == "cleanup-batch":
                if args.request or args.output_root or args.check:
                    raise ValueError("cleanup-batch takes no request, output root or --check")
                result = execution.cleanup_batch(
                    root, tuple(args.recipe) or ("shared-0c-cleanup-basic",),
                    2 if args.samples is None else args.samples,
                    tuple(args.hint) or ("needs-cleanup",), args.apply,
                    proposal_id=args.id, source_file=args.sources, per_person=args.per_person)
            elif args.command == "overlay-scan":
                if args.request or args.output_root or args.check or not args.inputs:
                    raise ValueError("overlay-scan takes --inputs DIR and no request, output root or --check")
                result = execution.overlay_scan(root, args.inputs, args.apply, scan_id=args.id)
                result = {**result, "mapped": len(result["mapped"]), "unmapped": result["unmapped"][:20]}
            elif args.command == "outputs":
                if args.request or args.check and args.apply:
                    raise ValueError("outputs takes no request; choose --apply or --check")
                result = outputs.publish(root, outputs.output_root(args.output_root),
                                         args.workspace, args.apply, args.check)
                print(json.dumps(result, indent=2))
                return 1 if args.check and not result["current"] else 0
            else:
                if not args.request or args.check:
                    raise ValueError("pull requires a manifest path and no --check")
                result = outputs.pull(root, pathlib.Path(args.request),
                                      outputs.output_root(args.output_root), args.apply)
            print(json.dumps(result, indent=2))
            return 0
        if args.allow_busy_queue and args.command not in {"submit", "run"}:
            raise ValueError("--allow-busy-queue requires submit or run")
        if args.command in {"catalog", "compile", "submit", "status", "retain", "run", "reconcile", "manual-prefixes"}:
            if __package__:
                from . import reference_execution as execution
            else:
                import reference_execution as execution
            if args.check or (args.apply and args.dry_run):
                raise ValueError("Execution commands do not accept --check or conflicting apply/dry-run")
            if args.command == "manual-prefixes":
                if not args.root or any((args.request, args.endpoint, args.job, args.output_sha,
                                         args.refresh, args.input_root, args.output_root, args.require_node)):
                    raise ValueError("Manual prefixes takes only --root and --apply/--dry-run")
                result = execution.manual_prefixes(library_root(args.root), args.apply)
            elif args.command == "catalog":
                if any((args.apply, args.refresh, args.endpoint, args.job, args.output_sha,
                        args.input_root, args.output_root, args.require_node, args.request)):
                    raise ValueError("Catalog is read-only and takes no execution arguments")
                result = execution.catalog()
            else:
                if not args.root or not args.request:
                    raise ValueError("Execution commands require batch ID and --root")
                if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", args.request):
                    raise ValueError("Invalid batch ID")
                root = library_root(args.root)
                if args.command == "compile":
                    if not all((args.endpoint, args.input_root, args.output_root)) or args.job or args.refresh or args.output_sha:
                        raise ValueError("Compile requires endpoint/input-root/output-root and no job/refresh/output selection")
                    result = execution.compile_batch(root, args.request, args.endpoint,
                                                     args.input_root, args.output_root, args.apply)
                else:
                    if args.endpoint or args.input_root or args.output_root or args.require_node:
                        raise ValueError("Execution endpoint/roots are frozen by compile")
                    if args.command == "run":
                        if args.job or args.refresh or args.output_sha:
                            raise ValueError("Run takes a bounded batch, not a job/refresh/output selection")
                        result = execution.run_batch(root, args.request, args.apply,
                                                     args.limit, args.timeout, args.interval,
                                                     allow_busy_queue=args.allow_busy_queue,
                                                     queue_depth=args.queue_depth or 1)
                    elif args.command in {"submit", "reconcile"}:
                        if not args.job or args.refresh or args.output_sha:
                            raise ValueError("Submit requires one --job and no refresh/output selection")
                        if args.command == "submit":
                            result = execution.submit(root, args.request, args.job, args.apply,
                                                      allow_busy_queue=args.allow_busy_queue)
                        else:
                            result = execution.reconcile(root, args.request, args.job, args.apply)
                    elif args.command == "status":
                        if args.apply or args.job or args.output_sha or args.dry_run:
                            raise ValueError("Status takes only optional --refresh")
                        result = execution.status(root, args.request, args.refresh)
                    else:
                        if not args.job or not args.output_sha or args.refresh:
                            raise ValueError("Retain requires --job and --output-sha")
                        result = execution.retain(root, args.request, args.job, args.output_sha, args.apply)
            print(json.dumps(result, indent=2))
            return 0
        if args.endpoint or args.job or args.output_sha or args.refresh:
            raise ValueError("Execution flags require compile/submit/status/retain")
        if not args.request:
            raise ValueError("This command requires a request path, batch ID or probe URL")
        if args.command == "probe":
            if args.apply or args.dry_run or args.check or args.root:
                raise ValueError("Probe is read-only online diagnostics; no apply/dry-run/check/root flags")
            result = probe_server(args.request, args.input_root, args.output_root, args.require_node)
            print(json.dumps(result, indent=2))
            return 1 if result["blockers"] else 0
        if args.input_root or args.output_root or args.require_node:
            raise ValueError("Server capability flags require probe")
        if args.apply and (args.dry_run or args.command != "prepare" or args.check):
            raise ValueError("--apply is only valid for prepare without --dry-run/--check")
        if args.check and args.command != "check":
            raise ValueError("--check requires the check command")
        if not args.root:
            raise ValueError("Offline commands require --root")
        root = library_root(args.root)
        if args.command == "check":
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", args.request):
                raise ValueError("Invalid batch ID")
            result = check(root, args.request)
        else:
            request = read_json(args.request)
            result = prepare(request, root) if args.apply else request_plan(request, root)[0]
        print(json.dumps(result, indent=2))
        print("Inputs only; no workflow compilation, deployment, network access or ComfyUI submission.")
        return 0
    except (ValueError, OSError, http.client.HTTPException,
            jsonschema.ValidationError, Image.DecompressionBombError) as error:
        print(f"Reference rendering refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
