"""Explicit Sandbox folder retirement; callers must retain the preview digest.

This is not an OS-wide writer lock. Callers must stop other library writers.
The inventory and journal checks detect observed conflicts and preserve evidence.
"""
import contextlib
import hashlib
import json
import os
import pathlib
import stat

from tools.art import temporary_storage
from tools.workflows import comfy_workflows as cw
from . import metadata, normal_transaction, person_rename, sandbox

KIND = "sandbox-empty-folder-retirement-v1"
CATEGORIES = frozenset(("Angels", "Sisters", "Models", "Prospects", "Potentials"))
IMAGES = frozenset((".jpg", ".jpeg", ".png", ".webp", ".bmp"))
MAX_FOLDERS = 256
MAX_ENTRIES = 100000
MAX_BYTES = 64 * 1024 ** 3
LOCK_NAME = ".sandbox-empty-retirement.lock"


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


def _root(root):
    root = pathlib.Path(root)
    if not root.is_absolute() or not sandbox.is_sandbox_working_path(root):
        raise ValueError("retirement requires an absolute Sandbox/Working root")
    # Check every existing component, including ancestors of the sandbox.
    for path in (root, *root.parents):
        if sandbox._is_reparse_point(path):
            raise ValueError(f"linked sandbox path: {path}")
    if root.resolve(strict=True) != root or not root.is_dir():
        raise ValueError("Sandbox/Working must be an existing unlinked directory")
    return root


def _path(root, relative):
    path = normal_transaction.safe(root, relative)
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if sandbox._is_reparse_point(current):
            raise ValueError(f"linked retirement path: {current}")
    return path


def _folder(key):
    if not isinstance(key, str) or "\\" in key:
        raise ValueError("invalid identity folder")
    parts = key.split("/")
    if (len(parts) != 2 or parts[0] not in CATEGORIES
            or not person_rename.valid_name(parts[1])):
        raise ValueError(f"unsupported identity folder: {key}")
    return key


def _absent(path):
    return not path.exists() and not sandbox._is_reparse_point(path)


def _directory_identity(path):
    info = path.lstat()
    if sandbox._is_reparse_point(path) or not stat.S_ISDIR(info.st_mode) or not info.st_ino:
        raise ValueError(f"unsafe or unidentifiable retirement directory: {path}")
    return {"device": info.st_dev, "inode": info.st_ino}


def _inventory(folder):
    """Capture bytes, directory structure and relevant Windows file metadata."""
    entries, count, size = [], 0, 0

    def visit(path):
        nonlocal count, size
        info = path.lstat()
        if sandbox._is_reparse_point(path):
            raise ValueError(f"linked identity entry: {path}")
        is_dir = stat.S_ISDIR(info.st_mode)
        if not is_dir and not stat.S_ISREG(info.st_mode):
            raise ValueError(f"unsupported identity entry: {path}")
        if not is_dir and info.st_nlink != 1:
            raise ValueError(f"hard-linked identity file: {path}")
        count += 1
        size += 0 if is_dir else info.st_size
        if count > MAX_ENTRIES or size > MAX_BYTES:
            raise ValueError("identity inventory exceeds retirement bounds")
        entry = {
            "path": path.relative_to(folder).as_posix(), "directory": is_dir,
            "mode": info.st_mode, "modifiedNs": info.st_mtime_ns,
            "attributes": getattr(info, "st_file_attributes", 0),
        }
        if not is_dir:
            entry["bytes"] = info.st_size
            entry["sha256"] = metadata.content_sha256(path)
        entries.append(entry)
        if is_dir:
            children = sorted(path.iterdir(), key=lambda p: (p.name.casefold(), p.name))
            names = [child.name.casefold() for child in children]
            if len(names) != len(set(names)):
                raise ValueError(f"case-colliding identity entries: {path}")
            for child in children:
                visit(child)
        after = path.lstat()
        if (info.st_mode, info.st_size, info.st_mtime_ns, getattr(info, "st_file_attributes", 0),
                info.st_ino, info.st_dev) != (
                after.st_mode, after.st_size, after.st_mtime_ns,
                getattr(after, "st_file_attributes", 0), after.st_ino, after.st_dev):
            raise ValueError(f"identity changed during inventory: {path}; "
                             f"mtime={info.st_mtime_ns}/{after.st_mtime_ns}; "
                             f"attributes={getattr(info, 'st_file_attributes', 0)}/"
                             f"{getattr(after, 'st_file_attributes', 0)}")

    visit(folder)
    return entries


