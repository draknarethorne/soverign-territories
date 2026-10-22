"""Clean, cast-seeded sandbox rebuild with a saved plan and reversible installation."""
import collections
import csv
import datetime
import json
import pathlib
import shutil

import numpy as np

from . import metadata
from .engine import Cache, Photo, Space
from .policy import load_policy
from .reconciliation import frozen_identity_cores, plan_reconciliation
from .sandbox import (
    RESET_CATEGORIES,
    _is_reparse_point,
    _source_files,
    require_sandbox_output,
    validate_sandbox,
)


def _write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2), encoding="utf-8")
    temporary.replace(path)


def _verify_routes(plan, source):
    sources, destinations = set(), set()
    for row in plan["photos"]:
        relative = pathlib.PurePosixPath(row["source"])
        destination = pathlib.PurePosixPath(row["destination"])
        for path in (relative, destination):
            if (
                path.is_absolute() or len(path.parts) != 4
                or any(p in ("..", ".") for p in path.parts)
                or ":" in str(path) or "\\" in str(path)
                or path.parts[2] not in ("gallery", "review")
            ):
                raise ValueError(f"unsafe rebase path: {path}")
        if relative.parts[0] not in RESET_CATEGORIES:
            raise ValueError(f"candidate outside generated categories: {relative}")
        if destination.parts[0] not in (*RESET_CATEGORIES, "Angels", "Sisters"):
            raise ValueError(f"invalid rebase destination: {destination}")
        if destination.parts[0] in ("Angels", "Sisters") and destination.parts[2] != "review":
            raise ValueError("cast candidates may only enter Review, never the cast core")
        if row["source"] in sources or row["destination"].casefold() in destinations:
            raise ValueError("duplicate source or destination in clean rebase")
        sources.add(row["source"])
        destinations.add(row["destination"].casefold())
        path = source.joinpath(*relative.parts)
        if metadata.content_sha256(path) != row["sha256"]:
            raise ValueError(f"source changed since preview: {path}")


