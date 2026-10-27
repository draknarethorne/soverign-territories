"""Immutable, opt-in erase-first sequence evidence; invoked by eraser-compare --sequence."""
import copy
import html
import json
import os
import pathlib
import tempfile
import time
from urllib.parse import quote

import numpy as np
import eraser_benchmark as benchmark
from intake_library import clutter, fill, pipeline
from likeness_library import gallery_chrome

preparation = benchmark.preparation


def recipe():
    return {"id": "intake-erase-first-v1", "baseline": "frozen v16, not rerun",
            "experiment": pipeline.EXPERIMENT_POLICY, "models": preparation.models.describe(),
            "pillow": benchmark.PIL.__version__, "opencv": benchmark.cv2.__version__,
            "selection": "comparison-only; never installed"}


def pill_icons(array, top, bottom):
    """Bounded bright outlined icon proposals beside an already detected pill, not semantic UI recognition."""
    height, width = array.shape[:2]
    bright = (array.min(axis=2) >= 240).astype(np.uint8)
    region = np.zeros_like(bright)
    region[max(0, top):min(height, bottom), int(.85 * width):] = 1
    bright *= region
    count, labels, stats, _ = benchmark.cv2.connectedComponentsWithStats(bright)
    found = []
    for label in range(1, count):
        x, y, w, h, area = map(int, stats[label])
        if (.025 * width <= w <= .1 * width and .01 * height <= h <= .06 * height
                and .5 <= w / h <= 2 and .06 <= area / (w * h) <= .65
                and y > top and y + h < bottom):
            mask = clutter.grow(clutter.fill_holes(labels == label), max(3, round(width * .004)))
            found.append(clutter.part("near-pill-icon-proposal", mask))
    return found


def head_overlay_candidates(image, row):
    """Unclipped UI masks for a separate, deliberately synthetic head-overlap trial."""
    array = np.asarray(image)
    pills = clutter.bubbles(array) if row["geometry"]["overlayDetected"] else []
    evidence = {"status": "skipped", "reason": "No detected screenshot search pill; not proof of clean.",
                "selected": False, "parts": [], "outsideMaskIdentical": None}
    row["experiment"]["headOverlay"] = evidence
    if not pills:
        return
    mask = np.zeros(array.shape[:2], dtype=bool)
    for item in pills:
        mask |= item["mask"]
        evidence["parts"].append({"kind": item["kind"], "box": item["box"]})
    # Keep nearby icon proposals bounded to the detected pill's vertical band.
    top = min(item["box"][1] for item in pills)
    bottom = max(item["box"][3] for item in pills)
    for item in clutter.glyphs(array, None, screenshot=True) + pill_icons(array, top, bottom):
        x0, y0, x1, y1 = item["box"]
        if x0 >= .8 * image.width and y0 >= top - .02 * image.height and y1 <= bottom + .02 * image.height:
            mask |= clutter.grow(item["mask"], max(2, round(min(image.size) * clutter.GROW)))
            evidence["parts"].append({"kind": "near-pill-icon-proposal", "box": [x0, y0, x1, y1]})
    coverage = float(mask.mean())
    evidence.update(coverage=coverage, maskPixels=int(mask.sum()))
    if coverage > pipeline.MAX_FILL:
        evidence.update(status="refused", reason="Complete UI mask exceeds existing maximum fill coverage.")
        return
    yield "head-overlay-mask", pipeline.mask_image(mask)
    try:
        painted = fill.fill(image, mask)
    except (OSError, RuntimeError, benchmark.cv2.error) as exc:
        evidence.update(status="failed", reason=f"Head-overlay reconstruction failed: {exc}")
        return
    if painted.size != image.size or not np.array_equal(np.asarray(painted)[~mask], array[~mask]):
        raise ValueError("head-overlay reconstruction changed dimensions or outside-mask pixels")
    evidence.update(status="comparison-only", outsideMaskIdentical=True,
                    reason="Face guard deliberately bypassed ONLY for this unselected synthetic candidate. "
                           "Hidden eyes/hair may be invented or distorted; not original/core likeness evidence. "
                           "Icon masks are heuristic proposals, not verified UI segmentation.")
    yield "head-overlay-reconstruction", painted


