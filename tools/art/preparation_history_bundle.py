#!/usr/bin/env python3
"""Independent, bounded lossy preparation history; never a source-pruning operation."""
import argparse
import collections
import hashlib
import html
import io
import json
import math
import os
import pathlib
import re
import stat
import sys
import time
import warnings

from PIL import Image, ImageDraw, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "art"))
import image_preparation as preparation  # noqa: E402
import temporary_storage  # noqa: E402

FORMAT = "preparation-history-bundle-v1"
MAX_PHOTOS = 64
MAX_ROLES = 128
MAX_FILES = 20000
MAX_FILE_BYTES = 128 * 1024 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024 * 1024
MAX_JSON_BYTES = 32 * 1024 * 1024
MAX_PIXELS = 40000000
MAX_DIMENSION = 32768
COMPACT_EDGE = 640
TILE = (256, 224)
PRUNE = {
    "sourceReportKept": True,
    "sourceReportsDeleted": 0,
    "dependencyApprovalRequired": True,
    "status": "conversion-only-not-pruning",
    "remainingGap": (
        "Inventory active/installed/retained/backup/rollback/report dependencies; obtain explicit "
        "retention and deletion approval; implement and verify dependency-aware pruning separately. "
        "Lossy history is not exact diagnostic masks, alternative native stages or full recovery evidence."
    ),
}


def digest_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def safe(root, path):
    root, path = pathlib.Path(root), pathlib.Path(path)
    if not root.is_absolute() or not path.is_absolute():
        raise ValueError("paths must be absolute")
    if ".." in path.parts or path == root or root not in path.parents:
        raise ValueError(f"path must remain below root: {path}")
    for ancestor in (path, *path.parents):
        if ancestor.exists() or ancestor.is_symlink():
            info = ancestor.lstat()
            if (ancestor.is_symlink()
                    or getattr(info, "st_file_attributes", 0) & 0x400):
                raise ValueError(f"links/reparse points are forbidden: {ancestor}")
            if stat.S_ISREG(info.st_mode) and info.st_nlink != 1:
                raise ValueError(f"hardlinked file is forbidden: {ancestor}")
    if root.resolve() not in path.resolve().parents:
        raise ValueError("resolved path escapes root")
    return path


def relative_path(root, relative):
    if (not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative
            or relative.startswith("/") or any(p in ("", ".", "..") for p in relative.split("/"))):
        raise ValueError(f"unsafe relative path: {relative!r}")
    return safe(root, root.joinpath(*relative.split("/")))


def checksum(path, limit=None):
    limit = MAX_FILE_BYTES if limit is None else limit
    if not path.is_file() or path.stat().st_size > limit:
        raise ValueError(f"missing/oversized file: {path}")
    total, digest = 0, hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            total += len(chunk)
            if total > limit:
                raise ValueError(f"file grew beyond limit: {path}")
            digest.update(chunk)
    return {"sha256": digest.hexdigest(), "bytes": total}


def read_json(path):
    if path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError("manifest exceeds JSON byte limit")
    payload = path.read_bytes()
    if len(payload) > MAX_JSON_BYTES:
        raise ValueError("manifest grew beyond JSON byte limit")
    return json.loads(payload)


def tree(directory):
    """Bound membership as well as payloads, without following directory links."""
    inventory, pending, total, entries = {}, [directory], 0, 0
    while pending:
        parent = pending.pop()
        for path in parent.iterdir():
            entries += 1
            if entries > MAX_FILES:
                raise ValueError("file/directory count exceeds bound")
            safe(directory, path)
            if path.is_dir():
                pending.append(path)
            elif path.is_file():
                record = checksum(path)
                total += record["bytes"]
                if total > MAX_TOTAL_BYTES:
                    raise ValueError("total bytes exceed bound")
                inventory[path.relative_to(directory).as_posix()] = record
            else:
                raise ValueError(f"unsupported filesystem entry: {path}")
    return inventory