CAST = frozenset(("Sisters", "Angels"))


class CastEmptied(ValueError):
    """A planned run would empty a Sisters/Angels folder; a human must decide."""


def _owner(relative):
    """CATEGORY/Name for a direct Gallery/Review original path, else None."""
    parts = relative.split("/") if isinstance(relative, str) else []
    if len(parts) == 4 and parts[0] in CATEGORIES and parts[2].casefold() in ("gallery", "review"):
        return "/".join(parts[:2])
    return None


def _folder_originals(folder):
    """Gallery/Review originals, counting nested identities' buckets so they are never retired."""
    found = []
    for directory in (folder / "gallery", folder / "review", *folder.glob("*/gallery"), *folder.glob("*/review")):
        if directory.is_dir():
            found.extend(child for child in directory.iterdir()
                         if child.is_file() and child.suffix.casefold() in IMAGES)
    return found


def retired_root(root, cfg):
    """Working-relative configured ``retired`` storage root."""
    return cw.storage_root(cfg, "retired", root=pathlib.Path(root)).relative_to(pathlib.Path(root)).as_posix()


def plan_emptied(root, cfg, moves, dispositions=()):
    """Identity folders that keep no Gallery/Review original after the planned moves.

    ``moves`` and ``dispositions`` are rows with Working-relative ``source`` and
    ``destination``. Derivative folders (for example 944x1104) do not count as
    originals and move with the retired folder. Returns sorted retirement rows
    ``{"source", "destination", "photos"}``; raises ``CastEmptied`` (with a
    per-folder report) when a Sisters/Angels folder would be emptied and refuses
    an existing retired destination. Read-only.
    """
    root = pathlib.Path(root)
    leaving, arriving = {}, set()
    for row in [*moves, *dispositions]:
        source, destination = row["source"], row["destination"]
        if source == destination:
            continue
        owner = _owner(source)
        if owner:
            leaving.setdefault(owner, []).append({"source": source, "destination": destination})
        target = _owner(destination)
        if target:
            arriving.add(target.casefold())
    retired = retired_root(root, cfg)
    retire, cast = [], []
    for owner, photos in sorted(leaving.items()):
        if owner.casefold() in arriving:
            continue
        folder = normal_transaction.safe(root, owner)
        if not folder.is_dir():
            continue
        gone = {row["source"].casefold() for row in photos}
        if any(path.relative_to(root).as_posix().casefold() not in gone for path in _folder_originals(folder)):
            continue
        row = {"source": owner, "destination": f"{retired}/{owner}",
               "photos": sorted(photos, key=lambda item: item["source"])}
        (cast if owner.split("/", 1)[0] in CAST else retire).append(row)
    if cast:
        raise CastEmptied(
            f"{len(cast)} Sisters/Angels folder(s) would be emptied; cast folders are never retired "
            "automatically. Inspect these moves and decide manually:\n" + "\n".join(
                f"  {row['source']}: " + "; ".join(
                    f"{photo['source']} -> {photo['destination']}" for photo in row["photos"])
                for row in cast))
    for row in retire:
        destination = normal_transaction.safe(root, row["destination"])
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"retired destination already exists; refusing to overwrite: {row['destination']}")
    return retire


def _empty(entries):
    for entry in entries:
        parts = entry["path"].split("/")
        if (len(parts) == 2 and parts[0].casefold() in ("gallery", "review")
                and not entry["directory"] and pathlib.PurePosixPath(parts[1]).suffix.casefold() in IMAGES):
            raise ValueError("identity still has a Gallery or Review original")
        if len(parts) == 2 and parts[1].casefold() == "gallery" and entry["directory"]:
            raise ValueError("identity contains a nested identity")


def _source_evidence(rows, folders):
    """Select the original rebase source rows for explicitly chosen folders."""
    if not isinstance(rows, list) or len(rows) > MAX_ENTRIES:
        raise ValueError("explicit rebase source rows are required")
    result = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid rebase source row")
        owner, source, digest = row.get("owner"), row.get("source"), row.get("sourceHash")
        if owner not in folders:
            continue
        parts = source.split("/") if isinstance(source, str) else []
        if (len(parts) != 4 or "/".join(parts[:2]) != owner
                or parts[2].casefold() not in ("gallery", "review")
                or not parts[3] or any(c in source for c in '\\:<>|?*')
                or any(ord(c) < 32 for c in source)
                or pathlib.PurePosixPath(parts[3]).suffix.casefold() not in IMAGES
                or not isinstance(digest, str) or len(digest) != 64
                or any(c not in "0123456789abcdef" for c in digest)):
            raise ValueError(f"invalid rebase source evidence for {owner}")
        result.append({"owner": owner, "source": source, "sourceHash": digest})
    result.sort(key=lambda row: (row["owner"], row["source"], row["sourceHash"]))
    if set(folders) != {row["owner"] for row in result}:
        raise ValueError("every selected folder requires an original rebase source row")
    if len({row["source"].casefold() for row in result}) != len(result):
        raise ValueError("duplicate rebase source rows")
    return result


