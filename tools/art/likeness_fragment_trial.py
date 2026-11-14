"""Compare coherent identity fragments and a bounded local appearance cue; never install."""
import argparse
import copy
import importlib.metadata
import json
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from PIL import Image, ImageOps  # noqa: E402
from tools.art import likeness_reference_trial as baseline_cli  # noqa: E402
from tools.art.likeness_library import (  # noqa: E402
    appearance_context, fragment_report, fragment_review, review_packet, shadow,
)
from tools.art.likeness_review_packet import output_path  # noqa: E402


def code_bindings():
    paths = [pathlib.Path(__file__), *(pathlib.Path(module.__file__) for module in (
        appearance_context, fragment_report, fragment_review, review_packet,
    )), ROOT / "tools" / "art" / "likeness_library" / "fragment_evidence.py"]
    return {str(path): shadow.digest(path) for path in paths}


def verify_inputs(args):
    receipt = json.loads((args.candidate / "receipt.json").read_bytes())
    baseline_cli.check(args.candidate, receipt["inputs"], receipt["compareOrder"], realign=True)
    for path, expected in receipt["inputs"].items():
        if shadow.digest(pathlib.Path(path)) != expected:
            raise ValueError(f"baseline input changed: {path}")
    if str(args.experiment / "receipt.json") not in receipt["inputs"]:
        raise ValueError("candidate was not built from this experiment")
    labels = [pathlib.Path(path) for path in receipt["inputs"] if pathlib.Path(path).name == "effective-labels.json"]
    if len(labels) != 1:
        raise ValueError("candidate requires exactly one effective direct-pair ledger")
    files = [
        args.candidate / "receipt.json", args.candidate / "realignment.json",
        args.candidate / "evaluation.json", args.feedback, args.context_checkpoint,
        args.experiment / "receipt.json", labels[0],
    ]
    return {**receipt["inputs"], **{str(path): shadow.digest(path) for path in files}}, labels[0]


