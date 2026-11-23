"""Face-quality classes that separate matching from reference authority.

The engine embeds the largest detected face and records the face count, the
second-largest/main area ratio ``f2``, the main box and its pixel size. This
module classifies one measured photo:

* ``single-face``: exactly one detected face. Eligible for matching and as a
  reference vote (the historical rule: ``faces == 1`` and ``f2 <= multiFace``).
* ``dominant-face``: more than one detected face, every other face is below
  ``dominantFaceSecondaryMaximum`` (default 0.5) of the main face's area, the
  main face meets ``minFace`` and head/chest framing can be built. Eligible for
  matching only; never a reference vote, core member or anchor.
* ``overlapping-duplicate-box``: the recorded second face is near-equal
  (``f2 >= NEAR_EQUAL_SECONDARY_MINIMUM``) and a bounded, read-only
  re-detection shows it overlaps the main box (one face detected twice). It is
  matched as one face but, because the cached measurement still records two
  boxes, it stays match-only.
* ``multi-face-held``: a separate second face is too large, or a near-equal
  second box cannot be proven to be the same face. Held for review.
* ``unusable``: no usable face vector at ``minFace``.

Re-detection is used only for near-equal second boxes during planning. It reads
the measured image with the already-local detector and never writes the
measurement cache or alignment evidence, so cache entries stay valid.
"""
import math

DEFAULT_DOMINANT_SECONDARY_MAXIMUM = 0.5
NEAR_EQUAL_SECONDARY_MINIMUM = 0.9
SAME_FACE_IOU_MINIMUM = 0.5
SAME_FACE_CONTAINMENT_MINIMUM = 0.8
REDETECTION_RATIO_TOLERANCE = 0.05
MATCH_ONLY_CLASSES = frozenset({"dominant-face", "overlapping-duplicate-box"})


def dominant_maximum(settings):
    value = settings.get("dominantFaceSecondaryMaximum", DEFAULT_DOMINANT_SECONDARY_MAXIMUM)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value <= 1:
        raise ValueError("dominantFaceSecondaryMaximum must be a number in (0, 1]")
    return float(value)


def box_overlap(first, second):
    """Return (IoU, containment of the smaller box) for two (x, y, w, h) boxes."""
    x1, y1, w1, h1 = (float(value) for value in first)
    x2, y2, w2, h2 = (float(value) for value in second)
    width = max(0., min(x1 + w1, x2 + w2) - max(x1, x2))
    height = max(0., min(y1 + h1, y2 + h2) - max(y1, y2))
    intersection = width * height
    first_area, second_area = max(w1, 0.) * max(h1, 0.), max(w2, 0.) * max(h2, 0.)
    union = first_area + second_area - intersection
    smaller = min(first_area, second_area)
    return (
        intersection / union if union > 0 else 0.,
        intersection / smaller if smaller > 0 else 0.,
    )


def same_face(first, second):
    iou, containment = box_overlap(first, second)
    return iou >= SAME_FACE_IOU_MINIMUM or containment >= SAME_FACE_CONTAINMENT_MINIMUM


def framing_box_valid(box, px, min_face):
    """Return whether a normalized main-face box can seed head/chest crops."""
    return (
        isinstance(box, (list, tuple)) and len(box) == 4
        and all(isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(value) for value in box)
        and box[2] > 0 and box[3] > 0
        and box[0] >= -0.05 and box[1] >= -0.05
        and box[0] + box[2] <= 1.05 and box[1] + box[3] <= 1.05
        and isinstance(px, (int, float)) and px >= min_face
    )


def redetector(embedder):
    """Bounded read-only re-detection using the embedder's already-local detector.

    It never downloads models and never writes the measurement cache or
    alignment evidence; failures are returned to the caller as a hold.
    """
    def redetect(path):
        from PIL import Image

        if getattr(embedder, "det", None) is None:
            root = getattr(embedder, "model_root", None)
            names = ("face_detection_yunet_2023mar.onnx", "face_recognition_sface_2021dec.onnx")
            if root is None or not all((root / "models" / name).is_file() for name in names):
                raise ValueError("local face models are unavailable; downloads are disabled for re-detection")
        with Image.open(path) as image:
            image.load()
            humans, _others = embedder.faces(image)
        return [tuple(float(value) for value in box) for box in humans]
    return redetect


def derivative_framing(path, photo):
    """Return None when head/chest framing is expected to build, else a reason."""
    from . import derivatives

    for framing in ("head", "chest"):
        reason = derivatives.expected_unavailability(path, framing, photo.box, photo.px, photo.faces)
        if reason:
            return reason
    return None