def _source_receipt(root, relative, folders, expected=None):
    path = _path(root, relative)
    if path.stat().st_size > 128 * 1024 ** 2:
        raise ValueError("rebase receipt exceeds retirement bounds")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected is not None and digest != expected:
        raise ValueError("rebase source receipt changed")
    receipt = json.loads(raw)
    if (receipt.get("kind") != "normal-rebase-receipt" or receipt.get("schemaVersion") != 1
            or receipt.get("status") != "applied" or receipt.get("root") != str(root)
            or not isinstance(receipt.get("plan"), dict)):
        raise ValueError("expected an applied rebase source receipt for this Sandbox")
    plan = receipt["plan"]
    hashes = plan.get("sourceHashes")
    if not isinstance(hashes, dict) or receipt.get("sourceHashes") != hashes:
        raise ValueError("rebase source hashes are not bound to the receipt")
    rows = _source_evidence(plan.get("sourceRows"), set(folders))
    if any(hashes.get(row["source"]) != row["sourceHash"] for row in rows):
        raise ValueError("rebase source row differs from receipt source hashes")
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError("rebase source receipt changed while reading")
    return path, digest, rows


def _previous(root, relative, expected=None):
    path = _path(root, relative)
    if path.stat().st_size > 64 * 1024 ** 2:
        raise ValueError("predecessor journal exceeds retirement bounds")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected is not None and digest != expected:
        raise ValueError("predecessor journal changed")
    data = json.loads(raw)
    if (data.get("kind") != "normal-publication" or data.get("status") != "applied"
            or data.get("root") != str(root) or data.get("externalAfter")
            or any(key.startswith("pending") for key in data)
            or not isinstance(data.get("after"), dict)
            or not isinstance(data.get("removed"), list)
            or len(data["after"]) > MAX_ENTRIES or len(data["removed"]) > MAX_ENTRIES):
        raise ValueError("unsupported predecessor publication")
    after, removed = data["after"], data["removed"]
    if (any(not isinstance(key, str) or not isinstance(value, str) or len(value) != 64
            or any(c not in "0123456789abcdef" for c in value) for key, value in after.items())
            or any(not isinstance(key, str) for key in removed)
            or len({key.casefold() for key in after}) != len(after)
            or len({key.casefold() for key in removed}) != len(removed)
            or {key.casefold() for key in after} & {key.casefold() for key in removed}):
        raise ValueError("invalid or colliding predecessor paths and hashes")
    return path, digest, data


def _previous_check(root, data, mapping):
    for relative, expected in data["after"].items():
        target = _path(root, mapping.get(relative, normal_transaction.located(data, relative)))
        if not target.is_file() or metadata.content_sha256(target) != expected:
            raise ValueError(f"predecessor published content changed: {relative}")
    for relative in data["removed"]:
        if not _absent(_path(root, normal_transaction.located(data, relative))):
            raise ValueError(f"predecessor removed content reappeared: {relative}")


def _exact_mapping(plan, previous):
    """Derive the complete predecessor mapping, never trust arbitrary redirects."""
    expected = {}
    for move in plan["moves"]:
        prefix = move["source"] + "/"
        for relative in previous["after"]:
            if relative.casefold().startswith(prefix.casefold()):
                expected[relative] = move["destination"] + relative[len(move["source"]):]
    if plan.get("predecessorMapping") != expected:
        raise ValueError("retirement predecessor mapping is not exact")
    return expected