def check(out, inputs, maximum):
    receipt = json.loads((out / "receipt.json").read_bytes())
    if receipt["inputs"] != inputs or receipt["code"] != code_bindings() or receipt["maxPhotos"] != maximum:
        raise ValueError("fragment inputs/code/parameters changed; use a new --out")
    expected = {"evidence.json", "prior-feedback.json", "packet.json", "context.json", "index.html", "display.json"}
    if not expected <= receipt["outputs"].keys():
        raise ValueError("fragment receipt incomplete")
    for name, value in receipt["outputs"].items():
        if shadow.digest(review_packet.safe_path(out, name)) != value:
            raise ValueError(f"fragment output changed: {name}")
    display = json.loads((out / "display.json").read_bytes())
    for record in display.values():
        if shadow.digest(pathlib.Path(record["path"])) != record["sha256"]:
            raise ValueError("fragment source photo changed")
    packet = json.loads((out / "packet.json").read_bytes())
    if fragment_review.digest({key: value for key, value in packet.items() if key != "packetSHA256"}) != packet["packetSHA256"]:
        raise ValueError("fragment packet canonical binding differs")
    if not 30 <= len(packet["usedPhotoIds"]) <= maximum:
        raise ValueError("fragment photo conservation/budget differs")
    return packet


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=pathlib.Path, required=True)
    parser.add_argument("--candidate", type=pathlib.Path, required=True)
    parser.add_argument("--feedback", type=pathlib.Path, required=True)
    parser.add_argument("--context-checkpoint", type=pathlib.Path, required=True,
                        help="Existing local ViT-B-32 safetensors checkpoint; never downloads")
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-photos", type=int, default=40)
    parser.add_argument("--answers", type=pathlib.Path, help="Validate a new fragment export with --check")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if any(not path.is_absolute() for path in (
            args.experiment, args.candidate, args.feedback, args.context_checkpoint,
        )):
            raise ValueError("all fragment inputs must be absolute")
        if not 30 <= args.max_photos <= 40:
            raise ValueError("--max-photos must be 30 to 40 distinct photos")
        if args.answers and (not args.check or not args.answers.is_absolute()):
            raise ValueError("--answers requires --check and an absolute export path")
        out = output_path(args.out)
        bindings, label_path = verify_inputs(args)
        initial_code = code_bindings()
        if args.check or args.apply and out.exists():
            packet = check(out, bindings, args.max_photos)
            if args.answers:
                print("Fragment answers:", fragment_review.validate_answers(packet, json.loads(args.answers.read_bytes())))
            print(f"Verified fragment review: {out / 'index.html'}")
            return 0
        from tools.art.likeness_library import fragment_evidence
        start = time.perf_counter()
        candidate = json.loads((args.candidate / "realignment.json").read_bytes())
        prior = fragment_review.ingest(candidate, json.loads(args.feedback.read_bytes()))
        run, vectors, _, binding = review_packet.load_experiment(args.experiment)
        labels = json.loads(label_path.read_bytes())
        evidence = fragment_evidence.evaluate(candidate, run, vectors, labels)
        reversed_candidate, reversed_run = copy.deepcopy((candidate, run))
        for key in ("rows", "identities", "appearances"):
            reversed_candidate[key].reverse()
        reversed_run["photos"].reverse()
        repeated = fragment_evidence.evaluate(reversed_candidate, reversed_run, dict(reversed(list(vectors.items()))), labels)
        if evidence != repeated:
            raise ValueError("fragment evidence differs with reversed inputs; no result accepted")
        packet = fragment_review.build(candidate, evidence, run, vectors, prior, max_photos=args.max_photos)
        reverse_packet = fragment_review.build(
            reversed_candidate, repeated, reversed_run, vectors, prior, max_photos=args.max_photos,
        )
        # Input-order probe has different serialized candidate bytes, not different evidence.
        reverse_packet["candidateSHA256"] = packet["candidateSHA256"]
        reverse_packet["packetSHA256"] = fragment_review.digest({
            key: value for key, value in reverse_packet.items() if key != "packetSHA256"
        })
        if packet != reverse_packet:
            raise ValueError("fragment packet selection differs with reversed inputs")
        cache_path = pathlib.Path(binding["sourceRun"]) / "likeness-cache.json"
        cache = json.loads(cache_path.read_bytes())
        images, _ = review_packet.image_assets(packet, run, cache, out, write=False)
        print("General fragment evidence:", evidence["summary"])
        print("Prior identity-only answers:", prior["counts"])
        print("Next review:", packet["summary"])
        print(f"Preview/evidence seconds: {time.perf_counter()-start:.3f}; reverse verified; zero library writes")
        if not args.apply:
            print("Preview only: hashes/face evidence/photo scope verified; no context inference or output writes.")
            print(f"Would measure below-face context locally with: {args.context_checkpoint}")
            print(f"Report: {out / 'index.html'}")
            return 0
        context_start = time.perf_counter()
        context = appearance_context.measure(packet, run, cache, args.context_checkpoint)
        context_seconds = time.perf_counter() - context_start
        if initial_code != code_bindings() or any(shadow.digest(pathlib.Path(p)) != h for p, h in bindings.items()):
            raise ValueError("fragment code/input changed during measurement")
        out.mkdir(parents=True, exist_ok=False)
        images, outputs = review_packet.image_assets(packet, run, cache, out, write=True)
        for pid, row in context["photos"].items():
            if row["status"] != "measured":
                continue
            source = pathlib.Path(images[pid]["path"])
            if shadow.digest(source) != row["sourceSHA256"]:
                raise ValueError("context source changed during publication")
            name = f"images/{fragment_review.digest(pid)[:20]}-context.jpg"
            with Image.open(source) as image:
                crop = ImageOps.exif_transpose(image).convert("RGB").crop(row["cropPixels"])
                ImageOps.contain(crop, (300, 360)).save(out / name, format="JPEG", quality=86)
            images[pid]["context"] = name
            outputs[name] = shadow.digest(out / name)
        for name, obj in (
            ("evidence.json", evidence), ("prior-feedback.json", prior), ("packet.json", packet),
            ("context.json", context), ("display.json", images),
        ):
            (out / name).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")
            outputs[name] = shadow.digest(out / name)
        (out / "index.html").write_text(fragment_report.render(packet, images, context), encoding="utf-8")
        outputs["index.html"] = shadow.digest(out / "index.html")
        if initial_code != code_bindings() or any(shadow.digest(pathlib.Path(p)) != h for p, h in bindings.items()):
            raise ValueError("fragment code/input changed during publication")
        receipt = {
            "schemaVersion": 1, "kind": "fragment-experiment-receipt", "inputs": bindings,
            "code": initial_code, "outputs": outputs, "maxPhotos": args.max_photos,
            "reverseVerified": True, "libraryWrites": 0, "downloads": 0,
            "contextSeconds": context_seconds, "totalSecondsBeforeCheck": time.perf_counter() - start,
            "packages": {name: importlib.metadata.version(name) for name in ("numpy", "Pillow", "open_clip_torch", "torch")},
        }
        temporary = out / "receipt.json.partial"
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, out / "receipt.json")
        check(out, bindings, args.max_photos)
        print(f"Context: {context['summary']} in {context_seconds:.3f}s")
        print(f"Built and verified review: {out / 'index.html'}")
        return 0
    except (OSError, ValueError, KeyError, TypeError, ImportError) as error:
        print(f"likeness-fragment-trial: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
