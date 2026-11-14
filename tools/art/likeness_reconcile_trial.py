"""Reconcile reviewed fragments in frozen report-only ablations, without installation."""
import argparse
import copy
import html
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.art import likeness_fragment_trial as source_cli  # noqa: E402
from tools.art.likeness_library import (  # noqa: E402
    fragment_evidence, fragment_reconciliation, fragment_review, review_packet, shadow,
)
from tools.art.likeness_review_packet import output_path  # noqa: E402


def codes():
    paths = [pathlib.Path(__file__), pathlib.Path(fragment_reconciliation.__file__),
             pathlib.Path(fragment_evidence.__file__), pathlib.Path(fragment_review.__file__)]
    return {str(p): shadow.digest(p) for p in paths}


def load_inputs(source, answers):
    receipt = json.loads((source / "receipt.json").read_bytes())
    for path, digest in receipt["inputs"].items():
        if shadow.digest(pathlib.Path(path)) != digest:
            raise ValueError(f"source input changed: {path}")
    expected_code = {str(pathlib.Path(p).resolve()): h for p, h in receipt["code"].items()}
    current_code = {str(pathlib.Path(p).resolve()): h for p, h in source_cli.code_bindings().items()}
    if expected_code != current_code:
        raise ValueError("review source code changed")
    required = {"packet.json", "evidence.json", "context.json", "display.json", "index.html", "prior-feedback.json"}
    if not required <= receipt["outputs"].keys():
        raise ValueError("review source receipt incomplete")
    for name, digest in receipt["outputs"].items():
        if shadow.digest(review_packet.safe_path(source, name)) != digest:
            raise ValueError(f"review source output changed: {name}")
    for record in json.loads((source / "display.json").read_bytes()).values():
        if shadow.digest(pathlib.Path(record["path"])) != record["sha256"]:
            raise ValueError("review source photo changed")
    packet = json.loads((source / "packet.json").read_bytes())
    if fragment_review.digest({k: v for k, v in packet.items() if k != "packetSHA256"}) != packet["packetSHA256"]:
        raise ValueError("review source packet binding differs")
    inputs = {**receipt["inputs"], str(source / "receipt.json"): shadow.digest(source / "receipt.json"),
              str(answers): shadow.digest(answers)}
    for path, digest in receipt["code"].items():
        inputs[path] = digest
    return receipt, inputs


