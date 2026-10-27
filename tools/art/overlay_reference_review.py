#!/usr/bin/env python3
"""Unconfirmed overlay reference candidates (GMW-style badges, search pills) from a preparation report.

Reads one existing, immutable preparation report and an explicit list of its row sources. For each selected row it
decodes the report's exact retained source bytes (hash-verified) and proposes regions with three heuristics:

* ``emblem-corner``: the existing restricted lower-corner badge heuristic (``clutter.emblems``), unchanged;
* ``emblem-any-location``: the same saturated-colour connected components with the location clipping disabled,
  so badges anywhere in the frame are proposed (implemented here; the clutter default is not changed);
* ``search-pill``: the existing wide top-fifth pill heuristic (``clutter.bubbles``).

Every proposal is UNCONFIRMED and must not be used for automatic repainting. Colour is a cue, not identity: a pink or
magenta region is not assumed to be a GMW badge. Nothing is repainted, no source is changed, no model loads and no
matcher is trained. The user reviews the page and confirms or rejects candidates in chat by source and candidate id.
"""
import argparse
import html
import json
import os
import pathlib
import sys
import tempfile
from urllib.parse import quote

import cv2
import numpy as np
import PIL
from jsonschema.exceptions import ValidationError
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import eraser_benchmark as benchmark  # noqa: E402
import image_preparation as preparation  # noqa: E402
from intake_library import clutter  # noqa: E402
from likeness_library import gallery_chrome, sandbox  # noqa: E402

TOOL = "overlay-reference-review"
MAX_PER_ROW = 8
LABEL = "unconfirmed; do not use for automatic repainting"
PREVIEW = 1200
DETECTORS = ("emblem-corner", "emblem-any-location", "search-pill")
RECIPE = {
    "id": "overlay-reference-review-v1",
    "opencv": cv2.__version__, "numpy": np.__version__, "pillow": PIL.__version__,
    "input": "the report's exact retained source bytes, decoded like the preparation (EXIF-oriented sRGB RGB)",
    "coordinates": "boxes are [x0, y0, x1, y1) pixels of the decoded, EXIF-oriented retained source",
    "detectors": {
        "emblem-corner": "clutter.emblems: saturated magenta/pink badges reaching a lower corner (unchanged)",
        "emblem-any-location": "the same HSV threshold, join and size/aspect/fill gates as clutter.emblems with "
                               "the lower-60% and corner-third clipping disabled; mask is the filled component",
        "search-pill": "clutter.bubbles: wide neutral rounded pill in the top fifth (unchanged)",
    },
    "overlapMerge": "an any-location component overlapping a corner emblem by IoU >= 0.5 is recorded on it",
    "maxPerRow": MAX_PER_ROW,
    "label": LABEL,
    "selection": "none: no candidate is confirmed, selected or used; confirmation happens only in chat",
}
NOTES = (
    "Every candidate is UNCONFIRMED; do not use for automatic repainting.",
    "Colour is a cue, not identity: a pink or magenta region is not assumed to be a GMW badge.",
    "Proposals are heuristic; a missing proposal is not proof an image is clean.",
    "No source was processed, repainted or changed; no model loaded; no matcher was trained.",
    "To confirm or reject, tell the assistant in chat the source and candidate id (for example: "
    "'Various/gallery/x.jpg c02 is a GMW badge; c03 is jewellery'). This page writes nothing.",
)


def any_location_emblems(array):
    """clutter.emblems' colour components with location clipping disabled; tight filled masks, not ellipses."""
    height, width = array.shape[:2]
    hsv = cv2.cvtColor(array, cv2.COLOR_RGB2HSV)
    chroma = ((hsv[:, :, 0] >= 150) & (hsv[:, :, 1] > 120) & (hsv[:, :, 2] > 130)).astype(np.uint8)
    join = max(3, round(min(width, height) * .015)) | 1
    chroma = cv2.dilate(chroma, np.ones((join, join), np.uint8))
    count, labels, stats, _ = cv2.connectedComponentsWithStats(chroma)
    parts = []
    for label in range(1, count):
        x, y, w, h, area = map(int, stats[label])
        if (.06 * width <= w <= .35 * width and .025 * height <= h <= .22 * height
                and .45 <= w / h <= 2.2 and area >= w * h * .06):
            parts.append(clutter.part("logo", clutter.fill_holes(labels == label), "saturated component, any location"))
    return parts


