#!/usr/bin/env python3
"""Explicit local photo housekeeping and derivative-backed reports, without matching."""
import argparse
import datetime
import hashlib
import json
import math
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/art"))
sys.path.insert(0, str(ROOT / "tools/workflows"))
import comfy_workflows as cw  # noqa: E402
import library_backup  # noqa: E402
import originals  # noqa: E402
from likeness_library import derivatives, metadata  # noqa: E402
from likeness_library.policy import load_policy  # noqa: E402
from likeness_library.sandbox import is_sandbox_working_path, require_sandbox_cache, require_sandbox_output  # noqa: E402

SETTLEMENT = ".gallery-maintenance-settlements.json"


def settled(root):
    path = pathlib.Path(root) / SETTLEMENT
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def active_batches(catalog):
    undone = {a["undoes"] for a in catalog["actions"] if a["type"] == "action-undone"}
    return sorted({a["batchId"] for a in catalog["actions"]
                   if a.get("batchId") and a["type"] != "action-undone" and a["id"] not in undone})


def undo_folders(catalog, batches, library, root):
    held = set()
    for action in catalog["actions"]:
        if action.get("batchId") not in batches:
            continue
        members = [action, action["swapPartner"]] if action.get("swapPartner") else [action]
        for member in members:
            paths = [member.get("source"), member.get("destination")]
            person = catalog["people"].get(member.get("personId"), {})
            paths.append(person.get("folder"))
            paths = [root / value for value in paths if isinstance(value, str) and value]
            if not paths:
                return set(library)
            held.update(folder for folder in library if any(
                folder == path or folder in path.parents or path in folder.parents for path in paths))
    return held


def folders(cfg, root):
    """Include Review-only identities, without recursively walking backups or archives."""
    result = set()
    for base in cw.photo_roots(cfg, root):
        candidates = [base]
        candidates += [p for p in base.iterdir() if p.is_dir() and not p.name.startswith("_")]
        if base.name == "Artists":
            candidates += [p for artist in list(candidates[1:]) for p in artist.iterdir()
                           if p.is_dir() and not p.name.startswith("_")]
        result.update(p for p in candidates if (p / "gallery").is_dir() or (p / "review").is_dir())
    return sorted(result)


def configured_names(value):
    if isinstance(value, str):
        return {pathlib.PureWindowsPath(value).name.casefold()}
    if isinstance(value, dict):
        return set().union(*(configured_names(item) for item in value.values())) if value else set()
    if isinstance(value, list):
        return set().union(*(configured_names(item) for item in value)) if value else set()
    return set()


def report_state(root, library, cache_path, policy_path):
    evidence = {"recipe": derivatives.RECIPE, "sources": {}, "manifests": {},
                "cache": derivatives.digest(cache_path) if cache_path.is_file() else None,
                "catalogue": derivatives.digest(metadata.path_for_root(root)),
                "policy": load_policy(policy_path)}
    for folder in library:
        manifest = folder / derivatives.MANIFEST
        if manifest.is_file():
            evidence["manifests"][folder.relative_to(root).as_posix()] = derivatives.digest(manifest)
        for bucket in ("gallery", "review"):
            for photo in originals.images(folder / bucket):
                evidence["sources"][photo.relative_to(root).as_posix()] = derivatives.digest(photo)
    return hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()


