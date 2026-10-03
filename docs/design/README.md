# Design — how the mark becomes vectors

Everything under `design/` describes the Git Guild emblem as data. The site never
loads the JPEG: the bitmap is traced once into paths, and the site renders those
paths as SVG.

## Files

| File | What it is |
|---|---|
| `design/logo-source.jpeg` | The supplied artwork (1408×768), traced from |
| `design/logo-geometry.json` | Raw extraction: 12 rings + traced paths in pixel coordinates |
| `design/logo-final.json` | Cleaned vector: path `d` strings, node list, viewBox, stroke widths |

`logo-geometry.json` and `logo-final.json` are intermediates, but they are
committed because they are the design source of the mark — regenerating them
requires the CV toolchain below.

## Scripts (`tools/logo/`)

Run from the repo root; all paths are resolved from the script location.

### 1. `extract_logo.py` — bitmap → skeleton

Reads `logo-source.jpeg`, splits it into white/orange pixels, restricts itself to
the emblem region (the wordmark is a different asset), skeletons the mask at 3×
supersampling, splits the skeleton into simple paths, prunes spurs, merges
segments that continue straight through a junction, then simplifies each path
(`approxPolyDP`) and converts it to cubic Béziers.

Output: `design/logo-geometry.json`.

Dependencies: `numpy`, `opencv-python`, `scikit-image`.

Node positions, ring radii and stroke width are constants at the top of the
script — they were measured off the artwork, not detected.

### 2. `cleanup_geometry.py` — raw → final

Four passes over `logo-geometry.json`:

1. **Snap** — pull path ends onto the ring band centre line so no stroke pokes
   outside a ring.
2. **Drop** — discard junk fragments (tiny slivers, ring artefacts).
3. **Weld** — join paths that continue straight through a junction.
4. **Simplify + emit** — rebuild the `d` strings, attach `a_node`/`b_node` to each
   path, compute a tidy 470×470 viewBox, write `design/logo-final.json`.

Dependency: `numpy`.

### 3. `preview_geometry.py` / `render.py` — visual diff

Both rasterise the vector mark and compare it against `logo-source.jpeg`;
`render.py --debug` colours each path individually for tracing work. Outputs go
to `build/` (gitignored): `build-preview.svg`, `compare.png`, `diff_overlay.png`,
`mine_hd.png`, `mine_frame.png`.

Dependencies: `numpy`, `Pillow`, `cairosvg`.

## Schema of `logo-final.json`

```jsonc
{
  "view":  [x, y, w, h],        // viewBox
  "stroke": 9.6,                 // stroke width
  "r_in": 11.0, "r_out": 20.5,   // ring band
  "nodes": [{ "id": "n0", "x": 703.5, "y": 137.0,
              "color": "white", "paths": [0, 3] }],
  "paths": [{ "color": "white", "d": "M…C…", "len": 142.3,
              "pts": [[x, y], …], "a_node": "n0", "b_node": "n7" }]
}
```

Node ids `n0 … n11` are ordered top-down/clockwise and are referenced everywhere
else (`projects.js` keys, `order`, `mergeTrain`), so they must not be renamed.

## Re-tracing (rare)

Only needed if the artwork itself changes:

```bash
python3 tools/logo/extract_logo.py
python3 tools/logo/cleanup_geometry.py
python3 tools/build/build_geometry.py     # regenerate gitguild/src/emblem-geometry.js
python3 tools/build/build_site.py         # rebuild the site
```
