"""Reuse a sandbox LEAN intake for a separately reviewed, reset-only matching preview."""
import argparse
import copy
import json
import pathlib
import re
import sys
from types import SimpleNamespace

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "art"))
sys.path.insert(0, str(REPO))

from tools.art import likeness
from tools.art.likeness_library import clean_preparation, clean_rebase, metadata, rebase_recap, sandbox
from tools.art.likeness_library.policy import load_policy

NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def bound_run(working, name):
    if not NAME.fullmatch(name) or name in (".", ".."):
        raise ValueError("run names must be plain folder names")
    path = working / "_sandbox-state" / name
    for candidate in (path, *path.parents):
        if sandbox._is_reparse_point(candidate):
            raise ValueError(f"linked continuation path: {candidate}")
    return path


def inspect(working, source_name, target_name):
    working = pathlib.Path(working)
    if not working.is_absolute() or not sandbox.is_sandbox_working_path(working):
        raise ValueError("continuation requires an absolute Sovereign Territories Sandbox\\Working root")
    if not (working.parent / "Source").is_dir() or not (working.parent / "source-manifest.json").is_file():
        raise ValueError("continuation requires the sandbox source snapshot")
    source, target = bound_run(working, source_name), bound_run(working, target_name)
    if source == target:
        raise ValueError("continuation must use a separate run; the original receipt is never replanned")
    plan = load(source / "run.json")
    if (pathlib.Path(plan["workingRoot"]) != working or not plan.get("preparation")
            or plan["preparation"].get("storageMode") != "lean"
            or plan["preparation"].get("processingProfile", "standard") != "standard"
            or plan["status"] not in ("applied", "preview")):
        raise ValueError("source must be a completed LEAN matching run belonging to this sandbox")
    intake = load(source / "intake.json")
    if intake.get("reusedFrom"):
        raise ValueError("reference the original intake, not a chained continuation")
    if target.exists() and not (target / "continuation.json").is_file():
        raise ValueError("target run already exists without a continuation receipt; choose a new run")
    return source, target, plan


def seed_catalog(source_plan, current, seed, installed=None):
    """Keep original identity evidence; carry only explicit content-bound decisions."""
    result = copy.deepcopy(seed)
    if installed is not None:
        known_actions = {row["id"] for row in installed["actions"]}
        supported = {
            "anchor-added", "anchor-removed", "photo-protected", "photo-unprotected",
            "person-protected", "person-unprotected", "match-rejected", "workflow-photo-selected",
        }
        unsupported = [
            row for row in current["actions"]
            if row["id"] not in known_actions and row["type"] not in supported
        ]
        if unsupported:
            raise ValueError("intervening placement/retirement/rename decisions require explicit migration before reuse")
    original_rows = {row.get("photoId"): row for row in source_plan["photos"] if row.get("photoId")}
    for photo_id, record in current["photos"].items():
        if installed is not None and record == installed["photos"].get(photo_id):
            continue
        original = seed["photos"].get(photo_id, {})
        automatic = record.get("protectionProvenance")
        explicit = (
            record.get("rejectedPersonIds") or record.get("automaticProtectionOverride")
            or (record.get("protected") and not automatic)
        )
        if not explicit or record == original:
            continue
        row = original_rows.get(photo_id)
        if not row or record["contentSha256"] not in (row["sha256"], row.get("preparedSHA256")):
            raise ValueError(f"cannot rebind manual decision to original prepared bytes: {photo_id}")
        rejected = record.get("rejectedPersonIds", [])
        if any(person_id not in seed["people"] for person_id in rejected):
            raise ValueError(f"manual rejection targets a generated identity; explicitly reconcile before reuse: {photo_id}")
        copied = copy.deepcopy(record)
        copied["contentSha256"] = row["sha256"]
        result["photos"][photo_id] = copied
    for person_id, person in current["people"].items():
        if installed is not None and person == installed["people"].get(person_id):
            continue
        old = result["people"].get(person_id)
        manual_protection = person.get("protected") and not person.get("protectionProvenance")
        if old is None:
            prior = installed["people"].get(person_id) if installed is not None else None
            if (prior is not None
                    and all(person.get(field) == prior.get(field)
                            for field in ("identityAnchors", "automaticProtectionOverride"))
                    and (not manual_protection or prior.get("protected"))):
                continue
            if person.get("automaticProtectionOverride") or person.get("identityAnchors") or manual_protection:
                raise ValueError(
                    "new identity manual decisions require explicit migration before saved-input reuse: "
                    f"{person_id} ({person['folder']})"
                )
            continue
        if person.get("identityAnchors") != old.get("identityAnchors"):
            old["identityAnchors"] = list(person.get("identityAnchors", []))
        if person.get("automaticProtectionOverride"):
            old["automaticProtectionOverride"] = person["automaticProtectionOverride"]
            old["protected"] = person.get("protected", False)
        elif manual_protection:
            old["protected"] = True
            old.pop("protectionProvenance", None)
    metadata.validate_catalog(result)
    return result


