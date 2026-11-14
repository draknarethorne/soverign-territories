"""Build a read-only visual label packet from verified shadow and final-audit evidence."""
import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.art.likeness_library import review_packet, shadow  # noqa: E402


def output_path(value):
    path = pathlib.Path(value)
    if not path.is_absolute():
        raise ValueError("--out must be an absolute generated-report directory")
    path = path.resolve()
    report_root = (ROOT / "reports" / "likeness-reassessment").resolve()
    if path == report_root or not path.is_relative_to(report_root):
        raise ValueError("--out must be a named directory inside reports\\likeness-reassessment")
    ignored = subprocess.run(
        ["git", "check-ignore", "--quiet", str(path / "receipt.json")], cwd=ROOT, check=False,
    )
    if ignored.returncode != 0:
        raise ValueError("report output must be verified git-ignored")
    return path


def code_bindings():
    return {
        str(path.relative_to(ROOT)): shadow.digest(path)
        for path in (pathlib.Path(__file__), pathlib.Path(review_packet.__file__),
                     pathlib.Path(review_packet.__file__).with_name("thumbnails.py"),
                     pathlib.Path(shadow.__file__), pathlib.Path(shadow.__file__).with_name("scoring.py"))
    }


def check(out, experiment, neighbours):
    receipt = json.loads((out / "receipt.json").read_bytes())
    if (receipt["shadowReceiptSHA256"] != shadow.digest(experiment / "receipt.json")
            or receipt["neighbours"] != neighbours or receipt["code"] != code_bindings()):
        raise ValueError("report inputs, parameters or code changed; use a new --out")
    shadow_receipt = json.loads((experiment / "receipt.json").read_bytes())
    for name, binding in shadow_receipt["provenance"]["inputs"].items():
        if pathlib.Path(binding["path"]).name != name or shadow.digest(pathlib.Path(binding["path"])) != binding["sha256"]:
            raise ValueError(f"baseline input changed: {name}")
    for name, expected in shadow_receipt["outputs"].items():
        if name not in {"scope.json", "experiment.json"} or shadow.digest(experiment / name) != expected:
            raise ValueError(f"shadow output changed: {name}")
    for name, expected in receipt["outputs"].items():
        if shadow.digest(review_packet.safe_path(out, name)) != expected:
            raise ValueError(f"report output changed: {name}")
    packet = json.loads((out / "packet.json").read_bytes())
    for image in packet["images"].values():
        if shadow.digest(pathlib.Path(image["path"])) != image["sha256"]:
            raise ValueError(f"displayed baseline photo changed: {image['path']}")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True, type=pathlib.Path, help="Absolute verified shadow output directory")
    parser.add_argument("--out", required=True, help="Absolute new reports\\likeness-reassessment\\NAME directory")
    parser.add_argument("--neighbours", type=int, default=12, choices=range(25), help="Additional distinct competing identities (0-24)")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true", help="Verify inputs/cases/source hashes; no images or report written (default)")
    modes.add_argument("--apply", action="store_true", help="Write bounded report thumbnails/HTML/JSON only; no library changes")
    modes.add_argument("--check", action="store_true", help="Verify report, sources and receipts read-only")
    args = parser.parse_args(argv)
    try:
        if not args.experiment.is_absolute():
            raise ValueError("--experiment must be absolute")
        experiment = args.experiment.resolve()
        out = output_path(args.out)
        if args.check or args.apply and out.exists():
            receipt = check(out, experiment, args.neighbours)
            print(f"Verified packet: {out / 'index.html'} ({receipt['caseCount']} cases)")
            return 0
        started = time.perf_counter()
        run, vectors, scope, binding = review_packet.load_experiment(experiment)
        packet = review_packet.build_packet(run, vectors, scope, binding, neighbours=args.neighbours)
        if len(packet["cases"]) > 100 or len(packet["usedPhotoIds"]) > 700:
            raise ValueError("packet exceeds 100-case / 700-unique-photo review budget; narrow the explicit scope")
        cache_path = pathlib.Path(binding["sourceRun"]) / "likeness-cache.json"
        cache = json.loads(cache_path.read_bytes())
        # Preview verifies the same files without decoding/resizing or writing them.
        images, _outputs = review_packet.image_assets(packet, run, cache, out)
        print(f"Packet: {len(packet['seedIdentities'])} seed identities, {len(packet['cases'])} cases, "
              f"{len(images)} unique photos from {scope['identityCount']} scoped identities")
        print(f"Final saved-score arithmetic: {packet['finalScoreParity']}")
        if not args.apply:
            print(f"Preview verified; no report writes or library changes. Output: {out / 'index.html'}")
            return 0
        out.mkdir(parents=True, exist_ok=False)
        images, outputs = review_packet.image_assets(packet, run, cache, out, write=True)
        packet["images"] = images
        packet["packetSHA256"] = hashlib.sha256(
            json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        for name, value in (("packet.json", json.dumps(packet, indent=2) + "\n"),
                            ("index.html", review_packet.render(packet))):
            (out / name).write_text(value, encoding="utf-8")
            outputs[name] = shadow.digest(out / name)
        receipt = {
            "schemaVersion": 1, "shadowReceiptSHA256": binding["shadowReceiptSHA256"],
            "neighbours": args.neighbours, "code": code_bindings(), "outputs": outputs,
            "caseCount": len(packet["cases"]), "uniquePhotoCount": len(images),
            "secondsBeforeCheck": time.perf_counter() - started,
            "libraryWrites": 0, "modelCalls": 0,
        }
        temporary = out / "receipt.json.partial"
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, out / "receipt.json")
        check(out, experiment, args.neighbours)
        print(f"Built and verified: {out / 'index.html'}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"likeness-review-packet: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
