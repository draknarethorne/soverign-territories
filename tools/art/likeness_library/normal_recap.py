"""Report-only adapter from saved SIMPLE receipts to movement recap and audit pages."""
import argparse
import collections
import hashlib
import html
import json
import math
import pathlib
import re
import sys
import time
import urllib.parse

if not __package__:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
    from tools.art.likeness_library import gallery_chrome, policy, rebase_recap
else:
    from . import gallery_chrome, policy, rebase_recap

SINGLE_PHOTO_LABEL = "single photo – not yet scoreable"


def _sha(payload):
    return hashlib.sha256(payload).hexdigest()


def _relative(value):
    path = pathlib.PurePosixPath(value)
    if not value or "\\" in value or path.is_absolute() or ".." in path.parts or ":" in value:
        raise ValueError(f"unsafe saved report path: {value}")
    return path


def _digest_value(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("invalid saved SHA-256")
    return value


def _under(root, path):
    path = pathlib.Path(path).absolute()
    path.relative_to(root)
    if path.resolve() != path or root.resolve() != root:
        raise ValueError(f"linked report input/output: {path}")
    return path


def _script(page, identifier):
    match = re.search(
        rf'<script\b[^>]*\bid="{re.escape(identifier)}"[^>]*>(.*?)</script>', page, re.S,
    )
    return json.loads(match[1]) if match else None


def collect(receipt_path, *, read_bytes=None):
    receipt_path = pathlib.Path(receipt_path).absolute()
    payload = receipt_path.read_bytes() if read_bytes is None else read_bytes(receipt_path)
    if payload is None:
        raise ValueError(f"saved receipt unavailable: {receipt_path}")
    receipt = json.loads(payload)
    if receipt.get("kind") not in {"normal-rebase-receipt", "normal-rebase-preview"}:
        raise ValueError("expected a saved normal-rebase receipt or preview")
    if receipt.get("schemaVersion") != 1 or receipt.get("status") not in {"applied", "preview"}:
        raise ValueError("only schema1 applied/preview receipts can produce a recap")
    root = pathlib.Path(receipt["root"]).absolute()
    _under(root, receipt_path)
    viewers = receipt.get("viewerPaths") or receipt["plan"].get("viewerPaths") or []
    review_paths = [pathlib.Path(path) for path in viewers if pathlib.Path(path).name == "people_gallery_review.html"]
    library = _under(root, review_paths[0].parent if review_paths else receipt_path.parent.parent / "library")
    plan = receipt["plan"]
    sources = plan["sourceRows"]
    hashes = plan["sourceHashes"]
    if not isinstance(sources, list) or not isinstance(hashes, dict):
        raise ValueError("saved source rows and hashes are required")
    if receipt.get("sourceHashes", hashes) != hashes:
        raise ValueError("receipt and plan disagree on source hashes")
    moves = plan["moves"]
    if receipt.get("moves", moves) != moves:
        raise ValueError("receipt and plan disagree on moves")
    by_source = {move["source"]: move for move in moves}
    if len(by_source) != len(moves):
        raise ValueError("duplicate saved move source")
    native = {item["native"]: item["sha256"] for item in receipt.get("publishedNative", [])}
    if len(native) != len(receipt.get("publishedNative", [])):
        raise ValueError("duplicate published native path")
    assignments = {item["photoId"]: item for item in plan.get("assignments", [])}
    assignments.update({item["photoId"]: item for item in plan.get("held", [])})
    archives = plan.get("duplicateArchives", {})
    junk = plan.get("junkDispositions", {})
    junk_prefix = _relative(plan["junkStorage"]) if junk else None
    source_rows = {row["source"]: row for row in sources}
    collision_groups = collections.defaultdict(list)
    content_archives = []
    rows = []
    seen = set()
    for source in sources:
        relative = source["source"]
        _relative(relative)
        if relative in seen or source["sourceHash"] != hashes.get(relative):
            raise ValueError(f"duplicate or unbound source row: {relative}")
        seen.add(relative)
        _digest_value(source["sourceHash"])
        move = by_source.get(relative)
        archive = archives.get(relative)
        discarded = junk.get(relative)
        if archive:
            keeper = source_rows.get(archive["selectedSource"], {})
            cross_id = "selectedPhotoId" in archive
            proof = archive.get("retainedOriginalProof")
            if proof:
                bytes_match = (
                    source.get("retainedOriginalProof") == proof
                    and keeper.get("retainedContentKeeper") is True
                    and keeper.get("retainedOriginal") == _relative(proof["path"]).as_posix()
                    and keeper.get("retainedManifest") == _relative(proof["manifest"]).as_posix()
                    and keeper.get("retainedSourceHash") == archive["sha256"]
                    and keeper.get("retainedCurrentHash") == keeper.get("sourceHash") == proof["keeperNativeSha256"]
                    and hashes.get(keeper.get("source")) == proof["keeperNativeSha256"] != archive["sha256"]
                    and keeper.get("source") not in junk
                )
            else:
                bytes_match = keeper.get("sourceHash") == archive["sha256"] and keeper.get("contentVoteCanonical") is True
            keeper_matches = (
                source.get("crossIdExactArchive") is True
                and keeper.get("photoId") == archive["selectedPhotoId"] != archive["photoId"]
                and bytes_match
                and keeper["source"] not in archives
            ) if cross_id else (keeper.get("photoId") == archive["photoId"] and keeper.get("collisionRule"))
            if (
                move or archive["source"] != relative or archive["photoId"] != source["photoId"]
                or archive["sha256"] != source["sourceHash"]
                or not keeper_matches or (proof and not cross_id)
                or source.get("sourceStatus") != "duplicate-archive"
                or _relative(archive["destination"]).parts[0] != "_duplicates"
                or (receipt["status"] == "applied" and native.get(archive["destination"]) != archive["sha256"])
            ):
                raise ValueError(f"unbound duplicate archive evidence: {relative}")
            if cross_id:
                content_archives.append(archive)
        if (archive and "selectedPhotoId" not in archive) or source.get("collisionRule") or source.get("versionConflict"):
            collision_groups[source["photoId"]].append((source, archive))
        if discarded and (
            archive or move or discarded["source"] != relative or discarded["photoId"] != source["photoId"]
            or discarded["sha256"] != source["sourceHash"] or source["group"] != "Various"
            or source["sourceStatus"] != "confirmed-no-face-junk" or discarded["faces"] != 0
            or _relative(discarded["destination"]) != junk_prefix / _relative(relative)
            or (receipt["status"] == "applied" and native.get(discarded["destination"]) != discarded["sha256"])
        ):
            raise ValueError(f"unbound no-face junk evidence: {relative}")
        if move and (move["photoId"] != source["photoId"] or move["sha256"] != source["sourceHash"]):
            raise ValueError(f"move does not bind its source: {relative}")
        disposition = archive or discarded
        destination = (disposition or move)["destination"] if disposition or move else relative
        _relative(destination)
        if receipt["status"] == "applied" and move and destination not in native:
            raise ValueError(f"published native evidence missing: {destination}")
        if destination in native:
            _digest_value(native[destination])
        old, old_bucket = rebase_recap.person_and_bucket(relative)
        new, new_bucket = rebase_recap.person_and_bucket(destination)
        if archive:
            new, new_bucket = "_duplicates", "archive"
        if discarded:
            new, new_bucket = plan["junkStorage"], "junk"
        assignment = {} if disposition else assignments.get(source["photoId"], {})
        row = dict.fromkeys((
            "preview", "detail", "score", "bestMatch", "bestScore", "nearestCast",
            "nearestCastScore", "secondCast", "secondCastScore", "castMargin",
            "castSeedCore", "castSeedScore", "clusterId", "groupSize", "destinationType",
            "preparationOutcome", "preparedPath",
        ))
        row.update(
            source=relative, destination=destination, photoId=source["photoId"],
            sha256=source["sourceHash"], preparedSHA256=native.get(destination, source["sourceHash"]),
            originalFolder=old, oldPerson=old, newPerson=new, oldBucket=old_bucket, newBucket=new_bucket,
            reason=(disposition or move or source).get("reason", "existing owner retained"),
            kind=("duplicate-archive" if archive else "junk-disposition" if discarded else
                  rebase_recap.change_kind({"source": relative, "destination": destination})),
            placementKind="Duplicate archive (non-voting)" if archive else
            "Recoverable junk (no detected face)" if discarded else
            rebase_recap._placement_kind(relative, destination, old, new, old_bucket, new_bucket),
            duplicateArchive=bool(archive),
            junkDisposition=bool(discarded),
            renamed=pathlib.PurePosixPath(relative).stem != pathlib.PurePosixPath(destination).stem,
            converted=pathlib.PurePosixPath(relative).suffix.lower() != pathlib.PurePosixPath(destination).suffix.lower(),
            topCast=[], bestScore=assignment.get("score", assignment.get("bestScore")),
            bestMatch=assignment.get("bestMatch"), clusterId=assignment.get("clusterId"),
            faceQuality=assignment.get("faceQuality") or (move or {}).get("faceQuality"),
            singlePhoto=bool(assignment.get("singlePhoto")),
            decisionReason=assignment.get("reason"),
        )
        rows.append(row)
    if (set(by_source) | set(archives) | set(junk)) - seen or seen != set(hashes):
        raise ValueError("saved moves/source hashes are outside the complete source census")
    destinations = collections.Counter(row["destination"] for row in rows)
    aliases = plan.get("exactAliasTargets", {})
    updates = plan.get("incomingUpdates", {})
    update_targets = {update["previousSource"] for update in updates.values()}
    repeated = {path for path, count in destinations.items() if count > 1}
    if (repeated != set(aliases) | update_targets or set(aliases) & update_targets
            or len(update_targets) != len(updates)
            or any(destinations[path] != 2 for path in repeated)):
        raise ValueError("repeated destinations lack exact-alias coalescence evidence")
    for target, alias in aliases.items():
        matching = [row for row in rows if row["destination"] == target]
        if ({row["source"] for row in matching} != {target, alias["source"]}
                or any(row["sha256"] != alias["sha256"] for row in matching)):
            raise ValueError(f"invalid exact-alias coalescence: {target}")
    for photo_id, update in updates.items():
        target, incoming = update["previousSource"], update["source"]
        matching = {row["source"]: row for row in rows if row["destination"] == target}
        if (set(matching) != {target, incoming}
                or any(row["photoId"] != photo_id for row in matching.values())
                or matching[target]["sha256"] != update["previousHash"]
                or matching[incoming]["sha256"] != update["sourceHash"]
                or update["previousHash"] == update["sourceHash"]
                or pathlib.PurePosixPath(target).parent.parent.as_posix() != update["owner"]
                or source_rows[target].get("sourceStatus") != "preserved-version"
                or source_rows[target].get("selectedSource") != incoming
                or source_rows[incoming].get("sourceStatus") != "incoming-update"):
            raise ValueError(f"invalid saved incoming replacement: {target}")
        matching[target].update(
            supersededVersion=True, preparedSHA256=update["previousHash"],
            kind="superseded-version", placementKind="Previous native version retained in history",
            reason="previous native superseded by selected incoming version: " + incoming,
        )
    old_people = {row["oldPerson"] for row in rows}
    new_people = {row["newPerson"] for row in rows if not (row["duplicateArchive"] or row["junkDisposition"])}
    data = {
        "normalReport": True, "run": str(receipt_path), "runId": receipt["runId"],
        "workingRoot": str(root), "libraryRoot": str(library), "status": receipt["status"], "rows": rows,
        "createdAt": receipt.get("createdAt"), "profile": receipt.get("profile"),
        "castSeedPolicy": "saved SIMPLE reference policy",
        "sourceManifestSHA256": _sha(json.dumps(hashes, sort_keys=True).encode("utf-8")),
        "sourceOverlaySHA256": None, "newIdentities": sorted(new_people - old_people),
        "emptiedIdentities": sorted(old_people - new_people), "expectations": {},
        "physicalSources": len(rows), "physicalDestinations": len(destinations),
        "coalescedAliases": len(aliases), "supersededVersions": len(updates),
        "duplicateArchives": len(archives),
        "contentArchives": content_archives,
        "unresolvedDuplicateIds": plan.get("unresolvedDuplicateIds", []),
        "collisionGroups": {pid: group for pid, group in collision_groups.items() if len(group) > 1},
        "recordedAudit": plan.get("frozenConsistencyCheck", {}),
        "phaseLog": plan.get("phaseLog", []),
        "phaseCounts": {key: plan[key] for key in (
            "sourceRowCount", "canonicalInputCount", "exactAliasCount", "heldSourceCount",
            "preparationInputCount", "preparedReferenceCount", "preparedCandidateCount",
            "coreCount", "candidateCount", "assignedCount", "heldCount",
            "freshGalleryCount", "freshSelectedCount", "freshBlockedCount",
            "freshUnavailableCount", "freshNonVotingCount",
            "freshCastSeedIdentityCount", "freshCastSeedKeptCount", "freshCastSeedReleaseCount",
            "freshCastSeedReturnedCount", "freshCastWorkflowReplacementCount",
            "settlePassCount", "settleReleasedCount", "settleMovedCount", "settleDidNotSettleCount",
        ) if key in plan},
        "freshCastSeed": plan.get("freshCastSeed"),
        "retiredIdentityFolders": _retired_identity_folders(receipt, plan),
        "settle": plan.get("settle"),
        "phaseMoves": len(moves), "phaseArchives": len(archives), "phaseJunk": len(junk),
        "phaseViewers": len(viewers) if receipt["status"] == "applied" else None,
        "preparationReusedFromPreview": plan.get("preparationReusedFromPreview"),
        "referenceSnapshots": plan.get("referenceSnapshots", {}),
        "groupRivals": plan.get("finalComparisonAndFamily", {}).get("finalRivals", {}),
        "auditRecords": [], "snapshotDiagnostics": [], "snapshotMatched": 0, "snapshotIdUnavailable": 0,
        "redScoreCutoff": None, "redScoreCount": None, "unscoredCount": 0, "singlePhotoCount": 0,
        "inputs": {str(receipt_path): _sha(payload)},
        "inputBytes": len(payload),
    }
    if receipt["status"] == "applied":
        _attach_review(data, read_bytes=read_bytes)
    else:
        data["snapshotDiagnostics"].append("Preview only: current Review is not final-placement evidence.")
    return data


def _attach_review(data, *, read_bytes=None):
    root = pathlib.Path(data["workingRoot"])
    review = _under(root, pathlib.Path(data["libraryRoot"]) / "people_gallery_review.html")
    payload = (review.read_bytes() if review.is_file() else None) if read_bytes is None else read_bytes(review)
    if payload is None:
        data["snapshotDiagnostics"].append("Review snapshot unavailable; only saved receipt audit is shown.")
        return
    data["inputs"][str(review)] = _sha(payload)
    data["inputBytes"] += len(payload)
    page = payload.decode("utf-8")
    records = _script(page, "review-data")
    if records is None:
        data["snapshotDiagnostics"].append("Review snapshot has no recorded photo data; no scores inferred.")
        return
    if not isinstance(records, list):
        raise ValueError("Review snapshot photo data must be an array")
    snapshot_policy = _script(page, "likeness-policy-data")
    if snapshot_policy is not None:
        if not isinstance(snapshot_policy, dict) or "scoreBands" not in snapshot_policy:
            raise ValueError("Review snapshot policy must contain scoreBands")
        policy.validate_score_bands(snapshot_policy["scoreBands"])
        data["redScoreCutoff"] = snapshot_policy["scoreBands"]["red"]["maximumExclusive"]
        data["redScoreCount"] = 0
    by_path = {}
    for record in records:
        path = (pathlib.PurePosixPath(record["folder"]) / record["bucket"].lower() / record["name"]).as_posix()
        _relative(path)
        if path in by_path:
            raise ValueError(f"duplicate Review snapshot path: {path}")
        by_path[path] = record
    rows_by_destination = collections.defaultdict(list)
    for row in data["rows"]:
        if not (row.get("supersededVersion") or row["duplicateArchive"] or row.get("junkDisposition")):
            rows_by_destination[row["destination"]].append(row)
    for destination, rows in rows_by_destination.items():
        record = by_path.get(destination)
        if (record is None or record.get("contentSha256") != rows[0]["preparedSHA256"]
                or record.get("photoId") not in (None, rows[0]["photoId"])):
            data["snapshotDiagnostics"].append(f"Missing/stale Review evidence: {destination}")
            continue
        data["snapshotMatched"] += 1
        if record.get("photoId") is None:
            data["snapshotIdUnavailable"] += 1
        for row in rows:
            thumb = record.get("thumbnail")
            if thumb and not urllib.parse.urlsplit(thumb).scheme:
                row["preview"] = str(_under(root, review.parent / pathlib.Path(*_relative(thumb).parts)))
        rivals = record.get("closestMatches") or []
        score = record.get("score")
        red = score is not None and snapshot_policy is not None and policy.score_band(score, snapshot_policy) == "red"
        higher = score is not None and any(item.get("score") is not None and item["score"] > score for item in rivals)
        context = record.get("scoreContext") or {}
        flags = []
        if higher:
            flags.append("higher rival (diagnostic, not move permission)")
        if record.get("workflowSelected") and not context.get("coreMember"):
            flags.append("workflow reference outside active core")
        if (record.get("identityProtected") or record.get("identityAnchor") or record.get("workflowSelected")) and higher:
            flags.append("protected/reference photo with higher rival")
        if score is None and context.get("singlePhoto"):
            flags.append(SINGLE_PHOTO_LABEL)
            data["singlePhotoCount"] = data.get("singlePhotoCount", 0) + 1
        elif score is None:
            flags.append("own score unavailable")
            data["unscoredCount"] += 1
        if red:
            flags.append("red own-core similarity")
            data["redScoreCount"] += 1
        if record.get("derivativeDiagnostics"):
            flags.append("image/lineage diagnostic")
        data["auditRecords"].append({
            "row": rows[0], "record": record, "flags": flags, "score": score, "rivals": rivals,
        })
    _attach_workflow_replacement_candidates(data)


def _attach_workflow_replacement_candidates(data):
    gallery_by_owner = collections.defaultdict(list)
    if data["redScoreCutoff"] is not None:
        for item in data["auditRecords"]:
            if (item["row"]["newBucket"] == "gallery" and item["score"] is not None
                    and item["score"] >= data["redScoreCutoff"]):
                gallery_by_owner[item["row"]["newPerson"]].append(item)
    selected_ids = {
        binding["photoId"] for binding in data.get("workflowConfig", {}).get("bindings", [])
        if binding["photoId"]
    }
    for item in data["auditRecords"]:
        item["workflowReplacementCandidates"] = []
        if ("red own-core similarity" not in item["flags"]
                or not (item["record"].get("workflowSelected") or item["record"].get("photoId") in selected_ids)):
            continue
        candidates = [
            other for other in gallery_by_owner[item["row"]["newPerson"]]
            if other["score"] > item["score"]
            and other["row"]["photoId"] != item["row"]["photoId"]
            and other["record"]["contentSha256"] != item["record"]["contentSha256"]
        ]
        item["workflowReplacementCandidates"] = sorted(
            candidates, key=lambda other: (-other["score"], other["row"]["destination"]),
        )


def _bind_red_native_evidence(data):
    if data["status"] != "applied" or data["redScoreCutoff"] is None or data["snapshotDiagnostics"]:
        raise ValueError("red native binding requires an applied receipt and complete, scored Review evidence")
    root = pathlib.Path(data["workingRoot"])
    reds = [item for item in data["auditRecords"] if "red own-core similarity" in item["flags"]]
    bound = {}
    paths_by_id = {}
    for red in reds:
        core = [
            item for item in data["auditRecords"]
            if item["row"]["newPerson"] == red["row"]["newPerson"]
            and (item["record"].get("scoreContext") or {}).get("coreMember") is True
        ]
        core_size = (red["record"].get("scoreContext") or {}).get("coreSize")
        if type(core_size) is not int or core_size < 1 or len(core) != core_size:
            raise ValueError(f"incomplete Review core for red photo: {red['row']['destination']}")
        for item in [red, *core, *red["workflowReplacementCandidates"]]:
            row, record = item["row"], item["record"]
            if not record.get("photoId") or record["photoId"] != row["photoId"]:
                raise ValueError(f"unbound Review photo ID: {row['destination']}")
            path = _under(root, root.joinpath(*_relative(row["destination"]).parts))
            if record["photoId"] in paths_by_id and paths_by_id[record["photoId"]] != path:
                raise ValueError(f"ambiguous Review photo ID: {record['photoId']}")
            paths_by_id[record["photoId"]] = path
            if str(path) in bound:
                if bound[str(path)] != row["preparedSHA256"]:
                    raise ValueError(f"conflicting Review native hashes: {row['destination']}")
                continue
            digest = _sha(path.read_bytes())
            if digest != row["preparedSHA256"]:
                raise ValueError(f"current native differs from Review evidence: {row['destination']}")
            bound[str(path)] = digest
    data["inputs"].update(bound)
    data["inputBytes"] += sum(pathlib.Path(path).stat().st_size for path in bound)
    data["redNativeBindings"] = len(bound)


def _attach_workflow_selection_bindings(data, *, configuration_path=None):
    from tools.art.likeness_library import actions

    config_path = pathlib.Path(
        actions.cw.CFG_PATH if configuration_path is None else configuration_path
    ).absolute()
    schema_path = pathlib.Path(actions.cw.CFG_SCHEMA_PATH).absolute()
    config_payload = config_path.read_bytes()
    schema_payload = schema_path.read_bytes()
    cfg = actions.cw.validate_config(json.loads(config_payload))
    bindings = actions.selected_photo_bindings(cfg)
    data["inputs"].update({
        str(config_path): _sha(config_payload),
        str(schema_path): _sha(schema_payload),
    })
    data["inputBytes"] += len(config_payload) + len(schema_payload)
    data["workflowConfig"] = {
        "path": str(config_path),
        "rootMatches": pathlib.Path(actions.cw.work_root(cfg)).resolve() == pathlib.Path(data["workingRoot"]).resolve(),
        "unidentified": sum(item["photoId"] is None for item in bindings),
        "bindings": bindings,
    }
    _attach_workflow_replacement_candidates(data)


def _red_candidate_evidence(data):
    results = []
    for item in data["auditRecords"]:
        if "red own-core similarity" not in item["flags"]:
            continue
        row, record = item["row"], item["record"]
        members = [
            {"photoId": other["record"]["photoId"], "path": other["row"]["destination"],
             "sha256": other["row"]["preparedSHA256"]}
            for other in data["auditRecords"]
            if other["row"]["newPerson"] == row["newPerson"]
            and (other["record"].get("scoreContext") or {}).get("coreMember") is True
        ]
        result = {
            "photoId": record["photoId"], "currentPath": row["destination"],
            "owner": row["newPerson"], "bucket": row["newBucket"],
            "nativeSha256": row["preparedSHA256"], "score": item["score"],
            "redMaximumExclusive": data["redScoreCutoff"],
            "scoreContext": record.get("scoreContext"), "comparison": record.get("comparison"),
            "reviewCore": sorted(members, key=lambda member: member["path"]),
            "identityProtected": record.get("identityProtected"),
            "photoProtectionInfo": record.get("photoProtectionInfo"),
            "identityAnchor": record.get("identityAnchor"),
            "workflowSelected": record.get("workflowSelected"),
            "workflowReplacementCandidates": [
                {"photoId": other["record"]["photoId"],
                 "currentPath": other["row"]["destination"],
                 "nativeSha256": other["row"]["preparedSHA256"],
                 "score": other["score"],
                 "scoreContext": other["record"].get("scoreContext")}
                for other in item["workflowReplacementCandidates"]
            ],
        }
        if "workflowConfig" in data:
            result["configuredSelections"] = [
                binding for binding in data["workflowConfig"]["bindings"]
                if binding["photoId"] == record["photoId"]
            ]
        results.append(result)
    return sorted(results, key=lambda item: item["currentPath"])


def _audit(data, out):
    saved = data["recordedAudit"]
    display_core = collections.defaultdict(list)
    for item in data["auditRecords"]:
        if (item["record"].get("scoreContext") or {}).get("coreMember") is True:
            display_core[item["row"]["newPerson"]].append(item)
    parts = [
        '<h2 id="audit">Placement and reference audit</h2>',
        "<p>This is saved evaluator evidence plus a hash-bound snapshot of the existing Review report. "
        "No inference, routing-policy evaluation or automatic move was performed. Snapshot scores are not "
        "the initial frozen-audit scores; higher similarity alone does not pass admission/protection gates.</p>",
        "<p>This snapshot covers the general People Review, not the separate Artist domain. "
        "It is not a complete census of every identity domain.</p>",
        f'<p>Review evidence matched {data["snapshotMatched"]} of {data["physicalDestinations"]} '
        "distinct saved destinations by path and recorded native hash. "
        "Snapshot matching alone does not rehash native/image bytes.</p>",
        f'<p>{data["snapshotIdUnavailable"]} matched Review records omit a stable photo ID; those are paired '
        "by exact physical path and recorded hash only. Their saved protection/workflow flags are not "
        "a fresh completeness audit of workflow references.</p>",
        f'<p>Saved frozen passes: {saved.get("passCount", "unavailable")}; '
        f'checks: {len(saved.get("lowMemberChecks", []))}; '
        f'corrections: {len(saved.get("corrections", []))}; '
        f'protected recommendations: {len(saved.get("recommendations", []))}. '
        + html.escape(saved.get("scope", "Saved evaluator scope unavailable.")) + "</p>",
    ]
    if "redNativeBindings" in data:
        parts.append(
            f'<p>At report verification, {data["redNativeBindings"]} red, matched Review-core and '
            "workflow-candidate native files matched their recorded hashes and are bound as report inputs. "
            "Core counts alone do not prove complete reference membership or workflow eligibility.</p>"
        )
    if "workflowConfig" in data:
        info = data["workflowConfig"]
        parts.append(
            "<p>Workspace configuration selections were inspected from "
            + html.escape(info["path"])
            + ", not the actual workflow files or workspace consumers. Configured production root "
            + ("matches" if info["rootMatches"] else "does not match")
            + f' this receipt root; {info["unidentified"]} selection(s) have no identifiable photo ID. '
            "Unidentified selections could refer to a red photo. This is not authority to change either root.</p>"
        )
    if data["redScoreCutoff"] is None:
        parts.append(f'<p>Among matched Review records: red score band unavailable; '
                     f'{data["unscoredCount"]} unscored; {data.get("singlePhotoCount", 0)} {SINGLE_PHOTO_LABEL}. No red classification was inferred.</p>')
    else:
        parts.append(f'<p>Among matched Review records: {data["redScoreCount"]} red own-core score(s) '
                     f'(unrounded score below {data["redScoreCutoff"]}); '
                     f'{data["unscoredCount"]} unscored; {data.get("singlePhotoCount", 0)} {SINGLE_PHOTO_LABEL}. These are findings, not release proposals.</p>')
    for key in ("corrections", "recommendations"):
        parts.append(f"<h3>Recorded {key}</h3><ul>")
        for item in saved.get(key, []):
            parts.append("<li>" + html.escape(json.dumps(item, ensure_ascii=False)) + "</li>")
        parts.append("</ul>")
    if data["snapshotDiagnostics"]:
        parts.append("<details><summary>Unavailable/stale snapshot evidence</summary><ul>"
                     + "".join("<li>" + html.escape(value) + "</li>" for value in data["snapshotDiagnostics"]) + "</ul></details>")
    parts.extend([
        '<h3>Per-photo audit navigation</h3><input id="audit-filter" placeholder="Identity, photo ID, reason">',
        '<label><input id="flagged" type="checkbox" checked> findings only</label>',
        '<table id="audit-table"><tr><th>Photo / identity</th><th>Own score / context</th>'
        '<th>Rivals</th><th>Protection / workflow</th><th>Findings / saved explanation</th></tr>',
    ])
    for item in data["auditRecords"]:
        row, record = item["row"], item["record"]
        rivals = ", ".join(
            rebase_recap._person_link(value["folder"], data, out.parent) + ": "
            + rebase_recap._score_text(value.get("score")) for value in item["rivals"]
        ) or "not recorded"
        replacements = item["workflowReplacementCandidates"]
        replacement_text = ""
        release_evidence = ""
        if "red own-core similarity" in item["flags"]:
            release_evidence = (
                "<br>Receipt source: " + html.escape(row["source"])
                + "<br>Saved destination: " + html.escape(row["destination"])
                + "<br>Recorded native SHA-256: " + html.escape(row["preparedSHA256"])
                + "<br>This saved audit does not propose or apply a release destination."
            )
            snapshots = data["referenceSnapshots"]
            if not isinstance(snapshots, dict):
                raise ValueError("saved planning reference snapshots must be an object")
            reference_details = []
            for round_name, snapshot in sorted(snapshots.items()):
                if not isinstance(snapshot, dict) or not isinstance(snapshot.get("photoIds"), dict):
                    raise ValueError("saved planning reference snapshot must contain photoIds")
                if any(not isinstance(ids, list) for ids in snapshot["photoIds"].values()):
                    raise ValueError("saved planning reference photoIds must be arrays")
                photo_id = record.get("photoId")
                owners = [folder for folder, ids in snapshot["photoIds"].items() if photo_id in ids]
                membership = ", ".join(sorted(owners)) if owners else "not listed"
                if photo_id is None:
                    membership = "photo ID unavailable"
                reference_details.append(
                    f'Round {round_name} ({snapshot.get("referenceVersion", "version unavailable")}): {membership}'
                )
            release_evidence += (
                "<br>Saved planning reference membership (not the displayed Review core): "
                + html.escape("; ".join(reference_details) or "unavailable")
            )
            core = display_core[row["newPerson"]]
            core_size = (record.get("scoreContext") or {}).get("coreSize")
            expected = str(core_size) if type(core_size) is int and core_size >= 0 else "unavailable"
            core_entries = "".join(
                "<li>" + html.escape(member["row"]["destination"]) + " / "
                + html.escape(str(member["record"].get("photoId") or "photo ID unavailable"))
                + " / recorded SHA-256: " + html.escape(member["row"]["preparedSHA256"]) + "</li>"
                for member in sorted(core, key=lambda member: member["row"]["destination"])
            )
            release_evidence += (
                "<details><summary>Saved Review core: "
                + str(len(core)) + " matched of " + expected
                + " reported; counts do not prove completeness</summary>"
                + ("<p>Snapshot entries; current bytes are bound, but reference eligibility was not verified.</p>"
                   if "redNativeBindings" in data else
                   "<p>Snapshot entries only; current bytes and reference eligibility were not verified.</p>")
                + "<ul>" + core_entries + "</ul></details>"
            )
            if "workflowConfig" in data:
                configured = [
                    binding for binding in data["workflowConfig"]["bindings"]
                    if binding["photoId"] and binding["photoId"] == record.get("photoId")
                ]
                selections = "; ".join(
                    ("base" if binding["flow"] is None else "flow " + str(binding["flow"]))
                    + " / " + str(binding["hero"]) + " / " + str(binding["filename"])
                    for binding in configured
                ) or "none identified (unidentified selections may still match)"
                release_evidence += "<br>Current configured selections: " + html.escape(selections)
        current_selected = any(
            binding["photoId"] and binding["photoId"] == record.get("photoId")
            for binding in data.get("workflowConfig", {}).get("bindings", [])
        )
        if "red own-core similarity" in item["flags"] and (record.get("workflowSelected") or current_selected):
            examples = "; ".join(
                html.escape(candidate["row"]["destination"]) + " (" + str(candidate["score"]) + ")"
                for candidate in replacements[:3]
            ) or "none in matched snapshot"
            replacement_text = (
                f"<br>Higher non-red same-owner Gallery candidates: {len(replacements)}; "
                f"{examples}. Snapshot evidence only; workflow eligibility not verified."
            )
        parts.append(
            f'<tr id="photo-{_sha(row["destination"].encode("utf-8"))}" data-finding="{int(bool(item["flags"]))}"><td>'
            + rebase_recap._person_link(row["newPerson"], data, out.parent, bucket=row["newBucket"])
            + "<br>" + _photo_link(row, data, out.parent) + "<br>" + html.escape(row["photoId"] or row["destination"])
            + "</td><td>" + rebase_recap._score_text(item["score"])
            + (f'<br>Unrounded: {html.escape(str(item["score"]))}' if item["score"] is not None else "")
            + "<br>"
            + html.escape(str(record.get("comparison", "not recorded"))) + "</td><td>" + rivals
            + "</td><td>" + html.escape(
                f'Identity protected: {record.get("identityProtected")}; '
                f'photo protection: {record.get("photoProtectionInfo", "not recorded")}; '
                f'anchor: {record.get("identityAnchor")}; '
                f'workflow selected: {record.get("workflowSelected")}; '
                f'core: {(record.get("scoreContext") or {}).get("coreMember", "not recorded")}'
            ) + "</td><td>" + html.escape("; ".join(item["flags"]) or "no selected diagnostic flags")
            + "<br>" + html.escape(record.get("reason", "")) + release_evidence + replacement_text + "</td></tr>"
        )
    return "".join(parts) + "</table>"


def _photo_link(row, data, out_dir):
    review = pathlib.Path(data["libraryRoot"]) / "people_gallery_review.html"
    query = urllib.parse.urlencode({"person": row["newPerson"], "bucket": row["newBucket"].title()})
    href = rebase_recap._href(review, out_dir) + "?" + query
    return f'<a href="{html.escape(href, quote=True)}" target="_blank" rel="noopener noreferrer">Review identity</a>'


_PHASE_DETAILS = {
    "source-inventory-and-sha256": ("Inventory and bind source bytes.", ("sourceRowCount",)),
    "stable-id-normalization-and-version-selection": (
        "Classify stable IDs, versions, aliases and source holds.",
        ("canonicalInputCount", "exactAliasCount", "heldSourceCount")),
    "accepted-profile-preparation": (
        "Prepare selected natives or verify reused preparation.",
        ("preparationInputCount", "preparedReferenceCount", "preparedCandidateCount")),
    "source-bound-measurement-and-frozen-cores": (
        "Measure selected sources and freeze identity cores.", ("coreCount",)),
    "fresh-source-measurement": (
        "Measure initial classified sources and establish their centering population.", ()),
    "fresh-source-release-selection": (
        "Verify measurement provenance, assess initial Gallery own-core release (including the "
        "Sisters/Angels cast seed) and retire selected membership.",
        ("freshGalleryCount", "freshSelectedCount", "freshBlockedCount",
         "freshUnavailableCount", "freshNonVotingCount",
         "freshCastSeedIdentityCount", "freshCastSeedKeptCount", "freshCastSeedReleaseCount")),
    "fresh-post-release-frozen-cores": (
        "Freeze remaining cores and prepare candidates after source retirement.", ("coreCount",)),
    "bounded-two-round-admission": (
        "Route candidates through bounded admission.",
        ("candidateCount", "assignedCount", "heldCount",
         "freshCastSeedReturnedCount", "freshCastWorkflowReplacementCount")),
    "single-candidate-plan": (
        "Route candidates using the single candidate plan.", ("candidateCount", "assignedCount", "heldCount")),
    "bound-admission-and-retained-member-check": (
        "Bind proposed moves and audit retained members.", ()),
    "single-frozen-low-member-audit": (
        "Bind proposed moves and audit low members against frozen cores.", ()),
    "final-rival-family-viewer-publication": (
        "Validate and stage publication, compare families, publish viewers and save cache.", ()),
}


def _phase_sections(data):
    phases = data.get("phaseLog")
    if not isinstance(phases, list) or not phases:
        return ('<h2 id="steps">Ordered processing summary</h2>'
                '<p>Phase records and timings unavailable in this receipt.</p>')
    summary, details = [], []
    counts = data.get("phaseCounts", {})
    for number, phase in enumerate(phases, 1):
        if not isinstance(phase, dict):
            summary.append("<li>Invalid phase record; timing unavailable.</li>")
            details.append(f"<li>Step {number}: invalid phase record.</li>")
            continue
        name = str(phase.get("phase", "unknown"))
        status = str(phase.get("status", "unknown"))
        duration = phase.get("durationSeconds")
        if (status == "complete" and isinstance(duration, (int, float))
                and not isinstance(duration, bool) and math.isfinite(duration) and duration >= 0):
            timing = f"{duration:.3f} seconds measured"
        else:
            timing = "duration unavailable"
        title = html.escape(name)
        purpose, keys = _PHASE_DETAILS.get(name, ("Purpose not recorded.", ()))
        if name.startswith("settle-pass-"):
            purpose = ("Rebuild each identity from its planned members, rescore them leave-one-out, release "
                       "red/orange members and rematch them under the normal rules.")
        if name == "fresh-source-release-selection":
            values = [f"{key}: {counts.get(key) if counts.get(key) is not None else 'unavailable'}"
                      for key in keys]
        elif name.startswith("settle-pass-"):
            values = [f"{key}: {phase[key]}" for key in (
                "releasedCount", "movedCount", "remainingFlaggedCount", "newIdentityCount",
            ) if key in phase]
        else:
            values = [f"{key}: {counts[key]}" for key in keys if key in counts]
        if name in ("bound-admission-and-retained-member-check", "single-frozen-low-member-audit"):
            values.append(f'proposed moves: {data["phaseMoves"]}')
            audit = data.get("recordedAudit", {})
            if "passCount" in audit:
                values.append(f'audit passes: {audit["passCount"]}')
        if name == "final-rival-family-viewer-publication":
            label = "published moves" if status == "complete" and data["status"] == "applied" else "proposed moves"
            values.extend((f'{label}: {data["phaseMoves"]}', f'archive dispositions: {data["phaseArchives"]}',
                           f'junk dispositions: {data["phaseJunk"]}'))
            if data.get("phaseViewers") is not None:
                values.append(f'viewers recorded: {data["phaseViewers"]}')
        summary_counts = "; " + html.escape("; ".join(values)) if values else ""
        summary.append(
            f'<li><a href="#step-{number}">{title}</a> — {html.escape(status)}; '
            f'{timing}{summary_counts}.</li>'
        )
        scope = phase.get("timingScope")
        extra = f" Timing scope: {scope}." if isinstance(scope, str) and scope else ""
        if name == "accepted-profile-preparation" and data.get("preparationReusedFromPreview"):
            extra += " Historical preparation was reused; its duration is not measured by this run."
        if (name == "final-rival-family-viewer-publication"
                and status == "apply-only" and data["status"] == "applied"):
            extra += " The applied receipt records publication; this phase did not record its completion timing."
        details.append(
            f'<li id="step-{number}"><b>{title}</b> — {html.escape(purpose)} '
            f'Status: {html.escape(status)}; {timing}.{html.escape(extra)} '
            f'{html.escape("; ".join(values) if values else "No step counts recorded.")}</li>'
        )
    return ('<h2 id="steps">Ordered processing summary</h2><ol>' + "".join(summary)
            + '</ol><h2>Processing step details</h2><ol>' + "".join(details) + "</ol>")


def render(data, out, *, audit=False, others=()):
    recap_name = data.get("recapPageName", data["runId"] + ".html")
    audit_name = data.get("auditPageName", data["runId"] + "-audit.html")
    section_prefix = recap_name if audit else ""
    body = [
        f'<h1>SIMPLE {"audit" if audit else "movement recap"}: {html.escape(data["runId"])}</h1>',
        f'<p>Status: <b>{html.escape(data["status"])}</b>; profile: {html.escape(str(data["profile"]))}. '
        "Saved run evidence, not a new grouping run. Current-file links are not fresh byte certification.</p>",
        '<nav><a href="index.html">All saved recaps</a> · '
        f'<a href="{html.escape(recap_name)}">Movement recap</a> · '
        f'<a href="{html.escape(audit_name)}">Placement audit</a> · '
        f'<a href="{html.escape(section_prefix)}#steps">Processing steps</a> · '
        f'<a href="{html.escape(section_prefix)}#flows">Where photos went</a> · '
        f'<a href="{html.escape(section_prefix)}#continuity">Identity continuity</a> · '
        f'<a href="{html.escape(section_prefix)}#collisions">ID collisions</a> · '
        '<a href="#audit">Audit evidence</a> · '
        f'<a href="{html.escape(section_prefix)}#all">Every source row</a></nav>',
        f'<p><b>{data["physicalSources"]} physical source rows → {data["physicalDestinations"]} distinct '
        f'destinations + {data["coalescedAliases"]} explicitly coalesced exact-alias targets '
        f'+ {data["supersededVersions"]} superseded native versions.</b> '
        f'Non-voting archive destinations: {data["duplicateArchives"]}. '
        "Continuity tables count source rows, not extra current photos or votes.</p>",
    ]
    if audit:
        body.append(_audit(data, out))
    else:
        body += [
            _phase_sections(data),
            rebase_recap._flow_section(data, out.parent),
            rebase_recap._continuity_section(data, out.parent),
            _collision_section(data, out.parent),
            _content_archive_section(data, out.parent),
            _retirement_section(data, out.parent),
            _cast_seed_section(data, out.parent),
            _settle_section(data, out.parent),
            _face_quality_section(data),
            _group_relationships(data, out.parent),
            "<section>" + _audit_summary(data) + "</section>",
            rebase_recap._comparison_section(data, list(others), out.parent) if others else "",
            rebase_recap._all_rows(data, out.parent),
        ]
    script = """function filters(){const q=(document.getElementById('filter')||document.getElementById('audit-filter')).value.toLowerCase();
const c=document.getElementById('changed'),f=document.getElementById('flagged');
for(const r of document.querySelectorAll('tr[data-kind],tr[data-finding]')){
r.hidden=!!((c&&c.checked&&r.dataset.kind==='stayed')||(f&&f.checked&&r.dataset.finding==='0')||(q&&!r.textContent.toLowerCase().includes(q))) }}
for(const e of document.querySelectorAll('input'))e.addEventListener('input',filters);filters();
function reveal(){const target=document.getElementById(location.hash.slice(1));if(!target)return;
const f=document.getElementById('flagged');if(target.matches('tr[data-finding]')&&f){f.checked=false;filters()}
target.scrollIntoView({block:'start'})}window.addEventListener('hashchange',reveal);reveal();"""
    page = ("<!doctype html><html><head><meta charset=utf-8><title>SIMPLE run recap and audit</title>"
            f"<style>{gallery_chrome.CSS}{rebase_recap.STYLE}</style></head><body>"
            + gallery_chrome.masthead(
                tagline="SIMPLE saved-run evidence",
                prefix=gallery_chrome.reports_prefix(out.parent, pathlib.Path(data["libraryRoot"]).parent),
            )
            + '<main class="recap-content"><section>' + "</section><section>".join(body)
            + f"</section></main><script>{script}</script></body></html>")
    return re.sub(r'(<a href="#[^"]+") target="_blank" rel="noopener noreferrer"', r"\1", page)


def _audit_summary(data):
    return ('<h2 id="audit">Audit evidence</h2><p>'
            f'{len(data["auditRecords"])} matched snapshot photo records; '
            f'{sum(bool(item["flags"]) for item in data["auditRecords"])} diagnostic finding rows. '
            f'<a href="{html.escape(data.get("auditPageName", data["runId"] + "-audit.html"))}">Open placement/reference audit</a>. '
            "Findings are not approved moves; missing scores/protection evidence are not inferred.</p>")


def _collision_section(data, out_dir):
    root = pathlib.Path(data["workingRoot"])
    parts = ['<h2 id="collisions">Photo ID collisions</h2>',
             '<p>Resolved before any core or matching vote. Modified time is the saved filesystem value in '
             'nanoseconds since Unix epoch. Archives are not active memberships.</p>',
             '<table><tr><th>Photo ID</th><th>Source / SHA-256 / modified time</th>'
             '<th>Disposition / archive</th></tr>']
    if data["unresolvedDuplicateIds"]:
        parts.insert(2, f'<p><strong>{len(data["unresolvedDuplicateIds"])} unresolved IDs block apply.</strong></p>')
    for pid, group in sorted(data["collisionGroups"].items()):
        for source, archive in group:
            outcome = html.escape(
                source.get("reason", "Held") if source.get("sourceStatus") == "held"
                else source.get("collisionRule", source.get("reason", "Kept")),
            )
            if archive:
                relative = archive["destination"]
                outcome += "<br>Keeper: " + html.escape(archive["selectedSource"]) + "<br>"
                if data["status"] == "applied":
                    href = rebase_recap._href(_under(root, root / _relative(relative)), out_dir)
                    outcome += f'<a href="{html.escape(href, quote=True)}">{html.escape(relative)}</a>'
                else:
                    outcome += "Proposed: " + html.escape(relative)
            parts.append(
                f'<tr><td>{html.escape(pid)}</td><td>{html.escape(source["source"])}<br>'
                f'{source["sourceHash"]}<br>{source.get("collisionModifiedNs", "Not used")}</td>'
                f'<td>{outcome}</td></tr>'
            )
    return "".join(parts + ["</table>"])


def _content_archive_section(data, out_dir):
    if not data["contentArchives"]:
        return ""
    root = pathlib.Path(data["workingRoot"])
    final = {row["source"]: row for row in data["rows"]}
    parts = ['<h2 id="content-archives">Duplicates: identical bytes under different photo IDs</h2>',
             f'<p>{len(data["contentArchives"])} byte-identical copies were archived recoverably, including '
             'released copies; the IDs are not merged. One keeper stays wherever matching placed it.</p>',
             '<table><tr><th>Archived copy / SHA-256</th><th>Former owner</th><th>Keeper at inventory</th>'
             '<th>Keeper final location</th><th>Exact match basis</th></tr>']
    for row in sorted(data["contentArchives"], key=lambda item: item["source"]):
        destination = html.escape(row["destination"])
        keeper = final.get(row["selectedSource"], {})
        keeper_final = keeper.get("destination") or row["selectedSource"]
        keeper_text = html.escape(keeper_final)
        if data["status"] == "applied":
            href = rebase_recap._href(_under(root, root / _relative(row["destination"])), out_dir)
            destination = f'<a href="{html.escape(href, quote=True)}">{destination}</a>'
            if not keeper.get("duplicateArchive") and not keeper.get("junkDisposition"):
                keeper_href = rebase_recap._href(_under(root, root / _relative(keeper_final)), out_dir)
                keeper_text = f'<a href="{html.escape(keeper_href, quote=True)}">{keeper_text}</a>'
        else:
            keeper_text = "Proposed: " + keeper_text
        owner = rebase_recap.person_and_bucket(row["source"])[0]
        proof = row.get("retainedOriginalProof")
        basis = f'Verified retained original<br>{html.escape(proof["path"])}' if proof else "Current keeper bytes"
        parts.append(
            f'<tr><td>{html.escape(row["photoId"])}<br>{html.escape(row["source"])}<br>'
            f'{destination}<br>{row["sha256"]}</td><td>{html.escape(str(owner))}</td>'
            f'<td>{html.escape(row["selectedPhotoId"])}<br>'
            f'{html.escape(row["selectedSource"])}</td><td>{keeper_text}</td><td>{basis}</td></tr>'
        )
    return "".join(parts + ["</table>"])


def _retired_identity_folders(receipt, plan):
    """Saved item (g) retirements; an applied receipt must agree with its plan."""
    planned = (plan.get("emptiedIdentityRetirement") or {}).get("folders")
    if receipt["status"] == "applied" and "retiredIdentityFolders" in receipt:
        if receipt["retiredIdentityFolders"] != (planned or []):
            raise ValueError("receipt and plan disagree on retired identity folders")
    if planned is None:
        return None
    for row in planned:
        _relative(row["source"])
        _relative(row["destination"])
        for photo in row["photos"]:
            _relative(photo["source"])
            _relative(photo["destination"])
    return planned


def _retirement_section(data, out_dir):
    """Item (g): emptied identity folders retired inside this run's transaction."""
    folders = data.get("retiredIdentityFolders")
    if folders is None:
        return ""
    applied = data["status"] == "applied"
    root = pathlib.Path(data["workingRoot"])
    parts = ['<h2 id="retired-identities">Emptied identities retired</h2>',
             f'<p>{len(folders)} identity folder(s) kept no Gallery or Review original after this run, so '
             + ("they were moved intact (with any derivative folders) to retired storage inside the same "
                "recoverable publication transaction; recovery restores them. Nothing was deleted."
                if applied else
                "apply will move them intact to retired storage inside the same recoverable transaction.")
             + " Sisters/Angels folders are never retired automatically.</p>"]
    if not folders:
        return "".join(parts)
    parts.append('<table><tr><th>Identity</th><th>Retired location</th><th>Photos that left it</th></tr>')
    for row in folders:
        destination = html.escape(row["destination"])
        if applied:
            href = rebase_recap._href(_under(root, root / _relative(row["destination"])), out_dir)
            destination = f'<a href="{html.escape(href, quote=True)}">{destination}</a>'
        else:
            destination = "Proposed: " + destination
        photos = "<br>".join(
            f'{html.escape(photo["source"])} → {html.escape(photo["destination"])}' for photo in row["photos"]
        )
        parts.append(f'<tr><td>{html.escape(row["source"])}</td><td>{destination}</td><td>{photos}</td></tr>')
    return "".join(parts + ["</table>"])


_SEED_OUTCOMES = {
    "returned-gallery": "Returned to same Gallery",
    "own-review": "Held in this identity's Review",
    "elsewhere": "Placed elsewhere",
    "archived-duplicate": "Archived identical copy",
}


def _cast_seed_section(data, out_dir):
    """Per cast identity: the kept seed and where each released member landed."""
    seed = data.get("freshCastSeed")
    if not isinstance(seed, dict):
        return ""
    rows_by_source = {row["source"]: row for row in data["rows"]}
    parts = [
        '<h2 id="cast-seed">Cast seed release</h2>',
        f'<p>Fresh Sandbox rebase, Sisters/Angels only. Each identity kept its top {seed.get("topCount")} '
        "photos by own score, no matter what their score is (including red or orange), plus every member at "
        f'or above {html.escape(str(seed.get("releaseBelow")))} as seed references. All other scored members '
        "were released before cores formed and rescored against the seed through the normal cast entry rules. "
        "Unscored members cannot be ranked and are released as before. "
        "Before is the initial own score; after is the recorded score against the seeded identity, "
        "where the decision recorded one.</p>",
    ]
    for identity in seed.get("identities", []):
        owner = identity["identity"]
        exempt = identity.get("seedBandExemptCount")
        parts.append(
            f'<h3 id="{html.escape(rebase_recap._anchor("cast-seed", owner), quote=True)}">'
            + rebase_recap._person_link(owner, data, out_dir, bucket="gallery") + "</h3>"
            f'<p>Members: {identity["memberCount"]}; seed size: {identity["seedSize"]}'
            + ("" if exempt is None else f" ({exempt} kept despite a red/orange band)")
            + f'; released: {identity["releasedCount"]} ({identity["seedReleaseCount"]} by the seed rule); '
            f'returned to Gallery: {identity["returnedCount"]}.</p>'
        )
        if not identity["released"]:
            parts.append("<p class=muted>None released.</p>")
            continue
        parts.append('<table><tr><th>Photo</th><th>Release basis</th><th>Before (own)</th>'
                     '<th>Outcome</th><th>After (vs seed)</th><th>Best recorded match</th></tr>')
        for item in identity["released"]:
            row = rows_by_source.get(item["currentPath"])
            photo = (rebase_recap._thumb(row, data, out_dir) + "<br>"
                     + rebase_recap._destination_links(row, data, out_dir)) if row else (
                '<span class=muted>Source row unavailable.</span>')
            outcome = html.escape(_SEED_OUTCOMES.get(item["outcome"], item["outcome"]))
            if item["outcome"] != "returned-gallery":
                outcome += "<br>" + rebase_recap._person_link(
                    rebase_recap.person_and_bucket(item["finalPath"])[0], data, out_dir,
                ) + "<br>" + html.escape(item["finalPath"])
            if item.get("workflowSelected"):
                outcome += "<br><b>Workflow-selected</b>"
            best = (rebase_recap._person_link(item["afterBestMatch"], data, out_dir) + ": "
                    + rebase_recap._score_text(item.get("afterBestScore"))) if item.get("afterBestMatch") else (
                '<span class=muted>not recorded</span>')
            parts.append(
                f'<tr><td>{photo}<br>{html.escape(item["photoId"])}<br>{html.escape(item["currentPath"])}</td>'
                f'<td>{html.escape(", ".join(item["selectionReasons"]))}'
                f'{"" if item.get("seedRank") is None else "<br>rank " + str(item["seedRank"])}</td>'
                f'<td>{rebase_recap._score_text(item["beforeScore"])}</td><td>{outcome}</td>'
                f'<td>{rebase_recap._score_text(item.get("afterScore"))}</td><td>{best}</td></tr>'
            )
        parts.append("</table>")
    proposals = seed.get("workflowReplacementProposals", [])
    parts.append('<h3 id="cast-seed-workflow">Workflow replacement proposals</h3>'
                 "<p>Released workflow-selected photos that did not return to their Gallery. Proposals only; "
                 "the workflow configuration was not changed.</p>")
    if not proposals:
        parts.append("<p class=muted>None.</p>")
    else:
        parts.append('<table><tr><th>Identity</th><th>Workflow photo / outcome</th>'
                     '<th>Proposed replacement</th></tr>')
        for proposal in proposals:
            replacement = proposal.get("replacement")
            if replacement:
                row = rows_by_source.get(replacement["currentPath"])
                text = ((rebase_recap._thumb(row, data, out_dir) + "<br>") if row else "") + (
                    html.escape(replacement["photoId"]) + "<br>" + html.escape(replacement["finalPath"])
                    + "<br>own score " + rebase_recap._score_text(replacement["ownScore"]))
            else:
                text = '<span class=muted>No remaining scored Gallery photo available.</span>'
            source = rows_by_source.get(proposal["currentPath"])
            parts.append(
                "<tr><td>" + rebase_recap._person_link(proposal["identity"], data, out_dir, bucket="gallery")
                + "</td><td>" + ((rebase_recap._thumb(source, data, out_dir) + "<br>") if source else "")
                + html.escape(proposal["photoId"]) + "<br>"
                + html.escape(_SEED_OUTCOMES.get(proposal["outcome"], proposal["outcome"]))
                + ": " + html.escape(proposal["finalPath"]) + "</td><td>" + text + "</td></tr>"
            )
        parts.append("</table>")
    return "".join(parts)


def _settle_section(data, out_dir):
    """Settle passes: per-pass counts and timings, released photos and the did-not-settle list."""
    settle = data.get("settle")
    if not isinstance(settle, dict):
        return ""
    rows_by_id = {}
    for row in data["rows"]:
        rows_by_id.setdefault(row.get("photoId"), row)
    timings = {
        phase.get("settlePass"): phase.get("durationSeconds")
        for phase in data.get("phaseLog", []) if isinstance(phase, dict) and phase.get("settlePass")
    }

    def photo(photo_id):
        row = rows_by_id.get(photo_id)
        thumb = (rebase_recap._thumb(row, data, out_dir) + "<br>") if row else ""
        return thumb + html.escape(photo_id)

    def timing(pass_index):
        value = timings.get(pass_index)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0:
            return f"{value:.3f} s"
        return "unavailable"

    passes = settle.get("passes", [])
    parts = [
        '<h2 id="settle">Settle passes</h2>',
        f'<p>Before publication, each identity was rebuilt from its final planned members (existing and '
        f'admitted; match-only dominant-face photos, non-voters and Review placements never vote; one vote '
        f'per content), every planned Gallery member was rescored leave-one-out, and red/orange members '
        f'were released and rematched under the normal rules, up to {html.escape(str(settle.get("maximumPasses")))} '
        f'passes. Cast seeds, protected or explicit placements and existing members this run did not place '
        f'are never released. {len(passes)} pass(es) ran; '
        + ("the last pass changed nothing." if settle.get("converged") else
           "the pass limit was reached while photos were still moving.") + "</p>",
        '<table><tr><th>Pass</th><th>Time</th><th>Flagged</th><th>Released</th><th>Moved</th>'
        '<th>Still flagged after</th><th>New identities</th></tr>',
    ]
    for item in passes:
        parts.append(
            f'<tr><td>{item["pass"]}</td><td>{timing(item["pass"])}</td><td>{item["flaggedCount"]}</td>'
            f'<td>{item["releasedCount"]}</td><td>{item["movedCount"]}</td>'
            f'<td>{item["remainingFlaggedCount"]}</td><td>{len(item.get("newIdentities", []))}</td></tr>'
        )
    parts.append("</table>")
    for item in passes:
        if not item.get("released") and not item.get("singlePhotoReductions"):
            continue
        parts.append(f'<h3 id="settle-pass-{item["pass"]}">Pass {item["pass"]}</h3>')
        if item.get("released"):
            parts.append('<table><tr><th>Photo</th><th>Released from</th><th>Score</th><th>Outcome</th></tr>')
            for released in item["released"]:
                outcome = html.escape(released["outcome"])
                if not released.get("moved"):
                    outcome += "<br><span class=muted>returned to the same place</span>"
                parts.append(
                    f'<tr><td>{photo(released["photoId"])}</td>'
                    f'<td>{rebase_recap._person_link(released["identity"], data, out_dir, bucket="gallery")}</td>'
                    f'<td>{rebase_recap._score_text(released.get("score"))} '
                    f'{html.escape(str(released.get("band") or ""))}</td><td>{outcome}</td></tr>'
                )
            parts.append("</table>")
        for reduction in item.get("singlePhotoReductions", []):
            gate = reduction.get("singlePhotoGate") or {}
            parts.append(
                f'<p>Reduced to one photo: {html.escape(reduction["identity"])} '
                f'({html.escape(reduction["photoId"])}) → {html.escape(reduction["outcome"])}; best rival '
                f'{html.escape(str(gate.get("bestRival")))} {rebase_recap._score_text(gate.get("bestRivalScore"))}.</p>'
            )
    unsettled = settle.get("didNotSettle", [])
    parts.append(f'<h3 id="did-not-settle">Did not settle ({len(unsettled)})</h3>')
    if not unsettled:
        parts.append("<p class=muted>None: no planned Gallery member is still red or orange.</p>")
        return "".join(parts)
    parts.append("<p>Planned Gallery members still red or orange after the last pass. Reported only; "
                 "they are not looped further.</p>"
                 '<table><tr><th>Photo</th><th>Identity</th><th>Score</th><th>Reason</th></tr>')
    for row in unsettled:
        released_in = row.get("releasedInPasses") or []
        reason = html.escape(row["reason"]) + (
            f'<br><span class=muted>released in pass {", ".join(map(str, released_in))}</span>' if released_in else "")
        parts.append(
            f'<tr><td>{photo(row["photoId"])}</td>'
            f'<td>{rebase_recap._person_link(row["identity"], data, out_dir, bucket="gallery")}</td>'
            f'<td>{rebase_recap._score_text(row.get("score"))} {html.escape(str(row.get("band") or ""))}</td>'
            f'<td>{reason}</td></tr>'
        )
    return "".join(parts + ["</table>"])


def _face_quality_section(data):
    """Dominant-face (match-only) evidence and the remaining Various reasons."""
    quality_rows = [row for row in data["rows"] if row.get("faceQuality")]
    various = collections.Counter(
        row.get("decisionReason") or row.get("reason") or "existing owner retained"
        for row in data["rows"]
        if row.get("newPerson") == "Various"
        and not (row.get("duplicateArchive") or row.get("junkDisposition") or row.get("supersededVersion"))
    )
    if not quality_rows and not various:
        return ""
    parts = ['<h2 id="face-quality">Face quality: dominant-face matches and holds</h2>',
             '<p>Dominant-face photos (other faces below the configured share of the main face) may be '
             'matched into a Gallery or Review but never vote as identity references. Near-equal second boxes '
             'are re-detected: overlapping boxes count as one face; separate ones stay held.</p>']
    if quality_rows:
        parts.append('<table><tr><th>Photo</th><th>Quality class</th><th>Evidence</th><th>Outcome</th></tr>')
        for row in sorted(quality_rows, key=lambda item: item["source"]):
            quality = row["faceQuality"]
            evidence = (f'faces {quality.get("faces")}; second/main area {quality.get("secondaryRatio")}; '
                        f'{quality.get("px")} px (min {quality.get("minFace")})')
            if "secondBoxIoU" in quality:
                evidence += (f'; re-detected IoU {quality["secondBoxIoU"]}, containment '
                             f'{quality["secondBoxContainment"]}')
            parts.append(
                f'<tr><td>{html.escape(str(row["photoId"]))}<br>{html.escape(row["source"])}</td>'
                f'<td>{html.escape(str(quality.get("class")))}'
                f'{" · match-only, no reference vote" if quality.get("matchEligible") else " · held"}</td>'
                f'<td>{html.escape(evidence)}<br>{html.escape(str(quality.get("reason", "")))}</td>'
                f'<td>{html.escape(str(row["newPerson"]))} / {html.escape(str(row["newBucket"]))}</td></tr>'
            )
        parts.append("</table>")
    if various:
        parts.append(f'<h3>Remaining Various reasons</h3><p>{sum(various.values())} source row(s) end in Various.</p>'
                     '<table><tr><th>Reason</th><th>Rows</th></tr>')
        for reason, count in sorted(various.items(), key=lambda item: (-item[1], item[0])):
            parts.append(f'<tr><td>{html.escape(reason)}</td><td>{count}</td></tr>')
        parts.append("</table>")
    return "".join(parts)


def _group_relationships(data, out_dir):
    parts = ['<h2 id="groups">Saved final group relationships</h2><p>'
             'These are group/core similarities, not individual-photo admission decisions. '
             'Only recorded qualified groups are present; no missing relationship is inferred.</p>'
             '<table><tr><th>Identity</th><th>Top recorded rival groups</th></tr>']
    for folder, rivals in sorted(data["groupRivals"].items()):
        parts.append("<tr><td>" + rebase_recap._person_link(folder, data, out_dir) + "</td><td>"
                     + ", ".join(rebase_recap._person_link(item["folder"], data, out_dir)
                                 + ": " + rebase_recap._score_text(item.get("score"))
                                 for item in rivals[:3]) + "</td></tr>")
    return "".join(parts) + "</table>"


def publish(receipt, *, out=None, compare=(), check=False, apply=False, bind_red_natives=False,
            inspect_workflow_selections=False, workflow_configuration_path=None):
    started = time.perf_counter()
    if workflow_configuration_path is not None and not inspect_workflow_selections:
        raise ValueError("a workflow configuration path requires workflow selection inspection")
    data = collect(receipt)
    if inspect_workflow_selections:
        _attach_workflow_selection_bindings(data, configuration_path=workflow_configuration_path)
    if bind_red_natives:
        _bind_red_native_evidence(data)
    root = pathlib.Path(data["workingRoot"])
    name = data["runId"]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", name):
        raise ValueError("unsafe run identifier")
    folder = pathlib.Path(data["libraryRoot"]) / "rebase-recap"
    if data["status"] == "applied":
        folder /= "applied"
    out = _under(root, pathlib.Path(out).absolute() if out else folder / (name + ".html"))
    audit = out.with_name(out.stem + "-audit.html")
    data.update(recapPageName=out.name, auditPageName=audit.name)
    others = [collect(path) for path in compare]
    for other in others:
        if other["sourceManifestSHA256"] != data["sourceManifestSHA256"]:
            raise ValueError("comparison requires the same frozen source paths/hashes")
        data["inputs"].update(other["inputs"])
        data["inputBytes"] += other["inputBytes"]
    outputs = {out: render(data, out, others=others), audit: render(data, audit, audit=True)}
    producers = [pathlib.Path(__file__), pathlib.Path(rebase_recap.__file__),
                 pathlib.Path(gallery_chrome.__file__), pathlib.Path(policy.__file__)]
    if inspect_workflow_selections:
        from tools.art.likeness_library import actions

        for module in (actions, actions.metadata, actions.cw):
            source = module.__file__
            if source is None:
                raise ValueError(f"workflow audit producer has no source path: {module.__name__}")
            producers.append(pathlib.Path(source))
    manifest = {
        "kind": "normal-recap-report", "runId": name, "status": data["status"],
        "receipt": str(pathlib.Path(receipt).absolute()), "inputs": data["inputs"],
        "producer": {str(path): _sha(path.read_bytes()) for path in producers},
        "outputs": {str(path): _sha(text.encode("utf-8")) for path, text in outputs.items()},
        "sourceRows": data["physicalSources"], "distinctDestinations": data["physicalDestinations"],
        "coalescedAliasTargets": data["coalescedAliases"], "snapshotMatched": data["snapshotMatched"],
        "supersededNativeVersions": data["supersededVersions"],
        "snapshotIdUnavailable": data["snapshotIdUnavailable"],
        "snapshotDiagnostics": data["snapshotDiagnostics"],
    }
    if bind_red_natives:
        manifest["redNativeBindings"] = data["redNativeBindings"]
        manifest["redCandidates"] = _red_candidate_evidence(data)
    if inspect_workflow_selections:
        manifest["workflowSelectionScope"] = {
            "productionRootMatches": data["workflowConfig"]["rootMatches"],
            "unidentifiedSelections": data["workflowConfig"]["unidentified"],
            "workspaceFilesInspected": False,
        }
    state = out.with_suffix(".report.json")
    for path in (*outputs, state, out.parent / "index.html"):
        _under(root, path)
        _under(root, path.with_suffix(".tmp"))
    if check:
        if not state.is_file() or json.loads(state.read_text(encoding="utf-8")) != manifest:
            raise ValueError("recap/audit bindings are missing or stale; regenerate reports only")
        for path, expected in manifest["outputs"].items():
            path = _under(root, pathlib.Path(path))
            if not path.is_file() or _sha(path.read_bytes()) != expected:
                raise ValueError(f"recap/audit output missing or changed: {path}")
        index = out.parent / "index.html"
        index_text = index.read_text(encoding="utf-8") if index.is_file() else ""
        if any(rebase_recap._safe_link(path, path.stem, out.parent) not in index_text for path in outputs):
            raise ValueError("saved recap index is missing this run's recap/audit navigation")
    elif apply:
        for path, expected in data["inputs"].items():
            if _sha(pathlib.Path(path).read_bytes()) != expected:
                raise ValueError(f"saved report input changed while rendering: {path}")
        for path, text in outputs.items():
            rebase_recap._write(path, text, newline="\n")
        rebase_recap._write(state, json.dumps(manifest, indent=2) + "\n", newline="\n")
        links = sorted(path for path in out.parent.glob("*.html") if path.name != "index.html")
        rebase_recap._write(out.parent / "index.html",
                            "<!doctype html><html><head><title>Saved rebase recaps</title></head><body>"
                            "<h1>Saved rebase recaps and audits</h1><ul>" + "".join(
                                "<li>" + rebase_recap._safe_link(path, path.stem, out.parent) + "</li>"
                                for path in links) + "</ul></body></html>", newline="\n")
    print(f'SIMPLE report {"checked" if check else "written" if apply else "preview"}: '
          f'{data["physicalSources"]} source rows; {data["physicalDestinations"]} destinations; '
          f'{data["coalescedAliases"]} coalesced aliases; {data["snapshotMatched"]} snapshot matches; '
          f'{data["supersededVersions"]} superseded native versions; '
          f'{len(data["snapshotDiagnostics"])} unavailable/stale diagnostics; '
          f'{data["inputBytes"]} report-input bytes; {time.perf_counter()-started:.3f}s')
    print(out)
    print(audit)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", help="saved normal-rebase applied/preview JSON; never runs matching")
    parser.add_argument("--out", help="recap HTML inside the saved receipt's library root")
    parser.add_argument("--compare", action="append", default=[], help="same-source SIMPLE receipt to compare")
    parser.add_argument("--bind-red-natives", action="store_true",
                        help="rehash and bind red photos, matched Review cores and workflow candidates")
    parser.add_argument("--inspect-workflow-selections", action="store_true",
                        help="report current base/flow configuration selections; does not inspect workflow files")
    parser.add_argument("--workflow-configuration",
                        help="inspect and bind this configuration instead of the default; requires selection inspection")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="preview counts only (default)")
    mode.add_argument("--apply", action="store_true", help="write only recap/audit reports and their bindings")
    mode.add_argument("--check", action="store_true", help="read-only exact report/input/producer check")
    args = parser.parse_args(argv)
    try:
        publish(args.receipt, out=args.out, compare=args.compare, check=args.check, apply=args.apply,
                bind_red_natives=args.bind_red_natives,
                inspect_workflow_selections=args.inspect_workflow_selections,
                workflow_configuration_path=args.workflow_configuration)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"SIMPLE recap stopped safely: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