class CachedOnlyEmbedder:
    def __call__(self, path):
        raise ValueError(f"saved face measurement unavailable; explicit new preparation required: {path}")


def _api(cfg):
    class FrozenWorkflows:
        def __getattr__(self, name):
            return getattr(likeness.cw, name)

        def load_cfg(self):
            return copy.deepcopy(cfg)

    return SimpleNamespace(**{
        **vars(likeness), "cw": FrozenWorkflows(),
    })


def _layout(working, source):
    layout = sandbox.validate_sandbox(working)
    return clean_rebase._verify_source_overlay(layout, source) if (source / "source-overlay").exists() else layout


def command(args):
    regroup = args.regroup
    if args.directed and not regroup:
        raise ValueError("directed mode requires regrouping")
    if args.directed and not args.directed_recipe:
        raise ValueError("directed mode requires an explicit recipe")
    if args.directed_recipe and not args.directed:
        raise ValueError("directed recipe requires directed mode")
    if args.review_source and not regroup:
        raise ValueError("review evidence requires regrouping")
    recipe = None
    if args.directed:
        from tools.art.likeness_library.directed_reformation import recipe_named
        recipe = recipe_named(args.directed_recipe)["name"]
    review_source = pathlib.Path(args.review_source) if args.review_source else None
    if review_source is not None and not review_source.is_absolute():
        raise ValueError("review evidence path must be absolute")
    grouping = {
        "regroup": regroup, "directedRecipe": recipe,
        "reviewSource": str(review_source) if review_source else None,
    }
    working = pathlib.Path(args.root)
    source, target, original = inspect(working, args.source_run, args.run)
    if args.dry_run or not any((args.apply, args.check, args.install)):
        print(f"LEAN continuation preview: {source.name} -> {target.name}")
        print("Reuse original prepared pixels and measured faces; recompute cast cores, grouping, refinement and names.")
        print("No reset, intake, backup or rollback. Recovery after failed installation is a fresh sandbox reset.")
        print("--apply creates matching preview only; --install publishes it; --check verifies without writes.")
        print(f"Grouping: {'directed ' + recipe if recipe else 'historical regroup' if regroup else 'historical default'}")
        print(f"Original intake count: {original['preparation']['inputCount']}; no matching was started.")
        return {"status": "inventory"}
    layout = _layout(working, source)
    if args.check and not target.exists():
        output, data = clean_preparation.verify(layout, source)
        print(f"Saved preparation verified: {len(data['photos'])} rows at {output}")
        return {"status": "source-verified"}
    if target.exists():
        receipt = load(target / "continuation.json")
        recorded_grouping = receipt.get("grouping", {
            "regroup": False, "directedRecipe": None, "reviewSource": None,
        })
        if recorded_grouping != grouping:
            raise ValueError("saved continuation grouping mode/recipe or review source differs")
        if receipt["sourceRun"] != str(source):
            raise ValueError("continuation belongs to another original intake")
        for name, digest in receipt["sourceFiles"].items():
            if metadata.content_sha256(source / name) != digest:
                raise ValueError(f"saved continuation source changed: {name}")
        plan = load(target / "run.json") if (target / "run.json").is_file() else None
        if plan is None:
            raise ValueError("incomplete continuation preview; choose a new run (no intake is repeated)")
        for name, field in (("seed-catalog.json", "seedCatalogSHA256"),
                            ("config-snapshot.json", "configSnapshotSHA256")):
            if metadata.content_sha256(target / name) != plan[field]:
                raise ValueError(f"continuation input snapshot changed: {name}")
        clean_preparation.verify(layout, target)
        if plan["status"] == "reset-required":
            raise ValueError("previous publication failed without rollback; reset sandbox before continuing")
        if plan["status"] != "applied" and (args.install or args.check):
            clean_rebase._verify_implementation_hashes(plan)
            if metadata.content_sha256(target / "likeness-cache.json") != plan["continuationCacheSHA256"]:
                raise ValueError("continuation measurements changed since preview")
        if args.install:
            if plan["status"] != "applied":
                clean_rebase.install_plan(layout, target, plan, preserve_legacy=True)
            clean_rebase._check_publication(working, plan)
            clean_rebase._refresh_galleries(working, target)
            rebase_recap.main([str(target)])
        elif args.check:
            if plan["status"] == "applied":
                clean_rebase._check_publication(working, plan)
            else:
                clean_rebase._verify_routes(plan, layout["source_root"])
                if metadata.content_sha256(metadata.path_for_root(working)) != plan["sourceCatalogSHA256"]:
                    raise ValueError("Working decisions changed since preview; create a new continuation")
                if metadata.content_sha256(target / "catalog.json") != plan["catalogSHA256"]:
                    raise ValueError("continuation catalogue changed")
            print(f"LEAN continuation verified: {plan['status']}")
        else:
            rebase_recap.main([str(target)])
            print("Matching preview already exists; recap refreshed only; not installed. "
                  "Use --check, --install or a new run name for new logic.")
        return plan
    if args.check or args.install:
        raise ValueError("create a separate matching preview with --apply before installation")
    cfg = likeness.cw.load_cfg()
    current = metadata.load_catalog(metadata.path_for_root(working))
    candidates = [
        (source / "seed-catalog.json", original.get("seedCatalogSHA256", original["sourceCatalogSHA256"])),
        (metadata.CATALOG_PATH, original["sourceCatalogSHA256"]),
    ]
    seed_path = next((
        path for path, digest in candidates if path.is_file()
        and metadata.content_sha256(path) == digest
    ), None)
    if seed_path is None:
        raise ValueError("exact original catalogue is unavailable; supply a fresh source rebase instead")
    if metadata.content_sha256(source / "catalog.json") != original["catalogSHA256"]:
        raise ValueError("original matched catalogue changed; cannot isolate intervening manual decisions")
    seed = seed_catalog(original, current, metadata.load_catalog(seed_path), metadata.load_catalog(source / "catalog.json"))
    policy = clean_rebase.core_protection_policy(load_policy(args.policy))
    print("LEAN continuation: verifying saved preparation; cached measurements only.", flush=True)
    preparation = clean_preparation.verify(layout, source)
    if metadata.content_sha256(preparation[0] / "manifest.json") != original["preparation"]["manifestSHA256"]:
        raise ValueError("saved preparation differs from original matching receipt")
    print("LEAN continuation: verifying current-photo continuity against immutable matching IDs.", flush=True)
    working_inputs = clean_rebase._curation_inventory(layout, current)
    target.mkdir()
    receipt = {
        "schemaVersion": 1, "sourceRun": str(source), "recoveryMode": "disposable",
        "grouping": grouping,
        "sourceFiles": {name: metadata.content_sha256(source / name) for name in (
            "run.json", "intake.json", "likeness-cache.json",
        )},
    }
    clean_rebase._write_json(target / "continuation.json", receipt)
    clean_rebase._write_json(target / "intake.json", {
        "schemaVersion": 1, "reusedFrom": str(source), "recoveryMode": "disposable",
        "sourceReceiptSHA256": receipt["sourceFiles"]["intake.json"],
    })
    clean_rebase._write_json(target / "likeness-cache.json", load(source / "likeness-cache.json"))
    api = _api(cfg)
    plan = clean_rebase.create_plan(
        layout, target, policy, api, embedder=CachedOnlyEmbedder(),
        reuse_measurements=True, preparation=preparation, cast_seeds="core",
        seed_catalog=seed, config_snapshot=cfg,
        working_inputs=working_inputs,
        matching_inputs={row["source"]: row["sha256"] for row in original["photos"]},
        workflow_reset={"mode": "all"},
        regroup=regroup, review_source=review_source, directed_recipe=recipe,
    )
    plan.update(
        recoveryMode="disposable", reusedPreparationFrom=str(source), rollbackCreated=False,
        continuationCacheSHA256=metadata.content_sha256(target / "likeness-cache.json"),
    )
    clean_rebase._write_json(target / "run.json", plan)
    clean_rebase._write_json(target / "policy.json", plan["policy"])
    rebase_recap.main([str(target)])
    print(f"Prepared-input matching preview complete: {target}; not installed; no backup/rollback created.")
    return plan


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--source-run", required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--policy")
    parser.add_argument("--regroup", action="store_true")
    parser.add_argument("--directed", action="store_true")
    parser.add_argument("--directed-recipe")
    parser.add_argument("--review-source")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true", help="create matching preview only, without intake or install")
    mode.add_argument("--install", action="store_true", help="install reviewed preview without backup/rollback")
    mode.add_argument("--check", action="store_true")
    command(parser.parse_args(argv))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(2)
