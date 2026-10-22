"""Rank person-folder centroid similarities for gallery cross-references."""

from .policy import default_policy, score_band


CATEGORY_ORDER = tuple(default_policy()["categoryOrder"])


def rank_identity_centroids(space, keys, categories=None, centroids=None, category_order=None):
    """Rank by library hierarchy, then similarity within each category."""
    centroid = getattr(space, "centroid", None)
    keys = list(dict.fromkeys(keys))
    categories = categories or {}
    category_priority = {
        category: index
        for index, category in enumerate(category_order or CATEGORY_ORDER)
    }
    if centroids is None and not callable(centroid):
        return {key: [] for key in keys}

    vectors = {
        key: centroids.get(key) if centroids is not None else centroid(key)
        for key in keys
    }
    rankings = {}
    for key in keys:
        vector = vectors[key]
        matches = []
        if vector is not None:
            for other_key in keys:
                other = vectors[other_key]
                if other_key != key and other is not None:
                    matches.append({
                        "key": other_key,
                        "category": categories.get(other_key, other_key.split("/", 1)[0]),
                        "name": other_key.split("/", 1)[1],
                        "score": float(vector @ other),
                    })
        rankings[key] = sorted(
            matches,
            key=lambda match: (
                category_priority.get(match["category"], len(category_priority)),
                -match["score"],
                match["key"].casefold(),
            ),
        )
    return rankings
