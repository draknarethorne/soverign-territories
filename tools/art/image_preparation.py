#!/usr/bin/env python3
"""Sandbox sidecar comparisons and explicit recoverable Junk routing; no identity assignment."""
import argparse
import collections
import hashlib
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
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError
from PIL import Image, ImageCms, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
import gallery_maintenance as upkeep  # noqa: E402
import originals  # noqa: E402
import preparation_geometry  # noqa: E402
import preparation_junk  # noqa: E402
import screens  # noqa: E402
from intake_library import legacy, models, pipeline  # noqa: E402
from likeness_library import gallery_chrome, metadata, sandbox  # noqa: E402

CATEGORIES = ("Angels", "Sisters", "Models", "Prospects", "Potentials", "Artists", "Various")
SCHEMA = ROOT / "data/art/_schema/image-preparation-pilot.schema.json"
STEPS = pipeline.STEPS
CURRENT = "preparation-comparison-v16"


def step_names(recipe_id):
    """The current order; published v6-v15 reports keep the order they were traced with."""
    return list(STEPS) if recipe_id == CURRENT else legacy.step_names(recipe_id)


RECIPE = {
    "id": CURRENT,
    "pillow": PIL.__version__, "opencv": cv2.__version__, "numpy": np.__version__,
    "control": "EXIF-oriented RGB; embedded ICC converted to sRGB",
    "encoding": "sRGB pixel bytes without copied EXIF/ICC metadata",
    "denoise": {"method": "bilateral", "diameter": 5, "sigmaColor": 15, "sigmaSpace": 3},
    "tone": {"method": "LAB-L CLAHE blend", "clipLimit": 1.5, "grid": [8, 8], "blend": 0.35},
    "maxPixels": 20000000,
    "crop": "solid borders plus guarded black reel panels; legacy fixed UI crop is comparison-only",
    "geometry": {"method": "full-span-solid-border-v1", "maxRange": 10,
                 "blackMax": 20, "whiteMin": 235, "minStrip": 5,
                 "maxFraction": 0.2, "boundaryGuard": 2},
    "reconstruction": "LaMa (big-lama TorchScript) patch fill of the clutter left after the second crop; selected",
    "matching": False,
    "trialPolicy": {
        "faceModelSha256": preparation_geometry.model_evidence(),
        "models": models.describe(),
        "faceDetection": "local YuNet .7/.5, shared human_rows, max1600; no recognition/cache",
        "eligibility": "no detected human face or largest minimum face dimension<60: report-only Junk candidate; "
                       "missing/failed detector: assessment error; no transforms for either",
        "panelDetection": "reel-only; dark<=35; top .08-.22, 20 rows>=.98, 10 picture rows<.75; "
                          "bottom .65-.93, 24 rows>=.88, sustained tail>=.7; face guards .45/1.5h",
        "subject": "Mask R-CNN v2 (COCO person, score>=.5, 800px): largest person plus companions>=20% of its "
                   "area; small figures (ad thumbnails) ignored; no person: body frame around the faces",
        "clutter": "pure-white glyphs (>=50% of strokes>=245) with dark edges in the outer 20%/bottom 30%, "
                   "rendered text kept even over the body; magenta corner badges (hue>=150) reaching an outer "
                   "third; screenshots also: top-fifth search bubbles and lower ui-cards (contours or paired "
                   "long edges); a part touching a face box is clipped there, one covering it is refused",
        "secondCrop": "before any fill; sides top/bottom/left/right, bands 25/40/30/30%; largest edge-inward run "
                      "of parts whose removal loses <=0.5% of the person mask (grown 1%), guard 1.5% "
                      "(screenshots) or 0.8%; keeps >=50% area, aspect .4-2; screenshot bottom app bar "
                      "(>=50% wide or a ui-card) may cut legs below 4.5 face heights, person loss<=45%",
        "eraser": "LaMa fills every remaining part on the second-crop output (dilate 3px, patches<=768px); "
                  "face boxes never filled; ui-cards >25% on the person and coverage>20% are not filled; "
                  "selected automatically",
        "composition": "Mask R-CNN subject box + 6% sides / 4% top / 3% bottom (min 12px), widened toward "
                       "944x1104; the bottom stays at the frame edge when the mask ends wider than 20% of its widest "
                       "row (legs lost mid-limb); skipped when it keeps >=92% of the area or no person mask",
        "enhancementSelection": "comparison-only; retain cleanup until quality safeguards calibrated",
        "scope": "shared preparation, no assignment; Artists scoped by original artist folder, Various origin unknown",
    },
    "padding": {"size": [944, 1104], "color": list(originals.CREAM), "crop": False},
    "overlayPolicy": "retain original; warn; no preparation hold or manual approval",
    "recommendationPolicy": "the last selected step: composition, else eraser, else second crop, else "
                            "first-crop geometry, else original; never the fixed UI crop or an enhancement",
}


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def sha_file(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_path(root, path):
    """Reject linked ancestors before resolving; junctions must not escape the sandbox."""
    root, path = pathlib.Path(root), pathlib.Path(path)
    if root not in path.parents:
        raise ValueError(f"path must be below {root}: {path}")
    for part in (path, *path.parents):
        if sandbox._is_reparse_point(part):
            raise ValueError(f"refusing linked path: {part}")
        if part == root:
            break
    if root.resolve() not in path.resolve().parents:
        raise ValueError(f"path escapes sandbox: {path}")
    return path


def locations(root, output):
    root, output = pathlib.Path(root).expanduser(), pathlib.Path(output).expanduser()
    if not root.is_absolute() or not output.is_absolute():
        raise ValueError("--root and --out must be absolute paths")
    if not sandbox.is_sandbox_working_path(root) or not root.is_dir():
        raise ValueError("pilot requires an existing sandbox root: Sovereign Territories Sandbox\\Working")
    for part in (root, *root.parents):
        if sandbox._is_reparse_point(part):
            raise ValueError(f"refusing linked sandbox root: {part}")
    base = root / "_reports" / "preparation"
    if output.parent != base or output.name.startswith("."):
        raise ValueError("--out must be a named run directly in Working\\_reports\\preparation")
    safe_path(root, output)
    return root, output


def inventory(root, source_folder=None):
    if source_folder:
        directory = pathlib.Path(source_folder)
        if not directory.is_absolute():
            directory = root / directory
        directory = safe_path(root, directory)
        relative = directory.relative_to(root)
        if (relative.parts[0] not in CATEGORIES or directory.name not in ("gallery", "review")
                or any(part.startswith(".") or part.startswith("_") for part in relative.parts)
                or not directory.is_dir()):
            raise ValueError("--source-folder must be an existing active Gallery/Review folder")
        return [safe_path(root, photo) for photo in originals.images(directory)]
    cfg = {"paths": {"photoRoots": list(CATEGORIES)}}
    for category in CATEGORIES:
        safe_path(root, root / category)
    paths = []
    for folder in upkeep.folders(cfg, root):
        safe_path(root, folder)
        for bucket in ("gallery", "review"):
            directory = safe_path(root, folder / bucket)
            for photo in originals.images(directory):
                paths.append(safe_path(root, photo))
    return sorted(set(paths), key=lambda path: path.relative_to(root).as_posix().casefold())


def sample(root, paths, limit):
    """Round-robin categories and identity folders; prefer screenshots inside each folder."""
    groups = {}
    for path in paths:
        relative = path.relative_to(root)
        groups.setdefault(relative.parts[0], {}).setdefault(relative.parent.parent, []).append(path)
    queues = {}
    for category, people in groups.items():
        people = [collections.deque(sorted(photos, key=lambda p: (
            "_shot_" not in p.name.casefold() and "screenshot" not in p.name.casefold(),
            p.as_posix().casefold()))) for photos in people.values()]
        ordered = []
        while any(people):
            for photos in people:
                if photos:
                    ordered.append(photos.popleft())
        queues[category] = collections.deque(ordered)
    selected = []
    while any(queues.values()) and (not limit or len(selected) < limit):
        for category in CATEGORIES:
            if queues.get(category) and (not limit or len(selected) < limit):
                selected.append(queues[category].popleft())
    return selected


def decode(payload):
    with Image.open(io.BytesIO(payload)) as opened:
        return decode_image(opened)


def decode_file(path):
    with Image.open(path) as opened:
        return decode_image(opened)


def decode_image(opened):
    if getattr(opened, "is_animated", False):
        raise ValueError("animated source: preparation requires a separate frame policy")
    if opened.width * opened.height > RECIPE["maxPixels"]:
        raise ValueError("source exceeds the pilot's 20 megapixel limit")
    image = ImageOps.exif_transpose(opened)
    if "A" in image.getbands() or "transparency" in image.info:
        if image.convert("RGBA").getchannel("A").getextrema()[0] < 255:
            raise ValueError("transparent source: compositing is not approved")
    profile = opened.info.get("icc_profile")
    if profile:
        image = ImageCms.profileToProfile(
            image, ImageCms.ImageCmsProfile(io.BytesIO(profile)),
            ImageCms.createProfile("sRGB"), outputMode="RGB")
    elif image.mode == "CMYK":
        raise ValueError("unprofiled CMYK: color conversion needs review")
    image = image.convert("RGB")
    image.info.clear()
    return image


def candidates(image):
    array = np.asarray(image)
    yield "control", image
    denoised = cv2.bilateralFilter(array, 5, 15, 3)
    yield "denoise", Image.fromarray(denoised)
    lab = cv2.cvtColor(array, cv2.COLOR_RGB2LAB)
    light = lab[:, :, 0]
    adjusted = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8)).apply(light)
    lab[:, :, 0] = cv2.addWeighted(light, 0.65, adjusted, 0.35, 0)
    yield "tone", Image.fromarray(cv2.cvtColor(lab, cv2.COLOR_LAB2RGB))


