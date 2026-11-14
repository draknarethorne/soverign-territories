"""Run saved-population reference/member candidates without intake or library mutation."""
import argparse
import copy
import json
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.art import likeness_character_packet as character_cli  # noqa: E402
from tools.art.likeness_library import (  # noqa: E402
    character_packet, member_outcomes, realignment_evaluation, realignment_report,
    reference_report, reference_trial, review_packet, shadow,
)
from tools.art.likeness_review_packet import output_path  # noqa: E402


def code_bindings():
    modules = (
        pathlib.Path(__file__), pathlib.Path(reference_trial.__file__),
        pathlib.Path(reference_report.__file__), pathlib.Path(character_packet.__file__),
        pathlib.Path(review_packet.__file__), pathlib.Path(shadow.__file__),
        pathlib.Path(character_cli.__file__),
        pathlib.Path(member_outcomes.__file__),
        pathlib.Path(realignment_evaluation.__file__), pathlib.Path(realignment_report.__file__),
    )
    paths = {*modules, *(pathlib.Path(reference_trial.__file__).with_name(name) for name in (
        *shadow.REPLAY_MODULES, "protection.py", "thumbnails.py", "feedback.py",
    ))}
    paths.add(ROOT / "tools" / "art" / "likeness_review_packet.py")
    return {str(path.relative_to(ROOT)): shadow.digest(path) for path in sorted(paths)}


def verify_inputs(experiment, character_directory, answers_path):
    receipt_path = character_directory / "receipt.json"
    receipt = json.loads(receipt_path.read_bytes())
    inputs = {path: shadow.digest(pathlib.Path(path)) for path in receipt["inputs"]}
    packet = character_cli.check(character_directory, inputs)
    if packet["binding"]["shadowReceiptSHA256"] != shadow.digest(experiment / "receipt.json"):
        raise ValueError("character answers and experiment are not bound to the same baseline")
    answers = json.loads(answers_path.read_bytes())
    character_packet.validate_answers(packet, answers)
    if any(item["choice"] == "unreviewed" for group in answers["characters"] for item in group["decisions"]):
        raise ValueError("reference experiment requires completed character decisions")
    paths = [
        receipt_path, character_directory / "packet.json", character_directory / "effective-labels.json",
        answers_path, *(experiment / name for name in ("receipt.json", "scope.json", "experiment.json")),
    ]
    binding = {str(path): shadow.digest(path) for path in paths}
    binding.update(inputs)
    binding.update(receipt["evidenceInputs"])
    return packet, answers, binding


