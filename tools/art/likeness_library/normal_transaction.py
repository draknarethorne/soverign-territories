"""Content-bound publication/recovery for one explicitly scoped normal batch."""
import hashlib
import json
import os
import pathlib
import shutil
import uuid

from . import metadata


def safe(root, relative):
    root = pathlib.Path(root).resolve()
    path = pathlib.PurePosixPath(relative)
    if path.is_absolute() or "\\" in relative or ":" in relative or any(
        part in ("", ".", "..") for part in relative.split("/")
    ):
        raise ValueError(f"unsafe normal transaction path: {relative}")
    target = root.joinpath(*path.parts)
    if root not in target.resolve().parents or target.resolve() != target:
        raise ValueError(f"linked/escaping normal transaction path: {target}")
    return target


def _external_target(path, allowed_roots):
    path = pathlib.Path(path)
    if not path.is_absolute() or path.resolve() != path:
        raise ValueError(f"external transaction target must be absolute and unlinked: {path}")
    roots = [pathlib.Path(root) for root in allowed_roots]
    if any(not root.is_absolute() or root.resolve() != root for root in roots):
        raise ValueError("approved external roots must be absolute and unlinked")
    if not roots or not any(root in path.parents for root in roots):
        raise ValueError(f"external transaction target is outside approved roots: {path}")
    return path


def write(path, data, *, exclusive=False):
    from .normal_import import _write_receipt

    if exclusive:
        _write_receipt(path, data, exclusive=True)
    else:
        _write_receipt(path, data)


def _swap_path(destination, token):
    if not isinstance(token, str) or len(token) != 32 or any(c not in "0123456789abcdef" for c in token):
        raise ValueError("invalid normal transaction swap token")
    return destination.with_name(f".{destination.name}.{token}.normal-swap")


def _replace(source, destination, checksum, token=None, *, exclusive=False):
    destination.parent.mkdir(parents=True, exist_ok=True)
    staged = _swap_path(destination, token or uuid.uuid4().hex)
    created = False
    try:
        with staged.open("xb") as target:
            created = True
            with source.open("rb") as original:
                shutil.copyfileobj(original, target)
        shutil.copystat(source, staged)
        if metadata.content_sha256(staged) != checksum:
            raise OSError(f"normal transaction copy changed: {source}")
        if exclusive:
            os.link(staged, destination)
        else:
            os.replace(staged, destination)
    finally:
        if created and staged.exists():
            staged.unlink()


def _present(path):
    return path.exists() or path.is_symlink()


def _retired_states(root, data):
    """Current location ("source"/"retired") of each journalled emptied-folder retirement.

    A folder recorded as retired, or one whose rename was pending, must be in
    exactly one location; any other row must still be at its source with the
    retired destination absent. Ambiguity is refused for inspection.
    """
    states = []
    for index, row in enumerate(data.get("retiredFolders", ())):
        source, destination = safe(root, row["source"]), safe(root, row["destination"])
        at_source, at_destination = _present(source), _present(destination)
        if row.get("state") == "retired" or index in (
            data.get("pendingFolderRetirement"), data.get("pendingFolderRestore"),
        ):
            if at_source == at_destination:
                raise ValueError(f"ambiguous retired folder locations; preserve and inspect: {row['source']}")
            states.append("retired" if at_destination else "source")
        else:
            if at_destination:
                raise ValueError(f"unexpected retired folder destination; preserve and inspect: {row['destination']}")
            states.append("source")
    return states


def located(data, relative, states=None):
    """Working-relative current path of a journalled file, following retired folders."""
    rows = data.get("retiredFolders", ())
    if states is None:
        states = ["retired" if row.get("state") == "retired" else "source" for row in rows]
    for row, state in zip(rows, states):
        prefix = row["source"] + "/"
        if state == "retired" and relative.casefold().startswith(prefix.casefold()):
            return row["destination"] + "/" + relative[len(prefix):]
    return relative


def _check_retired_inventory(root, row, location):
    from .empty_retirement import _inventory

    folder = safe(root, row[location])
    if not folder.is_dir() or _inventory(folder) != row["entries"]:
        raise ValueError(f"retired folder content changed; preserve and inspect: {row[location]}")


