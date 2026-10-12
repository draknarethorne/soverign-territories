#!/usr/bin/env python3
"""Keep prompts, repo workflows and the local ComfyUI workspaces in step.

Repo layout follows the prompts:  workflows/<set>/<Hero>/<Hero>_Qwen_<Stage>_<Name>.json
(<set> is the prompt group: drakn-sisters, drakn-bound, angel-primes, elder-dragons ...).

ComfyUI workspaces are DEPLOY TARGETS configured in workflows/workspaces.json. A workspace is tied to a set of cards (a prompt group):
  home      the workspace(s) a set lives in (the "homes" rules): the default target of every command (Drakn Sisters for the sisters, Sovereign Dawn Series for the
            Sovereign Dawn cards, Sovereign Territories for the brand set, Angel Primes ...). A hero may have several (Drakness is kept beside Drakn Sisters
            to work through issues with zz_ items without polluting the shared workspace).
  accepts   a workspace may also take a set on request, for a while: Sovereign Territories accepts any set (promotional videos, reels, a scene kept next to the art),
            Sovereign Dawn Series accepts the Drakn sets. You ask with deploy -w "<Workspace>" --group G; the copy is temporary and `cleanup -w` removes it when you are done.
            A workspace that neither homes nor accepts a set is refused, so a set can never land in the wrong place.
Which workspace is home for which set is configured under "homes"; nothing is hard-coded, and a set with no home workspace stops the command instead of landing
somewhere else. Only workspaces whose status is "active" and whose install exists are written to; a planned one is skipped with a message.

Hand-made workflows are mastered in the workspace: anything under a zz_ folder (zz_Curated, zz_Test, zz_Shots) or named zz_Curated_ or test_ is never
replaced, moved or removed by deploy, cleanup or tidy. Bring them into the repo with pull.

Commands
  list                                 workspaces, homes and repo contents
  status  [targets] [filters] [--lint]      repo vs workspace(s): aligned / stale / missing / install-only / published / unrouted / legacy
  make    [filters] [--create]         prompt -> repo workflow: set positive, negative, filename prefix (and file name)
  deploy  [targets] [filters]          repo -> home workspace(s), or -w a workspace that accepts the set. Existing workflows only get the three
                                       prompt values updated, so input image, seed and toggles survive. --overwrite replaces.
  cleanup -w WORKSPACE [filters] [--apply]
                                       preview (or --apply) removing the generated workflows the workspace is not home for (clone leftovers and finished temporary
                                       publishes), once their home workspace has an identical copy; also removes empty folders (not zz_). Everything else stays
                                       (hand-made, not in the repo, edited, not delivered). Moved to backup, never deleted.
  setup   -w WORKSPACE [--apply]       the whole job for one workspace: deploy every set it is home for (plus curated workflows and shots), tidy the folders,
                                       cleanup what it is not home for, show the status. A preview unless --apply.
  pull    [targets] [filters]          workspace -> repo. Files we did not generate are kept as CURATED workflows
                                       (workflows/_curated/<set>/<Hero>/); later edits to a curated file are captured too.
                                       --force also replaces generated repo copies.
  fork    NAME --as TAG                copy a generated workflow to _curated as NAME_TAG and put it in the hero's home workspace, to hand-edit in ComfyUI
  deploy  ... --curated                also copy curated workflows a workspace lacks (a differing workspace copy is never overwritten)
  inputs  [--fix]                      which A-pose image each hero's workflows read

targets:  (none) = home   |   -w <Workspace> (repeatable; must be home for the set or accept it)
filters:  --hero H  --group G  --stage S  --class studio|scene  --match TEXT   (stage = prompt folder: poses, head, scene, hair, motion, armor, clothing)
          deploy needs at least one filter, or --all.

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
import struct
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "generators"))
import art_layout  # noqa: E402  (phase_path: the pipeline folders of a workflow and its output)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import finals  # noqa: E402  (candidates and finals: tolerant name parsing and slots)
WF = ROOT / "workflows"
PROMPTS = ROOT / "prompts"
CFG_PATH = WF / "workspaces.json"
BACKUPS = WF / ".sync" / "backup"
CURATED = WF / "_curated"
TEST = WF / "_test"
# Curated workflow files carry this prefix so they sort to the bottom of a workspace list; a name with a render counter
# (Name_00001) is a workflow captured from a render and keeps its name. Test workflows (experiments, bisects) are kept in
# workflows/_test under a test_ prefix and are only pushed to a workspace on request (deploy --include tests).
CURATED_PREFIX = "zz_Curated_"
TEST_PREFIX = "test_"
# Inside a workspace, curated and test workflows sit in these folders, which sort after every generated stage folder.
CURATED_DIR = "zz_Curated"
TEST_DIR = "zz_Test"
# Shots: workflows you tuned for a specific render (seed, Turbo on or off). Saved in a workspace under zz_Shots/ (any subfolders) and kept
# in the repo under workflows/_shots/<set>/<Hero>/ with the same subfolders; never regenerated, never renamed, prefix left as you set it.
SHOTS = WF / "_shots"
SHOTS_DIR = "zz_Shots"
CAPTURED_NAME = re.compile(r"_\d{5}")


def plain_name(name):
    for prefix in (CURATED_PREFIX, TEST_PREFIX):
        if name.startswith(prefix):
            return name[len(prefix):]
    return name


def is_capture(rel, name):
    """A workflow ComfyUI saved from a render (a name with a counter, Hero_Qwen_Alpha_1_Prime_00004_) that sits outside the zz_ folders. It is a saved shot: it keeps the seed of that render,
    so it is captured as a shot (workflows/_shots) and never treated as a generated or an install-only workflow. A counter name already kept in workflows/_curated stays curated."""
    if not CAPTURED_NAME.search(name) or name.startswith((CURATED_PREFIX, TEST_PREFIX)) or pathlib.PurePath(rel).parts[0].startswith("zz_"):
        return False
    return name not in curated_files() and name not in test_files()


def curated_name(name):
    return name if name.startswith((CURATED_PREFIX, TEST_PREFIX)) or CAPTURED_NAME.search(name) else CURATED_PREFIX + name


# ---------- configuration ----------

def load_cfg():
    return json.loads(CFG_PATH.read_text(encoding="utf-8"))


def work_root(cfg):
    """The working drive folder that holds Sisters (originals) and Masters; accepts the old misspelled folder until it is renamed."""
    want = pathlib.Path(cfg.get("paths", {}).get("workRoot", "B:/Sovereign Territories"))
    old = pathlib.Path(str(want).replace("Sovereign", "Soverign"))
    return want if want.exists() or not old.exists() else old


def output_root(cfg):
    """The parent of every project output folder (ComfyUI-Outputs)."""
    return pathlib.Path(cfg.get("paths", {}).get("outputRoot") or cfg["sharedOutput"])


def output_home(cfg, group):
    """Where a set's images belong: <outputRoot>/<project folder>/<set>/ (the project comes from paths.outputFolders)."""
    project = cfg.get("paths", {}).get("outputFolders", {}).get(group)
    return output_root(cfg) / project / group if project else output_root(cfg) / group


def output_roots(cfg):
    """Existing output folders to search: the new root and the old shared one."""
    return [p for p in (output_root(cfg), pathlib.Path(cfg["sharedOutput"])) if p.is_dir()]


def input_dir(cfg, ws):
    """A workspace's own input folder when it exists, else the old shared one."""
    own = pathlib.Path(cfg.get("paths", {}).get("inputsRoot", "")) / ws
    return own if own.is_dir() else pathlib.Path(cfg["sharedInput"])


def input_dirs(cfg):
    """Every input folder in use: the shared one and each per-workspace one."""
    out = [pathlib.Path(cfg["sharedInput"])]
    root = pathlib.Path(cfg.get("paths", {}).get("inputsRoot", ""))
    if root.is_dir():
        out += sorted(p for p in root.iterdir() if p.is_dir())
    return [p for p in out if p.is_dir()]


def install_dir(cfg, ws, root=None):
    return pathlib.Path(root or cfg["installsRoot"]) / ws / cfg["workflowsSubpath"]


def install_exists(cfg, ws, root=None):
    return (pathlib.Path(root or cfg["installsRoot"]) / ws / "ComfyUI").is_dir()


def workspace_ready(cfg, ws, root=None):
    """(True, '') when a workspace may receive or lose files: it is listed, its status is active and its install exists. Otherwise (False, why)."""
    info = cfg["workspaces"].get(ws)
    if info is None:
        return False, "not listed under workspaces in workspaces.json"
    if info.get("status") != "active":
        return False, f"status is '{info.get('status')}', not active (set it to active in workflows/workspaces.json when the install is ready)"
    if not install_exists(cfg, ws, root):
        return False, f"workspace not created yet under {root or cfg['installsRoot']}"
    return True, ""


def ready_or_skip(cfg, ws, root=None):
    ok, why = workspace_ready(cfg, ws, root)
    if not ok:
        print(f"{ws}: {why}, skipped")
    return ok


def template_workspaces(cfg):
    """Workspaces flagged "templates": true; the ST stage templates are deployed to and pulled from these."""
    return [ws for ws, info in cfg["workspaces"].items() if info.get("templates")]


def is_hand_made(cfg, ws, path, root=None):
    """True for a workflow that is mastered in the workspace: anything under a zz_ folder (zz_Curated, zz_Test, zz_Shots) or named zz_Curated_ or test_.
    Tools never replace, move or remove these unless you ask for it by name; bring them into the repo with pull."""
    path = pathlib.Path(path)
    try:
        rel = path.relative_to(install_dir(cfg, ws, root))
    except ValueError:
        rel = pathlib.Path(path.name)
    return rel.parts[0].startswith("zz_") or path.name.startswith((CURATED_PREFIX, TEST_PREFIX))


def empty_dirs(d, ignore=()):
    """Folders below d that hold no file (counting the files in `ignore` as already gone), deepest first. Top-level zz_ folders and folders starting with . or _ are left alone."""
    ignore = set(ignore)
    out = []
    for folder in sorted((q for q in d.rglob("*") if q.is_dir()), key=lambda q: len(q.parts), reverse=True):
        if folder.relative_to(d).parts[0].startswith(("zz_", ".", "_")):
            continue
        if not any(f.is_file() and f not in ignore for f in folder.rglob("*")):
            out.append(folder)
    return out


def prune_empty_dirs(d, apply):
    """Remove the empty folders below d (only if apply); returns them. A folder with any file in it, even a non-workflow one, stays."""
    folders = empty_dirs(d)
    if apply:
        for folder in folders:
            if folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()
    return folders


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


def home_workspaces(cfg, group, hero, stage=None):
    """The workspaces a hero's workflows live in (the "homes" rules). Every matching rule counts, so a sister's own workspace and the shared one can both hold her work.

    A rule may carry "class": "studio" or "scene"; it then applies only to stages of that class."""
    out = []
    for r in cfg.get("homes", []):
        if "groups" in r and group not in r["groups"]:
            continue
        if "heroes" in r and hero not in r["heroes"]:
            continue
        if "class" in r and (stage is None or class_of(stage) != r["class"]):
            continue
        out.append(r["workspace"].format(hero=hero))
    return out


def is_home(cfg, ws, group, hero, stage=None):
    stages = [stage] if stage else list(CLASS_PROBE)
    return any(ws in home_workspaces(cfg, group, hero, s) for s in stages)


def accepts(cfg, ws, group):
    """True when a workspace may take this set on request (its "accepts" list names the group, or "*" for any set)."""
    acc = cfg["workspaces"].get(ws, {}).get("accepts", [])
    return "*" in acc or group in acc


def holds(cfg, ws, group, hero, stage=None):
    """True when the workspace may hold this hero's workflows: it is a home for the set, or it accepts the set on request."""
    return is_home(cfg, ws, group, hero, stage) or accepts(cfg, ws, group)


def home_names(cfg, hero=None, group=None, stage=None):
    """Every home workspace of the (filtered) heroes and stage."""
    names = []
    stages = [stage] if stage else list(CLASS_PROBE)
    for h, g in hero_groups().items():
        if (hero and h.lower() != hero.lower()) or (group and g != group):
            continue
        for s in stages:
            for w in home_workspaces(cfg, g, h, s):
                if w not in names:
                    names.append(w)
    return names


def groups_without_home(cfg, hero=None, group=None, stage=None):
    """The sets (filtered) that have no home workspace: a configuration gap, not something to fall back from."""
    stages = [stage] if stage else list(CLASS_PROBE)
    return sorted({g for h, g in hero_groups().items() if not ((hero and h.lower() != hero.lower()) or (group and g != group))
                   and not any(home_workspaces(cfg, g, h, s) for s in stages)})


def refused_groups(cfg, ws, hero=None, group=None, stage=None):
    """The (filtered) sets a workspace is neither home for nor accepts; deploying them there would be a mistake."""
    stages = [stage] if stage else list(CLASS_PROBE)
    return sorted({g for h, g in hero_groups().items() if not ((hero and h.lower() != hero.lower()) or (group and g != group))
                   and not accepts(cfg, ws, g) and not any(is_home(cfg, ws, g, h, s) for s in stages)})


# ---------- files ----------

def hero_groups():
    """{hero: group} from prompts/<group>/<Hero>/."""
    return {hero: group for hero, (group, _division) in hero_homes().items()}


def hero_homes():
    """{hero: (group, division or None)} from prompts/<group>/[<division>/]<Hero>/; a division folder is one listed in data/art/_settings/groups.json."""
    out = {}
    for g in sorted(PROMPTS.iterdir()):
        if g.is_dir() and not g.name.startswith(("_", ".")):
            divs = art_layout.divisions(g.name)
            for h in sorted(g.iterdir()):
                if not h.is_dir() or h.name.startswith(("_", ".")):
                    continue
                if h.name in divs:
                    for hh in sorted(h.iterdir()):
                        if hh.is_dir() and not hh.name.startswith(("_", ".")):
                            out[hh.name] = (g.name, h.name)
                else:
                    out[h.name] = (g.name, None)
    return out


def hero_dir(hero):
    """The folder of a hero below her group in the output tree: 'female/Seraphine' for a division group, 'Draknara' otherwise."""
    _group, division = hero_homes().get(hero, (None, None))
    return f"{division}/{hero}" if division else hero


def engine_roots(cfg):
    """{engine: folder holding its generated workflows}. FireRed is a local test engine kept out of git."""
    roots = {"qwen": WF}
    for engine in ("firered", "minimax"):
        if cfg.get("engines", {}).get(engine):
            roots[engine] = ROOT / cfg["engines"][engine]["dir"]
    return roots


def engine_of(name):
    return "firered" if "_FireRed_" in name else "minimax" if "_MiniMax_" in name else "qwen"


def is_staged(name):
    """A staged scene takes a pre-staged outfit render; it is built and kept in the repo but only deployed on request."""
    return "_Scene_Staged_" in plain_name(name)


def workspace_subdir(ws, wf):
    """Folder inside a workspace for a generated workflow, mirroring its output folder: <stage>/<family>/, with the hero
    first in a workspace that serves several heroes. Curated and test workflows are placed by CURATED_DIR and TEST_DIR instead."""
    s = save_node(wf)
    parts = s["widgets_values"][0].split("/") if s else []
    n = 2 if len(parts) > 1 and parts[1] in art_layout.divisions(parts[0]) else 1  # index of the hero folder (a division sits before it)
    if len(parts) < n + 3 or parts[n + 1].startswith(("_", ".")):
        return pathlib.Path()
    sub = pathlib.Path(*parts[n + 1:-1])
    if ws in hero_groups():
        return sub
    if load_cfg().get("layouts", {}).get(ws) == "stage-first":
        return sub / parts[n]  # a batch workspace: one stage and family holds every hero side by side
    return pathlib.Path(*parts[1:n + 1]) / sub


def special_dir(ws, base, hero):
    """zz_Curated, zz_Test and zz_Shots: flat in a sister's own workspace, one folder per hero in a shared one."""
    return pathlib.Path(base) if ws in hero_groups() or not hero else pathlib.Path(base) / hero


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
    """{name: path} for the workflows saved in a workspace (found by file name, whatever folder they sit in)."""
    out = {}
    d = install_dir(cfg, ws, root)
    if d.is_dir():
        for p in sorted(d.rglob("*.json")):
            rel = p.relative_to(d)
            if rel.parts[0] in (SHOTS_DIR, CANDIDATES_DIR, FINAL_DIR) or any(part.startswith((".", "_")) for part in rel.parts) or excluded(cfg, p.name) or is_capture(rel, p.name):
                continue
            out.setdefault(p.name, p)
    return out


def hero_of(name):
    prefix = plain_name(name).split("_", 1)[0]
    return prefix if prefix in hero_groups() else None


STAGE_WORDS = {"Scene": "scene", "Hair": "hair", "Motion": "motion", "Armor": "armor", "Clothing": "clothing",
               "Head": "head", "View": "poses", "Video": "video", "Brand": "brand", "Card": "card", "Alpha": "alpha"}


