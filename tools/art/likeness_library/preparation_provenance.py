"""Read-only links from gallery photos to verified preparation comparisons."""
import hashlib
import html
import json
import os
import pathlib
from urllib.parse import quote, urlencode


MAX_RUNS = 32
MAX_ROWS = 5000
MAX_ERRORS = 5
MAX_MANIFEST_BYTES = 8 * 1024 * 1024

EVIDENCE_SCRIPT = """
function appendPreparationEvidence(article, evidence) {
  const state=evidence?.state||"unverified";
  const matches=evidence?.matches||[];
  if(!matches.length) {
    const note=document.createElement("div"); note.className="detail preparation-"+state;
    note.textContent="Preparation: "+(evidence?.summary||"status unavailable"); article.append(note); return;
  }
  const entryPoint=document.createElement("a");
  entryPoint.className="intake-detail-link";
  entryPoint.textContent=matches.length===1?"Open intake detail":matches.length+" intake runs";
  entryPoint.href=matches.length===1?matches[0].href:evidence.historyHref;
  if(matches.length>1){
    const note=document.createElement("div");note.className="detail";
    note.textContent="Preparation: "+evidence.summary;
    article.append(entryPoint,note);return;
  }
  const details=document.createElement("details"); details.className="preparation-evidence preparation-"+state;
  const summary=document.createElement("summary");
  summary.textContent="Preparation: "+(evidence.summary||"verified trace"); details.append(summary);
  const guide=document.createElement("p");
  guide.textContent="Retained original, crops, eraser masks, skipped steps and recommendation. Comparison only; not proof of publication.";
  details.append(guide);
  const list=document.createElement("ul");
  for(const match of matches) {
    const entry=document.createElement("li");
    const anchor=document.createElement("a"); anchor.href=match.href; anchor.textContent="Open verified trace"; entry.append(anchor);
    entry.append(document.createTextNode(" · "+match.recipe+" · "+match.outcome+" · "+match.scope+" · "+match.treatment));
    const decision=document.createElement("div"); decision.textContent=match.decision+". "+match.reason; entry.append(decision);
    const source=document.createElement("div");
    source.textContent="Photo ID: "+(match.photoId||"not recorded")+" (not rename proof) · Source SHA-256: "+match.sourceSha256;
    entry.append(source); list.append(entry);
  }
  details.append(list); article.append(entryPoint,details);
}
"""


def _key(path):
    return pathlib.PurePosixPath(path).as_posix().casefold()


def _source_scope(source):
    parts = pathlib.PurePosixPath(source).parts
    if not parts:
        return None
    category = parts[0]
    artist = parts[1] if category == "Artists" and len(parts) >= 4 else None
    domain = f"Artists/{artist}" if artist else "Artists-unassigned" if category == "Artists" else "general"
    return category, artist, domain


def _scope_matches(row, source, domain):
    expected = _source_scope(source)
    scope = row.get("sourceScope")
    if not expected:
        return False
    category, artist, matching_domain = expected
    if scope is None:
        return matching_domain == "general" if domain == "general" else (
            category == "Artists" and matching_domain.startswith("Artists/")
        )
    if not isinstance(scope, dict):
        return False
    return (
        scope.get("category") == category
        and scope.get("artist") == artist
        and scope.get("matchingDomain") == matching_domain
        and bool(scope.get("reason"))
        and (
            matching_domain == "general"
            if domain == "general"
            else category == "Artists" and matching_domain.startswith("Artists/")
        )
    )


def _summary(row):
    recommendation = row.get("recommendation") or {}
    processing = row.get("processing") or {}
    cleanup = processing.get("cleanup", "not recorded")
    final = processing.get("final", "not recorded")
    treatment = row.get("sourceTreatment", "unassessed (legacy report)")
    decision = recommendation.get("use", "not recorded")
    reason = recommendation.get("reason") or "; ".join(row.get("diagnostics", [])) or "No reason recorded"
    return {
        "treatment": str(treatment),
        "decision": f"{decision}; cleanup {cleanup}; final {final}",
        "reason": str(reason),
    }


