"""Read-only family-reference suggestions and collision-aware naming evidence."""
import collections
import datetime
import html
import json
import pathlib
from urllib.parse import quote


def build_preview(identities, cores, policy):
    """Compare direct references; never infer transitive or confirmed membership."""
    identities = sorted(identities, key=lambda row: (row["folder"].casefold(), row["personId"] or ""))
    names = collections.defaultdict(list)
    surnames = collections.defaultdict(list)
    folders = collections.defaultdict(list)
    for row in identities:
        name = row["recordedName"]
        if name:
            names[name.casefold()].append(row["folder"])
            if len(name.split()) >= 2:
                surnames[name.rsplit(None, 1)[-1].casefold()].append(row)
        folders[row["folder"].casefold()].append(row["folder"])
    eligible = {
        row["folder"]: row for row in identities
        if row["personId"] and row["folder"] in cores
        and row["category"] != "Artists" and not row.get("mergedInto")
    }
    minimum = policy["lookalikeGroups"]["suggestionMinimumSimilarity"]
    suggestions, excluded = [], []
    for row in identities:
        folder = row["folder"]
        if folder not in eligible:
            excluded.append({
                "folder": folder, "personId": row["personId"],
                "reason": "Artist provenance, unregistered/merged identity, or no usable identity core",
            })
            continue
        vector = cores[folder]["vector"]
        ranked = sorted(
            (
                (float(vector @ cores[other]["vector"]), other)
                for other in eligible if other != folder
                and cores[other]["side"] == cores[folder]["side"]
            ),
            key=lambda item: (-item[0], item[1].casefold()),
        )
        if not ranked or ranked[0][0] < minimum:
            continue
        score, reference = ranked[0]
        target = eligible[reference]
        name, reference_name = row["recordedName"], target["recordedName"]
        fixed_slot = row["category"] in {"Angels", "Sisters"}
        proposed = None
        reason = "existing name remains unchanged; proposal needs review"
        if fixed_slot:
            reason = "fixed cast identity; no rename proposed"
        elif name and reference_name and len(name.split()) >= 2 and len(reference_name.split()) >= 2:
            proposed = name.split()[0] + " " + reference_name.rsplit(None, 1)[-1]
        else:
            reason = "incomplete recorded source/reference name; resolve before naming"
        collision = (
            [key for key in names.get(proposed.casefold(), []) if key != folder]
            if proposed else []
        )
        suggestions.append({
            "personId": row["personId"], "folder": folder, "currentName": name,
            "referencePersonId": target["personId"], "referenceFolder": reference,
            "referenceName": reference_name, "score": score,
            "nextBestScore": ranked[1][0] if len(ranked) > 1 else None,
            "nextBestFolder": ranked[1][1] if len(ranked) > 1 else None,
            "margin": score - ranked[1][0] if len(ranked) > 1 else None,
            "alternatives": [
                {"personId": eligible[key]["personId"], "folder": key, "score": value}
                for value, key in ranked[1:] if value >= minimum
            ],
            "state": "suggested", "proposedName": proposed, "nameCollisions": collision,
            "samePersonReviewRequired": score >= min(
                policy["categoryPolicies"][row["category"]]["mergeMinimum"],
                policy["categoryPolicies"][target["category"]]["mergeMinimum"],
            ),
            "reason": reason,
        })
    proposed_names = collections.defaultdict(list)
    for row in suggestions:
        if row["proposedName"]:
            proposed_names[row["proposedName"].casefold()].append(row["folder"])
    for row in suggestions:
        row["proposalCollisions"] = [
            folder for folder in proposed_names.get((row["proposedName"] or "").casefold(), [])
            if folder != row["folder"]
        ]
    return {
        "reportVersion": 1, "policyVersion": policy["version"], "policyStatus": policy["status"],
        "mode": "suggestions-only", "automaticChanges": False, "transitiveMembership": False,
        "suggestionMinimumSimilarity": minimum,
        "limitations": [
            "Direct closest-reference alternatives, not accepted family memberships.",
            "Reciprocal suggestions and overlapping references are not merged or followed transitively.",
            "Similarity and shared surnames do not prove distinctness, identity or family membership.",
            "Naming proposals preserve the current first name; shared-initial alternatives need review.",
            "Existing names, memberships, photos, catalogue and workflow selections are unchanged.",
        ],
        "identityCount": len(identities), "identities": identities, "suggestions": suggestions,
        "surnameReuse": [
            {"surname": surname, "folders": [row["folder"] for row in rows],
             "state": "unresolved", "reason": "shared surname alone is not relationship evidence"}
            for surname, rows in sorted(surnames.items()) if len(rows) > 1
        ],
        "existingNameCollisions": [
            {"name": name, "folders": rows} for name, rows in sorted(names.items()) if len(rows) > 1
        ],
        "folderCollisions": [
            {"folder": folder, "paths": rows} for folder, rows in sorted(folders.items()) if len(rows) > 1
        ],
        "coreEvidence": {
            folder: {key: value for key, value in core.items() if key != "vector"}
            for folder, core in sorted(cores.items()) if folder in eligible
        },
        "excluded": excluded,
    }


