"""Extracted reconciliation command implementation."""
import datetime
import json
import pathlib

from . import identity_families, identity_maintenance, maintenance, protection, rejections


def _save_report(output, report):
    output = pathlib.Path(output)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"cannot write reconciliation report {output}: {exc}") from exc


def run(args, api):
    """Plan Review and pool routing together, with one explicit apply boundary."""
    apply = getattr(args, 'apply', False)
    sandbox_root = bool(args.root and api.is_sandbox_working_path(args.root))
    policy = api.load_policy(args.policy)
    cfg = api.cw.load_cfg()
    root = pathlib.Path(args.root) if args.root else api.cw.work_root(cfg)
    if getattr(args, 'undo', None):
        rows = maintenance.undo_moves(root, args.undo, cfg, apply=apply)
        print(f"reconciliation undo: {len(rows)} move(s); {('applied' if apply else 'preview only')}")
        return
    if apply:
        maintenance.require_authorization(root, policy, args.sandbox_apply_draft)
    if sandbox_root:
        api.require_sandbox_cache(args.root, args.cache)
        if args.out:
            api.require_sandbox_output(args.root, args.out)
    cfg, st, work, cache, space = api.build(args)
    embed = args.embedder or api.Embedder()
    review_rows = api.load_review(cfg, work, space, cache, embed, st, include_empty=True)
    catalog = api.metadata.with_configured_anchors(
        api.metadata.load_catalog(api.metadata.path_for_root(work)), cfg, space.photos,
    )
    cores, locked_ids, diagnostics = api.frozen_identity_cores(
        space, catalog, photo_id_fn=api.metadata.photo_id_from_name,
        content_sha256_fn=api.metadata.content_sha256,
        additional_photos=[photo for _, _, photo in review_rows if photo is not None],
        policy=policy,
    )
    selected_names = list(cfg.get('photos', {}).values())
    for flow in cfg.get('flows', {}).values():
        selected_names.extend(flow.get('photos', {}).values())
    selected_ids = {photo_id for name in selected_names if isinstance(name, str) if (photo_id := api.metadata.photo_id_from_name(name))}
    candidates = []
    no_face = 0
    for photo in space.photos:
        if not api.matches(photo.key, st['pool']) or not photo.usable(st['minFace']) or api.junk_reason(photo, st):
            continue
        photo_id = api.metadata.photo_id_from_name(photo.name)
        candidates.append({
            "photoId": photo_id, "sourceFolder": photo.key, "sourceBucket": "Pool",
            "side": "Artists" if photo.key.startswith("Artists/") else "Prospects",
            "protected": bool(photo_id and (photo_id in locked_ids or photo_id in selected_ids)),
            "workflowSelected": bool(photo_id and photo_id in selected_ids),
            "identityProtected": bool(cores.get(photo.key, {}).get("identityProtected")),
            "vector": photo.vec,
            **rejections.photo_state(catalog, photo),
        })
    for folder, path, photo in review_rows:
        if photo is None:
            no_face += 1
            continue
        photo_id = api.metadata.photo_id_from_name(path.name)
        candidates.append({
            "photoId": photo_id, "sourceFolder": folder, "sourceBucket": "Review",
            "side": "Artists" if folder.startswith("Artists/") else "Prospects",
            "protected": bool(photo_id and (photo_id in locked_ids or photo_id in selected_ids)),
            "workflowSelected": bool(photo_id and photo_id in selected_ids),
            "identityProtected": False, "vector": photo.vec,
            **rejections.photo_state(catalog, photo),
        })
    outliers, outlier_evidence = identity_maintenance.split_candidates(
        space, cores, locked_ids, selected_ids, policy,
    )
    candidates.extend(outliers)
    photos_by_id = {
        api.metadata.photo_id_from_name(photo.name): photo
        for photo in space.photos
    }
    for candidate in outliers:
        photo = photos_by_id[candidate["photoId"]]
        candidate.update(rejections.photo_state(catalog, photo))
    taken = {name.split('/')[-1] for _, name, _ in api.cw.photo_folders(cfg, work)}
    report = api.plan_reconciliation(
        candidates, cores, assign=st["assign"], margin=st["margin"],
        cluster=policy["identityActions"]["identityClusterMinimumSimilarity"],
        minimum_cluster=st["minCluster"], cast_merge=policy["identityActions"]["autoMergeMinimum"],
        names_taken=taken, name_factory=api.invent_name, policy=policy,
    )
    report.update({
        "generatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "likeness-reconcile", "sourceRoot": str(work.resolve()),
        "scope": "Review, Various and qualified unprotected Gallery outliers; frozen established identities",
        "noUsableReviewPhotos": no_face, "coreDiagnostics": diagnostics,
        "policyVersion": policy["version"], "policyStatus": policy["status"],
        "outlierEvidence": outlier_evidence,
    })
    measured_photos = space.photos + [photo for _, _, photo in review_rows if photo is not None]
    report['moves'] = maintenance.proposed_moves(report, measured_photos, work)
    merges, merge_evidence = identity_maintenance.merge_actions(
        space, cores, catalog, locked_ids, selected_ids, policy, work, report["moves"],
    )
    identity_actions, category_evidence = identity_maintenance.category_transitions(
        space, cores, report, catalog, locked_ids, selected_ids, policy, work,
        measured_photos=measured_photos,
    )
    merge_folders = {action[key] for action in merges for key in ('sourceFolder', 'destinationFolder')}
    identity_actions = merges + [action for action in identity_actions if action['sourceFolder'] not in merge_folders]
    report['identityActions'] = identity_actions
    report['mergeEvidence'] = merge_evidence
    report['categoryEvidence'] = category_evidence
    report['moves'] = identity_maintenance.relocate_files(work, report['moves'], identity_actions)
    changed_folders = {
        pathlib.PurePosixPath(row[key]).parent.parent.as_posix()
        for row in report['moves'] for key in ("source", "destination")
    }
    protection_actions, protection_evidence = protection.plan_protection(
        space, cores, catalog, policy, root=work,
        moving_photo_ids={row.get("photoId") for row in report['moves']},
        moving_folders=changed_folders, selected_ids=selected_ids,
        additional_photos=[photo for _, _, photo in review_rows if photo is not None],
    )
    report['metadataActions'], report['familyEvidence'] = identity_families.augment_actions(
        protection_actions, space, cores, catalog, policy, work, changed_folders=changed_folders,
    )
    report['protectionEvidence'] = protection_evidence
    print(
        f"Reconciliation {'apply' if apply else 'preview'}: {report['candidateCount']} candidate(s), "
        f"{report['coreFolders']} frozen identity core(s), {report['assignedCount']} suggested destination(s), "
        f"{report['heldCount']} held, {len(report['clusters'])} candidate cluster(s)."
    )
    print(f"{len(report['moves'])} file move(s) proposed. Preview never changes images or catalogue data.")
    print(f'{len(identity_actions)} established identity action(s) proposed (merges/category transitions).')
    print(f'{len(protection_actions)} automatic protection metadata change(s) proposed.')
    print(f'{len(report["metadataActions"])} combined protection/name/family metadata change(s) proposed.')
    if not apply:
        print('No images or catalogue data are changed; the embedding cache may be updated.')
    print(f"likeness policy: {policy['version']} ({policy['status']})")
    for row in report['assignments']:
        score = f"{row['score']:.2f}" if row['score'] is not None else 'cluster'
        print(f"  {row['photoId']}  {row['sourceBucket']} {row['sourceFolder']} -> {row['destination']} ({score}; {row['reason']})")
    for row in report['held']:
        best_match = row.get('bestMatch')
        best_score = row.get('bestScore')
        best_text = f'; best match {best_match} ({best_score:.2f})' if best_match and best_score is not None else ''
        print(f"  HOLD {row.get('photoId') or '<no stable ID>'}  {row.get('sourceBucket') or 'unknown'} {row.get('sourceFolder') or ''}: {row['reason']}{best_text}")
    for diagnostic in diagnostics:
        print(f'  CORE WARNING {diagnostic}')
    if args.out:
        _save_report(args.out, report)
        print(f'report written: {args.out}')
    if apply:
        journal = maintenance.apply_moves(
            work, report["moves"], policy, cfg, sandbox_override=args.sandbox_apply_draft,
            identity_actions=identity_actions,
            metadata_actions=report['metadataActions'],
        )
        print(f'reconciliation applied: {journal}' if journal else 'reconciliation: no moves required')
        if journal:
            report["journal"] = str(journal)
            report["postApplyCheck"] = identity_maintenance.check_applied_membership(
                work, measured_photos, report["moves"], identity_actions, st, selected_ids, policy,
            )
            receipt = pathlib.Path(journal).with_name("check-" + pathlib.Path(journal).name)
            _save_report(receipt, report["postApplyCheck"])
            if args.out:
                _save_report(args.out, report)
            print(f"final-core check: {report['postApplyCheck']['status']}; {receipt}")
    return report
