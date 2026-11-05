# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: students (freshers, juniors, seniors, anyone at a lower-tier college without good opportunities) who want a community, a team and collaborators to learn and grow with. Mobile and desktop are equally important; make no assumption about device quality. Do not frame the site around "lost time" or recovery.

Secondary: maintainers and contributors who keep the collective's projects and welcome newcomers.

## Product Purpose

Git Guild is an open-source community and developer collective (est. 2026). The homepage exists so a visiting student feels "people like me start today" and can explore real GitGuild repositories or find an open issue to contribute to. Success is a visitor opening a repository page, browsing the project browser, or opening the GitHub contribution search.

## Positioning

Community plus start-today: a welcoming collective for overlooked students where the network itself is the way in. A neighboring tutorial site or course catalog could not truthfully copy the claim that every member project is wired into one shared mark that the visitor can touch to begin.

## Operating Context

Self-contained static website that works with no server and makes no runtime network requests. Mobile and desktop are equally important. Core workflows: arrive, feel welcome, then browse repository projects via the slider or open the GitHub issue search. GitHub data is refreshed through an explicit Python sync command and stored in a committed snapshot.

## Capabilities and Constraints

- One page, one self-contained file; no network requests, no web fonts, no CDN, no images.
- Sources live in `gitguild/src/*`; `tools/build/build_site.py` assembles `gitguild/index.html` (never hand-edited); `tools/qa/qa_assert.py` runs after every change.
- The slider is the sole way to browse projects; curated order determines ring slots, and projects after the first 12 remain available without rings.
- Ring tap selects only; an explicit "Open project" action navigates to the project page.
- Eligible projects are public, non-fork, non-archived organization repositories. Last-updated dates are metadata, not a claim of ongoing maintenance.
- Terminology per `GLOSSARY.md`: node = ring `n0–n11`; project = eligible GitHub repository; slot = curated order position in the first 12; work section = `#work`.

## Brand Commitments

Name: Git Guild, developer collective, est. 2026. Voice: warm-direct — plain, welcoming, maintainer-honest, never template-boastful. The emblem (12 rings, 22 traces) is the centerpiece and stays interactive.

## Evidence on Hand

- Real: committed GitHub snapshot, curation order and copy in `gitguild/src/project-curation.json`, traced emblem geometry (12 nodes, 22 traces).
- Not configured: community chat invite. Do not link to a bare placeholder or present the GitHub organization as a chat service.
- Repository descriptions and links come from GitHub; editorial overrides stay in the curation file.
- The three language repositories explicitly described as starting-from-zero curricula are marked as learning tracks in the project browser; other repositories remain unlabelled unless maintainers curate them.
- Visitors may follow their system color preference or choose a persisted light/dark theme. Each deliberate theme switch plays one brief click; page load stays silent.

## Product Principles

1. Welcoming students comes first — make community and collaboration immediately reachable.
2. One visit, one start — the page earns a single action today, not a tour of everything.
3. The network is the invitation — browsing and belonging run through the same emblem, never through duplicate lists.
4. Honest over impressive — project names and dates come from GitHub, while summaries and ordering remain maintainer-controlled; the page never invents activity.
5. Offline-grade durability — what ships must open, read, and navigate with nothing fetched.

## Accessibility & Inclusion

Equal support for mobile and desktop; keyboard-complete operation (`Tab`, arrow keys, `Enter`, `Esc`) with no focus theft; carousel semantics with polite live updates and only the active slide in the tab order; full `prefers-reduced-motion` support (static, no animation); small-screen readability floor of 11px for label text.