class PreparationIndex:
    """Index verified reports once, then hash only current files named by those reports."""

    def __init__(self, root, page_dir, source_paths, domain):
        self.root = pathlib.Path(root).resolve(strict=True)
        self.page_dir = pathlib.Path(page_dir).resolve()
        self.domain = domain
        self._sources = {}
        self._report_by_path = {}
        self._report_by_id = {}
        self._hashes = {}
        self._errors = []
        self.history_runs = []
        self.incomplete = False
        self._load(source_paths)
        self._load_staged()

    def _error(self, message):
        if len(self._errors) < MAX_ERRORS:
            self._errors.append(str(message)[:240])

    def _load(self, source_paths):
        current_by_path = {}
        current_by_id = {}
        for path, photo_id in source_paths:
            resolved = pathlib.Path(path).resolve()
            try:
                relative = resolved.relative_to(self.root).as_posix()
            except ValueError:
                continue
            current_by_path.setdefault(_key(relative), resolved)
            if photo_id:
                current_by_id.setdefault(str(photo_id), set()).add(_key(relative))
        self._sources = current_by_path

        reports = self.root / "_reports" / "preparation"
        if not reports.is_dir():
            return
        try:
            runs = sorted(
                (child for child in reports.iterdir()
                 if child.is_dir() and not child.is_symlink()
                 and child.resolve().parent == reports.resolve()),
                key=lambda child: child.name.casefold(),
            )
        except OSError as exc:
            self._error(f"Cannot list preparation reports: {exc}")
            self.incomplete = True
            return
        if len(runs) > MAX_RUNS:
            self.incomplete = True
            self._error(f"More than {MAX_RUNS} preparation runs; index is incomplete")
        self.history_runs = [
            {"name": run.name, "recipe": "", "status": "not verified", "photos": [], "href": ""}
            for run in runs
        ]
        history_by_name = {entry["name"]: entry for entry in self.history_runs}
        runs = runs[:MAX_RUNS]

        from image_preparation import verify

        row_count = 0
        for run in runs:
            manifest = run / "manifest.json"
            if not manifest.is_file():
                try:
                    empty = next(run.iterdir(), None) is None
                except OSError:
                    empty = False
                if empty:
                    # An aborted run that never wrote anything has nothing to verify or trust.
                    history_by_name[run.name]["status"] = "empty folder; ignored"
                    continue
                self._error(f"{run.name}: no manifest")
                continue
            try:
                if manifest.stat().st_size > MAX_MANIFEST_BYTES:
                    self.incomplete = True
                    self._error(f"{run.name}: manifest exceeds {MAX_MANIFEST_BYTES} bytes")
                    return
                preview = json.loads(manifest.read_text(encoding="utf-8"))
                row_total = len(preview.get("photos", []))
                if row_count + row_total > MAX_ROWS:
                    self.incomplete = True
                    self._error(f"More than {MAX_ROWS} preparation entries; index is incomplete")
                    return
                data = verify(self.root, run, current_sources=False)
            except Exception as exc:  # report is untrusted until the verifier accepts it
                self._error(f"{run.name}: {exc}")
                continue
            if data.get("root") != str(self.root):
                self._error(f"{run.name}: source root differs")
                continue
            recipe = data.get("recipe", {}).get("id", "unknown recipe")
            self._history_record(history_by_name[run.name], run, data)
            for row in data.get("photos", []):
                row_count += 1
                if row_count > MAX_ROWS:
                    self.incomplete = True
                    self._error(f"More than {MAX_ROWS} preparation entries; index is incomplete")
                    return
                source = row.get("source")
                if not isinstance(source, str):
                    continue
                record = {
                    "row": row,
                    "run": run,
                    "recipe": recipe,
                    "source": source,
                    "scope_ok": _scope_matches(row, source, self.domain),
                }
                self._report_by_path.setdefault(_key(source), []).append(record)
                photo_id = row.get("photoId")
                if photo_id:
                    self._report_by_id.setdefault(str(photo_id), []).append(record)

    def _href(self, target):
        return quote(os.path.relpath(target, self.page_dir).replace(os.sep, "/"), safe="/._-")

    def _load_staged(self):
        """History only: staged receipts never enter current-photo lookup maps."""
        from image_preparation import verify
        from .retained_preparation import _checked, _safe

        try:
            directory = _safe(self.root, "_sandbox-state")
            if not directory.is_dir():
                return
            for count, run in enumerate(sorted(directory.iterdir(), key=lambda item: item.name.casefold())):
                if count >= MAX_RUNS:
                    break
                entry = {
                    "name": "_sandbox-state/" + run.name, "recipe": "", "status": "not verified",
                    "photos": [], "href": "", "staged": True,
                }
                try:
                    relative = run.relative_to(self.root).as_posix()
                    _safe(self.root, relative)
                    receipt_path = _safe(self.root, relative + "/intake.json")
                    if not receipt_path.is_file():
                        continue
                    self.history_runs.append(entry)
                    if receipt_path.stat().st_size > MAX_MANIFEST_BYTES:
                        raise ValueError("staged receipt exceeds byte limit")
                    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                    if (receipt.get("schemaVersion") != 1
                            or not isinstance(receipt.get("assessmentErrors"), bool)):
                        raise ValueError("invalid staged intake receipt schema")
                    mirror_relative = relative + "/inputs"
                    mirror = _safe(self.root, mirror_relative)
                    report_relative = mirror_relative + "/_reports/preparation/all"
                    report = _safe(self.root, report_relative)
                    manifest = _checked(self.root, report_relative + "/manifest.json",
                                        receipt["preparationManifestSHA256"])
                    if manifest.stat().st_size > MAX_MANIFEST_BYTES:
                        raise ValueError("staged manifest exceeds byte limit")
                    preview = json.loads(manifest.read_text(encoding="utf-8"))
                    if len(preview.get("photos", [])) > MAX_ROWS:
                        raise ValueError("staged run exceeds photo limit")
                    inputs = receipt["inputs"]
                    if not isinstance(inputs, dict) or len(inputs) > MAX_ROWS:
                        raise ValueError("invalid staged receipt inputs")
                    expected = {}
                    for source, digest in inputs.items():
                        _checked(mirror, source, digest)
                        expected[source] = digest
                    actual = {row["source"]: row["sourceSha256"] for row in preview["photos"]}
                    if len(actual) != len(preview["photos"]) or actual != expected:
                        raise ValueError("staged receipt inputs differ from preparation manifest")
                    # Check every declared path for junctions as well as verifier checks.
                    for row in preview["photos"]:
                        for field in ("retained", "detail"):
                            _safe(report, row[field])
                        for variant in row.get("variants", {}).values():
                            for field in ("path", "thumbnail", "padded"):
                                _safe(report, variant[field])
                    _safe(report, "index.html")
                    data = verify(mirror, report, current_sources=True)
                    if data.get("root") != str(mirror):
                        raise ValueError("staged preparation root differs from receipt mirror")
                    if data.get("recipe") != receipt["recipe"]:
                        raise ValueError("staged receipt recipe differs from preparation manifest")
                    if (not isinstance(receipt.get("sourceManifestSHA256"), str)
                            or len(receipt["sourceManifestSHA256"]) != 64
                            or any(character not in "0123456789abcdef" for character in receipt["sourceManifestSHA256"])):
                        raise ValueError("invalid staged source manifest checksum")
                    self._history_record(entry, report, data)
                    entry["status"] = "verified staged/intake-only; not accepted publication"
                    for photo in entry["photos"]:
                        photo["staged"] = True
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    entry["status"] = "unverified staged receipt: " + str(exc)[:240]
        except (OSError, ValueError) as exc:
            self._error("Cannot discover staged intake receipts: " + str(exc))

    def _history_record(self, entry, run, data):
        entry.update(recipe=data.get("recipe", {}).get("id", "unknown recipe"),
                     status="verified historical artifacts")
        for row in data["photos"]:
            if not _scope_matches(row, row["source"], self.domain):
                continue
            variants = row.get("variants", {})
            preview = row.get("recommendation", {}).get("use")
            if preview not in variants:
                preview = "control" if "control" in variants else next(iter(variants), "")
            variant = variants.get(preview, {})
            entry["photos"].append({
                "source": row["source"], "sha256": row["sourceSha256"],
                "outcome": row.get("outcome", "unknown"),
                **_summary(row),
                "href": self._href(run / row["detail"]),
                "thumbnail": self._href(run / variant["thumbnail"]) if variant.get("thumbnail") else "",
                "preview": preview,
            })
        if len(entry["photos"]) == len(data["photos"]):
            entry["href"] = self._href(run / "index.html")

    def history_html(self, *, standalone=False):
        # History has a per-run budget; source-continuity evidence keeps its global budget.
        from image_preparation import verify
        from likeness_library import preparation_history
        for entry in self.history_runs:
            if entry["status"] != "not verified":
                continue
            run = self.root / "_reports" / "preparation" / entry["name"]
            try:
                manifest = run / "manifest.json"
                if manifest.stat().st_size > MAX_MANIFEST_BYTES:
                    raise ValueError(f"manifest exceeds {MAX_MANIFEST_BYTES} bytes")
                preview = json.loads(manifest.read_text(encoding="utf-8"))
                if not isinstance(preview, dict) or not isinstance(preview.get("photos"), list):
                    raise ValueError("manifest must contain a photos list")
                if len(preview.get("photos", [])) > MAX_ROWS:
                    raise ValueError(f"run exceeds {MAX_ROWS} entries")
                data = verify(self.root, run, current_sources=False)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                entry["status"] = f"unverified: {str(exc)[:240]}"
                continue
            self._history_record(entry, run, data)
        return preparation_history.render(self, standalone=standalone)

    def _current_hash(self, key, path):
        if key not in self._hashes:
            try:
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                self._hashes[key] = digest
            except OSError as exc:
                self._hashes[key] = None
                self._error(f"Cannot verify current source {path.name}: {exc}")
        return self._hashes[key]

    def evidence(self, path, photo_id=None):
        from .retained_preparation import claims_photo, verify_link

        retained = verify_link(self.root, path, photo_id)
        if retained and (
            (retained["domain"] == "general") == (self.domain == "general")
        ):
            row = retained["row"]
            href = os.path.relpath(self.root / retained["detail"], self.page_dir).replace(os.sep, "/")
            recipe = retained["recipe"]
            return {
                "state": "verified",
                "summary": "Published native photo and destination-owned retained original/variants verified by path and SHA-256",
                "matches": [{
                    **_summary(row), "href": quote(href, safe="/._-"),
                    "recipe": recipe.get("id", "unknown recipe") if isinstance(recipe, dict) else str(recipe),
                    "sourceSha256": retained["sourceSha256"], "photoId": retained["photoId"],
                    "scope": retained["domain"], "outcome": row.get("outcome", "retained"),
                }],
                "historyHref": "",
            }
        if claims_photo(self.root, path):
            return {
                "state": "unverified", "matches": [], "historyHref": "",
                "summary": "Destination-owned retained preparation is stale, invalid or outside this matching domain; links withheld",
            }
        resolved = pathlib.Path(path).resolve()
        try:
            relative = resolved.relative_to(self.root).as_posix()
        except ValueError:
            return {"state": "unverified", "summary": "Source is outside the preparation root", "matches": []}
        key = _key(relative)
        candidates = self._report_by_path.get(key, [])
        matches = []
        stale = []
        scope_mismatch = False
        if candidates:
            current_hash = self._current_hash(key, resolved)
            for record in candidates:
                row = record["row"]
                if not record["scope_ok"]:
                    scope_mismatch = True
                    continue
                if current_hash is None:
                    continue
                if row.get("sourceSha256") != current_hash:
                    stale.append(record)
                    continue
                details = {
                    **_summary(row),
                    "recipe": record["recipe"],
                    "sourceSha256": current_hash,
                    "photoId": row.get("photoId"),
                    "scope": (
                        row["sourceScope"]["matchingDomain"] if row.get("sourceScope")
                        else _source_scope(record["source"])[2] + " (derived from verified original path)"
                    ),
                    "outcome": row.get("outcome", "unknown"),
                }
                detail = record["row"]["detail"]
                target = (record["run"] / pathlib.PurePosixPath(detail)).resolve()
                try:
                    target.relative_to(record["run"].resolve())
                except ValueError:
                    scope_mismatch = True
                    continue
                relative_href = os.path.relpath(target, self.page_dir).replace(os.sep, "/")
                details["href"] = quote(relative_href, safe="/._-")
                matches.append(details)

        if self.incomplete:
            state = "unverified"
            summary = "Preparation report index is incomplete; no source continuity is asserted"
            matches = []
        elif self._errors:
            state = "unverified"
            summary = "One or more preparation reports could not be verified; matching trace links withheld"
            matches = []
        elif len(matches) > 1:
            state = "ambiguous"
            summary = (
                f"{len(matches)} exact verified traces; current source matches retained input by path and "
                "SHA-256; all are shown without choosing a latest run"
            )
        elif matches:
            state = "verified"
            summary = "Current source matches retained input by exact path and SHA-256"
        elif stale:
            state = "stale"
            summary = "A prior report exists for this path, but the current source hash differs; stale links withheld"
        elif scope_mismatch:
            state = "unverified"
            summary = "Report source/domain scope is missing or does not match; links withheld"
        else:
            renamed = bool(photo_id and any(
                _key(record["source"]) != key
                for record in self._report_by_id.get(str(photo_id), [])
            ))
            if renamed:
                state = "unverified"
                summary = "Photo ID appears at another path; rename continuity is not verified, so no link is claimed"
            else:
                state = "missing"
                summary = "No verified preparation trace for this exact source path and hash"

        return {
            "state": state, "summary": summary, "matches": matches,
            "historyHref": "intake_runs.html?" + urlencode({
                "source": relative, "sha256": matches[0]["sourceSha256"],
            }) if matches else "",
        }


