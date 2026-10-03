"""Render design/logo-final.json to preview SVG/PNG and compare with the original bitmap."""
import json, io, sys, os
import numpy as np, cairosvg
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "build")
os.makedirs(OUT, exist_ok=True)
path = lambda n: os.path.join(OUT, n)
write = lambda n, s: open(path(n), "w", encoding="utf-8", newline="\n").write(s)

G = json.load(open(os.path.join(ROOT, "design", "logo-final.json")))
BG, WHITE, ORANGE = "#101519", "#EBE8DB", "#F4A330"
V = G["view"]


def svg(bg=True, debug_ids=False, scale=1.0, frame=None):
    vb = frame or V
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{vb[2]*scale:.0f}" height="{vb[3]*scale:.0f}" '
             f'viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}">']
    if bg:
        parts.append(f'<rect x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" fill="{BG}"/>')
    if debug_ids:
        import colorsys
        cols = [f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                for h in np.linspace(0, 1, len(G['paths']), endpoint=False)
                for r, g, b in [colorsys.hsv_to_rgb(h, .85, 1)]]
        for i, p in enumerate(G["paths"]):
            parts.append(f'<path d="{p["d"]}" stroke="{cols[i]}" stroke-width="{G["stroke"]}" fill="none" stroke-linecap="round"/>')
            x, y = p["pts"][0]
            parts.append(f'<text x="{x}" y="{y}" font-size="13" fill="#fff">{i}</text>')
    else:
        for col in ("white", "orange"):
            c = WHITE if col == "white" else ORANGE
            parts.append(f'<g stroke="{c}" stroke-width="{G["stroke"]}" fill="none" stroke-linecap="round" stroke-linejoin="round">')
            for p in G["paths"]:
                if p["color"] == col:
                    parts.append(f'<path d="{p["d"]}"/>')
            parts.append("</g>")
    for n in G["nodes"]:
        c = WHITE if n["color"] == "white" else ORANGE
        r = (G["r_in"] + G["r_out"]) / 2
        parts.append(f'<circle cx="{n["x"]}" cy="{n["y"]}" r="{r}" fill="none" stroke="{c}" stroke-width="{G["r_out"]-G["r_in"]}"/>')
        if debug_ids:
            parts.append(f'<text x="{n["x"]+16}" y="{n["y"]-14}" font-size="15" fill="#6cf">{n["id"]}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    dbg = "--debug" in sys.argv
    orig = Image.open(os.path.join(ROOT, "design", "logo-source.jpeg")).convert("RGB")
    if dbg:
        s = svg(debug_ids=True)
        write("build-preview.svg", s)
        cairosvg.svg2png(bytestring=s.encode(), write_to=path("final_debug.png"),
                         output_width=1408, output_height=1408)
        print("wrote build/final_debug.png")
    else:
        s = svg()
        write("build-preview.svg", s)
        W = 1408
        cairosvg.svg2png(bytestring=s.encode(), write_to=path("mine_hd.png"), output_width=W, output_height=W)
        mine = Image.open(path("mine_hd.png")).convert("RGB")
        # pixel-exact frame: render the emblem in the ORIGINAL coordinate system too
        s2 = svg(frame=[0, 0, 1408, 768])
        cairosvg.svg2png(bytestring=s2.encode(), write_to=path("mine_frame.png"), output_width=1408, output_height=768)
        mf = Image.open(path("mine_frame.png")).convert("RGB")
        box = (500, 95, 910, 545)
        a = orig.crop(box); b = mf.crop(box)
        w, h = a.size
        combo = Image.new("RGB", (w * 2 + 10, h), (70, 70, 70))
        combo.paste(a, (0, 0)); combo.paste(b, (w + 10, 0))
        combo.resize((int(combo.width * 1.5), int(combo.height * 1.5)), Image.LANCZOS).save(path("compare.png"))
        na = np.asarray(a.convert("L"), float); nb = np.asarray(b.convert("L"), float)
        print("emblem mean abs diff:", round(np.abs(na - nb).mean(), 2))
        # overlay diff
        rgb = np.zeros((h, w, 3), np.uint8)
        rgb[..., 0] = na.astype(np.uint8); rgb[..., 1] = nb.astype(np.uint8)
        Image.fromarray(rgb).save(path("diff_overlay.png"))
        # aspect-correct resize for on-screen compare of the tight view
        mine.resize((1080, 1080), Image.LANCZOS).save(path("compare_small.png"))
        print("wrote build/{compare,diff_overlay,compare_small}.png")
