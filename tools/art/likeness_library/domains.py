"""Invocation-local library boundaries; algorithms and source layout stay shared."""
import contextlib
import copy
import pathlib
import sys
from contextvars import ContextVar

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.workflows import comfy_workflows as cw  # noqa: E402


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


def includes(key, work=None, cfg=None):
    domain = CURRENT.get()
    parts = pathlib.PurePosixPath(str(key).replace("\\", "/")).parts
    if not parts or ".." in parts or parts[0] in ("/", "."):
        return False
    prefixes = [(("_junk",), False), (("_retired",), True), (("_archive",), False)]
    if work is not None:
        config = cfg if cfg is not None else cw.load_cfg()
        root = pathlib.Path(work).resolve()
        prefixes = [
            (cw.storage_root(config, name, root=root).relative_to(root).parts, retired)
            for name, retired in (("junk", False), ("retired", True))
        ] + [(("_archive",), False)]
    for prefix, retired in prefixes:
        if parts[:len(prefix)] == prefix:
            parts = parts[len(prefix):]
            if retired and parts[:1] == ("photos",):
                parts = parts[1:]
            break
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
    if not includes(relative.as_posix(), root):
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


def state_path(work, name, storage_root=None):
    if CURRENT.get() is None:
        return None
    root = (
        pathlib.Path(storage_root)
        if storage_root is not None
        else cw.storage_root(cw.load_cfg(), "likeness", root=work)
    )
    return root / CURRENT.get() / name


def require_general_space(space):
    """A mixed space cannot be made general-only by hiding its Artist cards."""
    keys = set(getattr(space, "keys", ()))
    keys.update(photo.key for photo in getattr(space, "photos", ()))
    if any(key.split("/", 1)[0].casefold() == "artists" for key in keys):
        raise ValueError("people galleries require a general-only scoring space; rebuild in the general domain")
