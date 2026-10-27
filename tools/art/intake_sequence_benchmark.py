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
from PIL import Image, ImageFilter
import eraser_benchmark as benchmark
from intake_library import clutter, fill, pipeline
from likeness_library import gallery_chrome

preparation = benchmark.preparation
HEAD_POLICY = "cleaned-ui-reconstruction-picture-composition-v3"
ENHANCEMENT_POLICY = {
    "id": "native-comparison-v1",
    "denoise": preparation.RECIPE["denoise"], "tone": preparation.RECIPE["tone"],
    "sharpen": {"method": "UnsharpMask", "radius": 1.0, "percent": 75, "threshold": 3},
    "selection": "retain unenhanced prepared input; diagnostics are not calibrated quality rankings",
}


def enhancement_candidates(image, row):
    """Same native input for every candidate; low texture must not be labelled blur automatically."""
    array = np.asarray(image)
    gray = benchmark.cv2.cvtColor(array, benchmark.cv2.COLOR_RGB2GRAY)
    evidence = {
        "input": row["experiment"]["final"], "policy": ENHANCEMENT_POLICY,
        "diagnostics": {
            "laplacianVariance": round(float(benchmark.cv2.Laplacian(gray, benchmark.cv2.CV_64F).var()), 4),
            "meanLuminance": round(float(gray.mean()), 4),
            "darkFraction": round(float((gray <= 5).mean()), 6),
            "brightFraction": round(float((gray >= 250).mean()), 6),
        },
        "recommendation": row["experiment"]["final"],
        "reason": "No calibrated benefit test: keep unenhanced prepared image. Blur, noise and exposure "
                  "are distinct; texture/scale affect diagnostics. Sharpening cannot recover hidden detail.",
        "candidates": {},
    }
    row["experiment"]["enhancements"] = evidence
    for name, candidate in preparation.candidates(image):
        if name == "control":
            continue
        evidence["candidates"][name] = {
            "input": evidence["input"], "status": "comparison-only",
            "meanAbsolutePixelChange": preparation.mean_absolute_pixel_change(image, candidate)}
        yield "enhance-" + name, candidate
    sharpened = image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=75, threshold=3))
    evidence["candidates"]["sharpen"] = {
        "input": evidence["input"], "status": "comparison-only",
        "meanAbsolutePixelChange": preparation.mean_absolute_pixel_change(image, sharpened)}
    yield "enhance-sharpen", sharpened


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
    pills = (clutter.bubbles(array)
             if row.get("eligibility", {}).get("status") == "usable"
             and row.get("geometry", {}).get("overlayDetected") else [])
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
    layout = row["experiment"].get("screenshotLayout")
    if layout:
        parent = row["experiment"]["final"]
        sx, sy, _, _ = row["experiment"]["candidates"][parent]["sourceBox"]
        face_mask = np.zeros(mask.shape, dtype=bool)
        for box in clutter.face_boxes(row["eligibility"]["faces"], (sx, sy), image.size):
            face_mask |= clutter.solid(mask.shape, box)
        for item in layout["overlayParts"]:
            bx0, by0, bx1, by1 = item["box"]
            box = [max(0, bx0 - sx), max(0, by0 - sy),
                   min(image.width, bx1 - sx), min(image.height, by1 - sy)]
            if box[2] <= box[0] or box[3] <= box[1]:
                continue
            piece = clutter.grow(clutter.solid(mask.shape, box), max(4, round(image.width * .006)))
            if (piece & face_mask).any():
                evidence.setdefault("refusedParts", []).append(dict(item, reason="Face overlap outside pill."))
                continue
            mask |= piece
            evidence["parts"].append(dict(item, box=box, sourceBox=item["box"]))
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