def stage_of(name):
    """Prompt folder a workflow file belongs to: Hero_Qwen_X_Pose -> poses, Hero_Qwen_Scene_Glamour -> scene."""
    m = re.match(r"^[^_]+_(?:Qwen|FireRed|MiniMax)_(.+?)(?:\.json)?$", plain_name(name))
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
    return node_of(wf, "SaveImage") or node_of(wf, "SaveImageAdvanced") or node_of(wf, "SaveVideo")


def get_values(wf):
    n, s = prompt_node(wf), save_node(wf)
    if not n or not s:
        return None
    return n["widgets_values"][0], n["widgets_values"][1], s["widgets_values"][0]


def curated_prefix(group, hero, name):
    """Hand-curated workflows write to <group>/<Hero>/_curated/<name>, apart from the generated art (the sort prefix is not part of the output name)."""
    name = plain_name(name)
    return f"{group}/{hero_dir(hero)}/_curated/{name[:-5] if name.endswith('.json') else name}"


def test_prefix(group, hero, name):
    name = plain_name(name)
    return f"{group}/{hero_dir(hero)}/_test/{name[:-5] if name.endswith('.json') else name}"


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


def set_size(wf, prompt_text):
    """Apply a 'Size: WxH' line from a generated prompt's header to the text-to-image latent; return True if it changed."""
    m = re.search(r"^Size: (\d+)x(\d+)", prompt_text, re.M)
    if not m:
        return False
    w, h = int(m.group(1)), int(m.group(2))
    changed = False
    for sg in wf.get("definitions", {}).get("subgraphs", []):
        for n in sg.get("nodes", []):
            if n.get("type") == "EmptySD3LatentImage" and n["widgets_values"][:2] != [w, h]:
                n["widgets_values"][0], n["widgets_values"][1] = w, h
                changed = True
    return changed


def randomize_seed(wf):
    """A generated workflow draws a new seed on every run (control_after_generate = randomize); only a final (zz_Final, or a record replayed by `make`) fixes one. Returns True if anything changed."""
    changed = False
    for node in subgraph_nodes(wf):
        if node.get("type") not in ("KSampler", "KSamplerAdvanced", "RandomNoise"):
            continue
        wv, named = node.get("widgets_values"), node.get("widgets_values_named")
        if isinstance(wv, list) and len(wv) > 1 and wv[1] in ("fixed", "increment", "decrement"):
            wv[1] = "randomize"
            changed = True
        if isinstance(named, dict) and named.get("control_after_generate") in ("fixed", "increment", "decrement"):
            named["control_after_generate"] = "randomize"
            changed = True
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


def video_format(prompt_text):
    m = re.search(r"^Format:\s*(\w+)", prompt_text, re.M)
    return m.group(1).lower() if m else None


def video_template(cfg, prompt_text):
    """The MiniMax master for a video prompt: its 'Format:' header picks one of engines.minimax.templates (reel = 9:16 for Facebook, match = the still's own shape)."""
    mm = cfg["engines"]["minimax"]
    fmt = video_format(prompt_text) or mm.get("format", "reel")
    if fmt not in mm["templates"]:
        sys.exit(f"Unknown video format '{fmt}'. Known: {list(mm['templates'])}")
    return mm["templates"][fmt]


def set_video(wf, prompt_text, engine_cfg):
    """Apply a video prompt's header (Length, Source image) and the engine's turbo setting to a MiniMax workflow; return the source image name.
    The canvas size is not set here: the template's own size nodes derive it from the still (a width or height that is wired is left alone)."""
    n = prompt_node(wf)
    named = n.get("widgets_values_named") or {}
    names = list(named)
    wired = {i["name"] for i in n.get("inputs", []) if i.get("link") is not None}
    def put(key, val):
        if key in named and key not in wired:
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


def standard_megapixels(cfg):
    """The 'megapixels' value that makes the edit templates' resize-to-total-pixels nodes keep the standard size (944x1104 = 0.993896). ComfyUI counts a megapixel as 1024 x 1024 pixels,
    so 1.0 is 1,048,576 pixels: at 1.0 a 944x1104 image came out 947x1107 (not a multiple of 16)."""
    w, h = cfg.get("standardSize") or (944, 1104)
    return round(w * h / (1024 * 1024), 6)


def size_nodes(wf):
    """The nodes inside a template's subgraph that rescale the incoming image to a total number of pixels (ImageScaleToTotalPixels, and ResizeImageMaskNode in 'scale total pixels' mode)
    when that number is not driven by another node. Left at 1 megapixel (1,048,576 pixels) they turn a 944x1104 image into 947x1107 (Flux.2 also wants multiples of 16)."""
    for node in subgraph_nodes(wf):
        linked = {i["name"] for i in node.get("inputs", []) if i.get("link") is not None}
        if node.get("type") == "ImageScaleToTotalPixels" and "megapixels" not in linked:
            yield node
        elif node.get("type") == "ResizeImageMaskNode" and node.get("widgets_values", [None])[0] == "scale total pixels" and "resize_type.megapixels" not in linked:
            yield node


def align_size(wf, cfg):
    """Point every such node at the standard size's megapixels (and a resolution step of 16 where the node has one). Returns True if anything changed."""
    mp, changed = standard_megapixels(cfg), False
    for node in size_nodes(wf):
        wv, named = node["widgets_values"], node.get("widgets_values_named")
        pairs = [(1, "resize_type.megapixels", mp)] if node["type"] == "ResizeImageMaskNode" else [(1, "megapixels", mp), (2, "resolution_steps", max(wv[2], 16))]
        for idx, key, val in pairs:
            if wv[idx] != val:
                wv[idx] = val
                changed = True
            if isinstance(named, dict) and key in named and named[key] != val:
                named[key] = val
                changed = True
    return changed


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


_FACE_LOCK = {}


def engine_prompt(cfg, item, pos):
    """The positive prompt an engine should get. FireRed puts an identity-lock paragraph (engines.firered.primeFace, a template file) in front of the Prime, because it tends to invent a face when the
    head in the photo is turned; it can pull the Environment up beside the fidelity paragraph and tell the model to replace the studio backdrop (envFirst), and adds a magic-effects instruction (fx)
    on the scenes listed in fxScenes."""
    fr = cfg.get("engines", {}).get("firered", {})
    if item.get("engine") == "firered" and fr.get("primeFace") and item.get("stage") == "alpha" and "_Alpha_1_Prime" in item.get("stem", ""):
        path = ROOT / fr["primeFace"]
        if path not in _FACE_LOCK:
            _FACE_LOCK[path] = path.read_text(encoding="utf-8").strip()
        return _FACE_LOCK[path] + "\n\n" + pos
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


PHOTO_STEMS = ("_Alpha_1_Prime", "_Alpha_1b_BareBase", "_Alpha_1b_NeutralBase")  # the first shots: the Prime and its two experiment bases


def takes_photo(item):
    """True for a first shot, the only workflows that load the hero's source photo (Alpha 1 Prime and the 1b_Experiments bases)."""
    return item["stage"] == "alpha" and item["stem"].endswith(PHOTO_STEMS)


def flow_suffix(flow):
    """'frame' -> 'Frame', 'tight-crop' -> 'TightCrop': the word a flow's workflows carry in their name (Haniya_Qwen_Alpha_1_Prime_Frame)."""
    return "".join(w.capitalize() for w in re.split(r"[-_ ]+", flow) if w)


def flow_photo(cfg, flow, hero):
    """The image a flow feeds its Prime for a hero (workspaces.json flows.<flow>.photos), or None."""
    return cfg.get("flows", {}).get(flow, {}).get("photos", {}).get(hero)


def prompt_index(cfg, engine="qwen"):
    out = []
    for p in sorted(PROMPTS.glob("**/*.txt")):
        rel = p.relative_to(PROMPTS)
        if "_archive" in rel.parts or len(rel.parts) < 4 or rel.parts[0] in cfg.get("skipGroups", []):
            continue
        group, division, hero, dirs, _file = art_layout.split_under(rel.parts)
        stagedir, family = art_layout.parse_dirs(dirs)  # prompts sit in the pipeline phase folders, which are also the output folders
        if (stagedir == "video") != (engine == "minimax"):  # video prompts feed only the MiniMax engine
            continue
        stem = p.stem
        if not stem.startswith(hero + "_"):
            continue
        name = f"{hero}_{ENGINES[engine]}_{stem[len(hero) + 1:]}"
        out.append({"path": p, "group": group, "hero": hero, "stage": stagedir, "family": family, "stem": stem, "name": name,
                    "prefix": "/".join([group] + ([division] if division else []) + [hero] + dirs + [name])})
    # a flow is a second way to run the Prime: the same prompt, another incoming image (workspaces.json flows). Its workflow sits beside the normal one and carries the flow's name
    for flow in cfg.get("flows", {}):
        suffix = flow_suffix(flow)
        for it in [i for i in out if takes_photo(i) and flow_photo(cfg, flow, i["hero"])]:
            out.append({**it, "stem": f"{it['stem']}_{suffix}", "name": f"{it['name']}_{suffix}", "prefix": f"{it['prefix']}_{suffix}", "flow": flow})
    return out


def flow_index(cfg):
    """{workflow name (without .json): flow} for every flow workflow."""
    return {i["name"]: i["flow"] for engine in ("qwen", "firered") for i in prompt_index(cfg, engine) if i.get("flow")}


# ---------- input images ----------

def infer_input(hero):
    """The A-pose image most of a hero's non-pose workflows already read."""
    pat = re.compile(rf"^{re.escape(hero)}_Qwen_X_Pose_\d+_\.png$")
    seen = collections.Counter()
    for p in hero_files(hero):
        if stage_of(p.name) in ("poses", "alpha"):
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


def input_role(cfg, hero, stage, family):
    """The role of a workflow's default incoming image (photo, apose or bare, from cfg inputRoles); None when the hero has no role inputs."""
    conf, roles = cfg.get("inputs", {}).get(hero), cfg.get("inputRoles", {})
    if not isinstance(conf, dict) or not roles:
        return None
    if family and f"{stage}/{family[0]}" in roles:
        return roles[f"{stage}/{family[0]}"]  # e.g. alpha/bare
    key = stage + "/"
    return roles.get(key) if not family and key in roles else roles.get(stage, roles.get("default"))


def default_input(cfg, hero, stage, family):
    """The image a workflow loads by default, by role (cfg inputRoles): the original photo for the root of poses/, the barefoot A-pose for
    bare/head/motion, and the bare-skin A-pose for everything else. None when the hero has no role inputs configured (legacy behaviour)."""
    role = input_role(cfg, hero, stage, family)
    if role is None:
        return None
    if role == "photo":
        return cfg.get("photos", {}).get(hero)
    conf = cfg["inputs"][hero]
    return conf.get(role) or conf.get("apose")


def denoise_for(cfg, prompt_text, role):
    """The denoise a new workflow starts at: the card's hint (the 'Denoise ~0.5-0.7.' line in the prompt header) at the end cfg denoise.pick
    names (high by default). A full-generation hint (~1.0) stays 1.0 on the original photo but drops to denoise.golden when the incoming
    image is a golden A-pose or bare image, since a full redraw there throws the golden image away. None when there is no rule or hint."""
    rule = cfg.get("denoise")
    m = re.search(r"Denoise ~?(\d(?:\.\d+)?)(?:-(\d(?:\.\d+)?))?", prompt_text.split("\nprompt:", 1)[0]) if rule else None
    if not m:
        return None
    lo = float(m.group(1))
    hi = float(m.group(2) or lo)
    if lo >= 1.0:
        return float(rule.get("golden", 0.7)) if role in ("prime", "apose", "bare", "scene", "polish") else 1.0
    return {"low": lo, "mid": round((lo + hi) / 2, 2)}.get(rule.get("pick", "high"), hi)


def get_denoise(wf):
    n = prompt_node(wf)
    named = n.get("widgets_values_named") if n else None
    return named.get("denoise") if isinstance(named, dict) else None


def set_denoise(wf, value):
    """Set the denoise widget the template exposes on the outer subgraph node; return True if it changed."""
    n = prompt_node(wf)
    named = n.get("widgets_values_named") if n else None
    if not isinstance(named, dict) or "denoise" not in named:
        return False
    idx = list(named).index("denoise")
    if named["denoise"] == value and n["widgets_values"][idx] == value:
        return False
    named["denoise"] = n["widgets_values"][idx] = value
    return True


def input_index(cfg):
    """{workflow name: (hero, stage, family)} for every Qwen and FireRed workflow the prompts define."""
    out = {}
    for engine in ("qwen", "firered"):
        for it in prompt_index(cfg, engine):
            out[it["name"]] = (it["hero"], it["stage"], it["family"])
    return out


# ---------- selection ----------

def pick_targets(cfg, args, default):
    """Workspaces to act on: -w names, else the templates workspaces (--templates), else the home workspace(s) of the selected heroes.

    A set with no home workspace stops the command: there is no fallback workspace, so a missing home can never turn into a silent deploy somewhere else.
    With -w, the workspace must be home for the selected sets or accept them (deploy refuses it otherwise)."""
    ws = cfg["workspaces"]
    if args.workspace:
        bad = [n for n in args.workspace if n not in ws]
        if bad:
            sys.exit(f"Unknown workspace(s): {bad}. Known: {list(ws)}")
        return list(args.workspace)
    if default == "all":
        return list(ws)
    if getattr(args, "templates", False):
        return template_workspaces(cfg)
    stage = route_stage(args)
    missing = groups_without_home(cfg, args.hero, args.group, stage)
    if missing:
        sys.exit(f"No workspace is home for: {', '.join(missing)}. Add a rule under homes in workflows/workspaces.json (and create the workspace) or narrow the filter with --hero/--group.")
    names = home_names(cfg, args.hero, args.group, stage)
    if not names:
        sys.exit("No home workspace is configured for the selected heroes (homes in workflows/workspaces.json).")
    unknown = [n for n in names if n not in ws]
    for n in unknown:
        print(f"note: '{n}' is a home workspace but is not listed under workspaces in workflows/workspaces.json")
    return [n for n in names if n in ws]


def name_matches(pattern, text):
    """--match is a case-insensitive substring; with a ^ or $ in it, it is a regex (Hero_FireRed_X_Pose$ picks only the base A-pose)."""
    text = text[:-5] if text.endswith(".json") else text
    if "^" in pattern or "$" in pattern:
        return re.search(pattern, text, re.I) is not None
    return pattern.lower() in text.lower()


def selected(cfg, ws, args, repo, home_only=False):
    """Repo files a workspace should hold, after the filters. With home_only, only the sets the workspace is home for (what status compares); otherwise also the sets it accepts."""
    out = {}
    for name, (group, hero, p) in repo.items():
        if not (is_home(cfg, ws, group, hero, stage_of(name)) if home_only else holds(cfg, ws, group, hero, stage_of(name))):
            continue
        if args.hero and hero.lower() != args.hero.lower():
            continue
        if args.group and group != args.group:
            continue
        if not stage_ok(args, name):
            continue
        if args.match and not name_matches(args.match, name):
            continue
        out[name] = (group, hero, p)
    return out


def classify(repo_p, inst_p):
    try:
        rv = get_values(read_wf(repo_p))
        iv = get_values(read_wf(inst_p))
    except (ValueError, AttributeError):  # an emptied file reads as JSON null
        return "unreadable"
    if rv is None or iv is None:
        return "unreadable"
    return "aligned" if rv == iv else "stale"


# ---------- commands ----------

def cmd_list(args):
    cfg = load_cfg()
    repo = repo_files(cfg)
    print(f"installs root: {cfg['installsRoot']}")
    print(f"stage templates workspace(s): {', '.join(template_workspaces(cfg)) or '-'}")
    print("workspaces:")
    for ws, info in cfg["workspaces"].items():
        found = "found" if install_exists(cfg, ws, args.root) else "MISSING"
        flags = ",".join(k for k in ("templates", "legacy") if info.get(k))
        home = sum(1 for n, (g, h, _p) in repo.items() if is_home(cfg, ws, g, h, stage_of(n)))
        acc = info.get("accepts", [])
        takes = "any set" if "*" in acc else ", ".join(acc) if acc else "-"
        print(f"  {ws:22} {info['status']:9} install={found:7} home for {home:4} workflows  accepts: {takes:40} {flags:16} {info['role']}")
    print("sets (repo):")
    for g in sorted({g for g, _, _ in repo.values()}):
        for h in sorted({h for gg, h, _ in repo.values() if gg == g}):
            stages = collections.Counter(stage_of(n) for n, (gg, hh, _) in repo.items() if hh == h)
            studio, scene = home_workspaces(cfg, g, h, "poses"), home_workspaces(cfg, g, h, "scene")
            home = (",".join(studio) or "-") if studio == scene else f"studio {','.join(studio) or '-'} / scene {','.join(scene) or '-'}"
            print(f"  {g}/{h:12} {sum(stages.values()):3}  home: {home}   " + ", ".join(f"{s} {c}" for s, c in sorted(stages.items())))


