"""Rank person-folder centroid similarities for gallery cross-references."""

CATEGORY_ORDER = ("Sisters", "Angels", "Models", "Prospects", "Potentials", "Artists")
CATEGORY_PRIORITY = {category: index for index, category in enumerate(CATEGORY_ORDER)}


def score_band(score):
    """Return the shared, display-only similarity band for a numeric score."""
    if score >= 0.55:
        return "green"
    if score >= 0.30:
        return "yellow"
    if score >= 0.15:
        return "orange"
    return "red"


def rank_identity_centroids(space, keys, categories=None):
    """Rank by library hierarchy, then similarity within each category."""
    centroid = getattr(space, "centroid", None)
    keys = list(dict.fromkeys(keys))
    categories = categories or {}
    if not callable(centroid):
        return {key: [] for key in keys}

    vectors = {key: centroid(key) for key in keys}
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
                CATEGORY_PRIORITY.get(match["category"], len(CATEGORY_ORDER)),
                -match["score"],
                match["key"].casefold(),
            ),
        )
    return rankings
