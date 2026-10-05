#!/usr/bin/env python3
"""Keep prompts, repo workflows and the local ComfyUI workspaces in step.

Repo layout follows the prompts:  workflows/<set>/<Hero>/<Hero>_Qwen_<Stage>_<Name>.json
(<set> is the prompt group: drakn-sisters, drakn-bound, angel-primes, elder-dragons ...).

ComfyUI workspaces are DEPLOY TARGETS configured in workflows/workspaces.json, in three tiers:
  dev    where workflows are built and proven (Soverign Territories; the default target of every deploy)
  uat    acceptance: a hero's own workspace or a group workspace (Drakness, Angel Primes ...)
  prod   a card-series workspace for the final art ("Soverign Dawn Series"); holds only the cards of that series
Which workspace serves which hero or set is configured under "production"; nothing is hard-coded.

Commands
  list                                 workspaces, routes and repo contents
  status  [targets] [filters] [--lint]      repo vs workspace(s): aligned / stale / missing / install-only / legacy
  make    [filters] [--create]         prompt -> repo workflow: set positive, negative, filename prefix (and file name)
  deploy  [targets] [filters]          repo -> workspace (default: dev). Existing workflows only get the three
                                       prompt values updated, so input image, seed and toggles survive. --overwrite replaces.
  cleanup [filters] [--apply]          preview (or --apply) removing plain duplicates from dev that are identical in their UAT workspace;
                                       everything else stays (not in the repo, edited, not delivered). Moved to backup, never deleted.
  promote --to uat|prod [--from dev|uat] <filters>
                                       MOVE approved workflows up a tier: capture the source workspace copy into the repo
                                       master, copy it to the next tier, then take it out of the source workspace (backed up)
  pull    [targets] [filters]          workspace -> repo. Files we did not generate are kept as CURATED workflows
                                       (workflows/_curated/<set>/<Hero>/); later edits to a curated file are captured too.
                                       --force also replaces generated repo copies.
  fork    NAME --as TAG                copy a generated workflow to _curated as NAME_TAG and put it in dev, to hand-edit in ComfyUI
  deploy  ... --curated                also copy curated workflows a workspace lacks (a differing workspace copy is never overwritten)
  inputs  [--fix]                      which A-pose image each hero's workflows read

targets:  (none) = dev   |   --to dev|uat|prod   |   -w <Workspace> (repeatable)
filters:  --hero H  --group G  --stage S  --class studio|scene  --match TEXT   (stage = prompt folder: poses, head, scene, hair, motion, armor, clothing)
          deploy and promote need at least one filter, or --all.

The four values that always agree for a prompt Hero_Stage_Name.txt:
  positive prompt, negative prompt, SaveImage prefix <set>/<Hero>/<stage>/[family/]<Hero>_Qwen_<Stage>_<Name>, workflow file <Hero>_Qwen_<Stage>_<Name>.json
Nothing is ever deleted, and every overwritten workspace file is first copied to workflows/.sync/backup/.
"""
import argparse
import collections
import datetime
import fnmatch
import json
import pathlib
import re
import shutil
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[2]
WF = ROOT / "workflows"
PROMPTS = ROOT / "prompts"
CFG_PATH = WF / "workspaces.json"
BACKUPS = WF / ".sync" / "backup"
CURATED = WF / "_curated"
TIERS = ("dev", "uat", "prod")


# ---------- configuration ----------

def load_cfg():
    return json.loads(CFG_PATH.read_text(encoding="utf-8"))


def install_dir(cfg, ws, root=None):
    return pathlib.Path(root or cfg["installsRoot"]) / ws / cfg["workflowsSubpath"]


def install_exists(cfg, ws, root=None):
    return (pathlib.Path(root or cfg["installsRoot"]) / ws / "ComfyUI").is_dir()


def excluded(cfg, name):
    return any(fnmatch.fnmatch(name, pat) for pat in cfg.get("exclude", []))


def is_template(cfg, name):
    return fnmatch.fnmatch(name, cfg.get("stageTemplates", "ST?_*.json"))


def template_files(cfg):
    return {p.name: p for p in sorted((WF / "_templates").glob("*.json")) if is_template(cfg, p.name)}


def same_bytes(a, b):
    return pathlib.Path(a).read_bytes().rstrip() == pathlib.Path(b).read_bytes().rstrip()


# ---------- routing: which workspace serves which hero ----------

def stage_classes():
    """{prompt folder: 'studio' | 'scene'} from data/art/_schema/stages.json."""
    s = json.loads((ROOT / "data/art/_schema/stages.json").read_text(encoding="utf-8"))
    return {folder: cls for cls, folders in s["classes"].items() for folder in folders}


def class_of(stage):
    return stage_classes().get(stage)


CLASS_PROBE = ("poses", "scene")  # one stage folder of each class, for routes that do not depend on a stage


def stage_ok(args, name_or_stage, is_stage=False):
    """True when a file (or stage folder) passes the --stage and --class filters."""
    stage = name_or_stage if is_stage else stage_of(name_or_stage)
    if not is_stage and getattr(args, "engine", None) in ENGINES and engine_of(name_or_stage) != args.engine:
        return False
    return (not args.stage or stage == args.stage) and (not args.cls or class_of(stage) == args.cls)


def route_stage(args):
    """The stage to route by: the explicit one, else a probe of the chosen class, else None (all)."""
    return args.stage or (dict(zip(("studio", "scene"), CLASS_PROBE))[args.cls] if args.cls else None)


def targets_for(cfg, tier, group, hero, stage=None):
    """Workspaces that serve this hero and stage for a tier. Dev: the default dev workspace. UAT: first matching rule. Prod: every matching rule.

    A rule may carry "class": "studio" or "scene"; it then applies only to stages of that class."""
    if tier == "dev":
        return [cfg["dev"][0]]
    out = []
    for r in cfg.get("production", {}).get(tier, []):
        if "groups" in r and group not in r["groups"]:
            continue
        if "heroes" in r and hero not in r["heroes"]:
            continue
        if "class" in r and (stage is None or class_of(stage) != r["class"]):
            continue
        out.append(r["workspace"].format(hero=hero))
        if tier == "uat":
            break
    return out


