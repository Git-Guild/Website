# Website

Main website for the org — a single self-contained page for the **Git Guild**
developer collective, plus the tooling that builds and verifies it.

Open [`gitguild/index.html`](gitguild/index.html) in a browser: no server, no
build step, no network requests.

## Repository layout

```
.
├── gitguild/            ← the site (deploy this folder)
│   ├── index.html       ← built, self-contained output — committed on purpose
│   ├── assets/          ← generated SVGs (emblem, lockup, favicon)
│   └── src/             ← editable sources index.html is built from
├── design/              ← logo artwork + vector geometry (source of truth)
│   ├── logo-source.jpeg ← the original artwork everything was traced from
│   ├── logo-geometry.json
│   └── logo-final.json
├── tools/
│   ├── build/           ← assemble the site and its geometry
│   ├── logo/            ← trace the artwork, verify fidelity
│   └── qa/              ← browser assertions + screenshots
├── docs/                ← how everything works (start with docs/README.md)
└── README.md
```

Every script resolves paths from the repository root, so they run from any
working directory.

## Commands

```bash
python3 tools/build/build_site.py        # rebuild gitguild/index.html + SVGs
python3 tools/build/build_geometry.py    # regenerate src/emblem-geometry.js
python3 tools/qa/qa_assert.py            # functional checks (needs playwright)
python3 tools/qa/qa_shots.py             # screenshots -> build/qa/
```

Full detail on editing projects, the emblem and accessibility lives in
[`gitguild/README.md`](gitguild/README.md).

## Documentation

* [`docs/README.md`](docs/README.md) — the pipeline, repo map and conventions
* [`docs/design/README.md`](docs/design/README.md) — artwork → vector geometry
* [`docs/build/README.md`](docs/build/README.md) — sources → `index.html`
* [`docs/qa/README.md`](docs/qa/README.md) — browser checks and screenshots

## Deploy

`gitguild/index.html` is already final — drag the `gitguild/` folder onto
Netlify, or point GitHub Pages / Vercel / Cloudflare Pages at it. Nothing
builds on the host.

## Generated files

| Path | Produced by | Committed? |
|---|---|---|
| `gitguild/index.html` | `tools/build/build_site.py` | yes (deployable artifact) |
| `gitguild/assets/*.svg` | `tools/build/build_site.py` | yes |
| `gitguild/src/emblem-geometry.js` | `tools/build/build_geometry.py` | yes |
| `design/logo-geometry.json` | `tools/logo/extract_logo.py` | yes |
| `design/logo-final.json` | `tools/logo/cleanup_geometry.py` | yes |
| `build/` | previews, diffs, QA screenshots | no (gitignored) |
