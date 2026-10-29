"""Recipe v22 sequence: overlay preflight -> guarded crop/erase/reconstruct/compose.

The eraser handles confirmed clutter before the residual subject-guarded crop. Confirmed patterns may use a
separate masked reconstruction path; composition uses the repaired image and observed picture boundary.
Denoise and tone are compared later.
"""
import cv2
import numpy as np
from PIL import Image

import preparation_geometry as geometry
from intake_library import clutter, fill, overlays, subject as subjects

STEPS = ("first-crop", "second-crop", "eraser", "composition", "denoise", "tone")
PREPARED_STEPS = ("first-crop", "eraser", "residual-crop", "reconstruction", "composition", "denoise", "tone")
BANDS = {"top": .25, "bottom": .4, "left": .3, "right": .3}
MAX_CROP_LOSS = .5      # the second crop keeps at least half the image
SUBJECT_LOSS = .005     # ... and at most 0.5% of the person plus a margin
BODY_KEEP = 4.5         # bottom app UI may cut legs only below 4.5 face heights under the face top
MAX_FILL = .2           # never repaint more than a fifth of the picture
CARD_ON_BODY = .25      # a card lying this much on the person is not repainted (it would invent the body)
TARGET = 944 / 1104
LIMB_WIDTH = .2         # a mask ending wider than this share of its widest row was cut off mid-leg, not at the feet
EXPERIMENT_POLICY = (
    "erase-before-residual-v10: original face assessment; profile-driven reel frame (overlay_profiles.json, "
    "bottom navigation rows require horizontal flatness, paired rounded outlines confirm transparent pills, boxed "
    "pictures end at their black) or paired screenshot picture/panel transitions crop external UI while preserving "
    "complete overlapping pill; otherwise solid-border and flat letterbox-bar first crop; reel parts, "
    "structure-confirmed badges including transparent ring/central-letter verification, "
    "three-control playback/timecodes, lower-left nested-reel screen confirmed by a secondary face and phone-frame "
    "edges, perimeter-and-letter confirmed caption buttons, "
    "stroke-verified corner watermarks/caption blocks, corner sparkles, "
    "tilted stickers (polygon masks), viewer corner icons and reference-bank logos "
    "are overlay proposals on any image; colour-blob logos are never used; "
    "screenshot panel proposals comparison-only before erase; existing clutter masks and fill; "
    "refuse unconfirmed glyphs on ordinary photos, face/body/unknown and >20% coverage; "
    "one clutter redetection only after successful fill; "
    "one residual crop; cumulative grown-subject loss <=0.5%, no screenshot app-bar exception; "
    "composition proposals comparison-only, missing hair/feet completeness proof retains precomposition image; "
    "no second fill; detector misses never prove clean; comparison only"
)


def find_subject(image, faces, offset, *, detector_errors=None):
    """(subject, method, note): Mask R-CNN people, else a body frame around the faces."""
    try:
        found = subjects.detect(image)
    except (OSError, RuntimeError, ValueError) as exc:
        if detector_errors is not None:
            detector_errors.append({"stage": "subject", "detector": "person",
                                    "type": type(exc).__name__, "message": str(exc)})
        found, note = None, f"Person detector unavailable ({exc}); "
    else:
        note = "" if found else "Mask R-CNN found no person; "
    if found:
        return found, "mask-rcnn", (
            f"Mask R-CNN subject {found['box']}: {found['people']} person(s), {found['dropped']} small figure(s) "
            "ignored (ad thumbnails, background people).")
    found = subjects.from_faces(faces, offset, image.size)
    return found, "face-frame", note + "a body frame around the detected faces stands in for the person."


def within(item, side, box):
    x0, y0, x1, y1 = item["box"]
    bx0, by0, bx1, by1 = box
    if not (x0 >= bx0 and y0 >= by0 and x1 <= bx1 and y1 <= by1):
        return False
    band = BANDS[side]
    return {"top": y1 <= by0 + band * (by1 - by0), "bottom": y0 >= by1 - band * (by1 - by0),
            "left": x1 <= bx0 + band * (bx1 - bx0), "right": x0 >= bx1 - band * (bx1 - bx0)}[side]


def cut(box, side, line):
    x0, y0, x1, y1 = box
    return {"top": [x0, line, x1, y1], "bottom": [x0, y0, x1, line],
            "left": [line, y0, x1, y1], "right": [x0, y0, line, y1]}[side]


