#!/usr/bin/env python3
"""Same-mask eraser A/B: the saved LaMa eraser versus OpenCV Telea and Navier-Stokes inpainting.

Reads one existing, immutable preparation report and an explicit list of its row sources. Each eligible row
reuses the report's own pre-eraser input (the eraser step's traced input, not the final selection) and its saved
binary eraser mask, so every method fills the identical pixels of the identical image. Outside the mask the
OpenCV outputs are byte-identical copies of the input. This is a post-crop reconstruction comparison only:
not an erase-first sequence, not a quality score, not a selection and never an identity assignment.
"""
import argparse
import html
import io
import json
import os
import pathlib
import sys
import tempfile
import time
from urllib.parse import quote

import cv2
import numpy as np
import PIL
from jsonschema.exceptions import ValidationError
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import image_preparation as preparation  # noqa: E402
import originals  # noqa: E402
from likeness_library import gallery_chrome, sandbox  # noqa: E402

MAX_SOURCES = 64
RADIUS = 3
OUTPUT_DIR = "eraser-compare"
METHODS = (("telea", "INPAINT_TELEA", cv2.INPAINT_TELEA), ("ns", "INPAINT_NS", cv2.INPAINT_NS))
PADDED = (944, 1104)
RECIPE = {
    "id": "eraser-ab-v1",
    "opencv": cv2.__version__, "numpy": np.__version__, "pillow": PIL.__version__,
    "baseline": "saved LaMa eraser from the preparation report; no model is loaded or rerun",
    "methods": [{"name": name, "method": f"cv2.inpaint {flag}", "radius": RADIUS} for name, flag, _ in METHODS],
    "input": "the eraser step's traced input variant (pre-eraser image), never the final selection",
    "mask": "the saved eraser-mask exactly (binary 0/255 RGB, undilated); the same mask for every method",
    "outside": "outside-mask RGB copied byte-identically from the pre-eraser input and verified",
    "padding": {"size": list(PADDED), "color": list(originals.STUDIO_GREY), "crop": False},
    "selection": "none: comparison only; no candidate is selected, recommended or assigned",
}
NOTES = (
    "Comparison only: no candidate is selected, recommended, published to Gallery/Review or assigned to anyone.",
    "Pixel change is not quality; inside-mask change only says how different a fill is from the clutter it covers.",
    "Every fill is synthetic reconstruction, not recovery of what the clutter hid.",
    "This is a post-crop reconstruction A/B on the report's pre-eraser input; it is NOT an erase-first sequence.",
    "LaMa ran at patch scale (at most 768px) with a 3px-dilated model mask but pasted only inside the saved mask.",
)


def sha(payload):
    return preparation.sha(payload)


def absolute(value, flag):
    path = pathlib.Path(value).expanduser()
    if not path.is_absolute():
        raise ValueError(f"{flag} must be an absolute path")
    return path


def unlinked(path):
    for part in (path, *path.parents):
        if sandbox._is_reparse_point(part):
            raise ValueError(f"refusing linked path: {part}")
    return path


def open_report(report):
    """The frozen report, its root (from the manifest) and the hashes binding it; no full artifact scan."""
    report = absolute(report, "--report")
    manifest = unlinked(report / "manifest.json")
    if not manifest.is_file():
        raise ValueError(f"no preparation manifest: {manifest}")
    payload = manifest.read_bytes()
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("root"), str):
        raise ValueError("preparation manifest has no frozen root")
    preparation.validate(data)
    root, report, working = report_root(pathlib.Path(data["root"]), report, data, sha(payload))
    page_path = preparation.safe_path(report, report / "index.html")
    if preparation.sha_file(page_path) != data["reportSha256"]:
        raise ValueError("preparation report HTML hash mismatch")
    return root, report, data, sha(payload), working