def iou(a, b):
    inner = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inner
    return inner / union if union else 0.0


def propose(array):
    """(candidates, dropped): at most MAX_PER_ROW proposals in a fixed order, and how many were truncated."""
    found = [{"detectors": ["emblem-corner"], "mask": p["mask"], "box": p["box"]} for p in clutter.emblems(array)]
    corners = list(found)
    found += [{"detectors": ["search-pill"], "mask": p["mask"], "box": p["box"]} for p in clutter.bubbles(array)]
    extra = []
    for item in any_location_emblems(array):
        match = next((c for c in corners if iou(c["box"], item["box"]) >= .5), None)
        if match is not None:
            if "emblem-any-location" not in match["detectors"]:
                match["detectors"].append("emblem-any-location")
            continue
        extra.append({"detectors": ["emblem-any-location"], "mask": item["mask"], "box": item["box"]})
    found += sorted(extra, key=lambda c: (c["box"][1], c["box"][0]))
    return found[:MAX_PER_ROW], max(0, len(found) - MAX_PER_ROW)


def crop_box(box, size):
    width, height = size
    x0, y0, x1, y1 = box
    pad = max(4, round(.15 * max(x1 - x0, y1 - y0)))
    return [max(0, x0 - pad), max(0, y0 - pad), min(width, x1 + pad), min(height, y1 + pad)]


def plan(report, data, sources, expected=None):
    """One entry per selected source, in order; verifies each retained artifact; later same-hash rows reuse."""
    rows = {row["source"]: row for row in data["photos"]}
    missing = [s for s in sources if s not in rows]
    if missing:
        raise ValueError("selected sources are not rows of the report: " + ", ".join(missing))
    changed = [s for s, digest in (expected or {}).items() if rows[s]["sourceSha256"] != digest]
    if changed:
        raise ValueError("selected source hashes differ from the report rows: " + ", ".join(changed))
    seen, planned = {}, []
    for source in sources:
        row = rows[source]
        benchmark.artifact(report, row["retained"], row["sourceSha256"])
        entry = {"source": source, "sourceSha256": row["sourceSha256"], "retained": row["retained"]}
        if row["sourceSha256"] in seen:
            entry.update(status="duplicate", duplicateOf=seen[row["sourceSha256"]])
        else:
            seen[row["sourceSha256"]] = source
            entry["status"] = "proposed"
        planned.append(entry)
    return planned


def png(image):
    return benchmark.png(image)


def annotated(image, candidates):
    scale = min(1.0, PREVIEW / max(image.size))
    shown = image if scale == 1 else image.resize(
        (max(1, round(image.width * scale)), max(1, round(image.height * scale))), Image.Resampling.LANCZOS)
    shown = shown.copy()
    draw = ImageDraw.Draw(shown)
    for item in candidates:
        x0, y0, x1, y1 = (round(v * scale) for v in item["box"])
        draw.rectangle((x0, y0, max(x0, x1 - 1), max(y0, y1 - 1)), outline=(0, 255, 255), width=2)
        draw.text((x0 + 2, max(0, y0 - 12)), item["id"], fill=(0, 255, 255))
    return shown


def review(report, entry, stage, files):
    """Write one row's source copy, annotated preview and candidate crops/masks; return its manifest record."""
    folder = f"rows/{preparation.sha(entry['source'].encode('utf-8'))[:24]}"

    def put(name, payload):
        relative = f"{folder}/{name}"
        preparation.write_new(stage / relative, payload)
        files[relative] = preparation.sha(payload)
        return relative

    retained = preparation.safe_path(report, report / entry["retained"])
    payload = retained.read_bytes()
    if preparation.sha(payload) != entry["sourceSha256"]:
        raise ValueError(f"retained source changed while reading: {entry['source']}")
    source_copy = put("source" + retained.suffix.lower(), payload)
    image = preparation.decode(payload)
    array = np.asarray(image)
    found, dropped = propose(array)
    candidates = []
    for number, item in enumerate(found, 1):
        cid = f"c{number:02d}"
        box = [int(v) for v in item["box"]]
        crop = crop_box(box, image.size)
        mask = item["mask"][crop[1]:crop[3], crop[0]:crop[2]]
        crop_path = put(f"{cid}-crop.png", png(image.crop(tuple(crop))))
        mask_path = put(f"{cid}-mask.png", png(Image.fromarray((mask.astype(np.uint8) * 255)).convert("RGB")))
        candidates.append({
            "id": cid, "sourceId": entry["source"], "sourceSha256": entry["sourceSha256"],
            "detectors": list(item["detectors"]), "box": box, "cropBox": crop,
            "maskPixels": int(item["mask"].sum()), "maskInCropPixels": int(mask.sum()),
            "crop": {"path": crop_path, "sha256": files[crop_path]},
            "mask": {"path": mask_path, "sha256": files[mask_path]},
            "label": LABEL, "status": "unconfirmed", "confirmed": False})
    preview = put("annotated.png", png(annotated(image, candidates)))
    entry = dict(entry)
    entry.update(size=[image.width, image.height], copy={"path": source_copy, "sha256": files[source_copy]},
                 annotated={"path": preview, "sha256": files[preview]}, candidates=candidates, truncated=dropped)
    if dropped:
        entry["warning"] = (f"{dropped} more proposal(s) were not shown: only the first {MAX_PER_ROW} are kept; "
                            "the image may hold broad colour/pill regions that need a manual look")
    return entry


