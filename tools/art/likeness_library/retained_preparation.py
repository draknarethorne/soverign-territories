"""Bounded, destination-owned preparation evidence; never infer continuity by name."""
import hashlib
import html
import json
import os
import pathlib
import re
import stat
import sys
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.workflows import comfy_workflows as cw  # noqa: E402

from . import metadata, verification_reads


MAX_MANIFEST_BYTES = 8 * 1024 * 1024
MAX_ARTIFACTS = 256
MAX_SETS = 5000
MANIFEST = "manifest.json"


def _safe(root, relative):
    reads = verification_reads.active()
    return reads.safe_path(root, relative, _safe_uncached) if reads is not None else _safe_uncached(root, relative)


def _safe_uncached(root, relative):
    root = pathlib.Path(root).absolute()
    value = str(relative)
    parts = pathlib.PurePosixPath(value).parts
    if (not parts or "\\" in value or ":" in value or value.startswith("/")
            or any(part in ("", ".", "..") for part in value.split("/"))):
        raise ValueError(f"unsafe retained preparation path: {value}")
    target = root.joinpath(*parts)
    for path in (root, *[root.joinpath(*parts[:i]) for i in range(1, len(parts) + 1)]):
        if path.exists() or path.is_symlink():
            info = path.lstat()
            if path.is_symlink() or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise ValueError(f"linked retained preparation path: {path}")
    if target.resolve() != target:
        raise ValueError(f"reparse point in retained preparation path: {target}")
    return target


def _digest(path):
    return verification_reads.sha256(path)


def _storage_prefix(root, name, cfg=None):
    config = cfg if cfg is not None else cw.load_cfg()
    root = pathlib.Path(root).resolve()
    return cw.storage_root(config, name, root=root).relative_to(root).parts


def _domain(relative, root=None, cfg=None):
    parts = pathlib.PurePosixPath(relative).parts
    categories = {"Angels", "Sisters", "Models", "Prospects", "Potentials", "Artists", "Various"}
    # Configured operational roots cannot overlap a native photo category.
    if not parts or parts[0] not in categories:
        config = cfg if cfg is not None else cw.load_cfg()
        root = pathlib.Path(root) if root is not None else cw.work_root(config)
        junk = _storage_prefix(root, "junk", config)
        retired = _storage_prefix(root, "retired", config)
        if parts[:len(junk)] == junk:
            parts = parts[len(junk):]
        elif parts[:len(retired) + 1] == (*retired, "photos"):
            parts = parts[len(retired) + 1:]
    if not parts or parts[0] not in categories:
        raise ValueError("unsupported retained preparation owner")
    if parts[0] == "Artists":
        if len(parts) < 4:
            raise ValueError("artist preparation requires a known artist")
        return "/".join(parts[:2])
    return "general"


def _owner(relative, root=None, cfg=None):
    parts = pathlib.PurePosixPath(relative).parts
    _domain(relative, root, cfg)
    if len(parts) < 3 or parts[-2] not in ("gallery", "review"):
        raise ValueError("retained preparation requires a native gallery/review photo")
    return "/".join(parts[:-2])


def _checked(root, relative, expected):
    path = _safe(root, relative)
    if not isinstance(expected, str) or not re.fullmatch("[0-9a-f]{64}", expected):
        raise ValueError("invalid retained preparation checksum")
    if not path.is_file() or _digest(path) != expected:
        raise ValueError(f"retained preparation checksum mismatch: {relative}")
    return path