def create_plan(layout, run, policy, api, embedder=None, *, reuse_measurements=False):
    """Flatten source photos before building any non-cast identity references."""
    source = layout["source_root"]
    cache_path = run / "likeness-cache.json"
    if cache_path.exists() and not reuse_measurements:
        raise ValueError("clean rebase requires a new run directory and empty embedding cache")
    cfg = api.cw.load_cfg()
    settings = api.settings(cfg)
    cache = Cache(cache_path)
    embed = embedder or api.Embedder()
    photos, records = [], {}
    manifest = layout["manifest_files"]
    for group, name, folder in api.cw.photo_folders(cfg, source):
        category = group.split("/", 1)[0]
        if category not in (*RESET_CATEGORIES, "Angels", "Sisters"):
            continue
        buckets = ("gallery", "review") if category in RESET_CATEGORIES else ("gallery",)
        for bucket in buckets:
            for path in api.originals.images(folder / bucket):
                relative = path.relative_to(source).as_posix()
                digest = cache.sha(path)
                if digest not in cache.emb:
                    cache.emb[digest] = embed(path) or {"faces": -1}
                photo = Photo(path, group, name, digest, cache.emb[digest])
                photos.append(photo)
                if category in RESET_CATEGORIES:
                    records[relative] = (photo, bucket, manifest[relative][1])
                if len(photos) % 25 == 0:
                    print(f"clean rebase: measured {len(photos)} photos", flush=True)
                    cache.save()
    cache.save()
    # Center once over the selected photo population, not the old folder centroids.
    cast_photos = [p for p in photos if p.group in ("Angels", "Sisters")]
    usable = [p.raw for p in photos if p.usable(settings["minFace"])]
    if not usable:
        raise ValueError("clean rebase has no usable input faces")
    mean = np.mean(usable, axis=0)
    for photo in photos:
        if photo.raw is not None:
            photo.vec = api.nz(photo.raw - mean)
    space = Space([], settings)
    space.photos = cast_photos
    space.by_key = collections.defaultdict(list)
    for photo in cast_photos:
        if photo.usable(settings["minFace"]):
            space.by_key[photo.key].append(photo)
    space.keys = sorted(space.by_key)
    catalog = json.loads(json.dumps(metadata.load_catalog()))
    for key, rows in space.by_key.items():
        anchor_patterns = next(
            (patterns for name, patterns in cfg.get("likeness", {}).get("anchors", {}).items()
             if name.casefold() == key.split("/", 1)[1].casefold()),
            [],
        )
        anchors = [
            metadata.photo_id_from_name(photo.name) for photo in rows
            if any(pattern.casefold() in photo.name.casefold() for pattern in anchor_patterns)
        ]
        anchors = [photo_id for photo_id in anchors if photo_id]
        if anchors and not any(p["folder"] == key for p in catalog["people"].values()):
            catalog["people"][f"run-anchor:{key}"] = {
                "folder": key, "identityAnchors": anchors, "protected": True,
            }
    cores, _, diagnostics = frozen_identity_cores(
        space, catalog, photo_id_fn=metadata.photo_id_from_name,
        content_sha256_fn=metadata.content_sha256, policy=policy,
    )
    if not cores or any(not key.startswith(("Angels/", "Sisters/")) for key in cores):
        raise ValueError("clean rebuild must start with Angel/Sister cores only")
    selected = api.chosen_keys(cfg)
    protected_folders = {
        person["folder"] for person in catalog["people"].values() if person.get("protected")
    }
    candidates, by_id = [], {}
    preserved, unusable = [], []
    for relative, (photo, bucket, sha256) in sorted(records.items()):
        photo_id = metadata.photo_id_from_name(photo.name)
        base = {
            "source": relative, "sha256": sha256, "photoId": photo_id,
            "oldFolder": photo.key,
        }
        protected = (
            api.cw.photo_key(photo.name) in selected
            or photo.key in protected_folders
            or catalog["photos"].get(photo_id, {}).get("protected", False)
        )
        if protected:
            preserved.append({
                **base, "destination": relative,
                "reason": "protected/workflow photo retained; excluded from candidate clustering",
            })
            continue
        if not photo_id:
            unusable.append({
                **base,
                "destination": f"{photo.key}/review/{photo.name}",
                "reason": "missing stable photo ID; held in Review, excluded from clustering",
            })
            continue
        if photo_id in by_id:
            raise ValueError(f"duplicate candidate photo ID: {relative}")
        by_id[photo_id] = base
        quality_reason = api.junk_reason(photo, settings) if hasattr(api, "junk_reason") else None
        if not photo.usable(settings["minFace"]) or quality_reason:
            unusable.append({
                **base,
                "destination": f"{photo.key}/review/{photo.name}",
                "reason": (
                    f"quality hold: {quality_reason}; excluded from matching"
                    if quality_reason else
                    "unusable face; held in Review, excluded from matching"
                ),
            })
            continue
        candidates.append({
            "photoId": photo_id, "sourceFolder": "Various", "sourceBucket": "Pool",
            "side": "Prospects", "vector": photo.vec,
        })
    print(f"clean rebase: {len(cores)} cast-only cores; {len(candidates)} flattened candidates", flush=True)
    result = plan_reconciliation(
        candidates, cores, assign=settings["assign"], margin=settings["margin"],
        cluster=policy["identityActions"]["identityClusterMinimumSimilarity"],
        minimum_cluster=settings["minCluster"], cast_merge=settings["castMerge"],
        name_factory=lambda seed, taken: api.invent_name(seed, taken),
        policy=policy,
    )
    # Historical names are display provenance only, never matching evidence.
    cluster_names = {}
    taken = {row["oldFolder"].split("/", 1)[1].casefold() for row in preserved}
    for group in sorted(result["clusters"], key=lambda g: (-len(g["photoIds"]), g["clusterId"])):
        old_names = collections.Counter(
            by_id[photo_id]["oldFolder"].split("/", 1)[1] for photo_id in group["photoIds"]
        )
        name = next(
            (name for name, _ in sorted(old_names.items(), key=lambda r: (-r[1], r[0].casefold()))
             if name.casefold() not in taken),
            None,
        )
        if name is None:
            name = api.invent_name(group["clusterId"], taken)
        taken.add(name.casefold())
        category = group["destination"].split("/", 1)[0]
        cluster_names[group["destination"]] = f"{category}/{name}"
    routed = list(preserved) + list(unusable)
    held_names = {}
    for row in result["assignments"]:
        base = by_id[row["photoId"]]
        destination = cluster_names.get(row["destination"], row["destination"])
        routed.append({
            **base, **row, "destination": f"{destination}/gallery/{pathlib.PurePosixPath(base['source']).name}",
        })
    for row in result["held"]:
        base = by_id[row["photoId"]]
        destination = row.get("reviewDestination")
        if not destination:
            no_match = (
                row.get("bestScore") is None
                or row["bestScore"] < policy["photoRouting"]["reviewMinimum"]
            )
            bucket = "gallery" if no_match else "review"
            group_id = row.get("clusterId", row["photoId"])
            if group_id not in held_names:
                name = base["oldFolder"].split("/", 1)[1]
                if name.casefold() in taken:
                    name = api.invent_name(group_id, taken)
                taken.add(name.casefold())
                held_names[group_id] = name
            destination = f"Potentials/{held_names[group_id]}/{bucket}"
        routed.append({
            **base, **row, "destination": f"{destination}/{pathlib.PurePosixPath(base['source']).name}",
        })
    vectors = {row["photoId"]: row["vector"] for row in candidates}
    for row in routed:
        if row.get("bestMatch") in cluster_names:
            row["bestMatch"] = cluster_names[row["bestMatch"]]
        vector = vectors.get(row.get("photoId"))
        if vector is None:
            continue
        ranked = sorted(
            ((float(vector @ core["vector"]), folder) for folder, core in cores.items()),
            key=lambda item: (-item[0], item[1].casefold()),
        )
        row["initialBestCast"] = ranked[0][1]
        row["initialBestCastScore"] = ranked[0][0]
        row["initialSecondCast"] = ranked[1][1] if len(ranked) > 1 else None
        row["initialCastMargin"] = ranked[0][0] - ranked[1][0] if len(ranked) > 1 else None
    if len(routed) != len(records):
        raise AssertionError("clean rebase did not account for every source candidate")
    plan = {
        "schemaVersion": 1, "mode": "clean-cast-seeded-rebuild",
        "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sourceRoot": str(source), "workingRoot": str(layout["working_root"]),
        "sourceManifestSHA256": metadata.content_sha256(layout["sandbox_root"] / "source-manifest.json"),
        "policy": policy, "settings": settings, "referenceFolders": sorted(cores),
        "embeddingCache": str(cache_path), "embeddingCacheStartedEmpty": True,
        "cacheMeasurementsReusedForReplan": reuse_measurements,
        "centeringMean": mean.tolist(), "candidateCount": len(records),
        "coreDiagnostics": diagnostics, "photos": sorted(routed, key=lambda r: r["source"]),
        "status": "preview",
    }
    _verify_routes(plan, source)
    return plan