def holds(cfg, ws, group, hero, stage=None):
    stages = [stage] if stage else list(CLASS_PROBE)
    return ws in cfg["dev"] or any(ws in targets_for(cfg, t, group, hero, s) for t in TIERS for s in stages)


def tier_workspaces(cfg, tier, hero=None, group=None, stage=None):
    """Every workspace that serves some (filtered) hero and stage for a tier."""
    names = []
    stages = [stage] if stage else list(CLASS_PROBE)
    for h, g in hero_groups().items():
        if (hero and h.lower() != hero.lower()) or (group and g != group):
            continue
        for s in stages:
            for w in targets_for(cfg, tier, g, h, s):
                if w not in names:
                    names.append(w)
    return names


# ---------- files ----------

def hero_groups():
    """{hero: group} from prompts/<group>/<Hero>/."""
    out = {}
    for g in sorted(PROMPTS.iterdir()):
        if g.is_dir() and not g.name.startswith(("_", ".")):
            for h in sorted(g.iterdir()):
                if h.is_dir() and not h.name.startswith(("_", ".")):
                    out[h.name] = g.name
    return out


def engine_roots(cfg):
    """{engine: folder holding its generated workflows}. FireRed is a local test engine kept out of git."""
    roots = {"qwen": WF}
    for engine in ("firered", "minimax"):
        if cfg.get("engines", {}).get(engine):
            roots[engine] = ROOT / cfg["engines"][engine]["dir"]
    return roots


def engine_of(name):
    return "firered" if "_FireRed_" in name else "minimax" if "_MiniMax_" in name else "qwen"


def repo_path(cfg, group, hero, name):
    return engine_roots(cfg)[engine_of(name)] / group / hero / name


def repo_files(cfg):
    """{name: (group, hero, path)} for every workflow in <engine folder>/<set>/<Hero>/."""
    out = {}
    for root in engine_roots(cfg).values():
        if not root.is_dir():
            continue
        for g in sorted(root.iterdir()):
            if not g.is_dir() or g.name.startswith(("_", ".")):
                continue
            for h in sorted(g.iterdir()):
                if h.is_dir():
                    for p in sorted(h.glob("*.json")):
                        if not excluded(cfg, p.name):
                            out[p.name] = (g.name, h.name, p)
    return out


def hero_files(hero):
    g = hero_groups().get(hero)
    return sorted((WF / g / hero).glob("*.json")) if g else []


def install_files(cfg, ws, root=None):
    """{name: path} for the workflows saved in a workspace (flat by file name)."""
    out = {}
    d = install_dir(cfg, ws, root)
    if d.is_dir():
        for p in sorted(d.rglob("*.json")):
            rel = p.relative_to(d)
            if any(part.startswith((".", "_")) for part in rel.parts) or excluded(cfg, p.name):
                continue
            out.setdefault(p.name, p)
    return out


def hero_of(name):
    prefix = name.split("_", 1)[0]
    return prefix if prefix in hero_groups() else None


STAGE_WORDS = {"Scene": "scene", "Hair": "hair", "Motion": "motion", "Armor": "armor", "Clothing": "clothing",
               "Head": "head", "View": "poses", "Video": "video"}


def stage_of(name):
    """Prompt folder a workflow file belongs to: Hero_Qwen_X_Pose -> poses, Hero_Qwen_Scene_Glamour -> scene."""
    m = re.match(r"^[^_]+_(?:Qwen|FireRed|MiniMax)_(.+?)(?:\.json)?$", name)
    if not m:
        return "other"
    parts = m.group(1).split("_")
    if parts[0] == "X":
        return "head" if len(parts) > 1 and parts[1] == "Head" else "poses"
    return STAGE_WORDS.get(parts[0], parts[0].lower())


