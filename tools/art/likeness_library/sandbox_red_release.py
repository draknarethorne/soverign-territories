"""Bound Sandbox-only red release experiment; never changes workflow consumers."""
import argparse
import collections
import hashlib
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "art"))
import likeness  # noqa: E402
from likeness_library import (  # noqa: E402
    actions, metadata, normal_admission, normal_import, normal_products, normal_recap, normal_transaction,
    policy, rejections, report_assets, retained_preparation,
)


def moves_from_plan(snapshot, routing):
    evidence = {row["photoId"]: row for row in snapshot}
    decisions = routing["assignments"] + routing["held"]
    if (len(evidence) != len(snapshot) or len(decisions) != len(snapshot)
            or {row["photoId"] for row in decisions} != set(evidence)):
        raise ValueError("Sandbox red release does not conserve the saved candidates")
    moves = []
    for decision in decisions:
        row = evidence[decision["photoId"]]
        if decision.get("releaseBlocked") or decision.get("preserveStaged"):
            raise ValueError(f'{row["photoId"]}: blocked decision cannot be released')
        folder = decision.get("destination")
        review = decision.get("reviewDestination")
        if bool(folder) == bool(review):
            raise ValueError(f'{row["photoId"]}: exactly one destination is required')
        destination = f"{folder}/gallery" if folder else review
        target = f'{destination}/{pathlib.PurePosixPath(row["currentPath"]).name}'
        if target.casefold() == row["currentPath"].casefold():
            raise ValueError(f'{row["photoId"]}: release makes no progress')
        moves.append({
            "photoId": row["photoId"], "source": row["currentPath"],
            "destination": target,
            "sha256": row["nativeSha256"], "reason": decision["reason"],
        })
    return sorted(moves, key=lambda row: row["photoId"])


def report_html(root, rows, replacement):
    lines = [
        "<!doctype html><html><head><meta charset='utf-8'><title>Sandbox red release experiment</title></head><body>",
        "<h1>Sandbox red release experiment</h1>",
        "<p>Sandbox-only experiment. Shared workflows and Production were not changed. "
        "Workflow replacement and consumer coverage remain unverified; human review is required.</p>",
    ]
    for row in rows:
        target = normal_transaction.safe(root, row["destination"])
        lines.append(
            "<figure><a href='" + html.escape(target.as_uri(), quote=True) + "'>"
            "<img loading='lazy' style='max-width:250px;max-height:300px' src='"
            + html.escape(target.as_uri(), quote=True) + "'></a><figcaption>"
            + html.escape(row["photoId"] + ": " + row["source"] + " -> " + row["destination"])
            + (("<br>Saved " + html.escape(row["band"]) + " score: "
                + ("unavailable" if row["score"] is None else html.escape(str(row["score"]))))
               if "score" in row else "")
            + (("<br>Independent rival: " + html.escape(str(row["unscoredAssessment"]["bestRival"]))
                + "; score: " + html.escape(str(row["unscoredAssessment"]["bestRivalScore"]))
                + "; face-quality eligible: " + html.escape(str(row["unscoredAssessment"]["qualityEligible"]))
                + "; basis: " + html.escape(str(row["unscoredAssessment"]["basis"])))
               if row.get("unscoredAssessment") else "")
            + ("<br>Workflow-selected: replacement not applied." if row.get("workflowSelected") else "")
            + "<br>" + html.escape(row["reason"]) + "</figcaption></figure>"
        )
    for proposal in replacement:
        lines.append("<p>Workflow replacement proposal only: " + html.escape(
            proposal["photoId"] + " -> " + proposal["replacementPhotoId"]
        ) + "; no workflow was changed.</p>")
    return "\n".join(lines + ["</body></html>"])


def check_publication(root, journal, report):
    normal_transaction.verify(root, journal)
    data = json.loads(report.read_bytes())
    if data["kind"] != "sandbox-red-release-experiment" or data["root"] != str(root):
        raise ValueError("Sandbox red release report belongs to another operation")
    for relative, digest in data["unaffectedNativeSHA256"].items():
        if metadata.content_sha256(normal_transaction.safe(root, relative)) != digest:
            raise ValueError(f"unaffected Sandbox Gallery photo changed: {relative}")
    return data