def install_plan(layout, run, plan):
    """Stage and hash-check every candidate, retaining old categories for rollback."""
    import library_backup

    working, source = layout["working_root"], layout["source_root"]
    _verify_routes(plan, source)
    if plan["status"] != "preview":
        raise ValueError("this clean rebase plan has already been applied")
    for relative, (_, expected_hash) in layout["manifest_files"].items():
        parts = pathlib.PurePosixPath(relative).parts
        if parts[0] in ("Angels", "Sisters") and len(parts) > 2 and parts[2] == "gallery":
            path = working.joinpath(*parts)
            if not path.is_file() or metadata.content_sha256(path) != expected_hash:
                raise ValueError(f"Working cast reference differs from Source: {path}")
    library_backup.verify_backup(library_backup.latest_work_root_backup(working))
    staged, previous = run / "staged", run / "previous"
    if staged.exists() or previous.exists():
        raise ValueError("staging already exists; inspect the previous attempt before applying")
    for category in RESET_CATEGORIES:
        path = working / category
        if _is_reparse_point(path):
            raise ValueError(f"unsafe generated-category target: {path}")
        if path.exists():
            list(_source_files(path))
    staged.mkdir()
    previous.mkdir()
    for row in plan["photos"]:
        src = source.joinpath(*pathlib.PurePosixPath(row["source"]).parts)
        dest = staged.joinpath(*pathlib.PurePosixPath(row["destination"]).parts)
        if row["destination"].startswith(("Angels/", "Sisters/")):
            target = working.joinpath(*pathlib.PurePosixPath(row["destination"]).parts)
            if target.exists():
                raise ValueError(f"cast Review target already exists: {target}")
            if target.parent.resolve() != target.parent:
                raise ValueError(f"unsafe cast Review path: {target}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        if metadata.content_sha256(dest) != row["sha256"]:
            raise OSError(f"staged candidate checksum mismatch: {dest}")
    for category in RESET_CATEGORIES:
        for folder in sorted((staged / category).iterdir()) if (staged / category).exists() else ():
            gallery = folder / "gallery"
            gallery.mkdir(exist_ok=True)
            former_folders = sorted({
                row["oldFolder"] for row in plan["photos"]
                if pathlib.PurePosixPath(row["destination"]).parts[:2] == (category, folder.name)
                and row["oldFolder"].split("/", 1)[1] == folder.name
            })
            name_files = [
                path for former in former_folders
                for path in (source / pathlib.Path(former) / "gallery").glob("z_*.txt")
            ]
            if len(name_files) == 1:
                shutil.copy2(name_files[0], gallery / name_files[0].name)
                continue
            name_file = gallery / f"z_{folder.name.lower().replace(' ', '_')}.txt"
            name_file.write_text(
                f"name: {folder.name}\nClean sandbox rebuild; prior folders recorded in run.json\n",
                encoding="utf-8",
            )
    moved, installed, cast_added = [], [], []
    try:
        for category in RESET_CATEGORIES:
            target = working / category
            if target.exists():
                target.rename(previous / category)
                moved.append(category)
            if (staged / category).exists():
                (staged / category).rename(target)
                installed.append(category)
        for row in plan["photos"]:
            if not row["destination"].startswith(("Angels/", "Sisters/")):
                continue
            path = pathlib.PurePosixPath(row["destination"])
            src, dest = staged.joinpath(*path.parts), working.joinpath(*path.parts)
            dest.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dest)
            cast_added.append((dest, src))
        for row in plan["photos"]:
            target = working.joinpath(*pathlib.PurePosixPath(row["destination"]).parts)
            if metadata.content_sha256(target) != row["sha256"]:
                raise OSError(f"installed candidate checksum mismatch: {target}")
        plan["status"] = "applied"
        plan["previousCategories"] = str(previous)
        plan["previousCategoryNames"] = moved
        _write_json(run / "run.json", plan)
    except Exception:
        for dest, src in reversed(cast_added):
            dest.rename(src)
        for category in reversed(installed):
            (working / category).rename(staged / category)
        for category in reversed(moved):
            (previous / category).rename(working / category)
        raise


