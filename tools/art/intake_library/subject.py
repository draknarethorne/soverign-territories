"""Who is in the picture: Mask R-CNN person masks, reduced to the subject (main person plus other large people)."""
import numpy as np

SCORE = 0.5
MERGE = 0.5      # a box mostly inside the main person is part of it (split limbs, duplicates)
COMPANION = 0.2  # separate people at least this share of the main person's area count as subjects too
DETECT_SIZE = 800


def detect(image):
    """{box, mask, people, score} for the subject in `image`, or None when no person is found."""
    import cv2
    import torch

    from intake_library import models

    scale = min(1.0, DETECT_SIZE / max(image.size))
    small = image.resize((round(image.width * scale), round(image.height * scale))) if scale < 1 else image
    tensor = torch.from_numpy(np.asarray(small).transpose(2, 0, 1).copy()).float() / 255
    with torch.no_grad():
        result = models.person_detector()([tensor])[0]
    people = []
    for label, score, box, mask in zip(result["labels"], result["scores"], result["boxes"], result["masks"]):
        if int(label) == 1 and float(score) >= SCORE:
            full = cv2.resize(mask[0].numpy(), image.size) > 0.5
            if full.any():
                people.append({"score": float(score), "mask": full,
                               "box": [round(float(v) / scale) for v in box]})
    return select(people, image.size)


def area(box):
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def inside_share(box, other):
    """Share of the smaller box covered by their intersection."""
    overlap = area([max(box[0], other[0]), max(box[1], other[1]), min(box[2], other[2]), min(box[3], other[3])])
    return overlap / max(1, min(area(box), area(other)))


def select(people, size):
    if not people:
        return None
    main = max(people, key=lambda p: int(p["mask"].sum()))
    mask = main["mask"].copy()
    main_area = int(main["mask"].sum())
    kept, companions, dropped = [main], 0, 0
    for person in people:
        if person is main:
            continue
        if inside_share(person["box"], main["box"]) >= MERGE:
            kept.append(person)
        elif int(person["mask"].sum()) >= COMPANION * main_area:
            kept.append(person)
            companions += 1
        else:
            dropped += 1  # thumbnails in ad cards, far-away figures
    for person in kept:
        mask |= person["mask"]
    ys, xs = np.nonzero(mask)
    box = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    return {"box": box, "mask": mask, "people": 1 + companions, "dropped": dropped,
            "score": round(main["score"], 3)}


def from_faces(faces, offset, size):
    """Fallback subject when no person is detected: a body frame around every face."""
    width, height = size
    ox, oy = offset
    mask = np.zeros((height, width), dtype=bool)
    for x, y, w, h in faces:
        x0, y0 = max(0, int(x - 1.25 * w - ox)), max(0, int(y - 1.2 * h - oy))
        x1, y1 = min(width, int(x + 2.25 * w - ox)), min(height, int(y + 5 * h - oy))
        if x1 > x0 and y1 > y0:
            mask[y0:y1, x0:x1] = True
    if not mask.any():
        return None
    ys, xs = np.nonzero(mask)
    return {"box": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1], "mask": mask,
            "people": len(faces), "dropped": 0, "score": None}
