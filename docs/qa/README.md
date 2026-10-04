# QA — checking the built page

Both scripts drive a real Chromium over `file://` — no server, no network.

```bash
python3 tools/qa/qa_assert.py     # assertions, prints PASS/FAIL per check
python3 tools/qa/qa_shots.py      # screenshots for visual review
```

Dependencies: `pip install playwright && playwright install chromium`.
Run them after `python3 tools/build/build_site.py`, since they read
`gitguild/index.html` as it is on disk.

## `qa_assert.py` — functional checks

45 assertions across home, project, and legal pages:

* **Foundation** — React UMD runtime inlined, emblem renders through the React
  shell, no external requests.
* **Structure + slots** — 12 slots following `order[:12]`, all projects as cards
  in `order`, 6 merge-train commits, every card named, every node wired.
* **Hover** — hovering a node lights exactly its own traces, dims the rest,
  shows name and tagline; card and commit hover highlight the matching node.
* **Project pages** — node click navigates to `projects/<slug>.html` with name,
  tagline, blurb, stack, year, status, Visit / Source / Docs actions, back to
  work, and prev/next following ordering; missing links hide without breakage.
* **Nav + footer + legal** — five nav entries plus GitHub action, mobile menu
  with expanded state, nav resolving from project pages, four footer groups
  with good-first-issues, copyright and back-to-top, Privacy / Terms / License /
  Security pages stating no tracking and open terms.
* **Keyboard + panel** — arrows move focus, quick view opens the panel with a
  project-page link, `next`/`←` step through projects, `Esc` closes.
* **UI feedback** — the copy button reports `copied`.
* **Accessibility** — every node, card, and commit has an `aria-label`.
* **Cleanliness** — reduced-motion renders with no errors; zero console or page
  errors anywhere.

Exit output is either `ALL CHECKS PASSED` or a list of failures — use it as the
pre-commit gate.

## `qa_shots.py` — screenshots

Desktop (1440×940), mobile (390×844) and tablet (820×1100) passes covering the
hero, node hover, node-click navigation to the project page, the quick-view
panel and its navigation, cards, card hover, the merge train, manifesto/join,
footer, a project page, a legal page, and the full page. It also collects
console errors and reports them at the end.

Output: `build/qa/*.png` (gitignored, 20 files).

| Shot | What to look for |
|---|---|
| `01-hero`, `09-mobile-hero`, `13-tablet-hero` | Emblem centred, wordmark and CTAs clear |
| `02-hover-node` | Traces light up, everything else dims |
| `03-project`, `07d-project`, `14-tablet-project` | Project header, chips, actions, prev/next |
| `03b-panel`, `03c-panel-next` | Quick-view content, prev/next positions |
| `04-cards`, `05-card-hover` | Grid reflowing, hover state, Quick view buttons |
| `06-train` | Commit graph aligned, node highlight |
| `07c-footer`, `07e-legal` | Four footer groups, legal content |
| `10-mobile-project`, `11-mobile-cards`, `12-mobile-train` | Mobile layout, no horizontal overflow |

## What is not covered

Visual previews of the logo trace (`tools/logo/preview_geometry.py`,
`tools/logo/render.py`) are separate — see [../design/README.md](../design/README.md).