def read_wf(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def write_wf(p, d):
    p = pathlib.Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")


def prompt_node(wf):
    """The subgraph instance that holds the positive/negative prompt widgets."""
    sg_ids = {s["id"] for s in wf.get("definitions", {}).get("subgraphs", [])}
    for n in wf.get("nodes", []):
        wv = n.get("widgets_values")
        if n.get("type") in sg_ids and isinstance(wv, list) and len(wv) >= 2 and isinstance(wv[0], str):
            return n
    return None


def node_of(wf, kind):
    for n in wf.get("nodes", []):
        if n.get("type") == kind:
            return n
    return None


def save_node(wf):
    """The node that names the output files: SaveImage for pictures, SaveVideo for animations."""
    return node_of(wf, "SaveImage") or node_of(wf, "SaveVideo")


def get_values(wf):
    n, s = prompt_node(wf), save_node(wf)
    if not n or not s:
        return None
    return n["widgets_values"][0], n["widgets_values"][1], s["widgets_values"][0]


def curated_prefix(group, hero, name):
    """Hand-curated workflows write to <group>/<Hero>/_curated/<name>, apart from the generated art."""
    return f"{group}/{hero}/_curated/{name[:-5] if name.endswith('.json') else name}"


def set_prefix(wf, prefix):
    """Set only the SaveImage prefix; return True if it changed."""
    s = save_node(wf)
    if not s or s["widgets_values"][0] == prefix:
        return False
    s["widgets_values"][0] = prefix
    if isinstance(s.get("widgets_values_named"), dict) and "filename_prefix" in s["widgets_values_named"]:
        s["widgets_values_named"]["filename_prefix"] = prefix
    return True


def patch_wf(wf, pos, neg, prefix):
    """Set the three in-graph values; return True if anything changed."""
    n, s = prompt_node(wf), save_node(wf)
    if not n or not s:
        raise ValueError("workflow has no prompt subgraph or save node")
    changed = False
    wv = n["widgets_values"]
    named = n.get("widgets_values_named")
    has_neg = not isinstance(named, dict) or "prompt_1" in named  # FireRed exposes only a positive prompt
    if wv[0] != pos or (has_neg and wv[1] != neg):
        changed = True
    wv[0] = pos
    if has_neg:
        wv[1] = neg
    if isinstance(named, dict):
        named["prompt"] = pos
        if has_neg:
            named["prompt_1"] = neg
    if s["widgets_values"][0] != prefix:
        changed = True
        s["widgets_values"][0] = prefix
        if isinstance(s.get("widgets_values_named"), dict) and "filename_prefix" in s["widgets_values_named"]:
            s["widgets_values_named"]["filename_prefix"] = prefix
    return changed


def set_turbo(wf, on):
    """FireRed turbo = the Lightning LoRA, 8 steps and CFG 1; off = 40 steps and CFG 4. One boolean drives all three."""
    n = prompt_node(wf)
    if n and isinstance(n["widgets_values"][1], bool):
        n["widgets_values"][1] = on
        if isinstance(n.get("widgets_values_named"), dict):
            n["widgets_values_named"]["value"] = on
    for sg in wf.get("definitions", {}).get("subgraphs", []):
        for node in sg["nodes"]:
            if node["type"] == "PrimitiveBoolean":
                node["widgets_values"][0] = on


def set_video(wf, prompt_text, engine_cfg):
    """Apply a video prompt's header (Size, Length) and the engine's turbo setting to a MiniMax workflow; return the source image name."""
    n = prompt_node(wf)
    named = n.get("widgets_values_named") or {}
    names = list(named)
    def put(key, val):
        if key in named:
            n["widgets_values"][names.index(key)] = val
            named[key] = val
    size = re.search(r"^Size:\s*(\d+)x(\d+)", prompt_text, re.M)
    secs = re.search(r"^Length:\s*([\d.]+)", prompt_text, re.M)
    src = re.search(r"^Source image:\s*(\S+)", prompt_text, re.M)
    if size:
        put("width", int(size.group(1)))
        put("height", int(size.group(2)))
    if secs:
        put("value_1", float(secs.group(1)))
    put("value", bool(engine_cfg.get("turbo", True)))  # turbo = 8-step LoRA
    return src.group(1) if src and not src.group(1).startswith("(") else None


def input_image(wf):
    n = node_of(wf, "LoadImage")
    return n["widgets_values"][0] if n else None


# ---------- prompts ----------

def split_prompt(text):
    m = re.search(r"\nprompt:\n\n(.*?)\n\n-{10,}\nnegative prompt:\n\n(.*?)\s*$", text, re.S)
    if not m:
        raise ValueError("not a generated prompt file (no prompt:/negative prompt: blocks)")
    return m.group(1).strip(), m.group(2).strip()


ENGINES = {"qwen": "Qwen", "firered": "FireRed", "minimax": "MiniMax"}


def engine_prompt(cfg, item, pos):
    """The positive prompt an engine should get. FireRed can pull the Environment up beside the fidelity paragraph and tell the
    model to replace the studio backdrop (envFirst), and adds a magic-effects instruction (fx) on the scenes listed in fxScenes."""
    fr = cfg.get("engines", {}).get("firered", {})
    m = re.search(r"_Scene_(.+)$", item["stem"])
    if item.get("engine") != "firered" or not m:
        return pos
    scene = m.group(1)
    if scene in fr.get("envFirst", []):
        env = re.search(r"^Environment: (.*)\n\n?", pos, re.M)
        if env:
            rest = pos[:env.start()] + pos[env.end():]
            anchor = re.search(r"^Maintain strict fidelity.*\n\n", rest, re.M)
            if anchor:
                block = "Background: replace the plain studio backdrop of the incoming image completely with this environment: " + env.group(1) + "\n\n"
                pos = rest[:anchor.end()] + block + rest[anchor.end():]
    if fr.get("fx") and (fr.get("fxScenes") == "*" or scene in fr.get("fxScenes", [])):
        pos = pos + "\n\n" + fr["fx"]
    return pos


def prompt_index(cfg, engine="qwen"):
    out = []
    for p in sorted(PROMPTS.glob("**/*.txt")):
        rel = p.relative_to(PROMPTS)
        if "_archive" in rel.parts or len(rel.parts) < 4 or rel.parts[0] in cfg.get("skipGroups", []):
            continue
        group, hero, stagedir = rel.parts[0], rel.parts[1], rel.parts[2]
        if (stagedir == "video") != (engine == "minimax"):  # video prompts feed only the MiniMax engine
            continue
        family = list(rel.parts[3:-1])
        stem = p.stem
        if not stem.startswith(hero + "_"):
            continue
        name = f"{hero}_{ENGINES[engine]}_{stem[len(hero) + 1:]}"
        folder = cfg.get("stageFolders", {}).get(stagedir, stagedir)
        out.append({"path": p, "group": group, "hero": hero, "stage": stagedir, "stem": stem, "name": name,
                    "prefix": "/".join([group, hero, folder] + family + [name])})
    return out


# ---------- input images ----------

def infer_input(hero):
    """The A-pose image most of a hero's non-pose workflows already read."""
    pat = re.compile(rf"^{re.escape(hero)}_Qwen_X_Pose_\d+_\.png$")
    seen = collections.Counter()
    for p in hero_files(hero):
        if stage_of(p.name) == "poses":
            continue
        try:
            img = input_image(read_wf(p))
        except ValueError:
            continue
        if img and pat.match(img) and not img.endswith("_00001_.png"):
            seen[img] += 1
    return seen.most_common(1)[0][0] if seen else None


def input_for(cfg, hero, stage):
    conf = cfg.get("inputs", {}).get(hero)
    if isinstance(conf, dict):
        conf = conf.get(stage) or conf.get("default")
    return conf or infer_input(hero) or f"{hero}_Qwen_X_Pose_00001_.png"


# ---------- selection ----------

def pick_targets(cfg, args, default):
    """Workspaces to act on: -w names, --to tier, else the default ('testing' or all)."""
    ws = cfg["workspaces"]
    if args.workspace:
        bad = [n for n in args.workspace if n not in ws]
        if bad:
            sys.exit(f"Unknown workspace(s): {bad}. Known: {list(ws)}")
        return list(args.workspace)
    tier = args.to or default
    if tier == "all":
        return list(ws)
    names = [n for n in (tier_workspaces(cfg, tier, args.hero, args.group, route_stage(args)) if tier != "dev" else [cfg["dev"][0]])]
    unknown = [n for n in names if n not in ws]
    for n in unknown:
        print(f"note: '{n}' is a {tier} target but is not listed under workspaces in workspaces.json")
    return [n for n in names if n in ws]


def selected(cfg, ws, args, repo):
    """Repo files a workspace should hold, after the filters."""
    out = {}
    for name, (group, hero, p) in repo.items():
        if not holds(cfg, ws, group, hero, stage_of(name)):
            continue
        if args.hero and hero.lower() != args.hero.lower():
            continue
        if args.group and group != args.group:
            continue
        if not stage_ok(args, name):
            continue
        if args.match and args.match.lower() not in name.lower():
            continue
        out[name] = (group, hero, p)
    return out


def classify(repo_p, inst_p):
    try:
        rv = get_values(read_wf(repo_p))
        iv = get_values(read_wf(inst_p))
    except ValueError:
        return "unreadable"
    if rv is None or iv is None:
        return "unreadable"
    return "aligned" if rv == iv else "stale"


# ---------- commands ----------

def cmd_list(args):
    cfg = load_cfg()
    repo = repo_files(cfg)
    print(f"installs root: {cfg['installsRoot']}")
    print(f"dev workspaces (default deploy target first): {', '.join(cfg['dev'])}")
    print("workspaces:")
    for ws, info in cfg["workspaces"].items():
        found = "found" if install_exists(cfg, ws, args.root) else "MISSING"
        flags = ",".join(k for k in ("templates", "legacy") if info.get(k))
        held = sum(1 for n, (g, h, _p) in repo.items() if holds(cfg, ws, g, h, stage_of(n)))
        print(f"  {ws:22} {info['status']:9} install={found:7} holds={held:3} {flags:16} {info['role']}")
    print("sets (repo):")
    for g in sorted({g for g, _, _ in repo.values()}):
        for h in sorted({h for gg, h, _ in repo.values() if gg == g}):
            stages = collections.Counter(stage_of(n) for n, (gg, hh, _) in repo.items() if hh == h)
            def route(tier):
                studio, scene = targets_for(cfg, tier, g, h, "poses"), targets_for(cfg, tier, g, h, "scene")
                return (",".join(studio) or "-") if studio == scene else f"studio {','.join(studio) or '-'} / scene {','.join(scene) or '-'}"
            print(f"  {g}/{h:12} {sum(stages.values()):3}  uat->{route('uat')}  prod->{route('prod')}   "
                  + ", ".join(f"{s} {c}" for s, c in sorted(stages.items())))


def curated_files():
    """{name: (group, hero, path)} for hand-curated workflows in workflows/_curated/<set>/<Hero>/. make and deploy never touch them."""
    out = {}
    if CURATED.is_dir():
        for g in sorted(CURATED.iterdir()):
            for h in sorted(g.iterdir()) if g.is_dir() else []:
                for p in sorted(h.glob("*.json")) if h.is_dir() else []:
                    out[p.name] = (g.name, h.name, p)
    return out


def same_workflow(a, b):
    """Same graph, whatever the formatting: ComfyUI re-saves files with its own spacing."""
    return read_wf(a) == read_wf(b)


def lint(cfg, repo):
    idx = {i["stem"]: i for i in prompt_index(cfg)}
    out = [f"{n}: exists both as a generated and a curated workflow (rename the curated one)" for n in sorted(set(repo) & set(curated_files()))]
    for name, (group, hero, p) in repo.items():
        try:
            wf = read_wf(p)
        except ValueError:
            out.append(f"{hero}/{name}: unreadable json")
            continue
        vals = get_values(wf)
        if not vals:
            continue
        pos, neg, prefix = vals
        stem = name[:-5]
        if prefix.rsplit("/", 1)[-1] != stem:
            out.append(f"{hero}/{name}: prefix ends in '{prefix.rsplit('/', 1)[-1]}', expected '{stem}'")
        m = re.match(r"^(.+?)_(?:Qwen|FireRed|MiniMax)_(.+)$", stem)
        item = idx.get(f"{m.group(1)}_{m.group(2)}") if m else None
        if not item:
            continue
        try:
            ppos, pneg = split_prompt(item["path"].read_text(encoding="utf-8"))
            ppos = engine_prompt(cfg, {**item, "engine": engine_of(name)}, ppos)
        except ValueError:
            continue
        if pos.strip() != ppos or (engine_of(name) == "qwen" and neg.strip() != pneg):
            out.append(f"{hero}/{name}: prompt is out of date (make --match {item['stem']})")
    return out


def cmd_status(args):
    cfg = load_cfg()
    repo = repo_files(cfg)
    cur = curated_files()
    groups = hero_groups()
    for ws in pick_targets(cfg, args, "all"):
        if not install_exists(cfg, ws, args.root):
            print(f"{ws}: workspace not found under {args.root or cfg['installsRoot']}")
            continue
        info = cfg["workspaces"][ws]
        inst = install_files(cfg, ws, args.root)
        rows = collections.defaultdict(list)
        for name, (g, h, p) in selected(cfg, ws, args, repo).items():
            rows["missing" if name not in inst else classify(p, inst[name])].append(name)
        for name in inst:
            h = hero_of(name)
            if name in repo or not h or not holds(cfg, ws, groups[h], h, stage_of(name)):
                continue
            if args.hero and h.lower() != args.hero.lower():
                continue
            if name in cur:
                rows["curated" if same_workflow(cur[name][2], inst[name]) else "curated-changed"].append(name)
                continue
            rows["legacy" if info.get("legacy") else "install-only"].append(name)
        for name in selected(cfg, ws, args, cur):
            if name not in inst:
                rows["curated-missing"].append(name)
        counts = ", ".join(f"{len(rows[k])} {k}" for k in ("aligned", "stale", "missing", "install-only", "curated", "curated-changed", "curated-missing", "legacy", "unreadable") if rows[k] or k in ("aligned", "stale", "missing", "install-only"))
        print(f"{ws} [{info['status']}]: {counts}")
        hints = {"stale": "deploy", "missing": "deploy", "install-only": "pull: keeps it as a curated workflow", "curated-changed": "pull: captures your edits",
                 "curated-missing": "deploy --curated", "legacy": "old hand-made, no generated prompt"}
        for k, names in rows.items():
            if k in hints and names and (args.verbose or len(names) <= 5):
                print(f"    {k} ({hints[k]}): " + ", ".join(names))
        if args.templates:
            tpl, itpl = template_files(cfg), {n: p for n, p in inst.items() if is_template(cfg, n)}
            st = collections.Counter("missing" if n not in itpl else ("aligned" if same_bytes(p, itpl[n]) else "differs") for n, p in tpl.items())
            extra = [n for n in itpl if n not in tpl]
            print(f"    stage templates: {st['aligned']} aligned, {st['differs']} differ, {st['missing']} missing, {len(extra)} only in workspace")
    if args.lint:
        for line in lint(cfg, repo):
            print("    lint: " + line)


def backup(stamp, ws, name, src):
    b = BACKUPS / stamp / ws / name
    b.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, b)


