"""Read-only, evidence-bound diagnostic for the saved red-member snapshot."""
import argparse
import hashlib
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "art"))
import likeness  # noqa: E402
from likeness_library import actions, normal_admission, policy  # noqa: E402

MAX_CONSUMER_BYTES = 512 * 1024 * 1024


def workspace_consumer_scopes(cfg):
    """Include unconfigured local ComfyUI installs as unverified consumer scopes."""
    scopes = {f"workspace:{name}": likeness.cw.install_dir(cfg, name) for name in cfg["workspaces"]}
    install_root = pathlib.Path(likeness.cw.installs_root(cfg)).absolute()
    if likeness.cw.is_reparse_point(install_root):
        raise ValueError(f"consumer inventory refuses linked install root: {install_root}")
    if not install_root.exists():
        return scopes
    if not install_root.is_dir() or install_root.resolve() != install_root:
        raise ValueError(f"consumer inventory refuses invalid or linked install root: {install_root}")
    entries = sorted(install_root.iterdir(), key=lambda path: path.name.casefold())
    if len(entries) > 10000:
        raise ValueError("consumer inventory exceeds 10,000 install-root entries")
    configured = {name.casefold() for name in cfg["workspaces"]}
    for entry in entries:
        if entry.is_symlink() or likeness.cw.is_reparse_point(entry):
            raise ValueError(f"consumer inventory refuses linked installation: {entry}")
        if entry.name.casefold() in configured or not entry.is_dir():
            continue
        comfy = entry / "ComfyUI"
        if not comfy.exists():
            continue
        if not comfy.is_dir() or comfy.is_symlink() or likeness.cw.is_reparse_point(comfy):
            raise ValueError(f"consumer inventory refuses invalid or linked ComfyUI directory: {comfy}")
        scopes[f"unconfigured-workspace:{entry.name}"] = likeness.cw.install_dir(cfg, entry.name)
    return scopes


def inspect_consumers(scopes, photo_ids):
    """Scan all reachable JSON consumers; missing roots remain explicit coverage gaps."""
    if any(not isinstance(photo_id, str) or ":" not in photo_id for photo_id in photo_ids):
        raise ValueError("consumer inventory requires identifiable red photo IDs")
    tokens = [photo_id.split(":", 1)[1] for photo_id in photo_ids]
    if any(not token for token in tokens):
        raise ValueError("consumer inventory requires identifiable red photo IDs")
    total_bytes = 0
    files = {}
    matches, unavailable = [], []

    def fail(error):
        raise error

    def enumerate_json(root):
        paths = []
        for directory, subdirs, names in os.walk(root, onerror=fail, followlinks=False):
            folder = pathlib.Path(directory)
            subdirs[:] = sorted(name for name in subdirs if name.casefold() != "_archive")
            for name in subdirs:
                child = folder / name
                if child.is_symlink() or likeness.cw.is_reparse_point(child):
                    raise ValueError(f"consumer inventory refuses linked directory: {child}")
            for name in sorted(names):
                if name.casefold().endswith(".json"):
                    child = folder / name
                    if child.is_symlink() or likeness.cw.is_reparse_point(child):
                        raise ValueError(f"consumer inventory refuses linked file: {child}")
                    paths.append(child)
        return paths

    inventories = {}
    for scope, raw in scopes.items():
        root = pathlib.Path(raw).absolute()
        if not root.is_dir():
            unavailable.append({"scope": scope, "path": str(root)})
            continue
        if root.resolve() != root or likeness.cw.is_reparse_point(root):
            raise ValueError(f"consumer inventory refuses linked root: {root}")
        paths = enumerate_json(root)
        inventories[scope] = (root, paths)
        for path in paths:
            if path not in files:
                if len(files) >= 10000:
                    raise ValueError("consumer inventory exceeds 10,000 JSON files")
                size = path.stat().st_size
                if size > MAX_CONSUMER_BYTES - total_bytes:
                    raise ValueError("consumer inventory exceeds 512 MiB")
                with path.open("rb") as stream:
                    payload = stream.read(size + 1)
                if len(payload) != size:
                    raise ValueError(f"consumer workflow changed during scan: {path}")
                total_bytes += len(payload)
                document = json.loads(payload.decode("utf-8-sig"))
                files[path] = (hashlib.sha256(payload).hexdigest(),
                               actions.workflow_photo_references({"document": document}, tokens) if tokens else [])
            for match in files[path][1]:
                matches.append({"scope": scope, "path": str(path), **match})
    for scope, (root, paths) in inventories.items():
        if enumerate_json(root) != paths:
            raise ValueError(f"consumer inventory changed during scan: {scope}")
    for path, (digest, _) in files.items():
        if actions.metadata.content_sha256(path) != digest:
            raise ValueError(f"consumer workflow changed during scan: {path}")
    return {
        "files": len(files), "bytes": total_bytes, "matches": matches, "unavailable": unavailable,
        "fileHashes": {str(path): digest for path, (digest, _) in files.items()},
        "consumerCoverageVerified": False,
    }


