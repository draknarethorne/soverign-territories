"""One resumable preparation stage for an immutable sandbox rebuild."""
import json
import pathlib
import shutil

from . import metadata, sandbox


def inventory(layout):
    import image_preparation

    source = layout["source_root"]
    paths = image_preparation.inventory(source)
    rows = {}
    for path in paths:
        relative = path.relative_to(source).as_posix()
        expected = layout["manifest_files"].get(relative)
        if not expected or metadata.content_sha256(path) != expected[1]:
            raise ValueError(f"preparation input is not in the immutable snapshot: {relative}")
        rows[relative] = expected[1]
    if not rows:
        raise ValueError("no immutable Gallery/Review inputs to prepare")
    return rows


def prepare(layout, run):
    """Copy inputs once, then use the ordinary preparation runner without live writes."""
    import image_preparation

    run = pathlib.Path(run)
    receipt = run / "intake.json"
    if receipt.exists():
        return verify(layout, run)
    mirror = run / "inputs"
    if mirror.exists():
        raise ValueError("unfinished intake staging exists; inspect it and use a new run")
    rows = inventory(layout)
    mirror.mkdir(parents=True)
    for relative, expected in rows.items():
        target = mirror.joinpath(*pathlib.PurePosixPath(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(layout["source_root"] / relative, target)
        if metadata.content_sha256(target) != expected:
            raise OSError(f"intake staging checksum mismatch: {relative}")
    output = mirror / "_reports" / "preparation" / "all"
    paths = [mirror / relative for relative in rows]
    result = image_preparation.publish(mirror, output, paths)
    data = image_preparation.verify(mirror, output)
    value = {
        "schemaVersion": 1, "sourceManifestSHA256": metadata.content_sha256(
            layout["sandbox_root"] / "source-manifest.json"),
        "inputs": rows, "preparationManifestSHA256": metadata.content_sha256(output / "manifest.json"),
        "recipe": data["recipe"], "assessmentErrors": bool(result),
    }
    metadata.report_assets.replace_file(
        _stage_json(receipt, value), receipt,
    )
    return verify(layout, run)


def _stage_json(target, value):
    stage = target.with_suffix(".tmp")
    with stage.open("x", encoding="utf-8") as output:
        json.dump(value, output, indent=2)
        output.write("\n")
    return stage


def verify(layout, run):
    import image_preparation

    run = pathlib.Path(run)
    receipt = run / "intake.json"
    for path in (receipt, *receipt.parents):
        if sandbox._is_reparse_point(path):
            raise ValueError(f"linked intake receipt: {path}")
        if path == layout["working_root"]:
            break
    value = json.loads(receipt.read_text(encoding="utf-8"))
    if value.get("schemaVersion") != 1 or value.get("inputs") != inventory(layout):
        raise ValueError("intake input inventory changed; choose a new run")
    if value["sourceManifestSHA256"] != metadata.content_sha256(
        layout["sandbox_root"] / "source-manifest.json"
    ):
        raise ValueError("immutable source manifest changed since intake")
    mirror = run / "inputs"
    output = mirror / "_reports" / "preparation" / "all"
    if metadata.content_sha256(output / "manifest.json") != value["preparationManifestSHA256"]:
        raise ValueError("intake manifest changed since preparation")
    data = image_preparation.verify(mirror, output)
    actual = {row["source"]: row["sourceSha256"] for row in data["photos"]}
    if actual != value["inputs"] or len(actual) != len(data["photos"]):
        raise ValueError("intake did not account for every supplied image exactly once")
    if data["recipe"] != value["recipe"]:
        raise ValueError("intake recipe receipt mismatch")
    return output, data


def selected_path(output, row):
    """Unusable assessments retain the original; no invented clean-image fallback."""
    selected = row.get("recommendation", {}).get("use", "none")
    if selected in ("original", "none"):
        relative, expected = row["retained"], row["sourceSha256"]
    else:
        variant = row["variants"].get(selected)
        if not variant:
            raise ValueError(f"recommended preparation output is missing: {row['source']}")
        relative, expected = variant["path"], variant["sha256"]
    path = pathlib.Path(output).joinpath(*sandbox._safe_source_path(relative))
    import image_preparation

    image_preparation.safe_path(pathlib.Path(output), path)
    if metadata.content_sha256(path) != expected:
        raise ValueError(f"selected preparation bytes changed: {path}")
    return path