def cmd_deploy(args):
    cfg = load_cfg()
    repo = repo_files(cfg)
    if not args.templates and not (args.hero or args.group or args.stage or args.cls or args.match or args.all):
        sys.exit("Deploy needs a filter (--hero, --group, --stage, --class, --match) or --all, so a whole playground is never pushed by accident.")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for ws in pick_targets(cfg, args, "dev"):
        if not install_exists(cfg, ws, args.root):
            print(f"{ws}: workspace not created yet under {args.root or cfg['installsRoot']}, skipped")
            continue
        dest = install_dir(cfg, ws, args.root)
        inst = install_files(cfg, ws, args.root)
        tally = collections.Counter()
        if args.templates:
            for name, p in template_files(cfg).items():
                if name not in inst:
                    print(f"  template {ws}/{name} (new)")
                    if not args.dry_run:
                        shutil.copy2(p, dest / name)
                    tally["new"] += 1
                elif same_bytes(p, inst[name]):
                    tally["aligned"] += 1
                elif args.overwrite:
                    print(f"  template {ws}/{name} (replace)")
                    if not args.dry_run:
                        backup(stamp, ws, name, inst[name])
                        shutil.copy2(p, inst[name])
                    tally["updated"] += 1
                else:
                    print(f"  SKIP     {ws}/{name} differs from the repo template; use --overwrite")
                    tally["skipped"] += 1
            print(f"{ws} templates: " + ", ".join(f"{v} {k}" for k, v in tally.items()) + (" (dry run)" if args.dry_run else ""))
            continue
        for name, (g, h, p) in selected(cfg, ws, args, repo).items():
            replace = args.overwrite or (cfg["workspaces"][ws].get("legacy", False) and not getattr(args, "patch_only", False))
            if name not in inst and getattr(args, "existing", False):
                continue
            if name in inst and getattr(args, "new_only", False):
                tally["kept"] += 1
                continue
            if name not in inst:
                print(f"  new      {ws}/{name}")
                if not args.dry_run:
                    write_wf(dest / name, read_wf(p))
                tally["new"] += 1
                continue
            state = classify(p, inst[name])
            if state == "aligned" and not replace:
                tally["aligned"] += 1
                continue
            if state == "unreadable" and not replace:
                print(f"  SKIP     {ws}/{name} is not a Qwen workflow in one of the two places; use --overwrite")
                tally["skipped"] += 1
                continue
            print(f"  {'replace ' if replace else 'prompt  '} {ws}/{name}" + ("" if replace else f"  (keeps input {input_image(read_wf(inst[name]))})"))
            if not args.dry_run:
                backup(stamp, ws, name, inst[name])
                if replace:
                    write_wf(inst[name], read_wf(p))
                else:
                    wf = read_wf(inst[name])
                    patch_wf(wf, *get_values(read_wf(p)))
                    write_wf(inst[name], wf)
            tally["updated"] += 1
        if getattr(args, "curated", False):
            for name, (g, h, p) in selected(cfg, ws, args, curated_files()).items():
                if name not in inst:
                    print(f"  curated  {ws}/{name} (new)")
                    if not args.dry_run:
                        write_wf(dest / name, read_wf(p))
                    tally["curated"] += 1
                elif same_workflow(p, inst[name]):
                    tally["aligned"] += 1
                elif args.overwrite:
                    print(f"  curated  {ws}/{name} (replace)")
                    if not args.dry_run:
                        backup(stamp, ws, name, inst[name])
                        write_wf(inst[name], read_wf(p))
                    tally["curated"] += 1
                else:
                    print(f"  SKIP     {ws}/{name} differs from the curated copy (your edits?): pull it, or use --overwrite")
                    tally["skipped"] += 1
        print(f"{ws}: " + ", ".join(f"{v} {k}" for k, v in tally.items()) + (" (dry run)" if args.dry_run else ""))
    print("Restart the ComfyUI workspace (or reload the workflow list) to see changes.")


