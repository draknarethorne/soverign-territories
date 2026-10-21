#!/usr/bin/env python3
"""Shared face-centered thumbnail framing for the local people galleries."""
import pathlib
import sys

from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools/art"))
import originals  # noqa: E402


def crop_thumbnail(image, box, framing, size):
    """Return a chest-up or head crop using the cached normalized face box."""
    image = ImageOps.exif_transpose(image).convert("RGB")
    if not box:
        return ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    if framing == "head":
        crop_box = originals.headshot_box(image.size, box, size)
        return image.crop(crop_box).resize(size, Image.Resampling.LANCZOS)
    if framing != "chest":
        raise ValueError(f"unknown thumbnail framing: {framing}")

    width, height = image.size
    face_x, face_y, face_w, face_h = box
    crop_h = face_h * height * 4.4
    crop_w = crop_h * size[0] / size[1]
    scale = min(1.0, width / crop_w, height / crop_h)
    crop_w *= scale
    crop_h *= scale
    center_x = (face_x + face_w / 2) * width
    center_y = (face_y + face_h * 1.55) * height
    left = min(max(0, center_x - crop_w / 2), width - crop_w)
    top = min(max(0, center_y - crop_h / 2), height - crop_h)
    crop = image.crop((left, top, left + crop_w, top + crop_h))
    return ImageOps.fit(crop, size, Image.Resampling.LANCZOS)


def face_thumbnail(image, box, size=(320, 320)):
    """Return a square crop of the detected face with a small context margin."""
    if not box:
        raise ValueError("a detected face box is required")
    image = ImageOps.exif_transpose(image).convert("RGB")
    width, height = image.size
    face_x, face_y, face_w, face_h = box
    side = min(max(face_w * width, face_h * height) * 1.8, width, height)
    center_x = (face_x + face_w / 2) * width
    center_y = (face_y + face_h / 2) * height
    left = min(max(0, center_x - side / 2), width - side)
    top = min(max(0, center_y - side / 2), height - side)
    crop = image.crop((left, top, left + side, top + side))
    return ImageOps.fit(crop, size, Image.Resampling.LANCZOS)
