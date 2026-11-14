"""Pair original-anchor view reconciliation with saved ordered-middle controls."""
import argparse
import copy
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.art import likeness_entrance_trial as publisher  # noqa: E402
from tools.art.likeness_library import entrance_trial, shadow, view_hypotheses, view_reconciliation  # noqa: E402


def codes():
    paths = (pathlib.Path(__file__).resolve(), pathlib.Path(view_hypotheses.__file__).resolve(),
             ROOT / "bin" / "likeness-hypothesis-trial.cmd")
    return {**publisher.codes(), **{str(p): shadow.digest(p) for p in paths}}


def construct(state, run, vectors, ledger, baseline, progress=None):
    evidence = entrance_trial.Evidence(state, run, vectors, ledger)
    middle = entrance_trial.recipes()[1]
    coalesced, reconciliation = view_reconciliation.build(evidence, middle)
    if reconciliation != baseline["viewReconciliation"]:
        raise ValueError("saved control view construction differs from current original anchors")
    reconciled, report = view_hypotheses.build(coalesced, reconciliation, middle)
    controls = [
        copy.deepcopy(next(v for v in baseline["variants"] if v["recipe"]["name"] == name))
        for name in ("ordered-middle", "ordered-middle-coalesced", "ordered-middle-coalesced-growth")
    ]
    for control in controls:
        control["summary"]["reusedVerifiedControl"] = True
    output = controls
    for growth in (False, True):
        recipe = {
            **copy.deepcopy(middle), "name": "ordered-middle-reconciled" + ("-growth" if growth else ""),
            "growth": growth,
        }
        variant = entrance_trial.run_variant(reconciled, recipe)
        view_hypotheses.annotate(variant, reconciled, report)
        output.append(variant)
        if progress:
            progress(f'{recipe["name"]}: {variant["summary"]}')
    return {
        "kind": "original-anchor-hypothesis-trial", "schemaVersion": 1,
        "defaultVariant": "ordered-middle-reconciled",
        "variants": output, "viewReconciliation": report,
        "installedPolicyChanged": False, "installedMoves": 0,
        "limits": [*baseline["limits"], *report["hypothesisReconciliation"]["limits"]],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, required=True)
    parser.add_argument("--baseline", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if not args.source.is_absolute() or not args.baseline.is_absolute():
            raise ValueError("--source and --baseline must be absolute")
        out = publisher.output_path(args.out)
        if out.resolve() in (args.source.resolve(), args.baseline.resolve()):
            raise ValueError("output must be separate from both inputs")
        if args.check or args.apply and out.exists():
            receipt = json.loads((out / "receipt.json").read_bytes())
            if (receipt["kind"] != "original-anchor-hypothesis-receipt"
                    or receipt["source"] != str(args.source) or receipt["baseline"] != str(args.baseline)
                    or receipt["code"] != codes() or not receipt["reverseVerified"]
                    or receipt["installedMoves"] or receipt["recipe"] != entrance_trial.recipes()[1]):
                raise ValueError("hypothesis source/code/recipe contract changed")
            publisher.diagnostics.verify({**receipt["inputs"], **receipt["code"]})
            publisher.diagnostics.verify({
                str(publisher.review_packet.safe_path(out, p)): digest for p, digest in receipt["outputs"].items()
            })
            print(f"Verified original-anchor hypothesis trial: {out}")
            return 0
        baseline, baseline_bindings = publisher.load_reuse(args.baseline, args.source, True)
        state, run, vectors, _, ledger, _, bindings = publisher.diagnostics.load(args.source)
        bindings.update(baseline_bindings)
        code = codes()
        published = {p["path"]: p["sha256"] for p in run["publishedFiles"]}
        for photo in run["photos"]:
            path = publisher.review_packet.safe_path(pathlib.Path(run["workingRoot"]), photo["destination"])
            expected = published.get(photo["destination"])
            if not expected or shadow.digest(path) != expected:
                raise ValueError(f"installed viewer source differs: {photo['photoId']}")
            bindings[str(path)] = expected
        print(
            f"Preview: {len(state['rows'])} saved photos; reuse three verified controls; "
            "two paired original-anchor reconciliation variants. Existing union lineages only; "
            "complete-link, all-reference witnesses, complete joint-core qualification; "
            "all outside/uncertified rivals retained. No models, installed moves, policy changes or intake.",
            flush=True,
        )
        if not args.apply:
            return 0
        start = time.perf_counter()
        result = construct(state, run, vectors, ledger, baseline, progress=lambda s: print(s, flush=True))
        reverse_state = {**state, "rows": list(reversed(state["rows"])),
                         "appearances": list(reversed(state["appearances"]))}
        reverse = construct(
            reverse_state, run, dict(reversed(list(vectors.items()))),
            {**ledger, "pairs": list(reversed(ledger["pairs"]))}, baseline,
        )
        if publisher.semantic(result) != publisher.semantic(reverse):
            raise ValueError("hypothesis trial differs under reversed inputs")
        staging = out.with_name(out.name + ".partial")
        staging.mkdir(parents=True, exist_ok=False)
        (staging / "trial.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        (staging / "index.html").write_text(publisher.render(result, state, run), encoding="utf-8")
        outputs = {p.name: shadow.digest(p) for p in staging.iterdir()}
        publisher.diagnostics.verify({**bindings, **code})
        receipt = {
            "kind": "original-anchor-hypothesis-receipt", "source": str(args.source),
            "baseline": str(args.baseline), "inputs": bindings, "code": code, "outputs": outputs,
            "recipe": entrance_trial.recipes()[1], "reverseVerified": True, "installedMoves": 0,
            "elapsedSeconds": time.perf_counter() - start,
        }
        (staging / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        staging.rename(out)
        print(f"Published {out / 'index.html'} ({receipt['elapsedSeconds']:.3f}s).")
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(f"Hypothesis trial failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