def _corrected_receipt(root, relative, plan, expected=None):
    """Bind the corrected receipt to the predecessor and distinct source evidence."""
    from . import normal_rebase

    path = _path(root, relative)
    if path.stat().st_size > 128 * 1024 ** 2:
        raise ValueError("corrected rebase receipt exceeds retirement bounds")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected is not None and digest != expected:
        raise ValueError("corrected rebase receipt changed")
    saved = json.loads(raw)
    if (saved.get("kind") != "normal-rebase-receipt" or saved.get("schemaVersion") != 1
            or saved.get("status") != "applied" or saved.get("root") != str(root)
            or not isinstance(saved.get("plan"), dict)
            or saved.get("implementationSHA256") != metadata.content_sha256(pathlib.Path(normal_rebase.__file__))):
        raise ValueError("corrected rebase receipt or implementation changed")
    predecessor_path, _, previous = _previous(root, plan["predecessor"], plan["predecessorSha256"])
    if (pathlib.Path(saved["journal"]) != predecessor_path
            or not isinstance(saved.get("runId"), str) or not saved["runId"]
            or not isinstance(saved.get("bindings"), dict)
            or previous.get("runId") != saved.get("runId")
            or previous.get("bindings") != saved.get("bindings")):
        raise ValueError("retirement predecessor is not bound to rebase receipt")
    if relative != plan["sourceReceipt"]:
        lineage = saved["plan"].get("releaseLineage")
        source = _path(root, plan["sourceReceipt"])
        if (not isinstance(lineage, dict) or lineage.get("receipt") != str(source)
                or not isinstance(lineage.get("inputs"), dict)
                or lineage["inputs"].get("receiptSHA256") != plan["sourceReceiptSha256"]):
            raise ValueError("corrected rebase is not bound to original retirement source evidence")
    if path.read_bytes() != raw:
        raise ValueError("corrected rebase receipt changed while reading")
    return path, digest, saved


def _corrected_binding(root, plan):
    if "correctedReceipt" in plan:
        _corrected_receipt(root, plan["correctedReceipt"], plan, plan["correctedReceiptSha256"])


def preview(root, folders, source_receipt, predecessor, *, cfg, corrected_receipt=None):
    """Return a read-only plan and its digest; never discover additional folders.

    ``source_receipt`` is the Working-relative applied rebase receipt;
    its source rows and hashes bind the selected folders.
    ``predecessor`` is a Working-relative applied normal-publication journal.
    A distinct ``corrected_receipt`` binds that predecessor and the original
    source receipt; it is also Working-relative.
    """
    root = _root(root)
    if not isinstance(folders, (list, tuple)) or not 1 <= len(folders) <= MAX_FOLDERS:
        raise ValueError("provide 1..256 explicitly selected identity folders")
    folders = [_folder(key) for key in folders]
    if len({key.casefold() for key in folders}) != len(folders):
        raise ValueError("duplicate identity folders")
    folders = sorted(folders)
    source_path, source_hash, evidence = _source_receipt(root, source_receipt, folders)
    retired = cw.storage_root(cfg, "retired", root=root)
    retired_relative = retired.relative_to(root).as_posix()
    _path(root, retired_relative)
    if not retired.is_dir():
        raise ValueError("configured retired root must already exist")
    retired_identity = _directory_identity(retired)
    reports = cw.storage_root(cfg, "reports", root=root).relative_to(root).as_posix()
    _path(root, reports)
    previous_path, previous_hash, previous = _previous(root, predecessor)
    corrected_path = None
    corrected_hash = None
    if corrected_receipt is not None:
        corrected_path, corrected_hash, _ = _corrected_receipt(root, corrected_receipt, {
            "sourceReceipt": source_receipt, "sourceReceiptSha256": source_hash,
            "predecessor": predecessor, "predecessorSha256": previous_hash,
        })
    lock_relative = f"{reports}/{LOCK_NAME}"
    if (lock_relative in (predecessor, source_receipt, corrected_receipt)
            or lock_relative in previous["after"] or lock_relative in previous["removed"]):
        raise ValueError("retirement lock overlaps predecessor or rebase evidence")
    _previous_check(root, previous, {})
    moves, mapping, category_parents = [], {}, {}
    total_entries = total_bytes = 0
    for key in folders:
        source = _path(root, key)
        destination_relative = f"{retired_relative}/{key}"
        destination = _path(root, destination_relative)
        parent_relative = f'{retired_relative}/{key.split("/")[0]}'
        if parent_relative not in category_parents:
            category_parents[parent_relative] = (
                None if _absent(destination.parent) else _directory_identity(destination.parent)
            )
            if (category_parents[parent_relative] is None
                    and parent_relative.casefold() in {item.casefold() for item in previous["removed"]}):
                raise ValueError(f"category creation conflicts with predecessor removal: {parent_relative}")
        if not source.is_dir() or not _absent(destination):
            raise ValueError(f"missing source or destination collision: {key}")
        if any(source in path.parents or destination in path.parents
               for path in (previous_path, source_path, corrected_path) if path is not None):
            raise ValueError("source receipt or predecessor journal overlaps a retired folder")
        entries = _inventory(source)
        _empty(entries)
        total_entries += len(entries)
        total_bytes += sum(row.get("bytes", 0) for row in entries)
        if total_entries > MAX_ENTRIES or total_bytes > MAX_BYTES:
            raise ValueError("retirement exceeds aggregate inventory bounds")
        files = {f'{key}/{entry["path"]}': entry["sha256"] for entry in entries
                 if not entry["directory"]}
        for relative, digest in previous["after"].items():
            if relative.startswith(key + "/"):
                if files.get(relative) != digest:
                    raise ValueError(f"predecessor file differs from identity inventory: {relative}")
                mapping[relative] = destination_relative + relative[len(key):]
        moves.append({"source": key, "destination": destination_relative, "entries": entries})
    if hashlib.sha256(previous_path.read_bytes()).hexdigest() != previous_hash:
        raise ValueError("predecessor changed during preview")
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != source_hash:
        raise ValueError("rebase source receipt changed during preview")
    if corrected_path is not None and hashlib.sha256(corrected_path.read_bytes()).hexdigest() != corrected_hash:
        raise ValueError("corrected rebase receipt changed during preview")
    plan = {"kind": KIND, "root": str(root), "retiredRoot": retired_relative, "reportsRoot": reports,
            "retiredRootIdentity": retired_identity, "categoryParents": category_parents,
            "sourceReceipt": source_receipt, "sourceReceiptSha256": source_hash,
            "predecessor": predecessor, "predecessorSha256": previous_hash,
            "sourceRows": evidence, "moves": moves, "predecessorMapping": mapping}
    if corrected_receipt is not None:
        plan["correctedReceipt"] = corrected_receipt
        plan["correctedReceiptSha256"] = corrected_hash
    _check_parents(root, plan, {"createdParents": {}})
    return plan, _digest(plan)


