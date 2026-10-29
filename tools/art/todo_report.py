"""Write docs/todo.md: the open work of the active plans in one queue by priority and owner (what needs you, what the assistant can do), the completed plans, and where every top-tier card stands, read from the finals and candidates kept in the repo.

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
    """One queue for everything still open, read from the plans: a `- [ ] **P1 you** ...` box is priority 1 to 3 and owner you (needs your hands or decision), ai (the assistant, when you say go) or either.
    An untagged box is P2 either. Archived plans (docs/plans/_archive) are listed as completed work."""
    items = []
    for plan in sorted((ROOT / "docs" / "plans").glob("2*.md")):
        text = plan.read_text(encoding="utf-8")
        if plan_status(text) != "active":
            continue
        title = re.search(r"^# (.+)$", text, re.M).group(1)
        heading = ""
        for line in text.splitlines():
            if line.startswith("### "):
                heading = line[4:].strip()
            m = re.match(r"^\s*- \[ \] (.+)$", line)
            if m:
                body = m.group(1)
                t = TAG.match(body)
                prio, who = (t.group(1), t.group(2)) if t else ("2", "either")
                body = TAG.sub("", body)
                items.append((prio, who, body if len(body) <= 230 else body[:227].rsplit(" ", 1)[0] + " ...", plan.name, title))
    out = []
    for who, heading in (("you", "Your queue: needs your hands or a decision"), ("either", "Either of us"), ("ai", "For the assistant, when you say go")):
        sel = [i for i in items if i[1] == who]
        if not sel:
            continue
        out += [f"### {heading} ({len(sel)})", ""]
        for prio in "123":
            part = [i for i in sel if i[0] == prio]
            if part:
                out += [f"**{PRIORITY[prio]}**", ""] + [f"- [ ] {b} ([{p[:10]}](plans/{p}))" for _, _, b, p, _ in part] + [""]
    out = out or ["Nothing open in the active plans.", ""]
    done = sorted((ROOT / "docs" / "plans" / "_archive").glob("2*.md"))
    out += [f"### Completed plans ({len(done)}, in [plans/_archive](plans/_archive))", ""]
    for plan in done:
        title = re.search(r"^# (.+)$", plan.read_text(encoding="utf-8"), re.M).group(1)
        out.append(f"- [{plan.name[:10]}: {title}](plans/_archive/{plan.name})")
    return out + [""]


def build():
    cfg = cw.load_cfg()
    idx, finals, cands = collect(cfg)
    notes = ""
    if OUT.exists():
        m = re.search(re.escape(NOTES_START) + r"\n(.*?)\n" + re.escape(NOTES_END), OUT.read_text(encoding="utf-8"), re.S)
        notes = m.group(1) if m else ""
    notes = notes or "Your own notes go here; this section is kept when the file is regenerated."
    lines = ["# To do", "", "> Generated by `python tools/art/todo_report.py` (`bin\\todo.cmd`); do not edit outside the notes section. The queue is read from the open boxes of the active plans (`- [ ] **P1 you** ...`: priority, owner), the card tables from the finals and candidates in `workflows/_final` and `workflows/_candidates` (run `pull` first).",
             "> `FINAL` = a workflow was chosen as the final for that stage, `cN` = N candidates kept, `-` = none, `n/a` = no such stage, `no workflow yet` = the set is not in the pipeline yet (drakn-bound, elder-dragons). Q = Qwen, F = FireRed.", "",
             "## Open work, by priority", ""] + open_work() + ["## Where each card stands", ""]
    for title, group, division, columns in TABLES:
        lines += table(cfg, title, group, division, columns, idx, finals, cands)
    lines += ["## Notes", "", NOTES_START, notes, NOTES_END, ""]
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