def plan(report, data, sources, expected):
    rows = {row["source"]: row for row in data["photos"]}
    result = []
    for source in sources:
        if source not in rows:
            raise ValueError(f"source is not in the frozen report: {source}")
        row = rows[source]
        if source in expected and expected[source] != row["sourceSha256"]:
            raise ValueError(f"selected source hash differs: {source}")
        benchmark.artifact(report, row["retained"], row["sourceSha256"])
        baseline = row.get("processing", {}).get("final", "control")
        variant = row["variants"].get(baseline)
        if variant:
            benchmark.artifact(report, variant["path"], variant["sha256"])
        result.append({"source": source, "sourceSha256": row["sourceSha256"],
                       "retained": row["retained"], "baseline": baseline,
                       "baselineArtifact": variant})
    return result


def page(data):
    esc = html.escape
    cards = []
    for row in data["rows"]:
        panels = []
        for name, image in row["images"].items():
            panels.append(f'<figure><figcaption>{esc(name)}: {image["size"]}</figcaption>'
                          f'<a href="{quote(image["path"])}"><img loading="lazy" '
                          f'src="{quote(image["padded"])}" alt="{esc(name)}"></a></figure>')
        def cell(value):
            return f'<td>{esc(str(value))}</td>'

        steps = "".join('<tr>' + "".join(cell(step.get(key, "-")) for key in
                        ("name", "status", "input", "candidate", "selected", "subjectLoss", "reason"))
                        + '</tr>' for step in row["evidence"]["steps"])
        notes = json.dumps({key: value for key, value in row["evidence"].items()
                            if key != "steps"}, indent=2)
        cards.append(f'<article><h2>{esc(row["source"])}</h2><p>{row["seconds"]:.3f}s; '
                              f'experimental final: {esc(row["evidence"]["final"])}</p>'
                              + ('<p>Head-overlay reconstruction is UNSELECTED, synthetic and may alter identity.</p>'
                                 if data.get("headOverlayEnabled") else '')
                              +
                     f'<div class="panels">{"".join(panels)}</div>'
                     '<div class="trace"><table><thead><tr><th>Step</th><th>Status</th>'
                     '<th>Input</th><th>Candidate</th><th>Selected in experiment only</th>'
                     '<th>Subject loss</th><th>Reason</th></tr></thead>'
                     f'<tbody>{steps}</tbody></table></div>'
                     f'<details><summary>Detection, coordinates, refusals and errors</summary>'
                     f'<pre>{esc(notes)}</pre></details></article>')
    prefix = gallery_chrome.reports_prefix(pathlib.Path(data["out"]),
                                          pathlib.Path(data["working"]) / "_reports")
    return ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width"><title>Intake sequence comparison</title>'
            f'<style>{gallery_chrome.CSS}article{{padding:16px;margin:12px;background:white}}'
            '.panels{display:flex;flex-wrap:wrap;gap:12px}figure{margin:0;width:260px}'
            'img{max-width:100%}td{overflow-wrap:anywhere}table{width:100%}'
            '.trace{overflow-x:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><body id="top">'
            + gallery_chrome.masthead(None, prefix, "Intake sequence comparison", links=False)
            + '<div class="site-page"><header><h1>Experimental erase-first comparison</h1>'
            '<p>Saved v16 versus first crop, guarded erase, one residual detection/crop and framing. '
            'Comparison only: no assignments or default recipe changes. Masks are heuristic, not verified '
            'overlay labels. A successful erase or residual miss does not prove clean. '
            + ('Composition proposals are comparison-only; missing hair/feet coverage cannot be disproved '
               'by zero mask loss. The experimental final retains the pre-composition image. '
               if data.get("compositionComparisonOnly") else '')
            + 'Native images open on click; previews fit/pad to 944x1104 without crop.</p>'
            f'<p>{len(data["rows"])} sources. Read every refusal and failure below.</p></header>'
            + "".join(cards) + gallery_chrome.footer("Experimental evidence - no library changes")
            + '</div></body></html>\n').encode("utf-8")


def verify(out, working, report, payload, *, recorded_out=None):
    data = json.loads(preparation.safe_path(working, out / "manifest.json").read_text(encoding="utf-8"))
    root, _, baseline, digest, report_working = benchmark.open_report(report)
    if (data["tool"] != "intake-sequence-benchmark" or data["schemaVersion"] != 1
            or data["root"] != str(root) or data["working"] != str(working)
            or report_working != working or data["out"] != str(recorded_out or out)
            or data["report"] != {"path": str(report), "sha256": digest}
            or data["selectionSha256"] != benchmark.sha(payload)):
        raise ValueError("experimental comparison binding differs")
    sources, expected = benchmark.parse_sources(payload)
    planned = plan(report, baseline, sources, expected)
    if [row["binding"] for row in data["rows"]] != planned:
        raise ValueError("experimental rows disagree with selected frozen sources")
    present = set()
    for path in out.rglob("*"):
        benchmark.unlinked(path)
        if path.is_file() and path != out / "manifest.json":
            present.add(path.relative_to(out).as_posix())
    if present != set(data["files"]):
        raise ValueError("experimental run has missing or extra files")
    for relative, digest in data["files"].items():
        benchmark.artifact(out, relative, digest)
    if (data["files"]["sources.json"] != benchmark.sha(payload)
            or data["files"]["index.html"] != benchmark.sha(page(data))):
        raise ValueError("experimental page/selection differs from manifest")
    for row in data["rows"]:
        for image in row["images"].values():
            if any(data["files"].get(image[key]) != image[key + "Sha256"] for key in ("path", "padded")):
                raise ValueError("experimental image evidence differs from file inventory")
    return data