def _plan(root, plan, expected):
    root = _root(root)
    if (not isinstance(plan, dict) or plan.get("kind") != KIND
            or plan.get("root") != str(root) or _digest(plan) != expected):
        raise ValueError("retirement plan differs from the externally retained preview digest")
    if ("correctedReceipt" in plan) != ("correctedReceiptSha256" in plan):
        raise ValueError("incomplete corrected receipt binding")
    folders = [_folder(move["source"]) for move in plan["moves"]]
    if (not folders or len(folders) > MAX_FOLDERS
            or len({key.casefold() for key in folders}) != len(folders)):
        raise ValueError("invalid retirement plan folders")
    _source_evidence(plan["sourceRows"], set(folders))
    expected_parents = {f'{plan["retiredRoot"]}/{folder.split("/")[0]}' for folder in folders}
    if not isinstance(plan.get("categoryParents"), dict) or set(plan["categoryParents"]) != expected_parents:
        raise ValueError("invalid retirement category parents")
    for move in plan["moves"]:
        if move["destination"] != f'{plan["retiredRoot"]}/{move["source"]}':
            raise ValueError("retirement destination does not match preview")
        _path(root, move["source"])
        _path(root, move["destination"])
    return root


def _journal(root, relative, plan):
    path = _path(root, relative)
    reports = _path(root, plan["reportsRoot"])
    if reports not in path.parents:
        raise ValueError("retirement journal must remain inside configured reports storage")
    if not path.parent.is_dir():
        raise ValueError("retirement journal parent must already exist")
    for move in plan["moves"]:
        for key in ("source", "destination"):
            folder = _path(root, move[key])
            if path == folder or folder in path.parents:
                raise ValueError("journal overlaps retirement folder")
    if relative in (plan["predecessor"], plan["sourceReceipt"], plan.get("correctedReceipt"),
                    f'{plan["reportsRoot"]}/{LOCK_NAME}'):
        raise ValueError("journal overlaps predecessor or rebase receipt")
    return path


