"""One scoped policy check and final evidence/viewers, without iterative regrouping."""
import copy
import html
import pathlib

from . import identity_families, metadata
from .policy import evaluate_photo_consistency
from .reconciliation import frozen_identity_cores


def cores(api, space, catalog, policy):
    eligible = api.Space(
        [photo for photo in space.photos if photo.path.parent.name == "gallery"],
        space.st, mean=space.mean,
    )
    result, _locked, diagnostics = frozen_identity_cores(
        eligible, catalog, photo_id_fn=metadata.photo_id_from_name,
        content_sha256_fn=metadata.content_sha256, policy=policy,
        require_single_face="castAdmission" in policy,
    )
    return {key: value for key, value in result.items() if not key.startswith("Various")}, diagnostics


def comparisons(core_map):
    return {
        folder: [
            {"folder": other, "score": float(core["vector"] @ candidate["vector"])}
            for other, candidate in sorted(core_map.items(),
                                           key=lambda row: (-float(core["vector"] @ row[1]["vector"]), row[0]))
            if other != folder and candidate["side"] == core["side"]
        ] for folder, core in sorted(core_map.items())
    }


def check_batch(api, space, catalog, policy, moves, *, update_ids=()):
    frozen, diagnostics = cores(api, space, catalog, policy)
    evidence, corrections, recommendations = [], [], []
    protected_folders = {
        person["folder"] for person in catalog.get("people", {}).values() if person.get("protected")
    }
    photos = {metadata.photo_id_from_name(photo.name): photo for photo in space.photos}
    for folder, core in sorted(frozen.items()):
        for name, score in core["photoScores"].items():
            evidence.append({
                "folder": folder, "photo": name, "score": score,
                "coreMember": metadata.photo_id_from_name(name) in core["corePhotoIds"],
                "scope": "existing evidence only; existing photos are not correction candidates",
            })
    checked = []
    for move in moves:
        row = dict(move)
        folder = pathlib.PurePosixPath(move["destination"]).parent.parent.as_posix()
        if move.get("castAdmission") or move.get("normalAdmission"):
            if move.get("castAdmission"):
                from .normal_admission import validate_move

                validate_move(move, policy)
            elif pathlib.PurePosixPath(move["destination"]).parent.name == "gallery" and move.get("destinationType") == "existing":
                route = move["routingEvidence"]
                rules = policy["categoryPolicies"][folder.split("/", 1)[0]]
                if route["winner"] != folder or route["score"] < rules["photoRouteMinimum"] or route["margin"] < rules["photoRouteMargin"]:
                    raise ValueError("bound normal Gallery admission does not satisfy its selected receiving gates")
            evidence.append({
                "photoId": move["photoId"], "folder": folder,
                "decision": "retain-bound-normal-admission",
                "referenceVersion": move.get("referenceVersion"),
                "scope": "validate final matching-round admission, not legacy initial-core reclassification",
            })
            checked.append(row)
            continue
        photo = photos[move["photoId"]]
        core = frozen.get(folder)
        score = float(photo.vec @ core["vector"]) if core and photo.vec is not None else None
        count = max(1, len(core["photoScores"]) + int(photo.name not in core["photoScores"])) if core else 1
        decision = evaluate_photo_consistency(
            folder.split("/")[0], score=score, usable_photo_count=count,
            identity_protected=bool(core and core["identityProtected"]),
            photo_protected=bool(catalog["photos"].get(move["photoId"], {}).get("protected")),
            policy=policy,
        )
        evidence.append({
            "photoId": move["photoId"], "folder": folder, "score": score,
            "referenceAvailable": core is not None, "decision": decision,
        })
        if decision["decision"] in ("review", "split-review") and move["photoId"] not in update_ids:
            path = pathlib.PurePosixPath(move["destination"])
            proposed = (path.parent.parent / "review" / path.name).as_posix()
            source = pathlib.PurePosixPath(move["source"]) if move.get("auditOnly") else None
            rules = policy["categoryPolicies"].get(source.parts[0], {}) if source else {}
            protected_audit = source is not None and source.parent.name == "gallery" and (
                rules.get("identityProtectedByDefault")
                or source.parent.parent.as_posix() in protected_folders
                or not rules.get("automaticSplitEnabled", False)
            )
            if protected_audit:
                recommendations.append({
                    "photoId": move["photoId"], "proposedDestination": proposed,
                    "retainedDestination": row["destination"], "policy": decision,
                    "reason": "recommendation only: identity protection or disabled automatic split forbids Gallery removal",
                })
            else:
                row["destination"] = proposed
                row["reason"] += "; frozen consistency policy requires Review"
                corrections.append({"photoId": move["photoId"], "destination": row["destination"], "policy": decision})
        checked.append(row)
    return checked, {
        "passCount": 1, "frozenCoreDiagnostics": diagnostics,
        "frozenRivals": comparisons(frozen), "lowMemberChecks": evidence,
        "corrections": corrections, "recommendations": recommendations,
        "scope": "only selected incoming photos are eligible for correction; explicit updates retain their owner",
    }


def projected(api, root, stage_root, space, cache, moves):
    by_id = {row["photoId"]: row for row in moves}
    photos = []
    for photo in space.photos:
        photo_id = metadata.photo_id_from_name(photo.name)
        move = by_id.get(photo_id)
        if move:
            path = pathlib.Path(stage_root) / pathlib.PurePosixPath(move["destination"])
            relative = pathlib.PurePosixPath(move["destination"])
            group, name = relative.parts[0], relative.parts[-3] if relative.parts[0] != "Various" else "Various"
            digest = cache.sha(path)
            data = cache.emb.get(digest)
            if data is None:
                raise ValueError(f"published native lacks content-bound measurement: {relative}")
            photos.append(api.Photo(path, group, name, digest, data))
        else:
            photos.append(photo)
    return api.Space(photos, space.st, mean=space.mean)


