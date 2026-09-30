import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

f = "workflows/Drakness/Drakness_Qwen_Armor_Bikini.json"
with open(f, "rb") as fh:
    d = json.loads(fh.read().decode("utf-8-sig"))

found = []
def walk(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, path + "/" + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + f"[{i}]")
    elif isinstance(node, str):
        if len(node) > 60 and "http" not in node and "Subgraph" not in node:
            found.append((path, node))

walk(d, "")
for path, s in found:
    print("=" * 70)
    print(s)