def verify(root, journal, *, applied=True, allowed_external_roots=()):
    if pathlib.Path(root).resolve() not in pathlib.Path(journal).resolve().parents:
        raise ValueError("normal publication journal must stay inside its library")
    try:
        data = json.loads(pathlib.Path(journal).read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"normal publication journal is incomplete or invalid; preserve and inspect: {journal}") from exc
    if data.get("kind") != "normal-publication" or data.get("root") != str(pathlib.Path(root).resolve()):
        raise ValueError("normal publication journal is bound to another root or unsupported")
    if applied and data["status"] != "applied":
        raise ValueError(f"normal publication is {data['status']}, not applied")
    states = _retired_states(pathlib.Path(root).resolve(), data) if applied else None
    if applied:
        for row, state in zip(data.get("retiredFolders", ()), states):
            if row.get("state") != "retired" or state != "retired":
                raise ValueError(f"emptied identity folder is not at its retired location: {row['source']}")
            if not safe(root, row["destination"]).is_dir():
                raise ValueError(f"retired identity folder is missing: {row['destination']}")
    for relative, expected in data["after"].items():
        path = safe(root, located(data, relative, states))
        if applied and (not path.is_file() or metadata.content_sha256(path) != expected):
            raise ValueError(f"normal published content changed: {relative}")
    for path, state in data.get("externalAfter", {}).items():
        target = _external_target(path, allowed_external_roots)
        if applied:
            if state["sha256"] is None:
                if target.exists() or target.is_symlink():
                    raise ValueError(f"external removed file reappeared: {target}")
            elif not target.is_file() or metadata.content_sha256(target) != state["sha256"]:
                raise ValueError(f"external published content changed: {target}")
    if applied:
        for relative in data["removed"]:
            if safe(root, located(data, relative, states)).exists():
                raise ValueError(f"normal removed source reappeared: {relative}")
    return data