def curated_files(folder=None):
    """{name: (group, hero, path)} for hand-curated workflows in workflows/_curated/<set>/<Hero>/ (or test workflows in _test). make and deploy never touch them."""
    out = {}
    folder = folder or CURATED
    if folder.is_dir():
        for g in sorted(folder.iterdir()):
            for h in sorted(g.iterdir()) if g.is_dir() else []:
                for p in sorted(h.glob("*.json")) if h.is_dir() else []:
                    out[p.name] = (g.name, h.name, p)
    return out


def test_files():
    return curated_files(TEST)


def shot_files():
    """{(Hero, 'sub/folders/name.json'): (group, path)} for the shots kept in workflows/_shots/<set>/<Hero>/."""
    out = {}
    if SHOTS.is_dir():
        for g in sorted(SHOTS.iterdir()):
            for h in sorted(g.iterdir()) if g.is_dir() else []:
                for p in sorted(h.rglob("*.json")) if h.is_dir() else []:
                    out[(h.name, p.relative_to(h).as_posix())] = (g.name, p)
    return out


def workspace_shots(cfg, ws, root=None):
    """{(Hero, 'sub/folders/name.json'): path} for what a workspace holds under zz_Shots/ (a shared workspace may add a hero folder first)."""
    out, d = {}, install_dir(cfg, ws, root) / SHOTS_DIR
    if d.is_dir():
        heroes = hero_groups()
        for p in sorted(d.rglob("*.json")):
            parts = p.relative_to(d).parts
            if any(x.startswith(".") for x in parts):
                continue
            hero = hero_of(p.name) or (parts[0] if parts[0] in heroes else None)
            if not hero:
                continue
            sub = parts[1:] if parts[0] == hero and len(parts) > 1 else parts
            out[(hero, "/".join(sub))] = p
    return out


def shot_home(ws, hero, rel):
    return special_dir(ws, SHOTS_DIR, hero) / rel


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
    tst = test_files()
    groups = hero_groups()
    for ws in pick_targets(cfg, args, "all"):
        if not install_exists(cfg, ws, args.root):
            print(f"{ws}: workspace not found under {args.root or cfg['installsRoot']}")
            continue
        info = cfg["workspaces"][ws]
        inst = install_files(cfg, ws, args.root)
        rows = collections.defaultdict(list)
        for name, (g, h, p) in selected(cfg, ws, args, repo, home_only=True).items():
            if name not in inst:
                rows["staged" if is_staged(name) else "missing"].append(name)
            else:
                rows[classify(p, inst[name])].append(name)
        for name in inst:
            h = hero_of(name)
            if not h:
                continue
            if not holds(cfg, ws, groups[h], h, stage_of(name)):
                if not (args.hero and h.lower() != args.hero.lower()) and not (args.group and groups[h] != args.group):
                    rows["unrouted"].append(name)
                continue
            if name in repo:
                if not is_home(cfg, ws, groups[h], h, stage_of(name)) and not (args.hero and h.lower() != args.hero.lower()) and not (args.group and groups[h] != args.group):
                    rows["published"].append(name)
                continue
            if args.hero and h.lower() != args.hero.lower():
                continue
            if name in cur:
                rows["curated" if same_workflow(cur[name][2], inst[name]) else "curated-changed"].append(name)
                continue
            if name in tst:
                rows["test" if same_workflow(tst[name][2], inst[name]) else "test-changed"].append(name)
                continue
            rows["legacy" if info.get("legacy") else "install-only"].append(name)
        for name in selected(cfg, ws, args, cur, home_only=True):
            if name not in inst:
                rows["curated-missing"].append(name)
        have = workspace_shots(cfg, ws, args.root)
        store = shot_files()
        for key, p in have.items():
            if args.hero and key[0].lower() != args.hero.lower():
                continue
            rows["shots-new" if key not in store else "shots" if same_workflow(store[key][1], p) else "shots-changed"].append(key[1])
        for key, (g, p) in store.items():
            if key not in have and is_home(cfg, ws, g, key[0], None) and not (args.hero and key[0].lower() != args.hero.lower()):
                rows["shots-missing"].append(key[1])
        counts = ", ".join(f"{len(rows[k])} {k}" for k in ("aligned", "stale", "missing", "install-only", "published", "unrouted", "curated", "curated-changed", "curated-missing", "test", "test-changed", "shots", "shots-new", "shots-changed", "shots-missing", "staged", "legacy", "unreadable") if rows[k] or k in ("aligned", "stale", "missing", "install-only"))
        print(f"{ws} [{info['status']}]: {counts}")
        finals_status(cfg, ws, args, brief=True)
        hints = {"stale": "deploy", "missing": "deploy", "install-only": "pull: keeps it as a curated workflow", "curated-changed": "pull: captures your edits",
                 "published": "a temporary copy of a set whose home is elsewhere; cleanup -w removes it when you are done",
                 "unrouted": "this workspace is neither home for it nor accepts it; cleanup -w moves plain copies to backup once their home workspace holds them, hand-made zz_ ones stay",
                 "curated-missing": "deploy --include curated", "test-changed": "pull: captures your edits", "legacy": "old hand-made, no generated prompt",
                 "shots-new": "pull --only shots", "shots-changed": "pull --only shots", "shots-missing": "deploy --include shots"}
        for k, names in rows.items():
            if k in hints and names and (args.verbose or len(names) <= 5):
                print(f"    {k} ({hints[k]}): " + ", ".join(names))
        flagged = [c for c in input_choices(cfg, [ws], args.root, args.hero) if c["state"] != "same"]
        if flagged:
            print("    inputs-changed (inputs pull: keeps the default images you chose here in workspaces.json): "
                  + ", ".join(f"{c['hero']} {c['role']}" + (" (mixed)" if c["state"] == "mixed" else "") for c in flagged))
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
    targets = pick_targets(cfg, args, "home")
    if args.workspace and not args.templates:
        for ws in targets:
            refused = refused_groups(cfg, ws, args.hero, args.group, route_stage(args))
            if refused:
                sys.exit(f"{ws} is neither home for nor accepts: {', '.join(refused)}. Narrow the filter with --group/--hero, or list the set under \"accepts\" "
                         f"for that workspace in workflows/workspaces.json if it really should go there.")
    for ws in targets:
        if not ready_or_skip(cfg, ws, args.root):
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
            if name not in inst and is_staged(name) and not getattr(args, "staged", False):
                tally["staged held back"] += 1
                continue
            if name in inst and is_hand_made(cfg, ws, inst[name], args.root):
                print(f"  KEEP     {ws}/{name} is hand-made (zz_ folder or zz_Curated_/test_ name); deploy never changes it")
                tally["hand-made kept"] += 1
                continue
            if name in inst and getattr(args, "new_only", False):
                tally["kept"] += 1
                continue
            if name not in inst:
                print(f"  new      {ws}/{name}")
                if not args.dry_run:
                    wf = read_wf(p)
                    write_wf(dest / workspace_subdir(ws, wf) / name, wf)
                tally["new"] += 1
                continue
            state = classify(p, inst[name])
            reseed = not final_record(cfg, name)  # a final's seed stays fixed; every other generated workflow draws a new one per run
            if state == "aligned" and not replace:
                probe = read_wf(inst[name])
                stale_size = align_size(probe, cfg)
                stale_seed = reseed and randomize_seed(probe)
                if not (stale_size or stale_seed):
                    tally["aligned"] += 1
                    continue
                print(f"  {'size' if stale_size else 'seed'}     {ws}/{name}  ({'total pixels set to the standard size' if stale_size else 'seed set to randomize'}; prompt, seed value and input untouched)")
                if not args.dry_run:
                    backup(stamp, ws, name, inst[name])
                    swf = read_wf(inst[name])
                    align_size(swf, cfg)
                    if reseed:
                        randomize_seed(swf)
                    write_wf(inst[name], swf)
                tally["updated"] += 1
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
                    align_size(wf, cfg)
                    if reseed:
                        randomize_seed(wf)
                    write_wf(inst[name], wf)
            tally["updated"] += 1
        if getattr(args, "tests", False):
            for name, (g, h, p) in selected(cfg, ws, args, test_files()).items():
                if name not in inst:
                    print(f"  test     {ws}/{name} (new)")
                    if not args.dry_run:
                        write_wf(dest / special_dir(ws, TEST_DIR, h) / name, read_wf(p))
                    tally["test"] += 1
                elif same_workflow(p, inst[name]):
                    tally["aligned"] += 1
                else:
                    print(f"  SKIP     {ws}/{name} differs from the test copy (your edits?): pull it, or use --overwrite")
                    tally["skipped"] += 1
        if getattr(args, "curated", False):
            for name, (g, h, p) in selected(cfg, ws, args, curated_files()).items():
                if name not in inst:
                    print(f"  curated  {ws}/{name} (new)")
                    if not args.dry_run:
                        write_wf(dest / special_dir(ws, CURATED_DIR, h) / name, read_wf(p))
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
        if getattr(args, "shots", False):
            for (h, rel), (g, p) in shot_files().items():
                if not holds(cfg, ws, g, h, None) or (args.hero and h.lower() != args.hero.lower()) or (args.group and g != args.group) \
                        or (args.match and not name_matches(args.match, p.name)):
                    continue
                have = workspace_shots(cfg, ws, args.root).get((h, rel))
                if not have:
                    print(f"  shot     {ws}/{shot_home(ws, h, rel).as_posix()} (new)")
                    if not args.dry_run:
                        write_wf(dest / shot_home(ws, h, rel), read_wf(p))
                    tally["shots"] += 1
                elif same_workflow(p, have):
                    tally["aligned"] += 1
                elif args.overwrite:
                    print(f"  shot     {ws}/{SHOTS_DIR}/{rel} (replace)")
                    if not args.dry_run:
                        backup(stamp, ws, p.name, have)
                        write_wf(have, read_wf(p))
                    tally["shots"] += 1
                else:
                    print(f"  SKIP     {ws}/{SHOTS_DIR}/{rel} differs from the repo copy (your edits?): pull it, or use --overwrite")
                    tally["skipped"] += 1
        print(f"{ws}: " + ", ".join(f"{v} {k}" for k, v in tally.items()) + (" (dry run)" if args.dry_run else ""))
    print("Restart the ComfyUI workspace (or reload the workflow list) to see changes.")


def same_copy(a_path, b_path, master_path):
    """Loose duplicate test: same prompt values as the repo master and the same input image; seeds and other run-to-run values are ignored."""
    try:
        a, b, m = read_wf(a_path), read_wf(b_path), read_wf(master_path)
    except ValueError:
        return False
    return get_values(a) == get_values(b) == get_values(m) and input_image(a) == input_image(b)


def cleanup_orphans(cfg, args):
    """Move workflows named like generated ones that no prompt in the repo defines any more (a renamed or removed card) to backup.
    Needs --match (end it with $ for a regex) so only what you name is touched; zz_ folders, curated and test files are never moved."""
    if not args.match:
        sys.exit("--orphans needs --match, e.g. --match \"_X_Pose(_Barefoot|_Heels)?$\"")
    repo, cur, tst = repo_files(cfg), curated_files(), test_files()
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    apply = args.apply and not args.dry_run
    moved = 0
    for ws in args.workspace or list(cfg["workspaces"]):
        if not workspace_ready(cfg, ws, args.root)[0]:
            if args.workspace:
                ready_or_skip(cfg, ws, args.root)
            continue
        d = install_dir(cfg, ws, args.root)
        gone = []
        for name, p in sorted(install_files(cfg, ws, args.root).items()):
            h = hero_of(name)
            if not h or name in repo or name in cur or name in tst or is_template(cfg, name) or excluded(cfg, name):
                continue
            rel = p.relative_to(d)
            if is_hand_made(cfg, ws, p, args.root) or (args.hero and h.lower() != args.hero.lower()) or not name_matches(args.match, name):
                continue
            print(f"  {'move ' if apply else 'would move'}  {ws}: {rel.as_posix()}")
            moved += 1
            gone.append(p)
            if apply:
                b = BACKUPS / stamp / (ws + " (orphans)") / rel
                b.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(p), str(b))
        if gone:
            for folder in (prune_empty_dirs(d, apply) if apply else empty_dirs(d, gone)):
                print(f"  {'removed' if apply else 'would remove'} empty folder  {ws}: {folder.relative_to(d).as_posix()}")
    print(f"orphans: {moved} workflow(s) " + ("moved to workflows/.sync/backup" if apply else "would be moved (preview; use --apply)"))


def cmd_cleanup(args):
    """Remove the generated workflows a workspace is not routed to hold, once a workspace that is routed to hold them has an identical copy.

    The workspace is named with -w; there is no default. A file is removed only if all of these hold: it is a generated workflow in the repo, no route sends it to
    this workspace, it is not hand-made (a zz_ folder or a zz_Curated_/test_ name), and every home workspace that serves it is active and holds an identical copy.
    Anything else stays and is listed with its reason. Strict by default (identical graphs); --loose ignores seeds and other values that change every run.
    Temporary copies you published on request (a set this workspace accepts but is not home for) are removed the same way once you are done.
    Empty folders are removed afterwards (never the top-level zz_ ones). Default is a preview; --apply moves the files to workflows/.sync/backup/ (nothing is deleted)."""
    cfg = load_cfg()
    if args.orphans:
        return cleanup_orphans(cfg, args)
    if not args.workspace:
        sys.exit("cleanup needs -w WORKSPACE: it removes what that workspace is not home for (see `list`). Use --orphans --match ... for renamed or removed cards.")
    repo = repo_files(cfg)
    groups = hero_groups()
    src = args.workspace[0]
    if src not in cfg["workspaces"]:
        sys.exit(f"Unknown workspace '{src}'. Known: {list(cfg['workspaces'])}")
    ok, why = workspace_ready(cfg, src, args.root)
    if not ok:
        sys.exit(f"{src}: {why}.")
    apply = args.apply and not args.dry_run
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    cache, tally, kept = {}, collections.Counter(), collections.defaultdict(list)

    def files_of(ws):
        if ws not in cache:
            cache[ws] = install_files(cfg, ws, args.root) if workspace_ready(cfg, ws, args.root)[0] else None
        return cache[ws]

    gone = []
    for name, p in sorted(install_files(cfg, src, args.root).items()):
        h = hero_of(name)
        if not h or is_template(cfg, name) or excluded(cfg, name):
            continue
        g = groups[h]
        if (args.hero and h.lower() != args.hero.lower()) or (args.group and g != args.group) or not stage_ok(args, name) \
                or (args.match and not name_matches(args.match, name)):
            continue
        if is_home(cfg, src, g, h, stage_of(name)):
            tally["home here"] += 1
            continue
        why = None
        dests = [w for w in home_workspaces(cfg, g, h, stage_of(name)) if w != src]
        if is_hand_made(cfg, src, p, args.root):
            why = "hand-made (zz_ folder or zz_Curated_/test_ name): never removed; pull it into the repo or delete it yourself"
        elif name not in repo:
            why = "not a generated workflow in the repo (yours, curated or renamed)"
        elif not dests:
            why = "no home workspace is configured for it"
        else:
            for w in dests:
                held = files_of(w)
                if held is None:
                    why = f"{w} is not an active workspace with an install yet"
                elif name not in held:
                    why = f"not delivered to {w} yet"
                elif not (same_copy(p, held[name], repo[name][2]) if args.loose else same_workflow(p, held[name])):
                    why = f"differs from the copy in {w} (edited?)"
                if why:
                    break
        if why:
            kept[why].append(name)
            continue
        print(f"  {'remove ' if apply else 'would remove'}  {name}  (held by {', '.join(dests)})")
        tally["duplicates"] += 1
        gone.append(p)
        if apply:
            b = BACKUPS / stamp / (src + " (cleaned)") / name
            b.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(b))
    for why, names in kept.items():
        print(f"  KEEP {len(names):4}  {why}")
        for n in names[: args.show]:
            print(f"           {n}")
    d = install_dir(cfg, src, args.root)
    for folder in (prune_empty_dirs(d, apply) if apply else empty_dirs(d, gone)):
        print(f"  {'removed' if apply else 'would remove'} empty folder  {folder.relative_to(d).as_posix()}")
    print(f"{src}: {tally['duplicates']} workflow(s) this workspace is not home for " + ("moved to backup" if apply else "would be removed (preview; use --apply)")
          + f", {sum(map(len, kept.values()))} kept, {tally['home here']} home here and left alone")


