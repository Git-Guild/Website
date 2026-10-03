"""Clean up extracted geometry: snap stroke ends under node rings, weld collinear
joins, drop junk fragments. Writes design/logo-final.json."""
import json, math, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
G = json.load(open(os.path.join(ROOT, "design", "logo-geometry.json")))
NODES = G["nodes"]
R_OUT, R_IN, STROKE = G["r_out"], G["r_in"], G["stroke"]
SNAP_R = R_OUT - 1.9          # end caps must stop inside the ring band (hidden by the ring)
HW = STROKE / 2


# path utils
def to_pts(d):
    """Parse the M/L/C 'd' string back into a dense polyline + control info."""
    toks = d.replace("M", " M ").replace("L", " L ").replace("C", " C ").split()
    pts, ctrl, i = [], [], 0
    while i < len(toks):
        t = toks[i]
        if t == "M":
            x, y = map(float, toks[i + 1].split(","))
            pts.append((x, y)); i += 2
        elif t == "L":
            x, y = map(float, toks[i + 1].split(","))
            pts.append((x, y)); ctrl.append(None); i += 2
        elif t == "C":
            c1 = tuple(map(float, toks[i + 1].split(",")))
            c2 = tuple(map(float, toks[i + 2].split(",")))
            p = tuple(map(float, toks[i + 3].split(",")))
            pts.append(p); ctrl.append((c1, c2)); i += 4
        else:
            i += 1
    return pts, ctrl


def to_bezier(pts):
    if len(pts) < 2:
        return ""
    if len(pts) == 2:
        return f"M{pts[0][0]:.1f},{pts[0][1]:.1f}L{pts[1][0]:.1f},{pts[1][1]:.1f}"
    p = [pts[0]] + list(pts) + [pts[-1]]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def nearest_node(pt):
    best, bd = None, 1e9
    for n in NODES:
        d = math.dist(pt, (n["x"], n["y"]))
        if d < bd:
            best, bd = n, d
    return best, bd


paths = []
for p in G["paths"]:
    pts, _ = to_pts(p["d"])
    if len(pts) < 2:
        continue
    paths.append({"color": p["color"], "pts": pts})


# 1. snap ends under rings
def snap(pts):
    for which in (0, -1):
        e = pts[which]
        n, d = nearest_node(e)
        if d < 34 and d > 0.5:
            # place the endpoint exactly on the ring band centre line, keeping direction
            new = (n["x"] + (e[0] - n["x"]) / d * SNAP_R,
                   n["y"] + (e[1] - n["y"]) / d * SNAP_R)
            if which == 0:
                pts[0] = new
            else:
                pts[-1] = new
    return pts


for p in paths:
    p["pts"] = snap(p["pts"])


# 2. drop junk fragments
def clean_fragments(ps):
    out = []
    for p in ps:
        a, b = p["pts"][0], p["pts"][-1]
        ln = sum(math.dist(p["pts"][i], p["pts"][i + 1]) for i in range(len(p["pts"]) - 1))
        na, da = nearest_node(a)
        nb, db = nearest_node(b)
        same = na is nb and da < SNAP_R + 6 and db < SNAP_R + 6
        if ln < 26 and same and len(p["pts"]) <= 3:
            # a short bridge between two points on the same ring: keep only if it
            # is a clean radial stub (arcs like this are ring artefacts)
            ax, ay = a
            mx = (a[0] + b[0]) / 2 - na["x"], (a[1] + b[1]) / 2 - na["y"]
            if math.hypot(*mx) < SNAP_R - 2:
                continue
        out.append(p)
    return out


paths = clean_fragments(paths)

# hairline artefacts (tiny slivers next to a junction in the source art)
paths = [p for p in paths if not (
    p["color"] == "orange" and
    sum(math.dist(p["pts"][i], p["pts"][i + 1]) for i in range(len(p["pts"]) - 1)) < 30 and
    p["pts"][0][0] > 820 and p["pts"][0][1] < 320)]