def cmd_cleanup(args):
    """Remove plain duplicates from the dev workspace once the same workflow sits in its routed UAT workspace(s).

    A dev file is removed only if it is a generated workflow and every UAT workspace that serves it holds an identical copy.
    Anything else stays: files not in the repo (yours, curated or renamed), edited copies, and files not yet delivered.
    Default is a preview; --apply moves the duplicates to workflows/.sync/backup/ (nothing is deleted)."""
    cfg = load_cfg()
    repo = repo_files(cfg)
    groups = hero_groups()
    src = args.workspace[0] if args.workspace else cfg["dev"][0]
    if not install_exists(cfg, src, args.root):
        sys.exit(f"{src}: workspace not found")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    cache, tally, kept = {}, collections.Counter(), collections.defaultdict(list)

    def files_of(ws):
        if ws not in cache:
            cache[ws] = install_files(cfg, ws, args.root) if install_exists(cfg, ws, args.root) else None
        return cache[ws]

    for name, p in sorted(install_files(cfg, src, args.root).items()):
        h = hero_of(name)
        if not h or is_template(cfg, name) or excluded(cfg, name):
            continue
        g = groups[h]
        if (args.hero and h.lower() != args.hero.lower()) or (args.group and g != args.group) or not stage_ok(args, name) \
                or (args.match and args.match.lower() not in name.lower()):
            continue
        why = None
        dests = [w for w in targets_for(cfg, "uat", g, h, stage_of(name)) if w != src]
        if name not in repo:
            why = "not a generated workflow in the repo (yours, curated or renamed)"
        elif not dests:
            why = "no UAT workspace serves it"
        else:
            for w in dests:
                held = files_of(w)
                if held is None:
                    why = f"{w} does not exist yet"
                elif name not in held:
                    why = f"not delivered to {w} yet"
                elif not same_workflow(p, held[name]):
                    why = f"differs from the copy in {w} (edited?)"
                if why:
                    break
        if why:
            kept[why].append(name)
            continue
        print(f"  {'remove ' if args.apply else 'would remove'}  {name}  (also in {', '.join(dests)})")
        tally["duplicates"] += 1
        if args.apply:
            b = BACKUPS / stamp / (src + " (cleaned)") / name
            b.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(b))
    for why, names in kept.items():
        print(f"  KEEP {len(names):4}  {why}")
        for n in names[: args.show]:
            print(f"           {n}")
    print(f"{src}: {tally['duplicates']} duplicate(s) " + ("moved to backup" if args.apply else "would be removed (preview; use --apply)") + f", {sum(map(len, kept.values()))} kept")