def pull_shots(cfg, ws, args, stamp, seen=None):
    """Keep the workflows under zz_Shots/ in a workspace, and the numbered saves (Hero_Qwen_..._00004_) loose in its list, as repo shots (workflows/_shots/<set>/<Hero>/, same subfolders). Edits are captured again."""
    groups = hero_groups()
    done = skipped = 0
    for (h, rel), p in workspace_shots(cfg, ws, args.root).items():
        if seen is not None:
            seen.add((h, rel))
        if (args.hero and h.lower() != args.hero.lower()) or (args.group and groups[h] != args.group) \
                or (args.match and not name_matches(args.match, p.name)):
            continue
        dst = SHOTS / groups[h] / h / rel
        first = args.__dict__.setdefault("_shot_sources", {}).setdefault(dst, (ws, p))
        if first[1] != p and not same_workflow(first[1], p):  # two workspaces save a different shot under one name (another seed, say): the first one pulled stays, rename one of them to keep both
            print(f"  CONFLICT {ws}/{p.relative_to(install_dir(cfg, ws, args.root)).as_posix()} differs from the copy in {first[0]}, already pulled to {dst.relative_to(ROOT).as_posix()}; rename one of them to keep both")
            skipped += 1
            continue
        if dst.exists() and same_workflow(dst, p):
            skipped += 1
            continue
        print(f"  shot   {ws}/{p.relative_to(install_dir(cfg, ws, args.root)).as_posix()} -> {dst.relative_to(ROOT).as_posix()}" + (" (update)" if dst.exists() else ""))
        if not args.dry_run:
            write_wf(dst, read_wf(p))
        done += 1
    print(f"{ws} shots: pulled {done}, left {skipped} unchanged" + (" (dry run)" if args.dry_run else ""))


def prune_shots(cfg, args, stamp, seen, scanned):
    """Move repo shots that none of the pulled workspaces holds any more to the backup folder (git history keeps them too)."""
    for (h, rel), (g, p) in shot_files().items():
        if h not in scanned or (h, rel) in seen or (args.hero and h.lower() != args.hero.lower()) or (args.match and not name_matches(args.match, p.name)):
            continue
        print(f"  prune  {p.relative_to(ROOT).as_posix()} (no longer in the pulled workspaces)" + (" (dry run)" if args.dry_run else ""))
        if not args.dry_run:
            b = BACKUPS / stamp / "shots (pruned)" / h / rel
            b.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(b))


def cmd_pull(args):
    cfg = load_cfg()
    repo = repo_files(cfg)
    cur = curated_files()
    tst = test_files()
    groups = hero_groups()
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    seen, scanned = set(), set()
    if args.prune and not (args.shots and args.hero and args.workspace):
        sys.exit("--prune needs --shots, --hero and an explicit workspace (-w), so a shot another workspace holds is never removed by mistake.")
    for ws in pick_targets(cfg, args, "home"):
        if not ready_or_skip(cfg, ws, args.root):
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
            if not args.only_finals:
                pull_shots(cfg, ws, args, stamp, seen)
            scanned |= {h for h, g in groups.items() if holds(cfg, ws, g, h, None)}
            print(f"{ws}: pulling is turned off for this workspace (old hand-made workflows); only its zz_Shots were captured; use --include-legacy for the rest")
            finals_pull(cfg, ws, args)
            continue
        if not args.only_finals:
            pull_shots(cfg, ws, args, stamp, seen)
        finals_pull(cfg, ws, args)  # candidates and finals (and numbered saves loose in the list), arranged like the main tree
        scanned |= {h for h, g in groups.items() if holds(cfg, ws, g, h, None)}
        if args.shots or args.only_finals:
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
            if args.match and not name_matches(args.match, name):
                continue
            if name in cur or name in tst:  # a hand-curated or test workflow: the workspace is where it is edited, so keep the repo copy in step
                store, make_prefix = (cur, curated_prefix) if name in cur else (tst, test_prefix)
                wf = read_wf(p)
                prefix_fix = set_prefix(wf, make_prefix(groups[h], h, name))  # writes to <group>/<Hero>/_curated/ or _test/
                if prefix_fix and not args.dry_run:
                    backup(stamp, ws, name, p)
                    write_wf(p, wf)  # the workspace copy gets the same prefix so the two stay identical
                if read_wf(store[name][2]) == wf:
                    skipped += 1
                    continue
                print(f"  update {'curated' if name in cur else 'test'}  {ws}/{name}")
                if not args.dry_run:
                    write_wf(store[name][2], wf)
                done += 1
                continue
            if name in repo and not args.force:
                skipped += 1
                continue
            if name in repo:
                dst = repo_path(cfg, groups[h], h, name)
            elif name.startswith(TEST_PREFIX):
                dst = TEST / groups[h] / h / name  # an experiment: kept apart from the curated workflows
            else:
                dst = CURATED / groups[h] / h / curated_name(name)  # not generated by us: keep it as a curated workflow
            print(f"  pull   {ws}/{name} -> {dst.parent.relative_to(ROOT).as_posix()}/{dst.name if dst.name != name else ''}")
            wf = read_wf(p)
            if dst.is_relative_to(CURATED) or dst.is_relative_to(TEST):
                prefix = (test_prefix if dst.is_relative_to(TEST) else curated_prefix)(groups[h], h, name)
                print(f"           output folder: {prefix.rsplit('/', 1)[0]}/")
                if set_prefix(wf, prefix) and not args.dry_run:
                    backup(stamp, ws, name, p)
                    write_wf(p, wf)
            if not args.dry_run:
                write_wf(dst, wf)
                if dst.name != name:  # the workspace copy takes the curated name too, so the two stay one workflow
                    backup(stamp, ws, name, p)
                    write_wf(p.with_name(dst.name), wf)
                    p.unlink()
            done += 1
        print(f"{ws}: pulled {done}, left {skipped} unchanged" + (" (dry run)" if args.dry_run else ""))
    if args.prune:
        prune_shots(cfg, args, stamp, seen, scanned)


def cmd_fork(args):
    """Copy a generated workflow to workflows/_curated under a new name, so it can be hand-edited in ComfyUI without being regenerated."""
    cfg = load_cfg()
    repo, cur = repo_files(cfg), curated_files()
    src = args.name if args.name.endswith(".json") else args.name + ".json"
    if src not in repo:
        sys.exit(f"No generated workflow named {src} (try: status -v, or the name without .json).")
    g, h, p = repo[src]
    new = curated_name(f"{src[:-5]}_{args.tag}.json")
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
    homes = [w for w in home_workspaces(cfg, g, h, "poses") if workspace_ready(cfg, w, args.root)[0]]
    if args.no_deploy:
        return
    if not homes:
        print(f"  no active home workspace for {h}: the curated copy stays in the repo (deploy --include curated --hero {h} puts it in a workspace later)")
        return
    for ws in homes:
        write_wf(install_dir(cfg, ws, args.root) / special_dir(ws, CURATED_DIR, h) / new, wf)
        print(f"  deployed to {ws}: open {new} in ComfyUI, edit it, save it, then run pull to keep your changes")


def is_text_item(cfg, item):
    """A prompt whose family is listed under textGroups for its group is text-to-image (no incoming picture): the brand set."""
    parts = item["path"].relative_to(PROMPTS).parts
    wanted = cfg.get("textGroups", {}).get(item["group"], [])
    return item.get("engine") == "qwen" and (parts[2] in wanted or (len(parts) > 4 and parts[3] in wanted))


def cmd_make(args):
    cfg = load_cfg()
    engines = {"firered": ["firered"], "minimax": ["minimax"], "both": ["qwen", "firered"]}.get(args.engine, ["qwen"])
    items = []
    for engine in engines:
        its = prompt_index(cfg, engine)
        for i in its:
            i["engine"] = engine
        if engine == "firered" and not (args.stage or args.cls):
            # the class list limits what --create builds; a FireRed workflow that already exists (an Alpha test card, a Final) is always refreshed
            its = [i for i in its if class_of(i["stage"]) in cfg["engines"]["firered"].get("classes", ["scene"])
                   or i.get("flow") or i["stem"].endswith(PHOTO_STEMS[1:]) or (engine_roots(cfg)["firered"] / i["group"] / i["hero"] / f"{i['name']}.json").exists()]
        its = [i for i in its if engine in cfg.get("stageEngines", {}).get(i["stage"], [engine])]  # e.g. final is FireRed only
        items += its
    if args.group:
        items = [i for i in items if i["group"] == args.group]
    if args.hero:
        items = [i for i in items if i["hero"].lower() == args.hero.lower()]
    if args.stage or args.cls:
        items = [i for i in items if stage_ok(args, i["stage"], True)]
    if args.match:
        items = [i for i in items if name_matches(args.match, i["stem"])]
    tally = {"created": 0, "updated": 0, "unchanged": 0, "missing": 0}
    for it in items:
        target = engine_roots(cfg)[it["engine"]] / it["group"] / it["hero"] / f"{it['name']}.json"
        pos, neg = split_prompt(it["path"].read_text(encoding="utf-8"))
        pos = engine_prompt(cfg, it, pos)
        rec = final_record(cfg, it["name"] + ".json")
        if target.exists():
            wf = read_wf(target)
            resized = is_text_item(cfg, it) and set_size(wf, it["path"].read_text(encoding="utf-8"))
            replayed = bool(rec) and apply_final_settings(wf, rec)
            reseeded = not rec and randomize_seed(wf)
            resized = (not is_text_item(cfg, it) and align_size(wf, cfg)) or resized
            if patch_wf(wf, pos, neg, it["prefix"]) or resized or replayed or reseeded:
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
        is_apose = takes_photo(it)  # a first shot: the only workflows that take the hero's source photo
        is_text = is_text_item(cfg, it)
        master = ROOT / (video_template(cfg, it["path"].read_text(encoding="utf-8")) if it["engine"] == "minimax"
                         else cfg["engines"][it["engine"]]["template"] if it["engine"] == "firered"
                         else cfg["templates"].get("byStage", {}).get(it["stage"]) or cfg["templates"]["text" if is_text else "poses" if is_apose else "default"])
        if not master.exists():
            sys.exit(f"Master template not found: {master}")
        wf = read_wf(master)
        patch_wf(wf, pos, neg, it["prefix"])
        if is_text:
            set_size(wf, it["path"].read_text(encoding="utf-8"))
        if it["engine"] == "firered":
            set_turbo(wf, cfg["engines"]["firered"].get("turbo", True))
        if not is_text:
            dn = denoise_for(cfg, it["path"].read_text(encoding="utf-8"), input_role(cfg, it["hero"], it["stage"], it["family"]))
            if dn is not None:
                set_denoise(wf, dn)
        if not is_text:
            align_size(wf, cfg)
        if rec:
            apply_final_settings(wf, rec)  # a stage you finalised replays its seed, denoise and turbo
        else:
            randomize_seed(wf)
        video = set_video(wf, it["path"].read_text(encoding="utf-8"), cfg["engines"]["minimax"]) if it["engine"] == "minimax" else None
        wf["id"] = str(uuid.uuid4())
        ln = node_of(wf, "LoadImage")
        want = args.input or video or (flow_photo(cfg, it["flow"], it["hero"]) if it.get("flow") else None) or default_input(cfg, it["hero"], it["stage"], it["family"]) \
            or (cfg.get("photos", {}).get(it["hero"]) if is_apose else input_for(cfg, it["hero"], it["stage"]))
        if ln and want:
            ln["widgets_values"][0] = want
            if isinstance(ln.get("widgets_values_named"), dict) and "image" in ln["widgets_values_named"]:
                ln["widgets_values_named"]["image"] = want
        if not args.dry_run:
            write_wf(target, wf)
        tally["created"] += 1
        print(f"  created  {it['group']}/{it['hero']}/{target.name}  (input: {ln['widgets_values'][0] if ln else '?'})")
    print("make: " + ", ".join(f"{v} {k}" for k, v in tally.items()) + (" (dry run)" if args.dry_run else ""))
    if tally["missing"] and not args.create:
        print("      (use --create to build the missing workflows from the master template)")


def cmd_setup(args):
    """Bring one workspace to its intended state in one go: deploy every set it is home for (plus the curated workflows and shots the repo keeps for them), tidy the folders,
    remove what it is not home for (a clone's leftovers) and show the status. A preview unless --apply; every step is the normal command, so all the guards apply."""
    cfg = load_cfg()
    if not args.workspace or len(args.workspace) != 1:
        sys.exit("setup needs exactly one -w WORKSPACE.")
    ws = args.workspace[0]
    if ws not in cfg["workspaces"]:
        sys.exit(f"Unknown workspace '{ws}'. Known: {list(cfg['workspaces'])}")
    ok, why = workspace_ready(cfg, ws, args.root)
    if not ok:
        sys.exit(f"{ws}: {why}.")
    groups = hero_groups()
    homes = {h: g for h, g in groups.items() if is_home(cfg, ws, g, h)}
    whole = sorted(g for g in set(homes.values()) if all(h in homes for h, gg in groups.items() if gg == g))
    partial = sorted(h for h, g in homes.items() if g not in whole)
    root = ["--root", args.root] if args.root else []
    apply = ["--apply"] if args.apply else []
    print(f"setup {ws} ({'APPLY' if args.apply else 'preview; add --apply to do it'}): home for {len(whole)} whole set(s) {whole} and {len(partial)} hero(es) {partial}")
    steps = [["inputs", "pull", "-w", ws, *apply]]
    if cfg["workspaces"][ws].get("templates"):
        steps.append(["deploy", "--templates", "-w", ws, *apply])
    for g in whole:
        steps.append(["deploy", "--group", g, "-w", ws, "--include", "curated,shots", *apply])
    for h in partial:
        steps.append(["deploy", "--hero", h, "-w", ws, "--include", "curated,shots", *apply])
    steps += [["tidy", "-w", ws, *apply], ["finals", "sort", "-w", ws, *apply], ["finals", "deploy", "-w", ws, *apply], ["cleanup", "-w", ws, *apply], ["status", "-w", ws]]
    for step in steps:
        print("\n== " + " ".join(step))
        main([step[0], *root, *step[1:]])


def cmd_tidy(args):
    """Move generated workflows that sit loose in a workspace into <stage>/<family>/ folders, and curated and test ones into zz_Curated/ and zz_Test/, so the ComfyUI list shows folders, not hundreds of files."""
    cfg = load_cfg()
    repo, cur, tst = repo_files(cfg), curated_files(), test_files()
    for ws in pick_targets(cfg, args, "all"):
        if not ready_or_skip(cfg, ws, args.root):
            continue
        d = install_dir(cfg, ws, args.root)
        moved = 0
        for name, p in install_files(cfg, ws, args.root).items():
            top = p.relative_to(d).parts[0]
            if name in cur or name in tst:
                if args.hero and (cur.get(name) or tst[name])[1].lower() != args.hero.lower():
                    continue
                home_dir = CURATED_DIR if name in cur else TEST_DIR
                if top == home_dir:
                    continue  # already where hand-made workflows live, in whatever subfolder you keep it
                want = d / special_dir(ws, home_dir, hero_of(name)) / name
            elif name not in repo or (args.hero and repo[name][1].lower() != args.hero.lower()):
                continue
            elif is_hand_made(cfg, ws, p, args.root):
                continue  # a generated name inside a zz_ folder is yours; never move it out
            else:
                want = d / workspace_subdir(ws, read_wf(repo[name][2])) / name
            if p == want:
                continue
            if args.verbose:
                print(f"  {ws}: {p.relative_to(d).as_posix()} -> {want.relative_to(d).as_posix()}")
            if args.apply:
                want.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(p), str(want))
            moved += 1
        print(f"{ws}: {moved} workflow(s) {'moved' if args.apply else 'would move'}")
        # moving leaves empty folders behind (an old layout), which ComfyUI would still list; zz_ folders are never removed
        for folder in prune_empty_dirs(d, args.apply):
            print(f"  {'removed' if args.apply else 'would remove'} empty folder  {ws}: {folder.relative_to(d).as_posix()}")
    if not args.apply:
        print("Preview only: add --apply to move them. Reload the ComfyUI workflow list afterwards.")


