"""Run-local cast selection reset and deterministic replacement receipts."""
import copy
import json
import math
import pathlib

from . import metadata


def manual_photo_protection(record):
    return bool(
        record.get("protected")
        and (record.get("automaticProtectionOverride") == "enabled"
             or not record.get("protectionProvenance"))
    )


def reset_plan(cfg, catalog, entries, cores, api, specification=None):
    """Resolve base and flow choices without changing their shared configuration."""
    spec = copy.deepcopy(specification or {"mode": "all"})
    mode = spec.get("mode", "all")
    if mode not in {"all", "scoped", "low-score", "none"}:
        raise ValueError("workflow reset mode must be all, scoped, low-score or none")
    slots = spec.get("slots", [])
    if mode == "scoped" and (not isinstance(slots, list) or not slots):
        raise ValueError("scoped workflow reset requires slots")
    cutoff = spec.get("maximumOwnCoreSimilarity")
    if mode == "low-score" and (
        isinstance(cutoff, bool) or not isinstance(cutoff, (int, float))
        or not math.isfinite(cutoff) or not -1 <= cutoff <= 1
    ):
        raise ValueError("low-score workflow reset requires a finite own-core cutoff")
    by_id = {}
    for relative, photo, bucket, _digest in entries:
        if bucket == "gallery":
            by_id.setdefault(metadata.photo_id_from_name(photo.name), []).append((relative, photo))
    mappings = [("base", cfg.get("photos", {}))]
    mappings += [(f"flow:{name}", flow.get("photos", {})) for name, flow in cfg.get("flows", {}).items()]
    decisions, reset_ids = [], set()
    scoped = {str(slot).casefold() for slot in slots}
    for scope, mapping in mappings:
        for slot, selected in sorted(mapping.items()):
            photo_id = metadata.photo_id_from_name(selected)
            matches = by_id.get(photo_id, [])
            if not matches:
                folders = [
                    person["folder"] for person in catalog["people"].values()
                    if person.get("folder", "").split("/", 1)[0] in ("Angels", "Sisters")
                    and person["folder"].split("/", 1)[1].casefold() == slot.casefold()
                ]
                if folders:
                    decisions.append({
                        "scope": scope, "slot": slot, "folder": folders[0], "oldPhotoId": photo_id,
                        "oldSelection": selected, "oldSource": None, "initialOwnScore": None,
                        "reset": mode != "none", "manualPhotoProtection": False,
                        "reason": "configured selection has no unique input Gallery photo; publication held",
                    })
                continue
            if len(matches) != 1:
                raise ValueError(f"ambiguous selected cast photo: {selected}")
            relative, photo = matches[0]
            score = cores.get(photo.key, {}).get("photoScores", {}).get(photo.name)
            reset = (
                mode == "all"
                or mode == "scoped" and bool({slot.casefold(), photo.key.casefold()} & scoped)
                or mode == "low-score" and (score is None or score < cutoff)
            )
            manual = manual_photo_protection(catalog["photos"].get(photo_id, {}))
            if reset and not manual:
                reset_ids.add(photo_id)
            decisions.append({
                "scope": scope, "slot": slot, "folder": photo.key, "oldPhotoId": photo_id,
                "oldSelection": selected, "oldSource": relative, "initialOwnScore": score,
                "reset": reset, "manualPhotoProtection": manual,
                "reason": "explicit manual photo protection exception" if reset and manual else
                          "selection reset; old selection and anchors are not initial core evidence" if reset else
                          "selection outside requested reset scope",
            })
    local_catalog = copy.deepcopy(catalog)
    for person in local_catalog["people"].values():
        person["identityAnchors"] = [pid for pid in person.get("identityAnchors", []) if pid not in reset_ids]
    for photo_id in reset_ids:
        record = local_catalog["photos"].get(photo_id)
        if record:
            record["protected"] = False
    return local_catalog, reset_ids, {
        "schemaVersion": 1, "policy": spec, "decisions": decisions,
        "publication": "sandbox-local receipt only; shared configuration/workspaces/inputs unchanged",
        "sharedPublicationAuthorized": False,
    }


