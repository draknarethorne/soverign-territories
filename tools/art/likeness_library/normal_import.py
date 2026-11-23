"""Stable, profile-based intake for selected arrivals in Various.

This path plans only selected pool arrivals against the full eligible identity
snapshot. Whole-library reassessment remains an explicit rebase operation.
"""

import argparse
import collections
import datetime
import hashlib
import json
import pathlib
import re
import shutil
import sys
import uuid


ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
IDENTITY_ROOTS = frozenset({"Angels", "Sisters", "Models", "Prospects", "Potentials"})


def _arrival_name(path, originals, metadata):
    if metadata.photo_id_from_name(path.name):
        return path.name
    digest = originals.content_id(path)
    name = originals.standard_name(path.name, "various", digest=digest)
    if not metadata.photo_id_from_name(name):
        name = originals.standard_name("incoming" + path.suffix, "various", digest=digest)
    if not metadata.photo_id_from_name(name):
        raise ValueError(f"cannot establish a stable ID for incoming original: {path.name}")
    return name


def _arrival_versions(root, photo_ids, originals, metadata, *, classify=None, aliases=None):
    from tools.art import duplicates
    from tools.art.likeness_library import normal_transaction, retained_preparation

    root = pathlib.Path(root).resolve()
    pool = root / "Various" / "gallery"
    paths = originals.images(pool)
    by_id = {}
    for path in paths:
        normal_transaction.safe(root, path.relative_to(root).as_posix())
        name = _arrival_name(path, originals, metadata)
        photo_id = metadata.photo_id_from_name(name)
        by_id.setdefault(photo_id, []).append((path, name))
    requested = set(photo_ids or ())
    missing = sorted(requested - set(by_id))
    if missing:
        raise ValueError("selected photo IDs are not in Various/gallery: " + ", ".join(missing))
    selected = requested or set(by_id)
    retained_sources = classify(selected) if classify else {}
    result, older = [], []
    for photo_id in sorted(selected):
        rows = by_id[photo_id]
        originals_rows = []
        prepared_rows = []
        for path, name in rows:
            if retained_preparation.claims_photo(root, path):
                link = retained_preparation.verify_link(root, path, photo_id)
                if link is None:
                    raise ValueError(f"invalid or ambiguous retained incoming lineage for {photo_id}: {path}")
                prepared_rows.append((path, link))
            else:
                originals_rows.append((path, name))
        retained = retained_sources.get(photo_id)
        if retained:
            kept = []
            for path, name in originals_rows:
                digest = metadata.content_sha256(path)
                if digest == retained["sourceSha256"]:
                    manifest = retained["link"]["manifest"]
                    aliases.append({
                        "photoId": photo_id, "source": path.relative_to(root).as_posix(),
                        "sha256": digest, "owner": retained["owner"],
                        "ownerSha256": retained["ownerSha256"],
                        "manifest": manifest,
                        "manifestSha256": metadata.content_sha256(normal_transaction.safe(root, manifest)),
                    })
                else:
                    kept.append((path, name))
            originals_rows = kept
        if photo_id.startswith("photo:pic_"):
            original_hashes = {
                metadata.content_sha256(path) for path, _name in originals_rows
            } | {link["sourceSha256"] for _path, link in prepared_rows}
            if len(original_hashes) > 1:
                raise ValueError(f"short content ID collision for {photo_id}; compare full original SHA-256 values")
        if not originals_rows:
            if retained and not prepared_rows:
                continue
            raise ValueError(
                f"prepared incoming {photo_id} has no selected genuine original; "
                "restore its exact original before selecting a version"
            )
        entries = [(path, "Various", pool.parent, "gallery") for path, _name in originals_rows]
        selection = duplicates.select_incoming_version(entries)
        if selection["selected"] is None:
            raise ValueError(f"ambiguous incoming versions for {photo_id}; resolve the newest-time tie explicitly")
        chosen = selection["selected"][0]
        result.append(next(row for row in originals_rows if row[0] == chosen))
        older.extend((photo_id, path, "original", None) for path, _name in originals_rows if path != chosen)
        older.extend((photo_id, path, "prepared", {
            "sourceSha256": link["sourceSha256"],
            "manifest": link["manifest"],
            "manifestSha256": metadata.content_sha256(normal_transaction.safe(root, link["manifest"])),
        }) for path, link in prepared_rows)
    return result, older


def _intake_selection(api, root, photo_ids, originals, metadata, cfg, catalog):
    from tools.art.likeness_library import retained_preparation

    root = pathlib.Path(root).resolve()
    owners = collections.defaultdict(list)
    aliases = []

    def classify(selected):
        for group, _name, folder in api.cw.photo_folders(cfg, root):
            if group in IDENTITY_ROOTS:
                for path in originals.images(folder / "gallery"):
                    photo_id = metadata.photo_id_from_name(path.name)
                    if photo_id in selected:
                        owners[photo_id].append(path)
        retained = {}
        anchors = _catalog_evidence(catalog)["anchors"]
        for photo_id, paths in owners.items():
            if len(paths) != 1:
                raise ValueError(f"same-photo update has multiple current owners: {photo_id}")
            owner = paths[0]
            if not retained_preparation.claims_photo(root, owner):
                continue
            link = retained_preparation.verify_link(root, owner, photo_id)
            if link is None:
                raise ValueError(f"same-photo update {photo_id} has invalid retained history: {owner}")
            owner_hash = metadata.content_sha256(owner)
            record = catalog.get("photos", {}).get(photo_id, {})
            anchor_owners = {
                catalog.get("people", {}).get(person_id, {}).get("folder") or person_id
                for person_id in anchors.get(photo_id, ())
            }
            owner_folder = owner.parent.parent.relative_to(root).as_posix()
            if (record.get("contentSha256") == owner_hash
                    and anchor_owners.issubset({owner_folder})
                    and link["sourceSha256"] != owner_hash):
                retained[photo_id] = {
                    "sourceSha256": link["sourceSha256"],
                    "owner": owner.relative_to(root).as_posix(),
                    "ownerSha256": owner_hash,
                    "link": link,
                }
        return retained

    selected, older = _arrival_versions(
        root, photo_ids, originals, metadata, classify=classify, aliases=aliases,
    )
    return selected, older, aliases, owners


def _selected_arrivals(root, photo_ids, originals, metadata):
    return [path for path, _name in _arrival_versions(root, photo_ids, originals, metadata)[0]]


def _older_rows(root, older, metadata):
    return [
        {"photoId": photo_id, "source": path.relative_to(root).as_posix(),
         "sha256": metadata.content_sha256(path), "kind": kind, "lineage": lineage}
        for photo_id, path, kind, lineage in older
    ]


def _diagnose_membership(catalog, space, metadata):
    """Expose existing non-reference flags without promoting or rewriting them."""
    diagnostics = []
    seen = set()
    evidence = _catalog_evidence(catalog)
    for photo in space.photos:
        photo_id = metadata.photo_id_from_name(photo.name)
        record = catalog.get("photos", {}).get(photo_id, {})
        if not photo_id or photo_id in seen:
            continue
        seen.add(photo_id)
        details = _membership_details(catalog, photo_id, photo.key, record, evidence)
        if details is None:
            continue
        diagnostics.append(details)
    return diagnostics


