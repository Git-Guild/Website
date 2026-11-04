# How the Git Guild website is built

The site is a self-contained static website assembled with Python. Its logo is
also the project browser: selecting a ring highlights the connected wiring and
updates the project spotlight. Visitors can open a static detail page for each
repository.

## Where project data comes from

`data/github-projects.json` is the committed snapshot of Git Guild's public,
non-fork, non-archived repositories. It stores repository names, GitHub URLs,
descriptions, programming languages, topics, and GitHub update times. Refresh
it explicitly with:

```bash
python3 tools/sync/sync_github_projects.py
```

The sync script follows GitHub pagination and only replaces the saved snapshot
after it receives and validates the complete result. If a request fails, the
previous snapshot stays in place. The static site never makes GitHub requests.

Maintainers control the homepage wording, display names, project summaries,
and ordering in `gitguild/src/project-curation.json`. Uncurated repositories
are appended by last update time. The first twelve ordered repositories bind
to the emblem's twelve fixed rings; later projects remain in the browser and
have detail pages without rings.

## Build and inspect

```bash
python3 tools/build/build_site.py
python3 -m unittest tools/qa/test_project_catalog.py
python3 tools/qa/qa_assert.py
python3 tools/qa/qa_shots.py
```

The build works offline from the checked-in snapshot. It writes the homepage
to `gitguild/index.html` and static repository pages to `gitguild/projects/`.
Edit source files in `gitguild/src/`; generated HTML should be rebuilt rather
than edited by hand.

## Main source files

- `gitguild/src/template.html` — homepage structure and copy slots.
- `gitguild/src/styles.css` — responsive dark and amber design system.
- `gitguild/src/app.js` — inlined React project browser and interactions.
- `gitguild/src/emblem-geometry.js` — the emblem's rings, traces, and links.
- `gitguild/src/project-template.html` — generated project page shell.
- `gitguild/src/project-curation.json` — ordering and maintainer copy.
- `tools/build/project_catalog.py` — combines snapshot and curation.
- `tools/build/build_site.py` — produces the offline static pages.
- `tools/sync/sync_github_projects.py` — refreshes repository metadata.
