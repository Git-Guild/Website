"""Extract vector geometry (centerline strokes) from the Git Guild logo bitmap.
Output: design/logo-geometry.json (coordinates in original 1408x768 pixel space)."""
import json, math, os
import numpy as np
import cv2
from skimage.morphology import skeletonize

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "design", "logo-source.jpeg")
OUT = os.path.join(ROOT, "design", "logo-geometry.json")
UP = 3                      # supersample factor for a smoother skeleton

NODES = [
    (703.5, 137.0, "white"), (703.5, 191.1, "white"),
    (538.0, 227.6, "orange"), (869.1, 227.5, "orange"),
    (640.6, 259.1, "white"), (766.6, 259.1, "orange"),
    (538.1, 319.3, "orange"), (597.0, 319.3, "orange"), (869.1, 319.4, "orange"),
    (537.9, 411.7, "orange"), (869.1, 411.9, "orange"),
    (703.4, 502.5, "white"),
]
R_OUT, R_IN, STROKE = 20.5, 11.0, 9.6

im = cv2.medianBlur(cv2.imread(SRC), 3)
b, g, r = cv2.split(im.astype(np.int16))
bright = (r + g + b) / 3.0 > 70
# restrict to the emblem only (the wordmark below is a different asset)
region = np.zeros_like(bright)
region[104:534, 505:905] = True
bright &= region
orange = bright & ((r - b) > 55)
white = bright & ((r - b) <= 55)

H, W = bright.shape
yy, xx = np.mgrid[0:H, 0:W]
excl = np.zeros((H, W), bool)
for x, y, _ in NODES:
    excl |= (xx - x) ** 2 + (yy - y) ** 2 <= (R_OUT + 3) ** 2