def build_index(root, page_dir, source_paths, domain="general"):
    """Build one read-only report index for a single page generation."""
    return PreparationIndex(root, page_dir, source_paths, domain)


def render_evidence(evidence):
    """Render a compact, escaped per-photo status and verified detail links."""
    state = html.escape(str(evidence.get("state", "unverified")), quote=True)
    summary = html.escape(str(evidence.get("summary", "Preparation status unavailable")))
    matches = evidence.get("matches", [])
    if not matches:
        return (
            f'<div class="preparation-evidence preparation-{state}">'
            f'<strong>Preparation:</strong> {summary}</div>'
        )
    entries = []
    for match in matches:
        recipe = html.escape(str(match.get("recipe", "unknown recipe")))
        scope = html.escape(str(match.get("scope", "unverified")))
        source_hash = html.escape(str(match.get("sourceSha256", "")))
        photo_id = html.escape(str(match.get("photoId") or "not recorded"))
        treatment = html.escape(str(match.get("treatment", "unassessed")))
        decision = html.escape(str(match.get("decision", "not recorded")))
        reason = html.escape(str(match.get("reason", "No reason recorded")))
        href = html.escape(str(match.get("href", "")), quote=True)
        outcome = html.escape(str(match.get("outcome", "unknown")))
        entries.append(
            f'<li><a href="{href}">Open verified trace</a> · {recipe} · {outcome} · '
            f'{scope} · {treatment}<br><span>Photo ID: {photo_id} (not rename proof) · '
            f'Source SHA-256: <code>{source_hash}</code></span><br>'
            f'<span>{decision}. {reason}</span></li>'
        )
    direct_link = (
        f'<a class="intake-detail-link" href="{html.escape(str(matches[0]["href"]), quote=True)}">'
        'Open intake detail</a>' if len(matches) == 1 else
        f'<a class="intake-detail-link" href="{html.escape(str(evidence["historyHref"]), quote=True)}">'
        f'{len(matches)} intake runs</a>'
    )
    if len(matches) > 1:
        return direct_link + f'<div class="preparation-evidence preparation-{state}">Preparation: {summary}</div>'
    return (
        direct_link +
        f'<details class="preparation-evidence preparation-{state}">'
        f'<summary>Preparation: {summary}</summary>'
        '<p>Retained original, crops, eraser masks, skipped steps and recommendation. '
        'Comparison only; not proof of publication.</p>'
        f'<ul>{"".join(entries)}</ul></details>'
    )
