"""Read-only identity-core analysis over already embedded photo vectors."""
import numpy as np

from .scoring import core_scores, nz


def core_excluded_protection(catalog, protected_ids):
    """Automatic locking preserves prior eligibility, never grants new core membership."""
    return {
        photo_id for photo_id in protected_ids
        if (
            catalog["photos"].get(photo_id, {}).get("protectionProvenance", {}).get("recipeVersion")
            != "independent-gallery-loo-v1"
            or photo_id not in catalog["photos"].get(photo_id, {}).get("protectionProvenance", {}).get("frozenCorePhotoIds", ())
        )
    }


def identity_order_key(is_anchor, is_core, score, name):
    """Order trusted identity anchors, core members, then remaining photos."""
    priority = 0 if is_anchor else 1 if is_core else 2 if score is not None else 3
    return (
        priority,
        -(score if score is not None else 0.0),
        name.casefold(),
    )


def catalog_photo_flags(records, catalog):
    """Return protected, stale and ambiguous IDs from (photo_id, sha256) records."""
    counts = {}
    for photo_id, _content_sha256 in records:
        if photo_id:
            counts[photo_id] = counts.get(photo_id, 0) + 1
    ambiguous = {photo_id for photo_id, count in counts.items() if count > 1}
    protected, stale = set(), set()
    for photo_id, content_sha256 in records:
        if not photo_id or photo_id not in catalog["photos"] or photo_id in ambiguous:
            continue
        record = catalog["photos"][photo_id]
        if content_sha256 is not None and content_sha256 != record["contentSha256"]:
            stale.add(photo_id)
        elif record["protected"]:
            protected.add(photo_id)
    return protected, stale, ambiguous


def _filter_core_by_leave_one_out(vectors, core_indices, anchor_indices, minimum):
    """Remove weak provisional members without dropping every member at once."""
    core = list(core_indices)
    anchors = set(anchor_indices)
    while len(core) > 1:
        total = vectors[core].sum(0)
        scores = {
            index: float(vectors[index] @ nz(total - vectors[index]))
            for index in core
        }
        retained = [
            index for index in core
            if index in anchors or scores[index] >= minimum
        ]
        if retained == core:
            break
        if not retained:
            retained = [min(core, key=lambda index: (-scores[index], index))]
        core = retained
    return core


def audit_person(vectors, photo_ids, *, anchor_ids=(), protected_ids=(), stale_ids=(), ambiguous_ids=(),
                 minimum_core=3, seed_floor=0.2, core_minimum=0.3):
    """Score one folder, keeping trusted anchors distinct from provisional core members."""
    vectors = np.asarray(vectors, dtype=float)
    if vectors.size == 0:
        vectors = vectors.reshape((0, 0))
    if vectors.ndim != 2:
        raise ValueError("vectors must be a two-dimensional array")
    if len(photo_ids) != len(vectors):
        raise ValueError("photo_ids must have one entry per vector")
    if isinstance(minimum_core, bool) or not isinstance(minimum_core, int) or minimum_core < 1:
        raise ValueError("minimum_core must be a positive integer")
    for value, label in (
        (seed_floor, "seed_floor"),
        (core_minimum, "core_minimum"),
    ):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not np.isfinite(value)
            or not -1 <= value <= 1
        ):
            raise ValueError(f"{label} must be between -1 and 1")
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
            _, candidate_core, _ = core_scores(
                vectors[candidate_indices],
                seed=seed,
                first=seed_floor,
                thr=core_minimum,
                fallback_best=True,
            )
            core_indices.extend(candidate_indices[i] for i in candidate_core)
    elif eligible:
        mode = "provisional"
        _, provisional_core, _ = core_scores(
            vectors[eligible],
            first=seed_floor,
            thr=core_minimum,
            fallback_best=True,
        )
        core_indices = [eligible[i] for i in provisional_core]

    core_indices = _filter_core_by_leave_one_out(
        vectors,
        core_indices,
        anchor_indices,
        core_minimum,
    )
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
        "sufficient": len(eligible) >= minimum_core,
    }
