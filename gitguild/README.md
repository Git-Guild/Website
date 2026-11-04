# Git Guild website

The homepage is a self-contained static page with an interactive project
emblem. Its project data comes from GitGuild's public GitHub repositories, saved
as a committed snapshot so the deployed site works offline.

## Sources

- `src/project-curation.json` controls display order and editorial names or
  taglines.
- `../data/github-projects.json` contains repository metadata fetched from the
  GitHub organization.
- `src/emblem-geometry.js` contains generated 12-node geometry and wiring.
- `src/app.js`, `src/styles.css`, and `src/template.html` define the homepage.
- `src/project-template.html` defines generated repository detail pages.
- `index.html` and `projects/*.html` are generated outputs. Do not edit them
  directly.

## Update projects

```bash
python3 tools/sync/sync_github_projects.py
python3 tools/build/build_site.py
python3 tools/qa/qa_assert.py
```

The sync includes public organization repositories that are neither forks nor
archived. It handles pagination and keeps the previous snapshot if a fetch or
validation fails. The build reads only the local snapshot and does not use the
network.

Maintainers can reorder known repositories in `projectOrder` and add optional
`name`, `tagline`, `blurb`, or `featured` overrides in the curation JSON. New
repositories not listed there are appended by update date. The first 12
projects in the resulting order bind to the mark's fixed rings. Later projects
remain accessible in the browser and through generated detail pages.

The recent-updates band uses the six latest repository update dates. Dates are
GitHub metadata and do not imply that a repository is actively maintained.

## Build and QA

```bash
python3 tools/build/build_site.py
python3 tools/qa/qa_assert.py
python3 tools/qa/qa_shots.py
```

The site uses the bundled React UMD runtime. No package manager, CDN, remote
font, or browser data request is required.