def _catalog_evidence(catalog):
    anchors = collections.defaultdict(list)
    for person_id, person in catalog.get("people", {}).items():
        for photo_id in person.get("identityAnchors", ()):
            anchors[photo_id].append(person_id)
    actions = collections.defaultdict(list)
    for action in catalog.get("actions", ()):
        row = {
            key: action[key] for key in ("id", "timestamp", "actor", "type", "reason", "contentSha256")
            if key in action
        }
        for photo_id in action.get("photoIds", ()):
            actions[photo_id].append(row)
    return {"anchors": anchors, "actions": actions}


def _membership_details(catalog, photo_id, folder, record, evidence=None):
    membership = record.get("membership") or {}
    evidence = evidence or _catalog_evidence(catalog)
    anchors = sorted(evidence["anchors"].get(photo_id, ()))
    actions = evidence["actions"].get(photo_id, ())
    rejected_ids = list(record.get("rejectedPersonIds", ()))
    protected = bool(record.get("protected"))
    protection_provenance = record.get("protectionProvenance")
    has_membership_hold = membership and (
        membership.get("status") != "supported" or membership.get("coreUse") is not True
    )
    if not (
        has_membership_hold or protected or protection_provenance
        or rejected_ids or anchors or actions
    ):
        return None
    if has_membership_hold:
        action = "membership hold preserved, not migrated; no reference promotion; inspect provenance before changes"
    elif protected or protection_provenance or rejected_ids or actions:
        action = "protection, rejection, or action evidence preserved; resolve exact content bindings before changes"
    elif anchors:
        action = "registered identity anchor; content-bound core audit decides eligibility; no blanket photo hard lock"
    else:
        action = "metadata preserved; no automatic migration"
    return {
        "photoId": photo_id,
        "folder": folder,
        "status": membership.get("status"),
        "coreUse": membership.get("coreUse"),
        "membershipHold": bool(has_membership_hold),
        "reason": membership.get("reason"),
        "personId": membership.get("personId"),
        "groupId": membership.get("groupId"),
        "sourcePersonIds": list(membership.get("sourcePersonIds", ())),
        "assignmentDisposition": membership.get("assignmentDisposition"),
        "assignmentEvidence": membership.get("assignmentEvidence"),
        "referenceVersion": membership.get("referenceVersion"),
        "protected": protected,
        "protectionProvenance": protection_provenance,
        "identityAnchorOwners": anchors,
        "rejectedPersonIds": rejected_ids,
        "actionCount": len(actions),
        "actionHistory": actions[-10:],
        "provenanceClassification": (
            "registered identity anchor; no membership provenance"
            if anchors and not membership and not protection_provenance and not actions
            else "unverified; do not infer experimental or human origin"
        ),
        "action": action,
    }


def _candidate_rows(paths, photos, catalog, locked_ids, selected_ids, metadata, rejections, *, settings=None,
                    quality=None):
    from . import face_quality

    by_path = {photo.path.resolve(): photo for photo in photos}
    rows = []
    missing = []
    for path in paths:
        photo = by_path.get(path.resolve())
        if photo is None:
            missing.append(path.name)
            continue
        photo_id = metadata.photo_id_from_name(photo.name)
        if not photo_id:
            continue
        record = catalog.get("photos", {}).get(photo_id, {})
        assessment = (
            (quality(photo, path) if quality is not None else face_quality.assess(photo, settings))
            if settings is not None else None
        )
        rows.append({
            "photoId": photo_id,
            "sourceFolder": "Various",
            "sourceBucket": "Pool",
            "side": "Prospects",
            "protected": bool(photo_id in locked_ids or record.get("protected")),
            "workflowSelected": photo_id in selected_ids,
            "vector": photo.vec,
            "sha256": metadata.content_sha256(path),
            # Matching accepts single and dominant main faces; only single-face
            # quality may later become a reference vote.
            **(face_quality.candidate_fields(assessment) if assessment is not None
               else {"qualityEligible": False}),
            **rejections.photo_state(catalog, photo),
        })
    if missing:
        raise ValueError("selected arrivals were not measured: " + ", ".join(missing))
    return rows


def _refresh_content_digest(cache, path):
    """Hash each explicitly selected input, even if its stat tuple was cached."""
    path = pathlib.Path(path)
    stat = path.stat()
    digest = hashlib.sha1(path.read_bytes()).hexdigest()
    cache.stat[str(path)] = [stat.st_size, stat.st_mtime_ns, digest]
    return digest


def _current_measurement(data):
    """A cached zero-face result is evidence, not a request for new inference."""
    return isinstance(data, dict) and bool(data) and (
        bool(data.get("v")) or (
            isinstance(data.get("faces"), int)
            and not isinstance(data.get("faces"), bool) and "t" in data
        )
    )


def _workflow_ids(cfg, metadata):
    names = list(cfg.get("photos", {}).values())
    for flow in cfg.get("flows", {}).values():
        names.extend(flow.get("photos", {}).values())
    return {
        photo_id for name in names if isinstance(name, str)
        if (photo_id := metadata.photo_id_from_name(name))
    }


