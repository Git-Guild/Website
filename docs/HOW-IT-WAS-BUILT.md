# How this design came to life

## 1. What we were building

A one-page website for **Git Guild**, a developer collective with twelve
open-source projects.

Three rules shaped every decision:

1. **One page, one file.** The whole site had to be a single HTML file that works
   with no server, no internet and no build step on the host.
2. **The logo is the interface.** Not a logo sitting next to a list of projects —
   the logo *is* how you browse the projects.
3. **No downloads.** No web fonts, no image files, no CDN scripts. The page
   opens instantly and works offline.

---

## 2. The big idea in one sentence

> Every ring in the logo is a project, and every line between rings is a real
> connection between projects — so hovering shows you the wiring, and clicking
> opens the project.

The supplied artwork was already a network: rings connected by lines. That
matched the collective's story (twelve tools that share code and plumbing), so
instead of redrawing the logo, we made it clickable.

Everything else — the colours, the interactions, the way the page is organised —
follows from that one idea.

---

## 3. Where the artwork came from

We started with a single picture: `design/logo-source.jpeg`, a 1408×768 JPEG of
the mark.

A picture is fine for a print, but it has three problems on a website:

* it goes blurry when you scale it up,
* you can't animate or recolour parts of it,
* you can't make part of it clickable.

So the picture was **traced into geometry** — the same job a designer does by
hand in Illustrator, except it was scripted.

### Step 1 — `tools/logo/extract_logo.py` (picture → skeleton)

1. Read the JPEG and split every pixel into two colours: bone-white and amber.
2. Keep only the emblem area (the wordmark underneath is a different asset).
3. "Skeletonise" the shapes: shrink each thick stroke down to a one-pixel-wide
   centre line, run at 3× resolution so the curves stay smooth.
4. Turn that centre line into a graph and cut it into simple paths.
5. Prune the stray twigs (tiny false branches the tracing produces).
6. Simplify each path to a handful of points, then rebuild it as smooth cubic
   curves (the same curve type logos use).

**Output:** `design/logo-geometry.json` — the raw trace.

### Step 2 — `tools/logo/cleanup_geometry.py` (rough → clean)

Raw traces are messy, so four clean-up passes run over them:

1. **Snap** — pull every path end to the exact centre of the ring it touches, so
   no line pokes outside a ring.
2. **Drop** — throw away junk fragments (tiny slivers, tracing artefacts).
3. **Weld** — join paths that continue in a straight line through a junction, so
   one connection is one path instead of two halves.
4. **Normalise** — rebuild the curves and fit everything into a tidy square
   viewBox (476×476) centred on the emblem.

**Output:** `design/logo-final.json` — the clean vector version of the mark.

### Step 3 — checking it by eye

`tools/logo/preview_geometry.py` and `tools/logo/render.py` render our vector
version and place it next to the original JPEG so you can see any difference.
A `--debug` mode colours each line separately while tracing.

### The result, in numbers

| Thing | Value |
|---|---|
| Rings (nodes) | **12** |
| Connecting lines (traces) | **22** |
| Stroke width | 9.6 units |
| Ring band | 11 → 20.5 units |
| Canvas | 476 × 476 units |
| Total line length | ~2313 units |
| Colours | bone `#EBE8DB`, amber `#F4A330` |

The twelve rings are numbered `n0` to `n11`, going top-to-bottom and clockwise.
Those ids are the hook that connects the artwork to the content (next section).

---

## 4. Turning the logo into content

`gitguild/src/projects.js` is the only file you normally edit. It holds:

```js
window.GUILD = {
  collective: { … },        // name, tagline, links, founding year
  projects: {
    n0: { name, tagline, blurb, year, status, stack, url, repo, docs },
    n1: { … },
    …                       // twelve of them, one per ring
  },
  order:      [ … ],        // tab order and card order
  mergeTrain: [ … ],        // six projects shown in the commit graph
  nodeClickBehavior: 'panel'
};
```

Because everything reads from this one object, changing a project updates its
ring, its tooltip, its card, its detail panel and the CLI list — all at once,
with no chance of them disagreeing.

---

## 5. What the page looks like

Read `gitguild/src/styles.css` top to bottom and the page is six blocks:

1. **Hero** — the emblem in the middle, wordmark `GIT GUILD` underneath, a one
   sentence lede, and two buttons.
2. **The network** — twelve project cards in a grid (3 columns → 1 on phones).
3. **Merge train** — a commit-graph band showing the last six merges; hovering a
   commit lights up its ring in the emblem.
4. **Manifesto** — three numbered principles.
5. **Join** — call to action with a copyable install command and four stats.
6. **Footer** + a **slide-in panel** that shows the details of whichever project
   you clicked.

The visual language:

| Token | Value | Why |
|---|---|---|
| Background | `#0A0D11` (near-black) | makes the amber glow |
| Text | `#EBE8DB` (bone) | softer than pure white |
| Accent | `#F4A330` (amber) | the logo's second colour |
| Wordmark font | monospace, wide letter-spacing | reads as "developer tool" |
| Body font | your system font | zero downloads |

Everything is a CSS variable in `:root`, so a whole-page colour change is a
one-line edit.

---

## 6. How it moves and responds

