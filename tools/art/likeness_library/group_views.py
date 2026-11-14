"""Read-only appearance metadata and original-backed group browsing."""

import html
import hashlib
import json
import pathlib
import re

from . import metadata


def describe(catalog, photo_id):
    membership = (catalog.get("photos", {}).get(photo_id) or {}).get("membership")
    if not isinstance(membership, dict):
        return None
    group = catalog.get("photoGroups", {}).get(membership.get("groupId")) or {}
    group_id = membership.get("groupId")
    if membership.get("assignmentDisposition") == "provisional":
        label = "Provisional container; not a certified identity; no reference authority"
        if group.get("name"):
            label += " · " + group["name"]
    elif membership.get("assignmentDisposition") == "tentative-parent":
        label = "Tentative parent assignment; no reference authority"
        if group.get("name"):
            label += " · " + group["name"]
    elif group_id:
        label = group.get("name") or f"Appearance group {group_id} (name unrecorded)"
    elif membership.get("status") == "supported" and membership.get("personId"):
        label = "Primary photos"
    elif membership.get("status") == "unresolved":
        label = "Unresolved"
    elif membership.get("status") == "quality-hold":
        label = "Quality hold; no reference authority"
    elif membership.get("status") == "tentative":
        label = "Tentative; no reference authority"
    else:
        label = "Appearance unassigned"
    return {"membership": membership, "group": group, "label": label}


def parent_label(catalog, person_id):
    person = catalog.get("people", {}).get(person_id) or {}
    display_name = person.get("displayName") or "Parent name unavailable"
    folder = person.get("folder") or "folder unavailable"
    return (f"{html.escape(str(display_name))} "
            f"({html.escape(str(folder))}; {html.escape(str(person_id or 'identity unavailable'))})")


def reports_current(catalog, out):
    """Verify all current group index and manifest bytes against the generated receipt."""
    out = pathlib.Path(out)
    receipt = out / "people-gallery-manifest.json"
    if not receipt.is_file():
        return False
    try:
        files = json.loads(receipt.read_text(encoding="utf-8")).get("files", {})
        names = ["photo-groups/index.html"]
        for group_id in catalog.get("photoGroups", {}):
            if not re.fullmatch(r"group_[0-9a-f]{32}", group_id):
                return False
            names.extend(f"photo-groups/{group_id}/{name}" for name in ("index.html", "manifest.json"))
        for name in names:
            path = out.joinpath(*pathlib.PurePosixPath(name).parts)
            if (path.parent.is_symlink() or path.is_symlink() or not path.is_file()
                    or hashlib.sha256(path.read_bytes()).hexdigest() != files.get(name)):
                return False
    except (OSError, ValueError, TypeError):
        return False
    return True


