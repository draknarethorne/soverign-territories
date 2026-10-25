"""Recipe v16 intake steps: first crop -> second crop -> eraser -> composition.

The second crop runs before the eraser and may trim every side, but only where it costs (almost) no part of the
person; whatever clutter is left inside is filled by LaMa, and that fill is kept. Composition then frames the
person (whole body, hands and dress included) for the 944x1104 derivatives. Denoise and tone are compared later.
"""
import cv2
import numpy as np
from PIL import Image

import preparation_geometry as geometry
from intake_library import clutter, fill, subject as subjects

STEPS = ("first-crop", "second-crop", "eraser", "composition", "denoise", "tone")
BANDS = {"top": .25, "bottom": .4, "left": .3, "right": .3}
MAX_CROP_LOSS = .5      # the second crop keeps at least half the image
SUBJECT_LOSS = .005     # ... and at most 0.5% of the person plus a margin
BODY_KEEP = 4.5         # bottom app UI may cut legs only below 4.5 face heights under the face top
MAX_FILL = .2           # never repaint more than a fifth of the picture
CARD_ON_BODY = .25      # a card lying this much on the person is not repainted (it would invent the body)
TARGET = 944 / 1104
LIMB_WIDTH = .2         # a mask ending wider than this share of its widest row was cut off mid-leg, not at the feet


def find_subject(image, faces, offset):
    """(subject, method, note): Mask R-CNN people, else a body frame around the faces."""
    try:
        found = subjects.detect(image)
    except (OSError, RuntimeError, ValueError) as exc:
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


def second_crop(size, parts, subject, faces, offset, *, screenshot):
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
            app_bar = (screenshot and side == "bottom" and trial[3] >= keep_to and lost <= .45
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