def plan_consumer_retargets(inventory, proposals, configuration_path):
    """Propose exact JSON edits for inventoried workflows without writing them."""
    config = pathlib.Path(configuration_path).absolute()
    targets = {}
    proposed_ids = set()
    for proposal in proposals:
        if proposal["state"] != "proposed":
            continue
        if proposal["photoId"] in proposed_ids:
            raise ValueError("consumer retarget proposals contain duplicate photo IDs")
        proposed_ids.add(proposal["photoId"])
        token = proposal["photoId"].split(":", 1)[1].casefold()
        for match in inventory["matches"]:
            if token not in match["value"].casefold():
                continue
            path = pathlib.Path(match["path"]).absolute()
            targets.setdefault(path, {})[proposal["photoId"]] = proposal
    plans, blocked = [], []
    if proposed_ids and set(targets.get(config, {})) != proposed_ids:
        blocked.append({"path": str(config), "reason": "configuration is missing proposed photo references"})
        targets.pop(config, None)
    for path, by_id in sorted(targets.items(), key=lambda item: str(item[0]).casefold()):
        payload = path.read_bytes()
        before_hash = hashlib.sha256(payload).hexdigest()
        if before_hash != inventory["fileHashes"].get(str(path)):
            raise ValueError(f"consumer workflow changed before retarget planning: {path}")
        document = json.loads(payload.decode("utf-8-sig"))
        changes = []
        try:
            for photo_id, proposal in sorted(by_id.items()):
                before = pathlib.Path(proposal["beforeDerivative"]).name
                after = pathlib.Path(proposal["afterDerivative"]).name
                if path == config:
                    references = actions.workflow_photo_references(document, [photo_id.split(":", 1)[1]])
                    expected = {}
                    for binding in proposal["selectionChanges"]:
                        hero = binding["hero"].replace("~", "~0").replace("/", "~1")
                        if binding["flow"] is None:
                            pointer = f"/photos/{hero}"
                        else:
                            flow = binding["flow"].replace("~", "~0").replace("/", "~1")
                            pointer = f"/flows/{flow}/photos/{hero}"
                        if (pointer in expected or binding.get("after") != after
                                or binding.get("before", "").casefold() != before.casefold()):
                            raise ValueError("configuration has conflicting replacement bindings")
                        expected[pointer] = binding["before"]
                    if ({item["pointer"] for item in references} != set(expected)
                            or any(item.get("objectKey")
                            or item["pointer"] not in expected
                            or item["value"].casefold() != expected[item["pointer"]].casefold()
                            for item in references)):
                        raise ValueError("configuration has an unclassified old-photo reference")
                    changes.extend({"photoId": photo_id, "pointer": item["pointer"]} for item in references)
                    for binding in proposal["selectionChanges"]:
                        selection = document["photos"] if binding["flow"] is None else (
                            document["flows"][binding["flow"]]["photos"]
                        )
                        selection[binding["hero"]] = binding["after"]
                else:
                    document, pointers = actions.plan_workflow_photo_retarget(document, before, after)
                    changes.extend({"photoId": photo_id, "pointer": pointer} for pointer in pointers)
            for photo_id in by_id:
                if actions.workflow_photo_references(document, [photo_id.split(":", 1)[1]]):
                    raise ValueError("retarget leaves an old-photo reference")
        except ValueError as exc:
            blocked.append({"path": str(path), "reason": str(exc)})
            continue
        after = (json.dumps(document, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
        plans.append({"path": str(path), "beforeSHA256": before_hash,
                      "kind": "configuration" if path == config else "workflow",
                      "afterSHA256": hashlib.sha256(after).hexdigest(), "afterBytes": after,
                      "changes": changes})
        if actions.metadata.content_sha256(path) != before_hash:
            raise ValueError(f"consumer workflow changed during retarget planning: {path}")
    return {"plans": plans, "blocked": blocked, "consumerCoverageVerified": False}


def workspace_input_roots(cfg):
    roots = {"shared": likeness.cw.shared_input_root(cfg)}
    roots.update({f"workspace:{name}": likeness.cw.input_dir(cfg, name) for name in cfg["workspaces"]})
    base = pathlib.Path(likeness.cw.comfy_input_root(cfg)).absolute()
    if likeness.cw.is_reparse_point(base):
        raise ValueError(f"unidentified input inventory refuses linked input root: {base}")
    if not base.exists():
        roots["unconfigured-input-root"] = base
        return roots
    if not base.is_dir() or base.resolve() != base:
        raise ValueError(f"unidentified input inventory refuses invalid or linked input root: {base}")
    entries = sorted(base.iterdir(), key=lambda path: path.name.casefold())
    if len(entries) > 10000:
        raise ValueError("unidentified input inventory exceeds 10,000 input-root entries")
    configured = {name.casefold() for name in cfg["workspaces"]}
    for entry in entries:
        if entry.is_symlink() or likeness.cw.is_reparse_point(entry):
            raise ValueError(f"unidentified input inventory refuses linked input directory: {entry}")
        if entry.name.casefold() in configured or not entry.is_dir():
            continue
        roots[f"unconfigured-input:{entry.name}"] = entry
    return roots


def inspect_unidentified_inputs(cfg, candidates, proposals):
    """Compare unidentified configured input bytes with bound red native/derivative bytes."""
    from likeness_library import normal_transaction

    hashes = {}
    for candidate in candidates:
        hashes.setdefault(candidate["sha256"], set()).add(candidate["photoId"])
    for proposal in proposals:
        if proposal["state"] == "proposed":
            hashes.setdefault(proposal["beforeDerivativeSHA256"], set()).add(proposal["photoId"])
    bindings = [row for row in actions.selected_photo_bindings(cfg) if row["photoId"] is None]
    roots = workspace_input_roots(cfg)
    checked, missing, matches = {}, [], []
    total_bytes = 0
    for scope, raw in roots.items():
        root = pathlib.Path(raw).absolute()
        if not root.is_dir():
            if root.exists():
                raise ValueError(f"unidentified input root is not a directory: {root}")
            missing.append({"scope": scope, "path": str(root), "reason": "input root unavailable"})
            continue
        if root.resolve() != root or likeness.cw.is_reparse_point(root):
            raise ValueError(f"unidentified input inventory refuses linked root: {root}")
        for binding in bindings:
            name = binding["filename"]
            if not isinstance(name, str) or not name or "/" in name or "\\" in name or ":" in name:
                raise ValueError("unidentified configured selection is not a simple input filename")
            path = normal_transaction.safe(root, name)
            if not path.is_file():
                if path.exists():
                    raise ValueError(f"configured workflow input is not a file: {path}")
                missing.append({"scope": scope, "path": str(path), "reason": "configured input missing"})
                continue
            if path not in checked:
                total_bytes += path.stat().st_size
                if total_bytes > MAX_CONSUMER_BYTES:
                    raise ValueError("unidentified input inventory exceeds 512 MiB")
                checked[path] = actions.metadata.content_sha256(path)
            checksum = checked[path]
            for photo_id in sorted(hashes.get(checksum, ())):
                matches.append({"scope": scope, "path": str(path), "photoId": photo_id})
    for path, digest in checked.items():
        if actions.metadata.content_sha256(path) != digest:
            raise ValueError(f"unidentified workflow input changed during inspection: {path}")
    for row in missing:
        if pathlib.Path(row["path"]).exists():
            raise ValueError(f"unidentified workflow input appeared during inspection: {row['path']}")
    if workspace_input_roots(cfg) != roots:
        raise ValueError("local workflow input inventory changed during inspection")
    return {
        "checkedFiles": len(checked), "missing": missing, "exactMatches": matches,
        "consumerCoverageVerified": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="absolute Sandbox Working root")
    parser.add_argument("--receipt", required=True, help="saved applied SIMPLE receipt")
    parser.add_argument("--report", required=True, help="checked saved snapshot HTML")
    parser.add_argument("--cache", required=True, help="root-local saved general-domain cache")
    parser.add_argument("--workflow-configuration",
                        help="inspect the configuration bound by the report; defaults to the current configuration")
    parser.add_argument("--check", action="store_true", help="recheck evidence; identical to default read-only mode")
    parser.add_argument("--inspect-consumers", action="store_true",
                        help="also scan reachable workflow JSON and unidentified selected inputs; never modifies them")
    parser.add_argument("--simulate-routes", action="store_true",
                        help="also show hypothetical routes assuming all workflow gaps are resolved; never applies")
    parser.add_argument("--simulate-core-refresh", action="store_true",
                        help="also rebuild affected Review cores for an all-Review hypothetical; never applies")
    parser.add_argument("--simulate-destination-scores", action="store_true",
                        help="also score hypothetical Review destinations; never applies")
    args = parser.parse_args(argv)
    if not pathlib.Path(args.root).is_absolute():
        parser.error("--root must be absolute")
    if args.simulate_core_refresh and not args.simulate_routes:
        parser.error("--simulate-core-refresh requires --simulate-routes")
    if args.simulate_destination_scores and not args.simulate_core_refresh:
        parser.error("--simulate-destination-scores requires --simulate-core-refresh")
    cfg = likeness.cw.load_cfg()
    options = {"receipt": args.receipt, "report": args.report}
    if args.simulate_routes:
        options["simulate_all"] = True
    if args.simulate_core_refresh:
        options["simulate_core_refresh"] = True
    if args.simulate_destination_scores:
        options["simulate_destination_scores"] = True
    if args.workflow_configuration:
        options["workflow_configuration_path"] = args.workflow_configuration
    result = normal_admission.checked_red_release_diagnostic(
        likeness, args.root, cfg, policy.load_policy(), args.cache, **options,
    )
    print("READ-ONLY DIAGNOSTIC: does not approve or apply a release")
    print(f"Candidates: {result['candidateCount']}; blocked: "
          f"{sum(bool(row.get('releaseBlocked')) for row in result['held'])}; "
          f"proposed assignments: {len(result['assignments'])}")
    census = result["redRefreshCensus"]
    print(f"Fixed saved-Review core removal: {len(census['affectedOwners'])} affected owners, "
          f"{census['checkedCount']} scores checked, {len(census['newlyRed'])} newly red among those checked, "
          f"and {len(census['unavailable'])} affected scores unavailable; "
          "this does not rebuild cores or count all post-routing newly red photos")
    for gap in result["workflowGaps"]:
        print(f"Workflow gap: {gap}")
    for proposal in result["workflowReplacementProposals"]:
        if proposal["state"] == "proposed":
            print(f"Replacement proposal: {proposal['photoId']} -> {proposal['replacementPhotoId']} "
                  f"(saved score {proposal['replacementScore']:.6f}); consumer coverage not verified")
        else:
            print(f"Replacement blocked: {proposal['photoId']}: {proposal['reason']}")
    for row in result["held"]:
        print(f"{row['photoId']}: {row['reason']}")
    if args.simulate_routes:
        simulated = result["hypotheticalRouting"]
        print("HYPOTHETICAL ONLY: assumes workflow replacement and all consumer gaps are resolved; not an executable preview")
        for row in simulated["assignments"] + simulated["held"]:
            destination = row.get("destination") or row.get("reviewDestination") or "blocked"
            print(f"Hypothetical route: {row['photoId']}: {row['sourceFolder']} -> {destination}: {row['reason']}")
    if args.simulate_core_refresh:
        refreshed = result["hypotheticalReviewCensus"]
        moved_label = ("destination scores are hypothetical" if args.simulate_destination_scores
                       else "moved photos are not rescored")
        print(f"HYPOTHETICAL rebuilt Review cores: {len(refreshed['affectedOwners'])} owners, "
              f"{refreshed['checkedCount']} unmoved scores checked, {len(refreshed['newlyRed'])} newly red, "
              f"{len(refreshed['unavailable'])} unavailable; {moved_label}; not an executable preview")
        for row in refreshed["newlyRed"]:
            print(f"Hypothetical newly red: {row['photoId']} in {row['owner']}: "
                  f"{row['savedScore']:.6f} -> {row['refreshedScore']:.6f}")
        for row in refreshed["unavailable"]:
            print(f"Hypothetical score unavailable: {row['photoId']} in {row['owner']}: {row['reason']}")
        if args.simulate_destination_scores:
            for row in refreshed["movedScores"]:
                value = (f"{row['score']!r} ({row['band']})" if row["score"] is not None
                         else row["reason"])
                print(f"Hypothetical destination score: {row['photoId']} in {row['owner']}: {value}")
    if args.inspect_consumers:
        workflow_config_path = pathlib.Path(args.workflow_configuration or likeness.cw.CFG_PATH).absolute()
        workflow_cfg = likeness.cw.validate_config(json.loads(workflow_config_path.read_bytes()))
        print("Scanning repository and configured workspace JSON, then unidentified selected input bytes", flush=True)
        scopes = {"repository": likeness.cw.WF}
        workspace_scopes = workspace_consumer_scopes(workflow_cfg)
        scopes.update(workspace_scopes)
        ids = [row["photoId"] for row in result["held"] + result["assignments"]]
        inventory = inspect_consumers(scopes, ids)
        if workspace_consumer_scopes(workflow_cfg) != workspace_scopes:
            raise ValueError("local workspace inventory changed during consumer scan")
        print(f"Consumer scan: {inventory['files']} JSON files, {len(inventory['matches'])} matching references, "
              f"{len(inventory['unavailable'])} unavailable roots; coverage is not verified")
        for missing in inventory["unavailable"]:
            print(f"Unavailable consumer root: {missing['scope']}: {missing['path']}")
        for match in inventory["matches"]:
            print(f"Consumer reference: {match['scope']}: {match['path']} {match['pointer']}")
        print("JSON scan alone does not verify input image bytes or unidentified selections")
        retargets = plan_consumer_retargets(
            inventory, result["workflowReplacementProposals"], workflow_config_path,
        )
        print(f"Retarget planning: {len(retargets['plans'])} files, {len(retargets['blocked'])} blocked; no changes made")
        for blocked in retargets["blocked"]:
            print(f"Retarget blocked: {blocked['path']}: {blocked['reason']}")
        inputs = inspect_unidentified_inputs(
            workflow_cfg, result["redCandidateBindings"], result["workflowReplacementProposals"],
        )
        print(f"Unidentified inputs: {inputs['checkedFiles']} unique files checked, "
              f"{len(inputs['missing'])} missing, {len(inputs['exactMatches'])} exact red-byte matches; "
              "non-identical images remain unresolved")
        for missing in inputs["missing"]:
            if missing["reason"] == "input root unavailable":
                print(f"Unavailable input root: {missing['scope']}: {missing['path']}")
        for match in inputs["exactMatches"]:
            print(f"Exact red-byte input: {match['scope']}: {match['path']}: {match['photoId']}")
        for path, digest in result["snapshotInputs"].items():
            if actions.metadata.content_sha256(pathlib.Path(path)) != digest:
                raise ValueError(f"red snapshot input changed during consumer scan: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
