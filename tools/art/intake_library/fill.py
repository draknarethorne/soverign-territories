"""LaMa fill: each masked region is repainted from a padded patch around it, at most 768px on a side."""
import numpy as np
from PIL import Image

PATCH = 768


def fill(image, mask):
    """Repaint the True pixels of `mask` (bool HxW) in `image`; other pixels are returned unchanged."""
    import cv2
    import torch

    from intake_library import models

    pixels = np.asarray(image).copy()
    mask = mask.astype(np.uint8)
    if not mask.any():
        return image
    net = models.fill_model()
    height, width = mask.shape
    join = max(9, round(min(width, height) * .04)) | 1
    count, labels, stats, _ = cv2.connectedComponentsWithStats(cv2.dilate(mask, np.ones((join, join), np.uint8)))
    for label in range(1, count):
        x, y, w, h = (int(v) for v in stats[label, :4])
        pad = max(64, int(.6 * max(w, h)))
        x0, y0, x1, y1 = max(0, x - pad), max(0, y - pad), min(width, x + w + pad), min(height, y + h + pad)
        patch = pixels[y0:y1, x0:x1]
        region = mask[y0:y1, x0:x1] * (labels[y0:y1, x0:x1] == label)
        if not region.any():
            continue
        ph, pw = patch.shape[:2]
        scale = min(1.0, PATCH / max(ph, pw))
        sh, sw = max(8, int(ph * scale) // 8 * 8), max(8, int(pw * scale) // 8 * 8)
        small = cv2.resize(patch, (sw, sh), interpolation=cv2.INTER_AREA)
        small_mask = cv2.resize(region, (sw, sh), interpolation=cv2.INTER_NEAREST)
        small_mask = cv2.dilate(small_mask, np.ones((3, 3), np.uint8))
        with torch.no_grad():
            painted = net(torch.from_numpy(small.transpose(2, 0, 1).copy()).float()[None] / 255,
                          torch.from_numpy(small_mask).float()[None, None])[0]
        painted = np.clip(painted.permute(1, 2, 0).numpy() * 255, 0, 255).astype(np.uint8)
        painted = cv2.resize(painted, (pw, ph), interpolation=cv2.INTER_CUBIC)
        chosen = region > 0
        patch[chosen] = painted[chosen]
    return Image.fromarray(pixels)