def _set_key(source_hash, source, photo_id, domain, recipe):
    identity = {
        "sourceSha256": source_hash, "source": source, "photoId": photo_id,
        "domain": domain, "recipe": recipe,
    }
    return hashlib.sha256(json.dumps(
        identity, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")).hexdigest()[:32]


def _image_artifacts(row):
    for index, record in enumerate(row.get("variants", {}).values()):
        for field, checksum in (("path", "sha256"), ("thumbnail", "thumbnailSha256"),
                                ("padded", "paddedSha256")):
            if field == "padded" and field not in record and checksum not in record:
                continue
            yield f"v{index:02d}-{field}", record[field], record[checksum]
    if row.get("recommendedPadded"):
        record = row["recommendedPadded"]
        if (row.get("recommendation", {}).get("use") != "original"
                or record["source"] != row["retained"]):
            raise ValueError("retained original padding differs from recommendation")
        yield "recommended-padded", record["path"], record["sha256"]


def _detail_navigation(root, current, detail, domain, *, include_gallery_navigation=False):
    """Link only existing local views; derivative manifest is the availability proof."""
    from . import derivatives

    root = pathlib.Path(root).absolute()
    reports = cw.storage_root(cw.load_cfg(), "reports", root=root)
    photo = _safe(root, current)
    target = _safe(root, detail)
    report_area = "artists" if domain.startswith("Artists/") else "library"
    report_folder = (reports / report_area).relative_to(root).as_posix()
    overview = "artists_gallery.html" if domain.startswith("Artists/") else "people_gallery.html"
    review = "artists_gallery_review.html" if domain.startswith("Artists/") else "people_gallery_review.html"
    links = [("Current native photo", photo)]
    for label, filename in (("People" if domain == "general" else "Artists", overview),
                            ("Photo review", review), ("Intake runs", "intake_runs.html")):
        candidate = _safe(root, f"{report_folder}/{filename}")
        if include_gallery_navigation or candidate.is_file():
            links.append((label, candidate))
    for framing, label in (("padded", "Full padded"), ("head", "Head framing"), ("chest", "Chest framing")):
        try:
            key = derivatives.relative_target(photo, framing).as_posix()
            record = derivatives.load(photo.parent.parent)["entries"].get(key, {})
            candidate, _record = derivatives.verified(photo, framing, record.get("box"))
        except (OSError, ValueError, KeyError, TypeError):
            continue
        if candidate is not None:
            links.append((label, pathlib.Path(candidate)))
    anchors = []
    for label, path in links:
        href = quote(os.path.relpath(path, target.parent).replace(os.sep, "/"), safe="/._-")
        anchors.append(f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>')
    return '<nav class="retained-navigation" aria-label="Retained intake navigation">' + " · ".join(anchors) + "</nav>"


def refresh_detail(root, current_photo, photo_id=None, *, include_gallery_navigation=False):
    """Refresh verified retained navigation after viewers/derivatives exist."""
    data = verify_link(root, current_photo, photo_id)
    if data is None:
        raise ValueError("cannot refresh stale or invalid retained preparation detail")
    detail = _safe(root, data["detail"])
    before = detail.read_bytes()
    text = before.decode("utf-8")
    text = text.replace("Image preparation pilot - experimental, no library changes", "Retained intake evidence")
    text = text.replace("Image preparation pilot", "Retained intake evidence")
    text = re.sub(r"(?i)matching (?:is |has )?not (?:been )?run", "recipe comparison predates publication", text)
    text = text.replace("Sidecar comparisons only · No library changes",
                        "Retained recipe evidence · Current native publication linked above")
    navigation = _detail_navigation(
        root, data["current"], data["detail"], data["domain"],
        include_gallery_navigation=include_gallery_navigation,
    )
    if '<nav class="retained-navigation"' in text:
        text = re.sub(r'<nav class="retained-navigation".*?</nav>', navigation, text, count=1, flags=re.S)
    else:
        text = re.sub(r"(<body[^>]*>)", lambda match: match[1] + navigation, text, count=1)
    payload = text.encode("utf-8")
    manifest = _safe(root, data["manifest"])
    prior_manifest = manifest.read_bytes()
    updated = json.loads(prior_manifest)
    for entry in updated["artifacts"]:
        if entry["path"] == data["detail"]:
            entry["sha256"] = hashlib.sha256(payload).hexdigest()
    try:
        detail.write_bytes(payload)
        manifest.write_bytes((json.dumps(updated, indent=2) + "\n").encode("utf-8"))
        if verify_link(root, current_photo, photo_id) is None:
            raise ValueError("refreshed retained detail verification failed")
    except Exception:
        detail.write_bytes(before)
        manifest.write_bytes(prior_manifest)
        raise
    return [
        {"path": data["detail"], "sha256": hashlib.sha256(payload).hexdigest()},
        {"path": data["manifest"], "sha256": _digest(manifest)},
    ]


def stage_photo(root, destination, preparation_root, preparation_row, *, recipe):
    """Publish auxiliary files into an isolated staging root, without overwrites.

    Return [{path: root-relative POSIX string, sha256: checksum}], excluding the
    already installed native photo. Only this row's declared artifacts are read.
    """
    root = pathlib.Path(root).absolute()
    preparation_root = pathlib.Path(preparation_root).absolute()
    destination = pathlib.Path(destination).as_posix()
    owner = _owner(destination, root)
    row = json.loads(json.dumps(preparation_row))
    domain = _domain(destination, root)
    if _domain(row["source"], root) != domain:
        raise ValueError("retained preparation cannot cross artist/general domains")
    scope = row.get("sourceScope")
    if scope and scope.get("matchingDomain") != domain:
        raise ValueError("retained preparation source scope differs")
    source_hash = row["sourceSha256"]
    original = _checked(preparation_root, row["retained"], source_hash)
    native = _safe(root, destination)
    native_hash = _digest(native)
    selected = row.get("processing", {}).get("final", row.get("recommendation", {}).get("use", "original"))
    selected = "original" if selected == "control" else selected
    variant = row.get("variants", {}).get(selected)
    expected = variant["sha256"] if variant else source_hash if selected == "original" else None
    if native_hash != expected:
        raise ValueError("native photo does not match selected preparation bytes")
    set_key = _set_key(source_hash, row["source"], row.get("photoId"), domain, recipe)
    intake = f"{owner}/gallery_intake/{set_key}"
    org = f"{owner}/gallery_org/{set_key}"
    for folder in (intake, org):
        if _safe(root, folder).exists():
            raise ValueError(f"retained preparation already exists: {folder}")
    original_relative = f"{org}/original{original.suffix.lower()}"
    payloads = {original_relative: original.read_bytes()}
    detail = _checked(preparation_root, row["detail"], row["detailSha256"])
    if len(row.get("variants", {})) > (MAX_ARTIFACTS - 3) // 3:
        raise ValueError("too many retained preparation variants")
    artifact_map = {}
    for label, relative, checksum in _image_artifacts(row):
        artifact = _checked(preparation_root, relative, checksum)
        key = f"{intake}/{label}{artifact.suffix.lower()}"
        if key in payloads:
            raise ValueError("repeated retained preparation artifact")
        if relative in artifact_map:
            raise ValueError("repeated retained preparation source artifact")
        artifact_map[relative] = key
        payloads[key] = artifact.read_bytes()
    if len(payloads) > MAX_ARTIFACTS - 2:
        raise ValueError("too many retained preparation artifacts")
    detail_relative = f"{intake}/detail.html"
    detail_target = _safe(root, detail_relative)
    original_href = os.path.relpath(_safe(root, original_relative), detail_target.parent).replace(os.sep, "/")
    text = detail.read_text(encoding="utf-8")
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != row["detailSha256"]:
        raise ValueError("preparation detail changed during publication")
    text = text.replace(quote("../" + row["retained"]), quote(original_href, safe="/._-"))
    text = text.replace(quote("../" + row["detail"]), "#top")
    for source_relative, published_relative in artifact_map.items():
        href = pathlib.PurePosixPath(published_relative).name
        text = text.replace(quote("../" + source_relative), quote(href, safe="/._-"))
    text = text.replace('href="../index.html"', 'href="#top"')
    text = text.replace("Back to comparison gallery", "Back to retained comparison")
    text = re.sub(r' style="--st-banner:url\([^"]*\)"', "", text)
    text = text.replace("Image preparation pilot - experimental, no library changes", "Retained intake evidence")
    text = text.replace("Image preparation pilot", "Retained intake evidence")
    text = re.sub(r"(?i)matching (?:is |has )?not (?:been )?run", "recipe comparison predates publication", text)
    text = text.replace("Sidecar comparisons only · No library changes",
                        "Retained recipe evidence · Current native publication linked above")
    navigation = _detail_navigation(root, destination, detail_relative, domain)
    text = re.sub(r"(<body[^>]*>)", lambda match: match[1] + navigation, text, count=1)
    if detail_relative in payloads:
        raise ValueError("detail collides with retained variant")
    payloads[detail_relative] = text.encode("utf-8")
    data = {
        "formatVersion": 1, "sourceSha256": source_hash, "setKey": set_key,
        "original": original_relative, "current": destination, "currentSha256": native_hash,
        "photoId": metadata.photo_id_from_name(native.name) or row.get("photoId"),
        "domain": domain, "recipe": recipe,
        "selected": selected, "detail": detail_relative, "detailSourceSha256": row["detailSha256"],
        "artifactMap": artifact_map,
        "row": row,
        "artifacts": [{"path": key, "sha256": hashlib.sha256(payload).hexdigest()}
                      for key, payload in payloads.items()],
    }
    manifest_relative = f"{intake}/{MANIFEST}"
    payloads[manifest_relative] = (json.dumps(data, indent=2) + "\n").encode("utf-8")
    if len(payloads[manifest_relative]) > MAX_MANIFEST_BYTES:
        raise ValueError("retained preparation manifest too large")
    for relative in payloads:
        if _safe(root, relative).exists():
            raise ValueError(f"retained preparation destination exists: {relative}")
    completed = []
    try:
        for relative, payload in payloads.items():
            target = _safe(root, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(payload)
            completed.append(target)
            _checked(root, relative, hashlib.sha256(payload).hexdigest())
        if verify_link(root, destination) is None:
            raise ValueError("retained preparation changed during publication")
    except Exception:
        for target in reversed(completed):
            target.unlink()
        for folder in (intake, org):
            target = _safe(root, folder)
            if target.exists():
                for child in sorted(target.rglob("*"), reverse=True):
                    if child.is_dir():
                        child.rmdir()
                target.rmdir()
        raise
    return [{"path": relative, "sha256": hashlib.sha256(payload).hexdigest()}
            for relative, payload in payloads.items()]


def _manifests(root, current):
    owner = _owner(current, root)
    directory = _safe(root, f"{owner}/gallery_intake")
    reads = verification_reads.active()
    cache_key = (pathlib.Path(root).absolute(), directory)
    if reads is not None and cache_key in reads.manifests:
        return reads.manifests[cache_key]
    children = reads.children(directory) if reads is not None else None
    if not directory.exists():
        return []
    paths = []
    children = children if children is not None else directory.iterdir()
    for count, child in enumerate(children):
        if count >= MAX_SETS:
            raise ValueError("retained preparation index exceeds bounded set count")
        _safe(root, child.relative_to(root).as_posix())
        if child.is_dir():
            if not re.fullmatch("[0-9a-f]{32}", child.name):
                raise ValueError("unexpected retained preparation set")
            paths.append(_safe(root, f"{owner}/gallery_intake/{child.name}/{MANIFEST}"))
    if reads is not None:
        reads.manifests[cache_key] = paths
    return paths


def _load(path):
    reads = verification_reads.active()
    if reads is not None:
        data = reads.document(path, MAX_MANIFEST_BYTES)
        if data.get("formatVersion") != 1:
            raise ValueError("unsupported retained preparation manifest")
        return data
    if path.stat().st_size > MAX_MANIFEST_BYTES:
        raise ValueError("retained preparation manifest too large")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("formatVersion") != 1:
        raise ValueError("unsupported retained preparation manifest")
    return data


def verify_link(root, current_photo, photo_id=None):
    """Return verified lineage, or None; never fall back to basename or ID."""
    try:
        root = pathlib.Path(root).absolute()
        photo = pathlib.Path(current_photo)
        current = photo.relative_to(root).as_posix() if photo.is_absolute() else photo.as_posix()
        native = _safe(root, current)
        matches = []
        owner = _owner(current, root)
        for manifest in _manifests(root, current):
            data = _load(manifest)
            if data["current"] != current:
                continue
            if data["domain"] != _domain(current, root) or (photo_id is not None and data["photoId"] != photo_id):
                return None
            if _digest(native) != data["currentSha256"]:
                return None
            artifacts = data["artifacts"]
            if not 2 <= len(artifacts) <= MAX_ARTIFACTS:
                return None
            source_hash = data["sourceSha256"]
            set_key = data["setKey"]
            row = data["row"]
            if (manifest.parent.name != set_key or set_key != _set_key(
                    source_hash, row["source"], row.get("photoId"), data["domain"], data["recipe"])):
                return None
            paths = {}
            for entry in artifacts:
                relative = entry["path"]
                if (relative in paths or not (
                        relative.startswith(f"{owner}/gallery_org/{set_key}/")
                        or relative.startswith(f"{owner}/gallery_intake/{set_key}/"))):
                    return None
                paths[relative] = _checked(root, relative, entry["sha256"])
            if data["original"] not in paths or data["detail"] not in paths:
                return None
            if _digest(paths[data["original"]]) != source_hash:
                return None
            if row["sourceSha256"] != source_hash or _domain(row["source"], root) != data["domain"]:
                return None
            scope = row.get("sourceScope")
            if scope and scope.get("matchingDomain") != data["domain"]:
                return None
            expected_paths = {data["original"], data["detail"]}
            for _, source_relative, checksum in _image_artifacts(row):
                relative = data.get("artifactMap", {}).get(
                    source_relative, f"{owner}/gallery_intake/{set_key}/{source_relative}")
                if relative not in paths or _digest(paths[relative]) != checksum:
                    return None
                expected_paths.add(relative)
            if set(paths) != expected_paths:
                return None
            selected = data["selected"]
            expected = source_hash if selected == "original" else row["variants"][selected]["sha256"]
            if expected != data["currentSha256"]:
                return None
            matches.append({**data, "manifest": manifest.relative_to(root).as_posix()})
        return matches[0] if len(matches) == 1 else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


def require_unretained_move(root, source):
    """Refuse unjournalled set moves, including invalid/stale lineage."""
    root = pathlib.Path(root).absolute()
    source = pathlib.Path(source)
    current = source.relative_to(root).as_posix() if source.is_absolute() else source.as_posix()
    for manifest in _manifests(root, current):
        data = _load(manifest)
        if _owner(data["current"], root) != _owner(current, root):
            raise ValueError("retained preparation owner changed without verified lineage")
        if data.get("current") == current:
            raise ValueError("retained preparation move requires lineage-aware publication; no files moved")


def claims_photo(root, current_photo):
    """Invalid destination-owned evidence must not resurrect historical links."""
    try:
        root = pathlib.Path(root).absolute()
        current = pathlib.Path(current_photo)
        current = current.relative_to(root).as_posix() if current.is_absolute() else current.as_posix()
        return any(_load(path).get("current") == current for path in _manifests(root, current))
    except (OSError, ValueError, KeyError, TypeError):
        return True


def crop_guard(root, photo, photo_id=None):
    """Skip verified prepared natives; refuse stale/conflicting preparation claims."""
    root = pathlib.Path(root).absolute()
    candidate = pathlib.Path(getattr(photo, "path", photo))
    current = candidate.relative_to(root).as_posix() if candidate.is_absolute() else candidate.as_posix()
    _safe(root, current)
    if verify_link(root, current, photo_id) is not None:
        return True
    try:
        for manifest in _manifests(root, current):
            data = _load(manifest)
            # Stable ID is a conflict alarm only, never continuity evidence.
            if data.get("current") == current or (
                    photo_id is not None and data.get("photoId") == photo_id):
                raise ValueError(
                    "legacy crop refused: retained preparation is stale, invalid or conflicting; "
                    "verify current path, source bytes and retained artifacts before processing")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith("legacy crop refused:"):
            raise
        raise ValueError(f"legacy crop refused: unreadable or invalid retained preparation: {exc}") from exc
    return False


def source_is_prepared(photo):
    """Resolve only the native owner's explicit current-path claims, fail closed."""
    native = pathlib.Path(getattr(photo, "path", photo)).absolute()
    reads = verification_reads.active()
    if reads is None:
        return _source_is_prepared(native)
    if native not in reads.prepared:
        reads.prepared[native] = _source_is_prepared(native)
    return reads.prepared[native]


def _source_is_prepared(native):
    if native.parent.name not in ("gallery", "review"):
        return False
    owner = native.parent.parent
    directory = _safe(owner, "gallery_intake")
    reads = verification_reads.active()
    children = reads.children(directory) if reads is not None else None
    if not directory.exists():
        return False
    photo_id = metadata.photo_id_from_name(native.name)
    children = children if children is not None else directory.iterdir()
    for count, child in enumerate(children):
        if count >= MAX_SETS:
            raise ValueError("prepared source owner exceeds bounded set count")
        if reads is not None and child in reads.source_claims:
            data, root, expected = reads.source_claims[child]
        else:
            _safe(owner, child.relative_to(owner).as_posix())
            if not child.is_dir() or not re.fullmatch("[0-9a-f]{32}", child.name):
                raise ValueError("invalid retained preparation owner entry")
            manifest = _safe(owner, f"gallery_intake/{child.name}/{MANIFEST}")
            try:
                data = _load(manifest)
                relative = data["current"]
            except (OSError, ValueError, KeyError, TypeError) as exc:
                raise ValueError(f"invalid prepared source lineage: {manifest}: {exc}") from exc
            parts = pathlib.PurePosixPath(relative).parts
            root = native
            for _ in parts:
                root = root.parent
            _owner(relative, root)
            expected = _safe(root, relative)
            if reads is not None:
                reads.source_claims[child] = (data, root, expected)
        if expected == native:
            return crop_guard(root, native, photo_id)
        if data.get("photoId") == photo_id and photo_id is not None:
            raise ValueError("prepared source path changed without verified retained lineage")
    return False


def plan_transfer(root, source, destination):
    """Freeze a complete, checksum-verified set move for a maintenance journal."""
    root = pathlib.Path(root).absolute()
    source, destination = str(source), str(destination)
    if not claims_photo(root, source):
        return None
    data = verify_link(root, source)
    if data is None:
        raise ValueError("cannot transfer stale or invalid retained preparation")
    if _domain(source, root) != _domain(destination, root):
        raise ValueError("retained preparation cannot cross artist/general domains")
    old_owner, new_owner = _owner(source, root), _owner(destination, root)
    manifest = _safe(root, data["manifest"])
    before = manifest.read_text(encoding="utf-8")
    updated = json.loads(before)
    updated["current"] = destination
    updated["photoId"] = metadata.photo_id_from_name(pathlib.PurePosixPath(destination).name) or data["photoId"]
    files = []
    for entry in [*data["artifacts"], {"path": data["manifest"], "sha256": _digest(manifest)}]:
        old = entry["path"]
        new = new_owner + old[len(old_owner):]
        files.append({"source": old, "destination": new, "sha256": entry["sha256"]})
    for field in ("original", "detail"):
        updated[field] = new_owner + updated[field][len(old_owner):]
    for entry in updated["artifacts"]:
        entry["path"] = new_owner + entry["path"][len(old_owner):]
    for key, relative in updated.get("artifactMap", {}).items():
        updated["artifactMap"][key] = new_owner + relative[len(old_owner):]
    detail_before = _safe(root, data["detail"]).read_text(encoding="utf-8")
    detail_after = re.sub(
        r'<nav class="retained-navigation".*?</nav>',
        _detail_navigation(root, destination, updated["detail"], data["domain"]),
        detail_before, count=1, flags=re.S,
    )
    for entry in updated["artifacts"]:
        if entry["path"] == updated["detail"]:
            entry["sha256"] = hashlib.sha256(detail_after.encode("utf-8")).hexdigest()
    expected = {entry["source"] for entry in files}
    actual = set()
    for directory in ("gallery_org", "gallery_intake"):
        folder = _safe(root, f"{old_owner}/{directory}/{data['setKey']}")
        for path in folder.rglob("*"):
            _safe(root, path.relative_to(root).as_posix())
            if path.is_file():
                actual.add(path.relative_to(root).as_posix())
    if actual != expected:
        raise ValueError("retained preparation set contains untracked files")
    return {
        "sourcePhoto": source, "destinationPhoto": destination,
        "sourceSha256": data["sourceSha256"], "currentSha256": data["currentSha256"], "setKey": data["setKey"],
        "files": files, "manifestBefore": before,
        "manifestAfter": json.dumps(updated, indent=2) + "\n",
        "detailBefore": detail_before, "detailAfter": detail_after,
        "detailSource": data["detail"], "detailDestination": updated["detail"],
    }


def validate_transfers(root, transfers, *, reverse=False):
    """Recheck frozen source bytes and every destination before any mutation."""
    seen = set()
    for transfer in transfers:
        direction = ("destination", "source") if reverse else ("source", "destination")
        source_photo = transfer["destinationPhoto"] if reverse else transfer["sourcePhoto"]
        data = verify_link(root, source_photo)
        if (data is None or data["sourceSha256"] != transfer["sourceSha256"]
                or data["currentSha256"] != transfer["currentSha256"]
                or data["setKey"] != transfer["setKey"]):
            raise ValueError("retained preparation source version changed")
        current_manifest = _safe(root, data["manifest"])
        expected_manifest = transfer["manifestAfter"] if reverse else transfer["manifestBefore"]
        if current_manifest.read_text(encoding="utf-8") != expected_manifest:
            raise ValueError("retained preparation manifest version changed")
        for row in transfer["files"]:
            source, destination = row[direction[0]], row[direction[1]]
            expected = hashlib.sha256(expected_manifest.encode("utf-8")).hexdigest() if (
                row["source"].endswith("/manifest.json")) else row["sha256"]
            if reverse and row["source"] == transfer.get("detailSource"):
                expected = hashlib.sha256(transfer["detailAfter"].encode("utf-8")).hexdigest()
            _checked(root, source, expected)
            target = _safe(root, destination)
            if source != destination and target.exists():
                raise ValueError(f"retained preparation target exists: {destination}")
            if destination in seen:
                raise ValueError("retained preparation repeats a destination")
            seen.add(destination)
        if _owner(transfer["sourcePhoto"], root) != _owner(transfer["destinationPhoto"], root):
            target_photo = transfer["sourcePhoto"] if reverse else transfer["destinationPhoto"]
            for directory in ("gallery_org", "gallery_intake"):
                folder = _safe(root, f"{_owner(target_photo, root)}/{directory}/{transfer['setKey']}")
                if folder.exists():
                    raise ValueError(f"retained preparation target set exists: {folder}")


def owned_files(root, current_photo, photo_id=None):
    """Return exact verified withdrawal inventory; reject unknown/edited set files."""
    root = pathlib.Path(root).absolute()
    photo = pathlib.Path(getattr(current_photo, "path", current_photo))
    current = photo.relative_to(root).as_posix() if photo.is_absolute() else photo.as_posix()
    if verify_link(root, current, photo_id) is None:
        raise ValueError("cannot inventory stale or invalid retained preparation")
    transfer = plan_transfer(root, current, current)
    return [{"path": row["source"], "sha256": row["sha256"]} for row in transfer["files"]]


def execute_transfer(root, transfer, *, reverse=False):
    """Move a frozen set after its native photo, with local rollback on failure."""
    direction = ("destination", "source") if reverse else ("source", "destination")
    before = transfer["manifestAfter"] if reverse else transfer["manifestBefore"]
    after = transfer["manifestBefore"] if reverse else transfer["manifestAfter"]
    moved = []
    manifest_row = transfer["files"][-1]
    manifest = _safe(root, manifest_row[direction[1]])
    pending = _safe(root, manifest_row[direction[1]] + ".pending")
    if pending.exists():
        raise ValueError("unfinished retained preparation transfer")
    try:
        for row in transfer["files"]:
            source = _safe(root, row[direction[0]])
            destination = _safe(root, row[direction[1]])
            if source == destination:
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                raise ValueError("retained preparation target appeared during transfer")
            source.rename(destination)
            moved.append((source, destination))
        if transfer.get("detailSource"):
            detail_key = "detailSource" if reverse else "detailDestination"
            _safe(root, transfer[detail_key]).write_bytes(
                transfer["detailBefore" if reverse else "detailAfter"].encode("utf-8"))
        with pending.open("xb") as stream:
            stream.write(after.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        pending.replace(manifest)
        current = transfer["sourcePhoto"] if reverse else transfer["destinationPhoto"]
        if verify_link(root, current) is None:
            raise ValueError("transferred retained preparation failed verification")
        old_photo = transfer["destinationPhoto"] if reverse else transfer["sourcePhoto"]
        new_photo = transfer["sourcePhoto"] if reverse else transfer["destinationPhoto"]
        if _owner(old_photo, root) != _owner(new_photo, root):
            for directory in ("gallery_org", "gallery_intake"):
                folder = _safe(root, f"{_owner(old_photo, root)}/{directory}/{transfer['setKey']}")
                for child in sorted(folder.rglob("*"), reverse=True):
                    if child.is_dir():
                        child.rmdir()
                folder.rmdir()
                if not any(folder.parent.iterdir()):
                    folder.parent.rmdir()
    except Exception:
        if pending.exists():
            pending.unlink()
        if manifest.exists():
            manifest.write_bytes(before.encode("utf-8"))
        if transfer.get("detailSource"):
            detail_key = "detailSource" if reverse else "detailDestination"
            detail = _safe(root, transfer[detail_key])
            if detail.exists():
                detail.write_bytes(transfer["detailAfter" if reverse else "detailBefore"].encode("utf-8"))
        for source, destination in reversed(moved):
            source.parent.mkdir(parents=True, exist_ok=True)
            destination.rename(source)
        raise


def rename_photo(root, source, destination):
    """Rename within one owner, atomically updating the explicit current mapping."""
    root = pathlib.Path(root).absolute()
    source = pathlib.Path(source).relative_to(root).as_posix()
    destination = pathlib.Path(destination).relative_to(root).as_posix()
    if _owner(source, root) != _owner(destination, root):
        raise ValueError("retained preparation owner moves require lineage-aware publication")
    manifests = _manifests(root, source)
    affected = []
    for path in manifests:
        data = _load(path)
        if _owner(data["current"], root) != _owner(source, root):
            raise ValueError("retained preparation owner changed without verified lineage")
        if data.get("current") == source:
            affected.append(path)
    if not affected:
        _safe(root, source).rename(_safe(root, destination))
        return
    data = verify_link(root, source)
    if data is None:
        raise ValueError("cannot rename stale or invalid retained preparation")
    target = _safe(root, destination)
    if target.exists() and source.casefold() != destination.casefold():
        raise ValueError("retained preparation rename destination exists")
    manifest = affected[0]
    before = manifest.read_bytes()
    detail = _safe(root, data["detail"])
    detail_before = detail.read_bytes()
    updated = json.loads(before)
    updated["current"] = destination
    pending = manifest.with_name("manifest.rename-pending.json")
    if pending.exists():
        raise ValueError("unfinished retained preparation rename requires recovery")
    native = _safe(root, source)
    with pending.open("xb") as stream:
        stream.write((json.dumps(updated, indent=2) + "\n").encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())
    moved = False
    try:
        native.rename(target)
        moved = True
        pending.replace(manifest)
        refresh_detail(root, target)
    except Exception:
        if moved:
            target.rename(native)
            detail.write_bytes(detail_before)
            manifest.write_bytes(before)
        if pending.exists():
            pending.unlink()
        raise
