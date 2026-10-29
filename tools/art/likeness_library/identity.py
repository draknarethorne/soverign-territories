"""Compose identity evidence from photo cores, anchors, and optional renders."""

import collections

import numpy as np

import comfy_workflows as cw
from likeness_library.scoring import core_scores, nz


SAME_LOOK = 0.35


def kind_of(key):
    group = key.split("/")[0]
    return "sister" if group in cw.SISTER_ROOTS else "angel" if group == "Angels" else None


def identity(space, cfg, st, rend, key, extra=()):
    """Combine a chosen/anchored photo vector with agreeing render evidence."""
    photos = space.by_key.get(key, [])
    hero = key.split("/")[-1]
    parts = list(extra) + list(st.get("anchors", {}).get(hero, []))
    chosen = {
        cw.photo_key(name)
        for character, name in cfg.get("photos", {}).items()
        if character.lower() == hero.lower() and cw.photo_key(name)
    }
    anchors = [
        photo
        for photo in photos
        if cw.photo_key(photo.name) in chosen
        or any(part and part in photo.name for part in parts)
    ]
    anchor = nz(np.mean([photo.vec for photo in anchors], axis=0)) if anchors else None
    kind = kind_of(key)
    render = rend.centroid(hero, kind) if rend and kind else None
    render_vector = render[0] if render else None
    seeds, conflict = [], False
    if anchor is not None:
        seeds.append(anchor)
    if render_vector is not None:
        if anchor is None or float(anchor @ render_vector) >= SAME_LOOK:
            seeds.append(render_vector)
        else:
            conflict = True
    return {
        "anchors": anchors,
        "a": anchor,
        "r": render_vector,
        "nr": render[1] if render else 0,
        "seed": nz(np.sum(seeds, axis=0)) if seeds else None,
        "conflict": conflict,
    }


def folder_core(space, key, ident=None):
    photos = space.by_key[key]
    _scores, core, centroid = core_scores(
        np.array([photo.vec for photo in photos]),
        ident["seed"] if ident else None,
    )
    return photos, _scores, core, centroid


def identity_vec(centroid, ident):
    """Include the render vector only when it agrees with the photo identity core."""
    render = ident["r"] if ident else None
    return nz(centroid + render) if render is not None and float(centroid @ render) >= SAME_LOOK else centroid


def anchor_args(values):
    result = collections.defaultdict(list)
    for value in values or []:
        hero, _, fragment = value.partition("=")
        result[hero.lower()].append(fragment)
    return result