def integrated_head_candidates(image, row, original, eraser_mask=None):
    """Keep earlier cleanup and its coordinates when extending the synthetic review branch."""
    evidence = row["experiment"]
    parent = evidence["final"]
    candidates = evidence.setdefault("candidates", {})
    box = candidates.get(parent, {}).get("sourceBox", [0, 0, *original.size])
    evidence["guardedFinal"] = parent
    head_images = {}
    for name, output in head_overlay_candidates(image, row):
        head_images[name] = output
        candidates[name] = {"input": parent, "size": list(output.size), "sourceBox": list(box),
                            "diagnostic": name.endswith("-mask"), "status": "comparison"}
        yield name, output
    head = evidence["headOverlay"]
    head.update(input=parent, sourceBox=list(box), synthetic=True, likenessEligible=False)
    if "head-overlay-reconstruction" not in head_images:
        return
    selected = "head-overlay-reconstruction"
    restored = head_images[selected]
    head.update(selected=True, status="selected-for-review",
                reason="Synthetic review branch, not an accepted library/core image. "
                       "Retains prior guarded cleanup; enhancements consume this branch.")
    candidates[selected]["status"] = "selected"
    candidates[parent]["status"] = "comparison"
    evidence["final"] = selected
    evidence["steps"].append({
        "name": selected, "status": "selected-for-review", "input": parent,
        "candidate": selected, "selected": selected, "reason": head["reason"]})
    cumulative = np.zeros((original.height, original.width), dtype=bool)
    if eraser_mask is not None and "eraser" in candidates:
        ex0, ey0, ex1, ey1 = candidates["eraser"]["sourceBox"]
        cumulative[ey0:ey1, ex0:ex1] |= np.asarray(eraser_mask)[..., 0] > 0
    x0, y0, x1, y1 = box
    cumulative[y0:y1, x0:x1] |= np.asarray(head_images["head-overlay-mask"])[..., 0] > 0
    outside = ~cumulative[y0:y1, x0:x1]
    identical = np.array_equal(np.asarray(restored)[outside],
                               np.asarray(original)[y0:y1, x0:x1][outside])
    if not identical:
        raise ValueError("integrated reconstruction differs outside cumulative source-coordinate masks")
    head.update(cumulativeMaskPixels=int(cumulative.sum()), cumulativeOutsideMaskIdentical=True,
                cumulativeMaskCoordinates="original source")
    candidates["cumulative-erase-mask"] = {
        "input": selected, "size": list(original.size), "sourceBox": [0, 0, *original.size],
        "diagnostic": True, "status": "comparison"}
    yield "cumulative-erase-mask", pipeline.mask_image(cumulative)
    proposal = candidates.get("composition")
    layout = evidence.get("screenshotLayout")
    if layout:
        px0, py0, px1, py1 = layout["pictureBox"]
        frame = [px0 - x0, py0 - y0, px1 - x0, py1 - y0]
        if not (0 <= frame[0] < frame[2] <= restored.width
                and 0 <= frame[1] < frame[3] <= restored.height):
            raise ValueError("screenshot composition outside prepared reconstruction")
        proposed = restored.crop(frame)
        candidates["head-overlay-composition"] = {
            "input": selected, "size": list(proposed.size), "sourceBox": layout["pictureBox"],
            "box": frame, "diagnostic": False, "status": "selected",
            "reason": "Select observed picture boundary after reconstruction; no subject-box framing."}
        candidates[selected]["status"] = "comparison"
        evidence["final"] = "head-overlay-composition"
        evidence["steps"].append({
            "name": "head-overlay-composition", "status": "selected-for-review",
            "input": selected, "candidate": "head-overlay-composition",
            "selected": "head-overlay-composition",
            "reason": candidates["head-overlay-composition"]["reason"]})
        yield "head-overlay-composition", proposed
    elif proposal:
        frame = proposal["box"]
        proposed = restored.crop(frame)
        candidates["head-overlay-composition"] = dict(
            proposal, input=selected, size=list(proposed.size), status="comparison",
            reason="Rejected for automatic selection: incomplete hair/feet coverage proof; keep padding.")
        evidence["steps"].append({
            "name": "head-overlay-composition", "status": "attempted-rejected",
            "input": selected, "candidate": "head-overlay-composition", "selected": selected,
            "reason": candidates["head-overlay-composition"]["reason"]})
        yield "head-overlay-composition", proposed
    else:
        evidence["steps"].append({
            "name": "head-overlay-composition", "status": "skipped", "input": selected,
            "candidate": None, "selected": selected, "reason": "No useful composition crop; retain padding."})


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
    if data.get("reviewLayout") in (2, 3, 4):
        return review_page(data)
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


