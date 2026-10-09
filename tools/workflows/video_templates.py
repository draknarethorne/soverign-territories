"""Build the two MiniMax H3 image-to-video templates from the legacy one, and check that a template's links are consistent.

    python tools/workflows/video_templates.py            # rewrite workflows/_templates/ST6_MiniMax_Reel.json and ST6_MiniMax_Match.json

ST6_MiniMax_Reel   9:16 for Facebook reels: ResolutionSelector (9:16, 0.7 MP, multiple of 32 = 640x1152) sets the canvas, and the still is cover-cropped to it, so nothing is stretched.
ST6_MiniMax_Match  the video keeps the still's shape: the still is scaled to 0.95 MP in steps of 32 (944x1104 -> 928x1088) and that size is the canvas.

MiniMaxH3ImageToVideo stretches its first frame to the canvas, which is why both templates resize the still themselves. Both keep the legacy subgraph, models and turbo setup.
"""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEGACY = ROOT / "workflows" / "_archive" / "ST6_MiniMax_Video_legacy.json"
OUT = ROOT / "workflows" / "_templates"
NAMES = {"reel": "ST6_MiniMax_Reel.json", "match": "ST6_MiniMax_Match.json"}
SECONDS = 8
REEL = {"aspect": "9:16 (Portrait Widescreen)", "megapixels": 0.7, "multiple": 32}
MATCH = {"method": "lanczos", "megapixels": 0.95, "step": 32}