def write_new(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"refusing to overwrite different pilot artifact: {path}")
    else:
        with path.open("xb") as stream:
            stream.write(payload)
    if sha(path.read_bytes()) != sha(payload):
        raise OSError(f"pilot artifact verification failed: {path}")


def copy_new_file(path, source):
    path.parent.mkdir(parents=True, exist_ok=True)
    source_hash = sha_file(source)
    if path.exists():
        if sha_file(path) != source_hash:
            raise ValueError(f"refusing to overwrite different pilot artifact: {path}")
    else:
        with pathlib.Path(source).open("rb") as incoming, path.open("xb") as outgoing:
            for chunk in iter(lambda: incoming.read(1024 * 1024), b""):
                outgoing.write(chunk)
        if sha_file(path) != source_hash:
            raise OSError(f"pilot artifact verification failed: {path}")
    return source_hash


def save_image(path, image, image_format, **options):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".image-", dir=path.parent)
    temporary = pathlib.Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            image.save(stream, format=image_format, **options)
        candidate_hash = sha_file(temporary)
        if path.exists():
            if sha_file(path) != candidate_hash:
                raise ValueError(f"refusing to overwrite different pilot artifact: {path}")
            return candidate_hash
        os.replace(temporary, path)
        return candidate_hash
    finally:
        temporary.unlink(missing_ok=True)


def mean_absolute_pixel_change(control, variant):
    control_array = np.asarray(control)
    variant_array = np.asarray(variant)
    if control_array.shape != variant_array.shape:
        return None
    total = 0
    for start in range(0, control_array.shape[0], 64):
        end = start + 64
        delta = variant_array[start:end].astype(np.int16) - control_array[start:end].astype(np.int16)
        total += int(np.abs(delta).sum(dtype=np.int64))
    return round(total / control_array.size, 4)


