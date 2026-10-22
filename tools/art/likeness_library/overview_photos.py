"""Overview ranking and visibly separate workflow-photo pinning."""
from .audit import identity_order_key


MAX_PHOTOS = 9


def top_gallery_photos(photos, scores, *, identity_scores=None, priorities=None, sort_mode="identity"):
    """Rank overview photos using the selected identity sort."""
    identity_scores = identity_scores or {}
    priorities = priorities or {}
    if sort_mode == "score":
        return sorted(
            photos,
            key=lambda photo: (
                identity_scores.get(photo.name) is None,
                -(identity_scores.get(photo.name) or 0.0),
                photo.name.casefold(),
            ),
        )[:MAX_PHOTOS]
    if sort_mode != "identity":
        raise ValueError(f"unknown identity photo sort: {sort_mode}")
    return sorted(
        photos,
        key=lambda photo: priorities.get(
            photo.name, identity_order_key(False, False, None, photo.name),
        ),
    )[:MAX_PHOTOS]


def arrange_workflow_photo(photos, workflow_name):
    """Keep ranking intact unless the chosen photo needs the final visible slot."""
    ordered = list(photos)
    selected = next((index for index, photo in enumerate(ordered) if photo["name"] == workflow_name), None)
    pinned = selected is not None and selected >= MAX_PHOTOS
    if pinned:
        ordered.insert(MAX_PHOTOS - 1, ordered.pop(selected))
    return ordered, pinned
