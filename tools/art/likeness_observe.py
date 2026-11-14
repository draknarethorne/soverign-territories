"""Bounded local visual observations; never identity labels or placement decisions."""
import argparse
import html
import importlib.metadata
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.art.likeness_library import appearance_context, review_packet, shadow  # noqa: E402
from tools.art.likeness_review_packet import output_path  # noqa: E402

MODEL_ID = "HuggingFaceTB/SmolVLM-500M-Instruct"
REVISION = "a7da5b986cb59b408707209984f360a5f4ad7e47"
RUNTIME = ROOT / "tmp" / "local-vlm"
MODEL = RUNTIME / "model"
PYTHON = RUNTIME / "venv" / "Scripts" / "python.exe"
PROMPT = (
    "Describe only the visible clothing and background in this image in two short sentences. "
    "Say unknown if details are unclear. Do not infer a person's identity, age, body shape, "
    "ethnicity, relationships or whether two images show the same person."
)


def codes():
    paths = [pathlib.Path(__file__).resolve(), ROOT / "tools" / "art" / "local_observer_requirements.txt",
             pathlib.Path(appearance_context.__file__)]
    return {str(p): shadow.digest(p) for p in paths}


def verify_files(root, outputs):
    for name, digest in outputs.items():
        if shadow.digest(review_packet.safe_path(root, name)) != digest:
            raise ValueError(f"observer bound output changed: {name}")


def source_bindings(source, receipt):
    return {
        str(source / "receipt.json"): shadow.digest(source / "receipt.json"),
        **receipt["inputs"], **receipt["code"],
        **{str(review_packet.safe_path(source, name)): digest for name, digest in receipt["outputs"].items()},
    }


def setup(apply):
    print(f"Local-only CPU observer: {MODEL_ID}@{REVISION}; Apache-2.0; approximately 1GB weights. "
          "Isolated system-site-packages venv; no CUDA/PyTorch replacement, server or private-photo upload. "
          "Inference capped at six below-face crops, 72 generated tokens/image, two orders, four CPU threads.")
    if not apply:
        return
    RUNTIME.mkdir(parents=True, exist_ok=True)
    if not PYTHON.is_file():
        subprocess.run([sys.executable, "-m", "venv", "--system-site-packages", str(RUNTIME / "venv")], check=True)
    subprocess.run([str(PYTHON), "-m", "pip", "install", "-r",
                    str(ROOT / "tools" / "art" / "local_observer_requirements.txt")], check=True)
    from huggingface_hub import snapshot_download
    snapshot_download(MODEL_ID, revision=REVISION, local_dir=str(MODEL),
                      allow_patterns=["*.json", "*.txt", "*.safetensors"])
    manifest = {p.name: shadow.digest(p) for p in MODEL.iterdir() if p.is_file()}
    if not {"model.safetensors", "config.json", "tokenizer.json", "preprocessor_config.json"} <= manifest.keys():
        raise ValueError("observer download lacks required pinned model files")
    (RUNTIME / "model-receipt.json").write_text(json.dumps({
        "model": MODEL_ID, "revision": REVISION, "license": "Apache-2.0", "files": manifest,
    }, indent=2) + "\n", encoding="utf-8")


def selection(state):
    rows = {r["photoId"]: r for r in state["rows"]}
    selected, cases = [], []
    for disposition in ("released-to-reassessment-pool", "membership-ambiguous", "current-membership-supported"):
        row = next((r for r in state["rows"] if r["disposition"] == disposition), None)
        if row is None:
            continue
        own = row["membershipAssessment"]["own"]
        refs = (own["supportPhotoIds"] or own["frozenReferencePhotoIds"]) if own else []
        other = next((pid for pid in refs if pid != row["photoId"]), None)
        if other is None:
            continue
        pair = [row["photoId"], other]
        if len(set(selected + pair)) > 6:
            continue
        selected = list(dict.fromkeys([*selected, *pair]))
        cases.append({"photoIds": pair, "selectionReason": disposition,
                      "contextInterpretation": "unevaluated", "humanReview": "not-performed"})
    if not selected or any(pid not in rows for pid in selected):
        raise ValueError("no eligible bounded observer sample")
    return selected, cases


