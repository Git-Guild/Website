# ADR 0003: Front-end redesign (warm-direct, slider as browser)

Date: 2026-10-08
Status: proposed (STOP — awaiting go-ahead, do not build)

## Context

Git Guild site serves tier-3 (and lower) college students who lost their
first/second year. Likely visitors: mid-range Android phones, patchy data,
short attention. Design for them first, desktop second. Target feeling:
"there's a place for people like me, and I can start today."

Verified in `build/qa/` screenshots + live measurements (2026-10-08):

- 12-card work grid is generic: identical boxes, only pip color + one
  `flagship` badge differ. At 390px each card is ~1 viewport tall and
  `Quick view` sits detached below the card.
- Sections share one rhythm (`// TITLE` + sub + boxed card on the same dark
  ground); gaps read as dead space between identical blocks.
- Template feel comes from copy (stats `Projects / Traces / Technologies`,
  maintainer manifesto), but real copy is OUT for this phase — layout,
  hierarchy and spacing must carry the welcome.
- Hero fit: at 390×844 both CTAs in view (hero 777px, stage 351px) but hero
  fills 92% of viewport; at **360×640 both CTAs are below the fold**
  (CTA tops 673/731px, stage 324px). Emblem and CTA cannot both win at
  current size.
- Contrast on `BG #0A0D11`: amber `#F4A330` 9.39:1, `amber-2` 12.87:1,
  bone 15.85:1 (AA pass); `muted #78828F` 5.00:1 (passes, thin at 11px mono).
- Paint profile (390px, 4x CPU throttle, 120-frame rAF): `getTotalLength`
  over 22 traces 0.2ms → 1.0ms throttled; spark append ≈ 0ms. JS geometry is
  cheap. Risk is paint: `hero__glow` blur, fixed `body::before/::after`
  gradients + grid mask, 12× `card::after` gradients, spark `drop-shadow`,
  nav `backdrop-blur`. The 16.6ms readings are the 60fps cap — treated as
  no-regression only, not proof for low-end GPUs.

Non-negotiables (kept): single self-contained page, no network requests,
no web fonts, no CDN. Edit `gitguild/src/*`, rebuild with
`tools/build/build_site.py`, never hand-edit `gitguild/index.html`, run
`tools/qa/qa_assert.py` after each change. Emblem stays centerpiece and
interactive (12 rings, 22 traces). Touch, keyboard, `prefers-reduced-motion`.

Glossary (`GLOSSARY.md`): **node** = ring `n0–n11`; **project** = entry in
`projects.js`; **slot** = `order[:12]` binding; **work section** = `#work`.

## Decisions

1. **Slider is the sole browser.** No featured-strip + grid duplication.
   Slider browses all slotted projects (`order[:12]`); overflow
   (`order[12:]`) stays card-only per ADR-0002. `featured` is emphasis
   (badge / front of `order`), not a separate list. Must work 3–12
   projects, unpredictable blurb length — hierarchy from size/position,
   never from text length.
2. **Desktop = spotlight + index, same state machine.** One large selected
   project synced to the emblem + dense index rows. Same `store.selected`,
   same prev/next + `←/→` arrows + `03 / 12` counter as mobile. Mobile =
   peek carousel (next card partly visible) + counter + dots/compact index
   for jumping (peek alone is O(n) swipes at 12 projects).
3. **Retire the quick-view panel.** Three views (page + panel + spotlight)
   become two: browser (slider/spotlight) → project page. Ring tap =
   select only (jump slider/spotlight, light ring), never navigate on first
   tap. Explicit `Open project →` CTA navigates. `Quick view` buttons go
   away. (Note: `qa_assert.py` currently checks the panel — update it in
   build step 2.)
4. **Off-screen ring tap (mobile): no auto-scroll.** Inline chip inside
   `.stage` appears: `03/12 Vector · View ↓`; tapping it smooth-scrolls
   to the slider (instant under reduced-motion). Selection persists.
5. **Motion: breathing + interaction sparks only.** Idle constellation
   breathing (single wrapper/overlay `opacity` only, composited layer —
   not 12 SVG children) + spark on select/click. Cut scroll-driven emblem
   assembly and mouse parallax/tilt for this phase. Pause breathing when
   `#stage` out of view (`IntersectionObserver`), tab hidden
   (`visibilitychange`), and under `prefers-reduced-motion` (static).
6. **Emblem re-entry is instant.** `store.selected` persists;
   re-applying `is-selected`/`is-focused` on re-entry with no spark, no
   re-draw.
7. **Carousel a11y:** wrapper `role="region"` +
   `aria-roledescription="carousel"`; slides `role="group"` +
   `aria-label="3 of 12: Vector"` (name included); only active slide
   focusable (`tabindex="0"`), off-screen `aria-hidden="true"` + `inert`,
   out of tab order. Spotlight wrapper `aria-live="polite"`. Prev/next
   keep focus; ring hover never steals focus.
