"""Write docs/todo.md: active-plan Queue focus (all open tasks when absent), linked deferred/holding counts, completed plans, and top-tier card state.

    python tools/art/todo_report.py            write docs/todo.md (keeps the section you write between the notes markers)
    python tools/art/todo_report.py --print    show it instead of writing

Nothing here is ticked by hand: a cell is `FINAL` when a workflow was chosen as the final for that stage, `cN` when N candidates are kept, `-` when none, `n/a` when the card has no such stage.
Q and F are the engines (Qwen, FireRed). The table reads workflows/_final and workflows/_candidates, so run `pull` (and `finals sort`) first to bring in what you saved in the workspaces.
"""
import argparse
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "workflows"))
import comfy_workflows as cw  # noqa: E402

OUT = ROOT / "docs" / "todo.md"
NOTES_START, NOTES_END = "<!-- notes:start -->", "<!-- notes:end -->"
ENGINES = {"Qwen": "Q", "FireRed": "F"}

# (title, columns: label -> stage names after Hero_Engine_) per kind of card
WOMAN = {"Prime": ["Alpha_1_Prime"], "Bare": ["Alpha_2_Bare_Figure", "Alpha_2_Bare_Skin"], "Golden pose": ["Alpha_3_Barefoot"], "Heels": ["Alpha_3_Heels"]}
MAN = {"Prime": ["Alpha_1_Prime"], "Bare": ["Alpha_2_Bare_Figure"]}
BOUND = {"Prime (X Pose)": ["X_Pose"]}
DRAGON = {"Pose": ["X_Pose"], "Head": ["X_Head"], "Lair": ["Scene_Lair"]}
TABLES = [
    ("Angel women", "angel-primes", "female", WOMAN),
    ("Angel men", "angel-primes", "male", MAN),
    ("Alpha test heroes (not angels)", "angel-primes", "alpha", WOMAN),
    ("Drakn sisters", "drakn-sisters", None, WOMAN),
    ("Drakn Bound men", "drakn-bound", None, BOUND),
    ("Elder Dragons", "elder-dragons", None, DRAGON),
]


def state(finals, cands, hero, stems):
    cells = []
    for engine, letter in ENGINES.items():
        stem = next((s for s in stems if s.startswith(f"{hero}_{engine}_")), None)
        if not stem:
            continue
        if finals.get(stem):
            cells.append(f"{letter} FINAL" + (f" +{finals[stem] - 1}" if finals[stem] > 1 else ""))
        elif cands.get(stem):
            cells.append(f"{letter} c{cands[stem]}")
    return " · ".join(cells) or "-"


def collect(cfg):
    heroes, idx = list(cw.hero_groups()), cw.finals_index(cfg)
    finals, cands, other = collections.Counter(), collections.Counter(), collections.Counter()
    for kind, root, bucket in (("final", cw.FINALS, finals), ("candidate", cw.CANDIDATES, cands)):
        for p in sorted(root.rglob("*.json")) if root.is_dir() else []:
            parsed = cw.parse_saved(cfg, p.name, heroes, list(idx))
            if parsed:
                bucket[parsed["stem"]] += 1
    return idx, finals, cands


def table(cfg, title, group, division, columns, idx, finals, cands):
    homes = cw.hero_homes()
    names = sorted(h for h, (g, d) in homes.items() if g == group and (d == division if division else d is None))
    if not names:
        return []
    slot_stems = {h: {f"{h}_{e}_{n}" for names_ in columns.values() for n in names_ for e in ENGINES} for h in names}
    lines = [f"### {title} ({len(names)})", "", "| Hero | Photo | " + " | ".join(columns) + " | Other finals | Candidates |", "| --- | --- | " + " | ".join("---" for _ in columns) + " | ---: | ---: |"]
    photos = cfg.get("photos", {})
    for h in names:
        stems_all = [s for s in idx if s.startswith(f"{h}_")]
        row = []
        for label, stage_names in columns.items():
            stems = [f"{h}_{e}_{n}" for n in stage_names for e in ENGINES if f"{h}_{e}_{n}" in idx]
            row.append(state(finals, cands, h, stems) if stems else ("no workflow yet" if group in cfg.get("skipGroups", []) else "n/a"))
        mine_f = sum(v for s, v in finals.items() if s.startswith(f"{h}_") and s not in slot_stems[h])
        mine_c = sum(v for s, v in cands.items() if s.startswith(f"{h}_"))
        photo = re.sub(r"^various_(image|screenshot)_|_944x1104\.png$|\.png$", "", photos.get(h, ""))
        photo = (photo[:14] + "~") if len(photo) > 15 else photo
        lines.append(f"| {h} | {photo or '-'} | " + " | ".join(row) + f" | {mine_f or '-'} | {mine_c or '-'} |")
    return lines + [""]


