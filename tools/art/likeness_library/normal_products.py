"""Selected-input preparation and products using the accepted native recipe."""
import json
import pathlib
import shutil

from . import metadata, retained_preparation

WORKER_MEMORY_GIB = 3.5


def validate_workers(workers):
    if isinstance(workers, bool) or not isinstance(workers, int) or not 1 <= workers <= 3:
        raise ValueError("selected preparation workers must be an integer from 1 to 3")


def require_worker_memory(workers):
    import image_preparation

    validate_workers(workers)
    if workers > 1:
        free = image_preparation.available_memory_gb()
        required = workers * WORKER_MEMORY_GIB
        if free is None or free < required:
            raise ValueError(
                f"{workers} preparation workers require at least {required:g} GiB available memory; "
                f"observed {free if free is not None else 'unavailable'} GiB"
            )


def prepare(root, run, paths, profile, *, workers=1):
    import image_preparation

    require_worker_memory(workers)
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
            mirror, output, selected, workers=workers,
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


def relocated_origin(root, output, expected_manifest_sha256):
    """Original seal paths of a byte-identical sealed preparation copied to another Sandbox Working.

    Returns None unless the run's complete origin seal records a different
    preparation path. A relocation is accepted only in Sandbox Working, for the
    exact sealed manifest, and only at the same path relative to its Working.
    """
    from .sandbox import is_sandbox_working_path

    root = pathlib.Path(root).resolve()
    output = pathlib.Path(output).resolve()
    if len(output.parents) < 5 or root not in output.parents[4].parents:
        return None
    complete_path = output.parents[4] / "preparation-origin.complete.json"
    if not complete_path.is_file():
        return None
    try:
        complete = json.loads(complete_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"cannot read preparation origin seal: {exc}") from exc
    recorded_output = complete.get("preparationRoot")
    if recorded_output == str(output):
        return None
    if not is_sandbox_working_path(root):
        raise ValueError("relocated sealed preparation is restricted to Sandbox Working")
    if not isinstance(recorded_output, str) or not isinstance(complete.get("root"), str):
        raise ValueError("relocated preparation origin seal is incomplete")
    original_root = pathlib.PureWindowsPath(complete["root"])
    original_output = pathlib.PureWindowsPath(recorded_output)
    if (
        complete.get("manifestSHA256") != expected_manifest_sha256
        or not original_root.is_absolute() or ".." in original_root.parts
        or ".." in original_output.parts
    ):
        raise ValueError("relocated preparation origin seal does not bind this manifest")
    try:
        original_relative = original_output.relative_to(original_root)
    except ValueError as exc:
        raise ValueError("relocated preparation origin seal escapes its recorded Working") from exc
    if original_relative.as_posix() != output.relative_to(root).as_posix():
        raise ValueError("relocated preparation must keep its sealed path relative to Working")
    return {
        "originalRoot": str(original_root),
        "originalPreparationRoot": str(original_output),
        "originalMirror": str(original_output.parents[2]),
    }


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
    relocation = relocated_origin(root, output, expected_manifest_sha256) if allow_subset else None
    if relocation is None:
        data = image_preparation.verify(mirror, output)
    else:
        # Every artifact and frozen mirror input is still rehashed; only the
        # recorded mirror path differs because the sealed tree was copied.
        data = image_preparation.verify(mirror, output, recorded_root=relocation["originalMirror"])
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
        # A relocated copy's sources are its verified frozen mirror inputs; the
        # selected library binds to them only by identical content below.
        for source, checksum in (() if relocation is not None else actual.items()):
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
    if relocation is not None:
        data = {**data, "reuseRelocation": relocation}
    return output, data, native