def assess(photo, settings, *, path=None, redetect=None, framing=None):
    """Classify one measured photo; see the module docstring for the classes."""
    minimum = settings["minFace"]
    multi = settings["multiFace"]
    dominant = dominant_maximum(settings)
    faces = getattr(photo, "faces", -1)
    secondary = float(getattr(photo, "f2", 0.) or 0.)
    evidence = {
        "faces": faces, "secondaryRatio": secondary, "px": getattr(photo, "px", 0),
        "minFace": minimum, "referenceSecondaryMaximum": multi,
        "dominantSecondaryMaximum": dominant,
    }

    def result(kind, match, reason, **extra):
        return {
            "class": kind, "matchEligible": match,
            "referenceEligible": kind == "single-face", "reason": reason,
            **evidence, **extra,
        }

    if not photo.usable(minimum) or faces < 1:
        return result("unusable", False, "no usable face vector at the minimum face size")
    if faces == 1 and secondary <= multi:
        return result("single-face", True, "one detected face")
    kind, extra = "dominant-face", {}
    if secondary >= NEAR_EQUAL_SECONDARY_MINIMUM:
        if redetect is None or path is None:
            return result("multi-face-held", False,
                          "near-equal second face box; overlap re-detection is unavailable")
        try:
            boxes = sorted(redetect(path), key=lambda box: box[2] * box[3], reverse=True)
        except Exception as error:  # Detection failure must hold, never admit.
            return result("multi-face-held", False, f"near-equal second face box; re-detection failed: {error}")
        ratio = boxes[1][2] * boxes[1][3] / (boxes[0][2] * boxes[0][3]) if len(boxes) > 1 and boxes[0][2] * boxes[0][3] > 0 else 0.
        if len(boxes) != faces or abs(ratio - secondary) > REDETECTION_RATIO_TOLERANCE:
            return result("multi-face-held", False,
                          "near-equal second face box; re-detection does not reproduce the recorded measurement",
                          redetectedFaces=len(boxes), redetectedSecondaryRatio=round(ratio, 4))
        main = boxes[0]
        separate = [box for box in boxes[1:] if not same_face(main, box)]
        iou, containment = box_overlap(main, boxes[1])
        extra = {
            "redetectedFaces": len(boxes), "secondBoxIoU": round(iou, 4),
            "secondBoxContainment": round(containment, 4),
            "overlapRule": f"IoU >= {SAME_FACE_IOU_MINIMUM} or containment >= {SAME_FACE_CONTAINMENT_MINIMUM}",
        }
        if len(separate) == len(boxes) - 1:
            return result("multi-face-held", False,
                          "two near-equal separate faces; the main person is ambiguous", **extra)
        remaining = separate[0][2] * separate[0][3] / (main[2] * main[3]) if separate else 0.
        extra["remainingSecondaryRatio"] = round(remaining, 4)
        if remaining >= dominant:
            return result("multi-face-held", False,
                          f"after merging overlapping boxes another face is at least {dominant:.0%} of the main face",
                          **extra)
        kind = "overlapping-duplicate-box"
    elif secondary >= dominant:
        return result("multi-face-held", False,
                      f"a second face is at least {dominant:.0%} of the main face's area")
    if not framing_box_valid(getattr(photo, "box", None), getattr(photo, "px", 0), minimum):
        return result("multi-face-held", False, "head/chest framing unavailable: main face box is invalid", **extra)
    if framing is not None and path is not None:
        try:
            reason = framing(path, photo)
        except Exception as error:  # Unknown framing state must hold, never admit.
            reason = f"framing check failed: {error}"
        if reason:
            return result("multi-face-held", False, f"head/chest framing unavailable: {reason}", **extra)
    return result(
        kind, True,
        ("overlapping duplicate detection of the main face; matched as one face, match-only"
         if kind == "overlapping-duplicate-box" else
         f"dominant main face; other faces are below {dominant:.0%} of its area; match-only"),
        **extra,
    )


def candidate_fields(assessment, enabled=True):
    """Candidate fields shared by rebase and intake planning."""
    fields = {
        "qualityEligible": bool(enabled and assessment["matchEligible"]),
        "referenceQualityEligible": bool(enabled and assessment["referenceEligible"]),
    }
    if assessment["class"] in MATCH_ONLY_CLASSES or assessment["class"] == "multi-face-held":
        fields["faceQuality"] = assessment
    return fields


def reference_quality(candidate):
    """A candidate may become a reference vote only with single-face quality."""
    return (
        candidate.get("qualityEligible") is True
        and candidate.get("referenceQualityEligible", True) is not False
    )
