"""Recoverable Sandbox retirement of identity folders emptied by one applied SIMPLE rebase.

Preview (default) discovers emptied non-cast identity folders from the applied
normal-rebase receipt's source rows, then writes a new plan file holding the
plan and its digest. ``--apply`` publishes exactly that saved plan through the
journalled ``empty_retirement`` transaction and refuses a stale preview.
``--check`` verifies the applied journal; ``--recover`` previews exact recovery
and ``--recover-apply`` restores the folders. An emptied Sisters/Angels folder
stops the command with a report: cast folders are never retired here.
Pruning retired folders stays manual. Callers must stop other library writers.
"""
import argparse
import json
import pathlib
import re
import sys

if not __package__:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
    from tools.art.likeness_library import empty_retirement as retirement, sandbox
    from tools.workflows import comfy_workflows as cw
else:
    from . import empty_retirement as retirement, sandbox
    from tools.workflows import comfy_workflows as cw

CAST = frozenset(("Sisters", "Angels"))
PLAN_KIND = "sandbox-empty-folder-retirement-preview-v1"
MAX_RECEIPT_BYTES = 128 * 1024 ** 2


class CastEmptied(ValueError):
    """An emptied Sisters/Angels folder needs a human decision."""


def _run_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}", value):
        raise ValueError(f"unsafe run ID: {value!r}")
    return value


def _root(value):
    root = pathlib.Path(value)
    if not root.is_absolute() or not sandbox.is_sandbox_working_path(root):
        raise ValueError("--root must be an absolute Sandbox Working path (...\\Sovereign Territories Sandbox\\Working)")
    if not root.is_dir():
        raise ValueError(f"Sandbox Working root does not exist: {root}")
    return root


def _relative(root, value):
    """Return a Working-relative POSIX path for an absolute or relative receipt path."""
    path = pathlib.Path(value)
    if path.is_absolute():
        try:
            return path.relative_to(root).as_posix()
        except ValueError:
            try:
                return path.resolve().relative_to(root.resolve()).as_posix()
            except ValueError:
                raise ValueError(f"path is outside the Sandbox Working root: {value}") from None
    return str(value).replace("\\", "/")


def paths(root, cfg, run_id):
    """Working-relative plan and journal paths for one run ID."""
    reports = cw.storage_root(cfg, "reports", root=root).relative_to(root).as_posix()
    base = f"{reports}/runs/empty-retirement-{_run_id(run_id)}"
    return f"{base}-preview.json", f"{base}.json"


def _receipt(root, relative):
    path = retirement._path(root, relative)
    if not path.is_file():
        raise ValueError(f"rebase receipt not found: {path}")
    if path.stat().st_size > MAX_RECEIPT_BYTES:
        raise ValueError("rebase receipt exceeds retirement bounds")
    data = json.loads(path.read_bytes())
    if (not isinstance(data, dict) or data.get("kind") != "normal-rebase-receipt"
            or data.get("status") != "applied" or not isinstance(data.get("plan"), dict)):
        raise ValueError("expected an applied normal-rebase receipt")
    return data


def predecessor(root, receipt):
    journal = receipt.get("journal")
    if not isinstance(journal, str) or not journal:
        raise ValueError("rebase receipt names no publication journal")
    return _relative(root, journal)


def _has_original(folder):
    for bucket in ("gallery", "review"):
        directory = folder / bucket
        if directory.is_dir():
            for child in directory.iterdir():
                if child.is_file() and child.suffix.casefold() in retirement.IMAGES:
                    return True
    return False


def discover(root, receipt):
    """Return (emptied non-cast folders, emptied cast folders) owned by receipt source rows."""
    rows = receipt["plan"].get("sourceRows")
    if not isinstance(rows, list):
        raise ValueError("rebase receipt has no source rows")
    owners = sorted({row["owner"] for row in rows
                     if isinstance(row, dict) and isinstance(row.get("owner"), str)
                     and row["owner"].split("/", 1)[0] in retirement.CATEGORIES})
    empty, cast = [], []
    for owner in owners:
        folder = retirement._path(root, owner)
        if not folder.is_dir() or _has_original(folder):
            continue
        (cast if owner.split("/", 1)[0] in CAST else empty).append(owner)
    return empty, cast


def _select(root, receipt, explicit):
    empty, cast = discover(root, receipt)
    if cast:
        raise CastEmptied(
            f"{len(cast)} emptied Sisters/Angels folder(s) found; cast folders are never retired "
            "automatically - inspect the rebase and decide manually:\n"
            + "\n".join("  " + key for key in cast))
    if explicit:
        explicit = [key.replace("\\", "/") for key in explicit]
        bad = [key for key in explicit if key.split("/", 1)[0] in CAST]
        if bad:
            raise CastEmptied("Sisters/Angels folders are never retired by this command: " + ", ".join(bad))
        missing = [key for key in explicit if key not in empty]
        if missing:
            raise ValueError("--folder is not an emptied identity owned by this rebase: " + ", ".join(missing))
        return sorted(set(explicit))
    return empty


