"""Receipt-only experiments using the maintained candidate planner and refinement."""
import collections
import hashlib
import json
import pathlib
import time

import numpy as np

from . import refinement
from .planner import plan_candidates
from .reconciliation import _average_linkage
from .scoring import nz

SEEDS = ("angelica", "vale", "uma zane", "gaia thorn")
REPLAY_MODULES = (
    "planner.py", "refinement.py", "reconciliation.py", "scoring.py",
    "audit.py", "policy.py", "rejections.py",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folder_for(row):
    parts = pathlib.PurePosixPath(row["destination"]).parts
    if len(parts) == 3 and parts[0] == "Various" and parts[-2] in {"gallery", "review"}:
        return "Various"
    if len(parts) != 4 or parts[-2] not in {"gallery", "review"}:
        raise ValueError(f"unsupported baseline photo location: {row['destination']}")
    return "/".join(parts[:2])


def select_scope(run, seeds=SEEDS, *, hops=1, minimum_score=0.3, max_photos=1500):
    """Include whole seed identities and bounded saved-rival neighbours, not truth labels."""
    photos = collections.defaultdict(list)
    for row in run["photos"]:
        photos[folder_for(row)].append(row)
    matched = {}
    for seed in seeds:
        words = seed.casefold().split()
        matched[seed] = sorted(
            folder for folder in photos
            if all(word in folder.split("/")[-1].casefold().replace("_", " ").split() for word in words)
        )
        if not matched[seed]:
            raise ValueError(f"scope seed has no saved identity: {seed}")
    selected = {folder for folders in matched.values() for folder in folders}
    reasons = {folder: ["name seed (not an identity label)"] for folder in selected}
    audit = {row["photoId"]: row for row in run["finalMembershipAudit"]["rows"]}
    edges = collections.defaultdict(set)
    for folder, rows in photos.items():
        for photo in rows:
            for rival in audit.get(photo.get("photoId"), {}).get("rivals", []):
                if rival["score"] >= minimum_score and rival["folder"] in photos:
                    edges[folder].add(rival["folder"])
                    edges[rival["folder"]].add(folder)
    for hop in range(hops):
        additions = set().union(*(edges[folder] for folder in selected)) - selected
        for folder in additions:
            reasons[folder] = [f"saved top-three rival edge, hop {hop + 1}"]
        selected.update(additions)
    count = sum(len(photos[folder]) for folder in selected)
    if count > max_photos:
        raise ValueError(
            f"whole-identity scope requires {count} photos, exceeding --max-photos {max_photos}; "
            "raise the explicit limit or reduce hops, never silently truncate"
        )
    return {
        "seeds": matched, "hops": hops, "minimumRivalScore": minimum_score,
        "photoCount": count, "identityCount": len(selected),
        "identities": [
            {"folder": folder, "photoIds": sorted(row["photoId"] for row in photos[folder]),
             "personIds": sorted({
                 person_id for row in photos[folder]
                 for person_id in audit.get(row["photoId"], {}).get("identityIds", [])
             }),
             "reason": reasons[folder]}
            for folder in sorted(selected)
        ],
        "photos": [
            {
                "photoId": row["photoId"], "source": row.get("source"),
                "destination": row["destination"], "preparedSHA256": row.get("preparedSHA256"),
                "savedAudit": {
                    key: audit.get(row["photoId"], {}).get(key) for key in (
                        "ownScore", "rivals", "coreMember", "protected", "anchor",
                        "workflowSelected", "qualityEligible", "rejectionHistory", "refinementDecision",
                    )
                },
                "humanLabel": "unlabelled; saved membership is not ground truth",
            }
            for folder in sorted(selected) for row in sorted(photos[folder], key=lambda row: row["photoId"])
        ],
        "scopeLimit": "Saved rivals contain only the top three; this is a screening cohort, not a closed family.",
        "referenceBoundary": "Replay still uses ALL original candidates and ALL original cast cores.",
    }


def load_bundle(run_dir, *, max_json_bytes=128 * 1024 * 1024):
    paths = {name: run_dir / name for name in (
        "run.json", "likeness-cache.json", "policy.json",
        "seed-catalog.json", "config-snapshot.json",
    )}
    if sum(path.stat().st_size for path in paths.values()) > max_json_bytes:
        raise ValueError("saved JSON inputs exceed the explicit input-byte limit")
    raw = {name: path.read_bytes() for name, path in paths.items()}
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
    data = {name: json.loads(value) for name, value in raw.items()}
    run, cache = data["run.json"], data["likeness-cache.json"]
    if run.get("status") != "applied" or run.get("castSeedPolicy") != "core":
        raise ValueError("baseline must be a completed applied core-seed run")
    if run["policy"] != data["policy.json"]:
        raise ValueError("saved policy differs from the baseline receipt")
    if run.get("continuationCacheSHA256") != hashes["likeness-cache.json"]:
        raise ValueError("cached measurements differ from the continuation receipt")
    for field, name in (("seedCatalogSHA256", "seed-catalog.json"),
                        ("configSnapshotSHA256", "config-snapshot.json")):
        if run.get(field) != hashes[name]:
            raise ValueError(f"baseline {field} does not match {name}")
    seed = data["seed-catalog.json"]
    if seed.get("photos") or seed.get("people") or seed.get("actions"):
        raise ValueError("this first replay contract requires the empty preview11 manual-intent seed")
    if run["workflowSelection"]["policy"] != {"mode": "all"}:
        raise ValueError("this replay contract requires the baseline all-workflow reset")
    here = pathlib.Path(__file__).parent
    implementations = {name: digest(here / name) for name in REPLAY_MODULES}
    for name in REPLAY_MODULES:
        expected = run["implementationHashes"].get(name)
        if name != "scoring.py" and expected is None:
            raise ValueError(f"baseline implementation binding missing: {name}")
        if expected is not None and expected != implementations[name]:
            raise ValueError(f"baseline implementation differs: {name}; do not relabel changed code as baseline")
    mean = np.asarray(run["centeringMean"], dtype=float)
    if mean.ndim != 1 or not mean.size or not np.isfinite(mean).all():
        raise ValueError("invalid saved global centering mean")
    if not np.array_equal(mean, np.asarray(cache["centeringMean"], dtype=float)):
        raise ValueError("cache and receipt have different centering contexts")
    bound, models = {}, set()
    for item in cache["emb"].values():
        evidence = item.get("alignmentEvidence") or {}
        sha = evidence.get("sourceSha256")
        if not sha or not item.get("v"):
            continue
        if sha in bound and bound[sha] != item:
            raise ValueError(f"conflicting cached measurements: {sha}")
        model = evidence.get("model")
        model_id = hashlib.sha256(
            json.dumps(model, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if not model or evidence.get("modelId") != model_id:
            raise ValueError(f"invalid model provenance for cached measurement: {sha}")
        models.add(model_id)
        bound[sha] = item
    if len(models) != 1:
        raise ValueError("baseline requires exactly one bound measurement model")
    vectors = {}
    ids = set()
    for row in run["photos"]:
        pid = row.get("photoId")
        if not pid or pid in ids:
            raise ValueError("baseline requires unique stable IDs for every saved photo")
        ids.add(pid)
        item = bound.get(row.get("preparedSHA256"))
        if item is not None:
            vector = np.asarray(item["v"], dtype=float)
            if vector.shape != mean.shape or not np.isfinite(vector).all():
                raise ValueError(f"invalid cached vector: {pid}")
            vector = nz(vector - mean)
            if np.linalg.norm(vector) == 0:
                raise ValueError(f"zero centered vector: {pid}")
            vectors[pid] = vector
        elif row.get("castSeedCore") or "initialBestCast" in row:
            raise ValueError(f"missing content-bound cached measurement: {pid}")
    provenance = {
        "inputs": {name: {"path": str(paths[name]), "sha256": hashes[name]} for name in paths},
        "implementations": implementations,
        "harnessSHA256": digest(pathlib.Path(__file__)),
        "modelIds": sorted(models),
        "centering": "Exact saved full-population mean; never recentered on scope.",
        "jsonInputBytesRead": sum(len(value) for value in raw.values()),
        "imageReads": 0, "modelCalls": 0,
    }
    return run, vectors, provenance


def replay_inputs(run, vectors):
    groups = collections.defaultdict(list)
    candidates = []
    for row in run["photos"]:
        pid = row["photoId"]
        if row.get("castSeedCore"):
            groups[row["oldFolder"]].append(vectors[pid])
        if "initialBestCast" in row:
            candidates.append({
                "photoId": pid, "sourceFolder": "Various", "sourceBucket": "Pool",
                "side": "Prospects", "vector": vectors[pid],
                "rejectedPersonIds": row.get("excludedIdentityIds", []),
            })
    quality_holds = sum(bool(row.get("qualityHold")) for row in run["photos"])
    if len(candidates) + quality_holds != run["candidateCount"] or not groups:
        raise ValueError("candidate/core reconstruction differs from receipt counts")
    cores = {
        folder: {"vector": nz(np.mean(values, axis=0)), "side": "Prospects",
                 "category": folder.split("/")[0]}
        for folder, values in groups.items()
    }
    errors = []
    for row in run["photos"]:
        if "initialBestCast" not in row:
            continue
        ranked = sorted(
            ((float(vectors[row["photoId"]] @ core["vector"]), folder)
             for folder, core in cores.items()), key=lambda pair: (-pair[0], pair[1].casefold()),
        )
        if (ranked[0][1] != row["initialBestCast"]
                or abs(ranked[0][0] - row["initialBestCastScore"]) > 1e-10):
            errors.append(row["photoId"])
    if errors:
        raise ValueError(f"original cast score parity failed for {len(errors)} photos: {errors[:5]}")
    return candidates, cores


def stage_fingerprint(result):
    rows = result["assignments"] + result["held"]
    if len({row["photoId"] for row in rows}) != len(rows):
        raise ValueError("candidate-stage decisions contain duplicate photo IDs")
    groups = collections.defaultdict(list)
    for row in rows:
        groups[row["clusterId"]].append(row["photoId"])
    return {
        row["photoId"]: {
            "members": sorted(groups[row["clusterId"]]),
            "route": (row.get("reviewDestination") or row.get("destination") or "Various/review"),
            "bestMatch": row.get("bestMatch"), "bestScore": row.get("bestScore"),
        }
        for row in rows
    }


def refinement_signature(evidence):
    return {
        **{key: evidence[key] for key in (
            "passCount", "stopReason", "moveCount", "mergeCount", "dissolvedCount",
        )},
        "moves": sorted(
            (index, row["photoId"], row["kind"], row["ownScore"], row["rivalScore"], row["lead"])
            for index, step in enumerate(evidence["passes"]) for row in step["moves"]
        ),
    }


def experiment(run, vectors, *, compare_order=False):
    candidates, cores = replay_inputs(run, vectors)
    trials, baseline, first = [], None, None
    orders = ("baseline", "identical-repeat", "reverse-input") if compare_order else ("baseline",)
    for label in orders:
        started = time.perf_counter()
        cpu_started = time.process_time()
        ordered = list(reversed(candidates)) if label == "reverse-input" else candidates
        result = plan_candidates(
            ordered, cores, run["policy"], lambda seed, taken: f"Shadow {seed}", (), _average_linkage,
        )
        result, evidence = refinement.refine(result, ordered, cores, run["policy"])
        fingerprint = stage_fingerprint(result)
        if set(fingerprint) != {row["photoId"] for row in candidates}:
            raise ValueError("candidate-stage replay did not conserve all photo IDs")
        signature = refinement_signature(evidence)
        if baseline is None:
            if signature != refinement_signature(run["membershipRefinement"]):
                raise ValueError("saved provisional refinement parity failed; no experimental baseline claimed")
            baseline, first = fingerprint, signature
        elif signature != first or fingerprint != baseline:
            raise ValueError(f"{label} changed candidate-stage decisions")
        trials.append({
            "name": label, "seconds": time.perf_counter() - started,
            "cpuSeconds": time.process_time() - cpu_started,
            "photoCount": len(fingerprint), "changedPhotoIds": [],
            "refinement": signature,
        })
    return {
        "stage": "Full original candidate planner + provisional membership refinement ONLY",
        "notReplayed": [
            "Final Gallery audit/admission/refinement, continuity, naming, categories after installation",
            "Preparation, intake, model inference, derivatives, reports, installation",
        ],
        "scopeDoesNotRestrictCompetition": True,
        "originalCandidateCount": len(candidates), "originalCastCoreCount": len(cores),
        "originalCastScoreParity": len(candidates),
        "savedProvisionalRefinementParity": True,
        "trials": trials, "decisions": baseline,
        "accuracyClaim": "None: recorded memberships and surnames are not human identity labels.",
    }