def report_root(root, report, data, manifest_sha):
    """(root, report, Working): a direct sandbox Working run, or a receipt-bound clean-rebase intake mirror.

    The mirror is only ``Working\\_sandbox-state\\RUN\\inputs`` with its ``_reports\\preparation\\all`` report,
    whose manifest hash, recipe and complete source inventory are bound by that run's ``intake.json``.
    """
    if not root.is_absolute():
        raise ValueError("preparation manifest root must be absolute")
    if sandbox.is_sandbox_working_path(root):
        root, report = preparation.locations(root, report)
        return root, report, root
    working, run = root.parent.parent.parent, root.parent
    if (root.name != "inputs" or run.parent.name != "_sandbox-state" or run.name.startswith((".", "_"))
            or not sandbox.is_sandbox_working_path(working)):
        raise ValueError("report root must be sandbox Working or Working\\_sandbox-state\\RUN\\inputs")
    if not working.is_dir():
        raise ValueError(f"sandbox Working does not exist: {working}")
    unlinked(working)
    preparation.safe_path(working, root)
    if not root.is_dir() or report != root / "_reports" / "preparation" / "all":
        raise ValueError("nested report must be the intake run's inputs\\_reports\\preparation\\all")
    preparation.safe_path(root, report)
    receipt = preparation.safe_path(working, run / "intake.json")
    if not receipt.is_file():
        raise ValueError(f"nested inputs root has no intake receipt: {receipt}")
    value = json.loads(receipt.read_text(encoding="utf-8"))
    if (not isinstance(value, dict) or value.get("schemaVersion") != 1
            or value.get("preparationManifestSHA256") != manifest_sha or value.get("recipe") != data["recipe"]):
        raise ValueError("intake receipt does not bind this preparation report")
    if value.get("inputs") != {row["source"]: row["sourceSha256"] for row in data["photos"]}:
        raise ValueError("intake receipt inventory disagrees with the report rows")
    return root, report, working


def run_location(working, report, out):
    out = absolute(out, "--out")
    if out.parent != working / "_reports" / OUTPUT_DIR or out.name.startswith((".", "_")):
        raise ValueError(f"--out must be a new named run directly in Working\\_reports\\{OUTPUT_DIR}")
    preparation.safe_path(working, out)
    sandbox.require_sandbox_output(working, out)
    if sandbox._overlaps(out.resolve(strict=False), report.resolve()):
        raise ValueError("--out must not overlap the preparation report")
    return out


def read_sources(path):
    path = unlinked(absolute(path, "--sources"))
    payload = path.read_bytes()
    return parse_sources(payload)[0], payload


def parse_sources(payload):
    """(sources, expected hashes): an array of source strings, or of objects with "source" and optional
    "sourceSha256" (other keys are kept in the copied list but ignored)."""
    items = json.loads(payload.decode("utf-8"))
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_SOURCES:
        raise ValueError(f"--sources must be a JSON array of 1..{MAX_SOURCES} report sources")
    if all(isinstance(item, str) for item in items):
        sources, expected = list(items), {}
    elif all(isinstance(item, dict) and isinstance(item.get("source"), str) for item in items):
        sources = [item["source"] for item in items]
        expected = {item["source"]: item["sourceSha256"] for item in items if "sourceSha256" in item}
    else:
        raise ValueError('--sources items must all be source strings or all objects with a "source" string')
    if len(set(sources)) != len(sources):
        raise ValueError("--sources lists a source twice")
    for source in sources:
        sandbox._safe_source_path(source)
    return sources, expected


def artifact(report, relative, digest):
    sandbox._safe_source_path(relative)
    path = preparation.safe_path(report, report / relative)
    if preparation.sha_file(path) != digest:
        raise ValueError(f"preparation artifact hash mismatch: {path}")
    return path


def plan(report, data, sources, expected=None):
    """One entry per selected source, in list order: eligible with verified inputs, or an explicit skip."""
    rows = {row["source"]: row for row in data["photos"]}
    missing = [s for s in sources if s not in rows]
    if missing:
        raise ValueError("selected sources are not rows of the report: " + ", ".join(missing))
    changed = [s for s, digest in (expected or {}).items() if rows[s]["sourceSha256"] != digest]
    if changed:
        raise ValueError("selected source hashes differ from the report rows: " + ", ".join(changed))
    planned = []
    for source in sources:
        row = rows[source]
        entry = {"source": source, "sourceSha256": row["sourceSha256"], "outcome": row["outcome"]}
        step = next((s for s in (row.get("processing") or {}).get("steps", []) if s["name"] == "eraser"), None)
        variants = row["variants"]
        if step is None:
            reason = f"no eraser step in this row (outcome {row['outcome']})"
        elif step["candidate"] != "eraser" or "eraser" not in variants:
            reason = f"eraser step {step['status']}, no saved LaMa output: {step['reason']}"
        elif "eraser-mask" not in variants:
            reason = "no saved eraser mask"
        else:
            reason = None
        if reason:
            planned.append({**entry, "status": "skipped", "reason": reason})
            continue
        artifact(report, row["retained"], row["sourceSha256"])
        inputs = {"retained": {"path": row["retained"], "sha256": row["sourceSha256"]}}
        for role, name in (("input", step["input"]), ("mask", "eraser-mask"), ("baseline", "eraser")):
            if name not in variants:
                raise ValueError(f"eraser input variant {name!r} missing: {source}")
            variant = variants[name]
            artifact(report, variant["path"], variant["sha256"])
            inputs[role] = {"variant": name, "path": variant["path"], "sha256": variant["sha256"],
                            "size": variant["size"]}
        planned.append({**entry, "status": "compared", "eraserStep": {
            "status": step["status"], "input": step["input"], "reason": step["reason"]},
            "final": row["processing"]["final"], "inputs": inputs})
    return planned