TAG = re.compile(r"^\*\*P([123]) (you|ai|either)\*\*\s*")
PRIORITY = {"1": "P1 (blocks other work, or cheap and valuable)", "2": "P2 (normal)", "3": "P3 (later, or ideas)"}


def plan_status(text):
    """The word after 'Status:' in a plan (bold or plain), lower case, or ''."""
    m = re.search(r"^\*{0,2}Status:\*{0,2}\s*\**\s*([A-Za-z]+)", text, re.M)
    return m.group(1).lower() if m else ""


def open_work():
    """A focused execution queue plus deferred inventory: a `- [ ] **P1 you** ...` box is priority 1 to 3 and owner you (needs your hands or decision), ai (the assistant, when you say go) or either.
    An untagged box is P2 either. Archived plans (docs/plans/_archive) are listed as completed work."""
    items, waiting = [], []
    for plan in sorted((ROOT / "docs" / "plans").glob("2*.md")):
        text = plan.read_text(encoding="utf-8")
        status = plan_status(text)
        if status not in {"active", "holding"}:
            continue
        title = re.search(r"^# (.+)$", text, re.M).group(1)
        focus_line = re.search(r"^\*\*Queue focus:\*\*\s*(.+)$", text, re.M)
        focus = None
        if focus_line:
            tokens = [value.strip() for value in focus_line.group(1).split(",")]
            if (not all(re.fullmatch(r"[A-Z]+\d+[a-z]?", value) for value in tokens)
                    or len(tokens) != len(set(tokens))):
                raise ValueError(f"invalid or duplicate Queue focus IDs: {plan.name}")
            focus = tokens
        plan_items = []
        lines = text.splitlines()
        fenced = False
        fence_marker = ""
        for index, line in enumerate(lines):
            fence = re.match(r"^\s*(`{3,}|~{3,})", line)
            if fence:
                marker = fence.group(1)
                if not fenced:
                    fenced, fence_marker = True, marker
                elif marker[0] == fence_marker[0] and len(marker) >= len(fence_marker):
                    fenced = False
                continue
            if fenced:
                continue
            m = re.match(r"^\s*- \[ \] (.+)$", line)
            if m:
                body = m.group(1)
                t = TAG.match(body)
                prio, who = (t.group(1), t.group(2)) if t else ("2", "either")
                body = TAG.sub("", body)
                for continuation in lines[index + 1:]:
                    if (not re.match(r"^ {2,}\S", continuation)
                            or re.match(r"^\s*(?:[-*+] |\d+\. |`{3,}|~{3,})", continuation)):
                        break
                    body += " " + continuation.strip()
                plan_items.append((prio, who, body if len(body) <= 230 else body[:227].rsplit(" ", 1)[0] + " ...", plan.name, title))
        if focus is not None:
            open_ids = {item[2].split()[0] for item in plan_items}
            missing = set(focus) - open_ids
            if missing:
                raise ValueError(f"Queue focus IDs are not open tasks in {plan.name}: {sorted(missing)}")
        selected = [
            item for item in plan_items
            if status == "active" and (focus is None or item[2].split()[0] in focus)
        ]
        if focus is not None:
            selected.sort(key=lambda item: focus.index(item[2].split()[0]))
        items.extend(selected)
        deferred = len(plan_items) - len(selected)
        if deferred:
            waiting.append((plan.name, status, deferred))
    out = []
    for who, heading in (("you", "Your queue: needs your hands or a decision"), ("either", "Either of us"), ("ai", "For the assistant, when you say go")):
        sel = [i for i in items if i[1] == who]
        if not sel:
            continue
        out += [f"### {heading} ({len(sel)})", ""]
        for prio in "123":
            part = [i for i in sel if i[0] == prio]
            if part:
                out += [f"**{PRIORITY[prio]}**", ""] + [f"- [ ] {b} ([{p[11:-3].replace('-', ' ')}](plans/{p}))" for _, _, b, p, _ in part] + [""]
    out = out or ["Nothing open in the active plans.", ""]
    if waiting:
        out += [
            "<details>", "<summary>Deferred work by owning plan</summary>", "",
            "### Scheduled backlog (not the current execution queue)", "",
            "Open tasks remain in their owning plans; holding is not completion. "
            "Use [Now / next / holding](plans/README.md#now-next-and-holding) for resume gates.", "",
            "| Plan | Scheduling | Open tasks outside focus |",
            "| --- | --- | ---: |",
        ]
        out += [f"| [{name}](plans/{name}) | {status} | {count} |"
                for name, status, count in waiting]
        out += ["", "</details>", ""]
    done = sorted((ROOT / "docs" / "plans" / "_archive").glob("2*.md"))
    out += ["<details>", f"<summary>Archived plans ({len(done)} historical records, not all completed)</summary>", "",
            "### Archived plans", "",
            "Use the [archive guide](archive-guide.md) for topic navigation. "
            "`dropped` means superseded, not implemented.", ""]
    for plan in done:
        text = plan.read_text(encoding="utf-8")
        title = re.search(r"^# (.+)$", text, re.M).group(1)
        out.append(f"- **{plan_status(text) or 'unclassified'}**: [{title}](plans/_archive/{plan.name})")
    return out + ["", "</details>", ""]


