"""Shared masked overlay reconstruction and observed-picture composition."""
import cv2
import numpy as np

from intake_library import clutter, fill, pipeline

HEAD_POLICY = "pattern-overlay-reconstruction-picture-composition-v9"
HEAD_MAX_FILL = .3
STATUS_MARGIN = 0
BADGE_GROW = .0075


def pill_icons(array, top, bottom):
    """Bounded bright outlined icon proposals beside an already detected pill, not semantic UI recognition."""
    height, width = array.shape[:2]
    bright = (array.min(axis=2) >= 240).astype(np.uint8)
    region = np.zeros_like(bright)
    region[max(0, top):min(height, bottom), int(.85 * width):] = 1
    bright *= region
    count, labels, stats, _ = cv2.connectedComponentsWithStats(bright)
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
    evidence = {"status": "skipped", "reason": "No pill or overlay pattern proposal; not proof of clean.",
                "selected": False, "parts": [], "outsideMaskIdentical": None}
    row["experiment"]["headOverlay"] = evidence
    layout = row["experiment"].get("screenshotLayout")
    proposals = row["experiment"].get("overlayParts")
    if proposals is None:
        proposals = (layout or {}).get("overlayParts", [])
    if row.get("eligibility", {}).get("status") != "usable":
        proposals = []
    if not pills and not proposals:
        return
    mask = np.zeros(array.shape[:2], dtype=bool)
    for item in pills:
        mask |= item["mask"]
        evidence["parts"].append({"kind": item["kind"], "box": item["box"]})
    if pills:
        # Keep nearby icon proposals bounded to the detected pill's vertical band.
        top = min(item["box"][1] for item in pills)
        bottom = max(item["box"][3] for item in pills)
        for item in clutter.glyphs(array, None, screenshot=True) + pill_icons(array, top, bottom):
            x0, y0, x1, y1 = item["box"]
            if x0 >= .8 * image.width and y0 >= top - .02 * image.height and y1 <= bottom + .02 * image.height:
                mask |= clutter.grow(item["mask"], max(2, round(min(image.size) * clutter.GROW)))
                evidence["parts"].append({"kind": "near-pill-icon-proposal", "box": [x0, y0, x1, y1]})
    if proposals:
        parent = row["experiment"]["final"]
        sx, sy, _, _ = row["experiment"]["candidates"][parent]["sourceBox"]
        face_mask = np.zeros(mask.shape, dtype=bool)
        # A face whose centre sits inside a pattern part is that part's own avatar/thumbnail, not the subject.
        pattern_boxes = [item["box"] for item in proposals if item.get("pattern")]
        faces = [face for face in row["eligibility"]["faces"]
                 if not any(b[0] <= face[0] + face[2] / 2 <= b[2] and b[1] <= face[1] + face[3] / 2 <= b[3]
                            for b in pattern_boxes)]
        for box in clutter.face_boxes(faces, (sx, sy), image.size):
            face_mask |= clutter.solid(mask.shape, box)
        for item in proposals:
            bx0, by0, bx1, by1 = item["box"]
            box = [max(0, bx0 - sx), max(0, by0 - sy),
                   min(image.width, bx1 - sx), min(image.height, by1 - sy)]
            if box[2] <= box[0] or box[3] <= box[1]:
                continue
            if item.get("circle"):
                cx, cy, radius = item["circle"]
                disc = np.zeros(mask.shape, dtype=np.uint8)
                cv2.circle(disc, (round(cx - sx), round(cy - sy)), round(radius), 1, cv2.FILLED)
                # The badge's glow and anti-aliased rim reach past the fitted ring; leaving it in
                # context makes the fill repaint a ghost of the logo (r20 triage, Oct 28).
                piece = clutter.grow(disc > 0, max(3, round(min(image.size) * BADGE_GROW)))
            elif item.get("polygon"):
                shape = np.zeros(mask.shape, dtype=np.uint8)
                points = np.round(np.array(item["polygon"]) - [sx, sy]).astype(np.int32)
                cv2.fillPoly(shape, [points], 1)
                piece = clutter.grow(shape > 0, max(2, round(image.width * .003)))
            else:
                piece = clutter.grow(clutter.solid(mask.shape, box), max(4, round(image.width * .006)))
            if (piece & face_mask).any() and item["kind"] != "reel-search-pill":
                evidence.setdefault("refusedParts", []).append(dict(item, reason="Face overlap outside pill."))
                continue
            mask |= piece
            evidence["parts"].append(dict(item, box=box, sourceBox=item["box"]))
    coverage = float(mask.mean())
    evidence.update(coverage=coverage, maskPixels=int(mask.sum()))
    if coverage > HEAD_MAX_FILL:
        evidence.update(status="refused", reason=f"Complete UI mask exceeds {HEAD_MAX_FILL:.0%} fill coverage.")
        return
    yield "head-overlay-mask", pipeline.mask_image(mask)
    try:
        painted = fill.fill(image, mask)
    except (OSError, RuntimeError, cv2.error) as exc:
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
        reel = evidence.get("overlayFrame") or {}
        band = reel.get("statusBand")
        person_box = (evidence.get("subject") or {}).get("box")
        if (reel.get("layout") == "full-bleed" and band and person_box
                and person_box[1] >= band[3] + STATUS_MARGIN * original.height):
            py0 = max(py0, band[3])  # the status-bar scrim leaves a seam; the person starts below it
        frame = [px0 - x0, py0 - y0, px1 - x0, py1 - y0]
        if not (0 <= frame[0] < frame[2] <= restored.width
                and 0 <= frame[1] < frame[3] <= restored.height):
            raise ValueError("screenshot composition outside prepared reconstruction")
        proposed = restored.crop(frame)
        candidates["head-overlay-composition"] = {
            "input": selected, "size": list(proposed.size), "sourceBox": [px0, py0, px1, py1],
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