def publish(catalog, sources, out, *, source_root=None):
    """Write a report-only index; never copy or move original images."""
    root = pathlib.Path(out) / "photo-groups"
    if root.is_symlink():
        raise ValueError(f"linked group report directory: {root}")
    root.mkdir(parents=True, exist_ok=True)
    paths = {}
    for photo_id, path in sources:
        if photo_id:
            paths.setdefault(photo_id, []).append(pathlib.Path(path))
    generated = {}
    links = []
    current_ids = set()
    for group_id, group in sorted(catalog.get("photoGroups", {}).items()):
        if not re.fullmatch(r"group_[0-9a-f]{32}", group_id):
            continue
        current_ids.add(group_id)
        directory = root / group_id
        if directory.is_symlink():
            raise ValueError(f"linked group report directory: {directory}")
        directory.mkdir(parents=True, exist_ok=True)
        records, cards = [], []
        for photo_id in group.get("memberPhotoIds", []):
            matches = paths.get(photo_id, [])
            path = None
            if len(matches) == 1 and not matches[0].is_symlink():
                candidate = matches[0].resolve()
                try:
                    if source_root is not None:
                        candidate.relative_to(pathlib.Path(source_root).resolve())
                    expected = (catalog.get("photos", {}).get(photo_id) or {}).get("contentSha256")
                    if expected and candidate.is_file() and metadata.content_sha256(candidate) == expected:
                        path = candidate
                except (OSError, ValueError):
                    pass
            info = describe(catalog, photo_id) or {}
            membership = info.get("membership") or {}
            if membership.get("groupId") != group_id:
                path = None
            records.append({"photoId": photo_id, "path": str(path) if path else None,
                            "membership": membership})
            label = html.escape(str(photo_id))
            if path and path.is_file():
                href = html.escape(path.as_uri(), quote=True)
                card = (f'<a href="{href}"><img loading="lazy" src="{href}" alt="">'
                        f'{html.escape(path.name)}</a>')
            else:
                card = "Missing, ambiguous, inconsistent, or unverified original"
            cards.append(f"<li>{card}<br>{label} · {html.escape(str(membership.get('status', 'unrecorded')))}"
                         f" · core use: {html.escape(str(membership.get('coreUse', False)))}"
                         f"<br>Reason: {html.escape(str(membership.get('reason', '')))}"
                         f"<br>Reference version: {html.escape(str(membership.get('referenceVersion', '')))}"
                         f"<br>Original path: {html.escape(str(path or 'unavailable'))}</li>")
        manifest = {"group": group, "members": records}
        manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        title = html.escape(str(group.get("name") or group_id))
        parent = parent_label(catalog, group.get("personId"))
        page = ("<!doctype html><meta charset=utf-8><title>Appearance group</title>"
                "<style>img{max-width:180px;max-height:180px}li{display:inline-block;vertical-align:top;"
                "width:220px;overflow-wrap:anywhere}</style>"
                f"<h1>{title}</h1><p>Appearance group, not an independent identity. "
                f"Status: {html.escape(str(group.get('status', '')))}. "
                f"Person: {parent}</p>"
                f"<p>Reason: {html.escape(str(group.get('reason', '')))}</p>"
                f"<p>Qualified references in this appearance: {len(group.get('referencePhotoIds', []))}"
                + ("; reference unavailable in this appearance" if not group.get("referencePhotoIds") else "")
                + "</p>"
                f"<p>Source identities: {html.escape(', '.join(map(str, group.get('sourcePersonIds', []))))}</p>"
                '<p><a href="manifest.json">Manifest and lineage history</a> · '
                '<a href="../index.html">All groups</a></p><ul>' + "".join(cards) + "</ul>")
        for name, text in (("index.html", page), ("manifest.json", manifest_text)):
            relative = f"photo-groups/{group_id}/{name}"
            if (directory / name).is_symlink():
                raise ValueError(f"linked group report file: {directory / name}")
            generated[relative] = text.encode("utf-8")
            (directory / name).write_bytes(generated[relative])
        links.append(f'<li><a href="{group_id}/index.html">{title}</a> · '
                     f'{html.escape(str(group.get("status", "")))} · '
                     f'Parent: {parent}'
                     f' · Group ID: {html.escape(group_id)}</li>')
    manifest_path = pathlib.Path(out) / "people-gallery-manifest.json"
    if manifest_path.is_file():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        for name, digest in previous.get("files", {}).items():
            match = re.fullmatch(r"photo-groups/(group_[0-9a-f]{32})/(index\.html|manifest\.json)", name)
            if not match or match.group(1) in current_ids:
                continue
            target = root / match.group(1) / match.group(2)
            if (target.parent.is_symlink() or target.is_symlink() or not target.is_file()
                    or hashlib.sha256(target.read_bytes()).hexdigest() != digest):
                continue
            text = ('<!doctype html><meta charset=utf-8><title>Group unavailable</title>'
                    '<p>This group is no longer in the current catalogue. '
                    '<a href="../index.html">Browse current groups</a>.</p>') if match.group(2) == "index.html" else (
                        json.dumps({"id": match.group(1), "status": "not-current"}, sort_keys=True) + "\n")
            generated[name] = text.encode("utf-8")
            target.write_bytes(generated[name])
    index = ("<!doctype html><meta charset=utf-8><title>Appearance groups</title>"
             "<h1>Appearance groups</h1><p>Groups are views of originals, not separate identities or copies. "
             "Open an original to use its actual path in Explorer or ComfyUI.</p><ul>"
             + "".join(links) + "</ul>")
    if (root / "index.html").is_symlink():
        raise ValueError(f"linked group report file: {root / 'index.html'}")
    generated["photo-groups/index.html"] = index.encode("utf-8")
    (root / "index.html").write_bytes(generated["photo-groups/index.html"])
    return generated
