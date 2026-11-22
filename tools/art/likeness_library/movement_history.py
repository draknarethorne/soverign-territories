"""Report-only history of an applied SIMPLE receipt and its Sandbox releases."""
import argparse
import collections
import hashlib
import html
import json
import pathlib
import re
import stat
import sys

if not __package__:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
    from tools.art.likeness_library import normal_recap, normal_transaction, rebase_recap, sandbox_red_release
else:
    from . import normal_recap, normal_transaction, rebase_recap, sandbox_red_release


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _id(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", value):
        raise ValueError(f"unsafe identifier: {value}")
    return value


def _discover(root, reports, manifest_hash, *, successor=None):
    """Find every saved release bound to this original audit, including orphans."""
    library = normal_transaction.safe(root, f"{reports}/library")
    found = set()
    if not library.is_dir():
        raise ValueError("release report directory missing")
    paths = set(library.glob("*/report.json"))
    if successor is not None:
        for relative in successor.before:
            path = normal_transaction.safe(root, relative)
            if path.name == "report.json" and path.parent.parent == library:
                paths.add(path)
    for path in sorted(paths):
        normal_recap._under(root, path.absolute())
        payload = path.read_bytes() if successor is None else successor.read(path)
        if payload is None:
            continue
        data = json.loads(payload)
        if (data.get("kind") == "sandbox-red-release-experiment"
                and data.get("snapshotReportManifestSHA256") == manifest_hash):
            run = _id(data["runId"])
            if path.parent.name != run or data.get("root") != str(root) or run in found:
                raise ValueError("ambiguous release report")
            journal = normal_transaction.safe(root, f"{reports}/runs/{run}/publication-journal.json")
            if (not journal.is_file() if successor is None else successor.read(journal) is None):
                raise ValueError(f"{run}: release journal missing")
            found.add(run)
    return found


def _bind_first_moves(root, reports, run, publication, *, successor=None):
    """Bind the initial release's native moves to its journal and recovery bytes."""
    journal_path = normal_transaction.safe(root, f"{reports}/runs/{run}/publication-journal.json")
    def read(path):
        return path.read_bytes() if successor is None else successor.required(path)

    journal = json.loads(read(journal_path))
    backup = pathlib.Path(journal["backup"]).resolve()
    if root not in backup.parents:
        raise ValueError(f"{run}: recovery snapshot outside Sandbox")
    manifest_path = normal_recap._under(root, backup / "manifest.json")
    manifest_bytes = read(manifest_path)
    if hashlib.sha256(manifest_bytes).hexdigest() != journal["backupManifestSHA256"]:
        raise ValueError(f"{run}: recovery snapshot manifest changed")
    entries = {}
    for entry in json.loads(manifest_bytes)["entries"]:
        source = pathlib.Path(entry["source"])
        if not source.is_absolute() or source.resolve() != source or root not in source.parents:
            raise ValueError(f"{run}: invalid recovery source")
        relative = source.relative_to(root).as_posix()
        if relative in entries:
            raise ValueError(f"{run}: duplicate recovery source")
        entries[relative] = entry
    for move in publication["moves"]:
        source, destination, expected = move["source"], move["destination"], move["sha256"]
        normal_transaction.safe(root, source)
        normal_transaction.safe(root, destination)
        entry = entries.get(source)
        if (source == destination or source not in journal["removed"]
                or journal["after"].get(destination) != expected or not entry or entry["sha256"] != expected):
            raise ValueError(f"{run}: first release move is not bound to journal and recovery")
        archived = normal_transaction.safe(backup, pathlib.PurePath(entry["backup"]).as_posix())
        if hashlib.sha256(read(archived)).hexdigest() != expected:
            raise ValueError(f"{run}: first release recovery photo changed: {source}")


def _ordered_lineage(publications, hashes, runs):
    """Allow a missing immediate binding only when a later report binds the full prefix."""
    for index in range(1, len(publications)):
        recorded = publications[index].get("lineageJournalSHA256")
        if recorded is not None and recorded != hashes[:index]:
            raise ValueError(f"{runs[index]}: changed ordered journal lineage")
    for index in range(1, len(publications)):
        recorded = publications[index].get("lineageJournalSHA256")
        if recorded is None and not any(
            publications[later].get("lineageJournalSHA256") == hashes[:later]
            for later in range(index + 1, len(publications))
        ):
            raise ValueError(f"{runs[index]}: missing or ambiguous ordered journal lineage")


def _corrected(root, receipt, records, expected_cohort, *, retirement_view=None):
    # Import the existing read-only applied-receipt checker, not its runner.
    from tools.art.likeness_library import normal_rebase

    receipt = normal_recap._under(root, pathlib.Path(receipt).absolute())
    receipt_hash = _sha(receipt)
    if retirement_view is None:
        saved = normal_rebase._check(root, receipt)
    else:
        if retirement_view.receipt != receipt or retirement_view.retirement is None:
            raise ValueError("unsupported retirement successor")
        retirement_view.verify_unchanged()
        saved = retirement_view.saved
    journal_path = normal_recap._under(root, pathlib.Path(saved["journal"]).absolute())
    journal_hash = _sha(journal_path)
    journal = (normal_transaction.verify(root, journal_path) if retirement_view is None
               else retirement_view.journal)
    if (journal.get("runId") != saved.get("runId") or journal.get("bindings") != saved.get("bindings")
            or journal.get("externalAfter") or journal.get("pendingFinalizer")):
        raise ValueError("corrected rebase journal is not bound to its receipt")
    backup = pathlib.Path(journal["backup"]).absolute()
    normal_recap._under(root, backup)
    manifest = normal_recap._under(root, backup / "manifest.json")
    if _sha(manifest) != journal["backupManifestSHA256"]:
        raise ValueError("corrected rebase recovery manifest changed")
    before = {}
    for entry in json.loads(manifest.read_bytes())["entries"]:
        source = pathlib.Path(entry["source"])
        if not source.is_absolute() or source.resolve() != source or root not in source.parents:
            raise ValueError("corrected rebase recovery source is unsafe")
        relative = source.relative_to(root).as_posix()
        if relative in before:
            raise ValueError("corrected rebase recovery source is ambiguous")
        before[relative] = entry
    corrected = normal_recap.collect(receipt)
    if (corrected["status"] != "applied" or pathlib.Path(corrected["workingRoot"]) != root
            or corrected["snapshotDiagnostics"] or corrected["snapshotIdUnavailable"]
            or corrected["physicalSources"] != len(corrected["rows"])):
        raise ValueError("corrected rebase receipt or Review census is incomplete")
    by_source = {}
    ids = collections.Counter()
    review_rows = {id(item["row"]) for item in corrected["auditRecords"]}
    for row in corrected["rows"]:
        normal_recap._relative(row["source"])
        if row["source"] in by_source:
            raise ValueError("corrected rebase has ambiguous source paths")
        by_source[row["source"]] = row
        ids[row["photoId"]] += 1
    cohort = {row["photoId"] for row, history, _, active in records if active and history}
    if expected_cohort is not None and len(cohort) != expected_cohort:
        raise ValueError(f"historical release cohort count {len(cohort)} differs from required {expected_cohort}")
    mapped = {}
    for row, history, final, active in records:
        if not active:
            continue
        candidate = by_source.get(final)
        matches = candidate is not None and candidate["photoId"] == row["photoId"] and candidate["sha256"] == row["preparedSHA256"]
        eligible = (matches and ids[row["photoId"]] == 1 and not candidate.get("supersededVersion")
                    and (id(candidate) in review_rows or candidate.get("duplicateArchive")
                         or candidate.get("junkDisposition")))
        if history and not eligible:
            raise ValueError(f'{row["photoId"]}: required cohort has missing, ambiguous or changed-hash corrected lineage')
        if not eligible:
            continue
        # A rebase source touched by publication must be proven by its recovery
        # snapshot; an untouched source must still contain the recorded bytes.
        if final in journal["after"] or final in journal["removed"]:
            entry = before.get(final)
            if not entry or entry["sha256"] != candidate["sha256"]:
                raise ValueError(f"{final}: corrected source lacks recovery binding")
            archived = normal_transaction.safe(backup, pathlib.PurePath(entry["backup"]).as_posix())
            if _sha(archived) != candidate["sha256"]:
                raise ValueError(f"{final}: corrected source recovery bytes changed")
        elif _sha(normal_transaction.safe(root, final)) != candidate["sha256"]:
            raise ValueError(f"{final}: untouched corrected source changed")
        destination = candidate["destination"]
        target = normal_transaction.safe(root, destination)
        expected = candidate["preparedSHA256"]
        if journal["after"].get(destination) != expected:
            if destination != final or _sha(target) != expected:
                raise ValueError(f"{destination}: corrected destination lacks publication binding")
        mapped[row["source"]] = candidate
    if sum(1 for row, history, _, active in records if active and history and row["source"] in mapped) != len(cohort):
        raise ValueError("corrected rebase does not conserve the required cohort")
    if (_sha(receipt) != receipt_hash or _sha(journal_path) != journal_hash
            or _sha(manifest) != journal["backupManifestSHA256"]
            or any(_sha(pathlib.Path(path)) != digest for path, digest in corrected["inputs"].items())):
        raise ValueError("corrected rebase changed during verification")
    result = {
        "runId": saved["runId"], "receipt": str(receipt), "receiptSHA256": receipt_hash,
        "journal": str(journal_path), "journalSHA256": journal_hash,
        "manifestSHA256": _sha(manifest), "inputs": corrected["inputs"], "mapped": mapped,
        "cohort": cohort, "cohortCount": len(cohort),
    }
    if retirement_view is not None:
        retirement_view.verify_unchanged()
        result["retirement"] = dict(retirement_view.retirement)
    return result


def collect(root, receipt, audit, review_dir, runs, reports, corrected_receipt=None, expected_cohort=None, *,
            retirement_journal=None, retirement_digest=None):
    root = pathlib.Path(root).absolute()
    if root.resolve() != root:
        raise ValueError("Sandbox root must be absolute and unlinked")
    runs = [_id(run) for run in runs]
    if not runs or len(set(runs)) != len(runs):
        raise ValueError("supply each release exactly once in chronological order")
    receipt = normal_recap._under(root, pathlib.Path(receipt).absolute())
    audit = normal_recap._under(root, pathlib.Path(audit).absolute())
    review_dir = normal_recap._under(root, pathlib.Path(review_dir).absolute())
    review = normal_recap._under(root, review_dir / "people_gallery_review.html")
    manifest = normal_recap._under(root, audit.with_suffix(".report.json"))
    if ((retirement_journal is None) != (retirement_digest is None)
            or (retirement_journal is not None and not corrected_receipt)):
        raise ValueError("retirement requires a corrected receipt, journal and preview digest")
    if corrected_receipt and retirement_journal is not None:
        view = sandbox_red_release.VerifiedRebaseSuccessor(
            root, corrected_receipt, retirement_journal=retirement_journal, retirement_digest=retirement_digest,
        )
    else:
        view = sandbox_red_release.VerifiedRebaseSuccessor(root, corrected_receipt) if corrected_receipt else None

    def historical_read(path):
        return path.read_bytes() if view is None else view.required(path)

    def historical_sha(path):
        return hashlib.sha256(historical_read(path)).hexdigest()

    manifest_hash = historical_sha(manifest)
    discovered = (_discover(root, reports, manifest_hash) if view is None
                  else _discover(root, reports, manifest_hash, successor=view))
    if discovered != set(runs):
        raise ValueError("ordered releases do not cover all saved releases bound to this audit")

    # This verifies the audit binding, original Review, full release chain and
    # final Review census. A failed historical verification is never bypassed.
    snapshot = {"reviewSHA256": historical_sha(review)}
    if view is None:
        lineage = sandbox_red_release.verified_current_lineage(
            root, receipt, audit, runs[0], review_dir, snapshot, runs[1:],
        )
        publications, hashes = sandbox_red_release.verified_release_chain(root, reports, runs[0], runs[1:])
    else:
        lineage = sandbox_red_release.verified_current_lineage(
            root, receipt, audit, runs[0], review_dir, snapshot, runs[1:], successor=view,
        )
        publications, hashes = sandbox_red_release.verified_release_chain(
            root, reports, runs[0], runs[1:], successor=view,
        )
    if hashes != [lineage["priorJournalSHA256"], *lineage["continuationJournalSHA256"]]:
        raise ValueError("release journals changed between lineage checks")
    if view is not None and view.distinct_retirement_source is not None:
        recorded = view.saved["plan"].get("releaseLineage")
        expected_inputs = {key: lineage[key] for key in
                           ("receiptSHA256", "priorManifestSHA256", "currentReviewSHA256")}
        if (not isinstance(recorded, dict)
                or view.distinct_retirement_source["receipt"] != str(receipt)
                or view.distinct_retirement_source["receiptSHA256"] != lineage["receiptSHA256"]
                or recorded.get("receipt") != str(receipt) or recorded.get("audit") != str(audit)
                or recorded.get("review") != str(review_dir) or recorded.get("runs") != runs
                or recorded.get("journalSHA256") != hashes or recorded.get("inputs") != expected_inputs):
            raise ValueError("corrected rebase does not bind this complete retirement source lineage")
    if view is None:
        _bind_first_moves(root, reports, runs[0], publications[0])
    else:
        _bind_first_moves(root, reports, runs[0], publications[0], successor=view)
    _ordered_lineage(publications, hashes, runs)
    original = (normal_recap.collect(receipt) if view is None
                else normal_recap.collect(receipt, read_bytes=view.read))
    if original["status"] != "applied" or original["snapshotDiagnostics"] or original["snapshotIdUnavailable"]:
        raise ValueError("original receipt lacks complete applied Review evidence")
    if original["physicalSources"] != len(original["rows"]):
        raise ValueError("physical source census is incomplete")
    if (original["inputs"].get(str(receipt)) != lineage["receiptSHA256"]
            or historical_sha(receipt) != lineage["receiptSHA256"]
            or historical_sha(manifest) != lineage["priorManifestSHA256"]
            or historical_sha(review) != lineage["currentReviewSHA256"]):
        raise ValueError("lineage inputs changed during collection")
    current = {}
    physical_rows = {id(row) for row in original["rows"]}
    for item in original["auditRecords"]:
        row = item["row"]
        if id(row) not in physical_rows:
            raise ValueError("Review member is not a physical source row")
        key = (row["photoId"], row["destination"], row["preparedSHA256"])
        if key in current or any(existing[0] == key[0] for existing in current):
            raise ValueError("ambiguous original current photo")
        current[key] = []
    for run, publication in zip(runs, publications):
        seen = set()
        for move in publication["moves"]:
            key = (move["photoId"], move["source"], move["sha256"])
            if move["photoId"] in seen or key not in current:
                raise ValueError(f'{run}: move does not match preceding photo state: {move["photoId"]}')
            normal_recap._relative(move["destination"])
            seen.add(move["photoId"])
            history = current.pop(key)
            new_key = (move["photoId"], move["destination"], move["sha256"])
            if new_key in current:
                raise ValueError(f"{run}: ambiguous destination")
            current[new_key] = history + [(run, move["source"], move["destination"])]
    by_id = {key[0]: (key, history) for key, history in current.items()}
    records = []
    active_rows = {id(item["row"]) for item in original["auditRecords"]}
    for row in original["rows"]:
        key_history = by_id.get(row["photoId"])
        # Coalesced/superseded/archive rows remain physical source records;
        # only the actual Review-matched row may borrow later release history.
        original_match = id(row) in active_rows
        history = key_history[1] if original_match and key_history else []
        final = key_history[0][1] if original_match and key_history else row["destination"]
        records.append((row, history, final, original_match))
    if len(by_id) != lineage["conservedCount"]:
        raise ValueError("final census differs from reconstructed lineage")
    cohort_count = len({row["photoId"] for row, history, _, active in records if active and history})
    if expected_cohort is not None and cohort_count != expected_cohort:
        raise ValueError(f"historical release cohort count {cohort_count} differs from required {expected_cohort}")
    if view is not None and view.retirement is not None:
        successor = _corrected(root, corrected_receipt, records, expected_cohort, retirement_view=view)
    else:
        successor = _corrected(root, corrected_receipt, records, expected_cohort) if corrected_receipt else None
    bindings = {key: lineage[key] for key in ("receiptSHA256", "priorManifestSHA256", "currentReviewSHA256")}
    if view is not None:
        if (successor["receiptSHA256"] != hashlib.sha256(view.receipt_bytes).hexdigest()
                or successor["journalSHA256"] != hashlib.sha256(view.journal_bytes).hexdigest()
                or successor["manifestSHA256"] != hashlib.sha256(view.manifest_bytes).hexdigest()):
            raise ValueError("corrected rebase changed between lineage checks")
        view.verify_unchanged()
    return original, records, hashes, successor, bindings


def _image(root, path, digest, data, out_dir):
    target = normal_transaction.safe(root, path)
    cache = data.setdefault("_image_states", {})
    if target not in cache:
        try:
            if not stat.S_ISREG(target.stat().st_mode):
                cache[target] = ("not a file", None)
            else:
                cache[target] = ("available", _sha(target))
        except FileNotFoundError:
            cache[target] = ("missing", None)
        except OSError:
            cache[target] = ("unavailable", None)
    status, actual = cache[target]
    if status == "available":
        status = "verified" if actual == digest else "mismatch"
    if status != "verified":
        return f'<span class="missing">Image {html.escape(status)}; no substitute shown.</span>'
    href = html.escape(rebase_recap._href(target, out_dir), quote=True)
    return (f'<a href="{href}"><img loading="lazy" src="{href}" '
            'alt="Verified photo" onerror="this.hidden=true;this.parentNode.nextElementSibling.hidden=false"></a>'
            '<span hidden>Image load error; recorded bytes were verified when report was generated.</span>')


def render(root, original, records, runs, out, successor=None):
    esc = lambda value: html.escape(str(value))
    data = {"workingRoot": str(root)}
    cohort = {row["photoId"] for row, history, _, active in records if active and history}
    parts = [
        '<!doctype html><html><head><meta charset="utf-8"><title>Sandbox movement history</title>',
        '<style>body{font-family:sans-serif}article{border-top:1px solid #888;padding:1em}',
        'img{max-width:220px;max-height:220px}code{overflow-wrap:anywhere}.missing{color:#733}</style>',
        '</head><body><h1>Sandbox per-photo movement history</h1>',
        '<p>Recorded paths, not identity approval. Image states reflect report generation time; '
        'a later missing or changed file may fail to load. No historical image is substituted.</p>',
        '<p>These are historical outcomes only, not intended routing. Released photos are to be '
        'reconsidered as normal candidates at the start of a rebase; a recorded hold is not a '
        'recommendation or proof of intended placement.</p>',
        '<p>Applied rebase: ' + esc(original["runId"]) + '; ordered releases: ' + esc(", ".join(runs)) + '</p>',
        f'<p>Physical source rows: {len(records)}; current Review members: '
        f'{sum(active for _, _, _, active in records)}; other physical source dispositions: '
        f'{sum(not active for _, _, _, active in records)}. Duplicate IDs in non-current '
        'rows do not establish later movement.</p>',
        f'<p>Historical release cohort: {len(cohort)} distinct photos; '
        + (f'{len(cohort)} of {successor["cohortCount"]} released photos chained through corrected rebase '
           + esc(successor["runId"]) + '.</p>' if successor else
           'corrected rebase not supplied; final corrected placements are not shown.</p>'),
    ]
    if successor and "retirement" in successor:
        parts.append('<p>Empty-identity retirement verified after the corrected rebase; '
                     'retirement does not establish additional photo movements.</p>')
    for row, history, final, active in records:
        parts.append('<article><h2>' + esc(row["photoId"]) + '</h2>')
        if active and history:
            parts.append('<p><strong>Historical release cohort</strong></p>')
        parts.append('<p>Rebase disposition: ' + esc(row.get("placementKind") or row.get("kind") or "recorded")
                     + '; ' + ("unchanged path" if row["source"] == row["destination"] else "path changed")
                     + '. Reason: ' + esc(row.get("reason", "not recorded")) + '</p>')
        steps = [("Source", row["source"], row["sha256"]),
                 ("Applied rebase", row["destination"], row["preparedSHA256"])]
        steps.extend((run, destination, row["preparedSHA256"]) for run, _, destination in history)
        if active:
            steps.append(("After historical releases" if successor else "Final current path",
                          final, row["preparedSHA256"]))
        else:
            parts.append('<p>Historical source disposition; not a separate current Review member. '
                         'Later releases are not attributed to this row.</p>')
        if successor:
            corrected = successor["mapped"].get(row["source"])
            if corrected:
                steps.append(("Corrected rebase " + successor["runId"], corrected["destination"],
                              corrected["preparedSHA256"]))
                parts.append('<p>Corrected disposition: ' + esc(corrected["placementKind"]) + '</p>')
            else:
                parts.append('<p>Corrected lineage not established for this physical source row; '
                             'no corrected placement claimed.</p>')
        for label, path, digest in steps:
            parts.append('<p><strong>' + esc(label) + ':</strong> <code>' + esc(path) + '</code><br>'
                         + _image(root, path, digest, data, out.parent) + '</p>')
        parts.append('</article>')
    return "\n".join(parts + ["</body></html>", ""])


def publish(root, receipt, audit, review_dir, runs, reports, report_id, *, corrected_receipt=None,
            expected_cohort=None, retirement_journal=None, retirement_digest=None, apply=False, check=False):
    report_id = _id(report_id)
    root = pathlib.Path(root).absolute()
    out = normal_transaction.safe(root, f"{reports}/library/movement-history/{report_id}/index.html")
    original, records, hashes, successor, bindings = collect(root, receipt, audit, review_dir, runs, reports,
                                                             corrected_receipt, expected_cohort,
                                                             retirement_journal=retirement_journal,
                                                             retirement_digest=retirement_digest)
    payload = render(root, original, records, runs, out, successor).encode("utf-8")
    state = {
        "kind": "sandbox-movement-history", "receipt": str(pathlib.Path(receipt).absolute()),
        "receiptSHA256": bindings["receiptSHA256"], "auditManifestSHA256": bindings["priorManifestSHA256"],
        "reviewSHA256": bindings["currentReviewSHA256"],
        "releaseRuns": runs, "journalSHA256": hashes, "outputSHA256": hashlib.sha256(payload).hexdigest(),
        "expectedCohortGuard": expected_cohort,
        "producers": {str(pathlib.Path(module.__file__).absolute()): _sha(pathlib.Path(module.__file__))
                      for module in (sys.modules[__name__], normal_recap, rebase_recap, sandbox_red_release,
                                     normal_transaction, normal_recap.policy, normal_recap.gallery_chrome,
                                     sandbox_red_release.normal_recap, sandbox_red_release.normal_transaction,
                                     sandbox_red_release.metadata, sandbox_red_release.likeness.cw)},
    }
    if successor:
        state["corrected"] = {key: successor[key] for key in (
            "runId", "receipt", "receiptSHA256", "journal", "journalSHA256", "manifestSHA256",
            "inputs", "cohortCount",
        )}
        if "retirement" in successor:
            from likeness_library import empty_retirement
            from tools.art.likeness_library import normal_rebase

            state["corrected"]["retirement"] = successor["retirement"]
            for module in (empty_retirement, empty_retirement.sandbox, empty_retirement.person_rename, normal_rebase):
                path = pathlib.Path(module.__file__).absolute()
                state["producers"][str(path)] = _sha(path)
    state_bytes = (json.dumps(state, indent=2, sort_keys=True) + "\n").encode()
    state_path = normal_transaction.safe(root, f"{reports}/library/movement-history/{report_id}/report.json")
    if check or apply:
        expected = ((out, payload), (state_path, state_bytes))
        if check:
            for path, content in expected:
                if not path.is_file() or path.read_bytes() != content:
                    raise ValueError(f"history output missing or changed: {path}")
        else:
            # Never replace existing evidence, including an incomplete prior write.
            if out.parent.exists():
                for path, content in expected:
                    if not path.is_file() or path.read_bytes() != content:
                        raise ValueError(f"report directory exists with different or incomplete evidence: {out.parent}")
            else:
                # Revalidate the chain and rendered image states immediately before writing.
                again, again_records, again_hashes, again_successor, again_bindings = collect(
                    root, receipt, audit, review_dir, runs, reports, corrected_receipt, expected_cohort,
                    retirement_journal=retirement_journal, retirement_digest=retirement_digest,
                )
                if (again_hashes != hashes or again_successor != successor or again_bindings != bindings
                        or render(root, again, again_records, runs, out, again_successor).encode("utf-8") != payload
                        or any(_sha(pathlib.Path(path)) != checksum
                               for path, checksum in state["producers"].items())):
                    raise ValueError("history evidence changed during rendering")
                out.parent.mkdir(parents=True, exist_ok=False)
                for path, content in expected:
                    with path.open("xb") as stream:
                        stream.write(content)
    print(f'History {"checked" if check else "written" if apply else "preview"}: '
          f'{len(records)} physical source rows, {sum(active for _, _, _, active in records)} current Review '
          f'members, {sum(not active for _, _, _, active in records)} other source dispositions; '
          f'{len(runs)} releases, {len({row["photoId"] for row, history, _, active in records if active and history})} '
          f'distinct released photos; corrected rebase {"verified" if successor else "not supplied"}; {out}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "receipt", "audit", "current-review", "report-id"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--release", action="append", required=True, help="release run ID in order; repeat")
    parser.add_argument("--corrected-receipt", help="optional applied successor normal-rebase receipt")
    parser.add_argument("--retirement-journal", help="optional Working-relative applied retirement journal")
    parser.add_argument("--retirement-digest", help="externally retained retirement preview SHA-256")
    parser.add_argument("--expected-cohort", type=int,
                        help="optional guard for the derived distinct historical release count")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="read-only preview (default)")
    mode.add_argument("--apply", action="store_true", help="write only a new report")
    mode.add_argument("--check", action="store_true", help="read-only exact report check")
    args = parser.parse_args(argv)
    try:
        cw = sandbox_red_release.likeness.cw
        cfg = cw.load_cfg()
        root = pathlib.Path(args.root)
        if not root.is_absolute() or root.resolve() != root or root != pathlib.Path(cw.sandbox_work_root(cfg)).resolve():
            raise ValueError("configured Sandbox Working root required")
        if args.expected_cohort is not None and args.expected_cohort < 0:
            raise ValueError("expected cohort must be non-negative")
        reports = cw.storage_root(cfg, "reports", root=root).relative_to(root).as_posix()
        publish(root, args.receipt, args.audit, args.current_review, args.release, reports, args.report_id,
                corrected_receipt=args.corrected_receipt, expected_cohort=args.expected_cohort,
                retirement_journal=args.retirement_journal, retirement_digest=args.retirement_digest,
                apply=args.apply, check=args.check)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Movement history stopped safely: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