def run(args, cfg):
    root = pathlib.Path(args.root or cw.work_root(cfg)).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"library root does not exist: {root}")
    isolated = root != pathlib.Path(cw.work_root(cfg)).resolve()
    if isolated or is_sandbox_working_path(root):
        require_sandbox_cache(root, args.cache)
        if args.out:
            require_sandbox_output(root, args.out)
    load_policy(args.policy)
    if args.cache:
        cache_path = pathlib.Path(args.cache)
    elif root != pathlib.Path(cw.work_root(cfg)).resolve():
        raise ValueError("isolated library maintenance requires an explicit --cache FILE")
    else:
        import likeness
        cache_path = likeness.DATA / "likeness_cache.json"
    if not cache_path.is_file():
        raise ValueError(f"existing scenario cache required; refusing to create a new cache: {cache_path}")
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    catalog_path = metadata.path_for_root(root)
    catalog = metadata.load_catalog(catalog_path)
    settlements = settled(root)
    unsettled = [batch for batch in active_batches(catalog) if batch not in settlements]
    library = folders(cfg, root)
    held_folders = undo_folders(catalog, unsettled, library, root) if args.preserve_action_undo else set()
    output = pathlib.Path(args.out).resolve() if args.out else root / "_reports" / "library"
    if any(folder == location or folder in location.parents
           for folder in held_folders for location in (output, cache_path.resolve())):
        raise ValueError("report/cache writes must remain outside action-held identity trees")
    for folder in library:
        for path in [folder, *folder.parents]:
            if path == root:
                break
            if path.is_symlink() or root not in folder.resolve().parents:
                raise ValueError(f"refusing linked/escaped photo folder: {folder}")
    protected_names = configured_names(cfg)
    known = sorted({originals.prefix_of(p.name) for p in library}, key=len, reverse=True)
    renames, sources, problems = [], [], []
    for folder in library:
        if folder in held_folders:
            problems.append(f"HELD action undo inventory unchanged: {folder}")
            continue
        prefix = originals.prefix_of(folder.name)
        for bucket in ("gallery", "review"):
            photos = originals.images(folder / bucket)
            prefixes = sorted(set(known) | originals.folder_prefixes([p.name for p in photos], prefix),
                              key=len, reverse=True)
            proposals = {photo: photo.with_name(originals.standard_name(
                photo.name, prefix, prefixes, lambda p=photo: originals.content_id(p))) for photo in photos}
            counts = {}
            for final in proposals.values():
                counts[final.name.casefold()] = counts.get(final.name.casefold(), 0) + 1
            for photo in photos:
                if photo.is_symlink() or root not in photo.resolve().parents:
                    raise ValueError(f"refusing linked/escaped original: {photo}")
                final = proposals[photo]
                if counts[final.name.casefold()] > 1 or (
                        final != photo and final.exists() and final.name.casefold() != photo.name.casefold()):
                    problems.append(f"HELD name collision: {photo} -> {final.name}; original filename retained, "
                                    "derivatives maintained under that unchanged name")
                    final = photo
                sha = hashlib.sha1(photo.read_bytes()).hexdigest()
                face = cache.get("emb", {}).get(sha, {})
                box, px = face.get("box"), face.get("px", 0)
                if (not isinstance(box, (list, tuple)) or len(box) != 4
                        or not all(isinstance(value, (int, float)) and math.isfinite(value) for value in box)
                        or box[2] <= 0 or box[3] <= 0
                        or not isinstance(px, (int, float)) or not math.isfinite(px)):
                    box, px = None, 0
                sources.append((photo, final, box, px))
                if photo.name != final.name:
                    renames.append((photo, final, derivatives.digest(photo)))
    print(f"maintenance root: {root}\ncache (housekeeping reads only): {cache_path}")
    for source, target, _sha in renames:
        print(f"rename: {source} -> {target.name}")
    if unsettled:
        print("ACTIVE ACTION UNDO: " + ", ".join(unsettled))
        print("Undo first, or explicitly --settle-actions to close those undo windows. "
              "Settlement records a verified full pre-maintenance recovery snapshot; "
              "action undo will refuse settled batches, never bless changed tree hashes.")
    for problem in problems:
        print("DIAGNOSTIC: " + problem)
    pending = []
    for source, _target, box, px in sources:
        made, _messages = derivatives.maintain(source, box, px)
        pending.extend(made)
    for folder in library:
        if folder in held_folders:
            continue
        obsolete, _messages = derivatives.prune(folder, root, protected_names=protected_names)
        pending.extend(obsolete)
    mutating = bool(renames or pending)
    if args.apply and mutating and unsettled and not args.settle_actions and not args.preserve_action_undo:
        raise ValueError("maintenance blocked: active action batches must be undone or explicitly settled")
    if args.apply and mutating:
        if root != pathlib.Path(cw.work_root(cfg)).resolve() and catalog_path == metadata.CATALOG_PATH and unsettled:
            raise ValueError("isolated library cannot settle repository catalogue actions; provide its local catalogue")
        backup = library_backup.create_backup(
            root, config_path=cw.CFG_PATH,
            stamp=datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"),
            extra_sources=(("likeness-catalogue", catalog_path),))
        # Repeat the write-set guards after backup, before closing any undo window.
        if metadata.load_catalog(catalog_path) != catalog or settled(root) != settlements:
            raise ValueError("action state changed during backup; no maintenance applied")
        for source, target, sha in renames:
            if derivatives.digest(source) != sha or (
                    target.exists() and target.name.casefold() != source.name.casefold()):
                raise ValueError(f"rename state changed during backup: {source}")
        if unsettled and not args.preserve_action_undo:
            print("EXPLICIT CONSENT: closing action undo for " + ", ".join(unsettled))
            print(f"Recoverable pre-maintenance snapshot: {backup}")
            print(f'Recovery preview: cmd /c bin\\library-backup.cmd --restore "{backup}" '
                  '--destination "C:\\LibraryRecovery\\before-maintenance"')
            print("Add --apply only to materialize that recovery tree; the live library is not overwritten.")
            for batch in unsettled:
                settlements[batch] = {"backup": str(backup), "reason": "explicit gallery maintenance settlement"}
            destination = root / SETTLEMENT
            stage = destination.with_suffix(".json.pending")
            stage.write_text(json.dumps(settlements, indent=2) + "\n", encoding="utf-8")
            os.replace(stage, destination)
        for source, target, _sha in renames:
            if source.name.casefold() == target.name.casefold():
                stage = source.with_name(source.name + ".normalizing")
                source.rename(stage)
                stage.rename(target)
            else:
                source.rename(target)
    changes, diagnostics = [], list(problems)
    for source, target, box, px in sources:
        current = target if args.apply else source
        try:
            made, messages = derivatives.maintain(current, box, px, apply=args.apply)
            changes.extend(made)
            diagnostics.extend(messages)
        except (OSError, ValueError) as exc:
            diagnostics.append(f"Unprocessable {current}: {exc}")
    for folder in library:
        if folder in held_folders:
            continue
        obsolete, messages = derivatives.prune(folder, root, apply=args.apply, protected_names=protected_names)
        changes.extend(obsolete)
        diagnostics.extend(messages)
    for message in diagnostics:
        print("DIAGNOSTIC: " + message)
    print(f"{len(renames)} rename(s), {len(changes)} derivative(s) "
          f"{'processed' if args.apply else 'pending'}, {len(diagnostics)} diagnostic(s)")
    if args.check:
        reports_pending = False
        if not args.no_reports:
            out = pathlib.Path(args.out) if args.out else root / "_reports" / "library"
            state_path = out / ".gallery-maintenance-report-state.json"
            state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
            reports_pending = state.get("inputs") != report_state(root, library, cache_path, args.policy)
            for name in ("people_gallery_review.html", "people_gallery.html"):
                report = out / name
                if not report.is_file() or state.get("reports", {}).get(name) != derivatives.digest(report):
                    reports_pending = True
            if reports_pending:
                print("OUT OF SYNC: derivative-backed gallery reports need refresh")
        return int(bool(renames or changes or diagnostics or reports_pending))
    if not args.apply:
        print("Preview only: add --apply after reviewing; reports are not written.")
        return 0
    if not args.no_reports:
        from likeness_library import review_gallery
        import people_gallery
        shared = ["--root", str(root), "--cache", str(cache_path), "--no-renders"]
        if args.policy:
            shared += ["--policy", args.policy]
        if args.out:
            shared += ["--out", args.out]
        review_gallery.main(shared)
        people_gallery.main(shared)
        out = pathlib.Path(args.out) if args.out else root / "_reports" / "library"
        state = {"inputs": report_state(root, library, cache_path, args.policy),
                 "reports": {name: derivatives.digest(out / name)
                             for name in ("people_gallery_review.html", "people_gallery.html")}}
        state_path = out / ".gallery-maintenance-report-state.json"
        stage = state_path.with_suffix(".json.pending")
        stage.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        os.replace(stage, state_path)
    return 1 if diagnostics else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--dry-run", action="store_true", help="preview only (the default)")
    mode.add_argument("--check", action="store_true", help="read only; exit 1 if upkeep or diagnostics remain")
    parser.add_argument("--root")
    parser.add_argument("--cache")
    parser.add_argument("--policy")
    parser.add_argument("--out")
    parser.add_argument("--settle-actions", action="store_true",
                        help="explicitly close active action undo windows after a verified full backup")
    parser.add_argument("--preserve-action-undo", action="store_true",
                        help="leave every active action identity tree untouched; maintain other folders only")
    parser.add_argument("--no-reports", action="store_true", help="maintain files only")
    parser.add_argument("--no-renders", action="store_true", help="compatibility; renders are never loaded")
    parser.add_argument("--artists", action="store_true", help="retired: use artists-gallery.cmd for Artist pages")
    args = parser.parse_args(argv)
    if args.artists:
        parser.error("--artists no longer mixes Artists into people pages; use bin\\artists-gallery.cmd")
    if args.settle_actions and args.preserve_action_undo:
        parser.error("--settle-actions and --preserve-action-undo are mutually exclusive")
    try:
        return run(args, cw.load_cfg())
    except (OSError, ValueError) as exc:
        print(f"maintenance refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