def _released_source_lineage(catalog, source_catalog, moves):
    """Bind the original membership history to the exactly retired release moves."""
    from . import normal_admission

    selected = [move for move in moves if "releasedPhotoId" in move]
    if not selected:
        raise ValueError("released source catalogue requires marked release moves")
    bindings = []
    selected_ids = set()
    for move in selected:
        photo_id = move.get("photoId")
        if (not photo_id or move["releasedPhotoId"] != photo_id or photo_id in selected_ids
                or move.get("normalAdmission") is not True):
            raise ValueError("released source catalogue requires unique marked normal-admission moves")
        selected_ids.add(photo_id)
        bindings.append({
            "photoId": photo_id, "currentPath": move["source"], "sha256": move["sha256"],
        })
    counts = {}
    for move in moves:
        photo_id = move.get("photoId")
        counts[photo_id] = counts.get(photo_id, 0) + 1
    if any(counts[photo_id] != 1 for photo_id in selected_ids):
        raise ValueError("released photo has ambiguous publication moves")
    retired = normal_admission.retire_released_catalog(source_catalog, bindings, {
        move["photoId"]: pathlib.PurePosixPath(move["destination"]).name for move in selected
    })["catalog"]
    if retired != catalog:
        raise ValueError("released source catalogue does not match the retired staging catalogue")
    lineage = {}
    for photo_id in selected_ids:
        old = source_catalog["photos"].get(photo_id, {}).get("membership", {})
        lineage[photo_id] = set(old.get("sourcePersonIds", ()))
        if old.get("personId"):
            lineage[photo_id].add(old["personId"])
    return lineage