def prepare(source, out, *, apply):
    receipt = json.loads((source / "receipt.json").read_bytes())
    if receipt["kind"] != "reformation-state-receipt" or not receipt["reverseVerified"]:
        raise ValueError("observer requires a reverse-verified reformation candidate")
    verify_files(source, receipt["outputs"])
    for path, digest in {**receipt["inputs"], **receipt["code"]}.items():
        if shadow.digest(pathlib.Path(path)) != digest:
            raise ValueError("observer candidate source/code changed")
    state = json.loads((source / "state.json").read_bytes())
    selected, cases = selection(state)
    paths = [pathlib.Path(p) for p in receipt["inputs"] if pathlib.Path(p).name == "run.json"]
    caches = [pathlib.Path(p) for p in receipt["inputs"] if pathlib.Path(p).name == "likeness-cache.json"]
    if len(paths) != 1 or len(caches) != 1:
        raise ValueError("observer requires one bound saved run and face cache")
    run, cache = json.loads(paths[0].read_bytes()), json.loads(caches[0].read_bytes())
    print(f"Observer preview: {len(selected)} source-verified below-face crops, {len(cases)} paired samples; "
          "no names, scores or desired matches sent to model; raw AI observations never become human labels.")
    if not apply:
        return None
    from PIL import Image, ImageOps
    photos = {r["photoId"]: r for r in run["photos"]}
    published = {r["path"]: r["sha256"] for r in run["publishedFiles"]}
    boxes = {r["alignmentEvidence"]["sourceSha256"]: r["box"] for r in cache["emb"].values()
             if r.get("alignmentEvidence", {}).get("sourceSha256") and r.get("box")}
    out.mkdir(parents=True, exist_ok=False)
    records = []
    for number, pid in enumerate(selected):
        photo = photos[pid]
        path = review_packet.safe_path(pathlib.Path(run["workingRoot"]), photo["destination"])
        if shadow.digest(path) != published[photo["destination"]]:
            raise ValueError("observer installed source changed")
        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            region = appearance_context.crop_region(image, boxes[photo["preparedSHA256"]])
            record = {"photoId": pid, "source": str(path), "sourceSHA256": published[photo["destination"]],
                      "cropPixels": region, "status": "unavailable" if region is None else "prepared"}
            if region is not None:
                name = f"crop-{number:02d}.png"
                crop = image.crop(region)
                crop.thumbnail((512, 512))
                crop.save(out / name)
                record.update(crop=name, cropSHA256=shadow.digest(out / name))
            records.append(record)
    request = {"model": MODEL_ID, "revision": REVISION, "prompt": PROMPT, "records": records, "cases": cases,
               "inputs": source_bindings(source, receipt)}
    (out / "request.json").write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
    return request