def cmd_promote(args):
    """Move approved workflows up a tier without leaving duplicates behind."""
    cfg = load_cfg()
    if not (args.hero or args.group or args.stage or args.cls or args.match or args.all):
        sys.exit("Promote needs a filter (--hero, --group, --stage, --class, --match) or --all.")
    if args.src == args.to or TIERS.index(args.src) > TIERS.index(args.to):
        sys.exit(f"Promote goes up: dev -> uat -> prod (got {args.src} -> {args.to}).")
    repo = repo_files(cfg)
    groups = hero_groups()
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    moved = collections.Counter()
    if args.workspace:
        sources = args.workspace
    elif args.src == "dev":
        sources = [cfg["dev"][0]]
    else:
        sources = tier_workspaces(cfg, args.src, args.hero, args.group, route_stage(args))
    for src_ws in sources:
        if src_ws not in cfg["workspaces"] or not install_exists(cfg, src_ws, args.root):
            print(f"{src_ws}: source workspace not found, skipped")
            continue
        inst = install_files(cfg, src_ws, args.root)
        for name, p in inst.items():
            h = hero_of(name)
            if not h or is_template(cfg, name):
                continue
            g = groups[h]
            if not holds(cfg, src_ws, g, h, stage_of(name)):
                continue
            if (args.hero and h.lower() != args.hero.lower()) or (args.group and g != args.group):
                continue
            if not stage_ok(args, name) or (args.match and args.match.lower() not in name.lower()):
                continue
            dests = [w for w in targets_for(cfg, args.to, g, h, stage_of(name)) if w in cfg["workspaces"] and install_exists(cfg, w, args.root)]
            if not dests:
                print(f"  HOLD     {name}: no {args.to} workspace exists yet for {h} (left in {src_ws})")
                moved["held"] += 1
                continue
            wf = read_wf(p)
            print(f"  promote  {name}: {src_ws} -> {', '.join(dests)}" + ("" if args.keep else f" (leaves {src_ws})"))
            if args.dry_run:
                moved["promoted"] += 1
                continue
            write_wf(repo_path(cfg, g, h, name), wf)
            for w in dests:
                existing = install_files(cfg, w, args.root).get(name)
                if existing:
                    backup(stamp, w, name, existing)
                write_wf(existing or install_dir(cfg, w, args.root) / name, wf)
            if not args.keep:
                b = BACKUPS / stamp / (src_ws + " (promoted)") / name
                b.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(p), str(b))
            moved["promoted"] += 1
        print(f"{src_ws}: " + ", ".join(f"{v} {k}" for k, v in moved.items()) + (" (dry run)" if args.dry_run else ""))
    print("Restart the affected ComfyUI workspaces to see changes.")


