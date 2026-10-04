#!/usr/bin/env python3
"""Regenerates gitguild/src/emblem-geometry.js from design/logo-final.json."""
import os, json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FINAL_JSON = os.path.join(ROOT, "design", "logo-final.json")
OUTPUT_JS = os.path.join(ROOT, "gitguild", "src", "emblem-geometry.js")

def main():
    if not os.path.exists(FINAL_JSON):
        raise FileNotFoundError(f"Missing source file: {FINAL_JSON}")

    with open(FINAL_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    view = data.get("view", [465.5, 81.8, 476.0, 476.0])
    stroke = data.get("stroke", 9.6)
    r_out = data.get("rOut", 20.5)
    r_in = data.get("rIn", 11.0)

    nodes = []
    for n in data.get("nodes", []):
        color = "w" if n.get("color") == "white" else ("o" if n.get("color") in ["orange", "amber"] else n.get("color", "w"))
        nodes.append({
            "id": n["id"],
            "x": round(n["x"], 1),
            "y": round(n["y"], 1),
            "c": color
        })

    traces = []
    for idx, t in enumerate(data.get("paths", [])):
        color = "w" if t.get("color") == "white" else ("o" if t.get("color") in ["orange", "amber"] else t.get("color", "w"))
        traces.append({
            "i": t.get("id", idx),
            "c": color,
            "d": t["d"],
            "a": t.get("a_node", t.get("touches", [None, None])[0] if "touches" in t else None),
            "b": t.get("b_node", t.get("touches", [None, None])[1] if "touches" in t else None),
            "l": round(t.get("len", t.get("length", 0.0)), 1)
        })

    adjacency = {}
    for n in nodes:
        nid = n["id"]
        adj = []
        for t in traces:
            if t["a"] == nid:
                adj.append([t["i"], "a"])
            elif t["b"] == nid:
                adj.append([t["i"], "b"])
        adjacency[nid] = adj

    grid = {
        "view": view,
        "stroke": stroke,
        "rOut": r_out,
        "rIn": r_in,
        "nodes": nodes,
        "traces": traces,
        "adjacency": adjacency
    }

    content = f"""/* GENERATED — source: design/logo-final.json, regenerate with tools/build/build_geometry.py */
window.GUILD_GRID = {json.dumps(grid, separators=(',', ': '))};
"""
    with open(OUTPUT_JS, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    print(f"Successfully generated {OUTPUT_JS}")

if __name__ == "__main__":
    main()
