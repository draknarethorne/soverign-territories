"""Bounded local CLIP diagnostic on below-face context, never person identity."""
import hashlib
import importlib.metadata
import pathlib

import numpy as np
from PIL import Image, ImageOps

from . import review_packet, shadow


def crop_region(image, box):
    """Keep the saved face out; missing below-face pixels are explicit."""
    if (not isinstance(box, (tuple, list)) or len(box) != 4
            or not all(isinstance(v, (int, float)) and np.isfinite(v) for v in box)):
        raise ValueError("context requires a finite normalized face box")
    x, y, w, h = box
    if min(x, y) < 0 or min(w, h) <= 0 or x + w > 1.01 or y + h > 1.01:
        raise ValueError("context face box is outside normalized image")
    width, height = image.size
    left = max(0, round((x - .75 * w) * width))
    right = min(width, round((x + 1.75 * w) * width))
    top = min(height, int(np.ceil((y + 1.25 * h) * height)))
    bottom = min(height, round((y + 5.0 * h) * height))
    if right - left < 32 or bottom - top < max(32, .75 * h * height):
        return None
    return (left, top, right, bottom)


def measure(packet, run, cache, checkpoint):
    checkpoint = pathlib.Path(checkpoint)
    if not checkpoint.is_absolute() or not checkpoint.is_file() or checkpoint.suffix != ".safetensors":
        raise ValueError("context checkpoint must be an existing absolute local .safetensors file; no downloads")
    if not 1 <= len(packet["usedPhotoIds"]) <= 40:
        raise ValueError("context measurement exceeds the 40-photo bound")
    # Import only for this explicitly selected, offline experiment.
    import open_clip
    import torch

    weight_hash = shadow.digest(checkpoint)
    model, _, transform = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained=str(checkpoint), device="cpu",
    )
    model.eval()
    torch.set_num_threads(min(4, torch.get_num_threads()))
    photos = {row["photoId"]: row for row in run["photos"]}
    published = {row["path"]: row["sha256"] for row in run["publishedFiles"]}
    boxes = {
        row["alignmentEvidence"]["sourceSha256"]: row["box"] for row in cache["emb"].values()
        if row.get("alignmentEvidence", {}).get("sourceSha256") and row.get("box")
    }
    results, vectors = {}, {}
    for pid in packet["usedPhotoIds"]:
        row = photos[pid]
        source = review_packet.safe_path(pathlib.Path(run["workingRoot"]), row["destination"])
        expected = published.get(row["destination"])
        if not expected or shadow.digest(source) != expected:
            raise ValueError(f"context source missing or changed: {pid}")
        if row["preparedSHA256"] not in boxes:
            raise ValueError(f"content-bound face box missing for context: {pid}")
        with Image.open(source) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            region = crop_region(image, boxes[row["preparedSHA256"]])
            if region is None:
                results[pid] = {"status": "unavailable", "reason": "Insufficient pixels below face", "sourceSHA256": expected}
                continue
            crop = image.crop(region)
            tensor = transform(crop).unsqueeze(0)
            with torch.inference_mode():
                vector = model.encode_image(tensor).float().cpu().numpy()[0]
            norm = np.linalg.norm(vector)
            if not np.isfinite(vector).all() or not np.isfinite(norm) or norm == 0:
                raise ValueError(f"invalid context feature: {pid}")
            vectors[pid] = vector / norm
            results[pid] = {
                "status": "measured", "sourceSHA256": expected, "cropPixels": list(region),
                "cropRGBSHA256": hashlib.sha256(crop.tobytes()).hexdigest(),
                "vector": [round(float(value), 8) for value in vectors[pid]],
            }
    pairs = []
    for case in packet["cases"]:
        query = case["photoId"]
        for ref in dict.fromkeys([case["currentReferenceId"], *case["targetReferenceIds"]]):
            pairs.append({
                "caseId": case["id"], "photoId": query, "referencePhotoId": ref,
                "similarity": round(float(vectors[query] @ vectors[ref]), 6)
                if query in vectors and ref in vectors else None,
                "status": "measured" if query in vectors and ref in vectors else "unavailable",
            })
    if shadow.digest(checkpoint) != weight_hash:
        raise ValueError("context model changed during inference")
    return {
        "schemaVersion": 1, "kind": "below-face-context-diagnostic",
        "model": {"architecture": "ViT-B-32", "checkpoint": str(checkpoint),
                  "sha256": weight_hash, "openClipVersion": importlib.metadata.version("open_clip_torch"),
                  "torchVersion": torch.__version__, "device": "cpu"},
        "recipe": "Face-box-relative region below face (1.25h to 5h), x-.75w to x+1.75w; no segmentation",
        "photos": results, "pairs": pairs,
        "summary": {"photoCount": len(results), "measuredCount": len(vectors), "unavailableCount": len(results)-len(vectors)},
        "limits": [
            "Context may describe clothing, background or composition, NOT verified same person.",
            "The region excludes the saved face box but is not a person-segmentation mask.",
            "Different outfits can reduce similarity for the same person; shared outfits/background can raise it for different people.",
            "CLIP is a general visual-semantic model, not an accepted person re-identification classifier.",
            "Scores are not probabilities, no threshold or fusion weight is accepted, and no matching decision is changed.",
            "No body proportions, age, ethnicity, real family or sensitive attributes are inferred.",
            "Bounded report sample only; not full-library context extraction or pipeline integration.",
        ],
    }
