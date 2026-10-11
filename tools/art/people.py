#!/usr/bin/env python3
"""The z_ file: who a library folder's person was, and where she has been.

Every person folder (an angel, a sister, a prospect, a person grouped inside an artist's folder) keeps one file in its gallery,
named after the person's original name: z_molly_duval.txt. The file's first line says the name; the lines after it are dated history:

    name: Molly Duval
    2026-10-09 +73 from Prospects/Various: looks like Drakness (0.52)
    2026-10-10 now the sister Drakness

The tools write it (likeness moves, merges and pairings); you may edit it by hand. When the name is unknown the file carries the invented name
the folder was given, so a prospect who becomes an angel, or an angel who is replaced, is never anonymous. The image tools ignore the file.
"""
import datetime
import pathlib
import re

Z_FILE = re.compile(r"^z_(.+)\.txt$", re.I)


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "unknown"


def unslug(text):
    return " ".join(w.capitalize() for w in text.split("_") if w)


def find(folder):
    """The z_ file of a person folder (in its gallery; one left beside the gallery is found too), or None."""
    for d in (pathlib.Path(folder) / "gallery", pathlib.Path(folder)):
        if d.is_dir():
            for p in sorted(d.iterdir()):
                if p.is_file() and Z_FILE.match(p.name):
                    return p
    return None


def read(folder):
    """(name, [history lines]) or None when the folder has no z_ file."""
    p = find(folder)
    if not p:
        return None
    lines = [ln.rstrip() for ln in p.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
    name = unslug(Z_FILE.match(p.name)[1])
    if lines and lines[0].lower().startswith("name:"):
        name = lines.pop(0)[5:].strip() or name
    return name, lines


def name_of(folder):
    got = read(folder)
    return got[0] if got else None


def reserved(folder):
    """The 'reserved:' history lines of a folder (it looks like a top-tier angel or sister), newest last."""
    got = read(folder)
    return [ln for ln in (got[1] if got else []) if " reserved:" in ln]


def write(folder, name, history):
    """Write the z_ file (renamed after the name when the name changed); returns its path."""
    folder = pathlib.Path(folder)
    gallery = folder / "gallery"
    gallery.mkdir(parents=True, exist_ok=True)
    old = find(folder)
    path = gallery / f"z_{slug(name)}.txt"
    path.write_text("\n".join([f"name: {name}", *history]) + "\n", encoding="utf-8")
    if old and old != path and old.exists():
        old.unlink()
    return path


def today():
    return datetime.date.today().isoformat()


def note(folder, event, name=None, when=None):
    """Append a dated line to the folder's history; creates the file (named `name`, else the folder's own name) when there is none."""
    folder = pathlib.Path(folder)
    got = read(folder)
    nm, hist = got if got else (name or folder.name, [])
    line = f"{when or today()} {event}"
    if line not in hist:
        hist = hist + [line]
    return write(folder, nm, hist)


def adopt(folder, name, event, when=None):
    """The folder now holds a different person: the file is renamed after her and the old name is kept in the history."""
    got = read(folder)
    old = got[0] if got else None
    hist = got[1] if got else []
    if old and old.lower() != name.lower():
        hist = hist + [f"{when or today()} was {old}"]
    hist = hist + [f"{when or today()} {event}"]
    return write(folder, name, hist)
