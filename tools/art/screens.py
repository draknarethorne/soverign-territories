#!/usr/bin/env python3
"""Phone screenshots of Facebook Reels carry the app's own text over the picture: a status bar and a "Find related reels" bar on top, a caption, side icons,
a comment or "UP NEXT" bar and the phone's navigation bar below. Those overlays end up in the scaled copy and in the headshot, and they sit over the hair.

The layout is the same on every such screenshot, so it can be found and cut away without guessing: `is_reel_ui` recognises the bottom bars, `clean_box` is the
part of the picture that is only the picture, and `clean` crops to it. A photo whose head reaches into the overlay (`head_clear`) cannot be fixed by cropping.
"""
import numpy as np

# fractions of the screenshot's width and height: the picture without the app's bars, caption and side icons
CLEAN = (0.0, 0.105, 0.88, 0.71)
HAIR = 0.2  # how far above the detected face box (brows to chin) the hairline is, in face heights; a little of the crown may be cut, never the forehead


def lum(im):
    return np.asarray(im.convert("L"), dtype=float)


def is_reel_ui(im):
    """True for a phone screenshot of Facebook (reels, photo view): a light navigation bar along the bottom with a dark band just above it, on a tall picture."""
    w, h = im.size
    if h < 1.9 * w or h < 600:
        return False
    g = lum(im.resize((64, 256)))
    nav, band = g[int(256 * 0.965):], g[int(256 * 0.925):int(256 * 0.945)]
    return bool(nav.mean() > 195 and nav.std() < 40 and band.mean() < 90)


def clean_box(size):
    w, h = size
    x0, y0, x1, y1 = CLEAN
    return round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)


def clean(im):
    """The picture without the app's overlays when it is a reel screenshot, else the picture itself."""
    return im.crop(clean_box(im.size)) if is_reel_ui(im) else im


def head_clear(box, size=None):
    """Does the head (the face box widened upwards for the hair; box = x, y, w, h as fractions of the whole screenshot) lie inside the clean part?"""
    x0, y0, x1, y1 = CLEAN
    x, y, w, h = box
    return y - HAIR * h >= y0 and y + h <= y1 and x >= x0 and x + w <= x1