def roles(row):
    result = [{"role": "original", "sourcePath": row["retained"],
               "sourceSha256": row["sourceSha256"]}]
    for name, variant in sorted(row["variants"].items()):
        for field, checksum_field, label in (
                ("path", "sha256", "native"), ("thumbnail", "thumbnailSha256", "thumbnail"),
                ("padded", "paddedSha256", "padded")):
            if field in variant:
                result.append({"role": f"{name}/{label}", "sourcePath": variant[field],
                               "sourceSha256": variant[checksum_field]})
    if row.get("recommendedPadded"):
        value = row["recommendedPadded"]
        result.append({"role": "recommended/padded", "sourcePath": value["path"],
                       "sourceSha256": value["sha256"]})
    if len(result) > MAX_ROLES:
        raise ValueError("photo role count exceeds bound")
    return result


def exact_roles(row):
    selected = row["recommendation"]["use"]
    result = {"original": "original"}
    if selected == "none":
        return result
    if selected == "original":
        result["selectedNative"] = "original"
        if row.get("recommendedPadded"):
            result["selectedPadded"] = "recommended/padded"
        elif row["variants"].get("control", {}).get("padded"):
            result["selectedPadded"] = "control/padded"
    elif selected in row["variants"]:
        result["selectedNative"] = selected + "/native"
        if "padded" in row["variants"][selected]:
            result["selectedPadded"] = selected + "/padded"
    else:
        raise ValueError("selected native stage is missing")
    if "selectedPadded" not in result:
        raise ValueError("selected padded evidence is missing; choose a report with recorded workflow padding")
    return result


def source_root(root, report, recorded_root, cfg):
    """Accept only Working or a single clean-rebase run's input mirror."""
    root, report = pathlib.Path(root), pathlib.Path(report)
    if not isinstance(recorded_root, str):
        raise ValueError("source manifest root must be an absolute path")
    recorded = pathlib.Path(recorded_root)
    safe(root, report)
    if recorded != root:
        safe(root, recorded)
        parts = recorded.relative_to(root).parts
        if (len(parts) != 3 or parts[0] != "_sandbox-state" or parts[2] != "inputs"
                or parts[1].startswith(".")):
            raise ValueError("source root must be Working or Working\\_sandbox-state\\RUN\\inputs")
    expected = preparation.cw.storage_root(cfg, "reports", root=recorded) / "preparation"
    if report.parent != expected or report.name.startswith("."):
        raise ValueError("source report must be directly under its recorded root's configured reports\\preparation")
    safe(recorded, report)
    return recorded


def source_report(root, report):
    before = tree(report)
    data = read_json(relative_path(report, "manifest.json"))
    recorded = source_root(root, report, data["root"], preparation.cw.load_cfg())
    if not 1 <= len(data.get("photos", [])) <= MAX_PHOTOS:
        raise ValueError(f"source report must contain 1..{MAX_PHOTOS} photos (no implicit truncation)")
    for row in data["photos"]:
        for role in roles(row):
            entry = before.get(role["sourcePath"])
            if not entry or entry["sha256"] != role["sourceSha256"]:
                raise ValueError("source role payload missing or hash mismatch")
        exact_roles(row)
    # Historical inputs may have moved. The report's exact retained inputs, not
    # mutable Gallery paths, are the authority for this independent conversion.
    verified = preparation.verify(recorded, report, current_sources=False)
    if data != verified or tree(report) != before:
        raise ValueError("source report changed during verification")
    return data, before


def geometry(image):
    width, height = image.size
    if (width < 1 or height < 1 or max(width, height) > MAX_DIMENSION
            or width * height > MAX_PIXELS):
        raise ValueError("image geometry/pixels exceed bound")


def thumbnail(path, *, allow_invalid=False):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as opened:
                geometry(opened)
                if getattr(opened, "n_frames", 1) != 1:
                    raise ValueError("animated/multiframe history inputs are unsupported")
                opened.draft("RGB", (COMPACT_EDGE, COMPACT_EDGE))
                image = ImageOps.exif_transpose(opened)
                try:
                    geometry(image)
                    image.thumbnail((COMPACT_EDGE, COMPACT_EDGE), Image.Resampling.LANCZOS)
                    return image.convert("RGB")
                finally:
                    image.close()
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombWarning,
            Image.DecompressionBombError) as error:
        if not allow_invalid:
            raise ValueError(f"cannot decode bounded diagnostic history: {path}: {error}") from error
        image = Image.new("RGB", (COMPACT_EDGE, 160), "white")
        ImageDraw.Draw(image).text((12, 12), "UNPROCESSABLE original\nExact bytes retained; no decoded preview.",
                                  fill="black")
        return image


