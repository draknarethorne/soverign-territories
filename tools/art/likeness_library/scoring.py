"""Shared vector scoring for the likeness library."""
import numpy as np


def nz(a):
    n = np.linalg.norm(a, axis=-1, keepdims=True)
    return a / np.where(n == 0, 1, n)


def core_scores(vecs, seed=None, first=0.2, thr=0.3, rounds=3, fallback_best=False):
    """Score each vector against a refined core, leaving it out of its own score."""
    vecs = np.asarray(vecs)
    c = nz(seed) if seed is not None else nz(vecs.mean(0))
    core = list(range(len(vecs)))
    for r in range(rounds):
        sc = vecs @ c
        selected = [
            i for i, score in enumerate(sc)
            if score >= (first if seed is not None and r == 0 else thr)
        ]
        if selected:
            core = selected
        elif fallback_best and seed is None:
            core = [int(np.argmax(sc))]
        elif fallback_best:
            core = []
            break
        c = nz(vecs[core].mean(0))
    if not core:
        return [], [], nz(seed)
    total = vecs[core].sum(0)
    inside = set(core)
    scores = [float(v @ nz(total - v if i in inside and len(core) > 1 else total)) for i, v in enumerate(vecs)]
    return scores, core, c
