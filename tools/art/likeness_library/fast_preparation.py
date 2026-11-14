"""Original-byte intake for likeness-first sandbox tests; no image products."""
import html
import hashlib
import json
import pathlib
import shutil
from urllib.parse import quote

from . import metadata, sandbox

RECIPE = {"id": "likeness-originals-fast-v1", "editing": "deferred", "derivatives": "deferred"}
HEADER = (
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>FAST original-byte intake</title>'
    '<style>img{max-width:100%;max-height:70vh}li{margin-bottom:2em}body{overflow-wrap:anywhere}</style>'
    '</head><body>'
)


def _image_link(href, name, *, readable):
    image = (
        f'<img loading="lazy" src="{href}" alt="{html.escape(name, quote=True)}" '
        'onerror="this.hidden=true;this.parentElement.append(\'Image unavailable; use the filename link.\')">'
        if readable else '<span>Image cannot be decoded; original retained for inspection.</span>'
    )
    return f'<a href="{href}">{image}<br>{html.escape(name)}</a>'


def _checked(root, relative, expected=None):
    root = pathlib.Path(root)
    parts = sandbox._safe_source_path(relative)
    path = root.joinpath(*parts)
    for candidate in (root, *[root.joinpath(*parts[:i]) for i in range(1, len(parts)+1)]):
        if sandbox._is_reparse_point(candidate):
            raise ValueError(f"linked FAST input: {candidate}")
    if expected is not None and metadata.content_sha256(path) != expected:
        raise ValueError(f"FAST input changed: {relative}")
    return path


