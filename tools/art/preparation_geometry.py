"""Shared first-crop geometry: solid borders, reel panels, local face detection and the trace step record.

The v16 crop/erase/frame steps live in intake_library.pipeline; heuristics are not semantic hair-safety proof.
"""
import hashlib
import os
import pathlib

import cv2
import numpy as np

import screens
from likeness_library.engine import human_rows


def border_box(image):
    """Trim only contiguous, full-span near-solid black/white outer lines, retaining a guard."""
    pixels = np.asarray(image.convert("RGB"), dtype=np.int16)
    height, width = pixels.shape[:2]

    def edge_run(lines):
        count = 0
        color = None
        for line in lines:
            low, high = line.min(axis=0), line.max(axis=0)
            if np.any(high - low > 10) or not (np.all(high <= 20) or np.all(low >= 235)):
                break
            current = line[0]
            if color is not None and np.any(np.abs(current - color) > 10):
                break
            color = current if color is None else color
            count += 1
        # Refuse broad/ambiguous flat backgrounds, and leave two pixels at the content boundary.
        return count - 2 if 5 <= count <= len(lines) // 5 else 0

    top, bottom = edge_run(pixels), edge_run(pixels[::-1])
    middle = pixels[top:height - bottom]
    columns = np.swapaxes(middle, 0, 1)
    left, right = edge_run(columns), edge_run(columns[::-1])
    return left, top, width - right, height - bottom


def plan(image):
    full = (0, 0, *image.size)
    box = border_box(image)
    reel = screens.is_reel_ui(image)
    return {
        "box": list(box),
        "method": "full-span-solid-border-v1",
        "changed": box != full,
        "reason": ("Only near-solid external black/white strips removed; two-pixel boundary guard retained."
                   if box != full else "No confidently separable solid outer border; original geometry retained."),
        "overlayDetected": reel,
        "uiCropBox": list(screens.clean_box(image.size)) if reel else None,
        "uiCropAssessment": (
            "Existing fixed screenshot crop shown for comparison only; may remove hair/body. "
            "Not used for enhancements or recommended. Overlaid graphics remain for ComfyUI."
            if reel else "Narrow reel heuristic did not match; other overlays/borders may still exist."),
    }


def local_model():
    base = pathlib.Path(os.environ.get("LOCALAPPDATA", pathlib.Path.home() / ".cache"))
    return base / "sovereign-territories" / "models" / "face_detection_yunet_2023mar.onnx"


def model_evidence():
    path = local_model()
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "unavailable-no-download"


def detect_faces(image):
    """Use only the already-installed detector; never load recognition or download models."""
    path = local_model()
    if not path.is_file():
        return None, "Local YuNet unavailable; processing skipped, not classified as Junk. No download."
    try:
        detector = cv2.FaceDetectorYN.create(str(path), "", (320, 320), 0.7, 0.3, 5000)
        rgb = np.asarray(image.convert("RGB"))
        scale = min(1.0, 1600 / max(image.size))
        small = cv2.resize(rgb[:, :, ::-1], (round(image.width * scale), round(image.height * scale)))
        detector.setInputSize((small.shape[1], small.shape[0]))
        rows = None
        for threshold in (.7, .5):
            detector.setScoreThreshold(threshold)
            _, rows = detector.detect(small)
            if rows is not None and len(rows):
                break
    except cv2.error as exc:
        return None, f"Local face detector failed; processing skipped, not classified as Junk: {exc}"
    humans = human_rows(list(rows)) if rows is not None and len(rows) else []
    faces = [list(map(float, row[:4] / scale)) for row in humans]
    raw_count = len(rows) if rows is not None else 0
    return faces, (f"Local YuNet retained {len(faces)} face candidate(s) from {raw_count} using shared "
                   "human_rows filtering. This is not species classification: animal-only false detections "
                   "remain possible; no animal-driven subject crop is applied. Face margins are not "
                   "hair/body segmentation.")


def panel_box(image, faces, base):
    """Find black panel-to-picture transitions only in detected reel screenshots."""
    width, height = image.size
    if not faces:
        return base, "No detected face guard: panel crops not selected."
    dark = (np.asarray(image).max(axis=2) <= 35).mean(axis=1)
    top, bottom = base[1], base[3]
    # Top must end in a near-full-width solid band, followed by actual picture rows.
    for y in range(int(height * .08), int(height * .22)):
        if (np.all(dark[max(0, y - 20):y] >= .98)
                and np.all(dark[y:y + 10] < .75)
                and all(y <= fy - .45 * fh for _, fy, _, fh in faces)):
            top = y
            break
    # Caption text can interrupt a black panel; require sustained evidence after its edge.
    for y in range(int(height * .65), int(height * .93)):
        tail = dark[y:int(height * .94)]
        if (np.all(dark[y:y + 24] >= .88) and len(tail) and (tail >= .75).mean() >= .7
                and dark[max(0, y - 8):y].mean() < .75
                and all(y >= fy + 1.5 * fh for _, fy, _, fh in faces)):
            bottom = y
            break
    box = (base[0], top, base[2], bottom)
    return box, ("Detected black app-panel transitions with local face guards; provisional crop, "
                 "not proof of complete hair/body preservation. Side overlays may remain."
                 if box != base else "No panel transition passed black-band and face-margin safeguards.")


def step(name, status, source, candidate, selected, reason):
    return {"name": name, "status": status, "input": source, "candidate": candidate,
            "selected": selected, "reason": reason}