def publication_inventory(cfg, receipt, api):
    """Inventory every LoadImage, including alternate nodes and handmade workflows."""
    inventory, files = [], {}
    workflows = api.cw
    repo_root = getattr(workflows, "WF", None)
    if repo_root is not None and pathlib.Path(repo_root).is_dir():
        for path in pathlib.Path(repo_root).rglob("*.json"):
            if "_archive" not in path.relative_to(repo_root).parts:
                files[path] = ("repository", "_curated" in path.parts)
    installer = getattr(workflows, "install_files", None)
    if callable(installer):
        for workspace in cfg.get("workspaces", {}):
            for path in installer(cfg, workspace).values():
                handmade = workflows.is_hand_made(cfg, workspace, path)
                files[path] = (workspace, handmade)
    selected_ids = {row["oldPhotoId"] for row in receipt["decisions"]}
    slots = {row["slot"].casefold() for row in receipt["decisions"]}

    def images(value, location=""):
        if isinstance(value, dict):
            if value.get("type") == "LoadImage" and value.get("widgets_values"):
                yield location, value["widgets_values"][0]
            if value.get("class_type") == "LoadImage":
                yield location, value.get("inputs", {}).get("image")
            for key, child in value.items():
                yield from images(child, f"{location}/{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                yield from images(child, f"{location}/{index}")

    for path, (scope, manual) in sorted(files.items(), key=lambda item: str(item[0]).casefold()):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (ValueError, OSError):
            inventory.append({"path": str(path), "scope": scope, "state": "unreadable; publication held"})
            continue
        references = list(images(data))
        relevant = path.name.split("_", 1)[0].casefold() in slots or any(
            isinstance(image, str) and metadata.photo_id_from_name(image) in selected_ids
            for _location, image in references
        )
        if not relevant:
            continue
        for location, image in references:
            record = {
                "path": str(path), "sha256": metadata.content_sha256(path), "scope": scope,
                "manual": manual, "node": location, "image": image,
                "requiresExplicitPublication": True,
            }
            if scope != "repository" and isinstance(image, str):
                image_path = pathlib.PurePosixPath(image.replace("\\", "/"))
                if not image_path.is_absolute() and ".." not in image_path.parts and ":" not in image:
                    input_path = workflows.input_dir(cfg, scope).joinpath(*image_path.parts)
                    record["inputPath"] = str(input_path)
                    record["inputSHA256"] = metadata.content_sha256(input_path) if input_path.is_file() else None
            inventory.append(record)
    return inventory


def finish_receipt(receipt, audit, routed):
    """Select only final Gallery measurements with independent own-core scores."""
    receipt = copy.deepcopy(receipt)
    rows = {row["source"]: row for row in routed}
    comparisons = {row["source"]: row for row in audit["rows"]}
    for decision in receipt["decisions"]:
        old = rows.get(decision["oldSource"])
        keep = (
            old and pathlib.PurePosixPath(old["destination"]).parent.as_posix() == f"{decision['folder']}/gallery"
            and not decision["reset"]
        ) or bool(decision["manualPhotoProtection"] and old and
                   pathlib.PurePosixPath(old["destination"]).parent.as_posix() == f"{decision['folder']}/gallery")
        eligible = [
            row for row in audit["rows"]
            if pathlib.PurePosixPath(row["destination"]).parent.as_posix() == f"{decision['folder']}/gallery"
            and row.get("qualityEligible", False) and not row.get("metadataStale")
            and not row.get("ambiguousPhotoId") and not row.get("rejectionHistory")
            and row.get("ownScore") is not None and math.isfinite(row["ownScore"])
        ]
        eligible.sort(key=lambda row: (-row["ownScore"], row["photoId"], row["destination"].casefold()))
        old_comparison = comparisons.get(decision["oldSource"])
        keep = bool(keep and old_comparison and old_comparison.get("qualityEligible")
                    and not old_comparison.get("metadataStale") and not old_comparison.get("ambiguousPhotoId"))
        chosen = old_comparison if keep else (eligible[0] if eligible else None)
        decision.update(
            newPhotoId=chosen["photoId"] if chosen else None,
            newSource=chosen["destination"] if chosen else None,
            newOwnScore=chosen.get("ownScore") if chosen else None,
            state="selected" if chosen else "hold",
            selectionReason="existing eligible selection retained" if keep else
                            "highest eligible final Gallery leave-one-out score; stable photo-ID ties" if chosen else
                            "no eligible final Gallery replacement; explicit publication held",
        )
    return receipt