def render_html(report, review_page):
    """A static local preview; no scripts, file operations or automatic approval."""
    def escape(value):
        return html.escape(str(value if value is not None else ""))

    lines = [
        '<!doctype html><html><head><meta charset="utf-8"><title>Family and name preview</title>',
        "<style>body{font:15px Segoe UI,Arial;margin:24px;background:#faf8f3}"
        "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:8px;text-align:left}"
        "td{vertical-align:top}.warning{color:#8a3b16}code{overflow-wrap:anywhere}</style></head><body>",
        "<h1>Family-reference and name preview</h1>",
        f"<p>{report['identityCount']} identities; {len(report['suggestions'])} direct suggestions. "
        f"Policy: {escape(report['policyVersion'])}. No changes are authorized.</p><ul>",
        *[f"<li>{escape(note)}</li>" for note in report["limitations"]], "</ul>",
        "<h2>Direct reference suggestions</h2><table><tr><th>Identity</th><th>Reference</th>"
        "<th>Evidence</th><th>Name preview (not applied)</th></tr>",
    ]

    def person_link(folder):
        return f'<a href="{escape(review_page.as_uri() + "?person=" + quote(folder, safe=""))}">{escape(folder)}</a>'

    for row in report["suggestions"]:
        warnings = row["nameCollisions"] + row["proposalCollisions"]
        evidence = f'{row["score"]:.3f}'
        evidence += f'; lead {row["margin"]:.3f}' if row["margin"] is not None else "; no runner-up"
        if row["samePersonReviewRequired"]:
            evidence += "; inspect possible same-person match before calling these distinct family members"
        name = escape(row["proposedName"]) if row["proposedName"] else "No rename proposed"
        if warnings:
            name += '<p class="warning">Collision: ' + escape(", ".join(sorted(set(warnings)))) + "</p>"
        alternatives = (
            "<br>Next: " + person_link(row["nextBestFolder"])
            if row["nextBestFolder"] else ""
        )
        lines.append(
            f"<tr><td>{person_link(row['folder'])}<br>{escape(row['currentName'])}<br>"
            f"<code>{escape(row['personId'])}</code></td>"
            f"<td>{person_link(row['referenceFolder'])}<br>{escape(row['referenceName'])}<br>"
            f"<code>{escape(row['referencePersonId'])}</code></td>"
            f"<td>{escape(evidence)}{alternatives}</td><td>{name}<br>{escape(row['reason'])}</td></tr>"
        )
    lines.extend(["</table>", "<h2>Existing surname reuse (unresolved)</h2><ul>"])
    for row in report["surnameReuse"]:
        lines.append(f"<li>{escape(row['surname'])}: {escape(', '.join(row['folders']))}</li>")
    lines.extend(["</ul><h2>Existing full-name and folder collisions</h2><ul>"])
    for row in report["existingNameCollisions"]:
        lines.append(f"<li>{escape(row['name'])}: {escape(', '.join(row['folders']))}</li>")
    for row in report["folderCollisions"]:
        lines.append(f"<li>{escape(row['folder'])}: {escape(', '.join(row['paths']))}</li>")
    lines.extend(["</ul><h2>Excluded from matching suggestions</h2><ul>"])
    for row in report["excluded"]:
        lines.append(f"<li>{escape(row['folder'])}: {escape(row['reason'])}</li>")
    lines.append("</ul></body></html>\n")
    return "\n".join(lines)


def run(args, api):
    """CLI adapter: reuse frozen engine cores, write only requested report outputs."""
    sandbox = bool(args.root and api.is_sandbox_working_path(args.root))
    if sandbox:
        api.require_sandbox_cache(args.root, args.cache)
        if args.out:
            api.require_sandbox_output(args.root, args.out)
    policy = api.load_policy(args.policy)
    cfg, settings, root, _, space = api.build(args)
    catalog = api.metadata.with_configured_anchors(
        api.metadata.load_catalog(api.metadata.path_for_root(root)), cfg, space.photos,
    )
    cores, _, diagnostics = api.frozen_identity_cores(
        space, catalog, photo_id_fn=api.metadata.photo_id_from_name,
        content_sha256_fn=api.metadata.content_sha256, policy=policy,
    )
    records = collections.defaultdict(list)
    for person_id, person in catalog["people"].items():
        records[person["folder"]].append((person_id, person))
    identities = []
    for folder, path in api.library_people(cfg, settings, root):
        owned = records[folder]
        person_id, person = owned[0] if len(owned) == 1 else (None, {})
        identities.append({
            "folder": folder, "category": api.status_of(folder), "personId": person_id,
            "recordedName": api.people.name_of(path),
            "catalogueName": person.get("displayName"), "mergedInto": person.get("mergedInto"),
            "usablePhotos": len(space.by_key.get(folder, [])),
        })
    report = build_preview(identities, cores, policy)
    report["coreDiagnostics"] = diagnostics
    report["generatedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = pathlib.Path(args.out) if args.out else root / "_reports" / "analysis" / ("families-" + stamp)
    if sandbox:
        api.require_sandbox_output(args.root, output)
    output.mkdir(parents=True, exist_ok=True)
    files = {
        output / "family-preview.json": json.dumps(report, indent=2, ensure_ascii=True) + "\n",
        output / "family-preview.html": render_html(
            report, (root / "_reports" / "library" / "people_gallery_review.html").resolve(),
        ),
    }
    for path, text in files.items():
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(path)
    print(
        f"family preview: {report['identityCount']} identities, {len(report['suggestions'])} "
        f"direct suggestions, {len(report['surnameReuse'])} reused surnames; no library changes"
    )
    print("The embedding cache may be populated; all family and naming results are suggestions only.")
    print(f"report: {output / 'family-preview.html'}")
    return report