def build():
    cfg = cw.load_cfg()
    idx, finals, cands = collect(cfg)
    notes = ""
    if OUT.exists():
        m = re.search(re.escape(NOTES_START) + r"\n(.*?)\n" + re.escape(NOTES_END), OUT.read_text(encoding="utf-8"), re.S)
        notes = m.group(1) if m else ""
    notes = notes or "Your own notes go here; this section is kept when the file is regenerated."
    lines = ["# To do", "", "> Generated by `bin\\todo.cmd`; do not edit outside the notes section. Active-plan Queue focus selects the execution window (all open tasks when absent); deferred/holding counts below link to preserved backlog. Use [Now / next / holding](plans/README.md#now-next-and-holding) for dependencies. Card tables read finals/candidates in `workflows/_final` and `workflows/_candidates` (run `pull` first).",
             "> `FINAL` = a workflow was chosen as the final for that stage, `cN` = N candidates kept, `-` = none, `n/a` = no such stage, `no workflow yet` = the set is not in the pipeline yet (drakn-bound, elder-dragons). Q = Qwen, F = FireRed.", "",
             "[Execution sequence and parallel lanes](plans/README.md#parallel-analysis-and-small-improvements) | "
             "[Archive guide](archive-guide.md) | [Current resume](recap/README.md)", "",
             "## Open work, by priority", ""] + open_work() + [
                 "## Where each card stands", "",
                 "<details>", "<summary>Expand card finals and candidates (supporting inventory, not today's queue)</summary>", ""]
    for title, group, division, columns in TABLES:
        lines += table(cfg, title, group, division, columns, idx, finals, cands)
    lines += ["</details>", "", "## Notes", "", NOTES_START, notes, NOTES_END, ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--print", action="store_true", help="show it instead of writing docs/todo.md")
    args = ap.parse_args()
    text = build()
    if args.print:
        print(text)
    else:
        OUT.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {OUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