8. **Warm-direct, dark + amber kept.** Warmth from copy slot, hierarchy and
   spacing, not palette. Amber reserved for interactive/wiring only (never
   fills/backgrounds); small amber text ≥11px (contrast above).
9. **Type: system-only.** Keep `ui-monospace` wordmark/labels + system sans
   body. A subsetted inlined display face (A–Z, 0–9, `/.—→`, WOFF2+base64)
   would add ~11–19KB to today's 227KB file (+5–8%) for a marginally wider
   wordmark — not worth breaking the "no web fonts" rule this phase.
10. **Hero compaction:** ≤420px emblem capped at **248px (64vw, max 280px)**,
    one-line eyebrow, 30px wordmark, lede 2 lines max — primary CTA top
    edge ~570–640px so it clears 360×640 and 390×844 with comfort.
    (Current 351px/324px stage pushes CTAs to 673px+ at 360×640.)
11. **Sections alternate dense/air** instead of identical
    `clamp(56px,8vw,110px)` gaps. Kills dead space without new copy.
12. **Primary CTA = chat for now.** Mobile primary `Say hello in chat`
    (reads `collective.links.chat`), secondary `Browse projects ↓`;
    desktop primary `Browse projects ↓`. GitHub Star demoted to nav/footer.
    The org DOES have learning-track repos (C++/Python/Java "from 0"),
    tools and a game — not on the site yet. Once track content is wired in,
    **`start a track` becomes primary**; chat CTA is interim, not a claim
    that tracks don't exist.
13. **Future path picker: hook only.** Add `data-route` attribute / store
    field for a future route highlight + this ADR note. No empty DOM slot,
    no reserved layout space (that recreates dead space). Build the slot
    when the feature ships.

## Explicitly out

- Real project content, real copy (projects.js text stays placeholder;
  design must survive 3–12 items and any blurb length).
- `start a track` as primary CTA (waits on track content wiring).
- Path-picker UI (hook only, decision 13).
- Scroll-driven emblem assembly; mouse parallax / 3D tilt.
- Custom/inlined display font; web fonts; CDN; network requests.
- Re-tracing the mark for a 13th ring (ADR-0002 overflow rule stands).
- Any design that depends on content we don't have — flagged in build
  steps instead.

## Build order (small steps)

1. **Placeholder-link guard.** CTA reads `collective.links.chat` with
   `TODO(chat-link)` marker; build warns and `qa_assert` fails on bare
   placeholders (`https://discord.com/`, `https://github.com/` bare
   project URLs). No visual change.
2. **Retire panel → select-only rings + chip.** Remove panel + `Quick
   view`; ring tap selects; chip (`03/12 Name · View ↓`) scrolls to
   slider. Update `qa_assert` panel checks to chip/select checks.
3. **Slider as browser.** Mobile peek carousel + counter + dots/index;
   desktop spotlight + index; prev/next + arrows; a11y roles per
   decision 7. Single source from `window.GUILD`, `order[:12]`.
4. **Hero compaction + lede slot.** 248px emblem cap, one-line eyebrow,
   90–120-char `__LEDE__` slot (example for length/tone only, not claims:
   *"Lost a year? You're not late — pick one project and ask anything
   today."*). CTA hierarchy per decision 12.
5. **Section rhythm + amber tightening.** Dense/air alternation, amber to
   interactive/wiring, 11px-min labels, system-only type scale.
6. **Motion.** Wrapper-only breathing + interaction sparks with pause
   rules (decision 5); instant re-entry (decision 6); reduced-motion pass.
7. **Route hook.** `data-route` / store field only + comment; no layout.

## Verification per step

After **each** step: `python3 tools/build/build_site.py` then
`python3 tools/qa/qa_assert.py` (must print `ALL CHECKS PASSED`; step 2
includes the updated panel→chip assertions) plus `qa_shots.py`
screenshots at **360×640, 390×844, 1440×940** — hero CTA above fold at
360/390, slider/spotlight hierarchy legible, no console errors, keyboard
(`Tab`, `←/→`, `Enter`, `Esc`) and `prefers-reduced-motion` pass at each
width. Commit `gitguild/index.html` only when all three widths pass.

## Open placeholders (do not invent)

- `collective.links.chat` = `https://discord.com/` — BARE, TODO.
  CTA reads it; guard fails build/QA until replaced with the real invite.
- Lede `__LEDE__` — placeholder slot; example above is length/tone only.
- Project `url`/`repo`/`docs` — many bare `https://github.com/`; design
  must not depend on them being real.
- References below are the assistant's provisional picks, NOT approved —
  Sourabh confirms/replaces separately:
  `https://www.freecodecamp.org/` (one dominant start-here action);
  `https://www.theodinproject.com/` (community path framing, dense/air
  rhythm).