def publish(mirror, output, inputs, storage_mode):
    import image_preparation

    mirror, output = pathlib.Path(mirror), pathlib.Path(output)
    image_preparation.safe_path(mirror, output)
    if storage_mode not in ("lean", "full"):
        raise ValueError("FAST storage must be lean or full")
    if output.exists():
        return verify(mirror, output, inputs, storage_mode)
    stage = output.with_name(output.name + ".partial")
    image_preparation.safe_path(mirror, stage)
    if stage.exists():
        # Only a complete, verified stage may resume; partial evidence stays intact.
        verify(mirror, stage, inputs, storage_mode)
        metadata.report_assets.rename_directory(stage, output)
        return verify(mirror, output, inputs, storage_mode)
    stage.mkdir(parents=True, exist_ok=False)
    photos = []
    for relative, expected in sorted(inputs.items()):
        source = _checked(mirror, relative, expected)
        retained = f"originals/{expected}{source.suffix.lower()}"
        original = _checked(stage, retained)
        if not original.exists():
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, original)
        _checked(stage, retained, expected)
        parts = pathlib.PurePosixPath(relative).parts
        row = {
            "source": relative, "photoId": metadata.photo_id_from_name(source.name),
            "sourceSha256": expected, "retained": retained, "variants": {},
            "processingProfile": "fast", "sourceTreatment": "original-unassessed",
            "outcome": "analysis-only", "recommendation": {"use": "original"},
            "processing": {"final": "original", "cleanup": "original", "steps": []},
            "sourceScope": {
                "category": parts[0], "artist": parts[1] if parts[0] == "Artists" else None,
                "matchingDomain": "/".join(parts[:2]) if parts[0] == "Artists" else "general",
                "reason": "Original source domain preserved; FAST does not reassign artist scope.",
            },
            "diagnostics": [
                "FAST: image editing, composition, cleanup and 944x1104 outputs deferred.",
                "Decoding only at intake; face quality and likeness are assessed by the matching stage.",
            ],
        }
        try:
            image = image_preparation.decode_file(source)
            row["size"] = list(image.size)
            image.close()
        except (OSError, ValueError, image_preparation.Image.DecompressionBombError,
                image_preparation.ImageCms.PyCMSError) as exc:
            row["outcome"] = "unprocessable"
            row["diagnostics"].append(f"Decode failed; source retained without derivatives: {exc}")
        token = expected
        detail = f"details/{token[:16]}-{hashlib.sha256(relative.encode()).hexdigest()[:16]}.html"
        detail_path = stage / pathlib.PurePosixPath(detail)
        detail_path.parent.mkdir(parents=True, exist_ok=True)
        image_href = quote("../" + retained)
        detail_path.write_text(
            HEADER + '<h1>FAST original-byte intake</h1>'
            '<p>Image editing and 944x1104 generation deferred; not a clean-image certification.</p>'
            '<p>' + html.escape(relative) + '</p><p>' + html.escape("; ".join(row["diagnostics"])) + '</p>'
            + _image_link(image_href, source.name, readable=row["outcome"] != "unprocessable")
            + '</body></html>', encoding="utf-8",
        )
        row.update(detail=detail, detailSha256=metadata.content_sha256(detail_path))
        photos.append(row)
    data = {
        "kind": "fast-original-intake", "schemaVersion": 1, "recipe": RECIPE,
        "processingProfile": "fast", "storageMode": storage_mode, "photos": photos,
        "implementationSHA256": metadata.content_sha256(pathlib.Path(__file__)),
    }
    (stage / "index.html").write_text(
        HEADER + '<h1>FAST intake: originals only</h1>'
        '<p>Editing and 944x1104 generation are deferred. Matching has not been run.</p><ul>'
        + "".join('<li><a href="' + quote(row["detail"]) + '">' + html.escape(row["source"])
                  + '</a> - ' + html.escape(row["outcome"]) + '<br>'
                  + _image_link(quote(row["retained"]), pathlib.PurePosixPath(row["source"]).name,
                                readable=row["outcome"] != "unprocessable")
                  + '</li>' for row in photos) + '</ul></body></html>',
        encoding="utf-8",
    )
    data["indexSHA256"] = metadata.content_sha256(stage / "index.html")
    (stage / "manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    verify(mirror, stage, inputs, storage_mode)
    metadata.report_assets.rename_directory(stage, output)
    return verify(mirror, output, inputs, storage_mode)


def verify(mirror, output, inputs, storage_mode=None):
    import image_preparation

    output = pathlib.Path(output)
    image_preparation.safe_path(pathlib.Path(mirror), output)
    data = json.loads(_checked(output, "manifest.json").read_text(encoding="utf-8"))
    if (data.get("kind") != "fast-original-intake" or data.get("schemaVersion") != 1
            or data.get("recipe") != RECIPE or data.get("processingProfile") != "fast"
            or data.get("storageMode") not in ("lean", "full")
            or storage_mode is not None and data["storageMode"] != storage_mode
            or data.get("implementationSHA256") != metadata.content_sha256(pathlib.Path(__file__))):
        raise ValueError("FAST recipe/profile/storage/implementation changed; use a new run")
    actual = {}
    artifacts = {"manifest.json", "index.html"}
    _checked(output, "index.html", data["indexSHA256"])
    for row in data["photos"]:
        relative, expected = row["source"], row["sourceSha256"]
        if relative in actual or inputs.get(relative) != expected:
            raise ValueError("FAST intake inventory differs")
        actual[relative] = expected
        if (row["processingProfile"] != "fast" or row["variants"] or row.get("recommendedPadded")
                or row["recommendation"] != {"use": "original"}
                or row["processing"] != {"final": "original", "cleanup": "original", "steps": []}
                or row["outcome"] not in ("analysis-only", "unprocessable")
                or row["sourceTreatment"] != "original-unassessed"):
            raise ValueError("FAST intake cannot claim edited/prepared image products")
        parts = pathlib.PurePosixPath(relative).parts
        scope = row["sourceScope"]
        if (scope["category"] != parts[0]
                or scope["artist"] != (parts[1] if parts[0] == "Artists" else None)
                or scope["matchingDomain"] != ("/".join(parts[:2]) if parts[0] == "Artists" else "general")
                or not scope["reason"]):
            raise ValueError("FAST source domain differs")
        _checked(mirror, relative, expected)
        _checked(output, row["retained"], expected)
        _checked(output, row["detail"], row["detailSha256"])
        artifacts.update((row["retained"], row["detail"]))
    if actual != inputs:
        raise ValueError("FAST intake did not conserve every original")
    found = set()
    for path in output.rglob("*"):
        relative = path.relative_to(output).as_posix()
        _checked(output, relative)
        if path.is_file():
            found.add(relative)
    if found != artifacts:
        raise ValueError("FAST artifact inventory differs; unexpected or missing image products")
    return data


def deferred(photo):
    """Only verified original-byte lineage authorizes missing derivatives."""
    from . import retained_preparation

    native = pathlib.Path(photo).absolute()
    root = retained_preparation._library_root(native)
    if root is None:
        return False
    link = retained_preparation.verify_link(root, native)
    if link is None:
        # Retained lineage claims must fail closed even when their checksum is stale.
        retained_preparation.source_is_prepared(native)
        return False
    if link["row"].get("processingProfile") != "fast":
        return False
    if (link["recipe"] != RECIPE or link["selected"] != "original"
            or link["currentSha256"] != link["sourceSha256"]):
        raise ValueError(f"FAST original-byte lineage differs: {native}")
    return True