def run(args):
    root, report, baseline, digest, working = benchmark.open_report(args.report)
    out = benchmark.run_location(working, report, args.out)
    sources, payload = benchmark.read_sources(args.sources)
    planned = plan(report, baseline, sources, benchmark.parse_sources(payload)[1])
    if args.check or (args.apply and out.exists()):
        saved = verify(out, working, report, payload)
        if saved.get("headOverlayEnabled", False) != bool(args.head_overlay):
            raise ValueError("head-overlay mode differs; use the matching flag or a new output directory")
        if args.apply and args.head_overlay and saved.get("headOverlayPolicy") != "full-pill-near-icon-v1":
            raise ValueError("head-overlay policy changed; use a new output directory")
        if args.apply and saved["recipe"] != recipe():
            raise ValueError("experimental policy changed; use a new output directory")
        print(f"Verified {len(saved['rows'])} experimental sequence rows without rewriting.")
        return 0
    print(f"Experimental erase-first comparison: {len(planned)} sources; no library/default changes.")
    if not args.apply:
        print("Preview only; apply uses pinned CPU subject/fill models; may download missing models.")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    by_source = {row["source"]: row for row in baseline["photos"]}
    with tempfile.TemporaryDirectory(prefix=".intake-sequence-", dir=out.parent) as temp:
        stage = pathlib.Path(temp) / "run"
        stage.mkdir()
        files = {}

        def put(relative, raw):
            preparation.write_new(stage / relative, raw)
            files[relative] = benchmark.sha(raw)
            return relative

        put("sources.json", payload)
        rows = []
        for index, binding in enumerate(planned, 1):
            row = copy.deepcopy(by_source[binding["source"]])
            original = preparation.decode_file(report / binding["retained"])
            images = {}
            folder = f"rows/{benchmark.sha(binding['source'].encode('utf-8'))[:24]}"

            def save(name, image):
                path = put(f"{folder}/{name}.png", benchmark.png(image))
                padded = put(f"{folder}/{name}-944.png", benchmark.png(benchmark.padded(image)))
                images[name] = {"path": path, "pathSha256": files[path], "padded": padded,
                                "paddedSha256": files[padded], "size": list(image.size)}

            save("original", original)
            saved = binding["baselineArtifact"]
            save("saved-v16-final", preparation.decode_file(report / saved["path"]) if saved else original)
            started = time.perf_counter()
            for name, image in pipeline.experimental_candidates(original, row):
                save(name, image)
            if args.head_overlay:
                for name, image in head_overlay_candidates(original, row):
                    save(name, image)
            rows.append({"source": binding["source"], "binding": binding,
                         "seconds": round(time.perf_counter() - started, 4),
                         "images": images, "evidence": row["experiment"]})
            print(f"Prepared sequence {index}/{len(planned)}: {binding['source']}", flush=True)
        data = {"schemaVersion": 1, "tool": "intake-sequence-benchmark", "recipe": recipe(),
                "root": str(root), "working": str(working), "out": str(out),
                "report": {"path": str(report), "sha256": digest},
                "selectionSha256": benchmark.sha(payload), "compositionComparisonOnly": True,
                "headOverlayEnabled": bool(args.head_overlay),
                "headOverlayPolicy": "full-pill-near-icon-v1" if args.head_overlay else None, "rows": rows}
        put("index.html", page(data))
        data["files"] = files
        preparation.write_new(stage / "manifest.json", (json.dumps(data, indent=2) + "\n").encode("utf-8"))
        verify(stage, working, report, payload, recorded_out=out)
        os.rename(stage, out)
    gallery_chrome.publish_banner(working / "_reports")
    print(f"Published experimental sequence comparison: {out / 'index.html'}")
    return 0