def _bindings(api, cfg, policy):
    from tools.art.likeness_library import policy as policy_module

    shared = (
        "engine.py", "audit.py", "scoring.py", "reconciliation.py",
        "maintenance.py", "metadata.py", "rejections.py", "policy.py", "protection.py",
        "normal_products.py", "normal_transaction.py", "retained_preparation.py",
        "normal_admission.py", "planner.py",
        "normal_history.py", "normal_finish.py", "identity_families.py", "identity_names.py",
        "derivatives.py", "review_gallery.py",
    )
    library = pathlib.Path(policy_module.__file__).parent
    artifacts = {name: library / name for name in shared}
    artifacts.update({
        "art:image_preparation.py": library.parent / "image_preparation.py",
        "art:originals.py": library.parent / "originals.py",
        "art:duplicates.py": library.parent / "duplicates.py",
        "art:intake_library/models.py": library.parent / "intake_library" / "models.py",
        "art:people_gallery.py": library.parent / "people_gallery.py",
    })
    return {
        "policySHA256": hashlib.sha256(
            json.dumps(policy, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "configurationSHA256": hashlib.sha256(
            json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "sharedImplementation": {
            name: api.metadata.content_sha256(path) for name, path in artifacts.items()
        },
    }


def _validate_requested_receipt(data, args, bindings):
    if data.get("runId") and getattr(args, "run_id", None) != data["runId"]:
        raise ValueError("run-id is bound to another run; select its exact recorded identifier")
    if data.get("profile") != args.profile:
        raise ValueError("run-id is bound to another profile; select a new run-id")
    if args.photo_id and sorted(set(args.photo_id)) != data.get("selectedPhotoIds"):
        raise ValueError("run-id is bound to another selected photo scope; select a new run-id")
    if sorted(set(getattr(args, "update_photo_id", ()))) != data.get("updatePhotoIds", []):
        raise ValueError("run-id is bound to another same-photo update mode; select a new run-id")
    if data.get("bindings") != bindings:
        raise ValueError("policy, configuration or shared implementation changed; preview a new run")


def _route_plan(api, candidates, cores, settings, policy, names_taken, *, admission_context=None):
    """Keep the entire eligible core map and the common policy for every profile."""
    return api.plan_reconciliation(
        candidates,
        cores,
        assign=settings["assign"],
        margin=settings["margin"],
        cluster=policy["identityActions"]["identityClusterMinimumSimilarity"],
        minimum_cluster=settings["minCluster"],
        cast_merge=policy["identityActions"]["autoMergeMinimum"],
        names_taken=names_taken,
        name_factory=api.invent_name,
        policy=policy,
        **({"admission_context": admission_context} if admission_context is not None else {}),
    )


def _add_profile_evidence(report, cores, profile):
    report["preparation"] = (
        "FAST original-byte matching; editing and 944 products deferred; pixels are not certified clean"
        if profile == "fast" else
        "FULL/LEAN share the same matching policy and consume current native inputs; "
        "native preparation and 944 framing remain independent operations"
    )
    if profile == "full":
        report["fullEvidence"] = {
            folder: {
                "corePhotoIds": core["corePhotoIds"],
                "mode": core["mode"],
                "photoScores": core["photoScores"],
            }
            for folder, core in sorted(cores.items())
        }
    else:
        report["evidenceProduct"] = (
            "compact selected-arrival plan; unchanged identity evidence reused"
            if profile == "lean" else
            "original-byte selected-arrival plan; image editing and 944 framing deferred"
        )
    return report


def _policy_permitted_moves(moves, policy):
    permitted, held = [], []
    for move in moves:
        parts = pathlib.PurePosixPath(move["destination"]).parts
        if (
            parts[-2] == "gallery"
            and parts[0] != "Various"
            and not policy["categoryPolicies"][parts[0]]["automaticPhotoRoutingEnabled"]
            and not (
                parts[0] in ("Sisters", "Angels") and move.get("castAdmission")
                and policy["categoryPolicies"][parts[0]].get("galleryAdmissionEnabled")
            )
        ):
            held.append({
                "photoId": move["photoId"],
                "reason": "automatic Gallery admission is disabled by the current policy",
            })
        else:
            permitted.append(move)
    return permitted, held


def _stage_prepared_prior(root, stage_root, row):
    """Relocate one verified prior native and its lineage inside the batch transaction."""
    from tools.art.likeness_library import normal_history, normal_transaction, retained_preparation

    root = pathlib.Path(root).resolve()
    stage_root = pathlib.Path(stage_root).resolve()
    source = normal_transaction.safe(root, row["source"])
    token = hashlib.sha256(
        (stage_root.relative_to(root).as_posix() + "\0" + row["source"] + "\0" + row["sha256"]).encode("utf-8")
    ).hexdigest()[:16]
    destination = pathlib.PurePosixPath("Various", "duplicates", token, "gallery", source.name).as_posix()
    target = normal_transaction.safe(root, destination)
    if target.exists():
        raise ValueError(f"prior prepared native destination already exists: {destination}")
    lineage = row["lineage"]
    link = retained_preparation.verify_link(root, source, row["photoId"])
    if (
        link is None or link["sourceSha256"] != lineage["sourceSha256"]
        or link["manifest"] != lineage["manifest"]
        or hashlib.sha256(normal_transaction.safe(root, link["manifest"]).read_bytes()).hexdigest()
        != lineage["manifestSha256"]
    ):
        raise ValueError(f"prior prepared incoming lineage changed since selection: {row['source']}")
    transfer = retained_preparation.plan_transfer(root, row["source"], destination)
    if (transfer is None or transfer["currentSha256"] != row["sha256"]
            or transfer["sourceSha256"] != lineage["sourceSha256"]
            or transfer["files"][-1]["source"] != lineage["manifest"]
            or transfer["files"][-1]["sha256"] != lineage["manifestSha256"]):
        raise ValueError(f"prior prepared incoming lineage changed: {row['source']}")
    retained_preparation.validate_transfers(root, [transfer])
    expected = {row["source"]: row["sha256"]}
    preserved = {}

    def stage_bytes(relative, payload):
        destination_path = normal_transaction.safe(stage_root, relative)
        if destination_path.exists():
            raise ValueError(f"prior prepared staging collision: {relative}")
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_bytes(payload)

    native_bytes = source.read_bytes()
    if hashlib.sha256(native_bytes).hexdigest() != row["sha256"]:
        raise ValueError(f"prior prepared native changed while staging: {row['source']}")
    stage_bytes(destination, native_bytes)
    manifest_source = transfer["files"][-1]["source"]
    for item in transfer["files"]:
        src = normal_transaction.safe(root, item["source"])
        if item["source"] in expected:
            raise ValueError(f"prior prepared transfer repeats source: {item['source']}")
        expected[item["source"]] = item["sha256"]
        if item["source"] == manifest_source:
            payload = transfer["manifestAfter"].encode("utf-8")
        elif item["source"] == transfer["detailSource"]:
            payload = transfer["detailAfter"].encode("utf-8")
        else:
            payload = src.read_bytes()
            if hashlib.sha256(payload).hexdigest() != item["sha256"]:
                raise ValueError(f"prior preparation artifact changed while staging: {item['source']}")
        stage_bytes(item["destination"], payload)

    prefix = normal_transaction.safe(root, retained_preparation._processing_prefix(root))
    for index in sorted(prefix.rglob(normal_history.INDEX)) if prefix.exists() else ():
        relative = index.relative_to(root).as_posix()
        raw_index = index.read_bytes()
        original = json.loads(raw_index)
        if not any(entry.get("current") == row["source"] for entry in original.get("entries", {}).values()):
            continue
        normal_history.retired(root, index.parent)
        checksum = hashlib.sha256(raw_index).hexdigest()
        if hashlib.sha256(index.read_bytes()).hexdigest() != checksum:
            raise ValueError(f"prior prepared history changed while staging: {relative}")
        staged_index = normal_transaction.safe(stage_root, relative)
        data = json.loads(staged_index.read_text(encoding="utf-8")) if staged_index.exists() else original
        changed = False
        for entry in data["entries"].values():
            if entry.get("current") == row["source"]:
                if entry.get("currentSha256") != row["sha256"]:
                    raise ValueError(f"prior prepared history binding changed: {relative}")
                entry["current"] = destination
                changed = True
                for generation in entry["generations"]:
                    preserved[generation["native"]] = generation["sha256"]
                for manifest, digest in entry["retiredManifests"].items():
                    preserved[manifest] = digest
                    old = json.loads(normal_transaction.safe(root, manifest).read_text(encoding="utf-8"))
                    for artifact in old.get("artifacts", ()):
                        preserved[artifact["path"]] = artifact["sha256"]
                for view in entry.get("historyViews", {}).values():
                    preserved[view["path"]] = view["sha256"]
        if not changed:
            raise ValueError(f"prior prepared history staging conflicts: {relative}")
        staged_index.parent.mkdir(parents=True, exist_ok=True)
        staged_index.write_bytes((json.dumps(data, indent=2) + "\n").encode("utf-8"))
        expected[relative] = checksum
    return {
        **row, "destination": destination, "sourceSha256": transfer["sourceSha256"],
        "setKey": transfer["setKey"],
    }, expected, preserved


def _plan(api, root, profile, photo_ids, *, cache_path=None, policy_path=None,
          persist_evidence=False, sandbox_override=False, native_paths=None, update_ids=()):
    """Build one frozen-core plan; profile never alters thresholds or rival scope."""
    from tools.art import originals
    from tools.art.likeness_library.policy import effective_settings, load_policy
    from tools.art.likeness_library.reconciliation import frozen_identity_cores

    domains, metadata, rejections = api.domains, api.metadata, api.rejections
    root = pathlib.Path(root).resolve()
    cfg = api.configuration()
    policy = load_policy(policy_path)
    if persist_evidence:
        from tools.art.likeness_library import maintenance
        from tools.art.likeness_library.sandbox import is_normal_flow_proof_path

        maintenance.require_authorization(
            root, policy, sandbox_override,
            allow_isolated_proof=sandbox_override and is_normal_flow_proof_path(root),
        )
    settings = effective_settings(cfg, policy)
    settings["poolHome"] = "Various"
    read_token = domains.CURRENT.set("general")
    read_only_token = domains.READ_ONLY.set(True)
    try:
        if cache_path is None:
            cache_path = api.cache_path(argparse.Namespace(cache=None), root)
        cache = api.Cache(cache_path)
        embedder = api.Embedder()
        embedder.configure_evidence(
            api.cw.storage_root(cfg, "likeness", root=root) / "general" / "face-evidence",
            library_root=root,
        )
        catalog = metadata.load_catalog(metadata.path_for_root(root))
        selected, older, aliases, owners = _intake_selection(
            api, root, set(photo_ids or ()), originals, metadata, cfg, catalog,
        )
        selected_paths = [path for path, _name in selected]
        selected_names = {path: name for path, name in selected}
        selected_by_id = {metadata.photo_id_from_name(name): path for path, name in selected}
        from tools.art.likeness_library import retained_preparation

        effective_updates = set(update_ids) & set(selected_by_id)
        for photo_id in selected_by_id:
            record = catalog.get("photos", {}).get(photo_id)
            if record and photo_id not in owners:
                raise ValueError(
                    f"incoming {photo_id} has existing catalogue decisions but no unique current owner; "
                    "resolve its content binding before intake"
                )
        for photo_id, paths in owners.items():
            if photo_id not in selected_by_id:
                continue
            if len(paths) != 1:
                raise ValueError(f"same-photo update has multiple current owners: {photo_id}")
            owner = paths[0]
            link = None
            if retained_preparation.claims_photo(root, owner):
                link = retained_preparation.verify_link(root, owner, photo_id)
                if link is None:
                    raise ValueError(f"same-photo update {photo_id} has invalid retained history: {owner}")
            if photo_id.startswith("photo:pic_"):
                old_original = link["sourceSha256"] if link else metadata.content_sha256(owner)
                if old_original != metadata.content_sha256(selected_by_id[photo_id]):
                    raise ValueError(
                        f"short content ID collision for {photo_id}: incoming original differs from "
                        f"the existing owner's full original SHA-256 ({owner})"
                    )
            if photo_id not in update_ids:
                record = catalog.get("photos", {}).get(photo_id, {})
                guarded = [
                    field for field in ("protectionProvenance", "rejectedPersonIds")
                    if record.get(field)
                ]
                actions = [
                    action for action in catalog.get("actions", ())
                    if photo_id in action.get("photoIds", ()) and action.get("contentSha256")
                ]
                if guarded or actions:
                    raise ValueError(
                        f"automatic same-photo update {photo_id} has content-bound decisions "
                        f"({', '.join(guarded) or 'action history'}); inspect their exact bindings before replacement"
                    )
                if photo_id in _workflow_ids(cfg, metadata):
                    raise ValueError(
                        f"automatic same-photo update {photo_id} is workflow-selected; "
                        "review the exact content binding before explicit replacement"
                    )
            effective_updates.add(photo_id)
        identity_photos = []
        update_targets = {}
        update_target_hashes = {}
        missing_evidence = []
        membership_flags = []
        metadata_evidence = _catalog_evidence(catalog)
        for group, name, folder in api.cw.photo_folders(cfg, root):
            if group not in IDENTITY_ROOTS:
                continue
            for path in originals.images(folder / "gallery"):
                photo_id = metadata.photo_id_from_name(path.name)
                record = catalog.get("photos", {}).get(photo_id, {})
                if photo_id in effective_updates:
                    link = None
                    if retained_preparation.claims_photo(root, path):
                        link = retained_preparation.verify_link(root, path, photo_id)
                        if link is None:
                            raise ValueError(
                                f"same-photo update {photo_id} has invalid retained history; "
                                "resolve its exact content bindings before replacing it"
                            )
                    if photo_id in update_targets:
                        raise ValueError(f"same-photo update has multiple current owners: {photo_id}")
                    if record.get("protected"):
                        raise ValueError(f"same-photo update is blocked by a true photo lock: {photo_id}")
                    owner_hash = metadata.content_sha256(path)
                    if link and link.get("currentSha256", owner_hash) != owner_hash:
                        raise ValueError(f"same-photo owner changed after retained verification: {photo_id}")
                    if record and owner_hash != record["contentSha256"]:
                        raise ValueError(f"current same-photo owner has stale content binding: {photo_id}")
                    update_targets[photo_id] = path.relative_to(root).as_posix()
                    update_target_hashes[update_targets[photo_id]] = owner_hash
                    continue
                details = _membership_details(
                    catalog, photo_id, f"{group}/{name}", record, metadata_evidence,
                )
                if details is not None:
                    membership_flags.append(details)
                digest = _refresh_content_digest(cache, path)
                data = cache.emb.get(digest)
                if not _current_measurement(data):
                    missing_evidence.append(f"{group}/{name}/gallery/{path.name}")
                    continue
                identity_photos.append(api.Photo(path, group, name, digest, data))
        if missing_evidence:
            sample = ", ".join(missing_evidence[:8])
            suffix = f" (+{len(missing_evidence) - 8} more)" if len(missing_evidence) > 8 else ""
            category_counts = collections.Counter(row.split("/", 1)[0] for row in missing_evidence)
            membership_counts = collections.Counter(
                f"{row['status'] or 'unset'}/coreUse={row['coreUse']}"
                for row in membership_flags
            )
            flag_sample = membership_flags[:8]
            raise ValueError(
                f"{len(missing_evidence)} unchanged identity photo(s) lack cached vectors "
                f"by category={dict(sorted(category_counts.items()))}; refusing whole-library "
                f"reprocessing or rival truncation: {sample}{suffix}. Membership metadata in the "
                f"same identity scope={dict(sorted(membership_counts.items()))}; flag sample="
                f"{json.dumps(flag_sample, ensure_ascii=False)}. No membership/protection/rejection "
                "metadata was changed; inspect its source provenance before any explicit migration."
            )
        arrival_photos = []
        for path in selected_paths:
            expected_id = metadata.photo_id_from_name(selected_names[path])
            if selected_names[path] != path.name and expected_id.startswith("photo:pic_"):
                actual_id = "photo:pic_" + _refresh_content_digest(cache, path)[:8]
                if actual_id != expected_id:
                    raise ValueError(f"incoming original changed while establishing its stable ID: {path}")
            measured_path = (native_paths or {}).get(path.relative_to(root).as_posix(), path)
            digest = _refresh_content_digest(cache, measured_path)
            data = cache.emb.get(digest)
            if not _current_measurement(data):
                if persist_evidence:
                    from tools.art.likeness_library.engine import MODEL_URLS

                    missing_models = [
                        name for name in MODEL_URLS if not (api.DATA / "models" / name).is_file()
                    ]
                    if missing_models:
                        raise ValueError(
                            "selected arrival needs fresh inference but local models are missing; "
                            "downloads are disabled: " + ", ".join(missing_models)
                        )
                    # Load while read-only: a missing/disappearing model must
                    # fail locally rather than letting the writer download it.
                    if embedder.det is None:
                        embedder.load()
                    domains.READ_ONLY.set(False)
                data = embedder(measured_path)
                domains.READ_ONLY.set(True)
                if not data or not data.get("v"):
                    data = data or {"faces": -1}
                cache.emb[digest] = data
            photo = api.Photo(path, "Various", "Various", digest, data)
            photo.name = selected_names[path]
            arrival_photos.append(photo)
        photos = identity_photos + arrival_photos
        space = api.Space(photos, settings, mean=cache.centering_mean)
    finally:
        domains.READ_ONLY.reset(read_only_token)
        domains.CURRENT.reset(read_token)

    all_cores, locked_ids, core_diagnostics = frozen_identity_cores(
        space,
        catalog,
        photo_id_fn=metadata.photo_id_from_name,
        content_sha256_fn=metadata.content_sha256,
        policy=policy,
        require_single_face="castAdmission" in policy,
    )
    cores = {
        folder: core for folder, core in all_cores.items()
        if folder.split("/", 1)[0] in IDENTITY_ROOTS
    }
    requested_ids = set(photo_ids or ())
    selected_ids = set(selected_by_id) | {row["photoId"] for row in aliases}
    if requested_ids:
        selected_ids &= requested_ids
    identity_ids = {
        metadata.photo_id_from_name(photo.name)
        for photo in identity_photos
        if metadata.photo_id_from_name(photo.name)
    }
    duplicate_arrivals = sorted(set(selected_by_id) & identity_ids)
    if duplicate_arrivals:
        raise ValueError(
            "selected same-photo IDs are ambiguous in the current library; "
            "use explicit --update-photo-id for each replacement: " + ", ".join(duplicate_arrivals)
        )
    missing_updates = sorted(set(update_ids) - set(update_targets) - {row["photoId"] for row in aliases})
    if missing_updates:
        raise ValueError("explicit updates have no unique existing identity owner: " + ", ".join(missing_updates))
    selected_rows = arrival_photos

    names_taken = {
        name for _group, name, _folder in api.cw.photo_folders(cfg, root)
    }
    workflow_ids = _workflow_ids(cfg, metadata)
    from . import face_quality

    redetect = face_quality.redetector(embedder)

    def quality(photo, path):
        measured = (native_paths or {}).get(path.relative_to(root).as_posix(), path)
        return face_quality.assess(
            photo, settings, path=measured, redetect=redetect, framing=face_quality.derivative_framing,
        )

    candidates = _candidate_rows(
        selected_paths, selected_rows, catalog, locked_ids, workflow_ids, metadata, rejections,
        settings=settings if "castAdmission" in policy else None, quality=quality,
    )
    from . import normal_admission

    admission_context = (
        normal_admission.context(cores, normal_admission.reference_rows(space, cores, catalog), policy)
        if "castAdmission" in policy else None
    )
    report = _route_plan(
        api, [row for row in candidates if row["photoId"] not in update_targets],
        cores, settings, policy, names_taken, admission_context=admission_context,
    )
    if update_targets:
        report["assignments"] = [row for row in report["assignments"] if row["photoId"] not in update_targets]
        report["held"] = [row for row in report["held"] if row["photoId"] not in update_targets]
        report["assignments"].extend({
            "photoId": photo_id, "destination": pathlib.PurePosixPath(relative).parent.parent.as_posix(),
            "sourceBucket": "Pool", "reason": "content-bound same-photo update; existing owner/name/lineage retained",
        } for photo_id, relative in sorted(update_targets.items()))
    report.update({
        "kind": "normal-import-plan",
        "schemaVersion": 1,
        "profile": profile,
        "scope": "selected Various/gallery arrivals only",
        "selectedPhotoIds": sorted(selected_ids),
        "eligibleIdentityCount": len(cores),
        "allEligibleIdentitiesCompared": True,
        "profileMatchingPolicy": "shared",
        "policyVersion": policy["version"],
        "policyStatus": policy["status"],
        "coreDiagnostics": core_diagnostics,
        "membershipDiagnostics": _diagnose_membership(catalog, space, metadata),
        "implementationSHA256": metadata.content_sha256(pathlib.Path(__file__)),
        "bindings": _bindings(api, cfg, policy),
        "updateTargets": update_targets,
        "updateTargetHashes": update_target_hashes,
        "sourceHashes": {
            metadata.photo_id_from_name(name): metadata.content_sha256(path)
            for path, name in selected
        },
        "olderArrivals": _older_rows(root, older, metadata),
        "retainedOriginalAliases": aliases,
    })
    _add_profile_evidence(report, cores, profile)
    return report, candidates, selected_rows, space, catalog, cfg, policy, cache


def _receipt_path(root, run_id, cfg):
    from tools.workflows import comfy_workflows as cw

    return cw.storage_root(cfg, "reports", root=root) / "runs" / f"normal-import-{run_id}.json"


def _write_receipt(path, value, *, exclusive=False):
    import os
    import tempfile
    from tools.art.likeness_library import report_assets

    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        return
    staged = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n",
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False,
        ) as stream:
            staged = pathlib.Path(stream.name)
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        report_assets.replace_file(staged, path)
    finally:
        if staged is not None and staged.exists():
            staged.unlink()


def _transaction_backup(root, cfg, moves):
    """Back up only this batch's originals, retained prep, and catalogue."""
    from tools.art import library_backup
    from tools.art.likeness_library import metadata, retained_preparation

    root = pathlib.Path(root).resolve()
    scoped_sources = []
    for index, row in enumerate(moves):
        source = root / pathlib.PurePosixPath(row["source"])
        scoped_sources.append((f"arrival-{index:04d}", source))
        transfer = retained_preparation.plan_transfer(root, row["source"], row["destination"])
        if transfer:
            scoped_sources.extend(
                (f"retained-{index:04d}-{item_index:04d}", root / item["source"])
                for item_index, item in enumerate(transfer["files"])
            )
    scoped_sources.append(("likeness-catalogue", metadata.path_for_root(root)))
    return library_backup.create_backup(
        root, apply=True, scoped_sources=scoped_sources,
    )


def _check_receipt(root, receipt, bindings=None):
    from tools.art.likeness_library import metadata

    data = json.loads(pathlib.Path(receipt).read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or data.get("kind") != "normal-import-receipt":
        raise ValueError("not a supported normal-import receipt")
    if pathlib.Path(data["root"]).resolve() != pathlib.Path(root).resolve():
        raise ValueError("normal-import receipt is bound to another library root")
    if data.get("implementationSHA256") != metadata.content_sha256(pathlib.Path(__file__)):
        raise ValueError("normal-import implementation changed; preview a new run")
    if data.get("status") != "applied":
        raise ValueError("normal-import receipt is not in the applied state")
    if bindings is not None and data.get("bindings") != bindings:
        raise ValueError("policy, configuration or shared implementation changed; preview a new run")
    journal_path = data.get("journal")
    if journal_path:
        if data.get("publication"):
            from tools.art.likeness_library import normal_transaction

            normal_transaction.verify(root, journal_path)
            from tools.art.likeness_library import normal_history, retained_preparation

            prefix = pathlib.Path(root) / retained_preparation._processing_prefix(root)
            for index in prefix.rglob(normal_history.INDEX) if prefix.exists() else ():
                normal_history.retired(root, index.parent)
            return data
        journal = json.loads(pathlib.Path(journal_path).read_text(encoding="utf-8"))
        if journal.get("status") != "applied" or journal.get("root") != str(pathlib.Path(root).resolve()):
            raise ValueError("normal-import move journal is not in the applied state")
        catalog_path = pathlib.Path(journal["catalogPath"])
        if metadata.content_sha256(catalog_path) != journal.get("catalogAfterSHA256"):
            raise ValueError("catalogue changed since normal import; resolve before treating it as checked")
        for row in journal["moves"]:
            destination = pathlib.Path(root) / pathlib.PurePosixPath(row["destination"])
            if not destination.is_file() or metadata.content_sha256(destination) != row["sha256"]:
                raise ValueError(f"normal-import destination changed or disappeared: {row['destination']}")
            if (pathlib.Path(root) / pathlib.PurePosixPath(row["source"])).exists():
                raise ValueError(f"normal-import source still exists: {row['source']}")
    return data


def _parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--root", help="library root containing Various, identities and the local catalogue")
    parser.add_argument("--cache", help="embedding cache; defaults to the configured per-library cache")
    parser.add_argument("--policy", help="versioned likeness policy JSON")
    parser.add_argument("--profile", choices=("full", "lean", "fast"), default="lean")
    parser.add_argument("--photo-id", action="append", default=[], help="select one arrival; repeat for a small explicit batch")
    parser.add_argument("--update-photo-id", action="append", default=[], help="explicit content-bound replacement retaining the existing owner; repeatable")
    parser.add_argument("--run-id", help="stable receipt name; required for --check/--undo")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="preview only (the default)")
    mode.add_argument("--apply", action="store_true", help="apply selected, policy-authorized arrival moves with recovery")
    mode.add_argument("--check", action="store_true", help="verify an applied run without rescoring")
    parser.add_argument("--undo", action="store_true", help="preview exact recovery; add --apply to execute it")
    parser.add_argument("--recover", action="store_true", help="recover a partial publication using its run-id; preview unless --apply")
    parser.add_argument("--sandbox-apply-draft", action="store_true", help="explicitly authorize draft policy only in sandbox Working")
    return parser


def main(argv=None):
    parser = _parser()
    args = parser.parse_args(argv)
    args.photo_id = sorted(set(args.photo_id) | set(args.update_photo_id))
    from tools.art import likeness as api
    from tools.art.likeness_library import maintenance, metadata
    from tools.art.likeness_library.sandbox import is_normal_flow_proof_path
    from tools.workflows import comfy_workflows as cw

    cfg = api.cw.load_cfg()
    root = pathlib.Path(args.root or cw.work_root(cfg)).resolve()
    if args.check and args.undo:
        parser.error("--check and --undo are separate operations")
    if args.run_id and (args.check or args.undo):
        if args.photo_id:
            parser.error("--check/--undo with a run-id use its bound scope, not --photo-id")
    if (args.check or args.undo) and args.run_id:
        if not args.run_id or not RUN_ID.fullmatch(args.run_id):
            parser.error("--check and --undo require a safe --run-id")
        receipt_path = _receipt_path(root, args.run_id, cfg)
        from tools.art.likeness_library.policy import load_policy

        try:
            checked = _check_receipt(
                root, receipt_path, _bindings(api, api.configuration(), load_policy(args.policy)),
            )
        except (OSError, ValueError) as exc:
            print(f"normal import stopped safely: {exc}", file=sys.stderr)
            return 1
        journal = checked.get("journal")
        if args.undo:
            if checked.get("publication"):
                from tools.art.likeness_library import normal_transaction

                normal_transaction.recover(root, journal, apply=args.apply)
                if args.apply:
                    checked["status"] = "undone"
                    _write_receipt(receipt_path, checked)
                print(f"normal publication recovery: {'applied' if args.apply else 'preview only'}")
                return 0
            if not journal:
                print("this run made no file changes; nothing to undo")
                return 0
            result = maintenance.undo_moves(
                root,
                journal,
                cfg,
                apply=args.apply,
                backup_fn=lambda backup_root, backup_cfg: _transaction_backup(
                    backup_root,
                    backup_cfg,
                    [
                        {**row, "source": row["destination"], "destination": row["source"]}
                        for row in json.loads(pathlib.Path(journal).read_text(encoding="utf-8"))["moves"]
                    ],
                ),
            )
            if args.apply:
                checked["status"] = "undone"
                _write_receipt(receipt_path, checked)
            print(f"normal import undo: {len(result)} move(s); {'applied' if args.apply else 'preview only'}")
            return 0
        print(f"normal import check: {args.run_id} is applied and content-bound")
        return 0
    if args.undo:
        parser.error("--undo requires a --run-id")

    if args.run_id and not RUN_ID.fullmatch(args.run_id):
        parser.error("--run-id contains unsupported characters")
    run_id = args.run_id or datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    receipt_path = _receipt_path(root, run_id, cfg)
    # Keep accepted preparation's SHA-named originals below Windows path limits.
    batch_run = receipt_path.parent / ("n-" + hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:16])
    if args.recover:
        from tools.art.likeness_library import normal_transaction

        if not args.run_id:
            parser.error("--recover requires --run-id")
        try:
            journal = batch_run / "publication-journal.json"
            legacy = receipt_path.parent / f"normal-batch-{run_id}" / "publication-journal.json"
            if not journal.exists() and legacy.exists():
                journal = legacy
            data = normal_transaction.verify(root, journal, applied=False)
            if data.get("runId") != run_id:
                raise ValueError("recovery journal is bound to another run-id")
            normal_transaction.recover(root, journal, apply=args.apply)
            print(f"normal partial publication recovery: {'applied' if args.apply else 'preview only'}")
            return 0
        except (OSError, ValueError) as exc:
            print(f"normal recovery stopped safely: {exc}", file=sys.stderr)
            return 1
    if args.apply and not receipt_path.exists() and batch_run.exists():
        print("normal import stopped safely: prior/partial run exists; preserve evidence and recover its journal or choose a new run-id", file=sys.stderr)
        return 1
    if args.apply and receipt_path.exists():
        try:
            from tools.art.likeness_library.policy import load_policy

            existing = _check_receipt(root, receipt_path)
            _validate_requested_receipt(existing, args, _bindings(api, api.configuration(), load_policy(args.policy)))
            if not args.photo_id:
                from tools.art import originals

                current_catalog = metadata.load_catalog(metadata.path_for_root(root))
                pending, _older, aliases, _owners = _intake_selection(
                    api, root, [], originals, metadata, api.configuration(), current_catalog,
                )
                pending_ids = {metadata.photo_id_from_name(name) for _path, name in pending}
                pending_ids.update(row["photoId"] for row in aliases)
                if pending_ids - set(existing["selectedPhotoIds"]):
                    raise ValueError("new pending arrivals exist; select a new run-id")
        except (OSError, ValueError) as exc:
            print(f"normal import stopped safely: {exc}", file=sys.stderr)
            return 1
        if existing.get("status") == "applied":
            print(f"normal import already applied and checked: {receipt_path}")
            return 0
        parser.error("run-id already has a receipt; choose a new run-id")

    try:
        prepared = None
        if args.apply and args.profile != "fast":
            from tools.art import originals
            from tools.art.likeness_library import normal_products
            from tools.art.likeness_library.policy import load_policy

            current_catalog = metadata.load_catalog(metadata.path_for_root(root))
            selected, _older, _aliases, _owners = _intake_selection(
                api, root, args.photo_id, originals, metadata, api.configuration(), current_catalog,
            )
            maintenance.require_authorization(
                root, load_policy(args.policy), args.sandbox_apply_draft,
                allow_isolated_proof=args.sandbox_apply_draft and is_normal_flow_proof_path(root),
            )
            if selected:
                prepared = normal_products.prepare(
                    root, batch_run, [path for path, _name in selected], args.profile,
                )
        report, candidates, photos, space, catalog, cfg, policy, cache = _plan(
            api, root, args.profile, args.photo_id, cache_path=args.cache, policy_path=args.policy,
            persist_evidence=args.apply,
            sandbox_override=args.sandbox_apply_draft,
            native_paths=prepared[2] if prepared else None, update_ids=args.update_photo_id,
        )
        if prepared:
            frozen = {row["source"]: row["sourceSha256"] for row in prepared[1]["photos"]}
            current = {
                photo.path.relative_to(root).as_posix(): report["sourceHashes"][metadata.photo_id_from_name(photo.name)]
                for photo in photos
            }
            if frozen != current:
                raise ValueError("prepared pixels do not bind the exact selected incoming originals; preview again")
        ordinary = {**report, "assignments": [
            row for row in report["assignments"] if row["photoId"] not in report["updateTargets"]
        ]}
        proposed = maintenance.proposed_moves(ordinary, photos, root)
        moves, denied = _policy_permitted_moves(proposed, policy)
        moves.extend({
            "photoId": photo_id,
            "source": next(photo.path.relative_to(root).as_posix() for photo in photos if metadata.photo_id_from_name(photo.name) == photo_id),
            "destination": relative,
            "sha256": report["sourceHashes"][photo_id],
            "reason": "content-bound same-photo update; owner retained",
        } for photo_id, relative in report["updateTargets"].items())
        if denied:
            denied_ids = {row["photoId"] for row in denied}
            report["policyHolds"] = [
                {"photoId": row["photoId"], "reason": "automatic Gallery admission is disabled by the current policy"}
                for row in denied
            ]
            report["assignments"] = [
                row for row in report["assignments"] if row.get("photoId") not in denied_ids
            ]
            report["held"].extend(report["policyHolds"])
    except (OSError, ValueError) as exc:
        print(f"normal import stopped safely: {exc}", file=sys.stderr)
        return 1
    report["assignedCount"] = len(report["assignments"])
    report["heldCount"] = len(report["held"])
    moving_ids = {row["photoId"] for row in moves}
    normalizations = [
        {
            "photoId": metadata.photo_id_from_name(photo.name),
            "source": photo.path.relative_to(root).as_posix(),
            "destination": photo.path.with_name(photo.name).relative_to(root).as_posix(),
            "sha256": report["sourceHashes"][metadata.photo_id_from_name(photo.name)],
        }
        for photo in photos
        if metadata.photo_id_from_name(photo.name) not in moving_ids and photo.path.name != photo.name
    ]
    if prepared:
        report["preparation"] = "accepted selected native recipe; FULL/LEAN share recommendations; original bytes retained"
        report["preparationRecipe"] = prepared[1]["recipe"]
        report["preparationManifestSHA256"] = metadata.content_sha256(prepared[0] / "manifest.json")
    mode_label = "apply plan" if args.apply else "check" if args.check else "preview"
    print(
        f"Normal import {mode_label} ({args.profile.upper()}): {len(candidates)} selected arrival(s), "
        f"{report['eligibleIdentityCount']} eligible identities compared, "
        f"{report['assignedCount']} assignment(s), {report['heldCount']} held, "
        f"{len(report['clusters'])} new cluster(s), {len(moves)} permitted move(s)."
    )
    print(f"matching policy: {report['policyVersion']} ({report['policyStatus']}); profile policy: shared")
    for row in report["assignments"]:
        print(f"  {row['photoId']} -> {row.get('destination') or 'REVIEW'} ({row['reason']})")
    for row in report["held"]:
        destination = next((move["destination"] for move in moves if move["photoId"] == row.get("photoId")), None)
        if destination:
            print(f"  REVIEW {row['photoId']} -> {destination}: {row['reason']}")
        else:
            print(f"  HOLD {row.get('photoId') or '<no stable ID>'}: {row['reason']}")
    for row in report["olderArrivals"]:
        print(f"  PRIOR INCOMING {row['photoId']}: {row['source']} (retained on publication)")
    for row in report.get("retainedOriginalAliases", []):
        print(f"  RETAINED ORIGINAL {row['photoId']}: {row['source']} (preserved untouched)")
    for row in normalizations:
        print(f"  NORMALIZE {row['source']} -> {row['destination']}")
    for row in report["coreDiagnostics"]:
        print(f"  CORE DIAGNOSTIC {row}")
    for row in report["membershipDiagnostics"]:
        label = "METADATA HOLD" if (
            row["membershipHold"] or row["protected"] or row["protectionProvenance"]
            or row["rejectedPersonIds"]
        ) else "METADATA DIAGNOSTIC"
        print(
            f"  {label} {row['photoId']} {row['folder']}: {row['status'] or 'unset'}/"
            f"coreUse={row['coreUse']} ({row['reason'] or 'no reason'}); {row['action']}"
        )
    if not args.apply:
        print("preview only; no library files or catalogue metadata changed")
        waiting = bool(moves or normalizations or report["held"] or report["clusters"])
        if args.check:
            print("work waiting" if waiting else "no eligible arrivals found")
            return 1 if waiting else 0
        return 0
    try:
        allow_isolated_proof = args.sandbox_apply_draft and is_normal_flow_proof_path(root)
        maintenance.require_authorization(
            root,
            policy,
            args.sandbox_apply_draft,
            allow_isolated_proof=allow_isolated_proof,
        )
        from tools.art.likeness_library import normal_products, normal_transaction, normal_finish

        moves, report["frozenConsistencyCheck"] = normal_finish.check_batch(
            api, space, catalog, policy, moves, update_ids=report["updateTargets"],
        )

        ordinary_moves = [row for row in moves if row["photoId"] not in report["updateTargets"]]
        maintenance.validate_moves(root, ordinary_moves)
        maintenance._validate_permissions(root, ordinary_moves, policy, cfg)
        for row in moves:
            if metadata.content_sha256(root / pathlib.PurePosixPath(row["source"])) != row["sha256"]:
                raise ValueError(f"normal selected source changed before publication: {row['source']}")
        for relative, checksum in report["updateTargetHashes"].items():
            if metadata.content_sha256(root / pathlib.PurePosixPath(relative)) != checksum:
                raise ValueError(f"same-photo owner changed before publication: {relative}")
        from tools.art import originals

        current_selected, current_older, current_aliases, _owners = _intake_selection(
            api, root, args.photo_id, originals, metadata, cfg, catalog,
        )
        if (
            [(path, name) for path, name in current_selected]
            != [(photo.path, photo.name) for photo in photos]
            or _older_rows(root, current_older, metadata) != report["olderArrivals"]
            or current_aliases != report.get("retainedOriginalAliases", [])
        ):
            raise ValueError("incoming original/version selection changed; preview the batch again")
        if metadata.load_catalog(metadata.path_for_root(root)) != catalog:
            raise ValueError("catalogue changed before normal publication")
        stage_root = batch_run / "publication"
        published, updated, removed = normal_products.stage(
            root, stage_root, moves, prepared, profile=args.profile,
            photos=photos, cfg=cfg, catalog=catalog, policy=policy,
        )
        moved_ids = {row["photoId"] for row in moves}
        normalized_ids = {row["photoId"] for row in normalizations if row["photoId"] not in moved_ids}
        older_published, older_expected, older_preserved = [], {}, {}
        for row in report["olderArrivals"]:
            if row["photoId"] not in moved_ids | normalized_ids:
                continue
            if row["kind"] == "prepared":
                archived, sources, history = _stage_prepared_prior(root, stage_root, row)
            else:
                source = normal_transaction.safe(root, row["source"])
                destination = pathlib.PurePosixPath("Various", "duplicates", source.name).as_posix()
                if normal_transaction.safe(root, destination).exists():
                    raise ValueError(f"prior incoming destination already exists; preserve both versions: {destination}")
                target = normal_transaction.safe(stage_root, destination)
                if target.exists():
                    raise ValueError(f"prior incoming staging destination already exists: {destination}")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                if metadata.content_sha256(target) != row["sha256"]:
                    raise ValueError(f"prior incoming original changed before staging: {source}")
                archived, sources = {**row, "destination": destination}, {row["source"]: row["sha256"]}
                history = {}
            for relative, checksum in sources.items():
                if relative in older_expected and older_expected[relative] != checksum:
                    raise ValueError(f"conflicting prior incoming source bindings: {relative}")
                older_expected[relative] = checksum
            for relative, checksum in history.items():
                if relative in older_preserved and older_preserved[relative] != checksum:
                    raise ValueError(f"conflicting prior history bindings: {relative}")
                older_preserved[relative] = checksum
            older_published.append(archived)
        for row in normalizations:
            if row["photoId"] in moved_ids:
                continue
            source = root / pathlib.PurePosixPath(row["source"])
            destination = root / pathlib.PurePosixPath(row["destination"])
            if destination.exists() and row["destination"] not in older_expected:
                raise ValueError(f"normalized incoming destination already exists: {destination}")
            target = stage_root / pathlib.PurePosixPath(row["destination"])
            if target.exists():
                raise ValueError(f"normalized incoming staging destination already exists: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            if metadata.content_sha256(target) != row["sha256"]:
                raise ValueError(f"incoming original changed before normalization: {source}")
        normalization_moves = [row for row in normalizations if row["photoId"] in normalized_ids]
        projected = normal_finish.projected(api, root, stage_root, space, cache, moves + normalization_moves)
        report["finalComparisonAndFamily"] = normal_finish.family_and_final(
            api, root, stage_root, projected, updated, policy, moves,
        )
        preserved = {
            photo.path.relative_to(root).as_posix(): report["sourceHashes"][metadata.photo_id_from_name(photo.name)]
            for photo in photos if metadata.photo_id_from_name(photo.name) not in moved_ids | normalized_ids
        }
        for row in report.get("retainedOriginalAliases", []):
            relative, checksum = row["source"], row["sha256"]
            if relative in older_expected or (stage_root / pathlib.PurePosixPath(relative)).exists():
                raise ValueError(f"retained original conflicts with a staged publication: {relative}")
            if relative in preserved and preserved[relative] != checksum:
                raise ValueError(f"conflicting preserved source bindings: {relative}")
            preserved[relative] = checksum
        alias_bindings = {}
        for row in report.get("retainedOriginalAliases", []):
            for relative, checksum in (
                (row["owner"], row["ownerSha256"]), (row["manifest"], row["manifestSha256"]),
            ):
                if relative in alias_bindings and alias_bindings[relative] != checksum:
                    raise ValueError(f"conflicting retained original bindings: {relative}")
                alias_bindings[relative] = checksum
        for relative, checksum in older_preserved.items():
            if relative in older_expected or (stage_root / pathlib.PurePosixPath(relative)).exists():
                raise ValueError(f"prior history conflicts with a staged publication: {relative}")
            if relative in preserved and preserved[relative] != checksum:
                raise ValueError(f"conflicting preserved source bindings: {relative}")
            preserved[relative] = checksum
        report_prefix = api.cw.storage_root(cfg, "reports", root=root).relative_to(root).as_posix()

        def publish_viewers():
            paths = normal_finish.viewers(api, root, cfg, space, cache, moves + normalization_moves, args.policy, profile=args.profile)
            report["viewerPaths"] = paths
            return paths

        journal = normal_transaction.publish(
            root, stage_root,
            [row["source"] for row in moves] + [row["source"] for row in normalizations if row["photoId"] in normalized_ids] + list(older_expected) + list(removed),
            journal=batch_run / "publication-journal.json",
            bindings=report["bindings"], profile=args.profile, run_id=run_id,
            expected_sources={**{row["source"]: row["sha256"] for row in moves}, **{row["source"]: row["sha256"] for row in normalizations if row["photoId"] in normalized_ids}, **older_expected, **report["updateTargetHashes"], **removed, **alias_bindings, **preserved},
            preserved_sources=preserved, finalizer=publish_viewers,
            report_directories=[
                report_prefix + "/library", report_prefix + "/comparisons/pairings",
                report_prefix + "/_assets",
            ],
        )
        for row in published:
            path = root / pathlib.PurePosixPath(row["native"])
            _refresh_content_digest(cache, path)
        cache.save()
        receipt = {
            "kind": "normal-import-receipt",
            "schemaVersion": 1,
            "status": "applied",
            "runId": run_id,
            "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "root": str(root),
            "profile": args.profile,
            "selectedPhotoIds": report["selectedPhotoIds"],
            "updatePhotoIds": sorted(set(args.update_photo_id)),
            "sourceHashes": report["sourceHashes"],
            "policyVersion": report["policyVersion"],
            "implementationSHA256": report["implementationSHA256"],
            "bindings": report["bindings"],
            "plan": report,
            "moves": moves,
            "normalizations": [row for row in normalizations if row["photoId"] in normalized_ids],
            "olderIncomingVersions": older_published,
            "journal": str(journal) if journal else None,
            "publication": True,
            "publishedNative": published,
            "viewerPaths": report["viewerPaths"],
            "preparationReport": str(prepared[0] / "index.html") if prepared else None,
            "pixelTreatment": "editing/framing deferred; raw is not certified clean" if args.profile == "fast" else "accepted selected-input native preparation; originals retained",
            "metadataDiagnosticsPreserved": report["membershipDiagnostics"],
        }
        _write_receipt(receipt_path, receipt)
        print(f"normal import applied: {journal or 'no file changes'}")
        print(f"receipt: {receipt_path}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"normal import apply failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