def jpeg(image):
    if max(image.size) > 4096 or image.width * image.height > 16777216:
        raise ValueError("JPEG output geometry exceeds bound")
    stream = io.BytesIO()
    image.save(stream, format="JPEG", quality=78, optimize=False, progressive=False)
    payload = stream.getvalue()
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("JPEG output exceeds byte bound")
    return payload


def write(path, payload):
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def add_payload(stage, name, payload, inventory, *, kind, row):
    write(relative_path(stage, name), payload)
    inventory[name] = {"sha256": digest_bytes(payload), "bytes": len(payload),
                       "kind": kind, "row": row}
    if sum(value["bytes"] for value in inventory.values()) > MAX_TOTAL_BYTES:
        raise ValueError("bundle payload bytes exceed bound")
    return name


def copy_exact(stage, name, source, expected, inventory, row):
    target = relative_path(stage, name)
    digest, size = hashlib.sha256(), 0
    with source.open("rb") as incoming, target.open("xb") as outgoing:
        for chunk in iter(lambda: incoming.read(1024 * 1024), b""):
            size += len(chunk)
            if size > MAX_FILE_BYTES:
                raise ValueError("exact artifact exceeds byte bound")
            digest.update(chunk)
            outgoing.write(chunk)
        outgoing.flush()
        os.fsync(outgoing.fileno())
    if digest.hexdigest() != expected:
        raise ValueError("source exact artifact changed while copying")
    inventory[name] = {"sha256": expected, "bytes": size, "kind": "exact", "row": row}
    if sum(value["bytes"] for value in inventory.values()) > MAX_TOTAL_BYTES:
        raise ValueError("bundle payload bytes exceed bound")
    return name