def check(out, bindings, compare_order, *, realign=False):
    receipt = json.loads((out / "receipt.json").read_bytes())
    if (receipt["inputs"] != bindings or receipt["code"] != code_bindings()
            or receipt["compareOrder"] != compare_order):
        raise ValueError("reference experiment inputs/code/parameters changed; use a new --out")
    if receipt.get("realign", False) != realign:
        raise ValueError("realignment mode changed; use a new --out")
    expected_names = {"result.json", "reference-seed.json", "member-outcomes.json", "index.html", "display.json"}
    if realign:
        expected_names.update(("realignment.json", "realignment.html", "evaluation.json"))
        engine = ROOT / "tools" / "art" / "likeness_library" / "realignment.py"
        if receipt.get("realignmentCodeSHA256") != shadow.digest(engine):
            raise ValueError("realignment implementation changed; use a new --out")
    if not expected_names <= receipt["outputs"].keys():
        raise ValueError("reference experiment output receipt is incomplete")
    for name, digest in receipt["outputs"].items():
        if shadow.digest(review_packet.safe_path(out, name)) != digest:
            raise ValueError(f"reference experiment output changed: {name}")
    display = json.loads((out / "display.json").read_bytes())
    for image in display["images"].values():
        if shadow.digest(pathlib.Path(image["path"])) != image["sha256"]:
            raise ValueError(f"reference experiment displayed source changed: {image['path']}")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True, type=pathlib.Path)
    parser.add_argument("--character-packet", required=True, type=pathlib.Path)
    parser.add_argument("--answers", required=True, type=pathlib.Path)
    parser.add_argument("--out", required=True)
    parser.add_argument("--compare-order", action="store_true", help="Repeat with reversed input order; require identical result")
    parser.add_argument("--realign", action="store_true",
                        help="Also rebuild all provisional references and member/face-view hypotheses; never install")
    parser.add_argument("--max-photos", type=int, default=4000, help="Refuse full saved population overflow; never truncate")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if any(not path.is_absolute() for path in (args.experiment, args.character_packet, args.answers)):
            raise ValueError("all reference trial input paths must be absolute")
        if args.max_photos < 1:
            raise ValueError("--max-photos must be positive")
        started = time.perf_counter()
        initial_code = code_bindings()
        realignment_code = None
        if args.realign:
            from tools.art.likeness_library import realignment
            realignment_code = shadow.digest(pathlib.Path(realignment.__file__))
        packet, answers, inputs = verify_inputs(args.experiment, args.character_packet, args.answers)
        out = output_path(args.out)
        if args.check or args.apply and out.exists():
            receipt = check(out, inputs, args.compare_order, realign=args.realign)
            if receipt["photoCount"] > args.max_photos:
                raise ValueError("saved population exceeds --max-photos; no silent truncation")
            print(f"Verified frozen-reference experiment: {out / 'index.html'}")
            return 0
        run, vectors, _scope, binding = review_packet.load_experiment(args.experiment)
        if len(run["photos"]) > args.max_photos:
            raise ValueError("full saved population exceeds --max-photos; no silent truncation")
        effective = json.loads((args.character_packet / "effective-labels.json").read_bytes())
        phase_seconds = {"load": time.perf_counter() - started}
        phase_started = time.perf_counter()
        result = reference_trial.evaluate(run, vectors, packet, answers, effective)
        result["evidenceDiagnostics"] = reference_report.evidence_diagnostics(result)
        outcomes = member_outcomes.build(result, run)
        phase_seconds["frozenControl"] = time.perf_counter() - phase_started
        candidate, evaluation = None, None
        if args.realign:
            phase_started = time.perf_counter()
            candidate = realignment.evaluate(run, vectors, packet, answers, effective)
            realignment_report.validate_candidate(candidate, run)
            phase_seconds["generalCandidate"] = time.perf_counter() - phase_started
            phase_started = time.perf_counter()
            evaluation = realignment_evaluation.evaluate(
                run, vectors, packet, answers, effective, realignment.evaluate,
            )
            phase_seconds["labelBlindedDiagnostic"] = time.perf_counter() - phase_started
        trial_seconds = time.perf_counter() - started
        if args.compare_order:
            phase_started = time.perf_counter()
            reversed_run = copy.deepcopy(run)
            reversed_run["photos"].reverse()
            reversed_run["finalMembershipAudit"]["rows"].reverse()
            repeated = reference_trial.evaluate(
                reversed_run, dict(reversed(list(vectors.items()))), packet, answers, effective,
            )
            repeated["evidenceDiagnostics"] = reference_report.evidence_diagnostics(repeated)
            if result != repeated or outcomes != member_outcomes.build(repeated, reversed_run):
                raise ValueError("reference trial differs with reversed inputs; no result accepted")
            if args.realign:
                reversed_candidate = realignment.evaluate(
                    reversed_run, dict(reversed(list(vectors.items()))), packet, answers, effective,
                )
                if candidate != reversed_candidate:
                    raise ValueError("general realignment differs with reversed inputs; no result accepted")
            phase_seconds["reverseComparison"] = time.perf_counter() - phase_started
        display = {"usedPhotoIds": reference_report.select_photos(result)}
        if args.realign:
            display["usedPhotoIds"] = sorted(set(display["usedPhotoIds"]) | set(realignment_report.select_photos(candidate)))
        cache = json.loads((pathlib.Path(binding["sourceRun"]) / "likeness-cache.json").read_bytes())
        _images, _outputs = review_packet.image_assets(display, run, cache, out)
        if code_bindings() != initial_code:
            raise ValueError("experiment implementation changed during execution; result not accepted")
        if args.realign and shadow.digest(pathlib.Path(realignment.__file__)) != realignment_code:
            raise ValueError("realignment implementation changed during execution; result not accepted")
        print(f"Frozen-reference results: {result['summary']}")
        print(f"Member/reference proposals (not installed): {outcomes['summary']}")
        if args.realign:
            print(f"General realignment candidate (not installed): {candidate['summary']}")
            print(f"Label-blinded diagnostic (not independent held-out accuracy): {evaluation['summary']}")
            print(f"Phase seconds: {phase_seconds}")
        print(f"Displayed photos: {len(display['usedPhotoIds'])}; repeat/reverse verified: {args.compare_order}")
        print(f"Input load and first trial: {trial_seconds:.3f}s; no intake, model calls or library writes")
        if not args.apply:
            print(f"Preview only; nothing written. Proposed report: {out / 'index.html'}")
            return 0
        out.mkdir(parents=True, exist_ok=False)
        display["images"], outputs = review_packet.image_assets(display, run, cache, out, write=True)
        seed = {
            "schemaVersion": 1, "kind": "experimental-frozen-character-references",
            "binding": inputs,
            "characters": [{
                "folder": group["folder"],
                "referencePhotoIds": sorted(item["photoId"] for item in group["decisions"] if item["choice"] == "reference"),
                "otherDecisions": sorted(
                    (item for item in group["decisions"] if item["choice"] != "reference"),
                    key=lambda item: item["photoId"],
                ),
            } for group in answers["characters"]],
            "boundary": "Experimental reference influence only; no placement, protection, workflow or runtime policy changes.",
            "growth": "Frozen; no new query is admitted during this experiment.",
        }
        for name, content in (
            ("result.json", json.dumps(result, indent=2) + "\n"),
            ("reference-seed.json", json.dumps(seed, indent=2) + "\n"),
            ("member-outcomes.json", json.dumps(outcomes, indent=2) + "\n"),
            ("display.json", json.dumps(display, indent=2) + "\n"),
            ("index.html", reference_report.render(result, display["images"], outcomes=outcomes)),
        ):
            (out / name).write_text(content, encoding="utf-8")
            outputs[name] = shadow.digest(out / name)
        if args.realign:
            for name, content in (
                ("realignment.json", json.dumps(candidate, indent=2, allow_nan=False) + "\n"),
                ("evaluation.json", json.dumps(evaluation, indent=2, allow_nan=False) + "\n"),
                ("realignment.html", realignment_report.render(candidate, display["images"], run, evaluation=evaluation)),
            ):
                (out / name).write_text(content, encoding="utf-8")
                outputs[name] = shadow.digest(out / name)
        if (code_bindings() != initial_code
                or any(shadow.digest(pathlib.Path(path)) != digest for path, digest in inputs.items())):
            raise ValueError("experiment evidence changed during execution; result not accepted")
        if args.realign and shadow.digest(pathlib.Path(realignment.__file__)) != realignment_code:
            raise ValueError("realignment implementation changed during publication; result not accepted")
        receipt = {
            "schemaVersion": 1, "inputs": inputs, "code": initial_code,
            "outputs": outputs, "compareOrder": args.compare_order,
            "photoCount": len(run["photos"]), "firstTrialSeconds": trial_seconds,
            "totalSecondsBeforeCheck": time.perf_counter() - started,
            "libraryWrites": 0, "modelCalls": 0, "imageReads": len(display["images"]),
            "realign": args.realign, "realignmentCodeSHA256": realignment_code,
            "phaseSeconds": phase_seconds,
        }
        temporary = out / "receipt.json.partial"
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, out / "receipt.json")
        check(out, inputs, args.compare_order, realign=args.realign)
        print(f"Built and verified reference experiment: {out / 'index.html'}")
        if args.realign:
            print(f"Whole-library candidate: {out / 'realignment.html'}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"likeness-reference-trial: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