def undo_plan(layout, run, plan):
    """Restore saved categories and withdraw only this run's verified cast additions."""
    if plan["status"] != "applied":
        raise ValueError("only an applied clean rebase can be undone")
    working = layout["working_root"]
    previous, withdrawn = run / "previous", run / "withdrawn"
    if _is_reparse_point(previous) or not previous.is_dir():
        raise ValueError("verified prior categories are missing or unsafe")
    for category in plan["previousCategoryNames"]:
        if category not in RESET_CATEGORIES or not (previous / category).is_dir():
            raise ValueError(f"prior category is missing: {category}")
    if withdrawn.exists():
        raise ValueError("withdrawn outputs already exist; inspect the prior undo")
    cast_rows = [
        row for row in plan["photos"]
        if row["destination"].startswith(("Angels/", "Sisters/"))
    ]
    for row in cast_rows:
        path = working.joinpath(*pathlib.PurePosixPath(row["destination"]).parts)
        if metadata.content_sha256(path) != row["sha256"]:
            raise ValueError(f"cast Review addition changed; cannot undo automatically: {path}")
    for category in RESET_CATEGORIES:
        for root in (working / category, previous / category):
            if root.exists():
                list(_source_files(root))
    withdrawn.mkdir()
    moved, restored, cast_moved = [], [], []
    try:
        for row in cast_rows:
            relative = pathlib.PurePosixPath(row["destination"])
            source, target = working.joinpath(*relative.parts), withdrawn.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            source.rename(target)
            cast_moved.append((source, target))
        for category in RESET_CATEGORIES:
            if (working / category).exists():
                (working / category).rename(withdrawn / category)
                moved.append(category)
            if (previous / category).exists():
                (previous / category).rename(working / category)
                restored.append(category)
        plan["status"] = "undone"
        _write_json(run / "run.json", plan)
    except Exception:
        for category in reversed(restored):
            (working / category).rename(previous / category)
        for category in reversed(moved):
            (withdrawn / category).rename(working / category)
        for source, target in reversed(cast_moved):
            target.rename(source)
        raise