def _restore(root, data, allowed_external_roots=(), *, apply=True, journal=None):
    if "pendingFinalizer" in data:
        raise ValueError("normal recovery refuses interrupted viewer finalization; preserve and inspect its report directories")
    backup = pathlib.Path(data["backup"])
    manifest_bytes = (backup / "manifest.json").read_bytes()
    if ("backupManifestSHA256" in data
            and hashlib.sha256(manifest_bytes).hexdigest() != data["backupManifestSHA256"]):
        raise ValueError("normal recovery snapshot manifest changed; preserve and inspect")
    manifest = json.loads(manifest_bytes)
    before = {entry["source"]: entry for entry in manifest["entries"]}
    for entry in before.values():
        archived = backup / pathlib.PurePosixPath(entry["backup"])
        if not archived.is_file() or metadata.content_sha256(archived) != entry["sha256"]:
            raise ValueError(f"normal recovery snapshot changed: {archived}")
    before_relative, external_before = {}, {}
    for source, entry in before.items():
        path = pathlib.Path(source)
        if root in path.parents:
            before_relative[path.relative_to(root).as_posix()] = entry
        else:
            _external_target(path, allowed_external_roots)
            external_before[str(path)] = entry
    external = data.get("externalAfter", {})
    if set(external_before) - set(external):
        raise ValueError("normal recovery snapshot contains unexpected external paths")
    states = _retired_states(root, data)
    for row, state in zip(data.get("retiredFolders", ()), states):
        if "entries" in row and row.get("state") != "restored":
            _check_retired_inventory(root, row, "destination" if state == "retired" else "source")
    token = data.get("swapToken")
    pending = data.get("pendingExclusive")
    if pending is not None:
        target = safe(root, pending)
        if target.exists() or target.is_symlink():
            raise ValueError(f"normal recovery refuses ambiguous exclusive target; preserve and inspect: {target}")
    pending_external = data.get("pendingExternalExclusive")
    if pending_external is not None:
        target = _external_target(pending_external, allowed_external_roots)
        if target.exists() or target.is_symlink():
            raise ValueError(f"normal recovery refuses ambiguous external target; preserve and inspect: {target}")
    pending_restore = data.get("pendingRestoreExclusive")
    if pending_restore is not None:
        if not isinstance(pending_restore, dict) or set(pending_restore) not in ({"relative"}, {"external"}):
            raise ValueError("normal recovery has an invalid pending exclusive restoration")
        target = (safe(root, pending_restore["relative"]) if "relative" in pending_restore else
                  _external_target(pending_restore["external"], allowed_external_roots))
        if target.exists() or target.is_symlink():
            raise ValueError(f"normal recovery refuses ambiguous restored target; preserve and inspect: {target}")
    if token is not None:
        targets = [safe(root, located(data, relative, states))
                   for relative in set(before_relative) | set(data["after"])]
        targets.extend(_external_target(path, allowed_external_roots) for path in external)
        for target in targets:
            staged = _swap_path(target, token)
            if staged.exists() or staged.is_symlink():
                raise ValueError(f"normal recovery refuses interrupted swap; preserve and inspect: {staged}")
    absent_before_restore = set()
    for relative in set(before_relative) | set(data["after"]):
        target = safe(root, located(data, relative, states))
        if target.exists():
            accepted = {data["after"].get(relative)}
            if relative in before_relative:
                accepted.add(before_relative[relative]["sha256"])
            if not target.is_file() or metadata.content_sha256(target) not in accepted:
                raise ValueError(f"normal recovery refuses unexpected newer content: {relative}")
        elif relative in before_relative:
            absent_before_restore.add(relative)
    absent_external_before_restore = set()
    for path, state in external.items():
        target = _external_target(path, allowed_external_roots)
        entry = external_before.get(str(target))
        if (entry["sha256"] if entry else None) != state["beforeSha256"]:
            raise ValueError(f"external recovery snapshot differs from journal: {target}")
        if target.exists():
            if not target.is_file() or metadata.content_sha256(target) not in {
                state["beforeSha256"], state["sha256"],
            }:
                raise ValueError(f"external recovery refuses unexpected newer content: {target}")
        elif entry and state["sha256"] is not None:
            raise ValueError(f"external recovery refuses missing existing file: {target}")
        elif entry:
            absent_external_before_restore.add(path)
    if not apply:
        return
    if journal is None:
        raise ValueError("normal recovery requires a journal for exclusive restoration")
    if pending_restore is not None:
        del data["pendingRestoreExclusive"]
        write(journal, data)
    # Return emptied identity folders first (reverse order) so every file
    # restoration below targets its original, pre-publication path.
    rows = data.get("retiredFolders", ())
    for index in reversed(range(len(rows))):
        row = rows[index]
        if states[index] == "retired":
            data["pendingFolderRestore"] = index
            write(journal, data)
            source = safe(root, row["source"])
            if _present(source):
                raise ValueError(f"normal recovery refuses to overwrite a reappeared folder: {row['source']}")
            safe(root, row["destination"]).rename(source)
            _check_retired_inventory(root, row, "source")
        if "entries" in row and row.get("state") != "restored":
            row["state"] = "restored"
        data.pop("pendingFolderRestore", None)
        if data.get("pendingFolderRetirement") == index:
            del data["pendingFolderRetirement"]
        write(journal, data)

    def restore_file(source, target, checksum, exclusive, binding):
        if exclusive:
            data["pendingRestoreExclusive"] = binding
            write(journal, data)
        _replace(source, target, checksum, token, exclusive=exclusive)
        if exclusive:
            del data["pendingRestoreExclusive"]
            write(journal, data)

    for relative, entry in before_relative.items():
        target = safe(root, relative)
        if relative not in absent_before_restore:
            accepted = {entry["sha256"], data["after"].get(relative)}
            if not target.is_file() or metadata.content_sha256(target) not in accepted:
                raise ValueError(f"normal recovery refuses changed content during restoration: {relative}")
        restore_file(
            backup / pathlib.PurePosixPath(entry["backup"]),
            target, entry["sha256"],
            relative in absent_before_restore, {"relative": relative},
        )
        if relative in data.get("beforeModifiedNs", {}):
            target = safe(root, relative)
            os.utime(target, ns=(target.stat().st_atime_ns, data["beforeModifiedNs"][relative]))
    for relative, expected in data["after"].items():
        if relative not in before_relative:
            target = safe(root, relative)
            if target.exists():
                if metadata.content_sha256(target) != expected:
                    raise ValueError(f"normal recovery refuses changed generated file: {relative}")
                target.unlink()
    for path, state in external.items():
        target = _external_target(path, allowed_external_roots)
        entry = external_before.get(str(target))
        if target.exists() and metadata.content_sha256(target) not in {
            state["beforeSha256"], state["sha256"],
        }:
            raise ValueError(f"external recovery refuses changed content: {target}")
        if entry:
            if target.exists() and not target.is_file():
                raise ValueError(f"external recovery refuses missing existing file: {target}")
            restore_file(
                backup / pathlib.PurePosixPath(entry["backup"]), target, entry["sha256"],
                path in absent_external_before_restore, {"external": str(target)},
            )
        elif target.exists():
            target.unlink()


