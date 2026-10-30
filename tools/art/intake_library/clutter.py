"""Where the clutter is: app chrome, icons, counters, captions, ad cards and corner logos laid over a photo.

Every part is a complete filled shape (not just its strokes) so the fill cannot rebuild it from leftovers.
Detection is heuristic; a miss is not proof that an image is clean.
"""
import cv2
import numpy as np

EDGE = .2          # glyphs and logos are looked for in the outer 20% on each side
BOTTOM_EDGE = .3   # captions and counters reach higher at the bottom
GROW = .008        # complete-shape margin, as a share of the smaller image side
FACE_GUARD = .02


def rgb_bounds(array):
    red, green, blue = array[..., 0], array[..., 1], array[..., 2]
    return (np.minimum(np.minimum(red, green), blue).astype(np.int16),
            np.maximum(np.maximum(red, green), blue).astype(np.int16))


def part(kind, mask, reason=""):
    ys, xs = np.nonzero(mask)
    return {"kind": kind, "mask": mask, "reason": reason,
            "box": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]}


def solid(shape, box):
    mask = np.zeros(shape, dtype=bool)
    x0, y0, x1, y1 = box
    mask[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
    return mask


def grow(mask, pixels):
    size = max(3, pixels * 2 + 1)
    return cv2.dilate(mask.astype(np.uint8), np.ones((size, size), np.uint8)) > 0


def fill_holes(mask):
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros(mask.shape, dtype=np.uint8)
    cv2.drawContours(filled, contours, -1, 1, thickness=cv2.FILLED)
    return filled > 0


def edge_region(height, width):
    region = np.zeros((height, width), dtype=bool)
    region[:int(height * EDGE)] = True
    region[int(height * (1 - BOTTOM_EDGE)):] = True
    region[:, :int(width * EDGE)] = True
    region[:, int(width * (1 - EDGE)):] = True
    return region


def glyphs(array, subject, *, screenshot=False):
    """White strokes drawn over the picture (icons, counters, captions), grouped into whole shapes."""
    height, width = array.shape[:2]
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    low, high = rgb_bounds(array)
    white = (low > 215) & (high - low < 30)
    contrast = cv2.dilate((gray < 110).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    strokes = (white & contrast & edge_region(height, width)).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(strokes)
    small = np.zeros_like(strokes)
    for label in range(1, count):
        x, y, w, h, area = map(int, stats[label])
        if 3 <= area <= width * height * .004 and w < width * .15 and h < height * .08:
            small[labels == label] = 1
    join = max(5, round(min(width, height) * .018)) | 1
    grouped = cv2.morphologyEx(small, cv2.MORPH_CLOSE, np.ones((join, join), np.uint8))
    small_mask = small > 0
    count, labels, stats, _ = cv2.connectedComponentsWithStats(grouped)
    parts = []
    for label in range(1, count):
        x, y, w, h, area = map(int, stats[label])
        shape = labels == label
        if (w > width * .5 or h > height * .1 or (w > width * .2 and h > height * .05)
                or int(small_mask[shape].sum()) < 12):
            continue
        chrome = screenshot and (y + h <= height * .12 or y >= height * .85)
        if not chrome and (max(w, h) > 4 * min(w, h) or small_mask[shape].sum() < .08 * w * h):
            continue  # thin lit edges (walls, railings) are scenery; long text lines only count in app chrome
        stroke = array[shape & small_mask].min(axis=1)
        status_bar = screenshot and y + h <= height * .05
        if not status_bar and (stroke >= 245).mean() < .5:
            continue  # app glyphs are rendered pure white; sunlit highlights and lace are not
        rendered = screenshot and (stroke >= 245).mean() >= .8  # app text is drawn pure white, even over the body
        if subject is not None and not rendered and (shape & subject).sum() > .5 * shape.sum():
            continue  # white detail on the person (jewellery, lace, hair) rather than an overlay
        parts.append(part("glyph", fill_holes(shape), "white strokes with dark edges near the border"))
    return parts


def emblems(array):
    """Saturated magenta/pink logo badges in the lower corners (watermark envelopes)."""
    height, width = array.shape[:2]
    hsv = cv2.cvtColor(array, cv2.COLOR_RGB2HSV)
    chroma = ((hsv[:, :, 0] >= 150) & (hsv[:, :, 1] > 120) & (hsv[:, :, 2] > 130)).astype(np.uint8)
    chroma[:int(height * .6)] = 0
    join = max(3, round(min(width, height) * .015)) | 1
    chroma = cv2.dilate(chroma, np.ones((join, join), np.uint8))
    count, _, stats, _ = cv2.connectedComponentsWithStats(chroma)
    parts = []
    for x, y, w, h, area in (map(int, row) for row in stats[1:]):
        # The badge must reach into a corner third; cutting the middle out before labelling clipped wide badges.
        if not (x < width * .35 or x + w > width * .65):
            continue
        if (.06 * width <= w <= .35 * width and .025 * height <= h <= .22 * height
                and .45 <= w / h <= 2.2 and area >= w * h * .06):
            guard = max(2, round(min(width, height) * .012))
            ellipse = np.zeros((height, width), dtype=np.uint8)
            cv2.ellipse(ellipse, ((x + w / 2, y + h / 2), (w + 3 * guard, h + 3 * guard), 0), 1, cv2.FILLED)
            parts.append(part("logo", ellipse > 0, "saturated corner badge"))
    return parts


def bubbles(array):
    """The reel search bubble ("Find related reels") and similar wide pills in the top fifth."""
    height, width = array.shape[:2]
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    boxes = []
    neutral = ((array.max(axis=2).astype(np.int16) - array.min(axis=2) < 25) & (gray >= 45) & (gray <= 170))
    neutral = neutral.astype(np.uint8)
    neutral[int(height * .2):] = 0
    count, _, stats, _ = cv2.connectedComponentsWithStats(neutral)
    for x, y, w, h, area in (map(int, row) for row in stats[1:]):
        if .4 * width <= w <= .95 * width and .012 * height <= h <= .07 * height and w / h >= 5 and area >= w * h * .55:
            boxes.append([x, y, x + w, y + h])
    edges = cv2.Canny(gray[:round(height * .2)], 50, 150)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if (.4 * width <= w <= .95 * width and .012 * height <= h <= .07 * height and w / h >= 5
                and .7 <= cv2.contourArea(contour) / (w * h) <= .98):
            boxes.append([x, y, x + w, y + h])
    merged = []
    for box in boxes:
        for index, other in enumerate(merged):
            if min(box[2], other[2]) > max(box[0], other[0]) and min(box[3], other[3]) > max(box[1], other[1]):
                merged[index] = [min(box[0], other[0]), min(box[1], other[1]),
                                 max(box[2], other[2]), max(box[3], other[3])]
                break
        else:
            merged.append(box)
    guard = max(3, round(min(width, height) * .006))
    return [part("search-bubble", solid((height, width), [b[0] - guard, b[1] - guard, b[2] + guard, b[3] + guard]),
                 "wide rounded pill in the top fifth (reel search bar)") for b in merged]


def long_rows(edges, minimum):
    """(row, start, end) for rows whose longest horizontal edge run is at least `minimum` pixels."""
    found = []
    for row in range(edges.shape[0]):
        line = np.concatenate(([0], (edges[row] > 0).astype(np.int8), [0]))
        changes = np.flatnonzero(np.diff(line))
        if len(changes):
            starts, ends = changes[::2], changes[1::2]
            best = int(np.argmax(ends - starts))
            if ends[best] - starts[best] >= minimum:
                found.append((row, int(starts[best]), int(ends[best])))
    lines = []
    for row, start, end in found:
        if lines and row - lines[-1]["row"] <= 3:
            last = lines[-1]
            last.update(row=row, start=min(last["start"], start), end=max(last["end"], end))
        else:
            lines.append({"first": row, "row": row, "start": start, "end": end})
    return lines


def panels(array):
    """Translucent rounded cards at the bottom of reels: ad cards, 'UP NEXT' bars, the button pill."""
    height, width = array.shape[:2]
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    top = int(height * .55)
    edges = cv2.Canny(cv2.GaussianBlur(gray[top:], (3, 3), 0), 30, 90)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(closed, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if (.55 * width <= w <= width and .03 * height <= h <= .2 * height
                and cv2.contourArea(contour) >= .75 * w * h):
            boxes.append([x, y + top, x + w, y + h + top])
    # A card whose outline touches background edges is not one closed contour: pair its long top/bottom lines.
    lines = long_rows(cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((1, 9), np.uint8)), .5 * width)
    used = set()
    for i, upper in enumerate(lines):
        if i in used:
            continue
        for j in range(i + 1, len(lines)):
            lower = lines[j]
            gap = lower["first"] - upper["row"]
            overlap = min(upper["end"], lower["end"]) - max(upper["start"], lower["start"])
            if gap > .2 * height:
                break
            if gap >= .03 * height and overlap >= .85 * min(upper["end"] - upper["start"], lower["end"] - lower["start"]):
                boxes.append([min(upper["start"], lower["start"]), upper["first"] + top,
                              max(upper["end"], lower["end"]), lower["row"] + 1 + top])
                used.update((i, j))
                break
    boxes.sort(key=lambda b: -(b[2] - b[0]) * (b[3] - b[1]))
    kept = []
    for box in boxes:
        if not any(box[0] >= k[0] - 6 and box[1] >= k[1] - 6 and box[2] <= k[2] + 6 and box[3] <= k[3] + 6 for k in kept):
            kept.append(box)
    guard = max(3, round(min(width, height) * .006))
    return [part("ui-card", solid((height, width), [b[0] - guard, b[1] - guard, b[2] + guard, b[3] + guard]),
                 "rounded card in the lower half (ad, up-next bar, button pill)") for b in kept]


def face_boxes(faces, offset, size):
    width, height = size
    ox, oy = offset
    boxes = []
    for x, y, w, h in faces:
        gx, gy = max(2, FACE_GUARD * w), max(2, FACE_GUARD * h)
        boxes.append([int(x - gx - ox), int(y - gy - oy), int(x + w + gx - ox) + 1, int(y + h + gy - oy) + 1])
    return boxes


def detect(image, faces, offset, subject=None, *, screenshot=False, logos="emblems"):
    """(parts, refused): complete clutter shapes in `image`; parts touching a face are refused, never filled.

    logos="badges" uses only structure-confirmed badges (overlays.badges) instead of colour-blob emblems.
    """
    array = np.asarray(image)
    height, width = array.shape[:2]
    person = subject["mask"] if subject else None
    if logos == "badges":
        from intake_library import overlays
        marks = overlays.badges(array)
    else:
        marks = emblems(array)
    found = glyphs(array, person, screenshot=screenshot) + marks
    if screenshot:
        found += bubbles(array) + panels(array)
    margin = max(2, round(min(width, height) * GROW))
    guards = face_boxes(faces, offset, image.size)
    parts, refused = [], []
    for item in found:
        mask = grow(item["mask"], margin) if item["kind"] == "glyph" else item["mask"].copy()
        size = int(mask.sum())
        for x0, y0, x1, y1 in guards:
            clip = mask[max(0, y0):max(0, y1), max(0, x0):max(0, x1)]
            if clip.any():
                # A shape that merely touches the face box is clipped there; one covering the face is refused.
                if clip.sum() > .15 * size or clip.sum() > .03 * max(1, (x1 - x0) * (y1 - y0)):
                    size = 0
                    break
                clip[:] = False
        if not size or not mask.any():
            refused.append(part(item["kind"], item["mask"], item["reason"]))
        else:
            parts.append(part(item["kind"], mask, item["reason"]))
    return parts, refused


def union(parts, shape):
    mask = np.zeros(shape, dtype=bool)
    for item in parts:
        mask |= item["mask"]
    return mask