@contextlib.contextmanager
def _locked(root, plan):
    lock = _path(root, f'{plan["reportsRoot"]}/{LOCK_NAME}')
    try:
        stream = lock.open("x+b")
        created = True
    except FileExistsError:
        stream = lock.open("r+b")
        created = False
    with stream:
        if sandbox._is_reparse_point(lock) or lock.stat().st_nlink != 1:
            raise ValueError("unsafe retirement lock")
        if created:
            temporary_storage._ensure_lock_byte(stream)
        if not temporary_storage._lock(stream):
            raise ValueError("retirement journal is locked by another cooperating writer")
        try:
            if not created:
                stream.seek(0)
                if stream.read(2) != b"\0":
                    raise ValueError("unrecognized retirement lock; preserve and inspect")
            yield
        finally:
            temporary_storage._unlock(stream)


def _move_state(root, move):
    source = _path(root, move["source"])
    target = _path(root, move["destination"])
    if not source.parent.is_dir() or (not _absent(target.parent) and not target.parent.is_dir()):
        raise ValueError(f"retirement parent missing: {move['source']}")
    src, dst = not _absent(source), not _absent(target)
    if src == dst:
        raise ValueError(f"ambiguous retirement locations: {move['source']}")
    present = source if src else target
    if not present.is_dir() or _inventory(present) != move["entries"]:
        raise ValueError(f"retirement inventory changed: {present}")
    return "source" if src else "destination"


def _state(root, plan):
    return [_move_state(root, move) for move in plan["moves"]]


def _check_parents(root, plan, data, states=None, *, allow_pending=False):
    retired = _path(root, plan["retiredRoot"])
    if _directory_identity(retired) != plan["retiredRootIdentity"]:
        raise ValueError("retired root changed since preview")
    created = data.get("createdParents", {})
    pending = data.get("pendingParent")
    parents = plan["categoryParents"]
    if (not isinstance(created, dict) or not set(created).issubset(parents)
            or any(parents[key] is not None for key in created)
            or (pending is not None and (not allow_pending or pending not in parents
                                         or parents[pending] is not None or pending in created))):
        raise ValueError("invalid or ambiguous category parent journal state")
    for relative, before in parents.items():
        parent = _path(root, relative)
        expected = before if before is not None else created.get(relative)
        if expected is not None:
            if _absent(parent) or _directory_identity(parent) != expected:
                raise ValueError(f"retirement category parent changed: {relative}")
        elif pending == relative:
            if not _absent(parent):
                _directory_identity(parent)
            if states is None or any(
                state != "source" for move, state in zip(plan["moves"], states)
                if pathlib.PurePosixPath(move["destination"]).parent.as_posix() == relative
            ):
                raise ValueError(f"ambiguous interrupted category creation: {relative}")
        elif not _absent(parent):
            raise ValueError(f"retirement category parent appeared: {relative}")


def _read(root, journal, expected):
    path = _path(root, journal)
    if path.stat().st_size > 128 * 1024 ** 2:
        raise ValueError("retirement journal exceeds bounds; preserve and inspect")
    try:
        raw = path.read_bytes()
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("incomplete retirement journal; preserve and inspect") from exc
    _plan(root, data["plan"], expected)
    if data.get("planSha256") != expected or data.get("status") not in (
            "publishing", "applied", "recovery-required", "recovering", "recovered"):
        raise ValueError("invalid retirement journal")
    _journal(root, journal, data["plan"])
    return path, data, raw


class _JournalWriter:
    def __init__(self, path, raw):
        self.path = path
        self.raw = raw

    def write(self, data):
        if self.path.read_bytes() != self.raw:
            raise ValueError("retirement journal changed concurrently; preserve and inspect")
        normal_transaction.write(self.path, data)
        raw = self.path.read_bytes()
        if json.loads(raw) != data:
            raise ValueError("retirement journal changed while writing; preserve and inspect")
        self.raw = raw


def _check_partial(root, plan, states):
    """Verify all predecessor paths against their current source/archive location."""
    _source_binding(root, plan)
    _corrected_binding(root, plan)
    path, digest, previous = _previous(root, plan["predecessor"], plan["predecessorSha256"])
    _exact_mapping(plan, previous)
    moved = {move["source"] for move, state in zip(plan["moves"], states)
             if state == "destination"}
    mapping = {
        old: new for old, new in plan["predecessorMapping"].items()
        if any(old.startswith(folder + "/") for folder in moved)
    }
    _previous_check(root, previous, mapping)
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError("predecessor changed during recovery check")


def _source_binding(root, plan):
    _, _, rows = _source_receipt(root, plan["sourceReceipt"],
                                 [move["source"] for move in plan["moves"]],
                                 plan["sourceReceiptSha256"])
    if rows != plan["sourceRows"]:
        raise ValueError("retirement source rows differ from bound rebase receipt")