def recover(root, journal, *, apply=False, allowed_external_roots=()):
    data = verify(root, journal, applied=False, allowed_external_roots=allowed_external_roots)
    if data["status"] not in ("applied", "publishing", "rollback-failed", "rolled-back", "recovering"):
        raise ValueError(f"normal transaction state cannot be recovered: {data['status']}")
    if data["status"] == "applied":
        verify(root, journal, allowed_external_roots=allowed_external_roots)
    _restore(pathlib.Path(root).resolve(), data, allowed_external_roots, apply=False)
    if apply:
        data["status"] = "recovering"
        write(journal, data)
        _restore(pathlib.Path(root).resolve(), data, allowed_external_roots, journal=journal)
        data["status"] = "undone"
        write(journal, data)
    return data


def publish(root, stage, source_relatives, *, journal, bindings, profile, run_id, expected_sources=None,
            expected_modified_ns=None,
            preserved_sources=None, finalizer=None, report_directories=(),
            external_updates=(), allowed_external_roots=(), exclusive_targets=(), retire_folders=()):
    """Publish one staged batch; optionally retire emptied identity folders in the same journal.

    ``retire_folders`` rows (``source``/``destination`` Working-relative
    folders) are renamed intact after every file publication and removal and
    before viewer finalization. Each rename is journalled with its exact
    inventory so recovery restores the folder before restoring files; a
    remaining Gallery/Review original or an existing destination stops the run.
    Nothing is deleted.
    """
    from tools.art import library_backup

    root, stage = pathlib.Path(root).resolve(), pathlib.Path(stage).resolve()
    source_relatives = tuple(source_relatives)
    if root not in stage.parents:
        raise ValueError("normal publication staging must stay within its library")
    journal = pathlib.Path(journal).absolute()
    if root not in journal.parents or journal.resolve() != journal:
        raise ValueError("normal publication journal must be an unlinked path inside its library")
    if journal.exists() or journal.is_symlink():
        raise ValueError(f"normal publication journal already exists; preserve and inspect: {journal}")
    external = {}
    for update in external_updates:
        target = _external_target(update["target"], allowed_external_roots)
        deleting = update.get("delete") is True
        staged = None if deleting else pathlib.Path(update["staged"]).resolve()
        if (root in target.parents or (staged is not None
                and (stage.parent not in staged.parents or stage in staged.parents))):
            raise ValueError("external transaction staging or target overlaps library publication")
        if (str(target) in external or "beforeSha256" not in update
                or (deleting and ("staged" in update or update["beforeSha256"] is None))
                or (not deleting and (staged is None or not staged.is_file()))):
            raise ValueError("external transaction requires unique targets, staged bytes and before hashes")
        if not target.parent.is_dir():
            raise ValueError(f"external target parent does not exist: {target.parent}")
        before_hash = update["beforeSha256"]
        if target.exists():
            if not target.is_file() or metadata.content_sha256(target) != before_hash:
                raise ValueError(f"external target differs from preview: {target}")
        elif before_hash is not None:
            raise ValueError(f"external target is missing: {target}")
        external[str(target)] = {
            "staged": staged, "sha256": None if deleting else metadata.content_sha256(staged),
            "beforeSha256": before_hash,
        }
    targets = {
        path.relative_to(stage).as_posix(): metadata.content_sha256(path)
        for path in stage.rglob("*") if path.is_file()
    }
    exclusive = set(exclusive_targets)
    if not exclusive.issubset(targets):
        raise ValueError("exclusive publication targets must be staged files")
    for relative in exclusive:
        target = safe(root, relative)
        if target.exists() or target.is_symlink():
            raise ValueError(f"exclusive publication target already exists: {relative}")
    if any(safe(root, relative).exists() for relative in targets if relative.startswith("_duplicates/")):
        raise ValueError("normal duplicate archive target already exists")
    report_roots = [safe(root, relative) for relative in report_directories]
    journal_relative = journal.relative_to(root).as_posix()
    if (journal_relative in set(targets) | set(source_relatives) | set(preserved_sources or {})
            or stage == journal or stage in journal.parents
            or any(directory == journal or directory in journal.parents for directory in report_roots)):
        raise ValueError("normal publication journal overlaps transaction inputs or outputs")
    retirements = []
    for row in retire_folders:
        source_relative, destination_relative = row["source"], row["destination"]
        parts = source_relative.split("/") if isinstance(source_relative, str) else []
        if len(parts) != 2 or parts[0] not in ("Models", "Prospects", "Potentials"):
            raise ValueError(f"only emptied non-cast identity folders can be retired: {source_relative}")
        source, destination = safe(root, source_relative), safe(root, destination_relative)
        if not source.is_dir() or source.is_symlink():
            raise ValueError(f"emptied identity folder is missing: {source_relative}")
        if _present(destination):
            raise ValueError(f"retired destination already exists; refusing to overwrite: {destination_relative}")
        claimed = [item[key].casefold() for item in retirements for key in ("source", "destination")]
        if any(path == mine or path.startswith(mine + "/") or mine.startswith(path + "/")
               for mine in (source_relative.casefold(), destination_relative.casefold()) for path in claimed):
            raise ValueError(f"overlapping emptied folder retirements: {source_relative}")
        if any(path == folder or folder in path.parents
               for path in (journal, stage, *report_roots) for folder in (source, destination)):
            raise ValueError(f"emptied folder retirement overlaps publication evidence: {source_relative}")
        if any(relative.casefold().startswith(destination_relative.casefold() + "/") for relative in targets):
            raise ValueError(f"staged publication writes into a retired destination: {destination_relative}")
        retirements.append({"source": source_relative, "destination": destination_relative, "state": "planned"})
    report_before = {
        path.relative_to(root).as_posix()
        for directory in report_roots if directory.exists()
        for path in directory.rglob("*") if path.is_file()
    }
    before_paths = set(source_relatives) | set(preserved_sources or {}) | report_before | {
        relative for relative in targets if safe(root, relative).exists()
    }
    before = [(f"file-{index:04d}", safe(root, relative)) for index, relative in enumerate(sorted(before_paths))]
    before.extend(
        (f"external-{index:04d}", pathlib.Path(path))
        for index, path in enumerate(sorted(external)) if pathlib.Path(path).is_file()
    )
    def check_modified():
        for relative, modified_ns in (expected_modified_ns or {}).items():
            if safe(root, relative).stat().st_mtime_ns != modified_ns:
                raise ValueError(f"normal collision date changed before publication: {relative}")

    check_modified()
    for relative, checksum in {**(expected_sources or {}), **(preserved_sources or {})}.items():
        if metadata.content_sha256(safe(root, relative)) != checksum:
            raise ValueError(f"normal frozen source changed before snapshot: {relative}")
    backup = library_backup.create_backup(root, apply=True, scoped_sources=before)
    manifest_path = pathlib.Path(backup) / "manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    snapshot = json.loads(manifest_bytes)
    frozen_sources = {entry["source"]: entry["sha256"] for entry in snapshot["entries"]}
    for source, checksum in frozen_sources.items():
        if metadata.content_sha256(pathlib.Path(source)) != checksum:
            raise ValueError(f"normal source changed after snapshot: {source}")
    for path, state in external.items():
        if frozen_sources.get(path) != state["beforeSha256"]:
            raise ValueError(f"external snapshot differs from preview: {path}")
        if state["beforeSha256"] is None and pathlib.Path(path).exists():
            raise ValueError(f"external target appeared after preview: {path}")
    check_modified()
    if metadata.content_sha256(manifest_path) != manifest_hash:
        raise ValueError("normal snapshot manifest changed before publication")
    data = {
        "schemaVersion": 1, "kind": "normal-publication", "status": "publishing",
        "root": str(root), "runId": run_id, "profile": profile, "bindings": bindings,
        "swapToken": uuid.uuid4().hex,
        "backup": str(backup), "backupManifestSHA256": manifest_hash,
        "after": {**targets, **(preserved_sources or {})},
        "removed": sorted(set(source_relatives) - set(targets)),
        **({"externalAfter": {
            path: {"sha256": state["sha256"], "beforeSha256": state["beforeSha256"]}
            for path, state in external.items()
        }} if external else {}),
        **({"beforeModifiedNs": {relative: expected_modified_ns[relative] for relative in before_paths
                                if relative in expected_modified_ns}} if expected_modified_ns else {}),
        **({"retiredFolders": retirements} if retirements else {}),
    }
    write(journal, data, exclusive=True)
    try:
        for relative, checksum in targets.items():
            target = safe(root, relative)
            if target.exists() and not target.is_file():
                raise ValueError(f"normal target is not a file during publication: {relative}")
            current = metadata.content_sha256(target) if target.is_file() else None
            if current != frozen_sources.get(str(target)):
                raise ValueError(f"normal target changed during publication: {relative}")
            if relative in exclusive:
                data["pendingExclusive"] = relative
                write(journal, data)
                _replace(safe(stage, relative), target, checksum, data["swapToken"], exclusive=True)
                del data["pendingExclusive"]
                write(journal, data)
            else:
                _replace(safe(stage, relative), target, checksum, data["swapToken"])
        for relative in data["removed"]:
            if metadata.content_sha256(safe(root, relative)) != frozen_sources[str(safe(root, relative))]:
                raise ValueError(f"normal source changed during publication: {relative}")
            safe(root, relative).unlink()
        for path, state in external.items():
            target = _external_target(path, allowed_external_roots)
            current = metadata.content_sha256(target) if target.is_file() else None
            if current != state["beforeSha256"]:
                raise ValueError(f"external target changed during publication: {target}")
            if state["sha256"] is None:
                target.unlink()
            elif state["beforeSha256"] is None:
                data["pendingExternalExclusive"] = path
                write(journal, data)
                _replace(state["staged"], target, state["sha256"], data["swapToken"], exclusive=True)
                del data["pendingExternalExclusive"]
                write(journal, data)
            else:
                _replace(state["staged"], target, state["sha256"], data["swapToken"])
        for index, row in enumerate(data.get("retiredFolders", ())):
            from .empty_retirement import _empty, _inventory

            source, destination = safe(root, row["source"]), safe(root, row["destination"])
            entries = _inventory(source)
            _empty(entries)
            if _present(destination):
                raise ValueError(f"retired destination appeared during publication: {row['destination']}")
            missing = [parent for parent in destination.parents if root in parent.parents and not parent.exists()]
            for parent in reversed(missing):
                parent.mkdir()
                data.setdefault("createdFolderParents", []).append(parent.relative_to(root).as_posix())
            row["entries"] = entries
            data["pendingFolderRetirement"] = index
            write(journal, data)
            source.rename(destination)
            _check_retired_inventory(root, row, "destination")
            row["state"] = "retired"
            del data["pendingFolderRetirement"]
            write(journal, data)
        if finalizer is not None:
            data["pendingFinalizer"] = list(report_directories)
            write(journal, data)
            try:
                data["viewerPaths"] = finalizer()
            finally:
                report_after = {
                    path.relative_to(root).as_posix(): metadata.content_sha256(path)
                    for directory in report_roots if directory.exists()
                    for path in directory.rglob("*") if path.is_file()
                }
                data["after"].update(report_after)
                data["removed"] = sorted(set(data["removed"]) | (report_before - set(report_after)))
                del data["pendingFinalizer"]
                write(journal, data)
        data["status"] = "applied"
        write(journal, data)
        verify(root, journal, allowed_external_roots=allowed_external_roots)
    except Exception as exc:
        try:
            _restore(root, data, allowed_external_roots, journal=journal)
            data["status"] = "rolled-back"
        except Exception as rollback:
            data["status"] = "rollback-failed"
            data["rollbackError"] = str(rollback)
        data["error"] = str(exc)
        write(journal, data)
        raise OSError(f"normal publication failed ({data['status']}): {exc}; journal={journal}") from exc
    return pathlib.Path(journal)