def read(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def node(wf, kind):
    return next(n for n in wf["nodes"] if n["type"] == kind)


def outer(wf):
    """The subgraph instance: the one top-level node whose type is a subgraph id."""
    ids = {sg["id"] for sg in wf["definitions"]["subgraphs"]}
    return next(n for n in wf["nodes"] if n["type"] in ids)


def slot(n, name):
    return next(i for i, s in enumerate(n["inputs"]) if s["name"] == name)


def new_id(wf, key):
    wf[key] += 1
    return wf[key]


def add_node(wf, kind, pos, size, inputs, outputs, widgets):
    n = {"id": new_id(wf, "last_node_id"), "type": kind, "pos": pos, "size": size, "flags": {}, "order": 0, "mode": 0,
         "inputs": inputs, "outputs": outputs, "properties": {"Node name for S&R": kind, "cnr_id": "comfy-core", "ver": "0.33.0"}, "widgets_values": widgets}
    wf["nodes"].append(n)
    return n


def widget_in(name, kind):
    return {"localized_name": name, "name": name, "type": kind, "widget": {"name": name}, "link": None}


def out(name, kind):
    return {"localized_name": name, "name": name, "type": kind, "links": []}


def connect(wf, src, src_slot, dst, dst_input, kind):
    """Link src's output slot to dst's input (by name), replacing whatever was linked there."""
    i = slot(dst, dst_input)
    old = dst["inputs"][i].get("link")
    if old is not None:
        wf["links"] = [l for l in wf["links"] if l[0] != old]
        for n in wf["nodes"]:
            for o in n.get("outputs", []):
                if o.get("links") and old in o["links"]:
                    o["links"].remove(old)
    lid = new_id(wf, "last_link_id")
    wf["links"].append([lid, src["id"], src_slot, dst["id"], i, kind])
    dst["inputs"][i]["link"] = lid
    src["outputs"][src_slot].setdefault("links", []).append(lid)
    return lid


def defaults(wf, width, height):
    """The outer node's defaults: 8 seconds, turbo on, and the canvas the linked size nodes produce (shown if the links are ever cut)."""
    o = outer(wf)
    named = o["widgets_values_named"]
    keys = list(named)
    for key, val in (("width", width), ("height", height), ("value_1", SECONDS), ("value", True)):
        named[key] = val
        o["widgets_values"][keys.index(key)] = val


def place(wf, nodes):
    """Number the top-level nodes in execution order, so the 'order' field is not stale."""
    for n, o in zip(nodes, range(len(nodes))):
        n["order"] = o


def build_reel(legacy):
    wf = copy.deepcopy(legacy)
    defaults(wf, 640, 1152)
    load, o = node(wf, "LoadImage"), outer(wf)
    sel = add_node(wf, "ResolutionSelector", [-560, 5600], [270, 170], [widget_in("aspect_ratio", "COMBO"), widget_in("megapixels", "FLOAT"), widget_in("multiple", "INT")],
                   [out("width", "INT"), out("height", "INT")], [REEL["aspect"], REEL["megapixels"], REEL["multiple"]])
    crop = add_node(wf, "ImageScale", [-560, 5900], [280, 190], [{"localized_name": "image", "name": "image", "type": "IMAGE", "link": None}, widget_in("upscale_method", "COMBO"),
                    widget_in("width", "INT"), widget_in("height", "INT"), widget_in("crop", "COMBO")], [out("IMAGE", "IMAGE")], ["lanczos", 640, 1152, "center"])
    connect(wf, load, 0, crop, "image", "IMAGE")
    connect(wf, sel, 0, crop, "width", "INT")
    connect(wf, sel, 1, crop, "height", "INT")
    connect(wf, crop, 0, o, "first_frame", "IMAGE")
    connect(wf, sel, 0, o, "width", "INT")
    connect(wf, sel, 1, o, "height", "INT")
    place(wf, [load, sel, crop, o, node(wf, "SaveVideo")])
    return wf


def build_match(legacy):
    wf = copy.deepcopy(legacy)
    defaults(wf, 928, 1088)
    load, o = node(wf, "LoadImage"), outer(wf)
    scale = add_node(wf, "ImageScaleToTotalPixels", [-560, 5600], [280, 170], [{"localized_name": "image", "name": "image", "type": "IMAGE", "link": None},
                     widget_in("upscale_method", "COMBO"), widget_in("megapixels", "FLOAT"), widget_in("resolution_steps", "INT")], [out("IMAGE", "IMAGE")],
                     [MATCH["method"], MATCH["megapixels"], MATCH["step"]])
    size = add_node(wf, "GetImageSize", [-560, 5830], [230, 100], [{"localized_name": "image", "name": "image", "type": "IMAGE", "link": None}],
                    [out("width", "INT"), out("height", "INT"), out("batch_size", "INT")], [])
    size.pop("widgets_values")
    connect(wf, load, 0, scale, "image", "IMAGE")
    connect(wf, scale, 0, size, "image", "IMAGE")
    connect(wf, scale, 0, o, "first_frame", "IMAGE")
    connect(wf, size, 0, o, "width", "INT")
    connect(wf, size, 1, o, "height", "INT")
    place(wf, [load, scale, size, o, node(wf, "SaveVideo")])
    return wf


def check_links(wf):
    """Problems with a workflow's top-level links: both ends must agree, slot types must match, the id counters must cover every id. Empty list = consistent."""
    bad, nodes = [], {n["id"]: n for n in wf["nodes"]}
    seen = set()
    for lid, a, aslot, b, bslot, kind in wf["links"]:
        if lid in seen:
            bad.append(f"link {lid} listed twice")
        seen.add(lid)
        if a not in nodes or b not in nodes:
            bad.append(f"link {lid} joins a missing node")
            continue
        outs, ins = nodes[a].get("outputs", []), nodes[b].get("inputs", [])
        if aslot >= len(outs) or lid not in (outs[aslot].get("links") or []):
            bad.append(f"link {lid} is not on node {a} output {aslot}")
        elif outs[aslot].get("type") != kind:
            bad.append(f"link {lid} is {kind} but node {a} output {aslot} is {outs[aslot].get('type')}")
        if bslot >= len(ins) or ins[bslot].get("link") != lid:
            bad.append(f"link {lid} is not on node {b} input {bslot}")
        elif ins[bslot].get("type") != kind:
            bad.append(f"link {lid} is {kind} but node {b} input {bslot} is {ins[bslot].get('type')}")
    for n in wf["nodes"]:
        for o in n.get("outputs", []):
            bad += [f"node {n['id']} output lists link {l} that does not exist" for l in o.get("links") or [] if l not in seen]
        for i in n.get("inputs", []):
            if i.get("link") is not None and i["link"] not in seen:
                bad.append(f"node {n['id']} input {i['name']} points at link {i['link']} that does not exist")
    if wf["nodes"] and max(nodes) > wf["last_node_id"]:
        bad.append("last_node_id is behind the highest node id")
    if seen and max(seen) > wf["last_link_id"]:
        bad.append("last_link_id is behind the highest link id")
    return bad


def main():
    legacy = read(LEGACY)
    for key, build in (("reel", build_reel), ("match", build_match)):
        wf = build(legacy)
        problems = check_links(wf)
        if problems:
            sys.exit(f"{NAMES[key]}: " + "; ".join(problems))
        wf["id"] = f"st6-minimax-{key}"
        (OUT / NAMES[key]).write_text(json.dumps(wf, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote workflows/_templates/{NAMES[key]}")


if __name__ == "__main__":
    main()