def stage(root, stage_root, moves, prepared, *, profile, photos, cfg, catalog, policy, archives=None, junk=None,
          red_snapshot_candidates=None, red_routing_plan=None, released_source_catalog=None):
    """Stage products; optional released_source_catalog is the caller-verified pre-retirement catalogue."""
    from . import maintenance, derivatives, normal_history
    from .normal_transaction import safe

    released_lineage = None
    if released_source_catalog is not None:
        if red_snapshot_candidates is not None or red_routing_plan is not None:
            raise ValueError("released source catalogue cannot be combined with red release staging")
        released_lineage = _released_source_lineage(catalog, released_source_catalog, moves)
    red_catalog = None
    if red_snapshot_candidates is not None:
        from . import normal_admission

        if prepared or archives or junk:
            raise ValueError("red hold staging cannot mix preparation or other dispositions")
        red_catalog = (
            normal_admission.red_release_routed_catalog(
                catalog, moves, red_snapshot_candidates, policy, red_routing_plan,
            ) if red_routing_plan is not None else
            normal_admission.red_release_hold_catalog(catalog, moves, red_snapshot_candidates, policy)
        )
        destinations = set()
        for move in moves:
            target = safe(root, move["destination"])
            if target in destinations or target.exists() or target.is_symlink():
                raise ValueError(f"red hold destination already exists or is duplicated: {target}")
            destinations.add(target)
    elif red_routing_plan is not None:
        raise ValueError("red routing staging requires saved snapshot candidates")
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

    def stage_retained(move):
        transfer = retained_preparation.plan_transfer(
            root, move["source"], move["destination"], generation=stage_root.parent.name,
        )
        if not transfer:
            return False
        retained_preparation.validate_transfers(root, [transfer])
        for artifact in transfer["files"]:
            destination = safe(stage_root, artifact["destination"])
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(safe(root, artifact["source"]), destination)
            if metadata.content_sha256(destination) != artifact["sha256"]:
                raise ValueError(f"retained preparation artifact changed during staging: {artifact['source']}")
        safe(stage_root, transfer["files"][-1]["destination"]).write_bytes(transfer["manifestAfter"].encode("utf-8"))
        safe(stage_root, transfer["detailDestination"]).write_bytes(transfer["detailAfter"].encode("utf-8"))
        return True

    def retire_derivatives(move):
        source = safe(root, move["source"])
        owner = source.parent.parent
        staged_owner = stage_root / owner.relative_to(root)
        data = derivatives.load(staged_owner if derivatives.manifest_path(staged_owner).exists() else owner)
        changed = False
        for key, entry in list(data["entries"].items()):
            if entry["source"] != source.relative_to(owner).as_posix():
                continue
            asset = owner / pathlib.PurePosixPath(key)
            if not asset.is_file() or metadata.content_sha256(asset) != entry["sha256"]:
                raise ValueError(f"selected old derivative is edited/missing; retirement refused: {asset}")
            removed[asset.relative_to(root).as_posix()] = entry["sha256"]
            del data["entries"][key]
            changed = True
        if changed:
            derivatives.save(staged_owner, data)

    archived = list((archives or {}).values())
    disposed = archived + list((junk or {}).values())
    for row in disposed:
        target = safe(stage_root, row["destination"])
        source = safe(root, row["source"])
        if safe(root, row["destination"]).exists() or target.exists():
            raise ValueError(f"disposition destination already exists: {row['destination']}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if metadata.content_sha256(target) != row["sha256"]:
            raise ValueError(f"disposition source changed during staging: {row['source']}")
        stage_retained(row)
        retire_derivatives(row)
        published.append({
            "photoId": row["photoId"], "native": row["destination"], "sha256": row["sha256"],
            "framing": {}, **({"junkDisposition": True} if row["source"] in (junk or {}) else {"duplicateArchive": True}),
        })
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
        if red_catalog is not None and checksum != move["sha256"]:
            raise ValueError(f"red hold source changed during staging: {move['source']}")
        updated_moves.append({**move, "sha256": checksum})
        if move.get("membershipOnly"):
            if move["source"] != move["destination"] or checksum != move["sha256"]:
                raise ValueError("membership-only publication cannot change native bytes or owner")
        elif move["source"] in rows:
            if evidence is None or output is None:
                raise ValueError("selected preparation evidence is missing")
            preparation_row = rows[move["source"]]
            if preparation_row["source"] != move["source"]:
                # Exact-content aliases share one prepared row; keep a distinct retained
                # set per published photo while preserving the prepared source provenance.
                preparation_row = {**preparation_row, "photoId": move["photoId"]}
            retained_preparation.stage_photo(
                stage_root, move["destination"], output, preparation_row,
                recipe={**evidence["recipe"], "normalPublicationGeneration": stage_root.parent.name},
                storage_mode="full" if profile == "full" else "lean",
            )
        elif not stage_retained(move) and profile != "fast":
            if not (red_catalog is not None and move.get("unpreparedNonVoting") is True
                    and red_routing_plan is not None
                    and move["photoId"] in red_routing_plan.get("nonVotingIds", ())
                    and pathlib.PurePosixPath(move["destination"]).parent.as_posix() == "Various/review"
                    and not retained_preparation.claims_photo(root, move["source"])):
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
    updated = red_catalog["catalog"] if red_catalog is not None else maintenance._updated_catalog(catalog, updated_moves, policy)
    archived_retirement = False
    for row in archived:
        photo_id = row["photoId"]
        if row.get("selectedPhotoId") in (None, photo_id):
            continue
        # A cross-ID identical copy leaves its owner; only its keeper keeps membership.
        if any(photo_id in person["identityAnchors"] for person in updated["people"].values()):
            raise ValueError(f"{photo_id}: anchored identical copy cannot be archived")
        record = updated["photos"].get(photo_id)
        if record is not None and record.pop("membership", None) is not None:
            archived_retirement = True
        for group in updated.get("photoGroups", {}).values():
            if photo_id in group["memberPhotoIds"] or photo_id in group["referencePhotoIds"]:
                group["memberPhotoIds"] = [pid for pid in group["memberPhotoIds"] if pid != photo_id]
                group["referencePhotoIds"] = [pid for pid in group["referencePhotoIds"] if pid != photo_id]
                archived_retirement = True
    if archived_retirement:
        metadata.validate_catalog(updated)
    if released_lineage is not None:
        for photo_id, previous in released_lineage.items():
            membership = updated["photos"].get(photo_id, {}).get("membership")
            if membership is None:
                raise ValueError(f"{photo_id}: released normal admission has no staged membership")
            membership["sourcePersonIds"] = sorted(set(membership.get("sourcePersonIds", ())) | previous)
        metadata.validate_catalog(updated)
    normal_history.stage(
        root, stage_root, disposed + [move for move in updated_moves if not move.get("membershipOnly")],
        **({"vacated": archives} if archives else {}),
    )
    for move in moves:
        source = pathlib.Path(root) / pathlib.PurePosixPath(move["source"])
        destination = pathlib.Path(root) / pathlib.PurePosixPath(move["destination"])
        if source == destination:
            continue
        retire_derivatives(move)
    metadata.save_catalog(updated, stage_root / ".likeness-library.json")
    return published, updated, removed