def review_page(data):
    esc = html.escape
    cards = []
    for row in data["rows"]:
        evidence, images = row["evidence"], row["images"]
        final = evidence["final"]
        candidates = evidence.get("candidates", {})
        lineage = {name: item.get("input") for name, item in candidates.items()}
        lineage.update({name: evidence.get("enhancements", {}).get("input")
                        for name in images if name.startswith("enhance-")})

        def panel(name, label, status):
            image = images[name]
            consumers = [child for child, parent in lineage.items() if parent == name]
            return (f'<figure class="{status}"><figcaption><strong>{esc(label)}</strong><br>'
                    f'{esc(status.upper())} — {esc(name)}: {image["size"]}<br>'
                    f'Input: {esc(str(lineage.get(name, "frozen source")))}<br>'
                    f'Feeds: {esc(", ".join(consumers) or "none")}</figcaption>'
                    f'<a href="{quote(image["path"])}"><img loading="lazy" '
                    f'src="{quote(image["padded"])}" alt="{esc(label)}"></a></figure>')

        summary = (panel("original", "1. Original", "source")
                   + panel("saved-v16-final", "2. Historical v16 baseline", "baseline")
                   + panel(final, "3. Current recommendation FOR REVIEW", "selected"))
        details = []
        for name in images:
            status = ("source" if name == "original" else
                      "baseline" if name == "saved-v16-final" else
                      "selected" if name == final else
                      "diagnostic" if name.endswith("-mask") else
                      "rejected" if "composition" in name and
                      candidates.get(name, {}).get("status") != "selected" else
                      "comparison" if name.startswith("enhance-") else "intermediate")
            details.append(panel(name, name, status))
        synthetic = evidence.get("headOverlay", {}).get("selected", False)
        cards.append(f'<article><h2>{esc(row["source"])}</h2>'
                     f'<p>Recommendation for review: <strong>{esc(final)}</strong>. '
                     + ('SYNTHETIC HEAD RECONSTRUCTION — not original/core likeness evidence. '
                        if synthetic else '')
                     + 'No library changes. Enhancement candidates are not automatically ranked.</p>'
                     f'<div class="panels summary">{summary}</div>'
                     f'<details><summary>All stages, masks, rejected crops and filter comparisons</summary>'
                     f'<div class="panels">{"".join(details)}</div></details>'
                     f'<details><summary>Ordered processing trace and source-coordinate evidence</summary>'
                     f'<pre>{esc(json.dumps(evidence, indent=2))}</pre></details></article>')
    prefix = gallery_chrome.reports_prefix(pathlib.Path(data["out"]),
                                          pathlib.Path(data["working"]) / "_reports")
    responsive = ('h2{overflow-wrap:anywhere}figure{max-width:100%;box-sizing:border-box}'
                  if data.get("reviewLayout") in (3, 4) else '')
    framing_note = ('Observed screenshot picture boundaries can frame the restored result; '
                    'subject-box-only composition crops remain comparison-only to protect hair/feet. '
                    if data.get("reviewLayout") == 4 else
                    'composition crops remain rejected for automatic selection to protect hair/feet. ')
    return ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width"><title>Updated intake review</title>'
            f'<style>{gallery_chrome.CSS}article{{padding:16px;margin:12px;background:white}}'
            '.panels{display:flex;flex-wrap:wrap;gap:12px}figure{margin:0;width:280px;padding:8px;'
            'border:4px solid #68717c}figure.selected{border-color:#14743b}'
            'figure.rejected{border-color:#b12424}figure.diagnostic{border-color:#76509b}'
            'figure.comparison{border-color:#b67600}figure.intermediate{border-style:dashed}'
            'img{max-width:100%}figcaption{overflow-wrap:anywhere}pre{white-space:pre-wrap;'
            'overflow-wrap:anywhere}details{margin-top:16px}' + responsive + '</style><body id="top">'
            + gallery_chrome.masthead(None, prefix, "Updated intake review", links=False)
            + '<div class="site-page"><h1>Updated intake review</h1>'
            f'<p>{len(data["rows"])} frozen sources. First three panels: original, historical baseline, '
            'current recommendation for visual review. Selected does NOT mean accepted. '
            'Small/localized cleanup precedes optional synthetic pill reconstruction; '
            + framing_note + 'Previews fit/pad without cropping; click for native pixels. '
            'Unresolved logo detection, face/Junk gates and quality ranking remain open.</p>'
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
        if data.get("reviewLayout") in (2, 3, 4):
            evidence, images = row["evidence"], row["images"]
            if evidence["final"] not in images:
                raise ValueError("review recommendation has no image")
            head = evidence.get("headOverlay", {})
            if head.get("selected"):
                final = evidence["final"]
                restored = "head-overlay-reconstruction"
                if (final not in (restored, "head-overlay-composition") or not head.get("synthetic")
                        or head.get("likenessEligible") is not False
                        or head.get("input") != evidence["guardedFinal"]):
                    raise ValueError("synthetic review branch selection/lineage differs")
                original = np.asarray(preparation.decode_file(out / images["original"]["path"]))
                painted = np.asarray(preparation.decode_file(out / images[restored]["path"]))
                mask = np.asarray(preparation.decode_file(
                    out / images["cumulative-erase-mask"]["path"]))[..., 0] > 0
                x0, y0, x1, y1 = head["sourceBox"]
                outside = ~mask[y0:y1, x0:x1]
                if (not head.get("cumulativeOutsideMaskIdentical")
                        or int(mask.sum()) != head["cumulativeMaskPixels"]
                        or not np.array_equal(painted[outside], original[y0:y1, x0:x1][outside])):
                    raise ValueError("synthetic branch differs outside cumulative masks")
                if final == "head-overlay-composition":
                    composition = evidence["candidates"][final]
                    if composition["input"] != restored:
                        raise ValueError("composition does not consume reconstruction")
                    framed = preparation.decode_file(out / images[restored]["path"]).crop(composition["box"])
                    actual = preparation.decode_file(out / images[final]["path"])
                    if not np.array_equal(np.asarray(framed), np.asarray(actual)):
                        raise ValueError("composition differs from reconstructed crop")
            enhancements = evidence.get("enhancements", {})
            if "input" in enhancements and enhancements["input"] != evidence["final"]:
                raise ValueError("enhancements do not consume the review recommendation")
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
        if saved.get("enhancementsEnabled", False) != bool(args.enhancements):
            raise ValueError("enhancement mode differs; use matching flags or a new output directory")
        if args.apply and args.enhancements and saved.get("enhancementPolicy") != ENHANCEMENT_POLICY:
            raise ValueError("enhancement policy changed; use a new output directory")
        if args.apply and args.head_overlay and saved.get("headOverlayPolicy") != HEAD_POLICY:
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
                prepared = preparation.decode_file(stage / images[row["experiment"]["final"]]["path"])
                mask = (preparation.decode_file(stage / images["eraser-mask"]["path"])
                        if "eraser-mask" in images else None)
                for name, image in integrated_head_candidates(prepared, row, original, mask):
                    save(name, image)
            if args.enhancements and row.get("eligibility", {}).get("status") == "usable":
                prepared = preparation.decode_file(stage / images[row["experiment"]["final"]]["path"])
                for name, image in enhancement_candidates(prepared, row):
                    save(name, image)
            elif args.enhancements:
                row["experiment"]["enhancements"] = {
                    "status": "skipped", "reason": "Face assessment does not authorize enhancement.",
                    "recommendation": row["experiment"]["final"]}
            rows.append({"source": binding["source"], "binding": binding,
                         "seconds": round(time.perf_counter() - started, 4),
                         "images": images, "evidence": row["experiment"]})
            print(f"Prepared sequence {index}/{len(planned)}: {binding['source']}", flush=True)
        data = {"schemaVersion": 1, "tool": "intake-sequence-benchmark", "recipe": recipe(),
                "root": str(root), "working": str(working), "out": str(out),
                "report": {"path": str(report), "sha256": digest},
                "selectionSha256": benchmark.sha(payload),
                "compositionComparisonOnly": not any(
                    r["evidence"]["final"] == "head-overlay-composition" for r in rows),
                "compositionSelection": "observed screenshot picture boundary only; "
                                        "subject-box proposals remain comparison-only",
                "reviewLayout": 4, "headOverlayEnabled": bool(args.head_overlay),
                "enhancementsEnabled": bool(args.enhancements),
                "enhancementPolicy": ENHANCEMENT_POLICY if args.enhancements else None,
                "headOverlayPolicy": HEAD_POLICY if args.head_overlay else None, "rows": rows}
        put("index.html", page(data))
        data["files"] = files
        preparation.write_new(stage / "manifest.json", (json.dumps(data, indent=2) + "\n").encode("utf-8"))
        verify(stage, working, report, payload, recorded_out=out)
        os.rename(stage, out)
    gallery_chrome.publish_banner(working / "_reports")
    print(f"Published experimental sequence comparison: {out / 'index.html'}")
    return 0