def to_graph(sk):
    pts = set(zip(*np.nonzero(sk)))
    nbrs = {p: [q for q in ((p[0] + dy, p[1] + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                            if (dy, dx) != (0, 0)) if q in pts] for p in pts}
    return pts, nbrs


def segments(pts, nbrs):
    """Split the skeleton graph into simple paths between nodes of degree != 2."""
    junctions = {p for p in pts if len(nbrs[p]) != 2}
    if not junctions:
        junctions = {next(iter(pts))}
    seen, segs = set(), []
    for j in junctions:
        for nxt in nbrs[j]:
            if (j, nxt) in seen:
                continue
            path, prev, cur = [j, nxt], j, nxt
            seen.add((j, nxt))
            while cur not in junctions:
                fwd = [q for q in nbrs[cur] if q != prev]
                if len(fwd) != 1:
                    break
                prev, cur = cur, fwd[0]
                path.append(cur)
            seen.add((path[-1], path[-2]))
            segs.append(path)
    return segs


def seg_len(p):
    return sum(math.dist(p[i], p[i + 1]) for i in range(len(p) - 1))


def near_node(pt, mult):
    return min(math.dist((pt[1], pt[0]), (n[0], n[1])) for n in NODES) < (R_OUT + 6) * mult


def extract(mask, colour):
    ob = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    big = cv2.resize((ob * 255).astype(np.uint8), None, fx=UP, fy=UP, interpolation=cv2.INTER_LINEAR)
    big = (big > 110)
    # carve rings (supersampled)
    Hh, Ww = big.shape
    yy2, xx2 = np.mgrid[0:Hh, 0:Ww]
    ex2 = np.zeros((Hh, Ww), bool)
    for x, y, _ in NODES:
        ex2 |= (xx2 - x * UP) ** 2 + (yy2 - y * UP) ** 2 <= ((R_OUT + 3) * UP) ** 2
    big &= ~ex2
    sk = skeletonize(big)

    for _ in range(6):                      # prune spurs
        pts, nbrs = to_graph(sk)
        segs = segments(pts, nbrs)
        drop = set()
        for s in segs:
            if len(s) < 2:
                continue
            free_end = len(nbrs[s[0]]) == 1 or len(nbrs[s[-1]]) == 1
            if free_end and seg_len(s) < 15 * UP and not (near_node(s[0], UP) or near_node(s[-1], UP)):
                drop.update(s[:-1])
        if not drop:
            break
        sk = sk.copy()
        for p in drop:
            sk[p] = False

    pts, nbrs = to_graph(sk)
    segs = [s for s in segments(pts, nbrs) if seg_len(s) > 4 * UP]

    # merge segments that continue straight through a junction
    def tangent(path, at_end):
        k = min(len(path) - 1, int(9 * UP))
        a, b0 = (path[0], path[k]) if at_end else (path[-1], path[-1 - k])
        v = np.array([b0[1] - a[1], b0[0] - a[0]], float)
        n = np.linalg.norm(v)
        return v / n if n else v

    def joinable(s1, s2):
        # s1 ends at s2 start?
        if math.dist(s1[-1], s2[0]) > 3.5 * UP:
            return None
        t1, t2 = tangent(s1, False), tangent(s2, True)
        if float(np.dot(t1, t2)) < -0.86:
            return s1 + s2[1:]
        return None

    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(segs):
            j = 0
            while j < len(segs):
                if i != j:
                    m = joinable(segs[i], segs[j]) or joinable(segs[j], segs[i])
                    if m:
                        segs[i] = m
                        segs.pop(j)
                        changed = True
                        continue
                j += 1
            i += 1

    out = []
    for s in segs:
        raw = [(p[1] / UP, p[0] / UP) for p in s]
        out.append((colour, raw, seg_len(raw)))
    return out


def simplify(pts):
    arr = np.array(pts, np.float32).reshape(-1, 1, 2)
    for eps in (2.6, 2.0, 1.5, 1.1, 0.8, 0.5):
        ap = cv2.approxPolyDP(arr, eps, False)
        if len(ap) >= 2 and len(ap) <= max(3, len(pts) // 3):
            return [tuple(map(float, q[0])) for q in ap]
    return [tuple(map(float, q[0])) for q in cv2.approxPolyDP(arr, 0.4, False)]


def to_bezier(pts, tension=1.0):
    if len(pts) < 2:
        return ""
    if len(pts) == 2:
        return f"M{pts[0][0]:.1f},{pts[0][1]:.1f}L{pts[1][0]:.1f},{pts[1][1]:.1f}"
    p = [pts[0]] + list(pts) + [pts[-1]]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0 * tension, p1[1] + (p2[1] - p0[1]) / 6.0 * tension)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0 * tension, p2[1] - (p3[1] - p1[1]) / 6.0 * tension)
        d += f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


nodes_meta = [{"id": f"n{i}", "x": x, "y": y, "color": c} for i, (x, y, c) in enumerate(NODES)]
paths = []
for colour, mask in (("white", white), ("orange", orange)):
    for col, raw, ln in extract(mask & ~excl, colour):
        pts = simplify(raw)
        d = to_bezier(pts)
        ends = []
        for e in (pts[0], pts[-1]):
            best, bd = None, 1e9
            for n in nodes_meta:
                dd = math.dist(e, (n["x"], n["y"]))
                if dd < bd:
                    best, bd = n, dd
            ends.append(best["id"] if bd < 34 else None)
        paths.append({"color": col, "d": d, "len": round(ln, 1), "ends": ends,
                      "a": [round(v, 1) for v in pts[0]], "b": [round(v, 1) for v in pts[-1]]})

json.dump({"nodes": nodes_meta, "paths": paths, "r_out": R_OUT, "r_in": R_IN,
           "stroke": STROKE}, open(OUT, "w", encoding="utf-8", newline="\n"), indent=1)
print(f"{len(nodes_meta)} nodes / {len(paths)} paths")
for p in sorted(paths, key=lambda q: -q["len"]):
    print(f"  {p['color']:6s} {p['len']:7.1f}  {p['ends'][0]} -> {p['ends'][1]}")
