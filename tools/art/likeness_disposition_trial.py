"""Build a no-rescoring disposition handoff from verified reconciliation evidence."""
import argparse
import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.art import likeness_reconcile_trial as parent  # noqa: E402
from tools.art.likeness_library import fragment_disposition, fragment_review, review_packet, shadow  # noqa: E402
from tools.art.likeness_review_packet import output_path  # noqa: E402


def codes():
    return {str(p.resolve()): shadow.digest(p) for p in (
        pathlib.Path(__file__), pathlib.Path(fragment_disposition.__file__),
        pathlib.Path(fragment_review.__file__), pathlib.Path(review_packet.__file__),
        pathlib.Path(shadow.__file__), pathlib.Path(parent.__file__),
    )}


def load(source):
    receipt = json.loads((source / "receipt.json").read_bytes())
    inputs = receipt["inputs"]
    for path, digest in inputs.items():
        if shadow.digest(pathlib.Path(path)) != digest:
            raise ValueError(f"disposition source input changed: {path}")
    expected = {str(pathlib.Path(p).resolve()): h for p, h in receipt["code"].items()}
    if expected != {str(pathlib.Path(p).resolve()): h for p, h in parent.codes().items()}:
        raise ValueError("disposition reconciliation code changed")
    if not {"ledger.json", "comparison.json", "index.html"} <= receipt["outputs"].keys():
        raise ValueError("disposition source receipt incomplete")
    for name, digest in receipt["outputs"].items():
        if shadow.digest(review_packet.safe_path(source, name)) != digest:
            raise ValueError(f"disposition source output changed: {name}")
    ledger = json.loads((source / "ledger.json").read_bytes())
    answer_paths = [
        pathlib.Path(p) for p in inputs if pathlib.Path(p).suffix == ".json"
        and json.loads(pathlib.Path(p).read_bytes()).get("kind") == "identity-fragment-answers"
    ]
    if len(answer_paths) != 1:
        raise ValueError("expected exactly one bound fragment answer export")
    answers_path = answer_paths[0]
    packet_source = [
        pathlib.Path(p).parent for p in inputs
        if pathlib.Path(p).name == "receipt.json"
        and json.loads(pathlib.Path(p).read_bytes()).get("kind") == "fragment-experiment-receipt"
    ]
    if len(packet_source) != 1:
        raise ValueError("expected one bound fragment review source")
    _, parent_inputs = parent.load_inputs(packet_source[0], answers_path)
    if parent_inputs != inputs:
        raise ValueError("disposition source provenance chain differs")
    packet = json.loads((packet_source[0] / "packet.json").read_bytes())
    answers = json.loads(answers_path.read_bytes())
    comparison = json.loads((source / "comparison.json").read_bytes())
    binding = {**inputs, **{str(source / name): digest for name, digest in receipt["outputs"].items()},
               str(source / "receipt.json"): shadow.digest(source / "receipt.json")}
    return packet, answers, ledger, comparison, binding


def check(out, inputs):
    receipt = json.loads((out / "receipt.json").read_bytes())
    if receipt["inputs"] != inputs or receipt["code"] != codes():
        raise ValueError("disposition inputs/code changed; use a new --out")
    if set(receipt["outputs"]) != {"dispositions.json", "index.html"}:
        raise ValueError("disposition output receipt incomplete")
    for name, digest in receipt["outputs"].items():
        if shadow.digest(review_packet.safe_path(out, name)) != digest:
            raise ValueError(f"disposition output changed: {name}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, required=True, help="Absolute verified reconciliation report")
    parser.add_argument("--out", required=True, help="New absolute reports\\likeness-reassessment\\NAME")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if not args.source.is_absolute():
            raise ValueError("--source must be absolute")
        out = output_path(args.out)
        packet, answers, ledger, comparison, inputs = load(args.source)
        if args.check or args.apply and out.exists():
            check(out, inputs)
            print(f"Verified disposition handoff: {out / 'index.html'}")
            return 0
        code = codes()
        result = fragment_disposition.build(packet, answers, ledger, comparison)
        reverse = fragment_disposition.build(
            {**packet, "cases": list(reversed(packet["cases"]))},
            answers, ledger,
            {**comparison, "variants": {k: {**v, "rows": list(reversed(v["rows"]))}
                                       for k, v in comparison["variants"].items()}},
        )
        if result != reverse:
            raise ValueError("disposition result differs under reversed inputs")
        print(json.dumps(result["summary"]))
        if not args.apply:
            print("Preview only; no scoring, image extraction, output writes or installed changes.")
            return 0
        if codes() != code or any(shadow.digest(pathlib.Path(p)) != h for p, h in inputs.items()):
            raise ValueError("disposition inputs/code changed during build")
        out.mkdir(parents=True, exist_ok=False)
        (out / "dispositions.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        body = (
            "<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>Appearance and family disposition handoff</title>"
            "<style>body{font:16px system-ui;margin:24px;max-width:1100px}pre{white-space:pre-wrap;"
            "overflow-wrap:anywhere}li{margin:12px 0}</style>"
            "<h1>Appearance, separate identity or unresolved?</h1>"
            "<p>Experimental handoff only. No new review assignment or installed changes.</p><pre>"
            + html.escape(json.dumps(result["summary"], indent=2)) + "</pre><ul>"
        )
        for case in result["cases"]:
            body += "<li>" + html.escape(
                f'{case["caseId"]}: {case["currentFolder"]} / {case["targetFolder"]}: '
                f'{case["disposition"]}; uncertain references: {len(case["uncertainReferencePhotoIds"])}. '
                f'Family: {case["family"]["status"]}; no type assigned.'
            ) + "</li>"
        body += "</ul><pre>" + html.escape("\n".join(result["limits"])) + (
            '</pre><a href="dispositions.json">Exact member scopes and conserved per-photo handoff</a>'
        )
        (out / "index.html").write_text(body, encoding="utf-8")
        receipt = {"schemaVersion": 1, "kind": "fragment-disposition-receipt", "inputs": inputs,
                   "code": code, "outputs": {name: shadow.digest(out / name) for name in ("dispositions.json", "index.html")},
                   "reverseVerified": True, "libraryWrites": 0, "scoringPasses": 0}
        (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        check(out, inputs)
        print(f"Built and verified disposition handoff: {out / 'index.html'}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"likeness-disposition-trial: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