def load_rgb(path):
    with Image.open(path) as opened:
        if opened.mode != "RGB":
            raise ValueError(f"expected an RGB image: {path}")
        return np.array(opened)


def binary_mask(array, path):
    if array.ndim != 3 or not (np.array_equal(array[..., 0], array[..., 1])
                               and np.array_equal(array[..., 0], array[..., 2])):
        raise ValueError(f"eraser mask is not grey: {path}")
    if not np.isin(array[..., 0], (0, 255)).all():
        raise ValueError(f"eraser mask is not binary 0/255: {path}")
    mask = array[..., 0] == 255
    if not mask.any():
        raise ValueError(f"eraser mask is empty: {path}")
    return mask


def same_size(entry, arrays):
    shapes = {name: array.shape[:2] for name, array in arrays.items()}
    if len(set(shapes.values())) != 1:
        raise ValueError(f"input/mask/baseline sizes differ for {entry['source']}: {shapes}")
    height, width = next(iter(shapes.values()))
    if any(entry["inputs"][role]["size"] != [width, height] for role in ("input", "mask", "baseline")):
        raise ValueError(f"recorded sizes disagree with the images for {entry['source']}")


def outside_identical(candidate, original, mask):
    return bool(np.array_equal(candidate[~mask], original[~mask]))


def mean_change(candidate, original, mask):
    delta = np.abs(candidate[mask].astype(np.int16) - original[mask].astype(np.int16))
    return round(float(delta.mean()), 4)


