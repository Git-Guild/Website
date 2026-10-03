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

22 assertions across:

* **Structure** — 12 nodes, 12 cards, 6 merge-train commits, every card named,
  card ids matching node ids, every node wired to traces.
* **Hover** — hovering a node lights exactly its own traces, dims the rest of the
  emblem and shows the right tooltip; hovering a commit highlights its node.
* **Panel** — opens on node click, shows the right project, `next`/`←` step
  through projects, `Esc` and backdrop click close it.
* **Keyboard** — arrow keys move focus between nodes, `Enter` opens one.
* **UI feedback** — the copy button reports `copied`.
* **Accessibility** — every node and card has an `aria-label`.
* **Cleanliness** — no console errors or page errors.

Exit output is either `ALL CHECKS PASSED` or a list of failures — use it as the
pre-commit gate.

## `qa_shots.py` — screenshots

Desktop (1440×940), mobile (390×844) and tablet (820×1100) passes covering the
hero, node hover, the open panel, panel navigation, cards, card hover, the merge
train, manifesto/join/footer and the full page. It also collects console errors
and reports them at the end.

Output: `build/qa/*.png` (gitignored, 13 files).

| Shot | What to look for |
|---|---|
| `01-hero`, `09-mobile-hero`, `13-tablet-hero` | Emblem centred, wordmark and CTAs clear |
| `02-hover-node` | Traces light up, everything else dims |
| `03-panel`, `03b-panel-next` | Panel content, prev/next positions |
| `04-cards`, `05-card-hover` | 3-column grid reflowing, hover state |
| `06-train` | Commit graph aligned, node highlight |
| `10-mobile-panel`, `11-mobile-cards`, `12-mobile-train` | Mobile layout, no horizontal overflow |

## What is not covered

Visual previews of the logo trace (`tools/logo/preview_geometry.py`,
`tools/logo/render.py`) are separate — see [../design/README.md](../design/README.md).