class VerifiedRebaseSuccessor:
    """Read the pre-rebase state from an applied successor's bound recovery snapshot."""

    def __init__(self, root, receipt, *, retirement_journal=None, retirement_digest=None):
        from tools.art.likeness_library import normal_rebase

        self.root = pathlib.Path(root).resolve()
        self.receipt = normal_recap._under(self.root, pathlib.Path(receipt).absolute())
        self.receipt_bytes = self.receipt.read_bytes()
        if (retirement_journal is None) != (retirement_digest is None):
            raise ValueError("retirement journal and preview digest must be supplied together")
        self.retirement = None
        self.distinct_retirement_source = None
        self.retired_files = {}
        self.retired_folders = []
        if retirement_journal is None:
            self.saved = normal_rebase._check(self.root, self.receipt)
        else:
            from likeness_library import empty_retirement

            if not isinstance(retirement_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", retirement_digest):
                raise ValueError("invalid retirement preview digest")
            retirement_path = empty_retirement._path(self.root, retirement_journal)
            retirement_bytes = retirement_path.read_bytes()
            data = empty_retirement.verify_successor(
                self.root, retirement_journal, retirement_digest, self.receipt,
            )
            if retirement_path.read_bytes() != retirement_bytes or data != json.loads(retirement_bytes):
                raise ValueError("retirement journal changed during verification")
            self.retirement = {
                "journal": retirement_journal, "planSHA256": retirement_digest,
                "journalSHA256": hashlib.sha256(retirement_bytes).hexdigest(),
            }
            plan = data["plan"]
            if plan.get("correctedReceipt", plan["sourceReceipt"]) != plan["sourceReceipt"]:
                self.distinct_retirement_source = {
                    "receipt": str(empty_retirement._path(self.root, plan["sourceReceipt"])),
                    "receiptSHA256": plan["sourceReceiptSha256"],
                }
                self.retirement["sourceReceipt"] = self.distinct_retirement_source["receipt"]
                self.retirement["sourceReceiptSHA256"] = self.distinct_retirement_source["receiptSHA256"]
            self.retirement_bytes = retirement_bytes
            self.retirement_path = retirement_path
            for move in data["plan"]["moves"]:
                self.retired_folders.append(move["source"])
                for entry in move["entries"]:
                    if entry["path"] == ".":
                        continue
                    relative = move["source"] + "/" + entry["path"]
                    target = empty_retirement._path(self.root, move["destination"] + "/" + entry["path"])
                    key = relative.casefold()
                    if key in self.retired_files:
                        raise ValueError("ambiguous retired historical path")
                    self.retired_files[key] = (target, entry)
            self.saved = json.loads(self.receipt_bytes)
        if self.receipt.read_bytes() != self.receipt_bytes or self.saved != json.loads(self.receipt_bytes):
            raise ValueError("corrected rebase receipt changed during verification")
        self.journal_path = normal_recap._under(self.root, pathlib.Path(self.saved["journal"]).absolute())
        self.journal_bytes = self.journal_path.read_bytes()
        self.journal = (normal_transaction.verify(self.root, self.journal_path) if self.retirement is None
                        else json.loads(self.journal_bytes))
        if (self.journal != json.loads(self.journal_bytes)
                or self.journal.get("runId") != self.saved.get("runId")
                or self.journal.get("bindings") != self.saved.get("bindings")
                or self.journal.get("externalAfter") or self.journal.get("pendingFinalizer")):
            raise ValueError("corrected rebase journal is not bound to its receipt")
        self.backup = normal_recap._under(self.root, pathlib.Path(self.journal["backup"]).absolute())
        if self.root not in self.backup.parents:
            raise ValueError("corrected rebase recovery snapshot is outside Sandbox")
        self.manifest_path = normal_recap._under(self.root, self.backup / "manifest.json")
        self.manifest_bytes = self.manifest_path.read_bytes()
        if hashlib.sha256(self.manifest_bytes).hexdigest() != self.journal["backupManifestSHA256"]:
            raise ValueError("corrected rebase recovery manifest changed")
        self.before = {}
        archived_paths = set()
        for entry in json.loads(self.manifest_bytes)["entries"]:
            source = pathlib.Path(entry["source"])
            if not source.is_absolute() or source.resolve() != source or self.root not in source.parents:
                raise ValueError("corrected rebase recovery source is unsafe")
            relative = source.relative_to(self.root).as_posix()
            archived = normal_transaction.safe(self.backup, pathlib.PurePath(entry["backup"]).as_posix())
            digest = normal_recap._digest_value(entry["sha256"])
            if relative in self.before or archived in archived_paths:
                raise ValueError("corrected rebase recovery snapshot is ambiguous")
            self.before[relative] = (archived, digest)
            archived_paths.add(archived)
        self.touched = set(self.journal["after"]) | set(self.journal["removed"])
        for relative in self.touched:
            normal_transaction.safe(self.root, relative)
        if self.retirement is not None:
            self.touched_folded = {relative.casefold(): relative for relative in self.touched}
            self.before_folded = {relative.casefold(): entry for relative, entry in self.before.items()}
            if len(self.touched_folded) != len(self.touched) or len(self.before_folded) != len(self.before):
                raise ValueError("case-ambiguous corrected rebase recovery snapshot")
        self.observed = {}
        # Refuse recursive/overlapping snapshot views.
        if any(self.backup == normal_transaction.safe(self.root, relative)
               or self.backup in normal_transaction.safe(self.root, relative).parents for relative in self.touched):
            raise ValueError("corrected rebase modifies its own recovery snapshot")

    def read(self, path):
        path = normal_recap._under(self.root, pathlib.Path(path).absolute())
        relative = path.relative_to(self.root).as_posix()
        touched = (relative in self.touched if self.retirement is None
                   else relative.casefold() in self.touched_folded)
        if touched:
            entry = (self.before.get(relative) if self.retirement is None
                     else self.before_folded.get(relative.casefold()))
            if entry is None:
                payload, actual_path = None, None
            else:
                actual_path, expected = entry
                normal_recap._under(self.root, actual_path)
                try:
                    payload = actual_path.read_bytes()
                except FileNotFoundError as exc:
                    raise ValueError(f"corrected rebase recovery file missing: {relative}") from exc
                if hashlib.sha256(payload).hexdigest() != expected:
                    raise ValueError(f"corrected rebase recovery file changed: {relative}")
        else:
            retired = next((folder for folder in self.retired_folders
                            if relative.casefold().startswith((folder + "/").casefold())), None)
            entry = self.retired_files.get(relative.casefold()) if retired else None
            if retired and entry is None:
                payload, actual_path = None, None
            else:
                actual_path = entry[0] if entry else path
                if entry and entry[1]["directory"]:
                    raise ValueError(f"historical lineage path is not a file: {relative}")
                if actual_path.exists() and not actual_path.is_file():
                    raise ValueError(f"historical lineage path is not a file: {relative}")
                try:
                    payload = actual_path.read_bytes()
                except FileNotFoundError:
                    if entry:
                        raise ValueError(f"retired historical file missing: {relative}")
                    payload = None
                if entry and hashlib.sha256(payload).hexdigest() != entry[1]["sha256"]:
                    raise ValueError(f"retired historical file changed: {relative}")
        signature = None if payload is None else hashlib.sha256(payload).hexdigest()
        binding = (actual_path, signature)
        if relative in self.observed and self.observed[relative] != binding:
            raise ValueError(f"historical lineage changed during verification: {relative}")
        self.observed[relative] = binding
        return payload

    def required(self, path):
        payload = self.read(path)
        if payload is None:
            raise ValueError(f"historical lineage evidence missing: {path}")
        return payload

    def verify_unchanged(self):
        if (self.receipt.read_bytes() != self.receipt_bytes or self.journal_path.read_bytes() != self.journal_bytes
                or self.manifest_path.read_bytes() != self.manifest_bytes):
            raise ValueError("corrected rebase evidence changed during verification")
        if self.retirement is None:
            normal_transaction.verify(self.root, self.journal_path)
        else:
            from likeness_library import empty_retirement

            if self.retirement_path.read_bytes() != self.retirement_bytes:
                raise ValueError("retirement journal changed during verification")
            empty_retirement.verify_successor(
                self.root, self.retirement["journal"], self.retirement["planSHA256"], self.receipt,
            )
            if self.retirement_path.read_bytes() != self.retirement_bytes:
                raise ValueError("retirement journal changed during verification")
        for relative, (path, expected) in self.observed.items():
            if path is None:
                continue
            normal_recap._under(self.root, path)
            try:
                actual = metadata.content_sha256(path)
            except FileNotFoundError:
                actual = None
            if actual != expected:
                raise ValueError(f"historical lineage changed during verification: {relative}")


def verified_release_chain(root, reports, prior_run, continuation_runs, *, successor=None):
    """Verify earlier publications at their historical states using later snapshots."""
    run_ids = [prior_run, *continuation_runs]
    if len(set(run_ids)) != len(run_ids):
        raise ValueError("release lineage repeats a run")
    root = pathlib.Path(root).resolve()
    if successor is not None and (not isinstance(successor, VerifiedRebaseSuccessor) or successor.root != root):
        raise ValueError("unsupported corrected rebase successor")

    def read(path):
        return path.read_bytes() if successor is None else successor.required(path)

    def digest_file(path):
        if successor is None:
            return metadata.content_sha256(path) if path.is_file() else None
        payload = successor.read(path)
        return hashlib.sha256(payload).hexdigest() if payload is not None else None

    journals, publications, snapshots = [], [], []
    for run_id in run_ids:
        journal = normal_transaction.safe(root, f"{reports}/runs/{run_id}/publication-journal.json")
        report = normal_transaction.safe(root, f"{reports}/library/{run_id}/report.json")
        journal_bytes = read(journal)
        data = json.loads(journal_bytes)
        if (data.get("kind") != "normal-publication" or data.get("status") != "applied"
                or data.get("root") != str(root) or data.get("runId") != run_id
                or data.get("externalAfter") or data.get("pendingFinalizer")):
            raise ValueError(f"{run_id}: unsupported release lineage journal")
        report_bytes = read(report)
        report_data = json.loads(report_bytes)
        report_relative = report.relative_to(root).as_posix()
        if (report_data.get("kind") != "sandbox-red-release-experiment"
                or report_data.get("root") != str(root) or report_data.get("runId") != run_id
                or data["after"].get(report_relative) != hashlib.sha256(report_bytes).hexdigest()):
            raise ValueError(f"{run_id}: release report differs from its publication")
        backup = pathlib.Path(data["backup"]).resolve()
        if root not in backup.parents:
            raise ValueError(f"{run_id}: recovery snapshot is outside the library")
        manifest_bytes = read(backup / "manifest.json")
        if hashlib.sha256(manifest_bytes).hexdigest() != data["backupManifestSHA256"]:
            raise ValueError(f"{run_id}: recovery snapshot manifest changed")
        entries = {}
        for entry in json.loads(manifest_bytes)["entries"]:
            source = pathlib.Path(entry["source"])
            if not source.is_absolute() or source.resolve() != source or root not in source.parents:
                raise ValueError(f"{run_id}: invalid recovery snapshot source")
            relative = source.relative_to(root).as_posix()
            archived = normal_transaction.safe(backup, pathlib.PurePath(entry["backup"]).as_posix())
            if relative in entries:
                raise ValueError(f"{run_id}: duplicate recovery snapshot source")
            entries[relative] = (archived, entry["sha256"])
        journals.append((journal, journal_bytes, data))
        publications.append(report_data)
        snapshots.append(entries)

    def historical_digest(index, relative):
        normal_transaction.safe(root, relative)
        for later in range(index + 1, len(journals)):
            data = journals[later][2]
            if relative in data["after"] or relative in data["removed"]:
                entry = snapshots[later].get(relative)
                if entry is None:
                    return None
                archived, digest = entry
                if digest_file(archived) != digest:
                    raise ValueError(f"release recovery snapshot changed: {relative}")
                return digest
        path = normal_transaction.safe(root, relative)
        if successor is None and path.exists() and not path.is_file():
            raise ValueError(f"release lineage path is not a file: {relative}")
        return digest_file(path)

    for index, (_, _, data) in enumerate(journals):
        for relative, expected in data["after"].items():
            if historical_digest(index, relative) != expected:
                raise ValueError(f"release lineage published content changed: {relative}")
        for relative in data["removed"]:
            if historical_digest(index, relative) is not None:
                raise ValueError(f"release lineage removed content reappeared: {relative}")
        for relative, expected in publications[index]["unaffectedNativeSHA256"].items():
            if historical_digest(index, relative) != expected:
                raise ValueError(f"release lineage unaffected native changed: {relative}")
        if index:
            if publications[index].get("planSHA256") != data["bindings"].get("planSHA256"):
                raise ValueError("continuation report differs from its preview binding")
            recorded = publications[index].get("lineageJournalSHA256")
            expected = [hashlib.sha256(content).hexdigest() for _, content, _ in journals[:index]]
            if recorded is not None and recorded != expected:
                raise ValueError("continuation report differs from its preceding journals")
            for move in publications[index]["moves"]:
                entry = snapshots[index].get(move["source"])
                if entry is None or entry[1] != move["sha256"] or digest_file(entry[0]) != entry[1]:
                    raise ValueError("continuation source differs from its recovery snapshot")
                if data["after"].get(move["destination"]) != move["sha256"]:
                    raise ValueError("continuation destination differs from its journal")
    for journal, content, _ in journals:
        if read(journal) != content:
            raise ValueError("release lineage changed during verification")
    if successor is not None:
        successor.verify_unchanged()
    return publications, [hashlib.sha256(content).hexdigest() for _, content, _ in journals]


def verified_current_lineage(root, receipt, audit, prior_run, current_review, snapshot, continuation_runs=(),
                             *, successor=None):
    """Conserve the original receipt through the checked prior Sandbox release."""
    root = pathlib.Path(root).resolve()
    if successor is not None and (not isinstance(successor, VerifiedRebaseSuccessor) or successor.root != root):
        raise ValueError("unsupported corrected rebase successor")

    def read(path):
        return path.read_bytes() if successor is None else successor.required(path)

    def digest(path):
        return hashlib.sha256(read(path)).hexdigest()

    receipt = normal_recap._under(root, pathlib.Path(receipt).absolute())
    audit = normal_recap._under(root, pathlib.Path(audit).absolute())
    review = normal_recap._under(root, pathlib.Path(current_review).absolute() / "people_gallery_review.html")
    reports = likeness.cw.storage_root(likeness.cw.load_cfg(), "reports", root=root).relative_to(root).as_posix()
    if successor is not None and (successor.receipt == receipt
                                  or successor.saved.get("runId") in {prior_run, *continuation_runs}):
        raise ValueError("corrected rebase must be a distinct successor")
    journal = normal_transaction.safe(root, f"{reports}/runs/{prior_run}/publication-journal.json")
    prior_report = normal_transaction.safe(root, f"{reports}/library/{prior_run}/report.json")
    if continuation_runs or successor is not None:
        if successor is None:
            publications, journal_hashes = verified_release_chain(root, reports, prior_run, continuation_runs)
        else:
            publications, journal_hashes = verified_release_chain(
                root, reports, prior_run, continuation_runs, successor=successor,
            )
        prior = publications[0]
    else:
        prior = check_publication(root, journal, prior_report)
        publications = [prior]
        journal_hashes = [metadata.content_sha256(journal)]
    journal_bytes = read(journal)
    journal_data = json.loads(journal_bytes)
    if journal_data.get("runId") != prior_run or prior.get("runId") != prior_run:
        raise ValueError("previous release run ID differs from its journal")
    manifest_path = normal_recap._under(root, audit.with_suffix(".report.json"))
    manifest_bytes = read(manifest_path)
    manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
    if (manifest_hash != prior.get("snapshotReportManifestSHA256")
            or manifest_hash != journal_data.get("bindings", {}).get("snapshotReportManifestSHA256")):
        raise ValueError("previous release is not bound to the supplied audit manifest")
    manifest = json.loads(manifest_bytes)
    receipt_hash = digest(receipt)
    if (manifest.get("receipt") != str(receipt)
            or manifest.get("inputs", {}).get(str(receipt)) != receipt_hash):
        raise ValueError("original receipt differs from the previous release evidence")
    original = (normal_recap.collect(receipt) if successor is None
                else normal_recap.collect(receipt, read_bytes=successor.read))
    if (original["status"] != "applied" or pathlib.Path(original["workingRoot"]).resolve() != root
            or original["snapshotDiagnostics"] or original["snapshotIdUnavailable"]
            or any(manifest["inputs"].get(path) != digest for path, digest in original["inputs"].items())):
        raise ValueError("original receipt and saved Review do not match previous release evidence")
    original_by_id = {}
    for item in original["auditRecords"]:
        row = item["row"]
        if row["photoId"] in original_by_id:
            raise ValueError("original receipt has ambiguous current photo IDs")
        original_by_id[row["photoId"]] = (row["destination"], row["preparedSHA256"])
    old_candidates = {row["photoId"]: row for row in manifest["redCandidates"]}
    moves = prior["moves"]
    if len(old_candidates) != len(manifest["redCandidates"]) or len(moves) != len(old_candidates):
        raise ValueError("previous release does not conserve its original candidates")
    moved = set()
    for move in moves:
        photo_id = move["photoId"]
        saved = old_candidates.get(photo_id)
        if (photo_id in moved or saved is None or original_by_id.get(photo_id) !=
                (move["source"], move["sha256"]) or saved["currentPath"] != move["source"]
                or saved["nativeSha256"] != move["sha256"]):
            raise ValueError(f"{photo_id}: previous release differs from original receipt")
        moved.add(photo_id)
        original_by_id[photo_id] = (move["destination"], move["sha256"])
    released_ids = set(moved)
    for continuation in publications[1:]:
        if continuation.get("snapshotReportManifestSHA256") != manifest_hash:
            raise ValueError("continuation is bound to another original audit")
        moved = set()
        for move in continuation["moves"]:
            photo_id = move["photoId"]
            if photo_id in moved or original_by_id.get(photo_id) != (move["source"], move["sha256"]):
                raise ValueError(f"{photo_id}: continuation differs from preceding lineage")
            moved.add(photo_id)
            original_by_id[photo_id] = (move["destination"], move["sha256"])
        released_ids.update(moved)
    review_bytes = read(review)
    if hashlib.sha256(review_bytes).hexdigest() != snapshot["reviewSHA256"]:
        raise ValueError("current Review differs from the verified snapshot")
    current = normal_recap._script(review_bytes.decode("utf-8"), "review-data")
    if not isinstance(current, list):
        raise ValueError("current Review has no photo census")
    current_by_id = {}
    for row in current:
        photo_id = row.get("photoId")
        if not photo_id or photo_id in current_by_id:
            raise ValueError("current Review has ambiguous photo IDs")
        current_by_id[photo_id] = (row.get("generationSource"), row.get("contentSha256"))
    if current_by_id != original_by_id:
        raise ValueError("current Review does not conserve the original receipt and previous release")
    if successor is not None:
        plan = successor.saved["plan"]
        rows = plan["sourceRows"]
        if not isinstance(rows, list) or not isinstance(plan["sourceHashes"], dict):
            raise ValueError("corrected rebase has no complete source census")
        source_rows = {row["source"]: row for row in rows}
        id_counts = collections.Counter(row["photoId"] for row in rows)
        if len(source_rows) != len(rows) or successor.saved.get("sourceHashes", plan["sourceHashes"]) != plan["sourceHashes"]:
            raise ValueError("corrected rebase source census is ambiguous")
        for photo_id in released_ids:
            path, expected = current_by_id[photo_id]
            row = source_rows.get(path)
            if (row is None or row.get("photoId") != photo_id or row.get("sourceHash") != expected
                    or plan["sourceHashes"].get(path) != expected or id_counts[photo_id] != 1):
                raise ValueError(f"{photo_id}: corrected rebase is unrelated or ambiguous for released photo")
    saved_receipt = json.loads(read(receipt))
    nonvoting = {}
    original_by_source = {item["row"]["source"]: item["row"] for item in original["auditRecords"]}
    for source in saved_receipt["plan"]["sourceRows"]:
        if source.get("sourceStatus") != "same-content-nonvoting":
            continue
        row = original_by_source[source["source"]]
        if row["newPerson"].split("/", 1)[0] not in {"Sisters", "Angels", "Models", "Prospects", "Potentials"}:
            continue
        if (row["newBucket"] != "gallery" or row["destination"] != source["source"]
                or row["preparedSHA256"] != source["sourceHash"]):
            raise ValueError("original non-voting Gallery disposition changed")
        current = current_by_id.get(row["photoId"])
        if current != (row["destination"], row["preparedSHA256"]):
            if (not current or current[1] != row["preparedSHA256"]
                    or not current[0].startswith("Various/review/")):
                raise ValueError("moved non-voting Gallery photo is not in an unassigned hold")
            continue
        path = normal_transaction.safe(root, row["destination"])
        if digest(path) != row["preparedSHA256"]:
            raise ValueError(f"non-voting Gallery native changed: {row['destination']}")
        nonvoting[row["destination"]] = row["preparedSHA256"]
    if (read(journal) != journal_bytes or read(manifest_path) != manifest_bytes
            or digest(receipt) != receipt_hash or read(review) != review_bytes):
        raise ValueError("current release lineage changed during verification")
    if successor is not None:
        successor.verify_unchanged()
    return {
        "nonvotingBindings": nonvoting, "receiptSHA256": receipt_hash,
        "priorJournalSHA256": hashlib.sha256(journal_bytes).hexdigest(),
        "continuationJournalSHA256": journal_hashes[1:],
        "priorManifestSHA256": manifest_hash, "currentReviewSHA256": snapshot["reviewSHA256"],
        "conservedCount": len(current_by_id), "priorManifest": manifest,
    }


def hold_for_incomplete_rivals(routing, diagnostics):
    if any(not diagnostic.endswith(": no eligible identity core; skipped") for diagnostic in diagnostics):
        raise ValueError("current release has unresolved frozen-core diagnostics: " + "; ".join(diagnostics))
    if not diagnostics:
        return
    held = []
    for row in routing["assignments"] + routing["held"]:
        if row.get("releaseBlocked") or row.get("preserveStaged"):
            held.append(row)
            continue
        row.pop("destination", None)
        row.pop("destinationType", None)
        row["reviewDestination"] = "Various/review"
        row["releaseHold"] = True
        row["preserveStaged"] = False
        row["referenceEligible"] = False
        row["reason"] += "; incomplete rival cores require an unassigned hold"
        if row.get("unscoredAssessment"):
            row["unscoredAssessment"]["basis"] += "; available rivals only, other identities have no eligible core"
        held.append(row)
    routing["assignments"] = []
    routing["held"] = sorted(held, key=lambda row: row["photoId"])
    routing["heldCount"] = len(held)
    routing["rivalCoreDiagnostics"] = sorted(diagnostics)


def checked_current_routing(root, cfg, rules, cache, receipt, snapshot, lineage, run_id):
    """Rebuild the complete current rival inventory and plan an isolated Sandbox release."""
    centering = normal_admission._verify_red_centering_population(
        receipt, root, cache, cfg, rules, lineage["priorManifest"],
    )
    inventory = normal_admission.frozen_red_gallery_inventory(
        likeness, root, cfg, rules, cache, nonvoting_paths=lineage["nonvotingBindings"],
        collapse_identical_same_owner=True,
    )
    if any(not diagnostic.endswith(": no eligible identity core; skipped")
           for diagnostic in inventory["diagnostics"]):
        raise ValueError("current release has unresolved frozen-core diagnostics: "
                         + "; ".join(inventory["diagnostics"]))
    scored = [row for row in snapshot["snapshotCandidates"] if row["score"] is not None]
    unscored = [row for row in snapshot["snapshotCandidates"] if row["score"] is None]
    _, cache_hash, vectors, model_ids, measurements = normal_admission._red_cache_vectors(
        root, cache, {row["nativeSha256"] for row in scored},
    )
    review_proof = snapshot["reviewMeasurementProof"]
    if (cache_hash != inventory["cacheSHA256"] or cache_hash != review_proof["cacheSHA256"]
            or cache_hash != centering["cacheSHA256"]
            or (scored and (sorted(model_ids) != inventory["modelIds"]
                            or sorted(model_ids) != review_proof["modelIds"]))):
        raise ValueError("current release cache or model differs between Review and routing")
    if inventory["modelIds"] != centering["modelIds"]:
        raise ValueError("current release centering model differs from routing")
    catalog_path = normal_transaction.safe(root, ".likeness-library.json")
    catalog = metadata.load_catalog(catalog_path)
    if metadata.content_sha256(catalog_path) != inventory["catalogSHA256"]:
        raise ValueError("current release catalogue changed after inventory")
    protected = {person["folder"] for person in catalog["people"].values() if person.get("protected")}
    settings = policy.effective_settings(cfg, rules)
    if unscored:
        measured = normal_admission.measure_unscored_release_candidates(likeness, root, cache, unscored, settings)
        if measured["cacheSHA256"] != cache_hash or measured["modelIds"] != inventory["modelIds"]:
            raise ValueError("unscored candidate measurements differ from the frozen inventory")
        for item in measured["candidates"]:
            vectors[item["sha256"]] = item["vector"]
            measurements[item["sha256"]] = item["measurement"]
    candidates = []
    for row in snapshot["snapshotCandidates"]:
        photo_id, digest, owner = row["photoId"], row["nativeSha256"], row["owner"]
        record = catalog["photos"].get(photo_id, {})
        if record and record["contentSha256"] != digest:
            raise ValueError(f"{photo_id}: current release catalogue content is stale")
        candidates.append({
            "photoId": photo_id, "sourceFolder": owner, "sourceBucket": row["bucket"].title(),
            "currentPath": row["currentPath"], "sha256": digest, "redScore": row["score"],
            "side": "Prospects", "vector": vectors[digest],
            "qualityEligible": normal_admission._red_measurement_quality(measurements[digest], settings, photo_id),
            "protected": bool(record.get("protected")), "identityProtected": owner in protected,
            "nonVoting": row["currentPath"] in lineage["nonvotingBindings"],
            **rejections.candidate_state(catalog, photo_id, digest),
        })
    proof = normal_admission.verify_red_routing_measurements(
        root, cache, [row for row in candidates if row["redScore"] is not None],
        inventory["references"], inventory["referencePaths"], settings,
    )
    folders = list(likeness.cw.photo_folders(cfg, root))
    routing = normal_admission.red_release_plan(
        likeness, candidates, inventory["cores"], inventory["references"], settings, rules,
        {name for _, name, _ in folders}, snapshot_bands=rules["scoreBands"],
        snapshot_candidates=snapshot["snapshotCandidates"], selected_ids=set(),
        release_bands=snapshot["releaseBands"], allow_empty_source_cores=True,
        include_unscored=bool(unscored),
    )
    hold_for_incomplete_rivals(routing, inventory["diagnostics"])
    moves = moves_from_plan(snapshot["snapshotCandidates"], routing)
    normal_admission.red_release_routed_catalog(catalog, moves, snapshot["snapshotCandidates"], rules, routing)
    transfers = []
    for move in moves:
        target = normal_transaction.safe(root, move["destination"])
        if target.exists() or target.is_symlink():
            raise ValueError(f'current release destination already exists: {move["destination"]}')
        transfer = retained_preparation.plan_transfer(root, move["source"], move["destination"], generation=run_id)
        if not transfer:
            if lineage["nonvotingBindings"].get(move["source"]) != move["sha256"]:
                raise ValueError(f'current release lacks retained preparation: {move["source"]}')
            move["unpreparedNonVoting"] = True
        else:
            transfers.append(transfer)
    retained_preparation.validate_transfers(root, transfers)
    if (proof["cacheSHA256"] != cache_hash or proof["modelIds"] != inventory["modelIds"]
            or metadata.content_sha256(catalog_path) != inventory["catalogSHA256"]
            or list(likeness.cw.photo_folders(cfg, root)) != folders):
        raise ValueError("current release routing evidence changed during planning")
    workflow_ids = actions.selected_photo_ids(cfg)
    workflow_selected = sorted(
        row["photoId"] for row in snapshot["snapshotCandidates"]
        if row.get("workflowSelected") or row["photoId"] in workflow_ids
    )
    return {
        "moves": moves, "routing": routing, "inventory": inventory,
        "catalog": catalog, "routingProof": proof, "workflowSelected": workflow_selected,
        "cacheSHA256": cache_hash, "centeringProof": centering, "measurements": measurements,
        "measurementSHA256": hashlib.sha256(json.dumps(
            {row["sha256"]: measurements[row["sha256"]] for row in candidates},
            sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode()).hexdigest(),
    }


def current_plan_binding(root, run_id, snapshot, lineage, plan):
    from likeness_library import planner, protection, reconciliation, scoring

    producers = [pathlib.Path(__file__)]
    for module in (
        likeness, actions, metadata, normal_admission, normal_import, normal_products, normal_recap,
        normal_transaction, planner, policy, protection, reconciliation, rejections, report_assets,
        retained_preparation, scoring,
    ):
        if module.__file__ is None:
            raise ValueError(f"release producer has no file: {module.__name__}")
        producers.append(pathlib.Path(module.__file__))
    binding = {
        "root": str(root), "runId": run_id, "releaseBands": snapshot["releaseBands"],
        "reviewSHA256": snapshot["reviewSHA256"], "reportStateSHA256": snapshot["reportStateSHA256"],
        "receiptSHA256": lineage["receiptSHA256"], "priorJournalSHA256": lineage["priorJournalSHA256"],
        "continuationJournalSHA256": lineage.get("continuationJournalSHA256", []),
        "priorManifestSHA256": lineage["priorManifestSHA256"], "cacheSHA256": plan["cacheSHA256"],
        "catalogSHA256": plan["inventory"]["catalogSHA256"], "moves": plan["moves"],
        "includeUnscored": bool(any(row["score"] is None for row in snapshot["snapshotCandidates"])),
        "measurementSHA256": plan["measurementSHA256"],
        "unscoredAssessments": {
            row["photoId"]: row["unscoredAssessment"]
            for row in plan["routing"]["assignments"] + plan["routing"]["held"]
            if row.get("unscoredAssessment")
        },
        "emptySourceCores": plan["routing"]["emptySourceCores"], "workflowSelected": plan["workflowSelected"],
        "rivalCoreDiagnostics": plan["routing"].get("rivalCoreDiagnostics", []),
        "producer": {str(path): metadata.content_sha256(path) for path in producers},
    }
    return binding, hashlib.sha256(json.dumps(binding, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def publish_current_release(root, cfg, rules, args, snapshot, lineage, plan, plan_binding, plan_hash):
    if not plan["moves"]:
        raise ValueError("current release makes no progress: no moves to publish")
    reports = likeness.cw.storage_root(cfg, "reports", root=root).relative_to(root).as_posix()
    run = normal_transaction.safe(root, f"{reports}/runs/{args.run_id}")
    report_relative = f"{reports}/library/{args.run_id}"
    if run.exists() or normal_transaction.safe(root, report_relative).exists():
        raise ValueError("current release run or report already exists; preserve and inspect")
    cache_path = pathlib.Path(args.cache)
    cache_hash = metadata.content_sha256(cache_path)
    measurements = plan["measurements"]
    if cache_hash != plan["cacheSHA256"]:
        raise ValueError("current release cache changed after preview")
    photos = []
    for move in plan["moves"]:
        parts = pathlib.PurePosixPath(move["source"]).parts
        photos.append(likeness.Photo(
            normal_transaction.safe(root, move["source"]), parts[0], parts[1],
            move["sha256"], measurements[move["sha256"]],
        ))
    run.mkdir(parents=True, exist_ok=False)
    stage = run / "publication"
    published, _, removed = normal_products.stage(
        root, stage, plan["moves"], None, profile="lean", photos=photos, cfg=cfg,
        catalog=plan["catalog"], policy=rules, red_snapshot_candidates=snapshot["snapshotCandidates"],
        red_routing_plan=plan["routing"],
    )
    report_dir = normal_transaction.safe(stage, report_relative)
    report_dir.mkdir(parents=True, exist_ok=False)
    by_id = {row["photoId"]: row for row in snapshot["snapshotCandidates"]}
    decisions = {row["photoId"]: row for row in plan["routing"]["assignments"] + plan["routing"]["held"]}
    selected_ids = set(plan["workflowSelected"])
    report_moves = [{
        **move, "score": by_id[move["photoId"]]["score"],
        "band": (policy.score_band(by_id[move["photoId"]]["score"], rules)
                 if by_id[move["photoId"]]["score"] is not None else "unscored"),
        **({"unscoredAssessment": decisions[move["photoId"]]["unscoredAssessment"]}
           if decisions[move["photoId"]].get("unscoredAssessment") else {}),
        "scoreContext": by_id[move["photoId"]]["scoreContext"],
        "comparison": by_id[move["photoId"]]["comparison"],
        "workflowSelected": move["photoId"] in selected_ids,
    } for move in plan["moves"]]
    moved_sources = {row["source"] for row in plan["moves"]}
    report_data = {
        "kind": "sandbox-red-release-experiment", "root": str(root), "runId": args.run_id,
        "moves": report_moves, "publishedNative": published, "releaseBands": snapshot["releaseBands"],
        "workflowChangesApplied": False, "consumerCoverageVerified": False,
        "workflowSelected": plan["workflowSelected"], "workflowReplacementProposals": [],
        "emptySourceCores": plan["routing"]["emptySourceCores"], "planSHA256": plan_hash,
        "lineageJournalSHA256": [lineage["priorJournalSHA256"], *lineage.get("continuationJournalSHA256", [])],
        "snapshotReportManifestSHA256": lineage["priorManifestSHA256"],
        "unaffectedNativeSHA256": {
            path: digest for path, digest in snapshot["allNativeBindings"].items() if path not in moved_sources
        },
    }
    (report_dir / "report.json").write_text(json.dumps(report_data, indent=2) + "\n", encoding="utf-8")
    (report_dir / "index.html").write_text(report_html(root, report_moves, []), encoding="utf-8")
    again = normal_admission.verified_current_release_snapshot(
        root, args.current_review, args.cache, cfg, rules, release_bands=snapshot["releaseBands"],
        include_unscored=any(row["score"] is None for row in snapshot["snapshotCandidates"]),
    )
    again_lineage = verified_current_lineage(
        root, args.receipt, args.report, args.prior_run, args.current_review, again,
        getattr(args, "continuation_run", ()),
    )
    if (again != snapshot or any(again_lineage[key] != lineage[key] for key in (
            "receiptSHA256", "priorJournalSHA256", "continuationJournalSHA256",
            "priorManifestSHA256", "currentReviewSHA256",
            "nonvotingBindings",
    )) or current_plan_binding(root, args.run_id, snapshot, lineage, plan)[0] != plan_binding):
        raise ValueError("current release evidence or implementation changed during staging")
    expected = {}
    for bindings in (plan["inventory"]["nativeBindings"], snapshot["nativeBindings"], removed,
                     {".likeness-library.json": plan["inventory"]["catalogSHA256"]}):
        for path, digest in bindings.items():
            if path in expected and expected[path] != digest:
                raise ValueError(f"current release has conflicting source bindings: {path}")
            expected[path] = digest
    staged = [path.relative_to(stage).as_posix() for path in stage.rglob("*") if path.is_file()]
    exclusive = {relative for relative in staged if not normal_transaction.safe(root, relative).exists()}
    exclusive.update(row["destination"] for row in plan["moves"])
    normal_transaction.publish(
        root, stage, [row["source"] for row in plan["moves"]] + list(removed),
        journal=run / "publication-journal.json", bindings={"planSHA256": plan_hash},
        profile="lean", run_id=args.run_id, expected_sources=expected, exclusive_targets=exclusive,
    )
    check_publication(root, run / "publication-journal.json",
                      normal_transaction.safe(root, f"{report_relative}/report.json"))
    print(f"Sandbox release published and checked: {root / pathlib.PurePosixPath(report_relative) / 'index.html'}")
    print("Workflow selections were not changed; replacement and consumer coverage remain unresolved.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--receipt")
    parser.add_argument("--report")
    parser.add_argument("--cache")
    parser.add_argument("--current-review", help="reports-only output directory for a read-only candidate census")
    parser.add_argument("--release-band", action="append", choices=("red", "orange"),
                        help="score band to select; repeat for both")
    parser.add_argument("--include-unscored", action="store_true",
                        help="include unavailable own-core scores in the Sandbox release")
    parser.add_argument("--prior-run", help="previous Sandbox release run for current-review lineage")
    parser.add_argument("--continuation-run", action="append", default=[],
                        help="later Sandbox release in chronological order; repeat for each continuation")
    parser.add_argument("--expected-plan-sha256", help="exact preview binding required for current-review apply")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--recover", action="store_true")
    mode.add_argument("--recover-apply", action="store_true")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", args.run_id):
        parser.error("--run-id must be a simple run identifier")
    if not pathlib.Path(args.root).is_absolute():
        parser.error("--root must be absolute")
    cfg = likeness.cw.load_cfg()
    root = pathlib.Path(args.root).resolve()
    if root != pathlib.Path(likeness.cw.sandbox_work_root(cfg)).resolve():
        raise ValueError("Sandbox red release requires the configured Sandbox Working root")
    if args.current_review:
        if args.check or args.recover or args.recover_apply:
            parser.error("--current-review is for census, preview or apply, not check or recovery")
        if not args.cache:
            parser.error("--current-review requires --cache")
        if not args.prior_run:
            if args.apply or args.receipt or args.report or args.expected_plan_sha256 or args.continuation_run:
                parser.error("current-review census is read-only; routing requires --prior-run, --receipt and --report")
        elif not all((args.receipt, args.report)):
            parser.error("current-review routing requires --prior-run, --receipt and --report")
        if args.prior_run and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", args.prior_run):
            parser.error("--prior-run must be a simple run identifier")
        if any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", run) for run in args.continuation_run):
            parser.error("--continuation-run must be a simple run identifier")
        if args.apply and (not args.expected_plan_sha256
                           or not re.fullmatch(r"[0-9a-f]{64}", args.expected_plan_sha256)):
            parser.error("current-review apply requires --expected-plan-sha256 from its preview")
        if not args.apply and args.expected_plan_sha256:
            parser.error("--expected-plan-sha256 is only valid with --apply")
        rules = policy.load_policy()
        snapshot = normal_admission.verified_current_release_snapshot(
            root, args.current_review, args.cache, cfg, rules,
            release_bands=args.release_band or ("red",),
            include_unscored=args.include_unscored,
        )
        candidates = snapshot["snapshotCandidates"]
        print(f"Selected bands: {', '.join(snapshot['releaseBands'])}")
        print(f"Candidates: {len(candidates)}; Gallery: {sum(row['bucket'] == 'gallery' for row in candidates)}; "
              f"Review: {sum(row['bucket'] == 'review' for row in candidates)}")
        print(f"Unavailable named-person scores: {len(snapshot['unavailableIds'])}")
        print(f"Selected unavailable scores: {sum(row['score'] is None for row in candidates)}")
        print(f"Saved workflow-selected candidates: {sum(bool(row.get('workflowSelected')) for row in candidates)}")
        print(f"Verified score count: {snapshot['reviewMeasurementProof']['scoreCount']}")
        print(f"Review SHA-256: {snapshot['reviewSHA256']}")
        if not args.prior_run:
            print("READ-ONLY CENSUS: no routing, workflow replacement or release was performed")
            return 0
        lineage = verified_current_lineage(
            root, args.receipt, args.report, args.prior_run, args.current_review, snapshot,
            args.continuation_run,
        )
        plan = checked_current_routing(root, cfg, rules, args.cache, args.receipt, snapshot, lineage, args.run_id)
        binding, plan_hash = current_plan_binding(root, args.run_id, snapshot, lineage, plan)
        print(f"Conserved current photos: {lineage['conservedCount']}")
        print(f"Empty former matcher cores: {len(plan['routing']['emptySourceCores'])}")
        for diagnostic in plan["routing"].get("rivalCoreDiagnostics", []):
            print(f"Incomplete rival inventory: {diagnostic}")
        print(f"Workflow-selected candidates without replacement: {len(plan['workflowSelected'])}")
        decisions = {row["photoId"]: row for row in plan["routing"]["assignments"] + plan["routing"]["held"]}
        for move in plan["moves"]:
            print(f'{move["photoId"]}: {move["source"]} -> {move["destination"]}: {move["reason"]}')
            assessment = decisions[move["photoId"]].get("unscoredAssessment")
            if assessment:
                print(f'  independent rival: {assessment["bestRival"]}; score: {assessment["bestRivalScore"]}; '
                      f'face-quality eligible: {assessment["qualityEligible"]}; basis: {assessment["basis"]}')
        print(f"PLAN SHA-256: {plan_hash}")
        if not args.apply:
            print("Preview only; no files changed. Shared workflows and Production will not be modified.")
            return 0
        if plan_hash != args.expected_plan_sha256:
            raise ValueError("current release differs from the authorized preview; refuse apply")
        publish_current_release(root, cfg, rules, args, snapshot, lineage, plan, binding, plan_hash)
        return 0
    if args.release_band or args.include_unscored or args.prior_run or args.continuation_run or args.expected_plan_sha256:
        parser.error("release selection and lineage options require --current-review")
    reports = likeness.cw.storage_root(cfg, "reports", root=root).relative_to(root).as_posix()
    run = normal_transaction.safe(root, f"{reports}/runs/{args.run_id}")
    report_relative = f"{reports}/library/{args.run_id}"
    report = normal_transaction.safe(root, f"{report_relative}/report.json")
    journal = run / "publication-journal.json"
    if args.check:
        check_publication(root, journal, report)
        print(f"Sandbox red release publication checked: {journal}")
        return 0
    if args.recover or args.recover_apply:
        normal_transaction.recover(root, journal, apply=args.recover_apply)
        print(f"Sandbox red release recovery {'applied' if args.recover_apply else 'previewed'}: {journal}")
        return 0
    if not all((args.receipt, args.report, args.cache)):
        parser.error("--receipt, --report and --cache are required for preview and apply")
    if run.exists():
        raise ValueError(f"Sandbox red release run already exists; preserve and inspect: {run}")
    if normal_transaction.safe(root, report_relative).exists():
        raise ValueError("Sandbox red release report directory already exists; preserve and inspect")
    rules = policy.load_policy()
    diagnostic = normal_admission.checked_red_release_diagnostic(
        likeness, root, cfg, rules, args.cache, receipt=args.receipt, report=args.report,
        simulate_all=True, simulate_core_refresh=True, simulate_destination_scores=True,
    )
    snapshot = normal_admission.verified_red_snapshot(
        args.receipt, args.report, root, rules, diagnostic_workflow_gaps=True,
    )
    routing = diagnostic["hypotheticalRouting"]
    moves = moves_from_plan(snapshot["snapshotCandidates"], routing)
    catalog_path = normal_transaction.safe(root, ".likeness-library.json")
    catalog = metadata.load_catalog(catalog_path)
    normal_admission.red_release_routed_catalog(
        catalog, moves, snapshot["snapshotCandidates"], rules, routing,
    )
    print("SANDBOX-ONLY EXPERIMENT: no Production or workflow consumer changes")
    for move in moves:
        print(f'{move["photoId"]}: {move["source"]} -> {move["destination"]}: {move["reason"]}')
    print("Workflow replacement and other-machine consumer coverage remain unresolved.")
    if not args.apply:
        print("Preview only; no files changed.")
        return 0

    cache_path, cache_hash, _, _, measurements = normal_admission._red_cache_vectors(
        root, args.cache, {row["sha256"] for row in moves},
    )
    if cache_hash != diagnostic["galleryInventoryProof"]["cacheSHA256"]:
        raise ValueError("Sandbox red release cache changed after planning")
    photos = []
    for move in moves:
        source = normal_transaction.safe(root, move["source"])
        parts = pathlib.PurePosixPath(move["source"]).parts
        photos.append(likeness.Photo(source, parts[0], parts[1], move["sha256"], measurements[move["sha256"]]))
    run.mkdir(parents=True, exist_ok=False)
    stage = run / "publication"
    published, _, removed = normal_products.stage(
        root, stage, moves, None, profile="lean", photos=photos, cfg=cfg, catalog=catalog, policy=rules,
        red_snapshot_candidates=snapshot["snapshotCandidates"], red_routing_plan=routing,
    )
    report_dir = normal_transaction.safe(stage, report_relative)
    report_dir.mkdir(parents=True, exist_ok=False)
    proposals = [row for row in diagnostic["workflowReplacementProposals"] if row["state"] == "proposed"]
    report_data = {
        "kind": "sandbox-red-release-experiment", "root": str(root), "runId": args.run_id,
        "moves": moves, "publishedNative": published, "workflowReplacementProposals": [
            {"photoId": row["photoId"], "replacementPhotoId": row["replacementPhotoId"],
             "replacementScore": row["replacementScore"]} for row in proposals
        ],
        "workflowChangesApplied": False, "consumerCoverageVerified": False,
        "hypotheticalReviewCensus": diagnostic["hypotheticalReviewCensus"],
        "snapshotReportManifestSHA256": snapshot["reportManifestSHA256"],
        "unaffectedNativeSHA256": {
            path: digest for path, digest in diagnostic["galleryInventoryProof"]["nativeBindings"].items()
            if path not in {row["source"] for row in moves}
        },
    }
    (report_dir / "report.json").write_text(json.dumps(report_data, indent=2) + "\n", encoding="utf-8")
    (report_dir / "index.html").write_text(report_html(root, moves, proposals), encoding="utf-8")
    for path, digest in snapshot["inputBindings"].items():
        if metadata.content_sha256(pathlib.Path(path)) != digest:
            raise ValueError(f"Sandbox red snapshot changed before publication: {path}")
    if metadata.content_sha256(cache_path) != cache_hash:
        raise ValueError("Sandbox red cache changed before publication")
    expected = {
        **diagnostic["galleryInventoryProof"]["nativeBindings"], **removed,
        ".likeness-library.json": diagnostic["galleryInventoryProof"]["catalogSHA256"],
    }
    staged = [path.relative_to(stage).as_posix() for path in stage.rglob("*") if path.is_file()]
    exclusive = {relative for relative in staged if not normal_transaction.safe(root, relative).exists()}
    exclusive.update(row["destination"] for row in moves)
    exclusive.update(f"{report_relative}/{name}" for name in ("index.html", "report.json"))
    normal_transaction.publish(
        root, stage, [row["source"] for row in moves] + list(removed), journal=journal,
        bindings={"snapshotReportManifestSHA256": snapshot["reportManifestSHA256"], "cacheSHA256": cache_hash},
        profile="lean", run_id=args.run_id, expected_sources=expected, exclusive_targets=exclusive,
    )
    check_publication(root, journal, report)
    print(f"Sandbox experiment published and checked: {root / pathlib.PurePosixPath(report_relative) / 'index.html'}")
    print(f"Recovery journal: {journal}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