def cmd_pull(args):
    cfg = load_cfg()
    repo = repo_files(cfg)
    cur = curated_files()
    groups = hero_groups()
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for ws in pick_targets(cfg, args, "dev"):
        if not install_exists(cfg, ws, args.root):
            print(f"{ws}: workspace not found, skipped")
            continue
        info = cfg["workspaces"][ws]
        done = skipped = 0
        if args.templates:
            for name, p in install_files(cfg, ws, args.root).items():
                if not is_template(cfg, name):
                    continue
                dst = WF / "_templates" / name
                if dst.exists() and not args.force:
                    skipped += 1
                    continue
                print(f"  pull   {ws}/{name} -> workflows/_templates/")
                if not args.dry_run:
                    shutil.copy2(p, dst)
                done += 1
            print(f"{ws} templates: pulled {done}, left {skipped} existing" + (" (dry run)" if args.dry_run else ""))
            continue
        if info.get("pull") is False and not (args.force or args.include_legacy):
            print(f"{ws}: pulling is turned off for this workspace (old hand-made workflows); use --include-legacy to capture them as curated")
            continue
        for name, p in install_files(cfg, ws, args.root).items():
            h = hero_of(name)
            if not h or is_template(cfg, name) or not holds(cfg, ws, groups[h], h, stage_of(name)):
                continue
            if args.hero and h.lower() != args.hero.lower():
                continue
            if args.group and groups[h] != args.group:
                continue
            if not stage_ok(args, name):
                continue
            if args.match and args.match.lower() not in name.lower():
                continue
            if name in cur:  # a hand-curated workflow: the workspace is where it is edited, so keep the repo copy in step
                wf = read_wf(p)
                prefix_fix = set_prefix(wf, curated_prefix(groups[h], h, name))  # curated work writes to <group>/<Hero>/_curated/
                if prefix_fix and not args.dry_run:
                    backup(stamp, ws, name, p)
                    write_wf(p, wf)  # the workspace copy gets the same prefix so the two stay identical
                if read_wf(cur[name][2]) == wf:
                    skipped += 1
                    continue
                print(f"  update curated  {ws}/{name}")
                if not args.dry_run:
                    write_wf(cur[name][2], wf)
                done += 1
                continue
            if name in repo and not args.force:
                skipped += 1
                continue
            if name in repo:
                dst = repo_path(cfg, groups[h], h, name)
            else:
                dst = CURATED / groups[h] / h / name  # not generated by us: keep it as a curated workflow
            print(f"  pull   {ws}/{name} -> {dst.parent.relative_to(ROOT).as_posix()}/")
            wf = read_wf(p)
            if dst.is_relative_to(CURATED):
                prefix = curated_prefix(groups[h], h, name)
                print(f"           output folder: {prefix.rsplit('/', 1)[0]}/")
                if set_prefix(wf, prefix) and not args.dry_run:
                    backup(stamp, ws, name, p)
                    write_wf(p, wf)
            if not args.dry_run:
                write_wf(dst, wf)
            done += 1
        print(f"{ws}: pulled {done}, left {skipped} unchanged" + (" (dry run)" if args.dry_run else ""))


def cmd_fork(args):
    """Copy a generated workflow to workflows/_curated under a new name, so it can be hand-edited in ComfyUI without being regenerated."""
    cfg = load_cfg()
    repo, cur = repo_files(cfg), curated_files()
    src = args.name if args.name.endswith(".json") else args.name + ".json"
    if src not in repo:
        sys.exit(f"No generated workflow named {src} (try: status -v, or the name without .json).")
    g, h, p = repo[src]
    new = f"{src[:-5]}_{args.tag}.json"
    if new in repo or new in cur:
        sys.exit(f"{new} already exists.")
    wf = read_wf(p)
    set_prefix(wf, curated_prefix(g, h, new))
    wf.setdefault("extra", {})["curated"] = {"derivedFrom": src, "tag": args.tag, "date": datetime.date.today().isoformat()}
    wf["id"] = str(uuid.uuid4())
    dst = CURATED / g / h / new
    print(f"  fork  {src} -> {dst.relative_to(ROOT).as_posix()}")
    if args.dry_run:
        return
    write_wf(dst, wf)
    ws = cfg["dev"][0]
    if not args.no_deploy and install_exists(cfg, ws, args.root):
        write_wf(install_dir(cfg, ws, args.root) / new, wf)
        print(f"  deployed to {ws}: open {new} in ComfyUI, edit it, save it, then run pull to keep your changes")


def cmd_make(args):
    cfg = load_cfg()
    engines = {"firered": ["firered"], "minimax": ["minimax"], "both": ["qwen", "firered"]}.get(args.engine, ["qwen"])
    items = []
    for engine in engines:
        its = prompt_index(cfg, engine)
        for i in its:
            i["engine"] = engine
        if engine == "firered" and not (args.stage or args.cls):
            its = [i for i in its if class_of(i["stage"]) in cfg["engines"]["firered"].get("classes", ["scene"])]
        items += its
    if args.group:
        items = [i for i in items if i["group"] == args.group]
    if args.hero:
        items = [i for i in items if i["hero"].lower() == args.hero.lower()]
    if args.stage or args.cls:
        items = [i for i in items if stage_ok(args, i["stage"], True)]
    if args.match:
        items = [i for i in items if args.match.lower() in i["stem"].lower()]
    tally = {"created": 0, "updated": 0, "unchanged": 0, "missing": 0}
    for it in items:
        target = engine_roots(cfg)[it["engine"]] / it["group"] / it["hero"] / f"{it['name']}.json"
        pos, neg = split_prompt(it["path"].read_text(encoding="utf-8"))
        pos = engine_prompt(cfg, it, pos)
        if target.exists():
            wf = read_wf(target)
            if patch_wf(wf, pos, neg, it["prefix"]):
                if not args.dry_run:
                    write_wf(target, wf)
                tally["updated"] += 1
                print(f"  updated  {it['group']}/{it['hero']}/{target.name}")
            else:
                tally["unchanged"] += 1
            continue
        if not args.create:
            tally["missing"] += 1
            if args.verbose:
                print(f"  missing  {it['group']}/{it['hero']}/{target.name}")
            continue
        is_apose = it["engine"] == "qwen" and re.match(rf"^{re.escape(it['hero'])}_X_Pose", it["stem"]) is not None
        master = ROOT / (cfg["engines"][it["engine"]]["template"] if it["engine"] in ("firered", "minimax")
                         else cfg["templates"]["poses" if is_apose else "default"])
        if not master.exists():
            sys.exit(f"Master template not found: {master}")
        wf = read_wf(master)
        patch_wf(wf, pos, neg, it["prefix"])
        if it["engine"] == "firered":
            set_turbo(wf, cfg["engines"]["firered"].get("turbo", True))
        video = set_video(wf, it["path"].read_text(encoding="utf-8"), cfg["engines"]["minimax"]) if it["engine"] == "minimax" else None
        wf["id"] = str(uuid.uuid4())
        ln = node_of(wf, "LoadImage")
        want = args.input or video or (None if is_apose else input_for(cfg, it["hero"], it["stage"]))
        if ln and want:
            ln["widgets_values"][0] = want
        if not args.dry_run:
            write_wf(target, wf)
        tally["created"] += 1
        print(f"  created  {it['group']}/{it['hero']}/{target.name}  (input: {ln['widgets_values'][0] if ln else '?'})")
    print("make: " + ", ".join(f"{v} {k}" for k, v in tally.items()) + (" (dry run)" if args.dry_run else ""))
    if tally["missing"] and not args.create:
        print("      (use --create to build the missing workflows from the master template)")


