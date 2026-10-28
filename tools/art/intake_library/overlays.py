"""Reusable overlay patterns: screenshot frames, UI zones and confirmed badges, driven by overlay_profiles.json.

A pattern is data first: new frame layouts or badges are added to the profile file, and only a new kind of
measurement needs code. Every detector returns proposals with boxes in the input's coordinates; callers still
guard faces and decide whether to crop or fill. A miss is not proof of clean pixels.
"""
import functools
import json
import pathlib

import cv2
import numpy as np

from intake_library import clutter

PROFILES = pathlib.Path(__file__).with_name("overlay_profiles.json")


@functools.lru_cache(maxsize=1)
def profiles():
    return json.loads(PROFILES.read_text(encoding="utf-8"))


def runs(flags, gap):
    """[(start, end)] of True runs, bridging False gaps up to `gap` rows."""
    found = []
    for index in np.flatnonzero(flags):
        if found and index - found[-1][1] <= gap:
            found[-1][1] = int(index) + 1
        else:
            found.append([int(index), int(index) + 1])
    return found


def reel_frame(array, profile=None):
    """Picture box of a phone-reel screenshot, or None. Anchored on bottom UI rows, never on dark rows alone."""
    profile = profile or profiles()["frames"][0]
    height, width = array.shape[:2]
    if height / width < profile["minAspect"]:
        return None
    rule = profile["bottom"]
    low, high = array.min(axis=2).astype(np.int16), array.max(axis=2).astype(np.int16)
    dark = (high <= rule["darkMax"]).mean(axis=1)
    grey = ((low >= rule["greyMin"]) & (high - low <= rule["greyChroma"])).mean(axis=1)
    ui = (dark >= rule["uiRowFraction"]) | (grey >= rule["uiRowFraction"])
    if not ui[-max(3, height // 200):].all():
        return None  # no nav bar or panel at the very bottom
    card = ((high <= rule["cardMax"]) & (high - low <= rule["greyChroma"])).mean(axis=1)
    panel = (dark >= rule["panelRowFraction"]) | (grey >= rule["uiRowFraction"]) | (card >= rule["cardRowFraction"])
    gap = round(rule["gapTolerance"] * height)
    start = int(height * rule["searchFrom"])
    bottom_runs = [r for r in runs(panel[start:], gap) if r[1] + start == height]
    if not bottom_runs:
        return None
    bottom = bottom_runs[0][0] + start
    if height - bottom < rule["minHeight"] * height:
        return None
    rule = profile["top"]
    strip = max(2, round(rule["stripWidth"] * width))
    sides = np.concatenate([high[:, :strip], high[:, -strip:]], axis=1)
    side_dark = (sides <= rule["darkMax"]).mean(axis=1) >= rule["stripDarkFraction"]
    top_runs = runs(side_dark[:int(height * rule["maxHeight"]) + gap], round(rule["gapTolerance"] * height))
    top, status = 0, None
    if top_runs and top_runs[0][0] == 0 and top_runs[0][1] >= rule["minHeight"] * height:
        top = min(top_runs[0][1], int(height * rule["maxHeight"]))
        layout = "boxed"
        # The cap guards dark photos; a panel that is black across the full width may run past it.
        while top < height // 4 and dark[top] >= rule["fullDark"]:
            top += 1
        # A boxed picture also ends at black: the caption lines sit on that black, above the comment panel.
        black = side_dark & (dark >= profile["bottom"]["panelRowFraction"])
        edge, run = bottom, 0
        for y in range(bottom - 1, top, -1):
            if black[y]:
                edge, run = y, 0
            else:
                run += 1
                if run > gap:
                    break
        uiBottom = bottom
        bottom = edge if edge - top >= .5 * (bottom - top) else bottom
    else:
        layout = "full-bleed"
        uiBottom = bottom
        status = [0, 0, width, round(profile["statusBand"] * height)]
    return {"profile": profile["id"], "layout": layout, "pictureBox": [0, top, width, bottom],
            "uiBottom": uiBottom, "statusBand": status}


def zones(frame, size, profile=None):
    profile = profile or profiles()["frames"][0]
    width, height = size
    x0, top, x1, bottom = frame["pictureBox"]
    ui_bottom = frame.get("uiBottom", bottom)
    found = {}
    for zone in profile["zones"]:
        anchor = top if zone["from"] == "pictureTop" else ui_bottom
        y0 = max(top, round(anchor + zone["y"][0] * height))
        y1 = max(y0, min(bottom, round(anchor + zone["y"][1] * height)))
        found[zone["kind"]] = [round(zone["x"][0] * width), y0, round(zone["x"][1] * width), y1]
    return found


def rendered(array, region, rule, *, contrast=True, vivid=None):
    """Connected components of pure-white UI strokes inside `region`; by default only with a dark edge nearby.

    `vivid` also accepts a saturated edge (a filled "liked" heart button) as contrast.
    """
    height, width = array.shape[:2]
    low, high = array.min(axis=2).astype(np.int16), array.max(axis=2).astype(np.int16)
    if contrast:
        white = (low >= rule["whiteMin"]) & (high - low <= rule["whiteChroma"])
        gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
        near = max(3, round(width * rule["contrastReach"])) | 1
        edge = gray < rule["darkEdge"]
        if vivid is not None:
            edge |= (high - low) >= vivid
        white &= cv2.dilate(edge.astype(np.uint8), np.ones((near, near), np.uint8)) > 0
    else:
        white = (low >= rule["plainWhiteMin"]) & (high - low <= rule["plainWhiteChroma"])
    x0, y0, x1, y1 = region
    strokes = np.zeros((height, width), dtype=np.uint8)
    strokes[y0:y1, x0:x1] = white[y0:y1, x0:x1]
    count, labels, stats, _ = cv2.connectedComponentsWithStats(strokes)
    found = []
    for label in range(1, count):
        x, y, w, h, area = map(int, stats[label])
        if area >= rule["minArea"] and w <= rule["maxWidth"] * width and h <= rule["maxHeight"] * height:
            found.append([x, y, x + w, y + h])
    return found


def group(boxes, gap_x, gap_y):
    """Merge boxes closer than the gaps into envelopes."""
    merged = [list(box) for box in boxes]
    changed = True
    while changed:
        changed = False
        for i in range(len(merged)):
            for j in range(i + 1, len(merged)):
                a, b = merged[i], merged[j]
                if (a[0] - gap_x <= b[2] and b[0] - gap_x <= a[2]
                        and a[1] - gap_y <= b[3] and b[1] - gap_y <= a[3]):
                    merged[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    del merged[j]
                    changed = True
                    break
            if changed:
                break
    return merged


def pad(box, x, y, size):
    width, height = size
    return [max(0, round(box[0] - x)), max(0, round(box[1] - y)),
            min(width, round(box[2] + x)), min(height, round(box[3] + y))]


def stickers(array, region, rule):
    """Saturated rounded stickers (e.g. an orange "FOLLOW ME") carrying white lettering, near the rail."""
    height, width = array.shape[:2]
    hsv = cv2.cvtColor(array, cv2.COLOR_RGB2HSV)
    x0, y0, x1, y1 = region
    vivid = np.zeros((height, width), dtype=np.uint8)
    vivid[y0:y1, x0:x1] = ((hsv[..., 1] >= rule["saturationMin"]) & (hsv[..., 2] >= rule["valueMin"]))[y0:y1, x0:x1]
    vivid = cv2.morphologyEx(vivid, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    white = array.min(axis=2) >= 225
    count, _, stats, _ = cv2.connectedComponentsWithStats(vivid)
    found = []
    for x, y, w, h, area in (map(int, row) for row in stats[1:]):
        inside = float(white[y:y + h, x:x + w].mean()) if w and h else 0.0
        if (rule["width"][0] * width <= w <= rule["width"][1] * width
                and rule["minHeight"] * height <= h <= rule["maxHeight"] * height
                and area >= rule["fill"] * w * h and inside >= rule["letterShare"]):
            found.append([x, y, x + w, y + h])
    return found


def sliders(array, region, rule):
    """Tall translucent grey capsules (volume/more sliders) beside the rail: smooth, low chroma, vertical."""
    height, width = array.shape[:2]
    low, high = array.min(axis=2).astype(np.int16), array.max(axis=2).astype(np.int16)
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    smooth = cv2.blur(np.abs(cv2.Laplacian(gray, cv2.CV_16S)).astype(np.float32), (9, 9)) <= rule["textureMax"]
    flat = (high - low <= rule["chromaMax"]) & (gray >= rule["grayRange"][0]) & (gray <= rule["grayRange"][1])
    x0, y0, x1, y1 = region
    capsule = np.zeros((height, width), dtype=np.uint8)
    capsule[y0:y1, x0:x1] = (flat & smooth)[y0:y1, x0:x1]
    capsule = cv2.morphologyEx(capsule, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    count, _, stats, _ = cv2.connectedComponentsWithStats(capsule)
    found = []
    for x, y, w, h, area in (map(int, row) for row in stats[1:]):
        if (rule["width"][0] * width <= w <= rule["width"][1] * width and h >= rule["minHeight"] * height
                and h >= rule["minAspect"] * w and area >= rule["fill"] * w * h
                and x + w <= (1 - rule["edgeMargin"]) * width):
            found.append([x, y, x + w, y + h])
    return found


def frame_parts(array, frame, profile=None):
    """Envelopes of rendered UI inside the picture box, by zone; boxes in input coordinates.

    Lines and icon clusters are boxed separately so legs/feet between captions are not swept into one block.
    """
    profile = profile or profiles()["frames"][0]
    rule = profile["ui"]
    height, width = array.shape[:2]
    size = (width, height)
    area = zones(frame, size, profile)
    edge = rule["pad"] * width
    parts = []
    top = area["reel-top-controls"]
    for item in clutter.bubbles(array):
        x0, y0, x1, y1 = item["box"]
        if y1 <= top[3] + rule["pillReach"] * height:
            span = profile["pillSpan"]
            parts.append({"kind": "reel-search-pill",
                          "box": pad([min(x0, span[0] * width), y0, max(x1, span[1] * width), y1], 0, 0, size)})
            for left, right in profile["pillCompanions"]:
                parts.append({"kind": "reel-pill-companion",
                              "box": pad([left * width, y0, right * width, y1], 0, edge, size)})
    icons = []
    status_end = frame["statusBand"][3] if frame.get("statusBand") else top[1]
    for box in group(rendered(array, top, rule), rule["iconGap"] * width, rule["iconGap"] * width):
        if max(box[2] - box[0], box[3] - box[1]) < rule["iconMinSize"] * width:
            continue  # a lamp or highlight, not a control
        if (box[1] + box[3]) / 2 < status_end:
            continue  # status glyphs are handled with the status band
        if box[2] <= .2 * width or box[0] >= .7 * width:
            icons.append(box)
            parts.append({"kind": "reel-top-icon", "box": pad(box, edge, edge, size)})
    if icons and not any(p["kind"] == "reel-search-pill" for p in parts):
        # back / search / more sit in fixed slots; on a bright sky some of them lose their dark edge
        middle = sorted((b[1] + b[3]) / 2 for b in icons)[len(icons) // 2]
        half = rule["topSlotHalf"] * height
        for left, right in profile["topSlots"]:
            parts.append({"kind": "reel-top-icon",
                          "box": pad([left * width, middle - half, right * width, middle + half], 0, 0, size)})
    if frame.get("statusBand"):
        band = frame["statusBand"]
        for box in group(rendered(array, band, rule, contrast=False), rule["iconGap"] * width, height):
            if box[2] <= rule["statusCentre"][0] * width or box[0] >= rule["statusCentre"][1] * width:
                parts.append({"kind": "reel-status", "box": pad(box, edge, edge, size)})
    rail = area["reel-rail"]
    glyphs = rendered(array, rail, rule, vivid=rule["railVivid"])
    solid = [g for g in glyphs if min(g[2] - g[0], g[3] - g[1]) >= rule["railMinGlyph"] * width]
    for box in group(glyphs, width, rule["railGap"] * height):
        if not any(box[0] <= g[0] and box[1] <= g[1] and g[2] <= box[2] and g[3] <= box[3] for g in solid):
            continue  # only specks: textured background, not rendered icons
        parts.append({"kind": "reel-rail",
                      "box": pad([min(box[0], rule["railLeft"] * width), box[1], rail[2], box[3]], edge, 2 * edge, size)})
    wide = [round(profile["sticker"]["x"] * width), rail[1], width, rail[3]]
    parts.extend({"kind": "reel-sticker", "box": pad(box, edge, edge, size)}
                 for box in stickers(array, wide, profile["sticker"]))
    parts.extend({"kind": "reel-slider", "box": pad(box, edge, edge, size)}
                 for box in sliders(array, [round(profile["slider"]["x"] * width), top[1], width, rail[3]],
                                    profile["slider"]))
    meta = area["reel-meta"]
    lines = text_lines(rendered(array, meta, rule), rule, size)
    for box in lines:
        parts.append({"kind": "reel-meta-line", "box": pad(box, edge, edge, size)})
    named = [box for box in lines if rule["nameStart"][0] * width <= box[0] <= rule["nameStart"][1] * width]
    if named:
        reach = rule["avatarRadius"] * width
        upper = min(b[1] for b in named)
        # the name line can swallow the avatar's own strokes and start left of nameStart; it sits just above
        named += [b for b in lines if b not in named and b[0] <= rule["nameStart"][1] * width
                  and upper - 2 * reach <= b[3] <= upper + rule["lineGap"] * height]
        middle = (min(b[1] for b in named) + max(b[3] for b in named)) / 2
        parts.append({"kind": "reel-avatar",
                      "box": pad([rule["avatarLeft"] * width, middle - reach, rule["avatarRight"] * width,
                                  middle + reach], 0, 0, size)})
    return parts


def text_lines(words, rule, size):
    """Glyph boxes grouped into text lines: wide runs of several glyphs, plus the other pieces on the same row.

    Text runs wide; stone, lace and skin highlights do not. Once a row is confirmed, hashtags, "... more",
    emoji gaps and words split by a leg belong to it.
    """
    width, height = size
    lines, rest = [], []
    for box in group(words, rule["wordGap"] * width, rule["lineGap"] * height):
        inside = [w for w in words if box[0] <= w[0] and box[1] <= w[1] and w[2] <= box[2] and w[3] <= box[3]]
        if len(inside) >= rule["lineMinGlyphs"] and box[2] - box[0] >= rule["lineMinAspect"] * (box[3] - box[1]):
            lines.append(box)
        else:
            rest.append(box)
    reach = rule["rowGap"] * width
    merged = True
    while merged:
        merged = False
        for line in lines:
            for box in sorted(rest + [b for b in lines if b is not line], key=lambda b: abs(b[0] - line[0])):
                overlap = min(line[3], box[3]) - max(line[1], box[1])
                gap = max(box[0] - line[2], line[0] - box[2])
                if overlap >= .5 * min(box[3] - box[1], line[3] - line[1]) and gap <= reach:
                    line[:] = [min(line[0], box[0]), min(line[1], box[1]),
                               max(line[2], box[2]), max(line[3], box[3])]
                    (rest if any(b is box for b in rest) else lines).remove(box)
                    merged = True
                    break
            if merged:
                break
    return lines


def stroke_text(gray, box, rule):
    """Real rendered text: thin bright strokes over their local background, split into several separate glyphs.

    Lace, sky, chrome highlights and ceiling edges pass the glyph grouping but fail here: their bright pixels are
    not thin strokes (white top-hat) or they form one long run instead of letters.
    """
    x0, y0, x1, y1 = box
    height, width = gray.shape
    if y0 <= 0 or x0 <= 0 or y1 >= height or x1 >= width:
        return False
    line = max(1, y1 - y0)
    k = max(5, int(line * .6)) | 1
    pad_ = k
    sy0, sy1, sx0, sx1 = max(0, y0 - pad_), min(height, y1 + pad_), max(0, x0 - pad_), min(width, x1 + pad_)
    hat = cv2.morphologyEx(gray[sy0:sy1, sx0:sx1], cv2.MORPH_TOPHAT, np.ones((k, k), np.uint8))
    hat = hat[y0 - sy0:y1 - sy0, x0 - sx0:x1 - sx0]
    bright = gray[y0:y1, x0:x1] >= rule["brightMin"]
    if not bright.any() or (bright & (hat >= rule["strokeHat"])).sum() / bright.sum() < rule["strokeShare"]:
        return False
    count, _, stats, _ = cv2.connectedComponentsWithStats((hat >= rule["glyphHat"]).astype(np.uint8), 8)
    glyphs = [s for s in stats[1:] if s[3] >= rule["glyphHeight"] * line and s[2] <= rule["glyphWidth"] * (x1 - x0)]
    if len(glyphs) < rule["minGlyphs"]:
        return False
    # Letters share a baseline; carpet pile and foliage highlights do not.
    bottoms = np.array([s[1] + s[3] for s in glyphs])
    on_line = np.abs(bottoms - np.median(bottoms)) <= rule["baseline"] * line
    lefts = sorted(int(s[0]) for s, keep in zip(glyphs, on_line) if keep)
    distinct = sum(1 for a, b in zip([-10 ** 6] + lefts, lefts) if b - a >= 2)
    return distinct >= rule["minGlyphs"]


def caption_block(array, gray, hit, mark, rule):
    """Grow a confirmed corner line into its caption block: centre-aligned stroke lines stacked with it, plus a
    title line directly above once two lines are confirmed. A lone line (a generator mark) stays as it is."""
    block = mark.get("block")
    if not block:
        return hit
    height, width = gray.shape
    size = (width, height)
    line = hit[3] - hit[1]
    region = [max(0, round(hit[0] - block["reachX"] * width)), max(0, round(hit[1] - block["reachUp"] * height)),
              min(width, round(hit[2] + block["reachX"] * width)), min(height, round(hit[3] + line))]
    words = rendered(array, region, rule) + rendered(array, region, rule, contrast=False)
    lines = text_lines([list(w) for w in {tuple(w) for w in words}], rule, size)
    centre = (hit[0] + hit[2]) / 2

    def aligned(box):
        return abs((box[0] + box[2]) / 2 - centre) <= block["align"] * width

    box, confirmed = list(hit), 1
    grown = True
    while grown:
        grown = False
        for other in sorted(lines, key=lambda b: -b[3]):
            if other[1] >= box[1] or not aligned(other) or box[1] - other[3] > block["lineGap"] * line:
                continue
            if (other[3] - other[1] <= mark["maxLineHeight"] * height
                    and stroke_text(gray, other, mark["stroke"])):
                confirmed += 1
            elif not (confirmed >= 2 and other[3] - other[1] <= block["titleHeight"] * line):
                continue
            box = [min(box[0], other[0]), other[1], max(box[2], other[2]), box[3]]
            grown = True
            break
    return box if confirmed >= 2 else list(hit)


def watermarks(array):
    """Short white text lines (e.g. "Dola AI") in the image corners, on any image; filled boxes per line."""
    height, width = array.shape[:2]
    size = (width, height)
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    found = []
    for mark in profiles()["watermarks"]:
        rule = dict(profiles()["frames"][0]["ui"], **mark["text"])
        for corner in mark["regions"]:
            region = [round(corner[0] * width), round(corner[1] * height),
                      round(corner[2] * width), round(corner[3] * height)]
            words = rendered(array, region, rule) + rendered(array, region, rule, contrast=False)
            words = [list(w) for w in {tuple(w) for w in words}]
            for box in text_lines(words, rule, size):
                if (mark["minLineHeight"] * height <= box[3] - box[1] <= mark["maxLineHeight"] * height
                        and box[2] - box[0] <= mark["maxLineWidth"] * width
                        and stroke_text(gray, box, mark["stroke"])):
                    edge = mark["pad"] * min(width, height)
                    block, note = caption_block(array, gray, box, mark, rule), "corner text line"
                    if block != box:
                        box, note = block, "caption block"
                    item = clutter.part("watermark", clutter.solid((height, width), pad(box, edge, edge, size)),
                                        f"{mark['id']} {note}")
                    item["pattern"] = mark["id"]
                    found.append(item)
    return found


def sparkles(array):
    """Four-point star marks (a generator sparkle) in a corner: pale, square, tips touching the box mid-sides."""
    height, width = array.shape[:2]
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    chroma = array.max(axis=2).astype(np.int16) - array.min(axis=2)
    found = []
    for mark in profiles().get("sparkles", []):
        k = max(5, round(mark["hatWidth"] * width)) | 1
        for corner in mark["regions"]:
            x0, y0 = round(corner[0] * width), round(corner[1] * height)
            x1, y1 = round(corner[2] * width), round(corner[3] * height)
            hat = cv2.morphologyEx(gray[y0:y1, x0:x1], cv2.MORPH_TOPHAT, np.ones((k, k), np.uint8))
            count, labels, stats, _ = cv2.connectedComponentsWithStats((hat >= mark["hatMin"]).astype(np.uint8), 8)
            for label in range(1, count):
                x, y, w, h, area = map(int, stats[label])
                if not (mark["size"][0] * width <= w <= mark["size"][1] * width
                        and abs(w - h) <= mark["squareTolerance"] * max(w, h)
                        and mark["fill"][0] <= area / (w * h) <= mark["fill"][1]):
                    continue
                star = labels[y:y + h, x:x + w] == label
                cy, cx = h // 2, w // 2
                band = max(1, h // 10)
                cross = (star[cy - band:cy + band + 1].any(axis=0).mean() >= mark["tipSpan"]
                         and star[:, cx - band:cx + band + 1].any(axis=1).mean() >= mark["tipSpan"])
                q = max(1, round(mark["cornerEmpty"] * min(w, h)))
                corners = np.concatenate([star[:q, :q].ravel(), star[:q, -q:].ravel(),
                                          star[-q:, :q].ravel(), star[-q:, -q:].ravel()])
                pale = float(np.median(chroma[y0 + y:y0 + y + h, x0 + x:x0 + x + w][star])) <= mark["chromaMax"]
                if cross and not corners.any() and pale:
                    edge = mark["pad"] * min(width, height)
                    box = pad([x0 + x, y0 + y, x0 + x + w, y0 + y + h], edge, edge, (width, height))
                    item = clutter.part("watermark", clutter.solid((height, width), box), f"{mark['id']} corner sparkle")
                    item["pattern"] = mark["id"]
                    found.append(item)
    return found


def _sample(gray, points):
    height, width = gray.shape
    x, y = np.round(points[:, 0]).astype(int), np.round(points[:, 1]).astype(int)
    keep = (x >= 0) & (x < width) & (y >= 0) & (y < height)
    values = np.full(len(points), np.nan, dtype=np.float32)
    values[keep] = gray[y[keep], x[keep]]
    return values


def _edge_continues(gray, centre, along, across, start, stop, half, rule, inset=0):
    """True when both long edges of a tilted card keep a straight contrast line from start to stop along its axis."""
    offset = rule["edgeOffset"] * gray.shape[1]
    half = half + inset
    steps = np.linspace(start, stop, 24)[:, None]
    for side in (1, -1):
        edge = centre + steps * along + side * half * across
        inner, outer = _sample(gray, edge - side * offset * across), _sample(gray, edge + side * offset * across)
        valid = ~(np.isnan(inner) | np.isnan(outer))
        if valid.mean() < rule["edgeValid"] or np.median(np.abs(inner - outer)[valid]) < rule["edgeContrast"]:
            return False
    return True


def tilted_stickers(array):
    """Rotated flat pale cards with dark lettering (music/date stickers), plus an album thumbnail their edges run into."""
    height, width = array.shape[:2]
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    grayf = gray.astype(np.float32)
    variance = cv2.blur(grayf * grayf, (9, 9)) - cv2.blur(grayf, (9, 9)) ** 2
    chroma = array.max(axis=2).astype(np.int16) - array.min(axis=2)
    found = []
    for rule in profiles().get("tiltedStickers", []):
        flat = ((array.min(axis=2) >= rule["grayMin"]) & (chroma <= rule["chromaMax"])
                & (variance <= rule["varianceMax"])).astype(np.uint8)
        closed = cv2.morphologyEx(flat, cv2.MORPH_CLOSE, np.ones((rule["close"], rule["close"]), np.uint8))
        count, labels, stats, _ = cv2.connectedComponentsWithStats(closed, 8)
        for label in range(1, count):
            if not rule["area"][0] * width * height <= stats[label, 4] <= rule["area"][1] * width * height:
                continue
            contours, _ = cv2.findContours((labels == label).astype(np.uint8), cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)
            hull = cv2.convexHull(max(contours, key=cv2.contourArea))
            (cx, cy), (rw, rh), angle = cv2.minAreaRect(hull)
            tilt = angle % 90
            tilt = min(tilt, 90 - tilt)
            if not (rw and rh and rule["tilt"][0] <= tilt <= rule["tilt"][1]
                    and cv2.contourArea(hull) >= rule["hullFill"] * rw * rh):
                continue
            card = np.zeros((height, width), dtype=np.uint8)
            cv2.fillPoly(card, [hull.reshape(-1, 2)], 1)
            holes = (card > 0) & (flat == 0)
            share = float(holes.sum()) / max(1, int(card.sum()))
            if not (rule["textShare"][0] <= share <= rule["textShare"][1]
                    and holes.any() and float((gray[holes] <= rule["textDarkMax"]).mean()) >= rule["textDark"]):
                continue
            theta = np.deg2rad(angle)
            axis_w, axis_h = np.array([np.cos(theta), np.sin(theta)]), np.array([-np.sin(theta), np.cos(theta)])
            along, across, long_half, short_half = ((axis_w, axis_h, rw / 2, rh / 2) if rw >= rh
                                                    else (axis_h, axis_w, rh / 2, rw / 2))
            centre = np.array([cx, cy])
            # A real card has straight contrast edges along its own length; a pale patch of wall or skin does not.
            # The 9x9 variance window shrinks the flat mask ~4 px inside the card's true edge.
            if not _edge_continues(grayf, centre, along, across, -.7 * long_half, .7 * long_half, short_half, rule,
                                   inset=4):
                continue
            ends = {1: long_half, -1: long_half}
            for sign in (1, -1):
                if _edge_continues(grayf, centre, sign * along, across, long_half + .1 * short_half,
                                   long_half + 1.8 * short_half, short_half, rule):
                    ends[sign] = long_half + 2 * short_half
            margin = rule["pad"] * min(width, height)
            front, back = ends[1] + margin, ends[-1] + margin
            side = short_half + margin
            corners = np.array([centre + front * along + side * across, centre + front * along - side * across,
                                centre - back * along - side * across, centre - back * along + side * across])
            polygon = [[round(float(x), 1), round(float(y), 1)] for x, y in corners]
            xs, ys = corners[:, 0], corners[:, 1]
            box = [max(0, int(xs.min())), max(0, int(ys.min())),
                   min(width, int(np.ceil(xs.max()))), min(height, int(np.ceil(ys.max())))]
            shape = np.zeros((height, width), dtype=np.uint8)
            cv2.fillPoly(shape, [np.round(corners).astype(np.int32)], 1)
            extended = " with album thumbnail" if max(ends.values()) > long_half else ""
            item = clutter.part("watermark", shape > 0, f"{rule['id']} tilted {tilt:.0f} deg{extended}")
            item.update(box=box, pattern=rule["id"], polygon=polygon)
            found.append(item)
    return found


def viewer_icons(array):
    """A viewer's close "X" and "..." menu: pure white, small, in the top corners of the picture."""
    rule = profiles().get("viewerIcons")
    if not rule:
        return []
    height, width = array.shape[:2]
    band = max(1, round(rule["band"] * height))
    top = array[:band]
    white = ((top.min(axis=2) >= rule["whiteMin"])
             & (top.max(axis=2).astype(np.int16) - top.min(axis=2) <= rule["chromaMax"])).astype(np.uint8)
    count, labels, stats, centres = cv2.connectedComponentsWithStats(white, 8)
    corner = rule["corner"] * width
    edge = rule["pad"] * min(width, height)
    found, dots = [], []
    close, dot = rule["close"], rule["dots"]
    for label in range(1, count):
        x, y, w, h, area = map(int, stats[label])
        if corner < x and x + w < width - corner:
            continue
        side, fill_share = max(w, h), area / (w * h)
        if (close["size"][0] * width <= side <= close["size"][1] * width
                and abs(w - h) <= close["squareTolerance"] * side
                and close["fill"][0] <= fill_share <= close["fill"][1]):
            shape = cv2.dilate((labels[y:y + h, x:x + w] == label).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
            t = np.linspace(.1, .9, 17)
            diagonal = min(shape[(t * (h - 1)).astype(int), (t * (w - 1)).astype(int)].mean(),
                           shape[(t * (h - 1)).astype(int), ((1 - t) * (w - 1)).astype(int)].mean())
            q = max(1, round(.15 * side))
            sides = shape[:q, w // 2 - q // 2:w // 2 + q // 2 + 1].any() or shape[h // 2 - q // 2:h // 2 + q // 2 + 1, :q].any()
            if diagonal >= close["diagonal"] and not sides:
                box = pad([x, y, x + w, y + h], edge, edge, (width, height))
                item = clutter.part("watermark", clutter.solid((height, width), box), f"{rule['id']} close X")
                item["pattern"] = rule["id"]
                found.append(item)
                continue
        if (dot["size"][0] * width <= side <= dot["size"][1] * width
                and abs(w - h) <= dot["squareTolerance"] * side and fill_share >= dot["fill"]):
            dots.append((float(centres[label][0]), float(centres[label][1]), side, [x, y, x + w, y + h]))
    dots.sort()
    for start in range(max(0, len(dots) - dot["count"] + 1)):
        run = dots[start:start + dot["count"]]
        size = np.mean([d[2] for d in run])
        gaps = np.diff([d[0] for d in run])
        if (max(d[1] for d in run) - min(d[1] for d in run) <= dot["alignTolerance"] * size
                and all(dot["spacing"][0] * size <= g <= dot["spacing"][1] * size for g in gaps)
                and max(d[2] for d in run) <= (1 + dot["squareTolerance"]) * min(d[2] for d in run)):
            box = pad([min(d[3][0] for d in run), min(d[3][1] for d in run),
                       max(d[3][2] for d in run), max(d[3][3] for d in run)], edge, edge, (width, height))
            item = clutter.part("watermark", clutter.solid((height, width), box), f"{rule['id']} menu dots")
            item["pattern"] = rule["id"]
            found.append(item)
            break
    return found


REFERENCES = pathlib.Path(__file__).with_name("overlay_references")


def _reference_feature(array, kind):
    pixels = array.astype(np.float32)
    if kind == "gold":
        return cv2.GaussianBlur(np.clip((pixels[..., 0] + pixels[..., 1]) / 2 - pixels[..., 2], 0, 255), (3, 3), 0)
    if kind == "white":
        return cv2.GaussianBlur(pixels.min(axis=2), (3, 3), 0)
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY).astype(np.float32)
    return cv2.magnitude(cv2.Sobel(gray, cv2.CV_32F, 1, 0), cv2.Sobel(gray, cv2.CV_32F, 0, 1))


def references(array):
    """Known logos matched against stored reference crops (overlay_references/): multi-scale template match on a
    colour feature, confirmed by edge correlation at the same spot so flat areas cannot match."""
    height, width = array.shape[:2]
    found = []
    for ref in profiles().get("references", []):
        path = REFERENCES / ref["file"]
        if not path.exists():
            continue
        template = cv2.cvtColor(cv2.imread(str(path), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        work = ref["work"]
        image_feature = cv2.resize(_reference_feature(array, ref["feature"]), None, fx=work, fy=work,
                                   interpolation=cv2.INTER_AREA)
        image_edges = cv2.resize(_reference_feature(array, "edge"), None, fx=work, fy=work,
                                 interpolation=cv2.INTER_AREA)
        best = None
        for scale in ref["scales"]:
            size = scale * min(width, height) / ref["shortSide"]
            factor = work * size
            feature = cv2.resize(_reference_feature(template, ref["feature"]), None, fx=factor, fy=factor,
                                 interpolation=cv2.INTER_AREA)
            if min(feature.shape) < 8 or feature.shape[0] >= image_feature.shape[0] \
                    or feature.shape[1] >= image_feature.shape[1]:
                continue
            scores = cv2.matchTemplate(image_feature, feature, cv2.TM_CCOEFF_NORMED)
            _, score, _, (x, y) = cv2.minMaxLoc(scores)
            if best is None or score > best[0]:
                best = (score, x, y, factor)
        if best is None or best[0] < ref["threshold"]:
            continue
        score, x, y, factor = best
        edges = cv2.resize(_reference_feature(template, "edge"), None, fx=factor, fy=factor,
                           interpolation=cv2.INTER_AREA)
        patch = image_edges[y:y + edges.shape[0], x:x + edges.shape[1]]
        if patch.std() == 0 or edges.std() == 0 or float(np.corrcoef(patch.ravel(), edges.ravel())[0, 1]) < ref["edgeMin"]:
            continue
        edge = ref["pad"] * min(width, height)
        box = pad([x / work, y / work, (x + edges.shape[1]) / work, (y + edges.shape[0]) / work],
                  edge, edge, (width, height))
        item = clutter.part("watermark", clutter.solid((height, width), box), f"{ref['id']} reference logo {score:.2f}")
        item["pattern"] = ref["id"]
        found.append(item)
    return found


def letterbox(array):
    """(top, bottom) rows of flat dark bars (blurred letterbox fill) that end at one sharp full-width edge, or None."""
    rule = profiles().get("letterbox")
    if not rule:
        return None
    height = array.shape[0]
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY).astype(np.float32)
    lap = np.abs(cv2.Laplacian(gray, cv2.CV_32F)).mean(axis=1)
    flat = (lap <= rule["flatMax"]) & (gray.mean(axis=1) <= rule["darkMax"]) & (gray.std(axis=1) <= rule["rowStdMax"])
    edge = (np.abs(np.diff(gray, axis=0)) >= rule["edgeStep"]).mean(axis=1) >= rule["edgeShare"]

    def run(rows, edges):
        count, misses = 0, 0
        for index, value in enumerate(rows):
            if value:
                count, misses = index + 1, 0
            else:
                misses += 1
                if misses > rule["blockGap"]:
                    break
        if not rule["minHeight"] * height <= count <= rule["maxHeight"] * height:
            return 0
        window = edges[max(0, count - 3):count + round(rule["edgeReach"] * height) + 1]
        # Cut at the sharp edge itself, not where the flat run happened to stop.
        return max(0, count - 3) + int(np.argmax(window)) + 1 if window.any() else 0

    top = run(flat, edge)
    bottom = run(flat[::-1], edge[::-1])
    if not top and not bottom:
        return None
    return top, height - bottom


def colour_masks(array, badge):
    pixels = array.astype(np.int16)
    red, green, blue = pixels[..., 0], pixels[..., 1], pixels[..., 2]
    rule = badge["magenta"]
    magenta = ((red > rule["redMin"]) & (blue > rule["blueMin"]) & (red - green > rule["redMinusGreen"])
               & (blue - green > rule["blueMinusGreen"])).astype(np.uint8)
    low, high = pixels.min(axis=2), pixels.max(axis=2)
    return magenta, (low > badge["silver"]["min"]) & (high - low < badge["silver"]["chromaMax"])


ANGLES = np.linspace(0, 2 * np.pi, 96, endpoint=False)


def score_circle(magenta, silver, cx, cy, radius, badge):
    """Structure evidence for one circle: ring coverage, isolation, and silver lettering in a central band."""
    height, width = magenta.shape
    hits = 0
    for angle in ANGLES:
        for scale in np.linspace(.88, 1.08, 6):
            x, y = int(cx + scale * radius * np.cos(angle)), int(cy + scale * radius * np.sin(angle))
            if 0 <= x < width and 0 <= y < height and magenta[y, x]:
                hits += 1
                break
    reach = 1.5 * radius
    x0, y0 = max(0, int(cx - reach)), max(0, int(cy - reach))
    x1, y1 = min(width, int(cx + reach) + 1), min(height, int(cy + reach) + 1)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    distance = np.hypot(xx - cx, yy - cy)
    local_magenta, local_silver = magenta[y0:y1, x0:x1] > 0, silver[y0:y1, x0:x1]
    inner = distance < badge["innerRadius"] * radius
    band = inner & (np.abs(yy - cy) < .3 * radius)

    def share(mask, values):
        return float(values[mask].mean()) if mask.any() else 0.0

    return {"ringCoverage": hits / len(ANGLES), "silverFraction": share(inner, local_silver),
            "letterBand": share(band, local_silver), "offBand": share(inner & ~band, local_silver),
            "innerMagenta": share(distance < .85 * radius, local_magenta),
            "outerMagenta": share((distance > 1.2 * radius) & (distance < 1.5 * radius), local_magenta)}


def accepted(score, badge):
    rule = badge["structure"]
    return (score["ringCoverage"] >= badge["ringCoverageMin"]
            and score["silverFraction"] >= badge["silverFractionMin"]
            and score["innerMagenta"] <= rule["innerMagentaMax"]
            and score["outerMagenta"] <= rule["outerMagentaMax"]
            and score["letterBand"] >= rule["letterBandRatio"] * score["offBand"])


def circles(magenta, low, high):
    found = cv2.HoughCircles(cv2.GaussianBlur(magenta * 255, (5, 5), 0), cv2.HOUGH_GRADIENT, dp=1.5,
                             minDist=max(10, low), param1=80, param2=18, minRadius=low, maxRadius=high)
    return [] if found is None else [tuple(map(float, c)) for c in found[0][:40]]


def search(magenta, silver, window, low, high, badge):
    """Best accepted circle in a window: near the largest radius (outer ring, not inner letters), best coverage."""
    x0, y0, x1, y1 = window
    found = []
    for cx, cy, radius in circles(magenta[y0:y1, x0:x1], low, high):
        score = score_circle(magenta, silver, cx + x0, cy + y0, radius, badge)
        if accepted(score, badge):
            found.append((score, (cx + x0, cy + y0, radius)))
    if not found:
        return None
    largest = max(circle[2] for _, circle in found)
    return max((item for item in found if item[1][2] >= .8 * largest), key=lambda item: item[0]["ringCoverage"])


def described(badge, found):
    score, circle = found
    result = {"badge": badge["id"], "confirmed": True,
              "circle": [round(circle[0], 1), round(circle[1], 1), round(circle[2], 1)]}
    result.update({key: round(value, 3) for key, value in score.items()})
    return result


def confirm_badge(array, box, badge=None):
    """Structure check for a proposed logo box: isolated magenta ring around a band of silver lettering."""
    badge = badge or profiles()["badges"][0]
    height, width = array.shape[:2]
    x0, y0, x1, y1 = box
    margin = round(.25 * max(x1 - x0, y1 - y0))
    window = [max(0, x0 - margin), max(0, y0 - margin), min(width, x1 + margin), min(height, y1 + margin)]
    magenta, silver = colour_masks(array, badge)
    side = min(window[2] - window[0], window[3] - window[1])
    found = search(magenta, silver, window, max(6, int(.15 * side)), max(7, int(.7 * side)), badge)
    return described(badge, found) if found else {"badge": badge["id"], "confirmed": False}


def badges(array, badge=None):
    """Confirmed badges anywhere in the frame, as filled discs slightly larger than the ring.

    Magenta pixels are grouped generously only to choose search windows; each window is searched for circles
    of at least `minRadius` of the shorter side, and a circle counts only with full structure evidence.
    """
    badge = badge or profiles()["badges"][0]
    height, width = array.shape[:2]
    side = min(width, height)
    magenta, silver = colour_masks(array, badge)
    join = max(3, round(side * .03)) | 1
    count, _, stats, _ = cv2.connectedComponentsWithStats(cv2.dilate(magenta, np.ones((join, join), np.uint8)))
    low, high = max(6, round(badge["minRadius"] * side)), round(badge["maxRadius"] * side)
    found = []
    for x, y, w, h, area in (map(int, row) for row in stats[1:]):
        if max(w, h) < 2 * low:
            continue
        window = [max(0, x - join), max(0, y - join), min(width, x + w + join), min(height, y + h + join)]
        best = search(magenta, silver, window, low, min(high, max(low + 1, max(w, h))), badge)
        if best is None:
            continue
        cx, cy, radius = best[1]
        if any(abs(o["confirmation"]["circle"][0] - cx) < radius and
               abs(o["confirmation"]["circle"][1] - cy) < radius for o in found):
            continue
        disc = np.zeros((height, width), dtype=np.uint8)
        cv2.circle(disc, (round(cx), round(cy)), round(radius * 1.12 + side * .004), 1, cv2.FILLED)
        item = clutter.part("logo", disc > 0, f"confirmed {badge['id']} badge (ring/lettering structure)")
        item["confirmation"] = described(badge, best)
        found.append(item)
    return found
