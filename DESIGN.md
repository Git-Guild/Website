---
name: Git Guild
description: Developer collective — the logo is the project browser.
colors:
  bg: "#0A0D11"
  bg-2: "#0D1218"
  panel: "#111823"
  bone: "#EBE8DB"
  bone-dim: "#B9B7AC"
  amber: "#F4A330"
  amber-2: "#FFC978"
  muted: "#78828F"
  ink: "#150E02"
  wire-white: "#FFFFFF"
  wordmark-sheen: "#C8C4B4"
  shadow-black: "#000000"
typography:
  display:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "clamp(30px, 7.4vw, 72px)"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "0.3em"
  headline:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "clamp(19px, 2.6vw, 28px)"
    fontWeight: 700
    letterSpacing: "0.18em"
  body:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(14.5px, 1.55vw, 17px)"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "11.5px"
    letterSpacing: "0.14em"
  compact-label:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "13px"
  metadata-label:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "12.5px"
  caption-label:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "13.5px"
  small-body:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "15.5px"
  base-body:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "16px"
  minor-heading:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "18px"
  section-title:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "22px"
  join-title:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "26px"
  project-title:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "24px"
  large-project-title:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "34px"
  wordmark-mobile:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "30px"
  wordmark-tablet:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "52px"
  wordmark-desktop:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "64px"
rounded:
  keycap: "5px"
  focus: "6px"
  sm: "8px"
  button: "10px"
  panel: "12px"
  md: "14px"
  lg: "22px"
  pill: "100px"
spacing:
  pad: "clamp(20px, 4vw, 56px)"
  maxw: "1240px"
components:
  button-primary:
    backgroundColor: "{colors.amber}"
    textColor: "#150E02"
    rounded: "10px"
    padding: "12px 20px"
  button-primary-hover:
    backgroundColor: "{colors.amber-2}"
    textColor: "#150E02"
    rounded: "10px"
    padding: "12px 20px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.bone-dim}"
    rounded: "10px"
    padding: "12px 20px"
---

# Design System: Git Guild

## Overview

**Creative North Star: "The Wired Workbench"**

The page is a dark instrument panel with a live circuit at its center: bone-white and amber wiring on near-black, monospace labels set wide like engraved tags, and up to twelve projects reachable by touching the mark itself. Per accepted ADR-0003, the page uses alternating rhythm — dense passages earn quiet ones — while the emblem stays the centerpiece and the slider serves as the project browser.

**Key Characteristics:**
- Dark ground with amber-as-signal wiring, never as fill.
- Monospace wordmark and labels over a system-sans body.
- The emblem as the primary interface; the slider/spotlight is the sole browser synced to its rings.
- Alternating dense/air section rhythm instead of identical boxed gaps.

## Colors

Warm wiring on a near-black ground; amber means "live / touchable".