# 3. weld paths that continue straight
def tangent(pts, at_start, k=3):
    k = min(len(pts) - 1, k)
    a, b = (pts[0], pts[k]) if at_start else (pts[-1], pts[-1 - k])
    v = np.array([b[0] - a[0], b[1] - a[1]], float)
    n = np.linalg.norm(v)
    return v / n if n else v


def weld(ps, tol=3.0, dot=-0.55):
    changed = True
    while changed:
        changed = False
        for i in range(len(ps)):
            for j in range(len(ps)):
                if i == j or ps[i]["color"] != ps[j]["color"]:
                    continue
                pi, pj = ps[i]["pts"], ps[j]["pts"]
                pairs = [((0, -1), pi[0], pj[-1]), ((-1, 0), pi[-1], pj[0]),
                         ((0, 0), pi[0], pj[0]), ((-1, -1), pi[-1], pj[-1])]
                hit = None
                for (wi, wj), ea, eb in pairs:
                    if math.dist(ea, eb) > tol:
                        continue
                    ta = tangent(pi, wi == 0)
                    tb = tangent(pj, wj == 0)
                    if float(np.dot(ta, tb)) < dot:      # roughly opposite -> smooth join
                        hit = (wi, wj)
                        break
                if not hit:
                    continue
                wi, wj = hit
                a = list(pi) if wi == -1 else list(reversed(pi))
                b = list(pj) if wj == 0 else list(reversed(pj))
                if wi == -1:
                    a = list(pi) if wi == 0 else list(reversed(pi))
                    # ensure a ends where b starts
                    if math.dist(a[-1], b[0]) > tol:
                        b = list(reversed(b))
                merged = a + b[1:]
                if len(merged) > 40:
                    merged = merged[:1] + merged[1:-1:1] + merged[-1:]
                ps[i] = {"color": ps[i]["color"], "pts": merged}
                ps.pop(j)
                changed = True
                break
            if changed:
                break
    return ps


paths = weld(paths)


# 4. simplify + emit + meta
def rdp(pts, eps=0.7):
    arr = np.array(pts, np.float32).reshape(-1, 1, 2)
    import cv2
    ap = cv2.approxPolyDP(arr, eps, False)
    return [tuple(map(float, q[0])) for q in ap]


final = []
for p in paths:
    pts = rdp(p["pts"])
    a, b = pts[0], pts[-1]
    na, da = nearest_node(a)
    nb, db = nearest_node(b)
    final.append({
        "color": p["color"],
        "d": to_bezier(pts),
        "pts": [[round(x, 1), round(y, 1)] for x, y in pts],
        "len": round(sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)), 1),
        "a_node": na["id"] if da < 40 else None,
        "b_node": nb["id"] if db < 40 else None,
    })

# node -> path index map (for hover / highlight)
for n in NODES:
    n["paths"] = [i for i, p in enumerate(final)
                  if p["a_node"] == n["id"] or p["b_node"] == n["id"]]

# normalise into a tidy 470x470 viewBox centred on the emblem
cx = sum(n["x"] for n in NODES) / len(NODES)
xs = [n["x"] for n in NODES]
cy = (min(n["y"] for n in NODES) + max(n["y"] for n in NODES)) / 2
cx = (min(xs) + max(xs)) / 2
cy = (137 + 502.5) / 2
HALF = 238.0
out = {"view": [round(cx - HALF, 1), round(cy - HALF, 1), 2 * HALF, 2 * HALF],
       "nodes": NODES, "paths": final, "stroke": STROKE, "r_out": R_OUT, "r_in": R_IN}
json.dump(out, open(os.path.join(ROOT, "design", "logo-final.json"), "w",
                    encoding="utf-8", newline="\n"), indent=1)
print(f"final: {len(NODES)} nodes, {len(final)} paths")
for p in sorted(final, key=lambda q: -q["len"])[:40]:
    print(f"  {p['color']:6s} {p['len']:7.1f} {p['a_node']} -> {p['b_node']}")
orphan = [i for i, p in enumerate(final) if not p["a_node"] and not p["b_node"] and p["len"] > 40]
print("long orphan paths:", orphan)