def comparison_candidates(image, row):
    try:
        yield from candidates(image)
    except cv2.error as exc:
        row["outcome"] = "enhancement-failed"
        row["sourceTreatment"] = "original-enhancement-failed"
        row["diagnostics"].append(
            f"Enhancement failed; original retained, no manual approval required: {exc}")


def prepared_candidates(image, row):
    images = {}
    for name, candidate in pipeline.processing_candidates(image, row):
        images[name] = candidate
        yield name, candidate
    selected = row["processing"]["cleanup"]
    prepared = images[selected]
    for name, candidate in comparison_candidates(prepared, row):
        if name != "control":
            row["processing"]["steps"].append(preparation_geometry.step(
                name, "attempted-rejected", selected, name, selected,
                "Rendered for visual comparison from the cleanup recommendation. Not selected automatically: "
                "no calibrated benefit/detail-preservation test; pixel change is not quality."))
            yield name, candidate
    for name in ("denoise", "tone"):
        if not any(s["name"] == name for s in row["processing"]["steps"]):
            row["processing"]["steps"].append(preparation_geometry.step(
                name, "failed" if row["outcome"] == "enhancement-failed" else "skipped",
                selected, None, selected, "Filter unavailable after reported OpenCV failure; retain cleanup input."))


def render_photo(root, stage, source):
    digest = sha_file(source)
    retained = f"originals/{digest}{source.suffix.lower()}"
    copy_new_file(stage / retained, source)
    row = {
        "source": source.relative_to(root).as_posix(),
        "photoId": metadata.photo_id_from_name(source.name),
        "sourceSha256": digest, "retained": retained, "outcome": "compared",
        "sourceTreatment": "original-unassessed",
        "diagnostics": ["Retained current input; uncropped/raw provenance is not verified."],
        "variants": {},
    }
    relative = source.relative_to(root)
    artist = relative.parts[1] if relative.parts[0] == "Artists" and len(relative.parts) >= 4 else None
    row["sourceScope"] = {
        "category": relative.parts[0],
        "artist": artist,
        "matchingDomain": ("Artists/" + artist if artist else "Artists-unassigned")
        if relative.parts[0] == "Artists" else "general",
        "reason": ("Shared preparation only; preserve original artist scope, never mix into general/other artists."
                   if relative.parts[0] == "Artists" else
                   "Shared preparation only; no assignment. Copies in Various have unknown artist provenance; "
                   "use the original Artists/<artist>/gallery location for real artist-scoped processing."),
    }
    try:
        image = decode_file(source)
    except (OSError, ValueError, Image.DecompressionBombError, ImageCms.PyCMSError) as exc:
        row["outcome"] = "unprocessable"
        row["sourceTreatment"] = "unprocessable"
        row["diagnostics"].append(str(exc))
        return row
    faces, assessment = preparation_geometry.detect_faces(image)
    largest = max((min(face[2:]) for face in faces), default=0) if faces is not None else 0
    eligible = ("assessment-failed" if faces is None else
                "junk-candidate" if largest < originals.MIN_FACE_PX else "usable")
    reason = assessment
    if eligible == "junk-candidate":
        reason += (" No detected human face." if not faces else
                   f" Largest detected face minimum dimension {largest:.1f}px < {originals.MIN_FACE_PX}px.")
        reason += " Report-only Junk candidate: no moves/deletion; all preparation/enhancement steps skipped."
    row["eligibility"] = {"status": eligible, "faces": faces or [], "largestFacePixels": largest,
                          "minFace": originals.MIN_FACE_PX, "reason": reason}
    if eligible != "usable":
        row["outcome"] = eligible
        row["diagnostics"].append(reason)
        row["processing"] = {"cleanup": "original", "final": "original", "faceAssessment": reason,
                             "steps": [preparation_geometry.step(name, "skipped", "original", None, "original", reason)
                                       for name in STEPS]}
        return row
    row["geometry"] = preparation_geometry.plan(image)
    row["diagnostics"] += [row["geometry"]["reason"], row["geometry"]["uiCropAssessment"]]
    if row["geometry"]["overlayDetected"]:
        row["outcome"] = "compared-overlay"
        row["sourceTreatment"] = "original-overlay-unremoved"
        row["diagnostics"].append(
            "Overlay detected: original retained without cropping hair; preparation does not block "
            "the image or require manual approval. ComfyUI can perform later cleanup.")
    else:
        row["diagnostics"].append("Not flagged by reel heuristic; this is not proof of no overlays.")
    previous = time.perf_counter()
    for name, variant in prepared_candidates(image, row):
        path = f"candidates/{digest}/{name}.png"
        variant_hash = save_image(stage / path, variant, "PNG")
        thumbnail = variant.copy()
        thumbnail.thumbnail((360, 480), Image.Resampling.LANCZOS)
        preview = f"candidates/{digest}/{name}-preview.jpg"
        preview_hash = save_image(stage / preview, thumbnail, "JPEG", quality=88)
        thumbnail.close()
        fitted = ImageOps.contain(variant, (944, 1104), Image.Resampling.LANCZOS)
        padded = Image.new("RGB", (944, 1104), originals.CREAM)
        padded.paste(fitted, ((944 - fitted.width) // 2, (1104 - fitted.height) // 2))
        padded_path = f"candidates/{digest}/{name}-944x1104.png"
        padded_hash = save_image(stage / padded_path, padded, "PNG")
        fitted.close()
        padded.close()
        row["variants"][name] = {
            "path": path, "sha256": variant_hash, "thumbnail": preview,
            "thumbnailSha256": preview_hash, "padded": padded_path,
            "paddedSha256": padded_hash, "size": list(variant.size),
            "seconds": round(time.perf_counter() - previous, 4),
            "meanAbsolutePixelChange": mean_absolute_pixel_change(image, variant),
        }
        previous = time.perf_counter()
    if row["geometry"]["changed"] and row["outcome"] != "enhancement-failed":
        row["sourceTreatment"] = ("cropped-border-overlay-unremoved"
                                  if row["geometry"]["overlayDetected"] else "cropped-border")
    row["diagnostics"].append(row["processing"]["faceAssessment"])
    return row


def recommendation(row):
    if row["outcome"] in ("junk-candidate", "assessment-failed"):
        return {"use": "none", "reason": row["eligibility"]["reason"]}
    if row["outcome"] == "unprocessable":
        return {"use": "none", "reason": "Input could not be prepared; exact bytes retained. See diagnostic."}
    if row.get("processing"):
        selected = row["processing"]["final"]
        if selected == "composition":
            return {"use": "composition", "reason": (
                "Framed cleanup: the cleaned image cropped to the person found by Mask R-CNN (whole body, hands "
                "and dress) with a small margin, widened toward 944x1104. Pure crop of the cleaned image. "
                "Compare with the retained original.")}
        if selected == "eraser":
            return {"use": "eraser", "reason": (
                "Cleaned image: the crops removed what they could without cutting the person, then LaMa "
                "repainted the clutter left inside (icons, captions, search bubble, corner logos). Repainted "
                "areas are plausible, not recovered; faces are never repainted. Compare with the retained original.")}
        if selected == "second-crop":
            return {"use": "second-crop", "reason": (
                "Graphic-free second crop: a pure crop past the edge clutter that keeps the person (Mask R-CNN "
                "mask plus a margin). No pixels are invented. Compare with the retained original.")}
        return {"use": "geometry" if selected == "geometry" else "original",
                "reason": ("Provisional native-source recommendation after crop/eraser trials: "
                           + selected + ". "
                           + ("Enhancement failed; retain last safe cleanup. " if row["outcome"] == "enhancement-failed" else "")
                           + "No crop or repaint could improve on it without cutting the person or a face. "
                           "Denoise/tone remain review alternatives, "
                           "so the final recommendation retains the cleanup selection. "
                           "Unresolved overlays pass through for ComfyUI; this is not a measured quality winner.")}
    if row["sourceTreatment"] == "original-overlay-unremoved":
        reason = "Keep original and its hair/content; overlay cleanup is left for ComfyUI, without a preparation hold."
    elif row["sourceTreatment"] == "original-enhancement-failed":
        reason = "Enhancement failed; use the unchanged original, not a partial or unverified enhancement."
    else:
        reason = ("Conservative default: use original. Denoise/tone are unapproved comparisons, "
                  "not automatically better images. Borders/graphics may remain; clean status is not inferred.")
    if row.get("geometry", {}).get("changed") and row["outcome"] != "enhancement-failed":
        return {"use": "geometry", "reason": (
            "Use border-only geometry candidate: conservatively detected solid external strips removed "
            "before enhancement. Not a semantic hair-safety guarantee; compare against retained original. "
            "Remaining overlays are left for ComfyUI; fixed UI crop and denoise/tone are not recommended.")}
    return {"use": "original", "reason": reason}


def report(data, *, detail=False):
    esc = html.escape
    cards = []
    for row in data["photos"]:
        prefix = "../" if detail else ""
        panels = []
        if detail:
            raw = quote(prefix + row["retained"])
            panels.append(f'<figure><figcaption>Exact retained input (current Gallery/Review bytes; '
                          f'uncropped provenance unknown)</figcaption><a href="{raw}">'
                          f'<img src="{raw}" alt="retained input"></a></figure>')
        for name, variant in row["variants"].items():
            target = quote(prefix + variant["path"]) if detail else quote(row["detail"])
            display = variant["path"] if detail else variant["thumbnail"]
            change = variant["meanAbsolutePixelChange"]
            metric = f"{change:.2f}/255" if change is not None else "not comparable (different crop dimensions)"
            panels.append(
                f'<figure><figcaption>{name}: {variant["seconds"]:.3f}s; '
                f'pixel change {metric}</figcaption>'
                f'<a href="{target}"><img loading="lazy" '
                f'src="{quote(prefix + display)}" alt="{name}"></a></figure>')
        padding = ""
        if detail:
            padded_panels = "".join(
                f'<figure><figcaption>{name} padded 944x1104 (no crop)</figcaption>'
                f'<a href="{quote(prefix + variant["padded"])}"><img loading="lazy" '
                f'src="{quote(prefix + variant["padded"])}" alt="{name} padded"></a></figure>'
                for name, variant in row["variants"].items())
            padding = f'<h3>Downstream padded candidates</h3><div class="panels">{padded_panels}</div>'
        notes = " ".join(esc(message) for message in row["diagnostics"])
        treatment = esc(row.get("sourceTreatment", "original-unassessed"))
        geometry_html = ""
        if row.get("geometry"):
            geometry = row["geometry"]
            geometry_html = (f'<p>Border geometry [left, top, right, bottom]: {esc(str(geometry["box"]))}; '
                             f'UI proposal: {esc(str(geometry["uiCropBox"]))}. '
                             f'Changed: {geometry["changed"]}.</p>')
        processing_html = ""
        if row.get("processing"):
            processing = row["processing"]

            def summary_view(label, name):
                path = row["retained"] if name == "original" else row["variants"][name]["path"]
                return (f'<figure><figcaption>{esc(label)}: {esc(name)}</figcaption>'
                        f'<a href="{quote(prefix + path)}"><img loading="lazy" '
                        f'src="{quote(prefix + path)}" alt="{esc(label)}"></a></figure>')

            held = row["outcome"] in ("junk-candidate", "assessment-failed")
            summaries = (summary_view("1. Original", "original")
                         + summary_view("2. Not recommended - processing skipped" if held else
                                        "2. Recommended after crop / eraser", processing["cleanup"])
                         + summary_view("3. No source recommended for generation" if held else
                                        "3. Final recommended source for 944x1104", processing["final"]))
            rows = []
            for s in processing["steps"]:
                candidate = s["candidate"]
                link = (f'<a href="{quote(prefix + row["variants"][candidate]["path"])}">{esc(candidate)}</a>'
                        if candidate else "No candidate (see reason)")
                rows.append(f'<tr><td>{esc(s["name"])}</td><td>{esc(s["status"])}</td>'
                            f'<td>{esc(s["input"])}</td><td>{link}</td><td>{esc(s["selected"])}</td>'
                            f'<td>{esc(s["reason"])}</td></tr>')
            processing_html = (
                f'<h3>Decision summary (provisional, please review)</h3><div class="panels">{summaries}</div>'
                f'<p>{esc(processing["faceAssessment"])}</p><h3>Processing trace</h3>'
                '<div class="trace"><table><thead><tr><th>Step</th><th>Result</th><th>Input</th>'
                '<th>Attempt output</th><th>Kept</th><th>Reason / limitations</th></tr></thead>'
                f'<tbody>{"".join(rows)}</tbody></table></div>')
            comparison = processing.get("reconstructionComparison")
            if comparison:
                candidate = comparison["candidate"]
                link = (f'<a href="{quote(prefix + row["variants"][candidate]["path"])}">'
                        f'{esc(candidate)}</a>' if candidate else "No candidate")
                processing_html += (
                    '<h3>Same-mask reconstruction alternative (not selected)</h3>'
                    f'<p>{esc(comparison["method"])}: {esc(comparison["status"])}. '
                    f'Input: {esc(comparison["input"])}; mask: {esc(comparison["mask"])}. {link}. '
                    f'{esc(comparison["reason"])}</p>')
        advice = row.get("recommendation")
        recommendation_html = ""
        if advice:
            if advice["use"] in ("geometry", "second-crop", "eraser", "composition"):
                label = {"second-crop": "Graphic-free second crop", "composition": "Framed cleanup",
                         "eraser": "Cleaned (crop + LaMa eraser)",
                         "geometry": "Border/panel geometry"}[advice["use"]] + " (provisional recommendation)"
                target = f'<a href="{quote(prefix + row["variants"][advice["use"]]["path"])}">{label}</a>'
            else:
                target = (f'<a href="{quote(prefix + row["retained"])}">Original (recommended)</a>'
                          if advice["use"] == "original" else "No usable preparation output")
            recommendation_html = f'<p><strong>Recommended:</strong> {target}. {esc(advice["reason"])}</p>'
        cards.append(
            f'<article><h2>{esc(row["source"])}</h2><p>{esc(row["outcome"])}: {notes}</p>'
            + (f'<p>Source scope: <strong>{esc(row["sourceScope"]["matchingDomain"])}</strong>. '
               f'{esc(row["sourceScope"]["reason"])}</p>' if row.get("sourceScope") else "")
            +
            f'{processing_html}'
            f'<p><a href="{quote(prefix + row["retained"])}">Exact retained input</a> | '
            f'<a href="{quote(prefix + row["detail"])}">All views / larger comparison</a> | '
            f'Photo ID: {esc(row["photoId"] or "unregistered; no ID invented")}</p>'
            f'<p>Source treatment: <strong>{treatment}</strong></p>'
            f'{geometry_html}'
            f'{recommendation_html}'
            f'<p>Decision: processing is skipped for unusable/unassessed faces. Otherwise each step keeps its '
            f'result when it is safe: first crop, a second crop that never cuts the person, the LaMa eraser for the '
            f'clutter left inside, then framing. Denoise/tone are never accepted automatically.</p>'
            f'<div class="panels">{"".join(panels)}</div>{padding}</article>')
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width"><title>Image preparation pilot</title>'
        f'<style>{gallery_chrome.CSS}article{{background:var(--st-card);border:1px solid var(--st-line);'
        'border-radius:var(--st-radius);box-shadow:var(--st-shadow);'
        'padding:16px;margin-bottom:20px}h2{font-size:18px;overflow-wrap:anywhere}'
        '.panels{display:flex;flex-wrap:wrap;gap:12px}figure{margin:0;max-width:360px}'
        'img{max-width:100%;height:auto}figcaption{padding:8px 0}'
        'details{background:var(--st-card);border:1px solid var(--st-line);border-radius:var(--st-radius);padding:10px 14px}'
        '.trace{overflow-x:auto}table{border-collapse:collapse;width:100%}td,th{border:1px solid var(--st-line);'
        'padding:8px;text-align:left;vertical-align:top}th{background:#efebe3}'
        '.detail figure{max-width:620px;flex:1 1 440px}</style>'
        + ('<body class="detail" id="top">' if detail else '<body id="top">')
        + gallery_chrome.masthead(None, "../../../" if detail else "../../", "Image intake preparation", links=False)
        + '<div class="site-page">'
        '<header class="page-header"><div><h1>Image preparation pilot - experimental, no library changes</h1></div></header>'
        + ('<p><a href="../index.html">Back to comparison gallery</a></p>' if detail else '')
        +
        '<p>Control: oriented/sRGB only. Denoise and tone are separate alternatives, not a '
        'combined approved recipe. Click for full-resolution candidates or exact retained input. '
        'Crop/eraser trials come first; local face detection only, no identity scoring or assignment. '
        'Recommendations are provisional; matching is not run.</p>'
        '<details open><summary>What each image means / which should I use?</summary><ul>'
        '<li><strong>Original:</strong> exact input bytes, retained before any processing; '
        'recommended only when no crop or repaint step was safe.</li>'
        '<li><strong>Face eligibility:</strong> no detected human face or largest minimum face dimension '
        'below 60px skips all transforms as a report-only Junk candidate. Detector errors are separate errors, '
        'not Junk. Multiple faces and overlays alone are not rejected by this gate. Detection can miss faces.</li>'
        '<li><strong>Control:</strong> EXIF orientation and color-profile conversion to sRGB only; '
        'same content, not denoised, cropped or enhanced.</li>'
        '<li><strong>Denoise:</strong> gentle smoothing alternative; can remove real fine detail.</li>'
        '<li><strong>Tone:</strong> local light/contrast alternative, not denoise or overlay repair.</li>'
        '<li><strong>Geometry:</strong> solid borders and guarded black reel panels trimmed first; '
        'unchanged if none qualify. Denoise/tone start from the selected cleanup image.</li>'
        '<li><strong>Second-crop:</strong> runs before any repaint. Each side (top, bottom, left, right) is '
        'trimmed past its edge clutter only as far as the person allows (Mask R-CNN person mask plus a margin; '
        'at most 0.5% of the person lost). On screenshots a screen-wide app bar may cut the legs well below the hips. '
        'A pure crop: no pixels invented.</li>'
        '<li><strong>Eraser / eraser-mask:</strong> LaMa repaints the clutter the crop could not reach (white icons '
        'and captions, the search bubble over the hair, corner logo badges) on the second-crop output, and the '
        'result is kept. White mask pixels are what was repainted. Faces are never repainted; cards lying on the '
        'body and anything over a fifth of the picture are left. Repainted hair and background are plausible, '
        'not recovered: compare with the original.</li>'
        '<li><strong>Composition:</strong> frames the whole person (hands, legs, dress) with a small margin, '
        'widened toward 944x1104, to trim excess background. Skipped when it would gain little.</li>'
        '<li><strong>UI-crop-proposal:</strong> the existing screenshot crop rectangle; comparison '
        'only, never recommended because it may cut hair/body. It removes pixels, not overlaid graphics.</li>'
        '<li><strong>Padded 944x1104:</strong> each candidate fitted without cropping onto a cream '
        'canvas, for downstream display; padding does not clean or repair the photo.</li></ul>'
        '<p>Recommendations are provisional, not measured quality rankings. Clutter detection is heuristic: '
        'an image where nothing was found may still have overlays (round avatar photos and picture-in-picture '
        'thumbnails are not detected yet). No image is labelled clean just because detection missed it.</p></details>'
        '<p>Pixel change is not image quality or likeness confidence. Existing crops cannot '
        'recover lost hair; retained input may already be cropped. No candidate is published '
        'to Gallery/Review or ComfyUI. Local copies are not an independent backup.</p>'
        f'<p>Available category counts: {esc(json.dumps(data["inventory"]))}. '
        f'Comparison/warning/error rows: {len(data["photos"])}.</p>'
        + "".join(cards) + gallery_chrome.footer("Sidecar comparisons only · No library changes")
        + '</div></body></html>\n').encode("utf-8")


def validate_processing(row, *, same_mask_comparison=False, names=legacy.OLD_STEPS):
    processing = row.get("processing")
    if not processing:
        raise ValueError(f"missing processing trace: {row['source']}")
    variants = row["variants"]
    steps = processing["steps"]
    if [s["name"] for s in steps] != list(names):
        raise ValueError(f"invalid processing step order: {row['source']}")
    selected = "control"
    for s in steps:
        if s["input"] != selected or s["selected"] not in variants:
            raise ValueError(f"broken processing lineage: {row['source']}")
        candidate = s["candidate"]
        if s["status"].startswith("attempted-"):
            if candidate not in variants:
                raise ValueError(f"missing processing candidate: {row['source']}")
            if s["status"] == "attempted-selected" and s["selected"] != candidate:
                raise ValueError(f"selected candidate disagrees with decision: {row['source']}")
            if s["status"] == "attempted-rejected" and s["selected"] != selected:
                raise ValueError(f"rejected candidate changed selection: {row['source']}")
        elif candidate is not None or s["selected"] != selected:
            raise ValueError(f"skipped/failed step changed selection: {row['source']}")
        selected = s["selected"]
        if s["name"] == names[-3] and processing["cleanup"] != selected:
            raise ValueError(f"cleanup selection disagrees with trace: {row['source']}")
    if processing["final"] != selected:
        raise ValueError(f"final selection disagrees with trace: {row['source']}")
    expected = {"control", "geometry"}
    if row["geometry"]["uiCropBox"]:
        expected.add("ui-crop-proposal")
    expected.update(s["candidate"] for s in steps if s["candidate"])
    if "eraser" in expected:
        expected.add("eraser-mask")
    comparison = processing.get("reconstructionComparison")
    eraser_step = next(s for s in steps if s["name"] == "eraser")
    if same_mask_comparison and ("eraser" in expected) != (comparison is not None):
        raise ValueError(f"missing/unexpected reconstruction comparison: {row['source']}")
    if comparison:
        if (not same_mask_comparison or "eraser" not in expected or comparison["input"] != eraser_step["input"]
                or comparison["mask"] != "eraser-mask"):
            raise ValueError(f"broken reconstruction comparison lineage: {row['source']}")
        if comparison["status"] == "attempted-rejected":
            if comparison["candidate"] != "eraser-ns":
                raise ValueError(f"missing reconstruction comparison candidate: {row['source']}")
            expected.add("eraser-ns")
        elif comparison["candidate"] is not None:
            raise ValueError(f"failed reconstruction comparison has candidate: {row['source']}")
    if set(variants) != expected:
        raise ValueError(f"unexpected/missing traced variants: {row['source']}")
    cleanup_size = variants[processing["cleanup"]]["size"]
    eraser_size = variants[eraser_step["input"]]["size"]
    for name in ("eraser", "eraser-ns", "eraser-mask", "denoise", "tone"):
        wanted_size = eraser_size if name.startswith("eraser") else cleanup_size
        if name in variants and variants[name]["size"] != wanted_size:
            raise ValueError(f"processing input dimensions disagree: {row['source']}")
    wanted = "original" if selected == "control" else selected
    if row["recommendation"]["use"] != wanted:
        raise ValueError(f"recommendation disagrees with final selection: {row['source']}")


def validate(data):
    Draft7Validator(json.loads(SCHEMA.read_text(encoding="utf-8"))).validate(data)
    sources = [row["source"] for row in data["photos"]]
    if not sources:
        raise ValueError("pilot manifest contains no photos")
    if len(set(sources)) != len(sources):
        raise ValueError("duplicate source in pilot manifest")
    for row in data["photos"]:
        geometry = row.get("geometry")
        recipe = data["recipe"].get("id")
        traced = recipe == CURRENT or recipe in legacy.TRACED
        if recipe == CURRENT or recipe in legacy.SCOPED:
            sandbox._safe_source_path(row["source"])
            relative = pathlib.PurePosixPath(row["source"])
            if len(relative.parts) < 3 or relative.parts[0] not in CATEGORIES:
                raise ValueError(f"invalid preparation source: {row['source']}")
            scope = row.get("sourceScope")
            artist = relative.parts[1] if relative.parts[0] == "Artists" and len(relative.parts) >= 4 else None
            domain = ("Artists/" + artist if artist else "Artists-unassigned") if relative.parts[0] == "Artists" else "general"
            if (not scope or scope["category"] != relative.parts[0]
                    or scope["artist"] != artist or scope["matchingDomain"] != domain):
                raise ValueError(f"source/artist scope disagrees with source path: {row['source']}")
        if traced and row["outcome"] != "unprocessable":
            eligibility = row.get("eligibility")
            if not eligibility:
                raise ValueError(f"missing face eligibility: {row['source']}")
            if eligibility["status"] in ("junk-candidate", "assessment-failed"):
                processing = row.get("processing", {})
                steps = processing.get("steps", [])
                if (row["outcome"] != eligibility["status"] or row["variants"] or geometry
                        or processing.get("reconstructionComparison") is not None
                        or row["recommendation"]["use"] != "none"
                        or processing.get("cleanup") != "original" or processing.get("final") != "original"
                        or [s["name"] for s in steps] != step_names(recipe)
                        or any(s["status"] != "skipped" or s["candidate"] is not None
                               or s["input"] != "original" or s["selected"] != "original" for s in steps)):
                    raise ValueError(f"invalid skipped-face processing: {row['source']}")
                continue
            if eligibility["largestFacePixels"] < eligibility["minFace"]:
                raise ValueError(f"unusable face passed processing gate: {row['source']}")
        if (recipe == CURRENT or recipe in legacy.GEOMETRY) and row["outcome"] != "unprocessable":
            if not geometry or not row.get("recommendation"):
                raise ValueError(f"missing geometry/recommendation: {row['source']}")
        if geometry:
            if "control" not in row["variants"] or "geometry" not in row["variants"]:
                raise ValueError(f"missing geometry/control candidate: {row['source']}")
            width, height = row["variants"]["control"]["size"]
            for box in (geometry["box"], geometry["uiCropBox"]):
                if box is not None and not (0 <= box[0] < box[2] <= width and 0 <= box[1] < box[3] <= height):
                    raise ValueError(f"crop box outside control: {row['source']}")
            if geometry["changed"] != (geometry["box"] != [0, 0, width, height]):
                raise ValueError(f"geometry change disagrees with box: {row['source']}")
            if geometry["overlayDetected"] != (geometry["uiCropBox"] is not None):
                raise ValueError(f"overlay and UI proposal disagree: {row['source']}")
            box = geometry["box"]
            if row["variants"]["geometry"]["size"] != [box[2] - box[0], box[3] - box[1]]:
                raise ValueError(f"geometry dimensions disagree with crop box: {row['source']}")
        if row.get("recommendation", {}).get("use") == "geometry":
            if (not geometry or not geometry["changed"] or "geometry" not in row["variants"]
                    or row["outcome"] == "unprocessable"
                    or (row["outcome"] == "enhancement-failed" and not traced)):
                raise ValueError(f"invalid geometry recommendation: {row['source']}")
        if traced and row["outcome"] != "unprocessable":
            validate_processing(row, same_mask_comparison=recipe in legacy.SAME_MASK, names=step_names(recipe))
            continue
        if row["outcome"] == "enhancement-failed":
            if "control" not in row["variants"] or row.get("sourceTreatment") != "original-enhancement-failed":
                raise ValueError(f"enhancement failure must retain a control and explicit reason: {row['source']}")
            allowed = {"control", "denoise", "tone"}
            if geometry:
                allowed.add("geometry")
                if geometry["uiCropBox"]:
                    allowed.add("ui-crop-proposal")
                if "geometry" not in row["variants"]:
                    raise ValueError(f"missing geometry candidate: {row['source']}")
            if not set(row["variants"]) <= allowed:
                raise ValueError(f"unexpected failed comparison variants: {row['source']}")
            continue
        expected = set() if row["outcome"] == "unprocessable" else {"control", "denoise", "tone"}
        if geometry:
            expected.add("geometry")
            if geometry["uiCropBox"]:
                expected.add("ui-crop-proposal")
        if set(row["variants"]) != expected:
            raise ValueError(f"incomplete comparison variants: {row['source']}")


def verify(root, output, *, current_sources=True):
    manifest = safe_path(root, output / "manifest.json")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    validate(data)
    disposition = preparation_junk.verified_journal(root, output) if current_sources else None
    moved = ({move["source"]: move["target"] for move in disposition["moves"]}
             if disposition and disposition["status"] == "applied" else {})
    if data["root"] != str(root):
        raise ValueError("pilot manifest root differs from --root")
    for row in data["photos"]:
        sandbox._safe_source_path(row["source"])
        relative = pathlib.PurePosixPath(row["source"])
        if relative.parts[0] not in CATEGORIES or relative.parent.name not in ("gallery", "review"):
            raise ValueError(f"invalid pilot source: {relative}")
        artifacts = [(row["retained"], row["sourceSha256"]), (row["detail"], row["detailSha256"])]
        for variant in row["variants"].values():
            artifacts += [(variant["path"], variant["sha256"]),
                          (variant["thumbnail"], variant["thumbnailSha256"]),
                          (variant["padded"], variant["paddedSha256"])]
        for relative, digest in artifacts:
            sandbox._safe_source_path(relative)
            path = safe_path(output, output / relative)
            if sha(path.read_bytes()) != digest:
                raise ValueError(f"pilot artifact hash mismatch: {path}")
        if current_sources:
            source = safe_path(root, root / moved.get(row["source"], row["source"]))
            if sha(source.read_bytes()) != row["sourceSha256"]:
                raise ValueError(f"source changed since pilot: {source}; use a new run")
    page = safe_path(output, output / "index.html")
    if sha(page.read_bytes()) != data["reportSha256"]:
        raise ValueError("pilot HTML hash mismatch")
    return data


def run(args):
    root, output = locations(args.root, args.out)
    if args.quarantine_junk or args.undo_junk:
        data = verify(root, output, current_sources=True)
        import comfy_workflows as cw
        return preparation_junk.route(root, output, data, cw.load_cfg(), apply=args.apply, undo=args.undo_junk)
    if args.check:
        data = verify(root, output)
        print(f"Verified {len(data['photos'])} retained inputs, candidates, thumbnails and current sources.")
        return int(any(row["outcome"] in ("unprocessable", "assessment-failed") for row in data["photos"]))
    paths = inventory(root, args.source_folder)
    source_folder = None
    if args.source_folder:
        directory = pathlib.Path(args.source_folder)
        source_folder = (directory if directory.is_absolute() else root / directory).relative_to(root).as_posix()
    selected = sample(root, paths, args.limit)
    counts = {category: sum(p.relative_to(root).parts[0] == category for p in paths) for category in CATEGORIES}
    print(f"Inventory: {json.dumps(counts)}; selected {len(selected)} of {len(paths)}.")
    print("Sidecar preparation only. No source changes, matching, membership changes or ComfyUI writes.")
    print("Apply may download pinned CPU models once; preview and check do not download models.")
    for source in selected:
        print(f"  {source.relative_to(root)}")
    if not selected:
        raise ValueError("no supported Gallery/Review images found")
    if not args.apply:
        print(f"Preview only. Add --apply to retain exact inputs and publish comparisons in {output}")
        return 0
    return publish(root, output, selected, limit=args.limit, source_folder=source_folder, counts=counts)


def publish(root, output, selected, *, limit=0, source_folder=None, counts=None):
    """Publish one immutable report; sandbox orchestration supplies a verified source mirror."""
    safe_path(root, output)
    for source in selected:
        safe_path(root, source)
    if counts is None:
        counts = {category: sum(path.relative_to(root).parts[0] == category for path in selected)
                  for category in CATEGORIES}
    if output.exists():
        data = verify(root, output)
        if (data["recipe"] != RECIPE or data["limit"] != limit
                or [r["source"] for r in data["photos"]] != [p.relative_to(root).as_posix() for p in selected]
                or data["inventory"] != counts or data.get("sourceFolder") != source_folder):
            raise ValueError("existing run has different inputs/recipe; choose a new --out")
        print(f"Existing run verified without rewriting: {output / 'index.html'}")
        return int(any(row["outcome"] in ("unprocessable", "assessment-failed") for row in data["photos"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    data = {"schemaVersion": 1, "root": str(root), "recipe": RECIPE,
            "limit": limit, "sourceFolder": source_folder, "inventory": counts, "photos": []}
    with tempfile.TemporaryDirectory(prefix=".preparation-", dir=output.parent) as temporary:
        stage = pathlib.Path(temporary) / "run"
        stage.mkdir()
        for index, source in enumerate(selected, 1):
            row = render_photo(root, stage, source)
            row["recommendation"] = recommendation(row)
            row["detail"] = f"photos/{sha(row['source'].encode('utf-8'))}.html"
            detail = report({**data, "photos": [row]}, detail=True)
            write_new(stage / row["detail"], detail)
            row["detailSha256"] = sha(detail)
            data["photos"].append(row)
            print(f"Prepared {index}/{len(selected)}: {data['photos'][-1]['outcome']}", flush=True)
        page = report(data)
        write_new(stage / "index.html", page)
        data["reportSha256"] = sha(page)
        validate(data)
        write_new(stage / "manifest.json", (json.dumps(data, indent=2) + "\n").encode("utf-8"))
        verify(root, stage)
        os.rename(stage, output)
    print(f"Published comparison report: {output / 'index.html'}")
    return int(any(row["outcome"] in ("unprocessable", "assessment-failed") for row in data["photos"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="absolute sandbox Working directory")
    parser.add_argument("--out", required=True, help="absolute Working\\_reports\\preparation\\RUN")
    parser.add_argument("--limit", type=int, default=28, help="round-robin sample size; 0 = all active sources")
    parser.add_argument("--source-folder", help="one active Gallery/Review folder below Working; no recursion")
    disposition = parser.add_mutually_exclusive_group()
    disposition.add_argument("--quarantine-junk", action="store_true",
                             help="preview report-bound loose-intake Junk moves; --apply backs up and moves, no deletion")
    disposition.add_argument("--undo-junk", action="store_true",
                             help="preview/--apply exact undo of this report's completed Junk disposition")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true",
                      help="write sidecar comparisons, or apply an explicitly requested Junk disposition")
    mode.add_argument("--check", action="store_true", help="verify existing run; read only")
    args = parser.parse_args(argv)
    if (args.quarantine_junk or args.undo_junk) and args.check:
        parser.error("--check verifies reports and existing Junk journals; do not combine with disposition modes")
    if (args.quarantine_junk or args.undo_junk) and (args.source_folder is not None or args.limit != 28):
        parser.error("Junk disposition uses the immutable report scope, not --source-folder/--limit")
    if args.limit < 0:
        parser.error("--limit must be non-negative")
    try:
        return run(args)
    except (OSError, ValueError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
