"""Selected-input preparation and products using the accepted native recipe."""
import json
import pathlib
import shutil

from . import metadata, retained_preparation


def prepare(root, run, paths, profile):
    import image_preparation

    root, run = pathlib.Path(root).resolve(), pathlib.Path(run).resolve()
    mirror = run / "inputs"
    selected = []
    for source in paths:
        target = mirror / source.relative_to(root)
        checksum = metadata.content_sha256(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if metadata.content_sha256(target) != checksum:
                raise ValueError(f"normal frozen input changed: {source}")
        else:
            shutil.copy2(source, target)
        if metadata.content_sha256(target) != checksum:
            raise OSError(f"normal frozen input copy changed: {source}")
        selected.append(target)
    output = mirror / "_reports" / "preparation" / "selected"
    with image_preparation.models.offline():
        result = image_preparation.publish(
            mirror, output, selected, workers=1,
            storage_mode="full" if profile == "full" else "lean",
        )
    data = image_preparation.verify(mirror, output)
    if result:
        raise ValueError(f"selected preparation has unprocessable/assessment-failed inputs; retained report: {output}")
    from .clean_preparation import selected_path

    native = {
        row["source"]: selected_path(output, row) for row in data["photos"]
    }
    return output, data, native


def reuse_prepared(root, output, paths, profile, expected_manifest_sha256, *, allow_subset=False):
    import image_preparation

    from .clean_preparation import selected_path

    root = pathlib.Path(root).resolve()
    output = pathlib.Path(output).resolve()
    if root not in output.parents or not output.is_dir():
        raise ValueError("preview preparation is missing or outside the selected library root")
    if metadata.content_sha256(output / "manifest.json") != expected_manifest_sha256:
        raise ValueError("preview preparation manifest changed; create a new preview")
    if len(output.parents) < 3:
        raise ValueError("preview preparation path is incomplete")
    mirror = output.parents[2]
    data = image_preparation.verify(mirror, output)
    expected_mode = "full" if profile == "full" else "lean"
    if data.get("storageMode", "full") != expected_mode:
        raise ValueError("preview preparation profile differs from the requested apply")
    expected = {
        pathlib.Path(path).resolve().relative_to(root).as_posix(): metadata.content_sha256(path)
        for path in paths
    }
    actual = {row["source"]: row["sourceSha256"] for row in data["photos"]}
    if len(actual) != len(data["photos"]):
        raise ValueError("preview preparation does not bind the exact current selected source set")
    source_rows = {row["source"]: row for row in data["photos"]}
    selected_sources = {source: source for source in expected}
    aliases = {}
    if allow_subset:
        for source, checksum in actual.items():
            path = root / pathlib.PurePosixPath(source)
            if (
                path.resolve() != path or root not in path.parents
                or metadata.content_sha256(path) != checksum
            ):
                raise ValueError("reused preparation source changed or escapes the library root")
        if not expected:
            raise ValueError("preview preparation does not cover the current selected source set")
        for source, checksum in expected.items():
            if actual.get(source) == checksum:
                continue
            matches = sorted(key for key, value in actual.items() if value == checksum)
            if not matches:
                raise ValueError("preview preparation does not cover the current selected source set")
            native_hashes = {
                metadata.content_sha256(selected_path(output, source_rows[key]))
                for key in matches
            }
            if len(native_hashes) != 1:
                raise ValueError("byte-identical prepared aliases have conflicting selected native artifacts")
            selected_sources[source] = matches[0]
            aliases[source] = {
                "preparedSource": matches[0], "sourceSha256": checksum,
            }
    elif actual != expected:
        raise ValueError("preview preparation does not bind the exact current selected source set")
    native = {
        source: selected_path(output, source_rows[prepared_source])
        for source, prepared_source in selected_sources.items()
    }
    if allow_subset:
        data = {**data, "reuseSourceAliases": aliases}
    return output, data, native


def stage(root, stage_root, moves, prepared, *, profile, photos, cfg, catalog, policy):
    from . import maintenance, derivatives, normal_history

    stage_root = pathlib.Path(stage_root)
    if stage_root.exists():
        raise ValueError("normal publication staging already exists; preserve it and use recovery/new run")
    stage_root.mkdir(parents=True, exist_ok=True)
    output, evidence, selected = prepared if prepared else (None, None, {})
    rows = {row["source"]: row for row in evidence["photos"]} if evidence else {}
    for source, alias in (evidence or {}).get("reuseSourceAliases", {}).items():
        rows[source] = rows[alias["preparedSource"]]
    published = []
    measured = {metadata.photo_id_from_name(photo.name): photo for photo in photos}
    updated_moves = []
    removed = {}
    for move in moves:
        framing = {"full": "deferred", "head": "deferred"} if profile == "fast" else {
            "full": "unavailable: no usable measured face",
            "head": "unavailable: no usable measured face",
        }
        source = selected.get(move["source"], pathlib.Path(root) / pathlib.PurePosixPath(move["source"]))
        target = stage_root / pathlib.PurePosixPath(move["destination"])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        checksum = metadata.content_sha256(target)
        updated_moves.append({**move, "sha256": checksum})
        if move.get("membershipOnly"):
            if move["source"] != move["destination"] or checksum != move["sha256"]:
                raise ValueError("membership-only publication cannot change native bytes or owner")
        elif move["source"] in rows:
            retained_preparation.stage_photo(
                stage_root, move["destination"], output, rows[move["source"]],
                recipe={**evidence["recipe"], "normalPublicationGeneration": stage_root.parent.name},
                storage_mode="full" if profile == "full" else "lean",
            )
        else:
            transfer = retained_preparation.plan_transfer(
                root, move["source"], move["destination"], generation=stage_root.parent.name,
            )
            if transfer:
                retained_preparation.validate_transfers(root, [transfer])
                for artifact in transfer["files"]:
                    target_artifact = stage_root / pathlib.PurePosixPath(artifact["destination"])
                    target_artifact.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(pathlib.Path(root) / pathlib.PurePosixPath(artifact["source"]), target_artifact)
                (stage_root / pathlib.PurePosixPath(transfer["files"][-1]["destination"])).write_bytes(
                    transfer["manifestAfter"].encode("utf-8"),
                )
                (stage_root / pathlib.PurePosixPath(transfer["detailDestination"])).write_bytes(
                    transfer["detailAfter"].encode("utf-8"),
                )
            elif profile != "fast":
                raise ValueError(f"selected native has neither new preparation nor verified retained lineage: {move['source']}")
        old_folder = (pathlib.Path(root) / move["destination"]).parent.parent
        if not derivatives.manifest_path(target.parent.parent).exists():
            prior = derivatives.load(old_folder)
            if prior["entries"]:
                derivatives.save(target.parent.parent, prior)
        if profile == "fast":
            prior = derivatives.load(target.parent.parent)
            for key, entry in list(prior["entries"].items()):
                if entry["source"] != target.relative_to(target.parent.parent).as_posix():
                    continue
                asset = old_folder / pathlib.PurePosixPath(key)
                if not asset.is_file() or metadata.content_sha256(asset) != entry["sha256"]:
                    raise ValueError(f"old selected FAST product is edited/missing: {asset}")
                removed[asset.relative_to(root).as_posix()] = entry["sha256"]
                del prior["entries"][key]
            if derivatives.manifest_path(target.parent.parent).exists():
                derivatives.save(target.parent.parent, prior)
        else:
            photo = measured[move["photoId"]]
            _changes, diagnostics = derivatives.maintain(
                target, photo.box, photo.px, apply=True, faces=photo.faces,
            )
            errors = [row for row in diagnostics if not row.startswith("INFO:")]
            if errors:
                raise ValueError("selected derivative failure: " + "; ".join(errors))
            framing = {}
            for kind in ("padded", "head", "chest"):
                try:
                    derivative, _record = derivatives.verified(target, kind, photo.box)
                    framing[kind] = derivative.relative_to(stage_root).as_posix()
                except ValueError:
                    reason = derivatives.expected_unavailability(target, kind, photo.box, photo.px, photo.faces)
                    if reason is None:
                        raise
                    framing[kind] = "unavailable: " + reason
        published.append({
            "photoId": move["photoId"], "native": move["destination"], "sha256": checksum,
            "framing": framing,
        })
    updated = maintenance._updated_catalog(catalog, updated_moves, policy)
    normal_history.stage(root, stage_root, [move for move in updated_moves if not move.get("membershipOnly")])
    for move in moves:
        source = pathlib.Path(root) / pathlib.PurePosixPath(move["source"])
        destination = pathlib.Path(root) / pathlib.PurePosixPath(move["destination"])
        if source == destination:
            continue
        staged_owner = stage_root / source.parent.parent.relative_to(root)
        data = derivatives.load(staged_owner if derivatives.manifest_path(staged_owner).exists() else source.parent.parent)
        changed = False
        for key, entry in list(data["entries"].items()):
            if entry["source"] != source.relative_to(source.parent.parent).as_posix():
                continue
            asset = source.parent.parent / pathlib.PurePosixPath(key)
            if not asset.is_file() or metadata.content_sha256(asset) != entry["sha256"]:
                raise ValueError(f"selected old derivative is edited/missing; retirement refused: {asset}")
            relative = asset.relative_to(root).as_posix()
            removed[relative] = entry["sha256"]
            del data["entries"][key]
            changed = True
        if changed:
            derivatives.save(stage_root / source.parent.parent.relative_to(root), data)
    metadata.save_catalog(updated, stage_root / ".likeness-library.json")
    return published, updated, removed