def infer(out):
    import torch
    from PIL import Image
    from transformers import AutoModelForImageTextToText, AutoProcessor
    torch.set_num_threads(4)
    request = json.loads((out / "request.json").read_bytes())
    model_receipt = json.loads((RUNTIME / "model-receipt.json").read_bytes())
    if model_receipt["model"] != MODEL_ID or model_receipt["revision"] != REVISION:
        raise ValueError("local observer model receipt differs")
    verify_files(MODEL, model_receipt["files"])
    processor = AutoProcessor.from_pretrained(str(MODEL), local_files_only=True, trust_remote_code=False)
    model = AutoModelForImageTextToText.from_pretrained(
        str(MODEL), local_files_only=True, trust_remote_code=False, dtype=torch.float32,
        attn_implementation="eager",
    ).eval()
    started = time.perf_counter()
    def observe(record):
        path = out / record["crop"]
        if shadow.digest(path) != record["cropSHA256"]:
            raise ValueError("observer crop changed")
        with Image.open(path) as image:
            prompt = processor.apply_chat_template([{"role": "user", "content": [
                {"type": "image"}, {"type": "text", "text": PROMPT},
            ]}], add_generation_prompt=True)
            inputs = processor(text=prompt, images=[image.convert("RGB")], return_tensors="pt")
            with torch.inference_mode():
                generated = model.generate(**inputs, max_new_tokens=72, do_sample=False)
            return processor.batch_decode(
                generated[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True,
            )[0]

    for record in request["records"]:
        if record["status"] == "unavailable":
            continue
        record.update(status="observed", observation=observe(record),
                      authority="unvalidated-AI-observation-not-human-review")
        print(f'Observed {record["crop"]}; first order, local CPU only.', flush=True)
    for record in reversed(request["records"]):
        if record["status"] == "observed":
            record["reverseObservation"] = observe(record)
            record["orderStable"] = record["observation"] == record["reverseObservation"]
            print(f'Checked {record["crop"]}; reverse order stable={record["orderStable"]}.', flush=True)
    request.update(elapsedSeconds=time.perf_counter()-started, identityDecisionsChanged=0,
                   disposition="diagnostic-only-no-identity-fusion",
                   runtime={"python": sys.version, "torch": torch.__version__, "device": "cpu",
                            "transformers": importlib.metadata.version("transformers")},
                   orderProtocol="Independent single-image prompts, then reverse invocation order; no shared chat history")
    (out / "observations.json").write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")
    (out / "index.html").write_text(render(request), encoding="utf-8")


def render(result):
    cards = []
    for row in result["records"]:
        observation = row.get("observation", "Insufficient pixels below face: observation unavailable.")
        image = f'<img src="{html.escape(row["crop"], quote=True)}" alt="Below-face observation crop">' if "crop" in row else ""
        cards.append(
            '<article><h2>' + html.escape(row["photoId"]) + '</h2>' + image
            + '<p><a href="' + html.escape(pathlib.Path(row["source"]).as_uri(), quote=True)
            + '">Open original filename: ' + html.escape(pathlib.Path(row["source"]).name) + '</a></p>'
            + '<p><b>Unvalidated local AI observation:</b> ' + html.escape(observation) + '</p>'
            + '<p>Reverse invocation order identical: ' + html.escape(str(row.get("orderStable", "unavailable")))
            + '. Human review: not performed. No identity decision changed.</p></article>'
        )
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
        '<title>Local visual-cue observations - not identity review</title>'
        '<style>body{font:16px system-ui;max-width:1000px;margin:auto;padding:16px;background:#171c23;color:#edf1f7}'
        'article{padding:16px;border:1px solid #718096;margin:16px 0}img{max-width:100%;height:280px;object-fit:contain}'
        'p,h2{overflow-wrap:anywhere}a{color:#9ed1ff}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>'
        '<h1>Local visual-cue feasibility test</h1><p>SmolVLM-500M, Apache-2.0, pinned local weights. '
        'Face-excluding crops; no names, scores or desired answers in prompts. These descriptions can be wrong. '
        'They are not identity, appearance-membership or family labels, and do not replace human review.</p>'
        '<p>Six-image development feasibility sample only: no calibrated gain, reserved evaluation or matching fusion claimed.</p>'
        + "".join(cards) + '<details><summary>Exact protocol and results</summary><pre>'
        + html.escape(json.dumps(result, indent=2)) + '</pre></details></html>'
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup", action="store_true", help="Explicit isolated runtime and pinned public model download")
    parser.add_argument("--source", type=pathlib.Path)
    parser.add_argument("--out", type=pathlib.Path)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.setup:
            if args.check:
                raise ValueError("use --setup --dry-run or --setup --apply")
            setup(args.apply)
            return 0
        if not args.out or not args.out.is_absolute():
            raise ValueError("--out must be absolute")
        if args.worker:
            infer(args.out)
            return 0
        out = output_path(args.out)
        if not args.source or not args.source.is_absolute():
            raise ValueError("--source must be an absolute assessed report")
        if args.check or args.apply and out.exists():
            receipt = json.loads((out / "receipt.json").read_bytes())
            if receipt["code"] != codes() or receipt["source"] != str(args.source):
                raise ValueError("observer source/code contract changed")
            verify_files(out, receipt["outputs"])
            for path, digest in receipt["inputs"].items():
                if shadow.digest(pathlib.Path(path)) != digest:
                    raise ValueError("observer source/model changed")
            model_receipt = json.loads((RUNTIME / "model-receipt.json").read_bytes())
            verify_files(MODEL, model_receipt["files"])
            print(f"Verified local observations: {out}")
            return 0
        if not args.apply:
            prepare(args.source, out, apply=False)
            return 0
        if not PYTHON.is_file() or not (RUNTIME / "model-receipt.json").is_file():
            raise ValueError("missing local observer runtime; run likeness-observe.cmd --setup --apply")
        staging = out.with_name(out.name + ".partial")
        request = prepare(args.source, staging, apply=True)
        environment = {**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "HF_HUB_DISABLE_TELEMETRY": "1"}
        subprocess.run([str(PYTHON), str(pathlib.Path(__file__)), "--worker", "--out", str(staging)],
                       env=environment, check=True, timeout=600)
        outputs = {p.name: shadow.digest(p) for p in staging.iterdir() if p.is_file()}
        inputs = {**request["inputs"], str(RUNTIME / "model-receipt.json"): shadow.digest(RUNTIME / "model-receipt.json")}
        inputs.update({r["source"]: r["sourceSHA256"] for r in request["records"]})
        receipt = {"source": str(args.source), "code": codes(), "inputs": inputs, "outputs": outputs,
                   "modelCalls": 2 * sum(r["status"] == "prepared" for r in request["records"]), "libraryWrites": 0}
        (staging / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        staging.rename(out)
        print(f"Published local-only AI observations: {out}; no identity or placement decisions changed.")
        return 0
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        print(f"Local observer failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