def sync_inputs(cfg, args, workspaces=None):
    """Copy every image that a deployed workflow loads into the input folder of its workspace, when it is not there. Nothing is retargeted: no workflow and no workspaces.json entry changes,
    so a Prime you chose stays chosen. Covers what `inputs reset` copies only after it has retargeted (flow images such as the frame, the first-shot experiment photos)."""
    copied = missing = placeholders = 0
    for ws in workspaces if workspaces is not None else list(cfg["workspaces"]):
        if not workspace_ready(cfg, ws, args.root)[0]:
            continue
        d = input_dir(cfg, ws, args.root) if args.root else input_dir(cfg, ws)
        wanted = collections.defaultdict(int)
        repo = repo_files(cfg)
        for name, p in install_files(cfg, ws, args.root).items():
            if name not in repo or is_hand_made(cfg, ws, p, args.root):
                continue  # only generated workflows; curated, test and sample ones keep their own images
            if args.hero and not name.lower().startswith(args.hero.lower() + "_"):
                continue
            if getattr(args, "match", None) and not name_matches(args.match, name):
                continue
            try:
                ln = node_of(read_wf(p), "LoadImage")
            except (ValueError, OSError):
                continue
            if ln and ln["widgets_values"] and isinstance(ln["widgets_values"][0], str):
                wanted[ln["widgets_values"][0]] += 1
        for img, n in sorted(wanted.items()):
            if (d / img).exists():
                continue
            if img.endswith("_00000.png"):
                placeholders += 1  # "not chosen yet" (see inputs reset): no such file exists
                continue
            src = find_image(cfg, img)
            if not src:
                missing += 1
                print(f"  MISSING  {ws}: {img} ({n} workflow(s)) is not in {d}, any other input folder, the photo library or the output folders")
            else:
                copied += 1
                print(f"  {'would copy' if args.dry_run else 'copied   '} {ws}: {img} -> {d}")
                if not args.dry_run:
                    shutil.copy2(src, d / img)
    print(f"inputs sync: {copied} image(s) {'to copy' if args.dry_run else 'copied'}, {missing} missing, {placeholders} placeholder name(s) skipped (not chosen yet)" + (" (dry run)" if args.dry_run else ""))


def reset_inputs(cfg, args, workspaces=None, include_repo=True):
    """Point every generated workflow at its default incoming image (see default_input), in the repo and in the workspaces, and copy any image a
    workspace is missing into its input folder. Curated, test and shot workflows are left alone; a changed file is backed up first."""
    pending = [c for c in input_choices(cfg, workspaces, args.root, args.hero) if c["state"] != "same"]
    if pending and not getattr(args, "force", False):
        print("inputs reset STOPPED: the workspaces hold default images that workspaces.json does not (a reset would overwrite your choice):")
        for c in pending:
            print(f"    {c['hero']:10} {c['role'] + (' [' + c['flow'] + ']' if c['flow'] else ''):14} {c['state']:8} {c['counts']}   (configured: {c['configured'] or '-'})")
        print("Run  inputs pull  first to keep them (or --force to overwrite them; a changed workflow is backed up first).")
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    idx, repo = input_index(cfg), repo_files(cfg)
    flows = flow_index(cfg)
    needs = collections.defaultdict(set)
    changed = collections.Counter()

    def retarget(p, name, ws):
        info = idx.get(name[:-5] if name.endswith(".json") else name)
        if not info:
            return
        hero, stage, family = info
        if (args.hero and hero.lower() != args.hero.lower()) or (getattr(args, "stage", None) and stage != args.stage) \
                or (getattr(args, "match", None) and not name_matches(args.match, name)):
            return
        flow = flows.get(name[:-5] if name.endswith(".json") else name)
        want = flow_photo(cfg, flow, hero) if flow else default_input(cfg, hero, stage, family)
        wf = read_wf(p)
        ln = node_of(wf, "LoadImage") if isinstance(wf, dict) else None
        if not want or not ln:
            return
        if ws:
            needs[ws].add(want)
        if ln["widgets_values"][0] == want:
            return
        changed[ws or "repo"] += 1
        if args.dry_run:
            return
        if ws:
            backup(stamp, ws, p.name, p)
        ln["widgets_values"][0] = want
        if isinstance(ln.get("widgets_values_named"), dict) and "image" in ln["widgets_values_named"]:
            ln["widgets_values_named"]["image"] = want
        write_wf(p, wf)

    if include_repo:
        for name, (g, h, p) in repo.items():
            retarget(p, name, None)
    for ws in workspaces if workspaces is not None else list(cfg["workspaces"]):
        if not workspace_ready(cfg, ws, args.root)[0]:
            continue
        for name, p in install_files(cfg, ws, args.root).items():
            if name in repo and not is_hand_made(cfg, ws, p, args.root):
                retarget(p, name, ws)
    for ws, names in needs.items():
        d = input_dir(cfg, ws, args.root) if args.root else input_dir(cfg, ws)
        for img in sorted(names):
            if (d / img).exists():
                continue
            src = find_image(cfg, img)
            if not src:
                print(f"  MISSING  {img} is not in {d}, any other input folder or the output folders")
            elif args.dry_run:
                print(f"  would copy {img} -> {d}")
            else:
                shutil.copy2(src, d / img)
                print(f"  copied   {img} -> {d}")
    print("inputs reset: " + (", ".join(f"{v} in {k}" for k, v in changed.items()) or "nothing to change") + (" (dry run)" if args.dry_run else ""))


def image_size(path):
    """(width, height) of a PNG or JPEG read from its header, or None."""
    try:
        with open(path, "rb") as f:
            head = f.read(26)
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                return struct.unpack(">II", head[16:24])
            if head[:2] != b"\xff\xd8":
                return None
            f.seek(2)
            while True:
                b = f.read(1)
                while b and b != b"\xff":
                    b = f.read(1)
                m = f.read(1)
                while m == b"\xff":
                    m = f.read(1)
                if not m:
                    return None
                if m[0] in (0xD8, 0x01) or 0xD0 <= m[0] <= 0xD7:
                    continue
                n = struct.unpack(">H", f.read(2))[0]
                if m[0] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack(">HH", f.read(5)[1:5])
                    return w, h
                f.seek(n - 2, 1)
    except (OSError, struct.error):
        return None


def find_image(cfg, name):
    """First existing copy of an image: any input folder, the photo folders, the headshot folders, then anywhere under the output roots."""
    for d in input_dirs(cfg):
        if (d / name).exists():
            return d / name
    for folder, p in photo_library(cfg) + headshot_library(cfg):
        if p.name == name:
            return p
    for root in output_roots(cfg):
        hit = next(root.rglob(name), None)
        if hit:
            return hit
    return None


def dump_cfg(v, level=0):
    """workspaces.json as text, in its own compact style (one line per small object) so a change to one image does not rewrite the file."""
    pad = "  " * level
    if isinstance(v, dict) and v:
        flat = json.dumps(v, ensure_ascii=False)
        scalar = not any(isinstance(x, (dict, list)) for x in v.values())
        if level >= 2 and len(flat) <= 300 or level == 1 and (len(flat) <= 100 or scalar and len(flat) <= 300):
            return flat
        inner = ",\n".join(f"{pad}  {json.dumps(k, ensure_ascii=False)}: {dump_cfg(x, level + 1)}" for k, x in v.items())
        return "{\n" + inner + "\n" + pad + "}"
    if isinstance(v, list) and v:
        flat = json.dumps(v, ensure_ascii=False)
        if len(flat) <= 300:
            return flat
        return "[\n" + ",\n".join(f"{pad}  {dump_cfg(x, level + 1)}" for x in v) + "\n" + pad + "]"
    return json.dumps(v, ensure_ascii=False)


def write_cfg(cfg):
    CFG_PATH.write_text(dump_cfg(cfg) + "\n", encoding="utf-8")


PLACEHOLDER_IMAGE = re.compile(r"_00001_\.png$")
LEGACY_APOSE = re.compile(r"^([A-Za-z]+)_Qwen_X_Pose\.json$")  # the old single A-pose workflow, which read the photo (now Alpha 1 Prime)


def input_choices(cfg, workspaces=None, root=None, hero=None):
    """The default images you chose inside the workspaces' generated Qwen workflows, set against workspaces.json.

    Per (hero, role) - photo, prime, bare, apose, scene, polish - it looks at every generated Qwen workflow whose role that is. The tool's own placeholders (..._00001_.png) and
    images named for another hero are not a choice. One image that differs from the configured one is "changed" (pull it); several different ones are "mixed" (reported,
    never pulled); otherwise "same". The old <Hero>_Qwen_X_Pose.json counts as the photo workflow."""
    idx, repo, groups = input_index(cfg), repo_files(cfg), hero_groups()
    flows = flow_index(cfg)
    seen = collections.defaultdict(collections.Counter)
    for ws in workspaces if workspaces is not None else list(cfg["workspaces"]):
        if not workspace_ready(cfg, ws, root)[0]:
            continue
        for name, p in install_files(cfg, ws, root).items():
            if "_Qwen_" not in name:
                continue
            base = name[:-5] if name.endswith(".json") else name
            legacy = LEGACY_APOSE.match(name)
            if legacy and base not in idx:
                h, role = legacy.group(1), "photo"
            elif base in idx and name in repo:
                h, stage, family = idx[base]
                role = input_role(cfg, h, stage, family)
            else:
                continue
            if not role or (hero and h.lower() != hero.lower()) or is_hand_made(cfg, ws, p, root):
                continue
            wf = read_wf(p)
            img = input_image(wf) if isinstance(wf, dict) else None
            others = [o.lower() + "_" for o in groups if o.lower() != h.lower()]
            if img and not PLACEHOLDER_IMAGE.search(img) and not any(img.lower().startswith(o) for o in others):
                seen[(h, role, flows.get(base))][img] += 1
    out = []
    for (h, role, flow), counts in sorted(seen.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2] or "")):
        conf = cfg.get("inputs", {}).get(h)
        conf = conf if isinstance(conf, dict) else {}
        want = flow_photo(cfg, flow, h) if flow else cfg.get("photos", {}).get(h) if role == "photo" else (conf.get(role) or conf.get("apose"))
        state = "same" if set(counts) <= {want} else ("changed" if len(counts) == 1 else "mixed")
        out.append({"hero": h, "role": role, "flow": flow, "configured": want, "counts": dict(counts), "state": state, "chosen": next(iter(counts)) if len(counts) == 1 else None})
    return out


def pull_inputs(cfg, args, workspaces=None):
    """Write the default images you chose in the workspaces into workspaces.json (photos / inputs / flows), so a later `inputs reset` or a rebuilt workflow keeps them."""
    found = input_choices(cfg, workspaces, args.root, getattr(args, "hero", None))
    changed = [c for c in found if c["state"] == "changed"]
    for c in found:
        if c["state"] == "mixed":
            where = f" --flow {c['flow']}" if c["flow"] else ""
            print(f"  MIXED    {c['hero']} {c['role']}{' (flow ' + c['flow'] + ')' if c['flow'] else ''}: the workflows load different images {c['counts']}; set the one you want with: inputs set {c['hero']}{where} --{'photo' if c['role'] == 'photo' else c['role']} NAME")
    for c in changed:
        print(f"  pull     {c['hero']:10} {c['role'] + (' [' + c['flow'] + ']' if c['flow'] else ''):14} {c['configured'] or '-'} -> {c['chosen']}  ({sum(c['counts'].values())} workflow(s))")
        if not args.dry_run:
            if c["flow"]:
                cfg["flows"][c["flow"]].setdefault("photos", {})[c["hero"]] = c["chosen"]
            elif c["role"] == "photo":
                cfg.setdefault("photos", {})[c["hero"]] = c["chosen"]
            else:
                conf = cfg.setdefault("inputs", {}).get(c["hero"])
                cfg["inputs"][c["hero"]] = conf = conf if isinstance(conf, dict) else {}
                conf[c["role"]] = c["chosen"]
    if changed and not args.dry_run:
        write_cfg(cfg)
    print(f"inputs pull: {len(changed)} default image(s) " + ("would be " if args.dry_run else "") + "taken from the workspaces" + ("" if changed else " (workspaces.json already matches)") + (" - now run: inputs reset" if changed and not args.dry_run else ""))
    return len(changed)


def inputs_status(cfg):
    """Per hero: the configured photo, barefoot A-pose and bare-skin images, where each was found and whether it is the standard size."""
    std = tuple(cfg.get("standardSize") or ())
    print(f"standard size: {'x'.join(map(str, std)) if std else '(not set)'}")
    for h in sorted(cfg.get("photos", {})):
        conf = cfg.get("inputs", {}).get(h)
        conf = conf if isinstance(conf, dict) else {}
        print(h)
        for role, name in (("photo", cfg["photos"].get(h)), ("prime", conf.get("prime")), ("bare", conf.get("bare")), ("apose", conf.get("apose")), ("heels", conf.get("heels")), ("scene", conf.get("scene")), ("polish", conf.get("polish"))):
            if not name:
                print(f"    {role:6} -")
                continue
            p = find_image(cfg, name)
            size = image_size(p) if p else None
            flag = "MISSING" if not p else ("?" if not size else ("ok" if not std or size == std else "WRONG SIZE"))
            print(f"    {role:6} {name:48} {'x'.join(map(str, size)) if size else '-':10} {flag}" + (f"  ({p.parent.name})" if p else ""))
        for flow, spec in sorted(cfg.get("flows", {}).items()):
            name = spec.get("photos", {}).get(h)
            if name:
                p = find_image(cfg, name)
                size = image_size(p) if p else None
                flag = "MISSING" if not p else ("?" if not size else ("ok" if not std or size == std else "WRONG SIZE"))
                print(f"    {'flow ' + flow:11} {name:43} {'x'.join(map(str, size)) if size else '-':10} {flag}" + (f"  ({p.parent.name})" if p else ""))


def set_inputs(cfg, args):
    """Write --photo / --prime / --bare / --apose for one hero into workspaces.json (then run inputs reset). With --flow NAME, --photo is the image that flow feeds the hero's Prime instead
    (the flow is created when it is new; `make --create` then builds its workflows)."""
    hero = next((h for h in cfg.get("photos", {}) if h.lower() == args.set.lower()), None)
    if not hero:
        sys.exit(f"Unknown hero '{args.set}'. Known: {list(cfg.get('photos', {}))}")
    if getattr(args, "flow", None):
        if not args.photo:
            sys.exit("inputs set HERO --flow NAME needs --photo IMAGE (the image that flow feeds the Prime)")
        cfg.setdefault("flows", {}).setdefault(args.flow, {"label": "", "photos": {}}).setdefault("photos", {})[hero] = args.photo
        print(f"{hero}: flow {args.flow} photo={args.photo}")
        if args.dry_run:
            print("(dry run, nothing written)")
        else:
            write_cfg(cfg)
            print(f"workspaces.json updated; now run: make --create --hero {hero} --match Prime (and deploy), or inputs reset --hero {hero}")
        return
    if args.photo:
        cfg["photos"][hero] = args.photo
    conf = cfg["inputs"].get(hero)
    conf = conf if isinstance(conf, dict) else {}
    for role in ("prime", "bare", "apose", "heels", "scene", "polish"):
        if getattr(args, role):
            conf[role] = getattr(args, role)
    cfg["inputs"][hero] = conf
    print(f"{hero}: photo={cfg['photos'].get(hero)} prime={conf.get('prime')} bare={conf.get('bare')} apose={conf.get('apose')} heels={conf.get('heels')}")
    if args.dry_run:
        print("(dry run, nothing written)")
    else:
        write_cfg(cfg)
        print("workspaces.json updated; now run: inputs reset --hero " + hero)


PHOTO_ROOTS = ["Angels", "Sisters", "Models", "Prospects", "Artists", "Various"]  # Models is the old name of Sisters; Various is the pool of photos not yet sorted
SISTER_ROOTS = ("Sisters", "Models")


def photo_roots(cfg, base=None):
    """The folders that hold the original-photo library: <work root>/<name> for each of paths.photoRoots (default Angels, Sisters, Prospects, Artists, Various; the old Models folder is still read)."""
    base = pathlib.Path(base) if base else work_root(cfg)
    return [base / n for n in cfg.get("paths", {}).get("photoRoots", PHOTO_ROOTS) if (base / n).is_dir()]


def photo_folders(cfg, base=None):
    """[(group, name, path)] of every library folder that has a gallery: <root>/<Name>, and <root>/<Name>/<Sub> (an artist's folder grouped by the face in it); name is 'Name' or 'Name/Sub'.
    A root that has a gallery itself (the Various pool) is one folder whose group and name are both the root's."""
    out = []
    for root in photo_roots(cfg, base):
        if (root / "gallery").is_dir():
            out.append((root.name, root.name, root))
            continue
        for d in sorted(p for p in root.iterdir() if p.is_dir()):
            if (d / "gallery").is_dir():
                out.append((root.name, d.name, d))
            for s in sorted(p for p in d.iterdir() if p.is_dir()):
                if (s / "gallery").is_dir():
                    out.append((root.name, f"{d.name}/{s.name}", s))
    return out


def photo_library(cfg, base=None):
    """[(folder name, path)] of every scaled original: <folder>/gallery_<W>x<H>/*.png, for each library folder and each person grouped inside an artist's folder (the _org archive folders are not part of it)."""
    w, h = cfg.get("standardSize") or (944, 1104)
    out = []
    for root in photo_roots(cfg, base):
        for d in ([root] if (root / "gallery").is_dir() else sorted(p for p in root.iterdir() if p.is_dir())):
            for name, folder in [(d.name, d)] + [(f"{d.name}/{s.name}", s) for s in sorted(p for p in d.iterdir() if p.is_dir())]:
                g = folder / f"gallery_{w}x{h}"
                if g.is_dir():
                    out += [(name, f) for f in sorted(g.glob("*.png"))]
    return out


