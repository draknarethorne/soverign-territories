"""Owned, content-verified standard photo derivatives; never infer ownership by suffix."""
import hashlib
import io
import json
import math
import os
import pathlib
import time

from PIL import Image, ImageOps

import originals
from . import retained_preparation, verification_reads
from likeness_library.thumbnails import crop_thumbnail

SIZE = (944, 1104)
RECIPE = "standard-padded-head-chest-v1"
MANIFEST = ".photo-derivatives.json"
KINDS = {"padded": "full", "head": "head", "chest": "chest"}


def digest(path):
    return verification_reads.sha256(path)


def manifest_path(folder):
    """<person>/944x1104/.photo-derivatives.json; its keys stay relative to the person folder."""
    return originals.cw.derivative_root(folder, SIZE) / MANIFEST


def manifest_owner(manifest):
    """The person folder a manifest belongs to (the legacy layout kept it in the person folder itself)."""
    manifest = pathlib.Path(manifest)
    root = originals.cw.derivative_root(manifest.parent.parent, SIZE)
    return manifest.parent.parent if manifest.parent.name == root.name else manifest.parent


def load(folder):
    path = manifest_path(folder)
    reads = verification_reads.active()
    if reads is not None and path.exists():
        return reads.document(path, 64 * 1024 * 1024)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"entries": {}}