def second_crop(size, parts, subject, faces, offset, *, screenshot, allow_app_bar=True):
    """(box or None, removed parts, notes): trim each side past its edge clutter where the person allows."""
    width, height = size
    guard = max(4, round(min(size) * (.015 if screenshot else .008)))
    margin = max(4, round(min(size) * .01))
    near = clutter.grow(subject["mask"], margin)
    total = max(1, int(near.sum()))
    ox, oy = offset
    keep_to = max((y - oy + BODY_KEEP * h for _, y, _, h in faces), default=height)
    box, removed, notes = [0, 0, width, height], [], []
    for side in ("top", "bottom", "left", "right"):
        taken = {id(item) for item in removed}
        inside = [item for item in parts if id(item) not in taken and within(item, side, box)]
        key = {"top": lambda i: i["box"][3], "bottom": lambda i: -i["box"][1],
               "left": lambda i: i["box"][2], "right": lambda i: -i["box"][0]}[side]
        inside.sort(key=key)
        best = None
        for count in range(1, len(inside) + 1):
            chosen = inside[:count]
            line = {"top": max(i["box"][3] for i in chosen) + guard,
                    "bottom": min(i["box"][1] for i in chosen) - guard,
                    "left": max(i["box"][2] for i in chosen) + guard,
                    "right": min(i["box"][0] for i in chosen) - guard}[side]
            trial = cut(box, side, max(0, min(line, width if side in ("left", "right") else height)))
            kept_w, kept_h = trial[2] - trial[0], trial[3] - trial[1]
            if kept_w <= 0 or kept_h <= 0 or kept_w * kept_h < (1 - MAX_CROP_LOSS) * width * height:
                break
            if not .4 <= kept_w / kept_h <= 2.0:
                break
            lost = (total - int(near[trial[1]:trial[3], trial[0]:trial[2]].sum())) / total
            span = max(i["box"][2] for i in chosen) - min(i["box"][0] for i in chosen)
            app_bar = (allow_app_bar and screenshot and side == "bottom" and trial[3] >= keep_to and lost <= .45
                       and (span >= .5 * width or any(i["kind"] == "ui-card" for i in chosen)))
            if lost > SUBJECT_LOSS and not app_bar:
                break
            best = (trial, chosen, lost, app_bar)
        if best:
            box, chosen, lost, app_bar = best
            removed += chosen
            notes.append(f"{side} {len(chosen)} part(s), person lost {lost:.1%}"
                         + (" (screen-wide app bar below the hips)" if app_bar else ""))
    if box == [0, 0, width, height]:
        return None, [], notes
    return box, removed, notes


def composition_box(size, sbox):
    """Frame the whole person with a small margin, widened toward the 944x1104 shape; None if nothing to gain."""
    width, height = size
    x0, y0, x1, y1 = sbox
    w, h = x1 - x0, y1 - y0
    pad_x, pad_top, pad_bottom = max(12, .06 * w), max(12, .04 * h), max(12, .03 * h)
    left, top, right, bottom = x0 - pad_x, y0 - pad_top, x1 + pad_x, y1 + pad_bottom
    bw, bh = right - left, bottom - top
    if bw / bh < TARGET:
        grow_w = (bh * TARGET - bw) / 2
        left, right = left - grow_w, right + grow_w
    else:
        grow_h = (bw / TARGET - bh) / 2
        top, bottom = top - grow_h, bottom + grow_h
    left, right = shift(left, right, width)
    top, bottom = shift(top, bottom, height)
    box = [int(round(left)), int(round(top)), int(round(right)), int(round(bottom))]
    if (box[2] - box[0]) * (box[3] - box[1]) >= .92 * width * height:
        return None
    return box