def headshot_library(cfg, base=None):
    """[(folder name, path)] of every derived Prime input: <folder>/headshot_<W>x<H>/*.png (the face) and <folder>/frame_<W>x<H>/*.png (a partial-body photo shrunk to figure size). Kept apart from
    photo_library: they share their photo's id, so they must never count as the photo's rename."""
    w, h = cfg.get("standardSize") or (944, 1104)
    out = []
    for root in photo_roots(cfg, base):
        for d in ([root] if (root / "gallery").is_dir() else sorted(p for p in root.iterdir() if p.is_dir())):
            for name, folder in [(d.name, d)] + [(f"{d.name}/{s.name}", s) for s in sorted(p for p in d.iterdir() if p.is_dir())]:
                for kind in ("headshot", "frame"):
                    g = folder / f"{kind}_{w}x{h}"
                    if g.is_dir():
                        out += [(name, f) for f in sorted(g.glob("*.png"))]
    return out


PHOTO_KEY = re.compile(r"(image_\d+|(?:screenshot|shot)_\d{8}_?\d{6}|pic_[0-9a-f]{8})", re.I)


def photo_key(name):
    """The id inside an original's name (a Facebook id, a screenshot's date and time in either spelling, or pic_<hex>), or None: it identifies the picture whatever folder or prefix it has."""
    m = PHOTO_KEY.search(name)
    if not m:
        return None
    key = m[1].lower()
    shot = re.match(r"(?:screenshot|shot)_(\d{8})_?(\d{6})$", key)
    return f"shot_{shot[1]}{shot[2]}" if shot else key


def reconcile_photos(cfg, dry_run, root=None, hero=None, work=None):
    """A chosen photo whose original was renamed (moved into the hero's own folder, or renamed by the originals tool) is found again by its id and re-pointed:
    in workspaces.json ("photos"), in every generated workflow of that hero that loads it (repo and workspaces; a changed workspace file is backed up first), and its
    scaled image is copied into the input folder of each workspace that needed it. A photo whose original is gone, or sits in another hero's folder, is reported, never guessed."""
    by_name, by_key = collections.defaultdict(list), collections.defaultdict(list)
    heads = {p.name.lower() for _, p in headshot_library(cfg, work)}
    for folder, p in photo_library(cfg, work):
        by_name[p.name.lower()].append((folder, p))
        k = photo_key(p.name)
        if k:
            by_key[k].append((folder, p))
    renames = {}
    for h, name in sorted(cfg.get("photos", {}).items()):
        if hero and h.lower() != hero.lower():
            continue
        if name.lower() in heads:
            continue  # a headshot chosen on purpose
        m = photo_key(name)
        mine = [(f, p) for f, p in by_key.get(m, []) if f.lower() == h.lower()] if m else []
        if any(p.name == name for _, p in mine):
            continue
        if mine:
            renames[h] = (name, mine[0][1])
            print(f"  photo    {h:10} {name} -> {mine[0][1].name}")
        elif by_name.get(name.lower()):
            continue  # a photo kept in another folder on purpose (Female uses an Artists photo)
        elif m and by_key.get(m):
            print(f"  ELSEWHERE {h}: {name} is now in {', '.join(sorted({f for f, _ in by_key[m]}))}, not in {h}'s folder; move the original there, or choose it with: inputs set {h} --photo NAME")
        elif not find_image(cfg, name):
            if m:
                print(f"  MISSING  {h}: {name} is not in the library or any input folder (its original was removed?); choose another with: inputs set {h} --photo NAME")
            else:
                print(f"  NO PHOTO {h}: {name} is a placeholder; put originals in {h}'s library folder, run originals, then: inputs set {h} --photo NAME")
    for flow, spec in sorted(cfg.get("flows", {}).items()):
        for h, name in sorted(spec.get("photos", {}).items()):
            if (not hero or h.lower() == hero.lower()) and not find_image(cfg, name):
                print(f"  MISSING  {h} flow {flow}: {name} is not in the library or any input folder (its original was removed or renamed?); run originals, then: inputs set {h} --flow {flow} --photo NAME")
    if not renames:
        print("inputs photos: every chosen photo is where workspaces.json says")
        return 0
    touched = repoint_photos(cfg, renames, dry_run, root)
    print(f"inputs photos: {len(renames)} photo(s) re-pointed" + (" (dry run)" if dry_run else "") + "; workflows changed: " + (", ".join(f"{v} in {k}" for k, v in touched.items()) or "none"))
    return len(renames)


def repoint_photos(cfg, renames, dry_run, root=None):
    """renames: {hero: (old image name, path of the scaled new image)}. Point every generated workflow of that hero that loads the old name at the new one (repo and
    workspaces; a changed workspace file is backed up first), copy the new image into each workspace input folder that needed it, and write the new name into workspaces.json
    "photos". Returns {where: number of workflows changed}."""
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    repo, touched, copied = repo_files(cfg), collections.Counter(), set()

    def retarget(p, ws):
        wf = read_wf(p)
        ln = node_of(wf, "LoadImage") if isinstance(wf, dict) else None
        if not ln:
            return
        for h, (old, newp) in renames.items():
            if ln["widgets_values"][0] == old and p.name.split("_", 1)[0].lower() == h.lower():
                touched[ws or "repo"] += 1
                if not dry_run:
                    if ws:
                        backup(stamp, ws, p.name, p)
                    ln["widgets_values"][0] = newp.name
                    if isinstance(ln.get("widgets_values_named"), dict) and "image" in ln["widgets_values_named"]:
                        ln["widgets_values_named"]["image"] = newp.name
                    write_wf(p, wf)
                if ws and (ws, newp.name) not in copied:
                    copied.add((ws, newp.name))
                    d = input_dir(cfg, ws)
                    print(f"  {'would copy' if dry_run else 'copied   '} {newp.name} -> {d}")
                    if not dry_run and not (d / newp.name).exists():
                        shutil.copy2(newp, d / newp.name)

    for name, (g, h, p) in repo.items():
        if h in renames:
            retarget(p, None)
    for ws in list(cfg["workspaces"]):
        if not workspace_ready(cfg, ws, root)[0]:
            continue
        for name, p in install_files(cfg, ws, root).items():
            if name in repo and repo[name][1] in renames and not is_hand_made(cfg, ws, p, root):
                retarget(p, ws)
    if not dry_run:
        for h, (old, newp) in renames.items():
            cfg.setdefault("photos", {})[h] = newp.name
        write_cfg(cfg)
    return touched


def denoise_plan(cfg):
    """{workflow name: (hero, stage, family, role, denoise)} for every Qwen and FireRed workflow whose card gives a hint."""
    plan = {}
    for engine in ("qwen", "firered"):
        for it in prompt_index(cfg, engine):
            it["engine"] = engine
            if is_text_item(cfg, it):
                continue
            role = input_role(cfg, it["hero"], it["stage"], it["family"])
            dn = denoise_for(cfg, it["path"].read_text(encoding="utf-8"), role)
            if dn is not None:
                plan[it["name"]] = (it["hero"], it["stage"], it["family"], role, dn)
    return plan


def cmd_denoise(args):
    """Show, or with --reset apply, the denoise every generated workflow should start at (see denoise_for). Shots, curated and test workflows are left alone."""
    cfg = load_cfg()
    for label, rel in [("poses", cfg["templates"]["poses"]), ("default", cfg["templates"]["default"]), ("firered", cfg["engines"]["firered"]["template"])]:
        wf = read_wf(ROOT / rel)
        print(f"template {label:8} {rel}: denoise " + ("exposed on the outer node, set to " + str(get_denoise(wf)) if get_denoise(wf) is not None else "NOT exposed outside the subgraph"))
    plan = denoise_plan(cfg)
    rule = cfg.get("denoise", {})
    print(f"rule: pick the {rule.get('pick', 'high')} end of the range in each stage template (_templates/heroes/*.txt, 'Denoise ~lo-hi'); a 1.0 template fed a golden image uses {rule.get('golden', 0.7)}")
    wanted = {k: v for k, v in plan.items() if (not args.hero or v[0].lower() == args.hero.lower()) and (not args.stage or v[1] == args.stage)
              and (not args.match or name_matches(args.match, k))}
    table = collections.Counter((v[1], v[2][0] if v[2] else "", v[3] or "-", v[4]) for v in wanted.values())
    print(f"\n{'stage':10} {'family':12} {'input':6} denoise   workflows")
    for (stage, fam, role, dn), n in sorted(table.items()):
        print(f"{stage:10} {fam:12} {role:6} {dn:<9} {n}")
    if not args.reset:
        print("\nPreview only: add --reset to set these in the repo and every workspace (a changed workspace file is backed up first).")
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    changed, kept = collections.Counter(), collections.defaultdict(list)
    repo = repo_files(cfg)
    # What the repo copies hold now is what the tool last set; a workspace copy that differs from it was changed by you in place, and is kept (unless --force).
    before = {}
    for name, (g, h, p) in repo.items():
        wf = read_wf(p)
        before[name[:-5] if name.endswith(".json") else name] = get_denoise(wf) if isinstance(wf, dict) else None
    spots = [(None, p, name) for name, (g, h, p) in repo.items()]
    for ws in args.workspace or cfg["workspaces"]:
        if workspace_ready(cfg, ws, args.root)[0]:
            spots += [(ws, p, name) for name, p in install_files(cfg, ws, args.root).items() if name in repo and not is_hand_made(cfg, ws, p, args.root)]
    for ws, p, name in spots:
        stem = name[:-5] if name.endswith(".json") else name
        if stem not in wanted:
            continue
        wf = read_wf(p)
        if not isinstance(wf, dict) or get_denoise(wf) == wanted[stem][4] or get_denoise(wf) is None:
            continue
        if ws and not getattr(args, "force", False) and before.get(stem) is not None and abs(get_denoise(wf) - before[stem]) > 1e-6:
            kept[ws].append(f"{p.name} ({round(get_denoise(wf), 3)}, the tool would set {wanted[stem][4]})")
            continue
        changed[ws or "repo"] += 1
        if args.dry_run:
            continue
        if ws:
            backup(stamp, ws, p.name, p)
        set_denoise(wf, wanted[stem][4])
        write_wf(p, wf)
    for ws, names in kept.items():
        print(f"  KEPT     {len(names)} workflow(s) in {ws} carry a denoise you set by hand (use --force to overwrite): " + "; ".join(names[:6]) + (" ..." if len(names) > 6 else ""))
    print("denoise reset: " + (", ".join(f"{v} in {k}" for k, v in changed.items()) or "nothing to change") + (" (dry run)" if args.dry_run else ""))


def cmd_inputs(args):
    cfg = load_cfg()
    placeholder = re.compile(r"^(.+)_Qwen_X_Pose_00001_\.png$")
    if args.status:
        inputs_status(cfg)
        return
    if args.set:
        set_inputs(cfg, args)
        return
    if args.pull:
        pull_inputs(cfg, args, args.workspace)
        return
    if args.reset:
        reset_inputs(cfg, args, args.workspace)
        return
    if args.sync:
        sync_inputs(cfg, args, args.workspace)
        return
    if args.photos:
        reconcile_photos(cfg, args.dry_run, args.root, args.hero)
        return
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
            if stage_of(p.name) in ("poses", "alpha"):
                continue
            wf = read_wf(p)
            ln = node_of(wf, "LoadImage")
            if ln and placeholder.match(ln["widgets_values"][0]) and want != ln["widgets_values"][0]:
                print(f"      fix {p.name}: {ln['widgets_values'][0]} -> {want}")
                if not args.dry_run:
                    ln["widgets_values"][0] = want
                    write_wf(p, wf)


# ---------- candidates and finals ----------
# zz_Candidates: a generated workflow kept for a render with only small changes (seed, denoise, input, toggles); a numbered ComfyUI save (Hero_Qwen_..._00015_) is one.
# zz_Final: the candidate (or shot) you chose; one per slot (hero x engine x stage). zz_Shots (edited prompts) and zz_Curated (hand-written) are separate.
# All of them are hand-made (the zz_ guard), kept in the repo under workflows/_candidates and _final, and arranged like the main tree. `finals sort` puts a file where its NAME
# says it belongs (a misspelling, a wrong folder or a drop into the zz_Final root are corrected), never deleting: an identical duplicate goes to backup, a different one is a conflict.
CANDIDATES_DIR = "zz_Candidates"
FINAL_DIR = "zz_Final"
PREVIOUS_DIR = "_previous"
CANDIDATES = WF / "_candidates"
FINALS = WF / "_final"
DEFAULT_ALIASES = {"X_Pose": "Alpha_1_Prime"}  # the Prime was once called X_Pose; saves from then are still the Prime
DEFAULT_SLOTS = {"prime": ["Alpha_1_Prime", "X_Pose"], "bare": ["Alpha_2_Bare_Figure", "Alpha_2_Bare_Skin"], "golden": ["Alpha_3_Barefoot"]}


def finals_slots(cfg):
    return cfg.get("finals", {}).get("slots") or DEFAULT_SLOTS


def finals_index(cfg):
    """{stem: (group, hero, path)} for every generated workflow: what a saved candidate or final can be matched to."""
    return {n[:-5]: v for n, v in repo_files(cfg).items()}


def output_sub(wf):
    """The phase folders of a workflow's output below the hero (1_Alpha/1_Prime), so the repo copy of a candidate or final mirrors the main tree."""
    s = save_node(wf)
    parts = s["widgets_values"][0].split("/") if s else []
    n = 2 if len(parts) > 1 and parts[1] in art_layout.divisions(parts[0]) else 1
    if len(parts) < n + 3 or parts[n + 1].startswith(("_", ".")):
        return pathlib.Path()
    return pathlib.Path(*parts[n + 1:-1])


def parse_saved(cfg, name, heroes, stems):
    return finals.parse_name(name, heroes, stems, cfg.get("finals", {}).get("aliases", DEFAULT_ALIASES))


def canon_name(parsed):
    return parsed["file_stem"] + (f"_{parsed['counter']}_" if parsed["counter"] else "") + ".json"


ASSETS = ROOT / "assets" / "art"
RECORDS = ROOT / "data" / "art" / "finals"
# A final's settings are kept in the art data (data/art/finals/<set>.json, one record per workflow name) and replayed by `make`: the same seed (set to fixed), denoise and turbo,
# with the new prompt, so a regenerated stage keeps the composition you chose. `finals record` reads them from the finals in the repo; a record you edited by hand is kept.
RECORD_NOTE = "Settings of the workflows you chose as finals, one record per workflow name (Hero_Engine_Stage). Written by `finals record`, replayed by `make`; you may edit a record by hand (it is kept while the render it came from is still the final)."


def subgraph_nodes(wf):
    for sg in wf.get("definitions", {}).get("subgraphs", []):
        yield from sg.get("nodes", [])


def final_settings(wf):
    """What a final workflow holds that is worth replaying: seed, denoise, turbo (the Lightning LoRA) from the outer node, steps, cfg, sampler and scheduler from its KSampler, and every image it loads."""
    n = prompt_node(wf)
    named = (n.get("widgets_values_named") if n else None) or {}
    out = {"seed": named.get("seed"), "denoise": named.get("denoise"), "turbo": named.get("value") if isinstance(named.get("value"), bool) else None}
    for node in subgraph_nodes(wf):
        if node.get("type") == "KSampler" and len(node.get("widgets_values", [])) >= 7:
            _seed, _control, out["steps"], out["cfg"], out["sampler"], out["scheduler"], _denoise = node["widgets_values"][:7]
    out["inputs"] = [x["widgets_values"][0] for x in list(wf.get("nodes", [])) + list(subgraph_nodes(wf)) if x.get("type") == "LoadImage" and x.get("widgets_values")]
    return {k: v for k, v in out.items() if v is not None}


def apply_final_settings(wf, rec):
    """Replay a record on a generated workflow: seed (and its control set to fixed), denoise and turbo. Returns True if anything changed."""
    changed = False
    n = prompt_node(wf)
    named = n.get("widgets_values_named") if n else None
    if isinstance(named, dict):
        names = list(named)
        for key in ("seed", "denoise"):
            if rec.get(key) is not None and key in named and named[key] != rec[key]:
                named[key] = n["widgets_values"][names.index(key)] = rec[key]
                changed = True
        if isinstance(rec.get("turbo"), bool) and isinstance(named.get("value"), bool) and named["value"] != rec["turbo"]:
            set_turbo(wf, rec["turbo"])
            changed = True
    if rec.get("seed") is not None:
        for node in subgraph_nodes(wf):
            if node.get("type") == "KSampler" and len(node.get("widgets_values", [])) >= 2 and node["widgets_values"][1] != "fixed":
                node["widgets_values"][1] = "fixed"
                changed = True
    return changed


def record_path(group):
    return RECORDS / f"{group}.json"


_RECORD_CACHE = {}