def save(folder, data):
    path = manifest_path(folder)
    verification_reads.before_write(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    stage = path.with_suffix(".json.pending")
    stage.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    try:
        for attempt in range(6):
            try:
                os.replace(stage, path)
                break
            except PermissionError:
                if attempt == 5:
                    raise
                time.sleep(0.05 * (attempt + 1))
    finally:
        if stage.exists():
            stage.unlink()
    if verification_reads.active() is not None:
        verification_reads.document(path, 64 * 1024 * 1024)


def relative_target(source, framing):
    """<W>x<H>/<kind>/<stem>[_head|_chest]_<W>x<H>.png, under <W>x<H>/review/ for a Review photo."""
    source = pathlib.Path(source)
    directory = originals.cw.derivative_dir(
        pathlib.Path(), KINDS[framing], SIZE, review=source.parent.name != "gallery")
    suffix = "" if framing == "padded" else f"_{framing}"
    return directory / f"{source.stem}{suffix}_{SIZE[0]}x{SIZE[1]}.png"


def legacy_key(key):
    """The current manifest key for a key written under the former <prefix>_944x1104 folders (None when not one)."""
    parts = pathlib.PurePosixPath(key).parts
    for old, new in originals.cw.legacy_derivative_dirs(pathlib.Path(), SIZE):
        if len(parts) == 2 and parts[0] == old.name:
            return (pathlib.PurePosixPath(new.as_posix()) / parts[1]).as_posix()
    return None


def verified(source, framing, box=None):
    source = pathlib.Path(source)
    folder = source.parent.parent
    key = relative_target(source, framing).as_posix()
    record = load(folder)["entries"].get(key)
    target = folder / key
    if not record or not target.is_file():
        raise ValueError(f"Missing maintained {framing}: {source}; run bin\\people-gallery.cmd --apply")
    if framing != "padded" and box is None:
        raise ValueError(f"Unavailable {framing}: {source}; no usable cached face")
    if (record.get("recipe") != RECIPE or record.get("source") != source.relative_to(folder).as_posix()
            or record.get("sourceSha256") != digest(source) or record.get("sha256") != digest(target)
            or record.get("sourcePrepared", False) != retained_preparation.source_is_prepared(source)
            or (framing != "padded" and box is not None and record.get("box") != list(box))):
        raise ValueError(f"Stale or edited maintained {framing}: {target}; run maintenance")
    return target, record


def render(source, framing, box):
    """Deterministic bytes shared by maintenance, omission proof and recovery."""
    prepared = retained_preparation.source_is_prepared(source)
    return render_pixels(source, framing, box, prepared=prepared)


def render_pixels(source, framing, box, *, prepared):
    """Render pixels; prepared=True requires independently verified retained lineage."""
    output = io.BytesIO()
    if framing == "padded":
        originals.fit(source, output, SIZE, box, cleanup=not prepared)
    elif framing == "head":
        if not box or not originals.headshot(source, output, SIZE, box, cleanup=not prepared):
            raise ValueError(f"head cannot be reproduced: {source}")
    elif framing == "chest":
        if not box:
            raise ValueError(f"chest cannot be reproduced: {source}")
        with Image.open(source) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
            import screens
            if not prepared and screens.is_reel_ui(image):
                if not screens.head_clear(box):
                    raise ValueError(f"face under screenshot UI: {source}")
                x0, y0, x1, y1 = screens.clean_box(image.size)
                width, height = image.size
                box = [(box[0] * width - x0) / (x1 - x0), (box[1] * height - y0) / (y1 - y0),
                       box[2] * width / (x1 - x0), box[3] * height / (y1 - y0)]
                image = image.crop((x0, y0, x1, y1))
            crop_thumbnail(image, box, "chest", SIZE).save(output, format="PNG")
    else:
        raise ValueError(f"unknown derivative framing: {framing}")
    return output.getvalue()


def expected_unavailability(source, framing, box, px, faces):
    """Explain only known policy exclusions; malformed or unreadable cache data stays actionable."""
    if framing not in ("head", "chest"):
        return None
    valid_box = (
        isinstance(box, (list, tuple)) and len(box) == 4
        and all(isinstance(value, (int, float)) and math.isfinite(value) for value in box)
        and box[2] > 0 and box[3] > 0
    )
    if faces == 0 and not box and px == 0:
        return "no face detected; head/chest framing intentionally unavailable"
    if faces and faces > 0 and valid_box and isinstance(px, (int, float)) and px < originals.MIN_FACE_PX:
        return (f"detected face is {px:g}px, below the {originals.MIN_FACE_PX}px "
                "minimum; head/chest framing intentionally unavailable")
    if framing != "head" or not valid_box or not isinstance(px, (int, float)) or px < originals.MIN_FACE_PX:
        return None
    try:
        with Image.open(source) as image:
            image = ImageOps.exif_transpose(image).convert("RGB")
        if not retained_preparation.source_is_prepared(source):
            import screens
            if screens.is_reel_ui(image):
                if not screens.head_clear(box):
                    return None
                x0, y0, x1, y1 = screens.clean_box(image.size)
                width, height = image.size
                box = [(box[0] * width - x0) / (x1 - x0), (box[1] * height - y0) / (y1 - y0),
                       box[2] * width / (x1 - x0), box[3] * height / (y1 - y0)]
                image = image.crop((x0, y0, x1, y1))
        crop = originals.headshot_box(image.size, box, SIZE)
    except (OSError, ValueError, ZeroDivisionError):
        return None
    crop_height = crop[3] - crop[1]
    minimum = SIZE[1] * 0.3
    if crop_height < minimum:
        return (f"head crop is {crop_height}px high, below the {minimum:.1f}px minimum; "
                "head framing intentionally unavailable")
    return None


def _has_owned_framing(source, framing, data):
    relative = relative_target(source, framing)
    return (relative.as_posix() in data["entries"] or (pathlib.Path(source).parent.parent / relative).exists())


def maintain(source, box, px, *, apply=False, faces=None):
    source = pathlib.Path(source)
    folder = source.parent.parent
    data = load(folder)
    changes, diagnostics = [], []
    for framing in ("padded", "head", "chest"):
        relative = relative_target(source, framing)
        target = folder / relative
        if framing != "padded" and (not box or px < originals.MIN_FACE_PX):
            if _has_owned_framing(source, framing, data):
                diagnostics.append(f"Stale maintained {framing} remains although current face policy excludes it: {target}")
            else:
                reason = expected_unavailability(source, framing, box, px, faces)
                if reason:
                    diagnostics.append(f"INFO: {source}: {reason}")
                else:
                    diagnostics.append(f"{source}: {framing} unavailable (no usable cached face)")
            continue
        try:
            verified(source, framing, box)
            continue
        except ValueError:
            pass
        previous = data["entries"].get(relative.as_posix())
        try:
            payload = render(source, framing, box)
        except ValueError as exc:
            reason = expected_unavailability(source, framing, box, px, faces)
            if reason and not _has_owned_framing(source, framing, data):
                diagnostics.append(f"INFO: {source}: {reason}")
            else:
                diagnostics.append(str(exc))
            continue
        expected = hashlib.sha256(payload).hexdigest()
        if target.exists() and (not previous or previous.get("sha256") != digest(target)):
            if digest(target) != expected:
                diagnostics.append(f"Preserved unowned/edited asset: {target}")
                continue
        changes.append(str(target))
        if not apply:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        stage = target.with_name(target.name + ".pending")
        try:
            if not target.exists() or digest(target) != expected:
                verification_reads.before_write(target)
                stage.write_bytes(payload)
                os.replace(stage, target)
            data["entries"][relative.as_posix()] = {
                "source": source.relative_to(folder).as_posix(), "sourceSha256": digest(source),
                "sha256": digest(target), "box": list(box) if box else None, "recipe": RECIPE,
                "sourcePrepared": retained_preparation.source_is_prepared(source),
            }
            save(folder, data)
        finally:
            if stage.exists():
                stage.unlink()
    return changes, diagnostics


def thumbnail_key(source, framing, box=None):
    target, record = verified(source, framing, box)
    key = hashlib.sha256((RECIPE + record["sha256"]).encode()).hexdigest()[:12]
    return target, key


def thumbnail(source, framing, box=None, size=(320, 400), *, px=None, faces=None):
    """Return only a resized derivative, or a visibly diagnostic placeholder."""
    import io
    from PIL import ImageDraw
    diagnostic = None
    try:
        target, key = thumbnail_key(source, framing, box)
        with Image.open(target) as image:
            image = image.convert("RGB").resize(size, Image.Resampling.LANCZOS)
    except (OSError, ValueError, KeyError) as exc:
        reason = expected_unavailability(source, framing, box, px, faces)
        target = pathlib.Path(source).parent.parent / relative_target(source, framing)
        try:
            entry = load(pathlib.Path(source).parent.parent)["entries"].get(
                relative_target(source, framing).as_posix()
            )
        except (OSError, ValueError, KeyError):
            entry = True
        diagnostic = (f"INFO: {reason}" if reason and not entry and not target.exists() else str(exc))
        key = hashlib.sha256(diagnostic.encode()).hexdigest()[:12]
        image = Image.new("RGB", size, (245, 230, 215))
        notice = ("Intentional framing exclusion" if diagnostic.startswith("INFO: ")
                  else "Run gallery maintenance")
        ImageDraw.Draw(image).text((8, 12), f"{framing}: unavailable\n{notice}", fill="black")
    output = io.BytesIO()
    image.save(output, "JPEG", quality=84)
    return output.getvalue(), key, diagnostic


def prune(folder, work, *, apply=False, protected_names=()):
    """Archive only obsolete outputs still matching their exact ownership hash."""
    folder, work = pathlib.Path(folder), pathlib.Path(work)
    data = load(folder)
    changes, diagnostics = [], []
    for relative, record in list(data["entries"].items()):
        source = (folder / record["source"]).resolve()
        target = (folder / relative).resolve()
        if folder.resolve() not in source.parents or folder.resolve() not in target.parents:
            raise ValueError(f"Unsafe derivative manifest path in {folder}")
        expected_paths = {relative_target(source, framing).as_posix()
                          for framing in ("padded", "head", "chest")}
        if (record.get("recipe") != RECIPE or source.parent.name not in {"gallery", "review"}
                or relative not in expected_paths):
            diagnostics.append(f"Preserved unrecognized manifest entry: {target}")
            continue
        if source.exists() or not target.exists():
            continue
        if target.name.casefold() in protected_names:
            diagnostics.append(f"Preserved workflow-selected derivative: {target}")
            continue
        if digest(target) != record.get("sha256"):
            diagnostics.append(f"Preserved edited orphan: {target}")
            continue
        changes.append(str(target))
        if apply:
            destination = work / "_archive" / folder.relative_to(work) / relative
            if destination.exists():
                destination = destination.with_name(destination.stem + "_" + record["sha256"][:12] + destination.suffix)
            if destination.exists():
                diagnostics.append(f"Archive collision; retained {target}")
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(target, destination)
            del data["entries"][relative]
            save(folder, data)
    return changes, diagnostics