def check(out, inputs):
    receipt = json.loads((out / "receipt.json").read_bytes())
    if receipt["inputs"] != inputs or receipt["code"] != codes():
        raise ValueError("reconciliation inputs/code changed; use a new --out")
    for name, digest in receipt["outputs"].items():
        if shadow.digest(review_packet.safe_path(out, name)) != digest:
            raise ValueError(f"reconciliation output changed: {name}")
    if not {"ledger.json", "comparison.json", "index.html"} <= receipt["outputs"].keys():
        raise ValueError("reconciliation receipt incomplete")
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, required=True, help="Absolute verified fragment-trial report")
    parser.add_argument("--answers", type=pathlib.Path, required=True, help="Absolute returned fragment answers")
    parser.add_argument("--out", required=True, help="New absolute reports\\likeness-reassessment\\NAME")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if not args.source.is_absolute() or not args.answers.is_absolute():
            raise ValueError("source and answers must be absolute")
        out = output_path(args.out)
        receipt, inputs = load_inputs(args.source, args.answers)
        bound_code = codes()
        if args.check or args.apply and out.exists():
            check(out, inputs)
            print(f"Verified reconciliation: {out / 'index.html'}")
            return 0
        packet = json.loads((args.source / "packet.json").read_bytes())
        answers = json.loads(args.answers.read_bytes())
        def find_input(name):
            paths = [pathlib.Path(p) for p in receipt["inputs"] if pathlib.Path(p).name == name]
            if len(paths) != 1:
                raise ValueError(f"source requires one bound {name}")
            return paths[0]
        candidate = json.loads(find_input("realignment.json").read_bytes())
        effective = json.loads(find_input("effective-labels.json").read_bytes())
        experiment = find_input("experiment.json").parent
        run, vectors, _, _ = review_packet.load_experiment(experiment)
        repaired, ledger = fragment_reconciliation.prepare(candidate, packet, answers, effective, run)
        removed = sum(p["wasReference"] and p["referenceUse"] == "withdraw-in-shadow" for p in ledger["referenceProposals"])
        print(f"Bound pairs: {len(ledger['pairs'])}; associations: {len(ledger['associations'])}; "
              f"reference withdrawals in shadow: {removed}; unresolved: {len(ledger['unresolved'])}", flush=True)
        if not args.apply:
            print("Preview only: verified sources/evidence and proposed repair; no scoring, writes or library changes.")
            return 0
        started = time.perf_counter()
        direct = {"pairs": ledger["pairs"]}
        baseline = fragment_evidence.evaluate(candidate, run, vectors, direct)
        print("Label-updated baseline scored.", flush=True)
        repair = fragment_evidence.evaluate(repaired, run, vectors, direct)
        print("Reference repair scored.", flush=True)
        reversed_run = copy.deepcopy(run)
        reversed_run["photos"].reverse()
        def reverse(c):
            value = copy.deepcopy(c)
            for name in ("rows", "identities", "appearances"):
                value[name].reverse()
            return value
        repaired_reverse, ledger_reverse = fragment_reconciliation.prepare(
            candidate, packet, {**answers, "decisions": list(reversed(answers["decisions"]))}, effective, reversed_run,
        )
        # Answer serialization is provenance, not a decision dependency.
        ledger_reverse["answersSHA256"] = ledger["answersSHA256"]
        if repaired_reverse != repaired or ledger_reverse != ledger:
            raise ValueError("repair/ledger differs with answer/run order")
        for value, expected in ((candidate, baseline), (repaired, repair)):
            actual = fragment_evidence.evaluate(reverse(value), reversed_run, dict(reversed(list(vectors.items()))), direct)
            if actual != expected:
                raise ValueError("reconciliation evidence differs with reversed inputs")
        result = fragment_reconciliation.compare(baseline, repair, ledger)
        old = json.loads((args.source / "evidence.json").read_bytes())
        old_rows = {r["photoId"]: r for r in old["rows"]}
        result["labelUpdateSuggestionChanges"] = sum(
            row["suggestedFolder"] != old_rows[row["photoId"]]["suggestedFolder"] for row in baseline["rows"]
        )
        result["limits"] = ledger["limits"] + [
            "Same direct labels used in all four variants; label effects separated from reference repair.",
            "Association-only annotates direct evidence; it does not pool cores, bypass margins or discover unlabelled identities.",
            "Saved subgroup qualification is not full routing, protection, readiness or workflow acceptance.",
        ]
        if bound_code != codes() or any(shadow.digest(pathlib.Path(p)) != h for p, h in inputs.items()):
            raise ValueError("input/code changed during reconciliation")
        out.mkdir(parents=True, exist_ok=False)
        outputs = {}
        summaries = {key: value["summary"] for key, value in result["variants"].items()}
        text = ("<!doctype html><meta charset=utf-8><title>Fragment reconciliation comparison</title>"
                "<h1>Reference repair and direct fragment association</h1>"
                "<p>Experimental only: no installed changes, automatic merges or accepted accuracy.</p>"
                "<h2>Four variants</h2><pre>" + html.escape(json.dumps(summaries, indent=2)) +
                "</pre><h2>Reference proposals and unresolved cases</h2><pre>" +
                html.escape(json.dumps({key: ledger[key] for key in ("referenceProposals", "unresolved", "conflicts")}, indent=2)) +
                "</pre><h2>Limits</h2><pre>" + html.escape("\n".join(result["limits"])) +
                '</pre><p><a href="comparison.json">All per-photo old/new outcomes</a> | '
                '<a href="ledger.json">Bound direct evidence and reference proposals</a></p>')
        for name, value in (("ledger.json", ledger), ("comparison.json", result)):
            (out / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
            outputs[name] = shadow.digest(out / name)
        (out / "index.html").write_text(text, encoding="utf-8")
        outputs["index.html"] = shadow.digest(out / "index.html")
        final = {"schemaVersion": 1, "kind": "fragment-reconciliation-receipt", "inputs": inputs,
                 "code": bound_code, "outputs": outputs, "reverseVerified": True,
                 "seconds": time.perf_counter() - started, "libraryWrites": 0}
        (out / "receipt.json").write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
        check(out, inputs)
        print(json.dumps(summaries))
        print(f"Built and verified reconciliation: {out / 'index.html'}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"likeness-reconcile-trial: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
