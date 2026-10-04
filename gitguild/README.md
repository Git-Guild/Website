# Git Guild — interactive emblem site

Deeper documentation for the build, the logo pipeline and QA lives in
[`../docs/README.md`](../docs/README.md).

A one-page site built around the supplied **Git Guild** mark. The emblem is rebuilt
as real vector geometry (12 node rings + 22 traces, traced from the original
artwork), and **every node is a live project** you can click.

```
gitguild/
├── index.html              ← the whole site, self-contained (open this)
├── assets/                 ← generated SVGs (emblem, lockup, favicon)
└── src/                    ← editable sources (index.html is built from these)
    ├── projects.js         ← ALL PROJECT DATA + copy lives here
    ├── emblem-geometry.js  ← generated: node positions + trace paths
    ├── template.html
    ├── styles.css
    └── app.js
```

The original artwork and the vector geometry traced from it live one level up
in `design/` (`logo-source.jpeg`, `logo-geometry.json`, `logo-final.json`).

Open `gitguild/index.html` in a browser — no server, no build step, no network
requests. Everything (styles, scripts, logo geometry, favicon) is inlined.

---

## 1. Edit the projects (this is the only file you normally touch)

`src/projects.js`

```js
projects: {
  n6: {
    name: 'Warden',
    tagline: 'Policy-as-code for CI and secrets',
    blurb: 'Shown in the side panel …',
    year: 2023, status: 'stable',       // stable | beta | experimental
    stack: ['Go', 'OPA', 'Terraform'],
    url: 'https://github.com/…',        // "Visit project" button
    repo: 'https://github.com/…',       // optional, null hides it
    docs: 'https://…',                  // optional, null hides it
    featured: true                      // optional flagship badge
  },
  …
}
```

* **Change a project** → edit its entry. The node, tooltip, card, panel and CLI
  list all update together, because they are all rendered from this object.
* **Keys** `n0 … n11` are the nodes of the mark, numbered top-down/clockwise
  (see the order array below them). Do not rename them — they are tied to the
  geometry.
* **Order** `order: [...]` sets tab order, the "01 / 12" numbering and the card
  grid order.
* **Merge train** `mergeTrain: [...]` lists the six projects shown in the commit
  graph band, oldest first.
* Collective-level copy (lede, quickstart command, GitHub/chat/mail links, the
  "est." year) sits in the `collective: {}` block at the top.

### Click behaviour

In `src/app.js` (or override in `projects.js`):

```js
nodeClick: 'page'    // default — spark, then navigate to projects/<slug>.html
nodeClick: 'panel'   // opens the quick-view panel instead of navigating
```

Clicking a node, card, or merge-train commit navigates to that project's
shareable page. Each card also has a `Quick view` button that opens the info
panel without leaving home; the panel links out to the full project page.

### Rebuild after editing

```bash
python3 tools/build/build_site.py     # regenerates gitguild/index.html
```

(Editing `index.html` directly also works — the `src/` files just keep it tidy
and re-buildable.)

---

## 2. How the emblem works

`src/emblem-geometry.js` holds the mark as data:

| field | meaning |
|---|---|
| `nodes` | 12 rings — `{id, x, y, c}` where `c` is the original white/amber |
| `traces` | 22 stroke paths (`d` = SVG path data), each tagged with the node(s) it touches |
| `adjacency` | node → the traces wired to it (drives the hover highlight) |
| `view`, `stroke`, `rIn`, `rOut` | viewBox and stroke geometry |

On load the traces draw themselves in, the rings settle into place, and a signal
pulse runs out of the hub node. Hovering or focusing a node (or its card, or its
commit in the merge train) dims everything else and lights that node's wiring;
clicking fires a pulse along those traces and opens the project panel.

**Regenerating the geometry** (only needed if you re-trace the artwork):

```bash
python3 tools/logo/extract_logo.py      # bitmap → skeleton → centerlines
python3 tools/logo/cleanup_geometry.py  # snap ends under rings, weld, simplify
python3 tools/build/build_geometry.py   # → gitguild/src/emblem-geometry.js
python3 tools/build/build_site.py
```

`tools/logo/render.py` renders the vector mark next to the original bitmap with a
red/green difference overlay, if you want to check fidelity. Previews and QA
screenshots land in `build/` (gitignored).

---

## 3. Deploy

The site is a single static file. Any of these work:

* **Netlify** — drag the `gitguild` folder onto app.netlify.com/drop.
* **GitHub Pages** — commit `gitguild/` and point Pages at that folder.
* **Vercel / Cloudflare Pages / S3** — upload `gitguild/` as the output dir.

No build step runs on the host; `index.html` is already final.

---

## 4. Accessibility & compatibility

* Every node, card and commit is a real focusable control with an aria-label;
  <kbd>Tab</kbd>/<kbd>←</kbd><kbd>→</kbd> move through the network,
  <kbd>Enter</kbd> opens, <kbd>Esc</kbd> closes, <kbd>←</kbd><kbd>→</kbd>
  step through projects while the panel is open.
* `prefers-reduced-motion: reduce` turns off the draw-in, the pulses and the
  orbit animation.
* Layout is tested at 390 px, 820 px, 1024 px, 1280 px and 1920 px; the emblem
  scales with its container and the cards reflow from 3 columns to 1.
* No external fonts, scripts, images or trackers — the page works offline and
  inside sandboxed frames.

---

## 5. Adding a 13th project

The mark has twelve slots (`order[:12]`; keep flagship/`featured` projects at
the front of `order`). A new project joins as a card-only entry: add it to
`projects` and append it to `order` (leave `mergeTrain` alone), then rebuild —
it gets a card plus a `projects/<slug>.html` page with a "card only" note and
no ring. If you want a real 13th node in the mark, trace the modified
artwork through the scripts in `tools/logo/` and `tools/build/` and add the node id to `order`.

```bash
python3 tools/build/build_site.py     # regenerates index.html + projects/ + legal/
python3 tools/qa/qa_assert.py         # extended browser checks over slots, pages, nav, keyboard, labels
```

Home renders through the inlined React UMD runtime (`tools/build/vendor-react*.js`,
no CDN at runtime); project and legal pages are static with a tiny chrome script.
