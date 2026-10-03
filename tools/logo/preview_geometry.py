"""Render the extracted geometry to SVG/PNG and build a side-by-side diff vs the original."""
import json, sys, io, os
import numpy as np
from PIL import Image
import cairosvg

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "build")
os.makedirs(OUT, exist_ok=True)
w = lambda n: open(os.path.join(OUT, n), "w", encoding="utf-8", newline="\n")

G = json.load(open(os.path.join(ROOT, "design", "logo-geometry.json")))
BG, WHITE, ORANGE = "#101519", "#EBE8DB", "#F4A330"
W, H = 1408, 768


def build_svg(scale=1.0, bg=True):
    s = G["stroke"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*scale}" height="{H*scale}" '
             f'viewBox="0 0 {W} {H}">']
    if bg:
        parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    for col in ("white", "orange"):
        c = WHITE if col == "white" else ORANGE
        parts.append(f'<g stroke="{c}" stroke-width="{s}" fill="none" '
                     f'stroke-linecap="round" stroke-linejoin="round">')
        for p in G["paths"]:
            if p["color"] == col:
                parts.append(f'<path d="{p["d"]}"/>')
        parts.append("</g>")
    for n in G["nodes"]:
        c = WHITE if n["color"] == "white" else ORANGE
        parts.append(f'<circle cx="{n["x"]}" cy="{n["y"]}" r="{(G["r_in"]+G["r_out"])/2}" '
                     f'fill="none" stroke="{c}" stroke-width="{G["r_out"]-G["r_in"]}"/>')
        parts.append(f'<circle cx="{n["x"]}" cy="{n["y"]}" r="{G["r_out"]}" fill="none" stroke="#000" stroke-opacity="0" />')
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    w("build-preview.svg").write(svg)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H)
    mine = Image.open(io.BytesIO(png)).convert("RGB")
    orig = Image.open(os.path.join(ROOT, "design", "logo-source.jpeg")).convert("RGB")
    combo = Image.new("RGB", (W, H * 2 + 12), (40, 40, 40))
    combo.paste(orig, (0, 0))
    combo.paste(mine, (0, H + 12))
    combo.save(os.path.join(OUT, "compare.png"))
    # difference metric on the emblem area
    a = np.asarray(orig.crop((500, 100, 910, 540)).convert("L"), float)
    b = np.asarray(mine.crop((500, 100, 910, 540)).convert("L"), float)
    print(f"mean abs diff: {round(np.abs(a - b).mean(), 2)}")
    print("wrote build/build-preview.svg + build/compare.png")
