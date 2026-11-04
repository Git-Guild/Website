# ADR 0003: Front-end redesign

Date: 2026-11-04
Status: accepted and implemented

## Decision

Keep the self-contained Python-built static site and inlined React runtime.
The existing 12-ring emblem remains the signature project browser, connected
to a mobile carousel and desktop spotlight/index. Selecting a ring syncs its
wiring, project, and spotlight; opening details is a separate action. The
dark and amber identity, keyboard operation, responsive layout, and reduced
motion support remain in place.

Use the checked-in GitHub repository snapshot as project metadata and
maintainer curation for names, summaries, and order. Use GitHub's update time
as factual metadata, not as a maintenance guarantee. Keep routine builds
offline, without introducing a framework migration or external runtime
requests.

The organization homepage serves students seeking a place to learn, build,
collaborate, and contribute. The main call to action points to open issues;
the project browser is the secondary action. Do not promise an unconfigured
chat or invent repository activity.

## Consequences

- `tools/sync/sync_github_projects.py` refreshes repository metadata explicitly.
- `gitguild/src/project-curation.json` controls order and editorial copy.
- The first 12 ordered repositories occupy the fixed rings; overflow remains
  accessible in the project browser and generated detail pages.
- Build and browser checks must work from the checked-in snapshot without
  contacting GitHub.
