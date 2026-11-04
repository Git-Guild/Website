# Build pipeline

The Python build embeds a checked-in GitHub repository snapshot in a
self-contained static homepage and generates one detail page per repository.
The published site makes no network requests.

## Inputs

| Source | Purpose |
|---|---|
| `gitguild/src/template.html` | Homepage shell and content slots |
| `gitguild/src/project-template.html` | Generated repository detail page shell |
| `gitguild/src/styles.css` | Shared styles, inlined in every page |
| `gitguild/src/theme.js` | System-aware theme bootstrap, toggle, persistence, optional click sound |
| `gitguild/src/project-curation.json` | Collective copy, preferred order, editorial overrides |
| `data/github-projects.json` | Committed public repository snapshot |
| `gitguild/src/emblem-geometry.js` | Generated emblem geometry and trace adjacency |
| `gitguild/src/app.js` | React rendering and interactions |

The build combines the snapshot and curation into `window.GUILD`. The first 12
repositories in the resulting order bind to the 12 fixed emblem rings; remaining
repositories stay available in the project index and detail pages.

## Refreshing repository data

```bash
python3 tools/sync/sync_github_projects.py
python3 tools/build/build_site.py
```

The sync command reads GitHub's public organization repository endpoint and
keeps public repositories that are not forks or archived. It writes atomically
only after all pages are fetched and validated. If sync fails, the previous
snapshot remains intact. Routine builds consume the local snapshot and work
offline.

To edit presentation order or add concise editorial copy, update
`gitguild/src/project-curation.json`. Repositories not listed there are
appended by most recent update date. GitHub descriptions remain the default
project description.

## Build outputs

```bash
python3 tools/build/build_site.py
```

This writes `gitguild/index.html`, generates `gitguild/projects/*.html`, and
removes stale generated project pages. Edit sources rather than generated HTML.

The runtime remains a single offline homepage with inlined React, CSS, project
metadata, and emblem geometry. Project pages are static HTML using the same
inlined style system.