def load_records(group):
    """{workflow name: record} for a set (read once per file version: make asks for every workflow)."""
    p = record_path(group)
    if not p.is_file():
        return {}
    key = (str(p), p.stat().st_mtime_ns)
    if key not in _RECORD_CACHE:
        _RECORD_CACHE.clear()
        _RECORD_CACHE[key] = json.loads(p.read_text(encoding="utf-8")).get("finals", {})
    return _RECORD_CACHE[key]


def final_record(cfg, name):
    """The record for a generated workflow name (Hero_Qwen_Alpha_1_Prime.json), or None."""
    stem = name[:-5] if name.endswith(".json") else name
    group = hero_groups().get(stem.split("_", 1)[0])
    return load_records(group).get(stem) if group else None


# The image of a final is kept with it: assets/art/<set>/[<division>/]<Hero>/<phase>/<Hero>_<Engine>_<Stage>.png (the prompt-path convention, with the engine in the name so a Qwen and a FireRed final
# of one stage stay apart). Only finals get an image: candidates and shots never do.


def final_image_source(cfg, wf, counter):
    """The rendered PNG a final was saved from: <output project>/<SaveImage prefix>_<counter>_.png (or None: no counter in the name, or the render is not on disk)."""
    s = save_node(wf)
    if not counter or not s:
        return None
    prefix = s["widgets_values"][0]
    paths = cfg.get("paths", {})
    project = paths.get("outputFolders", {}).get(prefix.split("/")[0])
    base = paths.get("outputRoot") or cfg.get("sharedOutput")
    roots = ([pathlib.Path(base) / project] if base and project else []) + [pathlib.Path(x) for x in (base, cfg.get("sharedOutput")) if x]
    for r in roots:
        if (r / f"{prefix}_{counter}_.png").is_file():
            return r / f"{prefix}_{counter}_.png"
    return None


def final_image_dest(parsed, master_wf):
    s = save_node(master_wf)
    return ASSETS / pathlib.PurePosixPath(s["widgets_values"][0]).parent / (parsed["stem"] + ".png") if s else None


def capture_final_image(cfg, wf, parsed, master_wf, stamp, dry_run):
    """Copy the render of a final into assets/art. An image it replaces is copied to backup first. Returns 'copied', 'same', 'no image' or 'no counter'."""
    src, dst = final_image_source(cfg, wf, parsed["counter"]), final_image_dest(parsed, master_wf)
    if not parsed["counter"]:
        return "no counter"
    if not src or not dst:
        return "no image"
    if dst.exists() and dst.stat().st_size == src.stat().st_size and dst.read_bytes() == src.read_bytes():
        return "same"
    if not dry_run:
        if dst.exists():
            b = BACKUPS / stamp / "assets (replaced)" / dst.relative_to(ASSETS)
            b.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, b)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    print(f"  image     {src.name} ({src.stat().st_size // 1024} KB) -> {dst.relative_to(ROOT).as_posix()}" + (" (replaces the earlier image)" if dst.exists() else ""))
    return "copied"


def finals_entries(cfg, ws, root=None):
    """The candidates and finals a workspace holds (those in zz_Candidates and zz_Final, and numbered saves loose in the list), each with where it belongs: want (None = stay put)."""
    d = install_dir(cfg, ws, root)
    out = []
    if not d.is_dir():
        return out
    idx = finals_index(cfg)
    heroes, stems = list(hero_groups()), list(idx)
    for p in sorted(d.rglob("*.json")):
        rel = p.relative_to(d)
        top = rel.parts[0]
        if any(x.startswith(".") for x in rel.parts) or PREVIOUS_DIR in rel.parts:
            continue
        if top == SHOTS_DIR:
            parsed = parse_saved(cfg, p.name, heroes, stems)
            below = len(rel.parts) - 1  # a shot saved straight into zz_Shots (or straight into its hero folder) is filed by phase; one in a subfolder you made stays there
            if parsed and (below == 1 or (below == 2 and rel.parts[1] == parsed["hero"])):
                group, _hero, master = idx[parsed["stem"]]
                wf = read_wf(master)
                out.append({"path": p, "kind": "shot", "loose": False, "parsed": parsed, "group": group, "hero": parsed["hero"], "sub": output_sub(wf),
                            "want": d / special_dir(ws, SHOTS_DIR, parsed["hero"]) / output_sub(wf) / p.name})
            continue
        if top in (CANDIDATES_DIR, FINAL_DIR):
            kind, loose = ("candidate" if top == CANDIDATES_DIR else "final"), False
        elif is_capture(rel, p.name) and not any(x.startswith("_") for x in rel.parts):
            kind, loose = "candidate", True
        else:
            continue
        parsed = parse_saved(cfg, p.name, heroes, stems)
        e = {"path": p, "kind": kind, "loose": loose, "parsed": parsed, "want": None}
        if parsed:
            group, _hero, master = idx[parsed["stem"]]
            wf = read_wf(master)
            e.update(group=group, hero=parsed["hero"], sub=output_sub(wf),
                     want=d / (CANDIDATES_DIR if kind == "candidate" else FINAL_DIR) / workspace_subdir(ws, wf) / canon_name(parsed))
        out.append(e)
    return out


def _tidy_empty(base):
    """Remove the empty folders below a zz_ folder (never the folder itself)."""
    if base.is_dir():
        for f in sorted((q for q in base.rglob("*") if q.is_dir()), key=lambda q: len(q.parts), reverse=True):
            if not any(f.iterdir()):
                f.rmdir()


def finals_sort(cfg, ws, args, stamp):
    d = install_dir(cfg, ws, args.root)
    moved = dup = conflicts = stray = 0
    for e in finals_entries(cfg, ws, args.root):
        p, want, parsed = e["path"], e["want"], e["parsed"]
        rel = p.relative_to(d).as_posix()
        if parsed is None:
            print(f"  ?        {ws}/{rel}: cannot tell where it belongs from its name (left where it is)")
            stray += 1
            continue
        if args.hero and parsed["hero"].lower() != args.hero.lower():
            continue
        if want is None or p == want:
            continue
        note = f" (name corrected: {p.name} -> {want.name})" if want.name != p.name else ""
        if want.exists():
            if same_workflow(want, p):
                print(f"  duplicate {ws}/{rel}: the proper copy is already at {want.relative_to(d).as_posix()}; this one goes to backup")
                if args.apply:
                    backup(stamp, ws, p.name, p)
                    p.unlink()
                dup += 1
            else:
                print(f"  CONFLICT {ws}/{rel} differs from {want.relative_to(d).as_posix()}; rename one of them")
                conflicts += 1
            continue
        print(f"  {'move' if args.apply else 'would move'}  {ws}/{rel} -> {want.relative_to(d).as_posix()}{note}")
        if args.apply:
            want.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(want))
        moved += 1
    if args.apply:
        for z in (CANDIDATES_DIR, FINAL_DIR, SHOTS_DIR):
            _tidy_empty(d / z)
    print(f"{ws} finals sort: {moved} {'moved' if args.apply else 'to move'}, {dup} duplicate(s) to backup, {conflicts} conflict(s), {stray} not placeable")


def finals_find(cfg, ws, args):
    """Candidates and shots in a workspace whose name contains --match / the given name: [(path, parsed)]."""
    heroes, stems = list(hero_groups()), list(finals_index(cfg))
    want = args.name.lower().removesuffix(".json")
    found = [(e["path"], e["parsed"]) for e in finals_entries(cfg, ws, args.root) if e["kind"] == "candidate"]
    shots = install_dir(cfg, ws, args.root) / SHOTS_DIR
    if shots.is_dir():
        found += [(p, parse_saved(cfg, p.name, heroes, stems)) for p in sorted(shots.rglob("*.json"))]
    return [(p, q) for p, q in found if q and want in p.name.lower()]


USE_AS_ROLES = ("prime", "bare", "apose", "heels", "scene", "polish")


def use_final_as_input(cfg, ws, args, final_path, parsed):
    """Make the render of a final the hero's default image for a role (the Prime final feeds the Alpha 2 workflows, the Bare final the footwear, and so on): the PNG is copied into the input
    folder of every workspace that is home for the hero and workspaces.json says so; `inputs reset` then points the workflows at it. Only when you ask (--use-as); a plain promote never changes a default."""
    role, hero, group = args.use_as, parsed["hero"], hero_groups().get(parsed["hero"])
    src = final_image_source(cfg, read_wf(final_path), parsed["counter"])
    if not src:
        print(f"  --use-as {role}: the render of {final_path.name} was not found in the output folders (no render counter in the name, or it is not on disk); nothing changed")
        return
    homes = [w for w in home_workspaces(cfg, group, hero) if w in cfg["workspaces"]]
    for w in homes:
        dest = input_dir(cfg, w, ) / src.name
        print(f"  {'copy' if args.apply else 'would copy'}  {src.name} -> {w} input folder")
        if args.apply and not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    conf = cfg["inputs"].get(hero)
    conf = conf if isinstance(conf, dict) else {}
    print(f"  {'set' if args.apply else 'would set'}  workspaces.json inputs.{hero}.{role} = {src.name} (was {conf.get(role)}); then run: inputs reset --hero {hero} --apply")
    if args.apply:
        conf[role] = src.name
        cfg["inputs"][hero] = conf
        write_cfg(cfg)


def finals_promote(cfg, ws, args, stamp):
    d = install_dir(cfg, ws, args.root)
    hits = finals_find(cfg, ws, args)
    if not hits:
        print(f"{ws}: no candidate or shot matches '{args.name}'")
        return
    if len(hits) > 1:
        print(f"{ws}: '{args.name}' matches {len(hits)} files; give more of the name:")
        for p, _q in hits[:12]:
            print("    " + p.relative_to(d).as_posix())
        return
    src, parsed = hits[0]
    idx = finals_index(cfg)
    wf = read_wf(idx[parsed["stem"]][2])
    dest = d / FINAL_DIR / workspace_subdir(ws, wf) / canon_name(parsed)
    if dest.exists() and same_workflow(dest, src):
        print(f"{ws}: {src.name} is already the final for {parsed['stem']}")
        if args.use_as:
            use_final_as_input(cfg, ws, args, dest, parsed)
        return
    for e in finals_entries(cfg, ws, args.root):
        if e["kind"] == "final" and e["parsed"] and e["parsed"]["stem"] == parsed["stem"] and e["path"] != dest:
            old = d / FINAL_DIR / PREVIOUS_DIR / stamp / e["path"].name
            print(f"  {'archive' if args.apply else 'would archive'}  the earlier final {e['path'].relative_to(d).as_posix()} -> {old.relative_to(d).as_posix()}")
            if args.apply:
                old.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(e["path"]), str(old))
    if dest.exists():
        old = d / FINAL_DIR / PREVIOUS_DIR / stamp / dest.name
        print(f"  {'archive' if args.apply else 'would archive'}  the earlier final {dest.relative_to(d).as_posix()} (same file name, other render)")
        if args.apply:
            old.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dest), str(old))
    print(f"  {'promote' if args.apply else 'would promote'}  {src.relative_to(d).as_posix()} -> {dest.relative_to(d).as_posix()} (the original stays)")
    if args.apply:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    else:
        print("Preview only: add --apply to promote it.")
    if args.use_as:
        use_final_as_input(cfg, ws, args, dest if args.apply else src, parsed)


def finals_pull(cfg, ws, args, stamp=None):
    stamp = stamp or datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    done = same = 0
    images = collections.Counter()
    for e in finals_entries(cfg, ws, args.root):
        parsed = e["parsed"]
        if e["kind"] == "shot" or not parsed or (args.hero and parsed["hero"].lower() != args.hero.lower()):
            continue
        dst = (CANDIDATES if e["kind"] == "candidate" else FINALS) / e["group"] / e["hero"] / e["sub"] / canon_name(parsed)
        if e["kind"] == "final":
            images[capture_final_image(cfg, read_wf(e["path"]), parsed, read_wf(finals_index(cfg)[parsed["stem"]][2]), stamp, args.dry_run)] += 1
        if dst.exists() and same_workflow(dst, e["path"]):
            same += 1
            continue
        print(f"  {e['kind']:9} {ws}/{e['path'].relative_to(install_dir(cfg, ws, args.root)).as_posix()} -> {dst.relative_to(ROOT).as_posix()}" + (" (update)" if dst.exists() else ""))
        if not args.dry_run:
            write_wf(dst, read_wf(e["path"]))
        done += 1
    print(f"{ws} finals pull: {done} kept in the repo, {same} already there" + (f"; final images: {images['copied']} copied, {images['same']} already in assets/art"
          + (f", {images['no image']} render not found" if images["no image"] else "") + (f", {images['no counter']} name has no render counter" if images["no counter"] else "") if sum(images.values()) else "")
          + (" (dry run)" if args.dry_run else ""))


def finals_deploy(cfg, ws, args):
    """Repo candidates and finals of the heroes this workspace is home for that it lacks, into their proper folders. A file the workspace already has (wherever it sits) is left for `finals sort`."""
    d = install_dir(cfg, ws, args.root)
    idx = finals_index(cfg)
    heroes, stems = list(hero_groups()), list(idx)
    have = {e["parsed"]["stem"] + (e["parsed"]["counter"] or "") + e["kind"] for e in finals_entries(cfg, ws, args.root) if e["parsed"] and e["kind"] != "shot"}
    done = 0
    for kind, root, base in (("candidate", CANDIDATES, CANDIDATES_DIR), ("final", FINALS, FINAL_DIR)):
        for p in sorted(root.rglob("*.json")) if root.is_dir() else []:
            parts = p.relative_to(root).parts
            group, hero = parts[0], parts[1]
            parsed = parse_saved(cfg, p.name, heroes, stems)
            if not parsed or not is_home(cfg, ws, group, hero) or (args.hero and hero.lower() != args.hero.lower()):
                continue
            if parsed["stem"] + (parsed["counter"] or "") + kind in have:
                continue
            dest = d / base / workspace_subdir(ws, read_wf(idx[parsed["stem"]][2])) / p.name
            print(f"  {kind:9} {'copy' if args.apply else 'would copy'}  {p.relative_to(ROOT).as_posix()} -> {ws}/{dest.relative_to(d).as_posix()}")
            if args.apply:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dest)
            done += 1
    print(f"{ws} finals deploy: {done} {'copied' if args.apply else 'to copy'}")


def finals_status(cfg, ws, args, brief=False):
    entries = finals_entries(cfg, ws, args.root)
    d = install_dir(cfg, ws, args.root)
    count = collections.Counter(e["kind"] for e in entries)
    loose = sum(1 for e in entries if e["loose"])
    misplaced = sum(1 for e in entries if e["want"] is not None and e["path"] != e["want"])
    shots = sum(1 for _ in (d / SHOTS_DIR).rglob("*.json")) if (d / SHOTS_DIR).is_dir() else 0
    stray = sum(1 for e in entries if e["parsed"] is None)
    print(f"    candidates and finals: {count['candidate']} candidates ({loose} loose), {count['final']} finals, {shots} shots, {stray} not placeable (left where they are), {misplaced} to re-file (finals sort)"
          if brief else f"{ws}: {count['candidate']} candidates ({loose} loose), {count['final']} finals, {shots} shots, {stray} not placeable (left where they are), {misplaced} to re-file (finals sort)")
    if brief:
        return
    idx, slots = finals_index(cfg), finals_slots(cfg)
    heroes = sorted(h for h, g in hero_groups().items() if is_home(cfg, ws, g, h) and (not args.hero or h.lower() == args.hero.lower()))
    marks = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.Counter()))
    for e in entries:
        if e["parsed"] and e["kind"] != "shot":
            marks[(e["parsed"]["hero"], e["parsed"]["engine"])][e["parsed"]["stem"]][e["kind"]] += 1
    rows, idle = [], 0
    for h in heroes:
        active = False
        for engine in finals.ENGINES:
            cells = []
            for label in slots:
                stem = next((f"{h}_{engine}_{n}" for n in slots[label] if f"{h}_{engine}_{n}" in idx), None)
                if stem is None:
                    continue
                c = marks.get((h, engine), {}).get(stem, collections.Counter())
                cells.append(f"{label} " + ("FINAL" if c["final"] else f"c{c['candidate']}" if c["candidate"] else "-"))
                active = active or bool(c["final"] or c["candidate"])
            slot_stems = {f"{h}_{engine}_{n}" for names in slots.values() for n in names}
            other = sum(c["final"] for s, c in marks.get((h, engine), {}).items() if s not in slot_stems)
            active = active or bool(other)
            if cells and any(not x.endswith(" -") for x in cells) or other:
                rows.append(f"    {h:12} {engine:8} " + "   ".join(cells) + (f"   +{other} other final(s)" if other else ""))
        idle += 0 if active else 1
    for r in rows:
        print(r)
    print(f"    {len(heroes)} hero(es) are home here; {idle} have no candidate or final yet (c<N> = candidates kept, FINAL = a final is set, - = none)")