### Primary
- **Signal Amber** (#F4A330): interactive elements, wiring traces, focus, primary buttons, active states.
- **Pale Amber** (#FFC978): hover lift on amber, hot-ring highlight, spark glow.

### Neutral
- **Ground Black** (#0A0D11): page background.
- **Raised Ground** (#0D1218): cards and secondary surfaces.
- **Panel Deep** (#111823): dialog sheet, tooltip, filter bar.
- **Bone** (#EBE8DB): primary text and white traces.
- **Dimmed Bone** (#B9B7AC): secondary text, lede.
- **Quiet Gray** (#78828F): muted labels, captions, dividers (with bone text at small sizes).
- **Button Ink** (#150E02): near-black text on amber primary buttons (contrast checked).
- **Wire White** (#FFFFFF): white emblem traces, interaction highlights, and the wordmark sheen.
- **Wordmark Sheen** (#C8C4B4): the bone-to-bone wordmark's soft highlight at its edge.
- **Shadow Black** (#000000): shadow falloff only; never text or a large surface.

### Named Rules
**The Wiring-Only Rule.** Amber marks what is live or wired — buttons, rings, traces, focus, and selection. It never fills large surfaces. Amber stays the sole accent; background atmosphere uses the near-black and amber family.

**The Eleven-Pixel Floor.** No label text below 11px, however muted its color.

## Typography

**Display Font:** ui-monospace stack (with system fallback)
**Body Font:** system sans stack
**Label/Mono Font:** ui-monospace stack, uppercase, wide tracking
**Working type sizes:** 11–13.5px for compact labels, 14.5–17px for body
copy, 18–28px for compact headings, 30–34px for featured project titles,
and 52–64px for the desktop wordmark. The 11.5px hint text is an interface
instruction label, not body prose.

**Character:** Engraved instrument tags over plain-spoken body copy. The wordmark reads as a developer tool; the body stays quiet and legible.

### Hierarchy
- **Display** (700, clamp(30px, 7.4vw, 72px), 1.05, 0.3em tracking, uppercase): the `GIT GUILD` wordmark only.
- **Headline** (700, clamp(19px, 2.6vw, 28px), 0.18em tracking, uppercase): `//` section titles.
- **Title** (700, 17px mono, 0.14em tracking, uppercase): card and principle names.
- **Body** (400, clamp(14.5px, 1.55vw, 17px), 1.6): lede, blurbs, prose; max ~62–68ch.
- **Label** (mono, 10–12.5px, 0.1–0.24em tracking, uppercase): eyebrow, hints, indices, chips, buttons, stats.

### Named Rules
**The System-Only Rule.** Wordmark, labels, and body stay on system stacks to preserve the offline, dependency-free page.

## Layout

One centered column (`1240px` max, side padding `clamp(20px, 4vw, 56px)`). Block order: hero (eyebrow → emblem → `GIT GUILD` → lede → 2 CTAs) → work slider → recent-updates band → manifesto → join → footer. Per ADR-0003, sections alternate dense and air instead of sharing one identical `clamp(56px, 8vw, 110px)` gap rhythm, so gaps stop reading as dead space between identical blocks.

Per ADR-0003 hero compaction: at `≤420px` the emblem is capped at ~248px (64vw, max 280px) with a one-line eyebrow, 30px wordmark, and lede at 2 lines max, so the primary CTA clears 360×640 and 390×844 viewports. Primary CTA points to open issues; the project browser is the secondary action.

## Elevation & Depth

Flat by default with tonal layering; shadows appear only as responses to state. Depth comes from translucent white layering over the dark ground, amber glow on lit wiring, and a fixed ambient ground (radial amber wash plus a faint grid mask). The slider's active card lifts on selection; sparks carry a soft drop-shadow glow.

Per ADR-0003 motion grammar: idle constellation breathing on ONE wrapper/overlay (`opacity` only, composited layer — not 12 SVG children) plus spark on select/click. Scroll-driven emblem assembly and mouse parallax/tilt are explicitly cut this phase. Breathing pauses when the stage is out of view (`IntersectionObserver`), when the tab is hidden (`visibilitychange`), and under `prefers-reduced-motion` (static). Emblem re-entry is instant: persisted selection re-applies with no spark, no re-draw.

### Shadow Vocabulary
- **Slider active lift** (`box-shadow: 0 22px 50px -30px rgba(244,163,48,.6)`): selected or hot slider card only.
- **Primary button glow** (`box-shadow: 0 10px 30px -12px rgba(244,163,48,.65)`): primary CTA at rest, deepening on hover.

### Accepted detector exceptions
The following read as anti-patterns to an automated detector but are committed parts of this world — do not "fix" them without a redesign decision:
- Bone-to-bone wordmark gradient (`#fff → #EBE8DB → #C8C4B4`, engraved-tag sheen, not a colorful gradient) and the 2px amber progress hairline.
- Amber glow shadows (button glow, slider lift, spark `drop-shadow`) — the Shadow Vocabulary above, never neutral elevation.
- Fixed ambient ground (radial amber wash + 64px grid mask) and the 6px pulsing eyebrow dot.
- Pill `100px` radii (chips, flags, dots, steps), `10px` button radius, and `#150E02` button text — verbatim tokens of this system.
- `5px` keycap radius, `6px` focus outline radius, and `12px` information-panel radius — small functional shapes within the larger 8/14/22px surface scale.
- `11px` mono labels (the floor, never below) and `--muted #78828F` on flat ground (5.00:1, AA pass). On tinted gradients (join block) secondary text uses `--bone-dim` instead.

### Named Rules
**The Flat-By-Default Rule.** Surfaces are flat at rest. Glow and shadow answer to touch, hover, or selection — never as static decoration.

## Shapes

Rectangular instrument language: `14px` card radius (`8px` small, `22px` large), `1px` hairline borders, pill chips and pills for filters and flags, circular rings and commit dots in the emblem and train. Clipping is minimal; the emblem and its orbit rings provide the only round geometry at scale.

## Components

### Emblem (signature)
- Twelve tappable rings over 22 traces; hover/focus dims the rest and lights one node's wiring with a tooltip; ring tap selects only (jumps slider/spotlight, lights ring), never navigates on first tap. Emblem sync runs only while the emblem is in view (`IntersectionObserver`); re-entry restores the selected ring instantly. Keyboard: `Tab` travels rings, arrows move, `Enter` selects, `Esc` clears; ring hover never steals focus.

### Project slider (signature — REPLACES card grid per ADR-0003)
- The slider is the sole way to browse projects. It shows every eligible repository; the first 12 in curated order bind to physical nodes and later projects remain accessible without a ring. Mobile uses a swipeable card, counter, and jump dots. Desktop uses a spotlight and compact index. One selection state drives both views and the emblem.
- Carousel semantics: wrapper `role="region"` with `aria-roledescription="carousel"`; slides `role="group"` labeled `3 of 12: Vector` (name included); only the active slide focusable, off-screen slides `aria-hidden` plus `inert`; spotlight wrapper `aria-live="polite"`; prev/next keep focus.

### Off-screen ring chip (signature)
- Tapping an off-screen ring on mobile does not auto-scroll. An inline chip inside the stage appears (`03/12 Vector · View ↓`); tapping it smooth-scrolls to the slider (instant under reduced-motion). Selection persists.

### Buttons
- **Shape:** rounded rectangles (10px radius).
- **Primary:** amber fill, near-black text, mono uppercase; lifts and brightens on hover. The homepage offers one repository-browsing action and one open-issue action; no chat invite is shown until one exists.
- The selected project browser keeps a direct **Open repository** action beside a secondary detail page. This makes the real GitHub destination one action away without duplicating the project list.
- Maintainer-curated learning tracks carry a small amber **Learning track** label in the same browser. The badge is attached to its repository row and card, not presented as a second project list.
- **Ghost:** transparent, dimmed-bone text, hairline border; warms to an amber border on hover.
- Theme controls sit beside GitHub in the nav. The first visit follows the device preference; a deliberate toggle persists the choice. Light mode uses paper, charcoal, and deeper amber roles so the emblem and small labels stay legible.
- The theme change opens from the toggle with a circular wipe. Reduced-motion users get a direct change. Each deliberate switch plays one quiet, synthesized click; page load stays silent and no remote asset is loaded.

### Slider cards
- **Corner Style:** gently rounded rectangles (14px radius).
- **Background:** near-black raised ground with a faint top-lit gradient.
- **Shadow Strategy:** flat at rest; active-card lift per Elevation.
- **Border:** hairline light border, warming to amber on hover; amber when selected.
- **Internal Padding:** 20px cards.

### Card grid — REPLACED per ADR-0003
- The 12-card grid (identical boxes differing only in pip color plus one flagship badge, ~1 viewport tall per card at 390px with detached Quick-view buttons below) is replaced by the project slider above. Do not design new work around the grid; the work section keeps its `//` title but the browser inside it is the slider.

### Chips
- **Style:** pill outline, muted mono uppercase text; stack tags on cards, project metadata.
- **State:** active filter inverts to amber emphasis.

### Inputs / Fields
- **Style:** borderless search field inside the filter bar's outlined container.
- **Focus:** inherited focus ring; no bespoke error or disabled state (single search field).

### Navigation
- Sticky top bar: mark plus wide-tracked wordmark left, mono uppercase section links, ghost GitHub CTA; collapses to a hamburger menu under `760px`. A 2px amber scroll-progress hairline sits at the very top.

### Quick-view panel — RETIRED per ADR-0003
- The slide-in panel (right-side sheet / bottom sheet on phones, with Visit/Source/Docs links, prev/next stepping, and card Quick-view buttons opening it) is retired. Three views (page + panel + spotlight) become two: browser (slider/spotlight) → project page. Ring tap selects only; the explicit `Open project →` action navigates. `Quick view` buttons go away. (`tools/qa/qa_assert.py` panel checks move to chip/select checks in build step 2.)

### Recent updates
- A horizontal timeline shows up to six repository update dates, oldest to newest. Selecting an item selects its ring and the matching project in the browser. Dates come from the committed GitHub snapshot and describe GitHub update times.

## Do's and Don'ts

### Do:
- **Do** keep every surface offline and self-contained — no web fonts, no CDN, no images, no network requests.
- **Do** keep the slider as the single source from `window.GUILD`, `order[:12]` — no featured-strip plus grid duplication.
- **Do** respect `prefers-reduced-motion` fully: breathing static, sparks off, chip scroll instant, re-entry instant.
- **Do** keep small amber text at or above 11px.

### Don't:
- **Don't** hand-edit the built page — sources live in `gitguild/src/*`, assembled by `tools/build/build_site.py`.
- **Don't** design around the retired card grid or quick-view panel — both are replaced per ADR-0003 (see markers above).
- **Don't** add scroll-driven emblem assembly, mouse parallax, or tilt this phase — ADR-0003 cuts them.
- **Don't** add a 13th ring by redrawing — overflow projects are card-only per the slot rule.
- **Don't** invent real copy, real project URLs, the chat invite, or the path-picker UI — curation copy should be grounded in the organization’s actual repositories and links.