`gitguild/src/app.js` builds the emblem in the browser and makes it alive:

* **On load** — the 22 traces draw themselves in, the rings settle into place,
  a signal pulse runs out of the centre node.
* **Hover / keyboard focus** — everything else dims, that ring and its wiring
  light up, and a tooltip shows the project name.
* **Click** — a spark travels down the traces and the detail panel slides in.
* **Cards and commits** — hovering either one lights up the matching ring, so
  the grid and the emblem stay visually linked.
* **Keyboard** — `Tab` walks the rings, `←/→` move between projects inside the
  panel, `Enter` opens, `Esc` closes.
* **Reduced motion** — if the visitor's system asks for less animation, the
  draw-in, pulses and orbit all switch off.

Accessibility was treated as part of the design, not a clean-up pass: every ring
and card is a real focusable button with a text label for screen readers, and the
layout is checked at 390, 820, 1024, 1280 and 1920 pixels wide.

---

## 7. How five files become one file

You never hand-edit the final page. The sources are:

| Source | Job |
|---|---|
| `src/template.html` | the page skeleton, with `__PLACEHOLDER__` gaps |
| `src/styles.css` | all the CSS |
| `src/projects.js` | all the content |
| `src/emblem-geometry.js` | the traced logo, as JavaScript *(generated)* |
| `src/app.js` | rendering and interaction |

`tools/build/build_site.py`:

1. builds an SVG `<symbol>` of the mark from `design/logo-final.json`,
2. base64-encodes the favicon so the page needs no image files,
3. drops each source file into its placeholder,
4. writes `gitguild/index.html` — one self-contained file, about **67 KB**.

A second script, `tools/build/build_geometry.py`, turns `logo-final.json` into
`src/emblem-geometry.js` (node positions, paths, and which paths touch which
node — the data hover highlighting needs).

Two details that make the build trustworthy:

* paths are resolved from the script's own location, so it runs from any folder;
* files are written with Unix line endings, so a Windows build and a Mac build
  produce byte-identical output.

---

## 8. How we know it works

`tools/qa/qa_assert.py` opens the built page in a real Chromium browser and runs
**22 checks**: twelve rings, twelve cards, six commits, hover lights exactly the
right traces, the panel opens and steps through projects, keyboard navigation
works, the copy button responds, every control has an accessible label, and the
console is free of errors. It prints `ALL CHECKS PASSED` or the failures.

`tools/qa/qa_shots.py` takes 13 screenshots (desktop, tablet, mobile) into
`build/qa/` for a visual look.

Nothing gets committed until both pass.

---

## 9. How it ships

Because the output is already final, deployment is a drag-and-drop:

* **Netlify** — drag the `gitguild/` folder onto app.netlify.com/drop.
* **GitHub Pages / Vercel / Cloudflare Pages / S3** — publish `gitguild/`.

No build runs on the host. Nothing to install, nothing to break.

---

## 10. Explaining it to someone else

**The 30-second version**

> "We started with a JPEG logo of a network. We traced it into real vector
> geometry — 12 rings and 22 connecting lines — and decided each ring *is* one of
> our projects. That one idea drove the content, the interactions (hover to see
> the wiring, click to open the project) and the whole look: dark, monospace,
> amber-on-bone. Then a small Python script baked it into a single 67 KB HTML
> file with no external assets, behind 22 automated browser checks."

**If they ask…**

| Question | Answer |
|---|---|
| *Why trace the logo instead of using the image?* | So it scales perfectly, parts can animate and be clicked, and we ship zero image files. |
| *Why 12 rings?* | One ring per project — that's what makes the logo a navigation instead of decoration. |
| *Where does the content live?* | One file, `src/projects.js`. Change it, rebuild, done. |
| *What framework is it?* | None. Plain HTML, CSS and JavaScript, assembled by one Python script. |
| *How big is it?* | ~67 KB, single file, no network requests — it opens from a USB stick. |
| *How do you change the colours?* | Four CSS variables at the top of `styles.css`. |
| *Is it accessible?* | Yes — keyboard navigation, labels, and it respects reduced-motion settings. |
| *How do you deploy it?* | Drag the folder onto Netlify. |
| *How do you know it isn't broken?* | `tools/qa/qa_assert.py` runs 22 checks in a real browser. |

---

## 11. The file map (where to look)

```
design/logo-source.jpeg        the original picture we started from
design/logo-geometry.json      raw trace of that picture
design/logo-final.json         cleaned vector version of the mark

gitguild/src/template.html     page skeleton
gitguild/src/styles.css        all styling
gitguild/src/projects.js       all content (the file you edit)
gitguild/src/emblem-geometry.js  logo as data (generated)
gitguild/src/app.js            rendering + interaction
gitguild/index.html            the finished site (generated)

tools/logo/*.py                picture → vectors
tools/build/*.py               sources → index.html
tools/qa/*.py                  browser checks
docs/                          this documentation
```

## 12. Recipes

```bash
# change a project's text        → edit gitguild/src/projects.js, then:
python3 tools/build/build_site.py

# rebuild after re-tracing art    → then also:
python3 tools/build/build_geometry.py

# check nothing broke             →
python3 tools/qa/qa_assert.py

# take fresh screenshots          →
python3 tools/qa/qa_shots.py
```
