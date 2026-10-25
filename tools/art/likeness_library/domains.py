"""Invocation-local library boundaries; algorithms and source layout stay shared."""
import contextlib
import copy
import pathlib
from contextvars import ContextVar


CURRENT = ContextVar("likeness_domain", default=None)
READ_ONLY = ContextVar("likeness_read_only", default=False)
ARTIST_COMMANDS = frozenset({
    "scan", "calibrate", "audit-core", "diagnostics", "policy", "alike", "compare",
    "folder", "group", "artists", "crop", "crops", "junk", "undo", "names",
    "index", "profile", "who",
})


@contextlib.contextmanager
def activate(domain, *, read_only=False):
    if domain not in ("general", "artists"):
        raise ValueError(f"unknown likeness domain: {domain}")
    token = CURRENT.set(domain)
    read_token = READ_ONLY.set(read_only)
    try:
        yield
    finally:
        CURRENT.reset(token)
        READ_ONLY.reset(read_token)


def includes(key):
    domain = CURRENT.get()
    parts = pathlib.PurePosixPath(str(key).replace("\\", "/")).parts
    if not parts or ".." in parts or parts[0] in ("/", "."):
        return False
    if parts[0] in ("_junk", "_retired", "_archive"):
        retired = parts[0] == "_retired"
        parts = parts[1:]
        if retired and parts[:1] == ("photos",):
            parts = parts[1:]
    if not parts:
        return False
    return domain is None or (parts[0].casefold() == "artists") == (domain == "artists")


def configuration(cfg, default_roots):
    if CURRENT.get() is None:
        return cfg
    scoped = copy.deepcopy(cfg)
    paths = scoped.setdefault("paths", {})
    roots = paths.get("photoRoots", default_roots)
    for root in roots:
        if root not in default_roots:
            raise ValueError(f"likeness photoRoots must be supported top-level categories: {root}")
    paths["photoRoots"] = [root for root in roots if includes(root)]
    return scoped


def require_path(work, path):
    root = pathlib.Path(work).resolve()
    path = pathlib.Path(path)
    relative = path.resolve().relative_to(root)
    if not includes(relative.as_posix()):
        raise ValueError(f"{CURRENT.get()} likeness cannot access {relative}; use the owning entry point")
    for parent in (path, *path.parents):
        if parent.is_symlink() or (hasattr(parent, "is_junction") and parent.is_junction()):
            raise ValueError(f"linked likeness path is not permitted: {parent}")
        if parent.resolve() == root:
            break


def require_moves(work, moves):
    if CURRENT.get() is None:
        return
    for move in moves:
        require_path(work, move.photo.path)
        require_path(work, pathlib.Path(work) / move.to / move.bucket / move.photo.name)


def state_path(work, name):
    if CURRENT.get() is None:
        return None
    return pathlib.Path(work) / "_likeness" / CURRENT.get() / name


def require_general_space(space):
    """A mixed space cannot be made general-only by hiding its Artist cards."""
    keys = set(getattr(space, "keys", ()))
    keys.update(photo.key for photo in getattr(space, "photos", ()))
    if any(key.split("/", 1)[0].casefold() == "artists" for key in keys):
        raise ValueError("people galleries require a general-only scoring space; rebuild in the general domain")