def finals_record(cfg, args):
    """Write the settings of every final kept in the repo (workflows/_final) into data/art/finals/<set>.json. Preview unless --apply. A record you edited by hand is kept while its render is still the final."""
    heroes, idx = list(hero_groups()), finals_index(cfg)
    today = datetime.date.today().isoformat()
    per_group, tally = {}, collections.Counter()
    for p in sorted(FINALS.rglob("*.json")) if FINALS.is_dir() else []:
        parsed = parse_saved(cfg, p.name, heroes, list(idx))
        if not parsed or (args.hero and parsed["hero"].lower() != args.hero.lower()):
            continue
        group = idx[parsed["stem"]][0]
        records = per_group.setdefault(group, dict(load_records(group)))
        fresh = final_settings(read_wf(p))
        fresh.update(render=parsed["counter"], date=today)
        old = records.get(parsed["stem"])
        if old and old.get("render") == fresh["render"] and any(old.get(k) != v for k, v in fresh.items() if k != "date") and not getattr(args, "force", False):
            print(f"  kept     {parsed['stem']}: the record differs from the final it came from (hand edits); --force replaces it")
            tally["kept"] += 1
            continue
        if old and {k: v for k, v in old.items() if k != "date"} == {k: v for k, v in fresh.items() if k != "date"}:
            tally["same"] += 1
            continue
        print(f"  {'record' if args.apply else 'would record'}  {parsed['stem']}: seed {fresh.get('seed')}, denoise {fresh.get('denoise')}, turbo {fresh.get('turbo')}, {len(fresh.get('inputs', []))} input(s)" + (" (replaces the earlier record)" if old else ""))
        records[parsed["stem"]] = fresh
        tally["recorded"] += 1
    if args.apply:
        for group, records in per_group.items():
            record_path(group).parent.mkdir(parents=True, exist_ok=True)
            record_path(group).write_text(json.dumps({"description": RECORD_NOTE, "finals": dict(sorted(records.items()))}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"finals record: {tally['recorded']} {'written' if args.apply else 'to write'}, {tally['same']} unchanged, {tally['kept']} hand-edited kept" + ("" if args.apply else " (preview: add --apply)"))


def finals_images(cfg, args, stamp):
    """Copy the render of every final kept in the repo (workflows/_final) into assets/art; preview unless --apply. Run it after `pull`, or to catch up."""
    heroes, idx = list(hero_groups()), finals_index(cfg)
    tally = collections.Counter()
    for p in sorted(FINALS.rglob("*.json")) if FINALS.is_dir() else []:
        parsed = parse_saved(cfg, p.name, heroes, list(idx))
        if not parsed or (args.hero and parsed["hero"].lower() != args.hero.lower()):
            continue
        tally[capture_final_image(cfg, read_wf(p), parsed, read_wf(idx[parsed["stem"]][2]), stamp, not args.apply)] += 1
    size = sum(f.stat().st_size for f in ASSETS.rglob("*.png")) if ASSETS.is_dir() else 0
    print(f"finals images: {tally['copied']} {'copied' if args.apply else 'to copy'}, {tally['same']} already in assets/art, {tally['no image']} render not found, {tally['no counter']} without a render counter; "
          f"assets/art holds {size / 1024 / 1024:.0f} MB of PNG" + ("" if args.apply else " (preview: add --apply)"))


def finals_reclassify(cfg, args, stamp):
    """Clean the repo with the same name rules as `finals sort`: numbered saves at the top of a hero's _shots folder were candidates all along and move to _candidates (a shot in a subfolder was
    deliberate and stays; a shot at the top of the hero folder is filed into its phase folder, keeping its name); candidates and finals already kept are moved to their proper path (typos corrected); an identical duplicate goes to backup (git history keeps it too);
    a different file at the same path is a conflict. A name that cannot be placed is left exactly where it is. Preview unless --apply."""
    heroes, idx = list(hero_groups()), finals_index(cfg)
    sources = [(p, "candidate" if CAPTURED_NAME.search(rel) else "shot") for (_h, rel), (_g, p) in shot_files().items() if "/" not in rel]
    for kind, root in (("candidate", CANDIDATES), ("final", FINALS)):
        sources += [(p, kind) for p in (sorted(root.rglob("*.json")) if root.is_dir() else [])]
    moved = dup = conflicts = 0
    left = []
    for p, kind in sources:
        parsed = parse_saved(cfg, p.name, heroes, list(idx))
        if not parsed or (args.hero and parsed["hero"].lower() != args.hero.lower()):
            if not parsed:
                left.append(p)
            continue
        group, _h, master = idx[parsed["stem"]]
        dst = (SHOTS if kind == "shot" else CANDIDATES if kind == "candidate" else FINALS) / group / parsed["hero"] / output_sub(read_wf(master)) / (p.name if kind == "shot" else canon_name(parsed))
        if p == dst:
            continue
        rel = p.relative_to(ROOT).as_posix()
        if dst.exists():
            if same_workflow(dst, p):
                print(f"  duplicate {rel}: the proper copy is already at {dst.relative_to(ROOT).as_posix()}; this one goes to backup")
                if args.apply:
                    b = BACKUPS / stamp / "repo duplicates" / p.relative_to(WF)
                    b.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(p), str(b))
                dup += 1
            else:
                print(f"  CONFLICT {rel} differs from {dst.relative_to(ROOT).as_posix()}; left where it is")
                conflicts += 1
            continue
        print(f"  {'move' if args.apply else 'would move'}  {rel} -> {dst.relative_to(ROOT).as_posix()}")
        if args.apply:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(dst))
        moved += 1
    if args.apply:
        for root in (CANDIDATES, FINALS, SHOTS):
            _tidy_empty(root)
    for p in left[:20]:
        print(f"  ?        {p.relative_to(ROOT).as_posix()}: cannot tell where it belongs; left in place")
    print(f"finals reclassify: {moved} {'moved' if args.apply else 'to move'}, {dup} duplicate(s) to backup, {conflicts} conflict(s), {len(left)} left in place" + ("" if args.apply else " (preview: add --apply)"))


def cmd_finals(args):
    cfg = load_cfg()
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    if args.action == "reclassify":
        return finals_reclassify(cfg, args, stamp)
    if args.action == "images":
        return finals_images(cfg, args, stamp)
    if args.action == "record":
        return finals_record(cfg, args)
    if args.action == "promote" and not args.name:
        sys.exit("finals promote needs the file name (or part of it) of the candidate or shot, e.g.  finals promote Remiah_Qwen_Alpha_1_Prime_00015 -w \"Angel Primes\" --apply")
    for ws in pick_targets(cfg, args, "all"):
        if not ready_or_skip(cfg, ws, args.root):
            continue
        {"sort": lambda: finals_sort(cfg, ws, args, stamp), "promote": lambda: finals_promote(cfg, ws, args, stamp), "pull": lambda: finals_pull(cfg, ws, args, stamp),
         "deploy": lambda: finals_deploy(cfg, ws, args), "status": lambda: finals_status(cfg, ws, args)}[args.action]()
    if args.action in ("sort", "deploy", "promote") and not args.apply:
        print("Preview only: add --apply to do it. Reload the ComfyUI workflow list afterwards.")


WRITES = ("deploy", "pull", "make", "inputs", "denoise", "fork")
INCLUDE_KINDS = ("curated", "tests", "shots", "staged", "finals")
DEPLOY_MODES = {"overwrite": "overwrite", "existing": "existing", "patch_only": "patch", "new_only": "new"}


def normalise(args):
    """Turn the readable options (deploy --include/--mode, pull --only, inputs ACTION) into the switches the commands read, and make every command that changes files
    preview unless --apply. Returns True when a command that would write ran as a preview, so the caller can say so."""
    if args.cmd == "deploy":
        for kind in filter(None, (args.include or "").split(",")):
            if kind not in INCLUDE_KINDS:
                sys.exit(f"--include knows {', '.join(INCLUDE_KINDS)}, not '{kind}'.")
            setattr(args, kind, True)
        if args.mode:
            setattr(args, {m: a for a, m in DEPLOY_MODES.items()}[args.mode], True)
        args.finals = "finals" in (args.include or "").split(",")
    if args.cmd == "pull":
        args.shots = args.only == "shots"
        args.templates = args.only == "templates"
        args.only_finals = args.only == "finals"
    if args.cmd == "inputs":
        if args.action == "set":
            if not args.target:
                sys.exit("inputs set needs the hero:  inputs set Remiah --photo name.png")
            args.set = args.target
        elif args.action:
            setattr(args, args.action, True)
    if args.cmd not in WRITES:
        return False
    writes = not (args.cmd == "inputs" and not (args.pull or args.reset or args.fix or args.set or args.photos or args.sync)) and not (args.cmd == "denoise" and not args.reset)
    explicit = args.dry_run
    args.dry_run = args.dry_run or not args.apply
    return writes and not args.apply and not explicit


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, targets=False, filters=False):
        p.add_argument("--root", help="override installsRoot (testing)")
        p.add_argument("--dry-run", action="store_true")
        if targets:
            p.add_argument("-w", "--workspace", action="append", help="a specific workspace (repeatable); for deploy it must be home for the set or accept it")
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
    s.add_argument("--include", help="extra kinds to deploy besides the generated workflows, comma separated: curated, shots, tests, staged (scenes held back by default), finals (candidates and finals kept in the repo)")
    s.add_argument("--mode", choices=["patch", "new", "existing", "overwrite"],
                   help="patch: only update prompt values in place (also in a legacy workspace); new: only add files the workspace lacks; existing: only refresh files it already has; overwrite: replace the whole file")
    s.add_argument("--apply", action="store_true", help="really do it (default: preview only)")
    s.set_defaults(curated=False, tests=False, shots=False, staged=False, existing=False, patch_only=False, new_only=False, overwrite=False)
    s = sub.add_parser("cleanup")
    common(s, False, True)
    s.add_argument("-w", "--workspace", action="append", help="the workspace to clean (required): removes what it is not home for, once the home workspace holds an identical copy")
    s.add_argument("--apply", action="store_true", help="really move the files to backup (default: preview only)")
    s.add_argument("--loose", action="store_true", help="treat a file as an identical copy when prompts and input image match (ignores seeds and other run-to-run changes)")
    s.add_argument("--show", type=int, default=5, help="names to list per kept reason")
    s.add_argument("--orphans", action="store_true", help="instead: move workflows no prompt defines any more (renamed or removed cards) to backup; needs --match, honours -w and --hero")
    s = sub.add_parser("fork")
    common(s)
    s.add_argument("name", help="generated workflow to copy, e.g. Drakness_MiniMax_Video_X_Pose_Laugh")
    s.add_argument("--as", dest="tag", required=True, help="short tag added to the new name, e.g. Hand")
    s.add_argument("--no-deploy", action="store_true", help="only create the curated copy; do not put it in the hero's home workspace")
    s.add_argument("--apply", action="store_true", help="really do it (default: preview only)")
    s = sub.add_parser("pull")
    common(s, True, True)
    s.add_argument("--force", action="store_true", help="also replace repo copies")
    s.add_argument("--prune", action="store_true", help="with --only shots: also move repo shots that the pulled workspaces no longer hold to backup")
    s.add_argument("--only", choices=["shots", "templates", "finals"], help="pull only this kind: shots (zz_Shots), templates (the ST stage templates) or finals (candidates and finals); the default is everything")
    s.add_argument("--apply", action="store_true", help="really do it (default: preview only)")
    s.set_defaults(shots=False, templates=False)
    s.add_argument("--include-legacy", action="store_true", help="also pull from a workspace whose pulling is turned off (its old hand-made workflows); generated copies are never replaced")
    s = sub.add_parser("make")
    common(s, False, True)
    s.add_argument("--create", action="store_true", help="also build workflows that do not exist yet")
    s.add_argument("--apply", action="store_true", help="really do it (default: preview only)")
    s.add_argument("--input", help="LoadImage file for created workflows")
    s.add_argument("-v", "--verbose", action="store_true")
    s = sub.add_parser("inputs")
    common(s, True)
    s.add_argument("action", nargs="?", choices=["status", "pull", "reset", "fix", "set", "photos", "sync"],
                   help="status: which images each hero uses; pull: take the defaults you chose in the workspaces into workspaces.json; reset: point every workflow back at its default image; fix: replace placeholder inputs; "
                        "sync: copy the images the deployed workflows load into their workspace's input folder when missing (changes no workflow and no setting); "
                        "photos: re-point a chosen photo that the originals tool renamed or moved (workspaces.json, workflows, input folders); "
                        "set HERO --photo/--prime/--bare/--apose ...: write a hero's images into workspaces.json. No action lists the configured and inferred A-poses")
    s.add_argument("target", nargs="?", help="with set: the hero")
    s.add_argument("--apply", action="store_true", help="really do it (default: preview only)")
    s.add_argument("--force", action="store_true", help="with reset: overwrite images chosen in the workspaces that have not been pulled")
    s.add_argument("--hero", help="with --reset: only this hero")
    s.add_argument("--stage", help="with --reset: only this prompt folder (alpha, poses, armor ...)")
    s.add_argument("--match", help="with --reset: only workflows whose name contains this")
    s.add_argument("--photo", help="with --set: original photo file name")
    s.add_argument("--flow", help="with --set --photo: the flow (a second way to run the Prime, for example frame) this photo belongs to, instead of the normal flow")
    s.add_argument("--prime", help="with --set: Alpha 1 Prime image (the bikini A-pose made from the photo)")
    s.add_argument("--apose", help="with --set: Barefoot golden A-pose file name (head and motion read it)")
    s.add_argument("--heels", help="with --set: Heels golden A-pose file name")
    s.add_argument("--scene", help="with --set: the chosen scene image (Polish reads it)")
    s.add_argument("--polish", help="with --set: the chosen polished image (Final reads it)")
    s.add_argument("--bare", help="with --set: Alpha 2 Bare image (bare skin, individual figure)")
    s = sub.add_parser("denoise")
    common(s, True)
    s.add_argument("--apply", action="store_true", help="with --reset: really do it (default: preview only)")
    s.add_argument("--reset", action="store_true", help="set every generated workflow's denoise (repo and workspaces) from its stage template's range; without it, only show the plan. A workspace workflow whose denoise you changed by hand is kept")
    s.add_argument("--force", action="store_true", help="with --reset: also overwrite denoise values you set by hand in a workspace (a changed file is backed up first)")
    s.add_argument("--hero")
    s.add_argument("--stage", help="prompt folder: poses, head, scene, hair, motion, armor, clothing, showcase, bare")
    s.add_argument("--match", help="substring of the file name")
    sub.choices["inputs"].set_defaults(pull=False, reset=False, fix=False, status=False, set=None, photos=False, sync=False)
    s = sub.add_parser("setup")
    common(s, True, False)
    s.add_argument("--apply", action="store_true", help="really do it (default: preview only)")
    s = sub.add_parser("tidy")
    common(s, True, True)
    s.add_argument("--apply", action="store_true", help="really move the files (default: preview only)")
    s.add_argument("-v", "--verbose", action="store_true")
    s = sub.add_parser("finals")
    common(s, True)
    s.add_argument("action", choices=["sort", "promote", "status", "pull", "deploy", "reclassify", "images", "record"],
                   help="sort: file candidates and finals where their name says (never deletes); promote: make a candidate or shot the final for its slot; status: candidates, finals and slots per workspace; "
                        "pull: keep them in the repo (_candidates, _final); deploy: put repo ones a workspace lacks into their folders; reclassify: clean the repo with the same rules; images: copy the render of each final into assets/art; record: write each final's seed, denoise and inputs into data/art/finals so make replays them")
    s.add_argument("name", nargs="?", help="with promote: the file name (or part of it) of the candidate or shot")
    s.add_argument("--hero")
    s.add_argument("--apply", action="store_true", help="really do it (sort, promote, deploy, reclassify, images and record preview by default; pull writes unless --dry-run)")
    s.add_argument("--force", action="store_true", help="with record: replace a record you edited by hand")
    s.add_argument("--use-as", choices=list(USE_AS_ROLES), help="with promote: also make this final's render the hero's default image for a role (prime feeds the Alpha 2 workflows, bare the footwear, apose head and motion); a plain promote changes no default")
    args = ap.parse_args(argv)
    previewed = normalise(args)
    {"list": cmd_list, "status": cmd_status, "deploy": cmd_deploy, "cleanup": cmd_cleanup, "pull": cmd_pull, "make": cmd_make, "inputs": cmd_inputs, "denoise": cmd_denoise, "fork": cmd_fork, "tidy": cmd_tidy, "setup": cmd_setup,
     "finals": cmd_finals}[args.cmd](args)
    if args.cmd == "deploy" and args.finals:
        for ws in pick_targets(load_cfg(), args, "home"):
            if ready_or_skip(load_cfg(), ws, args.root):
                finals_deploy(load_cfg(), ws, args)
    if previewed:
        print("Preview only: add --apply to do it.")


if __name__ == "__main__":
    main()
