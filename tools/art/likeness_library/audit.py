"""Read-only identity-core analysis over already embedded photo vectors."""
import numpy as np

from .scoring import core_scores, nz


def audit_person(vectors, photo_ids, *, anchor_ids=(), protected_ids=(), stale_ids=(), ambiguous_ids=(),
                 minimum_core=3, seed_floor=0.2):
    """Score one folder, keeping trusted anchors distinct from provisional core members."""
    vectors = np.asarray(vectors, dtype=float)
    if vectors.size == 0:
        vectors = vectors.reshape((0, 0))
    if vectors.ndim != 2:
        raise ValueError("vectors must be a two-dimensional array")
    if len(photo_ids) != len(vectors):
        raise ValueError("photo_ids must have one entry per vector")
    if minimum_core < 1:
        raise ValueError("minimum_core must be positive")
    vectors = nz(vectors)

    anchors = set(anchor_ids) - set(stale_ids) - set(ambiguous_ids)
    protected = set(protected_ids) - set(stale_ids) - set(ambiguous_ids)
    stale = set(stale_ids)
    ambiguous = set(ambiguous_ids)
    anchor_indices = [i for i, photo_id in enumerate(photo_ids) if photo_id in anchors]
    protected_indices = [i for i, photo_id in enumerate(photo_ids) if photo_id in protected]
    blocked_indices = {
        i for i, photo_id in enumerate(photo_ids)
        if photo_id in stale or photo_id in ambiguous
    }
    eligible = [
        i for i, photo_id in enumerate(photo_ids)
        if i not in blocked_indices and (i not in protected_indices or i in anchor_indices)
    ]

    core_indices = []
    mode = "none"
    if anchor_indices:
        mode = "trusted"
        seed = nz(vectors[anchor_indices].mean(0))
        candidate_indices = [i for i in eligible if i not in anchor_indices]
        candidate_indices = [
            i for i in candidate_indices if float(vectors[i] @ seed) >= seed_floor
        ]
        core_indices = list(anchor_indices)
        if candidate_indices:
            _, candidate_core, _ = core_scores(vectors[candidate_indices], seed=seed)
            core_indices.extend(candidate_indices[i] for i in candidate_core)
    elif eligible:
        mode = "provisional"
        _, provisional_core, _ = core_scores(vectors[eligible])
        core_indices = [eligible[i] for i in provisional_core]

    scores = [None] * len(vectors)
    core_vector = None
    if core_indices:
        core_set = set(core_indices)
        total = vectors[core_indices].sum(0)
        reference = nz(total)
        core_vector = reference
        for i, vector in enumerate(vectors):
            if i in core_set:
                if len(core_indices) == 1:
                    continue
                comparison = nz(total - vector)
            else:
                comparison = reference
            scores[i] = float(vector @ comparison)

    return {
        "mode": mode,
        "core_indices": core_indices,
        "anchor_indices": anchor_indices,
        "protected_indices": protected_indices,
        "blocked_indices": sorted(blocked_indices),
        "scores": scores,
        "core_vector": core_vector,
        "sufficient": len(core_indices) >= minimum_core,
    }
