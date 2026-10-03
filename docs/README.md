# Documentation

How this repository works, end to end.

The repo contains one static site (**Git Guild**), the logo artwork it is built
from, and the Python scripts that turn that artwork into the site. There is no
package manager, no framework and no server: the deployable output is a single
HTML file.

| Doc | Covers |
|---|---|
| [design/README.md](design/README.md) | Artwork → vector geometry (`design/`, `tools/logo/`) |
| [build/README.md](build/README.md) | Sources → `index.html` (`gitguild/`, `tools/build/`) |
| [qa/README.md](qa/README.md) | Browser checks and screenshots (`tools/qa/`) |

## The pipeline

```
design/logo-source.jpeg                    the original bitmap artwork
        │  tools/logo/extract_logo.py
        ▼
design/logo-geometry.json                  raw skeleton: nodes + traced paths
        │  tools/logo/cleanup_geometry.py
        ▼
design/logo-final.json                     cleaned vector: paths, nodes, viewBox
        │  tools/build/build_geometry.py
        ▼
gitguild/src/emblem-geometry.js            window.GUILD_GRID (generated)
        │  tools/build/build_site.py  ◄── also reads gitguild/src/* (hand-written)
        ▼
gitguild/index.html + gitguild/assets/*.svg    the deployable site
        │  tools/qa/qa_assert.py, tools/qa/qa_shots.py
        ▼
PASS/FAIL on 22 checks, screenshots in build/qa/
```

Only the first three steps are ever re-run, and only when the artwork changes.
Everyday edits are to `gitguild/src/projects.js` followed by
`python3 tools/build/build_site.py`.

## Repository layout

```
design/                 logo artwork + geometry (source of truth for the mark)
gitguild/               the site: hand-written sources and the built output
  src/                  editable sources — index.html is generated from these
  index.html            built, self-contained, committed on purpose
  assets/               generated standalone SVGs
tools/build/            assembles the site
tools/logo/             traces and verifies the artwork
tools/qa/               browser assertions and screenshots
build/                  scratch output of the tools (gitignored)
docs/                   this documentation
```

## Conventions

* Every script computes the repo root from its own path, so
  `python3 tools/build/build_site.py` works from any directory.
* Generated files are written with LF line endings so a Windows build matches a
  Unix build byte for byte.
* Comments in source files are one or two short lines at most; the long
  explanation lives here in `docs/`.

## Everyday commands

```bash
python3 tools/build/build_site.py     # after editing anything in gitguild/src/
python3 tools/qa/qa_assert.py         # before committing
python3 tools/qa/qa_shots.py          # visual check -> build/qa/*.png
```