def cut_off_below(mask):
    """True when the person mask stops wide (legs it lost track of) rather than tapering to feet."""
    rows = np.nonzero(mask.any(axis=1))[0]
    if not len(rows):
        return False
    bottom = int(rows.max()) + 1
    band = mask[max(0, bottom - max(3, mask.shape[0] // 300)):bottom]
    widest = max(1, int(mask.sum(axis=1).max()))
    return int(band.any(axis=0).sum()) > LIMB_WIDTH * widest


def shift(low, high, limit):
    """Slide a span inside [0, limit] (keeping its length when it fits), then clip."""
    if low < 0:
        high, low = high - low, 0
    if high > limit:
        low, high = low - (high - limit), limit
    return max(0, low), min(limit, high)


def describe(items, offset=(0, 0)):
    ox, oy = offset
    return [{"kind": i["kind"], "box": [i["box"][0] - ox, i["box"][1] - oy, i["box"][2] - ox, i["box"][3] - oy],
             "action": i.get("action", "kept")} for i in items]


def processing_candidates(image, row):
    """Yield (variant name, image) in trace order and record the v16 trace on `row`."""
    step = geometry.step
    geo = row["geometry"]
    faces = row["eligibility"]["faces"]
    assessment = row["eligibility"]["reason"]
    base = tuple(geo["box"])
    screenshot = geo["overlayDetected"]
    if screenshot:
        box, reason = geometry.panel_box(image, faces, base)
        geo.update(box=list(box), changed=box != (0, 0, *image.size),
                   method="reel-panels-and-solid-border-v2", reason=geo["reason"] + " " + reason)
    else:
        box = base
    selected = "geometry" if geo["changed"] else "control"
    prepared = image.crop(box)
    offset = box[:2]
    trace = [step("first-crop", "attempted-selected" if geo["changed"] else "skipped",
                  "control", "geometry" if geo["changed"] else None, selected, geo["reason"])]
    processing = row["processing"] = {"steps": trace, "cleanup": selected, "final": selected,
                                      "faceAssessment": assessment}
    yield "control", image
    yield "geometry", prepared
    if geo["uiCropBox"]:
        yield "ui-crop-proposal", image.crop(geo["uiCropBox"])

    person, method, person_note = find_subject(prepared, faces, offset)
    processing["subject"] = {"method": method, "box": person["box"] if person else None,
                             "people": person["people"] if person else 0, "note": person_note}
    if person is None:
        for name in ("second-crop", "eraser", "composition"):
            trace.append(step(name, "skipped", selected, None, selected, person_note))
        processing["clutter"] = []
        return
    try:
        parts, refused = clutter.detect(prepared, faces, offset, person, screenshot=screenshot)
    except cv2.error as exc:
        parts, refused = [], []
        person_note += f" Clutter detection failed: {exc}."
    for item in refused:
        item["action"] = "refused-face"

    # Second crop: before any fill, so nothing a crop can remove is ever repainted.
    frame, removed, notes = second_crop(prepared.size, parts, person, faces, offset, screenshot=screenshot)
    current, origin = prepared, (0, 0)
    if frame:
        for item in removed:
            item["action"] = "cropped"
        current, origin = prepared.crop(frame), tuple(frame[:2])
        trace.append(step("second-crop", "attempted-selected", selected, "second-crop", "second-crop",
                          f"Trimmed {list(frame)} of the first crop: " + "; ".join(notes)
                          + ". A pure crop: no pixels invented; the person and a margin are kept."))
        selected = "second-crop"
        yield "second-crop", current
    else:
        trace.append(step("second-crop", "skipped", selected, None, selected,
                          "No side can be trimmed past its clutter without cutting the person"
                          + (" (" + "; ".join(notes) + ")" if notes else "") + "." if parts else
                          "No clutter found near the edges; a miss is not proof the image is clean."))

    # Eraser: LaMa repaints what is left, on the image the crop produced.
    x0, y0 = origin
    x1, y1 = x0 + current.width, y0 + current.height
    mask = np.zeros((current.height, current.width), dtype=bool)
    body = person["mask"][y0:y1, x0:x1]
    for item in parts:
        if item.get("action") == "cropped":
            continue
        piece = item["mask"][y0:y1, x0:x1]
        if not piece.any():
            item["action"] = "cropped"
            continue
        if item["kind"] == "ui-card" and (piece & body).sum() > CARD_ON_BODY * piece.sum():
            item["action"] = "refused-body"
            continue
        item["action"] = "filled"
        mask |= piece
    coverage = float(mask.mean())
    filled = [i for i in parts if i.get("action") == "filled"]
    if not filled:
        trace.append(step("eraser", "skipped", selected, None, selected,
                          "Nothing left to repaint after the crops." if parts else
                          "No clutter detected; a miss is not proof the image is clean."))
    elif coverage > MAX_FILL:
        for item in filled:
            item["action"] = "kept"
        trace.append(step("eraser", "skipped", selected, None, selected,
                          f"Clutter covers {coverage:.1%} of the image (over {MAX_FILL:.0%}); not repainted."))
    else:
        try:
            erased = fill.fill(current, mask)
        except (OSError, RuntimeError, cv2.error) as exc:
            for item in filled:
                item["action"] = "kept"
            trace.append(step("eraser", "failed", selected, None, selected,
                              f"LaMa fill failed; the last crop is kept: {exc}"))
        else:
            kinds = sorted({i["kind"] for i in filled})
            yield "eraser-mask", mask_image(mask)
            yield "eraser", erased
            trace.append(step("eraser", "attempted-selected", selected, "eraser", "eraser",
                              f"LaMa repainted {len(filled)} clutter shape(s) ({', '.join(kinds)}), "
                              f"{coverage:.2%} of the image; face boxes are never repainted. "
                              "Repainted areas are plausible, not recovered; compare with the original."))
            selected, current = "eraser", erased
    processing["clutter"] = describe(parts + refused)

    # Composition: frame the person (whole body, hands, dress) for the downstream 944x1104 shape.
    if method != "mask-rcnn":
        trace.append(step("composition", "skipped", selected, None, selected,
                          "No person mask, so no framing crop; " + person_note))
    else:
        sbox = [person["box"][0] - x0, person["box"][1] - y0, person["box"][2] - x0, person["box"][3] - y0]
        sbox = [max(0, sbox[0]), max(0, sbox[1]), min(current.width, sbox[2]), min(current.height, sbox[3])]
        limbs = sbox[3] < current.height and cut_off_below(person["mask"])
        if limbs:
            sbox[3] = current.height
        frame = composition_box(current.size, sbox)
        if frame is None:
            trace.append(step("composition", "skipped", selected, None, selected,
                              "The person already fills the picture; nothing to trim."))
        else:
            trace.append(step("composition", "attempted-selected", selected, "composition", "composition",
                              f"Framed the person {sbox} with a small margin, widened toward 944x1104: {frame}. "
                              + ("The person mask ends mid-limb, so the bottom is kept to the frame edge. " if limbs
                                 else "") + "Pure crop of the cleaned image."))
            selected = "composition"
            yield "composition", current.crop(frame)
    processing.update(cleanup=selected, final=selected)


def mask_image(mask):
    return Image.fromarray((mask * 255).astype(np.uint8)).convert("RGB")


def overlay_proposals(array):
    parts = []
    for item in overlays.badges(array):
        circle = item["confirmation"]["circle"]
        parts.append({"kind": "confirmed-badge", "box": item["box"], "pattern": item["confirmation"]["badge"],
                      "circle": [circle[0], circle[1],
                                 round(circle[2] * 1.12 + min(array.shape[:2]) * .004, 1)]})
    parts.extend(dict({"kind": item["kind"], "box": item["box"], "pattern": item["pattern"]},
                      **({"polygon": item["polygon"]} if item.get("polygon") else {}))
                 for item in overlays.watermarks(array) + overlays.sparkles(array)
                 + overlays.tilted_stickers(array) + overlays.viewer_icons(array)
                 + overlays.references(array))
    return parts


def recommended_candidates(image, row):
    """Run the proven sequence once; retain its full source-coordinate evidence per photo."""
    from intake_library import reconstruction

    images = {}
    for name, output in experimental_candidates(image, row, overlay_first=True):
        images[name] = output
        yield name, output
    evidence = row["experiment"]
    for name, output in reconstruction.integrated_head_candidates(
            images[evidence["final"]], row, image, images.get("eraser-mask")):
        images[name] = output
        yield name, output
    head = evidence.get("headOverlay", {})
    if head.get("selected"):
        head.update(status="selected", likenessEligible=True,
                    reason="Approved prepared source for Gallery, likeness and ComfyUI; "
                           "masked pixels are synthetic, exact original and masks retained.")
    selected = "control"
    trace = []
    stages = (
        ("first-crop", "first-crop"),
        ("eraser", "eraser"),
        ("residual-crop", "residual-crop"),
        ("reconstruction", "head-overlay-reconstruction"),
        ("composition", "head-overlay-composition"),
    )
    final = evidence["final"]
    ancestors = set()
    current = final
    while current is not None:
        ancestors.add(current)
        current = evidence["candidates"][current]["input"]
    for stage, name in stages:
        record = evidence["candidates"].get(name)
        used = name in ancestors
        reason = (record.get("reason") or "Selected verified prepared sequence output.") if record else (
            "No accepted candidate; retain preceding prepared pixels. See sequence evidence.")
        if stage == "reconstruction":
            reason = head.get("reason", reason)
        trace.append(geometry.step(stage, "attempted-selected" if used else
                                   "attempted-rejected" if record else "skipped",
                                   selected, name if record else None, name if used else selected, reason))
        if used:
            selected = name
    if selected != final:
        raise ValueError("prepared sequence final is absent from the processing trace")
    row["processing"] = {
        "steps": trace, "cleanup": final, "final": final,
        "faceAssessment": row["eligibility"]["reason"], "sequence": row.pop("experiment"),
    }


def experimental_candidates(image, row, *, overlay_first=False):
    """Yield named PIL candidates; only row['experiment'] is written, never the frozen v16 evidence.

    Exhaust the generator before reading final evidence. Boxes are xyxy; candidate boxes are in their
    input's coordinates, sourceBox is in original coordinates. Mask images are diagnostic, never selected.
    Composition proposals are emitted for comparison only; final retains the precomposition image.
    No face/person model is rerun; at most one post-fill clutter detection and no second fill are allowed.
    """
    import time

    started = time.perf_counter()
    faces = row["eligibility"]["faces"]
    evidence = row["experiment"] = {
        "policy": EXPERIMENT_POLICY, "steps": [], "candidates": {}, "final": "control",
        "detectorErrors": [], "detections": [], "redetections": 0,
        "fillCoverage": None, "subject": None,
        "faceAssessment": row["eligibility"]["reason"],
        "limitations": ["Heuristic masks do not establish overlay identity or garment safety.",
                        "A detector miss is not proof of clean pixels or complete subject coverage.",
                        "Fill synthesizes plausible content, not recovered hidden pixels."],
    }
    current, selected = image, "control"
    source_box = [0, 0, *image.size]
    original_near = None
    protected = np.zeros((image.height, image.width), dtype=bool)
    for box in clutter.face_boxes(faces, (0, 0), image.size):
        protected |= clutter.solid(protected.shape, box)

    def candidate(name, output, parent, box=None, diagnostic=False, comparison_only=False):
        evidence["candidates"][name] = {
            "input": parent, "size": list(output.size), "sourceBox": list(source_box),
            "box": box, "diagnostic": diagnostic,
            "status": "comparison" if diagnostic or comparison_only else "selected",
        }
        if not diagnostic and not comparison_only:
            if parent in evidence["candidates"]:
                evidence["candidates"][parent]["status"] = "comparison"
            evidence["final"] = name

    def record(name, status, reason, *, box=None, loss=None, output=None):
        entry = geometry.step(name, status, selected, output, output or selected, reason)
        entry.update(inputSize=list(current.size), inputSourceBox=list(source_box),
                     candidateBox=box, subjectLoss=loss,
                     elapsedSeconds=time.perf_counter() - started)
        evidence["steps"].append(entry)

    def crop_guard(box):
        absolute = [box[0] + source_box[0], box[1] + source_box[1],
                    box[2] + source_box[0], box[3] + source_box[1]]
        if not (0 <= box[0] < box[2] <= current.width and 0 <= box[1] < box[3] <= current.height):
            return False, None, "Invalid or out-of-bounds crop."
        x0, y0, x1, y1 = absolute
        if int(protected[y0:y1, x0:x1].sum()) != int(protected.sum()):
            return False, None, "Crop would remove a guarded face or refused region."
        if original_near is None:
            return False, None, "Subject coverage unknown; keep pixels unchanged."
        total = max(1, int(original_near.sum()))
        assessed = original_near
        layout = evidence.get("screenshotLayout")
        if layout:
            px0, py0, px1, py1 = layout["pictureBox"]
            assessed = original_near.copy()
            assessed[:py0] = False
            assessed[py1:] = False
            total = max(1, int(assessed.sum()))
        loss = (total - int(assessed[y0:y1, x0:x1].sum())) / total
        return loss <= SUBJECT_LOSS, loss, (
            f"Cumulative grown-subject loss {loss:.4%}; limit {SUBJECT_LOSS:.1%}; no app-bar exception.")

    def select_crop(name, box):
        nonlocal current, selected, source_box
        allowed, loss, reason = crop_guard(box)
        record(name, "attempted-selected" if allowed else "refused", reason,
               box=list(box), loss=loss, output=name if allowed else None)
        if not allowed:
            return False
        parent = selected
        current = current.crop(box)
        source_box = [source_box[0] + box[0], source_box[1] + box[1],
                      source_box[0] + box[2], source_box[1] + box[3]]
        selected = name
        candidate(name, current, parent, list(box))
        return True

    candidate("control", image, None)
    yield "control", image
    if row["eligibility"].get("status", "usable") != "usable" or not faces:
        if row["eligibility"].get("status") == "assessment-failed":
            evidence["detectorErrors"].append({
                "stage": "assessment", "detector": "face", "type": "assessment-failed",
                "message": row["eligibility"]["reason"]})
        for name in ("first-crop", "eraser", "residual-crop", "composition"):
            record(name, "skipped", "Face assessment does not authorize preparation.")
        evidence["stopReason"] = "Face assessment unavailable or ineligible."
        evidence["elapsedSeconds"] = time.perf_counter() - started
        return

    geo = row["geometry"]
    first = tuple(geometry.border_box(image))
    array = np.asarray(image)
    reel = overlays.reel_frame(array)
    if reel:
        evidence["overlayFrame"] = {key: reel.get(key) for key in ("profile", "layout", "pictureBox", "uiBottom", "statusBand")}
    else:
        bars = overlays.letterbox(array)
        if bars and all(bars[0] <= fy and fy + fh <= bars[1] for fx, fy, fw, fh in faces):
            first = (first[0], max(first[1], bars[0]), first[2], min(first[3], bars[1]))
            evidence["letterbox"] = {"pattern": "letterbox", "rows": list(bars)}
    patterns = overlay_proposals(array) if overlay_first else None
    if overlay_first:
        needs_subject = bool(
            geo.get("overlayDetected") or reel or first != (0, 0, *image.size) or patterns
        )
        glyphs = [] if needs_subject else clutter.glyphs(array, None, screenshot=False)
        needs_subject = needs_subject or bool(glyphs)
        evidence["preflight"] = {
            "status": "proposals" if needs_subject else "no-proposals",
            "patternCount": len(patterns), "glyphCount": len(glyphs),
            "subjectRequired": needs_subject,
            "reason": "Body-independent patterns and border/UI proposals precede subject protection; "
                      "a detection miss is not proof of clean pixels.",
        }
        if not needs_subject:
            reason = ("No detected overlay, border or UI proposal; retain unassessed pixels. "
                      "Subject segmentation and composition-only suggestions skipped.")
            evidence["subject"] = {"method": "not-requested", "box": None, "note": reason}
            evidence["overlayParts"] = []
            for name in ("first-crop", "eraser", "residual-crop", "composition"):
                record(name, "skipped", reason)
            evidence["stopReason"] = reason
            evidence["elapsedSeconds"] = time.perf_counter() - started
            return
    person, method, note = find_subject(image, faces, (0, 0), detector_errors=evidence["detectorErrors"])
    evidence["subject"] = {"method": method, "box": person["box"] if person else None, "note": note}
    if person is not None and method == "mask-rcnn":
        original_near = clutter.grow(person["mask"], max(4, round(min(image.size) * .01)))
    overlay_parts = []
    if geo.get("overlayDetected") or reel:
        panel, panel_note = geometry.panel_box(image, faces, first)
        evidence["panelAssessment"] = (
            "Panel proposal comparison-only before erase: face margins and incomplete person masks "
            "cannot prove hair/body preservation. " + panel_note)
        evidence["panelProposal"] = list(panel)
        picture = reel["pictureBox"] if reel else geometry.screenshot_picture_box(image)
        if picture and original_near is not None:
            pills = clutter.bubbles(np.asarray(image))
            top = min([picture[1]] + [max(0, p["box"][1] - 4) for p in pills])
            bottom = max([picture[3]] + [min(image.height, p["box"][3] + 4) for p in pills])
            proposed = [picture[0], top, picture[2], bottom]
            # Avatar thumbnails on the reel's own UI panel are not subject faces.
            subject_faces = [face for face in faces
                             if not (reel and face[1] + face[3] / 2 >= picture[3])]
            if all(proposed[0] <= fx and proposed[1] <= fy
                   and fx + fw <= proposed[2] and fy + fh <= proposed[3]
                   for fx, fy, fw, fh in subject_faces):
                evidence["screenshotLayout"] = {
                    "pictureBox": picture, "initialBox": proposed,
                    "reason": "Paired side-strip picture/black-panel transitions; retain complete pill "
                              "before fill. Only observed external panels excluded from subject budget."}
                if reel:
                    evidence["screenshotLayout"]["reason"] = (
                        f"{reel['profile']} frame anchored on bottom UI rows; retain complete pill before fill. "
                        "Only observed external panels excluded from subject budget.")
                caption_boxes = []
                cropped = np.asarray(image.crop(proposed))
                for item in clutter.glyphs(cropped, None, screenshot=True):
                    ix0, iy0, ix1, iy1 = item["box"]
                    ix0, ix1 = ix0 + proposed[0], ix1 + proposed[0]
                    iy0, iy1 = iy0 + proposed[1], iy1 + proposed[1]
                    rail = ix0 >= .87 * image.width
                    caption = iy0 >= picture[1] + .88 * (picture[3] - picture[1])
                    back = ix1 <= .15 * image.width and iy1 <= picture[1] + .06 * image.height
                    if (rail or caption or back) and iy1 > picture[1] and iy0 < picture[3]:
                        if rail:
                            middle = (iy0 + iy1) / 2
                            half = max((iy1 - iy0) / 2, image.width * .055)
                            overlay_parts.append({
                                "kind": "rendered-screenshot-rail",
                                "box": [int(image.width * .88), max(picture[1], int(middle - half)),
                                        int(image.width * .98), min(picture[3], int(middle + half))]})
                        elif caption:
                            caption_boxes.append([ix0, iy0, ix1, iy1])
                        else:
                            overlay_parts.append({"kind": "rendered-screenshot-ui",
                                                  "box": [0, max(top, picture[1] - int(image.width * .05)),
                                                          int(image.width * .11),
                                                          min(picture[3], picture[1] +
                                                              int(image.width * .07))]})
                if caption_boxes:
                    overlay_parts.append({
                        "kind": "rendered-screenshot-caption",
                        "box": [min(b[0] for b in caption_boxes), min(b[1] for b in caption_boxes),
                                max(b[2] for b in caption_boxes), max(b[3] for b in caption_boxes)]})
                if reel:
                    # The profile's zone parts replace the generic glyph heuristics above.
                    overlay_parts = [dict(item, pattern=reel["profile"])
                                     for item in overlays.frame_parts(array, reel, faces=faces)]
                evidence["screenshotLayout"]["overlayParts"] = overlay_parts
                first = tuple(proposed)
    overlay_parts.extend(patterns if patterns is not None else overlay_proposals(array))
    evidence["overlayParts"] = overlay_parts
    if first != (0, 0, *image.size):
        if select_crop("first-crop", first):
            yield "first-crop", current
    else:
        record("first-crop", "skipped",
               "No confidently separable solid border; preserve all sides for overlay erasing.", loss=0.0)
    if original_near is None:
        for name in ("eraser", "residual-crop", "composition"):
            record(name, "skipped", "Person mask unavailable; uncertain body coverage is kept unchanged.")
        evidence["stopReason"] = "No reliable person mask."
        evidence["elapsedSeconds"] = time.perf_counter() - started
        return

    x0, y0, x1, y1 = source_box
    body = person["mask"][y0:y1, x0:x1]
    local_person = dict(person, mask=body, box=[
        max(0, person["box"][0] - x0), max(0, person["box"][1] - y0),
        min(current.width, person["box"][2] - x0), min(current.height, person["box"][3] - y0)])

    def detect(stage):
        try:
            parts, refused = clutter.detect(current, faces, (x0, y0), local_person,
                                            screenshot=geo.get("overlayDetected", False), logos="badges")
        except (OSError, RuntimeError, ValueError, cv2.error) as exc:
            evidence["detectorErrors"].append({"stage": stage, "detector": "clutter",
                                               "type": type(exc).__name__, "message": str(exc)})
            return [], [], False
        # Copy detector-owned dictionaries; actions belong only to this experiment.
        return [dict(i) for i in parts], [dict(i) for i in refused], True

    def guard_parts(parts, refused, stage):
        mask = np.zeros(body.shape, dtype=bool)
        for item in refused:
            item["action"] = "refused-face"
        guards = protected[y0:y1, x0:x1]
        for item in parts:
            piece = item["mask"]
            if item.get("action", "").startswith("refused") or item["kind"] not in {
                    "glyph", "logo", "search-bubble", "ui-card"}:
                item["action"] = "refused-uncertain"
            elif item["kind"] == "glyph" and not (geo.get("overlayDetected") or reel):
                item["action"] = "refused-unconfirmed-glyph"
            elif (piece & guards).any():
                item["action"] = "refused-face-or-region"
            elif (piece & body).any():
                item["action"] = "refused-body"
            else:
                item["action"] = "candidate"
                mask |= piece
        for item in parts + refused:
            if item["action"].startswith("refused"):
                guards |= item["mask"]
        mask &= ~guards
        evidence["detections"].append({
            "stage": stage, "input": selected, "sourceBox": list(source_box),
            "parts": [dict(kind=i["kind"], box=list(i["box"]), action=i["action"],
                           reason=i.get("reason", ""), maskPixels=int(i["mask"].sum()))
                      for i in parts + refused]})
        return mask

    parts, refused, detected = detect("initial")
    mask = guard_parts(parts, refused, "initial")
    coverage = float(mask.mean())
    evidence["fillCoverage"] = coverage
    filled = False
    if not mask.any():
        record("eraser", "skipped", "No accepted clutter mask; misses/refusals do not establish clean pixels.")
    else:
        candidate("eraser-mask", mask_image(mask), selected, diagnostic=True)
        yield "eraser-mask", mask_image(mask)
        if coverage > MAX_FILL:
            record("eraser", "refused", f"Mask coverage {coverage:.2%} exceeds {MAX_FILL:.0%}.")
        else:
            try:
                erased = fill.fill(current, mask)
                if erased.size != current.size:
                    raise ValueError("Fill changed image dimensions.")
                # Enforce unchanged pixels outside the accepted mask, even for an imperfect filler.
                pixels = np.asarray(current).copy()
                pixels[mask] = np.asarray(erased)[mask]
                erased = Image.fromarray(pixels)
            except (OSError, RuntimeError, ValueError, cv2.error) as exc:
                record("eraser", "failed", f"Fill failed; input retained: {type(exc).__name__}: {exc}")
            else:
                record("eraser", "attempted-selected",
                       f"Accepted mask filled ({coverage:.2%}); refused regions unchanged.", output="eraser")
                parent, selected, current = selected, "eraser", erased
                candidate(selected, current, parent)
                filled = True
                yield selected, current

    if filled:
        evidence["redetections"] = 1
        parts, refused, detected = detect("post-fill")
        guard_parts(parts, refused, "post-fill")
    if detected and not evidence.get("screenshotLayout"):
        safe_parts = [i for i in parts if not i["action"].startswith("refused")]
        frame, _, notes = second_crop(current.size, safe_parts, local_person, faces, (x0, y0),
                                       screenshot=geo.get("overlayDetected", False), allow_app_bar=False)
        if frame:
            if select_crop("residual-crop", frame):
                yield "residual-crop", current
        elif evidence.get("screenshotLayout"):
            record("residual-crop", "skipped",
                   "Picture boundary retained; remaining on-picture UI needs erase, not body cropping.")
        else:
            record("residual-crop", "skipped",
                   "No residual edge crop passes the strict subject/area guards; no second fill. "
                   + "; ".join(notes))
    else:
        record("residual-crop", "skipped", "Clutter detector failed; residual state unknown.")

    sx, sy, ex, ey = source_box
    sbox = [max(0, person["box"][0] - sx), max(0, person["box"][1] - sy),
            min(current.width, person["box"][2] - sx), min(current.height, person["box"][3] - sy)]
    if sbox[3] < current.height and cut_off_below(person["mask"]):
        sbox[3] = current.height
    frame = composition_box(current.size, sbox) if not evidence.get("screenshotLayout") else None
    if frame:
        _, loss, guard_reason = crop_guard(frame)
        reason = ("Missing hair/feet completeness proof: a segmentation mask can omit visible extremities "
                  "even when calculated subject loss is zero. Composition is comparison-only; "
                  "the precomposition cleaned image remains selected. " + guard_reason)
        record("composition", "attempted-rejected", reason, box=list(frame), loss=loss)
        evidence["steps"][-1]["candidate"] = "composition"
        proposed = current.crop(frame)
        candidate("composition", proposed, selected, list(frame), comparison_only=True)
        evidence["candidates"]["composition"].update(
            sourceBox=[sx + frame[0], sy + frame[1], sx + frame[2], sy + frame[3]],
            reason=reason)
        yield "composition", proposed
    else:
        record("composition", "skipped", "Screenshot picture framing deferred until reconstruction."
               if evidence.get("screenshotLayout") else "No useful composition crop.")
    evidence["stopReason"] = ("One post-fill detection completed; no further detection or fill permitted."
                              if filled else "No successful fill; no redetection or further fill permitted.")
    evidence["elapsedSeconds"] = time.perf_counter() - started
