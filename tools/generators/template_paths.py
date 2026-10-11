"""Where each hero stage template lives under data/art/_templates/heroes, by the numbered stage folders the art sets use (1_Alpha, 2_Studies, ...).

template_path("bare-human.txt") -> "data/art/_templates/heroes/1_Alpha/bare-human.txt". The scaffold scripts name a template by its file name; this finds it, so a template can
move between stage folders without touching them. Names are unique across the folders (the generator looks a template up by its file name).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
HEROES = ROOT / "data" / "art" / "_templates" / "heroes"
_found = {}


def template_path(name):
    """The repo-relative path of a hero template by file name; a name that already has a folder in it is returned as it is."""
    if "/" in name:
        return name
    if not _found:
        for p in sorted(HEROES.rglob("*.txt")):
            _found.setdefault(p.name, p.relative_to(ROOT).as_posix())
    if name not in _found:
        raise KeyError(f"no hero template named {name} under {HEROES}")
    return _found[name]