def convert_row(stage, report, row, number, mode, inventory):
    key = f"{number:03d}-{row['sourceSha256'][:12]}"
    mappings = roles(row)
    by_role = {role["role"]: role for role in mappings}
    required = exact_roles(row)
    exact, by_hash = {}, {}
    for selection, role_name in required.items():
        role = by_role[role_name]
        digest = role["sourceSha256"]
        if digest not in by_hash:
            source = relative_path(report, role["sourcePath"])
            suffix = source.suffix.lower()
            if not re.fullmatch(r"\.[a-z0-9]{1,8}", suffix):
                suffix = ".bin"
            name = f"photos/{number:03d}-e-{digest[:16]}{suffix}"
            by_hash[digest] = copy_exact(stage, name, source, digest, inventory, number)
        exact[selection] = {"role": role_name, "path": by_hash[digest], "sha256": digest}
    groups = {}
    for role in mappings:
        groups.setdefault(role["sourceSha256"], []).append(role)
    collage = None
    if mode == "collage":
        columns = min(8, math.ceil(math.sqrt(len(groups))))
        rows = math.ceil(len(groups) / columns)
        collage = Image.new("RGB", (columns * TILE[0], rows * TILE[1]), "#dddddd")
        if max(collage.size) > 4096:
            collage.close()
            raise ValueError("collage geometry exceeds JPEG bound")
    try:
        for index, (digest, aliases) in enumerate(groups.items()):
            source = relative_path(report, aliases[0]["sourcePath"])
            image = thumbnail(source, allow_invalid=(
                row["outcome"] == "unprocessable" and digest == row["sourceSha256"]))
            try:
                if mode == "compact":
                    name = f"photos/{number:03d}-h-{digest[:16]}.jpg"
                    add_payload(stage, name, jpeg(image), inventory, kind="lossy-history", row=number)
                    representation = {"path": name, "lossy": True}
                else:
                    x, y = (index % columns) * TILE[0], (index // columns) * TILE[1]
                    image.thumbnail((TILE[0] - 8, TILE[1] - 54), Image.Resampling.LANCZOS)
                    collage.paste(image, (x + (TILE[0] - image.width) // 2, y + 4))
                    label = ", ".join(role["role"] for role in aliases)
                    # The complete labels and source mappings remain below the
                    # image in HTML and in the manifest, not just clipped tiles.
                    label = label.encode("ascii", "replace").decode("ascii")
                    draw = ImageDraw.Draw(collage)
                    draw.text((x + 4, y + TILE[1] - 48),
                              f"Stage {index + 1} {digest[:10]}\n{label[:36]}\n{label[36:72]}",
                              fill="black")
                    representation = {"path": f"photos/{number:03d}-collage.jpg", "lossy": True,
                                      "tile": [x, y, TILE[0], TILE[1]], "stage": index + 1}
                for role in aliases:
                    role["history"] = dict(representation)
                    role["exactPath"] = by_hash.get(digest)
            finally:
                image.close()
        if collage is not None:
            add_payload(stage, f"photos/{number:03d}-collage.jpg", jpeg(collage), inventory,
                        kind="lossy-history", row=number)
    finally:
        if collage is not None:
            collage.close()
    return {"key": key, "source": row["source"], "sourceSha256": row["sourceSha256"],
            "photoId": row.get("photoId"), "sourceScope": row.get("sourceScope"),
            "outcome": row["outcome"], "selection": row["recommendation"]["use"],
            "exact": exact, "roles": mappings}


def statistics(data, inventory, source_inventory):
    kinds = collections.Counter(value["kind"] for value in inventory.values())
    return {
        "photos": len(data["photos"]),
        "roles": sum(len(row["roles"]) for row in data["photos"]),
        "roleCounts": dict(collections.Counter(
            role["role"] for row in data["photos"] for role in row["roles"])),
        "outcomeCounts": dict(collections.Counter(row["outcome"] for row in data["photos"])),
        "selectionCounts": dict(collections.Counter(row["selection"] for row in data["photos"])),
        "payloadFiles": len(inventory),
        "payloadBytes": sum(value["bytes"] for value in inventory.values()),
        "exactFiles": kinds["exact"],
        "historyFiles": kinds["lossy-history"],
        "sourceReportFiles": len(source_inventory),
        "sourceReportBytes": sum(value["bytes"] for value in source_inventory.values()),
    }


def report_html(data):
    escape = lambda value: html.escape(str(value), quote=True)
    lines = ["<!doctype html><meta charset='utf-8'><title>Preparation history experiment</title>",
             "<h1>Independent preparation history experiment</h1>",
             "<p><strong>LOSSY diagnostic preview/history, NOT exact workflow or recovery evidence.</strong> "
             "Exact original, selected native and selected padded files are linked separately. "
             "Alternative native stages and masks in history are reduced JPEGs, not recoverable originals. "
             "Source report kept; conversion is NOT pruning; dependency approval required.</p>",
             "<h2>Measured payload statistics and conversion/verification seconds</h2>",
             "<p>Payload figures count actual exact/history files. Persisted totals include "
             "manifest, HTML and receipt; independent --check also prints current verify timing.</p>",
             "<pre>" + escape(json.dumps({"statistics": data["statistics"],
                                           "persistedTotals": data["persistedTotals"],
                                           "timings": data["timings"]}, sort_keys=True, indent=2)) + "</pre>"]
    for row in data["photos"]:
        lines += ["<hr><h2>" + escape(row["source"]) + "</h2>",
                  "<p>Outcome: " + escape(row["outcome"]) + "; selection: " + escape(row["selection"]) + "</p>",
                  "<h3>Exact workflow/recovery evidence (not lossy)</h3>"]
        for selection, artifact in sorted(row["exact"].items()):
            lines.append(f'<p><a href="{escape(artifact["path"])}">{escape(selection)}</a> '
                         f'SHA-256 {escape(artifact["sha256"])}</p>')
        lines.append("<h3>LOSSY diagnostic history</h3>")
        shown = set()
        for role in row["roles"]:
            preview = role["history"]["path"]
            if preview not in shown:
                lines.append(f'<p><a href="{escape(preview)}"><img alt="LOSSY history" '
                             f'src="{escape(preview)}" style="max-width:100%"></a></p>')
                shown.add(preview)
            lines.append("<p>" + escape(role["role"]) + " | source " + escape(role["sourcePath"])
                         + " | canonical SHA-256 " + escape(role["sourceSha256"])
                         + (" | stage " + str(role["history"]["stage"]) if "stage" in role["history"] else "")
                         + "</p>")
    return "\n".join(lines).encode("utf-8")


def validate_bundle(data):
    if data["format"] != FORMAT or data["mode"] not in ("compact", "collage") or data["prune"] != PRUNE:
        raise ValueError("unsupported bundle format/mode/pruning receipt")
    source = data["sourceManifest"]
    preparation.validate(source)
    recorded = source_root(pathlib.Path(data["root"]), pathlib.Path(data["sourceReport"]),
                           source["root"], data["conversionConfiguration"])
    if data["sourceRoot"] != str(recorded) or not 1 <= len(source["photos"]) <= MAX_PHOTOS:
        raise ValueError("bundle provenance root/photo count mismatch")
    if len(data["photos"]) != len(source["photos"]):
        raise ValueError("bundle photo count mismatch")
    inventory, owners = data["payloads"], {}
    if len(inventory) > MAX_FILES or sum(p["bytes"] for p in inventory.values()) > MAX_TOTAL_BYTES:
        raise ValueError("bundle inventory exceeds bounds")
    for number, (row, original) in enumerate(zip(data["photos"], source["photos"]), 1):
        expected = roles(original)
        if (row["key"] != f"{number:03d}-{original['sourceSha256'][:12]}"
                or any(row.get(field) != original.get(field) for field in
                       ("source", "sourceSha256", "photoId", "sourceScope", "outcome"))
                or row["selection"] != original["recommendation"]["use"]
                or len(row["roles"]) != len(expected)):
            raise ValueError("row provenance mismatch")
        aliases, histories = {}, {}
        for role, canonical in zip(row["roles"], expected):
            if any(role.get(field) != value for field, value in canonical.items()):
                raise ValueError("role provenance mismatch")
            preview = role["history"]
            name = preview["path"]
            record = inventory[name]
            if (not preview["lossy"] or record["kind"] != "lossy-history"
                    or record["row"] != number):
                raise ValueError("invalid lossy history mapping")
            histories.setdefault(role["sourceSha256"], preview)
            if histories[role["sourceSha256"]] != preview:
                raise ValueError("equal artifacts have inconsistent history mappings")
            for path in (name, role.get("exactPath")):
                if path is not None:
                    if path in owners and owners[path] != number:
                        raise ValueError("cross-row pooling forbidden")
                    owners[path] = number
            if role.get("exactPath"):
                artifact = inventory[role["exactPath"]]
                if (artifact["sha256"] != role["sourceSha256"] or artifact["kind"] != "exact"
                        or artifact["row"] != number):
                    raise ValueError("exact role binding mismatch")
                aliases.setdefault(role["sourceSha256"], role["exactPath"])
                if aliases[role["sourceSha256"]] != role["exactPath"]:
                    raise ValueError("duplicate exact bytes within row")
        if set(row["exact"]) != set(exact_roles(original)):
            raise ValueError("missing exact selected evidence")
        by_role = {role["role"]: role for role in row["roles"]}
        for selection, role_name in exact_roles(original).items():
            artifact = row["exact"][selection]
            canonical = by_role[role_name]
            if (artifact["role"] != role_name or artifact["path"] != canonical["exactPath"]
                    or artifact["sha256"] != canonical["sourceSha256"]):
                raise ValueError("exact selection mismatch")
        unique_paths = {preview["path"] for preview in histories.values()}
        if len(unique_paths) != (len(histories) if data["mode"] == "compact" else 1):
            raise ValueError("history mode payload count mismatch")
    if set(owners) != set(inventory):
        raise ValueError("unreferenced bundle payloads")
    if data["statistics"] != statistics(data, inventory, data["sourceInventory"]):
        raise ValueError("bundle statistics mismatch")
    if digest_bytes(encoded(source)) != data["sourceManifestCanonicalSha256"]:
        raise ValueError("source manifest provenance digest mismatch")


def check(root, output, *, expected_report=None, expected_mode=None, binding_output=None):
    started = time.perf_counter()
    actual = tree(output)
    if any(path.is_dir() and path != output / "photos" for path in output.rglob("*")):
        raise ValueError("bundle must use the fixed shallow photos layout")
    receipt = read_json(relative_path(output, "receipt.json"))
    data = read_json(relative_path(output, "manifest.json"))
    location = binding_output or output
    if (receipt["format"] != FORMAT or receipt["root"] != str(root)
            or receipt["output"] != str(location) or receipt["prune"] != PRUNE):
        raise ValueError("stale/mismatched bundle receipt")
    if (data["root"] != str(root) or data["output"] != str(location)
            or receipt["manifest"] != actual["manifest.json"]
            or receipt["html"] != actual["index.html"]):
        raise ValueError("bundle manifest/HTML hash or location mismatch")
    if expected_report is not None and data["sourceReport"] != str(expected_report):
        raise ValueError("existing bundle has a different source report")
    if expected_mode is not None and data["mode"] != expected_mode:
        raise ValueError("existing bundle has a different mode")
    validate_bundle(data)
    expected_names = set(data["payloads"]) | {"manifest.json", "receipt.json", "index.html"}
    if set(actual) != expected_names:
        raise ValueError("bundle membership mismatch")
    for name, record in data["payloads"].items():
        if actual[name] != {"sha256": record["sha256"], "bytes": record["bytes"]}:
            raise ValueError(f"bundle payload changed: {name}")
        if record["kind"] == "lossy-history":
            with Image.open(relative_path(output, name)) as image:
                if image.format != "JPEG" or max(image.size) > 4096 or image.width * image.height > 16777216:
                    raise ValueError("invalid bounded history JPEG")
                image.verify()
    if report_html(data) != relative_path(output, "index.html").read_bytes():
        raise ValueError("HTML no longer represents bundle")
    if data["persistedTotals"] != {
            "actualFiles": len(actual), "actualBytes": sum(p["bytes"] for p in actual.values())}:
        raise ValueError("persisted file/byte totals mismatch")
    result = {"actualFiles": len(actual), "actualBytes": sum(p["bytes"] for p in actual.values()),
              "verifySeconds": round(time.perf_counter() - started, 6), **data["statistics"]}
    return data, result


def publish(root, report, output, mode):
    if output.exists():
        data, result = check(root, output, expected_report=report, expected_mode=mode)
        source, inventory = source_report(root, report)
        if inventory != data["sourceInventory"] or source != data["sourceManifest"]:
            raise ValueError("source report changed since existing bundle; choose a new --out")
        return result
    started = time.perf_counter()
    source, source_inventory = source_report(root, report)
    verified = time.perf_counter()
    cfg = preparation.cw.load_cfg()
    output.parent.mkdir(parents=True, exist_ok=True)
    with temporary_storage.staging_directory(output.parent, ".history-bundle-") as stage:
        (stage / "photos").mkdir()
        inventory = {}
        rows = [convert_row(stage, report, row, number, mode, inventory)
                for number, row in enumerate(source["photos"], 1)]
        converted = time.perf_counter()
        # Re-hash all source members immediately before sealing publication.
        if tree(report) != source_inventory:
            raise ValueError("source report changed during conversion")
        rechecked = time.perf_counter()
        data = {
            "format": FORMAT, "root": str(root), "output": str(output), "sourceReport": str(report),
            "sourceRoot": source["root"],
            "mode": mode, "prune": dict(PRUNE),
            "sourceManifest": source, "sourceManifestCanonicalSha256": digest_bytes(encoded(source)),
            "sourceInventory": source_inventory,
            "configurationReceipt": preparation.cw.storage_configuration_receipt(
                cfg, root, {"historySourceReport": report, "historyBundleOutput": output}),
            "conversionConfiguration": cfg,
            "historyEncoding": {"pillow": Image.__version__, "format": "JPEG", "quality": 78,
                                "compactEdge": COMPACT_EDGE, "collageTile": list(TILE),
                                "lossy": True, "exactProcessingRecipeChanged": False},
            "photos": rows, "payloads": inventory,
            "timings": {"sourceVerifySeconds": round(verified - started, 6),
                        "conversionSeconds": round(converted - verified, 6),
                        "finalSourceRecheckSeconds": round(rechecked - converted, 6)},
        }
        data["statistics"] = statistics(data, inventory, source_inventory)
        validate_bundle(data)
        payload_started = time.perf_counter()
        actual = tree(stage)
        if actual != {name: {"sha256": record["sha256"], "bytes": record["bytes"]}
                      for name, record in inventory.items()}:
            raise ValueError("staged payload verification failed")
        data["timings"]["payloadVerifySeconds"] = round(time.perf_counter() - payload_started, 6)
        data["persistedTotals"] = {"actualFiles": len(inventory) + 3, "actualBytes": 0}
        for _ in range(12):
            manifest, page = encoded(data), report_html(data)
            receipt = encoded({
                "format": FORMAT, "root": str(root), "output": str(output),
                "manifest": {"sha256": digest_bytes(manifest), "bytes": len(manifest)},
                "html": {"sha256": digest_bytes(page), "bytes": len(page)},
                "prune": dict(PRUNE),
            })
            total = data["statistics"]["payloadBytes"] + len(manifest) + len(page) + len(receipt)
            if total == data["persistedTotals"]["actualBytes"]:
                break
            data["persistedTotals"]["actualBytes"] = total
        else:
            raise ValueError("could not seal stable actual byte counts")
        if len(manifest) > MAX_JSON_BYTES or total > MAX_TOTAL_BYTES:
            raise ValueError("bundle manifest/total bytes exceed bound")
        write(stage / "manifest.json", manifest)
        write(stage / "index.html", page)
        write(stage / "receipt.json", receipt)
        result = check(root, stage, binding_output=output,
                       expected_report=report, expected_mode=mode)[1]
        # A source change while sealing must not publish a stale conversion.
        if tree(report) != source_inventory:
            raise ValueError("source report changed before atomic publication")
        safe(root, output)
        if output.exists():
            raise ValueError("output appeared concurrently; refusing overwrite")
        stage.rename(output)
    return result


def locations(root, report, output):
    root, output = pathlib.Path(root).expanduser(), pathlib.Path(output).expanduser()
    if not root.is_absolute() or not root.is_dir():
        raise ValueError("--root must be an existing absolute sandbox Working root")
    if not preparation.sandbox.is_sandbox_working_path(root):
        raise ValueError("history experiment requires a sandbox Working root")
    safe(root, output)
    cfg = preparation.cw.load_cfg()
    base = preparation.cw.storage_root(cfg, "reports", root=root) / "preparation-history"
    if output.parent != base or output.name.startswith("."):
        raise ValueError("--out must be a named run directly under configured reports\\preparation-history")
    if report is not None:
        report = pathlib.Path(report).expanduser()
        safe(root, report)
        if not report.is_dir() or output == report or report in output.parents or output in report.parents:
            raise ValueError("source report and bundle must be separate, existing/new independent directories")
    return root, report, output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="absolute sandbox Working root")
    parser.add_argument("--report", help="absolute verified FULL/LEAN preparation report; not needed by --check")
    parser.add_argument("--out", required=True, help="absolute configured reports\\preparation-history\\NEW")
    parser.add_argument("--mode", choices=("compact", "collage"), default=None)
    flags = parser.add_mutually_exclusive_group()
    flags.add_argument("--dry-run", action="store_true", help="read-only preview (default)")
    flags.add_argument("--apply", action="store_true", help="publish a new independent bundle; never prune")
    flags.add_argument("--check", action="store_true", help="verify persisted bundle independently of source report")
    args = parser.parse_args(argv)
    try:
        root, report, output = locations(args.root, args.report, args.out)
        if args.check:
            result = check(root, output, expected_report=report, expected_mode=args.mode)[1]
        else:
            if report is None:
                raise ValueError("--report is required for preview/apply")
            mode = args.mode or "compact"
            if args.apply:
                result = publish(root, report, output, mode)
            else:
                started = time.perf_counter()
                data, inventory = source_report(root, report)
                result = {
                    "preview": True, "mode": mode, "photos": len(data["photos"]),
                    "sourceFiles": len(inventory), "sourceBytes": sum(p["bytes"] for p in inventory.values()),
                    "roles": sum(len(roles(row)) for row in data["photos"]),
                    "uniqueArtifactsWithinRows": sum(len({r["sourceSha256"] for r in roles(row)})
                                                     for row in data["photos"]),
                    "sourceVerifySeconds": round(time.perf_counter() - started, 6),
                    "note": "No writes. Output bytes/counts measured only after conversion.",
                }
                if output.exists():
                    check(root, output, expected_report=report, expected_mode=mode)
        print(json.dumps({"result": result, "prune": PRUNE}, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, IndexError, AssertionError,
            preparation.ValidationError, Image.DecompressionBombError) as error:
        print(f"Preparation history refused: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