def cmd_inputs(args):
    cfg = load_cfg()
    placeholder = re.compile(r"^(.+)_Qwen_X_Pose_00001_\.png$")
    for h in sorted(hero_groups()):
        if not hero_files(h):
            continue
        conf = cfg.get("inputs", {}).get(h)
        inferred = infer_input(h)
        print(f"  {h:12} configured={conf or '-':34} inferred={inferred or '-'}")
        if not args.fix:
            continue
        want = input_for(cfg, h, "scene")
        for p in hero_files(h):
            if stage_of(p.name) == "poses":
                continue
            wf = read_wf(p)
            ln = node_of(wf, "LoadImage")
            if ln and placeholder.match(ln["widgets_values"][0]) and want != ln["widgets_values"][0]:
                print(f"      fix {p.name}: {ln['widgets_values'][0]} -> {want}")
                if not args.dry_run:
                    ln["widgets_values"][0] = want
                    write_wf(p, wf)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, targets=False, filters=False):
        p.add_argument("--root", help="override installsRoot (testing)")
        p.add_argument("--dry-run", action="store_true")
        if targets:
            p.add_argument("--to", choices=list(TIERS), help="target tier (default: dev)")
            p.add_argument("-w", "--workspace", action="append", help="a specific workspace (repeatable)")
        if filters:
            p.add_argument("--hero")
            p.add_argument("--group", help="prompt group, e.g. drakn-sisters, angel-primes")
            p.add_argument("--stage", help="prompt folder: poses, head, scene, hair, motion, armor, clothing")
            p.add_argument("--class", dest="cls", choices=["studio", "scene"], help="every stage of one class (scene, or all studio stages)")
            p.add_argument("--engine", choices=["qwen", "firered", "minimax", "both"], help="restrict to one engine's workflows (make: which to build; default qwen)")
            p.add_argument("--match", help="substring of the file name")

    common(sub.add_parser("list"))
    s = sub.add_parser("status")
    common(s, True, True)
    s.add_argument("--lint", action="store_true")
    s.add_argument("--templates", action="store_true", help="also compare the ST?_ stage templates")
    s.add_argument("-v", "--verbose", action="store_true")
    s = sub.add_parser("deploy")
    common(s, True, True)
    s.add_argument("--all", action="store_true", help="allow a deploy with no filter")
    s.add_argument("--templates", action="store_true", help="deploy the ST?_ stage templates instead of hero workflows")
    s.add_argument("--overwrite", action="store_true", help="replace the workspace file instead of updating its prompt values")
    s.add_argument("--curated", action="store_true", help="also copy hand-curated workflows (workflows/_curated) the workspace lacks")
    s.add_argument("--existing", action="store_true", help="only refresh files the workspace already has; add nothing new")
    s.add_argument("--patch-only", action="store_true", help="in a legacy workspace too, only update prompt values in place; never replace a whole workflow")
    s.add_argument("--new-only", action="store_true", help="only add files the workspace lacks; never touch ones it already has (even in a legacy workspace)")
    s = sub.add_parser("cleanup")
    common(s, False, True)
    s.add_argument("-w", "--workspace", action="append", help="workspace to clean (default: the dev workspace)")
    s.add_argument("--apply", action="store_true", help="really move the duplicates to backup (default: preview only)")
    s.add_argument("--show", type=int, default=5, help="names to list per kept reason")
    s = sub.add_parser("fork")
    common(s)
    s.add_argument("name", help="generated workflow to copy, e.g. Drakness_MiniMax_Video_X_Pose_Laugh")
    s.add_argument("--as", dest="tag", required=True, help="short tag added to the new name, e.g. Hand")
    s.add_argument("--no-deploy", action="store_true", help="only create the curated copy; do not put it in the dev workspace")
    s = sub.add_parser("promote")
    common(s, False, True)
    s.add_argument("--from", dest="src", choices=list(TIERS), default="dev", help="source tier (default: dev)")
    s.add_argument("--to", choices=list(TIERS), required=True, help="destination tier")
    s.add_argument("-w", "--workspace", action="append", help="source workspace(s), when not the default")
    s.add_argument("--all", action="store_true")
    s.add_argument("--keep", action="store_true", help="copy instead of move: leave the source workspace copy")
    s = sub.add_parser("pull")
    common(s, True, True)
    s.add_argument("--templates", action="store_true", help="pull the ST?_ stage templates instead of hero workflows")
    s.add_argument("--force", action="store_true", help="also replace repo copies")
    s.add_argument("--include-legacy", action="store_true", help="also pull from a workspace whose pulling is turned off (its old hand-made workflows); generated copies are never replaced")
    s = sub.add_parser("make")
    common(s, False, True)
    s.add_argument("--create", action="store_true", help="also build workflows that do not exist yet")
    s.add_argument("--input", help="LoadImage file for created workflows")
    s.add_argument("-v", "--verbose", action="store_true")
    s = sub.add_parser("inputs")
    common(s)
    s.add_argument("--fix", action="store_true", help="replace placeholder 00001 inputs with the inferred or configured pick")
    args = ap.parse_args(argv)
    {"list": cmd_list, "status": cmd_status, "deploy": cmd_deploy, "promote": cmd_promote, "cleanup": cmd_cleanup, "pull": cmd_pull, "make": cmd_make, "inputs": cmd_inputs, "fork": cmd_fork}[args.cmd](args)


if __name__ == "__main__":
    main()