def page(data):
    esc = html.escape

    def figure(label, path, width=300):
        return (f'<figure style="max-width:{width}px"><figcaption>{esc(label)}</figcaption>'
                f'<a href="{quote(path)}"><img loading="lazy" src="{quote(path)}" alt="{esc(label)}"></a></figure>')

    cards = []
    for entry in data["rows"]:
        head = (f'<article><h2>{esc(entry["source"])}</h2><p>Source ID <code>{esc(entry["source"])}</code>; '
                f'SHA-256 <code>{esc(entry["sourceSha256"])}</code>.</p>')
        if entry["status"] == "duplicate":
            cards.append(head + f'<p><strong>Same bytes as</strong> {esc(entry["duplicateOf"])}: its candidates apply; '
                         'not proposed twice.</p></article>')
            continue
        warning = f'<p class="warn"><strong>Truncated:</strong> {esc(entry["warning"])}</p>' if entry["truncated"] else ""
        if not entry["candidates"]:
            body = "<p>No proposal (heuristics only; not proof the image is clean).</p>"
        else:
            body = ""
            for c in entry["candidates"]:
                body += (
                    f'<section class="cand"><h3>{esc(c["id"])} <span class="tag">{esc(c["label"])}</span></h3>'
                    f'<p>{esc(", ".join(c["detectors"]))}; box <code>{c["box"]}</code>, crop '
                    f'<code>{c["cropBox"]}</code>, mask {c["maskPixels"]} px.</p><div class="panels">'
                    + figure(f'{c["id"]} crop (native pixels)', c["crop"]["path"], 240)
                    + figure(f'{c["id"]} binary mask', c["mask"]["path"], 240)
                    + f'</div><p><code>crop {esc(c["crop"]["sha256"])}</code><br>'
                    f'<code>mask {esc(c["mask"]["sha256"])}</code></p></section>')
        cards.append(
            head + f'<p>{entry["size"][0]}x{entry["size"][1]}; {len(entry["candidates"])} candidate(s).</p>'
            + warning + '<div class="panels">'
            + figure("Source (exact retained bytes)", entry["copy"]["path"])
            + figure("Candidate boxes (display copy)", entry["annotated"]["path"], 420)
            + '</div>' + body + '</article>')
    prefix = gallery_chrome.reports_prefix(pathlib.Path(data["out"]), pathlib.Path(data["working"]) / "_reports")
    total = sum(len(e.get("candidates", ())) for e in data["rows"])
    truncated = sum(e.get("truncated", 0) for e in data["rows"])
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width"><title>Overlay reference candidates</title>'
        f'<style>{gallery_chrome.CSS}article{{background:var(--st-card);border:1px solid var(--st-line);'
        'border-radius:var(--st-radius);box-shadow:var(--st-shadow);padding:16px;margin-bottom:20px}'
        'h2{font-size:18px;overflow-wrap:anywhere}h3{font-size:15px}.panels{display:flex;flex-wrap:wrap;gap:12px}'
        'figure{margin:0}img{max-width:100%;height:auto}figcaption{padding:8px 0}'
        '.cand{border-top:1px solid var(--st-line);padding-top:8px}.tag{font-weight:normal;font-size:.85em}'
        '.warn{border-left:4px solid currentColor;padding-left:8px}code{font-size:.8em;overflow-wrap:anywhere}</style>'
        f'<body id="top">{gallery_chrome.masthead(None, prefix, "Overlay reference candidates", links=False)}'
        '<div class="site-page"><header class="page-header"><div><h1>Overlay reference candidates (unconfirmed)</h1>'
        f'<p>Report: <code>{esc(data["report"]["path"])}</code>; {len(data["rows"])} selected sources, '
        f'{total} candidates' + (f', {truncated} truncated' if truncated else '') + '.</p>'
        + "".join(f"<p>{esc(note)}</p>" for note in NOTES)
        + '</div></header>' + "".join(cards)
        + gallery_chrome.footer("Unconfirmed candidates - no confirmation, repainting or library changes")
        + '</div></body></html>\n').encode("utf-8")