def family_and_final(api, root, stage_root, projected_space, catalog, policy, moves):
    final, diagnostics = cores(api, projected_space, catalog, policy)
    actions, family_evidence = identity_families.plan(
        projected_space, final, catalog, policy, root,
    )
    affected = {pathlib.PurePosixPath(row["destination"]).parent.parent.as_posix() for row in moves}
    allowed = {pid for pid, person in catalog["people"].items() if person["folder"] in affected}
    family_members = {}
    for action in actions:
        family = action["after"].get("family")
        if family:
            family_members.setdefault(family["id"], set()).add(action["personId"])
    updated = copy.deepcopy(catalog)
    applied = []
    existing = metadata.load_catalog(metadata.path_for_root(root))["people"]
    for action in actions:
        family = action["after"].get("family")
        if action["personId"] not in allowed or (
            family and not family_members[family["id"]] <= allowed
        ):
            continue
        prior = existing.get(action["personId"])
        if prior and any(action["after"].get(field) != prior.get(field) for field in ("displayName", "folder", "folderHistory")):
            continue
        updated["people"][action["personId"]] = action["after"]
        applied.append(action)
    metadata.validate_catalog(updated)
    metadata.save_catalog(updated, pathlib.Path(stage_root) / ".likeness-library.json")
    return {
        "finalRivals": comparisons(final), "finalCoreDiagnostics": diagnostics,
        "finalFamilyEvidence": family_evidence, "finalFamilyActions": applied,
        "unrelatedPeopleUnchanged": all(
            updated["people"][pid] == person for pid, person in catalog["people"].items() if pid not in allowed
        ),
    }


def viewers(api, root, cfg, space, cache, moves, policy_path=None, *, profile="lean"):
    from tools.art import people_gallery
    from likeness_library import preparation_provenance, review_gallery, verification_reads
    from . import normal_history

    paths = {row["photoId"]: pathlib.Path(root) / pathlib.PurePosixPath(row["destination"]) for row in moves}
    photos = []
    for photo in space.photos:
        path = paths.get(metadata.photo_id_from_name(photo.name), photo.path)
        relative = path.relative_to(root)
        group = relative.parts[0]
        name = relative.parts[-3] if group != "Various" else "Various"
        digest = cache.sha(path)
        data = cache.emb.get(digest)
        if data is None:
            if metadata.photo_id_from_name(photo.name) in paths:
                raise ValueError(f"viewer native lacks current measured evidence: {path}")
            data = {"faces": -1, "normalDeferredMeasurement": True}
        photos.append(api.Photo(path, group, name, digest, data))
    final = api.Space(photos, space.st, mean=space.mean)
    final.cfg, final.work = cfg, pathlib.Path(root)
    context = (cfg, final.st, pathlib.Path(root), cache, final)
    arguments = ["--root", str(root), "--no-renders"]
    if policy_path:
        arguments += ["--policy", str(policy_path)]
    cache_only = lambda _path: {"faces": -1, "normalDeferredMeasurement": True}
    out = api.cw.storage_root(cfg, "reports", root=root) / "library"
    # Match both writers' canonical readers, including Review's nested FAST probe.
    with verification_reads.session(root, label="Shared normal viewer inputs"):
        provenance = preparation_provenance.build_index(root, out, [], "general", cfg=cfg)
        if people_gallery.main(arguments, context=context, provenance=provenance) != 0 or review_gallery.main(
            arguments, context=context, provenance=provenance, embed=cache_only,
        ) != 0:
            raise ValueError("shared normal viewer publication failed")
    (out / "native-generations.html").write_text(normal_history.render(root), encoding="utf-8")
    treatment = (
        "FAST: image editing and 944 framing are deferred; raw pixels are not certified clean."
        if profile == "fast" else
        "Accepted selected native preparation. Held originals remain unchanged and are not certified clean."
    )
    gallery = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Native Gallery</title></head><body>",
        "<h1>Native Gallery</h1><p>" + treatment + "</p>",
        '<p><a href="people_gallery.html">Overview and identity scores</a> · '
        '<a href="people_gallery_review.html">Photo Review</a> · '
        '<a href="native-generations.html">Immutable native history</a> · '
        '<a href="intake_runs.html">Recipe details</a></p>',
    ]
    for photo in final.photos:
        uri = photo.path.as_uri()
        photo_id = metadata.photo_id_from_name(photo.name)
        gallery.append(
            '<figure style="display:inline-block;vertical-align:top;width:260px">'
            '<a href="' + html.escape(uri, quote=True) + '"><img loading="lazy" style="max-width:250px;max-height:300px" src="' +
            html.escape(uri, quote=True) + '"></a><figcaption>' + html.escape(photo.key + " / " + photo.name) +
            '<br><a href="people_gallery_review.html?photo=' + html.escape(photo_id or "", quote=True) +
            '">Review / scores</a></figcaption></figure>'
        )
    (out / "gallery.html").write_text("\n".join(gallery + ["</body></html>"]), encoding="utf-8")
    (out / "index.html").write_text(
        "<!doctype html><html><head><title>Normal library</title></head><body><h1>Normal library</h1>"
        '<a href="gallery.html">Native Gallery</a> <a href="people_gallery.html">Overview</a> '
        '<a href="people_gallery_review.html">Photo Review</a> '
        '<a href="native-generations.html">Immutable native generations</a> '
        '<a href="intake_runs.html">Preparation history</a></body></html>', encoding="utf-8",
    )
    return [str(out / name) for name in (
        "index.html", "gallery.html", "people_gallery.html", "people_gallery_review.html", "native-generations.html",
    )]