def _require_windows():
    if os.name != "nt":
        raise ValueError("exclusive folder rename is supported on Windows only")


def apply(root, plan, expected, journal, *, cfg):
    """Publish a preview; interrupted or conflicted transactions retain the journal."""
    _require_windows()
    root = _plan(root, plan, expected)
    journal_path = _journal(root, journal, plan)
    with _locked(root, plan):
        if not _absent(journal_path):
            raise ValueError("retirement journal already exists")
        options = {"corrected_receipt": plan["correctedReceipt"]} if "correctedReceipt" in plan else {}
        fresh, digest = preview(root, [m["source"] for m in plan["moves"]],
                                plan["sourceReceipt"], plan["predecessor"], cfg=cfg, **options)
        if digest != expected or fresh != plan:
            raise ValueError("retirement preview is stale")
        data = {"plan": plan, "planSha256": expected, "status": "publishing", "createdParents": {}}
        # A partial exclusive initial write is deliberately retained for inspection.
        normal_transaction.write(journal_path, data, exclusive=True)
        raw = journal_path.read_bytes()
        if json.loads(raw) != data:
            raise ValueError(f"initial retirement journal changed; preserve {journal_path}")
        writer = _JournalWriter(journal_path, raw)
        try:
            _check_parents(root, plan, data)
            _check_partial(root, plan, _state(root, plan))
            for index, move in enumerate(plan["moves"]):
                _previous(root, plan["predecessor"], plan["predecessorSha256"])
                _check_parents(root, plan, data)
                if _move_state(root, move) != "source":
                    raise ValueError("retirement source moved concurrently")
                parent_relative = pathlib.PurePosixPath(move["destination"]).parent.as_posix()
                if plan["categoryParents"][parent_relative] is None and parent_relative not in data["createdParents"]:
                    data["pendingParent"] = parent_relative
                    writer.write(data)
                    parent = _path(root, parent_relative)
                    parent.mkdir()
                    data["createdParents"][parent_relative] = _directory_identity(parent)
                    del data["pendingParent"]
                    writer.write(data)
                _check_parents(root, plan, data)
                data["pending"] = index
                writer.write(data)
                _path(root, move["source"]).rename(_path(root, move["destination"]))
                if _move_state(root, move) != "destination":
                    raise ValueError("retirement changed during move")
                del data["pending"]
                writer.write(data)
            _check(root, plan, data)
            data["status"] = "applied"
            writer.write(data)
        except Exception as exc:
            data["status"] = "recovery-required"
            data["error"] = str(exc)
            try:
                writer.write(data)
            except Exception as journal_error:
                raise OSError(f"retirement failed; journal update also failed; preserve {journal_path}: "
                              f"{journal_error}") from exc
            raise OSError(f"retirement failed; recovery required; preserve {journal_path}: {exc}") from exc
    return journal_path


def _check(root, plan, data):
    states = _state(root, plan)
    _check_parents(root, plan, data, states)
    if any(state != "destination" for state in states):
        raise ValueError("retirement is not fully applied")
    _source_binding(root, plan)
    _corrected_binding(root, plan)
    path, digest, previous = _previous(root, plan["predecessor"], plan["predecessorSha256"])
    _exact_mapping(plan, previous)
    _previous_check(root, previous, plan["predecessorMapping"])
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError("predecessor changed during successor check")


def check(root, journal, expected):
    """Verify successor content; this does not change the predecessor checker."""
    root = _root(root)
    _, data, _ = _read(root, journal, expected)
    if data["status"] != "applied" or "pending" in data or "pendingParent" in data:
        raise ValueError("retirement is not fully applied")
    _check(root, data["plan"], data)
    return data


