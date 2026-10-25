"""Named intake folders: Various/<Name>/gallery holds photos the user knows are all one person.

The folder name is the identity. The whole folder is moved into that person's existing folder (one name match in a
general root), or into a new Prospects/<Name> (5+ photos) or Potentials/<Name>; face matching does not split it on the
way in. Artists are a separate domain and are never matched by name here.
"""
import hashlib
import pathlib

from .engine import unassigned_home

PERSON_ROOTS = ("Angels", "Sisters", "Models", "Prospects", "Potentials")
BUCKETS = ("gallery", "review")
RESERVED = {"gallery", "review", "duplicates", "various"}


def is_seed_name(name):
    lowered = name.casefold()
    return not (
        lowered in RESERVED or name.startswith(("_", "."))
        or lowered.startswith(("gallery_", "headshot_")) or "/" in name or "\\" in name
    )


def seeded_folders(work, images):
    """[(name, folder, {bucket: [paths]})] for every Various/<Name> that holds photos; images(path) lists a folder's photos."""
    pool = pathlib.Path(work) / "Various"
    if not pool.is_dir():
        return []
    found = []
    for folder in sorted((p for p in pool.iterdir() if p.is_dir()), key=lambda p: p.name.casefold()):
        if not is_seed_name(folder.name):
            continue
        files = {bucket: list(images(folder / bucket)) for bucket in BUCKETS}
        if any(files.values()):
            found.append((folder.name, folder, files))
    return found


def sha1(path):
    return hashlib.sha1(pathlib.Path(path).read_bytes()).hexdigest()


def plan_seeded(seeds, existing_keys, rejected=lambda path: False):
    """Plan whole-folder moves for named seeds.

    existing_keys: general person folders such as 'Prospects/Mia'. Returns (plans, held) where each plan is
    {name, source, destination, new, photos: [(path, bucket)], skipped: [(path, reason)]}.
    """
    by_name = {}
    for key in existing_keys:
        root, _, name = key.partition("/")
        if root in PERSON_ROOTS and name and "/" not in name:
            by_name.setdefault(name.casefold(), []).append(key)
    plans, held = [], []
    for name, folder, files in seeds:
        same = sorted(by_name.get(name.casefold(), []))
        total = sum(len(paths) for paths in files.values())
        if len(same) > 1:
            held.append({"name": name, "source": f"Various/{name}", "photos": total,
                         "reason": f"name matches several people ({', '.join(same)}); rename the folder or merge them first"})
            continue
        photos, skipped = [], []
        for bucket in BUCKETS:
            for path in files[bucket]:
                if rejected(path):
                    skipped.append((path, "a recorded identity rejection; use reconcile or a staged action"))
                else:
                    photos.append((path, bucket))
        plans.append({
            "name": name, "source": f"Various/{name}",
            "destination": same[0] if same else unassigned_home(name, total),
            "new": not same, "photos": photos, "skipped": skipped,
        })
    return plans, held