def _load_plan(root, relative):
    path = retirement._path(root, relative)
    if not path.is_file():
        raise ValueError(f"saved preview not found; run the preview first: {path}")
    saved = json.loads(path.read_bytes())
    if (not isinstance(saved, dict) or saved.get("kind", PLAN_KIND) != PLAN_KIND
            or not isinstance(saved.get("plan"), dict) or not isinstance(saved.get("digest"), str)
            or retirement._digest(saved["plan"]) != saved["digest"]):
        raise ValueError(f"saved preview is invalid or edited: {path}")
    if saved["plan"].get("root") != str(root):
        raise ValueError("saved preview belongs to another Working root")
    return saved


def _bind(root, plan, receipt_relative, predecessor_relative):
    if plan["sourceReceipt"] != receipt_relative or plan["predecessor"] != predecessor_relative:
        raise ValueError("saved preview is bound to another rebase receipt or predecessor journal")


def run(root, run_id, mode, *, cfg, receipt=None, folders=(), out=print):
    root = _root(root)
    plan_relative, journal_relative = paths(root, cfg, run_id)
    plan_path = retirement._path(root, plan_relative)
    journal_path = retirement._path(root, journal_relative)
    receipt_relative = _relative(root, receipt) if receipt else None
    if mode in ("preview", "apply") and not receipt_relative:
        raise ValueError("--receipt is required for preview and apply")
    if mode == "preview":
        for existing in (plan_path, journal_path):
            if existing.exists():
                raise ValueError(f"refusing to overwrite existing {existing}; choose a new --run-id")
        data = _receipt(root, receipt_relative)
        previous = predecessor(root, data)
        selected = _select(root, data, folders)
        out(f"emptied identity folders: {len(selected)}")
        for key in selected:
            out("  " + key)
        if not selected:
            out("nothing to retire; no plan written")
            return 0
        plan, digest = retirement.preview(root, selected, receipt_relative, previous, cfg=cfg)
        if not plan_path.parent.is_dir():
            raise ValueError(f"reports runs directory must already exist: {plan_path.parent}")
        payload = json.dumps({"kind": PLAN_KIND, "runId": run_id, "digest": digest, "plan": plan},
                             indent=2) + "\n"
        with plan_path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
        out(f"preview digest {digest}")
        out(f"plan {plan_path}")
        out("Preview only: nothing moved. Apply with --apply and the same --run-id.")
        return 0
    saved = _load_plan(root, plan_relative)
    plan, digest = saved["plan"], saved["digest"]
    if receipt_relative:
        data = _receipt(root, receipt_relative)
        _bind(root, plan, receipt_relative, predecessor(root, data))
    if mode == "apply":
        if journal_path.exists():
            raise ValueError(f"refusing to overwrite existing journal {journal_path}")
        empty, cast = discover(root, data)
        if cast:
            _select(root, data, ())  # raises the cast report
        stale = [move["source"] for move in plan["moves"] if move["source"] not in empty]
        if stale:
            raise ValueError("saved preview is stale (no longer emptied: " + ", ".join(stale)
                             + "); run a new preview with a new --run-id")
        path = retirement.apply(root, plan, digest, journal_relative, cfg=cfg)
        retirement.check(root, journal_relative, digest)
        out(f"applied and checked: {len(plan['moves'])} folder(s) retired under {plan['retiredRoot']}")
        out(f"journal {path}")
        out(f"digest {digest}")
        return 0
    if mode == "check":
        data = retirement.check(root, journal_relative, digest)
        out(f"checked: {len(data['plan']['moves'])} folder(s) retired under {data['plan']['retiredRoot']}")
        out(f"journal {journal_path}; digest {digest}")
        return 0
    if mode in ("recover", "recover-apply"):
        states = retirement.recover(root, journal_relative, digest, apply=mode == "recover-apply")
        for move, state in zip(plan["moves"], states):
            out(f"  {move['source']}: {state}")
        if mode == "recover":
            out("Recovery preview only: nothing moved. Restore with --recover-apply.")
        else:
            out(f"recovered: {len(states)} folder(s) restored; journal {journal_path}")
        return 0
    raise ValueError(f"unknown mode: {mode}")


def main(argv=None, *, cfg=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", required=True, help="absolute Sandbox Working root")
    parser.add_argument("--run-id", required=True, help="names the saved preview plan and journal")
    parser.add_argument("--receipt", help="applied normal-rebase receipt (Working-relative or absolute inside root); "
                                          "required for preview and apply")
    parser.add_argument("--folder", action="append", default=[],
                        help="optional explicit CATEGORY/Name subset of the discovered emptied folders; repeat")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="preview",
                      help="preview and save a new plan (default)")
    mode.add_argument("--apply", dest="mode", action="store_const", const="apply")
    mode.add_argument("--check", dest="mode", action="store_const", const="check")
    mode.add_argument("--recover", dest="mode", action="store_const", const="recover",
                      help="read-only recovery preview")
    mode.add_argument("--recover-apply", dest="mode", action="store_const", const="recover-apply")
    args = parser.parse_args(argv)
    try:
        if cfg is None:
            from tools.art import likeness as api
            cfg = api.configuration()
        return run(args.root, args.run_id, args.mode or "preview", cfg=cfg,
                   receipt=args.receipt, folders=args.folder)
    except CastEmptied as exc:
        print(f"Empty retirement stopped: {exc}", file=sys.stderr)
        return 3
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Empty retirement stopped safely: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