def padded(image):
    fitted = ImageOps.contain(image, PADDED, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", PADDED, originals.STUDIO_GREY)
    canvas.paste(fitted, ((PADDED[0] - fitted.width) // 2, (PADDED[1] - fitted.height) // 2))
    return canvas


def png(image):
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue()


def compare(report, entry, stage, files):
    """Write the panels of one row into the stage; return its manifest record."""
    folder = f"rows/{sha(entry['source'].encode('utf-8'))[:24]}"
    paths = {role: report / entry["inputs"][role]["path"] for role in ("input", "mask", "baseline")}
    arrays = {role: load_rgb(path) for role, path in paths.items()}
    same_size(entry, arrays)
    mask = binary_mask(arrays["mask"], paths["mask"])
    original = arrays["input"]

    def put(name, payload):
        relative = f"{folder}/{name}"
        preparation.write_new(stage / relative, payload)
        files[relative] = sha(payload)
        return relative

    retained = report / entry["inputs"]["retained"]["path"]
    copies = {"source": put("source" + retained.suffix.lower(), retained.read_bytes())}
    for role in ("input", "mask", "baseline"):
        copies[role] = put(f"{role}.png", paths[role].read_bytes())
    for role in copies:
        if files[copies[role]] != entry["inputs"]["retained" if role == "source" else role]["sha256"]:
            raise ValueError(f"copied {role} differs from the report artifact: {entry['source']}")
    displays = {role: put(f"{role}-944x1104.png", png(padded(Image.fromarray(arrays[role]))))
                for role in ("input", "mask", "baseline")}
    baseline = arrays["baseline"]
    entry["baseline"] = {"outsideMaskIdentical": outside_identical(baseline, original, mask),
                         "insideMaskMeanAbsChange": mean_change(baseline, original, mask)}
    mask_u8 = mask.astype(np.uint8) * 255
    outputs = {}
    for name, flag_name, flag in METHODS:
        started = time.perf_counter()
        filled = cv2.inpaint(original, mask_u8, RADIUS, flag)
        result = original.copy()
        result[mask] = filled[mask]
        seconds = round(time.perf_counter() - started, 4)
        if not outside_identical(result, original, mask):
            raise ValueError(f"{name} changed pixels outside the mask: {entry['source']}")
        image = Image.fromarray(result)
        path = put(f"{name}.png", png(image))
        if not outside_identical(load_rgb(stage / path), original, mask):
            raise ValueError(f"saved {name} changed pixels outside the mask: {entry['source']}")
        display = put(f"{name}-944x1104.png", png(padded(image)))
        outputs[name] = {"method": f"cv2.inpaint {flag_name}", "radius": RADIUS, "opencv": cv2.__version__,
                         "path": path, "sha256": files[path], "padded": display, "paddedSha256": files[display],
                         "size": [image.width, image.height], "seconds": seconds, "outsideMaskIdentical": True,
                         "insideMaskMeanAbsChange": mean_change(result, original, mask),
                         "role": "comparison-only, not selected"}
    entry["mask"] = {"pixels": int(mask.sum()), "coverage": round(float(mask.mean()), 6)}
    entry["copies"] = {role: {"path": copies[role], "sha256": files[copies[role]]} for role in copies}
    entry["displays"] = {role: {"path": displays[role], "sha256": files[displays[role]]} for role in displays}
    entry["outputs"] = outputs
    return entry


def page(data):
    esc = html.escape

    def figure(label, path):
        return (f'<figure><figcaption>{esc(label)}</figcaption><a href="{quote(path)}">'
                f'<img loading="lazy" src="{quote(path)}" alt="{esc(label)}"></a></figure>')

    cards = []
    for entry in data["rows"]:
        if entry["status"] != "compared":
            cards.append(f'<article><h2>{esc(entry["source"])}</h2><p><strong>Skipped</strong> '
                         f'(not compared; not a clean result): {esc(entry["reason"])}</p></article>')
            continue
        inputs, outputs = entry["inputs"], entry["outputs"]
        native = (figure("Source (exact retained bytes)", entry["copies"]["source"]["path"])
                  + figure(f"Pre-eraser input: {inputs['input']['variant']}", entry["copies"]["input"]["path"])
                  + figure("Saved binary eraser mask", entry["copies"]["mask"]["path"])
                  + figure("LaMa baseline (saved eraser)", entry["copies"]["baseline"]["path"])
                  + "".join(figure(f"{o['method']} r{o['radius']} (comparison only)", o["path"])
                            for o in outputs.values()))
        padded_panels = ("".join(figure(f"{role} padded 944x1104", entry["displays"][role]["path"])
                                 for role in ("input", "mask", "baseline"))
                         + "".join(figure(f"{name} padded 944x1104", o["padded"]) for name, o in outputs.items()))
        rows = [f'<tr><td>LaMa baseline (saved)</td><td>-</td><td>report</td>'
                f'<td>{entry["baseline"]["outsideMaskIdentical"]}</td>'
                f'<td>{entry["baseline"]["insideMaskMeanAbsChange"]:.2f}/255</td>'
                f'<td><code>{esc(inputs["baseline"]["sha256"])}</code></td></tr>']
        rows += [f'<tr><td>{esc(o["method"])} r{o["radius"]}</td><td>{o["seconds"]:.3f}s</td>'
                 f'<td>OpenCV {esc(o["opencv"])}</td><td>{o["outsideMaskIdentical"]}</td>'
                 f'<td>{o["insideMaskMeanAbsChange"]:.2f}/255</td><td><code>{esc(o["sha256"])}</code></td></tr>'
                 for o in outputs.values()]
        cards.append(
            f'<article><h2>{esc(entry["source"])}</h2>'
            f'<p>Eraser step {esc(entry["eraserStep"]["status"])} on input <strong>'
            f'{esc(inputs["input"]["variant"])}</strong> (report final: {esc(entry["final"])}). '
            f'Mask {entry["mask"]["pixels"]} px ({entry["mask"]["coverage"]:.2%}). Input '
            f'<code>{esc(inputs["input"]["sha256"])}</code>; mask <code>{esc(inputs["mask"]["sha256"])}</code>.</p>'
            f'<div class="panels">{native}</div><h3>Padded 944x1104 (display, no crop)</h3>'
            f'<div class="panels">{padded_panels}</div>'
            '<div class="trace"><table><thead><tr><th>Fill</th><th>Runtime</th><th>Version</th>'
            '<th>Outside mask identical</th><th>Inside-mask change (not quality)</th><th>SHA-256</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div></article>')
    prefix = gallery_chrome.reports_prefix(pathlib.Path(data["out"]), pathlib.Path(data["working"]) / "_reports")
    compared = sum(entry["status"] == "compared" for entry in data["rows"])
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width"><title>Eraser A/B comparison</title>'
        f'<style>{gallery_chrome.CSS}article{{background:var(--st-card);border:1px solid var(--st-line);'
        'border-radius:var(--st-radius);box-shadow:var(--st-shadow);padding:16px;margin-bottom:20px}'
        'h2{font-size:18px;overflow-wrap:anywhere}.panels{display:flex;flex-wrap:wrap;gap:12px}'
        'figure{margin:0;max-width:300px}img{max-width:100%;height:auto}figcaption{padding:8px 0}'
        '.trace{overflow-x:auto}table{border-collapse:collapse;width:100%}td,th{border:1px solid var(--st-line);'
        'padding:4px 6px;text-align:left}code{font-size:.8em;overflow-wrap:anywhere}</style>'
        f'<body id="top">{gallery_chrome.masthead(None, prefix, "Eraser A/B comparison", links=False)}'
        '<div class="site-page"><header class="page-header"><div><h1>Same-mask eraser A/B</h1>'
        f'<p>Report: <code>{esc(data["report"]["path"])}</code>; {compared} compared, '
        f'{len(data["rows"]) - compared} skipped of {len(data["rows"])} selected.</p>'
        + "".join(f"<p>{esc(note)}</p>" for note in NOTES)
        + '</div></header>' + "".join(cards)
        + gallery_chrome.footer("Comparison only - no selection, assignment or library changes")
        + '</div></body></html>\n').encode("utf-8")


def build(root, working, report, out, data, manifest_sha, sources, sources_payload, planned):
    """Stage the whole run beside its destination, verify it, then rename it into place in one step."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".eraser-compare-", dir=out.parent) as temporary:
        stage = pathlib.Path(temporary) / "run"
        stage.mkdir()
        files = {}
        preparation.write_new(stage / "sources.json", sources_payload)
        files["sources.json"] = sha(sources_payload)
        rows = []
        for index, entry in enumerate(planned, 1):
            rows.append(compare(report, dict(entry), stage, files) if entry["status"] == "compared" else entry)
            print(f"Compared {index}/{len(planned)}: {rows[-1]['status']}", flush=True)
        manifest = {
            "schemaVersion": 1, "tool": "eraser-benchmark", "recipe": RECIPE, "root": str(root), "working": str(working),
            "out": str(out),
            "report": {"path": str(report), "manifestSha256": manifest_sha, "reportSha256": data["reportSha256"],
                       "recipeId": data["recipe"]["id"]},
            "selection": {"file": "sources.json", "sha256": sha(sources_payload), "sources": sources},
            "notes": list(NOTES), "rows": rows,
        }
        index = page(manifest)
        preparation.write_new(stage / "index.html", index)
        files["index.html"] = sha(index)
        manifest["files"] = dict(sorted(files.items()))
        preparation.write_new(stage / "manifest.json", (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
        verify(stage, working, report, sources_payload, recorded_out=out)
        os.rename(stage, out)
    return manifest


def verify(out, working, report, sources_payload, *, recorded_out=None):
    """Read-only: selection binding, report binding, selected report artifacts, every output hash, outside-mask."""
    manifest = preparation.safe_path(working, out / "manifest.json")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("tool") != "eraser-benchmark" or data.get("schemaVersion") != 1:
        raise ValueError("not an eraser A/B run")
    root, _, report_data, manifest_sha, report_working = open_report(report)
    if (data["root"] != str(root) or data["working"] != str(working) or report_working != working
            or data["out"] != str(recorded_out or out)):
        raise ValueError("eraser A/B run root/location differs")
    if (data["report"]["path"] != str(report) or data["report"]["manifestSha256"] != manifest_sha
            or data["report"]["reportSha256"] != report_data["reportSha256"]):
        raise ValueError("preparation report differs from the one this run was built from")
    if data["selection"]["sha256"] != sha(sources_payload):
        raise ValueError("--sources differs from the selection recorded in this run")
    sources, expected = parse_sources(sources_payload)
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
        raise ValueError("eraser A/B run has missing or extra files: "
                         + ", ".join(sorted(present.symmetric_difference(files))))
    for relative, digest in files.items():
        sandbox._safe_source_path(relative)
        if preparation.sha_file(preparation.safe_path(out, out / relative)) != digest:
            raise ValueError(f"eraser A/B artifact hash mismatch: {out / relative}")
    if files["sources.json"] != data["selection"]["sha256"] or files["index.html"] != sha(page(data)):
        raise ValueError("eraser A/B page or selection copy does not match its manifest")
    for expected, entry in zip(planned, data["rows"]):
        if expected["status"] != entry["status"] or expected.get("inputs") != entry.get("inputs"):
            raise ValueError(f"row disagrees with the report: {entry['source']}")
        if entry["status"] != "compared":
            continue
        recorded = [entry["copies"][role] for role in entry["copies"]]
        recorded += [entry["displays"][role] for role in entry["displays"]]
        for o in entry["outputs"].values():
            recorded += [{"path": o["path"], "sha256": o["sha256"]}, {"path": o["padded"], "sha256": o["paddedSha256"]}]
        if any(files.get(item["path"]) != item["sha256"] for item in recorded):
            raise ValueError(f"row hashes disagree with the recorded files: {entry['source']}")
        original = load_rgb(out / entry["copies"]["input"]["path"])
        mask = binary_mask(load_rgb(out / entry["copies"]["mask"]["path"]), entry["copies"]["mask"]["path"])
        for name, o in entry["outputs"].items():
            if not outside_identical(load_rgb(out / o["path"]), original, mask):
                raise ValueError(f"{name} differs outside the mask: {entry['source']}")
    return data


def run(args):
    root, report, data, manifest_sha, working = open_report(args.report)
    out = run_location(working, report, args.out)
    sources, payload = read_sources(args.sources)
    if args.check:
        result = verify(out, working, report, payload)
        compared = sum(r["status"] == "compared" for r in result["rows"])
        print(f"Verified eraser A/B run: {compared} compared, {len(result['rows']) - compared} skipped; "
              "selection, report binding, selected inputs and all outputs match.")
        return 0
    planned = plan(report, data, sources, parse_sources(payload)[1])
    print(f"Report {report} ({data['recipe']['id']}); root {root}; {len(sources)} selected sources.")
    print("Comparison only: saved LaMa vs OpenCV Telea/NS r3 on the identical pre-eraser input and mask. "
          "No selection, assignment, model load or source change.")
    for entry in planned:
        if entry["status"] == "compared":
            print(f"  compare {entry['source']}: input {entry['inputs']['input']['variant']} "
                  f"{entry['inputs']['input']['sha256'][:12]}, mask {entry['inputs']['mask']['sha256'][:12]}")
        else:
            print(f"  skip    {entry['source']}: {entry['reason']}")
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
    build(root, working, report, out, data, manifest_sha, sources, payload, planned)
    gallery_chrome.publish_banner(working / "_reports")
    print(f"Published eraser A/B comparison: {out / 'index.html'}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--report", required=True, help="absolute existing Working\\_reports\\preparation\\RUN")
    parser.add_argument("--sources", required=True, help=f"JSON array of 1..{MAX_SOURCES} exact report row sources (strings, or objects with source/sourceSha256)")
    parser.add_argument("--out", required=True, help=f"absolute new Working\\_reports\\{OUTPUT_DIR}\\RUN")
    parser.add_argument("--sequence", action="store_true",
                        help="experimental erase-first sequence versus saved v16; apply uses pinned CPU models")
    parser.add_argument("--head-overlay", action="store_true",
                        help="with --sequence: supplemental synthetic full-pill reconstruction, never selected")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="preview (default); writes nothing")
    mode.add_argument("--apply", action="store_true", help="publish a new immutable run; repeating verifies")
    mode.add_argument("--check", action="store_true", help="verify an existing run; read only")
    args = parser.parse_args(argv)
    if args.head_overlay and not args.sequence:
        parser.error("--head-overlay requires --sequence")
    try:
        if args.sequence:
            import intake_sequence_benchmark
            return intake_sequence_benchmark.run(args)
        return run(args)
    except (OSError, ValueError, KeyError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