def command(args, api):
    if sum(bool(flag) for flag in (args.apply, args.check, args.dry_run, args.undo, args.replan)) > 1:
        raise ValueError("choose only one of --apply, --check, --dry-run, --undo, or --replan")
    policy = load_policy(args.policy)
    layout = validate_sandbox(args.root)
    run = require_sandbox_output(args.root, args.run_dir)
    if run == layout["working_root"] or any(
        run == layout["working_root"] / category
        or layout["working_root"] / category in run.parents
        for category in (*RESET_CATEGORIES, "Angels", "Sisters", "Artists")
    ):
        raise ValueError("run directory must be outside identity category roots")
    run.mkdir(parents=True, exist_ok=True)
    plan_path = run / "run.json"
    if plan_path.exists():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        if (plan["policy"] != policy and not args.replan) or plan["workingRoot"] != str(layout["working_root"]):
            raise ValueError("saved plan policy/root differs; use a new run directory")
        if plan["sourceManifestSHA256"] != metadata.content_sha256(layout["sandbox_root"] / "source-manifest.json"):
            raise ValueError("source manifest changed since preview")
        if args.replan:
            if (
                plan["status"] != "preview" or not plan["embeddingCacheStartedEmpty"]
                or plan["embeddingCache"] != str(run / "likeness-cache.json")
            ):
                raise ValueError("only a fresh-cache, unapplied preview can be replanned")
            _verify_routes(plan, layout["source_root"])
            original_preview = run / "initial-preview.json"
            if not original_preview.exists():
                _write_json(original_preview, plan)
            plan = create_plan(
                layout, run, policy, api, getattr(args, "embedder", None),
                reuse_measurements=True,
            )
            _write_json(plan_path, plan)
    else:
        if args.check or args.undo or args.replan:
            raise ValueError("no saved clean rebase plan exists")
        plan = create_plan(layout, run, policy, api, getattr(args, "embedder", None))
        _write_json(plan_path, plan)
    _verify_routes(plan, layout["source_root"])
    if args.apply:
        install_plan(layout, run, plan)
    if args.undo:
        undo_plan(layout, run, plan)
    if args.check and plan["status"] == "applied":
        for row in plan["photos"]:
            path = layout["working_root"].joinpath(*pathlib.PurePosixPath(row["destination"]).parts)
            if metadata.content_sha256(path) != row["sha256"]:
                raise ValueError(f"installed output changed: {path}")
    if not args.check:
        with (run / "photos.csv").open("w", encoding="utf-8-sig", newline="") as stream:
            fields = (
                "source", "destination", "photoId", "sha256", "bestMatch", "bestScore",
                "score", "initialBestCast", "initialBestCastScore", "initialSecondCast",
                "initialCastMargin", "reason",
            )
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(plan["photos"])
        summary = [
            "# Clean cast-seeded sandbox rebuild", "",
            f"Status: {plan['status']}", "",
            "All candidate photos were flattened before matching. Old names were used only after scoring.",
            f"Fresh embedding cache: {plan['embeddingCacheStartedEmpty']}",
            f"Initial reference identities: {len(plan['referenceFolders'])} (Angels/Sisters only)",
            f"Candidate photos accounted for: {plan['candidateCount']}",
            f"Policy: {plan['policy']['version']}",
            f"Candidate clustering minimum: {plan['policy']['identityActions']['identityClusterMinimumSimilarity']}",
            "",
            "Every source, destination, hash, match score, and reason is in photos.csv.",
            "The exact policy, centering mean, references, and per-photo decisions are in run.json.",
            "Review additions never enter an Angel/Sister gallery or identity core.",
            "Previous category directories are retained in previous/ after installation.",
            "",
            "## Initial reference folders", "",
        ] + [f"- {folder}" for folder in plan["referenceFolders"]]
        summary += [
            "", "## Effective thresholds", "",
            "| Rule | Value |", "| --- | --- |",
            *[
                f"| {name} display minimum | {plan['policy']['scoreBands'][name]['minimum']} |"
                for name in ("green", "yellow", "orange")
            ],
            f"| Red display band | <{plan['policy']['scoreBands']['red']['maximumExclusive']} |",
            f"| Small-group cast Review minimum | {plan['policy']['smallGroupCastReviewMinimum']} |",
            f"| High cast Review minimum | {plan['policy']['highCastSimilarityMinimum']} |",
            f"| Specific cast Review margin | {plan['policy']['photoRouting']['minimumMargin']} |",
            f"| Candidate clustering minimum | {plan['policy']['identityActions']['identityClusterMinimumSimilarity']} |",
            f"| Minimum initial cluster size | {plan['settings']['minCluster']} |",
            "", "## Actual destinations", "",
            "| Category / identity / bucket | Photos |", "| --- | ---: |",
        ] + [
            f"| {destination} | {count} |"
            for destination, count in sorted(collections.Counter(
                "/".join(pathlib.PurePosixPath(row["destination"]).parts[:3])
                for row in plan["photos"]
            ).items())
        ]
        for relative in (
            "diagnostics/diagnostics.md", "identity-core-audit.txt",
            "post-rebase-reconciliation.json",
        ):
            if (run / pathlib.Path(relative)).is_file():
                summary.append(f"\nPost-run evidence: [{relative}]({relative})")
        (run / "report.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    counts = collections.Counter(
        "/".join(pathlib.PurePosixPath(row["destination"]).parts[:3])
        for row in plan["photos"]
    )
    print(f"clean rebase {plan['status']}: {plan['candidateCount']} candidates; "
          f"{len(plan['referenceFolders'])} cast-only initial references")
    for destination, count in sorted(counts.items()):
        print(f"  {count:4} {destination}")
    print(f"per-photo audit and rollback locations: {plan_path}")
