"""Validate completed pair labels and build a bounded character-intent review."""
import argparse
import hashlib
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.art.likeness_library import character_packet, feedback, review_packet, shadow  # noqa: E402
from tools.art.likeness_review_packet import output_path  # noqa: E402


def code_bindings():
    paths = [
        pathlib.Path(__file__), pathlib.Path(character_packet.__file__), pathlib.Path(feedback.__file__),
        pathlib.Path(review_packet.__file__), pathlib.Path(shadow.__file__),
        pathlib.Path(review_packet.__file__).with_name("thumbnails.py"),
        pathlib.Path(review_packet.__file__).with_name("scoring.py"),
        ROOT / "tools" / "art" / "likeness_review_packet.py",
    ]
    return {str(path.relative_to(ROOT)): shadow.digest(path) for path in paths}


def input_bindings(paths):
    return {str(path): shadow.digest(path) for path in paths}


def check(out, inputs):
    receipt = json.loads((out / "receipt.json").read_bytes())
    if receipt["inputs"] != inputs or receipt["code"] != code_bindings():
        raise ValueError("character packet inputs/code changed; use a new --out")
    if not {"packet.json", "effective-labels.json", "index.html"} <= set(receipt["outputs"]):
        raise ValueError("character packet receipt is incomplete")
    for relative, expected in receipt["outputs"].items():
        if shadow.digest(review_packet.safe_path(out, relative)) != expected:
            raise ValueError(f"character packet output changed: {relative}")
    for path, digest in receipt["evidenceInputs"].items():
        if shadow.digest(pathlib.Path(path)) != digest:
            raise ValueError(f"saved experiment input changed: {path}")
    packet = json.loads((out / "packet.json").read_bytes())
    for record in packet["images"].values():
        if shadow.digest(pathlib.Path(record["path"])) != record["sha256"]:
            raise ValueError(f"displayed source changed: {record['path']}")
    return packet


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True, type=pathlib.Path)
    parser.add_argument("--review-packet", required=True, type=pathlib.Path, help="Existing completed pair packet directory")
    parser.add_argument("--feedback", required=True, type=pathlib.Path, help="Raw completed pair-answer export")
    parser.add_argument("--clarifications", required=True, type=pathlib.Path, help="Separate documented pair overrides")
    parser.add_argument("--out", required=True)
    parser.add_argument("--answers", type=pathlib.Path, help="With --check: validate exported character answers, no writes")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        paths = (args.experiment, args.review_packet, args.feedback, args.clarifications)
        if any(not path.is_absolute() for path in paths):
            raise ValueError("all input paths must be absolute")
        if args.answers and (not args.check or not args.answers.is_absolute()):
            raise ValueError("--answers requires --check and an absolute file")
        out = output_path(args.out)
        experiment_files = [args.experiment / name for name in ("receipt.json", "scope.json", "experiment.json")]
        source_paths = [
            *experiment_files, args.review_packet / "packet.json", args.review_packet / "receipt.json",
            args.feedback, args.clarifications,
        ]
        inputs = input_bindings(source_paths)
        if args.check or args.apply and out.exists():
            packet = check(out, inputs)
            if args.answers:
                answers = json.loads(args.answers.read_bytes())
                character_packet.validate_answers(packet, answers)
                reviewed = sum(
                    item["choice"] != "unreviewed"
                    for group in answers["characters"] for item in group["decisions"]
                )
                print(f"Character answers valid: {reviewed} reviewed; no changes applied")
            print(f"Verified: {out / 'index.html'}")
            return 0
        baseline = json.loads((args.review_packet / "packet.json").read_bytes())
        old_receipt = json.loads((args.review_packet / "receipt.json").read_bytes())
        if old_receipt["outputs"]["packet.json"] != inputs[str(args.review_packet / "packet.json")]:
            raise ValueError("original pair packet differs from its receipt")
        effective = feedback.ingest(
            baseline, json.loads(args.feedback.read_bytes()), json.loads(args.clarifications.read_bytes()),
        )
        run, vectors, _scope, binding = review_packet.load_experiment(args.experiment)
        if baseline["binding"] != binding:
            raise ValueError("completed review belongs to a different experiment")
        effective["inputFiles"] = inputs
        packet = character_packet.build_packet(run, vectors, effective, {
            **binding, "pairPacketSHA256": baseline["packetSHA256"],
            "feedbackFileSHA256": inputs[str(args.feedback)],
            "clarificationsFileSHA256": inputs[str(args.clarifications)],
        })
        count = sum(len(group["cards"]) for group in packet["characters"])
        if count > 60 or len(packet["usedPhotoIds"]) > 60:
            raise ValueError("character confirmation exceeds explicit 60-card/60-photo budget")
        cache = json.loads((pathlib.Path(binding["sourceRun"]) / "likeness-cache.json").read_bytes())
        images, _outputs = review_packet.image_assets(packet, run, cache, out)
        print(f"Validated pair feedback: {effective['summary']}")
        print(f"Character packet: {len(packet['characters'])} characters / {count} decisions / {len(images)} photos")
        if not args.apply:
            print("Preview only: no files written, no inference, no library changes")
            return 0
        out.mkdir(parents=True, exist_ok=False)
        images, outputs = review_packet.image_assets(packet, run, cache, out, write=True)
        packet["images"] = images
        packet["packetSHA256"] = hashlib.sha256(
            json.dumps(packet, sort_keys=True, separators=(",", ":")).encode(),
        ).hexdigest()
        for name, value in (
            ("effective-labels.json", json.dumps(effective, indent=2) + "\n"),
            ("packet.json", json.dumps(packet, indent=2) + "\n"),
            ("index.html", character_packet.render(packet)),
        ):
            (out / name).write_text(value, encoding="utf-8")
            outputs[name] = shadow.digest(out / name)
        evidence = json.loads((args.experiment / "receipt.json").read_bytes())["provenance"]["inputs"]
        receipt = {
            "schemaVersion": 1, "inputs": inputs, "code": code_bindings(), "outputs": outputs,
            "evidenceInputs": {record["path"]: record["sha256"] for record in evidence.values()},
            "libraryWrites": 0, "modelCalls": 0, "cardCount": count,
        }
        if input_bindings(source_paths) != inputs:
            raise ValueError("feedback or experiment changed during generation; output is not accepted")
        temporary = out / "receipt.json.partial"
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, out / "receipt.json")
        check(out, inputs)
        print(f"Built and verified: {out / 'index.html'}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"likeness-character-packet: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