def verify_successor(root, journal, expected, receipt):
    """Read-only verification for one explicit, digest-bound retirement.

    Normal-rebase's direct checker remains strict and is not changed by this view.
    """
    from . import normal_rebase, normal_recap

    root = _root(root)
    receipt = pathlib.Path(receipt).absolute()
    normal_recap._under(root, receipt)
    journal_path, data, raw = _read(root, journal, expected)
    if data["status"] != "applied" or "pending" in data or "pendingParent" in data:
        raise ValueError("retirement is not fully applied")
    plan = data["plan"]
    corrected_relative = plan.get("correctedReceipt", plan["sourceReceipt"])
    corrected_hash = plan.get("correctedReceiptSha256", plan["sourceReceiptSha256"])
    if receipt != _path(root, corrected_relative):
        raise ValueError("retirement is bound to another rebase receipt")
    _check(root, plan, data)
    receipt_bytes = receipt.read_bytes()
    _, _, saved = _corrected_receipt(root, corrected_relative, plan, corrected_hash)
    if receipt.read_bytes() != receipt_bytes:
        raise ValueError("corrected rebase receipt changed during verification")
    recap = normal_recap.collect(receipt)
    if recap["snapshotDiagnostics"] or recap["snapshotIdUnavailable"]:
        raise ValueError("rebase Review evidence is incomplete")
    def check_originals():
        for row in recap["rows"]:
            if row.get("supersededVersion"):
                continue
            relative = row["destination"]
            if any(relative.casefold().startswith((move["source"] + "/").casefold())
                   for move in plan["moves"]):
                raise ValueError(f"retired identity still owns a rebase original: {relative}")
            path = _path(root, relative)
            if not path.is_file() or metadata.content_sha256(path) != row["preparedSHA256"]:
                raise ValueError(f"rebase original missing or changed: {relative}")

    check_originals()
    if (receipt.read_bytes() != receipt_bytes or journal_path.read_bytes() != raw
            or any(metadata.content_sha256(pathlib.Path(path)) != digest
                   for path, digest in recap["inputs"].items())):
        raise ValueError("retirement evidence changed during verification")
    _check(root, plan, data)
    check_originals()
    if (receipt.read_bytes() != receipt_bytes or journal_path.read_bytes() != raw
            or saved["implementationSHA256"] != metadata.content_sha256(pathlib.Path(normal_rebase.__file__))
            or any(metadata.content_sha256(pathlib.Path(path)) != digest
                   for path, digest in recap["inputs"].items())):
        raise ValueError("retirement evidence changed during verification")
    return data


def recover(root, journal, expected, *, apply=False):
    """Restore intact trees without overwrites or deleting category directories."""
    root = _root(root)
    journal_path, data, _ = _read(root, journal, expected)
    if data["status"] == "recovered":
        raise ValueError("retirement is already recovered")
    plan = data["plan"]
    if not apply:
        states = _state(root, plan)
        _check_parents(root, plan, data, states, allow_pending=True)
        _check_partial(root, plan, states)
        return states
    _require_windows()
    with _locked(root, plan):
        _, data, raw = _read(root, journal, expected)
        if data["status"] == "recovered":
            raise ValueError("retirement is already recovered")
        plan = data["plan"]
        writer = _JournalWriter(journal_path, raw)
        try:
            states = _state(root, plan)
            _check_parents(root, plan, data, states, allow_pending=True)
            _check_partial(root, plan, states)
            data["status"] = "recovering"
            writer.write(data)
            for index, move in enumerate(plan["moves"]):
                _previous(root, plan["predecessor"], plan["predecessorSha256"])
                states = _state(root, plan) if "pendingParent" in data else None
                _check_parents(root, plan, data, states, allow_pending=True)
                if _move_state(root, move) == "destination":
                    data["pending"] = index
                    writer.write(data)
                    _path(root, move["destination"]).rename(_path(root, move["source"]))
                    if _move_state(root, move) != "source":
                        raise ValueError("identity changed during recovery")
                    del data["pending"]
                    writer.write(data)
            states = _state(root, plan)
            _check_parents(root, plan, data, states, allow_pending=True)
            if any(state != "source" for state in states):
                raise ValueError("recovery did not restore all folders")
            _source_binding(root, plan)
            _corrected_binding(root, plan)
            _, _, previous = _previous(root, plan["predecessor"], plan["predecessorSha256"])
            _previous_check(root, previous, {})
            data.pop("pending", None)
            pending_parent = data.pop("pendingParent", None)
            if pending_parent is not None:
                parent = _path(root, pending_parent)
                data["preservedPendingParent"] = {
                    "path": pending_parent,
                    "identity": None if _absent(parent) else _directory_identity(parent),
                    "ownership": "unknown",
                }
            data["status"] = "recovered"
            writer.write(data)
        except Exception as exc:
            data["status"] = "recovery-required"
            data["error"] = str(exc)
            try:
                writer.write(data)
            except Exception as journal_error:
                raise OSError(f"recovery and journal update failed; preserve {journal_path}: "
                              f"{journal_error}") from exc
            raise OSError(f"recovery required; preserve {journal_path}: {exc}") from exc
    return ["source"] * len(plan["moves"])