def build(root, working, report, out, data, manifest_sha, sources, sources_payload, planned):
    """Stage the whole run beside its destination, verify it, then rename it into place in one step."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".overlay-review-", dir=out.parent) as temporary:
        stage = pathlib.Path(temporary) / "run"
        stage.mkdir()
        files = {}
        preparation.write_new(stage / "sources.json", sources_payload)
        files["sources.json"] = preparation.sha(sources_payload)
        rows = []
        for index, entry in enumerate(planned, 1):
            rows.append(review(report, entry, stage, files) if entry["status"] == "proposed" else dict(entry))
            print(f"Reviewed {index}/{len(planned)}: {rows[-1]['status']}", flush=True)
        manifest = {
            "schemaVersion": 1, "tool": TOOL, "recipe": RECIPE, "root": str(root), "working": str(working),
            "out": str(out),
            "report": {"path": str(report), "manifestSha256": manifest_sha, "reportSha256": data["reportSha256"],
                       "recipeId": data["recipe"]["id"]},
            "selection": {"file": "sources.json", "sha256": preparation.sha(sources_payload), "sources": sources},
            "notes": list(NOTES), "rows": rows,
        }
        index = page(manifest)
        preparation.write_new(stage / "index.html", index)
        files["index.html"] = preparation.sha(index)
        manifest["files"] = dict(sorted(files.items()))
        preparation.write_new(stage / "manifest.json", (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
        verify(stage, working, report, sources_payload, recorded_out=out)
        os.rename(stage, out)
    return manifest


def binary(path):
    with Image.open(path) as opened:
        array = np.array(opened.convert("RGB"))
    if not np.isin(array, (0, 255)).all() or not (array[..., 0] == array[..., 2]).all():
        raise ValueError(f"candidate mask is not binary 0/255: {path}")
    return array


def verify(out, working, report, sources_payload, *, recorded_out=None):
    """Read-only: selection and report binding, selected retained sources, every output hash, candidate labels."""
    manifest = preparation.safe_path(working, out / "manifest.json")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("tool") != TOOL or data.get("schemaVersion") != 1:
        raise ValueError("not an overlay reference review run")
    root, _, report_data, manifest_sha, report_working = benchmark.open_report(report)
    if (data["root"] != str(root) or data["working"] != str(working) or report_working != working
            or data["out"] != str(recorded_out or out)):
        raise ValueError("overlay review run root/location differs")
    if (data["report"]["path"] != str(report) or data["report"]["manifestSha256"] != manifest_sha
            or data["report"]["reportSha256"] != report_data["reportSha256"]):
        raise ValueError("preparation report differs from the one this run was built from")
    if data["selection"]["sha256"] != preparation.sha(sources_payload):
        raise ValueError("--sources differs from the selection recorded in this run")
    sources, expected = benchmark.parse_sources(sources_payload)
    if data["selection"]["sources"] != sources or [r["source"] for r in data["rows"]] != sources:
        raise ValueError("recorded selection disagrees with its rows")
    planned = plan(report, report_data, sources, expected)
    files = data["files"]
    present = set()
    for path in out.rglob("*"):
        if sandbox._is_reparse_point(path):
            raise ValueError(f"refusing linked path in run: {path}")
        if path.is_file():
            present.add(path.relative_to(out).as_posix())
    present.discard("manifest.json")
    if present != set(files):
        raise ValueError("overlay review run has missing or extra files: "
                         + ", ".join(sorted(present.symmetric_difference(files))))
    for relative, digest in files.items():
        sandbox._safe_source_path(relative)
        if preparation.sha_file(preparation.safe_path(out, out / relative)) != digest:
            raise ValueError(f"overlay review artifact hash mismatch: {out / relative}")
    if files["sources.json"] != data["selection"]["sha256"] or files["index.html"] != preparation.sha(page(data)):
        raise ValueError("overlay review page or selection copy does not match its manifest")
    for wanted, entry in zip(planned, data["rows"]):
        if any(wanted[key] != entry.get(key) for key in wanted):
            raise ValueError(f"row disagrees with the report: {entry['source']}")
        if entry["status"] != "proposed":
            continue
        if entry["copy"]["sha256"] != entry["sourceSha256"] or len(entry["candidates"]) > MAX_PER_ROW:
            raise ValueError(f"row source copy or candidate count is wrong: {entry['source']}")
        recorded = [entry["copy"], entry["annotated"]]
        for c in entry["candidates"]:
            if (c.get("status") != "unconfirmed" or c.get("confirmed") is not False or c.get("label") != LABEL
                    or c.get("sourceId") != entry["source"] or c.get("sourceSha256") != entry["sourceSha256"]
                    or not set(c.get("detectors", ())) <= set(DETECTORS)):
                raise ValueError(f"candidate {c.get('id')} is not an unconfirmed proposal: {entry['source']}")
            recorded += [c["crop"], c["mask"]]
            x0, y0, x1, y1 = c["cropBox"]
            mask = binary(out / c["mask"]["path"])
            with Image.open(out / c["crop"]["path"]) as crop:
                size = crop.size
            if size != (x1 - x0, y1 - y0) or mask.shape[:2] != (y1 - y0, x1 - x0):
                raise ValueError(f"candidate {c['id']} crop/mask size disagrees with its box: {entry['source']}")
        if any(files.get(item["path"]) != item["sha256"] for item in recorded):
            raise ValueError(f"row hashes disagree with the recorded files: {entry['source']}")
    return data


def run(args):
    root, report, data, manifest_sha, working = benchmark.open_report(args.report)
    out = benchmark.run_location(working, report, args.out)
    sources, payload = benchmark.read_sources(args.sources)
    if args.check:
        result = verify(out, working, report, payload)
        total = sum(len(r.get("candidates", ())) for r in result["rows"])
        print(f"Verified overlay reference review: {len(result['rows'])} sources, {total} unconfirmed candidates; "
              "selection, report binding, retained sources and all outputs match.")
        return 0
    planned = plan(report, data, sources, benchmark.parse_sources(payload)[1])
    print(f"Report {report} ({data['recipe']['id']}); root {root}; {len(sources)} selected sources.")
    print("Unconfirmed overlay reference candidates only: no repainting, model load, training or source change.")
    for entry in planned:
        if entry["status"] == "duplicate":
            print(f"  same    {entry['source']}: bytes of {entry['duplicateOf']}; reused, not proposed twice")
        else:
            print(f"  propose {entry['source']}: {entry['sourceSha256'][:12]}")
    if out.exists():
        if not args.apply:
            print(f"Run already exists: {out} (use --check to verify)")
            return 0
        result = verify(out, working, report, payload)
        if result["recipe"] != RECIPE:
            raise ValueError("existing run used a different recipe/versions; choose a new --out")
        print(f"Existing run verified without rewriting: {out / 'index.html'}")
        return 0
    if not args.apply:
        print(f"Preview only; nothing written. Add --apply to publish {out}")
        return 0
    manifest = build(root, working, report, out, data, manifest_sha, sources, payload, planned)
    for entry in manifest["rows"]:
        if entry.get("truncated"):
            print(f"WARNING: {entry['source']}: {entry['warning']}")
    gallery_chrome.publish_banner(working / "_reports")
    print(f"Published unconfirmed overlay reference candidates: {out / 'index.html'}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", required=True, help="absolute existing Working\\_reports\\preparation\\RUN")
    parser.add_argument("--sources", required=True, help=f"JSON array of 1..{benchmark.MAX_SOURCES} exact report "
                        "row sources (strings, or objects with source/sourceSha256)")
    parser.add_argument("--out", required=True, help=f"absolute new Working\\_reports\\{benchmark.OUTPUT_DIR}\\RUN")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="preview (default); writes nothing")
    mode.add_argument("--apply", action="store_true", help="publish a new immutable run; repeating verifies")
    mode.add_argument("--check", action="store_true", help="verify an existing run; read only")
    args = parser.parse_args(argv)
    try:
        return run(args)
    except (OSError, ValueError, KeyError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
